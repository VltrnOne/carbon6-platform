"""Security Department Database - Event logging, threat tracking, audit trail.

Uses SQLite for portability with the same schema pattern as HERMES.
Can migrate to PostgreSQL schema 'security' for production.
"""
import json
import os
import sqlite3
import time
from datetime import datetime
from typing import Optional

DB_PATH = os.getenv("SECURITY_DB_PATH", "/root/security/sentinel.db")


class SecurityDB:
    """Security event database with full audit trail."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_tables()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_tables(self):
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'info',
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                resolved INTEGER DEFAULT 0,
                resolved_at TEXT,
                resolved_by TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_type TEXT NOT NULL,
                source TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'medium',
                cvss_score REAL,
                status TEXT DEFAULT 'open',
                remediation TEXT,
                auto_remediated INTEGER DEFAULT 0,
                detected_at TEXT DEFAULT (datetime('now')),
                resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                user TEXT,
                ip_address TEXT,
                resource TEXT,
                result TEXT NOT NULL DEFAULT 'allowed',
                details TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS secret_rotation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_name TEXT NOT NULL UNIQUE,
                last_rotated TEXT,
                next_rotation TEXT,
                rotation_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unknown',
                details TEXT,
                last_checked TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                description TEXT,
                affected_systems TEXT,
                timeline TEXT,
                remediation_steps TEXT,
                assigned_to TEXT DEFAULT 'SENTINEL',
                created_at TEXT DEFAULT (datetime('now')),
                resolved_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_events_type ON security_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity);
            CREATE INDEX IF NOT EXISTS idx_events_created ON security_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status);
            CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity);
            CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
        """)
        conn.commit()
        conn.close()

    # ── Events ───────────────────────────────────────────

    def log_event(self, event_type: str, title: str, severity: str = "info",
                  source: str = "sentinel", details: str = None,
                  ip_address: str = None) -> int:
        conn = self._conn()
        c = conn.execute(
            """INSERT INTO security_events
               (event_type, severity, source, title, details, ip_address)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event_type, severity, source, title, details, ip_address)
        )
        event_id = c.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_events(self, event_type: str = None, severity: str = None,
                   limit: int = 50, unresolved_only: bool = False) -> list:
        conn = self._conn()
        query = "SELECT * FROM security_events WHERE 1=1"
        params = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if unresolved_only:
            query += " AND resolved = 0"
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def resolve_event(self, event_id: int, resolved_by: str = "sentinel") -> bool:
        conn = self._conn()
        conn.execute(
            "UPDATE security_events SET resolved=1, resolved_at=datetime('now'), resolved_by=? WHERE id=?",
            (resolved_by, event_id)
        )
        conn.commit()
        conn.close()
        return True

    # ── Threats ──────────────────────────────────────────

    def add_threat(self, threat_type: str, source: str, description: str,
                   severity: str = "medium", cvss_score: float = None,
                   remediation: str = None) -> int:
        conn = self._conn()
        c = conn.execute(
            """INSERT INTO threats
               (threat_type, source, description, severity, cvss_score, remediation)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (threat_type, source, description, severity, cvss_score, remediation)
        )
        threat_id = c.lastrowid
        conn.commit()
        conn.close()
        return threat_id

    def get_threats(self, status: str = None, severity: str = None,
                    limit: int = 50) -> list:
        conn = self._conn()
        query = "SELECT * FROM threats WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def resolve_threat(self, threat_id: int, auto: bool = False) -> bool:
        conn = self._conn()
        conn.execute(
            "UPDATE threats SET status='resolved', resolved_at=datetime('now'), auto_remediated=? WHERE id=?",
            (1 if auto else 0, threat_id)
        )
        conn.commit()
        conn.close()
        return True

    # ── Incidents ────────────────────────────────────────

    def create_incident(self, title: str, severity: str, description: str,
                        affected_systems: str = None) -> int:
        conn = self._conn()
        c = conn.execute(
            """INSERT INTO incidents
               (title, severity, description, affected_systems)
               VALUES (?, ?, ?, ?)""",
            (title, severity, description, affected_systems)
        )
        inc_id = c.lastrowid
        conn.commit()
        conn.close()
        return inc_id

    def update_incident(self, incident_id: int, **kwargs) -> bool:
        conn = self._conn()
        sets = []
        params = []
        for k, v in kwargs.items():
            if k in ("status", "remediation_steps", "timeline", "assigned_to"):
                sets.append(f"{k} = ?")
                params.append(v)
        if not sets:
            return False
        if kwargs.get("status") == "resolved":
            sets.append("resolved_at = datetime('now')")
        params.append(incident_id)
        conn.execute(f"UPDATE incidents SET {', '.join(sets)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        return True

    def get_incidents(self, status: str = None, limit: int = 20) -> list:
        conn = self._conn()
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Secret Rotation ──────────────────────────────────

    def track_secret(self, name: str, rotation_days: int = 90) -> int:
        conn = self._conn()
        next_rot = datetime.now().isoformat()
        conn.execute(
            """INSERT OR REPLACE INTO secret_rotation
               (secret_name, last_rotated, next_rotation)
               VALUES (?, datetime('now'), datetime('now', ? || ' days'))""",
            (name, str(rotation_days))
        )
        conn.commit()
        conn.close()
        return 0

    def get_rotation_status(self) -> list:
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM secret_rotation ORDER BY next_rotation ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_overdue_rotations(self) -> list:
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM secret_rotation WHERE next_rotation < datetime('now')"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Compliance ───────────────────────────────────────

    def update_compliance(self, check_name: str, category: str,
                          status: str, details: str = None):
        conn = self._conn()
        conn.execute(
            """INSERT INTO compliance_checks (check_name, category, status, details, last_checked)
               VALUES (?, ?, ?, ?, datetime('now'))
               ON CONFLICT(check_name) DO UPDATE SET
               status=excluded.status, details=excluded.details, last_checked=excluded.last_checked""",
            (check_name, category, status, details)
        )
        conn.commit()
        conn.close()

    def get_compliance(self, category: str = None) -> list:
        conn = self._conn()
        query = "SELECT * FROM compliance_checks"
        params = []
        if category:
            query += " WHERE category = ?"
            params.append(category)
        query += " ORDER BY last_checked DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Access Log ───────────────────────────────────────

    def log_access(self, action: str, resource: str, result: str = "allowed",
                   user: str = None, ip_address: str = None, details: str = None):
        conn = self._conn()
        conn.execute(
            """INSERT INTO access_log (action, user, ip_address, resource, result, details)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (action, user, ip_address, resource, result, details)
        )
        conn.commit()
        conn.close()

    # ── Stats ────────────────────────────────────────────

    def stats(self) -> dict:
        conn = self._conn()
        events_24h = conn.execute(
            "SELECT COUNT(*) FROM security_events WHERE created_at > datetime('now', '-1 day')"
        ).fetchone()[0]
        open_threats = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE status = 'open'"
        ).fetchone()[0]
        critical_threats = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE status = 'open' AND severity = 'critical'"
        ).fetchone()[0]
        open_incidents = conn.execute(
            "SELECT COUNT(*) FROM incidents WHERE status = 'open'"
        ).fetchone()[0]
        overdue_secrets = conn.execute(
            "SELECT COUNT(*) FROM secret_rotation WHERE next_rotation < datetime('now')"
        ).fetchone()[0]
        compliance = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM compliance_checks GROUP BY status"
        ).fetchall()
        conn.close()

        return {
            "events_24h": events_24h,
            "open_threats": open_threats,
            "critical_threats": critical_threats,
            "open_incidents": open_incidents,
            "overdue_secret_rotations": overdue_secrets,
            "compliance": {r["status"]: r["cnt"] for r in compliance},
        }
