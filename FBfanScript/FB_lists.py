import asyncio
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QMessageBox, QScrollArea,
                             QSizePolicy, QGridLayout, QMenu, QInputDialog, QDialog)
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint, QEventLoop
from PyQt5.QtGui import QDrag, QColor, QFont, QPalette, QCursor, QPainter, QIcon, QPen
from PyQt5 import QtCore
from qasync import asyncSlot


def resource_path(relative_path):
    """ 获取资源的绝对路径（兼容开发环境和PyInstaller打包环境） """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DraggableLabel(QLabel):
    def __init__(self, index, color, text, parent=None, draggable=True):
        super().__init__(text, parent)
        icon_path = resource_path("FBmie.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.index = index
        self.draggable = draggable
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 12px;
            font-weight: bold;
            font-size: 14px;
            color: white;
            margin: 5px;
            border: none;
            /* 磨砂玻璃效果阴影 */
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18),
                        0 4px 8px rgba(0, 0, 0, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.4);
            /* 背景模糊效果（如果支持） */
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: all 0.4s ease;
        """)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # 添加鼠标悬停效果
    def enterEvent(self, event):
        if self.draggable:
            self.setStyleSheet(f"""
                background-color: {self.getDarkerColor()}; 
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin: 5px;
                border: none;
                /* 悬停时阴影更明显 */
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25), 
                            0 8px 25px rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
                transition: all 0.3s ease;
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.draggable:
            self.setStyleSheet(f"""
                background-color: {self.getOriginalColor()}; 
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                color: white;
                margin: 5px;
                border: none;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2), 
                            0 6px 20px rgba(0, 0, 0, 0.15);
                transform: translateY(0);
                transition: all 0.3s ease;
            """)
        super().leaveEvent(event)

    def getDarkerColor(self):
        """获取更深的颜色用于悬停效果"""
        colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
        original_color = colors[self.index]
        # 简单的颜色变暗处理
        if original_color.startswith('#'):
            r = int(original_color[1:3], 16)
            g = int(original_color[3:5], 16)
            b = int(original_color[5:7], 16)
            r = max(0, r - 20)
            g = max(0, g - 20)
            b = max(0, b - 20)
            return f"#{r:02x}{g:02x}{b:02x}"
        return original_color

    def getOriginalColor(self):
        """获取原始颜色"""
        colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
        return colors[self.index]

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not self.draggable or not (event.buttons() & Qt.LeftButton):
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimedata = QMimeData()

        # 将索引数据编码为字节流
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        stream.writeInt(self.index)
        # 添加标签文本信息
        stream.writeQString(self.text())
        # 添加标签来源信息（是否来自内部）
        stream.writeBool(hasattr(self, 'is_internal') and self.is_internal)

        mimedata.setData("application/x-draggable-label", byte_array)
        drag.setMimeData(mimedata)

        # 设置拖动时的预览图像
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # 开始拖动操作
        drag.exec_(Qt.MoveAction)


