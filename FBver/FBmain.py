import asyncio
import random
import subprocess
import time
import json
import base64
import platform
import os
import uuid
import winreg  # 仅适用于Windows
import shutil  # 适用于Linux和macOS
from idlelib.rpc import response_queue
import re
import aiohttp
import requests
from PyQt5.QtWidgets import QApplication
from async_timeout import timeout

from FB_loginwin import win_main
from playwright.async_api import async_playwright

class Crawler:
    def __init__(self, cookies, data, content0, content1, task_order, rest_times):
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 25
        self.is_logged_in = False
        self.browser_path = get_chrome_path()
        # """全局配置"""
        self.customer_code = str(data["AppConfigData"]["GlobalConfig"]["DeviceNumber"])#设备编号
        int(data["AppConfigData"]["GlobalConfig"]["EveryBrowserInterval"])#每个浏览器间隔
        parse_bool(data["AppConfigData"]["GlobalConfig"]["EnableLoopPosting"])#启动循环发文
        parse_bool(data["AppConfigData"]["GlobalConfig"]["EnableLoopPush"])#启动循环推文
        parse_bool(data["AppConfigData"]["GlobalConfig"]["EnableLoopJoinGroup"])#启动循环加社团
        parse_bool(data["AppConfigData"]["GlobalConfig"]["EnableAccountDevelop"])#启动养号
        parse_bool(data["AppConfigData"]["GlobalConfig"]["EnableFanPages"])#启动粉丝专页
        parse_bool(data["AppConfigData"]["GlobalConfig"]["IsSwitchIP"])#是否換IP
        parse_bool(data["AppConfigData"]["GlobalConfig"]["Isprefix"])#是否有前缀
        # """贴文、推文"""
        int(data["AppConfigData"]["PostsConfig"]["EveryGroupInterval"])#每个社团间隔
        int(data["AppConfigData"]["PostsConfig"]["EveryIntervalHowManyGroup"])#每间隔多少条
        int(data["AppConfigData"]["PostsConfig"]["GroupRestInterval"])#社团休息间隔
        self.Count_num = int(data["AppConfigData"]["PostsConfig"]["GetPostsNumber"])#获取贴文数量
        self.Count1 = int(data["AppConfigData"]["PostsConfig"]["Count1"])#Count1
        self.Count2 = int(data["AppConfigData"]["PostsConfig"]["Count2"])#Count2
        int(data["AppConfigData"]["PostsConfig"]["EachTimeInterval"])#每条时间间隔
        int(data["AppConfigData"]["PostsConfig"]["EveryIntervalHowManyPosts"])#每间隔多少条
        int(data["AppConfigData"]["PostsConfig"]["RestTimeInterval"])#休息时间间隔
        self.Is_post_like = parse_bool(data["AppConfigData"]["PostsConfig"]["EnablePostsLike"])#启用貼文讚
        self.LikeType = int(data["AppConfigData"]["PostsConfig"]["LikeType"])#點讚
        # """加社团"""
        int(data["AppConfigData"]["JoinGroupConfig"]["EveryGroupInterval"])#每个社团间隔
        int(data["AppConfigData"]["JoinGroupConfig"]["EveryIntervalHowManyGroup"])# 每间隔多少条
        int(data["AppConfigData"]["JoinGroupConfig"]["GroupRestInterval"])#社团休息间隔
        # """养号"""
        int(data["AppConfigData"]["AccountDevelopConfig"]["EachTimeInterval"])#每条时间间隔
        int(data["AppConfigData"]["AccountDevelopConfig"]["EveryIntervalHowManyAccount"])#每间隔多少条
        int(data["AppConfigData"]["AccountDevelopConfig"]["RestTimeInterval"])#休息时间间隔
        self.ConfirmFriend = parse_bool(data["AppConfigData"]["AccountDevelopConfig"]["IsConfirmFriendInvite"])#是否确认好友邀请
        self.ConfirmFriend_num = int(data["AppConfigData"]["AccountDevelopConfig"]["ConfirmHowManyFriendInvite"])#确认多少个好友邀请
        self.is_personal = parse_bool(data["AppConfigData"]["AccountDevelopConfig"]["SendPersonalUpdates"])#发个人动态
        self.is_home_like = parse_bool(data["AppConfigData"]["AccountDevelopConfig"]["IsHomeLike"])#养号是否首页点赞
        self.home_like = int(data["AppConfigData"]["AccountDevelopConfig"]["LikeType"])#點讚
        self.addFriend = parse_bool(data["AppConfigData"]["AccountDevelopConfig"]["IsAddFriend"])#是否添加朋友
        self.addFriend_num = int(data["AppConfigData"]["AccountDevelopConfig"]["AddHowManyFriend"])#添加多少个朋友
        self.home_like_num = int(data["AppConfigData"]["AccountDevelopConfig"]["SponsorCount"])#赞助的次数
        # """粉专"""
        self.is_home_page = parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsEnableHomeLike"])#是否启用页首
        int(data["AppConfigData"]["FanPagesConfig"]["EveryFanPagesInterval"])#每个粉丝专页间隔
        int(data["AppConfigData"]["FanPagesConfig"]["EveryIntervalHowManyFanPages"])#每间隔多少条
        int(data["AppConfigData"]["FanPagesConfig"]["FanPagesRestInterval"])#粉丝专页休息间隔
        self.is_leave_page = parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsEnablePush"])#是否启用推文
        int(data["AppConfigData"]["FanPagesConfig"]["LikeType"])#點讚
        int(data["AppConfigData"]["FanPagesConfig"]["EachTimeInterval"])#每条时间间隔
        int(data["AppConfigData"]["FanPagesConfig"]["EveryIntervalHowManyFanPages2"])#每间隔多少条
        int(data["AppConfigData"]["FanPagesConfig"]["RestTimeInterval"])#休息时间间隔
        self.fans_home_like = parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsCancelHomeLike"])#取消首页点赞
        self.leave_page_like = parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsCancelPostsLike"])#取消贴文点赞

        self.status_window = None  # 状态窗口引用
        self.task_order = task_order or []
        self.executed_tasks = []  # 用于跟踪已执行的任务
        self.rest_times = rest_times or {}  # 存储休息时间配置
        self.username = content1
        self.device_number = content0  # 设备号，可以从配置中获取
        self.machine_code = self.generate_machine_code()  # 获取机器码
        self.is_phone = 0  # 是否是手机
        self.remote_id = content1  # AnyDesk ID
        self.ui_update_lock = asyncio.Lock()  # 添加UI更新锁
        self.completion_times = {}  # 新增：存储其他任务的完成时间配置

        # 如果传递了completion_times，则使用它
        if isinstance(task_order, dict) and 'completion_times' in task_order:
            self.completion_times = task_order.get('completion_times', {})
        elif rest_times and 'completion_times' in rest_times:
            self.completion_times = rest_times.get('completion_times', {})

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

    async def periodic_online_report(self):
        """定期上报在线状态"""
        while True:
            await asyncio.sleep(40)  # 每分钟上报一次
            # 不等待完成，直接创建任务
            asyncio.create_task(self.report_online_status())

    async def start(self):

        if 0 in self.task_order or 1 in self.task_order or 2 in self.task_order or 3 in self.task_order or 4 in self.task_order:
            print("存在序号需要浏览器：", self.task_order)
            await self.robust_update_status("啟動瀏覽器...")
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
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/131.0.0.0"
            ]
            context = await self.browser.new_context(
                user_agent=random.choice(user_agents)
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
        await asyncio.sleep(1)
        function_map = {
            0: self.tweet_comment,
            1: self.post_comment,
            2: self.add_join_groups,
            3: self.account_nurturing,
            4: self.fan_pages,
            5: self.sleep_time
        }
        if self.task_order:
            print(f"将按照以下顺序执行任务: {self.task_order}")
            # 按顺序执行任务
            for position, task_index in enumerate(self.task_order):
                # 更新状态窗口显示当前任务队列
                if self.status_window:
                    self.status_window.task_update_signal.emit(self.task_order, self.executed_tasks)

                task_func = function_map.get(task_index)
                if task_func:
                    try:
                        # 如果是休息任务，传递休息时间
                        if task_index == 5:  # 休息时间任务
                            rest_time = self.rest_times.get(position, 60)
                            await task_func(rest_time)
                        else:
                            # 其他任务：获取完成时间并执行带超时控制的任务
                            completion_time = self.completion_times.get(position, 1800)  # 默认30分钟
                            await self.execute_task_with_timeout(task_func, task_index, position, completion_time)

                        # 记录已执行的任务
                        task_id = f"{position}_{task_index}"
                        self.executed_tasks.append(task_id)

                        # 更新状态窗口显示已完成任务
                        if self.status_window:
                            self.status_window.task_update_signal.emit(self.task_order, self.executed_tasks)

                    except Exception as e:
                        print(f"执行任务 {task_index} 时出错: {str(e)}")
                        await self.robust_update_status(f"任务执行出错: {str(e)}")
                        continue
        # await self.tweet_comment() # """贴文、推文"""
        # await self.post_comment() # """推文"""
        # await self.add_join_groups() # """加社團"""
        # await self.account_nurturing()#養號
        # await self.fan_pages()  # 粉丝专页
        print("任务完成")
        await self.robust_update_status("全部任務完成...")

        await self.browser.close()

    async def execute_task_with_timeout(self, task_func, task_index, position, completion_time):
        """执行带超时控制的任务"""
        task_names = {
            0: "循環發文",
            1: "循環推文",
            2: "循環加社團",
            3: "養號",
            4: "粉絲專頁"
        }

        task_name = task_names.get(task_index, f"任务{task_index}")
        task_id = f"{position}_{task_index}"  # 任务唯一标识

        if completion_time == 0:
            await self.robust_update_status(f"開始執行{task_name}，無時間限制")
            # 对于无时间限制的任务，不显示倒计时
            if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
                self.status_window.update_task_countdown(task_id, -1)  # -1表示无时间限制
        else:
            await self.robust_update_status(f"開始執行{task_name}，最大執行時間: {completion_time // 60}分鐘")

        start_time = time.time()
        task_completed = False

        try:
            # 创建任务
            task = asyncio.create_task(task_func())

            if completion_time == 0:
                # 无时间限制，直接等待任务完成
                await task
                task_completed = True
                elapsed_time = time.time() - start_time
                await self.robust_update_status(f"{task_name}完成，用時: {int(elapsed_time)}秒")
            else:
                # 有时间限制，等待任务完成或超时
                # 启动倒计时更新
                if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
                    asyncio.create_task(self.update_task_countdown(task_id, completion_time, start_time))

                try:
                    await asyncio.wait_for(task, timeout=completion_time)
                    task_completed = True
                    elapsed_time = time.time() - start_time
                    remaining_time = completion_time - elapsed_time

                    if remaining_time > 0:
                        await self.robust_update_status(f"{task_name}提前完成，等待剩余时间: {int(remaining_time)}秒")
                        # 更新倒计时显示为剩余等待时间
                        if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
                            asyncio.create_task(self.update_waiting_countdown(task_id, int(remaining_time)))
                        await asyncio.sleep(remaining_time)
                    else:
                        await self.robust_update_status(f"{task_name}在指定时间内完成")

                except asyncio.TimeoutError:
                    await self.robust_update_status(f"{task_name}執行超時，強制結束並進入下一個任務")
                    # 取消任务
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

        except Exception as e:
            await self.robust_update_status(f"{task_name}執行出錯: {str(e)}")
            raise

        finally:
            # 无论任务是否完成，都标记为已完成状态
            if self.status_window:
                # 清除倒计时显示
                if hasattr(self.status_window, 'update_task_countdown'):
                    self.status_window.update_task_countdown(task_id, 0)

                # 立即更新状态为完成
                if task_id not in self.executed_tasks:
                    self.executed_tasks.append(task_id)
                self.status_window.task_update_signal.emit(self.task_order, self.executed_tasks)

    async def update_task_countdown(self, task_id, total_time, start_time):
        """更新任务执行倒计时"""
        while True:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, total_time - elapsed_time)

            if remaining_time <= 0:
                break

            # 更新状态窗口的倒计时显示
            if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
                self.status_window.update_task_countdown(task_id, int(remaining_time))

            await asyncio.sleep(1)  # 每秒更新一次

    async def update_waiting_countdown(self, task_id, wait_time):
        """更新等待倒计时"""
        remaining = wait_time
        while remaining > 0:
            # 更新状态窗口的倒计时显示
            if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
                self.status_window.update_task_countdown(task_id, remaining)

            await asyncio.sleep(1)
            remaining -= 1

        # 等待结束，清除倒计时
        if self.status_window and hasattr(self.status_window, 'update_task_countdown'):
            self.status_window.update_task_countdown(task_id, 0)

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
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/131.0.0.0"
            ]
            page = await self.browser.new_page(user_agent=random.choice(user_agents))
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
        await self.page.goto(url="https://www.facebook.com/", wait_until='load', timeout=50000)
        title = await self.page.title()
        if "Facebook" in title:
            await asyncio.sleep(3)
        else:
            print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
            await asyncio.sleep(10)  # 等待10秒
        num_posts = self.home_like_num
        like_count = 0
        seek_count = 0
        i = 1
        print(f"准备与 {num_posts} 个帖子互动")
        while True:
            try:
                selector = f'//div[contains(@class, "x1hc1fzr x1unhpq9")]/div//div[@aria-posinset={i}]'
                element = await self.page.wait_for_selector(selector, timeout=15000)
                if element:
                    await element.scroll_into_view_if_needed()
                    print(f"第 {i} 个帖子")
                    like_count,seek_count = await self.sponsor_like(selector,like_count,seek_count)
                    if like_count >= num_posts:
                        break
            except Exception as e:
                print(f"处理第 {i} 个帖子时出错: {str(e)}")
            finally:
                i += 1
            #找不到执行普通点赞
            if seek_count >= 5 :
                like_count += 1
                like_type = self.home_like
                await self.like_post(selector, like_type)
                # 提示檢測
                await self.warning_prompt()

                # 請求數據
                tweet = await self.fetch_data(
                    f"http://aj.ry188.vip/api/GetUrlList.aspx?Account={self.username}")
                response_url = tweet.split("|+|")
                comment_text = response_url[7].split("{}")

                await self.comment_post(random.choice(comment_text), selector)

                # 提示檢測
                await self.warning_prompt()

                if like_count >= num_posts:
                    break

    async def sponsor_like(self,selector,like_count,seek_count):

        try:
            sponsor_element = await self.page.wait_for_selector(selector + '//span[contains(text(), "助")]',
                                                                timeout=10000)
            if sponsor_element:
                await sponsor_element.scroll_into_view_if_needed()

                print("出現啦")
                like_count += 1
                seek_count = 0
                like_type = self.home_like
                await self.like_post(selector,like_type)
                #提示檢測
                await self.warning_prompt()

                #請求數據
                tweet = await self.fetch_data(
                    f"http://aj.ry188.vip/api/GetUrlList.aspx?Account={self.username}")
                response_url = tweet.split("|+|")
                comment_text = response_url[7].split("{}")

                await self.comment_post(random.choice(comment_text),selector)

                # 提示檢測
                await self.warning_prompt()
            await asyncio.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"這个帖子不是贊助: {str(e)}")
            seek_count += 1
        return like_count,seek_count

    async def like_post(self,like,like_type):
        """封装点赞功能"""
        await asyncio.sleep(2)
        alreadylike = '//div[@aria-label="讚" or @aria-label="赞"]'
        cancellike = '//div[contains(@aria-label, "取消") or contains(@aria-label, "移除")]'
        try:
            # selector = like.format(index)
            selector = like
            selector = selector + alreadylike
            element = await self.page.wait_for_selector(selector, timeout=10000)

            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(2)
                await element.hover()
                await asyncio.sleep(3)

                target_emotion = like_type - 1
                target_emotion_list = ["赞", "大心", "加油", "哈", "哇", "嗚", "怒"]
                emotion_selector = f'//div[@role="button" and @aria-label="{target_emotion_list[target_emotion]}"]'
                try:
                    emotion_button = await self.page.wait_for_selector(emotion_selector, timeout=5000)
                    if emotion_button:
                        await emotion_button.click()
                        print(f"点击了表情: {target_emotion_list[target_emotion]}")
                    else:
                        print("未找到表情按钮，执行默认点赞")
                        await element.click()
                except Exception as e:
                    print(f"表情点击失败: {str(e)}")
                    await element.click()
            return True
        except Exception as e:
            print(f"点赞失败: {str(e)}")
            try:
                # like = like.format(index)
                like = like
                element = await self.page.wait_for_selector(like + cancellike, timeout=10000)
                if element:
                    print("已經點過讃")
                return False
            except Exception as e:
                print(f"点赞失败找不到可點讚位置: {str(e)}")

    async def comment_post(self, comment_text, posts):
        """封装留言功能"""
        await asyncio.sleep(2)
        try:
            # 点击留言按钮
            # selector = Posts.format(index)
            selector = posts
            element = await self.page.wait_for_selector(selector, timeout=10000)
        except Exception as e:
            print(f"留言失败: {str(e)}")
            return False

        try:
            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await element.click()
                await asyncio.sleep(2)

                # 定位留言输入框
                input_selector = '//div[@role="dialog"]//div[@role="textbox" and contains(@aria-label, "留言") or @role="textbox" and contains(@aria-label, "回答")]'
                input_element = await self.page.wait_for_selector(input_selector, timeout=10000)

                if input_element:
                    await input_element.scroll_into_view_if_needed()
                    aria_label = await input_element.get_attribute('aria-label')
                    print(f"获取到的 aria-label 为: {aria_label}")

                    if "送出" in aria_label or "回答" in aria_label:
                        close_selectors = [
                            '//div[@role="dialog"]//div[@aria-label="關閉"]',  # 方式1
                            '//div[@aria-label="關閉" and @aria-hidden="false"]'  # 方式2
                        ]
                        for selector in close_selectors:
                            try:
                                close_button = await self.page.wait_for_selector(selector, timeout=3000)
                                if close_button:
                                    await close_button.scroll_into_view_if_needed()
                                    await asyncio.sleep(1)
                                    await close_button.click()
                                    print("彈窗關閉！")
                                    return True
                            except Exception as e:
                                continue  # 尝试下一种选择器
                    else:

                        # 发送文字部分
                        if comment_text:
                            await asyncio.sleep(1)
                            await input_element.click()
                            await input_element.fill(comment_text)
                            await asyncio.sleep(2)
                        await asyncio.sleep(random.randint(6, 10))

                        close_selectors = [
                            '//div[@aria-label="關閉" and @aria-hidden="false"]',  # 方式1
                            '//div[@role="dialog"]//div[@aria-label="關閉"]'  # 方式2
                        ]
                        for selector in close_selectors:
                            try:
                                close_button = await self.page.wait_for_selector(selector, timeout=3000)
                                if close_button:
                                    await close_button.scroll_into_view_if_needed()
                                    await asyncio.sleep(1)
                                    await close_button.click()
                                    print("彈窗關閉！")
                                    return True
                            except Exception as e:
                                print(f"沒找到彈窗：{e}")
                                continue  # 尝试下一种选择器
                return False
        except Exception as e:
            print(f"留言失败: {str(e)}")
            return False
    # """發文、推文"""
    async def tweet_comment(self):
        tweet = await self.fetch_data(f"http://aj.ry188.vip/api/GetUrlList.aspx?Account={self.username}&Count1={self.Count1}&Count2={self.Count2}")
        response_url = tweet.split("|+|")
        post_url = response_url[0].split("{}")
        # 發文內容設置
        print(post_url)  # 發文網址
        print(response_url[5])  # 客戶代號
        print(response_url[1])  # 分享的網址
        print(response_url[2])  # 廣告的文案
        for i in range(len(post_url)):
            await self.page.goto(url=post_url[i], wait_until='load',timeout=50000)
            if await self.url_open_except() :# 檢測網站目前無法查看此內容
                continue
            isno_groups = await self.join_groups()#加社团
            if not isno_groups:
                try:
                    Mentions_selector = f'//div[@aria-orientation="horizontal" and @role="tablist"]//a[@role="tab" and @tabindex="0"]//span[contains(text(),"討論區") or contains(text(),"讨论")]/..'
                    Mentions_but = await self.page.wait_for_selector(Mentions_selector, timeout=10000)
                    if Mentions_but:
                        await Mentions_but.scroll_into_view_if_needed()
                        await Mentions_but.click()
                except Exception as e:
                    print(f"没有找到讨论区位置: {str(e)}")
            if not isno_groups:
                try:
                    option_selector ='//span[contains(text(), "留個言吧……") or contains(text(), "...") or contains(text(), "分享心情...")]/..'
                    option_but = await self.page.wait_for_selector(option_selector, timeout=10000)
                    if option_but:
                        await option_but.scroll_into_view_if_needed()
                        await option_but.click()
                        response = response_url[1]+" "+response_url[2]
                        print(response)
                        await self.personal_release(response)
                        await self.warning_prompt()
                        await self.get_tweet_comment(response_url[5])

                except Exception as e:
                    print(f"没有找到可发布贴文位置: {str(e)}")
                await asyncio.sleep(5)

    async def get_tweet_comment(self,code):
        await asyncio.sleep(5)
        try:
            friend_selectors = '//div[@aria-posinset="NaN" or @aria-posinset="1"]//span[contains(text(), "刚") or contains(text(), "剛")]'
            friend_but = await self.page.wait_for_selector(friend_selectors, timeout=15000)

            if friend_but:
                await friend_but.scroll_into_view_if_needed()
                await friend_but.click()
                await asyncio.sleep(8)
                current_url = await self.page.evaluate("() => window.location.href")
                print(current_url)
                await self.report_up_tweet_comment(current_url, code)
        except Exception as e:
            print(f"没有找到可发布贴文位置: {str(e)}")
        await asyncio.sleep(3)
    #推文
    async def post_comment(self):
        post = await self.fetch_data(
            f"http://aj.ry188.vip/api/GetPostUrlList.aspx?Account={self.username}&UrlCount={self.Count_num}&Count1={self.Count1}&Count2={self.Count2}")
        response_url = post.split("|+|")
        post_url = response_url[0].split("{}")
        print(post_url)  # 推文留言網址
        comment_text = response_url[1].split("{}")
        print(comment_text)  # 推文內容
        for i in range(len(post_url)):
            await self.page.goto(url=post_url[i], wait_until='load', timeout=50000)
            current_url = await self.page.evaluate("() => window.location.href")
            print("當前網頁：", current_url)
            if await self.url_open_except() :# 檢測網站目前無法查看此內容
                await self.report_dawn_post_status(current_url)
                continue
            if self.Is_post_like:
                await self.post_nei_like()#点赞
            await self.post_nei_comment(random.choice(comment_text))#留言
            await self.report_up_post_status(current_url)

    # 加社團up
    async def add_join_groups(self):
        groups = await self.fetch_data2(
            f"http://aj.ry188.vip/api/GetGroupUrl.aspx?Account={self.username}")
        is_on_line = parse_bool(groups["IsOnLineGroupData"])#是否在線社團
        answer = ["遵守版規", "同意版規", "感謝版主"]
        for i in range(len(groups["GroupDataList"])):
            await self.page.goto(url="https://www.facebook.com/groups/"+groups["GroupDataList"][i]["GroupId"], wait_until='load', timeout=50000)
            if is_on_line:
                for s in range(1, 4):
                    if groups["GroupDataList"][i]["Answer" + str(s)] != "" and groups["GroupDataList"][i]["IsAnswer"]:
                        answer[i] = groups["GroupDataList"][i]["Answer" + str(s)]
                if await self.join_groups():
                    await asyncio.sleep(random.uniform(5, 10))
                    await self.answer_questions(answer)
                    await self.report_add_join_groups(
                        "https://www.facebook.com/groups/" + groups["GroupDataList"][i]["GroupId"])#上傳add社團
            else:
                if await self.join_groups():
                    await asyncio.sleep(random.uniform(5, 10))
                    await self.answer_questions(answer)
                    await self.report_add_join_groups(
                        "https://www.facebook.com/groups/"+groups["GroupDataList"][i]["GroupId"])#上傳add社團

    # 加社團回答問題
    async def answer_questions(self,answer):
        click = 0
        for i in range(1,4):
            try:
                option_selector = f'//div[contains(@aria-label, "回答問題") and @role="dialog" or contains(@aria-label, "回答问题") and @role="dialog"]//div[contains(@class, "x1c1uobl")]/div[{i}]//textarea[contains(@placeholder, "撰寫回答") or contains(@placeholder, "输入回答")]'
                option_but = await self.page.wait_for_selector(option_selector, timeout=10000)
                if option_but:
                    await option_but.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(1, 2))
                    await option_but.click()
                    await option_but.fill(answer[i-1])
                    click += 1
            except Exception as e:
                print(f"没有找到回答問題窗口: {str(e)}")
                break#一次找不到就出去
        if click >= 1:
            try:
                submit_selector = f'//div[contains(@aria-label, "回答問題") and @role="dialog" or contains(@aria-label, "回答问题") and @role="dialog"]//div[contains(@aria-label, "提交") and @role="button" and @tabindex="0"]'
                submit_but = await self.page.wait_for_selector(submit_selector, timeout=10000)
                if submit_but:
                    await submit_but.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(1, 2))
                    await submit_but.click()
            except Exception as e:
                print(f"没有找到提交: {str(e)}")
        await asyncio.sleep(5)

    #加社團
    async def join_groups(self):
        try:
            option_selector = '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x2lah0s x193iq5w x1icxu4v x25sj25 x1yrsyyn x17upfok xdl72j9 x1iyjqo2 x1l90r2v x13a6bvl"]//div[@aria-label="加入社團" or @aria-label="加入小组"]'
            option_but = await self.page.wait_for_selector(option_selector, timeout=10000)
            if option_but:
                await option_but.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                print("加社团")
                await option_but.click()
                await asyncio.sleep(random.uniform(5, 8))
                return True
        except Exception as e:
            print(f"没有找到加入社團,可能已經申請過: {str(e)}")
            return False

    # 養號
    async def account_nurturing(self):
        if self.ConfirmFriend:
            await self.confirm_friend_invitation()#確認好友邀請
        if self.addFriend:
            await self.add_friend_invitation()#添加好友
        if self.is_personal:
            await self.post_personal_updates()#發佈個人動態
        if self.is_home_like:
            await self.home_post() # FB首页留言

    async def fan_pages(self):
        request_data = await self.fetch_data("http://aj.ry188.vip/api/GetFenPageData.aspx?Account=272275")
        data_url = request_data.split("|+|")
        home_page_data_split = data_url[0].split("{}")# 粉丝专页首頁网址
        tweet_data_split = data_url[1].split("{}")# 粉丝专页推文网址
        outgoing_message = data_url[2].split("{}")  # 粉丝专页发文内容
        leave_message = data_url[3].split("{}")  # 粉丝专页留言内容
        code = data_url[6]  # 客户代号
        if self.is_home_page or not self.fans_home_like:
            await self.fans_home_page(home_page_data_split,random.choice(outgoing_message))#粉丝专页发文首页
        if self.is_leave_page or not self.leave_page_like:
            await self.fans_leave_page(tweet_data_split,random.choice(leave_message),code)#粉丝专页贴文留言

    async def fans_home_page(self,home_page_data_split,comment_text):
        for i in range(len(home_page_data_split)):
            await self.page.goto(url=home_page_data_split[i], wait_until='load', timeout=50000)
            title = await self.page.title()
            if "Facebook" in title:
                await asyncio.sleep(3)
            else:
                print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                await asyncio.sleep(10)  # 等待10秒
            #点赞....
            if not self.fans_home_like :
                print("未开发")
            if self.is_home_page:
                try:
                    Mentions_selector = f'//div[@aria-orientation="horizontal" and @role="tablist"]//a[@role="tab" and @tabindex="0"]//span[contains(text(),"Mentions") or contains(text(),"提及")]/..'
                    Mentions_but = await self.page.wait_for_selector(Mentions_selector, timeout=10000)
                    if Mentions_but:
                        await Mentions_but.scroll_into_view_if_needed()
                        await Mentions_but.click()
                        await asyncio.sleep(random.uniform(4, 6))
                        # 查找留言按钮
                        friend_selectors = [
                            '//span[contains(text(), "留言給") or contains(text(), "对")]/ancestor::div[@role="button"]',
                            '//div[@role="button"]//span[contains(text(), "留言給") or contains(text(), "对")]',
                        ]
                        for selectors in friend_selectors:
                            friend_but = await self.page.wait_for_selector(selectors, timeout=15000)

                            if friend_but:
                                await friend_but.scroll_into_view_if_needed()
                                await friend_but.click()
                                await asyncio.sleep(random.uniform(3, 5))
                                await self.personal_release(comment_text)
                                break
                            else:
                                print("未找到留言按钮，跳过此专页")
                except Exception as e:
                    print(f"没有找到Mentions: {str(e)}")

        await asyncio.sleep(random.uniform(3, 5))

    async def fans_leave_page(self,tweet_data_split,comment_text,code):
        for i in range(len(tweet_data_split)):
            await self.page.goto(url=tweet_data_split[i], wait_until='load', timeout=50000)
            title = await self.page.title()
            if "Facebook" in title:
                await asyncio.sleep(3)
            else:
                print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                await asyncio.sleep(10)  # 等待10秒
            if await self.url_open_except():  # 檢測網站目前無法查看此內容
                await self.report_dawn_post_status(tweet_data_split[i])
                continue
            if not self.leave_page_like:
                await self.post_nei_like()  # 点赞
            if self.is_leave_page:
                await self.post_nei_comment(comment_text)  # 留言
            await self.report_up_fans_post_status(code,tweet_data_split[i])
        await asyncio.sleep(random.uniform(3, 5))

    async def confirm_friend_invitation(self):

        await self.page.goto(url="https://www.facebook.com/friends/requests", wait_until='load',timeout=50000)
        title = await self.page.title()
        if "Facebook" in title:
            await asyncio.sleep(3)
        else:
            print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
            await asyncio.sleep(10)  # 等待10秒
        confirm_friend_number = self.ConfirmFriend_num
        count_friend_num = 0
        while True:
            try:
                friend_selector = f'//div[@aria-label="交友邀請" and @role="navigation" or @aria-label="加好友请求" and @role="navigation"]//div[@role="button" and @tabindex="0" and contains(@aria-label,"確認") or @role="button" and @tabindex="0" and contains(@aria-label,"确认")]'
                friend_but = await self.page.wait_for_selector(friend_selector, timeout=10000)
                if friend_but:
                    await friend_but.scroll_into_view_if_needed()
                    await friend_but.click()
                    await asyncio.sleep(random.uniform(4, 6))
                    count_friend_num += 1
                    print("確認朋友成功",count_friend_num)
                    if count_friend_num >= confirm_friend_number :break
            except Exception as e:
                print(f"没有找到可以確認的朋友或沒有申請: {str(e)}")
                break

    async def add_friend_invitation(self):

        await self.page.goto(url="https://www.facebook.com/friends/suggestions", wait_until='load',timeout=50000)
        title = await self.page.title()
        if "Facebook" in title:
            await asyncio.sleep(3)
        else:
            print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
            await asyncio.sleep(10)  # 等待10秒
        add_friend_number = self.addFriend_num
        count_add_friend_num = 0
        while True:
            try:
                friend_selector = f'//div[@aria-label="建議" and @role="navigation" or @aria-label="推荐用户" and @role="navigation"]//div[@role="button" and @tabindex="0" and contains(@aria-label,"加朋友") or @role="button" and @tabindex="0" and contains(@aria-label,"加好友")]'
                friend_but = await self.page.wait_for_selector(friend_selector, timeout=10000)
                if friend_but:
                    await friend_but.scroll_into_view_if_needed()
                    await friend_but.click()
                    await asyncio.sleep(random.uniform(4, 6))
                    count_add_friend_num += 1
                    print("添加朋友成功",count_add_friend_num)
                    if count_add_friend_num >= add_friend_number :break
            except Exception as e:
                print(f"没有找到可以添加的朋友或推薦: {str(e)}")
                break

    async def post_personal_updates(self):
        tweet = await self.fetch_data(
            f"http://aj.ry188.vip/api/GetUrlList.aspx?Account={self.username}&Count1={self.Count1}&Count2={self.Count2}")
        response_url = tweet.split("|+|")
        await self.page.goto(url="https://www.facebook.com/", wait_until='load',timeout=50000)
        title = await self.page.title()
        if "Facebook" in title:
            await asyncio.sleep(3)
        else:
            print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
            await asyncio.sleep(10)  # 等待10秒
        try:
            friend_selector = f'//div[@aria-label="建立貼文" and @role="region" or @aria-label="创建帖子" and @role="region"]//span[contains(text(), "在想些什麼") or contains(text(), "?") or contains(text(), "分享你的新鲜事吧") or contains(text(), "!")]/..'
            friend_but = await self.page.wait_for_selector(friend_selector, timeout=10000)
            if friend_but:
                await friend_but.scroll_into_view_if_needed()
                await friend_but.click()
                await asyncio.sleep(random.uniform(4, 6))
                response = response_url[6] + " " + random.choice(response_url[3].split("{}"))
                await self.personal_release(response)
        except Exception as e:
            print(f"没有找到建立貼文: {str(e)}")

    async def personal_release(self,comment_text=None):

        try:
            input_selector = '//div[@role="dialog"]//div[@role="textbox" and contains(@aria-placeholder,"建立公開貼文……") or @role="textbox" and contains(@aria-placeholder, "...") or @role="textbox" and contains(@aria-placeholder, "发布公开帖…") or @role="textbox" and contains(@aria-placeholder, "在想些什麼") or @role="textbox" and contains(@aria-placeholder, "分享你的新鲜事吧") or @role="textbox" and contains(@aria-placeholder, "！") or @role="textbox" and contains(@aria-placeholder, "？") or @role="textbox" and contains(@aria-placeholder, "留言給") or @role="textbox" and contains(@aria-placeholder, "对")]'
            input_but = await self.page.wait_for_selector(input_selector, timeout=10000)
            if input_but:
                await input_but.scroll_into_view_if_needed()
                await input_but.click()
                await input_but.fill(comment_text)
                await asyncio.sleep(5)
                await self.personal_release_but()
        except Exception as e:
            print(f"没有找到输入框: {str(e)}")

    async def personal_release_but(self):
        try:
            but_selector = '//div[@role="dialog"]//div[@tabindex="0" and contains(@aria-label,"發佈") or @tabindex="0" and contains(@aria-label, "发布") or @tabindex="0" and contains(@aria-label, "发帖")]'
            but_but = await self.page.wait_for_selector(but_selector, timeout=15000)
            if but_but:
                await but_but.scroll_into_view_if_needed()
                await but_but.click()
                print("发布")
        except Exception as e:
            print(f"没有找到发布按钮: {str(e)}")

    async def post_nei_like(self):

        already_like = '//div[@aria-label="讚" or @aria-label="赞"]'
        cancel_like = '//div[contains(@aria-label, "取消") or contains(@aria-label, "移除")]'
        try:
            but_selector = '//div[@role="dialog"]//div[@class="xbmvrgn x1diwwjn"]'+ already_like
            but_but = await self.page.wait_for_selector(but_selector, timeout=15000)
            if but_but:
                await but_but.scroll_into_view_if_needed()
                await asyncio.sleep(3)
                await but_but.hover()
                await asyncio.sleep(3)
                target_emotion = self.LikeType - 1
                target_emotion_list = ["赞", "大心", "加油", "哈", "哇", "嗚", "怒"]
                emotion_selector = f'//div[@role="button" and @aria-label="{target_emotion_list[target_emotion]}"]'
                try:
                    emotion_button = await self.page.wait_for_selector(emotion_selector, timeout=5000)
                    if emotion_button:
                        await emotion_button.click()
                        print(f"点击了表情: {target_emotion_list[target_emotion]}")
                    else:
                        print("未找到表情按钮，执行默认点赞")
                        await but_but.click()
                except Exception as e:
                    print(f"表情点击失败: {str(e)}")
                    await but_but.click()
            return True
        except Exception as e:
            print(f"点赞失败: {str(e)}")
            try:
                but_selector = '//div[@role="dialog"]//div[@class="xbmvrgn x1diwwjn"]'+ cancel_like
                element = await self.page.wait_for_selector(but_selector , timeout=10000)
                if element:
                    print("已經點過讃")
                return False
            except Exception as e:
                print(f"点赞失败找不到可點讚位置: {str(e)}")

    async def post_nei_comment(self,comment_text):

        try:
            but_selector = '//div[@role="dialog"]//div[@role="textbox" and contains(@aria-label, "留言") or @role="textbox" and contains(@aria-label, "回答")]'
            input_element = await self.page.wait_for_selector(but_selector, timeout=10000)
            if input_element:
                await input_element.scroll_into_view_if_needed()
                aria_label = await input_element.get_attribute('aria-label')
                print(f"获取到的 aria-label 为: {aria_label}")
                await input_element.click()
                await input_element.fill(comment_text)
                await asyncio.sleep(5)
                await self._submit_comment()
        except Exception as e:
            print(f"点赞失败找不到可點讚位置: {str(e)}")

    async def _submit_comment(self):
        """提交评论"""
        try:
            submit_selector = '//div[@role="dialog"]//div[@id="focused-state-composer-submit"]//div[@role="button" and @tabindex="0"]'
            submit_button = await self.page.wait_for_selector(submit_selector, timeout=20000)
            if submit_button:
                await submit_button.scroll_into_view_if_needed()
                await asyncio.sleep(random.randint(8, 14))
                await submit_button.click()
                return True
        except Exception as e:
            print(f"提交评论失败: {str(e)}")
        return False

    async def url_open_except(self):
        try:
            url_selector = '//h2[@dir="auto"]//span[@dir="auto"]'
            url_button = await self.page.wait_for_selector(url_selector, timeout=7000)
            text = await url_button.inner_text()
            if text in "目前無法查看此內容":
                print("目前無法查看此內容")
                return True
        except Exception as e:
            print(f"找不到目前無法查看此內容: {str(e)}")
            return False

    async def report_add_join_groups(self, task_name):
        """异步上报add社團状态"""
        try:
            # 对task_name进行Base64编码并转换为字符串
            encoded_bytes = base64.b64encode(task_name.encode('utf-8'))
            encoded_task_name = encoded_bytes.decode('utf-8')

            url = f"http://aj.ry188.vip/api/UpJoinGroupUrl.aspx?Account={self.username}&Urls={encoded_task_name}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"社團上傳上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"社團上傳上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"社團上傳上报失败: {e}")
            return False
    async def report_up_post_status(self, task_name):
        """异步上报推文網址"""
        try:
            task_name = await self.extract_posturl_ids(task_name)
            url = f"http://aj.ry188.vip/api/UpPostUrl.aspx?Account={self.username}&PostId={task_name}&UserNumber={self.customer_code}&GroupName="

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"推文上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"推文上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"推文上报失败: {e}")
            return False
    async def report_up_fans_post_status(self,user_numer, task_name):
        """异步上报粉丝专页推文網址"""
        try:
            # task_name = await self.extract_posturl_ids(task_name)
            url = f"http://aj.ry188.vip/api/UpPagesPostUrl.aspx?Account={self.username}&UserNumber={user_numer}&Urls={task_name}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"粉丝推文上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"粉丝推文上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"粉丝推文上报失败: {e}")
            return False
    async def report_dawn_post_status(self, task_name):
        """异步上报刪除推文網址"""
        try:
            task_name = await self.extract_posturl_ids(task_name)
            url = f"http://aj.ry188.vip/api/DeleteUrls.aspx?Account={self.username}&PostId={task_name}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"推文上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"推文上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"推文上报失败: {e}")
            return False
    async def report_up_tweet_comment(self, task_name,code):
        """异步上报发文推文網址"""
        try:
            task_name2 = await self.extract_posturl_ids(task_name)
            group_id = ""
            # 一行代码提取所有群组ID
            match = re.search(r'/groups/(\d+)', task_name)
            if match:
                group_id = match.group(1)
                print("提取的群组ID:", group_id)
            else:
                print("未找到群组ID")
            url = f"http://aj.ry188.vip/api/UpUrls.aspx?Account={self.username}&Urls={task_name}&GroupId={group_id}&GroupName='123'&PostId={task_name2}&UserNumber={code}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"发文推文上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"发文推文上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"发文推文上报失败: {e}")
            return False
    async def extract_posturl_ids(self,urls):
        post_ids = ""
        # 匹配各种格式的帖子ID
        pattern = r'/(?:posts/|permalink/|permalink&id=)(\d+)'
        match = re.search(pattern, urls)
        if match:
            post_ids = match.group(1)

        return post_ids

    async def warning_prompt(self):
        await asyncio.sleep(4)
        close_selectors = [
            '//div[@role="dialog"]//div[@aria-label="關閉"]',  # 方式1
            '//div[@aria-label="關閉" and @aria-hidden="false"]' ,# 方式2
            '//div[@aria-label="關閉"]'# 方式3
        ]
        for selector in close_selectors:
            try:
                close_button = await self.page.wait_for_selector(selector, timeout=3000)
                if close_button:
                    await close_button.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await close_button.click()
                    print("彈窗關閉！")
                    return True
            except Exception as e:
                continue  # 尝试下一种选择器

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

    async def fetch_data(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                return await response.text()

    async def fetch_data2(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                return await response.json()

    async def sleep_time(self, rest_time=60):
        """执行休息任务"""
        asyncio.create_task(self.report_task_status(f"正在執行倒計時..."))
        await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"開始休息，持續 {rest_time} 秒...")

        # 发送倒计时信号
        if self.status_window:
            self.status_window.countdown_signal.emit(rest_time)

        # 使用异步方式等待，同时保持UI响应
        start_time = time.time()
        while time.time() - start_time < rest_time:
            await asyncio.sleep(1)
            remaining = rest_time - int(time.time() - start_time)
            if self.status_window and remaining > 0:
                self.status_window.countdown_signal.emit(remaining)

        await self.robust_update_status("休息結束，繼續執行任務...")

        # 隐藏倒计时显示
        if self.status_window:
            self.status_window.countdown_signal.emit(0)

    async def report_online_status(self):
        """异步上报在线状态"""
        try:
            url = f"http://aj.ry188.vip/API/UpDataState.aspx?Account={self.username}&DeviceNumber={self.device_number}&DeviceCode={self.machine_code}&IsPhone={self.is_phone}&RemoteId={self.remote_id}&RunText=在线"

            # 使用 aiohttp 进行异步请求
            timeout = aiohttp.ClientTimeout(total=10)  # 设置10秒超时
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"在线状态上报: {response.status}")
                    return True
        except asyncio.TimeoutError:
            print("在线状态上报超时")
            return False
        except Exception as e:
            print(f"在线状态上报失败: {e}")
            return False

    async def report_task_status(self, task_name):
        """异步上报任务执行状态"""
        try:
            url = f"http://aj.ry188.vip/API/UpDataRunState.aspx?Account={self.username}&DeviceNumber={self.device_number}&RunText={task_name}&DeviceCode={self.machine_code}&IsPhone={self.is_phone}&RemoteId={self.remote_id}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"任务状态上报: {task_name} - {response.status}")
                    return True
        except asyncio.TimeoutError:
            print(f"任务状态上报超时: {task_name}")
            return False
        except Exception as e:
            print(f"任务状态上报失败: {e}")
            return False
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
    def generate_machine_code(self):
        # 获取设备型号（去除空格）
        device_model = platform.machine().replace(" ", "")
        print(f"设备型号：{device_model}")

        # 获取 MAC 地址
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                            for elements in range(0, 2 * 6, 2)][::-1])
        except:
            mac = "00:00:00:00:00:00"
        print(f"Mac：{mac}")

        # 获取系统版本号
        try:
            if platform.system() == "Windows":
                system_version = platform.version()
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['sw_vers', '-productVersion'],
                                        capture_output=True, text=True)
                system_version = result.stdout.strip()
            else:  # Linux/Android
                system_version = platform.release()
        except:
            system_version = "未知版本"
        print(f"系统版本号：{system_version}")

        # 组合机器码并 Base64 编码
        machine_code = f"{device_model}{mac}{system_version}"
        base64_encoded = base64.b64encode(machine_code.encode('utf-8')).decode('utf-8')

        return base64_encoded
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