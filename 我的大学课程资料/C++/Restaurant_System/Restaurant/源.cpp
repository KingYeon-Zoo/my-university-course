#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <iomanip>

class Dish {
private:
	int dishId;
	std::string dishName;
	double price;
	double rating;

public:
	Dish() : dishId(0), price(0.0), rating(0.0) {}

	Dish(int id, const std::string& name, double dishPrice, double dishRating)
		: dishId(id), dishName(name), price(dishPrice), rating(dishRating) {}

	int getDishId() const { return dishId; }
	std::string getDishName() const { return dishName; }
	double getPrice() const { return price; }
	double getRating() const { return rating; }

	void setDishId(int id) { dishId = id; }
	void setDishName(const std::string& name) { dishName = name; }
	void setPrice(double dishPrice) { price = dishPrice; }
	void setRating(double dishRating) { rating = dishRating; }

	void displayDishInfo() const {
		std::cout << "菜品编号: " << dishId
			<< ", 名称: " << dishName
			<< ", 价格: " << price
			<< ", 评分: " << rating << std::endl;
	}
};

class Order {
private:
	int orderId;
	std::string orderTime;
	double totalAmount;
	std::string orderStatus;

public:
	Order() : orderId(0), totalAmount(0.0) {}

	Order(int id, const std::string& time, double amount, const std::string& status)
		: orderId(id), orderTime(time), totalAmount(amount), orderStatus(status) {}

	int getOrderId() const { return orderId; }
	std::string getOrderTime() const { return orderTime; }
	double getTotalAmount() const { return totalAmount; }
	std::string getOrderStatus() const { return orderStatus; }

	void setOrderId(int id) { orderId = id; }
	void setOrderTime(const std::string& time) { orderTime = time; }
	void setTotalAmount(double amount) { totalAmount = amount; }
	void setOrderStatus(const std::string& status) { orderStatus = status; }

	void displayOrderInfo() const {
		std::cout << "订单编号: " << orderId
			<< ", 下单时间: " << orderTime
			<< ", 总金额: " << totalAmount
			<< ", 订单状态: " << orderStatus << std::endl;
	}
};

class Customer {
private:
	int customerId;
	std::string name;
	std::string phoneNumber;

public:
	Customer() : customerId(0) {}

	Customer(int id, const std::string& customerName, const std::string& phone)
		: customerId(id), name(customerName), phoneNumber(phone) {}

	int getCustomerId() const { return customerId; }
	std::string getName() const { return name; }
	std::string getPhoneNumber() const { return phoneNumber; }

	void setCustomerId(int id) { customerId = id; }
	void setName(const std::string& customerName) { name = customerName; }
	void setPhoneNumber(const std::string& phone) { phoneNumber = phone; }

	void displayCustomerInfo() const {
		std::cout << "顾客编号: " << customerId
			<< ", 姓名: " << name
			<< ", 电话: " << phoneNumber << std::endl;
	}
};

class Restaurant {
private:
	std::vector<Dish> dishes;
	std::vector<Order> orders;
	std::vector<Customer> customers;

	const std::string DISHES_FILE = "dishes.txt";
	const std::string ORDERS_FILE = "orders.txt";
	const std::string CUSTOMERS_FILE = "customers.txt";

public:
	const std::vector<Dish>& getDishes() const {
		return dishes;
	}

	const std::vector<Order>& getOrders() const {
		return orders;
	}

	const std::vector<Customer>& getCustomers() const {
		return customers;
	}

	void addDish(const Dish& dish) {
		dishes.push_back(dish);
	}

	void removeDish(int dishId) {
		dishes.erase(
			std::remove_if(dishes.begin(), dishes.end(),
				[dishId](const Dish& dish) { return dish.getDishId() == dishId; }),
			dishes.end()
		);
	}

	void updateDish(int dishId, const Dish& newDish) {
		for (auto& dish : dishes) {
			if (dish.getDishId() == dishId) {
				dish = newDish;
				break;
			}
		}
	}

	Dish* findDish(int dishId) {
		auto it = std::find_if(dishes.begin(), dishes.end(),
			[dishId](const Dish& dish) { return dish.getDishId() == dishId; });

		return (it != dishes.end()) ? &(*it) : nullptr;
	}

	void sortDishesByPrice() {
		std::sort(dishes.begin(), dishes.end(),
			[](const Dish& a, const Dish& b) { return a.getPrice() < b.getPrice(); });
	}

	void addOrder(const Order& order) {
		orders.push_back(order);
	}

	void removeOrder(int orderId) {
		orders.erase(
			std::remove_if(orders.begin(), orders.end(),
				[orderId](const Order& order) { return order.getOrderId() == orderId; }),
			orders.end()
		);
	}

	void updateOrder(int orderId, const Order& newOrder) {
		for (auto& order : orders) {
			if (order.getOrderId() == orderId) {
				order = newOrder;
				break;
			}
		}
	}

	Order* findOrder(int orderId) {
		auto it = std::find_if(orders.begin(), orders.end(),
			[orderId](const Order& order) { return order.getOrderId() == orderId; });

		return (it != orders.end()) ? &(*it) : nullptr;
	}

