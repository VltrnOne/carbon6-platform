"""SENTINEL-INCIDENT: Automated incident response and playbooks.

Handles:
- Incident creation/tracking/resolution
- Automated playbook execution
- Auto-remediation for common threats
- HERMES notification integration
- Timeline tracking
"""
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Optional

from .database import SecurityDB
from ..config.settings import load_config

config = load_config()


class IncidentResponder:
    """Automated incident response with playbooks."""

    # Auto-remediation playbooks
    PLAYBOOKS = {
        "brute_force": {
            "name": "SSH Brute Force Response",
            "steps": [
                "Verify fail2ban is banning the IP",
                "Check if IP is already in UFW deny list",
                "Add permanent UFW block if repeat offender",
                "Log incident and notify via HERMES",
            ],
            "auto_actions": ["verify_fail2ban", "permanent_ban_repeat"],
        },
        "suspicious_process": {
            "name": "Suspicious Process Response",
            "steps": [
                "Identify process PID and owner",
                "Capture process details for forensics",
                "Kill process if confirmed malicious",
                "Check for persistence mechanisms",
                "Create high-severity incident",
            ],
            "auto_actions": ["capture_forensics"],
        },
        "config_tamper": {
            "name": "Configuration Tampering Response",
            "steps": [
                "Identify changed file and new permissions",
                "Restore correct permissions",
                "Check git history for unauthorized changes",
                "Log event and escalate",
            ],
            "auto_actions": ["restore_permissions"],
        },
        "service_down": {
            "name": "Security Service Down Response",
            "steps": [
                "Identify which service is down",
                "Attempt automatic restart",
                "Verify service is healthy after restart",
                "Notify if restart fails",
            ],
            "auto_actions": ["restart_service"],
        },
        "cert_expiry": {
            "name": "Certificate Expiry Response",
            "steps": [
                "Run certbot renewal",
                "Reload nginx",
                "Verify new certificate",
                "Update monitoring",
            ],
            "auto_actions": ["renew_cert"],
        },
    }

    def __init__(self, db: SecurityDB = None):
        self.db = db or SecurityDB()

    def handle_threat(self, threat: dict) -> dict:
        """Process a detected threat through the appropriate playbook."""
        threat_type = threat.get("threat_type", "unknown")
        playbook = self.PLAYBOOKS.get(threat_type)

        # Log the threat
        threat_id = self.db.add_threat(**threat)

        if not playbook:
            # No playbook - create incident for manual review
            inc_id = self.db.create_incident(
                title=f"Unclassified threat: {threat.get('description', 'Unknown')}",
                severity=threat.get("severity", "medium"),
                description=json.dumps(threat, indent=2),
                affected_systems=threat.get("source", "unknown"),
            )
            return {"threat_id": threat_id, "incident_id": inc_id, "playbook": None,
                    "action": "manual_review_required"}

        # Execute auto-remediation
        results = []
        for action in playbook.get("auto_actions", []):
            result = self._execute_action(action, threat)
            results.append(result)

        # Create incident with playbook reference
        inc_id = self.db.create_incident(
            title=f"{playbook['name']}: {threat.get('description', '')}",
            severity=threat.get("severity", "medium"),
            description=json.dumps(threat, indent=2),
            affected_systems=threat.get("source", "unknown"),
        )

        # Update incident with remediation steps and results
        timeline = json.dumps([
            {"time": datetime.now().isoformat(), "action": "Threat detected", "detail": threat.get("description")},
            {"time": datetime.now().isoformat(), "action": "Playbook triggered", "detail": playbook["name"]},
            *[{"time": datetime.now().isoformat(), "action": r["action"], "detail": r.get("detail", "")} for r in results],
        ])

        all_success = all(r.get("success") for r in results)
        self.db.update_incident(
            inc_id,
            timeline=timeline,
            remediation_steps=json.dumps(playbook["steps"]),
            status="resolved" if all_success else "open",
        )

        if all_success:
            self.db.resolve_threat(threat_id, auto=True)

        # Notify via HERMES if configured
        if config.alert.notify_hermes:
            self._notify_hermes(threat, playbook, results)

        return {
            "threat_id": threat_id,
            "incident_id": inc_id,
            "playbook": playbook["name"],
            "auto_actions": results,
            "auto_resolved": all_success,
        }

    def _execute_action(self, action: str, threat: dict) -> dict:
        """Execute a single remediation action."""
        handlers = {
            "verify_fail2ban": self._action_verify_fail2ban,
            "permanent_ban_repeat": self._action_permanent_ban,
            "capture_forensics": self._action_capture_forensics,
            "restore_permissions": self._action_restore_permissions,
            "restart_service": self._action_restart_service,
            "renew_cert": self._action_renew_cert,
        }

        handler = handlers.get(action)
        if not handler:
            return {"action": action, "success": False, "detail": "Unknown action"}

        try:
            return handler(threat)
        except Exception as e:
            return {"action": action, "success": False, "detail": str(e)}

    def _action_verify_fail2ban(self, threat: dict) -> dict:
        try:
            result = subprocess.run(
                ["fail2ban-client", "status", "sshd"],
                capture_output=True, text=True, timeout=5
            )
            ip = threat.get("source", "")
            banned = ip in result.stdout
            return {
                "action": "verify_fail2ban",
                "success": True,
                "detail": f"IP {ip} {'is' if banned else 'is NOT'} banned by fail2ban",
            }
        except Exception as e:
            return {"action": "verify_fail2ban", "success": False, "detail": str(e)}

    def _action_permanent_ban(self, threat: dict) -> dict:
        """Permanently ban repeat offender IPs via UFW."""
        ip = threat.get("source", "")
        if not ip or not all(c.isdigit() or c == "." for c in ip):
            return {"action": "permanent_ban", "success": False, "detail": "Invalid IP"}

        # Check if already banned
        result = subprocess.run(
            ["ufw", "status"], capture_output=True, text=True, timeout=5
        )
        if f"DENY.*{ip}" in result.stdout:
            return {"action": "permanent_ban", "success": True,
                    "detail": f"IP {ip} already in UFW deny list"}

        # Add permanent ban
        subprocess.run(
            ["ufw", "insert", "1", "deny", "from", ip],
            capture_output=True, timeout=5
        )
        self.db.log_event("auto_ban", f"Permanently banned IP {ip} via UFW",
                          severity="high", source="incident-response", ip_address=ip)
        return {"action": "permanent_ban", "success": True,
                "detail": f"IP {ip} permanently banned via UFW"}

    def _action_capture_forensics(self, threat: dict) -> dict:
        """Capture process details for forensic analysis."""
        source = threat.get("source", "")
        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=5
            )
            matching = [l for l in result.stdout.split("\n") if source in l.lower()]
            forensic_dir = os.path.join(config.log_dir, "forensics")
            os.makedirs(forensic_dir, exist_ok=True)

            report = {
                "timestamp": datetime.now().isoformat(),
                "threat": threat,
                "matching_processes": matching,
                "full_ps": result.stdout[:5000],
            }
            filepath = os.path.join(forensic_dir,
                                    f"forensic-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)

            return {"action": "capture_forensics", "success": True,
                    "detail": f"Forensics saved to {filepath}"}
        except Exception as e:
            return {"action": "capture_forensics", "success": False, "detail": str(e)}

    def _action_restore_permissions(self, threat: dict) -> dict:
        """Restore correct file permissions."""
        filepath = threat.get("source", "")
        remediation = threat.get("remediation", "")
        if "chmod" in remediation:
            try:
                subprocess.run(remediation.split(), capture_output=True, timeout=5)
                return {"action": "restore_permissions", "success": True,
                        "detail": f"Restored: {remediation}"}
            except Exception as e:
                return {"action": "restore_permissions", "success": False, "detail": str(e)}
        return {"action": "restore_permissions", "success": False, "detail": "No remediation cmd"}

    def _action_restart_service(self, threat: dict) -> dict:
        """Restart a down security service."""
        service = threat.get("source", "")
        if service not in ("fail2ban", "nginx", "redis-server", "ssh"):
            return {"action": "restart_service", "success": False,
                    "detail": f"Cannot auto-restart unknown service: {service}"}
        try:
            subprocess.run(["systemctl", "restart", service],
                           capture_output=True, timeout=30)
            # Verify
            result = subprocess.run(["systemctl", "is-active", service],
                                    capture_output=True, text=True, timeout=5)
            success = "active" in result.stdout
            return {"action": "restart_service", "success": success,
                    "detail": f"{service} {'restarted' if success else 'failed to restart'}"}
        except Exception as e:
            return {"action": "restart_service", "success": False, "detail": str(e)}

    def _action_renew_cert(self, threat: dict) -> dict:
        """Renew SSL certificate via certbot."""
        try:
            result = subprocess.run(
                ["certbot", "renew", "--quiet"],
                capture_output=True, text=True, timeout=120
            )
            subprocess.run(["systemctl", "reload", "nginx"],
                           capture_output=True, timeout=10)
            return {"action": "renew_cert", "success": result.returncode == 0,
                    "detail": "Certificate renewal attempted and nginx reloaded"}
        except Exception as e:
            return {"action": "renew_cert", "success": False, "detail": str(e)}

    def _notify_hermes(self, threat: dict, playbook: dict, results: list):
        """Send alert via HERMES communications."""
        try:
            import requests
            severity = threat.get("severity", "medium")
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(severity, "🔵")
            msg = (
                f"{emoji} SENTINEL ALERT\n"
                f"Threat: {threat.get('description', 'Unknown')}\n"
                f"Severity: {severity}\n"
                f"Playbook: {playbook['name']}\n"
                f"Auto-resolved: {all(r.get('success') for r in results)}"
            )
            requests.post(
                "http://127.0.0.1:3100/api/comms/send",
                json={"to": "admin", "body": msg, "channel": config.alert.notify_channel},
                timeout=5,
            )
        except Exception:
            pass  # Don't fail the incident response if notification fails
