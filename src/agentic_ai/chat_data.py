"""SQLite-based Chainlit data layer for conversation persistence.

Provides chat history, conversation sidebar, and thread management
using a local SQLite database. Used by the chat UI when
chat_persistence is set to "sqlite".

This module is only imported by chat.py and depends on chainlit
(optional dependency).
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from chainlit.data.base import BaseDataLayer
from chainlit.types import Feedback, PageInfo, PaginatedResponse, Pagination, ThreadFilter

if TYPE_CHECKING:
    from chainlit.element import ElementDict
    from chainlit.step import StepDict
    from chainlit.types import ThreadDict
    from chainlit.user import PersistedUser, User


class SQLiteDataLayer(BaseDataLayer):
    """Persist Chainlit conversations to a local SQLite database."""

    def __init__(self, db_path: str = ".chat_history.db") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                identifier TEXT UNIQUE NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                metadata TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT
            );
            CREATE TABLE IF NOT EXISTS steps (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                parent_id TEXT,
                name TEXT,
                type TEXT,
                input TEXT DEFAULT '',
                output TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}',
                start_time TEXT,
                end_time TEXT,
                show_input TEXT DEFAULT 'json',
                is_error INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS elements (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                step_id TEXT,
                name TEXT,
                type TEXT,
                url TEXT DEFAULT '',
                mime TEXT DEFAULT '',
                object_key TEXT DEFAULT '',
                display TEXT DEFAULT 'inline',
                size INTEGER,
                language TEXT,
                page INTEGER,
                chainlit_key TEXT,
                props TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                step_id TEXT NOT NULL,
                value REAL,
                comment TEXT
            );
        """)
        conn.commit()

    # --- User management ---

    async def get_user(self, identifier: str) -> PersistedUser | None:
        from chainlit.user import PersistedUser

        conn = self._get_conn()
        row = conn.execute("SELECT * FROM users WHERE identifier = ?", (identifier,)).fetchone()
        if not row:
            return None
        return PersistedUser(
            id=row["id"],
            identifier=row["identifier"],
            createdAt=row["created_at"],
            metadata=json.loads(row["metadata"]),
        )

    async def create_user(self, user: User) -> PersistedUser | None:
        from chainlit.user import PersistedUser

        conn = self._get_conn()
        existing = conn.execute(
            "SELECT * FROM users WHERE identifier = ?", (user.identifier,)
        ).fetchone()
        if existing:
            return PersistedUser(
                id=existing["id"],
                identifier=existing["identifier"],
                createdAt=existing["created_at"],
                metadata=json.loads(existing["metadata"]),
            )

        user_id = str(uuid.uuid4())
        now = datetime.now(tz=UTC).isoformat()
        conn.execute(
            "INSERT INTO users (id, identifier, metadata, created_at) VALUES (?, ?, ?, ?)",
            (user_id, user.identifier, json.dumps(user.metadata or {}), now),
        )
        conn.commit()
        return PersistedUser(
            id=user_id,
            identifier=user.identifier,
            createdAt=now,
            metadata=user.metadata or {},
        )

    # --- Thread management ---

    async def get_thread(self, thread_id: str) -> ThreadDict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM threads WHERE id = ? AND deleted_at IS NULL",
            (thread_id,),
        ).fetchone()
        if not row:
            return None
        thread = self._build_thread_dict(conn, row)
        return thread

    async def get_thread_author(self, thread_id: str) -> str:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT u.identifier FROM threads t JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (thread_id,),
        ).fetchone()
        return row["identifier"] if row else ""

    async def update_thread(
        self,
        thread_id: str,
        name: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        conn = self._get_conn()
        now = datetime.now(tz=UTC).isoformat()

        # Check if thread exists, create if not
        existing = conn.execute("SELECT id FROM threads WHERE id = ?", (thread_id,)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO threads (id, user_id, name, metadata, tags, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    thread_id,
                    user_id or "",
                    name or "",
                    json.dumps(metadata or {}),
                    json.dumps(tags or []),
                    now,
                    now,
                ),
            )
        else:
            updates = ["updated_at = ?"]
            params: list = [now]
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if user_id is not None:
                updates.append("user_id = ?")
                params.append(user_id)
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            params.append(thread_id)
            conn.execute(f"UPDATE threads SET {', '.join(updates)} WHERE id = ?", params)

        conn.commit()

    async def delete_thread(self, thread_id: str) -> None:
        conn = self._get_conn()
        now = datetime.now(tz=UTC).isoformat()
        conn.execute("UPDATE threads SET deleted_at = ? WHERE id = ?", (now, thread_id))
        conn.commit()

    async def list_threads(
        self, pagination: Pagination, filters: ThreadFilter
    ) -> PaginatedResponse[ThreadDict]:
        conn = self._get_conn()
        query = "SELECT * FROM threads WHERE deleted_at IS NULL"
        params: list = []

        if filters.userId:
            query += " AND user_id = ?"
            params.append(filters.userId)
        if filters.search:
            query += " AND name LIKE ?"
            params.append(f"%{filters.search}%")

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(pagination.first + 1)

        rows = conn.execute(query, params).fetchall()

        threads = [self._build_thread_dict(conn, row) for row in rows[: pagination.first]]

        has_next = len(rows) > pagination.first
        return PaginatedResponse(
            pageInfo=PageInfo(
                hasNextPage=has_next,
                startCursor=threads[0]["id"] if threads else None,
                endCursor=threads[-1]["id"] if threads else None,
            ),
            data=threads,
        )

    def _build_thread_dict(self, conn: sqlite3.Connection, row: sqlite3.Row) -> ThreadDict:
        steps = conn.execute(
            "SELECT * FROM steps WHERE thread_id = ? ORDER BY start_time", (row["id"],)
        ).fetchall()
        elements = conn.execute(
            "SELECT * FROM elements WHERE thread_id = ?", (row["id"],)
        ).fetchall()

        return {
            "id": row["id"],
            "createdAt": row["created_at"],
            "name": row["name"],
            "userId": row["user_id"],
            "userIdentifier": None,
            "metadata": json.loads(row["metadata"] or "{}"),
            "tags": json.loads(row["tags"] or "[]"),
            "steps": [self._step_to_dict(s) for s in steps],
            "elements": [self._element_to_dict(e) for e in elements],
        }

    # --- Step management ---

    async def create_step(self, step_dict: StepDict) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO steps "
            "(id, thread_id, parent_id, name, type, input, output, metadata, "
            "start_time, end_time, show_input, is_error, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                step_dict.get("id", str(uuid.uuid4())),
                step_dict.get("threadId", ""),
                step_dict.get("parentId"),
                step_dict.get("name", ""),
                step_dict.get("type", "run"),
                json.dumps(step_dict.get("input", "")),
                json.dumps(step_dict.get("output", "")),
                json.dumps(step_dict.get("metadata", {})),
                step_dict.get("start"),
                step_dict.get("end"),
                step_dict.get("showInput", "json"),
                1 if step_dict.get("isError") else 0,
                step_dict.get("createdAt", datetime.now(tz=UTC).isoformat()),
            ),
        )
        conn.commit()

    async def update_step(self, step_dict: StepDict) -> None:
        await self.create_step(step_dict)

    async def delete_step(self, step_id: str) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM steps WHERE id = ?", (step_id,))
        conn.commit()

    @staticmethod
    def _safe_json_load(value: str | None) -> object:
        if not value:
            return ""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def _step_to_dict(self, row: sqlite3.Row) -> StepDict:
        output = self._safe_json_load(row["output"])
        input_val = self._safe_json_load(row["input"])

        return {
            "id": row["id"],
            "threadId": row["thread_id"],
            "parentId": row["parent_id"],
            "name": row["name"],
            "type": row["type"],
            "input": input_val,
            "output": output,
            "metadata": json.loads(row["metadata"] or "{}"),
            "createdAt": row["created_at"],
            "start": row["start_time"],
            "end": row["end_time"],
            "showInput": row["show_input"] or "json",
            "isError": bool(row["is_error"]),
        }

    # --- Element management ---

    async def create_element(self, element: ElementDict) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO elements "
            "(id, thread_id, step_id, name, type, url, mime, object_key, "
            "display, size, language, page, chainlit_key, props) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                element.get("id", str(uuid.uuid4())),
                element.get("threadId", ""),
                element.get("forId"),
                element.get("name", ""),
                element.get("type", "file"),
                element.get("url", ""),
                element.get("mime", ""),
                element.get("objectKey", ""),
                element.get("display", "inline"),
                element.get("size"),
                element.get("language"),
                element.get("page"),
                element.get("chainlitKey"),
                json.dumps(element.get("props", {})),
            ),
        )
        conn.commit()

    async def get_element(self, thread_id: str, element_id: str) -> ElementDict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM elements WHERE id = ? AND thread_id = ?",
            (element_id, thread_id),
        ).fetchone()
        if not row:
            return None
        return self._element_to_dict(row)

    async def delete_element(self, element_id: str, thread_id: str | None = None) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM elements WHERE id = ?", (element_id,))
        conn.commit()

    def _element_to_dict(self, row: sqlite3.Row) -> ElementDict:
        return {
            "id": row["id"],
            "threadId": row["thread_id"],
            "type": row["type"],
            "url": row["url"] or "",
            "name": row["name"] or "",
            "mime": row["mime"] or "",
            "objectKey": row["object_key"] or "",
            "forId": row["step_id"] or "",
            "chainlitKey": row["chainlit_key"],
            "display": row["display"] or "inline",
            "size": row["size"],
            "language": row["language"],
            "page": row["page"],
            "props": json.loads(row["props"] or "{}"),
        }

    # --- Feedback management ---

    async def upsert_feedback(self, feedback: Feedback) -> str:
        conn = self._get_conn()
        feedback_id = feedback.id or str(uuid.uuid4())
        conn.execute(
            "INSERT OR REPLACE INTO feedback (id, step_id, value, comment) VALUES (?, ?, ?, ?)",
            (feedback_id, feedback.forId, feedback.value, feedback.comment),
        )
        conn.commit()
        return feedback_id

    async def delete_feedback(self, feedback_id: str) -> bool:
        conn = self._get_conn()
        conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        conn.commit()
        return True

    # --- Utility methods ---

    async def get_favorite_steps(self, user_id: str) -> list[StepDict]:
        return []

    async def build_debug_url(self) -> str:
        return ""

    async def close(self) -> None:
        self._conn.close()
