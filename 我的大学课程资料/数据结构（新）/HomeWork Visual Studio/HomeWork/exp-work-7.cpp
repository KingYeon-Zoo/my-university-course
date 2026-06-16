//#include <iostream>
//using namespace std;
//
//long long climbStairs(int n) {
//    if (n <= 0) return 0;
//    if (n == 1) return 1;
//    long long prev = 1;
//    long long curr = 2;
//    for (int i = 3; i <= n; ++i) {
//        long long next = prev + curr;
//        prev = curr;
//        curr = next;
//    }
//    return curr;
//}
//
//int main() {
//    int n;
//    cout << "请输入楼梯的总阶数 n: ";
//    if (!(cin >> n)) {
//        cout << "输入错误，请输入整数。" << endl;
//        return 0;
//    }
//    if (n <= 0) {
//        cout << "楼梯阶数应为正整数。" << endl;
//        return 0;
//    }
//
//    if (n > 92) {
//        cout << "n 过大，结果可能溢出，请限制在 1-92 范围内。" << endl;
//        return 0;
//    }
//
//    long long result = climbStairs(n);
//    cout << "不同的爬楼方法有: " << result << endl;
//    return 0;
//}
