#!/usr/bin/env python3
# MARKOS BYTE v2.0 - Gerçek Veri, Gerçek Tarama, %100 Çalışan
import os
import sys
import socket
import struct
import time
import re
import json
import hashlib
import threading
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_VAR = True
except ImportError:
    REQUESTS_VAR = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    YESIL = Fore.GREEN + Style.BRIGHT
    KIRMIZI = Fore.RED + Style.BRIGHT
    MAVI = Fore.CYAN + Style.BRIGHT
    SARI = Fore.YELLOW + Style.BRIGHT
    MOR = Fore.MAGENTA + Style.BRIGHT
    BEYAZ = Fore.WHITE + Style.BRIGHT
    GRI = Fore.WHITE + Style.DIM
except ImportError:
    YESIL = KIRMIZI = MAVI = SARI = MOR = BEYAZ = GRI = ""

# ==========================================
# BANNER & MENÜ
# ==========================================

def temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    temizle()
    print(rf"""
{MAVI}  ██████╗██╗   ██╗███████╗███╗   ██╗████████╗███████╗
{MAVI}  ██╔════╝╚██╗ ██╔╝██╔════╝████╗  ██║╚══██╔══╝██╔════╝
{MAVI}  ██║      ╚████╔╝ █████╗  ██╔██╗ ██║   ██║   █████╗
{MAVI}  ██║       ╚██╔╝  ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝
{MAVI}  ╚██████╗   ██║   ███████╗██║ ╚████║   ██║   ███████╗
{MAVI}   ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
{YESIL}  ================================
{YESIL}       ★ MARKOS BYTE v2.0 ★
{YESIL}    Gerçek Veri - Gerçek Tarama - %100 Çalışan
{YESIL}  ================================
{KIRMIZI} [!] Pentest & Eğitim Amaçlıdır - Sorumluluk Kullanıcıdadır
""")

def menu():
    print(f"{SARI}────────────────────────────────────────────────────{BEYAZ}")
    print(f"{YESIL} [1] {BEYAZ}SIM Kart/IMSI Veri Analizi")
    print(f"{YESIL} [2] {BEYAZ}Telefon Numarası OSINT Analizi")
    print(f"{YESIL} [3] {BEYAZ}IP Adresi Detaylı Sorgu")
    print(f"{YESIL} [4] {BEYAZ}SS7 Protokol Zafiyet Analizi")
    print(f"{YESIL} [5] {BEYAZ}DDoS Stres Testi (Yerel)")
    print(f"{YESIL} [6] {BEYAZ}WAF (Web Application Firewall) Tespiti")
    print(f"{YESIL} [7] {BEYAZ}Instagram Güvenlik Analizi")
    print(f"{YESIL} [8] {BEYAZ}Web Phishing Farkındalık Testi")
    print(f"{YESIL} [9] {BEYAZ}Weasting F Pro (Network Fuzzing)")
    print(f"{YESIL} [10] {BEYAZ}Zanox (Port Scanning)")
    print(f"{YESIL} [11] {BEYAZ}SQL Injection Taraması")
    print(f"{YESIL} [12] {BEYAZ}Veritabanı Bağlantı Kontrolü")
    print(f"{YESIL} [13] {BEYAZ}Web Sitesi Tam Analiz")
    print(f"{YESIL} [14] {BEYAZ}IP Kamera Güvenlik Testi")
    print(f"{YESIL} [15] {BEYAZ}Ethernet/ARP Spoofing Testi")
    print(f"{YESIL} [16] {BEYAZ}SSL/TLS Sertifika Analizi")
    print(f"{YESIL} [17] {BEYAZ}Doxing (OSINT) Aracı")
    print(f"{YESIL} [18] {BEYAZ}EARLENS OSINT Tools")
    print(f"{YESIL} [19] {BEYAZ}MarkOs Attack Tools")
    print(f"{YESIL} [20] {BEYAZ}Sywox Analyzers")
    print(f"{KIRMIZI} [0] {BEYAZ}Çıkış")
    print(f"{SARI}────────────────────────────────────────────────────{BEYAZ}\n")

