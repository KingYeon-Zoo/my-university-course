"""
实验4-题目3：完美数列
找到最长的子序列，使得最大值 <= 最小值 × p
"""

def find_perfect_sequence(n, p, numbers):
    """
    找到最长的完美数列
    使用排序+双指针
    """
    # 排序数组
    numbers.sort()
    
    max_length = 0
    
    # 双指针：左指针固定最小值，右指针扩展
    for i in range(n):
        min_val = numbers[i]
        
        # 二分查找最远的合法右端点
        # 找到最大的j使得numbers[j] <= min_val * p
        left, right = i, n - 1
        result = i
        
        while left <= right:
            mid = (left + right) // 2
            if numbers[mid] <= min_val * p:
                result = mid
                left = mid + 1
            else:
                right = mid - 1
        
        # 更新最大长度
        length = result - i + 1
        max_length = max(max_length, length)
    
    return max_length


def main():
    # 读取N和p
    n, p = map(int, input().split())
    
    # 读取N个正整数
    numbers = list(map(int, input().split()))
    
    # 计算最长完美数列
    result = find_perfect_sequence(n, p, numbers)
    
    # 输出结果
    print(result)


if __name__ == "__main__":
    main()

