import random
import numpy as np
import math

def fibonacci(n):
    result = [1, 1]
    while True:
        next_num = result[-1] + result[-2]
        if next_num >= n:
            break
        result.append(next_num)
    return result

def get_primes():
    set_n = 0
    while set_n <= 2:
        set_n = int(input("请输入一个大于2的整数n："))
        if set_n >2:
            break
        else:
            print("请输入一个大于2的整数n：")
    primes = []
    for i in range(2, set_n):
        for j in range(2, i):
            if i % j == 0:
                break
        else:
            primes.append(i)
    print(primes)  


def is_huiwen(s):
    return s == s[::-1]

def random_list(n):
    numbers = [np.random.randint(1, 100) for _ in range(n)]
    above_avg = tuple(x for x in numbers if x > np.mean(numbers))    
    return (np.mean(numbers), *above_avg)

def calculate_growth():
    target = 37.78 
    work_days = (365// 7) * 5 + (365 % 7) 
    rest_days = 365 - work_days  
    rest_day_effect = math.pow(0.99, rest_days)
    required_work_growth = target / rest_day_effect
    daily_effort = (math.pow(required_work_growth, 1/work_days) - 1) * 100
    
    print(f"工作日需要努力 {daily_effort:.3f}% 才能达到目标")
   

print("1. 斐波那契数列:")
n = int(input("请输入一个整数n："))
print(fibonacci(n))

print("\n2. 素数列表:")
get_primes()

print("\n3. 回文测试:")
s = input("请输入一个字符串：")
print(f"'{s}' 是回文串吗？ {is_huiwen(s)}")

print("\n4. 随机列表:")
n = int(input("请输入一个整数n："))
print(random_list(n))

print("\n5. 工作日努力程度计算:")
calculate_growth()
