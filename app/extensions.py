from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import structlog

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

def logger_setup(app):
    logging.basicConfig(level="INFO")
    structlog.configure(processors=[structlog.processors.KeyValueRenderer()])
    app.logger = structlog.get_logger()
