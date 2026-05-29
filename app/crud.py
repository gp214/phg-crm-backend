from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime

# --- UTENTI ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        avatar_url=user.avatar_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, hashed_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.hashed_password = hashed_password
        db.commit()
        db.refresh(db_user)
    return db_user

# --- PROGETTI ---
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int):
    db_project = models.Project(
        name=project.name,
        description=project.description,
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Aggiungi automaticamente l'owner come membro amministratore del progetto
    db_member = models.ProjectMember(
        project_id=db_project.id,
        user_id=owner_id,
        role="admin"
    )
    db.add(db_member)
    db.commit()
    
    return db_project

def update_project(db: Session, project_id: int, project: schemas.ProjectCreate):
    db_project = get_project(db, project_id)
    if db_project:
        db_project.name = project.name
        db_project.description = project.description
        db_project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# --- TASK ---
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.project_id == project_id).offset(skip).limit(limit).all()

def create_project_task(db: Session, task: schemas.TaskCreate, project_id: int):
    db_task = models.Task(
        project_id=project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assignee_id=task.assignee_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if db_task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# --- MEMBRI DEL PROGETTO ---
def add_project_member(db: Session, project_id: int, member: schemas.ProjectMemberCreate):
    db_member = models.ProjectMember(
        project_id=project_id,
        user_id=member.user_id,
        role=member.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

# --- ALLEGATI ---
def create_attachment(db: Session, attachment: schemas.AttachmentCreate):
    db_attachment = models.Attachment(
        task_id=attachment.task_id,
        filename=attachment.filename,
        filepath=attachment.filepath
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def get_attachment(db: Session, attachment_id: int):
    return db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()

def delete_attachment(db: Session, attachment_id: int):
    db_attachment = get_attachment(db, attachment_id)
    if db_attachment:
        db.delete(db_attachment)
        db.commit()
        return True
    return False

# --- CONTATTI (CLIENTI & FORNITORI) ---
def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(
        name=contact.name,
        type=contact.type,
        email=contact.email,
        phone=contact.phone,
        address=contact.address,
        vat_number=contact.vat_number
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return True
    return False

# --- AVVISI (BACHECA) ---
def get_notices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Notice).order_by(models.Notice.created_at.desc()).offset(skip).limit(limit).all()

def get_notice(db: Session, notice_id: int):
    return db.query(models.Notice).filter(models.Notice.id == notice_id).first()

def create_notice(db: Session, notice: schemas.NoticeCreate):
    db_notice = models.Notice(
        title=notice.title,
        content=notice.content,
        author_id=notice.author_id
    )
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice

def delete_notice(db: Session, notice_id: int):
    db_notice = get_notice(db, notice_id)
    if db_notice:
        db.delete(db_notice)
        db.commit()
        return True
    return False

# --- MESSAGGI (CHAT) ---
def get_messages_between_users(db: Session, user_a_id: int, user_b_id: int, limit: int = 100):
    from sqlalchemy import or_, and_
    return db.query(models.Message).filter(
        or_(
            and_(models.Message.sender_id == user_a_id, models.Message.receiver_id == user_b_id),
            and_(models.Message.sender_id == user_b_id, models.Message.receiver_id == user_a_id)
        )
    ).order_by(models.Message.created_at.asc()).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def mark_messages_as_read(db: Session, sender_id: int, receiver_id: int):
    db.query(models.Message).filter(
        models.Message.sender_id == sender_id,
        models.Message.receiver_id == receiver_id,
        models.Message.is_read == 0
    ).update({models.Message.is_read: 1}, synchronize_session=False)
    db.commit()

# --- CALENDARIO ED EVENTI ---
def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).order_by(models.Event.start_time.asc()).offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.EventCreate, creator_id: int):
    db_event = models.Event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        creator_id=creator_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    for p_id in event.participant_ids:
        db_participant = models.EventParticipant(event_id=db_event.id, user_id=p_id)
        db.add(db_participant)
    
    if event.participant_ids:
        db.commit()
        db.refresh(db_event)
        
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event
