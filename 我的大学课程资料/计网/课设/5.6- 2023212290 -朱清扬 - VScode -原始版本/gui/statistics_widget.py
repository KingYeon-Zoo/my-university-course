"""
统计分析组件（扩展功能）
包括RTT分析、吞吐量分析等
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatisticsWidget(QWidget):
    """统计分析组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP连接统计分析")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 统计信息栏
        stats_layout = QHBoxLayout()
        
        self.total_packets_label = QLabel("总数据包: 0")
        self.total_bytes_label = QLabel("总字节数: 0")
        self.duration_label = QLabel("持续时间: 0s")
        self.throughput_label = QLabel("平均吞吐量: 0 KB/s")
        
        stats_layout.addWidget(self.total_packets_label)
        stats_layout.addWidget(self.total_bytes_label)
        stats_layout.addWidget(self.duration_label)
        stats_layout.addWidget(self.throughput_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # RTT分析标签页
        rtt_widget = QWidget()
        rtt_layout = QVBoxLayout()
        rtt_widget.setLayout(rtt_layout)
        
        self.rtt_figure = Figure(figsize=(8, 5))
        self.rtt_canvas = FigureCanvas(self.rtt_figure)
        rtt_layout.addWidget(self.rtt_canvas)
        
        # RTT统计信息
        self.rtt_stats_label = QLabel("RTT统计: -")
        rtt_layout.addWidget(self.rtt_stats_label)
        
        tab_widget.addTab(rtt_widget, "RTT分析")
        
        # 吞吐量分析标签页
        throughput_widget = QWidget()
        throughput_layout = QVBoxLayout()
        throughput_widget.setLayout(throughput_layout)
        
        self.throughput_figure = Figure(figsize=(8, 5))
        self.throughput_canvas = FigureCanvas(self.throughput_figure)
        throughput_layout.addWidget(self.throughput_canvas)
        
        tab_widget.addTab(throughput_widget, "吞吐量分析")
        
        # 数据包详情标签页
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        detail_widget.setLayout(detail_layout)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(7)
        self.detail_table.setHorizontalHeaderLabels([
            '序号', '时间(s)', '源地址', '目标地址', 'Seq', 'Ack', '长度(bytes)'
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        detail_layout.addWidget(self.detail_table)
        
        tab_widget.addTab(detail_widget, "数据包详情")
        
        layout.addWidget(tab_widget)
    
    def update_view(self, packets, rtt_data):
        """更新视图"""
        if not packets:
            return
        
        # 计算基本统计信息
        total_packets = len(packets)
        total_bytes = sum(pkt['length'] for pkt in packets)
        
        start_time = packets[0]['time']
        end_time = packets[-1]['time']
        duration = end_time - start_time
        
        throughput = (total_bytes / duration / 1024) if duration > 0 else 0  # KB/s
        
        self.total_packets_label.setText(f"总数据包: {total_packets}")
        self.total_bytes_label.setText(f"总字节数: {total_bytes}")
        self.duration_label.setText(f"持续时间: {duration:.2f}s")
        self.throughput_label.setText(f"平均吞吐量: {throughput:.2f} KB/s")
        
        # 更新RTT分析
        self.update_rtt_analysis(rtt_data, start_time)
        
        # 更新吞吐量分析
        self.update_throughput_analysis(packets, start_time)
        
        # 更新数据包详情表
        self.update_packet_details(packets, start_time)
    
    def update_rtt_analysis(self, rtt_data, start_time):
        """更新RTT分析"""
        if not rtt_data:
            self.rtt_stats_label.setText("RTT统计: 无数据")
            return
        
        # 计算RTT统计信息
        rtt_values = [d['rtt'] for d in rtt_data]
        min_rtt = min(rtt_values)
        max_rtt = max(rtt_values)
        avg_rtt = sum(rtt_values) / len(rtt_values)
        
        self.rtt_stats_label.setText(
            f"RTT统计: 最小={min_rtt:.2f}ms, 最大={max_rtt:.2f}ms, 平均={avg_rtt:.2f}ms"
        )
        
        # 清空图表
        self.rtt_figure.clear()
        
        # 创建子图
        ax1 = self.rtt_figure.add_subplot(211)
        ax2 = self.rtt_figure.add_subplot(212)
        
        # 提取时间和RTT值
        times = [(d['time'] - start_time) for d in rtt_data]
        rtts = [d['rtt'] for d in rtt_data]
        
        # 绘制RTT随时间变化
        ax1.plot(times, rtts, 'b.-', linewidth=1.5, markersize=3)
        ax1.set_xlabel('时间 (秒)', fontsize=10, fontproperties='Microsoft YaHei')
        ax1.set_ylabel('RTT (毫秒)', fontsize=10, fontproperties='Microsoft YaHei')
        ax1.set_title('RTT随时间变化', fontsize=11, fontproperties='Microsoft YaHei', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 添加平均线
        ax1.axhline(y=avg_rtt, color='r', linestyle='--', linewidth=1.5, label=f'平均RTT={avg_rtt:.2f}ms')
        ax1.legend(prop={'family': 'Microsoft YaHei', 'size': 8})
        
        # 绘制RTT分布直方图
        ax2.hist(rtts, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('RTT (毫秒)', fontsize=10, fontproperties='Microsoft YaHei')
        ax2.set_ylabel('频次', fontsize=10, fontproperties='Microsoft YaHei')
        ax2.set_title('RTT分布直方图', fontsize=11, fontproperties='Microsoft YaHei', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 调整布局
        self.rtt_figure.tight_layout()
        
        # 刷新画布
        self.rtt_canvas.draw()
    
    def update_throughput_analysis(self, packets, start_time):
        """更新吞吐量分析"""
        # 清空图表
        self.throughput_figure.clear()
        
        # 创建子图
        ax = self.throughput_figure.add_subplot(111)
        
        # 计算每秒的吞吐量
        time_intervals = {}
        
        for pkt in packets:
            if pkt['length'] > 0:  # 只统计有数据的包
                relative_time = pkt['time'] - start_time
                time_bin = int(relative_time)  # 按秒分组
                
                if time_bin not in time_intervals:
                    time_intervals[time_bin] = 0
                time_intervals[time_bin] += pkt['length']
        
        # 排序并转换为列表
        if time_intervals:
            times = sorted(time_intervals.keys())
            throughputs = [time_intervals[t] / 1024 for t in times]  # 转换为KB
            
            # 绘制吞吐量柱状图
            ax.bar(times, throughputs, width=0.8, color='#4CAF50', edgecolor='black', alpha=0.7)
            ax.set_xlabel('时间 (秒)', fontsize=11, fontproperties='Microsoft YaHei')
            ax.set_ylabel('吞吐量 (KB/s)', fontsize=11, fontproperties='Microsoft YaHei')
            ax.set_title('TCP吞吐量随时间变化', fontsize=12, fontproperties='Microsoft YaHei', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # 调整布局
            self.throughput_figure.tight_layout()
        
        # 刷新画布
        self.throughput_canvas.draw()
    
    def update_packet_details(self, packets, start_time):
        """更新数据包详情表"""
        # 只显示前100个包，避免表格过大
        display_packets = packets[:100]
        
        self.detail_table.setRowCount(len(display_packets))
        
        for i, pkt in enumerate(display_packets):
            relative_time = pkt['time'] - start_time
            
            self.detail_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.detail_table.setItem(i, 1, QTableWidgetItem(f"{relative_time:.6f}"))
            self.detail_table.setItem(i, 2, QTableWidgetItem(f"{pkt['src_ip']}:{pkt['src_port']}"))
            self.detail_table.setItem(i, 3, QTableWidgetItem(f"{pkt['dst_ip']}:{pkt['dst_port']}"))
            self.detail_table.setItem(i, 4, QTableWidgetItem(str(pkt['seq'])))
            self.detail_table.setItem(i, 5, QTableWidgetItem(str(pkt['ack'])))
            self.detail_table.setItem(i, 6, QTableWidgetItem(str(pkt['length'])))

