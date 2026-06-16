"""
TCP拥塞控制可视化组件（拓展功能）
实现慢启动、拥塞避免、快速重传和快速恢复的可视化
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QTabWidget)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QRectF
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class CongestionControlWidget(QWidget):
    """拥塞控制组件"""
    
    def __init__(self):
        super().__init__()
        self.packets = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP拥塞控制机制分析")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 拥塞窗口演化
        cwnd_widget = QWidget()
        cwnd_layout = QVBoxLayout()
        cwnd_widget.setLayout(cwnd_layout)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.phase_label = QLabel("当前阶段: -")
        self.cwnd_label = QLabel("拥塞窗口: -")
        self.ssthresh_label = QLabel("慢启动阈值: -")
        
        stats_layout.addWidget(self.phase_label)
        stats_layout.addWidget(self.cwnd_label)
        stats_layout.addWidget(self.ssthresh_label)
        stats_layout.addStretch()
        
        cwnd_layout.addLayout(stats_layout)
        
        # 拥塞窗口图表
        self.cwnd_figure = Figure(figsize=(10, 6))
        self.cwnd_canvas = FigureCanvas(self.cwnd_figure)
        cwnd_layout.addWidget(self.cwnd_canvas)
        
        tab_widget.addTab(cwnd_widget, "📈 拥塞窗口演化")
        
        # 拥塞控制算法说明
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_widget.setLayout(info_layout)
        
        info_title = QLabel("TCP拥塞控制算法说明")
        info_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        info_layout.addWidget(info_title)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setHtml(self._get_congestion_info_html())
        info_layout.addWidget(self.info_text)
        
        tab_widget.addTab(info_widget, "📚 算法说明")
        
        # 性能分析
        perf_widget = QWidget()
        perf_layout = QVBoxLayout()
        perf_widget.setLayout(perf_layout)
        
        self.perf_figure = Figure(figsize=(10, 6))
        self.perf_canvas = FigureCanvas(self.perf_figure)
        perf_layout.addWidget(self.perf_canvas)
        
        tab_widget.addTab(perf_widget, "⚡ 性能分析")
        
        layout.addWidget(tab_widget)
    
    def update_view(self, packets):
        """更新视图"""
        if not packets:
            return
        
        self.packets = packets
        self.analyze_congestion_control()
        self.update_performance_analysis()
    
    def analyze_congestion_control(self):
        """分析拥塞控制"""
        if not self.packets:
            return
        
        # 估算拥塞窗口大小（基于窗口大小和数据传输模式）
        times = []
        estimated_cwnd = []
        windows = []
        
        start_time = self.packets[0]['time']
        
        # 简化的拥塞窗口估算
        current_cwnd = 1  # MSS
        ssthresh = 64  # 初始慢启动阈值
        
        data_packets_count = 0
        last_ack_time = start_time
        
        for pkt in self.packets:
            relative_time = pkt['time'] - start_time
            times.append(relative_time)
            windows.append(pkt['window'])
            
            # 简单的拥塞窗口模拟（基于数据包模式）
            if pkt['length'] > 0:
                data_packets_count += 1
                
                # 检测是否收到ACK（简化判断）
                if pkt['time'] - last_ack_time > 0.1:
                    if current_cwnd < ssthresh:
                        # 慢启动阶段：指数增长
                        current_cwnd *= 2
                    else:
                        # 拥塞避免阶段：线性增长
                        current_cwnd += 1
                    
                    last_ack_time = pkt['time']
                
                # 检测可能的超时（简化）
                if pkt['time'] - last_ack_time > 1.0:
                    ssthresh = max(current_cwnd / 2, 2)
                    current_cwnd = 1
            
            estimated_cwnd.append(min(current_cwnd, 100))  # 限制最大值
        
        # 更新统计信息
        if estimated_cwnd:
            current_cwnd_val = estimated_cwnd[-1]
            self.cwnd_label.setText(f"估算拥塞窗口: {current_cwnd_val:.0f} MSS")
            self.ssthresh_label.setText(f"慢启动阈值: {ssthresh:.0f} MSS")
            
            # 判断当前阶段
            if current_cwnd_val < ssthresh:
                phase = "慢启动 (Slow Start)"
            else:
                phase = "拥塞避免 (Congestion Avoidance)"
            self.phase_label.setText(f"当前阶段: {phase}")
        
        # 清空图表
        self.cwnd_figure.clear()
        
        # 创建子图
        ax1 = self.cwnd_figure.add_subplot(211)
        ax2 = self.cwnd_figure.add_subplot(212)
        
        # 绘制拥塞窗口估算
        ax1.plot(times, estimated_cwnd, 'b-', linewidth=2, label='估算拥塞窗口 (cwnd)')
        ax1.axhline(y=ssthresh, color='r', linestyle='--', linewidth=1.5, 
                   label=f'慢启动阈值 (ssthresh={ssthresh})')
        
        ax1.set_xlabel('时间 (秒)', fontsize=10, fontproperties='Microsoft YaHei')
        ax1.set_ylabel('拥塞窗口 (MSS)', fontsize=10, fontproperties='Microsoft YaHei')
        ax1.set_title('TCP拥塞窗口演化', fontsize=12, fontproperties='Microsoft YaHei', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
        
        # 填充不同阶段的背景色
        slow_start_region = [t for t, c in zip(times, estimated_cwnd) if c < ssthresh]
        if slow_start_region:
            ax1.axvspan(0, max(slow_start_region), alpha=0.2, color='blue', label='慢启动阶段')
        
        # 绘制接收窗口
        ax2.plot(times, windows, 'g-', linewidth=2, label='接收窗口 (rwnd)')
        ax2.set_xlabel('时间 (秒)', fontsize=10, fontproperties='Microsoft YaHei')
        ax2.set_ylabel('窗口大小 (bytes)', fontsize=10, fontproperties='Microsoft YaHei')
        ax2.set_title('TCP接收窗口变化', fontsize=12, fontproperties='Microsoft YaHei', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
        
        # 调整布局
        self.cwnd_figure.tight_layout()
        
        # 刷新画布
        self.cwnd_canvas.draw()
    
    def update_performance_analysis(self):
        """更新性能分析"""
        if not self.packets:
            return
        
        # 清空图表
        self.perf_figure.clear()
        
        # 创建子图
        ax = self.perf_figure.add_subplot(111)
        
        # 计算吞吐量随时间的变化
        time_windows = {}
        start_time = self.packets[0]['time']
        
        for pkt in self.packets:
            if pkt['length'] > 0:
                relative_time = pkt['time'] - start_time
                time_bin = int(relative_time * 10) / 10  # 100ms分辨率
                
                if time_bin not in time_windows:
                    time_windows[time_bin] = {'bytes': 0, 'packets': 0}
                
                time_windows[time_bin]['bytes'] += pkt['length']
                time_windows[time_bin]['packets'] += 1
        
        # 排序并转换
        if time_windows:
            times = sorted(time_windows.keys())
            throughputs = [time_windows[t]['bytes'] * 10 / 1024 for t in times]  # KB/s
            
            # 绘制吞吐量
            ax.plot(times, throughputs, 'b-', linewidth=2, label='瞬时吞吐量')
            
            # 绘制移动平均
            window_size = min(10, len(throughputs))
            if len(throughputs) >= window_size:
                moving_avg = np.convolve(throughputs, np.ones(window_size)/window_size, mode='valid')
                avg_times = times[window_size-1:]
                ax.plot(avg_times, moving_avg, 'r--', linewidth=2, label='移动平均')
            
            ax.set_xlabel('时间 (秒)', fontsize=11, fontproperties='Microsoft YaHei')
            ax.set_ylabel('吞吐量 (KB/s)', fontsize=11, fontproperties='Microsoft YaHei')
            ax.set_title('TCP吞吐量与拥塞控制关系', fontsize=12, 
                        fontproperties='Microsoft YaHei', fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
            
            # 标注峰值
            if throughputs:
                max_throughput = max(throughputs)
                max_idx = throughputs.index(max_throughput)
                ax.annotate(f'峰值: {max_throughput:.1f} KB/s', 
                           xy=(times[max_idx], max_throughput),
                           xytext=(times[max_idx] + 0.5, max_throughput + 5),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           fontproperties='Microsoft YaHei', fontsize=9)
        
        # 调整布局
        self.perf_figure.tight_layout()
        
        # 刷新画布
        self.perf_canvas.draw()
    
    def _get_congestion_info_html(self):
        """获取拥塞控制算法说明的HTML"""
        return """
        <html>
        <head>
            <style>
                body { font-family: "Microsoft YaHei"; font-size: 14px; line-height: 1.6; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }
                h3 { color: #4CAF50; margin-top: 15px; }
                .phase { background-color: #E3F2FD; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }
                .formula { background-color: #F5F5F5; padding: 8px; margin: 8px 0; font-family: monospace; }
            </style>
        </head>
        <body>
            <h2>TCP拥塞控制算法</h2>
            
            <div class="phase">
                <h3>1. 慢启动 (Slow Start)</h3>
                <p><strong>目标：</strong>快速探测网络可用带宽</p>
                <p><strong>机制：</strong>拥塞窗口(cwnd)从1个MSS开始，每收到一个ACK，cwnd增加1个MSS，实现指数增长</p>
                <div class="formula">cwnd(new) = cwnd(old) + MSS</div>
                <p><strong>终止条件：</strong>cwnd >= ssthresh 或检测到丢包</p>
            </div>
            
            <div class="phase">
                <h3>2. 拥塞避免 (Congestion Avoidance)</h3>
                <p><strong>目标：</strong>保持稳定的高吞吐量，避免网络拥塞</p>
                <p><strong>机制：</strong>每个RTT周期，cwnd增加1个MSS，实现线性增长</p>
                <div class="formula">cwnd(new) = cwnd(old) + MSS²/cwnd</div>
                <p><strong>触发：</strong>cwnd达到ssthresh阈值后进入此阶段</p>
            </div>
            
            <div class="phase">
                <h3>3. 快速重传 (Fast Retransmit)</h3>
                <p><strong>目标：</strong>快速检测和恢复单个数据包丢失</p>
                <p><strong>机制：</strong>收到3个重复ACK时，立即重传被确认丢失的数据包</p>
                <p><strong>优势：</strong>无需等待超时，减少恢复时间</p>
            </div>
            
            <div class="phase">
                <h3>4. 快速恢复 (Fast Recovery)</h3>
                <p><strong>目标：</strong>在快速重传后快速恢复传输速率</p>
                <p><strong>机制：</strong></p>
                <ul>
                    <li>设置 ssthresh = cwnd / 2</li>
                    <li>设置 cwnd = ssthresh + 3*MSS</li>
                    <li>每收到一个重复ACK，cwnd += 1 MSS</li>
                    <li>收到新ACK后，设置 cwnd = ssthresh</li>
                </ul>
            </div>
            
            <h3>关键参数</h3>
            <ul>
                <li><strong>cwnd (拥塞窗口)：</strong>发送方维护的窗口大小，限制未确认数据量</li>
                <li><strong>ssthresh (慢启动阈值)：</strong>区分慢启动和拥塞避免的阈值</li>
                <li><strong>rwnd (接收窗口)：</strong>接收方通告的可用缓冲区大小</li>
                <li><strong>有效窗口 = min(cwnd, rwnd)</strong></li>
            </ul>
            
            <h3>拥塞检测</h3>
            <ul>
                <li><strong>超时：</strong>RTO(重传超时)定时器到期，表示严重拥塞</li>
                <li><strong>重复ACK：</strong>收到3个重复ACK，表示轻微拥塞</li>
            </ul>
            
            <p style="margin-top: 20px; padding: 10px; background-color: #FFF3E0; border-left: 4px solid #FF9800;">
                <strong>注意：</strong>本工具通过分析数据包的窗口大小和传输模式来估算拥塞窗口的变化，
                实际的cwnd值由发送方维护，无法从接收到的数据包中直接获取。
            </p>
        </body>
        </html>
        """

