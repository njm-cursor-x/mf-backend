from ingest.refresh import post_snapshot


def test_post_snapshot_ok(tmp_path, monkeypatch):
    path = tmp_path / "snap.json"
    path.write_text('{"source":"test"}', encoding="utf-8")

    class Fake:
        status_code = 200
        text = '{"ingest_status":"ok"}'

    monkeypatch.setattr("ingest.refresh.httpx.post", lambda *args, **kwargs: Fake())
    assert post_snapshot("https://example.up.railway.app/", path, "mf_live_x") == 0


def test_post_snapshot_fails(tmp_path, monkeypatch):
    path = tmp_path / "snap.json"
    path.write_text("{}", encoding="utf-8")

    class Fake:
        status_code = 401
        text = '{"code":"UNAUTHORIZED"}'

    monkeypatch.setattr("ingest.refresh.httpx.post", lambda *args, **kwargs: Fake())
    assert post_snapshot("https://example.up.railway.app", path, "nope") == 1
