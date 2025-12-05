# scripts/test_oracle_conn.py
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

def run_check():
    url = os.getenv("DATABASE_URL")
    print("DATABASE_URL:", url)
    if not url:
        print("No DATABASE_URL set. Exiting.")
        return
    engine = create_engine(url, pool_pre_ping=True)
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1 FROM dual"))
        print("Ping result:", r.scalar())

if __name__ == "__main__":
    run_check()
