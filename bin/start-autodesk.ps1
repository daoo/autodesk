$env:AUTODESK_ADDRESS = "127.0.0.1"
$env:AUTODESK_PORT = "7380"
$env:AUTODESK_CONFIG = ".\\config\\ft232h.yml"
$env:AUTODESK_DATABASE = "$HOME\AppData\Local\autodesk\autodesk.db"

uv run autodesk
