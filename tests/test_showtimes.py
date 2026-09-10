def test_showtimes_grouped_by_theater(client, auth_headers):
    response = client.get(
        "/showtimes",
        params={"movie_id": "the-odyssey", "date": "today"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["movie"]["id"] == "the-odyssey"
    assert body["theaters"]
    lincoln = next(
        block for block in body["theaters"] if block["theater"]["id"] == "amc-lincoln-square-13"
    )
    formats = {item["format"] for item in lincoln["times"]}
    assert "IMAX" in formats
    assert lincoln["times"][0]["starts_at_local"]


def test_showtimes_zip_filter(client, auth_headers):
    response = client.get(
        "/showtimes",
        params={"movie_id": "the-odyssey", "zip_code": "10023"},
        headers=auth_headers,
    )
    ids = {block["theater"]["id"] for block in response.json()["theaters"]}
    assert "amc-lincoln-square-13" in ids


def test_list_theaters_for_movie(client, auth_headers):
    response = client.get(
        "/theaters",
        params={"movie_id": "the-odyssey", "date": "today"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    ids = {t["id"] for t in response.json()}
    assert "amc-lincoln-square-13" in ids
