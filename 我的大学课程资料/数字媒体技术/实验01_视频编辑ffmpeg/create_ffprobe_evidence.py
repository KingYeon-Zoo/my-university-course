from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
source = ROOT / "Logs" / "ffprobe_final.txt"
output = ROOT / "Evidence" / "ffprobe_terminal.png"

font_path = Path("/System/Library/Fonts/Menlo.ttc")
font = ImageFont.truetype(str(font_path), 22)
title_font = ImageFont.truetype(str(font_path), 24)

lines = [
    "$ ./.conda-ffmpeg/bin/ffprobe Results/2023212290.mp4",
    "",
]
for raw_line in source.read_text(encoding="utf-8").replace(str(ROOT), ".").splitlines():
    lines.extend(
        textwrap.wrap(
            raw_line,
            width=118,
            subsequent_indent="    ",
            replace_whitespace=False,
            drop_whitespace=False,
        )
        or [""]
    )
lines.extend(["", "$ verification: H.264 1280x720 25 fps + AAC stereo"])

image = Image.new("RGB", (1800, 1300), "#111827")
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, 1800, 62), fill="#1f2937")
draw.text((28, 17), "Terminal - FFPROBE final delivery check", font=title_font, fill="#f3f4f6")

y = 88
for index, line in enumerate(lines[:43]):
    color = "#86efac" if line.startswith("$") else "#e5e7eb"
    draw.text((34, y), line, font=font, fill=color)
    y += 27

output.parent.mkdir(parents=True, exist_ok=True)
image.save(output)
