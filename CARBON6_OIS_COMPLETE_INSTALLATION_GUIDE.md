# Carbon6 OiS Complete Installation Guide

```
 ██████╗ █████╗ ██████╗ ██████╗  ██████╗ ███╗   ██╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝
██║     ███████║██████╔╝██████╔╝██║   ██║██╔██╗ ██║███████╗
██║     ██╔══██║██╔══██╗██╔══██╗██║   ██║██║╚██╗██║██╔═══██╗
╚██████╗██║  ██║██║  ██║██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝

          OPERATIONAL INTELLIGENCE SYSTEM
          AGENTIC-FIRST OS-STYLE INSTALLATION
```

**Classification:** L5-BLACK Installation Protocol
**Version:** 1.0.0
**Release Date:** February 12, 2026
**Total Duration:** 40-65 minutes

---

## Overview

The Carbon6 OiS (Operational Intelligence System) is an enterprise-grade, AI-powered platform featuring:

- **462 Council Agents** with GENESIS Divine Orchestrator
- **12 NVIDIA Acceleration Backends** (NIM, Riva, Triton, NeMo, Morpheus, etc.)
- **8 LLM Providers** with intelligent routing
- **88x™ Chairman Console** with 1,000 Super Mini Traders
- **10-Gate Security System** (Ed25519 + JWT)
- **Web Terminal Interface** for OS-style command access
- **Connector Protocol** for external SDK integration
- **Three-Tier Creator System** (Carbon → Carbon[6] → [6])

This installation guide uses an **agentic-first approach** where specialized AI agents guide you through each phase of the installation process.

---

## Installation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    4-PART INSTALLATION FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Part 0: PRE-FLIGHT (10-15 min)                                 │
│  Agent: PRAXIS (Operations Director)                            │
│  ├─ Homebrew installation                                       │
│  ├─ Development tools (Git, Node.js, Python, Go)               │
│  ├─ Databases (PostgreSQL, Redis)                              │
│  ├─ Global NPM packages                                         │
│  ├─ Claude CLI + MCP servers                                   │
│  └─ SSH key generation                                          │
│                                                                 │
│  ↓                                                              │
│                                                                 │
│  Part 1: PRE-INSTALLATION (5-10 min)                           │
│  Agent: SCOUT (Discovery)                                       │
│  ├─ System requirements validation                             │
│  ├─ Installation mode selection                                │
│  ├─ Component selection wizard                                 │
│  ├─ Environment configuration                                  │
│  └─ Pre-installation automation                                │
│                                                                 │
│  ↓                                                              │
│                                                                 │
│  Part 2: MAIN INSTALLATION (15-25 min)                         │
│  Agent: GENESIS (Divine Orchestrator)                           │
│  ├─ Repository cloning                                         │
│  ├─ Dependency installation                                    │
│  ├─ Database setup & migrations                                │
│  ├─ Application build                                          │
│  ├─ Process manager (PM2/Docker)                               │
│  └─ Service verification                                       │
│                                                                 │
│  ↓                                                              │
│                                                                 │
│  Part 3: POST-INSTALLATION (10-15 min)                         │
│  Agent: SOVEREIGN (Strategic Command)                           │
│  ├─ Admin account creation                                     │
│  ├─ First creator onboarding                                   │
│  ├─ Plugin marketplace setup                                   │
│  ├─ Council agent testing                                      │
│  ├─ 88x™ console initialization                                │
│  ├─ Monitoring configuration                                   │
│  ├─ Automated backups                                          │
│  └─ Production hardening                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before starting the installation, ensure you have:

### Required
- ✅ macOS 12+ (Monterey or later) - *Linux support coming soon*
- ✅ 8GB RAM minimum (16GB recommended)
- ✅ 20GB free disk space
- ✅ Internet connection (for package downloads)
- ✅ Admin/sudo access

### Helpful (but will be installed if missing)
- Homebrew package manager
- Node.js 20+
- Python 3.12+
- PostgreSQL 15+
- Redis 7+

