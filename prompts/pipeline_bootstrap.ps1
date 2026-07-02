# pipeline_bootstrap.ps1 — DONG BO + SHIP DESKTOP (chay 1 lan tren MOI may).
# - pull repo moi nhat
# - tao shortcut Desktop tro toi launcher TRONG repo (path dung tren may do)
# Cross-machine: clone repo -> chay file nay -> co icon Desktop.
$ErrorActionPreference = 'Continue'
$repo = Split-Path $PSScriptRoot -Parent
Set-Location $repo
Write-Host "Repo: $repo"
git pull --rebase origin main

$desk = [Environment]::GetFolderPath('Desktop')
$sh = New-Object -ComObject WScript.Shell

function Make-Shortcut($lnkName, $scriptRel, $args2) {
  $lnk = $sh.CreateShortcut((Join-Path $desk $lnkName))
  $lnk.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  $lnk.Arguments  = "-ExecutionPolicy Bypass -File `"$repo\prompts\$scriptRel`" $args2"
  $lnk.WorkingDirectory = $repo
  $lnk.IconLocation = "$env:SystemRoot\System32\shell32.dll,167"
  $lnk.Save()
  Write-Host "  shortcut: $lnkName -> prompts\$scriptRel $args2"
}

Make-Shortcut "SVHMP PIPELINE (control).lnk"  "pipeline_control.ps1" ""
Make-Shortcut "SVHMP CMD BUILD.lnk"           "open_cmd.ps1" "BUILD"
Make-Shortcut "SVHMP CMD ARCH.lnk"            "open_cmd.ps1" "ARCH"
Make-Shortcut "SVHMP CMD QA.lnk"              "open_cmd.ps1" "QA"
Make-Shortcut "SVHMP CMD RELEASE.lnk"         "open_cmd.ps1" "RELEASE"
Make-Shortcut "SVHMP PIPELINE 4-quad.lnk"     "pipeline_4quad.ps1" ""

Write-Host "`nXONG. Desktop co icon 'SVHMP PIPELINE (control)' -> 1-click chay coordinator."
Write-Host "Cross-machine: clone repo + chay lai file nay la co icon."
Read-Host "Enter de dong"
