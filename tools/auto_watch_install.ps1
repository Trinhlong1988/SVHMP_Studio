# Install SVHMP Auto-Watch as Windows scheduled task (run at logon, hidden)
# Mr.Long chạy 1 lần với admin: pwsh -File tools/auto_watch_install.ps1
# Uninstall: schtasks /Delete /TN "SVHMP_AutoWatch" /F

$taskName = "SVHMP_AutoWatch"
$vbsPath = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\tools\auto_watch.vbs"

# Check existing task
$existing = schtasks /Query /TN $taskName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Task $taskName đã tồn tại. Xóa trước khi cài lại..."
    schtasks /Delete /TN $taskName /F | Out-Null
}

# Create scheduled task: trigger AtLogon, action = wscript hidden
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 3 `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)   # unlimited
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "SVHMP Auto-Watch daemon — Phase H5 Option A. Auto-trigger orchestrator khi episode.md mới/thay đổi."

Write-Host ""
Write-Host "✓ Task installed: $taskName"
Write-Host "  Khởi động ngay: schtasks /Run /TN $taskName"
Write-Host "  Kiểm tra status: schtasks /Query /TN $taskName /V /FO LIST"
Write-Host "  Stop daemon: Stop-Process -Id (Get-Content runtime\auto_watch.pid)"
Write-Host "  Uninstall: schtasks /Delete /TN $taskName /F"