---

## Quick Start

### Option 1: Interactive Installation (Recommended)

```bash
# Clone the Carbon6 platform repository
git clone https://github.com/vltrn/carbon6-platform.git
cd carbon6-platform

# Start the agentic installation
./install.sh
```

The `install.sh` script will:
1. Detect missing prerequisites
2. Guide you through each part with AI agents
3. Provide real-time status and progress
4. Handle errors and rollbacks automatically

### Option 2: Manual Step-by-Step

If you prefer to follow the documentation manually:

```bash
# Step 1: Open Part 0
cat CARBON6_OIS_INSTALLER_PART_0.md

# Step 2: Follow PRAXIS agent's instructions
# ... complete Part 0 ...

# Step 3: Open Part 1
cat CARBON6_OIS_INSTALLER_PART_1.md

# ... and so on through Part 3
```

---

## Installation Parts Breakdown

### Part 0: Pre-Flight System Prerequisites
**Agent:** PRAXIS (Operations Director)
**Time:** 10-15 minutes
**Purpose:** Install all system-level dependencies

**What Gets Installed:**
- Homebrew package manager
- Git, GitHub CLI, development tools
- Node.js 20 LTS, npm, pnpm
- Python 3.12, Go 1.21
- PostgreSQL 15, Redis 7
- Claude CLI with MCP servers
- Global NPM packages (n8n, PM2, Vercel, etc.)
- SSH keys (Ed25519)

**File:** `CARBON6_OIS_INSTALLER_PART_0.md`

**Key Commands:**
```bash
# After Part 0, verify with:
brew --version
node --version
psql --version
redis-cli --version
claude --version
```

---

### Part 1: Pre-Installation
**Agent:** SCOUT (Discovery)
**Time:** 5-10 minutes
**Purpose:** Validate requirements and configure installation

**What Happens:**
- System requirements check (OS, CPU, RAM, disk)
- Installation mode selection:
  - **Developer Mode**: SQLite, in-memory cache, single instance
  - **Production Mode**: PostgreSQL, Redis, PM2 cluster
  - **Docker Mode**: Containerized deployment
  - **Hybrid Mode**: PostgreSQL + Docker
- Component selection:
  - Core Platform (required)
  - Connector Protocol (optional)
  - Web Terminal (optional)
  - Council Integration (optional)
  - 88x™ Console (optional)
- Environment configuration wizard
- Pre-installation automation (directory creation, key generation)

**File:** `CARBON6_OIS_INSTALLER_PART_1.md`

**Outputs:**
- `.env` file with configuration
- Installation manifest
- Rollback checkpoint

---

### Part 2: Main Installation
**Agent:** GENESIS (Divine Orchestrator)
**Time:** 15-25 minutes
**Purpose:** Install and build the Carbon6 platform

**What Happens:**
1. **Repository Acquisition**
   - Clone Carbon6 repository
   - Verify structure integrity

2. **Dependency Installation**
   - npm ci (156+ packages)
   - Prisma client generation

3. **Environment Setup**
   - Create `.env` from Part 1 config
   - Database connection validation

4. **Database Setup**
   - PostgreSQL/SQLite schema migration
   - Seed feature gates and system data

5. **Application Build**
   - Next.js production build
   - TypeScript compilation
   - Static asset optimization

6. **Process Manager Setup**
   - PM2 cluster mode (8 instances) OR
   - Docker container deployment

7. **Service Verification**
   - Health checks
   - Smoke tests
   - Connector protocol validation

**File:** `CARBON6_OIS_INSTALLER_PART_2.md`

**Outputs:**
- Running Next.js application on port 3006
- Database with tables and indexes
- PM2/Docker services running

---

### Part 3: Post-Installation Configuration
**Agent:** SOVEREIGN (Strategic Command)
**Time:** 10-15 minutes
**Purpose:** Configure for production and operational excellence

