import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import csd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def run_fdd_core(file_path):
    """الگوریتم اصلی FDD روی داده‌های سه محور جهت استخراج فرکانس طبیعی مود اول"""
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
            sep = '\t' if '\t' in first_line else ','
            
        df = pd.read_csv(file_path, sep=sep)
        
        # پیدا کردن ستون‌ها به صورت هوشمند
        time_col = [c for c in df.columns if 'time' in c.lower()][0]
        ax_col = [c for c in df.columns if 'x' in c.lower()][0]
        ay_col = [c for c in df.columns if 'y' in c.lower()][0]
        az_col = [c for c in df.columns if 'z' in c.lower()][0]
        
        t = df[time_col].values
        dt = np.mean(np.diff(t))
        fs = 1.0 / dt
        
        # چیدن سیگنال‌های ۳ محور در ماتریس
        signals = [df[ax_col].values, df[ay_col].values, df[az_col].values]
        num_channels = len(signals)
        
        # حذف میانگین (Detrend ملایم) جهت حذف آفست DC
        for i in range(num_channels):
            signals[i] = signals[i] - np.mean(signals[i])
            
        # تنظیمات بهینه رزولوشن فرکانسی (Zero Padding داخلی در محاسبات تراکم طیفی متقاطع)
        nperseg = min(2048, len(t) // 2)
        nfft = max(16384, nperseg * 8) # ایجاد پله‌های بسیار ریز فرکانسی (زیر 0.01 هرتز)
        
        # گرفتن طول فرکانس خروجی به صورت فرضی
        _, f_dummy = csd(signals[0], signals[0], fs=fs, nperseg=nperseg, nfft=nfft)
        num_freqs = len(f_dummy)
        
        # تشکیل ماتریس سه بعدی Cross-Power Spectral Density (CPSD)
        Gyy = np.zeros((num_channels, num_channels, num_freqs), dtype=complex)
        for i in range(num_channels):
            for j in range(num_channels):
                f, f_csd = csd(signals[i], signals[j], fs=fs, nperseg=nperseg, nfft=nfft)
                Gyy[i, j, :] = f_csd

        # اعمال تجزیه مقادیر منفرد (SVD) روی ماتریس چگالی طیفی در هر فرکانس گسسته
        s_values = np.zeros((num_channels, num_freqs))
        for k in range(num_freqs):
            G_matrix = Gyy[:, :, k]
            U, S, Vh = np.linalg.svd(G_matrix)
            s_values[:, k] = S

        # زوم و فیلتر روی بازه فرکانسی مودهای ارتعاشی عمران (بین 0.5 تا 60 هرتز)
        valid_idx = (f > 0.5) & (f < 60)
        first_singular_value = s_values[0, :]
        
        if np.any(valid_idx):
            peak_idx = np.argmax(first_singular_value[valid_idx])
            natural_frequency = f[valid_idx][peak_idx]
        else:
            peak_idx = np.argmax(first_singular_value)
            natural_frequency = f[peak_idx]
            
        # محاسبه مشخصات آماری برای تکمیلی ماتریس ویژگی‌ها
        features = {
            'File_Name': os.path.basename(file_path),
            'Sampling_Rate_Hz': round(fs, 2),
            'Duration_Sec': round(t[-1] - t[0], 2),
            'FDD_Identified_Frequency_Hz': round(natural_frequency, 3), # استخراج با ۳ رقم اعشار
            'Z_RMS_Energy': round(np.sqrt(np.mean(signals[2]**2)), 4),
            'Z_Kurtosis': round(pd.Series(signals[2]).kurt(), 4)
        }
        
        return features, f, s_values, natural_frequency
    except Exception as e:
        print(f"Error executing FDD on {file_path}: {e}")
        return None

def process_batch_fdd():
    input_dir = entry_input.get()
    output_dir = entry_output.get()
    
    if not input_dir or not os.path.exists(input_dir):
        messagebox.showerror("خطا", "لطفاً پوشه حاوی فایل‌های CSV آزمایش را به درستی انتخاب کنید.")
        return
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("خطا", "لطفاً مسیر ذخیره خروجی FDD را انتخاب کنید.")
        return
        
    file_list = glob.glob(os.path.join(input_dir, "*.csv"))
    if not file_list:
        messagebox.showerror("خطا", "هیچ فایل داده‌ای با پسوند CSV در این پوشه یافت نشد.")
        return
        
    fdd_summary = []
    plt.rcParams['font.family'] = 'serif'
    
    for file_path in file_list:
        if "device" in os.path.basename(file_path).lower() or "report" in os.path.basename(file_path).lower():
            continue
            
        result = run_fdd_core(file_path)
        if result is None: 
            continue
            
        features, f, s_values, nat_freq = result
        fdd_summary.append(features)
        
        # ترسیم پلات‌های تخصصی OMA / FDD
        if var_plots.get():
            plt.figure(figsize=(9, 4.5), dpi=100)
            
            # ترسیم نمودار لگاریتمی مقادیر منفرد (که قله‌های سازه‌ای را بسیار تیز نشان می‌دهد)
            plt.semilogy(f, s_values[0, :], color='#d62728', linewidth=1.8, label='1st Singular Value ($S_1$ - Main Modal Energy)')
            plt.semilogy(f, s_values[1, :], color='#1f77b4', linewidth=1.0, alpha=0.6, label='2nd Singular Value ($S_2$ - Secondary/Noise)')
            plt.semilogy(f, s_values[2, :], color='#2ca02c', linewidth=1.0, alpha=0.4, label='3rd Singular Value ($S_3$ - Cross Noise)')
            
            plt.axvline(nat_freq, color='black', linestyle='--', linewidth=1.1,
                        label=f'Identified Structural Freq: {nat_freq:.3f} Hz')
            
            plt.xlim(0, 50) # زوم روی فرکانس‌های ارتعاشات اصلی تیر اولر برنولی
            plt.title(f"Operational Modal Analysis (FDD Spectrum): {features['File_Name']}", fontsize=10, fontweight='bold')
            plt.xlabel("Frequency (Hz)", fontsize=9)
            plt.ylabel("Singular Values (Log Scale)", fontsize=9)
            plt.grid(True, which="both", linestyle=':', alpha=0.5)
            plt.legend(loc='upper right', fontsize=8)
            plt.tight_layout()
            
            # ذخیره تصویر پلات FDD کنار فایل اکسل گزارش
            plt.savefig(os.path.join(output_dir, f"FDD_Spectrum_{os.path.splitext(features['File_Name'])[0]}.png"))
            plt.close()

    if fdd_summary:
        df_fdd = pd.DataFrame(fdd_summary)
        excel_path = os.path.join(output_dir, "SHM_FDD_Identified_Report.xlsx")
        
        # ذخیره نهایی ماتریس فرکانس‌های شناسایی شده در فایل اکسل
        df_fdd.to_excel(excel_path, index=False, sheet_name='FDD_Modal_Identification')
        messagebox.showinfo("موفقیت", f"آنالیز پیشرفته FDD به صورت گروهی انجام شد!\n\nنتایج در مسیر زیر ذخیره گردید:\n{excel_path}")
    else:
        messagebox.showwarning("هشدار", "هیچ فایلی واجد شرایط پردازش الگوریتم FDD نبود.")

def browse_input():
    directory = filedialog.askdirectory()
    if directory: entry_input.delete(0, tk.END); entry_input.insert(0, directory)

def browse_output():
    directory = filedialog.askdirectory()
    if directory: entry_output.delete(0, tk.END); entry_output.insert(0, directory)

# پیاده‌سازی پنجره گرافیکی مدیریت سیستم (GUI)
root = tk.Tk()
root.title("سامانه تحلیل دینامیکی سازه‌ها با الگوریتم FDD (شناسایی سیستم چندکاناله)")
root.geometry("640x330")
root.configure(bg="#f4f6f9")

font_title = ("Segoe UI", 9, "bold")
font_sub = ("Segoe UI", 10)

frame_io = tk.Frame(root, bg="#f4f6f9")
frame_io.pack(fill="x", padx=25, pady=20)

tk.Label(frame_io, text="۱. پوشه حاوی کل فایل‌های آزمایش (فرمت CSV سه محوره):", bg="#f4f6f9", font=font_title, fg="#212529").grid(row=0, column=0, sticky='w', pady=(0,5))
entry_input = tk.Entry(frame_io, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#dee2e6", width=45)
entry_input.grid(row=1, column=0, ipady=3, sticky='ew', padx=(0,10))
tk.Button(frame_io, text="انتخاب پوشه ورودی", command=browse_input, bg="#495057", fg="white", font=("Segoe UI", 9), relief="flat", width=15).grid(row=1, column=1, ipady=2)

tk.Label(frame_io, text="۲. پوشه محل ذخیره گزارش نهایی اکسل و طیف‌های SVD:", bg="#f4f6f9", font=font_title, fg="#212529").grid(row=2, column=0, sticky='w', pady=(15,5))
entry_output = tk.Entry(frame_io, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#dee2e6", width=45)
entry_output.grid(row=3, column=0, ipady=3, sticky='ew', padx=(0,10))
tk.Button(frame_io, text="انتخاب پوشه خروجی", command=browse_output, bg="#495057", fg="white", font=("Segoe UI", 9), relief="flat", width=15).grid(row=3, column=1, ipady=2)

frame_io.columnconfigure(0, weight=1)

frame_opts = tk.LabelFrame(root, text=" تنظیمات رسم طیف فرکانسی ", bg="white", font=font_title, fg="#198754", bd=1, relief="solid")
frame_opts.pack(fill="x", padx=25, pady=(0,20))

var_plots = tk.BooleanVar(value=True)
chk_plots = tk.Checkbutton(frame_opts, text="ترسیم خودکار نمودار مقادیر منفرد (Singular Values) و تفکیک مودال برای تمامی فایل‌ها", 
                           variable=var_plots, bg="white", activebackground="white", font=("Segoe UI", 9))
chk_plots.pack(anchor="w", padx=15, pady=10)

btn_run = tk.Button(root, text="اجرای آنالیز مودی عملیاتی (OMA) بر پایه الگوریتم FDD", command=process_batch_fdd, 
                    bg="#198754", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", activebackground="#157347")
btn_run.pack(fill="x", padx=25, ipady=6)

root.mainloop()