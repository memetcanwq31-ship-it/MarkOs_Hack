#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║         VirtualMark v4.0 - TAMAMEN BAĞIMSIZ            ║
║                                                          ║
║  Bu sistem HİÇBİR siteye bağımlı değildir!              ║
║  Cloudflare yok, sms24.me yok, Twilio yok!              ║
║                                                          ║
║  Kendi Android telefonun = Kendi GSM Sunucun            ║
║  Kendi SIM kartın = Kendi Sanal Numaran                 ║
║  Kendi kodun = Tam kontrol sende                        ║
║                                                          ║
║  📱 Termux:API ile telefona gelen SMS'i oku             ║
║  🌐 Flask ile kendi API'ni sun                            ║
║  🔄 Her 3 saniyede bir yeni SMS kontrolü                ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import re
import json
import subprocess
import threading
from datetime import datetime

# ── RENKLER ──
K = "\033[91m"; Y = "\033[92m"; S = "\033[93m"
M = "\033[94m"; P = "\033[95m"; C = "\033[96m"
B = "\033[97m"; KL = "\033[1m"; SN = "\033[0m"

# ── BAŞLIK ──
BASLIK = f"""
{KL}{C}
╔══════════════════════════════════════════════════════════╗
║      {Y}██╗   ██╗██╗██████╗ ████████╗{C}                   ║
║      {Y}██║   ██║██║██╔══██╗╚══██╔══╝{C}                   ║
║      {Y}██║   ██║██║██████╔╝   ██║{C}                      ║
║      {Y}╚██╗ ██╔╝██║██╔══██╗   ██║{C}                      ║
║      {Y} ╚████╔╝ ██║██║  ██║   ██║{C}                      ║
║      {Y}  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝{C}                      ║
║          {S}⚡ TAMAMEN BAĞIMSIZ SMS SİSTEMİ ⚡{C}           ║
║                                                          ║
║   {M}┌──────────────────────────────────────────┐{C}        ║
║   {M}│{B}  ❌ Cloudflare'ye bağımlı DEĞİL        {M}│{C}        ║
║   {M}│{B}  ❌ sms24.me'ye bağımlı DEĞİL          {M}│{C}        ║
║   {M}│{B}  ❌ Twilio/Vonage'a bağımlı DEĞİL      {M}│{C}        ║
║   {M}│{B}  ✅ SADECE senin telefonun + SIM kartın{M}│{C}        ║
║   {M}│{B}  ✅ Tamamen SENİN kontrolünde          {M}│{C}        ║
║   {M}└──────────────────────────────────────────┘{C}        ║
╚══════════════════════════════════════════════════════════╝
{SN}"""

# ═══════════════════════════════════════════════════════
# BÖLÜM 1: ANDROID SMS OKUYUCU (Termux:API)
# ═══════════════════════════════════════════════════════
# Bu bölüm, telefona GELEN tüm SMS'leri okur.
# Kendi SIM kartından gelen gerçek SMS'ler!
# ═══════════════════════════════════════════════════════

def sms_listele():
    """
    Android'deki tüm SMS'leri Termux:API ile oku.
    Bu, telefona gelen GERÇEK SMS'lerdir.
    """
    try:
        # Termux:API ile SMS'leri listele
        sonuc = subprocess.run(
            ["termux-sms-list", "-l", "20"],  # Son 20 SMS
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if sonuc.returncode != 0:
            return []
        
        # JSON çıktısını parse et
        sms_verisi = json.loads(sonuc.stdout)
        
        mesajlar = []
        for sms in sms_verisi:
            mesajlar.append({
                "gonderen": sms.get("number", "Bilinmiyor"),
                "mesaj": sms.get("body", ""),
                "tarih": sms.get("date", ""),
                "thread_id": sms.get("thread_id", 0)
            })
        
        return mesajlar
        
    except FileNotFoundError:
        return []  # termux-api yüklü değil
    except json.JSONDecodeError:
        return []
    except Exception:
        return []

def yeni_sms_kontrol(son_thread_id=0):
    """Sadece YENİ gelen SMS'leri kontrol et"""
    try:
        sonuc = subprocess.run(
            ["termux-sms-list", "-l", "1"],  # Son 1 SMS
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if sonuc.returncode != 0:
            return None, son_thread_id
        
        sms_verisi = json.loads(sonuc.stdout)
        if not sms_verisi:
            return None, son_thread_id
        
        en_son = sms_verisi[0]
        thread_id = en_son.get("thread_id", 0)
        
        if thread_id != son_thread_id:
            # Yeni SMS geldi!
            return {
                "gonderen": en_son.get("number", "Bilinmiyor"),
                "mesaj": en_son.get("body", ""),
                "tarih": en_son.get("date", "")
            }, thread_id
        
        return None, son_thread_id
        
    except Exception:
        return None, son_thread_id

def kendi_numaranı_bul():
    """Telefondaki SIM kartın numarasını bulmaya çalış"""
    try:
        sonuc = subprocess.run(
            ["termux-telephony-deviceinfo"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if sonuc.returncode == 0:
            bilgi = json.loads(sonuc.stdout)
            return bilgi.get("number", "Bilinmiyor")
    except:
        pass
    return "SIM'deki Numara"


# ═══════════════════════════════════════════════════════
# BÖLÜM 2: SMS ANALİZ & KOD BULMA
# ═══════════════════════════════════════════════════════

def kod_bul(mesaj):
    """SMS içindeki doğrulama kodlarını bul"""
    kodlar = []
    
    # 4-8 haneli kodlar
    kodlar += re.findall(r"\b(\d{4,8})\b", mesaj)
    
    # "CODE: XXXX" formatı
    kodlar += re.findall(r"(?:code|kod|doğrulama|onay|şifre)[:\s]*[#:]?\s*(\w{4,10})", mesaj, re.IGNORECASE)
    
    # Benzersiz yap
    return list(set(kodlar))


def sms_ozeti(mesaj):
    """SMS'in özetini çıkar"""
    ozet = {
        "kodlar": kod_bul(mesaj["mesaj"]),
        "gonderen": mesaj["gonderen"],
        "kisa_mesaj": mesaj["mesaj"][:100] + "..." if len(mesaj["mesaj"]) > 100 else mesaj["mesaj"],
        "tarih": mesaj.get("tarih", ""),
        "servis": servis_bul(mesaj["mesaj"], mesaj["gonderen"])
    }
    return ozet


def servis_bul(mesaj, gonderen):
    """Hangi servisten geldiğini tespit et"""
    servisler = {
        "whatsapp": r"(whatsapp|wa\s)", "telegram": r"(telegram|tg\s)",
        "instagram": r"(instagram|ig\s)", "facebook": r"(facebook|fb\s|meta)",
        "google": r"(google|gmail|youtube|g-\d)", "twitter": r"(twitter|x\.com)",
        "tiktok": r"(tiktok)", "linkedin": r"(linkedin)",
        "github": r"(github)", "microsoft": r"(microsoft|outlook|hotmail)",
        "amazon": r"(amazon|aws)", "apple": r"(apple|icloud)",
        "n11": r"(n11)", "trendyol": r"(trendyol)",
        "hepsiburada": r"(hepsiburada)", "yemeksepeti": r"(yemeksepeti)",
    }
    
    metin = (mesaj + " " + gonderen).lower()
    for servis, desen in servisler.items():
        if re.search(desen, metin):
            return servis.capitalize()
    
    # Gönderen numarasına bak
    if gonderen.startswith("+90") or gonderen.startswith("90"):
        return "Türkiye (Yerel)"
    elif gonderen.startswith("+1") or gonderen.startswith("1"):
        return "ABD/Uluslararası"
    
    return "Bilinmeyen Servis"


# ═══════════════════════════════════════════════════════
# BÖLÜM 3: SMS İZLEME MODÜLÜ
# ═══════════════════════════════════════════════════════

def sms_izleme_baslat():
    """Arka planda SMS izlemeyi başlat"""
    global son_thread_id, sms_gecmisi
    
    son_thread_id = 0
    sms_gecmisi = []
    
    print(f"\n  {C}[~] SMS izleme başlatılıyor...{SN}")
    print(f"  {B}  Telefonuna SMS gelince otomatik yakalayacağım!{SN}")
    print(f"  {B}  Çıkmak için {K}Ctrl+C{SN}{B} bas.{SN}")
    
    try:
        while True:
            yeni, son_thread_id = yeni_sms_kontrol(son_thread_id)
            
            if yeni:
                ozet = sms_ozeti(yeni)
                sms_gecmisi.append(ozet)
                
                os.system("clear")
                print(BASLIK)
                print(f"\n{KL}{Y}╔{'═'*54}╗{SN}")
                print(f"{KL}{Y}║{SN}  {M}📨 YENİ SMS GELDİ!                            {Y}║{SN}")
                print(f"{KL}{Y}╚{'═'*54}╝{SN}\n")
                print(f"  {B}  Gönderen: {C}{ozet['gonderen']}{SN}")
                print(f"  {B}  Servis  : {P}{ozet['servis']}{SN}")
                print(f"  {B}  Mesaj   : {Y}{ozet['kisa_mesaj']}{SN}")
                
                if ozet["kodlar"]:
                    print(f"\n  {KL}{Y}╔{'═'*50}╗{SN}")
                    print(f"  {KL}{Y}║{SN}  {S}🔑 DOĞRULAMA KODU BULUNDU!{S}              {Y}║{SN}")
                    for kod in ozet["kodlar"]:
                        print(f"  {KL}{Y}║{SN}       {KL}{P}► {kod} ◄{P}{KL}                    {Y}║{SN}")
                    print(f"  {KL}{Y}╚{'═'*50}╝{SN}")
                
                print(f"\n  {C}{'─'*50}{SN}")
                print(f"  {S}⏳ Yeni SMS bekleniyor...{SN}")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print(f"\n\n  {S}[!] İzleme durduruldu.{SN}")
        time.sleep(1)


# ═══════════════════════════════════════════════════════
# BÖLÜM 4: API SUNUCU (Arkadaşların da kullansın)
# ═══════════════════════════════════════════════════════
# Bu bölüm, kendi telefonundaki SMS'leri
# ağdaki diğer cihazlara sunar.
# ═══════════════════════════════════════════════════════

def api_sunucu_baslat(port=5555):
    """Flask ile SMS API sunucusu"""
    
    try:
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        app.config['JSON_AS_ASCII'] = False
        
        @app.route("/")
        def ana_sayfa():
            return jsonify({
                "sistem": "VirtualMark v4.0 - Tamamen Bağımsız",
                "durum": "çalışıyor",
                "kaynak": "Kendi Android Telefon + SIM Kart",
                "endpoints": {
                    "/": "Bu sayfa",
                    "/sms": "Tüm SMS'leri listele",
                    "/sms/son": "Son SMS'i göster",
                    "/sms/kodlar": "Sadece kodları göster",
                    "/saglik": "Sistem sağlık kontrolü"
                }
            })
        
        @app.route("/sms")
        def sms_liste():
            smsler = sms_listele()
            sonuclar = []
            for s in smsler[:20]:
                sonuclar.append(sms_ozeti(s))
            return jsonify({
                "toplam": len(sonuclar),
                "smsler": sonuclar
            })
        
        @app.route("/sms/son")
        def son_sms():
            smsler = sms_listele()
            if smsler:
                return jsonify(sms_ozeti(smsler[0]))
            return jsonify({"mesaj": "Henüz SMS yok"})
        
        @app.route("/sms/kodlar")
        def kodlar():
            smsler = sms_listele()
            tum_kodlar = []
            for s in smsler:
                tum_kodlar.extend(kod_bul(s["mesaj"]))
            return jsonify({
                "kodlar": list(set(tum_kodlar)),
                "adet": len(set(tum_kodlar))
            })
        
        @app.route("/saglik")
        def saglik():
            try:
                subprocess.run(["termux-sms-list", "-l", "1"],
                             capture_output=True, timeout=5)
                sms_durum = "✅ Çalışıyor"
            except:
                sms_durum = "❌ SMS izni yok"
            
            return jsonify({
                "durum": "sağlıklı",
                "sms_servisi": sms_durum,
                "zaman": datetime.now().isoformat()
            })
        
        # IP'yi bul
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        
        print(f"\n  {Y}[+] API SUNUCUSU BAŞLADI!{SN}")
        print(f"  {KL}{C}╔{'═'*54}╗{SN}")
        print(f"  {KL}{C}║{SN}  {B}📍 Aynı WiFi'dakiler için:{SN}              {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {M}  http://{ip}:{port}/{SN}                       {C}║{SN}")
        print(f"  {KL}{C}║{SN}                                          {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {S}📌 Kullanılabilir API'ler:{SN}              {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {C}  GET /sms     → Tüm SMS'ler{SN}           {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {C}  GET /sms/son → Son SMS{SN}              {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {C}  GET /sms/kodlar → Sadece kodlar{SN}      {C}║{SN}")
        print(f"  {KL}{C}║{SN}                                          {C}║{SN}")
        print(f"  {KL}{C}║{SN}  {K}  ❌ Durdurmak için Ctrl+C{SN}               {C}║{SN}")
        print(f"  {KL}{C}╚{'═'*54}╝{SN}")
        
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except ImportError:
        print(f"\n  {K}[HATA] Flask yüklü değil!{SN}")
        print(f"  {B}  Çözüm: {C}pip install flask{SN}")
        time.sleep(2)
    except Exception as e:
        print(f"\n  {K}[HATA] Sunucu hatası: {e}{SN}")
        time.sleep(2)


# ═══════════════════════════════════════════════════════
# BÖLÜM 5: SMS GEÇMİŞİ GÖSTER
# ═══════════════════════════════════════════════════════

def sms_gecmis_goster():
    """Telefondaki tüm SMS geçmişini göster"""
    print(f"\n  {C}[~] SMS geçmişi okunuyor...{SN}")
    
    smsler = sms_listele()
    
    if not smsler:
        print(f"\n  {S}⚠ Hiç SMS bulunamadı veya SMS izni verilmemiş.{SN}")
        print(f"  {B}  Çözüm:{SN}")
        print(f"  {B}  1. {C}pkg install termux-api{SN}")
        print(f"  {B}  2. {C}Ayarlar → Uygulamalar → Termux → İzinler → SMS{SN}")
        print(f"  {B}  3. Telefonu yeniden başlat{SN}")
        input(f"\n  {B}ENTER...{SN}")
        return
    
    os.system("clear")
    print(BASLIK)
    print(f"\n{KL}{Y}╔{'═'*54}╗{SN}")
    print(f"{KL}{Y}║{SN}  {M}📱 SMS GEÇMİŞİ ({len(smsler)} SMS){M}                  {Y}║{SN}")
    print(f"{KL}{Y}╚{'═'*54}╝{SN}\n")
    
    for i, s in enumerate(smsler[:15], 1):
        ozet = sms_ozeti(s)
        
        print(f"  {C}[{i}]{SN}")
        print(f"  {B}  Gönderen: {C}{ozet['gonderen']}{SN}")
        if ozet["servis"] != "Bilinmeyen Servis":
            print(f"  {B}  Servis  : {P}{ozet['servis']}{SN}")
        print(f"  {B}  Mesaj   : {Y}{ozet['kisa_mesaj']}{SN}")
        if ozet["kodlar"]:
            print(f"  {B}  Kodlar  : {S}{', '.join(ozet['kodlar'])}{SN}")
        print(f"  {C}{'─'*50}{SN}")
    
    if len(smsler) > 15:
        print(f"  {S}... ve {len(smsler)-15} SMS daha{SN}")
    
    input(f"\n  {B}ENTER'a bas...{SN}")


# ═══════════════════════════════════════════════════════
# BÖLÜM 6: YARDIMCI KONTROLLER
# ═══════════════════════════════════════════════════════

def sistem_kontrol():
    """Sistemin çalışıp çalışmadığını kontrol et"""
    sorunlar = []
    
    # Termux:API kontrol
    try:
        subprocess.run(["termux-sms-list", "-l", "1"], 
                      capture_output=True, timeout=5)
    except FileNotFoundError:
        sorunlar.append("❌ termux-api yüklü DEĞİL → pkg install termux-api")
    except Exception:
        sorunlar.append("❌ SMS izni verilmemiş → Ayarlar'dan izin ver")
    
    # Python paketleri
    try:
        import flask
    except ImportError:
        sorunlar.append("❌ Flask yüklü değil → pip install flask")
    
    try:
        import requests
    except ImportError:
        sorunlar.append("❌ requests yüklü değil → pip install requests")
    
    if sorunlar:
        print(f"\n  {K}[!] Şu sorunlar bulundu:{SN}")
        for sorun in sorunlar:
            print(f"  {B}  • {sorun}{SN}")
        return False
    
    kendi_no = kendi_numaranı_bul()
    print(f"\n  {Y}[✓] Tüm kontroller geçti!{SN}")
    print(f"  {B}  Telefon numaran: {C}{kendi_no}{SN}")
    return True


# ═══════════════════════════════════════════════════════
# BÖLÜM 7: ANA MENÜ
# ═══════════════════════════════════════════════════════

def temizle(): os.system("clear")

def menuyu_goster():
    temizle()
    print(BASLIK)
    print(f"{KL}{Y}╔{'═'*54}╗{SN}")
    print(f"{KL}{Y}║{SN}  {S}[1]{B} 📨 SMS İzleme Başlat (Anında yakala){SN}       {Y}║{SN}")
    print(f"{KL}{Y}║{SN}  {S}[2]{B} 📱 SMS Geçmişini Göster{SN}                 {Y}║{SN}")
    print(f"{KL}{Y}║{SN}  {S}[3]{B} 🌐 API Sunucu Başlat (Herkes kullansın){SN}     {Y}║{SN}")
    print(f"{KL}{Y}║{SN}  {S}[4]{B} 🔧 Sistem Kontrol{SN}                        {Y}║{SN}")
    print(f"{KL}{Y}║{SN}  {K}[5]{B} 🚪 Çıkış{SN}                                {Y}║{SN}")
    print(f"{KL}{Y}╚{'═'*54}╝{SN}")
    print(f"  {P}🔒 SADECE SENİN TELEFONUN • BAĞIMSIZ SİSTEM{SN}")
    print()

def ana_menu():
    while True:
        menuyu_goster()
        
        try:
            secim = input(f"  {KL}{Y}Seçim [1-5]: {SN}").strip()
        except:
            print(); sys.exit(0)
        
        if secim == "5":
            print(f"\n  {S}Görüşmek üzere! 🚀{SN}")
            print(f"  {B}  Bu sistem TAMAMEN senin kontrolünde.{SN}")
            sys.exit(0)
        
        elif secim == "4":
            print(f"\n  {C}[~] Sistem kontrol ediliyor...{SN}")
            sistem_kontrol()
            input(f"\n  {B}ENTER...{SN}")
        
        elif secim == "3":
            print(f"\n  {C}[~] API sunucusu başlatılıyor...{SN}")
            time.sleep(1)
            try:
                api_sunucu_baslat(5555)
            except KeyboardInterrupt:
                print(f"\n  {S}Sunucu durduruldu.{SN}")
                time.sleep(1)
        
        elif secim == "2":
            sms_gecmis_goster()
        
        elif secim == "1":
            sms_izleme_baslat()
        
        else:
            print(f"\n  {K}[HATA] 1-5 arası gir!{SN}")
            time.sleep(1.5)

# ═══════════════════════════════════════════════════════
# BAŞLANGIÇ
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Hoş geldin mesajı
        temizle()
        print(BASLIK)
        print(f"\n  {C}[~] Sistem başlatılıyor...{SN}")
        
        # Hızlı kontrol
        try:
            subprocess.run(["termux-sms-list", "-l", "1"], 
                         capture_output=True, timeout=5)
            print(f"  {Y}[✓] SMS servisi hazır{SN}")
        except:
            print(f"  {S}[!] SMS izni kontrol et: pkg install termux-api{SN}")
        
        time.sleep(2)
        ana_menu()
        
    except KeyboardInterrupt:
        print(f"\n  {S}Çıkılıyor...{SN}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{K}[KRİTİK HATA] {e}{SN}")
        sys.exit(1)
