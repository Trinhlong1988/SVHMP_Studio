# SVHMP — Launch QA realtime monitoring (3 visible CMD windows)
# Mr.Long 28/6 lệnh: "tao muốn nhìn rõ cách thức hoạt động"

$SVHMP = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"
Set-Location $SVHMP

# Window 1: Ollama gemma2:9b live skeptic
$ollamaCmd = @"
cd '$SVHMP'
Write-Host '=== OLLAMA gemma2:9b LIVE SKEPTIC ===' -ForegroundColor Cyan
Write-Host 'PID:' \$PID
Write-Host 'Started:' (Get-Date)
Write-Host ''
while (\$true) {
  Write-Host '[' (Get-Date -Format 'HH:mm:ss') '] Asking gemma2:9b để phản biện EP02 sample...' -ForegroundColor Yellow
  ollama run gemma2:9b 'Đánh giá ngắn (≤80 từ tiếng Việt) chất lượng EP02 SVHMP horror narration sau khi fix anaphora chains. Focus: rhythm tự nhiên, tính horror, lặp từ. Verdict: PASS/FAIL/REVIEW.' 2>&1
  Write-Host '[' (Get-Date -Format 'HH:mm:ss') '] Cycle done. Sleep 60s...' -ForegroundColor Green
  Start-Sleep -Seconds 60
}
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaCmd

# Window 2: QA Audit live monitor
$qaCmd = @"
cd '$SVHMP'
Write-Host '=== QA AUDIT LIVE MONITOR ===' -ForegroundColor Cyan
Write-Host 'Watching anaphora chains EP02-50 every 30s'
while (\$true) {
  \$env:PYTHONIOENCODING='utf-8'
  Write-Host ''
  Write-Host '[' (Get-Date -Format 'HH:mm:ss') '] Running audits...' -ForegroundColor Yellow
  python tools/audit_anaphora_consecutive.py --summary 2>&1 | Select-String 'SUMMARY'
  python tools/audit_tilde_eol.py --summary 2>&1 | Select-String 'SUMMARY'
  python tools/audit_short_eol.py --summary 2>&1 | Select-String 'SUMMARY'
  python tools/audit_short_start.py --summary 2>&1 | Select-String 'SUMMARY'
  \$total = 0
  for (\$ep = 2; \$ep -le 50; \$ep++) {
    \$result = python tools/post_render_gate.py --ep \$ep 2>&1 | Select-String 'Total:'
    if (\$result -match '0 FAIL') { \$total++ }
  }
  Write-Host '[' (Get-Date -Format 'HH:mm:ss') '] post_render_gate: '\$total'/49 PASS' -ForegroundColor Green
  Start-Sleep -Seconds 30
}
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $qaCmd

# Window 3: Anaphora fix live loop
$fixCmd = @"
cd '$SVHMP'
Write-Host '=== ANAPHORA FIX LIVE LOOP ===' -ForegroundColor Cyan
\$env:PYTHONIOENCODING='utf-8'
\$iter = 0
while (\$true) {
  \$iter++
  Write-Host ''
  Write-Host '[' (Get-Date -Format 'HH:mm:ss') '] Iter ' \$iter ' — checking chains...' -ForegroundColor Yellow
  python tools/fix_chains_zero_tolerance.py --apply 2>&1 | Select-String 'Iter|CONVERGED|limit' | Select-Object -First 5
  Start-Sleep -Seconds 120
}
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $fixCmd

Write-Host "✅ Launched 3 visible CMD windows:" -ForegroundColor Green
Write-Host "  1. Ollama gemma2:9b skeptic (60s cycle)"
Write-Host "  2. QA audit monitor (30s cycle)"
Write-Host "  3. Anaphora fix loop (120s cycle)"
