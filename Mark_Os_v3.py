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
    print("[!] Gerekli kütüphaneler kuruluyor: colorama, requests, aiohttp")
    os.system(f"{sys.executable} -m pip install colorama requests aiohttp")
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
    
    if not ip:
        print(f"{Fore.RED}[-] IP adresi boş bırakılamaz!")
        return
    
    # Siber güvenlikte en kritik kapılar
    kritik_portlar = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy"
    }
    
    print(f"{Fore.CYAN}[*] {ip} üzerinde tarama yapılıyor...")
    acik_portlar = []
    
    for port, servis in kritik_portlar.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            if s.connect_ex((ip, port)) == 0:
                acik_portlar.append((port, servis))
                print(f"{Fore.GREEN}[+] PORT AÇIK -> {port} ({servis})")
                # DÜZELTME: 'if port in:' syntax hatası düzeltildi
                if port in [21, 23, 25, 110, 143]:
                    print(f"    {Fore.RED}[🚨 ZAFİYET] Bu port şifresiz veri iletiyor!")
            else:
                print(f"{Fore.RED}[-] PORT KAPALI -> {port} ({servis})")
        except Exception as e:
            print(f"{Fore.RED}[-] Hata ({port}): {e}")
        finally:
            s.close()
    
    if acik_portlar:
        print(f"\n{Fore.GREEN}[+] Toplam {len(acik_portlar)} açık port bulundu.")
    else:
        print(f"\n{Fore.YELLOW}[!] Açık port bulunamadı.")


async def asenkron_web_request(session, url, u_field, p_field, user, password, basarili_kelime):
    """Mermi hızında HTTP istekleri fırlatan asenkron motor"""
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    if SIFRE_BULUNDU:
        return
    payload = {u_field: user, p_field: password}
    try:
        async with session.post(url, data=payload, timeout=5) as resp:
            text = await resp.text()
            # DÜZELTME: Daha esnek hevristik analiz - başarılı giriş kelimesi kontrolü eklendi
            if basarili_kelime and basarili_kelime.lower() in text.lower():
                SIFRE_BULUNDU = True
                BULUNAN_SIFRE = password
                return
            # Giriş hatası kelimelerini denetleme (Hevristik Analiz)
            hata_kelimeleri = ["hatali", "wrong", "invalid", "incorrect", "error", "failed", "başarısız"]
            if resp.status == 200 and not any(k in text.lower() for k in hata_kelimeleri):
                SIFRE_BULUNDU = True
                BULUNAN_SIFRE = password
    except Exception:
        pass


async def redray_attack_core(url, u_field, p_field, user, wordlist, basarili_kelime):
    connector = aiohttp.TCPConnector(limit=50, ssl=False)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [asenkron_web_request(session, url, u_field, p_field, user, pwd, basarili_kelime) for pwd in wordlist]
        await asyncio.gather(*tasks)


def redray_brute_force():
    """Modül 2: Hydra Mantıklı Asenkron Şifre Mukavemet Test Aracı"""
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    print(f"\n{Fore.RED}[🚨] Redray Asenkron Şifre Saldırı Motoru")
    print(f"{Fore.YELLOW}[!] UYARI: Bu aracı yalnızca size ait sistemlerde kullanın!")
    
    url = input(f"{Fore.GREEN}Hedef Login URL: ").strip()
    u_field = input(f"{Fore.GREEN}Kullanıcı Alan Adı (User Field) [username]: ").strip() or "username"
    p_field = input(f"{Fore.GREEN}Şifre Alan Adı (Pass Field) [password]: ").strip() or "password"
    user = input(f"{Fore.GREEN}Saldırılacak Kullanıcı Adı: ").strip()
    w_path = input(f"{Fore.GREEN}Wordlist Yolu: ").strip()
    basarili_kelime = input(f"{Fore.GREEN}Başarılı giriş belirteci (örn: 'Welcome', boş bırakılabilir): ").strip()
    
    if not url or not user or not w_path:
        print(f"{Fore.RED}[-] Gerekli alanlar boş bırakılamaz!")
        return
    
    try:
        with open(w_path, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [line.strip() for line in f if line.strip()]
        
        if not wordlist:
            print(f"{Fore.RED}[-] Wordlist boş!")
            return
            
        SIFRE_BULUNDU = False
        BULUNAN_SIFRE = None
        print(f"{Fore.YELLOW}[*] {len(wordlist)} şifre şebekeye asenkron fırlatılıyor...")
        print(f"{Fore.CYAN}[*] Hedef: {url} | Kullanıcı: {user}")
        
        asyncio.run(redray_attack_core(url, u_field, p_field, user, wordlist, basarili_kelime))
        
        if SIFRE_BULUNDU:
            print(f"\n{Fore.GREEN}{'='*50}")
            print(f"{Fore.GREEN}[+] ŞİFRE BULUNDU: {BULUNAN_SIFRE}")
            print(f"{Fore.GREEN}{'='*50}")
        else:
            print(f"\n{Fore.RED}[-] Başarısız: Wordlist bitti, şifre bulunamadı.")
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Hata: Wordlist dosyası bulunamadı: {w_path}")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")


