from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QFrame, QSizePolicy, QAbstractSpinBox,QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from qasync import QEventLoop, asyncClose, asyncSlot
from FB_middle import main

class likePage(QWidget):
    hideMainRequested = pyqtSignal()
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_events()

        # 默认参数
        self._defaults = {
            'device': '000',
            'refresh': '10',
            'post_count': 50,
            'collect_count': '50',
            'links': ''
        }

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 自定义标题栏 - 添加到右上角
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 5, 5, 5)
        title_bar_layout.setSpacing(10)
        title_bar_layout.addStretch(1)

        btn_min = QPushButton("-")
        btn_min.setFont(QFont("微軟雅黑", 10))
        btn_min.setFixedSize(24, 24)
        btn_min.clicked.connect(self.showMinimized)
        btn_min.setStyleSheet(
            """
            QPushButton { background-color: transparent; border: 1px solid #ddd; border-radius: 12px; }
            QPushButton:hover { background-color: #f0f0f0; }
            """
        )
        title_bar_layout.addWidget(btn_min)

        btn_close = QPushButton("×")
        btn_close.setFont(QFont("微軟雅黑", 10))
        btn_close.setFixedSize(24, 24)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet(
            """
            QPushButton { background-color: transparent; border: 1px solid #ddd; border-radius: 12px; }
            QPushButton:hover { background-color: #ff4d4f; color: white; }
            """
        )
        title_bar_layout.addWidget(btn_close)

        title_bar_container = QFrame()
        title_bar_container.setLayout(title_bar_layout)
        title_bar_container.setStyleSheet("QFrame { background-color: transparent; }")
        root.addWidget(title_bar_container)

        # 主内容容器
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 10, 30, 20)
        content_layout.setSpacing(20)

        # Page title
        title = QLabel("採集點讚用戶")
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title.setFont(QFont("微軟雅黑", 20, QFont.Bold))
        title.setStyleSheet("color: #333333;")
        content_layout.addWidget(title)
        content_layout.addSpacing(5)

        form = QVBoxLayout()
        form.setSpacing(16)

        def add_row(label_text, widget):
            row = QVBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("微軟雅黑", 10))
            row.addWidget(lbl)
            row.addWidget(widget)
            form.addLayout(row)

        self.device_input = QLineEdit()
        self.device_input.setText("000")
        self.device_input.setPlaceholderText("请输入设备唯一标识")

        self.refresh_input = QLineEdit()
        self.refresh_input.setText("10")
        self.refresh_input.setPlaceholderText("瀏覽器頁面刷新")
        self.refresh_input.setValidator(None)

        self.post_count = QSpinBox()
        self.post_count.setRange(1, 1000000)
        self.post_count.setValue(50)
        self.post_count.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.collect_count = QLineEdit()
        self.collect_count.setText("50")

        self.links_text = QTextEdit()
        self.links_text.setPlaceholderText("請輸入指定貼文地址,每行一個...\n例: https://www.facebook.com/steven.cheng.7792/posts/pfbid027Q7XqYq4L54FkA84mwTWt5nkjMjACf7XN38u9c2iVfutUWuW4CWGzdHY9sDpuzEwL")
        self.links_text.setMinimumHeight(120)
        self.links_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.links_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.links_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        add_row("設備號*", self.device_input)
        add_row("刷新數", self.refresh_input)
        add_row("採集贊助帖子數量*", self.post_count)
        add_row("採集數*", self.collect_count)
        add_row("採集指定貼文鏈接", self.links_text)

        form_container = QFrame()
        form_container.setLayout(form)
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout.addWidget(form_container)

        btns = QHBoxLayout()
        btns.setSpacing(12)
        btns.addStretch(1)

        self.reset_btn = QPushButton("重置設置")
        self.save_btn = QPushButton("保存設置")
        self.reset_btn.setObjectName("secondary")
        self.save_btn.setObjectName("primary")
        self.reset_btn.setFixedHeight(36)
        self.save_btn.setFixedHeight(36)
        self.reset_btn.setMinimumWidth(100)
        self.save_btn.setMinimumWidth(100)
        btns.addWidget(self.reset_btn)
        btns.addWidget(self.save_btn)

        content_layout.addLayout(btns)

        # 将内容布局添加到主布局
        root.addLayout(content_layout)
        self.setLayout(root)

        self.setStyleSheet(
            """
            QWidget {
                background-color: transparent;
            }
            QLabel { 
                color: #333333;
                background-color: transparent;
            }
            QLineEdit, QTextEdit, QSpinBox {
                padding: 8px; 
                border: 1px solid #e0e0e0; 
                border-radius: 6px; 
                font-size: 14px;
                background: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border: 1px solid #1890ff; 
                outline: none;
            }
            QPushButton#primary {
                border-radius: 6px; 
                background-color: #ff8800; 
                color: #ffffff; 
                font-weight: bold; 
                border: 0px;
            }
            QPushButton#primary:hover { 
                background-color: #ff9900; 
            }
            QPushButton#primary:pressed { 
                background-color: #cc6600; 
            }
            QPushButton#secondary {
                border-radius: 6px; 
                background-color: #ffe4e4; 
                color: #333333; 
                border: 1px solid #e0e0e0;
            }
            QPushButton#secondary:hover { 
                background-color: #ffe8e8; 
            }
            QPushButton#secondary:pressed { 
                background-color: #ffcccc; 
            }
            """
        )

    def _bind_events(self):
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.save_btn.clicked.connect(self.on_save_clicked)

    def on_reset_clicked(self):
        """恢复默认参数"""
        self.device_input.setText(self._defaults['device'])
        self.refresh_input.setText(self._defaults['refresh'])
        self.post_count.setValue(self._defaults['post_count'])
        self.collect_count.setText(self._defaults['collect_count'])
        self.links_text.setPlainText(self._defaults['links'])

    @asyncSlot()
    async def on_save_clicked(self):
        """打印当前设置（临时日志）"""
        params = {
            'device': self.device_input.text().strip(),
            'refresh': self.refresh_input.text().strip(),
            'post_count': self.post_count.value(),
            'collect_count': self.collect_count.text().strip(),
            'links': [line for line in self.links_text.toPlainText().split('\n') if line.strip()],
            'types':'like'
        }
        print('[Like Settings] 保存设置:', params)


        self.hideMainRequested.emit()

        # 总是创建新的crawler实例，避免资源冲突
        await main(params)




