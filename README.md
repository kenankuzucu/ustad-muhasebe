# ÜSTAD MUHASEBE · Kategorİ: MUHASEBE · v1.2

**Kenan Kuzucu** tarafından yazılan, tam teşkilat **ön muhasebe programı** (PC).
Yerel çalışır · kurulum istemez · veriler kendi bilgisayarında (SQLite) durur · internete hiçbir şey gönderilmez
(asistanı kendin açarsan yalnızca soru + defter özeti Google'a gider).

> **Kategori etiketi:** `muhasebe` · **Depo:** `ustad-muhasebe` · **Kardeş proje:** `USTAD-KASA` (aynı programın şatafatlı kopyası, port 8092)

---

## Açmak

| Ne | Nasıl |
|---|---|
| PC'de aç | `BASLAT.bat` dosyasına **çift tıkla** → tarayıcı `http://127.0.0.1:8091` adresinde açılır |
| Kapatmak | Açılan siyah pencereyi **KAPATMA**; kapatırsan program durur (açık kaldığı sürece çökse bile kendini yeniden başlatır) |
| Telefondan girmek | `AG-AC.bat` → aynı WiFi'deki telefondan `http://<bilgisayar-IP>:8091` (ağ modu varsayılan **kapalı**; HTTP şifresizdir, yalnız güvendiğin ağda aç) |
| Doğrudan sunucu | `python sunucu/sunucu.py 8091` |
| Kurulum | **Yok.** `pip install` gerekmez — bütün program Python **standart kütüphanesi** ile yazıldı |

## Giriş ve roller

| Kullanıcı | Şifre | Rol | Yetki |
|---|---|---|---|
| kenan | kenan1981 | Yönetici | her şey: kayıt, silme, ayar, yedek geri alma, kullanıcı yönetimi |
| kasa | kasa2026 | Kasiyer | kasa/fatura/gelir-gider girebilir; **silemez**, ayar değiştiremez |
| misafir | misafir2026 | Misafir | yalnız okuma ve rapor |

5 hatalı girişte 60 saniye kilitlenir. Şifreler sunucuda **PBKDF2 (100.000 tur + rastgele tuz)** ile saklanır;
girişte sunucu bir **oturum jetonu** verir (`X-Oturum` başlığı) ve her yazma işlemi sunucu tarafında rol denetiminden geçer.
Yeni kullanıcı: **Ayarlar › Kullanıcılar & Roller**.

## Modüller (19 ekran)

1. **Genel Bakış** — günlük/aylık gelir, gider, net kâr, kasa toplamı, 12 aylık grafik, kategori halkası, son işlemler, uyarılar
2. **Cari Yönetimi** — kart listesi + 6 sekme: Kart Bilgileri · Hareketler · Ekstre · Faturalar · Tahsilat/Ödeme · Notlar
3. **Görüşmeler** — müşteri görüşme kaydı, sonuç, takip planı (satır başına Düzenle/Sil)
4. **Görevler & Hatırlatma** — vergi/ödeme/sayım işleri; "Tamamla" düğmesi, geciken kırmızı
5. **Harcamalar · Sade Defter** — kurumsal olmayan günlük gelir/gider; hızlı kayıt paneli, 30 günlük grafik, kategori halkası
6. **Bütçe** — kategori bazlı aylık bütçe, renk değiştiren harcama çubuğu, aşım/uyarı durumu
7. **Gelirler** / 8. **Giderler** — kurumsal defter; kayıt kasa hareketine de işlenir
9. **Kasa & Bankalar** — Hesaplar · Hareketler · Gün Sonu
10. **Faturalar** — kalemli fatura, KDV/iskonto otomatik, ödeme durumu; satış faturası **stoktan düşer**
11. **Çek & Senet** — alınan/verilen, vade takvimi, vadesi geçen uyarısı, durum takibi
12. **Tekrarlayan Kayıt & Abonelik** — kira/maaş/abonelikler her ay kendiliğinden deftere işlenir
13. **Stok Yönetimi** — miktar, kritik seviye, stok değeri
14. **Personel & Bordro** — maaş, SGK ve stopaj ön izlemesi + **Puantaj** (avans/prim/izin/fazla mesai)
15. **Muhasebe Asistanı** — kendi defterindeki gerçek sayılarla Türkçe cevap (Gemini anahtarı gerekir)
16. **Fiş & Fatura Fotoğrafları** — fotoğraf yükle, kaydet, "Deftere İşle" ile sade deftere gider yaz
17. **Raporlar** — 10 klasik + 4 **akıllı rapor**: KDV Özeti · Harcama Anomalisi · Nakit Akışı Tahmini · Yıl Sonu Karnesi
18. **Word / Excel / PDF Çıktıları** — üretilen belgeler; indir/sil
19. **Ayarlar & Yedek** — 6 sekme: Firma · Kullanıcılar & Roller · Ağ & Güvenlik · Yedekleme · Otomasyon · Denetim Kaydı

## Çıktılar

- **Word (.docx)**, **Excel (.xlsx)** ve **PDF** (Word üzerinden gerçek PDF) — her ekranın sağ üstündeki düğmelerle.
- **Mali Müşavir Paketi**: Ayarlar › Otomasyon · seçilen tarih aralığındaki tüm defterleri **CSV + KDV özeti** olarak tek ZIP'te toplar.
- Word/Excel dosyaları `python-docx` / `openpyxl` **kurulmadan** üretilir: .xlsx/.docx paketleri `zipfile` + elle XML ile yazılır.

## Temalar ve renkler

- **13 tema**: Gece · Gündüz · Altın · Lavanta · Okyanus · Orman · Gül · Neon · Kahve · Zümrüt · Kuzey · Limon · Bordo
- **6 renk paleti** (temadan bağımsız): Tatlı · Canlı · Pastel · Sıcak · Kuzey · Zümrüt
- Seçim hatırlanır. Ekran geçişlerinde kartlar süzülür, çubuklar büyür, para rakamları sayarak yerine oturur.
- Yazılar 4K/5K'da keskin kalsın diye punto ve boşluklar ekranla birlikte ölçeklenir (1920 → 1.0 · 4K → 1.5 · 5K → 1.75).

## Yedekleme

- Elle: **Ayarlar › Yedekleme › Şimdi Yedek Al** (`yedek\` klasörü), tek düğmeyle geri yükleme.
- Otomatik: günde bir kez belirlenen saatte (Ayarlar › Otomasyon).
- Denetim kaydı: kim, ne zaman, ne yaptı (Ayarlar › Denetim Kaydı).

## Klasör düzeni

```
panel\     arayüz (index.html · stil.css · uygulama.js — kütüphanesiz saf JS)
sunucu\    sunucu.py (saf stdlib http.server + SQLite) · ozellikler.py (22 ek özellik) ·
           disa_aktar.py (Word/Excel motoru) · pdf_rapor.py (Word COM → PDF) · ai_asistan.py (Gemini köprüsü)
arac\      giris.py (exe girişi) · lan_bilgi.py · paketle.py (PyInstaller tek dosya)
veri\      muhasebe.db (SQLite) · ayar.json · ai.json · fisler\      → .gitignore'da (kişisel veri, depoya girmez)
yedek\     alınan yedekler · cikti\  üretilen belgeler · build\ dist\ derleme  → .gitignore'da
```

> **Depoda olmayanlar (bilerek):** `veri\` (firma bilgisi, gerçek defter, Gemini anahtarı, fiş fotoğrafları),
> `yedek\`, `cikti\`, `build\`, `dist\` ve `.exe`. Kaynak kod temiz, kişisel veri yok.
> Program ilk açılışta `veri\` klasörünü ve boş veritabanını kendisi kurar (`cari` tablosu boşken örnek veri de üretir).

## Derleme (tek dosya .exe)

```
uv tool install pyinstaller
pyinstaller --noconfirm --clean --onefile --console --name USTAD-MUHASEBE ^
  --hidden-import sunucu --hidden-import disa_aktar --hidden-import ozellikler ^
  --hidden-import pdf_rapor --hidden-import ai_asistan ^
  --add-data "<KOK>/panel;panel" --add-data "<KOK>/sunucu;sunucu" arac/giris.py
```

`arac/paketle.py` aynı komutu üretir. Kritik nokta: `sunucu.py` · `ozellikler.py` · `ai_asistan.py` kök/veri/DB
yollarını `__file__`'dan hesaplar; onefile exe'de bunlar `_MEIPASS` (geçici klasör) olur → `arac/giris.py`
`KOK · VERI · PANEL · CIKTI · YEDEK · FISLER · DB · EK_AYAR` sabitlerini **kalıcı klasöre** yamalar, yoksa panel açılır
ama ekranlar `500` verir. Doğrulama: exe'yi başlat, `muhasebe-api-test.py <port>` çalıştır, log'daki `500` sayısı **0** olmalı.

## Dürüst sınırlar

- **OCR kapalı**: Bu bilgisayarda Tesseract kurulu değil → fiş fotoğrafındaki tutarı program okuyamaz, sen yazarsın.
- **PDF**, Word kurulu olmasını gerektirir (Word açılıp kapanır, 5-15 sn). Word yoksa PDF üretilmez, Word/Excel çalışır.
- **Asistan** yalnızca API anahtarı girilirse çalışır; anahtar yoksa program tam çalışır.
- **e-Fatura / e-Arşiv entegrasyonu yoktur** — bu bir **ön muhasebe** programıdır, beyanname yerine geçmez.
- Yerel ağ modu **HTTP**'dir (şifresiz); dışarıdan erişim için VPN kullan.
- Android (APK) sürümü **yoktur**; bu bir PC (tarayıcı arayüzlü) programıdır.

---

© 2026 **Kenan Kuzucu** · ÜSTAD SALON KENAN · Gaziantep
TÜM HAKLARI SAKLIDIR · 5846 sayılı FSEK kapsamında korunur.
