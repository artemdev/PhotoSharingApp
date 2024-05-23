from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.user import UserOut, UserRoleUpdate
from src.repository import users as repository_users
from src.services.user import RoleAccess

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(RoleAccess([Role.admin]))]
)


@router.get("/users", response_model=List[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all users.

    :param db: AsyncSession instance for database interaction.
    :return: List of User objects.
    """
    try:
        users = await repository_users.get_all_users(db)
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/users/{user_id}/role", response_model=None)
async def update_role(user_id: int, role_update: UserRoleUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update the role of a user.

    :param user_id: The ID of the user to update.
    :param role_update: The new role to assign to the user.
    :param db: AsyncSession instance for database interaction.
    :return: Updated User object.
    """
    try:
        user = await repository_users.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        updated_user = await repository_users.update_user_role(user_id, role_update.role, db)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
