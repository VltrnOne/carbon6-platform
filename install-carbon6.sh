#!/bin/bash

################################################################################
# Carbon6 OiS - Agentic-First OS-Style Installer
# Main Installation Script
# Version: 1.0.0
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Installation state
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$INSTALL_DIR/.install-state.json"
LOG_FILE="$INSTALL_DIR/installation.log"

# Create directories
mkdir -p "$INSTALL_DIR/logs" "$INSTALL_DIR/scripts"

################################################################################
# Logging
################################################################################

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

################################################################################
# Display
################################################################################

print_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
 ██████╗ █████╗ ██████╗ ██████╗  ██████╗ ███╗   ██╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝
██║     ███████║██████╔╝██████╔╝██║   ██║██╔██╗ ██║███████╗
██║     ██╔══██║██╔══██╗██╔══██╗██║   ██║██║╚██╗██║██╔═══██╗
╚██████╗██║  ██║██║  ██║██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝

         OPERATIONAL INTELLIGENCE SYSTEM
         Agentic-First Installation v1.0.0
EOF
    echo -e "${NC}\n"
}

print_agent() {
    case $1 in
        "PRAXIS") echo -e "${MAGENTA}👤 PRAXIS:${NC} $2" ;;
        "SCOUT") echo -e "${GREEN}👤 SCOUT:${NC} $2" ;;
        "GENESIS") echo -e "${CYAN}👤 GENESIS:${NC} $2" ;;
        "SOVEREIGN") echo -e "${BLUE}👤 SOVEREIGN:${NC} $2" ;;
    esac
}

################################################################################
# Main Menu
################################################################################

show_menu() {
    print_banner
    
    echo -e "${WHITE}INSTALLATION OPTIONS:${NC}\n"
    echo "  1) Full Installation (Recommended) - 40-65 minutes"
    echo "  2) Quick Start (Developer Mode) - 25 minutes"
    echo "  3) Custom Installation (Advanced)"
    echo ""
    echo "  9) View Documentation"
    echo "  0) Exit"
    echo -e "\n${WHITE}═══════════════════════════════════════════════════════════${NC}\n"
    
    read -p "Select option: " choice
    
    case $choice in
        1) full_installation ;;
        2) quick_start ;;
        3) custom_installation ;;
        9) view_docs ;;
        0) exit 0 ;;
        *) echo "Invalid option"; sleep 2; show_menu ;;
    esac
}

################################################################################
# Installation Modes
################################################################################

full_installation() {
    print_banner
    print_agent "GENESIS" "Initializing full production installation..."
    echo ""
    
    echo "This will install:"
    echo "  ✓ System prerequisites (Homebrew, Node.js, PostgreSQL, Redis)"
    echo "  ✓ Carbon6 platform with all features"
    echo "  ✓ 462 Council agents"
    echo "  ✓ 88x™ Chairman Console"
    echo "  ✓ Production monitoring & backups"
    echo ""
    
    read -p "Continue? [y/N]: " confirm
    [[ ! $confirm =~ ^[Yy]$ ]] && show_menu && return
    
    bash "$INSTALL_DIR/scripts/install-part-0.sh" && \
    bash "$INSTALL_DIR/scripts/install-part-1.sh" && \
    bash "$INSTALL_DIR/scripts/install-part-2.sh" && \
    bash "$INSTALL_DIR/scripts/install-part-3.sh"
    
    installation_complete
}

quick_start() {
    print_banner
    print_agent "SCOUT" "Setting up developer environment..."
    echo ""
    
    echo "Quick Start Mode:"
    echo "  • SQLite database"
    echo "  • In-memory cache"
    echo "  • Single instance"
    echo "  • Core features only"
    echo ""
    
    read -p "Continue? [y/N]: " confirm
    [[ ! $confirm =~ ^[Yy]$ ]] && show_menu && return
    
    # Set dev mode
    export INSTALL_MODE="developer"
    
    bash "$INSTALL_DIR/scripts/install-part-0.sh" && \
    bash "$INSTALL_DIR/scripts/install-part-2.sh"
    
    installation_complete
}

custom_installation() {
    print_banner
    print_agent "SCOUT" "Let's customize your installation..."
    echo ""
    
    # Installation mode
    echo "Select installation mode:"
    echo "  1) Developer (SQLite, fast)"
    echo "  2) Production (PostgreSQL, full features)"
    echo "  3) Docker (containerized)"
    read -p "Mode [1-3]: " mode_choice
    
    # Components
    echo -e "\nSelect components:"
    echo "  [1] Core Platform (required)"
    echo "  [2] Connector Protocol"
    echo "  [3] Web Terminal"
    echo "  [4] Council Integration (462 agents)"
    echo "  [5] 88x™ Chairman Console"
    read -p "Enter component numbers (e.g., 12345): " components
    
    # Run installation
    export INSTALL_MODE=$mode_choice
    export INSTALL_COMPONENTS=$components
    
    bash "$INSTALL_DIR/scripts/install-part-0.sh"
    bash "$INSTALL_DIR/scripts/install-part-1.sh"
    bash "$INSTALL_DIR/scripts/install-part-2.sh"
    [ "$components" =~ "4" ] && bash "$INSTALL_DIR/scripts/install-part-3.sh"
    
    installation_complete
}

installation_complete() {
    print_banner
    print_agent "SOVEREIGN" "Installation complete!"
    echo ""
    echo -e "${GREEN}✓ Carbon6 OiS is now operational${NC}\n"
    echo "Access your system:"
    echo "  • Platform: http://localhost:3006"
    echo "  • Terminal: http://localhost:3006/terminal"
    echo "  • Console: http://localhost:3006/console"
    echo ""
    read -p "Press Enter to exit..."
    exit 0
}

view_docs() {
    print_banner
    echo "Documentation:"
    echo "  • Complete Guide: CARBON6_OIS_COMPLETE_INSTALLATION_GUIDE.md"
    echo "  • Part 0: CARBON6_OIS_INSTALLER_PART_0.md"
    echo "  • Part 1: CARBON6_OIS_INSTALLER_PART_1.md"
    echo "  • Part 2: CARBON6_OIS_INSTALLER_PART_2.md"
    echo "  • Part 3: CARBON6_OIS_INSTALLER_PART_3.md"
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

################################################################################
# Main
################################################################################

main() {
    log "Carbon6 OiS Installer started"
    
    # Check if scripts exist
    if [ ! -d "$INSTALL_DIR/scripts" ]; then
        echo -e "${RED}Error: Installation scripts not found${NC}"
        echo "Please ensure all installation files are present."
        exit 1
    fi
    
    show_menu
}

trap 'echo -e "\n${RED}Installation interrupted${NC}"; exit 1' INT TERM

main
