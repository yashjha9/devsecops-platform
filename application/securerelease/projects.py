import re

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Project, AuditLog

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def make_slug(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:120]


def project_response(project):
    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "description": project.description,
        "repository_url": project.repository_url,
        "owner_id": project.owner_id,
        "created_at": project.created_at.isoformat()
    }


@projects_bp.route("", methods=["POST"])
@login_required
def create_project():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    repository_url = data.get("repository_url", "").strip()

    if not name:
        return jsonify({"error": "Project name is required"}), 400

    if len(name) > 120:
        return jsonify({"error": "Project name must be 120 characters or fewer"}), 400

    if len(repository_url) > 500:
        return jsonify({"error": "Repository URL is too long"}), 400

    slug = make_slug(name)

    if not slug:
        return jsonify({"error": "Project name must contain letters or numbers"}), 400

    if Project.query.filter_by(slug=slug).first():
        return jsonify({"error": "A project with this name already exists"}), 409

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

    return jsonify({
        "message": "Project created successfully",
        "project": project_response(project)
    }), 201


@projects_bp.route("", methods=["GET"])
@login_required
def list_projects():
    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).order_by(Project.created_at.desc()).all()

    return jsonify({
        "projects": [project_response(project) for project in projects],
        "count": len(projects)
    }), 200


@projects_bp.route("/<int:project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    return jsonify({"project": project_response(project)}), 200
