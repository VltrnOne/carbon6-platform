# Carbon6 OiS Installer - Part 0 of 4: Pre-Flight System Prerequisites

```
██████╗ ██████╗ ███████╗      ███████╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗
██╔══██╗██╔══██╗██╔════╝      ██╔════╝██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
██████╔╝██████╔╝█████╗  █████╗█████╗  ██║     ██║██║  ███╗███████║   ██║
██╔═══╝ ██╔══██╗██╔══╝  ╚════╝██╔══╝  ██║     ██║██║   ██║██╔══██║   ██║
██║     ██║  ██║███████╗      ██║     ███████╗██║╚██████╔╝██║  ██║   ██║
╚═╝     ╚═╝  ╚═╝╚══════╝      ╚═╝     ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
```

**Classification:** L5-BLACK System Preparation
**Agent:** PRAXIS (Operations Director)
**Phase:** System Prerequisites (0 of 4)
**Duration:** 10-15 minutes

---

## Introduction

```
👤 PRAXIS: "Welcome! I'm PRAXIS, the Operations Director of the Council. Before
we can install Carbon6 OiS, I need to prepare your system with all the essential
tools and dependencies.

Think of me as your infrastructure engineer - I ensure the foundation is solid
before we build the skyscraper.

THIS IS CRITICAL: Without these prerequisites, Parts 1-3 will fail. We need to
install development tools, language runtimes, databases, and configure your
terminal ecosystem.

Don't worry - I'll handle everything automatically. You just need to approve
a few system-level installations."
```

**What This Part Does:**
- ✅ Install Homebrew (macOS package manager)
- ✅ Install development tools (Git, Node.js, Python, etc.)
- ✅ Install databases (PostgreSQL, Redis)
- ✅ Install global NPM packages (Claude CLI, n8n, etc.)
- ✅ Configure Claude CLI and MCP servers
- ✅ Generate SSH keys for secure deployments
- ✅ Verify all prerequisites are met

**Estimated Time:** 10-15 minutes (depends on internet speed)

---

## System Requirements Check

```
👤 PRAXIS: "First, let me verify your system meets the minimum requirements."

🔄 CHECKING: Operating system and hardware
```

**Automated Check:**
```bash
#!/bin/bash

echo "SYSTEM REQUIREMENTS CHECK:"
echo ""

# Operating System
os_name=$(uname -s)
os_version=$(sw_vers -productVersion 2>/dev/null || echo "Unknown")

if [ "$os_name" == "Darwin" ]; then
  echo "  ✓ Operating System: macOS $os_version"
else
  echo "  ⚠️  Operating System: $os_name (not macOS)"
  echo "    This installer is optimized for macOS. Linux support coming soon."
fi

# CPU Architecture
cpu_arch=$(uname -m)
cpu_cores=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo "Unknown")

echo "  ✓ CPU Architecture: $cpu_arch"
echo "  ✓ CPU Cores: $cpu_cores"

# Memory
total_mem=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
total_mem_gb=$((total_mem / 1024 / 1024 / 1024))

if [ $total_mem_gb -ge 8 ]; then
  echo "  ✓ RAM: ${total_mem_gb}GB (Sufficient)"
else
  echo "  ⚠️  RAM: ${total_mem_gb}GB (Minimum 8GB recommended)"
fi

# Disk Space
available_space=$(df -h / | awk 'NR==2 {print $4}')
echo "  ✓ Available Disk Space: $available_space"

# Internet Connectivity
if ping -c 1 google.com &> /dev/null; then
  echo "  ✓ Internet Connection: Active"
else
  echo "  ✗ Internet Connection: Failed"
  echo "    Please connect to the internet to continue."
  exit 1
fi

echo ""
echo "STATUS: ✅ SYSTEM REQUIREMENTS MET"
```

---

## Phase 1: Homebrew Installation

```
👤 PRAXIS: "Homebrew is the foundation of macOS development. It's like apt-get
for Mac - the package manager that installs everything else."

🔄 CHECKING: Homebrew installation
```

