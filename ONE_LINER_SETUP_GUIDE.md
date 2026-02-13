# One-Liner Installation Setup Guide

**Get your one-liner install command ready in 10 minutes**

---

## 🚀 Quick Setup (3 Steps)

### **Step 1: Run Setup Script**

```bash
cd /Users/Morpheous/Carbon6/platform
./setup-one-liner.sh
```

**You'll be prompted for:**
- GitHub username (e.g., `vltrn`, `morpheous`, etc.)
- Repository name (default: `carbon6-platform`)

**Script automatically:**
- ✅ Updates `remote-install.sh` with your repo URL
- ✅ Initializes git repository (if needed)
- ✅ Adds GitHub remote
- ✅ Creates `ONE_LINER_INSTALL.txt` with your command
- ✅ Shows next steps

---

### **Step 2: Create GitHub Repository**

**Go to:** https://github.com/new

**Settings:**
- **Name:** `carbon6-platform` (or whatever you chose)
- **Visibility:** Public (recommended) or Private
- **DO NOT** initialize with README
- Click "Create repository"

---

### **Step 3: Push Installer**

```bash
# Still in /Users/Morpheous/Carbon6/platform

# Add all installer files
git add .

# Commit
git commit -m "Add Carbon6 OiS One-Liner Installer"

# Push to GitHub
git push -u origin main
```

**Done!** Your one-liner is now live. 🎉

---

## 📋 Your One-Liner Command

After pushing to GitHub, your one-liner will be:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh | bash
```

**Find it in:** `ONE_LINER_INSTALL.txt`

---

## 🧪 Test It (Recommended)

**Before sharing, test on a clean macOS system:**

```bash
# On a different Mac (or VM)
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh | bash

# Should:
✓ Check macOS version
✓ Clone repository to ~/Carbon6/platform
✓ Make scripts executable
✓ Launch interactive installer
```

**If you don't have another Mac:**
- Test in a fresh user account
- Or test with a colleague
- Or just verify the URL loads: `curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh`

---

## 🎯 Distribution Examples

### **Email Announcement**

```
Subject: Carbon6 OiS - Install in One Command

We're excited to announce the Carbon6 Operational Intelligence System!

INSTALL NOW (3 minutes):
curl -sSL https://install.carbon6.io | bash

FEATURES:
• 462 AI agents with GENESIS orchestrator
• 88x™ Chairman Console
• 10-Gate security system
• OS-style guided installation

REQUIREMENTS:
• macOS 12+
• 8GB RAM
• 10GB disk space
• 40-65 minutes installation time

Questions? Reply to this email or visit:
https://github.com/YOUR_USERNAME/carbon6-platform
```

---

### **Slack/Discord Message**

```
🚀 Carbon6 OiS is ready!

Install with one command:
```bash
curl -sSL https://install.carbon6.io | bash
```

AI agents will guide you through the entire setup.
No prior knowledge required! 🤖

Docs: https://github.com/YOUR_USERNAME/carbon6-platform
```

---

### **Twitter/X Post**

```
Just shipped: Carbon6 OiS - Enterprise AI platform with 462 agents

Install in one line:
curl -sSL https://install.carbon6.io | bash

Features:
🤖 462 Council agents
🔐 10-Gate security
⚡ 12 NVIDIA backends
🎯 OS-style installer

macOS 12+ required
```

---

## 🌐 Custom Domain (Optional)

**Make it even shorter with your domain:**

### **Option 1: GitHub Short URL (Free)**

```bash
# Create short URL (one-time setup)
curl https://git.io/ \
  -i \
  -F "url=https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh" \
  -F "code=carbon6-install"

# Your new URL: https://git.io/carbon6-install
```

**Share:**
```bash
curl -sSL https://git.io/carbon6-install | bash
```

---

### **Option 2: Custom Domain (install.carbon6.io)**

**If you own carbon6.io:**

**DNS Setup (Redirect):**
```
Type: CNAME
Name: install
Value: raw.githubusercontent.com
```

**Or use a redirect service:**
```nginx
# nginx on your server
server {
    listen 443 ssl http2;
    server_name install.carbon6.io;

    location / {
        return 301 https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh;
    }
}
```

**Share:**
```bash
curl -sSL https://install.carbon6.io | bash
```

---

## 🔐 Security Verification

**Users can verify before running:**

### **View script first:**
```bash
# Download and inspect
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh > install.sh

