# authorization.py
import datetime
import os
import re

import pyodbc
import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox)
import clr

# 添加dll引用路径
try:
    dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AuthorizeManage.dll")
    if os.path.exists(dll_path):
        clr.AddReference(dll_path)
    clr.AddReference("mscorlib")
    clr.AddReference("AuthorizeManage")
    from AuthorizeManage import AuthorizeX
except Exception as e:
    print(f"加载授权DLL失败: {e}")
    AuthorizeX = None


class AuthorizationDialog(QDialog):
    def __init__(self, machine_code, parent=None):
        super().__init__(parent)
        self.machine_code = machine_code
        self.setWindowTitle("授權驗證")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.initUI()
        self.center()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("授權驗證")
        title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(title_label)

        # 提示信息
        info_label = QLabel("當前軟件未授權或授權已經過期")
        info_label.setFont(QFont("微軟雅黑", 10))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 机器码显示
        machine_label = QLabel("請複製以下機器碼聯繫管理員授權：")
        machine_label.setFont(QFont("微軟雅黑", 9))
        layout.addWidget(machine_label)

        self.code_text = QTextEdit()
        self.code_text.setText(self.machine_code)
        self.code_text.setReadOnly(True)
        self.code_text.setFixedHeight(80)
        self.code_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, monospace;
            }
        """)
        layout.addWidget(self.code_text)

        # 复制按钮
        copy_btn = QPushButton("複製機器碼")
        copy_btn.setFixedHeight(35)
        copy_btn.clicked.connect(self.copy_code)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        layout.addWidget(copy_btn)

        # 退出按钮
        exit_btn = QPushButton("退出程序")
        exit_btn.setFixedHeight(35)
        exit_btn.clicked.connect(self.close_application)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
        """)
        layout.addWidget(exit_btn)

        self.setLayout(layout)

    def center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def copy_code(self):
        # clipboard = QApplication.clipboard()
        # clipboard.setText(self.machine_code)
        pyperclip.copy(self.machine_code)
        QMessageBox.information(self, "提示", "機器碼已複製到剪切板")

    def close_application(self):
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()


def check_authorization():
    """检查授权状态"""
    if AuthorizeX is None:
        return False, "授权模块加载失败", "未知"

    try:
        # 获取机器码
        machine_code = AuthorizeX.GetAuthorize("FBCJ")
        print(f"机器码: {machine_code}")

        # 数据库连接字符串
        connection_string = (
            r"Driver={SQL Server};"
            r"Server=dbs.kydb.vip;"
            r"Database=DeviceAuthData;"
            r"UID=sa;"
            r"PWD=Yunsin@#861123823_shp4;"
            r"timeout=35;"
        )

        # 连接数据库验证授权
        conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
        cursor = conn.cursor()

        query = """
                SELECT PCCoded, installDate, ExpiryDate
                FROM UserData
                WHERE PCCoded = ? \
                """
        cursor.execute(query, (machine_code,))
        results = cursor.fetchall()

        if results:
            for row in results:
                PCCoded = row[0]
                installDate = row[1]
                ExpiryDate = row[2]

                current_date = datetime.datetime.now().date()
                installDate = installDate.date()
                ExpiryDate = ExpiryDate.date()

                if installDate <= current_date <= ExpiryDate:
                    days_remaining = (ExpiryDate - current_date).days
                    print(f"当前日期在有效期内。剩余天数: {days_remaining}")
                    return True, f"授權有效，剩餘{days_remaining}天", machine_code
                else:
                    print("当前日期不在有效期内。")
                    return False, "授權已經過期", machine_code
        else:
            print("没有找到授权信息！")
            return False, "未找到授權信息", machine_code

    except Exception as e:
        print(f"授权检查失败: {e}")
        return False, f"授權檢測失敗: {str(e)}", "獲取失敗"


def show_authorization_dialog(machine_code):
    """显示授权对话框"""
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    dialog = AuthorizationDialog(machine_code)
    dialog.exec_()


def verify_and_run(version, day):
    """验证授权并运行主程序"""
    is_authorized, message, machine_code = check_authorization()

    if is_authorized:
        print("当前日期在有效期内。")
        # 导入并运行主程序
        from FB_win import win_main
        day_match = re.search(r'\d+', message)
        if day_match:
            win_main(version, day_match.group())
        else:
            win_main(version, day)
    else:
        print(f"授权失败: {message}")
        # 直接显示授权对话框，阻塞直到关闭
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        dialog = AuthorizationDialog(machine_code)
        dialog.exec_()  # 使用 exec_() 阻塞直到对话框关闭

        # 对话框关闭后退出程序
        QApplication.quit()