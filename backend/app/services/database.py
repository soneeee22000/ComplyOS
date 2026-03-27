"""SQLite database service — persistent storage for AI systems and assessments."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "complyos.db")


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ai_systems (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            department TEXT DEFAULT '',
            use_case TEXT DEFAULT '',
            risk_level TEXT,
            annex_category TEXT,
            classification_reasoning TEXT,
            confidence_score REAL,
            overall_compliance_score INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL REFERENCES ai_systems(id),
            overall_score INTEGER NOT NULL,
            gaps TEXT NOT NULL,
            summary TEXT NOT NULL,
            priority_actions TEXT NOT NULL,
            assessed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL REFERENCES ai_systems(id),
            doc_type TEXT NOT NULL,
            content TEXT NOT NULL,
            generated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            system_id TEXT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def create_system(name: str, description: str, department: str, use_case: str) -> dict:
    """Insert a new AI system and return it."""
    conn = get_connection()
    system_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO ai_systems (id, name, description, department, use_case, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (system_id, name, description, department, use_case, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM ai_systems WHERE id = ?", (system_id,)).fetchone()
    conn.close()
    return dict(row)


def list_systems() -> list[dict]:
    """Return all AI systems."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM ai_systems ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_system(system_id: str) -> dict | None:
    """Return a single system by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM ai_systems WHERE id = ?", (system_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


ALLOWED_SYSTEM_FIELDS = frozenset({
    "risk_level", "annex_category", "classification_reasoning",
    "confidence_score", "overall_compliance_score", "updated_at",
})


def update_system(system_id: str, **fields: str | float | int | None) -> dict | None:
    """Update specific fields on an AI system.

    Only fields in ALLOWED_SYSTEM_FIELDS can be updated to prevent SQL injection.
    """
    invalid = set(fields) - ALLOWED_SYSTEM_FIELDS
    if invalid:
        raise ValueError(f"Invalid field(s): {invalid}")

    conn = get_connection()
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [system_id]
    conn.execute(f"UPDATE ai_systems SET {set_clause} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM ai_systems WHERE id = ?", (system_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_assessment(system_id: str, overall_score: int, gaps: list, summary: str, priority_actions: list) -> dict:
    """Save a gap analysis assessment."""
    conn = get_connection()
    assessment_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO assessments (id, system_id, overall_score, gaps, summary, priority_actions, assessed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (assessment_id, system_id, overall_score, json.dumps(gaps), summary, json.dumps(priority_actions), now),
    )
    conn.commit()
    conn.close()
    return {
        "id": assessment_id,
        "system_id": system_id,
        "overall_score": overall_score,
        "gaps": gaps,
        "summary": summary,
        "priority_actions": priority_actions,
        "assessed_at": now,
    }


def get_assessment(system_id: str) -> dict | None:
    """Get the latest assessment for a system."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM assessments WHERE system_id = ? ORDER BY assessed_at DESC LIMIT 1",
        (system_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["gaps"] = json.loads(result["gaps"])
    result["priority_actions"] = json.loads(result["priority_actions"])
    return result


def save_document(system_id: str, doc_type: str, content: str) -> dict:
    """Save a generated document."""
    conn = get_connection()
    doc_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO documents (id, system_id, doc_type, content, generated_at) VALUES (?, ?, ?, ?, ?)",
        (doc_id, system_id, doc_type, content, now),
    )
    conn.commit()
    conn.close()
    return {"id": doc_id, "system_id": system_id, "doc_type": doc_type, "content": content, "generated_at": now}


def log_audit(system_id: str | None, action: str, details: str | None = None) -> None:
    """Log an action to the audit trail."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (id, system_id, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid4()), system_id, action, details, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_dashboard_stats() -> dict:
    """Get aggregate stats for the dashboard."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM ai_systems").fetchone()[0]
    high = conn.execute("SELECT COUNT(*) FROM ai_systems WHERE risk_level = 'high'").fetchone()[0]
    limited = conn.execute("SELECT COUNT(*) FROM ai_systems WHERE risk_level = 'limited'").fetchone()[0]
    minimal = conn.execute("SELECT COUNT(*) FROM ai_systems WHERE risk_level = 'minimal'").fetchone()[0]
    unclassified = conn.execute("SELECT COUNT(*) FROM ai_systems WHERE risk_level IS NULL").fetchone()[0]

    scores_row = conn.execute(
        "SELECT AVG(overall_compliance_score) FROM ai_systems WHERE overall_compliance_score IS NOT NULL"
    ).fetchone()
    avg_score = scores_row[0] or 0.0

    critical_gaps = 0
    assessments = conn.execute("SELECT gaps FROM assessments").fetchall()
    for row in assessments:
        gaps = json.loads(row[0])
        critical_gaps += sum(1 for g in gaps if g.get("severity") == "critical")

    conn.close()
    return {
        "total_systems": total,
        "high_risk_count": high,
        "limited_risk_count": limited,
        "minimal_risk_count": minimal,
        "unclassified_count": unclassified,
        "average_compliance_score": avg_score,
        "critical_gaps_count": critical_gaps,
    }


# Initialize on import
init_db()