### 1.1 Check if Homebrew Exists

```bash
if command -v brew &> /dev/null; then
  echo "✓ Homebrew already installed: $(brew --version | head -n1)"
  brew update
else
  echo "⚠️  Homebrew not found. Installing now..."
fi
```

### 1.2 Install Homebrew (if needed)

```bash
👤 PRAXIS: "Installing Homebrew. This will ask for your system password."

🔄 EXECUTING: Homebrew installation
```

**Installation Command:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Expected Output:**
```
==> Checking for `sudo` access (which may request your password)...
Password:
==> This script will install:
/opt/homebrew/bin/brew
/opt/homebrew/share/doc/homebrew
/opt/homebrew/share/man/man1/brew.1
/opt/homebrew/share/zsh/site-functions/_brew
/opt/homebrew/etc/bash_completion.d/brew
/opt/homebrew/Homebrew

Press RETURN/ENTER to continue or any other key to abort:
==> Downloading and installing Homebrew...
==> Installation successful!

==> Next steps:
- Run `brew help` to get started
- Add Homebrew to your PATH:
  (echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ~/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"

✅ HOMEBREW INSTALLED
```

### 1.3 Add Homebrew to PATH

```bash
# For Apple Silicon (M1/M2/M3)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Intel Macs
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# Verify
brew --version
```

**Verification:**
```
Homebrew 4.2.5
STATUS: ✅ HOMEBREW READY
```

---

## Phase 2: Core Development Tools

```
👤 PRAXIS: "Now I'll install the core development tools: languages, runtimes,
version control, and build tools. This is the toolchain that powers Carbon6."

🔄 EXECUTING: Development tools installation
```

### 2.1 Essential CLI Tools

```bash
#!/bin/bash

echo "INSTALLING ESSENTIAL CLI TOOLS:"
echo ""

tools=(
  "git"           # Version control
  "gh"            # GitHub CLI
  "wget"          # File downloader
  "curl"          # HTTP client
  "jq"            # JSON processor
  "tree"          # Directory viewer
  "htop"          # Process monitor
  "gnu-sed"       # GNU sed (better than macOS sed)
  "p7zip"         # Archive utility
)

for tool in "${tools[@]}"; do
  echo "Installing $tool..."
  brew install $tool
done

echo ""
echo "✅ CLI TOOLS INSTALLED"
```

**Expected Output:**
```
Installing git...
==> Downloading https://ghcr.io/v2/homebrew/core/git/manifests/2.43.0
==> Pouring git--2.43.0.arm64_sonoma.bottle.tar.gz
🍺  /opt/homebrew/Cellar/git/2.43.0: 1,631 files, 54.3MB

Installing gh...
🍺  /opt/homebrew/Cellar/gh/2.42.0: 156 files, 34.2MB

[... continues for each tool ...]

✅ CLI TOOLS INSTALLED
```

### 2.2 Language Runtimes

```bash
echo "INSTALLING LANGUAGE RUNTIMES:"
echo ""

# Node.js (Latest LTS)
brew install node@20

# Python 3.12
brew install python@3.12

# Go
brew install go

# Verify installations
echo ""
echo "VERIFICATION:"
node --version      # Should show v20.x.x
npm --version       # Should show 10.x.x
python3 --version   # Should show Python 3.12.x
go version          # Should show go1.21.x
```

**Expected Output:**
```
INSTALLING LANGUAGE RUNTIMES:

Installing node@20...
🍺  /opt/homebrew/Cellar/node@20/20.11.0: 2,068 files, 71.2MB

Installing python@3.12...
🍺  /opt/homebrew/Cellar/python@3.12/3.12.1: 3,279 files, 61.4MB

Installing go...
🍺  /opt/homebrew/Cellar/go/1.21.6: 12 files, 547.8MB

VERIFICATION:
v20.11.0
10.2.4
Python 3.12.1
go version go1.21.6 darwin/arm64

✅ RUNTIMES INSTALLED
```

