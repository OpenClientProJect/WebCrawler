import asyncio
import os
import json
import sys
import datetime
import aiohttp
from PyQt5.QtWidgets import QApplication
from FB_status import StatusWindow

from FB_lists import show_task_order_window_async
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


async def GetHtmluser(data, messags_types, messags_types2):
    # 检查是否获取全部用户
    get_all = parse_bool(data["SendData"]["SendConfigs"]["IsSendAll"])

    if get_all:
        # 获取全部用户模式
        print("获取全部用户模式：忽略数量限制，获取所有可用用户")
        UserLists = []
        SourceMapping = {}  # 新增：用户ID到社团ID的映射
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
                        user_id = user["userid"]
                        UserLists.append(user_id)
                        SourceMapping[user_id] = current_id  # 记录映射关系

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
        return UserLists, SourceMapping  # 返回用户列表和映射关系
    else:
        # 原始模式：根据数量限制获取用户
        # 计算需要的总用户数
        total_needed = int(data["SendData"]["SendConfigs"]["FriendCount2"]) - int(
            data["SendData"]["SendConfigs"]["FriendCount"]) + 1

        # 计算需要跳过的用户数（起始点之前的用户）
        skip_count = int(data["SendData"]["SendConfigs"]["FriendCount"]) - 1

        print(f"需要获取 {total_needed} 个用户 (跳过前 {skip_count} 个)")

        UserLists = []
        SourceMapping = {}  # 新增：用户ID到社团ID的映射
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
                            user_id = user["userid"]
                            UserLists.append(user_id)
                            SourceMapping[user_id] = current_id  # 记录映射关系
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
        return UserLists, SourceMapping  # 返回用户列表和映射关系


def parse_bool(type_data):
    type_data = str(type_data).lower().strip()
    return type_data in ('true', '1', 'yes', 'yes')


def load_progress(account):
    """从文件加载处理进度"""
    filename = f"{account}_progress.json"
    if not os.path.exists(filename):
        print(f"无进度文件 {filename}")
        return None, 0, {}

    try:
        with open(filename, 'r') as f:
            progress_data = json.load(f)
        print(f"从 {filename} 加载进度: 位置 {progress_data['position']}/{len(progress_data['users'])}")

        # 加载 source_mapping，如果不存在则返回空字典
        source_mapping = progress_data.get("source_mapping", {})
        return progress_data["users"], progress_data["position"], source_mapping
    except:
        print(f"加载进度文件 {filename} 失败")
        return None, 0, {}



