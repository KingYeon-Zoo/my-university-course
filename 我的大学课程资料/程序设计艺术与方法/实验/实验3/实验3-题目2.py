"""
实验3-题目2：读者到访记录
记录每个读者是第几次出现
"""

def record_visits(n, readers):
    """
    记录每个读者的到访次数
    """
    visit_count = {}  # 记录每个读者的出现次数
    result = []
    
    for reader_id in readers:
        # 获取该读者当前的出现次数
        if reader_id in visit_count:
            visit_count[reader_id] += 1
        else:
            visit_count[reader_id] = 1
        
        # 记录这是第几次出现
        result.append(visit_count[reader_id])
    
    return result


def main():
    # 读取记录条数
    n = int(input())
    
    # 读取读者编号
    readers = list(map(int, input().split()))
    
    # 处理记录
    result = record_visits(n, readers)
    
    # 输出结果
    print(' '.join(map(str, result)))


if __name__ == "__main__":
    main()

