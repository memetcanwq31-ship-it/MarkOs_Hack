import os
import sys
import time
import socket
import subprocess
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama")
    from colorama import Fore, Style, init
    init(autoreset=True)

# ----------------- GERÇEK ARAÇ FONKSİYONLARI -----------------

def nmap_kur_calistir():
    """Kali Linux'taki Nmap aracını Termux'a entegre eder"""
    print(f"\n{Fore.YELLOW}[*] Nmap kontrol ediliyor...")
    # Termux'ta nmap kurulu mu bakıyoruz
    kontrol = subprocess.run(["which", "nmap"], capture_output=True, text=True)
    if not kontrol.stdout.strip():
        print(f"{Fore.CYAN}[!] Nmap bulunamadı. Otomatik kuruluyor...")
        os.system("pkg install nmap -y")
    
    hedef = input(f"{Fore.GREEN}Taranacak Hedef (IP veya Alan Adı): ").strip()
    if hedef:
        print(f"{Fore.YELLOW}[*] Hızlı port taraması başlatılıyor (nmap -F)...")
        os.system(f"nmap -F {hedef}")
    else:
        print(f"{Fore.RED}[-] Geçersiz hedef.")

def sqlmap_kur_calistir():
    """Kali Linux'taki Sqlmap aracını Termux'a otomatik kurar ve açar"""
    print(f"\n{Fore.YELLOW}[*] Sqlmap kontrol ediliyor...")
    if not os.path.exists("/data/data/com.termux/files/home/sqlmap"):
        print(f"{Fore.CYAN}[!] Sqlmap bulunamadı. GitHub'dan klonlanıyor...")
        os.system("git clone --depth 1 https://github.com ~/sqlmap")
    
    hedef_url = input(f"{Fore.GREEN}Açık taranacak URL (Örn: http://test.com): ").strip()
    if hedef_url:
        os.system(f"python ~/sqlmap/sqlmap.py -u '{hedef_url}' --batch --banner")
    else:
        print(f"{Fore.RED}[-] URL boş bırakılamaz.")

def python_port_scanner():
    """Kendi yazdığımız gerçek ve hızlı yerel ağ port tarayıcı"""
    print(f"\n{Fore.YELLOW}[*] Python Yerel Port Tarayıcı Başlatıldı.")
    hedef_ip = input(f"{Fore.GREEN}Hedef IP (Örn: 127.0.0.1): ").strip()
    try:
        print(f"{Fore.YELLOW}[*] Popüler portlar taranıyor...")
        populer_portlar = [21, 22, 23, 25, 53, 80, 110, 443, 8080]
        for port in populer_portlar:
            soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soket.settimeout(0.5)
            sonuc = soket.connect_ex((hedef_ip, port))
            if sonuc == 0:
                print(f"{Fore.GREEN}[+] Port {port} : AÇIK")
            soket.close()
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def osint_banner_grabber():
    """Hedef sunucunun hangi servisleri kullandığını bulan gerçek OSINT aracı"""
    print(f"\n{Fore.YELLOW}[*] Banner Grabbing (Servis Bilgisi Toplama)")
    hedef_ip = input(f"{Fore.GREEN}Hedef IP veya Domain: ").strip()
    hedef_port = int(input(f"{Fore.GREEN}Hedef Port (Örn: 21, 22, 80): "))
    try:
        soket = socket.socket()
        soket.settimeout(2.0)
        soket.connect((hedef_ip, hedef_port))
        # Sunucuya boş veya standart bir istek gönderip yanıtı okuyoruz
        if hedef_port == 80 or hedef_port == 443:
            soket.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        banner = soket.recv(1024).decode('utf-8', errors='ignore').strip()
        print(f"\n{Fore.GREEN}[+] Sunucudan Gelen Servis Bilgisi:\n{banner}")
    except Exception as e:
        print(f"{Fore.RED}[-] Bilgi alınamadı veya port kapalı: {e}")

