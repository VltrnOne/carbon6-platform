#!/bin/bash

################################################################################
# Carbon6 OiS - macOS Single-Click Installer (Personal)
#
# Double-click this file to install Carbon6 in your home directory
# for personal development use.
#
# Installation Location: ~/Carbon6
# Access: localhost only (this Mac only)
################################################################################

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║     CARBON6 OiS - PERSONAL INSTALLER                      ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║     Single User | Development | Fast Setup               ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This installer will:${NC}"
echo "  • Install Carbon6 to ~/Carbon6 (your home directory)"
echo "  • Install PostgreSQL, Redis, and all dependencies"
echo "  • Configure for localhost access only"
echo ""
echo -e "${YELLOW}Installation time: 15-20 minutes (first run) or 2-5 min (cached)${NC}"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone repository
echo ""
echo -e "${BLUE}[1/2] Downloading Carbon6...${NC}"
git clone --depth 1 https://github.com/VltrnOne/carbon6-platform.git 2>&1 | grep -v "Cloning into"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Download failed. Please check your internet connection.${NC}"
    echo ""
    read -p "Press ENTER to close..."
    exit 1
fi

echo -e "${GREEN}✓ Downloaded${NC}"

# Run installer
echo ""
echo -e "${BLUE}[2/2] Running installer...${NC}"
cd carbon6-platform
./install-carbon6-fast.sh

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║     ✓ INSTALLATION COMPLETE!                             ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo ""
    echo "  1. Start server:"
    echo -e "     ${GREEN}cd ~/Carbon6 && npm run dev${NC}"
    echo ""
    echo "  2. Access:"
    echo -e "     ${GREEN}http://localhost:3006${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Installation failed${NC}"
    echo ""
    echo "Check the error messages above for details."
    echo ""
fi

# Cleanup
cd ~
rm -rf "$TEMP_DIR"

echo ""
read -p "Press ENTER to close..."
