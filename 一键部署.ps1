# 血制品预约登记系统 - PowerShell一键部署脚本
# 使用方法: 右键点击此文件 -> "使用PowerShell运行"

param(
    [switch]$Auto,
    [switch]$Install,
    [switch]$Build,
    [switch]$Test
)

# 设置控制台
$Host.UI.RawUI.WindowTitle = "血制品预约登记系统 - 部署工具"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

Write-Host @"
████████████████████████████████████████████████████████████████
██                                                          ██
██            血制品预约登记系统 - 一键部署工具             ██
██                                                          ██
████████████████████████████████████████████████████████████████
"@

# 检查Python
function Test-Python {
    try {
        $version = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] 找到Python: $version" -ForegroundColor Cyan
            return $true
        }
    } catch {
        Write-Host "[ERROR] 未找到Python环境！" -ForegroundColor Red
        Write-Host "请先安装Python 3.8-3.11" -ForegroundColor Yellow
        Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Cyan
        return $false
    }
}

# 安装依赖
function Install-Dependencies {
    Write-Host "`n[步骤] 安装依赖包..." -ForegroundColor Yellow
    Write-Host "  正在安装 PySide6..." -ForegroundColor Gray
    pip install "PySide6>=6.6.0,<6.7.0" --quiet --no-warn-script-location
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  尝试使用最新版本..." -ForegroundColor Yellow
        pip install PySide6 --quiet --no-warn-script-location
    }

    Write-Host "  正在安装 reportlab..." -ForegroundColor Gray
    pip install reportlab==4.1.0 --quiet --no-warn-script-location

    Write-Host "  正在安装 pyinstaller..." -ForegroundColor Gray
    pip install pyinstaller --quiet --no-warn-script-location

    Write-Host "  正在安装其他依赖..." -ForegroundColor Gray
    pip install -r requirements.txt --quiet --no-warn-script-location 2>$null

    Write-Host "[OK] 依赖安装完成" -ForegroundColor Green
}

# 打包程序
function Build-Executable {
    Write-Host "`n[步骤] 开始打包..." -ForegroundColor Yellow

    if (Test-Path "build.spec") {
        pyinstaller --clean build.spec
    } else {
        pyinstaller --onefile --windowed --name="预约血" --version-file=version_info.txt main.py
    }

    if (Test-Path "dist\预约血.exe") {
        $exePath = Resolve-Path "dist\预约血.exe"
        $size = (Get-Item $exePath).Length

        Write-Host "`n✅ 打包成功！" -ForegroundColor Green
        Write-Host "`n文件信息:" -ForegroundColor Cyan
        Write-Host "  - 文件名: 预约血.exe"
        Write-Host "  - 大小: $([math]::Round($size/1MB, 2)) MB"
        Write-Host "  - 路径: $exePath"
        Write-Host "`n📋 部署说明:" -ForegroundColor Cyan
        Write-Host "  1. 将 dist 目录下的所有文件复制到目标电脑"
        Write-Host "  2. 双击 '预约血.exe' 即可运行"
        Write-Host "  3. 首次运行会自动创建数据库"

        return $true
    } else {
        Write-Host "`n❌ 打包失败！" -ForegroundColor Red
        return $false
    }
}

# 主逻辑
if ($Auto) {
    # 自动模式
    if (Test-Python) {
        Install-Dependencies
        $success = Build-Executable
        if ($success) {
            Write-Host "`n是否打开dist目录? (y/n)" -ForegroundColor Yellow
            $response = Read-Host
            if ($response -eq 'y' -or $response -eq 'Y') {
                explorer dist
            }
        }
    }
} elseif ($Install) {
    # 仅安装
    if (Test-Python) {
        Install-Dependencies
    }
} elseif ($Build) {
    # 仅打包
    $success = Build-Executable
} elseif ($Test) {
    # 测试数据库
    Write-Host "`n[步骤] 测试数据库功能..." -ForegroundColor Yellow
    python test_db.py
} else {
    # 交互模式
    Write-Host "`n请选择操作:" -ForegroundColor Yellow
    Write-Host "  [1] 自动安装依赖并打包 (推荐)"
    Write-Host "  [2] 仅安装依赖"
    Write-Host "  [3] 仅打包"
    Write-Host "  [4] 运行程序 (开发模式)"
    Write-Host "  [5] 测试数据库"
    Write-Host "  [0] 退出"
    Write-Host ""

    $choice = Read-Host "请输入选项 [0-5]"

    switch ($choice) {
        "1" {
            if (Test-Python) {
                Install-Dependencies
                $success = Build-Executable
                if ($success) {
                    Write-Host "`n是否打开dist目录? (y/n)" -ForegroundColor Yellow
                    $response = Read-Host
                    if ($response -eq 'y' -or $response -eq 'Y') {
                        explorer dist
                    }
                }
            }
        }
        "2" {
            if (Test-Python) {
                Install-Dependencies
            }
        }
        "3" {
            $success = Build-Executable
        }
        "4" {
            Write-Host "`n[步骤] 运行程序..." -ForegroundColor Yellow
            python main.py
        }
        "5" {
            Write-Host "`n[步骤] 测试数据库..." -ForegroundColor Yellow
            python test_db.py
        }
        "0" {
            Write-Host "感谢使用！" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "无效选项！" -ForegroundColor Red
        }
    }
}

Write-Host "`n操作完成！" -ForegroundColor Green
Read-Host "按Enter键退出"
