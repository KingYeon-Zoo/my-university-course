"""
TCP握手和挥手可视化组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
import time


class HandshakeCanvas(QWidget):
    """握手动画画布"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.handshake_data = None
        self.fin_data = None
        self.animation_step = 0
        self.animation_timer = None
        self.animation_mode = 'handshake'  # 'handshake' or 'fin'
    
    def set_data(self, handshake_data, fin_data):
        """设置数据"""
        self.handshake_data = handshake_data
        self.fin_data = fin_data
        self.animation_step = 0
        self.update()
    
    def start_animation(self, mode='handshake'):
        """开始动画"""
        self.animation_mode = mode
        self.animation_step = 0
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_animation_step)
        self.animation_timer.start(800)  # 每800ms一帧
    
    def next_animation_step(self):
        """下一帧动画"""
        max_steps = 6 if self.animation_mode == 'handshake' else 8
        
        if self.animation_step < max_steps:
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
        
        if self.animation_mode == 'handshake' and self.handshake_data:
            self.draw_handshake(painter)
        elif self.animation_mode == 'fin' and self.fin_data:
            self.draw_fin(painter)
        else:
            self.draw_placeholder(painter)
    
    def draw_placeholder(self, painter):
        """绘制占位符"""
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        font = QFont("Microsoft YaHei", 14)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "请选择一个TCP连接")
    
    def draw_handshake(self, painter):
        """绘制三次握手"""
        width = self.width()
        height = self.height()
        
        # 客户端和服务器位置
        client_x = width * 0.25
        server_x = width * 0.75
        start_y = height * 0.15
        
        # 绘制客户端和服务器
        self.draw_endpoint(painter, client_x, start_y, "客户端", QColor(66, 133, 244))
        self.draw_endpoint(painter, server_x, start_y, "服务器", QColor(52, 168, 83))
        
        # 绘制垂直时间线
        painter.setPen(QPen(QColor(200, 200, 200), 2, Qt.DashLine))
        painter.drawLine(int(client_x), int(start_y + 60), int(client_x), int(height - 50))
        painter.drawLine(int(server_x), int(start_y + 60), int(server_x), int(height - 50))
        
        # 绘制三次握手箭头
        y_offset = start_y + 100
        step_height = 100
        
        syn = self.handshake_data['syn']
        syn_ack = self.handshake_data['syn_ack']
        ack = self.handshake_data['ack']
        
        # 第一步: SYN
        if self.animation_step >= 1:
            self.draw_arrow(painter, client_x, server_x, y_offset, 
                          f"SYN (seq={syn['seq']})", QColor(244, 67, 54))
        
        # 第二步: SYN-ACK
        if self.animation_step >= 3:
            self.draw_arrow(painter, server_x, client_x, y_offset + step_height,
                          f"SYN-ACK (seq={syn_ack['seq']}, ack={syn_ack['ack']})",
                          QColor(33, 150, 243), reverse=True)
        
        # 第三步: ACK
        if self.animation_step >= 5:
            self.draw_arrow(painter, client_x, server_x, y_offset + step_height * 2,
                          f"ACK (ack={ack['ack']})", QColor(76, 175, 80))
        
        # 绘制状态文字
        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        
        if self.animation_step >= 2:
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(int(client_x - 80), int(y_offset + 30), "SYN_SENT")
        
        if self.animation_step >= 4:
            painter.drawText(int(server_x - 80), int(y_offset + step_height + 30), "SYN_RECEIVED")
        
        if self.animation_step >= 6:
            painter.setPen(QColor(0, 150, 0))
            painter.drawText(int(client_x - 80), int(y_offset + step_height * 2 + 60), "ESTABLISHED")
            painter.drawText(int(server_x - 80), int(y_offset + step_height * 2 + 60), "ESTABLISHED")
    
    def draw_fin(self, painter):
        """绘制四次挥手"""
        width = self.width()
        height = self.height()
        
        # 客户端和服务器位置
        client_x = width * 0.25
        server_x = width * 0.75
        start_y = height * 0.1
        
        # 绘制客户端和服务器
        self.draw_endpoint(painter, client_x, start_y, "客户端", QColor(66, 133, 244))
        self.draw_endpoint(painter, server_x, start_y, "服务器", QColor(52, 168, 83))
        
        # 绘制垂直时间线
        painter.setPen(QPen(QColor(200, 200, 200), 2, Qt.DashLine))
        painter.drawLine(int(client_x), int(start_y + 60), int(client_x), int(height - 30))
        painter.drawLine(int(server_x), int(start_y + 60), int(server_x), int(height - 30))
        
        # 绘制四次挥手
        y_offset = start_y + 100
        step_height = 80
        
        fin_packets = self.fin_data['fin_packets']
        
        # 第一步: FIN
        if self.animation_step >= 1 and len(fin_packets) > 0:
            self.draw_arrow(painter, client_x, server_x, y_offset,
                          f"FIN (seq={fin_packets[0]['seq']})", QColor(244, 67, 54))
        
        # 第二步: ACK
        if self.animation_step >= 3:
            self.draw_arrow(painter, server_x, client_x, y_offset + step_height,
                          "ACK", QColor(33, 150, 243), reverse=True)
        
        # 第三步: FIN
        if self.animation_step >= 5 and len(fin_packets) > 1:
            self.draw_arrow(painter, server_x, client_x, y_offset + step_height * 2,
                          f"FIN (seq={fin_packets[1]['seq']})", QColor(255, 152, 0), reverse=True)
        
        # 第四步: ACK
        if self.animation_step >= 7:
            self.draw_arrow(painter, client_x, server_x, y_offset + step_height * 3,
                          "ACK", QColor(76, 175, 80))
        
        # 绘制状态文字
        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        painter.setPen(QColor(100, 100, 100))
        
        if self.animation_step >= 2:
            painter.drawText(int(client_x - 80), int(y_offset + 30), "FIN_WAIT_1")
        
        if self.animation_step >= 4:
            painter.drawText(int(server_x - 80), int(y_offset + step_height + 30), "CLOSE_WAIT")
            painter.drawText(int(client_x - 80), int(y_offset + step_height + 30), "FIN_WAIT_2")
        
        if self.animation_step >= 6:
            painter.drawText(int(server_x - 80), int(y_offset + step_height * 2 + 30), "LAST_ACK")
        
        if self.animation_step >= 8:
            painter.setPen(QColor(200, 0, 0))
            painter.drawText(int(client_x - 80), int(y_offset + step_height * 3 + 50), "CLOSED")
            painter.drawText(int(server_x - 80), int(y_offset + step_height * 3 + 50), "CLOSED")
    
    def draw_endpoint(self, painter, x, y, label, color):
        """绘制端点（客户端/服务器）"""
        # 绘制圆形
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawEllipse(QPointF(x, y), 30, 30)
        
        # 绘制标签
        font = QFont("Microsoft YaHei", 11, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        # 计算文字位置使其居中
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(label)
        painter.drawText(int(x - text_width / 2), int(y + 5), label)
    
    def draw_arrow(self, painter, x1, x2, y, label, color, reverse=False):
        """绘制箭头"""
        if reverse:
            x1, x2 = x2, x1
        
        # 绘制箭头线
        painter.setPen(QPen(color, 3))
        painter.drawLine(int(x1), int(y), int(x2 - 10), int(y))
        
        # 绘制箭头头部
        arrow_size = 10
        painter.setBrush(QBrush(color))
        points = [
            QPointF(x2, y),
            QPointF(x2 - arrow_size, y - arrow_size / 2),
            QPointF(x2 - arrow_size, y + arrow_size / 2)
        ]
        painter.drawPolygon(*points)
        
        # 绘制标签
        font = QFont("Microsoft YaHei", 9)
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))
        mid_x = (x1 + x2) / 2
        painter.drawText(int(mid_x - 100), int(y - 10), label)