def kali_arac_entegrasyonu(cmd_name, install_pkg, arac_adi):
    """
    Modül 3: Kali Linux Yazılımlarını Otomatik Yöneten Sistem Alt Süreci
    DÜZELTME: Her araç için özelleştirilmiş kurulum ve çalıştırma mantığı eklendi
    """
    print(f"\n{Fore.YELLOW}[*] {arac_adi} kontrol ediliyor...")
    check_cmd = "where" if os.name == "nt" else "which"
    
    try:
        res = subprocess.run([check_cmd, cmd_name], capture_output=True, text=True, shell=(os.name == "nt"))
    except Exception as e:
        print(f"{Fore.RED}[-] Sistem komutu çalıştırılamadı: {e}")
        return
    
    if res.stdout.strip():
        print(f"{Fore.GREEN}[+] {arac_adi} hazır!")
        
        if cmd_name == "nmap":
            hedef = input(f"{Fore.GREEN}Taranacak IP/Domain: ").strip()
            if hedef:
                print(f"{Fore.CYAN}[*] nmap -sV -O {hedef} çalıştırılıyor...")
                os.system(f"nmap -sV -O {hedef}")
            else:
                print(f"{Fore.RED}[-] Hedef boş bırakılamaz!")
                
        elif cmd_name == "sqlmap":
            hedef_url = input(f"{Fore.GREEN}Test edilecek URL: ").strip()
            if hedef_url:
                print(f"{Fore.CYAN}[*] sqlmap -u '{hedef_url}' --batch --dbs çalıştırılıyor...")
                os.system(f"sqlmap -u '{hedef_url}' --batch --dbs")
            else:
                print(f"{Fore.RED}[-] URL boş bırakılamaz!")
                
        elif cmd_name == "msfconsole":
            print(f"{Fore.CYAN}[*] Metasploit Framework başlatılıyor...")
            os.system("msfconsole")
        else:
            os.system(cmd_name)
    else:
        print(f"{Fore.RED}[-] {arac_adi} sistemde bulunamadı!")
        q = input(f"{Fore.CYAN}[?] Kurulum talimatlarını görmek ister misiniz? (e/h): ").lower().strip()
        if q == "e":
            print(f"\n{Fore.YELLOW}[!] {arac_adi} Kurulum Talimatları:")
            if platform.system() == "Windows":
                print(f"{Fore.WHITE}  Windows'ta bu araçlar doğrudan çalışmaz.")
                print(f"{Fore.WHITE}  WSL (Windows Subsystem for Linux) kurun veya Kali Linux kullanın.")
            else:
                if cmd_name == "nmap":
                    print(f"{Fore.WHITE}  sudo apt update && sudo apt install nmap -y")
                elif cmd_name == "sqlmap":
                    print(f"{Fore.WHITE}  sudo apt update && sudo apt install sqlmap -y")
                    print(f"{Fore.WHITE}  VEYA: git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git")
                elif cmd_name == "msfconsole":
                    print(f"{Fore.WHITE}  curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall")
                    print(f"{Fore.WHITE}  chmod 755 msfinstall && ./msfinstall")
                else:
                    print(f"{Fore.WHITE}  sudo apt update && sudo apt install {install_pkg} -y")


def ip_geo_locator():
    """Modül 4: Canlı API Tabanlı IP Coğrafi Konum Takip Aracı"""
    print(f"\n{Fore.YELLOW}[*] IP Coğrafi Konum Çözücü")
    ip = input(f"{Fore.GREEN}Sorgulanacak IP (boş bırakırsan kendi IP'n): ").strip()
    
    try:
        # DÜZELTME: URL yapısı düzeltildi - /json/{ip} formatı
        api_url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        r = requests.get(api_url, timeout=10)
        data = r.json()
        
        if data.get("status") == "success":
            print(f"\n{Fore.GREEN}{'='*50}")
            print(f"{Fore.GREEN}[+] Konum Tespit Edildi:")
            print(f"{Fore.WHITE}  - IP        : {data.get('query')}")
            print(f"{Fore.WHITE}  - Ülke      : {data.get('country')} ({data.get('countryCode')})")
            print(f"{Fore.WHITE}  - Bölge     : {data.get('regionName')}")
            print(f"{Fore.WHITE}  - Şehir     : {data.get('city')}")
            print(f"{Fore.WHITE}  - ZIP       : {data.get('zip')}")
            print(f"{Fore.WHITE}  - ISP       : {data.get('isp')}")
            print(f"{Fore.WHITE}  - Organizasyon: {data.get('org')}")
            print(f"{Fore.WHITE}  - Zaman Dilimi: {data.get('timezone')}")
            lat = data.get('lat')
            lon = data.get('lon')
            # DÜZELTME: Google Maps URL'si düzeltildi
            if lat and lon:
                print(f"{Fore.CYAN}  - Harita    : https://www.google.com/maps?q={lat},{lon}")
            print(f"{Fore.GREEN}{'='*50}")
        else:
            print(f"{Fore.RED}[-] Geçersiz IP veya Yerel Ağ IP'si.")
            print(f"{Fore.RED}[-] Mesaj: {data.get('message', 'Bilinmeyen hata')}")
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}[-] API zaman aşımına uğradı.")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}[-] İnternet bağlantısı yok.")
    except Exception as e:
        print(f"{Fore.RED}[-] API Hatası: {e}")


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
    {Fore.YELLOW}[!] UYARI: Bu araçları yalnızca yetkili sistemlerde kullanın!
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
        
        if choice == "1":
            kurye_port_scanner()
        elif choice == "2":
            redray_brute_force()
        elif choice == "3":
            ip_geo_locator()
        elif choice == "4":
            kali_arac_entegrasyonu("nmap", "nmap", "Nmap")
        elif choice == "5":
            kali_arac_entegrasyonu("sqlmap", "sqlmap", "Sqlmap")
        elif choice == "6":
            kali_arac_entegrasyonu("msfconsole", "metasploit-framework", "Metasploit")
        elif choice == "0":
            print(f"\n{Fore.GREEN}[+] Mark.Os güvenli bir şekilde kapatıldı. İyi çalışmalar!")
            break
        else:
            print(f"{Fore.RED}[-] Bilinmeyen komut veya geçersiz seçim.")
            time.sleep(1)
        
        input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()
