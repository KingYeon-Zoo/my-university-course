import { Button } from "./ui/button";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";

interface 导航栏Props {}

export function 导航栏({}: 导航栏Props) {
  const { theme, setTheme } = useTheme();
  
  return (
    <nav className="h-16 bg-background/95 backdrop-blur-lg border-b border-border flex items-center justify-end px-6 relative z-50">
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="w-9 h-9"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
      </div>
    </nav>
  );
}
