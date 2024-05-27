import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, User, Picture, Tag
from src.repository.photos import PictureRepository
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="module")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = TestingSessionLocal()
    yield async_session
    await async_session.close()
    await engine.dispose()


@pytest.fixture(scope="module")
async def test_user(db: AsyncSession):
    return await create_test_user(db)


@pytest.fixture(scope="module")
async def test_picture(db: AsyncSession, test_user: User):
    return await create_test_picture(db, test_user.id)


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


async def test_post_picture(db: AsyncSession, test_user: User):
    file = b"test image content"
    description = "Test description"
    tags = ["test", "tag"]
    picture = await PictureRepository.post_picture(description, tags, file, test_user.id, db)
    assert picture is not None
    assert picture.description == description
    assert len(picture.tags) == 2


async def test_get_picture(db: AsyncSession, test_picture: Picture):
    picture = await PictureRepository.get_picture(test_picture.id, db)
    assert picture is not None
    assert picture.id == test_picture.id


async def test_update_picture(db: AsyncSession, test_picture: Picture, test_user: User):
    description = "Updated description"
    tags = ["updated", "tag"]
    updated_picture = await PictureRepository.update_picture(test_picture.id, description, tags, test_user.id, db)
    assert updated_picture is not None
    assert updated_picture.description == description
    assert len(updated_picture.tags) == 2


async def test_search_pictures(db: AsyncSession, test_picture: Picture):
    pictures = await PictureRepository.search_pictures(db=db, search_term="Test", page=1, page_size=10)
    assert len(pictures) > 0
    assert test_picture in pictures


async def test_resize_picture(db: AsyncSession, test_picture: Picture, test_user: User):
    transformation = {
        "width": 200,
        "height": 200,
        "crop": "fit"
    }
    resized_picture = await PictureRepository.resize_picture(test_picture.id, transformation, test_user.id, db)
    assert resized_picture is not None
    assert "image_url" in resized_picture.image_url


async def test_overlay_image(db: AsyncSession, test_picture: Picture, test_user: User):
    overlay_url = "https://example.com/overlay_image.jpg"
    overlaid_picture = await PictureRepository.overlay_image(test_picture.id, overlay_url, test_user.id, db)
    assert overlaid_picture is not None
    assert "image_url" in overlaid_picture.image_url


async def test_get_tags(db: AsyncSession, test_picture: Picture, test_user: User):
    tags = await PictureRepository.get_tags(test_picture.id, test_user.id, db)
    assert tags is not None
    assert len(tags) > 0
    assert "test" in tags
    assert "tag" in tags
