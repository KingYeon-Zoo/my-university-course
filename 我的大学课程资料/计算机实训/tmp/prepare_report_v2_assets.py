from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/Users/zoo/Desktop/计算机实训")
OUT = ROOT / "report_assets_v2"
DIAGRAMS = OUT / "diagrams"
EVIDENCE = OUT / "evidence"
FONT_PATH = next(
    path
    for path in (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    )
    if Path(path).exists()
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def wrapped_lines(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    result: list[str] = []
    for source in text.split("\n"):
        current = ""
        for char in source:
            candidate = current + char
            if current and draw.textlength(candidate, font=fnt) > max_width:
                result.append(current)
                current = char
            else:
                current = candidate
        result.append(current)
    return result


def draw_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    *,
    fill: str = "#EDF4FB",
    outline: str = "#24557A",
    size: int = 29,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=4)
    fnt = font(size)
    lines = wrapped_lines(draw, text, fnt, x2 - x1 - 30)
    line_height = size + 10
    start_y = (y1 + y2 - len(lines) * line_height) / 2
    for index, line in enumerate(lines):
        draw.text(((x1 + x2) / 2, start_y + index * line_height), line, font=fnt, fill="#102A43", anchor="ma")


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str = "",
) -> None:
    draw.line((start, end), fill="#263238", width=5)
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    tip = (ex, ey)
    left = (ex - 20 * ux + 10 * px, ey - 20 * uy + 10 * py)
    right = (ex - 20 * ux - 10 * px, ey - 20 * uy - 10 * py)
    draw.polygon((tip, left, right), fill="#263238")
    if label:
        draw.text(((sx + ex) / 2, (sy + ey) / 2 - 18), label, font=font(22), fill="#263238", anchor="mm")


def base_canvas(title: str, width: int = 1800, height: int = 1050) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((width / 2, 45), title, font=font(46), fill="#111111", anchor="ma")
    return image, draw


def save(image: Image.Image, name: str) -> None:
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    image.save(DIAGRAMS / name, dpi=(240, 240), quality=96)


def system_architecture() -> None:
    image, draw = base_canvas("智能无人飞行器系统总体架构")
    boxes = {
        "camera": (60, 180, 310, 330, "机载摄像头"),
        "board": (400, 140, 760, 370, "泰山派 RK3566\n图像采集、YOLO/RKNN、ROS"),
        "flight": (400, 650, 760, 880, "Pixhawk 飞控\n姿态、GPS、高度、速度"),
        "target": (850, 140, 1210, 370, "目标检测与坐标解算\n像素、航向、经纬度"),
        "drop": (1320, 170, 1720, 340, "投弹判断与 PWM 舵机"),
        "vpn": (850, 650, 1210, 880, "4G + WireGuard\n10.0.0.0/24"),
        "ground": (1320, 620, 1720, 910, "阿里云服务器\n地面虚拟机\n图像、终端与任务监控"),
    }
    for box in boxes.values():
        draw_box(draw, box[:4], box[4])
    draw_arrow(draw, (310, 255), (400, 255), "USB 图像")
    draw_arrow(draw, (760, 255), (850, 255), "检测结果")
    draw_arrow(draw, (1210, 255), (1320, 255), "释放时机")
    draw_arrow(draw, (580, 650), (580, 370), "MAVLink/MAVROS")
    draw_arrow(draw, (760, 765), (850, 765), "飞行状态")
    draw_arrow(draw, (1030, 650), (1030, 370), "任务数据")
    draw_arrow(draw, (1210, 765), (1320, 765), "VPN 中继")
    save(image, "01_system_architecture.png")


def implementation_route() -> None:
    image, draw = base_canvas("系统设计实现路线")
    labels = [
        "机体与飞控准备",
        "泰山派与外设部署",
        "数据集与模型训练",
        "模型转换与板端推理",
        "WireGuard 三端组网",
        "ROS 与 4G 图传联调",
        "定位及投弹程序",
        "地面测试与外场实飞",
    ]
    positions = []
    for index, label in enumerate(labels):
        row, col = divmod(index, 4)
        x1 = 70 + col * 430
        y1 = 190 + row * 440
        box = (x1, y1, x1 + 330, y1 + 150)
        positions.append(box)
        draw_box(draw, box, f"{index + 1}. {label}")
    for index in range(3):
        draw_arrow(draw, (positions[index][2], 265), (positions[index + 1][0], 265))
    draw_arrow(draw, (positions[3][2] - 165, positions[3][3]), (positions[7][2] - 165, positions[7][1]))
    for index in range(7, 4, -1):
        draw_arrow(draw, (positions[index][0], 705), (positions[index - 1][2], 705))
    save(image, "02_implementation_route.png")


