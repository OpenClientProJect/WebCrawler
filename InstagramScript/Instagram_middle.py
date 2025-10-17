import asyncio
import datetime
import os
import json
import sys

import requests
from PyQt5.QtWidgets import QApplication
from Instagram_status import StatusWindow

import aiohttp
from Instagrammain import Crawler
from Instagram_lists import show_task_order_window_async

def getCookie():
    if not os.path.exists("instagram.json"):
        return None
    with open("instagram.json", "r") as f:
        try:
            return json.load(f)
        except:
            return None

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            return await response.json()


async def GetHtmluser(data, desired_count):
    UserLists = []
    remaining = desired_count  # 剩余需要获取的用户数

    async with aiohttp.ClientSession() as session:
        # 遍历所有ID，直到满足需求或没有更多ID
        for user_info in data["UserInFIdList"]:
            if remaining <= 0:
                break

            # 计算本次请求需要获取的数量
            current_request = min(remaining, 100)  # 假设单次请求最大100

            url = f"https://ig.ry188.vip/API/GetUserList.aspx?Count={current_request}&Id={user_info['Id']}"
            print(url)
            UserRequests = await fetch_data(url)
            # UserRequests = requests.get(url).json()
            # 获取实际返回的用户数
            actual_count = len(UserRequests["UserList"])
            for user in UserRequests["UserList"]:
                UserLists.append(user["user_name"])

            # 更新剩余需要获取的数量
            remaining -= actual_count

            # 如果实际获取的数量少于请求的数量，说明该ID没有更多用户
            if actual_count < current_request:
                continue  # 继续尝试下一个ID

    return UserLists

def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')


def load_progress(account):
    """从文件加载处理进度"""
    filename = f"{account}_progress.json"
    if not os.path.exists(filename):
        print(f"无进度文件 {filename}")
        return None, 0

    try:
        with open(filename, 'r') as f:
            progress_data = json.load(f)
        print(f"从 {filename} 加载进度: 位置 {progress_data['position']}/{len(progress_data['users'])}")
        return progress_data["users"], progress_data["position"]
    except:
        print(f"加载进度文件 {filename} 失败")
        return None, 0


async def main(content0,content1):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    cookies = getCookie()  # 从文件读取cookies
    data = await fetch_data(f"https://ig.ry188.vip/API/GetData.aspx?Account={content1}")

    # 解析配置
    home_enable = parse_bool(data["SendData"]["ConfigDatas"]["Home_IsEnableBrowse"])  # 是否首页浏览
    key_enable = parse_bool(data["SendData"]["ConfigDatas"]["Key_IsEnableKey"])  # 是否启用关键字
    hudong_enable = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsHuDong"])  # 是否用户互动

    # 创建配置字典
    config = {
        "Home_IsEnableBrowse": home_enable,
        "Key_IsEnableKey": key_enable,
        "HuDong_IsHuDong": hudong_enable
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


    # 检查是否继续上一次
    continue_last = parse_bool(data["SendData"]["ConfigDatas"]["HuDong_IsResetProgress"])
    print(f"继续上一次: {continue_last}")

    app.setApplicationName("Instagram自動化脚本")
    status_window = StatusWindow()
    status_window.show()

    # 处理计划时间
    if scheduled_time != "0":
        await handle_scheduled_execution(status_window, scheduled_time, content0, content1, cookies, data,
                                         task_order, rest_times, completion_times, continue_last)
    else:
        # 立即执行
        await execute_tasks_immediately(status_window, content0, content1, cookies, data,
                                        task_order, rest_times, completion_times, continue_last)


async def handle_scheduled_execution(status_window, scheduled_time, content0, content1, cookies, data,
                                     task_order, rest_times, completion_times, continue_last):
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
                                            task_order, rest_times, completion_times, continue_last)

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
                                    task_order, rest_times, completion_times, continue_last):
    """立即执行任务"""
    status_window.update_signal.emit("提前獲取用戶數據耐心等待...")
    await asyncio.sleep(1)

    users = []
    start_position = 0
    desired_count = int(data["SendData"]["ConfigDatas"]["HuDong_GetUserCount"])
    if continue_last:
        # 尝试加载进度
        users, start_position = load_progress(content1)
    if not users:
        users = await GetHtmluser(data, desired_count)
    cookies = getCookie()
    crawler = Crawler(cookies, data, users, start_position, content0, content1, task_order, rest_times)
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