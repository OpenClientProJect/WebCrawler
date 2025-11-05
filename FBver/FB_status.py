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
#
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
#         layout.setContentsMargins(0, 0, 0, 0)  # 修改：移除边距让标题栏可以铺满
#         layout.setSpacing(0)  # 修改：移除间距
#
#         # 标题栏容器
#         title_container = QWidget()
#         title_container.setFixedHeight(40)  # 设置标题栏高度
#         title_container.setStyleSheet(
#             "background-color: #fce3c2; border-top-left-radius: 8px; border-top-right-radius: 8px;")
#
#         title_bar = QHBoxLayout(title_container)
#         title_bar.setContentsMargins(15, 0, 15, 0)
#
#         self.title_label = QLabel("執行任務狀態")
#         self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
#         self.title_label.setStyleSheet("color: #333333; background: transparent;")
#         title_bar.addWidget(self.title_label)
#         title_bar.addStretch(1)  # 添加弹性空间
#
#         # 最小化按钮
#         min_button = QPushButton("", self)  # 修改：使用减号字符
#         min_button.setFixedSize(20, 20)
#         min_button.setFont(QFont("Arial", 12, QFont.Bold))
#         min_button.clicked.connect(self.showMinimized)
#         min_button.setStyleSheet("""
#                     QPushButton {
#                         background-color: #f7b36a;
#                         color: white;
#                         border-radius: 10px;
#                         border: none;
#                     }
#                     QPushButton:hover {
#                         background-color: #fce3c2;
#                     }
#                     QPushButton:pressed {
#                         background-color: #4a3aac;
#                     }
#                 """)
#         title_bar.addWidget(min_button)
#
#         # 关闭按钮
#         close_button = QPushButton("", self)  # 修改：使用乘号字符
#         close_button.setFixedSize(20, 20)
#         close_button.setFont(QFont("Arial", 12, QFont.Bold))
#         close_button.clicked.connect(self.close)
#         close_button.setStyleSheet("""
#                     QPushButton {
#                         background-color: #f7b36a;
#                         color: white;
#                         border-radius: 10px;
#                         border: none;
#                     }
#                     QPushButton:hover {
#                         background-color: #ff5252;
#                     }
#                     QPushButton:pressed {
#                         background-color: #ff3838;
#                     }
#                 """)
#         title_bar.addWidget(close_button)
#
#         layout.addWidget(title_container)  # 添加标题栏容器
#
#         # 添加倒计时显示标签
#         self.countdown_label = QLabel("", self)
#         # self.countdown_label.setAlignment(Qt.AlignCenter)
#         self.countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
#         self.countdown_label.setStyleSheet("color: #e6875b; font-weight: bold; padding: 5px;margin-top: 10px;")
#         self.countdown_label.hide()  # 初始隐藏
#         layout.addWidget(self.countdown_label)
#
#         # 创建滚动区域
#         scroll_area = QScrollArea(self)
#         scroll_area.setWidgetResizable(True)
#         scroll_area.setFrameShape(QFrame.NoFrame)  # 无边框
#         scroll_area.setStyleSheet("""
#             QScrollArea {
#                 background-color: #8b8b8b;
#                 border: none;
#                 border-bottom-left-radius: 8px;
#                 border-bottom-right-radius: 8px;
#             }
#             QScrollBar:vertical {
#                 border: none;
#                 background: #f0f0f0;
#                 width: 10px;
#                 margin: 0px;
#                 border-radius: 5px;
#             }
#             QScrollBar::handle:vertical {
#                 background: #fce3c2;
#                 min-height: 20px;
#                 border-radius: 5px;
#             }
#             QScrollBar::handle:vertical:hover {
#                 background: #a89cf9;
#             }
#             QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
#                 height: 0px;
#             }
#             QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
#                 background: none;
#             }
#         """)
#
#         # 创建内容容器
#         content_widget = QWidget()
#         content_widget.setStyleSheet("background-color: #fffaf2;")
#         content_layout = QVBoxLayout(content_widget)
#         content_layout.setContentsMargins(15, 10, 15, 15)
#         content_layout.setAlignment(Qt.AlignTop)
#
#         # 状态文本区域
#         self.status_textedit = QTextEdit()
#         self.status_textedit.setReadOnly(True)
#         self.status_textedit.setFont(QFont("微軟雅黑", 10))
#         self.status_textedit.setStyleSheet("""
#                     QTextEdit {
#                         color: #3c9d6d;
#                         background-color: #ffffff;
#                         border: none;
#                         border-radius: 10px;
#                         border: 2px dashed #f9ecdb;
#                         padding: 10px;
#                         font-size: 14px;
#                     }
#                 """)
#         self.status_textedit.append("準備開始任務...")
#         content_layout.addWidget(self.status_textedit)
#
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
#         palette.setColor(QPalette.Window, QColor(255, 250, 242))
#         palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
#         palette.setColor(QPalette.Base, QColor(255, 255, 255))
#         self.setPalette(palette)
#
#     def closeEvent(self, event):
#         """重写关闭事件，发出关闭信号"""
#         reply = QMessageBox.question(
#             self, "關閉確認", "確認要關閉腳本程序嗎？",
#             QMessageBox.Yes | QMessageBox.No, QMessageBox.No
#         )
#         if reply == QMessageBox.Yes:
#             self.close_app_signal.emit()  # 发出关闭应用程序信号
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
#             self.countdown_label.setText(f"休息倒计时:{minutes:02d}:{remaining_seconds:02d}")
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
#
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
#
# def resource_path(relative_path):
#     """获取资源的绝对路径"""
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, \
    QScrollArea, QFrame, QWidget, QTextEdit


