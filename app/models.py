# app/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

# Import the db instance from extensions (must exist)
from app.extensions import db

def gen_uuid():
    return str(uuid.uuid4())

# -----------------------
# User model
# -----------------------
class User(db.Model):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=gen_uuid, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="user", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# -----------------------
# Application model
# -----------------------
class Application(db.Model):
    __tablename__ = "applications"
    id = Column(String(36), primary_key=True, default=gen_uuid, unique=True, nullable=False)
    sr_no = Column(Integer, nullable=False, index=True)
    purpose = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    emp_no = Column(String(100), nullable=False)
    emp_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", backref="applications", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "sr_no": self.sr_no,
            "purpose": self.purpose,
            "department": self.department,
            "emp_no": self.emp_no,
            "emp_name": self.emp_name,
            "designation": self.designation,
            "remarks": self.remarks,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# -----------------------
# ActionLog model
# -----------------------
class ActionLog(db.Model):
    __tablename__ = "action_logs"
    id = Column(String(36), primary_key=True, default=gen_uuid, unique=True, nullable=False)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", backref="action_logs", lazy="joined")
    actor = relationship("User", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
