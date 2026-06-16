# 实验 01 截图指南

本指南用于补拍实验报告中的终端操作截图。截图时应使用真实学号 `2023212290`，并确保终端中能看清命令、输入文件、输出文件和关键结果。

## 一、开始前准备

1. 打开 macOS 的“终端”应用。
2. 将终端窗口拉宽，建议宽度至少占屏幕的三分之二，高度至少占屏幕的四分之三。
3. 按 `Command + 加号` 适当放大终端文字，保证截图中的文字清晰可读。
4. 在终端运行以下命令进入实验目录：

```bash
cd "/Users/zoo/Desktop/数字媒体技术/实验01_视频编辑ffmpeg"
```

5. 设置实验所用 FFmpeg 和 FFprobe：

```bash
FFMPEG="./.conda-ffmpeg/bin/ffmpeg"
FFPROBE="./.conda-ffmpeg/bin/ffprobe"
```

6. 每次截图前运行以下命令清空终端：

```bash
clear
```

## 二、macOS 截图方法

1. 截取指定区域：按 `Command + Shift + 4`，拖动选择终端中需要保留的区域。
2. 截取完整终端窗口：按 `Command + Shift + 4`，再按一次空格，点击终端窗口。
3. 截图默认保存到桌面。
4. 截图时不要包含无关聊天窗口、个人账号信息、桌面通知或其他课程文件。
5. 建议每张截图保留终端标题栏、完整命令和完整关键输出，不要只截一小段结果。

## 三、必拍截图 1：添加学号水印

此截图用于证明按照学号后两位抽取了第 90 帧，并成功添加学号水印。

1. 在终端运行：

```bash
clear
echo "步骤 1：抽取第 90 帧并添加学号水印 2023212290"
"$FFMPEG" -hide_banner -y \
  -i Video/0001.mp4 \
  -vf "select=eq(n\,89)" \
  -fps_mode vfr -frames:v 1 -update 1 \
  Frames/0090.png

"$FFMPEG" -hide_banner -y \
  -i Frames/0090.png \
  -vf "drawtext=text='2023212290':x=w-tw-220:y=h-th-40:fontsize=34:fontcolor=white:shadowx=2:shadowy=2" \
  -frames:v 1 -update 1 \
  Frames/0090wm.png

echo "输出文件：Frames/0090wm.png"
```

2. 等命令执行完成后截图。截图中至少应显示：

   1. `select=eq(n\,89)`，表示抽取第 90 帧。
   2. `drawtext=text='2023212290'`。
   3. 输出文件 `Frames/0090wm.png`。
   4. 命令正常结束，没有红色报错。

3. 查看水印图片：

```bash
open Frames/0090wm.png
```

4. 图片打开后，使用 `Command + Shift + 4` 截取完整图片。截图必须清楚显示右下角完整学号 `2023212290`。

5. 建议保存为：

```text
截图01_第90帧添加学号水印.png
```

## 四、必拍截图 2：RAW 素材转 H.264

此截图用于证明 RAW 素材成功编码为 H.264 视频，并展示编码前后文件大小。

1. 在终端运行：

```bash
clear
echo "步骤 3：RAW 素材转 H.264"
"$FFMPEG" -hide_banner -y \
  -f rawvideo -pixel_format yuv420p \
  -video_size 1584x720 -framerate 25 \
  -i Video/0002_1584x720_25.yuv \
  -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
  Results/R0002.mp4

echo
echo "编码前后文件大小："
ls -lh Video/0002_1584x720_25.yuv Results/R0002.mp4
```

2. 截图中至少应显示：

   1. 输入格式 `rawvideo`。
   2. 分辨率 `1584x720`。
   3. 编码器 `libx264`。
   4. 输出文件 `Results/R0002.mp4`。
   5. `ls -lh` 显示的编码前后大小。

3. 建议保存为：

```text
截图02_RAW素材转H264.png
```

## 五、必拍截图 3：HEVC 视频转码

此截图用于证明原 HEVC 视频被放大至 1584×720，并转换为 H.264。

