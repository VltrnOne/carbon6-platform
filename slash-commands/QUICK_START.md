# Slash Commands - Quick Start

Get started with VLTRN Council slash commands in under 5 minutes.

---

## Installation

### Option 1: Global CLI (Recommended)
```bash
cd /Users/Morpheous/carbon6-platform/slash-commands
npm install
npm link

# Verify
slash --version
```

### Option 2: OiS Plugin
```bash
cd /Users/Morpheous/carbon6-platform/slash-commands
npm install
ois plugins install slash-commands

# Verify
ois plugins list
```

---

## Basic Usage

### Direct Execution
```bash
# Invoke agent directly
slash /genesis "Analyze my development workflow"

# Or use the exec command
slash exec /genesis "Analyze my development workflow"
```

### List Commands
```bash
# List all commands
slash list

# Filter by tier
slash list --tier tier1

# Search commands
slash search "financial"
```

### Get Command Info
```bash
# Get detailed info about a command
slash info aurum

# Get info about sub-agent
slash info aurum.analyst
```

### Search
```bash
# Search for commands
slash search deploy
slash search security
slash search analytics
```

### Statistics
```bash
# View system stats
slash stats
```

---

## Common Commands

### Tier 0: Divine Orchestrator
```bash
/genesis <task>                    # Supreme intelligence routing
/genesis-omega <strategic-task>    # Strategic analysis
```

### Tier 1: Council Core
```bash
/sovereign <strategic-decision>    # Executive strategy
/mnemos <knowledge-query>          # Memory & knowledge
/aegis <security-task>             # Security guardian
/praxis <execution-task>           # Operations director
/trust <compliance-task>           # Trust & compliance
```

### Tier 2: Domain Specialists
```bash
/aurum <finance-task>              # Finance & treasury
/techne <development-task>         # Technology & development
/sophia <research-task>            # Research & intelligence
/melodia <creative-task>           # Creative & media
/mercator <marketing-task>         # Marketing & growth
/datum <analytics-task>            # Data & analytics
```

---

## Sub-Agent Commands

Access specialized sub-agents using dot notation:

```bash
# Financial sub-agents
/aurum.controller <task>           # Bookkeeping, GAAP
/aurum.analyst <task>              # Variance, forecasting
/aurum.tax <task>                  # Tax compliance

# Development sub-agents
/techne.architect <task>           # System design
/techne.frontend <task>            # UI/UX implementation
/techne.backend <task>             # API, database
/techne.blockchain <task>          # Smart contracts

# Creative sub-agents
/melodia.content <task>            # Copy, scripts
/melodia.video <task>              # Video production
/melodia.audio <task>              # Music, podcasts
```

---

## Workflow Commands

Execute pre-built enterprise workflows:

```bash
# Financial workflows
/workflow.month-end-close          # Complete month-end process
/workflow.variance-analysis        # Budget vs actuals
/workflow.cash-flow-projection     # Forecast cash

# Development workflows
/workflow.full-stack-build         # Complete app build
/workflow.smart-contract-deploy    # Deploy contracts
/workflow.security-audit           # Security audit

# Marketing workflows
/workflow.campaign-launch          # Launch campaign
/workflow.ab-test-analysis         # A/B test analysis
/workflow.seo-optimization         # SEO optimization
```

---

## NVIDIA Backend Commands

Access GPU-accelerated capabilities:

```bash
/nvidia.nim <model> <task>         # LLM inference
/nvidia.riva.asr <audio>           # Speech-to-text
/nvidia.riva.tts <text>            # Text-to-speech
/nvidia.nemo.train <config>        # Train custom model
/nvidia.morpheus <data>            # Threat/fraud detection
/nvidia.cuopt <problem>            # Portfolio/route optimization
```

---

## LLM Router Commands

Route tasks to specific LLM providers:

