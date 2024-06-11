@echo off
setlocal enabledelayedexpansion

rem Prompt for user input
set /p password=Enter user password: 
set /p local_dir=Enter local dist directory: 
set /p remote_dir=Enter remote push directory: 

rem Build project
echo Running npm run build...
npm run build
if %errorlevel% neq 0 (
    echo Build failed, exiting.
    exit /b %errorlevel%
)

rem Push dist directory to remote server
echo Pushing dist directory to remote server...
echo %password% | scp -r %local_dir% root@8.138.124.53:%remote_dir%
if %errorlevel% neq 0 (
    echo SCP failed, exiting.
    exit /b %errorlevel%
)

rem Run remote script
echo Running remote script...
echo %password% | ssh root@8.138.124.53 "bash %remote_dir%/nginx2.sh"
if %errorlevel% neq 0 (
    echo SSH command failed, exiting.
    exit /b %errorlevel%
)

echo Done.
pause
