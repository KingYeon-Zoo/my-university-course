import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Settings, HelpCircle } from "lucide-react";

interface 顶部栏Props {
  知识库: string;
  模型: string;
  on知识库Change: (value: string) => void;
  on模型Change: (value: string) => void;
  onSettings: () => void;
  onHelp: () => void;
}

export function 顶部栏({ 知识库, 模型, on知识库Change, on模型Change, onSettings, onHelp }: 顶部栏Props) {
  return (
    <div className="h-12 bg-background border-b border-border flex items-center justify-between px-6">
      {/* 左侧品牌标识 */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
          <span className="text-white text-sm font-medium">RAG</span>
        </div>
        <h1 className="text-foreground">多模态 RAG 工作台</h1>
      </div>

      {/* 中间下拉选择 */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">知识库</label>
          <Select value={知识库} onValueChange={on知识库Change}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">默认知识库</SelectItem>
              <SelectItem value="tech">技术文档</SelectItem>
              <SelectItem value="legal">法律条文</SelectItem>
              <SelectItem value="medical">医学资料</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">模型</label>
          <Select value={模型} onValueChange={on模型Change}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gpt-4">GPT-4</SelectItem>
              <SelectItem value="claude">Claude 3.5</SelectItem>
              <SelectItem value="gemini">Gemini Pro</SelectItem>
              <SelectItem value="qwen">通义千问</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 右侧图标按钮 */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onSettings}
          className="w-8 h-8 p-0 hover:bg-accent"
        >
          <Settings className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onHelp}
          className="w-8 h-8 p-0 hover:bg-accent"
        >
          <HelpCircle className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}