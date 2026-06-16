def odd_number_generator(m):
    for x in range(1, m + 1, 2):  
        yield x

n = int(input("请输入要生成的元素个数n："))
m = int(input("请输入元素的最大值m："))

max_count = (m + 1) // 2

if max_count < n:
    print(f"在1到{m}之间只有{max_count}个奇数，无法生成{n}个奇数")
else:
    odd = odd_number_generator(m)
    my_tuple = tuple(next(odd) for _ in range(n))
    print(my_tuple)
