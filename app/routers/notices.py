from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    tags=["Notices"]
)

@router.get("/api/notices", response_model=List[schemas.Notice])
def read_notices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notices(db, skip=skip, limit=limit)

@router.post("/api/notices", response_model=schemas.Notice)
def create_notice(notice: schemas.NoticeCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=notice.author_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Autore non trovato")
    return crud.create_notice(db=db, notice=notice)

@router.delete("/api/notices/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    success = crud.delete_notice(db, notice_id=notice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Avviso non trovato")
    return {"message": "Avviso eliminato con successo"}
