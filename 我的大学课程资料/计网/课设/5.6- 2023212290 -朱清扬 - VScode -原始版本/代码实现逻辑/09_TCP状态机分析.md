# TCP状态机分析 - 算法实现逻辑

## 一、TCP状态机概述

TCP是一个**有限状态机（Finite State Machine, FSM）**，连接在整个生命周期中会经历不同的状态。理解TCP状态机对于网络调试和问题诊断至关重要。

## 二、TCP 11种状态

### 2.1 状态定义

```
┌───────────────────────────────────────────────────────────────┐
│                      TCP状态定义                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  CLOSED       - 初始状态，没有连接                             │
│  LISTEN       - 服务器等待连接请求                             │
│  SYN_SENT     - 客户端发送SYN后等待                           │
│  SYN_RECEIVED - 服务器收到SYN后发送SYN-ACK等待                 │
│  ESTABLISHED  - 连接已建立，可以传输数据                       │
│  FIN_WAIT_1   - 主动关闭方发送FIN后等待                        │
│  FIN_WAIT_2   - 主动关闭方收到ACK后等待对方FIN                  │
│  CLOSE_WAIT   - 被动关闭方收到FIN后等待应用关闭                 │
│  CLOSING      - 双方同时关闭                                   │
│  LAST_ACK     - 被动关闭方发送FIN后等待ACK                      │
│  TIME_WAIT    - 主动关闭方等待2MSL                             │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 完整状态转换图

```
                              ┌─────────┐
                              │ CLOSED  │
                              └────┬────┘
                    主动打开(发送SYN) │ │ 被动打开(等待连接)
                           ┌────────┘ └────────┐
                           │                   │
                           ▼                   ▼
                    ┌───────────┐       ┌──────────┐
                    │ SYN_SENT  │       │  LISTEN  │
                    └─────┬─────┘       └────┬─────┘
           收到SYN-ACK    │                  │ 收到SYN,发送SYN-ACK
           发送ACK        │                  │
                          │     ┌────────────┤
                          │     ▼            │
                          │ ┌───────────────┐│
                          │ │ SYN_RECEIVED  ││
                          │ └───────┬───────┘│
                          │收到ACK  │        │
                          │         ▼        │
                          └───►┌────────────┐│
                               │ESTABLISHED ││
                               └─────┬──────┘│
                                     │       │
              ┌──────────────────────┼───────┘
              │                      │
              │ 主动关闭(发送FIN)     │ 被动关闭(收到FIN)
              ▼                      ▼
        ┌───────────┐          ┌───────────┐
        │FIN_WAIT_1 │          │CLOSE_WAIT │
        └─────┬─────┘          └─────┬─────┘
收到ACK │     │ 同时收到FIN         │ 发送FIN
        │     │                     │
        ▼     ▼                     ▼
  ┌──────────┐ ┌─────────┐    ┌──────────┐
  │FIN_WAIT_2│ │ CLOSING │    │ LAST_ACK │
  └────┬─────┘ └────┬────┘    └────┬─────┘
       │收到FIN      │收到ACK        │收到ACK
       │             │              │
       ▼             ▼              ▼
  ┌───────────────────────┐   ┌─────────┐
  │      TIME_WAIT        │   │ CLOSED  │
  │     (等待2MSL)         │   └─────────┘
  └───────────┬───────────┘
              │ 超时
              ▼
        ┌─────────┐
        │ CLOSED  │
        └─────────┘
```

## 三、状态转换分析算法

### 3.1 核心状态分析

```python
def analyze_state_transitions(self):
    """
    分析TCP状态转换
    
    算法原理:
    1. 从CLOSED状态开始
    2. 根据数据包的标志位推断状态转换
    3. 记录每次状态变化
    
    限制:
    - 单端抓包只能看到部分状态
    - 状态转换是推断的,不是绝对的
    """
    if not self.packets:
        return
    
    state_history = []
    current_state = 'CLOSED'
    
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
        
        # 记录状态变化
        if new_state != current_state:
            state_history.append({
                'state': new_state,
                'time': pkt['time'],
                'event': event,
                'packet_info': f"{pkt['src_ip']}:{pkt['src_port']} -> {pkt['dst_ip']}:{pkt['dst_port']}"
            })
            current_state = new_state
    
    return state_history
```

### 3.2 标志位与状态映射

```python
# TCP标志位定义
TCP_FLAGS = {
    'SYN': 0x02,      # 同步
    'ACK': 0x10,      # 确认
    'FIN': 0x01,      # 结束
    'RST': 0x04,      # 重置
    'SYN-ACK': 0x12,  # SYN + ACK
    'FIN-ACK': 0x11,  # FIN + ACK
}

