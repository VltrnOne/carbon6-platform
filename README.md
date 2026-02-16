# Carbon6 Platform + OiS

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     CARBON[6] PLATFORM + OiS                              ║
║                                                           ║
║     Operational Intelligence System                      ║
║     Lead. Mentor. Build. Pressure Creates.                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**The complete Carbon6 creator collective platform with dual installation options:**
- **OiS Lite** - Terminal-first, lightweight OS layer
- **Full Production** - Complete multi-part installation with database, security, monitoring

**Version:** 1.0.0 | **Classification:** L5-BLACK

---

## 🚀 Quick Start - Choose Your Platform

### macOS / Linux

#### Option A: OiS Lite (Recommended for Quick Start)

**Simple, fast, terminal-based installation:**

```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

**Installs in ~5 minutes:**
- ✅ OiS CLI (`ois` command)
- ✅ Carbon Collective SDK (`carbon` command)
- ✅ Carbon6 Platform (website)
- ✅ Plugin architecture
- ✅ VLTRN Council agent access

**Requirements:** Node.js 18+, Git

#### Option B: Full Production Installation (macOS)

**Complete setup with database, security, monitoring:**

```bash
# Clone repository
git clone https://github.com/VltrnOne/carbon6-platform.git
cd carbon6-platform

# Fast installer (< 20 minutes)
./install-carbon6-fast.sh
```

**Installs in 15-20 minutes:**
- ✅ PostgreSQL 15 + Redis 7
- ✅ Bun package manager (10x faster)
- ✅ Parallel installation
- ✅ Optimized for speed

**Requirements:** macOS 12+, 8GB RAM, 10GB disk

---

### Windows 10/11

#### Personal Installation (Single User)

**For development on your local machine:**

```powershell
irm https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows.ps1 | iex
```

**Installs to:** `C:\Users\YourName\Carbon6`
**Access:** localhost only, single user
**Best for:** Development, testing, personal use

**📖 Full Guide:** [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

---

#### Shared Installation (Multi-User, Network-Ready)

**For team/production use - accessible from any computer:**

```powershell
# Run as Administrator
irm https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows-shared.ps1 | iex
```

**Installs to:** `C:\Carbon6` (all users can access)
**Access:** Network-accessible, multi-user
**Best for:** Production, teams, shared office environments

**Features:**
- ✅ All users on system can run the server
- ✅ Accessible from other computers on network
- ✅ Shared configuration in `C:\ProgramData\Carbon6`
- ✅ Desktop shortcut for all users
- ✅ Optional Windows service (auto-start)

**📖 Full Guide:** [INSTALL_WINDOWS_SHARED.md](INSTALL_WINDOWS_SHARED.md)

**Installs in 15-20 minutes:**
- ✅ Chocolatey package manager
- ✅ Bun (10x faster than npm)
- ✅ PostgreSQL 15
- ✅ Memurai (Redis for Windows)
- ✅ Express + WebSocket server

**Requirements:** Windows 10+, PowerShell 5.1+, Administrator privileges, 4GB RAM, 5GB disk

---

## 📦 What's Included

### Core Components

**1. OiS - Operational Intelligence System**
- Terminal-first OS layer
- AI agent orchestration
- Plugin architecture
- Natural language task execution
- < 500ms startup, ~50MB footprint

**2. Carbon Collective SDK**
- Team collaboration & file syncing
- Project tracking
- Auto-sync (30-second intervals)
- Multi-creator workspace

**3. Carbon6 Platform**
- Marketing website (Vite + GSAP)
- Creator portal (future)
- Tier system (C → C6 → [6])

---

## 🎯 OiS Lite - Terminal OS

### Features

- **AI Agent Integration** - Direct VLTRN Council access (462 agents)
- **Plugin System** - Hot-swappable capabilities (6 core plugins)
- **Carbon6 Integration** - Seamless SDK + platform connection
- **Natural Language** - Execute tasks via plain English
- **Security Model** - L1-L5 clearance levels, AES-256-GCM

### Commands

```bash
# System
ois init              # Initialize OiS
ois status            # System health
ois version           # Version info

# Plugins
ois plugins           # List all plugins
ois plugins install ois-carbon

