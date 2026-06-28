chcp 65001 | Out-Null
$Host.UI.RawUI.WindowTitle = "OLLAMA-SKEPTIC"
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
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\ollama.log"
function Log([string]$msg) {
  Write-Host $msg
  [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false))
}

Log ""
Log "=== OLLAMA SKEPTIC v4 — ROTATE ALL EP01-50 ==="

$systemPrompt = "You are Adversarial Skeptic for SVHMP Vietnamese horror narration. ATTACK Claude findings. Cite specific quotes. Reply 50 words ENGLISH only. Verdict: PASS / REVIEW / FAIL."

$cycle = 0
while ($true) {
  $cycle++
  Log ""
  Log "===== CYCLE $cycle ($([DateTime]::Now.ToString('HH:mm:ss'))) ====="
  
  $passCount = 0; $reviewCount = 0; $failCount = 0
  
  for ($ep = 1; $ep -le 50; $ep++) {
    $epStr = "{0:D2}" -f $ep
    $epFile = "C:\tmp\svhmp_review\output\ep_$epStr\episode.md"
    if (-not (Test-Path $epFile)) { continue }
    
    $epText = Get-Content $epFile -Raw -Encoding UTF8
    # Skip yaml metadata, take 1800 chars body
    if ($epText -match '(?s)```.*?```\s*---\s*(.+)$') {
      $epBody = $matches[1].Substring(0, [Math]::Min(1800, $matches[1].Length))
    } else {
      $epBody = $epText.Substring(0, [Math]::Min(1800, $epText.Length))
    }
    
    $userPrompt = "EP$epStr SVHMP:`n`n$epBody`n`nFind 1-2 issues: word repetition, anaphora chains, logic errors, Ngoc Ngan style. Reply ENGLISH 40 words + verdict."
    
    try {
      $body = @{
        model = "gemma2:9b"
        system = $systemPrompt
        prompt = $userPrompt
        stream = $false
        options = @{ temperature = 0.5; num_predict = 120 }
      } | ConvertTo-Json -Compress -Depth 5
      
      $resp = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
      $verdict = "?"
      if ($resp.response -match "FAIL") { $verdict = "FAIL"; $failCount++ }
      elseif ($resp.response -match "REVIEW") { $verdict = "REVIEW"; $reviewCount++ }
      elseif ($resp.response -match "PASS") { $verdict = "PASS"; $passCount++ }
      
      Log "EP$epStr : $verdict | $(($resp.response -replace '`r?`n+', ' ').Substring(0, [Math]::Min(120, $resp.response.Length)))..."
    } catch {
      Log "EP$epStr : ERROR $($_.Exception.Message)"
    }
  }
  
  Log ""
  Log "→ CYCLE $cycle SUMMARY: PASS=$passCount REVIEW=$reviewCount FAIL=$failCount"
  Log "Sleep 60s..."
  Start-Sleep -Seconds 60
}





