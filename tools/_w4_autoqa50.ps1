chcp 65001 | Out-Null
$Host.UI.RawUI.WindowTitle = "AUTO-QA-50"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$signature = @"
using System;
using System.Runtime.InteropServices;
public class CF2 {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct CONSOLE_FONT_INFOEX {
        public int cbSize; public uint nFont; public short FontWidth; public short FontHeight;
        public int FontFamily; public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string FaceName;
    }
    [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr GetStdHandle(int h);
    [DllImport("kernel32.dll", SetLastError=true)] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CONSOLE_FONT_INFOEX f);
}
"@
Add-Type -TypeDefinition $signature -ErrorAction SilentlyContinue
$font = New-Object CF2+CONSOLE_FONT_INFOEX
$font.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($font)
$font.FontHeight = 16; $font.FontFamily = 54; $font.FontWeight = 400
$font.FaceName = "Cascadia Mono"
[CF2]::SetCurrentConsoleFontEx([CF2]::GetStdHandle(-11), $false, [ref]$font) | Out-Null

$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\qa50.log"
function Log([string]$msg) {
  Write-Host $msg
  [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false))
}

Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log ""
Log "=== AUTO-QA-50 v2 — Full audit + R74 phrase repetition ==="

$cycle = 0
while ($true) {
  $cycle++
  Log ""
  Log "===== CYCLE $cycle ($([DateTime]::Now.ToString('HH:mm:ss'))) ====="
  
  # 1. post_render_gate per EP
  $pass = 0; $fail = 0
  for ($ep = 1; $ep -le 50; $ep++) {
    $gate = python tools\post_render_gate.py --ep $ep 2>&1 | Select-String "Total:" | Out-String
    if ($gate -match "(\d+) FAIL" -and [int]$matches[1] -eq 0) { $pass++ } else { $fail++ }
  }
  Log "post_render_gate: $pass/50 PASS"
  
  # 2. R74 phrase repetition audit
  python tools\audit_phrase_repetition.py --summary 2>&1 | Select-String "SUMMARY" | Out-String | ForEach-Object { Log "R74: $($_.Trim())" }
  
  # 3. Auto-trigger fixes
  Log ""
  Log "→ Auto-trigger fixes..."
  $changes = 0
  $out = python tools\auto_fix_tilde_eol.py --apply 2>&1 | Select-String "SUMMARY|Total" | Out-String
  Log "R58 fix: $($out.Trim())"
  
  $out = python tools\auto_fix_short_eol.py --apply 2>&1 | Select-String "Total" | Out-String
  Log "R60 fix: $($out.Trim())"
  
  $out = python tools\fix_chains_zero_tolerance.py --apply 2>&1 | Select-String "Iter 1:|CONVERGED" | Out-String
  Log "R62 fix: $($out.Trim())"
  
  $out = python tools\auto_fix_phrase_repetition.py --apply 2>&1 | Select-String "Total" | Out-String
  Log "R74 fix: $($out.Trim())"
  
  Log ""
  Log "Sleep 60s..."
  Start-Sleep -Seconds 60
}
