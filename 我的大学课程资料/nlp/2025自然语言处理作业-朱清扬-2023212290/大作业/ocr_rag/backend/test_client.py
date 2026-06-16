#!/usr/bin/env python3
"""
测试客户端 - 用于测试流式聊天接口
"""

import asyncio
import httpx
import json
from typing import AsyncGenerator

async def test_streaming_chat():
    """测试流式聊天接口"""
    print("🧪 测试流式聊天接口...")
    
    url = "http://localhost:8000/api/chat/stream"
    
    # 测试请求数据
    test_data = {
        "content": "你好！请介绍一下你的功能。",
        "history": [],
        "model": "gpt-4o",
        "knowledge_base": "default"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                json=test_data,
                headers={"Accept": "text/event-stream"}
            ) as response:
                
                print(f"状态码: {response.status_code}")
                print("=" * 50)
                print("📨 流式响应:")
                
                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # 移除 "data: " 前缀
                            
                            if data["type"] == "content_delta":
                                content = data["content"]
                                print(content, end="", flush=True)
                                full_content += content
                            elif data["type"] == "message_complete":
                                print("\n" + "=" * 50)
                                print(f"✅ 响应完成")
                                print(f"📄 完整内容长度: {len(data['full_content'])} 字符")
                                break
                            elif data["type"] == "error":
                                print(f"\n❌ 错误: {data['error']}")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                print(f"\n✅ 测试完成")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_sync_chat():
    """测试同步聊天接口"""
    print("\n🧪 测试同步聊天接口...")
    
    url = "http://localhost:8000/api/chat"
    
    test_data = {
        "content": "简单介绍一下LangChain",
        "history": [],
        "model": "gpt-4o",
        "knowledge_base": "default"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=test_data)
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("📨 同步响应:")
                print(f"角色: {result['role']}")
                print(f"时间: {result['timestamp']}")
                print(f"内容: {result['content']}")
                print("✅ 测试完成")
            else:
                print(f"❌ 响应错误: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_health():
    """测试健康检查接口"""
    print("🧪 测试健康检查接口...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("📊 服务状态:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
                print("✅ 服务运行正常")
            else:
                print(f"❌ 服务异常: {response.text}")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("💡 请确保后端服务正在运行: python start.py")

async def main():
    """主测试函数"""
    print("🚀 开始API接口测试")
    print("=" * 60)
    
    # 测试健康检查
    await test_health()
    
    # 测试同步接口
    await test_sync_chat()
    
    # 测试流式接口
    await test_streaming_chat()
    
    print("\n🎉 所有测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 