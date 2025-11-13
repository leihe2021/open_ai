#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库功能测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import BloodReservationDB
    print("[OK] 数据库模块导入成功")
except ImportError as e:
    print(f"[ERROR] 数据库模块导入失败: {e}")
    sys.exit(1)

def test_database():
    """测试数据库功能"""
    print("\n" + "="*50)
    print("血制品预约系统 - 数据库功能测试")
    print("="*50)

    # 初始化数据库
    print("\n1. 初始化数据库...")
    db = BloodReservationDB("test_records.db")
    print("[OK] 数据库创建成功")

    # 测试添加预约记录
    print("\n2. 测试添加预约记录...")
    test_data = [
        ("光谷院区", "红细胞", "悬浮红细胞", "A型", 2, "2024-11-11 10:30:00"),
        ("中法院区", "血小板", "单采血小板", "B型", 1, "2024-11-11 11:00:00"),
        ("军山院区", "新鲜冰冻血浆", "", "O型", 3, "2024-11-11 14:30:00"),
    ]

    for campus, product_type, subtype, blood_type, quantity, reservation_time in test_data:
        db.add_reservation(campus, product_type, subtype, blood_type, quantity, reservation_time)
        print(f"  [OK] 添加预约: {campus} - {product_type} - {blood_type} - 数量:{quantity}")

    # 测试获取所有记录
    print("\n3. 获取所有预约记录...")
    records = db.get_all_reservations()
    print(f"  总计 {len(records)} 条记录")
    print("\n  记录详情:")
    print("  " + "-"*80)
    for record in records:
        res_id, campus, product_type, subtype, blood_type, quantity, reservation_time, created_at = record
        print(f"  ID: {res_id} | 院区: {campus} | 血制品: {product_type} | "
              f"亚类: {subtype or '无'} | 血型: {blood_type} | 数量: {quantity} | "
              f"预约时间: {reservation_time}")
    print("  " + "-"*80)

    # 测试根据ID获取记录
    print("\n4. 测试根据ID查询...")
    if records:
        test_id = records[0][0]
        record = db.get_reservation_by_id(test_id)
        if record:
            print(f"  [OK] 查询ID={test_id} 成功")
            print(f"  记录: {record}")
        else:
            print(f"  [ERROR] 查询ID={test_id} 失败")

    # 清理测试文件
    print("\n5. 清理测试文件...")
    if os.path.exists("test_records.db"):
        os.remove("test_records.db")
        print("  [OK] 测试文件已清理")

    print("\n" + "="*50)
    print("[SUCCESS] 所有数据库功能测试通过！")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_database()
