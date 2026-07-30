#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║                VirtualMark v2.0                          ║
║  Sanal SMS Numarası + Kod Alma Aracı                     ║
║  Kaynak: receive-smss.com (Ücretsiz)                    ║
║  Termux + Python3 Uyumlu                                 ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import sys
import os
import time
import re
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
║              {YESIL}█▀▀ █▄█ █▀▄ █▄█ █ █▀▀ █ █ █ █ █ █ █ █ █▄▀ █▄█ █ {CYAN}║
║                                                          ║
║          {SARI}⚡ Virtual SMS Number + Kod Alma Aracı ⚡{CYAN}          ║
║              {BEYAZ}🔒 100% Ücretsiz • Gerçek Numaralar{BEYAZ}{CYAN}        ║
║              {MAVI}📡 receive-smss.com üzerinden{MAVI}{CYAN}               ║
╚══════════════════════════════════════════════════════════╝
{SON}"""

# ──────────────────────────────────────────────────────
# HEADER (Engellemeyi önlemek için)
# ──────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

OTURUM = requests.Session()
OTURUM.headers.update(HEADERS)


# ══════════════════════════════════════════════════════
# 1. NUMARA LİSTESİNİ ÇEK
# ══════════════════════════════════════════════════════
def numara_listesini_al():
    """receive-smss.com ana sayfasından tüm aktif numaraları çek."""
    url = "https://receive-smss.com/"
    try:
        resp = OTURUM.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"\n{KIRMIZI}[HATA] Sayfaya bağlanılamadı: {e}{SON}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # JavaScript scraper'daki class isimleri
    numara_elemanlari = soup.find_all(class_="number-boxes-itemm-number")
    ulke_elemanlari   = soup.find_all(class_="number-boxes-item-country")
    buton_elemanlari  = soup.find_all(class_="number-boxes1-item-button")

    # Eğer yukarıdaki class'lar yoksa alternatif yöntem dene
    if not numara_elemanlari:
        return numara_listesi_alternatif(soup)

    numaralar = []
    for i in range(len(numara_elemanlari)):
        if i >= len(buton_elemanlari):
            break

        buton_text = buton_elemanlari[i].get_text(strip=True)
        if buton_text.lower() != "open":
            continue  # Sadece aktif numaralar

        numara_raw = numara_elemanlari[i].get_text(strip=True)
        ulke       = ulke_elemanlari[i].get_text(strip=True) if i < len(ulke_elemanlari) else "Bilinmiyor"

        # Numarayı temizle (sadece rakam)
        numara_temiz = re.sub(r"\D", "", numara_raw)
        if not numara_temiz:
            continue

        numaralar.append({
            "orijinal": numara_raw,
            "temiz": numara_temiz,
            "ulke": ulke
        })

    return numaralar


def numara_listesi_alternatif(soup):
    """Yedek: inaktif-numaralar sayfasından veya genel link yapısından çek."""
    print(f"{SARI}[!] Ana sayfa yapısı değişmiş, alternatif yöntem deneniyor...{SON}")
    url = "https://receive-smss.com/inactive-numbers/"
    try:
        resp = OTURUM.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"{KIRMIZI}[HATA] Alternatif sayfaya bağlanılamadı: {e}{SON}")
        return []

    soup2 = BeautifulSoup(resp.text, "html.parser")
    numaralar = []

    # Linkleri bul: /sms/NUMARA/ formatındaki linkler
    for link in soup2.find_all("a", href=True):
        href = link["href"]
        match = re.search(r"/sms/(\d+)/?$", href)
        if match:
            numara_temiz = match.group(1)
            # Ülkeyi bul (link'in içindeki metin)
            link_text = link.get_text(strip=True)
            # Metin formatı: "+905312345678 Turkey" gibi
            ulke_aka = ""
            # Bayrak resmi varsa alt attribute'ünden veya yanındaki text'ten al
            img = link.find("img")
            if img and img.get("alt"):
                ulke_aka = img["alt"]
            
            # Link metninden ülkeyi çıkar
            ulke_bul = re.search(r"(\d+)\s+(.*)", link_text)
            if ulke_bul:
                ulke_aka = ulke_bul.group(2).strip()

            numaralar.append({
                "orijinal": "+" + numara_temiz if not numara_temiz.startswith("+") else numara_temiz,
                "temiz": numara_temiz,
                "ulke": ulke_aka or "Bilinmiyor"
            })

    return numaralar


# ══════════════════════════════════════════════════════
# 2. SMS MESAJLARINI ÇEK
# ══════════════════════════════════════════════════════
def sms_mesajlarini_al(numara_temiz):
    """Belirli bir numaraya gelen SMS'leri çek."""
    url = f"https://receive-smss.com/sms/{numara_temiz}/"
    try:
        resp = OTURUM.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"\n{KIRMIZI}[HATA] SMS sayfasına bağlanılamadı: {e}{SON}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    mesajlar = []

    # Yöntem 1: message_details class'ı
    detaylar = soup.find_all(class_="message_details")
    if detaylar:
        for detay in detaylar:
            gonderen_el = detay.find(class_="senderr")
            mesaj_el    = detay.find(class_="msgg")
            zaman_el    = detay.find(class_="time")

            # Alternatif: senderr içindeki a etiketi
            if gonderen_el:
                a_tag = gonderen_el.find("a")
                gonderen = a_tag.get_text(strip=True) if a_tag else gonderen_el.get_text(strip=True)
            else:
                gonderen = "Bilinmiyor"

            mesaj_text = mesaj_el.get_text(strip=True) if mesaj_el else ""
            zaman_text = zaman_el.get_text(strip=True) if zaman_el else ""

            mesajlar.append({
                "gonderen": gonderen,
                "mesaj": mesaj_text,
                "zaman": zaman_text
            })
        return mesajlar

    # Yöntem 2: wr3pc333el1878 class'ı (JavaScript scraper'daki)
    hucreler = soup.find_all(class_="wr3pc333el1878")
    if hucreler:
        hucre_metinleri = [h.get_text(strip=True) for h in hucreler]
        for i in range(0, len(hucre_metinleri), 3):
            if i + 2 < len(hucre_metinleri):
                mesajlar.append({
                    "gonderen": hucre_metinleri[i],
                    "mesaj": hucre_metinleri[i + 1],
                    "zaman": hucre_metinleri[i + 2]
                })
        return mesajlar

    # Yöntem 3: Tablo yapısı / genel div arama
    # Tüm div'leri tara, SMS içeren blokları bul
    tum_divler = soup.find_all("div")
    for div in tum_divler:
        div_text = div.get_text(strip=True)
        # Eğer div içinde "from:" veya "sender:" gibi ibareler varsa
        if re.search(r"(from|gönderen|sender|mesaj|message)", div_text, re.IGNORECASE):
            satirlar = div_text.split("\n")
            for satir in satirlar:
                satir = satir.strip()
                if satir and len(satir) > 3:
                    mesajlar.append({
                        "gonderen": "Sistem",
                        "mesaj": satir,
                        "zaman": ""
                    })

    return mesajlar


