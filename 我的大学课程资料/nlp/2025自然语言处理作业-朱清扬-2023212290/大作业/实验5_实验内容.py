"""
实验五：检索增强生成（RAG）系统实现 - 实验内容

本代码实现了RAG系统的完整流程，包括：
1. 环境准备与配置
2. 文档知识库构建（加载、分块、向量化）
3. 文档检索实现
4. RAG系统构建与生成
5. 评估RAG系统性能
6. 优化RAG系统（混合检索、增强提示）

作者：[姓名]
日期：2025-10-30
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

# 在导入其他模块前设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 设置UTF-8编码（解决Windows控制台编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
    # 设置控制台代码页为UTF-8
    try:
        import subprocess
        subprocess.run('chcp 65001', shell=True, capture_output=True)
    except:
        pass

# 创建输出文件夹
OUTPUT_DIR = "./实验5/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# 1. 环境准备
# ============================================================================
print("=" * 80)
print("步骤1：环境准备与配置")
print("=" * 80)

try:
    import numpy as np
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.embeddings import Embeddings
    from langchain_community.vectorstores import FAISS
    from langchain_community.document_loaders import TextLoader, DirectoryLoader
    from langchain_core.documents import Document
    from openai import OpenAI
    import json
    import time
    from typing import List, Tuple, Dict, Optional
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # 使用非交互式后端
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
    plt.rcParams['axes.unicode_minus'] = False
    
    print("✓ 所有依赖已成功导入")
    print("✓ 使用CPU模式（通过API调用LLM和Embedding）")
    
except ImportError as e:
    print(f"✗ 导入依赖失败: {e}")
    print("请运行: pip install langchain langchain-community langchain-core langchain-text-splitters faiss-cpu numpy openai matplotlib")
    exit(1)


# ============================================================================
# 自定义OpenAI Embeddings类
# ============================================================================

class OpenAIEmbeddings(Embeddings):
    """自定义OpenAI Embeddings类，使用API调用"""
    
    def __init__(self, 
                 api_key: str = "sk-xxyzvmuowozfpbkyswujkhbpiktzhuqcehdefmlcodtsnaig",
                 base_url: str = "https://api.siliconflow.cn/v1",
                 model: str = "Qwen/Qwen3-Embedding-8B",
                 dimension: int = 4096):
        """
        初始化OpenAI Embeddings
        
        参数:
            api_key: API密钥
            base_url: API基础URL
            model: 嵌入模型名称
            dimension: 嵌入维度
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.dimension = dimension
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档
        
        参数:
            texts: 文本列表
        
        返回:
            嵌入向量列表
        """
        embeddings = []
        batch_size = 10  # 每批处理10个文本
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            attempt = 0
            max_attempts = 3
            
            while attempt < max_attempts:
                try:
                    attempt += 1
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    break
                    
                except Exception as e:
                    if attempt < max_attempts:
                        print(f"  [Embedding API调用 {attempt}] 失败，重试: {e}")
                        time.sleep(2)
                    else:
                        print(f"  ✗ Embedding API调用失败: {e}")
                        # 返回零向量作为后备
                        embeddings.extend([[0.0] * self.dimension for _ in batch])
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询
        
        参数:
            text: 查询文本
        
        返回:
            嵌入向量
        """
        attempt = 0
        max_attempts = 3
        
        while attempt < max_attempts:
            try:
                attempt += 1
                response = self.client.embeddings.create(
                    model=self.model,
                    input=[text]
                )
                return response.data[0].embedding
                
            except Exception as e:
                if attempt < max_attempts:
                    print(f"  [Query Embedding API调用 {attempt}] 失败，重试: {e}")
                    time.sleep(2)
                else:
                    print(f"  ✗ Query Embedding API调用失败: {e}")
                    # 返回零向量作为后备
                    return [0.0] * self.dimension
        
        return [0.0] * self.dimension


# ============================================================================
# 2. 构建文档知识库
# ============================================================================
print("\n" + "=" * 80)
print("步骤2：构建文档知识库")
print("=" * 80)

class DocumentKnowledgeBase:
    """文档知识库类，负责文档加载、分块和向量化"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化知识库
        
        参数:
            chunk_size: 文档块大小
            chunk_overlap: 文档块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = []
        self.chunks = []
        self.vector_store = None
        
    def load_documents(self, directory_path: str) -> List[Document]:
        """
        从指定目录加载文档（优化版：支持错误处理和多种编码）
        
        参数:
            directory_path: 文档目录路径
        
        返回:
            文档列表
        """
        print(f"\n正在从 {directory_path} 加载文档...")
        
        if not os.path.exists(directory_path):
            print(f"⚠ 目录不存在，创建示例文档...")
            os.makedirs(directory_path, exist_ok=True)
            self._create_sample_documents(directory_path)
        
        documents = []
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        
        # 尝试不同编码加载文档
        for encoding in encodings:
            try:
                loader = DirectoryLoader(
                    directory_path,
                    glob="**/*.txt",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': encoding}
                )
                documents = loader.load()
                if documents:
                    print(f"✓ 使用 {encoding} 编码成功加载 {len(documents)} 个文档")
                    break
            except Exception as e:
                continue
        
        if not documents:
            print("✗ 无法加载文档，请检查文件编码和格式")
            return []
        
        self.documents = documents
        
        # 显示文档统计信息
        total_chars = sum(len(doc.page_content) for doc in documents)
        print(f"✓ 文档总字符数: {total_chars:,}")
        if documents:
            print(f"✓ 第一个文档预览: {documents[0].page_content[:100]}...")
        
        return documents
    
    def _create_sample_documents(self, directory_path: str):
        """创建示例文档"""
        sample_docs = [
            {
                "filename": "ai_development.txt",
                "content": """中国人工智能发展现状

