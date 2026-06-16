#include "restaurant.h"
#include <iostream>
#include <algorithm>
#include <fstream>

void Dish::displayDishInfo() const {
    std::cout << "菜品ID: " << id_ << "\n"
        << "名称: " << name_ << "\n"
        << "价格: " << price_ << "\n"
        << "评分: " << rating_ << "\n";
}

void Order::displayOrderInfo() const {
    std::cout << "订单ID: " << id_ << "\n"
        << "下单时间: " << order_time_ << "\n"
        << "总金额: " << total_amount_ << "\n"
        << "状态: " << status_ << "\n";
}

void Customer::displayCustomerInfo() const {
    std::cout << "顾客ID: " << id_ << "\n"
        << "姓名: " << name_ << "\n"
        << "电话: " << phone_ << "\n";
}

void Restaurant::displayAllDishes() const {
    if (dishes_.empty()) {
        std::cout << "暂无菜品信息\n";
        return;
    }
    for (const auto& dish : dishes_) {
        dish.displayDishInfo();
        std::cout << "------------------------\n";
    }
}

void Restaurant::displayAllOrders() const {
    if (orders_.empty()) {
        std::cout << "暂无订单信息\n";
        return;
    }
    for (const auto& order : orders_) {
        order.displayOrderInfo();
        std::cout << "------------------------\n";
    }
}

void Restaurant::displayAllCustomers() const {
    if (customers_.empty()) {
        std::cout << "暂无顾客信息\n";
        return;
    }
    for (const auto& customer : customers_) {
        customer.displayCustomerInfo();
        std::cout << "------------------------\n";
    }
}

Dish* Restaurant::findDish(int id) {
    auto it = std::find_if(dishes_.begin(), dishes_.end(),
        [id](const Dish& dish) { return dish.getDishId() == id; });
    return it != dishes_.end() ? &(*it) : nullptr;
}

Order* Restaurant::findOrder(int id) {
    auto it = std::find_if(orders_.begin(), orders_.end(),
        [id](const Order& order) { return order.getOrderId() == id; });
    return it != orders_.end() ? &(*it) : nullptr;
}

Customer* Restaurant::findCustomer(int id) {
    auto it = std::find_if(customers_.begin(), customers_.end(),
        [id](const Customer& customer) { return customer.getCustomerId() == id; });
    return it != customers_.end() ? &(*it) : nullptr;
}

void Restaurant::addDish(const Dish& dish) {
    if (!findDish(dish.getDishId())) {
        dishes_.push_back(dish);
        std::cout << "菜品添加成功\n";
    }
    else {
        std::cout << "菜品ID已存在\n";
    }
}

void Restaurant::addOrder(const Order& order) {
    if (!findOrder(order.getOrderId())) {
        orders_.push_back(order);
        std::cout << "订单添加成功\n";
    }
    else {
        std::cout << "订单ID已存在\n";
    }
}

void Restaurant::addCustomer(const Customer& customer) {
    if (!findCustomer(customer.getCustomerId())) {
        customers_.push_back(customer);
        std::cout << "顾客添加成功\n";
    }
    else {
        std::cout << "顾客ID已存在\n";
    }
}

void Restaurant::removeDish(int id) {
    auto it = std::find_if(dishes_.begin(), dishes_.end(),
        [id](const Dish& dish) { return dish.getDishId() == id; });
    if (it != dishes_.end()) {
        dishes_.erase(it);
        std::cout << "菜品删除成功\n";
    }
    else {
        std::cout << "未找到该菜品\n";
    }
}

void Restaurant::removeOrder(int id) {
    auto it = std::find_if(orders_.begin(), orders_.end(),
        [id](const Order& order) { return order.getOrderId() == id; });
    if (it != orders_.end()) {
        orders_.erase(it);
        std::cout << "订单删除成功\n";
    }
    else {
        std::cout << "未找到该订单\n";
    }
}

void Restaurant::removeCustomer(int id) {
    auto it = std::find_if(customers_.begin(), customers_.end(),
        [id](const Customer& customer) { return customer.getCustomerId() == id; });
    if (it != customers_.end()) {
        customers_.erase(it);
        std::cout << "顾客删除成功\n";
    }
    else {
        std::cout << "未找到该顾客\n";
    }
}

void Restaurant::updateDish(int id, const Dish& newDish) {
    auto it = std::find_if(dishes_.begin(), dishes_.end(),
        [id](const Dish& dish) { return dish.getDishId() == id; });
    if (it != dishes_.end()) {
        *it = newDish;
        std::cout << "菜品更新成功\n";
    }
    else {
        std::cout << "未找到该菜品\n";
    }
}

void Restaurant::updateOrder(int id, const Order& newOrder) {
    auto it = std::find_if(orders_.begin(), orders_.end(),
        [id](const Order& order) { return order.getOrderId() == id; });
    if (it != orders_.end()) {
        *it = newOrder;
        std::cout << "订单更新成功\n";
    }
    else {
        std::cout << "未找到该订单\n";
    }
}

void Restaurant::updateCustomer(int id, const Customer& newCustomer) {
    auto it = std::find_if(customers_.begin(), customers_.end(),
        [id](const Customer& customer) { return customer.getCustomerId() == id; });
    if (it != customers_.end()) {
        *it = newCustomer;
        std::cout << "顾客信息更新成功\n";
    }
    else {
        std::cout << "未找到该顾客\n";
    }
}

void Restaurant::loadFromFiles() {
    try {
        dishes_.clear();
        orders_.clear();
        customers_.clear();

        // 读取菜品数据
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
                dishes_.push_back(dish);
            }
        }
        dishFile.close();

        // 读取订单数据
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
                orders_.push_back(order);
            }
        }
        orderFile.close();

        // 读取顾客数据
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
                customers_.push_back(customer);
            }
        }
        customerFile.close();

        std::cout << "数据加载成功\n";
    }
    catch (const std::exception& e) {
        std::cerr << "文件读取错误: " << e.what() << std::endl;
    }
}

void Restaurant::saveToFiles() const {
    try {
        // 保存菜品数据
        std::ofstream dishFile(DISHES_FILE);
        for (const auto& dish : dishes_) {
            dishFile << dish.getDishId() << ","
                << dish.getDishName() << ","
                << dish.getPrice() << ","
                << dish.getRating() << "\n";
        }
        dishFile.close();

        // 保存订单数据
        std::ofstream orderFile(ORDERS_FILE);
        for (const auto& order : orders_) {
            orderFile << order.getOrderId() << ","
                << order.getOrderTime() << ","
                << order.getTotalAmount() << ","
                << order.getOrderStatus() << "\n";
        }
        orderFile.close();

        // 保存顾客数据
        std::ofstream customerFile(CUSTOMERS_FILE);
        for (const auto& customer : customers_) {
            customerFile << customer.getCustomerId() << ","
                << customer.getName() << ","
                << customer.getPhoneNumber() << "\n";
        }
        customerFile.close();

        std::cout << "数据保存成功\n";
    }
    catch (const std::exception& e) {
        std::cerr << "文件保存错误: " << e.what() << std::endl;
    }
}
