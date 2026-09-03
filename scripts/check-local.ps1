$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$pythonPath = Join-Path $PWD ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) { throw "Run uv sync --locked --extra dev first." }
& $pythonPath -m alembic current
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $pythonPath -m alembic check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($url in @("http://127.0.0.1:8000/health","http://127.0.0.1:8000/ready","http://127.0.0.1:8000/api/v1/settings","http://127.0.0.1:8501/_stcore/health")) {
    Write-Output $url
    Invoke-RestMethod -Uri $url -TimeoutSec 10 | ConvertTo-Json -Compress
}
Write-Output "Local checks passed. No Gemini generation request was made."
