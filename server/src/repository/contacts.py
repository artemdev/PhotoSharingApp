from datetime import date, timedelta
from typing import Sequence

from sqlalchemy import select, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.contact import ContactCreate, ContactUpdate, ContactBase


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Retrieve a list of contacts for a specific user from the database.

    :param limit: The maximum number of contacts to retrieve.
    :param offset: The number of contacts to skip.
    :param db: AsyncSession instance for database interaction.
    :param user: User object representing the owner of the contacts.
    :return: A list of Contact objects.
    """
    stmt = select(User).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    Retrieve all contacts from the database.

    :param limit: The maximum number of contacts to retrieve.
    :param offset: The number of contacts to skip.
    :param db: AsyncSession instance for database interaction.
    :return: A list of all Contact objects.
    """
    stmt = select(User).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession) -> User:
    """
    Retrieve a specific contact by its ID from the database.

    :param contact_id: The ID of the contact to retrieve.
    :param db: AsyncSession instance for database interaction.
    :return: The Contact object corresponding to the given ID, if found.
    """
    stmt = select(User).filter(User.id == contact_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(body: ContactBase, db: AsyncSession, user: User):
    """
    Create a new contact in the database.

    :param body: Data representing the new contact.
    :param db: AsyncSession instance for database interaction.
    :param user: User object representing the owner of the contact.
    :return: The newly created Contact object.
    """
    contact = User(**body.model_dump(exclude_unset=True), user=user)  # (title=body.title,
    # description=body.description)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactBase, db: AsyncSession, user: User):
    """
    Update an existing contact in the database.

    :param contact_id: The ID of the contact to update.
    :param body: Data representing the updated contact information.
    :param db: AsyncSession instance for database interaction.
    :param user: User object representing the owner of the contact.
    :return: The updated Contact object, if found and updated.
    """
    stmt = select(User).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.address = body.address
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Delete a contact from the database.

    :param contact_id: The ID of the contact to delete.
    :param db: AsyncSession instance for database interaction.
    :param user: User object representing the owner of the contact.
    :return: The deleted Contact object, if found and deleted.
    """
    stmt = select(User).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact

