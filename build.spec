# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集所有数据文件
datas = []
if os.path.exists('database'):
    datas.append(('database', 'database'))
if os.path.exists('utils'):
    datas.append(('utils', 'utils'))

# 手动添加 PySide6 和 shiboken6 的 DLL 文件
# 查找 conda 环境中 PySide6 的 bin 目录
try:
    import PySide6
    pyside6_path = os.path.dirname(PySide6.__file__)
    # 查找父级的 Library/bin 目录
    bin_path = os.path.join(os.path.dirname(os.path.dirname(pyside6_path)), 'Library', 'bin')
    if os.path.exists(bin_path):
        datas.append((bin_path, 'Library/bin'))
except:
    pass

# 收集PySide6的隐藏导入和子模块
hiddenimports = [
    'sqlite3',
    'reportlab.lib',
    'reportlab.platypus',
    'reportlab.pdfbase',
    'reportlab.lib.units',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.lib.styles',
    'reportlab.pdfbase.ttfonts',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
]

# 收集PySide6的所有子模块
try:
    hiddenimports += collect_submodules('PySide6')
except:
    pass

# 收集PySide6的数据文件
try:
    datas += collect_data_files('PySide6')
except:
    pass

# 收集reportlab的数据文件
try:
    datas += collect_data_files('reportlab')
except:
    pass

# 收集openpyxl的数据文件
try:
    datas += collect_data_files('openpyxl')
except:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'IPython',
        'jupyter',
        'test',
        'tests',
        'testing',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 合并重复的条目
a.datas = list(set(a.datas))
a.binaries = list(set(a.binaries))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='BloodReservationSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关闭控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)

# 添加COLLECT部分 - 生成目录模式
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='BloodReservationSystem',
)
