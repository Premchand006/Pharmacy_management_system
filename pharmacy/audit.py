"""Audit trail.

Every insert, update and delete that goes through the ORM is written to
audit_log in the same transaction, so a change and its log entry either
both commit or both roll back. GST Rule 56(8) and the Companies Act edit
log both expect this kind of trail.
"""
import json
from datetime import date, datetime
from decimal import Decimal

from flask import g, has_request_context, request
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from .models import AuditLog, LoginAttempt, utcnow

SKIP = (AuditLog, LoginAttempt)
# Values never copied into the log. For customers this keeps personal data
# out of the trail, so anonymising a profile really removes it.
HIDDEN = {
    "password_hash",
    "session_version",
    "Customer.name",
    "Customer.phone",
    "Customer.address",
    "Customer.age",
    "Customer.gender",
}


def _plain(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _hidden(obj, key):
    return key in HIDDEN or f"{type(obj).__name__}.{key}" in HIDDEN


def _changes(obj, action):
    state = inspect(obj)
    out = {}
    for attr in state.mapper.column_attrs:
        key = attr.key
        hist = state.attrs[key].history
        if action == "update" and not hist.has_changes():
            continue
        if action == "create":
            value = getattr(obj, key)
            if value is None:
                continue
            out[key] = "(set)" if _hidden(obj, key) else _plain(value)
        elif action == "update":
            old = hist.deleted[0] if hist.deleted else None
            new = hist.added[0] if hist.added else None
            out[key] = "(changed)" if _hidden(obj, key) else [_plain(old), _plain(new)]
    return out


def _actor():
    if has_request_context():
        user = getattr(g, "user", None)
        if user is not None:
            kind = "customer" if getattr(g, "user_kind", "") == "customer" else "staff"
            return f"{kind}:{user.name}", request.remote_addr or ""
        return "anonymous", request.remote_addr or ""
    return "system", ""


def record(session, action, entity, entity_id="", changes=None):
    """Write an audit entry for something that is not a plain row change."""
    actor, ip = _actor()
    session.add(AuditLog(actor=actor, action=action, entity=entity, entity_id=str(entity_id),
                         changes=json.dumps(changes or {}, default=str), ip=ip))


@event.listens_for(Session, "after_flush")
def _log_flush(session, flush_context):
    rows = []
    actor, ip = _actor()
    for action, objs in (("create", session.new), ("update", session.dirty), ("delete", session.deleted)):
        for obj in objs:
            if isinstance(obj, SKIP) or not hasattr(obj, "__table__"):
                continue
            if action == "update" and not session.is_modified(obj, include_collections=False):
                continue
            changes = _changes(obj, action) if action != "delete" else {}
            if action == "update" and not changes:
                continue
            pk = inspect(obj).identity
            rows.append({
                "at": utcnow(),
                "actor": actor,
                "action": action,
                "entity": type(obj).__name__,
                "entity_id": ",".join(str(p) for p in pk) if pk else "",
                "changes": json.dumps(changes, default=str),
                "ip": ip,
            })
    if rows:
        session.connection().execute(AuditLog.__table__.insert(), rows)
