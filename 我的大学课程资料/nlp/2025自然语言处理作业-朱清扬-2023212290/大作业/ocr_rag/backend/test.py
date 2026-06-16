import time
from openai import OpenAI


def call_openai_api(prompt):
   
    client = OpenAI(
        api_key='sk-WS55wBt8PAWacZUZurDsl9etlcDIvUQaGeTdRKVk8IrdPL0P',
        base_url='https://fanyi.963312.xyz/v1'
    )

    attempt = 0
    while True:
        try:
            attempt += 1
            print(f"[{attempt}] 发送API请求...")
            
            # 发送请求并同步等待响应（阻塞式调用）
            response = client.chat.completions.create(
                model="qwen-3-235b-a22b-thinking-2507",
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.2,
            )
            
            content = response.choices[0].message.content
            if content and content.strip():
                print(f"[{attempt}] ✓ 成功收到响应，等待2秒后继续...")
                time.sleep(2)  # 收到响应后再等待，确保严格串行
                return content
            else:
                print(f"[{attempt}] API returned empty content, retrying...")
                time.sleep(2)  # 重试前等待
        except Exception as e:
            print(f"[{attempt}] API call failed, retry. Error: {e}")
            time.sleep(2)  # 失败后等待再重试
            
            
if __name__ == '__main__':
    prompt = """
    你是谁，具体型号
    """
    print(call_openai_api(prompt))