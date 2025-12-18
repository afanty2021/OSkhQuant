@echo off
REM 看海量化交易系统 - 开发版启动脚本
REM Version: 2.1.5-dev
REM Build Date: 2025-12-13

echo ====================================
echo    看海量化交易系统 - 开发版
echo    Version: 2.1.5-dev
echo    Build Date: 2025-12-13
echo ====================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查虚拟环境
if exist venv\ (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
)

REM 检查依赖包
echo [信息] 检查核心依赖包...
python -c "import PyQt5, pandas, numpy, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [警告] 部分依赖包缺失，正在安装...
    pip install -r requirements.txt
)

REM 检查xtquant
echo [信息] 检查xtquant数据接口...
python -c "import xtquant" >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到xtquant包，请确保已安装MiniQMT客户端
    echo [提示] xtquant通常位于MiniQMT安装目录的python包中
)

REM 启动主程序
echo.
echo [信息] 启动看海量化交易系统开发版...
echo.

REM 设置开发环境变量
set KHQUANT_DEV=1
set KHQUANT_VERSION=2.1.5-dev

REM 启动GUI主界面
python GUIkhQuant.py

REM 如果程序异常退出，暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，错误代码: %errorlevel%
    pause
)