# 实验 01 环境隔离说明

1. FFmpeg 安装于项目内独立 Conda 环境 `.conda-ffmpeg`，不修改系统级 FFmpeg。
2. 原始素材仅从 `Video` 与 `Audio` 目录读取，不覆盖原文件。
3. 中间帧、实验结果、截图证据和日志分别写入 `Frames`、`Results`、`Evidence` 与 `Logs`。
4. 执行入口为 `bash run_experiment.sh`。
5. 本次使用 `STUDENT_ID=2023212290 FRAME_NUMBER=90 bash run_experiment.sh`，按真实学号末两位抽取第 90 帧。
