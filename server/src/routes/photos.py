from sqlalchemy.future import select
from src.database.models import User, Picture
from src.schemas.photos import PictureUpload, PictureResponse, PictureUpdate
from src.repository import photos as repository_pictures
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.photos import PictureUpload
from src.services.auth import auth_service
from typing import List, Optional
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


router = APIRouter(prefix='/photos', tags=['photos'])


@router.post("/", response_model=PictureUpload)
async def post_picture(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: List[str] = [],
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Route handler for uploading pictures.
    This function handles POST requests to '/pictures/' for uploading new pictures.

    :param picture: The picture to upload.
    :type picture: PictureUpload model.
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: The uploaded picture.
    :rtype: Picture model

    """
    picture = await repository_pictures.post_picture(description, tags, current_user.id, file.file, db)
    return picture


@router.get("/{picture_id}", response_model=PictureResponse)
# async def get_picture(picture_id: int, db: Session = Depends(get_db),
#                       current_user: User = Depends(auth_service.get_current_user)):
async def get_picture(picture_id: int, db: AsyncSession = Depends(get_db)):
    """
    Route handler for retrieving a specific picture.

    This function handles GET requests to '/picture/{picture_id}' for retrieving a specific picture.

    :param picture_id: The ID of the picture to retrieve.
    :type picture_id: int
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: The retrieved picture data.
    :rtype: PictureResponse form

    Raises:
    HTTPException: If the picture is not found.

    """
    try:
        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalars().first()
        return picture
    except Exception as e:
        logging.error(f"Error fetching picture: {e}")
        raise


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(
    picture_id: int,
    description: Optional[str] = Form(None),
    tags: List[str] = [],
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):

    picture = await update_picture(picture_id, description, tags, current_user.id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture
