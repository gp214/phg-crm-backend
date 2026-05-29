from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    prefix="/api/contacts",
    tags=["Contacts"]
)

@router.get("/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db=db, contact=contact)

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    success = crud.delete_contact(db, contact_id=contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contatto non trovato")
    return {"message": "Contatto eliminato con successo"}
