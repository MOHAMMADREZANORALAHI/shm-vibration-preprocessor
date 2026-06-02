import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import detrend, butter, filtfilt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# فیلتر دیجیتال میان‌گذر باترورث
def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def execute_preprocessing():
    input_file = entry_input.get()
    output_dir = entry_output.get()
    
    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("خطا", "لطفاً یک فایل داده معتبر (CSV) انتخاب کنید.")
        return
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("خطا", "لطفاً مسیر ذخیره‌سازی را انتخاب کنید.")
        return
        
    try:
        df = pd.read_csv(input_file)
        time_col = [c for c in df.columns if 'time' in c.lower()][0]
        
        t_raw = df[time_col].values.copy()
        dt = np.mean(np.diff(t_raw))
        fs = 1.0 / dt
        
        # کنترل فرکانس نایکویست
        if var_filter.get():
            lowcut = float(entry_low.get())
            highcut = float(entry_high.get())
            forder = int(entry_order.get())
            if highcut >= 0.5 * fs:
                messagebox.showerror("خطا فرکانسی", f"فرکانس بالا ({highcut} Hz) باید کمتر از نصف فرکانس سنسور ({0.5*fs:.1f} Hz) باشد.")
                return

        selected_axis = combo_axis.get()
        
        # تشخیص نگاشت ستون‌ها
        axis_mapping = {
            'x': [c for c in df.columns if 'x' in c.lower()][0],
            'y': [c for c in df.columns if 'y' in c.lower()][0],
            'z': [c for c in df.columns if 'z' in c.lower()][0],
            'Absolute': [c for c in df.columns if 'absolute' in c.lower() or 'total' in c.lower()][0]
        }
        
        # تعیین لیست جهت‌ها برای پردازش
        if selected_axis == "All Channels (x, y, z, Absolute)":
            axes_to_process = ['x', 'y', 'z', 'Absolute']
        else:
            axes_to_process = [selected_axis]
            
        # دیکشنری برای ذخیره نتایج نهایی
        output_data = {}
        
        # ماژول نرمال‌سازی مبدأ زمان
        if var_time_norm.get():
            t_processed = t_raw - t_raw[0]
        else:
            t_processed = t_raw.copy()
            
        output_data['Time_Processed'] = t_processed
        
        # حلقه پردازش روی کانال‌های انتخاب شده
        for axis in axes_to_process:
            col_name = axis_mapping[axis]
            acc_signal = df[col_name].values.copy()
            
            # ۱. حذف روند و میانگین
            if var_detrend.get():
                acc_signal = detrend(acc_signal, type='linear')
                acc_signal = acc_signal - np.mean(acc_signal)
                
            # ۲. فیلتر فرکانسی
            if var_filter.get():
                acc_signal = butter_bandpass_filter(acc_signal, lowcut, highcut, fs, order=forder)
                
            # ۳. نرمال‌سازی دامنه
            scaling_method = combo_scale.get()
            if scaling_method == "Standardization (Z-Score)":
                acc_signal = (acc_signal - np.mean(acc_signal)) / np.std(acc_signal)
            elif scaling_method == "Min-Max Scaling [-1, 1]":
                acc_min, acc_max = np.min(acc_signal), np.max(acc_signal)
                if acc_max != acc_min:
                    acc_signal = 2.0 * ((acc_signal - acc_min) / (acc_max - acc_min)) - 1.0
                    
            output_data[f'Acc_{axis}_Processed'] = acc_signal

        # ذخیره در فایل CSV
        processed_df = pd.DataFrame(output_data)
        base_name = os.path.basename(input_file)
        suffix = "All_Channels" if len(axes_to_process) > 1 else selected_axis
        output_name = f"Custom_SHM_{suffix}_{base_name}"
        full_out_path = os.path.join(output_dir, output_name)
        processed_df.to_csv(full_out_path, index=False)
        
        # رسم پلات تعاملی متناسب با تعداد کانال‌ها
        plt.rcParams['font.family'] = 'serif'
        num_plots = len(axes_to_process)
        
        fig, axs = plt.subplots(num_plots, 1, figsize=(11, 2.3 * num_plots + 1), sharex=True, dpi=100)
        if num_plots == 1:
            axs = [axs]
            
        colors = {'x': '#1f77b4', 'y': '#2ca02c', 'z': '#ff7f0e', 'Absolute': '#d62728'}
        
        for i, axis in enumerate(axes_to_process):
            raw_col = axis_mapping[axis]
            axs[i].plot(df[time_col].values - (df[time_col].values[0] if var_time_norm.get() else 0), 
                        df[raw_col].values, color='gray', alpha=0.35, label='Raw Input')
            axs[i].plot(t_processed, output_data[f'Acc_{axis}_Processed'], 
                        color=colors[axis], linewidth=1.1, label=f'Processed {axis}')
            axs[i].set_ylabel(f'Amplitude ({axis})', fontsize=9, fontweight='bold')
            axs[i].grid(True, linestyle=':', alpha=0.6)
            axs[i].legend(loc='upper right', fontsize=8)
            
        axs[0].set_title(f"SHM Multi-Channel Controlled Preprocessing Evaluation ({base_name})", fontsize=11, fontweight='bold', pad=10)
        axs[-1].set_xlabel('Time (s)' if not var_time_norm.get() else 'Normalized Time ($t_0=0$) (s)', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        messagebox.showinfo("موفقیت دیتای سازه", 
                            f"عملیات با موفقیت روی {num_plots} کانال انجام شد!\n\n"
                            f"نرخ فرکانس سنسور: {fs:.1f} هرتز\n"
                            f"ذخیره شده با نام:\n{output_name}")
        plt.show()
        
    except Exception as e:
        messagebox.showerror("خطا در پردازش", f"خطایی در اعمال فیلترها رخ داد:\n{str(e)}")

def browse_input():
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filename: entry_input.delete(0, tk.END); entry_input.insert(0, filename)

def browse_output():
    directory = filedialog.askdirectory()
    if directory: entry_output.delete(0, tk.END); entry_output.insert(0, directory)

# ساخت پنجره اصلی با استایل و دکوراسیون شکیل‌تر
root = tk.Tk()
root.title("داشبورد کنترلی و پیش‌پردازش پیشرفته سیگنال - پایش سلامت سازه")
root.geometry("640x510")
root.configure(bg="#f8f9fa")

# استایل‌دهی به ComboBox ها
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="white", background="#e9ecef")