**What Happens:**
1. **Admin Account Creation**
   - L5-BLACK clearance admin user
   - Master API key generation

2. **First Creator Onboarding**
   - Create Carbon tier creator
   - Generate SDK connector installation

3. **Plugin Marketplace Setup**
   - Seed sample plugins
   - Configure marketplace categories

4. **Council Agent Testing**
   - Test GENESIS orchestrator
   - Verify domain specialists (TECHNE, AURUM, AEGIS)
   - Confirm 462 agents responding

5. **88x™ Chairman Console**
   - Initialize 1,000 Super Mini Traders
   - Configure risk parameters
   - Set up dashboard state

6. **Monitoring & Observability**
   - Prometheus metrics
   - Grafana dashboards
   - Alerting rules

7. **Automated Backups**
   - Daily backup schedule (2:00 AM)
   - Encryption configuration
   - 30-day retention policy

8. **Production Hardening**
   - Rate limiting
   - Security headers
   - Permission audits

**File:** `CARBON6_OIS_INSTALLER_PART_3.md`

**Outputs:**
- Production-ready system
- Operational runbooks
- Monitoring dashboards
- Secure backups

---

## What You'll Have After Installation

### System Access
- 🌐 **Web Platform**: http://localhost:3006
- 🖥️ **Terminal Interface**: http://localhost:3006/terminal
- 📊 **88x™ Console**: http://localhost:3006/console
- 💾 **Admin Dashboard**: http://localhost:3006/admin
- 📈 **Metrics**: http://localhost:3006/api/metrics
- 🏥 **Health Check**: http://localhost:3006/api/health

### Accounts Created
- **Admin Account**: L5-BLACK clearance with full system access
- **First Creator**: Carbon tier (50/50 split)
- **SDK Installation**: Connector protocol configured

### Core Components
- **Next.js Application**: 8-instance cluster mode
- **PostgreSQL Database**: Full schema with 10 tables
- **Redis Cache**: 2GB memory limit
- **PM2 Process Manager**: Auto-restart, zero-downtime reload

### Security Infrastructure
- **10-Gate Security System**: Ed25519 signatures + JWT tokens
- **Feature Gates**: Tier-based access control (CARBON/CARBON[6]/[6])
- **Rate Limiting**: Per-installation and global limits
- **Audit Logging**: Comprehensive request tracking

### AI & Automation
- **462 Council Agents**: GENESIS orchestrator + domain specialists
- **12 NVIDIA Backends**: GPU-accelerated capabilities
- **8 LLM Providers**: Claude, Gemini, Kimi, Codex, etc.
- **172 God Mode Workflows**: Pre-built enterprise workflows

### Trading System
- **88x™ Chairman Console**: 1,000 Super Mini Traders initialized
- **Risk Engine**: Configured with safety parameters
- **Dashboard**: Real-time monitoring and control

### Operations
- **Daily Backups**: Encrypted, automated at 2:00 AM
- **Monitoring**: Prometheus + Grafana dashboards
- **Alerting**: Critical error and performance alerts
- **Runbooks**: Incident response and recovery procedures

---

## Common Installation Modes

### Developer Mode (Fastest)
**Best for:** Local development, testing, learning
**Time:** ~25 minutes
**Components:**
- SQLite database
- In-memory cache
- Single Node.js instance
- All features enabled

**Command:**
```bash
./install.sh --mode developer
```

---

### Production Mode (Recommended)
**Best for:** Production deployment, multi-user, high traffic
**Time:** ~50 minutes
**Components:**
- PostgreSQL database
- Redis cache
- PM2 cluster (8 instances)
- All features enabled
- Monitoring and backups

**Command:**
```bash
./install.sh --mode production
```

---

### Docker Mode (Containerized)
**Best for:** Cloud deployment, Kubernetes, isolated environments
**Time:** ~40 minutes
**Components:**
- PostgreSQL container
- Redis container
- Application container
- Docker Compose orchestration

