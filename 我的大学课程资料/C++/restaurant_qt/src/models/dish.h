/**
 * @file dish.h
 * @brief 餐品类的头文件
 * @details 定义了餐厅管理系统中的餐品类，包含餐品的基本信息和操作方法
 */

#ifndef DISH_H
#define DISH_H

#include <QString>      // Qt字符串类
#include <QDataStream>  // Qt数据流类，用于文件读写

/**
 * @class Dish
 * @brief 餐品类
 * @details 表示餐厅中的一个餐品，包含编号、名称、价格和评分等信息
 */
class Dish {
public:
    /**
     * @brief 默认构造函数
     * @details 创建一个空的餐品对象，所有数值成员初始化为0
     */
    Dish();

    /**
     * @brief 带参数的构造函数
     * @param id 餐品编号
     * @param name 餐品名称
     * @param price 餐品价格
     * @param rating 餐品评分
     * @details 使用给定的参数创建一个餐品对象
     */
    Dish(int id, const QString& name, double price, double rating);

    // Getter方法
    /**
     * @brief 获取餐品编号
     * @return 返回餐品的编号
     */
    int getId() const { return id; }

    /**
     * @brief 获取餐品名称
     * @return 返回餐品的名称
     */
    QString getName() const { return name; }

    /**
     * @brief 获取餐品价格
     * @return 返回餐品的价格
     */
    double getPrice() const { return price; }

    /**
     * @brief 获取餐品评分
     * @return 返回餐品的评分
     */
    double getRating() const { return rating; }

    // Setter方法
    /**
     * @brief 设置餐品编号
     * @param newId 新的餐品编号
     */
    void setId(int newId) { id = newId; }

    /**
     * @brief 设置餐品名称
     * @param newName 新的餐品名称
     */
    void setName(const QString& newName) { name = newName; }

    /**
     * @brief 设置餐品价格
     * @param newPrice 新的餐品价格
     */
    void setPrice(double newPrice) { price = newPrice; }

    /**
     * @brief 设置餐品评分
     * @param newRating 新的餐品评分
     */
    void setRating(double newRating) { rating = newRating; }

    /**
     * @brief 重载输出运算符
     * @param out 输出流对象
     * @param dish 要输出的餐品对象
     * @return 返回输出流对象
     * @details 用于将餐品对象写入文件或其他输出流
     */
    friend QDataStream& operator<<(QDataStream& out, const Dish& dish);

    /**
     * @brief 重载输入运算符
     * @param in 输入流对象
     * @param dish 要输入的餐品对象
     * @return 返回输入流对象
     * @details 用于从文件或其他输入流读取餐品对象
     */
    friend QDataStream& operator>>(QDataStream& in, Dish& dish);

private:
    int id;         ///< 餐品编号，唯一标识一个餐品
    QString name;   ///< 餐品名称，描述餐品的名字
    double price;   ///< 餐品价格，单位为元
    double rating;  ///< 餐品评分，范围0-5分
};

#endif // DISH_H 