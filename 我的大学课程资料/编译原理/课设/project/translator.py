import re

# 语言类型枚举
class LanguageType:
    PSEUDO = 'PSEUDO'  # 原始的伪代码语言
    C_STYLE = 'C_STYLE'  # C语言风格
    PYTHON = 'PYTHON'  # Python风格

# 标记类型
class TokenType:
    # 伪代码关键字
    FOR = 'FOR'
    TO = 'TO'
    DO = 'DO'
    ENDFOR = 'ENDFOR'
    
    # C风格关键字和操作符
    C_FOR = 'C_FOR'
    SEMICOLON = ';'
    INCREMENT = '++'
    DECREMENT = '--'
    
    # Python风格关键字
    PY_FOR = 'PY_FOR'
    IN = 'IN'
    RANGE = 'RANGE'
    COLON = ':'
    
    # 通用标记
    ID = 'ID'
    NUMBER = 'NUMBER'
    ASSIGN = ':='
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    COMMA = ','
    
    # 比较操作符
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    EQ = '=='
    NEQ = '!='
    
    # 赋值操作符
    ADD_ASSIGN = '+='
    SUB_ASSIGN = '-='
    MUL_ASSIGN = '*='
    DIV_ASSIGN = '/='
    
    EOF = 'EOF'  # 文件结束

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()

class Lexer:
    def __init__(self, text, language_type=LanguageType.PSEUDO):
        # 规范化空白并处理潜在的多行输入
        self.language_type = language_type
        
        if language_type == LanguageType.PSEUDO:
            processed_text = ' '.join(text.split())
        elif language_type == LanguageType.PYTHON:
            # 对于Python，保持原始缩进很重要
            processed_text = text
        else:
            # 对于C风格，保留原始结构，只移除多余空格
            processed_text = re.sub(r'\s+', ' ', text)
            
        self.text = processed_text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

        # 根据语言类型设置关键字
        if language_type == LanguageType.PSEUDO:
            self.keywords = {
                'FOR': Token(TokenType.FOR, 'FOR'),
                'TO': Token(TokenType.TO, 'TO'),
                'DO': Token(TokenType.DO, 'DO'),
                'ENDFOR': Token(TokenType.ENDFOR, 'ENDFOR'),
            }
        elif language_type == LanguageType.C_STYLE:
            self.keywords = {
                'for': Token(TokenType.C_FOR, 'for'),
            }
        elif language_type == LanguageType.PYTHON:
            self.keywords = {
                'for': Token(TokenType.PY_FOR, 'for'),
                'in': Token(TokenType.IN, 'in'),
                'range': Token(TokenType.RANGE, 'range'),
            }

    def advance(self):
        """推进 'pos' 指针并设置 'current_char'。"""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # 表示输入结束
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """返回从输入中消耗的一个（多位）整数。"""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, int(result))

    def identifier(self):
        """处理标识符和保留关键字。"""
        result = ''
        # 允许字母、数字和下划线，但必须以字母或下划线开头
        if self.current_char is not None and (self.current_char.isalpha() or self.current_char == '_'):
             result += self.current_char
             self.advance()
             while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                result += self.current_char
                self.advance()
        else:
            # 如果调用正确，则不应发生，但有助于提高健壮性
             raise Exception(f'Lexer error: Invalid start for identifier at position {self.pos}')

        if self.language_type == LanguageType.PSEUDO:
            token = self.keywords.get(result.upper())  # 检查关键字（不区分大小写）
        else:
            token = self.keywords.get(result)  # C语言和Python区分大小写

        if token is None:
            token = Token(TokenType.ID, result)  # 这是一个标识符
        return token

    def get_next_token(self):
        """词法分析器。"""
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            # 在其他符号之前检查标识符/关键字的开头
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            # 处理普通符号
            if self.current_char == ':':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.ASSIGN, ':=')
                else:
                    self.advance()
                    return Token(TokenType.COLON, ':')

            if self.current_char == '+':
                if self.peek() == '+':
                    self.advance()
                    self.advance()
                    return Token(TokenType.INCREMENT, '++')
                elif self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.ADD_ASSIGN, '+=')
                else:
                    self.advance()
                    return Token(TokenType.PLUS, '+')
                    
            if self.current_char == '-':
                if self.peek() == '-':
                    self.advance()
                    self.advance()
                    return Token(TokenType.DECREMENT, '--')
                elif self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.SUB_ASSIGN, '-=')
                else:
                    self.advance()
                    return Token(TokenType.MINUS, '-')
                    
            if self.current_char == '*':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.MUL_ASSIGN, '*=')
                else:
                    self.advance()
                    return Token(TokenType.MUL, '*')
                    
            if self.current_char == '/':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.DIV_ASSIGN, '/=')
                else:
                    self.advance()
                    return Token(TokenType.DIV, '/')
                    
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.EQ, '==')
                else:
                    self.advance()
                    return Token(TokenType.ASSIGN, '=')
                    
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NEQ, '!=')
                    
            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LE, '<=')
                else:
                    self.advance()
                    return Token(TokenType.LT, '<')
                    
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GE, '>=')
                else:
                    self.advance()
                    return Token(TokenType.GT, '>')
                    
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
                
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
                
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{')
                
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}')
                
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';')
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',')

            # 如果没有匹配，则引发错误
            raise Exception(f'Lexer error: Invalid character \'{self.current_char}\' at position {self.pos}')

        return Token(TokenType.EOF, None)  # 文件结束

    def peek(self):
        """向前查看一个字符而不消耗它。"""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

