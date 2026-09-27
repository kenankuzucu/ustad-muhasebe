# -*- coding: utf-8 -*-
"""
ÜSTAD MUHASEBE · ek özellikler modülü
Tekrarlayan kayıtlar · abonelikler · çek/senet · bütçe · KDV özeti · puantaj/avans/prim
fiş fotoğrafı · bildirimler · anomali · nakit akışı · yıl karnesi · mali müşavir paketi
kullanıcı + rol (PBKDF2) · otomatik yedek · AI asistan köprüsü · PDF köprüsü

Bu dosya ana sunucudan bağımsız durur; sunucu yalnızca şu iki kapıyı çağırır:
    ozellikler.get(isleyici, yol)   -> True dönerse yanıt verildi
    ozellikler.post(isleyici, yol, govde) -> True dönerse yanıt verildi
"""
import base64
import datetime
import hashlib
import hmac
import json
import os
import shutil
import socket
import sqlite3
import threading
import time
import urllib.parse
import zipfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(KOK, "veri")
PANEL = os.path.join(KOK, "panel")
CIKTI = os.path.join(KOK, "cikti")
YEDEK = os.path.join(KOK, "yedek")
FISLER = os.path.join(VERI, "fisler")
DB = os.path.join(VERI, "muhasebe.db")
EK_AYAR = os.path.join(VERI, "ek.json")

for k in (FISLER,):
    os.makedirs(k, exist_ok=True)

SEMA = """
CREATE TABLE IF NOT EXISTS tekrar(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad TEXT, tur TEXT DEFAULT 'gider', kategori TEXT, aciklama TEXT,
  tutar REAL DEFAULT 0, siklik TEXT DEFAULT 'Aylik', gun INTEGER DEFAULT 1,
  hesap_id INTEGER, defter TEXT DEFAULT 'kurumsal', abonelik INTEGER DEFAULT 0,
  baslangic TEXT, son_uygulama TEXT, aktif INTEGER DEFAULT 1, olusturma TEXT);
CREATE TABLE IF NOT EXISTS butce(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kategori TEXT, defter TEXT DEFAULT 'sade', tutar REAL DEFAULT 0,
  donem TEXT DEFAULT 'Aylik', uyari_yuzde INTEGER DEFAULT 80,
  aktif INTEGER DEFAULT 1, olusturma TEXT);
CREATE TABLE IF NOT EXISTS cek(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tur TEXT DEFAULT 'Çek', yon TEXT DEFAULT 'Alınan', no TEXT, cari_id INTEGER,
  banka TEXT, tutar REAL DEFAULT 0, kesim TEXT, vade TEXT,
  durum TEXT DEFAULT 'Portföyde', aciklama TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS puantaj(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  personel_id INTEGER, tarih TEXT, tur TEXT DEFAULT 'Avans',
  tutar REAL DEFAULT 0, gun REAL DEFAULT 0, aciklama TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS kullanici(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad TEXT UNIQUE, sifre_hash TEXT, tuz TEXT, rol TEXT DEFAULT 'kasiyer',
  aktif INTEGER DEFAULT 1, son_giris TEXT, olusturma TEXT);
CREATE TABLE IF NOT EXISTS oturum(
  token TEXT PRIMARY KEY, kullanici_id INTEGER, rol TEXT, zaman TEXT, son TEXT);
CREATE TABLE IF NOT EXISTS fis(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarih TEXT, dosya TEXT, tutar REAL DEFAULT 0, kategori TEXT, aciklama TEXT,
  durum TEXT DEFAULT 'Bekliyor', olusturma TEXT);
CREATE TABLE IF NOT EXISTS gorev(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarih TEXT, baslik TEXT, detay TEXT, oncelik TEXT DEFAULT 'Normal',
  durum TEXT DEFAULT 'Açık', olusturma TEXT);
"""

YENI_TABLOLAR = ["tekrar", "butce", "cek", "puantaj", "fis", "gorev", "kullanici"]

ROLLER = {"yonetici": "Yönetici", "kasiyer": "Kasiyer", "misafir": "Misafir"}
# hangi uç hangi rolü ister (yazma uçları)
YONETICI_UC = ("/api/ayar", "/api/yedek/geri", "/api/yedek/al", "/api/sil", "/api/kullanici",
               "/api/yedek-oto", "/api/ai/anahtar", "/api/disa-aktar", "/api/musavir-paketi")
YAZMA_UCLARI = ("/api/kaydet", "/api/tekrar", "/api/butce", "/api/cek", "/api/puantaj",
                "/api/fis", "/api/ai/sor", "/api/gorev")


# ------------------------------------------------------------------ yardımcılar
def baglan():
    v = sqlite3.connect(DB, timeout=15)
    v.row_factory = sqlite3.Row
    v.execute("PRAGMA journal_mode=WAL")
    return v


def bugun():
    return datetime.date.today().isoformat()


def simdi():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def kur_ek(v):
    v.executescript(SEMA)


def ek_oku():
    try:
        with open(EK_AYAR, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"oto_yedek": True, "ai_model": "gemini-2.0-flash", "renk": "tatli", "lan": False}


def ek_yaz(d):
    a = ek_oku()
    a.update(d or {})
    with open(EK_AYAR, "w", encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=2)
    return a


def yaz_log(v, islem, detay=""):
    try:
        v.execute("INSERT INTO log(zaman,kullanici,islem,detay) VALUES(?,?,?,?)",
                  (simdi(), "sistem", islem, detay))
        v.commit()
    except Exception:
        pass


# ------------------------------------------------------------------ şifre / rol
def tuz_uret():
    return base64.b16encode(os.urandom(8)).decode()


def sifre_hash(sifre, tuz, tur=200000):
    return hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz.encode("utf-8"), tur).hex()


def kullanici_kur(v, ad=None, sifre=None, rol="yonetici"):
    """Kullanıcıları kurar. Sıfırdan: kenan=kenan1981 (yönetici), misafir=misafir2026 (misafir),
    kasa=kasa2026 (kasiyer: silme yetkisi yok)."""
    varsayilan = [("kenan", "kenan1981", "yonetici"), ("kasa", "kasa2026", "kasiyer"),
                  ("misafir", "misafir2026", "misafir")]
    if ad:
        varsayilan = [(ad, sifre, rol)]
    for a, s, r in varsayilan:
        var = v.execute("SELECT id FROM kullanici WHERE ad=?", (a,)).fetchone()
        if var:
            continue
        t = tuz_uret()
        v.execute("INSERT INTO kullanici(ad,sifre_hash,tuz,rol,aktif,olusturma) VALUES(?,?,?,?,1,?)",
                  (a, sifre_hash(s, t), t, r, simdi()))
    v.commit()


