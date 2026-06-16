@echo off
chcp 65001 >nul
echo 开始转换Markdown文件为Word文档...
echo.

echo ========================================
echo 转换大作业中的解题报告
echo ========================================

echo 转换 B-环保数列/解题报告.md
pandoc "大作业\B-环保数列\解题报告.md" -o "大作业\B-环保数列\解题报告.docx"
if %errorlevel% equ 0 (echo ✓ 成功) else (echo ✗ 失败)

echo 转换 F-太阳能板/解题报告.md
pandoc "大作业\F-太阳能板\解题报告.md" -o "大作业\F-太阳能板\解题报告.docx"
if %errorlevel% equ 0 (echo ✓ 成功) else (echo ✗ 失败)

echo 转换 G-动物保护/解题报告.md
pandoc "大作业\G-动物保护\解题报告.md" -o "大作业\G-动物保护\解题报告.docx"
if %errorlevel% equ 0 (echo ✓ 成功) else (echo ✗ 失败)

echo 转换 H-电能输送/解题报告.md
pandoc "大作业\H-电能输送\解题报告.md" -o "大作业\H-电能输送\解题报告.docx"
if %errorlevel% equ 0 (echo ✓ 成功) else (echo ✗ 失败)

echo.
echo ========================================
echo 转换实验报告
echo ========================================

setlocal enabledelayedexpansion
for %%i in (1 2 3 4 5) do (
    echo.
    echo 转换实验%%i的报告:
    for %%f in ("实验\实验%%i\*报告.md") do (
        echo   转换 %%~nxf
        pandoc "%%f" -o "%%~dpnf.docx"
        if !errorlevel! equ 0 (echo   ✓ 成功) else (echo   ✗ 失败)
    )
)
endlocal

echo.
echo ========================================
echo 转换完成！
echo ========================================
pause

