# Carbon6 Platform - Windows Installation Guide

## Quick Start

### One-Line Install (PowerShell)

Open **PowerShell as Administrator** and run:

```powershell
irm https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows.ps1 | iex
```

**OR download and run manually:**

```powershell
# Download
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows.ps1" -OutFile "$env:TEMP\install-carbon6.ps1"

# Run
& "$env:TEMP\install-carbon6.ps1"
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (Build 19041+) | Windows 11 |
| **PowerShell** | 5.1 | 7.x |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 5 GB free | 10 GB free |
| **Admin Rights** | Recommended | Required for services |

---

## What Gets Installed

### Package Managers
- **Chocolatey** - Windows package manager
- **Bun** - Ultra-fast JavaScript runtime (10x faster than npm)

### System Dependencies
- **Node.js 20** (LTS)
- **PostgreSQL 15** - Database server
- **Memurai** - Redis-compatible in-memory data store for Windows
- **Git** - Version control

### Application Components
- **Express Server** - HTTP + WebSocket server
- **Prisma ORM** - Database toolkit
- **Carbon6 Platform** - Full application

---

## Installation Steps

The installer performs 7 steps:

```
[1/7] System Requirements Check
      ✓ Windows 10/11 version
      ✓ PowerShell 5.1+
      ✓ Administrator privileges

[2/7] Package Managers
      ✓ Chocolatey installation
      ✓ Bun installation

[3/7] System Dependencies
      ✓ Node.js 20
      ✓ PostgreSQL 15
      ✓ Memurai (Redis)
      ✓ Git

[4/7] Start Services
      ✓ PostgreSQL service
      ✓ Memurai service
      ✓ Create carbon6 database

[5/7] Application Dependencies
      ✓ Bun install (fast!)
      ✓ Node modules

[6/7] Database Schema
      ✓ Prisma migrations
      ✓ Generate Prisma client

[7/7] Server Creation
      ✓ Create server.js
      ✓ Create start scripts
      ✓ Configure environment
```

**Target Time:** < 20 minutes (10-15 min on fast systems)

---

## After Installation

### Start the Server

**Option 1: PowerShell**
```powershell
cd $env:USERPROFILE\Carbon6
.\start.ps1
```

**Option 2: Command Prompt**
```cmd
cd %USERPROFILE%\Carbon6
start.bat
```

**Option 3: Bun directly**
```powershell
cd $env:USERPROFILE\Carbon6
bun run dev
```

### Test the Installation

```powershell
# Health check
curl http://localhost:3006/api/health

# Or in browser
start http://localhost:3006/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T...",
  "platform": "windows",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

---

## Configuration

### Environment Variables

Edit `%USERPROFILE%\Carbon6\.env`:

```env
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/carbon6"
REDIS_URL="redis://localhost:6379"

# Security (CHANGE THESE!)
JWT_SECRET="your-secret-key-here"
ENCRYPTION_KEY="your-encryption-key-here"

# Node
NODE_ENV="development"
PORT=3006

# Council
COUNCIL_ENABLED=true
COUNCIL_API_URL="http://localhost:8080"
```

### PostgreSQL Default Credentials
- **Username:** `postgres`
- **Password:** `postgres` (set during installation)
- **Port:** `5432`

**⚠️ Change the password for production:**
```powershell
# Open pgAdmin or psql
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
# Then: ALTER USER postgres WITH PASSWORD 'new_secure_password';
```

---

## Service Management

### PostgreSQL

```powershell
# Check status
Get-Service postgresql*

# Start
Start-Service postgresql-x64-15

# Stop
Stop-Service postgresql-x64-15

# Restart
Restart-Service postgresql-x64-15
```

### Memurai (Redis)

```powershell
# Check status
Get-Service Memurai

# Start
Start-Service Memurai

# Stop
Stop-Service Memurai

# Restart
Restart-Service Memurai
```

---

## Troubleshooting

### PowerShell Execution Policy

If you get "script execution is disabled" error:

```powershell
# Allow scripts (run as Administrator)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for this session only
powershell -ExecutionPolicy Bypass -File install-carbon6-windows.ps1
```

### Chocolatey Not Found

```powershell
# Refresh environment
refreshenv

# Or restart PowerShell
```

### PostgreSQL Service Won't Start

```powershell
# Check Windows Event Viewer
eventvwr.msc

# Look in: Windows Logs > Application
# Filter by Source: PostgreSQL

# Common fix: Reset data directory
& "C:\Program Files\PostgreSQL\15\bin\initdb.exe" -D "C:\Program Files\PostgreSQL\15\data"
```

