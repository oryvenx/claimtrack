import pytest


def test_create_member_lowercases_email(client):
    res = client.post("/members", json={"email": "Alice@Example.com", "name": "Alice"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"
    assert "id" in body


def test_duplicate_email_returns_409_ignoring_case(client, make_member):
    make_member(email="alice@example.com")
    res = client.post("/members", json={"email": "ALICE@example.com", "name": "Other"})
    assert res.status_code == 409


def test_duplicate_email_does_not_consume_an_id(client, make_member):
    first = make_member(email="a@example.com")
    client.post("/members", json={"email": "a@example.com", "name": "Duplicate"})
    second = make_member(email="b@example.com")
    assert second["id"] == first["id"] + 1


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "name": "Alice"},
        {"email": "a@example.com"},
        {"email": "a@example.com", "name": ""},
        {"email": "a@example.com", "name": "Alice", "is_admin": True},
    ],
    ids=["bad-email", "missing-name", "empty-name", "unknown-field"],
)
def test_invalid_member_payload_returns_400(client, payload):
    res = client.post("/members", json=payload)
    assert res.status_code == 400
    assert res.get_json()["error"] == "Validation failed"


def test_non_json_body_returns_400(client):
    res = client.post("/members", data="not json", content_type="application/json")
    assert res.status_code == 400