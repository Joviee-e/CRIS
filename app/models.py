from .extensions import db
from datetime import datetime
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def gen_uuid():
    return str(uuid.uuid4())


# ==========================
# USER MODEL
# ==========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Methods must be INSIDE class
    def set_password(self, raw_password):
        self.password_hash = pwd_context.hash(raw_password)

    def check_password(self, raw_password):
        return pwd_context.verify(raw_password, self.password_hash)


# ==========================
# APPLICATION MODEL
# ==========================
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    sr_no = db.Column(db.Integer)
    purpose = db.Column(db.String(200))
    department = db.Column(db.String(100))
    emp_no = db.Column(db.String(50))
    emp_name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    remarks = db.Column(db.String(255))
    status = db.Column(db.String(20), default="submitted")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship → attachments
    attachments = db.relationship(
        "Attachment",
        backref="application",
        cascade="all, delete-orphan",
        lazy=True
    )


# ==========================
# ATTACHMENT MODEL
# ==========================
class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False
    )


# ==========================
# ACTION LOG MODEL
# ==========================
class ActionLog(db.Model):
    __tablename__ = "action_log"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    application_id = db.Column(db.String, db.ForeignKey("applications.id"))
    action = db.Column(db.String(50))
    user_id = db.Column(db.String)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
