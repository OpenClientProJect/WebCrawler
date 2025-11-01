import asyncio
import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, \
    QComboBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from qasync import QEventLoop

class MyApplog(QDialog):
    window_closed = pyqtSignal()
    
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
        self.setWindowTitle('Facebook 登錄')
        
        # 读取保存的登录信息
        login_name = ''
        login_pass = ''
        if os.path.exists('FBlogin.txt'):
            with open('FBlogin.txt', mode='r', newline='', encoding='utf-8') as file:
                login = file.read().split("|+|")
                login_name = login[0].strip('')
                login_pass = login[1].strip('')
        print(login_name, login_pass)

        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # 标题行（包含最小化、关闭按钮）
        title_row = QHBoxLayout()
        self.title_label = QLabel("Facebook登錄")
        self.title_label.setFont(QFont("微軟雅黑", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #333333;")
        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        
        # 最小化按钮
        min_button = QPushButton("-", self)
        min_button.setFixedSize(24, 24)
        min_button.setFont(QFont("微軟雅黑", 8))
        min_button.clicked.connect(self.showMinimized)
        min_button.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                border: 1px solid #ccc; 
                border-radius: 12px;
            }
            QPushButton:hover { 
                background-color: #f2b84b; 
            }
        """)
        title_row.addWidget(min_button)
        
        # 关闭按钮
        close_button = QPushButton("×", self)
        close_button.setFixedSize(24, 24)
        close_button.setFont(QFont("微軟雅黑", 8))
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                border: 1px solid #ccc; 
                border-radius: 12px;
            }
            QPushButton:hover { 
                background-color: #ff4d4f; 
                color: white; 
            }
        """)
        title_row.addWidget(close_button)
        
        main_layout.addLayout(title_row)

        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        main_layout.addSpacing(5)

        # 表单布局
        def add_row(label_text, widget):
            row = QVBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("微軟雅黑", 10))
            row.addWidget(lbl)
            row.addWidget(widget)
            main_layout.addLayout(row)

        # 创建输入框
        self.txt_username = QLineEdit(self)
        self.txt_username.setText(login_name)
        self.txt_username.setPlaceholderText("請輸入帳號...")
        add_row("Facebook帳號:", self.txt_username)

        self.txt_password = QLineEdit(self)
        self.txt_password.setText(login_pass)
        self.txt_password.setPlaceholderText("請輸入密碼...")
        self.txt_password.setEchoMode(QLineEdit.Password)
        add_row("Facebook密碼:", self.txt_password)

        main_layout.addSpacing(10)

        # 确定按钮
        self.button = QPushButton('確定', self)
        self.button.setFixedHeight(40)
        self.button.setObjectName("confirm")
        main_layout.addWidget(self.button)

        # 设置布局
        self.setLayout(main_layout)

        # 设置窗口大小
        self.setFixedSize(400, 320)

        # 应用全局样式
        self.setStyleSheet("""
            QWidget {
                background-color: #fefbf8;
            }
            QLabel { 
                color: #333333;
                background-color: transparent;
            }
            QLineEdit {
                padding: 8px; 
                border: 1px solid #e0e0e0; 
                border-radius: 6px; 
                font-size: 14px;
                background: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #1890ff; 
                outline: none;
            }
            QPushButton#confirm {
                border-radius: 6px; 
                background-color: #f2b84b; 
                color: #ffffff; 
                font-weight: bold; 
                border: 0px;
                font-size: 14px;
            }
            QPushButton#confirm:hover { 
                background-color: #ffc107; 
            }
            QPushButton#confirm:pressed { 
                background-color: #cc9900; 
            }
        """)

        # 连接按钮点击事件
        self.button.clicked.connect(self.on_click)

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

    # 设置应用程序的样式
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
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