"""
Lead model with SQLite persistence (stdlib sqlite3 — no extra dependencies).
DB file: data/leads.db  (relative to repo root, created automatically).
"""

import sqlite3
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "leads.db"


@dataclass
class Lead:
    id: int
    email: str
    name: Optional[str]
    phone: Optional[str]
    source: str
    whatsapp_notified: bool
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "source": self.source,
            "whatsapp_notified": self.whatsapp_notified,
            "created_at": self.created_at,
        }


def _row_to_lead(row: tuple) -> Lead:
    return Lead(
        id=row[0],
        email=row[1],
        name=row[2],
        phone=row[3],
        source=row[4],
        whatsapp_notified=bool(row[5]),
        created_at=row[6],
    )


class LeadStore:
    """Thread-safe SQLite lead store."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                    email              TEXT    UNIQUE NOT NULL,
                    name               TEXT,
                    phone              TEXT,
                    source             TEXT    NOT NULL DEFAULT 'taller',
                    whatsapp_notified  INTEGER NOT NULL DEFAULT 0,
                    created_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                )
            """)
            conn.commit()
        logger.info("LeadStore initialised at %s", self.db_path)

    def upsert(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        source: str = "taller",
    ) -> tuple[Lead, bool]:
        """
        Insert a new lead or return the existing one.
        Returns (lead, is_new).
        """
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id, email, name, phone, source, whatsapp_notified, created_at FROM leads WHERE email = ?",
                (email.lower().strip(),),
            ).fetchone()

            if existing:
                return _row_to_lead(tuple(existing)), False

            cursor = conn.execute(
                "INSERT INTO leads (email, name, phone, source) VALUES (?, ?, ?, ?)",
                (email.lower().strip(), name, phone, source),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, email, name, phone, source, whatsapp_notified, created_at FROM leads WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return _row_to_lead(tuple(row)), True

    def mark_notified(self, lead_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE leads SET whatsapp_notified = 1 WHERE id = ?", (lead_id,))
            conn.commit()

    def all(self, limit: int = 200) -> list[Lead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, email, name, phone, source, whatsapp_notified, created_at FROM leads ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [_row_to_lead(tuple(r)) for r in rows]

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]


# Singleton
lead_store = LeadStore()
