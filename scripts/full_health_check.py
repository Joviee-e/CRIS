# D:\CRIS CLONE\CRIS\scripts\full_health_check.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Runs automated smoke checks using Flask test_client.
"""
import json
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User

def pretty_print(title, ok, details=""):
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {title} {details}")

def main():
    app = create_app()
    test_email = "smoke_test_user@example.com"
    test_password = "pass1234"
    admin_email = "smoke_admin@example.com"
    admin_password = "adminpass"

    with app.app_context():
        client = app.test_client()

        # Health
        r = client.get("/health")
        pretty_print("Health endpoint", r.status_code == 200, f"status={r.status_code} body={r.get_data(as_text=True)}")

        # Ensure the test user doesn't exist
        u = User.query.filter_by(email=test_email).first()
        if u:
            db.session.delete(u)
            db.session.commit()

        # Register
        r = client.post("/api/auth/register", json={"email": test_email, "password": test_password})
        reg_ok = r.status_code in (200, 201)
        pretty_print("Register", reg_ok, f"code={r.status_code} body={r.get_data(as_text=True)}")

        # Login
        r = client.post("/api/auth/login", json={"email": test_email, "password": test_password})
        login_ok = r.status_code == 200
        pretty_print("Login", login_ok, f"code={r.status_code} body={r.get_data(as_text=True)}")
        access_token = r.get_json().get("access_token") if login_ok else None

        # Create admin if needed
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, password_hash=generate_password_hash(admin_password), role="admin")
            db.session.add(admin)
            db.session.commit()
            pretty_print("Admin creation", True, f"id={admin.id}")
        else:
            pretty_print("Admin exists", True, f"id={admin.id}, role={admin.role}")

        # Admin login
        r = client.post("/api/auth/login", json={"email": admin_email, "password": admin_password})
        admin_login_ok = r.status_code == 200
        pretty_print("Admin login", admin_login_ok, f"code={r.status_code} body={r.get_data(as_text=True)}")
        admin_token = r.get_json().get("access_token") if admin_login_ok else None

        # Promote test user (if admin_token present)
        if admin_token and access_token:
            user = User.query.filter_by(email=test_email).first()
            if user:
                headers = {"Authorization": f"Bearer {admin_token}"}
                r = client.post("/api/admin/promote", json={"user_id": user.id, "role": "manager"}, headers=headers)
                promote_ok = r.status_code == 200
                pretty_print("Admin promote", promote_ok, f"code={r.status_code} body={r.get_data(as_text=True)}")
                # revert role
                r2 = client.post("/api/admin/demote", json={"user_id": user.id, "role": "user"}, headers=headers)
                demote_ok = r2.status_code == 200
                pretty_print("Admin demote", demote_ok, f"code={r2.status_code} body={r2.get_data(as_text=True)}")
            else:
                pretty_print("Admin promote", False, "test user not found")
        else:
            print("Skipping admin promote/demote because admin or login failed.")

        if not (reg_ok and login_ok and admin_login_ok):
            print("\nOne or more core checks failed — inspect outputs above.")
            sys.exit(2)

        print("\nAll core checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
