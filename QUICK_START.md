# Carbon6 Platform - Quick Start Guide

## Install (30 seconds)

```bash
curl -sSL https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/remote-install.sh | bash
```

## Setup (1 minute)

```bash
# Initialize your profile
carbon init --name "Your Name"
```

## Start Platform (10 seconds)

```bash
cd ~/Carbon6
bun run dev
```

Visit: http://localhost:5173

## Track Your Work (5 seconds)

```bash
cd ~/your-project
carbon track
carbon watch  # Auto-sync every 30 seconds
```

---

## That's It! 🎉

Your work now syncs to: `~/carbon-collective/projects/your-name/`

---

## Commands Cheat Sheet

```bash
# Profile
carbon init --name "Name"     # First-time setup
carbon status                 # View profile info

# Projects
carbon track                  # Start tracking current dir
carbon list                   # List all tracked projects
carbon untrack               # Stop tracking

# Syncing
carbon sync                  # Sync now
carbon watch                 # Auto-sync (Ctrl+C to stop)

# Platform
cd ~/Carbon6 && bun run dev  # Start website
bun run build                # Build for production
```

---

## Tier System

| Tier | Badge | Split | Focus |
|------|-------|-------|-------|
| Carbon | [C] | 50/50 | Execute, learn, prove |
| Carbon[6] | [C6] | 65/35 | Lead, mentor, build |
| Black Ops | [6] | 80/20 | Govern, innovate |

---

**Pressure Creates.**
