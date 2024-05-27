from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime
import cloudinary.uploader
from src.database.models import Picture, Tag
import qrcode
import io
from PIL import Image



class PictureRepository:

    @staticmethod
    async def post_picture(description: Optional[str], tags: Optional[List[str]], file, user_id, db: AsyncSession):
        """
        Post a new picture by a specific user.

        :param description: The description of the picture.
        :type description: Optional[str]
        :param tags: A list of tags associated with the picture.
        :type tags: Optional[List[str]]
        :param file: The file to be uploaded to Cloudinary.
        :type file: file-like object
        :param user_id: The ID of the user posting the picture.
        :type user_id: int
        :param db: The database session.
        :type db: AsyncSession
        :return: The created Picture object.
        :rtype: Picture
        """
        try:
            # Upload the picture to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            url = upload_result['secure_url']

            # Create a new Picture object
            picture = Picture(
                image_url=url,
                description=description,
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Handle tags
            if tags:
                for tag_name in tags:
                    # Check if the tag already exists
                    result = await db.execute(select(Tag).filter(Tag.name == tag_name))
                    tag = result.scalar_one_or_none()
                    if not tag:
                        # Create a new tag if it does not exist
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        await db.commit()  # Commit to get the tag ID
                        await db.refresh(tag)
                    picture.tags.append(tag)

            # Add the picture to the database
            db.add(picture)
            await db.commit()
            await db.refresh(picture)

            return picture

        except Exception as e:
            logging.error(f"Error posting picture: {e}")
            raise

    @staticmethod
    async def get_picture(picture_id: int, db: AsyncSession):

        """
        Retrieve a single picture by its ID.

        :param picture_id: The ID of the picture to retrieve.
        :type picture_id: int
        :param db: The database session.
        :type db: AsyncSession
        :return: The picture with the specified ID, or None if it does not exist.
        :rtype: Optional[Picture]
        """

        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalar_one_or_none()
        return picture

    @staticmethod

    async def update_picture(
            picture_id: int,
            update_description: Optional[str],
            update_tags: Optional[List[str]],
            user_id: int,
            db: AsyncSession
    ):


        """
        Update an existing picture by its ID and user ID.

        :param picture_id: The ID of the picture to update.
        :type picture_id: int
        :param update_description: The new description of the picture.
        :type update_description: Optional[str]
        :param update_tags: A list of new tags for the picture.
        :type update_tags: Optional[List[str]]
        :param user_id: The ID of the user updating the picture.
        :type user_id: int
        :param db: The database session.
        :type db: AsyncSession
        :return: The updated picture, or None if it does not exist.
        :rtype: Optional[Picture]
        """

        # Retrieve the picture with tags from the database
        try:

            picture_result = await db.execute(
                select(Picture)
                .options(selectinload(Picture.tags))
                .filter(Picture.id == picture_id, Picture.user_id == user_id)
            )
            picture = picture_result.scalars().one_or_none()

            if not picture:
                return None

                # Update the description if provided
            if update_description is not None:
                picture.description = update_description

                # Update the tags if provided
            if update_tags is not None:
                # Clear existing tags
                picture.tags.clear()

                # Add new tags
                for tag_name in update_tags:
                    tag_result = await db.execute(select(Tag).filter(Tag.name == tag_name))
                    tag = tag_result.scalars().one_or_none()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        # await db.commit()  # Commit to get the tag ID
                        # await db.refresh(tag)
                        await db.flush()
                    picture.tags.append(tag)

                # Update the updated_at timestamp
            picture.updated_at = datetime.now()

            await db.commit()
            # await db.flush()
            await db.refresh(picture)
            # return picture

        except SQLAlchemyError as e:
            await db.rollback()
            raise e
        return picture

    @staticmethod
    async def search_pictures(
            db: AsyncSession,
            search_term: Optional[str] = None,
            tag: Optional[str] = None,
            user_id: Optional[int] = None,
            page: int = 1,
            page_size: int = 10
    ) -> List[Picture]:
        """
        Search for pictures based on search term, tag, and user_id, and sort by created_at.

        :param db: The database session.
        :type db: AsyncSession
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
        :return: A list of pictures matching the search criteria.
        :rtype: List[Picture]
        """
        query = select(Picture).options(joinedload(Picture.tags))

        if search_term:
            query = query.filter(Picture.description.ilike(f'%{search_term}%'))

        if tag:
            query = query.join(Picture.tags).filter(Tag.name == tag)

        if user_id:
            query = query.filter(Picture.user_id == user_id)

        query = query.order_by(desc(Picture.created_at))

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        pictures = list(result.scalars().unique().all())
        return pictures

    @staticmethod
    async def resize_picture(picture_id: int, transformation: dict, user_id: int, db: AsyncSession):

        """
         Resize a picture using Cloudinary.

         :param picture_id: The ID of the picture to resize.
         :type picture_id: int
         :param transformation: The transformation dictionary for resizing.
         :type transformation: dict
         :param user_id: The ID of the user resizing the picture.
         :type user_id: int
         :param db: The database session.
         :type db: AsyncSession
         :return: The resized picture, or None if it does not exist.
         :rtype: Optional[Picture]
         """

        # Retrieve the picture from the database
        result = await db.execute(select(Picture).filter(Picture.id == picture_id, Picture.user_id == user_id))
        picture = result.scalar_one_or_none()
        if not picture:
            return None

        # Extract public ID from the URL
        image_url = picture.image_url
        public_id = image_url.split('/')[-1].split('.')[0]

        # Perform the transformation using Cloudinary
        try:
            transformed = cloudinary.uploader.explicit(
                public_id, type="upload", **transformation)
            transformed_url = transformed['secure_url']
        except Exception as e:
            print(f"Error transforming image with Cloudinary: {e}")
            return None

        # Update the picture's image_url with the transformed URL
        picture.image_url = transformed_url
        picture.updated_at = datetime.now()

        db.add(picture)
        await db.commit()
        await db.refresh(picture)
        return picture

    @staticmethod
    async def overlay_image(picture_id: int, overlay_url: str, user_id: int, db: AsyncSession):
        """
        Overlay an image using Cloudinary.

        :param picture_id: The ID of the picture to overlay.
        :type picture_id: int
        :param overlay_url: The URL of the image to overlay.
        :type overlay_url: str
        :param user_id: The ID of the user overlaying the picture.
        :type user_id: int
        :param db: The database session.
        :type db: AsyncSession
        :return: The picture with the overlay, or None if it does not exist.
        :rtype: Optional[Picture]
        """

        # Retrieve the picture from the database
        result = await db.execute(select(Picture).filter(Picture.id == picture_id, Picture.user_id == user_id))
        picture = result.scalar_one_or_none()
        if not picture:
            return None

        # Extract public ID from the URL
        image_url = picture.image_url
        public_id = image_url.split('/')[-1].split('.')[0]

        # Extract overlay public ID from the URL
        overlay_public_id = overlay_url.split('/')[-1].split('.')[0]

        # Perform the overlay transformation using Cloudinary
        transformation = {
            "overlay": overlay_public_id
        }

        try:
            transformed = cloudinary.uploader.explicit(
                public_id, type="upload", **transformation)
            transformed_url = transformed['secure_url']
        except Exception as e:
            print(f"Error overlaying image with Cloudinary: {e}")
            return None

        # Update the picture's image_url with the transformed URL
        picture.image_url = transformed_url
        picture.updated_at = datetime.now()

        db.add(picture)
        await db.commit()
        await db.refresh(picture)
        return picture

    @staticmethod
    async def get_tags(picture_id: int, user_id: int, db: AsyncSession):
        """
        Retrieve the tags for a specific picture by its ID and user ID.

        :param picture_id: The ID of the picture.
        :type picture_id: int
        :param user_id: The ID of the user who owns the picture.
        :type user_id: int
        :param db: The database session.
        :type db: AsyncSession
        :return: A list of tags associated with the picture.
        :rtype: List[str]
        """
        result = await db.execute(
            select(Picture)
            .options(joinedload(Picture.tags))
            .filter(Picture.id == picture_id, Picture.user_id == user_id)
        )

        # Call unique() on the result to handle duplicates
        picture = result.scalars().unique().one_or_none()

        if not picture:
            return None

        return [tag.name for tag in picture.tags]

      
    @staticmethod
    async def delete_picture(picture_id: int, db: AsyncSession):
        """
        Deletes a single picture with the specified ID from the database.
        :param picture_id: The ID of the picture to delete.
        :type picture_id: int
        :param db: The database session.
        :type db: Session
        :return: The deleted picture, or None if it does not exist.
        :rtype: Picture | None
        """
        picture = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = picture.scalar_one_or_none()
        if not picture:
            return None

        await db.delete(picture)
        await db.commit()

        return picture


    @staticmethod
    async def create_qrcode(picture_id: int, db: AsyncSession):
        picture = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = picture.scalar_one_or_none()
        if not picture:
            return None

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
        )
        qr.add_data(picture.image_url)
        qr.make(fit=True)
        img = qr.make_image()

        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr.seek(0)

        qr_code_url = cloudinary.uploader.upload(byte_arr)['secure_url']

        picture.qr_code_url = qr_code_url
        db.add(picture)
        await db.commit()
        await db.refresh(picture)

        return picture

