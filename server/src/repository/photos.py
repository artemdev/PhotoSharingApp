from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
        """
        url = cloudinary.uploader.upload(file)['secure_url']
        picture = Picture(
            image_url=url,
            description=description,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # if tags:
        #     for tag_name in tags:
        #         result = await db.execute(select(Tag).filter(Tag.name == tag_name))
        #         tag = result.scalar_one_or_none()
        #         if not tag:
        #             tag = Tag(name=tag_name)
        #             db.add(tag)
        #             await db.commit()  # Commit to get the tag ID
        #             await db.refresh(tag)
        #         picture.tags.append(tag)

        db.add(picture)
        await db.commit()
        await db.refresh(picture)
        return picture

    @staticmethod
    async def get_picture(picture_id: int, db: AsyncSession):
        """
        Retrieve a single picture by its ID.
        """
        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalar_one_or_none()
        return picture

    @staticmethod
    async def update_picture(picture_id: int, update_description: Optional[str], update_tags: Optional[List[str]],
                             db: AsyncSession):
        """
        Update an existing picture by its ID.
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
        picture.updated_at = datetime.now()

        await db.commit()
        await db.refresh(picture)
        return picture

    @staticmethod
    async def search_pictures(
            db: AsyncSession,
            search_term: Optional[str] = None,
            tag: Optional[str] = None,
            page: int = 1,
            page_size: int = 10
    ) -> List[Picture]:
        """
        Search for pictures based on search term and/or tag.
        """
        query = db.query(Picture)

        if search_term:
            query = query.filter(Picture.description.ilike(f'%{search_term}%'))

        if tag:
            query = query.join(Picture.tags).filter(Tag.name == tag)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await query.all()
        return result

    @staticmethod
    async def resize_picture(picture_id: int, transformation: dict, db: AsyncSession):
        """
        Resize a picture using Cloudinary.
        """
        # Retrieve the picture from the database
        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalar_one_or_none()
        if not picture:
            return None

        # Perform the transformation using Cloudinary
        transformed = cloudinary.uploader.explicit(
            picture.image_url, **transformation)
        transformed_url = transformed['secure_url']

        # Update the picture's image_url with the transformed URL
        picture.image_url = transformed_url
        picture.updated_at = datetime.now()

        db.add(picture)
        await db.commit()
        await db.refresh(picture)
        return picture

    @staticmethod
    async def crop_picture_face_detection(picture_id: int, db: AsyncSession):
        """
        Crop a picture using face-detection with Cloudinary.
        """
        result = await db.execute(select(Picture).filter(Picture.id == picture_id))
        picture = result.scalar_one_or_none()
        if not picture:
            return None

        # Perform the face-detection based cropping using Cloudinary
        transformed = cloudinary.uploader.explicit(
            picture.image_url, crop="thumb", gravity="face")
        transformed_url = transformed['secure_url']

        # Update the picture's image_url with the transformed URL
        picture.image_url = transformed_url
        picture.updated_at = datetime.now()

        db.add(picture)
        await db.commit()
        await db.refresh(picture)
        return picture
      
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
