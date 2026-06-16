/**
 * @file mainwindow.h
 * @brief 餐厅管理系统的主窗口类头文件
 * @details 该类实现了餐厅管理系统的图形界面，包含三个主要功能模块：
 *          1. 餐品管理：添加、删除、修改、查询餐品信息
 *          2. 订单管理：处理订单的创建、修改、删除和查询
 *          3. 顾客管理：管理顾客信息的增删改查
 */

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

// Qt框架相关头文件
#include <QMainWindow>
#include <QTabWidget>
#include <QTableWidget>
#include <QPushButton>
#include <QLineEdit>
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMessageBox>
#include <QDateTime>
#include <QComboBox>
#include "src/restaurant.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

/**
 * @class MainWindow
 * @brief 主窗口类，继承自QMainWindow
 * @details 实现了餐厅管理系统的所有图形界面功能
 */
class MainWindow : public QMainWindow
{
    Q_OBJECT  // Qt的元对象宏，启用信号槽机制

public:
    /**
     * @brief 构造函数
     * @param parent 父窗口指针，默认为nullptr
     */
    MainWindow(QWidget *parent = nullptr);
    
    /**
     * @brief 析构函数
     */
    ~MainWindow();

private slots:
    // 餐品管理相关槽函数
    void addDish();      ///< 添加新餐品
    void removeDish();   ///< 删除已有餐品
    void updateDish();   ///< 更新餐品信息
    void searchDish();   ///< 搜索餐品
    void refreshDishTable(); ///< 刷新餐品表格显示

    // 订单管理相关槽函数
    void addOrder();     ///< 添加新订单
    void removeOrder();  ///< 删除订单
    void updateOrder();  ///< 更新订单状态
    void searchOrder();  ///< 搜索订单
    void refreshOrderTable(); ///< 刷新订单表格显示

    // 顾客管理相关槽函数
    void addCustomer();    ///< 添加新顾客
    void removeCustomer(); ///< 删除顾客信息
    void updateCustomer(); ///< 更新顾客信息
    void searchCustomer(); ///< 搜索顾客
    void refreshCustomerTable(); ///< 刷新顾客表格显示

private:
    Ui::MainWindow *ui;  ///< Qt Designer生成的UI类指针
    Restaurant restaurant; ///< 餐厅业务逻辑类实例

    // UI组件
    QTabWidget *tabWidget;  ///< 主标签页控件，用于切换不同功能模块
    
    // 餐品管理相关控件
    QTableWidget *dishTable;    ///< 餐品信息表格
    QLineEdit *dishIdEdit;      ///< 餐品ID输入框
    QLineEdit *dishNameEdit;    ///< 餐品名称输入框
    QLineEdit *dishPriceEdit;   ///< 餐品价格输入框
    QLineEdit *dishRatingEdit;  ///< 餐品评分输入框
    
    // 订单管理相关控件
    QTableWidget *orderTable;   ///< 订单信息表格
    QLineEdit *orderIdEdit;     ///< 订单ID输入框
    QLineEdit *orderAmountEdit; ///< 订单金额输入框
    QComboBox *orderStatusCombo;///< 订单状态下拉框
    
    // 顾客管理相关控件
    QTableWidget *customerTable;  ///< 顾客信息表格
    QLineEdit *customerIdEdit;    ///< 顾客ID输入框
    QLineEdit *customerNameEdit;  ///< 顾客姓名输入框
    QLineEdit *customerPhoneEdit; ///< 顾客电话输入框

    // UI初始化函数
    void setupUi();          ///< 初始化整体UI布局
    void setupDishTab();     ///< 初始化餐品管理标签页
    void setupOrderTab();    ///< 初始化订单管理标签页
    void setupCustomerTab(); ///< 初始化顾客管理标签页
};
#endif // MAINWINDOW_H
