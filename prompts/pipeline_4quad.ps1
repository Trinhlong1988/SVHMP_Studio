# pipeline_4quad.ps1 — TUY CHON: mo 4 CMD chia 4 goc 1 man hinh (Windows Terminal).
# LUU Y (bang chung): pipeline von TUAN TU/khong-chong-cheo -> khuyen dung
# pipeline_control.ps1 (mo 1 CMD theo ACTION_ROUTE). 4-goc chi de NHIN; coordinator
# co lock chong overlap that su. Can Windows Terminal (wt.exe).
$repo = Split-Path $PSScriptRoot -Parent
$wt = Get-Command wt.exe -ErrorAction SilentlyContinue

function Seed($name) {
  "Ban la $name trong pipeline SVHMP. Doc prompts/$name.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu. Cho lenh."
}

if (-not $wt) {
  Write-Host "Windows Terminal (wt.exe) CHUA cai -> khong the chia 4 goc 1 cua so." -ForegroundColor Yellow
  Write-Host "Cai: winget install Microsoft.WindowsTerminal  (roi chay lai)."
  Write-Host "Tam thoi mo 4 cua so rieng (best-effort)..."
  foreach ($r in 'BUILD','ARCH','QA','RELEASE') { & "$PSScriptRoot\open_cmd.ps1" $r }
  return
}

# 2x2: [BUILD | ARCH] / [QA | RELEASE]
$b = Seed 'CMD_BUILD'; $a = Seed 'CMD_ARCH_AUDIT'; $q = Seed 'CMD_QA_AUDIT'; $r = Seed 'CMD_RELEASE_AUDIT'
wt -w new new-tab  --title CMD_BUILD        -d "$repo" powershell -NoExit -ExecutionPolicy Bypass -Command "claude `"$b`"" `
   `; split-pane -V --title CMD_ARCH_AUDIT  -d "$repo" powershell -NoExit -ExecutionPolicy Bypass -Command "claude `"$a`"" `
   `; move-focus left `
   `; split-pane -H --title CMD_QA_AUDIT     -d "$repo" powershell -NoExit -ExecutionPolicy Bypass -Command "claude `"$q`"" `
   `; move-focus right `
   `; split-pane -H --title CMD_RELEASE_AUDIT -d "$repo" powershell -NoExit -ExecutionPolicy Bypass -Command "claude `"$r`""
Write-Host "Da mo 4 CMD (2x2). NHAC: chi lam 1 CMD theo ACTION_ROUTE cua controller."