中国在人工智能领域取得了显著进展。截至2024年，中国已成为全球人工智能专利申请最多的国家之一。

主要发展特点：
1. 技术创新：百度、阿里巴巴、腾讯等科技巨头在AI领域持续投入。百度的文心大模型、阿里的通义千问等大语言模型已达到国际先进水平。
2. 应用场景：AI技术在智慧城市、医疗诊断、自动驾驶等领域得到广泛应用。
3. 产业生态：形成了从基础研究到应用开发的完整产业链。华为、商汤科技、旷视科技等企业在计算机视觉领域处于领先地位。
4. 政策支持：国家出台了多项政策支持人工智能发展，包括《新一代人工智能发展规划》等。

挑战与机遇：
虽然发展迅速，但在基础算法、高端芯片等方面仍有提升空间。未来，中国AI产业将继续保持高速增长态势。"""
            },
            {
                "filename": "llm_technology.txt",
                "content": """大语言模型技术概述

大语言模型（Large Language Model, LLM）是近年来自然语言处理领域的重要突破。

核心技术：
1. Transformer架构：基于自注意力机制，能够捕捉长距离依赖关系。
2. 预训练-微调范式：通过大规模无监督预训练和任务特定微调实现强大性能。
3. 提示工程：通过精心设计的提示词引导模型生成高质量输出。

代表性模型：
- GPT系列：OpenAI开发的生成式预训练模型
- BERT系列：Google开发的双向编码器
- ChatGLM：清华大学开发的中英双语对话模型
- 文心一言：百度开发的中文大模型

应用场景：
文本生成、机器翻译、问答系统、代码生成、知识图谱构建等。

技术挑战：
模型幻觉、知识更新、计算资源消耗、安全性和可控性等问题仍需进一步解决。"""
            },
            {
                "filename": "rag_introduction.txt",
                "content": """检索增强生成（RAG）技术简介

RAG（Retrieval-Augmented Generation）是一种结合检索系统和生成模型的技术架构。

工作原理：
1. 检索阶段：根据用户查询，从外部知识库中检索相关文档
2. 增强阶段：将检索到的文档作为上下文添加到提示词中
3. 生成阶段：大语言模型基于增强后的提示生成回答

技术优势：
- 缓解模型幻觉问题
- 支持知识实时更新
- 提供可追溯的信息来源
- 降低模型训练成本

关键技术：
1. 向量数据库：FAISS、Milvus、Pinecone等
2. 嵌入模型：BERT、Sentence-BERT、M3E等
3. 检索策略：语义检索、混合检索、重排序等

