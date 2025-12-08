from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..models import Attachment

attachments_bp = Blueprint("attachments", __name__)

def serialize_attachment(a: Attachment):
    return {
        "id": a.id,
        "filename": a.filename,
        "mime_type": a.mime_type,
        "size": a.size,
        "created_at": a.created_at.isoformat(),
        "download_url": f"/uploads/{a.filename}",
    }


@attachments_bp.route("/attachments", methods=["GET"])
@jwt_required()
def list_attachments():
    app_id = request.args.get("app_id")

    q = Attachment.query
    if app_id:
        q = q.filter_by(application_id=app_id)

    attachments = q.order_by(Attachment.created_at.desc()).all()
    return {"attachments": [serialize_attachment(a) for a in attachments]}, 200
