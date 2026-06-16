#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态 RAG 工作台后端启动脚本
"""

import os
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置环境变量
from env_config import setup_environment
setup_environment()

def check_environment():
    """检查环境配置"""
    print("[INFO] 检查环境配置...")
    
    # 检查 .env 文件
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("[WARNING] 未找到 .env 文件，使用默认配置")
        print("[INFO] 建议创建 .env 文件并配置 API Keys")
    
    # 检查 OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[WARNING] 未配置 OPENAI_API_KEY")
        print("[INFO] 请在 .env 文件中设置: OPENAI_API_KEY=your_api_key")
    else:
        print(f"[OK] Qwen API Key 已配置 (前6位: {api_key[:6]}...)")
    
    # 检查 ASR API Key
    asr_key = os.getenv("ASR_API_KEY")
    if asr_key:
        print(f"[OK] ASR API Key 已配置 (前6位: {asr_key[:6]}...)")
    else:
        print("[WARNING] 未配置 ASR_API_KEY")
    
    # 检查日志目录
    logs_dir = current_dir / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print(f"[OK] 创建日志目录: {logs_dir}")
    
    print("[OK] 环境检查完成\n")

def install_dependencies():
    """检查并安装依赖"""
    print("[INFO] 检查依赖包...")
    
    try:
        import fastapi
        import uvicorn
        import langchain
        print("[OK] 主要依赖包已安装")
    except ImportError as e:
        print(f"[ERROR] 缺少依赖包: {e}")
        print("[INFO] 请运行: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("启动多模态 RAG 工作台后端服务")
    print("=" * 60)
    
    # 检查环境
    check_environment()
    
    # 检查依赖
    if not install_dependencies():
        print("\n[ERROR] 依赖检查失败，请先安装依赖:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # 启动服务
    print("\n[INFO] 启动 FastAPI 服务...")
    print("[INFO] API 文档: http://localhost:8000/docs")
    print("[INFO] 流式聊天: http://localhost:8000/api/chat/stream")
    print("[INFO] 停止服务: Ctrl+C")
    print("-" * 60)
    
    try:
        # 使用 uvicorn 命令行方式启动，避免导入问题
        import subprocess
        
        cmd = [
            sys.executable, 
            "-m", "uvicorn", 
            "main:app",
            "--host", "localhost",
            "--port", "8000"
        ]
        
        print(f"[RUN] {' '.join(cmd)}\n")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n[INFO] 服务已停止")
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
        print("[INFO] 你也可以直接运行: python -m uvicorn main:app --host localhost --port 8000 --reload")
        sys.exit(1)

if __name__ == "__main__":
    main() 