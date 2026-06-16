/**
 * @file customer.h
 * @brief 顾客类的头文件
 * @details 定义了餐厅管理系统中的顾客类，包含顾客的基本信息和操作方法
 */

#ifndef CUSTOMER_H
#define CUSTOMER_H

#include <QString>     // Qt字符串类
#include <QDataStream> // Qt数据流类，用于文件读写

/**
 * @class Customer
 * @brief 顾客类
 * @details 表示餐厅中的一个顾客，包含编号、姓名和电话等基本信息
 */
class Customer {
public:
    /**
     * @brief 默认构造函数
     * @details 创建一个空的顾客对象，编号初始化为0
     */
    Customer();

    /**
     * @brief 带参数的构造函数
     * @param id 顾客编号
     * @param name 顾客姓名
     * @param phone 顾客电话
     * @details 使用给定的参数创建一个顾客对象
     */
    Customer(int id, const QString& name, const QString& phone);

    // Getter方法
    /**
     * @brief 获取顾客编号
     * @return 返回顾客的编号
     */
    int getId() const { return id; }

    /**
     * @brief 获取顾客姓名
     * @return 返回顾客的姓名
     */
    QString getName() const { return name; }

    /**
     * @brief 获取顾客电话
     * @return 返回顾客的电话号码
     */
    QString getPhone() const { return phone; }

    // Setter方法
    /**
     * @brief 设置顾客编号
     * @param newId 新的顾客编号
     */
    void setId(int newId) { id = newId; }

    /**
     * @brief 设置顾客姓名
     * @param newName 新的顾客姓名
     */
    void setName(const QString& newName) { name = newName; }

    /**
     * @brief 设置顾客电话
     * @param newPhone 新的顾客电话号码
     */
    void setPhone(const QString& newPhone) { phone = newPhone; }

    /**
     * @brief 重载输出运算符
     * @param out 输出流对象
     * @param customer 要输出的顾客对象
     * @return 返回输出流对象
     * @details 用于将顾客对象写入文件或其他输出流
     */
    friend QDataStream& operator<<(QDataStream& out, const Customer& customer);

    /**
     * @brief 重载输入运算符
     * @param in 输入流对象
     * @param customer 要输入的顾客对象
     * @return 返回输入流对象
     * @details 用于从文件或其他输入流读取顾客对象
     */
    friend QDataStream& operator>>(QDataStream& in, Customer& customer);

private:
    int id;         ///< 顾客编号，唯一标识一个顾客
    QString name;   ///< 顾客姓名，记录顾客的姓名
    QString phone;  ///< 顾客电话，记录顾客的联系方式
};

#endif // CUSTOMER_H 