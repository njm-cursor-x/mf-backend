def test_resolve_manhattan_zip(client, auth_headers):
    response = client.get("/zips/10023", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["neighborhood"] == "Lincoln Square"
    ids = {t["id"] for t in body["theaters"]}
    assert "amc-lincoln-square-13" in ids


def test_out_of_area_zip(client, auth_headers):
    response = client.get("/zips/11201", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "OUT_OF_AREA"
