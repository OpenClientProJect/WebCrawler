import logging
import sys
from datetime import datetime


# 定义颜色
class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"    # 红色（错误）
    GREEN = "\033[32m"  # 绿色（正常信息）
    YELLOW = "\033[33m" # 黄色（警告）

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = LogColors.RESET
        if record.levelno == logging.ERROR:
            log_color = LogColors.RED
        elif record.levelno == logging.WARNING:
            log_color = LogColors.YELLOW
        elif record.levelno == logging.INFO:
            log_color = LogColors.GREEN

        # 时间戳 + 消息内容
        formatted = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {record.levelname}: {record.msg}"
        return f"{log_color}{formatted}{LogColors.RESET}"

def setup_logger():
    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.DEBUG)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 设置格式化器
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)

    # 添加处理器到日志对象
    logger.addHandler(console_handler)
    return logger