def count_words(text):
    words = text.split()

    word_count = {}

    for word in words:
        word = word.lower()
        word_count[word] = word_count.get(word, 0) + 1
    
    return word_count

def print_word_count(word_count):
    print("\n单词出现次数统计：")
    for word, count in word_count.items():
        print(f"{word}: {count}")

text = input("请输入一段英文文本：")

result = count_words(text)

print_word_count(result) 