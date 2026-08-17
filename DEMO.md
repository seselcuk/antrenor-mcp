# Demo Senaryosu — MCP Sunumu

Sunumda Claude Desktop + Streamlit ikilisiyle gösterilecek akış. Anahtar mesaj: **tek DB, iki farklı client — biri görsel (Streamlit), biri konuşmalı (Claude Desktop + MCP).**

## Ön Hazırlık (sunumdan önce)

1. Terminal 1'de Streamlit çalıştır (port 8502 — ana projenin 8501'i ile çakışmasın):
   ```bash
   cd <repo-yolu>  # örn: ~/projects/antrenor-mcp
   .venv/bin/streamlit run streamlit_demo/app.py --server.port 8502
   ```
   Tarayıcıda `http://localhost:8502` açılsın.
2. Claude Desktop uygulaması açık ve MCP server'ları bağlı olsun (config kurulu + uygulama restart edilmiş).

---

## Senaryo 1 — Garmin MCP (resource + tool)

**Claude Desktop'a sor:**
> "Son 30 günde HR zone dağılımım nasıl? Zone 2 disiplinim iyi mi?"

**Beklenen:**
- Claude `garmin` server'ından `zone_distribution_summary` tool'unu çağırır
- SQL sorgusu koşar, zone dağılımı JSON döner (Zone 3-4 baskın)
- Claude yorum yapar: *"Zone 2 hedefine göre yetersiz, Zone 3-4 çoğunlukta"*

**Ekranda göster:** Streamlit sekmesine geç → "Aktiviteler" tab'ındaki HR Zone Dağılımı grafiği aynı sonucu görsel olarak gösteriyor. **Anahtar mesaj:** Aynı DB, Claude JSON çekti, Streamlit grafik çizdi.

---

## Senaryo 2 — Pain MCP (yazma aksiyonu)

**Claude Desktop'a sor:**
> "Bugün sağ shin'im koşu sonrası 4/10 gergin. Log'la."

**Beklenen:**
- Claude `pain` server'ının `log_pain` tool'unu çağırır
- Argümanları kendisi doldurur: `region=shin, side=right, severity=4, context=post_run`
- SQL INSERT çalışır, `pain_logs` tablosuna yeni satır
- Claude "kaydettim" onayı verir

**Ekranda göster:** Streamlit → "Ağrı" tab → sayfayı yenile → yeni kayıt en üstte görünür. **Anahtar mesaj:** MCP sadece okumaz, yazar da. LLM state değiştirebiliyor.

---

## Senaryo 3 — Coach Rules MCP + multi-server

**Claude Desktop'a sor:**
> "Shin splints için ne yapmalıyım? Son bir haftada 3 kez koştum."

**Beklenen (birden fazla server aynı anda):**
- `coach-rules` → `coach://principles` resource'u pull edilir
- `garmin` → `garmin://activities/recent` ile son koşular çekilir
- `pain` → `pain://logs/by-region` ile shin ağrı trendi çekilir
- Claude hepsini birleştirip bütünsel öneri verir

**Ekranda göster:** Claude'un yanıtındaki "koşu detayları" ile Streamlit'teki Aktiviteler tab'ındaki tablo aynı sayıları söylüyor. **Anahtar mesaj:** MCP birden fazla kaynağı orkestre eder, LLM verinin akışını kendi kararlaştırır.

---

## Sunum Akışı Önerisi (3 dakika)

1. (15s) **Problemi göster:** "Ana projede LLM'e her seferinde tüm veriyi prompt'a yapıştırıyorduk"
2. (20s) **MCP mimarisi:** "MCP'de LLM ihtiyacı olanı kendisi çekiyor — protokol standart, aynı DB'ye farklı client'lar bağlanabilir"
3. (15s) **Streamlit'i aç:** "Aynı DB'yi görsel olarak gösteriyorum"
4. (45s) **Senaryo 1 canlı** — Zone dağılımı sorusu + Streamlit'te aynı grafik
5. (45s) **Senaryo 2 canlı** — Ağrı logla + Streamlit'te yeni satır
6. (30s) **Kapanış:** "Sunumdaki her şey local demo DB. Prod'da bu server'lar gerçek Garmin API'sine bağlanır, mimari aynı kalır."

## Manuel İş (senin yapman gereken)

- [ ] Claude Desktop config kuruldu (Claude tarafından `~/Library/Application Support/Claude/claude_desktop_config.json` yazıldı)
- [ ] Claude Desktop uygulamasını tam kapat + yeniden aç (Cmd+Q, sonra tekrar)
- [ ] Terminal 1'de Streamlit çalıştır: `.venv/bin/streamlit run streamlit_demo/app.py`
- [ ] Claude Desktop'ta yeni sohbet aç → 3 senaryoyu manuel test et
- [ ] Hata varsa log'lardan (`~/Library/Logs/Claude/mcp*.log`) çıktı topla
- [ ] QuickTime ile ekran kaydı al (canlı demo yerine güvenli fallback)