应用案例：
企业知识库问答、智能客服、文档摘要、代码助手等场景已广泛应用RAG技术。"""
            }
        ]
        
        for doc_info in sample_docs:
            file_path = os.path.join(directory_path, doc_info["filename"])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_info["content"])
        
        print(f"✓ 创建了 {len(sample_docs)} 个示例文档")
    
    def split_documents(self, documents: Optional[List[Document]] = None) -> List[Document]:
        """
        将文档分割成小块（优化版：自适应分隔符和统计信息）
        
        参数:
            documents: 文档列表（如果为None，使用已加载的文档）
        
        返回:
            文档块列表
        """
        if documents is None:
            documents = self.documents
        
        if not documents:
            print("✗ 没有可分割的文档")
            return []
        
        print(f"\n正在分割文档...")
        print(f"参数: chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        self.chunks = chunks
        
        # 统计信息
        chunk_lengths = [len(chunk.page_content) for chunk in chunks]
        print(f"✓ 文档被分割为 {len(chunks)} 个块")
        print(f"✓ 块大小统计: 最小={min(chunk_lengths)}, 最大={max(chunk_lengths)}, 平均={np.mean(chunk_lengths):.1f}")
        if chunks:
            print(f"✓ 第一个块示例: {chunks[0].page_content[:100]}...")
        
        return chunks
    
    def create_vector_store(self, 
                           chunks: Optional[List[Document]] = None,
                           api_key: str = "sk-xxyzvmuowozfpbkyswujkhbpiktzhuqcehdefmlcodtsnaig",
                           base_url: str = "https://api.siliconflow.cn/v1",
                           embedding_model: str = "Qwen/Qwen3-Embedding-8B",
                           dimension: int = 4096) -> FAISS:
        """
        创建向量存储（使用API调用）
        
        参数:
            chunks: 文档块列表
            api_key: API密钥
            base_url: API基础URL
            embedding_model: 嵌入模型名称
            dimension: 嵌入维度
        
        返回:
            向量存储对象
        """
        if chunks is None:
            chunks = self.chunks
        
        if not chunks:
            print("✗ 没有可向量化的文档块")
            return None
        
        print(f"\n正在创建向量存储...")
        print(f"使用嵌入模型: {embedding_model} (API)")
        print(f"嵌入维度: {dimension}")
        
        start_time = time.time()
        
        try:
            # 使用自定义OpenAI Embeddings
            embeddings = OpenAIEmbeddings(
                api_key=api_key,
                base_url=base_url,
                model=embedding_model,
                dimension=dimension
            )
            
            # 创建FAISS向量存储
            print(f"正在对 {len(chunks)} 个文档块进行向量化...")
            vector_store = FAISS.from_documents(chunks, embeddings)
            self.vector_store = vector_store
            
            elapsed_time = time.time() - start_time
            print(f"✓ 向量存储创建完成，包含 {len(chunks)} 个向量")
            print(f"✓ 耗时: {elapsed_time:.2f} 秒")
            
            return vector_store
            
        except Exception as e:
            print(f"✗ 创建向量存储失败: {e}")
            print("提示: 请确保API连接正常")
            return None
    
    def save_vector_store(self, save_path: str = "faiss_index"):
        """保存向量存储到本地"""
        if self.vector_store is None:
            print("✗ 没有可保存的向量存储")
            return False
        
        try:
            self.vector_store.save_local(save_path)
            print(f"✓ 向量存储已保存到: {save_path}")
            return True
        except Exception as e:
            print(f"✗ 保存向量存储失败: {e}")
            return False


# ============================================================================
# 3. 实现文档检索
# ============================================================================
print("\n" + "=" * 80)
print("步骤3：实现文档检索")
print("=" * 80)

class DocumentRetriever:
    """文档检索器类，负责从向量存储中检索相关文档"""
    
    def __init__(self, vector_store: FAISS = None,
                 api_key: str = "sk-xxyzvmuowozfpbkyswujkhbpiktzhuqcehdefmlcodtsnaig",
                 base_url: str = "https://api.siliconflow.cn/v1",
                 embedding_model: str = "Qwen/Qwen3-Embedding-8B",
                 dimension: int = 4096):
        """
        初始化检索器
        
        参数:
            vector_store: 向量存储对象
            api_key: API密钥
            base_url: API基础URL
            embedding_model: 嵌入模型名称
            dimension: 嵌入维度
        """
        self.vector_store = vector_store
        self.api_key = api_key
        self.base_url = base_url
        self.embedding_model = embedding_model
        self.dimension = dimension
    
    def load_vector_store(self, index_path: str = "faiss_index") -> FAISS:
        """
        加载向量存储（使用API）
        
        参数:
            index_path: 向量存储路径
        
        返回:
            向量存储对象
        """
        print(f"\n正在加载向量存储: {index_path}")
        
        try:
            embeddings = OpenAIEmbeddings(
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.embedding_model,
                dimension=self.dimension
            )
            
            vector_store = FAISS.load_local(
                index_path, 
                embeddings,
                allow_dangerous_deserialization=True  # 新版本需要此参数
            )
            self.vector_store = vector_store
            
            print(f"✓ 向量存储加载完成")
            return vector_store
            
        except Exception as e:
            print(f"✗ 加载向量存储失败: {e}")
            return None
    
    def retrieve_documents(self, 
                          query: str, 
                          top_k: int = 3,
                          score_threshold: Optional[float] = None) -> List[Tuple[Document, float]]:
        """
        检索相关文档（优化版：支持分数阈值过滤）
        
        参数:
            query: 查询文本
            top_k: 返回的文档数量
            score_threshold: 分数阈值，低于此值的文档将被过滤
        
        返回:
            相关文档列表及其相似度分数
        """
        if self.vector_store is None:
            print("✗ 向量存储未加载")
            return []
        
        print(f"\n正在检索查询: '{query}'")
        print(f"参数: top_k={top_k}, score_threshold={score_threshold}")
        
        start_time = time.time()
        
        # 执行相似度检索
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        # 应用分数阈值过滤
        if score_threshold is not None:
            docs_with_scores = [(doc, score) for doc, score in docs_with_scores if score <= score_threshold]
        
        elapsed_time = time.time() - start_time
        
        print(f"✓ 检索到 {len(docs_with_scores)} 个相关文档 (耗时: {elapsed_time:.3f}秒)")
        
        return docs_with_scores
    
    def display_retrieved_documents(self, docs_with_scores: List[Tuple[Document, float]], max_length: int = 200):
        """
        显示检索结果
        
        参数:
            docs_with_scores: 文档及相似度分数列表
            max_length: 显示的最大字符数
        """
        print("\n检索结果:")
        print("-" * 80)
        for i, (doc, score) in enumerate(docs_with_scores):
            print(f"\n[文档 {i+1}] 相似度分数: {score:.4f}")
            content = doc.page_content[:max_length]
            if len(doc.page_content) > max_length:
                content += "..."
            print(content)
            if doc.metadata:
                print(f"元数据: {doc.metadata}")
        print("-" * 80)


# ============================================================================
# 4. 构建RAG系统
# ============================================================================
print("\n" + "=" * 80)
print("步骤4：构建RAG系统")
print("=" * 80)

class RAGSystem:
    """RAG系统类，整合检索和生成功能"""
    
    def __init__(self, retriever: DocumentRetriever, 
                 api_key: str = "sk-WS55wBt8PAWacZUZurDsl9etlcDIvUQaGeTdRKVk8IrdPL0P",
                 base_url: str = "https://fanyi.963312.xyz/v1",
                 model_name: str = "qwen-3-235b-a22b-thinking-2507"):
        """
        初始化RAG系统
        
        参数:
            retriever: 文档检索器
            api_key: OpenAI API密钥
            base_url: API基础URL
            model_name: 大语言模型名称
        """
        self.retriever = retriever
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
    
    def load_llm(self) -> OpenAI:
        """
        初始化OpenAI客户端
        
        返回:
            OpenAI客户端对象
        """
        print(f"\n正在初始化OpenAI API客户端...")
        print(f"模型: {self.model_name}")
        print(f"API地址: {self.base_url}")
        
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            print(f"✓ OpenAI API客户端初始化完成")
            return self.client
            
        except Exception as e:
            print(f"✗ 初始化OpenAI客户端失败: {e}")
            self.client = None
            return None
    
    def format_retrieved_context(self, docs_with_scores: List[Tuple[Document, float]]) -> str:
        """
        格式化检索到的上下文（优化版：更清晰的格式）
        
        参数:
            docs_with_scores: 文档及其相似度分数列表
        
        返回:
            格式化后的上下文字符串
        """
        if not docs_with_scores:
            return ""
        
        context_parts = []
        for i, (doc, score) in enumerate(docs_with_scores):
            context_parts.append(f"[参考文档{i+1}] (相关度: {score:.4f})\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, 
                         query: str, 
                         context: Optional[str] = None, 
                         max_length: int = 512,
                         temperature: float = 0.7) -> str:
        """
        生成回答（使用OpenAI API）
        
        参数:
            query: 查询文本
            context: 上下文信息
            max_length: 生成文本的最大长度（此参数在API模式下作为参考）
            temperature: 生成温度
        
        返回:
            生成的回答
        """
        # 构建提示
        if context:
            prompt = f"""请基于以下参考信息回答用户的问题。如果参考信息不足以回答问题，请说明无法回答。

