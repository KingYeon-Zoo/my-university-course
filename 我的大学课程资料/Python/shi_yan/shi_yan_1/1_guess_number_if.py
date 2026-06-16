import random

target = random.randint(1, 100)
print("欢迎来到猜数字游戏！")
print("我已经生成了一个1-100之间的数字，请开始猜测：")

guess = int(input("请输入你猜的数字："))

if guess == target:
    print("恭喜你，猜对了！")
elif guess > target:
    print("太大了！正确答案是：", target)
else:
    print("太小了！正确答案是：", target)

