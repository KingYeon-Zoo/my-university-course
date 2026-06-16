import os
import json
import asyncio
import tempfile
import re
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger

# LangChain imports (使用最新版本的标准方式)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.callbacks import AsyncCallbackHandler

# 本地配置
from config import settings
from pdf_processor import PDFProcessor
import re

# 加载环境变量
load_dotenv(override=True)

# 配置日志
logger.add(settings.log_file, rotation="500 MB", level=settings.log_level)

app = FastAPI(
    title="多模态 RAG 工作台 API",
    description="基于 LangChain 1.0 的智能对话 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内容块模型（支持多模态）
class ContentBlock(BaseModel):
    type: str = Field(..., description="内容类型: text, image, audio")
    content: str = Field(..., description="内容数据")
    thumbnail: str = Field(default="", description="缩略图（可选）")
    transcription: str = Field(default="", description="音频转写文本（音频类型专用）")

# 请求模型（支持多模态）
class MessageRequest(BaseModel):
    content: str = Field(default="", description="纯文本内容（兼容旧版）")
    content_blocks: List[ContentBlock] = Field(default=[], description="多模态内容块")
    pdf_chunks: List[Dict[str, Any]] = Field(default=[], description="PDF文档块信息，用于引用溯源")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")
    model: str = Field(default="qwen-3-235b-a22b-thinking-2507", description="使用的模型")
    knowledge_base: str = Field(default="default", description="知识库名称")

class MessageResponse(BaseModel):
    content: str
    role: str
    timestamp: str
    references: List[Dict[str, Any]] = Field(default=[])

# 流式回调处理器
class StreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        self.tokens = []
        self.current_chunk = ""
        
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """处理新的 token"""
        self.tokens.append(token)
        self.current_chunk += token

# 初始化处理器
pdf_processor = PDFProcessor()

# 导入音频处理器
try:
    from audio_processor import AudioProcessor
    audio_processor = AudioProcessor()
    logger.info("[OK] 音频处理器初始化成功")
except ImportError as e:
    logger.warning(f"[WARNING] 音频处理器导入失败: {e}")
    logger.info("[INFO] 音频功能将被禁用，其他功能正常工作")
    logger.info("[INFO] 如需使用音频功能，请安装: pip install moviepy")
    audio_processor = None
except Exception as e:
    logger.warning(f"[WARNING] 音频处理器初始化失败: {e}")
    logger.info("[INFO] 音频功能将被禁用，其他功能正常工作")
    audio_processor = None

# 引用提取函数
def extract_references_from_content(content: str, pdf_chunks: list = None) -> list:
    """
    从AI回答内容中提取引用信息
    """
    references = []
    
    # 查找所有的引用标记 [1], [2], etc.
    reference_pattern = r'\[(\d+)\]'
    matches = re.findall(reference_pattern, content)
    
    if matches and pdf_chunks:
        for match in matches:
            ref_num = int(match)
            if ref_num <= len(pdf_chunks):
                chunk = pdf_chunks[ref_num - 1]  # 索引从0开始
                reference = {
                    "id": ref_num,
                    "text": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", ""),
                    "source": chunk.get("metadata", {}).get("source", "未知来源"),
                    "page": chunk.get("metadata", {}).get("page_number", 1),
                    "chunk_id": chunk.get("metadata", {}).get("chunk_id", 0),
                    "source_info": chunk.get("metadata", {}).get("source_info", "未知来源")
                }
                references.append(reference)
    
    return references

# 初始化聊天模型
def get_chat_model(model_name: str = None):
    """初始化聊天模型，支持模型名称映射"""
    if model_name is None:
        model_name = settings.default_model
    
    # 模型名称映射：将简称映射到完整名称
    model_mapping = {
        "qwen": "qwen-3-235b-a22b-thinking-2507",
        "qwen3": "qwen-3-235b-a22b-thinking-2507",
        "qwen-3": "qwen-3-235b-a22b-thinking-2507",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini"
    }
    
    # 如果传入的是简称，映射到完整名称
    full_model_name = model_mapping.get(model_name, model_name)
    
    logger.info(f"模型名称映射: {model_name} -> {full_model_name}")
        
    try:
        # 使用最新版本的 ChatOpenAI
        model = ChatOpenAI(
            model=full_model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            streaming=True
        )
        return model
    except Exception as e:
        logger.error(f"初始化模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")

def convert_history_to_messages(history: List[Dict[str, Any]]) -> List[BaseMessage]:
    """将历史记录转换为 LangChain 消息格式，支持多模态内容"""
    messages = []
    
    # 添加系统消息
    system_prompt = """你是一个专业的多模态 RAG 助手，具备以下能力：
1. 文档理解与分析
2. 图像内容识别和分析（OCR、对象检测、场景理解）
3. 音频转写与分析
4. 知识检索与问答

重要指导原则：
- 当用户上传图片并提出问题时，请结合图片内容和用户的具体问题来回答
- 仔细分析图片中的文字、图表、对象、场景等所有可见信息
- 根据用户的问题重点，有针对性地分析图片相关部分
- 如果图片包含文字，请准确识别并在回答中引用
- 如果用户只上传图片没有问题，则提供图片的全面分析

引用格式要求（重要）：
- 当回答基于提供的参考文档内容时，必须在相关信息后添加引用标记，格式为[1]、[2]等
- 引用标记应紧跟在相关内容后面，如："这是重要信息[1]"
- 每个不同的文档块使用对应的引用编号
- 如果用户消息中包含"=== 参考文档内容 ==="部分，必须使用其中的内容来回答问题并添加引用
- 只需要在正文中使用角标引用，不需要在最后列出"参考来源"

请以专业、准确、友好的方式回答，并严格遵循引用格式。当有参考文档时，优先使用文档内容回答。"""
    
    messages.append(SystemMessage(content=system_prompt))
    
    # 转换历史消息
    logger.info(f"处理历史消息: {len(history)} 条")
    for i, msg in enumerate(history):
        content = msg.get("content", "")
        content_blocks = msg.get("content_blocks", [])
        logger.info(f"历史消息 {i+1}: {msg['role']}, 内容块数: {len(content_blocks)}, 音频转写: {any(b.get('transcription') for b in content_blocks)}")
        
        if msg["role"] == "user":
            # 如果有多模态内容块，构建复合消息
            if content_blocks:
                message_content = []
                
                # 添加文本内容（如果有）
                if content and content.strip():
                    message_content.append({
                        "type": "text",
                        "text": content
                    })
                
                # 处理内容块
                for block in content_blocks:
                    if block.get("type") == "text":
                        text_data = block.get("content", "")
                        if text_data and text_data.strip():  # 确保有内容
                            message_content.append({
                                "type": "text", 
                                "text": text_data
                            })
                    elif block.get("type") == "image":
                        # 图片内容块 - 严格验证
                        image_data = block.get("content", "")
                        if image_data and image_data.startswith("data:image"):
                            message_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data
                                }
                            })
                    elif block.get("type") == "audio":
                        # 音频内容块 - 使用转写文本
                        transcription = block.get("transcription", "")
                        if transcription and transcription.strip():
                            message_content.append({
                                "type": "text",
                                "text": f"[音频转写] {transcription}"
                            })
                
                # 只有当有有效内容时才添加多模态消息
                if message_content:
                    # 如果只有一个文本块，直接使用字符串
                    if len(message_content) == 1 and message_content[0]["type"] == "text":
                        messages.append(HumanMessage(content=message_content[0]["text"]))
                    else:
                        messages.append(HumanMessage(content=message_content))
                else:
                    # 如果没有有效内容，使用原始文本
                    messages.append(HumanMessage(content=content if content else ""))
            else:
                # 纯文本消息
                messages.append(HumanMessage(content=content if content else ""))
                
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=content))
    
    return messages

