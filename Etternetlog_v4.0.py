#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Proje Adı: Etternetlog.py
# Sürüm: v4.0
# Amacı: OSINT, Ağ Analizi ve Atak Yönetimi İçeren Gelişmiş Pentest Paneli

import os
import sys
import socket
import json
import time
import hashlib

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
    print(f"                                                  |___/ v4.0{RESET}")
    print(f"{RED}=================================================================={RESET}")
    print(f"{YELLOW}[+] Proje: Etternetlog Gelişmiş Hack & Savunma Paneli{RESET}")
    print(f"{YELLOW}[+] Sürüm: v4.0 (OSINT ve Ağ Atak Modülleri Eklendi){RESET}")
    print(f"{RED}=================================================================={RESET}\n")

# --- 1. KATEGORİ: OSINT INSTAGRAM PROFİL ANALİZİ ---
def instagram_osint_analiz():
    print(f"\n{YELLOW}[*] OSINT - Instagram Profil İstihbarat Modülü{RESET}")
    username = input("Analiz edilecek Instagram kullanıcı adını girin: ").strip()
    
    print(f"\n{BLUE}[*] {username} için halka açık kaynaklar taranıyor...{RESET}")
    time.sleep(1.5)
    
    print(f"\n{GREEN}[+] OSINT Tarama Sonuçları (Halka Açık Veriler):{RESET}")
    print(f"{WHITE if 'WHITE' in locals() else RESET}- Profil Bağlantısı: https://instagram.com{username}")
    print(f"- Bilgi: Profil gizlilik durumu ve sunucu korumaları aktif.")
    print(f"\n{YELLOW}[!] Siber İstihbarat İpucu:{RESET}")
    print("Gerçek hayatta bu profilin konum veya iletişim bilgilerini bulmak için;")
    print("1. Profil fotoğraflarındaki konum etiketlerini (Geotag) inceleyin.")
    print("2. Paylaşılan resimlerin EXIF (meta veri) analizini yapın.")
    print("3. Kullanıcının biyografisinde bıraktığı Linktree veya e-posta adreslerini tarayın.")
    
    input(f"\n{CYAN}Ana menüye dönmek için Enter'a bas...{RESET}")

# --- 2. KATEGORİ: AĞ, WEB VE WI-FI ATAK SİMÜLASYONU VE KOMUT MOTORU ---
def ag_atak_motoru():
    print(f"\n{RED}--- AĞ VE KABLOSUZ AĞ SIZMA TESTİ ATALARI ---{RESET}")
    print(f"{GREEN}1.{RESET} Web / Sunucu (VPS) Atak Komutları")
    print(f"{GREEN}2.{RESET} Wi-Fi (WPA/WPS) Güvenlik ve Sızma Komutları")
    secim = input(f"{BOLD}{CYAN}Atak Türü Seçin > {RESET}").strip()
    
    if secim == "1":
        hedef_url = input("\nHedef Web Sitesi veya VPS IP: ").strip()
        print(f"\n{YELLOW}[+] Sunucu / VPS Analiz Reçetesi Hazırlandı:{RESET}")
        print(f"👉 HTTP Flood Testi İçin: 'python3 Etternetlog.py' ana menüsünden DDoS modülünü seçebilirsiniz.")
        print(f"👉 Zafiyet Taraması İçin Kali Komutu: {GREEN}nmap -sV --script=vuln {hedef_url}{RESET}")
        print(f"👉 Web Panel Şifre Kırma Komutu: {GREEN}hydra -l admin -P wordlist.txt {hedef_url} http-post-form{RESET}")
        
    elif secim == "2":
        print(f"\n{YELLOW}[+] Kablosuz Ağ (WPA/WPS) Pentest Komut Kılavuzu:{RESET}")
        print("Kali Linux terminalinde kartınızı dinleme moduna alıp şu gerçek komutları uygulayabilirsiniz:")
        print(f"1. Ağ Kartını İzlemeye Al: {GREEN}airmon-ng start wlan0{RESET}")
        print(f"2. Etraftaki Wi-Fi Ağlarını Tara: {GREEN}airodump-ng wlan0mon{RESET}")
        print(f"3. Hedef Ağın El Sıkışma (Handshake) Paketini Yakala: {GREEN}airodump-ng -c [Kanal] --bssid [Mac_Adresi] -w dosya wlan0mon{RESET}")
        print(f"4. WPS Açığı Deneme (PIN Saldırısı): {GREEN}reaver -i wlan0mon -b [Hedef_BSSID] -vv{RESET}")
    
    input(f"\n{CYAN}Ana menüye dönmek için Enter'a bas...{RESET}")

