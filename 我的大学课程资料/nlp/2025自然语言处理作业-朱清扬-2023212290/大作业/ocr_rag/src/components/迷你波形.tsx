import { useState } from "react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Play, Pause, FileAudio } from "lucide-react";
import { cn } from "./ui/utils";

interface 迷你波形Props {
  fileName: string;
  duration: number;
  onTranscribe: () => void;
  isTranscribing?: boolean;
  transcription?: string;
  className?: string;
}

export function 迷你波形({
  fileName,
  duration,
  onTranscribe,
  isTranscribing = false,
  transcription,
  className
}: 迷你波形Props) {
  const [isPlaying, setIsPlaying] = useState(false);

  // 模拟波形数据
  const waveformBars = Array.from({ length: 20 }, (_, i) => ({
    height: Math.random() * 100 + 20
  }));

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn(
      "p-4 bg-white border rounded-lg shadow-sm",
      className
    )}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <FileAudio className="w-5 h-5 text-blue-500" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm truncate">{fileName}</span>
            <Badge variant="secondary" className="text-xs">
              {formatDuration(duration)}
            </Badge>
          </div>
          
          {/* 波形可视化 */}
          <div className="flex items-center gap-3 mb-3">
            <Button
              variant="outline"
              size="sm"
              className="w-8 h-8 p-0"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? (
                <Pause className="w-3 h-3" />
              ) : (
                <Play className="w-3 h-3" />
              )}
            </Button>
            
            <div className="flex items-end gap-0.5 flex-1 h-8">
              {waveformBars.map((bar, index) => (
                <div
                  key={index}
                  className={cn(
                    "bg-blue-200 transition-colors",
                    isPlaying && "bg-blue-500"
                  )}
                  style={{
                    width: '2px',
                    height: `${bar.height * 0.3}%`,
                    minHeight: '2px'
                  }}
                />
              ))}
            </div>
          </div>
          
          {/* 转写按钮 */}
          <div className="flex items-center gap-2">
            <Button
              onClick={onTranscribe}
              disabled={isTranscribing}
              size="sm"
              className="h-7"
            >
              {isTranscribing ? "转写中..." : "转写"}
            </Button>
            
            {transcription && (
              <Badge variant="outline" className="text-xs">
                已转写
              </Badge>
            )}
          </div>
          
          {/* 转写结果 */}
          {transcription && (
            <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
              <p className="text-xs text-muted-foreground mb-1">转写结果:</p>
              <p>{transcription}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}