def create_multimodal_message(request: MessageRequest) -> HumanMessage:
    """创建多模态消息"""
    logger.info(f"开始构建多模态消息...")
    logger.info(f"文本内容: {request.content[:100]}..." if request.content else "📝 无文本内容")
    logger.info(f"内容块数量: {len(request.content_blocks)}")
    
    message_content = []
    
    # 添加文本内容（如果有）
    if request.content.strip():
        logger.info(f"添加文本内容")
        message_content.append({
            "type": "text",
            "text": request.content
        })
    
    # 处理内容块
    for i, block in enumerate(request.content_blocks):
        logger.info(f"处理内容块 {i+1}/{len(request.content_blocks)}: {block.type}")
        
        if block.type == "text":
            # 确保文本块有内容
            text_content = block.content if block.content else ""
            if text_content.strip():
                logger.info(f"添加文本块: {text_content[:50]}...")
                message_content.append({
                    "type": "text",
                    "text": text_content
                })
        elif block.type == "image":
            # 图片内容块 - 严格验证格式
            image_data = block.content if block.content else ""
            if image_data and image_data.startswith("data:image"):
                logger.info(f"添加图片块，数据长度: {len(image_data)}")
                message_content.append({
                    "type": "image_url", 
                    "image_url": {
                        "url": image_data
                    }
                })
            else:
                logger.warning(f"图片数据格式不正确或为空，跳过此块")
        elif block.type == "audio":
            # 音频内容块 - 直接使用转写文本
            transcription = block.transcription if hasattr(block, 'transcription') else ""
            if transcription and transcription.strip():
                logger.info(f"添加音频转写文本: {transcription[:50]}...")
                message_content.append({
                    "type": "text",
                    "text": f"[音频转写] {transcription}"
                })
            else:
                logger.warning(f"音频块缺少转写文本，跳过")
        elif block.type == "pdf":
            # PDF内容块 - 使用文件名作为标识
            filename = getattr(block, 'filename', '未知文件')
            filesize = getattr(block, 'filesize', 0)
            logger.info(f"添加PDF块: {filename}")
            message_content.append({
                "type": "text", 
                "text": f"[PDF文档] {filename} ({(filesize or 0) / 1024:.1f} KB)"
            })
        else:
            logger.warning(f"未知内容块类型: {block.type}，跳过")
    
    logger.info(f"消息构建完成，有效内容块数量: {len(message_content)}")
    
    # 如果没有任何内容块，返回空消息提示
    if len(message_content) == 0:
        logger.warning(f"消息内容为空，返回默认提示")
        return HumanMessage(content="请提供有效的消息内容")
    
    # 如果只有纯文本，直接返回字符串
    if len(message_content) == 1 and message_content[0]["type"] == "text":
        logger.info(f"返回纯文本消息")
        return HumanMessage(content=message_content[0]["text"])
    
    # 验证所有内容块的格式
    validated_content = []
    for block in message_content:
        if block["type"] == "text":
            # 确保text字段存在且为字符串
            if "text" in block and isinstance(block["text"], str):
                validated_content.append(block)
            else:
                logger.warning(f"文本块格式无效，跳过: {block}")
        elif block["type"] == "image_url":
            # 确保image_url字段存在且格式正确
            if "image_url" in block and isinstance(block["image_url"], dict) and "url" in block["image_url"]:
                validated_content.append(block)
            else:
                logger.warning(f"图片块格式无效，跳过: {block}")
        else:
            logger.warning(f"未知块类型: {block.get('type')}")
    
    # 如果验证后没有有效内容，返回纯文本
    if len(validated_content) == 0:
        logger.warning(f"验证后无有效内容块，返回默认消息")
        return HumanMessage(content=request.content if request.content else "请提供有效的消息内容")
    
    # 多模态消息
    logger.info(f"返回多模态消息，验证后块数: {len(validated_content)}")
    return HumanMessage(content=validated_content)

