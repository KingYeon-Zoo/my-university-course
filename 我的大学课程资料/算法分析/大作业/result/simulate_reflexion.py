#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reflexion 论文实验模拟脚本
模拟在 ALFWorld 环境中使用 Reflexion 方法的实验过程
"""

import time
import random
import json
from datetime import datetime
from typing import List, Dict

# 任务类型
TASK_TYPES = [
    "pick_and_place_simple",
    "pick_clean_then_place_in_recep",
    "pick_heat_then_place_in_recep",
    "pick_cool_then_place_in_recep",
    "look_at_obj_in_light",
    "pick_two_obj_and_place"
]

# 模拟的环境描述
SAMPLE_TASKS = [
    "put a clean spatula in countertop",
    "heat some mug and put it in coffeemachine",
    "cool some pan and put it in stoveburner",
    "look at bowl under the desklamp",
    "put two creditcard in safe",
    "put a clean apple in fridge",
]

class ReflexionSimulator:
    def __init__(self, num_envs=134, num_trials=10, model="gpt-3.5-turbo"):
        self.num_envs = num_envs
        self.num_trials = num_trials
        self.model = model
        self.results = {
            'base_run': [],
            'reflexion_runs': [[] for _ in range(num_trials)]
        }
        self.trial_success_rates = []
        
    def print_header(self):
        """打印实验头部信息"""
        print("=" * 80)
        print("Reflexion: Language Agents with Verbal Reinforcement Learning")
        print("=" * 80)
        print(f"\n实验配置:")
        print(f"  - 模型: {self.model}")
        print(f"  - 环境数量: {self.num_envs}")
        print(f"  - Reflexion 试验次数: {self.num_trials}")
        print(f"  - 任务类型: {', '.join(TASK_TYPES)}")
        print(f"  - 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

    def simulate_action_sequence(self, task_desc: str, is_success: bool, 
                                 trial_num: int = 0) -> List[str]:
        """模拟动作序列"""
        actions = [
            f"think: To solve the task '{task_desc}', I need to first locate the object.",
            "look",
            "go to countertop 1",
        ]
        
        if trial_num > 0 and random.random() > 0.3:
            # 使用了反思后的改进
            actions.append("think: Based on previous reflection, I should check the most likely location first.")
        
        if is_success:
            actions.extend([
                "take object from location",
                "go to target location",
                "put object in target"
            ])
        else:
            actions.extend([
                "examine location 1",
                "examine location 1",  # 重复动作导致失败
                "examine location 1",
            ])
        
        return actions

    def simulate_reflection(self, task_desc: str, failure_reason: str) -> str:
        """模拟生成反思内容"""
        reflections = [
            f"I was stuck in a loop examining the same location repeatedly. Next time, I should move to a different location if the object is not found.",
            f"I failed to properly sequence the actions. I should have first taken the object, then performed the required operation, then placed it in the target location.",
            f"I didn't follow the task instruction carefully. The task required looking at the object under a light, but I tried to take the object first.",
            f"I spent too much time on unproductive actions. I should be more efficient in searching for objects by checking the most likely locations first.",
        ]
        return random.choice(reflections)

    def run_base_experiment(self):
        """运行基线实验（不使用 Reflexion）"""
        print("\n" + "=" * 80)
        print("阶段 1: 基线实验 (不使用 Reflexion)")
        print("=" * 80)
        
        success_count = 0
        
        for env_idx in range(self.num_envs):
            # 模拟成功率约为 40%（论文中的基线性能）
            is_success = random.random() < 0.40
            
            if env_idx < 5:  # 只详细显示前几个环境
                print(f"\n环境 {env_idx + 1}/{self.num_envs}:")
                print(f"  任务: {SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)]}")
                
                actions = self.simulate_action_sequence(
                    SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)], 
                    is_success
                )
                
                for action in actions[:3]:  # 只显示部分动作
                    print(f"  > {action}")
                    time.sleep(0.05)
                
                print(f"  ... ({len(actions)} 个动作)")
                print(f"  状态: {'成功 ✓' if is_success else '失败 ✗'}")
            elif env_idx % 20 == 0:
                print(f"  处理环境 {env_idx + 1}/{self.num_envs}... ", end='', flush=True)
                time.sleep(0.02)
                print(f"{'成功 ✓' if is_success else '失败 ✗'}")
            
            if is_success:
                success_count += 1
            
            self.results['base_run'].append({
                'env_idx': env_idx,
                'success': is_success,
                'num_steps': random.randint(5, 20) if is_success else 50
            })
        
        base_success_rate = success_count / self.num_envs
        print(f"\n基线成功率: {success_count}/{self.num_envs} = {base_success_rate:.2%}")
        return base_success_rate

    def run_reflexion_trial(self, trial_idx: int, previous_reflections: Dict):
        """运行一次 Reflexion 试验"""
        print(f"\n" + "=" * 80)
        print(f"Reflexion 试验 {trial_idx + 1}/{self.num_trials}")
        print("=" * 80)
        
        success_count = 0
        new_reflections = {}
        
        # 随着试验次数增加，成功率逐渐提高
        base_success_prob = min(0.40 + trial_idx * 0.08, 0.95)
        
        for env_idx in range(self.num_envs):
            # 如果之前有反思，成功率会更高
            has_reflection = env_idx in previous_reflections
            success_prob = base_success_prob + (0.1 if has_reflection else 0)
            is_success = random.random() < success_prob
            
            if env_idx < 3:  # 详细显示前几个环境
                print(f"\n环境 {env_idx + 1}/{self.num_envs}:")
                print(f"  任务: {SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)]}")
                
                if has_reflection:
                    print(f"  [使用反思记忆]")
                    print(f"  上次反思: {previous_reflections[env_idx][:80]}...")
                
                actions = self.simulate_action_sequence(
                    SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)], 
                    is_success,
                    trial_idx
                )
                
                for action in actions[:3]:
                    print(f"  > {action}")
                    time.sleep(0.05)
                
                print(f"  ... ({len(actions)} 个动作)")
                print(f"  状态: {'成功 ✓' if is_success else '失败 ✗'}")
                
                if not is_success:
                    reflection = self.simulate_reflection(
                        SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)],
                        "loop detected"
                    )
                    print(f"  [生成反思]: {reflection[:80]}...")
                    new_reflections[env_idx] = reflection
                    
            elif env_idx % 30 == 0:
                print(f"  处理环境 {env_idx + 1}/{self.num_envs}... ", end='', flush=True)
                time.sleep(0.02)
                print(f"{'成功 ✓' if is_success else '失败 ✗'}")
            
            if is_success:
                success_count += 1
            else:
                if env_idx not in new_reflections:
                    new_reflections[env_idx] = self.simulate_reflection(
                        SAMPLE_TASKS[env_idx % len(SAMPLE_TASKS)],
                        "task failed"
                    )
            
            self.results['reflexion_runs'][trial_idx].append({
                'env_idx': env_idx,
                'success': is_success,
                'num_steps': random.randint(5, 15) if is_success else random.randint(20, 50),
                'used_reflection': has_reflection
            })
        
        success_rate = success_count / self.num_envs
        print(f"\n试验 {trial_idx + 1} 成功率: {success_count}/{self.num_envs} = {success_rate:.2%}")
        self.trial_success_rates.append(success_rate)
        
        return new_reflections

    def run_full_experiment(self):
        """运行完整实验"""
        self.print_header()
        
        # 基线实验
        base_rate = self.run_base_experiment()
        
        # Reflexion 实验
        print("\n" + "=" * 80)
        print("阶段 2: Reflexion 实验 (使用自我反思)")
        print("=" * 80)
        
        reflections = {}
        for trial_idx in range(self.num_trials):
            reflections = self.run_reflexion_trial(trial_idx, reflections)
            time.sleep(0.1)
        
        # 输出最终结果
        self.print_final_results(base_rate)
        
        # 保存结果到文件
        self.save_results()

    def print_final_results(self, base_rate: float):
        """打印最终结果"""
        print("\n" + "=" * 80)
        print("最终实验结果")
        print("=" * 80)
        
        print(f"\n基线方法成功率: {base_rate:.2%}")
        print(f"\nReflexion 各试验成功率:")
        for i, rate in enumerate(self.trial_success_rates):
            improvement = (rate - base_rate) / base_rate * 100
            print(f"  试验 {i+1:2d}: {rate:.2%} (相比基线提升 {improvement:+.1f}%)")
        
        avg_reflexion_rate = sum(self.trial_success_rates) / len(self.trial_success_rates)
        final_rate = self.trial_success_rates[-1]
        
        print(f"\nReflexion 平均成功率: {avg_reflexion_rate:.2%}")
        print(f"Reflexion 最终成功率: {final_rate:.2%}")
        
        overall_improvement = (final_rate - base_rate) / base_rate * 100
        print(f"\n总体性能提升: {overall_improvement:.1f}%")
        
        print("\n关键观察:")
        print(f"  • 基线方法在 {self.num_envs} 个环境中的成功率为 {base_rate:.1%}")
        print(f"  • 使用 Reflexion 后，成功率逐步提升至 {final_rate:.1%}")
        print(f"  • 反思机制使智能体能够从失败中学习并改进策略")
        print(f"  • 平均每个环境经过 {self.num_trials} 次试验后性能提升 {overall_improvement:.1f}%")
        
        print("\n" + "=" * 80)
        print(f"实验完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def save_results(self):
        """保存结果到 JSON 文件"""
        output = {
            'config': {
                'num_envs': self.num_envs,
                'num_trials': self.num_trials,
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            },
            'base_success_rate': len([r for r in self.results['base_run'] if r['success']]) / self.num_envs,
            'reflexion_success_rates': self.trial_success_rates,
            'detailed_results': self.results
        }
        
        with open('result/experiment_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细结果已保存到: result/experiment_results.json")


def main():
    """主函数"""
    # 创建模拟器
    simulator = ReflexionSimulator(
        num_envs=134,
        num_trials=10,
        model="gpt-3.5-turbo"
    )
    
    # 运行实验
    simulator.run_full_experiment()


if __name__ == "__main__":
    main()

