# import sys
# from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, \
#     QScrollArea, QFrame, QWidget, QTextEdit
# from PyQt5.QtCore import Qt, pyqtSignal, QTimer
# from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
# import os
#
#
# class StatusWindow(QDialog):
#     update_signal = pyqtSignal(str)  # 信号：更新状态文本
#     countdown_signal = pyqtSignal(int)  # 新增：倒计时信号
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         icon_path = resource_path("Thcat.ico")
#         self.setWindowIcon(QIcon(icon_path))
#         self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 无边框
#         self.setFixedSize(400, 550)  # 固定大小
#         self.initUI()
#         self.update_signal.connect(self.update_status)
#         # 设置窗口位置到右上角（距离边缘10像素）
#         self.setGeometryToTopRight()
#         self.countdown_signal.connect(self.update_countdown)
#         self.countdown_timer = None
#         self.countdown_seconds = 0
#
#     # 新增方法：设置窗口到右上角
#     def setGeometryToTopRight(self):
#         screen_geometry = QApplication.desktop().availableGeometry()
#         x = screen_geometry.width() - self.width() - 10  # 距离右边10像素
#         y = 10  # 距离顶部10像素
#         self.move(x, y)
#
#     def initUI(self):
#         # 主布局
#         layout = QVBoxLayout()
#         layout.setContentsMargins(20, 20, 20, 20)
#         layout.setSpacing(15)
#
#         # 标题栏
#         title_bar = QHBoxLayout()
#         self.title_label = QLabel("執行任務狀態", self)
#         self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
#         self.title_label.setStyleSheet("color: white;")
#         title_bar.addWidget(self.title_label)
#         title_bar.addStretch(1)
#
#         # 最小化按钮
#         min_button = QPushButton("-", self)
#         min_button.setFixedSize(24, 24)
#         min_button.setFont(QFont("微軟雅黑", 12))
#         min_button.clicked.connect(self.showMinimized)
#         title_bar.addWidget(min_button)
#
#         # 关闭按钮
#         close_button = QPushButton("×", self)
#         close_button.setFixedSize(24, 24)
#         close_button.setFont(QFont("微軟雅黑", 12))
#         close_button.clicked.connect(self.close)
#         close_button.setStyleSheet("""
#             QPushButton:hover {
#                 background-color: red;
#             }
#         """)
#         title_bar.addWidget(close_button)
#
#         layout.addLayout(title_bar)
#         # 创建滚动区域
#         scroll_area = QScrollArea(self)
#         scroll_area.setWidgetResizable(True)
#         scroll_area.setFrameShape(QFrame.NoFrame)  # 无边框
#         scroll_area.setStyleSheet("background-color: #252525; border: none;")
#         # 添加倒计时显示标签
#         self.countdown_label = QLabel("", self)
#         self.countdown_label.setAlignment(Qt.AlignCenter)
#         self.countdown_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
#         self.countdown_label.setStyleSheet("color: #FFA500;")  # 橙色显示
#         self.countdown_label.hide()  # 初始隐藏
#         layout.addWidget(self.countdown_label)
#         # 创建内容容器
#         content_widget = QWidget()
#         content_layout = QVBoxLayout(content_widget)
#         content_layout.setContentsMargins(5, 5, 5, 5)
#         content_layout.setAlignment(Qt.AlignTop)
#
#         # 状态文本区域
#         self.status_textedit = QTextEdit()
#         self.status_textedit.setReadOnly(True)
#         self.status_textedit.setFont(QFont("微軟雅黑", 10))
#         self.status_textedit.setStyleSheet("""
#                     QTextEdit {
#                         color: #7FFFD4;
#                         background-color: #252525;
#                         border: none;
#                     }
#                 """)
#         self.status_textedit.append("準備開始任務...")
#         content_layout.addWidget(self.status_textedit)
#         # 设置滚动区域的内容
#         scroll_area.setWidget(content_widget)
#
#         # 添加到主布局
#         layout.addWidget(scroll_area)  # 替换原来的 status_label
#
#         self.setLayout(layout)
#
#         # 设置暗色主题
#         palette = QPalette()
#         palette.setColor(QPalette.Window, QColor(53, 53, 53))
#         palette.setColor(QPalette.WindowText, Qt.white)
#         palette.setColor(QPalette.Base, QColor(25, 25, 25))
#         self.setPalette(palette)
#     def closeEvent(self, event):
#         """重写关闭事件，发出关闭信号"""
#         reply = QMessageBox.question(
#             self, "關閉確認", "確認要關閉腳本程序嗎？",
#             QMessageBox.Yes | QMessageBox.No, QMessageBox.No
#         )
#         if reply == QMessageBox.Yes:
#             self.window_closed.emit()
#             super().closeEvent(event)
#         else:
#             event.ignore()
#
#     def update_countdown(self, seconds):
#         """更新倒计时显示"""
#         if seconds > 0:
#             self.countdown_seconds = seconds
#             minutes = seconds // 60
#             remaining_seconds = seconds % 60
#             self.countdown_label.setText(f"休息倒计时: {minutes:02d}:{remaining_seconds:02d}")
#             self.countdown_label.show()
#
#             # 启动或重启计时器
#             if self.countdown_timer:
#                 self.countdown_timer.stop()
#             self.countdown_timer = QTimer(self)
#             self.countdown_timer.timeout.connect(self.decrement_countdown)
#             self.countdown_timer.start(1000)  # 每秒触发
#         else:
#             self.countdown_label.hide()
#             if self.countdown_timer:
#                 self.countdown_timer.stop()
#
#     def decrement_countdown(self):
#         """减少倒计时"""
#         if self.countdown_seconds > 0:
#             self.countdown_seconds -= 1
#             minutes = self.countdown_seconds // 60
#             remaining_seconds = self.countdown_seconds % 60
#             self.countdown_label.setText(f"休息倒计时: {minutes:02d}:{remaining_seconds:02d}")
#         else:
#             self.countdown_label.hide()
#             self.countdown_timer.stop()
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
#             event.accept()
#
#     def mouseMoveEvent(self, event):
#         if event.buttons() == Qt.LeftButton:
#             self.move(event.globalPos() - self.dragPosition)
#             event.accept()
#
#     # def update_status(self, text):
#     #     """更新状态文本"""
#     #     self.status_label.setText(text)
#
#     def update_status(self, text):
#         """更新状态文本，追加并滚动到底部"""
#         # 追加新状态
#         self.status_textedit.append(text)
#
#         # 滚动到底部
#         scrollbar = self.status_textedit.verticalScrollBar()
#         scrollbar.setValue(scrollbar.maximum())
#
#         # 确保立即显示更新
#         QApplication.processEvents()
#
# def resource_path(relative_path):
#     """获取资源的绝对路径"""
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, \
    QScrollArea, QFrame, QWidget, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import os


