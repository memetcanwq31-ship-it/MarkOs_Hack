#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telefonİstihbarat Pro v2.0 — Telefon Numarası İstihbarat & SMS Test Platformu
Yapımcı: @markos39

Yetkili test kapsamında kullanılır. Flood modülü YALNIZCA izin listesindeki
numaralara ve kendi endpoint'lerine çalışır. Üçüncü kişilere istenmeyen
SMS gönderimi yasal suçtur; bu araç bunu yapmaz.

Kullanım:
  python3 telefonistihbarat.py                          # Menü
  python3 telefonistihbarat.py +905321234567            # Tek satır analiz
  python3 telefonistihbarat.py sorgu +905321234567      # Canlı numara sorgu
  python3 telefonistihbarat.py flood --url http://x/otp --numara +905321234567 --adet 60 --dry-run
  python3 telefonistihbarat.py vsim al --provider twilio --ulke US
  python3 telefonistihbarat.py vsim webhook --port 8080
  python3 telefonistihbarat.py vsim mesajlar
  python3 telefonistihbarat.py modem gonder +905321234567 "test" [--port /dev/ttyUSB0]
  python3 telefonistihbarat.py selftest                 # Altyapı kendi kendini test eder
  python3 telefonistihbarat.py config                   # Config + izin listesi oluştur

