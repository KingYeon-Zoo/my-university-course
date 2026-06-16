import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re
from collections import defaultdict, deque

class Grammar:
    def __init__(self):
        self.productions = []
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
        self.first_sets = {}
        self.follow_sets = {}
        
    def parse_grammar(self, grammar_text):
        self.productions = []
        self.terminals = set()
        self.non_terminals = set()
        
        lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            if '->' not in line:
                continue
                
            left, right = line.split('->', 1)
            left = left.strip()
            self.non_terminals.add(left)
            
            if i == 0:  # 第一条产生式的左部作为开始符号
                self.start_symbol = left
            
            # 处理多个候选式，用|分隔
            for production in right.split('|'):
                production = production.strip()
                self.productions.append((left, production))
                
                # 识别终结符和非终结符
                for symbol in production.split():
                    if symbol and symbol not in self.non_terminals and symbol != 'ε':
                        self.terminals.add(symbol)
        
        # 添加结束符号
        self.terminals.add('$')
        
        # 为文法添加扩展开始符号
        self.productions.insert(0, (f"{self.start_symbol}'", self.start_symbol))
        self.non_terminals.add(f"{self.start_symbol}'")
        self.start_symbol = f"{self.start_symbol}'"
        
        return True
    
    def compute_first_sets(self):
        self.first_sets = {symbol: set() for symbol in self.terminals | self.non_terminals}
        
        # 终结符的FIRST集就是自身
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}
        
        # 空字符串ε的FIRST集就是它自己
        if 'ε' in self.terminals:
            self.first_sets['ε'] = {'ε'}
        
        # 计算非终结符的FIRST集
        changed = True
        while changed:
            changed = False
            for left, right in self.productions:
                if not right or right == 'ε':  # 空产生式
                    if 'ε' not in self.first_sets[left]:
                        self.first_sets[left].add('ε')
                        changed = True
                    continue
                
                symbols = right.split()
                all_can_derive_epsilon = True
                
                for i, symbol in enumerate(symbols):
                    if symbol in self.terminals:
                        if symbol not in self.first_sets[left]:
                            self.first_sets[left].add(symbol)
                            changed = True
                        all_can_derive_epsilon = False
                        break
                    
                    # 将当前符号的FIRST集中除了ε之外的所有符号加入到left的FIRST集
                    for terminal in self.first_sets[symbol] - {'ε'}:
                        if terminal not in self.first_sets[left]:
                            self.first_sets[left].add(terminal)
                            changed = True
                    
                    # 如果当前符号不能推导出ε，那么就停止
                    if 'ε' not in self.first_sets[symbol]:
                        all_can_derive_epsilon = False
                        break
                
                # 如果所有符号都能推导出ε，那么left也能推导出ε
                if all_can_derive_epsilon and 'ε' not in self.first_sets[left]:
                    self.first_sets[left].add('ε')
                    changed = True
    
    def first_of_string(self, symbols):
        if not symbols:
            return {'ε'}
        
        symbols_list = symbols.split()
        if not symbols_list:
            return {'ε'}
        
        result = set()
        all_derive_epsilon = True
        
        for symbol in symbols_list:
            if symbol in self.terminals:
                result.add(symbol)
                all_derive_epsilon = False
                break
            
            # 将当前非终结符的FIRST集中非ε的符号添加到结果集中
            for terminal in self.first_sets[symbol] - {'ε'}:
                result.add(terminal)
            
            # 如果当前符号不能推导出ε，则不再继续计算后续符号
            if 'ε' not in self.first_sets[symbol]:
                all_derive_epsilon = False
                break
        
        # 如果所有符号都能推导出ε，则结果集中应包含ε
        if all_derive_epsilon:
            result.add('ε')
            
        return result
    
    def compute_follow_sets(self):
        self.follow_sets = {nt: set() for nt in self.non_terminals}
        
        # 初始化开始符号的FOLLOW集，包含$
        self.follow_sets[self.start_symbol] = {'$'}
        
        changed = True
        while changed:
            changed = False
            for left, right in self.productions:
                if not right or right == 'ε':
                    continue
                    
                symbols = right.split()
                
                for i, symbol in enumerate(symbols):
                    if symbol in self.non_terminals:
                        # 计算symbol后面的符号串的FIRST集
                        rest = ' '.join(symbols[i+1:])
                        first_of_rest = self.first_of_string(rest)
                        
                        # 将除ε外的所有符号加入FOLLOW(symbol)
                        for terminal in first_of_rest - {'ε'}:
                            if terminal not in self.follow_sets[symbol]:
                                self.follow_sets[symbol].add(terminal)
                                changed = True
                        
                        # 如果FIRST(rest)包含ε或rest为空，则FOLLOW(left)中的所有符号也属于FOLLOW(symbol)
                        if 'ε' in first_of_rest or not rest:
                            for terminal in self.follow_sets[left]:
                                if terminal not in self.follow_sets[symbol]:
                                    self.follow_sets[symbol].add(terminal)
                                    changed = True

