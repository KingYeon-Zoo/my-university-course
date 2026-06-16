@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo     TCP协议可视化分析工具 - 快速启动脚本
echo ═══════════════════════════════════════════════════════════
echo.
echo 学号：2023212290
echo 姓名：朱清扬
echo.
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/3] 检查Python环境...
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
echo ✓ Python环境正常
echo.

echo [2/3] 检查依赖库...
echo 正在检查是否已安装所需依赖...
echo.

python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ✗ 缺少必要的依赖库
    echo.
    echo 是否现在安装依赖库？
    echo 这可能需要几分钟时间...
    echo.
    choice /C YN /M "请选择 (Y=是, N=否)"
    if errorlevel 2 goto :skip_install
    if errorlevel 1 goto :install_deps
) else (
    echo ✓ 依赖库检查通过
    echo.
    goto :run_program
)

:install_deps
echo.
echo 正在安装依赖库...
echo 使用清华镜像加速下载...
echo.
cd /d "%~dp0..\源程序"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo.
    echo ✗ 依赖安装失败
    echo.
    echo 请手动执行以下命令：
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo.
echo ✓ 依赖库安装完成
echo.
goto :run_program

:skip_install
echo.
echo 跳过依赖安装，程序可能无法正常运行
echo.

:run_program
echo [3/3] 启动程序...
echo.
cd /d "%~dp0..\源程序"
python main.py

if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo 程序异常退出
    echo.
    echo 如果提示缺少模块，请运行以下命令安装依赖：
    echo pip install -r requirements.txt
    echo ═══════════════════════════════════════════════════════════
    echo.
    pause
)

exit /b 0

