#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║                VirtualMark v2.1                          ║
║  Sanal SMS Numarası + Kod Alma Aracı                     ║
║  Çoklu Kaynak Destekli (sms24.me + receive-smss.com)     ║
║  Termux + Python3 Uyumlu                                 ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import sys
import os
import time
import re
import json
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────────────
# RENKLER (Termux için)
# ──────────────────────────────────────────────────────
KIRMIZI    = "\033[91m"
YESIL      = "\033[92m"
SARI       = "\033[93m"
MAVI       = "\033[94m"
MOR        = "\033[95m"
CYAN       = "\033[96m"
BEYAZ      = "\033[97m"
KALIN      = "\033[1m"
SON        = "\033[0m"

# ──────────────────────────────────────────────────────
# BAŞLIK
# ──────────────────────────────────────────────────────
BASLIK = f"""
{KALIN}{CYAN}
╔══════════════════════════════════════════════════════════╗
║              {YESIL}█▀█ █ █ █▀█ █ █ █ █▀█ █▀▀ █ █▀▄▀█ █ ▄▀█ █▄▄ █▄▀{CYAN}     ║
║              {YESIL}█▀▀ █▄█ █▀▄ █▄█ █ █▀▀ █ █ █ █ █ █ █ █▄▀ █▄█ █ {CYAN}║
║                                                          ║
║          {SARI}⚡ Virtual SMS Number + Kod Alma Aracı ⚡{CYAN}          ║
║              {BEYAZ}🔒 100% Ücretsiz • Gerçek Numaralar{BEYAZ}{CYAN}        ║
║              {MAVI}📡 Çoklu Kaynak (sms24.me + yedek){MAVI}{CYAN}         ║
╚══════════════════════════════════════════════════════════╝
{SON}"""

# ──────────────────────────────────────────────────────
# HEADERS (Gerçek mobil tarayıcı taklidi)
# ──────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
}

OTURUM = requests.Session()
OTURUM.headers.update(HEADERS)


