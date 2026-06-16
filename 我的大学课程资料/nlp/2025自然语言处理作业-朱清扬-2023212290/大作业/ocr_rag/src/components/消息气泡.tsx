import { cn } from "./ui/utils";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { Bot, User, Wrench, FileText } from "lucide-react";
import { 引用上标 } from "./引用上标";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface ContentBlock {
  type: 'text' | 'image' | 'audio' | 'pdf';
  content: string;
  thumbnail?: string;
  transcription?: string;
  filename?: string;
  filesize?: number;
}

export interface Reference {
  id: number;
  text: string;
  source: string;
  page: number;
  chunk_id: number;
  source_info: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  contentBlocks: ContentBlock[];
  references?: Reference[];
  timestamp: Date;
  isStreaming?: boolean;
}

interface 消息气泡Props {
  message: Message;
  onReferenceClick: (references: Reference[]) => void;
}

export function 消息气泡({ message, onReferenceClick }: 消息气泡Props) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isTool = message.role === 'tool';

  const renderAvatar = () => {
    if (isUser) {
      return (
        <Avatar className="w-8 h-8">
          <AvatarFallback>
            <User className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      );
    } else if (isAssistant) {
      return (
        <Avatar className="w-8 h-8">
          <AvatarFallback className="bg-blue-500 text-white">
            <Bot className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      );
    } else {
      return (
        <Avatar className="w-8 h-8">
          <AvatarFallback className="bg-orange-500 text-white">
            <Wrench className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      );
    }
  };

  const renderContent = (block: ContentBlock, index: number) => {
    switch (block.type) {
      case 'text':

        
        // 先处理引用标记，再进行Markdown渲染
        const processContent = () => {
          const parts = block.content.split(/(\[\d+\])/g);
          
          return parts.map((part, i) => {
            const match = part.match(/\[(\d+)\]/);
                          if (match) {
                if (message.references && message.references.length > 0) {
                  const refIndex = parseInt(match[1]) - 1;
                  const ref = message.references[refIndex];
                  
                  if (ref) {
                    return (
                      <引用上标
                        key={i}
                        number={match[1]}
                        onClick={() => {
                          console.log('🖱️ 点击引用:', ref);
                          onReferenceClick([ref]);
                        }}
                      />
                    );
                  }
                }
                
                // 如果没有引用数据，显示不可点击的引用标记
                return (
                  <引用上标
                    key={i}
                    number={match[1]}
                    onClick={() => {
                      console.log('❌ 点击了无效引用 - 引用数据缺失');
                    }}
                    className="opacity-50 cursor-not-allowed"
                  />
                );
              }
            
            // 对纯文本部分进行Markdown渲染
            if (part && !part.match(/\[\d+\]/)) {
              return (
                <ReactMarkdown
                  key={i}
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // 段落样式
                    p: ({ children }) => (
                      <span className="inline">
                        {children}
                      </span>
                    ),
                    // 代码块样式
                    code: ({ className, children, ...props }) => (
                      <code 
                        className={cn(
                          "relative rounded bg-muted px-1 py-0.5 font-mono text-sm font-semibold",
                          className
                        )} 
                        {...props}
                      >
                        {children}
                      </code>
                    ),
                    // 预格式化代码块
                    pre: ({ children }) => (
                      <pre className="overflow-x-auto rounded-lg bg-muted p-3 text-sm my-2">
                        {children}
                      </pre>
                    ),
                    // 列表样式
                    ul: ({ children }) => (
                      <ul className="my-2 ml-4 list-disc space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="my-2 ml-4 list-decimal space-y-1">
                        {children}
                      </ol>
                    ),
                    // 强调样式
                    strong: ({ children }) => (
                      <strong className="font-semibold text-foreground">
                        {children}
                      </strong>
                    ),
                    // 标题样式
                    h1: ({ children }) => (
                      <h1 className="text-lg font-bold mb-2 mt-4 first:mt-0">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-sm font-medium mb-1 mt-2 first:mt-0">{children}</h3>
                    ),
                  }}
                >
                  {part}
                </ReactMarkdown>
              );
            }
            
            return <span key={i}>{part}</span>;
          });
        };

        return (
          <div key={index} className="prose prose-sm max-w-none dark:prose-invert">
            <div className="space-y-1">
              {processContent()}
            </div>
          </div>
        );
      
      case 'image':
        return (
          <div key={index} className="mt-2">
            <img
              src={block.thumbnail || block.content}
              alt="上传的图片"
              className={cn(
                "max-w-sm rounded-lg border shadow-sm",
                isUser 
                  ? "border-blue-300 bg-blue-50/30" 
                  : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
              )}
            />
          </div>
        );
      
      case 'audio':
        return (
          <div key={index} className={cn(
            "mt-2 p-3 rounded-lg border",
            isUser 
              ? "bg-blue-600/10 border-blue-300/20" 
              : "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700"
          )}>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary" className="text-xs">🎙️ 音频</Badge>
              <span className={cn(
                "text-xs",
                isUser 
                  ? "text-blue-200" 
                  : "text-gray-500 dark:text-gray-400"
              )}>
                已转写
              </span>
            </div>
            {block.transcription && (
              <div className={cn(
                "text-sm leading-relaxed",
                isUser 
                  ? "text-white/90" 
                  : "text-gray-700 dark:text-gray-300"
              )}>
                <div className="relative">
                  <div className={cn(
                    "absolute left-0 top-0 w-1 h-full rounded-full",
                    isUser ? "bg-blue-300/50" : "bg-blue-500/30"
                  )} />
                  <div className="pl-4">
                    "{block.transcription}"
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      
      case 'pdf':
        return (
          <div key={index} className={cn(
            "mt-2 p-3 rounded-lg border",
            isUser 
              ? "bg-red-50 border-red-200" 
              : "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800"
          )}>
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-red-500 rounded-lg shadow-sm">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <div className={cn(
                  "font-medium text-sm",
                  isUser 
                    ? "text-red-800" 
                    : "text-red-700 dark:text-red-300"
                )}>
                  {block.filename || 'PDF文档'}
                </div>
                {block.filesize && (
                  <div className={cn(
                    "text-xs",
                    isUser 
                      ? "text-red-600" 
                      : "text-red-600 dark:text-red-400"
                  )}>
                    {(block.filesize / 1024).toFixed(1)} KB
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      
      default:
        return <div key={index}>{block.content}</div>;
    }
  };

  return (
    <div className={cn(
      "flex gap-3 mb-4",
      isUser && "flex-row-reverse"
    )}>
      {renderAvatar()}
      
      <div 
        className={cn(
          "max-w-[70%] rounded-lg px-4 py-3",
          isUser && "bg-blue-500 text-white ml-auto",
          isAssistant && "bg-white text-gray-900 border border-gray-200 shadow-md",
          isTool && "bg-orange-50 border-orange-200 text-orange-900"
        )}
      >
        {/* 角色标识 */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary" className={cn(
              "text-xs",
              isAssistant 
                ? "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800" 
                : "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800"
            )}>
              {isAssistant ? "助手" : "工具"}
            </Badge>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {message.timestamp.toLocaleTimeString()}
            </span>
          </div>
        )}

        {/* 内容块 */}
        <div className="space-y-2">
          {message.contentBlocks.map((block, index) => renderContent(block, index))}
        </div>

        {/* 流式输出骨架屏 */}
        {message.isStreaming && (
          <div className="flex items-center gap-1 mt-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        )}
      </div>
    </div>
  );
}