Bağımlılıklar: yalnızca GSM modem modülü için pyserial (pip install pyserial).
Diğer her şey saf Python standart kütüphanesidir (sıfır bağımlılık).
"""

import argparse
import base64
import json
import os
import random
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SURUM = "2.0.0"
DEFAULT_ULKE = "Türkiye"          # "0" ile başlayan ulusal girişler için varsayılan

# ═══════════════════════════════════════════════════
#  RENKLER
# ═══════════════════════════════════════════════════
class R:
    R = "\033[0m"; B = "\033[1m"; G = "\033[90m"
    K = "\033[91m"; Y = "\033[92m"; S = "\033[93m"
    M = "\033[94m"; P = "\033[95m"; C = "\033[96m"


# cprint ile kullanım için renk takma adları
RESET    = R.R
GRAY     = R.G
RED      = R.K
GREEN    = R.Y
YELLOW   = R.S
BLUE     = R.M
MAGENTA  = R.P
CYAN     = R.C
BOLD     = R.B


BANNER = f"""
{R.C} ████████╗███████╗██╗     ███████╗ ██████╗ ███╗   ██╗
{R.C} ╚══██╔══╝██╔════╝██║     ██╔════╝██╔═══██╗████╗  ██║{R.R}   {R.B}{R.P}TELEFON İSTİHBARAT PRO v{SURUM}{R.R}
{R.C}    ██║   █████╗  ██║     █████╗  ██║   ██║██╔██╗ ██║{R.R}   {R.C}İstihbarat + SMS Test + VSIM{R.R}
{R.C}    ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██║╚██╗██║{R.R}   {R.S}190+ Ülke | E.164 | OTP | Flood{R.R}
{R.C}    ██║   ███████╗███████╗███████╗╚██████╔╝██║ ╚████║{R.R}   {R.Y}Sorgu | VSIM | GSM Modem{R.R}
{R.C}    ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝{R.R}
{R.S}          Yapımcı: @markos39{R.R}
{R.K}   [!] Yalnızca yetkili test kapsamında. Flood modülü izin listesi zorunludur.{R.R}
"""

# ═══════════════════════════════════════════════════
#  YAPILANDIRMA
# ═══════════════════════════════════════════════════
CONFIG_DOSYA = "tf_config.json"
IZINLI_DOSYA = "izinli_numaralar.txt"
DB_DOSYA = "tf_veri.db"
RAPOR_KLASORU = "raporlar"


def config_yukle():
    cfg = {}
    if os.path.exists(CONFIG_DOSYA):
        try:
            with open(CONFIG_DOSYA, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    env_map = {
        "NUMVERIFY_KEY": ("sorgu", "numverify_key"),
        "ABSTRACT_KEY": ("sorgu", "abstract_key"),
        "TWILIO_SID": ("twilio", "sid"),
        "TWILIO_TOKEN": ("twilio", "token"),
        "VONAGE_KEY": ("vonage", "api_key"),
        "VONAGE_SECRET": ("vonage", "api_secret"),
        "TELNYX_KEY": ("telnyx", "api_key"),
        "VSIM_WEBHOOK_URL": ("vsim", "webhook_url"),
    }
    for env, (sec, key) in env_map.items():
        v = os.environ.get(env)
        if v:
            cfg.setdefault(sec, {})[key] = v
    return cfg


def config_ornegini_yaz():
    ornek = {
        "sorgu": {"numverify_key": "", "abstract_key": ""},
        "twilio": {"sid": "", "token": ""},
        "vonage": {"api_key": "", "api_secret": ""},
        "telnyx": {"api_key": ""},
        "vsim": {"webhook_url": "https://SENIN-TUNELIN.ngrok-free.app"},
        "flood": {"esik": 20, "timeout": 20},
    }
    if not os.path.exists(CONFIG_DOSYA):
        with open(CONFIG_DOSYA, "w", encoding="utf-8") as f:
            json.dump(ornek, f, ensure_ascii=False, indent=2)
        print(f"{R.Y}[+] {CONFIG_DOSYA} oluşturuldu — API anahtarlarını buraya yaz.{R.R}")
    else:
        print(f"{R.S}[i] {CONFIG_DOSYA} zaten var.{R.R}")


def izin_listesi_hazirla():
    if not os.path.exists(IZINLI_DOSYA):
        with open(IZINLI_DOSYA, "w", encoding="utf-8") as f:
            f.write("# Flood testi hedefleri — her satıra bir numara (E.164)\n")
            f.write("# +905321234567\n")
        print(f"{R.Y}[+] {IZINLI_DOSYA} oluşturuldu. Test edeceğin numarayı buraya ekle.{R.R}")
    else:
        print(f"{R.S}[i] {IZINLI_DOSYA} zaten var.{R.R}")


def izinli_mi(numara):
    hedef = sadece_rakam(numara)
    if not os.path.exists(IZINLI_DOSYA):
        return False
    with open(IZINLI_DOSYA, encoding="utf-8") as f:
        for satir in f:
            s = satir.strip()
            if not s or s.startswith("#"):
                continue
            if sadece_rakam(s) == hedef:
                return True
    return False


# ═══════════════════════════════════════════════════
#  VERİTABANI (SQLite)
# ═══════════════════════════════════════════════════
def db_baglan():
    con = sqlite3.connect(DB_DOSYA)
    con.execute("""CREATE TABLE IF NOT EXISTS numaralar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numara TEXT UNIQUE, etiket TEXT, ulke TEXT,
        notlar TEXT, tarih TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS loglar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zaman TEXT, olay TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gelen_mesajlar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zaman TEXT, saglayici TEXT,
        kimden TEXT, kime TEXT, metin TEXT, ham TEXT)""")
    return con


def log_yaz(olay):
    try:
        con = db_baglan()
        con.execute("INSERT INTO loglar(zaman, olay) VALUES(?,?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), olay))
        con.commit()
        con.close()
    except Exception:
        pass


def rapor_yaz(tur, baslik, satirlar):
    os.makedirs(RAPOR_KLASORU, exist_ok=True)
    dosya = os.path.join(RAPOR_KLASORU,
                         f"{tur}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(f"# {baslik}\n\n")
        f.write("\n".join(satirlar))
    return dosya


# ═══════════════════════════════════════════════════
#  ÜLKE VERİTABANI  (ülke: (ülke kodu, ulusal hane))
#  Kaynak: ITU E.164 (kamuya açık)
# ═══════════════════════════════════════════════════
ULKE_DB = {
    "Türkiye": ("+90", 10), "ABD": ("+1", 10), "Kanada": ("+1", 10),
    "Birleşik Krallık": ("+44", 10), "Almanya": ("+49", 11), "Fransa": ("+33", 9),
    "İtalya": ("+39", 10), "İspanya": ("+34", 9), "Portekiz": ("+351", 9),
    "Hollanda": ("+31", 9), "Belçika": ("+32", 9), "İsviçre": ("+41", 9),
    "Avusturya": ("+43", 10), "İsveç": ("+46", 9), "Norveç": ("+47", 8),
    "Danimarka": ("+45", 8), "Finlandiya": ("+358", 9), "İzlanda": ("+354", 7),
    "İrlanda": ("+353", 9), "Polonya": ("+48", 9), "Çekya": ("+420", 9),
    "Slovakya": ("+421", 9), "Macaristan": ("+36", 9), "Romanya": ("+40", 9),
    "Bulgaristan": ("+359", 9), "Yunanistan": ("+30", 10), "Sırbistan": ("+381", 9),
    "Hırvatistan": ("+385", 9), "Slovenya": ("+386", 9), "Bosna Hersek": ("+387", 8),
    "Kuzey Makedonya": ("+389", 8), "Karadağ": ("+382", 8), "Kosova": ("+383", 8),
    "Arnavutluk": ("+355", 9), "Ukrayna": ("+380", 9), "Rusya": ("+7", 10),
    "Belarus": ("+375", 9), "Litvanya": ("+370", 8), "Letonya": ("+371", 8),
    "Estonya": ("+372", 8), "Moldova": ("+373", 8), "Gürcistan": ("+995", 9),
    "Ermenistan": ("+374", 8), "Azerbaycan": ("+994", 9), "Kazakistan": ("+7", 10),
    "Özbekistan": ("+998", 9), "Kırgızistan": ("+996", 9), "Tacikistan": ("+992", 9),
    "Türkmenistan": ("+993", 8), "Moğolistan": ("+976", 8), "Çin": ("+86", 11),
    "Hong Kong": ("+852", 8), "Makao": ("+853", 8), "Tayvan": ("+886", 9),
    "Japonya": ("+81", 10), "Güney Kore": ("+82", 10), "Kuzey Kore": ("+850", 8),
    "Hindistan": ("+91", 10), "Pakistan": ("+92", 10), "Bangladeş": ("+880", 10),
    "Sri Lanka": ("+94", 10), "Nepal": ("+977", 10), "Bhutan": ("+975", 8),
    "Maldivler": ("+960", 7), "Afganistan": ("+93", 9), "İran": ("+98", 10),
    "Irak": ("+964", 10), "Suriye": ("+963", 9), "Lübnan": ("+961", 8),
    "Ürdün": ("+962", 9), "İsrail": ("+972", 9), "Suudi Arabistan": ("+966", 9),
    "BAE": ("+971", 9), "Katar": ("+974", 8), "Kuveyt": ("+965", 8),
    "Bahreyn": ("+973", 8), "Umman": ("+968", 8), "Yemen": ("+967", 9),
    "Endonezya": ("+62", 10), "Malezya": ("+60", 10), "Singapur": ("+65", 8),
    "Tayland": ("+66", 9), "Vietnam": ("+84", 10), "Filipinler": ("+63", 10),
    "Myanmar": ("+95", 10), "Kamboçya": ("+855", 9), "Laos": ("+856", 9),
    "Brunei": ("+673", 7), "Doğu Timor": ("+670", 8), "Avustralya": ("+61", 9),
    "Yeni Zelanda": ("+64", 10), "Papua Yeni Gine": ("+675", 8), "Fiji": ("+679", 7),
    "Samoa": ("+685", 7), "Tonga": ("+676", 5), "Vanuatu": ("+678", 7),
    "Solomon Adaları": ("+677", 7), "Mısır": ("+20", 10), "Fas": ("+212", 9),
    "Cezayir": ("+213", 9), "Tunus": ("+216", 8), "Libya": ("+218", 9),
    "Sudan": ("+249", 9), "Güney Sudan": ("+211", 9), "Etiyopya": ("+251", 9),
    "Kenya": ("+254", 9), "Nijerya": ("+234", 10), "Gana": ("+233", 9),
    "Güney Afrika": ("+27", 9), "Tanzanya": ("+255", 9), "Uganda": ("+256", 9),
    "Ruanda": ("+250", 9), "Zambiya": ("+260", 9), "Zimbabve": ("+263", 9),
    "Mozambik": ("+258", 9), "Angola": ("+244", 9), "Namibya": ("+264", 9),
    "Botsvana": ("+267", 8), "Senegal": ("+221", 9), "Fildişi Sahili": ("+225", 10),
    "Kamerun": ("+237", 9), "Kongo DC": ("+243", 9), "Kongo": ("+242", 9),
    "Gabon": ("+241", 8), "Nijer": ("+227", 8), "Mali": ("+223", 8),
    "Burkina Faso": ("+226", 8), "Çad": ("+235", 8), "Moritanya": ("+222", 8),
    "Somali": ("+252", 8), "Cibuti": ("+253", 6), "Eritre": ("+291", 7),
    "Liberya": ("+231", 7), "Sierra Leone": ("+232", 8), "Gine": ("+224", 9),
    "Togo": ("+228", 8), "Benin": ("+229", 8), "Madagaskar": ("+261", 9),
    "Mauritius": ("+230", 8), "Seyşeller": ("+248", 7), "Malavi": ("+265", 9),
    "Lesotho": ("+266", 8), "Esvatini": ("+268", 8), "Arjantin": ("+54", 10),
    "Brezilya": ("+55", 11), "Şili": ("+56", 9), "Kolombiya": ("+57", 10),
    "Peru": ("+51", 9), "Venezuela": ("+58", 10), "Ekvador": ("+593", 9),
    "Bolivya": ("+591", 8), "Paraguay": ("+595", 9), "Uruguay": ("+598", 8),
    "Meksika": ("+52", 10), "Guatemala": ("+502", 8), "Honduras": ("+504", 8),
    "El Salvador": ("+503", 8), "Nikaragua": ("+505", 8), "Kosta Rika": ("+506", 8),
    "Panama": ("+507", 8), "Küba": ("+53", 8), "Dominik Cum.": ("+1", 10),
    "Porto Riko": ("+1", 10), "Jamaika": ("+1", 10), "Bahamalar": ("+1", 10),
    "Barbados": ("+1", 10), "Trinidad Tobago": ("+1", 10), "Lüksemburg": ("+352", 9),
    "Monako": ("+377", 8), "Lihtenştayn": ("+423", 7), "Andorra": ("+376", 6),
    "San Marino": ("+378", 8), "Vatikan": ("+39", 10), "Malta": ("+356", 8),
    "Kıbrıs": ("+357", 8), "Grönland": ("+299", 6), "Faroe Adaları": ("+298", 6),
}

# VSIM sağlayıcıları için ISO ülke kodları
ULKE_ISO = {
    "Türkiye": "TR", "ABD": "US", "Kanada": "CA", "Birleşik Krallık": "GB",
    "Almanya": "DE", "Fransa": "FR", "İtalya": "IT", "İspanya": "ES",
    "Hollanda": "NL", "Belçika": "BE", "İsviçre": "CH", "Avusturya": "AT",
    "İsveç": "SE", "Norveç": "NO", "Danimarka": "DK", "Finlandiya": "FI",
    "İrlanda": "IE", "Polonya": "PL", "Portekiz": "PT", "Yunanistan": "GR",
    "Rusya": "RU", "Ukrayna": "UA", "Romanya": "RO", "Çekya": "CZ",
    "Macaristan": "HU", "Bulgaristan": "BG", "Hırvatistan": "HR",
    "Sırbistan": "RS", "Slovenya": "SI", "Slovakya": "SK", "Litvanya": "LT",
    "Letonya": "LV", "Estonya": "EE", "Gürcistan": "GE", "Azerbaycan": "AZ",
    "Ermenistan": "AM", "Kazakistan": "KZ", "Özbekistan": "UZ",
    "Çin": "CN", "Hong Kong": "HK", "Japonya": "JP", "Güney Kore": "KR",
    "Hindistan": "IN", "Pakistan": "PK", "Endonezya": "ID", "Malezya": "MY",
    "Singapur": "SG", "Tayland": "TH", "Vietnam": "VN", "Filipinler": "PH",
    "Avustralya": "AU", "Yeni Zelanda": "NZ", "Mısır": "EG", "Fas": "MA",
    "Nijerya": "NG", "Güney Afrika": "ZA", "Kenya": "KE", "İsrail": "IL",
    "BAE": "AE", "Suudi Arabistan": "SA", "Katar": "QA", "Kuveyt": "KW",
    "Ürdün": "JO", "Lübnan": "LB", "Meksika": "MX", "Brezilya": "BR",
    "Arjantin": "AR", "Şili": "CL", "Kolombiya": "CO", "Peru": "PE",
    "Venezuela": "VE", "Malta": "MT", "Kıbrıs": "CY", "İzlanda": "IS",
}

# NANP (+1) paylaşımlı bölge kodları
NANP_BOLGE = {
    "242": "Bahamalar", "246": "Barbados", "264": "Anguilla",
    "268": "Antigua ve Barbuda", "284": "Britanya Virjin Adaları",
    "345": "Cayman Adaları", "441": "Bermuda", "473": "Grenada",
    "649": "Turks ve Caicos", "664": "Montserrat", "721": "Sint Maarten",
    "758": "Saint Lucia", "767": "Dominika", "784": "Saint Vincent",
    "809": "Dominik Cum.", "829": "Dominik Cum.", "849": "Dominik Cum.",
    "868": "Trinidad ve Tobago", "869": "Saint Kitts ve Nevis",
    "876": "Jamaika", "939": "Porto Riko",
}
UCRETSIZ_ONEK = {"800", "833", "844", "855", "866", "877", "888"}

# Bazı ülkeler için mobil önekler (kamuya açık bilgi)
MOBIL_ONEKLER = {
    "Türkiye": ["501", "505", "506", "507", "530", "531", "532", "533", "534",
                "535", "536", "537", "538", "539", "540", "541", "542", "543",
                "544", "545", "546", "547", "548", "549", "551", "552", "553",
                "554", "555", "556", "557", "558", "559"],
    "ABD": ["201", "202", "212", "213", "305", "310", "312", "415", "646",
            "702", "718", "773", "786", "917", "929"],
    "Birleşik Krallık": ["70", "71", "72", "73", "74", "75", "77", "78", "79"],
    "Almanya": ["151", "152", "155", "157", "159", "160", "162", "163", "170",
                "171", "172", "173", "174", "175", "176", "177", "178", "179"],
    "Fransa": ["6", "7"],
    "Rusya": ["900", "901", "902", "903", "904", "905", "906", "908", "909",
              "910", "911", "912", "913", "914", "915", "916", "917", "918",
              "919", "920", "921", "922", "923", "924", "925", "926", "927",
              "928", "929", "930", "931", "932", "933", "934", "936", "937",
              "938", "939", "950", "951", "952", "953", "954", "955", "956",
              "958", "960", "961", "962", "963", "964", "965", "966", "967",
              "968", "969", "980", "981", "982", "983", "984", "985", "986",
              "987", "988", "989", "991", "992", "993", "994", "995", "996",
              "997", "999"],
    "Hindistan": ["6", "7", "8", "9"],
    "Brezilya": ["11", "21", "31", "41", "51", "61", "71", "81", "91", "92",
                 "93", "94", "95", "96", "97", "98", "99"],
}

# Türkiye operatör eşlemesi (BTK numara planı — kamuya açık)
TR_OPERATOR = {
    "501": "Turkcell (IoT/Veri)", "505": "Vodafone", "506": "Vodafone",
    "507": "Türk Telekom (Veri)",
    "530": "Turkcell", "531": "Turkcell", "532": "Turkcell", "533": "Turkcell",
    "534": "Turkcell", "535": "Turkcell", "536": "Turkcell", "537": "Turkcell",
    "538": "Turkcell", "539": "Turkcell",
    "540": "Vodafone", "541": "Vodafone", "542": "Vodafone", "543": "Vodafone",
    "544": "Vodafone", "545": "Vodafone", "546": "Vodafone", "547": "Vodafone",
    "548": "Vodafone", "549": "Vodafone",
    "550": "Türk Telekom", "551": "Türk Telekom", "552": "Türk Telekom",
    "553": "Türk Telekom", "554": "Türk Telekom", "555": "Türk Telekom",
    "556": "Türk Telekom", "557": "Türk Telekom", "558": "Türk Telekom",
    "559": "Türk Telekom",
}

# ═══════════════════════════════════════════════════
#  YARDIMCILAR
# ═══════════════════════════════════════════════════
def sadece_rakam(s):
    return re.sub(r"\D", "", s or "")


def e164_norm(numara):
    """Girdiyi E.164'e çevirir. '0' ulusal öneki varsayılan ülkeyle birleşir."""
    r = sadece_rakam(numara)
    if not r:
        return ""
    if r.startswith("00"):
        r = r[2:]
    elif r.startswith("0"):
        r = ULKE_DB[DEFAULT_ULKE][0][1:] + r[1:]
    return "+" + r


