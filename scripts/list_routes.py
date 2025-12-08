# D:\CRIS CLONE\CRIS\scripts\list_routes.py
import os, sys
# ensure project root (parent of scripts/) is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def main():
    app = create_app()
    with app.app_context():
        print("Registered routes:")
        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        for rule in rules:
            methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            print(f"{rule.rule:40s}  [{methods}]")

if __name__ == "__main__":
    main()
