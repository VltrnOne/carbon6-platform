# 🜏 CARBON6 OiS - OS-STYLE INSTALLATION
## Part 1 of 3: Pre-Installation & System Requirements

**Classification:** L3-CONFIDENTIAL - INSTALLATION SPEC
**Version:** 1.0.0
**Created:** 2026-02-12
**System:** Carbon6 Operational Intelligence System (Agentic First)

---

## OVERVIEW

The Carbon6 OiS installer uses an **Agentic-First** approach where AI agents guide you through the entire installation process. Think of it as having an expert DevOps engineer sitting next to you.

### What Gets Installed (Full Stack)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CARBON6 OiS PLATFORM                         │
├─────────────────────────────────────────────────────────────────┤
│  🜏 Chairman Oversight Console                                  │
│     ├── 88x™ Trading Dashboard                                  │
│     ├── 1,000 Super Mini Trader Management                      │
│     └── Congressional Alpha Feed                                │
│                                                                  │
│  🔗 Connector Protocol                                          │
│     ├── 10-Gate Security System                                 │
│     ├── Ed25519 Cryptography                                    │
│     └── SDK Management                                          │
│                                                                  │
│  🤖 Council Integration (462 Agents)                            │
│     ├── GENESIS Divine Orchestrator                             │
│     ├── 24 Domain Specialists                                   │
│     └── 12 NVIDIA Acceleration Backends                         │
│                                                                  │
│  💻 Terminal Interface                                          │
│     ├── OS-Style CLI (42 commands)                              │
│     ├── WebSocket Real-Time                                     │
│     └── Agent Invocation                                        │
│                                                                  │
│  🗄️ Data Layer                                                  │
│     ├── PostgreSQL + TimescaleDB                                │
│     ├── Redis Cache                                             │
│     └── Prisma ORM                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## INSTALLATION AGENT: SCOUT

**Agent Name:** SCOUT (System Configuration & User Onboarding Tool)
**Tier:** L1-PUBLIC (Discovery Agent)
**Purpose:** Guide users through pre-installation requirements

### Agent Personality

```
👤 SCOUT: "Hello! I'm SCOUT, your installation guide. I'll help you get
Carbon6 OiS up and running. Think of me as your personal DevOps engineer.

I'll be checking your system, asking a few questions about your setup
preferences, and making sure everything is ready before we begin the
actual installation.

This should take about 5-10 minutes. Ready to begin? (yes/no)"
```

---

## PRE-INSTALLATION CHECKLIST

### Phase 1: System Requirements Validation

#### 1.1 Operating System Check

```bash
👤 SCOUT: "First, let me check your operating system..."

CHECKING: Operating System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ SUPPORTED OS DETECTED:
  • macOS 12+ (Monterey or later)
  • Ubuntu 20.04+ / Debian 11+
  • Windows 10/11 with WSL2

YOUR SYSTEM: macOS 14.2 (Sonoma)
STATUS: ✅ COMPATIBLE

Next, I'll check your hardware...
```

#### 1.2 Hardware Requirements

```bash
👤 SCOUT: "Checking your hardware specifications..."

MINIMUM REQUIREMENTS          YOUR SYSTEM           STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CPU: 4 cores (8 recommended)  Apple M2 (8 cores)    ✅ EXCELLENT
RAM: 8GB (16GB recommended)   16GB                  ✅ RECOMMENDED
Disk: 20GB free               450GB free            ✅ EXCELLENT
Network: 10Mbps+              1Gbps                 ✅ EXCELLENT

👤 SCOUT: "Great! Your hardware exceeds our recommendations.
This means you can run the full Carbon6 OiS stack including all
462 Council agents without performance issues."
```

#### 1.3 Software Dependencies

