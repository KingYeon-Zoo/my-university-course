import { Sheet, SheetContent, SheetHeader, SheetTitle } from "./ui/sheet";
import { ScrollArea } from "./ui/scroll-area";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { X, Download } from "lucide-react";

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: string;
}

interface 日志抽屉Props {
  isOpen: boolean;
  onClose: () => void;
  logs: LogEntry[];
  fileName: string;
}

export function 日志抽屉({ isOpen, onClose, logs, fileName }: 日志抽屉Props) {
  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'bg-blue-100 text-blue-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'success': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const downloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] ${log.level.toUpperCase()}: ${log.message}${log.details ? '\n  ' + log.details : ''}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fileName}_parsing_log.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[500px]">
        <SheetHeader className="flex flex-row items-center justify-between">
          <SheetTitle>解析日志: {fileName}</SheetTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={downloadLogs}
              className="h-8"
            >
              <Download className="w-3 h-3 mr-1" />
              导出
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="w-8 h-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)] mt-4">
          <div className="space-y-3">
            {logs.map((log, index) => (
              <div
                key={index}
                className="p-3 border rounded-lg bg-card"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Badge className={getLevelColor(log.level)}>
                    {log.level.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {log.timestamp}
                  </span>
                </div>
                
                <div className="text-sm">
                  <p>{log.message}</p>
                  {log.details && (
                    <div className="mt-2 p-2 bg-muted rounded text-xs font-mono">
                      {log.details}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {logs.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                <p>暂无日志记录</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}