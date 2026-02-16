# Carbon6 Platform - Windows Shared Installation

## Overview

This installation method creates a **centralized, multi-user** setup accessible from any computer on your network.

### Key Differences: Personal vs Shared

| Feature | Personal Install | Shared Install |
|---------|------------------|----------------|
| **Location** | `C:\Users\YourName\Carbon6` | `C:\Carbon6` |
| **Access** | Single user only | All users on system |
| **Config** | User-specific | Shared in `C:\ProgramData\Carbon6` |
| **Network** | localhost only | Network-accessible |
| **Use Case** | Development | Production, Teams |

---

## Installation

### Requirements

- ✅ **Administrator privileges** (required for shared installation)
- ✅ Windows 10+ (Build 19041 or newer)
- ✅ PowerShell 5.1+

### One-Line Install

**Open PowerShell as Administrator:**

```powershell
irm https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows-shared.ps1 | iex
```

### Custom Installation Path

```powershell
# Download installer
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows-shared.ps1" -OutFile "$env:TEMP\install-shared.ps1"

# Run with custom paths
& "$env:TEMP\install-shared.ps1" -InstallPath "D:\Apps\Carbon6" -DataPath "D:\Data\Carbon6"
```

---

## Installation Locations

### Default Paths

```
C:\Carbon6\                    # Application files (read-only for users)
├── server.js                  # Main server
├── package.json               # Dependencies
├── prisma\                    # Database schema
├── node_modules\              # Packages
└── start.bat                  # Startup script

C:\ProgramData\Carbon6\        # Shared data (all users can modify)
├── config\
│   └── .env                   # Shared configuration
├── logs\                      # Application logs
└── database\                  # Database files (if SQLite used)

C:\Users\Public\Desktop\
└── Carbon6 OiS.lnk           # Desktop shortcut (all users)
```

### Permissions

| Location | Users Permission | Admins Permission |
|----------|------------------|-------------------|
| `C:\Carbon6\` | Read & Execute | Full Control |
| `C:\ProgramData\Carbon6\` | Modify | Full Control |
| Desktop Shortcut | Execute | Full Control |

---

## Network Access

### From This Machine

```powershell
# Local access
http://localhost:3006

# Network access (works from other computers)
http://YOUR-PC-NAME:3006
http://192.168.1.XXX:3006
```

### From Other Computers

```powershell
# Windows computers on same network
http://CARBON6-SERVER:3006/api/health

# Using IP address
http://192.168.1.100:3006/api/health
```

### Find Your Network Address

```powershell
# Get hostname
[System.Net.Dns]::GetHostName()

# Get IP address
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }).IPAddress
```

---

## Firewall Configuration

### Allow Incoming Connections

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Carbon6 HTTP" -Direction Inbound -LocalPort 3006 -Protocol TCP -Action Allow

# Verify rule created
Get-NetFirewallRule -DisplayName "Carbon6 HTTP"
```

### Remove Firewall Rule (if needed)

```powershell
Remove-NetFirewallRule -DisplayName "Carbon6 HTTP"
```

---

## Multi-User Usage

### Any User Can Start the Server

**Method 1: Desktop Shortcut**
```
Double-click "Carbon6 OiS" icon on desktop
```

**Method 2: Command Line**
```powershell
C:\Carbon6\start.bat
```

**Method 3: From Any Location**
```powershell
cd C:\Carbon6
.\start.bat
```

### Shared Configuration

All users share the same configuration:

```powershell
# Edit shared config (requires admin)
notepad C:\ProgramData\Carbon6\config\.env
```

**Any changes affect all users!**

---

## Network Deployment Scenarios

### Scenario 1: Shared Office Network

**Setup:**
- Install Carbon6 on one Windows PC
- Other team members access via network

**Example:**
```
Main PC: "OFFICE-PC-01"
Install: C:\Carbon6
Access from other PCs: http://OFFICE-PC-01:3006
```

### Scenario 2: Network Drive Installation

**Custom installation to network drive:**

```powershell
# Install to network drive (requires network drive mapped)
.\install-carbon6-windows-shared.ps1 -InstallPath "Z:\Carbon6" -DataPath "Z:\Carbon6Data"
```

**All computers can access same installation!**

### Scenario 3: Terminal Server / Remote Desktop

**Carbon6 on Windows Server:**
- Multiple users RDP into server
- All share same Carbon6 installation
- Each user sees same data

---

## Configuration

### Shared Environment Variables

Edit `C:\ProgramData\Carbon6\config\.env`:

```env
# Database (use network-accessible host if needed)
DATABASE_URL="postgresql://postgres:password@db-server:5432/carbon6"
REDIS_URL="redis://cache-server:6379"

# Server (bind to all interfaces for network access)
HOST=0.0.0.0
PORT=3006

# Paths (do not change unless custom install)
DATA_PATH="C:\ProgramData\Carbon6"
LOG_PATH="C:\ProgramData\Carbon6\logs"

# Security
JWT_SECRET="your-production-secret"
ENCRYPTION_KEY="your-encryption-key"
```

### Network-Accessible Database

**If PostgreSQL is on another server:**

```env
DATABASE_URL="postgresql://postgres:password@192.168.1.50:5432/carbon6"
```

**Configure PostgreSQL to allow network connections:**

1. Edit `pg_hba.conf`:
   ```
   host    all             all             0.0.0.0/0               md5
   ```

2. Edit `postgresql.conf`:
   ```
   listen_addresses = '*'
   ```

