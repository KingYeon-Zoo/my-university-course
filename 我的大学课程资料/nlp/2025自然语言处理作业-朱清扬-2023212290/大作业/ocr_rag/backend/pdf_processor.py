import base64
import io
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Any, Iterator, Tuple
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger
import tempfile
import os

class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _extract_text_with_pymupdf(self, pdf_path: str) -> List[Document]:
        """
        使用PyMuPDF提取PDF文本（备用方案）
        当unstructured[pdf]不可用时使用
        """
        documents = []
        try:
            pdf_doc = fitz.open(pdf_path)
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():  # 只添加非空页面
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "page_number": page_num + 1,
                            "total_pages": len(pdf_doc)
                        }
                    )
                    documents.append(doc)
            
            pdf_doc.close()
            logger.info(f"PyMuPDF提取了 {len(documents)} 页文本")
            return documents
            
        except Exception as e:
            logger.error(f"PyMuPDF提取失败: {str(e)}")
            raise
    
    async def process_pdf_stream(self, file_content: bytes, filename: str) -> Iterator[Dict[str, Any]]:
        """
        流式处理PDF文档
        返回处理进度和结果
        """
        try:
            # Step 1: 保存临时文件
            yield {
                "type": "progress",
                "step": "saving_file",
                "message": f"正在保存文件 {filename}...",
                "progress": 10
            }
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Step 2: 加载PDF文档
                yield {
                    "type": "progress", 
                    "step": "loading_pdf",
                    "message": "正在分析PDF结构...",
                    "progress": 30
                }
                
                # 使用UnstructuredLoader加载PDF（简化配置，避免依赖问题）
                try:
                    loader = UnstructuredLoader(
                        file_path=tmp_file_path,
                        partition_via_api=False,  # 本地处理，不使用API
                        strategy="fast",  # 使用快速策略，减少依赖
                    )
                    
                    # 加载文档
                    documents = []
                    for doc in loader.lazy_load():
                        documents.append(doc)
                    
                    logger.info(f"PDF加载完成，共 {len(documents)} 个文档块")
                    
                except Exception as load_error:
                    error_msg = str(load_error)
                    
                    # 检查是否是依赖问题
                    if "unstructured[pdf]" in error_msg or "partition_pdf" in error_msg:
                        logger.error(f"PDF处理依赖缺失，尝试使用PyMuPDF备用方案")
                        # 使用PyMuPDF作为备用方案
                        documents = self._extract_text_with_pymupdf(tmp_file_path)
                        logger.info(f"使用PyMuPDF提取完成，共 {len(documents)} 个文档块")
                    else:
                        raise load_error
                
                # Step 3: 文本分块
                yield {
                    "type": "progress",
                    "step": "splitting_text", 
                    "message": f"正在切分文本，共 {len(documents)} 个原始块...",
                    "progress": 60
                }
                
                # 合并所有文档内容并调试输出
                full_text = "\n\n".join([doc.page_content for doc in documents])
                logger.info(f"合并后文本长度: {len(full_text)} 字符")
                
                # 调试：输出前200个字符看看提取到了什么
                preview = full_text[:200] if full_text else "空内容"
                logger.info(f"文本预览: {repr(preview)}")
                
                # 检查文档元数据
                for i, doc in enumerate(documents):
                    logger.info(f"文档{i}: 长度={len(doc.page_content)}, 元数据={doc.metadata}")
                    if doc.page_content:
                        logger.info(f"文档{i}预览: {repr(doc.page_content[:100])}")
                
                # 使用RecursiveCharacterTextSplitter进行智能分块
                text_chunks = self.text_splitter.split_text(full_text)
                logger.info(f"文本分块完成，共 {len(text_chunks)} 个块")
                
                # Step 4: 构建文档块
                yield {
                    "type": "progress",
                    "step": "building_chunks",
                    "message": f"正在构建 {len(text_chunks)} 个文档块...",
                    "progress": 80
                }
                
                # 构建带元数据的文档块（包含页码信息）
                document_chunks = []
                for i, chunk in enumerate(text_chunks):
                    if chunk.strip():  # 过滤空块
                        # 尝试从原始文档块中获取页码信息
                        page_number = 1  # 默认页码
                        if documents:
                            # 寻找包含此chunk内容的原始文档块
                            for doc in documents:
                                if hasattr(doc, 'metadata') and 'page_number' in doc.metadata:
                                    if chunk.strip()[:50] in doc.page_content:
                                        page_number = doc.metadata.get('page_number', 1)
                                        break
                        
                        doc_chunk = {
                            "id": f"{filename}_{i}",
                            "content": chunk.strip(),
                            "metadata": {
                                "source": filename,
                                "chunk_id": i,
                                "chunk_size": len(chunk),
                                "total_chunks": len(text_chunks),
                                "page_number": page_number,
                                "reference_id": f"[{i+1}]",
                                "source_info": f"{filename} - 第{page_number}页"
                            }
                        }
                        document_chunks.append(doc_chunk)
                
                # Step 5: 完成处理
                yield {
                    "type": "progress",
                    "step": "completed",
                    "message": f"处理完成！共生成 {len(document_chunks)} 个文档块",
                    "progress": 100
                }
                
                # 返回处理结果
                yield {
                    "type": "result",
                    "chunks": document_chunks,
                    "summary": {
                        "filename": filename,
                        "total_chunks": len(document_chunks),
                        "total_characters": sum(len(chunk["content"]) for chunk in document_chunks),
                        "processing_strategy": "hi_res"
                    }
                }
                
            finally:
                # 清理临时文件
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"PDF处理失败: {str(e)}")
            yield {
                "type": "error",
                "error": f"PDF处理失败: {str(e)}"
            }
    
    def pdf_page_to_base64(self, pdf_content: bytes, page_number: int) -> str:
        """
        将PDF页面转换为base64编码的图像
        用于多模态模型处理
        """
        try:
            # 从内存中打开PDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page = pdf_document.load_page(page_number - 1)  # 0-based indexing
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            pdf_document.close()
            
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
            
        except Exception as e:
            logger.error(f"PDF页面转图像失败: {str(e)}")
            raise
    
    async def extract_pdf_pages_as_images(self, file_content: bytes, max_pages: int = 5) -> List[str]:
        """
        提取PDF的前几页作为图像，用于多模态处理
        """
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            total_pages = len(pdf_document)
            pages_to_extract = min(max_pages, total_pages)
            
            images = []
            for page_num in range(pages_to_extract):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                images.append(base64_image)
            
            pdf_document.close()
            logger.info(f"提取了 {len(images)} 页PDF图像")
            return images
            
        except Exception as e:
            logger.error(f"PDF图像提取失败: {str(e)}")
            raise 