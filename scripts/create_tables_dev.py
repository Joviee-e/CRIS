# scripts/create_tables_dev.py
import os, sys

# Make sure project root is on sys.path so `import app` works
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db

def main():
    app = create_app()
    with app.app_context():
        print("Before:", db.inspect(db.engine).get_table_names())
        db.create_all()
        print("After: ", db.inspect(db.engine).get_table_names())

if __name__ == "__main__":
    main()
