#!/usr/bin/env python3
"""SENTINEL - Carbon6 Security Department Lead Agent.

Usage:
    sentinel status              Show security dashboard
    sentinel scan                Run full threat detection scan
    sentinel threats [--open]    List detected threats
    sentinel logs [ssh|nginx|f2b] Analyze logs
    sentinel compliance          Run compliance check
    sentinel vault status        Vault health
    sentinel vault verify        Verify vault integrity
    sentinel vault secrets       List secret names
    sentinel vault rotation      Secret rotation status
    sentinel vault rotate <name> Rotate a secret (prompts for new value)
    sentinel incidents [--open]  List incidents
    sentinel incident <id>       View incident details
    sentinel events [--type T]   List security events
    sentinel report              Full security report
    sentinel worker              Start background worker daemon
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security_department.engine.database import SecurityDB
from security_department.engine.threat_detector import ThreatDetector
from security_department.engine.vault_manager import VaultManager
from security_department.engine.log_analyzer import LogAnalyzer
from security_department.engine.compliance import ComplianceEngine
from security_department.engine.incident_response import IncidentResponder


class Sentinel:
    """SENTINEL Lead Agent - Security operations CLI."""

    def __init__(self):
        self.db = SecurityDB()
        self.threats = ThreatDetector(db=self.db)
        self.vault = VaultManager(db=self.db)
        self.logs = LogAnalyzer(db=self.db)
        self.compliance = ComplianceEngine(db=self.db)
        self.incidents = IncidentResponder(db=self.db)

    def handle_command(self, args: list) -> dict:
        if not args:
            return self._cmd_status()

        cmd = args[0]
        handlers = {
            "status": self._cmd_status,
            "scan": self._cmd_scan,
            "threats": self._cmd_threats,
            "logs": self._cmd_logs,
            "compliance": self._cmd_compliance,
            "vault": self._cmd_vault,
            "incidents": self._cmd_incidents,
            "incident": self._cmd_incident,
            "events": self._cmd_events,
            "report": self._cmd_report,
            "worker": self._cmd_worker,
            "help": self._cmd_help,
        }

        handler = handlers.get(cmd, self._cmd_help)
        return handler(args[1:] if len(args) > 1 else [])

    def _cmd_status(self, args=None) -> dict:
        stats = self.db.stats()
        vault_st = self.vault.vault_status()
        log_summary = self.logs.get_summary()

        self._print_header("SENTINEL SECURITY DASHBOARD")
        print(f"  Open Threats:     {stats['open_threats']} "
              f"({'🔴 ' + str(stats['critical_threats']) + ' critical' if stats['critical_threats'] else '✅ none critical'})")
        print(f"  Open Incidents:   {stats['open_incidents']}")
        print(f"  Events (24h):     {stats['events_24h']}")
        print(f"  Overdue Rotations: {stats['overdue_secret_rotations']}")
        print(f"  Vault Secrets:    {vault_st['secret_count']}")
        print(f"  Vault OK:         {'✅' if vault_st['permissions_ok'] else '❌'}")
        print(f"  SSH Failed (log): {log_summary.get('ssh_failed_attempts', 0)}")
        print(f"  fail2ban Bans:    {log_summary.get('fail2ban_total_bans', 0)}")
        return stats

    def _cmd_scan(self, args=None) -> dict:
        self._print_header("THREAT SCAN")
        detected = self.threats.scan_all()
        if not detected:
            print("  ✅ No threats detected")
            return {"threats": 0}

        results = []
        for threat in detected:
            result = self.incidents.handle_threat(threat)
            results.append(result)
            icon = "🔴" if threat["severity"] == "critical" else "🟠" if threat["severity"] == "high" else "🟡"
            print(f"  {icon} [{threat['severity'].upper()}] {threat['description']}")
            if result.get("auto_resolved"):
                print(f"     → Auto-resolved via {result.get('playbook', 'N/A')}")
            else:
                print(f"     → Incident #{result.get('incident_id')} created")

        return {"threats": len(detected), "results": results}

    def _cmd_threats(self, args=None) -> dict:
        status = "open" if args and "--open" in args else None
        threats_list = self.db.get_threats(status=status)
        self._print_header(f"THREATS {'(open)' if status else '(all)'}")
        for t in threats_list:
            icon = "🔴" if t["severity"] == "critical" else "🟠" if t["severity"] == "high" else "🟡"
            print(f"  #{t['id']} {icon} [{t['status']}] {t['description'][:80]}")
        if not threats_list:
            print("  No threats found")
        return {"count": len(threats_list)}

    def _cmd_logs(self, args=None) -> dict:
        target = args[0] if args else "all"
        if target == "ssh":
            result = self.logs.analyze_ssh()
        elif target == "nginx":
            result = self.logs.analyze_nginx()
        elif target in ("f2b", "fail2ban"):
            result = self.logs.analyze_fail2ban()
        else:
            result = self.logs.analyze_all()

        self._print_header(f"LOG ANALYSIS ({target})")
        print(json.dumps(result, indent=2, default=str))
        return result

    def _cmd_compliance(self, args=None) -> dict:
        self._print_header("COMPLIANCE SCAN")
        result = self.compliance.run_all()
        print(f"\n  Score: {result['score']}% (Grade {result['grade']})")
        print(f"  Passed: {result['passed']}/{result['total']}\n")
        for category, checks in result["checks"].items():
            print(f"  [{category.upper()}]")
            for name, check in checks.items():
                icon = "✅" if check["status"] == "pass" else "❌" if check["status"] == "fail" else "⚠️"
                print(f"    {icon} {name}: {check['detail']}")
        return result

    def _cmd_vault(self, args=None) -> dict:
        if not args:
            return self._cmd_vault(["status"])

        subcmd = args[0]
        if subcmd == "status":
            status = self.vault.vault_status()
            self._print_header("VAULT STATUS")
            for k, v in status.items():
                print(f"  {k}: {v}")
            return status
        elif subcmd == "verify":
            result = self.vault.verify_integrity()
            self._print_header("VAULT INTEGRITY")
            print(f"  OK: {len(result['ok'])} secrets")
            if result["failed"]:
                print(f"  FAILED: {result['failed']}")
            return result
        elif subcmd == "secrets":
            secrets = self.vault.list_secrets()
            self._print_header("VAULT SECRETS (names only)")
            for s in secrets:
                print(f"  • {s}")
            return {"secrets": secrets}
        elif subcmd == "rotation":
            rot = self.vault.get_rotation_status()
            self._print_header("SECRET ROTATION STATUS")
            for s in rot.get("secrets", []):
                overdue = "⚠️ OVERDUE" if s["secret_name"] in [o["secret_name"] for o in rot.get("overdue", [])] else "✅"
                print(f"  {overdue} {s['secret_name']}: last={s.get('last_rotated', 'never')}")
            return rot
        elif subcmd == "rotate" and len(args) > 1:
            name = args[1]
            new_value = input(f"Enter new value for {name}: ").strip()
            if not new_value:
                print("  Aborted - no value provided")
                return {"rotated": False}
            return self.vault.rotate_secret(name, new_value)

        return {"error": "Unknown vault command"}

    def _cmd_incidents(self, args=None) -> dict:
        status = "open" if args and "--open" in args else None
        incs = self.db.get_incidents(status=status)
        self._print_header(f"INCIDENTS {'(open)' if status else '(all)'}")
        for i in incs:
            icon = "🔴" if i["severity"] == "critical" else "🟠" if i["severity"] == "high" else "🟡"
            print(f"  #{i['id']} {icon} [{i['status']}] {i['title'][:70]}")
        if not incs:
            print("  No incidents")
        return {"count": len(incs)}

    def _cmd_incident(self, args=None) -> dict:
        if not args:
            return {"error": "Provide incident ID"}
        inc_id = int(args[0])
        incs = self.db.get_incidents()
        for i in incs:
            if i["id"] == inc_id:
                self._print_header(f"INCIDENT #{inc_id}")
                print(json.dumps(i, indent=2, default=str))
                return i
        return {"error": "Not found"}

    def _cmd_events(self, args=None) -> dict:
        event_type = None
        if args and "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                event_type = args[idx + 1]
        events = self.db.get_events(event_type=event_type, limit=30)
        self._print_header("SECURITY EVENTS")
        for e in events:
            print(f"  [{e['severity']}] {e['created_at']} {e['title'][:60]}")
        return {"count": len(events)}

    def _cmd_report(self, args=None) -> dict:
        """Full security report."""
        self._print_header("FULL SECURITY REPORT")
        self._cmd_status()
        print()
        self._cmd_compliance()
        print()
        self._cmd_threats(["--open"])
        print()
        self._cmd_incidents(["--open"])
        vault = self.vault.get_rotation_status()
        if vault.get("overdue_count"):
            print(f"\n  ⚠️  {vault['overdue_count']} secrets overdue for rotation")
        return {"status": "complete"}

    def _cmd_worker(self, args=None) -> dict:
        from security_department.workers.sentinel_worker import main
        main()
        return {}

    def _cmd_help(self, args=None) -> dict:
        print(__doc__)
        return {}

    def _print_header(self, title: str):
        print(f"\n  ╔{'═' * (len(title) + 4)}╗")
        print(f"  ║  {title}  ║")
        print(f"  ╚{'═' * (len(title) + 4)}╝\n")


def main():
    sentinel = Sentinel()
    args = sys.argv[1:]
    sentinel.handle_command(args)


if __name__ == "__main__":
    main()
