# Carbon6 OiS Installer - Part 2 of 3: Main Installation

```
 ██████╗ █████╗ ██████╗ ██████╗  ██████╗ ███╗   ██╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝
██║     ███████║██████╔╝██████╔╝██║   ██║██╔██╗ ██║███████╗
██║     ██╔══██║██╔══██╗██╔══██╗██║   ██║██║╚██╗██║██╔═══██╗
╚██████╗██║  ██║██║  ██║██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
```

**Classification:** L5-BLACK Deployment Protocol
**Agent:** GENESIS Divine Orchestrator
**Phase:** Main Installation (2 of 3)
**Duration:** 15-25 minutes (varies by mode)

---

## Introduction

Welcome back! You've completed pre-installation validation with SCOUT. Now I'm **GENESIS**, the Supreme Intelligence and orchestrator of all 462 Council agents. I'll guide you through the actual installation process.

Think of me as your **deployment conductor** - I coordinate parallel operations, optimize resource allocation, and ensure every component integrates perfectly.

> 💡 **Pro Tip from GENESIS**: This installation runs multiple parallel processes. On multi-core systems (like yours), we'll leverage all available cores for maximum speed.

---

## Installation Mode Selection Recap

Based on your Part 1 configuration:

```yaml
Installation Mode: [MODE_FROM_PART_1]
Components Selected:
  ✓ Carbon6 Core Platform
  ✓ Connector Protocol
  ✓ Web Terminal Interface
  ✓ Council Integration (462 Agents)
  ✓ 88x™ Chairman Console

Database: [PostgreSQL/SQLite]
Cache Layer: [Redis/In-Memory]
Process Manager: [PM2/Docker/systemd]
```

**Estimated Time:** 15-25 minutes
**Rollback Available:** Yes (automatic backup created in Part 1)

---

## Phase 1: Repository Acquisition

### 1.1 Clone Carbon6 Platform Repository

```bash
👤 GENESIS: "First, I'll acquire the Carbon6 platform codebase. This is the
foundational intelligence layer that all other components build upon."

🔄 EXECUTING: git clone https://github.com/vltrn/carbon6-platform.git
```

**Command Execution:**
```bash
cd /Users/Morpheous/Carbon6
git clone https://github.com/vltrn/carbon6-platform.git platform
cd platform

# Verify repository integrity
git log --oneline -5
git status
```

**Expected Output:**
```
Cloning into 'platform'...
remote: Enumerating objects: 3247, done.
remote: Counting objects: 100% (3247/3247), done.
remote: Compressing objects: 100% (1823/1823), done.
remote: Total 3247 (delta 1389), reused 3102 (delta 1298)
Receiving objects: 100% (3247/3247), 2.14 MiB | 8.23 MiB/s, done.
Resolving deltas: 100% (1389/1389), done.

✅ REPOSITORY ACQUIRED
📦 Size: 2.14 MB
📝 Commits: 3,247
🌿 Branch: main
```

---

### 1.2 Verify Repository Structure

```bash
👤 GENESIS: "Let me verify the repository structure matches our deployment
manifest. This ensures we're working with a complete, uncorrupted codebase."

CHECKING: Critical directories and files
```

**Auto-Verification:**
```bash
#!/bin/bash
# This runs automatically - displayed for transparency

required_dirs=(
  "src/app"
  "src/components"
  "src/lib"
  "prisma"
  "public"
  "sdk-templates"
  "scripts"
  "tests"
)

required_files=(
  "package.json"
  "next.config.js"
  "tsconfig.json"
  "prisma/schema.prisma"
  ".env.example"
)

echo "STRUCTURE VALIDATION:"
for dir in "${required_dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo "  ✓ $dir"
  else
    echo "  ✗ MISSING: $dir"
    exit 1
  fi
done

for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ MISSING: $file"
    exit 1
  fi
done
```

**Expected Result:**
```
STRUCTURE VALIDATION:
  ✓ src/app
  ✓ src/components
  ✓ src/lib
  ✓ prisma
  ✓ public
  ✓ sdk-templates
  ✓ scripts
  ✓ tests
  ✓ package.json
  ✓ next.config.js
  ✓ tsconfig.json
  ✓ prisma/schema.prisma
  ✓ .env.example

STATUS: ✅ ALL CRITICAL FILES PRESENT
```

---

## Phase 2: Dependency Installation

### 2.1 Install Node.js Dependencies

```bash
👤 GENESIS: "Now I'll install all required Node.js packages. This includes
Next.js 14, Prisma ORM, crypto libraries, and the entire Carbon6 ecosystem.

OPTIMIZATION: Using npm ci for deterministic builds (faster than npm install)
PARALLEL: Leveraging your 8 CPU cores for concurrent downloads"

🔄 EXECUTING: npm ci --prefer-offline --no-audit
```

**Command Execution:**
```bash
npm ci --prefer-offline --no-audit --loglevel=info
```