def hardware_wiring() -> None:
    image, draw = base_canvas("机载硬件连接原理图")
    draw_box(draw, (650, 350, 1120, 650), "泰山派 RK3566\n机载边缘计算核心", fill="#E3F2FD", size=34)
    nodes = [
        ((70, 160, 430, 340), "USB 摄像头\n图像输入", (430, 250), (650, 430), "USB"),
        ((70, 690, 430, 880), "4G 模块\n公网接入", (430, 785), (650, 570), "USB/网卡"),
        ((1370, 150, 1730, 340), "Pixhawk 飞控\nTELEM 串口", (1370, 250), (1120, 430), "TX/RX/GND"),
        ((1370, 690, 1730, 890), "投弹舵机\nPWM8_M0", (1370, 790), (1120, 570), "PWM/5V/GND"),
    ]
    for box, text, start, end, label in nodes:
        draw_box(draw, box, text)
        draw_arrow(draw, start, end, label)
    draw.text((900, 760), "注意：控制信号必须共地；舵机负载较大时使用独立 5 V/BEC 供电。", font=font(28), fill="#8A3B12", anchor="ma")
    save(image, "03_hardware_wiring.png")


def software_dataflow() -> None:
    image, draw = base_canvas("机载软件与 ROS 数据流")
    labels = [
        ("摄像头节点", "sensor_msgs/Image"),
        ("YOLO/RKNN 节点", "检测框、类别、置信度"),
        ("目标定位节点", "目标经纬度"),
        ("投弹控制节点", "PWM 占空比"),
    ]
    boxes = []
    for index, (title, detail) in enumerate(labels):
        x1 = 60 + index * 430
        box = (x1, 220, x1 + 330, 410)
        boxes.append(box)
        draw_box(draw, box, f"{title}\n{detail}")
        if index:
            draw_arrow(draw, (boxes[index - 1][2], 315), (box[0], 315))
    draw_box(draw, (260, 650, 650, 870), "MAVROS\nGPS、高度、航向、速度")
    draw_box(draw, (800, 650, 1190, 870), "WireGuard/4G\nROS 跨公网链路")
    draw_box(draw, (1340, 650, 1730, 870), "地面虚拟机\nrqt_image_view 与终端")
    draw_arrow(draw, (455, 650), (1010, 410), "飞行状态")
    draw_arrow(draw, (965, 650), (965, 410), "图像与任务状态")
    draw_arrow(draw, (1190, 760), (1340, 760), "监控")
    save(image, "04_software_dataflow.png")


def horizontal_flow(title: str, labels: list[str], name: str) -> None:
    image, draw = base_canvas(title)
    count = len(labels)
    margin = 55
    gap = 45
    box_width = int((1800 - 2 * margin - (count - 1) * gap) / count)
    boxes = []
    for index, label in enumerate(labels):
        x1 = margin + index * (box_width + gap)
        box = (x1, 360, x1 + box_width, 650)
        boxes.append(box)
        draw_box(draw, box, label, size=27)
        if index:
            draw_arrow(draw, (boxes[index - 1][2], 505), (box[0], 505))
    save(image, name)


def wireguard_topology() -> None:
    image, draw = base_canvas("WireGuard 三端虚拟专网拓扑")
    draw_box(draw, (650, 160, 1150, 430), "阿里云服务器\n公网 UDP 51820\nwg0: 10.0.0.1/24", fill="#FFF3E0", outline="#A65C00", size=32)
    draw_box(draw, (120, 680, 620, 930), "地面虚拟机\nwg0: 10.0.0.2/24\nROS 监控端", size=31)
    draw_box(draw, (1180, 680, 1680, 930), "泰山派\nwg0: 10.0.0.3/24\nROS Master 与图像发布端", size=31)
    draw_arrow(draw, (720, 430), (530, 680), "加密 UDP 隧道")
    draw_arrow(draw, (1080, 430), (1270, 680), "加密 UDP 隧道")
    draw_arrow(draw, (620, 805), (1180, 805), "服务器开启 IPv4 转发后两端互通")
    save(image, "07_wireguard_topology.png")


