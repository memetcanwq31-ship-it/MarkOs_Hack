#!/usr/bin/env python3
# GERÇEK OSINT RECON — Termux uyumlu, bağımlılıksız (saf Python)
# Tüm sonuçlar gerçek sorgulardan gelir, simülasyon/hazır yanıt yoktur.                                                 
import os
import sys
import json                                                                                                             import struct
import socket
import urllib.request                                                                                                   import urllib.error

# ---------- ANSI Renkler (Termux uyumlu) ----------
R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
C  = "\033[96m"
W  = "\033[97m"
B  = "\033[1m"
S  = "\033[0m"
                                                                                                                        UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def temizle():                                                                                                              os.system("clear")


def banner():                                                                                                               print(f"{R}{B}{'='*64}")
    print(f"{R}{B} OSINT RECON — canlı sorgu,")
    print(f"{R}{B}{'='*64}{S}")


def http_get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


# =====================================================================
# MODÜL 1 — Gerçek IP / Alan Adı İstihbaratı (ip-api.com, ücretsiz)
# =====================================================================
def ip_locator():
    girdi = input(f"{C}Hedef IP veya alan adı: {W}").strip()
    if not girdi:
        print(f"{R}[!] Boş girdi.")
        return

    ip = girdi
    try:
        socket.inet_aton(girdi)  # IP formatında mı?
    except OSError:
        try:
            ip = socket.gethostbyname(girdi)
            print(f"{Y}[*] Alan adı çözümlendi -> {ip}")
        except socket.gaierror:
            print(f"{R}[!] Alan adı/IP çözümlenemedi.")
            return

    url = (f"http://ip-api.com/json/{ip}?fields=status,message,continent,country,"
           f"regionName,city,zip,lat,lon,timezone,currency,isp,org,as,mobile,"
           f"proxy,hosting,query")
    try:
        d = http_get_json(url)
    except Exception as e:
        print(f"{R}[!] Ağ hatası: {e}")
        return

    if d.get("status") != "success":
        print(f"{R}[!] Sorgu başarısız: {d.get('message', 'bilinmeyen')}")
        return

    print(f"\n{G}{B} ═[ GERÇEK IP İSTİHBARATI ]═{S}")
    for k, ad in [("query", "IP"), ("continent", "Kıta"), ("country", "Ülke"),
                  ("regionName", "Bölge"), ("city", "Şehir"), ("zip", "Posta Kodu"),
                  ("lat", "Enlem"), ("lon", "Boylam"), ("timezone", "Saat Dilimi"),
                  ("currency", "Para Birimi"), ("isp", "ISP"), ("org", "Organizasyon"),
                  ("as", "AS Numarası")]:
        print(f"  ├── {W}{ad:<14}: {d.get(k, '-')}")
    print(f"  ├── {W}Mobil Bağlantı : {'Evet' if d.get('mobile') else 'Hayır'}")
    print(f"  ├── {W}Proxy / VPN    : {'Evet' if d.get('proxy') else 'Hayır'}")
    print(f"  └── {W}Sunucu/Hosting : {'Evet' if d.get('hosting') else 'Hayır'}")


# =====================================================================
# MODÜL 2 — Gerçek Username Kontrolü (HTTP durum koduna dayalı)
# =====================================================================
SITELER = {
    "GitHub":   "https://github.com/{u}",
    "X/Twitter":"https://x.com/{u}",
    "Instagram":"https://www.instagram.com/{u}/",
    "Reddit":   "https://www.reddit.com/user/{u}",
    "TikTok":   "https://www.tiktok.com/@{u}",
    "Telegram": "https://t.me/{u}",
    "YouTube":  "https://www.youtube.com/@{u}",
    "Steam":    "https://steamcommunity.com/id/{u}",
    "Pinterest":"https://www.pinterest.com/{u}/",
    "Spotify":  "https://open.spotify.com/user/{u}",
}


def user_tracker():
    u = input(f"{C}Kullanıcı adı: {W}").strip()
    if not u:
        print(f"{R}[!] Boş girdi.")
        return

    print(f"{Y}[*] Siteler canlı sorgulanıyor...\n{S}")
    for ad, sablon in SITELER.items():
        url = sablon.format(u=u)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=8) as r:
                kod = r.getcode()
            durum = f"{G}VAR (HTTP {kod}){S}" if kod == 200 else f"{Y}BELİRSİZ (HTTP {kod}){S}"
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                durum = f"{R}YOK (HTTP {e.code}){S}"
            else:
                durum = f"{Y}Engelli/Kısıtlı (HTTP {e.code}){S}"
        except Exception:
            durum = f"{Y}Erişilemedi (timeout / engel){S}"
        print(f"  ├── {W}{ad:<11}: {durum}")

    print(f"{Y}[!] Not: 403/429 yanıtları 'yok' demek değildir; bazı siteler bot engeli uygular.{S}")


# =====================================================================
# MODÜL 3 — Gerçek EXIF / GPS Ayrıştırıcı (saf Python, Pillow'suz)
# =====================================================================
RAZON_TIP, RAZON8_TIP = 5, 10
TEMEL_ETIKETLER = {
    0x010F: "Üretici", 0x0110: "Model", 0x0131: "Yazılım",
    0x0132: "Değiştirme Tarihi", 0x9003: "Çekim Tarihi", 0x9004: "Dijitalleştirme",
    0x829A: "Pozlama Süresi", 0x829D: "F Değeri", 0x8827: "ISO",
    0x920A: "Odak Uzaklığı", 0xA002: "Genişlik", 0xA003: "Yükseklik",
}
GPS_ETIKETLER = {
    0x0001: "Enlem Ref", 0x0002: "Enlem", 0x0003: "Boylam Ref",
    0x0004: "Boylam", 0x0005: "Yükseklik Ref", 0x0006: "Yükseklik",
    0x0007: "GPS Zaman Damgası", 0x001B: "GPS Tarih",
}

TIPLER = {1: ("B", 1), 2: ("s", 1), 3: ("H", 2), 4: ("I", 4),
          5: ("II", 8), 7: ("B", 1), 9: ("i", 4), 10: ("ii", 8)}


def razon_degeri(veri, offset, endi, tip):
    """Rational (5) veya SRational (10) okur -> float"""
    p, q = struct.unpack_from(endi + ("I" if tip == 5 else "i"), veri, offset)
    return p / q if q != 0 else 0.0


def ifd_oku(veri, tiff_off, ifd_off, endi):
    """Bir IFD'deki etiketleri sözlük olarak döndürür."""
    etiketler = {}
    try:
        adet = struct.unpack_from(endi + "H", veri, ifd_off)[0]
    except struct.error:
        return etiketler
    for i in range(adet):
        entry = ifd_off + 2 + i * 12
        try:
            tag, tip, sayi = struct.unpack_from(endi + "HHI", veri, entry)
        except struct.error:
            break
        if tip not in TIPLER:
            continue
        fmt, boyut = TIPLER[tip]
        toplam = boyut * sayi
        val_off = entry + 8
        if toplam > 4:
            try:
                val_off = tiff_off + struct.unpack_from(endi + "I", veri, entry + 8)[0]
            except struct.error:
                continue
        try:
            if tip == 2:  # ASCII
                ham = veri[val_off:val_off + sayi]
                etiketler[tag] = ham.split(b"\x00")[0].decode("utf-8", errors="replace")
            elif tip in (5, 10):
                etiketler[tag] = [razon_degeri(veri, val_off + k * 8, endi, tip)
                                  for k in range(sayi)]
            else:
                etiketler[tag] = list(struct.unpack_from(endi + fmt * sayi, veri, val_off))
        except (struct.error, IndexError):
            continue
    return etiketler