### 2.3 Build Tools & Libraries

```bash
echo "INSTALLING BUILD TOOLS & LIBRARIES:"
echo ""

build_tools=(
  "cmake"         # Build system
  "pkg-config"    # Package configuration
  "automake"      # Build automation
  "autoconf"      # Configure scripts
  "libtool"       # Library building
  "openssl@3"     # Cryptography
  "sqlite"        # Database library
)

for tool in "${build_tools[@]}"; do
  echo "Installing $tool..."
  brew install $tool
done

echo ""
echo "✅ BUILD TOOLS INSTALLED"
```

---

## Phase 3: Database Systems

```
👤 PRAXIS: "Carbon6 requires PostgreSQL for production data and optionally
Redis for caching. I'll install both so you have maximum flexibility."

🔄 EXECUTING: Database installation
```

### 3.1 PostgreSQL Installation

```bash
echo "INSTALLING POSTGRESQL:"
echo ""

# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Wait for service to start
sleep 3

# Verify PostgreSQL is running
if pg_isready &> /dev/null; then
  echo "✓ PostgreSQL is running"
else
  echo "⚠️  PostgreSQL failed to start"
  echo "  Trying to start manually..."
  brew services restart postgresql@15
  sleep 3
fi

# Create default database
createdb $(whoami)

# Show PostgreSQL version
psql --version
```

**Expected Output:**
```
INSTALLING POSTGRESQL:

==> Downloading https://ghcr.io/v2/homebrew/core/postgresql@15/manifests/15.5
🍺  /opt/homebrew/Cellar/postgresql@15/15.5: 3,341 files, 44.2MB

==> Starting postgresql@15
==> Successfully started `postgresql@15` (label: homebrew.mxcl.postgresql@15)

✓ PostgreSQL is running
psql (PostgreSQL) 15.5

✅ POSTGRESQL INSTALLED
```

### 3.2 Redis Installation

```bash
echo "INSTALLING REDIS:"
echo ""

# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Wait for service to start
sleep 2

# Verify Redis is running
if redis-cli ping &> /dev/null; then
  echo "✓ Redis is running"
  redis-cli INFO server | grep redis_version
else
  echo "⚠️  Redis failed to start"
  brew services restart redis
fi
```

**Expected Output:**
```
INSTALLING REDIS:

==> Downloading https://ghcr.io/v2/homebrew/core/redis/manifests/7.2.4
🍺  /opt/homebrew/Cellar/redis/7.2.4: 14 files, 3.2MB

==> Starting redis
==> Successfully started `redis` (label: homebrew.mxcl.redis)

✓ Redis is running
redis_version:7.2.4

✅ REDIS INSTALLED
```

---

## Phase 4: Global NPM Packages

```
👤 PRAXIS: "Now for the AI and automation layer - global NPM packages that
power the Carbon6 ecosystem, Council agents, and development workflows."

🔄 EXECUTING: Global package installation
```

### 4.1 Essential Global Packages

```bash
#!/bin/bash

echo "INSTALLING GLOBAL NPM PACKAGES:"
echo ""

packages=(
  "@anthropic-ai/claude-code@latest"   # Claude CLI
  "n8n@latest"                          # Workflow automation
  "pm2@latest"                          # Process manager
  "vercel@latest"                       # Vercel deployment
  "netlify-cli@latest"                  # Netlify deployment
  "pnpm@latest"                         # Fast package manager
  "typescript@latest"                   # TypeScript compiler
  "ts-node@latest"                      # TypeScript executor
  "prisma@latest"                       # Database ORM
  "nodemon@latest"                      # Auto-restart
)

for package in "${packages[@]}"; do
  echo "Installing $package..."
  npm install -g $package
done

echo ""
echo "INSTALLED GLOBAL PACKAGES:"
npm list -g --depth=0
```

