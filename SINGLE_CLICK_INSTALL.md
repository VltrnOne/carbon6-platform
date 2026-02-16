# Carbon6 Platform - Single-Click Installation

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     CARBON6 OiS - SINGLE-CLICK INSTALLERS                ║
║                                                           ║
║     No Terminal Required | Just Double-Click             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

The easiest way to install Carbon6 Platform - just download and double-click!

---

## macOS Installation

### Option 1: Personal Installation (Development)

**For single-user development on your Mac**

1. **Download:** [Install Carbon6 (Personal).command](https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/Install%20Carbon6%20(Personal).command)
2. **Double-click** the downloaded file
3. Press ENTER when prompted

**Installs to:** `~/Carbon6`
**Access:** localhost only
**Time:** 15-20 minutes (first run) or 2-5 min (cached)

---

### Option 2: Shared Installation (Teams/Production)

**For multi-user access and network accessibility**

1. **Download:** [Install Carbon6 (Shared).command](https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/Install%20Carbon6%20(Shared).command)
2. **Double-click** the downloaded file
3. Enter your **Mac password** when prompted

**Installs to:** `/opt/carbon6`
**Access:** Network-accessible from other computers
**Time:** 15-20 minutes

**Features:**
- ✅ All users on Mac can access
- ✅ Available from other computers on network
- ✅ System-wide `carbon6` command
- ✅ Shared configuration

---

## Windows Installation

### Option 1: Personal Installation (Development)

**For single-user development on your PC**

1. **Download:** [Install Carbon6 (Personal).bat](https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/Install%20Carbon6%20(Personal).bat)
2. **Double-click** the downloaded file

**Installs to:** `C:\Users\YourName\Carbon6`
**Access:** localhost only
**Time:** 15-20 minutes

---

### Option 2: Shared Installation (Teams/Production)

**For multi-user access and network accessibility**

1. **Download:** [Install Carbon6 (Shared).bat](https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/Install%20Carbon6%20(Shared).bat)
2. **Right-click** → **"Run as administrator"**

**Installs to:** `C:\Carbon6`
**Access:** Network-accessible from other computers
**Time:** 15-20 minutes

**Features:**
- ✅ All users on PC can access
- ✅ Available from other computers on network
- ✅ Desktop shortcut for all users
- ✅ Shared configuration

---

## What Gets Installed

### All Platforms
- **Carbon6 Platform** - Creator collective platform
- **Express Server** - REST API + WebSocket
- **PostgreSQL 15** - Production database
- **Redis** - Session management & caching
- **Prisma** - Database ORM

### Additional (macOS)
- **Homebrew** - Package manager
- **Bun** - Fast JavaScript runtime (10x faster than npm)
- **Node.js 20** - JavaScript runtime

### Additional (Windows)
- **Chocolatey** - Package manager
- **Bun** - Fast JavaScript runtime
- **Memurai** - Redis for Windows

---

## After Installation

### macOS - Personal
```bash
# Start server
cd ~/Carbon6 && npm run dev

# Access
open http://localhost:3006
```

### macOS - Shared
```bash
# Start server
carbon6

# Access locally
open http://localhost:3006

# Access from other Macs
open http://$(hostname):3006
```

### Windows - Personal
```powershell
# Start server
cd $env:USERPROFILE\Carbon6
.\start.bat

# Access
start http://localhost:3006
```

### Windows - Shared
```powershell
# Start server (any user)
C:\Carbon6\start.bat

# Or double-click desktop shortcut

# Access locally
start http://localhost:3006

# Access from other computers
start http://$env:COMPUTERNAME:3006
```

---

## Troubleshooting

### macOS: "cannot be opened because it is from an unidentified developer"

**Fix:**
1. Right-click the `.command` file
2. Select **"Open"**
3. Click **"Open"** in the security dialog

Or via terminal:
```bash
xattr -d com.apple.quarantine "Install Carbon6 (Personal).command"
```

### Windows: "Windows protected your PC"

**Fix:**
1. Click **"More info"**
2. Click **"Run anyway"**

### Shared Install: "Administrator privileges required"

**macOS:** Run from terminal with `sudo`:
```bash
sudo bash "Install Carbon6 (Shared).command"
```

**Windows:** Right-click `.bat` file → **"Run as administrator"**

### Installation Hangs or Fails

**Check internet connection** - Installers download packages from internet

**macOS:** Check Homebrew status:
```bash
brew doctor
```

**Windows:** Check Chocolatey status:
```powershell
choco --version
```

---

## Network Access Setup

### macOS Firewall

**System Settings → Network → Firewall:**
1. Click "Options..."
2. Add Node.js or `/opt/carbon6/start.sh`
3. Select "Allow incoming connections"

### Windows Firewall

**Automatically configured** by installer

To manually configure:
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Carbon6 HTTP" -Direction Inbound -LocalPort 3006 -Protocol TCP -Action Allow
```

---

## Find Your Network Address

### macOS
```bash
# Hostname
hostname

# IP address
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet
```

### Windows
```powershell
# Hostname
$env:COMPUTERNAME

# IP address
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }).IPAddress
```

---

## Uninstall

### macOS - Personal
```bash
rm -rf ~/Carbon6
brew services stop postgresql@15
brew services stop redis
```

### macOS - Shared
```bash
sudo rm -rf /opt/carbon6
sudo rm -rf /var/lib/carbon6
sudo rm -rf /var/log/carbon6
sudo rm /usr/local/bin/carbon6
```

### Windows - Personal
```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\Carbon6
```

### Windows - Shared
```powershell
# Run as Administrator
Remove-Item -Recurse -Force C:\Carbon6
Remove-Item -Recurse -Force C:\ProgramData\Carbon6
Remove-Item "C:\Users\Public\Desktop\Carbon6 OiS.lnk"
```

---

## Full Documentation

- **macOS Shared:** [INSTALL_MACOS_SHARED.md](INSTALL_MACOS_SHARED.md)
- **Windows Personal:** [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)
- **Windows Shared:** [INSTALL_WINDOWS_SHARED.md](INSTALL_WINDOWS_SHARED.md)
- **Main README:** [README.md](README.md)

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No Terminal Required | Just Double-Click
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