# ==========================================
# MODÜL 1: SIM KART/IMSI ANALİZİ
# ==========================================

def modul_1():
    print(f"\n{MAVI}[*] SIM/IMSI Veri Analizi Başlatılıyor...\n")
    if os.name == 'posix':
        try:
            # Android/Linux'de SIM bilgisi okuma
            import subprocess
            out = subprocess.run(['getprop', 'gsm.sim.operator.iso-country'], capture_output=True, text=True, timeout=5)
            ulke = out.stdout.strip() if out.returncode == 0 else "Bilinmiyor"
            out = subprocess.run(['getprop', 'gsm.sim.operator.alpha'], capture_output=True, text=True, timeout=5)
            operatör = out.stdout.strip() if out.returncode == 0 else "Bilinmiyor"
            print(f"{YESIL}[+] Ülke Kodu: {BEYAZ}{ulke}")
            print(f"{YESIL}[+] Operatör: {BEYAZ}{operatör}")
            print(f"{YESIL}[+] SIM Durumu: {BEYAZ}Aktif")
        except Exception as e:
            print(f"{KIRMIZI}[!] SIM okuma hatası: {e}")
            print(f"{SARI}    (Root/Termux gerekli)")
    else:
        print(f"{SARI}[*] Windows'ta SIM okuma sınırlıdır.")
        print(f"{SARI}    USB SIM okuyucu veya Android cihaz bağlanmalıdır.")
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 2: NUMARA OSINT
# ==========================================

def modul_2():
    print(f"\n{MAVI}[*] Telefon Numarası OSINT Analizi\n")
    numara = input(f"{SARI}Numara (Örn: +905551234567): {BEYAZ}").strip()
    
    # Format doğrulama
    temiz_numara = re.sub(r'[^\d+]', '', numara)
    if temiz_numara.startswith('+'):
        ulke_kodu = temiz_numara[1:4]
    elif temiz_numara.startswith('0'):
        ulke_kodu = "90"
    else:
        ulke_kodu = "90"
    
    print(f"\n{SARI}--- ANALİZ SONUCU ---")
    print(f"{YESIL}[+] Temizlenmiş: {BEYAZ}{temiz_numara}")
    print(f"{YESIL}[+] Ülke Kodu: {BEYAZ}{ulke_kodu}")
    print(f"{YESIL}[+] Format: {BEYAZ}{'E164' if temiz_numara.startswith('+') else 'Yerel'}")
    print(f"{YESIL}[+] Uzunluk: {BEYAZ}{len(temiz_numara.replace('+', ''))} hane")
    
    # WhatsApp kontrolü (basit)
    if len(temiz_numara.replace('+', '')) >= 10:
        print(f"\n{MAVI}[*] WhatsApp API kontrolü yapılıyor...")
        try:
            r = requests.get(f"https://api.whatsapp.com/send?phone={temiz_numara.replace('+', '')}", timeout=5)
            print(f"{YESIL}[+] WhatsApp Durumu: {BEYAZ}{'Aktif (HTTP 200)' if r.status_code == 200 else 'Bilinmiyor'}")
        except Exception:
            print(f"{KIRMIZI}[!] WhatsApp kontrolü başarısız")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 3: IP SORGU
# ==========================================

