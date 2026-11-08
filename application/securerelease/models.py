from datetime import datetime, timezone

from flask_login import UserMixin

from . import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="developer")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    projects = db.relationship("Project", back_populates="owner")
    deployments = db.relationship("Deployment", back_populates="triggered_by")
    audit_logs = db.relationship("AuditLog", back_populates="user")


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    repository_url = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    owner = db.relationship("User", back_populates="projects")
    vulnerabilities = db.relationship(
        "Vulnerability", back_populates="project",
        cascade="all, delete-orphan"
    )
    deployments = db.relationship(
        "Deployment", back_populates="project",
        cascade="all, delete-orphan"
    )


class Vulnerability(db.Model):
    __tablename__ = "vulnerabilities"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    scanner = db.Column(db.String(80), nullable=False)
    external_id = db.Column(db.String(150))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="open")
    cvss_score = db.Column(db.Float)
    exploitability_score = db.Column(db.Float)
    component = db.Column(db.String(255))
    first_seen = db.Column(db.DateTime(timezone=True), default=utc_now)
    last_seen = db.Column(db.DateTime(timezone=True), default=utc_now)

    project = db.relationship("Project", back_populates="vulnerabilities")
    remediations = db.relationship(
        "Remediation", back_populates="vulnerability",
        cascade="all, delete-orphan"
    )


class Remediation(db.Model):
    __tablename__ = "remediations"

    id = db.Column(db.Integer, primary_key=True)
    vulnerability_id = db.Column(
        db.Integer, db.ForeignKey("vulnerabilities.id"), nullable=False
    )
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action_taken = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="planned")
    completed_at = db.Column(db.DateTime(timezone=True))

    vulnerability = db.relationship("Vulnerability", back_populates="remediations")
    assigned_to = db.relationship("User")


class Deployment(db.Model):
    __tablename__ = "deployments"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    triggered_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    risk_score = db.Column(db.Float)
    decision = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    project = db.relationship("Project", back_populates="deployments")
    triggered_by = db.relationship("User", back_populates="deployments")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    user = db.relationship("User", back_populates="audit_logs")
