"""
TCP协议可视化分析工具 - 主程序
作者: 朱清扬
学号: 2023212290
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet
from gui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("TCP协议可视化分析工具")
    app.setOrganizationName("合肥工业大学")
    
    # 应用现代化主题（浅色主题，白色背景）
    apply_stylesheet(app, theme='light_blue.xml', invert_secondary=False)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