# 状态转换规则
STATE_TRANSITIONS = {
    'CLOSED': {
        'SYN_sent': 'SYN_SENT',
        'passive_open': 'LISTEN',
    },
    'LISTEN': {
        'SYN_received': 'SYN_RECEIVED',
        'close': 'CLOSED',
    },
    'SYN_SENT': {
        'SYN-ACK_received': 'ESTABLISHED',
        'SYN_received': 'SYN_RECEIVED',
        'close': 'CLOSED',
    },
    'SYN_RECEIVED': {
        'ACK_received': 'ESTABLISHED',
        'RST_received': 'LISTEN',
        'close': 'FIN_WAIT_1',
    },
    'ESTABLISHED': {
        'FIN_sent': 'FIN_WAIT_1',
        'FIN_received': 'CLOSE_WAIT',
    },
    'FIN_WAIT_1': {
        'ACK_received': 'FIN_WAIT_2',
        'FIN_received': 'CLOSING',
        'FIN-ACK_received': 'TIME_WAIT',
    },
    'FIN_WAIT_2': {
        'FIN_received': 'TIME_WAIT',
    },
    'CLOSING': {
        'ACK_received': 'TIME_WAIT',
    },
    'TIME_WAIT': {
        'timeout': 'CLOSED',
    },
    'CLOSE_WAIT': {
        'FIN_sent': 'LAST_ACK',
    },
    'LAST_ACK': {
        'ACK_received': 'CLOSED',
    },
}
```

## 四、可视化实现

### 4.1 状态机画布

```python
class TCPStateMachineCanvas(QWidget):
    """TCP状态机画布"""
    
    # 状态节点位置定义
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
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 白色背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 绘制状态转换箭头
        self.draw_transitions(painter)
        
        # 绘制所有状态节点
        for state, pos in self.STATES.items():
            is_current = (state == self.current_state)
            self.draw_state(painter, state, pos[0], pos[1], is_current)
        
        # 绘制图例
        self.draw_legend(painter)
    
    def draw_state(self, painter, state, x, y, is_current):
        """绘制状态节点"""
        # 根据状态选择颜色
        if is_current:
            color = QColor(76, 175, 80)   # 绿色 - 当前状态
        elif state == 'ESTABLISHED':
            color = QColor(33, 150, 243)  # 蓝色 - 已建立
        elif state == 'CLOSED':
            color = QColor(158, 158, 158) # 灰色 - 关闭
        else:
            color = QColor(255, 193, 7)   # 黄色 - 过渡状态
        
        # 绘制圆形节点
        radius = 35 if is_current else 30
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(x, y), radius, radius)
        
        # 绘制状态名称
        painter.setPen(QColor(255, 255, 255))
        state_text = state.replace('_', '\n')
        painter.drawText(QRectF(x-radius, y-radius, radius*2, radius*2),
                        Qt.AlignCenter, state_text)
```

### 4.2 状态转换动画

```python
def start_animation(self):
    """开始状态转换动画"""
    if not self.state_history:
        return
    
    self.animation_step = 0
    
    # 创建定时器，每秒一个状态
    self.animation_timer = QTimer()
    self.animation_timer.timeout.connect(self.next_animation_step)
    self.animation_timer.start(1000)

def next_animation_step(self):
    """下一个动画步骤"""
    if self.animation_step < len(self.state_history):
        self.current_state = self.state_history[self.animation_step]['state']
        self.animation_step += 1
        self.update()  # 触发重绘
    else:
        self.animation_timer.stop()
```

### 4.3 状态历史列表

```python
def update_history_list(self, state_history):
    """更新状态历史列表"""
    self.history_list.clear()
    
    for i, state_info in enumerate(state_history):
        item_text = (f"{i+1}. {state_info['state']}\n"
                    f"   事件: {state_info['event']}\n"
                    f"   {state_info['packet_info']}")
        item = QListWidgetItem(item_text)
        
        # 根据状态设置背景色
        if state_info['state'] == 'ESTABLISHED':
            item.setBackground(QColor(200, 255, 200))  # 浅绿色
        elif state_info['state'] == 'CLOSED':
            item.setBackground(QColor(220, 220, 220))  # 浅灰色
        
        self.history_list.addItem(item)
```

## 五、常见状态序列

### 5.1 正常连接建立

```
CLOSED → SYN_SENT → ESTABLISHED
       (客户端)

CLOSED → LISTEN → SYN_RECEIVED → ESTABLISHED
       (服务器)
```

### 5.2 正常连接关闭（主动关闭方）

```
ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
```

### 5.3 正常连接关闭（被动关闭方）

```
ESTABLISHED → CLOSE_WAIT → LAST_ACK → CLOSED
```

### 5.4 同时关闭

```
ESTABLISHED → FIN_WAIT_1 → CLOSING → TIME_WAIT → CLOSED
```

## 六、知识点总结

### 6.1 状态机核心概念

| 概念 | 说明 |
|------|------|
| FSM | 有限状态机，TCP连接的状态管理模型 |
| 状态 | TCP连接在生命周期中的不同阶段 |
| 转换 | 由事件（收发报文）触发的状态变化 |
| 事件 | 发送/接收SYN、ACK、FIN等报文 |

### 6.2 关键状态说明

| 状态 | 角色 | 说明 |
|------|------|------|
| ESTABLISHED | 双方 | 正常通信状态 |
| TIME_WAIT | 主动关闭方 | 等待2MSL，确保连接正确关闭 |
| CLOSE_WAIT | 被动关闭方 | 等待应用程序关闭 |
| FIN_WAIT_2 | 主动关闭方 | 等待对方FIN |

### 6.3 实现要点

| 要点 | 说明 |
|------|------|
| 标志位识别 | 根据SYN/ACK/FIN判断事件类型 |
| 状态推断 | 根据当前状态和事件推断新状态 |
| 动画展示 | 逐帧展示状态转换过程 |
| 交互查看 | 点击历史记录跳转到对应状态 |
