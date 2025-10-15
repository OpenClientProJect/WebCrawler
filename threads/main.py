import argparse
import asyncio
import json
import os
import signal
from database import Database
from task import Task
from logger import logger
from crawler import Crawler
from monitor_window import MonitorWindow

is_running = True

def shutdown():
    global is_running
    is_running = False
    logger.warning("正在停止采集...")

def setup_signal_handlers():
    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda s, f: shutdown())
def getCookie():
    if not os.path.exists("threads.json"):
        return None
    with open("threads.json", "r") as f:
        try:
            return json.load(f)
        except:
            return None
    return None
async def main(content1, selected_types, limit,userpost_limit,follower_limit, monitor_window=None):
    global is_running
    setup_signal_handlers()
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--type', type=str, required=True)
    # parser.add_argument('--type', type=str, required=False, default='search')
    # parser.add_argument('--type', type=str, required=False, default='userpost')
    # parser.add_argument('--type', type=str, required=False, default='follower')
    # args = parser.parse_args()

    db = Database()
    db.init()
    # 先创建Crawler实例并进行登录验证
    cookies = getCookie()  # 从文件读取cookies
    crawler = Crawler(lambda: is_running, cookies, userpost_limit, follower_limit)

    # 确保登录成功
    if cookies is None or not await crawler.check_cookies_valid():
        try:
            # 尝试GUI登录
            await crawler.login_with_gui()
            if not crawler.is_logged_in:
                logger.error("登录失败，无法继续执行任务")
                return  # 直接返回，不再执行后续任务
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return  # 登录失败时直接返回
    else:
        # 如果cookies有效，标记为已登录
        crawler.is_logged_in = True
        logger.info("使用有效cookies登录成功")

    # 创建监控窗口
    if monitor_window is None:
        monitor_window = MonitorWindow()
        monitor_window.show()

    task = Task(lambda: is_running, monitor_window)
    task.crawler = crawler  # 传递已经登录的crawler实例
    try:
        for task_type in selected_types:
            print("執行任務：",task_type)
            if not is_running:
                break
            await task.run(task_type,content1, limit,userpost_limit,follower_limit)

    finally:
        db.close()
        await task.close()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         shutdown()