class StatusWindow(QDialog):
    update_signal = pyqtSignal(str)  # 信号：更新状态文本
    countdown_signal = pyqtSignal(int)  # 新增：倒计时信号

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = resource_path("image/FBre.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 无边框
        self.setFixedSize(400, 550)  # 固定大小
        self.initUI()
        self.update_signal.connect(self.update_status)
        # 设置窗口位置到右上角（距离边缘10像素）
        self.setGeometryToTopRight()
        self.countdown_signal.connect(self.update_countdown)
        self.countdown_timer = None
        self.countdown_seconds = 0

    # 新增方法：设置窗口到右上角
    def setGeometryToTopRight(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        x = screen_geometry.width() - self.width() - 10  # 距离右边10像素
        y = 10  # 距离顶部10像素
        self.move(x, y)

    def initUI(self):
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 修改：移除边距让标题栏可以铺满
        layout.setSpacing(0)  # 修改：移除间距

        # 标题栏容器
        title_container = QWidget()
        title_container.setFixedHeight(40)  # 设置标题栏高度
        title_container.setStyleSheet(
            "background-color: #e4eee9; border-top-left-radius: 8px; border-top-right-radius: 8px;")

        title_bar = QHBoxLayout(title_container)
        title_bar.setContentsMargins(15, 0, 15, 0)

        self.title_label = QLabel("執行任務狀態")
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #333333; background: transparent;")
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)  # 添加弹性空间

        # 最小化按钮
        min_button = QPushButton("-", self)  # 使用减号字符
        min_button.setFixedSize(20, 20)
        min_button.setFont(QFont("微軟雅黑", 12))
        min_button.clicked.connect(self.showMinimized)
        min_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #333333;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
        title_bar.addWidget(min_button)

        # 关闭按钮
        close_button = QPushButton("×", self)  # 使用乘号字符
        close_button.setFixedSize(20, 20)
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #333333;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #ff4d4f;
                        color: white;
                    }
                """)
        title_bar.addWidget(close_button)

        layout.addWidget(title_container)  # 添加标题栏容器

        # 添加倒计时显示标签
        self.countdown_label = QLabel("", self)
        # self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #e6875b; font-weight: bold; padding: 5px;margin-top: 10px;")
        self.countdown_label.hide()  # 初始隐藏
        layout.addWidget(self.countdown_label)

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # 无边框
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white; 
                border: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # 创建内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setAlignment(Qt.AlignTop)

        # 状态文本区域
        self.status_textedit = QTextEdit()
        self.status_textedit.setReadOnly(True)
        self.status_textedit.setFont(QFont("微軟雅黑", 10))
        self.status_textedit.setStyleSheet("""
                    QTextEdit {
                        color: #333333;
                        background-color: white;
                        border: none;
                        border: 2px dashed #ffe0e0;
                        border-radius: 4px;
                        padding: 10px;
                        font-size: 14px;
                    }
                """)
        self.status_textedit.append("準備開始任務...")
        content_layout.addWidget(self.status_textedit)

        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)

        # 添加到主布局
        layout.addWidget(scroll_area)  # 替换原来的 status_label

        self.setLayout(layout)

        # 设置亮色主题
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        self.setPalette(palette)

    def closeEvent(self, event):
        """重写关闭事件，发出关闭信号"""
        reply = QMessageBox.question(
            self, "關閉確認", "確認要關閉腳本程序嗎？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close_app_signal.emit()  # 发出关闭应用程序信号
            super().closeEvent(event)
        else:
            event.ignore()

    def update_countdown(self, seconds):
        """更新倒计时显示"""
        if seconds > 0:
            self.countdown_seconds = seconds
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            self.countdown_label.setText(f"休息倒计时:{minutes:02d}:{remaining_seconds:02d}")
            self.countdown_label.show()

            # 启动或重启计时器
            if self.countdown_timer:
                self.countdown_timer.stop()
            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.decrement_countdown)
            self.countdown_timer.start(1000)  # 每秒触发
        else:
            self.countdown_label.hide()
            if self.countdown_timer:
                self.countdown_timer.stop()

    def decrement_countdown(self):
        """减少倒计时"""
        if self.countdown_seconds > 0:
            self.countdown_seconds -= 1
            minutes = self.countdown_seconds // 60
            remaining_seconds = self.countdown_seconds % 60
            self.countdown_label.setText(f"休息倒计时: {minutes:02d}:{remaining_seconds:02d}")
        else:
            self.countdown_label.hide()
            self.countdown_timer.stop()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def update_status(self, text):
        """更新状态文本，追加并滚动到底部"""
        # 追加新状态
        self.status_textedit.append(text)

        # 滚动到底部
        scrollbar = self.status_textedit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # 确保立即显示更新
        QApplication.processEvents()


def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)