from .applications import app_bp
from .auth import auth_bp
from .attachments import attachments_bp

def register_routes(app):
    app.register_blueprint(app_bp, url_prefix="/api/applications")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(attachments_bp, url_prefix="/api")
