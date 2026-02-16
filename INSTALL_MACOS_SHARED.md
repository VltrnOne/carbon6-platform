# Carbon6 Platform - macOS Shared Installation

## Overview

This installation method creates a **centralized, multi-user** setup accessible from any computer on your network.

### Key Differences: Personal vs Shared

| Feature | Personal Install | Shared Install |
|---------|------------------|----------------|
| **Location** | `~/Carbon6` | `/opt/carbon6` |
| **Access** | Single user only | All users on Mac |
| **Config** | User-specific | Shared in `/var/lib/carbon6` |
| **Network** | localhost only | Network-accessible |
| **Command** | `cd ~/Carbon6 && npm run dev` | `carbon6` (system-wide) |
| **Use Case** | Development | Production, Teams |

---

## Installation

### Requirements

- ✅ **sudo access** (required for system-wide installation)
- ✅ macOS 12+ (Monterey or newer)
- ✅ Terminal access

### Quick Install

```bash
# Download installer
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-macos-shared.sh -o /tmp/install-shared.sh

# Run with sudo
sudo bash /tmp/install-shared.sh
```

### Custom Installation Path

```bash
sudo bash install-carbon6-macos-shared.sh --path /custom/path --data /custom/data
```

---

## Installation Locations

### Default Paths

```
/opt/carbon6/                  # Application files (all users can read)
├── server.js                  # Main server
├── package.json               # Dependencies
├── prisma/                    # Database schema
├── node_modules/              # Packages
├── .env → /var/lib/carbon6/config/.env  # Symlink to shared config
└── start.sh                   # Startup script

/var/lib/carbon6/              # Shared data (all staff can modify)
├── config/
│   └── .env                   # Shared configuration
├── logs/                      # Application logs
└── database/                  # Database files

/usr/local/bin/
└── carbon6 → /opt/carbon6/start.sh     # System-wide command
```

### Permissions

| Location | Users | Staff Group |
|----------|-------|-------------|
| `/opt/carbon6/` | Read & Execute | Read & Execute |
| `/var/lib/carbon6/` | Read | Modify |
| `/var/log/carbon6/` | Read | Write |

**Note:** macOS "staff" group includes all standard users

---

## Usage

### Start Server (Any User)

```bash
# Method 1: Use global command
carbon6

# Method 2: Direct execution
sudo /opt/carbon6/start.sh

# Method 3: Using Node directly
cd /opt/carbon6 && node server.js
```

### Access Points

```bash
# From this Mac
http://localhost:3006

# From other devices on network
http://YOUR-MAC-NAME.local:3006
http://192.168.1.XXX:3006
```

### Find Your Network Address

```bash
# Get hostname
hostname

# Get IP address
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet
```

---

## Network Access Configuration

### Enable Network Access in macOS Firewall

**System Settings → Network → Firewall:**

1. Click "Options..."
2. Add `/opt/carbon6/start.sh`
3. Select "Allow incoming connections"

**Or via command line:**

```bash
# Allow incoming connections for Node.js
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/node
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/node
```

### Configure Router (if needed)

For access from outside your local network:

1. Forward port 3006 to your Mac's IP
2. Use dynamic DNS for hostname
3. Consider VPN for security

---

## Service Management (launchd)

### Create System Service (Auto-Start)

**Create launch daemon (runs at boot, all users):**

```bash
sudo tee /Library/LaunchDaemons/com.vltrn.carbon6.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vltrn.carbon6</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/opt/carbon6/server.js</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/opt/carbon6</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/var/log/carbon6/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/var/log/carbon6/stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>DATA_PATH</key>
        <string>/var/lib/carbon6</string>
        <key>LOG_PATH</key>
        <string>/var/log/carbon6</string>
    </dict>
</dict>
</plist>
EOF

# Set permissions
sudo chown root:wheel /Library/LaunchDaemons/com.vltrn.carbon6.plist
sudo chmod 644 /Library/LaunchDaemons/com.vltrn.carbon6.plist
```

