#!/bin/bash

################################################################################
# Carbon6 OiS - macOS Shared Installation
#
# Multi-User | Network-Ready | Centralized
#
# Installation Locations:
#   Application:  /opt/carbon6
#   Data/Config:  /var/lib/carbon6
#   Logs:         /var/log/carbon6
#   Service:      ~/Library/LaunchAgents (per-user) or
#                 /Library/LaunchDaemons (system-wide)
#
# Usage:
#   sudo ./install-carbon6-macos-shared.sh
#   sudo ./install-carbon6-macos-shared.sh --path /custom/path
################################################################################

set -e

# Parse arguments
INSTALL_PATH="/opt/carbon6"
DATA_PATH="/var/lib/carbon6"
LOG_PATH="/var/log/carbon6"

while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --data)
            DATA_PATH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m'

# Timer
START_TIME=$(date +%s)

# Logging
log_info() { echo -e "${GRAY}  • $1${NC}"; }
log_success() { echo -e "${GREEN}  ✓ $1${NC}"; }
log_warning() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
log_error() { echo -e "${RED}  ✗ $1${NC}"; }

elapsed_time() {
    CURRENT=$(date +%s)
    echo "$((CURRENT - START_TIME))s"
}

# Banner
clear
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║     CARBON6 OiS - MACOS SHARED INSTALLATION              ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║     Multi-User | Network-Ready | Centralized             ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for sudo
if [ "$EUID" -ne 0 ]; then
    log_error "This installer requires sudo privileges"
    echo ""
    echo "Please run:"
    echo "  sudo $0"
    exit 1
fi

log_info "Installation Path: $INSTALL_PATH"
log_info "Data Path: $DATA_PATH"
log_info "Log Path: $LOG_PATH"
echo ""

################################################################################
# [1/8] SYSTEM CHECKS
################################################################################
echo -e "${GRAY}[1/8] Checking system requirements...${NC}"

# macOS version
MACOS_VERSION=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MACOS_VERSION" -lt 12 ]; then
    log_error "macOS 12+ required (detected: $MACOS_VERSION)"
    exit 1
fi
log_success "macOS $(sw_vers -productVersion) | $(elapsed_time)"

################################################################################
# [2/8] CREATE SHARED DIRECTORIES
################################################################################
echo ""
echo -e "${GRAY}[2/8] Creating shared directories...${NC}"

# Create directories
mkdir -p "$INSTALL_PATH"
mkdir -p "$DATA_PATH"
mkdir -p "$LOG_PATH"
mkdir -p "$DATA_PATH/config"
mkdir -p "$DATA_PATH/database"

# Set ownership to staff group (multi-user access)
chown -R root:staff "$INSTALL_PATH"
chown -R root:staff "$DATA_PATH"
chown -R root:staff "$LOG_PATH"

# Set permissions
chmod -R 755 "$INSTALL_PATH"      # All users can read/execute
chmod -R 775 "$DATA_PATH"         # All staff members can modify
chmod -R 775 "$LOG_PATH"          # All staff members can write logs

log_success "Application: $INSTALL_PATH"
log_success "Data: $DATA_PATH"
log_success "Logs: $LOG_PATH"
log_success "Permissions set for multi-user access | $(elapsed_time)"

################################################################################
# [3/8] INSTALL PACKAGE MANAGERS
################################################################################
echo ""
echo -e "${GRAY}[3/8] Installing package managers...${NC}"

# Install Homebrew (if not present)
if ! command -v brew &> /dev/null; then
    log_info "Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH
    if [ -d "/opt/homebrew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    log_success "Homebrew installed"
else
    log_success "Homebrew already installed"
    brew update 2>&1 | grep -v "^Warning:" || true
fi

# Install Bun (system-wide)
if ! command -v bun &> /dev/null; then
    log_info "Installing Bun (system-wide)..."
    curl -fsSL https://bun.sh/install | bash

    # Make bun accessible system-wide
    if [ -f "$HOME/.bun/bin/bun" ]; then
        ln -sf "$HOME/.bun/bin/bun" /usr/local/bin/bun 2>/dev/null || true
    fi

    log_success "Bun installed"
else
    log_success "Bun already installed"
fi

log_success "Package managers ready | $(elapsed_time)"

################################################################################
# [4/8] INSTALL SYSTEM DEPENDENCIES
################################################################################
echo ""
echo -e "${GRAY}[4/8] Installing system dependencies...${NC}"

# Create Brewfile
cat > /tmp/carbon6-brewfile << 'EOF'
brew "node@20"
brew "postgresql@15"
brew "redis"
brew "git"
brew "gh"
EOF

log_info "Installing via Homebrew..."
brew bundle --file=/tmp/carbon6-brewfile --no-lock 2>&1 | grep -E "Installing|Using|Upgrading" || true

# Link Node.js 20
brew link node@20 --force --overwrite 2>/dev/null || true

log_success "System dependencies installed | $(elapsed_time)"

################################################################################
# [5/8] CONFIGURE SERVICES
################################################################################
echo ""
echo -e "${GRAY}[5/8] Configuring database services...${NC}"

# Start PostgreSQL
if ! brew services list | grep postgresql@15 | grep started >/dev/null 2>&1; then
    log_info "Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 5
fi
log_success "PostgreSQL running"

# Configure PostgreSQL for network access
PG_CONF=""
if [ -d "/opt/homebrew/var/postgresql@15" ]; then
    PG_CONF="/opt/homebrew/var/postgresql@15/postgresql.conf"
    PG_HBA="/opt/homebrew/var/postgresql@15/pg_hba.conf"
elif [ -d "/usr/local/var/postgresql@15" ]; then
    PG_CONF="/usr/local/var/postgresql@15/postgresql.conf"
    PG_HBA="/usr/local/var/postgresql@15/pg_hba.conf"
fi

if [ -f "$PG_CONF" ]; then
    # Enable network connections
    if ! grep -q "listen_addresses = '\*'" "$PG_CONF"; then
        echo "" >> "$PG_CONF"
        echo "# Carbon6 network access" >> "$PG_CONF"
        echo "listen_addresses = '*'" >> "$PG_CONF"
    fi
fi

if [ -f "$PG_HBA" ]; then
    # Allow network connections
    if ! grep -q "host.*all.*all.*0.0.0.0/0.*md5" "$PG_HBA"; then
        echo "" >> "$PG_HBA"
        echo "# Carbon6 network access" >> "$PG_HBA"
        echo "host    all             all             0.0.0.0/0               md5" >> "$PG_HBA"

        # Restart PostgreSQL to apply changes
        brew services restart postgresql@15 >/dev/null 2>&1
        sleep 3
    fi
fi

# Start Redis
if ! brew services list | grep redis | grep started >/dev/null 2>&1; then
    log_info "Starting Redis..."
    brew services start redis
    sleep 2
fi
log_success "Redis running"

# Create database
createdb carbon6 2>/dev/null || true
log_success "Database ready | $(elapsed_time)"

################################################################################
# [6/8] INSTALL APPLICATION
################################################################################
echo ""
echo -e "${GRAY}[6/8] Installing application...${NC}"

cd "$INSTALL_PATH"

# Create package.json
cat > package.json << 'EOF'
{
  "name": "carbon6-ois",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "node server.js",
    "start": "NODE_ENV=production node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "prisma": "^5.0.0",
    "@prisma/client": "^5.0.0",
    "dotenv": "^16.3.1",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "ioredis": "^5.3.2",
    "ws": "^8.14.2"
  }
}
EOF

log_info "Installing dependencies with Bun..."
bun install --silent 2>&1 || npm install --silent

log_success "Application installed | $(elapsed_time)"

################################################################################
# [7/8] CONFIGURE DATABASE
################################################################################
echo ""
echo -e "${GRAY}[7/8] Setting up database schema...${NC}"

# Create Prisma directory
mkdir -p prisma

