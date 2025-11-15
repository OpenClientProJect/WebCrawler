import re
import sys
from pathlib import Path

from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DetailPage(QWidget):
    """指定帖子爬取页面"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # 创建标题标签
        title_label = QLabel("指定帖子爬取")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # 创建输入框标签
        url_label = QLabel("帖子鏈接")
        url_label.setStyleSheet("color: #34495e; font-size: 12px; font-weight: bold;")
        
        # 创建输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入要抓取的鏈接")
        self.url_input.setStyleSheet(self.get_input_style())
        self.url_input.setMinimumHeight(40)
        self.url_input.returnPressed.connect(self.on_start_clicked)
        
        # 创建开始按钮
        self.start_button = QPushButton("開始爬取")
        self.start_button.setStyleSheet(self.get_button_style())
        self.start_button.setMinimumHeight(45)
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.on_start_clicked)
        
        # 创建状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 8px;")
        self.status_label.setWordWrap(True)
        
        # 创建输出文本框
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        self.output_text.setMaximumHeight(250)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.output_text.hide()
        
        layout.addWidget(title_label)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.output_text)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_input_style(self) -> str:
        return """
            QLineEdit {
                background-color: white;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                outline: none;
            }
            QLineEdit:hover {
                border: 2px solid #bdc3c7;
            }
        """
    
    def get_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    def on_start_clicked(self) -> None:
        if self.parent_window:
            self.parent_window.start_crawler("detail", self.url_input.text().strip())


class KeywordSearchPage(QWidget):
    """關鍵詞搜索爬取页面"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # 创建标题标签
        title_label = QLabel("關鍵詞搜索爬取")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # 创建输入框标签
        keyword_label = QLabel("關鍵詞")
        keyword_label.setStyleSheet("color: #34495e; font-size: 12px; font-weight: bold;")
        
        # 创建输入框
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("輸入搜索關鍵詞")
        self.keyword_input.setStyleSheet(self.get_input_style())
        self.keyword_input.setMinimumHeight(40)
        self.keyword_input.returnPressed.connect(self.on_start_clicked)
        
        # 创建开始按钮
        self.start_button = QPushButton("開始爬取")
        self.start_button.setStyleSheet(self.get_button_style())
        self.start_button.setMinimumHeight(45)
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.on_start_clicked)
        
        # 创建状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 8px;")
        self.status_label.setWordWrap(True)
        
        # 创建输出文本框
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        self.output_text.setMaximumHeight(250)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.output_text.hide()
        
        layout.addWidget(title_label)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(keyword_label)
        layout.addWidget(self.keyword_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.output_text)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_input_style(self) -> str:
        return """
            QLineEdit {
                background-color: white;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                outline: none;
            }
            QLineEdit:hover {
                border: 2px solid #bdc3c7;
            }
        """
    
    def get_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    def on_start_clicked(self) -> None:
        if self.parent_window:
            self.parent_window.start_crawler("search", self.keyword_input.text().strip())


class HomeWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("小紅書 - 評論信息爬取")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # 居中显示窗口
        self.center_window()
        
        # 设置样式
        self.setStyleSheet(self.get_window_style())
        
        # 获取项目根目录（兼容 PyInstaller 打包路径）
        if getattr(sys, "frozen", False):
            # 打包后的临时目录
            self.project_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        else:
            self.project_root = Path(__file__).parent.parent.absolute()
        self.xhs_config_path = self.project_root / "config" / "xhs_config.py"
        self.base_config_path = self.project_root / "config" / "base_config.py"
        
        # 创建进程对象
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.on_process_output)
        self.process.readyReadStandardError.connect(self.on_process_error)
        self.process.finished.connect(self.on_process_finished)
        
        # 当前活动页面
        self.current_page = None
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self) -> None:
        # 创建主布局（水平布局：左侧菜单 + 右侧内容）
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建左侧菜单栏
        menu_widget = self.create_menu_bar()
        
        # 创建右侧内容区域（堆叠窗口）
        self.stacked_widget = QStackedWidget()
        
        # 创建两个页面
        self.keyword_page = KeywordSearchPage(self)
        self.detail_page = DetailPage(self)
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.keyword_page)
        self.stacked_widget.addWidget(self.detail_page)
        
        # 默认显示關鍵詞搜索页面
        self.stacked_widget.setCurrentWidget(self.keyword_page)
        self.current_page = self.keyword_page
        
        # 添加到主布局
        main_layout.addWidget(menu_widget)
        main_layout.addWidget(self.stacked_widget, 1)  # 1 表示拉伸因子
        
        self.setLayout(main_layout)
    
    def create_menu_bar(self) -> QWidget:
        """创建左侧菜单栏"""
        menu_widget = QWidget()
        menu_widget.setFixedWidth(200)
        menu_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
        """)
        
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(10)
        menu_layout.setContentsMargins(15, 20, 15, 20)
        
        # 菜单标题
        menu_title = QLabel("功能菜單")
        menu_title.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 0px;
            }
        """)
        menu_layout.addWidget(menu_title)
        
        menu_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 關鍵詞搜索按钮
        self.keyword_btn = QPushButton("關鍵詞搜索爬取")
        self.keyword_btn.setStyleSheet(self.get_menu_button_style(True))
        self.keyword_btn.setCursor(Qt.PointingHandCursor)
        self.keyword_btn.clicked.connect(lambda: self.switch_page(0))
        menu_layout.addWidget(self.keyword_btn)
        
        # 指定帖子按钮
        self.detail_btn = QPushButton("指定帖子爬取")
        self.detail_btn.setStyleSheet(self.get_menu_button_style(False))
        self.detail_btn.setCursor(Qt.PointingHandCursor)
        self.detail_btn.clicked.connect(lambda: self.switch_page(1))
        menu_layout.addWidget(self.detail_btn)
        
        menu_layout.addStretch()
        
        menu_widget.setLayout(menu_layout)
        return menu_widget
    
    def get_menu_button_style(self, is_active: bool) -> str:
        """获取菜单按钮样式"""
        if is_active:
            return """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: transparent;
                    color: #bdc3c7;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    padding: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
            """
    
    def switch_page(self, index: int) -> None:
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮样式
        if index == 0:
            self.current_page = self.keyword_page
            self.keyword_btn.setStyleSheet(self.get_menu_button_style(True))
            self.detail_btn.setStyleSheet(self.get_menu_button_style(False))
        else:
            self.current_page = self.detail_page
            self.keyword_btn.setStyleSheet(self.get_menu_button_style(False))
            self.detail_btn.setStyleSheet(self.get_menu_button_style(True))

    def center_window(self) -> None:
        """将窗口居中显示"""
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def get_window_style(self) -> str:
        """返回窗口样式表"""
        return """
            QWidget {
                background-color: #f5f7fa;
            }
        """

    def update_config_file(self, crawl_type: str, value: str) -> bool:
        """更新配置文件 """
        try:
            if crawl_type == "detail":
                # 指定帖子爬取：只更新 xhs_config.py 中的 URL 列表
                with open(self.xhs_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                pattern = r'(XHS_SPECIFIED_NOTE_URL_LIST\s*=\s*\[)(.*?)(\])'
                new_list_content = f'\n    "{value}"\n    # ........................\n'
                new_content = re.sub(pattern, r'\1' + new_list_content + r'\3', content, flags=re.DOTALL)
                with open(self.xhs_config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            elif crawl_type == "search":
                # 关键词搜索：只更新 base_config.py 中的 KEYWORDS
                with open(self.base_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 清理输入，移除引号并保持英文逗号分隔
                sanitized_value = value.replace('"', '').replace("'", '').strip()

                pattern = r'(KEYWORDS\s*=\s*")(.*?)(")'
                if re.search(pattern, content):
                    new_content = re.sub(
                        pattern,
                        rf'\1{sanitized_value}\3',
                        content,
                        count=1,
                    )
                else:
                    raise ValueError("在 base_config.py 中未找到 KEYWORDS 配置项")

                with open(self.base_config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                return False
            
            return True
        except Exception as e:
            if self.current_page:
                self.current_page.status_label.setText(f"❌ 更新配置失敗：{str(e)}")
                self.current_page.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            return False

    def on_process_output(self) -> None:
        """处理进程标准输出"""
        if not self.current_page:
            return
        output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        if output:
            self.current_page.output_text.moveCursor(self.current_page.output_text.textCursor().End)
            self.current_page.output_text.insertPlainText(output)
            scrollbar = self.current_page.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_process_error(self) -> None:
        """处理进程错误输出"""
        if not self.current_page:
            return
        error = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
        if error:
            self.current_page.output_text.moveCursor(self.current_page.output_text.textCursor().End)
            self.current_page.output_text.insertHtml(f"<span style='color: #e74c3c;'>{error}</span>")
            scrollbar = self.current_page.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_process_finished(self, exit_code: int, exit_status: int) -> None:
        """进程执行完成"""
        if not self.current_page:
            return
        if exit_code == 0:
            self.current_page.status_label.setText("✅ 爬取完成！")
            self.current_page.status_label.setStyleSheet("color: #27ae60; font-size: 11px; padding: 8px;")
        else:
            self.current_page.status_label.setText("❌ 爬取過程中出現錯誤，請查看輸出")
            self.current_page.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
        
        # 恢复按钮状态
        if isinstance(self.current_page, DetailPage):
            self.current_page.start_button.setEnabled(True)
            self.current_page.start_button.setText("開始爬取")
            self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())
        elif isinstance(self.current_page, KeywordSearchPage):
            self.current_page.start_button.setEnabled(True)
            self.current_page.start_button.setText("開始爬取")
            self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())

    def start_crawler(self, crawl_type: str, value: str) -> None:
        """启动爬虫"""
        if not self.current_page:
            return
        
        if not value:
            if crawl_type == "detail":
                self.current_page.status_label.setText("❌ 請先輸入鏈接")
            else:
                self.current_page.status_label.setText("❌ 請先輸入關鍵詞")
            self.current_page.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            return

        # 如果进程正在运行，则停止
        if self.process.state() == QProcess.Running:
            self.current_page.status_label.setText("⏹️ 正在停止爬蟲...")
            self.current_page.status_label.setStyleSheet("color: #f39c12; font-size: 11px; padding: 8px;")
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
                self.process.waitForFinished(1000)
            if isinstance(self.current_page, DetailPage):
                self.current_page.start_button.setEnabled(True)
                self.current_page.start_button.setText("開始爬取")
                self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())
            elif isinstance(self.current_page, KeywordSearchPage):
                self.current_page.start_button.setEnabled(True)
                self.current_page.start_button.setText("開始爬取")
                self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())
            self.current_page.status_label.setText("⏹️ 已停止")
            self.current_page.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 8px;")
            return

        # 更新配置文件
        if not self.update_config_file(crawl_type, value):
            return

        # 清空输出
        self.current_page.output_text.clear()
        self.current_page.output_text.show()

        # 更新状态
        self.current_page.status_label.setText("⏳ 正在更新配置並啟動爬蟲...")
        self.current_page.status_label.setStyleSheet("color: #f39c12; font-size: 11px; padding: 8px;")
        
        # 更新按钮
        running_style = """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        if isinstance(self.current_page, DetailPage):
            self.current_page.start_button.setEnabled(True)
            self.current_page.start_button.setText("運行中... (點擊停止)")
            self.current_page.start_button.setStyleSheet(running_style)
        elif isinstance(self.current_page, KeywordSearchPage):
            self.current_page.start_button.setEnabled(True)
            self.current_page.start_button.setText("運行中... (點擊停止)")
            self.current_page.start_button.setStyleSheet(running_style)

        # 设置工作目录为项目根目录
        self.process.setWorkingDirectory(str(self.project_root))

        # 执行命令
        if crawl_type == "detail":
            self.process.start("uv", ["run", "main.py", "--platform", "xhs", "--lt", "qrcode", "--type", "detail"])
        else:
            self.process.start("uv", ["run", "main.py", "--platform", "xhs", "--lt", "qrcode", "--type", "search"])

        # 检查进程是否成功启动
        if not self.process.waitForStarted(3000):
            self.current_page.status_label.setText("❌ 無法啟動爬蟲進程，請確保已安裝 uv")
            self.current_page.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            if isinstance(self.current_page, DetailPage):
                self.current_page.start_button.setEnabled(True)
                self.current_page.start_button.setText("開始爬取")
                self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())
            elif isinstance(self.current_page, KeywordSearchPage):
                self.current_page.start_button.setEnabled(True)
                self.current_page.start_button.setText("開始爬取")
                self.current_page.start_button.setStyleSheet(self.current_page.get_button_style())
            self.current_page.output_text.hide()
            return

        self.current_page.status_label.setStyleSheet("color: #3498db; font-size: 11px; padding: 8px;")


def main() -> None:
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

