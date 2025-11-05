import asyncio
import os.path
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, \
    QMessageBox, QDialog
from qasync import QEventLoop


class MyApplog(QDialog):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("Thcat.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 保持无边框
        self.credentials = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 设置窗口背景为白色
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
        """)
        
        # 设置窗口属性
        self.setWindowTitle('賬號登錄')
        self.setFixedSize(400, 300)  # 固定窗口大小
        
        # 创建主容器（浅灰色-白色面板，带圆角）
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
        """)
        
        # 创建整体布局
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)
        title_bar.setSpacing(8)  # 按钮之间的间距
        
        self.title_label = QLabel("Facebook 登錄")
        self.title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #82c3ed; background: transparent;")
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)

        # 添加最小化按钮（蓝色圆圈）
        min_button = QPushButton("")
        min_button.setFixedSize(12, 12)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #29b6f6;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        title_bar.addWidget(min_button)
        
        # 添加关闭按钮（绿色圆圈）
        close_button = QPushButton("")
        close_button.setFixedSize(12, 12)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4caf50;
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

        # Facebook賬號输入区域
        account_label = QLabel("Facebook賬號:")
        account_label.setStyleSheet("color: #64748b; font-size: 12px;")
        account_label.setFont(QFont("微軟雅黑", 11))
        main_layout.addWidget(account_label)
        
        self.txt_username = QLineEdit()
        self.txt_username.setText(login_name)
        self.txt_username.setPlaceholderText("請輸入賬號...")
        self.txt_username.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: #64748b;
            }
            QLineEdit:focus {
                border: 1px solid #82c3ed;
            }
        """)
        main_layout.addWidget(self.txt_username)
        
        # Facebook密碼输入区域
        password_label = QLabel("Facebook密碼:")
        password_label.setStyleSheet("color: #64748b; font-size: 12px;")
        password_label.setFont(QFont("微軟雅黑", 11))
        main_layout.addWidget(password_label)
        
        self.txt_password = QLineEdit()
        self.txt_password.setText(login_pass)
        self.txt_password.setPlaceholderText("請輸入密碼...")
        self.txt_password.setEchoMode(QLineEdit.Password)  # 密码模式
        self.txt_password.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: #64748b;
            }
            QLineEdit:focus {
                border: 1px solid #82c3ed;
            }
        """)
        main_layout.addWidget(self.txt_password)

        # 添加弹性空间
        main_layout.addStretch(1)
        
        # 创建确认按钮（全宽）
        self.button = QPushButton('確定')
        self.button.setFixedHeight(40)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                background-color: #72bade;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4fa3ff;
            }
            QPushButton:pressed {
                background-color: #3d8fff;
            }
        """)
        self.button.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        main_layout.addWidget(self.button)

        # 连接按钮点击事件到处理函数
        self.button.clicked.connect(self.on_click)

        # 设置主窗口布局
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(main_container)

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
            file.write(str(txt_username)+"|+|"+str(txt_password))
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

    # 设置应用程序的样式（浅色主题）
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, QColor(51, 51, 51))
    palette.setColor(QPalette.Button, QColor(99, 181, 255))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(130, 195, 237))
    palette.setColor(QPalette.Highlight, QColor(130, 195, 237))
    palette.setColor(QPalette.HighlightedText, Qt.white)
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