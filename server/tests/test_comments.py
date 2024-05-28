import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from src.database.db import get_db
from src.database.models import Base, User, Photo, Comment
from src.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_user(test_db):
    user = User(username="testuser", email="testuser@example.com",
                password=auth_service.hash_password("password"))
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="module")
def test_photo(test_db, test_user):
    photo = Photo(url="http://example.com/photo.jpg", user_id=test_user.id)
    test_db.add(photo)
    test_db.commit()
    test_db.refresh(photo)
    return photo


def test_create_comment(test_db, test_user, test_photo):
    token = auth_service.create_access_token(test_user.id)
    response = client.post(f"/photos/{test_photo.id}/comments", json={
                           "text": "Nice photo!"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["text"] == "Nice photo!"


def test_update_comment(test_db, test_user, test_photo):
    comment = Comment(text="Initial comment",
                      user_id=test_user.id, photo_id=test_photo.id)
    test_db.add(comment)
    test_db.commit()
    test_db.refresh(comment)

    token = auth_service.create_access_token(test_user.id)
    response = client.put(f"/comments/{comment.id}", json={
                          "text": "Updated comment"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["text"] == "Updated comment"


def test_delete_comment(test_db, test_user, test_photo):
    comment = Comment(text="Comment to be deleted",
                      user_id=test_user.id, photo_id=test_photo.id)
    test_db.add(comment)
    test_db.commit()
    test_db.refresh(comment)

    token = auth_service.create_access_token(test_user.id)
    response = client.delete(
        f"/comments/{comment.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_get_comments(test_db, test_user, test_photo):
    comment1 = Comment(text="Comment 1", user_id=test_user.id,
                       photo_id=test_photo.id)
    comment2 = Comment(text="Comment 2", user_id=test_user.id,
                       photo_id=test_photo.id)
    test_db.add(comment1)
    test_db.add(comment2)
    test_db.commit()
    test_db.refresh(comment1)
    test_db.refresh(comment2)

    response = client.get(f"/photos/{test_photo.id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    assert comments[0]["text"] == "Comment 1"
    assert comments[1]["text"] == "Comment 2"
