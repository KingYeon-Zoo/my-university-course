"""
主窗口模块
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QTabWidget, QFileDialog,
                             QLabel, QSplitter, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from packet_parser import PacketParser
from gui.handshake_widget import HandshakeWidget
from gui.sequence_widget import SequenceWidget
from gui.retransmit_widget import RetransmitWidget
from gui.flow_control_widget import FlowControlWidget
from gui.statistics_widget import StatisticsWidget
from gui.congestion_widget import CongestionControlWidget
from gui.state_machine_widget import TCPStateMachineWidget
from gui.dashboard_widget import DashboardWidget


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.parser = PacketParser()
        self.current_connection = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("TCP协议可视化分析工具 - 合肥工业大学")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 标题
        title_label = QLabel("TCP协议可视化分析工具")
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📁 加载文件")
        self.load_btn.setFixedSize(120, 35)
        self.load_btn.clicked.connect(self.load_file)
        toolbar_layout.addWidget(self.load_btn)
        
        self.export_btn = QPushButton("💾 导出报告")
        self.export_btn.setFixedSize(120, 35)
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)  # 初始禁用
        toolbar_layout.addWidget(self.export_btn)
        
        self.file_label = QLabel("未加载文件")
        toolbar_layout.addWidget(self.file_label)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 分割器（左侧连接列表，右侧详细信息）
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：连接列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        conn_label = QLabel("TCP连接列表")
        conn_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        left_layout.addWidget(conn_label)
        
        self.connection_list = QListWidget()
        self.connection_list.itemClicked.connect(self.on_connection_selected)
        left_layout.addWidget(self.connection_list)
        
        splitter.addWidget(left_widget)
        
        # 右侧：标签页
        self.tab_widget = QTabWidget()
        
        # 创建各个标签页
        self.dashboard_widget = DashboardWidget()
        self.handshake_widget = HandshakeWidget()
        self.sequence_widget = SequenceWidget()
        self.retransmit_widget = RetransmitWidget()
        self.flow_control_widget = FlowControlWidget()
        self.congestion_widget = CongestionControlWidget()
        self.state_machine_widget = TCPStateMachineWidget()
        self.statistics_widget = StatisticsWidget()
        
        self.tab_widget.addTab(self.dashboard_widget, "🎯 性能仪表盘")
        self.tab_widget.addTab(self.handshake_widget, "🤝 连接建立/释放")
        self.tab_widget.addTab(self.sequence_widget, "📊 序列号分析")
        self.tab_widget.addTab(self.retransmit_widget, "🔄 重传分析")
        self.tab_widget.addTab(self.flow_control_widget, "📈 流量控制")
        self.tab_widget.addTab(self.congestion_widget, "🚦 拥塞控制")
        self.tab_widget.addTab(self.state_machine_widget, "🔄 状态机")
        self.tab_widget.addTab(self.statistics_widget, "📉 统计分析")
        
        splitter.addWidget(self.tab_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 应用样式
        self.apply_styles()
    
    def apply_styles(self):
        """应用样式"""
        # qt-material主题已经在main.py中应用，这里只添加少量自定义样式
        self.setStyleSheet("""
            QLabel#title {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton {
                font-size: 13px;
                padding: 10px;
                min-width: 100px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
        """)
    
    def load_file(self):
        """加载pcapng文件"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据包文件",
            "",
            "PCAP文件 (*.pcap *.pcapng);;所有文件 (*.*)"
        )
        
        if filename:
            self.statusBar.showMessage("正在加载文件...")
            
            if self.parser.load_pcap(filename):
                self.file_label.setText(f"已加载: {filename}")
                self.update_connection_list()
                self.export_btn.setEnabled(True)  # 启用导出按钮
                self.statusBar.showMessage(f"成功加载 {len(self.parser.packets)} 个数据包")
                
                QMessageBox.information(
                    self,
                    "加载成功",
                    f"成功加载 {len(self.parser.packets)} 个数据包\n"
                    f"识别出 {len(self.parser.connection_list)} 个TCP连接"
                )
            else:
                self.statusBar.showMessage("加载文件失败")
                QMessageBox.critical(self, "错误", "加载文件失败！")
    
    def update_connection_list(self):
        """更新连接列表"""
        self.connection_list.clear()
        
        for conn in self.parser.get_connection_list():
            item_text = (f"{conn['id']}\n"
                        f"  数据包: {conn['packet_count']} 个 | "
                        f"持续时间: {conn['duration']:.2f} 秒")
            self.connection_list.addItem(item_text)
    
    def on_connection_selected(self, item):
        """当选择连接时"""
        # 获取选中的连接ID（从第一行提取）
        item_text = item.text()
        conn_id = item_text.split('\n')[0]
        
        self.current_connection = conn_id
        self.statusBar.showMessage(f"分析连接: {conn_id}")
        
        # 更新各个视图
        self.update_all_views(conn_id)
    
    def update_all_views(self, conn_id):
        """更新所有视图"""
        # 获取数据包
        packets = self.parser.get_connection_packets(conn_id)
        
        # 获取分析数据
        handshake_info = self.parser.analyze_handshake(conn_id)
        fin_info = self.parser.analyze_fin(conn_id)
        retransmissions = self.parser.detect_retransmission(conn_id)
        window_data = self.parser.get_window_evolution(conn_id)
        rtt_data = self.parser.calculate_rtt(conn_id)
        
        # 更新性能仪表盘（新增）
        self.dashboard_widget.update_view(packets, rtt_data, retransmissions)
        
        # 更新握手视图
        self.handshake_widget.update_view(handshake_info, fin_info)
        
        # 更新序列号视图
        self.sequence_widget.update_view(packets)
        
        # 更新重传视图
        self.retransmit_widget.update_view(packets, retransmissions)
        
        # 更新流量控制视图
        self.flow_control_widget.update_view(window_data)
        
        # 更新拥塞控制视图（新增）
        self.congestion_widget.update_view(packets)
        
        # 更新状态机视图（新增）
        self.state_machine_widget.update_view(packets)
        
        # 更新统计视图
        self.statistics_widget.update_view(packets, rtt_data)
    
    def export_report(self):
        """导出分析报告"""
        if not self.current_connection:
            QMessageBox.warning(self, "警告", "请先选择一个TCP连接")
            return
        
        # 选择保存位置
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出分析报告",
            f"TCP_分析报告_{self.current_connection.replace(':', '_').replace(' ', '_')}.html",
            "HTML文件 (*.html);;所有文件 (*.*)"
        )
        
        if filename:
            try:
                self.statusBar.showMessage("正在生成报告...")
                self._generate_html_report(filename)
                self.statusBar.showMessage(f"报告已导出到: {filename}")
                QMessageBox.information(self, "成功", f"分析报告已成功导出到:\n{filename}")
            except Exception as e:
                self.statusBar.showMessage("导出报告失败")
                QMessageBox.critical(self, "错误", f"导出报告失败:\n{str(e)}")
    
    def _generate_html_report(self, filename):
        """生成HTML报告"""
        import datetime
        
        # 获取当前连接的数据
        packets = self.parser.get_connection_packets(self.current_connection)
        handshake_info = self.parser.analyze_handshake(self.current_connection)
        fin_info = self.parser.analyze_fin(self.current_connection)
        retransmissions = self.parser.detect_retransmission(self.current_connection)
        window_data = self.parser.get_window_evolution(self.current_connection)
        rtt_data = self.parser.calculate_rtt(self.current_connection)
        
        # 计算统计数据
        total_packets = len(packets)
        total_bytes = sum(pkt['length'] for pkt in packets)
        data_packets = sum(1 for pkt in packets if pkt['length'] > 0)
        
        start_time = packets[0]['time']
        end_time = packets[-1]['time']
        duration = end_time - start_time
        throughput = (total_bytes / duration / 1024) if duration > 0 else 0
        
        windows = [pkt['window'] for pkt in packets]
        avg_window = sum(windows) / len(windows) if windows else 0
        max_window = max(windows) if windows else 0
        
        avg_rtt = 0
        if rtt_data:
            rtt_values = [d['rtt'] for d in rtt_data]
            avg_rtt = sum(rtt_values) / len(rtt_values) if rtt_values else 0
        
        # 生成HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TCP连接分析报告</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .metric-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        .metric-card .subtitle {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
        .good {{ color: #4CAF50; font-weight: bold; }}
        .warning {{ color: #FF9800; font-weight: bold; }}
        .bad {{ color: #F44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 TCP连接分析报告</h1>
        <p>连接: {self.current_connection}</p>
        <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>📈 性能概览</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>总数据包数</h3>
                <p class="value">{total_packets}</p>
                <p class="subtitle">数据包: {data_packets} | ACK: {total_packets - data_packets}</p>
            </div>
            <div class="metric-card">
                <h3>总字节数</h3>
                <p class="value">{total_bytes / 1024:.2f} KB</p>
                <p class="subtitle">{total_bytes} bytes</p>
            </div>
            <div class="metric-card">
                <h3>连接时长</h3>
                <p class="value">{duration:.2f} s</p>
                <p class="subtitle">持续时间</p>
            </div>
            <div class="metric-card">
                <h3>平均吞吐量</h3>
                <p class="value">{throughput:.2f} KB/s</p>
                <p class="subtitle">数据传输速率</p>
            </div>
            <div class="metric-card">
                <h3>平均RTT</h3>
                <p class="value">{avg_rtt:.2f} ms</p>
                <p class="subtitle">往返时延</p>
            </div>
            <div class="metric-card">
                <h3>重传次数</h3>
                <p class="value">{len(retransmissions)}</p>
                <p class="subtitle">{len(retransmissions)/total_packets*100:.2f}% 比例</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🤝 连接建立信息</h2>
        {"<p class='good'>✓ 检测到完整的三次握手过程</p>" if handshake_info and handshake_info.get('complete') else "<p class='warning'>⚠ 未检测到完整的三次握手</p>"}
        {self._generate_handshake_table(handshake_info) if handshake_info and handshake_info.get('complete') else ""}
    </div>

    <div class="section">
        <h2>🔄 重传分析</h2>
        {f"<p class='good'>✓ 未检测到重传</p>" if len(retransmissions) == 0 else f"<p class='warning'>⚠ 检测到 {len(retransmissions)} 次重传</p>"}
        {self._generate_retrans_table(retransmissions) if len(retransmissions) > 0 else ""}
    </div>

    <div class="section">
        <h2>📊 窗口控制</h2>
        <p>平均窗口大小: <strong>{avg_window:.0f} bytes</strong></p>
        <p>最大窗口大小: <strong>{max_window} bytes</strong></p>
    </div>

    <div class="section">
        <h2>📋 数据包详情（前50个）</h2>
        {self._generate_packets_table(packets[:50], start_time)}
    </div>

    <div class="footer">
        <p>由 TCP协议可视化分析工具 生成</p>
        <p>合肥工业大学 | 作者: 朱清扬 (2023212290)</p>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_handshake_table(self, handshake_info):
        """生成握手表格"""
        if not handshake_info or not handshake_info.get('complete'):
            return ""
        
        syn = handshake_info['syn']
        syn_ack = handshake_info['syn_ack']
        ack = handshake_info['ack']
        
        return f"""
        <table>
            <tr>
                <th>步骤</th>
                <th>源地址</th>
                <th>目标地址</th>
                <th>序列号</th>
                <th>确认号</th>
                <th>标志</th>
            </tr>
            <tr>
                <td>1. SYN</td>
                <td>{syn['src_ip']}:{syn['src_port']}</td>
                <td>{syn['dst_ip']}:{syn['dst_port']}</td>
                <td>{syn['seq']}</td>
                <td>-</td>
                <td>SYN</td>
            </tr>
            <tr>
                <td>2. SYN-ACK</td>
                <td>{syn_ack['src_ip']}:{syn_ack['src_port']}</td>
                <td>{syn_ack['dst_ip']}:{syn_ack['dst_port']}</td>
                <td>{syn_ack['seq']}</td>
                <td>{syn_ack['ack']}</td>
                <td>SYN-ACK</td>
            </tr>
            <tr>
                <td>3. ACK</td>
                <td>{ack['src_ip']}:{ack['src_port']}</td>
                <td>{ack['dst_ip']}:{ack['dst_port']}</td>
                <td>{ack['seq']}</td>
                <td>{ack['ack']}</td>
                <td>ACK</td>
            </tr>
        </table>
        """
    
    def _generate_retrans_table(self, retransmissions):
        """生成重传表格"""
        if not retransmissions:
            return ""
        
        rows = ""
        for i, retrans in enumerate(retransmissions[:20]):  # 只显示前20个
            orig = retrans['original']
            retrans_pkt = retrans['retransmit']
            time_diff = (retrans_pkt['time'] - orig['time']) * 1000
            
            rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{orig['seq']}</td>
                <td>{orig['time']:.6f}</td>
                <td>{retrans_pkt['time']:.6f}</td>
                <td>{time_diff:.2f} ms</td>
            </tr>
            """
        
        return f"""
        <table>
            <tr>
                <th>序号</th>
                <th>序列号</th>
                <th>原始时间</th>
                <th>重传时间</th>
                <th>时间差</th>
            </tr>
            {rows}
        </table>
        """
    
    def _generate_packets_table(self, packets, start_time):
        """生成数据包表格"""
        if not packets:
            return ""
        
        rows = ""
        for i, pkt in enumerate(packets):
            relative_time = pkt['time'] - start_time
            rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{relative_time:.6f}</td>
                <td>{pkt['src_ip']}:{pkt['src_port']}</td>
                <td>{pkt['dst_ip']}:{pkt['dst_port']}</td>
                <td>{pkt['seq']}</td>
                <td>{pkt['ack'] if pkt['ack'] > 0 else '-'}</td>
                <td>{pkt['length']}</td>
                <td>{pkt['window']}</td>
            </tr>
            """
        
        return f"""
        <table>
            <tr>
                <th>序号</th>
                <th>相对时间(s)</th>
                <th>源地址</th>
                <th>目标地址</th>
                <th>序列号</th>
                <th>确认号</th>
                <th>数据长度</th>
                <th>窗口大小</th>
            </tr>
            {rows}
        </table>
        """

