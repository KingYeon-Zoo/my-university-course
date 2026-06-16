"""
混合排序策略中切换阈值的实证分析实验
实现混合排序算法，并系统测试不同切换阈值对性能的影响
"""

import time
import random
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple


class HybridSortExperiment:
    """混合排序实验类"""
    
    def __init__(self):
        self.comparisons = 0  # 比较次数计数器
    
    def insertion_sort(self, arr: List[int], left: int, right: int) -> int:
        """
        插入排序
        
        参数:
            arr: 待排序数组
            left: 左边界
            right: 右边界
        
        返回:
            比较次数
        """
        comparisons = 0
        
        for i in range(left + 1, right + 1):
            key = arr[i]
            j = i - 1
            
            while j >= left and arr[j] > key:
                comparisons += 1
                arr[j + 1] = arr[j]
                j -= 1
            
            # 边界条件的比较
            if j >= left:
                comparisons += 1
            
            arr[j + 1] = key
        
        return comparisons
    
    def median_of_three(self, a: int, b: int, c: int) -> int:
        """
        三数取中
        
        参数:
            a, b, c: 三个待比较的数
        
        返回:
            中位数
        """
        if a <= b:
            if b <= c:
                return b
            elif a <= c:
                return c
            else:
                return a
        else:
            if a <= c:
                return a
            elif b <= c:
                return c
            else:
                return b
    
    def hybrid_quick_sort(self, arr: List[int], left: int, right: int, threshold: int) -> int:
        """
        混合快速排序（快速排序部分）
        
        参数:
            arr: 待排序数组
            left: 左边界
            right: 右边界
            threshold: 切换阈值
        
        返回:
            比较次数
        """
        comparisons = 0
        
        # 如果子数组长度小于等于阈值，直接返回
        if right - left + 1 <= threshold:
            return 0
        
        # 选择枢轴元素（三数取中）
        mid = (left + right) // 2
        pivot = self.median_of_three(arr[left], arr[mid], arr[right])
        comparisons += 3
        
        # 三路划分
        i = left
        lt = left  # 小于pivot的区域右边界
        gt = right  # 大于pivot的区域左边界
        
        while i <= gt:
            comparisons += 1
            if arr[i] < pivot:
                arr[i], arr[lt] = arr[lt], arr[i]
                i += 1
                lt += 1
            elif arr[i] > pivot:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1
        
        # 递归处理左右两部分
        comparisons += self.hybrid_quick_sort(arr, left, lt - 1, threshold)
        comparisons += self.hybrid_quick_sort(arr, gt + 1, right, threshold)
        
        return comparisons
    
    def hybrid_sort(self, arr: List[int], threshold: int) -> Tuple[List[int], int]:
        """
        混合排序主函数
        
        参数:
            arr: 待排序数组
            threshold: 切换阈值k
        
        返回:
            (排序后的数组, 比较次数)
        """
        n = len(arr)
        arr_copy = arr.copy()  # 复制数组，避免修改原数组
        comparisons = 0
        
        # 执行混合快速排序
        comparisons += self.hybrid_quick_sort(arr_copy, 0, n - 1, threshold)
        
        # 对整个数组执行插入排序，处理小片段
        comparisons += self.insertion_sort(arr_copy, 0, n - 1)
        
        return arr_copy, comparisons
    
    def generate_random_data(self, size: int, seed: int = 42) -> List[int]:
        """
        生成随机测试数据
        
        参数:
            size: 数据规模
            seed: 随机种子
        
        返回:
            随机数组
        """
        random.seed(seed)
        return [random.randint(0, 1000000) for _ in range(size)]
    
    def run_single_test(self, arr: List[int], threshold: int) -> Tuple[float, int]:
        """
        运行单次测试
        
        参数:
            arr: 测试数据
            threshold: 切换阈值
        
        返回:
            (运行时间, 比较次数)
        """
        start_time = time.perf_counter()
        _, comparisons = self.hybrid_sort(arr, threshold)
        end_time = time.perf_counter()
        
        runtime = end_time - start_time
        return runtime, comparisons
    
    def run_experiment(self, sizes: List[int], thresholds: List[int], repeats: int = 10) -> dict:
        """
        运行完整实验
        
        参数:
            sizes: 数据规模列表
            thresholds: 阈值列表
            repeats: 每组参数重复次数
        
        返回:
            实验结果字典
        """
        results = {}
        
        for size in sizes:
            print(f"\n测试数据规模: {size}")
            results[size] = {
                'thresholds': [],
                'avg_time': [],
                'avg_comparisons': []
            }
            
            for threshold in thresholds:
                total_time = 0
                total_comparisons = 0
                
                for repeat in range(repeats):
                    # 生成测试数据
                    arr = self.generate_random_data(size, seed=42 + repeat)
                    
                    # 运行测试
                    runtime, comparisons = self.run_single_test(arr, threshold)
                    total_time += runtime
                    total_comparisons += comparisons
                
                # 计算平均值
                avg_time = total_time / repeats
                avg_comparisons = total_comparisons / repeats
                
                results[size]['thresholds'].append(threshold)
                results[size]['avg_time'].append(avg_time)
                results[size]['avg_comparisons'].append(avg_comparisons)
                
                print(f"阈值 k={threshold:2d}: 平均时间={avg_time:.6f}秒, 平均比较次数={avg_comparisons:.0f}")
        
        return results
    
    def visualize_results(self, results: dict, save_path: str = None):
        """
        可视化实验结果
        
        参数:
            results: 实验结果
            save_path: 保存路径（可选）
        """
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文
        plt.rcParams['axes.unicode_minus'] = False  # 用于正常显示负号
        
        sizes = list(results.keys())
        
        # 图1: 运行时间对比
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        for size in sizes:
            plt.plot(results[size]['thresholds'], 
                    results[size]['avg_time'], 
                    marker='o', 
                    label=f'n={size}')
        plt.xlabel('切换阈值 k', fontsize=12)
        plt.ylabel('运行时间 (秒)', fontsize=12)
        plt.title('图1: 不同阈值下的运行时间', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 图2: 比较次数对比
        plt.subplot(1, 2, 2)
        for size in sizes:
            plt.plot(results[size]['thresholds'], 
                    results[size]['avg_comparisons'], 
                    marker='s', 
                    label=f'n={size}')
        plt.xlabel('切换阈值 k', fontsize=12)
        plt.ylabel('比较次数', fontsize=12)
        plt.title('图2: 不同阈值下的比较次数', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n图表已保存至: {save_path}")
        
        plt.show()
    
    def find_optimal_threshold(self, results: dict) -> dict:
        """
        找到最优阈值
        
        参数:
            results: 实验结果
        
        返回:
            每个数据规模对应的最优阈值
        """
        optimal_thresholds = {}
        
        print("\n" + "="*60)
        print("最优阈值分析")
        print("="*60)
        
        for size in results.keys():
            times = results[size]['avg_time']
            thresholds = results[size]['thresholds']
            
            min_idx = times.index(min(times))
            optimal_k = thresholds[min_idx]
            optimal_time = times[min_idx]
            
            # 计算相对于k=0的性能提升
            baseline_time = times[0]
            improvement = (baseline_time - optimal_time) / baseline_time * 100
            
            optimal_thresholds[size] = optimal_k
            
            print(f"\n数据规模 n={size}:")
            print(f"  最优阈值: k*={optimal_k}")
            print(f"  最优时间: {optimal_time:.6f}秒")
            print(f"  基准时间(k=0): {baseline_time:.6f}秒")
            print(f"  性能提升: {improvement:.2f}%")
        
        return optimal_thresholds
    
    def print_table(self, results: dict):
        """
        打印实验结果表格
        
        参数:
            results: 实验结果
        """
        print("\n" + "="*80)
        print("实验结果表格")
        print("="*80)
        
        for size in results.keys():
            print(f"\n表: 数据规模 n={size}")
            print("-" * 70)
            print(f"{'阈值k':^10} | {'运行时间(秒)':^15} | {'比较次数':^15}")
            print("-" * 70)
            
            for i in range(len(results[size]['thresholds'])):
                threshold = results[size]['thresholds'][i]
                avg_time = results[size]['avg_time'][i]
                avg_comp = results[size]['avg_comparisons'][i]
                
                print(f"{threshold:^10} | {avg_time:^15.6f} | {avg_comp:^15.0f}")
            
            print("-" * 70)


def main():
    """主函数"""
    print("混合排序策略中切换阈值的实证分析实验")
    print("="*80)
    
    # 创建实验对象
    experiment = HybridSortExperiment()
    
    # 实验参数设置
    sizes = [10000, 50000, 100000]  # 数据规模
    thresholds = list(range(0, 55, 5))  # 阈值: 0, 5, 10, ..., 50
    repeats = 10  # 每组参数重复10次
    
    print(f"\n实验参数:")
    print(f"  数据规模: {sizes}")
    print(f"  切换阈值: {thresholds}")
    print(f"  重复次数: {repeats}")
    print(f"  数据分布: 完全随机")
    print(f"  随机种子: 42")
    
    # 运行实验
    print("\n开始实验...")
    results = experiment.run_experiment(sizes, thresholds, repeats)
    
    # 打印结果表格
    experiment.print_table(results)
    
    # 找到最优阈值
    optimal_thresholds = experiment.find_optimal_threshold(results)
    
    # 可视化结果
    print("\n生成可视化图表...")
    experiment.visualize_results(results, save_path='混合排序实验结果.png')
    
    # 验证算法正确性
    print("\n" + "="*80)
    print("算法正确性验证")
    print("="*80)
    test_arr = [34, 7, 23, 32, 5, 62, 32, 12, 45, 18]
    print(f"原始数组: {test_arr}")
    
    sorted_arr, comparisons = experiment.hybrid_sort(test_arr, threshold=15)
    print(f"排序结果: {sorted_arr}")
    print(f"比较次数: {comparisons}")
    print(f"正确性检验: {'通过' if sorted_arr == sorted(test_arr) else '失败'}")
    
    print("\n实验完成！")


if __name__ == "__main__":
    main()
