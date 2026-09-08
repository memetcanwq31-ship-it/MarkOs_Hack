#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║   VirtualMark v6.0 - GERÇEK NUMARA SİSTEMİ              ║
║                                                          ║
║   ✅ GERÇEK numaralar (sms24.me - gerçek SIM'ler)        ║
║   ✅ GERÇEK kodlar (WhatsApp/Telegram/Instagram vs.)     ║
║   ✅ Ekstra: Kendi SIM'in de bağlanabilir                ║
║   ✅ Ücretsiz, Cloudflare yok, simülasyon YOK            ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import time
import json
import subprocess
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Eksik paket. Şunu çalıştır: pip install requests beautifulsoup4")
    sys.exit(1)

# ── RENKLER ──
K = "\033[91m"; Y = "\033[92m"; S = "\033[93m"
M = "\033[94m"; P = "\033[95m"; C = "\033[96m"
B = "\033[97m"; KL = "\033[1m"; SN = "\033[0m"

BASLIK = f"""{KL}{C}
╔══════════════════════════════════════════════════════════╗
║       {Y}VirtualMark v6.0{C} - {S}GERÇEK NUMARA SİSTEMİ{C}       ║
║       {M}Gerçek SIM'ler • Gerçek Kodlar • Ücretsiz{C}       ║
╚══════════════════════════════════════════════════════════╝{SN}"""

BAS = "https://sms24.me"
OTURUM = requests.Session()
OTURUM.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
})

# ── PLATFORM TESPİT ──
PLATFORM = {
    "whatsapp": "WhatsApp", "telegram": "Telegram", "instagram": "Instagram",
    "facebook": "Facebook", "google": "Google", "gmail": "Google",
    "tiktok": "TikTok", "twitter": "Twitter/X", "github": "GitHub",
    "microsoft": "Microsoft", "amazon": "Amazon", "apple": "Apple",
    "trendyol": "Trendyol", "steam": "Steam", "discord": "Discord",
    "netflix": "Netflix", "spotify": "Spotify", "binance": "Binance",
}

def kod_bul(metin):
    """Mesajdan 4-8 haneli doğrulama kodlarını çıkar"""
    kodlar = re.findall(r"\b(\d{3}[- ]?\d{3})\b", metin)      # 482-916 formatı
    kodlar += re.findall(r"\b(\d{4,8})\b", metin)              # 123456 formatı
    kodlar += re.findall(r"(?:code|kod|şifre)[:\s]*#?\s*([A-Z0-9]{4,8})", metin, re.I)
    temiz = []
    for k in kodlar:
        k = k.replace("-", "").replace(" ", "")
        # Yıl/tarih gibi olanları ele
        if len(k) >= 4 and not (k.startswith("20") and len(k) == 4):
            temiz.append(k)
    return list(dict.fromkeys(temiz))[:3]

def servis_bul(metin):
    m = metin.lower()
    for anahtar, ad in PLATFORM.items():
        if anahtar in m:
            return ad
    return "Bilinmeyen"

# ═══════════════════════════════════════════════════════
# BÖLÜM 1: GERÇEK NUMARALARI ÇEK (sms24.me)
# ═══════════════════════════════════════════════════════

def numaralari_cek(ulke="us", miktar=15):
    """GERÇEK halka açık numaraları çek"""
    url = f"{BAS}/en/countries/{ulke}"
    try:
        r = OTURUM.get(url, timeout=15)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        numaralar = []
        for a in soup.select("a[href*='/en/numbers/']"):
            href = a.get("href", "")
            num = href.rstrip("/").split("/")[-1]
            if num and re.match(r"^\+?\d{8,15}$", num) and num not in numaralar:
                numaralar.append(num)
            if len(numaralar) >= miktar:
                break
        return numaralar
    except Exception:
        return []

def ulke_listesi():
    return {
        "1": ("us", "🇺🇸 ABD"), "2": ("gb", "🇬🇧 İngiltere"),
        "3": ("de", "🇩🇪 Almanya"), "4": ("nl", "🇳🇱 Hollanda"),
        "5": ("fr", "🇫🇷 Fransa"), "6": ("ru", "🇷🇺 Rusya"),
        "7": ("ca", "🇨🇦 Kanada"), "8": ("se", "🇸🇪 İsveç"),
    }

def mesajlari_cek(numara):
    """Numaraya gelen GERÇEK mesajları çek"""
    url = f"{BAS}/en/numbers/{numara}"
    try:
        r = OTURUM.get(url, timeout=15)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        mesajlar = []
        # sms24.me yapısı: <dd> içinde <a> (gönderen) + <span> (mesaj)
        for dd in soup.select("dd"):
            a = dd.find("a")
            span = dd.find("span")
            if span:
                gonderen = a.get_text(strip=True) if a else "?"
                metin = span.get_text(strip=True)
                if metin:
                    mesajlar.append({"gonderen": gonderen, "mesaj": metin})
        return mesajlar
    except Exception:
        return []

