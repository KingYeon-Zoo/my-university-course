# TCP协议可视化分析工具

## 项目信息
- **题号**：5.6
- **学号**：2023212290
- **姓名**：朱清扬
- **开发工具**：VScode + Python 3.8+

## 项目结构

```
源程序/
├── main.py                    # 主程序入口
├── packet_parser.py           # 数据包解析模块
├── requirements.txt           # 依赖库清单
└── gui/                       # 图形界面模块
    ├── __init__.py
    ├── main_window.py         # 主窗口
    ├── dashboard_widget.py    # 仪表盘
    ├── handshake_widget.py    # 三次握手/四次挥手分析
    ├── sequence_widget.py     # 序列号/确认号分析
    ├── flow_control_widget.py # 流量控制分析
    ├── congestion_widget.py   # 拥塞控制分析
    ├── retransmit_widget.py   # 重传机制分析
    ├── state_machine_widget.py # TCP状态机
    └── statistics_widget.py   # 统计信息
```

## 核心模块说明

### 1. main.py
程序主入口，负责：
- 初始化PyQt5应用程序
- 应用现代化UI主题
- 创建并显示主窗口

### 2. packet_parser.py
数据包解析核心模块，实现：
- 读取pcapng格式抓包文件
- 解析TCP/IP协议栈
- 提取关键字段（序列号、确认号、标志位等）
- 识别TCP连接和会话

### 3. gui/main_window.py
主窗口界面，功能包括：
- 文件选择和加载
- 多标签页布局管理
- 协调各个功能模块

### 4. gui/handshake_widget.py
TCP握手/挥手分析，展示：
- 三次握手过程可视化
- 四次挥手过程可视化
- SYN、FIN等标志位识别

### 5. gui/sequence_widget.py
序列号分析模块：
- 序列号时间序列图
- 确认号变化图
- 数据传输可视化

### 6. gui/flow_control_widget.py
流量控制分析：
- 接收窗口大小变化
- 滑动窗口机制
- 窗口探测

### 7. gui/congestion_widget.py
拥塞控制分析：
- 拥塞窗口估算
- 慢启动阶段
- 拥塞避免阶段
- 快速重传和快速恢复

### 8. gui/retransmit_widget.py
重传机制分析：
- 重传数据包识别
- 超时重传检测
- 快速重传检测
- 重传统计

### 9. gui/state_machine_widget.py
TCP状态机：
- 状态转换图
- 当前连接状态
- 状态变化历史

### 10. gui/statistics_widget.py
统计信息模块：
- 连接数统计
- 数据包数统计
- 字节数统计
- 重传率统计
- 往返时延(RTT)统计

## 技术栈

- **GUI框架**：PyQt5
- **主题美化**：qt-material
- **数据包处理**：Scapy
- **数据分析**：Pandas、Numpy
- **数据可视化**：Matplotlib、PyQtGraph

## 安装依赖

```bash
pip install -r requirements.txt
```

或使用清华镜像加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行程序

```bash
python main.py
```

## 主要功能

1. **数据包加载**：支持Wireshark pcapng格式文件
2. **协议解析**：自动解析TCP/IP协议各层
3. **连接分析**：识别和跟踪TCP连接
4. **握手分析**：可视化三次握手和四次挥手
5. **序列号分析**：跟踪序列号和确认号变化
6. **流量控制**：分析接收窗口和流量控制机制
7. **拥塞控制**：展示拥塞窗口变化和控制算法
8. **重传检测**：识别重传数据包并统计
9. **状态机**：展示TCP连接状态转换
10. **统计报表**：提供多维度统计信息

## 设计特点

- ✅ 模块化设计，便于维护和扩展
- ✅ 现代化UI界面，用户体验良好
- ✅ 多维度可视化展示
- ✅ 完整的TCP协议分析功能
- ✅ 详细的统计和报表功能

## 开发环境

- Python 3.8+
- Visual Studio Code
- Windows 10/11

## 作者

朱清扬 (2023212290)

