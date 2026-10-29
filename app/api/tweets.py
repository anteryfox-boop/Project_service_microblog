from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Media, Tweet, User, likes_association
from app.schemas import (ResultResponse, TweetAuthor, TweetCreate,
                         TweetCreateResponse, TweetLike, TweetResponse,
                         TweetsListResponse)

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.get("", response_model=TweetsListResponse)
async def get_tweets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение ленты твитов."""
    following_result = await db.execute(
        select(User.id).where(User.followers.any(id=current_user.id))
    )
    following_ids = following_result.scalars().all()

    if not following_ids:
        return TweetsListResponse(tweets=[])

    likes_count = (
        select(
            Tweet.id.label("tweet_id"),
            func.count(likes_association.c.user_id).label("likes_count"),
        )
        .outerjoin(likes_association, Tweet.id == likes_association.c.tweet_id)
        .group_by(Tweet.id)
        .subquery()
    )

    result = await db.execute(
        select(Tweet)
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.liked_by),
            selectinload(Tweet.attachments),
        )
        .join(likes_count, Tweet.id == likes_count.c.tweet_id)
        .where(Tweet.user_id.in_(following_ids))
        .order_by(desc(likes_count.c.likes_count), Tweet.created_at.desc())
    )
    tweets = result.scalars().all()

    response_tweets = []
    for tweet in tweets:
        likes_data = [
            TweetLike(id=user.id, name=user.name, user_id=user.id)
            for user in tweet.liked_by
        ]
        media_urls = [
            f"/media/{media.file_path.split('/')[-1]}" for media in tweet.attachments
        ]
        response_tweets.append(
            TweetResponse(
                id=tweet.id,
                content=tweet.content,
                author=TweetAuthor(id=tweet.author.id, name=tweet.author.name),
                likes=likes_data,
                attachments=media_urls,
            )
        )

    return TweetsListResponse(tweets=response_tweets)


@router.post("", response_model=TweetCreateResponse)
async def create_tweet(
    tweet_data: TweetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание твита"""
    new_tweet = Tweet(
        content=tweet_data.tweet_data, user_id=current_user.id, attachments=[]
    )

    db.add(new_tweet)
    await db.flush()

    if tweet_data.tweet_media_ids:
        result = await db.execute(
            select(Media).where(Media.id.in_(tweet_data.tweet_media_ids))
        )
        media_list = result.scalars().all()

        for media in media_list:
            new_tweet.attachments.append(media)

    await db.commit()
    await db.refresh(new_tweet)

    return TweetCreateResponse(tweet_id=new_tweet.id)


@router.delete("/{tweet_id}", response_model=ResultResponse)
async def delete_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаление твита"""
    result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = result.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    if tweet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tweets",
        )

    await db.delete(tweet)
    await db.commit()

    return ResultResponse()


@router.post("/{tweet_id}/likes", response_model=ResultResponse)
async def like_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Лайк твита"""
    result = await db.execute(
        select(Tweet).options(selectinload(Tweet.liked_by)).where(Tweet.id == tweet_id)
    )
    tweet = result.scalar_one_or_none()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if current_user in tweet.liked_by:
        raise HTTPException(status_code=400, detail="You already liked this tweet")

    tweet.liked_by.append(current_user)

    await db.commit()

    return ResultResponse()


@router.delete("/{tweet_id}/likes", response_model=ResultResponse)
async def unlike_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаление лайка с твита"""
    result = await db.execute(
        select(Tweet).options(selectinload(Tweet.liked_by)).where(Tweet.id == tweet_id)
    )
    tweet = result.scalar_one_or_none()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if current_user not in tweet.liked_by:
        raise HTTPException(status_code=400, detail="You dont like this tweet")

    tweet.liked_by.remove(current_user)

    await db.commit()

    return ResultResponse()
