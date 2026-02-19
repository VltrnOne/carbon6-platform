# Installer Department

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     INSTALLER DEPARTMENT                                 ║
║                                                           ║
║     Package. Distribute. Deploy. At Scale.               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Build installable SDKs and plugins for any platform**

Part of VLTRN Council - Carbon Domain
Classification: L3-CONFIDENTIAL

---

## Overview

The Installer Department is a complete system for:
- 📦 **Packaging** - Bundle SDKs/plugins into distributable formats
- 🚀 **Building** - Create installers for macOS, Windows, Linux
- 🌐 **Distribution** - Deploy via GitHub, npm, Homebrew, Chocolatey
- 🔄 **Versioning** - Semantic versioning and auto-updates
- 🔌 **Plugins** - Plugin architecture system like OiS

---

## Agent Team

### Tier 2: Domain Specialists (L3-CONFIDENTIAL)

**PACKAGER** - SDK Packaging Specialist
- Role: Bundle code into distributable packages
- Capabilities: npm, pip, gem, cargo, go modules
- Output: Tarball, zip, executable bundles

**INSTALLER-ARCHITECT** - Installation System Designer
- Role: Design installer flows and UX
- Capabilities: Multi-platform installer design
- Output: Installer specifications, user flows

**DISTRIBUTOR** - Distribution Channel Manager
- Role: Publish to package managers and platforms
- Capabilities: GitHub Releases, npm, Homebrew, apt, yum
- Output: Published packages, release notes

**VERSIONER** - Version Control Specialist
- Role: Semantic versioning and changelog management
- Capabilities: SemVer, git tags, version bumping
- Output: Version numbers, changelogs, migration guides

**UPDATER** - Auto-Update System Engineer
- Role: Build auto-update mechanisms
- Capabilities: Delta updates, rollback, notification
- Output: Update clients, patch systems

---

## Directory Structure

```
installer-department/
├── agents/                    # Agent definitions
│   ├── PACKAGER.json
│   ├── INSTALLER-ARCHITECT.json
│   ├── DISTRIBUTOR.json
│   ├── VERSIONER.json
│   └── UPDATER.json
│
├── templates/                 # Installer templates
│   ├── macos/
│   │   ├── .command           # Single-click installer
│   │   ├── .pkg              # macOS package
│   │   └── homebrew/         # Homebrew formula
│   ├── windows/
│   │   ├── .bat              # Batch installer
│   │   ├── .exe              # Executable installer
│   │   └── chocolatey/       # Chocolatey package
│   ├── linux/
│   │   ├── .sh               # Shell installer
│   │   ├── .deb              # Debian package
│   │   ├── .rpm              # Red Hat package
│   │   └── snap/             # Snap package
│   └── cross-platform/
│       ├── npm/              # npm package
│       ├── pip/              # Python package
│       └── docker/           # Docker image
│
├── builders/                  # Build scripts
│   ├── build-macos.sh
│   ├── build-windows.ps1
│   ├── build-linux.sh
│   ├── build-npm.sh
│   ├── build-docker.sh
│   └── build-all.sh
│
├── distributors/              # Distribution scripts
│   ├── github-release.sh
│   ├── npm-publish.sh
│   ├── homebrew-publish.sh
│   ├── chocolatey-publish.ps1
│   └── docker-publish.sh
│
├── docs/                      # Documentation
│   ├── QUICK_START.md
│   ├── BUILDING.md
│   ├── DISTRIBUTING.md
│   ├── PLUGIN_SYSTEM.md
│   └── API.md
│
├── examples/                  # Example SDKs
│   ├── simple-cli/           # Basic CLI tool
│   ├── plugin-system/        # Plugin architecture
│   └── full-sdk/             # Complete SDK with plugins
│
└── sdk-builder/              # SDK Builder CLI
    ├── bin/sdk-builder
    ├── lib/
    └── templates/
```

---

## Quick Start

### Install SDK Builder

```bash
cd installer-department/sdk-builder
npm link
```

### Create New SDK

