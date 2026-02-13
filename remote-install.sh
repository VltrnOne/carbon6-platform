#!/bin/bash
#
# Carbon6 Platform - Remote Installer
# One-line install: curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
#
# Part of VLTRN Council - Carbon Domain
# Installs: SDK + Platform + Config + Dependencies
#

set -e

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/carbon6-platform"
SDK_DIR="$HOME/carbon-collective"
PLATFORM_DIR="$HOME/Carbon6"
GITHUB_ORG="VltrnOne"

# Banner
echo ""
echo -e "${GRAY}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GRAY}║                                                           ║${NC}"
echo -e "${GRAY}║     ${BLUE}CARBON${GRAY}[${BLUE}6${GRAY}]${NC} ${GRAY}PLATFORM                                  ║${NC}"
echo -e "${GRAY}║                                                           ║${NC}"
echo -e "${GRAY}║     ${NC}Lead. Mentor. Build.${GRAY}                              ║${NC}"
echo -e "${GRAY}║     ${NC}Pressure Creates.${GRAY}                                 ║${NC}"
echo -e "${GRAY}║                                                           ║${NC}"
echo -e "${GRAY}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Dependency checks
echo -e "${GRAY}[1/7] Checking system dependencies...${NC}"

# Check for Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is required but not installed.${NC}"
    echo -e "${YELLOW}Install from: https://git-scm.com${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Git found${NC}"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is required but not installed.${NC}"
    echo -e "${YELLOW}Install from: https://nodejs.org${NC}"
    exit 1
fi
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}✗ Node.js 18+ required (found v$(node -v))${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Node.js $(node -v)${NC}"

# Check for package manager (prefer bun > npm)
if command -v bun &> /dev/null; then
    PKG_MANAGER="bun"
    echo -e "${GREEN}  ✓ bun $(bun -v)${NC}"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
    echo -e "${YELLOW}  ⚠ npm found (bun recommended for performance)${NC}"
    echo -e "${GRAY}    Install bun: curl -fsSL https://bun.sh/install | bash${NC}"
else
    echo -e "${RED}✗ npm or bun is required${NC}"
    exit 1
fi

# Check for gh CLI (optional but recommended)
if command -v gh &> /dev/null; then
    USE_GH=true
    echo -e "${GREEN}  ✓ GitHub CLI found${NC}"
else
    USE_GH=false
    echo -e "${GRAY}  • GitHub CLI not found (will use git clone)${NC}"
fi

echo ""

# Clone/Update Carbon Collective SDK
echo -e "${GRAY}[2/7] Installing Carbon Collective SDK...${NC}"

if [ -d "$SDK_DIR/.git" ]; then
    echo -e "${GRAY}  Updating existing SDK installation...${NC}"
    cd "$SDK_DIR"
    git pull origin main
else
    echo -e "${GRAY}  Cloning carbon-collective repository...${NC}"
    if [ "$USE_GH" = true ]; then
        gh repo clone "$GITHUB_ORG/carbon-collective" "$SDK_DIR"
    else
        git clone "https://github.com/$GITHUB_ORG/carbon-collective.git" "$SDK_DIR"
    fi
fi

# Install SDK dependencies
echo -e "${GRAY}  Installing SDK dependencies...${NC}"
cd "$SDK_DIR/sdk"

if [ "$PKG_MANAGER" = "bun" ]; then
    bun install --silent
    echo -e "${GREEN}  ✓ SDK dependencies installed${NC}"
else
    npm install --silent
    echo -e "${GREEN}  ✓ SDK dependencies installed${NC}"
fi

echo ""

# Clone/Update Carbon6 Platform
echo -e "${GRAY}[3/7] Installing Carbon6 Platform...${NC}"

if [ -d "$PLATFORM_DIR/.git" ]; then
    echo -e "${GRAY}  Updating existing platform installation...${NC}"
    cd "$PLATFORM_DIR"
    git pull origin main
else
    echo -e "${GRAY}  Cloning Carbon6 repository...${NC}"
    if [ "$USE_GH" = true ]; then
        gh repo clone "$GITHUB_ORG/Carbon6" "$PLATFORM_DIR"
    else
        git clone "https://github.com/$GITHUB_ORG/Carbon6.git" "$PLATFORM_DIR"
    fi
fi

# Install platform dependencies
echo -e "${GRAY}  Installing platform dependencies...${NC}"
cd "$PLATFORM_DIR"

if [ "$PKG_MANAGER" = "bun" ]; then
    bun install --silent
    echo -e "${GREEN}  ✓ Platform dependencies installed${NC}"
else
    npm install --silent
    echo -e "${GREEN}  ✓ Platform dependencies installed${NC}"
fi

echo ""

# Link SDK globally
echo -e "${GRAY}[4/7] Linking Carbon SDK globally...${NC}"
cd "$SDK_DIR/sdk"

if [ "$PKG_MANAGER" = "bun" ]; then
    bun link 2>/dev/null || true
else
    npm link 2>/dev/null || true
fi

# Verify carbon command
if command -v carbon &> /dev/null; then
    echo -e "${GREEN}  ✓ 'carbon' command available globally${NC}"
else
    echo -e "${YELLOW}  ⚠ 'carbon' command not in PATH${NC}"
    echo -e "${GRAY}    You may need to restart your terminal${NC}"
fi

echo ""

# Environment setup
echo -e "${GRAY}[5/7] Setting up environment configuration...${NC}"

# SDK environment
if [ ! -f "$SDK_DIR/.env" ]; then
    if [ -f "$SDK_DIR/.env.example" ]; then
        cp "$SDK_DIR/.env.example" "$SDK_DIR/.env"
        echo -e "${YELLOW}  • Created SDK .env from template${NC}"
        echo -e "${GRAY}    Configure: $SDK_DIR/.env${NC}"
    fi
fi

# Platform environment
if [ ! -f "$PLATFORM_DIR/.env" ]; then
    cat > "$PLATFORM_DIR/.env" << 'EOF'
# Carbon6 Platform Environment
NODE_ENV=development
PORT=5173

# Database (optional)
# DATABASE_URL=postgresql://user:password@localhost:5432/carbon6

# API Keys (optional)
# STRIPE_SECRET_KEY=
# CLAUDE_API_KEY=
EOF
    echo -e "${YELLOW}  • Created platform .env${NC}"
    echo -e "${GRAY}    Configure: $PLATFORM_DIR/.env${NC}"
else
    echo -e "${GREEN}  ✓ Environment files exist${NC}"
fi

echo ""

# Create platform link
echo -e "${GRAY}[6/7] Creating platform shortcuts...${NC}"
mkdir -p "$INSTALL_DIR"

cat > "$INSTALL_DIR/start-sdk.sh" << 'EOF'
#!/bin/bash
cd ~/carbon-collective/sdk && npm run dev
EOF

cat > "$INSTALL_DIR/start-platform.sh" << 'EOF'
#!/bin/bash
cd ~/Carbon6 && npm run dev
EOF

cat > "$INSTALL_DIR/build-platform.sh" << 'EOF'
#!/bin/bash
cd ~/Carbon6 && npm run build && npm run preview
EOF

chmod +x "$INSTALL_DIR"/*.sh

echo -e "${GREEN}  ✓ Created helper scripts in $INSTALL_DIR${NC}"
echo ""

# System info
echo -e "${GRAY}[7/7] Installation complete!${NC}"
echo ""

# Success banner
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║     ✓ Carbon6 Platform Installed Successfully            ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Next steps
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${GRAY}1. Initialize your Carbon profile:${NC}"
echo -e "   ${BLUE}carbon init --name \"Your Name\"${NC}"
echo ""
echo -e "${GRAY}2. Start the platform:${NC}"
echo -e "   ${BLUE}cd ~/Carbon6 && ${PKG_MANAGER} run dev${NC}"
echo ""
echo -e "${GRAY}3. Track your first project:${NC}"
echo -e "   ${BLUE}cd ~/your-project && carbon track${NC}"
echo ""
echo -e "${GRAY}4. Start auto-sync:${NC}"
echo -e "   ${BLUE}carbon watch${NC}"
echo ""

# Helpful paths
echo -e "${GRAY}Installed Components:${NC}"
echo -e "  ${GRAY}• SDK:      $SDK_DIR${NC}"
echo -e "  ${GRAY}• Platform: $PLATFORM_DIR${NC}"
echo -e "  ${GRAY}• Scripts:  $INSTALL_DIR${NC}"
echo ""

# Documentation links
echo -e "${GRAY}Documentation:${NC}"
echo -e "  ${GRAY}• SDK Commands:    carbon --help${NC}"
echo -e "  ${GRAY}• Platform Docs:   ~/Carbon6/README.md${NC}"
echo -e "  ${GRAY}• Team Guide:      ~/carbon-collective/docs/${NC}"
echo ""

# Tier system reminder
echo -e "${GRAY}Carbon Tier System:${NC}"
echo -e "  ${GRAY}[C]   Carbon      50/50 split  Execute, learn, prove${NC}"
echo -e "  ${BLUE}[C6]  Carbon[6]   65/35 split  Lead, mentor, build${NC}"
echo -e "  ${GRAY}[6]   Black Ops   80/20 split  Govern, innovate, impossible${NC}"
echo ""

echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Pressure Creates.${NC}"
echo -e "${GRAY}Part of VLTRN Council - Carbon Domain${NC}"
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
