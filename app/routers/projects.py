from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

@router.get("/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate, 
    owner_id: int = Query(..., description="ID dell'utente proprietario/creatore"), 
    db: Session = Depends(get_db)
):
    # Verifica che l'owner esista
    owner = crud.get_user(db, user_id=owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Utente proprietario non trovato")
    return crud.create_project(db=db, project=project, owner_id=owner_id)

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return db_project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return {"message": "Progetto eliminato con successo"}

@router.post("/{project_id}/members", response_model=schemas.ProjectMember)
def add_member_to_project(
    project_id: int, 
    member: schemas.ProjectMemberCreate, 
    db: Session = Depends(get_db)
):
    # Verifica che il progetto esista
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    
    # Verifica che l'utente da aggiungere esista
    db_user = crud.get_user(db, user_id=member.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
        
    return crud.add_project_member(db=db, project_id=project_id, member=member)