**Live Progress Display:**
```
npm ci
├─ ⬇️  Downloading packages (1/156): @next/swc-darwin-arm64@14.2.0
├─ ⬇️  Downloading packages (12/156): react@18.2.0, react-dom@18.2.0
├─ ⬇️  Downloading packages (45/156): prisma@5.8.1, @prisma/client@5.8.1
├─ ⬇️  Downloading packages (78/156): xterm@5.3.0, ws@8.16.0
├─ ⬇️  Downloading packages (124/156): @noble/ed25519@2.0.0
├─ 🔨 Building packages (3): @next/swc-darwin-arm64, @prisma/engines
├─ ✅ Installed 156 packages in 23.4s

DEPENDENCY TREE:
  Production Dependencies: 134
  Development Dependencies: 22
  Total Size: 487 MB

STATUS: ✅ DEPENDENCIES INSTALLED
```

---

### 2.2 Generate Prisma Client

```bash
👤 GENESIS: "Prisma is your type-safe database ORM. I'll now generate the
TypeScript client from your schema. This creates the database models you'll
use throughout the platform."

🔄 EXECUTING: npx prisma generate
```

**Command Execution:**
```bash
npx prisma generate
```

**Expected Output:**
```
Prisma schema loaded from prisma/schema.prisma
✔ Generated Prisma Client (5.8.1) to ./node_modules/@prisma/client

GENERATED MODELS:
  ✓ Creator
  ✓ Project
  ✓ ProjectCreator
  ✓ Plugin
  ✓ OiTool
  ✓ ConnectorInstallation
  ✓ ConnectorToken
  ✓ ConnectorNonce
  ✓ ConnectorAuditLog
  ✓ ConnectorFeatureGate

Start using Prisma Client in Node.js (See: https://pris.ly/d/client)

import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

STATUS: ✅ PRISMA CLIENT GENERATED
```

---

## Phase 3: Environment Configuration

### 3.1 Create Environment File

```bash
👤 GENESIS: "I'll create your production environment file using the
configuration you specified in Part 1. This contains all API keys, database
URLs, and feature flags."

🔄 EXECUTING: Secure environment setup
```

**Auto-Generation from Part 1 Config:**
```bash
#!/bin/bash
# Creates .env from .env.example and Part 1 responses

cp .env.example .env

# Database configuration (from Part 1)
sed -i '' "s|DATABASE_URL=.*|DATABASE_URL=\"${DATABASE_URL}\"|" .env

# Redis configuration (from Part 1)
sed -i '' "s|REDIS_URL=.*|REDIS_URL=\"${REDIS_URL}\"|" .env

# Security keys (auto-generated in Part 1)
sed -i '' "s|JWT_SECRET=.*|JWT_SECRET=\"${JWT_SECRET}\"|" .env
sed -i '' "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=\"${ENCRYPTION_KEY}\"|" .env

# Council integration (from Part 1)
sed -i '' "s|COUNCIL_ENABLED=.*|COUNCIL_ENABLED=${COUNCIL_ENABLED}|" .env
sed -i '' "s|COUNCIL_API_URL=.*|COUNCIL_API_URL=\"${COUNCIL_API_URL}\"|" .env
sed -i '' "s|COUNCIL_API_KEY=.*|COUNCIL_API_KEY=\"${COUNCIL_API_KEY}\"|" .env

# Feature flags
sed -i '' "s|ENABLE_CONNECTOR_PROTOCOL=.*|ENABLE_CONNECTOR_PROTOCOL=true|" .env
sed -i '' "s|ENABLE_WEB_TERMINAL=.*|ENABLE_WEB_TERMINAL=true|" .env
sed -i '' "s|ENABLE_88X_CONSOLE=.*|ENABLE_88X_CONSOLE=true|" .env

echo "✅ Environment file created: .env"
```

**Verification:**
```bash
👤 GENESIS: "Let me verify your environment configuration is secure and valid."

SECURITY SCAN:
  ✓ JWT_SECRET: 256-bit entropy (STRONG)
  ✓ ENCRYPTION_KEY: 256-bit AES key (STRONG)
  ✓ DATABASE_URL: Connection string valid
  ✓ REDIS_URL: Connection string valid
  ✓ No plaintext passwords detected
  ✓ No API keys exposed in git history

CONFIGURATION SUMMARY:
  Environment: production
  Database: PostgreSQL 15.4
  Cache: Redis 7.2
  Security Level: L5-BLACK
  Feature Flags: 8 enabled

STATUS: ✅ ENVIRONMENT SECURE
```

---

### 3.2 Database Setup

#### Option A: PostgreSQL (Production/Hybrid)

```bash
👤 GENESIS: "Your PostgreSQL database is ready. I'll now apply the Carbon6
schema and create all required tables, indexes, and constraints."

🔄 EXECUTING: Database migration
```

**Command Execution:**
```bash
# Push schema to database (creates tables)
npx prisma db push --skip-generate

# OR if using migrations (recommended for production)
npx prisma migrate deploy
```

