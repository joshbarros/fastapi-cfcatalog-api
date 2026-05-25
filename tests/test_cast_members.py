from httpx import AsyncClient


async def test_create_and_list_cast_members(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/cast-members",
        json={"name": "Christopher Nolan", "type": "DIRECTOR"},
    )
    assert response.status_code == 201
    assert response.json()["type"] == "DIRECTOR"

    await client.post(
        "/api/v1/cast-members",
        json={"name": "Cillian Murphy", "type": "ACTOR"},
    )

    response = await client.get("/api/v1/cast-members")
    assert response.status_code == 200
    types = {c["type"] for c in response.json()}
    assert {"DIRECTOR", "ACTOR"} <= types
