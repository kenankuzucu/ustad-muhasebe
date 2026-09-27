# -*- coding: utf-8 -*-
"""
pdf_rapor.py — Word (.docx) → PDF dönüştürücü modülü.

ÜSTAD MUHASEBE projesi için tek amaçlı bir modül:
mevcut bir .docx dosyasını Microsoft Word COM otomasyonu ile gerçek bir
PDF'e çevirir. COM çağrıları pywin32 OLMADAN, subprocess ile PowerShell
üzerinden yapılır (pywin32 bu makinede KURULU DEĞİLDİR, kullanılmaz).

Yalnızca standart kütüphane kullanılır: os, subprocess, json, tempfile, time.

Genel API:
    pdf_uret(docx_yolu, pdf_yolu) -> dict
        {"tamam": bool, "pdf": str, "hata": str, "sayfa": int, "boyut": int}

    pdf_var_mi() -> bool
        Word COM otomasyonu bu makinede kullanılabilir mi?

Komut satırı kullanımı:
    python sunucu/pdf_rapor.py <girdi.docx> [cikti.pdf]
"""

import json
import os
import subprocess
import sys
import tempfile
import time

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

# wdFormatPDF — Word'ün "Farklı Kaydet" dosya biçimi numarası.
WD_FORMAT_PDF = 17

# wdStatisticPages — Word'ün sayfa sayısı istatistiği.
WD_STATISTIC_PAGES = 2

# PDF'in "var sayılması" için gereken en küçük boyut (bayt).
MIN_PDF_BAYT = 1024

# PowerShell dönüşümü için üst sınır (saniye). Büyük dosyalarda Word
# kendini toparlamaya çalışır; takılırsa süreç öldürülür.
VARSAYILAN_ZAMAN_ASIMI = 180

# COM sınama için kısa süre (Word.Application ayağa kalkması).
COM_SINAMA_ZAMAN_ASIMI = 45


# ---------------------------------------------------------------------------
# PowerShell betiği üretimi
# ---------------------------------------------------------------------------

def _ps_tirnak(yol: str) -> str:
    """
    Bir dosya yolunu PowerShell tek tırnaklı dizesi olarak güvenle gömer.

    Tek tırnaklı dizede kaçış kuralı tektir: ' karakteri '' olarak yazılır.
    Bu sayede boşluk, Türkçe karakter (Ö, ş, ı ...), ters bölü ve $ gibi
    özel karakterler sorunsuz taşınır.
    """
    return "'" + str(yol).replace("'", "''") + "'"


def _ps_betigi_olustur(docx_yolu: str, pdf_yolu: str) -> str:
    """
    Word COM ile docx'i PDF'e çeviren PowerShell betiğini döndürür.

    Tasarım kuralları:
      * $ErrorActionPreference = 'Stop'  → ilk hatada betik dursun.
      * try/catch/finally               → Word HER durumda kapatılsın
                                          (orphan WINWORD.EXE kalmasın).
      * SaveAs(FileFormat=17)           → asıl PDF kaydı.
      * Önce SaveAs denenir, olmazsa ExportAsFixedFormat'e düşülür.
      * Çıktı satırları (SAYFA=..., TAMAM / HATA: ...) Python'da ayrıştırılır.
    """
    docx_ps = _ps_tirnak(os.path.abspath(docx_yolu))
    pdf_ps = _ps_tirnak(os.path.abspath(pdf_yolu))

    return """$ErrorActionPreference = 'Stop'

$docx = {docx_ps}
$pdf  = {pdf_ps}
$sayfa = 0
$word = $null
$doc  = $null

try {{
    # Word uygulamasını görünmez olarak başlat.
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    # Belgeyi salt-okunur aç (ConfirmConversions=$false, ReadOnly=$true).
    $doc = $word.Documents.Open($docx, $false, $true)

    # Sayfa sayısını belge kapanmadan önce hesapla.
    try {{ $sayfa = [int]$doc.ComputeStatistics({wd_pages}) }} catch {{ $sayfa = 0 }}

    # Asıl dönüşüm: PDF olarak kaydet (wdFormatPDF = 17).
    $kaydedildi = $false
    try {{
        $doc.SaveAs([ref]$pdf, [ref]{wd_pdf})
        $kaydedildi = $true
    }} catch {{
        $kaydedildi = $false
    }}
    if (-not $kaydedildi) {{
        # Yedek yol: Word 2010+ ile gelen sabit biçim dışa aktarma.
        $doc.ExportAsFixedFormat($pdf, {wd_pdf})
    }}

    Write-Output ("SAYFA=" + $sayfa)
    Write-Output "TAMAM"
}}
catch {{
    Write-Output ("HATA: " + $_.Exception.Message)
    exit 1
}}
finally {{
    # Word'ü MUTLAKA kapat — orphan WINWORD.EXE bırakma.
    if ($doc -ne $null) {{
        try {{ $doc.Close($false) }} catch {{ }}
    }}
    if ($word -ne $null) {{
        try {{ $word.Quit() }} catch {{ }}
    }}
    # COM referanslarını serbest bırak (Word süreci temiz kapansın).
    if ($doc -ne $null) {{
        try {{ [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null }} catch {{ }}
    }}
    if ($word -ne $null) {{
        try {{ [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null }} catch {{ }}
    }}
}}
""".format(
        docx_ps=docx_ps,
        pdf_ps=pdf_ps,
        wd_pdf=WD_FORMAT_PDF,
        wd_pages=WD_STATISTIC_PAGES,
    )


