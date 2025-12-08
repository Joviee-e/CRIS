def test_non_admin_cannot_verify(client, db):
    # create regular user
    client.post("/api/auth/register", json={"email":"u2@example.com","password":"p2"})
    res = client.post("/api/auth/login", json={"email":"u2@example.com","password":"p2"})
    token = res.get_json()["access"]
    headers = {"Authorization": f"Bearer {token}"}

    # submit application
    payload = {"sr_no":2,"purpose":"role test","department":"D","emp_no":"EMP2","emp_name":"X","designation":"Y","remarks":"r"}
    res = client.post("/api/applications/", json=payload, headers=headers)
    assert res.status_code == 201
    app_id = res.get_json()["id"]

    # try to verify as non-admin -> expect 401 or 403
    res_verify = client.patch(f"/api/applications/{app_id}/verify", headers=headers)
    assert res_verify.status_code in (401, 403)