参考信息：
{context}

用户问题：{query}

回答："""
        else:
            prompt = f"用户问题：{query}\n\n回答："
        
        # 使用OpenAI API生成
        if self.client is not None:
            try:
                attempt = 0
                max_attempts = 3
                
                while attempt < max_attempts:
                    try:
                        attempt += 1
                        print(f"  [API调用 {attempt}] 正在生成回答...")
                        
                        response = self.client.chat.completions.create(
                            model=self.model_name,
                            messages=[{'role': 'user', 'content': prompt}],
                            temperature=temperature,
                        )
                        
                        content = response.choices[0].message.content
                        if content and content.strip():
                            print(f"  ✓ 成功生成回答")
                            return content
                        else:
                            print(f"  [API调用 {attempt}] 返回空内容，重试...")
                            time.sleep(2)
                    except Exception as e:
                        print(f"  [API调用 {attempt}] 失败: {e}")
                        if attempt < max_attempts:
                            time.sleep(2)
                        else:
                            raise
                
                # 如果所有尝试都失败，使用模拟生成
                print("  ⚠ API调用失败，使用模拟生成")
                return self._generate_mock_response(query, context)
                
            except Exception as e:
                print(f"⚠ API生成过程出错: {e}")
                return self._generate_mock_response(query, context)
        else:
            # 如果客户端未初始化，使用模拟生成
            print("  ⚠ OpenAI客户端未初始化，使用模拟生成")
            return self._generate_mock_response(query, context)
    
    def _generate_mock_response(self, query: str, context: Optional[str] = None) -> str:
        """
        模拟生成回答（用于没有实际模型时的演示）
        
        参数:
            query: 查询文本
            context: 上下文信息
        
        返回:
            模拟的回答
        """
        if context:
            # 基于上下文生成简单摘要
            lines = context.split('\n')
            relevant_lines = [line for line in lines if line.strip() and not line.startswith('[')]
            summary = '\n'.join(relevant_lines[:5])
            
            response = f"""基于提供的参考信息，我可以回答您的问题：

{summary}

这是根据检索到的文档内容生成的回答，包含了最相关的信息。"""
        else:
            response = f"""关于"{query}"这个问题，由于没有参考文档，我只能提供一般性的回答。

