# Install SVHMP Auto-Watch as Windows scheduled task (run at logon, hidden)
# Mr.Long run once: pwsh -File tools/auto_watch_install.ps1
# Uninstall: schtasks /Delete /TN "SVHMP_AutoWatch" /F

$taskName = "SVHMP_AutoWatch"
$workDir = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"

# Check existing task
$existing = schtasks /Query /TN $taskName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Task $taskName already exists. Removing before reinstall..."
    schtasks /Delete /TN $taskName /F | Out-Null
}

# Use ASCII-safe Python starter (Python handles UTF-8 path natively, unlike cmd.exe)
$starterPy = "C:\Users\Administrator\svhmp_auto_watch_starter.py"
if (-not (Test-Path $starterPy)) {
    Write-Host "ERROR: starter not found at $starterPy"
    exit 1
}
$pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue).Path
if (-not $pythonw) {
    $pyPath = (Get-Command python -ErrorAction Stop).Path
    $pythonw = Join-Path (Split-Path $pyPath) "pythonw.exe"
}
Write-Host "pythonw: $pythonw"
Write-Host "Starter: $starterPy"

# Schtask Execute = pythonw (ASCII), Argument = starter.py (ASCII), no WorkingDirectory
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$starterPy`""
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
    -Description "SVHMP Auto-Watch daemon Phase H5 Option A. Auto-trigger orchestrator on new/modified episode.md."

Write-Host ""
Write-Host "OK Task installed: $taskName"
Write-Host "  Start now: schtasks /Run /TN $taskName"
Write-Host "  Status: schtasks /Query /TN $taskName /V /FO LIST"
Write-Host "  Stop daemon: Stop-Process -Id (Get-Content runtime\auto_watch.pid)"
Write-Host "  Uninstall: schtasks /Delete /TN $taskName /F"