def coordinate_transform() -> None:
    image, draw = base_canvas("目标像素坐标到地理坐标的转换关系")
    draw.rectangle((120, 180, 760, 700), outline="#24557A", width=5)
    draw.line((440, 180, 440, 700), fill="#78909C", width=3)
    draw.line((120, 440, 760, 440), fill="#78909C", width=3)
    draw.ellipse((585, 525, 625, 565), fill="#D32F2F")
    draw.text((610, 580), "目标像素 (u,v)", font=font(28), fill="#D32F2F", anchor="ma")
    draw.text((440, 420), "图像中心 (cx,cy)", font=font(27), fill="#263238", anchor="ms")
    draw_arrow(draw, (440, 440), (605, 545), "像素偏移")
    draw_box(draw, (950, 200, 1660, 380), "相机坐标系\n利用焦距、图像尺寸和相对高度完成地面投影", size=29)
    draw_box(draw, (950, 450, 1660, 630), "机体坐标系 → 北东坐标系\n使用航向角完成二维旋转", size=29)
    draw_box(draw, (950, 700, 1660, 880), "地理坐标系\n根据纬度换算经纬度增量并叠加无人机 GPS", size=29)
    draw_arrow(draw, (760, 440), (950, 290))
    draw_arrow(draw, (1305, 380), (1305, 450))
    draw_arrow(draw, (1305, 630), (1305, 700))
    save(image, "09_coordinate_transform.png")


def drop_flow() -> None:
    image, draw = base_canvas("自动投弹判断程序流程")
    steps = [
        ((700, 120, 1100, 250), "读取目标、位置、高度与速度"),
        ((700, 310, 1100, 440), "数据是否有效？"),
        ((700, 500, 1100, 630), "计算下落时间、距离与补偿延迟"),
        ((700, 690, 1100, 820), "是否进入释放时间窗？"),
        ((700, 880, 1100, 1010), "执行 open_boom() 并锁定状态"),
    ]
    for box, text in steps:
        draw_box(draw, box, text, size=27)
    for index in range(len(steps) - 1):
        draw_arrow(draw, (900, steps[index][0][3]), (900, steps[index + 1][0][1]))
    draw_box(draw, (1250, 300, 1690, 450), "否：记录原因并等待下一帧", fill="#FFF3E0", outline="#A65C00", size=27)
    draw_box(draw, (1250, 680, 1690, 830), "否：继续更新飞行状态", fill="#FFF3E0", outline="#A65C00", size=27)
    draw_arrow(draw, (1100, 375), (1250, 375), "否")
    draw_arrow(draw, (1100, 755), (1250, 755), "否")
    draw.text((885, 475), "是", font=font(24), fill="#263238")
    draw.text((885, 855), "是", font=font(24), fill="#263238")
    save(image, "10_drop_flow.png")


def pwm_timing() -> None:
    image, draw = base_canvas("舵机 PWM 周期与脉宽控制示意")
    x0, y0 = 150, 600
    scale = 70
    draw.line((x0, y0, 1650, y0), fill="#263238", width=4)
    for pulse_ms, y, label in ((1.0, 260, "闭合位置：约 1.0 ms"), (1.5, 430, "中位：约 1.5 ms"), (2.0, 600, "释放位置：约 2.0 ms")):
        start = x0
        end = x0 + pulse_ms * scale
        draw.line((start, y, start, y - 90), fill="#1565C0", width=5)
        draw.line((start, y - 90, end, y - 90), fill="#1565C0", width=5)
        draw.line((end, y - 90, end, y), fill="#1565C0", width=5)
        draw.line((end, y, x0 + 20 * scale, y), fill="#1565C0", width=5)
        draw.text((900, y - 130), label, font=font(28), fill="#102A43", anchor="ma")
    draw.text((900, 790), "周期 T = 20 ms，频率 f = 50 Hz；高电平脉宽决定舵机角度。", font=font(31), fill="#263238", anchor="ma")
    save(image, "11_pwm_timing.png")


def test_pyramid() -> None:
    image, draw = base_canvas("系统分级测试与风险收敛过程")
    levels = [
        ((580, 760, 1220, 930), "第一级：数据与日志回放\n检查 nan、inf、范围与单位"),
        ((660, 570, 1140, 720), "第二级：地面静态测试\n摄像头、模型、PWM与机械释放"),
        ((740, 390, 1060, 530), "第三级：低速动态测试\n验证速度输入与延迟变化"),
        ((815, 210, 985, 350), "第四级\n外场实飞"),
    ]
    colors = ["#E8F5E9", "#E3F2FD", "#FFF8E1", "#FFEBEE"]
    outlines = ["#2E7D32", "#1565C0", "#9A6A00", "#B71C1C"]
    for (box, text), fill, outline in zip(levels, colors, outlines):
        draw_box(draw, box, text, fill=fill, outline=outline, size=26)
    draw.text((1450, 540), "风险逐级降低\n验证范围逐级扩大", font=font(33), fill="#263238", anchor="mm")
    draw_arrow(draw, (1350, 800), (1350, 300), "由地面到实飞")
    save(image, "12_test_pyramid.png")


