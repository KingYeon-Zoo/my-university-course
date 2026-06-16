from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("/Users/zoo/Desktop/计算机实训")
OLD = ROOT / "backups/智能无人飞行器设计报告-朱清扬-2023212290-重写前-20260612.md"
PERSONAL = ROOT / "重点：个人分工、遇到的困难与解决办法（每个人实验报告的核心差异项）/困难与解决办法.md"
OUTPUT = ROOT / "智能无人飞行器设计报告-朱清扬-2023212290.md"


def chapter(text: str, number: int, next_number: int) -> str:
    match = re.search(
        rf"(?ms)^# {number}\. .*?(?=^# {next_number}\. )",
        text,
    )
    if not match:
        raise RuntimeError(f"无法读取第 {number} 章")
    return match.group(0).strip()


def issue(text: str, major: int, minor: int) -> str:
    match = re.search(
        rf"(?ms)^### {major}\.{minor} (.+?)\n(.*?)(?=^### {major}\.\d+ |^## \d+\. |\Z)",
        text,
    )
    if not match:
        raise RuntimeError(f"无法读取问题 {major}.{minor}")
    title = match.group(1).strip()
    body = match.group(2).strip()
    body = body.replace("**问题现象：**", "在该环节的首次联调中，出现的主要现象如下。")
    body = body.replace("**原因分析：**", "结合命令输出、节点状态和接口工作过程进行检查后，原因可归纳如下。")
    body = body.replace("**解决办法：**", "根据上述原因，对系统进行了以下调整与验证。")
    replacements = {
        "我们": "本组",
        "我": "本人",
        "死活不动": "始终没有产生预期动作",
        "疯狂": "持续",
        "石沉大海一样，完全没有回包": "始终没有收到回包",
        "彻底理干净": "重新统一规划",
        "坑": "问题",
        "不管三七二十一": "不进行状态确认便",
        "一片空白": "保持空白",
        "非常糟糕": "不满足实时观察要求",
        "瞬间": "随后",
        "砖了": "无法正常启动",
        "泡汤": "受到影响",
        "笨办法": "分层验证方法",
        "真本事": "工程实践能力",
        "咔哒": "明显",
        "牢牢地挂在钩子上": "仍停留在挂钩上",
        "一下": "",
        "这下": "调整后",
        "唯一的可能": "重点检查方向",
        "唯一的解决办法": "有效处理方式",
        "彻底解决": "完成处理",
        "十分流畅": "保持稳定运行",
        "非常稳定": "保持稳定",
    }
    for source, target in replacements.items():
        body = body.replace(source, target)
    body = re.sub(r"(?m)^\s*[-*+]\s+", "1. ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return f"### {title}\n\n{body}"


def issue_group(text: str, major: int, minors: list[int]) -> str:
    return "\n\n".join(issue(text, major, minor) for minor in minors)


def refine_early_chapters(old: str) -> str:
    chapters = "\n\n".join(chapter(old, number, number + 1) for number in (1, 2, 3))
    chapters = chapters.replace(
        "本项目属于教学原理验证，不以工业级命中精度、超远距离通信或全天候飞行为指标。报告中出现的网络时延、模型指标和测试结论均以现有材料为依据；未保存原始记录的数据不构造精确数值。",
        "本项目以课程综合设计的功能闭环和工程可实现性为主要验收目标。模型训练采用实际保存的训练记录评价，网络与图传通过三端连通、图像显示和任务终端状态进行验证，飞行平台通过外场起飞、空中飞行和地面端实时回传进行综合验收。",
    )
    chapters = chapters.replace(
        "无人飞行器是飞行平台、导航控制、通信链路、嵌入式计算、任务载荷和人工智能算法的综合载体。",
        "无人飞行器是飞行平台、导航控制、通信链路、嵌入式计算、任务载荷和人工智能算法的综合载体<sup>[1]</sup>。",
        1,
    )
    chapters = chapters.replace(
        "YOLO 系列将检测转化为端到端回归，速度和精度平衡较好，便于嵌入式部署。",
        "YOLO 系列将检测转化为端到端回归，速度和精度平衡较好，便于嵌入式部署<sup>[3]</sup>。",
        1,
    )
    chapters = chapters.replace(
        "WireGuard 能在内核态建立三层虚拟网络，配置项少、加密开销低，并可通过云服务器中继解决两端都位于 NAT 后的问题。",
        "WireGuard 能在内核态建立三层虚拟网络，配置项少、加密开销低，并可通过云服务器中继解决两端都位于 NAT 后的问题<sup>[5]</sup>。",
        1,
    )
    chapters = chapters.replace(
        "ROS Master 只负责节点注册与连接发现，不负责转发图像数据。",
        "ROS Master 只负责节点注册与连接发现，不负责转发图像数据<sup>[2]</sup>。",
        1,
    )
    chapters = chapters.replace("## 3.7 关键问题与总体解决思路", "## 3.7 开发平台与工具链\n\n开发平台由 Windows 训练主机、Ubuntu 虚拟机、阿里云 Linux 服务器、泰山派 RK3566 和 Pixhawk 飞控构成。Windows 主机用于数据标注、YOLOv5 训练和曲线分析；Ubuntu 虚拟机作为 ROS 地面端和远程调试终端；阿里云服务器承担 WireGuard 中继；泰山派运行摄像头、RKNN 推理、MAVROS 任务节点和投弹控制程序；Mission Planner 用于飞控校准、参数检查和航点规划。该工具链把模型训练、嵌入式部署、网络通信和飞行控制分开，便于逐层验证。\n\n表 3.3 开发平台与主要用途\n\n| 平台或工具 | 主要用途 | 选择依据 |\n|:---|:---|:---|\n| YOLOv5 7.0 | 坦克目标训练与评估 | 训练资料完整，便于导出 ONNX |\n| RKNN Toolkit | 模型转换与 NPU 部署 | 与 RK3566 芯片匹配 |\n| ROS 与 MAVROS | 节点通信和飞控数据访问 | 统一消息、话题和服务接口 |\n| WireGuard | 三端虚拟专网 | 配置简洁，适应 NAT 与移动网络 |\n| Mission Planner | 飞控配置和航线任务 | 支持 ArduPlane 参数及任务管理 |\n| VMware Ubuntu | 地面监控和远程调试 | 与 ROS 工具链兼容 |\n\n## 3.8 关键问题与总体解决思路")
    return chapters


FRONT = r"""
<div align="center">

<img src="《计算机应用项目实训-智能无人飞行器》设计报告模板_images/image1.png" style="width:4.8in;height:0.88333in" alt="合肥工业大学校名" />

# 智能无人飞行器设计报告

## 基于 YOLO 目标识别、WireGuard 跨公网图传与自动投弹的固定翼无人机系统

</div>

| 项目 | 内容 |
|:---:|:---|
| 学院 | 计算机与信息学院 |
| 专业班级 | 计算机科学与技术 2023 级 3 班 |
| 学生姓名及学号 | 朱清扬 2023212290 |
| 指导教师 |  |
| 课题名称 | 智能无人飞行器设计与应用 |
| 小组名称 | 马刺总冠军 |
| 完成日期 | 2026 年 6 月 11 日 |

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# 摘要

智能无人飞行器综合实训涉及固定翼飞行平台、飞控系统、嵌入式计算、计算机视觉、机器人中间件、跨公网通信和机电执行机构等多个技术方向。本项目以塞斯纳固定翼无人机为载体，完成了机体与飞控配置、泰山派 RK3566 机载计算平台部署、坦克目标识别模型训练、ROS 与 MAVROS 任务程序、WireGuard 三端虚拟专网、4G 实时图像回传、目标地理坐标解算及自动投弹控制等功能。系统由 Pixhawk 飞控负责姿态稳定、航线执行和飞行状态输出，泰山派负责摄像头采集、YOLO/RKNN 推理和任务逻辑，阿里云服务器负责跨公网数据中继，Ubuntu 虚拟机负责地面端图像显示与终端监控，投弹舵机负责执行最终释放动作。

目标识别部分采用 YOLOv5s 预训练模型进行单类别坦克检测。实际保存的训练记录中，exp5 使用 640 像素输入尺寸、批大小 16 和 300 轮配置，并因早停机制在第 178 轮附近结束。末轮精确率约为 0.958，召回率约为 0.963，mAP@0.5 约为 0.950，mAP@0.5:0.95 约为 0.411。模型通过 ONNX 与 RKNN 工具链转换后部署到 RK3566，检测结果以 ROS 消息形式提供给目标定位节点。目标定位程序综合图像中心偏移、飞行高度、航向角和无人机 GPS 位置估算目标经纬度，并通过范围约束和多帧聚合降低单帧检测波动。

跨公网通信部分将阿里云服务器、地面虚拟机和泰山派分别配置为 10.0.0.1、10.0.0.2 和 10.0.0.3。服务器开放 UDP 51820 端口、启用 IPv4 转发并配置防火墙转发规则，客户端通过 PersistentKeepalive 维持运营商 NAT 映射。ROS 节点统一使用 WireGuard 地址注册，使图像话题能够从泰山派经 4G 网络传输到地面虚拟机。自动投弹程序依据飞行高度计算自由落体时间，根据水平速度和目标距离计算释放提前量，并加入通信、程序和舵机动作补偿；执行端通过 20 ms 周期的 PWM 信号控制舵机完成挂钩释放。

外场验收在东操场进行。实飞过程表明固定翼无人机能够正常升空和飞行，地面虚拟机能够接收机载实时图像，语音节点能够识别任务指令并推送航点，目标识别、通信链路和飞行任务能够在同一系统中协同工作。项目验证了计算机视觉、嵌入式系统、计算机网络和飞行控制技术在固定翼无人机任务中的综合应用。

**关键词：** 固定翼无人机；YOLOv5；RK3566；ROS；MAVROS；WireGuard；4G 图传；自动投弹

# 目录

1. 课题概述
2. 课题任务
3. 技术方案及关键问题
4. 设计实现及测试
5. 课程设计总结
6. 参考文献
"""


CHAPTER4_HEAD = r"""
# 4. 设计实现及测试

## 4.1 系统总体设计与实现路线

本项目的实现遵循“先建立稳定飞行平台，再完成机载计算与网络基础，随后部署视觉和任务算法，最后进行整机联调与外场验证”的顺序。采用这一顺序的原因是各模块存在明确依赖关系：目标识别依赖摄像头和嵌入式运行环境，目标坐标计算依赖模型输出和飞控状态，4G 图传依赖 VPN 与 ROS 地址配置，自动投弹依赖目标位置、飞行状态和舵机驱动同时有效。若在底层条件未确认前直接进行整机测试，任一故障都会表现为最终任务失败，难以判断问题所在。

系统总体结构如图 4.1 所示。飞控承担固定翼姿态与航迹的快速闭环控制，泰山派承担图像处理和任务决策。摄像头图像进入 YOLO/RKNN 节点后得到目标类别、置信度与检测框；MAVROS 同时提供 GPS、相对高度、航向角和水平速度；目标定位节点将视觉结果与飞行状态融合，得到目标地理坐标；投弹节点根据目标距离、飞行速度、下落时间和执行补偿判断释放时机；WireGuard 网络把机载端、云服务器和地面虚拟机连接在同一虚拟网段，地面端能够查看图像和任务状态。

![系统总体架构](<report_assets_v2/diagrams/01_system_architecture.png>){width=96%}

图 4.1 智能无人飞行器系统总体架构

项目实施过程划分为八个阶段，如图 4.2 所示。每个阶段均设置独立的验收点：机体阶段检查舵面和重心，飞控阶段检查传感器与 MAVROS，泰山派阶段检查设备和系统资源，模型阶段检查训练曲线和推理输出，网络阶段检查握手与路由，ROS 阶段检查节点和话题，投弹阶段检查数值与 PWM，最终通过地面测试和外场实飞验证整体链路。

![系统实现路线](<report_assets_v2/diagrams/02_implementation_route.png>){width=96%}

图 4.2 系统设计实现路线

表 4.1 系统实施阶段及主要验收点

| 实施阶段 | 主要工作 | 验收点 |
|:---:|:---|:---|
| 飞行平台 | 机体、舵面、动力、重心与飞控安装 | 舵面方向正确，飞控状态稳定 |
| 机载平台 | 泰山派、摄像头、4G 模块和舵机连接 | 设备节点存在，供电和散热正常 |
| 模型训练 | 数据标注、训练、评估和权重选择 | 曲线收敛，验证集检测结果正确 |
| 模型部署 | ONNX、RKNN 转换及板端推理 | 板端能够输出目标检测结果 |
| 网络组网 | 云服务器与两客户端 WireGuard 配置 | 三端地址唯一且两两可达 |
| ROS 图传 | Master、节点地址和压缩图像配置 | 地面端持续显示机载画面 |
| 任务程序 | 坐标解算、投弹判断和 PWM 控制 | 数值有效，舵机独立动作正常 |
| 综合测试 | 地面分级验证与外场实飞 | 起飞、图传、任务终端同时工作 |

## 4.2 实验平台与开发环境

实验平台由固定翼飞行平台、Pixhawk 飞控、泰山派 RK3566、USB 摄像头、4G 通信模块、投弹舵机、阿里云服务器和 Ubuntu 虚拟机组成。Pixhawk 运行 ArduPlane 固件，负责姿态估计、舵面输出、自主航线和飞行状态采集。泰山派运行 Linux 与 ROS 环境，通过串口与飞控通信，通过 USB 获取图像和 4G 网络，通过 PWM 引脚控制投弹舵机。地面虚拟机承担 ROS 图形工具、远程终端和任务状态观察。训练主机运行 YOLOv5 7.0、PyTorch 和 CUDA 环境，保存数据集、训练日志、权重及评估曲线。

表 4.2 实验软硬件平台

| 类别 | 平台或软件 | 在系统中的作用 |
|:---:|:---|:---|
| 飞行平台 | 塞斯纳固定翼模型 | 承载动力、飞控、任务计算机和载荷 |
| 飞控 | Pixhawk / ArduPlane | 姿态控制、GPS 定位、航线和状态输出 |
| 机载计算机 | 泰山派 RK3566 | ROS、图像采集、RKNN 推理和投弹程序 |
| 视觉传感器 | USB 摄像头与云台 | 采集地面目标图像 |
| 通信 | 4G 模块、阿里云、WireGuard | 构建跨公网虚拟局域网 |
| 地面端 | VMware Ubuntu 虚拟机 | 远程调试、图像显示和任务监控 |
| 模型工具 | YOLOv5 7.0、PyTorch、RKNN | 训练、导出、转换与板端部署 |
| 机器人中间件 | ROS、MAVROS | 统一飞控、视觉和任务节点接口 |

机载软件的数据流如图 4.3 所示。摄像头节点和 YOLO 节点构成视觉前端，MAVROS 构成飞行状态前端，目标定位和投弹控制构成任务决策层，WireGuard 与地面虚拟机构成监控链路。各层通过标准 ROS 话题和函数接口连接，便于单独启动和验证。

![软件数据流](<report_assets_v2/diagrams/04_software_dataflow.png>){width=96%}

图 4.3 机载软件与 ROS 数据流

## 4.3 固定翼机体、飞控及任务载荷

固定翼飞机依靠机翼上下表面的压力差产生升力。设空气密度为 $\rho$，飞行速度为 $V$，机翼面积为 $S$，升力系数为 $C_L$，则升力可表示为：

$$
L=\frac{1}{2}\rho V^2SC_L
$$

固定翼不能像多旋翼一样原地悬停，速度过低会使升力下降并增加失速风险，因此机体装配必须保证左右机翼对称、舵面活动顺畅、连接杆间隙合理和重心位置正确。副翼用于滚转控制，升降舵用于俯仰控制，方向舵用于偏航控制。安装完成后先拆除螺旋桨检查电机转向和各舵面响应，再在低风险条件下进行滑跑和起飞准备。

飞控安装在接近机体重心的位置，箭头方向与机头一致，并通过减振材料降低电机振动对惯性测量单元的影响。GPS 和磁罗盘远离电调、电机和动力线。通过 Mission Planner 完成加速度计、罗盘、遥控器和飞行模式校准，并核对 MAIN OUT 各通道与副翼、升降舵、油门和方向舵的映射。TELEM 串口用于飞控与泰山派之间的 MAVLink 通信，飞控状态由 MAVROS 转换为 ROS 话题。

![右翼与投弹机构](<report_assets_v2/evidence/evidence_01.jpg>){width=48%}
![左翼与云台摄像头](<report_assets_v2/evidence/evidence_02.jpg>){width=48%}

图 4.4 固定翼平台两侧任务载荷的实际安装

图 4.4 中，机翼一侧安装云台摄像头，另一侧安装投弹舵机和释放机构，使两侧附加载荷尽量保持平衡。机舱内部布置飞控、泰山派、供电和通信线束。安装时不仅需要保证器件固定，还需要避免线束干涉舵机拉杆，并为 USB、串口和电源接口预留应力缓冲。

![机舱内飞控安装](<report_assets_v2/evidence/evidence_03.jpg>){width=60%}

图 4.5 Pixhawk 飞控及机舱线束实际状态

## 4.4 机载硬件连接与调试

泰山派是机载任务计算核心，USB 摄像头提供图像，Pixhawk 通过 TELEM 串口提供飞行状态，4G 模块提供公网接入，投弹舵机由 PWM8_M0 控制。硬件连接关系如图 4.6 所示。串口连接需要交叉连接 TX 与 RX 并共地；摄像头和 4G 模块占用 USB 或对应通信接口；PWM 线、5 V 电源和 GND 分别连接舵机信号、电源和地。舵机负载电流较大时，使用独立 BEC 供电并保持控制地与泰山派共地，可避免舵机启动造成板端电压下降。

![机载硬件连接原理图](<report_assets_v2/diagrams/03_hardware_wiring.png>){width=96%}

图 4.6 机载硬件连接原理图

![泰山派安装状态一](<report_assets_v2/evidence/evidence_04.jpg>){width=48%}
![泰山派安装状态二](<report_assets_v2/evidence/evidence_05.jpg>){width=48%}

图 4.7 泰山派与机舱线束实际安装状态

硬件调试采用由静态到动态的顺序。首先使用 `lsusb`、`ls /dev/video*`、`dmesg` 和串口输出确认设备被系统识别；其次检查文件系统剩余空间、CPU 温度和电源稳定性；随后分别启动摄像头、MAVROS 和 PWM 测试程序；最后再启动 YOLO、网络图传和任务程序。这样能够把硬件识别、驱动、系统资源和应用程序问题分开。
"""


CHAPTER4_MIDDLE_1 = r"""
## 4.5 ROS 与 MAVROS 通信基础

MAVLink 是飞控与外部计算机之间的轻量通信协议，MAVROS 将 MAVLink 消息转换为 ROS 话题、服务和参数接口。飞控实时发布位置、速度、姿态、相对高度和系统状态，任务程序无需直接解析串口字节流，只需订阅相应话题。常用输入包括 `/mavros/global_position/global`、`/mavros/global_position/rel_alt`、`/mavros/global_position/compass_hdg`、`/mavros/local_position/velocity_local` 和 `/mavros/state`。

启动 MAVROS 前先确认飞控串口设备和波特率。启动后依次检查连接状态、消息频率和数值范围：

```bash
roslaunch mavros apm.launch fcu_url:=/dev/ttyUSB0:57600
rostopic echo -n 1 /mavros/state
rostopic hz /mavros/global_position/global
rostopic echo -n 1 /mavros/global_position/rel_alt
rostopic echo -n 1 /mavros/global_position/compass_hdg
```

`/mavros/state` 中 `connected` 为真说明 MAVLink 链路建立；GPS 和高度话题持续更新说明导航数据可供任务程序使用。若仅能看到节点而状态不更新，应检查串口占用、设备权限、波特率和飞控 TELEM 参数，而不是直接修改上层算法。

## 4.6 数据集制作与 YOLO 格式检查

目标数据集采用单类别 YOLO 格式，类别名称为 `tank`。每张图片对应一个同名文本文件，每一行包含类别编号、目标中心横坐标、目标中心纵坐标、目标宽度和目标高度。设图像宽高分别为 $W$ 和 $H$，标注框左上角为 $(x_1,y_1)$、右下角为 $(x_2,y_2)$，则归一化标签为：

$$
x_c=\frac{x_1+x_2}{2W},\qquad
y_c=\frac{y_1+y_2}{2H}
$$

$$
w=\frac{x_2-x_1}{W},\qquad
h=\frac{y_2-y_1}{H}
$$

所有坐标应位于 0 至 1 之间。数据集制作流程包括图像筛选、目标标注、标签检查、训练集与验证集划分、配置文件编写和训练前扫描，如图 4.8 所示。

![YOLO训练流程](<report_assets_v2/diagrams/05_yolo_training_flow.png>){width=96%}

图 4.8 YOLO 数据集构建与模型训练流程

数据集配置文件 `ccsszz.yaml` 指定数据根目录、训练集、验证集、类别数和类别名称：

```yaml
path: datasets
train: images/train
val: images/val
nc: 1
names: [tank]
```

训练前使用脚本检查图片与标签是否一一对应，读取每个标签的列数和坐标范围，并抽样显示标注框。数据分布图显示数据集中以单目标样本为主，目标尺寸和位置存在一定变化。验证集预测图能够直观检查模型是否把坦克目标框在合理位置。

![数据集标签分布](<report_assets_v2/evidence/evidence_21.jpg>){width=48%}
![验证集预测样本](<report_assets_v2/evidence/evidence_22.jpg>){width=48%}

图 4.9 数据集分布与验证集实际预测结果
"""


CHAPTER4_MIDDLE_2 = r"""
## 4.7 YOLO 模型训练实现

本项目采用 YOLOv5s 作为基础模型。YOLOv5 将输入图像经过主干网络提取多尺度特征，再由颈部网络融合不同分辨率的信息，最后在多个尺度的检测头上预测目标框、目标置信度和类别概率。与两阶段检测器相比，YOLOv5 能够在一次前向传播中完成候选框生成和分类，适合需要实时处理的机载平台。

训练使用 `yolov5s.pt` 预训练权重进行迁移学习，输入尺寸为 640，批大小为 16，优化器记录为 SGD。exp5 的训练命令如下：

```bash
python train.py \
  --data data/ccsszz.yaml \
  --weights yolov5s.pt \
  --epochs 300 \
  --batch-size 16 \
  --imgsz 640 \
  --optimizer SGD
```

训练过程的总损失由框回归损失、目标置信度损失和分类损失构成：

$$
L_{\mathrm{total}}
=\lambda_{\mathrm{box}}L_{\mathrm{box}}
+\lambda_{\mathrm{obj}}L_{\mathrm{obj}}
+\lambda_{\mathrm{cls}}L_{\mathrm{cls}}
$$

本任务只有一个类别，因此分类损失接近零属于正常现象。训练期间重点观察训练集与验证集损失是否共同下降，以及 Precision、Recall、mAP 是否进入稳定区间。若训练损失继续下降而验证损失明显上升，则可能出现过拟合；若训练初期即出现标签或路径警告，则应停止训练并修正数据，而不是等待全部轮次结束。
"""


CHAPTER4_MIDDLE_3 = r"""
## 4.8 模型训练结果及对比分析

表 4.3 给出了工作区中三组实际训练记录。exp4 与 exp20 均配置 100 轮，exp5 配置 300 轮并在第 177 轮附近结束。三组训练均采用批大小 16 和 640 像素输入，因此可以直接比较训练轮次变化后的指标。

表 4.3 YOLOv5 实际训练结果对比

| 训练记录 | 配置轮数 | 实际末轮 | 批大小 | 输入尺寸 | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| exp4 | 100 | 99 | 16 | 640 | 0.866 | 0.867 | 0.818 | 0.259 |
| exp20 | 100 | 99 | 16 | 640 | 0.839 | 0.840 | 0.790 | 0.256 |
| exp5 | 300 | 177 | 16 | 640 | 0.958 | 0.963 | 0.950 | 0.411 |

精确率与召回率分别定义为：

$$
P=\frac{TP}{TP+FP},\qquad
R=\frac{TP}{TP+FN}
$$

exp5 的 mAP@0.5 相比 exp4 提高约 0.132，Recall 提高约 0.096，说明增加有效训练轮次后模型在当前验证集上的检测能力明显提升。mAP@0.5:0.95 仍明显低于 mAP@0.5，说明当交并比要求提高时，检测框定位精细度下降，目标尺度、拍摄角度、标注一致性和数据多样性仍是限制因素。

![训练曲线](<report_assets_v2/evidence/evidence_17.png>){width=95%}

图 4.10 exp5 训练与验证曲线

训练曲线显示框损失和目标损失在前期快速下降，Precision、Recall 与 mAP 同步上升，随后进入波动收敛阶段。PR 曲线在较大召回范围内保持较高精确率，F1 曲线显示中等置信度阈值附近具有较好的综合表现。部署时不能简单使用最低置信度以追求召回率，因为投弹任务对误检更加敏感，应结合连续帧确认、地理范围和飞行状态进行二次判断。

![PR曲线](<report_assets_v2/evidence/evidence_18.png>){width=48%}
![F1曲线](<report_assets_v2/evidence/evidence_19.png>){width=48%}

图 4.11 exp5 的 PR 曲线与 F1 曲线

![混淆矩阵](<report_assets_v2/evidence/evidence_20.png>){width=62%}

图 4.12 exp5 验证结果混淆矩阵

综合曲线、末轮指标和验证集预测结果，项目选择 exp5 的 `best.pt` 作为后续模型转换输入。选择 `best.pt` 而不是 `last.pt`，是因为前者对应训练过程中验证指标较优的权重，能够降低末期波动对部署结果的影响。

## 4.9 ONNX 与 RKNN 模型部署

训练得到的 PyTorch 权重不能直接在 RK3566 NPU 上执行，需要先导出为 ONNX 计算图，再通过 RKNN Toolkit 完成算子转换、输入预处理配置、量化和芯片适配。部署流程如图 4.13 所示。

![模型转换流程](<report_assets_v2/diagrams/06_model_deployment_flow.png>){width=96%}

图 4.13 模型格式转换与嵌入式部署流程

模型转换时保持输入尺寸为 640×640，并核对输入张量排列、RGB/BGR 顺序、归一化方式和输出检测头。板端加载模型后先使用固定测试图验证输出，再接入实时摄像头。典型启动顺序为：

```bash
ls /dev/video*
v4l2-ctl --list-devices
roslaunch rknn_ros camera.launch device:=video0
roslaunch rknn_ros yolov5.launch chip_type:=RK356X
rostopic hz /rknn_image
```

转换成功只说明模型文件能够生成，不代表板端结果一定正确。若出现检测框位置错误、类别异常或置信度明显偏低，需要分别检查预处理通道顺序、量化样本、输出节点、Anchor 和后处理尺度。通过 PC 仿真输出与板端输出对比，可以区分模型转换问题和摄像头问题。
"""


CHAPTER4_MIDDLE_4 = r"""
## 4.10 WireGuard 三端网络搭建

泰山派使用 4G 网络接入公网，地面虚拟机通常位于校园网或局域网，两端均处于 NAT 后，无法依靠私有地址直接建立稳定连接。本项目使用具有固定公网地址的阿里云服务器作为 WireGuard 中心节点，建立 10.0.0.0/24 虚拟网段，拓扑如图 4.14 所示。

![WireGuard拓扑](<report_assets_v2/diagrams/07_wireguard_topology.png>){width=92%}

图 4.14 WireGuard 三端虚拟专网拓扑

表 4.4 WireGuard 地址规划

| 节点 | VPN 地址 | 角色 | 关键配置 |
|:---:|:---:|:---|:---|
| 阿里云服务器 | 10.0.0.1/24 | 中心节点与转发器 | UDP 51820、IPv4 转发 |
| 地面虚拟机 | 10.0.0.2/24 | ROS 地面监控端 | AllowedIPs 10.0.0.0/24 |
| 泰山派 | 10.0.0.3/24 | ROS Master 与图像发布端 | 4G 接入、Keepalive 25 s |

服务器端配置两个 Peer，每个 Peer 只绑定对应客户端的 `/32` 地址；客户端把 10.0.0.0/24 指向服务器 Peer，使访问任一 VPN 节点的流量进入隧道。服务器配置框架如下：

```ini
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <server_private_key>

[Peer]
PublicKey = <vm_public_key>
AllowedIPs = 10.0.0.2/32

[Peer]
PublicKey = <board_public_key>
AllowedIPs = 10.0.0.3/32
```

服务器还需要开放安全组和本机防火墙的 UDP 51820 端口，启用并持久化 IPv4 转发：

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -A FORWARD -i wg0 -o wg0 -j ACCEPT
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo netfilter-persistent save
sudo systemctl enable wg-quick@wg0
```

客户端位于 NAT 后时，在 Peer 中配置 `PersistentKeepalive = 25`，使客户端每隔 25 秒发送小型数据包维持 UDP 映射。网络验证按照“接口、握手、路由、转发、业务”的顺序进行：

```bash
ip addr show wg0
sudo wg
ip route
ping 10.0.0.1
ping 10.0.0.2
ping 10.0.0.3
```
"""


CHAPTER4_MIDDLE_5 = r"""
## 4.11 ROS 跨公网通信与 4G 图传

ROS Master 负责节点注册和连接发现，但不转发实际图像数据。虚拟机能够执行 `rostopic list` 只说明它能够访问 Master；订阅者获得发布者地址后，还需要直接访问发布者注册的 IP。为保证控制面和数据面都经过 WireGuard，泰山派和虚拟机分别使用 VPN 地址设置 `ROS_IP`。

泰山派配置：

```bash
export ROS_MASTER_URI=http://10.0.0.3:11311
export ROS_IP=10.0.0.3
```

虚拟机配置：

```bash
export ROS_MASTER_URI=http://10.0.0.3:11311
export ROS_IP=10.0.0.2
```

配置写入 `~/.bashrc` 后，在新终端执行 `source ~/.bashrc`，并使用 `echo $ROS_MASTER_URI` 和 `echo $ROS_IP` 检查。图像链路如图 4.15 所示。

![ROS图像传输链路](<report_assets_v2/diagrams/08_ros_image_flow.png>){width=96%}

图 4.15 ROS 跨公网图像传输链路

原始 640×480、三通道、8 位图像的单帧数据量约为：

$$
D_{\mathrm{frame}}=640\times480\times3\approx0.88\ \mathrm{MiB}
$$

若以 15 帧每秒传输，未计协议开销的数据率约为 13.2 MiB/s，明显不适合普通 4G 上行链路。因此实际图传使用 `image_transport` 的 JPEG 或 Theora 压缩话题，并在任务需要与网络负载之间选择分辨率和帧率。地面端先用 `rostopic info` 检查消息类型，再选择对应的 `compressed` 或 `theora` 子话题。

![完整图传链路](<report_assets_v2/evidence/evidence_06.png>){width=94%}

图 4.16 泰山派、WireGuard、ROS 与地面图像显示完整链路

图 4.16 中，虚拟机同时显示远程终端和图像查看窗口，说明 VPN、ROS Master、图像发布和地面解码环节已经贯通。调试时使用 `rostopic hz` 观察实际帧率，并结合 4G 信号、CPU/NPU 温度和网络丢包判断卡顿原因。
"""


CHAPTER4_MIDDLE_6 = r"""
## 4.12 语音识别与航点推送

语音识别模块将麦克风输入转换为任务关键词，任务节点根据有效口令调用 MAVROS 航点推送和模式切换服务。其工作过程为：启动语音模型，持续读取音频，判断是否识别到预设口令，解析航点文件，构造 `mavros_msgs/Waypoint` 数组，调用 `/mavros/mission/push` 写入飞控，随后根据任务阶段切换飞行模式。

航点推送函数需要检查服务调用是否成功以及飞控接受的航点数量，典型逻辑如下：

```cpp
if (waypoint_push_client.call(wp_srv) && wp_srv.response.success) {
    ROS_INFO("Waypoints pushed successfully");
} else {
    ROS_ERROR("Failed to push waypoints");
}
```

![语音节点启动与识别](<report_assets_v2/evidence/evidence_07.png>){width=62%}
![航点推送成功](<report_assets_v2/evidence/evidence_08.png>){width=62%}

图 4.17 语音识别节点运行及航点推送结果

![切换AUTO模式](<report_assets_v2/evidence/evidence_09.png>){width=66%}

图 4.18 识别起飞指令后任务模式切换

终端输出中出现 `Waypoints pushed successfully` 和 AUTO 模式切换信息，说明语音识别结果已经进入航点任务链，而不是停留在文本输出层面。语音模块与图传、目标识别和投弹程序共用 ROS 环境，因此网络地址和 Master 配置必须一致。

## 4.13 目标检测与地理坐标解算

目标定位需要完成图像坐标、相机坐标、机体坐标、北东坐标和地理坐标之间的转换，关系如图 4.19 所示。设检测框中心为 $(u,v)$，相机主点为 $(c_x,c_y)$，相机等效焦距为 $f_x,f_y$，相对高度为 $h$，则在相机近似垂直向下且地面局部平坦时，可将像素偏移投影为地面位移：

$$
x_c=\frac{u-c_x}{f_x}h,\qquad
y_c=\frac{c_y-v}{f_y}h
$$

![坐标转换关系](<report_assets_v2/diagrams/09_coordinate_transform.png>){width=94%}

图 4.19 目标像素坐标到地理坐标的转换关系

若无人机航向角为 $\psi$，将机体系位移旋转到东、北方向：

$$
\begin{bmatrix}x_e\\y_n\end{bmatrix}
=
\begin{bmatrix}
\cos\psi&-\sin\psi\\
\sin\psi&\cos\psi
\end{bmatrix}
\begin{bmatrix}x_c\\y_c\end{bmatrix}
$$

在局部小范围内，地球半径取 $R_e$，无人机纬度为 $\varphi$，经纬度增量近似为：

$$
\Delta\mathrm{lat}=\frac{y_n}{R_e}\frac{180}{\pi},\qquad
\Delta\mathrm{lon}=\frac{x_e}{R_e\cos\varphi}\frac{180}{\pi}
$$

为避免单帧检测框抖动直接造成目标经纬度跳变，程序先检查坐标是否位于任务区域，再把有效样本加入时间窗口。三秒内样本数量达到阈值后计算平均值并更新投弹目标：

```cpp
void Target::final_target_coordinates(double target_lat, double target_lon) {
    if (target_lat < SOUTH_lat_Scope || target_lat > NORTH_lat_Scope ||
        target_lon < WEST_Lon_Scope || target_lon > EAST_Lon_Scope) {
        return;
    }

    Final_Coordinates sample;
    sample.timestamp = ros::Time::now();
    sample.lat = target_lat;
    sample.lon = target_lon;

    if (final_coordinates_buf.empty() ||
        sample.timestamp - final_coordinates_buf.front().timestamp <
            ros::Duration(3.0)) {
        final_coordinates_buf.push_back(sample);
        return;
    }

    if (final_coordinates_buf.size() > 20) {
        double sum_lat = 0.0;
        double sum_lon = 0.0;
        for (const auto &item : final_coordinates_buf) {
            sum_lat += item.lat;
            sum_lon += item.lon;
        }
        drop_coordinates_lat = sum_lat / final_coordinates_buf.size();
        drop_coordinates_lon = sum_lon / final_coordinates_buf.size();
        find_goal = 1;
    }
    final_coordinates_buf.clear();
}
```
"""


CHAPTER4_MIDDLE_7 = r"""
## 4.14 自动投弹模型与程序实现

投弹模型采用固定翼在短时间内水平匀速、弹体释放后竖直方向做自由落体的近似。设相对高度为 $h$、重力加速度为 $g$，理论下落时间为：

$$
t_f=\sqrt{\frac{2h}{g}}
$$

若水平速度为 $v$，理论提前距离为：

$$
d_f=vt_f
$$

设无人机到目标的当前水平距离为 $d$，通信、程序处理和舵机动作补偿为 $t_c$，则等待时间为：

$$
t_d=\frac{d}{v}-t_f-t_c
$$

程序判断流程如图 4.20 所示。进入核心计算前必须确认目标已锁定、水平速度大于阈值、高度为正、位置数据有效且坐标位于任务范围内。若等待时间尚大于释放窗口，程序继续更新飞行状态；进入窗口后执行 `open_boom()`，并设置锁定标志防止重复触发。

![投弹程序流程](<report_assets_v2/diagrams/10_drop_flow.png>){width=82%}

图 4.20 自动投弹判断程序流程

```cpp
void fire() {
    const double velocity =
        std::hypot(drop_boom.velocity_x, drop_boom.velocity_y);

    if (!find_goal || velocity < 0.2 ||
        uav_coordinates.rel_alt <= 0.0) {
        ROS_WARN_THROTTLE(1.0, "Drop condition invalid.");
        return;
    }

    const double distance = distance_calculate(
        uav_coordinates.lat, uav_coordinates.lon);
    const double fall_time =
        std::sqrt(2.0 * uav_coordinates.rel_alt / 9.8);
    const double actuator_compensation = 0.12;
    const double delay =
        distance / velocity - fall_time - actuator_compensation;

    ROS_INFO("velocity=%.3f m/s, distance=%.3f m, delay=%.3f s",
             velocity, distance, delay);

    if (delay <= 0.0) {
        open_boom();
    } else if (delay <= 0.3) {
        ros::Duration(delay).sleep();
        open_boom();
    }
}
```

程序将距离统一为米、速度统一为米每秒、角度统一在输入处转换为弧度。0.2 m/s 的速度门限用于避免地面静态阶段或异常速度造成除零。0.12 s 补偿用于覆盖通信、调度和舵机机械动作延迟。真实飞行还受到风、姿态变化和空气阻力影响，因此系统通过连续帧确认、任务区域约束和地面分级测试降低误触发风险。

## 4.15 PWM 舵机控制与机械释放

常用舵机使用 20 ms 周期、50 Hz 的 PWM 信号，高电平脉宽决定转角。1.0 ms、1.5 ms 和 2.0 ms 脉宽通常分别对应舵机一端、中位和另一端，实际释放角度需根据舵机与挂钩结构标定。PWM 控制原理如图 4.21 所示。

![PWM控制示意](<report_assets_v2/diagrams/11_pwm_timing.png>){width=94%}

图 4.21 舵机 PWM 周期与脉宽控制示意

占空比定义为高电平时间与周期之比：

$$
\eta=\frac{t_{\mathrm{high}}}{T}\times100\%
$$

当周期为 20 ms 时，1.0 ms、1.5 ms 和 2.0 ms 脉宽分别对应约 5%、7.5% 和 10% 的占空比。Linux sysfs PWM 接口必须按照导出通道、设置周期、设置极性、设置占空比和使能输出的顺序操作：

```cpp
int PWM_Init() {
    write_value(PWM_EXPORT_PATH, "0");
    write_value(PWM_PERIOD_PATH, "20000000");
    write_value(PWM_POLARITY_PATH, "normal");
    write_value(PWM_DUTY_PATH, "1500000");
    write_value(PWM_ENABLE_PATH, "1");
    return 0;
}

int set_PWM(int duty_cycle_ns) {
    return write_value(PWM_DUTY_PATH,
                       std::to_string(duty_cycle_ns));
}

void open_boom() {
    set_PWM(2000000);
}

void close_boom() {
    set_PWM(1000000);
}
```

调试时先运行独立 PWM 程序，确认权限、通道、周期和舵机动作，再接入投弹节点。若舵机已经转动但弹体未释放，需要检查脉宽范围、舵机扭矩、独立供电和机械摩擦，而不能仅依据程序日志判断成功。

## 4.16 地面分级测试

自动投弹同时涉及飞行、视觉、网络、算法和机械机构，直接实飞难以定位问题且风险较高。本项目采用四级测试逐步扩大验证范围，如图 4.22 所示。

![分级测试](<report_assets_v2/diagrams/12_test_pyramid.png>){width=82%}

图 4.22 系统分级测试与风险收敛过程

表 4.5 分级测试内容及通过条件

| 阶段 | 输入与环境 | 主要观察量 | 通过条件 |
|:---:|:---|:---|:---|
| 数据与日志回放 | 保存图像、飞行状态或模拟输入 | 坐标、速度、高度、延迟 | 无 nan、inf 和越界触发 |
| 地面静态测试 | 固定机体、目标图、舵机挂载 | 检测框、PWM、机械释放 | 目标稳定识别，舵机可靠动作 |
| 低速动态测试 | 手持机体移动 | 速度门限、延迟变化 | 数值随距离和速度合理变化 |
| 外场实飞 | 完整飞行与网络环境 | 起飞、图传、任务状态 | 飞行稳定，地面端有实时画面 |
"""


CHAPTER4_TAIL = r"""
## 4.17 外场实飞与实时回传

外场验收在东操场进行。起飞前完成机体固定、舵面方向、飞控状态、GPS、遥控器、任务载荷、电池和网络链路检查。地面虚拟机保持 WireGuard、ROS 环境和图像查看窗口运行，泰山派依次启动 MAVROS、摄像头、识别和任务节点。确认终端无持续错误、图像能够显示且遥控链路正常后，固定翼进行起飞。

![飞机离地](<report_assets_v2/evidence/evidence_10.png>){width=60%}
![飞机空中飞行](<report_assets_v2/evidence/evidence_11.png>){width=60%}

图 4.23 固定翼无人机起飞和空中飞行状态

连续截图显示飞机从建筑物附近升空，随后在操场上空保持飞行。图中红框标记飞机位置，能够反映飞机与地面背景的相对变化。

![实飞连续画面一](<report_assets_v2/evidence/evidence_12.png>){width=47%}
![实飞连续画面二](<report_assets_v2/evidence/evidence_13.png>){width=47%}

图 4.24 固定翼无人机外场飞行连续画面

![实飞连续画面三](<report_assets_v2/evidence/evidence_14.png>){width=47%}
![实飞连续画面四](<report_assets_v2/evidence/evidence_15.png>){width=47%}

图 4.25 固定翼无人机航迹变化及远距离飞行画面

实飞过程中，地面虚拟机的 `rqt_image_view` 显示机载摄像头拍摄到的草地和机身局部，终端同时显示任务节点运行信息。该画面将飞机物理飞行、4G 网络、WireGuard 隧道、ROS 图像话题和地面显示连接在同一验证场景中。

![实飞地面端画面](<report_assets_v2/evidence/evidence_16.png>){width=94%}

图 4.26 外场实飞过程中地面虚拟机接收的机载画面

## 4.18 综合测试结果与分析

综合测试从模型、网络、图传、任务程序和飞行平台五个方面评价系统。模型训练方面，exp5 的各项指标高于两组 100 轮训练，验证了更充分训练和最佳权重选择的作用；但 mAP@0.5:0.95 仍低于 mAP@0.5，说明精细定位和复杂场景泛化需要继续改进。网络方面，WireGuard 解决了两个 NAT 客户端无法直接访问的问题，服务器转发和客户端保活保证了三端通信；校园网和 4G 的时延与丢包仍比局域网波动更大。

图传方面，压缩图像显著降低了带宽占用，使地面端能够持续显示机载画面。压缩同时会损失部分细节，因此识别推理应尽量在泰山派本地完成，地面图像主要用于监控和调试，不承担高速飞行控制闭环。任务程序方面，多帧聚合、任务区域、速度门限、高度有效性和单次触发锁定共同降低了误动作风险。执行机构方面，程序触发、PWM 输出、舵机动作和机械释放是四个不同的验收层级，必须分别确认。

表 4.6 系统主要方案对比

| 对比项目 | 初始方式 | 最终方式 | 改进效果 |
|:---:|:---|:---|:---|
| 目标坐标 | 使用单帧检测结果 | 范围过滤与多帧平均 | 降低检测框波动造成的坐标跳变 |
| 图像传输 | 原始图像话题 | 压缩图像话题 | 降低 4G 上行带宽占用 |
| ROS 地址 | 使用物理网卡地址 | 使用 WireGuard 地址 | 控制面与数据面均可跨公网访问 |
| VPN 稳定性 | 仅建立基础隧道 | 转发、路由、保活和持久化 | 空闲和重启后的链路更稳定 |
| 投弹判断 | 直接按理论时间触发 | 状态门限、补偿和触发锁定 | 避免除零、无效数据和重复动作 |
| 舵机测试 | 与主任务同时调试 | PWM 独立测试后再集成 | 区分程序、供电和机械问题 |

表 4.7 系统综合测试结论

| 测试对象 | 验证结果 | 对应证据 |
|:---:|:---|:---|
| 固定翼飞行 | 能够完成起飞和空中飞行 | 图 4.23 至图 4.25 |
| YOLO 模型 | exp5 指标达到本项目验证要求 | 表 4.3、图 4.10 至图 4.12 |
| 三端网络 | 云服务器、虚拟机和泰山派构成虚拟网段 | 图 4.14、相关配置与终端检查 |
| 4G 图传 | 地面虚拟机能够接收机载实时画面 | 图 4.16、图 4.26 |
| 语音任务 | 能够识别指令并推送航点、切换模式 | 图 4.17、图 4.18 |
| 投弹程序 | 具备坐标聚合、时机计算和 PWM 控制链路 | 图 4.19 至图 4.22及关键代码 |

系统已经完成课程要求的综合功能闭环。后续提高任务精度时，需要进一步扩充目标数据集，使用规范相机标定获得内外参数，记录采集、推理、传输和舵机动作时间戳，并把风估计、姿态角和弹体阻力纳入投放模型。
"""


SUMMARY = r"""
# 5. 课程设计总结

本次课程设计完成了固定翼无人机飞行平台、机载嵌入式计算、目标识别、跨公网通信、实时图传、语音任务、目标定位和自动投弹控制的综合实现。项目不是将若干独立实验简单拼接，而是围绕“任务输入、航线执行、目标感知、位置解算、释放控制和地面监控”建立完整数据链。飞控、泰山派、摄像头、YOLO 模型、MAVROS、WireGuard、4G 网络和投弹舵机均具有独立的工作条件，只有接口、地址、数据单位、启动顺序和物理结构全部匹配时，系统才能稳定运行。

本人承担的主要工作包括 YOLO 目标识别模型训练与部署、自动投弹程序编写和逻辑调试、阿里云服务器与 WireGuard 虚拟专网配置、泰山派与虚拟机的 ROS 通信以及 4G 实时图传链路联调。在模型训练过程中，完成了数据集检查、训练参数配置、曲线分析和最佳权重选择；在网络调试过程中，完成了端口开放、地址规划、路由、内核转发、防火墙规则、NAT 保活和服务持久化；在 ROS 图传过程中，完成了 Master 地址、节点注册地址、图像消息类型和传输带宽的检查；在投弹程序中，完成了目标坐标聚合、速度与高度门限、自由落体时间、执行延迟补偿和 PWM 舵机控制。

本项目的主要特点是采用云服务器与 WireGuard 将移动网络后的泰山派和校园网后的虚拟机连接到同一虚拟网段，使 ROS 节点可以使用稳定地址完成跨公网通信；目标识别结果不仅用于图像显示，还与飞控位置、高度、航向和速度结合，用于目标地理坐标与释放时机计算；系统采用多帧聚合、地理范围、数据有效性和分级测试等安全约束，避免单帧误检或异常状态直接触发执行机构。

课程设计过程中也发现了若干不足。首先，目标数据集在场景、光照、视角、遮挡和目标尺度方面仍不充分，模型在严格交并比阈值下的定位能力还有提升空间。其次，目标坐标计算采用局部平面和相机垂直安装近似，尚未利用完整相机标定和飞机实时滚转、俯仰姿态。再次，投弹模型采用水平匀速和理想自由落体近似，对风、阻力和姿态变化的描述较为有限。最后，4G 链路受无线环境影响，地面图像适合监控和任务确认，但不适合作为高速姿态闭环输入。

后续改进可以从数据、定位、时延和弹道四个方面进行。数据方面增加难例、负样本和多尺度目标，比较不同轻量网络在 RK3566 上的精度与速度。定位方面使用棋盘格完成相机内参标定，建立相机、云台、机体和北东地坐标系之间的完整外参关系。时延方面在采集、推理、传输、判断和舵机动作处加入时间戳，形成端到端延迟模型。弹道方面融合飞控风估计、姿态和多次外场数据，对释放点进行在线修正。

通过本次实训，本人掌握了复杂系统的分层调试方法。网络故障按照端口、握手、路由、转发和业务顺序检查；ROS 故障区分 Master 控制面与话题数据面；模型故障区分数据、训练、转换、预处理和后处理；投弹故障区分数值计算、PWM 输出、舵机供电和机械释放。该方法使问题定位从反复重启和试错转变为基于状态、日志和接口的逐层验证，对后续嵌入式系统、机器人和网络工程实践具有直接作用。

# 6. 参考文献

1. Beard R. W., McLain T. W. Small Unmanned Aircraft: Theory and Practice[M]. Princeton: Princeton University Press, 2012.
2. Quigley M., Conley K., Gerkey B., et al. ROS: an open-source Robot Operating System[C]. ICRA Workshop on Open Source Software, 2009.
3. Redmon J., Divvala S., Girshick R., Farhadi A. You Only Look Once: Unified, Real-Time Object Detection[C]. IEEE Conference on Computer Vision and Pattern Recognition, 2016: 779-788.
4. Jocher G., Chaurasia A., Stoken A., et al. ultralytics/yolov5: v7.0 - YOLOv5 SOTA Realtime Instance Segmentation[CP/OL]. Zenodo, 2022.
5. Donenfeld J. A. WireGuard: Next Generation Kernel Network Tunnel[R]. 2017.
6. Meier L., Tanskanen P., Heng L., et al. PIXHAWK: A micro aerial vehicle design for autonomous flight using onboard computer vision[J]. Autonomous Robots, 2012, 33: 21-39.
7. Hartley R., Zisserman A. Multiple View Geometry in Computer Vision[M]. Cambridge: Cambridge University Press, 2004.
8. Szeliski R. Computer Vision: Algorithms and Applications[M]. Cham: Springer, 2022.
9. Ultralytics. YOLOv5 Repository and Documentation[EB/OL]. https://github.com/ultralytics/yolov5.
10. ArduPilot Development Team. ArduPilot Plane and Mission Planner Documentation[EB/OL]. https://ardupilot.org/.
11. ROS Community. ROS Wiki and MAVROS Documentation[EB/OL]. https://wiki.ros.org/mavros.
12. WireGuard Project. WireGuard Documentation[EB/OL]. https://www.wireguard.com/.
"""


def normalize(text: str) -> str:
    text = re.sub(r"(?m)^---\s*$", "", text)
    text = re.sub(r"(?m)^(\s*)[-+*]\s+", r"\g<1>1. ", text)
    text = re.sub(r"(?m)^(\s*)[•▪◦·]\s*", r"\g<1>1. ", text)
    text = re.sub(r"!\[[^\]]*\](?=\()", "![]", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    old = OLD.read_text(encoding="utf-8")
    personal = PERSONAL.read_text(encoding="utf-8")
    early = refine_early_chapters(old)

    hardware_issues = issue_group(personal, 6, [1, 2, 3, 4, 5])
    dataset_issues = issue_group(personal, 4, [1, 2, 3, 4])
    training_issues = issue_group(personal, 4, [5, 6, 7, 8])
    deployment_issues = issue_group(personal, 4, [9, 10, 11])
    network_issues = issue_group(personal, 2, [1, 2, 3, 4, 5, 6, 7])
    ros_issues = issue_group(personal, 3, [1, 2, 3, 4, 5, 6, 7, 8])
    coordinate_issues = issue_group(personal, 5, [1, 2, 3])
    drop_issues = issue_group(personal, 5, [4, 5])
    pwm_issues = issue_group(personal, 5, [6, 7])
    test_issues = issue_group(personal, 5, [8])

    chapter4 = "\n\n".join(
        [
            CHAPTER4_HEAD,
            "### 机载平台运行问题及处理\n\n" + hardware_issues,
            CHAPTER4_MIDDLE_1,
            "### 数据集检查过程中发现的问题及处理\n\n" + dataset_issues,
            CHAPTER4_MIDDLE_2,
            "### 训练环境与训练过程调试\n\n" + training_issues,
            CHAPTER4_MIDDLE_3,
            "### 模型转换与板端推理调试\n\n" + deployment_issues,
            CHAPTER4_MIDDLE_4,
            "### WireGuard 联调过程与验证\n\n" + network_issues,
            CHAPTER4_MIDDLE_5,
            "### ROS 与 4G 图传调试过程\n\n" + ros_issues,
            CHAPTER4_MIDDLE_6,
            "### 目标坐标解算调试\n\n" + coordinate_issues,
            CHAPTER4_MIDDLE_7,
            "### 投弹时机计算的数值处理\n\n" + drop_issues,
            "### PWM 与机械释放调试\n\n" + pwm_issues,
            "### 分级验证的实施过程\n\n" + test_issues,
            CHAPTER4_TAIL,
        ]
    )

    report = normalize("\n\n".join([FRONT, early, chapter4, SUMMARY]))
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"generated={OUTPUT}")
    print(f"characters={len(report)}")
    print(f"lines={len(report.splitlines())}")
    print(f"images={report.count('![')}")
    print(f"display_math={report.count('$$') // 2}")
    print(f"appendix={'附录' in report}")


if __name__ == "__main__":
    main()
