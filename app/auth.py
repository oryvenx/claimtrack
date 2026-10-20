import hmac

from flask import request, current_app

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


def require_reviewer() -> None:
    expected = current_app.config.get("REVIEWER_API_KEY")
    provided = request.headers.get("X-Reviewer-Key")
    if provided is None:
        raise ApiError("Missing X-Reviewer-Key header", 401)
    if not expected or not hmac.compare_digest(provided.encode(), expected.encode()):
        raise ApiError("Reviewer access required", 403)