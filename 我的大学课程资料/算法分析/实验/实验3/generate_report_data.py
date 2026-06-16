"""
生成实验报告中的详细数据
用于补充实验报告的表格和图表
"""

import random
import time
from hybrid_sort_experiment import HybridSortExperiment


def generate_markdown_table(results: dict, size: int) -> str:
    """
    生成Markdown格式的表格
    
    参数:
        results: 实验结果
        size: 数据规模
    
    返回:
        Markdown表格字符串
    """
    table = f"\n表 不同阈值下混合排序的运行时间（数据规模n={size}）\n\n"
    table += "| 阈值k | 运行时间(秒) | 比较次数 |\n"
    table += "|-------|-------------|----------|\n"
    
    for i in range(len(results[size]['thresholds'])):
        k = results[size]['thresholds'][i]
        t = results[size]['avg_time'][i]
        c = results[size]['avg_comparisons'][i]
        table += f"| {k:5d} | {t:11.4f} | {c:8.0f} |\n"
    
    return table


def test_small_example():
    """测试小规模示例，用于报告中的算法演示"""
    print("\n" + "="*80)
    print("小规模示例测试（用于报告演示）")
    print("="*80)
    
    experiment = HybridSortExperiment()
    
    # 示例数组
    test_arr = [34, 7, 23, 32, 5, 62, 32, 12, 45, 18]
    print(f"\n原始数组: {test_arr}")
    print(f"数组长度: {len(test_arr)}")
    
    # 测试不同阈值
    thresholds = [0, 5, 10]
    
    for k in thresholds:
        arr_copy = test_arr.copy()
        start = time.perf_counter()
        sorted_arr, comparisons = experiment.hybrid_sort(arr_copy, threshold=k)
        end = time.perf_counter()
        
        print(f"\n阈值 k={k}:")
        print(f"  排序结果: {sorted_arr}")
        print(f"  比较次数: {comparisons}")
        print(f"  运行时间: {(end-start)*1000:.3f} 毫秒")
        print(f"  正确性: {'✓ 通过' if sorted_arr == sorted(test_arr) else '✗ 失败'}")


def analyze_threshold_impact():
    """分析阈值对性能的影响"""
    print("\n" + "="*80)
    print("阈值影响深度分析")
    print("="*80)
    
    experiment = HybridSortExperiment()
    
    size = 20000
    thresholds = [0, 5, 10, 15, 20, 25, 30]
    
    print(f"\n数据规模: {size}")
    print(f"测试阈值: {thresholds}")
    
    results = []
    
    for k in thresholds:
        total_time = 0
        total_comp = 0
        repeats = 5
        
        for i in range(repeats):
            arr = experiment.generate_random_data(size, seed=100+i)
            t, c = experiment.run_single_test(arr, k)
            total_time += t
            total_comp += c
        
        avg_time = total_time / repeats
        avg_comp = total_comp / repeats
        
        results.append({
            'threshold': k,
            'time': avg_time,
            'comparisons': avg_comp
        })
    
    # 找到最优点
    min_time_idx = min(range(len(results)), key=lambda i: results[i]['time'])
    optimal = results[min_time_idx]
    
    print("\n详细结果:")
    print("-" * 70)
    print(f"{'阈值k':^8} | {'时间(秒)':^12} | {'比较次数':^12} | {'相对性能':^12}")
    print("-" * 70)
    
    baseline_time = results[0]['time']
    
    for r in results:
        k = r['threshold']
        t = r['time']
        c = r['comparisons']
        relative = (baseline_time - t) / baseline_time * 100
        
        marker = " *最优*" if r == optimal else ""
        print(f"{k:^8} | {t:^12.6f} | {c:^12.0f} | {relative:^11.2f}%{marker}")
    
    print("-" * 70)
    
    print(f"\n结论:")
    print(f"  最优阈值: k* = {optimal['threshold']}")
    print(f"  最优时间: {optimal['time']:.6f} 秒")
    print(f"  性能提升: {(baseline_time - optimal['time']) / baseline_time * 100:.2f}%")


def compare_with_standard_sort():
    """与标准排序算法对比"""
    print("\n" + "="*80)
    print("与Python内置排序算法对比")
    print("="*80)
    
    experiment = HybridSortExperiment()
    
    sizes = [5000, 10000, 20000, 50000]
    
    print("\n" + "-" * 70)
    print(f"{'数据规模':^12} | {'混合排序':^15} | {'内置sort':^15} | {'速度比':^12}")
    print("-" * 70)
    
    for size in sizes:
        # 测试混合排序（k=15）
        arr1 = experiment.generate_random_data(size, seed=42)
        start = time.perf_counter()
        experiment.hybrid_sort(arr1, threshold=15)
        hybrid_time = time.perf_counter() - start
        
        # 测试Python内置排序
        arr2 = experiment.generate_random_data(size, seed=42)
        start = time.perf_counter()
        arr2.sort()
        builtin_time = time.perf_counter() - start
        
        ratio = hybrid_time / builtin_time
        
        print(f"{size:^12} | {hybrid_time:^15.6f} | {builtin_time:^15.6f} | {ratio:^12.2f}x")
    
    print("-" * 70)
    print("\n说明: Python内置sort使用Timsort算法，是高度优化的混合排序算法")


def verify_algorithm_correctness():
    """验证算法正确性"""
    print("\n" + "="*80)
    print("算法正确性验证")
    print("="*80)
    
    experiment = HybridSortExperiment()
    
    test_cases = [
        ([5, 2, 8, 1, 9], "随机数组"),
        ([1, 2, 3, 4, 5], "已排序数组"),
        ([5, 4, 3, 2, 1], "逆序数组"),
        ([3, 3, 3, 3, 3], "全部相同"),
        ([1], "单元素"),
        ([], "空数组"),
        ([2, 1], "两元素"),
        ([5, 2, 8, 2, 9, 1, 5], "包含重复元素"),
    ]
    
    print("\n测试用例:")
    all_passed = True
    
    for arr, description in test_cases:
        original = arr.copy()
        expected = sorted(arr)
        
        for k in [0, 10, 20]:
            sorted_arr, _ = experiment.hybrid_sort(arr, threshold=k)
            passed = sorted_arr == expected
            all_passed = all_passed and passed
            
            if not passed:
                print(f"  ✗ {description} (k={k}): 失败")
                print(f"    原始: {original}")
                print(f"    期望: {expected}")
                print(f"    实际: {sorted_arr}")
            else:
                print(f"  ✓ {description} (k={k}): 通过")
    
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")


def main():
    """主函数"""
    print("\n")
    print("="*80)
    print(" "*20 + "实验报告数据生成工具")
    print("="*80)
    
    # 1. 小规模示例测试
    test_small_example()
    
    # 2. 阈值影响分析
    analyze_threshold_impact()
    
    # 3. 与标准排序对比
    compare_with_standard_sort()
    
    # 4. 算法正确性验证
    verify_algorithm_correctness()
    
    print("\n" + "="*80)
    print("数据生成完成！")
    print("="*80)


if __name__ == "__main__":
    main()