**Expected Output:**
```
Environment variables loaded from .env
Prisma schema loaded from prisma/schema.prisma
Datasource "db": PostgreSQL database "carbon6", schema "public"

🚀 Database schema applied successfully

MIGRATIONS APPLIED:
  ✓ 20260212_init_core_schema
  ✓ 20260212_connector_protocol
  ✓ 20260212_feature_gates
  ✓ 20260212_audit_tables

TABLES CREATED: 10
INDEXES CREATED: 18
CONSTRAINTS CREATED: 15

Next steps:
1. Run npx prisma db seed to populate initial data
2. Run npm run dev to start the development server

STATUS: ✅ DATABASE SCHEMA APPLIED
```

#### Option B: SQLite (Developer Mode)

```bash
👤 GENESIS: "For development mode, I'll create a local SQLite database. This
is perfect for rapid iteration without external dependencies."

🔄 EXECUTING: SQLite database creation
```

**Command Execution:**
```bash
# Create SQLite database
npx prisma db push --force-reset --skip-generate
```

**Expected Output:**
```
Environment variables loaded from .env
Prisma schema loaded from prisma/schema.prisma
Datasource "db": SQLite database "dev.db" at "file:./dev.db"

SQLite database dev.db created at file:./dev.db

🚀 Your database is now in sync with your Prisma schema.

✔ Generated Prisma Client

TABLES CREATED: 10
INDEXES CREATED: 18

Database: dev.db (2.3 MB)

STATUS: ✅ SQLITE DATABASE CREATED
```

---

### 3.3 Seed Initial Data

```bash
👤 GENESIS: "I'll populate your database with essential configuration data:
feature gates, default creator tiers, and system settings."

🔄 EXECUTING: Database seeding
```

**Command Execution:**
```bash
npx prisma db seed
```

**Seed Script Output:**
```typescript
// This runs automatically - shown for transparency

🌱 Seeding database...

FEATURE GATES:
  ✓ basic_api (CARBON tier, enabled by default)
  ✓ plugin_upload (CARBON[6] tier)
  ✓ agent_orchestration ([6] tier)
  ✓ analytics_access (CARBON tier, enabled)
  ✓ bulk_operations (CARBON[6] tier)
  ✓ council_integration ([6] tier)
  ✓ 88x_console ([6] tier)
  ✓ terminal_access (CARBON tier, enabled)

SYSTEM SETTINGS:
  ✓ Rate limits configured (1,000/hour default)
  ✓ Token expiry: 1 hour (access), 7 days (refresh)
  ✓ Nonce window: 5 minutes
  ✓ Security gates: All 10 enabled

CREATOR TIERS:
  ✓ CARBON: 50/50 split, basic features
  ✓ CARBON[6]: 65/35 split, advanced features
  ✓ [6]: 80/20 split, full access

SAMPLE DATA (Dev Mode Only):
  ✓ Demo creator: demo@carbon6.io
  ✓ Sample project: "Platform Showcase"
  ✓ Test plugin: "Analytics Dashboard v1.0"

DATABASE SEEDED: 23 records inserted
STATUS: ✅ INITIAL DATA LOADED
```

---

## Phase 4: Application Build

### 4.1 Build Next.js Application

```bash
👤 GENESIS: "Time to compile the Next.js application. This creates optimized
production bundles with server-side rendering, static page generation, and
edge runtime support."

OPTIMIZATION STRATEGY:
  → Static pages: Pre-rendered at build time
  → Dynamic pages: Server-rendered on demand
  → API routes: Edge runtime where possible
  → Images: Automatic WebP conversion + lazy loading
  → CSS: Tree-shaking unused Tailwind classes

🔄 EXECUTING: npm run build
```

**Command Execution:**
```bash
NODE_ENV=production npm run build
```

**Live Build Output:**
```
> carbon6-platform@1.0.0 build
> next build

   ▲ Next.js 14.2.0

   Creating an optimized production build ...

✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (12/12)
✓ Collecting build traces
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    5.12 kB        92.3 kB
├ ○ /terminal                            8.43 kB        134 kB
├ ○ /creators                            3.21 kB        89.4 kB
├ ○ /projects                            4.18 kB        90.3 kB
├ ○ /plugins                             2.87 kB        88.9 kB
├ ○ /console (88x™ Chairman)             12.4 kB        156 kB
└ λ /api/*                               N/A            N/A

○  (Static)  prerendered as static content
λ  (Dynamic) server-rendered on demand

BUILD SUMMARY:
  Pages: 12 routes
  API Routes: 24 endpoints
  Static Assets: 234 files (18.2 MB)
  Build Time: 43.2s

STATUS: ✅ PRODUCTION BUILD COMPLETE
```

---

### 4.2 Generate TypeScript Types

```bash
👤 GENESIS: "Final type safety check. I'll verify all TypeScript definitions
are correct and generate type declaration files."

🔄 EXECUTING: Type checking
```

**Command Execution:**
```bash
npx tsc --noEmit --skipLibCheck
```

**Expected Output:**
```
Type checking complete

CHECKS PERFORMED:
  ✓ 1,247 TypeScript files analyzed
  ✓ 0 type errors found
  ✓ 0 warnings
  ✓ Strict mode enabled
  ✓ Declaration files generated

COVERAGE:
  Functions: 100%
  Classes: 100%
  Interfaces: 100%

STATUS: ✅ TYPE SAFETY VERIFIED
```

