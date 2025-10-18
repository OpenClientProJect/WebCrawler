import asyncio
import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, \
    QComboBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from qasync import QEventLoop

class MyApplog(QDialog):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("Threadsicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 保持无边框
        self.credentials = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口属性
        self.setWindowTitle('Threads登錄')  # 这个标题现在只用于任务栏显示
        self.setFixedSize(400, 550)  # 增加窗口高度，确保图标完全可见

        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # 设置为0间距
        main_layout.setContentsMargins(0, 0, 0, 0)  # 设置边距为0

        # 创建标题容器，设置背景色和固定高度
        title_container = QWidget()
        title_container.setFixedHeight(60)  # 设置标题栏固定高度为60像素
        title_container.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8965, stop:1 #ffa07a);")
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setContentsMargins(20, 0, 20, 0)  # 保留左右内边距

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(25, 5, 0, 0)
        self.title_label = QLabel("Threads登錄", self)  # 自定义标题文本
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        self.title_label.setStyleSheet('background: transparent; border: none; color: white;')
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)

        # 添加最小化按钮到标题栏
        minimize_button = QPushButton("")  # 改变按钮文本为减号表示最小化
        minimize_button.setFont(QFont("微軟雅黑", 12))
        minimize_button.setFixedSize(24, 24)
        minimize_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #ddd;
                        border-radius: 12px;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #01bcae;
                    }
                """)
        minimize_button.clicked.connect(self.showMinimized)  # 连接到最小化方法
        title_bar.addWidget(minimize_button)

        # 添加关闭按钮到标题栏
        close_button = QPushButton("")
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.setFixedSize(24, 24)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #ddd;
                        border-radius: 12px;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #ff4d4f;
                    }
                """)
        title_bar.addWidget(close_button)

        # 将标题栏添加到标题容器
        title_container_layout.addLayout(title_bar)

        # 将标题容器添加到主布局
        main_layout.addWidget(title_container)

        # 创建内容容器，用于放置其他控件并保留边距
        content_container = QWidget()
        content_container.setStyleSheet("background-color: white;")
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(30, 30, 30, 30)  # 减少顶部边距，避免被标题栏遮挡
        content_container_layout.setSpacing(25)  # 增加间距

        # 添加Threads账号图标和应用名称
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setSpacing(10)  # 设置图标和文本之间的间距

        # 添加Threads账号图标
        threads_icon = QLabel()
        threads_icon.setPixmap(QIcon(resource_path("iamge/Threads账号.png")).pixmap(80, 80))  # 增大图标尺寸
        threads_icon.setAlignment(Qt.AlignCenter)
        threads_icon.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")

        # 添加应用名称
        app_name = QLabel("Threads", self)
        app_name.setFont(QFont("微軟雅黑", 20, QFont.Bold))  # 增大字体
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("color: #ff8965; background: transparent; border: none; margin: 0; padding: 0;")

        icon_layout.addWidget(threads_icon)
        icon_layout.addWidget(app_name)
        content_container_layout.addLayout(icon_layout)

        login_name = ''
        login_pass = ''
        if os.path.exists('Threadslogin.txt'):
            with open('Threadslogin.txt', mode='r', newline='', encoding='utf-8') as file:
                login = file.read().split("|+|")
                login_name = login[0].strip('')
                login_pass = login[1].strip('')
        print(login_name,login_pass)

        # 创建输入框
        self.txt_username = QLineEdit(self)
        self.txt_username.setText(login_name)
        self.txt_username.setPlaceholderText("請輸入您的賬號")
        self.txt_username.setStyleSheet("""
                    QLineEdit {
                        padding: 12px;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 14px;
                        background-color: white;
                        color: #333;
                    }
                    QLineEdit:focus {
                        border: 1px solid #01bdae;
                        box-shadow: 0 0 8px rgba(1, 189, 174, 0.3);
                    }
                """)

        self.txt_password = QLineEdit(self)
        self.txt_password.setText(login_pass)
        self.txt_password.setPlaceholderText("請輸入您的密碼")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet("""
                    QLineEdit {
                        padding: 12px;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 14px;
                        background-color: white;
                        color: #333;
                    }
                    QLineEdit:focus {
                        border: 1px solid #01bdae;
                        box-shadow: 0 0 8px rgba(1, 189, 174, 0.3);
                    }
                """)

        # 账号输入框和图标
        account_layout = QHBoxLayout()
        account_icon = QLabel()
        account_icon.setPixmap(QIcon(resource_path("iamge/jurassic_user.png")).pixmap(20, 20))
        account_label = QLabel("Threads賬號:")
        account_label.setStyleSheet("color: #666; font-weight: bold; font-size: 14px;")
        account_layout.addWidget(account_icon)
        account_layout.addWidget(account_label)
        account_layout.addStretch()
        content_container_layout.addLayout(account_layout)
        content_container_layout.addWidget(self.txt_username)

        # 密码输入框和图标
        password_layout = QHBoxLayout()
        password_icon = QLabel()
        password_icon.setPixmap(QIcon(resource_path("iamge/tianchongxing-.png")).pixmap(20, 20))
        password_icon.setStyleSheet("margin-right: 8px;")
        password_label = QLabel("Threads密碼:")
        password_label.setStyleSheet("color: #666; font-weight: bold; font-size: 14px;")
        password_layout.addWidget(password_icon)
        password_layout.addWidget(password_label)
        password_layout.addStretch()
        content_container_layout.addLayout(password_layout)
        content_container_layout.addWidget(self.txt_password)

        # 创建登录按钮
        self.button = QPushButton('確定登錄', self)
        self.button.setFixedSize(350, 45)  # 设置按钮大小

        # 创建按钮图标
        login_icon = QIcon(resource_path("iamge/login-full.png"))
        self.button.setIcon(login_icon)
        self.button.setIconSize(login_icon.actualSize(login_icon.availableSizes()[0]))
        self.button.setIconSize(QSize(20,20))

        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #01bdae, stop:1 #7FFFD4);
                font-size: 16px;
                font-weight: bold;
                color: white;
                border: none;
                padding: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00a896, stop:1 #6bddd4);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(1, 189, 174, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #008b7a, stop:1 #5bc4b8);
            }
        """)

        # 创建按钮布局并居中
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # 添加伸缩量使得按钮居中
        button_layout.addWidget(self.button)
        button_layout.addStretch(1)  # 添加伸缩量使得按钮居中

        content_container_layout.addLayout(button_layout)

        # 将内容容器添加到主布局
        main_layout.addWidget(content_container)

        # 连接按钮点击事件到处理函数
        self.button.clicked.connect(self.on_click)

        # 设置布局
        self.setLayout(main_layout)

        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
        """)

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
        with open('Threadslogin.txt', mode='w', newline='', encoding='utf-8') as file:
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

    # 设置应用程序的样式
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(247, 248, 249))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(1, 189, 174))
    palette.setColor(QPalette.Highlight, QColor(1, 189, 174))
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