### Port Already in Use

```powershell
# Find what's using port 3006
netstat -ano | findstr :3006

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Bun Not Found

```powershell
# Add to PATH manually
$env:PATH = "$env:USERPROFILE\.bun\bin;$env:PATH"

# Make permanent (run as Administrator)
[Environment]::SetEnvironmentVariable("Path", "$env:USERPROFILE\.bun\bin;$env:PATH", "User")
```

### Database Connection Failed

```powershell
# Test PostgreSQL connection
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d carbon6

# If connection fails, check:
# 1. Service is running
Get-Service postgresql*

# 2. Firewall allows port 5432
# 3. pg_hba.conf allows local connections
notepad "C:\Program Files\PostgreSQL\15\data\pg_hba.conf"
```

---

## File Locations

| Component | Location |
|-----------|----------|
| **Installation** | `%USERPROFILE%\Carbon6` |
| **PostgreSQL** | `C:\Program Files\PostgreSQL\15` |
| **Memurai** | `C:\Program Files\Memurai` |
| **Chocolatey** | `C:\ProgramData\chocolatey` |
| **Bun** | `%USERPROFILE%\.bun` |
| **Node.js** | `C:\Program Files\nodejs` |

---

## Uninstall

### Remove Application

```powershell
# Remove Carbon6 files
Remove-Item -Recurse -Force $env:USERPROFILE\Carbon6

# Remove database
& "C:\Program Files\PostgreSQL\15\bin\dropdb.exe" -U postgres carbon6
```

### Remove System Components (Optional)

```powershell
# Uninstall via Chocolatey
choco uninstall postgresql15 -y
choco uninstall memurai -y
choco uninstall nodejs-lts -y

# Or use Windows Settings > Apps
```

---

## Performance Tips

### 1. Use Windows Terminal
- Better performance than Command Prompt
- Install from Microsoft Store
- Supports tabs and split panes

### 2. Enable WSL2 (Optional)
For even better performance, consider running the Linux version in WSL2:

```powershell
# Install WSL2
wsl --install

# Then use the macOS/Linux installer
wsl
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

### 3. Exclude from Antivirus
Add these folders to Windows Defender exclusions:
- `%USERPROFILE%\Carbon6`
- `%USERPROFILE%\.bun`
- `%USERPROFILE%\node_modules`

```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "$env:USERPROFILE\Carbon6"
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.bun"
```

### 4. Use Fast Disk
- Install on SSD if available
- Avoid network drives
- Avoid OneDrive/cloud-synced folders

---

## Windows-Specific Features

### Run as Windows Service (Optional)

Create a Windows service for automatic startup:

```powershell
# Install NSSM (service wrapper)
choco install nssm -y

# Create service
nssm install Carbon6 "C:\Users\YourName\.bun\bin\bun.exe"
nssm set Carbon6 AppDirectory "$env:USERPROFILE\Carbon6"
nssm set Carbon6 AppParameters "run" "dev"

# Start service
nssm start Carbon6
```

### Task Scheduler (Alternative)

```powershell
# Create scheduled task to run at startup
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File $env:USERPROFILE\Carbon6\start.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "Carbon6" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Security Considerations

### Firewall Rules

Allow Carbon6 through Windows Firewall:

```powershell
# Allow inbound on port 3006
New-NetFirewallRule -DisplayName "Carbon6 HTTP" -Direction Inbound -LocalPort 3006 -Protocol TCP -Action Allow

# Remove rule
Remove-NetFirewallRule -DisplayName "Carbon6 HTTP"
```

### PostgreSQL Security

```sql
-- Change default password (in psql)
ALTER USER postgres WITH PASSWORD 'strong_password_here';

-- Create dedicated user for Carbon6
CREATE USER carbon6_user WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE carbon6 TO carbon6_user;
```

Update `.env`:
```env
DATABASE_URL="postgresql://carbon6_user:app_password@localhost:5432/carbon6"
```

---

## Support

### Windows-Specific Issues

- **Forum:** GitHub Discussions
- **Issues:** https://github.com/VltrnOne/carbon6-platform/issues
- **Tag:** `[Windows]` when reporting

### Logs

```powershell
# Application logs
Get-Content $env:USERPROFILE\Carbon6\install.log

# Windows Event Viewer
eventvwr.msc
```

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Windows Installation Guide
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
