/*
 * 主程序入口文件
 * 这个文件是Qt应用程序的入口点，负责初始化应用程序并启动主窗口
 */

// 包含主窗口的头文件
#include "mainwindow.h"

// 包含Qt核心组件
#include <QApplication>  // Qt应用程序类
#include <QLocale>      // 本地化支持类
#include <QTranslator>  // 翻译器类，用于多语言支持

/**
 * @brief 程序入口函数
 * @param argc 命令行参数数量
 * @param argv 命令行参数数组
 * @return 应用程序退出码
 */
int main(int argc, char *argv[])
{
    // 创建Qt应用程序对象
    // 这是每个Qt GUI应用程序必须创建的核心对象
    QApplication a(argc, argv);

    // 初始化国际化支持
    QTranslator translator;
    // 获取系统UI语言列表
    const QStringList uiLanguages = QLocale::system().uiLanguages();
    // 遍历所有可用的语言
    for (const QString &locale : uiLanguages) {
        // 构建翻译文件的基础名称，格式为"restaurant_语言代码"
        const QString baseName = "restaurant_" + QLocale(locale).name();
        // 尝试加载对应的翻译文件
        if (translator.load(":/i18n/" + baseName)) {
            // 如果成功加载翻译文件，则安装翻译器
            a.installTranslator(&translator);
            break;
        }
    }

    // 创建主窗口对象
    MainWindow w;
    // 显示主窗口
    w.show();
    
    // 启动应用程序的事件循环
    // 程序将在此处等待，直到主窗口被关闭
    return a.exec();
}
