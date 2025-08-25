@echo off
setlocal

REM ==========================================================
REM  ���� Garden ��ƽű� (v3 - ���ܰ�)
REM  - ����ʹ�� 'garden.json'�������������ʹ�� 'garden.yaml'
REM  - ʹ�� 'py -3' ȷ������ Python 3
REM  - ���� Python �ű��Ĵ��󲢸���������ʾ
REM ==========================================================

REM �л���������ű����ڵ�Ŀ¼
cd /d %~dp0

echo [INFO] Current Directory: %cd%

set CONFIG_FILE=

REM --- ���ܼ�������ļ� ---
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

REM --- ���� Python �ű� ---
py -3 app.py --config %CONFIG_FILE% --output output.png

REM --- ��� Python �ű��Ƿ�ɹ�ִ�� ---
if %errorlevel% neq 0 (
    echo ----------------------------------------------------------
    echo [ERROR] The Python script failed with an error.
    echo Please check the error messages above.
    goto end
)

:end
echo.
pause