def local_dos_test():
    """UDP Flood protokolü ile yerel ağ stres testi modülü"""
    print(f"\n{Fore.YELLOW}[*] UDP Ağ Stres Testi Modülü")
    hedef_ip = input(f"{Fore.GREEN}Hedef IP: ").strip()
    hedef_port = int(input(f"{Fore.GREEN}Hedef Port: "))
    try:
        soket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sahte_veri = b"X" * 1024
        print(f"{Fore.YELLOW}[*] Test başlatıldı. Durdurmak için CTRL+C basın.")
        for i in range(500): # Sistemi kilitlememek için yasal sınır
            soket.sendto(sahte_veri, (hedef_ip, hedef_port))
        print(f"{Fore.GREEN}[+] 500 adet test paketi başarıyla gönderildi.")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] Test durduruldu.")
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

# ----------------- MENÜ VE LOGIC SİSTEMİ -----------------

def banner_goster():
    os.system("clear")
    print(f"""{Fore.RED}
 ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ 
█       █       █       █       █       █       █       █
█   ▄▄▄▄█▄     ▄█    ▄  █    ▄▄▄█    ▄  █    ▄▄▄█▄     ▄█
█  █  ▄▄  █   █ █   █▄█ █   █▄▄▄█   █▄█ █   █▄▄▄  █   █  
█  █ █  █ █   █ █    ▄▄ █    ▄▄▄█    ▄▄ █    ▄▄▄█ █   █  
█  █▄▄█ █ █   █ █   █  ██   █▄▄▄█   █  ██   █▄▄▄  █   █  
█▄▄▄▄▄▄▄█ █▄▄▄█ █▄▄▄█  █▄█▄▄▄▄▄▄▄█▄▄▄█  █▄█▄▄▄▄▄▄▄█ █▄▄▄█  
    {Fore.CYAN}--- TERMUX ÖZEL İŞLETİM SİSTEMİ & ARAÇ KUTUSU v1.0 ---
    {Fore.WHITE}Geliştirici: GitHub Projeniz | Toplam Araç Kapasitesi: 120
    """)

def ana_menu():
    while True:
        banner_goster()
        print(f"{Fore.BLUE}[ KATAGORİLER ]")
        print(f"{Fore.WHITE}1 - Siber Güvenlik / Defansif Araçlar (İlk Modüller)")
        print(f"{Fore.WHITE}2 - Ofansif / Kali Linux Entegrasyon Araçları")
        print(f"{Fore.WHITE}0 - Çıkış")
        print("-" * 55)
        
        secim = input(f"{Fore.YELLOW}Kategori Seçin: ").strip()
        
        if secim == "1":
            siber_guvenlik_menusu()
        elif secim == "2":
            hack_menusu()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] Sistem kapatılıyor. Güvenli günler!")
            sys.exit()
        else:
            print(f"{Fore.RED}[-] Geçersiz seçim!")
            time.sleep(1)

def siber_guvenlik_menusu():
    while True:
        banner_goster()
        print(f"{Fore.BLUE}[ SİBER GÜVENLİK / DEFANSİF ARAÇLAR ]")
        print("1 - Python Hızlı Port Tarayıcı (Port Scanner)")
        print("2 - Banner Grabber (Servis Bilgisi Analizi)")
        print("3 - Ağ Stres Kapasite Testi (UDP Flood)")
        print(".. - (Buraya 60 araca kadar defansif modüller eklenecek)")
        print("0 - Ana Menüye Dön")
        print("-" * 55)
        
        secim = input(f"{Fore.YELLOW}Araç Seçin: ").strip()
        if secim == "1": python_port_scanner()
        elif secim == "2": osint_banner_grabber()
        elif secim == "3": local_dos_test()
        elif secim == "0": break
        input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")

def hack_menusu():
    while True:
        banner_goster()
        print(f"{Fore.BLUE}[ OFANSİF / HACK ARAÇLARI ]")
        print("1 - Nmap Entegrasyonu (Port ve Zafiyet Tarama)")
        print("2 - Sqlmap Entegrasyonu (SQL Injection Otomasyonu)")
        print(".. - (Buraya Kali Linux'tan 60 araca kadar entegrasyon eklenecek)")
        print("0 - Ana Menüye Dön")
        print("-" * 55)
        
        secim = input(f"{Fore.YELLOW}Araç Seçin: ").strip()
        if secim == "1": nmap_kur_calistir()
        elif secim == "2": sqlmap_kur_calistir()
        elif secim == "0": break
        input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    ana_menu()