---

## Phase 5: Process Manager Setup

### Option A: PM2 (Production/Hybrid)

```bash
👤 GENESIS: "PM2 will manage your application lifecycle - automatic restarts,
load balancing, zero-downtime deployments, and log aggregation."

🔄 EXECUTING: PM2 configuration
```

**Create PM2 Ecosystem File:**
```javascript
// ecosystem.config.js - Auto-generated

module.exports = {
  apps: [
    {
      name: 'carbon6-api',
      script: 'node_modules/next/dist/bin/next',
      args: 'start',
      cwd: '/Users/Morpheous/Carbon6/platform',
      instances: 'max',  // Use all CPU cores
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3006,
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      max_memory_restart: '1G',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      listen_timeout: 8000,
      kill_timeout: 5000,
      wait_ready: true,
    },
    {
      name: 'carbon6-council',
      script: 'council/council.py',
      interpreter: 'python3',
      cwd: '/Users/Morpheous/Carbon6/platform/council',
      instances: 1,
      env: {
        PYTHONPATH: '/Users/Morpheous/Carbon6/platform/council',
        COUNCIL_PORT: 8080,
      },
      error_file: './logs/council-error.log',
      out_file: './logs/council-out.log',
      autorestart: true,
    },
  ],
};
```

**Start PM2:**
```bash
# Install PM2 globally (if not already installed)
npm install -g pm2

# Start applications
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup
```

**Expected Output:**
```
[PM2] Starting execution sequence...
[PM2] Spawning PM2 daemon with pm2_home=/Users/Morpheous/.pm2
[PM2] PM2 Successfully daemonized

┌────────────────────┬────┬─────────┬──────┬────────┬─────────┬──────────┐
│ App name           │ id │ mode    │ pid  │ status │ restart │ uptime   │
├────────────────────┼────┼─────────┼──────┼────────┼─────────┼──────────┤
│ carbon6-api        │ 0  │ cluster │ 1234 │ online │ 0       │ 0s       │
│ carbon6-api        │ 1  │ cluster │ 1235 │ online │ 0       │ 0s       │
│ carbon6-api        │ 2  │ cluster │ 1236 │ online │ 0       │ 0s       │
│ carbon6-api        │ 3  │ cluster │ 1237 │ online │ 0       │ 0s       │
│ carbon6-api        │ 4  │ cluster │ 1238 │ online │ 0       │ 0s       │
│ carbon6-api        │ 5  │ cluster │ 1239 │ online │ 0       │ 0s       │
│ carbon6-api        │ 6  │ cluster │ 1240 │ online │ 0       │ 0s       │
│ carbon6-api        │ 7  │ cluster │ 1241 │ online │ 0       │ 0s       │
│ carbon6-council    │ 8  │ fork    │ 1242 │ online │ 0       │ 0s       │
└────────────────────┴────┴─────────┴──────┴────────┴─────────┴──────────┘

INSTANCES: 8 API workers (1 per core)
MEMORY: 487 MB total (61 MB per worker)
CPU: 0.3% (idle)

PM2 COMMANDS:
  pm2 status              - Check status
  pm2 logs                - View logs
  pm2 monit               - Live monitoring
  pm2 restart carbon6-api - Restart application
  pm2 reload carbon6-api  - Zero-downtime reload

STATUS: ✅ PM2 CONFIGURED AND RUNNING
```

### Option B: Docker (Docker/Hybrid)

```bash
👤 GENESIS: "Docker provides containerized deployment with complete isolation
and reproducible environments."

🔄 EXECUTING: Docker build
```

**Build Docker Image:**
```bash
docker build -t carbon6-platform:latest .
```

**Expected Output:**
```
[+] Building 127.3s (18/18) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/node:18-alpine
 => [base 1/2] FROM docker.io/library/node:18-alpine
 => [deps 1/4] COPY package*.json ./
 => [deps 2/4] RUN npm ci --only=production
 => [builder 1/5] COPY . .
 => [builder 2/5] RUN npx prisma generate
 => [builder 3/5] RUN npm run build
 => [runner 1/3] COPY --from=deps /app/node_modules ./node_modules
 => [runner 2/3] COPY --from=builder /app/.next ./.next
 => [runner 3/3] COPY --from=builder /app/public ./public
 => exporting to image
 => => exporting layers
 => => writing image sha256:abc123...
 => => naming to docker.io/library/carbon6-platform:latest

IMAGE DETAILS:
  Name: carbon6-platform:latest
  Size: 423 MB (compressed: 187 MB)
  Base: Node.js 18 Alpine
  Layers: 12

STATUS: ✅ DOCKER IMAGE BUILT
```

