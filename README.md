# Carbon6 OiS - Executable Installation SDK

**Version:** 1.0.0
**Release:** February 12, 2026
**Classification:** L5-BLACK

---

## 🚀 Quick Start

### One-Command Installation

```bash
./install-carbon6.sh
```

That's it! The agentic installer will guide you through the entire process.

---

## 📦 What's Included

This executable installation SDK contains:

### Main Installer
- **install-carbon6.sh** - Interactive menu-driven installer with AI agents

### Installation Scripts
- **scripts/install-part-0.sh** - System prerequisites (PRAXIS)
- **scripts/install-part-1.sh** - Pre-installation configuration (SCOUT)
- **scripts/install-part-2.sh** - Main installation (GENESIS)
- **scripts/install-part-3.sh** - Post-installation setup (SOVEREIGN)

### Helper Scripts
- **scripts/create-admin.ts** - Admin account creation
- **scripts/backup-database.sh** - Automated database backups

### Documentation
- **CARBON6_OIS_COMPLETE_INSTALLATION_GUIDE.md** - Complete reference
- **CARBON6_OIS_INSTALLER_PART_0.md** - Detailed Part 0 guide
- **CARBON6_OIS_INSTALLER_PART_1.md** - Detailed Part 1 guide
- **CARBON6_OIS_INSTALLER_PART_2.md** - Detailed Part 2 guide
- **CARBON6_OIS_INSTALLER_PART_3.md** - Detailed Part 3 guide

---

## 🎯 Installation Modes

### 1. Full Installation (Recommended)
Complete production setup with all features.

```bash
./install-carbon6.sh
# Select option 1
```

**Includes:**
- System prerequisites
- PostgreSQL database
- Redis cache
- PM2 cluster mode
- 462 Council agents
- 88x™ Chairman Console
- Monitoring & backups

**Duration:** 40-65 minutes

---

### 2. Quick Start (Developer Mode)
Fast setup for local development.

```bash
./install-carbon6.sh
# Select option 2
```

**Includes:**
- Essential prerequisites
- SQLite database
- Single instance
- Core features only

**Duration:** 25 minutes

---

### 3. Custom Installation
Choose exactly what you need.

```bash
./install-carbon6.sh
# Select option 3
```

**Options:**
- Installation mode (Developer/Production/Docker)
- Components (Core/Connector/Terminal/Council/88x™)
- Custom configuration

**Duration:** 30-50 minutes

---

## 🤖 The Four AI Agents

### PRAXIS (Operations Director)
**Part 0: System Prerequisites**

```
👤 PRAXIS: "I ensure the foundation is solid before we build."
```

Installs:
- Homebrew
- Node.js 20, Python 3.12, Go 1.21
- PostgreSQL 15, Redis 7
- Development tools
- Global NPM packages
- SSH keys

---

### SCOUT (Discovery Agent)
**Part 1: Pre-Installation**

```
👤 SCOUT: "I'm your installation guide and DevOps engineer."
```

Configures:
- Installation mode
- Component selection
- Environment variables
- Database connection
- Security keys

---

### GENESIS (Divine Orchestrator)
**Part 2: Main Installation**

```
👤 GENESIS: "I coordinate parallel operations for maximum efficiency."
```

Executes:
- Repository verification
- Dependency installation (156+ packages)
- Database migration
- Application build
- Service startup

---

### SOVEREIGN (Strategic Command)
**Part 3: Post-Installation**

```
👤 SOVEREIGN: "I configure for operational excellence."
```

Establishes:
- Admin account
- First creator
- Council integration
- 88x™ console
- Monitoring
- Backups

---

## 📝 Usage Examples

### Full Production Installation

```bash
# Run interactive installer
./install-carbon6.sh

# Select Full Installation
> 1

# Follow PRAXIS agent's guidance
# Confirm each step
# Wait for completion (40-65 min)

# Access your system
open http://localhost:3006
```

---

### Individual Parts

Run each part separately for more control:

```bash
# Part 0: System prerequisites
./scripts/install-part-0.sh

# Part 1: Configuration
./scripts/install-part-1.sh

# Part 2: Main installation
./scripts/install-part-2.sh

# Part 3: Post-setup
./scripts/install-part-3.sh
```

---

### Automated Installation

