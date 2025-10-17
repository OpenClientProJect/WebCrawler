
import os
import sys

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout,
                            QPushButton, QMessageBox, QWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap


class ProgressWindow(QDialog):
    update_signal = pyqtSignal(str, str, dict)  # 类型，URL，用户数据

    def __init__(self):
        super().__init__()
        icon_path = resource_path("IGicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Instagram 爬取進度")
        self.setFixedSize(800, 600)
        self.counters = {
            'comment': 0,
            'like': 0,
            'follower': 0,
            'keyword': 0
        }
        self.current_counts = {}  # 当前任务计数
        self.current_task_label = QLabel("當前任務：無")  # 新增当前任务标签

        # 鼠标拖拽相关
        self.drag_pos = None

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建标题栏
        self.create_header(main_layout)

        # 创建内容区域
        self.create_content_area(main_layout)

        self.setLayout(main_layout)
        self.update_signal.connect(self.update_display)

    def create_header(self, main_layout):
        """创建蓝紫渐变标题栏"""
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #405de6, stop:1 #833ab4);
            }
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # 左侧标题
        title_label = QLabel("Instagram 爬取進度")
        title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent; border: none;")
        header_layout.addWidget(title_label)

        # 中间伸缩空间
        header_layout.addStretch(1)

        # 右侧控制按钮
        self.min_btn = QPushButton("-")
        self.min_btn.setFont(QFont("微軟雅黑", 12))
        self.min_btn.setFixedSize(24, 24)
        self.min_btn.clicked.connect(self.showMinimized)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        header_layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.setFont(QFont("微軟雅黑", 12))
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        header_layout.addWidget(self.close_btn)

        main_layout.addWidget(header_widget)

    def create_content_area(self, main_layout):
        """创建内容区域"""
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 0px 0px 15px 15px;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # 当前任务区域
        self.create_current_task_section(content_layout)

        # 进度卡片区域（四列水平布局）
        self.create_progress_cards(content_layout)

        # 日志区域
        self.create_log_section(content_layout)

        main_layout.addWidget(content_widget)

    def create_current_task_section(self, layout):
        """创建当前任务显示区域"""
        task_widget = QFrame()
        task_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e5e9;
            }
        """)
        task_widget.setFixedHeight(40)

        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(15, 10, 15, 10)
        task_layout.setAlignment(Qt.AlignVCenter)

        # 任务图标
        task_icon = QLabel()
        task_pixmap = QPixmap()
        task_pixmap.load(resource_path("./image/list.png"))
        if not task_pixmap.isNull():
            task_icon.setPixmap(task_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        task_icon.setStyleSheet("background: transparent; border: none;")
        task_icon.setAlignment(Qt.AlignVCenter)
        task_layout.addWidget(task_icon)

        # 当前任务标签
        self.current_task_label.setFont(QFont("微軟雅黑", 10))
        self.current_task_label.setStyleSheet("color: #333; background: transparent; border: none; margin-left: 10px;")
        self.current_task_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        task_layout.addWidget(self.current_task_label)

        task_layout.addStretch(1)

        layout.addWidget(task_widget)

    def create_progress_cards(self, layout):
        """创建四列水平布局的进度卡片"""
        cards_widget = QWidget()
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setSpacing(15)

        # 创建4个进度卡片
        self.progress_cards = {}
        card_types = [
            ('comment', '評論用戶'),
            ('like', '點讚用戶'),
            ('follower', '粉絲用戶'),
            ('keyword', '關鍵詞用戶')
        ]

        for card_type, card_name in card_types:
            card = self.create_progress_card(card_name)
            self.progress_cards[card_type] = card
            cards_layout.addWidget(card)

        layout.addWidget(cards_widget)

    def create_progress_card(self, title):
        """创建单个进度卡片"""
        card = QFrame()
        card.setFixedSize(180, 100)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e5e9;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("微軟雅黑", 9))
        title_label.setStyleSheet("color: #666; background: transparent; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        # 数字
        number_label = QLabel("0")
        number_label.setFont(QFont("微軟雅黑", 24, QFont.Bold))
        number_label.setStyleSheet("color: #6b7de9; background: transparent; border: none;")
        number_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(number_label)

        # 存储数字标签的引用
        card.number_label = number_label

        return card

    def create_log_section(self, layout):
        """创建日志显示区域"""
        log_widget = QFrame()
        log_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e5e9;
            }
        """)

        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(15, 15, 15, 15)

        # 日志标题
        log_title = QLabel("爬取日誌")
        log_title.setFont(QFont("微軟雅黑", 10, QFont.Bold))
        log_title.setStyleSheet("color: #333; background: transparent; border: none; margin-bottom: 10px;")
        log_layout.addWidget(log_title)

        # 日志显示区域
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e1e5e9;
                border-radius: 5px;
                padding: 10px;
                color: #333;
            }
        """)
        log_layout.addWidget(self.log_view)

        layout.addWidget(log_widget)

    @pyqtSlot(str, str, dict)
    def update_display(self, task_type, url, user_data):
        # 定义任务类型的中文映射（新增 "keyword" 对应 "关键词搜索用户"）
        task_name_map = {
            'comment': '評論用戶',
            'like': '點讚用戶',
            'follower': '粉絲用戶',
            'keyword': '關鍵詞用戶'
        }

        # 更新全局统计
        self.counters[task_type] += 1

        # 更新进度卡片中的数字
        if task_type in self.progress_cards:
            self.progress_cards[task_type].number_label.setText(str(self.counters[task_type]))

        # 更新当前任务计数
        current_count = self.current_counts.get(url, 0) + 1
        self.current_counts[url] = current_count

        # 生成中文日志条目
        log_entry = (
            f"{current_count} {task_name_map[task_type]}: "  # 使用中文任务类型
            f"ID: {user_data['id']} / "
            f"Name: {user_data['username']} / "
            f"Full Name: {user_data['full_name']}"
        )
        self.log_view.append(log_entry)

    def start_task(self, task_type, url):
        """开始新任务时重置当前计数"""
        self.current_counts[url] = 0
        task_name = {
            'comment': '評論用戶',
            'like': '點讚用戶',
            'follower': '粉絲用戶',
            'keyword': '關鍵詞用戶'
        }.get(task_type, task_type)
        self.current_task_label.setText(f"當前任務：正在採集 {task_name} ({url})")
        self.log_view.append(f"=== 開始採集 [{task_name}] {url} ===")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "關閉確認", "確認要關閉爬取程序嗎？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            super().closeEvent(event)
        else:
            event.ignore()
def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
