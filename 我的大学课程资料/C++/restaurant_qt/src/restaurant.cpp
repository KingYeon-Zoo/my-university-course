/**
 * @file restaurant.cpp
 * @brief 餐厅管理类的实现文件
 * @details 实现了餐厅管理系统的所有业务逻辑功能
 */

#include "restaurant.h"
#include <QDir>  // Qt目录操作类

/**
 * @brief 构造函数的实现
 * @details 初始化餐厅管理系统：
 *          1. 创建数据存储目录
 *          2. 加载已有的数据文件
 */
Restaurant::Restaurant() {
    // 确保数据目录存在
    QDir().mkpath("data");
    loadFromFile();
}

/**
 * @brief 析构函数的实现
 * @details 在系统关闭前保存所有数据到文件
 */
Restaurant::~Restaurant() {
    saveToFile();
}

// 餐品管理实现
/**
 * @brief 添加餐品的实现
 * @param dish 要添加的餐品对象
 * @return 添加成功返回true，餐品ID已存在返回false
 * @details 检查餐品ID是否已存在，如果不存在则添加到容器中
 */
bool Restaurant::addDish(const Dish& dish) {
    if (findDishById(dish.getId()) != nullptr) {
        return false;  // ID已存在
    }
    dishes.push_back(dish);
    return true;
}

/**
 * @brief 删除餐品的实现
 * @param id 要删除的餐品ID
 * @return 删除成功返回true，餐品不存在返回false
 * @details 使用STL算法查找并删除指定ID的餐品
 */
bool Restaurant::removeDish(int id) {
    auto it = std::find_if(dishes.begin(), dishes.end(),
                          [id](const Dish& d) { return d.getId() == id; });
    if (it != dishes.end()) {
        dishes.erase(it);
        return true;
    }
    return false;
}

/**
 * @brief 更新餐品的实现
 * @param dish 包含新信息的餐品对象
 * @return 更新成功返回true，餐品不存在返回false
 * @details 查找并更新指定ID的餐品信息
 */
bool Restaurant::updateDish(const Dish& dish) {
    for (auto& d : dishes) {
        if (d.getId() == dish.getId()) {
            d = dish;
            return true;
        }
    }
    return false;
}

/**
 * @brief 根据ID查找餐品的实现
 * @param id 要查找的餐品ID
 * @return 返回找到的餐品指针，不存在返回nullptr
 * @details 使用STL算法查找指定ID的餐品
 */
Dish* Restaurant::findDishById(int id) {
    auto it = std::find_if(dishes.begin(), dishes.end(),
                          [id](const Dish& d) { return d.getId() == id; });
    return it != dishes.end() ? &(*it) : nullptr;
}

/**
 * @brief 根据名称查找餐品的实现
 * @param name 要查找的餐品名称
 * @return 返回找到的餐品指针，不存在返回nullptr
 * @details 使用STL算法查找指定名称的餐品
 */
Dish* Restaurant::findDishByName(const QString& name) {
    auto it = std::find_if(dishes.begin(), dishes.end(),
                          [&name](const Dish& d) { return d.getName() == name; });
    return it != dishes.end() ? &(*it) : nullptr;
}

/**
 * @brief 获取所有餐品的实现
 * @return 返回包含所有餐品的向量
 */
QVector<Dish> Restaurant::getAllDishes() const {
    return dishes;
}

// 订单管理实现
/**
 * @brief 添加订单的实现
 * @param order 要添加的订单对象
 * @return 添加成功返回true，订单ID已存在返回false
 * @details 检查订单ID是否已存在，如果不存在则添加到容器中
 */
bool Restaurant::addOrder(const Order& order) {
    if (findOrderById(order.getId()) != nullptr) {
        return false;  // ID已存在
    }
    orders.push_back(order);
    return true;
}

/**
 * @brief 删除订单的实现
 * @param id 要删除的订单ID
 * @return 删除成功返回true，订单不存在返回false
 * @details 使用STL算法查找并删除指定ID的订单
 */
bool Restaurant::removeOrder(int id) {
    auto it = std::find_if(orders.begin(), orders.end(),
                          [id](const Order& o) { return o.getId() == id; });
    if (it != orders.end()) {
        orders.erase(it);
        return true;
    }
    return false;
}

/**
 * @brief 更新订单的实现
 * @param order 包含新信息的订单对象
 * @return 更新成功返回true，订单不存在返回false
 * @details 查找并更新指定ID的订单信息
 */
bool Restaurant::updateOrder(const Order& order) {
    for (auto& o : orders) {
        if (o.getId() == order.getId()) {
            o = order;
            return true;
        }
    }
    return false;
}

/**
 * @brief 根据ID查找订单的实现
 * @param id 要查找的订单ID
 * @return 返回找到的订单指针，不存在返回nullptr
 * @details 使用STL算法查找指定ID的订单
 */
Order* Restaurant::findOrderById(int id) {
    auto it = std::find_if(orders.begin(), orders.end(),
                          [id](const Order& o) { return o.getId() == id; });
    return it != orders.end() ? &(*it) : nullptr;
}

