from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QRadioButton, QLabel, QPushButton, QMessageBox, QFormLayout,
    QButtonGroup, QGroupBox, QDateTimeEdit, QFrame
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
from database.db_manager import BloodReservationDB
from utils.printer import BloodReservationPrinter
import os

class MainWindow(QMainWindow):
    """血制品预约系统主窗口"""

    def __init__(self):
        super().__init__()
        self.db = BloodReservationDB()
        self.printer = BloodReservationPrinter()
        self.current_reservation_id = None
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("血制品预约登记系统 v1.0")
        self.setMinimumSize(600, 500)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("血制品预约登记")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Microsoft YaHei", 20, QFont.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)

        # 创建表单组
        form_group = QGroupBox("预约信息")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setHorizontalSpacing(20)

        # 院区选择
        self.campus_combo = QComboBox()
        self.campus_combo.addItems([
            "请选择院区",
            "光谷院区",
            "中法院区",
            "军山院区"
        ])
        form_layout.addRow("院区：", self.campus_combo)

        # 血制品大类选择
        self.product_type_combo = QComboBox()
        self.product_type_combo.addItems([
            "请选择血制品大类",
            "红细胞",
            "血小板",
            "新鲜冰冻血浆"
        ])
        self.product_type_combo.currentTextChanged.connect(self.on_product_type_changed)
        form_layout.addRow("血制品大类：", self.product_type_combo)

        # 血制品亚类选择
        self.product_subtype_combo = QComboBox()
        self.product_subtype_combo.addItems(["请选择血制品亚类"])
        self.product_subtype_combo.setEnabled(False)
        form_layout.addRow("血制品亚类：", self.product_subtype_combo)

        # 血型选择
        blood_type_layout = QHBoxLayout()
        self.blood_type_group = QButtonGroup()
        blood_types = ["A型", "B型", "O型", "AB型"]
        for blood_type in blood_types:
            radio = QRadioButton(blood_type)
            self.blood_type_group.addButton(radio, blood_type)
            blood_type_layout.addWidget(radio)
        form_layout.addRow("血型：", blood_type_layout)

        # 预约时间
        self.reservation_time_edit = QDateTimeEdit()
        self.reservation_time_edit.setDateTime(QDateTime.currentDateTime())
        self.reservation_time_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.reservation_time_edit.setEnabled(False)
        form_layout.addRow("预约时间：", self.reservation_time_edit)

        main_layout.addWidget(form_group)

        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.submit_btn = QPushButton("提交预约")
        self.submit_btn.setMinimumHeight(40)
        submit_font = QFont("Microsoft YaHei", 11, QFont.Bold)
        self.submit_btn.setFont(submit_font)
        self.submit_btn.clicked.connect(self.submit_reservation)
        button_layout.addWidget(self.submit_btn)

        self.print_btn = QPushButton("打印预约单")
        self.print_btn.setMinimumHeight(40)
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self.print_reservation)
        button_layout.addWidget(self.print_btn)

        main_layout.addLayout(button_layout)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def on_product_type_changed(self, text):
        """血制品大类改变时的事件处理"""
        self.product_subtype_combo.clear()
        self.product_subtype_combo.setEnabled(True)

        if text == "红细胞":
            self.product_subtype_combo.addItems([
                "请选择血制品亚类",
                "洗涤红细胞",
                "辐照红细胞",
                "悬浮红细胞",
                "少白红细胞",
                "稀有血型红细胞"
            ])
        elif text == "血小板":
            self.product_subtype_combo.addItems([
                "请选择血制品亚类",
                "单采血小板",
                "辐照血小板",
                "少白血小板"
            ])
        elif text == "新鲜冰冻血浆":
            self.product_subtype_combo.setEnabled(False)
            self.product_subtype_combo.addItems(["无亚类"])
        else:
            self.product_subtype_combo.setEnabled(False)
            self.product_subtype_combo.addItems(["请选择血制品亚类"])

    def get_selected_blood_type(self):
        """获取选中的血型"""
        for button in self.blood_type_group.buttons():
            if button.isChecked():
                return button.text()
        return None

    def validate_input(self):
        """验证输入信息"""
        if self.campus_combo.currentText() == "请选择院区":
            QMessageBox.warning(self, "输入错误", "请选择院区！")
            return False

        if self.product_type_combo.currentText() == "请选择血制品大类":
            QMessageBox.warning(self, "输入错误", "请选择血制品大类！")
            return False

        if self.product_subtype_combo.isEnabled():
            if self.product_subtype_combo.currentText() in ["请选择血制品亚类", ""]:
                QMessageBox.warning(self, "输入错误", "请选择血制品亚类！")
                return False

        if not self.get_selected_blood_type():
            QMessageBox.warning(self, "输入错误", "请选择血型！")
            return False

        return True

    def submit_reservation(self):
        """提交预约"""
        if not self.validate_input():
            return

        # 获取输入数据
        campus = self.campus_combo.currentText()
        product_type = self.product_type_combo.currentText()
        product_subtype = self.product_subtype_combo.currentText() if self.product_subtype_combo.isEnabled() else ""
        blood_type = self.get_selected_blood_type()
        reservation_time = self.reservation_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")

        # 保存到数据库
        try:
            self.db.add_reservation(campus, product_type, product_subtype, blood_type, reservation_time)
            self.current_reservation_id = self.db.get_all_reservations()[0][0]  # 获取最新插入的ID

            QMessageBox.information(
                self,
                "提交成功",
                f"预约信息已成功保存！\n\n"
                f"院区：{campus}\n"
                f"血制品：{product_type}\n"
                f"亚类：{product_subtype if product_subtype else '无'}\n"
                f"血型：{blood_type}\n"
                f"预约时间：{reservation_time}"
            )

            self.print_btn.setEnabled(True)
            self.statusBar().showMessage("预约已提交", 5000)

        except Exception as e:
            QMessageBox.critical(self, "提交失败", f"保存预约信息时出错：{str(e)}")

    def print_reservation(self):
        """打印预约单"""
        if not self.current_reservation_id:
            QMessageBox.warning(self, "打印错误", "没有可打印的预约记录！")
            return

        try:
            # 获取最新预约记录
            reservation = self.db.get_reservation_by_id(self.current_reservation_id)
            if not reservation:
                QMessageBox.warning(self, "打印错误", "未找到预约记录！")
                return

            # 生成PDF文件
            output_file = self.printer.print_reservation(reservation)

            QMessageBox.information(
                self,
                "打印成功",
                f"预约单已生成：{output_file}\n\n"
                f"请使用PDF阅读器打开文件并打印。"
            )

            self.statusBar().showMessage(f"已生成PDF：{output_file}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "打印失败", f"生成打印文件时出错：{str(e)}")
