# Installer Department - Complete Demo

This demonstrates the full workflow of creating, building, and distributing an installable SDK using the Installer Department system.

---

## What is Installer Department?

The **Installer Department** is a complete system that allows you to create professional, distributable SDKs and plugins with:
- **Multi-platform installers** (macOS, Windows, Linux)
- **Package manager distribution** (npm, Homebrew, Chocolatey)
- **Plugin architecture** like OiS
- **Auto-update capabilities**
- **Semantic versioning**
- **Single-click installers**

It's like having your own installation factory - similar to the Carbon6 installers we created, but now **you can create your own**.

---

## System Status

✅ **SDK Builder CLI** - Installed globally (`sdk-builder` command available)
✅ **Templates Ready** - SDK, CLI, and Plugin templates created
✅ **Multi-platform Support** - macOS, Windows, Linux builders
✅ **Distribution Channels** - GitHub, npm, Homebrew, Chocolatey, Docker

---

## Quick Start Example

### 1. Create a New SDK

```bash
# Initialize new SDK project
sdk-builder init my-awesome-sdk --template sdk

# You'll be prompted for:
# - Description
# - Target platforms (macOS, Windows, Linux)
# - Package managers (npm, Homebrew, Chocolatey)
# - Enable plugin support? (Yes/No)
# - Enable auto-update? (Yes/No)

cd my-awesome-sdk
```

**Result:**
```
my-awesome-sdk/
├── lib/
│   └── index.js              # Main SDK code with plugin support
├── examples/                 # Usage examples
├── docs/                     # Documentation
├── tests/                    # Test suite
├── package.json
├── sdk-builder.config.json   # Builder configuration
└── README.md
```

### 2. Add Your Code

```javascript
// lib/index.js - Already includes plugin architecture
class SDK {
  constructor(config = {}) {
    this.config = config;
    this.plugins = [];
  }

  use(plugin) {
    if (typeof plugin.init === 'function') {
      plugin.init(this);
    }
    this.plugins.push(plugin);
    return this;
  }

  // Add your SDK methods here
  track(event, data) {
    console.log('Tracking:', event, data);
  }
}

module.exports = SDK;
```

### 3. Build Installers

```bash
# Build for all platforms
sdk-builder build --all

# Or build specific platforms
sdk-builder build --macos      # macOS .command and .pkg
sdk-builder build --windows    # Windows .bat and .exe
sdk-builder build --linux      # Linux .sh, .deb, .rpm
sdk-builder build --npm        # npm package
sdk-builder build --homebrew   # Homebrew formula
```

**Result:**
```
dist/
├── macos/
│   ├── Install my-awesome-sdk (Personal).command
│   ├── Install my-awesome-sdk (Shared).command
│   └── my-awesome-sdk.pkg
├── windows/
│   ├── Install my-awesome-sdk (Personal).bat
│   ├── Install my-awesome-sdk (Shared).bat
│   └── my-awesome-sdk-setup.exe
├── linux/
│   ├── install-my-awesome-sdk.sh
│   ├── my-awesome-sdk.deb
│   └── my-awesome-sdk.rpm
└── npm/
    └── my-awesome-sdk-1.0.0.tgz
```

### 4. Test Your Installer

**macOS:**
```bash
# Single-click install
open "dist/macos/Install my-awesome-sdk (Personal).command"

# Or run directly
./dist/macos/Install\ my-awesome-sdk\ (Personal).command
```

**Windows:**
```powershell
# Double-click or run
.\dist\windows\Install my-awesome-sdk (Personal).bat
```

**Linux:**
```bash
bash dist/linux/install-my-awesome-sdk.sh
```

### 5. Distribute Your SDK

```bash
# Publish to GitHub Releases
sdk-builder publish --github

# Publish to npm
sdk-builder publish --npm

# Publish to Homebrew
sdk-builder publish --homebrew

# Or publish to all channels at once
sdk-builder publish --all
```

**Result:**
- **GitHub Releases**: Users download installers directly
- **npm**: `npm install -g my-awesome-sdk`
- **Homebrew**: `brew install my-awesome-sdk`
- **Chocolatey**: `choco install my-awesome-sdk`

---

## Creating a CLI Tool

```bash
# Initialize CLI tool
sdk-builder init my-cli --template cli
cd my-cli
```

**Generated structure:**
```
my-cli/
├── bin/
│   └── cli                   # CLI executable
├── lib/
│   └── index.js             # CLI logic
├── package.json
└── README.md
```

