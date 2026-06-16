# Matplotlib renderer

# 基于Matplotlib的流程图渲染引擎（备用方案）
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon
import numpy as np
from typing import Dict, Optional, List, Tuple
import os
from graph_data import Graph, Node, Edge, NodeType, GraphType
from config import COLORS, RENDER_CONFIG

class MatplotlibRenderer:
    """基于Matplotlib的流程图渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染单个流程图"""
        
        if filename is None:
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}.png"
        
        # 计算节点位置
        positions = self._calculate_layout(graph)
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_aspect('equal')
        
        # 绘制边
        for edge in graph.edges:
            self._draw_edge(ax, edge, positions)
        
        # 绘制节点
        for node in graph.nodes:
            self._draw_node(ax, node, positions)
        
        # 设置图形属性
        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 9)
        ax.axis('off')
        ax.set_title(graph.title, fontsize=16, fontweight='bold', pad=20)
        
        # 保存文件
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"渲染完成: {output_path}")
        return output_path
    
    def _calculate_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """计算节点布局位置"""
        positions = {}
        
        if graph.graph_type == GraphType.STATE_MACHINE:
            # 状态机使用圆形布局
            positions = self._circular_layout(graph)
        else:
            # 其他类型使用层次化布局
            positions = self._hierarchical_layout(graph)
        
        return positions
    
    def _hierarchical_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """层次化布局算法"""
        positions = {}
        
        # 简单的网格布局
        nodes = list(graph.nodes)
        n_nodes = len(nodes)
        
        # 计算网格尺寸
        cols = min(4, n_nodes)  # 最多4列
        rows = (n_nodes + cols - 1) // cols
        
        x_spacing = 2.5
        y_spacing = 1.5
        start_x = 1
        start_y = 7
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = start_x + col * x_spacing
            y = start_y - row * y_spacing
            positions[node.id] = (x, y)
        
        return positions
    
    def _circular_layout(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """圆形布局算法"""
        positions = {}
        nodes = list(graph.nodes)
        n_nodes = len(nodes)
        
        if n_nodes == 0:
            return positions
        
        # 圆心和半径
        center_x, center_y = 5, 4
        radius = 3
        
        for i, node in enumerate(nodes):
            angle = 2 * np.pi * i / n_nodes
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            positions[node.id] = (x, y)
        
        return positions
    
    def _draw_node(self, ax, node: Node, positions: Dict[str, Tuple[float, float]]):
        """绘制节点"""
        if node.id not in positions:
            return
        
        x, y = positions[node.id]
        
        # 根据节点类型选择样式
        color = self._get_node_color(node.node_type)
        shape = self._get_node_shape(node.node_type)
        
        # 绘制形状
        if shape == 'box':
            # 矩形
            width, height = 1.5, 0.8
            rect = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.05",
                facecolor=color, edgecolor='black', linewidth=1.5
            )
            ax.add_patch(rect)
        elif shape == 'diamond':
            # 菱形
            size = 0.8
            diamond = Polygon([
                (x, y + size), (x + size, y), 
                (x, y - size), (x - size, y)
            ], facecolor=color, edgecolor='black', linewidth=1.5)
            ax.add_patch(diamond)
        elif shape == 'ellipse':
            # 椭圆
            width, height = 1.2, 0.6
            ellipse = patches.Ellipse(
                (x, y), width, height,
                facecolor=color, edgecolor='black', linewidth=1.5
            )
            ax.add_patch(ellipse)
        else:  # circle
            # 圆形
            radius = 0.4
            circle = Circle((x, y), radius, 
                          facecolor=color, edgecolor='black', linewidth=1.5)
            ax.add_patch(circle)
        
        # 添加文本
        text = self._format_node_label(node.label)
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=9, fontweight='bold', color='white')
    
    def _draw_edge(self, ax, edge: Edge, positions: Dict[str, Tuple[float, float]]):
        """绘制边"""
        if edge.source not in positions or edge.target not in positions:
            return
        
        x1, y1 = positions[edge.source]
        x2, y2 = positions[edge.target]
        
        # 绘制箭头
        color = COLORS['edge_highlight'] if edge.edge_type == "highlight" else COLORS['edge_normal']
        
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        
        # 添加标签
        if edge.label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y, edge.label, ha='center', va='center',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.2", 
                   facecolor='white', alpha=0.8))
    
    def _get_node_color(self, node_type: NodeType) -> str:
        """获取节点颜色"""
        color_map = {
            NodeType.PROCESS: COLORS['main_process'],
            NodeType.DECISION: COLORS['decision'],
            NodeType.START_END: COLORS['start_end'],
            NodeType.DATA: COLORS['sub_process'],
            NodeType.CONNECTOR: COLORS['special'],
            NodeType.SPECIAL: COLORS['special']
        }
        return color_map.get(node_type, COLORS['main_process'])
    
    def _get_node_shape(self, node_type: NodeType) -> str:
        """获取节点形状"""
        shape_map = {
            NodeType.PROCESS: 'box',
            NodeType.DECISION: 'diamond',
            NodeType.START_END: 'ellipse',
            NodeType.DATA: 'box',
            NodeType.CONNECTOR: 'circle',
            NodeType.SPECIAL: 'box'
        }
        return shape_map.get(node_type, 'box')
    
    def _format_node_label(self, label: str) -> str:
        """格式化节点标签"""
        label = label.strip('"\'')
        
        # 自动换行
        max_length = 8
        if len(label) > max_length:
            # 按字符分割
            lines = [label[i:i+max_length] for i in range(0, len(label), max_length)]
            label = '\n'.join(lines)
        
        return label
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        title = title.replace(' ', '_').replace('#', '').replace('.', '_')
        
        if len(title) > 50:
            title = title[:50]
        
        return title

class MatplotlibBatchRenderer:
    """Matplotlib批量渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output"):
        self.renderer = MatplotlibRenderer(output_dir)
        self.output_dir = output_dir
    
    def render_all_graphs(self, graphs: List[tuple]) -> List[str]:
        """批量渲染所有流程图"""
        
        rendered_files = []
        
        print(f"\n使用Matplotlib渲染引擎批量渲染 {len(graphs)} 个流程图...")
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
