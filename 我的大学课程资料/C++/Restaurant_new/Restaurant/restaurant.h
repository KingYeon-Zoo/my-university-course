#pragma once
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <iostream>

class Dish {
public:
    Dish(int id, const std::string& name, double price, double rating)
        : id_(id), name_(name), price_(price), rating_(rating) {}

    void displayDishInfo() const;
    int getDishId() const { return id_; }
    std::string getDishName() const { return name_; }
    double getPrice() const { return price_; }
    double getRating() const { return rating_; }

private:
    int id_;
    std::string name_;
    double price_;
    double rating_;
};

class Order {
public:
    Order(int id, const std::string& time, double amount, const std::string& status)
        : id_(id), order_time_(time), total_amount_(amount), status_(status) {}

    void displayOrderInfo() const;
    int getOrderId() const { return id_; }
    std::string getOrderTime() const { return order_time_; }
    double getTotalAmount() const { return total_amount_; }
    std::string getOrderStatus() const { return status_; }

private:
    int id_;
    std::string order_time_;
    double total_amount_;
    std::string status_;
};

class Customer {
public:
    Customer(int id, const std::string& name, const std::string& phone)
        : id_(id), name_(name), phone_(phone) {}

    void displayCustomerInfo() const;
    int getCustomerId() const { return id_; }
    std::string getName() const { return name_; }
    std::string getPhoneNumber() const { return phone_; }

private:
    int id_;
    std::string name_;
    std::string phone_;
};

class Restaurant {
public:
    void displayAllDishes() const;
    void displayAllOrders() const;
    void displayAllCustomers() const;

    Dish* findDish(int id);
    Order* findOrder(int id);
    Customer* findCustomer(int id);

    void addDish(const Dish& dish);
    void addOrder(const Order& order);
    void addCustomer(const Customer& customer);

    void removeDish(int id);
    void removeOrder(int id);
    void removeCustomer(int id);

    void updateDish(int id, const Dish& dish);
    void updateOrder(int id, const Order& order);
    void updateCustomer(int id, const Customer& customer);

    void loadFromFiles();
    void saveToFiles() const;

    const std::vector<Dish>& getDishes() const { return dishes_; }
    const std::vector<Order>& getOrders() const { return orders_; }
    const std::vector<Customer>& getCustomers() const { return customers_; }

private:
    std::vector<Dish> dishes_;
    std::vector<Order> orders_;
    std::vector<Customer> customers_;

    const std::string DISHES_FILE = "dishes.txt";
    const std::string ORDERS_FILE = "orders.txt";
    const std::string CUSTOMERS_FILE = "customers.txt";
};