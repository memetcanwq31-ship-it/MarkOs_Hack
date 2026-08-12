#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kart_dogrulayici.py - Ödeme Formu Kart Doğrulama Test Aracı v2.3 (Menülü + BIN Sorgu)

Özellikler:
  * Luhn algoritması ile kart numarası doğrulama
  * Kart ağı tespiti (Visa, MasterCard, AMEX, Discover, Diners, JCB,
    UnionPay, Maestro, Elo, Troy)
  * Ağa özel uzunluk / CVV / SKT kontrolü
  * 2 KATMAN 4 DERECE analiz:
      Katman 1 (Numara): Luhn, Ağ, Uzunluk, CVV/SKT
      Katman 2 (BIN):    BIN kaydı, Marka uyumu, Kurum, Ülke
  * BIN / Veritabanı sorgulama (yerleşik tablo + opsiyonel binlist.net)
  * Onaylı test kartı rehberi (Stripe + Braintree + PayPal resmî kartları)
  * Dosyadan toplu doğrulama
  * Resmî test BIN'leriyle Luhn-geçerli test kartı üretimi

Kullanım:
  python3 kart_dogrulayici.py                         # Menü
  python3 kart_dogrulayici.py "4242 4242 4242 4242"   # Tek kart
  python3 kart_dogrulayici.py 5555555555554444 --cvv 123 --ay 12 --yil 2028
  python3 kart_dogrulayici.py 4242424242424242 --bin            # BIN analizi
  python3 kart_dogrulayici.py 4242424242424242 --bin --online   # + binlist.net
  python3 kart_dogrulayici.py --test                 # Onaylı test kartları
