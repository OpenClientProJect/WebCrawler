import os
import sys
import asyncio
from task import main
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox,QMessageBox
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
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
        self.setWindowTitle('Instagram用戶獲取')
        self.resize(400, 650)  # 设置窗口初始大小

        # 创建整体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建顶部渐变标题区域
        header_widget = QWidget()
        header_widget.setFixedHeight(120)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # 标题栏
        title_bar = QHBoxLayout()

        # Instagram图标和标题
        icon_title_layout = QVBoxLayout()
        icon_title_layout.setSpacing(8)

        # Instagram图标
        icon_label = QLabel(self)
        icon_path = resource_path("./image/Instagram.png")
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(32,32,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        icon_label.setStyleSheet("background: transparent; border: none;")
        icon_title_layout.addWidget(icon_label)

        self.title_label = QLabel("Instagram用戶獲取", self)
        self.title_label.setFont(QFont("微軟雅黑", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent; border: none;")
        icon_title_layout.addWidget(self.title_label)

        title_bar.addLayout(icon_title_layout)
        title_bar.addStretch(1)

        # 窗口控制按钮
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
        title_bar.addWidget(minimize_button)

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
        title_bar.addWidget(close_button)

        header_layout.addLayout(title_bar)

        # 副标题
        subtitle = QLabel("高效獲取Instagram用戶數據", self)
        subtitle.setFont(QFont("微軟雅黑", 10,QFont.Bold))
        subtitle.setStyleSheet("color: white; background: transparent; border: none; margin-top: 5px;")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header_widget)

        # 创建主内容区域
        content_widget = QWidget()

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        input_style = """
            QLineEdit {
                padding: 5px 10px;
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
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
        """

        label_style = """
            QLabel {
                color: #495057;
                font-weight: 500;
                font-size: 15px;
                margin-bottom: 8px;
                font-family: "微軟雅黑";
            }
        """

        dropdown_style = """
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
                background-color: white;
                font-size: 12px;
                color: #495057;
                font-family: "微軟雅黑";
            }
            QComboBox:focus {
                border-color: #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #6c757d;
                margin-right: 15px;
            }
        """

        textarea_style = """
            QTextEdit {
                padding: 15px 20px;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
                background-color: white;
                font-size: 12px;
                color: #495057;
                min-height: 100px;
                font-family: "微軟雅黑";
            }
            QTextEdit:focus {
                border-color: #667eea;
                outline: none;
            }
        """
        # 输入框大小
        input_size = QSize(350, 40)


        # 设备号输入区域
        device_group = QVBoxLayout()
        device_group.setSpacing(8)

        device_label = QLabel("📱 設備號", self)
        device_label.setStyleSheet(label_style)
        device_group.addWidget(device_label)

        self.input0 = QLineEdit(self)
        self.input0.setText("000")
        self.input0.setPlaceholderText("請輸入設備號...")
        self.input0.setStyleSheet(input_style)
        self.input0.setFixedSize(input_size)
        device_group.addWidget(self.input0)

        content_layout.addLayout(device_group)

        # 关键词输入区域
        keyword_group = QVBoxLayout()
        keyword_group.setSpacing(8)

        # 创建水平布局用于图片和文本
        keyword_label_layout = QHBoxLayout()
        keyword_label_layout.setSpacing(3)

        # 添加yuechi图片
        yuechi_path = resource_path("./image/yuechi.png")
        yuechi_icon = QLabel(self)
        yuechi_pixmap = QPixmap(yuechi_path)
        yuechi_icon.setPixmap(yuechi_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        yuechi_icon.setStyleSheet("background: transparent; border: none;")
        keyword_label_layout.addWidget(yuechi_icon)

        # 添加文本标签
        keyword_label = QLabel("指定關鍵詞", self)
        keyword_label.setStyleSheet(label_style)
        keyword_label_layout.addWidget(keyword_label)

        keyword_label_layout.addStretch(1)  # 添加伸缩量
        keyword_group.addLayout(keyword_label_layout)

        self.input1 = QLineEdit(self)
        self.input1.setText("")
        self.input1.setPlaceholderText("請輸入關鍵詞...")
        self.input1.setStyleSheet(input_style)
        self.input1.setFixedSize(input_size)
        keyword_group.addWidget(self.input1)

        content_layout.addLayout(keyword_group)

        # 人数输入区域
        count_group = QVBoxLayout()
        count_group.setSpacing(8)

        # 创建水平布局用于图片和文本
        count_label_layout = QHBoxLayout()
        count_label_layout.setSpacing(3)

        # 添加shequn图片
        shequn_path = resource_path("./image/shequn.png")
        shequn_icon = QLabel(self)
        shequn_pixmap = QPixmap(shequn_path)
        shequn_icon.setPixmap(shequn_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        shequn_icon.setStyleSheet("background: transparent; border: none;")
        count_label_layout.addWidget(shequn_icon)

        # 添加文本标签
        count_label = QLabel("獲取的人數", self)
        count_label.setStyleSheet(label_style)
        count_label_layout.addWidget(count_label)

        count_label_layout.addStretch(1)  # 添加伸缩量
        count_group.addLayout(count_label_layout)

        self.input2 = QLineEdit(self)
        self.input2.setText("2025")
        self.input2.setPlaceholderText("請輸入獲取的人數...")
        self.input2.setStyleSheet(input_style)
        self.input2.setFixedSize(input_size)
        count_group.addWidget(self.input2)

        content_layout.addLayout(count_group)

        # 作品链接区域
        browser_group = QVBoxLayout()
        browser_group.setSpacing(8)

        # 创建水平布局
        browser_label_layout = QHBoxLayout()
        browser_label_layout.setSpacing(3)

        # 图片左侧
        browser_peth = resource_path("./image/shixin.png")
        shixin_icon = QLabel(self)
        shixin_pixmap = QPixmap(browser_peth)
        shixin_icon.setPixmap(shixin_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        shixin_icon.setStyleSheet("background: transparent; border: none;")
        browser_label_layout.addWidget(shixin_icon)

        # 文本标签右侧
        browser_label = QLabel("指定作品的點讚用戶列表和評論用戶列表", self)
        browser_label.setStyleSheet(label_style)
        browser_label_layout.addWidget(browser_label)

        browser_label_layout.addStretch(1)  # 添加伸缩量
        browser_group.addLayout(browser_label_layout)

        self.browser_dropdown = QComboBox(self)
        self.browser_dropdown.setFixedSize(input_size)
        self.browser_dropdown.addItem("隱藏輸入的鏈接地址框")
        self.browser_dropdown.addItem("顯示輸入的鏈接地址框")
        self.browser_dropdown.setStyleSheet(dropdown_style)
        self.browser_dropdown.currentIndexChanged.connect(self.toggle_browser_input)
        browser_group.addWidget(self.browser_dropdown)

        self.hidden_browser_input = QTextEdit(self)
        self.hidden_browser_input.setPlaceholderText("請輸入點讚用戶評論地址...")
        self.hidden_browser_input.setStyleSheet(textarea_style)
        self.hidden_browser_input.hide()
        browser_group.addWidget(self.hidden_browser_input)

        content_layout.addLayout(browser_group)
        self.toggle_browser_input(self.browser_dropdown.currentIndex())

        # 粉丝链接区域
        fans_group = QVBoxLayout()
        fans_group.setSpacing(8)

        # 创建水平布局
        fans_label_layout = QHBoxLayout()
        fans_label_layout.setSpacing(3)

        # 图片左侧
        fans_peth = resource_path("./image/renqun.png")
        renqun_icon = QLabel(self)
        renqun_pixmap = QPixmap(fans_peth)
        renqun_icon.setPixmap(renqun_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        renqun_icon.setStyleSheet("background: transparent; border: none;")
        fans_label_layout.addWidget(renqun_icon)

        # 文本标签右侧
        fans_label = QLabel("指定作者的粉絲用戶列表", self)
        fans_label.setStyleSheet(label_style)
        fans_label_layout.addWidget(fans_label)

        fans_label_layout.addStretch(1)  # 添加伸缩量
        fans_group.addLayout(fans_label_layout)

        self.dropdown = QComboBox(self)
        self.dropdown.addItem("隱藏輸入的鏈接地址框")
        self.dropdown.addItem("顯示輸入的鏈接地址框")
        self.dropdown.setFixedSize(input_size)
        self.dropdown.setStyleSheet(dropdown_style)
        self.dropdown.currentIndexChanged.connect(self.toggle_textbox)
        fans_group.addWidget(self.dropdown)

        self.hidden_textbox = QTextEdit(self)
        self.hidden_textbox.setPlaceholderText("請輸入粉絲用戶地址...")
        self.hidden_textbox.setStyleSheet(textarea_style)
        self.hidden_textbox.hide()
        fans_group.addWidget(self.hidden_textbox)

        content_layout.addLayout(fans_group)
        self.toggle_textbox(self.dropdown.currentIndex())

        # 确定按钮
        self.button = QPushButton(self)
        self.button.setFixedHeight(50)
        self.button.setFont(QFont("微軟雅黑", 13, QFont.Bold))
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(15, 0, 15, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignCenter)  # 设置水平居中
        
        # 添加Begin图片
        begin_path = resource_path("./image/Begin.png")
        begin_icon = QLabel(self)
        begin_pixmap = QPixmap(begin_path)
        begin_icon.setPixmap(begin_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        begin_icon.setStyleSheet("background: transparent; border: none;")
        button_layout.addWidget(begin_icon)
        
        # 添加文本
        button_text = QLabel("確定執行", self)
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
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4e5bc6, stop:1 #5e377e);
            }
        """)
        content_layout.addWidget(self.button)

        # 版本信息
        info_layout = QHBoxLayout()

        # 时间区域
        time_container_layout = QHBoxLayout()
        time_container_layout.setSpacing(3)
        
        # 添加shizhong图片
        shizhong_path = resource_path("./image/shizhong.png")
        shizhong_icon = QLabel(self)
        shizhong_pixmap = QPixmap(shizhong_path)
        shizhong_icon.setPixmap(shizhong_pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        shizhong_icon.setStyleSheet("background: transparent; border: none;")
        time_container_layout.addWidget(shizhong_icon)
        
        # 添加时间文本
        time_label = QLabel(f"時間: {days}天", self)
        time_label.setFont(QFont("微軟雅黑", 9))
        time_label.setStyleSheet("color: #6c757d; background: transparent;")
        time_container_layout.addWidget(time_label)
        
        info_layout.addLayout(time_container_layout)

        info_layout.addStretch(1)

        # 版本区域
        version_container_layout = QHBoxLayout()
        version_container_layout.setSpacing(3)
        
        # 添加git-branch-line图片
        git_branch_path = resource_path("./image/git-branch-line.png")
        git_branch_icon = QLabel(self)
        git_branch_pixmap = QPixmap(git_branch_path)
        git_branch_icon.setPixmap(git_branch_pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        git_branch_icon.setStyleSheet("background: transparent; border: none;")
        version_container_layout.addWidget(git_branch_icon)
        
        # 添加版本文本
        version_label = QLabel(f"版本: {versions}", self)
        version_label.setFont(QFont("微軟雅黑", 9))
        version_label.setStyleSheet("color: #6c757d; background: transparent;")
        version_container_layout.addWidget(version_label)
        
        info_layout.addLayout(version_container_layout)

        content_layout.addLayout(info_layout)

        main_layout.addWidget(content_widget)

        # 连接按钮点击事件到处理函数
        self.button.clicked.connect(self.on_click)

        # 设置布局
        self.setLayout(main_layout)

        # 显示窗口
        self.show()

    def toggle_textbox(self, index):
        if index == 0:
            self.hidden_textbox.hide()
        elif index == 1:
            self.hidden_textbox.show()

        # 调整窗口大小
        self.adjustSize()

    def toggle_browser_input(self, index):
        if index == 0:
            self.hidden_browser_input.hide()
        elif index == 1:
            self.hidden_browser_input.show()

        # 调整窗口大小
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
# if __name__ == '__main__':
#     win_main()
