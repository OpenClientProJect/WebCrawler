import argparse
import asyncio
import signal
from app.database import Database
from app.task import Task
from app.config import DEBUG
from app.logger import logger

is_running = True

def shutdown():
    global is_running
    is_running = False
    logger.warning("正在停止采集...")

def setup_signal_handlers():
    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda s, f: shutdown())

async def main():
    global is_running
    setup_signal_handlers()

    parser = argparse.ArgumentParser()
    # parser.add_argument('--type', type=str, required=True)
    parser.add_argument('--type', type=str, required=False, default='search')
    # parser.add_argument('--type', type=str, required=False, default='userpost')
    # parser.add_argument('--type', type=str, required=False, default='follower')
    args = parser.parse_args()

    db = Database()
    db.init()

    task = Task(lambda: is_running)

    try:
        await task.run(args.type)
    finally:
        db.close()
        await task.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        shutdown()
