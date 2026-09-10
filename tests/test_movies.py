def test_list_movies(client, auth_headers):
    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    titles = {m["title"] for m in response.json()["movies"]}
    assert "The Odyssey" in titles
    assert "Spider-Man: Brand New Day" in titles


def test_list_movies_filtered_by_zip(client, auth_headers):
    response = client.get("/movies", params={"zip_code": "10027"}, headers=auth_headers)
    assert response.status_code == 200
    titles = {m["title"] for m in response.json()["movies"]}
    assert "Spider-Man: Brand New Day" in titles


def test_get_movie(client, auth_headers):
    response = client.get("/movies/the-odyssey", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "The Odyssey"


def test_unknown_movie(client, auth_headers):
    response = client.get("/movies/not-a-film", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_spoken_title_search(client, auth_headers):
    response = client.get(
        "/movies/search",
        params={"q": "jurasic... wait no, the odysy"},
        headers=auth_headers,
    )
    # still should miss; use a real near-miss
    response = client.get("/movies/search", params={"q": "the odysy"}, headers=auth_headers)
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert matches
    assert matches[0]["id"] == "the-odyssey"


def test_spoken_spider_man(client, auth_headers):
    response = client.get(
        "/movies/search",
        params={"q": "spider man brand new day"},
        headers=auth_headers,
    )
    assert response.json()["matches"][0]["id"] == "spider-man-brand-new-day"
