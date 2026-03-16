"""SENTINEL-LOGS: Log analysis and SIEM-lite functionality.

Analyzes:
- SSH auth logs (brute force, successful logins, sudo)
- Nginx access/error logs (4xx/5xx spikes, bot attacks, path traversal)
- Application logs (errors, unusual patterns)
- fail2ban logs (ban/unban events)
"""
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional

from .database import SecurityDB
from ..config.settings import load_config

config = load_config()


class LogAnalyzer:
    """SIEM-lite log analysis engine."""

    def __init__(self, db: SecurityDB = None):
        self.db = db or SecurityDB()

    def analyze_all(self) -> dict:
        """Run full log analysis."""
        return {
            "ssh": self.analyze_ssh(),
            "nginx": self.analyze_nginx(),
            "fail2ban": self.analyze_fail2ban(),
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_ssh(self) -> dict:
        """Analyze SSH authentication logs."""
        auth_log = config.auth_log
        if not os.path.exists(auth_log):
            return {"error": "auth.log not found"}

        try:
            with open(auth_log, "r") as f:
                lines = f.readlines()[-2000:]  # Last 2000 lines
        except PermissionError:
            return {"error": "Cannot read auth.log"}

        failed_ips = Counter()
        success_ips = Counter()
        sudo_users = Counter()
        invalid_users = Counter()

        for line in lines:
            if "Failed password" in line:
                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                user = re.search(r'for (?:invalid user )?(\S+)', line)
                if ip:
                    failed_ips[ip.group(1)] += 1
                if user:
                    invalid_users[user.group(1)] += 1
            elif "Accepted" in line:
                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip:
                    success_ips[ip.group(1)] += 1
            elif "sudo:" in line and "COMMAND" in line:
                user = re.search(r'sudo:\s+(\S+)', line)
                if user:
                    sudo_users[user.group(1)] += 1

        result = {
            "total_lines_analyzed": len(lines),
            "failed_attempts": sum(failed_ips.values()),
            "successful_logins": sum(success_ips.values()),
            "top_attackers": dict(failed_ips.most_common(10)),
            "successful_ips": dict(success_ips.most_common(10)),
            "targeted_users": dict(invalid_users.most_common(10)),
            "sudo_usage": dict(sudo_users.most_common(10)),
        }

        # Flag anomalies
        for ip, count in failed_ips.most_common(5):
            if count >= config.alert.brute_force_threshold:
                self.db.log_event(
                    "brute_force_detected",
                    f"IP {ip}: {count} failed SSH attempts",
                    severity="high", source="log-analyzer", ip_address=ip,
                )

        return result

    def analyze_nginx(self) -> dict:
        """Analyze nginx access and error logs."""
        log_dir = config.nginx_log_dir
        results = {"sites": {}}

        for log_file in os.listdir(log_dir):
            if not log_file.endswith("-access.log"):
                continue

            site = log_file.replace("-access.log", "")
            filepath = os.path.join(log_dir, log_file)

            try:
                with open(filepath, "r") as f:
                    lines = f.readlines()[-5000:]
            except Exception:
                continue

            status_codes = Counter()
            ips = Counter()
            paths_4xx = Counter()
            suspicious_paths = []

            for line in lines:
                # Standard nginx log format
                parts = re.match(
                    r'(\S+) \S+ \S+ \[.*?\] "(\S+)\s+(\S+)\s+\S+" (\d+)',
                    line
                )
                if not parts:
                    continue

                ip, method, path, status = parts.groups()
                status = int(status)
                status_codes[status] += 1
                ips[ip] += 1

                if 400 <= status < 500:
                    paths_4xx[path] += 1

                # Detect path traversal, SQL injection, etc.
                if re.search(r'\.\./|/etc/passwd|<script|UNION\s+SELECT|%00', path, re.I):
                    suspicious_paths.append({"ip": ip, "path": path, "status": status})

            results["sites"][site] = {
                "total_requests": len(lines),
                "status_codes": dict(status_codes.most_common(10)),
                "top_ips": dict(ips.most_common(10)),
                "top_4xx_paths": dict(paths_4xx.most_common(10)),
                "suspicious_requests": suspicious_paths[:20],
                "error_rate": round(
                    sum(v for k, v in status_codes.items() if k >= 400) / max(len(lines), 1) * 100, 2
                ),
            }

            # Flag attacks
            if suspicious_paths:
                for req in suspicious_paths[:3]:
                    self.db.log_event(
                        "web_attack",
                        f"Suspicious request to {site}: {req['path']} from {req['ip']}",
                        severity="high", source="log-analyzer", ip_address=req["ip"],
                    )

        return results

    def analyze_fail2ban(self) -> dict:
        """Analyze fail2ban log for ban/unban events."""
        f2b_log = "/var/log/fail2ban.log"
        if not os.path.exists(f2b_log):
            return {"error": "fail2ban.log not found"}

        try:
            with open(f2b_log, "r") as f:
                lines = f.readlines()[-500:]
        except Exception:
            return {"error": "Cannot read fail2ban.log"}

        bans = Counter()
        unbans = Counter()
        jails = Counter()

        for line in lines:
            if "Ban" in line and "Unban" not in line:
                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                jail = re.search(r'\[(\S+)\]', line)
                if ip:
                    bans[ip.group(1)] += 1
                if jail:
                    jails[jail.group(1)] += 1
            elif "Unban" in line:
                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip:
                    unbans[ip.group(1)] += 1

        return {
            "total_bans": sum(bans.values()),
            "total_unbans": sum(unbans.values()),
            "top_banned_ips": dict(bans.most_common(10)),
            "bans_per_jail": dict(jails.most_common()),
            "repeat_offenders": {ip: c for ip, c in bans.items() if c > 2},
        }

    def get_summary(self) -> dict:
        """Quick summary for dashboard."""
        ssh = self.analyze_ssh()
        f2b = self.analyze_fail2ban()
        return {
            "ssh_failed_attempts": ssh.get("failed_attempts", 0),
            "ssh_successful_logins": ssh.get("successful_logins", 0),
            "top_attacker": next(iter(ssh.get("top_attackers", {})), None),
            "fail2ban_total_bans": f2b.get("total_bans", 0),
            "repeat_offenders": len(f2b.get("repeat_offenders", {})),
        }
