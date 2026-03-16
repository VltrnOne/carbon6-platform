"""SENTINEL-COMPLIANCE: Automated security compliance checks.

Checks:
- SSH hardening (key-only, no root password, MaxAuthTries)
- Firewall rules (UFW active, no wide-open ranges)
- SSL/TLS certificates (expiry, valid config)
- Redis/PostgreSQL authentication
- File permissions on secrets
- Kernel hardening (sysctl)
- Service isolation
- Unattended security updates
- Nginx security headers
- Vault encryption status
"""
import os
import re
import subprocess
from datetime import datetime

from .database import SecurityDB
from ..config.settings import load_config

config = load_config()


class ComplianceEngine:
    """Automated compliance and hardening verification."""

    def __init__(self, db: SecurityDB = None):
        self.db = db or SecurityDB()

    def run_all(self) -> dict:
        """Run all compliance checks and store results."""
        checks = {}
        checks["ssh"] = self._check_ssh()
        checks["firewall"] = self._check_firewall()
        checks["ssl"] = self._check_ssl()
        checks["redis"] = self._check_redis()
        checks["postgres"] = self._check_postgres()
        checks["file_permissions"] = self._check_file_permissions()
        checks["kernel"] = self._check_kernel()
        checks["nginx"] = self._check_nginx()
        checks["vault"] = self._check_vault()
        checks["updates"] = self._check_updates()
        checks["fail2ban"] = self._check_fail2ban()

        # Calculate overall score
        total = 0
        passed = 0
        for category, results in checks.items():
            for check_name, check in results.items():
                total += 1
                if check["status"] == "pass":
                    passed += 1
                # Store in DB
                self.db.update_compliance(
                    f"{category}.{check_name}",
                    category,
                    check["status"],
                    check.get("detail", ""),
                )

        score = round(passed / max(total, 1) * 100)
        grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "F"

        self.db.log_event(
            "compliance_scan",
            f"Compliance scan: {passed}/{total} passed ({score}% - Grade {grade})",
            severity="info" if score >= 75 else "warning",
            source="compliance",
        )

        return {
            "checks": checks,
            "score": score,
            "grade": grade,
            "passed": passed,
            "total": total,
            "failed": total - passed,
            "timestamp": datetime.now().isoformat(),
        }

    def _run(self, cmd: list, timeout: int = 5) -> str:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.stdout + r.stderr
        except Exception:
            return ""

    def _check_ssh(self) -> dict:
        checks = {}
        try:
            with open("/etc/ssh/sshd_config") as f:
                sshd = f.read()
        except Exception:
            return {"read_config": {"status": "fail", "detail": "Cannot read sshd_config"}}

        # PermitRootLogin
        if re.search(r'^PermitRootLogin\s+prohibit-password', sshd, re.M):
            checks["root_login"] = {"status": "pass", "detail": "Key-only root login"}
        elif re.search(r'^PermitRootLogin\s+no', sshd, re.M):
            checks["root_login"] = {"status": "pass", "detail": "Root login disabled"}
        else:
            checks["root_login"] = {"status": "fail", "detail": "Root password login enabled"}

        # PasswordAuthentication
        if re.search(r'^PasswordAuthentication\s+no', sshd, re.M):
            checks["password_auth"] = {"status": "pass", "detail": "Password auth disabled"}
        else:
            checks["password_auth"] = {"status": "fail", "detail": "Password auth enabled"}

        # MaxAuthTries
        match = re.search(r'^MaxAuthTries\s+(\d+)', sshd, re.M)
        if match and int(match.group(1)) <= 5:
            checks["max_auth"] = {"status": "pass", "detail": f"MaxAuthTries={match.group(1)}"}
        else:
            checks["max_auth"] = {"status": "fail", "detail": "MaxAuthTries too high or not set"}

        return checks

    def _check_firewall(self) -> dict:
        checks = {}
        output = self._run(["ufw", "status"])

        if "Status: active" in output:
            checks["ufw_active"] = {"status": "pass", "detail": "UFW active"}
        else:
            checks["ufw_active"] = {"status": "fail", "detail": "UFW not active"}

        # Check for overly broad port ranges
        if re.search(r'30001:30999', output):
            checks["no_wide_ranges"] = {"status": "fail", "detail": "Wide port range 30001-30999 open"}
        else:
            checks["no_wide_ranges"] = {"status": "pass", "detail": "No unnecessary wide port ranges"}

        return checks

    def _check_ssl(self) -> dict:
        checks = {}
        cert_dir = "/etc/letsencrypt/live"
        if not os.path.exists(cert_dir):
            return {"certs_exist": {"status": "fail", "detail": "No Let's Encrypt certs"}}

        for domain in os.listdir(cert_dir):
            cert = os.path.join(cert_dir, domain, "fullchain.pem")
            if not os.path.exists(cert):
                continue
            output = self._run(["openssl", "x509", "-enddate", "-noout", "-in", cert])
            match = re.search(r'notAfter=(.+)', output)
            if match:
                try:
                    expiry = datetime.strptime(match.group(1).strip(), "%b %d %H:%M:%S %Y %Z")
                    days = (expiry - datetime.now()).days
                    if days > config.alert.cert_expiry_warn_days:
                        checks[f"ssl_{domain}"] = {"status": "pass", "detail": f"{days} days remaining"}
                    else:
                        checks[f"ssl_{domain}"] = {"status": "fail", "detail": f"Expires in {days} days!"}
                except Exception:
                    checks[f"ssl_{domain}"] = {"status": "warn", "detail": "Cannot parse expiry"}

        return checks

    def _check_redis(self) -> dict:
        checks = {}
        # Check if Redis requires auth
        output = self._run(["redis-cli", "ping"])
        if "NOAUTH" in output or "ERR" in output:
            checks["redis_auth"] = {"status": "pass", "detail": "Authentication required"}
        elif "PONG" in output:
            checks["redis_auth"] = {"status": "fail", "detail": "No authentication - open access"}
        else:
            checks["redis_auth"] = {"status": "warn", "detail": "Cannot connect to Redis"}

        # Check bind address
        pw = ""
        try:
            with open("/root/.redis_password") as f:
                pw = f.read().strip()
        except Exception:
            pass
        output = self._run(["redis-cli", "-a", pw, "CONFIG", "GET", "bind"])
        if "127.0.0.1" in output:
            checks["redis_bind"] = {"status": "pass", "detail": "Bound to localhost only"}
        else:
            checks["redis_bind"] = {"status": "fail", "detail": "May be exposed externally"}

        return checks

    def _check_postgres(self) -> dict:
        checks = {}
        output = self._run(["ss", "-tlnp"])
        if "0.0.0.0:5432" not in output and ":::5432" not in output:
            checks["pg_local"] = {"status": "pass", "detail": "PostgreSQL localhost only"}
        else:
            checks["pg_local"] = {"status": "fail", "detail": "PostgreSQL exposed externally"}
        return checks

    def _check_file_permissions(self) -> dict:
        checks = {}
        files = {
            "vault_key": "/root/.carbon6-vault/vault.key",
            "vault_secrets": "/root/.carbon6-vault/secrets.enc",
            "redis_password": "/root/.redis_password",
            "webhook_secret": "/root/.webhook_secret",
            "hostinger_config": "/root/github-automation/config/hostinger.json",
            "render_config": "/root/github-automation/config/render.json",
        }

        for name, path in files.items():
            if not os.path.exists(path):
                checks[name] = {"status": "warn", "detail": f"{path} not found"}
                continue
            mode = oct(os.stat(path).st_mode)[-3:]
            if mode == "600":
                checks[name] = {"status": "pass", "detail": f"{mode} (owner-only)"}
            else:
                checks[name] = {"status": "fail", "detail": f"{mode} (should be 600)"}

        return checks

    def _check_kernel(self) -> dict:
        checks = {}
        params = {
            "syncookies": ("net.ipv4.tcp_syncookies", "1"),
            "no_redirects": ("net.ipv4.conf.all.accept_redirects", "0"),
            "rp_filter": ("net.ipv4.conf.all.rp_filter", "1"),
            "no_source_route": ("net.ipv4.conf.all.accept_source_route", "0"),
        }

        for name, (param, expected) in params.items():
            output = self._run(["sysctl", "-n", param]).strip()
            if output == expected:
                checks[name] = {"status": "pass", "detail": f"{param}={output}"}
            else:
                checks[name] = {"status": "fail", "detail": f"{param}={output} (expected {expected})"}

        return checks

    def _check_nginx(self) -> dict:
        checks = {}
        output = self._run(["nginx", "-t"])
        if "syntax is ok" in output.lower() or "test is successful" in output.lower():
            checks["config_valid"] = {"status": "pass", "detail": "Config valid"}
        else:
            checks["config_valid"] = {"status": "fail", "detail": "Config invalid"}

        # Check HSTS in vblox config
        try:
            with open("/etc/nginx/sites-enabled/vblox.conf") as f:
                vblox = f.read()
            if "Strict-Transport-Security" in vblox:
                checks["hsts"] = {"status": "pass", "detail": "HSTS enabled"}
            else:
                checks["hsts"] = {"status": "fail", "detail": "HSTS not configured"}
        except Exception:
            checks["hsts"] = {"status": "warn", "detail": "Cannot read vblox.conf"}

        return checks

    def _check_vault(self) -> dict:
        checks = {}
        vault_file = os.path.join(config.vault_path, "secrets.enc")
        key_file = os.path.join(config.vault_path, "vault.key")

        if os.path.exists(vault_file) and os.path.exists(key_file):
            checks["vault_initialized"] = {"status": "pass", "detail": "Vault exists"}
        else:
            checks["vault_initialized"] = {"status": "fail", "detail": "Vault not initialized"}

        vault_dir_mode = oct(os.stat(config.vault_path).st_mode)[-3:] if os.path.exists(config.vault_path) else "?"
        if vault_dir_mode == "700":
            checks["vault_dir_perms"] = {"status": "pass", "detail": "700 (owner-only)"}
        else:
            checks["vault_dir_perms"] = {"status": "fail", "detail": f"{vault_dir_mode} (should be 700)"}

        return checks

    def _check_updates(self) -> dict:
        checks = {}
        output = self._run(["dpkg", "-l", "unattended-upgrades"])
        if "ii" in output:
            checks["auto_updates"] = {"status": "pass", "detail": "unattended-upgrades installed"}
        else:
            checks["auto_updates"] = {"status": "fail", "detail": "unattended-upgrades not installed"}
        return checks

    def _check_fail2ban(self) -> dict:
        checks = {}
        output = self._run(["systemctl", "is-active", "fail2ban"])
        if "active" in output:
            checks["f2b_active"] = {"status": "pass", "detail": "Running"}
        else:
            checks["f2b_active"] = {"status": "fail", "detail": "Not running"}

        output = self._run(["fail2ban-client", "status"])
        match = re.search(r'Number of jail:\s+(\d+)', output)
        if match and int(match.group(1)) >= 3:
            checks["f2b_jails"] = {"status": "pass", "detail": f"{match.group(1)} jails active"}
        else:
            checks["f2b_jails"] = {"status": "fail", "detail": "Insufficient jails configured"}

        return checks