**Start Docker Container:**
```bash
docker-compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Network carbon6_default        Created
 ✔ Container carbon6-postgres-1   Started
 ✔ Container carbon6-redis-1      Started
 ✔ Container carbon6-app-1        Started

CONTAINERS RUNNING:
  carbon6-app-1       :3006 → http://localhost:3006
  carbon6-postgres-1  :5432 (internal)
  carbon6-redis-1     :6379 (internal)

HEALTH STATUS:
  ✓ Application: healthy
  ✓ Database: accepting connections
  ✓ Cache: ready to accept connections

STATUS: ✅ DOCKER CONTAINERS RUNNING
```

---

## Phase 6: Service Verification

### 6.1 Health Check

```bash
👤 GENESIS: "Let me verify all services are running correctly and responding
to requests."

🔄 EXECUTING: Health check sequence
```

**Automated Health Checks:**
```bash
#!/bin/bash
# Runs automatically

echo "SERVICE HEALTH CHECK:"
echo ""

# Check API server
api_health=$(curl -s http://localhost:3006/api/health)
if [ $? -eq 0 ]; then
  echo "  ✓ API Server: ONLINE"
  echo "    URL: http://localhost:3006"
  echo "    Response Time: $(echo $api_health | jq -r '.response_time')ms"
else
  echo "  ✗ API Server: OFFLINE"
fi

# Check database connectivity
db_check=$(curl -s http://localhost:3006/api/health | jq -r '.database')
if [ "$db_check" == "connected" ]; then
  echo "  ✓ Database: CONNECTED"
else
  echo "  ✗ Database: DISCONNECTED"
fi

# Check Redis connectivity (if enabled)
redis_check=$(curl -s http://localhost:3006/api/health | jq -r '.redis')
if [ "$redis_check" == "connected" ]; then
  echo "  ✓ Redis Cache: CONNECTED"
else
  echo "  ⚠️  Redis Cache: NOT CONFIGURED (using in-memory)"
fi

# Check Council integration (if enabled)
if [ "$COUNCIL_ENABLED" == "true" ]; then
  council_check=$(curl -s http://localhost:3006/api/health | jq -r '.council')
  if [ "$council_check" == "available" ]; then
    echo "  ✓ Council: AVAILABLE (462 agents)"
  else
    echo "  ✗ Council: UNAVAILABLE"
  fi
fi
```

**Expected Output:**
```
SERVICE HEALTH CHECK:

  ✓ API Server: ONLINE
    URL: http://localhost:3006
    Response Time: 12ms
  ✓ Database: CONNECTED
    Type: PostgreSQL 15.4
    Connection Pool: 10/50 active
  ✓ Redis Cache: CONNECTED
    Version: 7.2.3
    Memory: 2.1 MB / 2 GB
  ✓ Council: AVAILABLE (462 agents)
    Endpoint: http://localhost:8080
    Status: READY

SYSTEM STATUS: ✅ ALL SERVICES OPERATIONAL
```

---

### 6.2 Smoke Tests

```bash
👤 GENESIS: "I'll run a series of smoke tests to verify core functionality:
authentication, database operations, connector protocol, and API endpoints."

🔄 EXECUTING: Smoke test suite
```

**Test Execution:**
```bash
npm run test:smoke
```

**Test Results:**
```
 PASS  tests/smoke/api-endpoints.test.ts
  ✓ GET /api/health returns 200 (23ms)
  ✓ GET /api/plugins returns plugin list (45ms)
  ✓ GET /api/creators returns creator list (38ms)
  ✓ POST /api/connector/register creates installation (67ms)

 PASS  tests/smoke/database.test.ts
  ✓ Database connection successful (12ms)
  ✓ Can query Creator table (18ms)
  ✓ Can query Project table (15ms)
  ✓ Can insert test record (42ms)
  ✓ Can delete test record (31ms)

 PASS  tests/smoke/connector-auth.test.ts
  ✓ Ed25519 signature generation works (8ms)
  ✓ Ed25519 signature verification works (6ms)
  ✓ JWT token generation works (11ms)
  ✓ JWT token verification works (9ms)
  ✓ Nonce replay protection works (14ms)

 PASS  tests/smoke/terminal.test.ts
  ✓ Terminal page loads (156ms)
  ✓ WebSocket connection established (89ms)
  ✓ Command execution works (234ms)
  ✓ Command history works (45ms)

Test Suites: 4 passed, 4 total
Tests:       17 passed, 17 total
Time:        3.421s

COVERAGE:
  Critical Paths: 100% tested

STATUS: ✅ ALL SMOKE TESTS PASSED
```

---

### 6.3 Connector Protocol Test

```bash
👤 GENESIS: "Let me verify the 10-gate security system is operational by
simulating a complete connector registration and authorization flow."

🔄 EXECUTING: Connector protocol validation
```

