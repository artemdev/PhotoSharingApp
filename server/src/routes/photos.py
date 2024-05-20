from server.src.schemas import PictureUpload, PictureResponse, PictureUpdate
from server.src.repository import photos as repository_pictures
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import PictureUpload

router = APIRouter(prefix='/photos', tags=['photos'])


@router.post("/", response_model=PictureUpload)
async def post_picture(description: str, tags: List[str], file: UploadFile = File(...), db: Session = Depends(get_db)):

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
    picture = await repository_pictures.post_picture(description, tags, file.file, db)
    return picture

@router.get("/{picture_id}", response_model=PictureResponse)
# async def get_picture(picture_id: int, db: Session = Depends(get_db),
#                       current_user: User = Depends(auth_service.get_current_user)):
async def get_picture(picture_id: int, db: Session = Depends(get_db)):
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
    picture = await repository_pictures.get_picture(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture

@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(
    picture_id: int,
    picture_update: PictureUpdate,
    db: Session = Depends(get_db)
):
    picture = await repository_pictures.update_picture(picture_id, picture_update, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture
