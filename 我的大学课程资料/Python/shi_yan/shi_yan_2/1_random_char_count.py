import random
import string
from collections import Counter

def method1():
    chars = string.ascii_letters + string.digits
    random_string = ''
    for _ in range(1000):
        random_string += chars[random.randint(0, len(chars)-1)]

    char_count = {}
    for char in random_string:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1
    
    print("方法1结果：")
    for char, count in sorted(char_count.items()):
        print(f"字符 '{char}' 出现了 {count} 次")

def method2():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=1000))
    char_count = Counter(random_string)
    print("\n方法2结果：")
    for char, count in sorted(char_count.items()):
        print(f"字符 '{char}' 出现了 {count} 次")

print("生成1000个随机字符并统计每个字符出现的次数：")
method1()
method2() 