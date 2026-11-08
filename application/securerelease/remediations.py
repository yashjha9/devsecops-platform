from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, Remediation, AuditLog, User

remediations_bp = Blueprint(
    "remediations",
    __name__,
    url_prefix="/api/projects"
)

VALID_STATUSES = {"planned", "in_progress", "completed", "cancelled"}


def remediation_response(item):
    return {
        "id": item.id,
        "vulnerability_id": item.vulnerability_id,
        "assigned_to_id": item.assigned_to_id,
        "action_taken": item.action_taken,
        "status": item.status,
        "completed_at": (
            item.completed_at.isoformat() if item.completed_at else None
        )
    }


def get_owned_vulnerability(project_id, vulnerability_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return None

    return Vulnerability.query.filter_by(
        id=vulnerability_id,
        project_id=project.id
    ).first()


@remediations_bp.route(
    "/<int:project_id>/vulnerabilities/<int:vulnerability_id>/remediations",
    methods=["POST"]
)
@login_required
def create_remediation(project_id, vulnerability_id):
    vulnerability = get_owned_vulnerability(project_id, vulnerability_id)

    if not vulnerability:
        return jsonify({"error": "Project or vulnerability not found"}), 404

    data = request.get_json(silent=True) or {}
    action_taken = data.get("action_taken", "").strip()
    assigned_to_id = data.get("assigned_to_id")

    if not action_taken:
        return jsonify({"error": "Remediation action is required"}), 400

    if assigned_to_id is not None:
        if type(assigned_to_id) is not int:
            return jsonify({"error": "Invalid assigned user ID"}), 400

        assigned_user = db.session.get(User, assigned_to_id)

        if not assigned_user or not assigned_user.is_active:
            return jsonify({"error": "Assigned user not found or inactive"}), 404

    remediation = Remediation(
        vulnerability_id=vulnerability.id,
        assigned_to_id=assigned_to_id,
        action_taken=action_taken,
        status="planned"
    )

    db.session.add(remediation)
    db.session.flush()

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="remediation.created",
        entity_type="remediation",
        entity_id=remediation.id,
        details={"vulnerability_id": vulnerability.id}
    ))

    db.session.commit()

    return jsonify({
        "message": "Remediation action created successfully",
        "remediation": remediation_response(remediation)
    }), 201


@remediations_bp.route(
    "/<int:project_id>/vulnerabilities/<int:vulnerability_id>/remediations",
    methods=["GET"]
)
@login_required
def list_remediations(project_id, vulnerability_id):
    vulnerability = get_owned_vulnerability(project_id, vulnerability_id)

    if not vulnerability:
        return jsonify({"error": "Project or vulnerability not found"}), 404

    items = Remediation.query.filter_by(
        vulnerability_id=vulnerability.id
    ).order_by(Remediation.id.desc()).all()

    return jsonify({
        "count": len(items),
        "remediations": [remediation_response(item) for item in items]
    }), 200


@remediations_bp.route(
    "/<int:project_id>/vulnerabilities/<int:vulnerability_id>/remediations/<int:remediation_id>",
    methods=["PATCH"]
)
@login_required
def update_remediation(project_id, vulnerability_id, remediation_id):
    vulnerability = get_owned_vulnerability(project_id, vulnerability_id)

    if not vulnerability:
        return jsonify({"error": "Project or vulnerability not found"}), 404

    remediation = Remediation.query.filter_by(
        id=remediation_id,
        vulnerability_id=vulnerability.id
    ).first()

    if not remediation:
        return jsonify({"error": "Remediation not found"}), 404

    data = request.get_json(silent=True) or {}

    if "status" not in data:
        return jsonify({"error": "Remediation status is required"}), 400

    status = data["status"]

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid remediation status",
            "allowed_values": sorted(VALID_STATUSES)
        }), 400

    remediation.status = status

    if status == "completed":
        remediation.completed_at = datetime.now(timezone.utc)
        vulnerability.status = "resolved"
    else:
        remediation.completed_at = None

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="remediation.updated",
        entity_type="remediation",
        entity_id=remediation.id,
        details={
            "status": status,
            "vulnerability_id": vulnerability.id
        }
    ))

    db.session.commit()

    return jsonify({
        "message": "Remediation updated successfully",
        "remediation": remediation_response(remediation),
        "vulnerability_status": vulnerability.status
    }), 200
