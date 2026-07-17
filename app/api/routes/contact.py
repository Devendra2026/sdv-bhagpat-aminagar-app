from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.crud import contact as contact_crud
from app.db.session import get_db
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter()


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    return contact_crud.create_contact(db, payload)


@router.get("", response_model=list[ContactResponse])
def list_contacts(db: Session = Depends(get_db)):
    return contact_crud.get_contacts(db)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = contact_crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)):
    contact = contact_crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact_crud.update_contact(db, contact, payload)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = contact_crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact_crud.delete_contact(db, contact)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
