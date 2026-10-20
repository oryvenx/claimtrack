import os

from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(url: str | None) -> str | None:
    """Heroku provides postgres://..., SQLAlchemy needs a dialect+driver."""
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get("DATABASE_URL"))