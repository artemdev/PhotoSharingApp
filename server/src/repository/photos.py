from sqlalchemy import extract, and_
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from server.src.database.db import get_db
from server.src.database.models import Picture, User, Tag, Comment
from server.src.services.cloudinary import upload_picture
from server.src.schemas import PictureUpload, PictureUpdate
from typing import List


# from src.schemas import PictureCreate, PictureUpdate

# async def upload_picture(picture: PictureUpload, user: User, db: Session = Depends(get_db)):
async def post_picture(description: str, tags: List[str], file, db: Session):
    """
    Creates a new contact for a specific user.

    :param picture: The data for the contact to create.
    :type picture: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param Session: The database session.
    :type Session: Session
    :return: The newly uploaded picture.
    :rtype: Picture

    """

    url = upload_picture(file)
    picture = Picture(image_url=url, description=description)
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        picture.tags.append(tag)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def get_picture(picture_id: int, db: Session):

    """
    Retrieves a single picture with the specified ID for a specific user.

    :param picture_id: The ID of the picture to retrieve.
    :type picture_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The picture with the specified ID, or None if it does not exist.
    :rtype: Picture | None

    """
    return db.query(Picture).filter(Picture.id == picture_id).first()
