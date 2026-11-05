"""SQLite local persistence and optional PostgreSQL persistence for hosted deployments."""

import csv
import io
import json
import os
import sqlite3
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None

DB_PATH = Path(os.environ.get("GLOBAL_ASSISTANT_DB", Path(__file__).parent / "data" / "assistant.sqlite3"))


def using_postgres():
    return bool(
        os.environ.get("GLOBAL_ASSISTANT_DATABASE_URL")
        or os.environ.get("GLOBAL_ASSISTANT_DB_HOST")
    )


def _execute(connection, statement, parameters=()):
    if using_postgres():
        statement = statement.replace("?", "%s")
    return connection.execute(statement, parameters)


def _executemany(connection, statement, parameters):
    if using_postgres():
        statement = statement.replace("?", "%s")
    return connection.executemany(statement, parameters)


@contextmanager
def _connect():
    if using_postgres():
        if psycopg is None or dict_row is None:
            raise RuntimeError(
                "PostgreSQL is configured but psycopg is unavailable; install the project requirements."
            )
        database_url = os.environ.get("GLOBAL_ASSISTANT_DATABASE_URL")
        if database_url:
            connection = psycopg.connect(
                database_url,
                connect_timeout=15,
                row_factory=dict_row,
            )
        else:
            required = (
                "GLOBAL_ASSISTANT_DB_NAME",
                "GLOBAL_ASSISTANT_DB_USER",
                "GLOBAL_ASSISTANT_DB_PASSWORD",
            )
            missing = [key for key in required if not os.environ.get(key)]
            if missing:
                raise RuntimeError(f"Missing PostgreSQL settings: {', '.join(missing)}.")
            host = os.environ["GLOBAL_ASSISTANT_DB_HOST"]
            connection = psycopg.connect(
                host=host,
                dbname=os.environ["GLOBAL_ASSISTANT_DB_NAME"],
                user=os.environ["GLOBAL_ASSISTANT_DB_USER"],
                password=os.environ["GLOBAL_ASSISTANT_DB_PASSWORD"],
                sslmode="disable" if host.startswith("/cloudsql/") else "require",
                connect_timeout=15,
                row_factory=dict_row,
            )
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(DB_PATH, timeout=15)
        connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize():
    id_type = "BIGSERIAL" if using_postgres() else "INTEGER"
    with _connect() as connection:
        statements = [
            f"""
            CREATE TABLE IF NOT EXISTS messages (
                id {id_type} PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                tag TEXT,
                confidence REAL,
                language TEXT NOT NULL DEFAULT 'en',
                project_id TEXT,
                created_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS messages_session_id_idx ON messages(session_id, id)",
            f"""
            CREATE TABLE IF NOT EXISTS custom_faq (
                id {id_type} PRIMARY KEY,
                question TEXT NOT NULL UNIQUE,
                answer TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Custom',
                language TEXT NOT NULL DEFAULT 'en',
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                instructions TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS mobile_media_tasks (
                task_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS mobile_media_tasks_user_idx ON mobile_media_tasks(user_id, created_at)",
        ]
        for statement in statements:
            _execute(connection, statement)
        if using_postgres():
            _execute(connection, "ALTER TABLE messages ADD COLUMN IF NOT EXISTS project_id TEXT")
        else:
            columns = {
                dict(row)["name"] for row in _execute(
                    connection, "PRAGMA table_info(messages)"
                ).fetchall()
            }
            if "project_id" not in columns:
                _execute(connection, "ALTER TABLE messages ADD COLUMN project_id TEXT")


def save_message(session_id, role, content, tag=None, confidence=None, language="en", project_id=None):
    with _connect() as connection:
        _execute(
            connection,
            """INSERT INTO messages
               (session_id, role, content, tag, confidence, language, project_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, role, content, tag, confidence, language,
                project_id,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )


def get_history(session_id):
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT role, content, tag, confidence, language, created_at FROM messages "
            "WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_history(session_id):
    with _connect() as connection:
        _execute(connection, "DELETE FROM messages WHERE session_id = ?", (session_id,))


def get_all_messages():
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT session_id, role, content, tag, confidence, language, project_id, created_at "
            "FROM messages ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_project_messages(project_id):
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT session_id, role, content, tag, confidence, language, project_id, created_at "
            "FROM messages WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_faq(question, answer, category="Custom", language="en"):
    question, answer = question.strip(), answer.strip()
    if not question or not answer:
        raise ValueError("Both question and answer are required.")
    with _connect() as connection:
        _execute(
            connection,
            "INSERT INTO custom_faq(question, answer, category, language, created_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(question) DO UPDATE SET answer=excluded.answer, "
            "category=excluded.category, language=excluded.language",
            (
                question, answer, category.strip() or "Custom", language,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )


def find_custom_faq(message, language=None):
    normalized = " ".join(message.lower().split())
    with _connect() as connection:
        if language:
            rows = _execute(
                connection,
                "SELECT question, answer, category, language FROM custom_faq WHERE language = ?",
                (language,),
            ).fetchall()
        else:
            rows = _execute(
                connection,
                "SELECT question, answer, category, language FROM custom_faq"
            ).fetchall()
    for row in rows:
        faq = dict(row)
        if normalized == " ".join(faq["question"].lower().split()):
            return faq
    return None


def import_faq_csv(file_bytes):
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    required = {"question", "answer"}
    if not reader.fieldnames or not required.issubset({name.strip().lower() for name in reader.fieldnames}):
        raise ValueError("CSV needs question and answer columns; category and language are optional.")
    names = {name.strip().lower(): name for name in reader.fieldnames}
    rows = []
    for line_number, row in enumerate(reader, start=2):
        question = (row.get(names["question"]) or "").strip()
        answer = (row.get(names["answer"]) or "").strip()
        if not question or not answer:
            raise ValueError(f"CSV line {line_number} has an empty question or answer.")
        rows.append((
            question,
            answer,
            (row.get(names["category"]) or "Custom").strip() if "category" in names else "Custom",
            (row.get(names["language"]) or "en").strip() if "language" in names else "en",
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ))
    if not rows:
        raise ValueError("CSV has no FAQ rows to import.")
    with _connect() as connection:
        _executemany(
            connection,
            "INSERT INTO custom_faq(question, answer, category, language, created_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(question) DO UPDATE SET answer=excluded.answer, "
            "category=excluded.category, language=excluded.language",
            rows,
        )
    return len(rows)


def get_faq_rows():
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT question, answer, category, language, created_at FROM custom_faq ORDER BY category, question"
        ).fetchall()
    return [dict(row) for row in rows]


def get_setting(key):
    with _connect() as connection:
        row = _execute(
            connection,
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
    return dict(row)["value"] if row else None


def set_setting(key, value):
    with _connect() as connection:
        _execute(
            connection,
            "INSERT INTO app_settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def create_project(name, description=""):
    name = name.strip()
    if not name:
        raise ValueError("Project name is required.")
    project_id = os.urandom(12).hex()
    with _connect() as connection:
        _execute(
            connection,
            "INSERT INTO projects(id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (project_id, name, description.strip(), datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    return project_id


def get_projects():
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT id, name, description, created_at FROM projects ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


def create_agent(name, instructions):
    name, instructions = name.strip(), instructions.strip()
    if not name or not instructions:
        raise ValueError("Agent name and instructions are required.")
    agent_id = os.urandom(12).hex()
    with _connect() as connection:
        _execute(
            connection,
            "INSERT INTO agents(id, name, instructions, created_at) VALUES (?, ?, ?, ?)",
            (agent_id, name, instructions, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    return agent_id


def get_agents():
    with _connect() as connection:
        rows = _execute(
            connection,
            "SELECT id, name, instructions, created_at FROM agents ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


def register_mobile_media_task(task_id, user_id):
    with _connect() as connection:
        _execute(
            connection,
            "INSERT INTO mobile_media_tasks(task_id, user_id, created_at) VALUES (?, ?, ?)",
            (task_id, user_id, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )


def owns_mobile_media_task(task_id, user_id):
    with _connect() as connection:
        row = _execute(
            connection,
            "SELECT task_id FROM mobile_media_tasks WHERE task_id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
    return row is not None


def faq_csv():
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=("question", "answer", "category", "language", "created_at"))
    writer.writeheader()
    writer.writerows(get_faq_rows())
    return output.getvalue().encode("utf-8-sig")


def make_backup_zip():
    initialize()
    if using_postgres():
        with _connect() as connection:
            tables = (
                "messages", "custom_faq", "app_settings", "projects", "agents",
                "mobile_media_tasks",
            )
            data = {
                table: [dict(row) for row in _execute(connection, f"SELECT * FROM {table}").fetchall()]
                for table in tables
            }
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "assistant-postgres-export.json",
                json.dumps(data, ensure_ascii=False, indent=2, default=str),
            )
            archive.writestr("custom_faq.csv", faq_csv())
            archive.writestr(
                "README.txt",
                "Portable data export from PostgreSQL; this is not a restorable database dump.\n"
                "Use Cloud SQL automated backups for point-in-time recovery.\n"
                "Keep this file private: it contains user-submitted conversations.\n",
            )
        return output.getvalue()

    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = Path(temp_dir) / "assistant.sqlite3"
        source = sqlite3.connect(DB_PATH)
        backup = sqlite3.connect(backup_path)
        try:
            source.backup(backup)
        finally:
            backup.close()
            source.close()
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(backup_path, "assistant.sqlite3")
            archive.writestr("custom_faq.csv", faq_csv())
            archive.writestr(
                "README.txt",
                "Backup contains persistent chat history and admin-managed FAQ records.\n"
                "Keep this file private: it may contain user-submitted conversations.\n",
            )
        return output.getvalue()
