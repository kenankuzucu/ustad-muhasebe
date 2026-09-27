# -*- coding: utf-8 -*-
"""
ÜSTAD MUHASEBE · paketleme aracı
================================
arac/giris.py'yi PyInstaller ile TEK DOSYALIK Windows uygulamasına çevirir:

    dist/USTAD-MUHASEBE.exe

Kullanım:
    python arac/paketle.py            # derle
    python arac/paketle.py --temizle  # build/ ve dist/ klasörlerini sil

Notlar:
  · panel/ ve sunucu/ klasörleri exe'nin İÇİNE gömülür (--add-data, ayırıcı ';').
  · Konsol penceresi açık kalır (--console) ki hata görülebilsin.
  · PyInstaller yoksa 'python -m pip install --user pyinstaller' ile kurulmaya
    çalışılır. Kurulamazsa HİÇBİR ZAMAN sahte başarı bildirilmez; tam hata
    metni ekrana basılır ve çıkış kodu 1 olur.
"""
import os
import sys
import shutil
import subprocess

BETIK_ADI = "USTAD-MUHASEBE"
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARAC = os.path.join(KOK, "arac")
GIRIS = os.path.join(ARAC, "giris.py")
DIST = os.path.join(KOK, "dist")
BUILD = os.path.join(KOK, "build")
HEDEF_EXE = os.path.join(DIST, BETIK_ADI + ".exe")

GEREKLI_KLASORLER = ("panel", "sunucu")


# --------------------------------------------------------------- yardımcılar
def pyinstaller_surumu():
    """Kurulu PyInstaller sürümünü döndürür, yoksa None."""
    try:
        import PyInstaller  # noqa: F401
        return getattr(PyInstaller, "__version__", "bilinmiyor")
    except ImportError:
        return None


def pyinstaller_kur():
    """PyInstaller'ı kurmayı dener. (basari, mesaj) döndürür."""
    print("[i] PyInstaller bulunamadı, kurulmaya çalışılıyor...")
    cmd = [sys.executable, "-m", "pip", "install", "--user", "pyinstaller"]
    print("    $ " + " ".join(cmd))
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as e:
        return False, "pip komutu çalıştırılamadı: %r" % (e,)
    cikti = (p.stdout or "") + "\n" + (p.stderr or "")
    if p.returncode != 0:
        return False, ("PyInstaller KURULAMADI (çıkış kodu %d).\nTAM ÇIKTI:\n%s"
                       % (p.returncode, cikti.strip()))
    # kurulum gerçekten işe yaradı mı?
    if pyinstaller_surumu() is None:
        return False, ("pip başarılı göründü ama 'import PyInstaller' hâlâ başarısız "
                       "(farklı bir Python yorumlayıcısı olabilir).\nTAM ÇIKTI:\n%s"
                       % cikti.strip())
    return True, "PyInstaller kuruldu."


def temizle():
    for k in (BUILD, DIST):
        if os.path.isdir(k):
            shutil.rmtree(k)
            print("[i] silindi: %s" % k)


def dogrula():
    eksik = [k for k in GEREKLI_KLASORLER if not os.path.isdir(os.path.join(KOK, k))]
    if eksik:
        print("[X] Şu klasörler yok: %s" % ", ".join(eksik))
        return False
    if not os.path.isfile(GIRIS):
        print("[X] Giriş betiği yok: %s" % GIRIS)
        return False
    if not os.path.isfile(os.path.join(KOK, "panel", "index.html")):
        print("[!] panel/index.html bulunamadı - panel boş açılabilir.")
    return True


def komut_uret():
    ayrac = ";"  # Windows'ta --add-data ayırıcısı
    # ÖNEMLİ: --specpath build olduğu için --add-data kaynakları MUTLAK yol olmalı;
    # göreli "panel" yolu build/panel diye aranır ve derleme şu hatayla düşer:
    #   ERROR: Unable to find '...\build\panel' when adding binary and data files.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--console",                     # konsol penceresi açık kalsın
        "--name", BETIK_ADI,
        "--distpath", DIST,
        "--workpath", BUILD,
        "--specpath", BUILD,
        "--paths", os.path.join(KOK, "sunucu"),   # import sunucu / disa_aktar
        "--paths", ARAC,
        "--hidden-import", "sunucu",
        "--hidden-import", "disa_aktar",
        "--hidden-import", "ozellikler",
        "--hidden-import", "pdf_rapor",
        "--hidden-import", "ai_asistan",
        "--add-data", os.path.join(KOK, "panel") + ayrac + "panel",
        "--add-data", os.path.join(KOK, "sunucu") + ayrac + "sunucu",
        GIRIS,
    ]
    return cmd


# ------------------------------------------------------------------- ana akış
def main():
    if "--temizle" in sys.argv:
        temizle()
        return 0

    print("=" * 62)
    print("  ÜSTAD KASA · paketleme aracı")
    print("=" * 62)
    print("[i] proje kökü : %s" % KOK)
    print("[i] yorumlayıcı: %s" % sys.executable)

    surum = pyinstaller_surumu()
    if surum is None:
        basarili, mesaj = pyinstaller_kur()
        if not basarili:
            print("[X] " + mesaj)
            return 1
        print("[i] " + mesaj)
        surum = pyinstaller_surumu()
    print("[i] PyInstaller sürümü: %s" % surum)

    if not dogrula():
        return 1

    if os.path.exists(HEDEF_EXE):
        try:
            os.remove(HEDEF_EXE)
        except OSError as e:
            print("[!] Eski exe silinemedi (%s) - üzerine yazılacak." % e)

    cmd = komut_uret()
    print("[i] komut:")
    print("    " + " ".join(cmd))
    print("-" * 62)

    islem = subprocess.Popen(cmd, cwd=KOK, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace")
    for satir in islem.stdout:
        print(satir.rstrip())
    kod = islem.wait()

    print("-" * 62)
    if kod != 0:
        print("[X] PyInstaller BAŞARISIZ (çıkış kodu %d)." % kod)
        return 1
    if not os.path.isfile(HEDEF_EXE):
        print("[X] PyInstaller 0 döndürdü ama exe oluşmadı: %s" % HEDEF_EXE)
        return 1

    boyut = os.path.getsize(HEDEF_EXE)
    print("[OK] Üretildi: %s" % HEDEF_EXE)
    print("[OK] Boyut   : %s bayt (%.1f MB)" % (boyut, boyut / 1024 / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