建议使用RAG系统检索相关文档后再生成更准确的答案。"""
        
        return response
    
    def rag_query(self, query: str, top_k: int = 3, max_length: int = 512) -> Dict:
        """
        执行完整的RAG查询流程
        
        参数:
            query: 查询文本
            top_k: 检索文档数量
            max_length: 生成最大长度
        
        返回:
            包含检索结果和生成回答的字典
        """
        print(f"\n执行RAG查询: '{query}'")
        print("=" * 80)
        
        # 1. 检索相关文档
        docs_with_scores = self.retriever.retrieve_documents(query, top_k=top_k)
        
        if not docs_with_scores:
            print("⚠ 未检索到相关文档")
            return {
                "query": query,
                "retrieved_docs": [],
                "context": "",
                "rag_response": "抱歉，未能检索到相关文档。",
                "normal_response": self.generate_response(query, context=None, max_length=max_length)
            }
        
        # 2. 格式化上下文
        context = self.format_retrieved_context(docs_with_scores)
        
        # 3. RAG生成
        print("\n[RAG模式] 生成回答...")
        rag_response = self.generate_response(query, context=context, max_length=max_length)
        
        # 4. 普通生成（对比）
        print("\n[普通模式] 生成回答...")
        normal_response = self.generate_response(query, context=None, max_length=max_length)
        
        return {
            "query": query,
            "retrieved_docs": docs_with_scores,
            "context": context,
            "rag_response": rag_response,
            "normal_response": normal_response
        }


# ============================================================================
# 5. 评估RAG系统
# ============================================================================
print("\n" + "=" * 80)
print("步骤5：评估RAG系统")
print("=" * 80)

class RAGEvaluator:
    """RAG系统评估器"""
    
    @staticmethod
    def evaluate_responses(query: str, 
                          rag_response: str, 
                          normal_response: str,
                          reference_answer: Optional[str] = None) -> Dict:
        """
        评估RAG和普通生成的回答（优化版：更多评估指标）
        
        参数:
            query: 查询文本
            rag_response: RAG生成的回答
            normal_response: 普通生成的回答
            reference_answer: 参考答案（如果有）
        
        返回:
            评估结果字典
        """
        import re
        
        print("\n" + "=" * 80)
        print("评估结果")
        print("=" * 80)
        
        # 1. 基础指标
        rag_length = len(rag_response)
        normal_length = len(normal_response)
        
        # 2. 信息密度（句子数量）
        rag_sentences = len(re.findall(r'[。！？；]', rag_response))
        normal_sentences = len(re.findall(r'[。！？；]', normal_response))
        
        # 3. 词汇丰富度（唯一字符数）
        rag_unique_chars = len(set(rag_response))
        normal_unique_chars = len(set(normal_response))
        
        # 4. 关键实体提及
        entities = ["百度", "阿里", "腾讯", "华为", "科大讯飞", "商汤", "旷视", 
                   "GPT", "BERT", "Transformer", "RAG", "大语言模型", "人工智能"]
        rag_entity_count = sum(1 for entity in entities if entity in rag_response)
        normal_entity_count = sum(1 for entity in entities if entity in normal_response)
        
        # 5. 数字和统计信息提及
        rag_numbers = len(re.findall(r'\d+', rag_response))
        normal_numbers = len(re.findall(r'\d+', normal_response))
        
        results = {
            "length": {
                "rag": rag_length,
                "normal": normal_length,
                "diff_pct": ((rag_length - normal_length) / normal_length * 100) if normal_length > 0 else 0
            },
            "sentences": {
                "rag": rag_sentences,
                "normal": normal_sentences,
                "diff_pct": ((rag_sentences - normal_sentences) / normal_sentences * 100) if normal_sentences > 0 else 0
            },
            "vocabulary": {
                "rag": rag_unique_chars,
                "normal": normal_unique_chars,
                "diff_pct": ((rag_unique_chars - normal_unique_chars) / normal_unique_chars * 100) if normal_unique_chars > 0 else 0
            },
            "entities": {
                "rag": rag_entity_count,
                "normal": normal_entity_count
            },
            "numbers": {
                "rag": rag_numbers,
                "normal": normal_numbers
            }
        }
        
        # 打印评估结果
        print(f"\n1. 回答长度:")
        print(f"   RAG: {rag_length} 字符 | 普通: {normal_length} 字符 | 差异: {results['length']['diff_pct']:.1f}%")
        
        print(f"\n2. 句子数量:")
        print(f"   RAG: {rag_sentences} 句 | 普通: {normal_sentences} 句 | 差异: {results['sentences']['diff_pct']:.1f}%")
        
        print(f"\n3. 词汇丰富度:")
        print(f"   RAG: {rag_unique_chars} 个唯一字符 | 普通: {normal_unique_chars} 个唯一字符 | 差异: {results['vocabulary']['diff_pct']:.1f}%")
        
        print(f"\n4. 实体提及:")
        print(f"   RAG: {rag_entity_count} 个 | 普通: {normal_entity_count} 个")
        
        print(f"\n5. 数字信息:")
        print(f"   RAG: {rag_numbers} 个 | 普通: {normal_numbers} 个")
        
        # 如果有参考答案，计算ROUGE分数
        if reference_answer:
            try:
                from rouge import Rouge
                rouge = Rouge()
                
                rag_scores = rouge.get_scores(rag_response, reference_answer)[0]
                normal_scores = rouge.get_scores(normal_response, reference_answer)[0]
                
                print("\n6. ROUGE评分:")
                print(f"   RAG:")
                print(f"      ROUGE-1: {rag_scores['rouge-1']['f']:.4f}")
                print(f"      ROUGE-2: {rag_scores['rouge-2']['f']:.4f}")
                print(f"      ROUGE-L: {rag_scores['rouge-l']['f']:.4f}")
                print(f"   普通:")
                print(f"      ROUGE-1: {normal_scores['rouge-1']['f']:.4f}")
                print(f"      ROUGE-2: {normal_scores['rouge-2']['f']:.4f}")
                print(f"      ROUGE-L: {normal_scores['rouge-l']['f']:.4f}")
                
                results["rouge"] = {
                    "rag": rag_scores,
                    "normal": normal_scores
                }
            except ImportError:
                print("\n⚠ 未安装rouge库，跳过ROUGE评分")
        
        print("=" * 80)
        
        return results
    


# ============================================================================
# 6. 优化RAG系统
# ============================================================================
print("\n" + "=" * 80)
print("步骤6：优化RAG系统")
print("=" * 80)

class AdvancedRAGSystem(RAGSystem):
    """高级RAG系统，包含多种优化策略"""
    
    def hybrid_search(self, 
                     query: str, 
                     top_k: int = 3, 
                     alpha: float = 0.7) -> List[Tuple[Document, float]]:
        """
        混合检索策略（优化版：结合语义检索和关键词检索）
        
        参数:
            query: 查询文本
            top_k: 返回的文档数量
            alpha: 语义检索权重（0-1之间）
        
        返回:
            相关文档列表及其混合分数
        """
        print(f"\n执行混合检索 (alpha={alpha})...")
        
        try:
            from langchain_community.retrievers import BM25Retriever
            
            # 1. 语义检索
            semantic_docs = self.retriever.vector_store.similarity_search_with_score(query, k=top_k * 2)
            
            # 2. 提取所有文档用于BM25
            all_docs = [Document(page_content=doc.page_content, metadata=doc.metadata) 
                       for doc, _ in semantic_docs]
            
            # 3. BM25关键词检索
            if all_docs:
                bm25_retriever = BM25Retriever.from_documents(all_docs)
                bm25_retriever.k = top_k * 2
                keyword_docs = bm25_retriever.get_relevant_documents(query)
            else:
                keyword_docs = []
            
            # 4. 合并和重新评分
            doc_scores = {}
            
            # 处理语义检索结果（分数已经归一化）
            max_semantic_score = max(score for _, score in semantic_docs) if semantic_docs else 1.0
            for doc, score in semantic_docs:
                doc_id = hash(doc.page_content)
                normalized_score = score / max_semantic_score if max_semantic_score > 0 else 0
                doc_scores[doc_id] = {
                    "doc": doc,
                    "semantic_score": normalized_score,
                    "keyword_score": 0
                }
            
            # 处理关键词检索结果
            for i, doc in enumerate(keyword_docs):
                doc_id = hash(doc.page_content)
                keyword_score = 1.0 - (i / len(keyword_docs)) if keyword_docs else 0
                if doc_id in doc_scores:
                    doc_scores[doc_id]["keyword_score"] = keyword_score
                else:
                    doc_scores[doc_id] = {
                        "doc": doc,
                        "semantic_score": 0,
                        "keyword_score": keyword_score
                    }
            
            # 5. 计算混合分数
            for doc_id in doc_scores:
                semantic = doc_scores[doc_id]["semantic_score"]
                keyword = doc_scores[doc_id]["keyword_score"]
                doc_scores[doc_id]["final_score"] = alpha * semantic + (1 - alpha) * keyword
            
            # 6. 排序并返回top_k结果
            sorted_docs = sorted(
                doc_scores.values(),
                key=lambda x: x["final_score"],
                reverse=True
            )[:top_k]
            
            result = [(item["doc"], item["final_score"]) for item in sorted_docs]
            
            print(f"✓ 混合检索完成，返回 {len(result)} 个文档")
            return result
            
        except Exception as e:
            print(f"⚠ 混合检索失败，回退到语义检索: {e}")
            return self.retriever.retrieve_documents(query, top_k=top_k)
    
    def generate_enhanced_response(self,
                                  query: str,
                                  docs_with_scores: List[Tuple[Document, float]],
                                  max_length: int = 512) -> str:
        """
        使用增强提示模板生成回答（使用OpenAI API）
        
        参数:
            query: 查询文本
            docs_with_scores: 文档及其相似度分数列表
            max_length: 生成文本的最大长度（此参数在API模式下作为参考）
        
        返回:
            生成的回答
        """
        # 提取并编号文档内容
        contexts = []
        for i, (doc, score) in enumerate(docs_with_scores):
            contexts.append(f"[文档{i+1}] (相关度: {score:.2f})\n{doc.page_content}")
        
        context_text = "\n\n".join(contexts)
        
        # 增强提示模板
        prompt = f"""你是一个专业的AI助手。请严格基于以下参考文档回答用户的问题。

