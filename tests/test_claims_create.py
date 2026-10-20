import pytest

VALID = {
    "category": "dental",
    "amount_cents": 4500,
    "description": "Dental cleaning",
    "incurred_on": "2024-01-15",
}


def test_create_claim(client, make_member, as_member):
    member = make_member()
    res = client.post("/claims", json=VALID, headers=as_member(member))
    assert res.status_code == 201
    body = res.get_json()
    assert body["member_id"] == member["id"]
    assert body["status"] == "pending"
    assert body["decided_at"] is None
    assert body["currency"] == "EUR"
    assert body["amount_cents"] == 4500


def test_requires_member_header(client):
    res = client.post("/claims", json=VALID)
    assert res.status_code == 401


def test_unknown_member_is_rejected(client):
    res = client.post("/claims", json=VALID, headers={"X-Member-Id": "999"})
    assert res.status_code == 401


def test_non_numeric_member_header_is_rejected(client):
    res = client.post("/claims", json=VALID, headers={"X-Member-Id": "abc"})
    assert res.status_code == 401


def test_authentication_is_checked_before_validation(client):
    res = client.post("/claims", json={"category": "nope"})
    assert res.status_code == 401


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount_cents": 0},
        {"amount_cents": -5},
        {"amount_cents": "4500"},
        {"amount_cents": 12.5},
        {"incurred_on": "2999-01-01"},
        {"incurred_on": "not-a-date"},
        {"category": "massage"},
        {"description": ""},
        {"description": "x" * 501},
        {"currency": "USD"},
        {"surprise": 1},
    ],
    ids=[
        "zero-amount",
        "negative-amount",
        "string-amount",
        "float-amount",
        "future-date",
        "bad-date",
        "unknown-category",
        "empty-description",
        "description-too-long",
        "unsupported-currency",
        "unknown-field",
    ],
)
def test_invalid_claim_returns_400(client, make_member, as_member, overrides):
    member = make_member()
    res = client.post("/claims", json={**VALID, **overrides}, headers=as_member(member))
    assert res.status_code == 400
    body = res.get_json()
    assert body["error"] == "Validation failed"
    assert body["details"]