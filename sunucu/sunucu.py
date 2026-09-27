# -*- coding: utf-8 -*-
"""
ÜSTAD MUHASEBE · yerel sunucu (saf Python standart kütüphanesi)
Çalıştır:  python sunucu/sunucu.py 8091
Panel:     http://127.0.0.1:8091
"""
import json
import os
import re
import shutil
import sqlite3
import sys
import datetime
import http.server
import socketserver
import threading
import urllib.parse

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(KOK, "veri")
PANEL = os.path.join(KOK, "panel")
CIKTI = os.path.join(KOK, "cikti")
YEDEK = os.path.join(KOK, "yedek")
DB = os.path.join(VERI, "muhasebe.db")
AYAR_DOSYA = os.path.join(VERI, "ayar.json")
SURUM = "1.2.0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import disa_aktar  # noqa: E402
import ozellikler  # noqa: E402

for k in (VERI, CIKTI, YEDEK):
    os.makedirs(k, exist_ok=True)

AYAR_VARSAYILAN = {
    "firma": "ÜSTAD SALON KENAN",
    "vergi_dairesi": "Şehitkamil",
    "vergi_no": "1234567890",
    "adres": "Selimiye Mah. Şehitkamil / Gaziantep",
    "telefon": "0546 499 17 53",
    "email": "kenankuzucu@ustadcyber.com.tr",
    "para": "TRY",
    "kdv": 20,
    "tema": "gece",
    "kullanici": "kenan",
    "sifre_hash": "",   # ilk açılışta kilit.js tarafında SHA-256 ile kurulur
    "sunucu_port": 8091,
}

TABLOLAR = ["cari", "hareket", "hesap", "kasa_hareket", "fatura", "fatura_kalem",
            "stok", "personel", "gorusme", "gelir_gider", "log",
            "tekrar", "butce", "cek", "puantaj", "fis", "gorev"]


# --------------------------------------------------------------- veritabanı
def baglan():
    v = sqlite3.connect(DB, timeout=15)
    v.row_factory = sqlite3.Row
    v.execute("PRAGMA journal_mode=WAL")
    return v


KURULUM = """
CREATE TABLE IF NOT EXISTS cari(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kod TEXT, unvan TEXT NOT NULL, tip TEXT DEFAULT 'Müşteri',
  vergi_dairesi TEXT, vergi_no TEXT, yetkili TEXT, telefon TEXT, email TEXT,
  il TEXT, ilce TEXT, adres TEXT, acilis_bakiye REAL DEFAULT 0,
  risk_limiti REAL DEFAULT 0, notlar TEXT, aktif INTEGER DEFAULT 1,
  olusturma TEXT);
CREATE TABLE IF NOT EXISTS hareket(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cari_id INTEGER, tarih TEXT, evrak_no TEXT, aciklama TEXT,
  borc REAL DEFAULT 0, alacak REAL DEFAULT 0,
  kaynak TEXT DEFAULT 'elle', hesap_id INTEGER, olusturma TEXT);
CREATE TABLE IF NOT EXISTS hesap(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad TEXT NOT NULL, tur TEXT DEFAULT 'Kasa', banka TEXT, iban TEXT, sube TEXT,
  acilis REAL DEFAULT 0, aktif INTEGER DEFAULT 1, olusturma TEXT);
CREATE TABLE IF NOT EXISTS kasa_hareket(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hesap_id INTEGER, tarih TEXT, tur TEXT, tutar REAL DEFAULT 0,
  aciklama TEXT, kategori TEXT, cari_id INTEGER, evrak_no TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS fatura(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  no TEXT, tur TEXT DEFAULT 'Satış', cari_id INTEGER, tarih TEXT, vade TEXT,
  aciklama TEXT, ara_toplam REAL DEFAULT 0, iskonto REAL DEFAULT 0,
  kdv REAL DEFAULT 0, toplam REAL DEFAULT 0, durum TEXT DEFAULT 'Bekliyor',
  tahsil REAL DEFAULT 0, olusturma TEXT);
CREATE TABLE IF NOT EXISTS fatura_kalem(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fatura_id INTEGER, aciklama TEXT, miktar REAL DEFAULT 1, birim TEXT DEFAULT 'Adet',
  birim_fiyat REAL DEFAULT 0, kdv_orani REAL DEFAULT 20, tutar REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS stok(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kod TEXT, ad TEXT NOT NULL, birim TEXT DEFAULT 'Adet', miktar REAL DEFAULT 0,
  alis REAL DEFAULT 0, satis REAL DEFAULT 0, kdv REAL DEFAULT 20,
  kritik REAL DEFAULT 5, kategori TEXT, aktif INTEGER DEFAULT 1, olusturma TEXT);
CREATE TABLE IF NOT EXISTS personel(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad TEXT NOT NULL, gorev TEXT, telefon TEXT, email TEXT, maas REAL DEFAULT 0,
  giris_tarihi TEXT, durum TEXT DEFAULT 'Aktif', notlar TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS gorusme(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cari_id INTEGER, tarih TEXT, saat TEXT, konu TEXT, sonuc TEXT,
  takip TEXT, durum TEXT DEFAULT 'Planlandı', notlar TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS gelir_gider(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarih TEXT, tur TEXT, kategori TEXT, aciklama TEXT, tutar REAL DEFAULT 0,
  hesap_id INTEGER, cari_id INTEGER, evrak_no TEXT, tekrarlayan TEXT,
  defter TEXT DEFAULT 'kurumsal', olusturma TEXT);
CREATE TABLE IF NOT EXISTS log(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  zaman TEXT, kullanici TEXT, islem TEXT, detay TEXT);
"""


def kur(v):
    v.executescript(KURULUM)
    # --- küçük göçler: eski veritabanlarına sonradan eklenen sütunlar
    sutunlar = [r["name"] for r in v.execute("PRAGMA table_info(gelir_gider)").fetchall()]
    if "defter" not in sutunlar:
        v.execute("ALTER TABLE gelir_gider ADD COLUMN defter TEXT DEFAULT 'kurumsal'")
    # --- ek modülün tabloları (tekrar · bütçe · çek/senet · puantaj · fiş · görev · kullanıcı)
    ozellikler.kur_ek(v)
    ozellikler.kullanici_kur(v)
    v.commit()


def bugun():
    return datetime.date.today().isoformat()


def simdi():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def yaz_log(v, islem, detay=""):
    v.execute("INSERT INTO log(zaman,kullanici,islem,detay) VALUES(?,?,?,?)",
              (simdi(), AYAR.get("kullanici", "kenan"), islem, detay))


