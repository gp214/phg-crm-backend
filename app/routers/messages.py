from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    tags=["Messages"]
)

@router.get("/api/messages/{user_a_id}/{user_b_id}", response_model=List[schemas.Message])
def read_messages(user_a_id: int, user_b_id: int, db: Session = Depends(get_db)):
    # Verifica che entrambi gli utenti esistano
    u_a = crud.get_user(db, user_id=user_a_id)
    u_b = crud.get_user(db, user_id=user_b_id)
    if not u_a or not u_b:
        raise HTTPException(status_code=404, detail="Uno o entrambi gli utenti non sono stati trovati")
    
    # Segna come letti i messaggi che vanno da user_b a user_a
    crud.mark_messages_as_read(db, sender_id=user_b_id, receiver_id=user_a_id)
    
    return crud.get_messages_between_users(db, user_a_id=user_a_id, user_b_id=user_b_id)

@router.post("/api/messages", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    u_a = crud.get_user(db, user_id=message.sender_id)
    u_b = crud.get_user(db, user_id=message.receiver_id)
    if not u_a or not u_b:
        raise HTTPException(status_code=404, detail="Mittente o destinatario non valido")
    return crud.create_message(db=db, message=message)

@router.post("/api/messages/read")
def mark_read(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    crud.mark_messages_as_read(db, sender_id=sender_id, receiver_id=receiver_id)
    return {"message": "Messaggi segnati come letti"}
