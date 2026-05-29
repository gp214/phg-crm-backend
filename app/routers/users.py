from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email già registrata")
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return db_user

@router.post("/{user_id}/reset-password")
def admin_reset_password(
    user_id: int, 
    reset_data: schemas.AdminPasswordReset, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
        
    new_hashed = auth.get_password_hash(reset_data.new_password)
    crud.update_user_password(db, user_id, new_hashed)
    return {"message": "Password resettata con successo"}

@router.post("/me/password")
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # Recupera l'utente dal db per avere la password hashata corrente
    db_user = crud.get_user(db, user_id=current_user.id)
    if not auth.verify_password(password_data.current_password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password corrente non valida")
    
    # Hash nuova password
    new_hashed = auth.get_password_hash(password_data.new_password)
    crud.update_user_password(db, current_user.id, new_hashed)
    return {"message": "Password aggiornata con successo"}
