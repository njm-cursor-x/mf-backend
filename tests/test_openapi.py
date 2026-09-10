def test_operation_ids_present(client):
    spec = client.get("/openapi.json").json()
    ids = {
        spec["paths"][path][method].get("operationId")
        for path, methods in spec["paths"].items()
        for method in methods
        if method in {"get", "post", "put", "patch", "delete"}
    }
    assert {
        "health",
        "get_meta",
        "resolve_zip",
        "search_movies",
        "list_movies",
        "get_movie",
        "list_theaters",
        "get_showtimes",
        "ingest_snapshot",
    }.issubset(ids)
    assert spec["components"]["securitySchemes"]["ApiKeyAuth"]["name"] == "X-API-Key"
