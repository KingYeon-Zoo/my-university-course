"""
算法正确性测试
"""

from dp_algorithms import LCSAlgorithm, Knapsack01
import random


def test_lcs():
    """测试LCS算法的正确性"""
    print("=" * 80)
    print("最长公共子序列(LCS)算法正确性测试")
    print("=" * 80)
    
    lcs = LCSAlgorithm()
    test_cases = [
        # (X, Y, 期望长度, 期望LCS之一)
        ("ABCDGH", "AEDFHR", 3, "ADH"),
        ("AGGTAB", "GXTXAYB", 4, "GTAB"),
        ("", "ABC", 0, ""),
        ("ABC", "", 0, ""),
        ("A", "A", 1, "A"),
        ("ABC", "DEF", 0, ""),
        ("ABCDEF", "ABCDEF", 6, "ABCDEF"),
        ("XMJYAUZ", "MZJAWXU", 4, "MJAU"),
        ("HUMAN", "CHIMPANZEE", 4, "HMAN"),
        ("AAAA", "AA", 2, "AA"),
    ]
    
    print(f"\n{'测试编号':<8} {'测试类型':<12} {'X序列':<15} {'Y序列':<15} "
          f"{'期望长度':<8} {'实际长度':<8} {'期望LCS':<12} {'实际LCS':<12} {'结果':<6}")
    print("-" * 120)
    
    results = []
    for i, (X, Y, expected_len, expected_lcs) in enumerate(test_cases, 1):
        length, lcs_str, _ = lcs.solve(X, Y)
        
        # 确定测试类型
        if not X or not Y:
            test_type = "边界案例"
        elif X == Y:
            test_type = "相同序列"
        elif length == 0:
            test_type = "无公共子序列"
        elif len(X) <= 5 or len(Y) <= 5:
            test_type = "简单案例"
        else:
            test_type = "一般案例"
        
        # 验证结果
        is_correct = (length == expected_len)
        result_mark = "PASS" if is_correct else "FAIL"
        
        print(f"Test {i:<3} {test_type:<12} {X:<15} {Y:<15} "
              f"{expected_len:<8} {length:<8} {expected_lcs:<12} {lcs_str:<12} {result_mark:<6}")
        
        results.append({
            'id': i,
            'type': test_type,
            'X': X,
            'Y': Y,
            'expected_len': expected_len,
            'actual_len': length,
            'expected_lcs': expected_lcs,
            'actual_lcs': lcs_str,
            'correct': is_correct
        })
    
    # 统计结果
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    print("-" * 120)
    print(f"\n测试通过率: {correct_count}/{total_count} = {100*correct_count/total_count:.1f}%")
    
    return results


def test_knapsack():
    """测试0-1背包算法的正确性"""
    print("\n" + "=" * 80)
    print("0-1背包问题算法正确性测试")
    print("=" * 80)
    
    knapsack = Knapsack01()
    test_cases = [
        # (weights, values, capacity, 期望最大价值)
        ([2, 3, 4, 5], [3, 4, 5, 6], 8, 10),
        ([1, 2, 3], [6, 10, 12], 5, 22),
        ([10, 20, 30], [60, 100, 120], 50, 220),
        ([5], [10], 5, 10),
        ([5], [10], 4, 0),
        ([], [], 10, 0),
        ([1, 1, 1, 1], [1, 1, 1, 1], 2, 2),
        ([2, 1, 3, 2], [12, 10, 20, 15], 5, 37),
        ([7, 3, 4, 5], [42, 12, 40, 25], 10, 65),
        ([1, 2, 3, 4, 5], [10, 5, 15, 7, 6], 7, 32),
    ]
    
    print(f"\n{'测试编号':<8} {'测试类型':<12} {'物品数':<8} {'背包容量':<10} "
          f"{'期望价值':<10} {'实际价值':<10} {'结果':<6}")
    print("-" * 80)
    
    results = []
    for i, (weights, values, capacity, expected_value) in enumerate(test_cases, 1):
        if len(weights) == 0:
            max_value = 0
            selected = []
        else:
            max_value, selected, _ = knapsack.solve_with_items(weights, values, capacity)
        
        # 确定测试类型
        if len(weights) == 0:
            test_type = "边界案例"
        elif len(weights) == 1:
            test_type = "单物品"
        elif len(weights) <= 4:
            test_type = "简单案例"
        else:
            test_type = "一般案例"
        
        # 验证结果
        is_correct = (max_value == expected_value)
        result_mark = "PASS" if is_correct else "FAIL"
        
        print(f"Test {i:<3} {test_type:<12} {len(weights):<8} {capacity:<10} "
              f"{expected_value:<10} {max_value:<10} {result_mark:<6}")
        
        results.append({
            'id': i,
            'type': test_type,
            'weights': weights,
            'values': values,
            'capacity': capacity,
            'expected_value': expected_value,
            'actual_value': max_value,
            'selected': selected,
            'correct': is_correct
        })
    
    # 统计结果
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    print("-" * 80)
    print(f"\n测试通过率: {correct_count}/{total_count} = {100*correct_count/total_count:.1f}%")
    
    return results


def test_random_cases():
    """测试随机生成的案例"""
    print("\n" + "=" * 80)
    print("随机案例测试")
    print("=" * 80)
    
    random.seed(42)
    
    # LCS随机测试
    print("\nLCS随机测试:")
    lcs = LCSAlgorithm()
    for i in range(5):
        length = random.randint(5, 15)
        X = ''.join(random.choices('ABCDEFGH', k=length))
        Y = ''.join(random.choices('ABCDEFGH', k=length))
        
        lcs_len, lcs_str, _ = lcs.solve(X, Y)
        print(f"  案例{i+1}: X={X}, Y={Y}")
        print(f"         LCS长度={lcs_len}, LCS={lcs_str}")
    
    # 背包随机测试
    print("\n0-1背包随机测试:")
    knapsack = Knapsack01()
    for i in range(5):
        n = random.randint(3, 8)
        weights = [random.randint(1, 10) for _ in range(n)]
        values = [random.randint(1, 20) for _ in range(n)]
        capacity = random.randint(10, 30)
        
        max_value, selected, _ = knapsack.solve_with_items(weights, values, capacity)
        total_weight = sum(weights[j] for j in selected)
        
        print(f"  案例{i+1}: 物品数={n}, 容量={capacity}")
        print(f"         最大价值={max_value}, 选中物品={selected}, 总重量={total_weight}")


if __name__ == "__main__":
    # 运行所有测试
    lcs_results = test_lcs()
    knapsack_results = test_knapsack()
    test_random_cases()
    
    print("\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)

