import re

def find_three_letter_words(text):
    pattern = r'\b[a-zA-Z]{3}\b'
    return re.findall(pattern, text)

text = input("请输入一段英文文本：")

result = find_three_letter_words(text)

print("\n结果：")
print(result)