async def generate_streaming_response(
    messages: List[BaseMessage], 
    model_name: str,
    pdf_chunks: List[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        logger.info(f"开始生成流式响应，模型: {model_name}")
        logger.info(f"消息数量: {len(messages)}")
        
        # 如果有PDF内容，将其添加到系统消息中
        if pdf_chunks and len(pdf_chunks) > 0:
            logger.info(f"检测到 {len(pdf_chunks)} 个PDF块，添加到上下文中")
            pdf_content = "\n\n=== 参考文档内容 ===\n"
            for i, chunk in enumerate(pdf_chunks, 1):
                content = chunk.get("content", "")[:500]  # 限制长度
                source_info = chunk.get("metadata", {}).get("source_info", f"文档块 {i}")
                pdf_content += f"\n[{i}] {content}\n来源: {source_info}\n"
            
            pdf_content += "\n请在回答时引用相关内容，使用格式如 [1]、[2] 等。\n"
            
            # 将PDF内容添加到最后一条用户消息中
            if messages and isinstance(messages[-1], HumanMessage):
                if isinstance(messages[-1].content, str):
                    messages[-1].content = messages[-1].content + pdf_content
                    logger.info(f"已将PDF内容添加到用户消息中，总长度: {len(messages[-1].content)}")
                elif isinstance(messages[-1].content, list):
                    messages[-1].content.append({"type": "text", "text": pdf_content})
                    logger.info(f"已将PDF内容作为新块添加到用户消息中")
        
        # 记录每条消息的类型
        for i, msg in enumerate(messages):
            if hasattr(msg, 'content'):
                if isinstance(msg.content, str):
                    logger.info(f"消息{i+1}: {type(msg).__name__} - 纯文本，长度: {len(msg.content)}")
                elif isinstance(msg.content, list):
                    logger.info(f"消息{i+1}: {type(msg).__name__} - 多模态，块数: {len(msg.content)}")
                    for j, block in enumerate(msg.content):
                        if isinstance(block, dict):
                            logger.info(f"   块{j+1}: {block.get('type', '未知')}")
        
        model = get_chat_model(model_name)
        logger.info(f"模型初始化完成")
        
        # 创建流式响应
        full_response = ""
        logger.info(f"开始流式生成...")
        
        chunk_count = 0
        async for chunk in model.astream(messages):
            chunk_count += 1
            logger.debug(f"收到第 {chunk_count} 个chunk")
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content
                
                # 直接发送每个chunk的内容，避免重复
                data = {
                    "type": "content_delta",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        
        # 提取引用信息
        references = extract_references_from_content(full_response, pdf_chunks) if pdf_chunks else []
        logger.info(f"提取到 {len(references)} 个引用")
        
        # 发送完成信号
        final_data = {
            "type": "message_complete",
            "full_content": full_response,
            "timestamp": datetime.now().isoformat(),
            "references": references
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        logger.error(f"流式响应生成失败: {e}")
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "message": "多模态 RAG 工作台 API",
        "version": "1.0.0",
        "status": "running",
        "langchain_version": "1.0.0"
    }

@app.post("/api/chat/stream")
async def chat_stream(request: MessageRequest):
    """流式聊天接口（支持多模态）"""
    try:
        # 记录请求信息
        has_images = any(block.type == "image" for block in request.content_blocks)
        content_preview = request.content[:100] if request.content else "多模态消息"
        logger.info(f"收到聊天请求: {content_preview}... (包含图片: {has_images})")
        
        # PDF chunks接收情况
        logger.info(f"接收到的PDF chunks数量: {len(request.pdf_chunks) if request.pdf_chunks else 0}")
        if request.pdf_chunks:
            logger.info(f"PDF chunks预览: {str(request.pdf_chunks[:2])[:200]}...")
        else:
            logger.info(f"PDF chunks为空或None: {request.pdf_chunks}")
        
        # 转换消息历史
        messages = convert_history_to_messages(request.history)
        
        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)
        
        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages, request.model, request.pdf_chunks),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_sync(request: MessageRequest):
    """同步聊天接口（支持多模态）"""
    try:
        # 记录请求信息
        has_images = any(block.type == "image" for block in request.content_blocks)
        content_preview = request.content[:100] if request.content else "多模态消息"
        logger.info(f"收到同步聊天请求: {content_preview}... (包含图片: {has_images})")
        
        # 转换消息历史
        messages = convert_history_to_messages(request.history)
        
        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)
        
        # 获取模型响应
        model = get_chat_model(request.model)
        response = await model.ainvoke(messages)
        
        return MessageResponse(
            content=response.content,
            role="assistant",
            timestamp=datetime.now().isoformat(),
            references=[]
        )
        
    except Exception as e:
        logger.error(f"同步聊天请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """获取可用模型列表"""
    return {
        "models": [
            {
                "id": "qwen-3-235b-a22b-thinking-2507",
                "name": "Qwen-3 235B Thinking",
                "description": "阿里通义千问大模型（默认）"
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4O",
                "description": "OpenAI GPT-4O（如果API支持）"
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4O Mini",
                "description": "轻量级 GPT-4 版本"
            }
        ]
    }

@app.get("/api/knowledge-bases")
async def get_knowledge_bases():
    """获取知识库列表"""
    return {
        "knowledge_bases": [
            {
                "id": "default",
                "name": "默认知识库",
                "description": "通用知识库"
            },
            {
                "id": "technical",
                "name": "技术文档",
                "description": "技术相关文档库"
            }
        ]
    }

@app.post("/api/pdf/process")
async def process_pdf_stream(file_data: Dict[str, Any]):
    """
    流式处理PDF文档
    """
    try:
        # 提取请求数据
        content = file_data.get("content", "")  # base64编码的PDF内容
        filename = file_data.get("filename", "document.pdf")
        
        if not content:
            raise HTTPException(status_code=400, detail="缺少PDF内容")
        
        # 解码base64数据
        import base64
        try:
            pdf_bytes = base64.b64decode(content.split(',')[-1])  # 去除data:application/pdf;base64,前缀
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF数据解码失败: {str(e)}")
        
        logger.info(f"开始处理PDF: {filename}, 大小: {len(pdf_bytes)} bytes")
        
        # 定义流式响应生成器
        async def generate_pdf_stream():
            try:
                async for chunk in pdf_processor.process_pdf_stream(pdf_bytes, filename):
                    chunk_data = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {chunk_data}\n\n"
                    
                    # 如果是错误，立即结束
                    if chunk.get("type") == "error":
                        break
                        
            except Exception as e:
                logger.error(f"PDF流式处理失败: {str(e)}")
                error_chunk = json.dumps({
                    "type": "error",
                    "error": f"处理过程中出错: {str(e)}"
                }, ensure_ascii=False)
                yield f"data: {error_chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_pdf_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF处理端点出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf/pages")
async def extract_pdf_pages(file_data: Dict[str, Any]):
    """
    提取PDF页面为图像（用于多模态处理）
    """
    try:
        content = file_data.get("content", "")
        max_pages = file_data.get("max_pages", 3)
        
        if not content:
            raise HTTPException(status_code=400, detail="缺少PDF内容")
        
        # 解码PDF数据
        import base64
        try:
            pdf_bytes = base64.b64decode(content.split(',')[-1])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF数据解码失败: {str(e)}")
        
        logger.info(f"提取PDF页面图像，最多 {max_pages} 页")
        
        # 提取页面图像
        page_images = await pdf_processor.extract_pdf_pages_as_images(pdf_bytes, max_pages)
        
        return {
            "success": True,
            "total_pages": len(page_images),
            "images": page_images
        }
        
    except Exception as e:
        logger.error(f"PDF页面提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# 音频处理端点
# ================================

@app.post("/api/audio/process")
async def process_audio(file: UploadFile = File(...)):
    """处理音频文件，进行语音转文字"""
    
    if not audio_processor:
        raise HTTPException(status_code=500, detail="音频处理器未初始化，请检查依赖")
    
    try:
        logger.info(f"🎙️ 开始处理音频: {file.filename}")
        
        # 检查文件类型
        allowed_types = {
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/flac', 'audio/m4a', 'audio/ogg',
            'video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 处理音频
            result = audio_processor.process_audio_file(temp_file_path, file.filename)
            
            logger.info(f"音频处理成功: {file.filename}")
            return {
                "success": True,
                "filename": result["filename"],
                "transcription": result["transcription"],
                "duration": result["duration"],
                "format": result["format"]
            }
        
        finally:
            # 清理临时文件（Windows下可能需要延迟）
            if os.path.exists(temp_file_path):
                try:
                    # 尝试删除文件
                    os.unlink(temp_file_path)
                except PermissionError:
                    # Windows下文件可能仍被占用，延迟删除
                    import time
                    time.sleep(0.5)  # 等待500ms
                    try:
                        os.unlink(temp_file_path)
                    except Exception as cleanup_error:
                        logger.warning(f"⚠️ 临时文件清理失败（将稍后自动清理）: {cleanup_error}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ 临时文件清理失败: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"音频处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"音频处理失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    ) 