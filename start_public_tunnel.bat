@echo off
chcp 65001 >nul
title Cloudflare Tunnel - RetinaGuard AI
echo =====================================================================
echo    KHỞI ĐỘNG CLOUDFLARE TUNNEL - CÔNG KHAI ỨNG DỤNG RA INTERNET
echo =====================================================================
echo.
echo Đang kết nối cổng http://127.0.0.1:8000 ra Cloudflare Edge Network...
echo Hãy tìm dòng: "Your quick Tunnel has been created! Visit it at:"
echo để lấy đường dẫn HTTPS công khai (.trycloudflare.com).
echo.
echo Nhấn Ctrl+C để dừng chia sẻ công khai.
echo =====================================================================
echo.

"%~dp0tools\cloudflared.exe" tunnel --url http://127.0.0.1:8000
pause