def ulke_bul(numara):
    """En uzun eşleşen ülke kodunu bulur (+420 vs +42 çakışmaları güvenli)."""
    r = sadece_rakam(numara)
    if not r:
        return None
    eslesen = [(ad, kod) for ad, (kod, _) in ULKE_DB.items() if r.startswith(kod[1:])]
    if not eslesen:
        return None
    kod = sorted(eslesen, key=lambda x: (len(x[1]), x[1]), reverse=True)[0][1]
    ulkeler = [ad for ad, k in eslesen if k == kod]
    return kod, ulkeler


def tip_tahmin(ulusal, ulke_adi):
    """Mobil öneklerine göre hat tipi tahmini (API yoksa yerel DB)."""
    if ulke_adi == "ABD" and len(ulusal) >= 3:
        pre = ulusal[:3]
        if pre in UCRETSIZ_ONEK:
            return "Ücretsiz (Toll-Free)"
    onekler = MOBIL_ONEKLER.get(ulke_adi, [])
    if not onekler:
        return "Bilinmiyor (API ile doğrula)"
    for pre in sorted(onekler, key=len, reverse=True):
        if ulusal.startswith(pre):
            return "Mobil"
    return "Sabit/Diğer"


def operator_bul(ulusal, ulke_adi):
    if ulke_adi == "Türkiye" and len(ulusal) >= 3:
        return TR_OPERATOR.get(ulusal[:3], "Bilinmiyor")
    return "Yerel DB yok — canlı sorgu API'si kullan"


def cprint(metin, renk=RESET, son="\n", kalin=False):
    """Renkli, isteğe bağlı kalın yazdırma."""
    stil = renk
    if kalin:
        stil = BOLD + renk
    print(f"{stil}{metin}{RESET}", end=son)


def http_istek(url, metot="GET", veri=None, baslik=None, auth=None, timeout=20):
    """Sıfır bağımlılık HTTP istemcisi (requests gerekmez)."""
    baslik = dict(baslik or {})
    body = None
    if veri is not None:
        if isinstance(veri, dict):
            if metot == "GET":
                ayrac = "&" if "?" in url else "?"
                url += ayrac + urllib.parse.urlencode(veri)
            else:
                body = urllib.parse.urlencode(veri).encode()
                baslik.setdefault("Content-Type", "application/x-www-form-urlencoded")
        elif isinstance(veri, (str, bytes)):
            body = veri.encode() if isinstance(veri, str) else veri
            baslik.setdefault("Content-Type", "application/json")
    if auth:
        tok = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        baslik["Authorization"] = f"Basic {tok}"
    req = urllib.request.Request(url, method=metot, headers=baslik)
    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as y:
            ham = y.read().decode("utf-8", "replace")
            try:
                return y.status, json.loads(ham)
            except Exception:
                return y.status, ham
    except urllib.error.HTTPError as e:
        ham = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(ham)
        except Exception:
            return e.code, ham
    except Exception as e:
        return None, str(e)


# ═══════════════════════════════════════════════════
#  [1] ÜLKE VERİTABANI
# ═══════════════════════════════════════════════════
def ulke_menu():
    print(f"\n{R.B}{R.M}═══ ÜLKE VERİTABANI ({len(ULKE_DB)}+ ülke/bölge) ═══{R.R}")
    print(f"{R.G}Seçenekler: listele / ara / format / ISO kod{R.R}\n")
    sec = input(f"{R.C}[?]{R.R} (l=Listele, a=Ara, f=Format, i=ISO) [l]: ").strip().lower() or "l"
    if sec == "l":
        adlar = sorted(ULKE_DB.keys(), key=lambda x: ULKE_DB[x][0])
        print(f"\n{R.B}{'Ülke':<22}{'Kod':<8}{'Hane':<6}Örnek{R.R}")
        print(f"{R.M}{'─'*55}{R.R}")
        for ad in adlar:
            kod, uzunluk = ULKE_DB[ad]
            print(f"{ad:<22}{kod:<8}{uzunluk:<6}{kod} {'X'*uzunluk}")
        print(f"{R.M}{'─'*55}{R.R}")
        print(f"Toplam: {len(ULKE_DB)} kayıt\n")
    elif sec == "a":
        q = input(f"{R.C}[?]{R.R} Ülke adı veya kod: ").strip().lower()
        sonuclar = [(ad, v) for ad, v in ULKE_DB.items()
                    if q in ad.lower() or q in v[0].lower()]
        if not sonuclar:
            print(f"{R.K}[!] Eşleşme bulunamadı.{R.R}")
        else:
            for ad, (kod, uz) in sonuclar:
                print(f"  {ad:<22} {kod:<8} {uz} hane")
    elif sec == "i":
        q = input(f"{R.C}[?]{R.R} Ülke adı: ").strip()
        if q in ULKE_ISO:
            print(f"{R.Y}{q} → ISO: {ULKE_ISO[q]}{R.R}")
        else:
            benzer = [ad for ad in ULKE_ISO if q.lower() in ad.lower()]
            for ad in benzer[:10]:
                print(f"  {ad:<22} → {ULKE_ISO[ad]}")
            if not benzer:
                print(f"{R.K}[!] ISO eşleşmesi yok.{R.R}")
    else:
        ad = input(f"{R.C}[?]{R.R} Ülke adı: ").strip()
        bilgi = ULKE_DB.get(ad)
        if bilgi:
            print(f"\n{R.Y}{ad}{R.R} → Kod: {bilgi[0]}, Ulusal hane: {bilgi[1]}")
            print(f"  Format: {bilgi[0]} {'X'*bilgi[1]}")
            print(f"  ISO   : {ULKE_ISO.get(ad, '-')}")
        else:
            print(f"{R.K}[!] Ülke bulunamadı.{R.R}")


