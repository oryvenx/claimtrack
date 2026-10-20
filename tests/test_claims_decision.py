import threading
from concurrent.futures import ThreadPoolExecutor

import pytest


def _new_claim(make_member, make_claim):
    member = make_member()
    return member, make_claim(member["id"])


def test_approve_claim(client, make_member, make_claim, reviewer_headers):
    _, claim = _new_claim(make_member, make_claim)
    res = client.post(f"/claims/{claim['id']}/approve", headers=reviewer_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "approved"
    assert body["decided_at"] is not None


def test_reject_claim(client, make_member, make_claim, reviewer_headers):
    _, claim = _new_claim(make_member, make_claim)
    res = client.post(f"/claims/{claim['id']}/reject", headers=reviewer_headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "rejected"


@pytest.mark.parametrize(
    "first,second",
    [
        ("approve", "approve"),
        ("approve", "reject"),
        ("reject", "approve"),
        ("reject", "reject"),
    ],
)
def test_claim_can_only_be_decided_once(
    client, make_member, make_claim, as_member, reviewer_headers, first, second
):
    member, claim = _new_claim(make_member, make_claim)
    url = f"/claims/{claim['id']}"

    assert client.post(f"{url}/{first}", headers=reviewer_headers).status_code == 200
    res = client.post(f"{url}/{second}", headers=reviewer_headers)

    assert res.status_code == 409
    current = client.get(url, headers=as_member(member)).get_json()
    assert current["status"] == {"approve": "approved", "reject": "rejected"}[first]


def test_decision_requires_reviewer_key(
    client, make_member, make_claim, as_member
):
    member, claim = _new_claim(make_member, make_claim)
    res = client.post(f"/claims/{claim['id']}/approve")
    assert res.status_code == 401
    current = client.get(f"/claims/{claim['id']}", headers=as_member(member)).get_json()
    assert current["status"] == "pending"


def test_wrong_reviewer_key_is_forbidden(client, make_member, make_claim):
    _, claim = _new_claim(make_member, make_claim)
    res = client.post(
        f"/claims/{claim['id']}/approve", headers={"X-Reviewer-Key": "wrong"}
    )
    assert res.status_code == 403


def test_member_header_does_not_grant_reviewer_access(
    client, make_member, make_claim, as_member
):
    member, claim = _new_claim(make_member, make_claim)
    res = client.post(f"/claims/{claim['id']}/approve", headers=as_member(member))
    assert res.status_code == 401


def test_fails_closed_when_no_reviewer_key_is_configured(
    app, client, make_member, make_claim, monkeypatch
):
    _, claim = _new_claim(make_member, make_claim)
    monkeypatch.setitem(app.config, "REVIEWER_API_KEY", None)
    res = client.post(
        f"/claims/{claim['id']}/approve", headers={"X-Reviewer-Key": "anything"}
    )
    assert res.status_code == 403


def test_deciding_unknown_claim_returns_404(client, reviewer_headers):
    res = client.post("/claims/9999/approve", headers=reviewer_headers)
    assert res.status_code == 404


def test_concurrent_decisions_have_exactly_one_winner(
    app, make_member, make_claim, reviewer_headers
):
    _, claim = _new_claim(make_member, make_claim)
    actions = ["approve", "reject", "approve", "reject", "approve"]
    barrier = threading.Barrier(len(actions), timeout=10)

    def attempt(action: str) -> int:
        barrier.wait()  # release all requests at the same moment
        with app.test_client() as c:
            res = c.post(f"/claims/{claim['id']}/{action}", headers=reviewer_headers)
            return res.status_code

    with ThreadPoolExecutor(max_workers=len(actions)) as pool:
        codes = list(pool.map(attempt, actions))

    assert codes.count(200) == 1
    assert codes.count(409) == len(actions) - 1