#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置设置
请在使用前设置你的 API Key
"""

import os
import sys
from dotenv import load_dotenv

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv(override=True)

def setup_environment():
    """设置环境变量"""
    
    # 生成模型配置（Qwen）
    if not os.getenv("OPENAI_API_KEY"):
        print("[WARNING] 请设置你的 OPENAI_API_KEY (Qwen模型API Key)")
        print("[INFO] 在 .env 文件中设置: OPENAI_API_KEY=your_actual_api_key")
        print("[INFO] 或在系统环境变量中设置")
    
    if not os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = "https://fanyi.963312.xyz/v1"
    
    # 语音识别模型配置（阿里云 Qwen3-ASR）
    if not os.getenv("ASR_API_KEY"):
        print("[WARNING] 请设置你的 ASR_API_KEY (阿里云语音识别API Key)")
        print("[INFO] 在 .env 文件中设置: ASR_API_KEY=your_actual_api_key")
    
    if not os.getenv("ASR_BASE_URL"):
        os.environ["ASR_BASE_URL"] = "https://dashscope.aliyuncs.com/api/v1"
    
    if not os.getenv("ASR_MODEL"):
        os.environ["ASR_MODEL"] = "qwen3-asr-flash"
    
    # 服务器配置
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "8000"
    os.environ["DEBUG"] = "True"
    
    # 日志配置
    os.environ["LOG_LEVEL"] = "INFO"
    
    # 模型配置
    os.environ["DEFAULT_MODEL"] = "qwen-3-235b-a22b-thinking-2507"
    os.environ["MAX_TOKENS"] = "2048"
    os.environ["TEMPERATURE"] = "0.7"
    
    # OCR配置 - Tesseract
    tessdata_path = r"C:\ProgramData\anaconda3\envs\rag\share\tessdata"
    os.environ["TESSDATA_PREFIX"] = tessdata_path
    print(f"[OK] TESSDATA_PREFIX 已设置: {tessdata_path}")

if __name__ == "__main__":
    setup_environment()
    print("[OK] 环境变量设置完成")
    print("[INFO] 请在 .env 文件中配置以下API Key:")
    print("   - OPENAI_API_KEY (Qwen生成模型)")
    print("   - ASR_API_KEY (阿里云语音识别)") 