"""

import argparse
import datetime
import json
import os
import random
import re
import sys
import urllib.request


# ────────────────────────────────────────────────────────────
# 1) ANSI Renkler
# ────────────────────────────────────────────────────────────
class Renk:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    GRI      = "\033[90m"
    KIRMIZI  = "\033[91m"
    YESIL    = "\033[92m"
    SARI     = "\033[93m"
    MAVI     = "\033[94m"
    MOR      = "\033[95m"
    CYAN     = "\033[96m"


BANNER = f"""
{Renk.CYAN} ██╗  ██╗ █████╗ ██████╗ ████████╗{Renk.RESET}
{Renk.CYAN} ██║ ██╔╝██╔══██╗██╔══██╗╚══██╔══╝{Renk.RESET}     {Renk.BOLD}{Renk.MOR}KART DOĞRULAYICI v2.3{Renk.RESET}
{Renk.CYAN} █████╔╝ ███████║██████╔╝   ██║{Renk.RESET}          {Renk.CYAN}Ödeme Formu Test Aracı{Renk.RESET}
{Renk.CYAN} ██╔═██╗ ██╔══██║██╔══██╗   ██║{Renk.RESET}          {Renk.SARI}2 Katman | 4 Derece{Renk.RESET}
{Renk.CYAN} ██║  ██╗██║  ██║██║  ██║   ██║{Renk.RESET}          {Renk.YESIL}BIN Sorgu | Menü | Toplu{Renk.RESET}
{Renk.CYAN} ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝{Renk.RESET}
{Renk.SARI}          Yapımcı: @markos39{Renk.RESET}
{Renk.KIRMIZI}   [!] UYARI: Sorumluluk kullanıcıya aittir.{Renk.RESET}
"""


# ────────────────────────────────────────────────────────────
# 2) Kart ağı tanımları
# ────────────────────────────────────────────────────────────
AG_UZUNLUK = {
    "Visa":             (13, 16, 19),
    "MasterCard":       (16,),
    "American Express": (15,),
    "Discover":         (16, 19),
    "Diners Club":      (14, 16, 19),
    "JCB":              (16, 19),
    "UnionPay":         (16, 19),
    "Maestro":          (12, 13, 14, 15, 16, 17, 18, 19),
    "Elo":              (16,),
    "Troy":             (16,),
}

# Resmî / yaygın TEST BIN'leri (Stripe, Braintree, PayPal test dokümantasyonu)
TEST_BINLER = {
    "Visa":             ["424242", "400000", "411111", "401288", "400005"],
    "MasterCard":       ["555555", "510510", "222300", "520082", "222100"],
    "American Express": ["378282", "371449"],
    "Discover":         ["601111", "601100", "644564"],
    "Diners Club":      ["305693", "385200"],
    "JCB":              ["353011", "356600"],
    "Maestro":          ["675964"],
    "Troy":             ["979202"],
    "UnionPay":         ["620000"],
    "Elo":              ["636368"],
}

# Üreticide fallback olarak kullanılacak genel BIN önekleri
AG_BASLANGICLAR = {
    "Visa":             ["4"],
    "MasterCard":       ["51", "52", "53", "54", "55", "2221", "2222", "2720"],
    "American Express": ["34", "37"],
    "Discover":         ["6011", "65"],
    "Troy":             ["9792"],
    "UnionPay":         ["62"],
    "Diners Club":      ["36", "38", "300"],
    "JCB":              ["3528", "3530", "3589"],
    "Maestro":          ["5018", "5020", "5038", "5893", "6304", "6759"],
    "Elo":              ["636368", "438935"],
}

# Yerleşik (offline) BIN veritabanı — ilk 6 hane → kurum/ülke/tip/marka
BIN_VERITABANI = {
    "424242": {"kurum": "Stripe (resmî test)",        "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "400000": {"kurum": "Stripe (resmî test)",        "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "400005": {"kurum": "Stripe (resmî test)",        "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "411111": {"kurum": "Genel test BIN'i (Visa)",    "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "401288": {"kurum": "Genel test BIN'i (Visa)",    "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "555555": {"kurum": "Genel test BIN'i (MC)",      "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "510510": {"kurum": "Genel test BIN'i (MC)",      "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "222300": {"kurum": "Genel test BIN'i (MC 2-serisi)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "222100": {"kurum": "Genel test BIN'i (MC 2-serisi)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "520082": {"kurum": "Stripe (resmî test)",        "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "378282": {"kurum": "Genel test BIN'i (AMEX)",    "ulke": "US", "tip": "Kredi", "marka": "American Express"},
    "371449": {"kurum": "Genel test BIN'i (AMEX)",    "ulke": "US", "tip": "Kredi", "marka": "American Express"},
    "601111": {"kurum": "Genel test BIN'i (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "601100": {"kurum": "Genel test BIN'i (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "644564": {"kurum": "Genel test BIN'i (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "305693": {"kurum": "Genel test BIN'i (Diners)",  "ulke": "US", "tip": "Kredi", "marka": "Diners Club"},
    "385200": {"kurum": "Genel test BIN'i (Diners)",  "ulke": "US", "tip": "Kredi", "marka": "Diners Club"},
    "353011": {"kurum": "Genel test BIN'i (JCB)",     "ulke": "JP", "tip": "Kredi", "marka": "JCB"},
    "356600": {"kurum": "Genel test BIN'i (JCB)",     "ulke": "JP", "tip": "Kredi", "marka": "JCB"},
    "675964": {"kurum": "Genel test BIN'i (Maestro)", "ulke": "GB", "tip": "Banka", "marka": "Maestro"},
    "979202": {"kurum": "Troy test aralığı (TR)",     "ulke": "TR", "tip": "Kredi", "marka": "Troy"},
}

# Elo BIN'leri (kısmi temsili liste, tespit için)
ELO_BINLER = {
    "636368", "438935", "504175", "451416", "636297", "506699",
    "509048", "509067", "509049", "509069",
    "650031", "650033", "650035", "650051", "650054", "650057",
    "650058", "650059",
}


# ────────────────────────────────────────────────────────────
# 3) Yardımcı fonksiyonlar
# ────────────────────────────────────────────────────────────
def sadece_rakam(numara):
    """Girdiden boşluk, tire vb. temizleyip sadece rakamları döndürür."""
    return re.sub(r"\D", "", numara or "")


def luhn_dogrula(numara):
    """Luhn algoritması ile kart numarasını doğrular (üretmez, kontrol eder)."""
    rakamlar = [int(c) for c in sadece_rakam(numara)]
    if not 13 <= len(rakamlar) <= 19:
        return False
    toplam = 0
    for i, r in enumerate(reversed(rakamlar)):
        if i % 2 == 1:          # sağdan ikinci haneden itibaren ikiye katla
            r *= 2
            if r > 9:
                r -= 9
        toplam += r
    return toplam % 10 == 0


def luhn_kontrol_rakami(prefix):
    """Verilen öneke göre Luhn kontrol hanesini hesaplar (test kartı üretimi için)."""
    rakamlar = [int(c) for c in prefix]
    toplam = 0
    for i, r in enumerate(reversed(rakamlar)):
        if i % 2 == 0:          # kontrol hanesinden hemen önceki hane ikiye katlanır
            r *= 2
            if r > 9:
                r -= 9
        toplam += r
    return (10 - (toplam % 10)) % 10


def kart_ag(numara):
    """İlk hanelere göre kart ağını tespit eder (kısa/boş girdide bile güvenli)."""
    rakam = sadece_rakam(numara)
    if not rakam:
        return "Bilinmiyor"

    if rakam.startswith("9792"):            # Troy (Türkiye)
        return "Troy"
    if rakam.startswith("4"):               # Visa
        return "Visa"
    if rakam[:2] in ("51", "52", "53", "54", "55"):   # MasterCard 5-serisi
        return "MasterCard"
    if len(rakam) >= 4 and 2221 <= int(rakam[:4]) <= 2720:  # MasterCard 2-serisi
        return "MasterCard"
    if rakam[:2] in ("34", "37"):           # American Express
        return "American Express"
    if rakam[:3] in ("300", "301", "302", "303", "304", "305") or rakam[:2] in ("36", "38"):
        return "Diners Club"
    if len(rakam) >= 4 and 3528 <= int(rakam[:4]) <= 3589:  # JCB
        return "JCB"
    if rakam[:6] in ELO_BINLER:             # Elo (Discover "65" ile çakışanlar önce kontrol edilir)
        return "Elo"
    if rakam[:4] == "6011" or rakam[:3] in ("644", "645", "646", "647", "648", "649") or rakam[:2] == "65":
        return "Discover"
    if rakam.startswith("62"):              # UnionPay
        return "UnionPay"
    if rakam[:4] in ("5018", "5020", "5038", "5893", "6304", "6759", "6761", "6762", "6763"):
        return "Maestro"
    return "Bilinmiyor"


def uzunluk_bilgisi(numara, ag):
    """(uygun_mu, uzunluk, beklenen_uzunluklar) döndürür. Ağ bilinmiyorsa kontrol atlanır."""
    uzunluk = len(sadece_rakam(numara))
    beklenen = AG_UZUNLUK.get(ag)
    if beklenen is None:
        return True, uzunluk, None
    return uzunluk in beklenen, uzunluk, beklenen


def cvv_dogrula(cvv, ag):
    """CVV/CVC kontrolü: AMEX 4 hane, diğer ağlar 3 hane."""
    cvv = str(cvv or "")
    beklenen = 4 if ag == "American Express" else 3
    if not cvv.isdigit() or len(cvv) != beklenen:
        return False, f"{beklenen} haneli olmalı"
    return True, "Geçerli"


def son_kullanma_dogrula(ay, yil):
    """SKT (son kullanma tarihi) kontrolü. Yıl 2 (26) veya 4 (2026) haneli olabilir."""
    try:
        ay = int(ay)
        yil = int(yil)
    except (TypeError, ValueError):
        return False, "Ay/Yıl sayısal olmalı"
    if yil < 100:
        yil += 2000
    if not 1 <= ay <= 12:
        return False, "Ay 1-12 arasında olmalı"
    if yil < 2000 or yil > 2100:
        return False, "Yıl aralığı geçersiz (örn. 26 veya 2026)"
    bugun = datetime.date.today()
    if yil < bugun.year or (yil == bugun.year and ay < bugun.month):
        return False, "Kartın süresi dolmuş"
    return True, "Geçerli"


def grupla(numara):
    """Kart numarasını 4'erli gruplara bölüp okunur hale getirir."""
    return " ".join(numara[i:i + 4] for i in range(0, len(numara), 4))


