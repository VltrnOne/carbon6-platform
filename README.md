# Carbon6 Platform

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     CARBON[6] PLATFORM                                    ║
║                                                           ║
║     Lead. Mentor. Build.                                  ║
║     Pressure Creates.                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**The complete Carbon6 creator collective platform - unified installation system.**

---

## 🚀 One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

This installs:
- ✅ **Carbon Collective SDK** - Team collaboration & auto-sync system
- ✅ **Carbon6 Platform** - Marketing website & creator portal
- ✅ **Environment Configuration** - Pre-configured `.env` templates
- ✅ **CLI Tools** - Global `carbon` command for project management

---

## 📋 What Gets Installed

### 1. Carbon Collective SDK (`~/carbon-collective`)
- **Purpose**: Team collaboration & project syncing
- **Tech**: TypeScript, Bun/npm, File watching
- **Commands**: `carbon init`, `carbon track`, `carbon watch`

### 2. Carbon6 Platform (`~/Carbon6`)
- **Purpose**: Marketing site & creator portal
- **Tech**: Vite, GSAP, Vanilla JS
- **Runs on**: `localhost:5173` (dev)

### 3. Helper Scripts (`~/carbon6-platform`)
- `start-sdk.sh` - Launch SDK dev server
- `start-platform.sh` - Launch platform dev server
- `build-platform.sh` - Build & preview production

---

## 🎯 Quick Start

### After Installation

```bash
# 1. Initialize your profile (one time)
carbon init --name "Your Name"

# 2. Start the platform website
cd ~/Carbon6
npm run dev  # or bun run dev

# Visit: http://localhost:5173

# 3. Track any project
cd ~/your-client-project
carbon track

# 4. Enable auto-sync (every 30 seconds)
carbon watch
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Your Projects (~/any-project/)                             │
│  • Work happens here                                        │
│  • Files auto-sync via carbon watch                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Carbon Collective (~/carbon-collective/)                   │
│  • SDK: CLI tools for tracking                              │
│  • Projects: All synced work organized by creator           │
│  • Docs: Team guides & onboarding                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Carbon6 Platform (~/Carbon6/)                              │
│  • Marketing: Public-facing website                         │
│  • Portal: Creator dashboard (future)                       │
│  • API: Backend services (future)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 10.15+, Ubuntu 20.04+, Windows 10+ | Latest stable |
| **Node.js** | 18.x | 20.x (LTS) |
| **Package Manager** | npm 9+ | **bun 1.0+** (faster) |
| **Git** | 2.30+ | Latest |
| **Memory** | 4 GB RAM | 8 GB RAM |
| **Disk** | 1 GB free | 5 GB free |

### Optional but Recommended
- **GitHub CLI** (`gh`) - For faster cloning
- **bun** - 5-10x faster than npm

---

## 📦 Installation Methods

### Method 1: Remote Install (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

### Method 2: Manual Install
```bash
# Clone repositories
gh repo clone VltrnOne/carbon-collective ~/carbon-collective
gh repo clone VltrnOne/Carbon6 ~/Carbon6

# Install SDK
cd ~/carbon-collective/sdk
bun install && bun link

# Install Platform
cd ~/Carbon6
bun install

# Initialize
carbon init --name "Your Name"
```

### Method 3: Developer Install
```bash
# Clone with write access (requires auth)
gh repo clone VltrnOne/carbon-collective ~/carbon-collective
gh repo clone VltrnOne/Carbon6 ~/Carbon6

cd ~/carbon-collective/sdk
bun install
bun link

cd ~/Carbon6
bun install
cp .env.example .env  # Configure environment

# Start dev servers
bun run dev  # Platform on :5173
```

---

## 🎓 Carbon Tier System

The Carbon6 platform operates on a three-tier progression system:

| Tier | Badge | Revenue Split | Philosophy |
|------|-------|---------------|------------|
| **Carbon** | `[C]` | 50/50 | Execute, learn, prove |
| **Carbon[6]** | `[C6]` | 65/35 | Lead, mentor, build |
| **Black Ops** | `[6]` | 80/20 | Govern, innovate, impossible |

### Tier Progression
- **[C] → [C6]**: Proven execution + mentoring capability
- **[C6] → [6]**: System building + innovation leadership

---

## 📚 SDK Commands Reference

### Initialization
```bash
carbon init --name "Your Name"          # First-time setup
carbon init --name "New Name" --reset   # Reset profile
```

### Project Management
```bash
carbon track                  # Start tracking current directory
carbon untrack               # Stop tracking current directory
carbon list                  # List all tracked projects
carbon status                # Show profile & sync status
```

### Syncing
```bash
carbon sync                  # Manual sync now
carbon watch                 # Auto-sync every 30 seconds (Ctrl+C to stop)
carbon watch --interval 60   # Custom interval (seconds)
```

### Information
```bash
carbon --help                # Show all commands
carbon --version             # Show version
```

---

## 🌐 Platform Development

### Start Development Server
```bash
cd ~/Carbon6
bun run dev

