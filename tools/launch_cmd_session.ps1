# launch_cmd_session.ps1 — 1-click launcher cho CMD_BUILD / CMD_BUILD_2 / CMD_AUDIT.
# Desktop .bat goi script nay voi -Role, script doc dung PROMPT_CMD_<ROLE>.txt (UTF-8, tieng
# Viet co dau) roi mo claude ngay voi prompt do nap san, khong can copy-paste tay.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('BUILD', 'BUILD_2', 'AUDIT')]
    [string]$Role
)

$Repo = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"
$PromptFile = Join-Path $Repo "PROMPT_CMD_$Role.txt"
$Title = "CMD_$Role"

$Host.UI.RawUI.WindowTitle = "$Title - SVHMP_Studio"

if (-not (Test-Path $Repo)) {
    Write-Host "[ERR] Repo path khong ton tai: $Repo" -ForegroundColor Red
    Read-Host "Enter de dong"
    exit 1
}
if (-not (Test-Path $PromptFile)) {
    Write-Host "[ERR] Prompt file khong ton tai: $PromptFile" -ForegroundColor Red
    Read-Host "Enter de dong"
    exit 1
}

Set-Location $Repo
$prompt = Get-Content -Raw -Encoding UTF8 $PromptFile

Write-Host "=== $Title ready - dang mo claude voi prompt nap san (based on repo) ===" -ForegroundColor Cyan
Write-Host "Repo: $Repo"
Write-Host "Prompt: $PromptFile ($($prompt.Length) chars)"
Write-Host ""

if ($env:SVHMP_LAUNCH_DRYRUN -eq '1') {
    Write-Host "[DRY-RUN] would exec: claude <prompt $($prompt.Length) chars>" -ForegroundColor Yellow
} else {
    claude $prompt
}
