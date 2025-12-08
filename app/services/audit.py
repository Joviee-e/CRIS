# app/services/audit.py
from app.extensions import db
from app.models import ActionLog


def create_action_log(application_id, action, actor_id=None, comment=None):
    """
    Create an ActionLog entry and commit it.
    Returns the created ActionLog instance.
    """
    log = ActionLog(
        application_id=application_id,
        action=action,
        actor_id=actor_id,
        comment=comment,
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return log
