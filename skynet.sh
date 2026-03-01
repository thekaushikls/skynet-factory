#!/bin/bash
clear

# Get ESC character
ESC=$(printf "\033")

# -----------------------------
# Check Docker Daemon status
DOCKER_STATUS="${ESC}[31mSTOPPED${ESC}[0m"
if docker info > /dev/null 2>&1; then
    DOCKER_STATUS="${ESC}[92mRUNNING${ESC}[0m"
fi

# -----------------------------
# Check Skynet Container status
CONTAINER_EXISTS="${ESC}[31mDOWN${ESC}[0m"
CONTAINER_RUNNING=false
if docker ps -q -f "name=skynet" | grep -q .; then
    CONTAINER_EXISTS="${ESC}[92mACTIVE${ESC}[0m"
    CONTAINER_RUNNING=true
fi

if [ "$CONTAINER_RUNNING" = false ]; then
    if docker ps -aq -f "name=skynet" | grep -q .; then
        CONTAINER_EXISTS="${ESC}[31mSTOPPED${ESC}[0m"
    fi
fi

# -----------------------------
# Check npm version
NPM_VERSION="${ESC}[31mUNKNOWN${ESC}[0m"

if [ "$CONTAINER_RUNNING" = true ]; then
    NPM_VER=$(docker exec skynet npm --version 2>/dev/null)
    if [ -n "$NPM_VER" ]; then
        NPM_VERSION="${ESC}[92m${NPM_VER}${ESC}[0m"
    fi
fi

echo
echo -e "    Docker: $DOCKER_STATUS | Skynet: $CONTAINER_EXISTS | NPM: $NPM_VERSION"

if [ "$CONTAINER_RUNNING" = false ]; then
    echo
    echo -e "    ${ESC}[31m[ERROR]${ESC}[0m: Container is not running."
    exit 1

# Check if NPM version is unknown
elif [ "$NPM_VERSION" = "${ESC}[31mUNKNOWN${ESC}[0m" ]; then
    echo
    echo -e "    ${ESC}[31m[ERROR]${ESC}[0m: NPM version is unknown."
    exit 1
fi

# -----------------------------
# Beautiful Banner
echo 
echo 
echo -e "${ESC}[91m    ███████╗██╗  ██╗██╗   ██╗███╗   ██╗███████╗████████╗ ${ESC}[0m"
echo -e "${ESC}[91m    ██╔════╝██║ ██╔╝╚██╗ ██╔╝████╗  ██║██╔════╝╚══██╔══╝ ${ESC}[0m"
echo -e "${ESC}[91m    ███████╗█████╔╝  ╚████╔╝ ██╔██╗ ██║█████╗     ██║    ${ESC}[0m"
echo -e "${ESC}[91m    ╚════██║██╔═██╗   ╚██╔╝  ██║╚██╗██║██╔══╝     ██║    ${ESC}[0m"
echo -e "${ESC}[91m    ███████║██║  ██╗   ██║   ██║ ╚████║███████╗   ██║    ${ESC}[0m"
echo -e "${ESC}[91m    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝    ${ESC}[0m"
echo 
echo 

# -----------------------------
# Start bash session
docker exec -it skynet bash
