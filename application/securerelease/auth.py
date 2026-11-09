from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import secrets

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from . import db, login_manager
from .models import User, Project, ProjectAPIToken, AuditLog

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required"}), 400

    if len(password) < 12:
        return jsonify({"error": "Password must be at least 12 characters"}), 400

    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return jsonify({"error": "Username or email already exists"}), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403

    login_user(user)
    return jsonify({"message": "Login successful"}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }), 200

@auth_bp.route(
    "/projects/<int:project_id>/tokens",
    methods=["POST"]
)
@login_required
def create_project_token(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name", "GitHub Actions")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "A valid token name is required"}), 400

    if len(name.strip()) > 100:
        return jsonify({"error": "Token name must be 100 characters or fewer"}), 400

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    api_token = ProjectAPIToken(
        user_id=current_user.id,
        project_id=project.id,
        token_hash=token_hash,
        name=name.strip()
    )

    db.session.add(api_token)

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="api_token.created",
        entity_type="project",
        entity_id=project.id,
        details={"token_name": name.strip()}
    ))

    db.session.commit()

    return jsonify({
        "message": "API token created. Save it securely; it will not be shown again.",
        "token": raw_token,
        "project_id": project.id,
        "token_name": api_token.name
    }), 201
