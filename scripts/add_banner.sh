#!/bin/bash
# Setup terminal banner for Skynet container
# This script modifies ~/.bashrc to add custom ASCII banner

BASHRC="$HOME/.bashrc"

# Check if banner is already installed
if grep -q "skynet_banner()" "$BASHRC" 2>/dev/null; then
    echo "Terminal banner already installed, skipping..."
    exit 0
fi

echo "Installing Skynet terminal banner..."

# Append the skynet_banner function to bashrc
cat >> "$BASHRC" << 'EOF'

# Skynet Terminal Banner
skynet_banner() {
    # Use the original clear to avoid recursion
    command clear
    ESC=$(printf "\033")
    
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
}

# Override clear command to show banner
clear() {
    command clear    # call the original clear
    skynet_banner    # print ASCII on top
}

# Override Ctrl+L keybinding
bind -x '"\C-l":clear'

EOF
echo "Terminal banner installed successfully!"
