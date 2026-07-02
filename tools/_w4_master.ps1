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
[CF3]::SetCurrentConsoleFontEx([CF3]::GetStdHandle(-11), $false, [ref]$f) | Out-Null$Host.UI.RawUI.WindowTitle = "MASTER-INT"
$logFile = "C:\tmp\svhmp_review\runtime\realtime_logs\master.log"
function Log([string]$msg) { Write-Host $msg; [System.IO.File]::AppendAllText($logFile, $msg + "`n", [System.Text.UTF8Encoding]::new($false)) }
Set-Location C:\tmp\svhmp_review
$env:PYTHONIOENCODING = "utf-8"
Log "=== MASTER INTEGRATION TEST (C4 audio + C5 all audits) ==="
$c = 0
while ($true) {
  $c++
  Log ""
  Log "[$([DateTime]::Now.ToString('HH:mm:ss'))] Cycle $c — Audio render verify"
  
  # Check episode_tts_ready.md exists for all 50 EPs
  $readyCount = 0
  for ($ep = 1; $ep -le 50; $ep++) {
    if (Test-Path "output\ep_$('{0:D2}' -f $ep)\episode_tts_ready.md") { $readyCount++ }
  }
  Log "episode_tts_ready.md: $readyCount/50 EPs preprocessed"
  
  # Count pause markers + dialogue segments in tts_ready files
  $totalRevealPause = 0; $totalEmDashPause = 0; $totalDialogue = 0
  for ($ep = 1; $ep -le 50; $ep++) {
    $f = "output\ep_$('{0:D2}' -f $ep)\episode_tts_ready.md"
    if (Test-Path $f) {
      $t = Get-Content $f -Raw -Encoding UTF8
      $totalRevealPause += ([regex]::Matches($t, "\[pause:1000ms\]")).Count
      $totalEmDashPause += ([regex]::Matches($t, "\[pause:250ms\]")).Count
      $totalDialogue += ([regex]::Matches($t, "\[DIALOGUE_SEG_START\]")).Count
    }
  }
  Log "TTS adapter output: reveal_pauses=$totalRevealPause em_dash_pauses=$totalEmDashPause dialogue_segs=$totalDialogue"
  
  # Run ALL 15 audits summary
  Log ""
  Log "--- 15 AUDITS SUMMARY ---"
  $audits = @("audit_tilde_eol", "audit_short_eol", "audit_short_start", "audit_anaphora_consecutive",
              "audit_r68_to_r73", "audit_phrase_repetition", "audit_aesthetic_5_subdim",
              "audit_bimodal_sentence", "audit_continuity_cross_ep", "audit_dialogue_hierarchy",
              "audit_hidden_bugs", "audit_ngan_opening_template", "audit_pronoun_pov",
              "audit_story_mode", "audit_style_stats")
  foreach ($a in $audits) {
    $r = python tools\$a.py --summary 2>&1 | Select-String "SUMMARY|HIDDEN BUGS FOUND|REVEAL" | Select-Object -First 1 | Out-String
    Log "$a : $($r.Trim())"
  }
  
  Start-Sleep -Seconds 180
}