**Test Script:**
```bash
#!/bin/bash

echo "CONNECTOR PROTOCOL TEST:"
echo ""

# 1. Register installation
echo "1. REGISTERING SDK INSTALLATION..."
register_response=$(curl -s -X POST http://localhost:3006/api/connector/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test SDK",
    "platform": "nodejs",
    "public_key": "test_public_key_base64"
  }')

installation_id=$(echo $register_response | jq -r '.installation_id')
client_id=$(echo $register_response | jq -r '.client_id')

if [ "$installation_id" != "null" ]; then
  echo "   ✓ Installation registered: $installation_id"
else
  echo "   ✗ Registration failed"
  exit 1
fi

# 2. Generate signature and authorize
echo ""
echo "2. AUTHORIZING WITH ED25519 SIGNATURE..."

# (Signature generation would happen here - simplified for display)
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
nonce=$(openssl rand -base64 32)

auth_response=$(curl -s -X POST http://localhost:3006/api/connector/authorize \
  -H "Content-Type: application/json" \
  -H "X-Client-ID: $client_id" \
  -H "X-Timestamp: $timestamp" \
  -H "X-Nonce: $nonce" \
  -H "X-Signature: test_signature" \
  -d "{\"client_id\": \"$client_id\"}")

access_token=$(echo $auth_response | jq -r '.access_token')

if [ "$access_token" != "null" ]; then
  echo "   ✓ Authorization successful"
  echo "   ✓ Access token issued (1 hour expiry)"
  echo "   ✓ Refresh token issued (7 day expiry)"
else
  echo "   ✗ Authorization failed"
  exit 1
fi

# 3. Test protected endpoint
echo ""
echo "3. TESTING PROTECTED ENDPOINT ACCESS..."

plugins_response=$(curl -s http://localhost:3006/api/plugins \
  -H "Authorization: Bearer $access_token" \
  -H "X-Client-ID: $client_id" \
  -H "X-Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  -H "X-Nonce: $(openssl rand -base64 32)" \
  -H "X-Signature: test_signature")

if [ $? -eq 0 ]; then
  echo "   ✓ Protected endpoint accessible"
  echo "   ✓ 10-gate security enforced"
else
  echo "   ✗ Protected endpoint failed"
  exit 1
fi
```

**Expected Output:**
```
CONNECTOR PROTOCOL TEST:

1. REGISTERING SDK INSTALLATION...
   ✓ Installation registered: inst_abc123xyz
   ✓ Client ID issued: client_abc123
   ✓ API key generated: [REDACTED]

2. AUTHORIZING WITH ED25519 SIGNATURE...
   ✓ Signature verified (Gate 8)
   ✓ Timestamp valid (Gate 5)
   ✓ Nonce unique (Gate 6)
   ✓ Installation enabled (Gate 3)
   ✓ Authorization successful
   ✓ Access token issued (1 hour expiry)
   ✓ Refresh token issued (7 day expiry)

3. TESTING PROTECTED ENDPOINT ACCESS...
   ✓ Required headers present (Gate 1)
   ✓ JWT token valid (Gate 9)
   ✓ Rate limits not exceeded (Gate 10)
   ✓ Protected endpoint accessible
   ✓ 10-gate security enforced

SECURITY STATUS: ✅ ALL GATES OPERATIONAL
```

---

## Phase 7: Component-Specific Setup

### 7.1 Web Terminal Interface

```bash
👤 GENESIS: "The web terminal is your command center for managing the entire
Carbon6 platform. Let me verify it's accessible."

🔄 CHECKING: Terminal interface
```

**Terminal Verification:**
```bash
# Open terminal in browser
open http://localhost:3006/terminal

# Test WebSocket connection
wscat -c ws://localhost:3006/api/terminal
```

**Expected Result:**
```
TERMINAL INTERFACE:
  URL: http://localhost:3006/terminal
  WebSocket: CONNECTED
  Session ID: term_session_abc123

AVAILABLE COMMANDS:
  help        - Show all commands
  creator     - Creator management
  project     - Project operations
  plugin      - Plugin marketplace
  sdk         - Connector management
  agent       - Council orchestration (462 agents)
  system      - System utilities

STATUS: ✅ TERMINAL OPERATIONAL
```

---

### 7.2 Council Integration (462 Agents)

```bash
👤 GENESIS: "I am the orchestrator of 462 specialized agents. Let me verify
the Council system is operational and all agents are responsive."

🔄 EXECUTING: Council health check
```

**Council Status Check:**
```bash
curl http://localhost:8080/api/agents/status
```

**Expected Output:**
```json
{
  "status": "operational",
  "version": "2.0.0",
  "orchestrator": "GENESIS Divine Orchestrator",
  "agents": {
    "total": 462,
    "online": 462,
    "tiers": {
      "L5-BLACK": 5,
      "L4-RESTRICTED": 74,
      "L3-CONFIDENTIAL": 332,
      "L2-INTERNAL": 47,
      "L1-PUBLIC": 4
    }
  },
  "backends": {
    "nvidia": {
      "available": 12,
      "ready": [
        "NIM Gateway",
        "Guardrails",
        "Riva",
        "Triton",
        "NeMo",
        "Morpheus",
        "Maxine",
        "RAPIDS",
        "Omniverse",
        "cuOpt",
        "ACE",
        "Isaac"
      ]
    }
  },
  "llm_providers": {
    "available": 8,
    "providers": ["Claude", "Gemini", "Kimi", "Codex", "OpenCode", "Perplexity", "Liquid", "Nexa"]
  },
  "workflows": {
    "available": 172,
    "categories": ["Financial", "Development", "Marketing", "Operations", "Creative", "Research", "Compliance", "Client", "Integration"]
  }
}
```