# ══════════════════════════════════════════════════════
# KAYNAK 1: sms24.me (Ana kaynak - daha az korumalı)
# ══════════════════════════════════════════════════════
def sms24_numara_listesi():
    """sms24.me sitesinden tüm ülkelerdeki numaraları çek."""
    print(f"  {CYAN}[~] sms24.me üzerinden numaralar alınıyor...{SON}")
    tum_numaralar = []
    
    # Önce ülke listesini al
    try:
        resp = OTURUM.get("https://sms24.me/en/countries", timeout=30)
        if resp.status_code != 200:
            print(f"  {SARI}[!] sms24.me ülke sayfasına erişilemedi (HTTP {resp.status_code}){SON}")
            return []
        
        # Ülke linklerini bul (.callout class veya a[href*="/en/countries/"] )
        soup = BeautifulSoup(resp.text, "html.parser")
        
        ulke_linkleri = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if re.match(r"^/en/countries/[a-z]{2}$", href):
                ulke_kodu = href.split("/")[-1]
                ulke_adi = a.get_text(strip=True)
                # Sayıyı temizle (başında olabilir)
                ulke_adi = re.sub(r'^\d+\s*', '', ulke_adi).strip()
                if ulke_kodu not in [u["kod"] for u in ulke_linkleri]:
                    ulke_linkleri.append({"kod": ulke_kodu, "adi": ulke_adi, "href": href})
        
        if not ulke_linkleri:
            # Alternatif: tüm linkleri tara
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "countries" in href and len(href.split("/")) >= 4:
                    ulke_kodu = href.split("/")[-1]
                    if len(ulke_kodu) == 2 and ulke_kodu.isalpha():
                        ulke_adi = a.get_text(strip=True)
                        ulke_adi = re.sub(r'^\d+\s*', '', ulke_adi).strip()
                        if ulke_kodu not in [u["kod"] for u in ulke_linkleri]:
                            ulke_linkleri.append({"kod": ulke_kodu, "adi": ulke_adi, "href": href})
        
        print(f"  {YESIL}[+] {len(ulke_linkleri)} ülke bulundu, numaralar alınıyor...{SON}")
        
        # Her ülke için numaraları çek (ilk 10 ülke + Türkiye)
        oncelikli_ulkeler = ["tr", "us", "gb", "de", "fr", "nl", "ru", "ua", "es", "it"]
        
        for ulke in ulke_linkleri:
            if ulke["kod"] not in oncelikli_ulkeler and len(tum_numaralar) > 50:
                continue
            
            try:
                ulke_url = f"https://sms24.me/en/countries/{ulke['kod']}"
                ulke_resp = OTURUM.get(ulke_url, timeout=20)
                if ulke_resp.status_code != 200:
                    continue
                
                ulke_soup = BeautifulSoup(ulke_resp.text, "html.parser")
                
                # callout class'ındaki linklerden numaraları al
                for a in ulke_soup.find_all("a", class_="callout"):
                    href = a.get("href", "")
                    numara_ham = a.get_text(strip=True)
                    
                    # Link'ten numarayı çıkar (örn: /en/messages/12025550123)
                    numara_temiz = ""
                    if "/messages/" in href:
                        numara_temiz = href.split("/messages/")[-1].split("/")[0]
                        numara_temiz = re.sub(r"\D", "", numara_temiz)
                    
                    # Eğer link'ten çıkmazsa metinden al
                    if not numara_temiz:
                        numara_temiz = re.sub(r"\D", "", numara_ham)
                    
                    if numara_temiz and len(numara_temiz) >= 7:
                        tum_numaralar.append({
                            "orijinal": "+" + numara_temiz,
                            "temiz": numara_temiz,
                            "ulke": ulke["adi"],
                            "kaynak": "sms24.me"
                        })
            except Exception:
                continue
        
        # Ayrıca /en/numbers sayfasından da al
        try:
            num_resp = OTURUM.get("https://sms24.me/en/numbers", timeout=20)
            if num_resp.status_code == 200:
                num_soup = BeautifulSoup(num_resp.text, "html.parser")
                for a in num_soup.find_all("a", class_="callout"):
                    href = a.get("href", "")
                    numara_temiz = ""
                    if "/messages/" in href:
                        numara_temiz = href.split("/messages/")[-1].split("/")[0]
                        numara_temiz = re.sub(r"\D", "", numara_temiz)
                    
                    if numara_temiz and len(numara_temiz) >= 7:
                        # Dublicate kontrol
                        if not any(n["temiz"] == numara_temiz for n in tum_numaralar):
                            tum_numaralar.append({
                                "orijinal": "+" + numara_temiz,
                                "temiz": numara_temiz,
                                "ulke": "Çeşitli",
                                "kaynak": "sms24.me"
                            })
        except Exception:
            pass
        
    except Exception as e:
        print(f"  {KIRMIZI}[HATA] sms24.me bağlantı hatası: {e}{SON}")
    
    return tum_numaralar


# ══════════════════════════════════════════════════════
# KAYNAK 2: receive-smss.com alternatif (URL bazlı)
# ══════════════════════════════════════════════════════
def receive_smss_numara_listesi():
    """receive-smss.com'dan alternatif yöntemle numara çek."""
    print(f"  {CYAN}[~] receive-smss.com üzerinden numaralar alınıyor...{SON}")
    numaralar = []
    
    try:
        # Önce inaktif-sayfasını dene (orada link yapısı daha net)
        resp = OTURUM.get("https://receive-smss.com/inactive-numbers/", timeout=30)
        
        if resp.status_code != 200:
            print(f"  {SARI}[!] receive-smss.com erişilemedi (HTTP {resp.status_code}){SON}")
            return []
        
        # Cloudflare kontrolü
        if "Cloudflare" in resp.text or "cf-challenge" in resp.text or "cf-browser-verification" in resp.text:
            print(f"  {SARI}[!] receive-smss.com Cloudflare koruması var, atlanıyor...{SON}")
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Link yapısı: /sms/NUMARA/ şeklindeki linkleri bul
        for link in soup.find_all("a", href=True):
            href = link["href"]
            match = re.search(r"/sms/(\d+)/?$", href)
            if match:
                numara_temiz = match.group(1)
                
                # Ülke adını bul
                ulke_adi = "Bilinmiyor"
                
                # Bayrak resmi varsa alt attribute'ünden al
                img = link.find("img")
                if img and img.get("alt"):
                    ulke_adi = img["alt"]
                
                # Link metninden ülkeyi çıkar
                link_text = link.get_text(strip=True)
                ulke_bul = re.search(r"\d+\s+(.*)", link_text)
                if ulke_bul and not ulke_bul.group(1).isdigit():
                    ulke_adi = ulke_bul.group(1).strip()
                
                if numara_temiz and len(numara_temiz) >= 7:
                    numaralar.append({
                        "orijinal": "+" + numara_temiz,
                        "temiz": numara_temiz,
                        "ulke": ulke_adi,
                        "kaynak": "receive-smss.com"
                    })
        
        print(f"  {YESIL}[+] receive-smss.com'dan {len(numaralar)} numara alındı{SON}")
        
    except Exception as e:
        print(f"  {KIRMIZI}[HATA] receive-smss.com: {e}{SON}")
    
    return numaralar


