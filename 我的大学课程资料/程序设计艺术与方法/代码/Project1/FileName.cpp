#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int N;
    if (!(cin >> N)) return 0;
    int k = N / 15;
    cout << k + (2 * k) / 5;
    return 0;
}
