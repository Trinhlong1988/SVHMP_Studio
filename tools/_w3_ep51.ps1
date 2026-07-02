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
[CF3]::SetCurrentConsoleFontEx([CF3]::GetStdHandle(-11), $false, [ref]$f) | Out-Null$Host.UI.RawUI.WindowTitle = "EP51-PREP"
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\ep51.log"
function Log([string]$msg) { Write-Host $msg; [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false)) }
Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log "=== EP51 PREP — chapter_contract validation + Ollama review (C3) ==="
$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c"
  
  # Check bible/21b ep_51 chapter_contract exists
  $bible21b = Get-Content "bible\21b_ep51_90_spec.yaml" -Raw -Encoding UTF8
  if ($bible21b -match "ep_51_chapter_contract") {
    Log "✓ bible/21b ep_51_chapter_contract present"
  }
  
  # Ollama review chapter_contract
  $prompt = "CONTEXT: SVHMP planning EP51. Chapter contract: passenger archetype A1 grandma waiting child, Khai Phong M9 memory trigger, kết lửng triết lý Ngạn style. CÂU HỎI: Spec đủ specific để Generator viết EP51 quality không? Trả lời 50 từ tiếng Việt KHONG DAU. Verdict YES/NEEDS-MORE/NO."
  try {
    $body = @{ model = "gemma2:9b"; prompt = $prompt; stream = $false; options = @{ temperature = 0.5; num_predict = 120 } } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Log "Ollama EP51 chapter_contract review:"
    Log $r.response.Trim()
  } catch { Log "Ollama ERR: $($_.Exception.Message)" }
  
  Start-Sleep -Seconds 120
}
