/**
 * @file mainwindow.cpp
 * @brief 主窗口类的实现文件
 * @details 实现了餐厅管理系统的所有图形界面功能和业务逻辑
 */

#include "mainwindow.h"
#include "./ui_mainwindow.h"  // Qt Designer自动生成的UI头文件
#include <QMessageBox>        // 消息框组件
#include <QInputDialog>       // 输入对话框组件

/**
 * @brief 主窗口构造函数
 * @param parent 父窗口指针
 * @details 初始化UI组件并设置窗口属性
 */
MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)    // 调用父类构造函数
    , ui(new Ui::MainWindow) // 创建UI对象
{
    // 设置UI
    ui->setupUi(this);
    setupUi();
    
    // 设置窗口标题和大小
    setWindowTitle("餐厅管理系统");
    resize(800, 600);
}

/**
 * @brief 主窗口析构函数
 * @details 释放UI对象占用的内存
 */
MainWindow::~MainWindow()
{
    delete ui;
}

/**
 * @brief 初始化整体UI布局
 * @details 创建主标签页并初始化各个功能模块的标签页
 */
void MainWindow::setupUi() {
    // 创建主标签页控件
    tabWidget = new QTabWidget(this);
    setCentralWidget(tabWidget);

    // 初始化各个功能模块的标签页
    setupDishTab();     // 餐品管理标签页
    setupOrderTab();    // 订单管理标签页
    setupCustomerTab(); // 顾客管理标签页
}

/**
 * @brief 初始化餐品管理标签页
 * @details 创建餐品管理界面的所有控件并设置布局
 */
void MainWindow::setupDishTab() {
    // 创建餐品管理页面的主容器
    QWidget *dishWidget = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout();

    // 创建餐品信息表格
    dishTable = new QTableWidget();
    dishTable->setColumnCount(4);
    dishTable->setHorizontalHeaderLabels({"编号", "名称", "价格", "评分"});
    layout->addWidget(dishTable);

    // 创建输入区域，使用网格布局
    QGridLayout *inputLayout = new QGridLayout();
    // 创建输入框
    dishIdEdit = new QLineEdit();     // 餐品编号输入框
    dishNameEdit = new QLineEdit();    // 餐品名称输入框
    dishPriceEdit = new QLineEdit();   // 餐品价格输入框
    dishRatingEdit = new QLineEdit();  // 餐品评分输入框

    // 添加标签和输入框到网格布局
    inputLayout->addWidget(new QLabel("编号:"), 0, 0);
    inputLayout->addWidget(dishIdEdit, 0, 1);
    inputLayout->addWidget(new QLabel("名称:"), 0, 2);
    inputLayout->addWidget(dishNameEdit, 0, 3);
    inputLayout->addWidget(new QLabel("价格:"), 1, 0);
    inputLayout->addWidget(dishPriceEdit, 1, 1);
    inputLayout->addWidget(new QLabel("评分:"), 1, 2);
    inputLayout->addWidget(dishRatingEdit, 1, 3);

    layout->addLayout(inputLayout);

    // 创建按钮区域，使用水平布局
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    // 创建操作按钮
    QPushButton *addButton = new QPushButton("添加");
    QPushButton *removeButton = new QPushButton("删除");
    QPushButton *updateButton = new QPushButton("修改");
    QPushButton *searchButton = new QPushButton("查询");
    QPushButton *refreshButton = new QPushButton("刷新");

    // 连接按钮的点击信号到对应的槽函数
    connect(addButton, &QPushButton::clicked, this, &MainWindow::addDish);
    connect(removeButton, &QPushButton::clicked, this, &MainWindow::removeDish);
    connect(updateButton, &QPushButton::clicked, this, &MainWindow::updateDish);
    connect(searchButton, &QPushButton::clicked, this, &MainWindow::searchDish);
    connect(refreshButton, &QPushButton::clicked, this, &MainWindow::refreshDishTable);

    // 将按钮添加到布局中
    buttonLayout->addWidget(addButton);
    buttonLayout->addWidget(removeButton);
    buttonLayout->addWidget(updateButton);
    buttonLayout->addWidget(searchButton);
    buttonLayout->addWidget(refreshButton);

    // 将按钮布局添加到主布局
    layout->addLayout(buttonLayout);
    dishWidget->setLayout(layout);
    // 将餐品管理页面添加到主标签页
    tabWidget->addTab(dishWidget, "餐品管理");

    // 初始化显示数据
    refreshDishTable();
}