### Service Commands

```bash
# Load and start service
sudo launchctl load /Library/LaunchDaemons/com.vltrn.carbon6.plist

# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.vltrn.carbon6.plist

# Restart service
sudo launchctl unload /Library/LaunchDaemons/com.vltrn.carbon6.plist
sudo launchctl load /Library/LaunchDaemons/com.vltrn.carbon6.plist

# Check status
sudo launchctl list | grep carbon6
```

---

## Configuration

### Shared Environment (.env)

Edit `/var/lib/carbon6/config/.env`:

```bash
# Open with any editor
sudo nano /var/lib/carbon6/config/.env

# Or
sudo vim /var/lib/carbon6/config/.env
```

**Configuration options:**

```env
# Database (network-accessible PostgreSQL)
DATABASE_URL="postgresql://username@db-server:5432/carbon6"
REDIS_URL="redis://cache-server:6379"

# Server (0.0.0.0 = accessible from network)
HOST=0.0.0.0
PORT=3006

# Security (CHANGE THESE!)
JWT_SECRET="your-production-secret-key"
ENCRYPTION_KEY="your-encryption-key"

# Paths (set by installer)
INSTALL_PATH="/opt/carbon6"
DATA_PATH="/var/lib/carbon6"
LOG_PATH="/var/log/carbon6"
```

### PostgreSQL Network Access

**Already configured by installer!**

The installer automatically configures PostgreSQL to accept network connections by modifying:

- `postgresql.conf` → `listen_addresses = '*'`
- `pg_hba.conf` → Allow network connections

**Manual verification:**

```bash
# Find PostgreSQL config
brew --prefix postgresql@15

# Check if listening on network
netstat -an | grep 5432
```

---

## Multi-Mac Network Deployment

### Scenario 1: Office Network

**Setup:**
```bash
# On main Mac (install Carbon6)
sudo bash install-carbon6-macos-shared.sh

# On other Macs (access via network)
# Just open browser to: http://main-mac.local:3006
```

**Access from:**
- Mac 2: `http://main-mac.local:3006`
- iPhone: `http://192.168.1.50:3006`
- Windows PC: `http://main-mac.local:3006`

### Scenario 2: Distributed Team

**Use Carbon6 as central server:**

```bash
# Mac 1: Run Carbon6 server
sudo /opt/carbon6/start.sh

# Mac 2-5: Access via DNS
http://carbon-server.company.local:3006
```

### Scenario 3: Development → Production

**Copy installation between Macs:**

```bash
# On source Mac (create archive)
sudo tar -czf carbon6-backup.tar.gz /opt/carbon6 /var/lib/carbon6

# Transfer to new Mac
scp carbon6-backup.tar.gz user@new-mac:/tmp/

# On new Mac (restore)
cd /
sudo tar -xzf /tmp/carbon6-backup.tar.gz
```

---

## Monitoring & Logs

### View Real-Time Logs

```bash
# Application logs
tail -f /var/log/carbon6/stdout.log

# Error logs
tail -f /var/log/carbon6/stderr.log

# System logs
log stream --predicate 'subsystem == "com.vltrn.carbon6"'
```

### Log Rotation

**Create log rotation config:**

```bash
sudo tee /etc/newsyslog.d/carbon6.conf << 'EOF'
# Carbon6 log rotation
/var/log/carbon6/*.log  644  7  *  @T00  GZ
EOF
```

---

## Security Considerations

### 1. File Permissions

**Verify permissions:**

```bash
# Check application
ls -la /opt/carbon6

# Check data directory
ls -la /var/lib/carbon6

# Check logs
ls -la /var/log/carbon6
```

### 2. Network Security

**Restrict to local network only:**

```env
# In .env, change HOST to:
HOST=192.168.1.100  # Your Mac's local IP
```

Or use firewall rules to allow only specific IPs.

### 3. Database Security

**Create dedicated database user:**

