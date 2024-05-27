from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from src.database.models import Comment
from src.schemas.comments import CommentUpdate, CommentCreate
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status
from sqlalchemy.sql import func


class CommentRepository:

    @staticmethod
    async def create_comment(db: AsyncSession, comment: CommentCreate, user_id: int, picture_id: int) -> Comment:
        db_comment = Comment(
            text=comment.text, user_id=user_id, picture_id=picture_id)
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    @staticmethod
    async def update_comment(db: AsyncSession, comment_id: int, comment: CommentUpdate, user_id: int) -> Comment:
        result = await db.execute(select(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id))
        db_comment = result.scalars().first()

        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        db_comment.text = comment.text
        db_comment.updated_at = func.now()
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    @staticmethod
    async def delete_comment(db: AsyncSession, comment_id: int, user_role: str) -> None:
        result = await db.execute(select(Comment).filter(Comment.id == comment_id))
        db_comment = result.scalars().first()

        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        if user_role not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this comment")

        await db.delete(db_comment)
        await db.commit()

    @staticmethod
    async def get_comments(db: AsyncSession, photo_id: int, skip: int = 0, limit: int = 10):
        result = await db.execute(select(Comment).filter(Comment.picture_id == photo_id).offset(skip).limit(limit))
        return result.scalars().all()
