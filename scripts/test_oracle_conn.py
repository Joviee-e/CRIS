# backend/scripts/test_oracle_conn.py
"""
Test Oracle connection script.
Requires cx_Oracle (or python-oracledb) installed and ORACLE_* env vars set:
ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

This prints a simple test query result and exits with code 0 on success.
"""
import os
import sys

try:
    import oracledb as cx_Oracle
except Exception:
    try:
        import cx_Oracle
    except Exception:
        print("cx_Oracle / oracledb not installed. Install python-oracledb or cx_Oracle.", file=sys.stderr)
        sys.exit(2)

def main():
    user = os.getenv("ORACLE_USER")
    pwd = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")  # like host:port/service_name

    if not (user and pwd and dsn):
        print("Set ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN env vars.", file=sys.stderr)
        sys.exit(3)
    try:
        conn = cx_Oracle.connect(user, pwd, dsn)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM dual")
        r = cur.fetchone()
        print("Oracle test query result:", r)
        cur.close()
        conn.close()
        sys.exit(0)
    except Exception as e:
        print("Oracle connection failed:", e, file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
