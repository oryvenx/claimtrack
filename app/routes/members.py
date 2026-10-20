from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError

from app.errors import ApiError
from app.extensions import db
from app.models import Member
from app.schemas import MemberCreate
from app.serializers import serialize_member
from app.validation import parse_body

bp = Blueprint("members", __name__)


@bp.post("/members")
def create_member():
    data = parse_body(MemberCreate)
    member = Member(email=data.email.lower(), name=data.name)
    db.session.add(member)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("A member with this email already exists", 409)
    return jsonify(serialize_member(member)), 201