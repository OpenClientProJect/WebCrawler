# log_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ProgressWindow(QDialog):
    update_signal = pyqtSignal(str, str, dict)  # 类型，URL，用户数据

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("爬取進度")
        self.setFixedSize(600, 400)
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

        # 创建布局
        layout = QVBoxLayout()

        # 标题栏
        title_bar = QHBoxLayout()
        self.title_label = QLabel("IG爬取進度")
        self.title_label.setFont(QFont("微软雅黑", 12))
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()

        # 新增缩小按钮
        self.min_btn = QPushButton("-")
        self.min_btn.setFont(QFont("微軟雅黑", 12))
        self.min_btn.setFixedSize(24, 24)
        self.min_btn.clicked.connect(self.showMinimized)
        title_bar.addWidget(self.min_btn)

        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFont(QFont("微軟雅黑", 12))
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.close)
        title_bar.addWidget(self.close_btn)

        # 标题栏样式
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: #606060;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #606060;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)

        layout.addLayout(title_bar)

        # 当前任务显示
        self.current_task_label.setFont(QFont("微软雅黑", 9))
        layout.addWidget(self.current_task_label)

        # 统计面板（已改为中文）
        stats_layout = QHBoxLayout()
        self.stats_labels = {
            'comment': QLabel("評論用戶: 0"),
            'like': QLabel("點贊用戶: 0"),
            'follower': QLabel("粉絲用戶: 0"),
            'keyword': QLabel("關鍵詞用戶: 0")
        }
        for label in self.stats_labels.values():
            label.setFont(QFont("微软雅黑", 8))
            stats_layout.addWidget(label)
        layout.addLayout(stats_layout)

        # 实时数据显示
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_view)

        self.setLayout(layout)
        self.update_signal.connect(self.update_display)

    def update_display(self, task_type, url, user_data):
        # 定义任务类型的中文映射（新增 "keyword" 对应 "关键词搜索用户"）
        task_name_map = {
            'comment': '評論用戶',
            'like': '點贊用戶',
            'follower': '粉絲用戶',
            'keyword': '關鍵詞用戶'
        }

        # 更新全局统计
        self.counters[task_type] += 1
        self.stats_labels[task_type].setText(f"{task_name_map[task_type]}: {self.counters[task_type]}")

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
            'comment': '评论用户',
            'like': '点赞用户',
            'follower': '粉丝用户',
            'keyword': '关键词用户'
        }.get(task_type, task_type)
        self.current_task_label.setText(f"当前任务：正在采集 {task_name} ({url})")
        self.log_view.append(f"=== 开始采集 [{task_name}] {url} ===")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "關閉確認", "確認要關閉爬取程序嗎？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.window_closed.emit()
            super().closeEvent(event)
        else:
            event.ignore()