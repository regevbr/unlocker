@echo off
setlocal ENABLEEXTENSIONS
echo Get macOS VMware Tools 3.0.3
echo ===============================
echo (c) Dave Parsons 2011-21

net session >NUL 2>&1
if %errorlevel% neq 0 (
    echo Administrator privileges required! 
    exit
)

pushd %~dp0

echo.
set KeyName="HKLM\SOFTWARE\Wow6432Node\VMware, Inc.\VMware Player"
for /F "tokens=2*" %%A in ('REG QUERY %KeyName% /v InstallPath') do set InstallPath=%%B
echo VMware is installed at: %InstallPath%
for /F "tokens=2*" %%A in ('REG QUERY %KeyName% /v ProductVersion') do set ProductVersion=%%B
echo VMware product version: %ProductVersion%

echo Getting VMware Tools...
.\python-win-embed-amd64\python.exe gettools.py

popd

echo Finished!
