from httpx import AsyncClient


async def test_create_genre_with_categories(client: AsyncClient) -> None:
    cat = (await client.post("/api/v1/categories", json={"name": "Movies"})).json()

    response = await client.post(
        "/api/v1/genres",
        json={"name": "Sci-Fi", "category_ids": [cat["id"]]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Sci-Fi"
    assert body["category_ids"] == [cat["id"]]


async def test_create_genre_rejects_unknown_category(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/genres",
        json={
            "name": "Sci-Fi",
            "category_ids": ["00000000-0000-0000-0000-000000000000"],
        },
    )
    assert response.status_code == 422
