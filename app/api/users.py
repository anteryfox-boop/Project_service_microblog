from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ResultResponse, UserProfileResponse, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение информации о своем профиле"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()

    return UserProfileResponse(user=UserResponse.model_validate(user))


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получение информации о пользователе по его user_id"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "not found",
                "error_message": f"User with id {user_id} not found",
            },
        )

    return UserProfileResponse(user=UserResponse.model_validate(user))


@router.post("/{user_id}/follow", response_model=ResultResponse)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Подписка на пользователя по его user_id"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail=" You cannot follow yourself")

    result = await db.execute(
        select(User).options(selectinload(User.followers)).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()

    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user in target_user.followers:
        raise HTTPException(
            status_code=400, detail="You are already following this user"
        )

    target_user.followers.append(current_user)

    await db.commit()

    return ResultResponse()


@router.delete("/{user_id}/follow", response_model=ResultResponse)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаление подписки с пользователя по его user_id"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail=" You cannot unfollow yourself")

    result = await db.execute(
        select(User).options(selectinload(User.followers)).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()

    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user not in target_user.followers:
        raise HTTPException(status_code=400, detail="You are not following this user")

    target_user.followers.remove(current_user)
    await db.commit()

    return ResultResponse()
