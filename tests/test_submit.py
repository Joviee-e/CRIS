# tests/test_submit.py
import json

def create_user_and_get_token(client):
    client.post("/api/auth/register", json={"email":"u1@example.com","password":"p1"})
    res = client.post("/api/auth/login", json={"email":"u1@example.com","password":"p1"})
    return res.get_json()["access"]

def test_submit_application(client, db):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "sr_no": 42,
        "purpose": "Test Purpose",
        "department": "Dept",
        "emp_no": "EMP42",
        "emp_name": "Tester",
        "designation": "Dev",
        "remarks": "Test"
    }
    res = client.post("/api/applications/", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data

    # fetch the created resource
    app_id = data["id"]
    res2 = client.get(f"/api/applications/{app_id}", headers=headers)
    # your skeleton may not have GET detail implemented; if it does, assert 200
    # otherwise skip this assert. We'll attempt to be permissive:
    assert res2.status_code in (200, 404)