# async def main(content0, content1):
#     app = QApplication.instance()
#     if not app:
#         app = QApplication(sys.argv)
#     cookies = getCookie()  # 从文件读取cookies
#     data = await fetch_data(f"https://cj.ry188.vip/API/GetData.aspx?Account={content1}")
#     # 解析配置 - 个人主页留言相关
#     is_group_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsGroup"])  # 是否社团成员留言
#     is_pages_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsPages"])  # 是否粉专成员留言
#     is_ad_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsZanKe"])  # 是否赞客成员留言
#
#     # 个人主页留言总体状态（任意一个为真即为真）
#     user_enable = is_group_members_send_text or is_pages_members_send_text or is_ad_members_send_text
#
#     # 解析配置 - 关键字任务相关
#     is_enable_keyword_search = parse_bool(data["SendData"]["SendConfigs"]["IsEnableKeywordSearch"])  # 是否发送关键字
#     is_posts = parse_bool(data["SendData"]["SendConfigs"]["IsPosts"])  # 是否FB贴文
#     is_group_posts = parse_bool(data["SendData"]["SendConfigs"]["IsGroupPosts"])  # 是否FB社团贴文
#
#     # 关键字任务总体状态（发送关键字且（FB贴文或FB社团贴文）为真）
#     key_enable = is_enable_keyword_search and (is_posts or is_group_posts)
#
#     is_key_friend = parse_bool(data["SendData"]["SendConfigs"]["IsQueryFriend"])  # 是否搜寻好友
#
#     is_Group = parse_bool(data["SendData"]["SendConfigs"]["IsGroup"])
#     Groupjoin = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinGroup"])  # 是否社团邀请好友
#     is_Groupkey_join = is_Group and Groupjoin
#
#     is_Fans = parse_bool(data["SendData"]["SendConfigs"]["IsPages"])
#     Fansjoin = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinPages"])  # 是否粉丝邀请好友
#     is_Fanskey_join = is_Fans and Fansjoin
#
#     # 创建配置字典
#     config = {
#         "Key_IsEnableKey": key_enable,
#         "key_IsKeyfriend": is_key_friend,
#         "Groupkey_join": is_Groupkey_join,
#         "Fanskey_join": is_Fanskey_join,
#         "User_IsEnableBrowse": user_enable,
#         # 添加详细信息
#         "IsGroupMem": is_group_members_send_text,
#         "IsPagesMem": is_pages_members_send_text,
#         "IsAdMem": is_ad_members_send_text,
#         "User_Detail": {
#             "group": is_group_members_send_text,
#             "pages": is_pages_members_send_text,
#             "ad": is_ad_members_send_text
#         },
#         "IsFbPages": is_posts,
#         "IsGroupPages": is_group_posts,
#         "Key_Detail": {
#             "fbpages": is_posts,
#             "grouppages": is_group_posts,
#         }
#     }
#
#     # 显示任务顺序设置窗口并获取用户设置的顺序，传递配置参数
#     task_order_data = show_task_order_window_async(config)
#     if task_order_data is None:
#         print("用户取消了任务顺序设置")
#         return  # 或者进行其他处理
#
#     task_order = task_order_data.get('order', [])
#     rest_times = task_order_data.get('rest_times', {})
#     completion_times = task_order_data.get('completion_times', {})  # 新增：获取完成时间
#     scheduled_time = task_order_data.get('scheduled_time')   # 添加计划时间
#     print(task_order, rest_times,completion_times,scheduled_time)
#
#     # 检查是否继续上一次
#     continue_last = parse_bool(data["SendData"]["SendConfigs"]["IsResetProgress"])
#     print(f"继续上一次: {continue_last}")
#
#     app.setApplicationName("自動化脚本")
#     status_window = StatusWindow()
#     status_window.show()
#     status_window.update_signal.emit("提前獲取用戶數據耐心等待...")
#
#     users = []
#     start_position = 0
#     source_mapping = {}  # 新增：初始化 source_mapping
#
#     if continue_last:
#         # 尝试加载进度，包括 source_mapping
#         users, start_position, source_mapping = load_progress(content1)
#
#     # 如果没有加载到进度或不需要继续，重新获取用户列表
#     if not users:
#         # 确定请求类型
#         if parse_bool(data["SendData"]["SendConfigs"]["IsGroup"]):
#             messags_types = "G"
#             messags_types2 = "GroupIdList"
#         elif parse_bool(data["SendData"]["SendConfigs"]["IsPages"]):
#             messags_types = "P"
#             messags_types2 = "PagesIdList"
#         else:
#             messags_types = "S"
#             messags_types2 = "SupportIdList"
#
#         print(f"请求类型: {messags_types}, 数据源: {messags_types2}")
#
#         # 获取用户列表和映射关系
#         users, source_mapping = await GetHtmluser(data, messags_types, messags_types2)
#         print(f"共获取 {len(users)} 个用户ID, 映射关系数量: {len(source_mapping)}")
#
#     # 确保 source_mapping 不为 None
#     if source_mapping is None:
#         source_mapping = {}
#
#     crawler = Crawler(cookies, data, users, start_position, content0, content1, task_order, rest_times, source_mapping)
#     crawler.completion_times = completion_times
#     # 确保登录成功
#     if cookies is None or not await crawler.check_cookies_valid():
#         try:
#             # 尝试GUI登录
#             await crawler.login_with_gui()
#             while 1:
#                 if not crawler.is_logged_in:
#                     print("登录失败，无法继续执行任务")
#                     await crawler.login_with_gui()
#                     # return  # 直接返回，不再执行后续任务
#                 else:
#                     break
#         except Exception as e:
#             print(f"登录失败: {str(e)}")
#             return  # 登录失败时直接返回
#     else:
#         # 如果cookies有效，标记为已登录
#         crawler.is_logged_in = True
#         print("使用有效cookies登录成功")
#
#     try:
#         # app = QApplication.instance()
#         # if not app:
#         #     app = QApplication(sys.argv)
#         # app.setApplicationName("自動化脚本")
#         # status_window = StatusWindow()
#         # status_window.show()
#         # status_window.update_signal.emit("獲取用戶數據...")
#
#         # 关键修改：将状态窗口传递给crawler对象
#         crawler.status_window = status_window
#
#         QApplication.processEvents()  # 确保UI更新
#         await crawler.start()
#     finally:
#         # 确保关闭浏览器
#         pass
#     return crawler

