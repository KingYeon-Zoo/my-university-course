# YOLOv5-7.0 项目代码结构说明

本篇文档对当前目标检测项目 `yolov5-7.0` 的目录结构、核心运行脚本、关键代码模块以及数据集配置进行了整理，方便在实训中进行模型训练、评估和部署。

---

## 📂 核心文件结构概览

YOLOv5 采用模块化设计，结构清晰。根目录下的主要脚本用于控制整个生命周期，而核心逻辑则分布在 `models`、`utils` 和 `data` 中。

```
yolov5-7.0/
├── train.py              # 训练主入口
├── detect.py             # 推理/检测主入口
├── val.py                # 验证与指标评估
├── export.py             # 模型导出部署
├── data/                 # 数据集与超参数配置目录
│   ├── ccsszz.yaml       # 自定义数据集定义 (类别: tank)
│   └── hyps/             # 训练超参数定义
├── models/               # 神经网络模型定义目录
│   ├── common.py         # 基础骨干网络模块 (Conv, SPPF等)
│   └── yolo.py           # 搭建与解析模型的类
├── utils/                # 辅助函数与工具库
│   ├── dataloaders.py    # 数据读取与数据增强
│   ├── loss.py           # 损失函数定义
│   └── general.py        # 常用算法工具 (如 NMS)
├── datasets/             # 当前训练使用的坦克数据集
└── VOCData/              # 备用标注数据集目录
```

---

## 🛠 核心运行脚本

这些脚本是您在终端执行命令时的主要接口：

| 脚本名称 | 作用说明 | 常用命令示例 |
| :--- | :--- | :--- |
| **[train.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/train.py)** | **启动模型训练**。指定数据集、预训练权重、迭代轮数（epochs）和批次大小（batch-size）。 | `python train.py --data data/ccsszz.yaml --weights yolov5s.pt --epochs 100` |
| **[detect.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/detect.py)** | **目标检测推理**。在测试图像、视频或摄像头上运行训练好的模型模型，生成标注框。 | `python detect.py --weights runs/train/exp/weights/best.pt --source data/images` |
| **[val.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/val.py)** | **模型性能验证**。在验证集上计算 mAP（平均精度）、Precision、Recall 等核心指标。 | `python val.py --data data/ccsszz.yaml --weights best.pt` |
| **[export.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/export.py)** | **模型转换导出**。将 PyTorch 格式的 `.pt` 模型转换为更适合嵌入式部署的格式（如 ONNX、TFLite）。 | `python export.py --weights best.pt --include onnx` |

---

## 📂 关键模块详解

### 1. 网络构建模型 — [models/](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/models)
*   **[common.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/models/common.py)**：包含 YOLOv5 网络里最基础的模块。例如：
    *   `Conv`：标准的 卷积+批归一化+激活函数 块。
    *   `Bottleneck`：瓶颈残差结构。
    *   `C3`：CSP（Cross Stage Partial）结构的核心，减少计算量并提升特征融合能力。
    *   `SPPF`：快速空间金字塔池化，用于融合不同尺度的特征。
*   **[yolo.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/models/yolo.py)**：定义了模型架构解析类 `DetectionModel`，负责根据 `yolov5s.yaml` 等配置文件动态构建 PyTorch 网络。

### 2. 辅助工具库 — [utils/](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/utils)
*   **[dataloaders.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/utils/dataloaders.py)**：负责读取图像并将其转化为神经网络接受的张量，支持数据增强（如 MixUp、Mosaic 拼接等）。
*   **[loss.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/utils/loss.py)**：包含计算位置损失（GIoU/CIoU）、分类损失以及置信度损失的 `ComputeLoss` 类。
*   **[general.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/utils/general.py)**：通用计算函数，例如非极大值抑制 `non_max_suppression` 用于去除冗余重叠检测框，`scale_boxes` 用于缩放坐标。
*   **[metrics.py](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/utils/metrics.py)**：实现了混淆矩阵、AP/mAP 的计算公式。

---

## 📊 数据集配置与路径说明

项目当前主要使用的自定义数据集配置文件为 **[ccsszz.yaml](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/data/ccsszz.yaml)**：

> [!NOTE]
> 该配置文件将数据集根路径指向了项目的 **[datasets](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/datasets)** 文件夹。
> 它的识别任务为单分类，只识别一个类别：`0: tank` (坦克)。

数据集目录结构如下：
*   **📂 [datasets/images/train/](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/datasets/images)**：存放用于训练的坦克图片。
*   **📂 [datasets/labels/train/](file:///Users/zoo/Desktop/计算机实训/嵌入式系统的目标识别模型训练包/yolov5-7.0/datasets/labels)**：存放对应的 YOLO 格式归一化文本标注框（每一个 `.txt` 文件对应一张图片，包含类别ID和归一化的 `x_center y_center width height`）。
