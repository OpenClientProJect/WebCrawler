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
    def __init__(self, cookies,data,users,start_position,content1):
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
        self.IsGroupMem = parse_bool(data["SendData"]["SendConfigs"]["IsGroupMembersSendText"])#是否社团成员留言
        self.IsGroupMem_Messager = parse_bool(data["SendData"]["SendConfigs"]["IsGroupMembersSendMessager"])#是否社团成员发送私信
        self.IsGroup_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsAddGroupFriend"])  # 是否社团成员加好友
        self.IsGroup_FriendCount = int(data["SendData"]["SendConfigs"]["AddGroupFriendCount"]) #社团成员加好友数量
        # """粉专"""
        self.IsPagesMem = parse_bool(data["SendData"]["SendConfigs"]["IsPagesMembersSendText"])  # 是否粉专成员留言
        self.IsPagesMem_Messager = parse_bool( data["SendData"]["SendConfigs"]["IsPagesMembersSendMessager"])  # 是否粉专成员发送私信
        self.IsPages_Friend = parse_bool(data["SendData"]["SendConfigs"]["IsAddPagesFriend"])  # 是否粉专成员加好友
        self.IsPages_FriendCount = int(data["SendData"]["SendConfigs"]["AddPagesFriendCount"])  # 粉专粉专加好友数量
        # """赞客"""
        self.IsAdMem = parse_bool(data["SendData"]["SendConfigs"]["IsAdHomeLike"])  # 是否赞客成员点赞
        self.IsAdMem = int(data["SendData"]["SendConfigs"]["LikeType"])  # 是否赞客成员点赞类型
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
        self.IsInviteJoinGroupFriendCount = int(data["SendData"]["SendConfigs"]["InviteJoinGroupFriendCount"])  # 邀请社团邀请好友数量
        self.IsIsInviteJoinPages = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinPages"])  # 是否粉丝邀请好友
        self.IsInviteJoinPagesUrl = str(data["SendData"]["SendConfigs"]["InviteJoinPagesUrl"]).split("\n")  # 是否粉丝邀请好友地址
        self.IsInvitePagesFriendCount = int(data["SendData"]["SendConfigs"]["InvitePagesFriendCount"])  # 邀请粉丝邀请好友数量
        # """留言私信"""
        self.message_pic = parse_bool(data["SendData"]["SendConfigs"]["IsSendPic"])#是否发送图片
        self.ImageAndTextSend = parse_bool(data["SendData"]["SendConfigs"]["IsImageAndTextSend"])#是否图片合并发送
        self.IsSendText = parse_bool(data["SendData"]["SendConfigs"]["IsSendText"])#是否发送文字
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
        # await self.Usersmissing()  # 用户个人主页留言
        # await self.key_addFriend() # 關鍵字加好友
        # await self.groups_JoinFriend() # 社團邀請好友
        # await self.fans_JoinFriend() # 粉轉邀請好友
        # await self.key_post_operate()#關鍵字貼文操作
        await self.key_groups_post()#關鍵字社團貼文
        # await self.csgetusers()
        print("任务完成")

    async def like_post(self, index,like):
        """封装点赞功能"""
        alreadylike = '//div[@aria-label="讚" or @aria-label="赞"]'
        cancellike = '//div[contains(@aria-label, "取消") or contains(@aria-label, "移除")]'
        try:
            # selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div/div/div[{index}]//div[@aria-label="讚" or @aria-label="赞"]'
            # 点击留言按钮
            # selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div/div/div[{index}]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
            selector = like.format(index)
            selector = selector+alreadylike
            element = await self.page.wait_for_selector(selector, timeout=10000)

            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await element.hover()
                await asyncio.sleep(2)

                target_emotion = self.IsLike - 1
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
                like = like.format(index)
                element = await self.page.wait_for_selector(like+cancellike, timeout=10000)
                if element:
                    print("已經點過讃")
                return False
            except Exception as e:
                print(f"点赞失败找不到可點讚位置: {str(e)}")

    async def comment_post(self, index, comment_text, Posts, split_send=False):
        """封装留言功能"""
        try:
            # 点击留言按钮
            selector = Posts.format(index)
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
                            '//div[@role="dialog"]//div[@aria-label="關閉"]' , # 方式1
                            '//div[@aria-label="關閉" and @aria-hidden="false"]'# 方式2
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
                            await asyncio.sleep(2)

                        # 发送文字部分
                        if self.IsSendText and comment_text:
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
                                    return True
                            else:
                                # 先单独发送文字
                                if await self._submit_comment():
                                    print(f"成功发送文字: {comment_text}")
                                    await asyncio.sleep(random.randint(8, 12))

                                    # 重新打开评论框发送图片
                                    if self.message_pic and self.pic_path is not None:
                                        await self._reopen_comment_box()
                                        await asyncio.sleep(random.randint(8, 12))
                        else:
                            # 只发送图片的情况
                            if self.message_pic and self.pic_path is not None:
                                await self._upload_image()
                                if await self._submit_comment():
                                    print("成功发送图片")
                                    await asyncio.sleep(random.randint(8, 12))
                                    return True
                        close_selectors = [
                            '//div[@aria-label="關閉" and @aria-hidden="false"]',  # 方式1
                            '//div[@role="dialog"]//div[@aria-label="關閉"]' # 方式2
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
        """提交评论"""
        try:
            submit_selector = '//div[@role="dialog"]//div[@id="focused-state-composer-submit"]'
            submit_button = await self.page.wait_for_selector(submit_selector, timeout=10000)
            if submit_button:
                await submit_button.scroll_into_view_if_needed()
                await asyncio.sleep(3)
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
                self.new_user_Tracking_num += 1
            await asyncio.sleep(8)
            return True
        except Exception as e:
            print(f"使用完整路径选择器也失败: {str(e)}")
            return False

    async def miss_friend(self,comment_text,split_send=False):
        print("私信")
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
            await asyncio.sleep(self.SendingInterval)#倒計時

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

    async def Usersmissing(self):
        # 处理用户列表（从保存的位置开始）
        print(f"从位置 {self.Start_Position} 开始处理")
        for i in range(self.Start_Position, len(self.UsersLists)):
            user_id = self.UsersLists[i]
            print("处理用户ID:", user_id)

            await self.page.goto(url="https://www.facebook.com/"+user_id, wait_until='load')

            await asyncio.sleep(random.uniform(10.5, 13.5))
            try:
                # 交友邀请
                if self.IsGroup_Friend and self.new_user_Tracking_num < self.IsGroup_FriendCount:
                    if await self.add_friend():
                        print(f" {user_id} 加为好友成功")

                # 发送私信
                if self.IsEnableMessager and self.new_user_Miss_num < self.IsMessagerCount or self.IsGroupMem_Messager and self.new_user_Miss_num < self.IsMessagerCount:
                    comments = self.leavetext_MsgText
                    split_send = self.ImageAndTextSend
                    if await self.miss_friend(random.choice(comments),split_send):
                        print(f" {user_id} 发送私信成功")

                #检测是否存在贴文
                Posts_selector = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="1"]'
                Posts_posted = await self.page.wait_for_selector(Posts_selector, timeout=10000)
                if Posts_posted:
                    await Posts_posted.scroll_into_view_if_needed()
                    print(f"存在帖文")

                # 点赞
                if self.IsEnableFriendLike:
                    like = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]'
                    if await self.like_post(1,like):
                        print(f"第 {user_id} 个帖子点赞成功")

                # 留言
                if self.IsGroupMem:
                    comments = self.leavetext_messags
                    Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                    split_send = self.ImageAndTextSend
                    if await self.comment_post(1, random.choice(comments),Posts,split_send):
                        print(f"第 {user_id} 个帖子留言成功")

                await asyncio.sleep(random.uniform(5, 10))

            except Exception as e:
                print(f"处理第 {i} 个帖子时出错: {str(e)}")
            # 更新进度
            current_position = i + 1
            save_progress(self.User_Id, self.UsersLists, current_position)

            # 每处理一个用户等待3秒
            await asyncio.sleep(3)

        # 处理完成后清除进度
        clear_progress(self.User_Id)
        print("所有用户处理完成!")

    async def key_addFriend(self):
        print("添加好友")
        key = self.IsQuery_Key.split('#')
        for i in range(len(key)):
            await self.page.goto(url="https://www.facebook.com/search/people?q="+key[i], wait_until='load')
            await asyncio.sleep(10)
            k = 1
            try:
                while 1:
                    base_selector = '//div[@aria-label="搜尋結果" or @aria-label="搜索结果" ]//div[@role="feed"]/div[{}]'.format(k)
                    element = await self.page.wait_for_selector(base_selector, timeout=10000)
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
                                    print(f"成功点击加好友")
                                    self.key_addFriendnum += 1
                                    print(f"成功添加第 {self.key_addFriendnum}好友")
                                await asyncio.sleep(8)
                            else:
                                break
                        except Exception as e:
                            print(f"不可加好友: {str(e)}")
                            continue
            except Exception as e:
                print(f"没有找到搜索結果: {str(e)}")
                return False

    async def groups_JoinFriend(self):
        print("社團邀請好友")
        for i in range(len(self.IsInviteJoinGroupUrl)):
            await self.page.goto(url=self.IsInviteJoinGroupUrl[i], wait_until='load')
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

                    #沒有邀請過的
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

                    #儅已經邀請過的跳過
                    try:
                        Option_selector = '//div[@aria-label="邀請朋友加入這個社團" and @role="dialog" or @aria-label="邀请好友加入小组" and @role="dialog"]'
                        await self.page.wait_for_selector(Option_selector, timeout=10000)
                        try:
                            k = 1
                            while 1 :
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
                                    else:
                                        break
                        except Exception as e:
                            print(f"没有找到可邀請的人員: {str(e)}")
                        # 好友數量可能達不到輸入量的情況 存在一個也邀請進入
                        try:
                            if join_num > 0:
                                addJoinFriend_selector = Option_selector + '//div[@aria-label="傳送邀請" or @aria-label="发送邀请"]'
                                addJoinFriend_but = await self.page.wait_for_selector(addJoinFriend_selector, timeout=5000)
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
        print(self.IsInviteJoinPagesUrl)
        for i in range(len(self.IsInviteJoinPagesUrl)):
            await self.page.goto(url=self.IsInviteJoinPagesUrl[i], wait_until='load')
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
                                        else:
                                            break
                            except Exception as e:
                                print(f"没找到朋友: {str(e)}")
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
        key = self.IsEnableKeys.split('#')
        IsLoopkey = 0
        while IsLoopkey < 2:
            for i in range(len(key)):
                print("關鍵字：",key[i])
                await self.page.goto(url="https://www.facebook.com/search/top?q=" + key[i], wait_until='load')
                await asyncio.sleep(10)
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
                                if self.IskeyLike and key_post_num < post or self.IsKeyPosts and key_post_num:
                                    print(f"第 {k - 1} 个帖子")
                                    if self.IskeyLike :
                                        like = base_selector
                                        if await self.like_post(1, like):
                                            print(f"第 {k - 1} 个帖子点赞成功")
                                    if self.IsKeyPosts:
                                        comments = self.leavetext_messags
                                        Posts = base_selector + '//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                                        split_send = self.ImageAndTextSend
                                        if await self.comment_post(1, random.choice(comments), Posts, split_send):
                                            print(f"第 {k - 1} 个帖子留言成功")
                                    key_post_num += 1
                                    await asyncio.sleep(8)
                                else:
                                    break
                            except Exception as e:
                                print(f"沒有找到帖子: {str(e)}")
                                continue
                except Exception as e:
                    print(f"没有找到搜索結果: {str(e)}")
                    return False
            # 限制循環
            IsLoopkey += 2 if not self.IsLoop else 1

    async def key_groups_post(self):
        print("關鍵字社團貼文")

        # 进度文件路径
        progress_file = f"{self.User_Id}_key_groups_progress.json"

        # 如果启用进度保存且存在进度文件，则加载进度
        if self.IsPostsJinDu and os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                current_key_index = progress_data.get("current_key_index", 0)
                current_post_index = progress_data.get("current_post_index", 0)
                groups_postlist = progress_data.get("groups_postlist", [])
                print(
                    f"加载进度: 关键字索引 {current_key_index}, 帖子索引 {current_post_index}, 已保存帖子数 {len(groups_postlist)}")
            except Exception as e:
                print(f"加载进度文件失败: {e}, 从头开始")
                current_key_index = 0
                current_post_index = 0
                groups_postlist = []
        else:
            current_key_index = 0
            current_post_index = 0
            groups_postlist = []

        key = self.IsEnableKeys.split('#')
        IsLoopkey = 0

        # 如果从进度恢复，直接处理已保存的帖子列表
        if groups_postlist and current_post_index < len(groups_postlist):
            print(f"从进度继续: 处理第 {current_post_index + 1} 个帖子")

            for i in range(current_post_index, len(groups_postlist)):
                current_url = groups_postlist[i]
                print(f"正在处理链接: {current_url}")

                await self.page.goto(url=current_url, wait_until='load')

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

                if self.IsKeyPosts:
                    comments = self.leavetext_messags
                    Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                    split_send = self.ImageAndTextSend
                    if await self.comment_post(1, random.choice(comments), Posts, split_send):
                        print(f"第 {i + 1} 个帖子留言成功")

                await asyncio.sleep(8)

                # 更新进度
                if self.IsPostsJinDu:
                    progress_data = {
                        "current_key_index": current_key_index,
                        "current_post_index": i + 1,
                        "groups_postlist": groups_postlist
                    }
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                    print(f"进度已保存: 关键字 {current_key_index + 1}, 帖子 {i + 1}/{len(groups_postlist)}")

            # 当前关键字的所有帖子处理完成，移动到下一个关键字
            current_key_index += 1
            current_post_index = 0
            groups_postlist = []

            # 保存进度（准备处理下一个关键字）
            if self.IsPostsJinDu:
                progress_data = {
                    "current_key_index": current_key_index,
                    "current_post_index": current_post_index,
                    "groups_postlist": groups_postlist
                }
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)

        # 处理剩余的关键字
        while IsLoopkey < 2 and current_key_index < len(key):
            current_keyword = key[current_key_index]
            print(f"處理關鍵字 {current_key_index + 1}/{len(key)}: {current_keyword}")

            # 获取当前关键字的帖子列表
            current_groups_postlist = []
            await self.page.goto(
                url="https://www.facebook.com/search/groups?q=" + current_keyword + "&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D",
                wait_until='load'
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
                current_key_index += 1
                continue

            # 处理当前关键字的帖子
            for i in range(len(current_groups_postlist)):
                current_url = current_groups_postlist[i]
                print(f"正在处理第 {i + 1}/{len(current_groups_postlist)} 个帖子: {current_url}")

                await self.page.goto(url=current_url, wait_until='load')

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

                if self.IsKeyPosts:
                    comments = self.leavetext_messags
                    Posts = '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]/div/div/div/div[@aria-posinset="{}"]//div[contains(@aria-label, "发表评论") or contains(@aria-label, "留言")]'
                    split_send = self.ImageAndTextSend
                    if await self.comment_post(1, random.choice(comments), Posts, split_send):
                        print(f"第 {i + 1} 个帖子留言成功")

                await asyncio.sleep(8)

                # 更新进度
                if self.IsPostsJinDu:
                    progress_data = {
                        "current_key_index": current_key_index,
                        "current_post_index": i + 1,
                        "groups_postlist": current_groups_postlist
                    }
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                    print(f"进度已保存: 关键字 {current_key_index + 1}, 帖子 {i + 1}/{len(current_groups_postlist)}")

            current_key_index += 1

            # 保存进度（准备处理下一个关键字）
            if self.IsPostsJinDu and current_key_index < len(key):
                progress_data = {
                    "current_key_index": current_key_index,
                    "current_post_index": 0,
                    "groups_postlist": []
                }
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
                print(f"准备处理下一个关键字: {current_key_index + 1}/{len(key)}")

            # 限制循環
            IsLoopkey += 2 if not self.IsLoop else 1

        # 所有关键字处理完成，删除进度文件
        if self.IsPostsJinDu and os.path.exists(progress_file):
            os.remove(progress_file)
            print("所有关键字处理完成，已删除进度文件")

    async def csgetusers(self):
        await self.page.goto(
            url="https://www.facebook.com/groups/271444413891893/members",
            wait_until='load'
        )
        await asyncio.sleep(5)

        # 滚动加载更多用户
        previous_count = 0
        current_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 10

        while scroll_attempts < max_scroll_attempts:
            # 滚动到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

            # 获取当前用户数量
            user_links = await self.page.query_selector_all(
                '//div[@role="list"]//a[contains(@href, "/user/") or contains(@href, "facebook.com/")]')
            current_count = len(user_links)

            print(f"滚动后用户数量: {current_count}")

            if current_count == previous_count:
                scroll_attempts += 1
                print(f"用户数量未增加，尝试次数: {scroll_attempts}/{max_scroll_attempts}")
            else:
                scroll_attempts = 0

            previous_count = current_count

            if scroll_attempts >= 3:  # 连续3次没有新用户就停止
                print("已加载所有用户")
                break

        # 获取最终的用户列表
        return await self._extract_user_links()

    async def _extract_user_links(self):
        """提取用户链接的辅助方法"""
        user_links = await self.page.query_selector_all(
            '//div[@role="list"]//a[contains(@href, "/user/") or contains(@href, "facebook.com/")]')

        users = []
        for i, link in enumerate(user_links):
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text()

                if href and text.strip():
                    users.append({
                        'index': i + 1,
                        'name': text.strip(),
                        'profile_url': href,
                        'user_id': href.split('/')[-1].split('?')[0] if '/' in href else href
                    })
            except Exception as e:
                print(f"提取第 {i + 1} 个用户信息时出错: {str(e)}")
                continue

        return users

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