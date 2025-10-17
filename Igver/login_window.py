import asyncio
import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, \
    QComboBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt
from qasync import QEventLoop

class MyApplog(QDialog):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("IGicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 保持无边框
        self.credentials = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口属性
        self.setWindowTitle('Instagram 登錄')
        self.setFixedSize(400, 500)  # 设置窗口固定大小

        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部渐变标题区域
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # 标题栏水平布局
        title_bar_layout = QHBoxLayout()
        
        # 左侧标题
        title_label = QLabel("Instagram 登錄", self)
        title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent; border: none;")
        title_bar_layout.addWidget(title_label)
        
        # 中间伸缩空间
        title_bar_layout.addStretch(1)
        
        # 右侧窗口控制按钮
        minimize_button = QPushButton("-", self)
        minimize_button.setFont(QFont("微軟雅黑", 12))
        minimize_button.setFixedSize(24, 24)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_button)

        close_button = QPushButton("×", self)
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)

        header_layout.addLayout(title_bar_layout)

        main_layout.addWidget(header_widget)

        # 创建主内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 0px 0px 15px 15px;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Instagram图标
        icon_label = QLabel(self)
        icon_path = resource_path("./image/Instagram.png")
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(100, 100)
        content_layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # 读取保存的登录信息
        login_name = ''
        login_pass = ''
        if os.path.exists('IGlogin.txt'):
            with open('IGlogin.txt', mode='r', newline='', encoding='utf-8') as file:
                login = file.read().split("|+|")
                login_name = login[0].strip('')
                login_pass = login[1].strip('')
        print(login_name, login_pass)

        # 输入框样式
        input_style = """
            QLineEdit {
                padding: 15px 20px;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
                background-color: white;
                font-size: 12px;
                color: #495057;
                font-family: "微軟雅黑";
            }
            QLineEdit:focus {
                border-color: #667eea;
                outline: none;
            }
        """

        label_style = """
            QLabel {
                color: #495057;
                font-weight: 600;
                font-size: 15px;
                margin-bottom: 8px;
                font-family: "微軟雅黑";
            }
        """

        # 账号输入区域
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)

        username_label = QLabel("Instagram 賬號:", self)
        username_label.setStyleSheet(label_style)
        username_layout.addWidget(username_label)

        self.txt_username = QLineEdit(self)
        self.txt_username.setText(login_name)
        self.txt_username.setPlaceholderText("請輸入賬號...")
        self.txt_username.setStyleSheet(input_style)
        username_layout.addWidget(self.txt_username)

        content_layout.addLayout(username_layout)

        # 密码输入区域
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)

        password_label = QLabel("Instagram 密碼:", self)
        password_label.setStyleSheet(label_style)
        password_layout.addWidget(password_label)

        self.txt_password = QLineEdit(self)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setText(login_pass)
        self.txt_password.setPlaceholderText("請輸入密碼...")
        self.txt_password.setStyleSheet(input_style)
        password_layout.addWidget(self.txt_password)

        content_layout.addLayout(password_layout)

        # 登录按钮
        self.button = QPushButton(self)
        self.button.setFixedHeight(50)
        self.button.setFont(QFont("微軟雅黑", 13, QFont.Bold))

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(15, 0, 15, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignCenter)

        # 添加go图标
        go_path = resource_path("./image/go.png")
        go_icon = QLabel(self)
        go_pixmap = QPixmap(go_path)
        go_icon.setPixmap(go_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        go_icon.setStyleSheet("background: transparent; border: none;")
        button_layout.addWidget(go_icon)

        # 添加文本
        button_text = QLabel("確定登錄", self)
        button_text.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        button_layout.addWidget(button_text)

        self.button.setLayout(button_layout)

        self.button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 25px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                font-family: "微軟雅黑";
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4e5bc6, stop:1 #5e377e);
            }
        """)
        content_layout.addWidget(self.button)

        main_layout.addWidget(content_widget)

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
        with open('IGlogin.txt', mode='w', newline='', encoding='utf-8') as file:
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

    # 设置程序样式
    app.setStyle('Fusion')
    palette = QPalette()
    # 主题
    palette.setColor(QPalette.Window, QColor(248, 249, 250))  # 浅灰背景
    palette.setColor(QPalette.WindowText, QColor(73, 80, 87))  # 深色文字
    palette.setColor(QPalette.Base, QColor(255, 255, 255))  # 白色输入框背景
    palette.setColor(QPalette.AlternateBase, QColor(233, 236, 239))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(73, 80, 87))
    palette.setColor(QPalette.Text, QColor(73, 80, 87))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(73, 80, 87))
    palette.setColor(QPalette.BrightText, QColor(220, 53, 69))
    palette.setColor(QPalette.Link, QColor(102, 126, 234))  # 主题蓝色
    palette.setColor(QPalette.Highlight, QColor(118, 75, 162))  # 主题紫色
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    app.setFont(QFont("微軟雅黑", 10))
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    dialog = MyApplog()
    dialog.exec_()  # 模态显示

    return dialog.credentials
