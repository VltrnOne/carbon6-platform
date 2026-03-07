#!/usr/bin/env python3
"""Carbon6 Platform TUI - Department-Based Operational Intelligence Dashboard"""

import subprocess
import json
import os
import re
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Label, Button, RichLog, Input, ListView, ListItem,
)
from textual.binding import Binding
from textual.screen import Screen
from textual.message import Message
from textual import work, on
from textual.reactive import reactive

from .departments import DEPARTMENTS

# All OiS core plugins (cross-department)
OIS_PLUGINS = [
    {"name": "ois-carbon", "desc": "Carbon6 SDK integration", "installed": True},
    {"name": "ois-council", "desc": "VLTRN Council agent access (462 agents)", "installed": True},
    {"name": "ois-nvidia", "desc": "GPU acceleration toolkit (RAPIDS, NeMo, Triton)", "installed": False},
    {"name": "ois-flow", "desc": "Workflow automation engine", "installed": True},
    {"name": "ois-intel", "desc": "Intelligence gathering & analysis", "installed": False},
    {"name": "ois-secure", "desc": "Security & AES-256-GCM encryption", "installed": True},
]

SYSTEM_TOOLS = [
    {"name": "gh-auto", "desc": "GitHub automation suite (sync, CI, PRs, issues)", "installed": True},
    {"name": "memory-system", "desc": "SQLite + Redis persistent memory", "installed": True},
    {"name": "sdk-builder", "desc": "SDK & installer packaging tool", "installed": True},
    {"name": "slash-commands", "desc": "Slash command system (462 commands)", "installed": True},
    {"name": "render-api", "desc": "Render service management", "installed": True},
    {"name": "hostinger-api", "desc": "Hostinger VPS & DNS management", "installed": True},
    {"name": "redis-cache", "desc": "Redis caching layer", "installed": True},
    {"name": "cron-manager", "desc": "Scheduled task management", "installed": True},
    {"name": "n8n-workflows", "desc": "Visual workflow automation (VPS1)", "installed": True},
]


def run_cmd(cmd: str, timeout: int = 15) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


# ──────────────────────────────────────────────
# Department config persistence
# ──────────────────────────────────────────────
DEPT_CONFIG = Path.home() / ".ois" / "departments.json"


def load_dept_config() -> dict:
    if DEPT_CONFIG.exists():
        with open(DEPT_CONFIG) as f:
            return json.load(f)
    return {}


def save_dept_config(data: dict):
    DEPT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(DEPT_CONFIG, "w") as f:
        json.dump(data, f, indent=2)


def is_tool_installed(dept_key: str, tool_name: str) -> bool:
    config = load_dept_config()
    installed = config.get(dept_key, {}).get("installed_tools", [])
    # Also check defaults from DEPARTMENTS
    dept = DEPARTMENTS[dept_key]
    for t in dept["tools"]:
        if t["name"] == tool_name and t["installed"]:
            return True
    return tool_name in installed


def toggle_tool(dept_key: str, tool_name: str, install: bool):
    config = load_dept_config()
    if dept_key not in config:
        config[dept_key] = {"installed_tools": []}
    tools = config[dept_key].setdefault("installed_tools", [])
    if install and tool_name not in tools:
        tools.append(tool_name)
    elif not install and tool_name in tools:
        tools.remove(tool_name)
    save_dept_config(config)


