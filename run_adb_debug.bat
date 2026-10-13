@echo off
chcp 65001 >nul
title RetinaGuard AI - ADB Debugging Assistant
set "ADB_PATH=%~dp0tools\platform-tools\adb.exe"

:MENU
cls
echo =====================================================================
echo       CÔNG CỤ HỖ TRỢ DEBUG ANDROID QUA ADB (RETINAGUARD AI)
echo =====================================================================
echo.
echo 1. Kiểm tra danh sách thiết bị đang kết nối (adb devices)
echo 2. [KHÔNG DÙNG CÁP] Ghép nối và kết nối Wi-Fi (Android 11+ Wireless Debugging)
echo 3. [ĐÃ GHÉP NỐI RỒI] Kết nối nhanh lại qua IP & Cổng (adb connect)
echo 4. [NẾU DÙNG CÁP] Cầu nối cổng Backend về điện thoại (adb reverse tcp:8000)
echo 5. Xem Logcat thời gian thực từ ứng dụng (adb logcat)
echo 6. Chụp ảnh màn hình điện thoại lưu vào máy tính (screencap)
echo 7. Khởi động lại dịch vụ ADB (adb kill-server & start-server)
echo 8. Thoát
echo =====================================================================
echo.

set /p choice="Nhập lựa chọn của bạn (1-8): "

if "%choice%"=="1" goto CHECK_DEVICES
if "%choice%"=="2" goto WIRELESS_PAIR_A11
if "%choice%"=="3" goto WIRELESS_QUICK_CONNECT
if "%choice%"=="4" goto REVERSE_PORT
if "%choice%"=="5" goto LOGCAT
if "%choice%"=="6" goto SCREENCAP
if "%choice%"=="7" goto RESTART_ADB
if "%choice%"=="8" exit /b
goto MENU

:CHECK_DEVICES
cls
echo [1] Đang quét các thiết bị Android...
echo.
"%ADB_PATH%" devices -l
echo.
echo ---------------------------------------------------------------------
echo Nếu danh sách trống: Hãy chọn mục 2 để ghép nối không dây qua Wi-Fi!
echo ---------------------------------------------------------------------
echo.
pause
goto MENU

:WIRELESS_PAIR_A11
cls
echo =====================================================================
echo  [2] GỠ LỖI KHÔNG DÂY QUA WI-FI (ANDROID 11 TRỞ LÊN - KHÔNG CẦN DÂY CÁP)
echo =====================================================================
echo.
echo HƯỚNG DẪN THAO TÁC TRÊN ĐIỆN THOẠI (Cùng mạng Wi-Fi với máy tính):
echo 1. Vào Cài đặt ^> Tùy chọn nhà phát triển (Developer Options).
echo 2. Bật công tắc "Gỡ lỗi không dây" (Wireless debugging).
echo 3. Chạm VÀO DÒNG CHỮ "Gỡ lỗi không dây" để mở trang chi tiết.
echo 4. Chọn "Ghép nối thiết bị bằng mã ghép nối" (Pair device with pairing code).
echo.
echo Màn hình điện thoại sẽ hiện ra 2 thông số:
echo   - Mã ghép nối Wi-Fi (6 chữ số)
echo   - Địa chỉ IP ^& Cổng ghép nối (Ví dụ: 192.168.1.50:37125)
echo.
echo ---------------------------------------------------------------------
set /p pair_host="Nhập Địa chỉ IP & Cổng ghép nối (ví dụ: 192.168.1.50:37125): "
set /p pair_code="Nhập Mã ghép nối 6 chữ số (ví dụ: 123456): "
echo.
echo Đang ghép nối với %pair_host%...
"%ADB_PATH%" pair %pair_host% %pair_code%
echo.
if %errorlevel% neq 0 (
    echo [THẤT BẠI] Ghép nối chưa thành công. Vui lòng kiểm tra lại IP, Port và Mã.
    pause
    goto MENU
)
echo [THÀNH CÔNG] Đã ghép nối thiết bị thành công!
echo.
echo BÂY GIỜ ĐÓNG HỘP THOẠI MÃ GHÉP NỐI TRÊN ĐIỆN THOẠI.
echo Nhìn vào dòng "Địa chỉ IP & Cổng" ở màn hình chính của "Gỡ lỗi không dây":
echo (Lưu ý: Cổng kết nối chính này thường KHÁC với cổng ghép nối vừa nãy!)
echo.
set /p conn_host="Nhập Địa chỉ IP & Cổng kết nối hiển thị trên điện thoại: "
echo Đang kết nối tới %conn_host%...
"%ADB_PATH%" connect %conn_host%
echo.
"%ADB_PATH%" devices -l
echo.
echo [HOÀN TẤT] Bây giờ bạn có thể debug/run app Flutter qua Wi-Fi hoàn toàn không cần cáp!
pause
goto MENU

:WIRELESS_QUICK_CONNECT
cls
echo =====================================================================
echo  [3] KẾT NỐI NHANH LẠI THIẾT BỊ ĐÃ GHÉP NỐI QUA WI-FI
echo =====================================================================
echo.
echo Dành cho thiết bị đã từng Pair thành công trước đó.
echo Mở Gỡ lỗi không dây trên điện thoại và xem "Địa chỉ IP & Cổng":
echo.
set /p conn_host="Nhập Địa chỉ IP & Cổng (ví dụ: 192.168.1.50:41235): "
echo Đang kết nối tới %conn_host%...
"%ADB_PATH%" connect %conn_host%
echo.
"%ADB_PATH%" devices -l
echo.
pause
goto MENU

:REVERSE_PORT
cls
echo [4] Đang thiết lập cầu nối cổng adb reverse tcp:8000 tcp:8000...
"%ADB_PATH%" reverse tcp:8000 tcp:8000
if %errorlevel% equ 0 (
    echo.
    echo [THÀNH CÔNG] Đã chuyển tiếp cổng 8000!
    echo Bây giờ điện thoại có thể truy cập Backend AI trực tiếp tại:
    echo 👉 http://127.0.0.1:8000
) else (
    echo.
    echo [THẤT BẠI] Chưa nhận diện được thiết bị.
)
echo.
pause
goto MENU

:LOGCAT
cls
echo [5] Đang theo dõi logs ứng dụng từ thiết bị (Nhấn Ctrl+C để dừng)...
echo.
"%ADB_PATH%" logcat -s flutter:V RetinaGuard:V AndroidRuntime:E
pause
goto MENU

:SCREENCAP
cls
echo [6] Đang chụp ảnh màn hình điện thoại...
"%ADB_PATH%" exec-out screencap -p > "%~dp0phone_screen.png"
if %errorlevel% equ 0 (
    echo.
    echo [THÀNH CÔNG] Đã lưu ảnh chụp màn hình điện thoại vào:
    echo 👉 %~dp0phone_screen.png
) else (
    echo [THẤT BẠI] Không thể chụp ảnh màn hình. Kiểm tra kết nối thiết bị.
)
echo.
pause
goto MENU

:RESTART_ADB
cls
echo [7] Đang khởi động lại dịch vụ ADB...
"%ADB_PATH%" kill-server
"%ADB_PATH%" start-server
echo Hoàn tất.
echo.
pause
goto MENU
