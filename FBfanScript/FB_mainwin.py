import os
import sys
import asyncio
import aiohttp
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox,
                             QMessageBox, QCheckBox, QStackedWidget, QFrame, QSizePolicy)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from qasync import QEventLoop, asyncClose, asyncSlot
from FB_middle import main


class ImageSlider(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(3000)  # 3秒切换一次图片
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_image(self, image_path):
        label = QLabel()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border-radius: 10px;")
        self.addWidget(label)

    def resizeEvent(self, event):
        # 当尺寸改变时，更新所有图片的大小
        for i in range(self.count()):
            label = self.widget(i)
            if label and isinstance(label, QLabel):
                pixmap = QPixmap(label.pixmap())
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
        super().resizeEvent(event)

    def next_image(self):
        if self.count() > 0:
            self.current_index = (self.current_index + 1) % self.count()
            self.setCurrentIndex(self.current_index)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("FBmie.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.monitor_window = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('Facebook自動化脚本')
        self.setFixedSize(900, 485)  # 增加窗口宽度，右侧会更长

        # 创建主水平布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧轮播图区域 - 占比35%
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距让轮播图填满

        # 创建轮播图
        self.slider = ImageSlider()
        self.slider.add_image(resource_path("slide4.png"))
        left_layout.addWidget(self.slider)

        # 左侧底部文本
        left_text = QLabel("Facebook自動化管理平台\n高效安全的社交媒體管理解決方案")
        left_text.setAlignment(Qt.AlignCenter)
        left_text.setFont(QFont("微軟雅黑", 10))
        left_text.setStyleSheet("color: #666; padding: 10px;")
        left_layout.addWidget(left_text)

        # 右侧登录区域 - 占比65%（加长右侧）
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #f7f6ff;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(35, 25, 35, 20)  # 增加左右边距

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        self.title_label = QLabel("                         ", self)
        self.title_label.setFont(QFont("微軟雅黑", 10))
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)

        # 添加最小化和关闭按钮
        min_button = QPushButton("-")
        min_button.setFont(QFont("微軟雅黑", 10))
        min_button.setFixedSize(24, 24)
        min_button.clicked.connect(self.showMinimized)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        close_button = QPushButton("×")
        close_button.setFont(QFont("微軟雅黑", 10))
        close_button.setFixedSize(24, 24)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #ff4d4f;
                color: white;
            }
        """)

        title_bar.addWidget(min_button)
        title_bar.addWidget(close_button)
        right_layout.addLayout(title_bar)
        login_title0 = QLabel("Facebook自動化腳本")
        login_title0.setFont(QFont("微軟雅黑", 10, QFont.Bold))
        login_title0.setStyleSheet("margin-top: 3px; margin-bottom: 2px;color: #6e6e70;font-weight: bold;")
        login_title0.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(login_title0)
        # 添加登录表单标题
        login_title = QLabel("用戶登錄")
        login_title.setFont(QFont("微軟雅黑", 16, QFont.Bold))
        login_title.setStyleSheet("margin-top: 10px; margin-bottom: 20px;color: #1e5eff;font-weight: bold;")
        login_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(login_title)

        # 读取保存的登录信息
        login_name = ''
        login_pass = ''
        if os.path.exists('Facebookuser.txt'):
            with open('Facebookuser.txt', mode='r', newline='', encoding='utf-8') as file:
                login = file.read().split("|+|")
                login_name = login[0].strip('')
                login_pass = login[1].strip('')

        # 创建表单
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # 设备号输入
        self.input0 = QLineEdit(self)
        self.input0.setText("000")
        self.input0.setPlaceholderText("請輸入設備號...")
        self.input0.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #1890ff;
                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
            }
        """)
        device_label = QLabel("設備號:")
        device_label.setFont(QFont("微軟雅黑", 10))  # 微软雅黑，稍小字号
        form_layout.addWidget(device_label)
        form_layout.addWidget(self.input0)

        # 账号输入
        self.input1 = QLineEdit(self)
        self.input1.setText(login_name)
        self.input1.setPlaceholderText("請輸入Ai後臺賬號...")
        self.input1.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #1890ff;
                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
            }
        """)
        account_label = QLabel("Ai賬號:")
        account_label.setFont(QFont("微軟雅黑", 10))  # 微软雅黑，稍小字号
        form_layout.addWidget(account_label)
        form_layout.addWidget(self.input1)

        # 密码输入
        self.input2 = QLineEdit(self)
        self.input2.setText(login_pass)
        self.input2.setPlaceholderText("請輸入Ai後臺密碼...")
        self.input2.setEchoMode(QLineEdit.Password)
        self.input2.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #1890ff;
                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
            }
        """)
        password_label = QLabel("Ai密碼:")
        password_label.setFont(QFont("微軟雅黑", 10))  # 微软雅黑，稍小字号
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.input2)

        right_layout.addLayout(form_layout)

        # 记住密码复选框
        self.remember_check = QCheckBox("記住密碼")
        self.remember_check.setChecked(True)
        self.remember_check.setStyleSheet("""
                    QCheckBox {
                        background-color: #f7f6ff;
                    }

                """)
        self.remember_check.setFont(QFont("微軟雅黑", 9))  # 微软雅黑，更小字号
        right_layout.addWidget(self.remember_check)

        # 登录按钮 - 独占一行
        self.button = QPushButton('登錄', self)
        self.button.setFixedHeight(45)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background-color: #1e5eff;
                color: white;
                font-size: 12px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        right_layout.addWidget(self.button)

        # 忘记密码链接 - 单独一行，靠右对齐
        forget_layout = QHBoxLayout()
        forget_layout.addStretch(1)  # 添加弹性空间使按钮靠右
        forget_link = QPushButton("忘記密碼?")
        forget_link.setFlat(True)
        forget_link.setStyleSheet("""
            QPushButton {
                color: #1890ff;
                text-decoration: none;
                border: none;
                padding: 5px;
                font-size: 11px;
                background-color: #f7f6ff;
            }
            QPushButton:hover {
                color: #40a9ff;
                text-decoration: underline;
            }
        """)
        forget_link.setFont(QFont("微軟雅黑", 9))  # 微软雅黑，更小字号
        forget_link.clicked.connect(self.on_forget_password)
        forget_layout.addWidget(forget_link)
        right_layout.addLayout(forget_layout)

        # 版本信息
        self.days_label = QLabel(f"時間：{days}天 版本：{versions}", self)
        self.days_label.setFont(QFont("微軟雅黑", 8))
        self.days_label.setStyleSheet("color: #999; margin-top: 10px;")
        self.days_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.days_label)

        # 连接按钮点击事件
        self.button.clicked.connect(self.on_click)

        # 将左右两部分添加到主布局
        main_layout.addWidget(left_frame, 35)  # 左侧占比35%
        main_layout.addWidget(right_frame, 65)  # 右侧占比65%（加长）

        # 设置布局
        self.setLayout(main_layout)

        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #e6f0ff;
            }
        """)

    def on_forget_password(self):
        QMessageBox.information(self, "忘記密碼", "請聯繫系統管理員重置密碼")

    # 必须实现的拖动窗口的方法
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def center(self):
        # 获取窗口框架几何信息
        frame_gm = self.frameGeometry()
        # 获取屏幕中心点
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        # 设置框架几何信息的中心点为屏幕中心点
        frame_gm.moveCenter(center_point)
        # 根据新的框架几何信息调整窗口位置
        self.move(frame_gm.topLeft())

    @asyncSlot()
    async def on_click(self):
        # 获取输入框内容并去除首尾空格
        content0 = self.input0.text().strip()
        content1 = self.input1.text().strip()
        content2 = self.input2.text().strip()

        # 验证设备号
        if not content0:
            QMessageBox.warning(self, "输入错误", "错误：设备号不能为空", QMessageBox.Ok)
            return
        if not content1:
            QMessageBox.warning(self, "输入错误", "错误：賬號不能为空", QMessageBox.Ok)
            return
        if not content2:
            QMessageBox.warning(self, "输入错误", "错误：密碼不能为空", QMessageBox.Ok)
            return

        # 如果勾选了记住密码，保存登录信息
        if self.remember_check.isChecked():
            with open('Facebookuser.txt', mode='w', newline='', encoding='utf-8') as file:
                file.write(str(content1) + "|+|" + str(content2))

        # 检查登录
        login = await check_login(content1, content2)
        if "no" in login or "ok" in login:
            QMessageBox.warning(self, "登錄错误", "错误：賬號或密碼錯誤！", QMessageBox.Ok)
            return
        # 所有验证通过后的处理
        print(f"设备号: {content0}")
        print(f"账号: {content1}")
        print(f"密码: {content2}")
        # 所有验证通过后的处理
        self.hide()
        try:
            await main(content0, content1)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"任务执行失败: {str(e)}", QMessageBox.Ok)
            self.close()


async def check_login(account, password):
    url = f"http://aj.ry188.vip/api/Login.aspx?Account={account}&PassWord={password}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=15) as response:
            return await response.text()


def win_main(version, day):
    global versions, days
    versions = version
    days = day
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 设置应用程序的样式为亮色
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

    app.setFont(QFont("Arial", 10))
    ex = MyApp()
    ex.show()

    with loop:
        loop.run_forever()


def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    win_main("1.1.1.1", 1)
