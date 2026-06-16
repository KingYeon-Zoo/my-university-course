import { useState, useRef, KeyboardEvent } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Paperclip, Image, Mic, Send, Square, X, FileText, Clock, CheckCircle } from "lucide-react";
import { cn } from "./ui/utils";

interface PendingImage {
  id: string;
  file: File;
  dataUrl: string;
  thumbnail: string;
}

interface PendingPDF {
  id: string;
  file: File;
  filename: string;
  size: number;
  processed?: boolean;
}

interface PDFProcessing {
  isProcessing: boolean;
  progress: number;
  step: string;
  message: string;
}

interface PendingAudio {
  id: string;
  file: File;
  filename: string;
  duration: number;
  transcription?: string;
  processed?: boolean;
}

interface 输入栏Props {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onStop: () => void;
  onUploadPDF: (file: File) => void;
  onUploadImage: (file: File) => void;
  onUploadAudio: (file: File) => void;
  isStreaming: boolean;
  disabled?: boolean;
  pendingImages?: PendingImage[];
  onRemoveImage?: (id: string) => void;
  pendingPDFs?: PendingPDF[];
  onRemovePDF?: (id: string) => void;
  pdfProcessing?: PDFProcessing;
  pendingAudios?: PendingAudio[];
  onRemoveAudio?: (id: string) => void;
}

