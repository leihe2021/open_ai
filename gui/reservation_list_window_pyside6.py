#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预约记录列表窗口 (PySide6版本)
显示所有预约记录的汇总界面
使用与主窗口相同的PySide6框架
"""

import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QMessageBox, QComboBox,
    QDateEdit, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QFont, QIcon

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import BloodReservationDB
    HAS_DB = True
except ImportError:
    HAS_DB = False

try:
    from utils.exporter import DataExporter
    HAS_EXPORTER = True
except ImportError:
    HAS_EXPORTER = False


class ReservationListWindow(QMainWindow):
    """预约记录列表窗口 (PySide6版本)"""

    def __init__(self, parent=None, db_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db_instance

        # 设置窗口
        self.setWindowTitle("预约记录汇总 - 血制品预约登记系统")
        self.setMinimumSize(1000, 600)
        self.resize(1000, 600)

        # 设置窗口居中
        self.center_window()

        # 创建界面
        self.setup_ui()

        # 加载数据
        self.load_data()

        # 设置关闭事件
        self.closeEvent = self.on_closing

    def center_window(self):
        """窗口居中"""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def setup_ui(self):
        """设置界面"""
        # 设置字体
        self.setFont(QFont("Microsoft YaHei", 10))

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel("预约记录汇总")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Microsoft YaHei", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setFixedHeight(50)
        main_layout.addWidget(title_label)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 日期筛选
        filter_label = QLabel("筛选日期:")
        toolbar_layout.addWidget(filter_label)

        self.filter_date_combo = QComboBox()
        self.filter_date_combo.setMinimumWidth(120)
        self.filter_date_combo.addItem("全部")
        self.filter_date_combo.currentTextChanged.connect(self.filter_by_date)
        toolbar_layout.addWidget(self.filter_date_combo)

        toolbar_layout.addSpacing(20)

        # 操作按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("导出数据")
        self.export_btn.clicked.connect(self.export_data)
        toolbar_layout.addWidget(self.export_btn)

        self.pdf_btn = QPushButton("汇总输出为PDF")
        self.pdf_btn.clicked.connect(self.print_all)
        toolbar_layout.addWidget(self.pdf_btn)

        self.clear_btn = QPushButton("清空所有")
        self.clear_btn.clicked.connect(self.clear_all)
        toolbar_layout.addWidget(self.clear_btn)

        toolbar_layout.addStretch()
        self.stats_label = QLabel("总记录数: 0")
        toolbar_layout.addWidget(self.stats_label)

        main_layout.addLayout(toolbar_layout)

        # 创建表格
        self.create_table()
        main_layout.addWidget(self.splitter)

        # 状态栏
        self.statusBar().showMessage("就绪 - 双击记录查看详情")

    def create_table(self):
        """创建数据表格"""
        # 定义列
        self.columns = [
            "ID", "院区", "血制品大类", "血制品亚类",
            "血型", "数量", "预约时间"
        ]

        # 列宽
        self.column_widths = [60, 120, 120, 150, 80, 80, 200]

        # 创建表格
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)

        # 设置表格属性
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # 设置列宽
        for i, width in enumerate(self.column_widths):
            self.table.setColumnWidth(i, width)

        # 让表格填充可用空间 (PySide6兼容方式)
        # 方式1: 最后一列填充
        self.table.horizontalHeader().setStretchLastSection(True)

        # 方式2: 所有列自动拉伸 (可选)
        # from PySide6.QtWidgets import QHeaderView
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 连接双击事件
        self.table.doubleClicked.connect(self.view_details)

        # 创建分割器
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.table)

    def update_date_filter_options(self):
        """更新日期筛选选项"""
        try:
            if HAS_DB and self.db:
                # 从数据库获取所有日期
                all_data = self.db.get_all_reservations()
                dates = set()

                for record in all_data:
                    # 提取日期部分 (YYYY-MM-DD)
                    if len(record) >= 7:
                        date = record[6][:10]  # reservation_time
                        dates.add(date)

                # 转换为排序后的列表
                sorted_dates = sorted(list(dates))

                # 更新下拉菜单
                current = self.filter_date_combo.currentText()
                self.filter_date_combo.clear()
                self.filter_date_combo.addItem("全部")
                self.filter_date_combo.addItems(sorted_dates)

                # 恢复选择
                index = self.filter_date_combo.findText(current)
                if index >= 0:
                    self.filter_date_combo.setCurrentIndex(index)
            else:
                # 演示模式
                self.filter_date_combo.clear()
                self.filter_date_combo.addItem("全部")
        except Exception as e:
            print(f"更新日期筛选选项失败: {e}")
            self.filter_date_combo.clear()
            self.filter_date_combo.addItem("全部")

    def load_data(self):
        """加载数据"""
        try:
            # 清空表格
            self.table.setRowCount(0)

            if not HAS_DB or not self.db:
                # 演示模式
                demo_data = [
                    ('1', '光谷院区', '红细胞', '悬浮红细胞', 'A型', '1.0', '2024-11-11 10:30:00'),
                    ('2', '中法院区', '血小板', '单采血小板', 'B型', '5.0', '2024-11-11 11:00:00'),
                    ('3', '军山院区', '新鲜冰冻血浆', '', 'O型', '3.0', '2024-11-11 14:30:00'),
                ]
                data = demo_data
            else:
                # 从数据库获取数据
                data = self.db.get_all_reservations()

            # 插入数据
            for record in data:
                # 解包记录
                if len(record) == 7:
                    res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record
                else:
                    continue

                # 处理亚类
                if not subtype or subtype == '':
                    subtype = '无'

                # 根据血制品类型显示不同的单位
                if product_type == "新鲜冰冻血浆":
                    quantity_display = f"{quantity} ml"
                else:
                    quantity_display = f"{quantity} 单位"

                # 插入行
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                # 添加数据
                items = [
                    QTableWidgetItem(str(res_id)),
                    QTableWidgetItem(campus),
                    QTableWidgetItem(product_type),
                    QTableWidgetItem(subtype),
                    QTableWidgetItem(blood_type),
                    QTableWidgetItem(quantity_display),
                    QTableWidgetItem(reservation_time)
                ]

                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_position, col, item)

            # 更新统计信息
            self.stats_label.setText(f"总记录数: {self.table.rowCount()}")

            # 更新状态栏
            self.statusBar().showMessage(f"已加载 {self.table.rowCount()} 条记录")

            # 更新日期筛选选项
            self.update_date_filter_options()

        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"加载数据失败：\n{str(e)}\n\n请检查数据库文件或联系管理员"
            )
            self.statusBar().showMessage(f"加载数据失败: {str(e)[:50]}...", Qt.red)

    def filter_by_date(self, filter_text):
        """按日期筛选数据"""
        filter_text = filter_text.strip()

        # 如果选择"全部"，显示所有记录
        if filter_text == "" or filter_text == "全部":
            self.load_data()
            return

        try:
            # 验证日期格式
            if len(filter_text) < 10:
                QMessageBox.warning(self, "警告", "请选择有效的日期")
                return

            # 清空表格
            self.table.setRowCount(0)

            if not HAS_DB or not self.db:
                # 演示模式：显示所有记录
                self.load_data()
                return

            # 从数据库获取数据
            all_data = self.db.get_all_reservations()

            # 按日期筛选
            filtered_data = []
            for record in all_data:
                if len(record) >= 7:
                    date = record[6][:10]  # reservation_time
                    if date == filter_text:
                        filtered_data.append(record)

            # 插入筛选后的数据
            for record in filtered_data:
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record

                if not subtype or subtype == '':
                    subtype = '无'

                if product_type == "新鲜冰冻血浆":
                    quantity_display = f"{quantity} ml"
                else:
                    quantity_display = f"{quantity} 单位"

                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                items = [
                    QTableWidgetItem(str(res_id)),
                    QTableWidgetItem(campus),
                    QTableWidgetItem(product_type),
                    QTableWidgetItem(subtype),
                    QTableWidgetItem(blood_type),
                    QTableWidgetItem(quantity_display),
                    QTableWidgetItem(reservation_time)
                ]

                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_position, col, item)

            # 更新统计信息
            self.stats_label.setText(f"筛选日期: {filter_text} | 记录数: {len(filtered_data)}")
            self.statusBar().showMessage(f"已加载 {len(filtered_data)} 条记录 (日期筛选: {filter_text})")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"筛选失败：{str(e)}")
            self.statusBar().showMessage(f"筛选失败: {str(e)[:50]}...", Qt.red)

    def view_details(self):
        """双击查看详情"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条记录！")
            return

        # 获取数据
        values = []
        for col in range(self.table.columnCount()):
            item = self.table.item(current_row, col)
            values.append(item.text() if item else "")

        # 显示详情对话框
        self.show_details_dialog(values)

    def show_details_dialog(self, values):
        """显示详情对话框"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle(f"预约详情 - ID: {values[0]}")
        dialog.setMinimumSize(500, 400)
        dialog.setFont(QFont("Microsoft YaHei", 10))

        # 布局
        layout = QVBoxLayout(dialog)

        # 标题
        title = QLabel("预约记录详情")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title.setFont(title_font)
        title.setFixedHeight(50)
        layout.addWidget(title)

        # 详情信息
        grid_layout = QGridLayout()

        details = [
            ("预约编号", values[0]),
            ("院区", values[1]),
            ("血制品大类", values[2]),
            ("血制品亚类", values[3]),
            ("血型", values[4]),
            ("预约数量", values[5]),
            ("预约时间", values[6]),
        ]

        for i, (label, value) in enumerate(details):
            grid_layout.addWidget(QLabel(f"{label}:"), i, 0)
            grid_layout.addWidget(QLabel(value), i, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        # 按钮
        button_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()

    def print_all(self):
        """导出汇总记录为PDF"""
        if not HAS_DB or not self.db:
            QMessageBox.information(self, "提示", "演示模式：PDF输出功能不可用")
            return

        try:
            from utils.printer import BloodReservationPrinter
            printer = BloodReservationPrinter()
            reservations = self.db.get_all_reservations()

            if not reservations:
                QMessageBox.warning(self, "警告", "没有预约记录可输出！")
                return

            # 选择保存路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"预约记录汇总_{timestamp}.pdf"

            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "保存预约记录汇总为PDF",
                default_name,
                "PDF files (*.pdf)"
            )

            if output_file:
                printer.print_all_reservations(reservations, output_file)
                QMessageBox.information(self, "成功", f"汇总PDF已生成并保存到：\n{output_file}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"PDF输出失败：{str(e)}")

    def export_data(self):
        """导出数据（Excel/CSV）"""
        if not HAS_EXPORTER:
            QMessageBox.critical(self, "错误", "导出模块未正确加载！\n\n请检查 utils/exporter.py 文件")
            return

        try:
            # 获取当前显示的数据
            data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    value = item.text() if item else ""

                    # 处理数量字段（去掉单位）
                    if col == 5:  # 数量列
                        if value.endswith(' ml') or value.endswith(' 单位'):
                            value = value[:-3]
                    row_data.append(value)
                data.append(tuple(row_data))

            if not data:
                QMessageBox.warning(self, "警告", "没有数据可导出！")
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
            from utils.exporter import DataExporter
            exporter = DataExporter(self)
            success = exporter.export_data(data, file_format)

            if success:
                self.statusBar().showMessage(f"数据已导出为 {file_format.upper()} 格式")

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

    def on_closing(self, event):
        """窗口关闭事件"""
        event.accept()
        if self.parent:
            self.parent.show()  # 显示父窗口
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
