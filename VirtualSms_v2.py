#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║                VirtualMark v2.2 (FİNAL)                  ║
║  Sanal SMS Numarası + Kod Alma Aracı                     ║
║  Kaynak: sms24.me (Cloudflare'siz, hızlı, güvenilir)    ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import sys
import os
import time
import re
from bs4 import BeautifulSoup

# ── RENKLER ──
KIRMIZI = "\033[91m"; YESIL = "\033[92m"; SARI = "\033[93m"
MAVI = "\033[94m"; MOR = "\033[95m"; CYAN = "\033[96m"
BEYAZ = "\033[97m"; KALIN = "\033[1m"; SON = "\033[0m"

BASLIK = f"""
{KALIN}{CYAN}
╔══════════════════════════════════════════════════════════╗
║              {YESIL}█▀█ █ █ █▀█ █ █ █ █▀█ █▀▀ █ █▀▄▀█ █ ▄▀█ █▄▄ █▄▀{CYAN}     ║
║              {YESIL}█▀▀ █▄█ █▀▄ █▄█ █ █▀▀ █ █ █ █ █ █ █ █▄▀ █▄█ █ {CYAN}║
║          {SARI}⚡ Virtual SMS Number + Kod Alma Aracı ⚡{CYAN}          ║
║              {BEYAZ}🔒 Kaynak: sms24.me • 10.000+ Numara{BEYAZ}{CYAN}     ║
╚══════════════════════════════════════════════════════════╝
{SON}"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Upgrade-Insecure-Requests": "1",
}
OTURUM = requests.Session()
OTURUM.headers.update(HEADERS)

# ══════════════════════════════════════════════════════
# 1. ÜLKE KODLARINI AL
# ══════════════════════════════════════════════════════
def ulke_kodlarini_al():
    """sms24.me ülke listesinden tüm ülke kodlarını döndürür."""
    try:
        resp = OTURUM.get("https://sms24.me/en/countries", timeout=20)
        if resp.status_code != 200: return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        kodlar = []
        
        for a in soup.find_all("a", class_="callout"):
            href = a.get("href", "")
            # href formatı: /en/countries/us
            parcalar = href.split("/")
            for p in parcalar:
                if len(p) == 2 and p.isalpha():
                    kodlar.append(p)
                    break
        
        return kodlar
    except Exception as e:
        print(f"  {KIRMIZI}[HATA] Ülke listesi alınamadı: {e}{SON}")
        return []

# ══════════════════════════════════════════════════════
# 2. ÜLKEYE GÖRE NUMARA LİSTESİ
# ══════════════════════════════════════════════════════
def ulke_numaralari(ulke_kodu, ulke_adi="", max_sayfa=2):
    """Belirli bir ülkedeki tüm telefon numaralarını döndürür."""
    numaralar = []
    
    for sayfa in range(1, max_sayfa + 1):
        url = f"https://sms24.me/en/countries/{ulke_kodu}/{sayfa}"
        try:
            resp = OTURUM.get(url, timeout=20)
            if resp.status_code != 200: break
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            for a in soup.find_all("a", class_="callout"):
                href = a.get("href", "")
                # href formatı: /en/numbers/12025550123
                numara_temiz = href.split("/")[-1]
                numara_temiz = re.sub(r"\D", "", numara_temiz)
                
                if numara_temiz and len(numara_temiz) >= 7:
                    numaralar.append({
                        "orijinal": "+" + numara_temiz,
                        "temiz": numara_temiz,
                        "ulke": ulke_adi or ulke_kodu.upper(),
                        "kaynak": "sms24.me"
                    })
            
            # Son sayfa mı kontrol et
            pagination = soup.find("ul", class_="pagination")
            if not pagination: break
            
        except Exception:
            break
    
    return numaralar

# ══════════════════════════════════════════════════════
# 3. TÜM NUMARALARI AL (Ana fonksiyon)
# ══════════════════════════════════════════════════════
def numara_listesini_al():
    """Tüm ülkelerden numaraları topla."""
    print(f"  {CYAN}[~] sms24.me'ye bağlanılıyor...{SON}")
    
    # Öncelikli ülkeler (Türkiye ilk sırada)
    oncelikli = {
        "tr": "Türkiye", "us": "United States", "gb": "United Kingdom",
        "de": "Germany", "fr": "France", "nl": "Netherlands",
        "ru": "Russia", "ua": "Ukraine", "es": "Spain", "it": "Italy"
    }
    
    tumu = []
    
    # Önce ülke kodlarını al
    ulkeler = ulke_kodlarini_al()
    
    if not ulkeler:
        # Manuel yedek liste
        ulkeler = list(oncelikli.keys())
    
    print(f"  {YESIL}[+] {len(ulkeler)} ülke bulundu, numaralar taranıyor...{SON}")
    
    # Önce öncelikli ülkeleri tara
    for kod, ad in oncelikli.items():
        if kod in ulkeler:
            nfis = ulke_numaralari(kod, ad, max_sayfa=1)
            tumu.extend(nfis)
            print(f"  {MAVI}[{len(nfis):3d}] {ad}{SON}")
    
    # Kalan ülkeler (en fazla 5 tane daha)
    eklenen = 0
    for kod in ulkeler:
        if kod not in oncelikli and eklenen < 5:
            nfis = ulke_numaralari(kod, kod.upper(), max_sayfa=1)
            if nfis:
                tumu.extend(nfis)
                eklenen += 1
                print(f"  {MAVI}[{len(nfis):3d}] {kod.upper()}{SON}")
    
    # Ayrıca /en/numbers sayfasından en yeni numaralar
    try:
        resp = OTURUM.get("https://sms24.me/en/numbers", timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", class_="callout"):
                href = a.get("href", "")
                numara_temiz = href.split("/")[-1]
                numara_temiz = re.sub(r"\D", "", numara_temiz)
                if numara_temiz and len(numara_temiz) >= 7:
                    if not any(n["temiz"] == numara_temiz for n in tumu):
                        tumu.append({
                            "orijinal": "+" + numara_temiz,
                            "temiz": numara_temiz,
                            "ulke": "Çeşitli",
                            "kaynak": "sms24.me"
                        })
    except Exception:
        pass
    
    print(f"\n  {YESIL}[+] Toplam {len(tumu)} numara bulundu!{SON}")
    return tumu

# ══════════════════════════════════════════════════════
# 4. SMS MESAJLARINI AL (Düzeltilmiş versiyon!)
# ══════════════════════════════════════════════════════
def sms_mesajlarini_al(numara_bilgi):
    """
    Bir numaraya gelen SMS'leri al.
    URL: https://sms24.me/en/numbers/{numara}
    Mesajlar <dd> elementi içinde.
    """
    numara_temiz = numara_bilgi["temiz"]
    url = f"https://sms24.me/en/numbers/{numara_temiz}"
    
    try:
        resp = OTURUM.get(url, timeout=20)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        mesajlar = []
        
        # <dd> elementlerindeki mesajları al (makaledeki yöntem)
        for dd in soup.find_all("dd"):
            # Gönderen: <a> içinde "From: NUMARA"
            a_tag = dd.find("a")
            if not a_tag:
                continue
            
            sender_text = a_tag.get_text(strip=True)
            gonderen = sender_text.replace("From:", "").replace("Gönderen:", "").strip()
            
            # Mesaj: <span> içinde
            span_tag = dd.find("span")
            mesaj_text = span_tag.get_text(strip=True) if span_tag else dd.get_text(strip=True)
            
            if mesaj_text and len(mesaj_text) > 1:
                mesajlar.append({
                    "gonderen": gonderen or "Bilinmiyor",
                    "mesaj": mesaj_text,
                    "zaman": ""
                })
        
        return mesajlar
        
    except Exception as e:
        print(f"\n  {KIRMIZI}[HATA] SMS alınamadı: {e}{SON}")
        return []

# ══════════════════════════════════════════════════════
# 5. EKRAN FONKSİYONLARI
# ══════════════════════════════════════════════════════
def temizle(): os.system("clear" if os.name == "posix" else "cls")

def menuyu_goster():
    temizle()
    print(BASLIK)
    print(f"{KALIN}{CYAN}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{CYAN}║{SON}  {SARI}[1]{BEYAZ} 📱 SMS Numarası Al & Kodları Görüntüle       {CYAN}║{SON}")
    print(f"{KALIN}{CYAN}║{SON}  {KIRMIZI}[2]{BEYAZ} 🚪 Çıkış                                   {CYAN}║{SON}")
    print(f"{KALIN}{CYAN}╚{'═'*54}╝{SON}")
    print()

def numaralari_goster(numaralar):
    if not numaralar:
        print(f"\n{KIRMIZI}[!] Hiç numara bulunamadı!{SON}")
        print(f"  {SARI}Termux'ta şunları dene:{SON}")
        print(f"  {BEYAZ}  1. {CYAN}curl -v https://sms24.me{SON}{BEYAZ} (bağlantı testi){SON}")
        print(f"  {BEYAZ}  2. {CYAN}pip install --upgrade requests beautifulsoup4{SON}")
        print(f"  {BEYAZ}  3. VPN kullanıyorsan kapat{SON}")
        print(f"  {BEYAZ}  4. Telefonun saatini doğrula (otomatik saat){SON}")
        return []

    ulkeler = {}
    for n in numaralar:
        u = n["ulke"]
        if u not in ulkeler: ulkeler[u] = []
        ulkeler[u].append(n)

    print(f"\n{KALIN}{YESIL}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{YESIL}║{SON}  {MAVI}🌍 MEVCUT NUMARALAR ({len(numaralar)} adet){MAVI}                 {YESIL}║{SON}")
    print(f"{KALIN}{YESIL}╚{'═'*54}╝{SON}\n")

    sayac = 1
    index = []
    
    for ulke in sorted(ulkeler.keys()):
        print(f"{KALIN}{SARI}► {ulke.upper()}{SON}")
        for n in ulkeler[ulke]:
            print(f"  {CYAN}[{sayac:3d}]{SON} {YESIL}{n['orijinal']}{SON}")
            index.append(n)
            sayac += 1
            if sayac > 100:  # Maks 100 numara
                break
        print()
        if sayac > 100:
            print(f"  {SARI}... ve daha fazlası (toplam {len(numaralar)} numara){SON}\n")
            break
    
    return index

def smsleri_goster(mesajlar, numara_bilgi):
    temizle()
    print(f"\n{KALIN}{YESIL}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{YESIL}║{SON}  {MAVI}📨 NUMARA: {BEYAZ}{numara_bilgi['orijinal']}{MAVI} ({numara_bilgi['ulke']})           {YESIL}║{SON}")
    print(f"{KALIN}{YESIL}╚{'═'*54}╝{SON}\n")

    if not mesajlar:
        print(f"  {SARI}⚠ Henüz SMS alınmamış.{SON}")
        print(f"  {BEYAZ}  Bu numarayı bir platforma (WhatsApp, Telegram, Instagram vb.){SON}")
        print(f"  {BEYAZ}  kaydedip kod göndermesini bekle. Otomatik kontrol çalışıyor...{SON}")
        return False

    kodlar = []
    print(f"  {KALIN}{CYAN}{'─'*50}{SON}")
    
    for i, m in enumerate(mesajlar, 1):
        gonderen = m.get("gonderen", "Bilinmiyor")
        mesaj    = m.get("mesaj", "")
        
        kod_bul = re.findall(r"\b(\d{4,8})\b", mesaj)
        kod_vurgulu = mesaj
        for kod in kod_bul:
            kod_vurgulu = kod_vurgulu.replace(kod, f"{KALIN}{SARI}{kod}{SON}")
            if kod not in kodlar: kodlar.append(kod)

        print(f"  {MAVI}[{i}]{SON}")
        print(f"  {BEYAZ}  Gönderen: {CYAN}{gonderen}{SON}")
        print(f"  {BEYAZ}  Mesaj   : {YESIL}{kod_vurgulu}{SON}")
        print(f"  {CYAN}{'─'*50}{SON}")

    if kodlar:
        print(f"\n  {KALIN}{YESIL}╔{'═'*50}╗{SON}")
        print(f"  {KALIN}{YESIL}║{SON}  {SARI}🔑 BULUNAN DOĞRULAMA KODLARI:{SARI}               {YESIL}║{SON}")
        for kod in kodlar:
            print(f"  {KALIN}{YESIL}║{SON}        {KALIN}{MOR}  {kod}  {MOR}{KALIN}                             {YESIL}║{SON}")
        print(f"  {KALIN}{YESIL}╚{'═'*50}╝{SON}")

    return True

# ══════════════════════════════════════════════════════
# 6. SMS İZLEME DÖNGÜSÜ
# ══════════════════════════════════════════════════════
def sms_izleme_dongusu(numara_bilgi):
    gorulen = set()
    ilk = True
    
    try:
        while True:
            mesajlar = sms_mesajlarini_al(numara_bilgi)
            
            if ilk:
                smsleri_goster(mesajlar, numara_bilgi)
                ilk = False
                if mesajlar:
                    print(f"\n  {YESIL}✅ {len(mesajlar)} SMS bulundu!{SON}")
                else:
                    print(f"\n  {SARI}⏳ SMS bekleniyor (5sn'de bir kontrol)...{SON}")
                    print(f"  {BEYAZ}  Çıkmak için {KIRMIZI}Ctrl+C{SON}{BEYAZ} bas.{SON}")
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
                    print(f"\n  {YESIL}✅ Yeni SMS!{SON}")
                else:
                    sys.stdout.write(f"\r  {CYAN}[{time.strftime('%H:%M:%S')}]{SON} {SARI}Kontrol ediliyor...{SON}  ")
                    sys.stdout.flush()
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print(f"\n\n  {SARI}[!] Durduruldu.{SON}")
        input(f"  {BEYAZ}ENTER'a bas...{SON}")

# ══════════════════════════════════════════════════════
# 7. ANA MENÜ
# ══════════════════════════════════════════════════════
def ana_menu():
    while True:
        menuyu_goster()
        try:
            secim = input(f"  {KALIN}{YESIL}Seçim [1-2]: {SON}").strip()
        except (EOFError, KeyboardInterrupt):
            print(); sys.exit(0)
        
        if secim == "2":
            print(f"\n  {SARI}Görüşmek üzere!{SON}\n")
            sys.exit(0)
        elif secim == "1":
            print(f"\n  {CYAN}[~] Numaralar yükleniyor (10-20 saniye)...{SON}")
            numaralar = numara_listesini_al()
            
            temizle()
            print(BASLIK)
            index = numaralari_goster(numaralar)
            
            if not index:
                print(f"\n  {KIRMIZI}[!] Hiç numara alınamadı.{SON}")
                print(f"  {BEYAZ}  Termux'ta test etmek için:{SON}")
                print(f"  {BEYAZ}  {CYAN}curl -s https://sms24.me/en/numbers | head -50{SON}")
                input(f"\n  {BEYAZ}ENTER...{SON}")
                continue
            
            try:
                s = input(f"\n  {KALIN}{MAVI}Numara [1-{len(index)}]: {SON}").strip()
                if not s.isdigit() or int(s) < 1 or int(s) > len(index):
                    print(f"{KIRMIZI}[HATA] 1-{len(index)} arası gir!{SON}")
                    input(f"{BEYAZ}ENTER...{SON}"); continue
                
                sec = index[int(s) - 1]
                print(f"\n  {YESIL}✅ {sec['orijinal']} ({sec['ulke']}){SON}")
                print(f"  {CYAN}[~] SMS kontrolü...{SON}")
                time.sleep(1)
                
                try:
                    sms_izleme_dongusu(sec)
                except Exception as e:
                    print(f"\n  {KIRMIZI}[HATA] {e}{SON}")
                    input(f"{BEYAZ}ENTER...{SON}")
            except (EOFError, KeyboardInterrupt):
                continue
        else:
            print(f"\n  {KIRMIZI}[HATA] 1 veya 2 gir!{SON}")
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        ana_menu()
    except KeyboardInterrupt:
        print(f"\n  {SARI}Çıkılıyor...{SON}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{KIRMIZI}[HATA] {e}{SON}")
        sys.exit(1)