def _powershell_calistir(betik_metni: str, zaman_asimi: int) -> dict:
    """
    Verilen PowerShell betiğini geçici bir .ps1 dosyasına yazar ve çalıştırır.

    Yol karmaşasından kaçınmak için betik dosyası UTF-8 BOM ile yazılır
    (Windows PowerShell 5.1 BOM'suz dosyayı ANSI sanıp Türkçe karakterleri
    bozar).

    Döndürür: {"rc": int, "stdout": str, "stderr": str, "zaman_asimi": bool}
    """
    gecici_dizin = tempfile.mkdtemp(prefix="pdf_rapor_")
    betik_yolu = os.path.join(gecici_dizin, "donustur.ps1")

    try:
        # utf-8-sig → UTF-8 BOM'lu; PowerShell 5.1 doğru okur (Türkçe yollar).
        with open(betik_yolu, "w", encoding="utf-8-sig", newline="\r\n") as f:
            f.write(betik_metni)

        komut = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-File", betik_yolu,
        ]

        try:
            sonuc = subprocess.run(
                komut,
                capture_output=True,
                timeout=zaman_asimi,
            )
        except subprocess.TimeoutExpired as e:
            return {
                "rc": -1,
                "stdout": _coz(e.stdout),
                "stderr": _coz(e.stderr),
                "zaman_asimi": True,
            }

        return {
            "rc": sonuc.returncode,
            "stdout": _coz(sonuc.stdout),
            "stderr": _coz(sonuc.stderr),
            "zaman_asimi": False,
        }
    finally:
        # Geçici .ps1 dosyasını temizle (başarısız olsa da projeyi kirletme).
        try:
            if os.path.exists(betik_yolu):
                os.remove(betik_yolu)
            os.rmdir(gecici_dizin)
        except OSError:
            pass


def _coz(veri) -> str:
    """subprocess çıktısını (bytes/str/None) metne çevirir."""
    if veri is None:
        return ""
    if isinstance(veri, bytes):
        # PowerShell çıktısı çoğunlukla OEM kod sayfasında gelir; hata
        # durumunda metni kaybetmemek için 'replace' kullanıyoruz.
        for kod in ("utf-8", "cp1254", "cp850", "latin-1"):
            try:
                return veri.decode(kod)
            except (UnicodeDecodeError, LookupError):
                continue
        return veri.decode("latin-1", errors="replace")
    return str(veri)


def _ps_cikti_ayristir(stdout: str) -> dict:
    """PowerShell stdout'undan SAYFA= ve TAMAM/HATA satırlarını çıkarır."""
    bilgi = {"tamam_mi": False, "sayfa": 0, "hata": ""}
    for satir in stdout.replace("\r\n", "\n").split("\n"):
        satir = satir.strip()
        if not satir:
            continue
        if satir.startswith("SAYFA="):
            try:
                bilgi["sayfa"] = int(satir.split("=", 1)[1].strip())
            except (ValueError, IndexError):
                bilgi["sayfa"] = 0
        elif satir == "TAMAM":
            bilgi["tamam_mi"] = True
        elif satir.startswith("HATA:"):
            bilgi["hata"] = satir.split(":", 1)[1].strip()
    return bilgi


# ---------------------------------------------------------------------------
# PDF doğrulama yardımcıları
# ---------------------------------------------------------------------------

