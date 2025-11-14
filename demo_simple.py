#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
血制品预约登记系统 v1.1 - GUI演示
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 80)
    print("血制品预约登记系统 v1.1 - GUI功能概览")
    print("=" * 80)
    print()
    
    print("当前运行状态: GUI程序已在后台启动")
    print()
    
    print("=" * 80)
    print("主要功能区域:")
    print("=" * 80)
    print()
    
    print("1. 主界面 (MainWindow)")
    print("   - 标题: 血制品预约登记 v1.1")
    print("   - 院区选择: 光谷院区/中法院区/军山院区")
    print("   - 血制品: 红细胞/血小板/新鲜冰冻血浆")
    print("   - 血型: A型/B型/O型/AB型 (单选)")
    print("   - 数量: 0.1-10000 (小数支持)")
    print("   - 预约时间: 自动记录")
    print("   - 操作按钮:")
    print("     * 提交预约")
    print("     * 打印预约单")
    print("     * 查看所有预约")
    print()
    
    print("2. 预约列表窗口 (ReservationListWindow)")
    print("   - 显示所有预约记录")
    print("   - 日期筛选功能")
    print("   - 导出数据 (Excel/CSV)")
    print("   - 打印汇总")
    print()
    
    print("3. 数据库 (SQLite)")
    print("   - 文件: records.db")
    print("   - 字段: 7个 (v1.1格式)")
    print("   - 支持自动迁移 (v1.0->v1.1)")
    print()
    
    print("4. 工具模块")
    print("   - PDF打印 (ReportLab)")
    print("   - 数据导出 (openpyxl/CSV)")
    print("   - 中文字体支持")
    print()
    
    print("=" * 80)
    print("v1.1 新增功能:")
    print("=" * 80)
    print("  [NEW] 数量字段 (支持小数)")
    print("  [NEW] 数据导出 (Excel/CSV)")
    print("  [NEW] 批量打印")
    print("  [NEW] 预约列表窗口")
    print("  [NEW] 自动数据库迁移")
    print()
    
    print("=" * 80)
    print("测试命令:")
    print("=" * 80)
    print("  python test_all_features.py     # 完整测试")
    print("  python test_db.py               # 数据库测试")
    print("  python test_program_flow.py     # 流程测试")
    print()
    
    print("=" * 80)
    print("构建命令:")
    print("=" * 80)
    print("  build.bat                       # Windows打包")
    print("  pyinstaller --clean build.spec  # 手动打包")
    print()
    
    print("=" * 80)
    print("当前状态: 程序正在运行...")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
