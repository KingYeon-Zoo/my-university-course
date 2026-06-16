"""
实验3-题目3：扑克牌比较
比较两副扑克牌的大小
"""

class Card:
    """扑克牌类"""
    # 面值映射
    VALUE_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                 '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def __init__(self, card_str):
        self.value = self.VALUE_MAP[card_str[0]]
        self.suit = card_str[1]
    
    def __repr__(self):
        return f"{self.value}{self.suit}"


def parse_hand(cards_str):
    """解析一副牌"""
    cards = []
    for i in range(0, len(cards_str), 3):
        cards.append(Card(cards_str[i:i+2]))
    return cards


def get_hand_type(cards):
    """
    判断牌型并返回(类型编号, 关键值列表)
    类型编号越大，牌型越大
    """
    values = sorted([card.value for card in cards], reverse=True)
    suits = [card.suit for card in cards]
    
    # 统计每个面值的数量
    value_counts = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1
    
    # 按出现次数分组
    counts = sorted(value_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    
    # 判断是否同花
    is_flush = len(set(suits)) == 1
    
    # 判断是否顺子
    is_straight = False
    if len(value_counts) == 5:
        if values[0] - values[4] == 4:
            is_straight = True
        # A-2-3-4-5特殊情况
        elif values == [14, 5, 4, 3, 2]:
            is_straight = True
            values = [5, 4, 3, 2, 1]  # A算作1
    
    # 9. Straight Flush (同花顺)
    if is_flush and is_straight:
        return (9, values)
    
    # 8. Four of a Kind (四条)
    if counts[0][1] == 4:
        return (8, [counts[0][0], counts[1][0]])
    
    # 7. Full House (葫芦)
    if counts[0][1] == 3 and counts[1][1] == 2:
        return (7, [counts[0][0], counts[1][0]])
    
    # 6. Flush (同花)
    if is_flush:
        return (6, values)
    
    # 5. Straight (顺子)
    if is_straight:
        return (5, values)
    
    # 4. Three of a Kind (三条)
    if counts[0][1] == 3:
        other_values = sorted([counts[1][0], counts[2][0]], reverse=True)
        return (4, [counts[0][0]] + other_values)
    
    # 3. Two Pairs (两对)
    if counts[0][1] == 2 and counts[1][1] == 2:
        pairs = sorted([counts[0][0], counts[1][0]], reverse=True)
        return (3, pairs + [counts[2][0]])
    
    # 2. Pair (一对)
    if counts[0][1] == 2:
        other_values = sorted([counts[1][0], counts[2][0], counts[3][0]], reverse=True)
        return (2, [counts[0][0]] + other_values)
    
    # 1. High Card (高牌)
    return (1, values)


def compare_hands(black_cards, white_cards):
    """
    比较两副牌的大小
    返回: "Black wins.", "White wins.", 或 "Tie."
    """
    black_type, black_values = get_hand_type(black_cards)
    white_type, white_values = get_hand_type(white_cards)
    
    # 先比较牌型
    if black_type > white_type:
        return "Black wins."
    elif white_type > black_type:
        return "White wins."
    
    # 牌型相同，比较关键值
    for b, w in zip(black_values, white_values):
        if b > w:
            return "Black wins."
        elif w > b:
            return "White wins."
    
    # 完全相同
    return "Tie."


def main():
    n = int(input())
    
    for _ in range(n):
        line = input().strip().split()
        
        # 前5张是黑方的牌，后5张是白方的牌
        black_str = ' '.join(line[0:5])
        white_str = ' '.join(line[5:10])
        
        black_cards = parse_hand(black_str)
        white_cards = parse_hand(white_str)
        
        result = compare_hands(black_cards, white_cards)
        print(result)


if __name__ == "__main__":
    main()

