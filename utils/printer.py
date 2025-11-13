from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import os
from datetime import datetime

class BloodReservationPrinter:
    """血制品预约打印类"""

    def __init__(self):
        """初始化打印配置"""
        self.styles = getSampleStyleSheet()
        self.setup_fonts()

    def setup_fonts(self):
        """设置中文字体"""
        # 中文字体文件路径（相对于当前目录）
        font_paths = [
            'fonts/NotoSansCJK-Regular.ttc',
            'fonts/NotoSansCJKsc-Regular.otf',
            'fonts/simsun.ttc',
            'fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            '/System/Library/Fonts/PingFang.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        ]

        font_registered = False
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    # 使用字体文件名（不包含路径）作为字体名
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.styles['Normal'].fontName = font_name
                    self.chinese_font = font_name
                    font_registered = True
                    print(f"[INFO] 已注册中文字体: {font_path}")
                    break
            except Exception as e:
                print(f"[WARN] 字体注册失败 {font_path}: {e}")
                continue

        if not font_registered:
            # 如果没有找到字体文件，使用默认字体
            self.chinese_font = 'Helvetica'
            print("[WARN] 未找到中文字体文件，使用默认字体 (中文可能显示异常)")

        # 创建自定义样式（独立样式对象，不添加到样式表）
        self.chinese_style = ParagraphStyle(
            'ChineseStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            leading=14
        )

    def print_reservation(self, reservation_data, output_file=None):
        """
        打印预约记录

        Args:
            reservation_data: 包含预约信息的字典或元组
            output_file: 输出文件路径（可选）
        """
        if isinstance(reservation_data, (list, tuple)):
            # 如果是元组/列表格式
            # 当前版本是7个字段（已删除created_at）
            if len(reservation_data) == 7:
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = reservation_data
            elif len(reservation_data) == 8:
                # 旧版本包含created_at，跳过最后一个字段
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time, created_at = reservation_data
            else:
                # 旧版本不包含quantity
                res_id, campus, product_type, subtype, blood_type, reservation_time = reservation_data
                quantity = 1
        else:
            # 如果是字典格式
            campus = reservation_data.get('campus', '')
            product_type = reservation_data.get('product_type', '')
            subtype = reservation_data.get('subtype', '')
            blood_type = reservation_data.get('blood_type', '')
            quantity = reservation_data.get('quantity', 1)
            reservation_time = reservation_data.get('reservation_time', '')

        # 如果没有提供输出文件，生成默认文件名
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"blood_reservation_{timestamp}.pdf"

        # 创建PDF文档
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)

        # 构建文档内容
        story = []

        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 居中
        )
        title = Paragraph("血制品预约登记单", title_style)
        story.append(title)

        # 预约信息表格
        data = [
            ['项目', '内容'],
            ['预约编号', str(res_id) if isinstance(reservation_data, (list, tuple)) else 'N/A'],
            ['院区', campus],
            ['血制品大类', product_type],
            ['血制品亚类', subtype if subtype else '无'],
            ['血型', blood_type],
            ['预约数量', str(quantity)],
            ['预约时间', reservation_time],
        ]

        # 使用Paragraph包装表格数据以支持中文
        for i, row in enumerate(data):
            data[i] = [Paragraph(str(cell), self.chinese_style) for cell in row]

        # 创建表格
        table = Table(data, colWidths=[4*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 2*cm))

        # 打印时间
        print_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"打印时间: {print_time}", self.styles['Normal']))

        # 生成PDF
        doc.build(story)

        return output_file

    def print_all_reservations(self, reservations_list, output_file=None):
        """
        打印所有预约记录

        Args:
            reservations_list: 预约记录列表
            output_file: 输出文件路径（可选）
        """
        if not reservations_list:
            print("没有预约记录可打印")
            return None

        # 如果没有提供输出文件，生成默认文件名
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"all_reservations_{timestamp}.pdf"

        # 创建PDF文档
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                              rightMargin=1*cm, leftMargin=1*cm,
                              topMargin=1*cm, bottomMargin=1*cm)

        # 构建文档内容
        story = []

        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 居中
        )
        title = Paragraph("血制品预约记录汇总", title_style)
        story.append(title)

        # 表头
        headers = ['预约编号', '院区', '血制品大类', '血制品亚类', '血型', '数量', '预约时间']
        data = [[Paragraph(header, self.chinese_style) for header in headers]]

        # 添加数据行
        for res in reservations_list:
            # 当前版本是7个字段（已删除created_at）
            # res: (id, hospital_campus, blood_product_type, blood_product_subtype, blood_type, quantity, reservation_time)
            if len(res) == 7:
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time = res
            elif len(res) == 8:
                # 旧版本包含created_at，跳过最后一个字段
                res_id, campus, product_type, subtype, blood_type, quantity, reservation_time, created_at = res
            else:
                # 旧版本不包含quantity
                res_id, campus, product_type, subtype, blood_type, reservation_time = res
                quantity = 1

            data.append([
                Paragraph(str(res_id), self.chinese_style),
                Paragraph(campus, self.chinese_style),
                Paragraph(product_type, self.chinese_style),
                Paragraph(subtype if subtype else '无', self.chinese_style),
                Paragraph(blood_type, self.chinese_style),
                Paragraph(str(quantity), self.chinese_style),
                Paragraph(reservation_time, self.chinese_style)
            ])

        # 创建表格
        table = Table(data, colWidths=[1.5*cm, 2*cm, 2*cm, 2*cm, 1.5*cm, 1*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)

        # 打印时间
        print_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"打印时间: {print_time}", self.styles['Normal']))
        story.append(Paragraph(f"总记录数: {len(reservations_list)}", self.styles['Normal']))

        # 生成PDF
        doc.build(story)

        return output_file
