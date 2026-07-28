#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║           PIWXWARE PRO - ETIK SIBER GUVENLIK SUITI v3.0        ║
║    Yalnizca yetkili sistemlerde ve egitim amacli kullanim icindir║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import platform
import subprocess
import socket
import threading
import hashlib
import base64
import json
import re
import random
import string
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from itertools import product

# BAĞIMLILIKLAR
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] colorama kuruluyor...")
    os.system("pip install colorama requests")
    from colorama import Fore, Style, init
    init(autoreset=True)

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

# GLOBAL DEGISKENLER
RAPOR_VERILERI = []

# YARDIMCI FONKSIYONLAR
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clear()
    print(f"""{Fore.CYAN}
    ╔═══════════════════════════════════════════════════════════════╗
    ║  {Fore.RED}██████╗ ██╗██╗    ██╗██╗  ██╗██╗    ██╗ █████╗ ██████╗ {Fore.CYAN}    ║
    ║  {Fore.RED}██╔══██╗██║██║    ██║╚██╗██╔╝██║    ██║██╔══██╗██╔══██╗{Fore.CYAN}    ║
    ║  {Fore.RED}██████╔╝██║██║ █╗ ██║ ╚███╔╝ ██║ █╗ ██║███████║██████╔╝{Fore.CYAN}    ║
    ║  {Fore.RED}██╔═══╝ ██║██║███╗██║ ██╔██╗ ██║███╗██║██╔══██║██╔══██╗{Fore.CYAN}    ║
    ║  {Fore.RED}██║     ██║╚███╔███╔╝██╔╝ ██╗╚███╔███╔╝██║  ██║██║  ██║{Fore.CYAN}    ║
    ║  {Fore.RED}╚═╝     ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Fore.CYAN}    ║
    ║                                                               ║
    ║  {Fore.YELLOW}ETIK SIBER GUVENLIK & PENETRASYON TESTI SUITI v3.0 PRO{Fore.CYAN}   ║
    ║  {Fore.WHITE}Sistem: {platform.system()} | Python: {platform.python_version()} | Tarih: {datetime.now().strftime("%Y-%m-%d")}{Fore.CYAN}  ║
    ║  {Fore.GREEN}[✓] Yalnizca yetkili sistemlerde kullanim icindir{Fore.CYAN}          ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")

def log(msg, type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {"info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW, "error": Fore.RED, "highlight": Fore.MAGENTA}
    color = colors.get(type, Fore.WHITE)
    print(f"{Fore.WHITE}[{timestamp}] {color}{msg}{Style.RESET_ALL}")
    RAPOR_VERILERI.append(f"[{timestamp}] [{type.upper()}] {msg}")

def pause():
    input(f"\n{Fore.CYAN}[+] Ana menuye donmek icin Enter'a basin...{Style.RESET_ALL}")

def kaydet_rapor():
    if RAPOR_VERILERI:
        dosya = f"piwxware_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(dosya, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("  PIWXWARE PRO - SIZMA TESTI RAPORU\n")
            f.write(f"  Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            for satir in RAPOR_VERILERI:
                f.write(satir + "\n")
        log(f"Rapor kaydedildi: {dosya}", "success")

# MODUL 1: GELISMIS PORT TARAYICI
def port_scanner():
    banner()
    log("GELISMIS PORT TARAYICI AKTIF", "info")
    print(f"{Fore.YELLOW}[-] Not: Yalnizca size ait veya izin aldiginiz hedefleri tarayin!\n")
    hedef = input(f"{Fore.GREEN}[?] Hedef IP/Domain: {Fore.WHITE}").strip()
    if not hedef:
        log("Hedef bos birakilamaz!", "error")
        return
    try:
        baslangic = int(input(f"{Fore.GREEN}[?] Baslangic portu [1]: {Fore.WHITE}") or "1")
        bitis = int(input(f"{Fore.GREEN}[?] Bitis portu [1000]: {Fore.WHITE}") or "1000")
    except ValueError:
        log("Gecersiz port araligi!", "error")
        return
    timeout = float(input(f"{Fore.GREEN}[?] Timeout (sn) [0.5]: {Fore.WHITE}") or "0.5")
    thread_sayisi = int(input(f"{Fore.GREEN}[?] Thread sayisi [200]: {Fore.WHITE}") or "200")
    acik_portlar = []
    kilit = threading.Lock()
    def tara_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            sonuc = s.connect_ex((hedef, port))
            if sonuc == 0:
                with kilit:
                    acik_portlar.append(port)
                    log(f"Port {port} ACIK", "success")
                    try:
                        s.send(b"HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(hedef).encode())
                        banner_data = s.recv(1024).decode("utf-8", errors="ignore").strip()
                        if banner_data:
                            print(f"    {Fore.WHITE}↳ Banner: {banner_data.splitlines()[0][:80]}")
                    except:
                        pass
            s.close()
        except:
            pass
    log(f"Tarama baslatiliyor: {hedef}:{baslangic}-{bitis} | Threads: {thread_sayisi}", "info")
    baslangic_zamani = time.time()
    with ThreadPoolExecutor(max_workers=thread_sayisi) as executor:
        executor.map(tara_port, range(baslangic, bitis + 1))
    sure = time.time() - baslangic_zamani
    print(f"\n{Fore.CYAN}{'='*60}")
    log(f"Tarama tamamlandi! Sure: {sure:.2f} sn", "success")
    log(f"Toplam acik port: {len(acik_portlar)}", "info")
    if acik_portlar:
        print(f"{Fore.GREEN}[+] Acik portlar: {', '.join(map(str, acik_portlar))}")
    print(f"{Fore.CYAN}{'='*60}")

# MODUL 2: SUBDOMAIN ENUMERATION
def subdomain_enum():
    banner()
    log("SUBDOMAIN ENUMERASYON ARACI", "info")
    hedef = input(f"{Fore.GREEN}[?] Ana domain (orn: example.com): {Fore.WHITE}").strip()
    if not hedef:
        log("Domain bos birakilamaz!", "error")
        return
    subdomain_listesi = [
        "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
        "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "ns3", "m", "imap",
        "test", "ns", "blog", "pop3", "dev", "www2", "admin", "forum", "news",
        "vpn", "ns4", "www1", "mail2", "new", "mysql", "old", "lists", "support",
        "mobile", "mx", "static", "docs", "beta", "shop", "sql", "secure", "demo",
        "cp", "calendar", "wiki", "web", "media", "email", "images", "img",
        "www3", "start", "info", "stats", "login", "staging", "www4", "www5",
        "api", "app", "cdn", "assets", "video", "portal", "intranet", "extranet",
        "remote", "git", "svn", "jenkins", "jira", "confluence", "grafana", "prometheus",
        "kibana", "elasticsearch", "nagios", "zabbix", "cacti", "munin"
    ]
    bulunanlar = []
    log(f"{len(subdomain_listesi)} subdomain taraniyor...", "info")
    for sub in subdomain_listesi:
        tam_domain = f"{sub}.{hedef}"
        try:
            ip = socket.gethostbyname(tam_domain)
            log(f"{tam_domain} -> {ip}", "success")
            bulunanlar.append((tam_domain, ip))
        except socket.gaierror:
            pass
    print(f"\n{Fore.CYAN}{'='*60}")
    log(f"Tarama tamamlandi! {len(bulunanlar)} subdomain bulundu.", "info")
    if bulunanlar:
        for domain, ip in bulunanlar:
            print(f"  {Fore.GREEN}[✓] {domain:<35} {Fore.WHITE}{ip}")

# MODUL 3: DIZIN BRUTE FORCE
def dir_bruteforce():
    banner()
    log("DIZIN BRUTE FORCE ARACI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL (orn: http://example.com): {Fore.WHITE}").strip()
    if not hedef:
        log("Hedef bos!", "error")
        return
    if not hedef.startswith(("http://", "https://")):
        hedef = "http://" + hedef
    dizinler = [
        "admin", "login", "dashboard", "api", "test", "backup", "config",
        "wp-admin", "phpmyadmin", "admin.php", "login.php", "uploads",
        "images", "css", "js", "assets", "api/v1", "api/v2", "swagger",
        ".env", "robots.txt", "sitemap.xml", ".git", ".htaccess",
        "wp-content", "wp-includes", "cgi-bin", "tmp", "temp", "logs",
        "api/v3", "graphql", "graphiql", "playground", "console", "shell",
        "administrator", "manage", "panel", "control", "backend", "frontend",
        "dev", "development", "staging", "prod", "production", "uat",
        "api/docs", "api/swagger", "api/redoc", "openapi.json", "swagger.json",
        "actuator", "health", "metrics", "prometheus", "info", "env",
        "_vti_bin", "_vti_pvt", "aspnet_client", "exchange", "owa",
        "cacti", "nagios", "zabbix", "munin", "ganglia", "icinga",
        ".svn", ".git/config", ".DS_Store", "crossdomain.xml", "clientaccesspolicy.xml"
    ]
    log(f"{len(dizinler)} dizin taraniyor...", "info")
    bulunanlar = []
    for dizin in dizinler:
        url = f"{hedef}/{dizin}"
        try:
            response = requests.get(url, timeout=4, allow_redirects=False, headers={"User-Agent": "PiwXware/4.0"})
            if response.status_code in [200, 301, 302, 307, 403, 401]:
                log(f"[{response.status_code}] {url}", "success")
                bulunanlar.append((url, response.status_code))
        except:
            pass
    print(f"\n{Fore.CYAN}{'='*60}")
    log(f"{len(bulunanlar)} dizin/endpoint bulundu.", "info")

# MODUL 4: HASH CRACKER
def hash_cracker():
    banner()
    log("HASH CRACKER (MD5/SHA1/SHA256)", "info")
    hash_degeri = input(f"{Fore.GREEN}[?] Kirilacak hash: {Fore.WHITE}").strip()
    if not hash_degeri:
        log("Hash degeri bos!", "error")
        return
    uzunluk = len(hash_degeri)
    if uzunluk == 32:
        hash_tipi = "md5"; hash_func = hashlib.md5
    elif uzunluk == 40:
        hash_tipi = "sha1"; hash_func = hashlib.sha1
    elif uzunluk == 64:
        hash_tipi = "sha256"; hash_func = hashlib.sha256
    else:
        log("Desteklenmeyen hash formati!", "error")
        return
    log(f"Hash tipi tespit edildi: {hash_tipi.upper()}", "info")
    wordlist_yolu = input(f"{Fore.GREEN}[?] Wordlist dosyasi [varsayilan]: {Fore.WHITE}").strip()
    if not wordlist_yolu or not os.path.exists(wordlist_yolu):
        log("Varsayilan wordlist kullaniliyor...", "warning")
        wordlist = ["123456", "password", "12345678", "qwerty", "123456789",
                   "letmein", "1234567", "football", "iloveyou", "admin",
                   "welcome", "monkey", "login", "abc123", "111111",
                   "123123", "password123", "1234", "baseball", "qwertyuiop",
                   "superman", "1234567890", "master", "dragon", "sunshine",
                   "princess", "starwars", "trustno1", "batman", "harley",
                   "password1", "hacker", "root", "toor", "kali", "linux"]
    else:
        with open(wordlist_yolu, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [satir.strip() for satir in f.readlines()]
    log(f"Wordlist yuklendi: {len(wordlist)} kelime", "info")
    log("Kirma islemi baslatiliyor...", "info")
    baslangic = time.time()
    for kelime in wordlist:
        if hash_func(kelime.encode()).hexdigest() == hash_degeri:
            sure = time.time() - baslangic
            log(f"HASH KIRILDI! Sifre: {kelime}", "success")
            log(f"Sure: {sure:.3f} saniye", "info")
            return
    log("Hash kirilamadi. Daha buyuk wordlist deneyin.", "error")

# MODUL 5: WHOIS SORGULAMA
def whois_lookup():
    banner()
    log("WHOIS SORGULAMA ARACI", "info")
    domain = input(f"{Fore.GREEN}[?] Domain (orn: google.com): {Fore.WHITE}").strip()
    if not domain:
        log("Domain bos!", "error")
        return
    try:
        import whois
    except ImportError:
        log("python-whois kuruluyor...", "warning")
        os.system("pip install python-whois")
        import whois
    try:
        w = whois.whois(domain)
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}[+] Domain: {w.domain_name}")
        print(f"{Fore.YELLOW}[+] Registrar: {w.registrar}")
        print(f"{Fore.YELLOW}[+] Olusturulma: {w.creation_date}")
        print(f"{Fore.YELLOW}[+] Bitis: {w.expiration_date}")
        print(f"{Fore.YELLOW}[+] Name Servers: {w.name_servers}")
        print(f"{Fore.YELLOW}[+] Durum: {w.status}")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"WHOIS hatasi: {e}", "error")

# MODUL 6: AG BILGISI TOPLAMA
def network_info():
    banner()
    log("AG BILGISI TOPLAMA", "info")
    log(f"Hostname: {socket.gethostname()}", "info")
    try:
        log(f"Local IP: {socket.gethostbyname(socket.gethostname())}", "info")
    except:
        pass
    try:
        import psutil
        log("Ag arayuzleri:", "info")
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"  {Fore.GREEN}[✓] {interface}: {addr.address}")
                elif addr.family == psutil.AF_LINK:
                    print(f"  {Fore.YELLOW}    MAC: {addr.address}")
    except ImportError:
        log("psutil kurulu degil. 'pip install psutil' ile kurabilirsiniz.", "warning")
    hedef = input(f"\n{Fore.GREEN}[?] DNS cozumlemesi yapilacak domain: {Fore.WHITE}").strip()
    if hedef:
        try:
            ip = socket.gethostbyname(hedef)
            log(f"{hedef} -> {ip}", "success")
        except:
            log("DNS cozumlemesi basarisiz!", "error")

# MODUL 7: KALI LINUX ARAC ENTEGRASYONU
def kali_tools():
    banner()
    log("KALI LINUX / PENTEST ARAC PANELI", "info")
    print(f"""
    {Fore.YELLOW}[ KALI LINUX ARAC MENUSU ]

    {Fore.CYAN}[1]  {Fore.WHITE}Nmap - Ag tarayici ve guvenlik denetcisi
    {Fore.CYAN}[2]  {Fore.WHITE}Nikto - Web sunucu tarayici
    {Fore.CYAN}[3]  {Fore.WHITE}Gobuster - Dizin/DNS brute force
    {Fore.CYAN}[4]  {Fore.WHITE}WhatWeb - Web teknoloji tespiti
    {Fore.CYAN}[5]  {Fore.WHITE}Wafw00f - WAF tespiti
    {Fore.CYAN}[6]  {Fore.WHITE}Sqlmap - SQL Injection tespiti
    {Fore.CYAN}[7]  {Fore.WHITE}Hydra - Parola brute force
    {Fore.CYAN}[8]  {Fore.WHITE}John the Ripper - Hash kirma
    {Fore.CYAN}[9]  {Fore.WHITE}Aircrack-ng - Kablosuz ag kirma
    {Fore.CYAN}[10] {Fore.WHITE}Wireshark - Paket analizoru (tshark)
    {Fore.CYAN}[11] {Fore.WHITE}Metasploit Framework - Exploit gelistirme
    {Fore.CYAN}[12] {Fore.WHITE}Burp Suite - Web guvenlik testi
    {Fore.CYAN}[13] {Fore.WHITE}OWASP ZAP - Web uygulama tarayici
    {Fore.CYAN}[14] {Fore.WHITE}Recon-ng - OSINT framework
    {Fore.CYAN}[15] {Fore.WHITE}theHarvester - E-posta/OSINT toplama
    {Fore.CYAN}[16] {Fore.WHITE}Maltego - Gorsel istihbarat
    {Fore.CYAN}[17] {Fore.WHITE}Netcat - Ag soket araci
    {Fore.CYAN}[18] {Fore.WHITE}Enum4linux - SMB enumeration
    {Fore.CYAN}[19] {Fore.WHITE}Responder - LLMNR/NBT-NS poisoner
    {Fore.CYAN}[20] {Fore.WHITE}Impacket - Python ag protokolleri
    {Fore.CYAN}[21] {Fore.WHITE}Crackmapexec - Active Directory test
    {Fore.CYAN}[22] {Fore.WHITE}BloodHound - AD guvenlik analizi
    {Fore.CYAN}[23] {Fore.WHITE}LinPEAS / WinPEAS - Privilege Escalation
    {Fore.CYAN}[24] {Fore.WHITE}Sherlock - Windows exploit arama
    {Fore.CYAN}[25] {Fore.WHITE}Searchsploit - Exploit-DB arama
    {Fore.CYAN}[26] {Fore.WHITE}Hashcat - GPU hash kirma
    {Fore.CYAN}[27] {Fore.WHITE}CeWL - Ozel wordlist olusturucu
    {Fore.CYAN}[28] {Fore.WHITE}Dirb - Dizin brute force
    {Fore.CYAN}[29] {Fore.WHITE}Feroxbuster - Hizli dizin fuzzer
    {Fore.CYAN}[30] {Fore.WHITE}Masscan - Hizli port tarayici
    {Fore.CYAN}[0]  {Fore.WHITE}Geri Don
    """)
    secim = input(f"{Fore.GREEN}[?] Secim: {Fore.WHITE}").strip()
    check_cmd = "where" if os.name == "nt" else "which"
    tools = {
        "1": ("nmap", "nmap --help"),
        "2": ("nikto", "nikto -h"),
        "3": ("gobuster", "gobuster --help"),
        "4": ("whatweb", "whatweb --help"),
        "5": ("wafw00f", "wafw00f --help"),
        "6": ("sqlmap", "sqlmap --help"),
        "7": ("hydra", "hydra -h"),
        "8": ("john", "john --help"),
        "9": ("aircrack-ng", "aircrack-ng --help"),
        "10": ("tshark", "tshark -h"),
        "11": ("msfconsole", "msfconsole --help"),
        "12": ("burpsuite", "burpsuite --help"),
        "13": ("zaproxy", "zaproxy --help"),
        "14": ("recon-ng", "recon-ng --help"),
        "15": ("theHarvester", "theHarvester --help"),
        "16": ("maltego", "maltego --help"),
        "17": ("nc", "nc -h"),
        "18": ("enum4linux", "enum4linux --help"),
        "19": ("responder", "responder --help"),
        "20": ("impacket", "impacket --help"),
        "21": ("crackmapexec", "crackmapexec --help"),
        "22": ("bloodhound", "bloodhound --help"),
        "23": ("linpeas", "linpeas --help"),
        "24": ("sherlock", "sherlock --help"),
        "25": ("searchsploit", "searchsploit --help"),
        "26": ("hashcat", "hashcat --help"),
        "27": ("cewl", "cewl --help"),
        "28": ("dirb", "dirb --help"),
        "29": ("feroxbuster", "feroxbuster --help"),
        "30": ("masscan", "masscan --help")
    }
    if secim in tools:
        tool, help_cmd = tools[secim]
        res = subprocess.run([check_cmd, tool], capture_output=True, text=True)
        if res.returncode == 0:
            log(f"{tool} bulundu. Calistiriliyor...", "success")
            os.system(help_cmd)
        else:
            log(f"{tool} kurulu degil!", "error")
            log(f"Kurulum: sudo apt install {tool}", "warning")
    elif secim != "0":
        log("Gecersiz secim!", "error")

# MODUL 8: SSL/TLS SERTIFIKA ANALIZI
def ssl_analiz():
    banner()
    log("SSL/TLS SERTIFIKA ANALIZI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef domain: {Fore.WHITE}").strip()
    if not hedef:
        log("Domain bos!", "error")
        return
    try:
        import ssl
        context = ssl.create_default_context()
        with socket.create_connection((hedef, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hedef) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                print(f"\n{Fore.CYAN}{'='*60}")
                print(f"{Fore.GREEN}[+] SSL/TLS Versiyon: {version}")
                print(f"{Fore.GREEN}[+] Cipher Suite: {cipher[0]}")
                print(f"{Fore.GREEN}[+] Sertifika Konu: {cert.get('subject')}")
                print(f"{Fore.GREEN}[+] Sertifika Veren: {cert.get('issuer')}")
                print(f"{Fore.GREEN}[+] Gecerlilik Baslangic: {cert.get('notBefore')}")
                print(f"{Fore.GREEN}[+] Gecerlilik Bitis: {cert.get('notAfter')}")
                print(f"{Fore.GREEN}[+] SAN: {cert.get('subjectAltName')}")
                if version in ["TLSv1", "TLSv1.1", "SSLv3", "SSLv2"]:
                    log("UYARI: Eski ve guvensiz TLS versiyonu!", "error")
                else:
                    log("TLS versiyonu guvenli.", "success")
                print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"SSL analiz hatasi: {e}", "error")

# MODUL 9: HTTP GUVENLIK HEADER KONTROLU
def http_headers():
    banner()
    log("HTTP GUVENLIK HEADER KONTROLU", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL: {Fore.WHITE}").strip()
    if not hedef:
        log("URL bos!", "error")
        return
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    guvenlik_headerlari = [
        "Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options",
        "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
        "X-XSS-Protection", "Feature-Policy", "Expect-CT"
    ]
    try:
        response = requests.get(hedef, timeout=10, headers={"User-Agent": "PiwXware/4.0"})
        headers = response.headers
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}[*] Sunucu: {headers.get('Server', 'Bilinmiyor')}")
        print(f"{Fore.YELLOW}[*] Status: {response.status_code}")
        print(f"\n{Fore.WHITE}[ GUVENLIK HEADERLARI ANALIZI ]")
        eksik = []
        for header in guvenlik_headerlari:
            if header in headers:
                print(f"  {Fore.GREEN}[✓] {header:<35} {headers[header][:50]}")
            else:
                print(f"  {Fore.RED}[✗] {header:<35} EKSIK")
                eksik.append(header)
        if eksik:
            log(f"{len(eksik)} guvenlik headeri eksik!", "warning")
        else:
            log("Tum guvenlik headerlari mevcut!", "success")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"HTTP header hatasi: {e}", "error")

# MODUL 10: XSS TARAMA
def xss_scan():
    banner()
    log("REFLECTED XSS TARAMA", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL (parametre icermeli): {Fore.WHITE}").strip()
    if not hedef:
        log("URL bos!", "error")
        return
    payloadlar = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "\"><script>alert('XSS')</script>",
        "<body onload=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')>"
    ]
    log("Payloadlar test ediliyor...", "info")
    bulunan = []
    for payload in payloadlar:
        try:
            test_url = hedef + urllib.parse.quote(payload)
            response = requests.get(test_url, timeout=8, headers={"User-Agent": "PiwXware/4.0"})
            if payload in response.text:
                log(f"Potansiyel XSS! Payload: {payload[:40]}...", "warning")
                bulunan.append(payload)
        except:
            pass
    if bulunan:
        log(f"{len(bulunan)} potansiyel XSS zafiyeti!", "error")
    else:
        log("Reflected XSS tespit edilemedi.", "success")

# MODUL 11: SQL INJECTION TARAMA
def sql_scan():
    banner()
    log("SQL INJECTION TARAMA", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL (parametre icermeli): {Fore.WHITE}").strip()
    if not hedef:
        log("URL bos!", "error")
        return
    error_keywords = [
        "sql syntax", "mysql_fetch", "ORA-", "PostgreSQL", "SQLite",
        "Warning: mysql", "unclosed quotation", "quoted string not properly terminated",
        "SQLServer JDBC", "ODBC SQL Server Driver", "Microsoft OLE DB Provider"
    ]
    payloadlar = ["'", '"', "' OR '1'='1", "' AND 1=1--", "' UNION SELECT NULL--"]
    log("SQL Injection payloadlari test ediliyor...", "info")
    bulunan = False
    for payload in payloadlar:
        try:
            test_url = hedef + urllib.parse.quote(payload)
            response = requests.get(test_url, timeout=8, headers={"User-Agent": "PiwXware/4.0"})
            for keyword in error_keywords:
                if keyword.lower() in response.text.lower():
                    log(f"Potansiyel SQLi! Hata: {keyword}", "warning")
                    bulunan = True
        except:
            pass
    if not bulunan:
        log("Error-based SQL Injection tespit edilemedi.", "success")

# MODUL 12: IP GEOLOCATION
def ip_geo():
    banner()
    log("IP GEOLOCATION", "info")
    ip = input(f"{Fore.GREEN}[?] IP Adresi: {Fore.WHITE}").strip()
    if not ip:
        log("IP bos!", "error")
        return
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        if data.get("status") == "success":
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}[+] IP: {data.get('query')}")
            print(f"{Fore.GREEN}[+] Ulke: {data.get('country')} ({data.get('countryCode')})")
            print(f"{Fore.GREEN}[+] Sehir: {data.get('city')}")
            print(f"{Fore.GREEN}[+] Bolge: {data.get('regionName')}")
            print(f"{Fore.GREEN}[+] ISP: {data.get('isp')}")
            print(f"{Fore.GREEN}[+] Organizasyon: {data.get('org')}")
            print(f"{Fore.GREEN}[+] Koordinatlar: {data.get('lat')}, {data.get('lon')}")
            print(f"{Fore.GREEN}[+] Zaman Dilimi: {data.get('timezone')}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log("IP bilgisi alinamadi.", "error")
    except Exception as e:
        log(f"Geolocation hatasi: {e}", "error")

# MODUL 13: REVERSE IP LOOKUP
def reverse_ip():
    banner()
    log("REVERSE IP LOOKUP", "info")
    ip = input(f"{Fore.GREEN}[?] IP Adresi: {Fore.WHITE}").strip()
    if not ip:
        log("IP bos!", "error")
        return
    try:
        hostname = socket.gethostbyaddr(ip)
        log(f"Hostname: {hostname[0]}", "success")
        if hostname[1]:
            log(f"Aliaslar: {', '.join(hostname[1])}", "info")
    except socket.herror:
        log("Reverse lookup basarisiz.", "error")

# MODUL 14: WAF TESPITI
def waf_detect():
    banner()
    log("WAF/FIREWALL TESPITI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL: {Fore.WHITE}").strip()
    if not hedef:
        log("URL bos!", "error")
        return
    if not hedef.startswith(("http://", "https://")):
        hedef = "http://" + hedef
    waf_imzalari = {
        "Cloudflare": ["cloudflare", "cf-ray", "__cfduid"],
        "AWS WAF": ["awselb", "awsalb", "x-amzn-requestid"],
        "Akamai": ["akamai", "akamaighost"],
        "Sucuri": ["sucuri", "x-sucuri"],
        "Incapsula": ["incap_ses", "visid_incap"],
        "F5 BIG-IP": ["bigip", "f5"],
        "ModSecurity": ["mod_security", "modsecurity"],
        "Wordfence": ["wordfence"],
        "Barracuda": ["barra"]
    }
    try:
        normal = requests.get(hedef, timeout=8, headers={"User-Agent": "PiwXware/4.0"})
        malicious = requests.get(hedef + "?test=<script>alert(1)</script>", timeout=8, headers={"User-Agent": "PiwXware/4.0"})
        tespit_edilen = []
        for waf, imzalar in waf_imzalari.items():
            for imza in imzalar:
                if imza.lower() in str(normal.headers).lower() or imza.lower() in str(malicious.headers).lower():
                    if waf not in tespit_edilen:
                        tespit_edilen.append(waf)
        if tespit_edilen:
            log(f"WAF tespit edildi: {', '.join(tespit_edilen)}", "warning")
        else:
            log("WAF tespit edilemedi (veya bilinmeyen WAF).", "info")
    except Exception as e:
        log(f"WAF tespit hatasi: {e}", "error")

# MODUL 15: SIFRE URETICI
def password_generator():
    banner()
    log("GUCLU SIFRE URETICI", "info")
    try:
        uzunluk = int(input(f"{Fore.GREEN}[?] Sifre uzunlugu [16]: {Fore.WHITE}") or "16")
        sayi = input(f"{Fore.GREEN}[?] Sayi icersin mi? [E/h]: {Fore.WHITE}").strip().lower() != "h"
        ozel = input(f"{Fore.GREEN}[?] Ozel karakter icersin mi? [E/h]: {Fore.WHITE}").strip().lower() != "h"
        buyuk = input(f"{Fore.GREEN}[?] Buyuk harf icersin mi? [E/h]: {Fore.WHITE}").strip().lower() != "h"
        adet = int(input(f"{Fore.GREEN}[?] Kac adet sifre uretilsin [5]: {Fore.WHITE}") or "5")
    except ValueError:
        log("Gecersiz deger!", "error")
        return
    karakterler = string.ascii_lowercase
    if buyuk:
        karakterler += string.ascii_uppercase
    if sayi:
        karakterler += string.digits
    if ozel:
        karakterler += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    print(f"\n{Fore.CYAN}{'='*60}")
    for i in range(adet):
        sifre = ''.join(random.choice(karakterler) for _ in range(uzunluk))
        print(f"{Fore.GREEN}[{i+1}] {sifre}")
    print(f"{Fore.CYAN}{'='*60}")

# MODUL 16: BASE64 ENCODE/DECODE
def base64_tool():
    banner()
    log("BASE64 ENCODE/DECODE", "info")
    print(f"{Fore.CYAN}[1] {Fore.WHITE}Encode")
    print(f"{Fore.CYAN}[2] {Fore.WHITE}Decode")
    secim = input(f"{Fore.GREEN}[?] Secim: {Fore.WHITE}").strip()
    metin = input(f"{Fore.GREEN}[?] Metin: {Fore.WHITE}").strip()
    if not metin:
        log("Metin bos!", "error")
        return
    try:
        if secim == "1":
            sonuc = base64.b64encode(metin.encode()).decode()
            log(f"Encoded: {sonuc}", "success")
        elif secim == "2":
            sonuc = base64.b64decode(metin).decode()
            log(f"Decoded: {sonuc}", "success")
        else:
            log("Gecersiz secim!", "error")
    except Exception as e:
        log(f"Base64 hatasi: {e}", "error")

# MODUL 17: HASH OLUSTURUCU
def hash_generator():
    banner()
    log("HASH OLUSTURUCU", "info")
    metin = input(f"{Fore.GREEN}[?] Hashlenecek metin: {Fore.WHITE}").strip()
    if not metin:
        log("Metin bos!", "error")
        return
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}[+] MD5:    {hashlib.md5(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA1:   {hashlib.sha1(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA256: {hashlib.sha256(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA512: {hashlib.sha512(metin.encode()).hexdigest()}")
    print(f"{Fore.CYAN}{'='*60}")

# MODUL 18: STEGANOGRAFI
def steganografi():
    banner()
    log("BASIT STEGANOGRAFI", "info")
    print(f"{Fore.CYAN}[1] {Fore.WHITE}Metin gizle (Zero-Width karakter)")
    print(f"{Fore.CYAN}[2] {Fore.WHITE}Gizli metin cikar")
    secim = input(f"{Fore.GREEN}[?] Secim: {Fore.WHITE}").strip()
    if secim == "1":
        kapak = input(f"{Fore.GREEN}[?] Kapak metin: {Fore.WHITE}").strip()
        gizli = input(f"{Fore.GREEN}[?] Gizlenecek metin: {Fore.WHITE}").strip()
        binary = ''.join(format(ord(c), '08b') for c in gizli)
        sonuc = kapak
        for bit in binary:
            if bit == '1':
                sonuc += '\u200b'
            else:
                sonuc += '\u200c'
        log(f"Gizlenmis metin (kopyalayin):", "success")
        print(sonuc)
    elif secim == "2":
        metin = input(f"{Fore.GREEN}[?] Supheli metin: {Fore.WHITE}").strip()
        binary = ""
        for char in metin:
            if char == '\u200b':
                binary += '1'
            elif char == '\u200c':
                binary += '0'
        if binary:
            gizli = ""
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                if len(byte) == 8:
                    gizli += chr(int(byte, 2))
            log(f"Cikarilan metin: {gizli}", "success")
        else:
            log("Gizli metin bulunamadi.", "error")

# MODUL 19: PORT LISTENER
def port_listener():
    banner()
    log("PORT LISTENER", "info")
    try:
        port = int(input(f"{Fore.GREEN}[?] Dinlenecek port [4444]: {Fore.WHITE}") or "4444")
        max_baglanti = int(input(f"{Fore.GREEN}[?] Maksimum baglanti [5]: {Fore.WHITE}") or "5")
    except ValueError:
        log("Gecersiz port!", "error")
        return
    log(f"Port {port} dinleniyor... (Ctrl+C ile durdurun)", "info")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.listen(max_baglanti)
        while True:
            client, addr = s.accept()
            log(f"Baglanti alindi: {addr[0]}:{addr[1]}", "success")
            client.send(b"PiwXware Listener v3.0 - Baglanti aktif\n")
            data = client.recv(1024)
            if data:
                log(f"Veri alindi: {data.decode('utf-8', errors='ignore')[:100]}", "info")
            client.close()
    except KeyboardInterrupt:
        log("Listener durduruldu.", "warning")
        s.close()
    except Exception as e:
        log(f"Listener hatasi: {e}", "error")

# MODUL 20: TRACEROUTE
def traceroute():
    banner()
    log("TRACEROUTE", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef IP/Domain: {Fore.WHITE}").strip()
    if not hedef:
        log("Hedef bos!", "error")
        return
    max_hops = int(input(f"{Fore.GREEN}[?] Maksimum hop [30]: {Fore.WHITE}") or "30")
    timeout = int(input(f"{Fore.GREEN}[?] Timeout (sn) [2]: {Fore.WHITE}") or "2")
    log(f"Traceroute baslatiliyor: {hedef}", "info")
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE}Hop{' '*5}IP{' '*20}Zaman (ms)")
    print(f"{Fore.CYAN}{'='*60}")
    for ttl in range(1, max_hops + 1):
        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            recv_socket.settimeout(timeout)
            recv_socket.bind(("", 33434))
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            baslangic = time.time()
            send_socket.sendto(b"", (hedef, 33434))
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                gecen = (time.time() - baslangic) * 1000
                curr_addr = curr_addr[0]
                print(f"{Fore.GREEN}{ttl:<8}{curr_addr:<25}{gecen:.2f}")
                if curr_addr == hedef or socket.gethostbyname(hedef) == curr_addr:
                    log("Hedefe ulasildi!", "success")
                    break
            except socket.timeout:
                print(f"{Fore.YELLOW}{ttl:<8}{'*'*20:<25}TIMEOUT")
            send_socket.close()
            recv_socket.close()
        except PermissionError:
            log("RAW socket icin root yetkisi gerekli!", "error")
            break
        except Exception as e:
            log(f"Hop {ttl} hatasi: {e}", "error")
    print(f"{Fore.CYAN}{'='*60}")

# MODUL 21: ROBOTS.TXT ANALIZI
def robots_analiz():
    banner()
    log("ROBOTS.TXT ANALIZI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef domain: {Fore.WHITE}").strip()
    if not hedef:
        log("Domain bos!", "error")
        return
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    try:
        response = requests.get(f"{hedef}/robots.txt", timeout=10, headers={"User-Agent": "PiwXware/4.0"})
        if response.status_code == 200:
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}[+] robots.txt bulundu!")
            print(f"{Fore.WHITE}{response.text}")
            ilginc = []
            for line in response.text.splitlines():
                if line.strip().startswith("Disallow:"):
                    path = line.replace("Disallow:", "").strip()
                    if path and path != "/":
                        ilginc.append(path)
            if ilginc:
                print(f"\n{Fore.YELLOW}[*] Potansiyel ilginc dizinler:")
                for path in ilginc[:15]:
                    print(f"  {Fore.GREEN}-> {path}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log(f"robots.txt bulunamadi! Status: {response.status_code}", "error")
    except Exception as e:
        log(f"robots.txt hatasi: {e}", "error")

# MODUL 22: CMS TEKNOLOJI TESPITI
def cms_detect():
    banner()
    log("CMS TEKNOLOJI TESPITI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL: {Fore.WHITE}").strip()
    if not hedef:
        log("URL bos!", "error")
        return
    if not hedef.startswith(("http://", "https://")):
        hedef = "https://" + hedef
    try:
        response = requests.get(hedef, timeout=10, headers={"User-Agent": "PiwXware/4.0"})
        html = response.text.lower()
        headers_str = str(response.headers).lower()
        cms_imzalari = {
            "WordPress": ["/wp-content/", "wp-json"],
            "Joomla": ["joomla"],
            "Drupal": ["drupal"],
            "React": ["react"],
            "Vue.js": ["vue"],
            "Angular": ["angular"],
            "Laravel": ["laravel"],
            "Django": ["django"],
            "Flask": ["flask"]
        }
        bulunan = []
        for cms, imzalar in cms_imzalari.items():
            for imza in imzalar:
                if imza.lower() in html or imza.lower() in headers_str:
                    if cms not in bulunan:
                        bulunan.append(cms)
        print(f"\n{Fore.CYAN}{'='*60}")
        if bulunan:
            log("Tespit edilen teknolojiler:", "success")
            for cms in bulunan:
                print(f"  {Fore.GREEN}[✓] {cms}")
        else:
            log("CMS tespit edilemedi.", "warning")
        server = response.headers.get("Server", "Bilinmiyor")
        print(f"\n{Fore.YELLOW}[*] Sunucu: {server}")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"CMS tespit hatasi: {e}", "error")

# MODUL 23: WORDLIST OLUSTURUCU
def wordlist_generator():
    banner()
    log("OZEL WORDLIST OLUSTURUCU", "info")
    kelimeler = input(f"{Fore.GREEN}[?] Anahtar kelimeler (virgulle ayirin): {Fore.WHITE}").strip().split(",")
    kelimeler = [k.strip() for k in kelimeler if k.strip()]
    if not kelimeler:
        log("Kelime girilmedi!", "error")
        return
    max_uzunluk = int(input(f"{Fore.GREEN}[?] Maksimum kombinasyon uzunlugu [3]: {Fore.WHITE}") or "3")
    sonuclar = []
    for r in range(1, max_uzunluk + 1):
        for combo in product(kelimeler, repeat=r):
            sonuclar.append("".join(combo))
    dosya_adi = f"wordlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(dosya_adi, "w", encoding="utf-8") as f:
        for sifre in sonuclar:
            f.write(sifre + "\n")
    log(f"{len(sonuclar)} kombinasyon olusturuldu: {dosya_adi}", "success")

# MODUL 24: BASIT PAKET DINLEYICI (KENDI AG)
def packet_sniffer():
    banner()
    log("BASIT PAKET DINLEYICI", "info")
    log("UYARI: Sadece kendi aginizda kullanin!", "warning")
    try:
        import scapy.all as scapy
    except ImportError:
        log("scapy kuruluyor...", "warning")
        os.system("pip install scapy")
        try:
            import scapy.all as scapy
        except:
            log("scapy kurulamadi.", "error")
            return
    paket_sayisi = int(input(f"{Fore.GREEN}[?] Kac paket yakalansin [10]: {Fore.WHITE}") or "10")
    log(f"{paket_sayisi} paket dinleniyor... (Ctrl+C ile durdurun)", "info")
    try:
        paketler = scapy.sniff(count=paket_sayisi, timeout=30)
        print(f"\n{Fore.CYAN}{'='*60}")
        for i, pkt in enumerate(paketler, 1):
            src = pkt[scapy.IP].src if scapy.IP in pkt else "N/A"
            dst = pkt[scapy.IP].dst if scapy.IP in pkt else "N/A"
            proto = pkt[scapy.IP].proto if scapy.IP in pkt else "N/A"
            print(f"{Fore.GREEN}[{i}] {src:<20} -> {dst:<20} | Protokol: {proto}")
        print(f"{Fore.CYAN}{'='*60}")
    except PermissionError:
        log("Root yetkisi gerekli!", "error")
    except KeyboardInterrupt:
        log("Dinleyici durduruldu.", "warning")
    except Exception as e:
        log(f"Paket dinleyici hatasi: {e}", "error")

# MODUL 25: DNS ENUMERASYON
def dns_enum():
    banner()
    log("DNS ENUMERASYON", "info")
    domain = input(f"{Fore.GREEN}[?] Domain: {Fore.WHITE}").strip()
    if not domain:
        log("Domain bos!", "error")
        return
    kayit_tipleri = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]
    print(f"\n{Fore.CYAN}{'='*60}")
    for tip in kayit_tipleri:
        try:
            import dns.resolver
            cevaplar = dns.resolver.resolve(domain, tip)
            for cevap in cevaplar:
                print(f"{Fore.GREEN}[{tip:<6}] {str(cevap)}")
        except:
            pass
    print(f"{Fore.CYAN}{'='*60}")

# MODUL 26: METADATA CIKARICI
def metadata_extractor():
    banner()
    log("DOSYA METADATA CIKARICI", "info")
    dosya_yolu = input(f"{Fore.GREEN}[?] Dosya yolu: {Fore.WHITE}").strip()
    if not os.path.exists(dosya_yolu):
        log("Dosya bulunamadi!", "error")
        return
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(dosya_yolu)
        exif = img._getexif()
        if exif:
            print(f"\n{Fore.CYAN}{'='*60}")
            log("EXIF metadata bulundu!", "success")
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                print(f"  {Fore.GREEN}{tag:<30} {value}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log("EXIF metadata bulunamadi.", "warning")
    except ImportError:
        log("Pillow kurulu degil. 'pip install Pillow'", "warning")
    except Exception as e:
        log(f"Metadata hatasi: {e}", "error")

# MODUL 27: URL FUZZING
def url_fuzzing():
    banner()
    log("URL FUZZING", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef URL (FUZZ yer tutucusu): {Fore.WHITE}").strip()
    if "FUZZ" not in hedef:
        log("URL'de FUZZ yer tutucusu yok!", "error")
        return
    wordlist = input(f"{Fore.GREEN}[?] Wordlist (bos=varsayilan): {Fore.WHITE}").strip()
    if not wordlist or not os.path.exists(wordlist):
        kelimeler = ["admin", "test", "api", "v1", "v2", "dev", "backup", "config", "old", "new"]
    else:
        with open(wordlist, 'r') as f:
            kelimeler = [s.strip() for s in f.readlines()]
    log(f"{len(kelimeler)} kelime fuzzing ediliyor...", "info")
    bulunan = []
    for kelime in kelimeler:
        url = hedef.replace("FUZZ", kelime)
        try:
            response = requests.get(url, timeout=5, allow_redirects=False, headers={"User-Agent": "PiwXware/4.0"})
            if response.status_code != 404:
                log(f"[{response.status_code}] {url}", "success")
                bulunan.append((url, response.status_code))
        except:
            pass
    log(f"{len(bulunan)} sonuc bulundu.", "info")

# MODUL 28: ARP TARAMA (LOCAL AG)
def arp_scan():
    banner()
    log("ARP TARAMA (LOCAL AG)", "info")
    log("Sadece kendi local aginizda kullanin!", "warning")
    try:
        import scapy.all as scapy
    except ImportError:
        log("scapy kurulu degil.", "error")
        return
    hedef = input(f"{Fore.GREEN}[?] Hedef ag (orn: 192.168.1.0/24): {Fore.WHITE}").strip()
    if not hedef:
        log("Hedef bos!", "error")
        return
    try:
        log("ARP taramasi baslatiliyor...", "info")
        arp_request = scapy.ARP(pdst=hedef)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}IP{' '*20}MAC{' '*25}")
        print(f"{Fore.CYAN}{'='*60}")
        for element in answered_list:
            ip = element[1].psrc
            mac = element[1].hwsrc
            print(f"{Fore.GREEN}{ip:<25}{mac}")
        print(f"{Fore.CYAN}{'='*60}")
        log(f"{len(answered_list)} cihaz bulundu.", "success")
    except PermissionError:
        log("Root yetkisi gerekli!", "error")
    except Exception as e:
        log(f"ARP tarama hatasi: {e}", "error")

# MODUL 29: JWT TOKEN ANALIZI
def jwt_analiz():
    banner()
    log("JWT TOKEN ANALIZI", "info")
    token = input(f"{Fore.GREEN}[?] JWT Token: {Fore.WHITE}").strip()
    if not token:
        log("Token bos!", "error")
        return
    try:
        parts = token.split(".")
        if len(parts) != 3:
            log("Gecersiz JWT formati!", "error")
            return
        def decode_b64(data):
            padding = 4 - len(data) % 4
            if padding != 4:
                data += "=" * padding
            return base64.urlsafe_b64decode(data).decode('utf-8')
        header = json.loads(decode_b64(parts[0]))
        payload = json.loads(decode_b64(parts[1]))
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}[HEADER]")
        print(f"{Fore.GREEN}{json.dumps(header, indent=2)}")
        print(f"\n{Fore.YELLOW}[PAYLOAD]")
        print(f"{Fore.GREEN}{json.dumps(payload, indent=2)}")
        if header.get("alg") == "none":
            log("UYARI: 'none' algoritmasi - Guvenlik zafiyeti!", "error")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"JWT analiz hatasi: {e}", "error")

# MODUL 30: BASIT NMAP TARAYICI
def nmap_basit():
    banner()
    log("BASIT NMAP TARAYICI", "info")
    hedef = input(f"{Fore.GREEN}[?] Hedef IP/Domain: {Fore.WHITE}").strip()
    if not hedef:
        log("Hedef bos!", "error")
        return
    print(f"""
    {Fore.CYAN}[1] {Fore.WHITE}Hizli tarama (-F)
    {Fore.CYAN}[2] {Fore.WHITE}Versiyon tespiti (-sV)
    {Fore.CYAN}[3] {Fore.WHITE}OS tespiti (-O)
    {Fore.CYAN}[4] {Fore.WHITE}Agresif tarama (-A)
    {Fore.CYAN}[5] {Fore.WHITE}Custom komut
    """)
    secim = input(f"{Fore.GREEN}[?] Secim: {Fore.WHITE}").strip()
    komutlar = {
        "1": f"nmap -F {hedef}",
        "2": f"nmap -sV {hedef}",
        "3": f"nmap -O {hedef}",
        "4": f"nmap -A {hedef}",
        "5": None
    }
    if secim in komutlar:
        if secim == "5":
            komut = input(f"{Fore.GREEN}[?] Nmap komutu: {Fore.WHITE}").strip()
        else:
            komut = komutlar[secim]
        log(f"Calistiriliyor: {komut}", "info")
        os.system(komut)

# ANA MENU
def main():
    while True:
        banner()
        print(f"""
    {Fore.YELLOW}[ ETIK SIBER GUVENLIK ARACLARI - v3.0 PRO ]

    {Fore.CYAN}[1]  {Fore.WHITE}Gelismis Port Tarayici (Multi-threaded)
    {Fore.CYAN}[2]  {Fore.WHITE}Subdomain Enumeration
    {Fore.CYAN}[3]  {Fore.WHITE}Dizin Brute Force (Web)
    {Fore.CYAN}[4]  {Fore.WHITE}Hash Cracker (MD5/SHA1/SHA256)
    {Fore.CYAN}[5]  {Fore.WHITE}WHOIS Sorgulama
    {Fore.CYAN}[6]  {Fore.WHITE}Ag Bilgisi Toplama
    {Fore.CYAN}[7]  {Fore.WHITE}Kali Linux Arac Entegrasyonu (30+ Arac)
    {Fore.CYAN}[8]  {Fore.WHITE}SSL/TLS Sertifika Analizi
    {Fore.CYAN}[9]  {Fore.WHITE}HTTP Guvenlik Header Kontrolu
    {Fore.CYAN}[10] {Fore.WHITE}XSS Tarama
    {Fore.CYAN}[11] {Fore.WHITE}SQL Injection Tarama
    {Fore.CYAN}[12] {Fore.WHITE}IP Geolocation
    {Fore.CYAN}[13] {Fore.WHITE}Reverse IP Lookup
    {Fore.CYAN}[14] {Fore.WHITE}WAF Tespiti
    {Fore.CYAN}[15] {Fore.WHITE}Sifre Uretici
    {Fore.CYAN}[16] {Fore.WHITE}Base64 Encode/Decode
    {Fore.CYAN}[17] {Fore.WHITE}Hash Olusturucu
    {Fore.CYAN}[18] {Fore.WHITE}Steganografi
    {Fore.CYAN}[19] {Fore.WHITE}Port Listener
    {Fore.CYAN}[20] {Fore.WHITE}Traceroute
    {Fore.CYAN}[21] {Fore.WHITE}robots.txt Analizi
    {Fore.CYAN}[22] {Fore.WHITE}CMS Teknoloji Tespiti
    {Fore.CYAN}[23] {Fore.WHITE}Wordlist Olusturucu
    {Fore.CYAN}[24] {Fore.WHITE}Paket Dinleyici (Kendi Agin)
    {Fore.CYAN}[25] {Fore.WHITE}DNS Enumerasyon
    {Fore.CYAN}[26] {Fore.WHITE}Metadata Cikarici
    {Fore.CYAN}[27] {Fore.WHITE}URL Fuzzing
    {Fore.CYAN}[28] {Fore.WHITE}ARP Tarama (Local)
    {Fore.CYAN}[29] {Fore.WHITE}JWT Token Analizi
    {Fore.CYAN}[30] {Fore.WHITE}Basit Nmap Tarayici
    {Fore.CYAN}[99] {Fore.WHITE}Rapor Kaydet
    {Fore.CYAN}[0]  {Fore.WHITE}Cikis

    {Fore.RED}[!] UYARI: Bu araclar yalnizca yetkili sistemlerde kullanilmalidir!
    {Fore.RED}[!] Izinsiz kullanim yasal sorumluluk dogurur.
        """)
        secim = input(f"{Fore.GREEN}    PiwXware > {Fore.WHITE}").strip()
        moduller = {
            "1": port_scanner, "2": subdomain_enum, "3": dir_bruteforce,
            "4": hash_cracker, "5": whois_lookup, "6": network_info,
            "7": kali_tools, "8": ssl_analiz, "9": http_headers,
            "10": xss_scan, "11": sql_scan, "12": ip_geo,
            "13": reverse_ip, "14": waf_detect, "15": password_generator,
            "16": base64_tool, "17": hash_generator, "18": steganografi,
            "19": port_listener, "20": traceroute, "21": robots_analiz,
            "22": cms_detect, "23": wordlist_generator, "24": packet_sniffer,
            "25": dns_enum, "26": metadata_extractor, "27": url_fuzzing,
            "28": arp_scan, "29": jwt_analiz, "30": nmap_basit
        }
        if secim in moduller:
            moduller[secim]()
            pause()
        elif secim == "99":
            kaydet_rapor()
            pause()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] PiwXware kapatiliyor. Guvenli kalin!{Style.RESET_ALL}\n")
            break
        else:
            log("Gecersiz secim!", "error")
            time.sleep(1)

if __name__ == "__main__":
    main()
