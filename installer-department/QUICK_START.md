# Installer Department - Quick Start

Get your SDK packaged and distributed in under 10 minutes.

---

## Installation

### Step 1: Install SDK Builder

```bash
cd /Users/Morpheous/carbon6-platform/installer-department/sdk-builder
npm install
npm link
```

### Step 2: Verify Installation

```bash
sdk-builder --version
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     SDK BUILDER                                          ║
║                                                           ║
║     Package. Distribute. Deploy. At Scale.               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

1.0.0
```

---

## Create Your First SDK

### Example 1: Simple CLI Tool

```bash
# Initialize
sdk-builder init my-cli-tool --template cli

# Navigate
cd my-cli-tool

# You'll be prompted:
? Description: A powerful CLI tool
? Target platforms: macOS, Windows, Linux
? Package managers: npm, Homebrew
? Enable plugin support? Yes
? Enable auto-update? Yes
```

**Project structure created:**
```
my-cli-tool/
├── bin/
│   └── my-cli-tool           # CLI executable
├── lib/
│   ├── index.js              # Main logic
│   ├── commands/             # Command handlers
│   └── plugins/              # Plugin system
├── package.json
├── sdk-builder.config.json   # SDK Builder config
└── README.md
```

### Example 2: Full SDK with Plugins

```bash
# Initialize
sdk-builder init awesome-sdk --template sdk

# You'll get:
awesome-sdk/
├── lib/
│   ├── index.js              # SDK entry point
│   ├── core/                 # Core functionality
│   ├── plugins/              # Plugin architecture
│   └── utils/                # Utilities
├── examples/                 # Usage examples
├── docs/                     # Documentation
├── tests/                    # Test suite
└── sdk-builder.config.json
```

---

## Build Installers

### Build for All Platforms

```bash
cd my-cli-tool
sdk-builder build --all
```

**Output:**
```
Building my-cli-tool v1.0.0...
✓ macOS installer built
✓ Windows installer built
✓ Linux installer built

Installers created in dist/:
  dist/macos/Install my-cli-tool (Personal).command
  dist/macos/Install my-cli-tool (Shared).command
  dist/windows/Install my-cli-tool (Personal).bat
  dist/windows/Install my-cli-tool (Shared).bat
  dist/linux/install-my-cli-tool.sh
```

### Build Specific Platforms

```bash
# macOS only
sdk-builder build --macos

# Windows only
sdk-builder build --windows

# npm package
sdk-builder build --npm

# Homebrew formula
sdk-builder build --homebrew
```

---

## Test Your Installer

### macOS
```bash
# Test single-click installer
open "dist/macos/Install my-cli-tool (Personal).command"

# Or run directly
./dist/macos/Install\ my-cli-tool\ (Personal).command
```

### Windows
```powershell
# Double-click or run:
.\dist\windows\Install my-cli-tool (Personal).bat
```

### Linux
```bash
bash dist/linux/install-my-cli-tool.sh
```

---

## Distribute Your SDK

### Option 1: GitHub Releases

```bash
# First, ensure you have a GitHub repo
git init
git add .
git commit -m "Initial commit"
gh repo create my-cli-tool --public
git push -u origin main

# Publish release
sdk-builder publish --github
```

**Creates:**
- Release tag (v1.0.0)
- Release notes
- Installer attachments
- SHA256 checksums

### Option 2: npm Registry

```bash
# Login to npm (if not already)
npm login

# Publish
sdk-builder publish --npm
```

**Now users can install:**
```bash
npm install -g my-cli-tool
```

### Option 3: Homebrew

```bash
# Publish formula
sdk-builder publish --homebrew
```

**Now users can install:**
```bash
brew install my-cli-tool
```

### Option 4: All Channels

```bash
sdk-builder publish --all
```

---

## Add Plugins

### Create a Plugin

```bash
cd my-cli-tool
sdk-builder plugin create analytics
```

**Plugin structure:**
```
plugins/analytics/
├── plugin.json               # Plugin metadata
├── index.js                  # Plugin entry point
├── lib/                      # Plugin code
├── README.md
└── tests/
```

**Edit `plugins/analytics/index.js`:**
```javascript
module.exports = {
  name: 'analytics',
  version: '1.0.0',

  init: (sdk) => {
    sdk.track = (event, data) => {
      console.log('Tracking:', event, data);
    };
  }
};
```

### Use Plugin in Your SDK

**In `lib/index.js`:**
```javascript
const analytics = require('../plugins/analytics');

class MySDK {
  constructor() {
    this.plugins = [];
  }

  use(plugin) {
    plugin.init(this);
    this.plugins.push(plugin);
  }
}

const sdk = new MySDK();
sdk.use(analytics);
sdk.track('user_login', { userId: 123 });

module.exports = sdk;
```

---

## Version Management

### Bump Version

```bash
# Patch: 1.0.0 → 1.0.1
sdk-builder version patch

# Minor: 1.0.0 → 1.1.0
sdk-builder version minor

# Major: 1.0.0 → 2.0.0
sdk-builder version major
```

**Automatically updates:**
- `sdk-builder.config.json`
- `package.json`
- Creates git tag (if in git repo)

### Generate Changelog

```bash
sdk-builder changelog
```

**Creates `CHANGELOG.md`:**
```markdown
# Changelog

## [1.1.0] - 2026-02-18

### Added
- New analytics plugin
- Enhanced error handling

### Fixed
- Installation bug on Windows
```

---

## Real-World Example

Let's build a complete SDK from scratch:

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

Your SDK can integrate with the OiS system:

**In `lib/ois-integration.js`:**
```javascript
module.exports = {
  registerWithOiS: () => {
    // Register as OiS plugin
    console.log('Registering with OiS...');
  },

  invokeAgent: (agentName, task) => {
    // Invoke VLTRN Council agent
    console.log(`Invoking ${agentName}: ${task}`);
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

## Advanced Features

### Code Signing (macOS)

```bash
# Sign your installer
sdk-builder sign --macos --cert "Developer ID Application: Your Name (TEAMID)"
```

### Encryption

```bash
# Encrypt sensitive parts
sdk-builder encrypt --key production.key
```

### Analytics

```bash
# Track installations
sdk-builder analytics enable --provider mixpanel
```

### License Keys

```bash
# Add license validation
sdk-builder license add --key YOUR_LICENSE_KEY
```

---

## Troubleshooting

### "Command not found: sdk-builder"

```bash
# Re-link
cd /path/to/installer-department/sdk-builder
npm link
```

### Build Fails

```bash
# Check dependencies
npm install

# Verify config
cat sdk-builder.config.json

# Clean and rebuild
rm -rf dist
sdk-builder build --all
```

### Permission Denied

```bash
# Make installer executable
chmod +x dist/macos/*.command
chmod +x dist/linux/*.sh
```

---

## Next Steps

1. **Read Full Documentation**: [../docs/](../docs/)
2. **See Examples**: [../examples/](../examples/)
3. **Join Community**: Carbon Collective
4. **Get Support**: VLTRN Council - TECHNE

---

**You're ready to build and distribute professional SDKs!** 🚀
