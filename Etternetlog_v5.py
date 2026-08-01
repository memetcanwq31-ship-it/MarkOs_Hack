#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Proje Adı: Etternetlog.py
# Sürüm: v6.0
# Amacı: Çok İş Parçacıklı (Multi-threaded) Gelişmiş Siber Güvenlik ve Analiz Framework

import os
import sys
import socket
import json
import time
import hashlib
import threading

# Terminal Renk Kodları (ANSI)
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def ekran_temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner_goster():
    print(f"{CYAN}{BOLD}")
    print(r"  ______ _   _                        _   _                 ")
    print(r" |  ____| | | |                      | | | |                ")
    print(r" | |__  | |_| |_ ___ _ __ _ __   ___ | |_| | ___   __ _     ")
    print(r" |  __| | __| __/ _ \ '__| '_ \ / _ \| __| |/ _ \ / _` |    ")
    print(r" | |____| |_| ||  __/ |  | | | |  __/| |_| | (_) | (_| |    ")
    print(r" |______|\__|\__\___|_|  |_| |_|\___| \__|_|\___/ \__, |    ")
    print(r"                                                   __/ |    ")
    print(f"                                                  |___/ v6.0{RESET}")
    print(f"{RED}=================================================================={RESET}")
    print(f"{YELLOW}[+] Proje: Etternetlog v6.0 Güçlendirilmiş Siber Panel{RESET}")
    print(f"{YELLOW}[+] Özellik: Çok İş Parçacıklı (Multi-threaded) Hızlı Tarama Motoru{RESET}")
    print(f"{RED}=================================================================={RESET}\n")