```bash
# Connect to PostgreSQL
psql postgres

# Create user
CREATE USER carbon6_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE carbon6 TO carbon6_user;

# Update .env
DATABASE_URL="postgresql://carbon6_user:secure_password@localhost:5432/carbon6"
```

### 4. HTTPS/SSL

**Use nginx as reverse proxy:**

```bash
# Install nginx
brew install nginx

# Configure SSL (certificates from Let's Encrypt)
# Proxy: https://carbon6.local → http://localhost:3006
```

---

## Backup & Recovery

### Backup Everything

```bash
#!/bin/bash
# backup-carbon6.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Volumes/Backup/carbon6_$DATE"

mkdir -p "$BACKUP_DIR"

# Backup application
sudo tar -czf "$BACKUP_DIR/app.tar.gz" /opt/carbon6

# Backup data
sudo tar -czf "$BACKUP_DIR/data.tar.gz" /var/lib/carbon6

# Backup database
pg_dump carbon6 > "$BACKUP_DIR/database.sql"

echo "Backup complete: $BACKUP_DIR"
```

### Automated Backups (cron)

```bash
# Edit root crontab
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-carbon6.sh
```

### Restore from Backup

```bash
# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.vltrn.carbon6.plist

# Restore application
cd /
sudo tar -xzf /path/to/backup/app.tar.gz

# Restore data
sudo tar -xzf /path/to/backup/data.tar.gz

# Restore database
dropdb carbon6
createdb carbon6
psql carbon6 < /path/to/backup/database.sql

# Restart service
sudo launchctl load /Library/LaunchDaemons/com.vltrn.carbon6.plist
```

---

## Troubleshooting

### Cannot Access from Other Macs

**Check:**

1. **Firewall:** System Settings → Network → Firewall
2. **Server binding:** `.env` has `HOST=0.0.0.0`
3. **Network:** Both Macs on same network
4. **Port:** Test with `nc -zv mac-name.local 3006`

```bash
# Test from remote Mac
nc -zv carbon-server.local 3006

# If successful: "Connection to carbon-server.local 3006 port [tcp/*] succeeded!"
```

### Permission Denied

```bash
# Fix permissions
sudo chown -R root:staff /opt/carbon6
sudo chmod -R 755 /opt/carbon6

sudo chown -R root:staff /var/lib/carbon6
sudo chmod -R 775 /var/lib/carbon6
```

### PostgreSQL Connection Failed

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Check if database exists
psql -l | grep carbon6

# Test connection
psql -d carbon6 -c "SELECT 1;"
```

### Service Won't Start

```bash
# Check launchd logs
sudo log show --predicate 'subsystem == "com.vltrn.carbon6"' --last 1h

# Check service status
sudo launchctl list | grep carbon6

# Reload service
sudo launchctl unload /Library/LaunchDaemons/com.vltrn.carbon6.plist
sudo launchctl load /Library/LaunchDaemons/com.vltrn.carbon6.plist
```

---

## Uninstall

### Complete Removal

```bash
#!/bin/bash
# uninstall-carbon6.sh

# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.vltrn.carbon6.plist 2>/dev/null

# Remove service file
sudo rm /Library/LaunchDaemons/com.vltrn.carbon6.plist

# Remove application
sudo rm -rf /opt/carbon6

# Remove data
sudo rm -rf /var/lib/carbon6

# Remove logs
sudo rm -rf /var/log/carbon6

# Remove command
sudo rm /usr/local/bin/carbon6

# Drop database
dropdb carbon6 2>/dev/null

echo "Carbon6 uninstalled"
```

### Keep Data (Remove Application Only)

```bash
sudo rm -rf /opt/carbon6
sudo rm /usr/local/bin/carbon6
# Data remains in /var/lib/carbon6
```

---

## Summary

**Shared Installation Benefits:**

✅ **Accessible to all users** on the Mac
✅ **Network-ready** - accessible from any device
✅ **Centralized configuration** - one .env for everyone
✅ **System service** - runs automatically on boot
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
