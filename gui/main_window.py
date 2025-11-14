from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QRadioButton, QLabel, QPushButton, QMessageBox, QFormLayout,
    QButtonGroup, QGroupBox, QDateTimeEdit, QFrame, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDateTime, QSize
from PySide6.QtGui import QFont
from database.db_manager import BloodReservationDB
from utils.printer import BloodReservationPrinter
import os

class MainWindow(QMainWindow):
    """血制品预约系统主窗口"""

    def __init__(self):
        super().__init__()
        self.db = BloodReservationDB()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("血制品预约登记系统 v1.2 - UI Enhanced")
        self.setMinimumSize(700, 600)

        # 应用全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1976D2;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: white;
                color: #1976D2;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 200px;
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
            QRadioButton {
                font-size: 13px;
                color: #333333;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid #d0d0d0;
                border-radius: 9px;
                background-color: white;
            }
            QRadioButton::indicator::checked {
                border: 2px solid #2196F3;
                border-radius: 9px;
                background-color: #2196F3;
            }
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QDoubleSpinBox:hover {
                border-color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#submit_btn {
                background-color: #4CAF50;
            }
            QPushButton#submit_btn:hover {
                background-color: #388E3C;
            }
            QPushButton#view_all_btn {
                background-color: #FF9800;
            }
            QPushButton#view_all_btn:hover {
                background-color: #F57C00;
            }
            QDateTimeEdit {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLabel#title_label {
                color: #1976D2;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # 标题
        title_label = QLabel("血制品预约登记")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        title_label.setMinimumHeight(80)
        main_layout.addWidget(title_label)

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
            self.blood_type_group.addButton(radio)  # PySide6 6.9.2: remove second parameter
            blood_type_layout.addWidget(radio)
        form_layout.addRow("血型：", blood_type_layout)

        # 数量输入
        self.quantity_spinbox = QDoubleSpinBox()
        self.quantity_spinbox.setMinimum(0.1)
        self.quantity_spinbox.setMaximum(10000)
        self.quantity_spinbox.setDecimals(1)
        self.quantity_spinbox.setValue(1.0)
        form_layout.addRow("数量：", self.quantity_spinbox)

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
        button_layout.setAlignment(Qt.AlignCenter)

        # 提交预约按钮
        self.submit_btn = QPushButton("✓ 提交预约")
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setMinimumHeight(45)
        self.submit_btn.setMinimumWidth(160)
        self.submit_btn.setIconSize(QSize(20, 20))
        self.submit_btn.clicked.connect(self.submit_reservation)
        button_layout.addWidget(self.submit_btn)

        # 查看所有预约按钮
        self.view_all_btn = QPushButton("📋 查看所有预约")
        self.view_all_btn.setObjectName("view_all_btn")
        self.view_all_btn.setMinimumHeight(45)
        self.view_all_btn.setMinimumWidth(160)
        self.view_all_btn.setIconSize(QSize(20, 20))
        self.view_all_btn.clicked.connect(self.view_all_reservations)
        button_layout.addWidget(self.view_all_btn)

        main_layout.addLayout(button_layout)

        # 状态栏
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #f9f9f9;
                color: #666666;
                border-top: 1px solid #e0e0e0;
                padding: 5px;
                font-size: 12px;
            }
        """)
        self.statusBar().showMessage("就绪 - 请填写预约信息")

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
        quantity = self.quantity_spinbox.value()  # 获取数量
        reservation_time = self.reservation_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")

        # 保存到数据库
        try:
            self.db.add_reservation(campus, product_type, product_subtype, blood_type, quantity, reservation_time)

            # 显示单位
            unit = "ml" if product_type == "新鲜冰冻血浆" else "单位"
            QMessageBox.information(
                self,
                "提交成功",
                f"预约信息已成功保存！\n\n"
                f"院区：{campus}\n"
                f"血制品：{product_type}\n"
                f"亚类：{product_subtype if product_subtype else '无'}\n"
                f"血型：{blood_type}\n"
                f"数量：{quantity} {unit}\n"
                f"预约时间：{reservation_time}"
            )

            self.statusBar().showMessage("预约已提交", 5000)

        except Exception as e:
            QMessageBox.critical(self, "提交失败", f"保存预约信息时出错：{str(e)}")

    def view_all_reservations(self):
        """查看所有预约记录"""
        try:
            from gui.reservation_list_window_simple import ReservationListWindow

            # 创建并显示列表窗口 (不隐藏主窗口，因为是模态对话框)
            self.list_window = ReservationListWindow(parent=self, db_instance=self.db)
            self.list_window.exec()  # 使用exec()显示模态对话框

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开预约记录窗口时出错：{str(e)}")
