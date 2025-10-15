import asyncio
import random
import time
import json
import base64
import platform
import os
import winreg  # 仅适用于Windows
import shutil  # 适用于Linux和macOS
import uuid
import subprocess
import aiohttp
import requests

from PyQt5.QtWidgets import QApplication
from login_window import win_main
from playwright.async_api import async_playwright

class Crawler:
    def __init__(self, cookies,data,users,start_position,content0,content1, task_order=None, rest_times=None):
        self.playwright = None
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 25
        self.is_logged_in = False
        self.browser_path = get_chrome_path()
        #关键字
        self.Key_IsEnableKey = parse_bool(data["SendData"]["ConfigDatas"]["Key_IsEnableKey"])  # 是否启用关键字
        self.Keys = data["SendData"]["ConfigDatas"]["Keys"]  # 关键字
        self.Key_TrackingUserCount = int(data["SendData"]["ConfigDatas"]["Key_TrackingUserCount"])  # 追踪数量
        self.Key_SearchCount = int(data["SendData"]["ConfigDatas"]["Key_SearchCount"])  # 搜索数量
        self.Key_IsEnableTracking = parse_bool(data["SendData"]["ConfigDatas"]["Key_IsEnableTracking"])  # 是否启用追踪
        self.Key_IsEnableLike = parse_bool(data["SendData"]["ConfigDatas"]["Key_IsEnableLike"])  # 是否点赞
        self.Key_IsEnableLeave = parse_bool(data["SendData"]["ConfigDatas"]["Key_IsEnableLeave"])  # 是否留言
        self.Key_IntervalTime = int(data["SendData"]["ConfigDatas"]["Key_IntervalTime"])  # 间隔时间
        #首页浏览
        self.Home_IsEnableBrowse = parse_bool(data["SendData"]["ConfigDatas"]["Home_IsEnableBrowse"])  # 是否首页浏览
        self.Home_IsEnableLike = parse_bool(data["SendData"]["ConfigDatas"]["Home_IsEnableLike"])  # 是否首页点赞
        self.Home_IsEnableLeave = parse_bool(data["SendData"]["ConfigDatas"]["Home_IsEnableLeave"])  # 是否首页留言
        self.Home_HomeBrowseCount = int(data["SendData"]["ConfigDatas"]["Home_HomeBrowseCount"])  # 首页贴文数
        #用户互动
        self.HuDong_IsHuDong = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsHuDong"])  # 是否用户互动
        self.HuDong_IsEnableTracking = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsEnableTracking"])  # 是否用户追踪
        self.HuDong_IsEnableLike = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsEnableLike"])  # 是否用户点赞
        self.HuDong_IsEnableLeave = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsEnableLeave"])  # 是否用户留言
        self.HuDong_IsEnableMsg = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsEnableMsg"])  # 是否用户私信
        self.HuDong_TrackingUserCount = int(data["SendData"]["ConfigDatas"]["HuDong_TrackingUserCount"])  # 用户追踪数
        self.HuDong_SendUserCount = int(data["SendData"]["ConfigDatas"]["HuDong_SendUserCount"])  # 发送数量
        self.leavetext_messags = str(data["SendData"]["LeaveText"]).split("\n\n\n")  # 留言内容
        self.leavetext_MsgText = str(data["SendData"]["MsgText"]).split("\n\n\n")  # 私信内容
        self.UsersLists = users
        self.new_user_Tracking_num = 0
        self.Key_user_Tracking_num = 0
        self.new_fans_num = 0
        self.key_mun = 0
        self.init = data
        self.pic_path = None
        self.status_window = None  # 状态窗口引用
        self.Start_Position = start_position
        self.User_Id = content1
        self.task_order = task_order or []
        self.executed_tasks = []  # 用于跟踪已执行的任务
        self.rest_times = rest_times or {}  # 存储休息时间配置
        self.account = content1  # 保存账号
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
    # def update_status(self, text):
    #     """更新状态窗口"""
    #     if self.status_window:
    #         # 使用信号来更新 UI，确保线程安全
    #         self.status_window.update_signal.emit(text)
    #         # 立即处理事件队列
    #         QApplication.processEvents()

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
        # 程序开始时上报在线状态
        await self.report_online_status()

        # 设置定时器，每隔一段时间上报一次在线状态
        asyncio.create_task(self.periodic_online_report())
        if 0 in self.task_order or 1 in self.task_order or 2 in self.task_order :
            ##await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status("啟動瀏覽器...")
            #await asyncio.sleep(random.uniform(2, 4))
            self.playwright = await async_playwright().start()
            # 确保Playwright连接完全建立
            await asyncio.sleep(1)

            self.browser = await self.playwright.chromium.launch(headless=False, executable_path=self.browser_path,
                ignore_default_args=[
                    '--enable-automation',
                    '--disable-popup-blocking'
                ])
            # 确保浏览器完全启动
            await asyncio.sleep(1)

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
            # 确保上下文完全建立
            await asyncio.sleep(1)

            # 应用cookies到上下文
            if self.cookies:
                await context.add_cookies(self.cookies)
                print("已应用cookies到浏览器上下文")
                await asyncio.sleep(1)

            print("已确认登录状态，开始执行任务...")
            self.page = await context.new_page()
            await asyncio.sleep(1)

        function_map = {
            0: self.Home_clicks,
            1: self.key_clicks,
            2: self.Users_post,
            3: self.sleep_time
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
                        if task_index == 3:  # 休息时间任务
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

        # if self.Home_IsEnableBrowse:
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.robust_update_status("開始ig主頁貼文留言...")
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.Home_clicks()#个人主页留言
        # if self.Key_IsEnableKey:
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.robust_update_status("開始關鍵字用戶留言...")
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.key_clicks()#关键字
        # if self.HuDong_IsHuDong:
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.robust_update_status("開始用戶個人主頁留言...")
        #     #await asyncio.sleep(random.uniform(2, 4))
        #     await self.Users_post()#用户个人主页留言
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status("全部任務完成...")
        #await asyncio.sleep(random.uniform(2, 4))

        await self.browser.close()
    # async def Home_clicks(self):
    #     await self.page.goto(url="https://www.instagram.com/", wait_until='load', timeout=50000)
    #     # await self.force_minimize_browser()
    #     await asyncio.sleep(8)
    #     """执行自动化点击操作"""
    #     await asyncio.sleep(random.uniform(3, 4))
    #     await self.robust_update_status("開始ig主頁貼文留言...")
    #     await asyncio.sleep(random.uniform(3, 4))
    #     #檢查是否有貼文
    #     try:
    #         end_of_content = await self.page.query_selector("text='没有更多新内容了'")
    #         if end_of_content:
    #             print("检测到'没有更多新内容了'提示，滑动到底部加载更多...")
    #             #await asyncio.sleep(random.uniform(2, 4))
    #             await self.robust_update_status("檢測到主頁沒有更多貼文滑動刷新更多内容")
    #             #await asyncio.sleep(random.uniform(2, 4))
    #             # 只滑动一次
    #             await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    #             await asyncio.sleep(5)  # 等待新内容加载
    #     except Exception as e:
    #         print(f"检查新内容提示时出错: {str(e)}")
    #     num_posts = self.Home_HomeBrowseCount # 要操作的帖子数量
    #     comments = self.leavetext_messags
    #     for post_index in range(1, num_posts + 1):
    #         try:
    #             # 定位帖子
    #             post_locator = f"article >> nth={post_index - 1}"
    #             await self.page.wait_for_selector(post_locator, timeout=15000)
    #             post = self.page.locator(post_locator)
    #             await post.scroll_into_view_if_needed()
    #             await asyncio.sleep(2)
    #             print(f"正在处理第 {post_index} 个帖子...")
    #             #await asyncio.sleep(random.uniform(2, 4))
    #             await self.robust_update_status(f"正在處理第 {post_index} 個貼文")
    #             #await asyncio.sleep(random.uniform(2, 4))
    #             # 点赞
    #             if self.Home_IsEnableLike :
    #                 #await asyncio.sleep(random.uniform(2, 4))
    #                 await self.robust_update_status(f"開始執行點讚第 {post_index} 個貼文")
    #                 #await asyncio.sleep(random.uniform(2, 4))
    #                 await self.like_post(post_index)
    #
    #             # 留言
    #             if self.Home_IsEnableLeave :
    #                 #await asyncio.sleep(random.uniform(2, 4))
    #                 await self.robust_update_status(f"開始執行留言第 {post_index} 個貼文")
    #                 #await asyncio.sleep(random.uniform(2, 4))
    #                 await self.comment_post(post_index, random.choice(comments))
    #
    #             # 随机等待
    #             await asyncio.sleep(random.uniform(3, 7))
    #
    #         except Exception as e:
    #             print(f"处理第 {post_index} 个帖子时出错: {str(e)}")
    #             continue
    async def execute_task_with_timeout(self, task_func, task_index, position, completion_time):
        """执行带超时控制的任务"""
        task_names = {
            0: "首頁留言",
            1: "關鍵字任務",
            2: "用戶互動"
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
    async def Home_clicks(self):
        await self.page.goto(url="https://www.instagram.com/", wait_until='load', timeout=50000)
        await asyncio.sleep(8)
        await self.report_task_status("正在執行首頁任務")
        # 检查是否有"没有更多新内容了"提示
        try:
            end_of_content = await self.page.query_selector("text='没有更多新内容了'")
            if end_of_content:
                print("检测到'没有更多新内容了'提示，滑动到底部加载更多...")
                await self.robust_update_status("檢測到主頁沒有更多貼文滑動刷新更多内容")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(5)
        except Exception as e:
            print(f"检查新内容提示时出错: {str(e)}")

        num_posts = self.Home_HomeBrowseCount  # 要操作的帖子数量
        comments = self.leavetext_messags
        for post_index in range(1, num_posts + 1):
            try:
                # 先获取当前可见的帖子数量
                try:
                    articles = await self.page.query_selector_all("article")
                    max_visible_posts = len(articles)
                    print(f"当前可见帖子数量: {max_visible_posts}")
                except Exception as e:
                    print(f"获取帖子数量失败: {str(e)}")
                    max_visible_posts = 7
                # 如果请求的索引超过可见帖子数量，则使用最后一个可见帖子
                actual_index = min(post_index,max_visible_posts) - 1

                post_locator = f"article >> nth={actual_index}"
                await self.page.wait_for_selector(post_locator, timeout=15000)
                post = self.page.locator(post_locator)

                # 滚动前获取链接
                link_locator_before = post.locator('a[href*="/p/"]')
                if await link_locator_before.count() == 0:
                    print("未找到帖子链接，跳过该帖子")
                    continue  # 或者进行其他处理

                post_url_before = await link_locator_before.first.get_attribute('href')

                await post.scroll_into_view_if_needed()
                await asyncio.sleep(4)

                # 滚动后再次获取链接
                link_locator_after = post.locator('a[href*="/p/"]')
                if await link_locator_after.count() == 0:
                    print("滚动后未找到帖子链接，跳过该帖子")
                    continue

                post_url_after = await link_locator_after.first.get_attribute('href')

                # 对比两次获取的链接
                if post_url_before != post_url_after:
                    print(f"警告：滚动前后链接不一致！")
                    print(f"滚动前: {post_url_before}")
                    print(f"滚动后: {post_url_after}")
                    # 这里可以根据需要处理不一致的情况
                    # 例如选择使用其中一个链接或抛出异常
                    articles = await self.page.query_selector_all("article")
                    for i, po in enumerate(articles):
                        link_element = await po.query_selector('a[href*="/p/"]')
                        if link_element:
                            post_url = await link_element.get_attribute('href')
                            print(i, post_url)
                            if post_url == post_url_before:
                                print("滾動前位置：",i)
                                actual_index = i
                                break
                else:
                    print(f"链接一致: {post_url_before}")

                print(f"正在处理第 {post_index} 个帖子 (实际索引: {actual_index + 0})...")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"正在處理第 {post_index} 個貼文")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.report_task_status(f"正在處理第 {post_index} 個貼文")
                # 点赞
                if self.Home_IsEnableLike:
                    #await asyncio.sleep(random.uniform(2, 4))
                    await self.robust_update_status(f"開始執行點讚第 {post_index} 個貼文")
                    #await asyncio.sleep(random.uniform(2, 4))
                    await self.like_post(actual_index + 1)  # 传递实际索引

                # 留言
                if self.Home_IsEnableLeave:
                    #await asyncio.sleep(random.uniform(2, 4))
                    await self.robust_update_status(f"開始執行留言第 {post_index} 個貼文")
                    #await asyncio.sleep(random.uniform(2, 4))
                    await self.comment_post(actual_index + 1, random.choice(comments))  # 传递实际索引

                # 随机等待
                await asyncio.sleep(random.uniform(3, 7))
            except Exception as e:
                print(f"处理第 {post_index} 个帖子时出错: {str(e)}")
                break

    async def key_clicks(self):
        await self.report_task_status("正在關鍵字用戶留言")
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status("開始關鍵字用戶留言...")
        #await asyncio.sleep(random.uniform(2, 4))
        print("关键字")
        post_links = []
        keyword = self.Keys.split('#')

        # 收集链接
        for i in range(len(keyword)):
            print("关键字:", keyword[i])
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"當前執行關鍵字： {keyword[i]} ")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.report_task_status(f"當前執行關鍵字： {keyword[i]} ")
            await self.page.goto(url="https://www.instagram.com/", wait_until='load', timeout=50000)
            # await self.force_minimize_browser()
            await asyncio.sleep(8)

            try:
                # 点击搜索按钮
                search_selector = 'svg[aria-label="搜索"], svg[aria-label="搜尋"], svg[aria-label="Search"]'
                search_button = await self.page.wait_for_selector(search_selector, timeout=10000)
                await search_button.click()
                await asyncio.sleep(2)

                input_selector = 'input[aria-label*="搜索"], input[aria-label*="搜尋"], input[aria-label*="Search"]'
                search_input = await self.page.wait_for_selector(input_selector, timeout=10000)
                await search_input.type(keyword[i], delay=random.randint(50, 150))
                await asyncio.sleep(random.uniform(6, 8))

                # 等待搜索结果加载
                await self.page.wait_for_selector(
                    'div[class="x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xh8yej3 xocp1fn"]', timeout=15000)
                await asyncio.sleep(3)
                # 切换到最新标签页
                latest_tab = await self.page.query_selector('text="最新"')
                if not latest_tab:
                    latest_tab = await self.page.query_selector('text="Latest"')
                if latest_tab:
                    await latest_tab.click()
                    await asyncio.sleep(3)

                # 获取搜索结果
                posts = await self.page.query_selector_all(
                    'div[class="x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xh8yej3 xocp1fn"] object[type="nested/pressable"] a[href^="/"][role="link"][tabindex="0"]')
                print(f"找到 {len(posts)} 个相关帖子")

                # 获取所有匹配元素的href属性
                for post in posts:
                    href = await post.get_attribute('href')
                    if href:
                        full_url = "https://www.instagram.com" + href
                        post_links.append(full_url)

                        # 如果已经收集到足够的链接，立即跳出循环
                        if len(post_links) >= self.Key_SearchCount:
                            break

                print(f"找到 {len(post_links)} 个相关帖子，链接列表: {post_links}")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"獲取關鍵字： {keyword[i]} 當前總數： {len(post_links)} 個用戶")
                #await asyncio.sleep(random.uniform(2, 4))

                # 如果已经收集到足够的链接，跳出关键字循环
                if len(post_links) >= self.Key_SearchCount:
                    break

            except Exception as e:
                print(f"关闭对话框失败: {str(e)}")
                continue

            # 如果已经收集到足够的链接，跳出循环
            if len(post_links) >= self.Key_SearchCount:
                break

            await asyncio.sleep(8)

        # 处理用户
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行保存的關鍵字的用戶")
        #await asyncio.sleep(random.uniform(2, 4))

        # 关键字个人主页操作
        for k in range(min(len(post_links), self.Key_SearchCount)):  # 限制循环次数
            if self.key_mun >= self.Key_SearchCount:  # 如果已经处理足够数量的用户，跳出循环
                break

            print(f"第{k + 1}个,当前用户：{post_links[k]}")
            await self.report_task_status(f"執行保存的關鍵字第 {k + 1} 個用戶")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"執行保存的關鍵字第 {k + 1} 個用戶")
            #await asyncio.sleep(random.uniform(2, 4))

            await self.page.goto(url=post_links[k], wait_until='load', timeout=50000)
            # await self.force_minimize_browser()
            # 添加额外等待 - 确保用户界面完全加载
            await self.page.wait_for_selector("header section", timeout=30000)
            await asyncio.sleep(3)

            if self.Key_IsEnableTracking and self.Key_user_Tracking_num < self.Key_TrackingUserCount:
                print("追踪")
                val = 'key'
                await self.UsersTracking(val)
                await asyncio.sleep(8)

            if self.Key_IsEnableLike or self.Key_IsEnableLeave:
                print("留言")
                await self.message_post()

            self.key_mun += 1
            await asyncio.sleep(self.Key_IntervalTime)

    async def Users_post(self):
        await self.report_task_status(f"執行用戶個人主頁留言")
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status("開始用戶個人主頁留言...")
        #await asyncio.sleep(random.uniform(2, 4))
        for i in range(self.Start_Position, len(self.UsersLists)):
            user_id = self.UsersLists[i]
            print("处理用户ID:", user_id)

            await self.page.goto(url="https://www.instagram.com/"+user_id, wait_until='load', timeout=50000)
            # await self.force_minimize_browser()
            # 添加额外等待 - 确保用户界面完全加载
            await self.page.wait_for_selector("header section", timeout=30000)
            await asyncio.sleep(3)
            await self.report_task_status(f"執行用戶個人主頁留言:{user_id}")
            if self.HuDong_IsEnableTracking and self.new_user_Tracking_num < self.HuDong_TrackingUserCount:
                print("追踪")
                val = 'users'
                await self.report_task_status(f"執行用戶個人主頁留言/追踪")
                await self.UsersTracking(val)
                await asyncio.sleep(8)

            if self.HuDong_IsEnableMsg and self.new_fans_num < self.HuDong_SendUserCount:
                print("私信")
                await self.report_task_status(f"執行用戶個人主頁留言/私信")
                comments = self.leavetext_MsgText
                await self.Personal_post(random.choice(comments))
                await asyncio.sleep(8)

            if self.HuDong_IsEnableLike or self.HuDong_IsEnableLeave:
                print("留言")
                await self.report_task_status(f"執行用戶個人主頁留言/留言")
                await self.message_post()
            # 更新进度
            current_position = i + 1
            save_progress(self.User_Id, self.UsersLists, current_position)

            # 每处理一个用户等待3秒
            await asyncio.sleep(3)

        # 处理完成后清除进度
        clear_progress(self.User_Id)
        print("所有用户处理完成!")

    async def UsersTracking(self,val):
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行追蹤用戶")
        #await asyncio.sleep(random.uniform(2, 4))
        try:
            # 使用更可靠的选择器定位追踪按钮
            button_selector = "header section div:has(> div:has(button)) button:has(div > div)"
            element = await self.page.wait_for_selector(button_selector, timeout=30000)  # 增加超时时间

            # 检查按钮状态
            text = await element.inner_text()
            print("获取的按钮文本：", text)

            if text in ["已关注", "追蹤中", "Following","已发送","已發送"]:
                print("已追踪，跳过")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"已追蹤過該用戶，跳過...")
                #await asyncio.sleep(random.uniform(2, 4))
                return False

            # 点击追踪按钮
            await element.click()
            print("成功点击追踪")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"成功追蹤")
            #await asyncio.sleep(random.uniform(2, 4))
            if val == 'key':
                self.Key_user_Tracking_num += 1
            else:
                self.new_user_Tracking_num += 1

            await asyncio.sleep(5)  # 适当减少等待时间
            return True

        except Exception as e:
            print(f"追踪失败: {str(e)}")
            return False

    async def Personal_post(self,comment_text):
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行發送私信用戶")
        #await asyncio.sleep(random.uniform(2, 4))
        try:
            #查找发信息，發送訊息
            # 使用更可靠的选择器定位私信按钮
            button_selector = "div[role='button']:has-text('发消息'), div[role='button']:has-text('發送訊息'), div[role='button']:has-text('Message')"

            # 等待按钮出现（增加超时时间）
            element = await self.page.wait_for_selector(
                button_selector,
                timeout=20000,  # 延长超时时间
                state="attached"
            )

            # 确保按钮可见
            await element.scroll_into_view_if_needed()
            await element.click()
            # await self.page.evaluate("""() => {
            #     const buttons = document.querySelectorAll('div[role="button"]');
            #     for (const btn of buttons) {
            #         const text = btn.innerText.trim();
            #         if (text === '发消息' || text === '發送訊息') {
            #             btn.click();
            #             return;
            #         }
            #     }
            # }""")
            await asyncio.sleep(random.randint(5, 8))
            try:
                # 尝试多种可能的输入框选择器
                input_selectors = [
                    'div[role="dialog"]',
                    'div[aria-label="发消息"]',
                    'div[aria-label="發送訊息"]',
                    'div[aria-label="Message"]',
                    'div[contenteditable="true"]'
                ]

                input_element = None
                for selector in input_selectors:
                    try:
                        input_element = await self.page.wait_for_selector(
                            selector,
                            timeout=25000,
                            state="attached"
                        )
                        if input_element:
                            break
                    except:
                        continue

                if not input_element:
                    print("无法找到私信输入框")
                    return False

                await input_element.click()
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"發送的私信内容：{comment_text}")
                #await asyncio.sleep(random.uniform(2, 4))
                # await input_element.type(comment_text, delay=random.randint(50, 150))
                await input_element.fill(comment_text)
                print("成功输入私信内容")
                await asyncio.sleep(random.randint(5, 8))#等待发送
                # 3. 发送私信
                send_btn_selector = (
                    'div[aria-label="Send"], '
                    'div[aria-label="发送"], '
                    'div[aria-label="傳送"]'
                )
                try:
                    send_button = await self.page.wait_for_selector(
                        send_btn_selector,
                        timeout=15000
                    )
                    await send_button.click()
                    print("私信发送成功")
                    #await asyncio.sleep(random.uniform(2, 4))
                    await self.robust_update_status(f"私信發送成功")
                    #await asyncio.sleep(random.uniform(2, 4))
                    self.new_fans_num += 1
                except:
                    # 尝试按Enter发送
                    # await input_element.press("Enter")
                    print("使用Enter键发送私信")

            except Exception as e:
                print(f"发送私信失败: {str(e)}")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"該用戶禁止發送私信，跳過...")
                #await asyncio.sleep(random.uniform(2, 4))
                return False
            finally:
                await asyncio.sleep(8)
                # 4. 更可靠的关闭方式
                try:
                    # 使用多种方式尝试关闭对话框
                    close_selectors = [
                        'svg[aria-label="关闭"]',
                        'svg[aria-label="關閉"]',
                        'svg[aria-label="Close"]',
                        'div[aria-label="关闭"]',
                        'div[aria-label="關閉"]',
                        'div[aria-label="Close"]'
                    ]

                    # 如果ESC无效，尝试点击关闭按钮
                    for selector in close_selectors:
                        try:
                            close_button = await self.page.query_selector(selector)
                            if close_button:
                                await close_button.click()
                                await asyncio.sleep(2)
                                # 检查对话框是否关闭
                                if not await self.page.query_selector('div[aria-label="Send"]'):
                                    return
                        except:
                            continue

                except Exception as e:
                    print(f"关闭对话框失败: {str(e)}")

            return True

        except Exception as e:
            print(f"不可发私信: {str(e)}")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"該用戶無法發送私信，跳過...")
            #await asyncio.sleep(random.uniform(2, 4))
            return False

    async def message_post(self):
        """打开用户主页的第一个贴文"""
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行用戶個人主頁留言")
        #await asyncio.sleep(random.uniform(2, 4))
        try:
            # 等待用户主页加载完成 - 使用更可靠的选择器
            await self.page.wait_for_selector('header section', timeout=30000)
            print("用户主页加载完成")
            await asyncio.sleep(2)  # 额外等待确保内容稳定

            # 使用更可靠的选择器定位贴文
            clicked = await self.page.evaluate("""() => {
                // 尝试多种可能的贴文选择器
                const selectors = [
                    'a[href^="/p/"]',  // 标准贴文链接图片类
                    'a[href^="/reel/"]',   // 标准贴文链接视频类
                    'a[href*="/p/"]', // 
                    'a[href*="/reel/"]' 
                ];

                for (const selector of selectors) {
                    const posts = document.querySelectorAll(selector);
                    if (posts.length > 0) {
                        // 找到第一个可见的贴文
                        for (const post of posts) {
                            if (post.offsetParent !== null) { // 检查元素是否可见
                                post.click();
                                return true;
                            }
                        }
                    }
                }
                return false;
            }""")

            if not clicked:
                print("未找到贴文")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"未找到可以發送的貼文，跳過...")
                #await asyncio.sleep(random.uniform(2, 4))
                return False
            await asyncio.sleep(5)
            # 点赞
            if (self.HuDong_IsHuDong and self.HuDong_IsEnableLike) or (self.Key_IsEnableKey and self.Key_IsEnableLike):
                await self.Post_nei_like()
            # 留言
            if (self.HuDong_IsHuDong and self.HuDong_IsEnableLeave) or (self.Key_IsEnableKey and self.Key_IsEnableLeave):
                comments = self.leavetext_messags
                await self.Post_nei_comment(random.choice(comments))

        except Exception as e:
            print(f"打开贴文失败: {str(e)}")
            return False

        await asyncio.sleep(8)
        return True  # 添加返回语句表示成功打开贴文

    async def Post_nei_like(self):
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行用戶貼文點讚")
        #await asyncio.sleep(random.uniform(2, 4))
        try:
            await self.page.wait_for_selector('div[role="dialog"]', state="visible", timeout=15000)

            # 使用JavaScript直接执行点击
            clicked = await self.page.evaluate("""() => {
                // 检查是否已经点赞
                const likedButtons = document.querySelectorAll('svg[aria-label="取消赞"], svg[aria-label="取消讚"], svg[aria-label="收回讚"], svg[aria-label="Unlike"]');
                if (likedButtons.length > 0) {
                    console.log("帖子已点赞，跳过");
                    return false;
                }

                // 查找所有可能的点赞按钮
                const likeButtons = document.querySelectorAll('div[role="button"], button');

                for (const btn of likeButtons) {
                    const svg = btn.querySelector('svg');
                    if (svg) {
                        const label = svg.getAttribute('aria-label') || '';

                        // 检查是否为未点赞状态的按钮
                        if (label.includes('Like') || label.includes('赞') || label.includes('讚')) {
                            if (!label.includes('取消赞') && !label.includes('取消讚') && !label.includes('收回讚') && !label.includes('Unlike')) {
                                btn.click();
                                return true;
                            }
                        }
                    }
                }
                return false;
            }""")

            if clicked:
                print("成功点赞")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"成功點讚")
                await asyncio.sleep(random.uniform(8, 10))
            else:
                print("未找到可点击的点赞按钮或已点赞")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"未找到點讚")
                #await asyncio.sleep(random.uniform(2, 4))

        except Exception as e:
            print(f"点赞失败: {str(e)}")

    async def Post_nei_comment(self,comment_text):
        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status(f"執行用戶貼文留言")
        #await asyncio.sleep(random.uniform(2, 4))
        try:
            # 定位留言输入框
            # 确保弹窗完全加载
            await self.page.wait_for_selector('div[role="dialog"]',
                                              state="visible",
                                              timeout=15000)

            # 使用更可靠的定位方式
            input_selector = 'div[role="dialog"] form textarea'
            await self.page.wait_for_selector(input_selector, state="attached", timeout=5000)
            print("留言内容：",comment_text)
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"留言内容：{comment_text}")
            #await asyncio.sleep(random.uniform(2, 4))
            # 使用页面级输入方法
            # await self.page.type(input_selector, comment_text, delay=random.randint(50, 150))
            await self.page.fill(input_selector, comment_text)
            # 等待发布按钮可点击
            await self.page.wait_for_function(
                """() => {
                    const buttons = document.querySelectorAll('div[role="dialog"] div[role="button"]');
                    for (const btn of buttons) {
                        const text = btn.innerText.trim();
                        if ((text === '发布' || text === '發佈') && 
                            btn.getAttribute('aria-disabled') !== 'true') {
                            return true;
                        }
                    }
                    return false;
                }""",
                timeout=20000
            )
            #await asyncio.sleep(random.uniform(2, 4))
            # 点击可用的发布按钮
            await self.page.evaluate("""() => {
                            const buttons = document.querySelectorAll('div[role="dialog"] div[role="button"]');
                            for (const btn of buttons) {
                                const text = btn.innerText.trim();
                                if ((text === '发布' || text === '發佈') && 
                                    btn.getAttribute('aria-disabled') !== 'true') {
                                    btn.click();
                                    return;
                                }
                            }
                        }""")
            print("成功留言")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"成功留言")
            await asyncio.sleep(random.uniform(4, 6))
        except Exception as e:
            print(f"帖子不允许留言{str(e)}")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"貼文不允許留言，跳過...")
            #await asyncio.sleep(random.uniform(2, 4))
            return False

    async def like_post(self, post_index):
        try:
            # 定位到帖子
            article_locator = f"article >> nth={post_index - 1}"
            await self.page.wait_for_selector(article_locator, timeout=30000)
            post = self.page.locator(article_locator)
            # await post.scroll_into_view_if_needed()
            # 使用JavaScript直接执行点击
            already_liked = await self.page.evaluate(f"""() => {{
                const articles = document.querySelectorAll('article');
                if (articles.length >= {post_index}) {{
                    const post = articles[{post_index - 1}];

                    // 检查是否已经点赞
                    const likedButtons = post.querySelectorAll('svg[aria-label="取消赞"], svg[aria-label="取消讚"], svg[aria-label="Unlike"]');
                    if (likedButtons.length > 0) {{
                        console.log("帖子已点赞，跳过");
                        return true; // 已经点赞
                    }}

                    // 查找点赞按钮
                    const likeButtons = post.querySelectorAll('div[role="button"], button');
                    for (const btn of likeButtons) {{
                        const svg = btn.querySelector('svg');
                        if (svg) {{
                            const label = svg.getAttribute('aria-label') || '';
                            if (label.includes('Like') || label.includes('赞') || label.includes('讚')) {{
                                if (!label.includes('取消赞') && !label.includes('取消讚') && !label.includes('Unlike')) {{
                                    btn.click();
                                    return false; // 成功点赞
                                }}
                            }}
                        }}
                    }}
                }}
                return true; // 未找到按钮或已点赞
            }}""")

            if already_liked:
                print(f"第 {post_index} 个帖子已点赞，跳过")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"貼文已點讚，跳過")
                await asyncio.sleep(random.uniform(4, 6))
            else:
                print(f"成功点赞第 {post_index} 个帖子")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"成功點讚貼文")
                await asyncio.sleep(random.uniform(4, 6))

        except Exception as e:
            print(f"点赞帖子失败: {str(e)}")

    async def comment_post(self, post_index, comment_text):
        """在帖子下留言"""
        try:
            # 定位到帖子
            article_locator = f"article >> nth={post_index - 1}"
            await self.page.wait_for_selector(article_locator, timeout=30000)
            # 使用JavaScript直接执行点击
            await self.page.evaluate(f"""() => {{
                            const articles = document.querySelectorAll('article');
                            if (articles.length >= {post_index}) {{
                                const post = articles[{post_index - 1}];

                                // 查找留言按钮
                                const likeButtons = post.querySelectorAll('div[role="button"], button');
                                for (const btn of likeButtons) {{
                                    const svg = btn.querySelector('svg');
                                    if (svg) {{
                                        const label = svg.getAttribute('aria-label') || '';
                                        if (label.includes('Comment') || label.includes('評論') || label.includes('评论') || label.includes('回應')) {{
                                            btn.click();
                                            return true;
                                        }}
                                    }}
                                }}
                            }}
                            return false;
                        }}""")
            await asyncio.sleep(random.uniform(5, 8))
            try:
                await self.page.wait_for_selector('div[role="dialog"]', timeout=10000)
            except:
                print(f"留言弹窗未打开，跳过第 {post_index} 个帖子")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"不可留言，跳過帖子")
                #await asyncio.sleep(random.uniform(2, 4))
                return
            try:
                # 定位留言输入框
                # 确保弹窗完全加载
                await self.page.wait_for_selector('div[role="dialog"]',
                                                  state="visible",
                                                  timeout=15000)

                # 使用更可靠的定位方式
                input_selector = 'div[role="dialog"] form textarea'
                await self.page.wait_for_selector(input_selector, state="attached", timeout=10000)
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"留言内容： {comment_text}")
                #await asyncio.sleep(random.uniform(2, 4))
                # 使用页面级输入方法
                # await self.page.type(input_selector, comment_text, delay=random.randint(50, 150))
                await self.page.fill(input_selector, comment_text)
                # 等待发布按钮可点击
                await self.page.wait_for_function(
                    """() => {
                        const buttons = document.querySelectorAll('div[role="dialog"] div[role="button"]');
                        for (const btn of buttons) {
                            const text = btn.innerText.trim();
                            if ((text === '发布' || text === '發佈') && 
                                btn.getAttribute('aria-disabled') !== 'true') {
                                return true;
                            }
                        }
                        return false;
                    }""",
                    timeout=20000
                )
                #await asyncio.sleep(random.uniform(2, 4))
                # 点击可用的发布按钮
                await self.page.evaluate("""() => {
                                            const buttons = document.querySelectorAll('div[role="dialog"] div[role="button"]');
                                            for (const btn of buttons) {
                                                const text = btn.innerText.trim();
                                                if ((text === '发布' || text === '發佈') && 
                                                    btn.getAttribute('aria-disabled') !== 'true') {
                                                    btn.click();
                                                    return;
                                                }
                                            }
                                        }""")
                print("成功留言")
                await asyncio.sleep(random.uniform(4, 6))
                await self.robust_update_status(f"成功留言")
                await asyncio.sleep(random.uniform(4, 6))
            except Exception as e:
                print(f"在第 {post_index} 个帖子不允许留言{str(e)}")
                #await asyncio.sleep(random.uniform(2, 4))
                await self.robust_update_status(f"貼文不允許留言，跳過...")
                #await asyncio.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"在第 {post_index} 个帖子留言失败: {str(e)}")
            #await asyncio.sleep(random.uniform(2, 4))
            await self.robust_update_status(f"貼文留言失敗，跳過...")
            #await asyncio.sleep(random.uniform(2, 4))
        finally:
            await asyncio.sleep(random.uniform(6, 8))
            print("关闭弹窗")
            # 关闭按钮代码
            await self.page.evaluate("""() => {
                // 方法1: 直接使用您提供的选择器
                const closeSvg = document.querySelector("body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.xo2ifbc.x10l6tqk.x1eu8d0j.x1vjfegm > div > div > svg");
                if (closeSvg) {
                    // 找到SVG元素后，向上查找可点击的父元素
                    let clickableElement = closeSvg;
                    while (clickableElement && !clickableElement.onclick && clickableElement !== document.body) {
                        clickableElement = clickableElement.parentElement;
                    }
                    if (clickableElement && clickableElement !== document.body) {
                        clickableElement.click();
                        return;
                    }
                }

                // 方法2: 通过aria-label查找关闭按钮
                const closeButtons = document.querySelectorAll('[aria-label="关闭"], [aria-label="關閉"], [aria-label="Close"]');
                for (const btn of closeButtons) {
                    btn.click();
                    return;
                }

                // 方法3: 查找所有可能的关闭按钮
                const allButtons = document.querySelectorAll('button, div[role="button"]');
                for (const btn of allButtons) {
                    const svg = btn.querySelector('svg');
                    if (svg) {
                        const label = svg.getAttribute('aria-label') || '';
                        if (label.includes('Close') || label.includes('关闭') || label.includes('關閉')) {
                            btn.click();
                            return;
                        }
                    }
                }

                // 如果没找到，尝试按ESC键关闭
                document.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Escape',
                    keyCode: 27,
                    which: 27,
                    bubbles: true
                }));
            }""")
            #await asyncio.sleep(random.uniform(2, 4))

    async def check_cookies_valid(self):
        """检查cookies是否有效"""
        try:
            ds_user_id = next((c for c in self.cookies if c['name'] == "ds_user_id"), None)
            sessionid = next((c for c in self.cookies if c['name'] == "sessionid"), None)
            return ds_user_id and sessionid and sessionid['expires'] > time.time()
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
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                executable_path=self.browser_path,
            ignore_default_args=[
                '--enable-automation',
                '--disable-popup-blocking'
            ]
            )
            page = await self.browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            await page.goto(url="https://www.instagram.com/accounts/login/", wait_until='load', timeout=50000)
            await asyncio.sleep(1)

            # 输入凭证
            await page.locator("form input").first.fill(self.username)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.locator("form input").nth(1).fill(self.password)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.click("form button[type='submit']")

            # 检查登录是否成功
            try:
                await page.wait_for_url("https://www.instagram.net/?login_success=true", timeout=60000)
                self.is_logged_in = True
            except:
                current_url = await page.evaluate("() => window.location.href")
                if "accounts/login" in page.url or "accounts/suspended" in page.url:
                    print(f"登录失败，当前URL: {current_url}")
                    self.is_logged_in = False
                    await self.browser.close()
                    raise Exception("登录失败，请检查用户名和密码")

            # 登录成功处理
            self.cookies = await page.context.cookies()
            with open("instagram.json", "w") as f:
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

    async def sleep_time(self, rest_time=60):
        """执行休息任务"""
        await self.report_task_status(f"正在執行倒計時...")
        #await asyncio.sleep(random.uniform(2, 4))
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

        #await asyncio.sleep(random.uniform(2, 4))
        await self.robust_update_status("休息結束，繼續執行任務...")
        #await asyncio.sleep(random.uniform(2, 4))

        # 隐藏倒计时显示
        if self.status_window:
            self.status_window.countdown_signal.emit(0)

    async def report_online_status(self):
        """异步上报在线状态"""
        try:
            url = f"http://aj.ry188.vip/API/UpDataState.aspx?Account={self.account}&DeviceNumber={self.device_number}&DeviceCode={self.machine_code}&IsPhone={self.is_phone}&RemoteId={self.remote_id}&RunText=在线"

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
            url = f"http://aj.ry188.vip/API/UpDataRunState.aspx?Account={self.account}&DeviceNumber={self.device_number}&RunText={task_name}&DeviceCode={self.machine_code}&IsPhone={self.is_phone}&RemoteId={self.remote_id}"

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

    # 获取请求Auth签名
    def getBearerAuth(self):
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        sessionid = next((cookie for cookie in self.cookies if cookie['name'] == "sessionid"), None)
        auth_str = "{\"ds_user_id\":\"" + ds_user_id['value'] + "\",\"sessionid\":\"" + sessionid['value'] + "\"}"
        auth_bytes = auth_str.encode('utf-8')
        auth_str = base64.b64encode(auth_bytes)
        return "Bearer IGT:2:" + auth_str.decode('utf-8')

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
    if not data["SendData"]["ConfigDatas"]["SendPicList"]:
        return None

    random_test = random.randint(0, len(data["SendData"]["ConfigDatas"]["SendPicList"]) - 1)
    url = data["SendData"]["ConfigDatas"]["SendPicList"][random_test]

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

def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    if type_data in ('true', 'True', 'TRUE'):
        return True
    elif type_data in ('false', 'False', 'FALSE'):
        return False

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