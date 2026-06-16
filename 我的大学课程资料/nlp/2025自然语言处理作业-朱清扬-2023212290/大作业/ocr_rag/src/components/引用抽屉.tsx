import { Sheet, SheetContent, SheetHeader, SheetTitle } from "./ui/sheet";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import { Button } from "./ui/button";
import { X } from "lucide-react";
import { Reference } from "./消息气泡";
import { cn } from "./ui/utils";

interface 引用抽屉Props {
  isOpen: boolean;
  onClose: () => void;
  references: Reference[];
  selectedReference?: Reference;
  onReferenceSelect: (reference: Reference) => void;
}

export function 引用抽屉({ 
  isOpen, 
  onClose, 
  references, 
  selectedReference, 
  onReferenceSelect 
}: 引用抽屉Props) {
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent 
        side="bottom" 
        className="h-[50vh] rounded-t-lg"
      >
        <SheetHeader className="flex flex-row items-center justify-between">
          <SheetTitle>引用来源</SheetTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="w-8 h-8 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        </SheetHeader>

        <div className="flex h-full mt-4 gap-4">
          {/* 左侧引用列表 */}
          <div className="w-1/2 border-r pr-4">
            <ScrollArea className="h-full">
              <div className="space-y-3">
                {references.map((ref, index) => (
                  <div
                    key={ref.id}
                    className={cn(
                      "p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md",
                      selectedReference?.id === ref.id 
                        ? "border-blue-500 bg-blue-50" 
                        : "hover:border-gray-300"
                    )}
                    onClick={() => onReferenceSelect(ref)}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm">[{ref.id}] {ref.source}</h4>
                          <Badge variant="outline" className="text-xs">
                          第 {ref.page} 页
                          </Badge>
                        </div>
                      <p className="text-xs text-muted-foreground overflow-hidden" style={{ 
                        display: '-webkit-box', 
                        WebkitLineClamp: 2, 
                        WebkitBoxOrient: 'vertical' 
                      }}>
                        {ref.text}
                      </p>
                      <div className="text-xs text-muted-foreground">
                        {ref.source_info}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* 右侧文本预览区域 */}
          <div className="w-1/2 pl-4">
            {selectedReference ? (
              <div className="h-full flex flex-col">
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="font-semibold">[{selectedReference.id}] {selectedReference.source}</h3>
                  <Badge>第 {selectedReference.page} 页</Badge>
                </div>
                
                <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-hidden">
                  <ScrollArea className="h-full">
                    <div className="space-y-3">
                      <div className="text-sm text-muted-foreground">
                        <strong>来源信息：</strong>{selectedReference.source_info}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <strong>文档块ID：</strong>{selectedReference.chunk_id}
                      </div>
                      <div className="border-t pt-3">
                        <div className="text-sm font-medium text-muted-foreground mb-2">文本内容：</div>
                        <div className="text-sm leading-relaxed whitespace-pre-wrap bg-white p-3 rounded border">
                          {selectedReference.text}
                        </div>
                      </div>
                    </div>
                  </ScrollArea>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                <p>点击左侧引用项查看文本内容</p>
              </div>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}