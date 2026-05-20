"""
Lead model with MongoDB persistence via Motor (async).
Lazy-initialized: connects on first use — safe for serverless (Netlify Functions).
"""

import os
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

logger = logging.getLogger(__name__)


@dataclass
class Lead:
    id: str
    email: str
    name: Optional[str]
    phone: Optional[str]
    source: str
    whatsapp_notified: bool
    email_sent: bool
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "source": self.source,
            "whatsapp_notified": self.whatsapp_notified,
            "email_sent": self.email_sent,
            "created_at": self.created_at,
        }


def _doc_to_lead(doc: dict) -> Lead:
    return Lead(
        id=str(doc["_id"]),
        email=doc["email"],
        name=doc.get("name"),
        phone=doc.get("phone"),
        source=doc.get("source", "taller"),
        whatsapp_notified=bool(doc.get("whatsapp_notified", False)),
        email_sent=bool(doc.get("email_sent", False)),
        created_at=doc.get("created_at", ""),
    )


class LeadStore:
    """Async MongoDB lead store. Thread-safe via Motor's internal connection pool."""

    def __init__(self) -> None:
        self._col: Optional[AsyncIOMotorCollection] = None

    async def _get_col(self) -> AsyncIOMotorCollection:
        if self._col is None:
            mongo_uri = os.getenv("MONGOURI", "")
            if not mongo_uri:
                print("[mongodb] ERROR: MONGOURI env var not set")
                raise RuntimeError("MONGOURI env var is not set")
            print("[mongodb] connecting to Atlas...")
            client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self._col = client["ignia"]["leads"]
            await self._col.create_index("email", unique=True)
            print("[mongodb] connected OK — collection: ignia.leads")
        return self._col

    async def upsert(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        source: str = "taller",
    ) -> tuple[Lead, bool]:
        col = await self._get_col()
        email = email.lower().strip()

        existing = await col.find_one({"email": email})
        if existing:
            print(f"[mongodb] lead ya existe: {email}")
            return _doc_to_lead(existing), False

        doc = {
            "email": email,
            "name": name,
            "phone": phone,
            "source": source,
            "whatsapp_notified": False,
            "email_sent": False,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        result = await col.insert_one(doc)
        doc["_id"] = result.inserted_id
        print(f"[mongodb] lead guardado: {email} id={result.inserted_id}")
        return _doc_to_lead(doc), True

    async def mark_notified(self, email: str) -> None:
        col = await self._get_col()
        await col.update_one(
            {"email": email},
            {"$set": {"whatsapp_notified": True, "email_sent": True}},
        )

    async def all(self, limit: int = 200) -> list[Lead]:
        col = await self._get_col()
        cursor = col.find({}).sort("_id", -1).limit(limit)
        return [_doc_to_lead(doc) async for doc in cursor]

    async def count(self) -> int:
        col = await self._get_col()
        return await col.count_documents({})


lead_store = LeadStore()
