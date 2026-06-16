"""
重传分析和动画演示组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RetransmitCanvas(QWidget):
    """重传动画画布"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 300)
        self.retransmissions = []
        self.animation_step = 0
        self.animation_timer = None
        self.current_retrans = None
    
    def set_data(self, retransmissions):
        """设置重传数据"""
        self.retransmissions = retransmissions
        self.animation_step = 0
        self.current_retrans = None
        self.update()
    
    def start_animation(self):
        """开始动画"""
        if not self.retransmissions:
            return
        
        self.animation_step = 0
        self.current_retrans = self.retransmissions[0] if self.retransmissions else None
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_animation_step)
        self.animation_timer.start(500)
    
    def next_animation_step(self):
        """下一帧动画"""
        if self.animation_step < 8:
            self.animation_step += 1
            self.update()
        else:
            if self.animation_timer:
                self.animation_timer.stop()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if self.current_retrans:
            self.draw_retransmission(painter)
        else:
            self.draw_placeholder(painter)
    
    def draw_placeholder(self, painter):
        """绘制占位符"""
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        font = QFont("Microsoft YaHei", 12)
        painter.setFont(font)
        
        if not self.retransmissions:
            text = "未检测到重传"
        else:
            text = "点击'播放动画'查看重传过程"
        
        painter.drawText(self.rect(), Qt.AlignCenter, text)
    
    def draw_retransmission(self, painter):
        """绘制重传过程"""
        width = self.width()
        height = self.height()
        
        sender_x = width * 0.2
        receiver_x = width * 0.8
        center_y = height * 0.5
        
        # 绘制发送方和接收方
        painter.setBrush(QBrush(QColor(66, 133, 244)))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawEllipse(QPointF(sender_x, center_y), 40, 40)
        
        painter.setBrush(QBrush(QColor(52, 168, 83)))
        painter.setPen(QPen(QColor(40, 130, 60), 2))
        painter.drawEllipse(QPointF(receiver_x, center_y), 40, 40)
        
        # 标签
        font = QFont("Microsoft YaHei", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(int(sender_x - 25), int(center_y + 5), "发送方")
        painter.drawText(int(receiver_x - 25), int(center_y + 5), "接收方")
        
        # 绘制数据包
        if self.animation_step >= 1:
            # 原始数据包
            packet_x = sender_x + (receiver_x - sender_x) * min(self.animation_step / 4.0, 1.0)
            
            if self.animation_step <= 3:
                # 原始包在传输中
                painter.setBrush(QBrush(QColor(76, 175, 80)))
                painter.setPen(QPen(QColor(56, 142, 60), 2))
                painter.drawRect(int(packet_x - 20), int(center_y - 60), 40, 30)
                
                font = QFont("Microsoft YaHei", 8)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(int(packet_x - 18), int(center_y - 45), "数据包")
            
            elif self.animation_step == 4:
                # 包丢失
                painter.setPen(QPen(QColor(244, 67, 54), 3))
                font = QFont("Microsoft YaHei", 12, QFont.Bold)
                painter.setFont(font)
                painter.drawText(int(width * 0.5 - 30), int(center_y - 80), "丢包!")
                
                # 绘制X
                mid_x = (sender_x + receiver_x) / 2
                painter.drawLine(int(mid_x - 20), int(center_y - 70), int(mid_x + 20), int(center_y - 40))
                painter.drawLine(int(mid_x + 20), int(center_y - 70), int(mid_x - 20), int(center_y - 40))
        
        # 重传数据包
        if self.animation_step >= 5:
            packet_x = sender_x + (receiver_x - sender_x) * min((self.animation_step - 4) / 4.0, 1.0)
            
            painter.setBrush(QBrush(QColor(255, 152, 0)))
            painter.setPen(QPen(QColor(245, 124, 0), 2))
            painter.drawRect(int(packet_x - 20), int(center_y - 60), 40, 30)
            
            font = QFont("Microsoft YaHei", 8)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(int(packet_x - 18), int(center_y - 45), "重传")
        
        # 成功标记
        if self.animation_step >= 8:
            painter.setPen(QPen(QColor(76, 175, 80), 3))
            font = QFont("Microsoft YaHei", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(int(receiver_x - 40), int(center_y + 80), "接收成功!")


class RetransmitWidget(QWidget):
    """重传分析组件"""
    
    def __init__(self):
        super().__init__()
        self.packets = []
        self.retransmissions = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP重传检测与分析")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶ 播放重传动画")
        self.play_btn.clicked.connect(self.play_animation)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 动画画布
        self.canvas = RetransmitCanvas()
        layout.addWidget(self.canvas)
        
        # 重传统计表格
        stats_label = QLabel("重传统计:")
        stats_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(stats_label)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels(['序号', '原始Seq', '原始时间', '重传时间', '时间差(ms)'])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.setMaximumHeight(200)
        layout.addWidget(self.stats_table)
    
    def update_view(self, packets, retransmissions):
        """更新视图"""
        self.packets = packets
        self.retransmissions = retransmissions
        
        # 更新动画
        self.canvas.set_data(retransmissions)
        
        # 更新表格
        self.stats_table.setRowCount(len(retransmissions))
        
        for i, retrans in enumerate(retransmissions):
            orig = retrans['original']
            retrans_pkt = retrans['retransmit']
            time_diff = (retrans_pkt['time'] - orig['time']) * 1000  # 转换为毫秒
            
            self.stats_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(orig['seq'])))
            self.stats_table.setItem(i, 2, QTableWidgetItem(f"{orig['time']:.6f}"))
            self.stats_table.setItem(i, 3, QTableWidgetItem(f"{retrans_pkt['time']:.6f}"))
            self.stats_table.setItem(i, 4, QTableWidgetItem(f"{time_diff:.2f}"))
    
    def play_animation(self):
        """播放动画"""
        self.canvas.start_animation()

