from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from src.database.db import get_db
from src.schemas.comments import CommentCreate, CommentUpdate, CommentOut
from src.services.auth import auth_service
from src.repository.comments import CommentRepository
from src.database.models import User, Comment, Role
from src.services.user import RoleAccess

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post("/photos/{photo_id}/comments", response_model=CommentOut)
async def create_comment(photo_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await CommentRepository.create_comment(db, comment, current_user.id, photo_id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(comment_id: int, comment: CommentUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    db_comment = result.scalars().first()

    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if current_user.id != db_comment.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only edit your own comments")

    updated_comment = await CommentRepository.update_comment(db, comment_id, comment)
    return updated_comment


@router.delete("/comments/{comment_id}", dependencies=[Depends(RoleAccess([Role.admin, Role.moderator]))])
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    await CommentRepository.delete_comment(db, comment_id)
    return {"message": "Comment deleted"}


@router.get("/photos/{photo_id}/comments", response_model=List[CommentOut])
async def get_comments(photo_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    return await CommentRepository.get_comments(db, photo_id, skip=skip, limit=limit)
