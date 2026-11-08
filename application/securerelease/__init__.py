import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
   )

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-only-change-this-secret"
    )

    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        database_path = os.path.join(app.instance_path, "securerelease.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + database_path.replace("\\", "/")
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "web_auth.login"

    from . import models
    from .auth import auth_bp
    from .projects import projects_bp
    from .vulnerabilities import vulnerabilities_bp
    from .remediations import remediations_bp
    from .deployments import deployments_bp
    from .scanner_ingestion import scanner_bp
    from .dashboard import dashboard_bp
    from .web_auth import web_auth_bp
    from .web_projects import web_projects_bp
    from .web_vulnerabilities import web_vulnerabilities_bp
    from .web_remediations import web_remediations_bp
    from .web_deployments import web_deployments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(vulnerabilities_bp)
    app.register_blueprint(remediations_bp)
    app.register_blueprint(deployments_bp)
    app.register_blueprint(scanner_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(web_auth_bp)
    app.register_blueprint(web_projects_bp)
    app.register_blueprint(web_vulnerabilities_bp)
    app.register_blueprint(web_remediations_bp)
    app.register_blueprint(web_deployments_bp)

    with app.app_context():
        db.create_all()

    return app
