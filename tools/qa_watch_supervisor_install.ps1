# Auto-start qa_watch_supervisor.py tại Windows logon
# Run as Administrator OR user-level scheduled task

$TaskName = "SVHMP_QAWatchSupervisor"
$Repo = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"
$Python = "C:\Program Files\Python311\python.exe"
$Script = "$Repo\tools\qa_watch_supervisor.py"
$VbsLauncher = "$Repo\tools\qa_watch_supervisor.vbs"

# Create silent VBS launcher (chống flash CMD window per memory feedback_wscript_launcher_pattern)
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$Repo"
WshShell.Run "`"$Python`" `"$Script`"", 0, False
"@
$VbsContent | Out-File -FilePath $VbsLauncher -Encoding ASCII -Force
Write-Host "Created VBS launcher: $VbsLauncher"

# Register scheduled task at logon
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsLauncher`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force

Write-Host "Scheduled task '$TaskName' registered — auto-start at logon"
Write-Host ""
Write-Host "Manual start now: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Stop: Stop-ScheduledTask -TaskName '$TaskName'; Get-Process python | Where-Object {`$_.CommandLine -match 'qa_watch'} | Stop-Process -Force"
Write-Host "Uninstall: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