font_title = ("Segoe UI", 9, "bold")
font_sub = ("Segoe UI", 10)

# بخش آدرس‌دهی فایل‌ها
frame_files = tk.Frame(root, bg="#f8f9fa")
frame_files.pack(fill="x", padx=25, pady=15)

tk.Label(frame_files, text="فایل ورودی ارتعاشات آزمایش (CSV):", bg="#f8f9fa", font=font_title, fg="#343a40").grid(row=0, column=0, sticky='w', pady=(0,5))
entry_input = tk.Entry(frame_files, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#ced4da", width=50)
entry_input.grid(row=1, column=0, ipady=3, sticky='ew', padx=(0,10))
# اصلاح عرض دکمه در زمان تعریف آن (width=12)
tk.Button(frame_files, text="انتخاب فایل", command=browse_input, bg="#6c757d", fg="white", font=("Segoe UI", 9), relief="flat", activebackground="#495057", width=12).grid(row=1, column=1, ipady=2)

tk.Label(frame_files, text="مسیر خروجی ذخیره‌سازی داده‌های تمیز:", bg="#f8f9fa", font=font_title, fg="#343a40").grid(row=2, column=0, sticky='w', pady=(10,5))
entry_output = tk.Entry(frame_files, font=font_sub, bd=1, relief="solid", highlightthickness=1, highlightbackground="#ced4da", width=50)
entry_output.grid(row=3, column=0, ipady=3, sticky='ew', padx=(0,10))
# اصلاح عرض دکمه در زمان تعریف آن (width=12)
tk.Button(frame_files, text="انتخاب پوشه", command=browse_output, bg="#6c757d", fg="white", font=("Segoe UI", 9), relief="flat", activebackground="#495057", width=12).grid(row=3, column=1, ipady=2)

frame_files.columnconfigure(0, weight=1)

# فریم اصلی تنظیمات سیگنال (ماژولار)
frame_modules = tk.LabelFrame(root, text="  پیکربندی فیلترها و ماتریس کنترلرها  ", bg="white", font=font_title, fg="#0d6efd", bd=1, relief="solid")
frame_modules.pack(fill="both", expand=True, padx=25, pady=(0,15))

# ردیف ۱: انتخاب کانال
tk.Label(frame_modules, text="۱. کانال شتاب‌سنج هدف:", bg="white", font=("Segoe UI", 9)).place(x=20, y=18)
combo_axis = ttk.Combobox(frame_modules, values=["z", "x", "y", "Absolute", "All Channels (x, y, z, Absolute)"], state="readonly")
combo_axis.place(x=240, y=18, width=280, height=24)
combo_axis.current(4)

# ردیف ۲: میانگین‌گیری
var_detrend = tk.BooleanVar(value=True)
chk_detrend = tk.Checkbutton(frame_modules, text="۲. حذف خطای ماندگار، روند خطی و میانگین سیگنال (Detrend)", variable=var_detrend, bg="white", activebackground="white", font=("Segoe UI", 9))
chk_detrend.place(x=20, y=52)

# ردیف ۳: فیلتر فرکانس
var_filter = tk.BooleanVar(value=True)
chk_filter = tk.Checkbutton(frame_modules, text="۳. اعمال فیلتر فرکانسی میان‌گذر دیجیتال (Bandpass Filter)", variable=var_filter, bg="white", activebackground="white", font=("Segoe UI", 9))
chk_filter.place(x=20, y=85)

# باکس زیرپارامترهای فیلتر فرکانسی
tk.Label(frame_modules, text="فرکانس پایین (Low Hz):", bg="white", fg="#495057").place(x=45, y=115)
entry_low = tk.Entry(frame_modules, font=font_sub, justify='center', bd=1, relief="solid", highlightthickness=1, highlightbackground="#ced4da")
entry_low.place(x=180, y=115, width=70, height=22)
entry_low.insert(0, "0.5")

tk.Label(frame_modules, text="فرکانس بالا (High Hz):", bg="white", fg="#495057").place(x=280, y=115)
entry_high = tk.Entry(frame_modules, font=font_sub, justify='center', bd=1, relief="solid", highlightthickness=1, highlightbackground="#ced4da")
entry_high.place(x=410, y=115, width=70, height=22)
entry_high.insert(0, "45.0")

tk.Label(frame_modules, text="درجه فیلتر (Order):", bg="white", fg="#495057").place(x=45, y=145)
entry_order = tk.Entry(frame_modules, font=font_sub, justify='center', bd=1, relief="solid", highlightthickness=1, highlightbackground="#ced4da")
entry_order.place(x=180, y=145, width=70, height=22)
entry_order.insert(0, "4")

# ردیف ۴: زمان
var_time_norm = tk.BooleanVar(value=True)
chk_time = tk.Checkbutton(frame_modules, text="۴. همگام‌سازی و تغییر مبدأ زمان آزمایش به صفر مطلق (t0 = 0)", variable=var_time_norm, bg="white", activebackground="white", font=("Segoe UI", 9))
chk_time.place(x=20, y=180)

# ردیف ۵: نرمال‌سازی دامنه
tk.Label(frame_modules, text="۵. تکنیک مقیاس‌دهی دامنه (Scaling):", bg="white", font=("Segoe UI", 9)).place(x=20, y=215)
combo_scale = ttk.Combobox(frame_modules, values=["None", "Standardization (Z-Score)", "Min-Max Scaling [-1, 1]"], state="readonly")
combo_scale.place(x=240, y=215, width=220, height=24)
combo_scale.current(1)

# دکمه اجرای نهایی و شکیل پایین صفحه
btn_run = tk.Button(root, text="پردازش هوشمند و نمایش پلات مقایسه‌ای", command=execute_preprocessing, bg="#0d6efd", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", activebackground="#0b5ed7")
btn_run.pack(fill="x", padx=25, pady=(0,20), ipady=6)

root.mainloop()