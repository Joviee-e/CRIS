# D:\CRIS CLONE\CRIS\scripts\create_admin.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys as _sys
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User

def main():
    email = _sys.argv[1] if len(_sys.argv) > 1 else "admin@local"
    password = _sys.argv[2] if len(_sys.argv) > 2 else "adminpass"

    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"User with email {email} already exists (id={existing.id}, role={existing.role}).")
            return
        u = User(email=email, password_hash=generate_password_hash(password), role="admin")
        db.session.add(u)
        db.session.commit()
        print("Admin created:", u.id, email)

if __name__ == "__main__":
    main()
