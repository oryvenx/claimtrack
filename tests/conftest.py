import os
from pathlib import Path

import pytest
from flask_migrate import upgrade
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app import create_app
from app.config import _normalize_db_url
from app.extensions import db

MIGRATIONS_DIR = str(Path(__file__).resolve().parent.parent / "migrations")
REVIEWER_KEY = "test-reviewer-key"

TEST_DATABASE_URL = _normalize_db_url(
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://claimtrack:claimtrack@localhost:5432/claimtrack_test",
    )
)


def _assert_test_database(url: str) -> None:
    name = make_url(url).database or ""
    if not name.endswith("_test"):
        raise RuntimeError(
            f"Refusing to run tests against database '{name}': "
            "its name must end with '_test'."
        )


@pytest.fixture(scope="session")
def app():
    _assert_test_database(TEST_DATABASE_URL)

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
            "REVIEWER_API_KEY": REVIEWER_KEY,
        }
    )

    with app.app_context():
        with db.engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
        upgrade(directory=MIGRATIONS_DIR)

    yield app


@pytest.fixture(autouse=True)
def _clean_db(app):
    yield
    with app.app_context():
        db.session.execute(text("TRUNCATE members, claims RESTART IDENTITY CASCADE"))
        db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def reviewer_headers():
    return {"X-Reviewer-Key": REVIEWER_KEY}


@pytest.fixture
def as_member():
    def _headers(member: dict) -> dict:
        return {"X-Member-Id": str(member["id"])}

    return _headers


@pytest.fixture
def make_member(client):
    counter = {"n": 0}

    def _make(name: str = "Alice", email: str | None = None) -> dict:
        counter["n"] += 1
        email = email or f"user{counter['n']}@example.com"
        res = client.post("/members", json={"email": email, "name": name})
        assert res.status_code == 201, res.get_json()
        return res.get_json()

    return _make


@pytest.fixture
def make_claim(client):
    def _make(member_id: int, **overrides) -> dict:
        payload = {
            "category": "dental",
            "amount_cents": 4500,
            "description": "Dental cleaning",
            "incurred_on": "2024-01-15",
        }
        payload.update(overrides)
        res = client.post(
            "/claims", json=payload, headers={"X-Member-Id": str(member_id)}
        )
        assert res.status_code == 201, res.get_json()
        return res.get_json()

    return _make