# ═══════════════════════════════════════════════════
#  [2] TELEFON ANALİZCİSİ  (E.164 + NANP + operatör)
# ═══════════════════════════════════════════════════
def analiz_et(numara):
    print(f"\n{R.M}═══════════ TELEFON ANALİZİ ═══════════{R.R}")
    if not sadece_rakam(numara):
        print(f"{R.K}[!] Geçersiz numara.{R.R}")
        return

    e164 = e164_norm(numara)
    print(f"{R.B}Girdi        :{R.R} {numara}")
    print(f"{R.B}E.164       :{R.R} {R.C}{e164}{R.R}")

    if not re.fullmatch(r"\+[1-9]\d{1,14}", e164):
        print(f"{R.K}[!] E.164 biçimi geçersiz (maks. 15 hane).{R.R}")

    tespit = ulke_bul(e164)
    if not tespit:
        print(f"{R.K}[!] Ülke kodu tanınamadı.{R.R}")
        return
    kod, ulkeler = tespit
    ulke = ulkeler[0]
    beklenen = ULKE_DB[ulke][1]
    ulusal = e164[len(kod):]
    hane = len(ulusal)

    print(f"{R.B}Ülke         :{R.R} {', '.join(ulkeler)}")
    print(f"{R.B}Ülke Kodu    :{R.R} {kod}")
    print(f"{R.B}Ulusal Kısım :{R.R} {ulusal} ({hane} hane)")
    print(f"{R.B}Beklenen     :{R.R} {beklenen} hane → "
          + (f"{R.Y}UYUMLU ✓{R.R}" if hane == beklenen else f"{R.K}UYUMSUZ ✗{R.R}"))

    if kod == "+1" and len(ulusal) >= 3:
        pre3 = ulusal[:3]
        if pre3 in NANP_BOLGE:
            print(f"{R.B}NANP Bölge   :{R.R} {NANP_BOLGE[pre3]}")
        else:
            print(f"{R.B}NANP Bölge   :{R.R} ABD/Kanada (alan kodu {pre3})")

    print(f"{R.B}Hat Tipi     :{R.R} {tip_tahmin(ulusal, ulke)}")
    print(f"{R.B}Operatör     :{R.R} {operator_bul(ulusal, ulke)}")

    if hane != beklenen:
        fark = hane - beklenen
        if ulke == "Türkiye" and fark == -1:
            print(f"{R.S}Öneri: ulusal kısım başına 0 eklenmemiş olabilir → 0{ulusal}{R.R}")
        elif fark < 0:
            print(f"{R.S}Öneri: {abs(fark)} hane eksik.{R.R}")
        else:
            print(f"{R.S}Öneri: {fark} hane fazla — ülke kodu iki kez eklenmiş olabilir.{R.R}")

    if len(ulkeler) > 1:
        print(f"{R.G}[i] {kod} kodu birden çok ülkede kullanılıyor: {', '.join(ulkeler)}{R.R}")

    tam = hane == beklenen
    print(f"{R.M}{'─'*46}{R.R}")
    print(f"{R.B}SONUÇ:{R.R} " + (f"{R.Y}E.164 formatı geçerli ✓{R.R}" if tam
                                else f"{R.K}E.164 formatı geçersiz ✗{R.R}"))
    print(f"{R.G}[i] Format doğrulamasıdır; aktif/taşınmış hattı garanti etmez.{R.R}")
    print(f"{R.G}    Canlı doğrulama için menü 6 (SMS Sorgu).{R.R}\n")


# ═══════════════════════════════════════════════════
#  [3] OTP ÇÖZÜMLEYİCİ  (skorlu, çok dilli)
# ═══════════════════════════════════════════════════
OTP_ANAHTAR = re.compile(
    r"(?:kod|kodu|code|şifre|sifre|doğrulama|dogrulama|onay|pin|otp|verification|"
    r"password|token|parola|şifreniz|sifreniz)[^\dA-Z]{0,6}([A-Z0-9]{4,10})",
    re.IGNORECASE)


def otp_cikar(metin):
    """SMS metninden aday kodları skorlu çıkarır. Kendi test sistemin içindir."""
    sonuc = []
    ust = metin.upper()

    def ekle(kod, skor, aciklama):
        k = re.sub(r"[^A-Z0-9]", "", kod)
        if len(k) < 4 or len(k) > 10:
            return
        if any(x == k for x, _, _ in sonuc):
            return
        # Yıl/date benzeri 4-6 haneli sayıları ele (1900-2100)
        if k.isdigit() and len(k) in (4, 6) and 1900 <= int(k) <= 2100:
            return
        sonuc.append((k, skor, aciklama))

    for m in OTP_ANAHTAR.finditer(ust):
        ekle(m.group(1), 95, "anahtar kelimeli")
    for m in re.finditer(r"(?<!\d)\d{6}(?!\d)", ust):
        ekle(m.group(0), 80, "6 hane")
    for m in re.finditer(r"(?<!\d)\d{5}(?!\d)", ust):
        ekle(m.group(0), 70, "5 hane")
    for m in re.finditer(r"(?<!\d)\d{4}(?!\d)", ust):
        ekle(m.group(0), 60, "4 hane")
    for m in re.finditer(r"\b[A-Z]{1,3}[- ]?\d{4,8}\b", ust):
        ekle(m.group(0), 55, "harf+rakam")

    # Telefon numarası içinde geçen rakam gruplarını adaydan düş
    temiz = re.sub(r"\+?\d[\d\s\-]{7,15}", "", ust)
    sonuc.sort(key=lambda x: (-x[1], x[0]))
    filtrelenen = [k for k, _, _ in sonuc if re.sub(r"[^A-Z0-9]", "", k) not in temiz]
    return filtrelenen or [k for k, _, _ in sonuc]


def otp_menu():
    print(f"\n{R.B}{R.M}═══ OTP ÇÖZÜMLEYİCİ ═══{R.R}")
    print(f"{R.G}Kendi test sisteminden gelen SMS metnini yapıştır, kodu çıkaralım.{R.R}")
    print(f"{R.G}(örnek: 'WhatsApp kodu: 123456. 10 dk geçerli'){R.R}\n")
    metin = input(f"{R.C}[?]{R.R} SMS metni: ").strip()
    if not metin:
        print(f"{R.S}[i] Boş girdi.{R.R}")
        return
    kodlar = otp_cikar(metin)
    print()
    if kodlar:
        print(f"{R.Y}{len(kodlar)} aday kod (olasılık sırasına göre):{R.R}")
        for k in kodlar[:5]:
            print(f"  {R.C}▸ {k}{R.R}")
        print(f"\n{R.Y}En olası: {R.B}{kodlar[0]}{R.R}")
    else:
        print(f"{R.K}[ * ] Platform Kodunuz Bulunamadı{R.R}")
        print(f"{R.G}[i] İpucu: kod 4-10 haneli olmalı ve metinde geçmeli.{R.R}")


# ═══════════════════════════════════════════════════
#  [4] TEST NUMARASI ÜRETİCİ (gerçek değildir, işlemez)
# ═══════════════════════════════════════════════════
def test_numara_uret(ulke_adi, adet=1):
    bilgi = ULKE_DB.get(ulke_adi)
    if not bilgi:
        return []
    kod, uzunluk = bilgi
    sonuclar = []
    for _ in range(adet):
        onekler = MOBIL_ONEKLER.get(ulke_adi, [])
        if onekler:
            bas = random.choice(onekler)
        else:
            bas = str(random.randint(1, 9))
        kalan = uzunluk - len(bas)
        ulusal = bas + "".join(str(random.randint(0, 9)) for _ in range(kalan))
        sonuclar.append((kod, ulusal))
    return sonuclar


def uret_menu():
    print(f"\n{R.B}{R.M}═══ TEST NUMARASI ÜRETİCİ ═══{R.R}")
    print(f"{R.G}[i] Üretilen numaralar TEST VERİSİDİR; hiçbir ağda işlemez.{R.R}")
    ad = input(f"{R.C}[?]{R.R} Ülke adı (örn. Türkiye): ").strip()
    if ad not in ULKE_DB:
        print(f"{R.K}[!] Ülke bulunamadı.{R.R}")
        return
    try:
        adet = min(int(input(f"{R.C}[?]{R.R} Adet (1-50) [5]: ").strip() or "5"), 50)
    except ValueError:
        adet = 5
    kod, _ = ULKE_DB[ad]
    print(f"\n{R.Y}{ad} ({kod}) test numaraları:{R.R}")
    for i, (k, ul) in enumerate(test_numara_uret(ad, adet), 1):
        print(f"  {i:>2}. {R.C}{k} {ul}{R.R}  {R.G}({operator_bul(ul, ad)}){R.R}")
    print(f"\n{R.G}[i] Yalnızca kendi uygulamanın format doğrulama mantığını test eder.{R.R}\n")