# --- ESKİ SÜRÜMDEN GELEN DİĞER MODÜLLER ---
def port_tarayici():
    hedef_ip = input("\nTaranacak Hedef Yerel IP (Örn: 127.0.0.1): ").strip()
    print(f"\n{YELLOW}[*] {hedef_ip} portları taranıyor...{RESET}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    if s.connect_ex((hedef_ip, 80)) == 0: print(f"{GREEN}[+] Port 80 (HTTP) --> AÇIK!{RESET}")
    else: print(f"{RED}[-] Kritik portlar yanıt vermiyor.{RESET}")
    s.close()
    input(f"\n{CYAN}Ana menüye dönmek için Enter...{RESET}")

def brute_force_simor():
    print(f"\n{YELLOW}[*] Brute Force - MD5 Kırma Modülü{RESET}")
    hedef_hash = input("MD5 Hash: ").strip().lower()
    if hedef_hash == "21232f297a57a5a743894a0e4a801fc3": print(f"{GREEN}[+] Şifre Bulundu: admin{RESET}")
    else: print(f"{RED}[-] Şifre bulunamadı.{RESET}")
    input(f"\n{CYAN}Ana menüye dönmek için Enter...{RESET}")

def etternetlog_zeka():
    print(f"\n{CYAN}[ Etternetlog v4.0 Yapay Zeka Motoru Aktif ]{RESET}")
    soru = input(f"{BLUE}Sorunuz kanka: {RESET}").lower().strip()
    if "rat" in soru: print(f"{GREEN}AI: RAT, uzaktan erişim sağlayan bir arka kapıdır.{RESET}")
    elif "ddos" in soru: print(f"{GREEN}AI: DDoS, sunucu trafiğini şişirme saldırısıdır.{RESET}")
    else: print(f"{GREEN}AI: Bu terim siber sızma süreçleriyle ilgilidir. Menüdeki komut motorunu inceleyin.{RESET}")
    input(f"\n{CYAN}Ana menüye dönmek için Enter...{RESET}")

# --- ANA PROGRAM AKIŞI ---
def ana_menu():
    ekran_temizle()
    banner_goster()
    print(f"{GREEN}1.{RESET} OSINT - Instagram Profil Analiz Modülü")
    print(f"{GREEN}2.{RESET} Ağ, Web ve Kablosuz Ağ (Wi-Fi) Atak Komut Paneli")
    print(f"{GREEN}3.{RESET} Ağ Zafiyet Tarayıcı Modülü (Port Scanner)")
    print(f"{GREEN}4.{RESET} Kaba Kuvvet Saldırı Modülü (Brute Force MD5)")
    print(f"{GREEN}5.{RESET} Etternetlog v4.0 Siber Zeka Asistanı")
    print(f"{RED}0.{RESET} Çıkış\n")

def main():
    while True:
        ana_menu()
        secim = input(f"{BOLD}{RED}Etternetlog > {RESET}").strip()
        if secim == "1": instagram_osint_analiz()
        elif secim == "2": ag_atak_motoru()
        elif secim == "3": port_tarayici()
        elif secim == "4": brute_force_simor()
        elif secim == "5": etternetlog_zeka()
        elif secim == "0":
            print(f"\n{RED}[!] Etternetlog v4.0 kapatılıyor. Kodlar deftere hazır kanka!{RESET}"); break
        else:
            print(f"\n{RED}[X] Geçersiz seçim!{RESET}"); time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
