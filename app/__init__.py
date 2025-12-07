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
        # config_object may be a class or mapping (tests pass a class)
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

    # --- TESTING helper: create tables automatically for in-memory testing DBs ---
    # Ensure this covers both ways tests configure the app:
    # 1) Tests pass a TestConfig to create_app(TestConfig) -> config_object set
    # 2) Tests call create_app() then app.config.update(...) -> SQLALCHEMY_DATABASE_URI updated later,
    #    but those tests usually create tables themselves in fixtures; we only auto-create here
    #    when the factory already sees TESTING or detects an in-memory DB config_object.
    try:
        should_create = False

        # If a config_object was passed and it signals testing, create
        if config_object and getattr(config_object, "TESTING", False):
            should_create = True

        # Or if the app config is already testing (covers create_app(TestConfig) or explicit TESTING)
        if app.config.get("TESTING"):
            should_create = True

        # Also create if the DB is clearly an in-memory sqlite URI (convenience)
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "") or ""
        if db_uri.strip().startswith("sqlite:///:memory:"):
            should_create = True

        if should_create:
            with app.app_context():
                db.create_all()
    except Exception:
        # log but do not crash the factory — keep behavior non-fatal
        app.logger.exception("Failed to create DB tables during TESTING/init-time helper")

    return app

__all__ = ["create_app"]