def add_watermark(source: Path, destination: Path) -> None:
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    size = max(18, int(min(image.size) * 0.032))
    fnt = font(size)
    text = "朱清扬  2023212290"
    bounds = draw.textbbox((0, 0), text, font=fnt)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    padding = max(8, size // 3)
    x = image.width - text_width - 2 * padding
    y = image.height - text_height - 2 * padding
    draw.rounded_rectangle(
        (x, y, image.width - padding // 2, image.height - padding // 2),
        radius=max(6, padding // 2),
        fill=(255, 255, 255, 190),
        outline=(20, 55, 90, 230),
        width=max(2, size // 12),
    )
    draw.text((x + padding, y + padding - bounds[1]), text, font=fnt, fill=(15, 45, 75, 255))
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, quality=95)


def evidence_assets() -> None:
    sources = [
        ROOT / "实验截图/已经组装好的飞机真实图片/右翼与投弹舵机.jpg",
        ROOT / "实验截图/已经组装好的飞机真实图片/左翼与云台摄像头.jpg",
        ROOT / "实验截图/已经组装好的飞机真实图片/飞控图片.jpg",
        ROOT / "实验截图/已经组装好的飞机真实图片/泰山派照片.jpg",
        ROOT / "实验截图/已经组装好的飞机真实图片/泰山派图片 2.jpg",
        ROOT / "实验截图/泰山派调试截图/完整链路测试.png",
        ROOT / "实验截图/泰山派调试截图/测试语音识别.png",
        ROOT / "实验截图/泰山派调试截图/语音识别 2.png",
        ROOT / "实验截图/泰山派调试截图/语音识别 3.png",
        ROOT / "实验截图/飞机正式起飞截图/飞机飞上天截图 1.png",
        ROOT / "实验截图/飞机正式起飞截图/截图3.png",
        ROOT / "实验截图/飞机正式起飞截图/截图 2.png",
        ROOT / "实验截图/飞机正式起飞截图/截图 3.png",
        ROOT / "实验截图/飞机正式起飞截图/截图 4.png",
        ROOT / "实验截图/飞机正式起飞截图/截图 5.png",
        ROOT / "实验截图/飞机正式起飞截图/正式起飞，虚拟机画面.png",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/results.png",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/PR_curve.png",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/F1_curve.png",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/confusion_matrix.png",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/labels.jpg",
        ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train/exp5/val_batch0_pred.jpg",
    ]
    for index, source in enumerate(sources, start=1):
        if source.exists():
            suffix = ".jpg" if source.suffix.lower() in {".jpg", ".jpeg"} else ".png"
            add_watermark(source, EVIDENCE / f"evidence_{index:02d}{suffix}")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    system_architecture()
    implementation_route()
    hardware_wiring()
    software_dataflow()
    horizontal_flow(
        "YOLO 数据集构建与模型训练流程",
        ["采集与筛选图像", "YOLO 格式标注", "训练/验证集划分", "模型训练与早停", "曲线分析与权重选择"],
        "05_yolo_training_flow.png",
    )
    horizontal_flow(
        "模型格式转换与嵌入式部署流程",
        ["best.pt", "导出 ONNX", "RKNN 转换与量化", "RK3566 板端加载", "摄像头推理与 ROS 发布"],
        "06_model_deployment_flow.png",
    )
    wireguard_topology()
    horizontal_flow(
        "ROS 跨公网图像传输链路",
        ["摄像头采集", "YOLO/RKNN 推理", "压缩图像话题", "WireGuard/4G", "地面端解码显示"],
        "08_ros_image_flow.png",
    )
    coordinate_transform()
    drop_flow()
    pwm_timing()
    test_pyramid()
    evidence_assets()
    print(f"diagrams={len(list(DIAGRAMS.glob('*')))}")
    print(f"evidence={len(list(EVIDENCE.glob('*')))}")


if __name__ == "__main__":
    main()
