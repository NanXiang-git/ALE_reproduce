@echo off
setlocal
set "FOUND="
for %%P in (
  "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
  "C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe"
  "C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\AfterFX.exe"
) do (
  if exist %%~P (
    set "FOUND=%%~P"
    goto :launch
  )
)
echo Adobe After Effects was not found in the expected locations.
exit /b 1

:launch
start "" "%FOUND%"
