import os
import sys
import asyncio
from task import main
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
from qasync import QEventLoop, asyncClose, asyncSlot

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("IGicon.ico")
        self.setWindowIcon(QIcon(icon_path))
        # self.setWindowIcon(QIcon("IGicon.ico"))
        self.initUI()
        self.center()


    def initUI(self):
        # 禁用默认的窗口框架
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置窗口属性
        self.setWindowTitle('Instagram用戶獲取')  # 这个标题现在只用于任务栏显示
        # 创建整体布局
        main_layout = QVBoxLayout()

        # 创建自定义标题栏
        title_bar = QHBoxLayout()
        self.title_label = QLabel("Instagram用戶獲取", self)  # 自定义标题文本
        self.title_label.setFont(QFont("微軟雅黑", 12, QFont.Bold))
        # self.resize(350, 300)
        self.setFixedSize(350, 0)  # 设置窗口的固定大小
        title_bar.addWidget(self.title_label)
        title_bar.addStretch(1)

        # 添加关闭按钮到标题栏
        close_button = QPushButton("-")  # 改变按钮文本为减号表示最小化
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.setFixedSize(24, 24)
        close_button.clicked.connect(self.showMinimized)  # 连接到最小化方法
        title_bar.addWidget(close_button)
        # 添加关闭按钮到标题栏
        close_button = QPushButton("×")
        close_button.setFont(QFont("微軟雅黑", 12))
        close_button.setFixedSize(24, 24)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        close_button.setStyleSheet("""
                   QPushButton:hover {
                       background-color: red;
                   }
               """)
        # 将标题栏添加到主布局
        main_layout.addLayout(title_bar)

        # 创建三个输入框
        self.input0 = QLineEdit(self)
        self.input0.setText("000")
        self.input0.setPlaceholderText("請輸入設備號...")
        self.input1 = QLineEdit(self)
        self.input1.setText("")
        self.input1.setPlaceholderText("請輸入關鍵詞...")
        self.input2 = QLineEdit(self)
        self.input2.setText("2025")
        self.input2.setPlaceholderText("請輸入獲取的人數...")
        main_layout.addWidget(QLabel("設備號:"))
        main_layout.addWidget(self.input0)
        main_layout.addWidget(QLabel("指定關鍵詞:"))
        main_layout.addWidget(self.input1)
        main_layout.addWidget(QLabel("獲取的人數:"))
        main_layout.addWidget(self.input2)

        # 刷新浏览器数下拉菜单
        self.browser_dropdown = QComboBox(self)
        self.browser_dropdown.addItem("隱藏輸入的鏈接地址框")
        self.browser_dropdown.addItem("顯示輸入的鏈接地址框")
        self.browser_dropdown.currentIndexChanged.connect(self.toggle_browser_input)
        main_layout.addWidget(QLabel("指定作品的點讚用戶列表和評論用戶列表:"))
        main_layout.addWidget(self.browser_dropdown)

        # 隐藏的浏览器数输入框
        self.hidden_browser_input = QTextEdit(self)
        self.hidden_browser_input.setPlaceholderText("請輸入點讚用戶評論地址...")
        self.hidden_browser_input.hide()
        main_layout.addWidget(self.hidden_browser_input)
        self.toggle_browser_input(self.browser_dropdown.currentIndex())

        # 创建下拉菜单
        self.dropdown = QComboBox(self)
        self.dropdown.addItem("隱藏輸入的鏈接地址框")
        self.dropdown.addItem("顯示輸入的鏈接地址框")
        self.dropdown.currentIndexChanged.connect(self.toggle_textbox)

        main_layout.addWidget(QLabel("指定作者的粉絲用戶列表:"))
        main_layout.addWidget(self.dropdown)

        # 创建一个初始状态为隐藏的文本框，并设定最小高度以保持布局稳定
        self.hidden_textbox = QTextEdit(self)
        self.hidden_textbox.setPlaceholderText("請輸入粉絲用戶地址...")
        self.hidden_textbox.hide()
        main_layout.addWidget(self.hidden_textbox)
        # 设置默认状态（根据下拉菜单的第一个选项）
        self.toggle_textbox(self.dropdown.currentIndex())

        # 创建水平布局用于放置按钮并居中
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # 添加伸缩量使得按钮居中
        self.button = QPushButton('確定', self)
        self.button.setFixedSize(100, 40)  # 设置按钮大小
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                background-color: #90EE90;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7FFFD4;
            }
        """)
        button_layout.addWidget(self.button)
        button_layout.addStretch(1)  # 添加伸缩量使得按钮居中

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 创建左下角的标签
        self.days_label = QLabel(f"時間：{days}天 版本：{versions}", self)
        self.days_label.setFont(QFont("微軟雅黑", 10))
        self.days_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.days_label, alignment=Qt.AlignBottom | Qt.AlignLeft)

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

        # 获取隐藏输入框内容并处理空行
        hidden_line_content = self.hidden_browser_input.toPlainText().strip()
        lines_hidden_line = [line.strip() for line in hidden_line_content.split('\n') if line.strip()]

        hidden_text_content = self.hidden_textbox.toPlainText().strip()
        lines_hidden_text = [line.strip() for line in hidden_text_content.split('\n') if line.strip()]

        # 验证设备号
        if not content0:
            print("错误：设备号不能为空")
            QMessageBox.warning(self, "输入错误", "错误：设备号不能为空", QMessageBox.Ok)
            return  # 终止函数执行
        if not content2:
            print("错误：人數不能为空")
            QMessageBox.warning(self, "输入错误", "错误：人數不能为空", QMessageBox.Ok)
            return  # 终止函数执行
        # 验证链接地址（当输入框可见时）
        if self.browser_dropdown.currentIndex() == 1 and not lines_hidden_line:
            print("错误：请填写有效的鏈接地址")
            QMessageBox.warning(self, "輸入錯誤", "錯誤：未填寫有效的鏈接地址", QMessageBox.Ok)
            return

        # 验证粉丝地址（当输入框可见时）
        if self.dropdown.currentIndex() == 1 and not lines_hidden_text:
            print("错误：请填写有效的粉絲地址")
            QMessageBox.warning(self, "輸入錯誤", "錯誤：未填寫有效的粉絲地址", QMessageBox.Ok)
            return

        # 所有验证通过后的处理
        print(f"设备号: {content0}")
        print(f"关键词: {content1}")
        print(f"人數: {content2}")
        print("作品链接:", lines_hidden_line)
        print("粉絲链接:", lines_hidden_text)
        # 启动异步任务后，不关闭窗口，而是隐藏窗口
        self.hide()  # 隐藏窗口而非关闭
        try:
            await main(content0, content1,content2, lines_hidden_line, lines_hidden_text)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"任务执行失败: {str(e)}", QMessageBox.Ok)
        finally:
            self.close()  # 任务完成后关闭窗口

def win_main(version,day):
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
    ex = MyApp()
    ex.show()
    # app.exec_()  # 执行事件循环
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
# if __name__ == '__main__':
#     win_main()