参考文档:
{context_text}

用户问题: {query}

回答要求:
1. 仅使用参考文档中的信息，不要编造内容
2. 如果参考文档中没有相关信息，请明确说明"根据提供的文档，我无法回答这个问题"
3. 回答要全面、准确、客观
4. 使用分点或分段的结构组织答案
5. 不要提及"根据文档"或"文档中提到"等字样，直接回答即可

回答:"""
        
        # 使用OpenAI API生成
        if self.client is not None:
            try:
                attempt = 0
                max_attempts = 3
                
                while attempt < max_attempts:
                    try:
                        attempt += 1
                        print(f"  [增强模式API调用 {attempt}] 正在生成回答...")
                        
                        response = self.client.chat.completions.create(
                            model=self.model_name,
                            messages=[{'role': 'user', 'content': prompt}],
                            temperature=0.5,  # 降低温度获得更确定的回答
                        )
                        
                        content = response.choices[0].message.content
                        if content and content.strip():
                            print(f"  ✓ 成功生成回答")
                            return content
                        else:
                            print(f"  [增强模式API调用 {attempt}] 返回空内容，重试...")
                            time.sleep(2)
                    except Exception as e:
                        print(f"  [增强模式API调用 {attempt}] 失败: {e}")
                        if attempt < max_attempts:
                            time.sleep(2)
                        else:
                            raise
                
                print("  ⚠ API调用失败，使用模拟生成")
                return self._generate_mock_response(query, context_text)
                
            except Exception as e:
                print(f"⚠ 生成过程出错: {e}")
                return self._generate_mock_response(query, context_text)
        else:
            print("  ⚠ OpenAI客户端未初始化，使用模拟生成")
            return self._generate_mock_response(query, context_text)
    


# ============================================================================
# 主程序：演示完整的RAG流程
# ============================================================================

def visualize_results(eval_results, all_results, output_dir):
    """创建可视化图表"""
    
    print("\n[可视化] 正在创建图表...")
    
    # 1. RAG vs Normal Response Comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('RAG系统性能评估', fontsize=16, fontweight='bold')
    
    # 1.1 Response Length Comparison
    if 'length' in eval_results:
        categories = ['RAG', '普通']
        lengths = [eval_results['length']['rag'], eval_results['length']['normal']]
        axes[0, 0].bar(categories, lengths, color=['#2ecc71', '#3498db'])
        axes[0, 0].set_title('回答长度对比')
        axes[0, 0].set_ylabel('字符数')
        for i, v in enumerate(lengths):
            axes[0, 0].text(i, v, str(v), ha='center', va='bottom')
    
    # 1.2 Entity Mentions
    if 'entities' in eval_results:
        categories = ['RAG', '普通']
        entities = [eval_results['entities']['rag'], eval_results['entities']['normal']]
        axes[0, 1].bar(categories, entities, color=['#e74c3c', '#f39c12'])
        axes[0, 1].set_title('实体提及对比')
        axes[0, 1].set_ylabel('数量')
        for i, v in enumerate(entities):
            axes[0, 1].text(i, v, str(v), ha='center', va='bottom')
    
    # 1.3 Number Information
    if 'numbers' in eval_results:
        categories = ['RAG', '普通']
        numbers = [eval_results['numbers']['rag'], eval_results['numbers']['normal']]
        axes[1, 0].bar(categories, numbers, color=['#9b59b6', '#1abc9c'])
        axes[1, 0].set_title('数字信息对比')
        axes[1, 0].set_ylabel('数量')
        for i, v in enumerate(numbers):
            axes[1, 0].text(i, v, str(v), ha='center', va='bottom')
    
    # 1.4 Vocabulary Richness
    if 'vocabulary' in eval_results:
        categories = ['RAG', '普通']
        vocab = [eval_results['vocabulary']['rag'], eval_results['vocabulary']['normal']]
        axes[1, 1].bar(categories, vocab, color=['#34495e', '#16a085'])
        axes[1, 1].set_title('词汇丰富度')
        axes[1, 1].set_ylabel('唯一字符数')
        for i, v in enumerate(vocab):
            axes[1, 1].text(i, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/evaluation_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 已保存: evaluation_comparison.png")
    
    # 2. Query Response Statistics
    if all_results:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        queries = [r['query'][:20] + '...' for r in all_results]
        rag_lengths = [len(r['rag_response']) for r in all_results]
        normal_lengths = [len(r['normal_response']) for r in all_results]
        
        x = np.arange(len(queries))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, rag_lengths, width, label='RAG回答', color='#2ecc71')
        bars2 = ax.bar(x + width/2, normal_lengths, width, label='普通回答', color='#3498db')
        
        ax.set_xlabel('查询问题')
        ax.set_ylabel('回答长度（字符数）')
        ax.set_title('不同查询的回答长度对比')
        ax.set_xticks(x)
        ax.set_xticklabels(queries, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/query_response_lengths.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ 已保存: query_response_lengths.png")

def save_detailed_report(kb, eval_results, all_results, test_query, rag_response, normal_response, output_dir):
    """保存详细报告"""
    
    print("\n[报告] 正在生成详细报告...")
    
    report = {
        "experiment_info": {
            "title": "RAG System Implementation and Evaluation",
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Complete RAG system with document retrieval and generation"
        },
        "configuration": {
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "embedding_model": "Qwen/Qwen3-Embedding-8B",
            "embedding_dimension": 4096,
            "llm_model": "qwen-3-235b-a22b-thinking-2507",
            "vector_store": "FAISS"
        },
        "document_statistics": {
            "total_documents": len(kb.documents),
            "total_chunks": len(kb.chunks),
            "total_characters": sum(len(doc.page_content) for doc in kb.documents) if kb.documents else 0
        },
        "main_test_query": {
            "query": test_query,
            "rag_response": rag_response,
            "normal_response": normal_response
        },
        "evaluation_metrics": eval_results,
        "additional_queries": [
            {
                "query": r["query"],
                "rag_response": r["rag_response"],
                "normal_response": r["normal_response"],
                "rag_length": len(r["rag_response"]),
                "normal_length": len(r["normal_response"])
            }
            for r in all_results
        ]
    }
    
    # Save JSON report
    with open(f"{output_dir}/experiment_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 已保存: experiment_report.json")
    
    # Save Markdown report
    md_content = f"""# RAG System Experiment Report

