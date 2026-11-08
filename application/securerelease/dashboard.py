
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .models import (
    Project,
    Vulnerability,
    Remediation,
    Deployment
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    # Get projects owned by the logged-in user.
    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).all()

    project_ids = [project.id for project in projects]

    # Count projects.
    total_projects = len(projects)

    # Count unresolved vulnerabilities.
    open_vulnerabilities = Vulnerability.query.filter(
        Vulnerability.project_id.in_(project_ids),
        Vulnerability.status.in_(["open", "in_progress"])
    ).count() if project_ids else 0

    # Count vulnerabilities by severity.
    severity_counts = {}

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"]:
        severity_counts[severity] = Vulnerability.query.filter(
            Vulnerability.project_id.in_(project_ids),
            Vulnerability.severity == severity,
            Vulnerability.status.in_(["open", "in_progress"])
        ).count() if project_ids else 0

    # Count completed remediations.
    completed_remediations = Remediation.query.join(
        Vulnerability
    ).filter(
        Vulnerability.project_id.in_(project_ids),
        Remediation.status == "completed"
    ).count() if project_ids else 0

    # Count deployment decisions.
    deployments = Deployment.query.filter(
        Deployment.project_id.in_(project_ids)
    ).order_by(
        Deployment.created_at.desc()
    ).limit(5).all() if project_ids else []

    total_deployments = Deployment.query.filter(
        Deployment.project_id.in_(project_ids)
    ).count() if project_ids else 0

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        open_vulnerabilities=open_vulnerabilities,
        completed_remediations=completed_remediations,
        total_deployments=total_deployments,
        severity_counts=severity_counts,
        recent_deployments=deployments,
        username=current_user.username
    )
