#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预约记录列表窗口
显示所有预约记录的汇总界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import BloodReservationDB
    HAS_DB = True
except ImportError:
    HAS_DB = False


class ReservationListWindow:
    """预约记录列表窗口"""

    def __init__(self, parent=None, db_instance=None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("预约记录汇总 - 血制品预约登记系统")
        self.window.geometry("1000x600")
        self.window.resizable(True, True)

        # 居中窗口
        self.center_window()

        # 初始化数据库
        # 如果提供了db实例，使用它；否则创建新的
        if HAS_DB:
            if db_instance:
                self.db = db_instance
            else:
                self.db = BloodReservationDB()
        else:
            self.db = None

        # 创建界面
        self.setup_ui()

        # 加载数据
        self.load_data()

        # 设置关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """窗口居中"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """设置界面"""
        # 标题
        title_frame = tk.Frame(self.window, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="预约记录汇总",
            font=('Microsoft YaHei', 18, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)

        # 工具栏
        toolbar_frame = tk.Frame(self.window, bg='#ecf0f1', height=50)
        toolbar_frame.pack(fill=tk.X, pady=0)
        toolbar_frame.pack_propagate(False)

        # 日期筛选
        date_frame = tk.Frame(toolbar_frame, bg='#ecf0f1')
        date_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(
            date_frame,
            text="筛选日期:",
            font=('Microsoft YaHei', 10),
            bg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)

        self.filter_date_var = tk.StringVar()
        self.filter_date_combo = ttk.Combobox(
            date_frame,
            textvariable=self.filter_date_var,
            width=12,
            font=('Microsoft YaHei', 10),
            state='readonly'
        )
        self.filter_date_combo.pack(side=tk.LEFT, padx=5)
        # 设置默认选项
        self.filter_date_combo['values'] = ("全部",)
        self.filter_date_combo.set("全部")
        # 绑定选择事件触发筛选
        self.filter_date_combo.bind('<<ComboboxSelected>>', self.filter_by_date)

        filter_btn = tk.Button(
            date_frame,
            text="筛选",
            font=('Microsoft YaHei', 9),
            command=self.filter_by_date,
            bg='#8e44ad',
            fg='white',
            cursor='hand2'
        )
        filter_btn.pack(side=tk.LEFT, padx=5)

        # 刷新按钮
        refresh_btn = tk.Button(
            toolbar_frame,
            text="🔄 刷新",
            font=('Microsoft YaHei', 10),
            command=self.load_data,
            bg='#3498db',
            fg='white',
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # PDF输出按钮
        pdf_btn = tk.Button(
            toolbar_frame,
            text="📄 汇总输出为PDF",
            font=('Microsoft YaHei', 10),
            command=self.print_all,
            bg='#27ae60',
            fg='white',
            cursor='hand2'
        )
        pdf_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # 清空按钮
        clear_btn = tk.Button(
            toolbar_frame,
            text="🗑️ 清空所有",
            font=('Microsoft YaHei', 10),
            command=self.clear_all,
            bg='#e74c3c',
            fg='white',
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # 统计信息标签
        self.stats_label = tk.Label(
            toolbar_frame,
            text="",
            font=('Microsoft YaHei', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # 创建树形视图
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 定义列
        columns = ('ID', '院区', '血制品大类', '血制品亚类', '血型', '数量', '预约时间')

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # 设置列标题和宽度
        column_widths = {
            'ID': 60,
            '院区': 120,
            '血制品大类': 120,
            '血制品亚类': 150,
            '血型': 80,
            '数量': 80,
            '预约时间': 200
        }

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # 双击事件
        self.tree.bind('<Double-1>', self.on_item_double_click)

        # 右键菜单
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label='查看详情', command=self.view_details)
        self.context_menu.add_command(label='打印单据', command=self.print_single)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='删除记录', command=self.delete_record)

        self.tree.bind('<Button-3>', self.show_context_menu)

        # 状态栏
        status_frame = tk.Frame(self.window, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="就绪 - 双击记录查看详情，右键查看更多操作",
            bg='#34495e',
            fg='white',
            font=('Microsoft YaHei', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

    def update_date_filter_options(self):
        """更新日期筛选下拉菜单选项"""
        try:
            dates = set()

            if HAS_DB and self.db:
                # 从数据库获取所有日期
                all_data = self.db.get_all_reservations()
                for record in all_data:
                    # 提取日期部分 (YYYY-MM-DD)
                    date = record[6][:10]
                    dates.add(date)
            else:
                # 演示模式：添加示例日期
                dates.add("2024-11-11")

            # 转换为排序后的列表
            sorted_dates = sorted(list(dates))

            # 更新下拉菜单选项
            self.filter_date_combo['values'] = ("全部",) + tuple(sorted_dates)

            # 如果当前选择不在新选项中，重置为"全部"
            current = self.filter_date_var.get()
            if current not in self.filter_date_combo['values']:
                self.filter_date_combo.set("全部")
        except Exception as e:
            # 如果获取日期失败，使用默认选项
            self.filter_date_combo['values'] = ("全部",)
            self.filter_date_combo.set("全部")

    def filter_by_date(self, event=None):
        """按日期筛选预约记录"""
        filter_text = self.filter_date_var.get().strip()

        # 如果输入"全部"或空，显示所有记录
        if filter_text == "" or filter_text.lower() == "全部":
            self.load_data()
            return

        # 验证日期格式
        if len(filter_text) < 10:
            messagebox.showwarning("警告", "请输入完整的日期 (YYYY-MM-DD)\n例如: 2024-11-11")
            return

        try:
            # 提取日期部分 (YYYY-MM-DD)
            filter_date = filter_text[:10]

            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not HAS_DB or not self.db:
                # 演示模式：显示所有记录
                demo_data = [
                    ('1', '光谷院区', '红细胞', '悬浮红细胞', 'A型', '1', '2024-11-11 10:30:00'),
                    ('2', '中法院区', '血小板', '单采血小板', 'B型', '5', '2024-11-11 11:00:00'),
                    ('3', '军山院区', '新鲜冰冻血浆', '无', 'O型', '3', '2024-11-11 14:30:00'),
                ]
                data = demo_data
            else:
                # 从数据库获取数据
                all_data = self.db.get_all_reservations()
                # 按日期筛选
                data = [record for record in all_data if record[6][:10] == filter_date]

            # 插入数据
            total_quantity = 0
            campus_counts = {}

            for record in data:
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record

                if not subtype or subtype == '':
                    subtype = '无'

                # 根据血制品类型显示不同的单位
                if product_type == "新鲜冰冻血浆":
                    quantity_display = f"{quantity} ml"
                else:
                    quantity_display = f"{quantity} 单位"

                item_id = self.tree.insert('', tk.END, values=(
                    res_id, campus, product_type, subtype, blood_type,
                    quantity_display, reservation_time
                ))

                total_quantity += int(quantity) if isinstance(quantity, int) else 1
                campus_counts[campus] = campus_counts.get(campus, 0) + 1

            # 更新统计信息
            stats_text = f"筛选日期: {filter_date} | 记录数: {len(data)}"
            self.stats_label.config(text=stats_text)

            # 更新状态栏
            self.status_label.config(text=f"已加载 {len(data)} 条记录 (日期筛选: {filter_date})")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messagebox.showerror(
                "错误",
                f"筛选失败：\n{str(e)}\n\n"
                f"详细信息：\n{error_detail}"
            )

    def load_data(self):
        """加载数据"""
        try:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not HAS_DB or not self.db:
                # 演示模式
                demo_data = [
                    ('1', '光谷院区', '红细胞', '悬浮红细胞', 'A型', '1', '2024-11-11 10:30:00'),
                    ('2', '中法院区', '血小板', '单采血小板', 'B型', '5', '2024-11-11 11:00:00'),
                    ('3', '军山院区', '新鲜冰冻血浆', '无', 'O型', '3', '2024-11-11 14:30:00'),
                ]
                data = demo_data
            else:
                # 从数据库获取数据
                data = self.db.get_all_reservations()

            # 插入数据
            total_quantity = 0
            campus_counts = {}

            for record in data:
                # 统一处理：解包7个字段
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = record

                # 处理亚类
                if not subtype or subtype == '':
                    subtype = '无'

                # 根据血制品类型显示不同的单位
                if product_type == "新鲜冰冻血浆":
                    quantity_display = f"{quantity} ml"
                else:
                    quantity_display = f"{quantity} 单位"

                # 插入到树形视图
                item_id = self.tree.insert('', tk.END, values=(
                    res_id, campus, product_type, subtype, blood_type,
                    quantity_display, reservation_time
                ))

                # 统计
                total_quantity += int(quantity) if isinstance(quantity, int) else 1
                campus_counts[campus] = campus_counts.get(campus, 0) + 1

            # 更新统计信息（只显示记录数）
            stats_text = f"总记录数: {len(data)}"
            self.stats_label.config(text=stats_text)

            # 更新状态栏
            self.status_label.config(text=f"已加载 {len(data)} 条记录")

            # 更新日期筛选下拉菜单选项
            self.update_date_filter_options()

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messagebox.showerror(
                "错误",
                f"加载数据失败：\n{str(e)}\n\n"
                f"详细信息：\n{error_detail}\n\n"
                f"请检查数据库文件或联系管理员"
            )
            # 更新状态栏显示错误
            self.status_label.config(text=f"加载数据失败: {str(e)[:50]}...", fg='#e74c3c')

    def sort_by_column(self, col):
        """按列排序"""
        # 获取所有数据
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]

        # 排序
        try:
            # 尝试数字排序
            items.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else x[0])
        except:
            # 字符串排序
            items.sort()

        # 重新插入
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def on_item_double_click(self, event):
        """双击查看详情"""
        self.view_details()

    def view_details(self):
        """查看选中记录的详情"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条记录！")
            return

        item = selection[0]
        values = self.tree.item(item, 'values')

        # 创建详情窗口
        detail_window = tk.Toplevel(self.window)
        detail_window.title(f"预约详情 - ID: {values[0]}")
        detail_window.geometry("500x400")
        detail_window.resizable(False, False)
        detail_window.transient(self.window)
        detail_window.grab_set()

        # 居中
        detail_window.update_idletasks()
        x = (detail_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (detail_window.winfo_screenheight() // 2) - (400 // 2)
        detail_window.geometry(f'500x400+{x}+{y}')

        # 标题
        title_label = tk.Label(
            detail_window,
            text="预约记录详情",
            font=('Microsoft YaHei', 16, 'bold'),
            bg='#3498db',
            fg='white',
            height=2
        )
        title_label.pack(fill=tk.X, pady=0)

        # 详情信息
        info_frame = tk.Frame(detail_window, padx=30, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True)

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
            # 标签
            label_widget = tk.Label(
                info_frame,
                text=label + "：",
                font=('Microsoft YaHei', 11, 'bold'),
                anchor='w',
                width=15
            )
            label_widget.grid(row=i, column=0, sticky='w', pady=10)

            # 值
            value_widget = tk.Label(
                info_frame,
                text=value,
                font=('Microsoft YaHei', 11),
                anchor='w'
            )
            value_widget.grid(row=i, column=1, sticky='w', padx=10, pady=10)

        # 按钮
        button_frame = tk.Frame(detail_window, pady=20)
        button_frame.pack()

        close_btn = tk.Button(
            button_frame,
            text="关闭",
            font=('Microsoft YaHei', 10),
            command=detail_window.destroy,
            bg='#95a5a6',
            fg='white',
            width=10,
            cursor='hand2'
        )
        close_btn.pack(side=tk.LEFT, padx=5)

        print_btn = tk.Button(
            button_frame,
            text="打印此单据",
            font=('Microsoft YaHei', 10),
            command=lambda: self.print_specific(values[0]),
            bg='#27ae60',
            fg='white',
            width=12,
            cursor='hand2'
        )
        print_btn.pack(side=tk.LEFT, padx=5)

    def print_single(self):
        """打印选中的单条记录"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条记录！")
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        self.print_specific(values[0])

    def print_specific(self, res_id):
        """打印特定ID的记录"""
        messagebox.showinfo("提示", f"将在完整版本中实现打印ID={res_id}的预约单")

    def print_all(self):
        """导出汇总记录为PDF"""
        if not HAS_DB or not self.db:
            messagebox.showinfo("提示", "演示模式：PDF输出功能不可用")
            return

        try:
            from utils.printer import BloodReservationPrinter
            printer = BloodReservationPrinter()
            reservations = self.db.get_all_reservations()

            if not reservations:
                messagebox.showwarning("警告", "没有预约记录可输出！")
                return

            import tkinter.filedialog as filedialog
            output_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="保存预约记录汇总为PDF"
            )

            if output_file:
                printer.print_all_reservations(reservations, output_file)
                messagebox.showinfo("成功", f"汇总PDF已生成并保存到：\n{output_file}")
        except Exception as e:
            messagebox.showerror("错误", f"PDF输出失败：{str(e)}")

    def delete_record(self):
        """删除选中的记录"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条记录！")
            return

        item = selection[0]
        values = self.tree.item(item, 'values')

        # 确认删除
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除这条预约记录吗？\n\n"
            f"ID: {values[0]}\n"
            f"院区: {values[1]}\n"
            f"血制品: {values[2]}\n"
            f"血型: {values[4]}"
        )

        if result:
            try:
                affected_rows = self.db.delete_reservation(values[0])
                self.load_data()
                messagebox.showinfo("成功", f"记录 ID={values[0]} 已删除 (影响行数: {affected_rows})")
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                messagebox.showerror("错误", f"删除失败：\n{str(e)}\n\n详细信息：\n{error_detail}")

    def clear_all(self):
        """清空所有记录"""
        if not HAS_DB or not self.db:
            messagebox.showinfo("提示", "演示模式：清空功能不可用")
            return

        result = messagebox.askyesno(
            "确认清空",
            "确定要清空所有预约记录吗？\n\n此操作不可恢复！"
        )

        if result:
            try:
                # 使用数据库类的方法来清空
                affected_rows = self.db.clear_all_reservations()
                self.load_data()
                messagebox.showinfo("成功", f"所有记录已清空 (共删除 {affected_rows} 条)")
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                messagebox.showerror("错误", f"清空失败：\n{str(e)}\n\n详细信息：\n{error_detail}")

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_closing(self):
        """窗口关闭事件"""
        self.window.destroy()
        if self.parent:
            self.parent.deiconify()  # 恢复父窗口


def main():
    """测试函数"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = ReservationListWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
