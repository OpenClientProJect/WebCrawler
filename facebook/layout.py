import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from qasync import QEventLoop

from FB_win import MyApp as FBWidget
from like import likePage


class MainLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('主界面')
        self.setFixedSize(900, 560)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 自定义标题栏
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(10, 5, 5, 5)
        title_bar_layout.setSpacing(0)

        self.title_label = QLabel("Facebook")
        self.title_label.setFont(QFont("微軟雅黑", 10, QFont.Bold))
        self.title_label.setStyleSheet("color: #333;")
        title_bar_layout.addWidget(self.title_label)
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

        title_container = QFrame()
        title_container.setLayout(title_bar_layout)
        title_container.setStyleSheet(
            """
            QFrame { background-color: #f5f5f5; border-bottom: 1px solid #e0e0e0; }
            """
        )
        title_container.setFixedHeight(40)
        root.addWidget(title_container)

        # 主体区域：左侧导航 + 右侧内容
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav = QFrame()
        nav.setFixedWidth(140)
        nav.setStyleSheet("QFrame { background-color: #fafafa; border-right: 1px solid #e0e0e0; }")
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(10)

        btn_home = QPushButton("like")
        btn_fb = QPushButton("Facebook")
        for b in (btn_home, btn_fb):
            b.setFixedHeight(36)
            b.setFont(QFont("微軟雅黑", 10))
            b.setStyleSheet(
                """
                QPushButton { border-radius: 6px; background-color: #ffffff; border: 1px solid #e0e0e0; }
                QPushButton:hover { background-color: #f5f5f5; }
                QPushButton:checked { background-color: #e6f4ff; border-color: #91caff; }
                """
            )
            b.setCheckable(True)
        btn_home.setChecked(True)

        nav_layout.addWidget(btn_home)
        nav_layout.addWidget(btn_fb)
        nav_layout.addStretch(1)

        # 版本信息标签放置于导航底部
        self.version = "1.0.0.0"
        self.day = 100
        version_label = QLabel(f"{self.version} 剩余天数：{self.day}")
        version_label.setFont(QFont("微軟雅黑", 8))
        version_label.setStyleSheet("color: #999;")
        version_label.setAlignment(Qt.AlignHCenter)
        nav_layout.addWidget(version_label)
        nav.setLayout(nav_layout)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background-color: #ffffff; }")

        # 页面：首頁
        self.home_page = likePage()
        self.home_page.hideMainRequested.connect(self.hide)

        # 页面：Facebook（嵌入式，不使用其窗口框架）
        self.fb_page = FBWidget(embedded=True, version=self.version, day=self.day)
        # 连接子页面发出的隐藏主窗口请求
        self.fb_page.hideMainRequested.connect(self.hide)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.fb_page)

        main_layout.addWidget(nav)
        main_layout.addWidget(self.stack, 1)

        container = QFrame()
        container.setLayout(main_layout)
        container.setStyleSheet("QFrame { }")
        root.addWidget(container)

        self.setLayout(root)

        # 事件绑定
        btn_home.clicked.connect(lambda: self._switch_page(0, btn_home, btn_fb))
        btn_fb.clicked.connect(lambda: self._switch_page(1, btn_home, btn_fb))

    def _switch_page(self, index, btn_home, btn_fb):
        self.stack.setCurrentIndex(index)
        if index == 0:
            btn_home.setChecked(True)
            btn_fb.setChecked(False)
            self.title_label.setText("Facebook · like")
        else:
            btn_home.setChecked(False)
            btn_fb.setChecked(True)
            self.title_label.setText("Facebook · reptile")

    # 拖动无边框窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()


def main():
    app = QApplication(sys.argv)

    # 使用 qasync 事件循环以兼容內部異步槽
    loop = QEventLoop(app)
    import asyncio as _asyncio
    _asyncio.set_event_loop(loop)

    # 应用样式
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(24, 144, 255))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    app.setFont(QFont("微軟雅黑", 10))

    win = MainLayout()
    win.show()

    try:
        with loop:
            sys.exit(loop.run_forever())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

