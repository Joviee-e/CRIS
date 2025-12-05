# scripts/seed.py
import sys
import pathlib

# Ensure project root is on sys.path so `import app` works no matter how we run the script
project_root = pathlib.Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models import User

def main():
    app = create_app()
    with app.app_context():
        email = "admin@example.com"
        pwd = "admin123"
        existing = User.query.filter_by(email=email).first()
        if existing:
            print("Admin already exists:", email)
            return
        admin = User(email=email, role="admin")
        admin.set_password(pwd)
        db.session.add(admin)
        db.session.commit()
        print("Admin created:", email, "/", pwd)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # show any unexpected error clearly
        import traceback
        print("Error running seed.py:", e)
        traceback.print_exc()
