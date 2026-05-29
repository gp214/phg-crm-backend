import os
import shutil
import time
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    tags=["Tasks"]
)

# Endpoint per listare i task associati ad un progetto specifico
@router.get("/api/projects/{project_id}/tasks", response_model=List[schemas.Task])
def read_project_tasks(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Verifica che il progetto esista
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return crud.get_tasks(db, project_id=project_id, skip=skip, limit=limit)

# Endpoint per creare un task all'interno di un progetto
@router.post("/api/projects/{project_id}/tasks", response_model=schemas.Task)
def create_task_for_project(project_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Verifica che il progetto esista
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    
    # Se specificato, verifica che l'assegnatario esista
    if task.assignee_id is not None:
        db_user = crud.get_user(db, user_id=task.assignee_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Utente assegnatario non trovato")
            
    return crud.create_project_task(db=db, task=task, project_id=project_id)

# Endpoint per ottenere i dettagli di un singolo task
@router.get("/api/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task non trovato")
    return db_task

# Endpoint per aggiornare un task (ad es. cambio stato o assegnatario)
@router.patch("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task non trovato")
        
    # Se stiamo aggiornando l'assegnatario, verifica che esista
    if task_update.assignee_id is not None:
        db_user = crud.get_user(db, user_id=task_update.assignee_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Utente assegnatario non trovato")
            
    return crud.update_task(db=db, task_id=task_id, task_update=task_update)

# Endpoint per cancellare un task
@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task non trovato")
    return {"message": "Task eliminato con successo"}

# Endpoint per caricare un allegato per un task
@router.post("/api/tasks/{task_id}/attachments", response_model=schemas.Attachment)
def upload_task_attachment(task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task non trovato")

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    filename = f"{task_id}_{int(time.time())}_{file.filename}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment_in = schemas.AttachmentCreate(
        task_id=task_id,
        filename=file.filename,
        filepath=filename
    )
    return crud.create_attachment(db=db, attachment=attachment_in)

# Endpoint per cancellare un allegato
@router.delete("/api/attachments/{attachment_id}")
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = crud.get_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Allegato non trovato")

    filepath = os.path.join("uploads", attachment.filepath)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Errore rimozione file: {e}")

    success = crud.delete_attachment(db, attachment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Errore durante l'eliminazione dell'allegato")
    return {"message": "Allegato eliminato con successo"}