# --------------------------------------------------------------- örnek veri
def ornek_veri(v):
    if v.execute("SELECT COUNT(*) c FROM cari").fetchone()["c"]:
        return
    bug = datetime.date.today()
    yil = bug.year

    cariler = [
        ("C-001", "Yalçın Kuzucu", "Müşteri", "Şehitkamil", "1111111111", "Yalçın Bey", "0532 111 22 33", "yalcin@ornek.com", "Gaziantep", "Şehitkamil", "Selimiye Mah. No:12", 15000, 50000),
        ("C-002", "Gülşah Demir", "Tedarikçi", "Şahinbey", "2222222222", "Gülşah Hanım", "0533 222 33 44", "gulsah@ornek.com", "Gaziantep", "Şahinbey", "Atatürk Bul. No:44", 0, 25000),
        ("C-003", "Mehmet Aksoy", "Müşteri", "Şehitkamil", "3333333333", "Mehmet Bey", "0534 333 44 55", "mehmet@ornek.com", "Gaziantep", "Şehitkamil", "Karataş Mah. No:7", 8500, 20000),
        ("C-004", "Zeynep Kaya", "Müşteri", "Şahinbey", "4444444444", "Zeynep Hanım", "0535 444 55 66", "zeynep@ornek.com", "Gaziantep", "Şahinbey", "Değirmiçem No:19", 4200, 15000),
        ("C-005", "Antalya Divan Kuaför Malz.", "Tedarikçi", "Muratpaşa", "5555555555", "Satış Bölümü", "0242 555 66 77", "satis@divan.com", "Antalya", "Muratpaşa", "Lara Cad. No:101", 0, 60000),
        ("C-006", "Ahmet Yılmaz", "Müşteri", "Şehitkamil", "6666666666", "Ahmet Bey", "0536 666 77 88", "ahmet@ornek.com", "Gaziantep", "Şehitkamil", "Binevler No:3", 2600, 10000),
        ("C-007", "Elif Şahin", "Müşteri", "Şahinbey", "7777777777", "Elif Hanım", "0537 777 88 99", "elif@ornek.com", "Gaziantep", "Şahinbey", "Güneykent No:8", 0, 8000),
        ("C-008", "Mustafa Doğan", "Müşteri", "Şehitkamil", "8888888888", "Mustafa Bey", "0538 888 99 00", "mustafa@ornek.com", "Gaziantep", "Şehitkamil", "İbrahimli No:21", 11400, 30000),
        ("C-009", "Gaziantep Berber Odası", "Kurum", "Şehitkamil", "9999999999", "Oda Sekreterliği", "0342 999 00 11", "info@gbo.org.tr", "Gaziantep", "Şehitkamil", "Cumhuriyet Meydanı", 0, 5000),
        ("C-010", "Fatma Öztürk", "Müşteri", "Nizip", "1010101010", "Fatma Hanım", "0539 101 20 30", "fatma@ornek.com", "Gaziantep", "Nizip", "Nizip Merkez No:5", 3300, 9000),
        ("C-011", "Burak Şen", "Müşteri", "Şehitkamil", "1212121212", "Burak Bey", "0541 121 31 41", "burak@ornek.com", "Gaziantep", "Şehitkamil", "Karataş No:55", 0, 12000),
        ("C-012", "Kuzey Kozmetik Ltd.", "Tedarikçi", "Konak", "1313131313", "Bayi Hattı", "0232 131 41 51", "bayi@kuzey.com", "İzmir", "Konak", "Alsancak No:9", 0, 40000),
    ]
    for c in cariler:
        v.execute("""INSERT INTO cari(kod,unvan,tip,vergi_dairesi,vergi_no,yetkili,telefon,email,il,ilce,adres,
                     acilis_bakiye,risk_limiti,aktif,olusturma)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1,?)""", c + (simdi(),))

    hesaplar = [
        ("Merkez Kasa", "Kasa", "", "", "", 5000),
        ("Ziraat Bankası · 1234", "Banka", "Ziraat Bankası", "TR12 0001 0002 0003 0004 0005 01", "Şehitkamil", 42500),
        ("Garanti BBVA · 5678", "Banka", "Garanti BBVA", "TR34 0006 2000 5678 0000 1234 56", "Şehitkamil", 18600),
        ("İş Bankası · 9012", "Banka", "İş Bankası", "TR56 0006 4000 9012 0000 7890 12", "Şahinbey", 27300),
    ]
    for h in hesaplar:
        v.execute("""INSERT INTO hesap(ad,tur,banka,iban,sube,acilis,aktif,olusturma)
                     VALUES(?,?,?,?,?,?,1,?)""", h + (simdi(),))

    kategoriler_gelir = ["Kuaför Hizmet", "Ürün Satışı", "Bakım & Boya", "Gelin Paketi", "Diğer Gelir"]
    kategoriler_gider = ["Personel", "Kira", "Elektrik & Su", "Malzeme Alımı", "Vergi & Harç", "Reklam", "İnternet & Telefon", "Diğer Gider"]
    cariler_id = [r["id"] for r in v.execute("SELECT id FROM cari ORDER BY id").fetchall()]
    hesap_id = [r["id"] for r in v.execute("SELECT id FROM hesap ORDER BY id").fetchall()]

    # 12 aylık gelir/gider örnek akışı
    for ay_geri in range(11, -1, -1):
        ay_ilk = (bug.replace(day=1) - datetime.timedelta(days=ay_geri * 30)).replace(day=1)
        for gun in (3, 9, 17, 24, 27):
            tarih = (ay_ilk + datetime.timedelta(days=gun - 1)).isoformat()
            if tarih > bug.isoformat():
                continue
            tutar = round(6200 + ((gun * 137 + ay_geri * 911) % 5200) + ay_geri * 120, 2)
            kat = kategoriler_gelir[(gun + ay_geri) % len(kategoriler_gelir)]
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,hesap_id,cari_id,evrak_no,tekrarlayan,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?,?)""",
                      (tarih, "gelir", kat, "%s · %s" % (kat, tarih[5:7] + "/" + tarih[8:10]), tutar,
                       hesap_id[(gun + ay_geri) % len(hesap_id)], cariler_id[(gun + ay_geri) % len(cariler_id)],
                       "GG-%s-%03d" % (yil, 100 + (ay_geri * 10 + gun)), "", simdi()))
            v.execute("""INSERT INTO kasa_hareket(hesap_id,tarih,tur,tutar,aciklama,kategori,cari_id,evrak_no,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (hesap_id[(gun + ay_geri) % len(hesap_id)], tarih, "giriş", tutar,
                       "%s tahsilatı" % kat, kat, cariler_id[(gun + ay_geri) % len(cariler_id)],
                       "KSA-%s-%03d" % (yil, 100 + (ay_geri * 10 + gun)), simdi()))
            gider = round(1800 + ((gun * 89 + ay_geri * 601) % 3600), 2)
            gkat = kategoriler_gider[(gun + ay_geri) % len(kategoriler_gider)]
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,hesap_id,cari_id,evrak_no,tekrarlayan,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?,?)""",
                      (tarih, "gider", gkat, "%s ödemesi" % gkat, gider,
                       hesap_id[(gun * 3 + ay_geri) % len(hesap_id)], None,
                       "GG-%s-%03d" % (yil, 500 + (ay_geri * 10 + gun)), "", simdi()))
            v.execute("""INSERT INTO kasa_hareket(hesap_id,tarih,tur,tutar,aciklama,kategori,cari_id,evrak_no,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (hesap_id[(gun * 3 + ay_geri) % len(hesap_id)], tarih, "çıkış", gider,
                       "%s ödemesi" % gkat, gkat, None,
                       "KSA-%s-%03d" % (yil, 500 + (ay_geri * 10 + gun)), simdi()))

    # cari hareketleri
    for i, cid in enumerate(cariler_id):
        for j in range(3):
            tarih = (bug - datetime.timedelta(days=(i * 3 + j * 11) % 90)).isoformat()
            borc = round(1500 + ((i * 7 + j * 13) % 9) * 950, 2)
            v.execute("""INSERT INTO hareket(cari_id,tarih,evrak_no,aciklama,borc,alacak,kaynak,hesap_id,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (cid, tarih, "HR-%04d" % (1000 + i * 10 + j), "Hizmet / ürün bedeli", borc, 0, "elle",
                       hesap_id[i % len(hesap_id)], simdi()))
            if j % 2 == 0:
                v.execute("""INSERT INTO hareket(cari_id,tarih,evrak_no,aciklama,borc,alacak,kaynak,hesap_id,olusturma)
                             VALUES(?,?,?,?,?,?,?,?,?)""",
                          (cid, tarih, "TH-%04d" % (2000 + i * 10 + j), "Tahsilat", 0, round(borc * 0.6, 2),
                           "kasa", hesap_id[i % len(hesap_id)], simdi()))

    # faturalar
    for i in range(8):
        cid = cariler_id[i % len(cariler_id)]
        tarih = (bug - datetime.timedelta(days=i * 6)).isoformat()
        vade = (bug + datetime.timedelta(days=15 - i * 3)).isoformat()
        adet = 2 + (i % 3)
        birim = round(850 + i * 120, 2)
        ara = round(adet * birim, 2)
        kdv = round(ara * 0.20, 2)
        toplam = round(ara + kdv, 2)
        durum = ["Ödendi", "Bekliyor", "Kısmi", "Bekliyor"][i % 4]
        tahsil = toplam if durum == "Ödendi" else (round(toplam * 0.4, 2) if durum == "Kısmi" else 0)
        cur = v.execute("""INSERT INTO fatura(no,tur,cari_id,tarih,vade,aciklama,ara_toplam,iskonto,kdv,toplam,durum,tahsil,olusturma)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        ("FTR-%s-%04d" % (yil, 200 + i), "Satış" if i % 3 else "Alış", cid, tarih, vade,
                         "Kuaför hizmet ve ürün bedeli", ara, 0, kdv, toplam, durum, tahsil, simdi()))
        fid = cur.lastrowid
        for k in range(adet):
            v.execute("""INSERT INTO fatura_kalem(fatura_id,aciklama,miktar,birim,birim_fiyat,kdv_orani,tutar)
                         VALUES(?,?,?,?,?,?,?)""",
                      (fid, "Hizmet kalemi %d" % (k + 1), 1, "Adet", birim, 20, birim))

    # stok
    stoklar = [
        ("ST-001", "Saç Boyası (Siyah)", "Adet", 42, 180, 320, 20, 10, "Boya"),
        ("ST-002", "Saç Boyası (Kahve)", "Adet", 7, 180, 320, 20, 10, "Boya"),
        ("ST-003", "Şampuan 5 Lt", "Litre", 18, 240, 420, 20, 6, "Bakım"),
        ("ST-004", "Saç Kremi 1 Lt", "Adet", 24, 95, 180, 20, 8, "Bakım"),
        ("ST-005", "Tıraş Köpüğü", "Adet", 3, 60, 120, 20, 12, "Tıraş"),
        ("ST-006", "Jilet (100'lü)", "Paket", 15, 210, 350, 20, 5, "Tıraş"),
        ("ST-007", "Havlu (Koli)", "Koli", 9, 640, 980, 20, 4, "Sarf"),
        ("ST-008", "Kesim Makinesi Yağı", "Adet", 21, 45, 90, 20, 6, "Malzeme"),
        ("ST-009", "Ağda Bandı", "Rulo", 30, 55, 110, 20, 10, "Bakım"),
        ("ST-010", "Kolonya 1 Lt", "Adet", 12, 70, 140, 20, 8, "Sarf"),
    ]
    for s in stoklar:
        v.execute("""INSERT INTO stok(kod,ad,birim,miktar,alis,satis,kdv,kritik,kategori,aktif,olusturma)
                     VALUES(?,?,?,?,?,?,?,?,?,1,?)""", s + (simdi(),))

    personeller = [
        ("Ahmet Yılmaz", "Usta Kuaför", "0532 111 22 33", "ahmet@ustad.com", 32000, "2024-03-01", "Aktif", "on numara tıraş"),
        ("Zeynep Kaya", "Bayan Kuaför", "0533 222 33 44", "zeynep@ustad.com", 28500, "2024-07-15", "Aktif", "boya uzmanı"),
        ("Mehmet Aksoy", "Çırak", "0534 333 44 55", "mehmet@ustad.com", 17002, "2025-01-10", "Aktif", "öğrenci"),
        ("Elif Şahin", "Manikür & Pedikür", "0535 444 55 66", "elif@ustad.com", 24000, "2025-05-02", "Aktif", ""),
        ("Mustafa Doğan", "Kasa & Muhasebe", "0536 555 66 77", "mustafa@ustad.com", 30000, "2023-11-20", "Aktif", "muhasebe takibi"),
        ("Burak Şen", "Temizlik", "0537 666 77 88", "burak@ustad.com", 17002, "2026-02-01", "Aktif", ""),
    ]
    for p in personeller:
        v.execute("""INSERT INTO personel(ad,gorev,telefon,email,maas,giris_tarihi,durum,notlar,olusturma)
                     VALUES(?,?,?,?,?,?,?,?,?)""", p + (simdi(),))

    gorusmeler = [
        (0, "Gelin paketi fiyat teklifi", "Sonuçlandı", "Sözleşme imzalandı"),
        (1, "Boyа malzeme tedarik görüşmesi", "Sonuçlandı", "Yeni sipariş planlandı"),
        (2, "Aylık bakım anlaşması", "Planlandı", "Cuma tekrar aranacak"),
        (3, "Düğün organizasyonu", "Bekliyor", "Fiyat onayı bekleniyor"),
        (4, "Toptan alım indirimi", "Sonuçlandı", "%8 indirim alındı"),
        (5, "Kuaför odası aidat", "Planlandı", "Ödeme hatırlatılacak"),
    ]
    for i, (ci, konu, sonuc, takip) in enumerate(gorusmeler):
        tarih = (bug - datetime.timedelta(days=i * 4)).isoformat()
        v.execute("""INSERT INTO gorusme(cari_id,tarih,saat,konu,sonuc,takip,durum,notlar,olusturma)
                     VALUES(?,?,?,?,?,?,?,?,?)""",
                  (cariler_id[ci % len(cariler_id)], tarih, "%02d:30" % (9 + (i % 8)), konu, sonuc, takip,
                   "Tamamlandı" if sonuc == "Sonuçlandı" else "Devam ediyor", "", simdi()))
    v.commit()


