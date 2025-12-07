# app/routes/applications.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Application, ActionLog, User
from app.services.audit import create_action_log
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Application
from ..extensions import db

app_bp = Blueprint("applications_bp", __name__)


@app_bp.route("/", methods=["POST"])
@jwt_required()
def submit():
    data = request.get_json() or {}
    expected = ["sr_no", "purpose", "department", "emp_no", "emp_name"]
    missing = [f for f in expected if f not in data]
    if missing:
        return jsonify({"msg": "missing fields", "missing": missing}), 400

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
        # initial state of the workflow
        "status": "submitted",
    }

    app_obj = Application(**app_data)
    db.session.add(app_obj)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "db error", "error": str(e)}), 500

    # log creation
    try:
        create_action_log(
            application_id=app_obj.id,
            action="created",
            actor_id=created_by,
            comment=None,
        )
    except Exception:
        # app is already created; we just warn that audit failed
        return jsonify({"msg": "created, but failed to write audit log"}), 201

    return jsonify(app_obj.to_dict()), 201


def _require_admin(identity):
    """
    Helper: return User instance if admin, else None.
    """
    user = User.query.get(identity)
    if not user or user.role != "admin":
        return None
    return user


@app_bp.route("/<id>/verify", methods=["PATCH"])
@jwt_required()
def verify(id):
    """
    Verify an application.
    Allowed only from status 'submitted' -> 'verified'.
    Admin only.
    Optional JSON body: { "note": "..."} or { "comment": "..." }.
    """
    identity = get_jwt_identity()
    admin_user = _require_admin(identity)
    if not admin_user:
        return jsonify({"msg": "admin required"}), 403

    app_obj = Application.query.get(id)
    if not app_obj:
        return jsonify({"msg": "not found"}), 404

    current = (app_obj.status or "").lower()
    if current != "submitted":
        return jsonify({"msg": "invalid transition", "from": current, "to": "verified"}), 400

    app_obj.status = "verified"
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "db error", "error": str(e)}), 500

    payload = request.get_json(silent=True) or {}
    note = payload.get("note") or payload.get("comment")

    try:
        create_action_log(
            application_id=id,
            action="verified",
            actor_id=identity,
            comment=note,
        )
    except Exception:
        return jsonify({"msg": "verified (log failed)"}), 200

    return jsonify({"msg": "verified"}), 200


@app_bp.route("/<id>/approve", methods=["PATCH"])
@jwt_required()
def approve(id):
    """
    Approve an application.
    Allowed only from status 'verified' -> 'approved'.
    Admin only.
    Optional JSON body: { "note": "..."} or { "comment": "..." }.
    """
    identity = get_jwt_identity()
    admin_user = _require_admin(identity)
    if not admin_user:
        return jsonify({"msg": "admin required"}), 403

    app_obj = Application.query.get(id)
    if not app_obj:
        return jsonify({"msg": "not found"}), 404

    current = (app_obj.status or "").lower()
    if current != "verified":
        return jsonify({"msg": "invalid transition", "from": current, "to": "approved"}), 400

    app_obj.status = "approved"
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "db error", "error": str(e)}), 500

    payload = request.get_json(silent=True) or {}
    note = payload.get("note") or payload.get("comment")

    try:
        create_action_log(
            application_id=id,
            action="approved",
            actor_id=identity,
            comment=note,
        )
    except Exception:
        return jsonify({"msg": "approved (log failed)"}), 200

    return jsonify({"msg": "approved"}), 200


@app_bp.route("/<id>/logs", methods=["GET"])
@jwt_required()
def get_logs(id):
    """
    Return action logs for an application.
    Any authenticated user can see logs here (change if needed).
    """
    app_obj = Application.query.get(id)
    if not app_obj:
        return jsonify({"msg": "not found"}), 404

    logs = (
        ActionLog.query.filter_by(application_id=id)
        .order_by(ActionLog.created_at.asc())
        .all()
    )
    return jsonify({"logs": [log.to_dict() for log in logs]}), 200


# -------------------------
# New endpoints added below
# -------------------------

@app_bp.route("/", methods=["GET"])
@jwt_required()
def list_applications():
    """
    List applications with optional filters:
      - status
      - department
      - page, per_page (pagination)
    Returns paginated list of application dicts.
    """
    status = request.args.get("status", type=str)
    department = request.args.get("department", type=str)
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        per_page = 20

    q = Application.query
    if status:
        q = q.filter_by(status=status)
    if department:
        q = q.filter_by(department=department)

    pag = q.order_by(Application.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for a in pag.items:
        # prefer model serializer if present
        try:
            items.append(a.to_dict())
        except Exception:
            items.append({
                "id": a.id,
                "sr_no": a.sr_no,
                "purpose": a.purpose,
                "department": a.department,
                "emp_no": a.emp_no,
                "emp_name": a.emp_name,
                "designation": getattr(a, "designation", None),
                "remarks": getattr(a, "remarks", None),
                "status": getattr(a, "status", None),
                "created_at": getattr(a, "created_at", None).isoformat() if getattr(a, "created_at", None) else None,
            })

    return jsonify({
        "items": items,
        "page": pag.page,
        "per_page": pag.per_page,
        "total": pag.total
    }), 200


@app_bp.route("/<id>", methods=["GET"])
@jwt_required()
def get_application(id):
    """
    Get a single application by id and return its dict representation.
    """
    a = Application.query.get(id)
    if not a:
        return jsonify({"msg": "not found"}), 404

    try:
        return jsonify(a.to_dict()), 200
    except Exception:
        payload = {
            "id": a.id,
            "sr_no": a.sr_no,
            "purpose": a.purpose,
            "department": a.department,
            "emp_no": a.emp_no,
            "emp_name": a.emp_name,
            "designation": getattr(a, "designation", None),
            "remarks": getattr(a, "remarks", None),
            "status": getattr(a, "status", None),
            "created_at": getattr(a, "created_at", None).isoformat() if getattr(a, "created_at", None) else None,
        }
        return jsonify(payload), 200
