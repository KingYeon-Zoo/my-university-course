# RTT计算算法 - 算法实现逻辑

## 一、RTT概述

**RTT（Round-Trip Time，往返时延）**是TCP性能的关键指标，表示数据包从发送到收到确认的时间间隔。RTT用于：

1. 计算**重传超时时间（RTO）**
2. 评估**网络延迟**
3. 优化**拥塞控制**策略

## 二、RTT计算原理

### 2.1 RTT测量示意图

```
发送方                               接收方
   │                                  │
   │ t1 ─────── 数据包 Seq=N ────────>│
   │                                  │
   │                                  │ t2 (接收)
   │                                  │
   │<─────── ACK Ack=N+len ────────── │ t3 (发送ACK)
   │ t4                               │
   │                                  │

RTT = t4 - t1 = 传播时延×2 + 处理时延×2 + 排队时延×2 + 传输时延
```

### 2.2 RTT的组成

```
RTT = 2×(传播时延 + 传输时延 + 处理时延 + 排队时延)

详细分解:
┌───────────────────────────────────────────────────────┐
│ 传播时延（Propagation Delay）                         │
│ = 物理距离 / 信号传播速度                              │
│ 示例: 北京到上海约1000km，光纤中 ≈ 5ms                │
├───────────────────────────────────────────────────────┤
│ 传输时延（Transmission Delay）                        │
│ = 数据包大小 / 链路带宽                               │
│ 示例: 1500B / 100Mbps = 0.12ms                       │
├───────────────────────────────────────────────────────┤
│ 处理时延（Processing Delay）                          │
│ = 路由器/主机处理数据包的时间                          │
│ 通常: 微秒级                                          │
├───────────────────────────────────────────────────────┤
│ 排队时延（Queuing Delay）                             │
│ = 在路由器队列中等待的时间                             │
│ 高负载时: 可能很大                                    │
└───────────────────────────────────────────────────────┘
```

## 三、算法实现详解

### 3.1 RTT计算核心算法

```python
def calculate_rtt(self, conn_id):
    """
    计算RTT（往返时延）
    
    算法原理:
    1. 记录每个数据包的发送时间(按序列号存储)
    2. 收到ACK包时,找到被确认的数据包
    3. 计算时间差作为RTT样本
    
    注意事项:
    - 只有数据包才有RTT意义
    - ACK号表示期望的下一个字节
    - 需要过滤异常值
    
    参数:
        conn_id: TCP连接标识
        
    返回:
        list: RTT数据列表
        [{'time': timestamp, 'rtt': rtt_value}, ...]
    """
    packets = self.get_connection_packets(conn_id)
    rtt_data = []
    
    # 存储每个序列号的发送时间
    # key: 序列号, value: 发送时间
    seq_times = {}
    
    for pkt in packets:
        # 步骤1: 记录数据包的发送时间
        if pkt['length'] > 0:
            # 有数据的包,记录其序列号和时间
            seq_times[pkt['seq']] = pkt['time']
        
        # 步骤2: 如果是ACK包,计算RTT
        if pkt['ack'] > 0:
            # ACK号表示:期望收到的下一个字节序列号
            # 即确认了所有序列号 < ACK号 的字节
            
            for seq, send_time in seq_times.items():
                # 如果该序列号被确认
                if seq < pkt['ack']:
                    # 计算RTT
                    rtt = (pkt['time'] - send_time) * 1000  # 转换为毫秒
                    
                    # 过滤异常值
                    # RTT应该在合理范围内(0-10000ms)
                    if rtt > 0 and rtt < 10000:
                        rtt_data.append({
                            'time': pkt['time'],
                            'rtt': rtt
                        })
    
    return rtt_data
```

### 3.2 RTT样本匹配问题