class StatusWindow(QDialog):
    update_signal = pyqtSignal(str)  # 信号：更新状态文本
    countdown_signal = pyqtSignal(int)  # 新增：倒计时信号
    task_update_signal = pyqtSignal(list, list)  # 新增：任务更新信号（任务顺序，已完成任务）
    plan_countdown_signal = pyqtSignal(int)  # 添加这个信号
    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = resource_path("image/FB_it.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 无边框
        self.setFixedSize(600, 550)  # 增加宽度以容纳左右布局
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

    # 在 StatusWindow 类中添加以下方法

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
        # 设置窗口样式 - 圆角和阴影效果
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 8px;
            }
        """)
        
        # 主布局 - 改为水平布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧任务方块区域（30-35%宽度）
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 任务标题栏
        task_title_bar = QWidget()
        task_title_bar.setFixedHeight(50)
        task_title_bar.setStyleSheet("background-color: #edf6f7;")
        task_title_layout = QVBoxLayout(task_title_bar)
        task_title_layout.setContentsMargins(15, 10, 15, 10)
        task_title_layout.setSpacing(0)
        
        task_title = QLabel("任務隊列")
        task_title.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        task_title.setStyleSheet("color: #82c3ed; background: transparent;")
        task_title_layout.addWidget(task_title)
        
        # 分隔线
        # separator = QFrame()
        # separator.setFixedHeight(1)
        # separator.setStyleSheet("background-color: #b3d9ff;")
        # task_title_layout.addWidget(separator)
        
        left_layout.addWidget(task_title_bar)

        # 任务容器（滚动区域）- 白色背景
        task_scroll = QScrollArea()
        task_scroll.setWidgetResizable(True)
        task_scroll.setFrameShape(QFrame.NoFrame)
        task_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
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
        self.task_container.setStyleSheet("background-color: #ffffff;")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(10)
        self.task_layout.setContentsMargins(10, 10, 10, 10)

        task_scroll.setWidget(self.task_container)
        left_layout.addWidget(task_scroll)
        
        # 设置左侧面板宽度比例（约30-35%）
        main_layout.addWidget(self.left_panel, 1)

        # 右侧内容区域（65-70%宽度）
        right_container = QWidget()
        right_container.setStyleSheet("background-color: #ffffff;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 标题栏容器
        title_container = QWidget()
        title_container.setFixedHeight(50)
        title_container.setStyleSheet("background-color: #e8f4f5;")

        title_bar = QVBoxLayout(title_container)
        title_bar.setContentsMargins(15, 10, 15, 10)
        title_bar.setSpacing(0)
        
        title_hbox = QHBoxLayout()
        title_hbox.setContentsMargins(0, 0, 0, 0)
        title_hbox.setSpacing(8)  # 设置按钮之间的间距
        
        self.title_label = QLabel("執行任務狀態")
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #82c3ed; background: transparent;")
        title_hbox.addWidget(self.title_label)
        title_hbox.addStretch(1)
        
        # 窗口控制按钮
        min_button = QPushButton("", self)
        min_button.setFixedSize(12, 12)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #29b6f6;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        title_hbox.addWidget(min_button)
        
        close_button = QPushButton("", self)
        close_button.setFixedSize(12, 12)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4caf50;
            }
        """)
        close_button.clicked.connect(self.close)
        title_hbox.addWidget(close_button)
        
        title_bar.addLayout(title_hbox)
        
        # 分隔线
        # separator2 = QFrame()
        # separator2.setFixedHeight(1)
        # separator2.setStyleSheet("background-color: #b3d9ff;")
        # title_bar.addWidget(separator2)

        right_layout.addWidget(title_container)

        # 添加倒计时显示标签
        self.countdown_label = QLabel("", self)
        self.countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #aa55ff; font-weight: bold; padding: 5px; margin-top: 10px;")
        self.countdown_label.hide()
        right_layout.addWidget(self.countdown_label)

        # 添加计划时间倒计时标签 - 放在休息倒计时下面
        self.plan_countdown_label = QLabel("", self)
        self.plan_countdown_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.plan_countdown_label.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 5px; margin-top: 10px;")
        self.plan_countdown_label.hide()
        right_layout.addWidget(self.plan_countdown_label)

        # 创建滚动区域 - 白色背景
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff; 
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c1b8ff;
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

        # 创建内容容器（无边框，只作为容器）
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ffffff;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setAlignment(Qt.AlignTop)

        # 状态文本区域 - 添加虚线边框
        self.status_textedit = QTextEdit()
        self.status_textedit.setReadOnly(True)
        self.status_textedit.setFont(QFont("微軟雅黑", 10))
        # 禁用 QTextEdit 自己的滚动条，使用外层滚动条
        self.status_textedit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.status_textedit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.status_textedit.setStyleSheet("""
            QTextEdit {
                color: #333333;
                background-color: #ffffff;
                border: 2px dashed #b3d9ff;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.status_textedit.append("準備開始任務...")
        content_layout.addWidget(self.status_textedit)

        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        right_layout.addWidget(scroll_area)

        # 将右侧区域添加到主布局（65-70%宽度）
        main_layout.addWidget(right_container, 2)

        self.setLayout(main_layout)

        # 设置浅色主题
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
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
            0: "循環發文",
            1: "循環推文",
            2: "循環加社團",
            3: "養號",
            4: "粉絲專頁",
            5: "休息時間"
        }

        # 任务颜色映射（用于非活动任务的轻微颜色提示）
        task_light_colors = {
            0: "#82c3ec",  #蓝色
            1: "#d5eadd",  #绿色
            2: "#ffefd5",  #黄色
            3: "#e9d5ff",  #紫色
            4: "#fce4ec",  #粉色
            5: "#ffefd5"   #黄色（休息时间）
        }
        
        # 活动任务颜色（浅蓝色）
        active_task_color = "#90CAF9"
        
        # 当前活动任务ID（用于判断哪个任务是活动的）
        current_active_task = getattr(self, 'current_active_task_id', None)

        # 显示当前任务队列 - 使用位置而不是索引作为唯一标识
        for position, task_index in enumerate(self.task_order):
            # 使用位置和索引的组合作为唯一标识
            task_id = f"{position}_{task_index}"

            # 检查这个特定的任务实例是否完成
            is_completed = task_id in self.completed_tasks
            
            # 判断是否是当前活动任务（有倒计时且未完成）
            is_active = (task_id == current_active_task) and not is_completed
            
            # 获取任务的剩余时间
            remaining_time = getattr(self, 'task_remaining_times', {}).get(task_id, 0)
            
            # 如果有倒计时且未完成，则是活动任务
            if remaining_time > 0 and not is_completed:
                is_active = True
                self.current_active_task_id = task_id

            task_frame = QFrame()
            task_frame.setFixedHeight(50)
            
            if is_active:
                # 活动任务：浅蓝色实心背景，白色文字
                task_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {active_task_color};
                        border-radius: 8px;
                        margin: 2px;
                    }}
                """)
            else:
                # 非活动任务：非常浅的背景，有轻微颜色提示
                task_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {task_light_colors.get(task_index, "#ffffff")};
                        border-radius: 8px;
                        margin: 2px;
                    }}
                """)

            task_layout = QHBoxLayout(task_frame)
            task_layout.setContentsMargins(12, 8, 12, 8)

            # 任务名称
            name_label = QLabel(task_names.get(task_index, f"{task_index}"))
            name_label.setFont(QFont("微軟雅黑", 10))
            if is_active:
                name_label.setStyleSheet("color: white; font-weight: bold;")
            else:
                name_label.setStyleSheet("color: #333333; font-weight: normal;")

            # 状态指示器
            status_label = None
            if is_active:
                # 活动任务：显示倒计时（白色文字）
                if remaining_time > 0:
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60
                    time_text = f"{minutes:02d}:{seconds:02d}"
                    status_label = QLabel(time_text)
                    status_label.setFont(QFont("Arial", 11, QFont.Bold))
                    status_label.setStyleSheet("color: white;")
                    status_label.setAlignment(Qt.AlignCenter)
                    status_label.setMinimumWidth(50)
                else:
                    status_label = QLabel("")
                    status_label.setFixedSize(0, 0)
            elif is_completed:
                # 已完成：不显示任何标记
                status_label = QLabel("")
                status_label.setFixedSize(0, 0)
            else:
                # 非活动未完成：显示黄色小圆圈
                status_label = QLabel("●")
                status_label.setFont(QFont("Arial", 10, QFont.Bold))
                status_label.setStyleSheet("color: #ffd700;")  # 黄色
                status_label.setFixedSize(12, 12)
                status_label.setAlignment(Qt.AlignCenter)

            task_layout.addWidget(name_label)
            task_layout.addStretch(1)
            if status_label:
                task_layout.addWidget(status_label)
                # 存储状态标签的引用，以便后续更新
                task_frame.status_label = status_label

            self.task_layout.addWidget(task_frame)
            self.task_labels[task_id] = task_frame

    def update_task_countdown(self, task_id, remaining_seconds):
        """更新特定任务的倒计时显示"""
        # 存储任务的剩余时间
        if not hasattr(self, 'task_remaining_times'):
            self.task_remaining_times = {}

        old_active_task = getattr(self, 'current_active_task_id', None)
        self.task_remaining_times[task_id] = remaining_seconds
        
        # 更新当前活动任务ID
        if remaining_seconds > 0:
            self.current_active_task_id = task_id
        else:
            if hasattr(self, 'current_active_task_id') and self.current_active_task_id == task_id:
                self.current_active_task_id = None

        # 如果活动任务发生变化，需要刷新整个列表以更新样式
        if old_active_task != self.current_active_task_id:
            self.refresh_task_display()
            return

        # 如果任务标签存在，直接更新其时间显示（避免完全刷新）
        if task_id in self.task_labels:
            task_frame = self.task_labels[task_id]
            if hasattr(task_frame, 'status_label') and task_frame.status_label:
                status_label = task_frame.status_label
                if remaining_seconds > 0:
                    # 更新倒计时显示
                    minutes = remaining_seconds // 60
                    seconds = remaining_seconds % 60
                    time_text = f"{minutes:02d}:{seconds:02d}"
                    status_label.setText(time_text)
                    status_label.setStyleSheet("color: white;")
                    status_label.setFont(QFont("Arial", 11, QFont.Bold))
                    status_label.setAlignment(Qt.AlignCenter)
                    status_label.setMinimumWidth(50)
                    status_label.show()
                else:
                    # 如果倒计时结束，隐藏时间显示
                    status_label.hide()

    def closeEvent(self, event):
        """重写关闭事件，发出关闭信号"""
        # 创建消息框实例
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("關閉確認")
        msg_box.setText("確認要關閉腳本程序嗎？")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # 设置样式表
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        reply = msg_box.exec_()

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
            self.countdown_timer.start(1000)
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
            self.countdown_label.setText(f"休息倒計時: {minutes:02d}:{remaining_seconds:02d}")
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
