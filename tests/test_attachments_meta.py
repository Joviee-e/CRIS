from app.models import Application, Attachment


def auth_header(client):
    # same pattern as in your other tests (adapt names if needed)
    client.post("/api/auth/register", json={"email": "meta@example.com", "password": "pass123"})
    res = client.post("/api/auth/login", json={"email": "meta@example.com", "password": "pass123"})
    token = res.get_json()["access"]
    return {"Authorization": f"Bearer {token}"}


def test_get_app_attachments(client, db):
    app_obj = Application(
        sr_no=1,
        purpose="Testing",
        department="IT",
        emp_no="123",
        emp_name="Test User",
        designation="Engineer",
    )
    db.session.add(app_obj)
    db.session.commit()

    att = Attachment(
        application_id=app_obj.id,
        filename="file1.pdf",
        mime_type="application/pdf",
        size=1200,
    )
    db.session.add(att)
    db.session.commit()

    headers = auth_header(client)
    resp = client.get(f"/api/applications/{app_obj.id}/attachments", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert "attachments" in body
    assert len(body["attachments"]) == 1
    assert body["attachments"][0]["filename"] == "file1.pdf"
    assert "download_url" in body["attachments"][0]


def test_list_attachments(client, db):
    app_obj = Application(
        sr_no=2,
        purpose="Testing List",
        department="IT",
        emp_no="456",
        emp_name="Another User",
        designation="Admin",
    )
    db.session.add(app_obj)
    db.session.commit()

    att = Attachment(
        application_id=app_obj.id,
        filename="image.png",
        mime_type="image/png",
        size=3000,
    )
    db.session.add(att)
    db.session.commit()

    headers = auth_header(client)
    resp = client.get(f"/api/attachments?app_id={app_obj.id}", headers=headers)
    assert resp.status_code == 200
    
    body = resp.get_json()
    assert "attachments" in body
    assert len(body["attachments"]) == 1
    assert body["attachments"][0]["mime_type"] == "image/png"