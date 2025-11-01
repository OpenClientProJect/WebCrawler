import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget
)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from qasync import QEventLoop
from PyQt5.QtSvg import QSvgWidget

from FB_win import MyApp as FBWidget
from like import likePage


class MainLayout(QWidget):
    close_app_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        icon_path = resource_path("image/FBre.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('Facebookreptile')
        self.setFixedSize(850, 620)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 主体区域：左侧导航 + 右侧内容
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav = QFrame()
        nav.setFixedWidth(140)
        nav.setStyleSheet("QFrame { background-color: #f0f5f0; border-right: 1px solid #e0e0e0; }")
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 15, 10, 15)
        nav_layout.setSpacing(10)

        # Add Facebook logo
        logo_path = resource_path("image/facebookLogo.svg")
        logo_widget = QSvgWidget(logo_path)
        logo_widget.setFixedSize(40, 40)
        nav_layout.addWidget(logo_widget, alignment=Qt.AlignHCenter)
        nav_layout.addSpacing(15)

        btn_home = QPushButton("採集點讚用戶")
        btn_fb = QPushButton("採集社群成員")
        for b in (btn_home, btn_fb):
            b.setFixedHeight(36)
            b.setFont(QFont("微軟雅黑", 10))
            b.setStyleSheet(
                """
                QPushButton { 
                    border-radius: 6px; 
                    background-color: transparent; 
                    border: none;
                    color: #3d9e87;
                    text-align: left;
                    padding-left: 12px;
                }
                QPushButton:hover { background-color: #e0f0e0; }
                QPushButton:checked { 
                    background-color: #3d9e87; 
                    color: white;
                }
                """
            )
            b.setCheckable(True)
        btn_home.setChecked(True)

        nav_layout.addWidget(btn_home)
        nav_layout.addWidget(btn_fb)
        nav_layout.addStretch(1)

        # 版本信息标签放置于导航底部
        self.version = versions
        self.day = days
        version_label = QLabel(f"版本: {self.version}")
        version_label.setFont(QFont("微軟雅黑", 8))
        version_label.setStyleSheet("color: #999;")
        version_label.setAlignment(Qt.AlignHCenter)
        nav_layout.addWidget(version_label)
        
        day_label = QLabel(f"剩余天數: {self.day}")
        day_label.setFont(QFont("微軟雅黑", 8))
        day_label.setStyleSheet("color: #999;")
        day_label.setAlignment(Qt.AlignHCenter)
        nav_layout.addWidget(day_label)
        nav.setLayout(nav_layout)

        # 右侧内容区域容器
        right_content_container = QWidget()
        right_content_container.setStyleSheet("QWidget { background-color: #fefbf8; }")
        right_content_layout = QVBoxLayout()
        right_content_layout.setContentsMargins(0, 0, 0, 0)
        right_content_layout.setSpacing(0)

        # 顶部标题栏 - 透明背景覆盖在内容顶层
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("QFrame { background-color: transparent; }")
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

        title_bar.setLayout(title_bar_layout)
        right_content_layout.addWidget(title_bar)

        # 页面内容
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background-color: transparent; }")

        # 页面：首頁
        self.home_page = likePage()
        self.home_page.hideMainRequested.connect(self.hide)

        # 页面：Facebook（嵌入式，不使用其窗口框架）
        self.fb_page = FBWidget(embedded=True, version=self.version, day=self.day)
        # 连接子页面发出的隐藏主窗口请求
        self.fb_page.hideMainRequested.connect(self.hide)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.fb_page)

        right_content_layout.addWidget(self.stack)
        right_content_container.setLayout(right_content_layout)

        main_layout.addWidget(nav)
        main_layout.addWidget(right_content_container, 1)

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
        else:
            btn_home.setChecked(False)
            btn_fb.setChecked(True)

    # 拖动无边框窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def closeEvent(self, event):
        """发出关闭信号"""
        self.close_app_signal.emit()  # 发出关闭应用程序信号
        super().closeEvent(event)


def main(version, day):
    global versions, days
    versions = version
    days = day
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
    except RuntimeError:
        pass

def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
if __name__ == '__main__':
    main("1.0.0.0", 1)

