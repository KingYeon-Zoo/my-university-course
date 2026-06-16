import random

def list_operations(original_list):
    new_list = original_list[:]

    reversed_list = original_list[::-1]
    
    even_position_list = original_list[1::2]
    
    return new_list, reversed_list, even_position_list

def print_results(original, new, reversed_list, even_positions):
    print(f"原始列表：{original}")
    print(f"新列表（复制）：{new}")
    print(f"逆序列表：{reversed_list}")
    print(f"偶数位置元素列表：{even_positions}")

size = int(input("请输入要生成的列表大小："))
my_list = [random.randint(1, 100) for _ in range(size)]

new_list, reversed_list, even_position_list = list_operations(my_list)

print_results(my_list, new_list, reversed_list, even_position_list) 