# 流程图数据模型定义
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    """节点类型枚举"""
    PROCESS = "process"           # 处理节点
    DECISION = "decision"         # 决策节点
    START_END = "start_end"       # 开始/结束节点
    DATA = "data"                 # 数据节点
    CONNECTOR = "connector"       # 连接点
    SPECIAL = "special"           # 特殊节点

class GraphType(Enum):
    """流程图类型枚举"""
    HIERARCHICAL = "hierarchical"     # 层次化流程图
    STATE_MACHINE = "state_machine"   # 状态机图
    COMPLEX_NETWORK = "complex_network"  # 复杂网络图
    CIRCULAR = "circular"             # 环形布局

@dataclass
class Node:
    """流程图节点数据结构"""
    id: str                      # 节点唯一标识
    label: str                   # 节点显示文本
    node_type: NodeType          # 节点类型
    x: Optional[float] = None    # X坐标（可选）
    y: Optional[float] = None    # Y坐标（可选）
    width: Optional[float] = None    # 节点宽度
    height: Optional[float] = None   # 节点高度
    style: Optional[Dict] = None     # 自定义样式
    
    def __post_init__(self):
        """初始化后处理，设置默认样式"""
        if self.style is None:
            self.style = {}

@dataclass
class Edge:
    """流程图边数据结构"""
    source: str                  # 源节点ID
    target: str                  # 目标节点ID
    label: Optional[str] = None  # 边标签
    edge_type: str = "normal"    # 边类型（normal, highlight）
    style: Optional[Dict] = None # 自定义样式
    
    def __post_init__(self):
        """初始化后处理，设置默认样式"""
        if self.style is None:
            self.style = {}

@dataclass 
class Graph:
    """完整的流程图数据结构"""
    title: str                   # 图标题
    graph_type: GraphType        # 图类型
    nodes: List[Node]            # 节点列表
    edges: List[Edge]            # 边列表
    layout_config: Optional[Dict] = None  # 布局配置
    
    def __post_init__(self):
        """初始化后处理，验证图的完整性"""
        if self.layout_config is None:
            self.layout_config = {}
        
        # 验证所有边的源节点和目标节点都存在
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"边的源节点 '{edge.source}' 不存在")
            if edge.target not in node_ids:
                raise ValueError(f"边的目标节点 '{edge.target}' 不存在")
    
    def add_node(self, node: Node) -> None:
        """添加节点"""
        # 检查节点ID是否已存在
        existing_ids = {n.id for n in self.nodes}
        if node.id in existing_ids:
            raise ValueError(f"节点ID '{node.id}' 已存在")
        self.nodes.append(node)
    
    def add_edge(self, edge: Edge) -> None:
        """添加边"""
        # 检查节点是否存在
        node_ids = {node.id for node in self.nodes}
        if edge.source not in node_ids:
            raise ValueError(f"源节点 '{edge.source}' 不存在")
        if edge.target not in node_ids:
            raise ValueError(f"目标节点 '{edge.target}' 不存在")
        self.edges.append(edge)
    
    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_edges_from_node(self, node_id: str) -> List[Edge]:
        """获取从指定节点出发的所有边"""
        return [edge for edge in self.edges if edge.source == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[Edge]:
        """获取指向指定节点的所有边"""
        return [edge for edge in self.edges if edge.target == node_id]

class GraphBuilder:
    """流程图构建器"""
    
    def __init__(self, title: str, graph_type: GraphType):
        self.graph = Graph(title=title, graph_type=graph_type, nodes=[], edges=[])
    
    def add_process_node(self, node_id: str, label: str) -> 'GraphBuilder':
        """添加处理节点"""
        node = Node(id=node_id, label=label, node_type=NodeType.PROCESS)
        self.graph.add_node(node)
        return self
    
    def add_decision_node(self, node_id: str, label: str) -> 'GraphBuilder':
        """添加决策节点"""
        node = Node(id=node_id, label=label, node_type=NodeType.DECISION)
        self.graph.add_node(node)
        return self
    
    def add_start_node(self, node_id: str, label: str) -> 'GraphBuilder':
        """添加开始节点"""
        node = Node(id=node_id, label=label, node_type=NodeType.START_END)
        self.graph.add_node(node)
        return self
    
    def add_end_node(self, node_id: str, label: str) -> 'GraphBuilder':
        """添加结束节点"""
        node = Node(id=node_id, label=label, node_type=NodeType.START_END)
        self.graph.add_node(node)
        return self
    
    def add_edge(self, source: str, target: str, label: Optional[str] = None, 
                 edge_type: str = "normal") -> 'GraphBuilder':
        """添加边"""
        edge = Edge(source=source, target=target, label=label, edge_type=edge_type)
        self.graph.add_edge(edge)
        return self
    
    def build(self) -> Graph:
        """构建并返回完整的图"""
        return self.graph 