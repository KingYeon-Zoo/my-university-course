import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, AlertCircle, Info, XCircle } from "lucide-react";
import { cn } from "./ui/utils";

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
}

interface 轻提示Props {
  message: ToastMessage | null;
  onClose: () => void;
}

export function 轻提示({ message, onClose }: 轻提示Props) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (message) {
      setIsVisible(true);
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // 等待动画完成后关闭
      }, message.duration || 3000);

      return () => clearTimeout(timer);
    }
  }, [message, onClose]);

  if (!message) return null;

  const getIcon = () => {
    switch (message.type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'info': return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getBorderColor = () => {
    switch (message.type) {
      case 'success': return 'border-green-200';
      case 'error': return 'border-red-200';
      case 'warning': return 'border-yellow-200';
      case 'info': return 'border-blue-200';
    }
  };

  const getBackgroundColor = () => {
    switch (message.type) {
      case 'success': return 'bg-green-50';
      case 'error': return 'bg-red-50';
      case 'warning': return 'bg-yellow-50';
      case 'info': return 'bg-blue-50';
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.95 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="fixed top-20 right-6 z-[100] max-w-sm"
        >
          <div className={cn(
            "p-4 rounded-lg border shadow-lg backdrop-blur-sm",
            getBorderColor(),
            getBackgroundColor()
          )}>
            <div className="flex items-start gap-3">
              {getIcon()}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm">{message.title}</h4>
                {message.description && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {message.description}
                  </p>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}