import asyncio
import os
import json
import sys
from PyQt5.QtWidgets import QApplication

from Threads_lists import show_task_order_window_async
from Threads_status import StatusWindow

import aiohttp
from Threadsmain import Crawler


def getCookie():
    if not os.path.exists("threads.json"):
        return None
    with open("threads.json", "r") as f:
        try:
            return json.load(f)
        except:
            return None
def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            return await response.json()


async def GetHtmluser(data):
    UserLists = []
    getuser_num = 10

    async def fetch_with_retry(user_id, max_retries=3):
        for attempt in range(max_retries):
            try:
                url = f"https://th.ry188.vip/API/GetUserList.aspx?Count={getuser_num}&Id={user_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=15) as response:
                        UserRequests = await response.json()
                        return [user["name"] for user in UserRequests.get("UserList", [])]
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    print(f"用户 {user_id} 请求超时，已尝试 {max_retries} 次")
                    return []
                await asyncio.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                print(f"用户 {user_id} 请求失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    return []
                await asyncio.sleep(1)
        return []

    # 限制并发数量，避免过多请求
    semaphore = asyncio.Semaphore(10)  # 同时最多10个请求

    async def limited_fetch(user_id):
        async with semaphore:
            return await fetch_with_retry(user_id)

    tasks = []
    for user_info in data["UserInFIdList"]:
        tasks.append(limited_fetch(user_info["Id"]))

    results = await asyncio.gather(*tasks)

    for result in results:
        UserLists.extend(result)

    return UserLists


async def main(content0,content1):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    cookies = getCookie()  # 从文件读取cookies
    data = await fetch_data(f"https://th.ry188.vip/API/GetData.aspx?Account={content1}")

    home_enable = parse_bool(data["SendData"]["ConfigDatas"]["Home_IsEnableBrowse"])  # 是否主頁留言
    key_enable = parse_bool(data["SendData"]["ConfigDatas"]["IsKey"])  # 是否关键字
    fawen_enable = parse_bool(data["SendData"]["ConfigDatas"]["IsPersonalSend"])  # 是否发文
    print(home_enable,key_enable,fawen_enable)
    config = {
        "Home_IsEnableBrowse": home_enable,
        "IsKey": key_enable,
        "IsPersonalSend": fawen_enable
    }

    # 显示任务顺序设置窗口并获取用户设置的顺序，传递配置参数
    task_order_data = show_task_order_window_async(config)
    if task_order_data is None:
        print("用户取消了任务顺序设置")
        return  # 或者进行其他处理

    task_order = task_order_data.get('order', [])
    rest_times = task_order_data.get('rest_times', {})
    print(task_order, rest_times)

    userslists = await GetHtmluser(data)
    print(f"成功获取 {len(userslists)} 个用户")
    crawler = Crawler(cookies, data,content0,content1,userslists,task_order,rest_times)
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
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        app.setApplicationName("Threads自動化脚本")
        status_window = StatusWindow()
        status_window.show()
        # 关键修改：将状态窗口传递给crawler对象
        crawler.status_window = status_window

        QApplication.processEvents()  # 确保UI更新
        await crawler.start()
    finally:
        # 确保关闭浏览器
        pass
    return crawler