
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Project, AuditLog

web_projects_bp = Blueprint("web_projects", __name__)


def make_slug(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:120]


@web_projects_bp.route("/projects")
@login_required
def list_projects():
    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).order_by(Project.created_at.desc()).all()

    return render_template(
        "projects.html",
        projects=projects
    )


@web_projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def create_project():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        repository_url = request.form.get("repository_url", "").strip()

        if not name:
            flash("Project name is required.", "danger")
            return render_template("project_form.html")

        if len(name) > 120:
            flash("Project name must not exceed 120 characters.", "danger")
            return render_template("project_form.html")

        if len(description) > 5000:
            flash("Project description is too long.", "danger")
            return render_template("project_form.html")

        if len(repository_url) > 500:
            flash("Repository URL is too long.", "danger")
            return render_template("project_form.html")

        slug = make_slug(name)

        if not slug:
            flash("Project name must contain letters or numbers.", "danger")
            return render_template("project_form.html")

        if Project.query.filter_by(slug=slug).first():
            flash("A project with this name already exists.", "danger")
            return render_template("project_form.html")

        project = Project(
            name=name,
            slug=slug,
            description=description,
            repository_url=repository_url or None,
            owner_id=current_user.id
        )

        db.session.add(project)
        db.session.flush()

        db.session.add(AuditLog(
            user_id=current_user.id,
            action="project.created",
            entity_type="project",
            entity_id=project.id,
            details={"name": project.name}
        ))

        db.session.commit()

        flash("Project created successfully.", "success")
        return redirect(
            url_for("web_projects.project_detail", project_id=project.id)
        )

    return render_template("project_form.html")


@web_projects_bp.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    return render_template(
        "project_detail.html",
        project=project
    )
