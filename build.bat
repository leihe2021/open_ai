@echo off
chcp 65001 >nul
echo ========================================
echo  血制品预约登记系统 - 一键部署脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python 3.8-3.11
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/4] 安装依赖包...
echo 正在安装 PySide6...
pip install "PySide6>=6.6.0,<6.7.0" --quiet --no-warn-script-location
if errorlevel 1 (
    echo [警告] PySide6 安装失败，尝试使用其他版本...
    pip install PySide6 --quiet --no-warn-script-location
)

echo 正在安装 reportlab...
pip install reportlab==4.1.0 --quiet --no-warn-script-location

echo 正在安装 pyinstaller...
pip install pyinstaller --quiet --no-warn-script-location

echo.
echo [3/4] 使用PyInstaller打包...
pyinstaller --clean build.spec

echo.
echo [4/4] 检查打包结果...
if exist "dist\预约血.exe" (
    echo.
    echo ========================================
    echo  ✅ 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\预约血.exe
    echo 文件大小:
    dir "dist\预约血.exe" | findstr "预约血.exe"
    echo.
    echo 使用说明：
    echo 1. 将 dist 目录下的所有文件复制到目标电脑
    echo 2. 双击 "预约血.exe" 即可运行程序
    echo 3. 首次运行会自动创建数据库文件
    echo.
) else (
    echo.
    echo ========================================
    echo  ❌ 打包失败
    echo ========================================
    echo.
    echo 请检查错误信息并重试。
    echo 如果问题持续，请尝试手动安装依赖。
    echo.
)

pause
