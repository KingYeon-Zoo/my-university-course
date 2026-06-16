/**
 * @file order.h
 * @brief 订单类的头文件
 * @details 定义了餐厅管理系统中的订单类，包含订单的基本信息和操作方法
 */

#ifndef ORDER_H
#define ORDER_H

#include <QString>     // Qt字符串类
#include <QDateTime>   // Qt日期时间类
#include <QDataStream> // Qt数据流类，用于文件读写

/**
 * @class Order
 * @brief 订单类
 * @details 表示餐厅中的一个订单，包含编号、时间、金额和状态等信息
 */
class Order {
public:
    /**
     * @brief 订单状态枚举类
     * @details 定义了订单可能的所有状态
     */
    enum class Status {
        Pending,    ///< 待处理：订单刚创建，等待处理
        Processing, ///< 处理中：订单正在处理
        Completed,  ///< 已完成：订单已经完成
        Cancelled   ///< 已取消：订单被取消
    };

    /**
     * @brief 默认构造函数
     * @details 创建一个空的订单对象，设置当前时间，状态为待处理
     */
    Order();

    /**
     * @brief 带参数的构造函数
     * @param id 订单编号
     * @param time 订单时间
     * @param amount 订单金额
     * @param status 订单状态
     * @details 使用给定的参数创建一个订单对象
     */
    Order(int id, const QDateTime& time, double amount, Status status);

    // Getter方法
    /**
     * @brief 获取订单编号
     * @return 返回订单的编号
     */
    int getId() const { return id; }

    /**
     * @brief 获取订单时间
     * @return 返回订单的创建时间
     */
    QDateTime getTime() const { return orderTime; }

    /**
     * @brief 获取订单金额
     * @return 返回订单的总金额
     */
    double getAmount() const { return amount; }

    /**
     * @brief 获取订单状态
     * @return 返回订单的当前状态
     */
    Status getStatus() const { return status; }

    // Setter方法
    /**
     * @brief 设置订单编号
     * @param newId 新的订单编号
     */
    void setId(int newId) { id = newId; }

    /**
     * @brief 设置订单时间
     * @param newTime 新的订单时间
     */
    void setTime(const QDateTime& newTime) { orderTime = newTime; }

    /**
     * @brief 设置订单金额
     * @param newAmount 新的订单金额
     */
    void setAmount(double newAmount) { amount = newAmount; }

    /**
     * @brief 设置订单状态
     * @param newStatus 新的订单状态
     */
    void setStatus(Status newStatus) { status = newStatus; }

    /**
     * @brief 将订单状态转换为可读字符串
     * @param status 要转换的状态
     * @return 返回状态对应的中文描述
     */
    static QString statusToString(Status status);

    /**
     * @brief 将字符串转换为订单状态
     * @param str 状态的中文描述
     * @return 返回对应的订单状态枚举值
     */
    static Status stringToStatus(const QString& str);

    /**
     * @brief 重载输出运算符
     * @param out 输出流对象
     * @param order 要输出的订单对象
     * @return 返回输出流对象
     * @details 用于将订单对象写入文件或其他输出流
     */
    friend QDataStream& operator<<(QDataStream& out, const Order& order);

    /**
     * @brief 重载输入运算符
     * @param in 输入流对象
     * @param order 要输入的订单对象
     * @return 返回输入流对象
     * @details 用于从文件或其他输入流读取订单对象
     */
    friend QDataStream& operator>>(QDataStream& in, Order& order);

private:
    int id;              ///< 订单编号，唯一标识一个订单
    QDateTime orderTime; ///< 订单时间，记录订单创建的时间
    double amount;       ///< 订单金额，订单的总价
    Status status;       ///< 订单状态，表示订单当前的处理状态
};

#endif // ORDER_H 