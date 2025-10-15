import asyncio
import os
import random
import time
import json
import base64
import re
import platform
import winreg  # 仅适用于Windows
import shutil  # 适用于Linux和macOS
from urllib.parse import urlencode
import requests
from PyQt5.QtWidgets import QMessageBox
from playwright.async_api import async_playwright

DATABASE_CONFIG = {
    "host": "dbs.kydb.vip",
    "name": "Instagram",
    "username": "sa",
    "password": "Yunsin@#861123823_shp4"
}

PROXY_CONFIG = "http://127.0.0.1:25378"


class InstagramScraper:
    def __init__(self, cookies, log, db,progress_callback=None,getinputnum = 0):
        self.username = None
        self.password = None
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = 15
        self.proxies = {
            "http": PROXY_CONFIG,
            "https": PROXY_CONFIG
        }
        self.direct_region_hint = None
        self.u_rur = None
        self.log = log
        self.db = db
        self.current_url = None
        self.progress_callback = progress_callback

        self.getinput_num = getinputnum
        self.browser_path = get_chrome_path()
    # 模拟登录
    async def login(self, username, password):
        self.username = username
        self.password = password

        try:
            # 启动 Playwright 并设置超时
            playwright = await asyncio.wait_for(async_playwright().start(), timeout=30)
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",  # 禁用自动化控制特征
                    "--disable-infobars",  # 隐藏"Chrome正在被自动化软件控制"提示
                    "--start-maximized",  # 最大化窗口更接近人类操作
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
                    # 使用常见User-Agent
                ],  # 添加兼容性参数
                executable_path = self.browser_path
            )
            # 创建上下文时注入JavaScript覆盖WebDriver标志
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                viewport={"width": 1920, "height": 1080}  # 设置常见分辨率
            )

            # 注入JavaScript以覆盖navigator.webdriver属性
            await context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        window.chrome = { runtime: {} };  // 模拟Chrome环境
                    """)
            self.page = await self.browser.new_page()
            await self._perform_login()
            await self._save_cookies()
        except asyncio.TimeoutError:
            raise Exception("Playwright 启动超时，请检查网络或浏览器安装")
        except Exception as e:
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
            raise

    async def _perform_login(self):
        await self.page.goto(url="https://www.instagram.com/accounts/login/", wait_until='load', timeout=30000)

        # 增加元素检查
        try:
            # 显式等待用户名输入框
            await self.page.wait_for_selector("input[name='username']", timeout=10000)
            await self.page.wait_for_selector("input[name='password']", timeout=10000)
        except Exception as e:
            await self.browser.close()
            raise Exception("无法找到登录输入框，可能页面加载失败")

        await self.page.fill("input[name='username']", self.username)
        await asyncio.sleep(random.uniform(1, 3))  # 随机等待
        await self.page.fill("input[name='password']", self.password)
        await asyncio.sleep(random.uniform(1, 3))  # 随机等待

        # 增加登录结果检查
        try:
            # await self.page.click("button[type='submit']")
            submit_button = await self.page.query_selector("button[type='submit']")
            box = await submit_button.bounding_box()
            await self.page.mouse.move(
                box['x'] + box['width'] / 2,
                box['y'] + box['height'] / 2,
                steps=random.randint(5, 10)  # 分步移动
            )
            await self.page.mouse.click(
                box['x'] + box['width'] / 2,
                box['y'] + box['height'] / 2
            )
            await asyncio.sleep(25)

            # 检查是否仍在登录页
            if "auth_platform/codeentry" in self.page.url:
                await asyncio.sleep(60)
                await self.browser.close()
            elif "accounts/login" in self.page.url or "accounts/suspended" in self.page.url:
                await self.browser.close()
                raise Exception("登录失败，请检查账号密码")

        except Exception as e:
            await self.browser.close()
            raise

    async def validate_cookies(self):
        """验证cookies是否有效"""
        playwright = None
        try:
            if not self.cookies:
                return False

            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True,executable_path = self.browser_path)
            context = await browser.new_context()

            # 注入cookies
            await context.add_cookies(self.cookies)

            # 创建新页面并访问需要登录的页面
            page = await context.new_page()
            await page.goto("https://www.instagram.com/accounts/edit/", timeout=20000)

            # 检查是否重定向到登录页
            if "accounts/login" in page.url or "auth_platform/codeentry" in page.url or "accounts/suspended" in page.url:
                raise Exception("Cookies已失效")

            # 检查登录状态元素
            await page.wait_for_selector('svg[aria-label="Instagram"]', timeout=15000)
            return True

        except Exception as e:
            # QMessageBox.warning(None,"登錄错误", "错误：Cookies驗證登錄失敗", QMessageBox.Ok)
            raise Exception(f"Cookies验证失败: {str(e)}")
        finally:
            if playwright:
                await browser.close()
                await playwright.stop()

    async def _save_cookies(self):
        if "accounts/login" in self.page.url:
            raise Exception("Login failed")
        if "challenge" in self.page.url:
            raise Exception("Account restricted")
        self.cookies = await self.page.context.cookies()
        # os.makedirs("./cookies", exist_ok=True)
        with open("instagram.json", "w") as f:
            json.dump(self.cookies, f, indent=4)

        # 登录完成后关闭可视浏览器
        await self.browser.close()
        # 重新启动无头浏览器用于后续操作
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True,executable_path = self.browser_path)
        self.page = await self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        )

    # 获取请求Auth签名
    def getBearerAuth(self):
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        sessionid = next((cookie for cookie in self.cookies if cookie['name'] == "sessionid"), None)
        auth_str = "{\"ds_user_id\":\"" + ds_user_id['value'] + "\",\"sessionid\":\"" + sessionid['value'] + "\"}"
        auth_bytes = auth_str.encode('utf-8')
        auth_str = base64.b64encode(auth_bytes)
        return "Bearer IGT:2:" + auth_str.decode('utf-8')

    # 通过作品URL获取作品ID和用户ID
    async def getMediaIdAndUserIdFromPostUrl(self, url):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "dnt": "1",
            "dpr": "1",
            "priority": "u=0, i",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-full-version-list": "\"Google Chrome\";v=\"131.0.6778.265\", \"Chromium\";v=\"131.0.6778.265\", \"Not_A Brand\";v=\"24.0.0.0\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-model": "\"SM-G955U\"",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua-platform-version": "\"8.0.0\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "viewport-width": "360"
        }

        media_id = ""
        user_id = ""
        try:
            # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            pattern = r'<meta property="al:ios:url" content="instagram://media\?id=(\d+)" />'
            match = re.search(pattern, response.text)
            if match:
                media_id = match.group(1)
            else:
                raise Exception("获取作品ID失败")
            pattern = r'<meta property="instapp:owner_user_id" content="(\d+)" />'
            match = re.search(pattern, response.text)
            if match:
                user_id = match.group(1)
            else:
                raise Exception("获取用户ID失败")
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取用户ID及作品ID的请求失败({e})")

        await asyncio.sleep(5)
        return {"media_id": media_id, "user_id": user_id}

    # 通过用户主页URL获取用户ID
    async def getUserIdByHomeUrl(self, url):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "dnt": "1",
            "dpr": "1",
            "priority": "u=0, i",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-full-version-list": "\"Google Chrome\";v=\"131.0.6778.265\", \"Chromium\";v=\"131.0.6778.265\", \"Not_A Brand\";v=\"24.0.0.0\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-model": "\"SM-G955U\"",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua-platform-version": "\"8.0.0\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "viewport-width": "360"
        }
        cookie_str = ''
        for cookie in self.cookies:
            cookie_str += cookie['name'] + '=' + cookie['value'] + ';'

        headers['cookie'] = cookie_str

        try:
            # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            pattern = r'"profile_id":"(\d+)","sub_path":"posts"'
            match = re.search(pattern, response.text)
            if match:
                user_id = match.group(1)
            else:
                raise Exception("获取用户ID失败")
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取用户ID的请求失败({e})")

        await asyncio.sleep(5)
        return user_id

    # 获取文章/Reels相关用户（留言用户/点赞用户）
    async def getPostRelationUser(self, url):
        self.current_url = url
        res = await self.getMediaIdAndUserIdFromPostUrl(url)
        await self.getLikesUser(res['media_id'], res['user_id'])
        await self.getCommentsUser(res["media_id"], res['user_id'])
        self.current_url = None

    # 获取作品点赞用户列表
    async def getLikesUser(self, item_id, user_id):
        types = 2
        current_url = self.current_url or f"MediaID:{item_id}"
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        url = "https://i.instagram.com/api/v1/media/" + item_id + "_" + user_id + "/likers/"
        headers = {
            "host": "i.instagram.com",
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-10f01254-3bd2-47d9-852c-da07cf7cd9b4-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "393.000",
            "x-ig-bandwidth-totalbytes-b": "3091226",
            "x-ig-bandwidth-totaltime-ms": "7273",
            "x-bloks-version-id": "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb",
            "x-ig-www-claim": "hmac.AR0K2P0bYN8DR7cg1JtzX9WpqBVnAowCG4csanefr841T6td",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "caa03952-e663-4958-8d7c-a295a9bf3cab",
            "x-ig-family-device-id": "3e252b4f-de8c-4d41-99db-3633200053e1",
            "x-ig-android-id": "android-928cff2f722b4a54",
            "x-ig-timezone-offset": "28800",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "567067343352427",
            "priority": "u=3",
            "user-agent": "Instagram 275.0.0.27.98 Android (32/12; 640dpi; 1440x2560; Samsung; SM-S9210; e1q; Samsung; zh_CN; 458229258)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id[
                'value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "HIL," + ds_user_id[
                'value'] + ",1766216864:01f764001ec2705e2abfb0cbd7cec2df41dd6e7eb9f29f33398e11907bf0bba40bf9d897",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }
        statistics = 1
        statistics_show = 1
        user_list = []
        show_user_list = []
        try:
            # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            for user in data['users']:
                user_in_bool, user_list = duplicates_and_add(user_list, user['id'])
                if statistics <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                    self.log.info(f"点赞用户: ID: {user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                    self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'],instagram_id=current_url + "|+|點讚",types=types)
                    # self.db.insert_count(current_url + "|+|點讚", 1, types)
                    statistics = statistics + 1
            for user in data['users']:
                user_in_bool, show_user_list = duplicates_and_add(show_user_list, user['id'])
                if statistics_show <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                    if self.progress_callback:
                        self.progress_callback('like', self.current_url, {
                            'id': user['id'],
                            'username': user['username'],
                            'full_name': user['full_name']
                        })
                        statistics_show = statistics_show + 1

        except requests.exceptions.RequestException as e:
            raise Exception(f"获取作品点赞用户列表的请求失败({e})")

        await asyncio.sleep(self.delay)
        # self.db.insert_count(current_url+"|+|點讚",statistics - 1,types)
        # print("id,num",current_url+"|+|點讚",statistics - 1)
    # 获取作品评论用户列表
    async def getCommentsUser(self, item_id, user_id):
        types = 2
        current_url = self.current_url or f"MediaID:{item_id}"
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = "https://i.instagram.com/api/v1/media/" + item_id + "_" + user_id + "/stream_comments/?"

        params = {
            "can_support_threading": "true",
            "is_carousel_bumped_post": "false",
            "feed_position": "5"
        }

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-dbc7ac0c-7b1f-457e-a64f-0f5e914691e8-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "16e9197b928710eafdf1e803935ed8c450a1a2e3eb696bff1184df088b900bcf",
            "x-ig-www-claim": "hmac.AR0K2P0bYN8DR7cg1JtzX9WpqBVnAowCG4csanefr841T6m6",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-ig-transfer-encoding": "chunked",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "300d4af0-9663-40c6-89bd-04148558ebec",
            "x-ig-family-device-id": "7a832632-a1dc-492c-bc6e-aed4a60f788d",
            "x-ig-android-id": "android-88c940fbc3c7104c",
            "x-ig-timezone-offset": "28800",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "567067343352427",
            "priority": "u=3",
            "user-agent": "Instagram 361.0.0.46.88 Android (32/12; 640dpi; 1440x2560; Samsung; SM-S9210; e1q; Samsung; zh_CN; 674675155)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id[
                'value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "HIL," + ds_user_id[
                'value'] + ",1766216864:01f764001ec2705e2abfb0cbd7cec2df41dd6e7eb9f29f33398e11907bf0bba40bf9d897",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        min_id = ""
        hasNextPage = True
        statistics = 1
        statistics_show = 1
        user_list = []
        show_user_list = []
        while hasNextPage:
            if len(min_id) > 0:
                params["min_id"] = min_id

            url_params = urlencode(params)
            url = api_url + url_params

            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                resp_headers = response.headers
                self.direct_region_hint = resp_headers.get('ig-set-ig-u-ig-direct-region-hint')
                self.u_rur = resp_headers.get('ig-set-ig-u-rur')

                headers["ig-u-ig-direct-region-hint"] = self.direct_region_hint
                headers["ig-u-rur"] = self.u_rur

                json_str = "[" + response.text.replace("\n", ",").rstrip(',') + "]"
                data = json.loads(json_str)

                if "next_min_id" not in data[0]:
                    min_id = ""
                    hasNextPage = False
                else:
                    min_id = data[0]["next_min_id"]

                for item in data:
                    for comment in item['comments']:
                        user_in_bool, user_list = duplicates_and_add(user_list, comment['user_id'])
                        if statistics <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                            self.log.info(
                                f"评论用户: ID:{comment['user_id']} / Name: {comment['user']['username']} / Full Name: {comment['user']['full_name']}")
                            self.db.insert_data(user_id=comment['user_id'], user_name=comment['user']['username'],
                                                user_fullname=comment['user']['full_name'],instagram_id=current_url + "|+|評論",types=types)
                            # self.db.insert_count(current_url + "|+|評論", 1, types)
                            statistics = statistics + 1
                            sub_comments = comment.get('preview_child_comments', [])
                            if sub_comments and statistics_show <= self.getinput_num or sub_comments and self.getinput_num == 0:
                                for sub_comment in sub_comments:
                                    user_in_bool, user_list = duplicates_and_add(user_list, sub_comment['user_id'])
                                    if user_in_bool:
                                        self.log.info(
                                            f"评论用户: ID:{sub_comment['user_id']} / Name: {sub_comment['user']['username']} / Full Name: {sub_comment['user']['full_name']}")
                                        self.db.insert_data(user_id=sub_comment['user_id'],
                                                            user_name=sub_comment['user']['username'],
                                                            user_fullname=sub_comment['user']['full_name'],instagram_id=current_url + "|+|評論",types=types)
                                        # self.db.insert_count(current_url + "|+|評論", 1, types)
                                        statistics = statistics + 1
                    for comment in item['comments']:
                        user_in_bool, show_user_list = duplicates_and_add(show_user_list, comment['user_id'])
                        if statistics_show <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                            if self.progress_callback:
                                self.progress_callback('comment', self.current_url, {
                                    'id': comment['user_id'],
                                    'username': comment['user']['username'],
                                    'full_name': comment['user']['full_name']
                                })
                                statistics_show = statistics_show + 1
                                sub_comments = comment.get('preview_child_comments', [])
                                if sub_comments and statistics_show <= self.getinput_num or sub_comments and self.getinput_num == 0:
                                    for sub_comment in sub_comments:
                                        user_in_bool, show_user_list = duplicates_and_add(show_user_list,
                                                                                     sub_comment['user_id'])
                                        if user_in_bool:
                                            if self.progress_callback:
                                                self.progress_callback('comment', self.current_url, {
                                                    'id': sub_comment['user_id'],
                                                    'username': sub_comment['user']['username'],
                                                    'full_name': sub_comment['user']['full_name']
                                                })
                                                statistics_show = statistics_show + 1
                        else:
                            hasNextPage = False
            except requests.exceptions.RequestException as e:
                raise Exception(f"获取作品评论用户列表的请求失败({e})")

            await asyncio.sleep(self.delay)
        # self.db.insert_count(current_url + "|+|評論", statistics - 1,types)
        # print("id,num", current_url+"|+|評論", statistics - 1)
    # 获取用户粉丝用户列表
    async def getFollowUser(self, url):
        types = 3
        self.current_url = url
        auth = self.getBearerAuth()
        user_id = await self.getUserIdByHomeUrl(url)
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)

        url = "https://i.instagram.com/graphql/query"
        headers = {
            "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"none","request_category":"graphql","retry_attempt":"0"}}',
            "x-fb-rmd": "state=URL_ELIGIBLE",
            "x-ig-app-id": "567067343352427",
            "priority": "u=3, i",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig_legacy_eager_dict_validate_null": "true",
            "x-root-field-name": "xdt_api__v1__friendships__followers",
            "x-ig-device-id": "300d4af0-9663-40c6-89bd-04148558ebec",
            "ig-u-rur": "HIL," + ds_user_id[
                'value'] + ",1768318131:01f7b208b19c329eeda0839f2f798f0dc0160043297c83528c0f3eaf10fb78b144caf361",
            "x-fb-friendly-name": "FollowersList",
            "accept-language": "zh-CN, en-US",
            "x-mid": mid['value'],
            "content-type": "application/x-www-form-urlencoded",
            "x-ig-capabilities": "3brTv10=",
            "x-graphql-client-library": "pando",
            "authorization": auth,
            "ig_legacy_dict_validate_null": "true",
            "ig-intended-user-id": ds_user_id['value'],
            "x-tigon-is-retry": "False",
            "user-agent": "Instagram 361.0.0.46.88 Android (32/12; 640dpi; 1440x2560; Samsung; SM-S9210; e1q; Samsung; zh_CN; 674675155)",
            "accept-encoding": "gzip, deflate",
            "x-fb-http-engine": "Tigon/Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }
        data = {
            "method": "post",
            "pretty": "false",
            "format": "json",
            "server_timestamps": "true",
            "locale": "user",
            "fb_api_req_friendly_name": "FollowersList",
            "client_doc_id": "28479704798344003308647327139",
            "enable_canonical_naming": "true",
            "enable_canonical_variable_overrides": "true",
            "enable_canonical_naming_ambiguous_type_prefixing": "true",
        }
        variables = {
            "include_unseen_count": False,
            "query": "",
            "include_biography": False,
            "exclude_field_is_favorite": False,
            "user_id": user_id,
            "request_data": {
                "rank_token": "",
                "enableGroups": True
            },
            "search_surface": "follow_list_page"
        }
        max_id = ""
        hasNextPage = True
        statistics = 1
        statistics_show = 1
        user_list = []
        show_user_list = []
        while hasNextPage:
            if max_id != "":
                variables["max_id"] = max_id
                variable = variables["max_id"]
                self.log.info(f"加载更多分页: {variable}")
                if not variable or variable == None:
                    max_id = ''
                    hasNextPage = False
            if hasNextPage!=False:
                try:
                    data['variables'] = json.dumps(variables)
                    # response = requests.post(url, headers=headers, data=data, proxies=self.proxies, timeout=10)
                    response = requests.post(url, headers=headers, data=data, timeout=10)
                    response.raise_for_status()

                    resp_headers = response.headers
                    self.u_rur = resp_headers.get('ig-set-ig-u-rur')
                    headers["ig-u-rur"] = self.u_rur

                    res = json.loads(response.text)
                    items = res['data'][
                        '1$xdt_api__v1__friendships__followers(_request_data:$request_data,include_friendship_status:true,include_global_blacklist_sample:false,max_id:$max_id,query:$query,search_surface:$search_surface,user_id:$user_id)']
                    if "next_max_id" in items and items['next_max_id'] != '':
                        max_id = items['next_max_id']
                    else:
                        max_id = ''
                        hasNextPage = False
                    print(len(items['users']))
                    for user in items['users']:
                        user_in_bool, user_list = duplicates_and_add(user_list, user['id'])
                        if statistics <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                            self.log.info(
                                f"粉丝用户: ID:{user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                            self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'],instagram_id=self.current_url,types=types)
                            # self.db.insert_count(self.current_url, 1, types)
                            statistics = statistics + 1
                    users = res['data'][
                        '1$xdt_api__v1__friendships__followers(_request_data:$request_data,include_friendship_status:true,include_global_blacklist_sample:false,max_id:$max_id,query:$query,search_surface:$search_surface,user_id:$user_id)']['users']
                    print(len(users))
                    for user in users:
                        user_in_bool, show_user_list = duplicates_and_add(show_user_list, user['id'])
                        if statistics_show <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                            if self.progress_callback:
                                self.progress_callback('follower', url, {
                                    'id': user['id'],
                                    'username': user['username'],
                                    'full_name': user['full_name']
                                })
                                statistics_show = statistics_show + 1
                        else:
                            max_id = ''
                            hasNextPage = False

                except requests.exceptions.RequestException as e:
                    raise Exception(f"获取作者粉丝用户列表的请求失败({e})")

                await asyncio.sleep(self.delay)
        # self.db.insert_count(self.current_url, statistics - 1,types)
        # print("id,num", self.current_url, statistics - 1)
        self.current_url = None
    # 按关键词搜索用户列表
    async def getKeywordUsers(self, keyword):
        types = 1
        self.current_url = keyword
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = "https://i.instagram.com/api/v1/fbsearch/account_serp/?"

        params = {
            "search_surface": "user_serp",
            "timezone_offset": "28800",
            "count": "30",
            "query": keyword
        }

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-99d390a9-6688-4b53-bf0c-9c92bc5d61fc-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "16e9197b928710eafdf1e803935ed8c450a1a2e3eb696bff1184df088b900bcf",
            "x-ig-www-claim": "hmac.AR0K2P0bYN8DR7cg1JtzX9WpqBVnAowCG4csanefr841T6m6",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "true",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-ig-transfer-encoding": "chunked",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "300d4af0-9663-40c6-89bd-04148558ebec",
            "x-ig-family-device-id": "7a832632-a1dc-492c-bc6e-aed4a60f788d",
            "x-ig-android-id": "android-88c940fbc3c7104c",
            "x-ig-timezone-offset": "28800",
            "x-ig-client-endpoint": "UserSerpGridFragment:serp_users",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-fb-network-properties": "Validated;dhcpServerAddr=10.0.2.2;LocalAddrs=/fe80::5acf:7f80:7a75:72d3,/10.0.2.15,;",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "567067343352427",
            "priority": "u=3",
            "user-agent": "Instagram 361.0.0.46.88 Android (32/12; 640dpi; 1440x2560; Samsung; SM-S9210; e1q; Samsung; zh_CN; 674675155)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "HIL," + ds_user_id[
                'value'] + ",1766216864:01f764001ec2705e2abfb0cbd7cec2df41dd6e7eb9f29f33398e11907bf0bba40bf9d897",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        rank_token = ""
        page_token = ""
        page = 0
        num_results = 20
        hasNextPage = True
        statistics = 1
        statistics_show = 1
        user_list = []
        show_user_list = []
        while hasNextPage:
            if len(page_token) > 0:
                params["page_token"] = page_token
                params["next_max_id"] = page_token

            if len(rank_token) > 0:
                params["rank_token"] = rank_token

            if page > 0:
                params["paging_token"] = '{"total_num_items":' + str(page * num_results) + '}'

            url_params = urlencode(params)
            url = api_url + url_params
            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                resp_headers = response.headers
                self.u_rur = resp_headers.get('ig-set-ig-u-rur')
                headers["ig-u-rur"] = self.u_rur

                data = json.loads(response.text)

                page = page + 1

                if data['has_more'] == False or "has_more" not in data:
                    hasNextPage = False
                else:
                    rank_token = data['rank_token']
                    page_token = data['page_token']
                    num_results = data['num_results']

                for user in data['users']:
                    user_in_bool, user_list = duplicates_and_add(user_list, user['id'])
                    if statistics <=self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                        self.log.info(
                            f"关键词搜索用户: ID:{user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                        self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'],instagram_id=self.current_url,types=types)
                        # self.db.insert_count(self.current_url, 1, types)
                        statistics = statistics + 1
                for user in data['users']:
                    user_in_bool, show_user_list = duplicates_and_add(show_user_list, user['id'])
                    if statistics_show <= self.getinput_num and user_in_bool or self.getinput_num == 0 and user_in_bool:
                        if self.progress_callback:
                            self.progress_callback('keyword', keyword, {
                                'id': user['id'],
                                'username': user['username'],
                                'full_name': user['full_name']
                            })
                            statistics_show = statistics_show + 1
                        else:
                            max_id = ''
                            hasNextPage = False
            except requests.exceptions.RequestException as e:
                raise Exception(f"获取关键词用户列表的请求失败({e})")

            await asyncio.sleep(self.delay)
        # self.db.insert_count(self.current_url, statistics - 1,types)
        # print("id,num", self.current_url, statistics - 1)
        self.current_url = None

    # 销毁资源
    async def close(self):
        try:
            if self.browser:
                await self.browser.close()
            if self.db:
                self.db.close()
        except Exception as e:
            self.log.error(f"资源关闭异常: {str(e)}")
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
def duplicates_and_add(lst, string):
    if string in lst:
        return False, lst
    else:
        lst.append(string)
        return True, lst