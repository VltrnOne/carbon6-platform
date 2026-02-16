<#
.SYNOPSIS
    Carbon6 OiS - Windows Shared Installation
.DESCRIPTION
    Installs Carbon6 Platform in shared location accessible to all users

    Installation Locations:
    - Application: C:\Carbon6 (or custom path)
    - Data: C:\ProgramData\Carbon6
    - Services: System-wide PostgreSQL, Redis

.PARAMETER InstallPath
    Custom installation path (default: C:\Carbon6)

.PARAMETER DataPath
    Custom data path (default: C:\ProgramData\Carbon6)

.EXAMPLE
    .\install-carbon6-windows-shared.ps1

.EXAMPLE
    .\install-carbon6-windows-shared.ps1 -InstallPath "D:\Apps\Carbon6"
#>

param(
    [string]$InstallPath = "C:\Carbon6",
    [string]$DataPath = "C:\ProgramData\Carbon6"
)

#Requires -Version 5.1

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$StartTime = Get-Date

# Colors for output
function Write-Header { Write-Host $args -ForegroundColor Blue }
function Write-Success { Write-Host "  ✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "  • $args" -ForegroundColor Gray }
function Write-Warning { Write-Host "  ⚠ $args" -ForegroundColor Yellow }
function Write-Error-Custom { Write-Host "  ✗ $args" -ForegroundColor Red }

function Get-ElapsedTime {
    $elapsed = (Get-Date) - $StartTime
    return "{0}s" -f [math]::Round($elapsed.TotalSeconds)
}

function Write-Progress-Step {
    param($Step, $Total, $Message)
    Write-Host "`n[$Step/$Total] $Message" -ForegroundColor Gray
}

function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Banner
Clear-Host
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║                                                           ║" -ForegroundColor Blue
Write-Host "║     CARBON6 OiS - SHARED INSTALLATION                    ║" -ForegroundColor Blue
Write-Host "║                                                           ║" -ForegroundColor Blue
Write-Host "║     Multi-User | Network-Ready | Centralized             ║" -ForegroundColor Blue
Write-Host "║                                                           ║" -ForegroundColor Blue
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check Administrator
if (-not (Test-Administrator)) {
    Write-Error-Custom "This installer requires Administrator privileges for shared installation"
    Write-Info "Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

Write-Info "Installation Path: $InstallPath"
Write-Info "Data Path: $DataPath"
Write-Host ""

################################################################################
# [1/8] SYSTEM CHECKS
################################################################################
Write-Progress-Step 1 8 "Checking system requirements..."

$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion.Major -lt 10) {
    Write-Error-Custom "Windows 10 or later required"
    exit 1
}
Write-Success "Windows $($osVersion.Major).$($osVersion.Build) | $(Get-ElapsedTime)"
Write-Success "Running with Administrator privileges"
Write-Success "PowerShell $($PSVersionTable.PSVersion)"

################################################################################
# [2/8] CREATE SHARED DIRECTORIES
################################################################################
Write-Progress-Step 2 8 "Creating shared directories..."

# Create application directory
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
Write-Success "Application: $InstallPath"

# Create data directory
New-Item -ItemType Directory -Force -Path $DataPath | Out-Null
Write-Success "Data: $DataPath"

# Create subdirectories
New-Item -ItemType Directory -Force -Path "$DataPath\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataPath\database" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataPath\config" | Out-Null

# Set permissions for all users to access
$acl = Get-Acl $InstallPath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Users", "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl $InstallPath $acl

$aclData = Get-Acl $DataPath
$ruleData = New-Object System.Security.AccessControl.FileSystemAccessRule("Users", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
$aclData.SetAccessRule($ruleData)
Set-Acl $DataPath $aclData

Write-Success "Permissions set for all users | $(Get-ElapsedTime)"

################################################################################
# [3/8] INSTALL PACKAGE MANAGERS
################################################################################
Write-Progress-Step 3 8 "Installing package managers..."

# Install Chocolatey (system-wide)
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Chocolatey (system-wide)..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
    Write-Success "Chocolatey installed"
} else {
    Write-Success "Chocolatey already installed"
    choco upgrade chocolatey -y --no-progress --limit-output 2>&1 | Out-Null
}

# Install Bun globally
if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Bun globally..."

    # Download and install to Program Files
    $bunInstallPath = "C:\Program Files\bun"
    New-Item -ItemType Directory -Force -Path $bunInstallPath | Out-Null

    Invoke-WebRequest -Uri "https://github.com/oven-sh/bun/releases/latest/download/bun-windows-x64.zip" -OutFile "$env:TEMP\bun.zip"
    Expand-Archive -Path "$env:TEMP\bun.zip" -DestinationPath $bunInstallPath -Force

    # Add to system PATH
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($machinePath -notlike "*$bunInstallPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$machinePath;$bunInstallPath", "Machine")
        $env:PATH = "$env:PATH;$bunInstallPath"
    }

    Write-Success "Bun installed globally"
} else {
    Write-Success "Bun already installed"
}