# ═══════════════════════════════════════════════════════
# BÖLÜM 2: KENDİ SIM'İM (v4 motoru - opsiyonel ekstra)
# ═══════════════════════════════════════════════════════

def kendi_sim_smsleri(limit=20):
    try:
        sonuc = subprocess.run(["termux-sms-list", "-l", str(limit)],
                               capture_output=True, text=True, timeout=10)
        if sonuc.returncode != 0:
            return []
        return [{"gonderen": s.get("number", "?"), "mesaj": s.get("body", "")}
                for s in json.loads(sonuc.stdout)]
    except Exception:
        return []

# ═══════════════════════════════════════════════════════
# BÖLÜM 3: GERÇEK KOD AVI
# ═══════════════════════════════════════════════════════

def numara_sahnesi(numara):
    """Seçilen GERÇEK numarayı göster ve kodları canlı izle"""
    os.system("clear")
    print(BASLIK)
    print(f"""
  {KL}{Y}╔════════════════════════════════════════════╗{SN}
  {KL}{Y}║{SN}  {B}📱 GERÇEK NUMARAN:{SN}                       {Y}║{SN}
  {KL}{Y}║{SN}                                            {Y}║{SN}
  {KL}{Y}║{SN}       {KL}{Y}{numara}{SN}                     {Y}║{SN}
  {KL}{Y}╚════════════════════════════════════════════╝{SN}

  {S}[→] Bu numarayı platforma (WhatsApp, Telegram vs.) gir{SN}
  {S}[→] Kod buraya GERÇEK olarak gelecek{SN}
  {S}[→] Başka biri de kullanıyor olabilir, hızlı ol!{SN}
""")

    baslangic_mesajlari = {m["mesaj"] for m in mesajlari_cek(numara)}
    print(f"  {C}[~] Kod bekleniyor... (Ctrl+C: çık){SN}\n")

    try:
        while True:
            mesajlar = mesajlari_cek(numara)
            for m in mesajlar:
                if m["mesaj"] in baslangic_mesajlari:
                    continue  # eski mesaj, atla
                kodlar = kod_bul(m["mesaj"])
                servis = servis_bul(m["mesaj"] + " " + m["gonderen"])
                print(f"  {S}[{datetime.now().strftime('%H:%M:%S')}]{SN} "
                      f"{KL}{P}{servis}{SN} ← {B}{m['gonderen']}{SN}")
                print(f"      {B}{m['mesaj']}{SN}")
                if kodlar:
                    for k in kodlar:
                        print(f"      {KL}{S}🔑 KOD: {k}{SN}")
                print()
                baslangic_mesajlari.add(m["mesaj"])
            time.sleep(8)
    except KeyboardInterrupt:
        pass

def kod_avla(numara, hedef_servis=None, sure=180):
    """Belirli servisten kod bekle"""
    print(f"  {C}[~] {numara} numarasından kod bekleniyor ({sure}s)...{SN}")
    baslangic = {m["mesaj"] for m in mesajlari_cek(numara)}
    bitis = time.time() + sure
    while time.time() < bitis:
        for m in mesajlari_cek(numara):
            if m["mesaj"] in baslangic:
                continue
            kodlar = kod_bul(m["mesaj"])
            servis = servis_bul(m["mesaj"] + " " + m["gonderen"])
            if kodlar and (hedef_servis is None or servis.lower() == hedef_servis.lower()):
                return {"kod": kodlar[0], "tumu": kodlar, "servis": servis, "mesaj": m["mesaj"]}
            baslangic.add(m["mesaj"])
        print(f"  {B}  ...bekleniyor ({int(bitis - time.time())}s kaldı){SN}", end="\r")
        time.sleep(8)
    return None

# ═══════════════════════════════════════════════════════
# BÖLÜM 4: MENÜLER
# ═══════════════════════════════════════════════════════

def gercek_numara_al():
    """Akış: ülke seç → numara seç → kod bekle"""
    os.system("clear")
    print(BASLIK)
    print(f"\n  {KL}{Y}🌍 ÜLKE SEÇ (gerçek numaralar):{SN}\n")
    for k, (kod, ad) in ulke_listesi().items():
        print(f"  {S}[{k}]{B} {ad}{SN}")
    
    sec = input(f"\n  {KL}{Y}Seçim [1-8]: {SN}").strip()
    ulkeler = ulke_listesi()
    if sec not in ulkeler:
        print(f"  {K}[!] Geçersiz seçim{SN}"); time.sleep(1.5); return
    
    ulke_kodu, ulke_adi = ulkeler[sec]
    print(f"\n  {C}[~] {ulke_adi} gerçek numaraları çekiliyor...{SN}")
    
    numaralar = numaralari_cek(ulke_kodu)
    if not numaralar:
        print(f"  {K}[!] Numara çekilemedi. İnterneti kontrol et veya başka ülke dene.{SN}")
        time.sleep(2); return
    
    print(f"  {Y}[+] {len(numaralar)} GERÇEK numara bulundu:\n{SN}")
    for i, n in enumerate(numaralar, 1):
        # Numaranın son mesaj sayısını da göster
        print(f"  {S}[{i}]{B} {n}{SN}")
    
    n_sec = input(f"\n  {KL}{Y}Numara seç [1-{len(numaralar)}]: {SN}").strip()
    if not n_sec.isdigit() or not (1 <= int(n_sec) <= len(numaralar)):
        print(f"  {K}[!] Geçersiz{SN}"); time.sleep(1.5); return
    
    numara_sahnesi(numaralar[int(n_sec) - 1])