# ══════════════════════════════════════════════════════
# 3. GÖSTERİM FONKSİYONLARI
# ══════════════════════════════════════════════════════
def temizle():
    """Termux ekranını temizle."""
    os.system("clear" if os.name == "posix" else "cls")

def menuyu_goster():
    """Ana menüyü göster."""
    temizle()
    print(BASLIK)
    print(f"{KALIN}{CYAN}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{CYAN}║{SON}  {SARI}[1]{BEYAZ} 📱 SMS Numarası Al & Kodları Görüntüle       {CYAN}║{SON}")
    print(f"{KALIN}{CYAN}║{SON}  {KIRMIZI}[2]{BEYAZ} 🚪 Çıkış                                   {CYAN}║{SON}")
    print(f"{KALIN}{CYAN}╚{'═'*54}╝{SON}")
    print()

def numaralari_goster(numaralar):
    """Numaraları ülkelere göre gruplandırıp göster."""
    if not numaralar:
        print(f"\n{KIRMIZI}[!] Hiç numara bulunamadı. Lütfen internet bağlantınızı kontrol edin veya daha sonra tekrar deneyin.{SON}")
        return

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
    
    # Önce Türkiye varsa göster
    for ulke in sorted(ulkeler.keys()):
        if "turkey" in ulke.lower() or "türkiye" in ulke.lower():
            print(f"{KALIN}{SARI}► {ulke.upper()}{SON}")
            for n in ulkeler[ulke]:
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON}  {BEYAZ}({n['temiz']}){SON}")
                numara_index.append(n)
                sayac += 1
            print()

    # Diğer ülkeler
    for ulke in sorted(ulkeler.keys()):
        if "turkey" in ulke.lower() or "türkiye" in ulke.lower():
            continue
        print(f"{KALIN}{SARI}► {ulke.upper()}{SON}")
        for n in ulkeler[ulke]:
            if sayac > 100:  # Maks 100 numara göster
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON}")
            else:
                print(f"  {CYAN}[{sayac}]{SON} {YESIL}{n['orijinal']}{SON}  {BEYAZ}({n['temiz']}){SON}")
            numara_index.append(n)
            sayac += 1
        print()

    return numara_index


