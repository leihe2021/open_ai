import sqlite3
import os
from datetime import datetime

class BloodReservationDB:
    """血制品预约数据库管理类"""

    def __init__(self, db_path="records.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """创建数据库和表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建预约记录表（包含数量字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_campus TEXT NOT NULL,
                blood_product_type TEXT NOT NULL,
                blood_product_subtype TEXT,
                blood_type TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1.0,
                reservation_time TEXT NOT NULL
            )
        ''')

        # 自动升级表结构（v1.0 -> v1.1+）
        self._upgrade_table_structure(cursor)

        conn.commit()
        conn.close()

    def _upgrade_table_structure(self, cursor):
        """自动升级表结构到最新版本"""
        try:
            cursor.execute("PRAGMA table_info(reservations)")
            columns_info = cursor.fetchall()
            columns = [row[1] for row in columns_info]

            # 检查quantity字段的类型
            quantity_type = None
            for col in columns_info:
                if col[1] == 'quantity':
                    quantity_type = col[2]  # 列类型
                    break

            # 检查是否存在created_at字段
            has_created_at = 'created_at' in columns

            # 如果quantity是INTEGER类型或存在created_at，需要重建表
            if quantity_type == 'INTEGER' or has_created_at:
                print("正在升级数据库表结构到最新版本...")
                self._recreate_table(cursor)
                print("[OK] 数据库升级成功 - 已更新表结构")
        except sqlite3.OperationalError as e:
            # 如果表已存在或字段已存在，忽略错误
            pass

    def _recreate_table(self, cursor):
        """重建表结构（删除created_at字段，将quantity改为REAL）"""
        # 创建新表
        cursor.execute('''
            CREATE TABLE reservations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_campus TEXT NOT NULL,
                blood_product_type TEXT NOT NULL,
                blood_product_subtype TEXT,
                blood_type TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1.0,
                reservation_time TEXT NOT NULL
            )
        ''')

        # 复制数据（不包括created_at）
        cursor.execute('''
            INSERT INTO reservations_new (
                id, hospital_campus, blood_product_type, blood_product_subtype,
                blood_type, quantity, reservation_time
            )
            SELECT
                id, hospital_campus, blood_product_type, blood_product_subtype,
                blood_type, CAST(quantity AS REAL), reservation_time
            FROM reservations
        ''')

        # 删除旧表
        cursor.execute('DROP TABLE reservations')

        # 重命名新表
        cursor.execute('ALTER TABLE reservations_new RENAME TO reservations')

    def add_reservation(self, campus, product_type, subtype, blood_type, quantity, reservation_time):
        """添加预约记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reservations (
                hospital_campus, blood_product_type, blood_product_subtype,
                blood_type, quantity, reservation_time
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (campus, product_type, subtype, blood_type, quantity, reservation_time))

        conn.commit()
        conn.close()
        return True

    def get_all_reservations(self):
        """获取所有预约记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, hospital_campus, blood_product_type, blood_product_subtype,
                   blood_type, quantity, reservation_time
            FROM reservations
            ORDER BY id DESC
        ''')

        results = cursor.fetchall()
        conn.close()
        return results

    def get_reservation_by_id(self, res_id):
        """根据ID获取预约记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, hospital_campus, blood_product_type, blood_product_subtype,
                   blood_type, quantity, reservation_time
            FROM reservations
            WHERE id = ?
        ''', (res_id,))

        result = cursor.fetchone()
        conn.close()
        return result

    def delete_reservation(self, res_id):
        """删除指定ID的预约记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows

    def clear_all_reservations(self):
        """清空所有预约记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reservations")
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows
