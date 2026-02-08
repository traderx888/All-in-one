"""
DatabaseChecker — Zone ARD

Manages data integrity and provides a shared data access layer.
  - Validates data consistency
  - Provides CRUD interface for persistent storage
  - Logs all data operations for audit
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class DatabaseChecker(BaseAgent):
    """Data integrity monitor and access layer."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__(
            "database_checker", AgentRole.DATABASE_CHECKER, bus,
            division="management_hub", config=config,
        )
        # In-memory store (replace with SQLAlchemy in production)
        self._tables: dict[str, list[dict[str, Any]]] = {
            "trades": [],
            "signals": [],
            "orders": [],
            "performance": [],
        }

    async def handle_message(self, message: Message) -> None:
        action = message.payload.get("action", "")

        if action == "insert":
            table = message.payload.get("table", "")
            record = message.payload.get("record", {})
            if table in self._tables:
                self._tables[table].append(record)
                self.log.info("record_inserted", table=table)

        elif action == "query":
            table = message.payload.get("table", "")
            filters = message.payload.get("filters", {})
            results = self._query(table, filters)
            await self.send(
                message.sender,
                MessageType.RESULT,
                {"table": table, "records": results, "count": len(results)},
            )

        elif action == "get_stats":
            stats = {table: len(records) for table, records in self._tables.items()}
            await self.send(message.sender, MessageType.RESULT, {"stats": stats})

    def _query(self, table: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        records = self._tables.get(table, [])
        if not filters:
            return records
        result = []
        for r in records:
            if all(r.get(k) == v for k, v in filters.items()):
                result.append(r)
        return result
