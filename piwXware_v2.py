import os
import sys
import time
import platform
import subprocess

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama requests aiohttp scapy")
    from colorama import Fore, Style, init
    init(autoreset=True)

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def master_banner():
    ekran_temizle()
    print(f"""{Fore.RED}
  ██████╗ ██╗██╗    ██╗██╗  ██╗██╗    ██╗ █████╗ ██████╗ ███████╗    ██╗   ██╗██████╗ 
  ██╔══██╗██║██║    ██║╚██╗██╔╝██║    ██║██╔══██╗██╔══██╗██╔════╝    ██║   ██║╚════██╗
  ██████╔╝██║██║ █╗ ██║ ╚███╔╝ ██║ █╗ ██║███████║██████╔╝█████╗      ██║   ██║ █████╔╝
  ██╔═══╝ ██║██║███╗██║ ██╔██╗ ██║███╗██║██╔══██║██╔══██╗██╔══╝      ╚██╗ ██╔╝██╔═══╝ 
  ██║     ██║╚███╔███╔╝██╔╝ ██╗╚███╔███╔╝██║  ██║██║  ██║███████╗     ╚████╔╝ ███████╗
  ╚═╝     ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝      ╚═══╝  ╚══════╝
    {Fore.YELLOW}--- PIWXWARE v2 | ADVANCED CYBER PENETRATION SUITE ---
    {Fore.WHITE}Sistem Mimarisi: {platform.system()} | Bağımsız Modül Altyapısı
    {Fore.GREEN}[+] Durum: Etik Güvenlik ve Ofansif Analiz Laboratuvarı Aktif
    """)

def modulu_tetikle(modul_adi):
    """modules klasörünün içindeki siberknlik betiklerini çalıştırır"""
    dosya_yolu = os.path.join("modules", modul_adi)
    if os.path.exists(dosya_yolu):
        print(f"\n{Fore.YELLOW}[*] Modül yükleniyor: {modul_adi}...")
        time.sleep(1)
        try:
            subprocess.run([sys.executable, dosya_yolu])
        except Exception as e:
            print(f"{Fore.RED}[-] Modül hatası: {e}")
    else:
        print(f"\n{Fore.RED}[-] Hata: '{modul_adi}' bulunamadı! Lütfen modülü ekleyin.")

def ana_menu():
    while True:
        master_banner()
        print(f"{Fore.BLUE}[ 🛠️ OFANSİF & DEFANSİF SEÇENEKLER ]")
        print("1 - Gelişmiş Ağ Keşif & Zafiyet Tarayıcı (Recon Scanner)")
        print("2 - Asenkron Web Panel Mukavemet Motoru (Redray Engine)")
        print("3 - Akıllı Sosyal Mühendislik Link Analizörü (Link Phish Defender)")
        print("4 - Canlı Ağ Paket Koklayıcı & IDS Alarmı (NetAlert)")
        print("5 - Kali Linux Otomatik Araç Entegrasyon Merkezi")
        print("0 - Sistem İstasyonunu Kapat")
        print("-" * 65)
        
        secim = input(f"{Fore.CYAN}PiwXware > ").strip()
        
        if secim == "1": modulu_tetikle("recon_scanner.py")
        elif secim == "2": modulu_tetikle("redray_engine.py")
        elif secim == "3": modulu_tetikle("phish_analyzer.py")
        elif secim == "4": modulu_tetikle("net_alert.py")
        elif secim == "5": kali_entegrasyon_paneli()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] PiwXware Güvenli Modda Kapatıldı. İyi çalışmalar kanka!")
            break
        else:
            print(f"{Fore.RED}[-] Bilinmeyen modül seçimi.")
            time.sleep(1)
        input(f"\n{Fore.CYAN}Ana merkeze dönmek için Enter'a basın...")

def kali_entegrasyon_paneli():
    master_banner()
    print(f"{Fore.BLUE}[ KALI LINUX ENTEGRASYON SİSTEMİ ]")
    print("1 - Nmap Kur / Çalıştır")
    print("2 - Sqlmap Kur / Çalıştır")
    print("3 - Metasploit Framework Durum Kontrolü")
    print("0 - Geri Dön")
    
    sub_secim = input(f"{Fore.CYAN}PiwXware/Kali > ").strip()
    check_cmd = "where" if os.name == "nt" else "which"
    
    if sub_secim == "1":
        res = subprocess.run([check_cmd, "nmap"], capture_output=True, text=True)
        if res.stdout.strip(): os.system("nmap")
        else: print(f"{Fore.RED}[- ] Nmap kurulu değil. 'pkg install nmap' yazarak kurabilirsiniz.")
    elif sub_secim == "2":
        res = subprocess.run([check_cmd, "sqlmap"], capture_output=True, text=True)
        if res.stdout.strip(): os.system("sqlmap --wizard")
        else: print(f"{Fore.RED}[-] Sqlmap bulunamadı.")

if __name__ == "__main__":
    ana_menu()
import socket
import sys
from colorama import Fore

print(f"\n{Fore.RED}=== PIWXWARE RECONNAISSANCE SCANNER ===")
hedef = input(f"{Fore.GREEN}Taranacak Hedef IP veya Alan Adı: ").strip()

if not hedef:
    sys.exit(f"{Fore.RED}[-] Hedef boş bırakılamaz.")

print(f"{Fore.YELLOW}[*] Kritik servis portları taranıyor...\n")
portlar = [21, 22, 23, 25, 53, 80, 443, 3306, 8080]

for port in portlar:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.6)
    sonuc = s.connect_ex((hedef, port))
    if sonuc == 0:
        print(f"{Fore.GREEN}[+] Port {port:4d} : AÇIK")
        try:
            # Banner Grabbing - Servis sürüm bilgisi yakalama denemesi
            s.send(b"HEAD / HTTP/1.1\r\n\r\n")
            banner = s.recv(512).decode('utf-8', errors='ignore').strip()
            if banner:
                print(f"    {Fore.WHITE}↳ Servis Bilgisi: {banner.splitlines()[0]}")
        except: pass
    s.close()
print(f"\n{Fore.YELLOW}[+] Modül görevi tamamlandı.")
