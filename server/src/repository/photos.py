from sqlalchemy import extract, and_
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from server.src.database.db import get_db
from server.src.database.models import Picture, User, Tag, Comment
from server.src.services.cloudinary import upload_picture
from server.src.schemas import PictureUpload, PictureUpdate
from typing import List
from server.src.database.models import Picture, Tag
from server.src.schemas import PictureUpdate


# from src.schemas import PictureCreate, PictureUpdate

# async def upload_picture(picture: PictureUpload, user: User, db: Session = Depends(get_db)):
async def post_picture(description: str, tags: List[str], file, user_id, db: Session):
    """
    Post a new picture by a specific user.

    :param picture: The data for the picture to create.
    :type picture: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param Session: The database session.
    :type Session: Session
    :return: The newly uploaded picture.
    :rtype: Picture

    """

    url = upload_picture(file)
    picture = Picture(image_url=url, description=description, user_id=user_id)
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


async def update_picture(picture_id: int, picture_update: PictureUpdate, db: Session):
    # Retrieve the picture from the database
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        return None

    # Update the description if provided
    if picture_update.description is not None:
        picture.description = picture_update.description

    # Update the tags if provided
    if picture_update.tags is not None:
        # Clear existing tags
        picture.tags = []

        # Add new tags
        for tag_name in picture_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()  # Commit to get the tag ID
                db.refresh(tag)
            picture.tags.append(tag)

    db.commit()
    db.refresh(picture)
    return picture