```python
"""
问题: 如何正确匹配数据包和其ACK?

场景1: 简单一对一
发送 Seq=100 (100字节) 
收到 ACK=200  → RTT = ACK时间 - 发送时间 ✓

场景2: 累积确认
发送 Seq=100 (100字节)
发送 Seq=200 (100字节)
发送 Seq=300 (100字节)
收到 ACK=400  → 确认了全部3个包
问题: 应该匹配哪个包?

解决方案:
匹配所有 Seq < ACK 的包,都可以得到一个RTT样本
但这样可能导致RTT偏大(因为后面的包还没发)
"""

def improved_rtt_calculation(packets):
    """
    改进的RTT计算
    
    策略: 只为每个ACK计算一个RTT样本
    选择: 最接近ACK号的那个序列号
    """
    rtt_data = []
    seq_times = {}
    
    for pkt in packets:
        if pkt['length'] > 0:
            seq_times[pkt['seq']] = {
                'time': pkt['time'],
                'end_seq': pkt['seq'] + pkt['length']
            }
        
        if pkt['ack'] > 0:
            # 找到end_seq最接近ACK号的数据包
            best_match = None
            for seq, info in seq_times.items():
                if info['end_seq'] <= pkt['ack']:
                    if best_match is None or info['end_seq'] > best_match['end_seq']:
                        best_match = {'seq': seq, **info}
            
            if best_match:
                rtt = (pkt['time'] - best_match['time']) * 1000
                if 0 < rtt < 10000:
                    rtt_data.append({
                        'time': pkt['time'],
                        'rtt': rtt,
                        'matched_seq': best_match['seq']
                    })
    
    return rtt_data
```

### 3.3 重传包的RTT处理

```python
"""
重要: 重传包不能用于RTT计算！

原因: 无法确定ACK是对原始包还是重传包的确认

Karn算法:
1. 不对重传包进行RTT测量
2. 保持当前的RTO值不变
3. 如果发生超时重传,RTO翻倍(指数退避)
"""

def calculate_rtt_with_retrans_filter(packets, retransmissions):
    """
    过滤重传包的RTT计算
    """
    # 提取所有重传包的序列号
    retrans_seqs = set()
    for r in retransmissions:
        retrans_seqs.add(r['original']['seq'])
    
    rtt_data = []
    seq_times = {}
    
    for pkt in packets:
        if pkt['length'] > 0:
            # 跳过重传包
            if pkt['seq'] in retrans_seqs:
                continue
            seq_times[pkt['seq']] = pkt['time']
        
        if pkt['ack'] > 0:
            for seq, send_time in seq_times.items():
                if seq < pkt['ack']:
                    rtt = (pkt['time'] - send_time) * 1000
                    if 0 < rtt < 10000:
                        rtt_data.append({
                            'time': pkt['time'],
                            'rtt': rtt
                        })
    
    return rtt_data
```

## 四、RTT统计分析

### 4.1 RTT统计指标

```python
def calculate_rtt_statistics(rtt_data):
    """
    计算RTT统计指标
    
    返回:
        dict: {
            'min': 最小RTT,
            'max': 最大RTT,
            'avg': 平均RTT,
            'median': 中位数RTT,
            'std': 标准差,
            'jitter': 抖动(相邻样本差值的平均),
            'samples': 样本数量
        }
    """
    if not rtt_data:
        return None
    
    rtt_values = [d['rtt'] for d in rtt_data]
    
    min_rtt = min(rtt_values)
    max_rtt = max(rtt_values)
    avg_rtt = sum(rtt_values) / len(rtt_values)
    
    # 中位数
    sorted_rtt = sorted(rtt_values)
    n = len(sorted_rtt)
    median_rtt = sorted_rtt[n // 2] if n % 2 == 1 else \
                 (sorted_rtt[n // 2 - 1] + sorted_rtt[n // 2]) / 2
    
    # 标准差
    variance = sum((x - avg_rtt) ** 2 for x in rtt_values) / len(rtt_values)
    std_rtt = variance ** 0.5
    
    # 抖动(Jitter) - 相邻RTT差值的平均
    jitter = 0
    if len(rtt_values) > 1:
        diffs = [abs(rtt_values[i] - rtt_values[i-1]) 
                 for i in range(1, len(rtt_values))]
        jitter = sum(diffs) / len(diffs)
    
    return {
        'min': min_rtt,
        'max': max_rtt,
        'avg': avg_rtt,
        'median': median_rtt,
        'std': std_rtt,
        'jitter': jitter,
        'samples': len(rtt_values)
    }
```

### 4.2 SRTT和RTTVAR计算

