import os
import json
import sys

import aiohttp
from PyQt5.QtWidgets import QApplication
# from Threads_status import StatusWindow
import requests

from FBmain import Crawler


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


async def main(content1):
    cookies = getCookie()  # 从文件读取cookies
    data = await fetch_data(f"http://aj.ry188.vip/API/GetAppConfig.aspx?Account={content1}")

    crawler = Crawler(cookies,data,content1)

    # 确保登录成功
    if cookies is None or not await crawler.check_cookies_valid():
        try:
            # 尝试GUI登录
            await crawler.login_with_gui()
            while 1:
                if not crawler.is_logged_in:
                    print("登录失败，无法继续执行任务")
                    await crawler.login_with_gui()
                    # return  # 直接返回，不再执行后续任务
                else:
                    break
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return  # 登录失败时直接返回
    else:
        # 如果cookies有效，标记为已登录
        crawler.is_logged_in = True
        print("使用有效cookies登录成功")

    try:
        # app = QApplication.instance()
        # if not app:
        #     app = QApplication(sys.argv)
        # app.setApplicationName("Threads自動化脚本")
        # status_window = StatusWindow()
        # status_window.show()
        # # 关键修改：将状态窗口传递给crawler对象
        # crawler.status_window = status_window

        QApplication.processEvents()  # 确保UI更新
        await crawler.start()
    finally:
        # 确保关闭浏览器
        pass
    return crawler