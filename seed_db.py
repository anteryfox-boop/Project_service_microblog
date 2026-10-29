import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Tweet, User, Media


async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        if result.scalars().first():
            return

        user1 = User(
            name="Test User",
            nickname="test",
            api_key="test",
            description="Тестовый пользователь",
        )
        user2 = User(
            name="Cool Dev",
            nickname="cooldev",
            api_key="cooldev",
            description="Разработчик",
        )
        user3 = User(
            name="Olga",
            nickname="olga",
            api_key="olga",
            description="Автор проекта",
        )

        session.add_all([user1, user2, user3])
        await session.commit()

        await session.refresh(user1, ["following", "followers"])
        await session.refresh(user2, ["following", "followers"])
        await session.refresh(user3, ["following", "followers"])

        tweet1 = Tweet(content="Привет, мир! Это мой первый твит.", user_id=user2.id)
        tweet2 = Tweet(content="FastAPI — это огонь! 🔥", user_id=user1.id)
        tweet3 = Tweet(content="Пишу бэкенд для микроблога.", user_id=user3.id)

        session.add_all([tweet1, tweet2, tweet3])
        await session.commit()

        media1 = Media(file_path="olga_post.jpg")
        session.add(media1)
        await session.commit()
        await session.refresh(media1)

        tweet_with_media = Tweet(
            content="Смотрите, какой классный котик!",
            user_id=user3.id
        )
        tweet_with_media.attachments.append(media1)

        session.add(tweet_with_media)
        await session.commit()

        await session.refresh(tweet1, ["liked_by"])
        await session.refresh(tweet2, ["liked_by"])
        await session.refresh(tweet3, ["liked_by"])
        await session.refresh(tweet_with_media, ["liked_by"])

        user1.following.append(user2)
        user1.following.append(user3)
        user2.following.append(user1)

        tweet1.liked_by.append(user1)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
