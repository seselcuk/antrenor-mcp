# MCP Servers — Antrenör Deney Projesi

Bu klasörde 3 adet MCP (Model Context Protocol) server var. Claude Desktop bunlara bağlanır ve `mcp_servers/data/demo.db` SQLite veritabanına "kendi kararıyla" ulaşır. Aynı DB'yi `streamlit_demo/app.py` de görsel dashboard olarak sunar — tek veri kaynağı, iki client.

## Server'lar

| Server | Ne sunar | Örnek soru |
|---|---|---|
| **garmin** | Aktivite geçmişi, wellness, HR zone dağılımı, haftalık yük | "Son 30 günde ne kadar Zone 2 koştum?" |
| **pain** | Ağrı geçmişi + yeni ağrı loglama | "Sağ shin'im 4/10 ağrıyor, koşu sonrası" |
| **coach-rules** | Koçluk prensipleri, ağrı rubric'i | "Shin splints için ne yapmalıyım?" |

## API Yüzeyi

### garmin (SQLite'a bağlı)
- Resource `garmin://activities/recent` — son 30 gün aktivite (`activities` tablosu)
- Resource `garmin://wellness/recent` — son 30 gün wellness (`wellness` tablosu)
- Tool `get_activities_by_sport(sport)` — spora göre filtreleme
- Tool `zone_distribution_summary()` — HR zone dağılım özeti (Zone 2 disiplin kontrolü)
- Tool `weekly_load_summary()` — son 4 haftanın toplam yükü/süresi

### pain (SQLite'a bağlı)
- Resource `pain://logs/recent` — son 30 gün ağrı logları
- Resource `pain://logs/by-region` — bölgeye göre gruplu istatistik (count, avg severity, max severity)
- Tool `log_pain(region, side, severity, context, notes)` — yeni ağrı ekle (INSERT)

### coach-rules (dosya bazlı)
- Resource `coach://principles` — `docs/coach-principles.md` içeriği
- Resource `coach://pain-rubric` — `docs/pain-rubric.md` içeriği
- Prompt `coach_assessment(user_message)` — kullanıcı mesajı için system prompt üretir

## Kurulum ve Bağlantı

### 1. Sanal ortam + bağımlılıklar
```bash
cd <repo-yolu>  # örn: ~/projects/antrenor-mcp
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. DB'yi seed et
```bash
.venv/bin/python -m mcp_servers.data.seed
```
Bu, `mcp_servers/data/demo.db`'yi resetleyip 30 gün uydurma veri ile doldurur (22 aktivite, 30 wellness, 15 ağrı).

### 3. Server'ları Claude Desktop'a bağla
`claude_desktop_config.example.json` içeriğini şu dosyaya kopyala:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 4. Claude Desktop'ı restart et
Yeni server'lar sadece restart sonrası görünür.

### 5. Streamlit dashboard'u aç (opsiyonel)
```bash
.venv/bin/streamlit run streamlit_demo/app.py --server.port 8502
```
Tarayıcıda `http://localhost:8502` — 3 tab (Aktiviteler, Wellness, Ağrı).

> **Not:** Port 8502 kullanıyoruz çünkü ana proje Streamlit'i default 8501'i kullanıyor — çakışmasın diye.

## Test (Claude Desktop olmadan)

MCP handshake ile server'ların doğru cevap verdiğini kontrol et:
```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | .venv/bin/python mcp_servers/garmin/server.py
```

## Veri Yapısı

`mcp_servers/data/demo.db` — SQLite, 3 tablo:
- `activities` — 30 gün, Zone 3-4 baskın koşu profili (Pzt/Çar/Cum koşu, Cmt bisiklet, Per kuvvet)
- `wellness` — 30 gün, HRV/RHR/uyku/hazır olma skoru
- `pain_logs` — 15 kayıt, shin baskılı, çeşitli context'ler

Seed script `mcp_servers/data/seed.py` içindedir. Tekrar üretmek için: `.venv/bin/python -m mcp_servers.data.seed`

Production'da bu server'lar gerçek Garmin API'ya bağlı bir DB kullanırdı — mimari aynı, kaynak farklı.
