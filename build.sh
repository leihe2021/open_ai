#!/bin/bash
echo "================================"
echo "血制品预约登记系统 - 打包脚本"
echo "================================"
echo

echo "正在安装依赖包..."
pip install -r requirements.txt

echo
echo "正在使用PyInstaller打包..."
pyinstaller --clean build.spec

echo
echo "打包完成！"
echo "可执行文件位置: dist/预约血"
echo