def ornek_harcama(v):
    """Sade harcama defteri (kurumsal olmayan, kişisel gider/gelir). Kasaya dokunmaz (hesap_id NULL)."""
    if v.execute("SELECT COUNT(*) c FROM gelir_gider WHERE defter='sade'").fetchone()["c"]:
        return
    bug = datetime.date.today()
    gider_kat = [("Market", 450, 1400), ("Yemek & Kafe", 120, 600), ("Yakıt", 600, 1400),
                 ("Elektrik & Su", 400, 1100), ("İnternet & Telefon", 300, 700),
                 ("Kıyafet", 250, 900), ("Sağlık", 200, 900), ("Eğitim", 300, 900),
                 ("Kuaför & Bakım", 150, 600), ("Çocuk", 200, 700), ("Diğer", 100, 600)]
    gelir_kat = [("Maaş", 22000, 22000), ("Ek İş", 4000, 12000), ("Kira Geliri", 8000, 8000),
                 ("Satış", 2000, 6000), ("Diğer Gelir", 1000, 4000)]
    aciklamalar = {
        "Market": ["Haftalık market", "Meyve sebze", "Temizlik malzemesi", "Kırmızı et"],
        "Yemek & Kafe": ["Öğle yemeği", "Kahve", "Pide", "Lokanta"],
        "Yakıt": ["Benzin", "Motorin", "Otogaz"],
        "Kira": ["Aylık kira ödemesi"],
        "Elektrik & Su": ["Elektrik faturası", "Su faturası", "Doğalgaz"],
        "İnternet & Telefon": ["İnternet aboneliği", "Cep telefonu faturası"],
        "Kıyafet": ["Gömlek", "Ayakkabı", "Mont"],
        "Sağlık": ["Eczane", "Doktor muayenesi", "Diş"],
        "Eğitim": ["Kitap", "Kurs ücreti", "Kırtasiye"],
        "Kuaför & Bakım": ["Saç kesimi", "Bakım ürünü"],
        "Çocuk": ["Oyuncak", "Okul harçlığı"],
        "Diğer": ["Küçük harcama", "Hediye"],
    }
    for gun_geri in range(44, -1, -1):
        tarih = (bug - datetime.timedelta(days=gun_geri)).isoformat()
        # her gün 1-2 harcama
        for j in range(1 + (gun_geri % 2)):
            kat, alt, ust = gider_kat[(gun_geri * 3 + j * 5) % len(gider_kat)]
            tutar = round(alt + ((gun_geri * 137 + j * 311) % max(1, ust - alt + 1)), 2)
            ac = aciklamalar.get(kat, ["Harcama"])
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,defter,olusturma)
                         VALUES(?,?,?,?,?,?,?)""",
                      (tarih, "gider", kat, "%s · %s" % (ac[(gun_geri + j) % len(ac)], tarih[8:10] + "." + tarih[5:7]),
                       tutar, "sade", simdi()))
        # aylık kira
        if gun_geri % 30 == 0:
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,defter,olusturma)
                         VALUES(?,?,?,?,?,?,?)""",
                      (tarih, "gider", "Kira", "Aylık kira ödemesi · " + tarih[5:7], 12000.0, "sade", simdi()))
        # 5 günde bir gelir; 30 günde bir maaş
        if gun_geri % 5 == 0:
            if gun_geri % 30 == 0:
                kat, alt, ust = gelir_kat[0]
            else:
                kat, alt, ust = gelir_kat[1 + ((gun_geri // 5) % (len(gelir_kat) - 1))]
            tutar = round(alt + ((gun_geri * 97) % max(1, ust - alt + 1)), 2)
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,defter,olusturma)
                         VALUES(?,?,?,?,?,?,?)""",
                      (tarih, "gelir", kat, "%s geliri · %s" % (kat, tarih[8:10] + "." + tarih[5:7]),
                       tutar, "sade", simdi()))
    v.commit()


# --------------------------------------------------------------- hesaplamalar
def cari_bakiye(v, cari_id):
    r = v.execute("""SELECT COALESCE(SUM(borc),0) b, COALESCE(SUM(alacak),0) a
                     FROM hareket WHERE cari_id=?""", (cari_id,)).fetchone()
    ac = v.execute("SELECT COALESCE(acilis_bakiye,0) x FROM cari WHERE id=?", (cari_id,)).fetchone()
    return round((ac["x"] if ac else 0) + r["b"] - r["a"], 2)


def hesap_bakiye(v, hesap_id):
    a = v.execute("SELECT COALESCE(acilis,0) x FROM hesap WHERE id=?", (hesap_id,)).fetchone()
    g = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM kasa_hareket WHERE hesap_id=? AND tur='giriş'",
                  (hesap_id,)).fetchone()["t"]
    c = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM kasa_hareket WHERE hesap_id=? AND tur='çıkış'",
                  (hesap_id,)).fetchone()["t"]
    g2 = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM kasa_hareket WHERE hesap_id=? AND tur='giris'",
                   (hesap_id,)).fetchone()["t"]
    c2 = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM kasa_hareket WHERE hesap_id=? AND tur='cikis'",
                   (hesap_id,)).fetchone()["t"]
    return round((a["x"] if a else 0) + g + g2 - c - c2, 2)


def ozet(v):
    bug = bugun()
    ay_basi = bug[:8] + "01"
    g1 = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gelir' AND tarih=?",
                   (bug,)).fetchone()["t"]
    d1 = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gider' AND tarih=?",
                   (bug,)).fetchone()["t"]
    ga = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gelir' AND tarih>=?",
                   (ay_basi,)).fetchone()["t"]
    da = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gider' AND tarih>=?",
                   (ay_basi,)).fetchone()["t"]
    kasa = sum(hesap_bakiye(v, r["id"]) for r in v.execute("SELECT id FROM hesap").fetchall())
    bekleyen = v.execute("""SELECT COUNT(*) c, COALESCE(SUM(toplam-tahsil),0) t FROM fatura
                            WHERE durum IN ('Bekliyor','Kısmi')""").fetchone()
    vadesi_gecen = v.execute("""SELECT COUNT(*) c, COALESCE(SUM(toplam-tahsil),0) t FROM fatura
                                WHERE durum IN ('Bekliyor','Kısmi') AND vade < ?""", (bug,)).fetchone()
    alacak = 0.0
    borc = 0.0
    for r in v.execute("SELECT id FROM cari").fetchall():
        b = cari_bakiye(v, r["id"])
        if b > 0:
            alacak += b
        else:
            borc += -b

    seri = []
    for ay_geri in range(11, -1, -1):
        bas = (datetime.date.today().replace(day=1) - datetime.timedelta(days=ay_geri * 30)).replace(day=1)
        son = (bas + datetime.timedelta(days=31)).replace(day=1)
        g = v.execute("""SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider
                         WHERE tur='gelir' AND tarih>=? AND tarih<?""", (bas.isoformat(), son.isoformat())).fetchone()["t"]
        d = v.execute("""SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider
                         WHERE tur='gider' AND tarih>=? AND tarih<?""", (bas.isoformat(), son.isoformat())).fetchone()["t"]
        seri.append({"ay": bas.strftime("%b"), "gelir": round(g, 2), "gider": round(d, 2), "kar": round(g - d, 2)})

    kat = v.execute("""SELECT kategori, SUM(tutar) t FROM gelir_gider WHERE tur='gelir'
                       GROUP BY kategori ORDER BY t DESC LIMIT 8""").fetchall()
    son = v.execute("""SELECT h.tarih, c.unvan, h.aciklama, h.borc, h.alacak
                       FROM hareket h LEFT JOIN cari c ON c.id=h.cari_id
                       ORDER BY h.tarih DESC, h.id DESC LIMIT 10""").fetchall()
    en_borclu = []
    for r in v.execute("SELECT id, unvan FROM cari").fetchall():
        b = cari_bakiye(v, r["id"])
        if b > 0:
            en_borclu.append({"unvan": r["unvan"], "bakiye": b})
    en_borclu.sort(key=lambda x: -x["bakiye"])
    return {
        "gunluk_gelir": round(g1, 2), "gunluk_gider": round(d1, 2),
        "aylik_gelir": round(ga, 2), "aylik_gider": round(da, 2),
        "net_kar": round(ga - da, 2), "kasa_toplam": round(kasa, 2),
        "bekleyen_fatura_adet": bekleyen["c"], "bekleyen_fatura_tutar": round(bekleyen["t"], 2),
        "vadesi_gecen_adet": vadesi_gecen["c"], "vadesi_gecen_tutar": round(vadesi_gecen["t"], 2),
        "toplam_alacak": round(alacak, 2), "toplam_borc": round(borc, 2),
        "seri": seri, "kategoriler": [{"ad": r["kategori"], "tutar": round(r["t"], 2)} for r in kat],
        "son_islemler": [dict(r) for r in son], "en_borclu": en_borclu[:5],
        "cari_adet": v.execute("SELECT COUNT(*) c FROM cari").fetchone()["c"],
        "fatura_adet": v.execute("SELECT COUNT(*) c FROM fatura").fetchone()["c"],
        "kritik_stok": v.execute("SELECT COUNT(*) c FROM stok WHERE miktar<=kritik").fetchone()["c"],
        "personel_adet": v.execute("SELECT COUNT(*) c FROM personel WHERE durum='Aktif'").fetchone()["c"],
    }


# --------------------------------------------------------------- API
def j(o):
    return json.dumps(o, ensure_ascii=False).encode("utf-8")


class Isleyici(http.server.SimpleHTTPRequestHandler):
    # HTTP/1.1 + Content-Length: tarayıcı bağlantıyı canlı tutar, sayfa başına
    # düzinelerce yeni bağlantı açılmaz (antivirüs/proxy'li makinelerde "Failed to fetch" olmaz).
    protocol_version = "HTTP/1.1"
    server_version = "UstadMuhasebe/1.2"
    def log_message(self, fmt, *args):
        pass

    def handle(self):
        # Tarayıcı sekmesi kapanınca/keep-alive kesilince soket hataları normaldir;
        # bunları konsola yığın izi (traceback) olarak basma — pencere temiz kalsın.
        try:
            super().handle()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    # ---------------------------------------------------------- yardımcılar
    def govde(self):
        uzun = int(self.headers.get("Content-Length") or 0)
        if not uzun:
            return {}
        try:
            return json.loads(self.rfile.read(uzun).decode("utf-8"))
        except Exception:
            return {}

    def yolla(self, o, kod=200, tur="application/json; charset=utf-8"):
        g = j(o) if not isinstance(o, bytes) else o
        try:
            self.send_response(kod)
            self.send_header("Content-Type", tur)
            self.send_header("Content-Length", str(len(g)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(g)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            self.close_connection = True

    def sorgu(self):
        return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}

    def yol(self):
        return urllib.parse.urlparse(self.path).path

    # ---------------------------------------------------------- GET
    def do_GET(self):
        ys = self.yol()
        try:
            if ys == "/api/durum":
                v = baglan()
                return self.yolla({
                    "surum": SURUM, "firma": AYAR["firma"], "port": self.server.server_address[1],
                    "db": os.path.basename(DB), "db_boyut": os.path.getsize(DB) if os.path.exists(DB) else 0,
                    "sayilar": {
                        "cari": v.execute("SELECT COUNT(*) c FROM cari").fetchone()["c"],
                        "hareket": v.execute("SELECT COUNT(*) c FROM hareket").fetchone()["c"],
                        "fatura": v.execute("SELECT COUNT(*) c FROM fatura").fetchone()["c"],
                        "stok": v.execute("SELECT COUNT(*) c FROM stok").fetchone()["c"],
                        "personel": v.execute("SELECT COUNT(*) c FROM personel").fetchone()["c"],
                        "hesap": v.execute("SELECT COUNT(*) c FROM hesap").fetchone()["c"],
                        "gorusme": v.execute("SELECT COUNT(*) c FROM gorusme").fetchone()["c"],
                        "gelir_gider": v.execute("SELECT COUNT(*) c FROM gelir_gider").fetchone()["c"],
                        "kalem": v.execute("SELECT COUNT(*) c FROM fatura_kalem").fetchone()["c"],
                    }, "ayar": {k: AYAR[k] for k in ("firma", "tema", "kdv", "para")}})
            if ys == "/api/ozet":
                v = baglan()
                return self.yolla(ozet(v))
            if ys == "/api/cari":
                v = baglan()
                s = self.sorgu().get("q", "")
                kayit = []
                for r in v.execute("SELECT * FROM cari ORDER BY unvan").fetchall():
                    d = dict(r)
                    d["bakiye"] = cari_bakiye(v, r["id"])
                    kayit.append(d)
                if s:
                    s = s.lower()
                    kayit = [k for k in kayit if s in (k["unvan"] or "").lower() or s in (k["kod"] or "").lower()
                             or s in (k["telefon"] or "").lower()]
                return self.yolla({"kayit": kayit, "toplam": len(kayit),
                                   "alacak": round(sum(k["bakiye"] for k in kayit if k["bakiye"] > 0), 2),
                                   "borc": round(sum(-k["bakiye"] for k in kayit if k["bakiye"] < 0), 2)})
            if ys == "/api/hareket":
                v = baglan()
                cid = self.sorgu().get("cari_id")
                if cid:
                    rs = v.execute("""SELECT * FROM hareket WHERE cari_id=? ORDER BY tarih DESC, id DESC""",
                                   (cid,)).fetchall()
                else:
                    rs = v.execute("SELECT * FROM hareket ORDER BY tarih DESC, id DESC LIMIT 200").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs]})
            if ys == "/api/hesap":
                v = baglan()
                kayit = []
                for r in v.execute("SELECT * FROM hesap ORDER BY tur, ad").fetchall():
                    d = dict(r)
                    d["bakiye"] = hesap_bakiye(v, r["id"])
                    kayit.append(d)
                return self.yolla({"kayit": kayit,
                                   "kasa": round(sum(k["bakiye"] for k in kayit if k["tur"] == "Kasa"), 2),
                                   "banka": round(sum(k["bakiye"] for k in kayit if k["tur"] == "Banka"), 2)})
            if ys == "/api/kasa-hareket":
                v = baglan()
                hid = self.sorgu().get("hesap_id")
                if hid:
                    rs = v.execute("""SELECT * FROM kasa_hareket WHERE hesap_id=? ORDER BY tarih DESC, id DESC""",
                                   (hid,)).fetchall()
                else:
                    rs = v.execute("SELECT * FROM kasa_hareket ORDER BY tarih DESC, id DESC LIMIT 200").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs]})
            if ys == "/api/fatura":
                v = baglan()
                s = self.sorgu()
                kosul, arg = [], []
                if s.get("tur"):
                    kosul.append("f.tur=?")
                    arg.append(s["tur"])
                if s.get("cari_id"):
                    kosul.append("f.cari_id=?")
                    arg.append(s["cari_id"])
                nerede = ("WHERE " + " AND ".join(kosul)) if kosul else ""
                rs = v.execute("""SELECT f.*, c.unvan FROM fatura f LEFT JOIN cari c ON c.id=f.cari_id
                                  %s ORDER BY f.tarih DESC, f.id DESC""" % nerede, arg).fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs], "toplam": len(rs)})
            if ys == "/api/fatura-detay":
                v = baglan()
                fid = self.sorgu().get("id")
                f = v.execute("""SELECT f.*, c.unvan FROM fatura f LEFT JOIN cari c ON c.id=f.cari_id
                                 WHERE f.id=?""", (fid,)).fetchone()
                k = v.execute("SELECT * FROM fatura_kalem WHERE fatura_id=? ORDER BY id", (fid,)).fetchall()
                return self.yolla({"fatura": dict(f) if f else None, "kalem": [dict(r) for r in k]})
            if ys == "/api/stok":
                v = baglan()
                rs = v.execute("SELECT * FROM stok ORDER BY ad").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs],
                                   "deger": round(sum((r["miktar"] or 0) * (r["alis"] or 0) for r in rs), 2)})
            if ys == "/api/personel":
                v = baglan()
                rs = v.execute("SELECT * FROM personel ORDER BY ad").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs],
                                   "maas_toplam": round(sum(r["maas"] or 0 for r in rs), 2)})
            if ys == "/api/gorusme":
                v = baglan()
                rs = v.execute("""SELECT g.*, c.unvan FROM gorusme g LEFT JOIN cari c ON c.id=g.cari_id
                                  ORDER BY g.tarih DESC, g.id DESC""").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs]})
            if ys == "/api/gelir-gider":
                v = baglan()
                s = self.sorgu()
                tur = s.get("tur")
                kosul, arg = [], []
                if tur in ("gelir", "gider"):
                    kosul.append("gg.tur=?")
                    arg.append(tur)
                if s.get("defter") in ("sade", "kurumsal"):
                    kosul.append("gg.defter=?")
                    arg.append(s["defter"])
                nerede = ("WHERE " + " AND ".join(kosul)) if kosul else ""
                rs = v.execute("""SELECT gg.*, h.ad hesap, c.unvan FROM gelir_gider gg
                                  LEFT JOIN hesap h ON h.id=gg.hesap_id
                                  LEFT JOIN cari c ON c.id=gg.cari_id
                                  %s ORDER BY gg.tarih DESC, gg.id DESC LIMIT 400""" % nerede, arg).fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs]})
            if ys == "/api/harcama-ozet":
                v = baglan()
                s = self.sorgu()
                gun = int(s.get("gun", 30))
                bug = bugun()
                bas = (datetime.date.today() - datetime.timedelta(days=gun - 1)).isoformat()
                ay_basi = bug[:8] + "01"

                def toplam(kosul, arg):
                    return round(v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE defter='sade' AND " + kosul, arg).fetchone()["t"], 2)

                seri = []
                for i in range(gun - 1, -1, -1):
                    g = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
                    seri.append({
                        "gun": g, "etiket": g[8:10] + "." + g[5:7],
                        "gelir": toplam("tur='gelir' AND tarih=?", (g,)),
                        "gider": toplam("tur='gider' AND tarih=?", (g,)),
                    })
                kat = v.execute("""SELECT kategori, tur, SUM(tutar) t, COUNT(*) adet FROM gelir_gider
                                   WHERE defter='sade' GROUP BY kategori, tur ORDER BY t DESC""").fetchall()
                kayit = v.execute("""SELECT * FROM gelir_gider WHERE defter='sade'
                                     ORDER BY tarih DESC, id DESC LIMIT 200""").fetchall()
                return self.yolla({
                    "bugun_gelir": toplam("tur='gelir' AND tarih=?", (bug,)),
                    "bugun_gider": toplam("tur='gider' AND tarih=?", (bug,)),
                    "ay_gelir": toplam("tur='gelir' AND tarih>=?", (ay_basi,)),
                    "ay_gider": toplam("tur='gider' AND tarih>=?", (ay_basi,)),
                    "donem_gelir": toplam("tur='gelir' AND tarih>=?", (bas,)),
                    "donem_gider": toplam("tur='gider' AND tarih>=?", (bas,)),
                    "kayit_sayisi": v.execute("SELECT COUNT(*) c FROM gelir_gider WHERE defter='sade'").fetchone()["c"],
                    "seri": seri,
                    "kategoriler": [{"ad": r["kategori"], "tur": r["tur"], "tutar": round(r["t"], 2), "adet": r["adet"]} for r in kat],
                    "kayit": [dict(r) for r in kayit],
                })
            if ys == "/api/rapor":
                v = baglan()
                return self.yolla(rapor(v, self.sorgu().get("tur", "gelir-gider"), self.sorgu()))
            if ys == "/api/ciktilar":
                dosyalar = []
                for ad in sorted(os.listdir(CIKTI), reverse=True):
                    p = os.path.join(CIKTI, ad)
                    dosyalar.append({"ad": ad, "boyut": os.path.getsize(p),
                                     "zaman": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d.%m.%Y %H:%M")})
                return self.yolla({"kayit": dosyalar})

            if ys == "/api/disa-aktar":
                return self.disa_aktar()
            if ys == "/api/yedek/listele":
                kayit = []
                for ad in sorted(os.listdir(YEDEK), reverse=True):
                    p = os.path.join(YEDEK, ad)
                    if os.path.isfile(p):
                        kayit.append({"ad": ad, "boyut": os.path.getsize(p),
                                      "zaman": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d.%m.%Y %H:%M")})
                return self.yolla({"kayit": kayit, "klasor": YEDEK})
            if ys == "/api/log":
                v = baglan()
                rs = v.execute("SELECT * FROM log ORDER BY id DESC LIMIT 80").fetchall()
                return self.yolla({"kayit": [dict(r) for r in rs]})

            if ys.startswith("/api/"):
                if ozellikler.get(self, ys):
                    return
                return self.yolla({"hata": "bilinmeyen uç: " + ys}, 404)
            return self.dosya(ys)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self.yolla({"hata": "%s: %s" % (type(e).__name__, e)}, 500)

    # ---------------------------------------------------------- POST
    def do_POST(self):
        ys = self.yol()
        g = self.govde()
        try:
            v = baglan()
            # --- rol denetimi: kasiyer/misafir silme, ayar, yedek geri alma yapamaz
            if ys in ("/api/sil", "/api/ayar", "/api/yedek/geri", "/api/yedek/al", "/api/disa-aktar"):
                izin, rol = ozellikler.yetki(self, v, ys, True)
                if not izin:
                    ozellikler.yaz_log(v, "yetkisiz", "%s -> %s" % (ys, rol or "oturumsuz"))
                    v.commit()
                    return self.yolla({"tamam": False, "hata": rol or "bu işlem için yönetici yetkisi gerekir"}, 403)
            tablo = {
                "/api/cari/kaydet": ("cari", ["kod", "unvan", "tip", "vergi_dairesi", "vergi_no", "yetkili",
                                              "telefon", "email", "il", "ilce", "adres", "acilis_bakiye",
                                              "risk_limiti", "notlar"]),
                "/api/hareket/kaydet": ("hareket", ["cari_id", "tarih", "evrak_no", "aciklama", "borc", "alacak",
                                                    "kaynak", "hesap_id"]),
                "/api/hesap/kaydet": ("hesap", ["ad", "tur", "banka", "iban", "sube", "acilis"]),
                "/api/kasa-hareket/kaydet": ("kasa_hareket", ["hesap_id", "tarih", "tur", "tutar", "aciklama",
                                                              "kategori", "cari_id", "evrak_no"]),
                "/api/stok/kaydet": ("stok", ["kod", "ad", "birim", "miktar", "alis", "satis", "kdv", "kritik",
                                              "kategori"]),
                "/api/personel/kaydet": ("personel", ["ad", "gorev", "telefon", "email", "maas", "giris_tarihi",
                                                      "durum", "notlar"]),
                "/api/gorusme/kaydet": ("gorusme", ["cari_id", "tarih", "saat", "konu", "sonuc", "takip", "durum",
                                                    "notlar"]),
                "/api/gelir-gider/kaydet": ("gelir_gider", ["tarih", "tur", "kategori", "aciklama", "tutar",
                                                            "hesap_id", "cari_id", "evrak_no", "tekrarlayan", "defter"]),
            }
            if ys in tablo:
                t, alanlar = tablo[ys]
                kayit = self.kaydet(v, t, alanlar, g)
                return self.yolla({"tamam": True, "id": kayit, "kayit": kayit})
            if ys == "/api/fatura/kaydet":
                return self.yolla(self.fatura_kaydet(v, g))
            if ys == "/api/sil":
                t = g.get("tablo")
                if t not in TABLOLAR:
                    return self.yolla({"hata": "geçersiz tablo"}, 400)
                v.execute("DELETE FROM %s WHERE id=?" % t, (g.get("id"),))
                if t == "fatura":
                    v.execute("DELETE FROM fatura_kalem WHERE fatura_id=?", (g.get("id"),))
                yaz_log(v, "sil", "%s #%s" % (t, g.get("id")))
                v.commit()
                return self.yolla({"tamam": True})
            if ys == "/api/ayar":
                for k, val in (g or {}).items():
                    if k in AYAR_VARSAYILAN or k in AYAR:
                        AYAR[k] = val
                ayar_yaz()
                yaz_log(v, "ayar", json.dumps({k: g[k] for k in g if k != "sifre_hash"}, ensure_ascii=False))
                v.commit()
                return self.yolla({"tamam": True, "ayar": AYAR})
            if ys == "/api/giris":
                k, s = g.get("kullanici", ""), g.get("sifre", "") or g.get("sifre_hash", "")
                oturum = ozellikler.giris_yap(v, k, s)
                ok = bool(oturum)
                if not ok and not v.execute("SELECT COUNT(*) c FROM kullanici").fetchone()["c"]:
                    ok = (k == AYAR.get("kullanici")) and (not AYAR.get("sifre_hash") or s == AYAR["sifre_hash"])
                yaz_log(v, "giris", "%s -> %s" % (k, "başarılı" if ok else "hatalı"))
                v.commit()
                cevap = {"tamam": ok, "firma": AYAR["firma"], "tema": AYAR.get("tema", "gece")}
                if ok and oturum:
                    cevap.update(oturum)
                return self.yolla(cevap, 200 if ok else 401)
            if ys == "/api/yedek/al":
                ad = "muhasebe-yedek-%s.db" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                hedef = os.path.join(YEDEK, ad)
                v.commit()
                v.execute("PRAGMA wal_checkpoint(FULL)")
                shutil.copy2(DB, hedef)
                yaz_log(v, "yedek", ad)
                v.commit()
                return self.yolla({"tamam": True, "ad": ad, "boyut": os.path.getsize(hedef)})
            if ys == "/api/yedek/geri":
                ad = os.path.basename(g.get("ad", ""))
                kaynak = os.path.join(YEDEK, ad)
                if not os.path.exists(kaynak):
                    return self.yolla({"hata": "yedek bulunamadı"}, 404)
                self.onceki = DB + ".onceki"
                shutil.copy2(DB, self.onceki)
                v.close()
                shutil.copy2(kaynak, DB)
                v2 = baglan()
                yaz_log(v2, "yedek-geri", ad)
                v2.commit()
                return self.yolla({"tamam": True, "ad": ad})
            if ozellikler.post(self, ys, g):
                return
            return self.yolla({"hata": "bilinmeyen uç: " + ys}, 404)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self.yolla({"hata": "%s: %s" % (type(e).__name__, e)}, 500)

    # ---------------------------------------------------------- ortak işler
    def kaydet(self, v, tablo, alanlar, g):
        rid = g.get("id")
        deger = []
        for a in alanlar:
            x = g.get(a)
            if isinstance(x, str) and x.strip() == "":
                x = None
            deger.append(x)
        if rid:
            v.execute("UPDATE %s SET %s WHERE id=?" % (tablo, ",".join(a + "=?" for a in alanlar)),
                      deger + [rid])
            kid = rid
        else:
            v.execute("INSERT INTO %s(%s,olusturma) VALUES(%s,?)" % (
                tablo, ",".join(alanlar), ",".join("?" * len(alanlar))), deger + [simdi()])
            kid = v.execute("SELECT last_insert_rowid() i").fetchone()["i"]
        # kasa hareketi otomatik yansıması
        if tablo == "gelir_gider" and g.get("hesap_id"):
            v.execute("""INSERT INTO kasa_hareket(hesap_id,tarih,tur,tutar,aciklama,kategori,cari_id,evrak_no,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (g.get("hesap_id"), g.get("tarih"), "giriş" if g.get("tur") == "gelir" else "çıkış",
                       abs(float(g.get("tutar") or 0)), g.get("aciklama"), g.get("kategori"),
                       g.get("cari_id"), g.get("evrak_no"), simdi()))
        if tablo == "hareket" and g.get("hesap_id") and float(g.get("borc") or 0) == 0 and float(g.get("alacak") or 0) > 0:
            v.execute("""INSERT INTO kasa_hareket(hesap_id,tarih,tur,tutar,aciklama,cari_id,evrak_no,olusturma)
                         VALUES(?,?,?,?,?,?,?,?)""",
                      (g.get("hesap_id"), g.get("tarih"), "giriş", abs(float(g.get("alacak") or 0)),
                       g.get("aciklama") or "Tahsilat", g.get("cari_id"), g.get("evrak_no"), simdi()))
        yaz_log(v, "kaydet:" + tablo, "#%s %s" % (kid, g.get("unvan") or g.get("ad") or g.get("aciklama") or ""))
        v.commit()
        return kid

    def fatura_kaydet(self, v, g):
        kalem = g.pop("kalem", []) or []
        ara = 0.0
        kdv = 0.0
        for k in kalem:
            tut = round(float(k.get("miktar") or 0) * float(k.get("birim_fiyat") or 0), 2)
            k["tutar"] = tut
            ara += tut
            kdv += round(tut * float(k.get("kdv_orani") or 0) / 100.0, 2)
        isk = float(g.get("iskonto") or 0)
        toplam = round(ara - isk + kdv, 2)
        alanlar = ["no", "tur", "cari_id", "tarih", "vade", "aciklama", "durum", "tahsil"]
        deger = [g.get(a) for a in alanlar]
        if g.get("id"):
            v.execute("""UPDATE fatura SET no=?,tur=?,cari_id=?,tarih=?,vade=?,aciklama=?,ara_toplam=?,iskonto=?,
                         kdv=?,toplam=?,durum=?,tahsil=? WHERE id=?""",
                      deger + [round(ara, 2), isk, round(kdv, 2), toplam, round(float(g.get("tahsil") or 0), 2), g["id"]])
            fid = g["id"]
            v.execute("DELETE FROM fatura_kalem WHERE fatura_id=?", (fid,))
        else:
            if not g.get("no"):
                y = datetime.date.today().year
                s = v.execute("SELECT COUNT(*) c FROM fatura").fetchone()["c"] + 300
                g["no"] = "FTR-%s-%04d" % (y, s)
            v.execute("""INSERT INTO fatura(no,tur,cari_id,tarih,vade,aciklama,ara_toplam,iskonto,kdv,toplam,durum,
                         tahsil,olusturma) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (g["no"], g.get("tur"), g.get("cari_id"), g.get("tarih"), g.get("vade"), g.get("aciklama"),
                       round(ara, 2), isk, round(kdv, 2), toplam, g.get("durum") or "Bekliyor",
                       round(float(g.get("tahsil") or 0), 2), simdi()))
            fid = v.execute("SELECT last_insert_rowid() i").fetchone()["i"]
        for k in kalem:
            v.execute("""INSERT INTO fatura_kalem(fatura_id,aciklama,miktar,birim,birim_fiyat,kdv_orani,tutar)
                         VALUES(?,?,?,?,?,?,?)""",
                      (fid, k.get("aciklama"), k.get("miktar"), k.get("birim"), k.get("birim_fiyat"),
                       k.get("kdv_orani"), k["tutar"]))
        # --- stok otomatik düşümü: satışta ürün adı stokla eşleşiyorsa miktarı iner, alışta artar
        stok_etki = []
        try:
            for k in kalem:
                ad = (k.get("aciklama") or "").strip()
                if not ad:
                    continue
                s = v.execute("SELECT id, ad, miktar FROM stok WHERE lower(ad)=lower(?) OR lower(kod)=lower(?)",
                              (ad, ad)).fetchone()
                if not s:
                    continue
                mk = float(k.get("miktar") or 0)
                yon = -1 if (g.get("tur") or "Satış") == "Satış" else 1
                v.execute("UPDATE stok SET miktar = miktar + ? WHERE id=?", (yon * mk, s["id"]))
                stok_etki.append("%s %s%.0f" % (s["ad"], "+" if yon > 0 else "-", mk))
        except Exception as e:
            print("stok düşümü hatası:", e)
        # cari hareketine işle
        if g.get("cari_id"):
            if g.get("tur") == "Satış":
                v.execute("""INSERT INTO hareket(cari_id,tarih,evrak_no,aciklama,borc,alacak,kaynak,olusturma)
                             VALUES(?,?,?,?,?,0,'fatura',?)""",
                          (g["cari_id"], g.get("tarih"), g["no"], "Satış faturası", toplam, simdi()))
            else:
                v.execute("""INSERT INTO hareket(cari_id,tarih,evrak_no,aciklama,borc,alacak,kaynak,olusturma)
                             VALUES(?,?,?,?,0,?,'fatura',?)""",
                          (g["cari_id"], g.get("tarih"), g["no"], "Alış faturası", toplam, simdi()))
        yaz_log(v, "kaydet:fatura", "%s / %.2f TL" % (g.get("no"), toplam))
        v.commit()
        return {"tamam": True, "id": fid, "toplam": toplam, "ara_toplam": round(ara, 2), "kdv": round(kdv, 2)}

    # ---------------------------------------------------------- raporlar
    def rapor_veri(self, v, tur, s):
        bas = s.get("bas") or ""
        bit = s.get("bit") or ""
        if tur == "gelir-gider":
            n, arg = "", []
            if bas:
                n += " AND tarih>=?"
                arg.append(bas)
            if bit:
                n += " AND tarih<=?"
                arg.append(bit)
            r = v.execute("""SELECT kategori, tur, SUM(tutar) t, COUNT(*) adet FROM gelir_gider
                             WHERE 1=1 %s GROUP BY kategori, tur ORDER BY tur, t DESC""" % n, arg).fetchall()
            return {"tur": tur, "basliklar": ["Kategori", "Tür", "Adet", "Tutar"],
                    "satirlar": [[x["kategori"], x["tur"].title(), x["adet"], round(x["t"], 2)] for x in r],
                    "toplam": round(sum(x["t"] for x in r if x["tur"] == "gelir") -
                                    sum(x["t"] for x in r if x["tur"] == "gider"), 2)}
        if tur == "kar-zarar":
            out = []
            for ay_geri in range(11, -1, -1):
                bas2 = (datetime.date.today().replace(day=1) - datetime.timedelta(days=ay_geri * 30)).replace(day=1)
                son = (bas2 + datetime.timedelta(days=31)).replace(day=1)
                g = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gelir' AND tarih>=? AND tarih<?",
                              (bas2.isoformat(), son.isoformat())).fetchone()["t"]
                d = v.execute("SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider WHERE tur='gider' AND tarih>=? AND tarih<?",
                              (bas2.isoformat(), son.isoformat())).fetchone()["t"]
                out.append([bas2.strftime("%m/%Y"), round(g, 2), round(d, 2), round(g - d, 2)])
            return {"tur": tur, "basliklar": ["Dönem", "Gelir", "Gider", "Kâr / Zarar"], "satirlar": out,
                    "toplam": round(sum(x[3] for x in out), 2)}
        if tur == "vadesi-gecen":
            rs = v.execute("""SELECT f.no, c.unvan, f.tarih, f.vade, f.toplam, f.tahsil, f.durum
                              FROM fatura f LEFT JOIN cari c ON c.id=f.cari_id
                              WHERE f.durum IN ('Bekliyor','Kısmi') AND f.vade < ?
                              ORDER BY f.vade""", (bugun(),)).fetchall()
            return {"tur": tur, "basliklar": ["Fatura No", "Cari", "Tarih", "Vade", "Toplam", "Tahsil", "Kalan", "Durum"],
                    "satirlar": [[r["no"], r["unvan"], r["tarih"], r["vade"], round(r["toplam"], 2),
                                  round(r["tahsil"], 2), round(r["toplam"] - r["tahsil"], 2), r["durum"]] for r in rs],
                    "toplam": round(sum(r["toplam"] - r["tahsil"] for r in rs), 2)}
        if tur == "cari-ekstre":
            out = []
            for r in v.execute("SELECT id, kod, unvan FROM cari ORDER BY unvan").fetchall():
                out.append([r["kod"], r["unvan"], cari_bakiye(v, r["id"])])
            return {"tur": tur, "basliklar": ["Kod", "Cari", "Bakiye"], "satirlar": out,
                    "toplam": round(sum(x[2] for x in out), 2)}
        if tur == "kdv":
            rs = v.execute("""SELECT no, tur, tarih, ara_toplam, kdv, toplam FROM fatura
                              ORDER BY tarih DESC LIMIT 200""").fetchall()
            return {"tur": tur, "basliklar": ["Fatura No", "Tür", "Tarih", "Matrah", "KDV", "Toplam"],
                    "satirlar": [[r["no"], r["tur"], r["tarih"], round(r["ara_toplam"], 2), round(r["kdv"], 2),
                                  round(r["toplam"], 2)] for r in rs],
                    "toplam": round(sum(r["kdv"] for r in rs if r["tur"] == "Satış") -
                                    sum(r["kdv"] for r in rs if r["tur"] == "Alış"), 2)}
        if tur == "personel":
            rs = v.execute("SELECT ad, gorev, maas, giris_tarihi, durum FROM personel ORDER BY maas DESC").fetchall()
            return {"tur": tur, "basliklar": ["Personel", "Görev", "Maaş", "İşe Giriş", "Durum"],
                    "satirlar": [[r["ad"], r["gorev"], round(r["maas"], 2), r["giris_tarihi"], r["durum"]] for r in rs],
                    "toplam": round(sum(r["maas"] for r in rs), 2)}
        if tur == "stok":
            rs = v.execute("SELECT kod, ad, birim, miktar, alis, satis, kritik FROM stok ORDER BY ad").fetchall()
            return {"tur": tur, "basliklar": ["Kod", "Ürün", "Birim", "Miktar", "Alış", "Satış", "Kritik"],
                    "satirlar": [[r["kod"], r["ad"], r["birim"], round(r["miktar"], 2), round(r["alis"], 2),
                                  round(r["satis"], 2), r["kritik"]] for r in rs],
                    "toplam": round(sum(r["miktar"] * r["alis"] for r in rs), 2)}
        if tur == "kasa":
            out = []
            for r in v.execute("SELECT id, ad, tur FROM hesap ORDER BY tur, ad").fetchall():
                out.append([r["ad"], r["tur"], hesap_bakiye(v, r["id"])])
            return {"tur": tur, "basliklar": ["Hesap", "Tür", "Bakiye"], "satirlar": out,
                    "toplam": round(sum(x[2] for x in out), 2)}
        if tur == "tahsilat":
            rs = v.execute("""SELECT h.tarih, c.unvan, h.aciklama, h.alacak FROM hareket h
                              LEFT JOIN cari c ON c.id=h.cari_id WHERE h.alacak>0
                              ORDER BY h.tarih DESC LIMIT 200""").fetchall()
            return {"tur": tur, "basliklar": ["Tarih", "Cari", "Açıklama", "Tahsilat"],
                    "satirlar": [[r["tarih"], r["unvan"], r["aciklama"], round(r["alacak"], 2)] for r in rs],
                    "toplam": round(sum(r["alacak"] for r in rs), 2)}
        if tur == "gorusme":
            rs = v.execute("""SELECT g.tarih, g.saat, c.unvan, g.konu, g.sonuc, g.durum FROM gorusme g
                              LEFT JOIN cari c ON c.id=g.cari_id ORDER BY g.tarih DESC""").fetchall()
            return {"tur": tur, "basliklar": ["Tarih", "Saat", "Cari", "Konu", "Sonuç", "Durum"],
                    "satirlar": [[r["tarih"], r["saat"], r["unvan"], r["konu"], r["sonuc"], r["durum"]] for r in rs],
                    "toplam": len(rs)}
        return {"tur": tur, "basliklar": [], "satirlar": [], "toplam": 0}

    # ---------------------------------------------------------- dışa aktarma
    def ektar_veri(self, s):
        """Excel / Word / PDF için başlık ve satırları hazırlar."""
        kaynak = s.get("kaynak", "cari")
        v = baglan()
        adlar = {"cari": "Cari Listesi", "kasa-hareket": "Kasa Hareketleri", "fatura": "Fatura Listesi",
                 "stok": "Stok Listesi", "personel": "Personel Listesi", "gorusme": "Görüşmeler",
                 "gelir-gider": "Gelir Gider Defteri", "hesap": "Kasa ve Banka Hesapları",
                 "harcama": "Sade Harcama Defteri", "hareket": "Cari Hareketleri",
                 "cek": "Çek ve Senet Listesi", "butce": "Bütçe Durumu", "gorev": "Görev Listesi",
                 "tekrar": "Tekrarlayan Kayıtlar ve Abonelikler", "puantaj": "Puantaj Kayıtları",
                 "fis": "Fiş ve Fatura Fotoğrafları", "kullanicilar": "Kullanıcılar ve Roller"}
        if kaynak == "rapor":
            tur = s.get("rapor", "gelir-gider")
            r = self.rapor_veri(v, tur, s)
            baslik, basliklar, satirlar = tur, r["basliklar"], r["satirlar"]
            toplam = r.get("toplam")
        else:
            if kaynak not in adlar:
                return self.yolla({"hata": "bilinmeyen kaynak"}, 400)
            baslik = adlar[kaynak]
            if kaynak == "cari":
                basliklar = ["Kod", "Ünvan", "Tip", "Telefon", "Yetkili", "Bakiye"]
                satirlar = [[r["kod"], r["unvan"], r["tip"], r["telefon"], r["yetkili"], cari_bakiye(v, r["id"])]
                            for r in v.execute("SELECT * FROM cari ORDER BY unvan").fetchall()]
            elif kaynak == "hesap":
                basliklar = ["Hesap", "Tür", "Banka", "IBAN", "Bakiye"]
                satirlar = [[r["ad"], r["tur"], r["banka"], r["iban"], hesap_bakiye(v, r["id"])]
                            for r in v.execute("SELECT * FROM hesap ORDER BY tur, ad").fetchall()]
            elif kaynak == "kasa-hareket":
                basliklar = ["Tarih", "Hesap", "Tür", "Tutar", "Açıklama", "Kategori"]
                satirlar = [[r["tarih"], r["ad"], r["tur"], r["tutar"], r["aciklama"], r["kategori"]]
                            for r in v.execute("""SELECT k.*, h.ad FROM kasa_hareket k
                                                  LEFT JOIN hesap h ON h.id=k.hesap_id
                                                  ORDER BY k.tarih DESC LIMIT 500""").fetchall()]
            elif kaynak == "fatura":
                basliklar = ["No", "Tür", "Cari", "Tarih", "Vade", "Toplam", "Ödenen", "Durum"]
                satirlar = [[r["no"], r["tur"], r["unvan"], r["tarih"], r["vade"], r["toplam"], r["tahsil"], r["durum"]]
                            for r in v.execute("""SELECT f.*, c.unvan FROM fatura f LEFT JOIN cari c ON c.id=f.cari_id
                                                  ORDER BY f.tarih DESC""").fetchall()]
            elif kaynak == "stok":
                basliklar = ["Kod", "Ürün", "Birim", "Miktar", "Alış", "Satış", "Stok Değeri"]
                satirlar = [[r["kod"], r["ad"], r["birim"], r["miktar"], r["alis"], r["satis"],
                             round(r["miktar"] * r["alis"], 2)] for r in v.execute("SELECT * FROM stok ORDER BY ad").fetchall()]
            elif kaynak == "personel":
                basliklar = ["Ad", "Görev", "Telefon", "E-posta", "Maaş", "İşe Giriş", "Durum"]
                satirlar = [[r["ad"], r["gorev"], r["telefon"], r["email"], r["maas"], r["giris_tarihi"], r["durum"]]
                            for r in v.execute("SELECT * FROM personel ORDER BY ad").fetchall()]
            elif kaynak == "gorusme":
                basliklar = ["Tarih", "Saat", "Cari", "Konu", "Sonuç", "Durum"]
                satirlar = [[r["tarih"], r["saat"], r["unvan"], r["konu"], r["sonuc"], r["durum"]]
                            for r in v.execute("""SELECT g.*, c.unvan FROM gorusme g LEFT JOIN cari c ON c.id=g.cari_id
                                                  ORDER BY g.tarih DESC""").fetchall()]
            elif kaynak == "gelir-gider":
                basliklar = ["Tarih", "Tür", "Kategori", "Açıklama", "Tutar", "Hesap"]
                satirlar = [[r["tarih"], r["tur"], r["kategori"], r["aciklama"], r["tutar"], r["ad"]]
                            for r in v.execute("""SELECT gg.*, h.ad FROM gelir_gider gg LEFT JOIN hesap h ON h.id=gg.hesap_id
                                                  ORDER BY gg.tarih DESC LIMIT 500""").fetchall()]
            elif kaynak == "harcama":
                basliklar = ["Tarih", "Tür", "Kategori", "Açıklama", "Tutar"]
                satirlar = [[r["tarih"], r["tur"].title(), r["kategori"], r["aciklama"], r["tutar"]]
                            for r in v.execute("""SELECT * FROM gelir_gider WHERE defter='sade'
                                                  ORDER BY tarih DESC LIMIT 500""").fetchall()]
                toplam = round(sum(r["tutar"] if r["tur"] == "gelir" else -r["tutar"] for r in
                                   v.execute("SELECT tur, tutar FROM gelir_gider WHERE defter='sade'").fetchall()), 2)
            elif kaynak == "hareket":
                basliklar = ["Tarih", "Cari", "Evrak", "Açıklama", "Borç", "Alacak"]
                satirlar = [[r["tarih"], r["unvan"], r["evrak_no"], r["aciklama"], r["borc"], r["alacak"]]
                            for r in v.execute("""SELECT h.*, c.unvan FROM hareket h LEFT JOIN cari c ON c.id=h.cari_id
                                                  ORDER BY h.tarih DESC LIMIT 500""").fetchall()]
            elif kaynak == "cek":
                basliklar = ["Tür", "Yön", "No", "Cari", "Banka", "Tutar", "Kesim", "Vade", "Durum"]
                satirlar = [[r["tur"], r["yon"], r["no"], r["unvan"], r["banka"], r["tutar"],
                             r["kesim"], r["vade"], r["durum"]]
                            for r in v.execute("""SELECT k.*, c.unvan FROM cek_senet k
                                                  LEFT JOIN cari c ON c.id=k.cari_id
                                                  ORDER BY k.vade""").fetchall()]
                toplam = round(sum(r["tutar"] for r in v.execute(
                    "SELECT tutar FROM cek_senet WHERE durum IN ('Portföyde','Ödenecek')").fetchall()), 2)
            elif kaynak == "butce":
                basliklar = ["Kategori", "Defter", "Bütçe", "Harcanan", "Kalan", "Oran %", "Durum"]
                satirlar = []
                toplam = 0.0
                for b in v.execute("SELECT * FROM butce WHERE aktif=1 ORDER BY kategori").fetchall():
                    kosul = " AND kategori=?" if b["kategori"] and b["kategori"] != "TÜMÜ" else ""
                    arg = [b["kategori"]] if kosul else []
                    har = v.execute("""SELECT COALESCE(SUM(tutar),0) t FROM gelir_gider
                                       WHERE tur='gider' AND defter=? AND substr(tarih,1,7)=? %s""" % kosul,
                                    [b["defter"], bugun()[:7]] + arg).fetchone()["t"]
                    oran = round(har / b["tutar"] * 100, 2) if b["tutar"] else 0
                    durum = "aşıldı" if oran > 100 else ("uyarı" if oran >= (b["uyari_yuzde"] or 80) else "normal")
                    satirlar.append([b["kategori"], b["defter"], b["tutar"], round(har, 2),
                                     round(b["tutar"] - har, 2), oran, durum])
                    toplam += b["tutar"] - har
            elif kaynak == "gorev":
                basliklar = ["Tarih", "Başlık", "Detay", "Öncelik", "Durum"]
                satirlar = [[r["tarih"], r["baslik"], r["detay"], r["oncelik"], r["durum"]]
                            for r in v.execute("SELECT * FROM gorev ORDER BY tarih DESC").fetchall()]
                toplam = len(satirlar)
            elif kaynak == "tekrar":
                basliklar = ["Ad", "Tür", "Kategori", "Tutar", "Sıklık", "Gün", "Defter", "Abonelik"]
                satirlar = [[r["ad"], r["tur"], r["kategori"], r["tutar"], r["siklik"], r["gun"],
                             r["defter"], "Evet" if r["abonelik"] else "Hayır"]
                            for r in v.execute("SELECT * FROM tekrar ORDER BY aktif DESC, ad").fetchall()]
                toplam = round(sum(r["tutar"] for r in v.execute(
                    "SELECT tutar FROM tekrar WHERE aktif=1 AND siklik='Aylik'").fetchall()), 2)
            elif kaynak == "puantaj":
                basliklar = ["Tarih", "Personel", "Tür", "Tutar", "Gün", "Açıklama"]
                satirlar = [[r["tarih"], r["ad"], r["tur"], r["tutar"], r["gun"], r["aciklama"]]
                            for r in v.execute("""SELECT p.*, per.ad FROM puantaj p
                                                  LEFT JOIN personel per ON per.id=p.personel_id
                                                  ORDER BY p.tarih DESC""").fetchall()]
                toplam = round(sum(r[3] or 0 for r in satirlar if r[2] in ("Avans", "Prim")), 2)
            elif kaynak == "fis":
                basliklar = ["Tarih", "Dosya", "Tutar", "Kategori", "Açıklama", "Durum"]
                satirlar = [[r["tarih"], r["dosya"], r["tutar"], r["kategori"], r["aciklama"], r["durum"]]
                            for r in v.execute("SELECT * FROM fis ORDER BY tarih DESC").fetchall()]
                toplam = round(sum(r[2] or 0 for r in satirlar), 2)
            elif kaynak == "kullanicilar":
                basliklar = ["Kullanıcı", "Rol", "Ad Soyad", "Son Giriş"]
                roller = {"yonetici": "Yönetici (tam yetki)", "muhasebeci": "Muhasebeci",
                          "kasiyer": "Kasiyer (kasa/fatura)", "misafir": "Misafir (yalnız okuma)"}
                satirlar = [[r["kullanici"], roller.get(r["rol"], r["rol"]), r["ad"], r["son_giris"] or "—"]
                            for r in v.execute("SELECT * FROM kullanici ORDER BY rol, kullanici").fetchall()]
                toplam = len(satirlar)
            else:
                basliklar, satirlar = [], []
            if "toplam" not in locals():
                toplam = None
        return kaynak, baslik, basliklar, satirlar, toplam

    def ektar_dosya(self, s, dosya_turu):
        """Belirtilen biçimde dosyayı üretir ve (yol, ad, mime) döndürür."""
        kaynak, baslik, basliklar, satirlar, toplam = self.ektar_veri(s)
        v = baglan()
        zaman = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        guvenli = re.sub(r"[^A-Za-z0-9ĞÜŞİÖÇğüşıöç_-]", "-", baslik)
        yaz_log(v, "disa-aktar", "%s -> %s" % (kaynak, dosya_turu))
        v.commit()

        if dosya_turu == "xlsx":
            ad = "%s-%s.xlsx" % (guvenli, zaman)
            yol = os.path.join(CIKTI, ad)
            disa_aktar.xlsx_yaz(yol, baslik, basliklar, satirlar, sayi_ilk_sutun=max(2, len(basliklar) - 2),
                                alt_satirlar=[("TOPLAM", toplam)] if toplam is not None else None)
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            ad = "%s-%s.docx" % (guvenli, zaman)
            yol = os.path.join(CIKTI, ad)
            bolumler = [{
                "baslik": "%s" % baslik,
                "paragraf": ["Firma: %s · Dönem: %s" % (AYAR["firma"], datetime.date.today().strftime("%m/%Y")),
                             "Kayıt sayısı: %d" % len(satirlar)],
                "tablo": (basliklar, satirlar),
                "not": ("TOPLAM: %s" % ("{:,.2f}".format(toplam).replace(",", ".") if isinstance(toplam, (int, float)) else toplam))
                        if toplam is not None else "Bu belge ÜSTAD MUHASEBE tarafından üretilmiştir.",
            }]
            disa_aktar.docx_yaz(yol, baslik, bolumler)
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        return yol, ad, mime

    def disa_aktar(self):
        s = self.sorgu()
        yol, ad, mime = self.ektar_dosya(s, s.get("tur", "xlsx"))
        with open(yol, "rb") as f:
            icerik = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Disposition", 'attachment; filename="%s"' % ad)
        self.send_header("Content-Length", str(len(icerik)))
        self.end_headers()
        self.wfile.write(icerik)

    # ---------------------------------------------------------- statik dosya
    def dosya(self, ys):
        if ys in ("/", ""):
            ys = "/index.html"
        temiz = urllib.parse.unquote(ys.lstrip("/")).replace("\\", "/")
        if ".." in temiz:
            return self.yolla({"hata": "yasak"}, 403)
        if temiz.startswith("cikti/"):
            p = os.path.join(CIKTI, temiz[len("cikti/"):])
        elif temiz.startswith("yedek/"):
            p = os.path.join(YEDEK, temiz[len("yedek/"):])
        else:
            p = os.path.join(PANEL, temiz)
        if not os.path.isfile(p):
            return self.yolla({"hata": "bulunamadı: " + temiz}, 404)
        turler = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                  ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
                  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
                  ".ico": "image/x-icon", ".woff2": "font/woff2", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        tur = turler.get(os.path.splitext(p)[1].lower(), "application/octet-stream")
        with open(p, "rb") as f:
            icerik = f.read()
        self.send_response(200)
        self.send_header("Content-Type", tur)
        self.send_header("Content-Length", str(len(icerik)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(icerik)


def rapor(v, tur, s):
    class Sahte:
        def rapor_veri(self, v, t, s):
            return _rapor_veri(v, t, s)
    return _rapor_veri(v, tur, s)


def _rapor_veri(v, tur, s):
    # Isleyici.rapor_veri ile aynı gövde (paylaşımlı kullanım için ince sarmalayıcı)
    gecici = Isleyici.__new__(Isleyici)
    return gecici.rapor_veri(v, tur, s)


# --------------------------------------------------------------- ayar
AYAR = {}


def ayar_oku():
    global AYAR
    AYAR = dict(AYAR_VARSAYILAN)
    if os.path.exists(AYAR_DOSYA):
        try:
            with open(AYAR_DOSYA, "r", encoding="utf-8") as f:
                AYAR.update(json.load(f))
        except Exception:
            pass


def ayar_yaz():
    with open(AYAR_DOSYA, "w", encoding="utf-8") as f:
        json.dump(AYAR, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------- ana
class Sunucu(socketserver.ThreadingTCPServer):
    allow_reuse_address = False
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else AYAR_VARSAYILAN["sunucu_port"]
    ag_zorla = "--ag" in sys.argv
    ayar_oku()
    v = baglan()
    kur(v)
    ozellikler.kur_ek(v)          # tekrar/butce/cek/puantaj/fis/gorev/kullanici/oturum tabloları
    ornek_veri(v)
    ornek_harcama(v)
    ozellikler.ornek_ek(v)
    if ag_zorla:
        ozellikler.ek_yaz({"lan": True})
    otomatik = ozellikler.tekrar_uygula(v)
    sayilar = {t: v.execute("SELECT COUNT(*) c FROM %s" % t).fetchone()["c"] for t in TABLOLAR}
    print("=" * 62)
    print("  ÜSTAD MUHASEBE · yerel sunucu v%s" % SURUM)
    print("  Panel : http://127.0.0.1:%d" % port)
    print("  Veri  : %s" % DB)
    print("  Kayıt : " + " · ".join("%s=%d" % (k, n) for k, n in sayilar.items()))
    if otomatik:
        print("  Tekrarlayan kayıtlar işlendi: %d" % len(otomatik))
    ek = ozellikler.ek_oku()
    if ek.get("lan"):
        print("  Yerel ağ : " + ", ".join("http://%s:%d" % (a, port) for a in ozellikler.lan_adresleri()))
    print("=" * 62)
    # otomatik yedek (akşam saatlerinde günde bir)
    threading.Thread(target=ozellikler.yedek_dongusu, daemon=True).start()
    bagli = "0.0.0.0" if ek.get("lan") else "127.0.0.1"
    with Sunucu((bagli, port), Isleyici) as s:
        s.serve_forever()


if __name__ == "__main__":
    main()
