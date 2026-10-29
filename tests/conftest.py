import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.database import Base, get_db
from app.main import app
from app.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создает все таблицы перед тестами и удаляет после"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """Возвращает клиент для запросов к API"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def create_user_user(async_client):
    """Создает пользователя "test" перед каждым тестом и удаляет после."""
    async with TestingSessionLocal() as session:
        user = User(id=1, name="Test", nickname="test", api_key="test")
        session.add(user)
        await session.commit()

    yield

    async with TestingSessionLocal() as session:
        from app.models import (followers_association, likes_association,
                                tweet_media_association)

        await session.execute(delete(likes_association))
        await session.execute(delete(followers_association))
        await session.execute(delete(tweet_media_association))

        from app.models import Media, Tweet

        await session.execute(delete(Tweet))
        await session.execute(delete(Media))

        await session.execute(delete(User))
        await session.commit()


@pytest.fixture
def cleanup_media():
    """
    Фикстура, которая запоминает файлы в папке media до теста
    и удаляет все новые файлы после его завершения.
    """
    media_dir = "media"

    files_before = set(os.listdir(media_dir)) if os.path.exists(media_dir) else set()

    yield

    if os.path.exists(media_dir):
        files_after = set(os.listdir(media_dir))
        new_files = files_after - files_before

        for file_name in new_files:
            file_path = os.path.join(media_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)


@pytest_asyncio.fixture
async def second_user():
    """Создает второго пользователя для тестов."""
    async with TestingSessionLocal() as session:
        new_user = User(id=2, name="Alina", nickname="alina", api_key="secret")
        session.add(new_user)

        await session.commit()
        await session.refresh(new_user)

        return new_user


@pytest_asyncio.fixture
async def db_session():
    """Фикстура для получения сессии к тестовой БД."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def auth_headers():
    """Возвращает заголовки для авторизации по умолчанию(test_user)"""
    return {"api-key": "test"}


@pytest.fixture
def auth_second_headers():
    """Возвращает заголовки для авторизации второго пользователя(Alina)."""
    return {"api-key": "secret"}


@pytest_asyncio.fixture
async def tweet_from_second_user(async_client, auth_second_headers):
    """Создает твит от лица второго пользователя. Исп-ся для тестов на удаление чужого твита и лайки."""
    response = await async_client.post(
        "/api/tweets",
        json={"tweet_data": "Alinas tweet", "tweet_media_ids": []},
        headers=auth_second_headers,
    )
    assert response.status_code == 200

    tweet_data = response.json()
    return tweet_data["tweet_id"]