/**
 * @brief 初始化订单管理标签页
 * @details 创建订单管理界面的所有控件并设置布局
 */
void MainWindow::setupOrderTab() {
    // 创建订单管理页面的主容器
    QWidget *orderWidget = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout();

    // 创建订单信息表格
    orderTable = new QTableWidget();
    orderTable->setColumnCount(4);
    orderTable->setHorizontalHeaderLabels({"编号", "时间", "金额", "状态"});
    layout->addWidget(orderTable);

    // 创建输入区域，使用网格布局
    QGridLayout *inputLayout = new QGridLayout();
    // 创建输入控件
    orderIdEdit = new QLineEdit();        // 订单编号输入框
    orderAmountEdit = new QLineEdit();    // 订单金额输入框
    orderStatusCombo = new QComboBox();   // 订单状态下拉框
    orderStatusCombo->addItems({"待处理", "处理中", "已完成", "已取消"});

    // 添加标签和输入控件到网格布局
    inputLayout->addWidget(new QLabel("编号:"), 0, 0);
    inputLayout->addWidget(orderIdEdit, 0, 1);
    inputLayout->addWidget(new QLabel("金额:"), 0, 2);
    inputLayout->addWidget(orderAmountEdit, 0, 3);
    inputLayout->addWidget(new QLabel("状态:"), 1, 0);
    inputLayout->addWidget(orderStatusCombo, 1, 1);

    layout->addLayout(inputLayout);

    // 创建按钮区域，使用水平布局
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    // 创建操作按钮
    QPushButton *addButton = new QPushButton("添加");
    QPushButton *removeButton = new QPushButton("删除");
    QPushButton *updateButton = new QPushButton("修改");
    QPushButton *searchButton = new QPushButton("查询");
    QPushButton *refreshButton = new QPushButton("刷新");

    // 连接按钮的点击信号到对应的槽函数
    connect(addButton, &QPushButton::clicked, this, &MainWindow::addOrder);
    connect(removeButton, &QPushButton::clicked, this, &MainWindow::removeOrder);
    connect(updateButton, &QPushButton::clicked, this, &MainWindow::updateOrder);
    connect(searchButton, &QPushButton::clicked, this, &MainWindow::searchOrder);
    connect(refreshButton, &QPushButton::clicked, this, &MainWindow::refreshOrderTable);

    // 将按钮添加到布局中
    buttonLayout->addWidget(addButton);
    buttonLayout->addWidget(removeButton);
    buttonLayout->addWidget(updateButton);
    buttonLayout->addWidget(searchButton);
    buttonLayout->addWidget(refreshButton);

    // 将按钮布局添加到主布局
    layout->addLayout(buttonLayout);
    orderWidget->setLayout(layout);
    // 将订单管理页面添加到主标签页
    tabWidget->addTab(orderWidget, "订单管理");

    // 初始化显示数据
    refreshOrderTable();
}

/**
 * @brief 初始化顾客管理标签页
 * @details 创建顾客管理界面的所有控件并设置布局
 */
void MainWindow::setupCustomerTab() {
    // 创建顾客管理页面的主容器
    QWidget *customerWidget = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout();

    // 创建顾客信息表格
    customerTable = new QTableWidget();
    customerTable->setColumnCount(3);
    customerTable->setHorizontalHeaderLabels({"编号", "姓名", "电话"});
    layout->addWidget(customerTable);

    // 创建输入区域，使用网格布局
    QGridLayout *inputLayout = new QGridLayout();
    // 创建输入框
    customerIdEdit = new QLineEdit();      // 顾客编号输入框
    customerNameEdit = new QLineEdit();    // 顾客姓名输入框
    customerPhoneEdit = new QLineEdit();   // 顾客电话输入框

    // 添加标签和输入框到网格布局
    inputLayout->addWidget(new QLabel("编号:"), 0, 0);
    inputLayout->addWidget(customerIdEdit, 0, 1);
    inputLayout->addWidget(new QLabel("姓名:"), 0, 2);
    inputLayout->addWidget(customerNameEdit, 0, 3);
    inputLayout->addWidget(new QLabel("电话:"), 1, 0);
    inputLayout->addWidget(customerPhoneEdit, 1, 1);

    layout->addLayout(inputLayout);

    // 创建按钮区域，使用水平布局
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    // 创建操作按钮
    QPushButton *addButton = new QPushButton("添加");
    QPushButton *removeButton = new QPushButton("删除");
    QPushButton *updateButton = new QPushButton("修改");
    QPushButton *searchButton = new QPushButton("查询");
    QPushButton *refreshButton = new QPushButton("刷新");

    // 连接按钮的点击信号到对应的槽函数
    connect(addButton, &QPushButton::clicked, this, &MainWindow::addCustomer);
    connect(removeButton, &QPushButton::clicked, this, &MainWindow::removeCustomer);
    connect(updateButton, &QPushButton::clicked, this, &MainWindow::updateCustomer);
    connect(searchButton, &QPushButton::clicked, this, &MainWindow::searchCustomer);
    connect(refreshButton, &QPushButton::clicked, this, &MainWindow::refreshCustomerTable);

    // 将按钮添加到布局中
    buttonLayout->addWidget(addButton);
    buttonLayout->addWidget(removeButton);
    buttonLayout->addWidget(updateButton);
    buttonLayout->addWidget(searchButton);
    buttonLayout->addWidget(refreshButton);

    // 将按钮布局添加到主布局
    layout->addLayout(buttonLayout);
    customerWidget->setLayout(layout);
    // 将顾客管理页面添加到主标签页
    tabWidget->addTab(customerWidget, "顾客管理");

    // 初始化显示数据
    refreshCustomerTable();
}

/**
 * @brief 添加新餐品
 * @details 从输入框获取餐品信息，验证数据有效性后添加到系统中
 */
void MainWindow::addDish() {
    // 获取并验证餐品编号
    bool ok;
    int id = dishIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    // 获取并验证餐品名称
    QString name = dishNameEdit->text();
    if (name.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入餐品名称！");
        return;
    }

    // 获取并验证餐品价格
    double price = dishPriceEdit->text().toDouble(&ok);
    if (!ok || price < 0) {
        QMessageBox::warning(this, "错误", "请输入有效的价格！");
        return;
    }

    // 获取并验证餐品评分
    double rating = dishRatingEdit->text().toDouble(&ok);
    if (!ok || rating < 0 || rating > 5) {
        QMessageBox::warning(this, "错误", "请输入有效的评分（0-5）！");
        return;
    }

    // 创建餐品对象并添加到系统
    Dish dish(id, name, price, rating);
    if (restaurant.addDish(dish)) {
        QMessageBox::information(this, "成功", "添加餐品成功！");
        refreshDishTable();  // 刷新显示
    } else {
        QMessageBox::warning(this, "错误", "添加餐品失败，可能编号已存在！");
    }
}

/**
 * @brief 删除餐品
 * @details 根据输入的编号删除对应的餐品
 */
void MainWindow::removeDish() {
    // 获取并验证餐品编号
    bool ok;
    int id = dishIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    // 从系统中删除餐品
    if (restaurant.removeDish(id)) {
        QMessageBox::information(this, "成功", "删除餐品成功！");
        refreshDishTable();  // 刷新显示
    } else {
        QMessageBox::warning(this, "错误", "删除餐品失败，餐品不存在！");
    }
}

/**
 * @brief 更新餐品信息
 * @details 根据输入的编号更新对应餐品的信息
 */
void MainWindow::updateDish() {
    bool ok;
    int id = dishIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    QString name = dishNameEdit->text();
    if (name.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入餐品名称！");
        return;
    }

    double price = dishPriceEdit->text().toDouble(&ok);
    if (!ok || price < 0) {
        QMessageBox::warning(this, "错误", "请输入有效的价格！");
        return;
    }

    double rating = dishRatingEdit->text().toDouble(&ok);
    if (!ok || rating < 0 || rating > 5) {
        QMessageBox::warning(this, "错误", "请输入有效的评分（0-5）！");
        return;
    }

    Dish dish(id, name, price, rating);
    if (restaurant.updateDish(dish)) {
        QMessageBox::information(this, "成功", "更新餐品成功！");
        refreshDishTable();
    } else {
        QMessageBox::warning(this, "错误", "更新餐品失败，餐品不存在！");
    }
}

