#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
血制品预约登记系统 - 打包脚本
使用PyInstaller将Python程序打包为exe可执行文件
"""

import os
import sys
from PyInstaller.__main__ import run

def build_exe():
    """打包为exe文件"""

    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))

    # 主程序文件
    main_script = os.path.join(project_root, 'main_demo.py')

    # 输出目录
    output_dir = os.path.join(project_root, 'dist')

    print("=" * 60)
    print("血制品预约登记系统 - 打包工具")
    print("=" * 60)
    print(f"项目路径: {project_root}")
    print(f"主程序: {main_script}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)

    # 检查主程序文件是否存在
    if not os.path.exists(main_script):
        print(f"错误: 找不到主程序文件 {main_script}")
        return False

    # 切换到项目目录
    os.chdir(project_root)

    # 使用命令行的方式调用 PyInstaller（避免路径问题）
    import subprocess

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # 打包为单个exe文件
        '--windowed',  # Windows下不显示控制台窗口
        '--name=BloodReservationSystem',  # 使用英文名避免编码问题
        '--clean',  # 清理临时文件
        '--noconfirm',  # 覆盖输出目录
        '--distpath=dist',  # 输出目录
        '--workpath=build',  # 临时目录
        'main_demo.py'  # 主程序文件（相对于当前目录）
    ]

    print("\n开始打包...")
    print(f"执行命令: {' '.join(cmd)}\n")

    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        print(f"\n输出位置: {output_dir}")
        print("\n生成的文件:")
        exe_path = os.path.join(output_dir, 'BloodReservationSystem.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"  ✅ BloodReservationSystem.exe ({file_size:.1f} MB)")
        else:
            print("  ❌ 未找到生成的exe文件")

        print("\n" + "=" * 60)
        print("部署说明:")
        print("=" * 60)
        print("1. 将exe文件复制到目标电脑")
        print("2. 直接双击运行，无需安装Python")
        print("3. 系统会自动创建数据库文件 records.db")
        print("4. 如需PDF输出功能，请配置中文字体（参考PDF中文字体配置说明.md）")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
