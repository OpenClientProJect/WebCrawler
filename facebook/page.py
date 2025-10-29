from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("首頁")
        title.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        subtitle = QLabel("這裡是示例頁面，可根據需要擴展功能。")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        self.setLayout(layout)