export function 输入栏({
  value,
  onChange,
  onSend,
  onStop,
  onUploadPDF,
  onUploadImage,
  onUploadAudio,
  isStreaming,
  disabled = false,
  pendingImages = [],
  onRemoveImage,
  pendingPDFs = [],
  onRemovePDF,
  pdfProcessing,
  pendingAudios = [],
  onRemoveAudio
}: 输入栏Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const pdfInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);  
  const audioInputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if ((value.trim() || pendingImages.length > 0 || pendingPDFs.length > 0 || pendingAudios.length > 0) && !isStreaming) {
        onSend();
      }
    }
    
    // 键盘快捷键
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'u':
        case 'U':
          e.preventDefault();
          pdfInputRef.current?.click();
          break;
        case 'i':
        case 'I':
          e.preventDefault();
          imageInputRef.current?.click();
          break;
        case 'm':
        case 'M':
          e.preventDefault();
          audioInputRef.current?.click();
          break;
      }
    }
  };

  const handleFileUpload = (
    inputRef: React.RefObject<HTMLInputElement>,
    acceptTypes: string,
    onUpload: (file: File) => void
  ) => {
    if (inputRef.current) {
      inputRef.current.accept = acceptTypes;
      inputRef.current.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (file) {
          onUpload(file);
        }
      };
      inputRef.current.click();
    }
  };

  return (
    <div className={cn(
      "bg-background border-t border-border p-4",
      (pendingImages.length > 0 || pendingPDFs.length > 0 || pendingAudios.length > 0 || pdfProcessing?.isProcessing) ? "pb-4" : "h-20"
    )}>
      {/* PDF处理进度 */}
      {pdfProcessing?.isProcessing && (
        <div className="max-w-4xl mx-auto mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-blue-500 animate-spin" />
            <span className="text-sm font-medium text-blue-700">正在处理PDF文档...</span>
          </div>
          <div className="w-full bg-blue-100 rounded-full h-2 mb-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${pdfProcessing.progress}%` }}
            />
          </div>
          <p className="text-xs text-blue-600">{pdfProcessing.message}</p>
        </div>
      )}
      
      {/* 暂存PDF预览区 */}
      {pendingPDFs.length > 0 && (
        <div className="max-w-4xl mx-auto mb-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-muted-foreground">等待发送的文档:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {pendingPDFs.map((pdf) => (
              <div key={pdf.id} className="relative group bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-lg p-3 min-w-[120px] hover:shadow-md transition-all duration-200">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex items-center justify-center w-8 h-8 bg-red-500 rounded-lg shadow-sm">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  {pdf.processed && <CheckCircle className="w-4 h-4 text-green-500" />}
                </div>
                <button
                  onClick={() => onRemovePDF?.(pdf.id)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </button>
                <div className="text-xs font-medium text-gray-700 truncate mb-1" title={pdf.filename}>
                  {pdf.filename}
                </div>
                <div className="text-xs text-gray-500">
                  {(pdf.size / 1024).toFixed(1)} KB
                </div>
                {pdf.processed && (
                  <div className="text-xs text-green-600 mt-1">已处理</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* 暂存图片预览区 */}
      {pendingImages.length > 0 && (
        <div className="max-w-4xl mx-auto mb-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-muted-foreground">等待发送的图片:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {pendingImages.map((img) => (
              <div key={img.id} className="relative group">
                <img
                  src={img.thumbnail}
                  alt={img.file.name}
                  className="w-16 h-16 object-cover rounded-lg border border-border"
                />
                <button
                  onClick={() => onRemoveImage?.(img.id)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1 rounded-b-lg truncate">
                  {img.file.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* 暂存音频预览区 */}
      {pendingAudios.length > 0 && (
        <div className="max-w-4xl mx-auto mb-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-muted-foreground">等待发送的音频:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {pendingAudios.map((audio) => (
              <div key={audio.id} className="relative group">
                <div className="w-40 h-16 bg-muted rounded-lg border border-border flex items-center justify-center">
                  <div className="flex items-center gap-2">
                    <Mic className="w-4 h-4 text-muted-foreground" />
                    <div className="text-xs text-muted-foreground">
                      <div className="font-medium">{audio.filename}</div>
                      <div>{Math.round(audio.duration)}s</div>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => onRemoveAudio?.(audio.id)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </button>
                {audio.transcription && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1 rounded-b-lg">
                    <div className="truncate">{audio.transcription}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        {/* 文本输入框 */}
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              [pendingImages.length > 0 && "图片", pendingPDFs.length > 0 && "文档", pendingAudios.length > 0 && "音频"]
                .filter(Boolean).length > 0
                ? `输入关于${[pendingImages.length > 0 && "图片", pendingPDFs.length > 0 && "文档", pendingAudios.length > 0 && "音频"]
                    .filter(Boolean).join("、")}的问题... (Enter 发送)`
                : "输入您的问题... (Enter 发送，Shift+Enter 换行)"
            }
            className="min-h-[48px] max-h-32 resize-none pr-16"
            disabled={disabled}
          />
          
          {/* 上传按钮组 */}
          <div className="absolute right-2 bottom-2 flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="w-8 h-8 p-0 hover:bg-accent"
              onClick={() => handleFileUpload(pdfInputRef, '.pdf', onUploadPDF)}
              disabled={disabled}
              title="上传 PDF (Ctrl/Cmd+U)"
            >
              <Paperclip className="w-4 h-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              className="w-8 h-8 p-0 hover:bg-accent"
              onClick={() => handleFileUpload(imageInputRef, 'image/*', onUploadImage)}
              disabled={disabled}
              title="上传图片 (Ctrl/Cmd+I)"
            >
              <Image className="w-4 h-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              className="w-8 h-8 p-0 hover:bg-accent"
              onClick={() => handleFileUpload(audioInputRef, 'audio/*,video/mp4,video/avi,video/mov,video/mkv,video/webm', onUploadAudio)}
              disabled={disabled}
              title="上传音频/视频 (Ctrl/Cmd+M)"
            >
              <Mic className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* 发送/停止按钮 */}
        <div className="flex items-center gap-2">
          {isStreaming ? (
            <Button
              onClick={onStop}
              variant="destructive"
              size="sm"
              className="w-10 h-10 p-0"
            >
              <Square className="w-4 h-4" />
            </Button>
          ) : (
            <Button
              onClick={onSend}
              disabled={(!value.trim() && pendingImages.length === 0 && pendingPDFs.length === 0 && pendingAudios.length === 0) || disabled}
              className="w-10 h-10 p-0 bg-blue-500 hover:bg-blue-600"
            >
              <Send className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 隐藏的文件输入 */}
      <input ref={pdfInputRef} type="file" className="hidden" />
      <input ref={imageInputRef} type="file" className="hidden" />
      <input ref={audioInputRef} type="file" className="hidden" />
    </div>
  );
}