class LR1Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.action_table = {}
        self.goto_table = {}
        self.canonical_collection = []
        self.build_parsing_table()
    
    def build_parsing_table(self):
        # 构建项目集规范族
        self.build_canonical_collection()
        
        # 初始化action和goto表
        self.action_table = {}
        self.goto_table = {}
        
        # 调试日志：打印所有项目集规范族
        print("\n===== 开始构建分析表 =====")
        
        # 首先遍历所有状态，确保先处理所有移进动作(shift)
        for i, state in enumerate(self.canonical_collection):
            # 用于检测潜在的移进/归约冲突
            shift_actions = {}
            
            # 先处理所有可能的移进操作
            for item in state:
                production, dot_pos, lookahead = item
                left, right = production
                
                # 处理ε产生式
                if right == 'ε':
                    symbols = []
                else:
                    symbols = right.split()
                
                # 如果点不在末尾，可能有移进动作
                if dot_pos < len(symbols):
                    next_symbol = symbols[dot_pos]
                    
                    # 只处理终结符的移进
                    if next_symbol in self.grammar.terminals:
                        goto_state = self.goto(i, next_symbol)
                        if goto_state is not None:
                            shift_actions[next_symbol] = goto_state
                            self.action_table[(i, next_symbol)] = ('shift', goto_state)
                            print(f"添加移进: ACTION[{i}, {next_symbol}] = shift {goto_state}")
            
            # 再处理所有非终结符的goto操作
            for nt in self.grammar.non_terminals:
                goto_state = self.goto(i, nt)
                if goto_state is not None:
                    self.goto_table[(i, nt)] = goto_state
                    print(f"添加goto: GOTO[{i}, {nt}] = {goto_state}")
            
            # 最后处理所有归约动作(包括接受)
            for item in state:
                production, dot_pos, lookahead = item
                left, right = production
                
                # 处理ε产生式
                if right == 'ε':
                    symbols = []
                else:
                    symbols = right.split()
                
                # 点在末尾，需要归约
                if dot_pos == len(symbols):
                    # 检查是否为增广产生式的接受状态
                    if left == self.grammar.start_symbol and lookahead == '$':
                        self.action_table[(i, '$')] = ('accept', None)
                        print(f"添加接受: ACTION[{i}, $] = accept")
                    else:
                        # 找到对应产生式索引
                        original_right = right if right != '' else 'ε'
                        prod_index = self.grammar.productions.index((left, original_right))
                        
                        # 处理潜在的移进/归约冲突
                        if (i, lookahead) in self.action_table:
                            current_action = self.action_table[(i, lookahead)]
                            if current_action[0] == 'shift':
                                print(f"移进/归约冲突: 状态{i}, 符号{lookahead}")
                                print(f"  当前: {current_action}")
                                print(f"  新动作: reduce {prod_index} ({left} -> {original_right})")
                                # 默认解决方案：保留移进动作
                                print(f"  解决: 保留移进动作")
                                continue  # 跳过添加这个归约动作
                            elif current_action[0] == 'reduce':
                                # 归约/归约冲突
                                print(f"归约/归约冲突: 状态{i}, 符号{lookahead}")
                                print(f"  当前: {current_action}")
                                print(f"  新动作: reduce {prod_index} ({left} -> {original_right})")
                                # 简单规则：保留产生式编号较小的归约动作
                                if current_action[1] < prod_index:
                                    print(f"  解决: 保留原归约动作")
                                    continue
                                print(f"  解决: 使用新归约动作")
                        
                        # 添加归约动作
                        self.action_table[(i, lookahead)] = ('reduce', prod_index)
                        print(f"添加归约: ACTION[{i}, {lookahead}] = reduce {prod_index} ({left} -> {original_right})")
        
        # 最后打印完整的分析表
        self.print_parsing_table()
    
    def print_parsing_table(self):
        """打印完整的LR(1)分析表"""
        print("\n===== LR(1)分析表 =====")
        print("ACTION表:")
        
        # 收集所有状态和终结符
        all_states = range(len(self.canonical_collection))
        all_terminals = sorted(list(self.grammar.terminals))
        
        # 打印ACTION表头
        header = "状态 | " + " | ".join(all_terminals)
        print(header)
        print("-" * len(header))
        
        # 打印每个状态的ACTION
        for state in all_states:
            row = f"{state:4d} | "
            for terminal in all_terminals:
                if (state, terminal) in self.action_table:
                    action, value = self.action_table[(state, terminal)]
                    if action == 'shift':
                        cell = f"s{value}"
                    elif action == 'reduce':
                        left, right = self.grammar.productions[value]
                        cell = f"r{value}({left}->{right})"
                    elif action == 'accept':
                        cell = "acc"
                    else:
                        cell = "?"
                else:
                    cell = ""
                row += f"{cell:10s} | "
            print(row)
        
        print("\nGOTO表:")
        # 收集所有非终结符
        all_nonterminals = sorted(list(self.grammar.non_terminals))
        
        # 打印GOTO表头
        header = "状态 | " + " | ".join(all_nonterminals)
        print(header)
        print("-" * len(header))
        
        # 打印每个状态的GOTO
        for state in all_states:
            row = f"{state:4d} | "
            for nt in all_nonterminals:
                if (state, nt) in self.goto_table:
                    value = self.goto_table[(state, nt)]
                    cell = f"{value}"
                else:
                    cell = ""
                row += f"{cell:10s} | "
            print(row)
    
    def closure(self, items):
        """计算项目集的闭包"""
        result = set(items)
        changed = True
        
        while changed:
            changed = False
            new_items = set()
            
            for item in result:
                production, dot_pos, lookahead = item
                left, right = production
                
                # 处理ε产生式
                if right == 'ε':
                    # 如果是[A -> .ε, a]，则认为点在右侧的位置0
                    # 以便于计算后续项目
                    symbols = []
                else:
                    symbols = right.split()
                
                # 如果点已经在末尾，则跳过
                if dot_pos >= len(symbols):
                    continue
                
                # 获取点后面的符号
                next_symbol = symbols[dot_pos]
                
                # 如果下一个符号是非终结符，添加相应的项目
                if next_symbol in self.grammar.non_terminals:
                    # 获取原始项目的展望符 'a'
                    original_lookahead = lookahead

                    # 计算点后面符号串 beta
                    beta_symbols = symbols[dot_pos+1:]
                    
                    # 计算 FIRST(beta)
                    first_beta = self.grammar.first_of_string(' '.join(beta_symbols))

                    # 计算新项目的展望符集合 FIRST(beta + a)
                    # 即 (FIRST(beta) - {ε}) U ({a} if ε in FIRST(beta) else {})
                    new_lookaheads = set()
                    for terminal in first_beta - {'ε'}:
                        new_lookaheads.add(terminal)
                    if 'ε' in first_beta:
                        new_lookaheads.add(original_lookahead)

                    # 添加所有形如 [B -> .γ, b] 的项目, 其中 B 是 next_symbol, b ∈ new_lookaheads
                    for prod_left, prod_right in self.grammar.productions:
                        if prod_left == next_symbol:
                            for la in new_lookaheads:
                                new_item = ((prod_left, prod_right), 0, la)
                                # ---- 添加调试检查 ----
                                if la not in self.grammar.terminals and la != '$':
                                    print(f"\nCRITICAL ERROR in Closure: Generated non-terminal lookahead '{la}'!")
                                    print(f"  Original Item being processed: {item}")
                                    print(f"  Symbol after dot (B): {next_symbol}")
                                    print(f"  Symbols after B (beta): {beta_symbols}")
                                    print(f"  FIRST(beta): {first_beta}")
                                    print(f"  Original Lookahead ('a'): {original_lookahead}")
                                    print(f"  Calculated New Lookaheads (FIRST(beta a)): {new_lookaheads}")
                                    print(f"  New Item causing error: {new_item}\n")
                                    # 可以选择在这里抛出异常来停止执行
                                    # raise ValueError(f"Illegal lookahead '{la}' generated")
                                # ---- 结束调试检查 ----
                                # 避免在同一轮闭包计算中重复添加已存在于结果集或本次新增集合中的项目
                                if new_item not in result and new_item not in new_items:
                                    new_items.add(new_item)
                                    changed = True
            
            result.update(new_items)
        
        return frozenset(result)
    
    def goto(self, state_index, symbol):
        """计算GOTO(I, X)，返回项目集I经过符号X到达的状态索引"""
        next_items = set()
        
        for item in self.canonical_collection[state_index]:
            production, dot_pos, lookahead = item
            left, right = production
            
            # 处理ε产生式
            if right == 'ε':
                # ε产生式不会有goto转移，因为点要么在ε前面，要么在后面
                continue
            
            symbols = right.split()
            
            # 如果点已经在末尾或点后面的符号不是指定的符号，则跳过
            if dot_pos >= len(symbols) or symbols[dot_pos] != symbol:
                continue
            
            # 将点向右移动一位
            next_items.add((production, dot_pos + 1, lookahead))
        
        if not next_items:
            return None
        
        # 计算闭包
        next_closure = self.closure(next_items)
        
        # 查找是否已经存在相同的状态
        for i, state in enumerate(self.canonical_collection):
            if state == next_closure:
                return i
        
        # 如果不存在，则添加新状态
        self.canonical_collection.append(next_closure)
        return len(self.canonical_collection) - 1
    
    def build_canonical_collection(self):
        # 初始化项目集规范族
        self.canonical_collection = []
        
        # 获取增强后的文法的第一个产生式 (例如 S' -> S)
        augmented_production = self.grammar.productions[0]
        
        # 初始项目集为闭包({[S' -> .S, $]})
        initial_item = (augmented_production, 0, '$')
        initial_closure = self.closure({initial_item})
        self.canonical_collection.append(initial_closure)
        
        # 构建项目集规范族
        queue = deque([0])  # 状态索引队列
        processed_states = set() # 跟踪已处理的状态
        
        while queue:
            state_index = queue.popleft()
            
            # 如果状态已经被处理，则跳过
            if state_index in processed_states:
                continue
            processed_states.add(state_index)
            
            # 当前状态 I
            current_state = self.canonical_collection[state_index]
            
            # 收集当前状态中所有相关符号(点后面的符号)
            symbols_to_process = set()
            for item in current_state:
                production, dot_pos, _ = item
                _, right = production
                
                # 处理ε产生式
                if right == 'ε':
                    continue
                
                symbols = right.split()
                if dot_pos < len(symbols):
                    symbols_to_process.add(symbols[dot_pos])
            
            # 对于每个符号，计算GOTO(I, X)
            for symbol in symbols_to_process:
                # 计算 GOTO(state_index, symbol)
                next_state_index = self.goto(state_index, symbol)
                
                # 如果生成了有效的下一状态，并且该状态尚未被处理，则加入队列
                if next_state_index is not None and next_state_index not in processed_states:
                    # 避免将已在队列中的状态重复添加
                    if next_state_index not in queue:
                         queue.append(next_state_index)
        
        # 打印所有状态的项目集(调试用)
        print("\n===== 项目集规范族(LR(1)) =====")
        for i, state in enumerate(self.canonical_collection):
            print(f"状态 {i}:")
            for item in state:
                production, dot_pos, lookahead = item
                left, right = production
                
                # 格式化项目
                if right == 'ε':
                    symbols = []
                    formatted_item = f"[{left} -> .ε, {lookahead}]" if dot_pos == 0 else f"[{left} -> ε., {lookahead}]"
                else:
                    symbols = right.split()
                    if dot_pos == len(symbols):
                        formatted_item = f"[{left} -> {right}., {lookahead}]"
                    else:
                        dotted_right = ' '.join(symbols[:dot_pos] + ['.'] + symbols[dot_pos:])
                        formatted_item = f"[{left} -> {dotted_right}, {lookahead}]"
                
                print(f"  {formatted_item}")
            print()

    def parse(self, input_string):
        # 将输入字符串分词并添加结束符号
        tokens = input_string.split()
        tokens.append('$')
        
        # 初始化栈，压入初始状态0
        stack = [(0, '$')]  # (状态, 符号)
        
        # 初始化输出，存储详细步骤信息 (step_num, state_stack_repr, input_repr, action_desc)
        steps_details = []
        step_count = 1
        
        # 初始化输入指针
        input_pos = 0
        
        while True:
            # 获取当前状态和输入符号
            state = stack[-1][0]
            current_token = tokens[input_pos]
            
            # 记录当前步骤的状态
            current_state_stack_repr = ' '.join(str(s[0]) for s in stack)
            current_input_repr = ' '.join(tokens[input_pos:])
            
            # 查询action表
            if (state, current_token) not in self.action_table:
                error_message = f"语法错误：状态 {state} 下无法处理符号 {current_token}"
                steps_details.append((step_count, current_state_stack_repr, current_input_repr, f"错误: {error_message}"))
                return False, error_message, steps_details
            
            action, value = self.action_table[(state, current_token)]
            action_desc = ""
            
            if action == 'shift':
                action_desc = f"移进: 将状态 {value} 和符号 {current_token} 压入栈 (Shift {value})"
                steps_details.append((step_count, current_state_stack_repr, current_input_repr, action_desc))
                
                # 执行移进
                stack.append((value, current_token))
                input_pos += 1
            
            elif action == 'reduce':
                production = self.grammar.productions[value]
                left, right = production
                display_reduction_right = right if right else 'ε'
                action_desc = f"归约: 使用产生式 {left} -> {display_reduction_right} (Reduce {value})"
                steps_details.append((step_count, current_state_stack_repr, current_input_repr, action_desc))
                
                # 执行归约
                pop_count = len(right.split()) if right != 'ε' else 0
                for _ in range(pop_count):
                    stack.pop()
                
                top_state = stack[-1][0]
                
                if (top_state, left) not in self.goto_table:
                    error_message = f"语法错误：状态 {top_state} 下无法通过 {left} 进行goto转换"
                    # Append error to the description of the reduce step that led here
                    steps_details[-1] = steps_details[-1][:-1] + (steps_details[-1][-1] + f"; 错误: {error_message}",)
                    return False, error_message, steps_details
                
                next_state = self.goto_table[(top_state, left)]
                stack.append((next_state, left))
            
            elif action == 'accept':
                action_desc = "接受: 输入符合文法 (Accept)"
                steps_details.append((step_count, current_state_stack_repr, current_input_repr, action_desc))
                return True, "分析成功：输入符合文法", steps_details
            
            else:
                error_message = f"未知的操作: {action}"
                steps_details.append((step_count, current_state_stack_repr, current_input_repr, f"错误: {error_message}"))
                return False, error_message, steps_details
            
            step_count += 1 # Increment step counter after a successful action

