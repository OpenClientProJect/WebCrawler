import asyncio
import random
import time
import json
import base64
import platform
import os
import winreg  # 仅适用于Windows
import shutil  # 适用于Linux和macOS

import aiohttp
import requests
from PyQt5.QtWidgets import QApplication
from FB_loginwin import win_main
from playwright.async_api import async_playwright

class Crawler:
    def __init__(self, cookies,data,content1):
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 25
        self.is_logged_in = False
        self.browser_path = get_chrome_path()
        # """全局设定"""

        self.status_window = None  # 状态窗口引用

    def update_status(self, text):
        """更新状态窗口"""
        if self.status_window:
            # 确保在主线程更新UI
            self.status_window.update_signal.emit(text)
            # 立即处理事件队列
            QApplication.processEvents()

    async def start(self):
        playwright = await async_playwright().start()
        # 增强浏览器配置
        browser_args = [
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-component-extensions-with-background-pages',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-back-forward-cache',
            '--disable-site-isolation-trials'
        ]
        self.browser = await playwright.chromium.launch(headless=False,args=browser_args, executable_path=self.browser_path)
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        await context.add_init_script("""
               Object.defineProperty(navigator, 'webdriver', {
                   get: () => undefined,
               });
               window.chrome = {
                   runtime: {},
               };
           """)
        if self.cookies:
            await context.add_cookies(self.cookies)

        self.page = await context.new_page()
        # await self.home_post() # FB首页留言
        print("任务完成")


    async def check_cookies_valid(self):
        """检查cookies是否有效"""
        try:
            c_user = next((c for c in self.cookies if c["name"] == "c_user"), None)
            xs = next((c for c in self.cookies if c["name"] == "xs"), None)
            current_time = time.time()
            return c_user and xs and xs["expires"] > current_time
        except:
            return False

    async def login_with_gui(self):
        """通过GUI获取凭证并登录"""
        try:
            credentials = win_main()
            if not credentials:
                raise Exception("用户取消登录")

            self.username = credentials["username"]
            self.password = credentials["password"]
            await self.perform_browser_login()
        except Exception as e:
            print(f"GUI登录失败: {str(e)}")
            self.is_logged_in = False

    async def perform_browser_login(self):
        """使用浏览器执行登录"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False,
                executable_path=self.browser_path
            )
            page = await self.browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            await page.goto(url="https://www.facebook.com/login", wait_until='load')

            await asyncio.sleep(random.uniform(1.5, 3.5))

            # 模拟人类输入速度
            await page.locator("//input[@id='email']").first.fill(self.username)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.locator("//input[@id='pass']").fill(self.password)
            await asyncio.sleep(random.uniform(0.8, 1.5))

            # 点击登录
            await page.click("//button[@id='loginbutton']")

            # 检查登录是否成功
            try:
                await page.wait_for_url("https://www.facebook.com/?lsrc=lb", timeout=120000)
                title = await page.title()
                if "Facebook" in title:
                    await asyncio.sleep(3)
                    self.is_logged_in = True
                else:
                    print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                    await asyncio.sleep(10)  # 等待10秒
                await self.class_fb_set()
            except Exception as e:
                current_url = await page.evaluate("() => window.location.href")
                if "login" in current_url or "authentication" in current_url or "checkpoint" in current_url:
                    print(f"登录失败，当前URL: {current_url}")
                    self.is_logged_in = False
                    await self.browser.close()
                    raise Exception("登录失败，请检查用户名和密码")

            # 登录成功处理
            self.cookies = await page.context.cookies()
            with open("FB.json", "w") as f:
                json.dump(self.cookies, f, indent=4)

            print('登录成功')
            self.is_logged_in = True
            await self.browser.close()
        except Exception as e:
            print(f"浏览器登录过程中发生错误: {str(e)}")
            self.is_logged_in = False
            if self.browser:
                await self.browser.close()
            raise Exception(f"登录失败: {str(e)}")

    # 获取请求Auth签名
    def getBearerAuth(self):
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        sessionid = next((cookie for cookie in self.cookies if cookie['name'] == "sessionid"), None)
        auth_str = "{\"ds_user_id\":\"" + ds_user_id['value'] + "\",\"sessionid\":\"" + sessionid['value'] + "\"}"
        auth_bytes = auth_str.encode('utf-8')
        auth_str = base64.b64encode(auth_bytes)
        return "Bearer IGT:2:" + auth_str.decode('utf-8')


    async def home_post(self):
        await self.page.goto(url="https://www.facebook.com/", wait_until='load')
        await asyncio.sleep(10)

        # num_posts = 6
        # print(f"准备与 {num_posts} 个帖子互动")
        #
        # for i in range(1, num_posts + 1):
        #
        #     selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div/div/div[{i}]'
        #     element = await self.page.wait_for_selector(selector, timeout=10000)
        #     if element:
        #         await element.scroll_into_view_if_needed()
        #         print(f"第 {i} 个帖子")
        #     try:
        #         # 点赞
        #         # if await self.like_post(i):
        #         #     print(f"第 {i} 个帖子点赞成功")
        #         #
        #         # a = True
        #         # if a:
        #         #     comments = self.leavetext_messags
        #         #     if await self.comment_post(i, random.choice(comments)):
        #         #         print(f"第 {i} 个帖子留言成功")
        #
        #         await asyncio.sleep(random.uniform(5, 10))
        #
        #     except Exception as e:
        #         print(f"处理第 {i} 个帖子时出错: {str(e)}")

    async def class_fb_set(self):
        try:
            Option_selector = '//div[@data-visualcompletion="ignore-dynamic"]//div[@role="button" and contains(@aria-label, "選項")]'
            Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
            if Option_but:
                await Option_but.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await Option_but.click()
                await asyncio.sleep(random.uniform(5, 8))
                disabled_selector = '//div[@aria-label="聊天室設定"]//div[@aria-checked="true" and contains(@aria-label, "彈出新訊息")]'
                disabled_but = await self.page.wait_for_selector(disabled_selector, timeout=10000)
                if disabled_but:
                    await disabled_but.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await disabled_but.click()
                    await asyncio.sleep(random.uniform(5, 8))
                await Option_but.click()
        except Exception as e:
            print(f"没有找到: {str(e)}")
    # 添加新的辅助方法
    def minimize_browser_window(self):
        """最小化浏览器窗口（平台特定实现）"""
        try:
            system = platform.system()
            if system == "Windows":
                import win32gui, win32con
                # 获取浏览器窗口句柄
                time.sleep(1)  # 等待窗口创建
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            elif system == "Darwin":  # macOS
                import subprocess
                subprocess.run(["osascript", "-e",
                                'tell application "System Events" to set visible of process "Google Chrome" to false'])
            # Linux 系统需要额外的窗口管理器支持，这里暂不处理
        except Exception as e:
            print(f"最小化窗口失败: {e}")

    async def force_minimize_browser(self):
        """强制最小化浏览器窗口"""
        # 先尝试通过Playwright的方式
        try:
            if self.browser:
                # 获取所有页面
                pages = self.browser.contexts[0].pages if self.browser.contexts else []
                for page in pages:
                    # 尝试最小化窗口
                    await page.evaluate("""() => {
                        if (window.moveTo && window.resizeTo) {
                            window.moveTo(-2000, -2000);
                            window.resizeTo(1, 1);
                        }
                    }""")
        except:
            pass

        # 再使用平台特定的方法
        self.minimize_browser_window()

def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')

def save_progress(account, users, position):
    """保存当前处理进度到文件"""
    progress_data = {
        "users": users,
        "position": position
    }
    filename = f"{account}_progress.json"
    with open(filename, 'w') as f:
        json.dump(progress_data, f)
    print(f"保存进度到 {filename}: 位置 {position}/{len(users)}")

def clear_progress(account):
    """清除进度文件"""
    filename = f"{account}_progress.json"
    if os.path.exists(filename):
        os.remove(filename)
        print(f"已清除进度文件 {filename}")

async def GetHtmlpic(data):
    if not data["SendData"]["SendConfigs"]["SendPicList"]:
        return None

    random_test = random.randint(0, len(data["SendData"]["SendConfigs"]["SendPicList"]) - 1)
    url = data["SendData"]["SendConfigs"]["SendPicList"][random_test]

    if not os.path.exists('img'):
        os.makedirs('img')

    img_path = os.path.join('img', 'image.png')

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                with open(img_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                return os.path.abspath(img_path)

    return None

def get_chrome_path():
    system = platform.system()

    if system == "Windows":
        # 尝试通过注册表获取安装路径
        try:
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                chrome_path = os.path.join(install_path, "chrome.exe")
                if os.path.exists(chrome_path):
                    return chrome_path
        except FileNotFoundError:
            pass  # 继续检查默认路径

        # 检查常见的默认安装路径
        possible_paths = [
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    elif system == "Darwin":
        # macOS的默认安装路径
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return chrome_path if os.path.exists(chrome_path) else None

    elif system == "Linux":
        # 使用which命令查找或检查常见路径
        chrome_path = shutil.which("google-chrome") or "/usr/bin/google-chrome"
        return chrome_path if os.path.exists(chrome_path) else None

    else:
        return None