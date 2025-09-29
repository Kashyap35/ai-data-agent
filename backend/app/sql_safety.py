# backend/app/sql_safety.py
import re

READ_ONLY_ALLOWED = ["select"]

FORBIDDEN_KEYWORDS = [
    "drop ", "delete ", "update ", "insert ", "alter ",
    "create ", "attach ", "pragma ", "vacuum",
    ";--", "--", "exec(", "execute("
]

def is_safe_sql(sql: str, allowed_tables: list):
    if not sql or not isinstance(sql, str):
        return False, "empty or invalid sql"

    s = sql.strip().lower()

    # forbid dangerous keywords
    for kw in FORBIDDEN_KEYWORDS:
        if kw in s:
            return False, f"forbidden keyword detected: {kw.strip()}"

    # require startswith SELECT
    if not any(s.startswith(k) for k in READ_ONLY_ALLOWED):
        return False, "only SELECT queries are allowed"

    # check referenced tables
    referenced = set()
    for m in re.finditer(r"(?:from|join)\s+([`\"]?)([a-zA-Z0-9_]+)\1", s):
        referenced.add(m.group(2))

    if allowed_tables:
        for r in referenced:
            if r not in allowed_tables:
                return False, f"table '{r}' not in allowed list"

    return True, "ok"

