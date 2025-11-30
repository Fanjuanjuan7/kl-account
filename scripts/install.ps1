param(
    [string]$Python = "python"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

& $Python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
Write-Host "installed. activate with: .\.venv\Scripts\Activate.ps1"