class HandshakeWidget(QWidget):
    """握手组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP连接建立与释放过程")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        
        self.handshake_btn = QPushButton("▶ 播放三次握手")
        self.handshake_btn.clicked.connect(self.play_handshake)
        btn_layout.addWidget(self.handshake_btn)
        
        self.fin_btn = QPushButton("▶ 播放四次挥手")
        self.fin_btn.clicked.connect(self.play_fin)
        btn_layout.addWidget(self.fin_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 画布
        self.canvas = HandshakeCanvas()
        layout.addWidget(self.canvas)
        
        # 详细信息
        info_label = QLabel("详细信息:")
        info_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
    
    def update_view(self, handshake_data, fin_data):
        """更新视图"""
        self.canvas.set_data(handshake_data, fin_data)
        
        # 更新详细信息
        info = ""
        
        if handshake_data and handshake_data.get('complete'):
            info += "=== 三次握手 ===\n"
            syn = handshake_data['syn']
            syn_ack = handshake_data['syn_ack']
            ack = handshake_data['ack']
            
            info += f"1. SYN: {syn['src_ip']}:{syn['src_port']} -> {syn['dst_ip']}:{syn['dst_port']}\n"
            info += f"   Seq={syn['seq']}, Window={syn['window']}\n"
            info += f"2. SYN-ACK: {syn_ack['src_ip']}:{syn_ack['src_port']} -> {syn_ack['dst_ip']}:{syn_ack['dst_port']}\n"
            info += f"   Seq={syn_ack['seq']}, Ack={syn_ack['ack']}, Window={syn_ack['window']}\n"
            info += f"3. ACK: {ack['src_ip']}:{ack['src_port']} -> {ack['dst_ip']}:{ack['dst_port']}\n"
            info += f"   Ack={ack['ack']}, Window={ack['window']}\n"
        else:
            info += "未检测到完整的三次握手\n"
        
        info += "\n"
        
        if fin_data and fin_data.get('complete'):
            info += "=== 四次挥手 ===\n"
            fin_packets = fin_data['fin_packets']
            for i, fin_pkt in enumerate(fin_packets[:4]):
                info += f"{i+1}. FIN/ACK: {fin_pkt['src_ip']}:{fin_pkt['src_port']} -> {fin_pkt['dst_ip']}:{fin_pkt['dst_port']}\n"
                info += f"   Seq={fin_pkt['seq']}, Ack={fin_pkt['ack']}\n"
        else:
            info += "未检测到完整的四次挥手\n"
        
        self.info_text.setText(info)
    
    def play_handshake(self):
        """播放握手动画"""
        self.canvas.start_animation('handshake')
    
    def play_fin(self):
        """播放挥手动画"""
        self.canvas.start_animation('fin')

