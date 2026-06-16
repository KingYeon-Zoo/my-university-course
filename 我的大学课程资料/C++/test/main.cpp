#include<iostream>
using namespace std;
class Base {
private:
	int x;
public:
	Base() {
		x = 100;
	}
	void show() {
		cout << "Base"<<x;
	}
	~Base() {
		cout << "Base Destructor\n"<<x;
	}
};

int main() {
	Base b;
	b.show();
	return 0;
}