from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(
    prefix="/api/events",
    tags=["Events"]
)

@router.get("/", response_model=List[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    events = crud.get_events(db, skip=skip, limit=limit)
    
    # Mascheriamo il titolo e la descrizione se l'utente non è creatore o partecipante
    masked_events = []
    for ev in events:
        is_creator = ev.creator_id == current_user.id
        is_participant = any(p.user_id == current_user.id for p in ev.participants)
        
        if is_creator or is_participant:
            masked_events.append(ev)
        else:
            # Creiamo una copia mascherata
            masked_ev = schemas.Event.from_orm(ev).copy()
            creator_name = ev.creator.name if ev.creator else "Sconosciuto"
            masked_ev.title = f"Occupato ({creator_name})"
            masked_ev.description = "Impegno privato"
            masked_events.append(masked_ev)
            
    return masked_events

@router.post("/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_event(db=db, event=event, creator_id=current_user.id)

@router.patch("/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event_update: schemas.EventUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    if db_event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorizzato a modificare questo evento")
    
    return crud.update_event(db=db, event_id=event_id, event_update=event_update)

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    if db_event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorizzato a eliminare questo evento")
    
    crud.delete_event(db=db, event_id=event_id)
    return {"message": "Evento eliminato"}
