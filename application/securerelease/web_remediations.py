
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, Remediation, AuditLog

web_remediations_bp = Blueprint("web_remediations", __name__)


@web_remediations_bp.route(
    "/projects/<int:project_id>/remediations",
    methods=["GET", "POST"]
)
@login_required
def list_remediations(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        vulnerability_id = request.form.get("vulnerability_id", type=int)
        action_taken = request.form.get("action_taken", "").strip()

        vulnerability = Vulnerability.query.filter_by(
            id=vulnerability_id,
            project_id=project.id
        ).first()

        if not vulnerability:
            flash("Invalid vulnerability selected.", "danger")
            return redirect(url_for(
                "web_remediations.list_remediations",
                project_id=project.id
            ))

        if not action_taken:
            flash("Remediation action is required.", "danger")
            return redirect(url_for(
                "web_remediations.list_remediations",
                project_id=project.id
            ))

        remediation = Remediation(
            vulnerability_id=vulnerability.id,
            assigned_to_id=current_user.id,
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
            details={
                "vulnerability_id": vulnerability.id,
                "project_id": project.id
            }
        ))

        db.session.commit()

        flash("Remediation task created successfully.", "success")

        return redirect(url_for(
            "web_remediations.list_remediations",
            project_id=project.id
        ))

    findings = Vulnerability.query.filter_by(
        project_id=project.id
    ).order_by(Vulnerability.severity.asc()).all()

    remediations = Remediation.query.join(
        Vulnerability
    ).filter(
        Vulnerability.project_id == project.id
    ).order_by(
        Remediation.id.desc()
    ).all()

    return render_template(
        "remediations.html",
        project=project,
        findings=findings,
        remediations=remediations
    )


@web_remediations_bp.route(
    "/projects/<int:project_id>/remediations/<int:remediation_id>/status",
    methods=["POST"]
)
@login_required
def update_status(project_id, remediation_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    remediation = Remediation.query.join(
        Vulnerability
    ).filter(
        Remediation.id == remediation_id,
        Vulnerability.project_id == project.id
    ).first_or_404()

    status = request.form.get("status", "")

    valid_statuses = {
        "planned", "in_progress", "completed", "cancelled"
    }

    if status not in valid_statuses:
        flash("Invalid remediation status.", "danger")
        return redirect(url_for(
            "web_remediations.list_remediations",
            project_id=project.id
        ))

    remediation.status = status

    if status == "completed":
        remediation.completed_at = datetime.now(timezone.utc)
        remediation.vulnerability.status = "resolved"
    else:
        remediation.completed_at = None

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="remediation.updated",
        entity_type="remediation",
        entity_id=remediation.id,
        details={
            "status": status,
            "vulnerability_id": remediation.vulnerability_id
        }
    ))

    db.session.commit()

    flash("Remediation status updated successfully.", "success")

    return redirect(url_for(
        "web_remediations.list_remediations",
        project_id=project.id
    ))