def giris_yap(v, ad, sifre):
    k = v.execute("SELECT * FROM kullanici WHERE ad=? AND aktif=1", (ad or "",)).fetchone()
    if not k:
        return None
    if not hmac.compare_digest(k["sifre_hash"], sifre_hash(sifre or "", k["tuz"])):
        return None
    token = base64.b32encode(os.urandom(20)).decode()
    v.execute("INSERT OR REPLACE INTO oturum(token,kullanici_id,rol,zaman,son) VALUES(?,?,?,?,?)",
              (token, k["id"], k["rol"], simdi(), simdi()))
    v.execute("UPDATE kullanici SET son_giris=? WHERE id=?", (simdi(), k["id"]))
    v.commit()
    return {"token": token, "ad": k["ad"], "rol": k["rol"], "rol_ad": ROLLER.get(k["rol"], k["rol"])}


def oturum_bul(v, token):
    if not token:
        return None
    o = v.execute("SELECT * FROM oturum WHERE token=?", (token,)).fetchone()
    if not o:
        return None
    v.execute("UPDATE oturum SET son=? WHERE token=?", (simdi(), token))
    v.commit()
    return dict(o)


def rol_bul(isleyici, v):
    """İstek hangi rolle geliyor? Kullanıcı tablosu boşsa eski davranış: tam yetki."""
    if not v.execute("SELECT COUNT(*) c FROM kullanici").fetchone()["c"]:
        return "yonetici"
    token = isleyici.headers.get("X-Oturum") or isleyici.headers.get("x-oturum")
    o = oturum_bul(v, token)
    return o["rol"] if o else ""


def yetki(isleyici, v, ys, yazma=False):
    """(True, rol) / (False, mesaj)"""
    rol = rol_bul(isleyici, v)
    if rol == "yonetici":
        return True, rol
    if not rol:
        return False, "oturum yok — tekrar giriş yap"
    if any(ys.startswith(u) for u in YONETICI_UC):
        return False, "bu işlem için yönetici yetkisi gerekir"
    if yazma and rol == "misafir":
        return False, "misafir hesabı sadece görüntüler"
    return True, rol


# ------------------------------------------------------------------ hesaplar
def tekrar_uygula(v, ay_sonuna_kadar=False):
    """Vadesi gelmiş tekrarlayan kayıtları gelir_gider'e yazar. Kaç kayıt yazıldığını döndürür."""
    bug = datetime.date.today()
    yazilan = []
    for t in v.execute("SELECT * FROM tekrar WHERE aktif=1").fetchall():
        try:
            son = datetime.date.fromisoformat(t["son_uygulama"]) if t["son_uygulama"] else None
            bas = datetime.date.fromisoformat(t["baslangic"] or bug.isoformat())
        except Exception:
            son, bas = None, bug
        hedef = None
        if son is None:
            hedef = bas if bas <= bug else None
        else:
            if t["siklik"] == "Haftalik":
                hedef = son + datetime.timedelta(days=7)
            elif t["siklik"] == "Yillik":
                hedef = son.replace(year=son.year + 1) if son.month == bug.month else None
            else:  # Aylik
                y, m = son.year, son.month + 1
                if m > 12:
                    y, m = y + 1, 1
                g = min(int(t["gun"] or 1), 28)
                hedef = datetime.date(y, m, g)
        # ilk ay için gün düzeltmesi
        if son is None and hedef:
            hedef = hedef.replace(day=min(int(t["gun"] or 1), 28))
        if not hedef or hedef > bug:
            continue
        while hedef <= bug:
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,hesap_id,tekrarlayan,defter,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (hedef.isoformat(), t["tur"], t["kategori"], "%s (otomatik)" % (t["aciklama"] or t["ad"]),
                       t["tutar"], t["hesap_id"], "evet", t["defter"] or "kurumsal", simdi()))
            if t["hesap_id"]:
                v.execute("""INSERT INTO kasa_hareket(hesap_id,tarih,tur,tutar,aciklama,kategori,olusturma)
                             VALUES(?,?,?,?,?,?,?)""",
                          (t["hesap_id"], hedef.isoformat(), "giriş" if t["tur"] == "gelir" else "çıkış",
                           t["tutar"], "%s (otomatik)" % (t["aciklama"] or t["ad"]), t["kategori"], simdi()))
            yazilan.append(t["ad"])
            if t["siklik"] == "Haftalik":
                hedef += datetime.timedelta(days=7)
            elif t["siklik"] == "Yillik":
                hedef = hedef.replace(year=hedef.year + 1)
            else:
                y, m = hedef.year, hedef.month + 1
                if m > 12:
                    y, m = y + 1, 1
                hedef = datetime.date(y, m, min(int(t["gun"] or 1), 28))
        v.execute("UPDATE tekrar SET son_uygulama=? WHERE id=?", (bug.isoformat(), t["id"]))
    v.commit()
    return yazilan


def butce_durum(v, ay=None):
    ay = ay or datetime.date.today().strftime("%Y-%m")
    out = []
    for b in v.execute("SELECT * FROM butce WHERE aktif=1").fetchall():
        kosul = "substr(tarih,1,7)=? AND tur='gider'"
        arg = [ay]
        if b["defter"]:
            kosul += " AND defter=?"
            arg.append(b["defter"])
        if b["kategori"] and b["kategori"] != "TÜMÜ":
            kosul += " AND kategori=?"
            arg.append(b["kategori"])
        r = v.execute("SELECT COALESCE(SUM(tutar),0) s FROM gelir_gider WHERE " + kosul, arg).fetchone()
        harcanan = r["s"] or 0
        oran = (harcanan / b["tutar"] * 100) if b["tutar"] else 0
        out.append({**dict(b), "harcanan": harcanan, "kalan": (b["tutar"] or 0) - harcanan,
                    "oran": round(oran, 1),
                    "durum": "aşıldı" if oran > 100 else ("uyarı" if oran >= (b["uyari_yuzde"] or 80) else "normal")})
    return out


def kdv_ozet(v, yil=None, ay=None):
    bug = datetime.date.today()
    yil = int(yil or bug.year)
    ay = int(ay or bug.month)
    bas = datetime.date(yil, ay, 1)
    bit = (datetime.date(yil + (1 if ay == 12 else 0), 1 if ay == 12 else ay + 1, 1) - datetime.timedelta(days=1))
    def f(kosul, arg=None):
        return v.execute("SELECT COALESCE(SUM(kdv),0) s FROM fatura WHERE " + kosul, arg or []).fetchone()["s"] or 0
    s_ay = "%04d-%02d" % (yil, ay)
    hesaplanan = f("tur='Satış' AND substr(tarih,1,7)=?", [s_ay])
    indirilecek = f("tur='Alış' AND substr(tarih,1,7)=?", [s_ay])
    onceki = v.execute("SELECT * FROM log WHERE islem='kdv-devreden' ORDER BY id DESC LIMIT 1").fetchone()
    devreden = 0.0
    if onceki:
        try:
            devreden = float(json.loads(onceki["detay"]).get("tutar", 0))
        except Exception:
            devreden = 0.0
    odenecek = hesaplanan - indirilecek - devreden
    return {"yil": yil, "ay": ay, "bas": bas.isoformat(), "bit": bit.isoformat(),
            "hesaplanan_kdv": hesaplanan, "indirilecek_kdv": indirilecek, "devreden_kdv": devreden,
            "odenecek": odenecek if odenecek > 0 else 0.0,
            "sonraki_devreden": abs(odenecek) if odenecek < 0 else 0.0,
            "satis_fatura": v.execute("SELECT COUNT(*) c FROM fatura WHERE tur='Satış' AND substr(tarih,1,7)=?", [s_ay]).fetchone()["c"],
            "alis_fatura": v.execute("SELECT COUNT(*) c FROM fatura WHERE tur='Alış' AND substr(tarih,1,7)=?", [s_ay]).fetchone()["c"]}


