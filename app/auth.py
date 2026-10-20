from flask import request

from app.errors import ApiError
from app.extensions import db
from app.models import Member


def get_current_member() -> Member:
    raw = request.headers.get("X-Member-Id")
    if raw is None:
        raise ApiError("Missing X-Member-Id header", 401)
    try:
        member_id = int(raw)
    except ValueError:
        raise ApiError("Invalid X-Member-Id header", 401)
    member = db.session.get(Member, member_id)
    if member is None:
        raise ApiError("Unknown member", 401)
    return member