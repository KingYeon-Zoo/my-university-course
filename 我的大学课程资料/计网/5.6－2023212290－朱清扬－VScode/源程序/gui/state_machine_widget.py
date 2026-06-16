"""
TCP状态机可视化组件（拓展功能）
展示TCP连接的状态转换过程
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
import math


class TCPStateMachineCanvas(QWidget):
    """TCP状态机画布"""
    
    # TCP状态定义
    STATES = {
        'CLOSED': (100, 100),
        'LISTEN': (100, 200),
        'SYN_SENT': (300, 100),
        'SYN_RECEIVED': (300, 200),
        'ESTABLISHED': (500, 150),
        'FIN_WAIT_1': (700, 100),
        'FIN_WAIT_2': (700, 200),
        'CLOSE_WAIT': (500, 300),
        'CLOSING': (700, 300),
        'LAST_ACK': (500, 400),
        'TIME_WAIT': (900, 150)
    }
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 500)
        self.current_state = 'CLOSED'
        self.state_history = []
        self.animation_timer = None
        self.animation_step = 0
        
    def set_state(self, state):
        """设置当前状态"""
        if state in self.STATES:
            self.current_state = state
            self.update()
    
    def set_state_history(self, history):
        """设置状态历史"""
        self.state_history = history
        self.update()
    
    def start_animation(self):
        """开始状态转换动画"""
        if not self.state_history:
            return
        
        self.animation_step = 0
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_animation_step)
        self.animation_timer.start(1000)  # 每秒一个状态
    
    def next_animation_step(self):
        """下一个动画步骤"""
        if self.animation_step < len(self.state_history):
            self.current_state = self.state_history[self.animation_step]['state']
            self.animation_step += 1
            self.update()
        else:
            if self.animation_timer:
                self.animation_timer.stop()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 白色背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 绘制所有状态转换箭头
        self.draw_transitions(painter)
        
        # 绘制所有状态
        for state, pos in self.STATES.items():
            is_current = (state == self.current_state)
            self.draw_state(painter, state, pos[0], pos[1], is_current)
        
        # 绘制图例
        self.draw_legend(painter)
    
    def draw_state(self, painter, state, x, y, is_current):
        """绘制状态节点"""
        # 选择颜色
        if is_current:
            color = QColor(76, 175, 80)  # 绿色 - 当前状态
            border_color = QColor(56, 142, 60)
        elif state == 'ESTABLISHED':
            color = QColor(33, 150, 243)  # 蓝色 - 已建立
            border_color = QColor(25, 118, 210)
        elif state == 'CLOSED':
            color = QColor(158, 158, 158)  # 灰色 - 关闭
            border_color = QColor(117, 117, 117)
        else:
            color = QColor(255, 193, 7)  # 黄色 - 过渡状态
            border_color = QColor(255, 160, 0)
        
        # 绘制状态圆
        radius = 35 if is_current else 30
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(border_color, 3 if is_current else 2))
        painter.drawEllipse(QPointF(x, y), radius, radius)
        
        # 绘制状态名称
        font = QFont("Arial", 9 if is_current else 8, QFont.Bold if is_current else QFont.Normal)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        # 分行显示状态名
        state_text = state.replace('_', '\n')
        text_rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
        painter.drawText(text_rect, Qt.AlignCenter, state_text)
    
    def draw_transitions(self, painter):
        """绘制状态转换箭头"""
        painter.setPen(QPen(QColor(200, 200, 200), 1.5, Qt.DashLine))
        
        # 定义主要的状态转换
        transitions = [
            ('CLOSED', 'LISTEN'),
            ('CLOSED', 'SYN_SENT'),
            ('LISTEN', 'SYN_RECEIVED'),
            ('SYN_SENT', 'SYN_RECEIVED'),
            ('SYN_SENT', 'ESTABLISHED'),
            ('SYN_RECEIVED', 'ESTABLISHED'),
            ('ESTABLISHED', 'FIN_WAIT_1'),
            ('ESTABLISHED', 'CLOSE_WAIT'),
            ('FIN_WAIT_1', 'FIN_WAIT_2'),
            ('FIN_WAIT_1', 'CLOSING'),
            ('FIN_WAIT_2', 'TIME_WAIT'),
            ('CLOSE_WAIT', 'LAST_ACK'),
            ('CLOSING', 'TIME_WAIT'),
            ('LAST_ACK', 'CLOSED'),
            ('TIME_WAIT', 'CLOSED')
        ]
        
        for from_state, to_state in transitions:
            if from_state in self.STATES and to_state in self.STATES:
                from_pos = self.STATES[from_state]
                to_pos = self.STATES[to_state]
                
                # 绘制箭头（简化版）
                painter.drawLine(int(from_pos[0]), int(from_pos[1]), 
                               int(to_pos[0]), int(to_pos[1]))
    
    def draw_legend(self, painter):
        """绘制图例"""
        legend_x = 20
        legend_y = self.height() - 100
        
        painter.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        painter.setPen(QColor(50, 50, 50))
        painter.drawText(legend_x, legend_y, "状态图例:")
        
        # 图例项
        legend_items = [
            (QColor(76, 175, 80), "当前状态"),
            (QColor(33, 150, 243), "已建立连接"),
            (QColor(255, 193, 7), "过渡状态"),
            (QColor(158, 158, 158), "关闭状态")
        ]
        
        y_offset = legend_y + 20
        for color, text in legend_items:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawEllipse(QPointF(legend_x + 10, y_offset), 8, 8)
            
            painter.setPen(QColor(50, 50, 50))
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.drawText(legend_x + 30, y_offset + 5, text)
            
            y_offset += 20


class TCPStateMachineWidget(QWidget):
    """TCP状态机组件"""
    
    def __init__(self):
        super().__init__()
        self.packets = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP状态机可视化")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 主要布局（左侧状态机，右侧历史记录）
        main_layout = QHBoxLayout()
        
        # 左侧：状态机画布
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.animate_btn = QPushButton("▶ 播放状态转换")
        self.animate_btn.clicked.connect(self.play_animation)
        btn_layout.addWidget(self.animate_btn)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.reset_state)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        
        left_layout.addLayout(btn_layout)
        
        # 状态机画布
        self.canvas = TCPStateMachineCanvas()
        left_layout.addWidget(self.canvas)
        
        # 当前状态信息
        self.current_state_label = QLabel("当前状态: CLOSED")
        self.current_state_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        left_layout.addWidget(self.current_state_label)
        
        main_layout.addWidget(left_widget, 2)
        
        # 右侧：状态历史
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        history_label = QLabel("状态转换历史:")
        history_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        right_layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_clicked)
        right_layout.addWidget(self.history_list)
        
        main_layout.addWidget(right_widget, 1)
        
        layout.addLayout(main_layout)
        
        # 状态说明
        info_label = QLabel(
            "说明: TCP连接通过不同的状态进行管理。"
            "点击播放按钮可以查看连接状态的转换动画。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #E3F2FD; border-radius: 4px;")
        layout.addWidget(info_label)
    
    def update_view(self, packets):
        """更新视图"""
        if not packets:
            return
        
        self.packets = packets
        self.analyze_state_transitions()
    
    def analyze_state_transitions(self):
        """分析状态转换"""
        if not self.packets:
            return
        
        state_history = []
        current_state = 'CLOSED'
        
        # 分析数据包，推断状态转换
        for pkt in self.packets:
            flags = pkt['flags']
            new_state = current_state
            event = ""
            
            # 根据标志位推断状态转换
            if flags == 2 or flags == 'S':
                # SYN包
                if current_state == 'CLOSED':
                    new_state = 'SYN_SENT'
                    event = "发送 SYN"
                elif current_state == 'LISTEN':
                    new_state = 'SYN_RECEIVED'
                    event = "接收 SYN"
                    
            elif flags == 18 or flags == 'SA':
                # SYN-ACK包
                if current_state == 'SYN_SENT':
                    new_state = 'ESTABLISHED'
                    event = "接收 SYN-ACK，发送 ACK"
                elif current_state == 'LISTEN':
                    new_state = 'SYN_RECEIVED'
                    event = "发送 SYN-ACK"
                    
            elif flags == 16 or flags == 'A':
                # ACK包
                if current_state == 'SYN_RECEIVED':
                    new_state = 'ESTABLISHED'
                    event = "接收 ACK，连接建立"
                elif current_state == 'FIN_WAIT_1':
                    new_state = 'FIN_WAIT_2'
                    event = "接收 ACK"
                elif current_state == 'CLOSING':
                    new_state = 'TIME_WAIT'
                    event = "接收 ACK"
                elif current_state == 'LAST_ACK':
                    new_state = 'CLOSED'
                    event = "接收 ACK，连接关闭"
                    
            elif isinstance(flags, int) and (flags & 0x01):
                # FIN包
                if current_state == 'ESTABLISHED':
                    if pkt['ack'] > 0:
                        # FIN-ACK
                        new_state = 'FIN_WAIT_1'
                        event = "发送 FIN"
                    else:
                        new_state = 'CLOSE_WAIT'
                        event = "接收 FIN"
                elif current_state == 'FIN_WAIT_1':
                    new_state = 'CLOSING'
                    event = "接收 FIN"
                elif current_state == 'FIN_WAIT_2':
                    new_state = 'TIME_WAIT'
                    event = "接收 FIN"
                elif current_state == 'CLOSE_WAIT':
                    new_state = 'LAST_ACK'
                    event = "发送 FIN"
            
            # 如果状态改变，记录
            if new_state != current_state:
                state_history.append({
                    'state': new_state,
                    'time': pkt['time'],
                    'event': event,
                    'packet_info': f"{pkt['src_ip']}:{pkt['src_port']} -> {pkt['dst_ip']}:{pkt['dst_port']}"
                })
                current_state = new_state
        
        # 更新历史列表
        self.history_list.clear()
        for i, state_info in enumerate(state_history):
            item_text = (f"{i+1}. {state_info['state']}\n"
                        f"   事件: {state_info['event']}\n"
                        f"   {state_info['packet_info']}")
            item = QListWidgetItem(item_text)
            
            # 根据状态设置颜色
            if state_info['state'] == 'ESTABLISHED':
                item.setBackground(QColor(200, 255, 200))  # 浅绿色
            elif state_info['state'] == 'CLOSED':
                item.setBackground(QColor(220, 220, 220))  # 浅灰色
            
            self.history_list.addItem(item)
        
        # 设置状态历史到画布
        self.canvas.set_state_history(state_history)
        
        # 设置最终状态
        if state_history:
            final_state = state_history[-1]['state']
            self.canvas.set_state(final_state)
            self.current_state_label.setText(f"当前状态: {final_state}")
        else:
            self.current_state_label.setText("当前状态: CLOSED (未检测到状态转换)")
    
    def play_animation(self):
        """播放动画"""
        self.canvas.start_animation()
    
    def reset_state(self):
        """重置状态"""
        self.canvas.set_state('CLOSED')
        self.current_state_label.setText("当前状态: CLOSED")
    
    def on_history_clicked(self, item):
        """点击历史记录"""
        # 从文本中提取状态名
        text = item.text()
        state_line = text.split('\n')[0]
        state = state_line.split('. ')[1] if '. ' in state_line else 'CLOSED'
        
        self.canvas.set_state(state)
        self.current_state_label.setText(f"当前状态: {state}")