	void addCustomer(const Customer& customer) {
		customers.push_back(customer);
	}

	void removeCustomer(int customerId) {
		customers.erase(
			std::remove_if(customers.begin(), customers.end(),
				[customerId](const Customer& customer) { return customer.getCustomerId() == customerId; }),
			customers.end()
		);
	}

	void updateCustomer(int customerId, const Customer& newCustomer) {
		for (auto& customer : customers) {
			if (customer.getCustomerId() == customerId) {
				customer = newCustomer;
				break;
			}
		}
	}

	Customer* findCustomer(int customerId) {
		auto it = std::find_if(customers.begin(), customers.end(),
			[customerId](const Customer& customer) { return customer.getCustomerId() == customerId; });

		return (it != customers.end()) ? &(*it) : nullptr;
	}

	void saveToFiles() {
		std::ofstream dishFile(DISHES_FILE);
		for (const auto& dish : dishes) {
			dishFile << dish.getDishId() << ","
				<< dish.getDishName() << ","
				<< dish.getPrice() << ","
				<< dish.getRating() << std::endl;
		}
		dishFile.close();

		std::ofstream orderFile(ORDERS_FILE);
		for (const auto& order : orders) {
			orderFile << order.getOrderId() << ","
				<< order.getOrderTime() << ","
				<< order.getTotalAmount() << ","
				<< order.getOrderStatus() << std::endl;
		}
		orderFile.close();

		std::ofstream customerFile(CUSTOMERS_FILE);
		for (const auto& customer : customers) {
			customerFile << customer.getCustomerId() << ","
				<< customer.getName() << ","
				<< customer.getPhoneNumber() << std::endl;
		}
		customerFile.close();
	}

	void loadFromFiles() {
		try {
			dishes.clear();
			orders.clear();
			customers.clear();

			std::ifstream dishFile(DISHES_FILE);
			std::string line;
			while (std::getline(dishFile, line)) {
				std::stringstream ss(line);
				std::string item;
				std::vector<std::string> tokens;

				while (std::getline(ss, item, ',')) {
					tokens.push_back(item);
				}

				if (tokens.size() == 4) {
					Dish dish(std::stoi(tokens[0]), tokens[1],
						std::stod(tokens[2]), std::stod(tokens[3]));
					dishes.push_back(dish);
				}
			}
			dishFile.close();

			std::ifstream orderFile(ORDERS_FILE);
			while (std::getline(orderFile, line)) {
				std::stringstream ss(line);
				std::string item;
				std::vector<std::string> tokens;

				while (std::getline(ss, item, ',')) {
					tokens.push_back(item);
				}

				if (tokens.size() == 4) {
					Order order(std::stoi(tokens[0]), tokens[1],
						std::stod(tokens[2]), tokens[3]);
					orders.push_back(order);
				}
			}
			orderFile.close();

			std::ifstream customerFile(CUSTOMERS_FILE);
			while (std::getline(customerFile, line)) {
				std::stringstream ss(line);
				std::string item;
				std::vector<std::string> tokens;

				while (std::getline(ss, item, ',')) {
					tokens.push_back(item);
				}

				if (tokens.size() == 3) {
					Customer customer(std::stoi(tokens[0]), tokens[1], tokens[2]);
					customers.push_back(customer);
				}
			}
			customerFile.close();
		}
		catch (const std::exception& e) {
			std::cerr << "文件读取错误: " << e.what() << std::endl;
		}
	}

	void displayAllDishes() {
		std::cout << "所有餐品：" << std::endl;
		for (const auto& dish : dishes) {
			dish.displayDishInfo();
		}
	}

	void displayAllOrders() {
		std::cout << "所有订单：" << std::endl;
		for (const auto& order : orders) {
			order.displayOrderInfo();
		}
	}

	void displayAllCustomers() {
		std::cout << "所有顾客：" << std::endl;
		for (const auto& customer : customers) {
			customer.displayCustomerInfo();
		}
	}
};

void saveDataBeforeExit(Restaurant& restaurant) {
	char confirmSave;
	std::cout << "您确定要退出系统并保存所有数据吗？(y/n): ";
	std::cin >> confirmSave;

	if (confirmSave == 'y' || confirmSave == 'Y') {
		restaurant.saveToFiles();
		std::cout << "数据已保存，系统即将退出。\n";
	}
	else {
		std::cout << "未保存数据，系统将继续运行。\n";
	}
}

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
				std::cout << "请输入菜品编号、名称、价格、评分: ";
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
				if (phoneNumber.length() != 11) {
					std::cout << "电话号码必须是11位！\n";
					break;
				}
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
				if (phoneNumber.length() != 11) {
					std::cout << "电话号码必须是11位！\n";
					break;
				}
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


int main() {
	Restaurant restaurant;
	restaurant.loadFromFiles();

	int choice;
	do {
		showMenu();
		std::cin >> choice;
		switch_func(restaurant, choice);
	} while (choice != 0);

	return 0;
}
