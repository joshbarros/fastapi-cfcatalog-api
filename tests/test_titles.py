from httpx import AsyncClient


async def _seed_refs(client: AsyncClient) -> dict[str, str]:
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


async def _movie_payload(refs: dict[str, str], title: str = "Barbie") -> dict:
    return {
        "type": "MOVIE",
        "title": title,
        "description": "x",
        "release_year": 2023,
        "duration_seconds": 6840,
        "rating": "AGE_12",
        "category_ids": [refs["category_id"]],
        "genre_ids": [refs["genre_id"]],
        "cast_member_ids": [refs["cast_member_id"]],
    }


async def test_create_movie(client: AsyncClient) -> None:
    refs = await _seed_refs(client)
    response = await client.post("/api/v1/titles", json=await _movie_payload(refs))
    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "MOVIE"
    assert body["parent_id"] is None
    assert body["category_ids"] == [refs["category_id"]]


async def test_create_series_season_episode_hierarchy(client: AsyncClient) -> None:
    refs = await _seed_refs(client)

    series = (
        await client.post(
            "/api/v1/titles",
            json={
                "type": "SERIES",
                "title": "Stranger Things",
                "description": "Kids vs. Demogorgons",
                "release_year": 2016,
                "rating": "AGE_14",
                "category_ids": [refs["category_id"]],
                "genre_ids": [refs["genre_id"]],
            },
        )
    ).json()
    assert series["type"] == "SERIES"

    season = (
        await client.post(
            "/api/v1/titles",
            json={
                "type": "SEASON",
                "parent_id": series["id"],
                "title": "Season 1",
                "description": "Will Byers disappears",
                "season_number": 1,
                "rating": "AGE_14",
            },
        )
    ).json()
    assert season["type"] == "SEASON"
    assert season["parent_id"] == series["id"]

    episode = (
        await client.post(
            "/api/v1/titles",
            json={
                "type": "EPISODE",
                "parent_id": season["id"],
                "title": "Chapter One: The Vanishing of Will Byers",
                "description": "pilot",
                "season_number": 1,
                "episode_number": 1,
                "duration_seconds": 2820,
                "air_date": "2016-07-15",
                "rating": "AGE_14",
            },
        )
    ).json()
    assert episode["type"] == "EPISODE"
    assert episode["parent_id"] == season["id"]
    assert episode["episode_number"] == 1


async def test_movie_with_parent_rejected(client: AsyncClient) -> None:
    refs = await _seed_refs(client)
    series = (
        await client.post(
            "/api/v1/titles",
            json={
                "type": "SERIES",
                "title": "S",
                "description": "x",
                "rating": "L",
            },
        )
    ).json()
    response = await client.post(
        "/api/v1/titles",
        json={**await _movie_payload(refs), "parent_id": series["id"]},
    )
    assert response.status_code == 422


async def test_episode_without_parent_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/titles",
        json={
            "type": "EPISODE",
            "title": "Orphan",
            "description": "x",
            "episode_number": 1,
            "duration_seconds": 60,
            "rating": "L",
        },
    )
    assert response.status_code == 422


async def test_season_under_movie_rejected(client: AsyncClient) -> None:
    refs = await _seed_refs(client)
    movie = (await client.post("/api/v1/titles", json=await _movie_payload(refs))).json()

    response = await client.post(
        "/api/v1/titles",
        json={
            "type": "SEASON",
            "parent_id": movie["id"],
            "title": "Bad season",
            "description": "x",
            "season_number": 1,
            "rating": "L",
        },
    )
    assert response.status_code == 422


async def test_validation_rejects_bad_year(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/titles",
        json={
            "type": "MOVIE",
            "title": "Bad Year",
            "description": "x",
            "release_year": 1500,
            "duration_seconds": 60,
            "rating": "L",
        },
    )
    assert response.status_code == 422