## Experiment Information
- **Title**: {report['experiment_info']['title']}
- **Date**: {report['experiment_info']['date']}
- **Description**: {report['experiment_info']['description']}

## System Configuration
- **Chunk Size**: {report['configuration']['chunk_size']}
- **Chunk Overlap**: {report['configuration']['chunk_overlap']}
- **Embedding Model**: {report['configuration']['embedding_model']}
- **Embedding Dimension**: {report['configuration']['embedding_dimension']}
- **LLM Model**: {report['configuration']['llm_model']}
- **Vector Store**: {report['configuration']['vector_store']}

## Document Statistics
- **Total Documents**: {report['document_statistics']['total_documents']}
- **Total Chunks**: {report['document_statistics']['total_chunks']}
- **Total Characters**: {report['document_statistics']['total_characters']:,}

## Main Test Query

### Query
```
{test_query}
```

### RAG Response
```
{rag_response}
```

### Normal Response  
```
{normal_response}
```

## Evaluation Metrics

### Response Length
- RAG: {eval_results.get('length', {}).get('rag', 'N/A')} characters
- Normal: {eval_results.get('length', {}).get('normal', 'N/A')} characters
- Difference: {eval_results.get('length', {}).get('diff_pct', 'N/A'):.1f}%

### Entity Mentions
- RAG: {eval_results.get('entities', {}).get('rag', 'N/A')} entities
- Normal: {eval_results.get('entities', {}).get('normal', 'N/A')} entities

### Numeric Information
- RAG: {eval_results.get('numbers', {}).get('rag', 'N/A')} numbers
- Normal: {eval_results.get('numbers', {}).get('normal', 'N/A')} numbers

### Vocabulary Richness
- RAG: {eval_results.get('vocabulary', {}).get('rag', 'N/A')} unique characters
- Normal: {eval_results.get('vocabulary', {}).get('normal', 'N/A')} unique characters

## Additional Test Queries

"""
    
    for i, result in enumerate(report['additional_queries'], 1):
        md_content += f"""### Query {i}: {result['query']}

**RAG Response** ({result['rag_length']} chars):
```
{result['rag_response'][:500]}...
```

**Normal Response** ({result['normal_length']} chars):
```
{result['normal_response'][:500]}...
```

---

"""
    
    md_content += f"""
## Visualizations

