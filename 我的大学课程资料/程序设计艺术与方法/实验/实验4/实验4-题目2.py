"""
实验4-题目2：买蛋糕
找到k个连续蛋糕，使得最高和第二高的差值最小
"""

def find_min_difference(n, k, heights):
    """
    滑动窗口找到最小差值
    """
    if k == 1:
        return 0
    
    min_diff = float('inf')
    
    # 滑动窗口：遍历所有长度为k的连续子数组
    for i in range(n - k + 1):
        # 取出当前窗口
        window = heights[i:i+k]
        
        # 排序找到最大和第二大
        window_sorted = sorted(window, reverse=True)
        
        # 计算差值
        diff = window_sorted[0] - window_sorted[1]
        
        # 更新最小差值
        min_diff = min(min_diff, diff)
    
    return min_diff


def main():
    # 读取n和k
    n, k = map(int, input().split())
    
    # 读取蛋糕高度
    heights = list(map(int, input().split()))
    
    # 计算最小差值
    result = find_min_difference(n, k, heights)
    
    # 输出结果
    print(result)


if __name__ == "__main__":
    main()

