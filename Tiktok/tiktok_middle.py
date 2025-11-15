
import asyncio  # 异步I/O
import os  # 系统操作
import time  # 时间操作
from urllib.parse import urlencode, quote  # URL编码

from tiktok_method import MethodCrawler
from tiktok_login import LoginWebCrawler
from TokenManager import TokenManager
# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

class TiktokCrawler:

    # 从配置文件中获取抖音的请求头
    async def get_douyin_headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            # 'cookie': get_fresh_cookie(),
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }
        return headers

    # 获取单个作品数据
    async def fetch_video_comments(self, aweme_id: str):
        # 获取实时Cookie
        headers = await self.get_douyin_headers()
        cookies = TokenManager().getCookie()
        crawler = LoginWebCrawler(cookies)
        if await self.login_cookies(cookies,crawler):
            # 创建一个基础爬虫
            response = await MethodCrawler.get_all_comments(headers,aweme_id)
            return response
        return None

    # 登录验证
    async def login_cookies(self, cookies: list, crawler: LoginWebCrawler):
        # 确保登录成功
        if cookies is None or not await crawler.check_cookies_valid():
            print("需要重新登录...")
            if await crawler.perform_browser_login():
                return True
            else:
                return False
        else:
            return False
    "-------------------------------------------------------utils接口列表-------------------------------------------------------"

    # 生成真实msToken
    async def gen_real_msToken(self, ):
        result = {
            "msToken": TokenManager().gen_real_msToken()
        }
        return result

    # # 生成ttwid
    # async def gen_ttwid(self, ):
    #     result = {
    #         "ttwid": TokenManager().gen_ttwid()
    #     }
    #     return result

    # 生成verify_fp
    async def gen_verify_fp(self, ):
        result = {
            "verify_fp": TokenManager.gen_verify_fp()
        }
        return result

    # # 生成s_v_web_id
    # async def gen_s_v_web_id(self, ):
    #     result = {
    #         "s_v_web_id": TokenManager.gen_s_v_web_id()
    #     }
    #     return result

    # 使用接口地址生成Xb参数
    async def get_x_bogus(self, ):
        result = {
            "x_bogus":TokenManager.generate_x_bogus()
        }
        return result



    async def main(self):
        """-------------------------------------------------------handler接口列表-------------------------------------------------------"""

        # 获取指定用户的信息
        # sec_user_id = "MS4wLjABAAAAW9FWcqS7RdQAWPd2AA5fL_ilmqsIFUCQ_Iym6Yh9_cUa6ZRqVLjVQSUjlHrfXY1Y"
        # result = await self.handler_user_profile(sec_user_id)
        # print(result)

        # 获取单个视频评论数据
        aweme_id = "7552834568135527710"
        result = await self.fetch_video_comments(aweme_id)
        print(result)

        # 占位
        pass


if __name__ == "__main__":
    # 初始化
    TiktokCrawler = TiktokCrawler()

    # 开始时间
    start = time.time()

    asyncio.run(TiktokCrawler.main())

    # 结束时间
    end = time.time()
    print(f"耗时：{end - start}")
