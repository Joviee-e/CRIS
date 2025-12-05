from flask import Blueprint, request
from ..extensions import db
from ..models import Application, ActionLog
from flask_jwt_extended import jwt_required, get_jwt_identity

app_bp = Blueprint("applications", __name__)

@app_bp.route("/", methods=["POST"])
@jwt_required()
def submit():
    data = request.get_json()
    app_obj = Application(**data)
    db.session.add(app_obj)
    db.session.commit()

    log = ActionLog(application_id=app_obj.id, action="submitted",
                    user_id=get_jwt_identity()["id"])
    db.session.add(log)
    db.session.commit()

    return {"id": app_obj.id}, 201

@app_bp.route("/<id>/verify", methods=["PATCH"])
@jwt_required()
def verify(id):
    app = Application.query.get_or_404(id)
    if app.status != "submitted":
        return {"msg": "cannot verify"}, 400

    app.status = "verified"
    db.session.commit()

    log = ActionLog(application_id=id, action="verified",
                    user_id=get_jwt_identity()["id"])
    db.session.add(log)
    db.session.commit()

    return {"msg": "verified"}

@app_bp.route("/<id>/approve", methods=["PATCH"])
@jwt_required()
def approve(id):
    app = Application.query.get_or_404(id)
    if app.status != "verified":
        return {"msg": "cannot approve"}, 400

    app.status = "approved"
    db.session.commit()

    log = ActionLog(application_id=id, action="approved",
                    user_id=get_jwt_identity()["id"])
    db.session.add(log)
    db.session.commit()

    return {"msg": "approved"}
