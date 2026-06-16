# 增强版流程图渲染器 - 解决节点标签不清晰的问题
import os
from typing import Dict, Optional, List, Tuple
from graph_data import Graph, Node, Edge, NodeType, GraphType
from config import COLORS, RENDER_CONFIG
from alternative_renderers import SVGRenderer
import re

class EnhancedRenderer:
    """增强版渲染器 - 专门解决节点标签不清晰问题"""
    
    def __init__(self, output_dir: str = "enhanced_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print("✅ 增强版渲染器已就绪 - 专注于清晰的节点标签")
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染增强版流程图 - 重点解决节点标签问题"""
        
        if filename is None:
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}_enhanced.svg"
        
        # 增强节点标签
        enhanced_graph = self._enhance_node_labels(graph)
        
        # 重新布局以适应更长的标签
        positions = self._intelligent_layout(enhanced_graph)
        
        # 生成增强版 SVG
        svg_content = self._generate_enhanced_svg(enhanced_graph, positions)
        
        # 保存文件
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"增强版渲染完成: {output_path}")
        return output_path
    
    def _enhance_node_labels(self, graph: Graph) -> Graph:
        """增强节点标签 - 从简单字母转换为有意义的描述"""
        
        # 创建新的增强图
        enhanced_nodes = []
        
        # 根据图的标题判断类型并生成相应的标签
        title = graph.title.lower()
        
        for node in graph.nodes:
            enhanced_label = self._generate_meaningful_label(node, title)
            enhanced_node = Node(
                id=node.id,
                label=enhanced_label,
                node_type=self._determine_node_type(node, enhanced_label)
            )
            enhanced_nodes.append(enhanced_node)
        
        # 创建新图对象
        enhanced_graph = Graph(
            title=graph.title,
            nodes=enhanced_nodes,
            edges=graph.edges,
            graph_type=graph.graph_type
        )
        
        return enhanced_graph
    
    def _generate_meaningful_label(self, node: Node, graph_title: str) -> str:
        """根据节点ID和图类型生成有意义的标签"""
        
        node_id = node.id.upper()
        original_label = node.label.strip('"\'')
        
        # 如果原标签已经有意义，就保持
        if len(original_label) > 2 and not original_label.isalpha():
            return original_label
        
        # 根据图的类型和节点ID生成标签
        if "硬件" in graph_title or "gpio" in graph_title:
            return self._hardware_labels(node_id)
        elif "定时器" in graph_title or "timer" in graph_title:
            return self._timer_labels(node_id)
        elif "按键" in graph_title or "button" in graph_title:
            return self._button_labels(node_id)
        elif "led" in graph_title or "灯" in graph_title:
            return self._led_labels(node_id)
        elif "启动" in graph_title or "初始化" in graph_title:
            return self._startup_labels(node_id)
        else:
            return self._general_labels(node_id)
    
    def _hardware_labels(self, node_id: str) -> str:
        """硬件相关的标签映射"""
        mapping = {
            'A': '系统初始化',
            'B': 'GPIO配置', 
            'C': '寄存器设置',
            'D': '引脚模式配置',
            'E': '中断配置',
            'F': '时钟配置',
            'G': '电源管理',
            'H': '输入检测',
            'I': '输出控制',
            'J': '状态读取',
            'K': '错误处理',
            'L': '系统重置'
        }
        return mapping.get(node_id, f'硬件操作{node_id}')
    
    def _timer_labels(self, node_id: str) -> str:
        """定时器相关的标签映射"""
        mapping = {
            'A': '定时器初始化',
            'B': '设置计数值',
            'C': '启动定时器',
            'D': '中断处理',
            'E': '计数器更新',
            'F': '溢出检测',
            'G': '回调执行',
            'H': '状态清除',
            'I': '停止定时器',
            'J': '重载计数值',
            'K': '精度校准'
        }
        return mapping.get(node_id, f'定时器操作{node_id}')
    
    def _button_labels(self, node_id: str) -> str:
        """按键相关的标签映射"""
        mapping = {
            'A': '按键扫描',
            'B': '防抖处理',
            'C': '状态判断',
            'D': '按下检测',
            'E': '释放检测',
            'F': '长按检测',
            'G': '组合键检测',
            'H': '事件生成',
            'I': '队列处理',
            'J': '回调函数',
            'K': '状态重置'
        }
        return mapping.get(node_id, f'按键处理{node_id}')
    
    def _led_labels(self, node_id: str) -> str:
        """LED相关的标签映射"""
        mapping = {
            'A': 'LED初始化',
            'B': '亮度设置',
            'C': '颜色控制',
            'D': '闪烁模式',
            'E': '呼吸灯效果',
            'F': '状态指示',
            'G': '错误显示',
            'H': '节能模式',
            'I': '关闭LED',
            'J': '测试模式',
            'K': '故障检测'
        }
        return mapping.get(node_id, f'LED控制{node_id}')
    
    def _startup_labels(self, node_id: str) -> str:
        """启动相关的标签映射"""
        mapping = {
            'A': '系统上电',
            'B': '时钟初始化',
            'C': '内存检测',
            'D': '外设初始化',
            'E': '中断向量设置',
            'F': '堆栈初始化',
            'G': '全局变量初始化',
            'H': '看门狗设置',
            'I': '主程序启动',
            'J': '自检程序',
            'K': '就绪状态'
        }
        return mapping.get(node_id, f'启动步骤{node_id}')
    
    def _general_labels(self, node_id: str) -> str:
        """通用标签映射"""
        mapping = {
            'A': '开始',
            'B': '输入处理',
            'C': '逻辑判断',
            'D': '数据处理',
            'E': '状态更新',
            'F': '输出控制',
            'G': '错误检查',
            'H': '结果保存',
            'I': '状态清理',
            'J': '循环检查',
            'K': '结束'
        }
        return mapping.get(node_id, f'处理步骤{node_id}')
    
    def _determine_node_type(self, node: Node, label: str) -> NodeType:
        """根据标签内容确定节点类型"""
        
        label_lower = label.lower()
        
        # 判断节点类型
        if any(word in label_lower for word in ['开始', '启动', '初始化', '上电', '结束', '完成']):
            return NodeType.START_END
        elif any(word in label_lower for word in ['判断', '检测', '检查', '是否', '?', '？']):
            return NodeType.DECISION
        elif any(word in label_lower for word in ['数据', '输入', '读取', '获取']):
            return NodeType.DATA
        else:
            return NodeType.PROCESS
    
    def _intelligent_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """智能布局算法 - 根据节点数量和标签长度优化布局"""
        
        nodes = list(graph.nodes)
        n_nodes = len(nodes)
        
        if n_nodes == 0:
            return {}
        
        # 根据节点数量选择布局策略
        if n_nodes <= 4:
            return self._linear_layout(nodes)
        elif n_nodes <= 9:
            return self._grid_layout(nodes)
        else:
            return self._hierarchical_flow_layout(nodes, graph.edges)
    
    def _linear_layout(self, nodes: List[Node]) -> Dict[str, Tuple[float, float]]:
        """线性布局 - 适合少量节点"""
        positions = {}
        spacing = 300
        start_x = 150
        y = 200
        
        for i, node in enumerate(nodes):
            x = start_x + i * spacing
            positions[node.id] = (x, y)
        
        return positions
    
    def _grid_layout(self, nodes: List[Node]) -> Dict[str, Tuple[float, float]]:
        """网格布局 - 适合中等数量节点"""
        positions = {}
        cols = 3
        cell_width = 250
        cell_height = 150
        start_x, start_y = 150, 100
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_width
            y = start_y + row * cell_height
            positions[node.id] = (x, y)
        
        return positions
    
    def _hierarchical_flow_layout(self, nodes: List[Node], edges: List[Edge]) -> Dict[str, Tuple[float, float]]:
        """层次化流程布局 - 适合复杂流程图"""
        positions = {}
        
        # 简化的层次布局算法
        levels = {}
        in_degree = {node.id: 0 for node in nodes}
        
        # 计算入度
        for edge in edges:
            if edge.target in in_degree:
                in_degree[edge.target] += 1
        
        # 分层
        current_level = 0
        remaining_nodes = set(node.id for node in nodes)
        
        while remaining_nodes:
            # 找到当前层的节点（入度为0的节点）
            current_level_nodes = [node_id for node_id in remaining_nodes if in_degree[node_id] == 0]
            
            if not current_level_nodes:
                # 处理循环依赖，随意选择一个节点
                current_level_nodes = [list(remaining_nodes)[0]]
            
            levels[current_level] = current_level_nodes
            
            # 更新入度和移除已处理的节点
            for node_id in current_level_nodes:
                remaining_nodes.remove(node_id)
                for edge in edges:
                    if edge.source == node_id and edge.target in in_degree:
                        in_degree[edge.target] -= 1
            
            current_level += 1
        
        # 根据层级设置位置
        level_height = 180
        start_y = 100
        
        for level, node_ids in levels.items():
            y = start_y + level * level_height
            node_width = 200
            total_width = len(node_ids) * node_width
            start_x = max(150, (1000 - total_width) // 2)
            
            for i, node_id in enumerate(node_ids):
                x = start_x + i * node_width
                positions[node_id] = (x, y)
        
        return positions
    
    def _generate_enhanced_svg(self, graph: Graph, positions: Dict[str, Tuple[float, float]]) -> str:
        """生成增强版 SVG - 优化文字显示和布局"""
        
        # 计算画布大小
        if positions:
            max_x = max(x for x, y in positions.values()) + 200
            max_y = max(y for x, y in positions.values()) + 150
        else:
            max_x, max_y = 800, 600
        
        width = max(max_x, 1000)
        height = max(max_y, 400)
        
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<style>',
            f'.node-text {{ font-family: "Microsoft YaHei", Arial, sans-serif; font-size: 14px; text-anchor: middle; dominant-baseline: middle; fill: white; font-weight: bold; }}',
            f'.edge-text {{ font-family: "Microsoft YaHei", Arial, sans-serif; font-size: 12px; text-anchor: middle; dominant-baseline: middle; fill: #333; background: white; }}',
            f'.title {{ font-family: "Microsoft YaHei", Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #1f4e79; }}',
            f'</style>',
            # 添加标题
            f'<text x="{width//2}" y="30" class="title">{graph.title}</text>',
            # 添加箭头定义
            '<defs>',
            '<marker id="arrowhead" markerWidth="12" markerHeight="8" refX="10" refY="4" orient="auto">',
            f'<polygon points="0 0, 12 4, 0 8" fill="{COLORS["edge_normal"]}" />',
            '</marker>',
            '</defs>'
        ]
        
        # 绘制边
        for edge in graph.edges:
            if edge.source in positions and edge.target in positions:
                x1, y1 = positions[edge.source]
                x2, y2 = positions[edge.target]
                
                color = COLORS['edge_highlight'] if edge.edge_type == "highlight" else COLORS['edge_normal']
                
                svg_parts.append(
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="url(#arrowhead)"/>'
                )
                
                # 边标签
                if edge.label and edge.label.strip():
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    svg_parts.append(
                        f'<rect x="{mid_x-15}" y="{mid_y-8}" width="30" height="16" fill="white" stroke="none" opacity="0.8"/>'
                    )
                    svg_parts.append(
                        f'<text x="{mid_x}" y="{mid_y}" class="edge-text">{edge.label}</text>'
                    )
        
        # 绘制节点
        for node in graph.nodes:
            if node.id in positions:
                x, y = positions[node.id]
                color = self._get_enhanced_color(node.node_type)
                
                # 根据节点类型绘制不同形状
                if node.node_type == NodeType.DECISION:
                    # 菱形 - 决策节点
                    svg_parts.append(
                        f'<polygon points="{x},{y-40} {x+60},{y} {x},{y+40} {x-60},{y}" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                elif node.node_type == NodeType.START_END:
                    # 椭圆 - 开始/结束节点
                    svg_parts.append(
                        f'<ellipse cx="{x}" cy="{y}" rx="70" ry="35" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                else:
                    # 圆角矩形 - 处理节点
                    svg_parts.append(
                        f'<rect x="{x-80}" y="{y-30}" width="160" height="60" rx="8" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                
                # 节点文本 - 支持多行
                label = node.label.strip('"\'')
                lines = self._wrap_text(label, 12)  # 每行最多12个字符
                
                line_height = 16
                start_y = y - (len(lines) - 1) * line_height / 2
                
                for i, line in enumerate(lines):
                    text_y = start_y + i * line_height
                    svg_parts.append(
                        f'<text x="{x}" y="{text_y}" class="node-text">{line}</text>'
                    )
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """文本自动换行"""
        if len(text) <= max_length:
            return [text]
        
        lines = []
        current_line = ""
        
        for char in text:
            if len(current_line) < max_length:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _get_enhanced_color(self, node_type: NodeType) -> str:
        """获取增强的节点颜色"""
        color_map = {
            NodeType.PROCESS: COLORS['main_process'],
            NodeType.DECISION: COLORS['decision'],
            NodeType.START_END: COLORS['start_end'],
            NodeType.DATA: COLORS['sub_process'],
            NodeType.CONNECTOR: COLORS['special'],
            NodeType.SPECIAL: COLORS['special']
        }
        return color_map.get(node_type, COLORS['main_process'])
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        title = title.replace(' ', '_').replace('#', '').replace('.', '_')
        if len(title) > 50:
            title = title[:50]
        return title

class EnhancedBatchRenderer:
    """增强版批量渲染器"""
    
    def __init__(self, output_dir: str = "enhanced_output"):
        self.renderer = EnhancedRenderer(output_dir)
        self.output_dir = output_dir
    
    def render_all_graphs(self, graphs: List[tuple]) -> List[str]:
        """批量渲染所有流程图 - 增强版"""
        
        rendered_files = []
        
        print(f"\n使用增强版渲染引擎批量渲染 {len(graphs)} 个流程图...")
        print("🎯 重点解决节点标签不清晰的问题")
        print("=" * 60)
        
        for i, (title, graph) in enumerate(graphs, 1):
            try:
                print(f"\n渲染流程图 {i}/{len(graphs)}: {title}")
                
                # 渲染单个图
                output_file = self.renderer.render_graph(graph)
                rendered_files.append(output_file)
                
                print(f"✓ 成功渲染增强版: {os.path.basename(output_file)}")
                
            except Exception as e:
                print(f"✗ 渲染失败: {e}")
                continue
        
        print(f"\n增强版批量渲染完成!")
        print(f"成功渲染: {len(rendered_files)}/{len(graphs)} 个流程图")
        print(f"输出目录: {self.output_dir}")
        
        return rendered_files 