from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager
from .models import User

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
