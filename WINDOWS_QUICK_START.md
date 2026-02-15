# Windows Quick Start - Carbon6 Platform

## 🚀 60-Second Install

### 1. Open PowerShell as Administrator

**Windows 10/11:**
- Press `Win + X`
- Click "Windows PowerShell (Admin)" or "Terminal (Admin)"

### 2. Run One Command

```powershell
irm https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows.ps1 | iex
```

### 3. Wait 15-20 Minutes

The installer will:
- ✅ Install Chocolatey
- ✅ Install Bun (fast package manager)
- ✅ Install PostgreSQL 15
- ✅ Install Memurai (Redis)
- ✅ Configure services
- ✅ Set up database
- ✅ Install Carbon6 Platform

### 4. Start the Server

```powershell
cd $env:USERPROFILE\Carbon6
.\start.ps1
```

### 5. Test

Open browser: http://localhost:3006/api/health

---

## 📋 What You Get

```
%USERPROFILE%\Carbon6\
├── server.js          # Express + WebSocket server
├── package.json       # Dependencies
├── .env              # Configuration
├── prisma\           # Database schema
├── start.ps1         # PowerShell start script
└── start.bat         # Batch start script
```

**Services Running:**
- PostgreSQL on port 5432
- Memurai (Redis) on port 6379
- Carbon6 API on port 3006

---

## ⚡ Quick Commands

```powershell
# Start server
cd $env:USERPROFILE\Carbon6
.\start.ps1

# Check services
Get-Service postgresql*
Get-Service Memurai

# Edit configuration
notepad .env

# View logs
Get-Content install.log

# Test health endpoint
curl http://localhost:3006/api/health
```

---

## 🔧 Common Issues

### "Execution Policy" Error

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Chocolatey Not Found

```powershell
refreshenv
# Or restart PowerShell
```

### Port 3006 In Use

```powershell
# Find process using port
netstat -ano | findstr :3006

# Kill process (replace 1234 with actual PID)
taskkill /PID 1234 /F
```

### PostgreSQL Won't Start

```powershell
# Restart service
Restart-Service postgresql-x64-15

# Check Event Viewer for errors
eventvwr.msc
```

---

## 📖 Full Documentation

- **Complete Guide:** [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)
- **Troubleshooting:** See INSTALL_WINDOWS.md § Troubleshooting
- **Service Management:** See INSTALL_WINDOWS.md § Service Management
- **Security:** See INSTALL_WINDOWS.md § Security Considerations

---

## 🆘 Support

**Issues:** https://github.com/VltrnOne/carbon6-platform/issues
**Tag:** `[Windows]` when reporting Windows-specific issues

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Windows 10/11 Optimized Installation
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
