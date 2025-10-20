import asyncio
import random
import time
import json
import base64
import platform
import os
import winreg  # 仅适用于Windows
import shutil  # 适用于Linux和macOS
import sys
import re
import aiohttp
import requests
from urllib.parse import urlparse, parse_qs
from PyQt5.QtWidgets import QApplication
from FB_loginwin import win_main
from playwright.async_api import async_playwright
from FB_status import StatusWindow
class Crawler:
    def __init__(self, cookies,params):
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 25
        self.is_logged_in = False
        self.browser_path = get_chrome_path()
        self.IsKeys = params.get('search_content')  # 从参数获取搜索关键词
        self.search_results = []  # 存储搜索结果
        self.params = params  # 保存参数
        self.ui_update_lock = asyncio.Lock()  # 添加UI更新锁
        self.status_window = None  # 状态窗口引用
    async def safe_update_status(self, text):
        """安全的异步状态更新"""
        async with self.ui_update_lock:
            if self.status_window:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(
                    lambda: self.status_window.update_signal.emit(text)
                )
            await asyncio.sleep(0.01)  # 添加微小延迟

    async def robust_update_status(self, text, max_retries=3):
        """带重试机制的状态更新"""
        for attempt in range(max_retries):
            try:
                await self.safe_update_status(text)
                return True
            except Exception as e:
                print(f"状态更新失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                await asyncio.sleep(0.5 * (attempt + 1))
        return False
    async def cleanup(self):
        """清理浏览器资源"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
        except Exception as e:
            print(f"清理资源时出错: {str(e)}")
    async def start(self):
        playwright = None
        try:
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
            # 根据action参数执行不同的操作
            action = self.params.get('action', 'search')
            if action == 'search':
                await self.key_groups()
            elif action == 'confirm':
                app = QApplication.instance()
                if not app:
                    app = QApplication(sys.argv)

                # 创建状态窗口并保存引用
                self.status_window = StatusWindow()
                self.status_window.show()

                # 确保窗口显示
                QApplication.processEvents()
                await asyncio.sleep(0.5)  # 给窗口显示一点时间
                await self.csgetusers()
            print("任务完成")
        except Exception as e:
            print(f"任务执行出错: {str(e)}")
            raise
        finally:
            # 确保清理资源
            if self.browser:
                await self.browser.close()
            if playwright:
                await playwright.stop()

    async def start_confirm_action(self, params):
        """执行确认操作"""
        self.params = params
        await self.csgetusers()
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
            await page.goto(url="https://www.facebook.com/login", wait_until='load',timeout=50000)

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

    async def key_groups(self):
        """关键字搜索群组并返回地址列表 - 优化版"""
        print("關鍵字社團地址")
        key = self.IsKeys.split('#')

        # 处理所有关键字
        for key_index in range(len(key)):
            current_keyword = key[key_index]
            print(f"處理關鍵字 {key_index + 1}/{len(key)}: {current_keyword}")

            # 导航到搜索页面
            await self.page.goto(
                url="https://www.facebook.com/search/groups?q=" + current_keyword + "&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D",
                wait_until='load',
                timeout=50000
            )

            # 等待页面加载
            title = await self.page.title()
            if "Facebook" in title:
                await asyncio.sleep(3)
            else:
                print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                await asyncio.sleep(10)

            post = int(self.params.get('search_count')) # 设置要获取的帖子数量
            current_groups_postlist = []
            max_scroll_attempts = 10
            scroll_attempts = 0
            previous_count = 0

            try:
                # 批量处理方式：滚动并收集所有可见的群组链接
                while len(current_groups_postlist) < post and scroll_attempts < max_scroll_attempts:
                    # 获取当前页面所有群组链接
                    group_elements = await self.page.query_selector_all(
                        '//div[@aria-label="搜尋結果" or @aria-label="搜索结果"]//div[@role="feed"]//a[contains(@href, "/groups/")]'
                    )

                    current_count = len(group_elements)
                    print(f"当前找到 {current_count} 个群组链接")

                    # 批量处理所有找到的链接
                    for element in group_elements[len(current_groups_postlist):]:  # 只处理新找到的链接
                        try:
                            post_url_before = await element.get_attribute('href')

                            if post_url_before and len(current_groups_postlist) < post:
                                # 提取群组ID并构建成员页面URL
                                group_id = self.extract_group_id(post_url_before)
                                if group_id:
                                    members_url = f"https://www.facebook.com/groups/{group_id}/members"
                                    if members_url not in current_groups_postlist:
                                        current_groups_postlist.append(members_url)
                                        print(f"找到群组 {len(current_groups_postlist)}: {members_url}")

                                        # 如果已经达到目标数量，跳出循环
                                        if len(current_groups_postlist) >= post:
                                            break
                        except Exception as e:
                            print(f"处理群组链接时出错: {str(e)}")
                            continue

                    # 检查是否达到目标数量
                    if len(current_groups_postlist) >= post:
                        break

                    # 检查是否有新内容加载
                    if current_count == previous_count:
                        scroll_attempts += 1
                        print(f"没有新内容加载，尝试次数: {scroll_attempts}/{max_scroll_attempts}")
                    else:
                        scroll_attempts = 0

                    previous_count = current_count

                    # 滚动加载更多内容
                    if len(current_groups_postlist) < post:
                        await self.page.evaluate("""
                            window.scrollTo({
                                top: document.body.scrollHeight,
                                behavior: 'smooth'
                            });
                        """)
                        await asyncio.sleep(2)  # 等待新内容加载

            except Exception as e:
                print(f"搜索过程中出错: {str(e)}")

            # 将当前关键字的搜索结果添加到总结果中
            self.search_results.extend(current_groups_postlist)
            print(f"关键字 '{current_keyword}' 完成，找到 {len(current_groups_postlist)} 个群组")

        print(f"搜索完成，共找到 {len(self.search_results)} 个地址")
        return self.search_results

    def extract_group_id(self, url):
        """从Facebook群组URL中提取群组ID"""
        try:
            # 移除查询参数
            clean_url = url.split('?')[0]

            # 匹配多种可能的群组URL格式
            patterns = [
                r'https?://(?:www\.)?facebook\.com/groups/([^/?]+)/?',
                r'/groups/([^/?]+)/?',
            ]

            for pattern in patterns:
                match = re.search(pattern, clean_url)
                if match:
                    return match.group(1)

            return None
        except Exception as e:
            print(f"提取群组ID时出错: {str(e)}")
            return None

    async def csgetusers(self):
        """爬取用户信息"""
        addresses = self.params.get('addresses', [])
        if not addresses:
            print("没有提供地址列表")
            return

        # 使用第一个地址进行爬取
        if addresses and addresses[0].strip():
            url = addresses[0].strip()
            print(f"开始爬取用户信息，地址: {url}")
            await self.robust_update_status(f"社團地址:{url}")
            await self.page.goto(url=url, wait_until='load')
            await asyncio.sleep(5)
            await self.robust_update_status("开始爬取用户信息...")
            # 滚动加载更多用户
            previous_count = 0
            current_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 10
            users = []
            seen_user_ids = set()  # 用于跟踪已处理的用户ID
            user_counter = 0  # 新增：独立计数器

            while scroll_attempts < max_scroll_attempts:
                # 滚动到底部
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)

                # 获取当前用户数量
                user_links = await self.page.query_selector_all(
                    '//div[@role="list"]//a[@role="link" and @tabindex="-1" and contains(@href, "/user/") or @role="link" and @tabindex="-1" and contains(@href, "facebook.com/")]')
                current_count = len(user_links)
                print(f"滚动后用户数量: {current_count}")

                for i, link in enumerate(user_links):
                    try:
                        href = await link.get_attribute('href')
                        text = await link.get_attribute('aria-label')

                        if not href or not text or not text.strip():
                            continue

                        user_id = await self.extract_facebook_identifier(href)

                        # 检查用户ID是否已存在
                        if user_id and user_id not in seen_user_ids:
                            seen_user_ids.add(user_id)  # 添加到已见集合
                            user_counter += 1  # 只有在添加新用户时才增加计数器
                            users.append({
                                'index': user_counter,  # 使用独立计数器
                                'name': text.strip(),
                                'user_id': user_id
                            })
                            print(f"{user_counter}：{user_id} {text.strip()}")
                            await self.robust_update_status(f"{user_counter}：{user_id} {text.strip()}")

                            # 检查是否达到目标数量
                            if user_counter >= int(self.params.get('crawl_count')):
                                print(f"达到目标数量 {user_counter}，停止爬取")
                                break

                    except Exception as e:
                        print(f"提取用户信息时出错: {str(e)}")
                        continue

                # 如果已达到目标数量，跳出外层循环
                if user_counter >= int(self.params.get('crawl_count')):
                    break

                if current_count == previous_count:
                    scroll_attempts += 1
                    print(f"用户数量未增加，尝试次数: {scroll_attempts}/{max_scroll_attempts}")
                else:
                    scroll_attempts = 0

                previous_count = current_count

                if scroll_attempts >= 3:  # 连续3次没有新用户就停止
                    print("已加载所有用户")
                    break

            print(f"爬取完成，共获取 {user_counter} 个用户信息")
            return users
        else:
            print("地址为空，无法爬取")
    async def extract_facebook_identifier(self,url):
        # 处理相对路径
        if url.startswith('/'):
            user_match = re.search(r'/user/(\d+)', url)
            if user_match:
                return user_match.group(1)
            return None

        # 解析完整URL
        parsed = urlparse(url)

        # 处理profile.php情况
        if parsed.path == '/profile.php':
            query_params = parse_qs(parsed.query)
            if 'id' in query_params:
                return query_params['id'][0]

        # 处理用户名情况
        if parsed.netloc == 'www.facebook.com':
            path_parts = parsed.path.strip('/').split('/')
            if path_parts and path_parts[0] != 'profile.php':
                return path_parts[0]

        return None

    async def home_post(self):
        await self.page.goto(url="https://www.facebook.com/", wait_until='load')
        await asyncio.sleep(10)
        try:
            Option_selector = '//div[@data-visualcompletion="ignore-dynamic"]//div[@role="button" and contains(@aria-label, "選項")]'
            Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
            if Option_but:
                await Option_but.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await Option_but.click()
                await asyncio.sleep(random.uniform(5, 8))
                # 彈出來電音效
                disabled_selector = '//div[@aria-label="聊天室設定"]//div[@aria-checked="true" and contains(@aria-label, "來電音效")]'
                disabled_but = await self.page.wait_for_selector(disabled_selector, timeout=10000)
                if disabled_but:
                    await disabled_but.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await disabled_but.click()
                    await asyncio.sleep(random.uniform(3, 6))
                    input_selector = '//div[@role="dialog"]//div[@role="list"]/div[3]'
                    disabled_but = await self.page.wait_for_selector(input_selector, timeout=10000)
                    if disabled_but:
                        await disabled_but.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await disabled_but.click()
                        await asyncio.sleep(random.uniform(3, 5))
                        disabled_selector = '//div[@role="dialog"]//div[@role="button" and contains(@aria-label, "停用")]'
                        disabled_but = await self.page.wait_for_selector(disabled_selector, timeout=10000)
                        if disabled_but:
                            await disabled_but.scroll_into_view_if_needed()
                            await asyncio.sleep(1)
                            await disabled_but.click()
                            await asyncio.sleep(random.uniform(4, 6))
                            #找到再次点击才能激活下面查找
                            await Option_but.scroll_into_view_if_needed()
                            await asyncio.sleep(1)
                            await Option_but.click()
                            await asyncio.sleep(random.uniform(5, 8))
        except Exception as e:
            print(f"没有找到來電音效: {str(e)}")
        try:
                    # 彈出新訊息关闭
                    disabled_selector = '//div[@aria-label="聊天室設定"]//div[@aria-checked="true" and contains(@aria-label, "彈出新訊息")]'
                    disabled_but = await self.page.wait_for_selector(disabled_selector, timeout=10000)
                    if disabled_but:
                        await disabled_but.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await disabled_but.click()
                        await asyncio.sleep(random.uniform(3, 6))
                    await Option_but.click()
        except Exception as e:
            print(f"没有找到新訊息关闭: {str(e)}")

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