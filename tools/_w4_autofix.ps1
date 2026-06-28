$Host.UI.RawUI.WindowTitle = "AUTO-FIXER"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\autofix.log"
function Log([string]$msg) {
  Write-Host $msg
  [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false))
}

Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log ""
Log "=== AUTO-FIXER v2 — convergence loop EP02-50 ==="

$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c"
  
  # Convergence loop trong cycle: chạy đến khi 0 changes
  $iter = 0
  $totalChanges = 0
  do {
    $iter++
    $changes = 0
    
    # R58 tilde EOL
    $out58 = python tools\auto_fix_tilde_eol.py --apply 2>&1 | Select-String "Total:|SUMMARY:" | Out-String
    if ($out58 -match "Total: (\d+)") { $changes += [int]$matches[1] }
    elseif ($out58 -match "SUMMARY: (\d+)") { $changes += [int]$matches[1] }
    
    # R60 short EOL
    $out60 = python tools\auto_fix_short_eol.py --apply 2>&1 | Select-String "Total:" | Out-String
    if ($out60 -match "Total: (\d+)") { $changes += [int]$matches[1] }
    
    # R62 anaphora aggressive
    $out62 = python tools\fix_chains_zero_tolerance.py --apply 2>&1 | Select-String "Iter 1: fixes=(\d+)" | Out-String
    if ($out62 -match "fixes=(\d+)") { $changes += [int]$matches[1] }
    
    $totalChanges += $changes
    Log "  iter $iter changes=$changes"
  } while ($changes -gt 0 -and $iter -lt 5)
  
  # Final count
  $r58 = python tools\audit_tilde_eol.py --summary 2>&1 | Select-String "SUMMARY: (\d+)" | Out-String
  $r60 = python tools\audit_short_eol.py --summary 2>&1 | Select-String "SUMMARY: (\d+)" | Out-String
  $r61 = python tools\audit_short_start.py --summary 2>&1 | Select-String "SUMMARY: (\d+)" | Out-String
  $r62 = python tools\audit_anaphora_consecutive.py --summary 2>&1 | Select-String "SUMMARY: (\d+)" | Out-String
  
  $r58n = if ($r58 -match "SUMMARY: (\d+)") { $matches[1] } else { "?" }
  $r60n = if ($r60 -match "SUMMARY: (\d+)") { $matches[1] } else { "?" }
  $r61n = if ($r61 -match "SUMMARY: (\d+)") { $matches[1] } else { "?" }
  $r62n = if ($r62 -match "SUMMARY: (\d+)") { $matches[1] } else { "?" }
  
  Log ""
  Log "→ Cycle $c done — total changes=$totalChanges"
  Log "  Final state: R58=$r58n R60=$r60n R61=$r61n R62=$r62n"
  
  if ($r58n -eq "0" -and $r60n -eq "0" -and $r62n -eq "0") {
    Log "  ✅ All auto-fixable rules: 0 violations"
    Log "  ⚠️ R61=$r61n remains (manual rewrite needed)"
  }
  
  Start-Sleep -Seconds 45
}
