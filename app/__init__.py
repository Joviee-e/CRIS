from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors, limiter, logger_setup
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Optional: Oracle Instant Client
    if os.getenv("ORACLE_INSTANT_CLIENT_DIR"):
        import oracledb
        oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_INSTANT_CLIENT_DIR"))

    logger_setup(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": app.config.get("CORS_ORIGINS").split(",")}},
    )
    limiter.init_app(app)

    # ✅ Blueprints (ALL REGISTERED)
    from app.routes.auth import auth_bp
    from app.routes.applications import app_bp
    from app.routes.attachments import attachments_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(app_bp, url_prefix="/api/applications")
    app.register_blueprint(attachments_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