# AI Agents
ois agents            # List VLTRN Council agents
ois task "deploy my app"  # Natural language execution
ois agents invoke TECHNE "build API"

# Carbon6
ois carbon status     # SDK status
ois carbon sync       # Force sync
```

### Plugin Ecosystem

| Plugin | Description |
|--------|-------------|
| `ois-carbon` | Carbon6 SDK integration |
| `ois-council` | VLTRN Council agents |
| `ois-nvidia` | GPU acceleration |
| `ois-flow` | Workflow automation |
| `ois-intel` | Intelligence gathering |
| `ois-secure` | Security & encryption |

### After Installation

```bash
# 1. Initialize OiS
ois init

# 2. Initialize Carbon profile
carbon init --name "Your Name"

# 3. View system status
ois status

# 4. List available agents
ois agents

# 5. Start platform website
cd ~/Carbon6 && npm run dev

# 6. Track a project
cd ~/your-project && carbon track

# 7. Enable auto-sync
carbon watch
```

---

## 🏗️ Full Production Installation

### The Four AI Agents

**PRAXIS** (Operations Director) - Part 0: System Prerequisites
**SCOUT** (Discovery Agent) - Part 1: Pre-Installation Configuration
**GENESIS** (Divine Orchestrator) - Part 2: Main Installation
**SOVEREIGN** (Strategic Command) - Part 3: Post-Installation Setup

### Installation Modes

#### 1. Full Installation (Recommended)
```bash
./install-carbon6.sh
# Select option 1
```
**Duration:** 40-65 minutes
**Includes:** PostgreSQL, Redis, PM2, all agents, monitoring

#### 2. Quick Start (Developer Mode)
```bash
./install-carbon6.sh
# Select option 2
```
**Duration:** 25 minutes
**Includes:** SQLite, single instance, core features only

#### 3. Custom Installation
```bash
./install-carbon6.sh
# Select option 3
```
**Duration:** 30-50 minutes
**Choose:** Components, database, mode

### Individual Parts

Run each part separately for granular control:

```bash
./scripts/install-part-0.sh  # System prerequisites
./scripts/install-part-1.sh  # Configuration
./scripts/install-part-2.sh  # Main installation
./scripts/install-part-3.sh  # Post-setup
```

### Configuration

Create `.env` file:

```env
# Database
DATABASE_URL="postgresql://localhost/carbon6"
REDIS_URL="redis://localhost:6379"

# Security
JWT_SECRET="your-jwt-secret"
ENCRYPTION_KEY="your-encryption-key"

# Council
COUNCIL_ENABLED=true
COUNCIL_API_URL="http://localhost:8080"

# Features
ENABLE_CONNECTOR_PROTOCOL=true
ENABLE_WEB_TERMINAL=true
ENABLE_88X_CONSOLE=true
```

### Verification

```bash
# Check services
pm2 status

# Health check
curl http://localhost:3006/api/health

# View logs
pm2 logs carbon6-api

# Access terminal
open http://localhost:3006/terminal

# Access console
open http://localhost:3006/console
```

---

## 🔧 System Requirements

### OiS Lite

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 10.15+, Ubuntu 20.04+, Windows 10+ | Latest |
| **Node.js** | 18.x | 20.x (LTS) |
| **RAM** | 512 MB | 2 GB |
| **Disk** | 100 MB | 500 MB |

### Full Production (macOS)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 12+ | Latest |
| **Node.js** | 20.x | 20.x (LTS) |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB | 20 GB |
| **Database** | PostgreSQL 15 | PostgreSQL 15 |

### Full Production (Windows)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (Build 19041+) | Windows 11 |
| **PowerShell** | 5.1 | 7.x |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 5 GB | 10 GB |
| **Database** | PostgreSQL 15 | PostgreSQL 15 |

---

## 🎓 Carbon Tier System

| Tier | Badge | Revenue Split | Philosophy |
|------|-------|---------------|------------|
| **Carbon** | `[C]` | 50/50 | Execute, learn, prove |
| **Carbon[6]** | `[C6]` | 65/35 | Lead, mentor, build |
| **Black Ops** | `[6]` | 80/20 | Govern, innovate, impossible |

---

## 📚 Documentation

### OiS Lite Docs
- **OIS_ARCHITECTURE.md** - Complete technical architecture
- **OIS_ROADMAP.md** - Feature roadmap (v1.0 → v2.0)
- **ois/README.md** - OiS user guide
- **QUICK_START.md** - 30-second quick start

### Full Production Docs
- **CARBON6_OIS_COMPLETE_INSTALLATION_GUIDE.md** - Complete guide
- **CARBON6_OIS_INSTALLER_PART_0.md** - Part 0 detailed guide
- **CARBON6_OIS_INSTALLER_PART_1.md** - Part 1 detailed guide
- **CARBON6_OIS_INSTALLER_PART_2.md** - Part 2 detailed guide
- **CARBON6_OIS_INSTALLER_PART_3.md** - Part 3 detailed guide
- **SECURITY_MANAGEMENT_GUIDE.md** - Security best practices
- **DISTRIBUTION_GUIDE.md** - Distribution & deployment

---

## 🛠️ Troubleshooting

### OiS Lite

**"ois: command not found"**
```bash
# Restart terminal
exec $SHELL