# --- 四元式表示 ---
class Quadruple:
    # 如果生成大量四元式，使用 slots 以提高内存效率
    __slots__ = ('op', 'arg1', 'arg2', 'result')

    def __init__(self, op, arg1, arg2, result):
        self.op = op       # 操作符（例如 '+', ':=', 'J>', 'JMP', 'LABEL'）
        self.arg1 = arg1   # 第一个参数（可以是变量、数字或标签）
        self.arg2 = arg2   # 第二个参数（可以是变量、数字或标签）
        self.result = result # 结果（通常是变量或用于跳转的标签）

    def __str__(self):
        # 用 '_' 表示未使用的参数以保持清晰
        arg1_str = self.arg1 if self.arg1 is not None else '_'
        arg2_str = self.arg2 if self.arg2 is not None else '_'
        result_str = self.result if self.result is not None else '_'
        return f'({self.op}, {arg1_str}, {arg2_str}, {result_str})'

    def __repr__(self):
        return self.__str__()

# --- 解析器和四元式生成 ---
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.quadruples = []  # 用于存储生成的四元式的列表
        self.temp_var_count = 0  # 用于生成临时变量名的计数器
        self.label_count = 0     # 用于生成标签名的计数器
        self.language_type = lexer.language_type

    def error(self, message):
        # 报告解析期间的语法错误
        raise Exception(f'Parser error: {message}. Found token: {self.current_token}')

    def eat(self, token_type):
        # 如果当前标记与预期类型匹配，则消耗它。
        # 前进到下一个标记。
        # 如果标记类型不匹配，则引发错误。
        if self.current_token.type == token_type:
            #print(f"Eating: {self.current_token}") # 调试打印
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'Expected token {token_type}, but got {self.current_token.type}')

    def new_temp(self):
        # 生成一个新的唯一临时变量名（例如 t1, t2, ...）
        self.temp_var_count += 1
        return f't{self.temp_var_count}'

    def new_label(self):
        # 生成一个新的唯一标签名（例如 L1, L2, ...）
        self.label_count += 1
        return f'L{self.label_count}'

    def emit(self, op, arg1, arg2, result):
        # 创建一个新的四元式并将其添加到列表中
        quad = Quadruple(op, arg1, arg2, result)
        self.quadruples.append(quad)
        #print(f"Emitted: {quad}") # 调试打印

    # --- 带语义动作的语法规则解析方法 --- 

    def parse(self):
        # 解析的入口点，根据语言类型选择不同的解析方法
        if self.language_type == LanguageType.PSEUDO:
            self.parse_stmt_list()
        elif self.language_type == LanguageType.C_STYLE:
            self.parse_stmt_list()
        elif self.language_type == LanguageType.PYTHON:
            self.parse_stmt_list()
        
        # 解析语句后，我们期望输入的结束
        if self.current_token.type != TokenType.EOF:
            self.error("Expected end of input after statement")
        return self.quadruples

    def parse_stmt_list(self):
        """解析语句列表，支持多个语句（包括循环和赋值）"""
        if self.language_type == LanguageType.PSEUDO:
            # 解析伪代码语句
            if self.current_token.type == TokenType.FOR:
                self.parse_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_assign_stmt()
            else:
                self.error("Expected FOR or assignment statement")
        elif self.language_type == LanguageType.C_STYLE:
            # 解析C风格语句
            if self.current_token.type == TokenType.C_FOR:
                self.parse_c_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_assign_stmt()
            else:
                self.error("Expected for or assignment statement")
        elif self.language_type == LanguageType.PYTHON:
            # 解析Python风格语句
            if self.current_token.type == TokenType.PY_FOR:
                self.parse_python_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_py_assign_stmt()
            else:
                self.error("Expected for or assignment statement")

        # 如果还有更多语句，继续解析
        if self.current_token.type != TokenType.EOF:
            self.parse_stmt_list()

    def parse_for_stmt(self):
        # <for_stmt> -> FOR <id> := <expr> TO <expr> DO <stmt_list> ENDFOR
        # <stmt_list> -> <stmt> | <stmt> <stmt_list>
        # <stmt> -> <assign_stmt> | <for_stmt>
        self.eat(TokenType.FOR)

        # 获取循环变量名
        loop_var_token = self.current_token
        self.eat(TokenType.ID)
        loop_var = loop_var_token.value

        self.eat(TokenType.ASSIGN)

        # 解析初始值表达式 (E1)
        e1_result = self.parse_expr()
        # 发射：loop_var := E1_result
        self.emit(':=', e1_result, None, loop_var)

        self.eat(TokenType.TO)

        # 解析限制表达式 (E2)
        e2_result = self.parse_expr()

        # 创建用于循环控制的标签
        label_cond_check = self.new_label()  # 条件检查开始处的标签
        label_loop_end = self.new_label()    # 循环结束时跳转到的标签

        # 发射条件检查的标签
        self.emit('LABEL', None, None, label_cond_check)

        # 发射条件跳转
        cond_temp = self.new_temp()
        self.emit('>', loop_var, e2_result, cond_temp)
        self.emit('JZ', cond_temp, None, label_loop_end)

        self.eat(TokenType.DO)

        # 解析循环体中的语句列表，直到遇到ENDFOR
        while self.current_token.type != TokenType.ENDFOR:
            # 根据当前token类型选择解析方法
            if self.current_token.type == TokenType.FOR:
                self.parse_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_assign_stmt()
            else:
                self.error("Expected FOR, assignment statement, or ENDFOR")

        # 发射循环变量增量（假设步长 = 1）
        self.emit('+', loop_var, 1, loop_var)  # loop_var = loop_var + 1

        # 发射无条件跳转回条件检查
        self.emit('JMP', None, None, label_cond_check)

        # 发射循环退出跳转的结束标签
        self.emit('LABEL', None, None, label_loop_end)

        self.eat(TokenType.ENDFOR)

        return self.quadruples

    def parse_c_for_stmt(self):
        # <c_for_stmt> -> for ( <init> ; <condition> ; <increment> ) { <stmt_list> }
        # <stmt_list> -> <stmt> | <stmt> <stmt_list>
        # <stmt> -> <assign_stmt> | <c_for_stmt>
        self.eat(TokenType.C_FOR)
        self.eat(TokenType.LPAREN)
        
        # 解析初始化部分
        loop_var_token = self.current_token
        self.eat(TokenType.ID)
        loop_var = loop_var_token.value
        
        self.eat(TokenType.ASSIGN)  # '='
        
        # 解析初始值
        e1_result = self.parse_expr()
        self.emit(':=', e1_result, None, loop_var)
        
        self.eat(TokenType.SEMICOLON)
        
        # 解析条件部分
        left_operand = self.current_token.value
        self.eat(TokenType.ID)
        
        # 获取比较操作符
        op_token = self.current_token
        condition_op = op_token.type
        self.eat(condition_op)
        
        # 获取右操作数（限制值）
        e2_result = self.parse_expr()
        
        self.eat(TokenType.SEMICOLON)
        
        # 保存增量表达式信息
        inc_var = self.current_token.value
        self.eat(TokenType.ID)
        
        inc_op = self.current_token.type
        self.eat(inc_op)
        
        self.eat(TokenType.RPAREN)
        
        # 发射循环标签
        label_cond_check = self.new_label()
        label_loop_end = self.new_label()
        
        # 先发射条件标签
        self.emit('LABEL', None, None, label_cond_check)
        
        # 发射条件检查
        cond_op_map = {
            TokenType.LT: '<',
            TokenType.GT: '>',
            TokenType.LE: '<=',
            TokenType.GE: '>=',
            TokenType.EQ: '==',
            TokenType.NEQ: '!='
        }
        
        cond_op = cond_op_map.get(condition_op)
        temp_cond = self.new_temp()
        self.emit(cond_op, left_operand, e2_result, temp_cond)
        self.emit('JZ', temp_cond, None, label_loop_end)
        
        # 解析循环体
        self.eat(TokenType.LBRACE)
        
        # 解析循环体中的语句列表，直到遇到RBRACE
        while self.current_token.type != TokenType.RBRACE:
            # 根据当前token类型选择解析方法
            if self.current_token.type == TokenType.C_FOR:
                self.parse_c_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_assign_stmt()
            else:
                self.error("Expected for, assignment statement, or }")
            
        self.eat(TokenType.RBRACE)
        
        # 发射增量
        if inc_op == TokenType.INCREMENT:
            self.emit('+', inc_var, 1, inc_var)
        elif inc_op == TokenType.DECREMENT:
            self.emit('-', inc_var, 1, inc_var)
        
        # 发射跳回条件检查
        self.emit('JMP', None, None, label_cond_check)
        
        # 发射循环结束标签
        self.emit('LABEL', None, None, label_loop_end)
        
        return self.quadruples

    def parse_python_for_stmt(self):
        # <python_for_stmt> -> for <id> in range(<expr>, <expr>): <stmt_list>
        # <stmt_list> -> <stmt> | <stmt> <stmt_list>
        # <stmt> -> <py_assign_stmt> | <python_for_stmt>
        self.eat(TokenType.PY_FOR)
        
        # 获取循环变量名
        loop_var_token = self.current_token
        self.eat(TokenType.ID)
        loop_var = loop_var_token.value
        
        self.eat(TokenType.IN)
        self.eat(TokenType.RANGE)
        self.eat(TokenType.LPAREN)
        
        # 解析range的起始值
        start_expr = self.parse_expr()
        
        # 检查是否有第二个参数（结束值）
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            end_expr = self.parse_expr()
        else:
            # 如果没有第二个参数，则第一个参数是结束值，起始值默认为0
            end_expr = start_expr
            start_expr = 0
        
        # 检查是否有第三个参数（步长）
        step_expr = 1  # 默认步长为1
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            step_expr = self.parse_expr()
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        
        # 处理表达式结果，确保能够正确地处理复杂表达式
        # 如果start_expr不是直接值（如数字或变量），需要将其存储在临时变量中
        if not isinstance(start_expr, (int, str)):
            temp_start = self.new_temp()
            self.emit(':=', start_expr, None, temp_start)
            start_expr = temp_start
            
        # 同样处理end_expr
        if not isinstance(end_expr, (int, str)):
            temp_end = self.new_temp()
            self.emit(':=', end_expr, None, temp_end)
            end_expr = temp_end
            
        # 同样处理step_expr
        if not isinstance(step_expr, (int, str)):
            temp_step = self.new_temp()
            self.emit(':=', step_expr, None, temp_step)
            step_expr = temp_step
        
        # 生成初始化四元式：loop_var = start_expr
        self.emit(':=', start_expr, None, loop_var)
        
        # 创建循环标签
        label_cond_check = self.new_label()
        label_loop_end = self.new_label()
        
        # 发射条件检查标签
        self.emit('LABEL', None, None, label_cond_check)
        
        # 发射条件判断：如果loop_var >= end_expr则跳出循环
        temp_cond = self.new_temp()
        self.emit('<', loop_var, end_expr, temp_cond)  # temp_cond = (loop_var < end_expr)
        self.emit('JZ', temp_cond, None, label_loop_end)  # 如果条件为假，则跳转到结束
        
        # 解析至少一条语句
        # Python风格的语句，可以是for循环或赋值语句
        if self.current_token.type == TokenType.PY_FOR:
            self.parse_python_for_stmt()
        elif self.current_token.type == TokenType.ID:
            self.parse_py_assign_stmt()
        else:
            self.error("Expected for or assignment statement")
            
        # 继续解析缩进相同的其他语句（这里简化处理，不考虑缩进级别）
        while self.current_token.type != TokenType.EOF and (self.current_token.type == TokenType.PY_FOR or self.current_token.type == TokenType.ID):
            if self.current_token.type == TokenType.PY_FOR:
                self.parse_python_for_stmt()
            elif self.current_token.type == TokenType.ID:
                self.parse_py_assign_stmt()
        
        # 发射循环变量增量：loop_var = loop_var + step_expr
        self.emit('+', loop_var, step_expr, loop_var)
        
        # 发射跳回条件检查
        self.emit('JMP', None, None, label_cond_check)
        
        # 发射循环结束标签
        self.emit('LABEL', None, None, label_loop_end)
        
        return self.quadruples

    def parse_assign_stmt(self):
        # <assign_stmt> -> <id> := <expr>
        target_var_token = self.current_token
        self.eat(TokenType.ID)
        target_var = target_var_token.value

        if self.language_type == LanguageType.PSEUDO:
            self.eat(TokenType.ASSIGN)  # ':='
        else:
            self.eat(TokenType.ASSIGN)  # '='

        # 解析右侧的表达式
        expr_result = self.parse_expr()

        # 发射赋值四元式
        self.emit(':=', expr_result, None, target_var)
        
        if self.language_type == LanguageType.C_STYLE:
            self.eat(TokenType.SEMICOLON)

    def parse_py_assign_stmt(self):
        # Python风格的赋值语句，没有分号结尾
        target_var_token = self.current_token
        self.eat(TokenType.ID)
        target_var = target_var_token.value

        self.eat(TokenType.ASSIGN)  # '='

        # 解析右侧的表达式
        expr_result = self.parse_expr()

        # 发射赋值四元式
        self.emit(':=', expr_result, None, target_var)

    def parse_expr(self):
        # <expr> -> <term> { (+|-) <term> }
        # 处理 + 和 - 的左结合性
        result = self.parse_term()  # 解析第一项

        # 当当前标记是 PLUS 或 MINUS 时循环
        while self.current_token is not None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.ADD_ASSIGN, TokenType.SUB_ASSIGN):
            op_token = self.current_token
            self.eat(op_token.type)  # 消耗 '+', '-', '+=' 或 '-='
            
            # 确定操作符
            if op_token.type in (TokenType.ADD_ASSIGN, TokenType.SUB_ASSIGN):
                op = '+' if op_token.type == TokenType.ADD_ASSIGN else '-'
            else:
                op = op_token.value

            try:
                # 解析下一项（右操作数）
                right_operand = self.parse_term()
            except Exception as e:
                # 如果解析右操作数时出错，提供更有用的错误信息
                self.error(f"解析加减表达式时出错: 在 '{op}' 操作符后缺少有效操作数")
                raise

            # 为此操作的结果生成一个临时变量
            temp_var = self.new_temp()
            # 发射操作的四元式（例如 t1 = result + right_operand）
            self.emit(op, result, right_operand, temp_var)

            # 此操作的结果成为下一个操作的左操作数
            result = temp_var
            
            # 如果是复合赋值运算符，还需发射赋值操作
            if op_token.type in (TokenType.ADD_ASSIGN, TokenType.SUB_ASSIGN):
                # 假设结果要赋值给之前的左操作数（通常是变量）
                self.emit(':=', temp_var, None, result)

        return result  # 返回表达式的最终结果（可能是临时变量）

    def parse_term(self):
        # <term> -> <factor> { (*|/) <factor> }
        # 处理 * 和 / 的左结合性
        result = self.parse_factor()  # 解析第一个因子

        # 当当前标记是 MUL 或 DIV 时循环
        while self.current_token is not None and self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN):
            op_token = self.current_token
            self.eat(op_token.type)  # 消耗 '*', '/', '*=' 或 '/='
            
            # 确定操作符
            if op_token.type in (TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN):
                op = '*' if op_token.type == TokenType.MUL_ASSIGN else '/'
            else:
                op = op_token.value

            try:
                # 解析下一个因子（右操作数）
                right_operand = self.parse_factor()
            except Exception as e:
                # 如果解析右操作数时出错，提供更有用的错误信息
                self.error(f"解析乘除表达式时出错: 在 '{op}' 操作符后缺少有效操作数")
                raise

            # 为结果生成一个临时变量
            temp_var = self.new_temp()
            # 发射操作的四元式（例如 t2 = result * right_operand）
            self.emit(op, result, right_operand, temp_var)

            # 更新结果以用于下一个潜在操作
            result = temp_var
            
            # 如果是复合赋值运算符，还需发射赋值操作
            if op_token.type in (TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN):
                # 假设结果要赋值给之前的左操作数（通常是变量）
                self.emit(':=', temp_var, None, result)

        return result  # 返回项的最终结果

    def parse_factor(self):
        # <factor> -> <id> | <number> | ( <expr> ) | +<factor> | -<factor>
        token = self.current_token

        # 处理一元加减符号（如+x, -y）
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            # 一元加号可以简单地递归调用factor并返回结果
            return self.parse_factor()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            # 一元减号需要生成四元式来表示负值操作
            factor = self.parse_factor()
            temp = self.new_temp()
            self.emit('*', factor, -1, temp)  # 用乘以-1来表示负值
            return temp

        if token.type == TokenType.ID:
            self.eat(TokenType.ID)
            return token.value  # 返回变量名作为结果
        elif token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return token.value  # 返回数值作为结果
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            # 递归解析括号内的表达式
            result = self.parse_expr()
            self.eat(TokenType.RPAREN)
            return result  # 返回内部表达式的结果
        else:
            # 如果遇到其它操作符（如/），提供更有用的错误消息
            unexpected_token = self.current_token
            # 尝试进行恢复 - 跳过当前的token并继续解析
            self.advance_token()  # 这是一个新函数，需要添加
            self.error(f"语法错误：在'factor'位置遇到了意外的操作符 '{unexpected_token.value}'。可能缺少操作数或括号。")

    def advance_token(self):
        """帮助恢复解析的函数，跳过当前token"""
        self.current_token = self.lexer.get_next_token()

