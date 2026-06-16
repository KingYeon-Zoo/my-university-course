"""
实验3-题目1：序列操作
支持在序列尾部插入元素，以及查询以某位置为端点、和为x的子段个数
"""

def count_subsequences(sequence, i, x):
    """
    查询以i为左/右端点，和为x的子段个数
    i: 端点位置（1-based）
    x: 目标和
    返回：子段个数
    """
    n = len(sequence)
    count = 0
    
    # 情况1：i为左端点，向右扩展
    current_sum = 0
    for j in range(i - 1, n):  # i-1是0-based索引
        current_sum += sequence[j]
        if current_sum == x:
            count += 1
    
    # 情况2：i为右端点，向左扩展
    current_sum = 0
    for j in range(i - 1, -1, -1):  # 从i-1向左
        current_sum += sequence[j]
        if current_sum == x:
            count += 1
    
    # 注意：i作为单独子段（只有一个元素）的情况被计算了两次
    # 需要减去重复的情况
    if sequence[i - 1] == x:
        count -= 1
    
    return count


def main():
    n = int(input())
    sequence = []
    
    for _ in range(n):
        operation = list(map(int, input().split()))
        
        if operation[0] == 1:
            # 插入操作
            x = operation[1]
            sequence.append(x)
        elif operation[0] == 2:
            # 查询操作
            i = operation[1]
            x = operation[2]
            result = count_subsequences(sequence, i, x)
            print(result)


if __name__ == "__main__":
    main()

