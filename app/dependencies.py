from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User


async def get_current_user(
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Находит пользователя по api-key из заголовка"""
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "result": False,
                "error_type": "auth_error",
                "error_message": "Invalid api-key",
            },
        )

    return user
