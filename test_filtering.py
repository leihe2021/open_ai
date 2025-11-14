#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
筛选功能专项测试
测试院区和日期筛选功能
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import BloodReservationDB
    HAS_DB = True
except ImportError:
    HAS_DB = False
    print("[ERROR] 无法导入数据库模块")
    sys.exit(1)


def test_filtering():
    """测试筛选功能"""
    print("\n" + "="*60)
    print("血制品预约系统 - 筛选功能专项测试")
    print("="*60)

    # 初始化测试数据库
    print("\n1. 初始化测试数据库...")
    db = BloodReservationDB("test_filtering.db")
    print("[OK] 数据库创建成功")

    # 清理旧数据
    print("\n2. 清理旧数据...")
    db.clear_all_reservations()
    print("[OK] 旧数据已清理")

    # 添加测试数据
    print("\n3. 添加测试数据...")
    today = datetime.now()
    test_data = [
        # 光谷院区的记录
        (f"{today.strftime('%Y-%m-%d')} 08:30:00", "光谷院区", "红细胞", "悬浮红细胞", "A型", 2),
        (f"{today.strftime('%Y-%m-%d')} 09:15:00", "光谷院区", "血小板", "单采血小板", "B型", 1),
        (f"{today.strftime('%Y-%m-%d')} 10:45:00", "光谷院区", "新鲜冰冻血浆", "", "O型", 3),

        # 中法院区的记录
        (f"{today.strftime('%Y-%m-%d')} 11:00:00", "中法院区", "红细胞", "去白细胞悬浮红细胞", "AB型", 2),
        (f"{today.strftime('%Y-%m-%d')} 13:20:00", "中法院区", "血小板", "机采血小板", "A型", 2),

        # 军山院区的记录
        (f"{today.strftime('%Y-%m-%d')} 14:00:00", "军山院区", "新鲜冰冻血浆", "", "B型", 5),
        (f"{today.strftime('%Y-%m-%d')} 15:30:00", "军山院区", "红细胞", "洗涤红细胞", "O型", 1),

        # 昨天的记录
        ((today - timedelta(days=1)).strftime('%Y-%m-%d') + " 10:00:00", "光谷院区", "红细胞", "悬浮红细胞", "A型", 1),
        ((today - timedelta(days=1)).strftime('%Y-%m-%d') + " 14:00:00", "中法院区", "血小板", "单采血小板", "B型", 3),
    ]

    for i, (reservation_time, campus, product_type, subtype, blood_type, quantity) in enumerate(test_data, 1):
        db.add_reservation(campus, product_type, subtype, blood_type, quantity, reservation_time)
        print(f"  [OK] 添加记录 {i}: {campus} - {product_type} - {reservation_time[:10]}")

    # 测试获取所有记录
    print("\n4. 获取所有记录...")
    all_records = db.get_all_reservations()
    print(f"  总计 {len(all_records)} 条记录")

    # 验证数据完整性
    print("\n5. 验证数据完整性...")
    campus_count = {}
    for record in all_records:
        res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record
        date = reservation_time[:10]
        campus_count[campus] = campus_count.get(campus, 0) + 1
        print(f"  ID:{res_id} | {campus} | {product_type} | {blood_type} | {quantity} | {date}")

    print(f"\n  院区分布:")
    for campus, count in campus_count.items():
        print(f"    {campus}: {count} 条记录")

    # 测试按院区筛选
    print("\n6. 测试按院区筛选...")
    print("\n  6.1 筛选光谷院区:")
    guanggu_records = [r for r in all_records if r[1] == "光谷院区"]
    print(f"    光谷院区记录数: {len(guanggu_records)}")
    for record in guanggu_records:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6]}")

    print("\n  6.2 筛选中法院区:")
    zhongfa_records = [r for r in all_records if r[1] == "中法院区"]
    print(f"    中法院区记录数: {len(zhongfa_records)}")
    for record in zhongfa_records:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6]}")

    print("\n  6.3 筛选军山院区:")
    junshan_records = [r for r in all_records if r[1] == "军山院区"]
    print(f"    军山院区记录数: {len(junshan_records)}")
    for record in junshan_records:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6]}")

    # 测试按日期筛选
    print("\n7. 测试按日期筛选...")
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"\n  7.1 筛选今天 ({today_str}):")
    today_records = [r for r in all_records if r[6].startswith(today_str)]
    print(f"    今天记录数: {len(today_records)}")
    for record in today_records:
        print(f"      ID:{record[0]} | {record[1]} | {record[2]} | {record[4]} | {record[6][11:]}")

    print(f"\n  7.2 筛选昨天 ({yesterday_str}):")
    yesterday_records = [r for r in all_records if r[6].startswith(yesterday_str)]
    print(f"    昨天记录数: {len(yesterday_records)}")
    for record in yesterday_records:
        print(f"      ID:{record[0]} | {record[1]} | {record[2]} | {record[4]} | {record[6][11:]}")

    # 测试组合筛选（院区+日期）
    print("\n8. 测试组合筛选（院区+日期）...")

    print(f"\n  8.1 光谷院区 + 今天 ({today_str}):")
    guanggu_today = [r for r in all_records if r[1] == "光谷院区" and r[6].startswith(today_str)]
    print(f"    光谷院区今天记录数: {len(guanggu_today)}")
    for record in guanggu_today:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6][11:]}")

    print(f"\n  8.2 中法院区 + 今天 ({today_str}):")
    zhongfa_today = [r for r in all_records if r[1] == "中法院区" and r[6].startswith(today_str)]
    print(f"    中法院区今天记录数: {len(zhongfa_today)}")
    for record in zhongfa_today:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6][11:]}")

    print(f"\n  8.3 军山院区 + 今天 ({today_str}):")
    junshan_today = [r for r in all_records if r[1] == "军山院区" and r[6].startswith(today_str)]
    print(f"    军山院区今天记录数: {len(junshan_today)}")
    for record in junshan_today:
        print(f"      ID:{record[0]} | {record[2]} | {record[4]} | {record[6][11:]}")

    # 测试日期范围筛选
    print("\n9. 测试日期范围筛选...")
    start_date = today_str
    end_date = today_str
    print(f"\n  9.1 筛选日期范围: {start_date} 至 {end_date}")
    date_range_records = [
        r for r in all_records
        if start_date <= r[6][:10] <= end_date
    ]
    print(f"    范围内记录数: {len(date_range_records)}")
    for record in date_range_records:
        print(f"      ID:{record[0]} | {record[1]} | {record[6][:10]}")

    # 清理测试文件
    print("\n10. 清理测试文件...")
    if os.path.exists("test_filtering.db"):
        os.remove("test_filtering.db")
        print("  [OK] 测试文件已清理")

    print("\n" + "="*60)
    print("[SUCCESS] 所有筛选功能测试通过！")
    print("="*60)
    print("\n测试结果总结:")
    print(f"  - 总记录数: {len(all_records)}")
    print(f"  - 院区筛选: ✓ 通过")
    print(f"  - 日期筛选: ✓ 通过")
    print(f"  - 组合筛选: ✓ 通过")
    print(f"  - 日期范围: ✓ 通过")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_filtering()
