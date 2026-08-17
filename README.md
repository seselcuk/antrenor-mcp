# Antrenör MCP — Deney / Öğrenme Projesi

> **Bu üretim değildir.** Ana Antrenör uygulamasının MCP (Model Context Protocol) versiyonunu deneyimlemek için oluşturulmuş yan projedir. Amaç: MCP mimarisini öğrenmek, ana projeye entegre olsaydı nasıl görüneceğini göstermek.

## Mimari

```
mcp_servers/data/demo.db  (SQLite — uydurma seed veri)
        ↑                    ↑
   MCP server'lar        Streamlit
   (Claude Desktop)      (localhost:8501)
```

**Anahtar fikir:** Bir veri kaynağı, iki farklı client — biri konuşmalı (Claude Desktop + MCP), biri görsel (Streamlit).

## Ana Projeyle Farkı

| | Ana Proje (üretim) | Bu Deney |
|---|---|---|
| **Model erişimi** | Push modeli — Worker prompt'a context yapıştırır | Pull modeli — Claude MCP server'lardan çeker |
| **Client** | iOS + Streamlit | Claude Desktop + Streamlit |
| **Deploy** | Cloudflare Workers + D1 | Lokal Python |
| **Veri kaynağı** | Gerçek Garmin API | Uydurma SQLite seed |
| **Amaç** | Kullanıcıya değer üretmek | Mimariyi öğrenmek/göstermek |

## MCP Server'lar

1. **garmin** — Aktivite geçmişi, wellness, HR zone dağılımı, haftalık yük (SQLite'tan)
2. **pain** — Ağrı geçmişi + yeni ağrı loglama (SQLite'ta INSERT)
3. **coach-rules** — `coach-principles.md` + `pain-rubric.md` prompt template'i olarak

Detay ve API için: [`mcp_servers/README.md`](mcp_servers/README.md)

## Hızlı Başlangıç

```bash
# 1. Bağımlılıklar
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. DB seed
.venv/bin/python -m mcp_servers.data.seed

# 3. Claude Desktop config kur
cp mcp_servers/claude_desktop_config.example.json \
   "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# 4. Claude Desktop'ı restart (Cmd+Q sonra yeniden aç)

# 5. Streamlit dashboard (opsiyonel, görsel demo için — port 8502, ana projenin 8501 ile çakışmaz)
.venv/bin/streamlit run streamlit_demo/app.py --server.port 8502
```

## Demo Senaryosu

Sunumda kullanılacak 3 senaryo ve akış için: [`DEMO.md`](DEMO.md)

## Klasör Yapısı

```
antrenör_mcp/
├── mcp_servers/
│   ├── garmin/server.py       Aktivite + wellness + zone MCP
│   ├── pain/server.py         Ağrı geçmişi + log_pain tool
│   ├── coach_rules/server.py  Prensipler + rubric prompt template
│   ├── data/seed.py           DB seed script
│   ├── data/demo.db           SQLite (git'e girmez)
│   └── claude_desktop_config.example.json
├── streamlit_demo/app.py      3 tab dashboard
├── docs/
│   ├── coach-principles.md    Zone 2, shin, deload kuralları
│   └── pain-rubric.md         0-10 ağrı ölçeği
├── DEMO.md                    Sunum senaryosu
└── requirements.txt
```
