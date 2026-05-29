# Apex PM - Backend API

Servizio backend sviluppato con FastAPI e SQLite (SQLAlchemy) per la gestione del database relazionale del clone di Asana (Apex PM).

## Requisiti

- Python 3.8+

## Configurazione Locale

1. Crea e attiva un virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Avvia il server di sviluppo:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

Il server sarà attivo su [http://localhost:8000](http://localhost:8000). Puoi consultare la documentazione interattiva OpenAPI (Swagger UI) su [http://localhost:8000/docs](http://localhost:8000/docs).
