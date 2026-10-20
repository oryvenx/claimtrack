from flask import Blueprint, jsonify

from app.auth import get_current_member
from app.extensions import db
from app.models import Claim
from app.schemas import ClaimCreate
from app.serializers import serialize_claim
from app.validation import parse_body

bp = Blueprint("claims", __name__)


@bp.post("/claims")
def create_claim():
    member = get_current_member()
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