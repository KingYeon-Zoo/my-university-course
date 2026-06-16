from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/zoo/Desktop/计算机实训")
OUTPUT = ROOT / "tmp" / "evidence_sheets"
OUTPUT.mkdir(parents=True, exist_ok=True)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_sheet(paths: list[Path], name: str, columns: int = 2) -> None:
    tile_width = 900
    image_height = 560
    caption_height = 84
    tile_height = image_height + caption_height
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (tile_width * columns, tile_height * rows), "white")
    draw = ImageDraw.Draw(sheet)
    caption_font = font(28)

    for index, path in enumerate(paths):
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((tile_width - 24, image_height - 24))
            x = (index % columns) * tile_width + (tile_width - image.width) // 2
            y = (index // columns) * tile_height + (image_height - image.height) // 2
            sheet.paste(image, (x, y))
        caption = str(path.relative_to(ROOT))
        caption_x = (index % columns) * tile_width + 18
        caption_y = (index // columns) * tile_height + image_height + 12
        draw.text((caption_x, caption_y), caption, fill="black", font=caption_font)

    sheet.save(OUTPUT / f"{name}.jpg", quality=92)


def main() -> None:
    categories = {
        "assembled_aircraft": sorted((ROOT / "实验截图/已经组装好的飞机真实图片").glob("*.*")),
        "taishan_debug": sorted((ROOT / "实验截图/泰山派调试截图").glob("*.*")),
        "flight": sorted((ROOT / "实验截图/飞机正式起飞截图").glob("*.png")),
        "training_results": sorted(
            (ROOT / "嵌入式系统的目标识别模型训练包/yolov5-7.0/runs/train").glob("exp*/results.png")
        ),
    }
    for name, paths in categories.items():
        if paths:
            make_sheet(paths, name)


if __name__ == "__main__":
    main()
