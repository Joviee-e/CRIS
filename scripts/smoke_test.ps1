# scripts/smoke_test.ps1
# run from repo root, venv active
$login = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/api/auth/login `
  -ContentType 'application/json' `
  -Body '{"email":"admin@example.com","password":"admin123"}'
$token = $login.access
Write-Output "Got token length: $($token.Length)"

$body = @{
  sr_no = 1
  purpose = "Smoke Test ID Card"
  department = "Civil Admin"
  emp_no = "SMOKE001"
  emp_name = "Smoke Tester"
  designation = "Tester"
  remarks = "smoke test run"
} | ConvertTo-Json

$submit = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/api/applications/ `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $body

$appId = $submit.id
Write-Output "Created app id: $appId"

Invoke-RestMethod -Method PATCH -Uri "http://127.0.0.1:5000/api/applications/$appId/verify" `
  -Headers @{ Authorization = "Bearer $token" } | Write-Output

Start-Sleep -Seconds 1

Invoke-RestMethod -Method PATCH -Uri "http://127.0.0.1:5000/api/applications/$appId/approve" `
  -Headers @{ Authorization = "Bearer $token" } | Write-Output

Write-Output "Smoke test complete."
