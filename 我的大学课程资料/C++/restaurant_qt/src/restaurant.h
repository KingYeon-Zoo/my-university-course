/**
 * @file restaurant.h
 * @brief 餐厅管理类的头文件
 * @details 定义了餐厅管理系统的核心类，负责管理餐品、订单和顾客信息
 */

#ifndef RESTAURANT_H
#define RESTAURANT_H

#include <QVector>      // Qt向量容器类
#include <QString>      // Qt字符串类
#include <QFile>        // Qt文件操作类
#include <QDataStream>  // Qt数据流类
#include <algorithm>    // STL算法库
#include "models/dish.h"      // 餐品类
#include "models/order.h"     // 订单类
#include "models/customer.h"  // 顾客类

/**
 * @class Restaurant
 * @brief 餐厅管理类
 * @details 实现餐厅的核心业务逻辑，包括：
 *          - 餐品的增删改查
 *          - 订单的处理和管理
 *          - 顾客信息的维护
 *          - 数据的持久化存储
 */
class Restaurant {
public:
    /**
     * @brief 构造函数
     * @details 初始化餐厅管理系统，创建数据目录并加载已有数据
     */
    Restaurant();

    /**
     * @brief 析构函数
     * @details 在系统关闭时保存所有数据
     */
    ~Restaurant();

    // 餐品管理接口
    /**
     * @brief 添加新餐品
     * @param dish 要添加的餐品对象
     * @return 添加成功返回true，如果餐品ID已存在则返回false
     */
    bool addDish(const Dish& dish);

    /**
     * @brief 删除餐品
     * @param id 要删除的餐品ID
     * @return 删除成功返回true，如果餐品不存在则返回false
     */
    bool removeDish(int id);

    /**
     * @brief 更新餐品信息
     * @param dish 包含新信息的餐品对象
     * @return 更新成功返回true，如果餐品不存在则返回false
     */
    bool updateDish(const Dish& dish);

    /**
     * @brief 根据ID查找餐品
     * @param id 要查找的餐品ID
     * @return 返回找到的餐品指针，如果不存在则返回nullptr
     */
    Dish* findDishById(int id);

    /**
     * @brief 根据名称查找餐品
     * @param name 要查找的餐品名称
     * @return 返回找到的餐品指针，如果不存在则返回nullptr
     */
    Dish* findDishByName(const QString& name);

    /**
     * @brief 获取所有餐品
     * @return 返回包含所有餐品的向量
     */
    QVector<Dish> getAllDishes() const;

    // 订单管理接口
    /**
     * @brief 添加新订单
     * @param order 要添加的订单对象
     * @return 添加成功返回true，如果订单ID已存在则返回false
     */
    bool addOrder(const Order& order);

    /**
     * @brief 删除订单
     * @param id 要删除的订单ID
     * @return 删除成功返回true，如果订单不存在则返回false
     */
    bool removeOrder(int id);

    /**
     * @brief 更新订单信息
     * @param order 包含新信息的订单对象
     * @return 更新成功返回true，如果订单不存在则返回false
     */
    bool updateOrder(const Order& order);

    /**
     * @brief 根据ID查找订单
     * @param id 要查找的订单ID
     * @return 返回找到的订单指针，如果不存在则返回nullptr
     */
    Order* findOrderById(int id);

    /**
     * @brief 根据时间范围查找订单
     * @param start 开始时间
     * @param end 结束时间
     * @return 返回在指定时间范围内的所有订单
     */
    QVector<Order> findOrdersByTime(const QDateTime& start, const QDateTime& end);

    /**
     * @brief 获取所有订单
     * @return 返回包含所有订单的向量
     */
    QVector<Order> getAllOrders() const;

    // 顾客管理接口
    /**
     * @brief 添加新顾客
     * @param customer 要添加的顾客对象
     * @return 添加成功返回true，如果顾客ID已存在则返回false
     */
    bool addCustomer(const Customer& customer);

    /**
     * @brief 删除顾客
     * @param id 要删除的顾客ID
     * @return 删除成功返回true，如果顾客不存在则返回false
     */
    bool removeCustomer(int id);

    /**
     * @brief 更新顾客信息
     * @param customer 包含新信息的顾客对象
     * @return 更新成功返回true，如果顾客不存在则返回false
     */
    bool updateCustomer(const Customer& customer);

    /**
     * @brief 根据ID查找顾客
     * @param id 要查找的顾客ID
     * @return 返回找到的顾客指针，如果不存在则返回nullptr
     */
    Customer* findCustomerById(int id);

    /**
     * @brief 根据名称查找顾客
     * @param name 要查找的顾客名称
     * @return 返回找到的顾客指针，如果不存在则返回nullptr
     */
    Customer* findCustomerByName(const QString& name);

    /**
     * @brief 获取所有顾客
     * @return 返回包含所有顾客的向量
     */
    QVector<Customer> getAllCustomers() const;

    // 数据持久化接口
    /**
     * @brief 保存所有数据到文件
     * @return 保存成功返回true，失败返回false
     */
    bool saveToFile();

    /**
     * @brief 从文件加载所有数据
     * @return 加载成功返回true，失败返回false
     */
    bool loadFromFile();

private:
    QVector<Dish> dishes;         ///< 存储所有餐品的容器
    QVector<Order> orders;        ///< 存储所有订单的容器
    QVector<Customer> customers;  ///< 存储所有顾客的容器

    // 数据文件路径
    const QString DISHES_FILE = "data/dishes.dat";       ///< 餐品数据文件路径
    const QString ORDERS_FILE = "data/orders.dat";       ///< 订单数据文件路径
    const QString CUSTOMERS_FILE = "data/customers.dat"; ///< 顾客数据文件路径

    // 辅助函数
    /**
     * @brief 保存数据到指定文件的模板函数
     * @param filename 文件名
     * @param data 要保存的数据
     * @return 保存成功返回true，失败返回false
     */
    template<typename T>
    bool saveData(const QString& filename, const QVector<T>& data);
    
    /**
     * @brief 从指定文件加载数据的模板函数
     * @param filename 文件名
     * @param data 用于存储加载的数据
     * @return 加载成功返回true，失败返回false
     */
    template<typename T>
    bool loadData(const QString& filename, QVector<T>& data);
};

#endif // RESTAURANT_H 