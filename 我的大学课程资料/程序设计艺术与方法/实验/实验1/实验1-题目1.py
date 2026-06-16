"""
实验1-题目1：查询数据
使用可重复集合实现插入、删除和查询最接近元素的功能
"""

def find_closest(data_set, x):
    """查找集合中与x相差最小的元素"""
    if not data_set:
        return None
    
    sorted_list = sorted(data_set)
    n = len(sorted_list)
    
    # 二分查找插入位置
    left, right = 0, n - 1
    
    # 如果x小于最小值，返回最小值
    if x <= sorted_list[0]:
        return sorted_list[0]
    # 如果x大于最大值，返回最大值
    if x >= sorted_list[-1]:
        return sorted_list[-1]
    
    # 二分查找最接近的值
    while left < right:
        mid = (left + right) // 2
        if sorted_list[mid] < x:
            left = mid + 1
        else:
            right = mid
    
    # 比较left和left-1位置的值，找出最接近的
    candidates = []
    if left > 0:
        candidates.append(sorted_list[left - 1])
    if left < n:
        candidates.append(sorted_list[left])
    
    # 返回差值最小的元素
    min_diff = float('inf')
    result = None
    for candidate in candidates:
        diff = abs(candidate - x)
        if diff < min_diff:
            min_diff = diff
            result = candidate
    
    return result


def main():
    n = int(input())
    data_set = []  # 使用列表模拟可重复集合
    
    for _ in range(n):
        operation = list(map(int, input().split()))
        op_type = operation[0]
        x = operation[1]
        
        if op_type == 1:  # 插入元素
            data_set.append(x)
        elif op_type == 2:  # 删除元素
            if x in data_set:
                data_set.remove(x)
        elif op_type == 3:  # 查询最接近的元素
            closest = find_closest(data_set, x)
            print(closest)


if __name__ == "__main__":
    main()

