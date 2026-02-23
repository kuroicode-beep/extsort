# FileOrganizer launcher
$targetDir = "C:\Users\kuroi\OneDrive\문서\다운로드"
$pythonExe  = "C:\Users\kuroi\AppData\Local\Programs\Python\Python312\python.exe"
$scriptPath = "C:\Users\kuroi\extsort\organize.py"

Write-Host "=============================="
Write-Host " FileOrganizer 실행 중..."
Write-Host "=============================="

if (-Not (Test-Path $targetDir)) {
    Write-Host "[ERROR] 폴더를 찾을 수 없습니다: $targetDir"
    Read-Host "아무 키나 누르면 닫힙니다"
    exit 1
}

Set-Location $targetDir
Write-Host "작업 폴더: $(Get-Location)"
Write-Host ""

& $pythonExe $scriptPath

Write-Host ""
Write-Host "=============================="
Write-Host " 완료! Enter 를 누르면 닫힙니다."
Write-Host "=============================="
Read-Host
