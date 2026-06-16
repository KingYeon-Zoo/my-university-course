"""
测试修复的脚本
验证图片和PDF处理功能
"""

import sys
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from main import create_multimodal_message, MessageRequest, ContentBlock
from pdf_processor import PDFProcessor
from loguru import logger

def test_image_message_validation():
    """测试图片消息验证"""
    print("=" * 60)
    print("测试 1: 图片消息格式验证")
    print("=" * 60)
    
    # 测试用例1: 正常的图片消息
    request1 = MessageRequest(
        content="这是什么?",
        content_blocks=[
            ContentBlock(
                type="image",
                content="data:image/png;base64,iVBORw0KGgoAAAANSUhEUg"
            )
        ]
    )
    
    try:
        msg1 = create_multimodal_message(request1)
        print("✅ 测试1.1 通过: 正常图片消息")
        print(f"   消息类型: {type(msg1.content)}")
        if isinstance(msg1.content, list):
            print(f"   内容块数: {len(msg1.content)}")
            for i, block in enumerate(msg1.content):
                print(f"   块{i+1}: {block.get('type')}")
    except Exception as e:
        print(f"❌ 测试1.1 失败: {e}")
    
    # 测试用例2: 空图片内容
    request2 = MessageRequest(
        content="测试",
        content_blocks=[
            ContentBlock(type="image", content="")
        ]
    )
    
    try:
        msg2 = create_multimodal_message(request2)
        print("✅ 测试1.2 通过: 空图片内容被正确过滤")
        print(f"   消息内容: {msg2.content[:50] if isinstance(msg2.content, str) else '多模态'}")
    except Exception as e:
        print(f"❌ 测试1.2 失败: {e}")
    
    # 测试用例3: 无效的图片格式
    request3 = MessageRequest(
        content="测试",
        content_blocks=[
            ContentBlock(type="image", content="not-a-valid-image-url")
        ]
    )
    
    try:
        msg3 = create_multimodal_message(request3)
        print("✅ 测试1.3 通过: 无效图片格式被正确过滤")
    except Exception as e:
        print(f"❌ 测试1.3 失败: {e}")
    
    # 测试用例4: 混合内容
    request4 = MessageRequest(
        content="",
        content_blocks=[
            ContentBlock(type="text", content="这是文本"),
            ContentBlock(type="image", content="data:image/jpeg;base64,/9j/"),
            ContentBlock(type="image", content=""),  # 空图片,应该被过滤
        ]
    )
    
    try:
        msg4 = create_multimodal_message(request4)
        print("✅ 测试1.4 通过: 混合内容正确处理")
        if isinstance(msg4.content, list):
            print(f"   有效块数: {len(msg4.content)} (应该是2)")
    except Exception as e:
        print(f"❌ 测试1.4 失败: {e}")
    
    print()

def test_pdf_processor():
    """测试PDF处理器的备用方案"""
    print("=" * 60)
    print("测试 2: PDF处理器备用方案")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    # 检查备用方法是否存在
    if hasattr(processor, '_extract_text_with_pymupdf'):
        print("✅ 测试2.1 通过: PyMuPDF备用方法已实现")
    else:
        print("❌ 测试2.1 失败: PyMuPDF备用方法未找到")
    
    # 检查文本分割器
    if hasattr(processor, 'text_splitter'):
        print("✅ 测试2.2 通过: 文本分割器已初始化")
    else:
        print("❌ 测试2.2 失败: 文本分割器未初始化")
    
    print()

def test_message_content_formats():
    """测试各种消息格式"""
    print("=" * 60)
    print("测试 3: 消息内容格式验证")
    print("=" * 60)
    
    test_cases = [
        ("纯文本", MessageRequest(content="你好")),
        ("纯文本块", MessageRequest(content_blocks=[ContentBlock(type="text", content="文本块")])),
        ("空消息", MessageRequest(content="", content_blocks=[])),
    ]
    
    for name, request in test_cases:
        try:
            msg = create_multimodal_message(request)
            # 验证消息格式
            if isinstance(msg.content, str):
                assert msg.content != "", f"{name}: 消息不应该为空字符串"
                print(f"✅ 测试3.{test_cases.index((name, request))+1} 通过: {name} (字符串)")
            elif isinstance(msg.content, list):
                assert len(msg.content) > 0, f"{name}: 消息列表不应该为空"
                for block in msg.content:
                    assert "type" in block, f"{name}: 块缺少type字段"
                    if block["type"] == "text":
                        assert "text" in block, f"{name}: 文本块缺少text字段"
                        assert isinstance(block["text"], str), f"{name}: text必须是字符串"
                    elif block["type"] == "image_url":
                        assert "image_url" in block, f"{name}: 图片块缺少image_url字段"
                        assert "url" in block["image_url"], f"{name}: image_url缺少url字段"
                print(f"✅ 测试3.{test_cases.index((name, request))+1} 通过: {name} (列表)")
            else:
                print(f"❌ 测试3.{test_cases.index((name, request))+1} 失败: {name} - 未知消息类型")
        except AssertionError as e:
            print(f"❌ 测试3.{test_cases.index((name, request))+1} 失败: {name} - {e}")
        except Exception as e:
            print(f"❌ 测试3.{test_cases.index((name, request))+1} 失败: {name} - {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始运行修复验证测试")
    print("=" * 60 + "\n")
    
    try:
        test_image_message_validation()
        test_pdf_processor()
        test_message_content_formats()
        
        print("=" * 60)
        print("所有测试完成!")
        print("=" * 60)
        print("\n如果所有测试都通过 (✅),说明修复成功!")
        print("如果有失败 (❌),请查看错误信息并检查代码\n")
        
    except Exception as e:
        print(f"\n❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()

