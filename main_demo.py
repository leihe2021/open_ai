#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
血制品预约登记系统 - 演示版本
使用标准库tkinter，无需额外安装GUI库
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import BloodReservationDB
    from utils.printer import BloodReservationPrinter
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False

try:
    from gui.reservation_list_window import ReservationListWindow
    HAS_LIST_WINDOW = True
except ImportError:
    HAS_LIST_WINDOW = False


class BloodReservationSystem:
    """血制品预约系统主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("血制品预约登记系统 v1.0 (演示版)")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 初始化数据库（如果模块可用）
        if HAS_MODULES:
            self.db = BloodReservationDB()
            self.printer = BloodReservationPrinter()
        else:
            self.db = None
            self.printer = None

        self.current_reservation_id = None

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """设置界面"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(fill=tk.X, pady=0)

        title_label = tk.Label(
            title_frame,
            text="血制品预约登记系统",
            font=('Microsoft YaHei', 18, 'bold'),
            bg='#2c3e50',
            fg='white',
            pady=15
        )
        title_label.pack()

        # 主要内容区域
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 院区选择
        campus_frame = tk.Frame(main_frame)
        campus_frame.pack(fill=tk.X, pady=10)
        tk.Label(campus_frame, text="院区：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        self.campus_var = tk.StringVar()
        self.campus_combo = ttk.Combobox(campus_frame, textvariable=self.campus_var, width=30)
        self.campus_combo['values'] = ("光谷院区", "中法院区", "军山院区")
        self.campus_combo.pack(side=tk.LEFT, padx=10)

        # 血制品大类
        type_frame = tk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=10)
        tk.Label(type_frame, text="血制品大类：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        self.product_type_var = tk.StringVar()
        self.product_type_combo = ttk.Combobox(type_frame, textvariable=self.product_type_var, width=30)
        self.product_type_combo['values'] = ("红细胞", "血小板", "新鲜冰冻血浆")
        self.product_type_combo.pack(side=tk.LEFT, padx=10)
        self.product_type_combo.bind('<<ComboboxSelected>>', self.on_product_type_changed)

        # 血制品亚类
        subtype_frame = tk.Frame(main_frame)
        subtype_frame.pack(fill=tk.X, pady=10)
        tk.Label(subtype_frame, text="血制品亚类：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        self.product_subtype_var = tk.StringVar()
        self.product_subtype_combo = ttk.Combobox(subtype_frame, textvariable=self.product_subtype_var, width=30)
        self.product_subtype_combo.pack(side=tk.LEFT, padx=10)

        # 血型选择
        blood_frame = tk.Frame(main_frame)
        blood_frame.pack(fill=tk.X, pady=10)
        tk.Label(blood_frame, text="血型：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        self.blood_type_var = tk.StringVar()
        blood_types = [("A型", "A型"), ("B型", "B型"), ("O型", "O型"), ("AB型", "AB型")]
        for text, mode in blood_types:
            tk.Radiobutton(
                blood_frame,
                text=text,
                variable=self.blood_type_var,
                value=mode,
                font=('Microsoft YaHei', 10),
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=10)

        # 预约数量
        quantity_frame = tk.Frame(main_frame)
        quantity_frame.pack(fill=tk.X, pady=10)
        tk.Label(quantity_frame, text="预约数量：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar(value="1")
        # 使用Entry而不是Spinbox，支持小数
        self.quantity_entry = tk.Entry(
            quantity_frame,
            textvariable=self.quantity_var,
            width=10,
            font=('Microsoft YaHei', 10),
            justify=tk.CENTER,
            bd=2,
            relief='groove'
        )
        self.quantity_entry.pack(side=tk.LEFT, padx=10)
        self.quantity_unit_label = tk.Label(quantity_frame, text="单位 (支持0.5)", font=('Microsoft YaHei', 9), fg='#7f8c8d')
        self.quantity_unit_label.pack(side=tk.LEFT, padx=5)

        # 预约时间
        time_frame = tk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=10)
        tk.Label(time_frame, text="预约时间：", font=('Microsoft YaHei', 10), width=15).pack(side=tk.LEFT)
        # 延迟获取时间，在提交时再获取当前时间
        self.time_label = tk.Label(
            time_frame,
            text="",
            font=('Microsoft YaHei', 10),
            fg='#34495e'
        )
        self.time_label.pack(side=tk.LEFT, padx=10)
        self.update_reservation_time()

        # 定时更新显示时间
        self.update_time_display()

        # 按钮区域
        button_frame = tk.Frame(main_frame, pady=20)
        button_frame.pack()

        self.submit_btn = tk.Button(
            button_frame,
            text="提交预约",
            font=('Microsoft YaHei', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            height=2,
            cursor='hand2',
            command=self.submit_reservation
        )
        self.submit_btn.pack(side=tk.LEFT, padx=10)

        self.view_btn = tk.Button(
            button_frame,
            text="📋 查看记录",
            font=('Microsoft YaHei', 11, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            height=2,
            cursor='hand2',
            command=self.view_all_reservations
        )
        self.view_btn.pack(side=tk.LEFT, padx=10)

        # 状态栏
        status_frame = tk.Frame(self.root, bg='#ecf0f1', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(
            status_frame,
            text="就绪 - 演示版本（使用tkinter）",
            bg='#ecf0f1',
            fg='#7f8c8d',
            font=('Microsoft YaHei', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

    def update_reservation_time(self):
        """更新预约时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)

    def update_time_display(self):
        """定时更新时间显示（每秒更新一次）"""
        self.update_reservation_time()
        # 每秒更新一次
        self.root.after(1000, self.update_time_display)

    def on_product_type_changed(self, event):
        """血制品大类改变时的事件"""
        product_type = self.product_type_combo.get()

        if product_type == "红细胞":
            subtypes = ["洗涤红细胞", "辐照红细胞", "悬浮红细胞", "少白红细胞", "稀有血型红细胞"]
            # 红细胞和血小板：使用"单位"，支持0.5倍数
            self.quantity_unit_label.config(text="单位 (支持0.5)", fg='#7f8c8d')
            # 启用亚类选择
            self.product_subtype_combo.config(state='readonly')
            self.product_subtype_combo.set("")
        elif product_type == "血小板":
            subtypes = ["单采血小板", "辐照血小板", "少白血小板"]
            # 红细胞和血小板：使用"单位"，支持0.5倍数
            self.quantity_unit_label.config(text="单位 (支持0.5)", fg='#7f8c8d')
            # 启用亚类选择
            self.product_subtype_combo.config(state='readonly')
            self.product_subtype_combo.set("")
        else:  # 新鲜血浆
            subtypes = ["无"]
            # 血浆：使用"ml"，无数量限制
            self.quantity_unit_label.config(text="ml", fg='#27ae60')
            # 禁用亚类选择，自动设置为"无"
            self.product_subtype_combo.config(state='disabled')
            self.product_subtype_combo.set("无")

        self.product_subtype_combo['values'] = subtypes

    def validate_input(self):
        """验证输入"""
        if not self.campus_combo.get():
            messagebox.showerror("错误", "请选择院区！")
            return False

        if not self.product_type_combo.get():
            messagebox.showerror("错误", "请选择血制品大类！")
            return False

        product_type = self.product_type_combo.get()

        # 血浆不需要选择亚类（已自动设为"无"）
        if product_type != "新鲜冰冻血浆":
            if not self.product_subtype_combo.get():
                messagebox.showerror("错误", "请选择血制品亚类！")
                return False

        if not self.blood_type_var.get():
            messagebox.showerror("错误", "请选择血型！")
            return False

        # 验证数量
        try:
            quantity = float(self.quantity_var.get())

            if product_type == "新鲜冰冻血浆":
                # 血浆：数量无限制，只要是正数即可
                if quantity <= 0:
                    messagebox.showerror("错误", "血浆数量必须大于0！")
                    return False
            else:
                # 红细胞和血小板：0.5-100之间，且必须是0.5的倍数
                if quantity < 0.5 or quantity > 100:
                    messagebox.showerror("错误", "预约数量必须在0.5-100之间！")
                    return False
                # 支持0.5的倍数
                if quantity * 2 != int(quantity * 2):
                    messagebox.showerror("错误", "预约数量必须是0.5的倍数！")
                    return False
        except ValueError:
            messagebox.showerror("错误", "预约数量必须是数字！")
            return False

        return True

    def submit_reservation(self):
        """提交预约"""
        if not self.validate_input():
            return

        # 获取输入数据
        campus = self.campus_combo.get()
        product_type = self.product_type_combo.get()
        product_subtype = self.product_subtype_combo.get()
        blood_type = self.blood_type_var.get()
        quantity = float(self.quantity_var.get())

        # 实时获取当前时间
        reservation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 如果数据库模块可用，保存到数据库
        if HAS_MODULES:
            try:
                self.db.add_reservation(campus, product_type, product_subtype, blood_type, quantity, reservation_time)
                self.current_reservation_id = self.db.get_all_reservations()[0][0]

                # 询问是否查看记录汇总
                result = messagebox.askyesno(
                    "成功",
                    f"预约信息已成功保存！\n\n"
                    f"院区：{campus}\n"
                    f"血制品：{product_type}\n"
                    f"亚类：{product_subtype}\n"
                    f"血型：{blood_type}\n"
                    f"数量：{quantity}\n"
                    f"时间：{reservation_time}\n\n"
                    f"提交预约成功！是否查看记录汇总？"
                )

                # 根据用户选择决定是否跳转到汇总界面
                if result:
                    # 隐藏主窗口，打开记录窗口
                    self.root.withdraw()
                    list_window = ReservationListWindow(self.root, db_instance=self.db)
                else:
                    # 用户选择"否"，停留在当前界面，可以继续预约
                    pass

                self.status_label.config(text="预约已提交", fg='#27ae60')
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
        else:
            # 演示模式，只显示信息
            result = messagebox.askyesno(
                "演示模式",
                f"模拟预约提交成功！\n\n"
                f"院区：{campus}\n"
                f"血制品：{product_type}\n"
                f"亚类：{product_subtype}\n"
                f"血型：{blood_type}\n"
                f"数量：{quantity}\n"
                f"时间：{reservation_time}\n\n"
                f"注：当前为演示模式，未连接数据库\n\n"
                f"提交预约成功！是否查看记录汇总？"
            )

            # 打开演示记录窗口
            if result and HAS_LIST_WINDOW:
                # 隐藏主窗口，打开记录窗口
                self.root.withdraw()
                list_window = ReservationListWindow(self.root, db_instance=self.db if HAS_MODULES else None)
            elif result:
                messagebox.showinfo("提示", "记录汇总功能不可用")

            self.status_label.config(text="演示模式 - 模拟提交成功", fg='#f39c12')

    def view_all_reservations(self):
        """查看所有预约记录"""
        if HAS_LIST_WINDOW:
            # 隐藏主窗口，打开记录窗口
            self.root.withdraw()
            list_window = ReservationListWindow(self.root, db_instance=self.db if HAS_MODULES else None)
        else:
            messagebox.showinfo("提示", "记录汇总功能不可用")



def main():
    """主函数"""
    root = tk.Tk()
    app = BloodReservationSystem(root)

    # 添加关于信息
    def show_about():
        messagebox.showinfo(
            "关于",
            "血制品预约登记系统 v1.0\n"
            "演示版本\n\n"
            "本版本使用Python标准库tkinter开发\n"
            "完整版本使用PySide6提供更丰富的界面\n\n"
            "开发者: Claude AI\n"
            "日期: 2024-11-11"
        )

    menubar = tk.Menu(root)
    root.config(menu=menubar)
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="帮助", menu=help_menu)
    help_menu.add_command(label="关于", command=show_about)

    root.mainloop()


if __name__ == "__main__":
    main()
