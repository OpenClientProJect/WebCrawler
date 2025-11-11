import os.path
import time
import asyncio
import aiohttp
import requests
import os
import sys
import json
import subprocess
import threading
from tkinter import messagebox
from tkinter.ttk import Progressbar
import tkinter as tk

from layout import main
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": "https://www.instagram.com/",
# }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
def download_file_with_progress(ftp, remote_path, local_path, progress_var, progress_label):
    try:
        directory = '/'.join(remote_path.split('/')[:-1])
        ftp.cwd(directory)
        filename = remote_path.split('/')[-1]
        files = ftp.nlst()  # 使用nlst来获取目录列表
        if filename not in files:
            print(f"文件 {filename} 不存在。")
            return
        file_size = ftp.size(filename)
        bytes_downloaded = 0
        with open(local_path, 'wb') as file:
            def callback(data):
                nonlocal bytes_downloaded
                file.write(data)
                bytes_downloaded += len(data)
                progress_var.set(int((bytes_downloaded / file_size) * 100))
                progress_label.config(text=f"下載進度: {bytes_downloaded}/{file_size} ({bytes_downloaded / file_size * 100:.2f}%)")
                root.update()  # 更新GUI
            ftp.retrbinary(f'RETR {filename}', callback, blocksize=8192)
        print(f"文件 {filename} 下载成功。")
        create_shutdown_and_extract_script(local_path)
    except Exception as e:
        print(f"下载文件时发生错误： {e}")

def create_shutdown_and_extract_script(zip_file_path):
    script_content = (
        f'@echo off\n'
        f'echo 关闭当前程序...\n'
        f'taskkill /F /IM FBreptilever.exe\n'  # 确保进程名称正确
        f':CHECK\n'
        f'tasklist | findstr /I /C:"FBreptilever.exe" >nul\n'
        f'if %errorlevel%==0 (\n'
        f'    timeout /T 1 /NOBREAK >nul\n'
        f'    goto CHECK\n'
        f')\n'
        f'echo 删除旧程序...\n'
        f'del "%~dp0FBreptilever.exe"\n'  # 使用 %~dp0 获取批处理文件所在目录
        f'echo 解压新程序...\n'
        f'powershell -Command "Expand-Archive -Path \'%~dp0{zip_file_path}\' -DestinationPath \'%~dp0\' -Force"\n'
        f'echo 启动新程序...\n'
        f'start \"\" \"%~dp0FBreptilever.exe\"\n'  # 使用绝对路径启动
        f'echo 删除压缩包...\n'
        f'del \"%~dp0{zip_file_path}\"\n'
        f'echo 删除更新脚本...\n'
        f'del \"%~f0\"\n'  # 删除自身
    )
    with open('update.bat', 'w', encoding='utf-8') as bat_file:
        bat_file.write(script_content)

def get_real_path():
    """
    获取应用程序的真实路径。
    """
    if getattr(sys, 'frozen', False):  # 判断是否为打包后的exe文件
        application_path = os.path.dirname(sys.executable)  # 打包后的exe路径
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))  # 脚本路径
    return application_path

def get_absolute_path(relative_path):
    """
    将相对路径转换为基于应用程序安装目录的绝对路径。
    """
    application_path = get_real_path()
    return os.path.join(application_path, relative_path)