# ═══════════════════════════════════════════════════
#  [5] NUMARA HAVUZU (SQLite)
# ═══════════════════════════════════════════════════
def havuz_menu():
    print(f"\n{R.B}{R.M}═══ NUMARA HAVUZU (SQLite) ═══{R.R}")
    print(f"{R.G}Kendi test numaralarını kaydet/listele/ara + işlem logu.{R.R}")
    print(f"{R.G}Veritabanı: {DB_DOSYA}{R.R}\n")
    print("  1. Yeni numara ekle")
    print("  2. Listele")
    print("  3. Sil (indeksle)")
    print("  4. Logları göster")
    print("  5. Ara (ülke/etiket/numara)")
    sec = input(f"{R.C}[?]{R.R} Seçim: ").strip()
    con = db_baglan()

    if sec == "1":
        numara = input(f"{R.C}[?]{R.R} Numara (örn. +905321234567): ").strip()
        etiket = input(f"{R.C}[?]{R.R} Etiket (örn. test-01): ").strip() or "-"
        notlar = input(f"{R.C}[?]{R.R} Not: ").strip()
        e164 = e164_norm(numara)
        tespit = ulke_bul(e164)
        ulke = tespit[1][0] if tespit else "Bilinmiyor"
        try:
            con.execute("INSERT INTO numaralar(numara, etiket, ulke, notlar, tarih) VALUES(?,?,?,?,?)",
                        (e164, etiket, ulke, notlar,
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            con.commit()
            log_yaz(f"EKLENDI: {e164} ({etiket})")
            print(f"{R.Y}[+] Kaydedildi → {e164} [{ulke}]{R.R}")
        except sqlite3.IntegrityError:
            print(f"{R.S}[i] Bu numara zaten kayıtlı.{R.R}")

    elif sec == "2":
        rows = con.execute("SELECT id, numara, etiket, ulke, tarih FROM numaralar ORDER BY id").fetchall()
        if not rows:
            print(f"{R.S}[i] Havuz boş.{R.R}")
        else:
            print(f"\n{R.B}{'#':<4}{'Numara':<20}{'Etiket':<14}{'Ülke':<14}{'Tarih':<20}{R.R}")
            print(f"{R.M}{'─'*70}{R.R}")
            for r in rows:
                print(f"{r[0]:<4}{r[1]:<20}{r[2]:<14}{r[3]:<14}{r[4]:<20}")
            print(f"{R.M}{'─'*70}{R.R}  Toplam: {len(rows)}")

    elif sec == "3":
        try:
            i = int(input(f"{R.C}[?]{R.R} Silinecek indeks: ")) - 1
            row = con.execute("SELECT id, numara FROM numaralar ORDER BY id LIMIT 1 OFFSET ?",
                              (i,)).fetchone()
            if row:
                con.execute("DELETE FROM numaralar WHERE id=?", (row[0],))
                con.commit()
                log_yaz(f"SILINDI: {row[1]}")
                print(f"{R.Y}[-] Silindi: {row[1]}{R.R}")
            else:
                print(f"{R.K}[!] Geçersiz indeks.{R.R}")
        except ValueError:
            print(f"{R.K}[!] Sayı girin.{R.R}")

    elif sec == "4":
        rows = con.execute("SELECT zaman, olay FROM loglar ORDER BY id DESC LIMIT 50").fetchall()
        if not rows:
            print(f"{R.S}[i] Log boş.{R.R}")
        else:
            for z, o in reversed(rows):
                print(f"  {R.G}{z}{R.R}  {o}")

    elif sec == "5":
        q = input(f"{R.C}[?]{R.R} Ara (numara/etiket/ülke): ").strip().lower()
        rows = con.execute(
            "SELECT id, numara, etiket, ulke, tarih FROM numaralar "
            "WHERE numara LIKE ? OR etiket LIKE ? OR ulke LIKE ? ORDER BY id",
            (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        if not rows:
            print(f"{R.S}[i] Eşleşme yok.{R.R}")
        else:
            for r in rows:
                print(f"  {r[0]:<4}{r[1]:<20}{r[2]:<14}{r[3]:<14}{r[4]:<20}")
    con.close()
    print()


# ═══════════════════════════════════════════════════
#  [6] SMS SORGU  (canlı doğrulama — ücretsiz kotalı API'ler)
# ═══════════════════════════════════════════════════
def sorgu_numverify(numara, key):
    st, v = http_istek("http://apilayer.net/api/validate",
                       veri={"access_key": key, "number": numara})
    if st != 200 or not isinstance(v, dict):
        return None, f"API hatası ({st})"
    return v, None


def sorgu_abstract(numara, key):
    st, v = http_istek("https://phonevalidation.abstractapi.com/v1/",
                       veri={"api_key": key, "phone": numara})
    if st != 200 or not isinstance(v, dict):
        return None, f"API hatası ({st})"
    return v, None


def sorgu_goruntule(v, kaynak):
    if not v:
        return
    print(f"\n{R.P}── {kaynak} sonucu ──{R.R}")
    gecerlilik = v.get("valid", v.get("is_valid_number"))
    if gecerlilik is not None:
        print(f"{R.B}Geçerli      :{R.R} " + (f"{R.Y}Evet ✓{R.R}" if gecerlilik else f"{R.K}Hayır ✗{R.R}"))
    for anahtar, etiket in [("country_name", "Ülke"), ("country_code", "Ülke Kodu"),
                            ("location", "Konum"), ("carrier", "Operatör"),
                            ("line_type", "Hat Tipi"), ("line_type_int", "Hat Tipi (int)"),
                            ("international_format", "Int. Format"),
                            ("local_format", "Yerel Format"),
                            ("country_prefix", "Ülke Öneki")]:
        deger = v.get(anahtar)
        if deger is not None and deger != "":
            print(f"{R.B}{etiket:<12}:{R.R} {deger}")


def sorgu_calistir(numara):
    cfg = config_yukle()
    print(f"\n{R.M}═══════════ SMS SORGU (CANLI) ═══════════{R.R}")
    print(f"{R.B}Numara:{R.R} {numara}  ({e164_norm(numara)})\n")

    nv_key = cfg.get("sorgu", {}).get("numverify_key", "")
    ab_key = cfg.get("sorgu", {}).get("abstract_key", "")
    yapildi = 0

    if nv_key:
        v, hata = sorgu_numverify(e164_norm(numara), nv_key)
        if v:
            sorgu_goruntule(v, "Numverify")
            yapildi += 1
        else:
            print(f"{R.K}Numverify: {hata}{R.R}")
    if ab_key:
        v, hata = sorgu_abstract(e164_norm(numara), ab_key)
        if v:
            sorgu_goruntule(v, "Abstract")
            yapildi += 1
        else:
            print(f"{R.K}Abstract: {hata}{R.R}")

    if not yapildi:
        print(f"{R.K}[!] API anahtarı yok veya tüm API'ler hata verdi.{R.R}")
        print(f"{R.S}[i] Ücretsiz anahtar: numverify.com ve abstractapi.com (ayda 100 istek).{R.R}")
        print(f"{R.S}    Anahtarları {CONFIG_DOSYA} içindeki 'sorgu' bölümüne yaz.{R.R}")

    con = db_baglan()
    con.execute("INSERT OR IGNORE INTO numaralar(numara, etiket, ulke, notlar, tarih) VALUES(?,?,?,?,?)",
                (e164_norm(numara), "sorgu", "Bilinmiyor", "canlı sorgu",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()
    log_yaz(f"SORGU: {e164_norm(numara)}")
    print()


def sorgu_menu():
    print(f"\n{R.B}{R.M}═══ SMS SORGU / NUMARA DOĞRULAMA ═══{R.R}")
    print(f"{R.G}Ücretsiz kotalı API'lerle canlı doğrulama (numverify, abstract).{R.R}")
    numara = input(f"{R.C}[?]{R.R} Numara (örn. +905321234567): ").strip()
    if not numara:
        print(f"{R.S}[i] Boş girdi.{R.R}")
        return
    sorgu_calistir(numara)


# ═══════════════════════════════════════════════════
#  [7] SMS FLOOD / RATE-LIMIT TESTİ  (izin listesi zorunlu)
# ═══════════════════════════════════════════════════
def flood_istek_gonder(url, numara, timeout, gecikme, no):
    if gecikme:
        time.sleep(gecikme)
    veri = {
        "phone": numara, "number": numara, "tel": numara,
        "mobile": numara, "msisdn": numara, "telefon": numara,
        "merkez": f"{no:08d}", "sid": random.randint(100000, 999999),
    }
    basla = time.time()
    st, _ = http_istek(url, metot="POST", veri=veri, timeout=timeout)
    gecen = time.time() - basla
    return st, gecen


def flood_basla(url, numara, adet, paralel, timeout, gecikme, dry_run, evet):
    print(f"\n{R.M}═══════ SMS FLOOD / RATE-LIMIT TESTİ ═══════{R.R}")

    if not url.startswith("http"):
        print(f"{R.K}[!] Geçersiz URL: {url}{R.R}")
        return
    if not numara:
        numara = "905551234567"  # sahte test numarası
        print(f"{R.S}[i] Numara verilmedi — sahte test numarası kullanılıyor: {numara}{R.R}")

    if not dry_run and not izinli_mi(numara):
        print(f"{R.K}[!] DUR: {numara} izin listesinde değil.{R.R}")
        print(f"{R.S}    Test hedefini {IZINLI_DOSYA} dosyasına ekle (her satıra bir E.164 numara).{R.R}")
        print(f"{R.S}    Hedef yalnızca KENDİ endpoint'in olmalı. --dry-run ile önizleme yapabilirsin.{R.R}")
        return

    hedef_bilgi = ""
    tespit = ulke_bul(numara)
    if tespit:
        hedef_bilgi = f" ({tespit[1][0]})"
    print(f"{R.B}Hedef URL    :{R.R} {url}")
    print(f"{R.B}Hedef Numara :{R.R} {numara}{hedef_bilgi}")
    print(f"{R.B}Adet         :{R.R} {adet}")
    print(f"{R.B}Paralellik   :{R.R} {paralel}")
    if dry_run:
        print(f"\n{R.Y}[DRY-RUN] Hiçbir istek gönderilmeyecek. Örnek istek:{R.R}")
        print(f"  POST {url}")
        print(f"  phone={numara}&number={numara}&tel={numara}&mobile={numara}")
        print(f"  msisdn={numara}&telefon={numara}&merkez=00000001&sid=123456")
        return

    if not evet:
        try:
            onay = input(f"\n{R.K}[!]{R.R} {adet} istek gönderilecek. Devam? (e/H): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{R.S}İptal edildi.{R.R}")
            return
        if onay != "e":
            print(f"{R.S}İptal edildi.{R.R}")
            return

    print(f"\n{R.G}[*] İstekler gönderiliyor...{R.R}")
    basla = time.time()
    sonuclar = []
    with ThreadPoolExecutor(max_workers=paralel) as havuz:
        gelecekler = [havuz.submit(flood_istek_gonder, url, numara, timeout, gecikme, i + 1)
                      for i in range(adet)]
        for i, g in enumerate(gelecekler, 1):
            st, gecen = g.result()
            sonuclar.append((st, gecen))
            if i % max(1, adet // 20) == 0 or i == adet:
                print(f"  {R.C}{i}/{adet}{R.R} istek tamamlandı...")
    toplam = time.time() - basla

    durumlar = Counter(st if st is not None else "hata" for st, _ in sonuclar)
    sureler = sorted(gecen for _, gecen in sonuclar)
    p50 = sureler[len(sureler) // 2] if sureler else 0
    p95 = sureler[int(len(sureler) * 0.95) - 1] if sureler else 0
    hiz = adet / toplam if toplam > 0 else 0

    print(f"\n{R.M}{'─'*50}{R.R}")
    print(f"{R.B}Toplam Süre  :{R.R} {toplam:.2f} sn  ({hiz:.1f} istek/sn)")
    print(f"{R.B}Başarılı     :{R.R} {R.Y}{durumlar.get(200, 0)}{R.R}")
    print(f"{R.B}p50 / p95    :{R.R} {p50*1000:.0f} ms / {p95*1000:.0f} ms")
    print(f"{R.B}Durum Dağılımı:{R.R} " + ", ".join(f"{k}: {v}" for k, v in durumlar.most_common()))

    engelleme = [k for k in durumlar if k in (429, 503, 401, 403) or k == "hata"]
    ilk_engel = next((i for i, (s, _) in enumerate(sonuclar, 1)
                      if s in (429, 503, 401, 403) or s is None), "-")
    if engelleme:
        print(f"\n{R.Y}[!] Rate-limit/engelleme izleri tespit edildi: {', '.join(map(str, engelleme))}{R.R}")
        print(f"{R.S}    İlk engelleme: istek #{ilk_engel}{R.R}")
        zafiyet = "AÇIK — rate-limit koruması yetersiz" if durumlar.get(200, 0) > adet * 0.5 else \
                  "KISMEN KORUMALI"
        print(f"{R.B}Değerlendirme:{R.R} {zafiyet}")
    else:
        print(f"\n{R.K}[!] Hiç engellenme yok — {adet} isteğin tamamı geçti.{R.R}")
        print(f"{R.B}Değerlendirme:{R.R} {R.K}MUHTEMEL ZAFİYET — rate-limit yok/zayıf{R.R}")

    rapor = [
        f"Hedef URL    : {url}", f"Hedef Numara : {numara}",
        f"Adet         : {adet}", f"Paralellik   : {paralel}",
        f"Toplam Süre  : {toplam:.2f} sn", f"Hız          : {hiz:.1f} istek/sn",
        f"p50 / p95    : {p50*1000:.0f} ms / {p95*1000:.0f} ms",
        f"Durumlar     : " + ", ".join(f"{k}: {v}" for k, v in durumlar.most_common()),
    ]
    dosya = rapor_yaz("flood", f"SMS Flood Testi — {datetime.now().strftime('%Y-%m-%d %H:%M')}", rapor)
    log_yaz(f"FLOOD: {url} hedef={numara} adet={adet} sure={toplam:.1f}sn")
    print(f"\n{R.G}[+] Rapor: {dosya}{R.R}\n")


def flood_menu():
    print(f"\n{R.B}{R.M}═══ SMS FLOOD / RATE-LIMIT TESTİ ═══{R.R}")
    print(f"{R.G}Kendi OTP/SMS endpoint'ini rate-limit zafiyetine karşı test eder.{R.R}")
    print(f"{R.K}[!] Hedef numara izin listesinde olmalı: {IZINLI_DOSYA}{R.R}\n")
    url = input(f"{R.C}[?]{R.R} Endpoint URL (örn. https://kendi-site.com/api/otp/gonder): ").strip()
    if not url.startswith("http"):
        print(f"{R.K}[!] URL http(s) ile başlamalı.{R.R}")
        return
    numara = input(f"{R.C}[?]{R.R} Test numarası (izin listesinden): ").strip()
    try:
        adet = min(int(input(f"{R.C}[?]{R.R} Adet (1-300) [30]: ").strip() or "30"), 300)
        paralel = min(int(input(f"{R.C}[?]{R.R} Paralellik (1-20) [5]: ").strip() or "5"), 20)
    except ValueError:
        adet, paralel = 30, 5
    dry = input(f"{R.C}[?]{R.R} Önce DRY-RUN (ağ trafiği yok) yapılsın mı? (e/H): ").strip().lower() == "e"
    flood_basla(url, numara, adet, paralel, 20, 0.0, dry, False)


# ═══════════════════════════════════════════════════
#  [8] VSIM ALTYAPISI  (sanal numara + gelen SMS webhook)
# ═══════════════════════════════════════════════════
def vsim_twilio_al(cfg, iso):
    sid = cfg.get("twilio", {}).get("sid", "")
    token = cfg.get("twilio", {}).get("token", "")
    webhook = cfg.get("vsim", {}).get("webhook_url", "")
    if not sid or not token:
        print(f"{R.K}[!] Twilio SID/Token eksik. {CONFIG_DOSYA} doldur.{R.R}")
        return
    print(f"{R.G}[*] {iso} için uygun Twilio numarası aranıyor...{R.R}")
    st, v = http_istek(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/AvailablePhoneNumbers/{iso}/Local.json"
        "?SmsEnabled=true", auth=(sid, token))
    if st != 200 or not v.get("available_phone_numbers"):
        msg = v.get("message", v) if isinstance(v, dict) else v
        print(f"{R.K}[!] Numara bulunamadı ({st}): {msg}{R.R}")
        return
    num = v["available_phone_numbers"][0]["phone_number"]
    print(f"{R.Y}[+] Seçilen numara: {num}{R.R}")
    st2, v2 = http_istek(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json",
        metot="POST", veri={"PhoneNumber": num, "SmsUrl": webhook}, auth=(sid, token))
    if st2 in (200, 201):
        print(f"{R.Y}[+] Numara hesabına bağlandı → {num}{R.R}")
        print(f"{R.G}    SMS webhook: {webhook or '(ayarlanmadı — vsim.webhook_url)'}{R.R}")
        log_yaz(f"VSIM_TWILIO: {num}")
    else:
        msg = v2.get("message", v2) if isinstance(v2, dict) else v2
        print(f"{R.K}[!] Bağlama hatası ({st2}): {msg}{R.R}")
        print(f"{R.S}    Twilio hesabında bakiye gerekir. Ayrıntı: https://www.twilio.com/docs/phone-numbers{R.R}")


def vsim_vonage_al(cfg, iso):
    api_key = cfg.get("vonage", {}).get("api_key", "")
    api_secret = cfg.get("vonage", {}).get("api_secret", "")
    if not api_key or not api_secret:
        print(f"{R.K}[!] Vonage anahtarları eksik. {CONFIG_DOSYA} doldur.{R.R}")
        return
    st, v = http_istek("https://rest.nexmo.com/number/search",
                       veri={"api_key": api_key, "api_secret": api_secret,
                             "country": iso, "features": "SMS"})
    if st != 200 or not v.get("numbers"):
        print(f"{R.K}[!] Numara bulunamadı ({st}): {v}{R.R}")
        return
    num = v["numbers"][0]["msisdn"]
    print(f"{R.Y}[+] Seçilen numara: {num}{R.R}")
    st2, v2 = http_istek("https://rest.nexmo.com/number/buy", metot="POST",
                         veri={"api_key": api_key, "api_secret": api_secret,
                               "country": iso, "msisdn": num})
    if st2 == 200:
        print(f"{R.Y}[+] Numara satın alındı → {num}{R.R}")
        print(f"{R.G}    Webhook: 'SMS webhook' URL'ini Vonage panelinden ayarla.{R.R}")
        log_yaz(f"VSIM_VONAGE: {num}")
    else:
        print(f"{R.K}[!] Satın alma hatası ({st2}): {v2}{R.R}")


def vsim_telnyx_al(cfg, iso):
    key = cfg.get("telnyx", {}).get("api_key", "")
    if not key:
        print(f"{R.K}[!] Telnyx anahtarı eksik. {CONFIG_DOSYA} doldur.{R.R}")
        return
    baslik = {"Authorization": f"Bearer {key}"}
    st, v = http_istek(f"https://api.telnyx.com/v2/available_phone_numbers?country_code={iso}&limit=1",
                       baslik=baslik)
    if st != 200 or not v.get("data"):
        print(f"{R.K}[!] Numara bulunamadı ({st}): {v}{R.R}")
        return
    num = v["data"][0]["phone_number"]
    print(f"{R.Y}[+] Seçilen numara: {num}{R.R}")
    st2, v2 = http_istek("https://api.telnyx.com/v2/number_orders", metot="POST",
                         veri=json.dumps({"phone_numbers": [{"phone_number": num}],
                                          "customer_reference": "tf-tool"}),
                         baslik={**baslik, "Content-Type": "application/json"})
    if st2 in (200, 201):
        print(f"{R.Y}[+] Numara sipariş edildi → {num}{R.R}")
        log_yaz(f"VSIM_TELNYX: {num}")
    else:
        print(f"{R.K}[!] Sipariş hatası ({st2}): {v2}{R.R}")


class MesajHandler(BaseHTTPRequestHandler):
    def _kaydet(self, saglayici, kimden, kime, metin, ham):
        con = db_baglan()
        con.execute("INSERT INTO gelen_mesajlar(zaman, saglayici, kimden, kime, metin, ham) VALUES(?,?,?,?,?,?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     saglayici, kimden, kime, metin, ham))
        con.commit()
        con.close()
        log_yaz(f"SMS_GELDI: {kimden} → {kime} ({saglayici})")
        print(f"\n{R.P}┌─ GELEN SMS ({saglayici}) ─────────────{R.R}")
        print(f"{R.P}│{R.R} {R.B}Kimden:{R.R} {kimden}")
        print(f"{R.P}│{R.R} {R.B}Kime  :{R.R} {kime}")
        print(f"{R.P}│{R.R} {R.B}Metin :{R.R} {metin}")
        kodlar = otp_cikar(metin)
        if kodlar:
            print(f"{R.P}│{R.R} {R.Y}OTP adayı: {kodlar[0]}{R.R}")
        print(f"{R.P}└──────────────────────────────{R.R}")

    def do_POST(self):
        uzunluk = int(self.headers.get("Content-Length", 0) or 0)
        ham = self.rfile.read(uzunluk).decode("utf-8", "replace")
        ct = self.headers.get("Content-Type", "")
        saglayici, kimden, kime, metin = "genel", "", "", ""
        try:
            if "form" in ct:
                veri = urllib.parse.parse_qs(ham)
                kimden = veri.get("From", [""])[0]
                kime = veri.get("To", [""])[0]
                metin = veri.get("Body", [""])[0]
                saglayici = "twilio"
            else:
                j = json.loads(ham)
                if "msisdn" in j:
                    saglayici = "vonage"
                    kimden = j.get("msisdn", "")
                    kime = j.get("to", "")
                    metin = j.get("text", "")
                elif j.get("data", {}).get("payload"):
                    saglayici = "telnyx"
                    p = j["data"]["payload"]
                    kimden = p.get("from", "")
                    kime = p.get("to", "")
                    metin = p.get("text", "")
                elif j.get("from") or j.get("Body"):
                    saglayici = "genel"
                    kimden = j.get("from", "")
                    kime = j.get("to", "")
                    metin = j.get("Body", j.get("body", ""))
        except Exception as e:
            print(f"{R.K}[!] Webhook ayrıştırma hatası: {e}{R.R}")
        self._kaydet(saglayici, kimden, kime, metin, ham)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TelefonIstihbarat VSIM webhook aktif. POST ile SMS bildirimi bekleniyor.")

    def log_message(self, *a):
        pass


def vsim_webhook(port):
    print(f"\n{R.M}═══ VSIM WEBHOOK DİNLEYİCİ ═══{R.R}")
    print(f"{R.G}[*] Gelen SMS webhook'ları için dinleniyor: 0.0.0.0:{port}{R.R}")
    print(f"{R.S}    İnternetten erişim için bir tünel aç:{R.R}")
    print(f"{R.C}    ngrok http {port}   (veya: cloudflared tunnel --url http://localhost:{port}){R.R}")
    print(f"{R.S}    Tünel URL'ini {CONFIG_DOSYA} → vsim.webhook_url'e yaz.{R.R}")
    print(f"{R.S}    Sonra sağlayıcı paneline SMS webhook olarak ekle.{R.R}")
    print(f"{R.G}    Ctrl+C ile durdur.{R.R}\n")
    try:
        sunucu = ThreadingHTTPServer(("0.0.0.0", port), MesajHandler)
        sunucu.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{R.S}Webhook dinleyici durduruldu.{R.R}")


def vsim_mesajlar():
    con = db_baglan()
    rows = con.execute("SELECT zaman, saglayici, kimden, kime, metin FROM gelen_mesajlar ORDER BY id DESC LIMIT 30").fetchall()
    con.close()
    if not rows:
        print(f"{R.S}[i] Henüz gelen mesaj yok.{R.R}")
        return
    print(f"\n{R.B}{'Zaman':<20}{'Sağlayıcı':<10}{'Kimden':<18}{'Kime':<18}Metin{R.R}")
    print(f"{R.M}{'─'*90}{R.R}")
    for z, sag, kim, kime, metin in rows:
        print(f"{z:<20}{sag:<10}{kim:<18}{kime:<18}{metin[:40]}")


def vsim_menu():
    print(f"\n{R.B}{R.M}═══ VSIM ALTYAPISI ═══{R.R}")
    print(f"{R.G}1. Numara satın al (Twilio / Vonage / Telnyx){R.R}")
    print(f"{R.G}2. Webhook dinleyici başlat (gelen SMS al){R.R}")
    print(f"{R.G}3. Gelen mesajları listele{R.R}")
    sec = input(f"{R.C}[?]{R.R} Seçim: ").strip()
    cfg = config_yukle()

    if sec == "1":
        print("\n  1. Twilio\n  2. Vonage\n  3. Telnyx")
        p = input(f"{R.C}[?]{R.R} Sağlayıcı: ").strip()
        iso = input(f"{R.C}[?]{R.R} Ülke ISO kodu [US]: ").strip().upper() or "US"
        if p == "1":
            vsim_twilio_al(cfg, iso)
        elif p == "2":
            vsim_vonage_al(cfg, iso)
        elif p == "3":
            vsim_telnyx_al(cfg, iso)
        else:
            print(f"{R.K}[!] Geçersiz seçim.{R.R}")
    elif sec == "2":
        try:
            port = int(input(f"{R.C}[?]{R.R} Port [8080]: ").strip() or "8080")
        except ValueError:
            port = 8080
        vsim_webhook(port)
    elif sec == "3":
        vsim_mesajlar()
    else:
        print(f"{R.K}[!] Geçersiz seçim.{R.R}")


# ═══════════════════════════════════════════════════
#  [9] GSM MODEM SMS GÖNDERİMİ  (kendi modemin; pyserial)
# ═══════════════════════════════════════════════════
def modem_gonder(port, numara, mesaj, baud=115200):
    try:
        import serial
    except ImportError:
        print(f"{R.K}[!] pyserial gerekli: pip install pyserial{R.R}")
        return False
    print(f"{R.G}[*] Modem bağlanıyor: {port} @ {baud}...{R.R}")
    try:
        s = serial.Serial(port, baud, timeout=5)

        def at(komut, bekle=None, sure=5):
            s.write((komut + "\r").encode())
            s.flush()
            if bekle:
                return s.read_until(bekle.encode(), sure).decode("utf-8", "replace")
            time.sleep(1)
            return s.read(256).decode("utf-8", "replace")

        cevap = at("AT")
        if "OK" not in cevap:
            print(f"{R.K}[!] Modem yanıt vermiyor: {cevap!r}{R.R}")
            s.close()
            return False
        at("AT+CMGF=1")
        cevap = at(f'AT+CMGS="{numara}"', ">")
        if ">" not in cevap:
            print(f"{R.K}[!] CMGS hazır değil: {cevap!r}{R.R}")
            s.close()
            return False
        s.write((mesaj + "\x1a").encode())
        s.flush()
        sonuc = s.read_until(b"+CMGS:", 15)
        s.close()
        if sonuc:
            print(f"{R.Y}[+] SMS gönderildi → {numara}{R.R}")
            log_yaz(f"MODEM_SMS: {numara}")
            return True
        print(f"{R.K}[!] Gönderim zaman aşımı. Modem +CMGS onayı vermedi.{R.R}")
        return False
    except Exception as e:
        print(f"{R.K}[!] Modem hatası: {e}{R.R}")
        return False


def modem_menu():
    print(f"\n{R.B}{R.M}═══ GSM MODEM SMS GÖNDERİMİ ═══{R.R}")
    print(f"{R.G}Kendi GSM modeminle (USB/3G dongle) gerçek SMS gönderir.{R.R}")
    print(f"{R.G}Gereksinim: pip install pyserial{R.R}\n")
    port = input(f"{R.C}[?]{R.R} Seri port [/dev/ttyUSB0]: ").strip() or "/dev/ttyUSB0"
    numara = input(f"{R.C}[?]{R.R} Alıcı numara (E.164): ").strip()
    mesaj = input(f"{R.C}[?]{R.R} Mesaj: ").strip()
    if not numara or not mesaj:
        print(f"{R.K}[!] Numara ve mesaj zorunlu.{R.R}")
        return
    modem_gonder(port, numara, mesaj)


# ═══════════════════════════════════════════════════
#  [10] RAPORLAR & LOGLAR
# ═══════════════════════════════════════════════════
def rapor_menu():
    print(f"\n{R.B}{R.M}═══ RAPORLAR & LOGLAR ═══{R.R}")
    print("  1. Rapor dosyalarını listele")
    print("  2. Son logları göster")
    sec = input(f"{R.C}[?]{R.R} Seçim: ").strip()
    if sec == "1":
        if not os.path.isdir(RAPOR_KLASORU):
            print(f"{R.S}[i] Rapor yok.{R.R}")
            return
        dosyalar = sorted(os.listdir(RAPOR_KLASORU), reverse=True)
        if not dosyalar:
            print(f"{R.S}[i] Rapor yok.{R.R}")
            return
        for i, d in enumerate(dosyalar, 1):
            print(f"  {i:>2}. {d}")
        try:
            i = int(input(f"\n{R.C}[?]{R.R} Görüntüle (0=çık): ")) - 1
            if 0 <= i < len(dosyalar):
                with open(os.path.join(RAPOR_KLASORU, dosyalar[i]), encoding="utf-8") as f:
                    print(f"\n{R.G}{f.read()}{R.R}")
        except (ValueError, IndexError):
            pass
    elif sec == "2":
        con = db_baglan()
        rows = con.execute("SELECT zaman, olay FROM loglar ORDER BY id DESC LIMIT 30").fetchall()
        con.close()
        if not rows:
            print(f"{R.S}[i] Log boş.{R.R}")
        else:
            for z, o in reversed(rows):
                print(f"  {R.G}{z}{R.R}  {o}")
    print()


# ═══════════════════════════════════════════════════
#  SELFTEST — altyapının kendi kendini sınaması
# ═══════════════════════════════════════════════════
def selftest():
    print(f"\n{R.M}═══════ ALTYAPI SELFTEST ═══════{R.R}")
    testler = []
    testler.append(("e164_norm (0532...)", e164_norm("05321234567") == "+905321234567"))
    testler.append(("e164_norm (00 öneki)", e164_norm("00905321234567") == "+905321234567"))
    testler.append(("ulke_bul (+90)", ulke_bul("+905321234567") == ("+90", ["Türkiye"])))
    testler.append(("ulke_bul (+44)", ulke_bul("+447700900123")[0] == "+44"))
    testler.append(("ulke_bul (+420 çakışma)", ulke_bul("+420123456789")[0] == "+420"))
    testler.append(("NANP (+1 Karayip)", NANP_BOLGE.get("876") == "Jamaika"))
    testler.append(("operatör (532)", operator_bul("5321234567", "Türkiye") == "Turkcell"))
    testler.append(("tip_tahmin (TR mobil)", tip_tahmin("5321234567", "Türkiye") == "Mobil"))
    testler.append(("otp_cikar (anahtar kelime)", otp_cikar("WhatsApp kodu: 123456")[0] == "123456"))
    testler.append(("otp_cikar (İngilizce)", otp_cikar("Your code is 482913")[0] == "482913"))
    testler.append(("otp_cikar (yıl filtresi)", "2026" not in otp_cikar("Geçerlilik: 2026")))

    con = db_baglan()
    try:
        con.execute("INSERT OR REPLACE INTO numaralar(numara, etiket, ulke, notlar, tarih) VALUES(?,?,?,?,?)",
                    ("+905559998877", "selftest", "Türkiye", "", "now"))
        con.commit()
        n = con.execute("SELECT COUNT(*) FROM numaralar WHERE etiket='selftest'").fetchone()[0]
        con.execute("DELETE FROM numaralar WHERE etiket='selftest'")
        con.commit()
        testler.append(("SQLite havuz yaz/oku/sil", n == 1))
    except Exception as e:
        testler.append(("SQLite havuz yaz/oku/sil", f"HATA: {e}"))
    con.close()

    basarili = sum(1 for _, s in testler if s is True)
    print(f"\n{R.B}{'TEST':<42}{'SONUÇ':<10}{R.R}")
    print(f"{R.M}{'─'*54}{R.R}")
    for ad, sonuc in testler:
        if sonuc is True:
            print(f"{ad:<42}{R.Y}PASS ✓{R.R}")
        else:
            print(f"{ad:<42}{R.K}FAIL ✗ ({sonuc}){R.R}")
    print(f"{R.M}{'─'*54}{R.R}")
    print(f"{R.B}Toplam: {basarili}/{len(testler)} test geçti{R.R}")
    if basarili == len(testler):
        print(f"{R.Y}[+] Altyapı sağlıklı — aracı kullanabilirsin.{R.R}")
    else:
        print(f"{R.K}[!] Bazı testler geçemedi. Ortamı kontrol et.{R.R}")
    print()


# ═══════════════════════════════════════════════════
#  ANA MENÜ
# ═══════════════════════════════════════════════════
def ana_menu():
    while True:
        print(BANNER)
        c = R.M
        W = 62
        print(c + "┌" + "─" * W + "┐" + R.R)
        print(c + "│" + R.R + R.B + R.S + " ANA MENÜ".ljust(W) + R.R + c + "│" + R.R)
        print(c + "├" + "─" * W + "┤" + R.R)
        satirlar = [
            (" [1]", " Ülke Veritabanı & Numara Formatları", R.C),
            (" [2]", " Telefon Analizcisi (E.164 + NANP + Operatör)", R.C),
            (" [3]", " OTP Çözümleyici (SMS metninden kod)", R.C),
            (" [4]", " Test Numarası Üretici", R.C),
            (" [5]", " Numara Havuzu Yöneticisi (SQLite + Log)", R.C),
            (" [6]", " SMS Sorgu — Canlı Numara Doğrulama API'leri", R.C),
            (" [7]", " SMS Flood / Rate-Limit Testi (izin listesi zorunlu)", R.S),
            (" [8]", " VSIM Altyapısı (sanal numara + webhook dinle)", R.C),
            (" [9]", " GSM Modem ile Gerçek SMS Gönder", R.C),
            (" [10]", " Raporlar & Loglar", R.C),
            (" [11]", " Yapılandırma & İzin Listesi", R.C),
            (" [12]", " Altyapı Selftest", R.C),
            (" [0]", " Çıkış", R.K),
        ]
        for num, metin, renk in satirlar:
            duz = num + metin
            icerik = renk + duz + R.R
            print(c + "│" + R.R + icerik + " " * (W - len(duz)) + c + "│" + R.R)
        print(c + "└" + "─" * W + "┘" + R.R)
        try:
            secim = input(f"\n{R.C}[?]{R.R} Seçiminiz: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{R.S}Görüşmek üzere!{R.R}")
            return

        if secim == "1":
            ulke_menu()
        elif secim == "2":
            num = input(f"{R.C}[?]{R.R} Telefon numarası: ").strip()
            if num:
                analiz_et(num)
            else:
                print(f"{R.S}[i] Boş girdi.{R.R}")
        elif secim == "3":
            otp_menu()
        elif secim == "4":
            uret_menu()
        elif secim == "5":
            havuz_menu()
        elif secim == "6":
            sorgu_menu()
        elif secim == "7":
            flood_menu()
        elif secim == "8":
            vsim_menu()
        elif secim == "9":
            modem_menu()
        elif secim == "10":
            rapor_menu()
        elif secim == "11":
            config_ornegini_yaz()
            izin_listesi_hazirla()
        elif secim == "12":
            selftest()
        elif secim == "0":
            print(f"{R.S}Görüşmek üzere!{R.R}")
            return
        else:
            print(f"{R.K}[!] Geçersiz seçim.{R.R}")
        try:
            input(f"\n{R.G}[Enter] devam etmek için...{R.R}")
        except (KeyboardInterrupt, EOFError):
            print()
            return


# ═══════════════════════════════════════════════════
#  KOMUT SATIRI DAĞITICI
# ═══════════════════════════════════════════════════
def alt_komut(komut, args):
    if komut == "sorgu":
        if not args:
            print(f"{R.K}Kullanım: sorgu +905321234567{R.R}")
            return
        sorgu_calistir(args[0])
    elif komut == "flood":
        p = argparse.ArgumentParser(prog="flood")
        p.add_argument("--url", required=True)
        p.add_argument("--numara", default="")
        p.add_argument("--adet", type=int, default=30)
        p.add_argument("--paralel", type=int, default=5)
        p.add_argument("--timeout", type=int, default=20)
        p.add_argument("--gecikme", type=float, default=0.0)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--evet", action="store_true")
        a = p.parse_args(args)
        flood_basla(a.url, a.numara, a.adet, a.paralel,
                    a.timeout, a.gecikme, a.dry_run, a.evet)
    elif komut == "vsim":
        if not args:
            print(f"{R.K}Kullanım: vsim al|webhook|mesajlar{R.R}")
            return
        if args[0] == "webhook":
            port = 8080
            if "--port" in args:
                try:
                    port = int(args[args.index("--port") + 1])
                except (ValueError, IndexError):
                    pass
            vsim_webhook(port)
        elif args[0] == "mesajlar":
            vsim_mesajlar()
        elif args[0] == "al":
            saglayici = "twilio"
            iso = "US"
            if "--provider" in args:
                saglayici = args[args.index("--provider") + 1]
            if "--ulke" in args:
                iso = args[args.index("--ulke") + 1].upper()
            cfg = config_yukle()
            if saglayici == "twilio":
                vsim_twilio_al(cfg, iso)
            elif saglayici == "vonage":
                vsim_vonage_al(cfg, iso)
            elif saglayici == "telnyx":
                vsim_telnyx_al(cfg, iso)
            else:
                print(f"{R.K}Sağlayıcı: twilio | vonage | telnyx{R.R}")
        else:
            print(f"{R.K}Bilinmeyen vsim alt komutu: {args[0]}{R.R}")
    elif komut == "modem":
        if len(args) < 2 or args[0] != "gonder":
            print(f"{R.K}Kullanım: modem gonder +905321234567 \"mesaj\" [--port /dev/ttyUSB0]{R.R}")
            return
        numara = args[1]
        mesaj = args[2] if len(args) > 2 else "test"
        port = "/dev/ttyUSB0"
        if "--port" in args:
            port = args[args.index("--port") + 1]
        modem_gonder(port, numara, mesaj)
    elif komut == "selftest":
        selftest()
    elif komut == "config":
        config_ornegini_yaz()
        izin_listesi_hazirla()
    elif komut == "havuz":
        havuz_menu()
    else:
        print(f"{R.K}Bilinmeyen komut: {komut}{R.R}")


# ═══════════════════════════════════════════════════
#  MAIN — GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════
def main():
    """Programın ana giriş noktası."""
    os.system("cls" if os.name == "nt" else "clear")
    if len(sys.argv) > 1:
        ilk = sys.argv[1]
        if ilk in ("sorgu", "flood", "vsim", "modem", "selftest", "config", "havuz"):
            alt_komut(ilk, sys.argv[2:])
        else:
            print(BANNER)
            analiz_et(" ".join(sys.argv[1:]))
    else:
        main_menu()


def main_menu():
    """Menüyü başlatır; Ctrl+C ve beklenmedik hataları yakalar."""
    try:
        ana_menu()
    except KeyboardInterrupt:
        cprint("\nGüle güle!", GREEN)
    except Exception as e:
        cprint(f"\nKritik hata: {e}", RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