def kod_ara_numarada():
    """Mevcut numarada son gelen kodları tara"""
    os.system("clear")
    print(BASLIK)
    numara = input(f"\n  {KL}{Y}Numara gir (örn: +12025550123): {SN}").strip().replace(" ", "")
    if not numara:
        return
    print(f"\n  {C}[~] {numara} kontrol ediliyor...{SN}")
    mesajlar = mesajlari_cek(numara)
    if not mesajlar:
        print(f"  {K}[!] Mesaj bulunamadı veya numara geçersiz.{SN}")
        time.sleep(2); return
    print(f"  {Y}[+] {len(mesajlar)} mesaj bulundu:\n{SN}")
    bulundu = False
    for m in mesajlar[:15]:
        kodlar = kod_bul(m["mesaj"])
        servis = servis_bul(m["mesaj"] + " " + m["gonderen"])
        print(f"  {P}[{servis}]{SN} {B}{m['gonderen']}{SN}: {m['mesaj'][:80]}")
        if kodlar:
            bulundu = True
            print(f"      {KL}{S}🔑 KOD: {', '.join(kodlar)}{SN}")
    if not bulundu:
        print(f"\n  {S}[!] Son mesajlarda kod yok. Platforma kayıt ol, sonra tekrar tara.{SN}")
    input(f"\n  {B}ENTER...{SN}")

def kendi_sim_menu():
    """Kendi SIM'inin gerçek numarası"""
    os.system("clear")
    print(BASLIK)
    print(f"\n  {KL}{Y}📱 KENDİ SIM'İN (gerçek numaran){SN}\n")
    try:
        sonuc = subprocess.run(["termux-telephony-deviceinfo"],
                               capture_output=True, text=True, timeout=10)
        info = json.loads(sonuc.stdout)
        print(f"  {B}Numaran: {Y}{info.get('msisdn', 'Gizli/Görüntülenemiyor')}{SN}\n")
    except Exception:
        print(f"  {S}[!] Numara bilgisi alınamadı (normal, bazı operatörler gizler){SN}\n")
    
    print(f"  {C}[~] SMS'ler okunuyor...{SN}\n")
    smsler = kendi_sim_smsleri()
    if not smsler:
        print(f"  {K}[!] SMS okunamadı. İzin gerekli:{SN}")
        print(f"  {B}  Ayarlar → Uygulamalar → Termux → İzinler → SMS → Aç{SN}")
        print(f"  {B}  Ayrıca Termux'ta: {C}pkg install termux-api{SN}")
    else:
        for s in smsler[:20]:
            kodlar = kod_bul(s["mesaj"])
            servis = servis_bul(s["mesaj"] + " " + s["gonderen"])
            print(f"  {P}[{servis}]{SN} {B}{s['gonderen']}{SN}: {s['mesaj'][:70]}")
            if kodlar:
                print(f"      {KL}{S}🔑 KOD: {', '.join(kodlar)}{SN}")
    input(f"\n  {B}ENTER...{SN}")

def menu():
    os.system("clear")
    print(BASLIK)
    print(f"""
  {S}[1]{B} 📱 GERÇEK Numara Al + GERÇEK Kod Bekle{SN}
  {S}[2]{B} 🔍 Numarada Kod Ara (kendi girdiğin numara){SN}
  {S}[3]{B} 💳 Kendi SIM'im (gerçek numaram, termux-api){SN}
  {S}[4]{B} 🚪 Çıkış{SN}
""")

def ana():
    while True:
        menu()
        try:
            secim = input(f"  {KL}{Y}Seçim [1-4]: {SN}").strip()
        except KeyboardInterrupt:
            print(); sys.exit(0)
        
        if secim == "1":
            gercek_numara_al()
        elif secim == "2":
            kod_ara_numarada()
        elif secim == "3":
            kendi_sim_menu()
        elif secim == "4":
            print(f"\n  {S}Çıkılıyor...{SN}"); sys.exit(0)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(f"\n  {S}Çıkılıyor...{SN}")
