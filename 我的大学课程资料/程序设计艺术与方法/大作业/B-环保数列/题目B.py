"""
题目B: 环保数列
问题描述：
    神奇数定义：如果一个正整数n可以被表示成 a² - b² = n (a, b均为正整数)
    找到神奇数列第x项的值
    
数学原理：
    a² - b² = (a+b)(a-b) = n
    令 p = a+b, q = a-b，则 pq = n
    要使 a = (p+q)/2, b = (p-q)/2 都是正整数：
    1. p + q 必须是偶数（p、q同奇偶）
    2. p > q > 0
    
    能表示成神奇数的充要条件：
    - 所有奇数（≥3）都可以（n = n×1，其中n和1都是奇数）
    - 4的倍数（≥8）都可以（n = 4k，k≥2，可分解为2k×2，都是偶数）
    - 形如 4k+2 的数不可以（只能分解为(4k+2)×1，奇偶性不同）
    - 1, 2, 4 不可以（特殊情况）
    
    因此神奇数列 = {3, 5, 7, 8, 9, 11, 12, 13, 15, 16, ...}
    排除的数 = {1, 2, 4, 6, 10, 14, 18, 22, ...} = {1, 2, 4} ∪ {4k+2 | k≥1}
"""

def is_magic(n):
    """
    判断n是否为神奇数
    """
    if n <= 2:
        return False
    # 排除 4k+2 形式的数
    if n % 4 == 2:
        return False
    return True

def count_magic_numbers_up_to(n):
    """
    计算不大于n的神奇数个数
    """
    if n < 3:
        return 0
    
    # 总数减去非神奇数
    # 非神奇数包括: 1, 2, 4, 以及所有 4k+2 形式的数
    # 4k+2 形式的数：6, 10, 14, 18, ...
    # 在[1, n]范围内，4k+2形式的数有多少个？
    # 这些数是 6, 10, 14, ..., 即 4k+2，其中k从1开始
    # 最大的k使得 4k+2 <= n，即 k <= (n-2)/4
    
    count_4k_plus_2 = (n - 2) // 4
    
    # 去掉1, 2, 4和所有4k+2的数
    # 需要额外判断4是否在范围内
    magic_count = n - 2 - count_4k_plus_2
    if n >= 4:
        magic_count -= 1  # 减去4
    
    return magic_count

def find_kth_magic(k):
    """
    找到第k个神奇数
    使用二分查找
    """
    left, right = 1, k * 3  # 上界设置为k*3足够大
    
    while left < right:
        mid = (left + right) // 2
        if count_magic_numbers_up_to(mid) < k:
            left = mid + 1
        else:
            right = mid
    
    return left

def solve():
    """
    主求解函数
    """
    T = int(input())
    for _ in range(T):
        x = int(input())
        result = find_kth_magic(x)
        print(result)

if __name__ == "__main__":
    solve()

