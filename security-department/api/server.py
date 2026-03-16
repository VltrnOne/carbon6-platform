"""SENTINEL Security API - FastAPI REST endpoints.

Run: uvicorn security_department.api.server:app --host 127.0.0.1 --port 3300
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from security_department.engine.database import SecurityDB
from security_department.engine.threat_detector import ThreatDetector
from security_department.engine.vault_manager import VaultManager
from security_department.engine.log_analyzer import LogAnalyzer
from security_department.engine.compliance import ComplianceEngine
from security_department.engine.incident_response import IncidentResponder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sentinel.api")

app = FastAPI(
    title="SENTINEL Security API",
    description="Carbon6 Security Department - Automated threat detection, compliance, and incident response",
    version="1.0.0",
)

# Initialize engines
db = SecurityDB()
threats = ThreatDetector(db=db)
vault = VaultManager(db=db)
logs = LogAnalyzer(db=db)
compliance = ComplianceEngine(db=db)
incidents = IncidentResponder(db=db)


# ── Dashboard ────────────────────────────────────────────

@app.get("/api/security/status")
async def status():
    """Full security dashboard."""
    return {
        "agent": "SENTINEL",
        "department": "Security",
        "stats": db.stats(),
        "vault": vault.vault_status(),
    }


@app.get("/api/security/dashboard")
async def dashboard():
    """Comprehensive security dashboard."""
    return {
        "stats": db.stats(),
        "vault": vault.vault_status(),
        "logs_summary": logs.get_summary(),
        "open_incidents": db.get_incidents(status="open"),
        "open_threats": db.get_threats(status="open", limit=10),
        "recent_events": db.get_events(limit=20),
        "rotation_status": vault.get_rotation_status(),
    }


# ── Threat Detection ────────────────────────────────────

@app.post("/api/security/scan")
async def run_threat_scan():
    """Run a full threat detection scan."""
    detected = threats.scan_all()
    # Process each threat through incident response
    results = []
    for threat in detected:
        result = incidents.handle_threat(threat)
        results.append(result)
    return {
        "threats_detected": len(detected),
        "results": results,
    }


@app.get("/api/security/threats")
async def list_threats(status: Optional[str] = None, severity: Optional[str] = None,
                       limit: int = 50):
    return {"threats": db.get_threats(status=status, severity=severity, limit=limit)}


@app.post("/api/security/threats/{threat_id}/resolve")
async def resolve_threat(threat_id: int):
    db.resolve_threat(threat_id)
    return {"resolved": True}


# ── Log Analysis ────────────────────────────────────────

@app.get("/api/security/logs/analysis")
async def analyze_logs():
    """Full log analysis."""
    return logs.analyze_all()


@app.get("/api/security/logs/ssh")
async def analyze_ssh():
    return logs.analyze_ssh()


@app.get("/api/security/logs/nginx")
async def analyze_nginx():
    return logs.analyze_nginx()


@app.get("/api/security/logs/fail2ban")
async def analyze_fail2ban():
    return logs.analyze_fail2ban()


# ── Compliance ──────────────────────────────────────────

@app.post("/api/security/compliance/scan")
async def run_compliance():
    """Run full compliance check."""
    return compliance.run_all()


@app.get("/api/security/compliance")
async def get_compliance(category: Optional[str] = None):
    return {"checks": db.get_compliance(category=category)}


# ── Vault Management ────────────────────────────────────

@app.get("/api/security/vault/status")
async def vault_status():
    return vault.vault_status()


@app.post("/api/security/vault/verify")
async def vault_verify():
    """Verify vault integrity."""
    return vault.verify_integrity()


@app.get("/api/security/vault/secrets")
async def list_vault_secrets():
    """List secret names only (never values)."""
    return {"secrets": vault.list_secrets()}


@app.get("/api/security/vault/rotation")
async def rotation_status():
    return vault.get_rotation_status()


@app.post("/api/security/vault/rotation/init")
async def init_rotation():
    """Initialize rotation tracking for all vault secrets."""
    return vault.init_rotation_tracking()


class RotateSecret(BaseModel):
    name: str
    new_value: str


@app.post("/api/security/vault/rotate")
async def rotate_secret(req: RotateSecret):
    return vault.rotate_secret(req.name, req.new_value)


# ── Incidents ───────────────────────────────────────────

@app.get("/api/security/incidents")
async def list_incidents(status: Optional[str] = None, limit: int = 20):
    return {"incidents": db.get_incidents(status=status, limit=limit)}


@app.get("/api/security/incidents/{incident_id}")
async def get_incident(incident_id: int):
    incs = db.get_incidents()
    for inc in incs:
        if inc["id"] == incident_id:
            return inc
    raise HTTPException(status_code=404, detail="Incident not found")


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    remediation_steps: Optional[str] = None
    assigned_to: Optional[str] = None


@app.patch("/api/security/incidents/{incident_id}")
async def update_incident(incident_id: int, update: IncidentUpdate):
    kwargs = {k: v for k, v in update.dict().items() if v is not None}
    db.update_incident(incident_id, **kwargs)
    return {"updated": True}


# ── Events ──────────────────────────────────────────────

@app.get("/api/security/events")
async def list_events(event_type: Optional[str] = None, severity: Optional[str] = None,
                      limit: int = 50):
    return {"events": db.get_events(event_type=event_type, severity=severity, limit=limit)}


@app.post("/api/security/events/{event_id}/resolve")
async def resolve_event(event_id: int):
    db.resolve_event(event_id)
    return {"resolved": True}
