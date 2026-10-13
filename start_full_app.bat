@echo off
chcp 65001 >nul
title RetinaGuard AI - All-in-One Runner
echo =====================================================================
echo       KHỞI CHẠY HỆ THỐNG RETINAGUARD AI (MODELS A + B + C)
echo =====================================================================
echo.
echo Đang khởi động Backend FastAPI & Frontend Dashboard...
echo.

cd /d "%~dp0dr-fundus-app\backend"
python run_server.py
pause
