#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预约记录列表窗口 (极简版本)
使用最基础的PySide6组件，避免API兼容性问题
"""

import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox,
    QComboBox, QTextEdit, QWidget, QDateEdit
)
from PySide6.QtCore import Qt, QDate

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import BloodReservationDB
    HAS_DB = True
except ImportError:
    HAS_DB = False


class ReservationListWindow(QDialog):
    """预约记录列表窗口 (极简版本)"""

    def __init__(self, parent=None, db_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db_instance

        # 设置窗口
        self.setWindowTitle("预约记录汇总 - 血制品预约登记系统")
        self.setMinimumSize(1100, 750)
        self.resize(1100, 750)

        # 设置窗口居中
        self.center_window()

        # 创建界面
        self.setup_ui()

        # 加载数据
        self.load_data()

    def center_window(self):
        """窗口居中"""
        self.adjustSize()
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def setup_ui(self):
        """设置界面"""
        # 设置窗口模态
        self.setModal(True)

        # 应用全局样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                font-size: 13px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#filter_btn {
                background-color: #4CAF50;
            }
            QPushButton#filter_btn:hover {
                background-color: #388E3C;
            }
            QPushButton#clear_filter_btn {
                background-color: #FF9800;
            }
            QPushButton#clear_filter_btn:hover {
                background-color: #F57C00;
            }
            QPushButton#refresh_btn {
                background-color: #9C27B0;
            }
            QPushButton#refresh_btn:hover {
                background-color: #7B1FA2;
            }
            QPushButton#export_btn {
                background-color: #00BCD4;
            }
            QPushButton#export_btn:hover {
                background-color: #0097A7;
            }
            QPushButton#clear_btn {
                background-color: #f44336;
            }
            QPushButton#clear_btn:hover {
                background-color: #d32f2f;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 5px;
            }
            QDateEdit {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
                min-width: 120px;
            }
            QDateEdit:hover {
                border-color: #2196F3;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 5px;
            }
            QWidget#toolbar_widget {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
            QLabel#title_label {
                color: #1976D2;
                font-size: 22px;
                font-weight: bold;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
                border-radius: 8px;
                margin-bottom: 10px;
            }
            QLabel#status_label {
                color: #666666;
                font-size: 12px;
                padding: 8px 12px;
                background-color: #f9f9f9;
                border-left: 3px solid #2196F3;
                border-radius: 4px;
            }
            QLabel#separator_label {
                color: #999999;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#stats_label {
                color: #1976D2;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: #E3F2FD;
                border-radius: 4px;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("预约记录汇总")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        title_label.setMinimumHeight(60)
        main_layout.addWidget(title_label)

        # 工具栏容器
        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("toolbar_widget")
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(15, 15, 15, 15)
        toolbar_layout.setSpacing(15)

        # 院区筛选区域
        campus_group_layout = QVBoxLayout()
        campus_group_layout.setSpacing(5)

        campus_filter_label = QLabel("院区筛选")
        campus_filter_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        campus_group_layout.addWidget(campus_filter_label)

        self.campus_combo = QComboBox()
        self.campus_combo.addItems([
            "全部院区",
            "光谷院区",
            "中法院区",
            "军山院区"
        ])
        self.campus_combo.setMinimumWidth(140)
        campus_group_layout.addWidget(self.campus_combo)

        toolbar_layout.addLayout(campus_group_layout)

        # 分隔线
        separator = QLabel(" | ")
        separator.setObjectName("separator_label")
        toolbar_layout.addWidget(separator)

        # 日期筛选区域
        date_group_layout = QVBoxLayout()
        date_group_layout.setSpacing(5)

        date_filter_label = QLabel("时间筛选")
        date_filter_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        date_group_layout.addWidget(date_filter_label)

        date_input_layout = QHBoxLayout()
        date_input_layout.setSpacing(8)

        # 开始日期
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-1))  # 默认1天前（昨天）
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_input_layout.addWidget(self.start_date_edit)

        date_to_label = QLabel("至")
        date_to_label.setStyleSheet("color: #666; font-weight: bold;")
        date_input_layout.addWidget(date_to_label)

        # 结束日期
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_input_layout.addWidget(self.end_date_edit)

        date_group_layout.addLayout(date_input_layout)
        toolbar_layout.addLayout(date_group_layout)

        toolbar_layout.addStretch()

        # 操作按钮区域
        button_group_layout = QVBoxLayout()
        button_group_layout.setSpacing(8)

        # 筛选按钮
        filter_buttons_layout = QHBoxLayout()
        filter_buttons_layout.setSpacing(10)

        self.filter_btn = QPushButton("✓ 应用筛选")
        self.filter_btn.setObjectName("filter_btn")
        self.filter_btn.setMinimumHeight(35)
        self.filter_btn.clicked.connect(self.apply_filters)
        filter_buttons_layout.addWidget(self.filter_btn)

        self.clear_filter_btn = QPushButton("↺ 清除筛选")
        self.clear_filter_btn.setObjectName("clear_filter_btn")
        self.clear_filter_btn.setMinimumHeight(35)
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        filter_buttons_layout.addWidget(self.clear_filter_btn)

        button_group_layout.addLayout(filter_buttons_layout)

        # 功能按钮区域
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(10)

        self.refresh_btn = QPushButton("⟳ 刷新")
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.setMinimumHeight(35)
        self.refresh_btn.clicked.connect(self.load_data)
        action_buttons_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("⤓ 导出数据")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.setMinimumHeight(35)
        self.export_btn.clicked.connect(self.export_data)
        action_buttons_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("✖ 清空所有")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.setMinimumHeight(35)
        self.clear_btn.clicked.connect(self.clear_all)
        action_buttons_layout.addWidget(self.clear_btn)

        button_group_layout.addLayout(action_buttons_layout)

        toolbar_layout.addLayout(button_group_layout)

        # 统计信息
        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignCenter)

        self.stats_label = QLabel("总记录数: 0")
        self.stats_label.setObjectName("stats_label")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setMinimumWidth(150)
        stats_layout.addWidget(self.stats_label)

        toolbar_layout.addLayout(stats_layout)

        main_layout.addWidget(toolbar_widget)

        # 记录列表区域
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 10, 0, 0)

        list_title = QLabel("预约记录列表")
        list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; margin-bottom: 10px;")
        list_layout.addWidget(list_title)

        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setMinimumHeight(500)

        # 定义列
        self.columns = ["ID", "院区", "血制品大类", "血制品亚类", "血型", "数量", "预约时间"]
        self.table_widget.setColumnCount(len(self.columns))
        self.table_widget.setHorizontalHeaderLabels(self.columns)

        # 设置列宽
        column_widths = [60, 120, 120, 150, 80, 80, 200]
        for i, width in enumerate(column_widths):
            self.table_widget.setColumnWidth(i, width)

        # 最后一列拉伸
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        # 设置表格属性
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.verticalHeader().setVisible(False)

        # 连接双击事件
        self.table_widget.doubleClicked.connect(self.view_details)

        list_layout.addWidget(self.table_widget)

        main_layout.addWidget(list_container)

        # 状态栏
        self.status_label = QLabel("就绪 - 双击记录查看详情")
        self.status_label.setObjectName("status_label")
        self.status_label.setMinimumHeight(40)
        main_layout.addWidget(self.status_label)

        # 关闭按钮
        close_btn = QPushButton("✖ 关闭")
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #37474F;
            }
        """)
        close_btn.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def load_data(self):
        """加载数据"""
        try:
            # 清空表格
            self.table_widget.setRowCount(0)

            if not HAS_DB or not self.db:
                # 演示模式
                demo_data = [
                    (1, "光谷院区", "红细胞", "悬浮红细胞", "A型", 1.0, "2024-11-11 10:30:00"),
                    (2, "中法院区", "血小板", "单采血小板", "B型", 5.0, "2024-11-11 11:00:00"),
                    (3, "军山院区", "新鲜冰冻血浆", "", "O型", 3.0, "2024-11-11 14:30:00"),
                ]
                all_data = demo_data
            else:
                # 从数据库获取数据
                all_data = self.db.get_all_reservations()

            # 插入数据到表格
            row = 0
            for record in all_data:
                if len(record) >= 7:
                    res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record

                    if not subtype or subtype == '':
                        subtype = '无'

                    # 根据血制品类型显示不同的单位
                    if product_type == "新鲜冰冻血浆":
                        quantity_display = f"{quantity} ml"
                    else:
                        quantity_display = f"{quantity} 单位"

                    # 插入行
                    self.table_widget.insertRow(row)

                    # 设置单元格数据
                    self.table_widget.setItem(row, 0, QTableWidgetItem(str(res_id)))
                    self.table_widget.setItem(row, 1, QTableWidgetItem(campus))
                    self.table_widget.setItem(row, 2, QTableWidgetItem(product_type))
                    self.table_widget.setItem(row, 3, QTableWidgetItem(subtype))
                    self.table_widget.setItem(row, 4, QTableWidgetItem(blood_type))
                    self.table_widget.setItem(row, 5, QTableWidgetItem(quantity_display))
                    self.table_widget.setItem(row, 6, QTableWidgetItem(reservation_time))

                    # 设置行高
                    self.table_widget.setRowHeight(row, 30)

                    row += 1

            # 更新统计信息
            count = self.table_widget.rowCount()
            self.stats_label.setText(f"总记录数: {count}")
            self.status_label.setText(f"已加载 {count} 条记录")

        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"加载数据失败：\n{str(e)}\n\n请检查数据库文件或联系管理员"
            )

    def view_details(self, row, column):
        """查看记录详情 (表格双击事件)"""
        try:
            # 获取选中行的数据
            if row < 0 or row >= self.table_widget.rowCount():
                return

            record_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                record_data.append(item.text() if item else "")

            if len(record_data) >= 7:
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record_data
                details = f"""
预约记录详情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

预约编号: {res_id}
院区: {campus}
血制品大类: {product_type}
血制品亚类: {subtype}
血型: {blood_type}
数量: {quantity}
预约时间: {reservation_time}
"""
                QMessageBox.information(self, "记录详情", details)
            else:
                QMessageBox.warning(self, "提示", "记录格式不正确")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看详情失败：{str(e)}")

    def export_data(self):
        """导出数据（Excel/CSV）"""
        if not HAS_DB or not self.db:
            QMessageBox.information(self, "提示", "演示模式：导出功能不可用")
            return

        try:
            from PySide6.QtWidgets import QFileDialog
            from utils.exporter_pyside6 import DataExporter

            # 获取数据库数据
            all_data = self.db.get_all_reservations()

            if not all_data:
                QMessageBox.warning(self, "警告", "没有数据可导出！")
                return

            # 转换数据格式
            formatted_data = []
            for record in all_data:
                if len(record) >= 7:
                    formatted_data.append(record)

            if not formatted_data:
                QMessageBox.warning(self, "警告", "没有有效数据可导出！")
                return

            # 询问导出格式
            reply = QMessageBox.question(
                self,
                "选择导出格式",
                "要导出为Excel格式吗？\n\n"
                "是 (Yes) - 导出为 Excel (.xlsx)\n"
                "否 (No) - 导出为 CSV (.csv)",
                QMessageBox.Yes | QMessageBox.No
            )

            file_format = "xlsx" if reply == QMessageBox.Yes else "csv"

            # 导出数据
            exporter = DataExporter(self)
            success = exporter.export_data(formatted_data, file_format)

            if success:
                self.status_label.setText(f"数据已导出为 {file_format.upper()} 格式")

        except Exception as e:
            QMessageBox.critical(
                self,
                "导出失败",
                f"导出数据时发生错误：\n{str(e)}"
            )

    def clear_all(self):
        """清空所有记录"""
        if not HAS_DB or not self.db:
            QMessageBox.information(self, "提示", "演示模式：清空功能不可用")
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有预约记录吗？\n\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                affected_rows = self.db.clear_all_reservations()
                self.load_data()
                QMessageBox.information(self, "成功", f"所有记录已清空 (共删除 {affected_rows} 条)")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清空失败：{str(e)}")

    def apply_filters(self):
        """应用筛选（院区+日期）"""
        try:
            # 获取院区筛选
            selected_campus = self.campus_combo.currentText()

            # 获取日期范围
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            # 验证日期
            if start_date > end_date:
                QMessageBox.warning(self, "警告", "开始日期不能晚于结束日期！")
                return

            # 清空表格
            self.table_widget.setRowCount(0)

            if not HAS_DB or not self.db:
                # 演示模式：显示所有记录
                self.load_data()
                return

            # 从数据库获取数据
            all_data = self.db.get_all_reservations()
            row = 0

            for record in all_data:
                if len(record) >= 7:
                    res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record

                    # 检查院区筛选
                    if selected_campus != "全部院区" and campus != selected_campus:
                        continue

                    # 提取记录的日期部分 (YYYY-MM-DD)
                    record_date = reservation_time[:10]

                    # 检查是否在日期范围内
                    if start_date <= record_date <= end_date:
                        if not subtype or subtype == '':
                            subtype = '无'

                        # 根据血制品类型显示不同的单位
                        if product_type == "新鲜冰冻血浆":
                            quantity_display = f"{quantity} ml"
                        else:
                            quantity_display = f"{quantity} 单位"

                        # 插入行
                        self.table_widget.insertRow(row)

                        # 设置单元格数据
                        self.table_widget.setItem(row, 0, QTableWidgetItem(str(res_id)))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(campus))
                        self.table_widget.setItem(row, 2, QTableWidgetItem(product_type))
                        self.table_widget.setItem(row, 3, QTableWidgetItem(subtype))
                        self.table_widget.setItem(row, 4, QTableWidgetItem(blood_type))
                        self.table_widget.setItem(row, 5, QTableWidgetItem(quantity_display))
                        self.table_widget.setItem(row, 6, QTableWidgetItem(reservation_time))

                        # 设置行高
                        self.table_widget.setRowHeight(row, 30)

                        row += 1

            # 更新统计信息
            count = self.table_widget.rowCount()
            filter_info = []
            if selected_campus != "全部院区":
                filter_info.append(f"院区: {selected_campus}")
            filter_info.append(f"日期: {start_date} 至 {end_date}")

            filter_str = " | ".join(filter_info)
            self.stats_label.setText(f"筛选结果: {count} 条记录 ({filter_str})")
            self.status_label.setText(f"已筛选，显示 {count} 条记录")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"筛选失败：{str(e)}")

    def clear_filters(self):
        """清除所有筛选，显示所有记录"""
        try:
            # 重置院区选择
            self.campus_combo.setCurrentIndex(0)  # "全部院区"

            # 重置日期为默认值（昨天至今）
            self.start_date_edit.setDate(QDate.currentDate().addDays(-1))
            self.end_date_edit.setDate(QDate.currentDate())

            # 重新加载所有数据
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"清除筛选失败：{str(e)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        event.accept()
        if self.parent:
            self.parent.show()
            if hasattr(self.parent, 'statusBar'):
                self.parent.statusBar().showMessage("返回主窗口")


def main():
    """测试函数"""
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    window = ReservationListWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