# ══════════════════════════════════════════════════════
# ANA NUMARA ALMA FONKSİYONU (Çoklu kaynak)
# ══════════════════════════════════════════════════════
def numara_listesini_al():
    """Tüm kaynaklardan numara topla."""
    tumu = []
    
    # Kaynak 1: sms24.me
    sms24 = sms24_numara_listesi()
    tumu.extend(sms24)
    
    # Kaynak 2: receive-smss.com
    if len(tumu) < 5:
        receive = receive_smss_numara_listesi()
        tumu.extend(receive)
    
    # Dublicate'leri temizle
    gorulen = set()
    benzersiz = []
    for n in tumu:
        if n["temiz"] not in gorulen:
            gorulen.add(n["temiz"])
            benzersiz.append(n)
    
    return benzersiz


# ══════════════════════════════════════════════════════
# SMS24.ME ÜZERİNDEN SMS MESAJLARINI ÇEK
# ══════════════════════════════════════════════════════
def sms24_mesajlari_al(numara_temiz):
    """sms24.me'deki bir numaraya gelen SMS'leri çek."""
    url = f"https://sms24.me/en/messages/{numara_temiz}"
    try:
        resp = OTURUM.get(url, timeout=30)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        mesajlar = []
        
        # Mesaj kartlarını bul
        kartlar = soup.find_all(class_="message")
        if not kartlar:
            kartlar = soup.find_all("div", class_=re.compile(r"message|card|item|sms"))
        
        for kart in kartlar:
            gonderen_el = kart.find(class_="sender") or kart.find(class_="from") or kart.find("strong")
            mesaj_el = kart.find(class_="text") or kart.find(class_="msg") or kart.find(class_="content")
            zaman_el = kart.find(class_="date") or kart.find(class_="time") or kart.find("small")
            
            gonderen = gonderen_el.get_text(strip=True) if gonderen_el else "Bilinmiyor"
            mesaj_text = mesaj_el.get_text(strip=True) if mesaj_el else kart.get_text(strip=True)
            zaman = zaman_el.get_text(strip=True) if zaman_el else ""
            
            if mesaj_text:
                mesajlar.append({
                    "gonderen": gonderen,
                    "mesaj": mesaj_text,
                    "zaman": zaman
                })
        
        if not mesajlar:
            # Regex ile sayfa içindeki tüm metinden SMS deseni ara
            sayfa_text = resp.text
            # SMS formatlarını ara: "from: ... msg: ..." veya "sender: ..."
            sms_bloklari = re.findall(r'(?:from|sender|gönderen)[:\s]+([^<]+?)(?:msg|message|mesaj|text)[:\s]+([^<]+?)(?:\d+\s*(?:sec|min|hour|ago|önce|saniye|dakika))?',
                                       sayfa_text, re.IGNORECASE | re.DOTALL)
            for gonderen, mesaj in sms_bloklari:
                mesajlar.append({
                    "gonderen": gonderen.strip()[:50],
                    "mesaj": mesaj.strip()[:200],
                    "zaman": ""
                })
        
        return mesajlar
        
    except Exception as e:
        print(f"\n  {KIRMIZI}[HATA] SMS alınamadı: {e}{SON}")
        return []


