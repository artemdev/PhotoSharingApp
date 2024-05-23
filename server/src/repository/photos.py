from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.services.cloudinary import upload_picture
from typing import List, Optional
from src.database.models import Picture, Tag


async def post_picture(description: Optional[str], tags: Optional[List[str]], file, user_id, db: Session):
    """
    Post a new picture by a specific user.

    :param description: The description of the picture.
    :param tags: A list of tags for the picture.
    :param file: The file object representing the picture.
    :param user_id: The ID of the user uploading the picture.
    :param db: The database session.
    :return: The newly uploaded picture.
    """

    url = upload_picture(file)
    picture = Picture(
        image_url=url,
        description=description,
        user_id=user_id,
        created_at=datetime.datetime(),
        updated_at=datetime.datetime()
    )

    if tags:
        for tag_name in tags:
            tag = await db.execute(select(Tag).filter(Tag.name == tag_name))
            tag = tag.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            picture.tags.append(tag)

    db.add(picture)
    await db.commit()
    await db.refresh(picture)
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


async def update_picture(picture_id: int, update_description: Optional[str], update_tags: Optional[List[str]], db: Session):
    """
    Update an existing picture by its ID.

    :param picture_id: The ID of the picture to update.
    :param update_description: The new description for the picture.
    :param update_tags: The new tags for the picture.
    :param db: The database session.
    :return: The updated picture or None if not found.
    """
    # Retrieve the picture from the database
    result = await db.execute(select(Picture).filter(Picture.id == picture_id))
    picture = result.scalar_one_or_none()

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
            result = await db.execute(select(Tag).filter(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()  # Commit to get the tag ID
                await db.refresh(tag)
            picture.tags.append(tag)

    # Update the updated_at timestamp
    picture.updated_at = datetime.datetime()

    await db.commit()
    await db.refresh(picture)
    return picture


async def search_pictures(
        db: AsyncSession,
        search_term: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10
) -> List[Picture]:
    query = db.query(Picture)

    if search_term:
        query = query.filter(Picture.description.ilike(f'%{search_term}%'))

    if tags:
        query = query.join(Picture.tags).filter(Tag.name.in_(tags))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await query.all()
    return result

