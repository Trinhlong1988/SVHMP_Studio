# pipeline_control.ps1 — 1-CLICK CONTROLLER (KHUYEN NGHI)
# Chay coordinator tren committed ref sach; in gate matrix + CMD ke can mo.
# Portable: repo = thu muc cha cua prompts/. Cross-machine OK.
$ErrorActionPreference = 'Continue'
$repo = Split-Path $PSScriptRoot -Parent
Set-Location $repo

# Python: uu tien venv index-tts, fallback 'python'
$py = "C:\Users\Admin\index-tts\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=== SVHMP 4-CMD PIPELINE CONTROLLER ===" -ForegroundColor Cyan
Write-Host "Repo: $repo"
git fetch origin main | Out-Null
Write-Host "origin/main: $(git rev-parse --short origin/main)`n"

& $py tools\cmd_pipeline_gate.py --ref origin/main
$code = $LASTEXITCODE

Write-Host ""
switch ($code) {
  0 { Write-Host "READY_FOR_OWNER_FREEZE -> bao Mr.Long ky freeze." -ForegroundColor Green }
  1 { Write-Host "CHUA THONG. Xem ACTION_ROUTE o tren -> mo dung 1 CMD:" -ForegroundColor Yellow
      Write-Host "   .\prompts\open_cmd.ps1 BUILD|ARCH|QA|RELEASE" }
  2 { Write-Host "NOT_VERIFIED (thieu tool / lock / ref). Xem report." -ForegroundColor Red }
}
Write-Host "`nReport: reports\cmd_pipeline_gate_report.md"
Read-Host "`nEnter de dong"
