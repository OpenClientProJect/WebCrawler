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


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            return await response.json()


async def GetHtmluser(data, messags_types, messags_types2):
    # 检查是否获取全部用户
    get_all = parse_bool(data["SendData"]["SendConfigs"]["IsSendAll"])

    if get_all:
        # 获取全部用户模式
        print("获取全部用户模式：忽略数量限制，获取所有可用用户")
        UserLists = []

        # 遍历所有ID源（群组/页面/支持列表）
        for i in range(len(data[messags_types2])):
            current_id = data[messags_types2][i]['Id']
            pages = 1
            print(f"\n开始处理 ID源 {i + 1}/{len(data[messags_types2])}: {current_id}")

            while True:
                url = f"https://cj.ry188.vip/api/GetUserDatanew.aspx?T={messags_types}&P={pages}&Z=10&Id={current_id}"
                print(f"正在请求: {url}")

                try:
                    response = await fetch_data(url)

                    # 检查是否返回有效用户列表
                    if "UserList" not in response or not response["UserList"]:
                        print(f"ID {current_id} 第{pages}页无数据，结束此ID源")
                        break

                    # 添加本页所有用户ID
                    for user in response["UserList"]:
                        UserLists.append(user["userid"])

                    print(f"本页获取 {len(response['UserList'])} 个用户，总计 {len(UserLists)} 个用户")

                    # 检查是否最后一页（不足10人）
                    if len(response["UserList"]) < 10:
                        print(f"ID {current_id} 最后一页数据不足10条，结束此ID源")
                        break

                    pages += 1

                except Exception as e:
                    print(f"请求异常: {e}")
                    break

        print(f"全部用户获取完成，共获取 {len(UserLists)} 个用户")
        return UserLists
    else:
        # 原始模式：根据数量限制获取用户
        # 计算需要的总用户数
        total_needed = int(data["SendData"]["SendConfigs"]["FriendCount2"]) - int(
            data["SendData"]["SendConfigs"]["FriendCount"]) + 1

        # 计算需要跳过的用户数（起始点之前的用户）
        skip_count = int(data["SendData"]["SendConfigs"]["FriendCount"]) - 1

        print(f"需要获取 {total_needed} 个用户 (跳过前 {skip_count} 个)")

        UserLists = []
        global_skipped = 0  # 全局已跳过计数器
        global_collected = 0  # 全局已收集计数器

        # 遍历所有ID源（群组/页面/支持列表）
        for i in range(len(data[messags_types2])):
            current_id = data[messags_types2][i]['Id']
            pages = 1
            print(f"\n开始处理 ID源 {i + 1}/{len(data[messags_types2])}: {current_id}")
            print(f"全局状态: 已跳过 {global_skipped}/{skip_count}, 已收集 {global_collected}/{total_needed}")

            # 当还需要获取用户时继续请求
            while global_collected < total_needed:
                # 计算当前页需要跳过的用户数
                page_skip = 0
                if global_skipped < skip_count:
                    page_skip = min(10, skip_count - global_skipped)

                url = f"https://cj.ry188.vip/api/GetUserDatanew.aspx?T={messags_types}&P={pages}&Z=10&Id={current_id}"
                print(f"正在请求: {url} (跳过本页前 {page_skip} 个用户)")

                try:
                    response = await fetch_data(url)

                    # 检查是否返回有效用户列表
                    if "UserList" not in response or not response["UserList"]:
                        print(f"ID {current_id} 第{pages}页无数据")
                        break

                    # 更新全局跳过计数
                    global_skipped += page_skip

                    # 获取当前页用户列表（跳过指定数量的用户）
                    users_in_page = response["UserList"][page_skip:]

                    # 添加本页所有用户ID
                    for user in users_in_page:
                        if global_collected < total_needed:
                            UserLists.append(user["userid"])
                            global_collected += 1
                        else:
                            break

                    # 检查是否已获取足够用户
                    if global_collected >= total_needed:
                        print(f"已达目标人数 {total_needed}，停止请求")
                        break

                    # 检查是否最后一页（不足10人）
                    if len(response["UserList"]) < 10:
                        print(f"ID {current_id} 最后一页数据不足10条")
                        break

                    pages += 1

                except Exception as e:
                    print(f"请求异常: {e}")
                    break

            # 检查是否已满足总人数要求
            if global_collected >= total_needed:
                break

        print(f"实际获取 {len(UserLists)} 个用户 (跳过 {global_skipped} 个)")
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



async def main():
    cookies = getCookie()  # 从文件读取cookies
    content1 = "272275"
    data = await fetch_data(f"https://cj.ry188.vip/API/GetData.aspx?Account={content1}")

    # 检查是否继续上一次
    continue_last = parse_bool(data["SendData"]["SendConfigs"]["IsResetProgress"])
    print(f"继续上一次: {continue_last}")

    users = []
    start_position = 0

    if continue_last:
        # 尝试加载进度
        users, start_position = load_progress(content1)

    # 如果没有加载到进度或不需要继续，重新获取用户列表
    if not users:
        # 确定请求类型
        if parse_bool(data["SendData"]["SendConfigs"]["IsGroup"]):
            messags_types = "G"
            messags_types2 = "GroupIdList"
        elif parse_bool(data["SendData"]["SendConfigs"]["IsPages"]):
            messags_types = "P"
            messags_types2 = "PagesIdList"
        else:
            messags_types = "S"
            messags_types2 = "SupportIdList"

        print(f"请求类型: {messags_types}, 数据源: {messags_types2}")

        # 获取用户列表
        users = await GetHtmluser(data, messags_types, messags_types2)
        print(f"共获取 {len(users)} 个用户ID")
    crawler = Crawler(cookies,data,users,start_position,content1)

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