from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

web_auth_bp = Blueprint("web_auth", __name__)


@web_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(
            user.password_hash, password
        ):
            flash("Invalid username or password.", "danger")
            return render_template("login.html"), 401

        if not user.is_active:
            flash("Your account is inactive.", "danger")
            return render_template("login.html"), 403

        login_user(user)
        flash("Login successful.", "success")

        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


@web_auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html"), 400

        if len(password) < 12:
            flash("Password must contain at least 12 characters.", "danger")
            return render_template("register.html"), 400

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.", "danger")
            return render_template("register.html"), 409

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role="developer"
        )

        db.session.add(user)
        db.session.commit()
        print(
    "REGISTRATION DEBUG:",
    "User ID:", user.id,
    "Username:", user.username,
    "Database:", db.engine.url.database,
    "User count:", User.query.count()
  )

        flash("Account created. Please log in.", "success")
        return redirect(url_for("web_auth.login"))

    return render_template("register.html")


@web_auth_bp.route("/web-logout", methods=["POST"])
def web_logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "success")

    return redirect(url_for("web_auth.login"))
