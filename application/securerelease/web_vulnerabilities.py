
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, AuditLog

web_vulnerabilities_bp = Blueprint("web_vulnerabilities", __name__)


@web_vulnerabilities_bp.route(
    "/projects/<int:project_id>/vulnerabilities",
    methods=["GET"]
)
@login_required
def list_vulnerabilities(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    findings = Vulnerability.query.filter_by(
        project_id=project.id
    ).order_by(
        Vulnerability.first_seen.desc()
    ).all()

    severity_counts = {
        severity: sum(
            1 for finding in findings
            if finding.severity == severity
        )
        for severity in [
            "CRITICAL", "HIGH", "MEDIUM",
            "LOW", "INFO", "UNKNOWN"
        ]
    }

    return render_template(
        "vulnerabilities.html",
        project=project,
        findings=findings,
        severity_counts=severity_counts
    )


@web_vulnerabilities_bp.route(
    "/projects/<int:project_id>/vulnerabilities/<int:vulnerability_id>/status",
    methods=["POST"]
)
@login_required
def update_status(project_id, vulnerability_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    finding = Vulnerability.query.filter_by(
        id=vulnerability_id,
        project_id=project.id
    ).first_or_404()

    status = request.form.get("status", "")

    valid_statuses = {
        "open", "in_progress", "resolved", "accepted"
    }

    if status not in valid_statuses:
        flash("Invalid vulnerability status.", "danger")
        return redirect(
            url_for(
                "web_vulnerabilities.list_vulnerabilities",
                project_id=project.id
            )
        )

    finding.status = status

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="vulnerability.updated",
        entity_type="vulnerability",
        entity_id=finding.id,
        details={
            "status": status,
            "project_id": project.id
        }
    ))

    db.session.commit()

    flash("Vulnerability status updated successfully.", "success")

    return redirect(
        url_for(
            "web_vulnerabilities.list_vulnerabilities",
            project_id=project.id
        )
    )