# Review code
cat install.sh

# Run if satisfied
bash install.sh
```

### **Checksum verification (advanced):**
```bash
# You provide checksum (after pushing to GitHub)
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh | shasum -a 256

# Users verify
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/carbon6-platform/main/remote-install.sh | shasum -a 256
# Should match your published checksum
```

---

## 📊 Track Installations (Optional)

**Add anonymous analytics to `remote-install.sh`:**

```bash
# Add after line 7 (set -e)
INSTALL_ID=$(uuidgen)
INSTALL_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Add before "Clone or update repository" (line 31)
curl -X POST https://analytics.carbon6.io/install \
  -H "Content-Type: application/json" \
  -d "{
    \"install_id\": \"$INSTALL_ID\",
    \"timestamp\": \"$INSTALL_TIME\",
    \"os\": \"$(uname -s)\",
    \"os_version\": \"$(sw_vers -productVersion 2>/dev/null || echo 'unknown')\"
  }" > /dev/null 2>&1 || true
```

**Privacy-friendly:**
- No personal information
- Anonymous UUID
- Fails silently if analytics down
- Can't block installation

---

## 🆘 Troubleshooting

### **"Repository not found"**

**Solution:** Ensure repository is public or user has access
```bash
# Make repository public on GitHub
Settings → Danger Zone → Change visibility → Public
```

---

### **"Permission denied"**

**Solution:** User needs to allow Terminal (macOS security)
```
System Settings → Privacy & Security → Full Disk Access → Terminal
```

---

### **"Connection refused"**

**Solution:** Check internet connection or GitHub status
```bash
# Test GitHub connectivity
curl -I https://github.com

# Check GitHub status: https://www.githubstatus.com/
```

---

## 📋 Pre-Distribution Checklist

Before sharing your one-liner:

- [ ] Ran `./setup-one-liner.sh` successfully
- [ ] Created GitHub repository
- [ ] Pushed all installer files to main branch
- [ ] Tested one-liner on clean system (or verified URL loads)
- [ ] Reviewed `ONE_LINER_INSTALL.txt`
- [ ] (Optional) Set up custom domain
- [ ] (Optional) Added analytics tracking
- [ ] Prepared announcement message
- [ ] Set up support channel (Issues, Email, Discord)

---

## 🎓 What Happens When Users Run It

**Step-by-step user experience:**

```bash
$ curl -sSL https://install.carbon6.io | bash

🚀 Carbon6 OiS Remote Installation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ macOS 13.6 detected
✓ System requirements met
📥 Downloading Carbon6 OiS to ~/Carbon6/platform...

Cloning into '/Users/john/Carbon6/platform'...
remote: Enumerating objects: 87, done.
remote: Counting objects: 100% (87/87), done.
remote: Compressing objects: 100% (65/65), done.
Receiving objects: 100% (87/87), 245.32 KiB | 2.18 MiB/s, done.

✓ Scripts ready
✅ Ready to install!

Start installation now? [Y/n] y

 ██████╗ █████╗ ██████╗ ██████╗  ██████╗ ███╗   ██╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝
██║     ███████║██████╔╝██████╔╝██║   ██║██╔██╗ ██║███████╗

        OPERATIONAL INTELLIGENCE SYSTEM
        AGENTIC-FIRST INSTALLATION

Installation Progress:

  ○ Part 0: Pre-Flight (PRAXIS) - Pending
  ○ Part 1: Pre-Installation (SCOUT) - Pending
  ○ Part 2: Main Installation (GENESIS) - Pending
  ○ Part 3: Post-Installation (SOVEREIGN) - Pending

Options:

  1) Full Installation (Recommended)
  2) Quick Start (Developer Mode)
  3) Custom Installation (Advanced)

  9) View Installation Log
  0) Exit

Select option [1-3, 9, 0]: _
```

**Then AI agents take over!** 🤖

---

## 🎉 Success!

Your one-liner is ready to share. Users can install Carbon6 OiS with a single command, and the AI agents will guide them through the entire process.

**No manual configuration. No prior knowledge required. Just one command.** ✨

```
Document ID: L5-ONE-LINER-2026-001
Classification: L5-BLACK
Version: 1.0.0
```
