import io

import pytest

FAKE_IMAGE_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.mark.asyncio
async def test_upload_media_success(async_client, auth_headers, cleanup_media):
    """ "Тест: успешная загрука медиафайла."""
    file = io.BytesIO(FAKE_IMAGE_BYTES)
    file.name = "test_image.png"

    response = await async_client.post(
        "api/medias",
        files={"file": ("test_image.png", file, "image/png")},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True

    assert "media_id" in data
    assert isinstance(data["media_id"], int)
