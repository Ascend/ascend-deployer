python downloader/downloader_ui.py
if errorlevel 1 (
    exit 0
)
python downloader/downloader.py
python downloader/other_downloader.py
TIMEOUT /T 20
