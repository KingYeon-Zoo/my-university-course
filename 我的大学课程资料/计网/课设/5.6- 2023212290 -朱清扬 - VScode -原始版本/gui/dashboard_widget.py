"""
性能仪表盘组件（拓展功能）
集成显示TCP连接的关键性能指标
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame, QProgressBar)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
import math


class GaugeWidget(QWidget):
    """仪表盘组件"""
    
    def __init__(self, title="", unit="", max_value=100):
        super().__init__()
        self.title = title
        self.unit = unit
        self.max_value = max_value
        self.current_value = 0
        self.setMinimumSize(200, 180)
    
    def set_value(self, value):
        """设置当前值"""
        self.current_value = min(value, self.max_value)
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height - 40
        
        # 绘制背景圆弧
        radius = min(width, height - 40) / 2 - 10
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 背景圆弧
        painter.setPen(QPen(QColor(220, 220, 220), 15, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 180 * 16, 180 * 16)
        
        # 数值圆弧
        if self.current_value > 0:
            progress = self.current_value / self.max_value
            angle = int(progress * 180 * 16)
            
            # 根据进度选择颜色
            if progress < 0.5:
                color = QColor(76, 175, 80)  # 绿色
            elif progress < 0.75:
                color = QColor(255, 193, 7)  # 黄色
            else:
                color = QColor(244, 67, 54)  # 红色
            
            painter.setPen(QPen(color, 15, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(rect, 180 * 16, angle)
        
        # 绘制中心值
        painter.setPen(QColor(50, 50, 50))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        
        value_text = f"{self.current_value:.1f}"
        text_rect = QRectF(0, center_y - 30, width, 30)
        painter.drawText(text_rect, Qt.AlignCenter, value_text)
        
        # 绘制单位
        painter.setFont(QFont("Microsoft YaHei", 10))
        unit_rect = QRectF(0, center_y, width, 20)
        painter.drawText(unit_rect, Qt.AlignCenter, self.unit)
        
        # 绘制标题
        painter.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title_rect = QRectF(0, 10, width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)


class MetricCard(QFrame):
    """指标卡片"""
    
    def __init__(self, title, icon=""):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 数值
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(self.value_label)
        
        # 副标题
        self.subtitle_label = QLabel("")
        self.subtitle_label.setFont(QFont("Microsoft YaHei", 8))
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #666;")
        layout.addWidget(self.subtitle_label)
        
        self.setMinimumHeight(120)
    
    def set_value(self, value, subtitle=""):
        """设置数值"""
        self.value_label.setText(str(value))
        if subtitle:
            self.subtitle_label.setText(subtitle)


class DashboardWidget(QWidget):
    """性能仪表盘组件"""
    
    def __init__(self):
        super().__init__()
        self.packets = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 标题
        title = QLabel("TCP连接性能仪表盘")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 仪表盘区域
        gauges_layout = QHBoxLayout()
        
        self.throughput_gauge = GaugeWidget("吞吐量", "KB/s", 1000)
        gauges_layout.addWidget(self.throughput_gauge)
        
        self.rtt_gauge = GaugeWidget("平均RTT", "ms", 500)
        gauges_layout.addWidget(self.rtt_gauge)
        
        self.loss_gauge = GaugeWidget("丢包率", "%", 100)
        gauges_layout.addWidget(self.loss_gauge)
        
        layout.addLayout(gauges_layout)
        
        # 指标卡片区域
        cards_grid = QGridLayout()
        
        self.total_packets_card = MetricCard("总数据包", "📦")
        cards_grid.addWidget(self.total_packets_card, 0, 0)
        
        self.total_bytes_card = MetricCard("总字节数", "💾")
        cards_grid.addWidget(self.total_bytes_card, 0, 1)
        
        self.duration_card = MetricCard("连接时长", "⏱")
        cards_grid.addWidget(self.duration_card, 0, 2)
        
        self.retrans_card = MetricCard("重传次数", "🔄")
        cards_grid.addWidget(self.retrans_card, 0, 3)
        
        self.data_packets_card = MetricCard("数据包数", "📊")
        cards_grid.addWidget(self.data_packets_card, 1, 0)
        
        self.ack_packets_card = MetricCard("ACK包数", "✓")
        cards_grid.addWidget(self.ack_packets_card, 1, 1)
        
        self.avg_window_card = MetricCard("平均窗口", "🪟")
        cards_grid.addWidget(self.avg_window_card, 1, 2)
        
        self.max_window_card = MetricCard("最大窗口", "📈")
        cards_grid.addWidget(self.max_window_card, 1, 3)
        
        layout.addLayout(cards_grid)
        
        # 健康状态条
        health_layout = QVBoxLayout()
        
        health_label = QLabel("连接健康状态:")
        health_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        health_layout.addWidget(health_label)
        
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setValue(100)
        self.health_bar.setTextVisible(True)
        self.health_bar.setFormat("健康度: %p%")
        self.health_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.5 #8BC34A, stop:1 #4CAF50);
                border-radius: 3px;
            }
        """)
        health_layout.addWidget(self.health_bar)
        
        self.health_desc_label = QLabel("连接状态良好")
        self.health_desc_label.setFont(QFont("Microsoft YaHei", 9))
        self.health_desc_label.setAlignment(Qt.AlignCenter)
        health_layout.addWidget(self.health_desc_label)
        
        layout.addLayout(health_layout)
        
        # 添加弹性空间
        layout.addStretch()
    
    def update_view(self, packets, rtt_data=None, retransmissions=None):
        """更新视图"""
        if not packets:
            return
        
        self.packets = packets
        
        # 计算基本统计
        total_packets = len(packets)
        total_bytes = sum(pkt['length'] for pkt in packets)
        data_packets = sum(1 for pkt in packets if pkt['length'] > 0)
        ack_packets = total_packets - data_packets
        
        start_time = packets[0]['time']
        end_time = packets[-1]['time']
        duration = end_time - start_time
        
        # 窗口统计
        windows = [pkt['window'] for pkt in packets]
        avg_window = sum(windows) / len(windows) if windows else 0
        max_window = max(windows) if windows else 0
        
        # 吞吐量
        throughput_kbps = (total_bytes / duration / 1024) if duration > 0 else 0
        
        # 重传统计
        retrans_count = len(retransmissions) if retransmissions else 0
        
        # RTT统计
        avg_rtt = 0
        if rtt_data:
            rtt_values = [d['rtt'] for d in rtt_data]
            avg_rtt = sum(rtt_values) / len(rtt_values) if rtt_values else 0
        
        # 丢包率估算（基于重传）
        loss_rate = (retrans_count / total_packets * 100) if total_packets > 0 else 0
        
        # 更新仪表盘
        self.throughput_gauge.set_value(throughput_kbps)
        self.rtt_gauge.set_value(avg_rtt)
        self.loss_gauge.set_value(loss_rate)
        
        # 更新卡片
        self.total_packets_card.set_value(total_packets)
        self.total_bytes_card.set_value(f"{total_bytes / 1024:.1f} KB")
        self.duration_card.set_value(f"{duration:.2f} s")
        self.retrans_card.set_value(retrans_count, 
                                    f"{loss_rate:.2f}% 丢包率" if retrans_count > 0 else "无重传")
        
        self.data_packets_card.set_value(data_packets, 
                                        f"{data_packets/total_packets*100:.1f}% 比例")
        self.ack_packets_card.set_value(ack_packets,
                                       f"{ack_packets/total_packets*100:.1f}% 比例")
        self.avg_window_card.set_value(f"{avg_window:.0f} B")
        self.max_window_card.set_value(f"{max_window} B")
        
        # 计算健康分数
        health_score = self.calculate_health_score(
            throughput_kbps, avg_rtt, loss_rate, duration
        )
        
        self.health_bar.setValue(int(health_score))
        
        # 更新健康描述和颜色
        if health_score >= 80:
            status_text = "连接状态优秀"
            color_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4CAF50, stop:0.5 #8BC34A, stop:1 #4CAF50);
                }
            """
        elif health_score >= 60:
            status_text = "连接状态良好"
            color_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8BC34A, stop:0.5 #CDDC39, stop:1 #8BC34A);
                }
            """
        elif health_score >= 40:
            status_text = "连接状态一般，存在性能问题"
            color_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF9800, stop:0.5 #FFC107, stop:1 #FF9800);
                }
            """
        else:
            status_text = "连接状态较差，建议检查网络"
            color_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F44336, stop:0.5 #E91E63, stop:1 #F44336);
                }
            """
        
        self.health_desc_label.setText(status_text)
        
        # 更新进度条样式
        current_style = self.health_bar.styleSheet()
        base_style = current_style.split("QProgressBar::chunk")[0]
        self.health_bar.setStyleSheet(base_style + color_style)
    
    def calculate_health_score(self, throughput, rtt, loss_rate, duration):
        """计算连接健康分数（0-100）"""
        score = 100
        
        # RTT惩罚（RTT越高，扣分越多）
        if rtt > 0:
            if rtt > 200:
                score -= 30
            elif rtt > 100:
                score -= 20
            elif rtt > 50:
                score -= 10
        
        # 丢包率惩罚
        if loss_rate > 10:
            score -= 40
        elif loss_rate > 5:
            score -= 25
        elif loss_rate > 1:
            score -= 10
        
        # 吞吐量奖励（相对的）
        if throughput > 500:
            score += 0  # 已经很好
        elif throughput > 100:
            score -= 5
        elif throughput > 10:
            score -= 10
        else:
            score -= 15
        
        # 连接时长（过短可能不稳定）
        if duration < 1:
            score -= 10
        
        return max(0, min(100, score))

