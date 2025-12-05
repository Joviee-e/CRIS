# app/routes/applications.py
from flask import Blueprint, request
from ..extensions import db
from ..models import Application, ActionLog
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils import role_required

app_bp = Blueprint("applications", __name__)

@app_bp.route("/", methods=["POST"])
@jwt_required()
def submit():
    data = request.get_json()
    app_obj = Application(**data)
    db.session.add(app_obj)
    db.session.commit()

    user_id = get_jwt_identity()
    log = ActionLog(application_id=app_obj.id, action="submitted", user_id=user_id)
    db.session.add(log)
    db.session.commit()

    return {"id": app_obj.id}, 201

@app_bp.route("/<id>/verify", methods=["PATCH"])
@jwt_required()
@role_required("admin", "verifier")
def verify(id):
    app_obj = Application.query.get_or_404(id)
    if app_obj.status != "submitted":
        return {"msg": "cannot verify"}, 400

    app_obj.status = "verified"
    db.session.commit()

    user_id = get_jwt_identity()
    log = ActionLog(application_id=id, action="verified", user_id=user_id)
    db.session.add(log)
    db.session.commit()

    return {"msg": "verified"}

@app_bp.route("/<id>/approve", methods=["PATCH"])
@jwt_required()
@role_required("admin", "approver")
def approve(id):
    app_obj = Application.query.get_or_404(id)
    if app_obj.status != "verified":
        return {"msg": "cannot approve"}, 400

    app_obj.status = "approved"
    db.session.commit()

    user_id = get_jwt_identity()
    log = ActionLog(application_id=id, action="approved", user_id=user_id)
    db.session.add(log)
    db.session.commit()

    return {"msg": "approved"}
