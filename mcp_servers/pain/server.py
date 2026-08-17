"""Ağrı MCP Server — SQLite demo DB'sinde ağrı loglarını okur ve yazar."""
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).parent.parent / "data" / "demo.db"

mcp = MCPServer("pain")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_json(rows: list[sqlite3.Row]) -> str:
    return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)


@mcp.resource("pain://logs/recent")
def recent_pain_logs() -> str:
    """Son 30 günün ağrı logları, en yenisi üstte."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM pain_logs ORDER BY timestamp DESC LIMIT 30"
        ).fetchall()
    return _rows_to_json(rows)


@mcp.resource("pain://logs/by-region")
def pain_by_region() -> str:
    """Ağrı loglarını bölgeye göre gruplar (trend takibi için)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT region, COUNT(*) AS count, AVG(severity) AS avg_severity, MAX(severity) AS max_severity "
            "FROM pain_logs GROUP BY region ORDER BY count DESC"
        ).fetchall()
    return _rows_to_json(rows)


@mcp.tool()
def log_pain(
    region: str,
    side: str,
    severity: int,
    context: str,
    notes: str = "",
) -> str:
    """Yeni ağrı logu ekler.

    region: shin, knee, hip, calf, foot, back, other
    side: left, right, both
    severity: 0-10 (pain-rubric.md ölçeği)
    context: morning, post_run, rest, during_run, other
    notes: serbest metin
    """
    if not 0 <= severity <= 10:
        return json.dumps({"error": "severity 0-10 aralığında olmalı"})

    log_id = f"p{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO pain_logs (id, timestamp, region, side, severity, context, notes) VALUES (?,?,?,?,?,?,?)",
            (log_id, timestamp, region, side, severity, context, notes),
        )
        conn.commit()
    return json.dumps(
        {
            "ok": True,
            "logged": {
                "id": log_id,
                "timestamp": timestamp,
                "region": region,
                "side": side,
                "severity": severity,
                "context": context,
                "notes": notes,
            },
        },
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
