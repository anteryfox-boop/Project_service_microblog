from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

followers_association = Table(
    "followers",
    Base.metadata,
    Column(
        "follower_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "following_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


likes_association = Table(
    "likes",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tweet_id",
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


tweet_media_association = Table(
    "tweet_media",
    Base.metadata,
    Column(
        "tweet_id",
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "media_id",
        Integer,
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(100), nullable=True)

    tweets: Mapped[list["Tweet"]] = relationship(
        "Tweet",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=id == followers_association.c.following_id,
        secondaryjoin=id == followers_association.c.follower_id,
        back_populates="following",
    )

    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=id == followers_association.c.follower_id,
        secondaryjoin=id == followers_association.c.following_id,
        back_populates="followers",
    )

    liked_tweets: Mapped[list["Tweet"]] = relationship(
        "Tweet",
        secondary=likes_association,
        back_populates="liked_by",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="tweets",
    )

    attachments: Mapped[list["Media"]] = relationship(
        "Media",
        secondary=tweet_media_association,
        back_populates="tweets",
    )

    liked_by: Mapped[list["User"]] = relationship(
        "User", secondary=likes_association, back_populates="liked_tweets"
    )


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    tweets: Mapped[list["Tweet"]] = relationship(
        "Tweet", secondary=tweet_media_association, back_populates="attachments"
    )