```bash
👤 SCOUT: "Now I'll check for required software dependencies..."

CHECKING DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Node.js (18+)              ⏳ Checking...
  Found: v18.17.0          ✅ INSTALLED

npm (9+)                   ⏳ Checking...
  Found: v9.8.1            ✅ INSTALLED

Python (3.10+)             ⏳ Checking...
  Found: v3.11.4           ✅ INSTALLED

PostgreSQL (15+)           ⏳ Checking...
  Not found                ⚠️  MISSING

Redis (7+)                 ⏳ Checking...
  Not found                ⚠️  MISSING

Docker (optional)          ⏳ Checking...
  Found: v24.0.5           ✅ INSTALLED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 SCOUT: "I noticed PostgreSQL and Redis are not installed.
Would you like me to:

1. Install them via Docker (recommended, easiest)
2. Install them natively on your system
3. Use external hosted services (AWS RDS, Redis Cloud)

What would you prefer? (1/2/3)"
```

---

## INTERACTIVE CONFIGURATION

### Phase 2: Installation Mode Selection

```bash
👤 SCOUT: "Great! Now let's configure your installation.

Carbon6 OiS can be installed in several modes depending on your needs:

┌─────────────────────────────────────────────────────────────────┐
│  INSTALLATION MODES                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣  DEVELOPER MODE (Local Development)                         │
│     • SQLite database (no PostgreSQL needed)                    │
│     • In-memory Redis (no Redis server needed)                  │
│     • Hot reload enabled                                        │
│     • Debug logging                                             │
│     • Perfect for: Testing, development, learning               │
│                                                                  │
│  2️⃣  PRODUCTION MODE (Full Deployment)                          │
│     • PostgreSQL + TimescaleDB                                  │
│     • Redis cluster                                             │
│     • PM2 process manager                                       │
│     • Production logging                                        │
│     • Perfect for: Live trading, production use                 │
│                                                                  │
│  3️⃣  DOCKER MODE (Containerized)                                │
│     • All services in Docker Compose                            │
│     • One-command deployment                                    │
│     • Easy scaling                                              │
│     • Perfect for: Cloud deployment, CI/CD                      │
│                                                                  │
│  4️⃣  HYBRID MODE (Mix & Match)                                  │
│     • Let me guide you through custom configuration             │
│     • Choose services individually                              │
│     • Perfect for: Specific requirements                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Which installation mode would you like? (1/2/3/4)
```

### Phase 3: Component Selection

```bash
USER: 2

👤 SCOUT: "Excellent choice! Production mode it is.

Now, let's select which components you want to install. You can
enable/disable features based on your needs:

┌─────────────────────────────────────────────────────────────────┐
│  COMPONENT SELECTION                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CORE PLATFORM (Required)                           [MANDATORY] │
│  ├── Next.js Application Server                                │
│  ├── Prisma ORM + PostgreSQL                                   │
│  └── Authentication System                                      │
│                                                                  │
│  CONNECTOR PROTOCOL                                  [✓ YES]    │
│  ├── 10-Gate Security System                                   │
│  ├── Ed25519 Cryptography                                      │
│  ├── SDK Management                                            │
│  └── Audit Trail                                               │
│                                                                  │
│  TERMINAL INTERFACE                                  [✓ YES]    │
│  ├── Web Terminal (xterm.js)                                   │
│  ├── 42 CLI Commands                                           │
│  └── WebSocket Server                                          │
│                                                                  │
│  COUNCIL INTEGRATION (462 Agents)                    [? ASK]    │
│  ├── GENESIS Divine Orchestrator                               │
│  ├── 24 Domain Specialists                                     │
│  ├── 12 NVIDIA Backends (requires NVIDIA GPU)                  │
│  └── 8 LLM Providers (requires API keys)                       │
│                                                                  │
│  88x™ CHAIRMAN CONSOLE                               [? ASK]    │
│  ├── Trading Dashboard                                         │
│  ├── 1,000 Super Mini Traders                                  │
│  ├── QuiverQuant CNS Integration                               │
│  └── HybridFunding API                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

👤 SCOUT: "I see you've selected the Connector Protocol and Terminal
Interface. Great choices!

For COUNCIL INTEGRATION: This requires API keys for LLM providers
(Claude, Gemini, etc.) and optionally NVIDIA GPUs for acceleration.

Do you want to enable Council integration? (yes/no)
```

