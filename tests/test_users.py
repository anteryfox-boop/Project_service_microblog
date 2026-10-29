import pytest


@pytest.mark.asyncio
async def test_get_my_profile_failed(async_client):
    """Тест: попытка получения своего профиля без api-key. 401/422"""
    response = await async_client.get("/api/users/me")

    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_get_my_profile_success(async_client, auth_headers):
    """Тест: успешное получение своего профиля. 200"""
    response = await async_client.get("/api/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["name"] == "Test"


@pytest.mark.asyncio
async def test_get_user_profile(async_client, db_session, auth_headers, second_user):
    """Тест: успешное получение другого пользователя по его id. 200"""
    response = await async_client.get(
        f"/api/users/{second_user.id}", headers=auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_incorrect_user(async_client, auth_headers):
    """Тест: попытка получить профиль несуществующего пользователя. 404"""
    response = await async_client.get("api/users/999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_follow_user(async_client, db_session, auth_headers, second_user):
    """Тест: Успешная подписка на другого пользователя. 200"""
    response = await async_client.post(
        f"api/users/{second_user.id}/follow", headers=auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_follow_yourself_forbidden(async_client, auth_headers):
    """Тест: Попытка подписаться на себя 400"""
    response = await async_client.post("/api/users/1/follow", headers=auth_headers)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_follow_user_twice_forbidden(async_client, auth_headers, second_user):
    """Тест: нельзя подписаться на пользователя дважды"""
    response = await async_client.post(
        f"/api/users/{second_user.id}/follow", headers=auth_headers
    )

    assert response.status_code == 200

    new_response = await async_client.post(
        f"/api/users/{second_user.id}/follow", headers=auth_headers
    )

    assert new_response.status_code == 400


@pytest.mark.asyncio
async def test_unfollow_user(async_client, auth_headers, second_user):
    response = await async_client.post(
        f"/api/users/{second_user.id}/follow", headers=auth_headers
    )

    assert response.status_code == 200

    new_response = await async_client.delete(
        f"/api/users/{second_user.id}/follow", headers=auth_headers
    )

    assert new_response.status_code == 200
