import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .routers import users, projects, tasks, contacts, notices, messages, auth as auth_router, events
from . import models, auth
from datetime import datetime, date, timedelta

# Crea le tabelle del database SQLite all'avvio
Base.metadata.create_all(bind=engine)

# Funzione per popolare dati fittizi se il DB è vuoto
def seed_database():
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            default_pwd = auth.get_password_hash("password123")
            # 1. Crea Utenti
            marco = models.User(
                name="Marco Rossi",
                email="marco.rossi@example.com",
                hashed_password=default_pwd,
                avatar_url="https://api.dicebear.com/7.x/adventurer/svg?seed=Marco"
            )
            sofia = models.User(
                name="Sofia Bianchi",
                email="sofia.bianchi@example.com",
                hashed_password=default_pwd,
                avatar_url="https://api.dicebear.com/7.x/adventurer/svg?seed=Sofia"
            )
            luca = models.User(
                name="Luca Verdi",
                email="luca.verdi@example.com",
                hashed_password=default_pwd,
                avatar_url="https://api.dicebear.com/7.x/adventurer/svg?seed=Luca"
            )
            db.add_all([marco, sofia, luca])
            db.commit()
            
            # Refresh per ottenere gli ID
            db.refresh(marco)
            db.refresh(sofia)
            db.refresh(luca)
            
            # 2. Crea Progetti
            p1 = models.Project(
                name="Lancio Sito Web Marketing",
                description="Campagna di marketing e sviluppo frontend per il nuovo sito web corporate di PHG CRM.",
                owner_id=marco.id
            )
            p2 = models.Project(
                name="Refactoring Backend & Database",
                description="Miglioramento delle performance delle API e migrazione da SQLite a PostgreSQL.",
                owner_id=sofia.id
            )
            db.add_all([p1, p2])
            db.commit()
            db.refresh(p1)
            db.refresh(p2)
            
            # Aggiungi membri ai progetti
            db.add_all([
                models.ProjectMember(project_id=p1.id, user_id=marco.id, role="admin"),
                models.ProjectMember(project_id=p1.id, user_id=sofia.id, role="member"),
                models.ProjectMember(project_id=p1.id, user_id=luca.id, role="member"),
                models.ProjectMember(project_id=p2.id, user_id=sofia.id, role="admin"),
                models.ProjectMember(project_id=p2.id, user_id=marco.id, role="member")
            ])
            
            # 3. Crea Task per Progetto 1
            t1 = models.Task(
                project_id=p1.id,
                title="Pianificazione Copywriting Landing Page",
                description="Stesura della bozza per i testi della landing page promozionale.",
                status="completed",
                priority="high",
                due_date=date.today() - timedelta(days=1),
                assignee_id=luca.id
            )
            t2 = models.Task(
                project_id=p1.id,
                title="Sviluppo Componente Hero Section",
                description="Creazione del layout principale responsive con effetti di glassmorphism.",
                status="in_progress",
                priority="medium",
                due_date=date.today() + timedelta(days=1),
                assignee_id=marco.id
            )
            t3 = models.Task(
                project_id=p1.id,
                title="Integrazione Form Contatti con Hubspot",
                description="Configurazione degli endpoint API di Hubspot per raccogliere i lead.",
                status="todo",
                priority="low",
                due_date=date.today() + timedelta(days=4),
                assignee_id=sofia.id
            )
            
            # Crea Task per Progetto 2
            t4 = models.Task(
                project_id=p2.id,
                title="Analisi colli di bottiglia DB SQLite",
                description="Monitorare i tempi di risposta delle query complesse.",
                status="completed",
                priority="high",
                due_date=date.today() - timedelta(days=2),
                assignee_id=sofia.id
            )
            t5 = models.Task(
                project_id=p2.id,
                title="Scrittura test di integrazione CRUD",
                description="Predisporre la suite Pytest per testare la stabilità degli endpoint.",
                status="todo",
                priority="medium",
                due_date=date.today() + timedelta(days=7),
                assignee_id=marco.id
            )
            db.add_all([t1, t2, t3, t4, t5])
            db.commit()

            # 3.5 Crea Avvisi (Bacheca)
            n1 = models.Notice(
                title="Riunione di Allineamento Lunedì",
                content="Lunedì mattina alle 9:30 avremo la riunione settimanale di allineamento sul lancio del nuovo sito web. Si prega di aggiornare lo stato di tutti i task assegnati.",
                author_id=marco.id
            )
            n2 = models.Notice(
                title="Rilasciata versione beta PHG CRM",
                content="Abbiamo completato l'integrazione del modulo anagrafiche Clienti & Fornitori e della gestione allegati sui task. Potete iniziare a provarlo!",
                author_id=sofia.id
            )
            db.add_all([n1, n2])
            db.commit()

            # 3.6 Crea Messaggi (Chat one-to-one)
            m1 = models.Message(
                sender_id=marco.id,
                receiver_id=sofia.id,
                content="Ciao Sofia, hai visto la bozza per il refactoring del database?",
                is_read=1
            )
            m2 = models.Message(
                sender_id=sofia.id,
                receiver_id=marco.id,
                content="Sì Marco! Sto finendo di preparare la suite di test e poi procediamo con il merge.",
                is_read=1
            )
            m3 = models.Message(
                sender_id=luca.id,
                receiver_id=marco.id,
                content="Marco, ho caricato i testi della landing page sul task relativo, fammi sapere cosa ne pensi.",
                is_read=0
            )
            db.add_all([m1, m2, m3])
            db.commit()

        if db.query(models.Contact).count() == 0:
            # 4. Crea Contatti (Clienti / Fornitori)
            c1 = models.Contact(
                name="ACME Corporation S.r.l.",
                type="client",
                email="amministrazione@acme.it",
                phone="+39 02 1234567",
                address="Via Milano 12, Milano (MI)",
                vat_number="IT01234567890"
            )
            c2 = models.Contact(
                name="Global Tech Solutions Inc.",
                type="client",
                email="info@globaltech.com",
                phone="+39 06 9876543",
                address="Piazza Barberini 45, Roma (RM)",
                vat_number="IT09876543210"
            )
            c3 = models.Contact(
                name="Forniture Ufficio e Carta S.p.A.",
                type="supplier",
                email="ordini@ufficiocarta.it",
                phone="+39 011 5556789",
                address="Corso Vittorio Emanuele 101, Torino (TO)",
                vat_number="IT05556667778"
            )
            db.add_all([c1, c2, c3])
            db.commit()
    finally:
        db.close()

seed_database()

# Crea cartella uploads se non esiste
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI(
    title="PHG CRM API",
    description="Backend API per la web app PHG CRM",
    version="0.1.0"
)

# Configura CORS
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(contacts.router)
app.include_router(notices.router)
app.include_router(messages.router)
app.include_router(events.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Benvenuto nelle API di PHG CRM! Lo schema del database è pronto, popolato con dati di esempio ed inizializzato."
    }
