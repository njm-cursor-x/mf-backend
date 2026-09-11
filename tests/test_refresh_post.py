from ingest.refresh import main, post_snapshot


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


def test_post_url_succeeds_when_fandango_fetch_fails(tmp_path, monkeypatch):
    snap = tmp_path / "seed.json"
    snap.write_text('{"source":"seed"}', encoding="utf-8")
    monkeypatch.setenv("MF_API_KEY", "mf_live_x")
    monkeypatch.setattr("ingest.refresh.refresh_from_fandango", lambda: 1)
    monkeypatch.setattr("ingest.refresh.latest_snapshot_path", lambda: snap)
    monkeypatch.setattr("ingest.refresh.post_snapshot", lambda *args, **kwargs: 0)
    assert (
        main(
            [
                "--source",
                "fandango",
                "--post-url",
                "https://web-production-b3a9ce.up.railway.app",
            ]
        )
        == 0
    )


def test_post_url_fails_when_live_post_fails(tmp_path, monkeypatch):
    snap = tmp_path / "seed.json"
    snap.write_text('{"source":"seed"}', encoding="utf-8")
    monkeypatch.setenv("MF_API_KEY", "mf_live_x")
    monkeypatch.setattr("ingest.refresh.refresh_from_fandango", lambda: 1)
    monkeypatch.setattr("ingest.refresh.latest_snapshot_path", lambda: snap)
    monkeypatch.setattr("ingest.refresh.post_snapshot", lambda *args, **kwargs: 1)
    assert (
        main(
            [
                "--source",
                "fandango",
                "--post-url",
                "https://web-production-b3a9ce.up.railway.app",
            ]
        )
        == 1
    )
