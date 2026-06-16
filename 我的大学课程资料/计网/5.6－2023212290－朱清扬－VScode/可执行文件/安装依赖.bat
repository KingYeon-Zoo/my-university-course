@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo     依赖库安装脚本
echo ═══════════════════════════════════════════════════════════
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未检测到Python环境！
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python环境检测成功
echo.

echo 开始安装依赖库...
echo 使用清华大学镜像源加速下载...
echo.

cd /d "%~dp0..\源程序"

echo 当前目录：
cd
echo.

echo 正在安装，请稍候...
echo.

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo ✗ 安装失败！
    echo.
    echo 请尝试以下方法：
    echo 1. 使用管理员权限运行此脚本
    echo 2. 手动执行: pip install -r requirements.txt
    echo 3. 检查网络连接
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo ✓ 依赖库安装完成！
echo.
echo 已安装以下库：
echo - PyQt5        (图形界面框架)
echo - scapy        (数据包解析)
echo - matplotlib   (数据可视化)
echo - numpy        (数值计算)
echo - pandas       (数据处理)
echo - pyqtgraph    (实时绘图)
echo - qt-material  (Material Design主题)
echo - Pillow       (图像处理)
echo.
echo 现在可以运行程序了！
echo ═══════════════════════════════════════════════════════════
echo.
pause