/**
 * @brief 根据时间范围查找订单的实现
 * @param start 开始时间
 * @param end 结束时间
 * @return 返回在指定时间范围内的所有订单
 * @details 使用STL算法查找指定时间范围内的所有订单
 */
QVector<Order> Restaurant::findOrdersByTime(const QDateTime& start, const QDateTime& end) {
    QVector<Order> result;
    std::copy_if(orders.begin(), orders.end(), std::back_inserter(result),
                 [&](const Order& o) {
                     return o.getTime() >= start && o.getTime() <= end;
                 });
    return result;
}

/**
 * @brief 获取所有订单的实现
 * @return 返回包含所有订单的向量
 */
QVector<Order> Restaurant::getAllOrders() const {
    return orders;
}

// 顾客管理实现
/**
 * @brief 添加顾客的实现
 * @param customer 要添加的顾客对象
 * @return 添加成功返回true，顾客ID已存在返回false
 * @details 检查顾客ID是否已存在，如果不存在则添加到容器中
 */
bool Restaurant::addCustomer(const Customer& customer) {
    if (findCustomerById(customer.getId()) != nullptr) {
        return false;  // ID已存在
    }
    customers.push_back(customer);
    return true;
}

/**
 * @brief 删除顾客的实现
 * @param id 要删除的顾客ID
 * @return 删除成功返回true，顾客不存在返回false
 * @details 使用STL算法查找并删除指定ID的顾客
 */
bool Restaurant::removeCustomer(int id) {
    auto it = std::find_if(customers.begin(), customers.end(),
                          [id](const Customer& c) { return c.getId() == id; });
    if (it != customers.end()) {
        customers.erase(it);
        return true;
    }
    return false;
}

/**
 * @brief 更新顾客的实现
 * @param customer 包含新信息的顾客对象
 * @return 更新成功返回true，顾客不存在返回false
 * @details 查找并更新指定ID的顾客信息
 */
bool Restaurant::updateCustomer(const Customer& customer) {
    for (auto& c : customers) {
        if (c.getId() == customer.getId()) {
            c = customer;
            return true;
        }
    }
    return false;
}

/**
 * @brief 根据ID查找顾客的实现
 * @param id 要查找的顾客ID
 * @return 返回找到的顾客指针，不存在返回nullptr
 * @details 使用STL算法查找指定ID的顾客
 */
Customer* Restaurant::findCustomerById(int id) {
    auto it = std::find_if(customers.begin(), customers.end(),
                          [id](const Customer& c) { return c.getId() == id; });
    return it != customers.end() ? &(*it) : nullptr;
}

/**
 * @brief 根据名称查找顾客的实现
 * @param name 要查找的顾客名称
 * @return 返回找到的顾客指针，不存在返回nullptr
 * @details 使用STL算法查找指定名称的顾客
 */
Customer* Restaurant::findCustomerByName(const QString& name) {
    auto it = std::find_if(customers.begin(), customers.end(),
                          [&name](const Customer& c) { return c.getName() == name; });
    return it != customers.end() ? &(*it) : nullptr;
}

/**
 * @brief 获取所有顾客的实现
 * @return 返回包含所有顾客的向量
 */
QVector<Customer> Restaurant::getAllCustomers() const {
    return customers;
}

// 数据持久化实现
/**
 * @brief 保存数据到文件的模板函数实现
 * @param filename 文件名
 * @param data 要保存的数据
 * @return 保存成功返回true，失败返回false
 * @details 使用Qt的数据流将数据写入文件
 */
template<typename T>
bool Restaurant::saveData(const QString& filename, const QVector<T>& data) {
    QFile file(filename);
    if (!file.open(QIODevice::WriteOnly)) {
        return false;
    }
    QDataStream out(&file);
    out << data;
    file.close();
    return true;
}

/**
 * @brief 从文件加载数据的模板函数实现
 * @param filename 文件名
 * @param data 用于存储加载的数据
 * @return 加载成功返回true，失败返回false
 * @details 使用Qt的数据流从文件读取数据
 */
template<typename T>
bool Restaurant::loadData(const QString& filename, QVector<T>& data) {
    QFile file(filename);
    if (!file.open(QIODevice::ReadOnly)) {
        return false;
    }
    QDataStream in(&file);
    in >> data;
    file.close();
    return true;
}

/**
 * @brief 保存所有数据到文件的实现
 * @return 所有数据保存成功返回true，任一保存失败返回false
 * @details 依次保存餐品、订单和顾客数据到各自的文件
 */
bool Restaurant::saveToFile() {
    return saveData(DISHES_FILE, dishes) &&
           saveData(ORDERS_FILE, orders) &&
           saveData(CUSTOMERS_FILE, customers);
}

/**
 * @brief 从文件加载所有数据的实现
 * @return 所有数据加载成功返回true，任一加载失败返回false
 * @details 依次从各自的文件加载餐品、订单和顾客数据
 */
bool Restaurant::loadFromFile() {
    return loadData(DISHES_FILE, dishes) &&
           loadData(ORDERS_FILE, orders) &&
           loadData(CUSTOMERS_FILE, customers);
} 