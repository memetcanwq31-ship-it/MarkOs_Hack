import os
import sys
import socket
import time

# Gelişmiş renklendirme kütüphanesi kontrolü
try:
    from colorama import Fore, Style, init
    import requests
    init(autoreset=True)
except ImportError:
    os.system("pip install requests colorama")
    from colorama import Fore, Style, init
    import requests
    init(autoreset=True)

# Kullanıcı Veri Sözlüğü (Girdiğin şablona sadık kalındı)
hedef_veritabanı = {
    "username": "",
    "instagram_id": "",
    "ip_adresi": "",
    "konum_bilgisi": {}
}

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def banner_goster():
    ekran_temizle()
    print(f"""{Fore.RED}
  ██████╗ ███████╗██╗███╗   ██╗████████╗██╗     ▄██████▄  ▄████████ 
  ██╔══██╗██╔════╝██║████╗  ██║╚══██╔══╝██║    ███    ███ ███    ███ 
  ██║  ██║███████╗██║██╔██╗ ██║   ██║   ██║    ███    ███ ███    ███ 
  ██║  ██║╚════██║██║██║╚██╗██║   ██║   ██║    ███    ███ ███    ███ 
  ██████╔╝███████║██║██║ ╚████║   ██║   ███████  ▀██████▀   ▀████████ 
  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝                      
    {Fore.YELLOW}--- OSINT & IP Geo-Location Tracker v1.0.0 ---
    {Fore.CYAN}[+] Yetenekler: Canlı IP Konum Tespiti, Domain Çözücü, Soket Sinyali
    """)

def ip_konum_bul(ip):
    """Verilen IP adresinin coğrafi konumunu internetten canlı sorgular"""
    print(f"\n{Fore.YELLOW}[*] {ip} adresi için coğrafi konum sorgulanıyor...")
    try:
        # Ücretsiz ve yasal coğrafi konum API'si kullanılıyor
        url = f"http://ip-api.com{ip}"
        yanit = requests.get(url, timeout=5)
        
        if yanit.status_code == 200:
            veri = yanit.json()
            if veri.get("status") == "success":
                hedef_veritabanı["konum_bilgisi"] = {
                    "Ülke": veri.get("country"),
                    "Şehir": veri.get("city"),
                    "ISP (Sağlayıcı)": veri.get("isp"),
                    "Enlem (Lat)": veri.get("lat"),
                    "Boylam (Lon)": veri.get("lon")
                }
                
                print(f"\n{Fore.GREEN}[+] KONUM BİLGİLERİ BULUNDU:")
                for k, v in hedef_veritabanı["konum_bilgisi"].items():
                    print(f"{Fore.WHITE}  - {k:<15} : {v}")
                
                # Google Maps Linki Oluşturma
                print(f"{Fore.CYAN}  - Harita Linki    : https://google.com{veri.get('lat')},{veri.get('lon')}")
            else:
                print(f"{Fore.RED}[-] Hata: Geçersiz IP adresi veya özel (yerel) IP sorgulanamaz.")
        else:
            print(f"{Fore.RED}[-] API sunucusuna bağlanılamadı. Durum kodu: {yanit.status_code}")
    except Exception as e:
        print(f"{Fore.RED}[-] İstek hatası: {e}")

def domain_and_socket_test():
    """s.send ve socket mantığını kullanarak alan adından IP bulur ve sinyal atar"""
    print(f"\n{Fore.YELLOW}[*] Alan Adı IP Çözücü ve Soket Bağlantı Modülü")
    domain = input(f"{Fore.GREEN}Hedef Web Sitesi (Örn: google.com): ").strip()
    
    if not domain:
        print(f"{Fore.RED}[-] Alan adı boş bırakılamaz.")
        return

    try:
        # Alan adını IP adresine çeviriyoruz
        hedef_ip = socket.gethostbyname(domain)
        hedef_veritabanı["ip_adresi"] = hedef_ip
        print(f"{Fore.GREEN}[+] {domain} sitesinin gerçek IP adresi: {hedef_ip}")
        
        # Soket oluşturup s.send testi yapıyoruz
        print(f"{Fore.YELLOW}[*] Port 80 üzerinden TCP soketi açılıyor...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        
        if s.connect_ex((hedef_ip, 80)) == 0:
            print(f"{Fore.GREEN}[+] Bağlantı kuruldu. Paketler gönderiliyor (s.send)...")
            # Koddaki s.send yapıları gerçek hale getirildi
            s.send(b"HEAD / HTTP/1.1\r\n\r\n")
            s.send(b"Host: " + domain.encode() + b"\r\n")
            s.send(b"\r\n")
            print(f"{Fore.GREEN}[+] Sinyal başarıyla iletildi.")
            
            # IP adresini konumlandırmaya gönderiyoruz
            ip_konum_bul(hedef_ip)
        else:
            print(f"{Fore.RED}[-] Sitenin portu kapalı veya engellendi.")
        s.close()
        
    except Exception as e:
        print(f"{Fore.RED}[-] Soket/Domain hatası: {e}")

def ana_menu():
    while True:
        banner_goster()
        print(f"{Fore.BLUE}[ ANA MODÜLLER ]")
        print(f"{Fore.WHITE}1 - Manuel IP Adresi Gir ve Konum Bul")
        print(f"{Fore.WHITE}2 - Web Sitesi (Domain) Gir, IP Çöz ve Konumlandır (Soket Modu)")
        print(f"{Fore.WHITE}3 - Hedef Profil / Kullanıcı Veri Kartı Düzenle")
        print(f"{Fore.WHITE}0 - Çıkış")
        print("-" * 65)
        
        secim = input(f"{Fore.YELLOW}Seçiminiz: ").strip()
        
        if secim == "1":
            ip = input(f"{Fore.GREEN}Sorgulanacak IP Adresi (Örn: 8.8.8.8): ").strip()
            if ip:
                ip_konum_bul(ip)
            else:
                print(f"{Fore.RED}[-] IP adresi boş olamaz.")
            input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")
            
        elif secim == "2":
            domain_and_socket_test()
            input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")
            
        elif secim == "3":
            banner_goster()
            print(f"{Fore.BLUE}=== HEDEF PROFİL KARTI ===\n")
            hedef_veritabanı["username"] = input(f"{Fore.GREEN}Kullanıcı Adı girin: ").strip()
            hedef_veritabanı["instagram_id"] = input(f"{Fore.GREEN}Instagram ID girin: ").strip()
            print(f"\n{Fore.GREEN}[+] Kart Geçici Hafızaya Kaydedildi!")
            print(f"{Fore.WHITE}  - Kullanıcı Adı: {hedef_veritabanı['username']}")
            print(f"{Fore.WHITE}  - Instagram ID : {hedef_veritabanı['instagram_id']}")
            input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...")
            
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] Sistemden çıkılıyor. İyi çalışmalar kanka!")
            sys.exit()
        else:
            print(f"{Fore.RED}[-] Geçersiz seçim!")
            time.sleep(1)

if __name__ == "__main__":
    ana_menu()
