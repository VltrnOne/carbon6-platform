# OiS - Operational Intelligence System

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     OiS - OPERATIONAL INTELLIGENCE SYSTEM                ║
║                                                           ║
║     Terminal-First Operating System                      ║
║     Built on Carbon6 Platform                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**The lightweight, terminal-based OS layer for Carbon6 Platform**

---

## Quick Start

### Install via Carbon6 Platform

```bash
# Install complete platform (includes OiS)
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash

# Or install OiS standalone
npm install -g @vltrn/ois
```

### Initialize

```bash
ois init
```

### Basic Commands

```bash
# System status
ois status

# List available agents
ois agents

# Execute task
ois task "deploy my application"

# Manage plugins
ois plugins
ois plugins install ois-carbon
```

---

## Features

### ✅ Terminal-First
- CLI-native interface
- Zero GUI dependency
- Fast, lightweight (<50MB)
- Shell integration (bash, zsh, fish)

### ✅ Plugin Architecture
- Hot-swappable capabilities
- Modular design
- Custom plugin development
- Secure sandboxing

### ✅ AI Agent Integration
- Direct VLTRN Council access
- Natural language task execution
- Multi-agent orchestration
- Intelligent routing

### ✅ Carbon6 Integration
- Seamless SDK integration
- Auto-sync capabilities
- Project tracking
- Team collaboration

---

## Command Reference

### System

```bash
ois init [--full|--lite]    # Initialize OiS
ois status                   # System health
ois version                  # Version info
ois config                   # Show configuration
ois update                   # Update OiS
```

### Plugins

```bash
ois plugins                  # List all plugins
ois plugins install <name>   # Install plugin
ois plugins remove <name>    # Remove plugin
ois plugins enable <name>    # Enable plugin
ois plugins disable <name>   # Disable plugin
```

### Agents

```bash
ois agents                          # List available agents
ois agents invoke <agent> <task>    # Invoke specific agent
ois task "natural language task"    # Auto-route to best agent
```

### Carbon6

```bash
ois carbon status   # Carbon SDK status
ois carbon sync     # Force sync
ois carbon track    # Track project
```

---

## Architecture

```
Terminal → OiS Shell → Plugins → Carbon6 SDK → VLTRN Council
```

### Directory Structure

```
~/.ois/
├── config/
│   ├── ois.json          # Main configuration
│   └── plugins.json      # Plugin registry
├── plugins/              # Installed plugins
├── data/
│   ├── metrics/          # System metrics
│   ├── logs/             # Audit logs
│   └── sessions/         # Session history
├── cache/                # Intelligence cache
└── bin/
    └── ois               # Main executable
```

---

## Core Plugins

| Plugin | Description | Status |
|--------|-------------|--------|
| `ois-carbon` | Carbon6 SDK integration | Available |
| `ois-council` | VLTRN Council agents | Available |
| `ois-nvidia` | GPU acceleration | Available |
| `ois-flow` | Workflow automation | Available |
| `ois-intel` | Intelligence gathering | Available |
| `ois-secure` | Security & encryption | Available |

---

## Available Agents

| Tier | Agent | Description |
|------|-------|-------------|
| L5-BLACK | GENESIS | Divine Orchestrator |
| L4-RESTRICTED | SOVEREIGN | Strategic Command |
| L4-RESTRICTED | MNEMOS | Memory & Knowledge |
| L4-RESTRICTED | AEGIS | Security Guardian |
| L4-RESTRICTED | PRAXIS | Operations Director |
| L3-CONFIDENTIAL | TECHNE | Technology & Development |
| L3-CONFIDENTIAL | AURUM | Finance & Treasury |
| L3-CONFIDENTIAL | SOPHIA | Research & Intelligence |
| L3-CONFIDENTIAL | MERCATOR | Marketing & Growth |
| L3-CONFIDENTIAL | MELODIA | Creative & Media |
| L3-CONFIDENTIAL | DATUM | Data & Analytics |

---

## Configuration

Default config at `~/.ois/config/ois.json`:

```json
{
  "system": {
    "version": "1.0.0",
    "mode": "lite",
    "shell": "bash"
  },
  "intelligence": {
    "enabled": true,
    "auto_optimize": true,
    "predictive_mode": true
  },
  "carbon6": {
    "sdk_path": "~/carbon-collective",
    "platform_path": "~/Carbon6",
    "auto_sync": true,
    "sync_interval": 30
  },
  "council": {
    "endpoint": "https://council.vltrn.dev",
    "clearance_level": "L3-CONFIDENTIAL",
    "agents": ["GENESIS", "SOVEREIGN", "TECHNE", "AURUM"]
  },
  "security": {
    "encryption": "AES-256-GCM",
    "audit_logging": true,
    "secure_mode": true
  }
}
```

---

## Plugin Development

Create custom plugins:

```javascript
// ~/.ois/plugins/my-plugin/index.js

module.exports = {
  name: 'my-plugin',
  version: '1.0.0',

  commands: [
    {
      name: 'hello',
      description: 'Say hello',
      execute: async (args) => {
        return `Hello, ${args.name || 'World'}!`;
      }
    }
  ],

  async install() {
    console.log('Installing my-plugin...');
  },

  async uninstall() {
    console.log('Uninstalling my-plugin...');
  }
};
```

---

## Upgrade Path

OiS (lite) can be upgraded to full OS:

```bash
ois upgrade --to full-os
```

**Full OS features:**
- Desktop environment (optional)
- GUI applications
- Hardware drivers
- System services
- Advanced networking

---

## Security

- **Encryption**: AES-256-GCM at rest, TLS 1.3 in transit
- **Audit Logging**: All commands logged with timestamp, user, result
- **Sandboxing**: Plugins run in isolated environments
- **Clearance Levels**: L1-L5 security model

---

## Performance

| Metric | Value |
|--------|-------|
| Cold start | < 500ms |
| Command execution | < 100ms |
| Agent invocation | < 2s |
| Memory footprint | ~50 MB idle |
| Disk usage | ~100 MB |

---

## License

Proprietary - VLTRN Council
Exclusive to Carbon6 Platform users

---

## Links

- **Documentation**: See OIS_ARCHITECTURE.md
- **Carbon6 Platform**: https://github.com/VltrnOne/carbon6-platform
- **Carbon Collective**: https://github.com/VltrnOne/carbon-collective
- **VLTRN Council**: L5-BLACK Clearance Required

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Operational Intelligence, Simplified.
Part of VLTRN Council - Carbon Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