# ══════════════════════════════════════════════════════
# RECEIVE-SMSS ÜZERİNDEN SMS MESAJLARINI ÇEK
# ══════════════════════════════════════════════════════
def receive_smss_mesajlari_al(numara_temiz):
    """receive-smss.com'daki numaraya gelen SMS'leri çek."""
    url = f"https://receive-smss.com/sms/{numara_temiz}/"
    try:
        resp = OTURUM.get(url, timeout=30)
        if resp.status_code != 200:
            return []
        
        if "Cloudflare" in resp.text or "cf-challenge" in resp.text:
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        mesajlar = []
        
        # message_details class'ı
        for detay in soup.find_all(class_="message_details"):
            gonderen_el = detay.find(class_="senderr")
            mesaj_el = detay.find(class_="msgg")
            zaman_el = detay.find(class_="time")
            
            gonderen = gonderen_el.get_text(strip=True) if gonderen_el else "Bilinmiyor"
            mesaj_text = mesaj_el.get_text(strip=True) if mesaj_el else ""
            zaman = zaman_el.get_text(strip=True) if zaman_el else ""
            
            # A tag'ı varsa içini al
            if gonderen_el:
                a_tag = gonderen_el.find("a")
                if a_tag:
                    gonderen = a_tag.get_text(strip=True)
            
            if mesaj_text:
                mesajlar.append({
                    "gonderen": gonderen,
                    "mesaj": mesaj_text,
                    "zaman": zaman
                })
        
        return mesajlar
        
    except Exception:
        return []


# ══════════════════════════════════════════════════════
# SMS MESAJLARINI AL (Oto kaynak seçimi)
# ══════════════════════════════════════════════════════
def sms_mesajlarini_al(numara_bilgi):
    """Numaranın kaynağına göre uygun yöntemle SMS'leri çek."""
    kaynak = numara_bilgi.get("kaynak", "sms24.me")
    numara_temiz = numara_bilgi["temiz"]
    
    if "receive" in kaynak:
        mesajlar = receive_smss_mesajlari_al(numara_temiz)
        if mesajlar:
            return mesajlar
    
    # Varsayılan: sms24.me
    return sms24_mesajlari_al(numara_temiz)


# ══════════════════════════════════════════════════════
# GÖSTERİM FONKSİYONLARI
# ══════════════════════════════════════════════════════
def temizle():
    os.system("clear" if os.name == "posix" else "cls")

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
        print(f"\n{KIRMIZI}[!] Hiç numara bulunamadı.{SON}")
        print(f"  {SARI}Olası nedenler:{SON}")
        print(f"  {BEYAZ}  • İnternet bağlantınız yok{SON}")
        print(f"  {BEYAZ}  • Kaynak siteler geçici olarak kapalı{SON}")
        print(f"  {BEYAZ}  • VPN veya proxy kullanıyorsanız kapatıp deneyin{SON}")
        print(f"  {BEYAZ}  • Termux'ta: {CYAN}pkg install python -y && pip install requests beautifulsoup4{SON}")
        return []

    # Ülkelere göre grupla
    ulkeler = {}
    for n in numaralar:
        ulke = n["ulke"]
        if ulke not in ulkeler:
            ulkeler[ulke] = []
        ulkeler[ulke].append(n)

    print(f"\n{KALIN}{YESIL}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{YESIL}║{SON}  {MAVI}🌍 MEVCUT SANAL NUMARALAR ({len(numaralar)} adet){MAVI}          {YESIL}║{SON}")
    print(f"{KALIN}{YESIL}╚{'═'*54}╝{SON}\n")

    sayac = 1
    numara_index = []
    
    # Önce Türkiye
    for ulke in sorted(ulkeler.keys()):
        if "turk" in ulke.lower() or "turkey" in ulke.lower():
            print(f"{KALIN}{SARI}► {ulke.upper()}{SON}")
            for n in ulkeler[ulke]:
                kaynak_etiketi = f"{MAVI}[{n.get('kaynak','')}]{SON}" if n.get('kaynak') else ""
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON} {kaynak_etiketi}")
                numara_index.append(n)
                sayac += 1
            print()

    # Diğer ülkeler
    for ulke in sorted(ulkeler.keys()):
        if "turk" in ulke.lower() or "turkey" in ulke.lower():
            continue
        print(f"{KALIN}{SARI}► {ulke.upper()}{SON}")
        for n in ulkeler[ulke]:
            if sayac > 80:
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON}")
            else:
                kaynak_etiketi = f"{MAVI}[{n.get('kaynak','')}]{SON}" if n.get('kaynak') else ""
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON} {kaynak_etiketi}")
            numara_index.append(n)
            sayac += 1
        print()

    return numara_index