### Phase 4: Environment Configuration

```bash
USER: yes

👤 SCOUT: "Perfect! Council integration will be enabled.

Now I need to collect some configuration details. I'll guide you
through each one:

┌─────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT CONFIGURATION                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DATABASE CONFIGURATION                                         │
│  ─────────────────────────────────────────────────────────────  │
│  Host:     [localhost]                                          │
│  Port:     [5432]                                               │
│  Database: [carbon6_ois]                                        │
│  Username: [carbon6_admin]                                      │
│  Password: [●●●●●●●●] (will be securely stored)                │
│                                                                  │
│  REDIS CONFIGURATION                                            │
│  ─────────────────────────────────────────────────────────────  │
│  Host:     [localhost]                                          │
│  Port:     [6379]                                               │
│  Password: [optional]                                           │
│                                                                  │
│  SECURITY CONFIGURATION                                         │
│  ─────────────────────────────────────────────────────────────  │
│  JWT Secret:           [auto-generate] ✓                        │
│  Encryption Key:       [auto-generate] ✓                        │
│  Admin Email:          morpheous@carbon6.io                     │
│  Admin Password:       [●●●●●●●●]                               │
│  Enable 2FA:           [yes/no] → yes                           │
│                                                                  │
│  API KEYS (LLM Providers)                                       │
│  ─────────────────────────────────────────────────────────────  │
│  Anthropic (Claude):   [sk-ant-●●●●] ✓                         │
│  Google (Gemini):      [AIzaSy●●●●] ✓                          │
│  OpenAI (Codex):       [sk-proj-●●●●] (optional)                │
│  Moonshot (Kimi K2):   [sk-●●●●] (optional)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

👤 SCOUT: "I'll store these securely in an encrypted .env file.
Your credentials will NEVER be logged or transmitted.

Everything looks good! Let me summarize what we're about to install..."
```

---

## PRE-INSTALLATION SUMMARY

### Phase 5: Installation Plan Review

```bash
👤 SCOUT: "Here's your complete installation plan:

┌─────────────────────────────────────────────────────────────────┐
│  📋 INSTALLATION SUMMARY                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SYSTEM INFORMATION                                             │
│  ─────────────────────────────────────────────────────────────  │
│  OS:              macOS 14.2 (Sonoma)                           │
│  CPU:             Apple M2 (8 cores)                            │
│  RAM:             16 GB                                         │
│  Free Disk:       450 GB                                        │
│                                                                  │
│  INSTALLATION MODE                                              │
│  ─────────────────────────────────────────────────────────────  │
│  Mode:            Production                                    │
│  Method:          Native (non-Docker)                           │
│  Path:            /Users/Morpheous/Carbon6/platform             │
│                                                                  │
│  COMPONENTS TO INSTALL                                          │
│  ─────────────────────────────────────────────────────────────  │
│  ✓ Core Platform (Next.js + Prisma)                            │
│  ✓ Connector Protocol (10-Gate Security)                       │
│  ✓ Terminal Interface (42 CLI commands)                        │
│  ✓ Council Integration (462 Agents)                            │
│  ✗ 88x™ Chairman Console (skipped)                             │
│                                                                  │
│  SERVICES REQUIRED                                              │
│  ─────────────────────────────────────────────────────────────  │
│  ✓ PostgreSQL 15 (will install via Homebrew)                   │
│  ✓ Redis 7 (will install via Homebrew)                         │
│  ✓ PM2 Process Manager (will install via npm)                  │
│                                                                  │
│  ESTIMATED INSTALLATION TIME                                    │
│  ─────────────────────────────────────────────────────────────  │
│  Services Installation:   ~5-10 minutes                         │
│  Dependencies:            ~3-5 minutes                          │
│  Database Setup:          ~2-3 minutes                          │
│  Platform Build:          ~5-7 minutes                          │
│  Configuration:           ~2-3 minutes                          │
│  ───────────────────────────────────────────────                │
│  TOTAL:                   ~20-30 minutes                        │
│                                                                  │
│  DISK SPACE REQUIRED                                            │
│  ─────────────────────────────────────────────────────────────  │
│  Application:             ~500 MB                               │
│  Dependencies:            ~1.5 GB                               │
│  Database:                ~2 GB (initial)                       │
│  Logs & Cache:            ~500 MB                               │
│  ───────────────────────────────────────────────                │
│  TOTAL:                   ~4.5 GB                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

👤 SCOUT: "Before we proceed, I'll create a backup of your current
configuration (if any exists) and save this installation plan.

Everything ready to go! Shall we begin the installation? (yes/no)"
```

---

## INSTALLATION PREP TASKS

### Phase 6: Pre-Installation Automation

```bash
USER: yes

👤 SCOUT: "Great! Starting pre-installation tasks...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1/8: Creating installation directory
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Creating: /Users/Morpheous/Carbon6/platform
✓ Directory created successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2/8: Checking for existing installation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Scanning for existing Carbon6 installation...
⚠️  Found existing installation!
📦 Creating backup: carbon6_backup_20260212_193045.tar.gz
✓ Backup created: 487 MB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3/8: Installing system dependencies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🍺 Installing PostgreSQL via Homebrew...
⏳ brew install postgresql@15
✓ PostgreSQL 15.4 installed

🍺 Installing Redis via Homebrew...
⏳ brew install redis
✓ Redis 7.2.3 installed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4/8: Starting database services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting PostgreSQL...
✓ PostgreSQL running on port 5432

🚀 Starting Redis...
✓ Redis running on port 6379

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 5/8: Creating database
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗄️  Creating database: carbon6_ois
✓ Database created

🔐 Creating user: carbon6_admin
✓ User created with privileges

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 6/8: Generating security keys
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Generating JWT secret (256-bit)...
✓ JWT_SECRET generated

🔑 Generating encryption key (AES-256)...
✓ ENCRYPTION_KEY generated

🔑 Generating Ed25519 keypair for system...
✓ System keypair generated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 7/8: Creating configuration files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Writing .env.production...
✓ Environment file created

📝 Writing ecosystem.config.js...
✓ PM2 config created

📝 Writing docker-compose.yml (for future use)...
✓ Docker config created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 8/8: Validating configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Database connection verified
✓ Redis connection verified
✓ All API keys validated
✓ Disk space sufficient
✓ Network connectivity confirmed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PRE-INSTALLATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 SCOUT: "Perfect! All pre-installation tasks completed successfully.

Your system is now ready for the main installation. I've prepared
everything needed to install Carbon6 OiS.

WHAT'S NEXT:
Part 2 will handle the actual installation (downloading code, installing
dependencies, building the platform, running migrations).

Would you like to continue to Part 2 now, or would you like to review
the configuration first? (continue/review)"
```

---

## CONFIGURATION FILE GENERATED

### .env.production (Sample)

```bash
# Carbon6 OiS Configuration
# Generated: 2026-02-12 19:30:45
# Mode: Production

# Application
NODE_ENV=production
PORT=3006
NEXT_PUBLIC_API_URL=http://localhost:3006

# Database
DATABASE_URL=postgresql://carbon6_admin:●●●●●●●●@localhost:5432/carbon6_ois
DATABASE_POOL_MIN=10
DATABASE_POOL_MAX=50

# Redis
REDIS_URL=redis://localhost:6379
REDIS_TLS=false

# Security (Auto-Generated)
JWT_SECRET=f8e9d7c6b5a4938271605f4e3d2c1b0a... (64 chars)
JWT_REFRESH_SECRET=a1b2c3d4e5f6978889706f5e4d3c2b1a... (64 chars)
ENCRYPTION_KEY=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p...

# Council Integration
COUNCIL_ENABLED=true
COUNCIL_API_URL=http://localhost:8080
COUNCIL_DEFAULT_CLEARANCE=L3-CONFIDENTIAL

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-●●●●●●●●
GOOGLE_API_KEY=AIzaSy●●●●●●●●
OPENAI_API_KEY=sk-proj-●●●●●●●● (optional)

# Admin Account
ADMIN_EMAIL=morpheous@carbon6.io
ADMIN_2FA_ENABLED=true

# Feature Flags
FEATURE_CONNECTOR_PROTOCOL=true
FEATURE_TERMINAL_INTERFACE=true
FEATURE_COUNCIL_INTEGRATION=true
FEATURE_CHAIRMAN_CONSOLE=false
FEATURE_88X_TRADING=false

# Monitoring
SENTRY_DSN=(optional)
LOG_LEVEL=info
```

