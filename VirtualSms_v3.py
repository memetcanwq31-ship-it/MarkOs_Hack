#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║              VirtualMark v3.0 - ÜCRETSİZ                ║
║  Kendi Sanal SMS Sistemin - Hiçbir Ücret Yok           ║
║  Kaynak: sms24.me (Cloudflare'siz, ücretsiz)           ║
║                                                          ║
║  1) SMS Numarası Al & Kodları Gör                       ║
║  2) Kendi API Sunucunu Başlat (Arkadaşların da kullansın)║
║  3) Çıkış                                                ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import sys
import os
import time
import re
import json
import threading
from bs4 import BeautifulSoup

# ── RENKLER ──
K = "\033[91m"; Y = "\033[92m"; S = "\033[93m"
M = "\033[94m"; P = "\033[95m"; C = "\033[96m"
B = "\033[97m"; KL = "\033[1m"; SN = "\033[0m"

BASLIK = f"""
{KL}{C}
╔══════════════════════════════════════════════════════════╗
║           {Y}██╗   ██╗██╗██████╗ ████████╗{C}               ║
║           {Y}██║   ██║██║██╔══██╗╚══██╔══╝{C}               ║
║           {Y}██║   ██║██║██████╔╝   ██║   {C}               ║
║           {Y}╚██╗ ██╔╝██║██╔══██╗   ██║   {C}               ║
║           {Y} ╚████╔╝ ██║██║  ██║   ██║   {C}               ║
║           {Y}  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   {C}               ║
║          {S}⚡ Sanal SMS + Kod Alma Sistemi ⚡{C}            ║
║              {B}🔒 TAMAMEN ÜCRETSİZ - HERKESE AÇIK{C}        ║
║              {M}📡 Kaynak: sms24.me (10.000+ numara){C}       ║
╚══════════════════════════════════════════════════════════╝
{SN}"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Accept": "text/html,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}
OTURUM = requests.Session()
OTURUM.headers.update(HEADERS)

# ═══════════════════════════════════════════════════════
# BÖLÜM 1: sms24.me'DEN NUMARA ÇEK
# ═══════════════════════════════════════════════════════
def sms24_numaralari_al():
    """sms24.me'den tüm ülkelerden numaraları çek - TAMAMEN BEDAVA"""
    print(f"  {C}[~] sms24.me bağlanıyor...{SN}")
    
    # Anahtar: Ülke kodları (manuel liste - her zaman çalışır)
    ulkeler = {
        "tr": "Türkiye", "us": "Amerika", "gb": "İngiltere", "de": "Almanya",
        "fr": "Fransa", "nl": "Hollanda", "ru": "Rusya", "ua": "Ukrayna",
        "es": "İspanya", "it": "İtalya", "ca": "Kanada", "au": "Avustralya",
        "cn": "Çin", "jp": "Japonya", "kr": "G.Kore", "br": "Brezilya",
        "in": "Hindistan", "pl": "Polonya", "se": "İsveç", "no": "Norveç",
        "fi": "Finlandiya", "dk": "Danimarka", "be": "Belçika", "at": "Avusturya",
        "ch": "İsviçre", "za": "G.Afrika", "mx": "Meksika", "ar": "Arjantin"
    }
    
    tum_numaralar = []
    
    # Önce /en/numbers sayfasından en yeni 18 numarayı al
    try:
        r = OTURUM.get("https://sms24.me/en/numbers", timeout=20)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", class_="callout"):
                href = a.get("href", "")
                no = href.split("/")[-1]
                no = re.sub(r"\D", "", no)
                if no and len(no) >= 7:
                    tum_numaralar.append({
                        "orijinal": "+" + no,
                        "temiz": no,
                        "ulke": "En Yeni",
                        "kaynak": "sms24.me"
                    })
    except: pass
    
    # Her ülkeden numaraları al (ilk 2 sayfa)
    for kod, ad in ulkeler.items():
        for sayfa in [1, 2]:
            try:
                r = OTURUM.get(f"https://sms24.me/en/countries/{kod}/{sayfa}", timeout=15)
                if r.status_code != 200: break
                
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", class_="callout"):
                    href = a.get("href", "")
                    no = href.split("/")[-1]
                    no = re.sub(r"\D", "", no)
                    if no and len(no) >= 7:
                        tum_numaralar.append({
                            "orijinal": "+" + no,
                            "temiz": no,
                            "ulke": ad,
                            "kaynak": "sms24.me"
                        })
                
                # Pagination kontrol
                if not soup.find("ul", class_="pagination"): break
            except: break
    
    # Benzersiz yap
    gorulen = set()
    sonuc = []
    for n in tum_numaralar:
        if n["temiz"] not in gorulen:
            gorulen.add(n["temiz"])
            sonuc.append(n)
    
    return sonuc

