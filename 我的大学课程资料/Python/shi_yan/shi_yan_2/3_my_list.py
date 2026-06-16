import random
import string

def generate_sorted_list(n, m):
    my_list = [
        [
        ''.join(random.choices(string.ascii_letters + string.digits, 
                                k=random.randint(1, m))) 
        ]
        for _ in range(n)
    ]
    
    sorted_list = sorted(my_list, 
                        key=lambda x: len(x[0]),
                        reverse=True)
    
    return sorted_list

def print_sorted_list(my_list):
    for i, sublist in enumerate(my_list, 1):
        print(f"第{i}个子列表（最长字符串长度：{max(len(s) for s in sublist)}）：")
        print(sublist)

n = int(input("请输入外层列表的元素个数n："))
m = int(input("请输入嵌套的字符串的最大长度m："))

result = generate_sorted_list(n, m)
print("\n按照字符串长度降序排序后的结果：")
print_sorted_list(result) 