def marka_normalize(marka):
    """binlist.net gibi kaynaklardan gelen marka adlarını standart ağ adına çevirir."""
    m = (marka or "").lower().replace(" ", "").replace("-", "").replace("_", "")
    esleme = {
        "visa": "Visa",
        "mastercard": "MasterCard",
        "amex": "American Express",
        "americanexpress": "American Express",
        "discover": "Discover",
        "dinersclub": "Diners Club",
        "jcb": "JCB",
        "unionpay": "UnionPay",
        "maestro": "Maestro",
        "elo": "Elo",
        "troy": "Troy",
        "mir": "MIR",
    }
    return esleme.get(m)


# ────────────────────────────────────────────────────────────
# 4) Raporlama (tek kart)
# ────────────────────────────────────────────────────────────
def tam_rapor(numara, cvv=None, ay=None, yil=None):
    """Tüm kontrolleri yapıp renkli rapor basar. Dönüş: 0=geçerli, 1=geçersiz."""
    rakam = sadece_rakam(numara)
    print()
    print(Renk.MAVI + "─" * 62 + Renk.RESET)

    if not rakam:
        print(f"{Renk.KIRMIZI}[!] Kart numarası boş veya rakam içermiyor.{Renk.RESET}")
        print(Renk.MAVI + "─" * 62 + Renk.RESET)
        return 1
    if not 13 <= len(rakam) <= 19:
        print(f"{Renk.KIRMIZI}[!] Kart {len(rakam)} hane. Luhn kontrolü 13-19 hane arası yapılır.{Renk.RESET}")

    ag = kart_ag(rakam)
    luhn_ok = luhn_dogrula(rakam)
    uzunluk_uygun, uzunluk, beklenen = uzunluk_bilgisi(rakam, ag)

    cvv_ok, cvv_msj = None, None
    if cvv is not None:
        cvv_ok, cvv_msj = cvv_dogrula(cvv, ag)
    skt_ok, skt_msj = None, None
    if ay is not None and yil is not None:
        skt_ok, skt_msj = son_kullanma_dogrula(ay, yil)

    print(f"{Renk.BOLD}Kart Numarası :{Renk.RESET} {Renk.CYAN}{numara}{Renk.RESET}")
    print(f"{Renk.BOLD}Kart Ağı      :{Renk.RESET} {ag}")

    if beklenen is None:
        uzunluk_str = f"({Renk.SARI}ağ tespit edilemedi, uzunluk kontrolü atlandı{Renk.RESET})"
    elif uzunluk_uygun:
        uzunluk_str = f"({Renk.YESIL}ağa uygun{Renk.RESET})"
    else:
        uzunluk_str = f"({Renk.KIRMIZI}ağa uygun değil, beklenen: {beklenen}{Renk.RESET})"
    print(f"{Renk.BOLD}Hane Sayısı   :{Renk.RESET} {uzunluk} {uzunluk_str}")

    luhn_str = f"{Renk.YESIL}GEÇERLİ ✓{Renk.RESET}" if luhn_ok else f"{Renk.KIRMIZI}GEÇERSİZ ✗{Renk.RESET}"
    print(f"{Renk.BOLD}Luhn Kontrolü :{Renk.RESET} {luhn_str}")

    if cvv_ok is not None:
        c = f"{Renk.YESIL}Geçerli ✓{Renk.RESET}" if cvv_ok else f"{Renk.KIRMIZI}{cvv_msj} ✗{Renk.RESET}"
        print(f"{Renk.BOLD}CVV Kontrolü  :{Renk.RESET} {c}")
    if skt_ok is not None:
        s = f"{Renk.YESIL}Geçerli ✓{Renk.RESET}" if skt_ok else f"{Renk.KIRMIZI}{skt_msj} ✗{Renk.RESET}"
        print(f"{Renk.BOLD}SKT Kontrolü  :{Renk.RESET} {s}")

    print(Renk.MAVI + "─" * 62 + Renk.RESET)
    ek_ok = True
    if cvv_ok is not None:
        ek_ok = ek_ok and cvv_ok
    if skt_ok is not None:
        ek_ok = ek_ok and skt_ok

    if luhn_ok and uzunluk_uygun and ek_ok:
        print(f"{Renk.YESIL}{Renk.BOLD}SONUÇ: KART GEÇERLİ ✓{Renk.RESET}")
        return 0
    print(f"{Renk.KIRMIZI}{Renk.BOLD}SONUÇ: KART GEÇERSİZ ✗{Renk.RESET}")
    return 1


# ────────────────────────────────────────────────────────────
# 5) BIN / Veritabanı sorgulama (2 Katman 4 Derece)
# ────────────────────────────────────────────────────────────
def binlist_sorgula(bin_no, zaman_asimi=8):
    """binlist.net açık BIN veritabanından çevrimiçi sorgu yapar (opsiyonel)."""
    try:
        url = f"https://lookup.binlist.net/{bin_no}"
        istek = urllib.request.Request(url, headers={
            "User-Agent": "kart-dogrulayici/2.3",
            "Accept-Version": "3",
        })
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
            return json.loads(yanit.read().decode("utf-8"))
    except Exception:
        return None


