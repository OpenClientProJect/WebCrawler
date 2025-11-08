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
    task_update_signal = pyqtSignal(list, list)  # 新增：任务更新信号（任务顺序，已完成任务）
    plan_countdown_signal = pyqtSignal(int)  # 添加这个信号

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = resource_path("Thcat.ico")
        self.setWindowTitle('Threads')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 无边框
        self.setFixedSize(600, 550)  # 固定大小
        self.initUI()
        self.update_signal.connect(self.update_status)
        self.task_update_signal.connect(self.update_task_display)  # 连接任务更新信号
        # 设置窗口位置到右上角（距离边缘10像素）
        self.setGeometryToTopRight()
        self.countdown_signal.connect(self.update_countdown)
        self.countdown_timer = None
        self.countdown_seconds = 0
        # 任务相关变量
        self.task_order = []  # 任务顺序
        self.completed_tasks = []  # 已完成任务
        self.task_labels = {}  # 存储任务标签

        # 新增计划时间倒计时相关变量
        self.plan_countdown_signal.connect(self.update_plan_countdown)
        self.plan_countdown_timer = None
        self.plan_countdown_seconds = 0
    def update_plan_countdown(self, seconds):
        """更新计划时间倒计时显示"""
        if seconds > 0:
            self.plan_countdown_seconds = seconds

            # 格式化显示文本
            if seconds < 60:
                display_text = f"計劃時間倒計時: {seconds}秒"
            elif seconds < 3600:
                minutes = seconds // 60
                remaining_seconds = seconds % 60
                display_text = f"計劃時間倒計時: {minutes}分{remaining_seconds:02d}秒"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                display_text = f"計劃時間倒計時: {hours}小时{minutes:02d}分"

            self.plan_countdown_label.setText(display_text)
            self.plan_countdown_label.show()

            # 启动或重启计时器
            if self.plan_countdown_timer:
                self.plan_countdown_timer.stop()

            self.plan_countdown_timer = QTimer(self)
            self.plan_countdown_timer.timeout.connect(self.decrement_plan_countdown)
            self.plan_countdown_timer.start(1000)
        else:
            self.plan_countdown_label.hide()
            if self.plan_countdown_timer:
                self.plan_countdown_timer.stop()

    def decrement_plan_countdown(self):
        """减少计划时间倒计时"""
        if self.plan_countdown_seconds > 0:
            self.plan_countdown_seconds -= 1

            # 更新显示
            if self.plan_countdown_seconds < 60:
                display_text = f"計劃時間倒計時: {self.plan_countdown_seconds}秒"
            elif self.plan_countdown_seconds < 3600:
                minutes = self.plan_countdown_seconds // 60
                remaining_seconds = self.plan_countdown_seconds % 60
                display_text = f"計劃時間倒計時: {minutes}分{remaining_seconds:02d}秒"
            else:
                hours = self.plan_countdown_seconds // 3600
                minutes = (self.plan_countdown_seconds % 3600) // 60
                display_text = f"計劃時間倒計時: {hours}小时{minutes:02d}分"

            self.plan_countdown_label.setText(display_text)
        else:
            self.plan_countdown_label.hide()
            self.plan_countdown_timer.stop()
    # 新增方法：设置窗口到右上角
    def setGeometryToTopRight(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        x = screen_geometry.width() - self.width() - 10  # 距离右边10像素
        y = 10  # 距离顶部10像素
        self.move(x, y)

    def initUI(self):
        # 主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 修改：移除边距让标题栏可以铺满
        layout.setSpacing(0)  # 修改：移除间距

        # 左侧任务方块区域
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(200)  # 固定宽度
        self.left_panel.setStyleSheet("background-color: #fce3c2; border-right: 1px solid #e0e0e0;")

        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 50, 10, 10)
        left_layout.setSpacing(10)

        # 任务标题
        task_title = QLabel("任務隊列")
        task_title.setFont(QFont("微软雅黑", 12, QFont.Bold))
        task_title.setStyleSheet("color: #f7b36a; padding: 5px; border-bottom: 1px solid #f7b36a;")
        task_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(task_title)

        # 任务容器（滚动区域）
        task_scroll = QScrollArea()
        task_scroll.setWidgetResizable(True)
        task_scroll.setFrameShape(QFrame.NoFrame)
        task_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: transparent;
                        border: none;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: #f0f0f0;
                        width: 6px;
                        margin: 0px;
                        border-radius: 3px;
                    }
                    QScrollBar::handle:vertical {
                        background: #c1b8ff;
                        min-height: 20px;
                        border-radius: 3px;
                    }
                """)

        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(8)
        self.task_layout.setContentsMargins(5, 5, 5, 5)

        task_scroll.setWidget(self.task_container)
        left_layout.addWidget(task_scroll)

        # 添加到主布局
        layout.addWidget(self.left_panel)

        # 右侧内容区域
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 标题栏容器
        title_container = QWidget()
        title_container.setFixedHeight(40)  # 设置标题栏高度
        title_container.setStyleSheet(
            "background-color: #fce3c2; border-top-right-radius: 8px;")

        title_bar = QHBoxLayout(title_container)
        title_bar.setContentsMargins(15, 0, 15, 0)

        self.title_label = QLabel("執行任務狀態")
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #333333; background: transparent;")
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)  # 添加弹性空间

        # 最小化按钮
        min_button = QPushButton("", self)  # 修改：使用减号字符
        min_button.setFixedSize(20, 20)
        min_button.setFont(QFont("Arial", 12, QFont.Bold))
        min_button.clicked.connect(self.showMinimized)
        min_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f7b36a;
                        color: white;
                        border-radius: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #fce3c2;
                    }
                    QPushButton:pressed {
                        background-color: #4a3aac;
                    }
                """)
        title_bar.addWidget(min_button)

        # 关闭按钮
        close_button = QPushButton("", self)  # 修改：使用乘号字符
        close_button.setFixedSize(20, 20)
        close_button.setFont(QFont("Arial", 12, QFont.Bold))
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f7b36a;
                        color: white;
                        border-radius: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #ff5252;
                    }
                    QPushButton:pressed {
                        background-color: #ff3838;
                    }
                """)
        title_bar.addWidget(close_button)

        right_layout.addWidget(title_container)  # 添加标题栏容器

        # 添加倒计时显示标签
        self.countdown_label = QLabel("", self)
        # self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #e6875b; font-weight: bold; padding: 5px;margin-top: 10px;")
        self.countdown_label.hide()  # 初始隐藏
        right_layout.addWidget(self.countdown_label)

        # 添加计划时间倒计时标签 - 放在休息倒计时下面
        self.plan_countdown_label = QLabel("", self)
        self.plan_countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.plan_countdown_label.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 5px; margin-top: 10px;")
        self.plan_countdown_label.hide()
        right_layout.addWidget(self.plan_countdown_label)

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # 无边框
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #8b8b8b; 
                border: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #fce3c2;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a89cf9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # 创建内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #fffaf2;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 15)
        content_layout.setAlignment(Qt.AlignTop)

        # 状态文本区域
        self.status_textedit = QTextEdit()
        self.status_textedit.setReadOnly(True)
        self.status_textedit.setFont(QFont("微軟雅黑", 10))
        self.status_textedit.setStyleSheet("""
                    QTextEdit {
                        color: #3c9d6d;
                        background-color: #ffffff;
                        border: none;
                        border-radius: 10px;
                        border: 2px dashed #f9ecdb;
                        padding: 10px;
                        font-size: 14px;
                    }
                """)
        self.status_textedit.append("準備開始任務...")
        content_layout.addWidget(self.status_textedit)

        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        right_layout.addWidget(scroll_area)
        # 添加到主布局
        layout.addWidget(right_container)  # 替换原来的 status_label

        self.setLayout(layout)

        # 设置暗色主题
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 250, 242))
        palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        self.setPalette(palette)
    def update_task_display(self, task_order, completed_tasks):
        """更新任务显示"""
        self.task_order = task_order
        self.completed_tasks = completed_tasks  # 现在 completed_tasks 包含的是唯一标识符
        self.refresh_task_display()

    def refresh_task_display(self):
        """刷新任务显示"""
        # 清除现有任务标签
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.task_labels.clear()

        # 任务名称映射
        task_names = {
            0: "首頁留言",
            1: "關鍵字任務",
            2: "個人發文",
            3: "用戶留言",
            4: "休息時間"
        }

        # 任务颜色映射
        task_colors = {
            0: "#ffcccb",
            1: "#b2f0b2",
            2: "#ccccff",
            3: "#f8bbd0",
            4: "#e6e6fa"
        }

        # 显示当前任务队列 - 使用位置而不是索引作为唯一标识
        for position, task_index in enumerate(self.task_order):
            # 使用位置和索引的组合作为唯一标识
            task_id = f"{position}_{task_index}"

            # 检查这个特定的任务实例是否完成
            is_completed = task_id in self.completed_tasks

            task_frame = QFrame()
            task_frame.setFixedHeight(60)
            task_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {task_colors.get(task_index, "#cccccc")};
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    margin: 2px;
                }}
            """)

            task_layout = QHBoxLayout(task_frame)
            task_layout.setContentsMargins(8, 4, 8, 4)

            # 任务名称
            name_label = QLabel(task_names.get(task_index, f"{task_index}"))
            name_label.setFont(QFont("微软雅黑", 9))
            name_label.setStyleSheet("color: white; font-weight: bold;")

            # 状态指示器 - 修改为显示倒计时或完成标记
            if is_completed:
                # 已完成：显示✓
                status_label = QLabel("✓")
                status_label.setFont(QFont("Arial", 12, QFont.Bold))
                status_label.setStyleSheet("color: #00ff00;")
            else:
                # 未完成：显示倒计时
                # 获取任务的剩余时间（如果有的话）
                remaining_time = getattr(self, 'task_remaining_times', {}).get(task_id, 0)
                if remaining_time > 0:
                    # 显示格式化的时间
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60
                    time_text = f"{minutes:02d}:{seconds:02d}"
                    status_label = QLabel(time_text)
                    status_label.setFont(QFont("Arial", 10, QFont.Bold))
                    status_label.setStyleSheet("color: #ffff00;")  # 黄色显示倒计时
                else:
                    # 没有倒计时信息，显示默认状态
                    status_label = QLabel("●")
                    status_label.setFont(QFont("Arial", 12, QFont.Bold))
                    status_label.setStyleSheet("color: #ffff00;")

            status_label.setAlignment(Qt.AlignCenter)
            status_label.setFixedSize(40, 20)

            # task_layout.addWidget(seq_label)
            task_layout.addWidget(name_label)
            task_layout.addStretch(1)
            task_layout.addWidget(status_label)

            self.task_layout.addWidget(task_frame)
            self.task_labels[task_id] = task_frame

    def update_task_countdown(self, task_id, remaining_seconds):
        """更新特定任务的倒计时显示"""
        # 存储任务的剩余时间
        if not hasattr(self, 'task_remaining_times'):
            self.task_remaining_times = {}

        self.task_remaining_times[task_id] = remaining_seconds

        # 如果该任务标签存在，则更新显示
        if task_id in self.task_labels:
            task_frame = self.task_labels[task_id]
            # 找到状态标签（布局中的最后一个widget）
            layout = task_frame.layout()
            if layout and layout.count() > 0:
                status_widget = layout.itemAt(layout.count() - 1).widget()
                if isinstance(status_widget, QLabel):
                    if remaining_seconds > 0:
                        # 显示格式化的时间
                        minutes = remaining_seconds // 60
                        seconds = remaining_seconds % 60
                        time_text = f"{minutes:02d}:{seconds:02d}"
                        status_widget.setText(time_text)
                        status_widget.setStyleSheet("color: #ffff00;")
                        status_widget.setFont(QFont("Arial", 10, QFont.Bold))
                    else:
                        # 如果任务已完成，应该已经在completed_tasks中，这里不需要处理
                        # 保持原有的完成状态显示
                        pass
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
            self.countdown_label.setText(f"休息倒計時:{minutes:02d}:{remaining_seconds:02d}")
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