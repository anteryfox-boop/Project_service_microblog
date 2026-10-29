import pytest


@pytest.mark.asyncio
async def test_like_success(
    async_client, auth_headers, second_user, tweet_from_second_user
):
    """Тест: Успешная постановка лайка"""
    response = await async_client.post(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_like_twice_forbidden(
    async_client, auth_headers, second_user, tweet_from_second_user
):
    """Тест: попытка дважды поставить лайк. 400"""
    response = await async_client.post(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )
    assert response.status_code == 200

    new_response = await async_client.post(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )

    assert new_response.status_code == 400


@pytest.mark.asyncio
async def test_unlike_tweet(
    async_client, auth_headers, second_user, tweet_from_second_user
):
    """Тест: Удаление лайка с твита. 200"""
    response = await async_client.post(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )
    assert response.status_code == 200

    new_response = await async_client.delete(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )

    assert new_response.status_code == 200


@pytest.mark.asyncio
async def test_unlike_incorrect_tweet(async_client, auth_headers):
    """Тест: Попытка удалить лайк с твита, которого не существует. 404"""
    response = await async_client.delete("/api/tweets/999/likes", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unlike_tweet_forbidden(
    async_client, auth_headers, second_user, tweet_from_second_user
):
    """Тест: удалить лайк, которого нет. 400"""
    response = await async_client.delete(
        f"/api/tweets/{tweet_from_second_user}/likes", headers=auth_headers
    )

    assert response.status_code == 400
