import sys
import os
import re
import math

from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QFileDialog, QFrame,
                           QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QGridLayout, QGroupBox,
                           QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
                           QSplitter, QStatusBar, QStyleFactory, QTabWidget, QTextEdit,
                           QVBoxLayout, QWidget)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QLinearGradient, QPainter,
                       QPainterPath, QPalette, QPen, QSyntaxHighlighter, QTextCharFormat,
                       QPixmap)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize

from translator import translate_to_quadruples, LanguageType  # 导入翻译函数和语言类型枚举

# 语法高亮类
class ForLoopHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language_type=LanguageType.PSEUDO):
        super().__init__(document)
        self.language_type = language_type
        self.setup_formatting()
        
    def setup_formatting(self):
        # 设置不同的格式
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))  # 蓝色
        self.keyword_format.setFontWeight(QFont.Bold)
        
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#D4D4D4"))  # 浅灰色
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # 浅绿色
        
        self.identifier_format = QTextCharFormat()
        self.identifier_format.setForeground(QColor("#9CDCFE"))  # 浅蓝色
        
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#DCDCAA"))  # 黄色
        
        # 针对不同语言设置关键字
        self.pseudo_keywords = ["FOR", "TO", "DO", "ENDFOR"]
        self.c_keywords = ["for", "if", "while", "return", "int", "float", "double"]
        self.python_keywords = ["for", "in", "range", "if", "elif", "else", "while", "def", "return", "import", "from"]
        
    def highlightBlock(self, text):
        if not text:
            return
            
        # 根据语言类型选择相应的高亮规则
        if self.language_type == LanguageType.PSEUDO:
            self.highlight_pseudo(text)
        elif self.language_type == LanguageType.C_STYLE:
            self.highlight_c(text)
        elif self.language_type == LanguageType.PYTHON:
            self.highlight_python(text)
            
    def highlight_pseudo(self, text):
        # 高亮伪代码关键字
        for keyword in self.pseudo_keywords:
            start = 0
            while start >= 0:
                start = text.upper().find(keyword, start)
                if start >= 0:
                    length = len(keyword)
                    self.setFormat(start, length, self.keyword_format)
                    start += length
                    
        # 高亮操作符
        for op in [":=", "+", "-", "*", "/"]:
            start = 0
            while start >= 0:
                start = text.find(op, start)
                if start >= 0:
                    self.setFormat(start, len(op), self.operator_format)
                    start += len(op)
                    
        # 高亮数字
        for match in re.finditer(r'\b\d+\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
            
    def highlight_c(self, text):
        # 高亮C风格关键字
        for keyword in self.c_keywords:
            start = 0
            while start >= 0:
                start = text.find(keyword, start)
                if start >= 0 and (start == 0 or not text[start-1].isalnum()):
                    if start + len(keyword) == len(text) or not text[start + len(keyword)].isalnum():
                        self.setFormat(start, len(keyword), self.keyword_format)
                    start += len(keyword)
                else:
                    if start >= 0:
                        start += 1
                    
        # 高亮操作符
        for op in ["=", "+", "-", "*", "/", "++", "--", "+=", "-=", "*=", "/=", "==", "!=", "<", ">", "<=", ">=", ";", "{", "}"]:
            start = 0
            while start >= 0:
                start = text.find(op, start)
                if start >= 0:
                    self.setFormat(start, len(op), self.operator_format)
                    start += len(op)
                    
        # 高亮数字
        for match in re.finditer(r'\b\d+\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
            
    def highlight_python(self, text):
        # 高亮Python关键字
        for keyword in self.python_keywords:
            start = 0
            while start >= 0:
                start = text.find(keyword, start)
                if start >= 0 and (start == 0 or not text[start-1].isalnum()):
                    if start + len(keyword) == len(text) or not text[start + len(keyword)].isalnum():
                        self.setFormat(start, len(keyword), self.keyword_format)
                    start += len(keyword)
                else:
                    if start >= 0:
                        start += 1
        
        # 高亮range函数
        start = 0
        while start >= 0:
            start = text.find("range", start)
            if start >= 0 and (start == 0 or not text[start-1].isalnum()):
                if start + 5 == len(text) or not text[start + 5].isalnum():
                    self.setFormat(start, 5, self.function_format)
                start += 5
            else:
                if start >= 0:
                    start += 1
                    
        # 高亮操作符
        for op in ["=", "+", "-", "*", "/", ":", "(", ")", ",", "==", "!=", "<", ">", "<=", ">="]:
            start = 0
            while start >= 0:
                start = text.find(op, start)
                if start >= 0:
                    self.setFormat(start, len(op), self.operator_format)
                    start += len(op)
                    
        # 高亮数字
        for match in re.finditer(r'\b\d+\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)

# 四元式图形可视化类
class QuadrupleVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.quadruples = []
        self.setMinimumHeight(200)
        self.node_width = 180
        self.node_height = 36
        self.horizontal_spacing = 80
        self.vertical_spacing = 50
        self.margin = 50
        self.nodes = []
        self.edges = []
        
        # 设置背景色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f5f5"))
        self.setPalette(palette)

    def set_quadruples(self, quadruples):
        self.quadruples = quadruples
        self.calculate_layout()
        self.update()

    def calculate_layout(self):
        if not self.quadruples:
            return

        self.nodes = []
        self.edges = []
        
        # 标签到索引的映射
        labels = {}
        jump_ops = {'JMP', 'JZ', 'J>', 'J<', 'J>=', 'J<=', 'J==', 'J!='}
        
        # 识别所有标签
        for i, quad in enumerate(self.quadruples):
            op = quad.op
            if op.lower() == 'label':
                label = quad.result
                if label:
                    labels[label] = i
        
        # 简单垂直布局 - 每个节点一行
        for i, quad in enumerate(self.quadruples):
            # 垂直排列，固定x坐标，y坐标递增
            x = self.margin + self.node_width/2
            y = self.margin + i * (self.node_height + self.vertical_spacing)
            
            # 创建节点
            node_rect = QRectF(x, y, self.node_width, self.node_height)
            self.nodes.append((node_rect, quad, i))
            
            # 创建常规流边（除了跳转指令）
            if i + 1 < len(self.quadruples) and quad.op not in jump_ops:
                self.edges.append(('flow', i, i + 1))
            
            # 创建跳转边
            if quad.op in jump_ops and quad.result in labels:
                target = labels[quad.result]
                edge_type = 'back' if target < i else 'jump'
                self.edges.append((edge_type, i, target))
        
        # 计算画布所需大小
        width = int(self.margin * 2 + self.node_width * 2)  # 固定宽度
        height = int(self.margin * 2 + len(self.quadruples) * (self.node_height + self.vertical_spacing))
        
        # 确保有最小尺寸
        width = max(width, 600)  
        height = max(height, 400)
        
        self.setMinimumSize(width, height)

    def paintEvent(self, event):
        if not self.nodes:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 先绘制所有边线，这样它们会显示在节点下面
        for edge_type, from_idx, to_idx in self.edges:
            from_rect = self.nodes[from_idx][0]
            to_rect = self.nodes[to_idx][0]
            
            if edge_type == 'flow':
                self.draw_flow_edge(painter, from_rect, to_rect)
            elif edge_type == 'jump':
                self.draw_jump_edge(painter, from_rect, to_rect, is_back=False)
            elif edge_type == 'back':
                self.draw_jump_edge(painter, from_rect, to_rect, is_back=True)
        
        # 然后绘制所有节点，使它们显示在边线上面
        for rect, quad, idx in self.nodes:
            self.draw_node(painter, rect, quad, idx)

    def draw_node(self, painter, rect, quad, idx):
        # 设置节点样式
        path = QPainterPath()
        
        # 根据操作类型选择不同的形状和颜色
        op = quad.op.lower()
        
        # 跳转指令：使用菱形
        if op in {'jmp', 'jz', 'j>', 'j<', 'j>=', 'j<=', 'j==', 'j!='}:
            # 创建菱形路径
            center_x = rect.center().x()
            center_y = rect.center().y()
            half_width = rect.width() / 2
            half_height = rect.height() / 2
            
            diamond_path = QPainterPath()
            diamond_path.moveTo(center_x, rect.top())
            diamond_path.lineTo(rect.right(), center_y)
            diamond_path.lineTo(center_x, rect.bottom())
            diamond_path.lineTo(rect.left(), center_y)
            diamond_path.closeSubpath()
            
            # 渐变
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#5b9bd5"))
            gradient.setColorAt(1, QColor("#4285f4"))
            
            painter.fillPath(diamond_path, gradient)
            painter.setPen(QPen(QColor("#2060A0"), 2))
            painter.drawPath(diamond_path)
            
            path = diamond_path
            
        # 标签指令：使用圆角矩形，颜色为绿色
        elif op == 'label':
            path.addRoundedRect(rect, 15, 15)
            
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#70ad47"))
            gradient.setColorAt(1, QColor("#57a639"))
            
            painter.fillPath(path, gradient)
            painter.setPen(QPen(QColor("#406020"), 2))
            painter.drawPath(path)
            
        # 赋值指令：使用特殊颜色
        elif op == ':=' or op == '=':
            path.addRoundedRect(rect, 10, 10)
            
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#9966CC"))
            gradient.setColorAt(1, QColor("#8A2BE2"))
            
            painter.fillPath(path, gradient)
            painter.setPen(QPen(QColor("#6B238E"), 2))
            painter.drawPath(path)
            
        # 算术运算：使用棕色/橙色系
        elif op in {'+', '-', '*', '/', '%'}:
            path.addRoundedRect(rect, 10, 10)
            
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#ed7d31"))
            gradient.setColorAt(1, QColor("#e67e22"))
            
            painter.fillPath(path, gradient)
            painter.setPen(QPen(QColor("#B35A00"), 2))
            painter.drawPath(path)
            
        # 其他指令
        else:
            path.addRoundedRect(rect, 10, 10)
            
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#717171"))
            gradient.setColorAt(1, QColor("#5A5A5A"))
            
            painter.fillPath(path, gradient)
            painter.setPen(QPen(QColor("#404040"), 2))
            painter.drawPath(path)
        
        # 绘制阴影效果（使用不同的阴影使效果更好）
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 20))
        shadow_path = QPainterPath(path)
        shadow_path.translate(3, 3)
        painter.drawPath(shadow_path)
        
        # 准备绘制文本
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        
        # 根据节点类型格式化文本
        if op == 'label':
            text = f"{idx}: LABEL {quad.result}"
        elif op in {'jmp', 'jz', 'j>', 'j<', 'j>=', 'j<=', 'j==', 'j!='}:
            # 跳转指令更简洁地显示
            arg_text = ''
            if quad.arg1:
                arg_text = f"({quad.arg1})"
            text = f"{idx}: {quad.op} {arg_text} → {quad.result}"
        elif op == ':=' or op == '=':
            # 赋值指令
            text = f"{idx}: {quad.result} := {quad.arg1 or ''}"
            if quad.arg2 and quad.op == ':=':
                text = f"{idx}: {quad.result} := {quad.arg1 or ''} {quad.arg2 or ''}"
        else:
            # 其他四元式
            arg1_str = quad.arg1 or '_'
            arg2_str = quad.arg2 or '_'
            result_str = quad.result or '_'
            text = f"{idx}: ({quad.op}, {arg1_str}, {arg2_str}, {result_str})"
        
        # 如果文本太长，截断显示
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        if text_width > rect.width() - 20:
            shown_text = metrics.elidedText(text, Qt.ElideRight, rect.width() - 20)
        else:
            shown_text = text
        
        # 使用白色边框使文字在任何背景下都清晰可见
        text_rect = rect.adjusted(5, 5, -5, -5)
        painter.drawText(text_rect, Qt.AlignCenter, shown_text)

    def draw_flow_edge(self, painter, from_rect, to_rect):
        # 常规流程线
        start = QPointF(from_rect.center().x(), from_rect.bottom())
        end = QPointF(to_rect.center().x(), to_rect.top())
        
        # 绘制箭头路径
        path = QPainterPath()
        path.moveTo(start)
        
        # 如果两个节点在同一列，直接连接
        if abs(from_rect.center().x() - to_rect.center().x()) < 10:
            path.lineTo(end)
        else:
            # 否则使用贝塞尔曲线
            mid_y = (start.y() + end.y()) / 2
            path.cubicTo(
                QPointF(start.x(), mid_y),
                QPointF(end.x(), mid_y),
                end
            )
        
        # 设置线条样式
        painter.setPen(QPen(QColor("#2080E0"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        # 绘制箭头
        self.draw_arrow(painter, path, end, QColor("#2080E0"))

    def draw_jump_edge(self, painter, from_rect, to_rect, is_back):
        # 跳转边使用不同颜色和弧线
        start = QPointF(from_rect.right(), from_rect.center().y())
        end = QPointF(to_rect.left(), to_rect.center().y())
        
        # 如果是向上跳转（循环）
        if to_rect.top() < from_rect.top():
            start = QPointF(from_rect.center().x(), from_rect.top())
            end = QPointF(to_rect.center().x(), to_rect.bottom())
            
            # 弯曲的路径
            path = QPainterPath()
            path.moveTo(start)
            
            # 计算控制点
            ctrl_x = (start.x() + end.x()) / 2
            ctrl_y_top = start.y() - self.vertical_spacing / 2
            ctrl_y_bottom = end.y() + self.vertical_spacing / 2
            
            # 绘制曲线
            path.cubicTo(
                QPointF(start.x(), ctrl_y_top),
                QPointF(end.x(), ctrl_y_bottom),
                end
            )
        else:
            # 如果是向下或平行跳转
            path = QPainterPath()
            path.moveTo(start)
            
            # 如果两个节点相距较远
            distance = abs(to_rect.center().x() - from_rect.center().x())
            if distance > self.node_width * 2:
                ctrl1 = QPointF(start.x() + self.horizontal_spacing/2, start.y())
                ctrl2 = QPointF(end.x() - self.horizontal_spacing/2, end.y())
                path.cubicTo(ctrl1, ctrl2, end)
            else:
                path.lineTo(end)
        
        # 设置跳转边样式
        if is_back:
            painter.setPen(QPen(QColor("#FF5722"), 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(QColor("#2080E0"), 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        # 绘制箭头
        self.draw_arrow(painter, path, end, QColor("#FF5722" if is_back else "#2080E0"))

    def draw_arrow(self, painter, path, point, color):
        # 计算箭头方向
        angle = 0
        if path.elementCount() > 1:
            # 获取路径上最后两个点以计算方向
            last_pt = path.elementAt(path.elementCount() - 1)
            prev_pt = path.elementAt(path.elementCount() - 2)
            angle = math.atan2(last_pt.y - prev_pt.y, last_pt.x - prev_pt.x)
        
        # 箭头尺寸
        arrow_size = 10
        
        # 创建箭头路径
        arrow = QPainterPath()
        arrow.moveTo(point)
        arrow.lineTo(
            point.x() - arrow_size * math.cos(angle - math.pi/6),
            point.y() - arrow_size * math.sin(angle - math.pi/6)
        )
        arrow.lineTo(
            point.x() - arrow_size * math.cos(angle + math.pi/6),
            point.y() - arrow_size * math.sin(angle + math.pi/6)
        )
        arrow.lineTo(point)
        
        # 绘制填充箭头
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawPath(arrow)

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FOR 语句翻译器")
        self.setMinimumSize(900, 700)
        
        # 设置应用风格
        self.set_app_style()
        
        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建标题
        self.create_title()
        
        # 创建配置组
        self.create_config_group()
        
        # 创建输入输出区域分割器
        self.create_input_output_area()
        
        # 创建底部按钮区域
        self.create_button_area()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
        
        # 存储生成的四元式
        self.quadruples = []
        
        # 设置默认示例代码
        self.update_example_code()
        
    def set_app_style(self):
        # 设置亮色主题，提高对比度
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create('Fusion'))
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(248, 248, 248))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        
        # 设置边框样式，提高对比度
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F8F8;
            }
            QGroupBox {
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                background-color: #F5F5F5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
            }
            QPushButton {
                background-color: #2080E0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1070D0;
            }
            QPushButton:pressed {
                background-color: #0060C0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox {
                border: 1px solid #a0a0a0;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
                color: black;
                selection-background-color: #2080E0;
                selection-color: white;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #a0a0a0;
                background-color: white;
                selection-background-color: #2080E0;
                selection-color: white;
            }
            QTextEdit {
                border: 1px solid #a0a0a0;
                border-radius: 3px;
                background-color: white;
                font-family: 'Consolas', monospace;
                selection-background-color: #2080E0;
                selection-color: white;
                color: black;
            }
            QSplitter::handle {
                background-color: #c0c0c0;
            }
            QTabWidget::pane {
                border: 1px solid #a0a0a0;
                border-radius: 3px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #404040;
                border: 1px solid #a0a0a0;
                border-bottom: none;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2080E0;
                font-weight: bold;
            }
            QLabel {
                color: #202020;
                font-weight: bold;
            }
        """)
        
    def create_title(self):
        title_label = QLabel("FOR 语句翻译器 - 支持多种风格")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2080E0; margin: 10px;")
        self.main_layout.addWidget(title_label)
        
    def create_config_group(self):
        # 创建配置组
        config_group = QGroupBox("配置选项")
        config_layout = QGridLayout()
        config_layout.setSpacing(10)
        
        # 语言选择部分
        self.language_label = QLabel("选择语言风格:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("伪代码风格", LanguageType.PSEUDO)
        self.language_combo.addItem("C语言风格", LanguageType.C_STYLE)
        self.language_combo.addItem("Python风格", LanguageType.PYTHON)
        self.language_combo.currentIndexChanged.connect(self.update_example_code)
        
        # 添加语言描述标签
        self.language_desc = QLabel("伪代码风格: FOR ... TO ... DO ... ENDFOR")
        self.language_desc.setStyleSheet("color: #999999; font-weight: normal; font-style: italic;")
        
        # 设置网格布局
        config_layout.addWidget(self.language_label, 0, 0)
        config_layout.addWidget(self.language_combo, 0, 1)
        config_layout.addWidget(self.language_desc, 1, 0, 1, 2)
        
        # 添加间隔
        spacer = QWidget()
        config_layout.addWidget(spacer, 0, 2)
        config_layout.setColumnStretch(2, 1)
        
        config_group.setLayout(config_layout)
        self.main_layout.addWidget(config_group)
        
        # 连接信号
        self.language_combo.currentIndexChanged.connect(self.update_language_desc)

    def update_language_desc(self):
        # 更新语言描述标签
        language_type = self.language_combo.currentData()
        if language_type == LanguageType.PSEUDO:
            desc = "伪代码风格: FOR ... TO ... DO ... ENDFOR"
        elif language_type == LanguageType.C_STYLE:
            desc = "C语言风格: for (初始化; 条件; 增量) { ... }"
        elif language_type == LanguageType.PYTHON:
            desc = "Python风格: for ... in range(...): ..."
        self.language_desc.setText(desc)
        
        # 更新语法高亮器
        self.highlighter.language_type = language_type
        self.highlighter.rehighlight()

    def create_input_output_area(self):
        # 创建输入输出区域分割器
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(2)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2080E0;
            }
            QSplitter::handle:hover {
                background-color: #1070D0;
            }
            QSplitter::handle:pressed {
                background-color: #0060C0;
            }
        """)
        
        # 创建输入区域
        self.create_input_area()
        
        # 创建输出区域
        self.create_output_area()
        
        # 添加分割器到主布局
        self.main_layout.addWidget(self.splitter, 1)

    def create_input_area(self):
        # 创建输入区域
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 10, 0, 0)
        
        # 添加标题栏
        input_title_layout = QHBoxLayout()
        input_label = QLabel("输入 FOR 语句:")
        input_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        # 添加示例下拉菜单
        example_label = QLabel("示例代码:")
        self.example_combo = QComboBox()
        self.example_combo.addItem("选择示例...", None)
        self.example_combo.addItem("基本循环", "basic")
        self.example_combo.addItem("嵌套循环", "nested")
        self.example_combo.addItem("复杂表达式", "complex")
        self.example_combo.currentIndexChanged.connect(self.load_selected_example)
        
        # 添加输入框
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont("Consolas", 12))
        self.input_text.setLineWrapMode(QTextEdit.NoWrap)
        self.input_text.setMinimumHeight(150)
        
        # 创建语法高亮器
        self.highlighter = ForLoopHighlighter(self.input_text.document())
        
        input_title_layout.addWidget(input_label)
        input_title_layout.addStretch()
        input_title_layout.addWidget(example_label)
        input_title_layout.addWidget(self.example_combo)
        
        input_layout.addLayout(input_title_layout)
        input_layout.addWidget(self.input_text)
        
        # 添加到分割器
        self.splitter.addWidget(input_widget)

    def load_selected_example(self, index):
        # 获取当前语言类型
        language_type = self.language_combo.currentData()
        example_type = self.example_combo.currentData()
        
        if example_type is None:
            return
        
        # 不同语言和示例类型的代码示例
        examples = {
            LanguageType.PSEUDO: {
                "basic": "FOR i := 1 TO 10 DO\n  x := x + i\nENDFOR",
                "nested": "FOR i := 1 TO 5 DO\n  FOR j := 1 TO i DO\n    sum := sum + i * j\n  ENDFOR\nENDFOR",
                "complex": "FOR k := (a + b) * 2 TO n / 2 + 5 DO\n  result := result + (k * k - 3)\nENDFOR"
            },
            LanguageType.C_STYLE: {
                "basic": "for (i = 1; i < 10; i++) {\n  x = x + i;\n}",
                "nested": "for (i = 1; i <= 5; i++) {\n  for (j = 1; j <= i; j++) {\n    sum = sum + i * j;\n  }\n}",
                "complex": "for (k = (a + b) * 2; k <= n / 2 + 5; k++) {\n  result = result + (k * k - 3);\n}"
            },
            LanguageType.PYTHON: {
                "basic": "for i in range(1, 10):\n  x = x + i",
                "nested": "for i in range(1, 6):\n  for j in range(1, i+1):\n    sum = sum + i * j",
                "complex": "for k in range((a + b) * 2, n / 2 + 5):\n  result = result + (k * k - 3)"
            }
        }
        
        # 设置示例代码
        if language_type in examples and example_type in examples[language_type]:
            self.input_text.setPlainText(examples[language_type][example_type])
            
            # 更新高亮
            self.highlighter.language_type = language_type
            self.highlighter.rehighlight()
            
            # 更新状态栏
            self.status_bar.showMessage(f"已加载{self.language_combo.currentText()}的{self.example_combo.currentText()}示例")

    def create_output_area(self):
        # 创建输出区域（使用选项卡）
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 10, 0, 0)
        
        output_label = QLabel("生成的四元式:")
        output_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        # 创建选项卡部件
        self.output_tabs = QTabWidget()
        
        # 创建四元式输出选项卡
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 12))
        self.output_text.setReadOnly(True)
        self.output_text.setLineWrapMode(QTextEdit.NoWrap)
        
        # 创建可视化选项卡
        self.visual_widget = QWidget()
        visual_layout = QVBoxLayout(self.visual_widget)
        
        # 添加图形场景
        self.graphics_scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # 添加放大、缩小和重置按钮
        zoom_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.setIcon(QIcon.fromTheme("zoom-in"))
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.setIcon(QIcon.fromTheme("zoom-out"))
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_zoom_btn = QPushButton("重置视图")
        self.reset_zoom_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.reset_zoom_btn)
        zoom_layout.addStretch()
        
        visual_layout.addLayout(zoom_layout)
        visual_layout.addWidget(self.graphics_view)
        
        # 添加选项卡
        self.output_tabs.addTab(self.output_text, "四元式输出")
        self.output_tabs.addTab(self.visual_widget, "可视化图")
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_tabs)
        
        # 添加到分割器
        self.splitter.addWidget(output_widget)
        
    def zoom_in(self):
        self.graphics_view.scale(1.2, 1.2)
        
    def zoom_out(self):
        self.graphics_view.scale(1/1.2, 1/1.2)
        
    def reset_zoom(self):
        self.graphics_view.resetTransform()

    def create_button_area(self):
        # 创建底部按钮区域
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.StyledPanel)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # 翻译按钮
        self.translate_button = QPushButton("翻译为四元式")
        self.translate_button.setMinimumSize(QSize(150, 40))
        self.translate_button.setIcon(QIcon.fromTheme("system-run"))
        self.translate_button.clicked.connect(self.translate)
        
        # 保存四元式按钮
        self.save_button = QPushButton("保存四元式")
        self.save_button.setMinimumSize(QSize(150, 40))
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_quadruples)
        self.save_button.setEnabled(False)
        
        # 保存可视化图按钮
        self.save_visual_button = QPushButton("保存可视化图")
        self.save_visual_button.setMinimumSize(QSize(150, 40))
        self.save_visual_button.setIcon(QIcon.fromTheme("image-x-generic"))
        self.save_visual_button.clicked.connect(self.save_visualization)
        self.save_visual_button.setEnabled(False)
        
        # 清空按钮
        self.clear_button = QPushButton("清空")
        self.clear_button.setMinimumSize(QSize(150, 40))
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.clicked.connect(self.clear_all)
        
        # 添加按钮到布局
        button_layout.addStretch()
        button_layout.addWidget(self.translate_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_visual_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        self.main_layout.addWidget(button_frame)

    def update_example_code(self):
        # 根据选择的语言更新示例代码
        language_type = self.language_combo.currentData()
        
        if language_type == LanguageType.PSEUDO:
            example_code = "FOR i := 1 TO 10 DO\n  x := x + i\nENDFOR"
        elif language_type == LanguageType.C_STYLE:
            example_code = "for (i = 1; i < 10; i++) {\n  x = x + i;\n}"
        elif language_type == LanguageType.PYTHON:
            example_code = "for i in range(1, 10):\n  x = x + i"
            
        self.input_text.clear()
        self.input_text.setPlainText(example_code)
        
        # 重置示例选择下拉框
        self.example_combo.setCurrentIndex(0)
        
        # 更新语言描述
        self.update_language_desc()

    def translate(self):
        # 获取输入代码和选择的语言类型
        input_code = self.input_text.toPlainText().strip()
        language_type = self.language_combo.currentData()
        
        if not input_code:
            QMessageBox.warning(self, "输入错误", "请输入FOR语句")
            return
            
        # 更新状态栏
        self.status_bar.showMessage("正在翻译...")
        
        # 延时处理，提供更好的用户体验
        QApplication.processEvents()
        
        try:
            # 调用翻译函数
            self.quadruples = translate_to_quadruples(input_code, language_type)
            
            if not self.quadruples:
                self.output_text.clear()
                self.output_text.setPlainText("未生成四元式")
                self.save_button.setEnabled(False)
                self.save_visual_button.setEnabled(False)
                self.status_bar.showMessage("翻译完成：未生成四元式")
                
                # 清空可视化
                self.graphics_scene.clear()
                self.graphics_scene.addText("没有四元式数据可供可视化", QFont("Arial", 14))
                return
                
            # 处理和格式化四元式输出
            label_map = {}
            formatted_quads = []
            jump_ops = {'JMP', 'JZ', 'J>', 'J<', 'J>=', 'J<=', 'J==', 'J!='}
            
            # 第一遍：查找标签索引
            for i, quad in enumerate(self.quadruples):
                if quad.op == 'LABEL' and quad.result is not None:
                    label_map[quad.result] = i
                    
            # 第二遍：格式化显示
            for i, quad in enumerate(self.quadruples):
                arg1_str = quad.arg1 if quad.arg1 is not None else '_'
                arg2_str = quad.arg2 if quad.arg2 is not None else '_'
                result_str = quad.result if quad.result is not None else '_'
                
                if quad.op == 'LABEL':
                    display_str = f"{i}: LABEL {result_str}"
                elif quad.op in jump_ops and quad.result in label_map:
                    target_idx = label_map[quad.result]
                    display_str = f"{i}: ({quad.op}, {arg1_str}, {arg2_str}, {result_str} -> {target_idx})"
                else:
                    display_str = f"{i}: ({quad.op}, {arg1_str}, {arg2_str}, {result_str})"
                    
                formatted_quads.append(display_str)
                
            # 显示结果
            self.output_text.clear()
            self.output_text.setPlainText("\n".join(formatted_quads))

            # 创建并更新可视化图
            self.graphics_scene.clear() # 清空旧的图形
            visualizer = QuadrupleVisualizer() # 创建时不指定父控件
            visualizer.set_quadruples(self.quadruples) # 设置数据并计算布局/大小
            self.graphics_scene.addWidget(visualizer) # 将QWidget添加到场景中

            # 调整视图以适应所有内容
            # fitInView 现在应该能正确工作，因为它会适应场景中的 QGraphicsProxyWidget
            self.graphics_view.fitInView(self.graphics_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # 启用保存按钮
            self.save_button.setEnabled(True)
            self.save_visual_button.setEnabled(True)

            self.status_bar.showMessage(f"翻译完成：生成了 {len(self.quadruples)} 条四元式")

        except Exception as e:
            self.output_text.clear()
            self.output_text.setPlainText(f"错误: {str(e)}")
            self.save_button.setEnabled(False)
            self.save_visual_button.setEnabled(False)
            self.status_bar.showMessage(f"翻译出错: {str(e)}")

            # 清空可视化
            self.graphics_scene.clear() # 确保错误时也清空
            self.graphics_scene.addText(f"错误: {str(e)}", QFont("Arial", 14)) # 在场景中显示错误信息

    def save_quadruples(self):
        if not self.quadruples:
            QMessageBox.warning(self, "保存错误", "没有可保存的四元式")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存四元式",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # 再次格式化四元式用于保存
            label_map = {}
            formatted_quads = []
            jump_ops = {'JMP', 'JZ', 'J>', 'JG', 'J<', 'JL', 'J>=', 'J<=', 'J==', 'J!='}
            
            # 第一遍：查找标签索引
            for i, quad in enumerate(self.quadruples):
                if quad.op == 'LABEL' and quad.result is not None:
                    label_map[quad.result] = i
                    
            # 第二遍：格式化保存
            for i, quad in enumerate(self.quadruples):
                arg1_str = quad.arg1 if quad.arg1 is not None else '_'
                arg2_str = quad.arg2 if quad.arg2 is not None else '_'
                result_str = quad.result if quad.result is not None else '_'
                
                if quad.op == 'LABEL':
                    save_str = f"{i}: LABEL {result_str}"
                elif quad.op in jump_ops and quad.result in label_map:
                    target_idx = label_map[quad.result]
                    save_str = f"{i}: ({quad.op}, {arg1_str}, {arg2_str}, {result_str} -> {target_idx})"
                else:
                    save_str = f"{i}: ({quad.op}, {arg1_str}, {arg2_str}, {result_str})"
                    
                formatted_quads.append(save_str)
                
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(formatted_quads))
                
            QMessageBox.information(self, "保存成功", f"四元式已保存至 {file_path}")
            self.status_bar.showMessage(f"四元式已保存至 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存文件失败: {str(e)}")
            self.status_bar.showMessage(f"保存失败: {str(e)}")

    def save_visualization(self):
        """保存可视化图为图片文件"""
        if not self.quadruples:
            QMessageBox.warning(self, "保存错误", "没有可保存的可视化图")
            return
            
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "保存可视化图",
            "",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # 获取图形场景中的widget
            items = self.graphics_scene.items()
            if not items:
                QMessageBox.warning(self, "保存错误", "可视化图为空")
                return
                
            visualizer = None
            for item in items:
                if isinstance(item, QGraphicsProxyWidget):
                    widget = item.widget()
                    if isinstance(widget, QuadrupleVisualizer):
                        visualizer = widget
                        break
            
            if not visualizer:
                QMessageBox.warning(self, "保存错误", "找不到可视化器组件")
                return
                
            # 创建画布并渲染可视化图
            pixmap = QPixmap(visualizer.size())
            pixmap.fill(Qt.white)  # 使用白色背景
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            visualizer.render(painter)
            painter.end()
            
            # 保存图片
            if not pixmap.save(file_path):
                raise Exception("保存图片失败")
                
            QMessageBox.information(self, "保存成功", f"可视化图已保存至 {file_path}")
            self.status_bar.showMessage(f"可视化图已保存至 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存图片失败: {str(e)}")
            self.status_bar.showMessage(f"保存失败: {str(e)}")

    def clear_all(self):
        # 清空输入和输出
        self.input_text.clear()
        self.output_text.clear()
        self.quadruples = []
        self.save_button.setEnabled(False)
        self.save_visual_button.setEnabled(False)
        
        # 清空可视化图
        self.graphics_scene.clear()
        
        # 重新设置示例代码
        self.update_example_code()
        self.status_bar.showMessage("已清空所有内容")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    # app.setWindowIcon(QIcon("icon.png"))  # 如果有图标可以取消注释
    
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec_()) 