chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$signature = @"
using System;
using System.Runtime.InteropServices;
public class CF3 {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct CFI {
        public int cbSize; public uint nFont; public short FontWidth; public short FontHeight;
        public int FontFamily; public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string FaceName;
    }
    [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int h);
    [DllImport("kernel32.dll")] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CFI f);
}
"@
Add-Type -TypeDefinition $signature -ErrorAction SilentlyContinue
$f = New-Object CF3+CFI
$f.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($f)
$f.FontHeight = 16; $f.FontFamily = 54; $f.FontWeight = 400; $f.FaceName = "Cascadia Mono"
[CF3]::SetCurrentConsoleFontEx([CF3]::GetStdHandle(-11), $false, [ref]$f) | Out-Null$Host.UI.RawUI.WindowTitle = "BIBLE-AUDIT"
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\bible.log"
function Log([string]$msg) { Write-Host $msg; [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false)) }
Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log "=== BIBLE R40-R57 audit (C2) ==="
$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c - run post_render_gate (11 checks per EP)"
  $pass = 0; $fail = 0; $failed = @()
  for ($ep = 1; $ep -le 50; $ep++) {
    $r = python tools\post_render_gate.py --ep $ep 2>&1 | Select-String "Total:" | Out-String
    if ($r -match "0 FAIL") { $pass++ } else { $fail++; $failed += $ep }
  }
  Log "post_render_gate (R40 intro + R42 driver + R44 dict + Hà rename + Quang + bell + ghost + dur + section): $pass/50 PASS, $fail FAIL"
  if ($failed.Count -gt 0) { Log "Failed EPs: $($failed -join ',')" }
  
  # Run dialogue + story_mode + ngan_opening
  $d = python tools\audit_dialogue_hierarchy.py --summary 2>&1 | Select-String "SUMMARY|HIGH" | Out-String
  Log "Dialogue (R48): $($d.Trim())"
  $s = python tools\audit_story_mode.py --summary 2>&1 | Select-String "SUMMARY" | Out-String
  Log "Story mode (R56): $($s.Trim())"
  Start-Sleep -Seconds 60
}
