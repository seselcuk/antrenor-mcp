"""Antrenör MCP Deney — Streamlit Dashboard.

MCP server'larla aynı SQLite DB'sini okur (mcp_servers/data/demo.db).
İki client, tek veri kaynağı: Streamlit görsel, Claude Desktop konuşmalı.

Çalıştırma:
    streamlit run streamlit_demo/app.py
"""
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

TR_DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

DB_PATH = Path(__file__).parent.parent / "mcp_servers" / "data" / "demo.db"

st.set_page_config(page_title="Antrenör MCP Demo", page_icon=":runner:", layout="wide")


@st.cache_data(ttl=5)
def load_table(query: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)


st.title("Antrenör MCP — Demo Dashboard")
st.caption(f"Veri kaynağı: `{DB_PATH.name}` (aynı DB Claude Desktop MCP tarafından da okunuyor)")

if not DB_PATH.exists():
    st.error(f"DB bulunamadı: {DB_PATH}. Önce seed komutunu çalıştır: `python -m mcp_servers.data.seed`")
    st.stop()

tab_week, tab_act, tab_well, tab_pain = st.tabs(["📅 Bu Hafta", "Aktiviteler", "Wellness", "Ağrı"])

with tab_week:
    # Seed 2026-08-15'te bitiyor; gerçek "bugün" DB'nin dışında kalabildiği için
    # referans olarak DB'deki en son aktivite tarihini alıyoruz — böylece demo daima dolu.
    latest = load_table("SELECT MAX(date) AS d FROM activities").iloc[0]["d"]
    ref_day = datetime.strptime(latest, "%Y-%m-%d").date() if latest else date.today()
    week_start = ref_day - timedelta(days=ref_day.weekday())
    week_end = week_start + timedelta(days=6)
    iso_year, iso_week, _ = ref_day.isocalendar()

    st.subheader(f"Bu Hafta · {iso_year}-W{iso_week:02d}")
    st.caption(f"Pzt {week_start.isoformat()} → Paz {week_end.isoformat()}  ·  referans: DB'nin son aktivite günü ({ref_day})")

    week_df = load_table(
        f"SELECT date, sport, duration_min, distance_km, avg_hr, max_hr, training_load, "
        f"zone1_min, zone2_min, zone3_min, zone4_min, zone5_min "
        f"FROM activities WHERE date >= '{week_start.isoformat()}' AND date <= '{week_end.isoformat()}' "
        f"ORDER BY date"
    )

    if week_df.empty:
        st.info("Bu hafta aralığında aktivite yok.")
    else:
        total_min = int(week_df["duration_min"].sum())
        total_km = round(week_df["distance_km"].fillna(0).sum(), 1)
        total_load = int(week_df["training_load"].fillna(0).sum())
        run_df = week_df[week_df["sport"] == "running"]
        avg_hr_run = round(run_df["avg_hr"].mean(), 0) if not run_df.empty else None

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Antrenman", f"{len(week_df)}")
        c2.metric("Toplam süre", f"{total_min} dk")
        c3.metric("Toplam mesafe", f"{total_km} km")
        c4.metric("Toplam yük", f"{total_load}")

        if avg_hr_run is not None and avg_hr_run > 155:
            st.warning(
                f"Zone 2 uyarısı: Bu hafta koşu ort. HR **{int(avg_hr_run)}** — "
                "Zone 3-4 baskın görünüyor. Hedef: Z2 (<145 BPM)."
            )

        st.divider()
        st.markdown("**Gün gün antrenman**")

        by_date = {row["date"]: row for _, row in week_df.iterrows()}
        for i in range(7):
            d = week_start + timedelta(days=i)
            row = by_date.get(d.isoformat())
            cols = st.columns([1, 5])
            cols[0].markdown(f"**{TR_DAYS[i]}** · {d.strftime('%m-%d')}")
            if row is None:
                cols[1].markdown("_(dinlenme)_")
            else:
                sport = row["sport"]
                dur = int(row["duration_min"])
                parts = [f"✅ **{sport}**", f"{dur} dk"]
                if pd.notna(row["distance_km"]):
                    parts.append(f"{row['distance_km']} km")
                if pd.notna(row["avg_hr"]):
                    parts.append(f"avg HR {int(row['avg_hr'])}")
                cols[1].markdown(" · ".join(parts))

        st.divider()
        st.subheader("Son 4 Haftanın Yük Trendi")
        st.caption("MCP `weekly_load_summary` tool'unun görsel karşılığı")
        trend = load_table(
            "SELECT strftime('%Y-W%W', date) AS week, "
            "COUNT(*) AS antrenman, "
            "COALESCE(SUM(training_load), 0) AS toplam_yuk, "
            "COALESCE(SUM(duration_min), 0) AS toplam_dk "
            "FROM activities GROUP BY week ORDER BY week DESC LIMIT 4"
        ).sort_values("week")
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.bar_chart(trend.set_index("week")[["toplam_yuk"]])
        with col_b:
            st.dataframe(trend, use_container_width=True, hide_index=True)

with tab_act:
    st.subheader("Son 30 Gün Aktivite")
    df = load_table("SELECT date, sport, duration_min, distance_km, avg_hr, max_hr, avg_pace_per_km, training_load FROM activities ORDER BY date DESC")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("HR Zone Dağılımı (30 gün toplam)")
    zones = load_table(
        "SELECT SUM(zone1_min) z1, SUM(zone2_min) z2, SUM(zone3_min) z3, SUM(zone4_min) z4, SUM(zone5_min) z5 FROM activities"
    ).iloc[0]
    zone_df = pd.DataFrame({"zone": ["Z1", "Z2", "Z3", "Z4", "Z5"], "minutes": zones.values})
    col1, col2 = st.columns([2, 1])
    with col1:
        st.bar_chart(zone_df.set_index("zone"))
    with col2:
        total = int(zones.sum())
        zone_df["pct"] = (zone_df["minutes"] / total * 100).round(1)
        st.dataframe(zone_df, use_container_width=True, hide_index=True)

with tab_well:
    st.subheader("Son 30 Gün Wellness")
    df = load_table("SELECT date, hrv_ms, rhr_bpm, sleep_hours, sleep_score, stress_avg, body_battery_max, readiness_score FROM wellness ORDER BY date DESC")
    st.dataframe(df, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("HRV Trendi")
        st.line_chart(df.sort_values("date").set_index("date")[["hrv_ms"]])
    with col2:
        st.subheader("Uyku Süresi")
        st.line_chart(df.sort_values("date").set_index("date")[["sleep_hours"]])

with tab_pain:
    st.subheader("Ağrı Kayıtları")
    df = load_table("SELECT timestamp, region, side, severity, context, notes FROM pain_logs ORDER BY timestamp DESC")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Bölgeye Göre Özet")
    by_region = load_table(
        "SELECT region, COUNT(*) AS kayit, ROUND(AVG(severity), 1) AS ortalama_siddet, MAX(severity) AS max_siddet FROM pain_logs GROUP BY region ORDER BY kayit DESC"
    )
    st.dataframe(by_region, use_container_width=True, hide_index=True)
