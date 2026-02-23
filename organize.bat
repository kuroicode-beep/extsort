@echo off
chcp 65001 > nul
echo ==============================
echo  FileOrganizer 실행 중...
echo ==============================
cd /d "C:\Users\kuroi\OneDrive\문서\다운로드"
if errorlevel 1 (
    echo [ERROR] 다운로드 폴더를 찾을 수 없습니다.
    pause
    exit /b 1
)
echo 작업 폴더: %CD%
echo.
"C:\Users\kuroi\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\kuroi\extsort\organize.py"
echo.
echo ==============================
echo  완료! 아무 키나 누르면 닫힙니다.
echo ==============================
pause
