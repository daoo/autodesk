$env:AUTODESK_ADDRESS = "127.0.0.1"
$env:AUTODESK_PORT = "8080"
$env:AUTODESK_CONFIG = ".\\config\\ft232h.yml"
$env:AUTODESK_DATABASE = "C:\\temp\\autodesk.db"

. .\venv\Scripts\activate.ps1

python.exe -m autodesk.program