# ──────────────────────────────────────────────
# Home Screen
# ──────────────────────────────────────────────
class HomeScreen(Screen):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("t", "open_tools", "Tools"),
        Binding("h", "open_help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(
                "\n[bold cyan]CARBON[6][/]  [dim]Operational Intelligence System[/]\n"
                "[dim]v1.0.0 | L5-BLACK | Pressure Creates.[/]\n",
                id="home-banner",
            ),
            Static("[bold]SELECT DEPARTMENT[/]\n", id="home-subtitle"),
            Container(*self._dept_buttons(), id="dept-grid"),
            Horizontal(
                Button("[bold cyan]>> Tools & Plugins[/]\n[dim]Manage all platform tools[/]", id="nav-tools", classes="nav-btn"),
                Button("[bold yellow]>> Help & Reference[/]\n[dim]Keybindings, commands, about[/]", id="nav-help", classes="nav-btn"),
                id="nav-bar",
            ),
            Static("", id="home-status"),
            id="home-container",
        )
        yield Footer()

    def _dept_buttons(self):
        buttons = []
        for key, dept in DEPARTMENTS.items():
            installed_count = sum(1 for t in dept["tools"] if t["installed"] or is_tool_installed(key, t["name"]))
            total = len(dept["tools"])
            label = (
                f"[bold {dept['color']}]{dept['icon']} {dept['name']}[/]\n"
                f"[dim]{dept['tagline']}[/]\n"
                f"[dim]{dept['lead_agent']}[/]  |  "
                f"[dim]{len(dept['agents'])} agents[/]  |  "
                f"[dim]{installed_count}/{total} tools[/]"
            )
            buttons.append(Button(label, id=f"dept-{key}", classes="dept-btn"))
        return buttons

    @on(Button.Pressed)
    def on_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id:
            return
        if btn_id.startswith("dept-"):
            dept_key = btn_id.replace("dept-", "")
            self.app.push_screen(DepartmentScreen(dept_key))
        elif btn_id == "nav-tools":
            self.app.push_screen(ToolsScreen())
        elif btn_id == "nav-help":
            self.app.push_screen(HelpScreen())

    def on_mount(self) -> None:
        self.refresh_status()

    @work(thread=True)
    def refresh_status(self) -> None:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        redis_ok = run_cmd("redis-cli ping 2>/dev/null") == "PONG"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = (
            f"\n[dim]CPU: {cpu:.0f}% | "
            f"RAM: {mem.percent:.0f}% ({mem.used // (1024**3)}/{mem.total // (1024**3)}GB) | "
            f"Redis: {'UP' if redis_ok else 'DOWN'} | "
            f"{now}[/]"
        )
        self.app.call_from_thread(self.query_one("#home-status").update, status)

    def action_refresh(self) -> None:
        self.refresh_status()

    def action_open_tools(self) -> None:
        self.app.push_screen(ToolsScreen())

    def action_open_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ──────────────────────────────────────────────
