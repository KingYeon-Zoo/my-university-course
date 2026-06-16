"""
数据包解析模块
用于解析pcapng文件并提取TCP连接信息
"""

from scapy.all import rdpcap, TCP, IP
from collections import defaultdict
import pandas as pd


class PacketParser:
    """数据包解析器"""
    
    def __init__(self):
        self.packets = []
        self.tcp_connections = {}
        self.connection_list = []
        
    def load_pcap(self, filename):
        """
        加载pcapng文件
        :param filename: 文件路径
        :return: 是否成功加载
        """
        try:
            self.packets = rdpcap(filename) # 读取pcapng文件，并且将数据包存储在self.packets中
            print(f"成功加载 {len(self.packets)} 个数据包")
            self._extract_tcp_connections()
            return True
        except Exception as e:
            print(f"加载文件失败: {e}")
            return False
    
    def _extract_tcp_connections(self):
        """提取TCP连接"""
        # 用于存储每个连接的数据包
        conn_packets = defaultdict(list)
        
        for idx, pkt in enumerate(self.packets):
            if TCP in pkt and IP in pkt: # 判断数据包是否为TCP数据包
                # 获取连接的四元组信息
                src_ip = pkt[IP].src # 源IP地址
                dst_ip = pkt[IP].dst # 目的IP地址
                src_port = pkt[TCP].sport # 源端口
                dst_port = pkt[TCP].dport # 目的端口
                
                # 创建连接标识（规范化：较小的IP:Port在前）
                if (src_ip, src_port) < (dst_ip, dst_port):
                    conn_id = f"{src_ip}:{src_port} <-> {dst_ip}:{dst_port}"
                else:
                    conn_id = f"{dst_ip}:{dst_port} <-> {src_ip}:{src_port}"
                
                # 存储数据包信息
                packet_info = {
                    'index': idx,
                    'time': float(pkt.time),
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'seq': pkt[TCP].seq,
                    'ack': pkt[TCP].ack,
                    'flags': pkt[TCP].flags,
                    'window': pkt[TCP].window,
                    'length': len(pkt[TCP].payload) if pkt[TCP].payload else 0,
                    'packet': pkt
                }
                
                conn_packets[conn_id].append(packet_info)
        
        # 将连接信息转换为更易用的格式
        self.tcp_connections = {}
        self.connection_list = []
        
        for conn_id, packets in conn_packets.items():
            if len(packets) > 0:  # 只保留有数据包的连接
                self.tcp_connections[conn_id] = packets
                # 提取连接的起止时间
                start_time = min(p['time'] for p in packets)
                end_time = max(p['time'] for p in packets)
                
                self.connection_list.append({
                    'id': conn_id,
                    'packet_count': len(packets),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time
                })
        
        print(f"识别出 {len(self.tcp_connections)} 个TCP连接")
    
    def get_connection_list(self):
        """获取所有TCP连接的列表"""
        return self.connection_list
    
    def get_connection_packets(self, conn_id):
        """获取指定连接的所有数据包"""
        return self.tcp_connections.get(conn_id, [])
    
    def analyze_handshake(self, conn_id):
        """
        分析TCP三次握手
        :param conn_id: 连接ID
        :return: 握手信息
        """
        packets = self.get_connection_packets(conn_id)
        if len(packets) < 3:
            return None
        
        # 查找SYN、SYN-ACK、ACK
        syn_packet = None
        syn_ack_packet = None
        ack_packet = None
        
        for pkt in packets[:10]:  # 只在前10个包中查找
            flags = pkt['flags']
            
            # SYN (flags = 2 or 'S')
            if flags == 2 or flags == 'S':
                if syn_packet is None:
                    syn_packet = pkt
            # SYN-ACK (flags = 18 or 'SA')
            elif flags == 18 or flags == 'SA':
                if syn_ack_packet is None:
                    syn_ack_packet = pkt
            # ACK (flags = 16 or 'A')
            elif flags == 16 or flags == 'A':
                if syn_packet and syn_ack_packet and ack_packet is None:
                    ack_packet = pkt
        
        if syn_packet and syn_ack_packet and ack_packet:
            return {
                'syn': syn_packet,
                'syn_ack': syn_ack_packet,
                'ack': ack_packet,
                'complete': True
            }
        
        return None
    
    def analyze_fin(self, conn_id):
        """
        分析TCP四次挥手
        :param conn_id: 连接ID
        :return: 挥手信息
        """
        packets = self.get_connection_packets(conn_id)
        
        # 查找FIN包
        fin_packets = []
        for pkt in packets:
            flags = pkt['flags']
            # FIN (flags包含FIN标志: 1, 17, 25等)
            if isinstance(flags, int):
                if flags & 0x01:  # FIN标志位
                    fin_packets.append(pkt)
            elif 'F' in str(flags):
                fin_packets.append(pkt)
        
        if len(fin_packets) >= 2:
            return {
                'fin_packets': fin_packets,
                'complete': True
            }
        
        return None
    
    def detect_retransmission(self, conn_id):
        """
        检测重传
        :param conn_id: 连接ID
        :return: 重传信息列表
        """
        packets = self.get_connection_packets(conn_id)
        retransmissions = []
        
        # 按方向分组
        direction_seqs = defaultdict(list)
        
        for pkt in packets:
            direction = f"{pkt['src_ip']}:{pkt['src_port']}->{pkt['dst_ip']}:{pkt['dst_port']}"
            if pkt['length'] > 0:  # 只考虑有数据的包
                direction_seqs[direction].append(pkt)
        
        # 检测每个方向的重传
        for direction, pkts in direction_seqs.items():
            seen_seqs = {}
            for pkt in pkts:
                seq = pkt['seq']
                if seq in seen_seqs:
                    # 发现重传
                    retransmissions.append({
                        'original': seen_seqs[seq],
                        'retransmit': pkt,
                        'direction': direction
                    })
                else:
                    seen_seqs[seq] = pkt
        
        return retransmissions
    
    def get_window_evolution(self, conn_id):
        """
        获取窗口大小变化
        :param conn_id: 连接ID
        :return: 窗口变化数据
        """
        packets = self.get_connection_packets(conn_id)
        
        window_data = []
        for pkt in packets:
            window_data.append({
                'time': pkt['time'],
                'window': pkt['window'],
                'direction': f"{pkt['src_ip']}:{pkt['src_port']}"
            })
        
        return window_data
    
    def calculate_rtt(self, conn_id):
        """
        计算RTT (往返时延)
        :param conn_id: 连接ID
        :return: RTT数据
        """
        packets = self.get_connection_packets(conn_id)
        rtt_data = []
        
        # 存储每个序列号的发送时间
        seq_times = {}
        
        for pkt in packets:
            # 记录发送数据包的时间
            if pkt['length'] > 0:
                seq_times[pkt['seq']] = pkt['time']
            
            # 如果是ACK包，计算RTT
            if pkt['ack'] > 0:
                # 查找对应的数据包
                for seq, send_time in seq_times.items():
                    if seq < pkt['ack']:
                        rtt = (pkt['time'] - send_time) * 1000  # 转换为毫秒
                        if rtt > 0 and rtt < 10000:  # 过滤异常值
                            rtt_data.append({
                                'time': pkt['time'],
                                'rtt': rtt
                            })
        
        return rtt_data

