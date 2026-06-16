"""
序列号和确认号变化可视化组件（增强版）
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                             QSplitter, QComboBox, QCheckBox)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QPointF
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt


class SequenceAnimationCanvas(QWidget):
    """序列号动画画布"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 400)
        self.packets = []
        self.animation_step = 0
        self.animation_timer = None
        self.current_packet_idx = 0
        
    def set_data(self, packets):
        """设置数据"""
        self.packets = packets[:50]  # 只显示前50个包
        self.animation_step = 0
        self.current_packet_idx = 0
        self.update()
    
    def start_animation(self):
        """开始动画"""
        if not self.packets:
            return
        
        self.animation_step = 0
        self.current_packet_idx = 0
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_animation_step)
        self.animation_timer.start(300)  # 每300ms一帧
    
    def next_animation_step(self):
        """下一帧动画"""
        if self.current_packet_idx < len(self.packets):
            self.current_packet_idx += 1
            self.update()
        else:
            if self.animation_timer:
                self.animation_timer.stop()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.packets:
            self.draw_placeholder(painter)
            return
        
        width = self.width()
        height = self.height()
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 绘制时间轴
        axis_y = height * 0.8
        axis_start_x = 50
        axis_end_x = width - 50
        
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(int(axis_start_x), int(axis_y), int(axis_end_x), int(axis_y))
        
        # 绘制时间轴标签
        font = QFont("Microsoft YaHei", 9)
        painter.setFont(font)
        painter.drawText(int(axis_start_x - 30), int(axis_y + 20), "时间")
        
        # 绘制数据包
        if self.current_packet_idx > 0:
            display_packets = self.packets[:self.current_packet_idx]
            
            for i, pkt in enumerate(display_packets):
                # 计算位置
                progress = i / max(len(self.packets) - 1, 1)
                x = axis_start_x + (axis_end_x - axis_start_x) * progress
                
                # 根据数据长度决定包的高度
                packet_height = min(20 + pkt['length'] / 100, 100)
                y = axis_y - packet_height - 10
                
                # 根据包类型选择颜色
                if pkt['length'] > 0:
                    color = QColor(76, 175, 80)  # 有数据 - 绿色
                elif pkt['flags'] == 2 or pkt['flags'] == 'S':
                    color = QColor(33, 150, 243)  # SYN - 蓝色
                elif pkt['flags'] == 18 or pkt['flags'] == 'SA':
                    color = QColor(156, 39, 176)  # SYN-ACK - 紫色
                else:
                    color = QColor(158, 158, 158)  # 其他 - 灰色
                
                # 绘制数据包矩形
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(color.darker(120), 2))
                painter.drawRect(int(x - 10), int(y), 20, int(packet_height))
                
                # 绘制序列号标签（最新的几个包）
                if i >= self.current_packet_idx - 3:
                    painter.setPen(QColor(50, 50, 50))
                    painter.setFont(QFont("Arial", 7))
                    painter.drawText(int(x - 25), int(y - 5), f"Seq:{pkt['seq'] % 10000}")
        
        # 绘制当前进度
        painter.setPen(QColor(244, 67, 54))
        painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        painter.drawText(20, 30, f"已显示: {self.current_packet_idx}/{len(self.packets)} 个数据包")
    
    def draw_placeholder(self, painter):
        """绘制占位符"""
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        font = QFont("Microsoft YaHei", 12)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "请选择一个TCP连接")


