import { useState } from "react";
import { Button } from "./ui/button";
import { ScrollArea } from "./ui/scroll-area";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { 
  MessageSquare, 
  FileText, 
  Image, 
  Mic, 
  History,
  Settings,
  HelpCircle,
  Plus,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Brain,
  Zap
} from "lucide-react";
import { cn } from "./ui/utils";

interface ConversationItem {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
}

interface 侧边栏Props {
  isCollapsed: boolean;
  onToggle: () => void;
  conversations: ConversationItem[];
  activeConversationId?: string;
  onConversationSelect: (id: string) => void;
  onNewConversation: () => void;
  onSettings: () => void;
  onHelp: () => void;
}

export function 侧边栏({
  isCollapsed,
  onToggle,
  conversations,
  activeConversationId,
  onConversationSelect,
  onNewConversation,
  onSettings,
  onHelp
}: 侧边栏Props) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const menuItems = [
    {
      id: 'knowledge',
      icon: BookOpen,
      label: '知识库管理',
      badge: '3',
      color: 'text-blue-500'
    },
    {
      id: 'models',
      icon: Brain,
      label: '模型配置',
      badge: null,
      color: 'text-purple-500'
    },
    {
      id: 'analysis',
      icon: Zap,
      label: '性能分析',
      badge: 'New',
      color: 'text-orange-500'
    }
  ];

  return (
    <div className={cn(
      "h-full bg-sidebar/95 backdrop-blur-lg border-r border-sidebar-border/50 flex flex-col transition-all duration-300 relative z-40",
      isCollapsed ? "w-16" : "w-80"
    )}>
      {/* 折叠按钮 */}
      <div className="absolute -right-3 top-6 z-50">
        <Button
          variant="outline"
          size="sm"
          onClick={onToggle}
          className="w-6 h-6 p-0 rounded-full bg-background shadow-lg border-border/50 hover:shadow-xl transition-all duration-200"
        >
          {isCollapsed ? (
            <ChevronRight className="w-3 h-3" />
          ) : (
            <ChevronLeft className="w-3 h-3" />
          )}
        </Button>
      </div>

      {/* 侧边栏头部 */}
      <div className="p-4 border-b border-sidebar-border/50">
        <Button
          onClick={onNewConversation}
          className={cn(
            "w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-300",
            isCollapsed && "px-0"
          )}
        >
          <Plus className="w-4 h-4" />
          {!isCollapsed && <span className="ml-2">新建对话</span>}
        </Button>
      </div>

      {/* 功能菜单 */}
      {!isCollapsed && (
        <div className="p-4 space-y-2">
          <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
            功能模块
          </h3>
          {menuItems.map((item) => (
            <Button
              key={item.id}
              variant="ghost"
              className="w-full justify-start h-10 relative group"
              onMouseEnter={() => setHoveredItem(item.id)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <item.icon className={cn("w-4 h-4", item.color)} />
              <span className="ml-3 flex-1 text-left">{item.label}</span>
              {item.badge && (
                <Badge variant="secondary" className="ml-2 h-5 text-xs">
                  {item.badge}
                </Badge>
              )}
              {hoveredItem === item.id && (
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-md" />
              )}
            </Button>
          ))}
        </div>
      )}

      <Separator className="mx-4" />

      {/* 对话历史 */}
      <div className="flex-1 p-4">
        {!isCollapsed && (
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              对话历史
            </h3>
            <Badge variant="outline" className="h-5 text-xs">
              {conversations.length}
            </Badge>
          </div>
        )}
        
        <ScrollArea className="h-full">
          <div className="space-y-1">
            {conversations.map((conversation) => (
              <Button
                key={conversation.id}
                variant={activeConversationId === conversation.id ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start h-auto p-3 group relative overflow-hidden",
                  isCollapsed && "px-0 w-12 h-12",
                  activeConversationId === conversation.id && 
                  "bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-200/50"
                )}
                onClick={() => onConversationSelect(conversation.id)}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                {!isCollapsed && (
                  <div className="ml-3 flex-1 text-left min-w-0">
                    <div className="truncate text-sm">{conversation.title}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">
                        {conversation.messageCount} 条消息
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {conversation.timestamp.toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                )}
              </Button>
            ))}
            
            {conversations.length === 0 && !isCollapsed && (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">暂无对话记录</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* 底部操作 */}
      <div className="p-4 border-t border-sidebar-border/50 space-y-2">
        <Button
          variant="ghost"
          onClick={onSettings}
          className={cn(
            "w-full justify-start",
            isCollapsed && "px-0 w-12 h-12"
          )}
        >
          <Settings className="w-4 h-4" />
          {!isCollapsed && <span className="ml-3">设置</span>}
        </Button>
        
        <Button
          variant="ghost"
          onClick={onHelp}
          className={cn(
            "w-full justify-start",
            isCollapsed && "px-0 w-12 h-12"
          )}
        >
          <HelpCircle className="w-4 h-4" />
          {!isCollapsed && <span className="ml-3">帮助</span>}
        </Button>
      </div>
    </div>
  );
}