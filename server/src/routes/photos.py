from src.database.models import User, Picture
from src.repository.photos import PictureRepository
from fastapi import UploadFile, File, Form
import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.auth import auth_service
from src.schemas.photos import PictureUpload, PictureResponse

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

router = APIRouter(prefix='/photos', tags=['photos'])


@router.get("/search", response_model=List[PictureResponse])
async def search_pictures(
        search_term: Optional[str] = Query(None),
        tag: Optional[str] = Query(None),
        user_id: Optional[int] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        db: AsyncSession = Depends(get_db),
):
    """
    Route handler for searching pictures.

    :param search_term: The search term to filter by.
    :type search_term: Optional[str]
    :param tag: The tag to filter by.
    :type tag: Optional[str]
    :param user_id: The ID of the user to filter by.
    :type user_id: Optional[int]
    :param page: The page number for pagination.
    :type page: int
    :param page_size: The number of items per page.
    :type page_size: int
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of pictures matching the search criteria.
    :rtype: List[PictureResponse]
    """
    pictures = await PictureRepository.search_pictures(db=db, search_term=search_term, tag=tag, user_id=user_id, page=page, page_size=page_size)

    return pictures

@router.post("/", response_model=PictureResponse)
async def post_picture(
        file: UploadFile = File(...),
        description: Optional[str] = Form(None),
        tags: List[str] = Form([]),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Route handler for uploading pictures.

    :param file: The file to be uploaded.
    :type file: UploadFile
    :param description: The description of the picture.
    :type description: Optional[str]
    :param tags: A list of tags associated with the picture.
    :type tags: List[str]
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The uploaded picture.
    :rtype: PictureResponse
    """
    try:
        tags_list = tags[0].split(",") if tags else []
        picture = await PictureRepository.post_picture(description, tags_list, file.file, current_user.id, db)
        return picture

    except Exception as e:
        logging.error(f"Error in post_picture endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{picture_id}", response_model=PictureResponse)
async def get_picture(
        picture_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for retrieving a specific picture.

    :param picture_id: The ID of the picture to retrieve.
    :type picture_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The retrieved picture.
    :rtype: PictureResponse
    """
    picture = await PictureRepository.get_picture(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(
        picture_id: int,
        description: Optional[str] = Form(None),
        tags: List[str] = Form([]),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Route handler for updating a picture.

    :param picture_id: The ID of the picture to update.
    :type picture_id: int
    :param description: The new description of the picture.
    :type description: Optional[str]
    :param tags: A list of new tags for the picture.
    :type tags: List[str]
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated picture.
    :rtype: PictureResponse
    """
    tags_list = tags[0].split(",") if tags else None
    picture = await PictureRepository.update_picture(picture_id, description, tags_list, current_user.id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.post("/transform/{picture_id}", response_model=PictureResponse)
async def resize_picture(
        picture_id: int,
        width: Optional[int] = Query(None),
        height: Optional[int] = Query(None),
        crop: Optional[str] = Query(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for resizing a picture.

    :param picture_id: The ID of the picture to resize.
    :type picture_id: int
    :param width: The new width of the picture.
    :type width: Optional[int]
    :param height: The new height of the picture.
    :type height: Optional[int]
    :param crop: The crop mode for the picture.
    :type crop: Optional[str]
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The resized picture.
    :rtype: PictureResponse
    """
    transformation = {
        "width": width,
        "height": height,
        "crop": crop.lower() if crop else None,
    }
    transformation = {k: v for k, v in transformation.items() if v is not None}

    picture = await PictureRepository.resize_picture(picture_id, transformation, current_user.id, db)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.post("/overlay/{picture_id}", response_model=PictureResponse)
async def overlay_image(
        picture_id: int,
        overlay_url: str = Query(..., description="URL of the image to overlay"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for overlaying an image.

    :param picture_id: The ID of the picture to overlay.
    :type picture_id: int
    :param overlay_url: The URL of the image to overlay.
    :type overlay_url: str
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The picture with the overlay applied.
    :rtype: PictureResponse
    """
    picture = await PictureRepository.overlay_image(picture_id, overlay_url, current_user.id, db)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.get("/{picture_id}/tags", response_model=List[str])
async def get_tags(
        picture_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for retrieving the tags of a specific picture.

    :param picture_id: The ID of the picture to get tags for.
    :type picture_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of tags associated with the picture.
    :rtype: List[str]
    """
    tags = await PictureRepository.get_tags(picture_id, current_user.id, db)

    if tags is None:
        raise HTTPException(status_code=404, detail="Picture not found")

    return tags