async def main(content0, content1):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    cookies = getCookie()
    data = await fetch_data(f"https://cj.ry188.vip/API/GetData.aspx?Account={content1}")

    # 解析配置 - 保持不变
    is_group_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsGroup"])
    is_pages_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsPages"])
    is_ad_members_send_text = parse_bool(data["SendData"]["SendConfigs"]["IsZanKe"])
    user_enable = is_group_members_send_text or is_pages_members_send_text or is_ad_members_send_text

    is_enable_keyword_search = parse_bool(data["SendData"]["SendConfigs"]["IsEnableKeywordSearch"])
    is_posts = parse_bool(data["SendData"]["SendConfigs"]["IsPosts"])
    is_group_posts = parse_bool(data["SendData"]["SendConfigs"]["IsGroupPosts"])
    key_enable = is_enable_keyword_search and (is_posts or is_group_posts)

    is_key_friend = parse_bool(data["SendData"]["SendConfigs"]["IsQueryFriend"])

    is_Group = parse_bool(data["SendData"]["SendConfigs"]["IsGroup"])
    Groupjoin = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinGroup"])
    is_Groupkey_join = is_Group and Groupjoin

    is_Fans = parse_bool(data["SendData"]["SendConfigs"]["IsPages"])
    Fansjoin = parse_bool(data["SendData"]["SendConfigs"]["IsInviteJoinPages"])
    is_Fanskey_join = is_Fans and Fansjoin

    config = {
        "Key_IsEnableKey": key_enable,
        "key_IsKeyfriend": is_key_friend,
        "Groupkey_join": is_Groupkey_join,
        "Fanskey_join": is_Fanskey_join,
        "User_IsEnableBrowse": user_enable,
        "IsGroupMem": is_group_members_send_text,
        "IsPagesMem": is_pages_members_send_text,
        "IsAdMem": is_ad_members_send_text,
        "User_Detail": {
            "group": is_group_members_send_text,
            "pages": is_pages_members_send_text,
            "ad": is_ad_members_send_text
        },
        "IsFbPages": is_posts,
        "IsGroupPages": is_group_posts,
        "Key_Detail": {
            "fbpages": is_posts,
            "grouppages": is_group_posts,
        }
    }

    # 显示任务顺序设置窗口
    task_order_data = show_task_order_window_async(config)
    if task_order_data is None:
        print("用户取消了任务顺序设置")
        return

    task_order = task_order_data.get('order', [])
    rest_times = task_order_data.get('rest_times', {})
    completion_times = task_order_data.get('completion_times', {})
    scheduled_time = task_order_data.get('scheduled_time', "0")

    print(f"任务顺序: {task_order}, 休息时间: {rest_times}, 完成时间: {completion_times}, 计划时间: {scheduled_time}")

    # 检查是否继续上一次
    continue_last = parse_bool(data["SendData"]["SendConfigs"]["IsResetProgress"])
    print(f"继续上一次: {continue_last}")

    # 创建状态窗口
    app.setApplicationName("自動化脚本")
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
    source_mapping = {}

    if continue_last:
        users, start_position, source_mapping = load_progress(content1)

    if not users:
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
        users, source_mapping = await GetHtmluser(data, messags_types, messags_types2)
        print(f"共获取 {len(users)} 个用户ID, 映射关系数量: {len(source_mapping)}")

    if source_mapping is None:
        source_mapping = {}

    crawler = Crawler(cookies, data, users, start_position, content0, content1, task_order, rest_times, source_mapping)
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
        status_window.update_signal.emit(f"任务执行失败: {str(e)}")
        await asyncio.sleep(1)
        print(f"任务执行失败: {str(e)}")
    finally:
        # 确保资源清理
        pass