**Example CLI (already included in template):**
```javascript
#!/usr/bin/env node

const program = require('commander');

program
  .command('hello <name>')
  .description('Say hello')
  .action((name) => {
    console.log(`Hello, ${name}!`);
  });

program.parse(process.argv);
```

**Build and distribute:**
```bash
sdk-builder build --all
sdk-builder publish --npm

# Now users can install:
npm install -g my-cli
my-cli hello World  # Output: Hello, World!
```

---

## Plugin System

### Create a Plugin

```bash
cd my-awesome-sdk
sdk-builder plugin create analytics
```

**Generated:**
```
plugins/analytics/
├── plugin.json               # Plugin metadata
├── index.js                  # Plugin entry point
├── lib/                      # Plugin code
└── README.md
```

**Plugin code (template):**
```javascript
module.exports = {
  name: 'analytics',
  version: '1.0.0',

  init: (sdk) => {
    // Add analytics capability to SDK
    sdk.track = (event, data) => {
      console.log('[Analytics]', event, data);
    };
  }
};
```

### Use Plugin in SDK

```javascript
const SDK = require('my-awesome-sdk');
const analytics = require('./plugins/analytics');

const sdk = new SDK();
sdk.use(analytics);

sdk.track('user_login', { userId: 123 });
// Output: [Analytics] user_login { userId: 123 }
```

---

## Version Management

```bash
# Bump version
sdk-builder version patch   # 1.0.0 → 1.0.1
sdk-builder version minor   # 1.0.0 → 1.1.0
sdk-builder version major   # 1.0.0 → 2.0.0

# Generate changelog
sdk-builder changelog

# Tag release
git tag -a v1.1.0 -m "Version 1.1.0"
git push --tags
```

---

## Real-World Example: Analytics SDK

Let's create a complete analytics SDK from scratch:

```bash
# 1. Initialize
sdk-builder init vltrn-analytics --template sdk
cd vltrn-analytics

# 2. Add core functionality
cat > lib/index.js << 'EOF'
class VLTRNAnalytics {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.events = [];
  }

  track(event, properties) {
    this.events.push({
      event,
      properties,
      timestamp: new Date().toISOString()
    });
    console.log(`[Analytics] ${event}`, properties);
  }

  identify(userId, traits) {
    console.log(`[Analytics] Identified user: ${userId}`, traits);
  }

  flush() {
    console.log(`[Analytics] Flushing ${this.events.length} events`);
    this.events = [];
  }
}

module.exports = VLTRNAnalytics;
EOF

# 3. Add example
cat > examples/basic.js << 'EOF'
const VLTRNAnalytics = require('../lib');

const analytics = new VLTRNAnalytics('your-api-key');

analytics.identify('user123', {
  name: 'John Doe',
  email: 'john@example.com'
});

analytics.track('page_view', {
  page: '/home',
  referrer: 'google.com'
});

analytics.track('button_click', {
  button: 'sign_up',
  location: 'header'
});

analytics.flush();
EOF

# 4. Test it
node examples/basic.js

# 5. Build all installers
sdk-builder build --all

# 6. Test installer
open "dist/macos/Install vltrn-analytics (Personal).command"

# 7. Publish
sdk-builder version minor  # 1.0.0 → 1.1.0
sdk-builder publish --github --npm

# Done! Your SDK is live:
# - GitHub: https://github.com/you/vltrn-analytics/releases
# - npm: npm install vltrn-analytics
```

---

## Integration with OiS

Your SDK can integrate with the OiS (Operational Intelligence System):

```javascript
// lib/ois-integration.js
module.exports = {
  registerWithOiS: () => {
    console.log('Registering with OiS...');
    // Register as OiS plugin
  },

  invokeAgent: (agentName, task) => {
    console.log(`Invoking ${agentName}: ${task}`);
    // Invoke VLTRN Council agent
  }
};
```

**Users can then:**
```bash
# Install your SDK
npm install -g your-sdk

# Use with OiS
ois plugins install your-sdk

# Invoke via OiS
ois your-sdk <command>
```

---

## Comparison: Before vs After

### Before Installer Department
- Manual packaging scripts for each platform
- Inconsistent installer experiences
- No versioning system
- Manual distribution to each channel
- No plugin architecture
- Hours of setup for each new SDK

### After Installer Department
- Single command: `sdk-builder init my-sdk`
- Consistent, professional installers across all platforms
- Automatic semantic versioning
- One command publishes to all channels
- Built-in plugin system
- **5 minutes from idea to distributable SDK**

