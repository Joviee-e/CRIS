from .extensions import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def gen_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

class Application(db.Model):
    __tablename__ = "application"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    sr_no = db.Column(db.Integer)
    purpose = db.Column(db.String(500))
    department = db.Column(db.String(255))
    emp_no = db.Column(db.String(100))
    emp_name = db.Column(db.String(255))
    designation = db.Column(db.String(255))
    remarks = db.Column(db.Text)
    status = db.Column(db.String(50), default="submitted")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attachments = relationship("Attachment", back_populates="application")


class ActionLog(db.Model):
    __tablename__ = "action_log"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    application_id = db.Column(db.String, db.ForeignKey("application.id"))
    action = db.Column(db.String(50))
    user_id = db.Column(db.String)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="attachments")