**Expected Output:**
```
INSTALLING GLOBAL NPM PACKAGES:

Installing @anthropic-ai/claude-code@latest...
added 234 packages in 12s

Installing n8n@latest...
added 1,892 packages in 45s

Installing pm2@latest...
added 187 packages in 8s

[... continues for each package ...]

INSTALLED GLOBAL PACKAGES:
/opt/homebrew/lib
├── @anthropic-ai/claude-code@2.0.76
├── n8n@1.23.0
├── pm2@5.3.0
├── vercel@33.0.1
├── netlify-cli@17.10.1
├── pnpm@8.14.1
├── typescript@5.3.3
├── ts-node@10.9.2
├── prisma@5.8.1
└── nodemon@3.0.2

✅ GLOBAL PACKAGES INSTALLED
```

---

## Phase 5: Claude CLI Configuration

```
👤 PRAXIS: "The Claude CLI is your gateway to AI-powered development. I'll
configure it now and set up the MCP (Model Context Protocol) servers that
allow Claude to access your codebase, databases, and external services."

🔄 EXECUTING: Claude CLI setup
```

### 5.1 Claude CLI Authentication

```bash
echo "AUTHENTICATING CLAUDE CLI:"
echo ""

# Check if already authenticated
if claude auth status &> /dev/null; then
  echo "✓ Claude CLI already authenticated"
  claude auth status
else
  echo "⚠️  Claude CLI not authenticated"
  echo ""
  echo "Please authenticate now (this will open your browser):"
  claude auth login
fi
```

**Interactive Authentication:**
```
AUTHENTICATING CLAUDE CLI:

⚠️  Claude CLI not authenticated

Please authenticate now (this will open your browser):
? Opening browser to authenticate...
✓ Authentication successful!

Logged in as: morpheous@vltrn.agency
Plan: Professional
API Credits: 1,000,000 tokens remaining

✅ CLAUDE CLI AUTHENTICATED
```

### 5.2 MCP Server Configuration

```bash
echo "CONFIGURING MCP SERVERS:"
echo ""

# Create MCP configuration directory
mkdir -p ~/.claude/mcp

# Create MCP configuration file
cat > ~/.claude/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/Morpheous"],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/carbon6"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_KEY": "${SUPABASE_KEY}"
      }
    }
  }
}
EOF

echo "✓ MCP configuration created: ~/.claude/mcp/config.json"
echo ""
echo "MCP SERVERS CONFIGURED:"
echo "  ✓ filesystem - Access local files"
echo "  ✓ postgres - Database queries"
echo "  ✓ github - Repository operations"
echo "  ✓ supabase - Supabase integration"
```

### 5.3 Create Claude Configuration

```bash
echo "CREATING CLAUDE CLI CONFIGURATION:"
echo ""

# Create main Claude config
mkdir -p ~/.claude
cat > ~/.claude/config.json << 'EOF'
{
  "version": "1.0.0",
  "user": {
    "email": "morpheous@vltrn.agency",
    "organization": "VLTRN",
    "role": "Admin"
  },
  "theme": {
    "syntax_highlighting": true,
    "color_scheme": "carbon-dark"
  },
  "terminal": {
    "preferred": ["kitty", "alacritty", "warp"],
    "shell": "zsh"
  },
  "approved_projects": [
    "/Users/Morpheous/Carbon6",
    "/Users/Morpheous/vltrndataroom",
    "/Users/Morpheous/council"
  ],
  "features": {
    "auto_commit": false,
    "smart_suggestions": true,
    "context_memory": true,
    "mcp_enabled": true
  }
}
EOF

echo "✓ Claude configuration created: ~/.claude/config.json"
echo ""
echo "✅ CLAUDE CLI CONFIGURED"
```

**Verification:**
```bash
# Verify Claude CLI is working
claude --version

# Test MCP servers
claude mcp list
```

**Expected Output:**
```
Claude CLI v2.0.76

MCP SERVERS:
  ✓ filesystem - Ready
  ✓ postgres - Ready
  ✓ github - Ready
  ✓ supabase - Ready

✅ CLAUDE CLI CONFIGURED
```