def bin_analiz(numara, online=False):
    """BIN'i yerleşik tablodan (ve istenirse binlist.net'ten) sorgular."""
    rakam = sadece_rakam(numara)
    bin6 = rakam[:6]
    sonuc = {"bin": bin6, "marka": None, "kurum": None, "ulke": None,
             "tip": None, "kaynak": None, "on_odeme": None}
    kayit = BIN_VERITABANI.get(bin6)
    if kayit:
        sonuc.update(kayit)
        sonuc["kaynak"] = "yerleşik tablo (offline)"
    elif online and len(bin6) == 6:
        veri = binlist_sorgula(bin6)
        if veri:
            sonuc["marka"] = veri.get("scheme")
            sonuc["tip"] = veri.get("type")
            sonuc["on_odeme"] = veri.get("prepaid")
            ulke = veri.get("country") or {}
            sonuc["ulke"] = ulke.get("name")
            banka = veri.get("bank") or {}
            sonuc["kurum"] = banka.get("name")
            sonuc["kaynak"] = "binlist.net (online)"
    else:
        sonuc["kaynak"] = "yok"
    return sonuc


def bin_rapor(numara, sonuc, cvv=None, ay=None, yil=None):
    """2 Katman x 4 Derece BIN analiz raporu basar. Dönüş: 0/1 (çıkış kodu)."""
    rakam = sadece_rakam(numara)
    ag = kart_ag(rakam)
    print()
    print(Renk.MAVI + "═" * 62 + Renk.RESET)
    print(f"{Renk.BOLD}{Renk.SARI} BIN / VERİTABANI ANALİZİ{Renk.RESET}")
    print(Renk.MAVI + "═" * 62 + Renk.RESET)
    print(f"{Renk.BOLD}Numara    :{Renk.RESET} {Renk.CYAN}{numara}{Renk.RESET}")
    print(f"{Renk.BOLD}BIN (6)   :{Renk.RESET} {sonuc['bin']}")
    print(f"{Renk.BOLD}Tespit Ağ :{Renk.RESET} {ag}")

    # ── KATMAN 1: Numara doğrulama (4 derece) ──
    print()
    print(f"{Renk.BOLD}{Renk.MAVI}KATMAN 1 — NUMARA DOĞRULAMA (4 Derece){Renk.RESET}")
    derece1 = []

    derece1.append(("Luhn Kontrolü", luhn_dogrula(rakam)))
    derece1.append(("Kart Ağı Tespiti", ag != "Bilinmiyor"))

    uygun, uzunluk, beklenen = uzunluk_bilgisi(rakam, ag)
    derece1.append(("Uzunluk Uygunluğu", uygun if beklenen is not None else None))

    if cvv is not None or (ay is not None and yil is not None):
        cvv_ok = True
        if cvv is not None:
            cvv_ok, _ = cvv_dogrula(cvv, ag)
        skt_ok = True
        if ay is not None and yil is not None:
            skt_ok, _ = son_kullanma_dogrula(ay, yil)
        derece1.append(("CVV/SKT Kontrolü", cvv_ok and skt_ok))
    else:
        derece1.append(("CVV/SKT Kontrolü", None))

    for ad, ok in derece1:
        if ok is None:
            g = f"{Renk.GRI}— (girilmedi, atlandı){Renk.RESET}"
        elif ok:
            g = f"{Renk.YESIL}✓{Renk.RESET}"
        else:
            g = f"{Renk.KIRMIZI}✗{Renk.RESET}"
        print(f"  [{Renk.CYAN}D{Renk.RESET}] {ad:<22} : {g}")

    # ── KATMAN 2: BIN / kurum analizi (4 derece) ──
    print()
    print(f"{Renk.BOLD}{Renk.MAVI}KATMAN 2 — BIN / KURUM ANALİZİ (4 Derece){Renk.RESET}")
    derece2 = []

    kayit_var = sonuc.get("kaynak") not in (None, "yok")
    derece2.append(("BIN Kaydı", kayit_var))

    marka_uyum = None
    if sonuc.get("marka"):
        marka_uyum = (marka_normalize(sonuc["marka"]) == ag) and ag != "Bilinmiyor"
    derece2.append(("Marka Uyumu", marka_uyum))

    derece2.append(("Kurum Bilgisi", bool(sonuc.get("kurum"))))
    derece2.append(("Ülke Bilgisi", bool(sonuc.get("ulke"))))

    for ad, ok in derece2:
        if ok is None:
            g = f"{Renk.GRI}— (veri yok){Renk.RESET}"
        elif ok:
            g = f"{Renk.YESIL}✓{Renk.RESET}"
        else:
            g = f"{Renk.KIRMIZI}✗{Renk.RESET}"
        print(f"  [{Renk.CYAN}D{Renk.RESET}] {ad:<22} : {g}")

    # ── BIN detayları ──
    print()
    print(f"{Renk.BOLD}{Renk.SARI}BIN Detayları:{Renk.RESET}")
    kaynak_str = f"{Renk.YESIL}{sonuc['kaynak']}{Renk.RESET}" if kayit_var else f"{Renk.KIRMIZI}veritabanında kayıt yok{Renk.RESET}"
    print(f"  Kaynak      : {kaynak_str}")
    print(f"  BIN Markası : {sonuc.get('marka') or Renk.GRI + 'bilinmiyor' + Renk.RESET}")
    print(f"  Kurum       : {sonuc.get('kurum') or Renk.GRI + 'bilinmiyor' + Renk.RESET}")
    print(f"  Ülke        : {sonuc.get('ulke') or Renk.GRI + 'bilinmiyor' + Renk.RESET}")
    print(f"  Tip         : {sonuc.get('tip') or Renk.GRI + 'bilinmiyor' + Renk.RESET}")
    if sonuc.get("on_odeme") is not None:
        print(f"  Ön Ödemeli  : {'Evet' if sonuc['on_odeme'] else 'Hayır'}")

    # ── REALİTE SKORU ──
    kazanc = sum(1 for _, ok in derece1 + derece2 if ok is True)
    toplam = sum(1 for _, ok in derece1 + derece2 if ok is not None)
    print(Renk.MAVI + "═" * 62 + Renk.RESET)
    if toplam == 0:
        durum = "veri yok"
    elif kazanc == toplam:
        durum = "YÜKSEK tutarlılık"
    elif kazanc >= toplam / 2:
        durum = "ORTA tutarlılık"
    else:
        durum = "DÜŞÜK tutarlılık"
    print(f"{Renk.BOLD}REALİTE SKORU:{Renk.RESET} {Renk.YESIL}{kazanc}/{toplam}{Renk.RESET} ({durum})")
    print(f"{Renk.GRI}[i] Bu skor yalnızca FORMAT tutarlılığını ölçer. Numaranın gerçek bir{Renk.RESET}")
    print(f"{Renk.GRI}    hesaba bağlı olduğunu veya ödemede çalışacağını GARANTİ ETMEZ.{Renk.RESET}")
    print(Renk.MAVI + "═" * 62 + Renk.RESET)
    return 0 if kazanc == toplam else 1


