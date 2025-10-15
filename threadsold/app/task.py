import asyncio
import csv
import json
import os
import traceback
from threadsold.app.logger import logger
from threadsold.app.crawler import Crawler

class Task:
    def __init__(self, is_running_fn):
        self.is_running_fn = is_running_fn
        self.semaphore = asyncio.Semaphore(1)
        self.crawler = None
        self.keywords = []
        self.tasks = []

    def loadData(self):
        data = []
        if os.path.exists("./data/keywords.csv"):
            with open('./data/keywords.csv', mode='r', newline='', encoding='utf-8') as file:
                csv_data = csv.reader(file)
                for keyword in csv_data:
                    data.append(keyword[0])
        self.keywords = data

    def getCookie(self):
        if not os.path.exists("./data/threads.json"):
            return None
        with open("./data/threads.json", "r") as f:
            try:
                return json.load(f)
            except:
                return None
        return None
    
    async def worker(self, type, keyword):
        async with self.semaphore:
            try:
                await self.crawler.start(type, keyword)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"采集器发生错误: {e}\n{tb}")

    async def run(self, type):
        self.loadData()
        cookies = self.getCookie()
        self.crawler = Crawler(self.is_running_fn, cookies)

        for keyword in self.keywords:
            if self.is_running_fn() == False:
                break
            task = asyncio.create_task(self.worker(type, keyword))
            self.tasks.append(task)

        await asyncio.gather(*self.tasks)

    async def close(self):
        if self.crawler:
            await self.crawler.close()
