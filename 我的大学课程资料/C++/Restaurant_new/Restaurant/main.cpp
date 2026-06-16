#include <iostream>
#include "show_menu.h"
#include "restaurant.h"

int main() {
	Restaurant restaurant;
	int choice;

	do {
		showMenu();
		std::cin >> choice;

		if (choice >= 0 && choice <= 4) {
			switch_func(restaurant, choice);
		}
		else {
			std::cout << "无效选项，请重新选择。\n";
		}
	} while (choice != 0);

	return 0;
}