def anomali(v, defter="sade"):
    """Bu ay ile geçen ayı kategori bazında karşılaştır; %35+ artışları uyarı olarak döndür."""
    b1 = datetime.date.today().strftime("%Y-%m")
    ilk = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    b0 = ilk.strftime("%Y-%m")
    out = []
    kats = [r["kategori"] for r in v.execute(
        "SELECT DISTINCT kategori FROM gelir_gider WHERE substr(tarih,1,7) IN (?,?)", (b1, b0)).fetchall()]
    for k in kats:
        def t(ay):
            return v.execute("""SELECT COALESCE(SUM(tutar),0) s, COUNT(*) c FROM gelir_gider
                                WHERE substr(tarih,1,7)=? AND kategori=? AND tur='gider'""",
                             (ay, k)).fetchone()
        a, g = t(b1), t(b0)
        if not g["s"]:
            continue
        fark = (a["s"] - g["s"]) / g["s"] * 100
        if fark >= 35:
            out.append({"kategori": k, "bu_ay": a["s"], "gecen_ay": g["s"], "fark_yuzde": round(fark, 1),
                        "adet": a["c"], "seviye": "yüksek" if fark >= 80 else "orta"})
    return sorted(out, key=lambda x: -x["fark_yuzde"])


def nakit_akis(v, ay=3):
    """Önümüzdeki N ayın kasa projeksiyonu: tekrarlayanlar + ortalama günlük + vadesi gelen çekler/faturalar."""
    bug = datetime.date.today()
    kasa = sum((r["acilis"] or 0) + hesap_net(v, r["id"])
               for r in v.execute("SELECT * FROM hesap WHERE aktif=1").fetchall())
    # son 60 günün ortalaması (sade + kurumsal gider)
    ort = v.execute("""SELECT COALESCE(AVG(g),0) o FROM (
        SELECT substr(tarih,1,10) t, SUM(tutar) g FROM gelir_gider
        WHERE tur='gider' AND tarih >= ? GROUP BY substr(tarih,1,10))""",
                    ((bug - datetime.timedelta(days=60)).isoformat(),)).fetchone()["o"] or 0
    ort_gelir = v.execute("""SELECT COALESCE(AVG(g),0) o FROM (
        SELECT substr(tarih,1,10) t, SUM(tutar) g FROM gelir_gider
        WHERE tur='gelir' AND tarih >= ? GROUP BY substr(tarih,1,10))""",
                          ((bug - datetime.timedelta(days=60)).isoformat(),)).fetchone()["o"] or 0
    seri, kalan = [], kasa
    for i in range(int(ay)):
        bas = (bug.replace(day=1) + datetime.timedelta(days=32 * i)).replace(day=1)
        son = (bas + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        tekr = v.execute("""SELECT tur, COALESCE(SUM(tutar),0) s FROM tekrar
                            WHERE aktif=1 AND siklik='Aylik' GROUP BY tur""").fetchall()
        tg = sum(r["s"] for r in tekr if r["tur"] == "gelir")
        ts = sum(r["s"] for r in tekr if r["tur"] == "gider")
        cekler = v.execute("""SELECT COALESCE(SUM(tutar),0) s FROM cek
                              WHERE yon='Verilen' AND durum IN ('Portföyde','Verildi','Ödenecek')
                              AND vade BETWEEN ? AND ?""", (bas.isoformat(), son.isoformat())).fetchone()["s"] or 0
        cek_gel = v.execute("""SELECT COALESCE(SUM(tutar),0) s FROM cek
                               WHERE yon='Alınan' AND durum IN ('Portföyde','Tahsil')
                               AND vade BETWEEN ? AND ?""", (bas.isoformat(), son.isoformat())).fetchone()["s"] or 0
        gun = (son - bas).days + 1
        gelir = tg + ort_gelir * gun
        gider = ts + ort * gun + cekler
        tahsil = v.execute("""SELECT COALESCE(SUM(toplam - tahsil),0) s FROM fatura
                              WHERE tur='Satış' AND durum IN ('Bekliyor','Kısmi')
                              AND vade BETWEEN ? AND ?""", (bas.isoformat(), son.isoformat())).fetchone()["s"] or 0
        net = gelir + cek_gel + tahsil - gider
        kalan += net
        seri.append({"ay": bas.strftime("%Y-%m"), "ad": AYLAR[bas.month - 1], "gelir": round(gelir, 2),
                     "gider": round(gider, 2), "cek_verilen": cekler, "cek_alinan": cek_gel,
                     "tahsilat": tahsil, "net": round(net, 2), "kasa_sonu": round(kalan, 2)})
    return {"baslangic_kasa": round(kasa, 2), "seri": seri,
            "gunluk_ort_gelir": round(ort_gelir, 2), "gunluk_ort_gider": round(ort, 2)}


AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos",
         "Eylül", "Ekim", "Kasım", "Aralık"]


def hesap_net(v, hesap_id):
    r = v.execute("""SELECT COALESCE(SUM(CASE WHEN tur='giriş' THEN tutar ELSE -tutar END),0) s
                     FROM kasa_hareket WHERE hesap_id=?""", (hesap_id,)).fetchone()
    return r["s"] or 0


def karne(v, yil=None):
    yil = int(yil or datetime.date.today().year)
    def s(kosul, arg=None):
        return v.execute("SELECT COALESCE(SUM(tutar),0) s FROM gelir_gider WHERE " + kosul,
                         arg or []).fetchone()["s"] or 0
    gelir = s("tur='gelir' AND substr(tarih,1,4)=?", [str(yil)])
    gider = s("tur='gider' AND substr(tarih,1,4)=?", [str(yil)])
    aylik = []
    for m in range(1, 13):
        ay = "%04d-%02d" % (yil, m)
        g = s("tur='gelir' AND substr(tarih,1,7)=?", [ay])
        h = s("tur='gider' AND substr(tarih,1,7)=?", [ay])
        aylik.append({"ay": AYLAR[m - 1], "gelir": g, "gider": h, "net": g - h})
    kats = [dict(r) for r in v.execute("""SELECT kategori, SUM(tutar) tutar, COUNT(*) adet FROM gelir_gider
        WHERE tur='gider' AND substr(tarih,1,4)=? GROUP BY kategori ORDER BY tutar DESC LIMIT 10""",
                                       [str(yil)]).fetchall()]
    cariler = [dict(r) for r in v.execute("""SELECT unvan, SUM(borc)-SUM(alacak) bakiye FROM hareket
        JOIN cari ON cari.id=hareket.cari_id GROUP BY cari_id ORDER BY bakiye DESC LIMIT 8""").fetchall()]
    return {"yil": yil, "gelir": gelir, "gider": gider, "net": gelir - gider, "aylik": aylik,
            "kategoriler": kats, "cariler": cariler,
            "en_iyi_ay": max(aylik, key=lambda x: x["net"])["ay"] if aylik else "-",
            "en_kotu_ay": min(aylik, key=lambda x: x["net"])["ay"] if aylik else "-",
            "kayit": v.execute("SELECT COUNT(*) c FROM gelir_gider WHERE substr(tarih,1,4)=?", [str(yil)]).fetchone()["c"]}


