
import os

base_path = "/mnt/agents/output/etternetlog"
os.makedirs(f"{base_path}/cybersec_tools", exist_ok=True)
os.makedirs(f"{base_path}/pentest_tools", exist_ok=True)
os.makedirs(f"{base_path}/custom_tools", exist_ok=True)

# =================== CYBERSEC TOOLS (40) ===================

cybersec = {
"01_log_analyzer.py": '''#!/usr/bin/env python3
"""Log Analyzer - Suspicious activity and error detection."""
import re, sys, argparse, collections
from datetime import datetime

PATTERNS = {
    "error": re.compile(r"ERROR|CRITICAL|FATAL", re.I),
    "failed_login": re.compile(r"Failed password|authentication failure|login failed", re.I),
    "sql_injection": re.compile(r"(\%27)|(\')|(\-\-)|(\%23)|(#)", re.I),
    "xss_attempt": re.compile(r"<script|javascript:|onerror=|onload=", re.I),
    "privilege_escalation": re.compile(r"sudo|su -|chmod 777|chown root", re.I)
}

def analyze_log(filepath):
    results = collections.defaultdict(list)
    with open(filepath, 'r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    results[name].append((i, line.strip()))
    return results

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Etternetlog Log Analyzer")
    p.add_argument("file", help="Log file path")
    args = p.parse_args()
    res = analyze_log(args.file)
    for cat, items in res.items():
        print(f"\n[!] {cat.upper()}: {len(items)} matches")
        for line_no, line in items[:5]:
            print(f"   Line {line_no}: {line[:100]}")
''',

"02_file_integrity_monitor.py": '''#!/usr/bin/env python3
"""File Integrity Monitor - Detect unauthorized file changes."""
import hashlib, json, os, sys, argparse, time

DB_FILE = ".fim_db.json"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan(directory):
    db = {}
    for root, _, files in os.walk(directory):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                db[fpath] = hash_file(fpath)
            except Exception:
                pass
    return db

def check(directory):
    if not os.path.exists(DB_FILE):
        print("[+] Baseline creating...")
        json.dump(scan(directory), open(DB_FILE, 'w'), indent=2)
        return
    baseline = json.load(open(DB_FILE))
    current = scan(directory)
    changed = [f for f in current if f in baseline and baseline[f] != current[f]]
    new_files = [f for f in current if f not in baseline]
    missing = [f for f in baseline if f not in current]
    for c in changed: print(f"[CHANGED] {c}")
    for n in new_files: print(f"[NEW] {n}")
    for m in missing: print(f"[MISSING] {m}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    args = p.parse_args()
    check(args.directory)
''',

"03_network_analyzer.py": '''#!/usr/bin/env python3
"""Network Traffic Analyzer - PCAP or live stats."""
import argparse, socket, struct, time

def analyze_live(interface=None):
    print("[+] Live capture simulation (requires scapy for full PCAP)")
    print("[*] Use: python3 -m pip install scapy && modify script for full capture")
    # Basic socket stats
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print(f"[+] Local IP: {s.getsockname()[0]}")
        s.close()
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--interface", default=None)
    args = p.parse_args()
    analyze_live(args.interface)
''',

"04_port_scanner_defensive.py": '''#!/usr/bin/env python3
"""Defensive Port Scanner - Audit your own network."""
import socket, argparse, concurrent.futures

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return port if s.connect_ex((ip, port)) == 0 else None
    except:
        return None

def scan(ip, ports):
    print(f"[+] Scanning {ip}...")
    with concurrent.futures.ThreadPoolExecutor(100) as ex:
        results = ex.map(lambda p: scan_port(ip, p), ports)
    open_ports = [r for r in results if r]
    print(f"[+] Open ports: {open_ports}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("ip")
    p.add_argument("--ports", default="1-1024")
    args = p.parse_args()
    start, end = map(int, args.ports.split('-'))
    scan(args.ip, range(start, end+1))
''',

"05_ssl_checker.py": '''#!/usr/bin/env python3
"""SSL/TLS Certificate Checker."""
import ssl, socket, argparse, datetime

def check_ssl(hostname, port=443):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (not_after - datetime.datetime.utcnow()).days
                print(f"[+] Host: {hostname}")
                print(f"[+] Protocol: {version}")
                print(f"[+] Cipher: {cipher[0]}")
                print(f"[+] Expires: {cert['notAfter']} ({days_left} days left)")
                print(f"[+] Subject: {cert.get('subject')}")
                if days_left < 30:
                    print("[!] WARNING: Certificate expires soon!")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("host")
    p.add_argument("--port", type=int, default=443)
    args = p.parse_args()
    check_ssl(args.host, args.port)
''',

"06_password_strength.py": '''#!/usr/bin/env python3
"""Password Strength Checker."""
import re, argparse, math

def check_strength(password):
    score = 0
    checks = {
        "length": len(password) >= 12,
        "upper": bool(re.search(r'[A-Z]', password)),
        "lower": bool(re.search(r'[a-z]', password)),
        "digit": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    score = sum(checks.values())
    entropy = len(password) * math.log2(94) if len(password) > 0 else 0
    print(f"[+] Score: {score}/5")
    print(f"[+] Entropy: {entropy:.1f} bits")
    for k, v in checks.items():
        print(f"   {'[OK]' if v else '[FAIL]'} {k}")
    if score < 3 or entropy < 40:
        print("[!] WEAK password")
    elif score < 5:
        print("[*] MODERATE password")
    else:
        print("[+] STRONG password")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("password")
    args = p.parse_args()
    check_strength(args.password)
''',

"07_firewall_analyzer.py": '''#!/usr/bin/env python3
"""Firewall Rule Analyzer - Basic iptables/JSON rule audit."""
import argparse, json, re

def analyze_rules(rulefile):
    with open(rulefile) as f:
        rules = json.load(f)
    issues = []
    for rule in rules:
        if rule.get("action") == "ACCEPT" and rule.get("source") == "0.0.0.0/0":
            if rule.get("port") in [22, 3389, 23, 21]:
                issues.append(f"[!] Wide open admin port: {rule}")
        if rule.get("action") == "ACCEPT" and not rule.get("logging", False):
            issues.append(f"[*] No logging for rule: {rule}")
    print(f"[+] Analyzed {len(rules)} rules, {len(issues)} issues found.")
    for i in issues[:10]:
        print(i)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("rulefile")
    args = p.parse_args()
    analyze_rules(args.rulefile)
''',

"08_yara_scanner.py": '''#!/usr/bin/env python3
"""YARA Rule Scanner - File pattern matching."""
import argparse, os, re

# Built-in simple YARA-like rules
RULES = {
    "suspicious_strings": [b"cmd.exe", b"powershell.exe", b"/bin/sh", b"eval("],
    "pe_header": re.compile(b"MZ"),
    "pdf_js": re.compile(b"/JavaScript|/JS", re.I)
}

def scan_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        matches = []
        for name, pattern in RULES.items():
            if isinstance(pattern, list):
                if any(p in data for p in pattern):
                    matches.append(name)
            elif pattern.search(data):
                matches.append(name)
        return matches
    except Exception:
        return []

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    args = p.parse_args()
    for root, _, files in os.walk(args.path):
        for f in files:
            fp = os.path.join(root, f)
            m = scan_file(fp)
            if m:
                print(f"[MATCH] {fp}: {m}")
''',

"09_memory_dump_strings.py": '''#!/usr/bin/env python3
"""Memory Dump String Extractor."""
import argparse, re, string

def extract_strings(filepath, min_len=4):
    with open(filepath, 'rb') as f:
        data = f.read()
    # ASCII strings
    ascii_chars = string.printable.encode()
    results = []
    current = bytearray()
    for byte in data:
        if byte in ascii_chars:
            current.append(byte)
        else:
            if len(current) >= min_len:
                results.append(current.decode('ascii', errors='ignore'))
            current = bytearray()
    for s in results[:50]:
        print(s)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dumpfile")
    p.add_argument("--min", type=int, default=4)
    args = p.parse_args()
    extract_strings(args.dumpfile, args.min)
''',

"10_registry_monitor.py": '''#!/usr/bin/env python3
"""Windows Registry Monitor (requires Windows + winreg)."""
import argparse, json, os, sys

def monitor_keys(keylist_file):
    if sys.platform != "win32":
        print("[!] This tool requires Windows.")
        return
    import winreg
    with open(keylist_file) as f:
        keys = json.load(f)
    for k in keys:
        try:
            hkey = getattr(winreg, k["hive"])
            key = winreg.OpenKey(hkey, k["path"])
            val = winreg.QueryValueEx(key, k["value"])
            print(f"[+] {k['path']}\\{k['value']} = {val[0]}")
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[!] {k['path']}: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("keylist")
    args = p.parse_args()
    monitor_keys(args.keylist)
''',

"11_dns_security_check.py": '''#!/usr/bin/env python3
"""DNS Security Checker - DNSSEC and basic spoofing detection."""
import dns.resolver, argparse, socket

def check_dns(domain):
    print(f"[+] Checking {domain}")
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for r in answers:
            print(f"[+] A record: {r}")
    except Exception as e:
        print(f"[!] A record error: {e}")
    try:
        dns.resolver.resolve(domain, 'DNSKEY')
        print("[+] DNSSEC appears enabled (DNSKEY found)")
    except:
        print("[!] DNSSEC not detected")
    try:
        mx = dns.resolver.resolve(domain, 'MX')
        for m in mx:
            print(f"[+] MX: {m}")
    except:
        pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    args = p.parse_args()
    check_dns(args.domain)
''',

"12_backup_verifier.py": '''#!/usr/bin/env python3
"""Backup Integrity Verifier."""
import hashlib, json, os, argparse

MANIFEST = "backup_manifest.json"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def create_manifest(backup_dir):
    manifest = {}
    for root, _, files in os.walk(backup_dir):
        for f in files:
            fp = os.path.join(root, f)
            manifest[fp] = hash_file(fp)
    json.dump(manifest, open(MANIFEST, 'w'), indent=2)
    print(f"[+] Manifest created: {MANIFEST}")

def verify(backup_dir):
    manifest = json.load(open(MANIFEST))
    current = {}
    for root, _, files in os.walk(backup_dir):
        for f in files:
            fp = os.path.join(root, f)
            current[fp] = hash_file(fp)
    for f, h in manifest.items():
        if f not in current:
            print(f"[MISSING] {f}")
        elif current[f] != h:
            print(f"[CORRUPT] {f}")
    print("[+] Verification complete")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("backup_dir")
    p.add_argument("--create", action="store_true")
    args = p.parse_args()
    if args.create:
        create_manifest(args.backup_dir)
    else:
        verify(args.backup_dir)
''',

"13_patch_checker.py": '''#!/usr/bin/env python3
"""System Patch Checker - Linux apt/yum check simulation."""
import subprocess, argparse, sys, platform

def check_patches():
    system = platform.system()
    if system == "Linux":
        try:
            result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True)
            lines = [l for l in result.stdout.splitlines() if "upgradable" in l]
            print(f"[+] {len(lines)} packages can be upgraded (apt)")
            for l in lines[:10]:
                print(f"   {l}")
        except FileNotFoundError:
            try:
                result = subprocess.run(["yum", "check-update"], capture_output=True, text=True)
                print("[+] yum check-update output:")
                print(result.stdout[:1000])
            except FileNotFoundError:
                print("[!] No supported package manager found")
    elif system == "Windows":
        print("[*] Use 'Get-WindowsUpdate' or 'sconfig' on Windows Server")
    else:
        print(f"[!] Unsupported system: {system}")

if __name__ == "__main__":
    check_patches()
''',

"14_ioc_scanner.py": '''#!/usr/bin/env python3
"""IOC Scanner - Indicator of Compromise file/network scanner."""
import argparse, os, json, re, socket, hashlib

def load_iocs(ioc_file):
    with open(ioc_file) as f:
        return json.load(f)

def scan_files(directory, iocs):
    hashes = iocs.get("file_hashes", [])
    filenames = iocs.get("filenames", [])
    for root, _, files in os.walk(directory):
        for f in files:
            fp = os.path.join(root, f)
            if any(fn in f for fn in filenames):
                print(f"[IOC MATCH] Filename: {fp}")
            try:
                h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
                if h in hashes:
                    print(f"[IOC MATCH] Hash: {fp}")
            except:
                pass

def scan_network(iocs):
    ips = iocs.get("ip_addresses", [])
    for ip in ips:
        try:
            socket.gethostbyname(ip)
            print(f"[RESOLVED] {ip} is reachable (check if malicious)")
        except:
            pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ioc", required=True)
    p.add_argument("--path", default="/")
    args = p.parse_args()
    iocs = load_iocs(args.ioc)
    scan_files(args.path, iocs)
    scan_network(iocs)
''',

"15_syslog_server.py": '''#!/usr/bin/env python3
"""Simple Syslog Server - UDP 514 collector."""
import socket, argparse, datetime

def start_server(host="0.0.0.0", port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[+] Syslog server listening on {host}:{port}")
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            msg = data.decode('utf-8', errors='ignore')
            ts = datetime.datetime.now().isoformat()
            print(f"[{ts}] {addr[0]}: {msg.strip()}")
    except KeyboardInterrupt:
        print("\n[!] Stopping server")
        sock.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=514)
    args = p.parse_args()
    start_server(args.host, args.port)
''',

"16_honeypot.py": '''#!/usr/bin/env python3
"""Simple TCP Honeypot - Logs connection attempts."""
import socket, argparse, datetime, threading

def handle_client(conn, addr, logfile):
    ts = datetime.datetime.now().isoformat()
    log = f"[{ts}] Connection from {addr}"
    print(log)
    with open(logfile, 'a') as f:
        f.write(log + "\n")
    try:
        conn.send(b"220 Welcome\\n")
        data = conn.recv(1024)
        if data:
            with open(logfile, 'a') as f:
                f.write(f"[{ts}] Data from {addr}: {data.decode('utf-8', errors='ignore').strip()}\\n")
    except:
        pass
    conn.close()

def start_honeypot(port=8080, logfile="honeypot.log"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen(5)
    print(f"[+] Honeypot listening on port {port}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr, logfile)).start()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--log", default="honeypot.log")
    args = p.parse_args()
    start_honeypot(args.port, args.log)
''',

"17_baseline_checker.py": '''#!/usr/bin/env python3
"""Security Baseline Checker."""
import argparse, json, os, platform

def check_baseline(baseline_file):
    with open(baseline_file) as f:
        rules = json.load(f)
    system = platform.system().lower()
    for rule in rules:
        if rule.get("os") and rule["os"] != system:
            continue
        check = rule["check"]
        if check == "file_exists":
            exists = os.path.exists(rule["path"])
            status = "PASS" if exists == rule["expected"] else "FAIL"
        elif check == "permission":
            try:
                mode = oct(os.stat(rule["path"]).st_mode)[-3:]
                status = "PASS" if mode == rule["expected"] else "FAIL"
            except:
                status = "ERROR"
        else:
            status = "UNKNOWN"
        print(f"[{status}] {rule['name']}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("baseline")
    args = p.parse_args()
    check_baseline(args.baseline)
''',

"18_usb_monitor.py": '''#!/usr/bin/env python3
"""USB Device Monitor (Linux udev simulation via dmesg)."""
import subprocess, time, argparse, re

def monitor():
    print("[+] Monitoring USB connections (Linux dmesg tail)")
    try:
        proc = subprocess.Popen(["dmesg", "-w"], stdout=subprocess.PIPE, text=True)
        for line in proc.stdout:
            if "usb" in line.lower() and ("new" in line.lower() or "disconnect" in line.lower()):
                print(f"[USB EVENT] {line.strip()}")
    except KeyboardInterrupt:
        print("\n[!] Stopped")

if __name__ == "__main__":
    monitor()
''',

"19_process_monitor.py": '''#!/usr/bin/env python3
"""Suspicious Process Monitor."""
import psutil, argparse, time

SUSPICIOUS_NAMES = ["mimikatz", "mimilib", "pwdump", "nc.exe", "netcat", "socat"]
SUSPICIOUS_PATHS = ["/tmp/", "/var/tmp/", "C:\\\\Users\\\\Public\\\\"]

def check():
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ""
            exe = proc.info['exe'] or ""
            if any(s in name for s in SUSPICIOUS_NAMES):
                print(f"[!] SUSPICIOUS NAME: {proc.info}")
            if any(s in exe for s in SUSPICIOUS_PATHS):
                print(f"[!] SUSPICIOUS PATH: {proc.info}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == "__main__":
    check()
''',

"20_entropy_analyzer.py": '''#!/usr/bin/env python3
"""File Entropy Analyzer - Detect encrypted/packed files."""
import math, os, argparse

def entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p = data.count(bytes([x])) / len(data)
        if p > 0:
            entropy += -p * math.log2(p)
    return entropy

def scan(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            fp = os.path.join(root, f)
            try:
                with open(fp, 'rb') as file:
                    data = file.read(8192)
                    e = entropy(data)
                    if e > 7.5:
                        print(f"[HIGH ENTROPY {e:.2f}] {fp}")
            except:
                pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    args = p.parse_args()
    scan(args.directory)
''',

"21_email_header_analyzer.py": '''#!/usr/bin/env python3
"""Email Header Security Analyzer."""
import argparse, re

def analyze_header(header_file):
    with open(header_file) as f:
        header = f.read()
    checks = {
        "SPF": bool(re.search(r'spf=pass', header, re.I)),
        "DKIM": bool(re.search(r'dkim=pass', header, re.I)),
        "DMARC": bool(re.search(r'dmarc=pass', header, re.I)),
        "TLS": bool(re.search(r'tls=1|version=TLS', header, re.I)),
        "Suspicious_Origin": bool(re.search(r'X-Originating-IP|X-Forwarded-For', header, re.I))
    }
    for k, v in checks.items():
        print(f"{'[OK]' if v else '[FAIL]'} {k}")
    from_match = re.search(r'From: (.+)', header)
    if from_match:
        print(f"[+] From: {from_match.group(1).strip()}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("header_file")
    args = p.parse_args()
    analyze_header(args.header_file)
''',

"22_url_reputation.py": '''#!/usr/bin/env python3
"""URL Reputation Checker - Basic domain age and redirect analysis."""
import argparse, urllib.request, ssl, datetime
from urllib.parse import urlparse

def check_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    print(f"[+] Checking {domain}")
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        print(f"[+] Status: {resp.status}")
        print(f"[+] Final URL: {resp.geturl()}")
        if resp.geturl() != url:
            print("[!] Redirect detected")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    check_url(args.url)
''',

"23_shodan_lookup.py": '''#!/usr/bin/env python3
"""Shodan API Lookup."""
import argparse, urllib.request, json

def lookup(api_key, query):
    url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={urllib.parse.quote(query)}"
    try:
        resp = urllib.request.urlopen(url)
        data = json.loads(resp.read())
        print(f"[+] Total results: {data['total']}")
        for match in data['matches'][:5]:
            print(f"   {match['ip_str']}:{match.get('port','?')} - {match.get('org','N/A')}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    import urllib.parse
    p = argparse.ArgumentParser()
    p.add_argument("--key", required=True)
    p.add_argument("--query", default="apache")
    args = p.parse_args()
    lookup(args.key, args.query)
''',

"24_cert_transparency.py": '''#!/usr/bin/env python3
"""Certificate Transparency Log Monitor."""
import argparse, urllib.request, json

def check_ct(domain):
    url = f"https://crt.sh/?q={domain}&output=json"
    try:
        resp = urllib.request.urlopen(url)
        data = json.loads(resp.read())
        seen = set()
        for entry in data[:20]:
            name = entry["name_value"]
            if name not in seen:
                seen.add(name)
                print(f"[+] Cert: {name} (ID: {entry['id']})")
        print(f"[+] Total unique entries: {len(seen)}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    args = p.parse_args()
    check_ct(args.domain)
''',

"25_windows_event_analyzer.py": '''#!/usr/bin/env python3
"""Windows Event Log Analyzer (requires Windows + pywin32)."""
import argparse, sys

def analyze_log(logtype="Security"):
    if sys.platform != "win32":
        print("[!] Windows only")
        return
    import win32evtlog
    hand = win32evtlog.OpenEventLog(None, logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand, flags, 0)
    for ev in events[:20]:
        print(f"[{ev.TimeGenerated}] EventID:{ev.EventID} Source:{ev.SourceName}")
    win32evtlog.CloseEventLog(hand)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--log", default="Security")
    args = p.parse_args()
    analyze_log(args.log)
''',

"26_linux_audit_parser.py": '''#!/usr/bin/env python3
"""Linux Audit Log Parser."""
import argparse, re

def parse_audit(audit_file):
    with open(audit_file) as f:
        for line in f:
            if "type=SYSCALL" in line:
                exe = re.search(r'exe="([^"]+)"', line)
                auid = re.search(r'auid=(\d+)', line)
                if exe:
                    print(f"[SYSCALL] exe={exe.group(1)} auid={auid.group(1) if auid else '?'}")
            elif "type=USER_LOGIN" in line:
                acct = re.search(r'acct="([^"]+)"', line)
                res = re.search(r'res=([A-Z]+)', line)
                print(f"[LOGIN] acct={acct.group(1) if acct else '?'} result={res.group(1) if res else '?'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("audit_file")
    args = p.parse_args()
    parse_audit(args.audit_file)
''',

"27_threat_intel_feed.py": '''#!/usr/bin/env python3
"""Threat Intelligence Feed Parser."""
import argparse, urllib.request

def fetch_feed(url):
    try:
        resp = urllib.request.urlopen(url)
        data = resp.read().decode('utf-8', errors='ignore')
        lines = [l.strip() for l in data.splitlines() if l.strip() and not l.startswith('#')]
        print(f"[+] Fetched {len(lines)} IOCs")
        for ioc in lines[:20]:
            print(f"   {ioc}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="https://openphish.com/feed.txt")
    args = p.parse_args()
    fetch_feed(args.url)
''',

"28_vuln_scanner_local.py": '''#!/usr/bin/env python3
"""Local Vulnerability Scanner - Check for common misconfigurations."""
import os, platform, argparse

def scan():
    issues = []
    if platform.system() == "Linux":
        if os.path.exists("/etc/shadow"):
            mode = oct(os.stat("/etc/shadow").st_mode)[-3:]
            if mode != "640" and mode != "600":
                issues.append(f"[!] /etc/shadow permissions: {mode}")
        if os.path.exists("/etc/ssh/sshd_config"):
            with open("/etc/ssh/sshd_config") as f:
                cfg = f.read()
                if "PermitRootLogin yes" in cfg:
                    issues.append("[!] SSH root login enabled")
                if "PasswordAuthentication yes" in cfg:
                    issues.append("[!] SSH password auth enabled")
    elif platform.system() == "Windows":
        print("[*] Run additional checks manually on Windows")
    if issues:
        for i in issues:
            print(i)
    else:
        print("[+] No obvious local misconfigurations found")

if __name__ == "__main__":
    scan()
''',

"29_av_signature_check.py": '''#!/usr/bin/env python3
"""Antivirus Signature Update Checker."""
import subprocess, platform, argparse

def check():
    sys = platform.system()
    if sys == "Linux":
        try:
            r = subprocess.run(["freshclam", "--version"], capture_output=True, text=True)
            print(f"[+] ClamAV: {r.stdout.strip()}")
        except FileNotFoundError:
            print("[!] ClamAV not found")
    elif sys == "Windows":
        try:
            r = subprocess.run(["MpCmdRun.exe", "-SignatureUpdateCheck"], capture_output=True, text=True)
            print(f"[+] Windows Defender: {r.stdout[:500]}")
        except FileNotFoundError:
            print("[!] Windows Defender MpCmdRun not found")
    else:
        print(f"[!] Platform {sys} not supported")

if __name__ == "__main__":
    check()
''',

"30_secure_eraser.py": '''#!/usr/bin/env python3
"""Secure File Eraser - Overwrite before delete."""
import os, argparse

def secure_erase(filepath, passes=3):
    size = os.path.getsize(filepath)
    with open(filepath, 'r+b') as f:
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(size))
            f.flush()
    os.remove(filepath)
    print(f"[+] Securely erased: {filepath}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--passes", type=int, default=3)
    args = p.parse_args()
    secure_erase(args.file, args.passes)
''',

"31_pcap_analyzer.py": '''#!/usr/bin/env python3
"""PCAP Analyzer - Basic statistics (requires scapy for full parsing)."""
import argparse, struct

def analyze_pcap(pcap_file):
    with open(pcap_file, 'rb') as f:
        global_header = f.read(24)
        if global_header[:4] not in (b'\\xa1\\xb2\\xc3\\xd4', b'\\xd4\\xc3\\xb2\\xa1'):
            print("[!] Not a valid PCAP file")
            return
        magic = global_header[:4]
        print(f"[+] Magic: {magic.hex()}")
        print(f"[+] This tool requires 'scapy' for deep packet inspection.")
        print(f"[*] Install: pip install scapy")
        print(f"[*] Quick stat: File size {os.path.getsize(pcap_file)} bytes")

if __name__ == "__main__":
    import os
    p = argparse.ArgumentParser()
    p.add_argument("pcap")
    args = p.parse_args()
    analyze_pcap(args.pcap)
''',

"32_arp_monitor.py": '''#!/usr/bin/env python3
"""ARP Table Monitor - Detect ARP changes."""
import subprocess, time, argparse, re

def get_arp_table():
    try:
        r = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        entries = {}
        for line in r.stdout.splitlines():
            m = re.search(r'\\((.+?)\\) at ([0-9a-f:]{17})', line)
            if m:
                entries[m.group(1)] = m.group(2)
        return entries
    except:
        return {}

def monitor():
    baseline = get_arp_table()
    print("[+] ARP baseline captured. Monitoring...")
    try:
        while True:
            time.sleep(10)
            current = get_arp_table()
            for ip, mac in current.items():
                if ip in baseline and baseline[ip] != mac:
                    print(f"[!] ARP CHANGE: {ip} {baseline[ip]} -> {mac}")
            baseline = current
    except KeyboardInterrupt:
        print("\n[!] Stopped")

if __name__ == "__main__":
    monitor()
''',

"33_login_anomaly.py": '''#!/usr/bin/env python3
"""Login Anomaly Detector - Analyze auth logs."""
import argparse, re, collections
from datetime import datetime

def detect_anomalies(logfile):
    attempts = collections.defaultdict(list)
    with open(logfile) as f:
        for line in f:
            m = re.search(r'Failed password for .* from ([\\d.]+)', line)
            if m:
                ip = m.group(1)
                attempts[ip].append(line)
    for ip, lines in attempts.items():
        if len(lines) > 5:
            print(f"[!] Brute-force suspect: {ip} ({len(lines)} failed attempts)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("logfile")
    args = p.parse_args()
    detect_anomalies(args.logfile)
''',

"34_bandwidth_anomaly.py": '''#!/usr/bin/env python3
"""Bandwidth Anomaly Detector."""
import psutil, time, argparse

def monitor(interface="eth0", threshold=100*1024*1024):
    print(f"[+] Monitoring {interface} (threshold: {threshold/1024/1024:.1f} MB/s)")
    old = psutil.net_io_counters(pernic=True).get(interface)
    if not old:
        print(f"[!] Interface {interface} not found")
        return
    try:
        while True:
            time.sleep(1)
            new = psutil.net_io_counters(pernic=True).get(interface)
            if not new:
                continue
            sent = new.bytes_sent - old.bytes_sent
            recv = new.bytes_recv - old.bytes_recv
            if sent > threshold or recv > threshold:
                print(f"[!] ANOMALY: Sent={sent/1024/1024:.1f}MB/s Recv={recv/1024/1024:.1f}MB/s")
            old = new
    except KeyboardInterrupt:
        print("\n[!] Stopped")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--interface", default="eth0")
    p.add_argument("--threshold", type=int, default=104857600)
    args = p.parse_args()
    monitor(args.interface, args.threshold)
''',

"35_config_security_check.py": '''#!/usr/bin/env python3
"""Configuration File Security Checker."""
import argparse, re

DANGEROUS = [
    (r'password\s*=\s*"[^"]+"', "Hardcoded password"),
    (r'secret\s*=\s*"[^"]+"', "Hardcoded secret"),
    (r'api_key\s*=\s*"[^"]+"', "Hardcoded API key"),
    (r'DEBUG\s*=\s*True', "Debug mode enabled"),
    (r'eval\s*\(', "Dangerous eval() usage")
]

def check_config(config_file):
    with open(config_file) as f:
        content = f.read()
    for pattern, desc in DANGEROUS:
        if re.search(pattern, content, re.I):
            print(f"[!] {desc} found in {config_file}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("config")
    args = p.parse_args()
    check_config(args.config)
''',

"36_docker_security_scan.py": '''#!/usr/bin/env python3
"""Docker Security Scanner - Check running containers."""
import subprocess, argparse, json

def scan():
    try:
        r = subprocess.run(["docker", "ps", "--format", "json"], capture_output=True, text=True)
        containers = [json.loads(l) for l in r.stdout.strip().splitlines() if l.strip()]
        print(f"[+] Found {len(containers)} containers")
        for c in containers:
            print(f"   {c['Names']} - {c['Image']} - {c['Status']}")
            # Check privileged
            inspect = subprocess.run(["docker", "inspect", c['ID']], capture_output=True, text=True)
            data = json.loads(inspect.stdout)
            host_config = data[0].get("HostConfig", {})
            if host_config.get("Privileged"):
                print(f"[!]   {c['Names']} is PRIVILEGED")
            if host_config.get("PublishAllPorts"):
                print(f"[!]   {c['Names']} publishes all ports")
    except FileNotFoundError:
        print("[!] Docker not found")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    scan()
''',

"37_aws_s3_checker.py": '''#!/usr/bin/env python3
"""AWS S3 Bucket Permission Checker."""
import argparse, subprocess, json

def check_bucket(bucket):
    try:
        r = subprocess.run(["aws", "s3api", "get-bucket-acl", "--bucket", bucket], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[!] Error: {r.stderr}")
            return
        data = json.loads(r.stdout)
        for grant in data.get("Grants", []):
            grantee = grant.get("Grantee", {})
            if grantee.get("URI", "").endswith("AllUsers"):
                print(f"[!] Bucket {bucket} is PUBLIC (AllUsers)")
            if grantee.get("URI", "").endswith("AuthenticatedUsers"):
                print(f"[!] Bucket {bucket} is open to AuthenticatedUsers")
        print(f"[+] ACL check complete for {bucket}")
    except FileNotFoundError:
        print("[!] AWS CLI not found")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("bucket")
    args = p.parse_args()
    check_bucket(args.bucket)
''',

"38_hash_verifier.py": '''#!/usr/bin/env python3
"""File Hash Verifier - Compare SHA256/MD5."""
import hashlib, argparse

def verify(filepath, expected_hash, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    actual = h.hexdigest()
    if actual.lower() == expected_hash.lower():
        print(f"[+] MATCH: {actual}")
    else:
        print(f"[!] MISMATCH: expected {expected_hash}, got {actual}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("hash")
    p.add_argument("--algo", default="sha256")
    args = p.parse_args()
    verify(args.file, args.hash, args.algo)
''',

"39_network_mapper.py": '''#!/usr/bin/env python3
"""Network Mapper - Map local network topology."""
import socket, subprocess, argparse, concurrent.futures

def ping_host(ip):
    try:
        r = subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True)
        return ip if r.returncode == 0 else None
    except:
        return None

def map_network(subnet):
    print(f"[+] Mapping {subnet}.0/24 ...")
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    with concurrent.futures.ThreadPoolExecutor(50) as ex:
        results = ex.map(ping_host, ips)
    alive = [r for r in results if r]
    print(f"[+] Alive hosts: {len(alive)}")
    for h in alive:
        try:
            hostname = socket.gethostbyaddr(h)[0]
            print(f"   {h} ({hostname})")
        except:
            print(f"   {h}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("subnet", help="e.g. 192.168.1")
    args = p.parse_args()
    map_network(args.subnet)
''',

"40_certificate_validator.py": '''#!/usr/bin/env python3
"""Certificate Chain Validator."""
import ssl, socket, argparse

def validate(hostname, port=443):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                chain = ssock.getpeercert(True)
                print(f"[+] Connected to {hostname}")
                print(f"[+] Subject: {cert.get('subject')}")
                print(f"[+] Issuer: {cert.get('issuer')}")
                print(f"[+] Chain length: {len(chain) if isinstance(chain, list) else 1}")
                print("[+] Certificate chain appears valid")
    except ssl.SSLError as e:
        print(f"[!] SSL Error: {e}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("host")
    p.add_argument("--port", type=int, default=443)
    args = p.parse_args()
    validate(args.host, args.port)
'''
}

