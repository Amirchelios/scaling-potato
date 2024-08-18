import tkinter as tk
from tkinter import filedialog

def replace_content_in_selected_files():
    """
    این تابع محتوای فایل منبع را در فایل‌های انتخاب شده توسط کاربر جایگزین می‌کند
    و قبل از کپی کردن، محتوای قبلی فایل هدف را حذف می‌کند.
    """

    source_file = "off.txt"  # مسیر فایل منبع را در اینجا وارد کنید
    selected_files = filedialog.askopenfilenames(title="انتخاب فایل‌های هدف")

    if selected_files:
        with open(source_file, 'r') as f:
            content = f.read()

        for target_file in selected_files:
            with open(target_file, 'w') as f:
                f.write(content)
        print("محتوای فایل با موفقیت در فایل‌های انتخاب شده جایگزین شد.")
    else:
        print("هیچ فایلی انتخاب نشده است.")

# ... بقیه کد رابط کاربری ...
# ایجاد پنجره اصلی
root = tk.Tk()
root.title("جایگزینی محتوا در فایل‌ها")

# دکمه برای شروع عملیات
start_button = tk.Button(root, text="شروع", command=replace_content_in_selected_files)
start_button.pack()

root.mainloop()