@echo off
set SOFFICE=C:\Program Files\LibreOffice\program\soffice.exe
if exist "%SOFFICE%" start "" "%SOFFICE%" %*
if not exist "%SOFFICE%" echo LibreOffice is not installed yet. Run the Stage 4 provisioning plan.
exit /b 0
