from flask import Blueprint, jsonify, request
from sqlalchemy import func, select

from app.auth import get_current_member
from app.errors import ApiError
from app.extensions import db
from app.models import Claim, ClaimStatus
from app.schemas import ClaimCreate
from app.serializers import serialize_claim
from app.validation import parse_body

bp = Blueprint("claims", __name__)

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def _int_arg(name: str, default: int, minimum: int, maximum: int | None = None) -> int:
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ApiError(f"'{name}' must be an integer", 400)
    if value < minimum or (maximum is not None and value > maximum):
        bound = f"between {minimum} and {maximum}" if maximum else f"at least {minimum}"
        raise ApiError(f"'{name}' must be {bound}", 400)
    return value


@bp.post("/claims")
def create_claim():
    member = get_current_member()  # authenticate first, then validate
    data = parse_body(ClaimCreate)
    claim = Claim(
        member_id=member.id,
        category=data.category,
        amount_cents=data.amount_cents,
        currency=data.currency,
        description=data.description,
        incurred_on=data.incurred_on,
    )
    db.session.add(claim)
    db.session.commit()
    return jsonify(serialize_claim(claim)), 201


@bp.get("/claims")
def list_claims():
    member = get_current_member()

    query = select(Claim).where(Claim.member_id == member.id)

    status = request.args.get("status")
    if status is not None:
        try:
            query = query.where(Claim.status == ClaimStatus(status))
        except ValueError:
            allowed = ", ".join(s.value for s in ClaimStatus)
            raise ApiError(f"Invalid status. Allowed values: {allowed}", 400)

    limit = _int_arg("limit", DEFAULT_LIMIT, 1, MAX_LIMIT)
    offset = _int_arg("offset", 0, 0)

    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    claims = db.session.scalars(
        query.order_by(Claim.created_at.desc(), Claim.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return jsonify(
        items=[serialize_claim(c) for c in claims],
        total=total,
        limit=limit,
        offset=offset,
    )


@bp.get("/claims/<int:claim_id>")
def get_claim(claim_id: int):
    member = get_current_member()
    claim = db.session.scalar(
        select(Claim).where(Claim.id == claim_id, Claim.member_id == member.id)
    )
    if claim is None:
        raise ApiError("Claim not found", 404)
    return jsonify(serialize_claim(claim))