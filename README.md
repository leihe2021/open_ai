# 血制品预约登记系统 v1.1

## 项目简介
血制品预约登记系统是专为医院分院设计的血制品预约管理工具，支持院区选择、血制品预约、血型登记等功能。

## 主要功能
- ✅ 院区选择（光谷院区、中法院区、军山院区）
- ✅ 血制品预约（红细胞、血小板、新鲜冰冻血浆）
- ✅ 血型选择（A型、B型、O型、AB型）
- ✅ 自动记录预约时间
- ✅ SQLite本地数据库存储
- ✅ PDF打印功能
- ✅ 中文界面，操作简便

## 系统要求
- Windows 10 及以上操作系统
- 无需安装 Python 环境（打包后）

## 安装说明

### 开发环境安装
1. 安装 Python 3.8+ 和 pip
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```

### 生产环境打包
1. Windows 系统运行：
   ```bash
   build.bat
   ```
2. Linux/Mac 系统运行：
   ```bash
   chmod +x build.sh
   ./build.sh
   ```
3. 打包完成后，可执行文件位于 `dist/` 目录

## 使用说明
1. 选择院区（下拉菜单）
2. 选择血制品大类（红细胞/血小板/新鲜冰冻血浆）
3. 根据大类选择血制品亚类（新鲜冰冻血浆无亚类）
4. 选择血型（单选按钮）
5. 系统自动记录当前时间
6. 点击"提交预约"保存信息
7. 点击"打印预约单"生成PDF文件

## 数据存储
- 所有预约记录保存在 `records.db`（SQLite数据库）
- 数据库文件与可执行文件在同一目录
- 可使用 SQLite 管理工具（如 SQLiteBrowser）查看数据

## 目录结构
```
预约血online/
├── main.py                 # 主程序入口
├── build.spec              # PyInstaller 配置
├── requirements.txt        # 依赖包列表
├── build.bat              # Windows 打包脚本
├── build.sh               # Linux/Mac 打包脚本
├── README.md              # 说明文档
├── gui/                   # 图形界面模块
│   ├── main_window.py
│   └── reservation_list_window.py
├── database/              # 数据库模块
│   └── db_manager.py
└── utils/                 # 工具模块
    └── printer.py
```

## 技术栈
- **GUI 框架**: PySide6
- **数据库**: SQLite
- **PDF 生成**: ReportLab
- **打包工具**: PyInstaller

## 版本历史
- v1.1 (2025-11-13)
  - 新增数据导出功能（Excel/CSV）
  - 在预约列表窗口添加"导出数据"按钮
  - 支持按日期筛选导出
  - 新增"查看所有预约"按钮
  - 升级依赖：添加 openpyxl 库

- v1.0 (2024-11-11)
  - 初始版本发布
  - 实现基本预约登记功能
  - 支持打印和数据库存储

## 联系方式
如有问题或建议，请联系医院信息科。

## 许可证
本软件仅供医院内部使用。