#include "show_menu.h"
#include <iostream>
#include "restaurant.h"

// 声明外部函数
void saveDataBeforeExit(Restaurant& restaurant);

void showMenu() {
	std::cout << "\n╔════════════════════════════╗\n";
	std::cout << "║    餐厅管理系统主菜单      ║\n";
	std::cout << "╠════════════════════════════╣\n";
	std::cout << "║  1. 餐品管理               ║\n";
	std::cout << "║  2. 订单管理               ║\n";
	std::cout << "║  3. 顾客管理               ║\n";
	std::cout << "║  4. 读取数据               ║\n";
	std::cout << "║  0. 退出系统               ║\n";
	std::cout << "╚════════════════════════════╝\n";
	std::cout << "请选择操作类别: ";
}

void showDishMenu() {
	std::cout << "\n╔════════════════════════════╗\n";
	std::cout << "║        餐品管理菜单        ║\n";
	std::cout << "╠════════════════════════════╣\n";
	std::cout << "║  1. 显示所有餐品           ║\n";
	std::cout << "║  2. 根据编号查找餐品       ║\n";
	std::cout << "║  3. 根据名称查找餐品       ║\n";
	std::cout << "║  4. 添加餐品               ║\n";
	std::cout << "║  5. 删除餐品               ║\n";
	std::cout << "║  6. 修改餐品信息           ║\n";
	std::cout << "║  0. 返回主菜单             ║\n";
	std::cout << "╚════════════════════════════╝\n";
	std::cout << "请选择操作: ";
}

void showOrderMenu() {
	std::cout << "\n╔════════════════════════════╗\n";
	std::cout << "║        订单管理菜单        ║\n";
	std::cout << "╠════════════════════════════╣\n";
	std::cout << "║  1. 显示所有订单           ║\n";
	std::cout << "║  2. 根据编号查找订单       ║\n";
	std::cout << "║  3. 根据时间查找订单       ║\n";
	std::cout << "║  4. 添加订单               ║\n";
	std::cout << "║  5. 删除订单               ║\n";
	std::cout << "║  6. 修改订单信息           ║\n";
	std::cout << "║  0. 返回主菜单             ║\n";
	std::cout << "╚════════════════════════════╝\n";
	std::cout << "请选择操作: ";
}

void showCustomerMenu() {
	std::cout << "\n╔════════════════════════════╗\n";
	std::cout << "║        顾客管理菜单        ║\n";
	std::cout << "╠════════════════════════════╣\n";
	std::cout << "║  1. 显示所有顾客           ║\n";
	std::cout << "║  2. 根据编号查找顾客       ║\n";
	std::cout << "║  3. 根据姓名查找顾客       ║\n";
	std::cout << "║  4. 添加顾客               ║\n";
	std::cout << "║  5. 删除顾客               ║\n";
	std::cout << "║  6. 修改顾客信息           ║\n";
	std::cout << "║  0. 返回主菜单             ║\n";
	std::cout << "╚════════════════════════════╝\n";
	std::cout << "请选择操作: ";
}

