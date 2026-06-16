# 替代渲染引擎集合
import os
import json
from typing import Dict, Optional, List, Tuple
from graph_data import Graph, Node, Edge, NodeType, GraphType
from config import COLORS, RENDER_CONFIG

# ================================
# 1. Plotly 交互式渲染器
# ================================

class PlotlyRenderer:
    """基于 Plotly 的交互式流程图渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
            self.go = go
            self.pyo = pyo
            self.available = True
            print("✅ Plotly 渲染器已就绪")
        except ImportError:
            self.available = False
            print("❌ Plotly 未安装，无法使用交互式渲染")
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染交互式流程图"""
        
        if not self.available:
            raise ImportError("Plotly 未安装")
        
        if filename is None:
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}_interactive.html"
        
        # 计算布局
        positions = self._force_directed_layout(graph)
        
        # 创建边的轨迹
        edge_traces = self._create_edge_traces(graph, positions)
        
        # 创建节点的轨迹
        node_trace = self._create_node_trace(graph, positions)
        
        # 创建图形
        fig = self.go.Figure(data=edge_traces + [node_trace],
                            layout=self.go.Layout(
                                title=graph.title,
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20,l=5,r=5,t=40),
                                annotations=[ dict(
                                    text="拖拽节点进行交互",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.005, y=-0.002,
                                    xanchor="left", yanchor="bottom",
                                    font=dict(color="#888", size=12)
                                )],
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                paper_bgcolor='white',
                                plot_bgcolor='white'
                            ))
        
        # 保存为 HTML
        output_path = os.path.join(self.output_dir, filename)
        self.pyo.plot(fig, filename=output_path, auto_open=False)
        
        print(f"交互式渲染完成: {output_path}")
        return output_path
    
    def _force_directed_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """力导向布局算法"""
        import random
        import math
        
        nodes = list(graph.nodes)
        n_nodes = len(nodes)
        
        if n_nodes == 0:
            return {}
        
        # 初始化随机位置
        positions = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n_nodes
            radius = 2
            x = radius * math.cos(angle) + random.uniform(-0.5, 0.5)
            y = radius * math.sin(angle) + random.uniform(-0.5, 0.5)
            positions[node.id] = (x, y)
        
        # 简化的力导向算法
        for iteration in range(50):
            forces = {node.id: (0, 0) for node in nodes}
            
            # 计算斥力
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes[i+1:], i+1):
                    x1, y1 = positions[node1.id]
                    x2, y2 = positions[node2.id]
                    
                    dx, dy = x1 - x2, y1 - y2
                    distance = math.sqrt(dx*dx + dy*dy) + 0.01
                    
                    # 斥力
                    force = 0.5 / (distance * distance)
                    fx, fy = force * dx / distance, force * dy / distance
                    
                    fx1, fy1 = forces[node1.id]
                    forces[node1.id] = (fx1 + fx, fy1 + fy)
                    
                    fx2, fy2 = forces[node2.id]
                    forces[node2.id] = (fx2 - fx, fy2 - fy)
            
            # 计算引力
            for edge in graph.edges:
                if edge.source in positions and edge.target in positions:
                    x1, y1 = positions[edge.source]
                    x2, y2 = positions[edge.target]
                    
                    dx, dy = x2 - x1, y2 - y1
                    distance = math.sqrt(dx*dx + dy*dy) + 0.01
                    
                    # 引力
                    force = 0.01 * distance
                    fx, fy = force * dx / distance, force * dy / distance
                    
                    fx1, fy1 = forces[edge.source]
                    forces[edge.source] = (fx1 + fx, fy1 + fy)
                    
                    fx2, fy2 = forces[edge.target]
                    forces[edge.target] = (fx2 - fx, fy2 - fy)
            
            # 更新位置
            for node in nodes:
                fx, fy = forces[node.id]
                x, y = positions[node.id]
                
                # 限制移动步长
                step = 0.1
                x += fx * step
                y += fy * step
                
                positions[node.id] = (x, y)
        
        return positions
    
    def _create_edge_traces(self, graph: Graph, positions: Dict[str, Tuple[float, float]]) -> List:
        """创建边的轨迹"""
        edge_traces = []
        
        for edge in graph.edges:
            if edge.source not in positions or edge.target not in positions:
                continue
            
            x0, y0 = positions[edge.source]
            x1, y1 = positions[edge.target]
            
            color = COLORS['edge_highlight'] if edge.edge_type == "highlight" else COLORS['edge_normal']
            
            edge_trace = self.go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                line=dict(width=2, color=color),
                hoverinfo='none',
                mode='lines'
            )
            edge_traces.append(edge_trace)
        
        return edge_traces
    
    def _create_node_trace(self, graph: Graph, positions: Dict[str, Tuple[float, float]]):
        """创建节点轨迹"""
        node_x = []
        node_y = []
        node_colors = []
        node_text = []
        node_info = []
        
        for node in graph.nodes:
            if node.id in positions:
                x, y = positions[node.id]
                node_x.append(x)
                node_y.append(y)
                node_colors.append(self._get_plotly_color(node.node_type))
                node_text.append(node.label.strip('"\''))
                node_info.append(f"类型: {node.node_type.value}<br>标签: {node.label}")
        
        node_trace = self.go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                showscale=False,
                color=node_colors,
                size=30,
                line=dict(width=2, color="black")
            ),
            textfont=dict(color="white", size=10)
        )
        
        return node_trace
    
    def _get_plotly_color(self, node_type: NodeType) -> str:
        """获取 Plotly 节点颜色"""
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

