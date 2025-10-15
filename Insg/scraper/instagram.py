import asyncio
import os
import time
import json
import base64
import re
from urllib.parse import urlencode
import requests
from PyQt5.QtWidgets import QMessageBox
from playwright.async_api import async_playwright

DATABASE_CONFIG = {
    "host": "dbs.kydb.vip",
    "name": "FbSocietiesUser",
    "username": "sa",
    "password": "Yunsin@#861123823_shp4"
}

PROXY_CONFIG = "http://127.0.0.1:25378"


class InstagramScraper:
    def __init__(self, cookies, log, db,progress_callback=None):
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
    # 模拟登录
    async def login(self, username, password):
        self.username = username
        self.password = password
        try:
            # 启动 Playwright 并设置超时
            playwright = await asyncio.wait_for(async_playwright().start(), timeout=30)
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=["--disable-gpu", "--no-sandbox"]  # 添加兼容性参数
            )
            self.page = await self.browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
            )
            await self._perform_login()
            await self._save_cookies()
        except asyncio.TimeoutError:
            raise Exception("Playwright 启动超时，请检查网络或浏览器安装")
        except Exception as e:
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
            raise

    async def _perform_login(self):
        await self.page.goto(url="https://www.instagram.com/accounts/login/", wait_until='load')
        await asyncio.sleep(1)

        await self.page.fill("input[name='username']", self.username)
        await asyncio.sleep(1)
        await self.page.fill("input[name='password']", self.password)
        await asyncio.sleep(1)
        await self.page.click("button[type='submit']")

        await asyncio.sleep(10)

    async def validate_cookies(self):
        """验证cookies是否有效"""
        playwright = None
        try:
            if not self.cookies:
                return False

            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()

            # 注入cookies
            await context.add_cookies(self.cookies)

            # 创建新页面并访问需要登录的页面
            page = await context.new_page()
            await page.goto("https://www.instagram.com/accounts/edit/", timeout=20000)

            # 检查是否重定向到登录页
            if "accounts/login" in page.url:
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
        self.browser = await playwright.chromium.launch(headless=True)
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
            response = requests.get(url, headers=headers, timeout=10, verify=False)
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
            response = requests.get(url, headers=headers, timeout=10, verify=False)
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

        try:
            # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            data = json.loads(response.text)
            for user in data['users']:
                self.log.info(f"点赞用户: ID: {user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'])
            for user in data['users']:
                if self.progress_callback:
                    self.progress_callback('like', self.current_url, {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name']
                    })
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取作品点赞用户列表的请求失败({e})")

        await asyncio.sleep(self.delay)

    # 获取作品评论用户列表
    async def getCommentsUser(self, item_id, user_id):
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

        while hasNextPage:
            if len(min_id) > 0:
                params["min_id"] = min_id

            url_params = urlencode(params)
            url = api_url + url_params

            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
                response = requests.get(url, headers=headers, timeout=10, verify=False)
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
                        self.log.info(
                            f"评论用户: ID:{comment['user_id']} / Name: {comment['user']['username']} / Full Name: {comment['user']['full_name']}")
                        self.db.insert_data(user_id=comment['user_id'], user_name=comment['user']['username'],
                                            user_fullname=comment['user']['full_name'])

                        sub_comments = comment.get('preview_child_comments', [])
                        if sub_comments:
                            for sub_comment in sub_comments:
                                self.log.info(
                                    f"评论用户: ID:{sub_comment['user_id']} / Name: {sub_comment['user']['username']} / Full Name: {sub_comment['user']['full_name']}")
                                self.db.insert_data(user_id=sub_comment['user_id'],
                                                    user_name=sub_comment['user']['username'],
                                                    user_fullname=sub_comment['user']['full_name'])
                    for comment in item['comments']:
                        if self.progress_callback:
                            self.progress_callback('comment', self.current_url, {
                                'id': comment['user_id'],
                                'username': comment['user']['username'],
                                'full_name': comment['user']['full_name']
                            })
            except requests.exceptions.RequestException as e:
                raise Exception(f"获取作品评论用户列表的请求失败({e})")

            await asyncio.sleep(self.delay)

    # 获取用户粉丝用户列表
    async def getFollowUser(self, url):
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
            "variables": "{\"include_unseen_count\":false,\"query\":\"\",\"include_biography\":false,\"exclude_field_is_favorite\":false,\"user_id\":\"" + user_id + "\",\"request_data\":{\"rank_token\":\"\",\"enableGroups\":true},\"search_surface\":\"follow_list_page\"}"
        }

        try:
            # response = requests.post(url, headers=headers, data=data, proxies=self.proxies, timeout=10)
            response = requests.post(url, headers=headers, data=data, timeout=10, verify=False)
            response.raise_for_status()

            resp_headers = response.headers
            self.u_rur = resp_headers.get('ig-set-ig-u-rur')
            headers["ig-u-rur"] = self.u_rur

            data = json.loads(response.text)
            for user in data['data'][
                '1$xdt_api__v1__friendships__followers(_request_data:$request_data,include_friendship_status:true,include_global_blacklist_sample:false,max_id:$max_id,query:$query,search_surface:$search_surface,user_id:$user_id)'][
                'users']:
                self.log.info(f"粉丝用户: ID:{user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'])
            users = data['data'][
                '1$xdt_api__v1__friendships__followers(_request_data:$request_data,include_friendship_status:true,include_global_blacklist_sample:false,max_id:$max_id,query:$query,search_surface:$search_surface,user_id:$user_id)'][
                'users']
            for user in users:
                if self.progress_callback:
                    self.progress_callback('follower', url, {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name']
                    })
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取作者粉丝用户列表的请求失败({e})")
        self.current_url = None
        await asyncio.sleep(self.delay)

    # 按关键词搜索用户列表
    async def getKeywordUsers(self, keyword):
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
                response = requests.get(url, headers=headers, timeout=10, verify=False)
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
                    self.log.info(
                        f"关键词搜索用户: ID:{user['id']} / Name: {user['username']} / Full Name: {user['full_name']}")
                    self.db.insert_data(user_id=user['id'], user_name=user['username'], user_fullname=user['full_name'])
                for user in data['users']:
                    if self.progress_callback:
                        self.progress_callback('keyword', keyword, {
                            'id': user['id'],
                            'username': user['username'],
                            'full_name': user['full_name']
                        })
            except requests.exceptions.RequestException as e:
                raise Exception(f"获取关键词用户列表的请求失败({e})")

            await asyncio.sleep(self.delay)

        self.current_url = None

    # 销毁资源
    async def close(self):
        """确保所有资源正确关闭"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()  # 显式停止playwright
            self.db.close()
        except Exception as e:
            self.log.error(f"资源关闭时发生错误: {str(e)}")