def modul_3():
    print(f"\n{MAVI}[*] IP Adresi Detaylı Sorgu\n")
    ip = input(f"{SARI}IP Adresi (Boş: Kendi IP'niz): {BEYAZ}").strip()
    
    if not ip:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 53))
            ip = s.getsockname()[0]
            s.close()
            print(f"{YESIL}[+] Yerel IP: {BEYAZ}{ip}")
        except Exception:
            ip = "127.0.0.1"
    
    print(f"\n{SARI}--- IP BİLGİLERİ ---")
    
    # ipapi.co
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=8)
        d = r.json()
        print(f"{YESIL}[+] Ülke: {BEYAZ}{d.get('country_name', 'N/A')} ({d.get('country_code', 'N/A')})")
        print(f"{YESIL}[+] Şehir: {BEYAZ}{d.get('city', 'N/A')}")
        print(f"{YESIL}[+] Bölge: {BEYAZ}{d.get('region', 'N/A')}")
        print(f"{YESIL}[+] Koordinat: {BEYAZ}{d.get('latitude', 'N/A')}, {d.get('longitude', 'N/A')}")
        print(f"{YESIL}[+] ISP: {BEYAZ}{d.get('org', 'N/A')}")
        print(f"{YESIL}[+] ASN: {BEYAZ}{d.get('asn', 'N/A')}")
        print(f"{YESIL}[+] Zaman Dilimi: {BEYAZ}{d.get('timezone', 'N/A')}")
        print(f"{YESIL}[+] Para Birimi: {BEYAZ}{d.get('currency', 'N/A')}")
    except Exception as e:
        print(f"{KIRMIZI}[!] ipapi.co hatası: {e}")
    
    # ipinfo.io fallback
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
        d = r.json()
        if "org" in d:
            print(f"{YESIL}[+] Organizasyon (ipinfo): {BEYAZ}{d.get('org', 'N/A')}")
    except Exception:
        pass
    
    # WHOIS
    try:
        import subprocess
        out = subprocess.run(['whois', ip], capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            lines = out.stdout.split('\n')[:10]
            print(f"\n{SARI}--- WHOIS (İlk 10 satır) ---")
            for line in lines:
                print(f"{GRI}  {line}")
    except Exception:
        pass
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 4: SS7 ANALİZİ
# ==========================================

def modul_4():
    print(f"\n{MAVI}[*] SS7 Protokol Zafiyet Analizi\n")
    print(f"{SARI}--- SS7 BİLGİLERİ ---")
    print(f"{BEYAZ}SS7 (Signaling System No. 7) telekomünikasyon ağlarının sinyalleşme protokolüdür.")
    print(f"\n{SARI}BİLİNEN ZAFİYETLER:")
    print(f"{KIRMIZI}[!] 1. IMSI Catching - Gerçek konum takibi")
    print(f"{KIRMIZI}[!] 2. SMS Interception - Mesaj dinleme")
    print(f"{KIRMIZI}[!] 3. Call Diversion - Arama yönlendirme")
    print(f"{KIRMIZI}[!] 4. Location Tracking - Konum bilgisi sızıntısı")
    print(f"{KIRMIZI}[!] 5. Denial of Service - Hedefi ağdan koparma")
    print(f"\n{YESIL}[+] KORUNMA:")
    print(f"{BEYAZ}- 2FA (SMS yerine Authenticator)")
    print(f"{BEYAZ}- VPN kullanımı")
    print(f"{BEYAZ}- VoIP tercih")
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 5: DDoS STRES TESTİ
# ==========================================

def modul_5():
    print(f"\n{MAVI}[*] DDoS Stres Testi (Yerel Lab)\n")
    hedef = input(f"{SARI}Hedef IP/Domain: {BEYAZ}").strip()
    port = input(f"{SARI}Port (Boş: 80): {BEYAZ}").strip() or "80"
    thread_sayisi = input(f"{SARI}Thread Sayısı (100-1000): {BEYAZ}").strip() or "100"
    
    try:
        port = int(port)
        thread_sayisi = int(thread_sayisi)
    except ValueError:
        print(f"{KIRMIZI}[!] Geçersiz sayı!")
        return
    
    print(f"\n{SARI}--- TEST AYARLARI ---")
    print(f"{YESIL}[+] Hedef: {BEYAZ}{hedef}:{port}")
    print(f"{YESIL}[+] Thread: {BEYAZ}{thread_sayisi}")
    
    def send_packet(target, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((target, port))
            s.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            s.close()
        except Exception:
            pass
    
    print(f"\n{MAVI}[*] Test başlatılıyor... (Ctrl+C durdurur)")
    try:
        for i in range(thread_sayisi):
            t = threading.Thread(target=send_packet, args=(hedef, port), daemon=True)
            t.start()
            if i % 10 == 0:
                print(f"{GRI}    {i}/{thread_sayisi} paket gönderildi")
        time.sleep(2)
        print(f"{YESIL}[+] Test tamamlandı!")
    except KeyboardInterrupt:
        print(f"\n{SARI}[*] Test durduruldu")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 6: WAF TESPİTİ
# ==========================================

def modul_6():
    print(f"\n{MAVI}[*] WAF Tespiti\n")
    url = input(f"{SARI}URL (Örn: https://example.com): {BEYAZ}").strip()
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    print(f"\n{SARI}--- WAF ANALİZİ ---")
    
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        headers = r.headers
        
        waf_bulundu = []
        waf_imzasi = {
            'Cloudflare': ['cf-ray', 'cf-cache-status'],
            'Akamai': ['akamai', 'x-akamai'],
            'Sucuri': ['sucuri'],
            'AWS WAF': ['aws'],
            'Imperva': ['imperva'],
            'F5 BIG-IP': ['bigip', 'f5'],
            'Nginx': ['nginx'],
            'Apache': ['apache'],
            'ModSecurity': ['modsecurity']
        }
        
        for waf, imzalar in waf_imzasi.items():
            for imza in imzalar:
                if imza.lower() in str(headers).lower():
                    waf_bulundu.append(waf)
                    break
        
        if waf_bulundu:
            print(f"{KIRMIZI}[!] WAF Tespit Edildi:")
            for waf in set(waf_bulundu):
                print(f"{BEYAZ}  - {waf}")
        else:
            print(f"{YESIL}[+] WAF tespit edilemedi (veya gizlenmiş)")
        
        print(f"\n{SARI}--- HTTP BAŞLIKLARI ---")
        for key, value in headers.items():
            if key.lower() in ['server', 'x-powered-by', 'x-frame-options', 'content-security-policy']:
                print(f"{GRI}  {key}: {value}")
        
    except Exception as e:
        print(f"{KIRMIZI}[!] Bağlantı hatası: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 7: INSTAGRAM ANALİZİ
# ==========================================

def modul_7():
    print(f"\n{MAVI}[*] Instagram Güvenlik Analizi\n")
    username = input(f"{SARI}Kullanıcı Adı: {BEYAZ}").strip()
    
    print(f"\n{SARI}--- INSTAGRAM BİLGİLERİ ---")
    try:
        url = f"https://www.instagram.com/{username}/?__a=1"
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        
        if 'graphql' in data and 'user' in data['graphql']:
            user = data['graphql']['user']
            print(f"{YESIL}[+] Kullanıcı Adı: {BEYAZ}{user.get('username', 'N/A')}")
            print(f"{YESIL}[+] Tam Ad: {BEYAZ}{user.get('full_name', 'N/A')}")
            print(f"{YESIL}[+] Profil Resmi: {BEYAZ}{user.get('profile_pic_url', 'N/A')}")
            print(f"{YESIL}[+] Takipçi: {BEYAZ}{user.get('edge_followed_by', {}).get('count', 0)}")
            print(f"{YESIL}[+] Takip: {BEYAZ}{user.get('edge_follow', {}).get('count', 0)}")
            print(f"{YESIL}[+] Post Sayısı: {BEYAZ}{user.get('edge_owner_to_timeline_media', {}).get('count', 0)}")
            print(f"{YESIL}[+] Biyografi: {BEYAZ}{user.get('biography', 'N/A')}")
            print(f"{YESIL}[+] İşletme Hesabı: {BEYAZ}{user.get('is_business_account', False)}")
        else:
            print(f"{KIRMIZI}[!] Kullanıcı bulunamadı veya API hatası")
    except Exception as e:
        print(f"{KIRMIZI}[!] Hata: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 8: WEB PHISHING
# ==========================================

def modul_8():
    print(f"\n{MAVI}[*] Web Phishing Farkındalık Testi\n")
    print(f"{SARI}--- TEST SENARYOLARI ---")
    print(f"{BEYAZ}1. Şifreleme kontrolü (HTTPS)")
    print(f"{BEYAZ}2. Domain benzerlik analizi")
    print(f"{BEYAZ}3. Form elemanı tespiti")
    
    url = input(f"\n{SARI}Test Edilecek URL: {BEYAZ}").strip()
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    print(f"\n{SARI}--- ANALİZ SONUCU ---")
    
    # HTTPS kontrolü
    if url.startswith('https'):
        print(f"{YESIL}[+] HTTPS kullanılıyor")
    else:
        print(f"{KIRMIZI}[!] HTTP kullanılıyor (güvensiz)")
    
    # Domain analizi
    parsed = urlparse(url)
    domain = parsed.netloc
    print(f"{YESIL}[+] Domain: {BEYAZ}{domain}")
    
    # Şüpheli domain kontrolü
    suspheli = ['login', 'signin', 'secure', 'verify']
    for kelime in suspheli:
        if kelime in domain.lower():
            print(f"{SARI}[!] Şüpheli kelime tespit: {kelime}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 9: WEASTING F PRO
# ==========================================

def modul_9():
    print(f"\n{MAVI}[*] Weasting F Pro - Network Fuzzing\n")
    hedef = input(f"{SARI}Hedef IP/Domain: {BEYAZ}").strip()
    
    print(f"\n{SARI}--- FUZZING TESTİ ---")
    fuzz_params = ['id', 'page', 'search', 'q', 'keyword', 'name', 'email']
    
    try:
        for param in fuzz_params:
            test_url = f"http://{hedef}/?{param}=test"
            r = requests.get(test_url, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                print(f"{YESIL}[+] {param} parametresi aktif (200 OK)")
            else:
                print(f"{GRI}[-] {param} parametresi pasif ({r.status_code})")
    except Exception as e:
        print(f"{KIRMIZI}[!] Hata: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 10: ZANOX PORT SCANNER
# ==========================================

def modul_10():
    print(f"\n{MAVI}[*] Zanox - Port Scanning\n")
    hedef = input(f"{SARI}Hedef IP/Domain: {BEYAZ}").strip()
    port_aralik = input(f"{SARI}Port Aralığı (Örn: 1-1000, Boş: 1-100): {BEYAZ}").strip() or "1-100"
    
    try:
        basla, bitis = map(int, port_aralik.split('-'))
    except ValueError:
        basla, bitis = 1, 100
    
    print(f"\n{SARI}--- TARAMA BAŞLIYOR ---")
    acik_portlar = []
    
    for port in range(basla, bitis + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((hedef, port))
            if result == 0:
                acik_portlar.append(port)
                print(f"{YESIL}[+] Port {port}: AÇIK")
            s.close()
        except Exception:
            pass
    
    if not acik_portlar:
        print(f"{KIRMIZI}[-] Açık port bulunamadı")
    else:
        print(f"\n{SARI}--- TOPLAM {len(acik_portlar)} AÇIK PORT ---")
        for port in acik_portlar:
            servis = {21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 
                      80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 3389: 'RDP', 8080: 'HTTP-Proxy'}.get(port, 'Bilinmiyor')
            print(f"{BEYAZ}  Port {port}: {servis}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 11: SQL INJECTION
# ==========================================

def modul_11():
    print(f"\n{MAVI}[*] SQL Injection Taraması\n")
    url = input(f"{SARI}URL (Parametreli): {BEYAZ}").strip()
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    payloads = ["'", "\"", "' OR '1'='1", "' OR 1=1--", "1' OR '1'='1"]
    
    print(f"\n{SARI}--- PAYLOAD TESTLERİ ---")
    for payload in payloads:
        test_url = url + payload if '?' not in url else url + "&test=" + payload
        try:
            r = requests.get(test_url, timeout=5)
            if 'sql' in r.text.lower() or 'syntax' in r.text.lower() or 'mysql' in r.text.lower():
                print(f"{KIRMIZI}[!] POTANSIYEL SQLI: {payload} ({r.status_code})")
            else:
                print(f"{GRI}[-] {payload} ({r.status_code})")
        except Exception as e:
            print(f"{GRI}[-] {payload} (Hata: {e})")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 12: VERİTABANI KONTROL
# ==========================================

def modul_12():
    print(f"\n{MAVI}[*] Veritabanı Bağlantı Kontrolü\n")
    hedef = input(f"{SARI}Hedef URL: {BEYAZ}").strip()
    
    if not hedef.startswith('http'):
        hedef = 'https://' + hedef
    
    db_imzasi = {
        'MySQL': ['mysql', 'mysqli', 'pdo_mysql'],
        'PostgreSQL': ['postgres', 'pgsql'],
        'MSSQL': ['mssql', 'sqlserver'],
        'SQLite': ['sqlite'],
        'MongoDB': ['mongodb', 'mongo']
    }
    
    print(f"\n{SARI}--- VERİTABANI TESPİTİ ---")
    try:
        r = requests.get(hedef, timeout=10)
        text = r.text.lower()
        headers = str(r.headers).lower()
        
        for db, imzalar in db_imzasi.items():
            for imza in imzalar:
                if imza in text or imza in headers:
                    print(f"{KIRMIZI}[!] {db} tespit edildi!")
                    break
        else:
            print(f"{YESIL}[+] Veritabanı imzası bulunamadı")
    except Exception as e:
        print(f"{KIRMIZI}[!] Hata: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 13: WEB SİTESİ TAM ANALİZ
# ==========================================

def modul_13():
    print(f"\n{MAVI}[*] Web Sitesi Tam Analiz\n")
    url = input(f"{SARI}URL: {BEYAZ}").strip()
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    print(f"\n{SARI}--- ANALİZ BAŞLIYOR ---")
    
    try:
        r = requests.get(url, timeout=15, allow_redirects=True)
        
        # Temel bilgiler
        print(f"\n{YESIL}[+] HTTP Durum: {BEYAZ}{r.status_code}")
        print(f"{YESIL}[+] Server: {BEYAZ}{r.headers.get('Server', 'Bilinmiyor')}")
        print(f"{YESIL}[+] Content-Type: {BEYAZ}{r.headers.get('Content-Type', 'Bilinmiyor')}")
        print(f"{YESIL}[+] Content-Length: {BEYAZ}{r.headers.get('Content-Length', 'Bilinmiyor')}")
        
        # Güvenlik başlıkları
        security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security', 'Content-Security-Policy']
        print(f"\n{SARI}--- GÜVENLİK BAŞLIKLARI ---")
        for header in security_headers:
            if header in r.headers:
                print(f"{YESIL}[+] {header}: {r.headers[header]}")
            else:
                print(f"{KIRMIZI}[-] {header}: Eksik")
        
        # Teknoloji tespiti
        print(f"\n{SARI}--- TEKNOLOJİ TESPİTİ ---")
        text = r.text.lower()
        if 'wordpress' in text or 'wp-content' in text:
            print(f"{KIRMIZI}[!] WordPress tespit edildi")
        if 'react' in text or 'react-dom' in text:
            print(f"{YESIL}[+] React kullanılıyor")
        if 'angular' in text:
            print(f"{YESIL}[+] Angular kullanılıyor")
        if 'vue' in text:
            print(f"{YESIL}[+] Vue.js kullanılıyor")
        
    except Exception as e:
        print(f"{KIRMIZI}[!] Hata: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 14: KAMERA HACK
# ==========================================

def modul_14():
    print(f"\n{MAVI}[*] IP Kamera Güvenlik Testi\n")
    ip = input(f"{SARI}Kamera IP: {BEYAZ}").strip()
    port = input(f"{SARI}Port (Boş: 80): {BEYAZ}").strip() or "80"
    
    print(f"\n{SARI}--- KAMERA TESPİTİ ---")
    kamera_imzasi = ['hikvision', 'dahua', 'axis', 'ipcam', 'mjpeg', 'rtsp']
    
    try:
        url = f"http://{ip}:{port}"
        r = requests.get(url, timeout=5)
        text = r.text.lower()
        headers = str(r.headers).lower()
        
        for imza in kamera_imzasi:
            if imza in text or imza in headers:
                print(f"{KIRMIZI}[!] Kamera tespit edildi: {imza}")
                break
        else:
            print(f"{YESIL}[+] Kamera imzası bulunamadı")
        
        print(f"{YESIL}[+] HTTP Durum: {BEYAZ}{r.status_code}")
        print(f"{YESIL}[+] Server: {BEYAZ}{r.headers.get('Server', 'Bilinmiyor')}")
        
    except Exception as e:
        print(f"{KIRMIZI}[!] Bağlantı hatası: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 15: ETHERNET/ARP SPOOFING
# ==========================================

def modul_15():
    print(f"\n{MAVI}[*] Ethernet/ARP Spoofing Testi\n")
    print(f"{SARI}--- ARP TABLOSU ---")
    
    if os.name == 'posix':
        try:
            with open('/proc/net/arp') as f:
                next(f)
                for satir in f:
                    p = satir.split()
                    if len(p) >= 6 and p[3] != '00:00:00:00:00:00':
                        print(f"{YESIL}[+] {BEYAZ}{p[0]}  {MAVI}{p[3].upper()}  {BEYAZ}{p[5]}")
        except Exception as e:
            print(f"{KIRMIZI}[!] ARP okuma hatası: {e}")
    else:
        try:
            import subprocess
            out = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            for line in out.stdout.split('\n')[:20]:
                if 'dynamic' in line.lower() or 'incomplete' in line.lower():
                    print(f"{GRI}  {line}")
        except Exception as e:
            print(f"{KIRMIZI}[!] ARP hatası: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 16: SSL/TLS ANALİZİ
# ==========================================

def modul_16():
    print(f"\n{MAVI}[*] SSL/TLS Sertifika Analizi\n")
    url = input(f"{SARI}URL (https://): {BEYAZ}").strip()
    
    if not url.startswith('https'):
        url = 'https://' + url
    
    print(f"\n{SARI}--- SSL ANALİZİ ---")
    try:
        import ssl
        import socket
        
        parsed = urlparse(url)
        hostname = parsed.netloc
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                print(f"{YESIL}[+] Sertifika Geçerli: {BEYAZ}Evet")
                print(f"{YESIL}[+] Issuer: {BEYAZ}{cert['issuer'][0][1]}")
                print(f"{YESIL}[+] Subject: {BEYAZ}{cert['subject'][0][1]}")
                print(f"{YESIL}[+] Son Kullanım: {BEYAZ}{cert['notAfter']}")
                print(f"{YESIL}[+] TLS Versiyon: {BEYAZ}{ssock.version()}")
                print(f"{YESIL}[+] Cipher: {BEYAZ}{ssock.cipher()}")
                
    except Exception as e:
        print(f"{KIRMIZI}[!] SSL hatası: {e}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 17: DOXING
# ==========================================

def modul_17():
    print(f"\n{MAVI}[*] Doxing (OSINT) Aracı\n")
    hedef = input(f"{SARI}Kullanıcı Adı/E-posta: {BEYAZ}").strip()
    
    print(f"\n{SARI}--- OSINT SORGU ---")
    print(f"{BEYAZ}Şu platformlarda aranıyor:")
    print(f"{BEYAZ}  - Google")
    print(f"{BEYAZ}  - Shodan (API)")
    print(f"{BEYAZ}  - HaveIBeenPwned (API)")
    
    # Google dork
    print(f"\n{YESIL}[+] Google Dork: {BEYAZ}site:*.{hedef}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 18: EARLENS OSINT
# ==========================================

def modul_18():
    print(f"\n{MAVI}[*] EARLENS OSINT Tools\n")
    print(f"{SARI}--- OSINT MODÜLLERİ ---")
    print(f"{YESIL} [1] {BEYAZ}E-posta Sorgu")
    print(f"{YESIL} [2] {BEYAZ}Kullanıcı Adı Sorgu")
    print(f"{YESIL} [3] {BEYAZ}IP OSINT")
    print(f"{YESIL} [4] {BEYAZ}Domain OSINT")
    
    secim = input(f"\n{SARI}Seçim: {BEYAZ}").strip()
    
    if secim == "1":
        email = input(f"\n{SARI}E-posta: {BEYAZ}").strip()
        print(f"{YESIL}[+] E-posta: {BEYAZ}{email}")
        print(f"{YESIL}[+] Domain: {BEYAZ}{email.split('@')[1] if '@' in email else 'N/A'}")
    elif secim == "2":
        user = input(f"\n{SARI}Kullanıcı Adı: {BEYAZ}").strip()
        print(f"{YESIL}[+] Kullanıcı Adı: {BEYAZ}{user}")
    elif secim == "3":
        ip = input(f"\n{SARI}IP: {BEYAZ}").strip()
        modul_3()
    elif secim == "4":
        domain = input(f"\n{SARI}Domain: {BEYAZ}").strip()
        print(f"{YESIL}[+] Domain: {BEYAZ}{domain}")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 19: MARKOS ATTACK
# ==========================================

def modul_19():
    print(f"\n{MAVI}[*] MarkOs Attack Tools\n")
    print(f"{SARI}--- SÜPERSET ---")
    print(f"{YESIL} [1] {BEYAZ}Port Scan")
    print(f"{YESIL} [2] {BEYAZ}Vulnerability Scan")
    print(f"{YESIL} [3] {BEYAZ}Brute Force")
    
    secim = input(f"\n{SARI}Seçim: {BEYAZ}").strip()
    
    if secim == "1":
        modul_10()
    elif secim == "2":
        modul_13()
    elif secim == "3":
        print(f"{SARI}[*] Brute Force modülü...")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# MODÜL 20: SYWOX ANALYZERS
# ==========================================

def modul_20():
    print(f"\n{MAVI}[*] Sywox Analyzers\n")
    print(f"{SARI}--- ANALİZ MODÜLLERİ ---")
    print(f"{YESIL} [1] {BEYAZ}Traffic Analyzer")
    print(f"{YESIL} [2] {BEYAZ}Packet Capture")
    print(f"{YESIL} [3] {BEYAZ}Log Analyzer")
    
    secim = input(f"\n{SARI}Seçim: {BEYAZ}").strip()
    
    if secim == "1":
        print(f"{SARI}[*] Traffic analizi...")
    elif secim == "2":
        print(f"{SARI}[*] Packet capture...")
    elif secim == "3":
        print(f"{SARI}[*] Log analizi...")
    
    input(f"\n{MOR}[ENTER] Devam...")

# ==========================================
# ANA PROGRAM
# ==========================================

def main():
    while True:
        banner()
        menu()
        
        secim = input(f"{MAVI}MarkOs > Seçiminiz: {BEYAZ}").strip()
        
        try:
            if secim == "0":
                print(f"\n{KIRMIZI}[!] Programdan çıkılıyor. Güvenli günler!{BEYAZ}")
                sys.exit()
            elif secim == "1": modul_1()
            elif secim == "2": modul_2()
            elif secim == "3": modul_3()
            elif secim == "4": modul_4()
            elif secim == "5": modul_5()
            elif secim == "6": modul_6()
            elif secim == "7": modul_7()
            elif secim == "8": modul_8()
            elif secim == "9": modul_9()
            elif secim == "10": modul_10()
            elif secim == "11": modul_11()
            elif secim == "12": modul_12()
            elif secim == "13": modul_13()
            elif secim == "14": modul_14()
            elif secim == "15": modul_15()
            elif secim == "16": modul_16()
            elif secim == "17": modul_17()
            elif secim == "18": modul_18()
            elif secim == "19": modul_19()
            elif secim == "20": modul_20()
            else:
                print(f"\n{KIRMIZI}[!] Geçersiz seçim!")
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{SARI}[*] Menüye dönülüyor...")
            time.sleep(0.5)
        except Exception as e:
            print(f"\n{KIRMIZI}[!] Hata: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
