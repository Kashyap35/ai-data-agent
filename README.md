# AI Data Agent — Conversational SQL Assistant

**Author:** Your Name (Kashyap)  
**Project:** Conversational interface that answers business questions from a SQL DB with charts & tables.

## What it does
- Accepts natural language questions (POST `/ask`) and returns:
  - Natural language explanation
  - Executed SQL
  - Table of results
  - Auto-chosen visualization (bar / line / pie)
- Handles messy schemas, unnamed columns and has a SQL safety layer (blocks destructive statements).
- Uses a fallback rule-based translator when an LLM is unavailable; can be wired to OpenAI for NL→SQL.

## Stack
- Frontend: React + Vite + Recharts
- Backend: FastAPI + SQLite
- LLM: Optional OpenAI integration (configurable via `.env`)

## Run locally (Windows PowerShell)
1. Backend:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
python app/seed_db.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
