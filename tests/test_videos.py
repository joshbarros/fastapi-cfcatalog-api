from httpx import AsyncClient


async def _seed(client: AsyncClient) -> dict[str, str]:
    cat = (await client.post("/api/v1/categories", json={"name": "Movies"})).json()
    genre = (
        await client.post(
            "/api/v1/genres",
            json={"name": "Drama", "category_ids": [cat["id"]]},
        )
    ).json()
    director = (
        await client.post(
            "/api/v1/cast-members",
            json={"name": "Greta Gerwig", "type": "DIRECTOR"},
        )
    ).json()
    return {
        "category_id": cat["id"],
        "genre_id": genre["id"],
        "cast_member_id": director["id"],
    }


async def test_create_video_with_relations(client: AsyncClient) -> None:
    refs = await _seed(client)

    response = await client.post(
        "/api/v1/videos",
        json={
            "title": "Barbie",
            "description": "Barbie steps out of Barbieland.",
            "release_year": 2023,
            "duration": 6840,
            "rating": "AGE_12",
            "opened": True,
            "published": True,
            "category_ids": [refs["category_id"]],
            "genre_ids": [refs["genre_id"]],
            "cast_member_ids": [refs["cast_member_id"]],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Barbie"
    assert body["category_ids"] == [refs["category_id"]]
    assert body["genre_ids"] == [refs["genre_id"]]
    assert body["cast_member_ids"] == [refs["cast_member_id"]]


async def test_video_validation_rejects_bad_year(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/videos",
        json={
            "title": "Bad Year",
            "description": "x",
            "release_year": 1500,
            "duration": 60,
            "rating": "L",
        },
    )
    assert response.status_code == 422