# ================================
# 2. NetworkX + Matplotlib 渲染器
# ================================

class NetworkXRenderer:
    """基于 NetworkX 的网络图渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            self.nx = nx
            self.plt = plt
            self.mpatches = mpatches
            self.available = True
            print("✅ NetworkX 渲染器已就绪")
        except ImportError:
            self.available = False
            print("❌ NetworkX 未安装，无法使用网络图渲染")
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染网络图"""
        
        if not self.available:
            raise ImportError("NetworkX 未安装")
        
        if filename is None:
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}_network.png"
        
        # 创建 NetworkX 图
        G = self.nx.DiGraph()
        
        # 添加节点
        for node in graph.nodes:
            G.add_node(node.id, label=node.label, node_type=node.node_type)
        
        # 添加边
        for edge in graph.edges:
            G.add_edge(edge.source, edge.target, label=edge.label, edge_type=edge.edge_type)
        
        # 选择布局算法
        if graph.graph_type == GraphType.STATE_MACHINE:
            pos = self.nx.circular_layout(G)
        elif len(graph.nodes) > 15:
            pos = self.nx.spring_layout(G, k=3, iterations=50)
        else:
            pos = self.nx.hierarchical_layout(G) if hasattr(self.nx, 'hierarchical_layout') else self.nx.spring_layout(G)
        
        # 创建图形
        fig, ax = self.plt.subplots(1, 1, figsize=(14, 10))
        
        # 按类型分组绘制节点
        node_types = {}
        for node in graph.nodes:
            if node.node_type not in node_types:
                node_types[node.node_type] = []
            node_types[node.node_type].append(node.id)
        
        # 绘制不同类型的节点
        for node_type, node_ids in node_types.items():
            color = self._get_networkx_color(node_type)
            shape = self._get_networkx_shape(node_type)
            self.nx.draw_networkx_nodes(G, pos, nodelist=node_ids, 
                                       node_color=color, node_shape=shape,
                                       node_size=2000, alpha=0.9, ax=ax)
        
        # 绘制边
        self.nx.draw_networkx_edges(G, pos, edge_color=COLORS['edge_normal'],
                                   arrows=True, arrowsize=20, arrowstyle='->', 
                                   width=2, alpha=0.8, ax=ax)
        
        # 绘制节点标签
        labels = {}
        for node in graph.nodes:
            label = node.label.strip('"\'')
            if len(label) > 10:
                label = label[:8] + '...'
            labels[node.id] = label
        
        self.nx.draw_networkx_labels(G, pos, labels, font_size=8, 
                                    font_color='white', font_weight='bold', ax=ax)
        
        # 绘制边标签
        edge_labels = {}
        for edge in graph.edges:
            if edge.label:
                edge_labels[(edge.source, edge.target)] = edge.label
        
        if edge_labels:
            self.nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7, ax=ax)
        
        # 设置图形属性
        ax.set_title(graph.title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # 添加图例
        legend_elements = []
        for node_type in node_types.keys():
            color = self._get_networkx_color(node_type)
            legend_elements.append(
                mpatches.Patch(color=color, label=node_type.value)
            )
        
        ax.legend(handles=legend_elements, loc='upper right')
        
        # 保存图片
        output_path = os.path.join(self.output_dir, filename)
        self.plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                        facecolor='white', edgecolor='none')
        self.plt.close()
        
        print(f"NetworkX 渲染完成: {output_path}")
        return output_path
    
    def _get_networkx_color(self, node_type: NodeType) -> str:
        """获取 NetworkX 节点颜色"""
        color_map = {
            NodeType.PROCESS: COLORS['main_process'],
            NodeType.DECISION: COLORS['decision'],
            NodeType.START_END: COLORS['start_end'],
            NodeType.DATA: COLORS['sub_process'],
            NodeType.CONNECTOR: COLORS['special'],
            NodeType.SPECIAL: COLORS['special']
        }
        return color_map.get(node_type, COLORS['main_process'])
    
    def _get_networkx_shape(self, node_type: NodeType) -> str:
        """获取 NetworkX 节点形状"""
        shape_map = {
            NodeType.PROCESS: 's',      # 方形
            NodeType.DECISION: 'D',     # 菱形
            NodeType.START_END: 'o',    # 圆形
            NodeType.DATA: 's',         # 方形
            NodeType.CONNECTOR: 'o',    # 圆形
            NodeType.SPECIAL: '^'       # 三角形
        }
        return shape_map.get(node_type, 's')
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        title = title.replace(' ', '_').replace('#', '').replace('.', '_')
        if len(title) > 50:
            title = title[:50]
        return title

