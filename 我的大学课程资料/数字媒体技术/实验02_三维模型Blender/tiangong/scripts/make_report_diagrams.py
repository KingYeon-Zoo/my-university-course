import base64
import html
import subprocess
from pathlib import Path


ROOT = Path("/Users/zoo/Desktop/数字媒体技术/实验02_三维模型Blender")
SCREENSHOTS = ROOT / "tiangong" / "screenshots"
FLAG = ROOT / "三维模型部分贴图" / "国旗1024 官方.png"
STAR = ROOT / "三维模型部分贴图" / "星空全景图.jpg"
CONVERTER = Path("/Users/zoo/Desktop/数字媒体技术/实验01_视频编辑ffmpeg/.conda-ffmpeg/bin/rsvg-convert")


def data_uri(path):
    suffix = path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    return f"data:image/{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def write_svg_png(svg_name, png_name, svg):
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    svg_path = SCREENSHOTS / svg_name
    png_path = SCREENSHOTS / png_name
    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run([str(CONVERTER), str(svg_path), "-o", str(png_path)], check=True)
    print(f"WROTE {png_path}")


def node_diagram():
    flag = data_uri(FLAG)
    star = data_uri(STAR)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <marker id="arrow" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto">
      <path d="M0,0 L14,7 L0,14 Z" fill="#6fb7ff"/>
    </marker>
    <style>
      .bg {{ fill: #10151f; }}
      .panel {{ fill: #17202c; stroke: #40556c; stroke-width: 2; rx: 12; }}
      .node {{ fill: #243244; stroke: #7aa7d9; stroke-width: 2; rx: 10; }}
      .node2 {{ fill: #2a273d; stroke: #b59aff; stroke-width: 2; rx: 10; }}
      .text {{ fill: #eef5ff; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 34px; }}
      .small {{ fill: #c8d7e8; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 25px; }}
      .tiny {{ fill: #9db2c8; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 21px; }}
      .arrow {{ stroke: #6fb7ff; stroke-width: 5; fill: none; marker-end: url(#arrow); }}
    </style>
  </defs>
  <rect class="bg" width="1600" height="1000"/>
  <text class="text" x="70" y="82">图 3 国旗贴图与星空环境节点设置</text>
  <text class="small" x="70" y="125">根据 Blender 文件中的材质节点和 World 节点整理，用于报告截图位置。</text>

  <rect class="panel" x="70" y="170" width="1460" height="330"/>
  <text class="text" x="110" y="230">国旗贴图材质：核心舱国旗贴图</text>
  <image href="{flag}" x="115" y="270" width="250" height="170" preserveAspectRatio="xMidYMid meet"/>
  <rect class="node" x="410" y="285" width="280" height="110"/>
  <text class="small" x="440" y="330">Image Texture</text>
  <text class="tiny" x="440" y="365">国旗1024 官方.png</text>
  <path class="arrow" d="M690 340 H810"/>
  <rect class="node" x="815" y="285" width="310" height="110"/>
  <text class="small" x="845" y="330">Principled BSDF</text>
  <text class="tiny" x="845" y="365">Base Color / Alpha</text>
  <path class="arrow" d="M1125 340 H1240"/>
  <rect class="node" x="1245" y="285" width="230" height="110"/>
  <text class="small" x="1275" y="330">Material Output</text>
  <text class="tiny" x="1275" y="365">核心舱国旗显示</text>

  <rect class="panel" x="70" y="545" width="1460" height="330"/>
  <text class="text" x="110" y="605">世界环境贴图：星空环境贴图</text>
  <image href="{star}" x="115" y="645" width="250" height="125" preserveAspectRatio="xMidYMid meet"/>
  <rect class="node2" x="410" y="650" width="300" height="115"/>
  <text class="small" x="440" y="695">Environment Texture</text>
  <text class="tiny" x="440" y="730">星空全景图.jpg</text>
  <path class="arrow" d="M710 707 H835"/>
  <rect class="node2" x="840" y="650" width="270" height="115"/>
  <text class="small" x="870" y="695">Background</text>
  <text class="tiny" x="870" y="730">Color / Strength 0.9</text>
  <path class="arrow" d="M1110 707 H1240"/>
  <rect class="node2" x="1245" y="650" width="230" height="115"/>
  <text class="small" x="1275" y="695">World Output</text>
  <text class="tiny" x="1275" y="730">星空渲染背景</text>

  <text class="tiny" x="70" y="935">文件：tiangong/output/tiangong_manual_modeling.blend　对象：国旗贴图_核心舱　World 节点：星空环境贴图</text>
</svg>'''
    write_svg_png("图3_材质与贴图节点.svg", "图3_材质与贴图节点.png", svg)


def collection_diagram():
    rows = [
        ("手动建模_展示与贴图", "新增模型展示集合，组织场景对象"),
        ("国旗贴图_核心舱", "核心舱国旗贴图平面"),
        ("展示说明牌", "展示主题说明牌"),
        ("标题文字", "中国空间站 Tiangong 文本"),
        ("展示轨道线", "空间展示轨道线"),
        ("主补光_Area", "区域补光"),
        ("太阳方向光", "太阳方向光"),
        ("相机01_国旗正面", "国旗正面渲染角度"),
        ("相机02_空间站斜俯视", "整体斜俯视渲染角度"),
        ("贴图坐标观察_平面", "彩色棋盘贴图观察"),
        ("贴图坐标观察_立方体", "彩色棋盘贴图观察"),
        ("贴图坐标观察_球体", "彩色棋盘贴图观察"),
        ("贴图坐标观察_柱体", "彩色棋盘贴图观察"),
    ]
    row_svg = []
    y = 205
    for i, (name, desc) in enumerate(rows):
        fill = "#1b2532" if i % 2 == 0 else "#202c3a"
        prefix = "▾ " if i == 0 else "   └ "
        row_svg.append(f'<rect x="80" y="{y - 35}" width="1440" height="54" fill="{fill}" rx="6"/>')
        row_svg.append(f'<text class="small" x="115" y="{y}">{html.escape(prefix + name)}</text>')
        row_svg.append(f'<text class="tiny" x="900" y="{y}">{html.escape(desc)}</text>')
        y += 58
    rows_joined = "\n  ".join(row_svg)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <style>
      .bg {{ fill: #111722; }}
      .panel {{ fill: #17202c; stroke: #41556c; stroke-width: 2; rx: 12; }}
      .text {{ fill: #eef5ff; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 34px; }}
      .small {{ fill: #e8f0fb; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 27px; }}
      .tiny {{ fill: #aebfd2; font-family: "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 23px; }}
    </style>
  </defs>
  <rect class="bg" width="1600" height="1000"/>
  <text class="text" x="70" y="82">图 4 手动建模集合与新增对象结构</text>
  <text class="tiny" x="70" y="125">根据 Blender 大纲视图中的对象命名整理，展示新增内容和用途。</text>
  <rect class="panel" x="55" y="155" width="1490" height="775"/>
  {rows_joined}
  <text class="tiny" x="80" y="955">空间站主体结构组件（如核心舱、实验舱、载人飞船等）保存在主场景集合中，新增的辅助展示组件统一放入手动建模展示集合，便于场景管理。</text>
</svg>'''
    write_svg_png("图4_手动建模集合结构.svg", "图4_手动建模集合结构.png", svg)


def main():
    if not CONVERTER.exists():
        raise FileNotFoundError(CONVERTER)
    node_diagram()
    collection_diagram()


if __name__ == "__main__":
    main()
