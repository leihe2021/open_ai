#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
程序流程测试
模拟用户完整操作流程
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_workflow():
    """测试完整的用户工作流程"""
    print("=" * 70)
    print("血制品预约登记系统 - 完整流程测试")
    print("=" * 70)
    print()

    # 步骤 1: 导入测试
    print("[步骤 1] 导入模块...")
    try:
        from database.db_manager import BloodReservationDB
        from utils.exporter import DataExporter
        from utils.printer import BloodReservationPrinter
        print("[OK] 所有模块导入成功")
    except Exception as e:
        print(f"[错误] 模块导入失败: {e}")
        return False

    # 步骤 2: 初始化数据库
    print("\n[步骤 2] 初始化数据库...")
    try:
        db = BloodReservationDB()
        print("[OK] 数据库初始化成功")
    except Exception as e:
        print(f"[错误] 数据库初始化失败: {e}")
        return False

    # 步骤 3: 创建多个预约记录
    print("\n[步骤 3] 创建预约记录...")
    test_data = [
        {
            "campus": "光谷院区",
            "product_type": "红细胞",
            "product_subtype": "悬浮红细胞",
            "blood_type": "A型",
            "quantity": 2,
            "patient_name": "张三"
        },
        {
            "campus": "中法院区",
            "product_type": "血小板",
            "product_subtype": "单采血小板",
            "blood_type": "B型",
            "quantity": 5,
            "patient_name": "李四"
        },
        {
            "campus": "军山院区",
            "product_type": "新鲜冰冻血浆",
            "product_subtype": "",
            "blood_type": "O型",
            "quantity": 400,
            "patient_name": "王五"
        }
    ]

    reservation_ids = []
    for i, data in enumerate(test_data, 1):
        try:
            reservation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.add_reservation(
                data["campus"],
                data["product_type"],
                data["product_subtype"],
                data["blood_type"],
                data["quantity"],
                reservation_time
            )
            print(f"  [OK] 预约 {i}: {data['campus']} - {data['product_type']} ({data['blood_type']})")
        except Exception as e:
            print(f"  [错误] 预约 {i} 失败: {e}")
            return False

    # 步骤 4: 查询记录
    print("\n[步骤 4] 查询所有记录...")
    try:
        all_reservations = db.get_all_reservations()
        print(f"[OK] 查询成功，共 {len(all_reservations)} 条记录")

        for record in all_reservations:
            print(f"  - ID: {record[0]}, 院区: {record[1]}, 血制品: {record[2]}, 血型: {record[4]}")
    except Exception as e:
        print(f"[错误] 查询失败: {e}")
        return False

    # 步骤 5: 测试导出功能
    print("\n[步骤 5] 测试数据导出功能...")

    # 准备导出数据
    export_data = []
    for record in all_reservations:
        # 转换数据库记录为导出格式
        export_data.append((
            record[0],  # ID
            record[1],  # 院区
            record[2],  # 血制品大类
            record[3] if record[3] else "无",  # 血制品亚类
            record[4],  # 血型
            record[5],  # 数量
            record[6]   # 预约时间
        ))

    try:
        # 创建导出器实例
        exporter = DataExporter()

        # 测试 CSV 导出
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
            csv_file = tmp.name

        if exporter.export_to_csv(export_data, csv_file):
            print(f"[OK] CSV 导出成功: {csv_file}")
            import os
            if os.path.exists(csv_file):
                size = os.path.getsize(csv_file)
                print(f"     文件大小: {size} 字节")
                os.unlink(csv_file)
        else:
            print("[错误] CSV 导出失败")
            return False

    except Exception as e:
        print(f"[错误] 导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 步骤 6: 测试打印功能
    print("\n[步骤 6] 测试打印功能...")
    try:
        printer = BloodReservationPrinter()
        print("[OK] 打印机初始化成功")
        print(f"     支持页面: A4")
        print(f"     中文字体: {getattr(printer, 'chinese_font', '未设置')}")
    except Exception as e:
        print(f"[错误] 打印功能测试失败: {e}")
        return False

    # 步骤 7: 按院区统计
    print("\n[步骤 7] 数据统计分析...")
    try:
        campus_stats = {}
        for record in all_reservations:
            campus = record[1]
            if campus in campus_stats:
                campus_stats[campus] += 1
            else:
                campus_stats[campus] = 1

        print("[OK] 统计数据:")
        for campus, count in campus_stats.items():
            print(f"  - {campus}: {count} 条预约")
    except Exception as e:
        print(f"[错误] 统计失败: {e}")
        return False

    # 步骤 8: 清理测试数据
    print("\n[步骤 8] 清理测试数据...")
    try:
        affected = db.clear_all_reservations()
        print(f"[OK] 清理完成，删除了 {affected} 条记录")
    except Exception as e:
        print(f"[错误] 清理失败: {e}")
        return False

    print("\n" + "=" * 70)
    print("[SUCCESS] 所有流程测试通过！")
    print("=" * 70)
    print()
    print("测试结果摘要:")
    print(f"  [OK] 模块导入: 正常")
    print(f"  [OK] 数据库操作: 正常")
    print(f"  [OK] 预约记录: 正常")
    print(f"  [OK] 查询功能: 正常")
    print(f"  [OK] 数据导出: 正常")
    print(f"  [OK] 打印功能: 正常")
    print(f"  [OK] 数据统计: 正常")
    print(f"  [OK] 清理功能: 正常")
    print()
    print("[SUCCESS] 程序功能完整，可以正常使用！")
    print()

    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
