@echo off
REM M3SFMODE Kurulum Scripti - Windows

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          M3SFMODE Kurulum Scripti v1.0.0                 ║
echo ║                    Windows Edition                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [*] Sistem kontrol ediliyor...
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] g++ bulunamadi!
    echo [!] Lutfen MinGW veya GCC yukleyin.
    pause
    exit /b 1
)

echo [*] Derleme yapiliyor...
mingw32-make -f Makefile.windows clean
mingw32-make -f Makefile.windows

if %errorlevel% equ 0 (
    echo [+] Derleme basarili!
) else (
    echo [-] Derleme hata!
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║             Kurulum Tamamlandi! ✓                        ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║  Kullanim: m3sfmode.exe                                  ║
echo ║  Dosya:    m3sfmode.exe (mevcut dizinde)                 ║
echo ║  Versiyon: 1.0.0                                         ║
echo ║  GitHub:   github.com/memetcanwq31-ship-it/m3sfmode     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
