import pytest


@pytest.mark.asyncio
async def test_test_generate_tweet_unauthorized(async_client):
    """Тест: попытка получить ленту твитов без api-key."""
    response = await async_client.get("/api/tweets")

    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_get_tweets_success(async_client, auth_headers):
    """Тест: с правильным api-key лента успешно отдается. 200"""
    response = await async_client.get("/api/tweets", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "tweets" in data
    assert isinstance(data["tweets"], list)


@pytest.mark.asyncio
async def test_create_new_tweet(async_client, auth_headers):
    """Тест: Создание твита. 200"""
    payload = {"tweet_data": "Testing tweet", "tweet_media_ids": []}
    response = await async_client.post(
        "/api/tweets", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data


@pytest.mark.asyncio
async def test_delete_my_tweet(async_client, auth_headers):
    """Тест: Удаление своего твита. 200"""
    payload = {"tweet_data": "Testing tweet", "tweet_media_ids": []}
    response = await async_client.post(
        "/api/tweets", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    tweet_id = response.json()["tweet_id"]

    new_response = await async_client.delete(
        f"/api/tweets/{tweet_id}", headers=auth_headers
    )

    assert new_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_other_tweet_forbidden(
    async_client, auth_headers, second_user, tweet_from_second_user
):
    """Тест: нельзя удалить чужой твит. 403"""
    response = await async_client.delete(
        f"/api/tweets/{tweet_from_second_user}", headers=auth_headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_incorrect_tweet(async_client, auth_headers):
    """Тест: попытка удалить несуществующий твит. 404"""
    response = await async_client.delete("api/tweets/999", headers=auth_headers)
    assert response.status_code == 404
