
# backend/app/main.py
import os
import sqlite3
import traceback
from typing import Any, Dict, List
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .sql_safety import is_safe_sql


# relative imports from this package
from . import llm_agent
from .sql_safety import is_safe_sql

# App & CORS setup
app = FastAPI(title="AI Data Agent")

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = os.path.join(os.path.dirname(__file__), "ai_agent.db")


class AskIn(BaseModel):
    question: str


@app.post("/ask")
async def ask(payload: AskIn) -> Any:
    """Handle an NL question: inspect schema, generate SQL via llm_agent,
    run a safety check, execute the query (read-only) and return results."""
    question = payload.question


    # Connect to DB
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # 1) Inspect tables and columns
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]

        schema: Dict[str, List[str]] = {}
        for t in tables:
            try:
                cur.execute(f"PRAGMA table_info('{t}')")
                cols = [r[1] for r in cur.fetchall()]
                # sanitize empty/unnamed columns
                sanitized = []
                for i, c in enumerate(cols):
                    if not c or str(c).strip() == "":
                        sanitized.append(f"col_unknown_{i}")
                    else:
                        sanitized.append(c)
                schema[t] = sanitized
            except Exception:
                schema[t] = []

        # 2) Generate SQL + explanation (llm_agent handles fallback if no key)
        sql, explanation = llm_agent.question_to_sql(question, schema)

        # 3) Safety check
        safe, reason = is_safe_sql(sql, list(schema.keys()))
        if not safe:
            return {"error": "SQL safety check failed", "reason": reason, "sql": sql}

        # 4) Execute the SQL (read-only). Limit rows returned.
        cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(1000)  # safe cap
        rows_list = [list(r) for r in rows]

        return {
            "answer": f"Explanation: {explanation}",
            "sql": sql,
            "columns": cols,
            "rows": rows_list,
        }

    except Exception as exc:
        tb = traceback.format_exc()
        return {"error": str(exc), "traceback": tb, "sql": locals().get("sql")}
    finally:
        conn.close()