# Department Screen
# ──────────────────────────────────────────────
class DepartmentScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
        Binding("1", "show_agents", "Agents"),
        Binding("2", "show_tools", "Tools"),
        Binding("3", "show_workflows", "Workflows"),
        Binding("4", "focus_terminal", "Terminal"),
    ]

    def __init__(self, dept_key: str):
        super().__init__()
        self.dept_key = dept_key
        self.dept = DEPARTMENTS[dept_key]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            # Department header
            Static(self._header(), id="dept-header"),
            # Main layout: left panel (agents/tools/workflows) + right panel (terminal)
            Horizontal(
                # Left: info panels
                Vertical(
                    Container(
                        Static(self._agents_panel(), id="agents-panel"),
                        id="agents-container",
                        classes="info-panel",
                    ),
                    Container(
                        Static(self._tools_panel(), id="tools-panel"),
                        id="tools-container",
                        classes="info-panel",
                    ),
                    Container(
                        Static(self._workflows_panel(), id="workflows-panel"),
                        id="workflows-container",
                        classes="info-panel",
                    ),
                    id="left-col",
                ),
                # Right: terminal
                Vertical(
                    Static(f"[bold {self.dept['color']}]Terminal[/]  [dim]Run commands in this department[/]", id="term-title"),
                    Container(
                        *self._quick_cmd_buttons(),
                        id="quick-cmds",
                    ),
                    Horizontal(
                        Label(f"[bold {self.dept['color']}]$[/] ", id="prompt"),
                        Input(placeholder="enter command...", id="cmd-input"),
                        id="cmd-bar",
                    ),
                    ScrollableContainer(
                        RichLog(id="cmd-output", highlight=True, markup=True),
                        id="cmd-scroll",
                    ),
                    id="right-col",
                ),
                id="main-layout",
            ),
            id="dept-container",
        )
        yield Footer()

    def _header(self) -> str:
        d = self.dept
        installed = sum(1 for t in d["tools"] if t["installed"] or is_tool_installed(self.dept_key, t["name"]))
        return (
            f"\n[bold {d['color']}]{d['icon']} {d['name'].upper()} DEPARTMENT[/]  "
            f"[dim]{d['tagline']}[/]\n"
            f"[dim]Lead: {d['lead_agent']} - {d['lead_desc']}  |  "
            f"{len(d['agents'])} agents  |  {installed}/{len(d['tools'])} tools active[/]\n"
        )

    def _agents_panel(self) -> str:
        lines = [f"[bold]Agents[/]  [dim](press 1)[/]\n"]
        for name, role, desc in self.dept["agents"]:
            if role == "Lead":
                lines.append(f"  [bold {self.dept['color']}]{name:<22}[/] [yellow]LEAD[/]  {desc}")
            elif role == "Support":
                lines.append(f"  [{self.dept['color']}]{name:<22}[/] [dim]SUPP[/]  {desc}")
            else:
                lines.append(f"  [dim]{name:<22}[/] [dim] SUB[/]  {desc}")
        return "\n".join(lines)

    def _tools_panel(self) -> str:
        lines = [f"[bold]Tools & Plugins[/]  [dim](press 2 | click to install/remove)[/]\n"]
        for t in self.dept["tools"]:
            installed = t["installed"] or is_tool_installed(self.dept_key, t["name"])
            status = f"[green]ON [/]" if installed else f"[dim]OFF[/]"
            icon = "[green]+[/]" if installed else "[dim]o[/]"
            lines.append(f"  {icon} {t['name']:<20} {status}  [dim]{t['desc']}[/]")
        return "\n".join(lines)

    def _workflows_panel(self) -> str:
        lines = [f"[bold]Workflows[/]  [dim](press 3)[/]\n"]
        for wf in self.dept["workflows"]:
            lines.append(f"  [dim]>[/] {wf}")
        return "\n".join(lines)

    def _quick_cmd_buttons(self):
        buttons = []
        for cmd, label in self.dept.get("quick_cmds", []):
            safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', label)
            buttons.append(Button(f"[dim]{label}[/]", id=f"qcmd-{safe_id}", classes="quick-btn"))
        # Tool management buttons
        buttons.append(Button("[bold green]+ Install Tool[/]", id="install-tool-btn", classes="quick-btn"))
        buttons.append(Button("[bold red]- Remove Tool[/]", id="remove-tool-btn", classes="quick-btn"))
        return buttons

    @on(Button.Pressed)
    def on_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id:
            return

        log = self.query_one("#cmd-output", RichLog)

        if btn_id.startswith("qcmd-"):
            # Find the matching quick command by sanitized label
            sanitized_id = btn_id.replace("qcmd-", "")
            for cmd, lbl in self.dept.get("quick_cmds", []):
                if re.sub(r'[^a-zA-Z0-9_-]', '-', lbl) == sanitized_id:
                    log.write(f"[bold {self.dept['color']}]$ {cmd}[/]")
                    self._run_cmd(cmd, log)
                    break

        elif btn_id == "install-tool-btn":
            # Show installable tools
            uninstalled = [
                t for t in self.dept["tools"]
                if not t["installed"] and not is_tool_installed(self.dept_key, t["name"])
            ]
            if not uninstalled:
                log.write(f"[green]All tools already installed![/]")
            else:
                log.write(f"[bold]Available tools to install:[/]")
                for i, t in enumerate(uninstalled, 1):
                    log.write(f"  {i}. {t['name']} - {t['desc']}")
                log.write(f"[dim]Type: install <name> (e.g. install {uninstalled[0]['name']})[/]")
                log.write("")

        elif btn_id == "remove-tool-btn":
            installed = [
                t for t in self.dept["tools"]
                if t["installed"] or is_tool_installed(self.dept_key, t["name"])
            ]
            if not installed:
                log.write(f"[yellow]No tools installed.[/]")
            else:
                log.write(f"[bold]Installed tools:[/]")
                for i, t in enumerate(installed, 1):
                    log.write(f"  {i}. {t['name']} - {t['desc']}")
                log.write(f"[dim]Type: remove <name> (e.g. remove {installed[0]['name']})[/]")
                log.write("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return
        event.input.value = ""
        log = self.query_one("#cmd-output", RichLog)

        # Handle install/remove commands
        if cmd.startswith("install "):
            tool_name = cmd.split(" ", 1)[1].strip()
            tool_exists = any(t["name"] == tool_name for t in self.dept["tools"])
            if tool_exists:
                toggle_tool(self.dept_key, tool_name, True)
                log.write(f"[green]+ Installed {tool_name}[/]")
                self._refresh_panels()
            else:
                log.write(f"[red]Tool '{tool_name}' not found in {self.dept['name']} department[/]")
            log.write("")
            return

        if cmd.startswith("remove "):
            tool_name = cmd.split(" ", 1)[1].strip()
            tool_exists = any(t["name"] == tool_name for t in self.dept["tools"])
            if tool_exists:
                toggle_tool(self.dept_key, tool_name, False)
                log.write(f"[red]- Removed {tool_name}[/]")
                self._refresh_panels()
            else:
                log.write(f"[red]Tool '{tool_name}' not found[/]")
            log.write("")
            return

        # Regular shell command
        log.write(f"[bold {self.dept['color']}]$ {cmd}[/]")
        self._run_cmd(cmd, log)

    @work(thread=True)
    def _run_cmd(self, cmd: str, log: RichLog) -> None:
        output = strip_ansi(run_cmd(cmd, timeout=30))
        self.app.call_from_thread(log.write, output if output else "[dim]No output[/]")
        self.app.call_from_thread(log.write, "")

    def _refresh_panels(self) -> None:
        self.query_one("#tools-panel").update(self._tools_panel())
        self.query_one("#dept-header").update(self._header())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_show_agents(self) -> None:
        log = self.query_one("#cmd-output", RichLog)
        log.write(self._agents_panel())
        log.write("")

    def action_show_tools(self) -> None:
        log = self.query_one("#cmd-output", RichLog)
        log.write(self._tools_panel())
        log.write("")

    def action_show_workflows(self) -> None:
        log = self.query_one("#cmd-output", RichLog)
        log.write(self._workflows_panel())
        log.write("")

    def action_focus_terminal(self) -> None:
        self.query_one("#cmd-input").focus()


# ──────────────────────────────────────────────
# Tools Screen
# ──────────────────────────────────────────────
class ToolsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(
                "\n[bold cyan]TOOLS & PLUGINS[/]  [dim]Manage all platform tools[/]\n",
                id="tools-banner",
            ),
            Horizontal(
                # Left: OiS plugins + system tools
                ScrollableContainer(
                    Static(self._ois_panel(), id="ois-tools-panel"),
                    Static(self._system_panel(), id="system-tools-panel"),
                    id="tools-left",
                ),
                # Right: per-department tools + terminal
                Vertical(
                    ScrollableContainer(
                        Static(self._dept_tools_panel(), id="dept-tools-panel"),
                        id="tools-right-scroll",
                    ),
                    Horizontal(
                        Label("[bold cyan]$[/] ", id="tools-prompt"),
                        Input(placeholder="install <tool> | remove <tool> | search <query>", id="tools-cmd-input"),
                        id="tools-cmd-bar",
                    ),
                    ScrollableContainer(
                        RichLog(id="tools-cmd-output", highlight=True, markup=True),
                        id="tools-cmd-scroll",
                    ),
                    id="tools-right",
                ),
                id="tools-layout",
            ),
            id="tools-container",
        )
        yield Footer()

    def _ois_panel(self) -> str:
        lines = ["[bold yellow]OiS Core Plugins[/]\n"]
        for p in OIS_PLUGINS:
            icon = "[green]+[/]" if p["installed"] else "[dim]o[/]"
            status = "[green]ON [/]" if p["installed"] else "[dim]OFF[/]"
            lines.append(f"  {icon} {p['name']:<20} {status}  [dim]{p['desc']}[/]")
        lines.append("")
        return "\n".join(lines)

    def _system_panel(self) -> str:
        lines = ["[bold cyan]System Tools[/]\n"]
        for t in SYSTEM_TOOLS:
            icon = "[green]+[/]" if t["installed"] else "[dim]o[/]"
            status = "[green]ON [/]" if t["installed"] else "[dim]OFF[/]"
            lines.append(f"  {icon} {t['name']:<20} {status}  [dim]{t['desc']}[/]")
        lines.append("")
        return "\n".join(lines)

    def _dept_tools_panel(self) -> str:
        lines = ["[bold magenta]Department Tools[/]  [dim](by department)[/]\n"]
        for key, dept in DEPARTMENTS.items():
            installed = sum(1 for t in dept["tools"] if t["installed"] or is_tool_installed(key, t["name"]))
            total = len(dept["tools"])
            lines.append(f"  [bold {dept['color']}]{dept['name']}[/]  [dim]{installed}/{total} active[/]")
            for t in dept["tools"]:
                is_on = t["installed"] or is_tool_installed(key, t["name"])
                icon = "[green]+[/]" if is_on else "[dim]o[/]"
                status = "[green]ON [/]" if is_on else "[dim]OFF[/]"
                lines.append(f"    {icon} {t['name']:<20} {status}  [dim]{t['desc']}[/]")
            lines.append("")
        return "\n".join(lines)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return
        event.input.value = ""
        log = self.query_one("#tools-cmd-output", RichLog)

        if cmd.startswith("install "):
            tool_name = cmd.split(" ", 1)[1].strip()
            found = False
            for key, dept in DEPARTMENTS.items():
                for t in dept["tools"]:
                    if t["name"] == tool_name:
                        toggle_tool(key, tool_name, True)
                        log.write(f"[green]+ Installed {tool_name} in {dept['name']}[/]")
                        found = True
                        break
                if found:
                    break
            if not found:
                log.write(f"[red]Tool '{tool_name}' not found in any department[/]")
            else:
                self.query_one("#dept-tools-panel").update(self._dept_tools_panel())
            log.write("")
            return

        if cmd.startswith("remove "):
            tool_name = cmd.split(" ", 1)[1].strip()
            found = False
            for key, dept in DEPARTMENTS.items():
                for t in dept["tools"]:
                    if t["name"] == tool_name:
                        toggle_tool(key, tool_name, False)
                        log.write(f"[red]- Removed {tool_name} from {dept['name']}[/]")
                        found = True
                        break
                if found:
                    break
            if not found:
                log.write(f"[red]Tool '{tool_name}' not found[/]")
            else:
                self.query_one("#dept-tools-panel").update(self._dept_tools_panel())
            log.write("")
            return

        if cmd.startswith("search "):
            query = cmd.split(" ", 1)[1].strip().lower()
            log.write(f"[bold]Search: {query}[/]")
            results = []
            for p in OIS_PLUGINS + SYSTEM_TOOLS:
                if query in p["name"].lower() or query in p["desc"].lower():
                    results.append(("system", p))
            for key, dept in DEPARTMENTS.items():
                for t in dept["tools"]:
                    if query in t["name"].lower() or query in t["desc"].lower():
                        results.append((dept["name"], t))
            if results:
                for source, t in results:
                    icon = "[green]+[/]" if t.get("installed") else "[dim]o[/]"
                    log.write(f"  {icon} {t['name']:<20} [{source}]  [dim]{t['desc']}[/]")
            else:
                log.write(f"  [dim]No tools matching '{query}'[/]")
            log.write("")
            return

        # Shell command fallback
        log.write(f"[bold cyan]$ {cmd}[/]")
        self._run_cmd(cmd, log)

    @work(thread=True)
    def _run_cmd(self, cmd: str, log: RichLog) -> None:
        output = strip_ansi(run_cmd(cmd, timeout=30))
        self.app.call_from_thread(log.write, output if output else "[dim]No output[/]")
        self.app.call_from_thread(log.write, "")

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ──────────────────────────────────────────────
# Help Screen
# ──────────────────────────────────────────────
class HelpScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static(self._help_content(), id="help-content"),
            id="help-scroll",
        )
        yield Footer()

    def _help_content(self) -> str:
        return (
            "\n[bold cyan]CARBON[6] TUI HELP[/]  [dim]v1.0.0[/]\n"
            "\n"
            "[bold]HOME SCREEN[/]\n"
            "  Click a department button to enter it\n"
            "  Click [bold]Tools[/] to manage all platform tools\n"
            "  Click [bold]Help[/] to view this screen\n"
            "\n"
            "[bold yellow]GLOBAL KEYBINDINGS[/]\n"
            "  [cyan]q[/]          Quit the application\n"
            "  [cyan]r[/]          Refresh current screen\n"
            "  [cyan]b / Esc[/]    Go back to previous screen\n"
            "\n"
            "[bold yellow]DEPARTMENT KEYBINDINGS[/]\n"
            "  [cyan]1[/]          Show agents in terminal\n"
            "  [cyan]2[/]          Show tools in terminal\n"
            "  [cyan]3[/]          Show workflows in terminal\n"
            "  [cyan]4[/]          Focus terminal input\n"
            "\n"
            "[bold yellow]TERMINAL COMMANDS[/]\n"
            "  [cyan]install <tool>[/]      Install a department tool\n"
            "  [cyan]remove <tool>[/]       Remove a department tool\n"
            "  [cyan]search <query>[/]      Search all tools (Tools screen)\n"
            "  [cyan]<any command>[/]       Run shell command (gh-auto, ois, etc.)\n"
            "\n"
            "[bold yellow]QUICK COMMANDS[/]\n"
            "  [cyan]gh-auto status[/]      All repo statuses\n"
            "  [cyan]gh-auto sync[/]        Sync all repos\n"
            "  [cyan]gh-auto ci[/]          CI/CD check results\n"
            "  [cyan]gh-auto dash[/]        Full dashboard\n"
            "  [cyan]gh-auto render-status[/]  Render services\n"
            "  [cyan]gh-auto hst-status[/]  Hostinger VPS status\n"
            "  [cyan]ois status[/]          OiS system health\n"
            "  [cyan]ois agents[/]          List Council agents\n"
            "  [cyan]ois plugins[/]         List OiS plugins\n"
            "\n"
            "[bold yellow]MEMORY SYSTEM[/]\n"
            "  [cyan]python3 /root/memory-system/scripts/memory.py list[/]\n"
            "  [cyan]python3 /root/memory-system/scripts/memory.py search \"query\"[/]\n"
            "  [cyan]python3 /root/memory-system/scripts/memory.py stats[/]\n"
            "\n"
            "[bold]ARCHITECTURE[/]\n"
            "  [bold cyan]462[/] slash commands across [bold]5 tiers[/] (L1-L5)\n"
            "  [bold cyan]7[/] departments with dedicated agents & tools\n"
            "  [bold cyan]6[/] OiS core plugins\n"
            "  [bold cyan]9[/] system tools\n"
            "\n"
            "[bold]AGENT TIERS[/]\n"
            "  [red]L5-BLACK[/]        GENESIS (Divine Orchestrator)\n"
            "  [yellow]L4-RESTRICTED[/]   SOVEREIGN, MNEMOS, AEGIS, PRAXIS, TRUST\n"
            "  [cyan]L3-CONFIDENTIAL[/] TECHNE, AURUM, SOPHIA, MERCATOR, MELODIA, DATUM + more\n"
            "  [dim]L2-INTERNAL[/]     CALAMUS, CHRONOS, BENEFACTOR, HERMES, LOGOS\n"
            "  [dim]L1-PUBLIC[/]       SCOUT, FORMA, NUNTIUS, VERBUM\n"
            "\n"
            "[bold]CARBON TIER SYSTEM[/]\n"
            "  [dim][C][/]   Carbon       50/50 split   Execute, learn, prove\n"
            "  [cyan][C6][/]  Carbon[6]    65/35 split   Lead, mentor, build\n"
            "  [bold][6][/]   Black Ops    80/20 split   Govern, innovate, impossible\n"
            "\n"
            "[bold]INFRASTRUCTURE[/]\n"
            "  GitHub:    [green]VltrnOne[/] | 29 repos | 10 cloned & tracked\n"
            "  Render:    18 services (16 live, 2 suspended)\n"
            "  Hostinger: 3 VPS | 10 CPUs | 40GB RAM | 500GB disk\n"
            "  Domain:    vltrn.cloud (active)\n"
            "\n"
            "[dim]Pressure Creates. | VLTRN Council - Carbon Domain[/]\n"
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ──────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────
class Carbon6App(App):
    """Carbon6 Platform TUI - Department Dashboard"""

    CSS = """
    Screen {
        background: $surface;
    }

    #home-container {
        padding: 1 2;
    }

    #home-banner {
        text-align: center;
        padding: 1 0;
    }

    #home-subtitle {
        text-align: center;
    }

    #home-status {
        text-align: center;
        dock: bottom;
        height: 3;
    }

    #dept-grid {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
        padding: 0 2;
        height: auto;
    }

    .dept-btn {
        height: 7;
        content-align: center middle;
        text-align: center;
        border: solid $primary-darken-2;
    }

    .dept-btn:hover {
        border: solid $accent;
        background: $primary-background;
    }

    .dept-btn:focus {
        border: solid $accent;
    }

    /* Department screen */
    #dept-container {
        padding: 0 1;
    }

    #dept-header {
        height: auto;
        padding: 0 1;
    }

    #main-layout {
        height: 1fr;
    }

    #left-col {
        width: 50%;
        height: 1fr;
        overflow-y: auto;
    }

    #right-col {
        width: 50%;
        height: 1fr;
        border-left: solid $primary-darken-2;
        padding: 0 1;
    }

    .info-panel {
        height: auto;
        padding: 1 1;
        border-bottom: solid $primary-darken-3;
    }

    #term-title {
        height: 2;
        padding: 0 0;
    }

    #quick-cmds {
        layout: horizontal;
        height: auto;
        padding: 0 0 1 0;
    }

    .quick-btn {
        height: 3;
        min-width: 16;
        margin: 0 1 0 0;
    }

    #cmd-bar {
        height: 3;
        padding: 0 0;
        dock: top;
    }

    #prompt {
        width: 3;
        padding: 1 0;
    }

    #cmd-input {
        width: 1fr;
    }

    #cmd-scroll {
        height: 1fr;
    }

    #cmd-output {
        height: auto;
        min-height: 5;
    }

    /* Nav bar (Tools / Help buttons on home) */
    #nav-bar {
        height: auto;
        padding: 1 2;
        align: center middle;
    }

    .nav-btn {
        height: 5;
        min-width: 30;
        margin: 0 2;
        content-align: center middle;
        text-align: center;
        border: solid $accent;
    }

    .nav-btn:hover {
        background: $primary-background;
    }

    /* Tools screen */
    #tools-container {
        padding: 1 2;
    }

    #tools-banner {
        text-align: center;
        height: auto;
    }

    #tools-layout {
        height: 1fr;
    }

    #tools-left {
        width: 45%;
        height: 1fr;
        padding: 0 1;
    }

    #tools-right {
        width: 55%;
        height: 1fr;
        border-left: solid $primary-darken-2;
        padding: 0 1;
    }

    #tools-right-scroll {
        height: 1fr;
    }

    #tools-cmd-bar {
        height: 3;
        dock: bottom;
    }

    #tools-prompt {
        width: 3;
        padding: 1 0;
    }

    #tools-cmd-input {
        width: 1fr;
    }

    #tools-cmd-scroll {
        height: 10;
    }

    #tools-cmd-output {
        height: auto;
        min-height: 5;
    }

    /* Help screen */
    #help-scroll {
        padding: 1 4;
    }

    #help-content {
        height: auto;
    }
    """

    TITLE = "CARBON[6]"
    SUB_TITLE = "Operational Intelligence System"

    SCREENS = {"home": HomeScreen}

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def main():
    app = Carbon6App()
    app.run()


if __name__ == "__main__":
    main()
