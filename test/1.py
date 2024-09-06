import msvcrt
import os
import random
import re
import subprocess
import sys
import time
import keyboard
import qrcode
import tkinter as tk
import datetime
from tqdm import tqdm
from khayyam import JalaliDate
import requests
import base64
import json
import pyperclip  # اضافه کردن pyperclip برای کپی به کلیپبورد


# غیرفعال کردن هشدار مربوط به C extension در khayyam
import warnings
warnings.filterwarnings("ignore", message="The C extension is not available.")

# --- اطلاعات GitHub ---
github_username = "Amirchelios"  # نام کاربری GitHub شما
github_repo = "scaling-potato"  # نام مخزن GitHub شما
github_token = "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"  # توکن GitHub شما را اینجا قرار دهید

# --- متغیرهای سراسری ---
users_data = {}  # دیکشنری برای نگهداری اطلاعات کاربران از فایل‌ها
files_cache = {}  # دیکشنری برای نگهداری محتوای فایل‌های GitHub

# --- توابع کمکی ---

def clear_screen():
    """صفحه ترمینال را پاک می‌کند."""
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_screen(text="HI VPN", duration=3):
    """صفحه لودینگ ترمینالی را نمایش می‌دهد."""
    start_time = time.time()
    while time.time() - start_time < duration:
        clear_screen()
        x = random.randint(0, os.get_terminal_size().columns - len(text))
        y = random.randint(0, os.get_terminal_size().lines - 1)
        print("\033[{};{}H{}".format(y, x, text))
        time.sleep(0.4)

def check_and_change_language():
    clear_screen()
    """
    این تابع از کاربر می‌خواهد یک حرف وارد کند و زبان صفحه کلید را بررسی می‌کند.
    اگر زبان انگلیسی نباشد، آن را به انگلیسی تغییر می‌دهد.
    """
    while True:
        print("Lotfan Yek Harf Vared Konid ?!")
        char = input()
        if len(char) == 1:
            if char.isascii() and char.isalpha():
                break
            else:
                try:
                    keyboard.press_and_release('alt+shift')
                    break
                except ValueError:
                    break
        else:
            print("Lotfan Yek Harf Vared Konid ?!")

check_and_change_language()

def my_long_running_task():
    """یک عملیات طولانی مدت شبیه‌سازی شده را نمایش می‌دهد."""
    for _ in tqdm(range(100), desc="    Waiting  "):
        time.sleep(0.03)

def generate_qr_code(text):
    """
    یک کد QR از متن داده شده ایجاد می‌کند و آن را در یک پنجره نمایش می‌دهد.
    """
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=15, border=8)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("myqrcode.png")

    root = tk.Tk()
    root.title(" QR user ")
    img_tk = tk.PhotoImage(file="myqrcode.png")
    img_label = tk.Label(root, image=img_tk)
    img_label.pack()

    # پنجره را در مرکز صفحه نمایش قرار دهید
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.focus_force()

    def close_window(event):
        root.destroy()

    root.bind_all("<Key>", close_window)
    root.mainloop()

def get_file_from_github(file_path):
    """محتوای فایل را از GitHub می‌خواند و در حافظه نهان (cache) ذخیره می‌کند."""
    if file_path not in files_cache:
        api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/test/program/{file_path}"
        headers = {"Authorization": f"token {github_token}"}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            content = base64.b64decode(response.json()["content"]).decode()
            files_cache[file_path] = content
        else:
            raise Exception(f"Erorr Dar Daryafte File ! {response.text}")
    return files_cache[file_path]

def update_file_on_github(file_path, new_content, commit_message="Update file"):
    """محتوای فایل را در GitHub به‌روزرسانی می‌کند و حافظه نهان را به‌روز می‌کند."""
    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/test/program/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # دریافت SHA فعلی فایل (برای به‌روزرسانی)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        raise Exception(f"Erorr Dar Sha {response.text}")

    # به‌روزرسانی فایل
    data = {
        "message": commit_message,
        "content": base64.b64encode(new_content.encode()).decode(),
        "sha": sha
    }
    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 200:
        #print(f"فایل {file_path} با موفقیت به‌روزرسانی شد.")
        # به‌روزرسانی حافظه نهان
        files_cache[file_path] = new_content
    else:
        raise Exception(f"Erorr Dar Beroz Rasani !! {response.text}")