void MainWindow::searchDish() {
    QString searchText = dishNameEdit->text();
    if (searchText.isEmpty()) {
        refreshDishTable();
        return;
    }

    bool ok;
    int id = searchText.toInt(&ok);
    Dish* dish = nullptr;
    
    if (ok) {
        dish = restaurant.findDishById(id);
    } else {
        dish = restaurant.findDishByName(searchText);
    }

    if (dish) {
        dishTable->setRowCount(1);
        dishTable->setItem(0, 0, new QTableWidgetItem(QString::number(dish->getId())));
        dishTable->setItem(0, 1, new QTableWidgetItem(dish->getName()));
        dishTable->setItem(0, 2, new QTableWidgetItem(QString::number(dish->getPrice())));
        dishTable->setItem(0, 3, new QTableWidgetItem(QString::number(dish->getRating())));
    } else {
        QMessageBox::information(this, "提示", "未找到相关餐品！");
        refreshDishTable();
    }
}

void MainWindow::refreshDishTable() {
    QVector<Dish> dishes = restaurant.getAllDishes();
    dishTable->setRowCount(dishes.size());
    
    for (int i = 0; i < dishes.size(); ++i) {
        dishTable->setItem(i, 0, new QTableWidgetItem(QString::number(dishes[i].getId())));
        dishTable->setItem(i, 1, new QTableWidgetItem(dishes[i].getName()));
        dishTable->setItem(i, 2, new QTableWidgetItem(QString::number(dishes[i].getPrice())));
        dishTable->setItem(i, 3, new QTableWidgetItem(QString::number(dishes[i].getRating())));
    }
}

// 订单管理功能实现
void MainWindow::addOrder() {
    bool ok;
    int id = orderIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    double amount = orderAmountEdit->text().toDouble(&ok);
    if (!ok || amount < 0) {
        QMessageBox::warning(this, "错误", "请输入有效的金额！");
        return;
    }

    Order::Status status = Order::stringToStatus(orderStatusCombo->currentText());
    Order order(id, QDateTime::currentDateTime(), amount, status);

    if (restaurant.addOrder(order)) {
        QMessageBox::information(this, "成功", "添加订单成功！");
        refreshOrderTable();
    } else {
        QMessageBox::warning(this, "错误", "添加订单失败，可能编号已存在！");
    }
}

void MainWindow::removeOrder() {
    bool ok;
    int id = orderIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    if (restaurant.removeOrder(id)) {
        QMessageBox::information(this, "成功", "删除订单成功！");
        refreshOrderTable();
    } else {
        QMessageBox::warning(this, "错误", "删除订单失败，订单不存在！");
    }
}

void MainWindow::updateOrder() {
    bool ok;
    int id = orderIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    Order* existingOrder = restaurant.findOrderById(id);
    if (!existingOrder) {
        QMessageBox::warning(this, "错误", "订单不存在！");
        return;
    }

    double amount = orderAmountEdit->text().toDouble(&ok);
    if (!ok || amount < 0) {
        QMessageBox::warning(this, "错误", "请输入有效的金额！");
        return;
    }

    Order::Status status = Order::stringToStatus(orderStatusCombo->currentText());
    Order order(id, existingOrder->getTime(), amount, status);

    if (restaurant.updateOrder(order)) {
        QMessageBox::information(this, "成功", "更新订单成功！");
        refreshOrderTable();
    } else {
        QMessageBox::warning(this, "错误", "更新订单失败！");
    }
}

void MainWindow::searchOrder() {
    bool ok;
    int id = orderIdEdit->text().toInt(&ok);
    if (!ok) {
        refreshOrderTable();
        return;
    }

    Order* order = restaurant.findOrderById(id);
    if (order) {
        orderTable->setRowCount(1);
        orderTable->setItem(0, 0, new QTableWidgetItem(QString::number(order->getId())));
        orderTable->setItem(0, 1, new QTableWidgetItem(order->getTime().toString("yyyy-MM-dd hh:mm:ss")));
        orderTable->setItem(0, 2, new QTableWidgetItem(QString::number(order->getAmount())));
        orderTable->setItem(0, 3, new QTableWidgetItem(Order::statusToString(order->getStatus())));
    } else {
        QMessageBox::information(this, "提示", "未找到相关订单！");
        refreshOrderTable();
    }
}

