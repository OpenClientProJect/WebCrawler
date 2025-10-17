import asyncio
import datetime
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
    completion_times = task_order_data.get('completion_times', {})
    scheduled_time = task_order_data.get('scheduled_time', "0")
    print(f"任务顺序: {task_order}, 休息时间: {rest_times}, 完成时间: {completion_times}, 计划时间: {scheduled_time}")

    app.setApplicationName("Threads自動化脚本")
    status_window = StatusWindow()
    status_window.show()

    # 处理计划时间
    if scheduled_time != "0":
        await handle_scheduled_execution(status_window, scheduled_time, content0, content1, cookies, data,
                                         task_order, rest_times, completion_times)
    else:
        # 立即执行
        await execute_tasks_immediately(status_window, content0, content1, cookies, data,
                                        task_order, rest_times, completion_times)

async def handle_scheduled_execution(status_window, scheduled_time, content0, content1, cookies, data,
                                     task_order, rest_times, completion_times):
    """处理计划时间执行"""
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")

        # 修改判断条件：使用时间戳比较而不是字符串相等
        current_timestamp = datetime.datetime.now()
        scheduled_hour, scheduled_minute = map(int, scheduled_time.split(':'))
        scheduled_today = current_timestamp.replace(hour=scheduled_hour, minute=scheduled_minute, second=0,
                                                    microsecond=0)

        # 如果今天的时间已经过去，就计算明天的时间
        if current_timestamp > scheduled_today:
            scheduled_tomorrow = scheduled_today + datetime.timedelta(days=1)
            time_diff = scheduled_tomorrow - current_timestamp
        else:
            time_diff = scheduled_today - current_timestamp

        wait_seconds = time_diff.total_seconds()

        # 当时间差小于等于5s时开始执行
        if wait_seconds <= 5:
            # 隐藏倒计时显示
            if hasattr(status_window, 'plan_countdown_signal'):
                status_window.plan_countdown_signal.emit(0)

            status_window.update_signal.emit(f"到達計劃時間 {scheduled_time}，開始執行任務...")
            await asyncio.sleep(1)  # 给UI更新时间

            await execute_tasks_immediately(status_window, content0, content1, cookies, data,
                                            task_order, rest_times, completion_times)

            # 任务完成后，等待到第二天再检查
            status_window.update_signal.emit("任務完成，等待第二天同一時間再次執行...")
            await asyncio.sleep(1)

            # 等待一段时间确保不会立即再次触发
            await asyncio.sleep(5)

            # 重新计算下一次执行时间
            continue

        # 使用倒计时机制显示等待信息
        if hasattr(status_window, 'plan_countdown_signal'):
            status_window.plan_countdown_signal.emit(int(wait_seconds))
        else:
            # 回退到原来的显示方式
            if wait_seconds < 60:
                display_text = f"等待計劃時間 {scheduled_time}，剩餘 {int(wait_seconds)}秒"
            elif wait_seconds < 3600:
                minutes = int(wait_seconds // 60)
                seconds = int(wait_seconds % 60)
                display_text = f"等待計劃時間 {scheduled_time}，剩餘 {minutes}分{seconds}秒"
            else:
                hours = int(wait_seconds // 3600)
                minutes = int((wait_seconds % 3600) // 60)
                display_text = f"等待計劃時間 {scheduled_time}，剩餘 {hours}小時{minutes}分"
            status_window.update_signal.emit(display_text)

        # 使用较长的检查间隔，减少频率
        await asyncio.sleep(5)  # 改为30秒检查一次


async def execute_tasks_immediately(status_window, content0, content1, cookies, data,
                                    task_order, rest_times, completion_times):
    """立即执行任务"""
    status_window.update_signal.emit("提前獲取用戶數據耐心等待...")
    await asyncio.sleep(1)
    userslists = await GetHtmluser(data)
    print(f"成功获取 {len(userslists)} 个用户")

    cookies = getCookie()
    crawler = Crawler(cookies, data, content0, content1, userslists, task_order, rest_times)
    crawler.completion_times = completion_times

    # 确保登录成功
    if cookies is None or not await crawler.check_cookies_valid():
        try:
            await crawler.login_with_gui()
            while True:
                if not crawler.is_logged_in:
                    print("登录失败，无法继续执行任务")
                    await crawler.login_with_gui()
                else:
                    break
        except Exception as e:
            print(f"登录失败: {str(e)}")
            status_window.update_signal.emit(f"登录失败: {str(e)}")
            await asyncio.sleep(1)
            return
    else:
        crawler.is_logged_in = True
        print("使用有效cookies登录成功")

    try:
        crawler.status_window = status_window
        QApplication.processEvents()
        await crawler.start()

        # 任务完成后清除进度
        status_window.update_signal.emit("任务执行完成！")
        await asyncio.sleep(1)

    except Exception as e:
        # status_window.update_signal.emit(f"任务执行失败: {str(e)}")
        await asyncio.sleep(1)
        print(f"任务执行失败: {str(e)}")
    finally:
        # 确保资源清理
        pass