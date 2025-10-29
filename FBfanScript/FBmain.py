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
from FB_loginwin import win_main
from playwright.async_api import async_playwright


class Crawler:
    def __init__(self, cookies, data, users, start_position, content0, content1, task_order=None, rest_times=None, source_mapping=None):
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 25
        self.is_logged_in = False
        self.browser_path = get_chrome_path()
        # """全局设定"""
        self.IsSwitchBrowser = int(data["SendData"]["SendConfigs"]["SwitchBrowserInterval"])  # 浏览器跳转时间
        self.IsLike = int(data["SendData"]["SendConfigs"]["LikeType"])  # 点赞类型
        self.IsEnableFriendLike = parse_bool(data["SendData"]["SendConfigs"]["IsEnableFriendLike"])  # 是否点赞
        self.IsGroup = parse_bool(data["SendData"]["SendConfigs"]["IsGroup"])
        self.IsPages = parse_bool(data["SendData"]["SendConfigs"]["IsPages"])
        self.IsZanKe = parse_bool(data["SendData"]["SendConfigs"]["IsZanKe"])
        self.IsEnableMessager = parse_bool(data["SendData"]["SendConfigs"]["IsEnableMessager"])  # 是否发送私信
        self.IsMessagerCount = int(data["SendData"]["SendConfigs"]["MessagerCount"])  # 私信发送数量
        self.SendingInterval = int(data["SendData"]["SendConfigs"]["SendingInterval"])  # 私信发送间隔
        self.IsEnableKeywordSearch = parse_bool(data["SendData"]["SendConfigs"]["IsEnableKeywordSearch"])  # 是否发送关键字
        self.IsEnableKeys = data["SendData"]["SendConfigs"]["Keys"]  # 关键字
        self.IsEnableKeys_PostsCount = int(data["SendData"]["SendConfigs"]["PostsCount"])  # 发送关键字数量
        self.IsPosts = parse_bool(data["SendData"]["SendConfigs"]["IsPosts"])  # 是否FB贴文
        self.IsGroupPosts = parse_bool(data["SendData"]["SendConfigs"]["IsGroupPosts"])  # 是否FB社团贴文
        self.IskeyLike = parse_bool(data["SendData"]["SendConfigs"]["IskeyLike"])  # 是否关键字点赞
        self.IsKeyPosts = parse_bool(data["SendData"]["SendConfigs"]["IsKeyPosts"])  # 是否关键字留言
        self.IsPostsJinDu = parse_bool(data["SendData"]["SendConfigs"]["IsPostsJinDu"])  # 是否贴文进度
        self.IsLoop = parse_bool(data["SendData"]["SendConfigs"]["IsLoop"])  # 是否循环关键字
        # """社团"""
        self.IsGroupMem = parse_bool(data["SendData"]["SendConfigs"]["IsGroupMembersSendText"])  # 是否社团成员留言
        self.IsGroupMem_Messager = parse_bool(
            data["SendData"]["SendConfigs"]["IsGroupMembersSendMessager"])  # 是否社团成员发送私信
        self.IsGroup_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsAddGroupFriend"])  # 是否社团成员加好友
        self.IsGroup_FriendCount = int(data["SendData"]["SendConfigs"]["AddGroupFriendCount"])  # 社团成员加好友数量
        # """粉专"""
        self.IsPagesMem = parse_bool(data["SendData"]["SendConfigs"]["IsPagesMembersSendText"])  # 是否粉专成员留言
        self.IsPagesMem_Messager = parse_bool(
            data["SendData"]["SendConfigs"]["IsPagesMembersSendMessager"])  # 是否粉专成员发送私信
        self.IsPages_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsAddPagesFriend"])  # 是否粉专成员加好友
        self.IsPages_FriendCount = int(data["SendData"]["SendConfigs"]["AddPagesFriendCount"])  # 粉专粉专加好友数量
        # """赞客"""
        self.IsAdMem_l = parse_bool(data["SendData"]["SendConfigs"]["IsAdHomeLike"])  # 是否赞客成员点赞
        self.IsAdMem_t = int(data["SendData"]["SendConfigs"]["LikeType"])  # 是否赞客成员点赞类型
        self.IsAdMem = parse_bool(data["SendData"]["SendConfigs"]["IsAdMembersSendText"])  # 是否赞客成员留言
        self.IsAdMem_Messager = parse_bool(data["SendData"]["SendConfigs"]["IsAdMembersSendMessager"])  # 是否赞客成员发送私信
        self.IsAd_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsAddAdFriend"])  # 是否赞客成员加好友
        self.IsAd_FriendCount = int(data["SendData"]["SendConfigs"]["AddAdFriendCount"])  # 赞客成员加好友数量
        # """好友设定"""
        self.IsQuery_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsQueryFriend"])  # 是否搜寻好友
        self.IsQuery_Key = data["SendData"]["SendConfigs"]["QueryKey"]  # 搜寻关键字
        self.IsAdd_FriendCount = int(data["SendData"]["SendConfigs"]["AddFriendCount"])  # 邀请加好友数量
        self.IsInviteJoinGroup = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinGroup"])  # 是否社团邀请好友
        self.IsInviteJoinGroupUrl = str(data["SendData"]["SendConfigs"]["InviteJoinGroupUrl"]).split("\n")  # 是否社团邀请好友地址
        self.IsInviteJoinGroupFriendCount = int(
            data["SendData"]["SendConfigs"]["InviteJoinGroupFriendCount"])  # 邀请社团邀请好友数量
        self.IsIsInviteJoinPages = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinPages"])  # 是否粉丝邀请好友
        self.IsInviteJoinPagesUrl = str(data["SendData"]["SendConfigs"]["InviteJoinPagesUrl"]).split("\n")  # 是否粉丝邀请好友地址
        self.IsInvitePagesFriendCount = int(data["SendData"]["SendConfigs"]["InvitePagesFriendCount"])  # 邀请粉丝邀请好友数量
        # """留言私信"""
        self.message_pic = parse_bool(data["SendData"]["SendConfigs"]["IsSendPic"])  # 是否发送图片
        self.ImageAndTextSend = parse_bool(data["SendData"]["SendConfigs"]["IsImageAndTextSend"])  # 是否图片合并发送
        self.IsSendText = parse_bool(data["SendData"]["SendConfigs"]["IsSendText"])  # 是否发送文字
        self.leavetext_messags = str(data["SendData"]["SendText"]).split("\n\n\n")  # 留言内容
        self.leavetext_MsgText = str(data["SendData"]["MsgText"]).split("\n\n\n")  # 私信内容
        self.new_user_Tracking_num = 0
        self.new_user_Miss_num = 0
        self.new_fans_num = 0
        self.key_addFriendnum = 0
        self.pic_path = None
        self.init = data
        self.status_window = None  # 状态窗口引用
        self.UsersLists = users
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
        self.source_mapping = source_mapping or {}  # 用户ID到社团ID的映射

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
        # 程序开始时上报在线状态
        await self.report_online_status()

        # 设置定时器，每隔一段时间上报一次在线状态
        asyncio.create_task(self.periodic_online_report())

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
            self.browser = await playwright.chromium.launch(headless=False, args=browser_args,
                                                            executable_path=self.browser_path)
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

        await asyncio.sleep(1)
        function_map = {
            0: self.key_post_operate,
            1: self.key_addFriend,
            2: self.groups_JoinFriend,
            3: self.fans_JoinFriend,
            4: self.Usersmissing,
            5: self.sleep_time
        }
        if self.IsInviteJoinGroup :
            function_map[0] = self.key_post_operate # 是否社团邀请好友
        if self.IsIsInviteJoinPages :
            function_map[0] = self.key_groups_post # 是否粉丝邀请好友

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
        # await self.home_post() # FB首页留言
        # await self.Usersmissing()  # 用户个人主页留言
        # await self.key_addFriend() # 關鍵字加好友
        # await self.groups_JoinFriend() # 社團邀請好友
        # await self.fans_JoinFriend() # 粉轉邀請好友
        # await self.key_post_operate()#關鍵字貼文操作
        # await self.key_groups_post()#關鍵字社團貼文
        print("任务完成")
        await self.robust_update_status("全部任務完成...")

        await self.browser.close()

    async def execute_task_with_timeout(self, task_func, task_index, position, completion_time):
        """执行带超时控制的任务"""
        task_names = {
            0: "關鍵字任務",
            1: "搜尋添加好友",
            2: "社團邀請好友",
            3: "粉轉邀請好友",
            4: "用戶留言"
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
    async def like_post(self, index, like):
        """封装点赞功能"""
        await self.robust_update_status(f"開始執行點讚")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"執行點讚帖子"))
        alreadylike = '//div[@aria-label="讚" or @aria-label="赞"]'
        cancellike = '//div[contains(@aria-label, "取消") or contains(@aria-label, "移除")]'
        try:
            # selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div/div/div[{index}]//div[@aria-label="讚" or @aria-label="赞"]'
            # 点击留言按钮
            # selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div/div/div[{index}]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
            selector = like.format(index)
            selector = selector + alreadylike
            element = await self.page.wait_for_selector(selector, timeout=10000)

            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(2)
                await element.hover()
                await asyncio.sleep(3)

                target_emotion = self.IsLike - 1
                target_emotion_list = ["赞", "大心", "加油", "哈", "哇", "嗚", "怒"]
                emotion_selector = f'//div[@role="button" and @aria-label="{target_emotion_list[target_emotion]}"]'
                await self.robust_update_status(f"表情：{target_emotion_list[target_emotion]}")
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
                    await self.robust_update_status(f"點讚失敗普通點讚")
            return True
        except Exception as e:
            print(f"点赞失败: {str(e)}")
            try:
                like = like.format(index)
                element = await self.page.wait_for_selector(like + cancellike, timeout=10000)
                if element:
                    print("已經點過讃")
                    await self.robust_update_status(f"已經點讚過")
                return False
            except Exception as e:
                print(f"点赞失败找不到可點讚位置: {str(e)}")
                await self.robust_update_status(f"該貼文不可點讚")

    async def comment_post(self, index, comment_text, Posts, split_send=False):
        """封装留言功能"""
        await self.robust_update_status(f"開始執行留言")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"執行留言帖子"))
        try:
            # 点击留言按钮
            selector = Posts.format(index)
            element = await self.page.wait_for_selector(selector, timeout=10000)
        except Exception as e:
            print(f"留言失败: {str(e)}")
            await self.robust_update_status(f"該貼文不可留言")
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
                        # 下载图片（如果需要）
                        if self.message_pic and (not split_send or self.pic_path is None):
                            self.pic_path = await GetHtmlpic(self.init)
                            await asyncio.sleep(3)

                        # 发送文字部分
                        if self.IsSendText and comment_text:
                            await self.robust_update_status(f"留言內容：{comment_text}")
                            await asyncio.sleep(1)
                            await input_element.click()
                            await input_element.fill(comment_text)
                            await asyncio.sleep(2)

                            # 如果不需要分开发送，直接发送文字
                            if not split_send:
                                if self.message_pic and self.pic_path is not None:
                                    await self._upload_image()

                                # 提交留言
                                if await self._submit_comment():
                                    print(f"成功留言: {comment_text}")
                                    # return True
                            else:
                                # 先单独发送文字
                                if await self._submit_comment():
                                    print(f"成功发送文字: {comment_text}")
                                    await asyncio.sleep(random.randint(10, 14))

                                    # 重新打开评论框发送图片
                                    if self.message_pic and self.pic_path is not None:
                                        await self._reopen_comment_box()
                                        await asyncio.sleep(random.randint(10, 14))
                        else:
                            # 只发送图片的情况
                            if self.message_pic and self.pic_path is not None:
                                await self._upload_image()
                                if await self._submit_comment():
                                    print("成功发送图片")
                                    await asyncio.sleep(random.randint(10, 14))
                                    # return True
                        await self.robust_update_status(f"等待發送完成...")
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

    async def _upload_image(self):
        """上传图片"""
        try:
            # 使用文件选择器
            file_input = await self.page.query_selector(
                'div[role="dialog"] input[type="file"]'
            )
            if file_input:
                await asyncio.sleep(2)
                await file_input.set_input_files(self.pic_path)
                print(f"已上传图片: {self.pic_path}")
                await asyncio.sleep(2)  # 等待图片上传完成
                return True
        except Exception as e:
            print(f"上传图片失败: {str(e)}")
        return False

    async def _submit_comment(self):

        if self.message_pic and self.pic_path is not None:
            try:
                input_selector = '//div[@role="dialog"]//div[@aria-atomic="true" and @aria-live="polite" and @role="status" and contains(text(), "相片附加成功")]'
                await self.page.wait_for_selector(input_selector, timeout=10000)
                await self.robust_update_status(f"圖片加載完成...")
            except Exception as e:
                print(f"沒找到圖片：{e}")
                await self.robust_update_status(f"圖片未加載完成等待...")
                await asyncio.sleep(random.randint(6, 10))

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

    async def _upload_image_miss(self):
        """上传图片"""
        try:
            # 使用文件选择器
            file_input = await self.page.query_selector(
                'div[data-visualcompletion="ignore"] input[type="file"]'
            )
            if file_input:
                await asyncio.sleep(2)
                await file_input.set_input_files(self.pic_path)
                print(f"已上传图片: {self.pic_path}")
                await asyncio.sleep(2)  # 等待图片上传完成
                return True
        except Exception as e:
            print(f"上传图片失败: {str(e)}")
        return False

    async def _submit_comment_miss(self):
        """私信提交评论"""
        try:
            submit_selector = '//div[@data-visualcompletion="ignore"]//div[contains(@aria-label, "傳送") or contains(@aria-label, "发送")]'
            submit_button = await self.page.wait_for_selector(submit_selector, timeout=10000)
            if submit_button:
                await submit_button.scroll_into_view_if_needed()
                await asyncio.sleep(3)
                await submit_button.click()
                return True
        except Exception as e:
            print(f"提交评论失败: {str(e)}")
        return False

    async def _reopen_comment_box_miss(self):
        """重新打开评论框发送图片"""
        try:

            # 定位留言输入框
            input_selector = '//div[@data-visualcompletion="ignore"]//div[@role="textbox" and contains(@aria-label, "訊息") or @role="textbox" and contains(@aria-label, "发消息")]'
            input_element = await self.page.wait_for_selector(input_selector, timeout=10000)

            if input_element:
                # 上传图片
                if await self._upload_image_miss():
                    # 提交评论
                    if await self._submit_comment_miss():
                        print("成功发送图片")
                        return True
        except Exception as e:
            print(f"重新打开评论框失败: {str(e)}")
        return False

    async def _reopen_comment_box(self):
        """重新打开评论框发送图片"""
        try:

            # 定位留言输入框
            input_selector = '//div[@role="dialog"]//div[@role="textbox" and contains(@aria-label, "留言")]'
            input_element = await self.page.wait_for_selector(input_selector, timeout=10000)

            if input_element:
                # 上传图片
                if await self._upload_image():
                    # 提交评论
                    if await self._submit_comment():
                        print("成功发送图片")
                        return True
        except Exception as e:
            print(f"重新打开评论框失败: {str(e)}")
        return False

    async def add_friend(self):
        print("加好友")
        await self.robust_update_status(f"開始執行加好友")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行加好友"))
        try:
            base_selector = '//div[@class="xh8yej3"]//div[@role="button" and contains(@aria-label, "加為朋友") or @role="button" and contains(@aria-label, "加为好友")]'
            element = await self.page.wait_for_selector(base_selector, timeout=10000)
            text = await element.get_attribute('aria-label')
            print("获取的文本：", text)
            if text == "朋友" or "取消" in text:
                await asyncio.sleep(8)
                return False
            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await element.click()
                print(f"成功点击追踪")
                if await self.addFriend_up():  # 添加 await 和括號來調用方法
                    self.new_user_Tracking_num += 1
                    print(f"成功添加第 {self.new_user_Tracking_num} 個好友")
                    await self.robust_update_status(f"成功添加第{self.new_user_Tracking_num} 個好友")
                else:
                    await self.robust_update_status(f"不可添加好友")
            await asyncio.sleep(8)
            return True
        except Exception as e:
            print(f"使用完整路径选择器也失败: {str(e)}")
            return False

    async def miss_friend(self, comment_text, split_send=False):
        print("私信")
        await self.robust_update_status(f"開始執行發送私信")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行發送私信"))
        try:
            base_selector = '//div[@class="xh8yej3"]//div[@role="button" and contains(@aria-label, "發送訊息") or @role="button" and contains(@aria-label, "发消息")]'
            element = await self.page.wait_for_selector(base_selector, timeout=10000)
            await asyncio.sleep(8)
        except Exception as e:
            print(f"使用完整路径选择器也失败: {str(e)}")
            return False
        try:
            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await element.click()
                print(f"成功点击私信")
                miss_selector = '//div[@data-visualcompletion="ignore"]//div[@role="textbox" and contains(@aria-label, "訊息") or @role="textbox" and contains(@aria-label, "发消息")]'
                miss_input = await self.page.wait_for_selector(miss_selector, timeout=10000)
                if miss_input:
                    await miss_input.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await miss_input.click()
                    await asyncio.sleep(8)
                    # 下载图片（如果需要）
                    if self.message_pic and (not split_send or self.pic_path is None):
                        self.pic_path = await GetHtmlpic(self.init)
                        await asyncio.sleep(2)

                    # 发送文字部分
                    if self.IsSendText and comment_text:
                        await self.robust_update_status(f"發送私信內容 {comment_text}")
                        await asyncio.sleep(1)
                        await miss_input.click()
                        await miss_input.fill(comment_text)
                        await asyncio.sleep(2)

                        # 如果不需要分开发送，直接发送文字
                        if not split_send:
                            if self.message_pic and self.pic_path is not None:
                                await self._upload_image_miss()

                            # 提交留言
                            if await self._submit_comment_miss():
                                print(f"成功留言: {comment_text}")
                                return True
                        else:
                            # 先单独发送文字
                            if await self._submit_comment_miss():
                                print(f"成功发送文字: {comment_text}")
                                await asyncio.sleep(random.randint(8, 12))

                                # 重新打开评论框发送图片
                                if self.message_pic and self.pic_path is not None:
                                    await self._reopen_comment_box_miss()
                                    await asyncio.sleep(random.randint(8, 12))
                    else:
                        # 只发送图片的情况
                        if self.message_pic and self.pic_path is not None:
                            await self._upload_image_miss()
                            if await self._submit_comment_miss():
                                print("成功发送图片")
                                await asyncio.sleep(random.randint(8, 12))
                                return True
                self.new_user_Miss_num += 1
            await asyncio.sleep(8)
            return True
        except Exception as e:
            print(f"使用完整路径选择器也失败: {str(e)}")
            return False
        finally:
            close_selector = '//div[@data-visualcompletion="ignore"]//div[@role="button" and contains(@aria-label, "關閉聊天室")]'
            close_element = await self.page.wait_for_selector(close_selector, timeout=10000)
            if close_element:
                await close_element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await close_element.click()
                print(f"關閉聊天")
            await asyncio.sleep(self.SendingInterval)  # 倒計時

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
            page = await self.browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            await page.goto(url="https://www.facebook.com/login", wait_until='load', timeout=50000)

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
                await self.class_fb_set(page)
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

    async def Usersmissing(self):
        await self.robust_update_status(f"開始執行用戶個人主頁留言")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行個人主頁留言"))
        # 处理用户列表（从保存的位置开始）
        print(f"从位置 {self.Start_Position} 开始处理")
        for i in range(self.Start_Position, len(self.UsersLists)):
            user_id = self.UsersLists[i]

            # 获取对应的社团ID
            group_id = self.source_mapping.get(user_id, "未知")
            print(f"处理用户ID: {user_id}, 对应社团ID: {group_id}")

            # 可以上报状态时包含社团信息
            await self.robust_update_status(f"处理用户 {user_id}(社团:{group_id})")

            await self.page.goto(url="https://www.facebook.com/" + user_id, wait_until='load', timeout=50000)

            await asyncio.sleep(random.uniform(10.5, 13.5))
            try:
                # 交友邀请
                if self.IsGroup_Friend and self.new_user_Tracking_num < self.IsGroup_FriendCount and self.IsGroup or self.IsAd_Friend and self.new_user_Tracking_num < self.IsAd_FriendCount and self.IsZanKe:
                    if await self.add_friend():
                        print(f" {user_id} 加为好友成功")

                # 发送私信
                if self.IsEnableMessager and self.new_user_Miss_num < self.IsMessagerCount and self.IsGroupMem_Messager and self.IsGroup or self.IsEnableMessager and self.new_user_Miss_num < self.IsMessagerCount and self.IsPagesMem_Messager and self.IsPages or self.IsEnableMessager and self.new_user_Miss_num < self.IsMessagerCount and self.IsAdMem_Messager and self.IsZanKe:
                    comments = self.leavetext_MsgText
                    split_send = self.ImageAndTextSend
                    if await self.miss_friend(random.choice(comments), split_send):
                        print(f" {user_id} 发送私信成功")

                # 检测是否存在贴文
                Posts_selector = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="1"]'
                Posts_posted = await self.page.wait_for_selector(Posts_selector, timeout=10000)
                if Posts_posted:
                    await Posts_posted.scroll_into_view_if_needed()
                    print(f"存在帖文")
                    await self.robust_update_status(f"用戶個人主頁留言存在貼文")

                # 点赞
                if self.IsGroup and self.IsEnableFriendLike or self.IsPages and self.IsEnableFriendLike or self.IsZanKe and self.IsAdMem_l:
                    like = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]'
                    if await self.like_post(1, like):
                        print(f"第 {user_id} 个帖子点赞成功")

                # 留言
                if self.IsGroup and self.IsGroupMem or self.IsPages and self.IsPagesMem or self.IsZanKe and self.IsAdMem:
                    comments = self.leavetext_messags
                    Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                    split_send = self.ImageAndTextSend
                    if await self.comment_post(1, random.choice(comments), Posts, split_send):
                        print(f"第 {user_id} 个帖子留言成功")

                await asyncio.sleep(random.uniform(5, 10))

            except Exception as e:
                print(f"处理第 {i} 个帖子时出错: {str(e)}")
            # 更新进度
            current_position = i + 1
            save_progress(self.User_Id, self.UsersLists, current_position, self.source_mapping)
            await self.up_users_status(group_id)
            # 每处理一个用户等待
            await asyncio.sleep(self.IsSwitchBrowser)

        # 处理完成后清除进度
        clear_progress(self.User_Id)
        print("所有用户处理完成!")

    async def key_addFriend(self):
        print("添加好友")
        await self.robust_update_status(f"開始關鍵字添加好友")
        key = self.IsQuery_Key.split('#')
        for i in range(len(key)):
            await self.robust_update_status(f"關鍵字：{key}")
            await asyncio.sleep(2)
            asyncio.create_task(self.report_task_status(f"正在執行添加好友關鍵字：{key}"))
            await self.page.goto(url="https://www.facebook.com/search/people?q=" + key[i], wait_until='load', timeout=50000)
            await asyncio.sleep(10)
            k = 1
            try:
                while 1:
                    base_selector = '//div[@aria-label="搜尋結果" or @aria-label="搜索结果" ]//div[@role="feed"]/div[{}]'.format(
                        k)
                    element = await self.page.wait_for_selector(base_selector, timeout=10000)
                    await self.robust_update_status(f"當前選擇搜索列表好友第 {k} 個")
                    k += 1
                    if element:
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(3)
                        try:
                            if self.key_addFriendnum < self.IsAdd_FriendCount:
                                addbase_selector = base_selector + '//div[@role="button" and contains(@aria-label, "加朋友") or @role="button" and contains(@aria-label, "加好友")]'
                                add_element = await self.page.wait_for_selector(addbase_selector, timeout=5000)
                                text = await self.page.locator(addbase_selector).inner_text()
                                print("获取的文本：", text)
                                if add_element:
                                    await asyncio.sleep(1)
                                    await add_element.click()
                                    await asyncio.sleep(3)
                                    print(f"成功点击加好友")
                                    # 正確的調用方式：
                                    if await self.addFriend_up():  # 添加 await 和括號來調用方法
                                        self.key_addFriendnum += 1
                                        print(f"成功添加第 {self.key_addFriendnum}好友")
                                        await self.robust_update_status(f"成功添加第{self.key_addFriendnum} 個好友")
                                    else:
                                        await self.robust_update_status(f"不可添加好友")
                                await asyncio.sleep(8)
                            else:
                                break
                        except Exception as e:
                            print(f"不可加好友: {str(e)}")
                            await self.robust_update_status(f"不可添加好友")
                            continue
            except Exception as e:
                print(f"没有找到搜索結果: {str(e)}")
                return False

    async def addFriend_up(self):
        print("檢查是否成功添加好友")
        try:
            # 更精確的選擇器，只匹配純粹的關閉按鈕
            close_selectors = [
                '//div[@role="dialog"]//div[@role="button" and (@aria-label="關閉" or @aria-label="关闭")]',
                '//div[@role="dialog"]//div[@aria-label="關閉" and not(contains(@aria-label, "卡片"))]',
                '//div[@role="dialog"]//div[@aria-label="关闭" and not(contains(@aria-label, "卡片"))]'
            ]

            for selector in close_selectors:
                try:
                    close_but = await self.page.wait_for_selector(selector, timeout=3000)
                    if close_but:
                        print(f"找到關閉按鈕，點擊關閉")
                        await asyncio.sleep(1)
                        await close_but.click()
                        await asyncio.sleep(4)
                        return False  # 出現關閉按鈕，表示添加失敗
                except Exception as e:
                    continue  # 嘗試下一個選擇器
            print("沒有找到關閉按鈕或成功標誌，默認認為添加成功")
            return True

        except Exception as e:
            print(f"檢查過程中出錯: {str(e)}")
            # 如果出現異常，默認認為添加成功
            return True

    async def groups_JoinFriend(self):
        print("社團邀請好友")
        await self.robust_update_status(f"開始社團邀請好友")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行社團邀請好友"))
        for i in range(len(self.IsInviteJoinGroupUrl)):
            await self.page.goto(url=self.IsInviteJoinGroupUrl[i], wait_until='load', timeout=50000)
            print(self.IsInviteJoinGroupUrl[i])
            await asyncio.sleep(10)
            join_num = 0
            try:
                Option_selector = '//div[@aria-label="邀請" or @aria-label="邀请" ]'
                Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                if Option_but:
                    await Option_but.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await Option_but.click()
                    await asyncio.sleep(random.uniform(6, 8))

                    # 沒有邀請過的
                    # try:
                    #     Option_selector = '//div[@aria-label="邀請朋友加入這個社團" and @role="dialog" or @aria-label="邀请好友加入小组" and @role="dialog"]'
                    #     await self.page.wait_for_selector(Option_selector, timeout=10000)
                    #     try:
                    #         k = 1
                    #         while 1 :
                    #             JoinFriend_selector = Option_selector + '//div[@data-visualcompletion="ignore-dynamic"][{}]'.format(k)
                    #             JoinFriend_but = await self.page.wait_for_selector(JoinFriend_selector, timeout=5000)
                    #             k += 1
                    #             if JoinFriend_but:
                    #                 await Option_but.scroll_into_view_if_needed()
                    #                 if join_num < self.IsInviteJoinGroupFriendCount:
                    #                     await asyncio.sleep(1)
                    #                     await JoinFriend_but.click()
                    #                     join_num += 1
                    #                     print(f"選擇好友數:{join_num}")
                    #                 else:
                    #                     break
                    #     except Exception as e:
                    #         print(f"没有找到邀請的人員: {str(e)}")
                    #     # 好友數量可能達不到輸入量的情況 存在一個也邀請進入
                    #     try:
                    #         if join_num > 0:
                    #             addJoinFriend_selector = Option_selector + '//div[@aria-label="傳送邀請" or @aria-label="发送邀请"]'
                    #             addJoinFriend_but = await self.page.wait_for_selector(addJoinFriend_selector, timeout=5000)
                    #             if addJoinFriend_but:
                    #                 await Option_but.scroll_into_view_if_needed()
                    #                 await asyncio.sleep(1)
                    #                 await addJoinFriend_but.click()
                    #                 print(f"點擊邀請")
                    #                 await asyncio.sleep(random.uniform(3, 5))
                    #     except Exception as e:
                    #         print(f"没有找到邀請: {str(e)}")
                    # except Exception as e:
                    #     print(f"没有打開邀請: {str(e)}")

                    # 儅已經邀請過的跳過
                    try:
                        Option_selector = '//div[@aria-label="邀請朋友加入這個社團" and @role="dialog" or @aria-label="邀请好友加入小组" and @role="dialog"]'
                        await self.page.wait_for_selector(Option_selector, timeout=10000)
                        try:
                            k = 1
                            while 1:
                                JoinFriend_selector = Option_selector + '//div[@data-visualcompletion="ignore-dynamic"]/div[@aria-checked="false" and @tabindex="0"]'
                                JoinFriend_but = await self.page.wait_for_selector(JoinFriend_selector, timeout=5000)
                                k += 1
                                if JoinFriend_but:
                                    await Option_but.scroll_into_view_if_needed()
                                    if join_num < self.IsInviteJoinGroupFriendCount:
                                        await asyncio.sleep(1)
                                        await JoinFriend_but.click()
                                        join_num += 1
                                        print(f"選擇好友數:{join_num}")
                                        await self.robust_update_status(f"選擇好友數：{join_num}")
                                    else:
                                        break
                        except Exception as e:
                            print(f"没有找到可邀請的人員: {str(e)}")
                            await self.robust_update_status(f"沒有找到可邀請的好友")
                        # 好友數量可能達不到輸入量的情況 存在一個也邀請進入
                        try:
                            if join_num > 0:
                                addJoinFriend_selector = Option_selector + '//div[@aria-label="傳送邀請" or @aria-label="发送邀请"]'
                                addJoinFriend_but = await self.page.wait_for_selector(addJoinFriend_selector,
                                                                                      timeout=5000)
                                if addJoinFriend_but:
                                    await Option_but.scroll_into_view_if_needed()
                                    await asyncio.sleep(1)
                                    await addJoinFriend_but.click()
                                    print(f"點擊邀請")
                                    await asyncio.sleep(random.uniform(3, 5))
                        except Exception as e:
                            print(f"没有找到邀請: {str(e)}")
                    except Exception as e:
                        print(f"没有打開邀請: {str(e)}")
            except Exception as e:
                print(f"没有找到邀請: {str(e)}")
                try:
                    Option_selector = '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x2lah0s x193iq5w x1icxu4v x25sj25 x1yrsyyn x17upfok xdl72j9 x1iyjqo2 x1l90r2v x13a6bvl"]//div[@aria-label="加入社團" or @aria-label="加入小组"]'
                    Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                    if Option_but:
                        await Option_but.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await Option_but.click()
                        await asyncio.sleep(random.uniform(5, 8))
                except Exception as e:
                    print(f"没有找到加入社團,可能已經申請過: {str(e)}")

    async def fans_JoinFriend(self):
        print("粉轉邀請好友")
        await self.robust_update_status(f"開始粉轉邀請好友")
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行粉轉邀請好友"))
        print(self.IsInviteJoinPagesUrl)
        for i in range(len(self.IsInviteJoinPagesUrl)):
            await self.page.goto(url=self.IsInviteJoinPagesUrl[i], wait_until='load', timeout=50000)
            print(self.IsInviteJoinPagesUrl[i])
            await asyncio.sleep(10)
            join_fans_num = 0
            try:
                Option_selector = '//div[@aria-haspopup="menu" and contains(@aria-label, "選項") or @aria-haspopup="menu" and contains(@aria-label, "选项")]'
                Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                if Option_but:
                    await Option_but.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await Option_but.click()
                    await asyncio.sleep(random.uniform(6, 8))
                    try:
                        Option_selector = '//div[@role="menu" and (contains(@aria-label, "功能表") or @role="menu" and contains(@aria-label, "菜单"))]//span[contains(text(), "邀請朋友") or contains(text(), "邀请好友")]/..'
                        Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                        if Option_but:
                            await Option_but.scroll_into_view_if_needed()
                            await asyncio.sleep(1)
                            await Option_but.click()
                            await asyncio.sleep(random.uniform(6, 8))
                            try:
                                while 1:
                                    Option_selector = '//div[@aria-label="邀請朋友" and @role="dialog" or @aria-label="邀请好友" and @role="dialog"]//div[@aria-checked="false" and @role="checkbox"]'
                                    Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                                    if Option_but:
                                        await Option_but.scroll_into_view_if_needed()
                                        if join_fans_num < self.IsInvitePagesFriendCount:
                                            await asyncio.sleep(1)
                                            await Option_but.click()
                                            join_fans_num += 1
                                            print(f"選擇好友數:{join_fans_num}")
                                            await self.robust_update_status(
                                                f"選擇好友數：{join_fans_num}")
                                        else:
                                            break
                            except Exception as e:
                                print(f"没找到朋友: {str(e)}")
                                await self.robust_update_status(f"沒有找到可邀請的好友")
                            try:
                                if join_fans_num > 0:
                                    Option_selector = '//div[@aria-label="邀請朋友" and @role="dialog" or @aria-label="邀请好友" and @role="dialog"]//div[@aria-label="傳送邀請" and @role="button" and @tabindex="0" or @aria-label="发送邀请" and @role="button" and @tabindex="0"]'
                                    Option_but = await self.page.wait_for_selector(Option_selector, timeout=10000)
                                    if Option_but:
                                        await Option_but.scroll_into_view_if_needed()
                                        await asyncio.sleep(1)
                                        await Option_but.click()
                                        print(f"點擊傳送邀請")
                                        await asyncio.sleep(random.uniform(5, 8))
                            except Exception as e:
                                print(f"没找到傳送邀請: {str(e)}")
                    except Exception as e:
                        print(f"没找到邀請朋友选项: {str(e)}")
            except Exception as e:
                print(f"沒找到选项{str(e)}")

    async def key_post_operate(self):
        print("關鍵字fb貼文")
        await self.robust_update_status("執行關鍵字fb貼文")
        # 进度文件路径
        progress_file = f"{self.User_Id}_key_post_progress.json"
        # 如果启用进度保存且存在进度文件，则加载进度
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行關鍵字fb貼文"))
        if self.IsPostsJinDu and os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                current_key_index = progress_data.get("current_key_index", "")  # 上一次中斷的關鍵字
                current_key_indexall = progress_data.get("current_key_indexall", [])  # 上一次的全部關鍵字
                current_post_index = progress_data.get("current_post_index", 0)  # 上一次中斷的關鍵字貼文序號
                print(
                    f"加载进度: 上一次关键字 {current_key_index}, 帖子索引 {current_post_index}")
            except Exception as e:
                print(f"加载进度文件失败: {e}, 从头开始")
                current_key_index = ""
                current_key_indexall = []
                current_post_index = 0
        else:
            current_key_index = ""
            current_key_indexall = []
            current_post_index = 0

        key = self.IsEnableKeys.split('#')
        # 判断所有关键字是否都在current_key_indexall中
        all_keys_exist = True
        for k in key:
            if k not in current_key_indexall:
                all_keys_exist = False
                break

        print(f"关键字检查结果: 所有关键字都存在 = {all_keys_exist}")

        # 如果所有关键字都存在，可以跳过处理或者做其他操作
        if all_keys_exist and self.IsPostsJinDu and current_key_index != "" and current_post_index != 0:
            print("執行上一次关键字")
            IsLoopkey = 0
            Issuss = 0
            while IsLoopkey < 2:
                for i in range(len(key)):
                    print("關鍵字：", key[i])
                    print(Issuss, IsLoopkey)
                    if key[i] == current_key_index and Issuss == 0:
                        await self.robust_update_status(f"執行關鍵字:{key[i]}")
                        await self.page.goto(url="https://www.facebook.com/search/top?q=" + key[
                            i] + "&filters=eyJ0b3BfdGFiX3JlY2VudF9wb3N0czowIjoie1wibmFtZVwiOlwidG9wX3RhYl9yZWNlbnRfcG9zdHNcIixcImFyZ3NcIjpcIlwifSJ9", wait_until='load',
                                             timeout=50000)
                        await asyncio.sleep(10)
                        asyncio.create_task(self.report_task_status(f"執行fb貼文關鍵字:{key[i]}"))
                        key_post_num = 0
                        post = self.IsEnableKeys_PostsCount
                        k = 1
                        try:
                            while 1:
                                base_selector = '//div[@aria-label="搜尋結果" or @aria-label="搜索结果" ]//div[@role="feed"]/div[{}]'.format(
                                    k)
                                element = await self.page.wait_for_selector(base_selector, timeout=10000)
                                k += 1
                                if element:
                                    await element.scroll_into_view_if_needed()
                                    await asyncio.sleep(3)
                                    try:
                                        if self.IskeyLike and key_post_num < post or self.IsKeyPosts and key_post_num < post:
                                            print(f"第 {k - 1} 个帖子")
                                            await self.robust_update_status(f"當前第: {k - 1} 個帖子 ")
                                            await asyncio.sleep(2)
                                            asyncio.create_task(self.report_task_status(f"執行當前第: {k - 1} 個帖子"))
                                            if k >= current_post_index:
                                                if self.IskeyLike:
                                                    like = base_selector
                                                    if await self.like_post(1, like):
                                                        print(f"第 {k - 1} 个帖子点赞成功")
                                                        await self.robust_update_status(f"點讚第 {k - 1} 個帖子成功")
                                                if self.IsKeyPosts:
                                                    comments = self.leavetext_messags
                                                    Posts = base_selector + '//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                                                    split_send = self.ImageAndTextSend
                                                    if await self.comment_post(1, random.choice(comments), Posts,
                                                                               split_send):
                                                        print(f"第 {k - 1} 个帖子留言成功")
                                                        await self.robust_update_status(f"留言第 {k - 1} 個帖子成功")
                                                await asyncio.sleep(8)

                                                # 更新进度
                                                if self.IsPostsJinDu:
                                                    progress_data = {
                                                        "current_key_index": key[i],
                                                        "current_key_indexall": key,
                                                        "current_post_index": k,
                                                    }
                                                    with open(progress_file, 'w', encoding='utf-8') as f:
                                                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                                                    print(
                                                        f"进度已保存: 关键字 {key[i]}, 帖子 {k - 1}")
                                            key_post_num += 1
                                        else:
                                            break
                                    except Exception as e:
                                        print(f"沒有找到帖子: {str(e)}")
                                        continue
                        except Exception as e:
                            print(f"没有找到搜索結果: {str(e)}")
                            # return False
                    elif IsLoopkey == 1 or Issuss == 1:
                        await self.robust_update_status(f"執行關鍵字:{key[i]}")
                        await self.page.goto(url="https://www.facebook.com/search/top?q=" + key[
                            i] + "&filters=eyJ0b3BfdGFiX3JlY2VudF9wb3N0czowIjoie1wibmFtZVwiOlwidG9wX3RhYl9yZWNlbnRfcG9zdHNcIixcImFyZ3NcIjpcIlwifSJ9", wait_until='load',
                                             timeout=50000)
                        await asyncio.sleep(10)
                        asyncio.create_task(self.report_task_status(f"正在執行fb貼文關鍵字：{key[i]}"))
                        key_post_num = 0
                        post = self.IsEnableKeys_PostsCount
                        k = 1
                        try:
                            while 1:
                                base_selector = '//div[@aria-label="搜尋結果" or @aria-label="搜索结果" ]//div[@role="feed"]/div[{}]'.format(
                                    k)
                                element = await self.page.wait_for_selector(base_selector, timeout=10000)
                                k += 1
                                if element:
                                    await element.scroll_into_view_if_needed()
                                    await asyncio.sleep(3)
                                    try:
                                        if self.IskeyLike and key_post_num < post or self.IsKeyPosts and key_post_num < post:
                                            print(f"第 {k - 1} 个帖子")
                                            await self.robust_update_status(f"當前第: {k - 1}個帖子 ")
                                            if self.IskeyLike:
                                                like = base_selector
                                                if await self.like_post(1, like):
                                                    print(f"第 {k - 1} 个帖子点赞成功")
                                                    await self.robust_update_status(f"點讚第 {k - 1} 個帖子成功")
                                            if self.IsKeyPosts:
                                                comments = self.leavetext_messags
                                                Posts = base_selector + '//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                                                split_send = self.ImageAndTextSend
                                                if await self.comment_post(1, random.choice(comments), Posts,
                                                                           split_send):
                                                    print(f"第 {k - 1} 个帖子留言成功")
                                                    await self.robust_update_status(f"留言第 {k - 1} 個帖子成功")
                                            key_post_num += 1
                                            await asyncio.sleep(8)

                                            # 更新进度
                                            if self.IsPostsJinDu:
                                                progress_data = {
                                                    "current_key_index": key[i],
                                                    "current_key_indexall": key,
                                                    "current_post_index": k,
                                                }
                                                with open(progress_file, 'w', encoding='utf-8') as f:
                                                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
                                                print(
                                                    f"进度已保存: 关键字 {key[i]}, 帖子 {k - 1}")

                                        else:
                                            break
                                    except Exception as e:
                                        print(f"沒有找到帖子: {str(e)}")
                                        continue
                        except Exception as e:
                            print(f"没有找到搜索結果: {str(e)}")
                    Issuss = 1
                # 限制循環
                IsLoopkey += 2 if not self.IsLoop else 1
        else:
            IsLoopkey = 0
            while IsLoopkey < 2:
                for i in range(len(key)):
                    print("關鍵字：", key[i])
                    await self.robust_update_status(f"執行關鍵字:{key[i]}")
                    await self.page.goto(url="https://www.facebook.com/search/top?q=" + key[
                        i] + "&filters=eyJ0b3BfdGFiX3JlY2VudF9wb3N0czowIjoie1wibmFtZVwiOlwidG9wX3RhYl9yZWNlbnRfcG9zdHNcIixcImFyZ3NcIjpcIlwifSJ9", wait_until='load',
                                         timeout=50000)
                    await asyncio.sleep(10)
                    asyncio.create_task(self.report_task_status(f"正在執行fb貼文關鍵字：{key[i]}"))
                    key_post_num = 0
                    post = self.IsEnableKeys_PostsCount
                    k = 1
                    try:
                        while 1:
                            base_selector = '//div[@aria-label="搜尋結果" or @aria-label="搜索结果" ]//div[@role="feed"]/div[{}]'.format(
                                k)
                            element = await self.page.wait_for_selector(base_selector, timeout=10000)
                            k += 1
                            if element:
                                await element.scroll_into_view_if_needed()
                                await asyncio.sleep(3)
                                try:
                                    if self.IskeyLike and key_post_num < post or self.IsKeyPosts and key_post_num < post:
                                        print(f"第 {k - 1} 个帖子")
                                        await self.robust_update_status(f"當前第: {k - 1}個帖子 ")
                                        if self.IskeyLike:
                                            like = base_selector
                                            if await self.like_post(1, like):
                                                print(f"第 {k - 1} 个帖子点赞成功")
                                                await self.robust_update_status(f"點讚第 {k - 1} 個帖子成功")
                                        if self.IsKeyPosts:
                                            comments = self.leavetext_messags
                                            Posts = base_selector + '//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                                            split_send = self.ImageAndTextSend
                                            if await self.comment_post(1, random.choice(comments), Posts, split_send):
                                                print(f"第 {k - 1} 个帖子留言成功")
                                                await self.robust_update_status(f"留言第 {k - 1} 個帖子成功")
                                        key_post_num += 1
                                        await asyncio.sleep(8)

                                        # 更新进度
                                        if self.IsPostsJinDu:
                                            progress_data = {
                                                "current_key_index": key[i],
                                                "current_key_indexall": key,
                                                "current_post_index": k,
                                            }
                                            with open(progress_file, 'w', encoding='utf-8') as f:
                                                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                                            print(
                                                f"进度已保存: 关键字 {key[i]}, 帖子 {k - 1}")

                                    else:
                                        break
                                except Exception as e:
                                    print(f"沒有找到帖子: {str(e)}")
                                    continue
                    except Exception as e:
                        print(f"没有找到搜索結果: {str(e)}")
                        # return False
                # 限制循環
                IsLoopkey += 2 if not self.IsLoop else 1

        # 所有关键字处理完成，删除进度文件
        if self.IsPostsJinDu and os.path.exists(progress_file):
            os.remove(progress_file)
            print("所有关键字处理完成，已删除进度文件")

    async def key_groups_post(self):
        print("關鍵字社團貼文")
        await self.robust_update_status(f"執行關鍵字社團貼文")
        # 进度文件路径
        progress_file = f"{self.User_Id}_key_groups_progress.json"
        await asyncio.sleep(2)
        asyncio.create_task(self.report_task_status(f"正在執行關鍵字社團貼文"))
        # 如果启用进度保存且存在进度文件，则加载进度
        if self.IsPostsJinDu and os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                current_key_index = progress_data.get("current_key_index", 0)
                current_post_index = progress_data.get("current_post_index", 0)
                groups_postlist = progress_data.get("groups_postlist", [])
                loop_count = progress_data.get("loop_count", 0)  # 新增循环计数
                print(
                    f"加载进度: 关键字索引 {current_key_index}, 帖子索引 {current_post_index}, 已保存帖子数 {len(groups_postlist)}, 循环计数 {loop_count}")
            except Exception as e:
                print(f"加载进度文件失败: {e}, 从头开始")
                current_key_index = 0
                current_post_index = 0
                groups_postlist = []
                loop_count = 0
        else:
            current_key_index = 0
            current_post_index = 0
            groups_postlist = []
            loop_count = 0

        key = self.IsEnableKeys.split('#')

        # 如果从进度恢复且有未完成的帖子列表，先处理这些帖子
        if groups_postlist and current_post_index < len(groups_postlist):
            print(f"从进度继续: 处理第 {current_post_index + 1} 个帖子")
            await self.robust_update_status(f"從進度繼續貼文")
            for i in range(current_post_index, len(groups_postlist)):
                current_url = groups_postlist[i]
                print(f"正在处理链接: {current_url}")

                await self.page.goto(url=current_url, wait_until='load', timeout=50000)

                title = await self.page.title()
                if "Facebook" in title:
                    await asyncio.sleep(3)
                else:
                    print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                    await asyncio.sleep(10)

                if self.IskeyLike:
                    like = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]'
                    if await self.like_post(1, like):
                        print(f"第 {i + 1} 个帖子点赞成功")
                        await self.robust_update_status(f"第 {i+1} 個貼文點讚成功")
                if self.IsKeyPosts:
                    comments = self.leavetext_messags
                    Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                    split_send = self.ImageAndTextSend
                    if await self.comment_post(1, random.choice(comments), Posts, split_send):
                        print(f"第 {i + 1} 个帖子留言成功")
                        await self.robust_update_status(f"第 {i + 1} 個貼文留言成功")
                await asyncio.sleep(8)

                # 更新进度
                if self.IsPostsJinDu:
                    progress_data = {
                        "current_key_index": current_key_index,
                        "current_post_index": i + 1,
                        "groups_postlist": groups_postlist,
                        "loop_count": loop_count
                    }
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                    print(f"进度已保存: 关键字 {current_key_index + 1}, 帖子 {i + 1}/{len(groups_postlist)}")

            # 当前关键字的所有帖子处理完成
            print(f"关键字 {current_key_index + 1} 处理完成")
            current_key_index += 1
            current_post_index = 0
            groups_postlist = []

        # 主循环逻辑
        max_loops = 2 if self.IsLoop else 1  # 如果循环就执行2次，不循环就执行1次

        while loop_count < max_loops:
            print(f"\n=== 开始第 {loop_count + 1} 次执行 ===")

            # 处理所有关键字
            for key_index in range(current_key_index, len(key)):
                current_keyword = key[key_index]
                print(f"處理關鍵字 {key_index + 1}/{len(key)}: {current_keyword}")
                await self.robust_update_status(f"處理關鍵字：{current_keyword}")
                # 获取当前关键字的帖子列表
                current_groups_postlist = []
                await self.page.goto(
                    url="https://www.facebook.com/search/groups?q=" + current_keyword + "&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D", wait_until='load',
                    timeout=50000
                )

                title = await self.page.title()
                if "Facebook" in title:
                    await asyncio.sleep(3)
                else:
                    print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                    await asyncio.sleep(10)

                post = self.IsEnableKeys_PostsCount
                k = 1

                try:
                    while k <= post:
                        base_selector = f'//div[@aria-label="搜尋結果" or @aria-label="搜索结果"]//div[@role="feed"]/div[{k}]'
                        try:
                            element = await self.page.wait_for_selector(base_selector, timeout=10000)
                            k += 1
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(3)

                            link_locator_before = await element.query_selector('a[href*="/groups/"]')
                            if not link_locator_before:
                                print("未找到帖子链接，跳过该帖子")
                                continue

                            post_url_before = await link_locator_before.get_attribute('href')
                            current_groups_postlist.append(post_url_before)
                            print(f"找到帖子 {len(current_groups_postlist)}: {post_url_before}")

                        except Exception as e:
                            print(f"处理第 {k} 个元素时出错: {str(e)}")
                            k += 1
                            continue

                except Exception as e:
                    print(f"没有找到搜索結果: {str(e)}")
                    continue

                # 处理当前关键字的帖子
                for post_index in range(len(current_groups_postlist)):
                    current_url = current_groups_postlist[post_index]
                    print(f"正在处理第 {post_index + 1}/{len(current_groups_postlist)} 个帖子: {current_url}")

                    await self.page.goto(url=current_url, wait_until='load', timeout=50000)

                    title = await self.page.title()
                    if "Facebook" in title:
                        await asyncio.sleep(3)
                    else:
                        print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
                        await asyncio.sleep(10)

                    if self.IskeyLike:
                        like = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]'
                        if await self.like_post(1, like):
                            print(f"第 {post_index + 1} 个帖子点赞成功")
                            await self.robust_update_status(f"第 {post_index + 1} 個貼文點讚成功")
                    if self.IsKeyPosts:
                        comments = self.leavetext_messags
                        Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                        split_send = self.ImageAndTextSend
                        if await self.comment_post(1, random.choice(comments), Posts, split_send):
                            print(f"第 {post_index + 1} 个帖子留言成功")
                            await self.robust_update_status(f"第 {post_index + 1} 個貼文留言成功")
                    await asyncio.sleep(8)

                    # 更新进度
                    if self.IsPostsJinDu:
                        progress_data = {
                            "current_key_index": key_index,
                            "current_post_index": post_index + 1,
                            "groups_postlist": current_groups_postlist,
                            "loop_count": loop_count
                        }
                        with open(progress_file, 'w', encoding='utf-8') as f:
                            json.dump(progress_data, f, ensure_ascii=False, indent=2)
                        print(
                            f"进度已保存: 关键字 {key_index + 1}, 帖子 {post_index + 1}/{len(current_groups_postlist)}")

                print(f"关键字 {key_index + 1} 处理完成")

            # 一轮执行完成
            loop_count += 1

            # 如果循环且还有下一次执行，重置索引从头开始
            if self.IsLoop and loop_count < max_loops:
                current_key_index = 0
                current_post_index = 0
                groups_postlist = []

                # 更新进度，准备下一次执行
                if self.IsPostsJinDu:
                    progress_data = {
                        "current_key_index": 0,
                        "current_post_index": 0,
                        "groups_postlist": [],
                        "loop_count": loop_count
                    }
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                    print(f"准备第 {loop_count + 1} 次执行")

        # 所有处理完成，删除进度文件
        if self.IsPostsJinDu and os.path.exists(progress_file):
            os.remove(progress_file)
            print("所有关键字处理完成，已删除进度文件")

    async def home_post(self):
        await self.page.goto(url="https://www.facebook.com/", wait_until='load', timeout=50000)
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
                            # 找到再次点击才能激活下面查找
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

    async def class_fb_set(self,page):
        try:
            Option_selector = '//div[@data-visualcompletion="ignore-dynamic"]//div[@role="button" and contains(@aria-label, "選項")]'
            Option_but = await page.wait_for_selector(Option_selector, timeout=10000)
            if Option_but:
                await Option_but.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await Option_but.click()
                await asyncio.sleep(random.uniform(5, 8))
                disabled_selector = '//div[@aria-label="聊天室設定"]//div[@aria-checked="true" and contains(@aria-label, "彈出新訊息")]'
                disabled_but = await page.wait_for_selector(disabled_selector, timeout=10000)
                if disabled_but:
                    await disabled_but.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await disabled_but.click()
                    await asyncio.sleep(random.uniform(5, 8))
                await Option_but.click()
        except Exception as e:
            print(f"没有找到: {str(e)}")

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

    async def up_users_status(self, user_statusid):
        """异步上报用户状态"""
        try:
            url = f"http://cj.ry188.vip/API/SendCount.aspx?Account={self.account}&DeviceName={self.device_number}&UpDataNumber=1&eqtype=1&id={user_statusid}"

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"人数增加上报: {response.status}")
                    return True
        except asyncio.TimeoutError:
            print("人数增加上报超时")
            return False
        except Exception as e:
            print(f"人数增加上报失败: {e}")
            return False

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


def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')


def save_progress(account, users, position, source_mapping=None):
    """保存当前处理进度到文件"""
    progress_data = {
        "users": users,
        "position": position,
        "source_mapping": source_mapping or {}  # 保存映射关系
    }
    filename = f"{account}_progress.json"
    with open(filename, 'w') as f:
        json.dump(progress_data, f)
    print(f"保存进度到 {filename}: 位置 {position}/{len(users)}")


def load_progress(account):
    """从文件加载处理进度"""
    filename = f"{account}_progress.json"
    if not os.path.exists(filename):
        print(f"无进度文件 {filename}")
        return None, 0, {}

    try:
        with open(filename, 'r') as f:
            progress_data = json.load(f)
        print(f"从 {filename} 加载进度: 位置 {progress_data['position']}/{len(progress_data['users'])}")

        # 加载 source_mapping，如果不存在则返回空字典
        source_mapping = progress_data.get("source_mapping", {})
        return progress_data["users"], progress_data["position"], source_mapping
    except:
        print(f"加载进度文件 {filename} 失败")
        return None, 0, {}

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
