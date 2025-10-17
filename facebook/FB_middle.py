import os
import json
import sys

import aiohttp
from PyQt5.QtWidgets import QApplication
from FBmain import Crawler
from FB_status import StatusWindow


def getCookie():
    if not os.path.exists("FB.json"):
        return None
    with open("FB.json", "r") as f:
        try:
            return json.load(f)
        except:
            return None

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            return await response.json()

def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')


async def main(params=None):
    cookies = getCookie()  # 从文件读取cookies

    # 每次操作都创建新的crawler实例
    crawler = Crawler(cookies, params)

    # 确保登录成功
    if cookies is None or not await crawler.check_cookies_valid():
        try:
            # 尝试GUI登录
            await crawler.login_with_gui()
            while 1:
                if not crawler.is_logged_in:
                    print("登录失败，无法继续执行任务")
                    await crawler.login_with_gui()
                else:
                    break
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return None
    else:
        crawler.is_logged_in = True
        print("使用有效cookies登录成功")

    try:
        await crawler.start()
        return crawler
    except Exception as e:
        print(f"执行过程中出现错误: {str(e)}")
        return None
    finally:
        # 确保清理资源
        pass