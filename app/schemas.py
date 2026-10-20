from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import ClaimCategory


class MemberCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class ClaimCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: ClaimCategory
    amount_cents: int = Field(gt=0, le=100_000_000, strict=True)
    currency: Literal["EUR"] = "EUR"
    description: str = Field(min_length=1, max_length=500)
    incurred_on: date

    @field_validator("incurred_on")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > datetime.now(timezone.utc).date():
            raise ValueError("incurred_on cannot be in the future")
        return value