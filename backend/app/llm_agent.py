# backend/app/llm_agent.py
import os
import json
import re
from typing import Tuple
from dotenv import load_dotenv

# force it to load the .env in the same folder as this file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

print("🔑 OPENAI_KEY loaded:", OPENAI_KEY[:8] + "..." if OPENAI_KEY else None)


if OPENAI_KEY:
    import openai
    openai.api_key = OPENAI_KEY

SYSTEM_PROMPT = """
You are a SQL generation assistant for an sqlite database. Given a schema and a user question,
produce a single read-only SQL SELECT query that answers the question. Use the table and
column names exactly as provided. If question is ambiguous, ask for clarification instead
of guessing. Output a JSON with keys: sql and explanation only.
"""

def parse_model_output(content: str):
    # try JSON first
    try:
        return json.loads(content)
    except Exception:
        # try to extract SQL block
        m = re.search(r"```sql\\n([\\s\\S]+?)```", content, flags=re.I)
        if m:
            return {"sql": m.group(1).strip(), "explanation": content}
        # fallback to first SELECT...
        m2 = re.search(r"(select[\\s\\S]+?)(?:;|$)", content, flags=re.I)
        if m2:
            return {"sql": m2.group(1).strip(), "explanation": content}
    return {"sql": None, "explanation": content}

def question_to_sql(question: str, schema_inspect: dict) -> Tuple[str, str]:
    # fallback when no key available
    if not OPENAI_KEY:
        q = question.lower()
        if "sales" in q or "top" in q or "selling" in q:
            return (
                "SELECT prod, SUM(qty) as total_qty, SUM(qty*price) as revenue FROM sales_data GROUP BY prod ORDER BY total_qty DESC LIMIT 10",
                "fallback rule-based: aggregated sales by product",
            )
        return ("SELECT date('now') as now", "fallback timestamp")

    # build schema text
    schema_lines = []
    for t, cols in schema_inspect.items():
        schema_lines.append(f"Table {t}: columns = {cols}")
    schema_text = "\n".join(schema_lines) if schema_lines else "No schema available."

    prompt = f"{SYSTEM_PROMPT}\nSchema:\n{schema_text}\n\nQuestion: {question}\n\nRespond with JSON like: {{\"sql\":\"...\",\"explanation\":\"...\"}}"

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",   # use a safe widely-available model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
            temperature=0,
        )
        # log the raw response for debugging
        content = resp["choices"][0]["message"]["content"].strip()
        print("🟣 OpenAI raw response start\n", content, "\n🟣 OpenAI raw response end")
        parsed = parse_model_output(content)
        sql = parsed.get("sql")
        explanation = parsed.get("explanation", "")
        if not sql:
            print("⚠️ OpenAI did not return SQL. Parsed object:", parsed)
            return ("SELECT date('now') as now", "model responded but no SQL parsed; " + explanation)
        return (sql, explanation)
    except Exception as e:
        # print the exception to logs so we know why it failed
        print("❌ OpenAI call failed with exception:", type(e), e)
        # fallback to stub but include error in explanation
        q = question.lower()
        if "sales" in q or "top" in q or "selling" in q:
            return (
                "SELECT prod, SUM(qty) as total_qty, SUM(qty*price) as revenue FROM sales_data GROUP BY prod ORDER BY total_qty DESC LIMIT 10",
                "fallback rule-based due to error: " + str(e),
            )
        return ("SELECT date('now') as now", "fallback timestamp due to error: " + str(e))

