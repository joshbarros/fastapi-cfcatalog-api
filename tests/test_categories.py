from httpx import AsyncClient

PREFIX = "/api/v1/categories"


async def test_create_and_get_category(client: AsyncClient) -> None:
    response = await client.post(PREFIX, json={"name": "Movies", "description": "Feature films"})
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Movies"
    assert created["is_active"] is True

    response = await client.get(f"{PREFIX}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_list_categories(client: AsyncClient) -> None:
    for name in ("Action", "Drama"):
        await client.post(PREFIX, json={"name": name})

    response = await client.get(PREFIX)
    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    assert {"Action", "Drama"} <= names


async def test_update_and_delete_category(client: AsyncClient) -> None:
    created = (await client.post(PREFIX, json={"name": "Old"})).json()

    response = await client.patch(f"{PREFIX}/{created['id']}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"

    response = await client.delete(f"{PREFIX}/{created['id']}")
    assert response.status_code == 204

    response = await client.get(f"{PREFIX}/{created['id']}")
    assert response.status_code == 404


async def test_get_missing_category_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"{PREFIX}/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
