#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <cmath>
#include <stack>
#include <cctype>
#include <algorithm>
#include <numeric>

using namespace std;

// 检查是否是命题变元
bool isProposition(char c) {
    return isalpha(c) && isupper(c);
}

int precedence(char op) {
    if (op == '!') return 4;
    if (op == '&') return 3;
    if (op == '|') return 2;
    if (op == '-' || op == '=') return 1; // -> 和 == 的优先级最低
    return -1; // 无效符号
}

// 解析公式为后缀表达式（逆波兰表达式）
vector<string> infixToPostfix(const string& formula) {
    stack<char> ops;
    vector<string> postfix;
    for (size_t i = 0; i < formula.size(); ++i) {
        char c = formula[i];
        if (isProposition(c)) {
            postfix.push_back(string(1, c));
        }
        else if (c == '(') {
            ops.push(c);
        }
        else if (c == ')') {
            while (!ops.empty() && ops.top() != '(') {
                postfix.push_back(string(1, ops.top()));
                ops.pop();
            }
            if (!ops.empty()) ops.pop(); // 弹出 '('
        }
        else if (c == '!' || c == '&' || c == '|') {
            while (!ops.empty() && precedence(ops.top()) >= precedence(c)) {
                postfix.push_back(string(1, ops.top()));
                ops.pop();
            }
            ops.push(c);
        }
        else if (c == '-' && i + 1 < formula.size() && formula[i + 1] == '>') {
            while (!ops.empty() && precedence(ops.top()) >= precedence('-')) {
                postfix.push_back(string(1, ops.top()));
                ops.pop();
            }
            ops.push('-');
            ++i; // 跳过 '>' 
        }
        else if (c == '=' && i + 1 < formula.size() && formula[i + 1] == '=') {
            while (!ops.empty() && precedence(ops.top()) >= precedence('=')) {
                postfix.push_back(string(1, ops.top()));
                ops.pop();
            }
            ops.push('=');
            ++i; // 跳过第二个 '='
        }
    }
    while (!ops.empty()) {
        postfix.push_back(string(1, ops.top()));
        ops.pop();
    }
    return postfix;
}

// 计算后缀表达式结果
bool evaluatePostfix(const vector<string>& postfix, const map<char, bool>& values) {
    stack<bool> eval;
    for (const string& token : postfix) {
        if (token.size() == 1 && isProposition(token[0])) {
            eval.push(values.at(token[0]));
        }
        else if (token == "!") {
            bool a = eval.top(); eval.pop();
            eval.push(!a);
        }
        else if (token == "&") {
            bool b = eval.top(); eval.pop();
            bool a = eval.top(); eval.pop();
            eval.push(a && b);
        }
        else if (token == "|") {
            bool b = eval.top(); eval.pop();
            bool a = eval.top(); eval.pop();
            eval.push(a || b);
        }
        else if (token == "-") {
            bool b = eval.top(); eval.pop();
            bool a = eval.top(); eval.pop();
            eval.push(!a || b);
        }
        else if (token == "=") {
            bool b = eval.top(); eval.pop();
            bool a = eval.top(); eval.pop();
            eval.push((!a || b) && (!b || a)); // 等价于 (!a || b) && (!b || a)
        }
    }
    return eval.top();
}

// 构建最小项或最大项表示
string buildTerm(const vector<char>& propositions, const map<char, bool>& values, bool pdnf) {
    string term;
    for (char prop : propositions) {
        if (values.at(prop)) {
            term += pdnf ? string(1, prop) : "!" + string(1, prop);
        }
        else {
            term += pdnf ? "!" + string(1, prop) : string(1, prop);
        }
        term += " & ";
    }
    term.erase(term.length() - 3); // 移除最后多余的 " & "
    return term;
}

// 生成主析取范式和主合取范式
void generateNormalForms(const string& formula) {
    vector<char> propositions;
    for (char c : formula) {
        if (isProposition(c) && find(propositions.begin(), propositions.end(), c) == propositions.end()) {
            propositions.push_back(c);
        }
    }

    vector<string> postfix = infixToPostfix(formula);

    size_t n = propositions.size();
    size_t rows = 1 << n;
    vector<string> pdnfTerms, pcnfTerms;

    for (size_t i = 0; i < rows; ++i) {
        map<char, bool> values;
        for (size_t j = 0; j < n; ++j) {
            values[propositions[j]] = (i & (1 << (n - j - 1))) != 0;
        }
        bool result = evaluatePostfix(postfix, values);
        if (result) {
            pdnfTerms.push_back(buildTerm(propositions, values, true));
        }
        else {
            pcnfTerms.push_back(buildTerm(propositions, values, false));
        }
    }

    cout << "主析取范式: " << (pdnfTerms.empty() ? "False" : accumulate(pdnfTerms.begin(), pdnfTerms.end(), string(), [](const string& a, const string& b) { return a + (a.empty() ? "" : " | ") + b; })) << endl;

    cout << "主合取范式: " << (pcnfTerms.empty() ? "True" : accumulate(pcnfTerms.begin(), pcnfTerms.end(), string(), [](const string& a, const string& b) { return a + (a.empty() ? "" : " & ") + b; })) << endl;
}

// 主函数
int main() {
    string formula;
    cout << "输入命题公式,其中&表示合取，|表示析取，！表示非，->表示蕴含，==表示等价: " << endl;
    cout << "必须用大写字母表示变元而且从A按顺序开始：";
    cin >> formula;

    generateNormalForms(formula);

    return 0;
}

