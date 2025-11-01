import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QFrame, QSizePolicy, QAbstractSpinBox,QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from qasync import QEventLoop, asyncClose, asyncSlot
from PyQt5.QtSvg import QSvgWidget
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

        def add_row(label_text, widget, warning_text=None):
            row = QVBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("微軟雅黑", 10))
            row.addWidget(lbl)
            row.addWidget(widget)
            
            # 如果提供了文本，添加警告提示
            if warning_text:
                warning_layout = QHBoxLayout()
                warning_layout.setSpacing(8)
                warning_layout.setContentsMargins(0, 0, 0, 0)
                
                # 警告图标
                warn_icon_path = resource_path("image/warn.svg")
                warn_icon = QSvgWidget(warn_icon_path)
                warn_icon.setFixedSize(20, 20)
                warning_layout.addWidget(warn_icon)
                
                # 警告文本
                warn_label = QLabel(warning_text)
                warn_label.setFont(QFont("微軟雅黑", 9))
                warn_label.setStyleSheet("color: #333333;")
                warning_layout.addWidget(warn_label)
                warning_layout.addStretch()
                
                row.addLayout(warning_layout)
            
            form.addLayout(row)
        
        def resource_path(relative_path):
            """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

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
        self.links_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        add_row("設備號*", self.device_input)
        add_row("刷新數", self.refresh_input)
        add_row("採集贊助帖子數量*", self.post_count, "贊助貼文與指定貼文僅能二選一進行採集")
        add_row("採集數*", self.collect_count)
        add_row("採集指定貼文鏈接", self.links_text)

        content_layout.addLayout(form)

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




