import random
import string

def generate_random_strings(num_strings, min_length=5, max_length=15):
    strings = []
    for _ in range(num_strings):
        length = random.randint(min_length, max_length)
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        strings.append(random_string)
    return strings

def write_strings_to_file(strings, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for s in strings:
            f.write(s + '\n')

def read_and_count_strings(filename):
    count = 0
    with open(filename, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
    return count


num_strings = 10
strings = generate_random_strings(num_strings)

print("生成的随机字符串：")
for i, s in enumerate(strings, 1):
    print(f"{i}. {s}")

filename = "random_strings.txt"
write_strings_to_file(strings, filename)
print(f"\n字符串已写入文件：{filename}")

count = read_and_count_strings(filename)
print(f"文件中的字符串数量：{count}")

