$remote = qwinsta.exe $env:UserName | Out-String
if ($remote.contains("rdp-tcp")) {
  Write-Host "RDP session, exiting."
} else {
  curl.exe `
    --connect-timeout 300 `
    --data inactive `
    --header 'Content-Type: text/plain' `
    --request PUT `
    http://localhost:7380/api/session
}
