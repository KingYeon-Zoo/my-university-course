// 五种联结词优先级 ! * + @ $ 分别代表否定 合取 析取 单条件 双条件
//"规定符号代换规则为 ┐:!  ∧:*  ∨:+  ->:@  <->:$"
//"输入应当保证命题公式合法"
#include<iostream>
#include<cstring>
#include<stdlib.h>
using namespace std;
short int IsTrue[128]; //存储为真的真值指派
bool getTrue[128][7]; //存储所有的真值指派
int loc;//表示第几个真值指派类型
bool state[27]; //表示命题变元对应的真值
void set_getTrue() {
    for (int i = 0; i < 128; i++) {
        for (int j = 0; j < 7; j++) {
            getTrue[i][j] = 0;
        }
    }
}
int mi(int n) { //求2的n次幂
    int k = 1;
    for (int i = 0; i < n; i++) {
        k = k * 2;
    }
    return k;
}
template<class T>
class Stack {
private:
    int top;
    int maxnum;
    T* st;
public:
    Stack() {
        maxnum = 20;
        top = -1;
        st = new T[20];
    }
    ~Stack() {
        delete[] st;
    }
    void clean() {
        top = -1;
    }
    bool push(T n) {
        if (IsFull()) {
            return false; 
        }
        top++;
        this->st[top] = n;
        return true;
    }
    T get_top() {
        int k = st[top];
        top--;
        return k;
    }
    T read_top() {
        return st[this->top];
    }
    bool IsEmpty() {
        if (this->top == -1) return true;
        return false;
    }
    bool IsFull() {
        if (top + 1 == maxnum) return true;
        return false;
    }
};
class Calculator {
private:
    char InfixExp[30];
    char PostfixExp[30];
public:
    Calculator(char* exp);
    void getinf();
    void getpost();
    void ans(int nn);
    void trans();
};
void Calculator::getinf() {
    cout << InfixExp << endl;
}
void Calculator::getpost() {
    cout << PostfixExp << endl;
}
Calculator::Calculator(char* exp) {
    strcpy_s(this->InfixExp, sizeof(this->InfixExp), exp);
    for (int i = 0; i < 30; i++) {
        PostfixExp[i] = '\0';
    }
}
void Calculator::trans() {
    Stack<char> save;
    int i = 0, j = 0;
    while (this->InfixExp[i] != '\0') {
        if (this->InfixExp[i] >= 65 && this->InfixExp[i] <= 90) {
            while (this->InfixExp[i] >= 65 && this->InfixExp[i] <= 90) {
                PostfixExp[j] = this->InfixExp[i];
                j++; i++;
            }
            //PostfixExp[j]=' '; j++;
        }
        else {
            if (this->InfixExp[i] == '(' || this->InfixExp[i] == ')') {
                if (this->InfixExp[i] == '(') {
                    save.push(this->InfixExp[i]);
                }
                else if (this->InfixExp[i] == ')') {
                    if (save.IsEmpty()) {
                        cout << "WRONG!" << endl;
                        exit(0);
                    }
                    while (!save.IsEmpty() && save.read_top() != '(') {
                        PostfixExp[j] = save.get_top();
                        j++;
                    }
                    if (save.read_top() == '(') save.get_top();
                }
            }
            else {
                if (save.IsEmpty()) {
                    save.push(this->InfixExp[i]);
                }
                else {
                    if (this->InfixExp[i] == '!') {
                        char temp = save.read_top();
                        while (temp == '!' && temp != '(' && !save.IsEmpty()) {
                            PostfixExp[j] = save.get_top();
                            j++;
                            temp = save.read_top();
                        }
                        save.push(this->InfixExp[i]);
                    }
                    else
                        if (this->InfixExp[i] == '*') {
                            char temp = save.read_top();
                            while (temp != '+' && temp != '(' && !save.IsEmpty()) {
                                PostfixExp[j] = save.get_top();
                                j++;
                                temp = save.read_top();
                            }
                            save.push(this->InfixExp[i]);
                        }
                        else
                            if (this->InfixExp[i] == '+') {
                                char temp = save.read_top();
                                while ((temp == '*' || temp == '!') && !save.IsEmpty()) {
                                    PostfixExp[j] = save.get_top();
                                    j++;
                                    temp = save.read_top();
                                }
                                save.push(this->InfixExp[i]);
                            }
                            else
                                if (this->InfixExp[i] == '@') {
                                    char temp = save.read_top();
                                    while ((temp == '*' || temp == '!' || temp == '+') && !save.IsEmpty()) {
                                        PostfixExp[j] = save.get_top();
                                        j++;
                                        temp = save.read_top();
                                    }
                                    save.push(this->InfixExp[i]);
                                }
                                else
                                    if (this->InfixExp[i] == '$') {
                                        char temp = save.read_top();
                                        while ((temp == '*' || temp == '!' || temp == '+' || temp == '@') && !save.IsEmpty()) {
                                            PostfixExp[j] = save.get_top();
                                            j++;
                                            temp = save.read_top();
                                        }
                                        save.push(this->InfixExp[i]);
                                    }
                }

            }
            i++;
        }
    }
    while (!save.IsEmpty()) {
        PostfixExp[j] = save.get_top();
        j++;
    }
    PostfixExp[j] = '\0';
}
void Calculator::ans(int nn) {
    Stack<int> save_num;
    int i = 0, j = 0;
    int n1 = 0, n2 = 0;
    for (i = 0; i < nn; i++) {
        cout << ' ' << getTrue[loc][i] << ' ';
    }
    i = 0;
    while (this->PostfixExp[i] != '\0') {
        if (this->PostfixExp[i] >= 65 && this->PostfixExp[i] <= 90) {
            int temp = 0;
            temp = getTrue[loc][this->PostfixExp[i] - 65];
            i++;
            save_num.push(temp);
            //cout<<"temp="<<temp<<' ';
        }
        else if (this->PostfixExp[i] == '!') {
            n1 = save_num.get_top();
            n1 = 1 - n1;
            save_num.push(n1);
            i++;
        }
        else if (this->PostfixExp[i] == '+' || this->PostfixExp[i] == '*'
            || this->PostfixExp[i] == '@' || this->PostfixExp[i] == '$') {
            n2 = save_num.get_top();
            n1 = save_num.get_top();
            switch (this->PostfixExp[i]) {
            case('+'):
                n1 += n2;
                save_num.push(n1);
                break;
            case('*'):
                n1 *= n2;
                save_num.push(n1);
                break;
            case('@'):
                if (n1 > 0 && n2 == 0) n1 = 0;
                else n1 = 1;
                save_num.push(n1);
                break;
            case('$'):
                if ((n1 + n2 > 0) && (n1 * n2 == 0)) n1 = 0;
                else n1 = 1;
                save_num.push(n1);
                break;
            }
            i++;
        }
        else {
            i++;
        }
    }
    if (save_num.read_top() > 0) IsTrue[loc] = 1;
    else IsTrue[loc] = 0;
    //cout<<"ans="<<save_num.get_top()<<endl;
    cout << "  " << save_num.get_top() << endl;
}
void printxiqu(int num, int m) {
    int i, j;
    int temp = m;
    cout << "主析取范式: ";
    for (; temp > 0 && !IsTrue[temp]; temp--)
        m = temp;

    for (i = 0; i < m - 1; i++) {
        if (IsTrue[i] == 1) {
            cout << '(';
            for (j = 0; j < num - 1; j++) {
                if (getTrue[i][j] == 0) cout << "┐";
                cout << (char)(j + 65);
                cout << "∧";
            }
            if (getTrue[i][num - 1] == 0) cout << "┐";
            cout << (char)(j + 65);
            cout << ')';
            cout << "∨";
        }
    }
    i = m - 1;
    if (IsTrue[i] == 1) {
        cout << '(';
        for (j = 0; j < num - 1; j++) {
            if (getTrue[i][j] == 0) cout << "┐";
            cout << (char)(j + 65);
            cout << "∧";
        }
        if (getTrue[i][num - 1] == 0) cout << "┐";
        cout << (char)(j + 65);
        cout << ')';
    }
    cout << endl;
}
void printhequ(int num, int m) {
    int i, j;
    int temp = m;
    cout << "主合取范式: ";
    for (; temp > 0 && IsTrue[temp]; temp--)
        m = temp;

    for (i = 0; i < m - 1; i++) {
        if (IsTrue[i] == 0) {
            cout << '(';
            for (j = 0; j < num - 1; j++) {
                if (getTrue[i][j] == 1) cout << "┐";
                cout << (char)(j + 65);
                cout << "∨";
            }
            if (getTrue[i][num - 1] == 1) cout << "┐";
            cout << (char)(j + 65);
            cout << ')';
            cout << "∧";
        }
    }
    i = m - 1;
    if (IsTrue[i] == 0) {
        cout << '(';
        for (j = 0; j < num - 1; j++) {
            if (getTrue[i][j] == 1) cout << "┐";
            cout << (char)(j + 65);
            cout << "∨";
        }
        if (getTrue[i][num - 1] == 1) cout << "┐";
        cout << (char)(j + 65);
        cout << ')';
    }
    cout << endl;
}

int main() {
    for (int i = 0; i < 27; i++) state[i] = 0;
    for (int i = 0; i < 128; i++) IsTrue[i] = -1;
    set_getTrue();
    int i, j, m = 1;
    int num;//命题变元的数目
    cout << "输入命题公式中所含变元的数目：";
    cin >> num;
    for (i = 0; i < num; i++) m = m * 2;
    char exp[30];
    cout << "输入命题公式，且应当变元从A开始使用:";
    cin >> exp; //命题公式
    Calculator cal(exp);
    cal.trans();
    //cal.getpost();
    for (i = 0; i < m; i++) {
        int temp = i, tt = 0;
        for (j = 0; j < num - 1; j++) { //决定第j个命题变元的取值为0或1
            tt = mi(num - 1 - j); //cout<<"tt="<<tt<<endl;
            state[j] = temp / tt;
            temp = temp % tt;
        }
        state[num - 1] = temp;
        for (int k = 0; k < num; k++) {
            getTrue[i][k] = state[k];
        }
    }
    for (i = 0; i < m; i++) {
        for (j = 0; j < num; j++) {
            state[j] = getTrue[i][j];
        }
    }

    printxiqu(num, m);
    printhequ(num, m);

    return 0;
}