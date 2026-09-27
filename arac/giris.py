# -*- coding: utf-8 -*-
"""
ÜSTAD KASA · paketlenmiş (PyInstaller) giriş betiği
====================================================
Bu betik iki şekilde çalışır:

  1) Paketlenmiş hâlde  (dist/USTAD-KASA.exe)
     panel/ ve sunucu/ dosyaları exe'nin içinden (sys._MEIPASS) okunur;
     veri (veri/, cikti/, yedek/) ise exe'nin YANINDA tutulur, böylece
     program güncellense bile kayıtlar kaybolmaz.

  2) Paketlenmemiş hâlde (python arac/giris.py)
     Proje kökündeki panel/ ve sunucu/ kullanılır.

Davranış:
  · localhost:8091 üzerinde sunucuyu çalıştırır
  · 3 saniye sonra tarayıcıyı http://127.0.0.1:8091 adresine açar
  · konsol penceresi KAPANMAZ (--console ile derlenmiştir)
  · sunucu çökerse 5 saniye sonra otomatik yeniden başlatır
"""
import os
import sys
import time
import threading
import traceback
import webbrowser
import socket

SURUM = "1.2.0"
BASLIK = "ÜSTAD MUHASEBE"
PORT = 8091
PORT_ARALIK = (8091, 8092, 8093, 8094, 8095)
YENIDEN_BASLATMA_SN = 5
AKTIF_PORT = PORT


def _bos_port():
    """8091 doluysa sıradaki boş portu döndürür (port çakışmasında program açılmaz kalmasın)."""
    for p in PORT_ARALIK:
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", p))
            s.close()
            return p
        except OSError:
            s.close()
            continue
    return None


def _klasorler():
    """(paket_klasoru, veri_klasoru) döndürür."""
    if getattr(sys, "frozen", False):
        # PyInstaller tek dosya: içerik geçici _MEIPASS altında açılır
        paket = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        # kalıcı veri: exe'nin bulunduğu klasör
        veri_kok = os.path.dirname(os.path.abspath(sys.executable))
    else:
        paket = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        veri_kok = paket
    return paket, veri_kok


def _tarayici_ac(gectirme_sn=3):
    def _isci():
        time.sleep(gectirme_sn)
        url = "http://127.0.0.1:%d" % AKTIF_PORT
        try:
            webbrowser.open(url)
        except Exception:
            print("  [!] Tarayıcı otomatik açılamadı. Elle açın: %s" % url)

    t = threading.Thread(target=_isci, daemon=True)
    t.start()


def sunucuyu_yukle():
    """sunucu/sunucu.py dosyasını modül olarak yükler ve yollarını ayarlar."""
    paket, veri_kok = _klasorler()
    sunucu_dir = os.path.join(paket, "sunucu")

    if sunucu_dir not in sys.path:
        sys.path.insert(0, sunucu_dir)
    if paket not in sys.path:
        sys.path.insert(0, paket)

    import sunucu  # noqa: E402

    # --- çalışma yollarını kalıcı klasöre çevir -------------------------
    veri = os.path.join(veri_kok, "veri")
    cikti = os.path.join(veri_kok, "cikti")
    yedek = os.path.join(veri_kok, "yedek")

    sunucu.KOK = veri_kok
    sunucu.VERI = veri
    sunucu.PANEL = os.path.join(paket, "panel")
    sunucu.CIKTI = cikti
    sunucu.YEDEK = yedek
    sunucu.DB = os.path.join(veri, "muhasebe.db")
    sunucu.AYAR_DOSYA = os.path.join(veri, "ayar.json")

    # ÖNEMLİ: ozellikler.py ve ai_asistan.py kendi yol sabitlerini tutar; bunlar
    # paketlenmiş hâlde _MEIPASS (geçici) klasörüne bakar. Yamalanmazsa exe
    # tabloları geçici klasörde arar ve "no such table: cek" gibi 500 hataları verir.
    import ozellikler  # noqa: E402
    ozellikler.KOK = veri_kok
    ozellikler.VERI = veri
    ozellikler.PANEL = os.path.join(paket, "panel")
    ozellikler.CIKTI = cikti
    ozellikler.YEDEK = yedek
    ozellikler.FISLER = os.path.join(veri, "fisler")
    ozellikler.DB = os.path.join(veri, "muhasebe.db")
    ozellikler.EK_AYAR = os.path.join(veri, "ek.json")

    import ai_asistan  # noqa: E402
    ai_asistan.KOK = veri_kok
    ai_asistan.VERI = veri
    ai_asistan.AI_DOSYA = os.path.join(veri, "ai.json")

    for k in (veri, cikti, yedek, ozellikler.FISLER):
        os.makedirs(k, exist_ok=True)

    if not os.path.exists(os.path.join(sunucu.PANEL, "index.html")):
        print("  [!] panel/index.html bulunamadı: %s" % sunucu.PANEL)

    print("  %s · paket : %s" % (BASLIK, paket))
    print("  %s · veri  : %s" % (BASLIK, veri_kok))
    return sunucu


def calistir():
    sunucu = sunucuyu_yukle()
    # sunucu.main() portu sys.argv[1]'den okur
    sys.argv = [sys.argv[0] if sys.argv else "giris.py", str(AKTIF_PORT)]
    sunucu.main()


def main():
    global AKTIF_PORT
    AKTIF_PORT = _bos_port() or PORT
    print("=" * 62)
    print("  %s · giriş betiği v%s" % (BASLIK, SURUM))
    print("  Panel : http://127.0.0.1:%d" % AKTIF_PORT)
    if AKTIF_PORT != PORT:
        print("  [!] %d portu doluydu (başka bir program kullanıyor) - %d portu seçildi."
              % (PORT, AKTIF_PORT))
    print("  Bu pencereyi KAPATMAYIN - kapanırsa program durur.")
    print("=" * 62)

    _tarayici_ac()

    while True:
        try:
            calistir()
        except SystemExit:
            raise
        except KeyboardInterrupt:
            print("\n  [i] Kapatıldı.")
            break
        except Exception:
            print("\n  [X] Sunucu çöktü - tam hata:")
            traceback.print_exc()
        print("\n  [i] %d saniye sonra yeniden başlatılıyor..." % YENIDEN_BASLATMA_SN)
        time.sleep(YENIDEN_BASLATMA_SN)


if __name__ == "__main__":
    main()
