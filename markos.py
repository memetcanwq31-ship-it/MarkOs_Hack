import os
import sys
import socket
import platform

# Girdiğiniz araç listesinin ve siber güvenlikteki gerçek görevlerinin tanımlanması
ARAC_VERITABANI = {
    "Nmap": "Ağ tarama ve zafiyet tespiti aracıdır. Açık portları ve servisleri bulur.",
    "Bettercap": "Ortadaki Adam (MITM) saldırıları ve kablosuz ağ analizleri için gelişmiş bir platformdur.",
    "Nethunter": "Kali Linux'un Android cihazlar için geliştirilmiş mobil sızma testi platformudur.",
    "edex-ui": "Bilim kurgu arayüzlerine benzeyen, terminali görselleştiren bir masaüstü ekran aracıdır.",
    "Sorgubot": "OSINT (Açık Kaynak İstihbaratı) süreçlerinde veri analizi ve bilgi toplama mantığını ifade eder.",
    "Ncat": "Ağ üzerinden veri okuma ve yazma sağlayan, 'Netcat' aracının modern ve gelişmiş versiyonudur.",
    "Hashcat": "Ekran kartının (GPU) gücünü kullanarak şifre hash'lerini kıran dünyanın en hızlı araçlarından biridir.",
    "John The Ripper": "Farklı formatlardaki şifrelenmiş dosyaları ve hash'leri kırmak için kullanılan bir diğer popüler araçtır.",
    "Hydra": "Web panelleri, SSH, FTP gibi servislere karşı hızlı sözlük (brute-force) saldırısı düzenleyen araçtır.",
    "Reaver": "WPA/WPA2 kablosuz ağ şifrelerini, WPS açıklarını istismar ederek kırmaya çalışan bir araçtır.",
    "Ddos_attack": "Sistemlerin yük kapasitesini ve dayanıklılığını ölçmek için yapılan Hizmet Engelleme testleridir.",
    "Wp-in / Wpscan": "WordPress tabanlı web sitelerindeki güvenlik açıklarını ve eklenti zafiyetlerini tarayan araçtır.",
    "Metasploit Framework": "Bulunan sistem açıklarını sömürmek (exploit) ve sızma testlerini yönetmek için kullanılan en büyük platformdur.",
    "Ettercap": "Yerel ağlarda (LAN) koklama (sniffing) ve MITM saldırıları gerçekleştiren klasik bir güvenlik aracıdır."
}

def sistem_bilgilerini_goster():
    # Ekranı temizle
    os.system("clear" if os.name == "posix" else "cls")
    
    print("=" * 50)
    print("      SİBER GÜVENLİK ARAÇLARI BİLGİ PANELİ       ")
    print("=" * 50)
    
    # OS ve Network Kütüphanelerinin Kullanımı
    print(f"[+] Çalışılan Dizin   : {os.getcwd()}")
    print(f"[+] İşletim Sistemi   : {platform.system()} {platform.release()}")
    try:
        # Cihazın yerel ağdaki adını alma
        print(f"[+] Cihaz Adı (Host)  : {socket.gethostname()}")
    except:
        pass
    print("=" * 50)

def menu():
    sistem_bilgilerini_goster()
    print("\n[ LİSTELENEN SİBER GÜVENLİK ARAÇLARI ]")
    
    # Araçları numaralandırarak listeleme
    arac_listesi = list(ARAC_VERITABANI.keys())
    for index, arac in enumerate(arac_listesi, 1):
        print(f"{index:2d}- {arac}")
    print(" 0- Çıkış")
    print("-" * 50)
    
    try:
        secim = int(input("Hakkında bilgi almak istediğiniz aracın numarasını girin: "))
        if secim == 0:
            print("\n[+] Programdan çıkılıyor. Güvenli günler!")
            sys.exit()
        elif 1 <= secim <= len(arac_listesi):
            secilen_arac = arac_listesi[secim - 1]
            print(f"\n[!] ARACIN GÖREVİ ({secilen_arac}):")
            print(f"--> {ARAC_VERITABANI[secilen_arac]}")
        else:
            print("\n[-] Geçersiz numara girdiniz.")
    except ValueError:
        print("\n[-] Lütfen sadece sayısal bir değer girin.")
    
    input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    while True:
        menu()