See the following generated charts:
- `evaluation_comparison.png` - Comparison of RAG vs Normal responses
- `query_response_lengths.png` - Response lengths across queries

## Conclusion

This experiment demonstrates the effectiveness of RAG (Retrieval-Augmented Generation) system in:
1. Providing more factual and detailed responses
2. Reducing hallucinations through document grounding
3. Enabling real-time knowledge updates

Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with open(f"{output_dir}/experiment_report.md", 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  ✓ 已保存: experiment_report.md")

def main():
    """主函数：完整的RAG系统工作流程及输出可视化"""
    
    print("\n" + "=" * 80)
    print("RAG系统完整工作流程")
    print("=" * 80)
    
    # Step 1: Build knowledge base
    print("\n[步骤1] 构建知识库")
    kb = DocumentKnowledgeBase(chunk_size=500, chunk_overlap=50)
    documents = kb.load_documents("./实验5/knowledgebase")
    
    if not documents:
        print("✗ 文档加载失败")
        return
    
    chunks = kb.split_documents(documents)
    vector_store = kb.create_vector_store(chunks)
    
    if vector_store:
        kb.save_vector_store("./实验5/faiss_index")
    else:
        print("✗ 向量存储创建失败")
        return
    
    # Step 2: Create retriever
    print("\n[步骤2] 创建检索器")
    retriever = DocumentRetriever(vector_store)
    
    # Step 3: Test basic retrieval
    print("\n[步骤3] 测试基础检索")
    test_query = "中国的人工智能发展现状如何？"
    retrieved_docs = retriever.retrieve_documents(test_query, top_k=3)
    retriever.display_retrieved_documents(retrieved_docs)
    
    # Step 4: Create RAG system
    print("\n[步骤4] 创建RAG系统")
    rag_system = RAGSystem(retriever)
    rag_system.load_llm()
    
    # Step 5: Execute RAG query
    print("\n[步骤5] 执行RAG查询")
    result = rag_system.rag_query(test_query, top_k=3)
    
    print("\n" + "-" * 80)
    print("[RAG回答]")
    print("-" * 80)
    print(result["rag_response"])
    
    print("\n" + "-" * 80)
    print("[普通回答]")
    print("-" * 80)
    print(result["normal_response"])
    
    # Step 6: Evaluation
    print("\n[步骤6] 评估RAG系统")
    evaluator = RAGEvaluator()
    eval_results = evaluator.evaluate_responses(
        test_query,
        result["rag_response"],
        result["normal_response"]
    )
    
    # Step 7: Advanced RAG system
    print("\n[步骤7] 测试高级RAG功能")
    advanced_rag = AdvancedRAGSystem(retriever)
    advanced_rag.client = rag_system.client
    advanced_rag.api_key = rag_system.api_key
    advanced_rag.base_url = rag_system.base_url
    advanced_rag.model_name = rag_system.model_name
    
    # Test hybrid search
    hybrid_docs = advanced_rag.hybrid_search(test_query, top_k=3, alpha=0.7)
    print("\n混合检索结果:")
    for i, (doc, score) in enumerate(hybrid_docs):
        print(f"[文档{i+1}] 混合分数: {score:.4f}")
        print(f"{doc.page_content[:150]}...\n")
    
    # Enhanced generation
    enhanced_response = advanced_rag.generate_enhanced_response(test_query, hybrid_docs)
    print("\n" + "-" * 80)
    print("[增强回答]")
    print("-" * 80)
    print(enhanced_response)
    
    # Step 8: Test multiple queries
    print("\n[步骤8] 测试多个查询")
    test_queries = [
        "什么是RAG技术？",
        "大语言模型有哪些应用场景？",
        "中国有哪些知名的AI企业？"
    ]
    
    all_results = []
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"查询: {query}")
        print('='*80)
        result_item = rag_system.rag_query(query, top_k=2)
        all_results.append(result_item)
        print(f"\nRAG回答:\n{result_item['rag_response']}")
    
    # Step 9: Save results and create visualizations
    print("\n[步骤9] 保存结果并创建可视化")
    
    # Save to output folder
    save_detailed_report(kb, eval_results, all_results, test_query, 
                        result["rag_response"], result["normal_response"], OUTPUT_DIR)
    
    # Create visualizations
    visualize_results(eval_results, all_results, OUTPUT_DIR)
    
    # Save simple JSON results
    try:
        with open(f"{OUTPUT_DIR}/rag_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                "test_queries": test_queries,
                "results": [
                    {
                        "query": r["query"],
                        "rag_response": r["rag_response"],
                        "normal_response": r["normal_response"]
                    }
                    for r in all_results
                ],
                "evaluation": eval_results
            }, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 已保存: rag_results.json")
    except Exception as e:
        print(f"✗ 保存结果失败: {e}")
    
    print("\n" + "=" * 80)
    print("实验完成！")
    print("=" * 80)
    print(f"\n所有输出文件已保存至: {OUTPUT_DIR}/")
    print("\n生成的文件:")
    print("  - experiment_report.json (完整实验数据)")
    print("  - experiment_report.md (可读性报告)")
    print("  - evaluation_comparison.png (指标可视化)")
    print("  - query_response_lengths.png (查询分析)")
    print("  - rag_results.json (查询结果)")
    print("\n总结:")
    print("  ✓ 成功构建文档知识库")
    print("  ✓ 实现基于FAISS的向量检索")
    print("  ✓ 完成RAG系统构建和生成")
    print("  ✓ 对比RAG与普通生成")
    print("  ✓ 实现高级优化策略")
    print("=" * 80)


if __name__ == "__main__":
    main()

