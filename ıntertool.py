import os
import sys
import time
import socket
import platform
import subprocess

# Gelişmiş renklendirme kütüphanesi kontrolü
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[*] Gerekli 'colorama' kütüphanesi kuruluyor...")
    os.system("pip install colorama")
    from colorama import Fore, Style, init
    init(autoreset=True)

# Girdiğin Kali Linux araçlarının veritabanı ve sistemdeki terminal komut karşılıkları
KALI_ARAClAR = {
    "1": {"name": "sqlmap", "cmd": "sqlmap", "desc": "SQL Injection zafiyet tespit ve sömürü otomasyonu."},
    "2": {"name": "sqlmapapi", "cmd": "sqlmapapi", "desc": "Sqlmap'i API modunda uzaktan çalıştırma servisi."},
    "3": {"name": "metasploit", "cmd": "msfconsole", "desc": "Dünyanın en büyük sızma testi ve exploit platformu."},
    "4": {"name": "bettercap", "cmd": "bettercap", "desc": "Gelişmiş MITM (Ortadaki Adam) ve ağ analiz aracı."},
    "5": {"name": "Ettercap", "cmd": "ettercap", "desc": "Yerel ağlarda koklama (sniffing) ve zehirleme aracı."},
    "6": {"name": "WireShark", "cmd": "wireshark", "desc": "Grafiksel ağ paket analiz ve izleme yazılımı."},
    "7": {"name": "Sherlock", "cmd": "sherlock", "desc": "Sosyal medya üzerinde kullanıcı adı üzerinden OSINT arama aracı."},
    "8": {"name": "burpsuite", "cmd": "burpsuite", "desc": "Web uygulamaları güvenlik testi ve proxy (istek yakalama) aracı."},
    "9": {"name": "caido", "cmd": "caido", "desc": "Burp Suite'e alternatif, Rust ile yazılmış hafif web proxy aracı."},
    "10": {"name": "dirb", "cmd": "dirb", "desc": "Sözlük tabanlı web dizini ve gizli klasör bulucu aracı."},
    "11": {"name": "dirbuster", "cmd": "dirbuster", "desc": "Grafik arayüze sahip gelişmiş web dizin tarayıcısı."},
    "12": {"name": "maltego", "cmd": "maltego", "desc": "Görsel tabanlı devasa siber istihbarat (OSINT) ilişkilendirme aracı."},
    "13": {"name": "nmap", "cmd": "nmap", "desc": "Ağ keşfi, port tarama ve sistem zafiyeti tespit yazılımı."},
    "14": {"name": "zenmap", "cmd": "zenmap", "desc": "Nmap aracının grafiksel arayüze (GUI) sahip versiyonu."},
    "15": {"name": "Hydra", "cmd": "hydra", "desc": "Ağ servislerine (SSH, FTP vb.) karşı hızlı brute-force aracı."},
    "16": {"name": "John The Ripper", "cmd": "john", "desc": "Farklı formatlardaki şifre hash'lerini kıran popüler yazılım."},
    "17": {"name": "ffuf", "cmd": "ffuf", "desc": "Go diliyle yazılmış, dünyanın en hızlı web fuzzing (tarama) aracı."},
    "18": {"name": "Raven", "cmd": "raven", "desc": "Kimlik avı ve siber savunma testlerinde kullanılan yardımcı modül."}
}

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def banner_goster():
    ekran_temizle()
    print(f"""{Fore.CYAN}
  ██████╗ ███╗   ██╗████████╗███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     
  ██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     
  ██████╔╝██╔██╗ ██║   ██║   █████╗  ██████╔╝   ██║   ██║   ██║██║   ██║██║     
  ██╔═══╝ ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗   ██║   ██║   ██║██║   ██║██║     
  ██║     ██║ ╚████║   ██║   ███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗
  ╚═╝     ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    {Fore.RED}--- InterTool v1.0.0 | Hepsi Bir Arada Siber Güvenlik İstasyonu ---
    {Fore.GREEN}[+] Desteklenen Platformlar: Termux, Linux, Windows, macOS
    {Fore.WHITE}[*] Toplam Hazır Entegre Modül: {len(KALI_ARAClAR)} Kali Aracı + Ağ Entegrasyonu
    """)

def network_test_modulu():
    """Yazdığın s.send mantığını kullanan gerçek bir Port/Bağlantı Test aracı"""
    print(f"\n{Fore.YELLOW}[*] Python Ağ ve Soket (s.send) Kontrol Modülü")
    hedef_ip = input(f"{Fore.GREEN}Test edilecek Hedef IP (Örn: 127.0.0.1): ").strip()
    hedef_port = input(f"{Fore.GREEN}Test edilecek Port (Örn: 80): ").strip()
    
    if not hedef_ip or not hedef_port:
        print(f"{Fore.RED} [-] Hata: IP veya Port boş olamaz.")
        return

    try:
        port = int(hedef_port)
        # TCP Soket bağlantısı açıyoruz
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        print(f"{Fore.YELLOW}[*] Sinyal gönderiliyor (s.send)...")
        
        # El sıkışma denemesi
        sonuc = s.connect_ex((hedef_ip, port))
        if sonuc == 0:
            print(f"{Fore.GREEN}[+] BAŞARILI: Port {port} aktif!")
            # Sunucuya örnek bir veri gönderimi (s.send simülasyonu)
            s.send(b"PING\r\n")
            print(f"{Fore.GREEN}[+] Veri paketi soket üzerinden başarıyla iletildi.")
        else:
            print(f"{Fore.RED}[-] BAŞARISIZ: Port {port} kapalı veya erişilemez durumda.")
        s.close()
    except Exception as e:
        print(f"{Fore.RED}[-] Soket hatası oluştu: {e}")

def arac_durum_kontrol(cmd):
    """Aracın sistem terminalinde kurulu olup olmadığını yasal yolla sorgular"""
    sistem = platform.system()
    # Windows için 'where', Linux/Termux için 'which' komutu kullanılır
    kontrol_komutu = "where" if sistem == "Windows" else "which"
    try:
        sonuc = subprocess.run([kontrol_komutu, cmd], capture_output=True, text=True)
        return bool(sonuc.stdout.strip())
    except:
        return False

def kali_araclari_menusu():
    while True:
        banner_goster()
        print(f"{Fore.BLUE}[ KALI LINUX ENTEGRE ARAÇ LİSTESİ ]")
        print(f"{Fore.WHITE}{'No':<4} {'Araç Adı':<18} {'Durum (Sisteminizde)':<22}")
        print("-" * 55)
        
        for k, v in KALI_ARAClAR.items():
            kurulu_mu = arac_durum_kontrol(v["cmd"])
            durum_yazisi = f"{Fore.GREEN}Yüklü / Hazır" if kurulu_mu else f"{Fore.RED}Kurulu Değil"
            print(f"{Fore.WHITE}{k:<4} {v['name']:<18} {durum_yazisi}")
            
        print(f"\n{Fore.YELLOW}99 - Ağ ve Soket Testini Çalıştır (s.send Modülü)")
        print(f"{Fore.YELLOW}0  - Sistemden Çıkış")
        print("-" * 55)
        
        secim = input(f"{Fore.CYAN}Hakkında bilgi almak veya çalıştırmak için numara girin: ").strip()
        
        if secim == "0":
            print(f"\n{Fore.GREEN}[+] InterTool kapatılıyor. Güvenli günler dilerim bebiş!")
            sys.exit()
        elif secim == "99":
            network_test_modulu()
            input(f"\n{Fore.CYAN}Menüye dönmek için Enter'a basın...")
        elif secim in KALI_ARAClAR:
            secilen = KALI_ARAClAR[secim]
            banner_goster()
            print(f"{Fore.BLUE}=== ARAÇ DETAYI: {secilen['name'].upper()} ===")
            print(f"{Fore.WHITE}Açıklama: {secilen['desc']}")
            print(f"{Fore.WHITE}Terminal Tetikleme Komutu: {secilen['cmd']}")
            print("-" * 55)
            
            kurulu_mu = arac_durum_kontrol(secilen["cmd"])
            if kurulu_mu:
                calistir = input(f"{Fore.GREEN}Bu araç sisteminizde yüklü! Doğrudan başlatılsın mı? (e/h): ").lower().strip()
                if calistir == "e":
                    print(f"{Fore.YELLOW}[*] {secilen['name']} başlatılıyor... Çıkmak için araç içinde 'exit' yazın.")
                    time.sleep(1)
                    os.system(secilen["cmd"])
            else:
                print(f"{Fore.RED}[!] Uyarı: Bu araç şu an kullandığınız işletim sisteminde kurulu değil.")
                print(f"{Fore.WHITE}Kurmak için Linux/Termux üzerinde: 'sudo apt install {secilen['cmd']}' veya 'pkg install {secilen['cmd']}' yazabilirsiniz.")
                
            input(f"\n{Fore.CYAN}Geri dönmek için Enter'a basın...")
        else:
            print(f"{Fore.RED}[-] Geçersiz seçim yaptınız.")
            time.sleep(1)

if __name__ == "__main__":
    kali_araclari_menusu() 


# InterTool - Cross-Platform Security Station

InterTool, Kali Linux dünyasındaki en popüler siber güvenlik ve penetrasyon testi araçlarını tek bir dinamik arayüz altında birleştiren, çapraz platform destekli bir Python framework'üdür.

## 🚀 Desteklenen İşletim Sistemleri
- **Android (Termux)**
- **Linux (Kali, Ubuntu, Debian vb.)**
- **Windows (CMD / PowerShell)**
- **macOS**

## 🛠️ Kurulum Komutları

### Termux İçin (Android):
```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com
cd InterTool
python InterTool.py
```

### Kali Linux / Linux İçin:
```bash
sudo apt update && sudo apt install python3 git -y
git clone https://github.com
cd InterTool
python3 InterTool.py
```

### Windows İçin:
Python yüklü olduğundan emin olduktan sonra terminale yazın:
```cmd
git clone https://github.com
cd InterTool
python InterTool.py
```

## ⚖️ Yasal Uyarı (Disclaimer)
Bu araç yalnızca eğitim, defansif analiz ve laboratuvar sızma testleri amacıyla geliştirilmiştir. Yetkisiz sistemlerde kullanımı yasal sorumluluk doğurur.

