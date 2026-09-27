import json

from flask import has_request_context, request
from flask_login import current_user

from .extensions import db
from .models import AuditLog


def _json_default(value):
    return str(value)


def audit(action, entity=None, summary="", details=None, user=None):
    """Add an audit entry to the current transaction. The caller commits."""
    if user is None and has_request_context() and current_user.is_authenticated:
        user = current_user
    entry = AuditLog(
        user_id=user.id if user else None,
        user_label=f"{user.name} <{user.email}>" if user else "System",
        action=action,
        entity_type=entity.__tablename__ if entity is not None else None,
        entity_id=getattr(entity, "id", None),
        summary=summary[:500],
        details=json.dumps(details, default=_json_default) if details else None,
        ip_address=request.remote_addr if has_request_context() else None,
    )
    db.session.add(entry)
    return entry


def diff(obj, fields, new_values):
    """Apply new_values to obj and return {field: [old, new]} for what changed."""
    changes = {}
    for field in fields:
        if field not in new_values:
            continue
        old, new = getattr(obj, field), new_values[field]
        if old != new:
            changes[field] = [old, new]
            setattr(obj, field, new)
    return changes