def _pdf_sayfa_sayisi(pdf_yolu: str) -> int:
    """
    PDF ikili verisinden kaba bir sayfa sayısı tahmini yapar.

    Word genellikle sayfa ağaçlarını sıkıştırılmış nesne akışlarına koyar;
    bu yüzden kesin bir sayım değildir. Word zaten sayfayı bildirdiyse
    (SAYFA=...) bu fonksiyon kullanılmaz, yalnızca yedek yoldur.
    """
    try:
        with open(pdf_yolu, "rb") as f:
            veri = f.read()
    except OSError:
        return 0
    # Sayfa nesneleri: "/Type /Page" ( "/Pages" ile karışmasın diye sonda
    # boşluk/satır sonu aranır).
    sayac = 0
    for kalip in (b"/Type /Page\n", b"/Type /Page\r", b"/Type /Page ", b"/Type/Page\n"):
        sayac = max(sayac, veri.count(kalip))
    if sayac == 0:
        # Sıkıştırılmış nesne akışları: /Count N ipucuna bak.
        isaret = veri.find(b"/Count ")
        while isaret != -1 and sayac == 0:
            parca = veri[isaret + 7:isaret + 14].split(b"/")[0].split(b">")[0].strip()
            try:
                aday = int(parca)
                if 0 < aday < 100000:
                    sayac = aday
            except ValueError:
                pass
            isaret = veri.find(b"/Count ", isaret + 1)
    return sayac


def _pdf_dogrula(pdf_yolu: str) -> dict:
    """
    Üretilen PDF'in gerçekten var olup olmadığını doğrular.

    Koşullar: dosya var, boyut > 1 KB, ilk baytları %PDF imzası.
    """
    if not os.path.isfile(pdf_yolu):
        return {"gecerli": False, "hata": "PDF dosyası oluşmadı: " + pdf_yolu,
                "boyut": 0}

    try:
        boyut = os.path.getsize(pdf_yolu)
    except OSError as e:
        return {"gecerli": False, "hata": "PDF boyutu okunamadı: " + str(e),
                "boyut": 0}

    if boyut <= MIN_PDF_BAYT:
        return {
            "gecerli": False,
            "hata": "PDF çok küçük ({} bayt <= {} bayt)".format(boyut, MIN_PDF_BAYT),
            "boyut": boyut,
        }

    try:
        with open(pdf_yolu, "rb") as f:
            imza = f.read(5)
        if not imza.startswith(b"%PDF-"):
            return {"gecerli": False,
                    "hata": "Dosya geçerli bir PDF değil (imza: %r)" % imza,
                    "boyut": boyut}
    except OSError as e:
        return {"gecerli": False, "hata": "PDF okunamadı: " + str(e), "boyut": boyut}

    return {"gecerli": True, "hata": "", "boyut": boyut}


# ---------------------------------------------------------------------------
# Genel API
# ---------------------------------------------------------------------------

def pdf_var_mi() -> bool:
    """
    Word COM otomasyonu bu makinede kullanılabilir mi?

    İki aşamalı kontrol:
      1. Kayıt defterinde Word.Application ProgID'si var mı (hızlı).
      2. Kısa bir COM denemesi: Word.Application nesnesi gerçekten
         oluşturulabiliyor mu, sonra hemen kapatılıyor.

    Hiçbir durumda istisna yükseltmez; yalnızca True/False döndürür.
    """
    # 1) Kayıt defteri kontrolü (reg.exe, ek modül gerektirmez).
    try:
        sonuc = subprocess.run(
            ["reg", "query", r"HKCR\Word.Application\CLSID"],
            capture_output=True, timeout=15,
        )
        if sonuc.returncode != 0:
            return False
        cikti = _coz(sonuc.stdout).lower()
        # Office kurulu değilsa ProgID var olabilir ama CLSID {000209FF-...}
        # gerçek Word'e işaret eder.
        if "000209ff" not in cikti and "word" not in cikti:
            return False
    except Exception:
        return False

    # 2) Hızlı COM denemesi — nesne oluşturulup kapatılıyor.
    betik = """$ErrorActionPreference = 'Stop'
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    Write-Output ("KOM_OK=" + $word.Version)
    Write-Output "TAMAM"
}
catch {
    Write-Output ("HATA: " + $_.Exception.Message)
    exit 1
}
finally {
    if ($word -ne $null) {
        try { $word.Quit() } catch { }
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch { }
    }
}
"""
    try:
        r = _powershell_calistir(betik, COM_SINAMA_ZAMAN_ASIMI)
        if r["rc"] != 0 or r["zaman_asimi"]:
            return False
        return _ps_cikti_ayristir(r["stdout"])["tamam_mi"]
    except Exception:
        return False


