# SVHMP — Launch QA realtime monitoring (ASCII path via junction)
# Uses C:\tmp\svhmp_review junction (avoids Vietnamese path issues)

$SVHMP = "C:\tmp\svhmp_review"
Set-Location $SVHMP

# Window 1: Ollama gemma2:9b live skeptic loop
$ollamaScript = @'
$SVHMP = "C:\tmp\svhmp_review"
Set-Location $SVHMP
$Host.UI.RawUI.WindowTitle = "OLLAMA SKEPTIC - SVHMP QA"
Write-Host "=== OLLAMA gemma2:9b LIVE SKEPTIC ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)"
Write-Host ""
$cycle = 0
while ($true) {
  $cycle++
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $cycle - phản biện anaphora fix EP02-50..." -ForegroundColor Yellow
  $prompt = "Đánh giá ngắn 80 từ tiếng Việt: SVHMP horror narration sau khi auto-fix 469 vary anaphora chains EP02-50 (giảm 202 chains về 0). Risk: narrative coherence broken không? Verdict PASS/REVIEW/FAIL."
  ollama run gemma2:9b $prompt 2>&1
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $cycle done. Sleep 60s..." -ForegroundColor Green
  Start-Sleep -Seconds 60
}
'@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaScript -WindowStyle Normal

# Window 2: QA Audit live monitor
$qaScript = @'
$SVHMP = "C:\tmp\svhmp_review"
Set-Location $SVHMP
$Host.UI.RawUI.WindowTitle = "QA AUDIT MONITOR - SVHMP"
$env:PYTHONIOENCODING = "utf-8"
Write-Host "=== QA AUDIT LIVE MONITOR ===" -ForegroundColor Cyan
$cycle = 0
while ($true) {
  $cycle++
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $cycle audits..." -ForegroundColor Yellow
  python tools\audit_anaphora_consecutive.py --summary 2>&1 | Select-String "SUMMARY"
  python tools\audit_tilde_eol.py --summary 2>&1 | Select-String "SUMMARY"
  python tools\audit_short_eol.py --summary 2>&1 | Select-String "SUMMARY"
  python tools\audit_short_start.py --summary 2>&1 | Select-String "SUMMARY"
  python tools\audit_r68_to_r73.py --summary 2>&1 | Select-String "SUMMARY"
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Sleep 30s..." -ForegroundColor Green
  Start-Sleep -Seconds 30
}
'@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $qaScript -WindowStyle Normal

# Window 3: Anaphora fix continuous loop
$fixScript = @'
$SVHMP = "C:\tmp\svhmp_review"
Set-Location $SVHMP
$Host.UI.RawUI.WindowTitle = "ANAPHORA FIX LOOP - SVHMP"
$env:PYTHONIOENCODING = "utf-8"
Write-Host "=== ANAPHORA FIX CONTINUOUS LOOP ===" -ForegroundColor Cyan
$iter = 0
while ($true) {
  $iter++
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Iter $iter zero-tolerance fix..." -ForegroundColor Yellow
  python tools\fix_chains_zero_tolerance.py --apply 2>&1 | Select-Object -First 8
  Write-Host ""
  Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Sleep 120s..." -ForegroundColor Green
  Start-Sleep -Seconds 120
}
'@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $fixScript -WindowStyle Normal

Write-Host ""
Write-Host "=== LAUNCHED 3 VISIBLE WINDOWS ===" -ForegroundColor Green
Write-Host "1. OLLAMA SKEPTIC (60s cycle)"
Write-Host "2. QA AUDIT MONITOR (30s cycle)"
Write-Host "3. ANAPHORA FIX LOOP (120s cycle)"
Write-Host ""
Write-Host "Logs realtime trong các CMD windows visible"
Write-Host "Path: C:\tmp\svhmp_review (junction to D:\DỰ ÁN AI\...)"
