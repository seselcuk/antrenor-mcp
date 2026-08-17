"""Antrenör MCP Deney — Streamlit Dashboard.

MCP server'larla aynı SQLite DB'sini okur (mcp_servers/data/demo.db).
İki client, tek veri kaynağı: Streamlit görsel, Claude Desktop konuşmalı.

Çalıştırma:
    streamlit run streamlit_demo/app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

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

tab_act, tab_well, tab_pain = st.tabs(["Aktiviteler", "Wellness", "Ağrı"])

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
