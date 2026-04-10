@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   四年级数学教程技能 - 云服务器数据同步
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [OK] Python已安装
echo.

REM 检查依赖
echo 检查依赖包...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo 安装requests包...
    pip install requests
) else (
    echo [OK] requests已安装
)

echo.
echo 四年级专用云数据同步功能
echo.

echo 请选择功能:
echo 1. 测试四年级云服务器连接
echo 2. 演示四年级完整工作流程
echo 3. 交互式模式（输入数据）
echo 4. 启动后台自动同步
echo 5. 查看当前四年级数据状态
echo 6. 强制同步所有四年级数据
echo 0. 退出
echo.

set /p choice=请选择 (0-6): 

if "%choice%"=="1" (
    echo.
    echo 测试四年级云服务器连接...
    python scripts/cloud_data_sender.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 演示四年级完整工作流程...
    python scripts/fourth_grade_data_handler.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo 启动四年级交互式模式...
    python scripts/fourth_grade_data_handler.py
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo 启动四年级后台自动同步...
    echo 注意: 后台同步将在每10分钟自动检查并发送待处理数据
    echo 按Ctrl+C可停止
    echo.
    python -c "
from scripts.fourth_grade_data_handler import FourthGradeDataHandler
import time
handler = FourthGradeDataHandler()
thread = handler.start_auto_sync(interval_minutes=10)
print('四年级后台同步已启动，按Ctrl+C停止')
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print('停止四年级后台同步')
"
    goto :end
)

if "%choice%"=="5" (
    echo.
    echo 查看四年级当前状态...
    python -c "
from scripts.fourth_grade_data_handler import FourthGradeDataHandler
handler = FourthGradeDataHandler()
status = handler.get_status()
print('四年级数据状态:')
print(f'  年级: {status[\"grade\"]}')
print(f'  本地用户数: {status[\"local_users_count\"]}')
print(f'  本地错题数: {status[\"local_mistakes_count\"]}')
print(f'  待同步用户: {status[\"pending_sync_users\"]}')
print(f'  待同步错题: {status[\"pending_sync_mistakes\"]}')
print(f'  云服务器: {\"[OK] 已启用\" if status[\"cloud_enabled"] else \"[WARN] 未启用\"}')
print(f'  云连接: {\"[OK] 已连接\" if status[\"cloud_connected"] else \"[WARN] 未连接\"}')
print(f'  最后更新: {status.get(\"last_user_update\", \"未知\")}')
"
    goto :end
)

if "%choice%"=="6" (
    echo.
    echo 强制同步所有四年级数据...
    python -c "
from scripts.fourth_grade_data_handler import FourthGradeDataHandler
handler = FourthGradeDataHandler()
result = handler.force_sync_all()
print(f'四年级数据同步结果: {result[\"message\"]}')
if result['success']:
    print(f'用户: {result[\"users\"][\"success\"]}/{result[\"users\"][\"total\"]} 成功')
    print(f'错题: {result[\"mistakes\"][\"success\"]}/{result[\"mistakes\"][\"total\"]} 成功')
"
    goto :end
)

if "%choice%"=="0" (
    echo 退出
    goto :end
)

echo 无效选择

:end
echo.
echo 按任意键退出...
pause >nul