# ═══════════════════════════════════════════════════════
# BÖLÜM 2: SMS MESAJLARINI AL (ÇALIŞAN YÖNTEM)
# ═══════════════════════════════════════════════════════
def sms_mesajlarini_al(numara_bilgi):
    """
    DOĞRU YÖNTEM: sms24.me/en/numbers/{NUMARA}
    Mesajlar <dd> elementi içinde
    """
    no = numara_bilgi["temiz"]
    
    try:
        r = OTURUM.get(f"https://sms24.me/en/numbers/{no}", timeout=20)
        if r.status_code != 200: return []
        
        soup = BeautifulSoup(r.text, "html.parser")
        mesajlar = []
        
        # <dd> elementleri = her bir SMS
        for dd in soup.find_all("dd"):
            a = dd.find("a")
            span = dd.find("span")
            
            if a and span:
                gonderen = a.get_text(strip=True)
                gonderen = gonderen.replace("From:", "").replace("Kaynak:", "").strip()
                mesaj = span.get_text(strip=True)
                
                if mesaj:
                    mesajlar.append({
                        "gonderen": gonderen or "Bilinmiyor",
                        "mesaj": mesaj
                    })
        
        return mesajlar
        
    except Exception as e:
        return []

# ═══════════════════════════════════════════════════════
# BÖLÜM 3: KENDİ API SUNUCUN (Arkadaşların da kullansın)
# ═══════════════════════════════════════════════════════
def api_sunucu_baslat(port=5555):
    """Termux'ta çalışan ücretsiz API sunucusu"""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
        
        class SMSAPI(BaseHTTPRequestHandler):
            def doget(self):
                path = urllib.parse.urlparse(self.path).path
                
                if path == "/" or path == "/numaralar":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    
                    nfis = sms24_numaralari_al()
                    # Sadece temiz liste
                    basit = []
                    for n in nfis[:50]:
                        basit.append({"numara": n["orijinal"], "ulke": n["ulke"]})
                    
                    self.wfile.write(json.dumps({
                        "sistem": "VirtualMark v3.0 - Ücretsiz SMS",
                        "toplam": len(nfis),
                        "numaralar": basit,
                        "kaynak": "sms24.me"
                    }, indent=2, ensure_ascii=False).encode())
                    
                elif path.startswith("/sms/"):
                    no = path.replace("/sms/", "").replace("/", "")
                    no = re.sub(r"\D", "", no)
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    
                    if no:
                        bilgi = {"temiz": no, "orijinal": "+"+no, "ulke": "API"}
                        mesajlar = sms_mesajlarini_al(bilgi)
                        
                        # Kodları ayıkla
                        for m in mesajlar:
                            kodlar = re.findall(r"\b(\d{4,8})\b", m["mesaj"])
                            m["kodlar"] = kodlar
                        
                        self.wfile.write(json.dumps({
                            "numara": "+" + no,
                            "mesaj_sayisi": len(mesajlar),
                            "mesajlar": mesajlar
                        }, indent=2, ensure_ascii=False).encode())
                    else:
                        self.wfile.write(json.dumps({"hata": "Numara gerekli"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"hata": "Bilinmeyen yol. Kullan: /numaralar veya /sms/NUMARA"}).encode())
            
            def do_GET(self):
                self.doget()
            
            def log_message(self, format, *args):
                pass  # Sessiz mod
        
        print(f"\n  {Y}[+] API Sunucusu başladı!{SN}")
        print(f"  {B}  ───────────────────────────────────{SN}")
        print(f"  {C}  📡 http://{_ip_al()}:{port}/numaralar{SN}")
        print(f"  {C}  📡 http://{_ip_al()}:{port}/sms/NUMARA{SN}")
        print(f"  {B}  ───────────────────────────────────{SN}")
        print(f"  {S}  🎯 Arkadaşların da kullanabilir!{SN}")
        print(f"  {B}  Aynı WiFi'daysalar IP'ni ver:{SN}")
        print(f"  {M}  http://{_ip_al()}:{port}/{SN}")
        print(f"  {B}  ───────────────────────────────────{SN}")
        print(f"  {K}  ❌ Durdurmak için Ctrl+C{SN}\n")
        
        sunucu = HTTPServer(("0.0.0.0", port), SMSAPI)
        sunucu.serve_forever()
        
    except ImportError:
        print(f"  {K}[HATA] Flask gerekli değil, standart http.server kullanılıyor...{SN}")
    except Exception as e:
        print(f"  {K}[HATA] Sunucu başlatılamadı: {e}{SN}")
        print(f"  {S}  Port 5555 dolu olabilir, farklı bir port dene.{SN}")