# Write cybersec tools
for fname, content in cybersec.items():
    with open(f"{base_path}/cybersec_tools/{fname}", 'w') as f:
        f.write(content)
        
print(f"[+] Written {len(cybersec)} cybersec tools")

# Fix problematic pentest files
pentest_fixes = {
"31_osint_metadata.py": r'''#!/usr/bin/env python3
"""OSINT Metadata Extractor from documents."""
import argparse, re

def extract(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read().decode('utf-8', errors='ignore')
        patterns = {
            "Email": re.compile(r'[\w.-]+@[\w.-]+\.\w+'),
            "URL": re.compile(r'https?://[^\s"<>]+'),
            "IP": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "User": re.compile(r'(?i)(author|creator|user|owner)[=: \t]+([^\r\n]+)')
        }
        for name, pat in patterns.items():
            matches = pat.findall(data)
            if matches:
                print(f"[+] {name}: {set(matches[:10])}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    args = p.parse_args()
    extract(args.file)
''',

"22_robots_analyzer.py": r'''#!/usr/bin/env python3
"""robots.txt Analyzer - Find hidden paths."""
import urllib.request, argparse, re

def analyze(url):
    test = f"{url.rstrip('/')}/robots.txt"
    try:
        req = urllib.request.Request(test, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read().decode('utf-8', errors='ignore')
        disallow = re.findall(r'Disallow:\s*(.+)', body)
        print(f"[+] Found {len(disallow)} disallowed paths:")
        for d in disallow:
            print(f"   {d.strip()}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    analyze(args.url)
''',

"19_wordpress_scanner.py": r'''#!/usr/bin/env python3
"""WordPress Security Scanner."""
import urllib.request, argparse, re

def scan(url):
    base = url.rstrip('/')
    checks = {
        "readme": f"{base}/readme.html",
        "wp-login": f"{base}/wp-login.php",
        "xmlrpc": f"{base}/xmlrpc.php",
        "wp-config": f"{base}/wp-config.php"
    }
    for name, check_url in checks.items():
        try:
            req = urllib.request.Request(check_url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            if resp.status == 200:
                if name == "readme":
                    body = resp.read().decode('utf-8', errors='ignore')
                    ver = re.search(r'Version (\d+\.\d+)', body)
                    print(f"[!] WordPress version exposed: {ver.group(1) if ver else 'unknown'}")
                else:
                    print(f"[!] {name} accessible: {check_url}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"[*] {name} returns 403 (exists but blocked)")
        except:
            pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    scan(args.url)
''',

"39_xxe_scanner.py": r'''#!/usr/bin/env python3
"""XXE (XML External Entity) Scanner."""
import urllib.request, argparse

PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>"""

def scan(url):
    try:
        req = urllib.request.Request(url, data=PAYLOAD.encode(), headers={
            'Content-Type': 'application/xml',
            'User-Agent': 'Mozilla/5.0'
        })
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read().decode('utf-8', errors='ignore')
        if "root:x:0:0" in body:
            print("[!] XXE vulnerability detected")
        else:
            print("[+] No obvious XXE")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    scan(args.url)
'''
}

