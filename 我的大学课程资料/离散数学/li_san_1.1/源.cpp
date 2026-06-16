#include <iostream>
#include <iomanip>
#include <string>

using namespace std;

bool getBooleanInput(const string& prompt) {
    while (true) {
        cout << prompt << " (输入 1 表示 true，0 表示 false): ";
        int input;
        cin >> input;
        if (input == 0 || input == 1) {
            return static_cast<bool>(input);
        }
        else {
            cout << "无效输入，请输入 1 或 0。" << endl;
        }
    }
}

void printSingleRowOfTruthTable(bool p, bool q) {
    // 计算逻辑运算的结果
    bool not_p = !p;
    bool not_q = !q;
    bool and_result = p && q;
    bool or_result = p || q;
    bool imply_result = !p || q;
    bool equivalent_result = (p && q) || (!p && !q);

    // 打印标题
    cout << setw(5) << "p" << setw(5) << "q"
        << setw(10) << "!p" << setw(10) << "!q"
        << setw(10) << "p && q" << setw(10) << "p || q"
        << setw(10) << "p -> q" << setw(10) << "p <-> q" << endl;

    // 打印对应行
    cout << setw(5) << p << setw(5) << q
        << setw(10) << not_p << setw(10) << not_q
        << setw(10) << and_result << setw(10) << or_result
        << setw(10) << imply_result << setw(10) << equivalent_result
        << endl;
}

int main() {
    bool p = getBooleanInput("请输入命题变元 p 的值");
    bool q = getBooleanInput("请输入命题变元 q 的值");

    cout << "以下是根据您的输入生成的真值表：" << endl;
    printSingleRowOfTruthTable(p, q);

    return 0;
}