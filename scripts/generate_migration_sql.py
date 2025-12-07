# scripts/generate_migration_sql.py

import argparse
from contextlib import redirect_stdout
from pathlib import Path
import sys

# Make sure the project root (which contains the `app` package) is importable
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from flask_migrate import upgrade


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Alembic migration SQL for Oracle handover."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="scripts/migration.sql",
        help="Path to write the generated SQL file (default: scripts/migration.sql)",
    )
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Flask-Migrate's upgrade(sql=True) prints SQL to stdout; capture it into a file.
        with output_path.open("w", encoding="utf-8") as f, redirect_stdout(f):
            # Run upgrade to the latest revision (head) in SQL mode (no DB changes)
            upgrade(revision="head", sql=True)

    print(f"Migration SQL written to {output_path}")


if __name__ == "__main__":
    main()
