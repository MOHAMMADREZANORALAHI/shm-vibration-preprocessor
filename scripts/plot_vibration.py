import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

def process_and_plot():
    input_file = entry_input.get()
    output_dir = entry_output.get()
    
    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("خطا", "لطفاً یک فایل داده معتبر (.csv) انتخاب کنید.")
        return
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("خطا", "لطفاً مسیر ذخیره‌سازی معتبری را انتخاب کنید.")
        return
        
    try:
        # خواندن داده‌ها با جداکننده تب یا کاما
        try:
            df = pd.read_csv(input_file, sep='\t')
            if df.shape[1] <= 1:
                df = pd.read_csv(input_file, sep=',')
        except Exception:
            df = pd.read_csv(input_file)
            
        # انطباق نام ستون‌ها با ساختار فایل
        time_col = [c for c in df.columns if 'time' in c.lower()][0]
        acc_x = [c for c in df.columns if 'x' in c.lower()][0]
        acc_y = [c for c in df.columns if 'y' in c.lower()][0]
        acc_z = [c for c in df.columns if 'z' in c.lower()][0]
        acc_abs = [c for c in df.columns if 'absolute' in c.lower() or 'total' in c.lower()][0]
        
        t = df[time_col].values
        x = df[acc_x].values
        y = df[acc_y].values
        z = df[acc_z].values
        abs_acc = df[acc_abs].values
        
        # پیدا کردن لحظه پیک ضربه
        max_idx = df[acc_abs].idxmax()
        t_impact = t[max_idx]
        val_impact = abs_acc[max_idx]
        
        # تنظیمات فونت و ظاهر مهندسی
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['axes.linewidth'] = 1.0
        
        # ایجاد ۴ زیرنمودار مجزا که محور زمان (x) آن‌ها به هم قفل (sharex) است
        # این ویژگی باعث می‌شود وقتی روی محور زمانِ یکی از نمودارها زوم می‌کنید، بقیه هم همزمان زوم شوند
        fig, axs = plt.subplots(4, 1, figsize=(11, 9), sharex=True, dpi=100)
        
        # ۱. راستای X
        axs[0].plot(t, x, color='#1f77b4', linewidth=0.8)
        axs[0].set_ylabel('$a_x$ $(m/s^2)$', fontsize=10, fontweight='bold')
        axs[0].set_title('Directional Time-History Analysis (Cantilever Beam Impact Test)', fontsize=12, fontweight='bold', pad=12)
        axs[0].grid(True, linestyle=':', alpha=0.6)
        
        # ۲. راستای Y
        axs[1].plot(t, y, color='#2ca02c', linewidth=0.8)
        axs[1].set_ylabel('$a_y$ $(m/s^2)$', fontsize=10, fontweight='bold')
        axs[1].grid(True, linestyle=':', alpha=0.6)
        
        # ۳. راستای Z (راستای اصلی ارتعاش خمشی تیر طره‌ای در اکثر آزمایش‌ها)
        axs[2].plot(t, z, color='#ff7f0e', linewidth=0.8)
        axs[2].set_ylabel('$a_z$ $(m/s^2)$', fontsize=10, fontweight='bold')
        axs[2].grid(True, linestyle=':', alpha=0.6)
        
        # ۴. شتاب مطلق + نشانگر زمان ضربه
        axs[3].plot(t, abs_acc, color='#d62728', linewidth=0.9)
        axs[3].scatter(t_impact, val_impact, color='black', s=30, zorder=5, 
                       label=f'Max Impact: {t_impact:.3f} s')
        axs[3].set_ylabel('$a_{abs}$ $(m/s^2)$', fontsize=10, fontweight='bold')
        axs[3].set_xlabel('Time $(Seconds)$', fontsize=11, fontweight='bold')
        axs[3].grid(True, linestyle=':', alpha=0.6)
        axs[3].legend(loc='upper right', fontsize=9, frameon=True)
        
        # رسم یک خط‌چین عمودی در تمام نمودارها برای مشخص کردن لحظه ضربه
        for ax in axs:
            ax.axvline(x=t_impact, color='purple', linestyle='--', linewidth=0.8, alpha=0.7)
            
        plt.tight_layout()
        
        # مسیر پیش‌فرض برای ذخیره اتوماتیک نسخه اولیه
        default_save_path = os.path.join(output_dir, 'Detailed_Time_History.png')
        plt.savefig(default_save_path, dpi=300, bbox_inches='tight')
        
        # نمایش پنجره تعاملی به کاربر (برنامه تا زمان بستن این پنجره منتظر می‌ماند)
        messagebox.showinfo("راهنما", "نمودار تعاملی باز خواهد شد.\n\nاز ابزار دکمه ذره‌بین (Zoom) در پایین پنجره نمودار استفاده کنید تا بتوانید روی بازه زمانی ضربه زوم کنید و داده‌ها را با دقت میلی‌ثانیه ببینید.")
        plt.show()
        
    except Exception as e:
        messagebox.showerror("خطا در پردازش", f"خطایی رخ داد:\n{str(e)}")

def browse_input():
    filename = filedialog.askopenfilename(title="انتخاب فایل داده آزمایش (CSV)", filetypes=[("CSV Files", "*.csv")])
    if filename:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, filename)

def browse_output():
    directory = filedialog.askdirectory(title="انتخاب پوشه خروجی")
    if directory:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, directory)

# ساخت پنجره GUI
root = tk.Tk()
root.title("سامانه تحلیل ارتعاشات تیر - تفکیک جهات")
root.geometry("580x250")
root.resizable(False, False)
root.configure(bg="#f4f4f6")

font_label = ("Tahoma", 9, "bold")
font_entry = ("Arial", 10)

lbl_input = tk.Label(root, text="فایل داده خام (Raw Data.csv):", bg="#f4f4f6", font=font_label, anchor='w')
lbl_input.place(x=20, y=20, width=200, height=25)
entry_input = tk.Entry(root, font=font_entry, bd=1, relief="solid")
entry_input.place(x=20, y=50, width=420, height=28)
btn_input = tk.Button(root, text="انتخاب فایل", command=browse_input, bg="#e1e1e5", font=("Tahoma", 9))
btn_input.place(x=450, y=50, width=100, height=28)

lbl_output = tk.Label(root, text="محل ذخیره‌سازی پیش‌فرض:", bg="#f4f4f6", font=font_label, anchor='w')
lbl_output.place(x=20, y=95, width=200, height=25)
entry_output = tk.Entry(root, font=font_entry, bd=1, relief="solid")
entry_output.place(x=20, y=125, width=420, height=28)
btn_output = tk.Button(root, text="انتخاب پوشه", command=browse_output, bg="#e1e1e5", font=("Tahoma", 9))
btn_output.place(x=450, y=125, width=100, height=28)

btn_run = tk.Button(root, text="نمایش نمودار تعاملی و تفکیکی", command=process_and_plot, bg="#2ca02c", fg="white", font=("Tahoma", 10, "bold"), relief="flat")
btn_run.place(x=160, y=185, width=260, height=40)

root.mainloop()