# --- UI 调用的主翻译函数 ---

def translate_to_quadruples(code, language_type=LanguageType.PSEUDO):
    """接收源代码字符串和语言类型，返回一个 Quadruple 对象列表。"""
    if not code.strip():
        return []  # 对于空输入返回空列表
    try:
        # 打印一下输入代码，帮助调试
        # print(f"开始翻译 {language_type} 代码: {code}")
        
        lexer = Lexer(code, language_type)
        parser = Parser(lexer)
        quadruples = parser.parse()
        
        # 调试信息：打印生成的四元式（可选）
        # for i, q in enumerate(quadruples):
        #     print(f"{i}: {q}")
            
        return quadruples
    except Exception as e:
        # 提供更详细的错误信息
        import traceback
        error_msg = f"翻译错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # 开发时输出错误到控制台
        
        # 对于Python风格的表达式，提供特别的处理
        if language_type == LanguageType.PYTHON and ('/' in code or '*' in code):
            err_details = "检测到Python风格代码中可能存在问题的乘除运算表达式。"
            err_details += "\n可能的问题原因："
            err_details += "\n1. 表达式中缺少操作数，例如 'a * / b' 或 'a / * b'"
            err_details += "\n2. 表达式格式不正确，例如 '(a * )b' 或 'a(/ b)'"
            err_details += "\n3. 使用了复杂的表达式嵌套，例如 'a * (b / (c * d))'"
            err_details += "\n请检查表达式格式是否正确，确保每个操作符都有合法的左右操作数。"
            print(err_details)
            
            # 重新引发带有更多详细信息的异常
            raise Exception(f"翻译错误: {str(e)}\n{err_details}")
        
        # 重新引发异常，以便 UI 捕获并显示
        raise Exception(f"翻译错误: {str(e)}")

