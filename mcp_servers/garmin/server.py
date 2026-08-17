"""Garmin MCP Server — SQLite demo DB'sinden aktivite ve wellness verisi sunar."""
import json
import sqlite3
from pathlib import Path
from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).parent.parent / "data" / "demo.db"

mcp = MCPServer("garmin")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_json(rows: list[sqlite3.Row]) -> str:
    return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)


@mcp.resource("garmin://activities/recent")
def recent_activities() -> str:
    """Son 30 günün Garmin aktivite kayıtları."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM activities ORDER BY date DESC LIMIT 30"
        ).fetchall()
    return _rows_to_json(rows)


@mcp.resource("garmin://wellness/recent")
def recent_wellness() -> str:
    """Son 30 günün wellness verisi: HRV, RHR, uyku, hazır olma skoru."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM wellness ORDER BY date DESC LIMIT 30"
        ).fetchall()
    return _rows_to_json(rows)


@mcp.tool()
def get_activities_by_sport(sport: str) -> str:
    """Belirli bir spora ait aktiviteleri döner (running, cycling, strength)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM activities WHERE sport = ? ORDER BY date DESC", (sport,)
        ).fetchall()
    return _rows_to_json(rows)


@mcp.tool()
def zone_distribution_summary() -> str:
    """Son 30 günün HR zone dağılımını özetler — Zone 2 disiplinini denetlemek için."""
    with _connect() as conn:
        row = conn.execute(
            """SELECT
                COALESCE(SUM(zone1_min), 0) AS z1,
                COALESCE(SUM(zone2_min), 0) AS z2,
                COALESCE(SUM(zone3_min), 0) AS z3,
                COALESCE(SUM(zone4_min), 0) AS z4,
                COALESCE(SUM(zone5_min), 0) AS z5
            FROM activities"""
        ).fetchone()
    totals = dict(row)
    grand = sum(totals.values()) or 1
    summary = {
        zone: {"minutes": mins, "pct": round(100 * mins / grand, 1)}
        for zone, mins in totals.items()
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def weekly_load_summary() -> str:
    """Son 4 haftanın antrenman yükü toplamı — deload/yüksek yük dönemlerini görmek için."""
    with _connect() as conn:
        rows = conn.execute(
            """SELECT
                strftime('%Y-W%W', date) AS week,
                COUNT(*) AS session_count,
                COALESCE(SUM(training_load), 0) AS total_load,
                COALESCE(SUM(duration_min), 0) AS total_minutes
            FROM activities
            GROUP BY week
            ORDER BY week DESC
            LIMIT 4"""
        ).fetchall()
    return _rows_to_json(rows)


if __name__ == "__main__":
    mcp.run()
