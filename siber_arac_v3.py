#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MARK.OS v3.0 — ULTIMATE CYBER SECURITY ARSENAL                              ║
║  104 Gerçek Siber Güvenlik Aracı | Tek Dosya | Tam Çalışan Kod               ║
╚══════════════════════════════════════════════════════════════════════════════╝
ETİK UYARI: Bu araçlar yalnızca yetkili sistemlerde, savunma ve eğitim amaçlı
kullanılmalıdır. İzinsiz sistemlere müdahale yasaktır.
"""

import os
import sys
import time
import socket
import platform
import asyncio
import subprocess
import hashlib
import base64
import urllib.parse
import urllib.request
import json
import ssl
import re
import random
import string
import ipaddress
import threading
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
#                           KÜTÜPHANE KONTROLÜ
# ═══════════════════════════════════════════════════════════════════════════════

def install(package):
    print(f"    [!] {package} kuruluyor...")
    os.system(f"{sys.executable} -m pip install {package} -q")

try:
    from colorama import Fore, Style, init
    import requests
    import aiohttp
    init(autoreset=True)
except ImportError:
    install("colorama requests aiohttp")
    from colorama import Fore, Style, init
    import requests
    import aiohttp
    init(autoreset=True)

DNS_AVAILABLE = False
PHONE_AVAILABLE = False
try:
    import dns.resolver
    DNS_AVAILABLE = True
except:
    pass
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    PHONE_AVAILABLE = True
except:
    pass

# ═══════════════════════════════════════════════════════════════════════════════
#                         GLOBAL & YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════════════════════

SIFRE_BULUNDU = False
BULUNAN_SIFRE = None

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def pause():
    input(f"\n{Fore.CYAN}[Enter] Ana menüye dönmek için...")

def banner():
    clear()
    print(f"""{Fore.RED}
  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗   ██████╗ ███████╗
  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝  ██╔═══██╗██╔════╝
  ██╔████╔██║███████║██████╔╝█████╔╝   ██║   ██║███████╗
  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗   ██║   ██║╚════██║
  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗  ╚██████╔╝███████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═════╝ ╚══════╝
    {Fore.CYAN}--- Mark.Os v3.0 | 104 Real Cyber Security Tools ---
    {Fore.WHITE}Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}
    {Fore.GREEN}[+] {('dnspython, ' if DNS_AVAILABLE else '')}{('phonenumbers' if PHONE_AVAILABLE else '')} Active
    {Fore.YELLOW}[!] ETHICAL USE ONLY — Authorized Systems Only
    """)

def check_tool(cmd):
    check_cmd = "where" if os.name == "nt" else "which"
    try:
        res = subprocess.run([check_cmd, cmd], capture_output=True, text=True, shell=(os.name == "nt"))
        return bool(res.stdout.strip())
    except:
        return False

def run_cmd(cmd, shell=True):
    try:
        subprocess.run(cmd, shell=shell)
    except Exception as e:
        print(f"{Fore.RED}[-] Çalıştırma hatası: {e}")

def tool_status(name, pkg, check_args=["--version"]):
    print(f"\n{Fore.YELLOW}[*] {name} kontrol ediliyor...")
    if check_tool(name.split()[0]):
        print(f"{Fore.GREEN}[+] {name} kurulu!")
        if input(f"{Fore.CYAN}[?] Çalıştırılsın mı? (e/h): ").lower() == "e":
            run_cmd(f"{name} {' '.join(check_args)}")
    else:
        print(f"{Fore.RED}[-] {name} kurulu değil!")
        print(f"{Fore.WHITE}  Kurulum: sudo apt install {pkg} -y")

def info_tool(name, description, install_cmd):
    print(f"\n{Fore.YELLOW}[*] {name}")
    print(f"{Fore.WHITE}  Açıklama: {description}")
    print(f"{Fore.CYAN}  Kurulum: {install_cmd}")
    if check_tool(name.split()[0]):
        print(f"{Fore.GREEN}  [+] Sistemde kurulu görünüyor!")
    else:
        print(f"{Fore.RED}  [-] Sistemde kurulu değil!")

# ═══════════════════════════════════════════════════════════════════════════════
#                    1-15: NETWORK RECONNAISSANCE
# ═══════════════════════════════════════════════════════════════════════════════

def tool_01_nmap():
    print(f"\n{Fore.YELLOW}[01] Nmap — Ağ Keşfi & Port Taraması")
    if not check_tool("nmap"):
        print(f"{Fore.RED}[-] Nmap kurulu değil! sudo apt install nmap -y"); return
    hedef = input(f"{Fore.GREEN}Hedef IP/Domain: ").strip()
    if hedef:
        run_cmd(f"nmap -sV -O --top-ports 100 {hedef}")

def tool_02_masscan():
    print(f"\n{Fore.YELLOW}[02] Masscan — Yüksek Hızlı Ağ Tarayıcı")
    if not check_tool("masscan"):
        print(f"{Fore.RED}[-] Masscan kurulu değil! sudo apt install masscan -y"); return
    hedef = input(f"{Fore.GREEN}Hedef IP/Range: ").strip()
    if hedef:
        run_cmd(f"sudo masscan {hedef} -p1-65535 --rate=10000")

def tool_03_wireshark():
    print(f"\n{Fore.YELLOW}[03] Wireshark — Paket Analizörü")
    if not check_tool("wireshark"):
        print(f"{Fore.RED}[-] Wireshark kurulu değil! sudo apt install wireshark -y"); return
    print(f"{Fore.CYAN}[*] Wireshark GUI başlatılıyor...")
    run_cmd("wireshark &")

def tool_04_tcpdump():
    print(f"\n{Fore.YELLOW}[04] Tcpdump — CLI Paket Yakalama")
    if not check_tool("tcpdump"):
        print(f"{Fore.RED}[-] Tcpdump kurulu değil! sudo apt install tcpdump -y"); return
    iface = input(f"{Fore.GREEN}Arayüz [eth0]: ").strip() or "eth0"
    count = input(f"{Fore.GREEN}Paket sayısı [100]: ").strip() or "100"
    run_cmd(f"sudo tcpdump -i {iface} -c {count}")

def tool_05_suricata():
    print(f"\n{Fore.YELLOW}[05] Suricata — IDS/IPS")
    tool_status("suricata", "suricata", ["--version"])

def tool_06_snort():
    print(f"\n{Fore.YELLOW}[06] Snort — Geleneksel IDS/IPS")
    tool_status("snort", "snort", ["--version"])

def tool_07_zeek():
    print(f"\n{Fore.YELLOW}[07] Zeek (Bro) — Ağ Güvenlik İzleme")
    tool_status("zeek", "zeek", ["--version"])

def tool_08_curl():
    print(f"\n{Fore.YELLOW}[08] cURL — HTTP/İstek Aracı")
    if not check_tool("curl"):
        print(f"{Fore.RED}[-] curl kurulu değil!"); return
    url = input(f"{Fore.GREEN}URL: ").strip()
    if url:
        run_cmd(f"curl -I {url}")

def tool_09_netcat():
    print(f"\n{Fore.YELLOW}[09] Netcat — Sihirli Ağ Aracı")
    nc = "ncat" if check_tool("ncat") else ("nc" if check_tool("nc") else None)
    if not nc:
        print(f"{Fore.RED}[-] Netcat kurulu değil! sudo apt install netcat -y"); return
    print("1 - Dinleme modu\n2 - Bağlantı modu\n3 - Banner grabbing")
    mod = input(f"{Fore.GREEN}Seçim: ").strip()
    if mod == "1":
        p = input(f"{Fore.GREEN}Port: ").strip()
        run_cmd(f"{nc} -lvnp {p}")
    elif mod == "2":
        ip = input(f"{Fore.GREEN}IP: ").strip()
        p = input(f"{Fore.GREEN}Port: ").strip()
        run_cmd(f"{nc} {ip} {p}")
    elif mod == "3":
        ip = input(f"{Fore.GREEN}IP: ").strip()
        p = input(f"{Fore.GREEN}Port: ").strip()
        run_cmd(f"echo '' | {nc} -v -w 2 {ip} {p}")

def tool_10_ping_sweep():
    print(f"\n{Fore.YELLOW}[10] Python Ping Sweep — Yerel Ağ Tarama")
    ip_range = input(f"{Fore.GREEN}IP Aralığı (örn: 192.168.1.0/24): ").strip()
    if not ip_range:
        return
    try:
        net = ipaddress.ip_network(ip_range, strict=False)
    except:
        print(f"{Fore.RED}[-] Geçersiz aralık!"); return
    print(f"{Fore.CYAN}[*] Taranıyor: {ip_range}")
    aktif = []
    def ping(ip):
        param = "-n" if os.name == "nt" else "-c"
        try:
            res = subprocess.run(["ping", param, "1", str(ip)], capture_output=True, timeout=2)
            if res.returncode == 0:
                print(f"{Fore.GREEN}[+] AKTİF: {ip}")
                aktif.append(str(ip))
        except:
            pass
    threads = []
    for ip in net.hosts():
        t = threading.Thread(target=ping, args=(ip,))
        t.daemon = True
        t.start()
        threads.append(t)
        if len(threads) >= 100:
            for th in threads: th.join(timeout=3)
            threads = []
    for th in threads: th.join(timeout=3)
    print(f"\n{Fore.YELLOW}[*] {len(aktif)} aktif host bulundu.")

def tool_11_banner_grab():
    print(f"\n{Fore.YELLOW}[11] Banner Grabbing — Servis Tanımlama")
    ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    port = input(f"{Fore.GREEN}Port [80]: ").strip() or "80"
    if not ip:
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, int(port)))
        if int(port) in [80, 8080, 443]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: test\r\n\r\n")
        banner = s.recv(4096).decode('utf-8', errors='ignore').strip()
        s.close()
        print(f"{Fore.GREEN}[+] Banner:\n{Fore.WHITE}{banner}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def tool_12_reverse_ip():
    print(f"\n{Fore.YELLOW}[12] Reverse IP Lookup")
    ip = input(f"{Fore.GREEN}IP: ").strip()
    if not ip:
        return
    try:
        req = urllib.request.Request(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            print(f"{Fore.GREEN}[+] Sonuçlar:\n{Fore.WHITE}{data}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def tool_13_cidr_calc():
    print(f"\n{Fore.YELLOW}[13] CIDR / Subnet Hesaplayıcı")
    cidr = input(f"{Fore.GREEN}CIDR (örn: 192.168.1.0/24): ").strip()
    if not cidr:
        return
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        print(f"\n{Fore.GREEN}[+] Sonuçlar:")
        print(f"  Ağ Adresi : {net.network_address}")
        print(f"  Broadcast : {net.broadcast_address}")
        print(f"  Host Sayısı: {net.num_addresses - 2 if net.num_addresses > 2 else net.num_addresses}")
        print(f"  Netmask   : {net.netmask}")
        print(f"  Özel Ağ   : {'Evet' if net.is_private else 'Hayır'}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def tool_14_ssl_check():
    print(f"\n{Fore.YELLOW}[14] SSL/TLS Sertifika Kontrolü")
    hostname = input(f"{Fore.GREEN}Hostname: ").strip()
    if not hostname:
        return
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"{Fore.GREEN}[+] TLS: {ssock.version()}")
                print(f"  Subject: {cert.get('subject')}")
                print(f"  Issuer : {cert.get('issuer')}")
                print(f"  Bitiş  : {cert.get('notAfter')}")
                if ssock.version() in ["TLSv1", "TLSv1.1"]:
                    print(f"{Fore.RED}[⚠] ZAYIF TLS!")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def tool_15_http_header():
    print(f"\n{Fore.YELLOW}[15] HTTP Header & Güvenlik Analizörü")
    url = input(f"{Fore.GREEN}URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        r = requests.get(url, timeout=10)
        print(f"{Fore.GREEN}[+] Status: {r.status_code}")
        for k, v in r.headers.items():
            print(f"  {Fore.WHITE}{k}: {v}")
        print(f"\n{Fore.YELLOW}[*] Güvenlik Header Kontrolü:")
        for h in ['X-Frame-Options', 'X-XSS-Protection', 'Content-Security-Policy', 'Strict-Transport-Security']:
            print(f"  {Fore.GREEN if h in r.headers else Fore.RED}{'[✓]' if h in r.headers else '[✗]'} {h}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    16-25: VULNERABILITY SCANNING
# ═══════════════════════════════════════════════════════════════════════════════

def tool_16_openvas():
    print(f"\n{Fore.YELLOW}[16] OpenVAS / Greenbone — Zafiyet Tarayıcı")
    if check_tool("openvas"):
        run_cmd("openvas --version")
    elif check_tool("gvm-cli"):
        run_cmd("gvm-cli --version")
    else:
        print(f"{Fore.RED}[-] OpenVAS kurulu değil!")
        print(f"{Fore.WHITE}  Kurulum: sudo apt install openvas -y && sudo gvm-setup")

def tool_17_nessus():
    print(f"\n{Fore.YELLOW}[17] Nessus — Ticari Zafiyet Tarayıcı")
    tool_status("nessuscli", "nessus", ["--version"])

def tool_18_nikto():
    print(f"\n{Fore.YELLOW}[18] Nikto — Web Sunucusu Tarayıcı")
    if not check_tool("nikto"):
        print(f"{Fore.RED}[-] Nikto kurulu değil! sudo apt install nikto -y"); return
    url = input(f"{Fore.GREEN}Hedef URL: ").strip()
    if url:
        run_cmd(f"nikto -h {url}")

def tool_19_owasp_zap():
    print(f"\n{Fore.YELLOW}[19] OWASP ZAP — Web Güvenlik Tarayıcı")
    if not check_tool("zap-cli") and not check_tool("zaproxy"):
        print(f"{Fore.RED}[-] ZAP kurulu değil! sudo apt install zaproxy -y"); return
    print(f"{Fore.CYAN}[*] ZAP başlatılıyor...")
    run_cmd("zaproxy &")

def tool_20_burp_suite():
    print(f"\n{Fore.YELLOW}[20] Burp Suite — Web Uygulama Analizi")
    if not check_tool("burpsuite"):
        print(f"{Fore.RED}[-] Burp Suite kurulu değil!"); return
    print(f"{Fore.CYAN}[*] Burp Suite başlatılıyor...")
    run_cmd("burpsuite &")

def tool_21_lynis():
    print(f"\n{Fore.YELLOW}[21] Lynis — Sistem Güvenlik Denetimi")
    if not check_tool("lynis"):
        print(f"{Fore.RED}[-] Lynis kurulu değil! sudo apt install lynis -y"); return
    run_cmd("sudo lynis audit system")

def tool_22_sqli_scan():
    print(f"\n{Fore.YELLOW}[22] SQL Injection Hata Pattern Tarayıcı (Python)")
    url = input(f"{Fore.GREEN}URL (parametreli): ").strip()
    if not url:
        return
    payloads = ["'", "\"", "' OR '1'='1", "1 AND 1=2"]
    errors = ["sql syntax", "mysql_fetch", "pg_query", "ora-", "unclosed quotation"]
    for p in payloads:
        try:
            test = f"{url}{p}" if "?" in url else f"{url}?id={p}"
            r = requests.get(test, timeout=10)
            for e in errors:
                if e in r.text.lower():
                    print(f"{Fore.RED}[🚨] SQLi ZAFİYETİ! Payload: {p}"); return
        except:
            pass
    print(f"{Fore.GREEN}[+] SQLi hatası bulunamadı.")

def tool_23_xss_scan():
    print(f"\n{Fore.YELLOW}[23] Reflected XSS Tester (Python)")
    url = input(f"{Fore.GREEN}URL (parametreli): ").strip()
    if "?" not in url:
        print(f"{Fore.RED}[-] Parametre gerekli!"); return
    payloads = ["<script>alert('XSS')</script>", "\"><img src=x onerror=alert('XSS')>"]
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    if not qs:
        return
    fp = list(qs.keys())[0]
    for p in payloads:
        nq = urllib.parse.urlencode({k: (p if k == fp else v[0]) for k, v in qs.items()})
        test = urllib.parse.urlunparse(parsed._replace(query=nq))
        try:
            r = requests.get(test, timeout=10)
            if p in r.text:
                print(f"{Fore.RED}[🚨] REFLECTED XSS! Param: {fp}"); return
        except:
            pass
    print(f"{Fore.GREEN}[+] XSS bulunamadı.")

def tool_24_open_redirect():
    print(f"\n{Fore.YELLOW}[24] Open Redirect Tester (Python)")
    url = input(f"{Fore.GREEN}URL (redirect parametreli): ").strip()
    if not url:
        return
    payloads = ["https://evil.com", "//evil.com"]
    for p in payloads:
        try:
            test = url.replace("TARGET", p) if "TARGET" in url else f"{url}{p}"
            r = requests.get(test, timeout=10, allow_redirects=False)
            if r.status_code in [301, 302] and 'evil.com' in r.headers.get('Location', ''):
                print(f"{Fore.RED}[🚨] OPEN REDIRECT!"); return
        except:
            pass
    print(f"{Fore.GREEN}[+] Güvenli görünüyor.")

def tool_25_csrf_check():
    print(f"\n{Fore.YELLOW}[25] CSRF Token Kontrolü (Python)")
    url = input(f"{Fore.GREEN}Form URL: ").strip()
    if not url:
        return
    try:
        r = requests.get(url, timeout=10)
        tokens = ['csrf', 'xsrf', '_token', 'authenticity_token']
        found = [t for t in tokens if t in r.text.lower()]
        if found:
            print(f"{Fore.GREEN}[+] Token bulundu: {found}")
        else:
            print(f"{Fore.RED}[⚠] CSRF token BULUNAMADI!")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    26-40: ENDPOINT SECURITY (BLUE TEAM)
# ═══════════════════════════════════════════════════════════════════════════════

def tool_26_ossec():
    print(f"\n{Fore.YELLOW}[26] OSSEC — Host IDS")
    tool_status("ossec-control", "ossec-hids", ["status"])

def tool_27_wazuh():
    print(f"\n{Fore.YELLOW}[27] Wazuh — Genişletilmiş HIDS/SIEM")
    if check_tool("wazuh-control"):
        run_cmd("wazuh-control status")
    elif check_tool("systemctl"):
        run_cmd("systemctl status wazuh-manager 2>/dev/null || systemctl status wazuh-agent 2>/dev/null")
    else:
        print(f"{Fore.RED}[-] Wazuh bulunamadı! sudo apt install wazuh-manager -y")

def tool_28_fail2ban():
    print(f"\n{Fore.YELLOW}[28] Fail2ban — Brute-force Engelleme")
    if not check_tool("fail2ban-client"):
        print(f"{Fore.RED}[-] Fail2ban kurulu değil! sudo apt install fail2ban -y"); return
    run_cmd("sudo fail2ban-client status")

def tool_29_modsecurity():
    print(f"\n{Fore.YELLOW}[29] ModSecurity — Web Uygulama Güvenlik Duvarı")
    print(f"{Fore.CYAN}[*] Apache/Nginx mod_security modülü kontrol ediliyor...")
    run_cmd("apachectl -M 2>/dev/null | grep -i security || nginx -V 2>&1 | grep -i modsecurity || echo '[!] ModSecurity modülü bulunamadı'")

def tool_30_clamav():
    print(f"\n{Fore.YELLOW}[30] ClamAV — Açık Kaynak Antivirüs")
    if not check_tool("clamscan"):
        print(f"{Fore.RED}[-] ClamAV kurulu değil! sudo apt install clamav -y"); return
    path = input(f"{Fore.GREEN}Taranacak dizin [./]: ").strip() or "."
    run_cmd(f"clamscan -r {path}")

def tool_31_rkhunter():
    print(f"\n{Fore.YELLOW}[31] Rkhunter — Rootkit Tespiti")
    if not check_tool("rkhunter"):
        print(f"{Fore.RED}[-] Rkhunter kurulu değil! sudo apt install rkhunter -y"); return
    run_cmd("sudo rkhunter --check --sk")

def tool_32_chkrootkit():
    print(f"\n{Fore.YELLOW}[32] Chkrootkit — Rootkit Tarayıcı")
    if not check_tool("chkrootkit"):
        print(f"{Fore.RED}[-] Chkrootkit kurulu değil! sudo apt install chkrootkit -y"); return
    run_cmd("sudo chkrootkit")

def tool_33_aide():
    print(f"\n{Fore.YELLOW}[33] AIDE — Dosya Bütünlüğü")
    if not check_tool("aide"):
        print(f"{Fore.RED}[-] AIDE kurulu değil! sudo apt install aide -y"); return
    print("1 - Init (Veritabanı oluştur)\n2 - Check (Kontrol et)")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        run_cmd("sudo aideinit")
    elif s == "2":
        run_cmd("sudo aide --check")

def tool_34_tripwire():
    print(f"\n{Fore.YELLOW}[34] Tripwire — Bütünlük İzleme")
    tool_status("tripwire", "tripwire", ["--version"])

def tool_35_auditd():
    print(f"\n{Fore.YELLOW}[35] auditd — Linux Denetim Altyapısı")
    if not check_tool("ausearch"):
        print(f"{Fore.RED}[-] auditd kurulu değil! sudo apt install auditd -y"); return
    print("1 - Son olayları görüntüle\n2 - Belirli kullanıcıyı ara")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        run_cmd("sudo ausearch -ts recent -i | head -50")
    elif s == "2":
        u = input(f"{Fore.GREEN}Kullanıcı: ").strip()
        run_cmd(f"sudo ausearch -ua {u} -i | head -30")

def tool_36_selinux():
    print(f"\n{Fore.YELLOW}[36] SELinux — Zorunlu Erişim Kontrolü")
    if not check_tool("getenforce") and not os.path.exists("/sys/fs/selinux/enforce"):
        print(f"{Fore.RED}[-] SELinux desteklenmiyor veya kurulu değil!"); return
    run_cmd("getenforce && sestatus && echo '--- İzin Verilen Modlar: Enforcing, Permissive, Disabled ---'")

def tool_37_apparmor():
    print(f"\n{Fore.YELLOW}[37] AppArmor — Profil Tabanlı MAC")
    if not check_tool("aa-status"):
        print(f"{Fore.RED}[-] AppArmor kurulu değil! sudo apt install apparmor-utils -y"); return
    run_cmd("sudo aa-status")

def tool_38_sysdig():
    print(f"\n{Fore.YELLOW}[38] Sysdig — Sistem Çağrı İzleme")
    tool_status("sysdig", "sysdig", ["--version"])

def tool_39_falco():
    print(f"\n{Fore.YELLOW}[39] Falco — Runtime Güvenlik İzleme")
    tool_status("falco", "falco", ["--version"])

def tool_40_osquery():
    print(f"\n{Fore.YELLOW}[40] osquery — Uç Nokta Sorgulama")
    if not check_tool("osqueryi"):
        print(f"{Fore.RED}[-] osquery kurulu değil! sudo apt install osquery -y"); return
    q = input(f"{Fore.GREEN}SQL Sorgusu [SELECT * FROM os_version;]: ").strip() or "SELECT * FROM os_version;"
    run_cmd(f"osqueryi '{q}'")

# ═══════════════════════════════════════════════════════════════════════════════
#                    41-55: MONITORING & SIEM
# ═══════════════════════════════════════════════════════════════════════════════

def tool_41_prometheus():
    print(f"\n{Fore.YELLOW}[41] Prometheus — Zaman Serisi İzleme")
    tool_status("prometheus", "prometheus", ["--version"])

def tool_42_grafana():
    print(f"\n{Fore.YELLOW}[42] Grafana — Dashboard & Görselleştirme")
    if not check_tool("grafana-cli") and not check_tool("grafana-server"):
        print(f"{Fore.RED}[-] Grafana bulunamadı! sudo apt install grafana -y"); return
    print(f"{Fore.GREEN}[+] Grafana kurulu. Web arayüzü: http://localhost:3000")

def tool_43_elk():
    print(f"\n{Fore.YELLOW}[43] ELK Stack — Log Analizi")
    for c in ["elasticsearch", "logstash", "kibana"]:
        if check_tool(c):
            print(f"{Fore.GREEN}[+] {c} bulundu!")
        else:
            print(f"{Fore.RED}[-] {c} kurulu değil!")

def tool_44_graylog():
    print(f"\n{Fore.YELLOW}[44] Graylog — Merkezi Log Yönetimi")
    if check_tool("graylog-ctl") or check_tool("graylog-server"):
        print(f"{Fore.GREEN}[+] Graylog kurulu! Web: http://localhost:9000")
    else:
        print(f"{Fore.RED}[-] Graylog kurulu değil! Docker ile kurulum önerilir.")

def tool_45_splunk():
    print(f"\n{Fore.YELLOW}[45] Splunk — SIEM & Log Analizi")
    if check_tool("splunk"):
        run_cmd("splunk --version")
    else:
        print(f"{Fore.RED}[-] Splunk kurulu değil! https://www.splunk.com/en_us/download.html")

def tool_46_netdata():
    print(f"\n{Fore.YELLOW}[46] Netdata — Gerçek Zamanlı İzleme")
    if check_tool("netdata") or os.path.exists("/usr/sbin/netdata"):
        print(f"{Fore.GREEN}[+] Netdata çalışıyor! Web: http://localhost:19999")
        run_cmd("curl -s http://localhost:19999/api/v1/info | head -20")
    else:
        print(f"{Fore.RED}[-] Netdata kurulu değil! bash <(curl -Ss https://my-netdata.io/kickstart.sh)")

def tool_47_nagios():
    print(f"\n{Fore.YELLOW}[47] Nagios — Altyapı İzleme")
    tool_status("nagios", "nagios4", ["--version"])

def tool_48_zabbix():
    print(f"\n{Fore.YELLOW}[48] Zabbix — Ağ & Uygulama İzleme")
    tool_status("zabbix_agentd", "zabbix-agent", ["--version"])

def tool_49_thehive():
    print(f"\n{Fore.YELLOW}[49] TheHive — Olay Müdahale Platformu")
    if check_tool("thehive") or os.path.exists("/opt/thehive"):
        print(f"{Fore.GREEN}[+] TheHive kurulu! Web: http://localhost:9000")
    else:
        print(f"{Fore.RED}[-] TheHive kurulu değil! Docker ile kurulum önerilir.")

def tool_50_cortex():
    print(f"\n{Fore.YELLOW}[50] Cortex — Analiz & Otomasyon")
    if check_tool("cortex"):
        print(f"{Fore.GREEN}[+] Cortex kurulu!")
    else:
        print(f"{Fore.RED}[-] Cortex kurulu değil! TheHive ile birlikte kurulur.")

def tool_51_misp():
    print(f"\n{Fore.YELLOW}[51] MISP — Tehdit İstihbaratı Paylaşımı")
    if os.path.exists("/var/www/MISP"):
        print(f"{Fore.GREEN}[+] MISP kurulu! Web: https://localhost")
    else:
        print(f"{Fore.RED}[-] MISP kurulu değil! https://github.com/MISP/MISP")

def tool_52_opencti():
    print(f"\n{Fore.YELLOW}[52] OpenCTI — Tehdit İstihbaratı Yönetimi")
    if check_tool("opencti"):
        print(f"{Fore.GREEN}[+] OpenCTI bulundu!")
    else:
        print(f"{Fore.RED}[-] OpenCTI kurulu değil! Docker ile kurulum önerilir.")

def tool_53_packetbeat():
    print(f"\n{Fore.YELLOW}[53] Packetbeat — Ağ Trafik Metrikleri")
    tool_status("packetbeat", "packetbeat", ["--version"])

def tool_54_filebeat():
    print(f"\n{Fore.YELLOW}[54] Filebeat — Log Gönderici")
    tool_status("filebeat", "filebeat", ["--version"])

def tool_55_auditbeat():
    print(f"\n{Fore.YELLOW}[55] Auditbeat — Host Davranış İzleme")
    tool_status("auditbeat", "auditbeat", ["--version"])

# ═══════════════════════════════════════════════════════════════════════════════
#                    56-65: CONTAINER & CLOUD SECURITY
# ═══════════════════════════════════════════════════════════════════════════════

def tool_56_trivy():
    print(f"\n{Fore.YELLOW}[56] Trivy — Container Zafiyet Tarayıcı")
    if not check_tool("trivy"):
        print(f"{Fore.RED}[-] Trivy kurulu değil! sudo apt install trivy -y"); return
    target = input(f"{Fore.GREEN}İmaj adı veya dosya: ").strip()
    if target:
        run_cmd(f"trivy image {target}" if not os.path.exists(target) else f"trivy filesystem {target}")

def tool_57_clair():
    print(f"\n{Fore.YELLOW}[57] Clair — Container Görüntüsü Analizi")
    if check_tool("clair"):
        print(f"{Fore.GREEN}[+] Clair bulundu!")
    else:
        print(f"{Fore.RED}[-] Clair kurulu değil! Docker ile çalıştırılır.")

def tool_58_anchore():
    print(f"\n{Fore.YELLOW}[58] Anchore Engine — İmaj Politika & Zafiyet")
    if check_tool("anchore-cli"):
        run_cmd("anchore-cli --version")
    else:
        print(f"{Fore.RED}[-] Anchore kurulu değil! Docker ile kurulum önerilir.")

def tool_59_grype():
    print(f"\n{Fore.YELLOW}[59] Grype — Artefakt Zafiyet Tarayıcı")
    tool_status("grype", "grype", ["--version"])

def tool_60_kubebench():
    print(f"\n{Fore.YELLOW}[60] kube-bench — CIS Kubernetes Benchmark")
    if not check_tool("kube-bench"):
        print(f"{Fore.RED}[-] kube-bench kurulu değil! sudo apt install kube-bench -y"); return
    run_cmd("kube-bench")

def tool_61_kubehunter():
    print(f"\n{Fore.YELLOW}[61] kube-hunter — Kubernetes Güvenlik Değerlendirmesi")
    tool_status("kube-hunter", "kube-hunter", ["--version"])

def tool_62_kubeaudit():
    print(f"\n{Fore.YELLOW}[62] kubeaudit — Kubernetes Kaynak Denetimi")
    tool_status("kubeaudit", "kubeaudit", ["--version"])

# ═══════════════════════════════════════════════════════════════════════════════
#                    66-75: CRYPTOGRAPHY & SECRETS
# ═══════════════════════════════════════════════════════════════════════════════

def tool_63_vault():
    print(f"\n{Fore.YELLOW}[63] HashiCorp Vault — Gizli Yönetimi")
    if not check_tool("vault"):
        print(f"{Fore.RED}[-] Vault kurulu değil! https://developer.hashicorp.com/vault/downloads"); return
    run_cmd("vault status")

def tool_64_gnupg():
    print(f"\n{Fore.YELLOW}[64] GnuPG — Şifreleme & İmza")
    if not check_tool("gpg"):
        print(f"{Fore.RED}[-] GPG kurulu değil! sudo apt install gnupg -y"); return
    print("1 - Versiyon gör\n2 - Anahtarları listele")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        run_cmd("gpg --version")
    elif s == "2":
        run_cmd("gpg --list-keys")

def tool_65_keycloak():
    print(f"\n{Fore.YELLOW}[65] Keycloak — Kimlik & Erişim Yönetimi")
    if check_tool("kc.sh") or os.path.exists("/opt/keycloak"):
        print(f"{Fore.GREEN}[+] Keycloak kurulu! Web: http://localhost:8080")
    else:
        print(f"{Fore.RED}[-] Keycloak kurulu değil! https://www.keycloak.org/downloads")

def tool_66_certbot():
    print(f"\n{Fore.YELLOW}[66] Certbot — TLS Sertifika Yönetimi")
    if not check_tool("certbot"):
        print(f"{Fore.RED}[-] Certbot kurulu değil! sudo apt install certbot -y"); return
    run_cmd("certbot --version")

def tool_67_openssl():
    print(f"\n{Fore.YELLOW}[67] OpenSSL — Kriptografi Araçları")
    if not check_tool("openssl"):
        print(f"{Fore.RED}[-] OpenSSL kurulu değil!"); return
    print("1 - Versiyon\n2 - Sertifika bilgisi (dosya)")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        run_cmd("openssl version")
    elif s == "2":
        f = input(f"{Fore.GREEN}Sertifika dosyası: ").strip()
        if f and os.path.exists(f):
            run_cmd(f"openssl x509 -in {f} -text -noout")

def tool_68_sslyze():
    print(f"\n{Fore.YELLOW}[68] SSLyze — TLS Yapılandırma Analizi")
    if not check_tool("sslyze"):
        print(f"{Fore.RED}[-] SSLyze kurulu değil! pip install sslyze"); return
    host = input(f"{Fore.GREEN}Hedef host:port: ").strip()
    if host:
        run_cmd(f"sslyze {host}")

def tool_69_hash_id():
    print(f"\n{Fore.YELLOW}[69] Hash Identifier (Python)")
    h = input(f"{Fore.GREEN}Hash: ").strip()
    if not h:
        return
    patterns = {32: "MD5", 40: "SHA1", 64: "SHA256", 128: "SHA512"}
    print(f"{Fore.GREEN}[+] Muhtemel tip: {patterns.get(len(h), 'Bilinmiyor')}")

def tool_70_pass_gen():
    print(f"\n{Fore.YELLOW}[70] Güçlü Şifre Üretici (Python)")
    try:
        uzunluk = int(input(f"{Fore.GREEN}Uzunluk [16]: ").strip() or "16")
        adet = int(input(f"{Fore.GREEN}Adet [5]: ").strip() or "5")
    except:
        return
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    for i in range(adet):
        print(f"  {i+1}. {''.join(random.choice(chars) for _ in range(uzunluk))}")

def tool_71_encode_decode():
    print(f"\n{Fore.YELLOW}[71] Encode/Decode Merkezi (Python)")
    print("1-Base64Enc 2-Base64Dec 3-URLEnc 4-URLDec 5-HexEnc 6-HexDec 7-ROT13")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    t = input(f"{Fore.GREEN}Metin: ").strip()
    if not t:
        return
    try:
        if s == "1": print(base64.b64encode(t.encode()).decode())
        elif s == "2": print(base64.b64decode(t.encode()).decode())
        elif s == "3": print(urllib.parse.quote(t))
        elif s == "4": print(urllib.parse.unquote(t))
        elif s == "5": print(t.encode().hex())
        elif s == "6": print(bytes.fromhex(t).decode())
        elif s == "7": print(t.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')))
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def tool_72_metadata():
    print(f"\n{Fore.YELLOW}[72] Dosya Metadata Çıkarıcı (Python)")
    path = input(f"{Fore.GREEN}Dosya yolu: ").strip()
    if not path or not os.path.exists(path):
        print(f"{Fore.RED}[-] Dosya bulunamadı!"); return
    stat = os.stat(path)
    print(f"  Boyut: {stat.st_size} bytes")
    print(f"  Oluşturulma: {datetime.fromtimestamp(stat.st_ctime)}")
    print(f"  Değiştirilme: {datetime.fromtimestamp(stat.st_mtime)}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    73-90: FORENSICS & INVESTIGATION
# ═══════════════════════════════════════════════════════════════════════════════

def tool_73_velociraptor():
    print(f"\n{Fore.YELLOW}[73] Velociraptor — Uç Nokta Adli Analiz")
    tool_status("velociraptor", "velociraptor", ["--version"])

def tool_74_grr():
    print(f"\n{Fore.YELLOW}[74] GRR Rapid Response — Uç Nokta Müdahele")
    if check_tool("grr_console") or os.path.exists("/usr/share/grr"):
        print(f"{Fore.GREEN}[+] GRR kurulu!")
    else:
        print(f"{Fore.RED}[-] GRR kurulu değil! https://github.com/google/grr")

def tool_75_autopsy():
    print(f"\n{Fore.YELLOW}[75] Autopsy — Dijital Adli Analiz Arayüzü")
    if not check_tool("autopsy"):
        print(f"{Fore.RED}[-] Autopsy kurulu değil! sudo apt install autopsy -y"); return
    run_cmd("autopsy &")

def tool_76_sleuthkit():
    print(f"\n{Fore.YELLOW}[76] Sleuth Kit — Adli Analiz Kütüphaneleri")
    tool_status("fsstat", "sleuthkit", ["--version"])

def tool_77_volatility():
    print(f"\n{Fore.YELLOW}[77] Volatility — Bellek Adli Analizi")
    vol = "vol.py" if check_tool("vol.py") else ("volatility" if check_tool("volatility") else None)
    if not vol:
        print(f"{Fore.RED}[-] Volatility kurulu değil! sudo apt install volatility -y"); return
    print(f"{Fore.GREEN}[+] Volatility hazır: {vol}")

def tool_78_bulk_extractor():
    print(f"\n{Fore.YELLOW}[78] Bulk Extractor — Toplu Veri Çıkarımı")
    tool_status("bulk_extractor", "bulk-extractor", ["--version"])

def tool_79_scalpel():
    print(f"\n{Fore.YELLOW}[79] Scalpel — Dosya Carve Aracı")
    tool_status("scalpel", "scalpel", ["--version"])

def tool_80_foremost():
    print(f"\n{Fore.YELLOW}[80] Foremost — Dosya Kurtarma")
    if not check_tool("foremost"):
        print(f"{Fore.RED}[-] Foremost kurulu değil! sudo apt install foremost -y"); return
    disk = input(f"{Fore.GREEN}İmaj dosyası: ").strip()
    if disk and os.path.exists(disk):
        out = input(f"{Fore.GREEN}Çıktı dizini [/tmp/foremost]: ").strip() or "/tmp/foremost"
        run_cmd(f"sudo foremost -i {disk} -o {out}")

def tool_81_plaso():
    print(f"\n{Fore.YELLOW}[81] Plaso (log2timeline) — Zaman Çizelgesi")
    tool_status("log2timeline.py", "plaso-tools", ["--version"])

def tool_82_mac_tool():
    print(f"\n{Fore.YELLOW}[82] MAC Adres Aracı (Python)")
    print("1 - Rastgele MAC üret\n2 - Vendor lookup")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        mac = ":".join([f"{random.randint(0,255):02x}" for _ in range(6)])
        print(f"{Fore.GREEN}[+] MAC: {mac.upper()}")
    elif s == "2":
        mac = input(f"{Fore.GREEN}MAC (ilk 3 octet): ").strip()
        oui = mac.replace(":", "").replace("-", "")[:6].upper()
        vendors = {"005056": "VMware", "080027": "VirtualBox", "001B11": "Intel", "00166F": "Apple", "001451": "Cisco"}
        print(f"{Fore.GREEN}[+] Vendor: {vendors.get(oui, 'Bilinmiyor')}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    83-100: DEVSECOPS, SAST & MISC
# ═══════════════════════════════════════════════════════════════════════════════

def tool_83_openscap():
    print(f"\n{Fore.YELLOW}[83] OpenSCAP — Sertleştirme & Uyumluluk")
    if not check_tool("oscap"):
        print(f"{Fore.RED}[-] OpenSCAP kurulu değil! sudo apt install libopenscap8 -y"); return
    run_cmd("oscap --version")

def tool_84_bandit():
    print(f"\n{Fore.YELLOW}[84] Bandit — Python Statik Güvenlik Analizi")
    if not check_tool("bandit"):
        print(f"{Fore.RED}[-] Bandit kurulu değil! pip install bandit"); return
    path = input(f"{Fore.GREEN}Python dosyası/dizin: ").strip()
    if path:
        run_cmd(f"bandit -r {path}")

def tool_85_brakeman():
    print(f"\n{Fore.YELLOW}[85] Brakeman — Rails Statik Analiz")
    tool_status("brakeman", "brakeman", ["--version"])

def tool_86_semgrep():
    print(f"\n{Fore.YELLOW}[86] Semgrep — Hafif Statik Analiz")
    if not check_tool("semgrep"):
        print(f"{Fore.RED}[-] Semgrep kurulu değil! pip install semgrep"); return
    path = input(f"{Fore.GREEN}Kod dizini: ").strip()
    if path:
        run_cmd(f"semgrep --config=auto {path}")

def tool_87_trufflehog():
    print(f"\n{Fore.YELLOW}[87] TruffleHog — Git Gizli Anahtar Arama")
    if not check_tool("trufflehog"):
        print(f"{Fore.RED}[-] TruffleHog kurulu değil! pip install truffleHog"); return
    repo = input(f"{Fore.GREEN}Git repo yolu: ").strip()
    if repo:
        run_cmd(f"trufflehog {repo}")

def tool_88_gitleaks():
    print(f"\n{Fore.YELLOW}[88] Gitleaks — Depo Gizli Anahtar Tespiti")
    tool_status("gitleaks", "gitleaks", ["--version"])

def tool_89_sonarqube():
    print(f"\n{Fore.YELLOW}[89] SonarQube — Kod Kalitesi & Güvenlik")
    if os.path.exists("/opt/sonarqube") or check_tool("sonar-scanner"):
        print(f"{Fore.GREEN}[+] SonarQube bulundu! Web: http://localhost:9000")
    else:
        print(f"{Fore.RED}[-] SonarQube kurulu değil! Docker ile kurulum önerilir.")

def tool_90_dependabot():
    print(f"\n{Fore.YELLOW}[90] Dependabot — Bağımlılık Güncelleme")
    print(f"{Fore.CYAN}[*] Dependabot GitHub entegre servisidir. CLI'si yoktur.")
    print(f"{Fore.WHITE}  GitHub repo ayarlarından Security > Dependabot sekmesinden aktif edilir.")

def tool_91_snyk():
    print(f"\n{Fore.YELLOW}[91] Snyk — Bağımlılık & Container Tarama")
    if not check_tool("snyk"):
        print(f"{Fore.RED}[-] Snyk kurulu değil! npm install -g snyk"); return
    run_cmd("snyk --version")

def tool_92_ansible():
    print(f"\n{Fore.YELLOW}[92] Ansible — Konfigürasyon Yönetimi")
    if not check_tool("ansible"):
        print(f"{Fore.RED}[-] Ansible kurulu değil! sudo apt install ansible -y"); return
    print("1 - Versiyon\n2 - Ping testi (inventory gerekir)")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        run_cmd("ansible --version")
    elif s == "2":
        inv = input(f"{Fore.GREEN}Inventory dosyası: ").strip()
        if inv and os.path.exists(inv):
            run_cmd(f"ansible all -i {inv} -m ping")

def tool_93_puppet():
    print(f"\n{Fore.YELLOW}[93] Puppet — Konfigürasyon Yönetimi")
    tool_status("puppet", "puppet-agent", ["--version"])

def tool_94_chef():
    print(f"\n{Fore.YELLOW}[94] Chef — Altyapı Otomasyonu")
    tool_status("chef-client", "chef", ["--version"])

def tool_95_saltstack():
    print(f"\n{Fore.YELLOW}[95] SaltStack — Uzaktan Yürütme")
    tool_status("salt", "salt-master", ["--version"])

# ═══════════════════════════════════════════════════════════════════════════════
#                    96-104: BACKUP, FIREWALL, VPN, MISC
# ═══════════════════════════════════════════════════════════════════════════════

def tool_96_borgbackup():
    print(f"\n{Fore.YELLOW}[96] BorgBackup — Şifreli Yedekleme")
    tool_status("borg", "borgbackup", ["--version"])

def tool_97_restic():
    print(f"\n{Fore.YELLOW}[97] Restic — Hafif Şifreli Yedekleme")
    tool_status("restic", "restic", ["--version"])

def tool_98_iptables():
    print(f"\n{Fore.YELLOW}[98] iptables/nftables — Paket Filtreleme")
    if check_tool("iptables"):
        print(f"{Fore.GREEN}[+] iptables kurulu!")
        if input(f"{Fore.CYAN}[?] Mevcut kuralları görüntüle? (e/h): ").lower() == "e":
            run_cmd("sudo iptables -L -n -v")
    elif check_tool("nft"):
        print(f"{Fore.GREEN}[+] nftables kurulu!")
        run_cmd("sudo nft list ruleset")
    else:
        print(f"{Fore.RED}[-] iptables/nftables bulunamadı!")

def tool_99_ufw():
    print(f"\n{Fore.YELLOW}[99] UFW — Basit Firewall Yönetimi")
    if not check_tool("ufw"):
        print(f"{Fore.RED}[-] UFW kurulu değil! sudo apt install ufw -y"); return
    run_cmd("sudo ufw status verbose")

def tool_100_pfsense():
    print(f"\n{Fore.YELLOW}[100] pfSense — Firewall/Router Dağıtımı")
    print(f"{Fore.CYAN}[*] pfSense bir işletim sistemidir, bu araç üzerinden çalıştırılamaz.")
    print(f"{Fore.WHITE}  https://www.pfsense.org/download/ adresinden ISO indirilir.")

def tool_101_openvpn():
    print(f"\n{Fore.YELLOW}[101] OpenVPN — VPN Çözümü")
    tool_status("openvpn", "openvpn", ["--version"])

def tool_102_wireguard():
    print(f"\n{Fore.YELLOW}[102] WireGuard — Modern VPN")
    if not check_tool("wg"):
        print(f"{Fore.RED}[-] WireGuard kurulu değil! sudo apt install wireguard -y"); return
    print(f"{Fore.GREEN}[+] WireGuard kurulu!")
    if input(f"{Fore.CYAN}[?] Aktif bağlantıları gör? (e/h): ").lower() == "e":
        run_cmd("sudo wg show")

def tool_103_strongswan():
    print(f"\n{Fore.YELLOW}[103] StrongSwan — IPsec VPN")
    tool_status("ipsec", "strongswan", ["--version"])

def tool_104_ntopng():
    print(f"\n{Fore.YELLOW}[104] ntopng — Ağ Trafik Analizörü")
    if check_tool("ntopng"):
        print(f"{Fore.GREEN}[+] ntopng kurulu! Web: http://localhost:3000")
        run_cmd("ntopng --version")
    else:
        print(f"{Fore.RED}[-] ntopng kurulu değil! sudo apt install ntopng -y")

# ═══════════════════════════════════════════════════════════════════════════════
#                         ANA MENÜ & MOTOR
# ═══════════════════════════════════════════════════════════════════════════════

MENU = {
    "=== AĞ KEŞİF & TARAMA ===": {
        "1": ("Nmap — Port & Servis Taraması", tool_01_nmap),
        "2": ("Masscan — Hızlı Ağ Tarayıcı", tool_02_masscan),
        "3": ("Wireshark — Paket Analizörü", tool_03_wireshark),
        "4": ("Tcpdump — CLI Paket Yakalama", tool_04_tcpdump),
        "5": ("Suricata — IDS/IPS", tool_05_suricata),
        "6": ("Snort — Geleneksel IDS", tool_06_snort),
        "7": ("Zeek (Bro) — Ağ İzleme", tool_07_zeek),
        "8": ("cURL — HTTP İstek Aracı", tool_08_curl),
        "9": ("Netcat — Sihirli Ağ Aracı", tool_09_netcat),
        "10": ("Ping Sweep — Yerel Ağ Tarama", tool_10_ping_sweep),
        "11": ("Banner Grabbing — Servis Tanıma", tool_11_banner_grab),
        "12": ("Reverse IP Lookup", tool_12_reverse_ip),
        "13": ("CIDR Hesaplayıcı", tool_13_cidr_calc),
        "14": ("SSL/TLS Kontrolü", tool_14_ssl_check),
        "15": ("HTTP Header Analizi", tool_15_http_header),
    },
    "=== ZAFİYET TARAMA & WEB TEST ===": {
        "16": ("OpenVAS / Greenbone", tool_16_openvas),
        "17": ("Nessus — Zafiyet Tarayıcı", tool_17_nessus),
        "18": ("Nikto — Web Sunucusu Tarayıcı", tool_18_nikto),
        "19": ("OWASP ZAP — Web Tarayıcı", tool_19_owasp_zap),
        "20": ("Burp Suite — Web Analiz", tool_20_burp_suite),
        "21": ("Lynis — Sistem Denetimi", tool_21_lynis),
        "22": ("SQLi Tarayıcı (Python)", tool_22_sqli_scan),
        "23": ("XSS Tester (Python)", tool_23_xss_scan),
        "24": ("Open Redirect Tester", tool_24_open_redirect),
        "25": ("CSRF Token Kontrolü", tool_25_csrf_check),
    },
    "=== UÇ NOKTA GÜVENLİĞİ (BLUE TEAM) ===": {
        "26": ("OSSEC — Host IDS", tool_26_ossec),
        "27": ("Wazuh — HIDS/SIEM", tool_27_wazuh),
        "28": ("Fail2ban — Brute-force Engel", tool_28_fail2ban),
        "29": ("ModSecurity — WAF", tool_29_modsecurity),
        "30": ("ClamAV — Antivirüs", tool_30_clamav),
        "31": ("Rkhunter — Rootkit Tespiti", tool_31_rkhunter),
        "32": ("Chkrootkit — Rootkit Tarayıcı", tool_32_chkrootkit),
        "33": ("AIDE — Bütünlük Kontrolü", tool_33_aide),
        "34": ("Tripwire — Bütünlük İzleme", tool_34_tripwire),
        "35": ("auditd — Linux Denetim", tool_35_auditd),
        "36": ("SELinux — MAC Kontrolü", tool_36_selinux),
        "37": ("AppArmor — Profil MAC", tool_37_apparmor),
        "38": ("Sysdig — Sistem Çağrı İzleme", tool_38_sysdig),
        "39": ("Falco — Runtime Güvenlik", tool_39_falco),
        "40": ("osquery — Uç Nokta Sorgulama", tool_40_osquery),
    },
    "=== İZLEME & SIEM ===": {
        "41": ("Prometheus — Metrik Toplama", tool_41_prometheus),
        "42": ("Grafana — Dashboard", tool_42_grafana),
        "43": ("ELK Stack — Log Analizi", tool_43_elk),
        "44": ("Graylog — Log Yönetimi", tool_44_graylog),
        "45": ("Splunk — SIEM", tool_45_splunk),
        "46": ("Netdata — Gerçek Zamanlı İzleme", tool_46_netdata),
        "47": ("Nagios — Altyapı İzleme", tool_47_nagios),
        "48": ("Zabbix — Ağ İzleme", tool_48_zabbix),
        "49": ("TheHive — Olay Müdahale", tool_49_thehive),
        "50": ("Cortex — Analiz/Otomasyon", tool_50_cortex),
        "51": ("MISP — Tehdit İstihbaratı", tool_51_misp),
        "52": ("OpenCTI — TI Yönetimi", tool_52_opencti),
        "53": ("Packetbeat — Ağ Metrikleri", tool_53_packetbeat),
        "54": ("Filebeat — Log Gönderici", tool_54_filebeat),
        "55": ("Auditbeat — Host İzleme", tool_55_auditbeat),
    },
    "=== KONTeyner & BULUT GÜVENLİĞİ ===": {
        "56": ("Trivy — Container Zafiyet", tool_56_trivy),
        "57": ("Clair — İmaj Analizi", tool_57_clair),
        "58": ("Anchore Engine — Politika", tool_58_anchore),
        "59": ("Grype — Artefakt Tarama", tool_59_grype),
        "60": ("kube-bench — CIS K8s", tool_60_kubebench),
        "61": ("kube-hunter — K8s Değerlendirme", tool_61_kubehunter),
        "62": ("kubeaudit — K8s Denetim", tool_62_kubeaudit),
    },
    "=== KRİPTO & GİZLİ YÖNETİMİ ===": {
        "63": ("HashiCorp Vault — Secret Yönetimi", tool_63_vault),
        "64": ("GnuPG — Şifreleme/İmza", tool_64_gnupg),
        "65": ("Keycloak — IAM/SSO", tool_65_keycloak),
        "66": ("Certbot — TLS Sertifika", tool_66_certbot),
        "67": ("OpenSSL — Kripto Araçları", tool_67_openssl),
        "68": ("SSLyze — TLS Analizi", tool_68_sslyze),
        "69": ("Hash Identifier (Python)", tool_69_hash_id),
        "70": ("Şifre Üretici (Python)", tool_70_pass_gen),
        "71": ("Encode/Decode (Python)", tool_71_encode_decode),
        "72": ("Metadata Çıkarıcı (Python)", tool_72_metadata),
    },
    "=== ADLİ BİLİŞİM & SORUŞTURMA ===": {
        "73": ("Velociraptor — Uç Nokta Adli", tool_73_velociraptor),
        "74": ("GRR — Uç Nokta Müdahale", tool_74_grr),
        "75": ("Autopsy — Dijital Adli Analiz", tool_75_autopsy),
        "76": ("Sleuth Kit — Adli Kütüphane", tool_76_sleuthkit),
        "77": ("Volatility — Bellek Analizi", tool_77_volatility),
        "78": ("Bulk Extractor — Veri Çıkarım", tool_78_bulk_extractor),
        "79": ("Scalpel — Dosya Carve", tool_79_scalpel),
        "80": ("Foremost — Dosya Kurtarma", tool_80_foremost),
        "81": ("Plaso — Zaman Çizelgesi", tool_81_plaso),
        "82": ("MAC Adres Aracı (Python)", tool_82_mac_tool),
    },
    "=== DEVSECOPS & SAST ===": {
        "83": ("OpenSCAP — Uyumluluk Denetim", tool_83_openscap),
        "84": ("Bandit — Python SAST", tool_84_bandit),
        "85": ("Brakeman — Rails SAST", tool_85_brakeman),
        "86": ("Semgrep — Statik Analiz", tool_86_semgrep),
        "87": ("TruffleHog — Git Secret Arama", tool_87_trufflehog),
        "88": ("Gitleaks — Depo Secret Tespit", tool_88_gitleaks),
        "89": ("SonarQube — Kod Kalitesi", tool_89_sonarqube),
        "90": ("Dependabot — Bağımlılık Uyarı", tool_90_dependabot),
        "91": ("Snyk — Zafiyet Tarama", tool_91_snyk),
        "92": ("Ansible — Konfigürasyon Yönetimi", tool_92_ansible),
        "93": ("Puppet — Konfigürasyon", tool_93_puppet),
        "94": ("Chef — Altyapı Otomasyonu", tool_94_chef),
        "95": ("SaltStack — Uzaktan Yürütme", tool_95_saltstack),
    },
    "=== YEDEKLEME, GÜVENLİK DUVARI & VPN ===": {
        "96": ("BorgBackup — Şifreli Yedek", tool_96_borgbackup),
        "97": ("Restic — Hafif Yedekleme", tool_97_restic),
        "98": ("iptables/nftables — Firewall", tool_98_iptables),
        "99": ("UFW — Basit Firewall", tool_99_ufw),
        "100": ("pfSense — Firewall OS", tool_100_pfsense),
        "101": ("OpenVPN — VPN", tool_101_openvpn),
        "102": ("WireGuard — Modern VPN", tool_102_wireguard),
        "103": ("StrongSwan — IPsec VPN", tool_103_strongswan),
        "104": ("ntopng — Trafik Analizörü", tool_104_ntopng),
    }
}

def main():
    while True:
        banner()
        for category, items in MENU.items():
            print(f"\n{Fore.MAGENTA}{category}")
            for num, (name, _) in items.items():
                print(f"  {Fore.YELLOW}{num:>3}{Fore.WHITE} - {name}")
        print(f"\n{Fore.RED}  0 - Sistemi Kapat")
        print(f"{Fore.CYAN}{'─'*70}")
        
        choice = input(f"{Fore.GREEN}Mark.Os> ").strip()
        if choice == "0":
            print(f"\n{Fore.GREEN}[+] Mark.Os kapatıldı. Güvenli kal!"); break
        
        found = False
        for category, items in MENU.items():
            if choice in items:
                items[choice][1]()
                found = True
                break
        
        if not found:
            print(f"{Fore.RED}[-] Geçersiz seçim!")
            time.sleep(1)
        else:
            pause()

if __name__ == "__main__":
    main()
