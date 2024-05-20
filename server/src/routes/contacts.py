from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.contact import ContactBase, ContactResponse, ContactCreate, ContactUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts.

    :param limit: Maximum number of contacts to retrieve (between 10 and 500).
    :param offset: Number of contacts to skip.
    :param db: AsyncSession instance for database interaction.
    :param user: Current authenticated user.
    :return: List of ContactResponse objects.
    """
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)  # Змінено на get_contacts()
    return contacts


@router.get("/all", response_model=list[ContactResponse])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve all contacts without user filtering.

    :param limit: Maximum number of contacts to retrieve (between 10 and 500).
    :param offset: Number of contacts to skip.
    :param db: AsyncSession instance for database interaction.
    :return: List of ContactResponse objects.
    """
    contacts = await repository_contacts.get_all_contacts(limit, offset, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a specific contact by ID.

    :param contact_id: ID of the contact to retrieve (must be greater than or equal to 1).
    :param db: AsyncSession instance for database interaction.
    :param user: Current authenticated user.
    :return: ContactResponse object.
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact.

    :param body: Data representing the new contact.
    :param db: AsyncSession instance for database interaction.
    :param user: Current authenticated user.
    :return: Newly created ContactResponse object.
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Update an existing contact by ID.

    :param contact_id: ID of the contact to update (must be greater than or equal to 1).
    :param body: Data representing the updated contact information.
    :param db: AsyncSession instance for database interaction.
    :param user: Current authenticated user.
    :return: Updated ContactResponse object.
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Delete a contact by ID.

    :param contact_id: ID of the contact to delete (must be greater than or equal to 1).
    :param db: AsyncSession instance for database interaction.
    :param user: Current authenticated user.
    :return: Deleted ContactResponse object.
    """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact
