curl.exe `
  --connect-timeout 300 `
  --data inactive `
  --header 'Content-Type: text/plain' `
  --request PUT `
  http://localhost:8080/api/session