**Command:**
```bash
./install.sh --mode docker
```

---

### Hybrid Mode (Flexible)
**Best for:** Mixed environments, gradual migration
**Time:** ~45 minutes
**Components:**
- PostgreSQL database (local or remote)
- Docker application container
- Flexible cache (Redis or in-memory)

**Command:**
```bash
./install.sh --mode hybrid
```

---

## Troubleshooting

### Issue: Port 3006 Already in Use

```bash
# Find process using port 3006
lsof -i :3006

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=3007 npm start
```

### Issue: PostgreSQL Connection Failed

```bash
# Check PostgreSQL is running
pg_isready

# Restart PostgreSQL
brew services restart postgresql@15

# Verify connection string
echo $DATABASE_URL
```

### Issue: PM2 Not Starting

```bash
# Check PM2 logs
pm2 logs carbon6-api --lines 50

# Restart PM2
pm2 restart carbon6-api

# If still failing, delete and recreate
pm2 delete carbon6-api
pm2 start ecosystem.config.js
```

### Issue: Council Agents Not Responding

```bash
# Check Council service
curl http://localhost:8080/api/agents/status

# Restart Council
pm2 restart carbon6-council

# Check logs
pm2 logs carbon6-council
```

### Issue: Installation Rollback

```bash
# Automatic rollback (if installation fails)
./install.sh --rollback

# Manual rollback
cd /Users/Morpheous/Carbon6/platform
git checkout <previous-commit>
pm2 stop all
dropdb carbon6
```

---

## Post-Installation Tasks

### 1. Add SSH Keys to GitHub
```bash
# Display your public SSH key
cat ~/.ssh/id_ed25519.pub

# Copy and add to: https://github.com/settings/ssh/new
```

### 2. Configure External Services (Optional)
- **Sentry**: Error tracking
- **Prometheus/Grafana**: Monitoring
- **PagerDuty**: Alerting
- **Supabase**: External database (if needed)

### 3. Customize Environment
```bash
# Edit environment variables
nano .env

# Restart application
pm2 restart carbon6-api
```

### 4. Create Additional Creators
```bash
# Via terminal interface
http://localhost:3006/terminal
> creator create --email dev@example.com --name "John Doe" --tier CARBON

# Or via API
curl -X POST http://localhost:3006/api/creators \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -d '{"email":"dev@example.com","name":"John Doe","tier":"CARBON"}'
```

