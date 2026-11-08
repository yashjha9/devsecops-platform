from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, AuditLog

vulnerabilities_bp = Blueprint(
    "vulnerabilities",
    __name__,
    url_prefix="/api/projects"
)

VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_STATUSES = {"open", "in_progress", "resolved", "accepted"}


def vulnerability_response(item):
    return {
        "id": item.id,
        "project_id": item.project_id,
        "scanner": item.scanner,
        "external_id": item.external_id,
        "title": item.title,
        "description": item.description,
        "severity": item.severity,
        "status": item.status,
        "cvss_score": item.cvss_score,
        "exploitability_score": item.exploitability_score,
        "component": item.component,
        "first_seen": item.first_seen.isoformat(),
        "last_seen": item.last_seen.isoformat()
    }


@vulnerabilities_bp.route(
    "/<int:project_id>/vulnerabilities",
    methods=["POST"]
)
@login_required
def create_vulnerability(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}

    scanner = data.get("scanner", "").strip()
    title = data.get("title", "").strip()
    severity = data.get("severity", "").strip().upper()

    if not scanner or not title or not severity:
        return jsonify({
            "error": "Scanner, title and severity are required"
        }), 400

    if severity not in VALID_SEVERITIES:
        return jsonify({
            "error": "Invalid severity",
            "allowed_values": sorted(VALID_SEVERITIES)
        }), 400

    try:
        cvss_score = data.get("cvss_score")
        exploitability_score = data.get("exploitability_score")

        if cvss_score is not None:
            cvss_score = float(cvss_score)
            if not 0 <= cvss_score <= 10:
                raise ValueError()

        if exploitability_score is not None:
            exploitability_score = float(exploitability_score)
            if not 0 <= exploitability_score <= 10:
                raise ValueError()

    except (TypeError, ValueError):
        return jsonify({
            "error": "CVSS and exploitability scores must be between 0 and 10"
        }), 400

    item = Vulnerability(
        project_id=project.id,
        scanner=scanner,
        external_id=data.get("external_id"),
        title=title,
        description=data.get("description"),
        severity=severity,
        cvss_score=cvss_score,
        exploitability_score=exploitability_score,
        component=data.get("component")
    )

    db.session.add(item)
    db.session.flush()

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="vulnerability.created",
        entity_type="vulnerability",
        entity_id=item.id,
        details={
            "project_id": project.id,
            "severity": severity,
            "scanner": scanner
        }
    ))

    db.session.commit()

    return jsonify({
        "message": "Vulnerability recorded successfully",
        "vulnerability": vulnerability_response(item)
    }), 201


@vulnerabilities_bp.route(
    "/<int:project_id>/vulnerabilities",
    methods=["GET"]
)
@login_required
def list_vulnerabilities(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    findings = Vulnerability.query.filter_by(
        project_id=project.id
    ).order_by(Vulnerability.first_seen.desc()).all()

    return jsonify({
        "project_id": project.id,
        "count": len(findings),
        "vulnerabilities": [
            vulnerability_response(item) for item in findings
        ]
    }), 200


@vulnerabilities_bp.route(
    "/<int:project_id>/vulnerabilities/<int:vulnerability_id>",
    methods=["PATCH"]
)
@login_required
def update_vulnerability(project_id, vulnerability_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    item = Vulnerability.query.filter_by(
        id=vulnerability_id,
        project_id=project.id
    ).first()

    if not item:
        return jsonify({"error": "Vulnerability not found"}), 404

    data = request.get_json(silent=True) or {}

    if "status" in data:
        status = data["status"]

        if status not in VALID_STATUSES:
            return jsonify({
                "error": "Invalid status",
                "allowed_values": sorted(VALID_STATUSES)
            }), 400

        item.status = status

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="vulnerability.updated",
        entity_type="vulnerability",
        entity_id=item.id,
        details={"status": item.status}
    ))

    db.session.commit()

    return jsonify({
        "message": "Vulnerability updated successfully",
        "vulnerability": vulnerability_response(item)
    }), 200
