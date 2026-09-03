param([ValidateSet("api", "ui", "check")][string]$Service = "api")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$pythonPath = Join-Path $PWD ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    throw "Missing .venv. Run: uv sync --locked --extra dev"
}
if ($Service -eq "api") {
    & $pythonPath -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
} elseif ($Service -eq "ui") {
    & $pythonPath -m streamlit run apps/ui/Home.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
} else {
    & $pythonPath -m ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $pythonPath -m ruff format --check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $pythonPath -m mypy src/hireme_ai
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $pythonPath -m pytest
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $pythonPath evaluation/run_evaluation.py
}
exit $LASTEXITCODE
