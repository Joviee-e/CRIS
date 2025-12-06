# app/routes/applications.py (only the submit handler shown; keep the rest)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Application, ActionLog, User

app_bp = Blueprint("applications_bp", __name__)

@app_bp.route("/", methods=["POST"])
@jwt_required()
def submit():
    data = request.get_json() or {}
    expected = ["sr_no", "purpose", "department", "emp_no", "emp_name"]
    missing = [f for f in expected if f not in data]
    if missing:
        return jsonify({"msg": "missing fields", "missing": missing}), 400

    # set created_by from JWT identity
    created_by = get_jwt_identity()
    if not created_by:
        return jsonify({"msg": "invalid token / identity"}), 401

    app_data = {
        "sr_no": data.get("sr_no"),
        "purpose": data.get("purpose"),
        "department": data.get("department"),
        "emp_no": data.get("emp_no"),
        "emp_name": data.get("emp_name"),
        "designation": data.get("designation"),
        "remarks": data.get("remarks"),
        "created_by": created_by,
    }

    app_obj = Application(**app_data)
    db.session.add(app_obj)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "db error", "error": str(e)}), 500

    # log action
    log = ActionLog(application_id=app_obj.id, action="created", actor_id=created_by)
    db.session.add(log)
    db.session.commit()

    # Return the created application object at the top level (tests expect "id" at top-level)
    return jsonify(app_obj.to_dict()), 201

# Approve endpoint (admin only) — example kept brief (ensure admin check elsewhere)
@app_bp.route("/<id>/approve", methods=["PATCH"])
@jwt_required()
def approve(id):
    # admin check — user role is expected in JWT claims or DB fallback
    claims = get_jwt()
    identity = get_jwt_identity()
    # simple check: look up user role
    user = User.query.get(identity)
    if not user or user.role != "admin":
        return jsonify({"msg": "admin required"}), 403

    app_obj = Application.query.get(id)
    if not app_obj:
        return jsonify({"msg": "not found"}), 404
    app_obj.status = "approved"
    db.session.commit()
    log = ActionLog(application_id=id, action="approved", actor_id=identity)
    db.session.add(log)
    db.session.commit()
    return jsonify({"msg": "approved"}), 200


# Verify endpoint (admin only)
@app_bp.route("/<id>/verify", methods=["PATCH"])
@jwt_required()
def verify(id):
    claims = get_jwt()
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != "admin":
        return jsonify({"msg": "admin required"}), 403
    app_obj = Application.query.get(id)
    if not app_obj:
        return jsonify({"msg": "not found"}), 404
    app_obj.status = "verified"
    db.session.commit()
    log = ActionLog(application_id=id, action="verified", actor_id=identity)
    db.session.add(log)
    db.session.commit()
    return jsonify({"msg": "verified"}), 200
