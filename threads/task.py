import asyncio
import csv
import json
import os
import traceback
from logger import logger
from crawler import Crawler
import sys
from PyQt5.QtWidgets import QApplication
from monitor_window import MonitorWindow
class Task:
    def __init__(self, is_running_fn, monitor_window=None):
        self.is_running_fn = is_running_fn
        self.semaphore = asyncio.Semaphore(1)
        self.crawler = None
        self.keywords = []
        self.tasks = []
        self.limit = 0  # 新增limit属性
        self.current_count = 0  # 新增计数器
        self.userpost_count = 0
        self.follower_count = 0
        self.monitor_window = monitor_window  # 保存监控窗口引用

    def log_message(self, log_type, message):
        """发送日志到监控窗口"""
        if self.monitor_window:
            self.monitor_window.signals.log_signal.emit(log_type, message)

    def update_counter(self, counter_type, count=1):
        """更新计数器，添加 count 参数"""
        if self.monitor_window:
            self.monitor_window.signals.counter_signal.emit(counter_type, count)
    def loadData(self):
        data = []
        if os.path.exists("keywords.csv"):
            with open('keywords.csv', mode='r', newline='', encoding='utf-8') as file:
                csv_data = csv.reader(file)
                for keyword in csv_data:
                    data.append(keyword[0])
        self.keywords = data



    async def worker(self, type, keyword):
        async with self.semaphore:
            try:
                self.crawler.task = self

                await self.crawler.start(type, keyword)

                # 只在特定日志时调用 log_message
                if type == 'search':
                    # self.log_message("search", f"开始采集关键词[{keyword}]的相关数据")
                    self.log_message(type, f"採集關鍵詞任務完成~~")
                elif type == 'userpost':
                    # self.log_message("userpost", f"开始采集用户[{keyword}]的帖子")
                    self.log_message(type, f"採集用戶帖子任務完成~~")
                elif type == 'follower':
                    # self.log_message("follower", f"开始采集用户[{keyword}]的粉丝用户")
                    self.log_message(type, f"採集粉絲用戶任務完成~~")

            except Exception as e:
                self.log_message(type, f"任务错误: {str(e)}")
                if "登录失败" in str(e):
                    logger.warning("登录凭证无效，正在尝试重新登录...")
                    await self.crawler.login_with_gui()
                    await self.crawler.start(type, keyword)
                else:
                    tb = traceback.format_exc()
                    logger.error(f"采集器发生错误: {e}\n{tb}")

    async def run(self, type,content1, limit,userpost_limit,follower_limit):
        # self.loadData()
        self.keywords = content1
        self.limit = limit
        # cookies = self.getCookie()
        # self.crawler = Crawler(self.is_running_fn, cookies,userpost_limit,follower_limit)
        self.crawler.task = self
        self.crawler.is_running_fn = self.is_running_fn
        # for keyword in self.keywords:
        #     if self.is_running_fn() == False:
        #         break
        #     task = asyncio.create_task(self.worker(type, keyword))
        #     self.tasks.append(task)

        task = asyncio.create_task(self.worker(type, self.keywords))
        self.tasks.append(task)

        await asyncio.gather(*self.tasks)

    def check_limit(self):
        if self.limit == 0:  # 0表示无限制
            return True
        return self.current_count < self.limit

    def userpost_limit_num(self):
        return self.userpost_count
    def follower_limit_num(self):
        return self.follower_count
    def increment_count(self, amount=1):
        self.current_count += amount
        print(self.current_count)
    def userpost_limit_count(self, amount=1):
        self.userpost_count += amount
    def follower_limit_count(self, amount=1):
        self.follower_count += amount

    async def close(self):
        if self.crawler:
            await self.crawler.close()