class SequenceWidget(QWidget):
    """序列号变化组件（增强版）"""
    
    def __init__(self):
        super().__init__()
        self.packets = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel("TCP序列号和确认号变化分析")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 视图切换按钮
        self.view_combo = QComboBox()
        self.view_combo.addItems(['图表视图', '动画视图', '表格视图'])
        self.view_combo.currentIndexChanged.connect(self.on_view_changed)
        title_layout.addWidget(QLabel("显示模式:"))
        title_layout.addWidget(self.view_combo)
        
        layout.addLayout(title_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 图表视图
        chart_widget = QWidget()
        chart_layout = QVBoxLayout()
        chart_widget.setLayout(chart_layout)
        
        # 图表选项
        chart_options_layout = QHBoxLayout()
        self.show_seq_check = QCheckBox("显示序列号")
        self.show_seq_check.setChecked(True)
        self.show_seq_check.stateChanged.connect(self.update_chart)
        
        self.show_ack_check = QCheckBox("显示确认号")
        self.show_ack_check.setChecked(True)
        self.show_ack_check.stateChanged.connect(self.update_chart)
        
        chart_options_layout.addWidget(self.show_seq_check)
        chart_options_layout.addWidget(self.show_ack_check)
        chart_options_layout.addStretch()
        
        chart_layout.addLayout(chart_options_layout)
        
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(chart_widget, "📊 图表分析")
        
        # 动画视图
        animation_widget = QWidget()
        animation_layout = QVBoxLayout()
        animation_widget.setLayout(animation_layout)
        
        # 动画控制按钮
        anim_control_layout = QHBoxLayout()
        self.play_anim_btn = QPushButton("▶ 播放动画")
        self.play_anim_btn.clicked.connect(self.play_animation)
        anim_control_layout.addWidget(self.play_anim_btn)
        anim_control_layout.addStretch()
        
        animation_layout.addLayout(anim_control_layout)
        
        # 动画画布
        self.animation_canvas = SequenceAnimationCanvas()
        animation_layout.addWidget(self.animation_canvas)
        
        # 图例
        legend_label = QLabel("图例: 🟢 数据包 | 🔵 SYN | 🟣 SYN-ACK | ⚪ 其他")
        animation_layout.addWidget(legend_label)
        
        self.tab_widget.addTab(animation_widget, "🎬 动画演示")
        
        # 表格视图
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_widget.setLayout(table_layout)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("总包数: 0")
        self.data_label = QLabel("数据包: 0")
        self.ack_label = QLabel("纯ACK: 0")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.data_label)
        stats_layout.addWidget(self.ack_label)
        stats_layout.addStretch()
        
        table_layout.addLayout(stats_layout)
        
        # 详细表格
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(8)
        self.detail_table.setHorizontalHeaderLabels([
            '序号', '相对时间(s)', '序列号', '确认号', '数据长度', 
            '窗口大小', '标志位', '说明'
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setSortingEnabled(True)
        
        table_layout.addWidget(self.detail_table)
        
        self.tab_widget.addTab(table_widget, "📋 详细数据")
        
        layout.addWidget(self.tab_widget)
    
    def on_view_changed(self, index):
        """视图切换"""
        self.tab_widget.setCurrentIndex(index)
    
    def play_animation(self):
        """播放动画"""
        self.animation_canvas.start_animation()
    
    def update_view(self, packets):
        """更新视图"""
        if not packets:
            return
        
        self.packets = packets
        self.animation_canvas.set_data(packets)
        self.update_chart()
        self.update_table()
    
    def update_chart(self):
        """更新图表"""
        if not self.packets:
            return
        
        # 清空图表
        self.figure.clear()
        
        # 创建子图
        num_plots = sum([self.show_seq_check.isChecked(), self.show_ack_check.isChecked()])
        if num_plots == 0:
            return
        
        current_plot = 1
        
        # 提取数据
        times = []
        seqs = []
        acks = []
        lengths = []
        
        start_time = self.packets[0]['time']
        
        for pkt in self.packets:
            relative_time = pkt['time'] - start_time
            times.append(relative_time)
            seqs.append(pkt['seq'])
            acks.append(pkt['ack'])
            lengths.append(pkt['length'])
        
        # 绘制序列号变化
        if self.show_seq_check.isChecked():
            ax1 = self.figure.add_subplot(num_plots, 1, current_plot)
            
            # 区分有数据和无数据的包
            data_points = [(t, s) for t, s, l in zip(times, seqs, lengths) if l > 0]
            ack_points = [(t, s) for t, s, l in zip(times, seqs, lengths) if l == 0]
            
            if data_points:
                data_times, data_seqs = zip(*data_points)
                ax1.plot(data_times, data_seqs, 'go-', label='数据包序列号', linewidth=2, markersize=6)
            
            if ack_points:
                ack_times, ack_seqs = zip(*ack_points)
                ax1.plot(ack_times, ack_seqs, 'b.', label='ACK包序列号', markersize=4, alpha=0.6)
            
            ax1.set_xlabel('时间 (秒)', fontsize=10, fontproperties='Microsoft YaHei')
            ax1.set_ylabel('序列号', fontsize=10, fontproperties='Microsoft YaHei')
            ax1.set_title('TCP序列号变化（区分数据包和ACK包）', fontsize=12, 
                         fontproperties='Microsoft YaHei', fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
            
            current_plot += 1
        
        # 绘制确认号变化
        if self.show_ack_check.isChecked():
            ax2 = self.figure.add_subplot(num_plots, 1, current_plot)
            
            # 只显示非零确认号
            valid_acks = [(t, a) for t, a in zip(times, acks) if a > 0]
            if valid_acks:
                valid_times, valid_acks_vals = zip(*valid_acks)
                ax2.plot(valid_times, valid_acks_vals, 'r.-', label='确认号 (ACK)', 
                        linewidth=2, markersize=5)
                
                # 标记ACK跳跃（可能表示数据丢失）
                for i in range(1, len(valid_acks_vals)):
                    if valid_acks_vals[i] == valid_acks_vals[i-1]:
                        # 重复ACK - 可能的丢包指示
                        ax2.plot(valid_times[i], valid_acks_vals[i], 'yo', 
                                markersize=8, label='重复ACK' if i == 1 else '')
            
            ax2.set_xlabel('时间 (秒)', fontsize=10, fontproperties='Microsoft YaHei')
            ax2.set_ylabel('确认号', fontsize=10, fontproperties='Microsoft YaHei')
            ax2.set_title('TCP确认号变化（突出重复ACK）', fontsize=12, 
                         fontproperties='Microsoft YaHei', fontweight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
        
        # 调整布局
        self.figure.tight_layout()
        
        # 刷新画布
        self.canvas.draw()
    
    def update_table(self):
        """更新表格"""
        if not self.packets:
            return
        
        # 计算统计信息
        total_packets = len(self.packets)
        data_packets = sum(1 for pkt in self.packets if pkt['length'] > 0)
        ack_packets = total_packets - data_packets
        
        self.total_label.setText(f"总包数: {total_packets}")
        self.data_label.setText(f"数据包: {data_packets}")
        self.ack_label.setText(f"纯ACK: {ack_packets}")
        
        # 填充表格（限制显示前200个）
        display_packets = self.packets[:200]
        self.detail_table.setRowCount(len(display_packets))
        
        start_time = self.packets[0]['time']
        
        for i, pkt in enumerate(display_packets):
            relative_time = pkt['time'] - start_time
            
            # 序号
            self.detail_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # 相对时间
            time_item = QTableWidgetItem(f"{relative_time:.6f}")
            self.detail_table.setItem(i, 1, time_item)
            
            # 序列号
            seq_item = QTableWidgetItem(str(pkt['seq']))
            self.detail_table.setItem(i, 2, seq_item)
            
            # 确认号
            ack_item = QTableWidgetItem(str(pkt['ack']) if pkt['ack'] > 0 else "-")
            self.detail_table.setItem(i, 3, ack_item)
            
            # 数据长度
            length_item = QTableWidgetItem(str(pkt['length']))
            if pkt['length'] > 0:
                length_item.setBackground(QColor(200, 255, 200))  # 浅绿色背景
            self.detail_table.setItem(i, 4, length_item)
            
            # 窗口大小
            window_item = QTableWidgetItem(str(pkt['window']))
            self.detail_table.setItem(i, 5, window_item)
            
            # 标志位
            flags_item = QTableWidgetItem(str(pkt['flags']))
            self.detail_table.setItem(i, 6, flags_item)
            
            # 说明
            description = self.get_packet_description(pkt)
            desc_item = QTableWidgetItem(description)
            self.detail_table.setItem(i, 7, desc_item)
    
    def get_packet_description(self, pkt):
        """获取数据包描述"""
        flags = pkt['flags']
        length = pkt['length']
        
        if flags == 2 or flags == 'S':
            return "SYN - 建立连接"
        elif flags == 18 or flags == 'SA':
            return "SYN-ACK - 响应连接"
        elif flags == 16 or flags == 'A':
            if length > 0:
                return f"数据传输 ({length} bytes)"
            else:
                return "纯ACK确认"
        elif isinstance(flags, int) and flags & 0x01:
            return "FIN - 关闭连接"
        elif length > 0:
            return f"数据传输 ({length} bytes)"
        else:
            return "控制包"