```bash
# Initialize new SDK
sdk-builder init my-awesome-sdk

# Answer prompts:
# - SDK name
# - Description
# - Platform targets (macOS, Windows, Linux)
# - Package managers (npm, Homebrew, Chocolatey)
# - Plugin support (yes/no)
# - Auto-update (yes/no)

cd my-awesome-sdk
```

### Build Installers

```bash
# Build for all platforms
sdk-builder build --all

# Build specific platform
sdk-builder build --macos
sdk-builder build --windows
sdk-builder build --linux

# Build package manager versions
sdk-builder build --npm
sdk-builder build --homebrew
sdk-builder build --docker
```

### Distribute

```bash
# Publish to GitHub Releases
sdk-builder publish --github

# Publish to npm
sdk-builder publish --npm

# Publish to Homebrew
sdk-builder publish --homebrew

# Publish all
sdk-builder publish --all
```

---

## Features

### 📦 Multi-Platform Packaging

**macOS:**
- ✅ `.command` - Single-click terminal installer
- ✅ `.pkg` - Native macOS package
- ✅ Homebrew formula
- ✅ DMG with drag-to-install

**Windows:**
- ✅ `.bat` - Batch installer
- ✅ `.exe` - NSIS installer
- ✅ Chocolatey package
- ✅ MSI installer

**Linux:**
- ✅ `.sh` - Shell installer
- ✅ `.deb` - Debian/Ubuntu package
- ✅ `.rpm` - Red Hat/Fedora package
- ✅ Snap package
- ✅ AppImage

**Cross-Platform:**
- ✅ npm package (Node.js)
- ✅ pip package (Python)
- ✅ Docker image
- ✅ Cargo crate (Rust)

### 🔌 Plugin Architecture

Built-in plugin system like OiS:

```javascript
// Your SDK with plugins
const sdk = require('your-sdk');

// List plugins
sdk.plugins.list();

// Install plugin
sdk.plugins.install('awesome-plugin');

// Use plugin
sdk.use('awesome-plugin');
```

### 🔄 Auto-Update System

```javascript
// Check for updates
sdk.update.check();

// Auto-update
sdk.update.install();

// Rollback
sdk.update.rollback();
```

### 📊 Version Management

```bash
# Bump version
sdk-builder version patch  # 1.0.0 → 1.0.1
sdk-builder version minor  # 1.0.0 → 1.1.0
sdk-builder version major  # 1.0.0 → 2.0.0

# Generate changelog
sdk-builder changelog

# Tag release
sdk-builder release
```

---

## SDK Builder Commands

```bash
# Initialize
sdk-builder init <name>           # Create new SDK
sdk-builder init --template cli   # Use template

# Development
sdk-builder dev                    # Start dev server
sdk-builder test                   # Run tests
sdk-builder lint                   # Lint code

# Building
sdk-builder build                  # Build all
sdk-builder build --platform macos # Build specific
sdk-builder build --watch          # Watch mode

# Versioning
sdk-builder version <type>         # Bump version
sdk-builder changelog              # Generate changelog
sdk-builder release                # Create release

# Distribution
sdk-builder publish --npm          # Publish to npm
sdk-builder publish --github       # GitHub release
sdk-builder publish --all          # Publish everywhere

# Plugin Management
sdk-builder plugin create <name>   # Create plugin
sdk-builder plugin publish <name>  # Publish plugin
sdk-builder plugin install <name>  # Install plugin
```

---

## Templates

### CLI Tool Template
```bash
sdk-builder init my-cli --template cli
```

Creates:
- Argument parsing
- Config file support
- Plugin system
- Auto-update
- Help system
- Version command

### SDK Template
```bash
sdk-builder init my-sdk --template sdk
```

Creates:
- Core library
- Plugin architecture
- API documentation
- Examples
- Test suite
- CI/CD pipeline

### Plugin Template
```bash
sdk-builder plugin create my-plugin
```

Creates:
- Plugin scaffold
- Metadata
- Installation hooks
- Documentation
- Tests

---

## Integration Examples

### Carbon SDK Integration

```javascript
// your-sdk/lib/carbon-integration.js
const carbon = require('carbon-collective-sdk');

module.exports = {
  track: (project) => carbon.track(project),
  sync: () => carbon.sync(),
  status: () => carbon.status()
};
```

