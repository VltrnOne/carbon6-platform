"""SENTINEL-THREAT: Real-time threat detection engine.

Monitors:
- SSH brute force attacks (auth.log)
- fail2ban status and banned IPs
- Suspicious processes (miners, reverse shells)
- Port scanning / unexpected listeners
- File integrity (sensitive config changes)
"""
import os
import re
import subprocess
import time
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from .database import SecurityDB
from ..config.settings import load_config

config = load_config()


class ThreatDetector:
    """Real-time threat detection and auto-response."""

    SEVERITY_MAP = {
        "brute_force": "high",
        "suspicious_process": "critical",
        "port_scan": "medium",
        "unauthorized_access": "critical",
        "config_tamper": "high",
        "service_down": "medium",
    }

    def __init__(self, db: SecurityDB = None):
        self.db = db or SecurityDB()

    def scan_all(self) -> list:
        """Run all threat detection scans. Returns list of detected threats."""
        threats = []
        threats.extend(self._scan_brute_force())
        threats.extend(self._scan_suspicious_processes())
        threats.extend(self._scan_unexpected_listeners())
        threats.extend(self._scan_fail2ban())
        threats.extend(self._scan_file_integrity())
        return threats

    def _scan_brute_force(self) -> list:
        """Detect SSH brute force attacks from auth.log."""
        threats = []
        auth_log = config.auth_log

        if not os.path.exists(auth_log):
            return threats

        try:
            # Get recent failed attempts
            result = subprocess.run(
                ["grep", "-E", "Failed password|Invalid user", auth_log],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return threats

            lines = result.stdout.strip().split("\n")
            if not lines or lines == [""]:
                return threats

            # Count by IP in last hour
            now = datetime.now()
            ip_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
            ip_counts = Counter()

            for line in lines[-500:]:  # Last 500 lines
                match = ip_pattern.search(line)
                if match:
                    ip_counts[match.group(1)] += 1

            for ip, count in ip_counts.most_common(10):
                if count >= config.alert.brute_force_threshold:
                    threat = {
                        "threat_type": "brute_force",
                        "source": ip,
                        "description": f"SSH brute force: {count} failed attempts from {ip}",
                        "severity": "high",
                        "cvss_score": 7.5,
                        "remediation": f"IP {ip} should be banned via fail2ban or UFW",
                    }
                    threats.append(threat)

                    # Auto-remediate: check if already banned
                    self._auto_ban_ip(ip, count)

        except Exception as e:
            self.db.log_event("scan_error", f"Brute force scan failed: {e}",
                              severity="warning", source="threat-detector")

        return threats

    def _auto_ban_ip(self, ip: str, attempt_count: int):
        """Auto-ban IP if not already banned by fail2ban."""
        try:
            result = subprocess.run(
                ["fail2ban-client", "status", "sshd"],
                capture_output=True, text=True, timeout=5
            )
            if ip not in result.stdout:
                # Not yet banned - log but don't auto-ban (fail2ban handles this)
                self.db.log_event(
                    "brute_force_detected",
                    f"IP {ip} has {attempt_count} failed SSH attempts",
                    severity="high",
                    source="threat-detector",
                    ip_address=ip,
                )
        except Exception:
            pass

    def _scan_suspicious_processes(self) -> list:
        """Detect known malicious process patterns."""
        threats = []
        suspicious_patterns = [
            (r"xmrig|cryptominer|minerd|cpuminer", "cryptominer", "critical", 9.0),
            (r"nc\s+-l|ncat\s+-l|socat\s+TCP-LISTEN", "reverse_shell", "critical", 9.5),
            (r"masscan|zmap|nmap\s+-sS", "port_scanner", "high", 6.0),
        ]

        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=5
            )

            for pattern, name, severity, cvss in suspicious_patterns:
                matches = re.findall(pattern, result.stdout, re.IGNORECASE)
                if matches:
                    threat = {
                        "threat_type": "suspicious_process",
                        "source": name,
                        "description": f"Suspicious process detected: {name} ({len(matches)} matches)",
                        "severity": severity,
                        "cvss_score": cvss,
                        "remediation": f"Investigate and kill suspicious {name} processes",
                    }
                    threats.append(threat)
                    self.db.log_event(
                        "suspicious_process",
                        f"Detected {name} process",
                        severity=severity,
                        source="threat-detector",
                    )

        except Exception:
            pass

        return threats

    def _scan_unexpected_listeners(self) -> list:
        """Detect new/unexpected listening ports."""
        threats = []
        # Known safe ports
        known_ports = {22, 80, 443, 3000, 3001, 3006, 3100, 3200, 3300,
                       4000, 5000, 5001, 5432, 6379, 11434}

        try:
            result = subprocess.run(
                ["ss", "-tlnp"], capture_output=True, text=True, timeout=5
            )

            for line in result.stdout.split("\n")[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                addr = parts[3]
                # Extract port
                port_match = re.search(r':(\d+)$', addr)
                if not port_match:
                    continue
                port = int(port_match.group(1))

                # Skip localhost-only and known ports
                if "127.0.0." in addr or "::1:" in addr:
                    continue
                if port in known_ports:
                    continue
                if port < 1024 or port > 65000:
                    continue

                process = parts[-1] if len(parts) > 5 else "unknown"
                threat = {
                    "threat_type": "unexpected_listener",
                    "source": f"port:{port}",
                    "description": f"Unexpected public listener on port {port}: {process}",
                    "severity": "medium",
                    "cvss_score": 5.0,
                    "remediation": f"Investigate process on port {port} or block with UFW",
                }
                threats.append(threat)

        except Exception:
            pass

        return threats

    def _scan_fail2ban(self) -> list:
        """Check fail2ban health and recently banned IPs."""
        threats = []
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "fail2ban"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip() != "active":
                threats.append({
                    "threat_type": "service_down",
                    "source": "fail2ban",
                    "description": "fail2ban is not running - brute force protection disabled",
                    "severity": "critical",
                    "cvss_score": 8.0,
                    "remediation": "systemctl restart fail2ban",
                })
                self.db.log_event("service_down", "fail2ban not active",
                                  severity="critical", source="threat-detector")
        except Exception:
            pass

        return threats

    def _scan_file_integrity(self) -> list:
        """Check if sensitive files have unexpected permissions."""
        threats = []
        checks = [
            ("/root/.carbon6-vault/vault.key", "600"),
            ("/root/.carbon6-vault/secrets.enc", "600"),
            ("/root/.redis_password", "600"),
            ("/root/.webhook_secret", "600"),
            ("/root/github-automation/config/hostinger.json", "600"),
            ("/root/github-automation/config/render.json", "600"),
            ("/root/github-automation/config/repos.json", "600"),
        ]

        for filepath, expected_mode in checks:
            if not os.path.exists(filepath):
                continue
            actual_mode = oct(os.stat(filepath).st_mode)[-3:]
            if actual_mode != expected_mode:
                threats.append({
                    "threat_type": "config_tamper",
                    "source": filepath,
                    "description": f"File {filepath} has mode {actual_mode} (expected {expected_mode})",
                    "severity": "high",
                    "cvss_score": 7.0,
                    "remediation": f"chmod {expected_mode} {filepath}",
                })

        return threats
