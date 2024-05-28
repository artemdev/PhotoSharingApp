from sqlalchemy.ext.asyncio import AsyncSession
from server.src.database.models import User, Picture, Tag
from datetime import datetime
import bcrypt


async def create_test_user(db: AsyncSession):
    hashed_password = bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt())
    user = User(email="test@example.com", hashed_password=hashed_password.decode("utf-8"))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_test_picture(db: AsyncSession, user_id: int):
    picture = Picture(
        image_url="https://example.com/test_image.jpg",
        description="Test picture",
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    tag = Tag(name="test")
    picture.tags.append(tag)
    db.add(picture)
    await db.commit()
    await db.refresh(picture)
    return picture