# Platform available at: http://localhost:5173
```

### Build for Production
```bash
cd ~/Carbon6
bun run build          # Build optimized bundle
bun run preview        # Preview production build
```

### Run Tests
```bash
bun run test           # Run all tests
bun run test:watch     # TDD mode
bun run lint           # Lint check
bun run lint:fix       # Auto-fix issues
```

---

## 🔒 Environment Configuration

### SDK Environment (`~/carbon-collective/.env`)
```env
# Carbon Collective SDK
CARBON_API_URL=https://api.carbon6.dev
CARBON_SYNC_INTERVAL=30
CARBON_MAX_FILE_SIZE=10485760  # 10MB
```

### Platform Environment (`~/Carbon6/.env`)
```env
NODE_ENV=development
PORT=5173

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/carbon6

# API Keys (optional)
STRIPE_SECRET_KEY=sk_test_...
CLAUDE_API_KEY=sk-ant-...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## 🛠️ Troubleshooting

### "carbon: command not found"
```bash
# Re-link the SDK
cd ~/carbon-collective/sdk
bun link

# Or restart your terminal
exec $SHELL
```

### "Permission denied" during install
```bash
# Use sudo only if necessary
sudo chown -R $(whoami) ~/carbon-collective ~/Carbon6
```

### Port 5173 already in use
```bash
# Change port in Carbon6/.env
PORT=3000

# Or kill existing process
lsof -ti:5173 | xargs kill -9
```

### Sync not working
```bash
# Check carbon status
carbon status

# Verify Git config
cd ~/carbon-collective
git config --get user.name
git config --get user.email

# Re-initialize if needed
carbon init --reset
```

---

## 📁 Directory Structure

After installation, your system will have:

```
~/
├── carbon6-platform/          # Installation scripts
│   ├── remote-install.sh      # Main installer
│   ├── start-sdk.sh           # SDK launcher
│   ├── start-platform.sh      # Platform launcher
│   └── build-platform.sh      # Production builder
│
├── carbon-collective/         # SDK & Team Workspace
│   ├── sdk/                   # CLI tool source
│   ├── projects/              # Synced creator work
│   │   ├── creator-one/
│   │   └── creator-two/
│   ├── docs/                  # Team documentation
│   ├── CLAUDE.md              # AI instructions
│   └── README.md
│
└── Carbon6/                   # Platform Website
    ├── src/                   # Source code
    ├── public/                # Static assets
    ├── platform/              # Platform modules
    ├── blockchain/            # Web3 integration
    ├── dist/                  # Build output
    └── README.md
```

---

## 🚀 Advanced Usage

### Custom Installation Location
```bash
# Download installer
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh -o install.sh

# Edit paths in script
nano install.sh

# Run custom install
bash install.sh
```

### Development Workflow
```bash
# Terminal 1: SDK Development
cd ~/carbon-collective/sdk
bun run dev

# Terminal 2: Platform Development
cd ~/Carbon6
bun run dev

# Terminal 3: Live Syncing
carbon watch
```

---

## 🤝 Contributing

Carbon6 Platform is maintained by the VLTRN Council Carbon Domain team.

### For Carbon Members
1. All work auto-syncs via `carbon watch`
2. Update `carbon-collective/CLAUDE.md` with learnings
3. Follow tier-specific contribution guidelines

### For External Contributors
- Issues: https://github.com/VltrnOne/carbon6-platform/issues
- Discussions: https://github.com/VltrnOne/carbon6-platform/discussions

---

## 📄 License

ISC License - See individual repositories for details.

---

## 🔗 Links

- **SDK Repository**: https://github.com/VltrnOne/carbon-collective
- **Platform Repository**: https://github.com/VltrnOne/Carbon6
- **Documentation**: https://docs.carbon6.dev (coming soon)
- **Team Portal**: https://portal.carbon6.dev (coming soon)

---

## 💬 Support

### For Carbon Team Members
- **Discord**: #carbon-support channel
- **Internal Docs**: `~/carbon-collective/docs/`

### For External Users
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Community Q&A

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pressure Creates.
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Carbon6** - Where capable creators become leaders.