# --- 1. MODÜL: HIZLANDIRILMIŞ MULTI-THREAD PORT TARAYICI ---
def port_kontrol(hedef_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    sonuc = s.connect_ex((hedef_ip, port))
    if sonuc == 0:
        try:
            servis = socket.getservbyport(port)
        except:
            servis = "Bilinmeyen Servis"
        print(f"{GREEN}[+] Port {port} [{servis.upper()}] --> AÇIK!{RESET}")
    s.close()

def hizli_port_tarayici():
    print(f"\n{YELLOW}[*] Multi-threaded Kritik Port Tarayıcı Başlatıldı{RESET}")
    hedef_ip = input("Taranacak Hedef IP veya Domain: ").strip()
    print(f"{BLUE}[*] Tarama ajanları dağıtılıyor...{RESET}\n")
    
    # Siber güvenlikte taranan en kritik 20 standart port
    kritik_portlar = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
    
    threadler = []
    for port in kritik_portlar:
        # Her port için arka planda ayrı bir iş parçacığı (Thread) başlatarak hızlandırıyoruz
        t = threading.Thread(target=port_kontrol, args=(hedef_ip, port))
        threadler.append(t)
        t.start()
        
    for t in threadler:
        t.join() # Tüm taramaların bitmesini bekle
        
    print(f"\n{CYAN}[+] Eşzamanlı port taraması tamamlandı.{RESET}")
    input(f"\n{CYAN}Ana menüye dönmek için Enter'a bas kanka...{RESET}")

# --- 2. MODÜL: GERÇEK HTTP DURUM VE HEADER ANALİZÖRÜ ---
def http_header_analiz():
    print(f"\n{YELLOW}[*] Web Sunucu HTTP Durum Kod Analiz Motoru{RESET}")
    hedef_web = input("Hedef Domain (Örn: google.com veya IP): ").strip()
    port = 80
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((hedef_web, port))
        
        # Gerçek bir HTTP ham isteği oluşturulup gönderiliyor
        istek = f"HEAD / HTTP/1.1\r\nHost: {hedef_web}\r\nUser-Agent: Etternetlog_v6.0\r\n\r\n"
        s.sendall(istek.encode('utf-8'))
        
        yanit = s.recv(1024).decode('utf-8')
        s.close()
        
        print(f"\n{GREEN}[+] Sunucudan Gelen HTTP Başlık Bilgileri:{RESET}\n")
        lines = yanit.split('\r\n')
        # İlk satır HTTP durum kodunu verir (Örn: HTTP/1.1 200 OK)
        print(f"{BOLD}{YELLOW}Durum Satırı: {lines[0]}{RESET}")
        print("-" * 40)
        for line in lines[1:]:
            if line: print(line)
            
    except Exception as e:
        print(f"{RED}[X] Web sunucusuna bağlanılamadı: {e}{RESET}")
        
    input(f"\n{CYAN}Ana menüye dönmek için Enter'a bas kanka...{RESET}")

# --- 3. MODÜL: GELİŞMİŞ HAM PAKET DETEKTÖRÜ (SNIFFER 2.0) ---
def gelismis_sniffer():
    print(f"\n{RED}[!] Gelişmiş Protokol Detektörü Aktif (Root Yetkisi Gerekir){RESET}")
    print(f"{YELLOW}[*] Ağ üzerinden geçen ilk 5 paket detaylıca çözümlenecektir...{RESET}\n")
    
    try:
        kendi_ip = socket.gethostbyname(socket.gethostname())
        # Tüm IP protokollerini dinleyecek ham bir soket açıyoruz
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sniffer.bind((kendi_ip, 0))
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        for i in range(5):
            ham_veri, adres = sniffer.recvfrom(65565)
            # IP paket başlığındaki (Header) 9. bayt protokol türünü söyler
            protokol_no = ham_veri[9]
            
            if protokol_no == 6: protokol_tipi = "TCP"
            elif protokol_no == 17: protokol_tipi = "UDP"
            elif protokol_no == 1: protokol_tipi = "ICMP (Ping)"
            else: protokol_tipi = f"Diğer ({protokol_no})"
            
            print(f"{GREEN}[PAKET {i+1}] Kaynak: {adres[0]} | Protokol: {protokol_tipi} | Boyut: {len(ham_veri)} Byte{RESET}")
            
    except PermissionError:
        print(f"{RED}[X] HATA: Ham paket yakalamak için ROOT/Yönetici yetkisi şarttır!{RESET}")
    except Exception as e:
        print(f"{RED}[X] Soket okuma hatası: {e}{RESET}")
        
    input(f"\n{CYAN}Ana menüye dönmek için Enter'a bas kanka...{RESET}")

# --- ESKİ SÜRÜMLERDEN ALINAN KORUNAN MODÜLLER ---
def subdomain_tarayici():
    hedef_domain = input("\nHedef Ana Domain (Örn: example.com): ").strip()
    populer_sub = ["www", "mail", "ftp", "admin", "api"]
    print(f"\n{YELLOW}[*] Alt alan adları sorgulanıyor...{RESET}")
    for sub in populer_sub:
        try:
            ip = socket.gethostbyname(f"{sub}.{hedef_domain}")
            print(f"{GREEN}[+] Aktif: {sub}.{hedef_domain} [{ip}]{RESET}")
        except socket.gaierror: pass
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

def sha256_sifreleyici():
    metin = input("\nHash alınacak metin: ").strip()
    sha256_ozet = hashlib.sha256(metin.encode('utf-8')).hexdigest()
    print(f"{GREEN}[+] SHA-256 Karşılığı: {sha256_ozet}{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

def etternetlog_zeka():
    print(f"\n{CYAN}[ Etternetlog v6.0 Yapay Zeka Motoru ]{RESET}")
    soru = input(f"{BLUE}Sorunuz kanka: {RESET}").lower().strip()
    if "threading" in soru or "hız" in soru: print(f"{GREEN}AI: Çoklu iş parçacığı (Threading), tarama işlemlerini işlemci çekirdeklerini eşzamanlı kullanarak hızlandırır.{RESET}")
    elif "header" in soru: print(f"{GREEN}AI: HTTP Başlıkları (Headers), sunucunun işletim sistemi ve yazılım versiyonu (Apache, Nginx vb.) hakkında bilgi toplamak için incelenir.{RESET}")
    else: print(f"{GREEN}AI: Bu teknik bir siber analiz konusudur. Gelişmiş menü modüllerini inceleyebilirsiniz.{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- ANA PROGRAM AKIŞI ---
def ana_menu():
    ekran_temizle()
    banner_goster()
    print(f"{GREEN}1.{RESET} Güçlendirilmiş Hızlı Port Tarayıcı (Multi-threaded Scanner)")
    print(f"{GREEN}2.{RESET} Web Sunucu Durum ve Bilgi Toplama Modülü (HTTP Header)")
    print(f"{GREEN}3.{RESET} Gelişmiş Protokol Detektörü (Sniffer 2.0)")
    print(f"{GREEN}4.{RESET} Halka Açık Subdomain Keşif Aracı (OSINT)")
    print(f"{GREEN}5.{RESET} Kriptografik SHA-256 Şifreleme Motoru")
    print(f"{GREEN}6.{RESET} Etternetlog v6.0 Siber Zeka Asistanı")
    print(f"{RED}0.{RESET} Çıkış\n")

def main():
    while True:
        ana_menu()
        secim = input(f"{BOLD}{RED}Etternetlog > {RESET}").strip()
        if secim == "1": hizli_port_tarayici()
        elif secim == "2": http_header_analiz()
        elif secim == "3": gelismis_sniffer()
        elif secim == "4": subdomain_tarayici()
        elif secim == "5": sha256_sifreleyici()
        elif secim == "6": etternetlog_zeka()
        elif secim == "0":
            print(f"\n{RED}[!] Güvende kalın kanka. Yazılım deftere hazır!{RESET}"); break
        else:
            print(f"\n{RED}[X] Geçersiz seçim!{RESET}"); time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
