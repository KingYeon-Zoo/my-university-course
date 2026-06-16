"""
实验1-题目2：约瑟夫环
N个小朋友排成圆圈，从1开始报数，报到M的小朋友离开，求最后剩下的小朋友编号
"""

def josephus_circle(n, m):
    """
    使用列表模拟约瑟夫环
    n: 小朋友总数
    m: 报数到m的小朋友离开
    返回：最后剩下的小朋友编号
    """
    # 创建小朋友列表，编号从1到N
    children = list(range(1, n + 1))
    
    current_index = 0  # 当前报数起始位置
    
    # 当列表中还有多个小朋友时继续
    while len(children) > 1:
        # 计算要离开的小朋友的索引
        # (current_index + m - 1) % len(children)
        # m-1是因为从当前位置开始数，数到第m个
        leave_index = (current_index + m - 1) % len(children)
        
        # 移除这个小朋友
        children.pop(leave_index)
        
        # 更新下一次报数的起始位置
        # 如果删除的是最后一个元素，下一次从0开始
        # 否则从删除位置开始
        current_index = leave_index % len(children) if children else 0
    
    # 返回最后剩下的小朋友编号
    return children[0]


def josephus_formula(n, m):
    """
    使用数学公式求解约瑟夫环问题（更高效）
    递推公式：f(n, m) = (f(n-1, m) + m) % n
    f(1, m) = 0（编号从0开始）
    """
    result = 0
    for i in range(2, n + 1):
        result = (result + m) % i
    
    # 因为题目编号从1开始，所以加1
    return result + 1


def main():
    # 读取输入
    n, m = map(int, input().split())
    
    # 使用模拟方法求解
    result = josephus_circle(n, m)
    print(result)
    
    # 也可以使用数学公式求解（更快）
    # result = josephus_formula(n, m)
    # print(result)


if __name__ == "__main__":
    main()

