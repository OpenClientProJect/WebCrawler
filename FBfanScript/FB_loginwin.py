import asyncio
import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, \
    QComboBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
from qasync import QEventLoop


class MyApplog(QDialog):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("FBmie.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 保持无边框
        self.credentials = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口属性
        self.setWindowTitle('賬號登錄')  # 这个标题现在只用于任务栏显示
        # 设置窗口背景颜色
        self.setStyleSheet("background-color: #f8f4ff;")

        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # 设置外边距
        main_layout.setSpacing(15)  # 设置控件间距

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 10)  # 设置标题栏底部间距

        self.title_label = QLabel("Facebook登錄", self)  # 自定义标题文本
        self.title_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.title_label.setStyleSheet("color: #6a5acd;font-weight: bold;")  # 设置标题颜色
        self.setFixedSize(350, 0)  # 设置窗口的固定大小
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)

        # 添加最小化按钮 - 缩小尺寸
        minimize_button = QPushButton("", self)  # 使用减号作为最小化图标
        minimize_button.setFont(QFont("Arial", 10, QFont.Bold))
        minimize_button.setFixedSize(20, 20)  # 缩小按钮尺寸
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #6a5acd;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5a4abc;
            }
            QPushButton:pressed {
                background-color: #4a3aac;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        title_bar.addWidget(minimize_button)

        # 添加关闭按钮 - 缩小尺寸
        close_button = QPushButton("", self)  # 使用乘号作为关闭图标
        close_button.setFont(QFont("Arial", 10, QFont.Bold))
        close_button.setFixedSize(20, 20)  # 缩小按钮尺寸
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #ff3838;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)

        # 将标题栏添加到主布局
        main_layout.addLayout(title_bar)

        login_name = ''
        login_pass = ''
        if os.path.exists('FBlogin.txt'):
            with open('FBlogin.txt', mode='r', newline='', encoding='utf-8') as file:
                login = file.read().split("|+|")
                login_name = login[0].strip('')
                login_pass = login[1].strip('')
        print(login_name, login_pass)

        # 创建账号输入区域
        username_layout = QVBoxLayout()
        username_layout.setSpacing(5)
        username_label = QLabel("Facebook賬號:")
        username_label.setStyleSheet("color: #333333; font-weight: bold;")
        username_layout.addWidget(username_label)

        self.txt_username = QLineEdit(self)
        self.txt_username.setText(login_name)
        self.txt_username.setPlaceholderText("請輸入賬號...")
        self.txt_username.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #d8d0e3;
                border-radius: 8px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #6a5acd;
            }
        """)
        username_layout.addWidget(self.txt_username)
        main_layout.addLayout(username_layout)

        # 添加间距
        main_layout.addSpacing(10)

        # 创建密码输入区域
        password_layout = QVBoxLayout()
        password_layout.setSpacing(5)
        password_label = QLabel("Facebook密碼:")
        password_label.setStyleSheet("color: #333333; font-weight: bold;")
        password_layout.addWidget(password_label)

        self.txt_password = QLineEdit(self)
        self.txt_password.setText(login_pass)
        self.txt_password.setPlaceholderText("請輸入密碼...")
        # self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #d8d0e3;
                border-radius: 8px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #6a5acd;
            }
        """)
        password_layout.addWidget(self.txt_password)
        main_layout.addLayout(password_layout)

        # 添加间距
        main_layout.addSpacing(15)

        # 创建水平布局用于放置按钮并居中
        button_layout = QHBoxLayout()
        # button_layout.addStretch(1)

        self.button = QPushButton('確定', self)
        # 设置按钮的最小宽度以确保圆角效果
        self.button.setMinimumWidth(120)
        self.button.setMinimumHeight(40)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                background-color: #6495ed;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5a7fdb;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a6bc9;
            }
        """)
        button_layout.addWidget(self.button)
        # button_layout.addStretch(1)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 连接按钮点击事件到处理函数
        self.button.clicked.connect(self.on_click)

        # 设置布局
        self.setLayout(main_layout)

        # 显示窗口
        self.show()

    # 必须实现的拖动窗口的方法
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

    def on_click(self):
        # 获取输入框内容并去除首尾空格
        txt_username = self.txt_username.text().strip()
        txt_password = self.txt_password.text().strip()

        # 验证设备号
        if not txt_username:
            print("错误：账号不能为空")
            QMessageBox.warning(self, "输入错误", "错误：账号不能为空", QMessageBox.Ok)
            return  # 终止函数执行
        if not txt_password:
            print("错误：密码不能为空")
            QMessageBox.warning(self, "输入错误", "错误：密码不能为空", QMessageBox.Ok)
            return  # 终止函数执行
        # 所有验证通过后的处理
        print(f"账号: {txt_username}")
        print(f"密码: {txt_password}")
        self.credentials = {  # 将结果保存到实例变量
            "username": txt_username,
            "password": txt_password
        }
        with open('FBlogin.txt', mode='w', newline='', encoding='utf-8') as file:
            file.write(str(txt_username) + "|+|" + str(txt_password))
        self.hide()


def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def win_main():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # 设置应用程序的样式
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 244, 255))  # #f8f4ff
    palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 244, 255))
    palette.setColor(QPalette.ToolTipBase, QColor(248, 244, 255))
    palette.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
    palette.setColor(QPalette.Text, QColor(51, 51, 51))
    palette.setColor(QPalette.Button, QColor(248, 244, 255))
    palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
    palette.setColor(QPalette.BrightText, QColor(255, 107, 107))
    palette.setColor(QPalette.Link, QColor(106, 90, 205))
    palette.setColor(QPalette.Highlight, QColor(106, 90, 205))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    app.setFont(QFont("微軟雅黑", 10))
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    dialog = MyApplog()
    dialog.exec_()  # 模态显示

    # if result == QDialog.Accepted:
    #     return dialog.credentials
    # return None
    return dialog.credentials