void switch_func(Restaurant& restaurant, int choice) {
	int subChoice;
	int id;
	std::string name, orderTime, orderStatus, phoneNumber;
	double price, rating, totalAmount;

	switch (choice) {
	case 1:
		do {
			showDishMenu();
			std::cin >> subChoice;
			switch (subChoice) {
			case 1:
				restaurant.displayAllDishes();
				break;
			case 2:
				std::cout << "请输入菜品编号: ";
				std::cin >> id;
				if (auto dish = restaurant.findDish(id)) {
					dish->displayDishInfo();
				}
				else {
					std::cout << "未找到该菜品。\n";
				}
				break;
			case 3:
				std::cout << "请输入菜品名称: ";
				std::cin >> name;
				{
					bool found = false;
					for (const auto& dish : restaurant.getDishes()) {
						if (dish.getDishName() == name) {
							dish.displayDishInfo();
							found = true;
						}
					}
					if (!found) {
						std::cout << "未找到该菜品。\n";
					}
				}
				break;
			case 4:
				std::cout << "请输入菜品编号、名称、价格、评分: ";
				std::cin >> id >> name >> price >> rating;
				restaurant.addDish(Dish(id, name, price, rating));
				break;
			case 5:
				std::cout << "请输入要删除的菜品编号: ";
				std::cin >> id;
				restaurant.removeDish(id);
				break;
			case 6:
				std::cout << "请输入菜品编号、名称、��格、评分: ";
				std::cin >> id >> name >> price >> rating;
				restaurant.updateDish(id, Dish(id, name, price, rating));
				break;
			case 0:
				break;
			default:
				std::cout << "无效选项，请重新选择。\n";
			}
		} while (subChoice != 0);
		break;

	case 2:
		do {
			showOrderMenu();
			std::cin >> subChoice;
			switch (subChoice) {
			case 1:
				restaurant.displayAllOrders();
				break;
			case 2:
				std::cout << "请输入订单编号: ";
				std::cin >> id;
				if (auto order = restaurant.findOrder(id)) {
					order->displayOrderInfo();
				}
				else {
					std::cout << "未找到该订单。\n";
				}
				break;
			case 3:
				std::cout << "请输入订单时间: ";
				std::cin >> orderTime;
				{
					bool found = false;
					for (const auto& order : restaurant.getOrders()) {
						if (order.getOrderTime() == orderTime) {
							order.displayOrderInfo();
							found = true;
						}
					}
					if (!found) {
						std::cout << "未找到该订单。\n";
					}
				}
				break;
			case 4:
				std::cout << "请输入订单编号、时间、总金额、状态: ";
				std::cin >> id >> orderTime >> totalAmount >> orderStatus;
				restaurant.addOrder(Order(id, orderTime, totalAmount, orderStatus));
				break;
			case 5:
				std::cout << "请输入要删除的订单编号: ";
				std::cin >> id;
				restaurant.removeOrder(id);
				break;
			case 6:
				std::cout << "请输入订单编号、时间、总金额、状态: ";
				std::cin >> id >> orderTime >> totalAmount >> orderStatus;
				restaurant.updateOrder(id, Order(id, orderTime, totalAmount, orderStatus));
				break;
			case 0:
				break;
			default:
				std::cout << "无效选项，请重新选择。\n";
			}
		} while (subChoice != 0);
		break;

	case 3:
		do {
			showCustomerMenu();
			std::cin >> subChoice;
			switch (subChoice) {
			case 1:
				restaurant.displayAllCustomers();
				break;
			case 2:
				std::cout << "请输入顾客编号: ";
				std::cin >> id;
				if (auto customer = restaurant.findCustomer(id)) {
					customer->displayCustomerInfo();
				}
				else {
					std::cout << "未找到该顾客。\n";
				}
				break;
			case 3:
				std::cout << "请输入顾客姓名: ";
				std::cin >> name;
				{
					bool found = false;
					for (const auto& customer : restaurant.getCustomers()) {
						if (customer.getName() == name) {
							customer.displayCustomerInfo();
							found = true;
						}
					}
					if (!found) {
						std::cout << "未找到该顾客。\n";
					}
				}
				break;
			case 4:
				std::cout << "请输入顾客编号、姓名、电话: ";
				std::cin >> id >> name >> phoneNumber;
				restaurant.addCustomer(Customer(id, name, phoneNumber));
				break;
			case 5:
				std::cout << "请输入要删除的顾客编号: ";
				std::cin >> id;
				restaurant.removeCustomer(id);
				break;
			case 6:
				std::cout << "请输入顾客编号、姓名、电话: ";
				std::cin >> id >> name >> phoneNumber;
				restaurant.updateCustomer(id, Customer(id, name, phoneNumber));
				break;
			case 0:
				break;
			default:
				std::cout << "无效选项，请重新选择。\n";
			}
		} while (subChoice != 0);
		break;

	case 4:
		restaurant.loadFromFiles();
		std::cout << "读取成功\n";
		break;

	case 0:
		saveDataBeforeExit(restaurant);
		break;

	default:
		std::cout << "无效选项，请重新选择。\n";
	}
}

void saveDataBeforeExit(Restaurant& restaurant) {
	char confirmSave;
	std::cout << "您确定要退出系统并保存所有数据吗？(y/n): ";
	std::cin >> confirmSave;

	if (confirmSave == 'y' || confirmSave == 'Y') {
		restaurant.saveToFiles();
		std::cout << "数据已保存，系统即将退出。\n";
	}
	else {
		std::cout << "未保存数据，系统即将退出。\n";
	}
}