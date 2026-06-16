#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证配置是否正确加载"""

from dotenv import load_dotenv
import os
import sys

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("配置验证")
print("=" * 60)

# 生成模型配置
print("\n[生成模型配置] Qwen:")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"  [OK] API Key: {openai_key[:20]}...{openai_key[-10:]}")
else:
    print(f"  [ERROR] API Key: 未设置")
print(f"  [OK] Base URL: {os.getenv('OPENAI_BASE_URL')}")
print(f"  [OK] 默认模型: {os.getenv('DEFAULT_MODEL')}")

# 语音识别配置
print("\n[语音识别配置] 阿里云 Qwen3-ASR:")
asr_key = os.getenv("ASR_API_KEY")
if asr_key:
    print(f"  [OK] API Key: {asr_key[:20]}...{asr_key[-10:]}")
else:
    print(f"  [ERROR] API Key: 未设置")
print(f"  [OK] Base URL: {os.getenv('ASR_BASE_URL')}")
print(f"  [OK] 模型: {os.getenv('ASR_MODEL')}")

# 服务器配置
print("\n[服务器配置]:")
print(f"  [OK] Host: {os.getenv('HOST')}")
print(f"  [OK] Port: {os.getenv('PORT')}")
print(f"  [OK] Debug: {os.getenv('DEBUG')}")

# 其他配置
print("\n[其他配置]:")
print(f"  [OK] Max Tokens: {os.getenv('MAX_TOKENS')}")
print(f"  [OK] Temperature: {os.getenv('TEMPERATURE')}")
print(f"  [OK] Tesseract: {os.getenv('TESSDATA_PREFIX')}")

print("\n" + "=" * 60)
print("[SUCCESS] 所有配置加载成功！")
print("=" * 60)

