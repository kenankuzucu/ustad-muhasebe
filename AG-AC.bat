@echo off
chcp 65001 >nul
title USTAD MUHASEBE · YEREL AG MODU (telefondan giris)
cd /d "%~dp0"

rem ---------------------------------------------------------------
rem  YEREL AG MODU: programi yalniz bu bilgisayardan degil, ayni WiFi
rem  agindaki telefon/tabletten de acmak icin kullanilir.
rem  Guvenlik notu: trafik sifresiz (HTTP) oldugu icin yalnizca guvendigin
rem  agda kullan. Varsayilan (kapali) mod icin BASLAT.bat kullanilir.
rem ---------------------------------------------------------------

echo ============================================================
echo    USTAD MUHASEBE · YEREL AG MODU
echo    Bu pencereyi KAPATMAYIN - kapanirsa program durur.
echo ============================================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
  set "IP=%%a"
  goto :ipbulundu
)
:ipbulundu
set "IP=%IP: =%"
echo    Telefonundan su adresi ac:  http://%IP%:8091
echo.

start "" cmd /c "timeout /t 3 >nul & start http://%IP%:8091"

:nobet
python sunucu\sunucu.py 8091 --ag
echo.
echo [%date% %time%] Sunucu durdu - 5 saniye sonra yeniden baslatiliyor...
timeout /t 5 >nul
goto nobet
