# Graphviz 智能路径检测器
import os
import shutil
from typing import Optional, Dict, List
from config import GRAPHVIZ_CONFIG

class GraphvizDetector:
    """智能检测 Graphviz 安装位置"""
    
    def __init__(self):
        self.graphviz_path: Optional[str] = None
        self.executables: Dict[str, str] = {}
        
    def detect_graphviz(self) -> bool:
        """
        检测 Graphviz 是否可用
        返回: True 如果检测到 Graphviz，False 否则
        """
        
        # 方法 1: 检查系统 PATH
        if self._check_system_path():
            print("✅ 在系统 PATH 中找到 Graphviz")
            return True
        
        # 方法 2: 检查环境变量
        if self._check_environment_variable():
            print(f"✅ 通过环境变量找到 Graphviz: {self.graphviz_path}")
            return True
        
        # 方法 3: 检查常见安装位置
        if self._check_common_paths():
            print(f"✅ 在常见位置找到 Graphviz: {self.graphviz_path}")
            return True
        
        print("❌ 未能检测到 Graphviz 安装")
        return False
    
    def _check_system_path(self) -> bool:
        """检查系统 PATH 中是否有 Graphviz"""
        
        for exe in GRAPHVIZ_CONFIG['executables']:
            exe_path = shutil.which(exe)
            if exe_path:
                self.graphviz_path = os.path.dirname(exe_path)
                self.executables[exe] = exe_path
                return True
        
        return False
    
    def _check_environment_variable(self) -> bool:
        """检查环境变量中是否配置了 Graphviz 路径"""
        
        env_var = GRAPHVIZ_CONFIG['env_var']
        if env_var in os.environ:
            env_path = os.environ[env_var]
            if os.path.isfile(env_path):
                # 环境变量指向具体的可执行文件
                self.graphviz_path = os.path.dirname(env_path)
                return self._validate_path(self.graphviz_path)
            elif os.path.isdir(env_path):
                # 环境变量指向目录
                self.graphviz_path = env_path
                return self._validate_path(self.graphviz_path)
        
        return False
    
    def _check_common_paths(self) -> bool:
        """检查常见的 Graphviz 安装位置"""
        
        for path in GRAPHVIZ_CONFIG['common_paths']:
            if self._validate_path(path):
                self.graphviz_path = path
                return True
        
        return False
    
    def _validate_path(self, path: str) -> bool:
        """验证指定路径是否包含有效的 Graphviz 安装"""
        
        if not os.path.isdir(path):
            return False
        
        # 检查是否存在必要的可执行文件
        found_executables = {}
        for exe in GRAPHVIZ_CONFIG['executables']:
            exe_path = os.path.join(path, exe)
            if os.path.isfile(exe_path):
                found_executables[exe] = exe_path
        
        # 至少需要 dot.exe 可执行文件
        if 'dot.exe' in found_executables:
            self.executables = found_executables
            return True
        
        return False
    
    def get_executable_path(self, name: str) -> Optional[str]:
        """
        获取指定可执行文件的完整路径
        
        Args:
            name: 可执行文件名，如 'dot', 'neato', 'fdp', 'circo'
            
        Returns:
            完整路径或 None
        """
        
        exe_name = f"{name}.exe"
        return self.executables.get(exe_name)
    
    def get_all_executables(self) -> Dict[str, str]:
        """获取所有检测到的可执行文件路径"""
        return self.executables.copy()
    
    def get_graphviz_directory(self) -> Optional[str]:
        """获取 Graphviz 安装目录"""
        return self.graphviz_path

def test_detection():
    """测试 Graphviz 检测功能"""
    
    print("开始测试 Graphviz 检测...")
    
    detector = GraphvizDetector()
    
    if detector.detect_graphviz():
        print(f"Graphviz 目录: {detector.get_graphviz_directory()}")
        print("可用的可执行文件:")
        for exe, path in detector.get_all_executables().items():
            print(f"  {exe}: {path}")
        
        # 测试 dot 程序
        try:
            dot_path = detector.get_executable_path('dot')
            if dot_path:
                print(f"\n测试 dot 程序: {dot_path}")
                import subprocess
                result = subprocess.run([dot_path, '-V'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ dot 程序工作正常")
                    print(f"版本信息: {result.stderr.strip()}")
                else:
                    print(f"❌ dot 程序测试失败: {result.stderr}")
            
        except Exception as e:
            print(f"❌ 测试 dot 程序时出错: {e}")
    
    else:
        print("❌ 未检测到 Graphviz")
        print("\n建议的解决方案:")
        print("1. 检查 Graphviz 是否已正确安装")
        print("2. 将 Graphviz bin 目录添加到系统 PATH")
        print("3. 设置环境变量 GRAPHVIZ_DOT 指向 dot.exe")

if __name__ == "__main__":
    test_detection() 