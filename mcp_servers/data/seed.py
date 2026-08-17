"""Demo DB oluştur ve uydurma veri seed et.

Kullanım:
    python -m mcp_servers.data.seed          # DB'yi resetler ve doldurur
    python -m mcp_servers.data.seed --keep   # varsa dokunmaz, yoksa oluşturur
"""
import argparse
import random
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    sport TEXT NOT NULL,
    duration_min INTEGER NOT NULL,
    distance_km REAL,
    avg_hr INTEGER,
    max_hr INTEGER,
    avg_pace_per_km TEXT,
    training_load INTEGER,
    zone1_min INTEGER DEFAULT 0,
    zone2_min INTEGER DEFAULT 0,
    zone3_min INTEGER DEFAULT 0,
    zone4_min INTEGER DEFAULT 0,
    zone5_min INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS wellness (
    date TEXT PRIMARY KEY,
    hrv_ms INTEGER,
    rhr_bpm INTEGER,
    sleep_hours REAL,
    sleep_score INTEGER,
    stress_avg INTEGER,
    body_battery_max INTEGER,
    readiness_score INTEGER
);

CREATE TABLE IF NOT EXISTS pain_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    region TEXT NOT NULL,
    side TEXT,
    severity INTEGER NOT NULL,
    context TEXT,
    notes TEXT
);
"""


def make_activities(days: int = 30) -> list[tuple]:
    """30 gün için Zone 3-4 baskın koşu profilinde aktivite üret."""
    random.seed(42)
    today = datetime(2026, 8, 15).date()
    rows = []
    for offset in range(days):
        d = today - timedelta(days=offset)
        wd = d.weekday()
        if wd in (0, 2, 4):  # Pzt, Çar, Cum → koşu
            dur = random.randint(35, 60)
            dist = round(dur / 6.2, 1)
            avg_hr = random.randint(150, 160)
            max_hr = avg_hr + random.randint(8, 16)
            pace = f"6:{random.randint(5, 25):02d}"
            load = int(dur * random.uniform(1.7, 2.1))
            z1_pct = random.uniform(0.06, 0.12)
            z2_pct = random.uniform(0.40, 0.52)
            z3_pct = random.uniform(0.30, 0.40)
            z4_pct = random.uniform(0.04, 0.11)
            total = z1_pct + z2_pct + z3_pct + z4_pct
            z1 = round(dur * z1_pct / total)
            z2 = round(dur * z2_pct / total)
            z3 = round(dur * z3_pct / total)
            z4 = max(0, dur - z1 - z2 - z3)
            rows.append((d.isoformat(), "running", dur, dist, avg_hr, max_hr, pace, load, z1, z2, z3, z4, 0))
        elif wd == 5:  # Cmt → bisiklet (Zone 2 baskın)
            dur = random.randint(60, 90)
            dist = round(dur * random.uniform(0.32, 0.4), 1)
            avg_hr = random.randint(135, 148)
            max_hr = avg_hr + random.randint(15, 25)
            load = int(dur * random.uniform(1.0, 1.3))
            z1 = random.randint(8, 15)
            z2 = random.randint(28, 40)
            z3 = random.randint(15, 25)
            z4 = max(0, dur - z1 - z2 - z3)
            rows.append((d.isoformat(), "cycling", dur, dist, avg_hr, max_hr, None, load, z1, z2, z3, z4, 0))
        elif wd == 3:  # Per → kuvvet
            dur = random.randint(40, 55)
            avg_hr = random.randint(110, 125)
            max_hr = avg_hr + random.randint(20, 30)
            load = int(dur * 0.9)
            z1 = random.randint(20, 30)
            z2 = random.randint(10, 18)
            z3 = max(0, dur - z1 - z2)
            rows.append((d.isoformat(), "strength", dur, None, avg_hr, max_hr, None, load, z1, z2, z3, 0, 0))
    return rows


def make_wellness(days: int = 30) -> list[tuple]:
    random.seed(101)
    today = datetime(2026, 8, 15).date()
    rows = []
    for offset in range(days):
        d = today - timedelta(days=offset)
        hrv = random.randint(36, 48)
        rhr = random.randint(52, 58)
        sleep = round(random.uniform(6.3, 8.0), 1)
        sleep_score = int(sleep * 10 + random.randint(-5, 5))
        stress = random.randint(25, 50)
        battery = random.randint(70, 95)
        readiness = int((hrv - 35) * 3 + (sleep - 6) * 15 + random.randint(-8, 8))
        readiness = max(40, min(95, readiness))
        rows.append((d.isoformat(), hrv, rhr, sleep, sleep_score, stress, battery, readiness))
    return rows


def make_pain_logs(count: int = 15) -> list[tuple]:
    random.seed(7)
    today = datetime(2026, 8, 15)
    regions = [
        ("shin", "right", 55),
        ("shin", "both", 15),
        ("shin", "left", 10),
        ("knee", "left", 8),
        ("calf", "right", 7),
        ("foot", "right", 5),
    ]
    contexts = ["post_run", "morning", "rest", "during_run"]
    weights = [r[2] for r in regions]
    rows = []
    for i in range(count):
        days_back = random.randint(0, 29)
        ts = (today - timedelta(days=days_back, hours=random.randint(0, 23))).isoformat(timespec="seconds")
        region, side, _ = random.choices(regions, weights=weights, k=1)[0]
        severity = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 25, 30, 20, 10, 5], k=1)[0]
        context = random.choice(contexts)
        note_pool = {
            "post_run": f"Koşu sonrası {region} bölgesinde gerginlik hissettim.",
            "morning": f"Sabah uyanınca hafif {region} baskısı vardı.",
            "rest": f"Dinlenirken bile hissediyorum, hafif ama sürekli.",
            "during_run": f"Koşunun ortasında {region} sıkıştı.",
        }
        rows.append((f"p{uuid.uuid4().hex[:6]}", ts, region, side, severity, context, note_pool[context]))
    return rows


def init_db(reset: bool = True) -> None:
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        if reset:
            conn.executemany(
                "INSERT INTO activities (date, sport, duration_min, distance_km, avg_hr, max_hr, avg_pace_per_km, training_load, zone1_min, zone2_min, zone3_min, zone4_min, zone5_min) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                make_activities(),
            )
            conn.executemany(
                "INSERT INTO wellness VALUES (?,?,?,?,?,?,?,?)",
                make_wellness(),
            )
            conn.executemany(
                "INSERT INTO pain_logs VALUES (?,?,?,?,?,?,?)",
                make_pain_logs(),
            )
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", action="store_true", help="Varolan DB'yi silme, yoksa oluştur")
    args = parser.parse_args()
    reset = not args.keep
    init_db(reset=reset)
    conn = sqlite3.connect(DB_PATH)
    a = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    w = conn.execute("SELECT COUNT(*) FROM wellness").fetchone()[0]
    p = conn.execute("SELECT COUNT(*) FROM pain_logs").fetchone()[0]
    conn.close()
    print(f"DB: {DB_PATH}")
    print(f"  activities: {a}")
    print(f"  wellness:   {w}")
    print(f"  pain_logs:  {p}")