### 5. Deploy First Project
```bash
# Via terminal
> project create --title "Website Redesign" --type "Digital Product"

# Or via admin dashboard
http://localhost:3006/admin/projects/new
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CARBON6 OIS ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ PRESENTATION LAYER                                    │     │
│  │ ├─ Next.js 14 (App Router)                           │     │
│  │ ├─ Web Terminal (xterm.js + WebSocket)               │     │
│  │ ├─ 88x™ Chairman Console                             │     │
│  │ └─ Admin Dashboard                                   │     │
│  └───────────────────────────────────────────────────────┘     │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ API LAYER                                             │     │
│  │ ├─ REST API (24 endpoints)                           │     │
│  │ ├─ WebSocket (terminal + real-time)                  │     │
│  │ ├─ Connector Protocol (10-gate security)             │     │
│  │ └─ Council Integration (462 agents)                  │     │
│  └───────────────────────────────────────────────────────┘     │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ BUSINESS LOGIC LAYER                                  │     │
│  │ ├─ Creator Management (3-tier system)                │     │
│  │ ├─ Project Lifecycle                                 │     │
│  │ ├─ Plugin Marketplace                                │     │
│  │ ├─ SDK Connector Registry                            │     │
│  │ └─ Agent Orchestration (GENESIS)                     │     │
│  └───────────────────────────────────────────────────────┘     │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ DATA LAYER                                            │     │
│  │ ├─ Prisma ORM                                         │     │
│  │ ├─ PostgreSQL (10 tables, 18 indexes)                │     │
│  │ ├─ Redis (caching + rate limiting)                   │     │
│  │ └─ Audit Logs (tamper-evident)                       │     │
│  └───────────────────────────────────────────────────────┘     │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ INTEGRATION LAYER                                     │     │
│  │ ├─ Council (462 agents, 12 NVIDIA, 8 LLMs)           │     │
│  │ ├─ 88x™ Trading (1,000 Super Minis)                  │     │
│  │ ├─ External APIs (GitHub, Stripe, etc.)              │     │
│  │ └─ MCP Servers (filesystem, postgres, etc.)          │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Model

### 10-Gate Security System

Every connector request passes through 10 sequential gates:

1. **Gate 1**: Required headers present (`X-Client-ID`, `X-Timestamp`, `X-Nonce`, `X-Signature`)
2. **Gate 2**: Installation exists in database
3. **Gate 3**: Installation is enabled (not suspended)
4. **Gate 4**: Not suspended for violations
5. **Gate 5**: Timestamp within 5-minute window (replay protection)
6. **Gate 6**: Nonce never used before (prevents replay attacks)
7. **Gate 7**: Body hash matches request content
8. **Gate 8**: Ed25519 signature valid
9. **Gate 9**: JWT token valid and not revoked
10. **Gate 10**: Rate limits not exceeded

**Rejection at Any Gate = 401/403 Response**

### Clearance Levels

| Level | Name | Access | Agents |
|-------|------|--------|--------|
| **L5-BLACK** | Supreme | Full system control | GENESIS + 4 super minis |
| **L4-RESTRICTED** | Council Core | Strategic operations | SOVEREIGN, MNEMOS, AEGIS, PRAXIS, TRUST_DIRECTOR |
| **L3-CONFIDENTIAL** | Domain Specialists | Specialized operations | 24 domain specialists (TECHNE, AURUM, etc.) |
| **L2-INTERNAL** | Support Agents | Operational support | CALAMUS, CHRONOS, BENEFACTOR, HERMES, LOGOS |
| **L1-PUBLIC** | Interface Agents | Public-facing | SCOUT, FORMA, NUNTIUS, VERBUM |

---

## Support & Resources

### Documentation
- **Installation Guide**: This document
- **API Reference**: `/docs/API_REFERENCE.md`
- **SDK Documentation**: `/sdk-templates/*/README.md`
- **Council Guide**: `COUNCIL_INTEGRATION.md`
- **Production Deployment**: `PRODUCTION_DEPLOYMENT.md`

### Runbooks
- **Incident Response**: `/runbooks/INCIDENT_RESPONSE.md`
- **Backup & Restore**: `/runbooks/BACKUP_RESTORE.md`
- **Scaling Guide**: `/runbooks/SCALING.md`

### Community
- **GitHub Issues**: https://github.com/vltrn/carbon6-platform/issues
- **Discord**: https://discord.gg/carbon6
- **Email**: support@carbon6.io

### Quick Commands
```bash
# Status
pm2 status
pm2 monit

# Logs
pm2 logs carbon6-api
pm2 logs carbon6-council

# Restart
pm2 restart carbon6-api
pm2 reload carbon6-api  # Zero-downtime

# Database
psql carbon6
npx prisma studio

# Backups
./scripts/backup-database.sh
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-12 | Initial release - Complete 4-part installation |

---

## License

Copyright © 2026 VLTRN AGENCY
Classification: L5-BLACK | Sovereign Technology

---

**Ready to Begin?**

Start with Part 0:
```bash
cat CARBON6_OIS_INSTALLER_PART_0.md
```

Or run the automated installer:
```bash
./install.sh
```

**Welcome to Carbon6 - Operational Intelligence for the Sovereign Era.**

```
GENESIS Divine Orchestrator
Document ID: L5-INSTALL-2026-MASTER
Classification: L5-BLACK | February 12, 2026
```
