from sqlalchemy import extract, and_
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models import Picture, User, Tag, Comment
from src.services.cloudinary import upload_picture
from src.schemas.photos import PictureUpload, PictureUpdate
from typing import List, Optional
from src.database.models import Picture, Tag


async def post_picture(description: Optional[str], tags: Optional[List[str]], file, user_id, db: Session):
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
    # picture = Picture(image_url=url, description=description)
    if tags:
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


async def get_picture(picture_id: int, db: AsyncSession):
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

    async def get_picture(picture_id: int, db: AsyncSession):
        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalars().first()
        return picture


async def update_picture(picture_id: int, update_description, update_tags, db: Session):
    # Retrieve the picture from the database
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        return None

    # Update the description if provided
    if update_description is not None:
        picture.description = update_description

    # Update the tags if provided
    if update_tags is not None:
        # Clear existing tags
        picture.tags = []

        # Add new tags
        for tag_name in update_tags:
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
