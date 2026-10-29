import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Media, User
from app.schemas import MediaResponse

router = APIRouter(prefix="/api", tags=["media"])

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)


@router.post("/medias", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Загрузка медиа"""
    filename = file.filename or "uploaded_file"
    file_extension = Path(filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = MEDIA_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_media = Media(file_path=str(file_path))
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)

    return MediaResponse(media_id=new_media.id)
