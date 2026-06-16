/**
 * @file customer.cpp
 * @brief 顾客类的实现文件
 * @details 实现了顾客类的各个成员函数
 */

#include "customer.h"

/**
 * @brief 默认构造函数的实现
 * @details 初始化一个空的顾客对象：
 *          - 编号设为0
 *          - 姓名为空字符串
 *          - 电话为空字符串
 */
Customer::Customer() : id(0) {}

/**
 * @brief 带参数构造函数的实现
 * @param id 顾客编号
 * @param name 顾客姓名
 * @param phone 顾客电话
 * @details 使用初始化列表方式创建顾客对象，并设置初始值：
 *          - 设置顾客编号
 *          - 设置顾客姓名
 *          - 设置顾客电话
 */
Customer::Customer(int id, const QString& name, const QString& phone)
    : id(id), name(name), phone(phone) {}

/**
 * @brief 重载输出运算符的实现
 * @param out 输出流对象
 * @param customer 要输出的顾客对象
 * @return 返回输出流对象的引用
 * @details 将顾客对象的所有成员按顺序写入输出流中：
 *          1. 顾客编号
 *          2. 顾客姓名
 *          3. 顾客电话
 */
QDataStream& operator<<(QDataStream& out, const Customer& customer) {
    out << customer.id << customer.name << customer.phone;
    return out;
}

/**
 * @brief 重载输入运算符的实现
 * @param in 输入流对象
 * @param customer 要输入的顾客对象
 * @return 返回输入流对象的引用
 * @details 从输入流中按顺序读取数据到顾客对象的成员中：
 *          1. 读取顾客编号
 *          2. 读取顾客姓名
 *          3. 读取顾客电话
 */
QDataStream& operator>>(QDataStream& in, Customer& customer) {
    in >> customer.id >> customer.name >> customer.phone;
    return in;
} 