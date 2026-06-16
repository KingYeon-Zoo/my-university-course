"""
实验2-题目1：输出二维矩阵的四周中出现次数最多的元素
如果次数相同，按数值从大到小的次序依次输出
"""

def get_boundary_elements(matrix, n):
    """
    获取矩阵边界的所有元素
    边界包括：第一行、最后一行、第一列、最后一列
    """
    boundary = []
    
    if n == 0:
        return boundary
    
    # 第一行
    for j in range(n):
        boundary.append(matrix[0][j])
    
    # 最后一行（如果不是第一行）
    if n > 1:
        for j in range(n):
            boundary.append(matrix[n-1][j])
    
    # 第一列（排除已添加的第一行和最后一行的元素）
    for i in range(1, n-1):
        boundary.append(matrix[i][0])
    
    # 最后一列（排除已添加的第一行和最后一行的元素）
    if n > 1:
        for i in range(1, n-1):
            boundary.append(matrix[i][n-1])
    
    return boundary


def find_most_frequent(boundary):
    """
    找出边界中出现次数最多的元素
    如果有多个元素出现次数相同，按数值从大到小排序
    """
    # 统计每个元素的出现次数
    frequency = {}
    for num in boundary:
        frequency[num] = frequency.get(num, 0) + 1
    
    # 找出最大出现次数
    max_count = max(frequency.values())
    
    # 找出所有出现次数等于最大次数的元素
    result = []
    for num, count in frequency.items():
        if count == max_count:
            result.append(num)
    
    # 按数值从大到小排序
    result.sort(reverse=True)
    
    return result


def main():
    # 读取矩阵维度
    n = int(input())
    
    # 读取矩阵
    matrix = []
    for i in range(n):
        row = list(map(int, input().split()))
        matrix.append(row)
    
    # 获取边界元素
    boundary = get_boundary_elements(matrix, n)
    
    # 找出出现次数最多的元素
    result = find_most_frequent(boundary)
    
    # 输出结果
    print(' '.join(map(str, result)))


if __name__ == "__main__":
    main()

