# tests/test_auth.py
import json

def test_register_login(client, db):
    # register
    res = client.post("/api/auth/register", json={"email":"test@example.com","password":"pass123"})
    assert res.status_code == 201

    # login success
    res = client.post("/api/auth/login", json={"email":"test@example.com","password":"pass123"})
    assert res.status_code == 200
    data = res.get_json()
    assert "access" in data and "refresh" in data

    # login failure
    res = client.post("/api/auth/login", json={"email":"test@example.com","password":"wrong"})
    assert res.status_code == 401
