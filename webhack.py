import os
import sys
import time
from colorama import Fore, Style, init
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# ANSI Renk İlklendirmesi
init(autoreset=True)

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
WHITE = Fore.WHITE

# ==========================================
# MARKOS RESMİ DEFACEMENT HTML İNDEKSİ
# ==========================================
HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Belsis.site</title>
    <style>
        body { 
            background-color: #050505; 
            color: #ff0000; 
            font-family: 'Courier New', monospace; 
            text-align: center; 
            padding-top: 12%; 
        }
        h1 { font-size: 55px; text-shadow: 0px 0px 20px #ff0000; animation: blink 1.2s infinite; }
        .logo-sub { color: #00ffff; font-size: 24px; text-shadow: 0px 0px 10px #00ffff; font-weight: bold; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <h1>🏴‍☠️ MarkOs El Koydu 🏴‍☠️</h1>
    <p class="logo-sub">MARKOS PRIVATE CYBER OS & SECURITY SYSTEM</p>
    <p style="color: white; font-size: 18px;">Bu web sistemi siber güvenlik denetiminden geçirilmiştir.</p>
    <p style="color: #444; margin-top: 40px;">Sürüm: 2026.1.7.0 — Global Tehdit İstihbarat Ağı</p>
</body>
</html>
"""

class MarkOsZeroErrorEngine:
    def __init__(self):
        self.hedef_site = ""
        # Root yetkisi istememesi için portu standart dışı (8080) yapıyoruz
        self.port = 8080 

    def temizle(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def sunucu_altyapisini_hazirla(self):
        """Geçici sunucu klasörünü ve indeks dosyasını sıfır hatayla hazırlar."""
        dizin = "markos_proxy_server"
        if not os.path.exists(dizin):
            os.makedirs(dizin)
        
        with open(os.path.join(dizin, "index.html"), "w", encoding="utf-8") as f:
            f.write(HTML_CONTENT)
        
        # Sunucu dizinine geçiş yapıyoruz
        os.chdir(dizin)

    def baslat(self):
        self.temizle()
        print(f"{RED}=========================================================================")
        print(f"{RED}    MARKOS HYBRID PROXY & WEB DEFACEMENT ENGINE v3.4                    ")
        print(f"{RED}=========================================================================")
        print(f"{GREEN}[+] Durum: Dosya Sisteminden Bağımsız Katman Aktif (Sıfır Hata Modu)")
        
        self.hedef_site = input(f"\nHack şovu yapacağın web sitesini gir (Örn: instagram.com): {WHITE}").strip()
        if not self.hedef_site:
            print(f"{RED}[─] Geçersiz domain girdiniz.")
            return

        clean_domain = self.hedef_site.replace("http://", "").replace("https://", "").replace("www.", "").strip("/")
        
        # Sunucu dosyalarını hazırlıyoruz
        self.sunucu_altyapisini_hazirla()

        # Port çakışmalarını önlemek için soket ayarı
        TCPServer.allow_reuse_address = True
        
        try:
            with TCPServer(("", self.port), SimpleHTTPRequestHandler) as httpd:
                print(f"\n{GREEN}[🔥] MARKOS INTERACTIVE PROXY SERVER ONLINE (PORT {self.port})")
                print(f"{CYAN}[*] Hedef Ağ Filtresi: {clean_domain}")
                print(f"─" * 73)
                print(f"{YELLOW}[💡] ŞOVU BAŞLATMAK İÇİN ŞU ADIMI YAPIN:")
                print(f"     Tarayıcınızda veya Cihazınızda şu adrese gidin:")
                print(f"     {Fore.WHITE}http://localhost:{self.port} VEYA http://127.0.0.1:{self.port}")
                print(f"     {YELLOW}Böylece '{clean_domain}' yerine doğrudan MarkOs panonuz ekrana basılır!")
                print(f"─" * 73)
                print(f"{RED}[*] Sunucuyu kapatmak için CTRL+C tuşlarına basın...\n")
                httpd.serve_forever()
                
        except Exception as e:
            print(f"{RED}[─] Sunucu Başlatma Hatası: {e}")

if __name__ == "__main__":
    try:
        motor = MarkOsZeroErrorEngine()
        motor.baslat()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[*] Operasyon güvenli şekilde sonlandırıldı, babus.")
        sys.exit(0)