# Or re-run installer
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

**"carbon: command not found"**
```bash
cd ~/carbon-collective/sdk
npm link
```

### Full Production

**Installation Failed**
```bash
# View logs
cat installation.log
pm2 logs

# Restart services
pm2 restart all
```

**Port Already in Use**
```bash
# Find process
lsof -i :3006

# Kill process
kill -9 <PID>
```

**Database Issues**
```bash
# Reset database
npx prisma db push --force-reset

# Restart PostgreSQL
brew services restart postgresql@15

# Restart Redis
brew services restart redis
```

---

## 📁 Directory Structure

```
~/
├── carbon6-platform/          # This repository
│   ├── remote-install.sh      # OiS Lite installer
│   ├── install-carbon6.sh     # Full production installer
│   ├── ois/                   # OiS CLI source
│   │   ├── bin/ois           # Executable
│   │   ├── plugins/          # Plugin directory
│   │   └── config/           # Config templates
│   ├── scripts/               # Installation scripts
│   │   ├── install-part-0.sh
│   │   ├── install-part-1.sh
│   │   ├── install-part-2.sh
│   │   └── install-part-3.sh
│   └── docs/                  # Complete documentation
│
├── carbon-collective/         # Carbon SDK
│   ├── sdk/                   # CLI tool
│   └── projects/              # Synced work
│
└── Carbon6/                   # Platform website
    ├── src/                   # Source code
    └── public/                # Static assets
```

---

## 🔄 Upgrade Paths

### OiS Lite → Full OS (Future)
```bash
ois upgrade --to full-os
```

Adds desktop environment, GUI apps, hardware drivers, system services.

### Quick Start → Full Production
```bash
# Run full installer
./install-carbon6.sh
# Select "Full Installation"
```

---

## 🤝 Contributing

Carbon6 Platform is maintained by the VLTRN Council Carbon Domain team.

**For Carbon Members:**
1. All work auto-syncs via `carbon watch`
2. Update `carbon-collective/CLAUDE.md` with learnings
3. Follow tier-specific contribution guidelines

**For External Contributors:**
- Issues: https://github.com/VltrnOne/carbon6-platform/issues
- Discussions: https://github.com/VltrnOne/carbon6-platform/discussions

---

## 🔒 Security

### Credentials (Never Commit)
- `.env` - Contains secrets
- `.install-state.json` - Installation info
- `installation.log` - May contain sensitive data

### SSH Keys
Generated in `~/.ssh/`:
- `id_ed25519` - Private key (keep secure!)
- `id_ed25519.pub` - Public key (add to GitHub)

### Admin Account
Change default password immediately after production installation.

---

## 📄 License

ISC License - See individual repositories for details.
Copyright © 2026 VLTRN Council - Carbon Domain
**Classification:** L5-BLACK | Sovereign Technology

---

## 🔗 Links

- **SDK Repository**: https://github.com/VltrnOne/carbon-collective
- **Platform Repository**: https://github.com/VltrnOne/Carbon6
- **Documentation**: See `/docs` directory
- **Support**: support@carbon6.io

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pressure Creates.
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Carbon6** - Where capable creators become leaders.
