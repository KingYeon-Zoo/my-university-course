#pragma once
#include "restaurant.h"

// 显示主菜单
void showMenu();

// 显示餐品管理菜单
void showDishMenu();

// 显示订单管理菜单
void showOrderMenu();

// 显示顾客管理菜单
void showCustomerMenu();

// 处理用户选择的功能
void switch_func(Restaurant& restaurant, int choice);


