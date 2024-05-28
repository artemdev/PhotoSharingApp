import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, User
from src.services.auth import auth_service
from src.database.db import get_db
from main import app  # Import the main FastAPI app
from utils import create_test_user, create_test_picture

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db dependency for tests
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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


async def test_search_pictures(client: AsyncClient):
    response = await client.get("/photos/search?search_term=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_search_pictures_by_user(db: AsyncSession, test_picture: Picture, test_user: User):
    pictures = await PictureRepository.search_pictures(db=db, user_id=test_user.id, page=1, page_size=10)
    assert len(pictures) > 0
    assert all(picture.user_id == test_user.id for picture in pictures)


async def test_search_pictures_sorted_by_created_at(db: AsyncSession, test_picture: Picture):
    pictures = await PictureRepository.search_pictures(db=db, page=1, page_size=10)
    assert len(pictures) > 0
    sorted_pictures = sorted(pictures, key=lambda pic: pic.created_at, reverse=True)
    assert pictures == sorted_pictures


async def test_post_picture(client: AsyncClient, test_user: User):
    user_token = auth_service.create_access_token(data={"sub": test_user.email})

    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    files = {"file": ("test_image.jpg", b"test image content", "image/jpeg")}
    data = {
        "description": "Test description",
        "tags": "test,tag"
    }
    response = await client.post("/photos/", headers=headers, files=files, data=data)
    assert response.status_code == 200
    assert "image_url" in response.json()


async def test_get_picture(client: AsyncClient, test_picture):
    response = await client.get(f"/photos/{test_picture.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_picture.id


async def test_update_picture(client: AsyncClient, test_picture, test_user: User):
    user_token = auth_service.create_access_token(data={"sub": test_user.email})

    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    data = {
        "description": "Updated description",
        "tags": "updated,tag"
    }
    response = await client.put(f"/photos/{test_picture.id}", headers=headers, data=data)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


async def test_resize_picture(client: AsyncClient, test_picture, test_user: User):
    user_token = auth_service.create_access_token(data={"sub": test_user.email})

    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    params = {
        "width": 200,
        "height": 200,
        "crop": "fit"
    }
    response = await client.post(f"/photos/transform/{test_picture.id}", headers=headers, params=params)
    assert response.status_code == 200
    assert "image_url" in response.json()


async def test_overlay_image(client: AsyncClient, test_picture, test_user: User):
    user_token = auth_service.create_access_token(data={"sub": test_user.email})

    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    params = {
        "overlay_url": "https://example.com/overlay_image.jpg"
    }
    response = await client.post(f"/photos/overlay/{test_picture.id}", headers=headers, params=params)
    assert response.status_code == 200
    assert "image_url" in response.json()


async def test_get_tags(client: AsyncClient, test_picture, test_user: User):
    user_token = auth_service.create_access_token(data={"sub": test_user.email})

    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    response = await client.get(f"/photos/{test_picture.id}/tags", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "test" in response.json()
    assert "tag" in response.json()
