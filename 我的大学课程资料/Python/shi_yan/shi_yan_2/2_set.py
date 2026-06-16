class CustomSet:
    def __init__(self, elements=None):
        self.elements = [] if elements is None else list(elements)

    def jiaoji(self, other_set):
        print(f'交集：{CustomSet([x for x in self.elements if x in other_set.elements])}')

    def chaji(self, other_set):
        print(f'差集：{CustomSet([x for x in self.elements if x not in other_set.elements])}')

    def bingji(self, other_set):
        result = self.elements.copy()
        for element in other_set.elements:
            if element not in result:
                result.append(element)
        print(f'并集：{CustomSet(result)}')
        
    def __str__(self):
        return str(self.elements)

def system_set_method():
    print("\n使用系统集合类：")

    setA = set(input("请输入第一个集合（元素用空格分隔）：").split())
    setB = set(input("请输入第二个集合（元素用空格分隔）：").split())

    print(f"交集：{setA & setB}")
    print(f"差集：{setA - setB}")
    print(f"并集：{setA | setB}")

def custom_set_method():
    print("\n使用自定义集合类：")

    setA = CustomSet(input("请输入第一个集合（元素用空格分隔）：").split())
    setB = CustomSet(input("请输入第二个集合（元素用空格分隔）：").split())

    setA.jiaoji(setB)
    setA.chaji(setB)
    setA.bingji(setB)
print("集合操作演示：")
system_set_method()
custom_set_method() 