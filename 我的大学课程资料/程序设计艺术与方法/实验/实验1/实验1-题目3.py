"""
实验1-题目3：特殊质数（纯质数）
判断一个数是否为纯质数：本身是质数，且首位和末位也是质数
"""

def is_prime(n):
    """判断一个数是否为质数"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # 只需检查到sqrt(n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    
    return True


def is_pure_prime(n):
    """
    判断一个数是否为纯质数
    纯质数定义：本身是质数，且首位和末位也是质数
    """
    # 首先判断本身是否为质数
    if not is_prime(n):
        return False
    
    # 转换为字符串以便获取首位和末位
    num_str = str(n)
    
    # 获取首位和末位数字
    first_digit = int(num_str[0])
    last_digit = int(num_str[-1])
    
    # 判断首位和末位是否都是质数
    # 质数只能是：2, 3, 5, 7
    prime_digits = {2, 3, 5, 7}
    
    return first_digit in prime_digits and last_digit in prime_digits


def main():
    # 读取输入
    n = int(input())
    numbers = list(map(int, input().split()))
    
    # 统计纯质数个数
    count = 0
    for num in numbers:
        if is_pure_prime(num):
            count += 1
    
    # 输出结果
    print(count)


if __name__ == "__main__":
    main()

