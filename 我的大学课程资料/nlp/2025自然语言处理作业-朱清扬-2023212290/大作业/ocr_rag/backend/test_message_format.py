"""
独立测试脚本 - 验证消息格式逻辑
不需要完整的依赖
"""

def validate_text_block(block):
    """验证文本块格式"""
    if not isinstance(block, dict):
        return False, "块不是字典"
    
    if block.get("type") != "text":
        return False, f"类型错误: {block.get('type')}"
    
    if "text" not in block:
        return False, "缺少text字段"
    
    if not isinstance(block["text"], str):
        return False, f"text不是字符串: {type(block['text'])}"
    
    if not block["text"].strip():
        return False, "text是空字符串"
    
    return True, "OK"

def validate_image_block(block):
    """验证图片块格式"""
    if not isinstance(block, dict):
        return False, "块不是字典"
    
    if block.get("type") != "image_url":
        return False, f"类型错误: {block.get('type')}"
    
    if "image_url" not in block:
        return False, "缺少image_url字段"
    
    if not isinstance(block["image_url"], dict):
        return False, "image_url不是字典"
    
    if "url" not in block["image_url"]:
        return False, "缺少url字段"
    
    url = block["image_url"]["url"]
    if not url.startswith("data:image"):
        return False, f"URL格式错误: {url[:30]}"
    
    return True, "OK"

def test_message_formats():
    """测试各种消息格式"""
    
    print("=" * 60)
    print("消息格式验证测试")
    print("=" * 60 + "\n")
    
    # 测试用例
    test_cases = [
        ("正确的文本块", {
            "type": "text",
            "text": "这是一段文本"
        }, validate_text_block, True),
        
        ("空文本块", {
            "type": "text",
            "text": ""
        }, validate_text_block, False),
        
        ("缺少text字段", {
            "type": "text"
        }, validate_text_block, False),
        
        ("正确的图片块", {
            "type": "image_url",
            "image_url": {
                "url": "data:image/png;base64,iVBORw0KGg"
            }
        }, validate_image_block, True),
        
        ("错误的图片URL", {
            "type": "image_url",
            "image_url": {
                "url": "http://example.com/image.png"
            }
        }, validate_image_block, False),
        
        ("缺少url字段", {
            "type": "image_url",
            "image_url": {}
        }, validate_image_block, False),
    ]
    
    passed = 0
    failed = 0
    
    for name, block, validator, should_pass in test_cases:
        is_valid, message = validator(block)
        
        if should_pass:
            if is_valid:
                print(f"[PASS] {name}: 通过")
                passed += 1
            else:
                print(f"[FAIL] {name}: 应该通过但失败了 - {message}")
                failed += 1
        else:
            if not is_valid:
                print(f"[PASS] {name}: 正确拒绝 - {message}")
                passed += 1
            else:
                print(f"[FAIL] {name}: 应该失败但通过了")
                failed += 1
    
    print(f"\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60 + "\n")
    
    return failed == 0

def test_content_filtering():
    """测试内容过滤逻辑"""
    
    print("=" * 60)
    print("内容过滤逻辑测试")
    print("=" * 60 + "\n")
    
    # 模拟过滤过程
    test_blocks = [
        {"type": "text", "text": "有效文本"},
        {"type": "text", "text": ""},  # 应该被过滤
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},  # 有效
        {"type": "image_url", "image_url": {"url": "http://example.com"}},  # 应该被过滤
        {"type": "text", "text": "另一段文本"},
    ]
    
    filtered = []
    for block in test_blocks:
        if block["type"] == "text":
            is_valid, _ = validate_text_block(block)
        elif block["type"] == "image_url":
            is_valid, _ = validate_image_block(block)
        else:
            is_valid = False
        
        if is_valid:
            filtered.append(block)
    
    print(f"原始块数: {len(test_blocks)}")
    print(f"过滤后块数: {len(filtered)}")
    print(f"预期块数: 3")
    
    if len(filtered) == 3:
        print("[PASS] 过滤逻辑正确")
        return True
    else:
        print(f"[FAIL] 过滤逻辑错误: 应该保留3个块,实际保留{len(filtered)}个")
        return False

if __name__ == "__main__":
    print("\n开始测试...\n")
    
    result1 = test_message_formats()
    print()
    result2 = test_content_filtering()
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print(">>> 所有测试通过!")
        print("修复的消息格式验证逻辑运行正常")
    else:
        print(">>> 部分测试失败")
        print("需要检查代码逻辑")
    print("=" * 60 + "\n")