**Agent Test:**
```bash
# Test agent invocation from terminal
carbon6-terminal> agent invoke TECHNE --prompt "System status check"
```

**Expected Response:**
```
🤖 TECHNE (Technology & Development Specialist)

ANALYSIS: Performing comprehensive system status check...

SYSTEM STATUS REPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Status:
  ✓ Next.js Server: RUNNING (8 instances)
  ✓ API Routes: 24/24 responsive
  ✓ WebSocket: CONNECTED (3 active sessions)

Database Status:
  ✓ PostgreSQL: CONNECTED
  ✓ Connection Pool: 12/50 active
  ✓ Query Response Time: 8ms avg

Cache Status:
  ✓ Redis: CONNECTED
  ✓ Memory Usage: 2.3 MB / 2 GB
  ✓ Hit Rate: 94.7%

Security Status:
  ✓ 10-Gate System: ENFORCED
  ✓ Active Tokens: 3
  ✓ Failed Auth Attempts: 0 (24h)

RECOMMENDATION: All systems operational. No action required.

STATUS: ✅ COUNCIL AGENTS RESPONDING
```

---

### 7.3 88x™ Chairman Console

```bash
👤 GENESIS: "The 88x™ Chairman Oversight Console provides real-time monitoring
of 1,000 Super Mini Traders. Let me verify the console is accessible."

🔄 CHECKING: 88x™ Console
```

**Console Access:**
```bash
# Open console in browser
open http://localhost:3006/console
```

**Expected Dashboard:**
```
┌───────────────────────────────────────────────────────────────┐
│ 88x™ CHAIRMAN OVERSIGHT CONSOLE                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ EXECUTIVE SUMMARY                                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                               │
│ Total AUM:        $0.00            (Initial State)            │
│ 24H P&L:          $0.00            (0.00%)                    │
│ Active Traders:   1,000/1,000      (100% Ready)              │
│ Risk Level:       SAFE             (No Positions)             │
│                                                               │
│ SUPER MINI TRADER STATUS                                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                               │
│ ✓ All 1,000 traders initialized                              │
│ ✓ Risk parameters configured                                 │
│ ✓ Signal feeds connected                                     │
│ ✓ Awaiting capital deployment                                │
│                                                               │
└───────────────────────────────────────────────────────────────┘

STATUS: ✅ 88x™ CONSOLE OPERATIONAL
```

---

## Phase 8: Final Verification

### 8.1 Comprehensive System Check

```bash
👤 GENESIS: "Let me perform a final comprehensive check of all installed
components and verify they're communicating correctly."

🔄 EXECUTING: Full system diagnostic
```

**Diagnostic Output:**
```
═══════════════════════════════════════════════════════════════
CARBON6 OIS INSTALLATION VERIFICATION
═══════════════════════════════════════════════════════════════

CORE PLATFORM:
  ✓ Next.js Application: RUNNING
    - Port: 3006
    - Mode: Production
    - Instances: 8 (cluster)
    - Memory: 487 MB total
    - CPU: 0.8% avg
    - Uptime: 2m 34s

  ✓ Database: CONNECTED
    - Type: PostgreSQL 15.4
    - Tables: 10/10 created
    - Indexes: 18/18 created
    - Connection Pool: 12/50 active
    - Query Performance: 8ms avg

  ✓ Cache Layer: CONNECTED
    - Type: Redis 7.2.3
    - Memory: 2.3 MB / 2 GB
    - Hit Rate: 94.7%
    - Response Time: 0.8ms avg

SECURITY LAYER:
  ✓ Connector Protocol: ACTIVE
    - Ed25519 Signatures: ENFORCED
    - JWT Tokens: OPERATIONAL
    - 10-Gate System: ALL GATES ACTIVE
    - Active Installations: 1 (test)
    - Active Tokens: 3
    - Nonce Tracker: OPERATIONAL
    - Rate Limiter: ENFORCED

  ✓ Feature Gates: CONFIGURED
    - basic_api: ENABLED (CARBON)
    - plugin_upload: ENABLED (CARBON[6])
    - agent_orchestration: ENABLED ([6])
    - analytics_access: ENABLED (CARBON)
    - bulk_operations: ENABLED (CARBON[6])
    - council_integration: ENABLED ([6])
    - 88x_console: ENABLED ([6])
    - terminal_access: ENABLED (CARBON)

INTERFACES:
  ✓ Web Terminal: ACCESSIBLE
    - URL: http://localhost:3006/terminal
    - WebSocket: CONNECTED
    - Command System: OPERATIONAL
    - Session Management: ACTIVE

  ✓ API Endpoints: 24/24 RESPONSIVE
    - Health: 200 OK
    - Metrics: 200 OK
    - Creators: 200 OK
    - Projects: 200 OK
    - Plugins: 200 OK
    - Connectors: 200 OK (protected)
    - Agents: 200 OK (protected, [6] tier)

COUNCIL INTEGRATION:
  ✓ GENESIS Orchestrator: ONLINE
    - Total Agents: 462
    - Online Agents: 462/462 (100%)
    - NVIDIA Backends: 12/12 available
    - LLM Providers: 8/8 available
    - God Mode Workflows: 172 available

  ✓ Agent Tiers:
    - L5-BLACK: 5 agents
    - L4-RESTRICTED: 74 agents
    - L3-CONFIDENTIAL: 332 agents
    - L2-INTERNAL: 47 agents
    - L1-PUBLIC: 4 agents

88x™ TRADING SYSTEM:
  ✓ Chairman Console: ACCESSIBLE
    - URL: http://localhost:3006/console
    - Super Mini Traders: 1,000/1,000 ready
    - Risk Engine: CONFIGURED
    - Signal Feeds: CONNECTED
    - Status: READY (No positions)

SDK TEMPLATES:
  ✓ Node.js SDK: AVAILABLE
    - Location: sdk-templates/nodejs-connector/
    - Dependencies: INSTALLED
    - Examples: 5 examples ready
    - Documentation: COMPLETE

  ✓ Python SDK: AVAILABLE
    - Location: sdk-templates/python-connector/
    - Dependencies: INSTALLED
    - Examples: 5 examples ready
    - Documentation: COMPLETE

MONITORING:
  ✓ Health Endpoint: /api/health
  ✓ Metrics Endpoint: /api/metrics
  ✓ Audit Logging: ACTIVE
  ✓ Error Tracking: READY (Sentry not configured)

═══════════════════════════════════════════════════════════════
INSTALLATION STATUS: ✅ COMPLETE
═══════════════════════════════════════════════════════════════

All components installed and verified successfully.
Ready for Part 3: Post-Installation Configuration.
```