def create_registry_file():
    """
    创建注册表文件并导入注册表。
    """
    # 使用绝对路径生成注册表文件
    regeditfile = get_absolute_path('regeditfile.reg')
    sstap_path = get_absolute_path("FBreptilever.exe")
    sstap_path_registry = sstap_path.replace("\\", "\\\\")

    script_content = (
        'Windows Registry Editor Version 5.00\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol]\n'
        '@="URL:myAppProtocol Protocol"\n'
        '"URL Protocol"=""\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\DefaultIcon]\n'
        f'@="{sstap_path_registry},1"\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell]\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell\\open]\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell\\open\\command]\n'
        f'@="\\"{sstap_path_registry}\\" \\"%1\\""\n'
    )

    if not os.path.exists(regeditfile):
        try:
            with open(regeditfile, 'w', encoding='utf-8') as reg_file:
                reg_file.write(script_content)
            print("注册表文件创建完成，正在导入注册表...")

            # 等待片刻以确保文件已完全写入磁盘
            time.sleep(2)

            if os.path.exists(regeditfile):
                os.system(f'regedit /s "{regeditfile}"')  # 使用 'reg import' 而不是 'regedit /s'
                print("注册表导入完成。")
            else:
                print("注册表文件未找到，无法导入。")
        except PermissionError:
            print("权限不足，无法创建或修改注册表文件。请以管理员身份运行程序。")
        except Exception as e:
            print(f"发生了一个错误: {e}")

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

def install_new_version_thread(version, remote_version):
    def install():
        global root
        root = tk.Tk()
        root.withdraw()
        answer = messagebox.askyesno("新版本可用",
                                     f"檢測到新版本：\n当前版本：{version}\n最新版本：{remote_version}\n是否立即下載最新版本？")
        if answer:
            progress_var = tk.IntVar()
            progress_var.set(0)
            progress_label = tk.Label(root, text="下載進度: 0/0 (0.00%)")
            progress_label.pack(pady=5)
            root.deiconify()
            root.title("下載更新")
            center_window(root, 300, 100)
            root.resizable(0, 0)
            progress_bar = Progressbar(root, variable=progress_var, maximum=100, length=250)
            progress_bar.pack(pady=15)
            def start_download():
                url = f"http://ver.kydb.vip/UpData/FBfans/FBreptilever.zip?x={int(time.time())}"
                local_path = 'FBreptilever.zip'
                download_file_with_progress_http(url, local_path, progress_var, progress_label)
                messagebox.showinfo("更新完成", "下載完成。等待重新啟動。")
                subprocess.run("update.bat", creationflags=subprocess.CREATE_NO_WINDOW,cwd=os.path.dirname(sys.executable))
            threading.Thread(target=start_download).start()
            root.mainloop()
        else:
            print("用户选择不安装。")

    thread = threading.Thread(target=install)
    thread.start()

def download_file_with_progress_http(url, local_path, progress_var, progress_label):
    try:
        response = requests.get(url,headers=headers, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = 0
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bytes_downloaded += len(chunk)
                progress_var.set(int((bytes_downloaded / total_size) * 100))
                progress_label.config(text=f"下載進度: {bytes_downloaded}/{total_size} ({bytes_downloaded / total_size * 100:.2f}%)")
                root.update()  # 更新GUI
        print(f"文件 {local_path} 下载成功。")
        create_shutdown_and_extract_script(local_path)
    except Exception as e:
        print(f"下载文件时发生错误： {e}")


async def check_version():
    # config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    # if os.path.exists(config_path):
    #     with open(config_path, 'r', encoding='utf-8') as f:
    #         conig = json.load(f)
    #         version = conig['version']
    #         print("当前版本：", version)
    #         remote_version_url = 'http://ver.ry188.vip/API/getver.aspx?N=FBreptile'
    version = '1.0.0.7'
    remote_version_url = 'http://ver.ry188.vip/API/getver.aspx?N=FBreptile'
    async with aiohttp.ClientSession() as session:
        async with session.get(remote_version_url, headers=headers) as response:
            remote_version = (await response.text()).strip()
            return version, remote_version


def version_ver():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    version, remote_version = loop.run_until_complete(check_version())
    print(version, remote_version)

    if remote_version > version:
        install_new_version_thread(version, remote_version)
    else:
        # 使用授权验证来启动主程序
        from authorization import verify_and_run
        verify_and_run(version, 1)
if __name__ == "__main__":
    application_path = get_real_path()
    os.chdir(application_path)
    print(f"当前工作目录已设置为: {application_path}")
    create_registry_file()#寫入註冊表
    version_ver()#檢測程序版本
