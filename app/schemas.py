from pydantic import (AliasChoices, BaseModel, ConfigDict, Field,
                      field_validator, model_validator)


class UserShort(BaseModel):
    """Краткая информация о пользователе (для вложенных объектов)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserResponse(BaseModel):
    """Полная информация о текущем пользователе."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    followers: list[UserShort]
    following: list[UserShort]


class UserProfileResponse(BaseModel):
    """Ответ для GET /api/users/<id>"""

    result: bool = True
    user: UserResponse


class TweetCreate(BaseModel):
    """Схема для создания твита"""

    tweet_data: str
    tweet_media_ids: list[int] = []


class TweetCreateResponse(BaseModel):
    """Ответ после создания твита"""

    result: bool = True
    tweet_id: int


class TweetAuthor(BaseModel):
    """Краткая информация об авторе"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TweetLike(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    user_id: int | None = None

    @model_validator(mode="after")
    def fill_user_id(self):
        if self.user_id is None:
            self.user_id = self.id
        return self


class TweetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    author: TweetAuthor
    likes: list[TweetLike] = Field(
        default=[], validation_alias=AliasChoices("liked_by", "likes")
    )
    attachments: list[str] = []

    @field_validator("attachments", mode="before")
    @classmethod
    def media_to_urls(cls, value):
        if value and isinstance(value, list) and hasattr(value[0], "file_path"):
            return [f"/media/{media.file_path.split('/')[-1]}" for media in value]
        return value


class TweetsListResponse(BaseModel):
    """Ответ для GET /api/tweets"""

    result: bool = True
    tweets: list[TweetResponse]


class ResultResponse(BaseModel):
    """Универсальный ответ для действий(follow, unfollow, like)"""

    result: bool = True


class MediaResponse(BaseModel):
    result: bool = True
    media_id: int
