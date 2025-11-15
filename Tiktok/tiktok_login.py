import asyncio
import json
import os
import platform
import random
import shutil
import time
import winreg
from typing import Optional

from playwright.async_api import async_playwright


class LoginWebCrawler:
    def __init__(self,cookies):
        self.cookies = cookies
        self.browser = None
        self.playwright = None
        self.browser_path = self.get_chrome_path()  # 同步调用

    def get_chrome_path(self) -> Optional[str]:
        """同步方法获取Chrome路径"""
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
            except Exception:
                pass  # 注册表查找失败，继续检查默认路径

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
            chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or "/usr/bin/google-chrome"
            return chrome_path if os.path.exists(chrome_path) else None

        else:
            return None

    async def perform_browser_login(self):
        """使用浏览器执行登录"""
        try:
            self.playwright = await async_playwright().start()

            # 浏览器启动参数
            launch_options = {
                "headless": False,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                    "--no-first-run",
                    "--no-default-browser-check",
                ]
            }

            # 如果找到Chrome路径，使用系统Chrome，否则使用Playwright自带的Chromium
            if self.browser_path:
                launch_options["executable_path"] = self.browser_path
                print(f"使用系统Chrome: {self.browser_path}")
            else:
                print("使用Playwright Chromium")

            self.browser = await self.playwright.chromium.launch(**launch_options)

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/131.0.0.0"
            ]

            page = await self.browser.new_page(user_agent=random.choice(user_agents))
            print("正在打开TikTok登录页面...")
            await page.goto(url="https://www.tiktok.com/login", wait_until='domcontentloaded')

            print("请在浏览器中完成登录...")
            print("登录成功后程序会自动继续...")

            # 等待登录成功 - 监控URL变化或特定元素出现
            try:
                # 方法1: 等待URL变化（登录后通常会跳转）
                await page.wait_for_url("https://www.tiktok.com/foryou**", timeout=120000)  # 5分钟超时

            except Exception:
                # 方法2: 如果URL没变化，等待用户手动完成
                print("正在等待手动登录完成...")
                return False

            # 获取cookies
            self.cookies = await page.context.cookies()

            # 保存cookies
            with open("tiktok.json", "w", encoding='utf-8') as f:
                json.dump(self.cookies, f, indent=4, ensure_ascii=False)

            print('登录成功，cookies已保存到 tiktok.json')
            return True
        except Exception as e:
            print(f"浏览器登录过程中发生错误: {str(e)}")
            raise Exception(f"登录失败: {str(e)}")
        finally:
            # 确保资源被清理
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def check_cookies_valid(self):
        """检查TikTok cookies是否有效"""
        try:
            if not self.cookies:
                return False

            # 检查关键的TikTok登录cookies
            sessionid = next((c for c in self.cookies if c["name"] == "sessionid"), None)
            sid_tt = next((c for c in self.cookies if c["name"] == "sid_tt"), None)
            uid_tt = next((c for c in self.cookies if c["name"] == "uid_tt"), None)

            current_time = time.time()

            # 检查cookies是否存在且未过期
            # sessionid 是主要的会话cookie
            # sid_tt 和 uid_tt 是重要的用户标识cookie
            has_valid_session = bool(sessionid)
            has_valid_user_ids = bool(sid_tt and uid_tt)

            # 检查过期时间（有些cookies的expires可能是-1，表示会话cookie）
            def is_cookie_valid(cookie):
                if not cookie:
                    return False
                expires = cookie.get("expires", -1)
                return expires == -1 or expires > current_time

            session_valid = is_cookie_valid(sessionid)
            sid_tt_valid = is_cookie_valid(sid_tt)
            uid_tt_valid = is_cookie_valid(uid_tt)

            # 如果存在有效的sessionid和用户标识cookies，则认为登录有效
            return (has_valid_session and has_valid_user_ids and
                    session_valid and sid_tt_valid and uid_tt_valid)

        except Exception as e:
            print(f"检查cookies有效性时出错: {e}")
            return False

    async def main(self):
        try:
            await self.perform_browser_login()
        except Exception as e:
            print(f"程序执行失败: {e}")
        finally:
            await self.cleanup()
