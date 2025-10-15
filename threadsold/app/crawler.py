import asyncio
from datetime import datetime
import random
import time
import json
import base64
from urllib.parse import urlencode
import requests
from playwright.async_api import async_playwright
from threadsold.app.logger import logger
from threadsold.app.config import ACCOUNT_USERNAME, ACCOUNT_PASSWORD, REQUEST_DELAY, REQUEST_PROXY
from threadsold.app.database import Database

class Crawler:
    def __init__(self, is_running_fn, cookies):
        self.username = ACCOUNT_USERNAME
        self.password = ACCOUNT_PASSWORD
        self.browser = None
        self.page = None
        self.cookies = cookies
        self.delay = REQUEST_DELAY
        self.proxies = {
            "http": REQUEST_PROXY,
            "https": REQUEST_PROXY
        }
        self.direct_region_hint = None
        self.u_rur = None
        self.db = Database()
        self.is_running_fn = is_running_fn

    async def start(self, type, keyword):
        if self.cookies == None:
            await self.login()
        else:
            ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
            sessionid = next((cookie for cookie in self.cookies if cookie['name'] == "sessionid"), None)
            if not self.cookies or not ds_user_id or not sessionid or sessionid['expires'] < time.time() + 86400:
                logger.warning("获取登陆状态失败或登陆已过期, 开始重新登陆账号")
                await self.login()

        if type == 'search':
            await self.getKeywordSearch(keyword)
        elif type == 'userpost':
            users = self.db.get_all_users()
            for user in users:
                await self.getUserPost(user['user_id'], user['name'])
        elif type == 'follower':
            users = self.db.get_all_users()
            for user in users:
                await self.getUserFans(user['name'], user['user_id'])

    # 模拟登录
    async def login(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        await self.page.goto(url="https://www.threads.net/login",wait_until='load')
        await asyncio.sleep(1)
        
        username_input = self.page.locator("form input").first
        password_input = self.page.locator("form input").nth(1)
        await username_input.fill(self.username)
        await asyncio.sleep(1)
        await password_input.fill(self.password)
        await asyncio.sleep(1)
        await self.page.click("form div[role='button']")

        await self.page.wait_for_url("https://www.threads.net/?login_success=true")
        await asyncio.sleep(10)

        self.cookies = await self.page.context.cookies()

        with open("./data/threads.json", "w") as f:
            json.dump(self.cookies, f, indent=4)

        if "login" in self.page.url:
            raise Exception("登录失败，请检查用户名和密码")
        else:
            logger.info('登陆成功')
    
    # 获取请求Auth签名
    def getBearerAuth(self):
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        sessionid = next((cookie for cookie in self.cookies if cookie['name'] == "sessionid"), None)
        auth_str = "{\"ds_user_id\":\"" + ds_user_id['value'] + "\",\"sessionid\":\"" + sessionid['value'] + "\"}"
        auth_bytes = auth_str.encode('utf-8')
        auth_str = base64.b64encode(auth_bytes)
        return "Bearer IGT:2:" + auth_str.decode('utf-8')
    
    # 搜索指定关键词
    async def getKeywordSearch(self, keyword):
        logger.info(f"开始采集关键词[{keyword}]的相关数据")
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = 'https://i.instagram.com/api/v1/fbsearch/text_app/serp/'

        params = {
            "search_surface": "search_tab_typeahead",
            "recent": 0,
            "query": keyword,
            "is_from_pull_to_refresh": 0
        }

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-c7e30dd9-6350-4b68-a3ac-60d67ad2127f-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "1631.000",
            "x-ig-bandwidth-totalbytes-b": "0",
            "x-ig-bandwidth-totaltime-ms": "0",
            "x-bloks-version-id": "873c78bbf5b48072533688c4dfe047ad5f7d6774851be63e2c609a6ed0f0957c",
            "x-ig-www-claim": "hmac.AR0JoLlXUGrLbilcEM402EAZnxT2u-EAa7nQR0CE9BVWfuOK",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "ef19f395-4663-4e2e-8695-317050bc4e92",
            "x-ig-family-device-id": "da6b602e-ed2f-4e7b-9052-5f1d9cc6dfa4",
            "x-ig-android-id": "android-af1261f2f3d61aba",
            "x-ig-timezone-offset": "28800",
            "x-ig-nav-chain": "BcnRoute:ig_text_feed_timeline:1:cold_start:1744385489.737::,SearchDestination:ig_text_search_nullstate:2:button:1744385539.523::,BcnRoute:ig_text_search_typeahead:3:button:1744385545.79::,BcnRoute:ig_text_search_serp_top:4:button:1744385562.6::",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "3419628305025917",
            "priority": "u=3",
            "user-agent": "Barcelona 361.3.0.53.106 Android (32/12; 640dpi; 1440x2560; Xiaomi; 24031PN0DC; aurora; Xiaomi; zh_CN; 676217033)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "VLL," + ds_user_id['value'] + ",1775921545:01f7a1a5acde9eb65f6ac0dcc53919975351832d7af07effd53b29ee8b3c24fec6eaff64",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "true",
            "x-fb-server-cluster": "true"
        }

        rank_token = ""
        page_token = ""
        hasNextPage = True

        while hasNextPage and self.is_running_fn():
            if rank_token != "":
                params["rank_token"] = rank_token
            if page_token != "":
                params["page_token"] = page_token

            url_params = urlencode(params)
            url = f"{api_url}?{url_params}"

            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                resp_headers = response.headers
                self.direct_region_hint = resp_headers.get('ig-set-ig-u-ig-direct-region-hint')
                self.u_rur = resp_headers.get('ig-set-ig-u-rur')

                headers["ig-u-ig-direct-region-hint"] = self.direct_region_hint
                headers["ig-u-rur"] = self.u_rur

                data = json.loads(response.text)
                if "rank_token" not in data or data["rank_token"] == "" or "page_token" not in data or data["page_token"] == "":
                    rank_token = ""
                    page_token = ""
                    hasNextPage = False
                else:
                    rank_token = data["rank_token"]
                    page_token = data["page_token"]
                    hasNextPage = True

                if "threads" not in data:
                    logger.warning(f'关键词[{keyword}]没有帖子数据')
                else:
                    threads = data["threads"]
                    for item in threads:
                        post_id = item['id']
                        user_id = item['thread_items'][0]['post']['user']['pk']
                        user_name = item['thread_items'][0]['post']['user']['username']
                        text = ""
                        images = ""
                        video = ""
                        like_count = item['thread_items'][0]['post']['like_count']
                        mention_count = 0
                        quote_count = item['thread_items'][0]['post']['text_post_app_info']['quote_count']
                        reply_count = item['thread_items'][0]['post']['text_post_app_info']['direct_reply_count']
                        repost_count = item['thread_items'][0]['post']['text_post_app_info']['repost_count']
                        reshare_count = item['thread_items'][0]['post']['text_post_app_info'].get('reshare_count', 0)
                        permalink = item['thread_items'][0]['post']['permalink']
                        taken_at = datetime.fromtimestamp(item['thread_items'][0]['post']['taken_at'])

                        if "text" in item['thread_items'][0]['post']['caption'] and item['thread_items'][0]['post']['caption']['text'] != None:
                            text = item['thread_items'][0]['post']['caption']['text']

                        if "mention_count" in item['thread_items'][0]['post']['text_post_app_info']:
                            mention_count = item['thread_items'][0]['post']['text_post_app_info']['mention_count']

                        image_list = []
                        if "carousel_media" in item['thread_items'][0]['post']:
                            for media in item['thread_items'][0]['post']['carousel_media']:
                                image_list.append(media['image_versions2']['candidates'][0]['url'])
                            images = json.dumps(image_list)
                        elif "image_versions2" in item['thread_items'][0]['post'] and 'candidates' in item['thread_items'][0]['post']['image_versions2'] and len(item['thread_items'][0]['post']['image_versions2']['candidates']) > 0:
                            image_list.append(item['thread_items'][0]['post']['image_versions2']['candidates'][0]['url'])
                            images = json.dumps(image_list)

                        if "video_versions" in item['thread_items'][0]['post'] and len(item['thread_items'][0]['post']['video_versions']) > 0:
                            video = item['thread_items'][0]['post']['video_versions'][0]['url']

                        logger.info(f"关键词[{keyword}]发现用户[{user_name}]及帖子[{post_id}]")

                        if not self.db.post_exists(post_id):
                            self.db.insert_post(user_id, post_id, text, images, video, like_count, mention_count, quote_count, reply_count, repost_count, reshare_count, permalink, taken_at)

                        # 获取用户详情
                        if not self.db.user_exists(user_id):
                            await self.getUserProfile(user_id, user_name)

                        # 获取帖子评论及用户
                        if reply_count > 0:
                            await self.getCommentsUser(post_id)

            except requests.exceptions.RequestException as e:
                raise Exception(f"获取[{keyword}]的搜索结果发生错误:{e}")
            
            await asyncio.sleep(random.uniform(self.delay, self.delay + 10))

    # 获取作品评论用户列表
    async def getCommentsUser(self, post_id):
        logger.info(f'开始采集帖子[{post_id}]的评论用户')
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = f"https://i.instagram.com/api/v1/text_feed/{post_id}/replies/"

        params = {
            "deeplink_fb_tifu": "false",
            "is_app_start": "false",
            "deeplink_ig_tifu": "false"
        }

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-c7e30dd9-6350-4b68-a3ac-60d67ad2127f-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "873c78bbf5b48072533688c4dfe047ad5f7d6774851be63e2c609a6ed0f0957c",
            "x-ig-www-claim": "hmac.AR0JoLlXUGrLbilcEM402EAZnxT2u-EAa7nQR0CE9BVWfuOK",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-ig-transfer-encoding": "chunked",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "ef19f395-4663-4e2e-8695-317050bc4e92",
            "x-ig-family-device-id": "da6b602e-ed2f-4e7b-9052-5f1d9cc6dfa4",
            "x-ig-android-id": "android-af1261f2f3d61aba",
            "x-ig-timezone-offset": "28800",
            "x-ig-nav-chain": "BcnRoute:ig_text_feed_timeline:1:cold_start:1744385489.737::,SearchDestination:ig_text_search_nullstate:9:button:1744385981.44::,BcnRoute:ig_text_search_serp_top:10:button:1744385981.45::,BcnRoute:ig_text_search_typeahead:11:button:1744386007.870::,BcnRoute:ig_text_search_serp_top:12:button:1744386013.860:11:3608451474153473423,PermalinkDestination:ig_text_post_permalink:13:button:1744386024.793::",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "3419628305025917",
            "priority": "u=3",
            "user-agent": "Barcelona 361.3.0.53.106 Android (32/12; 640dpi; 1440x2560; Xiaomi; 24031PN0DC; aurora; Xiaomi; zh_CN; 676217033)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id['value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "VLL," + ds_user_id['value'] + ",1775922025:01f7b92cca494a69ce99904f6f1e5bfa289ee38b8d4d226f04c14913621db8a2ebd1ba6d",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        paging_token = ""
        hasNextPage = True

        while hasNextPage and self.is_running_fn():
            if paging_token != "":
                params["paging_token"] = paging_token

            url_params = urlencode(params)
            url = f"{api_url}?{url_params}"

            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
                response = requests.get(url, headers=headers, timeout=30)
                if response.ok:
                    resp_headers = response.headers
                    self.direct_region_hint = resp_headers.get('ig-set-ig-u-ig-direct-region-hint')
                    self.u_rur = resp_headers.get('ig-set-ig-u-rur')

                    headers["ig-u-ig-direct-region-hint"] = self.direct_region_hint
                    headers["ig-u-rur"] = self.u_rur

                    data = json.loads(response.text)

                    if "paging_tokens" not in data or "downwards" not in data["paging_tokens"] or data["paging_tokens"]["downwards"] == "" or len(data['reply_threads']) < 12:
                        paging_token = ""
                        hasNextPage = False
                    else:
                        paging_token = data["paging_tokens"]['downwards']

                    if "target_post_id" in data:
                        post_id = data['target_post_id']

                        for item in data['reply_threads']:
                            user_id = item['thread_items'][0]['post']['user']['pk']
                            comment_id = item['thread_items'][0]['post']['pk']
                            text = ""
                            images = ""
                            video = ""
                            like_count = item['thread_items'][0]['post']['like_count']
                            reply_count = item['thread_items'][0]['post']['text_post_app_info']['direct_reply_count']
                            repost_count = item['thread_items'][0]['post']['text_post_app_info']['repost_count']
                            reshare_count = item['thread_items'][0]['post']['text_post_app_info'].get('reshare_count', 0)
                            taken_at = datetime.fromtimestamp(item['thread_items'][0]['post']['taken_at'])

                            if "caption" in item['thread_items'][0]['post'] and "text" in item['thread_items'][0]['post']['caption'] and item['thread_items'][0]['post']['caption']['text'] != None:
                                text = item['thread_items'][0]['post']['caption']['text']

                            image_list = []
                            if "carousel_media" in item['thread_items'][0]['post']:
                                for media in item['thread_items'][0]['post']['carousel_media']:
                                    image_list.append(media['image_versions2']['candidates'][0]['url'])
                                images = json.dumps(image_list)
                            elif "image_versions2" in item['thread_items'][0]['post'] and 'candidates' in item['thread_items'][0]['post']['image_versions2'] and len(item['thread_items'][0]['post']['image_versions2']['candidates']) > 0:
                                image_list.append(item['thread_items'][0]['post']['image_versions2']['candidates'][0]['url'])
                                images = json.dumps(image_list)

                            if "video_versions" in item['thread_items'][0]['post'] and len(item['thread_items'][0]['post']['video_versions']) > 0:
                                video = item['thread_items'][0]['post']['video_versions'][0]['url']

                            user_name = item['thread_items'][0]['post']['user']['username']
                            
                            logger.info(f"帖子[{post_id}]评论用户: {user_name}")

                            if not self.db.comment_exists(comment_id):
                                self.db.insert_comment(user_id, post_id, comment_id, text, images, video, like_count, reply_count, repost_count, reshare_count, taken_at)

                            if not self.db.user_exists(user_id):
                                await self.getUserProfile(user_id, user_name)

            except requests.exceptions.RequestException as e:
                raise Exception(f"获取作品评论用户列表的请求失败({e})")

            await asyncio.sleep(random.uniform(self.delay, self.delay + 10))

    # 获取帖子作者的粉丝列表
    async def getUserFans(self, user_name, user_id):
        logger.info(f'开始采集用户[{user_name}]的粉丝用户')
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/"

        params = {
            "include_user_count": "true",
            "search_surface": "barcelona_following_graph_page"
        }

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-c7e30dd9-6350-4b68-a3ac-60d67ad2127f-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "873c78bbf5b48072533688c4dfe047ad5f7d6774851be63e2c609a6ed0f0957c",
            "x-ig-www-claim": "hmac.AR0JoLlXUGrLbilcEM402EAZnxT2u-EAa7nQR0CE9BVWfuOK",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "ef19f395-4663-4e2e-8695-317050bc4e92",
            "x-ig-family-device-id": "da6b602e-ed2f-4e7b-9052-5f1d9cc6dfa4",
            "x-ig-android-id": "android-af1261f2f3d61aba",
            "x-ig-timezone-offset": "28800",
            "x-ig-nav-chain": "BcnRoute:ig_text_feed_timeline:1:cold_start:1744385489.737::,SearchDestination:ig_text_search_nullstate:2:button:1744385539.523::,BcnRoute:ig_text_search_typeahead:3:button:1744385545.79::,BcnRoute:ig_text_search_serp_top:4:button:1744385562.6:11:3608481483795444749,PermalinkDestination:ig_text_post_permalink:5:button:1744385636.540:318:3608481483795444749,ProfileDestination:ig_text_feed_profile:7:button:1744385795.275::,FollowingGraphDestination:ig_text_feed_follow_list:8:button:1744385816.167::",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "3419628305025917",
            "priority": "u=3",
            "user-agent": "Barcelona 361.3.0.53.106 Android (32/12; 640dpi; 1440x2560; Xiaomi; 24031PN0DC; aurora; Xiaomi; zh_CN; 676217033)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id['value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "VLL," + ds_user_id['value'] + ",1775922025:01f7b92cca494a69ce99904f6f1e5bfa289ee38b8d4d226f04c14913621db8a2ebd1ba6d",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        max_id = ""
        hasNextPage = True

        while hasNextPage and self.is_running_fn():
            if max_id != "":
                params["max_id"] = max_id

            url_params = urlencode(params)
            url = f"{api_url}?{url_params}"

            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                resp_headers = response.headers
                self.direct_region_hint = resp_headers.get('ig-set-ig-u-ig-direct-region-hint')
                self.u_rur = resp_headers.get('ig-set-ig-u-rur')

                headers["ig-u-ig-direct-region-hint"] = self.direct_region_hint
                headers["ig-u-rur"] = self.u_rur

                data = json.loads(response.text)

                if "next_max_id" not in data or data["next_max_id"] == "":
                    max_id = ""
                    hasNextPage = False
                else:
                    max_id = data["next_max_id"]
                numer = len(data['users'])
                logger.info(f'用户[{user_name}]发现{numer}个粉丝用户')
                for item in data['users']:
                    follower_user_id = item['pk']
                    follower_user_name = item['username']
                    logger.info(f'用户[{user_name}]粉丝: {follower_user_name}')

                    if not self.db.follower_exists(user_id, follower_user_id):
                        self.db.insert_follower(user_id, follower_user_id)

                    if not self.db.user_exists(follower_user_id):
                        await self.getUserProfile(follower_user_id, follower_user_name)

            except requests.exceptions.RequestException as e:
                raise Exception(f"获取用户[{user_name}]粉丝请求失败({e})")

            await asyncio.sleep(random.uniform(self.delay, self.delay + 10))

    # 获取作者信息
    async def getUserProfile(self, user_id, user_name):
        logger.info(f'开始采集用户[{user_name}]的详情')
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        url = f"https://i.instagram.com/api/v1/users/{user_id}/info/?entry_point=profile&from_module=ProfileViewModel"

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-c7e30dd9-6350-4b68-a3ac-60d67ad2127f-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "873c78bbf5b48072533688c4dfe047ad5f7d6774851be63e2c609a6ed0f0957c",
            "x-ig-www-claim": "hmac.AR0JoLlXUGrLbilcEM402EAZnxT2u-EAa7nQR0CE9BVWfuOK",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "ef19f395-4663-4e2e-8695-317050bc4e92",
            "x-ig-family-device-id": "da6b602e-ed2f-4e7b-9052-5f1d9cc6dfa4",
            "x-ig-android-id": "android-af1261f2f3d61aba",
            "x-ig-timezone-offset": "28800",
            "x-ig-nav-chain": "BcnRoute:ig_text_feed_timeline:1:cold_start:1744638208.809:318:3610384082619249640:1744638208.809,ProfileDestination:ig_text_feed_profile:2:button:1744638254.276:::1744638254.276",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "3419628305025917",
            "priority": "u=3",
            "user-agent": "Barcelona 361.3.0.53.106 Android (32/12; 640dpi; 1440x2560; Xiaomi; 24031PN0DC; aurora; Xiaomi; zh_CN; 676217033)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id['value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "VLL," + ds_user_id['value'] + ",1775922025:01f7b92cca494a69ce99904f6f1e5bfa289ee38b8d4d226f04c14913621db8a2ebd1ba6d",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        try:
            # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = json.loads(response.text)
            user = data["user"]
            user_id = user["pk"]
            name = user["username"]
            full_name = user["full_name"]
            biography = user["biography"]
            follower_count = user["follower_count"]
            following_count = user.get("following_count", 0)
            profile_pic_url = user["profile_pic_url"]

            if not self.db.user_exists(user_id):
                self.db.insert_user(user_id, name, full_name, biography, profile_pic_url, follower_count, following_count)

        except requests.exceptions.RequestException as e:
            raise Exception(f"获取用户[{user_name}]详情请求失败({e})")

        await asyncio.sleep(random.uniform(self.delay, self.delay + 10))

    # 获取用户帖子
    async def getUserPost(self, user_id, user_name):
        logger.info(f'开始采集用户[{user_name}]的帖子')
        auth = self.getBearerAuth()
        ds_user_id = next((cookie for cookie in self.cookies if cookie['name'] == "ds_user_id"), None)
        mid = next((cookie for cookie in self.cookies if cookie['name'] == "mid"), None)
        timestamp = "{:.3f}".format(time.time())

        api_url = f"https://i.instagram.com/api/v1/text_feed/{user_id}/profile/?exclude_reposts=true&is_app_start=false"

        headers = {
            "x-ig-app-locale": "zh_CN",
            "x-ig-device-locale": "zh_CN",
            "x-ig-mapped-locale": "zh_CN",
            "x-pigeon-session-id": "UFS-c7e30dd9-6350-4b68-a3ac-60d67ad2127f-0",
            "x-pigeon-rawclienttime": timestamp,
            "x-ig-bandwidth-speed-kbps": "5764.000",
            "x-ig-bandwidth-totalbytes-b": "4795860",
            "x-ig-bandwidth-totaltime-ms": "609",
            "x-bloks-version-id": "873c78bbf5b48072533688c4dfe047ad5f7d6774851be63e2c609a6ed0f0957c",
            "x-ig-www-claim": "hmac.AR0JoLlXUGrLbilcEM402EAZnxT2u-EAa7nQR0CE9BVWfuOK",
            "x-bloks-prism-button-version": "CONTROL",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-ax-base-colors-enabled": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": "ef19f395-4663-4e2e-8695-317050bc4e92",
            "x-ig-family-device-id": "da6b602e-ed2f-4e7b-9052-5f1d9cc6dfa4",
            "x-ig-android-id": "android-af1261f2f3d61aba",
            "x-ig-timezone-offset": "28800",
            "x-ig-nav-chain": "BcnRoute:ig_text_feed_timeline:1:cold_start:1744721028.6:11:3610635140357001607:1744723478.99,PermalinkDestination:ig_text_post_permalink:21:button:1744723485.579:318:3610635140357001607:1744724439.299,ProfileDestination:ig_text_feed_profile:23:button:1744724964.767:::1744724964.767",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTv10=",
            "x-ig-app-id": "3419628305025917",
            "priority": "u=3",
            "user-agent": "Barcelona 361.3.0.53.106 Android (32/12; 640dpi; 1440x2560; Xiaomi; 24031PN0DC; aurora; Xiaomi; zh_CN; 676217033)",
            "accept-language": "zh-CN, en-US",
            "authorization": auth,
            "x-mid": mid['value'],
            "ig-u-ig-direct-region-hint": "EAG," + ds_user_id['value'] + ",1766216854:01f7d9d36db73f01dee6bfdb4ff3158a788ee5da92fb7b16a8b50b0f561dc80498d288c2",
            "ig-u-ds-user-id": ds_user_id['value'],
            "ig-u-rur": "VLL," + ds_user_id['value'] + ",1775922025:01f7b92cca494a69ce99904f6f1e5bfa289ee38b8d4d226f04c14913621db8a2ebd1ba6d",
            "ig-intended-user-id": ds_user_id['value'],
            "accept-encoding": "gzip",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True"
        }

        max_id = ""
        hasNextPage = True

        while hasNextPage and self.is_running_fn():
            if max_id != "":
                url = f'{api_url}&max_id={max_id}'
            else:
                url = api_url
            try:
                # response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
                response = requests.get(url, headers=headers, timeout=30)

                resp_headers = response.headers
                self.direct_region_hint = resp_headers.get('ig-set-ig-u-ig-direct-region-hint')
                self.u_rur = resp_headers.get('ig-set-ig-u-rur')

                headers["ig-u-ig-direct-region-hint"] = self.direct_region_hint
                headers["ig-u-rur"] = self.u_rur

                data = json.loads(response.text)

                if "next_max_id" not in data or data["next_max_id"] == "" or len(data["threads"]) < 4:
                    max_id = ""
                    hasNextPage = False
                else:
                    max_id = data["next_max_id"]
                numer = len(data['threads'])
                logger.info(f'用户[{user_name}]发现{numer}个帖子')
                for item in data['threads']:
                    post_id = item['id']
                    user_id = item['thread_items'][0]['post']['user']['pk']
                    text = ""
                    images = ""
                    video = ""
                    like_count = item['thread_items'][0]['post']['like_count']
                    mention_count = 0
                    quote_count = item['thread_items'][0]['post']['text_post_app_info']['quote_count']
                    reply_count = item['thread_items'][0]['post']['text_post_app_info']['direct_reply_count']
                    repost_count = item['thread_items'][0]['post']['text_post_app_info']['repost_count']
                    reshare_count = item['thread_items'][0]['post']['text_post_app_info'].get('reshare_count', 0)
                    permalink = item['thread_items'][0]['post']['permalink']
                    taken_at = datetime.fromtimestamp(item['thread_items'][0]['post']['taken_at'])

                    if "mention_count" in item['thread_items'][0]['post']['text_post_app_info']:
                        mention_count = item['thread_items'][0]['post']['text_post_app_info']['mention_count']

                    if "text" in item['thread_items'][0]['post']['caption'] and item['thread_items'][0]['post']['caption']['text'] != "":
                        text = item['thread_items'][0]['post']['caption']['text']
                        
                    image_list = []
                    if "carousel_media" in item['thread_items'][0]['post']:
                        for media in item['thread_items'][0]['post']['carousel_media']:
                            image_list.append(media['image_versions2']['candidates'][0]['url'])
                        images = json.dumps(image_list)
                    elif "image_versions2" in item['thread_items'][0]['post'] and 'candidates' in item['thread_items'][0]['post']['image_versions2'] and len(item['thread_items'][0]['post']['image_versions2']['candidates']) > 0:
                        image_list.append(item['thread_items'][0]['post']['image_versions2']['candidates'][0]['url'])
                        images = json.dumps(image_list)

                    if "video_versions" in item['thread_items'][0]['post'] and len(item['thread_items'][0]['post']['video_versions']) > 0:
                        video = item['thread_items'][0]['post']['video_versions'][0]['url']

                    logger.info(f'用户[{user_name}]的帖子:[{post_id}]')

                    if not self.db.post_exists(post_id):
                        self.db.insert_post(user_id, post_id, text, images, video, like_count, mention_count, quote_count, reply_count, repost_count, reshare_count, permalink, taken_at)

                    if reply_count > 0:
                        await self.getCommentsUser(post_id)

            except requests.exceptions.RequestException as e:
                raise Exception(f"获取用户[{user_name}]帖子列表请求失败({e})")

            await asyncio.sleep(random.uniform(self.delay, self.delay + 10))

    # 销毁资源
    async def close(self):
        if self.browser:
            await self.browser.close()
