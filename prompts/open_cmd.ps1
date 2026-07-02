# open_cmd.ps1 — mo MOT phien Claude cho dung 1 CMD (seed vai tro + memory).
# Dung: .\prompts\open_cmd.ps1 BUILD | ARCH | QA | RELEASE
param([Parameter(Mandatory)][ValidateSet('BUILD','ARCH','QA','RELEASE')]$Role)
$repo = Split-Path $PSScriptRoot -Parent
$map = @{ BUILD='CMD_BUILD'; ARCH='CMD_ARCH_AUDIT'; QA='CMD_QA_AUDIT'; RELEASE='CMD_RELEASE_AUDIT' }
$name = $map[$Role]
# Seed ngan: bao Claude doc file vai tro (memory/chuc nang) + protocol, roi cho lenh.
$seed = "Ban la $name trong pipeline SVHMP. Doc prompts/$name.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu tuyet doi. Xac nhan vai tro va cho lenh."
# Mo cua so PowerShell moi -> cd repo -> chay claude voi seed (claude auto-load CLAUDE.md/memory cua repo).
Start-Process powershell -ArgumentList @(
  '-NoExit','-ExecutionPolicy','Bypass','-Command',
  "Set-Location '$repo'; claude `"$seed`""
)
Write-Host "Da mo $name (cua so moi)."
