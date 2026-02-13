# Carbon6 Platform - Deployment Guide

## GitHub Repository Setup

### 1. Create GitHub Repository

```bash
# Option A: Using GitHub CLI (recommended)
cd /Users/Morpheous/carbon6-platform
gh repo create VltrnOne/carbon6-platform --public --source=. --remote=origin --push

# Option B: Manual via GitHub.com
# 1. Go to: https://github.com/organizations/VltrnOne/repositories/new
# 2. Repository name: carbon6-platform
# 3. Description: "Carbon6 Platform - Unified installation system"
# 4. Visibility: Public
# 5. Click "Create repository"
```

### 2. Push to GitHub (if using manual method)

```bash
cd /Users/Morpheous/carbon6-platform
git remote add origin https://github.com/VltrnOne/carbon6-platform.git
git branch -M main
git push -u origin main
```

### 3. Verify Installation URL

After pushing, the installation command will be:

```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

---

## Testing the Installer

### Local Test (before publishing)

```bash
# Test the script locally
cd /Users/Morpheous/carbon6-platform
bash remote-install.sh
```

### Remote Test (after publishing to GitHub)

```bash
# Test the curl command
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

---

## Repository Settings (Recommended)

### Branch Protection

1. Go to: `Settings → Branches → Add branch protection rule`
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Require status checks to pass

### Repository Description

```
Carbon6 Platform - Unified installation system for Carbon Collective SDK and Platform. One-command setup for creator collective infrastructure.
```

### Topics/Tags

Add these topics for discoverability:
- `carbon6`
- `vltrn`
- `creator-platform`
- `installation-script`
- `sdk`
- `shell-script`
- `developer-tools`

### About Section

- **Website**: https://carbon6.dev (or your domain)
- **Topics**: (as listed above)
- **Releases**: Enable releases for versioning

---

## Release Management

### Creating a Release

```bash
# Tag the current version
git tag -a v1.0.0 -m "Release v1.0.0: Initial Carbon6 Platform installer"
git push origin v1.0.0

# Or use GitHub CLI
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "
## Features
- Unified installation for Carbon Collective SDK + Platform
- Automatic dependency detection
- Environment configuration
- Helper scripts for development

## Installation
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
\`\`\`
"
```

---

## Updating the Installer

### After making changes:

```bash
cd /Users/Morpheous/carbon6-platform

# Make your changes to remote-install.sh

# Test locally first
bash remote-install.sh

# Commit and push
git add .
git commit -m "fix: improve error handling in installer"
git push origin main

# The curl command automatically uses the latest version!
```

---

## Integration with Other Repos

### Update carbon-collective README

Add a reference to the unified installer:

```markdown
## Quick Install

**Recommended**: Install the complete Carbon6 Platform (SDK + Website)
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
\`\`\`

**SDK Only**:
\`\`\`bash
curl -fsSL https://raw.githubusercontent.com/VltrnOne/carbon-collective/main/install.sh | bash
\`\`\`
```

### Update Carbon6 README

Add a reference to the unified installer:

```markdown
## Installation

**Recommended**: Use the unified Carbon6 Platform installer
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
\`\`\`

This installs both the platform and the Carbon Collective SDK.
```

---

## Monitoring & Analytics

### Track Installation Success

You can track installs by adding analytics to the script (optional):

```bash
# Add to remote-install.sh (end of script)
curl -s "https://analytics.carbon6.dev/install?version=1.0.0&os=$(uname -s)" > /dev/null 2>&1 || true
```

### Monitor Issues

- Watch GitHub Issues for installation problems
- Check GitHub Discussions for questions
- Monitor curl request logs if using custom domain

---

## Security Considerations

### Script Integrity

**Current approach**: Users pipe curl directly to bash
- ✅ Simple and convenient
- ⚠️  Requires trust in the repository

**Enhanced security** (optional):

```bash
# Download, review, then execute
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh -o install.sh
less install.sh  # Review the script
bash install.sh
```

### Checksum Verification (advanced)

For paranoid users, provide SHA256 checksums:

```bash
# Generate checksum
sha256sum remote-install.sh > remote-install.sh.sha256

# Users can verify:
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh -o install.sh
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh.sha256 -o install.sh.sha256
sha256sum -c install.sh.sha256
bash install.sh
```

---

## Rollback Procedure

### If the installer has a critical bug:

```bash
# 1. Revert to previous commit
git revert HEAD
git push origin main

# 2. Or force push to last known good commit
git reset --hard <previous-commit-hash>
git push --force origin main

# 3. Update release notes warning users
gh release create v1.0.1 --title "v1.0.1 - Hotfix" --notes "Fixed critical installation bug"
```

---

## Distribution Checklist

Before announcing the installer publicly:

- [ ] Repository is public
- [ ] Install script is executable (`chmod +x`)
- [ ] README has clear instructions
- [ ] Quick start guide exists
- [ ] Tested on clean system (macOS)
- [ ] Tested on clean system (Linux)
- [ ] Error messages are helpful
- [ ] Success messages are clear
- [ ] Links in documentation work
- [ ] Example commands work
- [ ] Repository has topics/tags
- [ ] License file exists (ISC)
- [ ] Contributing guidelines exist (optional)
- [ ] Code of conduct exists (optional)

---

## Next Steps After Deployment

1. **Announce on Discord**: Share in #carbon-announcements
2. **Update Team Docs**: Add to onboarding materials
3. **Create Video Tutorial**: Screen recording of installation
4. **Monitor Feedback**: Watch for issues/questions first 48 hours
5. **Iterate**: Update based on real-world usage

---

**Ready to deploy?**

```bash
gh repo create VltrnOne/carbon6-platform --public --source=. --remote=origin --push
```

Then test:

```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```