def bildirimler(v):
    """Uyarı listesi: vadesi geçen fatura/çek, bütçe aşımı, kasa eksiye düşme, kritik stok."""
    bug = bugun()
    out = []
    for f in v.execute("""SELECT * FROM fatura WHERE durum IN ('Bekliyor','Kısmi') AND vade < ?
                          ORDER BY vade LIMIT 12""", (bug,)).fetchall():
        out.append({"tur": "fatura", "seviye": "kırmızı", "id": f["id"],
                    "baslik": "Vadesi geçen fatura %s" % (f["no"] or ""),
                    "mesaj": "%s · %s · kalan %.2f ₺" % (f["tur"], f["vade"], (f["toplam"] or 0) - (f["tahsil"] or 0))})
    for c in v.execute("""SELECT * FROM cek WHERE durum IN ('Portföyde','Verildi','Ödenecek') AND vade < ?
                          ORDER BY vade LIMIT 12""", (bug,)).fetchall():
        out.append({"tur": "cek", "seviye": "kırmızı", "id": c["id"],
                    "baslik": "%s vadesi geçti (%s)" % (c["tur"], c["no"] or ""),
                    "mesaj": "%s · %s · %.2f ₺" % (c["yon"], c["vade"], c["tutar"])})
    for c in v.execute("""SELECT * FROM cek WHERE durum IN ('Portföyde','Verildi','Ödenecek')
                          AND vade BETWEEN ? AND date(?, '+7 day') ORDER BY vade LIMIT 12""", (bug, bug)).fetchall():
        out.append({"tur": "cek", "seviye": "altın", "id": c["id"],
                    "baslik": "Vadesi yaklaşan %s (%s)" % (c["tur"], c["no"] or ""),
                    "mesaj": "%s · %s · %.2f ₺" % (c["yon"], c["vade"], c["tutar"])})
    for b in butce_durum(v):
        if b["durum"] in ("uyarı", "aşıldı"):
            out.append({"tur": "butce", "seviye": "kırmızı" if b["durum"] == "aşıldı" else "altın",
                        "id": b["id"], "baslik": "Bütçe %s: %s" % (b["durum"], b["kategori"] or "TÜMÜ"),
                        "mesaj": "%.2f / %.2f ₺ (%%%.1f)" % (b["harcanan"], b["tutar"], b["oran"])})
    for h in v.execute("SELECT * FROM hesap WHERE aktif=1").fetchall():
        net = (h["acilis"] or 0) + hesap_net(v, h["id"])
        if net < 0:
            out.append({"tur": "kasa", "seviye": "kırmızı", "id": h["id"],
                        "baslik": "Hesap ekside: %s" % h["ad"], "mesaj": "%.2f ₺" % net})
    for s in v.execute("SELECT * FROM stok WHERE aktif=1 AND miktar <= kritik").fetchall():
        out.append({"tur": "stok", "seviye": "altın", "id": s["id"],
                    "baslik": "Kritik stok: %s" % s["ad"],
                    "mesaj": "%.1f %s kaldı (kritik %.1f)" % (s["miktar"], s["birim"], s["kritik"])})
    return out


def lan_adresleri():
    out = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        out.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for a in socket.gethostbyname_ex(socket.gethostname())[2]:
            if a not in out and not a.startswith("127."):
                out.append(a)
    except Exception:
        pass
    return out


# ------------------------------------------------------------------ dosya indirme
def indir(isleyici, yol, ad=None, tur="application/octet-stream"):
    if not os.path.exists(yol):
        return isleyici.yolla({"hata": "dosya yok"}, 404)
    ad = ad or os.path.basename(yol)
    boyut = os.path.getsize(yol)
    try:
        isleyici.send_response(200)
        isleyici.send_header("Content-Type", tur)
        isleyici.send_header("Content-Length", str(boyut))
        isleyici.send_header("Cache-Control", "no-store")
        isleyici.send_header("Content-Disposition",
                             "attachment; filename=\"%s\"; filename*=UTF-8''%s" % (
                                 ad.encode("ascii", "ignore").decode() or "dosya",
                                 urllib.parse.quote(ad)))
        isleyici.end_headers()
        with open(yol, "rb") as f:
            shutil.copyfileobj(f, isleyici.wfile)
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        isleyici.close_connection = True
    return True


# ------------------------------------------------------------------ AI köprüsü
def ai_modulu():
    try:
        import ai_asistan  # noqa
        return ai_asistan
    except Exception:
        return None


def pdf_modulu():
    try:
        import pdf_rapor  # noqa
        return pdf_rapor
    except Exception:
        return None


def pdf_uret(isleyici, kaynak, tur="xlsx"):
    """Önce Word üretir, sonra Word COM ile gerçek PDF'e çevirir."""
    pr = pdf_modulu()
    if not pr:
        return isleyici.yolla({"hata": "PDF modülü (pdf_rapor.py) bulunamadı"}, 500)
    s = dict(isleyici.sorgu())
    s["kaynak"] = kaynak
    yol, ad, mime = isleyici.ektar_dosya(s, "docx")
    pdf = os.path.splitext(yol)[0] + ".pdf"
    sonuc = pr.pdf_uret(yol, pdf)
    if not sonuc.get("tamam"):
        return isleyici.yolla({"hata": "PDF'e çevrilemedi: %s" % sonuc.get("hata", "bilinmeyen hata"),
                               "word": os.path.basename(yol)}, 500)
    v = baglan()
    yaz_log(v, "pdf", "%s (%s sayfa, %s bayt)" % (os.path.basename(pdf), sonuc.get("sayfa", "?"),
                                                  sonuc.get("boyut", "?")))
    v.commit()
    v.close()
    return indir(isleyici, pdf, os.path.basename(pdf), "application/pdf")