void MainWindow::refreshOrderTable() {
    QVector<Order> orders = restaurant.getAllOrders();
    orderTable->setRowCount(orders.size());
    
    for (int i = 0; i < orders.size(); ++i) {
        orderTable->setItem(i, 0, new QTableWidgetItem(QString::number(orders[i].getId())));
        orderTable->setItem(i, 1, new QTableWidgetItem(orders[i].getTime().toString("yyyy-MM-dd hh:mm:ss")));
        orderTable->setItem(i, 2, new QTableWidgetItem(QString::number(orders[i].getAmount())));
        orderTable->setItem(i, 3, new QTableWidgetItem(Order::statusToString(orders[i].getStatus())));
    }
}

// 顾客管理功能实现
void MainWindow::addCustomer() {
    bool ok;
    int id = customerIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    QString name = customerNameEdit->text();
    if (name.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入顾客姓名！");
        return;
    }

    QString phone = customerPhoneEdit->text();
    if (phone.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入顾客电话！");
        return;
    }

    Customer customer(id, name, phone);
    if (restaurant.addCustomer(customer)) {
        QMessageBox::information(this, "成功", "添加顾客成功！");
        refreshCustomerTable();
    } else {
        QMessageBox::warning(this, "错误", "添加顾客失败，可能编号已存在！");
    }
}

void MainWindow::removeCustomer() {
    bool ok;
    int id = customerIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    if (restaurant.removeCustomer(id)) {
        QMessageBox::information(this, "成功", "删除顾客成功！");
        refreshCustomerTable();
    } else {
        QMessageBox::warning(this, "错误", "删除顾客失败，顾客不存在！");
    }
}

void MainWindow::updateCustomer() {
    bool ok;
    int id = customerIdEdit->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "错误", "请输入有效的编号！");
        return;
    }

    QString name = customerNameEdit->text();
    if (name.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入顾客姓���！");
        return;
    }

    QString phone = customerPhoneEdit->text();
    if (phone.isEmpty()) {
        QMessageBox::warning(this, "错误", "请输入顾客电话！");
        return;
    }

    Customer customer(id, name, phone);
    if (restaurant.updateCustomer(customer)) {
        QMessageBox::information(this, "成功", "更新顾客信息成功！");
        refreshCustomerTable();
    } else {
        QMessageBox::warning(this, "错误", "更新顾客信息失败，顾客不存在！");
    }
}

void MainWindow::searchCustomer() {
    QString searchText = customerNameEdit->text();
    if (searchText.isEmpty()) {
        refreshCustomerTable();
        return;
    }

    bool ok;
    int id = searchText.toInt(&ok);
    Customer* customer = nullptr;
    
    if (ok) {
        customer = restaurant.findCustomerById(id);
    } else {
        customer = restaurant.findCustomerByName(searchText);
    }

    if (customer) {
        customerTable->setRowCount(1);
        customerTable->setItem(0, 0, new QTableWidgetItem(QString::number(customer->getId())));
        customerTable->setItem(0, 1, new QTableWidgetItem(customer->getName()));
        customerTable->setItem(0, 2, new QTableWidgetItem(customer->getPhone()));
    } else {
        QMessageBox::information(this, "提示", "未找到相关顾客！");
        refreshCustomerTable();
    }
}

void MainWindow::refreshCustomerTable() {
    QVector<Customer> customers = restaurant.getAllCustomers();
    customerTable->setRowCount(customers.size());
    
    for (int i = 0; i < customers.size(); ++i) {
        customerTable->setItem(i, 0, new QTableWidgetItem(QString::number(customers[i].getId())));
        customerTable->setItem(i, 1, new QTableWidgetItem(customers[i].getName()));
        customerTable->setItem(i, 2, new QTableWidgetItem(customers[i].getPhone()));
    }
}
