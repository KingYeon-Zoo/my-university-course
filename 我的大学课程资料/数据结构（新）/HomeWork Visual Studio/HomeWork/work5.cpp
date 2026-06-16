//#include <iostream>
//#include <cstring>
//#include <cctype>
//#include <cstdlib>
//
//using namespace std;
//
//
//struct IntNode {
//    int data;
//    IntNode* next;
//
//    IntNode(int val) : data(val), next(nullptr) {}
//};
//
//
//struct CharNode {
//    char data;
//    CharNode* next;
//
//    CharNode(char val) : data(val), next(nullptr) {}
//};
//
//
//
//class IntStack {
//private:
//    IntNode* top;
//
//public:
//    IntStack() {
//        top = nullptr;
//    }
//
//    ~IntStack() {
//        while (!isEmpty()) {
//            pop();
//        }
//    }
//
//    bool isEmpty() {
//        return top == nullptr;
//    }
//
//    void push(int item) {
//        IntNode* newNode = new IntNode(item);
//        if (!newNode) {
//            cerr << "错误：内存分配失败！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        newNode->next = top;
//        top = newNode;
//    }
//
//    int pop() {
//        if (isEmpty()) {
//            cerr << "错误：整数栈下溢！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        int item = top->data;
//        IntNode* temp = top;
//        top = top->next;
//        delete temp;
//        return item;
//    }
//
//    int peek() {
//        if (isEmpty()) {
//            cerr << "错误：无法查看空整数栈的栈顶！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        return top->data;
//    }
//
//};
//
//
//class CharStack {
//private:
//    CharNode* top;
//
//public:
//    CharStack() {
//        top = nullptr;
//    }
//
//    ~CharStack() {
//        while (!isEmpty()) {
//            pop();
//        }
//    }
//
//    bool isEmpty() {
//        return top == nullptr;
//    }
//
//    void push(char item) {
//        CharNode* newNode = new CharNode(item);
//        if (!newNode) {
//            cerr << "错误：内存分配失败！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        newNode->next = top;
//        top = newNode;
//    }
//
//    int pop() {
//        if (isEmpty()) {
//            cerr << "错误：字符栈下溢！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        char item = top->data;
//        CharNode* temp = top;
//        top = top->next;
//        delete temp;
//        return item;
//    }
//
//    char peek() {
//        if (isEmpty()) {
//            cerr << "错误：无法查看空字符栈的栈顶！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        return top->data;
//    }
//
//};
//
//
//int getPrecedence(char op) {
//    if (op == '*' || op == '/') {
//        return 2;
//    }
//    else if (op == '+' || op == '-') {
//        return 1;
//    }
//    else if (op == '(') {
//        return 0;
//    }
//    return -1;
//}
//
//
//int applyOperation(int operand1, int operand2, char op) {
//    switch (op) {
//    case '+': return operand1 + operand2;
//    case '-': return operand1 - operand2;
//    case '*': return operand1 * operand2;
//    case '/':
//        if (operand2 == 0) {
//            cerr << "错误：除数为零！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        return operand1 / operand2;
//    default:
//        cerr << "错误：无效的操作符 '" << op << "'" << endl;
//        exit(EXIT_FAILURE);
//    }
//}
//
//
//int evaluateExpression(const char* expression) {
//    IntStack operandStack;
//    CharStack operatorStack;
//    int length = strlen(expression);
//
//    for (int i = 0; i < length; ++i) {
//
//        if (expression[i] == ' ') {
//            continue;
//        }
//
//
//        if (isdigit(expression[i])) {
//            int number = 0;
//
//            while (i < length && isdigit(expression[i])) {
//                number = number * 10 + (expression[i] - '0');
//                i++;
//            }
//            i--;
//            operandStack.push(number);
//
//        }
//
//        else if (expression[i] == '(') {
//            operatorStack.push(expression[i]);
//        }
//
//        else if (expression[i] == ')') {
//
//            while (!operatorStack.isEmpty() && operatorStack.peek() != '(') {
//                char op = operatorStack.pop();
//
//                if (operandStack.isEmpty()) {
//                    cerr << "错误：操作符 '" << op << "' 缺少操作数！" << endl;
//                    exit(EXIT_FAILURE);
//                }
//                int operand2 = operandStack.pop();
//                if (operandStack.isEmpty()) {
//                    cerr << "错误：操作符 '" << op << "' 缺少操作数！" << endl;
//                    exit(EXIT_FAILURE);
//                }
//                int operand1 = operandStack.pop();
//                int result = applyOperation(operand1, operand2, op);
//                operandStack.push(result);
//            }
//
//            if (operatorStack.isEmpty() || operatorStack.peek() != '(') {
//                cerr << "错误：括号不匹配！" << endl;
//                exit(EXIT_FAILURE);
//            }
//            operatorStack.pop();
//        }
//
//        else if (expression[i] == '+' || expression[i] == '-' || expression[i] == '*' || expression[i] == '/') {
//
//            char currentOp = expression[i];
//
//            while (!operatorStack.isEmpty() && operatorStack.peek() != '(' && getPrecedence(operatorStack.peek()) >= getPrecedence(currentOp)) {
//                char op = operatorStack.pop();
//                if (operandStack.isEmpty()) {
//                    cerr << "错误：操作符 '" << op << "' 缺少操作数！" << endl;
//                    exit(EXIT_FAILURE);
//                }
//                int operand2 = operandStack.pop();
//                if (operandStack.isEmpty()) {
//                    cerr << "错误：操作符 '" << op << "' 缺少操作数！" << endl;
//                    exit(EXIT_FAILURE);
//                }
//                int operand1 = operandStack.pop();
//                int result = applyOperation(operand1, operand2, op);
//                operandStack.push(result);
//            }
//
//            operatorStack.push(currentOp);
//        }
//        else {
//
//            cerr << "错误：表达式中存在无效字符：'" << expression[i] << "'" << endl;
//            exit(EXIT_FAILURE);
//        }
//    }
//
//
//    while (!operatorStack.isEmpty()) {
//        char op = operatorStack.pop();
//
//        if (op == '(') {
//            cerr << "错误：表达式末尾括号不匹配！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        if (operandStack.isEmpty()) {
//            cerr << "错误：末尾的操作符 '" << op << "' 缺少操作数！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        int operand2 = operandStack.pop();
//        if (operandStack.isEmpty()) {
//            cerr << "错误：末尾的操作符 '" << op << "' 缺少操作数！" << endl;
//            exit(EXIT_FAILURE);
//        }
//        int operand1 = operandStack.pop();
//        int result = applyOperation(operand1, operand2, op);
//        operandStack.push(result);
//    }
//
//
//    if (operandStack.isEmpty()) {
//        cerr << "错误：未计算出结果。表达式可能为空或无效。" << endl;
//        exit(EXIT_FAILURE);
//    }
//    int finalResult = operandStack.pop();
//
//
//    if (!operandStack.isEmpty()) {
//        cerr << "错误：表达式格式无效，剩余过多操作数。" << endl;
//        exit(EXIT_FAILURE);
//    }
//
//    return finalResult;
//}
//
//
//int main() {
//
//
//    cout << "简单整型算术表达式计算器 (链栈实现)" << endl;
//    cout << "支持 +, -, *, /, ()" << endl;
//    cout << "-----------------------------" << endl;
//
//
//    char inputExpression[256];
//    cout << "\n请输入一个表达式进行计算 (输入 'quit' 退出): ";
//    cin.getline(inputExpression, sizeof(inputExpression));
//
//    while (strcmp(inputExpression, "quit") != 0) {
//        cout << "计算: \"" << inputExpression << "\"" << endl;
//
//        int result = evaluateExpression(inputExpression);
//        cout << "结果: " << result << endl;
//        cout << "-----------------------------" << endl;
//        cout << "请输入一个表达式进行计算 (输入 'quit' 退出): ";
//
//        if (cin.fail()) {
//            cin.clear();
//
//        }
//        cin.getline(inputExpression, sizeof(inputExpression));
//    }
//
//    cout << "计算器已退出。" << endl;
//
//    return 0;
//}