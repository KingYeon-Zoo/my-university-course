def f(s1, s2):
    is_over = lambda str1, str2, pos: str1.endswith(str2[:pos])
    concat = lambda str1, str2, len: str1 + str2[overlap_len:]
    
    max_len = min(len(s1), len(s2))
    overlap_len = 0
    
    for i in range(1, max_len + 1):
        if is_over(s1, s2, i):
            overlap_len = i
            
    result = concat(s1, s2, overlap_len)
    return result


s1 = input("请输入字符串1：")
s2 = input("请输入字符串2：")

result = f(s1, s2)
print(f"字符串1: {s1}")
print(f"字符串2: {s2}")
print(f"连接结果: {result}")
