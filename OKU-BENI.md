# ÜSTAD MUHASEBE · Tam Teşkilat Muhasebe Programı · v1.2

Yerel çalışır · kurulum istemez · veriler kendi bilgisayarında (SQLite) durur · internete hiçbir şey gönderilmez
(asistanı kendin açarsan yalnızca soru + defter özeti Google'a gider).

## Açmak
`BASLAT.bat` dosyasına **çift tıkla**. Tarayıcı `http://127.0.0.1:8091` adresinde açılır.
Açılan siyah pencereyi KAPATMA — kapatırsan program durur (açık kalırsa çökse bile kendi kendini yeniden başlatır).

Telefondan girmek için: `AG-AC.bat` (aynı WiFi'deki telefon/tablet tarayıcısından `http://<bilgisayar-IP>:8091`).
Ağ modu varsayılan olarak **kapalıdır**; trafik şifresiz (HTTP) olduğu için yalnız güvendiğin ağda aç.

## Giriş ve roller
| Kullanıcı | Şifre | Rol | Yetki |
|---|---|---|---|
| kenan | kenan1981 | Yönetici | her şey: kayıt, silme, ayar, yedek geri alma, kullanıcı yönetimi |
| kasa | kasa2026 | Kasiyer | kasa/fatura/gelir-gider girebilir; **silemez**, ayar değiştiremez |
| misafir | misafir2026 | Misafir | yalnız okuma ve rapor |

5 hatalı girişte 60 saniye kilitlenir. Şifreler sunucuda **PBKDF2 (100.000 tur + rastgele tuz)** ile saklanır;
girişte sunucu bir **oturum jetonu** verir ve her yazma işlemi rol denetiminden geçer.
Yeni kullanıcı eklemek: **Ayarlar › Kullanıcılar & Roller**.

## Modüller (19 ekran)
1. **Genel Bakış** — günlük/aylık gelir, gider, net kâr, kasa toplamı, 12 aylık grafik, kategori halkası, son işlemler, uyarılar
2. **Cari Yönetimi** — kart listesi + 6 sekme: Kart Bilgileri · Hareketler · Ekstre · Faturalar · Tahsilat/Ödeme · Notlar
3. **Görüşmeler** — müşteri görüşme kaydı, sonuç, takip planı (düzenle/sil)
4. **Görevler & Hatırlatma** — vergi/ödeme/sayım işleri; “Tamamla” düğmesi, geciken kırmızı
5. **Harcamalar · Sade Defter** — kurumsal olmayan günlük gelir/gider; hızlı kayıt paneli, 30 günlük grafik,
   kategori halkası, filtre ve her satırda Düzenle/Sil
6. **Bütçe** — kategori bazlı aylık bütçe, renk değiştiren harcama çubuğu, aşım/uyarı durumu
7. **Gelirler / 8. Giderler** — kurumsal defter; kayıt kasa hareketine de işlenir (düzenle/sil)
9. **Kasa & Bankalar** — Hesaplar · Hareketler · Gün Sonu sekmeleri
10. **Faturalar** — kalemli fatura, KDV/iskonto otomatik, ödeme durumu; satış faturası **stoktan düşer**
11. **Çek & Senet** — alınan/verilen, vade takvimi, vadesi geçen uyarısı, durum takibi (düzenle/sil)
12. **Tekrarlayan Kayıt & Abonelik** — kira/maaş/abonelikler her ay kendiliğinden deftere işlenir
13. **Stok Yönetimi** — miktar, kritik seviye, stok değeri
14. **Personel & Bordro** — maaş, SGK ve stopaj ön izlemesi + **Puantaj** (avans/prim/izin/fazla mesai)
15. **Muhasebe Asistanı** — kendi defterindeki gerçek sayılarla Türkçe cevap (Gemini anahtarı gerekir)
16. **Fiş & Fatura Fotoğrafları** — fotoğraf yükle, kaydet, “Deftere İşle” ile sade deftere gider yaz
17. **Raporlar** — 10 klasik rapor + 4 **akıllı rapor**: KDV Özeti · Harcama Anomalisi · Nakit Akışı Tahmini · Yıl Sonu Karnesi
18. **Word / Excel / PDF Çıktıları** — üretilen belgeler; indir/sil
19. **Ayarlar & Yedek** — 6 sekme: Firma Bilgisi · Kullanıcılar & Roller · Ağ & Güvenlik · Yedekleme · Otomasyon · Denetim Kaydı

## Çıktılar
- **Word (.docx)**, **Excel (.xlsx)** ve **PDF** (Word üzerinden gerçek PDF) — her ekranın sağ üstündeki
  Word / Excel / PDF düğmeleri ve her listenin altındaki düğmelerle.
- **Mali Müşavir Paketi**: Ayarlar › Otomasyon · seçilen tarih aralığındaki tüm defterleri
  **CSV + KDV özeti metni** olarak tek ZIP'te toplar.
- Word/Excel dosyaları `python-docx` / `openpyxl` **kurulmadan** üretilir (paketler standart kütüphaneyle elle yazılır). `pip install` gerekmez.

## Temalar ve renkler
- **13 tema**: Gece · Gündüz · Altın · Lavanta · Okyanus · Orman · Gül · Neon · Kahve · Zümrüt · Kuzey · Limon · Bordo
- **6 renk paleti** (temadan bağımsız): Tatlı · Canlı · Pastel · Sıcak · Kuzey · Zümrüt
- Sağ üstteki renk topları veya **Ayarlar › Firma Bilgisi › Görünüm** kartlarından seçilir; seçim hatırlanır.
- Ekran geçişlerinde kartlar süzülür, çubuklar büyür, para rakamları sayarak yerine oturur.
- Yazılar 4K/5K'da keskin kalsın diye punto ve boşluklar ekranla birlikte ölçeklenir (1920 → 1.0 · 4K → 1.5 · 5K → 1.75).

## Yedekleme
- Elle: **Ayarlar › Yedekleme › Şimdi Yedek Al** (`yedek\` klasörü), tek düğmeyle geri yükleme.
- Otomatik: günde bir kez belirlenen saatte (Ayarlar › Otomasyon).
- Denetim kaydı: kim, ne zaman, ne yaptı (Ayarlar › Denetim Kaydı).

## Klasörler
```
panel\     arayüz (index.html · stil.css · uygulama.js)
sunucu\    sunucu.py (saf Python + SQLite) · ozellikler.py (22 ek özellik) ·
           disa_aktar.py (Word/Excel motoru) · pdf_rapor.py (Word→PDF) · ai_asistan.py (Gemini köprüsü)
arac\      giris.py · lan_bilgi.py · paketle.py
veri\      muhasebe.db (SQLite) · ayar.json · ai.json (varsa) · fisler\
yedek\     alınan yedekler
cikti\     üretilen Word/Excel/PDF dosyaları
```

## Dürüst sınırlar
- **OCR kapalı**: Bu bilgisayarda Tesseract kurulu değil, bu yüzden fiş fotoğrafındaki tutarı program okuyamaz — sen yazarsın.
  (Tesseract kurulursa program onu otomatik görüp kullanır.)
- **PDF**, Word kurulu olmasını gerektirir (Word açılıp kapanır, 5-15 saniye sürer). Word yoksa PDF üretilmez, Word/Excel çalışır.
- **Asistan** yalnızca API anahtarı girilirse çalışır; anahtar yoksa program tam çalışır.
- **e-Fatura / e-Arşiv entegrasyonu yoktur**; bu bir ön muhasebe programıdır, beyanname yerine geçmez.
- Yerel ağ modu **HTTP**'dir (şifresiz); dışarıdan erişim için VPN kullan.
