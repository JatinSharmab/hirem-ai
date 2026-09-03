$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
foreach ($port in @(8000, 8501)) {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
        $insideProject = $processInfo.ExecutablePath -and $processInfo.ExecutablePath.StartsWith(
            $projectRoot + "\", [System.StringComparison]::OrdinalIgnoreCase)
        $expectedServer = $processInfo.CommandLine -match '(uvicorn apps\.api\.main:app|streamlit run apps/ui/Home\.py)'
        if ($insideProject -and $expectedServer) {
            Stop-Process -Id $processInfo.ProcessId
            Write-Output "Stopped HireMe AI on port $port."
        } else {
            Write-Output "Port $port belongs to another process; left it running."
        }
    }
}