# ------------------------------------------------------------------ GET
def get(isleyici, ys):
    v = baglan()
    s = isleyici.sorgu()
    try:
        if ys == "/api/tekrar":
            kayit = [dict(r) for r in v.execute("SELECT * FROM tekrar ORDER BY ad").fetchall()]
            return isleyici.yolla({"kayit": kayit, "adet": len(kayit),
                                   "aylik_gelir": sum(x["tutar"] for x in kayit if x["tur"] == "gelir" and x["aktif"]),
                                   "aylik_gider": sum(x["tutar"] for x in kayit if x["tur"] == "gider" and x["aktif"]),
                                   "yillik_yuk": sum(x["tutar"] * (12 if x["siklik"] == "Aylik" else (52 if x["siklik"] == "Haftalik" else 1))
                                                     for x in kayit if x["tur"] == "gider" and x["aktif"])})
        if ys == "/api/butce":
            return isleyici.yolla({"kayit": butce_durum(v, s.get("ay")),
                                   "toplam_butce": sum(b["tutar"] for b in butce_durum(v, s.get("ay"))),
                                   "toplam_harcanan": sum(b["harcanan"] for b in butce_durum(v, s.get("ay")))})
        if ys == "/api/cek":
            kayit = [dict(r) for r in v.execute("""SELECT cek.*, cari.unvan FROM cek
                                                   LEFT JOIN cari ON cari.id=cek.cari_id
                                                   ORDER BY vade""").fetchall()]
            bug = bugun()
            return isleyici.yolla({
                "kayit": kayit,
                "alinan_portfoy": sum(x["tutar"] for x in kayit if x["yon"] == "Alınan" and x["durum"] in ("Portföyde", "Tahsil")),
                "verilen_portfoy": sum(x["tutar"] for x in kayit if x["yon"] == "Verilen" and x["durum"] not in ("Ödendi", "İptal")),
                "vadesi_gecen": [x for x in kayit if x["vade"] and x["vade"] < bug and x["durum"] not in ("Ödendi", "Tahsil", "İptal")],
                "yaklasan": [x for x in kayit if x["vade"] and bug <= x["vade"] <= (
                    datetime.date.today() + datetime.timedelta(days=30)).isoformat() and x["durum"] not in ("Ödendi", "Tahsil", "İptal")]})
        if ys == "/api/puantaj":
            pid = s.get("personel_id")
            kosul, arg = "", []
            if pid:
                kosul, arg = " WHERE puantaj.personel_id=?", [pid]
            kayit = [dict(r) for r in v.execute("""SELECT puantaj.*, personel.ad FROM puantaj
                        LEFT JOIN personel ON personel.id=puantaj.personel_id""" + kosul + " ORDER BY tarih DESC",
                                                arg).fetchall()]
            return isleyici.yolla({"kayit": kayit,
                                   "avans_toplam": sum(x["tutar"] for x in kayit if x["tur"] == "Avans"),
                                   "prim_toplam": sum(x["tutar"] for x in kayit if x["tur"] == "Prim"),
                                   "izin_gun": sum(x["gun"] for x in kayit if x["tur"] == "İzin")})
        if ys == "/api/kdv-ozet":
            return isleyici.yolla(kdv_ozet(v, s.get("yil"), s.get("ay")))
        if ys == "/api/anomali":
            return isleyici.yolla({"kayit": anomali(v, s.get("defter", "sade"))})
        if ys == "/api/nakit-akis":
            return isleyici.yolla(nakit_akis(v, int(s.get("ay", 3))))
        if ys == "/api/karne":
            return isleyici.yolla(karne(v, s.get("yil")))
        if ys == "/api/bildirim":
            return isleyici.yolla({"kayit": bildirimler(v)})
        if ys == "/api/fis":
            kayit = [dict(r) for r in v.execute("SELECT * FROM fis ORDER BY id DESC LIMIT 60").fetchall()]
            try:
                import shutil as _sh
                ocr = bool(_sh.which("tesseract"))
            except Exception:
                ocr = False
            return isleyici.yolla({"kayit": kayit, "ocr": ocr})
        if ys == "/api/gorev":
            return isleyici.yolla({"kayit": [dict(r) for r in v.execute(
                "SELECT * FROM gorev ORDER BY durum, tarih LIMIT 80").fetchall()]})
        if ys == "/api/ai/durum":
            m = ai_modulu()
            a = ek_oku()
            return isleyici.yolla({"modul": bool(m), "anahtar": bool(m and m.anahtar_oku()),
                                   "model": a.get("ai_model", "gemini-2.0-flash"),
                                   "mesaj": ("hazır" if (m and m.anahtar_oku()) else
                                             ("Gemini anahtarı gir" if m else "ai_asistan.py bulunamadı"))})
        if ys == "/api/lan":
            ek = ek_oku()
            adresler = lan_adresleri()
            return isleyici.yolla({"adresler": adresler, "port": isleyici.server.server_address[1],
                                   "acik": bool(ek.get("lan")), "telefon": "http://%s:%d" % (
                                       adresler[0] if adresler else "127.0.0.1", isleyici.server.server_address[1])})
        if ys == "/api/kullanici":
            return isleyici.yolla({"kayit": [{"id": r["id"], "ad": r["ad"], "rol": r["rol"],
                                              "rol_ad": ROLLER.get(r["rol"], r["rol"]), "aktif": r["aktif"],
                                              "son_giris": r["son_giris"]}
                                             for r in v.execute("SELECT * FROM kullanici ORDER BY id").fetchall()],
                                   "roller": ROLLER})
        if ys == "/api/pdf":
            return pdf_uret(isleyici, s.get("kaynak", "cari"))
        if ys == "/api/musavir-paketi":
            bas = s.get("bas") or (datetime.date.today().replace(day=1).isoformat())
            bit = s.get("bit") or bugun()
            izin, rol = yetki(isleyici, v, ys)
            if not izin:
                return isleyici.yolla({"tamam": False, "hata": rol or "yetki yok"}, 403)
            return musavir_paketi(isleyici, v, bas, bit)
        if ys == "/api/ek-ayar":
            return isleyici.yolla({"ayar": ek_oku()})
        if ys == "/api/yedek/oto":
            return isleyici.yolla({"ayar": ek_oku(), "yedekler": oto_yedek_listesi()})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return isleyici.yolla({"hata": "%s: %s" % (type(e).__name__, e)}, 500)
    finally:
        v.close()
    return False


