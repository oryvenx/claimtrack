def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_health_db(client):
    res = client.get("/health/db")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok", "database": "reachable"}


def test_unknown_route_returns_json_404(client):
    res = client.get("/nope")
    assert res.status_code == 404
    assert res.is_json
    assert "error" in res.get_json()