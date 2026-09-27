@echo off
chcp 65001 >nul
title USTAD MUHASEBE · Tam Teşkilat Muhasebe Programı
cd /d "%~dp0"

echo ============================================================
echo    USTAD MUHASEBE · yerel sunucu baslatiliyor
echo    Panel  : http://127.0.0.1:8091
echo    Bu pencereyi KAPATMAYIN - kapanirsa program durur.
echo ============================================================
echo.

rem Tarayiciyi 3 saniye sonra ac (sunucu ayaga kalksin)
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8091"

:nobet
python sunucu\sunucu.py 8091
echo.
echo [%date% %time%] Sunucu durdu - 5 saniye sonra yeniden baslatiliyor...
timeout /t 5 >nul
goto nobet
