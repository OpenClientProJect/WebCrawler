from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QFrame, QSizePolicy, QAbstractSpinBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class likePage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel("系统设置")
        title.setAlignment(Qt.AlignHCenter)
        title.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        root.addWidget(title)

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
        self.device_input.setPlaceholderText("请输入设备唯一标识")

        self.refresh_input = QLineEdit()
        self.refresh_input.setText("10")
        self.refresh_input.setPlaceholderText("10")
        self.refresh_input.setValidator(None)

        self.post_count = QSpinBox()
        self.post_count.setRange(1, 1000000)
        self.post_count.setValue(50)
        self.post_count.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.collect_count = QLineEdit()
        self.collect_count.setText("50")

        self.links_text = QTextEdit()
        self.links_text.setPlaceholderText("请输入链接 1")
        self.links_text.setMinimumHeight(220)

        add_row("设备号 *", self.device_input)
        add_row("刷新数", self.refresh_input)
        add_row("采集帖子数量 *", self.post_count)
        add_row("采集数 *", self.collect_count)
        add_row("采集链接 (回车确认)", self.links_text)

        form_container = QFrame()
        form_container.setLayout(form)

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

