#!/usr/bin/env python3
"""SENTINEL Worker - Continuous security monitoring daemon.

Runs threat detection, log analysis, compliance checks on intervals.
Handles auto-remediation through incident response playbooks.

Run: python3 -m security_department.workers.sentinel_worker
  or: python3 /root/carbon6-platform/security-department/workers/sentinel_worker.py
"""
import logging
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from security_department.engine.database import SecurityDB
from security_department.engine.threat_detector import ThreatDetector
from security_department.engine.log_analyzer import LogAnalyzer
from security_department.engine.compliance import ComplianceEngine
from security_department.engine.incident_response import IncidentResponder
from security_department.engine.vault_manager import VaultManager
from security_department.config.settings import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SENTINEL] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/security/logs/sentinel-worker.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("sentinel.worker")

config = load_config()


def run_threat_scan(db, detector, responder):
    """Run threat detection and process results."""
    log.info("Running threat scan...")
    try:
        detected = detector.scan_all()
        for threat in detected:
            result = responder.handle_threat(threat)
            log.info(
                f"Threat processed: {threat.get('threat_type')} "
                f"[{threat.get('severity')}] → "
                f"{'auto-resolved' if result.get('auto_resolved') else 'needs review'}"
            )
        if not detected:
            log.info("Threat scan clear - no threats detected")
        return len(detected)
    except Exception as e:
        log.error(f"Threat scan failed: {e}")
        return -1


def run_log_analysis(analyzer):
    """Run log analysis."""
    log.info("Running log analysis...")
    try:
        summary = analyzer.get_summary()
        if summary.get("ssh_failed_attempts", 0) > 0:
            log.info(
                f"SSH: {summary['ssh_failed_attempts']} failed, "
                f"{summary['ssh_successful_logins']} success, "
                f"top attacker: {summary.get('top_attacker', 'none')}"
            )
        log.info(f"fail2ban: {summary.get('fail2ban_total_bans', 0)} total bans")
    except Exception as e:
        log.error(f"Log analysis failed: {e}")


def run_compliance_check(compliance_eng):
    """Run compliance scan."""
    log.info("Running compliance check...")
    try:
        result = compliance_eng.run_all()
        log.info(
            f"Compliance: {result['passed']}/{result['total']} passed "
            f"({result['score']}% - Grade {result['grade']})"
        )
        return result
    except Exception as e:
        log.error(f"Compliance check failed: {e}")
        return None


def check_vault_health(vault_mgr):
    """Check vault integrity and rotation status."""
    log.info("Checking vault health...")
    try:
        integrity = vault_mgr.verify_integrity()
        if integrity["failed"]:
            log.error(f"Vault integrity FAILED: {integrity['failed']}")
        else:
            log.info(f"Vault OK: {len(integrity['ok'])} secrets verified")

        rotation = vault_mgr.get_rotation_status()
        if rotation["overdue_count"] > 0:
            log.warning(f"Overdue secret rotations: {rotation['overdue_count']}")
            for secret in rotation["overdue"]:
                log.warning(f"  Overdue: {secret['secret_name']} (since {secret['next_rotation']})")
    except Exception as e:
        log.error(f"Vault check failed: {e}")


def main():
    log.info("=" * 60)
    log.info("SENTINEL Worker starting...")
    log.info(f"Threat scan interval: {config.scan.threat_scan_interval}s")
    log.info(f"Log analysis interval: {config.scan.log_analysis_interval}s")
    log.info(f"Compliance interval: {config.scan.compliance_interval}s")
    log.info("=" * 60)

    db = SecurityDB()
    detector = ThreatDetector(db=db)
    responder = IncidentResponder(db=db)
    analyzer = LogAnalyzer(db=db)
    compliance_eng = ComplianceEngine(db=db)
    vault_mgr = VaultManager(db=db)

    db.log_event("worker_started", "SENTINEL worker started",
                 severity="info", source="sentinel-worker")

    # Track last run times
    last_threat_scan = 0
    last_log_analysis = 0
    last_compliance = 0
    last_vault_check = 0

    try:
        while True:
            now = time.time()

            # Threat scan (every 5 min)
            if now - last_threat_scan >= config.scan.threat_scan_interval:
                run_threat_scan(db, detector, responder)
                last_threat_scan = now

            # Log analysis (every 10 min)
            if now - last_log_analysis >= config.scan.log_analysis_interval:
                run_log_analysis(analyzer)
                last_log_analysis = now

            # Compliance check (daily)
            if now - last_compliance >= config.scan.compliance_interval:
                run_compliance_check(compliance_eng)
                last_compliance = now

            # Vault health (every hour)
            if now - last_vault_check >= 3600:
                check_vault_health(vault_mgr)
                last_vault_check = now

            time.sleep(30)  # Check loop every 30s

    except KeyboardInterrupt:
        log.info("SENTINEL worker stopped")
        db.log_event("worker_stopped", "SENTINEL worker stopped",
                     severity="info", source="sentinel-worker")


if __name__ == "__main__":
    main()
