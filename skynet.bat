@echo off
cls

chcp 65001 > nul
setlocal EnableDelayedExpansion

REM Get ESC character
for /f %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"

REM -----------------------------
REM Check Docker Daemon status
set DOCKER_STATUS=!ESC![31mSTOPPED!ESC![0m
docker info > nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "DOCKER_STATUS=!ESC![92mRUNNING!ESC![0m"
)


REM -----------------------------
REM Check Skynet Container status
set CONTAINER_EXISTS=!ESC![31mDOWN!ESC![0m
set CONTAINER_RUNNING=false
for /f %%i in ('docker ps -q -f "name=skynet" 2^>nul') do (
    set CONTAINER_EXISTS=!ESC![92mACTIVE!ESC![0m
    set CONTAINER_RUNNING=true
)

if "!CONTAINER_RUNNING!"=="false" (
    for /f %%i in ('docker ps -aq -f "name=skynet" 2^>nul') do (
        set CONTAINER_EXISTS=!ESC![31mSTOPPED!ESC![0m
    )
)

REM -----------------------------
REM Check npm version
set NPM_VERSION=!ESC![31mUNKNOWN!ESC![0m
if "!CONTAINER_RUNNING!"=="true" (
    for /f %%i in ('docker exec skynet npm --version 2^>nul') do set NPM_VERSION=!ESC![92m%%i!ESC![0m
)

echo:
echo     Docker: !DOCKER_STATUS! ^| Skynet: !CONTAINER_EXISTS! ^| NPM: !NPM_VERSION!

if "!CONTAINER_RUNNING!"=="false" (
    echo:
    echo     !ESC![31m^[ERROR^]!ESC![0m: Container is not running.
    exit /b 1
) else if "!NPM_VERSION!"=="!ESC![31mUNKNOWN!ESC![0m" (
    echo:
    echo     !ESC![31m^[ERROR^]!ESC![0m: NPM version is unknown.
    exit /b 1
)

REM -----------------------------
REM Beautiful Banner
echo:
echo:
echo !ESC![91m    ███████╗██╗  ██╗██╗   ██╗███╗   ██╗███████╗████████╗ !ESC![0m
echo !ESC![91m    ██╔════╝██║ ██╔╝╚██╗ ██╔╝████╗  ██║██╔════╝╚══██╔══╝ !ESC![0m
echo !ESC![91m    ███████╗█████╔╝  ╚████╔╝ ██╔██╗ ██║█████╗     ██║    !ESC![0m
echo !ESC![91m    ╚════██║██╔═██╗   ╚██╔╝  ██║╚██╗██║██╔══╝     ██║    !ESC![0m
echo !ESC![91m    ███████║██║  ██╗   ██║   ██║ ╚████║███████╗   ██║    !ESC![0m
echo !ESC![91m    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝    !ESC![0m
echo:
echo:

REM -----------------------------
REM Start bash session
docker exec -it skynet bash
