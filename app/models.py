# app/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    
    def set_password(self, raw_password: str) -> None:
        """
        Hash and set the user's password.
        """
        if raw_password is None:
            raise ValueError("Password cannot be None")
        # method uses pbkdf2:sha256 by default via werkzeug
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        Verify provided password against stored hash.
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)



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
    # initial state is "submitted" for the workflow
    status = Column(String(50), nullable=False, default="submitted")
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", backref="applications", lazy="joined")
    attachments = relationship("Attachment", back_populates="application", lazy="joined")

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

    # Relationships
    application = relationship("Application", backref="action_logs", lazy="joined")
    actor = relationship("User", lazy="joined")

    def to_dict(self):
        # actor_role is derived from the related User (no schema change needed)
        actor_role = self.actor.role if self.actor else None
        return {
            "id": self.id,
            "application_id": self.application_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "actor_role": actor_role,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# -----------------------
# Attachment model
# -----------------------
class Attachment(db.Model):
    __tablename__ = "attachments"

    # Use UUID string primary key for Oracle-friendly, consistent IDs
    id = Column(String(36), primary_key=True, default=gen_uuid, unique=True, nullable=False, index=True)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="attachments", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "size": self.size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
