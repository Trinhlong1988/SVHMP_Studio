chcp 65001 | Out-Null
$Host.UI.RawUI.WindowTitle = "ANAPHORA-FIX"
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
  Add-Content -Path "C:\tmp\svhmp_review\runtime\realtime_logs\fix.log" -Value $msg -Encoding UTF8
}
$env:PYTHONIOENCODING = "utf-8"
Log "=== ANAPHORA FIX LOOP ==="
$i = 0
while ($true) {
  $i++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Iter $i"
  $out = python tools\fix_chains_zero_tolerance.py --apply 2>&1 | Out-String
  $lines = $out -split "`n" | Select-Object -First 6
  Log ($lines -join "`n")
  Start-Sleep -Seconds 120
}