def load_users_data():
    """
    اطلاعات کاربران را از فایل‌های GitHub می‌خواند و در دیکشنری users_data ذخیره می‌کند.
    """
    global users_data
    users_data = {}
    for operator in ["irancell", "mci"]:
        filename = f"allnet.txt" if operator == "irancell" else "hamrah.txt"
        try:
            content = get_file_from_github(filename)
            lines = content.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("Number:"):
                    number = line.split(":")[1].strip()
                    expire_date_str = lines[i + 1].split(":")[1].strip()
                    expire_date = JalaliDate.strptime(expire_date_str, '%Y-%m-%d')
                    name = lines[i + 2].split(":")[1].strip()
                    shomare = lines[i + 3].split(":")[1].strip()
                    users_data[number] = {
                        "operator": operator,
                        "expire_date": expire_date,
                        "name": name,
                        "shomare": shomare
                    }
                    i += 4
                else:
                    i += 1
        except Exception as e:
            print(f"Erorr Dar Khandane Etelaat !!{filename}: {e}")

def save_users_data():
    """
    اطلاعات کاربران را از دیکشنری users_data به فایل‌های GitHub برمی‌گرداند.
    """
    for operator in ["irancell", "mci"]:
        filename = f"allnet.txt" if operator == "irancell" else "hamrah.txt"
        new_content = ""
        for number, user_info in users_data.items():
            if user_info["operator"] == operator:
                new_content += f"Number: {number}\n"
                new_content += f"Expire Date: {user_info['expire_date'].strftime('%Y-%m-%d')}\n"
                new_content += f"name: {user_info['name']}\n"
                new_content += f"Shomare: {user_info['shomare']}\n\n"
        update_file_on_github(filename, new_content)


