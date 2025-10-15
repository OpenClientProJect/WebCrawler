import os
import sys

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QFrame, QApplication, QPushButton, QDialog,
                             QScrollArea, QSizePolicy, QMessageBox)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class MonitorSignals(QObject):
    log_signal = pyqtSignal(str, str)  # 参数: 类型, 消息
    counter_signal = pyqtSignal(str, int)  # 参数: 类型, 数量

class MonitorWindow(QDialog):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("Threadsicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.signals = MonitorSignals()
        self.init_ui()
        self.counters = {
            'search': 0,
            'userpost': 0,
            'follower': 0
        }
        self.log_counters = {
            'search': 1,
            'userpost': 1,
            'follower': 1
        }

        # 连接信号与槽
        self.signals.log_signal.connect(self.add_log)
        self.signals.counter_signal.connect(self.update_counter)

        # 设置窗口标志
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle('Threads爬取數據監控')
        self.setFixedSize(800, 600)

        # 设置样式
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(40, 44, 52))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(30, 34, 42))
        palette.setColor(QPalette.Text, Qt.white)
        self.setPalette(palette)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 自定义标题栏
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #282c34;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)

        # 标题
        title_label = QLabel("Threads爬取數據監控")
        title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        title_label.setStyleSheet("color: #61afef;")
        title_layout.addWidget(title_label)

        title_layout.addStretch(1)

        # 最小化按钮
        min_button = QPushButton("-")
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4b5263;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_button)

        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e06c75;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # 计数器区域
        counter_frame = QFrame()
        counter_frame.setStyleSheet("background-color: #282c34; border-radius: 8px;")
        counter_layout = QHBoxLayout(counter_frame)
        counter_layout.setContentsMargins(10, 10, 10, 10)
        counter_layout.setSpacing(15)

        # 关键词搜索计数器
        self.search_counter = self.create_counter_box("關鍵詞發現用戶", "#e06c75")
        counter_layout.addWidget(self.search_counter)

        # 用户帖子计数器
        self.userpost_counter = self.create_counter_box("用戶帖子採集", "#98c379")
        counter_layout.addWidget(self.userpost_counter)

        # 粉丝列表计数器
        self.follower_counter = self.create_counter_box("粉絲用戶採集", "#61afef")
        counter_layout.addWidget(self.follower_counter)

        content_layout.addWidget(counter_frame)

        # 日志区域标题
        log_title_layout = QHBoxLayout()
        log_title_layout.addWidget(QLabel("爬取過程:"))
        log_title_layout.addStretch()

        # 添加清空按钮
        clear_btn = QPushButton("清空數據")
        clear_btn.setFixedSize(80, 25)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c6370;
                color: white;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4b5263;
            }
        """)
        clear_btn.clicked.connect(self.clear_logs)
        log_title_layout.addWidget(clear_btn)

        content_layout.addLayout(log_title_layout)

        # 日志区域 - 使用滚动区域确保滚动条可见
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("微軟雅黑", 10))
        self.log_text.setStyleSheet("""
            background-color: #282c34;
            color: #abb2bf;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #5c6370;  # 添加边框以便看到滚动区域
        """)

        # 确保滚动区域设置正确：
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.log_text)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #5c6370;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: 1px solid #5c6370;
                background: #282c34;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #5c6370;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        log_layout.addWidget(scroll_area)
        content_layout.addWidget(log_frame, 1)  # 设置拉伸因子为1

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        # 初始化计数器显示
        self.search_count_label.setText("0")
        self.userpost_count_label.setText("0")
        self.follower_count_label.setText("0")

    def closeEvent(self, event):
        """重写关闭事件，发出关闭信号"""
        # self.window_closed.emit()  # 发送关闭信号
        # super().closeEvent(event)
        reply = QMessageBox.question(
            self, "關閉確認", "確認要關閉爬取程序嗎？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.window_closed.emit()
            super().closeEvent(event)
        else:
            event.ignore()
    def create_counter_box(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {color}; border-radius: 8px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("微軟雅黑", 11, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 计数器
        count_label = QLabel("0")
        count_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        count_label.setStyleSheet("color: white;")
        count_label.setAlignment(Qt.AlignCenter)

        # 根据标题存储对应的计数器
        if title == "關鍵詞發現用戶":
            self.search_count_label = count_label
        elif title == "用戶帖子採集":
            self.userpost_count_label = count_label
        elif title == "粉絲用戶採集":
            self.follower_count_label = count_label

        layout.addWidget(count_label)

        return frame

    def add_log(self, log_type, message):
        """添加日志，只有特定类型才加序号"""
        # 检查是否是需要加序号的日志类型
        if ("的帖子" in message and ("的粉絲" in message or "帖子" in message)) or ("的粉絲" in message) or (
                "關鍵詞" in message and "發現用戶" in message):
            # 获取当前类型的序号
            log_num = self.log_counters[log_type]
            self.log_counters[log_type] += 1

            # 创建带颜色的类型标签
            type_label = ""
            if log_type == "search":
                type_label = f'<span style="color:#e06c75; font-weight:bold;">[關鍵詞{log_num}]</span>'
            elif log_type == "userpost":
                type_label = f'<span style="color:#98c379; font-weight:bold;">[用戶貼{log_num}]</span>'
            elif log_type == "follower":
                type_label = f'<span style="color:#61afef; font-weight:bold;">[粉絲{log_num}]</span>'

            # 添加带序号的新日志
            log_entry = f"{type_label} {message}"
        else:
            # 普通日志不加序号
            log_entry = f"<span style='color:#abb2bf;'>{message}</span>"

        self.log_text.append(log_entry)

        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_counter(self, counter_type, count):
        """更新计数器"""
        if counter_type in self.counters:
            self.counters[counter_type] += count

            if counter_type == "search":
                self.search_count_label.setText(str(self.counters[counter_type]))
            elif counter_type == "userpost":
                self.userpost_count_label.setText(str(self.counters[counter_type]))
            elif counter_type == "follower":
                self.follower_count_label.setText(str(self.counters[counter_type]))

    def clear_logs(self):
        """清空日志并重置计数器"""
        self.log_text.clear()
        self.counters = {'search': 0, 'userpost': 0, 'follower': 0}
        self.log_counters = {'search': 1, 'userpost': 1, 'follower': 1}
        self.search_count_label.setText("0")
        self.userpost_count_label.setText("0")
        self.follower_count_label.setText("0")

    def mousePressEvent(self, event):
        """实现窗口拖动功能"""
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        """实现窗口拖动功能"""
        if hasattr(self, 'oldPos') and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication([])
    window = MonitorWindow()
    window.show()
    app.exec_()