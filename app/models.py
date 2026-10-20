import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class ClaimCategory(str, enum.Enum):
    DENTAL = "dental"
    OPTICAL = "optical"
    CONSULTATION = "consultation"
    PHARMACY = "pharmacy"
    HOSPITAL = "hospital"


class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Member(db.Model):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    claims: Mapped[list["Claim"]] = relationship(back_populates="member")


class Claim(db.Model):
    __tablename__ = "claims"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_claims_amount_positive"),
        Index("ix_claims_member_status", "member_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    category: Mapped[ClaimCategory] = mapped_column(
        Enum(
            ClaimCategory,
            native_enum=False,
            length=20,
            values_callable=_enum_values,
        )
    )
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    description: Mapped[str] = mapped_column(String(500))
    incurred_on: Mapped[date] = mapped_column(Date)
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(
            ClaimStatus,
            native_enum=False,
            length=20,
            values_callable=_enum_values,
        ),
        default=ClaimStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    member: Mapped["Member"] = relationship(back_populates="claims")