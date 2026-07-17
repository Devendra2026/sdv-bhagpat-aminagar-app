from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


def create_contact(db: Session, payload: ContactCreate) -> Contact:
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

# get all contact
def get_contacts(db: Session) -> list[Contact]:
    return list(db.scalars(select(Contact).order_by(Contact.id.desc())))

# get contact by id
def get_contact(db: Session, contact_id: int) -> Contact | None:
    return db.get(Contact, contact_id)


def update_contact(db: Session, contact: Contact, payload: ContactUpdate) -> Contact:
    for field, value in payload.model_dump().items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: Contact) -> None:
    db.delete(contact)
    db.commit()