def pdf_uret(docx_yolu: str, pdf_yolu: str = "") -> dict:
    """
    Bir .docx dosyasını Word COM ile PDF'e çevirir.

    Parametreler:
        docx_yolu : kaynak Word belgesi (boşluklu / Türkçe karakterli olabilir)
        pdf_yolu  : hedef PDF yolu; boş bırakılırsa docx ile aynı klasörde
                    aynı adla .pdf uzantısı kullanılır.

    Döndürür:
        {"tamam": True,  "pdf": <yol>, "hata": "",   "sayfa": n, "boyut": b}
        {"tamam": False, "pdf": "",    "hata": "...", "sayfa": 0, "boyut": 0}

    Hiçbir hata durumunda istisna yükseltilmez; her şey sözlüğe yazılır.
    """
    baslangic = time.time()

    try:
        # --- Girdi doğrulama -------------------------------------------------
        if not docx_yolu or not isinstance(docx_yolu, str):
            return {"tamam": False, "pdf": "", "hata": "docx yolu boş",
                    "sayfa": 0, "boyut": 0}

        docx_yolu = os.path.abspath(docx_yolu)
        if not os.path.isfile(docx_yolu):
            return {"tamam": False, "pdf": "",
                    "hata": "docx bulunamadı: " + docx_yolu, "sayfa": 0, "boyut": 0}

        if not docx_yolu.lower().endswith(".docx"):
            return {"tamam": False, "pdf": "",
                    "hata": "Kaynak dosya .docx değil: " + docx_yolu,
                    "sayfa": 0, "boyut": 0}

        # --- Hedef yolu belirle ---------------------------------------------
        if not pdf_yolu:
            pdf_yolu = os.path.splitext(docx_yolu)[0] + ".pdf"
        pdf_yolu = os.path.abspath(pdf_yolu)
        hedef_dizin = os.path.dirname(pdf_yolu)
        if hedef_dizin and not os.path.isdir(hedef_dizin):
            return {"tamam": False, "pdf": "",
                    "hata": "Hedef klasör yok: " + hedef_dizin,
                    "sayfa": 0, "boyut": 0}

        # Önceki (bayat) PDF'i sil — doğrulamanın yanlış pozitif olmaması için
        # dosyanın gerçekten bu çalıştırmada üretildiğinden emin olmak istiyoruz.
        if os.path.exists(pdf_yolu):
            try:
                os.remove(pdf_yolu)
            except OSError as e:
                return {"tamam": False, "pdf": "",
                        "hata": "Eski PDF silinemedi (Word açık olabilir): " + str(e),
                        "sayfa": 0, "boyut": 0}

        # --- Word COM yüklü mü? ---------------------------------------------
        if not pdf_var_mi():
            return {"tamam": False, "pdf": "",
                    "hata": "Microsoft Word COM otomasyonu kullanılamıyor "
                            "(Word kurulu değil veya Office COM engelli)",
                    "sayfa": 0, "boyut": 0}

        # --- Dönüşümü çalıştır ----------------------------------------------
        betik = _ps_betigi_olustur(docx_yolu, pdf_yolu)
        ps = _powershell_calistir(betik, VARSAYILAN_ZAMAN_ASIMI)
        bilgi = _ps_cikti_ayristir(ps["stdout"])

        if ps["zaman_asimi"]:
            return {"tamam": False, "pdf": "",
                    "hata": "PowerShell zaman aşımına uğradı ({} sn)".format(
                        VARSAYILAN_ZAMAN_ASIMI),
                    "sayfa": 0, "boyut": 0}

        if not bilgi["tamam_mi"]:
            mesaj = bilgi["hata"] or ps["stderr"].strip() or ps["stdout"].strip()
            if not mesaj:
                mesaj = "PowerShell rc={} ile başarısız oldu".format(ps["rc"])
            return {"tamam": False, "pdf": "",
                    "hata": mesaj[:1500], "sayfa": 0, "boyut": 0}

        # --- Üretilen PDF'i gerçekten doğrula -------------------------------
        dogrula = _pdf_dogrula(pdf_yolu)
        if not dogrula["gecerli"]:
            return {"tamam": False, "pdf": "",
                    "hata": dogrula["hata"], "sayfa": 0, "boyut": 0}

        sayfa = bilgi["sayfa"]
        if sayfa <= 0:
            # Word sayfayı bildirmediyse ikili veriden tahmin et.
            sayfa = _pdf_sayfa_sayisi(pdf_yolu)

        return {
            "tamam": True,
            "pdf": pdf_yolu,
            "hata": "",
            "sayfa": sayfa,
            "boyut": dogrula["boyut"],
            "sure": round(time.time() - baslangic, 2),
        }

    except Exception as e:
        # ASLA çökme: her beklenmedik hata sözlüğe yazılır.
        return {"tamam": False, "pdf": "",
                "hata": "{}: {}".format(type(e).__name__, e),
                "sayfa": 0, "boyut": 0}


# ---------------------------------------------------------------------------
# Komut satırı arayüzü
# ---------------------------------------------------------------------------

def _main(argv):
    if len(argv) < 2:
        print(json.dumps({
            "tamam": False,
            "hata": "Kullanım: python sunucu/pdf_rapor.py <girdi.docx> [cikti.pdf]",
        }, ensure_ascii=False))
        return 1

    docx = argv[1]
    pdf = argv[2] if len(argv) > 2 else ""
    sonuc = pdf_uret(docx, pdf)

    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0 if sonuc.get("tamam") else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