def smsleri_goster(mesajlar, numara_bilgi):
    """SMS mesajlarını formatlı göster."""
    temizle()
    print(f"\n{KALIN}{YESIL}╔{'═'*54}╗{SON}")
    print(f"{KALIN}{YESIL}║{SON}  {MAVI}📨 NUMARA: {BEYAZ}{numara_bilgi['orijinal']} {MAVI}({numara_bilgi['ulke']})        {YESIL}║{SON}")
    print(f"{KALIN}{YESIL}╚{'═'*54}╝{SON}\n")

    if not mesajlar:
        print(f"  {SARI}⚠ Henüz SMS alınmamış.{SON}")
        print(f"  {BEYAZ}  Bu numarayı bir platforma (WhatsApp, Telegram, Instagram vb.){SON}")
        print(f"  {BEYAZ}  kaydedin. Kod geldiğinde burada görünecektir.{SON}")
        print(f"  {BEYAZ}  Her 5 saniyede bir otomatik kontrol edilecek...{SON}")
        return False

    print(f"  {KALIN}{CYAN}{'─'*50}{SON}")
    for i, m in enumerate(mesajlar, 1):
        gonderen = m.get("gonderen", "Bilinmiyor")
        mesaj    = m.get("mesaj", "")
        zaman    = m.get("zaman", "")

        # Kodları vurgula
        kod_bul = re.findall(r"\b(\d{4,8})\b", mesaj)
        kod_vurgulu = mesaj
        if kod_bul:
            for kod in kod_bul:
                kod_vurgulu = kod_vurgulu.replace(kod, f"{SARI}{KALIN}{kod}{SON}{BEYAY}{SON}")

        print(f"  {MAVI}[{i}]{SON}")
        print(f"  {BEYAZ}  Gönderen: {CYAN}{gonderen}{SON}")
        print(f"  {BEYAZ}  Mesaj   : {YESIL}{kod_vurgulu}{SON}")
        if zaman:
            print(f"  {BEYAZ}  Zaman   : {SARI}{zaman}{SON}")
        print(f"  {CYAN}{'─'*50}{SON}")

    # Eğer mesajda kod varsa belirgin göster
    for m in mesajlar:
        kod_bul = re.findall(r"\b(\d{4,8})\b", m.get("mesaj", ""))
        if kod_bul:
            print(f"\n  {KALIN}{YESIL}╔{'═'*50}╗{SON}")
            print(f"  {KALIN}{YESIL}║{SON}  {SARI}🔑 BULUNAN DOĞRULAMA KODLARI:{SARI}               {YESIL}║{SON}")
            for kod in kod_bul:
                print(f"  {KALIN}{YESIL}║{SON}         {KALIN}{MOR}{kod}{MOR}{KALIN}                           {YESIL}║{SON}")
            print(f"  {KALIN}{YESIL}╚{'═'*50}╝{SON}")

    return True