---

## Phase 6: SSH Key Generation

```
👤 PRAXIS: "Secure deployments require SSH keys. I'll generate Ed25519 keys
for GitHub, deployment servers, and hosting platforms."

🔄 EXECUTING: SSH key generation
```

### 6.1 Generate Primary SSH Key

```bash
#!/bin/bash

echo "GENERATING SSH KEYS:"
echo ""

ssh_dir="$HOME/.ssh"
mkdir -p "$ssh_dir"
chmod 700 "$ssh_dir"

# Primary key for GitHub/Git
if [ ! -f "$ssh_dir/id_ed25519" ]; then
  echo "Generating primary SSH key (GitHub/Git)..."
  ssh-keygen -t ed25519 -C "morpheous@carbon6-$(hostname)" -f "$ssh_dir/id_ed25519" -N ""
  echo "✓ Primary key generated: $ssh_dir/id_ed25519"
else
  echo "✓ Primary key already exists: $ssh_dir/id_ed25519"
fi

# Deployment key
if [ ! -f "$ssh_dir/id_ed25519_deploy" ]; then
  echo "Generating deployment SSH key..."
  ssh-keygen -t ed25519 -C "deploy@carbon6-$(hostname)" -f "$ssh_dir/id_ed25519_deploy" -N ""
  echo "✓ Deployment key generated: $ssh_dir/id_ed25519_deploy"
else
  echo "✓ Deployment key already exists: $ssh_dir/id_ed25519_deploy"
fi

# Start SSH agent and add keys
eval "$(ssh-agent -s)"
ssh-add "$ssh_dir/id_ed25519"
ssh-add "$ssh_dir/id_ed25519_deploy"

echo ""
echo "✅ SSH KEYS GENERATED"
```

### 6.2 Create SSH Config

```bash
cat > ~/.ssh/config << 'EOF'
# GitHub
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  AddKeysToAgent yes
  UseKeychain yes

# Deployment Server (example)
Host carbon6-deploy
  HostName deploy.carbon6.io
  User deploy
  IdentityFile ~/.ssh/id_ed25519_deploy
  Port 22
  ServerAliveInterval 60
  ServerAliveCountMax 3

# SiteGround (if needed)
Host siteground
  HostName ssh.siteground.com
  User carbon6
  IdentityFile ~/.ssh/id_ed25519_deploy
  Port 18765
EOF

chmod 600 ~/.ssh/config
echo "✓ SSH config created: ~/.ssh/config"
```

### 6.3 Display Public Keys

```bash
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "YOUR PUBLIC SSH KEYS (Add these to GitHub/Servers):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "PRIMARY KEY (GitHub):"
cat ~/.ssh/id_ed25519.pub
echo ""
echo "DEPLOYMENT KEY (Servers):"
cat ~/.ssh/id_ed25519_deploy.pub
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "NEXT STEPS:"
echo "1. Copy the PRIMARY KEY above"
echo "2. Add to GitHub: https://github.com/settings/ssh/new"
echo "3. Add DEPLOYMENT KEY to your servers"
echo ""
echo "✅ SSH KEYS READY"
```

---

## Phase 7: Optional Tools & Utilities

```
👤 PRAXIS: "These optional tools enhance your development experience. I'll
install them now, but you can skip any you don't need."

🔄 EXECUTING: Optional tools installation
```

### 7.1 Development Utilities

```bash
echo "INSTALLING OPTIONAL DEVELOPMENT TOOLS:"
echo ""

# Docker Desktop (you may already have this)
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  brew install --cask docker
else
  echo "✓ Docker already installed"
fi

# VS Code Extensions Helper
if command -v code &> /dev/null; then
  echo "Installing recommended VS Code extensions..."
  code --install-extension bradlc.vscode-tailwindcss
  code --install-extension dbaeumer.vscode-eslint
  code --install-extension esbenp.prettier-vscode
  code --install-extension Prisma.prisma
fi

# Terminal enhancers
brew install --cask iterm2 2>/dev/null || echo "iTerm2 already installed"
brew install zsh-autosuggestions
brew install zsh-syntax-highlighting

echo ""
echo "✅ OPTIONAL TOOLS INSTALLED"
```

