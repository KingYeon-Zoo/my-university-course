import random

target = random.randint(1, 100)
max_tries = 5 
tries = 0

print("欢迎来到猜数字游戏！")
print(f"我已经生成了一个1-100之间的数字，你有{max_tries}次机会猜测：")

while tries < max_tries:
    tries += 1
    print(f"\n这是第{tries}次尝试，还剩{max_tries-tries}次机会")
    guess = int(input("请输入你猜的数字："))     
    if guess == target:
        print(f"恭喜你，猜对了！总共用了{tries}次")
        break
    elif guess > target:
        print("太大了！")
    else:
        print("太小了！")

if tries == max_tries:
    print(f"\n游戏结束！你已用完{max_tries}次机会")
    print(f"正确答案是：{target}")