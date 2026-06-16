@echo off
chcp 65001 >nul
echo ========================================
echo Reflexion 论文实验模拟 - 一键生成
echo ========================================
echo.

echo [1/2] 正在运行实验模拟...
python simulate_reflexion.py
echo.

echo [2/2] 正在生成可视化图表...
python generate_charts.py
echo.

echo ========================================
echo 全部完成！
echo ========================================
echo.
echo 生成的文件：
echo   - 实验输出示例.txt (控制台输出，可截图)
echo   - experiment_results.json (详细数据)
echo   - 图表1_成功率趋势.png
echo   - 图表2_方法对比.png
echo   - 图表3_任务类型分析.png
echo   - 图表4_性能提升分析.png
echo   - 图表5_学习曲线.png
echo   - 图表6_综合仪表板.png
echo.
pause