class LALR1Parser(LR1Parser):
    def __init__(self, grammar):
        # 只初始化 grammar，不调用父类的 __init__ 或 build_parsing_table
        self.grammar = grammar
        self.action_table = {}
        self.goto_table = {}
        self.canonical_collection = [] # LALR(1) states
        self.lr1_canonical_collection = [] # To store the original LR(1) states
        self.lr1_action_table = {} # To store the original LR(1) action table
        self.lr1_goto_table = {}   # To store the original LR(1) goto table
        # 构建 LALR(1) 分析表
        self.build_parsing_table()

    def get_core(self, item):
        # 获取项目的核心部分（去掉展望符）
        production, dot_pos, _ = item
        return (production, dot_pos)

    def merge_states(self, lr1_collection):
        # 按核心项目的集合划分状态
        core_to_states = {}
        for state_idx, state in enumerate(lr1_collection):
            # 获取状态的核心
            state_core = frozenset(self.get_core(item) for item in state)

            if state_core not in core_to_states:
                core_to_states[state_core] = []
            core_to_states[state_core].append(state_idx)

        # 合并具有相同核心项目的状态
        merged_collection = []
        lr1_to_lalr1_map = {} # Map from original LR(1) state index to merged LALR(1) index
        state_core_to_merged_idx = {} # Map from state core to merged LALR(1) index

        for state_core, lr1_state_indices in core_to_states.items():
            # 检查这个核心是否已经被合并过
            if state_core in state_core_to_merged_idx:
                merged_idx = state_core_to_merged_idx[state_core]
                # 更新映射：这些 LR(1) 状态也映射到同一个 LALR(1) 状态
                for lr1_idx in lr1_state_indices:
                     lr1_to_lalr1_map[lr1_idx] = merged_idx
                continue # 跳过，因为核心相同的状态已经合并

            # 合并相同核心的所有状态的 *项目*
            merged_state_items = set()
            for lr1_idx in lr1_state_indices:
                for item in lr1_collection[lr1_idx]:
                    merged_state_items.add(item) # Add the LR(1) item (prod, dot, lookahead)

            # 将合并后的项目集添加到 LALR(1) 规范族
            merged_collection.append(frozenset(merged_state_items))
            new_merged_idx = len(merged_collection) - 1

            # 记录核心到新合并状态索引的映射
            state_core_to_merged_idx[state_core] = new_merged_idx

            # 记录这些 LR(1) 状态到合并后状态的映射
            for lr1_idx in lr1_state_indices:
                lr1_to_lalr1_map[lr1_idx] = new_merged_idx

        return merged_collection, lr1_to_lalr1_map

    def build_parsing_table(self):
        # 1. 构建 LR(1) 项目集规范族
        # Temporarily create an LR(1) parser instance to get its collection and tables
        print("--- Building temporary LR(1) parser ---")
        temp_lr1_parser = LR1Parser(self.grammar)
        self.lr1_canonical_collection = temp_lr1_parser.canonical_collection
        self.lr1_action_table = temp_lr1_parser.action_table
        self.lr1_goto_table = temp_lr1_parser.goto_table
        print("--- Finished temporary LR(1) parser ---")


        # 2. 合并具有相同核心项目的状态
        self.canonical_collection, lr1_to_lalr1_map = self.merge_states(self.lr1_canonical_collection)
        num_lr1_states = len(self.lr1_canonical_collection)
        num_lalr1_states = len(self.canonical_collection)
        print(f"\nMerging LR(1) states into LALR(1): {num_lr1_states} -> {num_lalr1_states}")
        # print("LR(1) to LALR(1) state mapping:", lr1_to_lalr1_map) # Debugging

        # 3. 初始化 LALR(1) action 和 goto 表
        self.action_table = {}
        self.goto_table = {}

        # 4. 合并 LR(1) 表项来构建 LALR(1) 表
        print("\n--- Merging LR(1) tables into LALR(1) table ---")
        for lr1_state_idx in range(num_lr1_states):
            if lr1_state_idx not in lr1_to_lalr1_map:
                 print(f"Warning: LR(1) state {lr1_state_idx} not found in mapping.")
                 continue
            lalr1_state_idx = lr1_to_lalr1_map[lr1_state_idx]

            # 合并 Action 表项
            for terminal in self.grammar.terminals:
                if (lr1_state_idx, terminal) in self.lr1_action_table:
                    lr1_action = self.lr1_action_table[(lr1_state_idx, terminal)]
                    lalr1_key = (lalr1_state_idx, terminal)

                    if lalr1_key in self.action_table:
                        existing_action = self.action_table[lalr1_key]
                        if existing_action != lr1_action:
                            # 冲突处理
                            conflict_resolved = False
                            # 移进/归约冲突：优先移进 (Shift/Reduce)
                            if existing_action[0] == 'shift' and lr1_action[0] == 'reduce':
                                print(f"  Shift/Reduce conflict at LALR state {lalr1_state_idx}, terminal '{terminal}'. LR1 state {lr1_state_idx} wanted {lr1_action}, kept {existing_action}.")
                                conflict_resolved = True # Keep shift
                            elif existing_action[0] == 'reduce' and lr1_action[0] == 'shift':
                                print(f"  Shift/Reduce conflict at LALR state {lalr1_state_idx}, terminal '{terminal}'. LR1 state {lr1_state_idx} wanted {lr1_action}, replaced {existing_action}.")
                                self.action_table[lalr1_key] = lr1_action # Prioritize shift
                                conflict_resolved = True
                            # 归约/归约冲突：优先产生式编号小的 (Reduce/Reduce)
                            elif existing_action[0] == 'reduce' and lr1_action[0] == 'reduce':
                                if existing_action[1] != lr1_action[1]: # Only conflict if different reductions
                                     if lr1_action[1] < existing_action[1]:
                                          print(f"  Reduce/Reduce conflict at LALR state {lalr1_state_idx}, terminal '{terminal}'. LR1 state {lr1_state_idx} wanted {lr1_action}, replaced {existing_action}.")
                                          self.action_table[lalr1_key] = lr1_action # Keep smaller index reduce
                                     else:
                                           print(f"  Reduce/Reduce conflict at LALR state {lalr1_state_idx}, terminal '{terminal}'. LR1 state {lr1_state_idx} wanted {lr1_action}, kept {existing_action}.")
                                # If same reduction, no real conflict
                                conflict_resolved = True
                            # 其他冲突 (e.g., accept/shift) - 简单地报告并可能覆盖
                            if not conflict_resolved:
                                 print(f"WARNING: Unhandled conflict merging action at LALR state {lalr1_state_idx}, terminal '{terminal}'. ")
                                 print(f"  Existing: {existing_action}, New (from LR1 state {lr1_state_idx}): {lr1_action}. Overwriting.")
                                 self.action_table[lalr1_key] = lr1_action # Default: overwrite, may need better logic

                    else:
                        # 直接添加 Action
                        self.action_table[lalr1_key] = lr1_action
                        # print(f"  Adding Action[{lalr1_state_idx}, {terminal}] = {lr1_action} (from LR1 state {lr1_state_idx})")

            # 合并 Goto 表项 (Gotos should not conflict for same core)
            for non_terminal in self.grammar.non_terminals:
                if (lr1_state_idx, non_terminal) in self.lr1_goto_table:
                    lr1_goto_target_state = self.lr1_goto_table[(lr1_state_idx, non_terminal)]
                    # Map the target LR(1) state to its corresponding LALR(1) state
                    if lr1_goto_target_state not in lr1_to_lalr1_map:
                         print(f"Warning: Target LR(1) state {lr1_goto_target_state} for GOTO[{lr1_state_idx},{non_terminal}] not in mapping.")
                         continue
                    lalr1_goto_target_state = lr1_to_lalr1_map[lr1_goto_target_state]
                    lalr1_key = (lalr1_state_idx, non_terminal)

                    if lalr1_key in self.goto_table:
                        existing_goto = self.goto_table[lalr1_key]
                        if existing_goto != lalr1_goto_target_state:
                            # This indicates an issue, Gotos for same core should be consistent
                            print(f"ERROR: GOTO conflict at LALR state {lalr1_state_idx}, non-terminal '{non_terminal}'. ")
                            print(f"  Existing: {existing_goto}, New (from LR1 state {lr1_state_idx}): {lalr1_goto_target_state}. Keeping existing.")
                    else:
                        self.goto_table[lalr1_key] = lalr1_goto_target_state
                        # print(f"  Adding GOTO[{lalr1_state_idx}, {non_terminal}] = {lalr1_goto_target_state} (from LR1 GOTO[{lr1_state_idx},{non_terminal}]={lr1_goto_target_state})")

        print("--- Finished merging tables ---")
        # 打印分析表 (可以选择性调用父类的打印方法或自定义)
        self.print_parsing_table()

