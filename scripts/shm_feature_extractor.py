import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def extract_signal_features(file_path):
    """استخراج ویژگی‌های آماری و دینامیکی پیشرفته به همراه تکنیک افزایش رزولوشن فرکانسی"""
    try:
        # تشخیص جداکننده فایل (کاما یا تب)
        with open(file_path, 'r') as f:
            first_line = f.readline()
            sep = '\t' if '\t' in first_line else ','
            
        df = pd.read_csv(file_path, sep=sep)
        
        # پیدا کردن ستون‌ها به صورت هوشمند
        time_col = [c for c in df.columns if 'time' in c.lower()][0]
        az_col = [c for c in df.columns if 'z' in c.lower()][0]
        abs_col = [c for c in df.columns if 'absolute' in c.lower() or 'total' in c.lower()][0]
        
        t = df[time_col].values
        dt = np.mean(np.diff(t))
        fs = 1.0 / dt
        
        # سیگنال‌های هدف (محور قائم Z و شتاب مطلق)
        acc_z = df[az_col].values
        acc_abs = df[abs_col].values
        
        # حذف آفست و روند خطی برای تحلیل دقیق فرکانسی
        acc_z_detrend = acc_z - np.mean(acc_z)
        
        # -----------------------------------------------------------
        # پیاده‌سازی تکنیک Zero Padding برای افزایش فوق‌العاده رزولوشن فرکانسی
        # -----------------------------------------------------------
        N_original = len(acc_z_detrend)
        # پد کردن سیگنال به طول بزرگتر (حداقل 16384 نقطه جهت ریز شدن پله‌های فرکانسی)
        N_fft = max(16384, 2**int(np.ceil(np.log2(N_original)) + 2)) 
        
        yf = fft(acc_z_detrend, n=N_fft)
        xf = fftfreq(N_fft, dt)[:N_fft//2]
        fft_amps = 2.0 / N_original * np.abs(yf[:N_fft//2]) # نرمال‌سازی بر اساس طول سیگنال اصلی
        
        # فیلتر کردن بازه فرکانسی مجاز برای سازه‌های ساختمانی و عمران (بین 0.5 تا 60 هرتز)
        valid_idx = (xf > 0.5) & (xf < 60)
        if np.any(valid_idx):
            peak_freq = xf[valid_idx][np.argmax(fft_amps[valid_idx])]
        else:
            peak_freq = xf[np.argmax(fft_amps)]
        # -----------------------------------------------------------
            
        # محاسبه شاخص‌های آماری و فیزیکی سیگنال
        features = {
            'File_Name': os.path.basename(file_path),
            'Sampling_Rate_Hz': round(fs, 2),
            'Duration_Sec': round(t[-1] - t[0], 2),
            'Z_Peak_Acceleration': round(np.max(np.abs(acc_z)), 4),
            'Z_RMS': round(np.sqrt(np.mean(acc_z_detrend**2)), 4),
            'Z_Kurtosis': round(pd.Series(acc_z_detrend).kurt(), 4),
            'Z_Skewness': round(pd.Series(acc_z_detrend).skew(), 4),
            'Natural_Frequency_Hz': round(peak_freq, 3),  # افزایش دقت استخراج فرکانس به ۳ رقم اعشار
            'Abs_Max_Acceleration': round(np.max(acc_abs), 4),
            'Abs_Mean': round(np.mean(acc_abs), 4)
        }
        return features, xf, fft_amps, t, acc_z_detrend
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def run_batch_processing():
    input_dir = entry_input.get()
    output_dir = entry_output.get()
    
    if not input_dir or not os.path.exists(input_dir):
        messagebox.showerror("خطا", "لطفاً پوشه حاوی فایل‌های CSV را انتخاب کنید.")
        return
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("خطا", "لطفاً مسیر ذخیره‌سازی فایل خروجی را انتخاب کنید.")
        return
        
    file_list = glob.glob(os.path.join(input_dir, "*.csv"))
    if not file_list:
        messagebox.showerror("خطا", "هیچ فایل CSV در پوشه انتخابی پیدا نشد.")
        return
        
    all_features = []
    plt.rcParams['font.family'] = 'serif'
    
    for file_path in file_list:
        # نادیده گرفتن فایل‌های متادیتا نظیر مشخصات سخت‌افزاری دستگاه
        if "device" in os.path.basename(file_path).lower():
            continue
            
        result = extract_signal_features(file_path)
        if result is None: 
            continue
        
        features, xf, fft_amps, t, acc_z = result
        all_features.append(features)
        
        # رسم و ذخیره خودکار نمودارها در صورت فعال بودن گزینه گرافیکی
        if var_plots.get():
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5), dpi=100)
            
            # ۱. نمودار حوزه زمان (شتاب واگرایی زد)
            ax1.plot(t - t[0], acc_z, color='#1f77b4', linewidth=1)
            ax1.set_title(f"Signal Time-Frequency Fingerprint: {features['File_Name']}", fontsize=11, fontweight='bold')
            ax1.set_xlabel("Time (s)", fontsize=9)
            ax1.set_ylabel("Detrended Z Acc ($m/s^2$)", fontsize=9)
            ax1.grid(True, linestyle=':', alpha=0.6)
            
            # ۲. نمودار حوزه فرکانس ارتقایافته (FFT)
            ax2.plot(xf, fft_amps, color='#d62728', linewidth=1.2)
            ax2.axvline(features['Natural_Frequency_Hz'], color='black', linestyle='--', 
                        label=f"Identified Natural Freq: {features['Natural_Frequency_Hz']} Hz")
            ax2.set_xlabel("Frequency (Hz)", fontsize=9)
            ax2.set_ylabel("FFT Amplitude Magnitude", fontsize=9)
            ax2.set_xlim(0, 50)  # تمرکز روی فرکانس‌های مودهای اولیه سازه‌ای
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right', fontsize=9)
            
            plt.tight_layout()
            # ذخیره اتوماتیک نمودارها به صورت تصویر کنار فایل اکسل
            plt.savefig(os.path.join(output_dir, f"Analysis_{os.path.splitext(features['File_Name'])[0]}.png"))
            plt.close()

    # ایجاد ساختار گزارش نهایی در اکسل
    if all_features:
        df_features = pd.DataFrame(all_features)
        
        # ثبت و ذخیره مشخصات فیزیکی و ثابت سنسور گوشی شما (جهت گزارش مستند در پایان‌نامه)
        hardware_info = {
            'Property': ['Sensor Name', 'Vendor', 'Range', 'Resolution', 'Power Consumption'],
            'Value': ['LSM6DSO Acceleration Sensor', 'STMicroelectronics', '78.4532 m/s^2 (~8g)', '0.0023942017 m/s^2', '0.25 mA']
        }
        df_hardware = pd.DataFrame(hardware_info)
        
        excel_path = os.path.join(output_dir, "SHM_Extracted_Features_Report.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df_features.to_excel(writer, sheet_name='Signals_Features', index=False)
            df_hardware.to_excel(writer, sheet_name='Sensor_Hardware_Specs', index=False)
            
        messagebox.showinfo("موفقیت", f"استخراج ویژگی‌ها با موفقیت انجام شد!\n\nفایل اکسل و نمودارها در مسیر زیر ذخیره شدند:\n{excel_path}")
    else:
        messagebox.showwarning("هشدار", "هیچ داده‌ای پردازش نشد.")

def browse_input():
    directory = filedialog.askdirectory()
    if directory: 
        entry_input.delete(0, tk.END)
        entry_input.insert(0, directory)

def browse_output():
    directory = filedialog.askdirectory()
    if directory: 
        entry_output.delete(0, tk.END)
        entry_output.insert(0, directory)

# ساخت رابط کاربری گرافیکی (GUI)
root = tk.Tk()
root.title("سامانه هوشمند استخراج ویژگی‌های پایش سلامت سازه (SHM)")
root.geometry("620x330")
root.configure(bg="#f1f3f5")

font_title = ("Segoe UI", 9, "bold")
font_sub = ("Segoe UI", 10)

# المان‌های آدرس‌دهی فایل‌ها
frame_io = tk.Frame(root, bg="#f1f3f5")
frame_io.pack(fill="x", padx=25, pady=20)

tk.Label(frame_io, text="۱. پوشه حاوی فایل‌های آزمایش (پوشه شامل چندین فایل CSV):", bg="#f1f3f5", font=font_title, fg="#212529").grid(row=0, column=0, sticky='w', pady=(0,5))
entry_input = tk.Entry(frame_io, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#dee2e6", width=45)
entry_input.grid(row=1, column=0, ipady=3, sticky='ew', padx=(0,10))
tk.Button(frame_io, text="انتخاب پوشه ورودی", command=browse_input, bg="#495057", fg="white", font=("Segoe UI", 9), relief="flat", width=15).grid(row=1, column=1, ipady=2)

tk.Label(frame_io, text="۲. مسیر محل ذخیره گزارش اکسل و نمودارها:", bg="#f1f3f5", font=font_title, fg="#212529").grid(row=2, column=0, sticky='w', pady=(15,5))
entry_output = tk.Entry(frame_io, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#dee2e6", width=45)
entry_output.grid(row=3, column=0, ipady=3, sticky='ew', padx=(0,10))
tk.Button(frame_io, text="انتخاب پوشه خروجی", command=browse_output, bg="#495057", fg="white", font=("Segoe UI", 9), relief="flat", width=15).grid(row=3, column=1, ipady=2)

frame_io.columnconfigure(0, weight=1)

# فریم پیکربندی پیشرفته گرافیکی
frame_opts = tk.LabelFrame(root, text=" تنظیمات خروجی گرافیکی ", bg="white", font=font_title, fg="#0d6efd", bd=1, relief="solid")
frame_opts.pack(fill="x", padx=25, pady=(0,20))

var_plots = tk.BooleanVar(value=True)
chk_plots = tk.Checkbutton(frame_opts, text="ترسیم و ذخیره خودکار نمودارهای حوزه زمان و فرکانس ریز شده (FFT) با تکنیک پدینگ برای همه فایل‌ها", 
                           variable=var_plots, bg="white", activebackground="white", font=("Segoe UI", 9))
chk_plots.pack(anchor="w", padx=15, pady=10)

# دکمه پردازش گروهی نهایی
btn_run = tk.Button(root, text="شروع پردازش گروهی و استخراج ماتریس ویژگی‌ها", command=run_batch_processing, 
                    bg="#0d6efd", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", activebackground="#0b5ed7")
btn_run.pack(fill="x", padx=25, ipady=6)

root.mainloop()