---

## ROLLBACK CAPABILITY

```bash
👤 SCOUT: "If anything goes wrong during installation, I can roll back
to your previous state.

ROLLBACK OPTIONS:
1. Automatic rollback on critical failure
2. Manual rollback command: npm run rollback
3. Restore from backup: carbon6_backup_20260212_193045.tar.gz

Your system is protected! Let's proceed to Part 2..."
```

---

## PART 1 COMPLETION SUMMARY

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ PART 1 COMPLETE: PRE-INSTALLATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COMPLETED TASKS                                                │
│  ─────────────────────────────────────────────────────────────  │
│  ✓ System requirements validated                               │
│  ✓ Hardware compatibility confirmed                            │
│  ✓ Software dependencies checked                               │
│  ✓ Installation mode selected (Production)                     │
│  ✓ Components configured                                       │
│  ✓ Environment variables generated                             │
│  ✓ Database services installed & started                       │
│  ✓ Security keys generated                                     │
│  ✓ Backup created                                              │
│  ✓ Configuration validated                                     │
│                                                                  │
│  FILES CREATED                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  📄 .env.production         (Encrypted environment config)      │
│  📄 ecosystem.config.js     (PM2 process manager)               │
│  📄 docker-compose.yml      (Docker configuration)              │
│  📄 installation.log        (Detailed installation log)         │
│  📦 carbon6_backup.tar.gz   (Rollback archive)                  │
│                                                                  │
│  NEXT: PART 2 - MAIN INSTALLATION                              │
│  ─────────────────────────────────────────────────────────────  │
│  • Clone Carbon6 repository                                    │
│  • Install npm dependencies                                    │
│  • Build Next.js application                                   │
│  • Run Prisma migrations                                       │
│  • Seed initial data                                           │
│  • Configure PM2                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## TECHNICAL IMPLEMENTATION

### SCOUT Agent Code Structure

```typescript
// src/lib/installer/scout-agent.ts

import { AIAgent } from '@/lib/agents/base';
import { SystemRequirements } from '@/lib/installer/requirements';
import { ConfigurationWizard } from '@/lib/installer/wizard';

export class ScoutAgent extends AIAgent {
  name = 'SCOUT';
  tier = 'L1-PUBLIC';
  personality = 'helpful-devops-engineer';

  async checkSystemRequirements() {
    return await SystemRequirements.validate({
      os: ['macos', 'linux', 'windows-wsl'],
      cpu: { min: 4, recommended: 8 },
      ram: { min: 8, recommended: 16 },
      disk: { min: 20, recommended: 50 },
    });
  }

  async interactiveConfiguration() {
    const wizard = new ConfigurationWizard();

    return await wizard.run([
      'selectInstallationMode',
      'selectComponents',
      'configureDatabases',
      'configureAPIs',
      'reviewAndConfirm',
    ]);
  }

  async prepareInstallation(config) {
    // Generate secure environment files
    // Install system dependencies
    // Create database
    // Validate configuration
    // Create backup
  }
}
```

---

**STATUS:** ✅ PART 1 COMPLETE - READY FOR PART 2

**Estimated Time for Part 1:** 5-10 minutes (interactive)
**User Interaction Required:** Yes (answering configuration questions)
**Rollback Available:** Yes (automatic backup created)

---

*"Intelligence begins with understanding the environment."*
**— SCOUT, Installation Agent**