3. Restart PostgreSQL service

---

## Service Management

### Run as Windows Service (Optional)

**Install NSSM (service wrapper):**

```powershell
choco install nssm -y
```

**Create service:**

```powershell
nssm install Carbon6 "C:\Program Files\nodejs\node.exe"
nssm set Carbon6 AppDirectory "C:\Carbon6"
nssm set Carbon6 AppParameters "server.js"
nssm set Carbon6 AppEnvironmentExtra "DATA_PATH=C:\ProgramData\Carbon6"
nssm set Carbon6 Description "Carbon6 OiS Platform - Shared Installation"
nssm set Carbon6 Start SERVICE_AUTO_START

# Start service
nssm start Carbon6
```

**Service benefits:**
- ✅ Starts automatically on boot
- ✅ Runs even when no user logged in
- ✅ Managed via Windows Services
- ✅ Automatic restart on failure

### Service Commands

```powershell
# Start
nssm start Carbon6

# Stop
nssm stop Carbon6

# Restart
nssm restart Carbon6

# Remove service
nssm remove Carbon6 confirm
```

---

## Monitoring & Logs

### View Logs

```powershell
# Real-time log viewing
Get-Content C:\ProgramData\Carbon6\logs\app.log -Wait

# Last 50 lines
Get-Content C:\ProgramData\Carbon6\logs\app.log -Tail 50
```

### Event Viewer Integration

Application events are logged to Windows Event Viewer:

```powershell
# Open Event Viewer
eventvwr.msc

# View: Windows Logs > Application
# Filter by Source: "Carbon6"
```

---

## Security Considerations

### 1. File Permissions

**Verify permissions:**

```powershell
# Check application permissions
Get-Acl C:\Carbon6 | Format-List

# Check data permissions
Get-Acl C:\ProgramData\Carbon6 | Format-List
```

### 2. Network Security

**Restrict access by IP:**

```powershell
# Allow only specific network
New-NetFirewallRule -DisplayName "Carbon6 HTTP (LAN Only)" `
    -Direction Inbound -LocalPort 3006 -Protocol TCP -Action Allow `
    -RemoteAddress 192.168.1.0/24
```

### 3. HTTPS/SSL (Recommended for production)

Use reverse proxy (nginx or IIS) for SSL:

```powershell
# Install IIS URL Rewrite
choco install iis-arr -y

# Configure reverse proxy:
# External: https://carbon6.yourdomain.com
# Internal: http://localhost:3006
```

---

## Backup & Recovery

### Backup Shared Configuration

```powershell
# Backup data directory
$backupPath = "C:\Backups\Carbon6_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Recurse C:\ProgramData\Carbon6 $backupPath

Write-Host "Backed up to: $backupPath"
```

### Automated Backup (Task Scheduler)

```powershell
# Create scheduled backup task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @"
-Command "Copy-Item -Recurse C:\ProgramData\Carbon6 'C:\Backups\Carbon6_`$(Get-Date -Format 'yyyyMMdd')' -Force"
"@

$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "Carbon6 Backup" -Action $action -Trigger $trigger -RunLevel Highest
```

### Restore from Backup

```powershell
# Stop service
nssm stop Carbon6

# Restore data
Copy-Item -Recurse C:\Backups\Carbon6_20260212 C:\ProgramData\Carbon6 -Force

# Restart service
nssm start Carbon6
```

---

## Troubleshooting

### Cannot Access from Other Computers

**Check:**

1. Firewall allows port 3006
2. Server is bound to `0.0.0.0` (not `127.0.0.1`)
3. Both computers on same network
4. Windows firewall not blocking

```powershell
# Test from remote computer
Test-NetConnection -ComputerName CARBON6-SERVER -Port 3006
```

### Permission Denied Errors

**Fix:**

```powershell
# Run as Administrator
$path = "C:\ProgramData\Carbon6"
$acl = Get-Acl $path
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Users", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl $path $acl
```

### Database Connection Failed from Network

**Configure PostgreSQL:**

1. Allow network connections in `postgresql.conf`:
   ```
   listen_addresses = '*'
   ```

2. Allow authentication in `pg_hba.conf`:
   ```
   host    all             all             0.0.0.0/0               md5
   ```

3. Restart PostgreSQL

---

## Uninstall

### Complete Removal

```powershell
# Run as Administrator

# Stop service (if installed)
nssm stop Carbon6
nssm remove Carbon6 confirm

# Remove application
Remove-Item -Recurse -Force C:\Carbon6

# Remove data
Remove-Item -Recurse -Force C:\ProgramData\Carbon6

# Remove desktop shortcut
Remove-Item "C:\Users\Public\Desktop\Carbon6 OiS.lnk"

# Remove firewall rule
Remove-NetFirewallRule -DisplayName "Carbon6 HTTP"
```

### Keep Data (Remove Application Only)

```powershell
# Remove application but keep data/config
Remove-Item -Recurse -Force C:\Carbon6
# Data remains in C:\ProgramData\Carbon6
```

---

## Summary

**Shared Installation Benefits:**

✅ **Accessible to all users** on the system
✅ **Network-ready** - accessible from other computers
✅ **Centralized configuration** - one .env for everyone
✅ **Service mode** - runs automatically on boot
✅ **Production-ready** - designed for team/enterprise use

**Best for:**
- Office environments
- Team collaboration
- Production deployments
- Network services
- Multi-user systems

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Multi-User | Network-Ready | Centralized Installation
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
