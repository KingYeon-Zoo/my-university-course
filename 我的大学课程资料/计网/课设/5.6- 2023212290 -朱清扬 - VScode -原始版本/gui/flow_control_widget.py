"""
流量控制（滑动窗口）可视化组件
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class FlowControlWidget(QWidget):
    """流量控制组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP流量控制 - 滑动窗口机制")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        self.min_window_label = QLabel("最小窗口: - ")
        self.max_window_label = QLabel("最大窗口: - ")
        self.avg_window_label = QLabel("平均窗口: - ")
        
        stats_layout.addWidget(self.min_window_label)
        stats_layout.addWidget(self.max_window_label)
        stats_layout.addWidget(self.avg_window_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # 创建matplotlib图表
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def update_view(self, window_data):
        """更新视图"""
        if not window_data:
            return
        
        # 提取数据
        times = []
        windows = []
        directions = {}
        
        start_time = window_data[0]['time']
        
        for data in window_data:
            relative_time = data['time'] - start_time
            times.append(relative_time)
            windows.append(data['window'])
            
            direction = data['direction']
            if direction not in directions:
                directions[direction] = {'times': [], 'windows': []}
            directions[direction]['times'].append(relative_time)
            directions[direction]['windows'].append(data['window'])
        
        # 计算统计信息
        if windows:
            min_window = min(windows)
            max_window = max(windows)
            avg_window = sum(windows) / len(windows)
            
            self.min_window_label.setText(f"最小窗口: {min_window} bytes")
            self.max_window_label.setText(f"最大窗口: {max_window} bytes")
            self.avg_window_label.setText(f"平均窗口: {avg_window:.0f} bytes")
        
        # 清空图表
        self.figure.clear()
        
        # 创建子图
        ax = self.figure.add_subplot(111)
        
        # 如果有多个方向，分别绘制
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for idx, (direction, data) in enumerate(directions.items()):
            color = colors[idx % len(colors)]
            # 提取IP地址作为标签
            label = direction.split(':')[0]  # 只显示IP
            ax.plot(data['times'], data['windows'], '.-', 
                   label=f'{label}', color=color, linewidth=2, markersize=4)
        
        ax.set_xlabel('时间 (秒)', fontsize=11, fontproperties='Microsoft YaHei')
        ax.set_ylabel('窗口大小 (bytes)', fontsize=11, fontproperties='Microsoft YaHei')
        ax.set_title('TCP接收窗口大小变化', fontsize=13, fontproperties='Microsoft YaHei', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if len(directions) > 1:
            ax.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
        
        # 添加零窗口标记
        zero_windows = [(t, w) for t, w in zip(times, windows) if w == 0]
        if zero_windows:
            zero_times = [t for t, w in zero_windows]
            zero_vals = [0 for t, w in zero_windows]
            ax.plot(zero_times, zero_vals, 'ro', markersize=8, 
                   label='零窗口', zorder=10)
            ax.legend(prop={'family': 'Microsoft YaHei', 'size': 9})
        
        # 调整布局
        self.figure.tight_layout()
        
        # 刷新画布
        self.canvas.draw()

