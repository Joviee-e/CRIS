
# app/__init__.py
"""
Application package initializer and app factory.
"""

import os
from flask import Flask, Blueprint
from .config import Config
from .extensions import db, migrate, jwt, cors, limiter, logger_setup

def _clone_blueprint(bp: Blueprint, new_name: str) -> Blueprint:
    """
    Create a shallow clone of a Blueprint so it can be registered again
    under a different name / url_prefix.
    """
    new_bp = Blueprint(new_name, bp.import_name, url_prefix=bp.url_prefix,
                       template_folder=bp.template_folder, static_folder=bp.static_folder)
    # copy deferred functions so route registration is duplicated
    new_bp.deferred_functions = list(bp.deferred_functions)
    return new_bp

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=False)

    # load config
    if config_object:
        # allow either a config object or a plain dict
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    # optional Oracle client init (non-fatal)
    if os.getenv("ORACLE_INSTANT_CLIENT_DIR"):
        try:
            import oracledb
            oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_INSTANT_CLIENT_DIR"))
        except Exception:
            app.logger.exception("Oracle client init failed (ignored)")

    # setup logger + extensions
    logger_setup(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors_origins = app.config.get("CORS_ORIGINS") or ""
    try:
        origins = [o for o in (cors_origins.split(",") if cors_origins else []) if o]
        cors.init_app(app, resources={r"/*": {"origins": origins or ["*"]}})
    except Exception:
        app.logger.exception("Failed to init CORS (continuing)")

    limiter.init_app(app)
    app.limiter = limiter

    # import blueprints
    from app.routes.auth import auth_bp, admin_bp
    from app.routes.applications import app_bp

    # Register canonical blueprints under API prefixes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(app_bp, url_prefix="/api/applications")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Register short aliases for legacy/tests (clone so blueprint name conflict avoided)
    try:
        auth_short = _clone_blueprint(auth_bp, new_name="auth_bp_short")
        app.register_blueprint(auth_short, url_prefix="/auth")
    except Exception:
        app.logger.exception("Failed to clone/register /auth alias")

    try:
        admin_short = _clone_blueprint(admin_bp, new_name="admin_bp_short")
        app.register_blueprint(admin_short, url_prefix="/admin")
    except Exception:
        app.logger.exception("Failed to clone/register /admin alias")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    # ------------------------------
    # AUTO-CREATE TABLES FOR TESTING
    # ------------------------------
    # Create tables automatically under test runs so pytest won't fail
    # when tests call create_app() before injecting test config.
    #
    # Conditions we consider "test mode":
    #  - app.config["TESTING"] is truthy
    #  - using in-memory sqlite (sqlite:///:memory:)
    #  - running under pytest (env var PYTEST_CURRENT_TEST present)
    try:
        testing_flag = bool(app.config.get("TESTING"))
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
        use_in_memory_sqlite = isinstance(db_uri, str) and db_uri.startswith("sqlite:///:memory:")
        running_under_pytest = os.getenv("PYTEST_CURRENT_TEST") is not None

        if testing_flag or use_in_memory_sqlite or running_under_pytest:
            with app.app_context():
                db.create_all()
                app.logger.debug("db.create_all() executed for test mode (TESTING=%s, in_memory=%s, pytest=%s)",
                                 testing_flag, use_in_memory_sqlite, running_under_pytest)
    except Exception:
        # don't let table creation break the app factory — log and continue
        app.logger.exception("Auto-create tables failed (continuing)")

    return app

__all__ = ["create_app"]