1. 在终端运行：

```bash
clear
echo "步骤 4：HEVC 转 H.264，并放大到 1584x720"
"$FFMPEG" -hide_banner -y \
  -i Video/0003.mp4 \
  -vf "scale=1584:720:flags=lanczos" \
  -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
  Results/R0003.mp4

echo
echo "转码前后属性："
"$FFPROBE" -v error \
  -show_entries stream=codec_name,width,height \
  -show_entries format=size,duration \
  -of default=noprint_wrappers=1 \
  Video/0003.mp4

echo
"$FFPROBE" -v error \
  -show_entries stream=codec_name,width,height \
  -show_entries format=size,duration \
  -of default=noprint_wrappers=1 \
  Results/R0003.mp4
```

2. 截图中至少应显示：

   1. 原视频编码 `hevc`、分辨率 `792x360`。
   2. 转码后编码 `h264`、分辨率 `1584x720`。
   3. 转码前后的文件大小。

3. 建议保存为：

```text
截图03_HEVC转H264.png
```

## 六、必拍截图 4：最终视频 FFprobe 检查

这是报告中最重要的终端截图。应完整展示最终视频的分辨率、编码、帧率和音频属性。

1. 在终端运行以下精简版命令，输出适合截图：

```bash
clear
echo "实验 01 最终视频交付检查"
echo "姓名：朱清扬"
echo "学号：2023212290"
echo
echo "命令：ffprobe Results/2023212290.mp4"
echo
"$FFPROBE" -v error \
  -show_entries format=filename,format_name,duration,size,bit_rate \
  -show_entries stream=index,codec_name,codec_type,width,height,pix_fmt,r_frame_rate,sample_rate,channels \
  -of default=noprint_wrappers=1 \
  Results/2023212290.mp4
```

2. 截图中必须清楚显示：

   1. 姓名 `朱清扬` 和学号 `2023212290`。
   2. 最终文件名 `Results/2023212290.mp4`。
   3. 视频编码 `h264`。
   4. 分辨率 `1280` 和 `720`。
   5. 像素格式 `yuv420p`。
   6. 帧率 `25/1`。
   7. 音频编码 `aac`。
   8. 采样率 `44100`。
   9. 声道数 `2`。
   10. 时长约 `15.08` 秒。

3. 建议保存为：

```text
截图04_最终视频FFprobe检查.png
```

## 七、可选截图：完整实验执行成功

此截图可用于证明整个实验脚本能够重复执行。

1. 运行：

```bash
clear
STUDENT_ID=2023212290 FRAME_NUMBER=90 bash run_experiment.sh
```

2. 等命令全部执行完成，滚动到终端底部，确保截图中显示：

```text
Experiment completed: .../Results/2023212290.mp4
```

3. 建议保存为：

```text
截图05_完整实验执行成功.png
```

## 八、将截图放入报告

1. 将拍摄好的截图放入实验目录的 `Evidence` 文件夹：

```bash
open Evidence
```

2. 建议最终保留以下截图：

   1. `截图01_第90帧添加学号水印.png`
   2. `截图02_RAW素材转H264.png`
   3. `截图03_HEVC转H264.png`
   4. `截图04_最终视频FFprobe检查.png`
   5. `截图05_完整实验执行成功.png`，此项可选。

3. 在 Word 中替换旧截图时，应保持图片宽高比，不要横向或纵向拉伸。
4. 图片宽度建议为页面正文宽度的 80% 至 100%。
5. FFprobe 截图中的文字必须能够直接阅读，不能缩得过小。

## 九、截图前最终检查

1. 截图是否包含真实姓名 `朱清扬` 和学号 `2023212290`。
2. 水印截图是否是第 90 帧，学号是否完整。
3. FFprobe 截图是否显示 H.264、1280×720、25 fps、AAC 双声道。
4. 截图是否清晰、无裁切、无无关窗口、无个人隐私信息。
5. 报告中的截图说明是否和实际截图一致。
