from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, Deployment, AuditLog

deployments_bp = Blueprint(
    "deployments",
    __name__,
    url_prefix="/api/projects"
)

SEVERITY_BASE_SCORES = {
    "INFO": 5,
    "LOW": 15,
    "MEDIUM": 35,
    "HIGH": 70,
    "CRITICAL": 100
}

DEFAULT_EXPLOITABILITY = 5.0


def calculate_finding_risk(finding):
    severity_score = SEVERITY_BASE_SCORES.get(
        (finding.severity or "").upper()
    )

    # Unknown or unsupported severity requires manual review.
    if severity_score is None:
        return None

    exploitability = finding.exploitability_score

    if exploitability is None:
        exploitability = DEFAULT_EXPLOITABILITY

    risk_score = severity_score * (0.5 + exploitability / 20)

    return round(min(risk_score, 100), 2)


def evaluate_project_risk(project_id):
    findings = Vulnerability.query.filter(
        Vulnerability.project_id == project_id,
        Vulnerability.status.in_(["open", "in_progress"])
    ).all()

    finding_risks = [
        {
            "vulnerability_id": finding.id,
            "title": finding.title,
            "severity": finding.severity,
            "risk_score": calculate_finding_risk(finding)
        }
        for finding in findings
    ]

    numeric_risks = [
        item["risk_score"]
        for item in finding_risks
        if item["risk_score"] is not None
    ]

    overall_risk = max(numeric_risks, default=0)

    has_unknown_severity = any(
        item["risk_score"] is None
        for item in finding_risks
    )

    if overall_risk >= 60:
        decision = "BLOCK"
    elif overall_risk >= 30 or has_unknown_severity:
        decision = "REVIEW"
    else:
        decision = "ALLOW"

    return overall_risk, decision, finding_risks

@deployments_bp.route(
    "/<int:project_id>/deployments",
    methods=["POST"]
)
@login_required
def evaluate_deployment(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}
    version = data.get("version", "").strip()

    if not version:
        return jsonify({"error": "Deployment version is required"}), 400

    if len(version) > 80:
        return jsonify({"error": "Deployment version is too long"}), 400

    risk_score, decision, finding_risks = evaluate_project_risk(
        project.id
    )

    deployment = Deployment(
        project_id=project.id,
        triggered_by_id=current_user.id,
        version=version,
        risk_score=risk_score,
        decision=decision,
        status="decision_recorded"
    )

    db.session.add(deployment)
    db.session.flush()

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="deployment.evaluated",
        entity_type="deployment",
        entity_id=deployment.id,
        details={
            "version": version,
            "risk_score": risk_score,
            "decision": decision,
            "finding_count": len(finding_risks)
        }
    ))

    db.session.commit()

    return jsonify({
        "message": "Deployment risk evaluation completed",
        "deployment": {
            "id": deployment.id,
            "project_id": project.id,
            "version": deployment.version,
            "risk_score": deployment.risk_score,
            "decision": deployment.decision,
            "status": deployment.status,
            "finding_count": len(finding_risks)
        },
        "findings": finding_risks
    }), 201


@deployments_bp.route(
    "/<int:project_id>/deployments",
    methods=["GET"]
)
@login_required
def list_deployments(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    records = Deployment.query.filter_by(
        project_id=project.id
    ).order_by(Deployment.created_at.desc()).all()

    return jsonify({
        "count": len(records),
        "deployments": [
            {
                "id": item.id,
                "version": item.version,
                "risk_score": item.risk_score,
                "decision": item.decision,
                "status": item.status,
                "created_at": item.created_at.isoformat()
            }
            for item in records
        ]
    }), 200
