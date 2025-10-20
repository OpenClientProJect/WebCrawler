import os
import sys

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QFrame, QApplication, QPushButton, QDialog,
                             QScrollArea, QSizePolicy, QMessageBox)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize


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
        self.setFixedSize(900, 700)

        # 设置样式 - 白色背景
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, Qt.black)
        self.setPalette(palette)

        # 主布局 - 直接使用白色背景
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 设置窗口背景为白色
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 0px;
            }
        """)

        # 标题栏 - 渐变背景
        title_bar = QFrame()
        title_bar.setFixedHeight(80)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8965, stop:1 #ffa07a);
                border-radius: 0px;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(25, 0, 15, 0)

        # 左侧占位符，用于平衡布局
        left_spacer = QWidget()
        left_spacer.setFixedSize(48, 24) 
        title_layout.addWidget(left_spacer)

        # 标题 
        title_label = QLabel("Threads爬取數據監控")
        title_label.setFont(QFont("微軟雅黑", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label, 1)  

        # 按钮容器 - 右对齐
        button_container = QHBoxLayout()
        button_container.setSpacing(8)

        # 最小化按钮
        min_button = QPushButton("")
        min_button.setFixedSize(24, 24)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #01bcae;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        button_container.addWidget(min_button)

        # 关闭按钮
        close_button = QPushButton("")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #ff4d4f;
            }
        """)
        close_button.clicked.connect(self.close)
        button_container.addWidget(close_button)

        # 将按钮容器添加到标题布局
        title_layout.addLayout(button_container)

        main_layout.addWidget(title_bar)

        # 添加渐变分割线
        separator_line = QFrame()
        separator_line.setFixedHeight(6)
        separator_line.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #01bdae, stop:1 #01bdae);
                border: none;
            }
        """)
        main_layout.addWidget(separator_line)

        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # 统计卡片区域
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(25)

        # 关键词搜索计数器
        self.search_counter = self.create_counter_box("關鍵詞發現用戶", "947", "#ff8965", "#ff6b6b")
        stats_layout.addWidget(self.search_counter)

        # 用户帖子计数器
        self.userpost_counter = self.create_counter_box("用戶帖子採集", "470", "#51cf66", "#01bdae")
        stats_layout.addWidget(self.userpost_counter)

        # 粉丝列表计数器
        self.follower_counter = self.create_counter_box("粉絲用戶採集", "298", "#339af0", "#01bdae")
        stats_layout.addWidget(self.follower_counter)

        content_layout.addLayout(stats_layout)

        # 日志区域标题
        log_title_layout = QHBoxLayout()

        # 添加greater-than图标
        greater_than_icon = QLabel()
        greater_than_icon.setPixmap(QIcon(resource_path("iamge/greater-than.png")).pixmap(16, 16))
        greater_than_icon.setStyleSheet(" background: transparent; border: none;")
        log_title_layout.addWidget(greater_than_icon)

        log_title_label = QLabel("爬取過程:")
        log_title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        log_title_label.setStyleSheet("color: #ff8965; background: transparent; border: none;")
        log_title_layout.addWidget(log_title_label)
        log_title_layout.addStretch()

        content_layout.addLayout(log_title_layout)

        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("微軟雅黑", 11))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e0e0e0;
                font-size: 12px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #01bdae;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content_layout.addWidget(self.log_text, 1)  # 设置拉伸因子为1

        # 清空按钮
        clear_btn = QPushButton("清空數據")
        clear_btn.setFixedSize(200, 45)
        clear_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8965, stop:1 #ffa07a);
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                padding: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7a5a, stop:1 #ff9a7a);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255, 137, 101, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b4a, stop:1 #ff8a6a);
            }
        """)

        # 添加删除图标
        delete_icon = QIcon(resource_path("iamge/shanchu.png"))
        clear_btn.setIcon(delete_icon)
        clear_btn.setIconSize(QSize(20, 20))
        clear_btn.clicked.connect(self.clear_logs)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch(1)

        content_layout.addLayout(button_layout)

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
    def create_counter_box(self, title, initial_value, color1, color2):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 12px;
                border: none;
                border-left: 2px solid {color1};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding-left: 0px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("微軟雅黑", 13))
        title_label.setStyleSheet("color: #333; background: transparent; border: none; font-weight: normal;")
        title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(title_label)

        # 计数器
        count_label = QLabel(initial_value)
        count_label.setFont(QFont("微軟雅黑", 32, QFont.Bold))
        count_label.setStyleSheet("color: #333; background: transparent; border: none;")
        count_label.setAlignment(Qt.AlignLeft)

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

            # 创建带颜色的圆点和类型标签
            dot_color = ""
            if log_type == "search":
                dot_color = "#ff8965"
            elif log_type == "userpost":
                dot_color = "#51cf66"
            elif log_type == "follower":
                dot_color = "#339af0"

            # 添加带彩色圆点的日志
            log_entry = f'<div style="margin: 8px 0; padding: 8px 12px; background: white; border-radius: 8px; border: 1px solid #e0e0e0;"><span style="color: {dot_color}; font-size: 16px;">●</span> <span style="color: #333; margin-left: 8px;">{message}</span></div>'
        else:
            # 普通日志不加序号
            log_entry = f'<div style="margin: 8px 0; padding: 8px 12px; background: white; border-radius: 8px; border: 1px solid #e0e0e0;"><span style="color: #666;">{message}</span></div>'

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