def _ip_al():
    """Yerel IP'yi bul"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ═══════════════════════════════════════════════════════
# BÖLÜM 4: EKRAN FONKSİYONLARI
# ═══════════════════════════════════════════════════════
def temizle(): os.system("clear" if os.name == "posix" else "cls")

def menuyu_goster():
    temizle()
    print(BASLIK)
    print(f"{KL}{C}╔{'═'*54}╗{SN}")
    print(f"{KL}{C}║{SN}  {S}[1]{B} 📱 SMS Numarası Al & Kodları Görüntüle       {C}║{SN}")
    print(f"{KL}{C}║{SN}  {S}[2]{B} 🌐 Kendi API Sunucunu Başlat (Herkes kullansın){C}║{SN}")
    print(f"{KL}{C}║{SN}  {K}[3]{B} 🚪 Çıkış                                   {C}║{SN}")
    print(f"{KL}{C}╚{'═'*54}╝{SN}")
    print(f"  {P}🔒 TAMAMEN ÜCRETSİZ • SMS24.ME KAYNAKLI{SN}")
    print()

def numaralari_goster(numaralar):
    if not numaralar:
        print(f"\n{K}[!] Hiç numara bulunamadı.{SN}")
        print(f"  {S}Termux'ta test et:{SN}")
        print(f"  {B}  1. {C}curl -s https://sms24.me/en/numbers | wc -c{SN}")
        print(f"  {B}  2. {C}pip install --upgrade requests beautifulsoup4{SN}")
        print(f"  {B}  3. Telefon saatini otomatik yap{SN}")
        return []

    ulkeler = {}
    for n in numaralar:
        u = n["ulke"]
        if u not in ulkeler: ulkeler[u] = []
        ulkeler[u].append(n)

    print(f"\n{KL}{Y}╔{'═'*54}╗{SN}")
    print(f"{KL}{Y}║{SN}  {M}🌍 MEVCUT SANAL NUMARALAR ({len(numaralar)} adet){M}           {Y}║{SN}")
    print(f"{KL}{Y}╚{'═'*54}╝{SN}\n")

    sayac = 1
    index = []
    
    for ulke in sorted(ulkeler.keys()):
        print(f"{KL}{S}► {ulke}{SN}")
        for n in ulkeler[ulke]:
            print(f"  {C}[{sayac:3d}]{SN} {Y}{n['orijinal']}{SN}")
            index.append(n)
            sayac += 1
            if sayac > 80: break
        print()
        if sayac > 80:
            print(f"  {S}... +{len(numaralar)-80} numara daha var{SN}\n")
            break
    
    return index

def smsleri_goster(mesajlar, numara_bilgi):
    temizle()
    print(f"\n{KL}{Y}╔{'═'*54}╗{SN}")
    print(f"{KL}{Y}║{SN}  {M}📨 NUMARA: {B}{numara_bilgi['orijinal']}{M} ({numara_bilgi['ulke']})         {Y}║{SN}")
    print(f"{KL}{Y}╚{'═'*54}╝{SN}\n")

    if not mesajlar:
        print(f"  {S}⚠ Bu numaraya henüz SMS gelmemiş.{SN}")
        print(f"  {B}  WhatsApp/Telegram/Instagram'da bu numarayı kullan,{SN}")
        print(f"  {B}  kod geldiğinde otomatik yakalayacağım.{SN}")
        print(f"  {B}  Her 5 saniyede kontrol ediyorum.{SN}")
        return False

    kodlar = []
    print(f"  {KL}{C}{'─'*50}{SN}")
    
    for i, m in enumerate(mesajlar[-10:], 1):  # Son 10 mesaj
        gnd = m.get("gonderen", "?")
        msj = m.get("mesaj", "")
        
        kod_bul = re.findall(r"\b(\d{4,8})\b", msj)
        vurgulu = msj
        for kod in kod_bul:
            vurgulu = vurgulu.replace(kod, f"{KL}{S}{kod}{SN}")
            if kod not in kodlar: kodlar.append(kod)

        print(f"  {M}[{i}]{SN}")
        print(f"  {B}  Gönderen: {C}{gnd}{SN}")
        print(f"  {B}  Mesaj   : {Y}{vurgulu}{SN}")
        print(f"  {C}{'─'*50}{SN}")

    if kodlar:
        print(f"\n  {KL}{Y}╔{'═'*50}╗{SN}")
        print(f"  {KL}{Y}║{SN}  {S}🔑 BULUNAN KODLAR:{S}                         {Y}║{SN}")
        for kod in kodlar:
            print(f"  {KL}{Y}║{SN}       {KL}{P}► {kod} ◄{P}{KL}                         {Y}║{SN}")
        print(f"  {KL}{Y}╚{'═'*50}╝{SN}")
    
    return True

# ═══════════════════════════════════════════════════════
# BÖLÜM 5: SMS İZLEME
# ═══════════════════════════════════════════════════════
def sms_izle(numara_bilgi):
    gorulen = set()
    ilk = True
    
    try:
        while True:
            mesajlar = sms_mesajlarini_al(numara_bilgi)
            
            if ilk:
                smsleri_goster(mesajlar, numara_bilgi)
                ilk = False
                if mesajlar:
                    print(f"\n  {Y}✅ {len(mesajlar)} SMS mesajı bulundu!{SN}")
                else:
                    print(f"\n  {S}⏳ SMS bekleniyor (5sn'de bir kontrol)...{SN}")
                    print(f"  {B}  Çıkış: {K}Ctrl+C{SN}")
            else:
                yeni = False
                for m in mesajlar:
                    h = f"{m.get('gonderen','')}|{m.get('mesaj','')}"
                    if h not in gorulen:
                        gorulen.add(h)
                        yeni = True
                
                if yeni:
                    temizle()
                    smsleri_goster(mesajlar, numara_bilgi)
                    print(f"\n  {Y}✅ Yeni SMS geldi!{SN}")
                else:
                    sys.stdout.write(f"\r  {C}[{time.strftime('%H:%M:%S')}]{SN} {S}Kontrol ediliyor...{SN}  ")
                    sys.stdout.flush()
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print(f"\n\n  {S}[!] Durdu.{SN}")
        input(f"  {B}ENTER'a bas...{SN}")

# ═══════════════════════════════════════════════════════
# BÖLÜM 6: ANA MENÜ
# ═══════════════════════════════════════════════════════
def ana_menu():
    while True:
        menuyu_goster()
        try:
            secim = input(f"  {KL}{Y}Seçim [1-3]: {SN}").strip()
        except: print(); sys.exit(0)
        
        if secim == "3":
            print(f"\n  {S}Görüşmek üzere! 🚀{SN}\n")
            sys.exit(0)
            
        elif secim == "2":
            print(f"\n  {C}[~] API sunucusu başlatılıyor...{SN}")
            print(f"  {S}  Port 5555 kullanılacak.{SN}")
            time.sleep(1)
            try:
                api_sunucu_baslat(5555)
            except KeyboardInterrupt:
                print(f"\n  {S}Sunucu durduruldu.{SN}")
                time.sleep(1)
                continue
            
        elif secim == "1":
            print(f"\n  {C}[~] sms24.me'den numaralar alınıyor...{SN}")
            print(f"  {S}  Bu işlem 15-25 saniye sürebilir...{SN}")
            
            numaralar = sms24_numaralari_al()
            
            temizle()
            print(BASLIK)
            index = numaralari_goster(numaralar)
            
            if not index:
                print(f"\n  {K}[!] Hiç numara gelmedi.{SN}")
                print(f"  {B}  Çözüm: {C}curl -s https://sms24.me/en/numbers | head -20{SN}")
                print(f"  {B}  Çalışıyorsa: {C}pip install --upgrade requests beautifulsoup4{SN}")
                input(f"\n  {B}ENTER...{SN}")
                continue
            
            try:
                s = input(f"\n  {KL}{M}Numara seç [1-{len(index)}]: {SN}").strip()
                if not s.isdigit() or int(s) < 1 or int(s) > len(index):
                    print(f"{K}[HATA] 1-{len(index)} arası gir!{SN}")
                    input(f"{B}ENTER...{SN}"); continue
                
                sec = index[int(s)-1]
                print(f"\n  {Y}✅ Seçilen: {KL}{sec['orijinal']}{SN} ({sec['ulke']}){SN}")
                print(f"  {C}[~] SMS'ler taranıyor...{SN}")
                time.sleep(1)
                
                try:
                    sms_izle(sec)
                except Exception as e:
                    print(f"\n  {K}[HATA] {e}{SN}")
                    input(f"{B}ENTER...{SN}")
            except: continue
        
        else:
            print(f"\n  {K}[HATA] 1, 2 veya 3 gir!{SN}")
            time.sleep(1.5)

# ═══════════════════════════════════════════════════════
# ÇALIŞTIR
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        ana_menu()
    except KeyboardInterrupt:
        print(f"\n  {S}Çıkılıyor...{SN}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{K}[KRİTİK] {e}{SN}")
        sys.exit(1)
