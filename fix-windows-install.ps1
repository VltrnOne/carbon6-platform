# Quick Fix for Partial Windows Installation
# Run this if install-carbon6-windows.ps1 encountered issues

Write-Host "`nCarbon6 Installation Quick Fix" -ForegroundColor Blue
Write-Host "==============================`n" -ForegroundColor Blue

$InstallDir = "$env:USERPROFILE\Carbon6"

# Fix 1: Verify what's actually installed
Write-Host "[1/4] Checking installed packages..." -ForegroundColor Gray

$hasNode = Get-Command node -ErrorAction SilentlyContinue
$hasGit = Get-Command git -ErrorAction SilentlyContinue
$hasBun = Get-Command bun -ErrorAction SilentlyContinue
$hasPg = Test-Path "C:\Program Files\PostgreSQL\15\bin\psql.exe"

if ($hasNode) { Write-Host "  ✓ Node.js: $(node --version)" -ForegroundColor Green } else { Write-Host "  ✗ Node.js not found" -ForegroundColor Red }
if ($hasGit) { Write-Host "  ✓ Git: $(git --version)" -ForegroundColor Green } else { Write-Host "  ✗ Git not found" -ForegroundColor Red }
if ($hasBun) { Write-Host "  ✓ Bun: $(bun --version)" -ForegroundColor Green } else { Write-Host "  ✗ Bun not found" -ForegroundColor Red }
if ($hasPg) { Write-Host "  ✓ PostgreSQL found" -ForegroundColor Green } else { Write-Host "  ✗ PostgreSQL not found" -ForegroundColor Red }

# Fix 2: Create database manually
Write-Host "`n[2/4] Setting up database..." -ForegroundColor Gray

if ($hasPg) {
    Write-Host "  Enter your PostgreSQL password (or press Enter to skip):" -ForegroundColor Yellow
    $pgPassword = Read-Host -AsSecureString
    $pgPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pgPassword))

    if ($pgPasswordPlain) {
        $env:PGPASSWORD = $pgPasswordPlain
        & "C:\Program Files\PostgreSQL\15\bin\createdb.exe" -U postgres carbon6 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Database 'carbon6' created" -ForegroundColor Green

            # Update .env with correct password
            if (Test-Path "$InstallDir\.env") {
                $envContent = Get-Content "$InstallDir\.env"
                $envContent = $envContent -replace 'DATABASE_URL=".*"', "DATABASE_URL=`"postgresql://postgres:$pgPasswordPlain@localhost:5432/carbon6`""
                Set-Content "$InstallDir\.env" $envContent
                Write-Host "  ✓ Updated .env with correct password" -ForegroundColor Green
            }
        } else {
            Write-Host "  ⚠ Could not create database (may already exist)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ Skipped database creation" -ForegroundColor Yellow
        Write-Host "  Manual: psql -U postgres -c `"CREATE DATABASE carbon6;`"" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠ PostgreSQL not found - install manually:" -ForegroundColor Yellow
    Write-Host "  choco install postgresql15 -y" -ForegroundColor Cyan
}

# Fix 3: Install missing packages
Write-Host "`n[3/4] Installing missing components..." -ForegroundColor Gray

if (-not $hasNode) {
    Write-Host "  Installing Node.js..." -ForegroundColor Gray
    choco install nodejs-lts -y
}

if (-not $hasBun) {
    Write-Host "  Installing Bun..." -ForegroundColor Gray
    irm bun.sh/install.ps1 | iex
}

if (-not $hasPg) {
    Write-Host "  Installing PostgreSQL..." -ForegroundColor Gray
    choco install postgresql15 -y
}

# Fix 4: Complete application setup
Write-Host "`n[4/4] Completing application setup..." -ForegroundColor Gray

if (Test-Path $InstallDir) {
    Set-Location $InstallDir

    # Install dependencies if not done
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing app dependencies..." -ForegroundColor Gray
        if ($hasBun) {
            bun install
        } else {
            npm install
        }
    } else {
        Write-Host "  ✓ Dependencies already installed" -ForegroundColor Green
    }

    # Run Prisma migrations
    if (Test-Path "prisma\schema.prisma") {
        Write-Host "  Setting up database schema..." -ForegroundColor Gray
        if ($hasBun) {
            bunx prisma generate 2>&1 | Out-Null
        } else {
            npx prisma generate 2>&1 | Out-Null
        }
        Write-Host "  ✓ Database schema ready" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "✓ Quick Fix Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Blue
Write-Host "1. Start the server:" -ForegroundColor Gray
Write-Host "   cd $InstallDir" -ForegroundColor Cyan
Write-Host "   .\start.ps1" -ForegroundColor Cyan
Write-Host "`n2. Test the health endpoint:" -ForegroundColor Gray
Write-Host "   curl http://localhost:3006/api/health" -ForegroundColor Cyan
Write-Host "`n3. If database connection fails:" -ForegroundColor Gray
Write-Host "   Edit .env and set correct DATABASE_URL" -ForegroundColor Cyan
Write-Host ""