class DropArea(QFrame):
    orderChanged = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = resource_path("FBmie.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setStyleSheet("""
            DropArea {
                background-color: #ffffff;  /* 改为白色背景 */
                margin: 5px;
                border: none;  /* 移除外层边框 */
                border-radius: 10px;
            }
        """)
        self.setMinimumSize(200, 400)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;  /* 改为白色背景 */
                border: none;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # 创建容器widget - 在这里添加虚线边框
        self.container = QWidget()
        self.container.setStyleSheet("""
            background-color: #ffffff;  /* 改为白色背景 */
            border: 2px dashed #d8deff;  /* 在内层容器添加虚线边框 */
            border-radius: 10px;
        """)
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # 修改为左上对齐
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.scroll_area.setWidget(self.container)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)

        # 创建包含"新增區域"标签和"清空任務"按钮的容器
        bottom_container = QWidget()
        bottom_container.setStyleSheet("background-color: #ffffff;")
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # 美化"添加区域"标签
        self.add_area_label = QLabel("新增區域")
        self.add_area_label.setAlignment(Qt.AlignCenter)
        self.add_area_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: transparent;
            }
        """)
        self.add_area_label.setFont(QFont("微軟雅黑", 10))
        # bottom_layout.addWidget(self.add_area_label)
        bottom_layout.addStretch(1)
        # 添加弹性空间使元素居中
        bottom_layout.addStretch(1)

        main_layout.addWidget(bottom_container)

        self.setLayout(main_layout)

        self.labels = []
        self.replace_mode = False  # 默认为添加模式
        self.drag_source_index = -1  # 记录拖动源的索引
        self.drag_in_progress = False  # 标记拖动是否在进行中

    def setReplaceMode(self, mode):
        self.replace_mode = mode

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-draggable-label"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-draggable-label"):
            # 在拖动过程中绘制可视化反馈
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red if self.replace_mode else Qt.green, 2, Qt.DashLine))
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
            painter.end()

            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        # 当拖动离开区域时，标记为拖动中
        self.drag_in_progress = True
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-draggable-label"):
            # 从MIME数据中读取索引和文本
            byte_array = event.mimeData().data("application/x-draggable-label")
            stream = QDataStream(byte_array, QIODevice.ReadOnly)
            index = stream.readInt()
            text = stream.readQString()
            is_internal = stream.readBool()  # 读取是否来自内部

            # 获取鼠标位置
            pos = event.pos()
            global_pos = self.mapToGlobal(pos)
            container_pos = self.container.mapFromGlobal(global_pos)

            # 检查是否要替换现有标签
            if self.replace_mode:
                # 替换模式：找到鼠标位置下的标签并替换它
                for i, label in enumerate(self.labels):
                    if label.geometry().contains(container_pos):
                        # 移除现有标签
                        self.layout.removeWidget(label)
                        label.deleteLater()
                        self.labels.pop(i)

                        # 创建新标签并添加到相同位置
                        colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
                        texts = ["關鍵字任務", "搜尋添加好友", "社團邀請好友", "粉轉邀請好友", "用戶留言", "休息時間"]
                        new_label = DraggableLabel(index, colors[index], texts[index], draggable=True)
                        new_label.is_internal = True  # 标记为内部标签

                        # 如果是休息时间任务，弹出输入框获取休息时间
                        if index == 5:  # 休息时间任务的索引为5
                            rest_time, ok = self.getRestTime()
                            if ok:
                                new_label.rest_time = rest_time
                            else:
                                new_label.rest_time = 60  # 默认60秒
                        # 为其他任务添加完成时间输入框
                        elif index in [0, 1, 2, 3, 4]:  # 其他任务
                            completion_time, ok = self.getCompletionTime(index, texts[index])
                            if ok:
                                new_label.completion_time = completion_time
                            else:
                                new_label.completion_time = 1800  # 默认30分钟（1800秒）
                        new_label.setContextMenuPolicy(Qt.CustomContextMenu)
                        new_label.customContextMenuRequested.connect(
                            lambda pos, label=new_label: self.showContextMenu(pos, label))

                        self.layout.insertWidget(i, new_label)
                        self.labels.insert(i, new_label)

                        event.acceptProposedAction()
                        self.emitOrder()
                        return

            # 添加模式：检查是否拖到了其他标签上
            target_index = -1
            for i, label in enumerate(self.labels):
                if label.geometry().contains(container_pos):
                    target_index = i
                    break

            if target_index >= 0:
                # 如果拖到了其他标签上，交换位置
                if is_internal:
                    # 内部拖动：交换两个标签的位置
                    source_index = -1
                    for i, label in enumerate(self.labels):
                        if label.index == index:
                            source_index = i
                            break

                    if source_index >= 0:
                        # 交换标签位置
                        self.swapLabels(source_index, target_index)
                else:
                    # 外部拖动：插入新标签并移除目标标签
                    colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
                    texts = ["關鍵字任務", "搜尋添加好友", "社團邀請好友", "粉轉邀請好友", "用戶留言", "休息時間"]

                    # 移除目标位置的标签
                    target_label = self.labels[target_index]
                    self.layout.removeWidget(target_label)
                    target_label.deleteLater()
                    self.labels.pop(target_index)

                    # 创建新标签并插入到目标位置
                    new_label = DraggableLabel(index, colors[index], texts[index], draggable=True)
                    new_label.is_internal = True  # 标记为内部标签

                    # 如果是休息时间任务，弹出输入框获取休息时间
                    if index == 5:  # 休息时间任务的索引为3
                        rest_time, ok = self.getRestTime()
                        if ok:
                            new_label.rest_time = rest_time
                        else:
                            new_label.rest_time = 60  # 默认60秒
                    # 为其他任务添加完成时间输入框
                    elif index in [0, 1, 2, 3, 4]:  # 其他任务
                        completion_time, ok = self.getCompletionTime(index, texts[index])
                        if ok:
                            new_label.completion_time = completion_time
                        else:
                            new_label.completion_time = 1800  # 默认30分钟（1800秒）

                    new_label.setContextMenuPolicy(Qt.CustomContextMenu)
                    new_label.customContextMenuRequested.connect(
                        lambda pos, label=new_label: self.showContextMenu(pos, label))

                    self.layout.insertWidget(target_index, new_label)
                    self.labels.insert(target_index, new_label)
            else:
                # 添加到末尾
                colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
                texts = ["關鍵字任務", "搜尋添加好友", "社團邀請好友", "粉轉邀請好友", "用戶留言", "休息時間"]
                new_label = DraggableLabel(index, colors[index], texts[index], draggable=True)
                new_label.is_internal = True  # 标记为内部标签

                # 如果是休息时间任务，弹出输入框获取休息时间
                if index == 5:  # 休息时间任务
                    rest_time, ok = self.getRestTime()
                    if ok:
                        new_label.rest_time = rest_time
                    else:
                        new_label.rest_time = 60  # 默认60秒
                # 为其他任务添加完成时间输入框
                elif index in [0, 1, 2, 3, 4]:  # 其他任务
                    completion_time, ok = self.getCompletionTime(index, texts[index])
                    if ok:
                        new_label.completion_time = completion_time
                    else:
                        new_label.completion_time = 1800  # 默认30分钟（1800秒）

                new_label.setContextMenuPolicy(Qt.CustomContextMenu)
                new_label.customContextMenuRequested.connect(
                    lambda pos, label=new_label: self.showContextMenu(pos, label))

                self.layout.addWidget(new_label)
                self.labels.append(new_label)

            event.acceptProposedAction()
            self.emitOrder()

        # 重置拖动状态
        self.drag_in_progress = False

    def getCompletionTime(self, task_index, task_name):
        """获取任务完成时间，使用自定义样式的输入对话框"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle(f"{task_name}完成時間")
        dialog.setLabelText(f"請輸入{task_name}的最大執行時間（分鐘）:\n(輸入0表示不受時間限制)1分-8時")
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setIntRange(0, 480)  # 0分钟到8小时，0表示无限制
        dialog.setIntValue(30)  # 默认30分钟

        # 设置对话框样式以匹配应用程序主题
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f8ff;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                background-color: transparent;
            }
            QSpinBox {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #3492ED;
            }
            QPushButton {
                background-color: #63b5ff;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3492ED;
            }
        """)

        result = dialog.exec_()
        if result == QDialog.Accepted:
            minutes = dialog.intValue()
            if minutes == 0:
                return 0, True  # 0表示无时间限制
            else:
                return minutes * 60, True  # 转换为秒
        return 1800, False  # 默认30分钟

    def getRestTime(self):
        """获取休息时间，使用自定义样式的输入对话框"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("休息時間")
        dialog.setLabelText("請輸入休息時間（秒）:\n1秒-1時")
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setIntRange(1, 3600)
        dialog.setIntValue(60)

        # 设置对话框样式以匹配应用程序主题
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f8ff;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                background-color: transparent;
            }
            QSpinBox {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #3492ED;
            }
            QPushButton {
                background-color: #63b5ff;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3492ED;
            }
        """)

        result = dialog.exec_()
        if result == QDialog.Accepted:
            return dialog.intValue(), True
        return 60, False

    def swapLabels(self, index1, index2):
        """交换两个标签的位置"""
        if index1 == index2:
            return

        # 获取两个标签
        label1 = self.labels[index1]
        label2 = self.labels[index2]

        # 从布局中移除
        self.layout.removeWidget(label1)
        self.layout.removeWidget(label2)

        # 交换位置重新插入
        if index1 < index2:
            self.layout.insertWidget(index1, label2)
            self.layout.insertWidget(index2, label1)
        else:
            self.layout.insertWidget(index2, label1)
            self.layout.insertWidget(index1, label2)

        # 更新标签列表
        self.labels[index1], self.labels[index2] = self.labels[index2], self.labels[index1]

        # 发射顺序改变信号
        self.emitOrder()

    def showContextMenu(self, pos, label):
        # 创建右键菜单
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #f5f8ff;
                color: #333333;
                border: 1px solid #f5f8ff;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
        """)
        delete_action = menu.addAction("刪除")
        move_up_action = menu.addAction("上移")
        move_down_action = menu.addAction("下移")

        # 显示菜单并等待用户选择
        action = menu.exec_(label.mapToGlobal(pos))

        if action == delete_action:
            self.removeLabel(label)
        elif action == move_up_action:
            self.moveLabelUp(label)
        elif action == move_down_action:
            self.moveLabelDown(label)

    def removeLabel(self, label):
        self.layout.removeWidget(label)
        label.deleteLater()
        self.labels.remove(label)
        self.emitOrder()

    def moveLabelUp(self, label):
        index = self.layout.indexOf(label)
        if index > 0:
            self.swapLabels(index, index - 1)

    def moveLabelDown(self, label):
        index = self.layout.indexOf(label)
        if index < self.layout.count() - 1:
            self.swapLabels(index, index + 1)

    def emitOrder(self):
        # 获取当前顺序
        order = []
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget():
                order.append(item.widget().index)
        self.orderChanged.emit(order)


class TaskOrderWindow(QDialog):
    # order_saved = QtCore.pyqtSignal(list)

    def __init__(self, config=None, parent=None):  # 添加 config 参数
        super().__init__(parent)
        icon_path = resource_path("FBmie.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("任務順序設置")
        self.setFixedSize(800, 550)
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.config = config or {}  # 存储配置
        self.initUI()
        self.center()
        self.accept_order = []
        self.result = None  # 用于存储结果

    def initUI(self):
        # 设置窗口背景颜色
        self.setStyleSheet("background-color: #e2dbff; color: white;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建自定义标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            background-color: #eff4ff; 
            border-top-left-radius: 5px; 
            border-top-right-radius: 5px;
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 5, 0)

        self.title_label = QLabel("任務執行順序")
        self.title_label.setStyleSheet("color: black;")  # 改为黑色字体
        self.title_label.setFont(QFont("微軟雅黑", 10, QFont.Bold))
        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch(1)

        # 添加最小化按钮
        min_button = QPushButton("−")
        min_button.setFixedSize(20, 20)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: green;
                border-radius: 10px;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(min_button)

        # 添加关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: red;
                border-radius: 10px;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        # 内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧放置区域
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 0, 0)

        # 放置区域 - 现在DropArea内部已经包含了清空按钮
        self.drop_area = DropArea()
        # 连接清空按钮的点击事件
        self.drop_area.clear_btn.clicked.connect(self.clearAll)
        left_panel.addWidget(self.drop_area)

        content_layout.addLayout(left_panel, 2)  # 2/3的空间

        # 右侧可拖拽标签区域
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #e2dbff;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        label = QLabel("拖拽任務到左側區域:")
        label.setStyleSheet("color: blue;font-size: 13px;")  # 改为蓝色字体
        label.setFont(QFont("微軟雅黑", 12))
        label.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(label)

        # 创建4个可拖拽的标签，但根据配置决定是否显示
        colors = ["#9ee6ef", "#b4ddb6", "#6A5ACD", "#DDA0DD", "#f598b7", "#ffd598"]
        texts = ["關鍵字任務", "搜尋添加好友", "社團邀請好友", "粉轉邀請好友", "用戶留言", "休息時間"]

        # 根据配置决定哪些标签应该显示
        show_labels = [True, True, True, True, True, True]  # 默认全部显示

        if self.config:
            show_labels[0] = self.config.get("Key_IsEnableKey", False)
            show_labels[1] = self.config.get("key_IsKeyfriend", False)
            show_labels[2] = self.config.get("Groupkey_join", False)
            show_labels[3] = self.config.get("Fanskey_join", False)
            show_labels[4] = self.config.get("User_IsEnableBrowse", False)
            # 索引5（休息时间）始终为True，不需要设置

            # 动态计算位置
            visible_count = sum(show_labels)
            rows = 2
            cols = 2

            # 如果需要显示的元素数量少于4个，调整网格大小
            if visible_count <= 2:
                rows = 2
                cols = 1
            elif visible_count == 3:
                rows = 2
                cols = 2

            # 创建网格布局
            grid_layout = QGridLayout()
            grid_layout.setSpacing(10)

            # 放置可见的标签
            row, col = 0, 0
            for i in range(6):
                if show_labels[i]:
                    display_text = texts[i]
                    tooltip_text = ""

                    # 为用户留言标签设置工具提示
                    if i == 0 and self.config:  # 關鍵字留言
                        tooltip_parts = []
                        if self.config.get("IsFbPages", False):
                            tooltip_parts.append("FB貼文")
                        if self.config.get("IsGroupPages", False):
                            tooltip_parts.append("社團貼文")

                        if tooltip_parts:
                            tooltip_text = "關鍵字类型: " + " | ".join(tooltip_parts)

                    # 为用户留言标签设置工具提示
                    if i == 4 and self.config:  # 用户留言
                        tooltip_parts = []
                        if self.config.get("IsGroupMem", False):
                            tooltip_parts.append("社團成員留言")
                        if self.config.get("IsPagesMem", False):
                            tooltip_parts.append("粉轉成員留言")
                        if self.config.get("IsAdMem", False):
                            tooltip_parts.append("讃客成員留言")

                        if tooltip_parts:
                            tooltip_text = "留言類型: " + " | ".join(tooltip_parts)

                    draggable_label = DraggableLabel(i, colors[i], display_text, draggable=True)

                    # 设置工具提示
                    if tooltip_text:
                        draggable_label.setToolTip(tooltip_text)
                        # 可选：在文本后面添加小图标或符号表示有详细信息
                        draggable_label.setText(display_text + "🔔")

                    grid_layout.addWidget(draggable_label, row, col)

                    # 更新位置
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1

            right_layout.addLayout(grid_layout)
        right_layout.addStretch()

        # 保存按钮 - 修改为左对齐且宽度适应内容
        save_btn_container = QWidget()
        save_btn_layout = QHBoxLayout(save_btn_container)
        save_btn_layout.setContentsMargins(0, 0, 0, 0)

        save_btn = QPushButton("保存順序")
        save_btn.setFixedWidth(save_btn.fontMetrics().width("保存順序") + 20)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #63b5ff;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3492ED;
            }
        """)
        save_btn.clicked.connect(self.saveOrder)
        
        # 添加清空按钮
        self.clear_btn = QPushButton("清空任務")
        self.clear_btn.setFixedWidth(self.clear_btn.fontMetrics().width("清空任務") + 20)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ee5253;
            }
        """)
        self.clear_btn.clicked.connect(self.clearAll)
        
        save_btn_layout.addWidget(save_btn)
        save_btn_layout.addWidget(self.clear_btn)
        
        # 添加操作指南文本
        guide_text = QLabel(
            "操作指南:\n"
            "1. 拖拽右側任務到左側清空按鈕兩側\n"
            "2. 右鍵點擊可以刪除或移動\n"
            "3. 拖拽回右側空白処刪除\n"
            "4. 拖拽到左側相應任務的可以覆蓋\n"
            "5. 在左側區域內拖拽任務可以交換位置"
        )
        guide_text.setAlignment(Qt.AlignLeft)
        guide_text.setStyleSheet("""
            QLabel {
                color: #99989e;
                font-size: 12px;
                background-color: #f5f0ff;
                padding: 5px;
                border: 1px solid #f5f0ff;
                border-radius: 5px;

            }
        """)
        guide_text.setWordWrap(True)  # 允许文本换行
        right_layout.addWidget(guide_text)
        right_layout.addWidget(save_btn_container)
        content_layout.addWidget(right_panel, 1)  # 1/3的空间

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        # 连接顺序改变信号
        self.drop_area.orderChanged.connect(self.onOrderChanged)

        self.current_order = []

        # 设置窗口接受拖放事件
        self.setAcceptDrops(True)

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

    # 必须实现的拖动窗口的方法
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def dragEnterEvent(self, event):
        # 接受所有拖拽事件
        event.acceptProposedAction()

    def dropEvent(self, event):
        # 如果拖拽到窗口的其他区域（非DropArea），则删除标签
        if event.mimeData().hasFormat("application/x-draggable-label"):
            # 获取鼠标位置
            pos = event.pos()
            # 检查是否在DropArea内
            drop_area_pos = self.drop_area.mapFromGlobal(self.mapToGlobal(pos))
            if not self.drop_area.rect().contains(drop_area_pos):
                # 不在DropArea内，删除标签
                byte_array = event.mimeData().data("application/x-draggable-label")
                stream = QDataStream(byte_array, QIODevice.ReadOnly)
                index = stream.readInt()
                text = stream.readQString()

                # 查找并删除对应的标签
                for label in self.drop_area.labels[:]:
                    if label.index == index:
                        self.drop_area.removeLabel(label)
                        break

                event.acceptProposedAction()
            else:
                # 在DropArea内，让DropArea处理
                event.ignore()

    def setAddMode(self):
        self.add_mode_btn.setChecked(True)
        self.replace_mode_btn.setChecked(False)
        self.drop_area.setReplaceMode(False)

    def setReplaceMode(self):
        self.add_mode_btn.setChecked(False)
        self.replace_mode_btn.setChecked(True)
        self.drop_area.setReplaceMode(True)

    def clearAll(self):
        for label in self.drop_area.labels[:]:
            self.drop_area.removeLabel(label)

    def onOrderChanged(self, order):
        self.current_order = order
        print("当前顺序:", order)

    # 在 TaskOrderWindow 类的 saveOrder 方法中添加启动时间设置
    def saveOrder(self):
        if not self.current_order:
            QMessageBox.warning(self, "警告", "請先添加任務到左側!")
            return

        # 弹出启动时间设置对话框
        dialog = QInputDialog(self)
        dialog.setWindowTitle("設置啟動時間")
        dialog.setLabelText("請輸入每日啟動時間（24小時制，格式 HH:MM）:\n輸入 0 表示立即運行")
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setTextValue("09:00")  # 默认9点

        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f8ff;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                background-color: transparent;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #63b5ff;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3492ED;
            }
        """)

        result = dialog.exec_()
        scheduled_time = "0"  # 默认立即运行

        if result == QDialog.Accepted:
            scheduled_time = dialog.textValue().strip()
            # 验证时间格式
            if scheduled_time != "0":
                import re
                if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', scheduled_time):
                    QMessageBox.warning(self, "輸入錯誤", "時間格式不正確，請使用 HH:MM 格式（如 09:00）")
                    return

        # 收集所有任务的配置
        rest_times = {}
        completion_times = {}

        for i, label in enumerate(self.drop_area.labels):
            if hasattr(label, 'rest_time'):
                rest_times[i] = label.rest_time
            if hasattr(label, 'completion_time'):
                completion_times[i] = label.completion_time

        self.accept_order = {
            'order': self.current_order,
            'rest_times': rest_times,
            'completion_times': completion_times,
            'scheduled_time': scheduled_time  # 添加计划时间
        }

        print(f"保存顺序: {self.accept_order}")
        self.hide()

    def closeEvent(self, event):
        # 如果你想在用户直接关闭窗口时返回特定值，可以在这里设置
        # 例如，设置 self.accept_order 为 None
        self.accept_order = None
        self.reject()  # 确保返回 Rejected
        event.accept()


def show_task_order_window_async(config=None):
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
    app.setFont(QFont("Arial", 10))

    dialog = TaskOrderWindow(config=config)
    dialog.exec_()  # 模态显示，并获取结果

    return dialog.accept_order
