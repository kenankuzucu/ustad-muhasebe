# -*- coding: utf-8 -*-
"""
ÜSTAD KASA · LAN erişim yardımcısı
==================================
Program yalnızca localhost (127.0.0.1:8091) üzerinde dinler. Bu betik,
telefondan/başka bilgisayardan panele erişmek için hangi adreslerin
kullanılabileceğini SÖYLER. Ana sunucu dosyasına (sunucu/sunucu.py)
DOKUNMAZ - sadece bilgi üretir.

Kullanım:
    python arac/lan_bilgi.py          -> JSON basar
"""
import json
import socket

PORT = 8091


def lan_adresleri():
    """Bu makinenin yerel IPv4 adreslerini döndürür (0.0.0.0 ve 127.* hariç)."""
    bulunan = []

    # 1) Varsayılan çıkış arayüzünü bulma (paket gönderilmez)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and ip != "0.0.0.0":
                bulunan.append(ip)
        finally:
            s.close()
    except Exception:
        pass

    # 2) Ana bilgisayar adı üzerinden tüm adresler
    try:
        _, _, ipler = socket.gethostbyname_ex(socket.gethostname())
        bulunan.extend(ipler)
    except Exception:
        pass

    # 3) Temizle: yinelenenleri at, 127.* ve 0.0.0.0'ı çıkar
    temiz = []
    for ip in bulunan:
        if not ip or ip.startswith("127.") or ip == "0.0.0.0":
            continue
        if ip.startswith("169.254."):   # APIPA - bağlantı yok
            continue
        if ip not in temiz:
            temiz.append(ip)
    return temiz


def lan_durum():
    """Panelin LAN adreslerini özetleyen sözlük döndürür."""
    adresler = lan_adresleri()
    birincil = adresler[0] if adresler else "127.0.0.1"
    return {
        "adresler": adresler,
        "port": PORT,
        "telefon_adresi": "http://%s:%d" % (birincil, PORT),
        "yerel_adres": "http://127.0.0.1:%d" % PORT,
        "not": ("Sunucu şu an yalnızca 127.0.0.1'e bağlıdır; bu adresler "
                "telefondan çalışması için sunucunun LAN'a açılması gerekir."),
        "bulunan_arayuz": len(adresler),
    }


if __name__ == "__main__":
    print(json.dumps(lan_durum(), ensure_ascii=False, indent=2))
