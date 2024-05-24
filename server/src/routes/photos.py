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


@router.post("/", response_model=PictureUpload)
async def post_picture(
        file: UploadFile = File(...),
        description: Optional[str] = Form(None),
        tags: List[str] = Form(None),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Route handler for uploading pictures.
    """
    picture = await PictureRepository.post_picture(description, tags, file.file, current_user.id, db)
    return picture


@router.get("/{picture_id}", response_model=PictureResponse)
async def get_picture(picture_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for retrieving a specific picture.
    """
    picture = await PictureRepository.get_picture(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(
        picture_id: int,
        description: Optional[str] = Form(None),
        tags: List[str] = Form(None),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Route handler for updating a picture.
    """
    picture = await PictureRepository.update_picture(picture_id, description, tags, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.delete("/{picture_id}", response_model=PictureResponse)
async def delete_picture(picture_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for deleting a specific picture.

    This function handles DELETE requests to '/{picture_id}' for deleting a specific picture.

    :param picture_id: The ID of the picture to delete.
    :type picture_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :return: The deleted picture data.
    :rtype: PictureResponse form

    Raises:
    HTTPException: If the picture is not found.
    """
    picture = await PictureRepository.delete_picture(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture


@router.get("/search", response_model=List[PictureResponse])
async def search_pictures(
        search_term: Optional[str] = Query(None),
        tag: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for searching pictures.
    """
    pictures = await PictureRepository.search_pictures(db, search_term, tag, page, page_size)
    if not pictures:
        raise HTTPException(status_code=404, detail="No pictures found")
    return pictures


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
    """
    transformation = {}
    if width:
        transformation["width"] = width
    if height:
        transformation["height"] = height
    if crop:
        transformation["crop"] = crop

    picture = await PictureRepository.resize_picture(picture_id, transformation, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.post("/transform/{picture_id}/face-detect-crop", response_model=PictureResponse)
async def crop_picture_face_detection(
        picture_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for cropping a picture using face-detection with Cloudinary.
    """
    picture = await PictureRepository.crop_picture_face_detection(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture


@router.post("/{picture_id}/qrcode", response_model=PictureResponse)
async def create_qrcode(
        picture_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    picture = await PictureRepository.create_qrcode(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture


@router.get("/{picture_id}/qrcode")
async def get_qrcode(picture_id: int, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    picture = await PictureRepository.get_picture(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture.qr_code_url