For CI/CD or unattended installation:

```bash
# Set environment variables
export INSTALL_MODE="production"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="SecurePassword123!"

# Run all parts
./scripts/install-part-0.sh && \
./scripts/install-part-1.sh && \
./scripts/install-part-2.sh && \
./scripts/install-part-3.sh
```

---

## 🔧 Configuration

### Environment Variables

Create or edit `.env` file:

```bash
# Database
DATABASE_URL="postgresql://localhost/carbon6"

# Redis
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

### Installation State

Track installation progress:

```bash
cat .install-state.json
```

### Installation Log

View detailed logs:

```bash
tail -f installation.log
```

---

## ✅ Verification

After installation, verify everything is working:

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

## 🛠️ Troubleshooting

### Installation Failed

```bash
# View error logs
cat installation.log

# Check specific part logs
pm2 logs

# Restart services
pm2 restart all
```

### Port Already in Use

```bash
# Find process on port 3006
lsof -i :3006

# Kill process
kill -9 <PID>

# Or use different port
PORT=3007 npm start
```

### Database Issues

```bash
# Reset database
npx prisma db push --force-reset

# Check PostgreSQL
pg_isready
brew services restart postgresql@15

# Check Redis
redis-cli ping
brew services restart redis
```

### Permission Errors

```bash
# Fix script permissions
chmod +x install-carbon6.sh
chmod +x scripts/*.sh

# Fix .env permissions
chmod 600 .env
```

---

## 📊 Installation Checklist

Use this checklist to track your installation:

- [ ] System requirements met (macOS, 8GB RAM, internet)
- [ ] Part 0: Homebrew, Node.js, PostgreSQL, Redis installed
- [ ] Part 1: Installation mode selected, .env configured
- [ ] Part 2: Dependencies installed, application built
- [ ] Part 3: Admin created, backups scheduled
- [ ] Health check passed (http://localhost:3006/api/health)
- [ ] Terminal accessible (http://localhost:3006/terminal)
- [ ] Console accessible (http://localhost:3006/console)

---

## 🔒 Security Notes

### Credentials

**Never commit these files:**
- `.env` - Contains secrets
- `.install-state.json` - Contains installation info
- `installation.log` - May contain sensitive data

### SSH Keys

Your SSH keys are generated in `~/.ssh/`:
- `id_ed25519` - Private key (keep secure!)
- `id_ed25519.pub` - Public key (add to GitHub)

### Admin Account

Change the default admin password immediately:
```bash
# Access admin dashboard
open http://localhost:3006/admin

# Login with credentials
# Change password in settings
```

---

## 📚 Additional Resources

### Documentation
- Complete Guide: `CARBON6_OIS_COMPLETE_INSTALLATION_GUIDE.md`
- API Reference: `/docs/API_REFERENCE.md`
- SDK Docs: `/sdk-templates/*/README.md`

### Support
- GitHub Issues: https://github.com/vltrn/carbon6-platform/issues
- Email: support@carbon6.io
- Discord: https://discord.gg/carbon6

### Commands
```bash
# View all install scripts
ls -lh scripts/install-*.sh

# Read documentation
cat CARBON6_OIS_COMPLETE_INSTALLATION_GUIDE.md

# Check version
./install-carbon6.sh --version
```

---

## 🎉 Next Steps

After successful installation:

1. **Login to Admin Dashboard**
   ```bash
   open http://localhost:3006/admin
   ```

2. **Create Your First Project**
   ```bash
   open http://localhost:3006/terminal
   > project create --title "My First Project"
   ```

3. **Test Council Agents**
   ```bash
   > agent invoke GENESIS --prompt "System status"
   ```

4. **Explore 88x™ Console**
   ```bash
   open http://localhost:3006/console
   ```

5. **Configure Backups**
   ```bash
   ./scripts/backup-database.sh
   ```

---

## 📄 License

Copyright © 2026 VLTRN AGENCY
Classification: L5-BLACK | Sovereign Technology

---

**Ready to Install?**

```bash
./install-carbon6.sh
```

**Welcome to Carbon6 - Operational Intelligence for the Sovereign Era.**

```
INSTALLATION SDK v1.0.0
Document ID: L5-SDK-2026-001
Classification: L5-BLACK | February 12, 2026
```
