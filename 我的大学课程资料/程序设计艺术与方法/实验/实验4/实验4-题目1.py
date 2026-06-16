"""
实验4-题目1：重排数字
重新排列A得到新的数字C（不能有前导0），在C≤B的情况下，求C的最大值
"""

def find_max_arrangement(a_str, b):
    """
    找到A的重排列，使其小于等于B且最大
    """
    digits = list(a_str)
    n = len(digits)
    b_str = str(b)
    
    # 如果A和B位数不同
    if len(digits) > len(b_str):
        # A位数更多，无解（即使最小排列也大于B）
        return -1
    elif len(digits) < len(b_str):
        # A位数更少，直接排成最大值（降序）
        digits.sort(reverse=True)
        # 检查前导0
        if digits[0] == '0':
            return -1
        return int(''.join(digits))
    
    # 位数相同的情况，需要仔细处理
    # 尝试从高位到低位构造
    result = construct_max_valid(digits, b_str)
    
    if result is not None:
        return result
    
    # 如果无法构造相同位数的，尝试少一位
    if n > 1:
        # 排成最大值（降序）
        digits.sort(reverse=True)
        # 去掉最高位，重新排列剩余的
        # 但这样会改变位数，题目要求不能有前导0
        # 实际上如果无法构造，就返回-1
        pass
    
    return -1


def construct_max_valid(digits, target):
    """
    构造不超过target的最大排列
    使用贪心+回溯
    """
    from itertools import permutations
    
    # 生成所有排列
    all_perms = set([''.join(p) for p in permutations(digits)])
    
    # 过滤掉有前导0的
    valid_perms = [p for p in all_perms if p[0] != '0']
    
    # 转换为整数并过滤
    target_val = int(target)
    valid_nums = [int(p) for p in valid_perms if int(p) <= target_val]
    
    if not valid_nums:
        return None
    
    return max(valid_nums)


def main():
    a, b = map(int, input().split())
    
    result = find_max_arrangement(str(a), b)
    print(result)


if __name__ == "__main__":
    main()

