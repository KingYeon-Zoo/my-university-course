import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import re

class LexicalAnalyzer:
    def __init__(self):       
        # 关键字表 (t=1)
        self.keywords = ["if", "then", "else", "for", "while", "do", "int", "float", "double", "return", "void", "printf"]
        
        # 分界符表 (t=2)
        self.delimiters = [";", ",", "(", ")", "[", "]", "{", "}", "."]
        
        # 算术运算符表 (t=3)
        self.arithmetic_operators = ["+", "-", "*", "/", "%"]
        
        # 关系运算符表 (t=4)
        self.relational_operators = ["<", "<=", "=", ">", ">=", "<>", "==", "!="]
        
        # 标识符表和常数表
        self.identifiers = []
        self.constants = []
        
        # 行数和列数计数器
        self.line_num = 1
        self.col_num = 1
        
    def analyze(self, source_code):
        result = []
        lines = source_code.split('\n') #将 source_code 按换行符 \n 分割成多行 lines
        
        # 逐行分析
        for line_index, line in enumerate(lines):
            self.line_num = line_index + 1  #注意：line_index 从 0 开始，而 self.line_num 从 1 开始
            self.col_num = 1 
            
            i = 0 # 当前行中的字符索引（指针i）
            while i < len(line):
                # 跳过空格
                if line[i].isspace():
                    self.col_num += 1
                    i += 1
                    continue 
                
                # 如果是字母，判断是标识符或关键字
                if line[i].isalpha() or line[i] == '_': 
                    start_col = self.col_num
                    identifier = ''
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        identifier += line[i]
                        self.col_num += 1
                        i += 1
                    
                    # 判断是否是关键字
                    if identifier in self.keywords:
                        result.append({
                            'word': identifier,
                            'type': 1,
                            'attribute': identifier,
                            'type_name': '关键字',
                            'position': f'({self.line_num}, {start_col})'
                        })
                    else:
                        # 标识符
                        if identifier not in self.identifiers:
                            self.identifiers.append(identifier)
                        
                        result.append({
                            'word': identifier,
                            'type': 6,
                            'attribute': identifier,
                            'type_name': '标识符',
                            'position': f'({self.line_num}, {start_col})'
                        })
                
                # 如果是数字，判断是否是常数
                elif line[i].isdigit():
                    start_col = self.col_num
                    number = ''
                    has_error = False
                    
                    while i < len(line) and (line[i].isalnum() or line[i] == '.'):
                        number += line[i]
                        self.col_num += 1
                        i += 1
                    
                    # 检查是否是合法的数字
                    if re.match(r'^[0-9]+(\.[0-9]+)?$', number):
                        if number not in self.constants:
                            self.constants.append(number)
                        
                        result.append({
                            'word': number,
                            'type': 5,
                            'attribute': number,
                            'type_name': '常数',
                            'position': f'({self.line_num}, {start_col})'
                        })
                    else:
                        # 错误的数字格式
                        result.append({
                            'word': number,
                            'type': 'Error',
                            'attribute': 'Error',
                            'type_name': 'Error',
                            'position': f'({self.line_num}, {start_col})'
                        })
                
                # 如果不是字母或者数字，那么就检查是否是运算符和分界符
                else:
                    start_col = self.col_num
                    operator = line[i]
                    self.col_num += 1
                    i += 1
                    
                    # 检查是否是双字符运算符
                    if i < len(line):
                        two_char_op = operator + line[i]
                        if two_char_op in self.relational_operators:
                            operator = two_char_op
                            self.col_num += 1
                            i += 1
                    
                    # 分类处理
                    if operator in self.delimiters:
                        result.append({
                            'word': operator,
                            'type': 2,
                            'attribute': operator,
                            'type_name': '分界符',
                            'position': f'({self.line_num}, {start_col})'
                        })
                    elif operator in self.arithmetic_operators:
                        result.append({
                            'word': operator,
                            'type': 3,
                            'attribute': operator,
                            'type_name': '算术运算符',
                            'position': f'({self.line_num}, {start_col})'
                        })
                    elif operator in self.relational_operators:
                        result.append({
                            'word': operator,
                            'type': 4,
                            'attribute': operator,
                            'type_name': '关系运算符',
                            'position': f'({self.line_num}, {start_col})'
                        })
                    else:
                        # 未识别的符号
                        result.append({
                            'word': operator,
                            'type': 'Error',
                            'attribute': 'Error',
                            'type_name': 'Error',
                            'position': f'({self.line_num}, {start_col})'
                        })
        
        return result

class LexicalAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("词法分析器")
        self.root.geometry("900x600")
        
        self.analyzer = LexicalAnalyzer()
        
        # 创建界面
        self.create_ui()
    
    def create_ui(self):
        # 创建左右分隔的界面
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 输入区域
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # 右侧面板 - 输出区域
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # 左侧输入区域
        ttk.Label(left_frame, text="输入源代码:").pack(anchor=tk.W, pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=40, height=20)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存结果", command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="分析", command=self.analyze_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # 右侧结果区域
        ttk.Label(right_frame, text="分析结果:").pack(anchor=tk.W, pady=(0, 5))
        
        # 创建表格
        columns = ('单词', '二元序列', '类型', '位置')
        self.result_table = ttk.Treeview(right_frame, columns=columns, show='headings')
        
        # 设置列标题
        for col in columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_table.yview)
        self.result_table.configure(yscroll=scrollbar.set)
        
        self.result_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("错误", f"打开文件时出错: {str(e)}")
    
    def save_results(self):
        if not self.result_table.get_children():
            messagebox.showinfo("提示", "没有分析结果可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("单词\t二元序列\t类型\t位置\n")
                    for item_id in self.result_table.get_children():
                        values = self.result_table.item(item_id)['values']
                        file.write(f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\n")
                messagebox.showinfo("成功", "分析结果已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
    
    def analyze_code(self):
        # 清空之前的结果
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        
        # 获取输入的代码
        source_code = self.input_text.get(1.0, tk.END)
        
        # 分析代码
        results = self.analyzer.analyze(source_code)
        
        # 显示结果
        for result in results:
            token_type = result['type']
            token_attr = result['attribute']
            
            # 二元序列表示
            binary_repr = f"({token_type}, {token_attr})"
            
            self.result_table.insert('', tk.END, values=(
                result['word'],
                binary_repr,
                result['type_name'],
                result['position']
            ))
    
    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        for item in self.result_table.get_children():
            self.result_table.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = LexicalAnalyzerApp(root)
    root.mainloop() 