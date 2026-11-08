
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Project, Deployment, AuditLog
from .deployments import evaluate_project_risk

web_deployments_bp = Blueprint("web_deployments", __name__)


@web_deployments_bp.route(
    "/projects/<int:project_id>/deployments",
    methods=["GET", "POST"]
)
@login_required
def list_deployments(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        version = request.form.get("version", "").strip()

        if not version:
            flash("Deployment version is required.", "danger")
            return redirect(url_for(
                "web_deployments.list_deployments",
                project_id=project.id
            ))

        if len(version) > 80:
            flash("Deployment version is too long.", "danger")
            return redirect(url_for(
                "web_deployments.list_deployments",
                project_id=project.id
            ))

        risk_score, decision, findings = evaluate_project_risk(
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
                "finding_count": len(findings)
            }
        ))

        db.session.commit()

        flash(
            f"Risk evaluation completed: {decision} "
            f"(Risk score: {risk_score})",
            "success"
        )

        return redirect(url_for(
            "web_deployments.list_deployments",
            project_id=project.id
        ))

    deployments = Deployment.query.filter_by(
        project_id=project.id
    ).order_by(
        Deployment.created_at.desc()
    ).all()

    risk_score, decision, findings = evaluate_project_risk(
        project.id
    )

    return render_template(
        "deployments.html",
        project=project,
        deployments=deployments,
        risk_score=risk_score,
        decision=decision,
        findings=findings
    )
