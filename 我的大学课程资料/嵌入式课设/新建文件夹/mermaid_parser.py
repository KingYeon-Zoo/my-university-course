# Mermaid流程图解析器
import re
from typing import List, Dict, Tuple, Optional
from graph_data import Graph, Node, Edge, GraphBuilder, NodeType, GraphType

class MermaidParser:
    """Mermaid语法解析器"""
    
    def __init__(self):
        # 节点定义的正则表达式模式
        self.node_patterns = {
            'simple': re.compile(r'^([A-Za-z0-9_]+)\["(.+?)"\]'),
            'rounded': re.compile(r'^([A-Za-z0-9_]+)\("(.+?)"\)'),
            'diamond': re.compile(r'^([A-Za-z0-9_]+)\{"(.+?)"\}'),
            'circle': re.compile(r'^([A-Za-z0-9_]+)\(\("(.+?)"\)\)'),
            'simple_text': re.compile(r'^([A-Za-z0-9_]+)\[(.+?)\]'),
            'state_node': re.compile(r'^\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*:\s*(.+)'),  # 状态机节点
        }
        
        # 边连接的正则表达式模式
        self.edge_patterns = {
            'arrow': re.compile(r'^([A-Za-z0-9_\u4e00-\u9fff]+)\s*-->\s*([A-Za-z0-9_\u4e00-\u9fff]+)'),
            'arrow_with_label': re.compile(r'^([A-Za-z0-9_\u4e00-\u9fff]+)\s*-->\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*:\s*(.+)'),
            'line': re.compile(r'^([A-Za-z0-9_\u4e00-\u9fff]+)\s*---\s*([A-Za-z0-9_\u4e00-\u9fff]+)'),
            'line_with_label': re.compile(r'^([A-Za-z0-9_\u4e00-\u9fff]+)\s*--\|(.+?)\|\s*([A-Za-z0-9_\u4e00-\u9fff]+)'),
            'state_transition': re.compile(r'^\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*-->\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*:\s*(.+)'),
        }
    
    def parse_mermaid_text(self, mermaid_text: str, title: str = "流程图") -> Graph:
        """解析Mermaid文本并返回Graph对象"""
        lines = [line.strip() for line in mermaid_text.split('\n') if line.strip()]
        
        # 检测图类型
        graph_type = self._detect_graph_type(lines)
        
        # 创建图构建器
        builder = GraphBuilder(title, graph_type)
        
        # 存储已处理的节点，避免重复
        processed_nodes = set()
        
        for line in lines:
            # 跳过流程图类型声明行
            if line.startswith('flowchart') or line.startswith('stateDiagram') or line.startswith('graph'):
                continue
            
            # 解析节点定义
            node_id, node_label, node_type = self._parse_node_definition(line)
            if node_id and node_id not in processed_nodes:
                self._add_node_to_builder(builder, node_id, node_label, node_type)
                processed_nodes.add(node_id)
            
            # 解析边连接
            edge_info = self._parse_edge_definition(line)
            if edge_info:
                source, target, edge_label = edge_info
                
                # 确保源节点和目标节点存在
                if source not in processed_nodes:
                    self._add_node_to_builder(builder, source, source, NodeType.PROCESS)
                    processed_nodes.add(source)
                if target not in processed_nodes:
                    self._add_node_to_builder(builder, target, target, NodeType.PROCESS)
                    processed_nodes.add(target)
                
                builder.add_edge(source, target, edge_label)
        
        return builder.build()
    
    def _detect_graph_type(self, lines: List[str]) -> GraphType:
        """检测流程图类型"""
        first_line = lines[0].lower() if lines else ""
        
        if 'statediagram' in first_line:
            return GraphType.STATE_MACHINE
        elif 'flowchart td' in first_line or 'graph td' in first_line:
            return GraphType.HIERARCHICAL
        elif 'flowchart lr' in first_line or 'graph lr' in first_line:
            return GraphType.HIERARCHICAL
        else:
            return GraphType.HIERARCHICAL
    
    def _parse_node_definition(self, line: str) -> Tuple[Optional[str], Optional[str], Optional[NodeType]]:
        """解析节点定义"""
        # 尝试匹配各种节点模式
        for pattern_name, pattern in self.node_patterns.items():
            match = pattern.search(line)
            if match:
                node_id = match.group(1)
                node_label = match.group(2)
                
                # 根据语法确定节点类型
                if pattern_name == 'diamond':
                    node_type = NodeType.DECISION
                elif pattern_name == 'rounded':
                    node_type = NodeType.START_END
                elif pattern_name == 'circle':
                    node_type = NodeType.CONNECTOR
                else:
                    node_type = NodeType.PROCESS
                
                return node_id, node_label, node_type
        
        return None, None, None
    
    def _parse_edge_definition(self, line: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """解析边定义"""
        # 尝试匹配各种边模式
        for pattern_name, pattern in self.edge_patterns.items():
            match = pattern.search(line)
            if match:
                if 'with_label' in pattern_name:
                    source = match.group(1)
                    edge_label = match.group(2)
                    target = match.group(3)
                    return source, target, edge_label
                else:
                    source = match.group(1)
                    target = match.group(2)
                    return source, target, None
        
        return None
    
    def _add_node_to_builder(self, builder: GraphBuilder, node_id: str, 
                           node_label: str, node_type: NodeType) -> None:
        """向构建器添加节点"""
        if node_type == NodeType.DECISION:
            builder.add_decision_node(node_id, node_label)
        elif node_type == NodeType.START_END:
            # 根据标签内容判断是开始还是结束节点
            if any(keyword in node_label.lower() for keyword in ['开始', '启动', 'start', 'begin']):
                builder.add_start_node(node_id, node_label)
            else:
                builder.add_end_node(node_id, node_label)
        else:
            builder.add_process_node(node_id, node_label)

def extract_mermaid_from_markdown(markdown_text: str) -> List[Tuple[str, str]]:
    """从Markdown文件中提取所有Mermaid代码块"""
    mermaid_blocks = []
    
    # 正则表达式匹配Mermaid代码块
    pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    matches = pattern.findall(markdown_text)
    
    for i, match in enumerate(matches):
        title = f"流程图_{i+1}"
        # 尝试从上下文中提取标题
        title = _extract_title_from_context(markdown_text, match) or title
        mermaid_blocks.append((title, match.strip()))
    
    return mermaid_blocks

def _extract_title_from_context(markdown_text: str, mermaid_code: str) -> Optional[str]:
    """尝试从上下文中提取流程图标题"""
    # 查找Mermaid代码块的位置
    code_position = markdown_text.find(f'```mermaid\n{mermaid_code}')
    if code_position == -1:
        return None
    
    # 在代码块前查找最近的标题
    before_text = markdown_text[:code_position]
    lines = before_text.split('\n')
    
    # 从后向前查找标题
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('###') or line.startswith('**') and line.endswith('**'):
            # 清理标题文本
            title = line.replace('###', '').replace('**', '').strip()
            if '流程' in title or '图' in title:
                return title
    
    return None

# 测试函数
def test_parser():
    """测试解析器功能"""
    sample_mermaid = """
    flowchart TD
        A["系统启动"] --> B["硬件初始化"]
        B --> C["时钟配置"]
        C --> D{"检测到按键？"}
        D -->|是| E["按键处理"]
        D -->|否| F["继续扫描"]
        E --> G["返回主循环"]
        F --> D
        G --> D
    """
    
    parser = MermaidParser()
    graph = parser.parse_mermaid_text(sample_mermaid, "测试流程图")
    
    print(f"解析结果：")
    print(f"标题：{graph.title}")
    print(f"类型：{graph.graph_type}")
    print(f"节点数量：{len(graph.nodes)}")
    print(f"边数量：{len(graph.edges)}")

if __name__ == "__main__":
    test_parser() 