def exif_oku(yol):
    """JPEG dosyasından EXIF TIFF yapısını çözer. Dict döndürür."""
    with open(yol, "rb") as f:
        veri = f.read()

    if veri[:2] != b"\xff\xd8":
        raise ValueError("Bu bir JPEG dosyası değil (EXIF tarayıcı yalnızca JPEG okur)")

    # APP1 / Exif segmentini bul
    off = 2
    tiff = None
    while off + 4 <= len(veri):
        if veri[off] != 0xFF:
            break
        marker = veri[off + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            off += 2
            continue
        if marker == 0xDA:  # SOS -> EXIF bitti
            break
        seg_uzun = struct.unpack_from(">H", veri, off + 2)[0]
        if marker == 0xE1 and veri[off + 4:off + 10] == b"Exif\x00\x00":
            tiff = off + 10
            break
        off += 2 + seg_uzun

    if tiff is None:
        return {}

    # TIFF byte order
    if veri[tiff:tiff + 2] == b"II":
        endi = "<"
    elif veri[tiff:tiff + 2] == b"MM":
        endi = ">"
    else:
        raise ValueError("Geçersiz TIFF başlığı")

    ifd0_rel = struct.unpack_from(endi + "I", veri, tiff + 4)[0]
    ifd0 = ifd_oku(veri, tiff, tiff + ifd0_rel, endi)

    sonuc = {"temel": {}, "gps": {}}
    for tag, deger in ifd0.items():
        if tag in TEMEL_ETIKETLER:
            sonuc["temel"][TEMEL_ETIKETLER[tag]] = deger

    # GPSInfo alt-IFD işaretçisi (0x8825)
    if 0x8825 in ifd0 and isinstance(ifd0[0x8825], list):
        gps_rel = ifd0[0x8825][0]
        gps_ifd = ifd_oku(veri, tiff, tiff + gps_rel, endi)
        for tag, deger in gps_ifd.items():
            if tag in GPS_ETIKETLER:
                sonuc["gps"][GPS_ETIKETLER[tag]] = deger

    return sonuc


def dereceye_cevir(liste):
    d, m, s = (listelene := list(liste) + [0] * (3 - len(liste)))
    return float(d) + float(m) / 60 + float(s) / 3600


def geotag_parser():
    yol = input(f"{C}Resim dosyasının yolu: {W}").strip().strip('"').strip("'")
    if not yol:
        print(f"{R}[!] Boş girdi.")
        return
    if not os.path.isfile(yol):
        print(f"{R}[!] Dosya bulunamadı: {yol}")
        return

    try:
        exif = exif_oku(yol)
    except ValueError as e:
        print(f"{R}[!] {e}")
        return
    except Exception as e:
        print(f"{R}[!] EXIF okunamadı: {e}")
        return

    temel, gps = exif["temel"], exif["gps"]

    if not temel and not gps:
        print(f"{Y}[!] EXIF verisi bulunamadı (temizlenmiş veya desteklenmeyen format).{S}")
        return

    print(f"\n{G}{B} ═[ GERÇEK EXIF VERİSİ ]═{S}")
    if temel:
        for k, v in temel.items():
            print(f"  ├── {W}{k:<18}: {v}")
    else:
        print(f"  ├── {W}Temel etiket: yok")

    if not gps:
        print(f"  └── {Y}GPS koordinatı yok.{S}")
        return

    lat = lon = None
    if "Enlem" in gps and "Boylam" in gps:
        lat = dereceye_cevir(gps["Enlem"])
        lon = dereceye_cevir(gps["Boylam"])
        if gps.get("Enlem Ref") == "S":
            lat = -lat
        if gps.get("Boylam Ref") == "W":
            lon = -lon

        print(f"  ├── {W}Enlem            : {lat:.6f}")
        print(f"  ├── {W}Boylam           : {lon:.6f}")
        if "Yükseklik" in gps:
            print(f"  ├── {W}Yükseklik        : {gps['Yükseklik'][0]:.1f} m")
        print(f"  ├── {W}Harita Bağlantısı: https://www.google.com/maps?q={lat},{lon}")

        # Koordinattan gerçek adres (OpenStreetMap Nominatim)
        try:
            d = http_get_json(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
            )
            print(f"  ├── {W}Çözümlenen Adres : {d.get('display_name', '-')}")
        except Exception:
            print(f"  ├── {Y}Adres çözümlenemedi (ağ hatası).{S}")
    else:
        print(f"  ├── {Y}GPS etiketi eksik/okunamadı.{S}")

    print(f"  └── {W}GPS Tarih/Zaman  : {gps.get('GPS Tarih', '-')} {gps.get('GPS Zaman Damgası', '')}")


# =====================================================================
# ANA DÖNGÜ
# =====================================================================
MODULLER = {
    "1": ("Global IP Locator (gerçek sorgu)", ip_locator),
    "2": ("Username Tracker (gerçek HTTP kontrolü)", user_tracker),
    "3": ("GeoTags EXIF Parser (gerçek dosya okuma)", geotag_parser),
}


def main():
    while True:
        temizle()
        banner()
        for k, (ad, _) in MODULLER.items():
            print(f" {W}[{k}] {C}{ad}")
        print(f" {W}[0] Çıkış\n{S}")

        secim = input(f"{G}Seçim: {W}").strip()
        if secim == "0":
            print(f"{G}Çıkılıyor...{S}")
            sys.exit(0)
        if secim in MODULLER:
            MODULLER[secim][1]()
        else:
            print(f"{R}[!] Geçersiz seçim.{S}")

        input(f"\n{Y}Menüye dönmek için ENTER'a bas...{S}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}Kesinti algılandı, çıkılıyor...{S}")
        sys.exit(0)
