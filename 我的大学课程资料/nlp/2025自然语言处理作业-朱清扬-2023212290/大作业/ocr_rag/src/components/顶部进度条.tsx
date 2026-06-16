import { Progress } from "./ui/progress";
import { Button } from "./ui/button";
import { FileText, X } from "lucide-react";
import { cn } from "./ui/utils";

interface ParseStep {
  key: string;
  label: string;
  completed: boolean;
}

interface 顶部进度条Props {
  isVisible: boolean;
  fileName: string;
  progress: number;
  currentStep: string;
  steps: ParseStep[];
  onClose: () => void;
  onViewLog: () => void;
}

export function 顶部进度条({
  isVisible,
  fileName,
  progress,
  currentStep,
  steps,
  onClose,
  onViewLog
}: 顶部进度条Props) {
  if (!isVisible) return null;

  return (
    <div className="absolute top-12 left-0 right-0 bg-blue-50 border-b border-blue-200 px-6 py-3 z-50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <FileText className="w-4 h-4 text-blue-600" />
          <span className="text-sm">解析文档: {fileName}</span>
          <span className="text-xs text-muted-foreground">
            {steps.find(s => s.key === currentStep)?.label || currentStep}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onViewLog}
            className="text-xs h-6 px-2"
          >
            查看日志
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="w-6 h-6 p-0"
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <Progress value={progress} className="flex-1 h-2" />
        <span className="text-xs text-muted-foreground min-w-[40px]">
          {Math.round(progress)}%
        </span>
      </div>
      
      {/* 步骤指示器 */}
      <div className="flex items-center gap-4 mt-2">
        {steps.map((step, index) => (
          <div key={step.key} className="flex items-center gap-1">
            <div className={cn(
              "w-2 h-2 rounded-full",
              step.completed ? "bg-blue-500" : 
              step.key === currentStep ? "bg-blue-300 animate-pulse" : "bg-gray-300"
            )} />
            <span className="text-xs text-muted-foreground">
              {step.label}
            </span>
            {index < steps.length - 1 && (
              <div className="w-4 h-px bg-gray-300 ml-2" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}