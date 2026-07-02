chcp 65001 | Out-Null
$Host.UI.RawUI.WindowTitle = "QA-MONITOR"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Set Consolas font 14pt
$signature = @"
using System;
using System.Runtime.InteropServices;
public class ConsoleFont {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct CONSOLE_FONT_INFOEX {
        public int cbSize;
        public uint nFont;
        public short FontWidth;
        public short FontHeight;
        public int FontFamily;
        public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string FaceName;
    }
    [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr GetStdHandle(int h);
    [DllImport("kernel32.dll", SetLastError=true)] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CONSOLE_FONT_INFOEX f);
}
"@
Add-Type -TypeDefinition $signature -ErrorAction SilentlyContinue
$font = New-Object ConsoleFont+CONSOLE_FONT_INFOEX
$font.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($font)
$font.FontWidth = 0
$font.FontHeight = 16
$font.FontFamily = 54  # FF_DONTCARE | TMPF_TRUETYPE
$font.FontWeight = 400
$font.FaceName = "Cascadia Mono"
[ConsoleFont]::SetCurrentConsoleFontEx([ConsoleFont]::GetStdHandle(-11), $false, [ref]$font) | Out-Null
Set-Location C:\tmp\svhmp_review
function Log([string]$msg) {
  Write-Host $msg
  Add-Content -Path "C:\tmp\svhmp_review\runtime\realtime_logs\qa.log" -Value $msg -Encoding UTF8
}
$env:PYTHONIOENCODING = "utf-8"
Log "=== QA AUDIT MONITOR ==="
$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c"
  $r58 = python tools\audit_tilde_eol.py --summary 2>&1 | Select-String "SUMMARY" | Out-String
  $r60 = python tools\audit_short_eol.py --summary 2>&1 | Select-String "SUMMARY" | Out-String
  $r61 = python tools\audit_short_start.py --summary 2>&1 | Select-String "SUMMARY" | Out-String
  $r62 = python tools\audit_anaphora_consecutive.py --summary 2>&1 | Select-String "SUMMARY" | Out-String
  Log "R58: $($r58.Trim())"
  Log "R60: $($r60.Trim())"
  Log "R61: $($r61.Trim())"
  Log "R62: $($r62.Trim())"
  Start-Sleep -Seconds 30
}



