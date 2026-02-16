#!/bin/bash

################################################################################
# Carbon6 OiS - macOS Single-Click Installer (Shared/Network)
#
# Double-click this file to install Carbon6 for all users on your Mac
# with network accessibility.
#
# Installation Location: /opt/carbon6
# Data Location: /var/lib/carbon6
# Network Access: http://YOUR-MAC-NAME.local:3006
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
echo -e "${BLUE}║     CARBON6 OiS - SINGLE-CLICK INSTALLER                  ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║     Multi-User | Network-Ready | Centralized             ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This installer will:${NC}"
echo "  • Install Carbon6 to /opt/carbon6 (accessible to all users)"
echo "  • Configure for network access from other computers"
echo "  • Install PostgreSQL, Redis, and all dependencies"
echo "  • Create a system-wide 'carbon6' command"
echo ""
echo -e "${YELLOW}Installation time: 15-20 minutes${NC}"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."

# Download installer
echo ""
echo -e "${BLUE}[1/2] Downloading installer...${NC}"
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-macos-shared.sh -o /tmp/carbon6-installer.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Download failed. Please check your internet connection.${NC}"
    echo ""
    read -p "Press ENTER to close..."
    exit 1
fi

echo -e "${GREEN}✓ Installer downloaded${NC}"

# Make executable
chmod +x /tmp/carbon6-installer.sh

# Run with sudo (will prompt for password)
echo ""
echo -e "${BLUE}[2/2] Running installer...${NC}"
echo -e "${YELLOW}⚠ You will be prompted for your Mac password${NC}"
echo ""

sudo bash /tmp/carbon6-installer.sh

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
    echo -e "     ${GREEN}carbon6${NC}"
    echo ""
    echo "  2. Access from this Mac:"
    echo -e "     ${GREEN}http://localhost:3006${NC}"
    echo ""
    echo "  3. Access from other computers:"
    echo -e "     ${GREEN}http://$(hostname):3006${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Installation failed${NC}"
    echo ""
    echo "Check the error messages above for details."
    echo ""
fi

echo ""
read -p "Press ENTER to close..."