def smsleri_goster(mesajlar, numara_bilgi):
    temizle()
    print(f"\n{KALIN}{YESIL}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{YESIL}║{SON}  {MAVI}📨 NUMARA: {BEYAZ}{numara_bilgi['orijinal']} {MAVI}({numara_bilgi['ulke']})       {YESIL}║{SON}")
    print(f"{KALIN}{YESIL}╚{'═'*54}╝{SON}\n")

    if not mesajlar:
        print(f"  {SARI}⚠ Henüz SMS alınmamış.{SON}")
        print(f"  {BEYAZ}  Bu numarayı bir platforma (WhatsApp, Telegram, Instagram vb.){SON}")
        print(f"  {BEYAZ}  kaydedin. Kod geldiğinde burada görünecektir.{SON}")
        print(f"  {BEYAZ}  Her 5 saniyede bir otomatik kontrol edilecek...{SON}")
        return False

    print(f"  {KALIN}{CYAN}{'─'*50}{SON}")
    kodlar = []
    
    for i, m in enumerate(mesajlar, 1):
        gonderen = m.get("gonderen", "Bilinmiyor")
        mesaj    = m.get("mesaj", "")
        zaman    = m.get("zaman", "")

        # Kodları vurgula
        kod_bul = re.findall(r"\b(\d{4,8})\b", mesaj)
        kod_vurgulu = mesaj
        for kod in kod_bul:
            kod_vurgulu = kod_vurgulu.replace(kod, f"{KALIN}{SARI}{kod}{SON}")
            if kod not in kodlar:
                kodlar.append(kod)

        print(f"  {MAVI}[{i}]{SON}")
        print(f"  {BEYAZ}  Gönderen: {CYAN}{gonderen}{SON}")
        print(f"  {BEYAZ}  Mesaj   : {YESIL}{kod_vurgulu}{SON}")
        if zaman:
            print(f"  {BEYAZ}  Zaman   : {SARI}{zaman}{SON}")
        print(f"  {CYAN}{'─'*50}{SON}")

    # Kodları belirgin göster
    if kodlar:
        print(f"\n  {KALIN}{YESIL}╔{'═'*50}╗{SON}")
        print(f"  {KALIN}{YESIL}║{SON}  {SARI}🔑 BULUNAN DOĞRULAMA KODLARI:{SARI}               {YESIL}║{SON}")
        print(f"  {KALIN}{YESIL}║{SON}                                          {YESIL}║{SON}")
        for kod in kodlar:
            print(f"  {KALIN}{YESIL}║{SON}        {KALIN}{MOR}  {kod}  {MOR}{KALIN}                             {YESIL}║{SON}")
        print(f"  {KALIN}{YESIL}╚{'═'*50}╝{SON}")

    return True