class LR1ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LR(1)/LALR(1)语法分析器")
        self.root.geometry("1200x800")
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建文法输入选项卡
        self.grammar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.grammar_frame, text="文法输入")
        
        # 创建分析器选项卡
        self.parser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parser_frame, text="语法分析")
        
        # 创建项目集选项卡
        self.items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.items_frame, text="项目集与分析表")
        
        # 初始化文法输入界面
        self.setup_grammar_input()
        
        # 初始化分析器界面
        self.setup_parser_interface()
        
        # 初始化项目集和分析表界面
        self.setup_items_interface()
        
        # 初始化语法分析器和文法
        self.grammar = None
        self.parser = None
        self.parser_type = "LR(1)"  # 默认为LR(1)分析器
    
    def setup_grammar_input(self):
        # 文法输入区域
        frame = ttk.LabelFrame(self.grammar_frame, text="输入文法（每行一条产生式，符号间用空格分隔，例如：S -> ( S ) | ε）")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.grammar_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=20)
        self.grammar_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 更新示例文法以符合空格分隔要求
        example_grammar = "S  -> a E c \nS  -> a F d \nS  -> b E d \nS  -> b F c \nE  -> e \nF  -> e  "
        self.grammar_text.insert(tk.END, example_grammar)
        
        # 分析器类型选择框
        parser_type_frame = ttk.Frame(self.grammar_frame)
        parser_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(parser_type_frame, text="选择分析器类型:").pack(side=tk.LEFT, padx=5)
        
        self.parser_type_var = tk.StringVar(value="LR(1)")
        parser_type_combo = ttk.Combobox(parser_type_frame, textvariable=self.parser_type_var, values=["LR(1)", "LALR(1)"], state="readonly", width=10)
        parser_type_combo.pack(side=tk.LEFT, padx=5)
        
        # 构建分析器按钮
        buttons_frame = ttk.Frame(self.grammar_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.build_button = ttk.Button(buttons_frame, text="构建分析器", command=self.build_parser)
        self.build_button.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        self.grammar_result = scrolledtext.ScrolledText(self.grammar_frame, wrap=tk.WORD, width=80, height=10)
        self.grammar_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_parser_interface(self):
        # 输入串输入区域
        input_frame = ttk.LabelFrame(self.parser_frame, text="输入串（用空格分隔符号）")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_text = ttk.Entry(input_frame, width=80)
        self.input_text.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.input_text.insert(0, "a e c")
        
        # 分析按钮
        self.parse_button = ttk.Button(self.parser_frame, text="分析", command=self.parse_input)
        self.parse_button.pack(pady=10)
        
        # 分析结果区域
        result_frame = ttk.LabelFrame(self.parser_frame, text="分析结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.parse_result = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=25)
        self.parse_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_items_interface(self):
        # 创建水平分割窗口
        paned_window = ttk.PanedWindow(self.items_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：项目集规范族
        items_frame = ttk.LabelFrame(paned_window, text="项目集规范族")
        paned_window.add(items_frame, weight=1)
        
        self.items_text = scrolledtext.ScrolledText(items_frame, wrap=tk.WORD, width=40, height=30)
        self.items_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧：分析表 (使用 Treeview 显示表格)
        tables_frame = ttk.Frame(paned_window)
        paned_window.add(tables_frame, weight=2)
        
        table_notebook = ttk.Notebook(tables_frame)
        table_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action 表 Frame 和 Treeview (Initial setup)
        action_frame = ttk.Frame(table_notebook)
        table_notebook.add(action_frame, text='Action 表')
        
        # Initialize Treeview with minimal columns first
        self.action_tree = ttk.Treeview(action_frame, columns=['状态'], show='headings')
        self.action_tree.heading('状态', text='状态')
        self.action_tree.column('状态', width=60, anchor='center')
        self.action_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        action_scrollbar = ttk.Scrollbar(action_frame, orient=tk.VERTICAL, command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=action_scrollbar.set)
        action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Goto 表 Frame 和 Treeview (Initial setup)
        goto_frame = ttk.Frame(table_notebook)
        table_notebook.add(goto_frame, text='Goto 表')
        
        # Initialize Treeview with minimal columns first
        self.goto_tree = ttk.Treeview(goto_frame, columns=['状态'], show='headings')
        self.goto_tree.heading('状态', text='状态')
        self.goto_tree.column('状态', width=60, anchor='center')
        self.goto_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        goto_scrollbar = ttk.Scrollbar(goto_frame, orient=tk.VERTICAL, command=self.goto_tree.yview)
        self.goto_tree.configure(yscrollcommand=goto_scrollbar.set)
        goto_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def build_parser(self):
        # 获取文法文本
        grammar_text = self.grammar_text.get("1.0", tk.END)
        
        try:
            # 创建文法对象
            self.grammar = Grammar()
            if not self.grammar.parse_grammar(grammar_text):
                self.grammar_result.delete("1.0", tk.END)
                self.grammar_result.insert(tk.END, "文法解析错误")
                return
            
            # 计算FIRST集和FOLLOW集
            self.grammar.compute_first_sets()
            self.grammar.compute_follow_sets()
            
            # 获取选择的分析器类型
            self.parser_type = self.parser_type_var.get()
            
            # 构建相应类型的分析器
            if self.parser_type == "LR(1)":
                self.parser = LR1Parser(self.grammar)
            else:  # LALR(1)
                self.parser = LALR1Parser(self.grammar)
            
            # 显示构建结果
            self.grammar_result.delete("1.0", tk.END)
            self.grammar_result.insert(tk.END, f"{self.parser_type}分析器构建成功\n\n")
            
            # 显示终结符和非终结符
            self.grammar_result.insert(tk.END, f"终结符: {', '.join(sorted(self.grammar.terminals))}\n")
            self.grammar_result.insert(tk.END, f"非终结符: {', '.join(sorted(self.grammar.non_terminals))}\n\n")
            
            # 显示FIRST集和FOLLOW集
            self.grammar_result.insert(tk.END, "FIRST集:\n")
            for symbol in sorted(self.grammar.non_terminals):
                self.grammar_result.insert(tk.END, f"FIRST({symbol}) = {{{', '.join(sorted(self.grammar.first_sets[symbol]))}}}\n")
            
            self.grammar_result.insert(tk.END, "\nFOLLOW集:\n")
            for symbol in sorted(self.grammar.non_terminals):
                self.grammar_result.insert(tk.END, f"FOLLOW({symbol}) = {{{', '.join(sorted(self.grammar.follow_sets[symbol]))}}}\n")
            
            # 如果是LALR(1)分析器，显示状态合并信息
            if self.parser_type == "LALR(1)":
                lalr_parser = self.parser
                original_state_count = len(lalr_parser.lr1_canonical_collection)
                merged_state_count = len(lalr_parser.canonical_collection)
                self.grammar_result.insert(tk.END, f"\nLALR(1)状态合并信息:\n")
                self.grammar_result.insert(tk.END, f"原始LR(1)状态数: {original_state_count}\n")
                self.grammar_result.insert(tk.END, f"合并后LALR(1)状态数: {merged_state_count}\n")
                self.grammar_result.insert(tk.END, f"减少状态数: {original_state_count - merged_state_count}\n")
            
            # 更新项目集和分析表
            self.update_items_and_tables()
            
            # 切换到分析器选项卡
            self.notebook.select(1)
            
        except Exception as e:
            self.grammar_result.delete("1.0", tk.END)
            self.grammar_result.insert(tk.END, f"错误: {str(e)}")
    
    def update_items_and_tables(self):
        if not self.parser or not self.grammar: # Ensure both parser and grammar exist
            return
        
        # 更新项目集规范族
        self.items_text.delete("1.0", tk.END)
        
        # 添加分析器类型信息
        self.items_text.insert(tk.END, f"{self.parser_type}分析表\n\n")
        
        for i, state in enumerate(self.parser.canonical_collection):
            self.items_text.insert(tk.END, f"状态 {i}:\n")
            sorted_items = sorted(list(state), key=lambda item: (item[0][0], item[0][1], item[1], item[2]))
            for item in sorted_items:
                production, dot_pos, lookahead = item
                left, original_right = production
                if original_right == 'ε': display_right = "." 
                else:
                    symbols = original_right.split()
                    display_symbols = symbols[:dot_pos] + ['.'] + symbols[dot_pos:]
                    display_right = ' '.join(display_symbols)
                    if display_right.endswith(' .'): display_right = display_right[:-2] + '.'
                self.items_text.insert(tk.END, f"    [{left} -> {display_right}, {lookahead}]\n")
            self.items_text.insert(tk.END, "\n")
        
        # --- 更新 Action 表 (使用 Treeview) ---
        # 清空旧数据
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        
        # ** 设置 Action 表的列 (移到这里) **
        terminals = sorted([t for t in self.grammar.terminals if t != 'ε'])
        action_cols = ['状态'] + terminals
        self.action_tree["columns"] = action_cols
        # ** 配置所有列的标题和宽度 (移到这里) **
        for col in action_cols:
             self.action_tree.heading(col, text=col)
             self.action_tree.column(col, width=max(60, len(col)*10), anchor='center') # Adjust width

        # 填充 Action 表数据
        for i in range(len(self.parser.canonical_collection)):
            row_values = [str(i)]
            for terminal in terminals:
                cell_value = ""
                if (i, terminal) in self.parser.action_table:
                    action, value = self.parser.action_table[(i, terminal)]
                    if action == 'shift': cell_value = f"s{value}"
                    elif action == 'reduce':
                        left, right = self.grammar.productions[value]
                        display_reduction_right = right if right else 'ε'
                        cell_value = f"r({left}->{display_reduction_right})"
                    # Accept is handled specially below for '$' column
                if terminal == '$' and (i, '$') in self.parser.action_table and self.parser.action_table[(i, '$')][0] == 'accept':
                    cell_value = "acc"
                row_values.append(cell_value)
            self.action_tree.insert("", tk.END, values=row_values)

        # --- 更新 Goto 表 (使用 Treeview) ---
        # 清空旧数据
        for item in self.goto_tree.get_children():
            self.goto_tree.delete(item)
        
        # ** 设置 Goto 表的列 (移到这里) **
        non_terminals = sorted([nt for nt in self.grammar.non_terminals if nt != self.grammar.start_symbol])
        goto_cols = ['状态'] + non_terminals
        self.goto_tree["columns"] = goto_cols
        # ** 配置所有列的标题和宽度 (移到这里) **
        for col in goto_cols:
             self.goto_tree.heading(col, text=col)
             self.goto_tree.column(col, width=max(60, len(col)*10), anchor='center') # Adjust width

        # 填充 Goto 表数据
        for i in range(len(self.parser.canonical_collection)):
            row_values = [str(i)]
            for nt in non_terminals:
                cell_value = ""
                if (i, nt) in self.parser.goto_table:
                    cell_value = str(self.parser.goto_table[(i, nt)])
                row_values.append(cell_value)
            self.goto_tree.insert("", tk.END, values=row_values)
    
    def parse_input(self):
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器")
            return
        
        # 获取输入串
        input_string = self.input_text.get()
        
        # 进行语法分析
        success, message, detailed_steps = self.parser.parse(input_string)
        
        # 显示分析结果
        self.parse_result.delete("1.0", tk.END)
        self.parse_result.insert(tk.END, f"{message}\n\n")
        
        # 显示分析步骤表头
        # 使用制表符分隔，可能需要调整列宽或使用更复杂的格式化方式（如固定宽度）以保证对齐
        header = f"步骤\t状态栈{' ' * 15}输入串{' ' * 15}动作\n"
        self.parse_result.insert(tk.END, header)
        self.parse_result.insert(tk.END, "-" * 80 + "\n") # Separator line
        
        # 显示详细分析步骤
        for step_data in detailed_steps:
            step_num, state_stack_repr, input_repr, action_desc = step_data
            # Format with tabs, adjust spacing as needed for alignment
            line = f"{step_num}\t{state_stack_repr.ljust(20)}{input_repr.ljust(20)}{action_desc}\n"
            self.parse_result.insert(tk.END, line)

def main():
    root = tk.Tk()
    root.title("LR(1)/LALR(1)语法分析器")
    app = LR1ParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 