def create_file_on_github(file_path, file_content, commit_message):
    """
    یک فایل جدید در گیت‌هاب می‌سازد و محتوا را در آن کپی می‌کند.
    """
    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # تبدیل محتوا به base64
    encoded_content = base64.b64encode(file_content.encode()).decode()

    # ساخت درخواست برای API گیت‌هاب
    data = {
        "message": commit_message,
        "content": encoded_content
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Ok.")
    else:
        print(f"Erorr Dar Sakhte File !!! {response.text}")





#ساخت کد برخط

# اطلاعات GitHub
github_username = "Amirchelios"  # نام کاربری GitHub شما
github_repo = "scaling-potato"  # نام مخزن GitHub شما
github_token = "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"  # توکن GitHub شما را اینجا قرار دهید

def get_file_content(file_path):
  """
  محتوای فایل را از GitHub می‌خواند.

  Args:
      file_path: مسیر فایل در مخزن GitHub.

  Returns:
      str: محتوای فایل.
  """
  api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
  headers = {"Authorization": f"token {github_token}"}
  response = requests.get(api_url, headers=headers)

  if response.status_code == 200:
    content = base64.b64decode(response.json()["content"]).decode()
    return content
  else:
    raise Exception(f"Erorr Dar Daryafte File !! {response.text}")

def create_file_on_github(file_path, file_content, commit_message):
    """
    یک فایل جدید در گیت‌هاب می‌سازد و محتوا را در آن کپی می‌کند.
    """
    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # تبدیل محتوا به base64
    encoded_content = base64.b64encode(file_content.encode()).decode()

    # ساخت درخواست برای API گیت‌هاب
    data = {
        "message": commit_message,
        "content": encoded_content
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Ok.")
    else:
        print(f"Erorr Dar Sakhte File !!! {response.text} ")

def create_user_file(operator, number):
    """
    این تابع با دریافت operator و number، فایل مورد نظر را از GitHub خوانده 
    و یک فایل جدید با نام number.txt در GitHub ایجاد می‌کند.

    Args:
        operator (str): نوع اپراتور ("allnet" یا "hamrah")
        number (str): شناسه کاربر 
    """
    if operator == "irancell":
        file_path = "s.allnet.txt"
        destination_path = f"test/file/irancell/{number}.txt"  # مسیر مخصوص ایرانسل
    elif operator == "mci":
        file_path = "s.hamrah.txt"
        destination_path = f"test/file/mci/{number}.txt"  # مسیر مخصوص همراه اول
    else:
        print("Erorr Dar Etebar")
        return
    

    try:
        response = requests.get(
            f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{destination_path}",
            headers={"Authorization": f"token {github_token}"}
        )
        if response.status_code == 200:
            clear_screen()
            # فایل وجود دارد
            print("Be Dalil Etmam Mohlat Nemitavanid Az In Ghesmat Eghdami Konid !!!")
            print()
            print("Bastan Barname ...")
            time.sleep(5)
            # راه اندازی مجدد برنامه با os.execv
            os.execv(sys.executable, [sys.executable] + sys.argv)
        elif response.status_code == 404:
            # فایل وجود ندارد، ادامه مراحل ساخت فایل
            pass  # به ساخت فایل ادامه دهید
        else:
            print(f"Erorr Dar Baresi Etelaat !! {response.status_code}")
            return
    except Exception as e:
        print(f"Erorr Dar Baresi Vojod {e}")
        return    

    
    
    try:
        file_content = get_file_content(file_path)
    except Exception as e:
        print(f"Erorr !!: {e}")
        return

    try:
        create_file_on_github(destination_path, file_content, f"ساخت فایل جدید با شناسه {number} از {file_path}")
    except Exception as e:
        print(f"Erorr Dar Sakht !! {e}")





def delete_file_from_github(file_path, commit_message="Delete file"):
    """
    فایل مشخص شده را از GitHub حذف می‌کند.

    Args:
        file_path (str): مسیر فایل در GitHub (مثلاً "test/file/irancell/1234567890.txt")
        commit_message (str, optional): پیام کامیت برای حذف. مقدار پیش‌فرض "Delete file" است.
    """
    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # دریافت SHA فعلی فایل (برای حذف)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        print(f"Erorr Dar sha {response.text}")
        return

    # حذف فایل
    data = {
        "message": commit_message,
        "sha": sha
    }
    response = requests.delete(api_url, headers=headers, json=data)

    if response.status_code == 200:
        #print(f"File{file_path}")
        # حذف فایل از حافظه نهان (در صورت وجود)
        files_cache.pop(file_path, None)
    else:
        print(f"Erorr Dar Hazf !! {response.text}")



def upload_number_to_github(file_path, number_to_add, commit_message="Update number"):
    """
    یک عدد را به عددی که از قبل در یک فایل متنی در GitHub وجود دارد، اضافه کرده و نتیجه را در فایل ذخیره می‌کند.

    Args:
        file_path (str): مسیر فایل در GitHub (مثلاً "test/number.txt")
        number_to_add (int): عددی که باید به عدد موجود در فایل اضافه شود.
        commit_message (str, optional): پیام کامیت برای به‌روزرسانی. 
                                         مقدار پیش‌فرض "Update number" است.
    """

    # --- اطلاعات GitHub ---
    github_username = "Amirchelios"  # نام کاربری GitHub شما
    github_repo = "scaling-potato"  # نام مخزن GitHub شما
    github_token = "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"  # توکن GitHub شما را اینجا قرار دهید

    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/test/program/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # --- 1. خواندن عدد فعلی از فایل ---
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            current_number_str = base64.b64decode(response.json()["content"]).decode()
            try:
                current_number = int(current_number_str)
            except ValueError:
                print("Add Mojod Na Motabar Ast !!")
                return
        else:
            print(f"Erorr {response.text}")
            return
    except Exception as e:
        print(f"Erorr: {e}")
        return

    # --- 2. اضافه کردن عدد جدید ---
    new_number = current_number + number_to_add

    # --- 3. به‌روزرسانی فایل با عدد جدید ---
    # دریافت SHA فعلی فایل (برای به‌روزرسانی)
    try:
        sha = response.json()["sha"]
    except KeyError:
        print(f"Erorr Dar Daryaft {file_path}")
        return

    # تبدیل عدد جدید به رشته و سپس به base64
    new_content = str(new_number)
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # به‌روزرسانی فایل
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Movafahg Dar Beroz Rasani .")
    else:
        print(f"Eror Dar Beroz Rasani File !! {response.text}")



def add_to_number_in_github_file_prise(file_path, number_to_add, commit_message="Update number"):
    """
    یک عدد را از یک فایل در GitHub می‌خواند، 
    عدد داده شده را به آن اضافه می‌کند و 
    نتیجه را در همان فایل در GitHub ذخیره می‌کند.

    Args:
        file_path (str): مسیر فایل در GitHub (مثلاً "test/number.txt")
        number_to_add (int): عددی که باید به عدد موجود در فایل اضافه شود.
        commit_message (str, optional): پیام کامیت برای به‌روزرسانی. 
                                         مقدار پیش‌فرض "Update number" است.
    """

    # --- اطلاعات GitHub ---
    github_username = "Amirchelios"  # نام کاربری GitHub شما
    github_repo = "scaling-potato"  # نام مخزن GitHub شما
    github_token = "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"  # توکن GitHub شما را اینجا قرار دهید

    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/vnd.github.v3+json"
    }

    # --- 1. خواندن عدد فعلی از فایل ---
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            current_number_str = base64.b64decode(response.json()["content"]).decode()
            try:
                current_number = int(current_number_str)
            except ValueError:
                current_number = 0  # در صورت عدم وجود عدد معتبر، 0 را در نظر بگیرید

        else:
            print(f"Erorr")
            return
    except Exception as e:
        print(f"Erorr")
        return

    # --- 2. اضافه کردن عدد جدید ---
    new_number = current_number + number_to_add

    # --- 3. به‌روزرسانی فایل با عدد جدید ---
    # دریافت SHA فعلی فایل (برای به‌روزرسانی)
    try:
        sha = response.json()["sha"]
    except KeyError:
        print(f"Erorr")
        return

    # تبدیل عدد جدید به رشته و سپس به base64
    new_content = str(new_number)
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # به‌روزرسانی فایل
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Movafagh Dar Beroz Rasani .")
    else:
        print(f"Erorr {response.text}")






def search_and_update(number, operator):
    """
    یک شماره را در دیکشنری users_data جستجو می‌کند و در صورت وجود، گزینه‌های نمایش، تمدید یا حذف را ارائه می‌دهد.
    در غیر این صورت، یک پروفایل جدید ایجاد می‌کند.
    """


    global users_data
    if any(user_info["operator"] == operator and number == user_number for user_number, user_info in users_data.items()):
        clear_screen()
        print("User Vojod Darad !!!\n")
                                # سوال از کاربر برای تایید تمدید
        confirm = input("ٍEdame ??  (y/n): ")
        if confirm.lower() != "y":
            # در صورت عدم تایید، برنامه مجددا شروع می‌شود
            subprocess.Popen([sys.executable, __file__])  # شروع یک فرآیند جدید
            sys.exit(0)  # خروج کامل از فرآیند فعلی


        
        print("Entekhab Kon??\n")

        while True:
            choice = input("Namayesh QR(1)\n   \nTamdid(2)\n   \n \n \n ")
            if choice == '1':
                create_user_file(operator, number)  # ساخت فایل برای کاربر allnet با شناسه 1234567890
                clear_screen()
                pyperclip.copy(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
                print("Link Dar Hafeze Zakhire Shod !!!")
                my_long_running_task()
                generate_qr_code(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
                if operator == "irancell":
                    delete_file_from_github(f"test/file/irancell/{number}.txt") 
                elif operator == "mci":
                    delete_file_from_github(f"test/file/mci/{number}.txt") 
                break
            elif choice == '2':
                clear_screen()
                                # سوال از کاربر برای تایید تمدید
                confirm = input("Aya az Tandid Motmaen Hastid ??  (y/n): ")
                if confirm.lower() != "y":
                    # در صورت عدم تایید، برنامه مجددا شروع می‌شود
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                
                clear_screen()
                # استفاده از JalaliDate برای محاسبه تاریخ انقضا
                
                while True:
                    try:
                        months = int(input("Chand Mah Tamdid Shavad ?? (1 Ta 6) "))
                        if 1 <= months <= 6:
                            months_mapping = {
                                1: 1,
                                2: 1.9,
                                3: 2.7,
                                4: 3.5,
                                5: 4.4,
                                6: 5.3,
                            }
                            months = months_mapping[months]
                            
                            break
                        else:
                            print("Lotfan Bein In Adad Bashad  !! (1 ta 6)")
                    except ValueError:
                        print("Na Motabar")

                days_to_add = months * 30

                today = JalaliDate.today()
                new_expire_date = today + datetime.timedelta(days=days_to_add)
                users_data[number]["expire_date"] = new_expire_date
                save_users_data()
                clear_screen()
                pyperclip.copy(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
                print("Link Dar Hafeze Zakhire Shod !!!")
                my_long_running_task()
                generate_qr_code(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
                if operator == "irancell":
                    delete_file_from_github(f"test/file/irancell/{number}.txt") 
                elif operator == "mci":
                    delete_file_from_github(f"test/file/mci/{number}.txt") 
                
                print("Tamdid Shod  !!!")
                if operator == "irancell":
                    add_to_number_in_github_file_prise(f"test/program/fee.txt", Mablagh * 90 )
                if operator == "mci":
                    add_to_number_in_github_file_prise(f"test/program/fee.txt", Mablagh * 100 )  # 123 به عدد موجود در فایل اضافه می‌شود

                time.sleep(1)
                break
            else:
                clear_screen()
                print("\nErorr Dar Entekhab  !!!!\n\n")
                time.sleep(3)
    else:
        create_user_file(operator, number)  # ساخت فایل برای کاربر allnet با شناسه 1234567890
        while True:
            try:
                
                num_users = int(input("Chand Karbar ?? (1 ta 5) "))
                if 1 <= num_users <= 5:
                    # تبدیل ورودی کاربر به تعداد کاربران واقعی
                    num_users_mapping = {
                        1: {'cost':1},
                        2: {'cost':1.8},
                        3: {'cost':2.6},
                        4: {'cost':3.4},
                        5: {'cost':4.2}
                    }
                    selected_num_users = num_users_mapping[num_users]['cost']
                    break
                else:
                    print("Entakhab bine (1 ta 5)")
            except ValueError:
                print("Eror Dar Entekhab !!")       
        clear_screen()
        # سوال از کاربر برای تعداد ماه‌های تمدید
        while True:
            try:
                months = int(input("Chand Mah Etebar Dashte Bashad ??  (1 ta 6) "))
                if 1 <= months <= 6:
                    months_mapping = {
                        1: {'cost':1},
                        2: {'cost':1.9},
                        3: {'cost':2.7},
                        4: {'cost':3.5},
                        5: {'cost':4.4},
                        6: {'cost':5.3},
                    }
                    selected_month_cost = months_mapping[months]['cost']
                    break
                else:
                    print("Entekhab Bine (1 ta 6)")
            except ValueError:
                print("ورودی نامعتبر. لطفاً یک عدد وارد کنید.")
        # استفاده از JalaliDate برای محاسبه تاریخ انقضا
        days_to_add = selected_month_cost * 30

        today = JalaliDate.today()
        expire_date = today + datetime.timedelta(days=days_to_add)
        operator_users = [user_info for user_info in users_data.values() if user_info["operator"] == operator]

        #محاسبه هزینه فیلتر شکن

        Mablagh = months_mapping[months]['cost'] * num_users_mapping[num_users]['cost']
        while True:
            name = input("Name User ?? ")
            if name not in [user_info["name"] for user_info in operator_users]:
                break
            print("\n\nIn Name Vojod Darad")
            print("Entekhabi Digar ??\n\n\n ")

        shomare = ""
        while True:
            clear_screen()
            shomare = input("number?\n   09")

            # بررسی اینکه آیا ورودی فقط شامل اعداد است یا خیر
            if shomare.isdigit() and len(shomare) == 9:
                break  # خروج از حلقه اگر ورودی معتبر بود
            else:
                print("Eror Dar Vorodi !")

                # --- اضافه شدن کد کپی فایل از گیت‌هاب ---


            
            
        







        users_data[number] = {
            "operator": operator,
            "expire_date": expire_date,
            "name": name,
            "shomare": f"09{shomare}"
        }
        save_users_data()

        print("\n            Darhale Sakhte User")
        print()
        my_long_running_task()
        clear_screen()
        pyperclip.copy(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
        print("Link Dar Hafeze Zakhire Shod !!!")
        my_long_running_task()

        generate_qr_code(f"https://github.com/Amirchelios/scaling-potato/raw/main/test/file/{operator}/{number}.txt")
        clear_screen()
        if operator == "irancell":
            delete_file_from_github(f"test/file/irancell/{number}.txt") 
        elif operator == "mci":
            delete_file_from_github(f"test/file/mci/{number}.txt") 
        print("ANTY COPY LINK !!!")
        print()
        my_long_running_task()
        print()
        clear_screen()
        print()
        print("Darhale Zakhire Sazi Etelaat !!!")
        print()
        my_long_running_task()
        if operator == "irancell":
            add_to_number_in_github_file_prise("test/program/fee.txt", Mablagh * 90 )
        if operator == "mci":
            add_to_number_in_github_file_prise("test/program/fee.txt", Mablagh * 100 )  # 123 به عدد موجود در فایل اضافه می‌شود













def check_internet_connection():
    """
    اتصال به اینترنت را بررسی می‌کند.
    """
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

# --- حلقه اصلی برنامه ---

# بررسی اتصال به اینترنت در شروع برنامه
if not check_internet_connection():
    print("Internet Erorr !!!")
    input("Baraye Khoroj (Enter) ...")
    sys.exit(1)

load_users_data()  # بارگیری اطلاعات کاربران در شروع برنامه


def calculate_total_t():
    """
    تعداد کاربران allnet.txt و hamrah.txt را می‌خواند و 
    به ازای هر کاربر allnet 80T و هر کاربر hamrah 100T محاسبه می‌کند.
    
    Returns:
        tuple: یک تاپل شامل (تعداد کاربران allnet، تعداد کاربران همراه اول، مجموع T)
    """
    load_users_data()  # مطمئن شوید که اطلاعات کاربران بارگیری شده است

    allnet_users = len([user for user in users_data.values() if user["operator"] == "irancell"])
    hamrah_users = len([user for user in users_data.values() if user["operator"] == "mci"])

    total_t = (allnet_users * 80) + (hamrah_users * 100)

    return allnet_users, hamrah_users, total_t

while True:
    while True:
        allnet_count, hamrah_count, total_t_value = calculate_total_t()
        loading_screen()
        clear_screen()
        print("═" * 50)
        print("║" + " " * 48 + "║")
        print("                    ║ HI VPN ║")
        print("║" + " " * 48 + "║")
        print("═" * 50)
        print("\nHI MOHSEN\n")
        print("ACTIVE USER:\n")
        print(len(users_data))
        print()
        print("All Net USER:", allnet_count)
        print("Hamrah User:", hamrah_count)
        #print("مجموع T:", total_t_value)
        print()

        choice = input("Operator ?\n\n1. All Net\n2. Hamrah Avval\n3. Exit\n")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= 3:
                if choice == 3:
                    sys.exit(0)
                else:
                    clear_screen()
                    print()
                    print()
                    if choice == 1:
                        print("Online User : ", len([user for user in users_data.values() if user["operator"] == "irancell"]))
                    if choice == 2:
                        print("Online User : ", len([user for user in users_data.values() if user["operator"] == "mci"]))
                    print()
                    print()
                    while True:
                        clear_screen()
                        print()
                        print()
                        if choice == 1:
                            print("Online User : ", len([user for user in users_data.values() if user["operator"] == "irancell"]))
                        if choice == 2:
                            print("Online User : ", len([user for user in users_data.values() if user["operator"] == "mci"]))
                        print()
                        print()
                        number = input(" Shenase User ?")

                        # بررسی اینکه آیا ورودی فقط شامل اعداد است یا خیر
                        if number.isdigit():
                            break  # خروج از حلقه اگر ورودی معتبر بود
                        else:
                            print("Erorr !!")

                    operator = "irancell" if choice == 1 else "mci"
                    search_and_update(number, operator)
                    #  حذف break برای جلوگیری از ریست شدن
            else:
                print("Yek Gozine Motabar Vared Konid !?\n")
        else:
            print("Yek Add Vared Konid !?\n")

        print("Bazgasht Be menu ??\n: ")
        print("Enter = Bazgasht , Space = Exit")
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                if char == b'\r':  # Enter key
                    break  # شکستن حلقه داخلی و بازگشت به ابتدای حلقه بیرونی
                elif char == b' ':  # Space key
                    sys.exit(0)  # خروج از کل برنامه