for fname, content in pentest_fixes.items():
    with open(f"{base_path}/pentest_tools/{fname}", 'w') as f:
        f.write(content)

print("[+] Fixed problematic pentest files")

base_path = "/mnt/agents/output/etternetlog"

pentest_fixes = {
"31_osint_metadata.py": r'''#!/usr/bin/env python3
"""OSINT Metadata Extractor from documents."""
import argparse, re

def extract(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read().decode('utf-8', errors='ignore')
        patterns = {
            "Email": re.compile(r'[\w.-]+@[\w.-]+\.\w+'),
            "URL": re.compile(r'https?://[^\s"<>]+'),
            "IP": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "User": re.compile(r'(?i)(author|creator|user|owner)[=: \t]+([^\r\n]+)')
        }
        for name, pat in patterns.items():
            matches = pat.findall(data)
            if matches:
                print(f"[+] {name}: {set(matches[:10])}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    args = p.parse_args()
    extract(args.file)
''',

"22_robots_analyzer.py": r'''#!/usr/bin/env python3
"""robots.txt Analyzer - Find hidden paths."""
import urllib.request, argparse, re

def analyze(url):
    test = f"{url.rstrip('/')}/robots.txt"
    try:
        req = urllib.request.Request(test, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read().decode('utf-8', errors='ignore')
        disallow = re.findall(r'Disallow:\s*(.+)', body)
        print(f"[+] Found {len(disallow)} disallowed paths:")
        for d in disallow:
            print(f"   {d.strip()}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    analyze(args.url)
''',

"19_wordpress_scanner.py": r'''#!/usr/bin/env python3
"""WordPress Security Scanner."""
import urllib.request, argparse, re

def scan(url):
    base = url.rstrip('/')
    checks = {
        "readme": f"{base}/readme.html",
        "wp-login": f"{base}/wp-login.php",
        "xmlrpc": f"{base}/xmlrpc.php",
        "wp-config": f"{base}/wp-config.php"
    }
    for name, check_url in checks.items():
        try:
            req = urllib.request.Request(check_url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            if resp.status == 200:
                if name == "readme":
                    body = resp.read().decode('utf-8', errors='ignore')
                    ver = re.search(r'Version (\d+\.\d+)', body)
                    print(f"[!] WordPress version exposed: {ver.group(1) if ver else 'unknown'}")
                else:
                    print(f"[!] {name} accessible: {check_url}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"[*] {name} returns 403 (exists but blocked)")
        except:
            pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    scan(args.url)
''',

"39_xxe_scanner.py": r'''#!/usr/bin/env python3
"""XXE (XML External Entity) Scanner."""
import urllib.request, argparse

PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>"""

def scan(url):
    try:
        req = urllib.request.Request(url, data=PAYLOAD.encode(), headers={
            'Content-Type': 'application/xml',
            'User-Agent': 'Mozilla/5.0'
        })
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read().decode('utf-8', errors='ignore')
        if "root:x:0:0" in body:
            print("[!] XXE vulnerability detected")
        else:
            print("[+] No obvious XXE")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    args = p.parse_args()
    scan(args.url)
'''
}

