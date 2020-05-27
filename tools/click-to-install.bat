@echo off

cd ..\

echo Activating environment
call .\venv\Scripts\activate

set "SDKFolder=C:\Program Files (x86)\Windows Kits\10\Redist\10.0.19041.0\ucrt\DLLs\x64"

if exist "%SDKFolder%" (
    echo Adding Windows SDK to path
    set "PATH=%PATH%;%SDKFolder%"
) else (
    echo Windows SDK not found. Compilation might fail.
)

echo Compiling
fbs freeze

echo Creating installer
fbs installer

echo Running installer
.\target\ImageWAOSetup
