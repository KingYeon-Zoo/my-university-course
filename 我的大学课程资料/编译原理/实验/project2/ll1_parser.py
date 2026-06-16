import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re

class LL1Parser:
    def __init__(self):
        # 文法规则
        self.grammar = {
            'E': ['TG'],
            'G': ['+TG', '-TG', 'ε'],
            'T': ['FS'],
            'S': ['*FS', '/FS', 'ε'],
            'F': ['(E)', 'i']
        }
        
        # 初始化终结符和非终结符集合
        self.terminals = set(['+', '-', '*', '/', '(', ')', 'i', 'ε'])
        self.non_terminals = set(self.grammar.keys())
        
        # 初始化FIRST集合、FOLLOW集合和预测分析表
        self.first_sets = {}
        self.follow_sets = {}
        self.parsing_table = {}
        
        # 初始化冲突标记
        self.conflicts = []
        self.grammar_transformation_steps = []
        
        self.calculate_first_sets()
        self.calculate_follow_sets()
        self.build_parsing_table()
        
        # 初始化分析栈和步骤记录
        self.stack = []
        self.steps = []
    
    def set_grammar(self, grammar, terminals=None):
        """设置新的文法规则并重新计算所有集合"""
        self.grammar = grammar
        self.non_terminals = set(grammar.keys())
        
        if terminals is None:
            # 自动提取终结符
            self.terminals = set()
            for productions in grammar.values():
                for prod in productions:
                    if prod != 'ε':
                        i = 0
                        while i < len(prod):
                            # 处理非终结符
                            is_non_terminal = False
                            for nt in self.non_terminals:
                                if i <= len(prod) - len(nt) and prod[i:i+len(nt)] == nt:
                                    i += len(nt)
                                    is_non_terminal = True
                                    break
                            
                            # 如果不是非终结符，则添加为终结符
                            if not is_non_terminal:
                                self.terminals.add(prod[i])
                                i += 1
            self.terminals.add('ε')
        else:
            self.terminals = terminals
        
        # 重新计算集合
        self.conflicts = []
        self.grammar_transformation_steps = []
        self.first_sets = {}
        self.follow_sets = {}
        self.parsing_table = {}
        self.calculate_first_sets()
        self.calculate_follow_sets()
        self.build_parsing_table()
    
    def is_ll1_grammar(self):
        """检查当前文法是否是LL(1)文法"""
        self.conflicts = []
        
        # 确保FIRST和FOLLOW集合已计算
        self.calculate_first_sets()
        self.calculate_follow_sets()
        
        # 构建预测分析表，检查是否有冲突
        for nt in self.non_terminals:
            productions = self.grammar[nt]
            
            # 记录每个终结符对应的产生式
            terminal_to_production = {}
            
            for production in productions:
                # 计算该产生式的FIRST集
                production_first = self.get_production_first(production)
                
                # 检查FIRST集中的每个终结符
                for terminal in production_first:
                    if terminal != 'ε':
                        if terminal in terminal_to_production:
                            # 发现冲突
                            self.conflicts.append({
                                'non_terminal': nt,
                                'terminal': terminal,
                                'production1': terminal_to_production[terminal],
                                'production2': production
                            })
                        else:
                            terminal_to_production[terminal] = production
                
                # 检查是否包含ε，如果包含则需要检查FOLLOW集
                if 'ε' in production_first:
                    for terminal in self.follow_sets.get(nt, []):
                        if terminal in terminal_to_production:
                            # 发现冲突
                            self.conflicts.append({
                                'non_terminal': nt,
                                'terminal': terminal,
                                'production1': terminal_to_production[terminal],
                                'production2': production
                            })
                        else:
                            terminal_to_production[terminal] = production
        
        return len(self.conflicts) == 0
    
    def convert_to_ll1(self):
        """将非LL(1)文法转换为LL(1)文法"""
        if self.is_ll1_grammar():
            return True, "当前文法已经是LL(1)文法"
        
        # 记录原始文法
        original_grammar = {k: list(v) for k, v in self.grammar.items()}
        self.grammar_transformation_steps.append({
            'description': '原始文法',
            'grammar': self.grammar_str(original_grammar)
        })
        
        # 消除左递归
        has_left_recursion = self.eliminate_left_recursion()
        
        # 完全重新计算FIRST和FOLLOW集合
        self.first_sets = {}
        self.follow_sets = {}
        self.calculate_first_sets()
        self.calculate_follow_sets()
        
        # 消除回溯（左因子提取）
        has_backtracking = self.eliminate_backtracking()
        
        # 再次完全重新计算FIRST和FOLLOW集合
        self.first_sets = {}
        self.follow_sets = {}
        self.calculate_first_sets()
        self.calculate_follow_sets()
        
        # 重新构建分析表
        self.parsing_table = {}
        self.build_parsing_table()
        
        # 检查转换后的文法是否是LL(1)文法
        if not self.is_ll1_grammar():
            return False, "无法将文法转换为LL(1)文法"
        
        return True, "文法已成功转换为LL(1)文法"
    
    def eliminate_left_recursion(self):
        """消除左递归"""
        has_left_recursion = False
        non_terminals = list(self.grammar.keys())
        
        # 按照特定顺序处理非终结符
        for i, A in enumerate(non_terminals):
            # 消除间接左递归
            for j in range(i):
                B = non_terminals[j]
                new_productions = []
                
                for production in self.grammar[A]:
                    if production and production[0] == B:
                        # 如果产生式以B开头，用B的所有产生式替换
                        for b_production in self.grammar[B]:
                            if b_production == 'ε':
                                new_productions.append(production[1:])
                            else:
                                new_productions.append(b_production + production[1:])
                    else:
                        new_productions.append(production)
                
                self.grammar[A] = new_productions
            
            # 消除直接左递归
            alpha_productions = []  # 不以A开头的产生式
            beta_productions = []   # 以A开头的产生式
            
            for production in self.grammar[A]:
                if production and production[0] == A:
                    has_left_recursion = True
                    beta_productions.append(production[1:])
                else:
                    alpha_productions.append(production)
            
            if beta_productions:  # 存在直接左递归
                new_non_terminal = A + "'"
                while new_non_terminal in self.non_terminals:
                    new_non_terminal += "'"
                
                # 创建A的新产生式
                new_A_productions = []
                for alpha in alpha_productions:
                    if alpha == 'ε':
                        new_A_productions.append(new_non_terminal)
                    else:
                        new_A_productions.append(alpha + new_non_terminal)
                
                # 创建A'的产生式
                new_A_prime_productions = ['ε']
                for beta in beta_productions:
                    if beta == 'ε':
                        new_A_prime_productions.append(new_non_terminal)
                    else:
                        new_A_prime_productions.append(beta + new_non_terminal)
                
                # 更新文法
                self.grammar[A] = new_A_productions
                self.grammar[new_non_terminal] = new_A_prime_productions
                self.non_terminals.add(new_non_terminal)
                
                # 记录转换步骤
                self.grammar_transformation_steps.append({
                    'description': f'消除直接左递归 {A}',
                    'grammar': self.grammar_str(self.grammar)
                })
        
        return has_left_recursion
    
    def eliminate_backtracking(self):
        """消除回溯（左因子提取）"""
        has_backtracking = False
        changed = True
        
        while changed:
            changed = False
            
            for nt in list(self.non_terminals):
                productions = list(set(self.grammar[nt])) # Use set to remove duplicate productions initially
                self.grammar[nt] = productions # Update grammar with unique productions

                # 按第一个符号分组
                grouped_productions = {}
                for prod in productions:
                    first_sym, _ = self.get_first_symbol(prod)
                    if first_sym is None and prod == 'ε':
                        first_sym = 'ε' # 特殊处理ε产生式

                    if first_sym is not None:
                        if first_sym not in grouped_productions:
                            grouped_productions[first_sym] = []
                        grouped_productions[first_sym].append(prod)

                # 检查是否有需要提取左因子的情况
                for first_sym, prods in grouped_productions.items():
                    if first_sym == 'ε' or len(prods) <= 1:
                        continue # ε规则或只有一个产生式，无需处理

                    # 找到当前组的最长公共前缀 (基于字符串)
                    common_prefix = self.find_longest_common_prefix(prods)

                    if common_prefix: # 确保找到非空公共前缀
                        has_backtracking = True
                        changed = True

                        # 创建新的非终结符
                        new_non_terminal = nt + "_"
                        while new_non_terminal in self.non_terminals:
                            new_non_terminal += "_"

                        # 更新原文法规则:
                        # 1. 移除所有以此公共前缀开头的产生式
                        # 2. 添加一条指向新非终结符的产生式
                        new_productions_for_nt = [p for p in productions if not p.startswith(common_prefix)]
                        new_productions_for_nt.append(common_prefix + new_non_terminal)

                        # 创建新非终结符的产生式:
                        # 对于每个以此公共前缀开头的原产生式，取其后缀作为新产生式
                        # 如果原产生式就是公共前缀本身，则添加ε
                        new_nt_productions = []
                        for prod in prods: # 只处理当前组共享前缀的产生式
                            suffix = prod[len(common_prefix):]
                            if not suffix:
                                new_nt_productions.append('ε')
                            else:
                                new_nt_productions.append(suffix)

                        # 更新文法
                        self.grammar[nt] = list(set(new_productions_for_nt)) # 去重
                        self.grammar[new_non_terminal] = list(set(new_nt_productions)) # 去重 (特别是ε)
                        self.non_terminals.add(new_non_terminal)

                        # 记录转换步骤
                        self.grammar_transformation_steps.append({
                            'description': f'提取左因子 {nt} 的公共前缀 {common_prefix}',
                            'grammar': self.grammar_str(self.grammar)
                        })

                        # 因为文法已改变，需要重新开始检查当前非终结符 nt
                        # 通过外层 while changed=True 循环来处理
                        # 但为了效率，可以直接跳出内层循环，让外层循环继续
                        break # 跳出对 first_sym 的循环，重新检查 nt

            # 如果在内层循环中发生了改变，外层 while 会继续迭代
            # 如果内层循环对所有 nt 都没有改变，则 changed 保持 False，外层 while 结束

        return has_backtracking
    
    def find_longest_common_prefix(self, productions):
        """找到一组产生式的最长公共前缀"""
        if not productions or 'ε' in productions:
            return ""
        
        # 找到最短的产生式长度
        min_length = min(len(p) for p in productions)
        
        # 找到最长公共前缀
        prefix = ""
        for i in range(min_length):
            char = productions[0][i]
            if all(p[i] == char for p in productions):
                prefix += char
            else:
                break
        
        return prefix
    
    def get_first_symbol(self, production_string):
        """获取产生式字符串的第一个符号（终结符或非终结符）及其长度"""
        if not production_string or production_string == 'ε':
            return None, 0 # 空或ε没有符号

        # 优先匹配最长的非终结符
        sorted_non_terminals = sorted(self.non_terminals, key=len, reverse=True)
        for nt in sorted_non_terminals:
            if production_string.startswith(nt):
                return nt, len(nt)

        # 如果不是非终结符，检查是否为终结符（假设单字符）
        first_char = production_string[0]
        if first_char in self.terminals:
            return first_char, 1
        else:
            # 可能是错误或未定义的符号，但为了鲁棒性，暂时视为一个符号
            # 或者可以在这里抛出错误
            print(f"警告：在产生式 '{production_string}' 中遇到未知起始符号 '{first_char}'")
            return first_char, 1
            # raise ValueError(f"Unknown start symbol '{first_char}' in production '{production_string}'")

    def grammar_str(self, grammar=None):
        """返回文法的字符串表示"""
        if grammar is None:
            grammar = self.grammar
        
        result = ""
        for nt, productions in sorted(grammar.items()):
            productions_str = " | ".join(productions)
            result += f"{nt} -> {productions_str}\n"
        
        return result
    
    def calculate_first_sets(self):
        """计算FIRST集合"""
        # 初始化FIRST集合
        self.first_sets = {}
        for nt in self.non_terminals:
            self.first_sets[nt] = set()
        
        # 对于终结符，FIRST集合就是其自身
        for terminal in self.terminals:
            if terminal != 'ε':  # ε不是终结符的FIRST集
                self.first_sets[terminal] = {terminal}
        
        # 迭代计算，直到FIRST集合不再变化
        changed = True
        while changed:
            changed = False
            
            # 遍历每个非终结符的产生式
            for nt, productions in self.grammar.items():
                for production in productions:
                    # 如果产生式为ε，直接添加到FIRST集
                    if production == 'ε':
                        if 'ε' not in self.first_sets[nt]:
                            self.first_sets[nt].add('ε')
                            changed = True
                        continue
                    
                    # 处理产生式的首符号
                    all_can_derive_epsilon = True
                    
                    for i, symbol in enumerate(production):
                        if symbol in self.terminals:
                            # 如果是终结符，直接添加并停止
                            if symbol not in self.first_sets[nt]:
                                self.first_sets[nt].add(symbol)
                                changed = True
                            all_can_derive_epsilon = False
                            break
                        elif symbol in self.non_terminals:
                            # 如果是非终结符，添加其FIRST集(除了ε)
                            for terminal in self.first_sets.get(symbol, set()):
                                if terminal != 'ε' and terminal not in self.first_sets[nt]:
                                    self.first_sets[nt].add(terminal)
                                    changed = True
                            
                            # 如果该非终结符不能推导出ε，则停止
                            if 'ε' not in self.first_sets.get(symbol, set()):
                                all_can_derive_epsilon = False
                                break
                            
                            # 如果已经到达产生式的最后一个符号，且可以推导出ε，则将ε添加到FIRST集
                            if i == len(production) - 1 and 'ε' in self.first_sets.get(symbol, set()):
                                if 'ε' not in self.first_sets[nt]:
                                    self.first_sets[nt].add('ε')
                                    changed = True
                        else:
                            # 如果是其他字符(可能是未定义的符号)，将其视为终结符
                            if symbol not in self.first_sets[nt]:
                                self.first_sets[nt].add(symbol)
                                changed = True
                            all_can_derive_epsilon = False
                            break
                    
                    # 如果产生式中所有符号都可以推导出ε，则将ε添加到FIRST集
                    if all_can_derive_epsilon and production and 'ε' not in self.first_sets[nt]:
                        self.first_sets[nt].add('ε')
                        changed = True
                        
    def calculate_follow_sets(self):
        """计算FOLLOW集合"""
        # 初始化FOLLOW集合
        self.follow_sets = {}
        for nt in self.non_terminals:
            self.follow_sets[nt] = set()
        
        # 将#添加到开始符号(第一个非终结符)的FOLLOW集中
        start_symbol = next(iter(self.grammar.keys()))
        self.follow_sets[start_symbol].add('#')
        
        # 迭代计算，直到FOLLOW集合不再变化
        changed = True
        while changed:
            changed = False
            
            # 遍历每个产生式
            for nt, productions in self.grammar.items():
                for production in productions:
                    if production == 'ε':
                        continue
                    
                    # 分析产生式中的每个位置
                    pos = 0
                    while pos < len(production):
                        # 查找非终结符
                        found_nt = None
                        for candidate_nt in sorted(self.non_terminals, key=len, reverse=True):
                            if pos <= len(production) - len(candidate_nt) and production[pos:pos+len(candidate_nt)] == candidate_nt:
                                found_nt = candidate_nt
                                break
                        
                        if not found_nt:
                            # 如果不是非终结符，移到下一个位置
                            pos += 1
                            continue
                        
                        # 找到非终结符，计算其FOLLOW集
                        nt_end_pos = pos + len(found_nt)
                        
                        # 如果非终结符后面还有字符
                        if nt_end_pos < len(production):
                            # 计算后续符号组成的子串的FIRST集
                            beta = production[nt_end_pos:]
                            beta_first = self.get_production_first(beta)
                            
                            # 将beta的FIRST集(除ε外)添加到非终结符的FOLLOW集
                            for terminal in beta_first:
                                if terminal != 'ε' and terminal not in self.follow_sets[found_nt]:
                                    self.follow_sets[found_nt].add(terminal)
                                    changed = True
                            
                            # 如果beta可以推导出ε，将左侧非终结符的FOLLOW集添加到found_nt的FOLLOW集
                            if 'ε' in beta_first:
                                for terminal in self.follow_sets[nt]:
                                    if terminal not in self.follow_sets[found_nt]:
                                        self.follow_sets[found_nt].add(terminal)
                                        changed = True
                        
                        # 如果非终结符是产生式的最后一个符号
                        else:
                            # 将左侧非终结符的FOLLOW集添加到非终结符的FOLLOW集
                            for terminal in self.follow_sets[nt]:
                                if terminal not in self.follow_sets[found_nt]:
                                    self.follow_sets[found_nt].add(terminal)
                                    changed = True
                        
                        # 移动到下一个位置
                        pos = nt_end_pos
    
    def build_parsing_table(self):
        # 初始化预测分析表
        self.parsing_table = {}
        for nt in self.non_terminals:
            self.parsing_table[nt] = {}
        
        # 填充预测分析表
        for nt, productions in self.grammar.items():
            for production in productions:
                # 计算产生式的FIRST集合
                production_first = self.get_production_first(production)
                
                # 对于产生式的FIRST集中的每个终结符(除ε外)，将产生式填入表中
                for terminal in production_first:
                    if terminal != 'ε':
                        if terminal in self.parsing_table[nt]:
                            # 如果已有产生式，说明产生了冲突，这里选择保留新的产生式
                            # 在实际应用中，应向用户报告冲突
                            print(f"警告: 预测分析表冲突在 M[{nt}, {terminal}], 覆盖 {self.parsing_table[nt][terminal]} 为 {production}")
                        self.parsing_table[nt][terminal] = production
                
                # 如果产生式的FIRST集包含ε，则对于FOLLOW集中的每个终结符，也将产生式填入表中
                if 'ε' in production_first:
                    for terminal in self.follow_sets.get(nt, []):
                        if terminal in self.parsing_table[nt]:
                            # 冲突处理
                            print(f"警告: 预测分析表冲突在 M[{nt}, {terminal}], 覆盖 {self.parsing_table[nt][terminal]} 为 {production}")
                        self.parsing_table[nt][terminal] = production
    
    def get_production_first(self, production):
        """计算产生式的FIRST集合"""
        if production == 'ε':
            return {'ε'}
        
        result = set()
        
        # 找到产生式的第一个符号（可能是多字符的非终结符）
        i = 0
        while i < len(production):
            is_non_terminal = False
            
            # 检查是否匹配多字符非终结符
            for nt in sorted(self.non_terminals, key=len, reverse=True):
                if i <= len(production) - len(nt) and production[i:i+len(nt)] == nt:
                    # 找到了非终结符
                    symbol_first = self.first_sets.get(nt, set())
                    
                    # 添加FIRST集（除了ε）
                    for terminal in symbol_first:
                        if terminal != 'ε':
                            result.add(terminal)
                    
                    # 如果该非终结符不能推导出ε，停止
                    if 'ε' not in symbol_first:
                        return result
                    
                    # 如果已经到产生式末尾，添加ε
                    if i + len(nt) >= len(production):
                        result.add('ε')
                        return result
                    
                    # 继续检查下一个符号
                    i += len(nt)
                    is_non_terminal = True
                    break
            
            # 如果当前字符不是非终结符的开始
            if not is_non_terminal:
                if production[i] in self.terminals:
                    result.add(production[i])
                else:
                    # 未知符号，视为终结符
                    result.add(production[i])
                return result
        
        return result
    
    def tokenize_production(self, production_string):
        """Tokenizes a production string into a list of terminals and non-terminals."""
        if production_string == 'ε':
            return [] # Empty list for epsilon

        tokens = []
        pos = 0
        # Sort non-terminals by length descending to match longest first (e.g., S' before S)
        sorted_non_terminals = sorted(self.non_terminals, key=len, reverse=True)

        while pos < len(production_string):
            found_symbol = None

            # Check for non-terminals first (longest match)
            for nt in sorted_non_terminals:
                if production_string.startswith(nt, pos):
                    found_symbol = nt
                    break

            # If not a non-terminal, check for terminals (assuming single char terminals for now)
            if found_symbol is None:
                symbol = production_string[pos]
                if symbol in self.terminals:
                    found_symbol = symbol
                else:
                    # This case indicates an issue with the grammar or table generation
                    raise ValueError(f"Unknown symbol '{symbol}' encountered in production '{production_string}' at position {pos}")

            if found_symbol:
                tokens.append(found_symbol)
                pos += len(found_symbol)
            else:
                 # Should not happen if logic above is correct
                 raise ValueError(f"Failed to tokenize production '{production_string}' at position {pos}")


        return tokens
    
    def get_first_sets_str(self):
        result = "FIRST集合:\n\n"
        for nt in sorted(self.non_terminals):
            result += f"FIRST({nt}) = {{{', '.join(sorted(self.first_sets[nt]))}}}\n"
        return result
    
    def get_follow_sets_str(self):
        result = "FOLLOW集合:\n\n"
        for nt in sorted(self.non_terminals):
            result += f"FOLLOW({nt}) = {{{', '.join(sorted(self.follow_sets[nt]))}}}\n"
        return result
    
    def get_parsing_table_str(self):
        result = "预测分析表:\n\n"
        terminals = sorted([t for t in self.terminals if t != 'ε'] + ['#'])
        
        # 表头
        result += f"{'非终结符':<15}"
        for terminal in terminals:
            result += f"{terminal:<15}"
        result += "\n"
        
        # 分隔线
        result += "-" * (15 * (len(terminals) + 1)) + "\n"
        
        # 表内容
        for nt in sorted(self.non_terminals):
            result += f"{nt:<15}"
            for terminal in terminals:
                if terminal in self.parsing_table[nt]:
                    result += f"{nt}->{self.parsing_table[nt][terminal]:<15}"
                else:
                    result += f"{'空':<15}"
            result += "\n"
        
        return result
        
    def parse(self, input_string):
        # 获取起始符号（假设是第一个非终结符）
        start_symbol = next(iter(self.grammar.keys()))
        
        # 重置分析栈和步骤
        self.stack = ['#', start_symbol]  # 初始栈，#在底，S在顶
        input_tokens = list(input_string) # 输入串
        self.steps = []
        
        step_count = 0
        
        # 记录初始状态 (栈顶在右侧显示)
        self.steps.append({
            'step': step_count,
            'stack': ' '.join(self.stack), # 栈底到栈顶
            'input': input_string,
            'production': '',
            'action': '初始化'
        })
        
        i = 0  # 输入串指针
        
        while True: # Loop until success or error return
            step_count += 1

            # 检查栈是否为空 (理论上不应在匹配 # 之前发生)
            if not self.stack:
                # This indicates an error state not caught earlier
                action = "错误：分析栈意外为空"
                self.steps.append({
                    'step': step_count,
                    'stack': '(栈空)',
                    'input': ''.join(input_tokens[i:]) if i < len(input_tokens) else '#',
                    'production': '错误',
                    'action': action
                })
                return False, action

            # 获取栈顶元素
            top = self.stack[-1]

            # 获取当前输入符号
            current_symbol = input_tokens[i] if i < len(input_tokens) else '#'

            # --- 准备记录当前步骤的状态 (在执行动作之前) ---
            current_stack_str = ' '.join(self.stack) # 栈底到栈顶
            remaining_input_str = ''.join(input_tokens[i:]) if i < len(input_tokens) else '#'
            action = ''
            production_used = ''
            # --- 状态准备完毕 ---

            # 情况 1: 栈顶是终结符或#
            if top in self.terminals or top == '#':
                if top == current_symbol:  # 匹配成功
                    if top == '#': # 分析成功结束
                        action = "匹配! POP #. 分析成功"
                        production_used = '#'
                        # 记录最终成功步骤
                        self.steps.append({
                            'step': step_count,
                            'stack': current_stack_str, # 记录包含#的栈
                            'input': remaining_input_str, # 记录包含#的输入
                            'production': production_used,
                            'action': action
                        })
                        self.stack.pop() # 弹出#
                        return True, "分析成功"
                    else: # 匹配中间终结符
                        action = f"匹配! POP {top}, 输入指针后移 (i++)"
                        production_used = ''
                        # 记录匹配步骤
                        self.steps.append({
                            'step': step_count,
                            'stack': current_stack_str,
                            'input': remaining_input_str,
                            'production': production_used,
                            'action': action
                        })
                        # 执行动作
                        self.stack.pop()
                        i += 1
                else:  # 匹配失败
                    action = f"错误：栈顶终结符 {top} 与输入 {current_symbol} 不匹配"
                    # 记录错误步骤
                    self.steps.append({
                        'step': step_count,
                        'stack': current_stack_str,
                        'input': remaining_input_str,
                        'production': '错误',
                        'action': action
                    })
                    return False, action

            # 情况 2: 栈顶是非终结符
            else:
                # 查找预测分析表
                if top in self.parsing_table and current_symbol in self.parsing_table[top]:
                    production_right = self.parsing_table[top][current_symbol]
                    production_used = f"{top} -> {production_right}"

                    # 如果不是ε产生式
                    if production_right != 'ε':
                        symbols_to_push = self.tokenize_production(production_right)
                        action = f"POP {top}, PUSH {' '.join(reversed(symbols_to_push))}" # 显示压栈顺序
                        # 记录推导步骤
                        self.steps.append({
                            'step': step_count,
                            'stack': current_stack_str,
                            'input': remaining_input_str,
                            'production': production_used,
                            'action': action
                        })
                        # 执行动作
                        self.stack.pop()
                        for symbol in reversed(symbols_to_push):
                            self.stack.append(symbol)
                    else: # ε 产生式
                        action = f"POP {top} (ε 产生式)"
                        production_used = f"{top} -> ε" # 更明确
                        # 记录ε推导步骤
                        self.steps.append({
                            'step': step_count,
                            'stack': current_stack_str,
                            'input': remaining_input_str,
                            'production': production_used,
                            'action': action
                        })
                        # 执行动作
                        self.stack.pop()
                else: # 分析表查找失败
                    action = f"错误：分析表中没有对应项 ({top}, {current_symbol})"
                    # 记录错误步骤
                    self.steps.append({
                        'step': step_count,
                        'stack': current_stack_str,
                        'input': remaining_input_str,
                        'production': '错误',
                        'action': action
                    })
                    return False, action

            # --- 循环继续 ---

        # 此处代码理论上不应到达，因为循环通过 return 退出
        # 但保留以防万一
        final_stack_str = ' '.join(self.stack) if self.stack else '(栈空)'
        final_input_str = ''.join(input_tokens[i:]) if i < len(input_tokens) else '(输入结束)'
        self.steps.append({
            'step': step_count + 1,
            'stack': final_stack_str,
            'input': final_input_str,
            'production': '错误',
            'action': "错误：分析循环意外终止"
        })
        return False, "错误：分析循环意外终止"

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LL(1)语法分析器")
        self.root.geometry("1200x700")
        
        self.parser = LL1Parser()
        
        # 创建主标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建语法编辑页面
        self.grammar_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.grammar_tab, text="文法编辑")
        
        # 创建分析页面
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="语法分析")
        
        # 创建集合页面
        self.sets_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sets_tab, text="FIRST/FOLLOW集")
        
        # 创建分析表页面
        self.table_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="预测分析表")
        
        # 创建转换过程页面
        self.transformation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transformation_tab, text="文法转换过程")
        
        # 在语法编辑页面创建编辑器
        self.create_grammar_editor(self.grammar_tab)
        
        # 在分析页面创建输入框和按钮
        self.create_input_frame(self.analysis_tab)
        
        # 在分析页面创建结果显示区域
        self.create_output_frame(self.analysis_tab)
        
        # 在集合页面显示FIRST和FOLLOW集
        self.create_sets_frame(self.sets_tab)
        
        # 在分析表页面显示预测分析表
        self.create_table_frame(self.table_tab)
        
        # 在转换过程页面显示文法转换步骤
        self.create_transformation_frame(self.transformation_tab)
        
        # 更新显示当前文法
        self.update_grammar_display()
    
    def create_grammar_editor(self, parent):
        """创建文法编辑界面"""
        # 清空现有内容
        for widget in parent.winfo_children():
            widget.destroy()
            
        grammar_frame = tk.Frame(parent)
        grammar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文法编辑区标题
        tk.Label(grammar_frame, text="输入文法规则 (格式: A->α|β|γ，每行一个非终结符):", anchor="w").pack(fill=tk.X, pady=(0, 5))
        
        # 文法编辑文本框
        self.grammar_text = scrolledtext.ScrolledText(grammar_frame, wrap=tk.WORD, width=80, height=15)
        self.grammar_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 默认填充当前文法
        self.update_grammar_display()
        
        # 终结符输入区
        terminals_frame = tk.Frame(grammar_frame)
        terminals_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(terminals_frame, text="终结符 (用逗号分隔，ε会自动添加):").pack(side=tk.LEFT, padx=(0, 5))
        self.terminals_entry = tk.Entry(terminals_frame, width=50)
        self.terminals_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 设置默认终结符
        terminals_str = ",".join(sorted([t for t in self.parser.terminals if t != 'ε']))
        self.terminals_entry.insert(0, terminals_str)
        
        # 按钮区
        button_frame = tk.Frame(grammar_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="应用文法", command=self.apply_grammar).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="检查LL(1)", command=self.check_ll1).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="转换为LL(1)", command=self.convert_to_ll1).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="重置为默认文法", command=self.reset_to_default).pack(side=tk.LEFT, padx=5)
        
        # 文法检查结果显示区
        tk.Label(grammar_frame, text="文法检查结果:", anchor="w").pack(fill=tk.X, pady=(10, 5))
        
        self.grammar_check_text = scrolledtext.ScrolledText(grammar_frame, wrap=tk.WORD, width=80, height=10)
        self.grammar_check_text.pack(fill=tk.BOTH, expand=True)
    
    def update_grammar_display(self):
        """更新显示当前文法"""
        self.grammar_text.delete(1.0, tk.END)
        
        # 格式化文法规则
        for nt, productions in sorted(self.parser.grammar.items()):
            productions_str = " | ".join(productions)
            self.grammar_text.insert(tk.END, f"{nt} -> {productions_str}\n")
    
    def parse_grammar_input(self):
        """解析用户输入的文法"""
        grammar_text = self.grammar_text.get(1.0, tk.END).strip()
        grammar = {}
        
        for line in grammar_text.split('\n'):
            if not line.strip() or '->' not in line:
                continue
            
            parts = line.split('->')
            if len(parts) != 2:
                return None, f"格式错误: {line}，应为 'A->α|β|γ'"
            
            nt = parts[0].strip()
            productions_str = parts[1].strip()
            
            productions = [p.strip() for p in productions_str.split('|')]
            grammar[nt] = productions
        
        # 解析终结符
        terminals_str = self.terminals_entry.get().strip()
        terminals = set([t.strip() for t in terminals_str.split(',') if t.strip()])
        terminals.add('ε')  # 确保ε总是在终结符集合中
        
        return grammar, terminals
    
    def apply_grammar(self):
        """应用用户输入的文法"""
        try:
            grammar, terminals = self.parse_grammar_input()
            if grammar is None:
                messagebox.showerror("错误", terminals)  # terminals此时包含错误信息
                return
            
            # 更新解析器的文法
            self.parser.set_grammar(grammar, terminals)
            
            # 更新UI
            self.update_all_tabs()
            
            messagebox.showinfo("成功", "文法已成功应用")
        except Exception as e:
            messagebox.showerror("错误", f"应用文法时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())  # 打印详细错误信息到控制台
    
    def check_ll1(self):
        """检查当前文法是否是LL(1)文法"""
        is_ll1 = self.parser.is_ll1_grammar()
        
        self.grammar_check_text.delete(1.0, tk.END)
        
        if is_ll1:
            self.grammar_check_text.insert(tk.END, "当前文法是LL(1)文法。\n")
        else:
            self.grammar_check_text.insert(tk.END, "当前文法不是LL(1)文法。以下是冲突:\n\n")
            
            for conflict in self.parser.conflicts:
                nt = conflict['non_terminal']
                terminal = conflict['terminal']
                prod1 = conflict['production1']
                prod2 = conflict['production2']
                
                self.grammar_check_text.insert(tk.END, f"非终结符 {nt} 遇到 {terminal} 时有冲突:\n")
                self.grammar_check_text.insert(tk.END, f"  产生式1: {nt} -> {prod1}\n")
                self.grammar_check_text.insert(tk.END, f"  产生式2: {nt} -> {prod2}\n\n")
    
    def convert_to_ll1(self):
        """将当前文法转换为LL(1)文法"""
        try:
            success, message = self.parser.convert_to_ll1()
            
            if success:
                # 更新所有标签页
                self.update_all_tabs()
                
                # 显示转换消息
                self.grammar_check_text.delete(1.0, tk.END)
                self.grammar_check_text.insert(tk.END, message + "\n\n")
                
                if len(self.parser.grammar_transformation_steps) > 1:  # 如果有转换步骤
                    self.grammar_check_text.insert(tk.END, "文法已成功转换，请查看\"文法转换过程\"标签页了解详细步骤。\n")
                    
                    # 切换到转换过程标签页
                    self.notebook.select(self.transformation_tab)
                
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
        except Exception as e:
            messagebox.showerror("错误", f"转换文法时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())  # 打印详细错误信息到控制台
    
    def reset_to_default(self):
        """重置为默认文法"""
        default_grammar = {
            'E': ['TG'],
            'G': ['+TG', '-TG', 'ε'],
            'T': ['FS'],
            'S': ['*FS', '/FS', 'ε'],
            'F': ['(E)', 'i']
        }
        
        default_terminals = set(['+', '-', '*', '/', '(', ')', 'i', 'ε'])
        
        # 更新解析器的文法
        self.parser.set_grammar(default_grammar, default_terminals)
        
        # 更新终结符输入框
        self.terminals_entry.delete(0, tk.END)
        self.terminals_entry.insert(0, "+,-,*,/,(,),i")
        
        # 更新UI
        self.update_all_tabs()
        
        messagebox.showinfo("成功", "已重置为默认文法")
    
    def update_all_tabs(self):
        """更新所有标签页的内容"""
        self.update_grammar_display()
        self.create_sets_frame(self.sets_tab)
        self.create_table_frame(self.table_tab)
        self.create_transformation_frame(self.transformation_tab)
    
    def create_transformation_frame(self, parent):
        """创建文法转换过程显示界面"""
        # 清空现有内容
        for widget in parent.winfo_children():
            widget.destroy()
        
        transformation_frame = tk.Frame(parent)
        transformation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if not self.parser.grammar_transformation_steps:
            tk.Label(transformation_frame, text="未进行文法转换或当前文法已经是LL(1)文法。", anchor="w").pack(fill=tk.X)
            return
        
        # 创建转换步骤显示区
        tk.Label(transformation_frame, text="文法转换步骤:", anchor="w", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(0, 10))
        
        for i, step in enumerate(self.parser.grammar_transformation_steps):
            step_frame = tk.Frame(transformation_frame, relief=tk.RIDGE, bd=1)
            step_frame.pack(fill=tk.X, pady=5)
            
            # 步骤标题
            tk.Label(step_frame, text=f"步骤 {i+1}: {step['description']}", anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X, padx=5, pady=5)
            
            # 步骤内容 - 使用文本框显示文法
            step_text = scrolledtext.ScrolledText(step_frame, wrap=tk.WORD, width=80, height=8)
            step_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            step_text.insert(tk.END, step['grammar'])
            step_text.config(state=tk.DISABLED)  # 设为只读

    def create_input_frame(self, parent):
        input_frame = tk.Frame(parent)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="输入表达式:").grid(row=0, column=0, padx=5, pady=5)
        self.expression_entry = tk.Entry(input_frame, width=30)
        self.expression_entry.grid(row=0, column=1, padx=5, pady=5)
        self.expression_entry.insert(0, "i+i*i#")
        
        self.check_grammar_var = tk.BooleanVar(value=True)
        self.check_grammar_checkbox = tk.Checkbutton(input_frame, text="检查并转换表达式",
                                                     variable=self.check_grammar_var)
        self.check_grammar_checkbox.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Button(input_frame, text="分析", command=self.analyze).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(input_frame, text="清空", command=self.clear).grid(row=0, column=4, padx=5, pady=5)
    
    def create_output_frame(self, parent):
        output_frame = tk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格框架
        table_view_frame = tk.Frame(output_frame)
        table_view_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建表格标题
        headers = ["步骤", "分析栈", "剩余输入串", "所用产生式", "动作"]
        widths = [5, 20, 15, 25, 35]
        for i, header in enumerate(headers):
            tk.Label(table_view_frame, text=header, relief=tk.RIDGE, width=widths[i]).grid(row=0, column=i, sticky=tk.NSEW)
        
        # 创建分析结果表格框架，用于在分析后填充
        self.analysis_table_frame = tk.Frame(output_frame)
        self.analysis_table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本框用于显示分析详情
        detail_label = tk.Label(output_frame, text="分析过程详情:", anchor="w")
        detail_label.pack(fill=tk.X, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=100, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def create_sets_frame(self, parent):
        """创建FIRST和FOLLOW集显示界面"""
        # 清空现有内容
        for widget in parent.winfo_children():
            widget.destroy()
            
        sets_frame = tk.Frame(parent)
        sets_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建FIRST集表格
        first_label = tk.Label(sets_frame, text="FIRST集:", anchor="w", font=("Arial", 10, "bold"))
        first_label.pack(fill=tk.X, pady=(0, 5))
        
        first_frame = tk.Frame(sets_frame)
        first_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # FIRST集表头
        tk.Label(first_frame, text="非终结符", relief=tk.RIDGE, width=15).grid(row=0, column=0, sticky=tk.NSEW)
        tk.Label(first_frame, text="FIRST集合", relief=tk.RIDGE, width=40).grid(row=0, column=1, sticky=tk.NSEW)
        
        # FIRST集内容
        for i, nt in enumerate(sorted(self.parser.non_terminals)):
            tk.Label(first_frame, text=nt, relief=tk.RIDGE, width=15).grid(row=i+1, column=0, sticky=tk.NSEW)
            first_set = '{' + ', '.join(sorted(self.parser.first_sets.get(nt, []))) + '}'
            tk.Label(first_frame, text=first_set, relief=tk.RIDGE, width=40, anchor="w").grid(row=i+1, column=1, sticky=tk.NSEW)
        
        # 创建FOLLOW集表格
        follow_label = tk.Label(sets_frame, text="FOLLOW集:", anchor="w", font=("Arial", 10, "bold"))
        follow_label.pack(fill=tk.X, pady=(10, 5))
        
        follow_frame = tk.Frame(sets_frame)
        follow_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # FOLLOW集表头
        tk.Label(follow_frame, text="非终结符", relief=tk.RIDGE, width=15).grid(row=0, column=0, sticky=tk.NSEW)
        tk.Label(follow_frame, text="FOLLOW集合", relief=tk.RIDGE, width=40).grid(row=0, column=1, sticky=tk.NSEW)
        
        # FOLLOW集内容
        for i, nt in enumerate(sorted(self.parser.non_terminals)):
            tk.Label(follow_frame, text=nt, relief=tk.RIDGE, width=15).grid(row=i+1, column=0, sticky=tk.NSEW)
            follow_set = '{' + ', '.join(sorted(self.parser.follow_sets.get(nt, []))) + '}'
            tk.Label(follow_frame, text=follow_set, relief=tk.RIDGE, width=40, anchor="w").grid(row=i+1, column=1, sticky=tk.NSEW)
        
        # 文本显示区
        text_label = tk.Label(sets_frame, text="FIRST和FOLLOW集的文本表示:", anchor="w")
        text_label.pack(fill=tk.X, pady=(10, 5))
        
        self.sets_text = scrolledtext.ScrolledText(sets_frame, wrap=tk.WORD, width=100, height=10)
        self.sets_text.pack(fill=tk.BOTH, expand=True)
        
        # 填充FIRST集和FOLLOW集的文本表示
        first_sets_str = self.parser.get_first_sets_str()
        follow_sets_str = self.parser.get_follow_sets_str()
        
        self.sets_text.insert(tk.END, first_sets_str + "\n\n" + follow_sets_str)
    
    def create_table_frame(self, parent):
        """创建预测分析表显示界面"""
        # 清空现有内容
        for widget in parent.winfo_children():
            widget.destroy()
            
        table_frame = tk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格形式显示预测分析表
        table_view_frame = tk.Frame(table_frame)
        table_view_frame.pack(fill=tk.BOTH, expand=True)
        
        # 获取终结符列表（不包括ε，但包括#）
        terminals = sorted([t for t in self.parser.terminals if t != 'ε'] + ['#'])
        
        # 创建表头
        tk.Label(table_view_frame, text="非终结符", relief=tk.RIDGE, width=15).grid(row=0, column=0, sticky=tk.NSEW)
        for i, terminal in enumerate(terminals):
            tk.Label(table_view_frame, text=terminal, relief=tk.RIDGE, width=15).grid(row=0, column=i+1, sticky=tk.NSEW)
        
        # 创建表内容
        for i, nt in enumerate(sorted(self.parser.non_terminals)):
            tk.Label(table_view_frame, text=nt, relief=tk.RIDGE, width=15).grid(row=i+1, column=0, sticky=tk.NSEW)
            for j, terminal in enumerate(terminals):
                content = ""
                if nt in self.parser.parsing_table and terminal in self.parser.parsing_table[nt]:
                    content = f"{nt}->{self.parser.parsing_table[nt][terminal]}"
                else:
                    content = "空"
                tk.Label(table_view_frame, text=content, relief=tk.RIDGE, width=15).grid(row=i+1, column=j+1, sticky=tk.NSEW)
        
        # 设置表格可滚动
        table_scroll_frame = tk.Frame(table_frame)
        table_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        explanation_label = tk.Label(table_scroll_frame, text="预测分析表的文本表示:", anchor="w")
        explanation_label.pack(fill=tk.X)
        
        self.table_text = scrolledtext.ScrolledText(table_scroll_frame, wrap=tk.WORD, width=100, height=10)
        self.table_text.pack(fill=tk.BOTH, expand=True)
        
        # 填充预测分析表的文本表示
        parsing_table_str = self.parser.get_parsing_table_str()
        self.table_text.insert(tk.END, parsing_table_str)
    
    def analyze(self):
        """分析输入表达式"""
        try:
            expression = self.expression_entry.get().strip()
            if not expression:
                messagebox.showerror("错误", "请输入表达式")
                return
            
            # 清空上次的分析结果
            self.output_text.delete(1.0, tk.END)
            
            # 清空分析表格
            for widget in self.analysis_table_frame.winfo_children():
                widget.destroy()
            
            # 如果需要检查文法
            if self.check_grammar_var.get():
                is_ll1 = self.parser.is_ll1_grammar()
                if not is_ll1:
                    self.output_text.insert(tk.END, "当前文法不是LL(1)文法，尝试转换...\n\n")
                    success, message = self.parser.convert_to_ll1()
                    if success:
                        self.output_text.insert(tk.END, f"{message}\n\n")
                        # 更新所有UI显示
                        self.update_all_tabs()
                    else:
                        messagebox.showerror("错误", message)
                        return
            
            # 确保表达式以#结尾
            if not expression.endswith('#'):
                expression += '#'
                self.expression_entry.delete(0, tk.END)
                self.expression_entry.insert(0, expression)
            
            # 检查输入表达式中的终结符是否都在文法的终结符集合中
            invalid_tokens = []
            for token in expression:
                if token != '#' and token not in self.parser.terminals and token != 'ε':
                    invalid_tokens.append(token)
            
            if invalid_tokens:
                messagebox.showerror("错误", f"表达式中包含未定义的终结符: {', '.join(invalid_tokens)}")
                return
            
            # 分析表达式
            success, message = self.parser.parse(expression)
            
            if not success:
                messagebox.showerror("分析失败", message)
                self.output_text.insert(tk.END, f"分析失败: {message}\n")
                return
            
            # 将分析步骤显示在表格中
            for i, step in enumerate(self.parser.steps):
                tk.Label(self.analysis_table_frame, text=step['step'], relief=tk.RIDGE, width=5).grid(row=i, column=0, sticky=tk.NSEW)
                tk.Label(self.analysis_table_frame, text=step['stack'], relief=tk.RIDGE, width=20, anchor='w').grid(row=i, column=1, sticky=tk.NSEW)
                tk.Label(self.analysis_table_frame, text=step['input'], relief=tk.RIDGE, width=15, anchor='w').grid(row=i, column=2, sticky=tk.NSEW)
                tk.Label(self.analysis_table_frame, text=step['production'], relief=tk.RIDGE, width=25, anchor='w').grid(row=i, column=3, sticky=tk.NSEW)
                tk.Label(self.analysis_table_frame, text=step['action'], relief=tk.RIDGE, width=35, anchor='w').grid(row=i, column=4, sticky=tk.NSEW)
            
            # 在文本框中显示详细信息 (格式化输出)
            header = f"{'步骤':<5}\t{'分析栈':<25}\t{'剩余输入串':<20}\t{'所用产生式':<25}\t{'动作'}\n"
            separator = "-" * (len(header) + 10) + "\n" # Adjust length as needed
            self.output_text.insert(tk.END, header)
            self.output_text.insert(tk.END, separator)

            for step in self.parser.steps:
                # Format each part for alignment
                step_str = f"{step['step']:<5}"
                stack_str = f"{step['stack']:<25}"
                input_str = f"{step['input']:<20}"
                prod_str = f"{step['production']:<25}"
                action_str = f"{step['action']}" # Action takes remaining space
                line = f"{step_str}\t{stack_str}\t{input_str}\t{prod_str}\t{action_str}\n"
                self.output_text.insert(tk.END, line)

            self.output_text.insert(tk.END, "\n" + message) # Append final status message
        except Exception as e:
            messagebox.showerror("错误", f"分析表达式时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())  # 打印详细错误信息到控制台
    
    def clear(self):
        self.expression_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        
        # 清空分析表格
        for widget in self.analysis_table_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop() 