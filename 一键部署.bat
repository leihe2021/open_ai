@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 血制品预约登记系统 - 一键部署工具

color 0A
mode con: cols=70 lines=40

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                          ██
echo ██            血制品预约登记系统 - 一键部署工具             ██
echo ██                                                          ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 请选择部署方式:
echo.
echo   [1] 自动安装依赖并打包为exe (推荐)
echo   [2] 仅安装依赖，不打包
echo   [3] 仅打包，不安装依赖
echo   [4] 运行程序 (开发模式)
echo   [5] 测试数据库功能
echo   [0] 退出
echo.
set /p choice=请输入选项 [0-5]:

if "%choice%"=="1" goto auto_deploy
if "%choice%"=="2" goto install_only
if "%choice%"=="3" goto build_only
if "%choice%"=="4" goto run_dev
if "%choice%"=="5" goto test_db
if "%choice%"=="0" goto exit
goto menu

:auto_deploy
echo.
echo ================================================================
echo  [自动模式] 正在安装依赖并打包...
echo ================================================================
echo.

echo [步骤 1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未找到Python环境！
    echo.
    echo 请先安装Python 3.8-3.11
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    goto menu
)

echo [OK] Python环境正常
echo.

echo [步骤 2/3] 安装依赖包...
echo  正在安装 PySide6 (GUI框架)...
pip install "PySide6>=6.6.0,<6.7.0" --quiet --no-warn-script-location
if errorlevel 1 (
    echo  [警告] 尝试使用最新版本...
    pip install PySide6 --quiet --no-warn-script-location
)
echo  正在安装 reportlab (PDF生成)...
pip install reportlab==4.1.0 --quiet --no-warn-script-location
echo  正在安装 pyinstaller (打包工具)...
pip install pyinstaller --quiet --no-warn-script-location
echo  正在安装其他依赖...
pip install -r requirements.txt --quiet --no-warn-script-location 2>nul
echo [OK] 依赖安装完成
echo.

echo [步骤 3/3] 开始打包...
pyinstaller --clean build.spec

echo.
echo ================================================================
echo  检查打包结果...
echo ================================================================
echo.

if exist "dist\预约血.exe" (
    echo ✅ 打包成功！
    echo.
    echo 文件信息:
    for %%A in ("dist\预约血.exe") do echo   - 文件名: 预约血.exe
    for %%A in ("dist\预约血.exe") do echo   - 大小:   %%~zA 字节
    for %%A in ("dist\预约血.exe") do echo   - 路径:   !cd!\dist\
    echo.
    echo 📋 部署说明:
    echo   1. 将 dist 目录下的所有文件复制到目标电脑
    echo   2. 双击 "预约血.exe" 即可运行
    echo   3. 首次运行会自动创建数据库
    echo.
    echo 是否现在打开dist目录? (Y/N)
    set /p open_dir=
    if /i "!open_dir!"=="Y" explorer dist
) else (
    echo ❌ 打包失败！
    echo.
    echo 请检查:
    echo   1. Python版本是否为3.8-3.11
    echo   2. 是否有足够的磁盘空间
    echo   3. 是否关闭了杀毒软件
    echo   4. 查看上方错误信息
    echo.
)

goto end

:install_only
echo.
echo ================================================================
echo  [仅安装模式] 正在安装依赖...
echo ================================================================
echo.
pip install "PySide6>=6.6.0,<6.7.0" reportlab pyinstaller
if errorlevel 1 (
    echo.
    echo 部分包安装失败，尝试使用最新版本...
    pip install PySide6 reportlab pyinstaller
)
goto end

:build_only
echo.
echo ================================================================
echo  [仅打包模式] 正在打包...
echo ================================================================
echo.
pyinstaller --clean build.spec
if exist "dist\预约血.exe" (
    echo.
    echo ✅ 打包完成，文件位于: dist\预约血.exe
) else (
    echo.
    echo ❌ 打包失败，请先运行 [选项2] 安装依赖
)
goto end

:run_dev
echo.
echo ================================================================
echo  [开发模式] 正在运行程序...
echo ================================================================
echo.
python main.py
goto end

:test_db
echo.
echo ================================================================
echo  [测试模式] 正在测试数据库功能...
echo ================================================================
echo.
python test_db.py
goto end

:menu
echo.
echo 无效选项，请重新选择
echo.
pause >nul
cls
goto :eof

:exit
echo.
echo 感谢使用！
echo.
timeout /t 2 >nul
exit /b 0

:end
echo.
echo ================================================================
echo 操作完成
echo ================================================================
echo.
pause >nul
cls
goto :eof