# ══════════════════════════════════════════════════════
# SMS İZLEME DÖNGÜSÜ
# ══════════════════════════════════════════════════════
def sms_izleme_dongusu(numara_bilgi):
    gorulen_mesajlar = set()
    ilk_sefer = True
    
    try:
        while True:
            mesajlar = sms_mesajlarini_al(numara_bilgi)

            if ilk_sefer:
                smsleri_goster(mesajlar, numara_bilgi)
                ilk_sefer = False
                
                if mesajlar:
                    print(f"\n  {YESIL}✅ SMS mesajları bulundu!{SON}")
                else:
                    print(f"\n  {SARI}⏳ SMS bekleniyor... Her 5 saniyede otomatik kontrol.{SON}")
                    print(f"  {BEYAZ}  Çıkmak için {KIRMIZI}Ctrl+C{SON}{BEYAZ} basın.{SON}")
            else:
                yeni_mesaj_var = False
                for m in mesajlar:
                    mesaj_hash = f"{m.get('gonderen','')}|{m.get('mesaj','')}|{m.get('zaman','')}"
                    if mesaj_hash not in gorulen_mesajlar:
                        gorulen_mesajlar.add(mesaj_hash)
                        yeni_mesaj_var = True

                if yeni_mesaj_var:
                    temizle()
                    smsleri_goster(mesajlar, numara_bilgi)
                    print(f"\n  {YESIL}✅ Yeni SMS alındı!{SON}")
                    print(f"\n  {SARI}⏳ Yeni mesajlar için izleniyor...{SON}")
                else:
                    sys.stdout.write(f"\r  {CYAN}[{time.strftime('%H:%M:%S')}]{SON} {SARI}Yeni SMS kontrol ediliyor...{SON}     ")
                    sys.stdout.flush()

            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n  {SARI}[!] SMS izleme durduruldu.{SON}")
        input(f"\n  {BEYAZ}Ana menüye dönmek için ENTER'a basın...{SON}")


# ══════════════════════════════════════════════════════
# ANA MENÜ
# ══════════════════════════════════════════════════════
def ana_menu():
    while True:
        menuyu_goster()
        
        try:
            secim = input(f"  {KALIN}{YESIL}Seçiminiz [1-2]: {SON}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {SARI}[!] Çıkılıyor...{SON}")
            sys.exit(0)

        if secim == "2":
            print(f"\n  {SARI}[!] VirtualMark kapatılıyor...{SON}")
            print(f"  {YESIL}Görüşmek üzere! 👋{SON}\n")
            sys.exit(0)

        elif secim == "1":
            print(f"\n  {CYAN}[~] Numaralar yükleniyor, lütfen bekleyin...{SON}")
            print(f"  {SARI}[!] Bu işlem 10-20 saniye sürebilir...{SON}")
            
            numaralar = numara_listesini_al()

            temizle()
            print(BASLIK)
            numara_index = numaralari_goster(numaralar)

            if not numara_index:
                print(f"\n  {SARI}[!] Hiç numara alınamadı.{SON}")
                print(f"  {BEYAZ}  Çözüm önerileri:{SON}")
                print(f"  {BEYAZ}  1. {CYAN}pip install --upgrade requests beautifulsoup4{SON}")
                print(f"  {BEYAZ}  2. VPN kullanıyorsanız kapatın{SON}")
                print(f"  {BEYAZ}  3. {CYAN}pkg install curl{SON} && {CYAN}curl -v https://sms24.me{SON}")
                print(f"  {BEYAZ}  4. Bir süre sonra tekrar deneyin{SON}")
                input(f"\n  {BEYAZ}Devam için ENTER...{SON}")
                continue

            try:
                secim_no = input(f"\n  {KALIN}{MAVI}Numara seçin [1-{len(numara_index)}]: {SON}").strip()
                if not secim_no.isdigit() or int(secim_no) < 1 or int(secim_no) > len(numara_index):
                    print(f"\n  {KIRMIZI}[HATA] 1-{len(numara_index)} arası seçim yapın!{SON}")
                    input(f"{BEYAZ}ENTER...{SON}")
                    continue
                
                secilen = numara_index[int(secim_no) - 1]
                print(f"\n  {YESIL}✅ Seçilen: {KALIN}{secilen['orijinal']}{SON} ({secilen['ulke']}){SON}")
                print(f"  {CYAN}[~] SMS'ler kontrol ediliyor...{SON}")
                time.sleep(1)

                try:
                    sms_izleme_dongusu(secilen)
                except Exception as e:
                    print(f"\n  {KIRMIZI}[HATA] {e}{SON}")
                    input(f"{BEYAZ}ENTER...{SON}")

            except (EOFError, KeyboardInterrupt):
                continue

        else:
            print(f"\n  {KIRMIZI}[HATA] 1 veya 2 girin!{SON}")
            time.sleep(1.5)


# ══════════════════════════════════════════════════════
# BAŞLANGIÇ
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        ana_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {SARI}[!] Çıkılıyor...{SON}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{KIRMIZI}[KRİTİK HATA] {e}{SON}")
        sys.exit(1)
