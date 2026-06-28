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
[CF3]::SetCurrentConsoleFontEx([CF3]::GetStdHandle(-11), $false, [ref]$f) | Out-Null$Host.UI.RawUI.WindowTitle = "HIDDEN-BUGS"
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\hidden.log"
function Log([string]$msg) { Write-Host $msg; [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false)) }
Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log "=== HIDDEN BUGS 20-DIM (C1) ==="
$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c"
  python tools\audit_hidden_bugs.py 2>&1 | Select-Object -Last 30 | ForEach-Object { Log $_.Trim() }
  Start-Sleep -Seconds 90
}
