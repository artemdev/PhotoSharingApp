import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from src.database.db import get_db
from src.database.models import User, Picture
from src.repository.users import get_user_photo_count
from src.schemas.user import UserGet, UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])

# Configure Cloudinary
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserGet,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the current user.

    :param user: User object retrieved from authentication service.
    :param db: AsyncSession instance for database interaction.
    :return: UserResponse containing user details.
    """
    num_photos = await get_user_photo_count(user.id, db)

    return UserGet(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        role=user.role,
        registered_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        num_photos=num_photos,
    )


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_user_avatar(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Updates the current user's avatar.

    :param file: Uploaded file containing the new avatar image.
    :param user: User object retrieved from authentication service.
    :param db: AsyncSession instance for database interaction.
    :return: Updated UserResponse containing user details.
    """
    public_id = f"App id №{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
