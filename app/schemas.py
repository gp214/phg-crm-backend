from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List

# --- SCHEMI UTENTE ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SCHEMI TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

# --- SCHEMI MEMBRO PROGETTO ---
class ProjectMemberBase(BaseModel):
    user_id: int
    role: str = "member"

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMember(ProjectMemberBase):
    id: int
    project_id: int
    created_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True

# --- SCHEMI ALLEGATO ---
class AttachmentBase(BaseModel):
    filename: str
    filepath: str

class AttachmentCreate(AttachmentBase):
    task_id: int

class Attachment(AttachmentBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SCHEMI TASK ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None

class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    assignee: Optional[User] = None
    attachments: List[Attachment] = []

    class Config:
        from_attributes = True

# --- SCHEMI PROGETTO ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: User
    tasks: List[Task] = []
    members: List[ProjectMember] = []

    class Config:
        from_attributes = True

# --- SCHEMI CONTATTO (CLIENTI / FORNITORI) ---
class ContactBase(BaseModel):
    name: str
    type: str  # 'client' o 'supplier'
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    vat_number: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SCHEMI AVVISI (BACHECA) ---
class NoticeBase(BaseModel):
    title: str
    content: str
    author_id: int

class NoticeCreate(NoticeBase):
    pass

class Notice(NoticeBase):
    id: int
    created_at: datetime
    author: Optional[User] = None

    class Config:
        from_attributes = True

# --- SCHEMI MESSAGGI (CHAT) ---
class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    created_at: datetime
    is_read: int
    sender: Optional[User] = None
    receiver: Optional[User] = None

    class Config:
        from_attributes = True

class EventParticipantBase(BaseModel):
    user_id: int

class EventParticipantCreate(EventParticipantBase):
    pass

class EventParticipant(EventParticipantBase):
    id: int
    event_id: int
    user: Optional[User] = None

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class EventCreate(EventBase):
    participant_ids: List[int] = []

class Event(EventBase):
    id: int
    creator_id: int
    created_at: datetime
    creator: Optional[User] = None
    participants: List[EventParticipant] = []

    class Config:
        from_attributes = True
