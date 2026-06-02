import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def crop_data():
    input_file = entry_input.get()
    output_dir = entry_output.get()
    start_time_str = entry_start.get()
    end_time_str = entry_end.get()
    
    # اعتبار سنجی ورودی‌ها
    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("خطا", "لطفاً یک فایل داده معتبر (.csv) انتخاب کنید.")
        return
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("خطا", "لطفاً مسیر ذخیره‌سازی معتبری را انتخاب کنید.")
        return
        
    try:
        start_time = float(start_time_str)
        end_time = float(end_time_str)
        if start_time < 0 or end_time <= start_time:
            messagebox.showerror("خطا", "زمان شروع و پایان وارد شده معتبر نیست. (زمان پایان باید بزرگتر از زمان شروع باشد)")
            return
    except ValueError:
        messagebox.showerror("خطا", "لطفاً برای زمان‌های شروع و پایان فقط عدد وارد کنید.")
        return
        
    try:
        # خواندن داده‌ها با در نظر گرفتن دلیمیترهای احتمالی (\t یا ,)
        try:
            df = pd.read_csv(input_file, sep='\t')
            if df.shape[1] <= 1:
                df = pd.read_csv(input_file, sep=',')
        except Exception:
            df = pd.read_csv(input_file)
            
        # پیدا کردن ستون زمان
        time_col = [c for c in df.columns if 'time' in c.lower()][0]
        
        # فیلتر کردن داده‌ها بر اساس بازه زمانی وارد شده
        cropped_df = df[(df[time_col] >= start_time) & (df[time_col] <= end_time)]
        
        if cropped_df.empty:
            messagebox.showwarning("هشدار", "هیچ داده‌ای در این بازه زمانی یافت نشد! لطفاً بازه را با توجه به نمودار بررسی کنید.")
            return
            
        # ساخت نام فایل خروجی جدید بر اساس بازه انتخابی
        output_filename = f"Cropped_Data_{start_time:.1f}s_to_{end_time:.1f}s.csv"
        full_output_path = os.path.join(output_dir, output_filename)
        
        # ذخیره فایل جدید با فرمت استاندارد کاما دلیمیتد (CSV) همراه با حفظ ستون‌ها و بدون ایندکس اضافه
        cropped_df.to_csv(full_output_path, index=False, sep=',')
        
        # نمایش اطلاعات آماری کوچک به کاربر برای اطمینان
        messagebox.showinfo("موفقیت", 
                            f"فایل جدید با موفقیت برش داده و ذخیره شد!\n\n"
                            f"تعداد ردیف‌های استخراج شده: {len(cropped_df)} ردیف\n"
                            f"محل ذخیره:\n{full_output_path}")
                            
    except Exception as e:
        messagebox.showerror("خطا در پردازش", f"خطایی در حین برش داده‌ها رخ داد:\n{str(e)}")

# توابع کمکی پنجره گرافیکی
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

# ساخت رابط کاربری گرافیکی
root = tk.Tk()
root.title("سامانه برش سیگنال و جداسازی بازه آزمایش")
root.geometry("580x320")
root.resizable(False, False)
root.configure(bg="#f4f4f6")

font_label = ("Tahoma", 9, "bold")
font_entry = ("Arial", 10)

# بخش انتخاب فایل ورودی
lbl_input = tk.Label(root, text="فایل داده اصلی (Raw Data.csv):", bg="#f4f4f6", font=font_label, anchor='w')
lbl_input.place(x=20, y=15, width=200, height=25)
entry_input = tk.Entry(root, font=font_entry, bd=1, relief="solid")
entry_input.place(x=20, y=40, width=420, height=28)
btn_input = tk.Button(root, text="انتخاب فایل", command=browse_input, bg="#e1e1e5", font=("Tahoma", 9))
btn_input.place(x=450, y=40, width=100, height=28)

# بخش انتخاب پوشه خروجی
lbl_output = tk.Label(root, text="محل ذخیره فایل خروجی جدید:", bg="#f4f4f6", font=font_label, anchor='w')
lbl_output.place(x=20, y=85, width=200, height=25)
entry_output = tk.Entry(root, font=font_entry, bd=1, relief="solid")
entry_output.place(x=20, y=110, width=420, height=28)
btn_output = tk.Button(root, text="انتخاب پوشه", command=browse_output, bg="#e1e1e5", font=("Tahoma", 9))
btn_output.place(x=450, y=110, width=100, height=28)

# بخش وارد کردن فواصل زمانی (بازه پنجره ارتعاش)
lbl_time_section = tk.Label(root, text="تعیین بازه زمانی جهت برش سیگنال (بر حسب ثانیه):", bg="#f4f4f6", font=font_label, anchor='w')
lbl_time_section.place(x=20, y=160, width=350, height=25)

lbl_start = tk.Label(root, text="از زمان (شروع):", bg="#f4f4f6", font=("Tahoma", 9))
lbl_start.place(x=20, y=195, width=90, height=25)
entry_start = tk.Entry(root, font=font_entry, bd=1, relief="solid", justify='center')
entry_start.place(x=115, y=195, width=100, height=25)
entry_start.insert(0, "75.0")  # مقدار پیش‌فرض نمونه بر اساس زمان ضربه شما

lbl_end = tk.Label(root, text="تا زمان (پایان):", bg="#f4f4f6", font=("Tahoma", 9))
lbl_end.place(x=260, y=195, width=90, height=25)
entry_end = tk.Entry(root, font=font_entry, bd=1, relief="solid", justify='center')
entry_end.place(x=355, y=195, width=100, height=25)
entry_end.insert(0, "90.0")  # مقدار پیش‌فرض نمونه

# دکمه اجرای اصلی عملیات برش
btn_run = tk.Button(root, text="برش سیگنال و خروجی CSV جدید", command=crop_data, bg="#0078d4", fg="white", font=("Tahoma", 10, "bold"), relief="flat")
btn_run.place(x=160, y=250, width=260, height=42)

root.mainloop()