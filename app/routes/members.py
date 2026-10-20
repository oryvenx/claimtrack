from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.errors import ApiError
from app.extensions import db
from app.models import Member
from app.schemas import MemberCreate
from app.serializers import serialize_member
from app.validation import parse_body

bp = Blueprint("members", __name__)

EMAIL_TAKEN = "A member with this email already exists"


@bp.post("/members")
def create_member():
    data = parse_body(MemberCreate)
    email = data.email.lower()

    if db.session.scalar(select(Member.id).where(Member.email == email)):
        raise ApiError(EMAIL_TAKEN, 409)

    member = Member(email=email, name=data.name)
    db.session.add(member)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError(EMAIL_TAKEN, 409)
    return jsonify(serialize_member(member)), 201