def oto_yedek_listesi():
    out = []
    if os.path.isdir(YEDEK):
        for ad in sorted(os.listdir(YEDEK), reverse=True):
            if ad.startswith("oto-"):
                p = os.path.join(YEDEK, ad)
                out.append({"ad": ad, "boyut": os.path.getsize(p),
                            "zaman": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d.%m.%Y %H:%M")})
    return out[:20]


def musavir_paketi(isleyici, v, bas, bit):
    ad = "mali-musavir-%s_%s.zip" % (bas.replace("-", ""), bit.replace("-", ""))
    yol = os.path.join(CIKTI, ad)
    ks, args = [], []
    try:
        from disa_aktar import xlsx, docx
    except Exception:
        xlsx = docx = None
    def tablo_ver(tablo, kosul, arg):
        return v.execute("SELECT * FROM %s WHERE %s" % (tablo, kosul), arg).fetchall()
    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
        # ham CSV'ler (Excel'de açılır, BOM'lu)
        for tablo, kosul, arg in [("fatura", "tarih BETWEEN ? AND ?", [bas, bit]),
                                  ("fatura_kalem", "fatura_id IN (SELECT id FROM fatura WHERE tarih BETWEEN ? AND ?)", [bas, bit]),
                                  ("gelir_gider", "tarih BETWEEN ? AND ?", [bas, bit]),
                                  ("kasa_hareket", "tarih BETWEEN ? AND ?", [bas, bit]),
                                  ("hareket", "tarih BETWEEN ? AND ?", [bas, bit]),
                                  ("cek", "vade BETWEEN ? AND ?", [bas, bit]),
                                  ("stok", "1=1", []), ("cari", "1=1", []), ("personel", "1=1", [])]:
            rs = tablo_ver(tablo, kosul, arg)
            basliklar = (list(rs[0].keys()) if rs else
                         [c[1] for c in v.execute("SELECT * FROM %s LIMIT 0" % tablo).description])
            satirlar = [",".join(basliklar)]
            for r in rs:
                satirlar.append(",".join('"%s"' % str(x).replace('"', "'") for x in tuple(r)))
            z.writestr("%s.csv" % tablo, "\ufeff" + "\n".join(satirlar))
        # KDV özeti
        try:
            k = kdv_ozet(v, int(bit[:4]), int(bit[5:7]))
            z.writestr("kdv-ozeti.txt", "\n".join("%s: %s" % (a, b) for a, b in k.items()))
        except Exception:
            pass
        z.writestr("OKU.txt", "ÜSTAD MUHASEBE mali müşavir paketi\nDönem: %s - %s\nÜretim: %s\n\n"
                              "İçerik: fatura, fatura kalemleri, gelir/gider, kasa, cari hareket, çek/senet,\n"
                              "stok, cari kartlar, personel (CSV) + KDV özeti.\n" % (bas, bit, simdi()))
    yaz_log(v, "musavir-paketi", ad)
    v.commit()
    return indir(isleyici, yol, ad, "application/zip")


# ------------------------------------------------------------------ POST
def post(isleyici, ys, g):
    v = baglan()
    try:
        # --- giriş (yeni: kullanıcı tablosu + token)
        if ys == "/api/giris2":
            s = giris_yap(v, g.get("kullanici"), g.get("sifre"))
            yaz_log(v, "giris", "%s -> %s" % (g.get("kullanici"), "başarılı" if s else "hatalı"))
            if not s:
                return isleyici.yolla({"tamam": False, "hata": "kullanıcı adı veya şifre hatalı"}, 401)
            return isleyici.yolla({"tamam": True, **s})
        if ys == "/api/cikis":
            v.execute("DELETE FROM oturum WHERE token=?", (g.get("token") or "",))
            v.commit()
            return isleyici.yolla({"tamam": True})

        # --- yetki
        yazma = ys.endswith("/kaydet") or ys in ("/api/sil", "/api/tekrar/uygula", "/api/fis/yukle",
                                                 "/api/ai/sor", "/api/yedek/al", "/api/yedek/geri", "/api/ayar")
        ok, rol = yetki(isleyici, v, ys, yazma)
        if not ok:
            yaz_log(v, "yetkisiz", "%s (%s)" % (ys, rol or "oturumsuz"))
            v.commit()
            return isleyici.yolla({"tamam": False, "hata": rol or "yetki yok"}, 403)

        tablo = {
            "/api/tekrar/kaydet": ("tekrar", ["ad", "tur", "kategori", "aciklama", "tutar", "siklik",
                                              "gun", "hesap_id", "defter", "abonelik", "baslangic", "aktif"]),
            "/api/butce/kaydet": ("butce", ["kategori", "defter", "tutar", "donem", "uyari_yuzde", "aktif"]),
            "/api/cek/kaydet": ("cek", ["tur", "yon", "no", "cari_id", "banka", "tutar", "kesim", "vade",
                                        "durum", "aciklama"]),
            "/api/puantaj/kaydet": ("puantaj", ["personel_id", "tarih", "tur", "tutar", "gun", "aciklama"]),
            "/api/gorev/kaydet": ("gorev", ["tarih", "baslik", "detay", "oncelik", "durum"]),
            "/api/fis/kaydet": ("fis", ["tarih", "tutar", "kategori", "aciklama", "durum"]),
        }
        if ys in tablo:
            t, alanlar = tablo[ys]
            kid = kaydet(v, t, alanlar, g)
            yaz_log(v, "kaydet", "%s #%s (%s)" % (t, kid, rol))
            v.commit()
            return isleyici.yolla({"tamam": True, "id": kid})
        if ys == "/api/tekrar/uygula":
            yazilan = tekrar_uygula(v)
            return isleyici.yolla({"tamam": True, "yazilan": yazilan, "adet": len(yazilan)})
        if ys == "/api/kullanici/kaydet":
            ad = (g.get("ad") or "").strip()
            if not ad:
                return isleyici.yolla({"hata": "ad gerekli"}, 400)
            mevcut = v.execute("SELECT * FROM kullanici WHERE ad=?", (ad,)).fetchone()
            if mevcut:
                if g.get("sifre"):
                    t = tuz_uret()
                    v.execute("UPDATE kullanici SET sifre_hash=?,tuz=?,rol=?,aktif=? WHERE ad=?",
                              (sifre_hash(g["sifre"], t), t, g.get("rol", mevcut["rol"]),
                               1 if g.get("aktif", 1) else 0, ad))
                else:
                    v.execute("UPDATE kullanici SET rol=?,aktif=? WHERE ad=?",
                              (g.get("rol", mevcut["rol"]), 1 if g.get("aktif", 1) else 0, ad))
                kid = mevcut["id"]
            else:
                if not g.get("sifre"):
                    return isleyici.yolla({"hata": "yeni kullanıcı için şifre gerekli"}, 400)
                t = tuz_uret()
                v.execute("INSERT INTO kullanici(ad,sifre_hash,tuz,rol,aktif,olusturma) VALUES(?,?,?,?,1,?)",
                          (ad, sifre_hash(g["sifre"], t), t, g.get("rol", "kasiyer"), simdi()))
                kid = v.execute("SELECT last_insert_rowid() i").fetchone()["i"]
            yaz_log(v, "kullanici", "%s (%s)" % (ad, g.get("rol", "")))
            v.commit()
            return isleyici.yolla({"tamam": True, "id": kid})
        if ys == "/api/ai/anahtar":
            m = ai_modulu()
            if not m:
                return isleyici.yolla({"hata": "ai_asistan.py yok"}, 500)
            a = (g.get("anahtar") or "").strip()
            if g.get("model"):
                ek_yaz({"ai_model": g["model"]})
            if not a:
                return isleyici.yolla({"tamam": False, "hata": "anahtar boş"})
            m.anahtar_kaydet(a)
            d = m.anahtar_gecerli_mi(a) if hasattr(m, "anahtar_gecerli_mi") else {"tamam": True}
            yaz_log(v, "ai-anahtar", "kaydedildi · geçerli=%s" % d.get("tamam"))
            v.commit()
            return isleyici.yolla({"tamam": bool(d.get("tamam")), "hata": d.get("hata", "")})
        if ys == "/api/ai/sor":
            m = ai_modulu()
            if not m:
                return isleyici.yolla({"hata": "ai_asistan.py bulunamadı"}, 500)
            baglam = muhasebe_baglami(v, g.get("baglam", "genel"))
            s = m.sor(g.get("soru", ""), baglam, model=ek_oku().get("ai_model", "gemini-2.0-flash"))
            return isleyici.yolla(s)
        if ys == "/api/fis/yukle":
            ad = g.get("ad") or ("fis-%s.jpg" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            ad = os.path.basename(ad)
            ham = g.get("veri") or ""
            if "," in ham:
                ham = ham.split(",", 1)[1]
            try:
                icerik = base64.b64decode(ham)
            except Exception:
                return isleyici.yolla({"hata": "görüntü çözülemedi"}, 400)
            yol = os.path.join(FISLER, ad)
            with open(yol, "wb") as f:
                f.write(icerik)
            # OCR var mı?
            import shutil as _sh
            okuma = ""
            if _sh.which("tesseract"):
                try:
                    import subprocess
                    okuma = subprocess.run(["tesseract", yol, "stdout", "-l", "tur+eng"],
                                           capture_output=True, text=True, timeout=40).stdout or ""
                except Exception:
                    okuma = ""
            v.execute("""INSERT INTO fis(tarih,dosya,tutar,kategori,aciklama,durum,olusturma)
                         VALUES(?,?,?,?,?,?,?)""",
                      (g.get("tarih") or bugun(), ad, sayi(g.get("tutar")), g.get("kategori"),
                       (g.get("aciklama") or "") + (" | OCR: " + okuma[:300] if okuma else ""),
                       "Bekliyor", simdi()))
            v.commit()
            return isleyici.yolla({"tamam": True, "dosya": ad, "boyut": len(icerik), "ocr": bool(okuma),
                                   "okuma": okuma[:400]})
        if ys == "/api/fis/isle":
            fid = g.get("id")
            f = v.execute("SELECT * FROM fis WHERE id=?", (fid,)).fetchone()
            if not f:
                return isleyici.yolla({"hata": "fiş yok"}, 404)
            v.execute("""INSERT INTO gelir_gider(tarih,tur,kategori,aciklama,tutar,defter,olusturma)
                         VALUES(?,?,?,?,?,?,?)""",
                      (f["tarih"], "gider", f["kategori"] or "Diğer", (f["aciklama"] or "Fiş")[:180],
                       f["tutar"] or 0, "sade", simdi()))
            v.execute("UPDATE fis SET durum='İşlendi' WHERE id=?", (fid,))
            v.commit()
            return isleyici.yolla({"tamam": True})
        if ys == "/api/yedek-oto":
            ek_yaz({"oto_yedek": bool(g.get("acik")), "oto_yedek_saat": int(g.get("saat", 20))})
            return isleyici.yolla({"tamam": True, "ayar": ek_oku()})
        if ys == "/api/kdv-devreden":
            yaz_log(v, "kdv-devreden", json.dumps({"tutar": sayi(g.get("tutar"))}))
            v.commit()
            return isleyici.yolla({"tamam": True})
        if ys == "/api/lan":
            ek_yaz({"lan": bool(g.get("acik"))})
            return isleyici.yolla({"tamam": True, "ayar": ek_oku()})
        if ys == "/api/renk":
            ek_yaz({"renk": g.get("renk"), "tema": g.get("tema")})
            return isleyici.yolla({"tamam": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return isleyici.yolla({"hata": "%s: %s" % (type(e).__name__, e)}, 500)
    finally:
        v.close()
    return False


def sayi(x, varsayilan=0.0):
    try:
        return float(str(x).replace(".", "").replace(",", ".")) if isinstance(x, str) and "," in str(x) else float(x or 0)
    except Exception:
        return varsayilan


def kaydet(v, tablo, alanlar, g):
    rid = g.get("id")
    deger = []
    for a in alanlar:
        x = g.get(a)
        if isinstance(x, str) and x.strip() == "":
            x = None
        deger.append(x)
    if rid:
        v.execute("UPDATE %s SET %s WHERE id=?" % (tablo, ",".join(a + "=?" for a in alanlar)), deger + [rid])
        return rid
    v.execute("INSERT INTO %s(%s,olusturma) VALUES(%s,?)" % (
        tablo, ",".join(alanlar), ",".join("?" * len(alanlar))), deger + [simdi()])
    return v.execute("SELECT last_insert_rowid() i").fetchone()["i"]


def muhasebe_baglami(v, tur="genel"):
    """AI'ya verilecek gerçek sayılar — uydurmasın diye yalnızca ölçülmüş veri."""
    bug = datetime.date.today()
    def s(kosul, arg=None):
        return v.execute("SELECT COALESCE(SUM(tutar),0) s FROM gelir_gider WHERE " + kosul, arg or []).fetchone()["s"] or 0
    g = s("tur='gelir' AND substr(tarih,1,7)=?", [bug.strftime("%Y-%m")])
    h = s("tur='gider' AND substr(tarih,1,7)=?", [bug.strftime("%Y-%m")])
    kasa = sum((r["acilis"] or 0) + hesap_net(v, r["id"]) for r in v.execute("SELECT * FROM hesap").fetchall())
    top_kat = v.execute("""SELECT kategori, SUM(tutar) t FROM gelir_gider WHERE tur='gider'
                           AND substr(tarih,1,7)=? GROUP BY kategori ORDER BY t DESC LIMIT 8""",
                        [bug.strftime("%Y-%m")]).fetchall()
    b = bildirimler(v)
    return "\n".join([
        "Dönem: %s (bugün %s)" % (bug.strftime("%Y-%m"), bug.isoformat()),
        "Bu ay gelir %.2f ₺, gider %.2f ₺, net %.2f ₺" % (g, h, g - h),
        "Kasa+banka toplamı %.2f ₺" % kasa,
        "En büyük gider kategorileri: " + ", ".join("%s %.2f ₺" % (r["kategori"], r["t"]) for r in top_kat),
        "Uyarılar: " + (", ".join(x["baslik"] for x in b[:8]) if b else "yok"),
        "Sade defter bu ay: gelir %.2f, gider %.2f" % (
            s("tur='gelir' AND substr(tarih,1,7)=? AND defter='sade'", [bug.strftime("%Y-%m")]),
            s("tur='gider' AND substr(tarih,1,7)=? AND defter='sade'", [bug.strftime("%Y-%m")])),
    ])


# ------------------------------------------------------------------ örnek veri
def ornek_ek(v):
    """Ek tablolara örnek veri (yalnızca boşsa)."""
    bug = datetime.date.today()
    def g(delta):
        return (bug + datetime.timedelta(days=delta)).isoformat()
    if not v.execute("SELECT COUNT(*) c FROM tekrar").fetchone()["c"]:
        hesap = {r["ad"]: r["id"] for r in v.execute("SELECT id, ad FROM hesap").fetchall()}
        banka = hesap.get("Ziraat Bankası") or (list(hesap.values())[0] if hesap else None)
        tekrarlar = [
            ("Dükkan Kirası", "gider", "Kira", "Selimiye Mah. dükkan kirası", 14000, "Aylik", 5, banka, "kurumsal", 0),
            ("Elektrik", "gider", "Elektrik & Su", "Elektrik faturası", 2400, "Aylik", 18, banka, "kurumsal", 1),
            ("Su", "gider", "Elektrik & Su", "Su faturası", 420, "Aylik", 22, banka, "kurumsal", 1),
            ("İnternet & Telefon", "gider", "İnternet & Telefon", "Fiber abonelik", 690, "Aylik", 20, banka, "kurumsal", 1),
            ("Personel Maaşı", "gider", "Personel", "Aylık maaş ödemesi", 17000, "Aylik", 1, banka, "kurumsal", 0),
            ("Kira Geliri", "gelir", "Kira Geliri", "Dükkan kira geliri", 8000, "Aylik", 10, banka, "kurumsal", 0),
            ("Muhasebeci Ücreti", "gider", "Vergi & Harç", "Serbest muhasebeci", 1500, "Aylik", 25, banka, "kurumsal", 1),
            ("Ev Kirası", "gider", "Kira", "Kişisel ev kirası", 12000, "Aylik", 1, None, "sade", 0),
            ("Netflix & Dijital", "gider", "Diğer", "Dijital abonelikler", 320, "Aylik", 12, None, "sade", 1),
        ]
        for ad, tur, kat, ack, tutar, sik, gun, hid, defter, abonelik in tekrarlar:
            v.execute("""INSERT INTO tekrar(ad,tur,kategori,aciklama,tutar,siklik,gun,hesap_id,defter,
                         abonelik,baslangic,son_uygulama,aktif,olusturma) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
                      (ad, tur, kat, ack, tutar, sik, gun, hid, defter, abonelik, bug.isoformat(),
                       bug.isoformat(), simdi()))
    if not v.execute("SELECT COUNT(*) c FROM butce").fetchone()["c"]:
        for kat, defter, tutar, uyari in [("TÜMÜ", "sade", 45000, 80), ("Market", "sade", 12000, 80),
                                          ("Yemek & Kafe", "sade", 5000, 75), ("Yakıt", "sade", 5000, 80),
                                          ("Kıyafet", "sade", 3000, 90), ("Personel", "kurumsal", 25000, 80),
                                          ("Reklam", "kurumsal", 4000, 85)]:
            v.execute("""INSERT INTO butce(kategori,defter,tutar,donem,uyari_yuzde,aktif,olusturma)
                         VALUES(?,?,?,'Aylik',?,1,?)""", (kat, defter, tutar, uyari, simdi()))
    if not v.execute("SELECT COUNT(*) c FROM cek").fetchone()["c"]:
        cariler = v.execute("SELECT id, unvan FROM cari ORDER BY id").fetchall()
        c = lambda i: cariler[i % len(cariler)]["id"] if cariler else None
        cekler = [
            ("Çek", "Alınan", "0451234", c(0), "Garanti BBVA", 18500, g(-20), g(10), "Portföyde", "Müşteri ödemesi"),
            ("Çek", "Alınan", "0451235", c(1), "Ziraat Bankası", 9200, g(-35), g(-4), "Portföyde", "Vadesi geçti - ara"),
            ("Senet", "Alınan", "SN-77", c(2), "-", 6400, g(-50), g(25), "Portföyde", "2 taksit senet"),
            ("Çek", "Verilen", "778901", c(3), "İş Bankası", 14000, g(-15), g(2), "Ödenecek", "Dükkan kirası çeki"),
            ("Çek", "Verilen", "778902", c(4), "Akbank", 22500, g(-40), g(-6), "Ödenecek", "Malzeme alımı"),
            ("Senet", "Verilen", "SN-91", c(5), "-", 5000, g(-10), g(45), "Ödenecek", "Tedarikçi senedi"),
            ("Çek", "Alınan", "0451236", c(0), "Garanti BBVA", 11000, g(-90), g(-60), "Tahsil", "Tahsil edildi"),
        ]
        for tur, yon, no, cid, banka, tutar, kesim, vade, durum, ack in cekler:
            v.execute("""INSERT INTO cek(tur,yon,no,cari_id,banka,tutar,kesim,vade,durum,aciklama,olusturma)
                         VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                      (tur, yon, no, cid, banka, tutar, kesim, vade, durum, ack, simdi()))
    if not v.execute("SELECT COUNT(*) c FROM gorev").fetchone()["c"]:
        for tarih, baslik, detay, onc in [(g(2), "KDV beyannamesi", "Aylık KDV beyannamesi verilecek", "Yüksek"),
                                          (g(5), "KASKO ödemesi", "Araç kasko yenileme", "Normal"),
                                          (g(1), "Stok sayımı", "Boy boya stok sayımı yapılacak", "Normal"),
                                          (g(9), "Personel avansı", "Mehmet'e avans ödemesi", "Düşük"),
                                          (g(14), "Muhasebeci görüşmesi", "Dönem kapanışı için", "Normal")]:
            v.execute("""INSERT INTO gorev(tarih,baslik,detay,oncelik,durum,olusturma) VALUES(?,?,?,?,'Açık',?)""",
                      (tarih, baslik, detay, onc, simdi()))
    if not v.execute("SELECT COUNT(*) c FROM puantaj").fetchone()["c"]:
        p = v.execute("SELECT id, ad FROM personel ORDER BY id").fetchall()
        if p:
            kayitlar = [("Avans", 3000, 0, "Maaş avansı"), ("Prim", 1500, 0, "Ay hedefi primi"),
                        ("İzin", 0, 2, "İzin kullanımı"), ("Fazla Mesai", 850, 0, "Cumartesi çalışma")]
            for i, (tur, tutar, gun, ack) in enumerate(kayitlar):
                kisi = p[i % len(p)]
                v.execute("""INSERT INTO puantaj(personel_id,tarih,tur,tutar,gun,aciklama,olusturma)
                             VALUES(?,?,?,?,?,?,?)""", (kisi["id"], g(-i * 6), tur, tutar, gun, ack, simdi()))
    v.commit()


# ------------------------------------------------------------------ otomatik yedek
def oto_yedek_al(saat=None):
    ad = "oto-muhasebe-%s.db" % datetime.date.today().isoformat()
    hedef = os.path.join(YEDEK, ad)
    if os.path.exists(hedef):
        return None
    try:
        v = baglan()
        v.commit()
        v.execute("PRAGMA wal_checkpoint(FULL)")
        v.close()
        shutil.copy2(DB, hedef)
    except Exception as e:
        print("otomatik yedek alınamadı:", e)
        return None
    # eski yedekleri buda (son 30)
    otolar = sorted([x for x in os.listdir(YEDEK) if x.startswith("oto-")])
    for x in otolar[:-30]:
        try:
            os.remove(os.path.join(YEDEK, x))
        except Exception:
            pass
    return ad


def yedek_dongusu(durdur=None):
    while True:
        try:
            ek = ek_oku()
            if ek.get("oto_yedek", True):
                oto_yedek_al()
        except Exception:
            pass
        time.sleep(1800)