---

## Commands Reference

### Initialization
```bash
sdk-builder init <name>           # Create new SDK
sdk-builder init --template cli   # Create CLI tool
sdk-builder init --template plugin # Create plugin
```

### Development
```bash
sdk-builder dev                    # Start dev server
sdk-builder test                   # Run tests
sdk-builder lint                   # Lint code
```

### Building
```bash
sdk-builder build                  # Build all
sdk-builder build --all            # Build all platforms
sdk-builder build --macos          # macOS only
sdk-builder build --windows        # Windows only
sdk-builder build --linux          # Linux only
sdk-builder build --npm            # npm package
sdk-builder build --homebrew       # Homebrew formula
sdk-builder build --docker         # Docker image
sdk-builder build --watch          # Watch mode
```

### Versioning
```bash
sdk-builder version patch          # Bump patch version
sdk-builder version minor          # Bump minor version
sdk-builder version major          # Bump major version
sdk-builder changelog              # Generate changelog
```

### Distribution
```bash
sdk-builder publish --npm          # Publish to npm
sdk-builder publish --github       # GitHub release
sdk-builder publish --homebrew     # Homebrew tap
sdk-builder publish --chocolatey   # Chocolatey gallery
sdk-builder publish --all          # Publish everywhere
```

### Plugin Management
```bash
sdk-builder plugin create <name>   # Create plugin
sdk-builder plugin publish <name>  # Publish plugin
sdk-builder plugin install <name>  # Install plugin
```

---

## What Gets Built

### macOS Installers
- **Personal (.command)**: Installs to `~/your-sdk` (user-specific)
- **Shared (.command)**: Installs to `/opt/your-sdk` (system-wide, network-accessible)
- **Package (.pkg)**: Native macOS installer package
- **Homebrew**: Formula for `brew install your-sdk`

### Windows Installers
- **Personal (.bat)**: Installs to `C:\Users\Name\your-sdk`
- **Shared (.bat)**: Installs to `C:\your-sdk` (accessible to all users)
- **Executable (.exe)**: NSIS installer with GUI
- **Chocolatey**: Package for `choco install your-sdk`

### Linux Installers
- **Shell Script (.sh)**: Universal installer
- **Debian (.deb)**: For Ubuntu/Debian
- **Red Hat (.rpm)**: For Fedora/RHEL
- **Snap**: Containerized package
- **AppImage**: Portable executable

### Cross-Platform
- **npm**: JavaScript package manager
- **Docker**: Container image
- **pip**: Python package (if applicable)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  USER CREATES SDK                        │
│         sdk-builder init my-awesome-sdk                  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              SDK BUILDER GENERATES                       │
│  • Project structure from templates                      │
│  • package.json with metadata                            │
│  • Plugin architecture scaffolding                       │
│  • sdk-builder.config.json                               │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              USER DEVELOPS SDK                           │
│  • Add core functionality                                │
│  • Create plugins                                        │
│  • Write tests and docs                                  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              BUILD INSTALLERS                            │
│         sdk-builder build --all                          │
│                                                          │
│  PACKAGER      → Bundle code                             │
│  INSTALLER     → Create platform installers              │
│  BUILDER       → Compile executables                     │
│  VERSIONER     → Tag release                             │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              DISTRIBUTE                                  │
│         sdk-builder publish --all                        │
│                                                          │
│  DISTRIBUTOR   → GitHub Releases                         │
│                → npm Registry                            │
│                → Homebrew                                │
│                → Chocolatey                              │
│                → Docker Hub                              │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              END USERS INSTALL                           │
│  • npm install -g my-awesome-sdk                         │
│  • brew install my-awesome-sdk                           │
│  • choco install my-awesome-sdk                          │
│  • Double-click installer                                │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Read Full Documentation**: [README.md](README.md)
2. **See Quick Start**: [QUICK_START.md](QUICK_START.md)
3. **Create Your First SDK**: Follow the examples above
4. **Join Carbon Collective**: Share your SDKs with the community
5. **Contribute**: Help improve the Installer Department

---

## Support

- **Issues**: [GitHub Issues](https://github.com/VltrnOne/carbon6-platform/issues)
- **Documentation**: [Full Docs](docs/)
- **Community**: Carbon Collective
- **Council**: VLTRN Council - Carbon Domain

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package. Distribute. Deploy. At Scale.
Installer Department - Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
