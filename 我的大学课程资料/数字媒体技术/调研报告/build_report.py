from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "调研报告.md"
OUTPUT = ROOT / "调研报告-规范版.md"
MEDIA = ROOT / "media"


def make_signature(text: str, font_path: str, output: Path, angle: float) -> None:
    canvas = Image.new("RGBA", (780, 220), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(font_path, 128)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    x = (canvas.width - (bbox[2] - bbox[0])) // 2
    y = (canvas.height - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(20, 42, 90, 245),
        stroke_width=1,
        stroke_fill=(20, 42, 90, 180),
    )
    canvas = canvas.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    alpha = canvas.getchannel("A").filter(ImageFilter.GaussianBlur(0.35))
    canvas.putalpha(alpha)
    canvas.save(output)


def clean(text: str) -> str:
    text = re.sub(r"(?:cite|navlist).*?", "", text)
    text = text.replace("——", "：")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def section(source: str, heading: str, next_heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)\n## {re.escape(next_heading)}"
    match = re.search(pattern, source, flags=re.S)
    if not match:
        raise RuntimeError(f"未找到章节：{heading}")
    return clean(match.group(1))


MEDIA.mkdir(exist_ok=True)
make_signature(
    "朱清扬",
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc",
    MEDIA / "signature_zhu.png",
    -2.0,
)
make_signature(
    "李奕霖",
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/a3c69464b629577766c23bcdb12ffbfe3759b923.asset/AssetData/Hanzipen.ttc",
    MEDIA / "signature_li.png",
    1.5,
)

source = SOURCE.read_text(encoding="utf-8")
intro = section(source, "引言与问题界定", "产业背景与产品演进")
academic = section(source, "学术研究与方法证据", "开源生态与工业佐证")
workflow = section(source, "多智能体创作流程重构", "关键挑战与未来趋势")

industry = """
生成式视频的产品演进表明，行业关注点已经从“能否由文字生成一个短片段”转向“能否围绕多个镜头持续创作”。OpenAI 在 Sora 的产品界面中引入 storyboard、extend、remix 与 blend 等功能，使用户能够以分镜和已有素材为中间控制手段。Google 在 2025 年推出 Flow，将 Veo、Imagen 与 Gemini 组织为面向电影化创作的工具，并提供 Camera Controls、Scenebuilder 与 Asset Management。两者都说明，视频生成产品正在主动补齐镜头规划、素材管理和连续编辑能力。

Google Flow 对“ingredients”的设计尤其具有代表性。创作者可以把角色、物体和风格参考作为可复用资产，再在不同镜头中调用；Frames to Video 则允许指定起止画面，为镜头衔接提供更精确的控制。它并没有把提示词视为唯一输入，而是把参考资产、镜头状态和项目上下文共同纳入生成过程。这种产品结构与传统影视制作中的角色设定、场景设定和镜头表具有明显对应关系。

![Google Flow 官方宣传画面](media/google_flow.png){width=5.6in}

**图1. Google Flow 将生成模型组织为面向镜头与场景的创作工具**

Adobe 的路线更强调生成与既有后期流程的结合。Firefly Video 支持文本生成视频、图像生成视频、相机角度控制以及首尾帧约束；Premiere Pro 中的 Generative Extend 则把生成能力直接放入时间线，用于补足画面或音频长度。Adobe 还在 Firefly 中整合自有模型和合作伙伴模型，使创作者能够在同一工作环境中完成构思、生成、编辑与交付。其价值不只是模型数量增加，而是降低多模型切换、素材搬运和版本管理的成本。

![Adobe Firefly Video 官方产品画面](media/adobe_firefly.jpg){width=5.6in}

**图2. Adobe Firefly Video 面向生成、编辑与后期衔接的一体化界面**

Runway、Luma 以及国内的可灵、Seedance、Wan 等产品也持续强化参考图驱动、角色一致性、视频编辑、镜头延展和音画协同。不同厂商的技术路线并不相同，但产品功能正在趋向同一目标：把一次性生成改造成可反复调整的镜头生产环节。由此可见，未来竞争不仅取决于基础模型的画质，还取决于系统能否管理角色、场景、音频、版本、成本和质量反馈。

综合上述产品，可以把产业趋势归纳为四点：视频生成由无声片段走向音画协同；控制方式由单一提示词扩展到分镜、参考图、首尾帧、相机参数和时间线；产品由单模型入口走向多模型创作平台；评价重点由“第一眼是否惊艳”转向“能否复用、修改、审校并进入真实生产流程”。这些变化共同构成多智能体与流程化创作兴起的产业基础。

**表1. 典型 AI 视频产品的流程化能力比较**

| 产品或系统 | 主要控制方式 | 对工作流的意义 |
|:---:|:---|:---|
| Sora | Storyboard、扩展、混合、重制 | 用分镜和既有素材控制生成过程 |
| Google Flow | Ingredients、相机控制、Scenebuilder | 管理跨镜头角色、物体与场景 |
| Adobe Firefly | 首尾帧、相机参数、时间线与模型选择 | 连接构思、生成、后期和交付 |
| Runway / Luma | 视频编辑、运动迁移、版本迭代 | 强化镜头修改与多版本比较 |
| 可灵 / Seedance / Wan | 参考图、多镜头、音画协同、视频编辑 | 面向短视频与本土创作场景完善生产能力 |
"""

opensource = """
开源生态可以检验一种技术是否具备可组合、可复现和可扩展的基础。ComfyUI 的节点式界面允许用户把文本编码、图像参考、视频模型、结构控制、插帧、放大和导出等环节连接成图形化流程。其意义在于，创作者不必把全部能力寄托于一个模型，而可以根据镜头需求替换节点、保存流程并复用参数。AnimateDiff、CogVideoX、HunyuanVideo、Wan 等项目对 ComfyUI 或 Diffusers 的适配，又进一步增强了这种模块化趋势。

多智能体开源项目则从另一侧补足流程组织能力。CrewAI、AutoGen 等通用框架提供角色、任务、工具和流程控制机制；MM-StoryAgent 等垂直项目把故事写作、图像、语音、音效、音乐与视频合成组织为多阶段管线。它们说明，多智能体视频系统并不一定需要从零训练一个巨型模型，而可以通过明确的数据接口和调度机制，把语言模型、生成模型、传统算法与人工审核组合起来。

![MM-StoryAgent 多模态智能体框架](media/mm_storyagent.png){width=5.8in}

**图3. MM-StoryAgent 将文本、图像、语音、音效和音乐智能体组织为视频生产管线**

当然，开源项目的关注度并不等同于工业成熟度。节点依赖、显存需求、模型许可证、版本兼容和生成稳定性仍会提高部署门槛。但从技术形态看，真正活跃的方向已经不仅是“训练更大的视频模型”，还包括“构建更可靠的编排层”。这与商业产品从单点生成走向项目化创作的趋势形成相互印证。
"""

challenges = """
首先，长时序一致性仍是最核心的技术难题。人物外观、服饰、场景布局和物体状态需要跨镜头保持稳定，而现有系统往往通过多个短片段拼接完整短片。镜头越多，上游设定的微小偏差越容易被放大。因此，多智能体流程必须维护角色与场景资料，并把一致性检查作为持续任务，而不能只在最终导出时检查。

其次，镜头控制与创意保真之间存在张力。参考图、首尾帧、相机参数和时间标签提高了可控性，却也增加了操作复杂度。系统需要把创作者的自然语言意图转换为可执行的镜头参数，并在结果偏离时解释偏差来源。导演或分镜智能体的价值正在于建立“创意描述—镜头结构—模型参数”之间的映射，而不是简单扩写提示词。

第三，音画同步、成本调度和质量评估正在成为同等重要的工程问题。完整短片不仅需要画面，还需要对白、配音、环境声、音乐、字幕和节奏。不同模型的计费方式、生成速度和擅长场景不同，系统必须根据镜头重要程度选择模型与重试次数。VBench、VBench-2.0、DEVIL 和 VideoGen-Eval 等工作表明，自动评价也需要覆盖主体一致性、时间平滑、动态程度、物理合理性和文本对齐等多个维度。

第四，版权、安全和内容溯源必须进入工作流本身。参考素材是否具有使用权、生成内容是否模仿特定作者、人物肖像是否获得授权、输出是否保留 Content Credentials 或 C2PA 信息，都不能只依赖最终人工检查。较合理的做法是设置专门的审校智能体，对素材来源、提示词、模型版本、生成参数和修改记录进行留痕，并由人类完成最终确认。

基于上述问题，未来 AI 视频创作可能呈现五种趋势：创作交互从提示词工程转向智能体协作；生成对象从单片段转向以场景和镜头表为中间表示的短片工程；平台从单模型入口转向多模型路由；评价从单一视觉分数转向多维自动检查与人工审片结合；人的角色从逐项制作素材，逐步转向定义目标、维护审美边界、处理例外并作最终裁决。多智能体不会自动消除创作难度，但有望把复杂流程变得更可管理。
"""

conclusion = """
本次调研表明，AI 视频创作正在从单模型、单片段的生成方式，转向由模型、工具、数据资产、编辑界面和多智能体共同组成的生产流程。Sora、Google Flow、Adobe Firefly 等产品把分镜、参考资产、相机控制和时间线纳入生成界面；StoryAgent、MM-StoryAgent、VideoDiff 等研究把任务分解、人机协同和质量评价纳入系统设计；ComfyUI 等开源工具则提供了可组合的模型编排基础。三方面证据共同说明，决定系统实用性的关键已经不只是画质，还包括一致性、可控性、可编辑性、可追溯性与协作效率。

对于数字媒体技术学习者而言，这一变化意味着能力结构也需要调整。除了理解扩散模型和视频生成原理，还应掌握分镜表达、素材规范、工作流设计、模型选路、自动评价、版权审查和人机交互。未来更有价值的实践，不是追求“一句话生成完整影片”的表面自动化，而是设计一条能够保留创意主导权、允许局部修改、支持质量反馈并可稳定复用的 AI 原生内容生产线。
"""

report = f"""# 2026年《数字媒体技术》课程调研报告

## 从文本到短片：多智能体协同在 AI 视频生成与数字媒体创作流程中的应用调研

| 项目 | 信息 |
|:---:|:---|
| 班级 | 计科 23-3 班 |
| 成员 1 | 朱清扬，2023212290 |
| 成员 2 | 李奕霖，2023215332 |
| 日期 | 2026.06.13 |

# 调研报告摘要

本文围绕 AI 视频创作由单模型生成向多智能体协同流程演进的趋势展开调研，综合分析 Sora、Google Flow、Adobe Firefly 等产品，StoryAgent、VideoDiff、VBench 等研究，以及 ComfyUI、MM-StoryAgent 等开源项目。调研发现，行业竞争重点正由单段视频画质转向分镜控制、角色一致性、音画协同、时间线编辑、模型路由和质量反馈。多智能体系统可将需求理解、编剧、分镜、素材管理、生成、声音、剪辑与审校分配给不同角色，并由人类负责目标、审美和最终决策。其主要瓶颈仍包括长时序一致性、控制复杂度、自动评价、成本、版权与溯源。

本调研团队由朱清扬（2023212290）与李奕霖（2023215332）组成。朱清扬担任队长，主导选题设计、资料检索方案、产品与论文分析、整体结构规划、主要章节撰写、图表整理和终稿统筹；李奕霖参与资料筛选与交叉核对，协助整理国内外案例、开源项目和参考文献，并对报告语言与格式进行复核。

**关键词：** AI 视频生成；多智能体系统；数字媒体创作；工作流；人机协同

**调研团队成员电子签名：**

| 朱清扬 | 李奕霖 |
|:---:|:---:|
| ![朱清扬电子签名](media/signature_zhu.png){{width=1.6in}} | ![李奕霖电子签名](media/signature_li.png){{width=1.6in}} |

# 调研报告正文

## 引言与问题界定

{intro}

## 产业背景与产品演进

{clean(industry)}

## 学术研究与方法证据

{academic}

## 开源生态与工业佐证

{clean(opensource)}

## 多智能体创作流程重构

{workflow}

## 关键挑战与未来趋势

{clean(challenges)}

## 结论

{clean(conclusion)}

# 参考文献

1. Brooks T, Peebles B, Holmes C, et al. Video generation models as world simulators[EB/OL]. OpenAI, 2024. https://openai.com/index/video-generation-models-as-world-simulators/
2. OpenAI. Sora is here[EB/OL]. 2024-12-09. https://openai.com/index/sora-is-here/
3. Google. Meet Flow: AI-powered filmmaking with Veo 3[EB/OL]. 2025-05-20. https://blog.google/innovation-and-ai/products/google-flow-veo-ai-filmmaking-tool/
4. Adobe. Adobe Expands Generative AI Offerings Delivering New Firefly App[EB/OL]. 2025-02-12. https://news.adobe.com/news/2025/02/firefly-web-app-commercially-safe
5. Adobe. New AI Innovation in Adobe Premiere Pro[EB/OL]. 2025-04-02. https://news.adobe.com/news/2025/04/new-ai-innovation-in-industry
6. Ho J, Salimans T, Gritsenko A, et al. Video Diffusion Models[C]. NeurIPS, 2022.
7. Bar-Tal O, Chefer H, Tov O, et al. Lumiere: A Space-Time Diffusion Model for Video Generation[EB/OL]. arXiv:2401.12945, 2024.
8. Wu J Z, Ge Y, Wang X, et al. Tune-A-Video: One-Shot Tuning of Image Diffusion Models for Text-to-Video Generation[C]. ICCV, 2023.
9. Yang S, Gao R, Wang H, et al. Direct-a-Video: Customized Video Generation with User-Directed Camera and Motion[C]. SIGGRAPH, 2024.
10. Hu P, Jiang J, Chen J, et al. StoryAgent: Customized Storytelling Video Generation via Multi-Agent Collaboration[EB/OL]. arXiv:2411.04925, 2024.
11. Xu X, Mei J, Li C, et al. MM-StoryAgent: Immersive Narrated Storybook Video Generation with a Multi-Agent Paradigm across Text, Image and Audio[EB/OL]. arXiv:2503.05242, 2025.
12. Huh M, Li D, et al. VideoDiff: Human-AI Video Co-Creation with Alternatives[C]. CHI, 2025.
13. Huang Z, Zhang Y, et al. VBench: Comprehensive Benchmark Suite for Video Generative Models[C]. CVPR, 2024.
14. Zheng D, Zhang Y, et al. VBench-2.0: Advancing Video Generation Benchmark for Intrinsic Faithfulness[EB/OL]. arXiv, 2025.
15. Yang Y, Fan K, et al. VideoGen-Eval: Agent-based System for Video Generation Evaluation[EB/OL]. arXiv, 2025.
16. Comfy-Org. ComfyUI[EB/OL]. https://github.com/Comfy-Org/ComfyUI
17. X-PLUG. MM-StoryAgent[EB/OL]. https://github.com/X-PLUG/MM_StoryAgent
18. Wan-Video. Wan2.1[EB/OL]. https://github.com/Wan-Video/Wan2.1

# 调研报告成绩评定表

此表格用于教师评分，学生不自行填写。验收项不计得分，未提交为 0 分，迟交按课程要求扣分。

| 序号 | 评价内容 | 分值范围 | 得分 |
|:---:|:---|:---:|:---:|
| 验收 | 是否按时提交 | - |  |
| 1 | 报告格式是否规范，语言使用是否规范，行文是否流畅。 | 1-5 |  |
| 2 | 调研内容是否详实、描述是否恰当；是否图文并茂、逻辑清晰、条理清楚。 | 1-5 |  |
| 3 | 调研分工是否清楚；素材是否经过凝练、归纳、整理与再加工；是否提出自己的分析与见解。 | 1-5 |  |
| 最终得分 |  | 3-15 |  |

指导教师签章：____________________    日期：____________________
"""

OUTPUT.write_text(clean(report) + "\n", encoding="utf-8")
print(OUTPUT)