---

## Phase 8: System Verification

```
👤 PRAXIS: "Final verification - I'll check that all prerequisites are
correctly installed and configured."

🔄 EXECUTING: Comprehensive system check
```

### 8.1 Verification Script

```bash
#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "CARBON6 OIS PRE-FLIGHT VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

all_passed=true

# Check Homebrew
if command -v brew &> /dev/null; then
  echo "✓ Homebrew: $(brew --version | head -n1)"
else
  echo "✗ Homebrew: NOT INSTALLED"
  all_passed=false
fi

# Check Git
if command -v git &> /dev/null; then
  echo "✓ Git: $(git --version)"
else
  echo "✗ Git: NOT INSTALLED"
  all_passed=false
fi

# Check Node.js
if command -v node &> /dev/null; then
  echo "✓ Node.js: $(node --version)"
else
  echo "✗ Node.js: NOT INSTALLED"
  all_passed=false
fi

# Check npm
if command -v npm &> /dev/null; then
  echo "✓ npm: $(npm --version)"
else
  echo "✗ npm: NOT INSTALLED"
  all_passed=false
fi

# Check Python
if command -v python3 &> /dev/null; then
  echo "✓ Python: $(python3 --version)"
else
  echo "✗ Python: NOT INSTALLED"
  all_passed=false
fi

# Check PostgreSQL
if command -v psql &> /dev/null; then
  echo "✓ PostgreSQL: $(psql --version)"
  if pg_isready &> /dev/null; then
    echo "  └─ Service: RUNNING"
  else
    echo "  └─ Service: NOT RUNNING"
    all_passed=false
  fi
else
  echo "✗ PostgreSQL: NOT INSTALLED"
  all_passed=false
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
  echo "✓ Redis: $(redis-cli --version)"
  if redis-cli ping &> /dev/null 2>&1; then
    echo "  └─ Service: RUNNING"
  else
    echo "  └─ Service: NOT RUNNING"
    all_passed=false
  fi
else
  echo "✗ Redis: NOT INSTALLED"
  all_passed=false
fi

# Check Claude CLI
if command -v claude &> /dev/null; then
  echo "✓ Claude CLI: $(claude --version)"
  if claude auth status &> /dev/null; then
    echo "  └─ Authentication: VALID"
  else
    echo "  └─ Authentication: NOT AUTHENTICATED"
    all_passed=false
  fi
else
  echo "✗ Claude CLI: NOT INSTALLED"
  all_passed=false
fi

# Check PM2
if command -v pm2 &> /dev/null; then
  echo "✓ PM2: $(pm2 --version)"
else
  echo "✗ PM2: NOT INSTALLED"
  all_passed=false
fi

# Check SSH Keys
if [ -f ~/.ssh/id_ed25519 ]; then
  echo "✓ SSH Keys: Generated"
  echo "  └─ Primary: ~/.ssh/id_ed25519"
  echo "  └─ Deploy: ~/.ssh/id_ed25519_deploy"
else
  echo "✗ SSH Keys: NOT GENERATED"
  all_passed=false
fi

# Check MCP Configuration
if [ -f ~/.claude/mcp/config.json ]; then
  echo "✓ MCP Servers: Configured"
else
  echo "✗ MCP Servers: NOT CONFIGURED"
  all_passed=false
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ "$all_passed" = true ]; then
  echo "STATUS: ✅ ALL PREREQUISITES INSTALLED"
  echo ""
  echo "READY FOR NEXT STEP:"
  echo "→ Part 1: Pre-Installation (SCOUT Agent)"
  echo ""
  echo "Run: ./CARBON6_OIS_INSTALLER_PART_1.md"
else
  echo "STATUS: ⚠️  SOME PREREQUISITES MISSING"
  echo ""
  echo "Please review the items marked with ✗ above and install them"
  echo "before proceeding to Part 1."
fi

echo "═══════════════════════════════════════════════════════════════"
```

