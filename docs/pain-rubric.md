# Ağrı Şiddet Rubric'i (0-10)

Kişiye özel — kronik shin splints/tibia yönetimi için. Coach hem plan hem
sohbet sırasında bu ölçeği referans alır. Kullanıcı ağrısını doğal dille
anlatır, coach bu ölçeğe göre yorumlar ve gerekirse "3 mü 4 mü?" gibi
soru sorup net rakama çeker.

## Ölçek

| Seviye | Tarif | Koşuya izin | Aksiyon |
|---|---|---|---|
| **0** | Ağrı yok, farkındalık yok | ✅ | Normal plan |
| **1** | Çok hafif farkındalık; "acaba var mı" hissi. Palpasyon (parmakla bastırma) temiz | ✅ | Normal plan |
| **2** | Palpasyonda hafif hassasiyet; koşarken hissetmiyorsun ya da sadece ilk 5 dk | ✅ | Normal plan + mobility |
| **3** | Sabah gerginlik, ısınmayla geçer; koşarken sürekli hatırlatmaz | ✅ (koşu-içi 3 ise hayır) | HR ceiling sıkı tut, izle |
| **4** | Koşarken farkındasın ama tempoyu değiştirmiyorsun; ertesi gün merdiven inerken hissedersin | ⚠️ Kısıtlı | Sonraki koşuyu %30 kısalt, HR ceiling düşür |
| **5** | Koşarken sürekli hatırlatır, formu değiştiresin gelir; koşu sonrası 1-2h sürer | ❌ | 48h koşu yok; cross veya rest |
| **6** | Koşuyu kısaltmak istersin; ısınma yeterli değil; merdiven ağrı yapar | ❌ | 3-5 gün koşu yok, fizyoterapist |
| **7** | Koşu sırasında yavaşlaman gerekir, ağrı devam ediyor | ❌ | Koşu bırak, fizyo görüşü |
| **8** | Yürüme zor, günlük aktivite ağrılı | ❌ | Fizyo hemen |
| **9** | Sürekli ağrı, uyku etkileniyor — yaralanma sinyali | ❌ | Doktor |
| **10** | Katlanılmaz | ❌ | Doktor |

## Context'e göre nüans (aynı skor, farklı anlam)

Aynı rakam farklı zamanda farklı ciddi:

- **Sabah kalkışta gerginlik (isınmayla geçer):** 0-3 klasik shin patrn, tolere edilir
- **Dinlenirken (rest):** 3+ ciddi — inflammation sinyali
- **Koşu sonrası (post_run):** 2+ = yük fazla gelmiş; sonraki koşuyu ayarla
  - Post-run 0-1 → koşu tolere edildi, aynı yükte devam
  - Post-run 2 → limite yakın, sonraki koşu HR daha sıkı
  - Post-run 3 → aşırı yük, sonraki koşu %30 kısalt
  - Post-run 4+ → gelecek koşu iptal, 3-5 gün recovery
- **Koşu sırasında (during_run):** herhangi bir seviye başladıktan sonra
  ARTIYORSA dur; normal ısındıktan sonra azalmalı. Artan ağrı = tehlike.

## Sohbet için ipuçları (Claude için)

Kullanıcı "biraz ağrıyor" gibi soyut anlatırsa şu netleştirici sorular:
1. **Ne zaman?** Sabah / koşu öncesi / koşu sırasında / koşu sonrası / dinlenirken?
2. **Neresi?** Sağ mı sol mu, ön kaval / arka baldır / diz / topuk / diğer?
3. **Nasıl?** Zonklama / batma / künt / gerginlik / yanma / keskin?
4. **Ne kadar?** Palpasyonda mı, hareketle mi, sürekli mi?
5. **Şu seviye tanımına yakın mı?** (Rubric'ten 2 örnek göster)

Sonunda net skor + bölge + taraf + context + kısa açıklama çıksın.

## Trend kuralları

- Post-run ağrı 2+ **arka arkaya 2 koşuda** → yük azalt
- Sabah gerginlik **7 gün üst üste 3+** → hafta yükünü %20 kes, deload öne al
- Post-run ağrı **1 puan artıyorsa haftalar arasında** → shin ilerliyor, koş azalt
- Post-run ağrı **düşüyorsa** → adaptasyon oluyor, yük az artırılabilir