```bash
/llm.claude <task>                 # Use Claude (Anthropic)
/llm.gemini <task>                 # Use Gemini (Google)
/llm.codex <task>                  # Use Codex (OpenAI)
/llm.perplexity <task>             # Use Perplexity
```

---

## Aliases

Use short aliases for common commands:

```bash
# Financial aliases
/finance → /aurum
/accounting → /aurum.controller
/fpa → /aurum.analyst
/tax → /aurum.tax

# Development aliases
/dev → /techne
/code → /techne.architect
/frontend → /techne.frontend
/backend → /techne.backend
/deploy → /techne.devops

# Creative aliases
/creative → /melodia
/content → /melodia.content
/video → /melodia.video
/design → /melodia.visual

# Marketing aliases
/marketing → /mercator
/growth → /mercator.growth
/social → /mercator.social

# Research aliases
/research → /sophia
/intel → /sophia.intel
/dd → /sophia.diligence
```

---

## Examples

### Example 1: Financial Analysis
```bash
slash /aurum "Analyze Q4 P&L and identify cost-saving opportunities"

# Or use sub-agent
slash /aurum.analyst "Variance analysis for marketing spend vs budget"

# Or use workflow
slash /workflow.variance-analysis
```

### Example 2: Product Development
```bash
slash /techne "Build authentication system with OAuth2"

# Specific sub-agent
slash /techne.backend "Design REST API for user management"

# Workflow
slash /workflow.full-stack-build
```

### Example 3: Marketing Campaign
```bash
slash /mercator "Create Q1 growth strategy"

# Sub-agent
slash /mercator.growth "Setup Google Ads campaign with $10k budget"

# Workflow
slash /workflow.campaign-launch
```

### Example 4: Security Audit
```bash
slash /aegis "Complete security audit of production environment"

# Specific testing
slash /aegis.penetrator "Penetration test on web application"

# Workflow
slash /workflow.security-audit
```

---

## Help System

### General Help
```bash
slash help
```

### Tier-Specific Help
```bash
slash help tier0        # L5-BLACK commands
slash help tier1        # L4-RESTRICTED commands
slash help tier2        # L3-CONFIDENTIAL commands
slash help tier3        # L2-INTERNAL commands
slash help tier4        # L1-PUBLIC commands
```

### Topic Help
```bash
slash help workflows    # Available workflows
slash help nvidia       # NVIDIA backends
slash help llm          # LLM providers
```

---

## Command Discovery

### List by Tier
```bash
slash list --tier tier1
slash list --tier tier2
```

### List by Domain
```bash
slash list --domain finance
slash list --domain technology
slash list --domain marketing
```

### Search
```bash
slash search deploy
slash search security
slash search analytics
```

---

## Configuration

Create a config file at `~/.slash-commands.json`:

```json
{
  "commandPrefix": "/",
  "enableAliases": true,
  "enableAutoRouting": true,
  "defaultLLM": "claude-opus-4-5",
  "enableNVIDIA": true,
  "logLevel": "info"
}
```

---

## Integration with OiS

Use slash commands within OiS:

```bash
# Install as OiS plugin
ois plugins install slash-commands

# Use commands
ois /aurum "Analyze financials"
ois /techne "Deploy to production"
```

---

## Troubleshooting

### "Command not found"
```bash
# Re-link the CLI
cd /Users/Morpheous/carbon6-platform/slash-commands
npm link

# Or reinstall
npm install
```

### View Available Commands
```bash
slash list              # List all commands
slash search <query>    # Search for specific commands
```

### Check System Status
```bash
slash stats             # View system statistics
```

---

## Next Steps

1. **Explore Commands**: `slash list` to see all available commands
2. **Try Basic Commands**: Start with `/genesis`, `/aurum`, `/techne`
3. **Use Sub-Agents**: Explore specialized sub-agents
4. **Execute Workflows**: Try pre-built workflows
5. **Read Full Docs**: [README.md](README.md)

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
462 Commands Ready
Direct Access to VLTRN Council
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
