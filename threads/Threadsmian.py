import os
import sys
import asyncio
from main import main
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, \
    QComboBox, QMessageBox, QCheckBox, QGroupBox
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
from qasync import QEventLoop, asyncClose, asyncSlot
from monitor_window import MonitorWindow


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("Threadsicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.monitor_window = None
        self.initUI()
        self.center()

    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口属性
        self.setWindowTitle('Threads用戶獲取')  # 这个标题现在只用于任务栏显示
        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # 设置为0间距
        main_layout.setContentsMargins(0, 0, 0, 15)  # 左右和上边距设为0，只保留底部边距

        # 创建标题容器，设置背景色和下边框
        title_container = QWidget()
        title_container.setStyleSheet("background-color: #ff8965;border-bottom: 3px solid #01bdae;")
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setContentsMargins(20, 0, 20, 0)  # 保留左右内边距

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(25, 5, 0, 0)
        self.title_label = QLabel("", self)  # 自定义标题文本
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        self.title_label.setStyleSheet('background-color: #ff8965;border: none;')
        self.setFixedSize(350, 0)  # 设置窗口的固定大小
        title_bar.addWidget(self.title_label)

        # 添加关闭按钮到标题栏
        close_button = QPushButton("")  # 改变按钮文本为减号表示最小化
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #ddd;
                        border-radius: 12px;
                    }
                    QPushButton:hover {
                        background-color: #01bcae;
                    }
                """)
        close_button.clicked.connect(self.showMinimized)  # 连接到最小化方法
        title_bar.addWidget(close_button)

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
                    }
                    QPushButton:hover {
                        background-color: #ff4d4f;
                        color: white;
                    }
                """)
        title_bar.addWidget(close_button)

        # 添加标题文字
        title_text_layout = QVBoxLayout()
        title_text_layout.setAlignment(Qt.AlignCenter)
        title_text_layout.setContentsMargins(0, 10, 0, 10)  # 添加上下内边距

        main_title = QLabel("Threads用戶獲取", self)
        main_title.setFont(QFont("微軟雅黑", 16, QFont.Bold))
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("color: white; margin-top: 5px;border: none;")

        sub_title = QLabel("高效獲取和管理用戶數據", self)
        sub_title.setFont(QFont("微軟雅黑", 10))
        sub_title.setAlignment(Qt.AlignCenter)
        sub_title.setStyleSheet("color: white; margin-bottom: 10px;border: none;")

        title_text_layout.addWidget(main_title)
        title_text_layout.addWidget(sub_title)

        # 将标题栏和标题文字添加到标题容器
        title_container_layout.addLayout(title_bar)
        title_container_layout.addLayout(title_text_layout)

        # 将标题容器添加到主布局
        main_layout.addWidget(title_container)

        # 创建内容容器，用于放置其他控件并保留边距
        content_container = QWidget()
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(20, 10, 20, 0)  # 设置内容区域的左右边距
        content_container_layout.setSpacing(10)

        # 创建三个输入框
        self.input0 = QLineEdit(self)
        self.input0.setText("000")
        self.input0.setPlaceholderText("請輸入設備號...")
        self.input0.setStyleSheet("""
                    QLineEdit {
                        padding: 10px;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 14px;
                        background-color: white;
                        color: #a6acb2;
                    }
                    QLineEdit:focus {
                        border: 1px solid #1890ff;
                        box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
                    }
                     QLineEdit:hover {
                        background-color: #e9ecef;
                        color: black;
                    }
                """)
        self.input1 = QLineEdit(self)
        self.input1.setText("")
        self.input1.setPlaceholderText("請輸入關鍵詞...")
        self.input1.setStyleSheet("""
                            QLineEdit {
                                padding: 10px;
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                font-size: 14px;
                                background-color: white;
                                color: #a6acb2;
                            }
                            QLineEdit:focus {
                                border: 1px solid #1890ff;
                                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
                            }
                            QLineEdit:hover {
                        background-color: #e9ecef;
                        color: black;
                    }
                        """)
        self.input2 = QLineEdit(self)
        self.input2.setText("2025")
        self.input2.setPlaceholderText("請輸入獲取的人數...")
        self.input2.setStyleSheet("""
                            QLineEdit {
                                padding: 10px;
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                font-size: 14px;
                                background-color: white;
                                color: #a6acb2;
                            }
                            QLineEdit:focus {
                                border: 1px solid #1890ff;
                                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
                            }
                            QLineEdit:hover {
                        background-color: #e9ecef;
                        color: black;
                    }
                        """)
        self.input3 = QLineEdit(self)
        self.input3.setText("10")
        self.input3.setPlaceholderText("請輸入獲取的貼文數...")
        self.input3.setStyleSheet("""
                            QLineEdit {
                                padding: 10px;
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                font-size: 14px;
                                background-color: white;
                                color: #a6acb2;
                            }
                            QLineEdit:focus {
                                border: 1px solid #1890ff;
                                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
                            }
                            QLineEdit:hover {
                        background-color: #e9ecef;
                        color: black;
                    }
                        """)
        self.input4 = QLineEdit(self)
        self.input4.setText("20")
        self.input4.setPlaceholderText("請輸入獲取幾個用戶的粉絲...")
        self.input4.setStyleSheet("""
                            QLineEdit {
                                padding: 10px;
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                font-size: 14px;
                                background-color: white;
                                color: #a6acb2;
                            }
                            QLineEdit:focus {
                                border: 1px solid #1890ff;
                                box-shadow: 0 0 12px rgba(24, 144, 255, 0.4);
                            }
                            QLineEdit:hover {
                        background-color: #e9ecef;
                        color: black;
                    }
                        """)
        content_container_layout.addWidget(QLabel("設備號:"))
        content_container_layout.addWidget(self.input0)
        content_container_layout.addWidget(QLabel("指定關鍵詞:"))
        content_container_layout.addWidget(self.input1)
        content_container_layout.addWidget(QLabel("獲取的人數:"))
        content_container_layout.addWidget(self.input2)
        content_container_layout.addWidget(QLabel("獲取的貼文的評論數:"))
        content_container_layout.addWidget(self.input3)
        content_container_layout.addWidget(QLabel("獲取幾個用戶的粉絲:"))
        content_container_layout.addWidget(self.input4)

        # 创建任务类型分组框
        task_group = QGroupBox("任務類型:")
        task_group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border-left: 2px solid #ff7e5f;
                        border-radius: 5px;
                        margin-top: 5px;
                        padding-top: 20px;
                        color: #a6acb2;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 5px 0 5px;
                    }
                """)
        task_layout = QHBoxLayout()

        self.check_search = QCheckBox("關鍵詞", self)
        self.check_search.setStyleSheet("""
        QCheckBox {
                        background-color: white;
                    }""")
        self.check_userpost = QCheckBox("用戶帖子", self)
        self.check_userpost.setStyleSheet('background-color: white;')
        self.check_follower = QCheckBox("粉絲列表", self)
        self.check_follower.setStyleSheet('background-color: white;')

        task_layout.addWidget(self.check_search)
        task_layout.addWidget(self.check_userpost)
        task_layout.addWidget(self.check_follower)

        task_group.setLayout(task_layout)
        content_container_layout.addWidget(task_group)

        # 创建水平布局用于放置按钮并居中
        button_layout = QHBoxLayout()
        self.button = QPushButton('開始執行任務', self)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                background-color: #01c6ad;
                font-size: 14px;
                font-weight: bold;
                padding:13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7FFFD4;
            }
        """)
        button_layout.addWidget(self.button)

        content_container_layout.addLayout(button_layout)

        # 创建底部信息栏
        footer_layout = QHBoxLayout()

        # 左下角的标签
        self.days_label = QLabel(f"時間：{days}天", self)
        self.days_label.setFont(QFont("微軟雅黑", 10))
        self.days_label.setStyleSheet("color: gray;")

        # 右下角的版本标签
        self.version_label = QLabel(f"版本：{versions}", self)
        self.version_label.setFont(QFont("微軟雅黑", 10))
        self.version_label.setStyleSheet("color: gray;")
        self.version_label.setAlignment(Qt.AlignRight)

        footer_layout.addWidget(self.days_label)
        footer_layout.addStretch(1)  # 添加弹性空间
        footer_layout.addWidget(self.version_label)

        content_container_layout.addLayout(footer_layout)

        # 将内容容器添加到主布局
        main_layout.addWidget(content_container)

        # 连接按钮点击事件到处理函数
        self.button.clicked.connect(self.on_click)

        # 设置布局
        self.setLayout(main_layout)

        # 显示窗口
        self.show()

    def toggle_textbox(self, index):
        if index == 0:
            self.hidden_textbox.hide()
            self.adjustSize()
        elif index == 1:
            self.hidden_textbox.show()
            self.adjustSize()

    def toggle_browser_input(self, index):
        if index == 0:
            self.hidden_browser_input.hide()
            self.adjustSize()
        elif index == 1:
            self.hidden_browser_input.show()
            self.adjustSize()

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
        content3 = self.input3.text().strip()
        content4 = self.input4.text().strip()
        try:
            limit = int(content2)
            userpost_limit = int(content3)
            follower_limit = int(content4)
        except:
            QMessageBox.warning(self, "输入错误", "错误：输入必须为数字", QMessageBox.Ok)
            return

        # 验证设备号
        if not content0:
            print("错误：设备号不能为空")
            QMessageBox.warning(self, "输入错误", "错误：设备号不能为空", QMessageBox.Ok)
            return  # 终止函数执行
        if not content2:
            print("错误：人數不能为空")
            QMessageBox.warning(self, "输入错误", "错误：人數不能为空", QMessageBox.Ok)
            return  # 终止函数执行

        # 获取选中的任务类型
        selected_types = []
        if self.check_search.isChecked():
            selected_types.append('search')
        if self.check_userpost.isChecked():
            selected_types.append('userpost')
        if self.check_follower.isChecked():
            selected_types.append('follower')

        if not selected_types and not content1:
            QMessageBox.warning(self, "選擇錯誤", "請至少選擇一個爬取任務", QMessageBox.Ok)
            return
        # 所有验证通过后的处理
        print(f"设备号: {content0}")
        print(f"关键词: {content1}")
        print(f"人數: {limit}")
        print(f"贴文数: {userpost_limit}")
        print(f"用户粉丝: {follower_limit}")
        print(f"爬取类型: {selected_types}")
        # 创建监控窗口
        # self.create_monitor_window()
        # 启动异步任务后，不关闭窗口，而是隐藏窗口
        self.hide()  # 隐藏窗口而非关闭
        try:
            await main(content1, selected_types, limit, userpost_limit, follower_limit, None)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"任务执行失败: {str(e)}", QMessageBox.Ok)
        finally:
            self.close()


def win_main(version, day):
    global versions
    global days
    versions = version
    days = day
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # 设置应用程序的样式
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(247, 248, 249))
    palette.setColor(QPalette.WindowText, Qt.black)
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