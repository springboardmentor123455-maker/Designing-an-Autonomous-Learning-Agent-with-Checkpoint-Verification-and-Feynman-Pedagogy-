# PowerShell script to run all tests
Write-Host "Running all tests..." -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Running installation test..." -ForegroundColor Yellow
python test_installation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation test failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Running component tests..." -ForegroundColor Yellow
python test_components.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Component tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Running workflow test..." -ForegroundColor Yellow
python test_workflow.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Workflow test failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All tests passed!" -ForegroundColor Green
