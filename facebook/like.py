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
            'device': '',
            'refresh': '10',
            'post_count': 50,
            'collect_count': '50',
            'links': ''
        }

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(10, 15, 10, 15)
        root.setSpacing(14)

        # title = QLabel("系统设置")
        # title.setAlignment(Qt.AlignHCenter)
        # title.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        # root.addWidget(title)

        form = QVBoxLayout()
        form.setSpacing(12)

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
        self.refresh_input.setText("30")
        self.refresh_input.setPlaceholderText("瀏覽器頁面刷新")
        self.refresh_input.setValidator(None)

        self.post_count = QSpinBox()
        self.post_count.setRange(1, 1000000)
        self.post_count.setValue(50)
        self.post_count.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.collect_count = QLineEdit()
        self.collect_count.setText("2025")

        self.links_text = QTextEdit()
        self.links_text.setPlaceholderText("請輸入地址，每行一個...\n例：https://www.facebook.com/steven.cheng.7792/posts/pfbid027XQvyQ4LS4FkA84nwYWt5snkMjcAGF7XN38u9c2iVFutWUwN4CWGuZdTygDpusEwl")
        self.links_text.setMinimumHeight(150)
        self.links_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.links_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.links_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        add_row("設備號 *", self.device_input)
        add_row("刷新數", self.refresh_input)
        add_row("採集帖子數量 *", self.post_count)
        add_row("採集數 *", self.collect_count)
        add_row("採集鏈接", self.links_text)

        form_container = QFrame()
        form_container.setLayout(form)
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root.addWidget(form_container)

        btns = QHBoxLayout()
        btns.setSpacing(16)
        btns.addStretch(1)

        self.reset_btn = QPushButton("重置设置")
        self.save_btn = QPushButton("保存设置")
        self.reset_btn.setObjectName("secondary")
        self.save_btn.setObjectName("primary")
        self.reset_btn.setFixedHeight(36)
        self.save_btn.setFixedHeight(36)
        self.reset_btn.setMinimumWidth(120)
        self.save_btn.setMinimumWidth(120)
        btns.addWidget(self.reset_btn)
        btns.addWidget(self.save_btn)
        btns.addStretch(1)

        root.addLayout(btns)

        self.setLayout(root)

        self.setStyleSheet(
            """
            QLabel { color: #333; }
            QLineEdit, QTextEdit, QAbstractSpinBox {
                padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px;
                background: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus, QAbstractSpinBox:focus {
                border: 1px solid #1890ff; outline: none;
            }
            QPushButton#primary {
                border-radius: 6px; background-color: #1677ff; color: #ffffff; font-weight: bold; border: 0px;
            }
            QPushButton#primary:hover { background-color: #4096ff; }
            QPushButton#primary:pressed { background-color: #0958d9; }
            QPushButton#secondary {
                border-radius: 6px; background-color: #f0f0f0; color: #333333; border: 1px solid #d9d9d9;
            }
            QPushButton#secondary:hover { background-color: #f5f5f5; }
            QPushButton#secondary:pressed { background-color: #d9d9d9; }
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




