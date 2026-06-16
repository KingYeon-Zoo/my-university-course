import React, { useState, useEffect, useRef } from "react";
import { 导航栏 } from "./components/导航栏";
import { 侧边栏 } from "./components/侧边栏";
import { chatAPI } from "./api/chat";
import { 顶部栏 } from "./components/顶部栏";
import { 消息气泡, Message, Reference, ContentBlock } from "./components/消息气泡";
import { 引用抽屉 } from "./components/引用抽屉";
import { 输入栏 } from "./components/输入栏";
import { 顶部进度条 } from "./components/顶部进度条";
import { 迷你波形 } from "./components/迷你波形";
import { 日志抽屉 } from "./components/日志抽屉";
import { 轻提示, ToastMessage } from "./components/轻提示";
import { 粒子背景 } from "./components/粒子背景";

import { Alert, AlertDescription } from "./components/ui/alert";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./components/ui/dialog";
import { Button } from "./components/ui/button";

interface ParseStep {
  key: string;
  label: string;
  completed: boolean;
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: string;
}

interface ConversationItem {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
}

export default function App() {
  // 状态管理
  const [知识库, set知识库] = useState("default");
  const [模型, set模型] = useState("qwen-3-235b-a22b-thinking-2507");
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [引用抽屉Open, set引用抽屉Open] = useState(false);
  const [selectedReferences, setSelectedReferences] = useState<Reference[]>([]);
  const [selectedReference, setSelectedReference] = useState<Reference | undefined>();
  const [toast, setToast] = useState<ToastMessage | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  
  // 侧边栏状态
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [conversations, setConversations] = useState<ConversationItem[]>([
    {
      id: '1',
      title: '多模态RAG系统架构设计',
      timestamp: new Date(Date.now() - 86400000),
      messageCount: 12
    },
    {
      id: '2', 
      title: '向量数据库优化策略',
      timestamp: new Date(Date.now() - 172800000),
      messageCount: 8
    },
    {
      id: '3',
      title: 'OCR技术在文档解析中的应用',
      timestamp: new Date(Date.now() - 259200000),
      messageCount: 15
    }
  ]);
  const [activeConversationId, setActiveConversationId] = useState<string>('1');

  // PDF 解析进度相关
  const [parseProgress, setParseProgress] = useState({
    isVisible: false,
    fileName: "",
    progress: 0,
    currentStep: "upload",
    logs: [] as LogEntry[]
  });
  const [logDrawerOpen, setLogDrawerOpen] = useState(false);

  // 音频处理相关
  const [audioFile, setAudioFile] = useState<{ name: string; duration: number } | null>(null);
  const [transcription, setTranscription] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);

  // 图片暂存相关
  const [pendingImages, setPendingImages] = useState<Array<{
    id: string;
    file: File;
    dataUrl: string;
    thumbnail: string;
  }>>([]);

  // PDF暂存相关
  const [pendingPDFs, setPendingPDFs] = useState<Array<{
    id: string;
    file: File;
    filename: string;
    size: number;
    processed?: boolean;
    chunks?: Array<{
      id: string;
      content: string;
      metadata: any;
    }>;
  }>>([]);

  // 音频暂存相关
  const [pendingAudios, setPendingAudios] = useState<Array<{
    id: string;
    file: File;
    filename: string;
    duration: number;
    transcription?: string;
    processed?: boolean;
  }>>([]);

  // PDF处理进度
  const [pdfProcessing, setPdfProcessing] = useState<{
    isProcessing: boolean;
    progress: number;
    step: string;
    message: string;
  }>({
    isProcessing: false,
    progress: 0,
    step: '',
    message: ''
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // 解析步骤定义
  const parseSteps: ParseStep[] = [
    { key: "upload", label: "上传", completed: false },
    { key: "ocr", label: "OCR", completed: false },
    { key: "segment", label: "切分", completed: false },
    { key: "vectorize", label: "向量化", completed: false },
    { key: "store", label: "入库", completed: false }
  ];

  // 模拟引用数据（更新到新的Reference接口）
  const mockReferences: Reference[] = [
    {
      id: 1,
      text: "这是技术规范文档中的重要信息...",
      source: "技术规范文档.pdf",
      page: 15,
      chunk_id: 0,
      source_info: "技术规范文档.pdf - 第15页"
    },
    {
      id: 2,
      text: "用户手册中的操作说明...",
      source: "用户手册.pdf", 
      page: 8,
      chunk_id: 1,
      source_info: "用户手册.pdf - 第8页"
    }
  ];

  // 自动滚动到底部
  useEffect(() => {
    if (scrollAreaRef.current) {
      // 延迟滚动以确保内容已渲染
      const scrollToBottom = () => {
        if (scrollAreaRef.current) {
          const element = scrollAreaRef.current;
          element.scrollTop = element.scrollHeight - element.clientHeight;
        }
      };
      
      // 立即滚动
      scrollToBottom();
      // 延迟滚动确保内容完全渲染
      setTimeout(scrollToBottom, 100);
    }
  }, [messages]);

  // 流式回复时也要自动滚动
  useEffect(() => {
    if (isStreaming && scrollAreaRef.current) {
      const scrollToBottom = () => {
        if (scrollAreaRef.current) {
          const element = scrollAreaRef.current;
          element.scrollTop = element.scrollHeight - element.clientHeight;
        }
      };
      
      const interval = setInterval(scrollToBottom, 300);
      return () => clearInterval(interval);
    }
  }, [isStreaming]);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        set引用抽屉Open(false);
        setLogDrawerOpen(false);
        setSettingsOpen(false);
        setHelpOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // 发送消息
  const handleSend = async () => {
    if ((!inputValue.trim() && pendingImages.length === 0 && pendingAudios.length === 0) || isStreaming) return;

    const currentInput = inputValue;
    
    // 构建用户消息（包含文本、图片和PDF信息）
    const contentBlocks: any[] = [];
    
    // 添加文本内容
    if (currentInput.trim()) {
      contentBlocks.push({ type: 'text', content: currentInput });
    }
    
    // 添加暂存的图片
    if (pendingImages.length > 0) {
      console.log('🖼️ 发送消息时包含图片数量:', pendingImages.length);
      pendingImages.forEach(img => {
        contentBlocks.push({
          type: 'image',
          content: img.dataUrl,
          thumbnail: img.thumbnail
        });
      });
    }

    // 添加暂存的音频
    if (pendingAudios.length > 0) {
      console.log('🎙️ 发送消息时包含音频数量:', pendingAudios.length);
      pendingAudios.forEach((audio, index) => {
        console.log(`🎵 音频 ${index + 1}:`, {
          filename: audio.filename,
          hasTranscription: !!audio.transcription,
          transcriptionPreview: audio.transcription?.substring(0, 100) + '...'
        });
        contentBlocks.push({
          type: 'audio',
          content: '', // 音频文件不直接传输
          transcription: audio.transcription || ''
        });
      });
    }

    // 处理PDF文档（如果有的话）
    let pdfDocuments = null;
    if (pendingPDFs.length > 0) {
      console.log('📄 发送消息时包含PDF数量:', pendingPDFs.length);
      // 为每个PDF文档创建单独的内容块
      pendingPDFs.forEach(pdf => {
        contentBlocks.push({
          type: 'pdf',
          content: pdf.filename,
          filename: pdf.filename,
          filesize: pdf.size
        });
      });
      pdfDocuments = pendingPDFs;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      contentBlocks: contentBlocks,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
            clearPendingImages(); // 清除暂存图片
        clearPendingAudios(); // 清除暂存音频
    setIsStreaming(true);

    try {
      // 准备聊天历史（保持多模态结构）
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.contentBlocks.map(block => block.content).join(''), // 兼容纯文本
        content_blocks: msg.contentBlocks.map(block => ({
          type: block.type,
          content: block.content,
          thumbnail: block.thumbnail,
          transcription: block.transcription // 保持音频转写信息
        }))
      }));

      console.log('📜 传递给API的对话历史:', history.length, '条消息');
      if (history.length > 0) {
        console.log('📝 最近的历史消息预览:', history.slice(-2).map(h => ({
          role: h.role,
          content_blocks_count: h.content_blocks.length,
          has_transcription: h.content_blocks.some(b => b.transcription)
        })));
      }

      // 创建助手消息用于流式更新
      const assistantMessageId = (Date.now() + 1).toString();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        contentBlocks: [{ type: 'text', content: '' }],
        references: [],
        timestamp: new Date(),
        isStreaming: true
      };

      setMessages(prev => [...prev, assistantMessage]);

              // 如果有PDF，先处理PDF并获取内容
        let pdfContent = '';
        let allProcessedPdfChunks: any[] = []; // 直接收集PDF块，不依赖state
        
        if (pdfDocuments && pdfDocuments.length > 0) {
          console.log('🚀 开始处理PDF文档...');
          
          try {
            // 处理所有PDF文档并收集内容和块
            for (const pdf of pdfDocuments) {
              console.log(`📄 处理PDF: ${pdf.filename}`);
              const chunks = await processPDF(pdf);
              if (chunks && chunks.length > 0) {
                // 将PDF内容添加到用户消息中
                const pdfTexts = chunks.map((chunk: any) => chunk.content).join('\n\n');
                pdfContent += `\n\n=== PDF文档：${pdf.filename} ===\n${pdfTexts}`;
                
                // 直接收集PDF块用于引用
                allProcessedPdfChunks = allProcessedPdfChunks.concat(chunks);
                console.log(`✅ PDF ${pdf.filename} 处理完成，提取文本长度: ${pdfTexts.length}，块数: ${chunks.length}`);
              }
            }
            console.log('✅ 所有PDF处理完成，总内容长度:', pdfContent.length, '，总块数:', allProcessedPdfChunks.length);
          } catch (error) {
            console.error('PDF处理失败，继续进行对话:', error);
          }
          
          // 注意：不在这里清除PDF暂存，因为后续还需要使用PDF块信息
        }
        
        // 调用后端流式API
        // 构建API请求的content_blocks
        const apiContentBlocks: Array<{ 
          type: 'image' | 'audio'; 
          content: string; 
          thumbnail?: string;
          transcription?: string;
        }> = [];
        
        // 添加图片内容块
        if (pendingImages.length > 0) {
          pendingImages.forEach(img => {
            apiContentBlocks.push({
              type: 'image' as const,
              content: img.dataUrl,
              thumbnail: img.thumbnail
            });
          });
        }

        // 添加音频内容块
        if (pendingAudios.length > 0) {
          console.log('🔊 添加音频到API请求，数量:', pendingAudios.length);
          pendingAudios.forEach((audio, index) => {
            console.log(`🎵 添加音频 ${index + 1} 到API:`, {
              filename: audio.filename,
              hasTranscription: !!audio.transcription,
              transcriptionLength: audio.transcription?.length || 0
            });
            apiContentBlocks.push({
              type: 'audio' as const,
              content: '', // 音频文件不直接传输
              transcription: audio.transcription || ''
            });
          });
        }

        console.log('📋 最终apiContentBlocks:', apiContentBlocks.map(b => ({
          type: b.type,
          hasContent: !!b.content,
          hasTranscription: !!b.transcription
        })));

        // 构建完整的用户输入（包含PDF内容）
        const fullUserInput = pdfContent ? `${currentInput}${pdfContent}` : currentInput;
        console.log('📤 发送给GPT的完整内容长度:', fullUserInput.length);
        if (pdfContent) {
          console.log('📄 包含PDF内容，预览:', pdfContent.substring(0, 200) + '...');
        }
        
        // 使用直接收集的PDF块信息（不依赖state）
        console.log('📚 传递PDF块信息，总数:', allProcessedPdfChunks.length);

        let fullContent = '';
        for await (const chunk of chatAPI.streamChat({
          content: fullUserInput,
          content_blocks: apiContentBlocks,
          pdf_chunks: allProcessedPdfChunks,
          history: history,
          model: 模型,
          knowledge_base: 知识库
        })) {
        if (chunk.type === 'content_delta' && chunk.content) {
          fullContent += chunk.content;
          
          // 更新消息内容
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { 
                  ...msg, 
                  contentBlocks: [{ type: 'text', content: fullContent }]
                }
              : msg
          ));
        } else if (chunk.type === 'message_complete') {
          // 消息完成
          console.log('🏁 消息完成，引用数量:', chunk.references?.length || 0);
          if (chunk.references && chunk.references.length > 0) {
            console.log('📚 引用详情:', chunk.references);
          }
          
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { 
                  ...msg, 
                  isStreaming: false,
                  references: chunk.references || []
                }
              : msg
          ));
          setIsStreaming(false);
          
          // 聊天完成后清除暂存
          clearPendingPDFs();
          clearPendingAudios();
          break;
        } else if (chunk.type === 'error') {
          console.error('聊天错误:', chunk.error);
          // 显示错误消息
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { 
                  ...msg, 
                  contentBlocks: [{ type: 'text', content: `抱歉，发生了错误：${chunk.error}` }],
                  isStreaming: false
                }
              : msg
          ));
          setIsStreaming(false);
          
          // 错误时也清除暂存
          clearPendingPDFs();
          clearPendingAudios();
          break;
        }
      }
    } catch (error) {
      console.error('API调用失败:', error);
      
      // 显示错误提示
      setToast({
        id: Date.now().toString(),
        type: 'error',
        title: '连接失败',
        description: '无法连接到后端服务，请检查服务是否正常运行'
      });
      
      setIsStreaming(false);
      
      // 异常时也清除暂存
      clearPendingPDFs();
      clearPendingAudios();
    }
  };

  // 停止生成
  const handleStop = () => {
    setIsStreaming(false);
    setMessages(prev => prev.map(msg => ({ ...msg, isStreaming: false })));
  };

  // 引用点击处理
  const handleReferenceClick = (references: Reference[]) => {
    console.log('🔍 点击引用:', references);
    
    if (references.length > 0) {
      const ref = references[0];
      
      // 显示Toast提示
      showToast({
        id: Date.now().toString(),
        type: 'info',
        title: `引用来源：${ref.source_info}`,
        description: ref.text.substring(0, 100) + (ref.text.length > 100 ? '...' : '')
      });
      
      // 保留原有的引用面板功能
      setSelectedReferences(references);
      setSelectedReference(references[0]);
      set引用抽屉Open(true);
    }
  };

  // PDF 上传处理
  const handleUploadPDF = async (file: File) => {
    setParseProgress({
      isVisible: true,
      fileName: file.name,
      progress: 0,
      currentStep: "upload",
      logs: []
    });

    // 模拟解析过程
    const steps = ["upload", "ocr", "segment", "vectorize", "store"];
    let currentStepIndex = 0;

    const processStep = async () => {
      const step = steps[currentStepIndex];
      const stepProgress = ((currentStepIndex + 1) / steps.length) * 100;

      // 添加日志
      const logEntry = {
        timestamp: new Date().toLocaleTimeString(),
        level: 'info' as const,
        message: `开始${parseSteps.find(s => s.key === step)?.label}阶段`,
        details: step === 'ocr' ? '使用 Tesseract OCR 引擎进行文字识��' : undefined
      };

      setParseProgress(prev => ({
        ...prev,
        progress: stepProgress,
        currentStep: step,
        logs: [...prev.logs, logEntry]
      }));

      if (currentStepIndex < steps.length - 1) {
        currentStepIndex++;
        setTimeout(processStep, 1500);
      } else {
        // 完成
        setTimeout(() => {
          setParseProgress(prev => ({ ...prev, isVisible: false }));
          showToast({
            id: Date.now().toString(),
            type: 'success',
            title: 'PDF 解析完成',
            description: `${file.name} 已成功加入知识库`
          });
        }, 1000);
      }
    };

    processStep();
  };

  // 图片上传处理（暂存，不自动发送）
  const handleUploadImage = async (file: File) => {
    console.log('🖼️ 开始处理图片上传:', file.name, file.size);
    
    if (isStreaming) {
      console.log('❌ 当前正在流式响应中，跳过图片上传');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target?.result as string;
      console.log('📁 图片读取完成，数据长度:', imageData.length);
      
      // 将图片添加到暂存区
      const pendingImage = {
        id: Date.now().toString(),
        file: file,
        dataUrl: imageData,
        thumbnail: imageData
      };
      
      setPendingImages(prev => [...prev, pendingImage]);
      console.log('📌 图片已暂存，等待用户输入问题');
      
      showToast({
        id: Date.now().toString(),
        type: 'info',
        title: '图片已上传',
        description: '请输入您的问题，然后点击发送'
      });
    };
    
    reader.readAsDataURL(file);
  };

  // 清除暂存图片
  const clearPendingImages = () => {
    setPendingImages([]);
  };

  // 清除暂存PDF
  const clearPendingPDFs = () => {
    setPendingPDFs([]);
  };

  // 清除暂存音频
  const clearPendingAudios = () => {
    setPendingAudios([]);
  };



  // 简化的PDF上传处理（暂存版）
  const handleUploadPDFNew = async (file: File) => {
    if (isStreaming || pdfProcessing.isProcessing) return;

    console.log('📄 PDF上传:', file.name, file.size);
    
    // 将PDF添加到暂存区
    const pendingPDF = {
      id: Date.now().toString(),
      file: file,
      filename: file.name,
      size: file.size,
      processed: false
    };
    
    setPendingPDFs(prev => [...prev, pendingPDF]);
    
    showToast({
      id: Date.now().toString(),
      type: 'info',
      title: 'PDF已上传',
      description: '请输入您的问题，系统将自动处理PDF并回答'
    });
  };

  // PDF处理函数
  const processPDF = async (pdfFile: {id: string, file: File}) => {
    console.log('🚀 开始处理PDF:', pdfFile.file.name);
    
    setPdfProcessing({
      isProcessing: true,
      progress: 0,
      step: 'preparing',
      message: '准备处理PDF...'
    });

    try {
      // 将PDF转换为base64
      const reader = new FileReader();
      const fileData = await new Promise<string>((resolve, reject) => {
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(pdfFile.file);
      });

      console.log('📤 开始调用PDF处理API');

      // 调用PDF处理API
      const response = await fetch('http://localhost:8000/api/pdf/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: fileData,
          filename: pdfFile.file.name
        })
      });

      if (!response.body) {
        throw new Error('响应体为空');
      }

      const reader2 = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';  // 用于存储不完整的数据

      while (true) {
        const { done, value } = await reader2.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        // 按行分割处理
        const lines = buffer.split('\n');
        // 保留最后一行（可能不完整）
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') continue;
            if (!data) continue;  // 跳过空数据
            
            try {
              const parsed = JSON.parse(data);
              console.log('📦 PDF处理进度:', parsed);

              if (parsed.type === 'progress') {
                setPdfProcessing({
                  isProcessing: true,
                  progress: parsed.progress || 0,
                  step: parsed.step || '',
                  message: parsed.message || ''
                });
              } else if (parsed.type === 'result') {
                // 处理完成，保存结果到state（用于UI显示）
                setPendingPDFs(prev => prev.map(pdf => 
                  pdf.id === pdfFile.id 
                    ? { ...pdf, processed: true, chunks: parsed.chunks }
                    : pdf
                ));
                console.log('✅ PDF处理完成，文档块数量:', parsed.chunks?.length);
                return parsed.chunks; // 返回文档块
              } else if (parsed.type === 'error') {
                throw new Error(parsed.error);
              }
            } catch (e) {
              console.warn('解析PDF处理响应失败:', e, '数据:', data.slice(0, 200));
            }
          }
        }
      }
      
      // 处理最后的缓冲区数据
      if (buffer.trim() && buffer.startsWith('data: ')) {
        const data = buffer.slice(6).trim();
        if (data !== '[DONE]' && data) {
          try {
            const parsed = JSON.parse(data);
            if (parsed.type === 'result') {
              setPendingPDFs(prev => prev.map(pdf => 
                pdf.id === pdfFile.id 
                  ? { ...pdf, processed: true, chunks: parsed.chunks }
                  : pdf
              ));
              console.log('✅ PDF处理完成（缓冲区），文档块数量:', parsed.chunks?.length);
              return parsed.chunks;
            }
          } catch (e) {
            console.warn('解析缓冲区PDF响应失败:', e);
          }
        }
      }

    } catch (error) {
      console.error('PDF处理失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      showToast({
        id: Date.now().toString(),
        type: 'error',
        title: 'PDF处理失败',
        description: `处理 ${pdfFile.file.name} 时出错: ${errorMessage}`
      });
      throw error;
    } finally {
      setPdfProcessing({
        isProcessing: false,
        progress: 0,
        step: '',
        message: ''
      });
    }
  };

  // 音频上传处理  
  const handleUploadAudio = async (file: File) => {
    console.log('🎙️ 音频上传:', file.name, file.size);
    
    try {
      showToast({
        id: Date.now().toString(),
        type: 'info',
        title: '正在处理音频...',
        description: '请稍等，正在进行语音转文字'
      });

      // 调用后端音频处理API
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/audio/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '音频处理失败');
      }

      const result = await response.json();
      console.log('✅ 音频处理成功:', result);

      // 创建待处理音频对象
      const pendingAudio = {
        id: Date.now().toString(),
        file: file,
        filename: result.filename,
        duration: result.duration,
        transcription: result.transcription,
        processed: true
      };

      // 添加到暂存列表
      setPendingAudios(prev => [...prev, pendingAudio]);

      showToast({
        id: Date.now().toString(),
        type: 'success',
        title: '音频处理完成',
        description: `转写内容：${result.transcription.substring(0, 50)}${result.transcription.length > 50 ? '...' : ''}`
      });

    } catch (error) {
      console.error('❌ 音频处理失败:', error);
      showToast({
        id: Date.now().toString(),
        type: 'error',
        title: '音频处理失败',
        description: error instanceof Error ? error.message : '未知错误'
      });
    }
  };

  // 音频转写
  const handleTranscribe = () => {
    setIsTranscribing(true);
    
    setTimeout(() => {
      const mockTranscription = "您好，我想了解关于多模态RAG系统的技术实现细节，特别是在处理图像和文档时的最佳实践。";
      setTranscription(mockTranscription);
      setInputValue(mockTranscription);
      setIsTranscribing(false);
      setAudioFile(null);

      showToast({
        id: Date.now().toString(),
        type: 'success',
        title: '转写完成',
        description: '语音内容已插入到输入框'
      });
    }, 3000);
  };

  // 新建对话
  const handleNewConversation = () => {
    const newId = Date.now().toString();
    const newConversation: ConversationItem = {
      id: newId,
      title: '新对话',
      timestamp: new Date(),
      messageCount: 0
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newId);
    setMessages([]);
  };

  // 选择对话
  const handleConversationSelect = (id: string) => {
    setActiveConversationId(id);
    // 这里可以加载对应对话的消息历史
    setMessages([]);
  };

  // 显示提示
  const showToast = (message: ToastMessage) => {
    setToast(message);
  };

  return (
    <div className="h-screen bg-background flex flex-col relative overflow-hidden">
      {/* 粒子背景 */}
      <粒子背景 />

              {/* 导航栏 */}
        <导航栏 />

      {/* 主内容区域 */}
      <div className="flex-1 flex relative min-h-0">
        {/* 侧边栏 */}
        <侧边栏
          isCollapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          conversations={conversations}
          activeConversationId={activeConversationId}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
          onSettings={() => setSettingsOpen(true)}
          onHelp={() => setHelpOpen(true)}
        />

        {/* 主聊天区域 */}
        <div className="flex-1 flex flex-col relative min-h-0">
          {/* 顶部栏 */}
          <顶部栏
            知识库={知识库}
            模型={模型}
            on知识库Change={set知识库}
            on模型Change={set模型}
            onSettings={() => setSettingsOpen(true)}
            onHelp={() => setHelpOpen(true)}
          />

          {/* 顶部进度条 */}
          <顶部进度条
            isVisible={parseProgress.isVisible}
            fileName={parseProgress.fileName}
            progress={parseProgress.progress}
            currentStep={parseProgress.currentStep}
            steps={parseSteps.map(step => ({
              ...step,
              completed: parseSteps.indexOf(step) < parseSteps.findIndex(s => s.key === parseProgress.currentStep)
            }))}
            onClose={() => setParseProgress(prev => ({ ...prev, isVisible: false }))}
            onViewLog={() => setLogDrawerOpen(true)}
          />

          {/* 消息区域 */}
          <div className={`flex-1 relative ${parseProgress.isVisible ? 'mt-24' : ''}`} style={{ minHeight: 0 }}>
            <div 
              ref={scrollAreaRef} 
              className="absolute inset-0 overflow-y-auto overflow-x-hidden chat-scroll"
            >
              <div className="max-w-4xl mx-auto px-6 py-6 space-y-4 relative z-10 min-h-full">
                {messages.length === 0 && (
                  <div className="text-center py-16">
                    <div className="w-20 h-20 bg-gradient-to-br from-gray-800 to-gray-900 dark:from-gray-100 dark:to-gray-200 rounded-2xl mx-auto mb-8 flex items-center justify-center shadow-2xl">
                      <span className="text-white dark:text-black text-2xl font-bold">RAG</span>
                    </div>
                    <h2 className="text-3xl text-foreground mb-4 font-semibold">
                      欢迎使用多模态 RAG 工作台
                    </h2>
                    <p className="text-muted-foreground text-lg mb-10 max-w-2xl mx-auto">
                      基于先进AI技术，提供专业的文档分析、图像理解和音频处理能力
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
                      <div className="p-6 bg-card backdrop-blur-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-lg transition-all duration-300 group">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg mx-auto mb-4 flex items-center justify-center shadow-lg group-hover:scale-105 group-hover:shadow-blue-200 transition-all duration-300">
                          <span className="text-white text-lg">📝</span>
                        </div>
                        <p className="text-sm font-medium text-card-foreground group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">智能问答</p>
                      </div>
                      <div className="p-6 bg-card backdrop-blur-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:border-green-300 dark:hover:border-green-500 hover:shadow-lg transition-all duration-300 group">
                        <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg mx-auto mb-4 flex items-center justify-center shadow-lg group-hover:scale-105 group-hover:shadow-green-200 transition-all duration-300">
                          <span className="text-white text-lg">🖼️</span>
                        </div>
                        <p className="text-sm font-medium text-card-foreground group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">图片分析</p>
                      </div>
                      <div className="p-6 bg-card backdrop-blur-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-500 hover:shadow-lg transition-all duration-300 group">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg mx-auto mb-4 flex items-center justify-center shadow-lg group-hover:scale-105 group-hover:shadow-purple-200 transition-all duration-300">
                          <span className="text-white text-lg">🎙️</span>
                        </div>
                        <p className="text-sm font-medium text-card-foreground group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">音频转写</p>
                      </div>
                      <div className="p-6 bg-card backdrop-blur-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:border-orange-300 dark:hover:border-orange-500 hover:shadow-lg transition-all duration-300 group">
                        <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg mx-auto mb-4 flex items-center justify-center shadow-lg group-hover:scale-105 group-hover:shadow-orange-200 transition-all duration-300">
                          <span className="text-white text-lg">📄</span>
                        </div>
                        <p className="text-sm font-medium text-card-foreground group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">PDF 解析</p>
                      </div>
                    </div>
                  </div>
                )}

                {messages.map((message) => (
                  <消息气泡
                    key={message.id}
                    message={message}
                    onReferenceClick={handleReferenceClick}
                  />
                ))}

                {/* 音频波形卡片 */}
                {audioFile && (
                  <div className="max-w-md">
                    <迷你波形
                      fileName={audioFile.name}
                      duration={audioFile.duration}
                      onTranscribe={handleTranscribe}
                      isTranscribing={isTranscribing}
                      transcription={transcription}
                    />
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          {/* 输入栏 */}
          <输入栏
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            onStop={handleStop}
            onUploadPDF={handleUploadPDFNew}
            onUploadImage={handleUploadImage}
            onUploadAudio={handleUploadAudio}
            isStreaming={isStreaming}
            pendingImages={pendingImages}
            onRemoveImage={(id) => setPendingImages(prev => prev.filter(img => img.id !== id))}
                    pendingPDFs={pendingPDFs}
        onRemovePDF={(id) => setPendingPDFs(prev => prev.filter(pdf => pdf.id !== id))}
        pdfProcessing={pdfProcessing}
        pendingAudios={pendingAudios}
        onRemoveAudio={(id) => setPendingAudios(prev => prev.filter(audio => audio.id !== id))}
          />
        </div>
      </div>

      {/* 引用抽屉 */}
      <引用抽屉
        isOpen={引用抽屉Open}
        onClose={() => set引用抽屉Open(false)}
        references={selectedReferences}
        selectedReference={selectedReference}
        onReferenceSelect={setSelectedReference}
      />

      {/* 日志抽屉 */}
      <日志抽屉
        isOpen={logDrawerOpen}
        onClose={() => setLogDrawerOpen(false)}
        logs={parseProgress.logs}
        fileName={parseProgress.fileName}
      />

      {/* 轻提示 */}
      <轻提示
        message={toast}
        onClose={() => setToast(null)}
      />

      {/* 设置对话框 */}
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>系统设置</DialogTitle>
            <DialogDescription>
              配置多模态 RAG 系统的参数和偏好设置
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Alert>
              <AlertDescription>
                设置功能正在开发中，敬请期待更多自定义选项。
              </AlertDescription>
            </Alert>
          </div>
        </DialogContent>
      </Dialog>

      {/* 帮助对话框 */}
      <Dialog open={helpOpen} onOpenChange={setHelpOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>使用帮助</DialogTitle>
            <DialogDescription>
              了解如何使用多模态 RAG 工作台的各项功能
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <h4 className="font-medium mb-2">键盘快捷键</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Enter: 发送消息</li>
                <li>• Shift + Enter: 换行</li>
                <li>• Ctrl/Cmd + U: 上传 PDF</li>
                <li>• Ctrl/Cmd + I: 上传图片</li>
                <li>• Esc: 关闭弹窗</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">支持的文件格式</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• PDF: 支持 OCR 文字识别</li>
                <li>• 图片: JPG, PNG, WebP 等常见格式</li>
                <li>• 音频: MP3, WAV, M4A 等格式</li>
              </ul>
            </div>
          </div>
        </DialogContent>
      </Dialog>


    </div>
  );
}