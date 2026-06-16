/**
 * @file dish.cpp
 * @brief 餐品类的实现文件
 * @details 实现了餐品类的各个成员函数
 */

#include "dish.h"

/**
 * @brief 默认构造函数的实现
 * @details 初始化一个空的餐品对象，将所有数值成员设置为0
 */
Dish::Dish() : id(0), price(0.0), rating(0.0) {}

/**
 * @brief 带参数构造函数的实现
 * @param id 餐品编号
 * @param name 餐品名称
 * @param price 餐品价格
 * @param rating 餐品评分
 * @details 使用初始化列表方式创建餐品对象，并设置初始值
 */
Dish::Dish(int id, const QString& name, double price, double rating)
    : id(id), name(name), price(price), rating(rating) {}

/**
 * @brief 重载输出运算符的实现
 * @param out 输出流对象
 * @param dish 要输出的餐品对象
 * @return 返回输出流对象的引用
 * @details 将餐品对象的所有成员按顺序写入输出流中
 */
QDataStream& operator<<(QDataStream& out, const Dish& dish) {
    out << dish.id << dish.name << dish.price << dish.rating;
    return out;
}

/**
 * @brief 重载输入运算符的实现
 * @param in 输入流对象
 * @param dish 要输入的餐品对象
 * @return 返回输入流对象的引用
 * @details 从输入流中按顺序读取数据到餐品对象的成员中
 */
QDataStream& operator>>(QDataStream& in, Dish& dish) {
    in >> dish.id >> dish.name >> dish.price >> dish.rating;
    return in;
} 