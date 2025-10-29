import asyncio
import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox,
                             QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from qasync import QEventLoop, asyncClose, asyncSlot
from FB_middle import main
from database_manager import db_manager
class MyApp(QWidget):
    # 嵌入模式下请求隐藏主窗口
    hideMainRequested = pyqtSignal()
    def __init__(self, embedded=False, version=None, day=None):
        super().__init__()
        self.embedded = embedded
        self.version = version
        self.day = day
        self.crawler = None  # 保存crawler实例
        self.is_searching = False  # 添加搜索状态标志
        self.initUI()
        if not self.embedded:
            self.center()

    def initUI(self):
        # 禁用默认的窗口框架（仅独立窗口时）
        if not self.embedded:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setWindowTitle('爬虫脚本')
            self.setFixedSize(520, 500)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建内容区域
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # 第一行：长输入框和搜索按钮
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("請輸入搜索內容...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1890ff;
            }
        """)

        self.search_button = QPushButton("搜索")
        self.search_button.setFixedSize(80, 35)
        self.search_button.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                background-color: #1890ff;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        row1_layout.addWidget(self.search_input)
        row1_layout.addWidget(self.search_button)
        content_layout.addLayout(row1_layout)

        # 第二行：搜索数量和爬取数量 - 修复布局问题
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        # 搜索数量
        search_count_layout = QHBoxLayout()
        search_count_layout.setSpacing(5)
        search_count_label = QLabel("搜索数量:")
        search_count_label.setFont(QFont("微軟雅黑", 10))
        self.search_count_input = QLineEdit()
        self.search_count_input.setText("10")
        self.search_count_input.setPlaceholderText("例如: 100")
        self.search_count_input.setFixedWidth(100)
        self.search_count_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        search_count_layout.addWidget(search_count_label)
        search_count_layout.addWidget(self.search_count_input)
        # 移除不必要的 addStretch(1)

        # 爬取数量
        crawl_count_layout = QHBoxLayout()
        crawl_count_layout.setSpacing(5)
        crawl_count_label = QLabel("爬取数量:")
        crawl_count_label.setFont(QFont("微軟雅黑", 10))
        self.crawl_count_input = QLineEdit()
        self.crawl_count_input.setText("2025")
        self.crawl_count_input.setPlaceholderText("例如: 50")
        self.crawl_count_input.setFixedWidth(100)
        self.crawl_count_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        crawl_count_layout.addWidget(crawl_count_label)
        crawl_count_layout.addWidget(self.crawl_count_input)
        # 移除不必要的 addStretch(1)

        row2_layout.addLayout(search_count_layout)
        row2_layout.addStretch(1)  # 在两者之间添加拉伸，使它们分布在左右两侧
        row2_layout.addLayout(crawl_count_layout)
        content_layout.addLayout(row2_layout)

        # 第三行：设备编号和下拉框
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(10)

        # 设备编号
        device_layout = QHBoxLayout()
        device_layout.setSpacing(5)
        device_label = QLabel("设备编号:")
        device_label.setFont(QFont("微軟雅黑", 10))
        self.device_input = QLineEdit()
        self.device_input.setText("000")
        self.device_input.setPlaceholderText("請輸入設備編號")
        self.device_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_input)

        # 下拉框
        self.combo_box = QComboBox()
        self.combo_box.addItem("社團")
        self.combo_box.addItem("粉絲專頁")
        self.combo_box.setFixedWidth(120)
        self.combo_box.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)

        row3_layout.addLayout(device_layout)
        row3_layout.addWidget(self.combo_box)
        content_layout.addLayout(row3_layout)

        # 地址文本框
        address_label = QLabel("地址列表:")
        address_label.setFont(QFont("微軟雅黑", 10))
        content_layout.addWidget(address_label)

        self.address_textbox = QTextEdit()
        self.address_textbox.setPlaceholderText(
            "請輸入地址，每行一個...\n例：https://www.facebook.com/groups/613691032041093/members")
        self.address_textbox.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            /* 美化滚动条 */
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f5f5f5;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
        """)
        content_layout.addWidget(self.address_textbox)

        # 底部布局
        bottom_layout = QHBoxLayout()

        # 右下角确定按钮
        self.confirm_button = QPushButton("確定")
        self.confirm_button.setFixedSize(100, 35)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                background-color: #52c41a;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        if not self.embedded:
            bottom_layout.addWidget(self.version_label)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.confirm_button)
        content_layout.addLayout(bottom_layout)

        # 设置主布局
        main_container = QFrame()
        main_container.setLayout(content_layout)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        main_layout.addWidget(main_container)

        self.setLayout(main_layout)

        # 连接按钮事件
        self.confirm_button.clicked.connect(self.on_confirm)
        self.search_button.clicked.connect(self.on_search)
        # 必须实现的拖动窗口的方法

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.embedded:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.embedded:
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

    def set_search_button_state(self, searching):
        """设置搜索按钮状态"""
        self.is_searching = searching
        if searching:
            self.search_button.setText("获取中...")
            self.search_button.setEnabled(False)
        else:
            self.search_button.setText("搜索")
            self.search_button.setEnabled(True)

    @asyncSlot()
    async def on_search(self):
        """搜索按钮：执行key_groups并显示结果在地址框"""
        if self.is_searching:
            return  # 防止重复点击

        search_content = self.search_input.text()
        if not search_content.strip():
            QMessageBox.warning(self, "警告", "请输入搜索内容！")
            return

        # 获取其他参数
        search_count = self.search_count_input.text()
        if not search_count.strip():
            QMessageBox.warning(self, "警告", "请输入搜索数量！")
            return

        crawl_count = self.crawl_count_input.text()
        device_id = self.device_input.text()
        combo_value = self.combo_box.currentText()

        params = {
            'search_content': search_content,
            'search_count': search_count,
            'crawl_count': crawl_count,
            'device_id': device_id,
            'combo_value': combo_value,
            'action': 'search'
        }

        print(f"搜索内容: {search_content}")

        # 设置搜索按钮状态为"获取中"
        self.set_search_button_state(True)
        self.confirm_button.setEnabled(False)  # 禁用确定按钮

        try:
            # 执行搜索操作 - 创建新的crawler实例
            crawler = await main(params)
            if crawler and hasattr(crawler, 'search_results'):
                # 将搜索结果显示在地址框中
                addresses_text = '\n'.join(crawler.search_results)
                self.address_textbox.setPlainText(addresses_text)
                self.search_results = crawler.search_results  # 保存结果
                QMessageBox.information(self, "完成", f"搜索完成，找到 {len(crawler.search_results)} 个地址！")
            else:
                QMessageBox.warning(self, "警告", "搜索完成但未找到地址！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索过程中出现错误: {str(e)}")
        finally:
            # 无论成功失败，都恢复按钮状态
            self.set_search_button_state(False)
            self.confirm_button.setEnabled(True)

    @asyncSlot()
    async def on_confirm(self):
        """确定按钮：执行csgetusers，先检查地址是否重复"""
        if self.is_searching:
            QMessageBox.warning(self, "警告", "请等待搜索完成！")
            return

        # 获取地址列表
        addresses = self.address_textbox.toPlainText().strip()
        if not addresses:
            QMessageBox.warning(self, "警告", "地址列表为空，请先进行搜索！")
            return

        if not self.crawl_count_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入爬取数量！")
            return

        # 处理地址列表
        address_list = [addr.strip() for addr in addresses.split('\n') if addr.strip()]

        # 检查重复地址
        try:
            result = db_manager.check_duplicate_addresses(address_list)
            duplicate_addresses = result['duplicate']
            unique_addresses = result['unique']
            failed_addresses = result['failed']

            # 如果有解析失败的地址，提示用户
            # if failed_addresses:
            #     failed_text = "\n".join(failed_addresses[:5])  # 最多显示5个
            #     if len(failed_addresses) > 5:
            #         failed_text += f"\n... 还有 {len(failed_addresses) - 5} 个地址格式错误"
            #
            #     reply = QMessageBox.question(
            #         self,
            #         "地址格式错误",
            #         f"以下地址格式不正确，无法提取群组ID：\n\n{failed_text}\n\n是否继续处理其他有效地址？",
            #         QMessageBox.Yes | QMessageBox.No,
            #         QMessageBox.Yes
            #     )
            #
            #     if reply == QMessageBox.No:
            #         return

            # 如果有重复地址，提示用户
            if duplicate_addresses:
                duplicate_text = "\n".join(duplicate_addresses[:5])  # 最多显示5个
                if len(duplicate_addresses) > 5:
                    duplicate_text += f"\n... 还有 {len(duplicate_addresses) - 5} 个重复地址"

                reply = QMessageBox.question(
                    self,
                    "发现重复地址",
                    f"发现 {len(duplicate_addresses)} 个重复地址：\n\n{duplicate_text}\n\n是否自动删除重复地址，只保留新地址？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # 删除重复地址，只保留唯一地址
                    remaining_addresses = unique_addresses + failed_addresses  # 保留格式错误的地址让用户决定
                    self.address_textbox.setPlainText("\n".join(remaining_addresses))
                    if not unique_addresses:
                        QMessageBox.warning(self, "警告", "所有有效地址都已存在数据库中，没有新地址可处理！")
                        return

            # 如果没有唯一地址且没有格式错误的地址，则返回
            if not unique_addresses and not failed_addresses:
                QMessageBox.warning(self, "警告", "没有有效的地址可处理！")
                return

        except Exception as e:
            QMessageBox.warning(self, "数据库连接错误", f"无法连接数据库检查重复地址：{str(e)}\n将继续处理所有地址。")
            unique_addresses = address_list

        # 获取所有输入内容
        search_content = self.search_input.text()
        search_count = self.search_count_input.text()
        crawl_count = self.crawl_count_input.text()
        device_id = self.device_input.text()
        combo_value = self.combo_box.currentText()
        print("下拉框：", combo_value)

        # 使用处理后的地址列表
        final_addresses = unique_addresses + failed_addresses  # 包含格式错误的地址，让爬虫尝试处理

        params = {
            'search_content': search_content,
            'search_count': search_count,
            'crawl_count': crawl_count,
            'device_id': device_id,
            'combo_value': combo_value,
            'addresses': final_addresses,
            'action': 'confirm'
        }

        print("开始执行爬取用户操作...")

        try:
            if not self.embedded:
                self.hide()
            self.confirm_button.setEnabled(False)

            # 通知主窗口隐藏（当作为子页面嵌入时）
            if self.embedded:
                self.hideMainRequested.emit()

            # 总是创建新的crawler实例，避免资源冲突
            await main(params)

            QMessageBox.information(self, "完成", "爬取任务已完成！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"爬取过程中出现错误: {str(e)}")
        finally:
            self.confirm_button.setEnabled(True)
            if not self.embedded:
                self.show()

def win_main(version, day):
    global versions, days
    versions = version
    days = day

    app = QApplication(sys.argv)

    # 设置异步事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 设置应用程序样式
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

    app.setFont(QFont("微軟雅黑", 10))

    ex = MyApp()
    ex.show()

    try:
        with loop:
            sys.exit(loop.run_forever())
    except KeyboardInterrupt:
        pass
    finally:
        # 确保清理资源
        db_manager.close_connection()


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