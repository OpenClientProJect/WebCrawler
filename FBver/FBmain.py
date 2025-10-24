import asyncio
import random
import time
import json
import base64
import platform
import os
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
    def __init__(self, cookies,data,content1):
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
        parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsEnableHomeLike"])#是否启用页首
        int(data["AppConfigData"]["FanPagesConfig"]["EveryFanPagesInterval"])#每个粉丝专页间隔
        int(data["AppConfigData"]["FanPagesConfig"]["EveryIntervalHowManyFanPages"])#每间隔多少条
        int(data["AppConfigData"]["FanPagesConfig"]["FanPagesRestInterval"])#粉丝专页休息间隔
        parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsEnablePush"])#是否启用推文
        int(data["AppConfigData"]["FanPagesConfig"]["LikeType"])#點讚
        int(data["AppConfigData"]["FanPagesConfig"]["EachTimeInterval"])#每条时间间隔
        int(data["AppConfigData"]["FanPagesConfig"]["EveryIntervalHowManyFanPages2"])#每间隔多少条
        int(data["AppConfigData"]["FanPagesConfig"]["RestTimeInterval"])#休息时间间隔
        parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsCancelHomeLike"])#是否取消首页点赞
        parse_bool(data["AppConfigData"]["FanPagesConfig"]["IsCancelPostsLike"])#是否取消贴文点赞

        self.status_window = None  # 状态窗口引用
        self.username = content1

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
        # await self.tweet_comment() # """贴文、推文"""
        # await self.post_comment() # """推文"""
        # await self.add_join_groups() # """加社團"""
        await self.account_nurturing()#養號
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
        await self.page.goto(url="https://www.facebook.com/", wait_until='load')
        title = await self.page.title()
        if "Facebook" in title:
            await asyncio.sleep(3)
        else:
            print(f"標題未包含 'Facebook'，當前標題: {title}，等待10秒後重試...")
            await asyncio.sleep(10)  # 等待10秒
        # num_posts = self.home_like_num
        num_posts = 20
        print(f"准备与 {num_posts} 个帖子互动")

        for i in range(1, num_posts + 1):

            selector = f'//div[@class="x1hc1fzr x1unhpq9 x6o7n8i"]/div//div[@aria-posinset={i}]'
            element = await self.page.wait_for_selector(selector, timeout=15000)
            if element:
                await element.scroll_into_view_if_needed()
                print(f"第 {i} 个帖子")
            try:
                element = await self.page.wait_for_selector(selector+'//span[contains(text(), "助")]', timeout=10000)
                if element:
                    await element.scroll_into_view_if_needed()
                    print("出現啦",i)
                like = self.home_like
                await asyncio.sleep(random.uniform(5, 10))

            except Exception as e:
                print(f"处理第 {i} 个帖子时出错: {str(e)}")

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
            await self.page.goto(url=post_url[i]+"/buy_sell_discussion", wait_until='load',timeout=50000)
            if await self.url_open_except() :# 檢測網站目前無法查看此內容
                continue
            isno_groups = await self.join_groups()#加社团
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
                except Exception as e:
                    print(f"没有找到可发布贴文位置: {str(e)}")
                await asyncio.sleep(5)
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
            input_selector = '//div[@role="dialog"]//div[@role="textbox" and contains(@aria-placeholder,"建立公開貼文……") or @role="textbox" and contains(@aria-placeholder, "...") or @role="textbox" and contains(@aria-placeholder, "发布公开帖…") or @role="textbox" and contains(@aria-placeholder, "在想些什麼") or @role="textbox" and contains(@aria-placeholder, "分享你的新鲜事吧") or @role="textbox" and contains(@aria-placeholder, "！")or @role="textbox" and contains(@aria-placeholder, "？")]'
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
            url_selector = '//h2[@dir="auto"]/span[@dir="auto"]'
            url_button = await self.page.wait_for_selector(url_selector, timeout=5000)
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
    async def extract_posturl_ids(self,urls):
        post_ids = []
        # 匹配各种格式的帖子ID
        pattern = r'/(?:posts/|permalink/|permalink&id=)(\d+)'

        for url in urls:
            match = re.search(pattern, url)
            if match:
                post_ids.append(match.group(1))

        return post_ids
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