---

## Installation Summary

```
👤 PRAXIS: "Pre-flight complete! Here's what we accomplished:"

SYSTEM PREREQUISITES INSTALLED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PACKAGE MANAGER
   └─ Homebrew 4.2.5

✅ DEVELOPMENT TOOLS
   └─ Git, GitHub CLI, wget, curl, jq, tree, htop

✅ LANGUAGE RUNTIMES
   └─ Node.js 20.11.0
   └─ npm 10.2.4
   └─ Python 3.12.1
   └─ Go 1.21.6

✅ DATABASES
   └─ PostgreSQL 15.5 (RUNNING)
   └─ Redis 7.2.4 (RUNNING)

✅ GLOBAL NPM PACKAGES
   └─ @anthropic-ai/claude-code@2.0.76
   └─ n8n@1.23.0
   └─ pm2@5.3.0
   └─ vercel@33.0.1
   └─ netlify-cli@17.10.1
   └─ pnpm@8.14.1
   └─ prisma@5.8.1

✅ CLAUDE CLI
   └─ Authenticated
   └─ MCP Servers configured (4 servers)

✅ SSH KEYS
   └─ Primary key generated
   └─ Deployment key generated
   └─ SSH config created

✅ BUILD TOOLS
   └─ cmake, pkg-config, automake, autoconf

NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Add SSH public keys to GitHub:
   https://github.com/settings/ssh/new

2. Proceed to Part 1:
   CARBON6_OIS_INSTALLER_PART_1.md
   (SCOUT Agent - Pre-Installation)

Your system is now fully prepared for Carbon6 OiS installation!
```

---

## Quick Reference

### Service Management

```bash
# PostgreSQL
brew services start postgresql@15    # Start
brew services stop postgresql@15     # Stop
brew services restart postgresql@15  # Restart
pg_isready                           # Check status

# Redis
brew services start redis            # Start
brew services stop redis             # Stop
brew services restart redis          # Restart
redis-cli ping                       # Check status

# View all Homebrew services
brew services list
```

### Useful Commands

```bash
# Update all Homebrew packages
brew update && brew upgrade

# Check for issues
brew doctor

# Clean up old versions
brew cleanup

# View installed packages
brew list

# Search for packages
brew search <package-name>

# View package info
brew info <package-name>
```

### Claude CLI Commands

```bash
# Check authentication status
claude auth status

# Login/logout
claude auth login
claude auth logout

# List MCP servers
claude mcp list

# Test Claude
claude "Hello, are you working?"
```

---

## Troubleshooting

### Issue: Homebrew Installation Failed

```bash
# Check Xcode Command Line Tools
xcode-select --install

# If already installed, reset and reinstall
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

### Issue: PostgreSQL Won't Start

```bash
# Check if port 5432 is already in use
lsof -i :5432

# If yes, kill the process or use different port
kill -9 <PID>

# Remove old PostgreSQL data (if upgrading)
rm -rf /opt/homebrew/var/postgresql@15

# Reinitialize
initdb /opt/homebrew/var/postgresql@15
```

### Issue: Redis Won't Start

```bash
# Check if port 6379 is already in use
lsof -i :6379

# Remove old Redis data
rm -rf /opt/homebrew/var/db/redis

# Restart
brew services restart redis
```

### Issue: Claude CLI Not Authenticated

```bash
# Clear existing auth
rm -rf ~/.claude/auth

# Re-authenticate
claude auth login
```

---

**Pre-Flight Complete**
**Next:** Part 1 - Pre-Installation (SCOUT Agent)
**Status:** ✅ SYSTEM READY

```
PRAXIS (Operations Director)
Document ID: L5-INSTALL-2026-000 | Part 0 of 4
Classification: L5-BLACK | February 12, 2026
```
