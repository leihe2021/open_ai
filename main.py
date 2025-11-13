import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from gui.main_window import MainWindow

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("血制品预约登记系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("医院信息科")

    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 启动事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