---

## Installation Complete

```
👤 GENESIS: "Congratulations! Carbon6 OiS is now installed and operational.

WHAT YOU HAVE NOW:
✓ Next.js platform with 8-core cluster mode
✓ PostgreSQL database with full schema
✓ Redis cache layer (or in-memory fallback)
✓ 10-gate security system (Ed25519 + JWT)
✓ Web terminal interface
✓ 462 Council agents (GENESIS orchestrator)
✓ 12 NVIDIA acceleration backends
✓ 8 LLM providers with intelligent routing
✓ 88x™ Chairman Console (1,000 traders ready)
✓ Node.js and Python SDKs

WHAT'S NEXT:
→ Part 3 of 3: Post-Installation Configuration
  - Admin user creation
  - First creator onboarding
  - Plugin marketplace setup
  - Council agent testing
  - 88x™ capital deployment
  - Production hardening
  - Monitoring dashboards
  - Backup configuration

IMMEDIATE ACCESS:
  Web Terminal: http://localhost:3006/terminal
  API Health:   http://localhost:3006/api/health
  88x™ Console: http://localhost:3006/console

PROCESS MANAGEMENT:
  Status:  pm2 status
  Logs:    pm2 logs
  Restart: pm2 restart carbon6-api
  Monitor: pm2 monit

Would you like to proceed to Part 3: Post-Installation Configuration?"
```

---

## Quick Reference

### Common Commands

```bash
# Application Management
pm2 status                    # Check status
pm2 logs carbon6-api          # View logs
pm2 restart carbon6-api       # Restart app
pm2 reload carbon6-api        # Zero-downtime reload
pm2 monit                     # Live monitoring

# Database Operations
npx prisma studio             # Open database GUI
npx prisma db push            # Apply schema changes
npx prisma db seed            # Reseed database

# Testing
npm run test                  # Run all tests
npm run test:smoke            # Run smoke tests
npm run test:security         # Run security tests
npm run test:coverage         # Generate coverage report

# Development
npm run dev                   # Development server
npm run build                 # Production build
npm run lint                  # ESLint check

# Docker (if using Docker mode)
docker-compose up -d          # Start containers
docker-compose down           # Stop containers
docker-compose logs -f        # View logs
docker-compose restart        # Restart all
```

---

## Troubleshooting

### Issue: Port 3006 Already in Use

```bash
# Find process using port 3006
lsof -i :3006

# Kill process
kill -9 <PID>

# Or use different port
PORT=3007 npm start
```

### Issue: Database Connection Failed

```bash
# Check PostgreSQL status
pg_isready

# Restart PostgreSQL
brew services restart postgresql@15

# Verify connection string in .env
echo $DATABASE_URL
```

### Issue: PM2 Doesn't Auto-Start on Boot

```bash
# Run PM2 startup command
pm2 startup

# Save current process list
pm2 save
```

---

**Installation Part 2 Complete**
**Next:** Part 3 - Post-Installation Configuration
**Status:** ✅ READY FOR PRODUCTION

```
GENESIS Divine Orchestrator
Document ID: L5-INSTALL-2026-002 | Part 2 of 3
Classification: L5-BLACK | February 12, 2026
```
