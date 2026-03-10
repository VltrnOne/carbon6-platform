"""Device Operations database layer - PostgreSQL with SQLAlchemy."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    Boolean, Float, JSON, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from ..config.settings import load_config

Base = declarative_base()


class DeviceSnapshot(Base):
    __tablename__ = "devops_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_type = Column(String(50), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id, "type": self.snapshot_type,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DeviceEvent(Base):
    __tablename__ = "devops_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default="info", index=True)
    data = Column(JSON, default=dict)
    acknowledged = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("ix_devops_events_type_time", "event_type", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id, "event_type": self.event_type,
            "severity": self.severity, "data": self.data,
            "acknowledged": self.acknowledged,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DeviceCommand(Base):
    __tablename__ = "devops_commands"

    id = Column(Integer, primary_key=True)
    subsystem = Column(String(30), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    status = Column(String(20), default="pending", index=True)
    result = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime)

    __table_args__ = (
        Index("ix_devops_commands_sub_time", "subsystem", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id, "subsystem": self.subsystem,
            "action": self.action, "payload": self.payload,
            "status": self.status, "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class LocationHistory(Base):
    __tablename__ = "devops_locations"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    address = Column(Text)
    accuracy = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id, "latitude": self.latitude,
            "longitude": self.longitude, "altitude": self.altitude,
            "address": self.address, "accuracy": self.accuracy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Geofence(Base):
    __tablename__ = "devops_geofences"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, nullable=False, default=100.0)
    on_enter_action = Column(JSON, default=dict)
    on_exit_action = Column(JSON, default=dict)
    active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "latitude": self.latitude, "longitude": self.longitude,
            "radius_meters": self.radius_meters,
            "on_enter_action": self.on_enter_action,
            "on_exit_action": self.on_exit_action,
            "active": self.active,
        }


class DeviceOpsDB:
    """Device Operations database manager."""

    def __init__(self):
        config = load_config()
        self.engine = create_engine(config.database.url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    # --- Snapshots ---

    def store_snapshot(self, snapshot_type: str, data: dict) -> int:
        with self.get_session() as session:
            snap = DeviceSnapshot(snapshot_type=snapshot_type, data=data)
            session.add(snap)
            session.commit()
            session.refresh(snap)
            return snap.id

    def get_latest_snapshot(self, snapshot_type: str) -> Optional[dict]:
        with self.get_session() as session:
            snap = (
                session.query(DeviceSnapshot)
                .filter(DeviceSnapshot.snapshot_type == snapshot_type)
                .order_by(DeviceSnapshot.created_at.desc())
                .first()
            )
            return snap.to_dict() if snap else None

    def get_snapshots(self, snapshot_type: str = None, limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(DeviceSnapshot)
            if snapshot_type:
                q = q.filter(DeviceSnapshot.snapshot_type == snapshot_type)
            return [s.to_dict() for s in q.order_by(DeviceSnapshot.created_at.desc()).limit(limit).all()]

    # --- Events ---

    def store_event(self, event_type: str, severity: str = "info", data: dict = None) -> int:
        with self.get_session() as session:
            evt = DeviceEvent(event_type=event_type, severity=severity, data=data or {})
            session.add(evt)
            session.commit()
            session.refresh(evt)
            return evt.id

    def get_events(self, event_type: str = None, severity: str = None,
                   unacknowledged: bool = False, limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(DeviceEvent)
            if event_type:
                q = q.filter(DeviceEvent.event_type == event_type)
            if severity:
                q = q.filter(DeviceEvent.severity == severity)
            if unacknowledged:
                q = q.filter(DeviceEvent.acknowledged == False)
            return [e.to_dict() for e in q.order_by(DeviceEvent.created_at.desc()).limit(limit).all()]

    def acknowledge_event(self, event_id: int) -> bool:
        with self.get_session() as session:
            evt = session.query(DeviceEvent).filter(DeviceEvent.id == event_id).first()
            if evt:
                evt.acknowledged = True
                session.commit()
                return True
            return False

    # --- Commands ---

    def store_command(self, subsystem: str, action: str, payload: dict = None) -> int:
        with self.get_session() as session:
            cmd = DeviceCommand(subsystem=subsystem, action=action, payload=payload or {})
            session.add(cmd)
            session.commit()
            session.refresh(cmd)
            return cmd.id

    def update_command(self, command_id: int, status: str, result: dict = None) -> bool:
        with self.get_session() as session:
            cmd = session.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
            if cmd:
                cmd.status = status
                cmd.result = result or {}
                if status in ("completed", "failed"):
                    cmd.completed_at = datetime.now(timezone.utc)
                session.commit()
                return True
            return False

    def get_commands(self, subsystem: str = None, status: str = None, limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(DeviceCommand)
            if subsystem:
                q = q.filter(DeviceCommand.subsystem == subsystem)
            if status:
                q = q.filter(DeviceCommand.status == status)
            return [c.to_dict() for c in q.order_by(DeviceCommand.created_at.desc()).limit(limit).all()]

    # --- Location ---

    def store_location(self, latitude: float, longitude: float,
                       altitude: float = None, address: str = None,
                       accuracy: float = None) -> int:
        with self.get_session() as session:
            loc = LocationHistory(
                latitude=latitude, longitude=longitude,
                altitude=altitude, address=address, accuracy=accuracy,
            )
            session.add(loc)
            session.commit()
            session.refresh(loc)
            return loc.id

    def get_location_history(self, limit: int = 100) -> list:
        with self.get_session() as session:
            return [
                l.to_dict() for l in
                session.query(LocationHistory)
                .order_by(LocationHistory.created_at.desc())
                .limit(limit).all()
            ]

    def get_latest_location(self) -> Optional[dict]:
        with self.get_session() as session:
            loc = session.query(LocationHistory).order_by(LocationHistory.created_at.desc()).first()
            return loc.to_dict() if loc else None

    # --- Geofences ---

    def add_geofence(self, name: str, latitude: float, longitude: float,
                     radius_meters: float = 100.0,
                     on_enter: dict = None, on_exit: dict = None) -> dict:
        with self.get_session() as session:
            gf = Geofence(
                name=name, latitude=latitude, longitude=longitude,
                radius_meters=radius_meters,
                on_enter_action=on_enter or {}, on_exit_action=on_exit or {},
            )
            session.add(gf)
            session.commit()
            session.refresh(gf)
            return gf.to_dict()

    def list_geofences(self, active_only: bool = True) -> list:
        with self.get_session() as session:
            q = session.query(Geofence)
            if active_only:
                q = q.filter(Geofence.active == True)
            return [g.to_dict() for g in q.all()]

    def delete_geofence(self, geofence_id: int) -> bool:
        with self.get_session() as session:
            gf = session.query(Geofence).filter(Geofence.id == geofence_id).first()
            if gf:
                session.delete(gf)
                session.commit()
                return True
            return False