# ────────────────────────────────────────────────────────────
# 6) Test kartı üretici (resmî test BIN'leriyle, Luhn-geçerli)
# ────────────────────────────────────────────────────────────
def kart_uret(ag, adet=1, test_binleri=True):
    """Ağa uygun Luhn-geçerli TEST kart numarası üretir (gerçek kart değildir)."""
    if test_binleri and ag in TEST_BINLER:
        kaynaklar = TEST_BINLER[ag]
    else:
        kaynaklar = AG_BASLANGICLAR.get(ag, [])
    if not kaynaklar:
        return []
    sonuclar = []
    for _ in range(adet):
        bas = random.choice(kaynaklar)
        hedef = random.choice(AG_UZUNLUK.get(ag, (16,)))
        eksik = hedef - len(bas) - 1          # kontrol hanesi hariç
        if eksik < 0:
            continue
        prefix = bas + "".join(random.choice("0123456789") for _ in range(eksik))
        sonuclar.append(prefix + str(luhn_kontrol_rakami(prefix)))
    return sonuclar


# ────────────────────────────────────────────────────────────
# 7) Onaylı test kartları (Stripe + Braintree + PayPal resmî dokümantasyonu)
#    Format: (kart, marka, sağlayıcı, davranış)
# ────────────────────────────────────────────────────────────
TEST_KARTLARI = [
    # ── STRIPE ──
    ("4242 4242 4242 4242", "Visa",             "Stripe",   "✅ Başarılı ödeme"),
    ("4000 0000 0000 0002", "Visa",             "Stripe",   "❌ Reddedilir (genel)"),
    ("4000 0000 0000 9995", "Visa",             "Stripe",   "❌ Yetersiz bakiye"),
    ("4000 0000 0000 3220", "Visa",             "Stripe",   "🔐 3DS doğrulama gerekli"),
    ("4000 0000 0000 0341", "Visa",             "Stripe",   "🔐 3DS2 doğrulama gerekli"),
    ("4000 0000 0000 9235", "Visa",             "Stripe",   "🔐 3DS2 doğrulama gerekli"),
    ("4000 0000 0000 3063", "Visa",             "Stripe",   "🔐 3DS2 doğrulama gerekli"),
    ("4000 0000 0000 0069", "Visa",             "Stripe",   "❌ Kart süresi dolmuş"),
    ("4000 0000 0000 0127", "Visa",             "Stripe",   "❌ Hatalı CVC"),
    ("4000 0000 0000 0077", "Visa",             "Stripe",   "❌ Reddedilir (risk)"),
    ("4000 0000 0000 0101", "Visa",             "Stripe",   "❌ İşlem hatası"),
    ("5555 5555 5555 4444", "MasterCard",       "Stripe",   "✅ Başarılı ödeme"),
    ("2223 0000 4841 0010", "MasterCard",       "Stripe",   "✅ Başarılı ödeme (2-serisi)"),
    ("5105 1051 0510 5100", "MasterCard",       "Stripe",   "✅ Başarılı ödeme"),
    ("5200 8282 8282 8210", "MasterCard",       "Stripe",   "✅ Başarılı ödeme"),
    ("3782 822463 10005",   "American Express", "Stripe",   "✅ Başarılı ödeme"),
    ("3714 496353 98431",   "American Express", "Stripe",   "❌ Reddedilir (genel)"),
    ("6011 1111 1111 1117", "Discover",         "Stripe",   "✅ Başarılı ödeme"),
    ("6011 0009 9013 9424", "Discover",         "Stripe",   "✅ Başarılı ödeme"),
    ("3056 9309 0259 04",   "Diners Club",      "Stripe",   "✅ Başarılı ödeme"),
    ("3530 1113 3330 0000", "JCB",              "Stripe",   "✅ Başarılı ödeme"),
    ("3566 0020 2036 0505", "JCB",              "Stripe",   "✅ Başarılı ödeme"),
    ("6759 6498 2643 8453", "Maestro",          "Stripe",   "✅ Başarılı ödeme"),
    ("6200 0000 0000 0005", "UnionPay",         "Stripe",   "✅ Başarılı ödeme"),
    # ── BRAINTREE / PAYPAL (ortak sandbox kartları) ──
    ("4111 1111 1111 1111", "Visa",             "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("4000 1111 1111 1115", "Visa",             "Braintree/PayPal", "❌ Reddedilir (genel)"),
    ("4012 8888 8888 1881", "Visa",             "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("4222 2222 2222 2",    "Visa",             "Braintree/PayPal", "✅ Başarılı ödeme (13 hane)"),
    ("5555 5555 5555 4444", "MasterCard",       "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("2221 0000 0000 0009", "MasterCard",       "Braintree/PayPal", "✅ Başarılı ödeme (2-serisi)"),
    ("5105 1051 0510 5100", "MasterCard",       "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("3782 822463 10005",   "American Express", "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("6011 1111 1111 1117", "Discover",         "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("3852 0000 0232 37",   "Diners Club",      "Braintree/PayPal", "✅ Başarılı ödeme"),
    ("3530 1113 3330 0000", "JCB",              "Braintree/PayPal", "✅ Başarılı ödeme"),
]


def test_kartlari_goster():
    """Tüm sağlayıcıların onaylı test kartlarını Luhn ve ağ tespitiyle listeler."""
    print(f"\n{Renk.BOLD}{Renk.SARI}=== ONAYLI TEST KARTLARI (Stripe + Braintree + PayPal) ==={Renk.RESET}")
    print(f"{Renk.GRI}Not: Bu kartlar yalnızca ilgili sağlayıcının SANDOX ortamında işleme alınır,{Renk.RESET}")
    print(f"{Renk.GRI}    gerçek işleme alınmaz. Resmî dokümantasyonda yayınlanmıştır.{Renk.RESET}\n")

    mevcut_saglayici = None
    for kart, ag, saglayici, davranis in TEST_KARTLARI:
        if saglayici != mevcut_saglayici:
            mevcut_saglayici = saglayici
            print(f"{Renk.BOLD}{Renk.MAVI}── {saglayici} ────────────────────────────────────────{Renk.RESET}")

        luhn = luhn_dogrula(kart)
        tespit = kart_ag(kart)
        durum = f"{Renk.YESIL}geçerli{Renk.RESET}" if luhn else f"{Renk.KIRMIZI}GEÇERSİZ!{Renk.RESET}"
        ag_uyum = f"{Renk.YESIL}✓{Renk.RESET}" if tespit == ag else f"{Renk.KIRMIZI}✗ (tespit: {tespit}){Renk.RESET}"
        print(f"  {Renk.CYAN}{kart:<23}{Renk.RESET} [{ag:<15}] {davranis:<35} Luhn: {durum}  Ağ: {ag_uyum}")

    print(f"\n{Renk.SARI}Geçerli ek bilgiler:{Renk.RESET}")
    print(f"  CVV      : 123 (AMEX için 1234)")
    print(f"  SKT      : gelecekteki herhangi bir tarih (örn. 12/2028)")
    print(f"  İsim     : herhangi bir isim (örn. TEST USER)")
    print()


# ────────────────────────────────────────────────────────────
# 8) Dosyadan toplu doğrulama
# ────────────────────────────────────────────────────────────
def ornek_dosya_olustur(dosya):
    """Örnek toplu test dosyası oluşturur. Format: kart,cvv,ay,yil"""
    ornek = [
        "4242 4242 4242 4242,123,12,2028",
        "5555 5555 5555 4444,123,05,2027",
        "4000 0000 0000 0002,123,11,2026",
        "3782 822463 10005,1234,09,2029",
        "1234 5678 9012 3456,123,12,2028",
    ]
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            f.write("\n".join(ornek) + "\n")
        return True
    except Exception:
        return False


def dosyadan_dogrula(dosya):
    """Dosyadaki kartları tek tek doğrular ve özet istatistik basar."""
    if not os.path.isfile(dosya):
        print(f"{Renk.KIRMIZI}[!] Dosya bulunamadı: {dosya}{Renk.RESET}")
        return
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            satirlar = [s.strip() for s in f if s.strip()]
    except Exception as e:
        print(f"{Renk.KIRMIZI}[!] Dosya okunamadı: {e}{Renk.RESET}")
        return

    print(f"\n{Renk.BOLD}{Renk.SARI}Toplu doğrulama başladı ({len(satirlar)} satır){Renk.RESET}")
    print(Renk.MAVI + "─" * 62 + Renk.RESET)
    dogru = 0
    yanlis = 0
    for no, satir in enumerate(satirlar, 1):
        parcalar = [p.strip() for p in satir.replace(";", ",").split(",")]
        kart = parcalar[0]
        cvv = parcalar[1] if len(parcalar) > 1 and parcalar[1] else None
        ay = parcalar[2] if len(parcalar) > 2 and parcalar[2] else None
        yil = parcalar[3] if len(parcalar) > 3 and parcalar[3] else None

        rakam = sadece_rakam(kart)
        luhn = luhn_dogrula(rakam)
        ag = kart_ag(rakam)

        cvv_ok = True
        if cvv is not None:
            cvv_ok, _ = cvv_dogrula(cvv, ag)
        skt_ok = True
        if ay is not None and yil is not None:
            skt_ok, _ = son_kullanma_dogrula(ay, yil)

        hepsi = luhn and cvv_ok and skt_ok
        if hepsi:
            dogru += 1
            isaret = f"{Renk.YESIL}✓ GEÇERLİ{Renk.RESET}"
        else:
            yanlis += 1
            isaret = f"{Renk.KIRMIZI}✗ GEÇERSİZ{Renk.RESET}"

        ek = ""
        if not luhn:
            ek += " | Luhn hatalı"
        if cvv is not None and not cvv_ok:
            ek += " | CVV hatalı"
        if ay is not None and yil is not None and not skt_ok:
            ek += " | SKT hatalı"

        print(f"  {no:>3}. {Renk.CYAN}{kart:<23}{Renk.RESET} [{ag}] {isaret}{Renk.GRI}{ek}{Renk.RESET}")

    print(Renk.MAVI + "─" * 62 + Renk.RESET)
    print(f"{Renk.YESIL}Geçerli: {dogru}{Renk.RESET}   {Renk.KIRMIZI}Geçersiz: {yanlis}{Renk.RESET}   {Renk.SARI}Toplam: {len(satirlar)}{Renk.RESET}")
    print()


# ────────────────────────────────────────────────────────────
# 9) Menü
# ────────────────────────────────────────────────────────────
def ana_menu_goster():
    """Kutulu, renkli ana menüyü çizer."""
    print(BANNER)
    c = Renk.MAVI
    W = 66
    print(c + "┌" + "─" * W + "┐" + Renk.RESET)
    print(c + "│" + Renk.RESET + Renk.BOLD + Renk.SARI + " ANA MENÜ".ljust(W) + Renk.RESET + c + "│" + Renk.RESET)
    print(c + "├" + "─" * W + "┤" + Renk.RESET)
    satirlar = [
        (" [1]", " Tek Kart Doğrula (Luhn + Ağ + Uzunluk)", Renk.CYAN),
        (" [2]", " Tam Form Kontrolü (CVV + SKT ile)", Renk.CYAN),
        (" [3]", " Onaylı Test Kartlarını Listele", Renk.CYAN),
        (" [4]", " Toplu Doğrulama (Dosyadan)", Renk.CYAN),
        (" [5]", " Luhn-Geçerli Test Kartı Üret", Renk.CYAN),
        (" [6]", " BIN / Veritabanı Sorgulama (2 Katman 4 Derece)", Renk.CYAN),
        (" [7]", " Onaylı Test Kartı Rehberi (Stripe+Braintree+PayPal)", Renk.CYAN),
        (" [8]", " Hakkında / Yardım", Renk.CYAN),
        (" [0]", " Çıkış", Renk.KIRMIZI),
    ]
    for num, metin, renk in satirlar:
        duz = num + metin
        icerik = renk + duz + Renk.RESET
        print(c + "│" + Renk.RESET + icerik + " " * (W - len(duz)) + c + "│" + Renk.RESET)
    print(c + "└" + "─" * W + "┘" + Renk.RESET)


def tek_kart_menu():
    """Menü 1: Tek kart doğrulama."""
    print()
    girdi = input(f"{Renk.CYAN}[?]{Renk.RESET} Kart numarası: ").strip()
    if not girdi:
        print(f"{Renk.SARI}[i] Girdi yok, iptal edildi.{Renk.RESET}")
        return
    tam_rapor(girdi)


def tam_form_menu():
    """Menü 2: Kart + CVV + SKT tam form kontrolü."""
    print()
    numara = input(f"{Renk.CYAN}[?]{Renk.RESET} Kart numarası: ").strip()
    if not numara:
        print(f"{Renk.SARI}[i] Kart numarası gerekli, iptal edildi.{Renk.RESET}")
        return
    cvv = input(f"{Renk.CYAN}[?]{Renk.RESET} CVV/CVC (3-4 hane, boş geçilebilir): ").strip()
    ay = input(f"{Renk.CYAN}[?]{Renk.RESET} Son kullanma ayı (1-12, boş geçilebilir): ").strip()
    yil = input(f"{Renk.CYAN}[?]{Renk.RESET} Son kullanma yılı (örn. 2028, boş geçilebilir): ").strip()
    tam_rapor(numara, cvv=cvv or None, ay=ay or None, yil=yil or None)


def dosya_menu():
    """Menü 4: Dosyadan toplu doğrulama."""
    print()
    girdi = input(f"{Renk.CYAN}[?]{Renk.RESET} Dosya yolu [{Renk.GRI}kartlar.txt{Renk.RESET}]: ").strip()
    if not girdi:
        girdi = "kartlar.txt"
    if not os.path.isfile(girdi):
        cevap = input(f"{Renk.SARI}[i] '{girdi}' bulunamadı. Örnek dosya oluşturulsun mu? (e/H): {Renk.RESET}").strip().lower()
        if cevap in ("e", "evet", "y", "yes"):
            if ornek_dosya_olustur(girdi):
                print(f"{Renk.YESIL}[+] Örnek dosya oluşturuldu: {girdi}{Renk.RESET}")
            else:
                print(f"{Renk.KIRMIZI}[!] Dosya oluşturulamadı.{Renk.RESET}")
                return
        else:
            print(f"{Renk.SARI}[i] İptal edildi.{Renk.RESET}")
            return
    dosyadan_dogrula(girdi)


def uret_menu():
    """Menü 5: Resmî test BIN'leriyle Luhn-geçerli test kartı üretici."""
    print()
    aglar = sorted(TEST_BINLER.keys())
    print(f"{Renk.BOLD}Kart ağı seçin:{Renk.RESET}")
    for i, a in enumerate(aglar, 1):
        print(f"  {Renk.CYAN}[{i}]{Renk.RESET} {a}")
    print(f"  {Renk.KIRMIZI}[0]{Renk.RESET} Geri")
    sec = input(f"{Renk.CYAN}[?]{Renk.RESET} Seçim: ").strip()
    if sec in ("", "0"):
        return
    if not sec.isdigit() or not (1 <= int(sec) <= len(aglar)):
        print(f"{Renk.KIRMIZI}[!] Geçersiz seçim.{Renk.RESET}")
        return
    ag = aglar[int(sec) - 1]

    try:
        adet = int(input(f"{Renk.CYAN}[?]{Renk.RESET} Kaç adet üretilsin (1-20) [{Renk.GRI}1{Renk.RESET}]: ").strip() or "1")
    except ValueError:
        adet = 1
    adet = max(1, min(adet, 20))

    kartlar = kart_uret(ag, adet, test_binleri=True)
    print()
    print(f"{Renk.YESIL}{Renk.BOLD}Üretilen Luhn-geçerli TEST kartları ({ag}):{Renk.RESET}")
    for k in kartlar:
        print(f"  {Renk.CYAN}{grupla(k)}{Renk.RESET}")
    print(f"\n{Renk.GRI}[i] Resmî test BIN'leri kullanıldı — BIN sorgulama ([6]) bu numaraları eşleştirir.{Renk.RESET}")
    print(f"{Renk.GRI}    Bu numaralar yalnızca istemci tarafı form testi içindir; gerçek kart değildir{Renk.RESET}")
    print(f"{Renk.GRI}    ve canlı ödeme sağlayıcısında işleme alınmaz.{Renk.RESET}")


def bin_menu():
    """Menü 6: BIN / Veritabanı sorgulama (2 Katman 4 Derece)."""
    print()
    numara = input(f"{Renk.CYAN}[?]{Renk.RESET} Kart numarası veya BIN (ilk 6-8 hane): ").strip()
    if not numara:
        print(f"{Renk.SARI}[i] Girdi yok, iptal edildi.{Renk.RESET}")
        return
    if len(sadece_rakam(numara)) < 6:
        print(f"{Renk.KIRMIZI}[!] BIN analizi için en az 6 hane gerekli.{Renk.RESET}")
        return
    cevap = input(f"{Renk.CYAN}[?]{Renk.RESET} Çevrimiçi BIN veritabanı (binlist.net) sorgusu yapılsın mı? (e/H): ").strip().lower()
    online = cevap in ("e", "evet", "y", "yes")
    print(f"{Renk.GRI}[i] Çevrimiçi sorgu: {'AÇIK' if online else 'KAPALI (yerleşik tablo)'}{Renk.RESET}")
    cvv = input(f"{Renk.CYAN}[?]{Renk.RESET} CVV (boş geçilebilir): ").strip()
    ay = input(f"{Renk.CYAN}[?]{Renk.RESET} SKT ay (boş geçilebilir): ").strip()
    yil = input(f"{Renk.CYAN}[?]{Renk.RESET} SKT yıl (boş geçilebilir): ").strip()
    sonuc = bin_analiz(numara, online=online)
    bin_rapor(numara, sonuc, cvv=cvv or None, ay=ay or None, yil=yil or None)


def hakkimda_goster():
    """Menü 8: Hakkında / yardım ekranı."""
    print()
    print(Renk.MAVI + "─" * 62 + Renk.RESET)
    print(f"{Renk.BOLD}{Renk.SARI}KART DOĞRULAYICI v2.3{Renk.RESET} - Ödeme Formu Kart Doğrulama Test Aracı")
    print(f"{Renk.BOLD}Yapımcı:{Renk.RESET} {Renk.CYAN}@markos39{Renk.RESET}")
    print(f"{Renk.KIRMIZI}[!] Uyarı: Sorumluluk kullanıcıya aittir.{Renk.RESET}")
    print()
    print(f"{Renk.BOLD}Özellikler:{Renk.RESET}")
    print("  • Luhn algoritması ile kart numarası doğrulama")
    print("  • Kart ağı tespiti: Visa, MasterCard, American Express, Discover,")
    print("    Diners Club, JCB, UnionPay, Maestro, Elo, Troy")
    print("  • Ağa özel uzunluk, CVV ve son kullanma tarihi kontrolü")
    print("  • BIN / Veritabanı sorgulama: 2 Katman x 4 Derece analiz")
    print("    (yerleşik offline tablo + opsiyonel binlist.net çevrimiçi sorgu)")
    print("  • Onaylı test kartı rehberi (Stripe + Braintree + PayPal resmî kartları)")
    print("  • Dosyadan toplu doğrulama")
    print("  • Resmî test BIN'leriyle Luhn-geçerli test kartı üretimi")
    print()
    print(f"{Renk.BOLD}Komut satırı kullanımı:{Renk.RESET}")
    print("  python3 kart_dogrulayici.py                     → Menü")
    print("  python3 kart_dogrulayici.py '4242 4242 4242 4242'")
    print("  python3 kart_dogrulayici.py 5555555555554444 --cvv 123 --ay 12 --yil 2028")
    print("  python3 kart_dogrulayici.py 4242424242424242 --bin            → BIN analizi")
    print("  python3 kart_dogrulayici.py 4242424242424242 --bin --online   → + binlist.net")
    print("  python3 kart_dogrulayici.py --test              → Onaylı test kartları")
    print(Renk.MAVI + "─" * 62 + Renk.RESET)


def ana_menu():
    """Ana menü döngüsü."""
    while True:
        ana_menu_goster()
        try:
            secim = input(f"\n{Renk.CYAN}[?]{Renk.RESET} Seçiminiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
            return
        if secim == "0":
            print(f"{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
            return
        elif secim == "1":
            tek_kart_menu()
        elif secim == "2":
            tam_form_menu()
        elif secim == "3":
            test_kartlari_goster()
        elif secim == "4":
            dosya_menu()
        elif secim == "5":
            uret_menu()
        elif secim == "6":
            bin_menu()
        elif secim == "7":
            test_kartlari_goster()      # Onaylı Test Kartı Rehberi
        elif secim == "8":
            hakkimda_goster()
        else:
            print(f"\n{Renk.KIRMIZI}[!] Geçersiz seçim: '{secim}'{Renk.RESET}")
        try:
            input(f"\n{Renk.GRI}[Enter] devam etmek için...{Renk.RESET}")
        except (EOFError, KeyboardInterrupt):
            print()
            return


# ────────────────────────────────────────────────────────────
# 10) Ana giriş
# ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="kart_dogrulayici",
        description="Ödeme formlarının kart doğrulama mantığını test etmek için Luhn / ağ / CVV / SKT / BIN doğrulayıcı.",
        epilog="Örnek: python3 kart_dogrulayici.py '4242 4242 4242 4242' --cvv 123 --ay 12 --yil 2028",
    )
    parser.add_argument("kart", nargs="?", help="Kart numarası (boşluk veya tire olabilir)")
    parser.add_argument("--cvv", help="CVV/CVC değeri (AMEX için 4, diğerleri için 3 hane)")
    parser.add_argument("--ay", help="Son kullanma ayı (1-12)")
    parser.add_argument("--yil", help="Son kullanma yılı (örn. 26 veya 2026)")
    parser.add_argument("-b", "--bin", action="store_true", help="BIN / veritabanı analizi yap (2 Katman 4 Derece)")
    parser.add_argument("--online", action="store_true", help="BIN analizinde binlist.net sorgusu da yap")
    parser.add_argument("-t", "--test", action="store_true", help="Onaylı test kartlarını listele")
    args = parser.parse_args()

    if args.test:
        print(BANNER)
        test_kartlari_goster()
        sys.exit(0)

    if args.bin:
        print(BANNER)
        if not args.kart:
            print(f"{Renk.KIRMIZI}[!] --bin ile birlikte bir kart numarası verin.{Renk.RESET}")
            sys.exit(2)
        sonuc = bin_analiz(args.kart, online=args.online)
        sys.exit(bin_rapor(args.kart, sonuc, cvv=args.cvv, ay=args.ay, yil=args.yil))

    if not args.kart:
        try:
            ana_menu()
        except KeyboardInterrupt:
            print(f"\n{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
        sys.exit(0)

    print(BANNER)
    sys.exit(tam_rapor(args.kart, cvv=args.cvv, ay=args.ay, yil=args.yil))


if __name__ == "__main__":
    main()