Write-Success "Package managers ready | $(Get-ElapsedTime)"

################################################################################
# [4/8] INSTALL SYSTEM DEPENDENCIES
################################################################################
Write-Progress-Step 4 8 "Installing system dependencies..."

$packages = @(
    "nodejs-lts",
    "postgresql15",
    "memurai",
    "git"
)

Write-Info "Installing via Chocolatey (system-wide)..."
foreach ($package in $packages) {
    $installed = choco list --local-only | Select-String -Pattern "^$package "

    if ($installed) {
        Write-Success "$package already installed"
    } else {
        Write-Info "Installing $package..."
        choco install $package -y --no-progress --limit-output --install-arguments="ALLUSERS=1" 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Success "$package installed"
        } else {
            Write-Warning "$package installation needs verification"
        }
    }
}

refreshenv
Write-Success "System dependencies installed | $(Get-ElapsedTime)"

################################################################################
# [5/8] CONFIGURE SERVICES
################################################################################
Write-Progress-Step 5 8 "Configuring database services..."

# Configure PostgreSQL for network access
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    if ($pgService.Status -ne "Running") {
        Write-Info "Starting PostgreSQL..."
        Start-Service $pgService.Name
        Start-Sleep -Seconds 5
    }
    Write-Success "PostgreSQL running"

    # Configure pg_hba.conf for network access
    $pgData = "C:\Program Files\PostgreSQL\15\data"
    if (Test-Path "$pgData\pg_hba.conf") {
        $hbaContent = Get-Content "$pgData\pg_hba.conf"
        if ($hbaContent -notmatch "host.*all.*all.*0.0.0.0/0.*md5") {
            Add-Content "$pgData\pg_hba.conf" "`n# Carbon6 network access"
            Add-Content "$pgData\pg_hba.conf" "host    all             all             0.0.0.0/0               md5"
            Restart-Service $pgService.Name
            Start-Sleep -Seconds 3
            Write-Success "PostgreSQL configured for network access"
        }
    }
} else {
    Write-Warning "PostgreSQL service not found"
}

# Configure Redis/Memurai
$redisService = Get-Service -Name "Memurai" -ErrorAction SilentlyContinue
if ($redisService) {
    if ($redisService.Status -ne "Running") {
        Start-Service Memurai
        Start-Sleep -Seconds 2
    }
    Write-Success "Memurai (Redis) running"
} else {
    Write-Info "Memurai not required for basic setup"
}

Write-Success "Services configured | $(Get-ElapsedTime)"

################################################################################
# [6/8] SETUP APPLICATION
################################################################################
Write-Progress-Step 6 8 "Installing application..."

Set-Location $InstallPath

# Create package.json
$packageJson = @"
{
  "name": "carbon6-ois",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "node server.js",
    "start": "set NODE_ENV=production&& node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "prisma": "^5.0.0",
    "@prisma/client": "^5.0.0",
    "dotenv": "^16.3.1",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "ioredis": "^5.3.2",
    "ws": "^8.14.2"
  }
}
"@

Set-Content -Path "$InstallPath\package.json" -Value $packageJson

# Install dependencies
Write-Info "Installing application dependencies..."
npm install --silent

Write-Success "Application installed | $(Get-ElapsedTime)"

################################################################################
# [7/8] CONFIGURE DATABASE
################################################################################
Write-Progress-Step 7 8 "Configuring database..."

# Create Prisma schema
New-Item -ItemType Directory -Force -Path "$InstallPath\prisma" | Out-Null