### OiS Integration

```javascript
// your-sdk/lib/ois-integration.js
module.exports = {
  registerAgent: (name, definition) => {
    // Register with OiS agent system
  },

  invokeAgent: (name, task) => {
    // Invoke VLTRN Council agent
  }
};
```

---

## Distribution Channels

### GitHub Releases
```bash
# Automatic release creation
sdk-builder publish --github

# Creates:
# - Release tag
# - Release notes from changelog
# - Binary attachments
# - Asset checksums
```

### npm Registry
```bash
# Publish to npm
sdk-builder publish --npm

# Scoped package
sdk-builder publish --npm --scope @yourorg
```

### Homebrew
```bash
# Create and publish formula
sdk-builder publish --homebrew

# Updates:
# - Formula file
# - SHA256 checksum
# - Version number
# - Submits PR to homebrew-core
```

### Chocolatey
```powershell
# Publish to Chocolatey
sdk-builder publish --chocolatey

# Creates:
# - .nuspec file
# - Installation script
# - Submits to chocolatey.org
```

---

## Advanced Features

### Code Signing

```bash
# macOS
sdk-builder sign --macos --cert "Developer ID"

# Windows
sdk-builder sign --windows --cert certificate.pfx

# Verify
sdk-builder verify dist/installer.pkg
```

### Encryption

```bash
# Encrypt distribution
sdk-builder encrypt --key production.key

# Decrypt on install
# Auto-handled by installer
```

### Analytics

```javascript
// Track installations
sdk.analytics.track('install', {
  version: '1.0.0',
  platform: 'macos',
  installMethod: 'homebrew'
});
```

### License Management

```bash
# Add license key validation
sdk-builder license add --key LICENSE_KEY

# Validate on runtime
sdk.license.validate();
```

---

## Workflow

### 1. Create SDK
```bash
sdk-builder init awesome-sdk --template sdk
cd awesome-sdk
```

### 2. Develop
```bash
# Write your code
vim lib/index.js

# Add plugins
sdk-builder plugin create auth
sdk-builder plugin create storage
```

### 3. Test
```bash
sdk-builder test
sdk-builder lint
```

### 4. Version
```bash
# Bump version
sdk-builder version minor

# Update changelog
sdk-builder changelog
```

### 5. Build
```bash
# Build all platforms
sdk-builder build --all
```

### 6. Distribute
```bash
# Publish everywhere
sdk-builder publish --all

# Or specific channels
sdk-builder publish --github --npm
```

---

## Example: Creating a New SDK

```bash
# Initialize
sdk-builder init vltrn-analytics --template sdk

# Configure
cd vltrn-analytics
vim package.json  # Update metadata

# Add core functionality
mkdir lib
cat > lib/index.js << 'EOF'
module.exports = {
  track: (event, data) => {
    console.log('Tracking:', event, data);
  },

  identify: (userId) => {
    console.log('Identified:', userId);
  }
};
EOF

# Add plugin
sdk-builder plugin create dashboards

# Build
sdk-builder build --all

# Test
./dist/macos/Install\ vltrn-analytics\ (Shared).command

# Publish
sdk-builder version minor
sdk-builder publish --github --npm
```

---

## Documentation

- **Quick Start**: [docs/QUICK_START.md](docs/QUICK_START.md)
- **Building**: [docs/BUILDING.md](docs/BUILDING.md)
- **Distribution**: [docs/DISTRIBUTING.md](docs/DISTRIBUTING.md)
- **Plugin System**: [docs/PLUGIN_SYSTEM.md](docs/PLUGIN_SYSTEM.md)
- **API Reference**: [docs/API.md](docs/API.md)

---

## Examples

Live examples in `examples/`:
- **simple-cli** - Basic CLI tool with OiS integration
- **plugin-system** - Full plugin architecture
- **full-sdk** - Complete SDK with all features

---

## Support

- **Issues**: GitHub Issues
- **Documentation**: [Full Docs](docs/)
- **Community**: Carbon Collective
- **Council**: VLTRN Council - TECHNE domain

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package. Distribute. Deploy. At Scale.
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
