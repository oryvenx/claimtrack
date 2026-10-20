from app.models import Claim, Member


def serialize_member(member: Member) -> dict:
    return {
        "id": member.id,
        "email": member.email,
        "name": member.name,
        "created_at": member.created_at.isoformat(),
    }


def serialize_claim(claim: Claim) -> dict:
    return {
        "id": claim.id,
        "member_id": claim.member_id,
        "category": claim.category.value,
        "amount_cents": claim.amount_cents,
        "currency": claim.currency,
        "description": claim.description,
        "incurred_on": claim.incurred_on.isoformat(),
        "status": claim.status.value,
        "created_at": claim.created_at.isoformat(),
        "updated_at": claim.updated_at.isoformat(),
        "decided_at": claim.decided_at.isoformat() if claim.decided_at else None,
    }