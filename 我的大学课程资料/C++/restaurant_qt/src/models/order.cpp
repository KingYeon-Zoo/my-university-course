/**
 * @file order.cpp
 * @brief 订单类的实现文件
 * @details 实现了订单类的各个成员函数
 */

#include "order.h"

/**
 * @brief 默认构造函数的实现
 * @details 初始化一个空的订单对象：
 *          - 编号设为0
 *          - 金额设为0.0
 *          - 状态设为待处理
 *          - 时间设为当前系统时间
 */
Order::Order() : id(0), amount(0.0), status(Status::Pending) {
    orderTime = QDateTime::currentDateTime();
}

/**
 * @brief 带参数构造函数的实现
 * @param id 订单编号
 * @param time 订单时间
 * @param amount 订单金额
 * @param status 订单状态
 * @details 使用初始化列表方式创建订单对象，并设置初始值
 */
Order::Order(int id, const QDateTime& time, double amount, Status status)
    : id(id), orderTime(time), amount(amount), status(status) {}

/**
 * @brief 将订单状态转换为可读字符串的实现
 * @param status 要转换的状态枚举值
 * @return 返回状态对应的中文描述
 * @details 将订单状态枚举值转换为用户友好的中文描述：
 *          - Pending -> "待处理"
 *          - Processing -> "处理中"
 *          - Completed -> "已完成"
 *          - Cancelled -> "已取消"
 */
QString Order::statusToString(Status status) {
    switch (status) {
        case Status::Pending: return "待处理";
        case Status::Processing: return "处理中";
        case Status::Completed: return "已完成";
        case Status::Cancelled: return "已取消";
        default: return "未知状态";
    }
}

/**
 * @brief 将字符串转换为订单状态的实现
 * @param str 状态的中文描述
 * @return 返回对应的订单状态枚举值
 * @details 将用户友好的中文描述转换为订单状态枚举值：
 *          - "待处理" -> Pending
 *          - "处理中" -> Processing
 *          - "已完成" -> Completed
 *          - "已取消" -> Cancelled
 *          如果输入的字符串不匹配任何状态，则返回Pending
 */
Order::Status Order::stringToStatus(const QString& str) {
    if (str == "待处理") return Status::Pending;
    if (str == "处理中") return Status::Processing;
    if (str == "已完成") return Status::Completed;
    if (str == "已取消") return Status::Cancelled;
    return Status::Pending;  // 默认返回待处理状态
}

/**
 * @brief 重载输出运算符的实现
 * @param out 输出流对象
 * @param order 要输出的订单对象
 * @return 返回输出流对象的引用
 * @details 将订单对象的所有成员按顺序写入输出流中：
 *          1. 订单编号
 *          2. 订单时间
 *          3. 订单金额
 *          4. 订单状态（转换为整数后写入）
 */
QDataStream& operator<<(QDataStream& out, const Order& order) {
    out << order.id << order.orderTime << order.amount << static_cast<int>(order.status);
    return out;
}

/**
 * @brief 重载输入运算符的实现
 * @param in 输入流对象
 * @param order 要输入的订单对象
 * @return 返回输入流对象的引用
 * @details 从输入流中按顺序读取数据到订单对象的成员中：
 *          1. 读取订单编号
 *          2. 读取订单时间
 *          3. 读取订单金额
 *          4. 读取订单状态（先读取为整数，再转换为枚举值）
 */
QDataStream& operator>>(QDataStream& in, Order& order) {
    int statusInt;
    in >> order.id >> order.orderTime >> order.amount >> statusInt;
    order.status = static_cast<Order::Status>(statusInt);
    return in;
} 