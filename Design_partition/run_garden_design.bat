@echo off
setlocal

REM ==========================================================
REM  启动 Garden 设计脚本 (v3 - 智能版)
REM  - 优先使用 'garden.json'，如果不存在则使用 'garden.yaml'
REM  - 使用 'py -3' 确保调用 Python 3
REM  - 捕获 Python 脚本的错误并给出清晰提示
REM ==========================================================

REM 切换到批处理脚本所在的目录
cd /d %~dp0

echo [INFO] Current Directory: %cd%

set CONFIG_FILE=

REM --- 智能检测配置文件 ---
if exist "garden.json" (
    set CONFIG_FILE=garden.json
) else if exist "garden.yaml" (
    set CONFIG_FILE=garden.yaml
)

if not defined CONFIG_FILE (
    echo [ERROR] No configuration file found!
    echo Please create either 'garden.json' or 'garden.yaml' in this directory.
    goto end
)

echo [INFO] Using configuration file: %CONFIG_FILE%
echo [INFO] Starting the design process...
echo ----------------------------------------------------------

REM --- 运行 Python 脚本 ---
py -3 app.py --config %CONFIG_FILE% --output output.png

REM --- 检查 Python 脚本是否成功执行 ---
if %errorlevel% neq 0 (
    echo ----------------------------------------------------------
    echo [ERROR] The Python script failed with an error.
    echo Please check the error messages above.
    goto end
)

:end
echo.
pause