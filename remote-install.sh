#!/bin/bash
################################################################################
# Carbon6 OiS Remote Installer
# One-liner: curl -sSL https://install.carbon6.io/install.sh | bash
################################################################################

set -e

REPO_URL="https://github.com/VltrnOne/carbon6-platform.git"
INSTALL_DIR="$HOME/Carbon6/platform"

echo "🚀 Carbon6 OiS Remote Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This installer currently supports macOS only"
    echo "   Linux support coming soon!"
    exit 1
fi

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MACOS_VERSION" -lt 12 ]; then
    echo "❌ Error: macOS 12 (Monterey) or later required"
    echo "   Current: macOS $MACOS_VERSION"
    exit 1
fi

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    echo "📂 Existing installation found at $INSTALL_DIR"
    read -p "   Update existing installation? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$INSTALL_DIR"
        git pull origin main
    else
        echo "   Installation cancelled"
        exit 0
    fi
else
    echo "📥 Downloading Carbon6 OiS to $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Make installer executable
chmod +x install-carbon6.sh
chmod +x scripts/*.sh

# Run installation
echo ""
echo "✅ Ready to install!"
echo ""
read -p "Start installation now? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    ./install-carbon6.sh
else
    echo ""
    echo "Installation files ready at: $INSTALL_DIR"
    echo "Run anytime with: cd $INSTALL_DIR && ./install-carbon6.sh"
fi
