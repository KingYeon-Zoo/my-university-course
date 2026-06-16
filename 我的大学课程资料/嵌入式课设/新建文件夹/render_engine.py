# 基于Graphviz的流程图渲染引擎
import graphviz
from typing import Dict, Optional, List
import os
from graph_data import Graph, Node, Edge, NodeType, GraphType
from config import COLORS, RENDER_CONFIG, LAYOUT_ENGINES, NODE_SHAPES, FONT_CONFIG
from graphviz_detector import GraphvizDetector

class FlowchartRenderer:
    """流程图渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output", graphviz_path: Optional[str] = None):
        self.output_dir = output_dir
        self.graphviz_path = graphviz_path
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 如果提供了自定义 Graphviz 路径，设置环境变量
        if self.graphviz_path and os.path.isdir(self.graphviz_path):
            os.environ['PATH'] = f"{self.graphviz_path}{os.pathsep}{os.environ.get('PATH', '')}"
    
    def render_graph(self, graph: Graph, filename: Optional[str] = None) -> str:
        """渲染单个流程图"""
        
        # 生成文件名
        if filename is None:
            # 清理标题作为文件名
            safe_title = self._sanitize_filename(graph.title)
            filename = f"{safe_title}"
        
        # 选择合适的布局引擎
        engine = self._select_layout_engine(graph)
        
        # 创建Graphviz图对象
        dot = graphviz.Digraph(
            name=filename,
            comment=graph.title,
            engine=engine,
            format=RENDER_CONFIG['format']
        )
        
        # 设置图的全局属性
        self._configure_graph_attributes(dot, graph)
        
        # 添加节点
        for node in graph.nodes:
            self._add_node_to_dot(dot, node)
        
        # 添加边
        for edge in graph.edges:
            self._add_edge_to_dot(dot, edge)
        
        # 渲染到文件
        output_path = os.path.join(self.output_dir, filename)
        dot.render(output_path, cleanup=True)
        
        print(f"渲染完成: {output_path}.{RENDER_CONFIG['format']}")
        return f"{output_path}.{RENDER_CONFIG['format']}"
    
    def _select_layout_engine(self, graph: Graph) -> str:
        """根据图类型选择最佳布局引擎"""
        if graph.graph_type == GraphType.STATE_MACHINE:
            return LAYOUT_ENGINES['state_machine']
        elif graph.graph_type == GraphType.CIRCULAR:
            return LAYOUT_ENGINES['circular']
        elif len(graph.nodes) > 20:  # 复杂图使用网络布局
            return LAYOUT_ENGINES['complex_network']
        else:
            return LAYOUT_ENGINES['hierarchical']
    
    def _configure_graph_attributes(self, dot: graphviz.Digraph, graph: Graph):
        """配置图的全局属性"""
        
        # 图级别属性
        dot.attr(
            rankdir=RENDER_CONFIG['rankdir'],
            bgcolor=COLORS['background'],
            margin=RENDER_CONFIG['margin'],
            dpi=str(RENDER_CONFIG['dpi']),
            fontname=FONT_CONFIG['font_name'],
            fontsize=FONT_CONFIG['font_size_title']
        )
        
        # 节点默认属性
        dot.attr('node',
            fontname=FONT_CONFIG['font_name'],
            fontsize=RENDER_CONFIG['node_font_size'],
            style='filled',
            height=RENDER_CONFIG['node_height'],
            width=RENDER_CONFIG['node_width']
        )
        
        # 边默认属性
        dot.attr('edge',
            fontname=FONT_CONFIG['font_name'],
            fontsize=RENDER_CONFIG['edge_font_size'],
            color=COLORS['edge_normal']
        )
        
        # 根据图类型调整特定参数
        if graph.graph_type == GraphType.STATE_MACHINE:
            dot.attr(overlap='false', splines='true')
        elif graph.graph_type == GraphType.HIERARCHICAL:
            dot.attr(nodesep='0.8', ranksep='1.0')
    
    def _add_node_to_dot(self, dot: graphviz.Digraph, node: Node):
        """添加节点到Graphviz图"""
        
        # 根据节点类型选择样式
        node_attrs = self._get_node_style(node)
        
        # 处理换行的标签
        formatted_label = self._format_node_label(node.label)
        
        dot.node(node.id, formatted_label, **node_attrs)
    
    def _add_edge_to_dot(self, dot: graphviz.Digraph, edge: Edge):
        """添加边到Graphviz图"""
        
        edge_attrs = {}
        
        # 设置边的样式
        if edge.edge_type == "highlight":
            edge_attrs['color'] = COLORS['edge_highlight']
            edge_attrs['penwidth'] = '2'
        else:
            edge_attrs['color'] = COLORS['edge_normal']
        
        # 添加标签（如果有）
        if edge.label:
            edge_attrs['label'] = edge.label
            edge_attrs['fontcolor'] = COLORS['text_black']
        
        dot.edge(edge.source, edge.target, **edge_attrs)
    
    def _get_node_style(self, node: Node) -> Dict[str, str]:
        """根据节点类型返回样式"""
        
        style = {
            'fontcolor': COLORS['text_white'],
            'style': 'filled',
        }
        
        if node.node_type == NodeType.PROCESS:
            style.update({
                'shape': NODE_SHAPES['process'],
                'fillcolor': COLORS['main_process'],
            })
        elif node.node_type == NodeType.DECISION:
            style.update({
                'shape': NODE_SHAPES['decision'],
                'fillcolor': COLORS['decision'],
            })
        elif node.node_type == NodeType.START_END:
            style.update({
                'shape': NODE_SHAPES['start_end'],
                'fillcolor': COLORS['start_end'],
            })
        elif node.node_type == NodeType.DATA:
            style.update({
                'shape': NODE_SHAPES['data'],
                'fillcolor': COLORS['sub_process'],
            })
        elif node.node_type == NodeType.CONNECTOR:
            style.update({
                'shape': NODE_SHAPES['connector'],
                'fillcolor': COLORS['special'],
                'width': '0.5',
                'height': '0.5'
            })
        else:  # SPECIAL
            style.update({
                'shape': NODE_SHAPES['process'],
                'fillcolor': COLORS['special'],
            })
        
        return style
    
    def _format_node_label(self, label: str) -> str:
        """格式化节点标签，处理长文本和换行"""
        
        # 移除多余的引号
        label = label.strip('"\'')
        
        # 如果标签过长，自动换行
        max_length = 20
        if len(label) > max_length:
            # 尝试在合适的位置换行
            words = label.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + word) <= max_length:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line.strip())
            
            # 如果分词效果不好，按字符强制换行
            if len(lines) <= 1 and len(label) > max_length:
                lines = [label[i:i+max_length] for i in range(0, len(label), max_length)]
            
            label = "\\n".join(lines)
        
        return label
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名，移除非法字符"""
        
        # 移除或替换非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        # 移除多余的空格和特殊字符
        title = title.replace(' ', '_').replace('#', '').replace('.', '_')
        
        # 限制长度
        if len(title) > 50:
            title = title[:50]
        
        return title