```python
def calculate_smoothed_rtt(rtt_samples, alpha=0.125, beta=0.25):
    """
    计算平滑RTT（SRTT）和RTT变差（RTTVAR）
    
    RFC 6298 算法:
    SRTT = (1 - α) × SRTT + α × RTT_sample
    RTTVAR = (1 - β) × RTTVAR + β × |SRTT - RTT_sample|
    RTO = SRTT + 4 × RTTVAR
    
    参数:
        rtt_samples: RTT样本列表
        alpha: SRTT平滑因子，默认0.125
        beta: RTTVAR平滑因子，默认0.25
    """
    if not rtt_samples:
        return None
    
    # 初始化
    srtt = rtt_samples[0]
    rttvar = srtt / 2
    rto = srtt + 4 * rttvar
    
    history = [{
        'sample': rtt_samples[0],
        'srtt': srtt,
        'rttvar': rttvar,
        'rto': rto
    }]
    
    # 迭代计算
    for i in range(1, len(rtt_samples)):
        rtt = rtt_samples[i]
        
        # 更新RTTVAR（必须在SRTT之前）
        rttvar = (1 - beta) * rttvar + beta * abs(srtt - rtt)
        
        # 更新SRTT
        srtt = (1 - alpha) * srtt + alpha * rtt
        
        # 更新RTO
        rto = srtt + 4 * rttvar
        
        # 确保最小RTO（通常1秒）
        rto = max(rto, 1000)  # ms
        
        history.append({
            'sample': rtt,
            'srtt': srtt,
            'rttvar': rttvar,
            'rto': rto
        })
    
    return {
        'final_srtt': srtt,
        'final_rttvar': rttvar,
        'final_rto': rto,
        'history': history
    }
```

## 五、可视化实现

### 5.1 RTT时序图

```python
def update_rtt_analysis(self, rtt_data, start_time):
    """更新RTT分析图表"""
    if not rtt_data:
        self.rtt_stats_label.setText("RTT统计: 无数据")
        return
    
    # 计算统计信息
    rtt_values = [d['rtt'] for d in rtt_data]
    min_rtt = min(rtt_values)
    max_rtt = max(rtt_values)
    avg_rtt = sum(rtt_values) / len(rtt_values)
    
    self.rtt_stats_label.setText(
        f"RTT统计: 最小={min_rtt:.2f}ms, 最大={max_rtt:.2f}ms, 平均={avg_rtt:.2f}ms"
    )
    
    # 清空图表
    self.rtt_figure.clear()
    
    # 创建两个子图
    ax1 = self.rtt_figure.add_subplot(211)  # RTT时序
    ax2 = self.rtt_figure.add_subplot(212)  # RTT分布
    
    # 提取数据
    times = [(d['time'] - start_time) for d in rtt_data]
    rtts = [d['rtt'] for d in rtt_data]
    
    # 绘制RTT随时间变化
    ax1.plot(times, rtts, 'b.-', linewidth=1.5, markersize=3)
    ax1.axhline(y=avg_rtt, color='r', linestyle='--', 
               label=f'平均RTT={avg_rtt:.2f}ms')
    ax1.set_xlabel('时间 (秒)')
    ax1.set_ylabel('RTT (毫秒)')
    ax1.set_title('RTT随时间变化')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 绘制RTT分布直方图
    ax2.hist(rtts, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('RTT (毫秒)')
    ax2.set_ylabel('频次')
    ax2.set_title('RTT分布直方图')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 标注统计线
    ax2.axvline(x=avg_rtt, color='r', linestyle='--', label=f'平均={avg_rtt:.2f}')
    ax2.axvline(x=min_rtt, color='g', linestyle=':', label=f'最小={min_rtt:.2f}')
    ax2.axvline(x=max_rtt, color='orange', linestyle=':', label=f'最大={max_rtt:.2f}')
    ax2.legend()
    
    self.rtt_figure.tight_layout()
    self.rtt_canvas.draw()
```

## 六、知识点总结

### 6.1 RTT核心概念

| 概念 | 说明 |
|------|------|
| RTT | 数据包从发送到收到确认的时间 |
| SRTT | 平滑RTT，对历史样本的指数加权平均 |
| RTTVAR | RTT变差，衡量RTT的波动程度 |
| RTO | 重传超时时间，基于SRTT和RTTVAR计算 |

### 6.2 RTT计算要点

| 要点 | 说明 |
|------|------|
| 匹配规则 | ACK确认序列号小于ACK值的所有数据 |
| 重传过滤 | 不使用重传包计算RTT（Karn算法） |
| 异常过滤 | 过滤不合理的RTT值（如>10秒） |
| 单位转换 | 时间戳通常是秒，RTT用毫秒表示 |

### 6.3 RTT对TCP性能的影响

| 影响 | 说明 |
|------|------|
| RTO设置 | RTT大则RTO大，丢包检测慢 |
| 吞吐量 | RTT大时，管道容量(BDP)增大，需更大窗口 |
| 响应时间 | RTT直接影响用户感知的延迟 |
| 拥塞控制 | RTT用于计算发送速率 |
