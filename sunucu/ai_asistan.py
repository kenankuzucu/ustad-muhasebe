# -*- coding: utf-8 -*-
"""
ÜSTAD MUHASEBE · yapay zekâ asistanı (Gemini REST)
Bağımsız modül — yalnızca Python standart kütüphanesi kullanır.

Kullanım (kütüphane):
    import ai_asistan
    ai_asistan.anahtar_kaydet("AIza...")
    print(ai_asistan.sor("Bu ay kârım ne?", baglam="ciro: 120000, gider: 80000"))

Kullanım (komut satırı):
    python sunucu/ai_asistan.py "KDV oranı kaç?"
    python sunucu/ai_asistan.py --dogrula      # anahtarı sınar
    python sunucu/ai_asistan.py --kaydet AIza...  # anahtarı dosyaya yazar

Anahtar sırası: GEMINI_API_KEY > GEMINI_KEY > GOOGLE_API_KEY > veri/ai.json
Anahtar ASLA ekrana/loga yazılmaz; hata mesajlarında maskelenir.
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

# --------------------------------------------------------------------- yollar
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(KOK, "veri")
AI_DOSYA = os.path.join(VERI, "ai.json")

# ------------------------------------------------------------- sabitler / API
API_KOK = "https://generativelanguage.googleapis.com/v1beta"
VARSAYILAN_MODEL = "gemini-2.0-flash"
ZAMAN_ASIMI = 45  # saniye

ENV_ADLARI = ("GEMINI_API_KEY", "GEMINI_KEY", "GOOGLE_API_KEY")

SISTEM_YONERGESI = (
    "Sen ÜSTAD MUHASEBE uygulamasının Türkçe muhasebe ve finans asistanısın. "
    "Kurallar: (1) Her zaman Türkçe, kısa ve net cevap ver; gereksiz giriş cümlesi yazma. "
    "(2) Sana verilen BAĞLAM dışındaki hiçbir sayıyı, tutarı, vergi numarasını veya "
    "tarihi uydurma; bağlamda yoksa 'bu bilgi verilerde yok' de. "
    "(3) Muhasebe, KDV, fatura, cari hesap, gelir-gider ve finans konularında "
    "yardımcı ol; kesin emin olmadığın hukuki/mali konularda 'mali müşavirinize danışın' uyarısı ekle. "
    "(4) Gerektiğinde kısa madde imleri kullan."
)


# ------------------------------------------------------------------- yardımcı
def _maskele(anahtar):
    """Anahtarı loglanabilir biçime çevirir: AIzaSy...1b2c -> 'AIza****c'."""
    if not anahtar:
        return ""
    a = str(anahtar).strip()
    if len(a) <= 6:
        return "*" * len(a)
    return a[:4] + "****" + a[-2:]


def _anahtar_temizle(anahtar):
    """Girilen anahtardaki boşluk/tırnak artıklarını temizler."""
    if not anahtar:
        return ""
    return str(anahtar).strip().strip('"').strip("'")


def _ssl_baglami():
    """Varsayılan sertifika doğrulamalı SSL bağlamı.

    Doğrulama ASLA kapatılmaz. Sertifika deposu bozuksa çağıran taraf
    yakalar ve kullanıcıya Türkçe 'sertifika' mesajı döner.
    """
    return ssl.create_default_context()


def _http_json(adres, govde=None, anahtar=None):
    """Basit JSON HTTP çağrısı. (durum, veri) döner.

    Ağ/sertifika hatalarında (0, {"_hata": "..."}) döner.
    """
    veri = None
    basliklar = {"Content-Type": "application/json; charset=utf-8"}
    if govde is not None:
        veri = json.dumps(govde, ensure_ascii=False).encode("utf-8")
    istek = urllib.request.Request(adres, data=veri, headers=basliklar, method="POST" if veri else "GET")
    try:
        baglam = _ssl_baglami()
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI, context=baglam) as c:
            ham = c.read().decode("utf-8", "replace")
            return c.status, (json.loads(ham) if ham else {})
    except urllib.error.HTTPError as h:
        ham = ""
        try:
            ham = h.read().decode("utf-8", "replace")
        except Exception:
            pass
        try:
            hata_json = json.loads(ham) if ham else {}
        except Exception:
            hata_json = {"_ham": ham[:400]}
        return h.code, hata_json
    except urllib.error.URLError as u:
        neden = getattr(u, "reason", u)
        metin = str(neden)
        if "CERTIFICATE" in metin.upper() or "SSL" in metin.upper():
            return 0, {"_hata": "SSL sertifika doğrulaması başarısız (Windows sertifika deposu). "
                                "Sertifika dosyalarını güncelleyip tekrar dene."}
        return 0, {"_hata": "Bağlantı kurulamadı (internet yok ya da güvenlik duvarı engelliyor): " + metin[:200]}
    except ssl.SSLError as s:
        return 0, {"_hata": "SSL sertifika hatası: " + str(s)[:200]}
    except TimeoutError:
        return 0, {"_hata": "Zaman aşımı — sunucu %d saniyede yanıt vermedi." % ZAMAN_ASIMI}
    except Exception as e:  # son çare
        return 0, {"_hata": "Beklenmeyen hata: " + e.__class__.__name__ + ": " + str(e)[:200]}


def _http_mesaji(durum, veri, baglam_metni="istek"):
    """HTTP durum kodunu Türkçe anlaşılır mesaja çevirir. Anahtar sızdırmaz."""
    ayrinti = ""
    if isinstance(veri, dict):
        hata = veri.get("error") or {}
        if isinstance(hata, dict):
            ayrinti = (hata.get("message") or "").strip()
        ayrinti = ayrinti or veri.get("_hata") or veri.get("_ham") or ""
    ayrinti = str(ayrinti)[:180]

    if durum == 400:
        alt = ayrinti.lower()
        if "api key not valid" in alt or "api_key_invalid" in alt or "api key" in alt and "invalid" in alt:
            return "Gemini anahtarı geçersiz — Ayarlar ekranından yeni bir anahtar gir."
        if "api has not been used" in alt or "is disabled" in alt:
            return "Generative Language API bu projede kapalı — Google AI Studio'dan etkinleştir. " \
                   "(Detay: %s)" % ayrinti
        return "İstek geçersiz (400). Soruyu kısaltıp tekrar dene." + (" Detay: " + ayrinti if ayrinti else "")
    if durum == 401:
        return "Gemini anahtarı geçersiz (401) — Ayarlar ekranından yeni anahtar gir."
    if durum == 403:
        return "Gemini anahtarı bu modele yetkili değil ya da API devre dışı (403) — " \
               "Google AI Studio'dan Generative Language API'yi aç."
    if durum == 404:
        return "Model bulunamadı (404) — '%s' adı geçersiz. Ayarlardan farklı model seç." % baglam_metni
    if durum == 413:
        return "Gönderilen bağlam çok büyük (413) — daha az veriyle tekrar dene."
    if durum == 429:
        return "Kota doldu, biraz sonra tekrar dene (429)."
    if durum and 500 <= durum < 600:
        return "Gemini sunucusunda geçici hata (%d) — biraz sonra tekrar dene." % durum
    if durum == 0:
        return ayrinti or "Bağlantı kurulamadı."
    return "Beklenmeyen yanıt (%s).%s" % (durum, (" Detay: " + ayrinti) if ayrinti else "")


# --------------------------------------------------------------- anahtar işleri
def anahtar_oku():
    """Sırayla ortam değişkenleri, sonra veri/ai.json okunur. Yoksa '' döner."""
    for ad in ENV_ADLARI:
        deger = _anahtar_temizle(os.environ.get(ad))
        if deger:
            return deger
    try:
        if os.path.exists(AI_DOSYA):
            with open(AI_DOSYA, "r", encoding="utf-8") as f:
                kayit = json.load(f)
            if isinstance(kayit, dict):
                return _anahtar_temizle(kayit.get("anahtar"))
    except Exception:
        pass
    return ""


def anahtar_kaydet(anahtar):
    """Anahtarı veri/ai.json içine yazar (klasör yoksa oluşturur).

    Dosya izinleri mümkünse sadece sahibine açık hale getirilir.
    """
    anahtar = _anahtar_temizle(anahtar)
    os.makedirs(VERI, exist_ok=True)
    mevcut = {}
    try:
        if os.path.exists(AI_DOSYA):
            with open(AI_DOSYA, "r", encoding="utf-8") as f:
                mevcut = json.load(f) or {}
    except Exception:
        mevcut = {}
    if not isinstance(mevcut, dict):
        mevcut = {}
    mevcut["anahtar"] = anahtar
    if "model" not in mevcut:
        mevcut["model"] = VARSAYILAN_MODEL
    gecici = AI_DOSYA + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=2)
    os.replace(gecici, AI_DOSYA)
    try:  # Windows dışında dosyayı özel kıl
        os.chmod(AI_DOSYA, 0o600)
    except Exception:
        pass


def _govde_uret(soru, baglam):
    """Gemini generateContent istek gövdesini hazırlar."""
    soru = (soru or "").strip()
    baglam = (baglam or "").strip()
    if baglam:
        metin = (
            SISTEM_YONERGESI
            + "\n\n--- BAĞLAM (uygulamadan gelen gerçek veriler) ---\n"
            + baglam[:12000]
            + "\n--- BAĞLAM SONU ---\n\nSORU: "
            + soru
        )
    else:
        metin = SISTEM_YONERGESI + "\n\nSORU: " + soru
    return {
        "contents": [{"role": "user", "parts": [{"text": metin}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }


def _cevabi_ayikla(veri):
    """Gemini yanıtından düz metni çıkarır."""
    adaylar = veri.get("candidates") or []
    if not adaylar:
        blok = (veri.get("promptFeedback") or {}).get("blockReason")
        if blok:
            return "", "İstek güvenlik filtresine takıldı (%s) — soruyu farklı ifadeyle dene." % blok
        return "", "Model boş yanıt döndü."
    parcalar = []
    for aday in adaylar:
        icerik = aday.get("content") or {}
        for parca in (icerik.get("parts") or []):
            metin = parca.get("text")
            if metin:
                parcalar.append(metin)
    cevap = "\n".join(parcalar).strip()
    if not cevap:
        bitis = (adaylar[0].get("finishReason") or "").upper()
        if bitis == "MAX_TOKENS":
            return "", "Cevap token sınırına takıldı — soruyu daha kısa sor."
        if bitis in ("SAFETY", "PROHIBITED_CONTENT", "RECITATION"):
            return "", "Cevap güvenlik filtresine takıldı (%s)." % bitis
        return "", "Model boş cevap döndü."
    return cevap, ""


def _model_listesi(anahtar):
    """generateContent destekleyen model adlarını döner (başarısızsa [])."""
    adres = "%s/models?key=%s&pageSize=100" % (API_KOK, anahtar)
    durum, veri = _http_json(adres)
    if durum != 200 or not isinstance(veri, dict):
        return []
    adlar = []
    for m in (veri.get("models") or []):
        yontemler = m.get("supportedGenerationMethods") or []
        ad = (m.get("name") or "").split("/")[-1]
        if ad and "generateContent" in yontemler:
            adlar.append(ad)
    return adlar


# Sohbet için uygun olmayan model adları (görsel/ses/araştırma vb.)
_KOTU_KELIMELER = ("tts", "image", "transcribe", "computer-use", "lyria", "robotics",
                   "deep-research", "embedding", "aqa", "live", "native-audio")


def uygun_model_sec(adlar):
    """Elde edilen model listesinden sohbet için en uygun olanı seçer."""
    temiz = [a for a in adlar if not any(k in a.lower() for k in _KOTU_KELIMELER)]
    if not temiz:
        return ""
    # 1) bilinen sağlam tercihler
    for tercih in ("gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"):
        if tercih in temiz:
            return tercih
    # 2) genel flash modelleri (sürüm numaralı, önizlemesiz olanlar önce)
    import re as _re
    duz_flash = sorted(
        (a for a in temiz if _re.fullmatch(r"gemini-\d+(\.\d+)?-flash(-lite)?", a)),
        key=lambda s: [int(p) for p in _re.findall(r"\d+\.?\d*", s)][:2], reverse=True,
    )
    if duz_flash:
        return duz_flash[0]
    # 3) herhangi bir flash
    flash = [a for a in temiz if "flash" in a.lower()]
    if flash:
        return flash[0]
    # 4) gemini olan herhangi biri, yoksa ilk aday
    return next((a for a in temiz if a.startswith("gemini")), temiz[0])


def _tek_istek(anahtar, model, soru, baglam):
    """Tek generateContent çağrısı → (durum, veri)."""
    adres = "%s/models/%s:generateContent?key=%s" % (API_KOK, model, anahtar)
    return _http_json(adres, govde=_govde_uret(soru, baglam))


def sor(soru, baglam="", anahtar=None, model=VARSAYILAN_MODEL):
    """Gemini'ye Türkçe soru sorar.

    Dönen: {"tamam": True, "cevap": "...", "model": "..."}
         veya {"tamam": False, "hata": "..."}
    Model yoksa (404) otomatik olarak uygun bir modele geçilir; kullanılan
    model yanıtta "model" alanında bildirilir.
    """
    if not (soru or "").strip():
        return {"tamam": False, "hata": "Soru boş — bir şey yaz."}

    anahtar = _anahtar_temizle(anahtar) or anahtar_oku()
    if not anahtar:
        return {"tamam": False, "hata": "Gemini anahtarı yok — Ayarlar ekranından gir"}

    model = (model or VARSAYILAN_MODEL).strip() or VARSAYILAN_MODEL
    durum, veri = _tek_istek(anahtar, model, soru, baglam)
    uyari = ""

    # Model bulunamadı → listeden uygun bir model seçip bir kez daha dene
    if durum == 404:
        adlar = _model_listesi(anahtar)
        yeni = uygun_model_sec(adlar)
        if yeni and yeni != model:
            durum, veri = _tek_istek(anahtar, yeni, soru, baglam)
            uyari = "'%s' bu hesapta yok; '%s' kullanıldı." % (model, yeni)
            model = yeni

    if durum == 0 or not isinstance(veri, dict):
        return {"tamam": False, "hata": _http_mesaji(durum, veri if isinstance(veri, dict) else {})}
    if durum != 200:
        return {"tamam": False, "hata": _http_mesaji(durum, veri, baglam_metni=model)}

    cevap, hata = _cevabi_ayikla(veri)
    if hata:
        return {"tamam": False, "hata": hata}
    sonuc = {"tamam": True, "cevap": cevap, "model": model}
    if uyari:
        sonuc["uyari"] = uyari
    return sonuc


def anahtar_gecerli_mi(anahtar=None):
    """Anahtarı models listesi çekerek sınar.

    Dönen: {"tamam": True, "model_sayisi": n} veya {"tamam": False, "hata": "..."}
    """
    anahtar = _anahtar_temizle(anahtar) or anahtar_oku()
    if not anahtar:
        return {"tamam": False, "hata": "Gemini anahtarı yok — Ayarlar ekranından gir"}

    adres = "%s/models?key=%s&pageSize=50" % (API_KOK, anahtar)
    durum, veri = _http_json(adres)
    if durum == 0 or not isinstance(veri, dict):
        return {"tamam": False, "hata": _http_mesaji(durum, veri if isinstance(veri, dict) else {})}
    if durum != 200:
        return {"tamam": False, "hata": _http_mesaji(durum, veri)}
    modeller = veri.get("models") or []
    if not modeller:
        return {"tamam": False, "hata": "Anahtar geçerli görünüyor ama hiç model listelenmedi."}
    return {"tamam": True, "model_sayisi": len(modeller)}


def durum_ozeti():
    """Ayarlar ekranı için anahtarsız özet (anahtarın kendisi asla yazılmaz)."""
    a = anahtar_oku()
    return {
        "anahtar_var": bool(a),
        "anahtar_maske": _maskele(a),
        "dosya": AI_DOSYA,
        "ortam_degiskeni": next((ad for ad in ENV_ADLARI if _anahtar_temizle(os.environ.get(ad))), ""),
    }


# ------------------------------------------------------------------------ CLI
if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--yardim", "--help"):
        print("Kullanım:")
        print('  python sunucu/ai_asistan.py "sorunuz"')
        print("  python sunucu/ai_asistan.py --durum")
        print("  python sunucu/ai_asistan.py --dogrula")
        print('  python sunucu/ai_asistan.py --kaydet AIza...')
        sys.exit(0)

    if args[0] == "--durum":
        print(json.dumps(durum_ozeti(), ensure_ascii=False, indent=2))
        sys.exit(0)

    if args[0] == "--kaydet":
        if len(args) < 2:
            print("HATA: anahtar verilmedi. Örnek: --kaydet AIza...")
            sys.exit(2)
        anahtar_kaydet(args[1])
        print("Anahtar kaydedildi:", _maskele(args[1]), "→", AI_DOSYA)
        sys.exit(0)

    if args[0] == "--dogrula":
        s = anahtar_gecerli_mi()
        if s.get("tamam"):
            print("Anahtar geçerli. Erişilebilen model sayısı:", s.get("model_sayisi"))
            sys.exit(0)
        print("HATA:", s.get("hata"))
        sys.exit(1)

    soru = " ".join(args)
    r = sor(soru)
    if r.get("tamam"):
        print(r["cevap"])
        sys.exit(0)
    print("HATA:", r.get("hata"))
    sys.exit(1)