class BatchRenderer:
    """批量渲染器"""
    
    def __init__(self, output_dir: str = "flowchart_output", graphviz_path: Optional[str] = None):
        self.renderer = FlowchartRenderer(output_dir, graphviz_path)
        self.output_dir = output_dir
    
    def render_all_graphs(self, graphs: List[tuple]) -> List[str]:
        """批量渲染所有流程图"""
        
        rendered_files = []
        
        print(f"\n开始批量渲染 {len(graphs)} 个流程图...")
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

def test_renderer():
    """测试渲染器功能"""
    from graph_data import GraphBuilder, NodeType, GraphType
    
    # 创建测试图
    builder = GraphBuilder("测试流程图", GraphType.HIERARCHICAL)
    builder.add_start_node("start", "开始") \
           .add_process_node("process1", "处理步骤1") \
           .add_decision_node("decision", "是否继续？") \
           .add_process_node("process2", "处理步骤2") \
           .add_end_node("end", "结束") \
           .add_edge("start", "process1") \
           .add_edge("process1", "decision") \
           .add_edge("decision", "process2", "是") \
           .add_edge("decision", "end", "否") \
           .add_edge("process2", "end")
    
    test_graph = builder.build()
    
    # 渲染测试图
    renderer = FlowchartRenderer()
    output_file = renderer.render_graph(test_graph, "test_flowchart")
    print(f"测试渲染完成: {output_file}")

if __name__ == "__main__":
    test_renderer() 