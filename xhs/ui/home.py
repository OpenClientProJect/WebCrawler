import re
import sys
from pathlib import Path

from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HomeWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("小紅書 - 評論信息爬取")
        self.setMinimumSize(600, 450)
        self.resize(700, 550)
        
        # 居中显示窗口
        self.center_window()
        
        # 设置样式
        self.setStyleSheet(self.get_window_style())

        # 创建标题标签
        title_label = QLabel("評論信息爬取")
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
        self.url_input.setPlaceholderText("请输入要抓取的链接")
        self.url_input.setStyleSheet(self.get_input_style())
        self.url_input.setMinimumHeight(40)
        
        # 回车键触发开始按钮
        self.url_input.returnPressed.connect(self.on_start_clicked)

        # 创建开始按钮
        self.start_button = QPushButton("开始爬取")
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
        self.output_text.hide()  # 初始隐藏

        # 创建进程对象
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.on_process_output)
        self.process.readyReadStandardError.connect(self.on_process_error)
        self.process.finished.connect(self.on_process_finished)

        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.absolute()
        self.config_path = self.project_root / "config" / "xhs_config.py"

        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 25, 30, 25)
        
        main_layout.addWidget(title_label)
        main_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        main_layout.addWidget(url_label)
        main_layout.addWidget(self.url_input)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.output_text)
        main_layout.addStretch()

        self.setLayout(main_layout)

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

    def get_input_style(self) -> str:
        """返回输入框样式表"""
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
        """返回按钮样式表"""
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

    def update_config_file(self, url: str) -> bool:
        """更新配置文件中的 XHS_SPECIFIED_NOTE_URL_LIST"""
        try:
            # 读取配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式替换 URL 列表
            # 匹配 XHS_SPECIFIED_NOTE_URL_LIST = [...] 部分
            pattern = r'(XHS_SPECIFIED_NOTE_URL_LIST\s*=\s*\[)(.*?)(\])'
            
            # 构建新的列表内容
            new_list_content = f'\n    "{url}"\n    # ........................\n'
            
            # 替换
            new_content = re.sub(pattern, r'\1' + new_list_content + r'\3', content, flags=re.DOTALL)
            
            # 写回文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        except Exception as e:
            self.status_label.setText(f"❌ 更新配置失败：{str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            return False

    def on_process_output(self) -> None:
        """处理进程标准输出"""
        output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        if output:
            # 使用纯文本追加，HTML格式可能导致问题
            self.output_text.moveCursor(self.output_text.textCursor().End)
            self.output_text.insertPlainText(output)
            # 自动滚动到底部
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_process_error(self) -> None:
        """处理进程错误输出"""
        error = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
        if error:
            # 使用HTML格式显示错误（红色）
            self.output_text.moveCursor(self.output_text.textCursor().End)
            self.output_text.insertHtml(f"<span style='color: #e74c3c;'>{error}</span>")
            # 自动滚动到底部
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_process_finished(self, exit_code: int, exit_status: int) -> None:
        """进程执行完成"""
        if exit_code == 0:
            self.status_label.setText("✅ 爬取完成！")
            self.status_label.setStyleSheet("color: #27ae60; font-size: 11px; padding: 8px;")
            self.start_button.setEnabled(True)
            self.start_button.setText("开始爬取")
            self.start_button.setStyleSheet(self.get_button_style())
        else:
            self.status_label.setText("❌ 爬取过程中出现错误，请查看输出")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            self.start_button.setEnabled(True)
            self.start_button.setText("开始爬取")
            self.start_button.setStyleSheet(self.get_button_style())

    def on_start_clicked(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("❌ 请先输入链接")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            return

        # 如果进程正在运行，则停止
        if self.process.state() == QProcess.Running:
            self.status_label.setText("⏹️ 正在停止爬虫...")
            self.status_label.setStyleSheet("color: #f39c12; font-size: 11px; padding: 8px;")
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
                self.process.waitForFinished(1000)
            self.start_button.setEnabled(True)
            self.start_button.setText("开始爬取")
            self.start_button.setStyleSheet(self.get_button_style())
            self.status_label.setText("⏹️ 已停止")
            self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 8px;")
            return

        # 更新配置文件
        if not self.update_config_file(url):
            return

        # 清空输出
        self.output_text.clear()
        self.output_text.show()

        # 更新状态
        self.status_label.setText("⏳ 正在更新配置并启动爬虫...")
        self.status_label.setStyleSheet("color: #f39c12; font-size: 11px; padding: 8px;")
        self.start_button.setEnabled(True)
        self.start_button.setText("运行中... (点击停止)")
        self.start_button.setStyleSheet("""
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
        """)

        # 设置工作目录为项目根目录
        self.process.setWorkingDirectory(str(self.project_root))

        # 执行命令
        self.process.start("uv", ["run", "main.py", "--platform", "xhs", "--lt", "qrcode", "--type", "detail"])

        # 检查进程是否成功启动
        if not self.process.waitForStarted(3000):
            self.status_label.setText("❌ 无法启动爬虫进程，请确保已安装 uv")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 8px;")
            self.start_button.setEnabled(True)
            self.start_button.setText("开始爬取")
            self.start_button.setStyleSheet(self.get_button_style())
            self.output_text.hide()
            return

        self.status_label.setStyleSheet("color: #3498db; font-size: 11px; padding: 8px;")


def main() -> None:
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