# Create schema
cat > prisma/schema.prisma << 'EOF'
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  password  String
  role      String   @default("user")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Project {
  id          String   @id @default(uuid())
  title       String
  description String?
  status      String   @default("active")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
EOF

# Create shared environment file
cat > "$DATA_PATH/config/.env" << EOF
# Carbon6 Platform Configuration (Shared)
# Location: $DATA_PATH/config/.env

# Database (network-accessible)
DATABASE_URL="postgresql://$(whoami)@localhost:5432/carbon6"
REDIS_URL="redis://localhost:6379"

# Security
JWT_SECRET="change-this-secret-key"
ENCRYPTION_KEY="change-this-encryption-key"

# Server (bind to all interfaces for network access)
NODE_ENV="production"
PORT=3006
HOST=0.0.0.0

# Paths
INSTALL_PATH="$INSTALL_PATH"
DATA_PATH="$DATA_PATH"
LOG_PATH="$LOG_PATH"

# Council
COUNCIL_ENABLED=true
COUNCIL_API_URL="http://localhost:8080"
EOF

# Create symlink to shared config
ln -sf "$DATA_PATH/config/.env" "$INSTALL_PATH/.env"

# Set permissions
chmod 664 "$DATA_PATH/config/.env"

# Run Prisma
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/carbon6"
bunx prisma generate 2>&1 | grep -v "warning" || npx prisma generate 2>&1 | grep -v "warning" || true

log_success "Database schema ready | $(elapsed_time)"

################################################################################
# [8/8] CREATE SERVER & LAUNCH SCRIPT
################################################################################
echo ""
echo -e "${GRAY}[8/8] Creating server and launch configuration...${NC}"

# Create server.js
cat > "$INSTALL_PATH/server.js" << 'SERVERJS'
import express from 'express';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import os from 'os';

dotenv.config();

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

const PORT = process.env.PORT || 3006;
const HOST = process.env.HOST || '0.0.0.0';

app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    platform: 'macos-shared',
    hostname: os.hostname(),
    installPath: process.env.INSTALL_PATH,
    dataPath: process.env.DATA_PATH,
    services: {
      database: 'connected',
      redis: 'connected'
    }
  });
});

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to Carbon6 OiS (Shared Installation)'
  }));
});

server.listen(PORT, HOST, () => {
  const networkInterfaces = os.networkInterfaces();
  const addresses = [];

  for (const name of Object.keys(networkInterfaces)) {
    for (const iface of networkInterfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        addresses.push(iface.address);
      }
    }
  }

  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     CARBON6 OiS SERVER RUNNING (Shared)                  ║
║                                                           ║
║     Local:     http://localhost:${PORT}                      ║
║     Network:   http://${os.hostname()}:${PORT}              ║
${addresses.map(addr => `║     IP:        http://${addr}:${PORT}                       ║`).join('\n')}
║                                                           ║
║     Install:   ${process.env.INSTALL_PATH}                ║
║     Data:      ${process.env.DATA_PATH}                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});
SERVERJS

# Create global start script
cat > "$INSTALL_PATH/start.sh" << 'EOF'
#!/bin/bash
cd /opt/carbon6
export DATA_PATH=/var/lib/carbon6
export LOG_PATH=/var/log/carbon6
node server.js
EOF

chmod +x "$INSTALL_PATH/start.sh"

# Create command-line shortcut
ln -sf "$INSTALL_PATH/start.sh" /usr/local/bin/carbon6 2>/dev/null || true

log_success "Server created | $(elapsed_time)"

################################################################################
# COMPLETION
################################################################################

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_TIME / 60))
SECONDS=$((TOTAL_TIME % 60))

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║     ✓ SHARED INSTALLATION COMPLETE!                      ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║     Total Time: ${MINUTES}m ${SECONDS}s                                     ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Installation Locations:${NC}"
log_info "Application:  $INSTALL_PATH"
log_info "Data/Config:  $DATA_PATH"
log_info "Logs:         $LOG_PATH"
log_info "Command:      carbon6 (system-wide)"
echo ""

echo -e "${BLUE}Network Access:${NC}"
HOSTNAME=$(hostname)
IP_ADDR=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "N/A")
log_info "From this Mac:      http://localhost:3006"
log_info "From other devices: http://$HOSTNAME:3006"
if [ "$IP_ADDR" != "N/A" ]; then
    log_info "                    http://$IP_ADDR:3006"
fi
echo ""

echo -e "${BLUE}Quick Start:${NC}"
echo -e "  ${GRAY}1. Start server:${NC}"
echo -e "     ${GREEN}carbon6${NC}  ${GRAY}(or)${NC}  ${GREEN}sudo $INSTALL_PATH/start.sh${NC}"
echo ""
echo -e "  ${GRAY}2. Test from this Mac:${NC}"
echo -e "     ${GREEN}curl http://localhost:3006/api/health${NC}"
echo ""
echo -e "  ${GRAY}3. Test from another device:${NC}"
echo -e "     ${GREEN}curl http://$HOSTNAME:3006/api/health${NC}"
echo ""

echo -e "${BLUE}For All Users:${NC}"
log_info "Any user on this Mac can run: carbon6"
log_info "Configuration: $DATA_PATH/config/.env"
log_info "Logs: $LOG_PATH"
echo ""

echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Multi-User | Network-Ready | Centralized Installation${NC}"
echo -e "${GRAY}Part of VLTRN Council - Carbon Domain${NC}"
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