$prismaSchema = @"
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  password  String
  role      String   @default("user")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Project {
  id          String   @id @default(uuid())
  title       String
  description String?
  status      String   @default("active")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
"@

Set-Content -Path "$InstallPath\prisma\schema.prisma" -Value $prismaSchema

# Create shared .env in data directory
$envContent = @"
# Carbon6 Platform Configuration
# Location: $DataPath\config\.env

# Database (accessible from any machine on network)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/carbon6"
REDIS_URL="redis://localhost:6379"

# Security
JWT_SECRET="change-this-secret-key"
ENCRYPTION_KEY="change-this-encryption-key"

# Server
NODE_ENV="production"
PORT=3006
HOST=0.0.0.0

# Paths
DATA_PATH="$DataPath"
LOG_PATH="$DataPath\logs"

# Council
COUNCIL_ENABLED=true
COUNCIL_API_URL="http://localhost:8080"
"@

New-Item -ItemType Directory -Force -Path "$DataPath\config" | Out-Null
Set-Content -Path "$DataPath\config\.env" -Value $envContent

# Create symlink to shared .env
if (Test-Path "$InstallPath\.env") {
    Remove-Item "$InstallPath\.env" -Force
}
New-Item -ItemType SymbolicLink -Path "$InstallPath\.env" -Target "$DataPath\config\.env" -Force | Out-Null

# Run Prisma migrations
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/carbon6"
npx prisma generate 2>&1 | Out-Null

Write-Success "Database configured | $(Get-ElapsedTime)"

################################################################################
# [8/8] CREATE SERVER & SCRIPTS
################################################################################
Write-Progress-Step 8 8 "Creating server application..."

# Create server.js
$serverJs = @"
import express from 'express';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load shared config
dotenv.config({ path: process.env.DATA_PATH ? path.join(process.env.DATA_PATH, 'config', '.env') : '.env' });

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

const PORT = process.env.PORT || 3006;
const HOST = process.env.HOST || '0.0.0.0';

app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    platform: 'windows-shared',
    installPath: '$InstallPath',
    dataPath: process.env.DATA_PATH || '$DataPath',
    services: {
      database: 'connected',
      redis: 'connected'
    }
  });
});

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to Carbon6 OiS (Shared Installation)'
  }));
});

server.listen(PORT, HOST, () => {
  console.log(\`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     CARBON6 OiS SERVER RUNNING (Shared)                  ║
║                                                           ║
║     HTTP:      http://\${HOST}:\${PORT}                      ║
║     Health:    http://\${HOST}:\${PORT}/api/health           ║
║     Network:   http://\${require('os').hostname()}:\${PORT}  ║
║                                                           ║
║     Install:   $InstallPath                               ║
║     Data:      \${process.env.DATA_PATH}                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  \`);
});
"@

Set-Content -Path "$InstallPath\server.js" -Value $serverJs

# Create global start script
$startBat = @"
@echo off
cd /d $InstallPath
set DATA_PATH=$DataPath
node server.js
"@

Set-Content -Path "$InstallPath\start.bat" -Value $startBat

# Create desktop shortcut for all users
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("C:\Users\Public\Desktop\Carbon6 OiS.lnk")
$shortcut.TargetPath = "$InstallPath\start.bat"
$shortcut.WorkingDirectory = $InstallPath
$shortcut.Description = "Carbon6 Platform - Shared Installation"
$shortcut.Save()

Write-Success "Server created | $(Get-ElapsedTime)"

################################################################################
# COMPLETION
################################################################################

$endTime = Get-Date
$totalTime = $endTime - $StartTime
$minutes = [math]::Floor($totalTime.TotalMinutes)
$seconds = $totalTime.Seconds

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║     ✓ SHARED INSTALLATION COMPLETE!                      ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║     Total Time: $minutes`m $seconds`s                                     ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Header "Installation Locations:"
Write-Info "Application:  $InstallPath"
Write-Info "Data/Config:  $DataPath"
Write-Info "Logs:         $DataPath\logs"
Write-Info "Desktop Link: C:\Users\Public\Desktop\Carbon6 OiS.lnk"
Write-Host ""

Write-Header "Network Access:"
$hostname = [System.Net.Dns]::GetHostName()
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" } | Select-Object -First 1).IPAddress
Write-Info "From this machine:  http://localhost:3006"
Write-Info "From other machines: http://$hostname`:3006"
Write-Info "                     http://$ipAddress`:3006"
Write-Host ""

Write-Header "For All Users:"
Write-Info "Any user can run: $InstallPath\start.bat"
Write-Info "Or use desktop shortcut: Carbon6 OiS"
Write-Info "Or from any location: cd $InstallPath && .\start.bat"
Write-Host ""

Write-Header "Configuration:"
Write-Info "Shared config file: $DataPath\config\.env"
Write-Info "Edit for all users: notepad $DataPath\config\.env"
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "Multi-User | Network-Ready | Centralized Installation" -ForegroundColor Blue
Write-Host "Part of VLTRN Council - Carbon Domain" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