# 示例用法（用于无 UI 测试）
if __name__ == "__main__":
    # 伪代码风格测试用例
    pseudo_test_cases = [
        "FOR i := 1 TO 10 DO x := x + i ENDFOR",
        "FOR count := start + 1 TO end * 2 DO result := 1 ENDFOR",
    ]

    # C语言风格测试用例
    c_style_test_cases = [
        "for (i = 1; i < 10; i++) { x = x + i; }",
        "for (count = start + 1; count <= end * 2; count++) { result = 1; }",
    ]
    
    # Python风格测试用例
    python_test_cases = [
        "for i in range(1, 10): x = x + i",
        "for count in range(start + 1, end * 2): result = 1",
        "for j in range(10): y = y + 1",  # 单参数range
        "for k in range(0, 10, 2): z = z + k",  # 带步长的range
    ]

    print("--- 伪代码风格测试 ---")
    for i, code in enumerate(pseudo_test_cases):
        print(f"测试用例 {i+1}:")
        print(f"输入: {code}")
        print("输出四元式:")
        try:
            quads = translate_to_quadruples(code, LanguageType.PSEUDO)
            if quads:
                for j, q in enumerate(quads):
                    print(f"{j}: {q}")
            else:
                print("(没有生成四元式)")
        except Exception as e:
            print(f"错误: {e}")
        print("\n")

    print("--- C语言风格测试 ---")
    for i, code in enumerate(c_style_test_cases):
        print(f"测试用例 {i+1}:")
        print(f"输入: {code}")
        print("输出四元式:")
        try:
            quads = translate_to_quadruples(code, LanguageType.C_STYLE)
            if quads:
                for j, q in enumerate(quads):
                    print(f"{j}: {q}")
            else:
                print("(没有生成四元式)")
        except Exception as e:
            print(f"错误: {e}")
        print("\n")
        
    print("--- Python风格测试 ---")
    for i, code in enumerate(python_test_cases):
        print(f"测试用例 {i+1}:")
        print(f"输入: {code}")
        print("输出四元式:")
        try:
            quads = translate_to_quadruples(code, LanguageType.PYTHON)
            if quads:
                for j, q in enumerate(quads):
                    print(f"{j}: {q}")
            else:
                print("(没有生成四元式)")
        except Exception as e:
            print(f"错误: {e}")
        print("\n") 