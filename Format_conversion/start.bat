@echo off
:: 一键启动批处理文件

chcp 65001 >nul
echo 正在启动图像格式转换工具...
echo 请确保Python环境已配置，且已安装所需库（Pillow, tqdm）。

:: 检查是否有Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 未检测到Python，请安装Python并确保其已添加到环境变量中。
    pause
    exit /b
)

:: 安装所需库
echo 正在检查并安装所需的Python库...
pip install Pillow tqdm

:: 运行Python脚本
python Format_conversion.py

echo Congratulation！！
pause
