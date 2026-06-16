# 流程图渲染配置文件
# Scientific Research Color Scheme Configuration

# 科研配色方案
COLORS = {
    # 主要节点颜色
    'main_process': '#1f4e79',      # 深蓝色 - 主流程节点
    'sub_process': '#2e5d8a',       # 中蓝色 - 子流程节点
    'decision': '#ff7f00',          # 橙色 - 决策节点
    'start_end': '#404040',         # 深灰色 - 开始/结束节点
    'special': '#5b9bd5',           # 浅蓝色 - 特殊节点
    
    # 文字颜色
    'text_white': '#ffffff',        # 白色文字
    'text_black': '#000000',        # 黑色文字
    
    # 连接线颜色
    'edge_normal': '#404040',       # 普通连接线
    'edge_highlight': '#1f4e79',    # 重要路径连接线
    
    # 背景颜色
    'background': '#ffffff',        # 纯白背景
}

# 渲染参数
RENDER_CONFIG = {
    'dpi': 300,                     # 高分辨率输出
    'format': 'png',                # 输出格式
    'node_font_size': '12',         # 节点字体大小
    'edge_font_size': '10',         # 边标签字体大小
    'margin': '0.5',                # 页面边距
    'rankdir': 'TB',                # 默认布局方向（TB=自上而下）
    'node_height': '0.8',           # 节点高度
    'node_width': '1.5',            # 节点宽度
}

# 布局引擎选择
LAYOUT_ENGINES = {
    'hierarchical': 'dot',          # 层次化流程图
    'state_machine': 'fdp',         # 状态机图
    'complex_network': 'neato',     # 复杂网络图
    'circular': 'circo',            # 环形布局
    'force_directed': 'fdp',        # 力导向布局
}

# 节点形状定义
NODE_SHAPES = {
    'process': 'box',               # 处理节点 - 矩形
    'decision': 'diamond',          # 决策节点 - 菱形
    'start_end': 'ellipse',         # 开始/结束 - 椭圆
    'data': 'parallelogram',        # 数据节点 - 平行四边形
    'connector': 'circle',          # 连接点 - 圆形
}

# 字体配置
FONT_CONFIG = {
    'font_name': 'Microsoft YaHei', # 支持中文的字体
    'font_size_title': '14',        # 标题字体大小
    'font_size_normal': '11',       # 普通字体大小
    'font_size_small': '9',         # 小字体大小
}

# Graphviz 路径配置
GRAPHVIZ_CONFIG = {
    # 常见的 Graphviz 安装位置
    'common_paths': [
        'D:\\Graphviz\\bin',                    # 用户指定位置
        'C:\\Program Files\\Graphviz\\bin',     # 默认安装位置 64-bit
        'C:\\Program Files (x86)\\Graphviz\\bin', # 默认安装位置 32-bit
        'C:\\Graphviz\\bin',                    # 简化安装位置
        'D:\\Graphviz\\bin',                    # D盘安装位置
        'E:\\Graphviz\\bin',                    # E盘安装位置
    ],
    
    # 需要检查的可执行文件
    'executables': ['dot.exe', 'neato.exe', 'fdp.exe', 'circo.exe'],
    
    # Graphviz 环境变量
    'env_var': 'GRAPHVIZ_DOT',
} 