# ══════════════════════════════════════════════════════
# 4. ANA DÖNGÜ - SMS İZLEME
# ══════════════════════════════════════════════════════
def sms_izleme_dongusu(numara_bilgi):
    """Seçilen numarayı sürekli kontrol et, yeni SMS'leri göster."""
    gorulen_mesajlar = set()
    ilk_sefer = True
    
    try:
        while True:
            mesajlar = sms_mesajlarini_al(numara_bilgi["temiz"])

            if ilk_sefer:
                smsleri_goster(mesajlar, numara_bilgi)
                ilk_sefer = False
                
                # İlk mesaj kontrolü
                if mesajlar:
                    print(f"\n  {YESIL}✅ SMS mesajları bulundu!{SON}")
                else:
                    print(f"\n  {SARI}⏳ SMS bekleniyor... Sayfayı her 5 saniyede otomatik yeniliyorum.{SON}")
                    print(f"  {BEYAZ}  Çıkmak için {KIRMIZI}Ctrl+C{SON}{BEYAZ} basın.{SON}")
            else:
                # Yeni mesaj var mı?
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
                    print(f"\n  {SARI}⏳ Yeni mesajlar için izleniyor... (5sn){SON}")
                else:
                    # Tek satırda güncelleme göster
                    sys.stdout.write(f"\r  {CYAN}[{time.strftime('%H:%M:%S')}]{SON} {SARI}Yeni SMS kontrol ediliyor... (her 5sn){SON}        ")
                    sys.stdout.flush()

            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n  {SARI}[!] SMS izleme durduruldu.{SON}")
        input(f"\n  {BEYAZ}Ana menüye dönmek için ENTER'a basın...{SON}")


# ══════════════════════════════════════════════════════
# 5. ANA PROGRAM
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
            numaralar = numara_listesini_al()

            temizle()
            print(BASLIK)
            numara_index = numaralari_goster(numaralar)

            if not numara_index:
                print(f"\n  {KIRMIZI}[!] Hiç numara alınamadı. İnternet bağlantınızı kontrol edin.{SON}")
                input(f"\n  {BEYAZ}Devam etmek için ENTER'a basın...{SON}")
                continue

            try:
                secim_no = input(f"\n  {KALIN}{MAVI}Seçmek istediğiniz numara [1-{len(numara_index)}]: {SON}").strip()
                if not secim_no.isdigit() or int(secim_no) < 1 or int(secim_no) > len(numara_index):
                    print(f"\n  {KIRMIZI}[HATA] Geçersiz seçim! 1 ile {len(numara_index)} arasında bir sayı girin.{SON}")
                    input(f"\n  {BEYAZ}Devam etmek için ENTER'a basın...{SON}")
                    continue
                
                secilen = numara_index[int(secim_no) - 1]
                
                print(f"\n  {YESIL}✅ Seçilen numara: {KALIN}{secilen['orijinal']}{SON} ({secilen['ulke']}){SON}")
                print(f"  {CYAN}[~] Bu numaraya gelen SMS'ler kontrol ediliyor...{SON}")
                time.sleep(1)

                try:
                    sms_izleme_dongusu(secilen)
                except Exception as e:
                    print(f"\n  {KIRMIZI}[HATA] SMS izleme sırasında hata: {e}{SON}")
                    input(f"\n  {BEYAZ}Devam etmek için ENTER'a basın...{SON}")

            except (EOFError, KeyboardInterrupt):
                print(f"\n\n  {SARI}[!] Ana menüye dönülüyor...{SON}")
                continue

        else:
            print(f"\n  {KIRMIZI}[HATA] Lütfen 1 veya 2 girin!{SON}")
            time.sleep(1.5)
            continue


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
        print(f"\n  {KIRMIZI}[KRİTİK HATA] {e}{SON}")
        sys.exit(1)