# ================================
# 3. SVG 直接渲染器
# ================================

class SVGRenderer:
    """轻量级 SVG 直接渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print("✅ SVG 渲染器已就绪")
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染 SVG 流程图"""
        
        if filename is None:
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}.svg"
        
        # 计算布局
        positions = self._grid_layout(graph)
        
        # 生成 SVG 内容
        svg_content = self._generate_svg(graph, positions)
        
        # 保存文件
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG 渲染完成: {output_path}")
        return output_path
    
    def _grid_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """网格布局算法"""
        positions = {}
        nodes = list(graph.nodes)
        n_nodes = len(nodes)
        
        if n_nodes == 0:
            return positions
        
        # 计算网格尺寸
        cols = min(4, n_nodes)
        rows = (n_nodes + cols - 1) // cols
        
        cell_width = 200
        cell_height = 120
        margin = 50
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = margin + col * cell_width + cell_width // 2
            y = margin + row * cell_height + cell_height // 2
            positions[node.id] = (x, y)
        
        return positions
    
    def _generate_svg(self, graph: Graph, positions: Dict[str, Tuple[float, float]]) -> str:
        """生成 SVG 内容"""
        
        # 计算画布大小
        max_x = max(x for x, y in positions.values()) if positions else 200
        max_y = max(y for x, y in positions.values()) if positions else 200
        width = max_x + 100
        height = max_y + 100
        
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<style>',
            f'.node-text {{ font-family: "Microsoft YaHei", sans-serif; font-size: 12px; text-anchor: middle; dominant-baseline: middle; fill: white; font-weight: bold; }}',
            f'.edge-text {{ font-family: "Microsoft YaHei", sans-serif; font-size: 10px; text-anchor: middle; dominant-baseline: middle; fill: black; }}',
            f'</style>',
            f'<title>{graph.title}</title>'
        ]
        
        # 绘制边
        for edge in graph.edges:
            if edge.source in positions and edge.target in positions:
                x1, y1 = positions[edge.source]
                x2, y2 = positions[edge.target]
                
                color = COLORS['edge_highlight'] if edge.edge_type == "highlight" else COLORS['edge_normal']
                
                svg_parts.extend([
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="url(#arrowhead)"/>',
                ])
                
                # 边标签
                if edge.label:
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    svg_parts.append(
                        f'<text x="{mid_x}" y="{mid_y}" class="edge-text">{edge.label}</text>'
                    )
        
        # 绘制节点
        for node in graph.nodes:
            if node.id in positions:
                x, y = positions[node.id]
                color = self._get_svg_color(node.node_type)
                
                # 根据节点类型绘制形状
                if node.node_type == NodeType.DECISION:
                    # 菱形
                    svg_parts.append(
                        f'<polygon points="{x},{y-30} {x+40},{y} {x},{y+30} {x-40},{y}" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                elif node.node_type == NodeType.START_END:
                    # 椭圆
                    svg_parts.append(
                        f'<ellipse cx="{x}" cy="{y}" rx="50" ry="25" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                else:
                    # 矩形
                    svg_parts.append(
                        f'<rect x="{x-50}" y="{y-25}" width="100" height="50" rx="5" fill="{color}" stroke="black" stroke-width="2"/>'
                    )
                
                # 节点文本
                label = node.label.strip('"\'')
                if len(label) > 12:
                    # 分行显示
                    lines = [label[i:i+12] for i in range(0, len(label), 12)]
                    for i, line in enumerate(lines[:2]):  # 最多两行
                        text_y = y + (i - 0.5) * 12
                        svg_parts.append(
                            f'<text x="{x}" y="{text_y}" class="node-text">{line}</text>'
                        )
                else:
                    svg_parts.append(
                        f'<text x="{x}" y="{y}" class="node-text">{label}</text>'
                    )
        
        # 添加箭头标记
        svg_parts.extend([
            '<defs>',
            '<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
            f'<polygon points="0 0, 10 3.5, 0 7" fill="{COLORS["edge_normal"]}" />',
            '</marker>',
            '</defs>',
            '</svg>'
        ])
        
        return '\n'.join(svg_parts)
    
    def _get_svg_color(self, node_type: NodeType) -> str:
        """获取 SVG 节点颜色"""
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

# ================================
# 4. 统一的替代渲染器批量处理类
# ================================

class AlternativeRenderer:
    """统一的替代渲染器"""
    
    def __init__(self, method: str = "matplotlib", output_dir: str = "flowchart_output"):
        self.method = method.lower()
        self.output_dir = output_dir
        
        if self.method == "plotly":
            self.renderer = PlotlyRenderer(output_dir)
        elif self.method == "networkx":
            self.renderer = NetworkXRenderer(output_dir)
        elif self.method == "svg":
            self.renderer = SVGRenderer(output_dir)
        elif self.method == "matplotlib":
            from matplotlib_renderer import MatplotlibRenderer
            self.renderer = MatplotlibRenderer(output_dir)
        else:
            raise ValueError(f"不支持的渲染方法: {method}")
    
    def render_all_graphs(self, graphs: List[tuple]) -> List[str]:
        """批量渲染所有流程图"""
        
        rendered_files = []
        
        print(f"\n使用 {self.method.upper()} 渲染引擎批量渲染 {len(graphs)} 个流程图...")
        print("=" * 60)
        
        for i, (title, graph) in enumerate(graphs, 1):
            try:
                print(f"\n渲染流程图 {i}/{len(graphs)}: {title}")
                
                # 渲染单个图
                output_file = self.renderer.render_graph(graph)
                rendered_files.append(output_file)
                
                print(f"✓ 成功渲染: {os.path.basename(output_file)}")
                
            except Exception as e:
                print(f"✗ 渲染失败: {e}")
                continue
        
        print(f"\n批量渲染完成!")
        print(f"成功渲染: {len(rendered_files)}/{len(graphs)} 个流程图")
        print(f"输出目录: {self.output_dir}")
        
        return rendered_files 