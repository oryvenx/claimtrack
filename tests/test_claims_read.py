import pytest


def test_list_returns_only_own_claims(client, make_member, make_claim, as_member):
    alice = make_member("Alice")
    bob = make_member("Bob")
    make_claim(alice["id"])
    make_claim(alice["id"])
    make_claim(bob["id"])

    body = client.get("/claims", headers=as_member(alice)).get_json()

    assert body["total"] == 2
    assert {c["member_id"] for c in body["items"]} == {alice["id"]}


def test_list_is_ordered_newest_first(client, make_member, make_claim, as_member):
    alice = make_member()
    first = make_claim(alice["id"], description="first")
    second = make_claim(alice["id"], description="second")

    items = client.get("/claims", headers=as_member(alice)).get_json()["items"]

    assert [c["id"] for c in items] == [second["id"], first["id"]]


def test_filter_by_status(
    client, make_member, make_claim, as_member, reviewer_headers
):
    alice = make_member()
    to_approve = make_claim(alice["id"])
    still_pending = make_claim(alice["id"])
    client.post(f"/claims/{to_approve['id']}/approve", headers=reviewer_headers)

    approved = client.get("/claims?status=approved", headers=as_member(alice)).get_json()
    pending = client.get("/claims?status=pending", headers=as_member(alice)).get_json()
    rejected = client.get("/claims?status=rejected", headers=as_member(alice)).get_json()

    assert [c["id"] for c in approved["items"]] == [to_approve["id"]]
    assert [c["id"] for c in pending["items"]] == [still_pending["id"]]
    assert rejected["items"] == [] and rejected["total"] == 0


def test_invalid_status_returns_400(client, make_member, as_member):
    alice = make_member()
    res = client.get("/claims?status=banana", headers=as_member(alice))
    assert res.status_code == 400


def test_pagination(client, make_member, make_claim, as_member):
    alice = make_member()
    for _ in range(3):
        make_claim(alice["id"])

    page1 = client.get("/claims?limit=2&offset=0", headers=as_member(alice)).get_json()
    page2 = client.get("/claims?limit=2&offset=2", headers=as_member(alice)).get_json()

    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 1
    assert page1["total"] == page2["total"] == 3
    ids = [c["id"] for c in page1["items"] + page2["items"]]
    assert len(set(ids)) == 3  # no overlap between pages


@pytest.mark.parametrize(
    "query", ["limit=0", "limit=101", "limit=abc", "offset=-1"]
)
def test_invalid_pagination_returns_400(client, make_member, as_member, query):
    alice = make_member()
    res = client.get(f"/claims?{query}", headers=as_member(alice))
    assert res.status_code == 400


def test_list_requires_member_header(client):
    assert client.get("/claims").status_code == 401


def test_get_own_claim(client, make_member, make_claim, as_member):
    alice = make_member()
    claim = make_claim(alice["id"])
    res = client.get(f"/claims/{claim['id']}", headers=as_member(alice))
    assert res.status_code == 200
    assert res.get_json()["id"] == claim["id"]


def test_other_members_claim_returns_404(client, make_member, make_claim, as_member):
    alice = make_member("Alice")
    bob = make_member("Bob")
    claim = make_claim(alice["id"])
    res = client.get(f"/claims/{claim['id']}", headers=as_member(bob))
    assert res.status_code == 404


def test_missing_claim_returns_404(client, make_member, as_member):
    alice = make_member()
    res = client.get("/claims/9999", headers=as_member(alice))
    assert res.status_code == 404


def test_non_numeric_claim_id_returns_json_404(client, make_member, as_member):
    alice = make_member()
    res = client.get("/claims/abc", headers=as_member(alice))
    assert res.status_code == 404
    assert res.is_json