for fname, content in pentest_fixes.items():
    with open(f"{base_path}/pentest_tools/{fname}", 'w') as f:
        f.write(content)

print("[+] Fixed problematic pentest files")

import zipfile, os

base_path = "/mnt/agents/output/etternetlog"
zip_path = "/mnt/agents/output/etternetlog.zip"

# Update ZIP
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(base_path):
        for file in files:
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, os.path.dirname(base_path))
            zf.write(fp, arcname)

print(f"[+] Updated ZIP: {zip_path}")
print(f"[+] Size: {os.path.getsize(zip_path) / 1024:.1f} KB")

# Quick tests
import subprocess, sys

tests = [
    ("custom_tools/04_base_converter.py", ["255", "--from", "10", "--to", "16"]),
    ("custom_tools/23_hash_generator.py", ["test", "--algo", "sha256"]),
    ("cybersec_tools/06_password_strength.py", ["MyStr0ng!Pass"]),
    ("custom_tools/11_subnet_calculator.py", ["192.168.1.0/24"]),
]

for tool, args in tests:
    cmd = [sys.executable, f"{base_path}/{tool}"] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        status = "OK" if r.returncode == 0 else "FAIL"
        print(f"[{status}] {tool}: {r.stdout.strip()[:60]}")
    except Exception as e:
        print(f"[ERR] {tool}: {e}")
