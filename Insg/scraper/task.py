import asyncio
import json
import os
import sys

from PyQt5.QtWidgets import QApplication
from Insg.database.database import Database
from Insg.interface.log_window import ProgressWindow
from Insg.logger.logger import setup_logger
from Insg.interface.login_window import win_main
from Insg.scraper.instagram import InstagramScraper, DATABASE_CONFIG

semaphore = asyncio.Semaphore(1)

def getConfig():
    if not os.path.exists("./config/config.json"):
        raise Exception("未找到配置文件")
    with open("./config/config.json", "r") as f:
        return json.load(f)
    return None

def getCookie(path):
    if os.path.exists(path):
        with open("instagram.json", "r") as f:
            return json.load(f)
    return None

def loadData(Keywords,Works,Author):
    data = []
    if not  Works:
        print("空的Works")
    else:
        for Works in Works:
            data.append({"url": Works, "type": "post"})
    if not  Keywords:
        print("空的Keywords")
    else:
        Keywords = Keywords.split("#")
        for Keywords in Keywords:
            data.append({"url": Keywords, "type": "keyword"})
    if not Author:
        print("空的Author")
    else:
        for Author in Author:
            data.append({"url": Author, "type": "follower"})

    # if os.path.exists("./data/post.csv"):
    #     with open('./data/post.csv', mode='r', newline='', encoding='utf-8') as file:
    #         csv_data = csv.reader(file)
    #         for row in csv_data:
    #             data.append({"url": row[0], "type": "post"})
    #
    # if os.path.exists("./data/keyword.csv"):
    #     with open('./data/keyword.csv', mode='r', newline='', encoding='utf-8') as file:
    #         csv_data = csv.reader(file)
    #         for row in csv_data:
    #             data.append({"url": row[0], "type": "keyword"})
    #
    # if os.path.exists("./data/follower.csv"):
    #     with open('./data/follower.csv', mode='r', newline='', encoding='utf-8') as file:
    #         csv_data = csv.reader(file)
    #         for row in csv_data:
    #             data.append({"url": row[0], "type": "follower"})
    print(data)
    return data

async def worker(scraper, task, log,progress_window):
    task_url = task["url"]
    task_type = task["type"]
    # 通知进度窗口开始新任务

    async with semaphore:
        try:
            if task_type == "post":
                log.info(f"开始采集作品[{task_url}]的点赞用户和评论用户")
                progress_window.start_task(task_type, task_url)
                await scraper.getPostRelationUser(task_url)
                progress_window.log_view.append(f"=== 點贊跟評論 {task_url} 采集完成 ===")
            elif task_type == "follower":
                log.info(f"开始采集作者[{task_url}]的粉丝用户")
                progress_window.start_task(task_type, task_url)
                await scraper.getFollowUser(task_url)
                progress_window.log_view.append(f"=== 粉絲用戶 {task_url} 采集完成 ===")
            elif task_type == "keyword":
                log.info(f"开始采集关键词[{task_url}]的用户")
                progress_window.start_task(task_type, task_url)
                await scraper.getKeywordUsers(task_url)
                progress_window.log_view.append(f"=== 關鍵詞 {task_url} 采集完成 ===")
        except Exception as e:
            log.error(f"任务执行失败: {str(e)}")
            progress_window.log_view.append(f"[错误] {str(e)}")
        progress_window.log_view.append(f"=== 采集任務完成 ===")

async def check_and_login(log):
    cookies = None
    cookies_path = "instagram.json"

    # 尝试加载并验证cookies
    if os.path.exists(cookies_path):
        try:
            with open(cookies_path, "r") as f:
                cookies = json.load(f)

            # 初始化临时爬虫进行cookies验证
            db = Database(DATABASE_CONFIG['host'], DATABASE_CONFIG['username'],
                          DATABASE_CONFIG['password'], DATABASE_CONFIG['name'])
            scraper = InstagramScraper(cookies, log, db)

            # 实际验证cookies有效性
            if await scraper.validate_cookies():
                log.info("Cookies验证成功，使用缓存登录")
                await scraper.close()
                return cookies

        except Exception as e:
            log.warning(f"Cookies验证失败: {str(e)}")
            os.remove(cookies_path)
            await scraper.close() if scraper else None

    # 如果没有有效的cookies，尝试登录
    try:
        credentials = win_main()
        if not credentials:
            log.error("用户取消了登录，无法继续执行")
            return None  # 不抛出异常，返回None

        # 初始化爬虫并登录
        db = Database(DATABASE_CONFIG['host'], DATABASE_CONFIG['username'],
                      DATABASE_CONFIG['password'], DATABASE_CONFIG['name'])
        scraper = InstagramScraper(None, log, db)

        try:
            await scraper.login(credentials['username'], credentials['password'])
            return scraper.cookies
        except Exception as e:
            log.error(f"登录失败: {str(e)}")
            os.remove(cookies_path) if os.path.exists(cookies_path) else None
            return None  # 登录失败，返回None

    except Exception as e:
        log.error(f"登录过程中发生错误: {str(e)}")
        return None

async def main(content0,content1,lines_hidden_line,lines_hidden_text):
    Keywords,Works,Author = content1, lines_hidden_line, lines_hidden_text
    scraper = None
    log = setup_logger()
    # 初始化数据库
    db = Database(DATABASE_CONFIG['host'], DATABASE_CONFIG['username'],
                  DATABASE_CONFIG['password'], DATABASE_CONFIG['name'])
    db.init_table()

    try:
        cookies = await check_and_login(log)
        if not cookies:
            log.error("登录失败，程序终止")
            return
    except Exception as e:
        log.error(f"登录失败: {str(e)}")
        return

    # # 初始化爬虫
    # scraper = InstagramScraper(cookies, log, db)
    # 创建GUI应用
    app = QApplication(sys.argv)
    progress_window = ProgressWindow()
    progress_window.show()

    try:

        tasks = loadData(Keywords,Works,Author)
        scraper = InstagramScraper(cookies, log, db, progress_window.update_signal.emit)
        try:
            # 创建任务时传入进度窗口
            task_list = [worker(scraper, task, log, progress_window) for task in tasks]
            await asyncio.gather(*task_list)
        finally:
            db.close()
            await scraper.close()
    finally:
        db.close()
        await scraper.close()
        # app.quit()