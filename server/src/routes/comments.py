from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from src.database.db import get_db
from src.schemas.comments import CommentCreate, CommentUpdate, CommentOut
from src.services.auth import auth_service
from src.repository.comments import CommentRepository
from src.database.models import User

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post("/photos/{photo_id}/comments", response_model=CommentOut)
async def create_comment(photo_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await CommentRepository.create_comment(db, comment, current_user.id, photo_id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(comment_id: int, comment: CommentUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    try:
        updated_comment = await CommentRepository.update_comment(db, comment_id, comment, current_user.id)
        return updated_comment
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to update comment: {e}")


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    await CommentRepository.delete_comment(db, comment_id, current_user.role)
    return {"message": "Comment deleted"}


@router.get("/photos/{photo_id}/comments", response_model=List[CommentOut])
async def get_comments(photo_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    db: Session = Depends(get_db)
    return await CommentRepository.get_comments(db, photo_id, skip=skip, limit=limit)
