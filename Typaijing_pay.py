#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════
 Payment_grand v2026.5.0.0 ULTIMATE
 Ödeme Formu Kart Doğrulama Test Aracı + Çoklu Veritabanı Motoru
════════════════════════════════════════════════════════════════════════
 MODÜLLER:
  [Çekirdek]  : Luhn (std+varyant), 19 ağ tespiti, ağırlıklı skor,
                risk faktörü motoru, PCI-DSS maskeleme, PAN SHA-256
  [BIN]       : 6/8 haneli IIN, TTL önbellek, hız limitli binlist.net
  [Üretici]   : Sandbox BIN'ler, 8 senaryo, SKT/CVV üretimi
  [VERİTABANI]: SQLite3 (yerleşik) | PostgreSQL | MySQL | Oracle | MSSQL
                → doğrulama kayıtları, BIN önbelleği, denetim izi (audit)
  [Rapor]     : CSV / JSON / JSONL / HTML / DB sorgu çıktısı
  [Konsol]    : Renkli loglama (DEBUG/INFO/WARN/ERROR), ISO 8601
  [Test]      : Genişletilmiş --oztest + DB bağlantı testi

 VERİTABANI KURULUMU (opsiyonel sürücüler):
  SQLite      : (yerleşik, kuruluma gerek yok)
  PostgreSQL  : pip install psycopg2-binary
  MySQL       : pip install mysql-connector-python
  Oracle      : pip install oracledb
  MSSQL       : pip install pyodbc

 KULLANIM:
  python3 payment_grand.py                          # Menü
  python3 payment_grand.py "4242 4242 4242 4242"    # Tek kart (SQLite'a kaydeder)
  python3 payment_grand.py 4242424242424242 --db sqlite:///pg.db
  python3 payment_grand.py 4242424242424242 --db postgresql://user:pass@host/pg
  python3 payment_grand.py 4242424242424242 --db mysql://user:pass@host/pg
  python3 payment_grand.py 4242424242424242 --db oracle://user:pass@host/pg
  python3 payment_grand.py 4242424242424242 --db mssql://user:pass@host/pg
  python3 payment_grand.py --db-gecmis              # kayıtlı geçmişi listele
  python3 payment_grand.py --db-istatistik          # istatistik
  python3 payment_grand.py --db-test "sqlite:///pg.db"   # bağlantı testi
  python3 payment_grand.py --oztest
  python3 payment_grand.py kartlar.txt --html-rapor rapor.html
════════════════════════════════════════════════════════════════════════
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
import random
import re
import sqlite3
import sys
import time
import urllib.request


# ═══════════════════════════════════════════════════════════
# 0) SÜRÜM & SABİTLER
# ═══════════════════════════════════════════════════════════
PROGRAM_ADI = "payment_grand"
SURUM       = "2026.5.0.0"
BINA_TARIHI = "2026-09-13"

PROFILLER = {
    "dev":  {"log_seviye": "DEBUG", "renk": True,  "json": False},
    "prod": {"log_seviye": "WARN",  "renk": True,  "json": True},
    "ci":   {"log_seviye": "ERROR", "renk": False, "json": True},
}

# Sürücü importları (opsiyonel)
SURUCU = {}
try:
    import psycopg2
    SURUCU["postgresql"] = psycopg2
except ImportError:
    pass
try:
    import mysql.connector as mysql_conn
    SURUCU["mysql"] = mysql_conn
except ImportError:
    pass
try:
    import oracledb as oracle_conn
    SURUCU["oracle"] = oracle_conn
except ImportError:
    try:
        import cx_Oracle as oracle_conn
        SURUCU["oracle"] = oracle_conn
    except ImportError:
        pass
try:
    import pyodbc
    SURUCU["mssql"] = pyodbc
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════
# 1) RENK & LOG
# ═══════════════════════════════════════════════════════════
class Renk:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GRI     = "\033[90m"
    KIRMIZI = "\033[91m"
    YESIL   = "\033[92m"
    SARI    = "\033[93m"
    MAVI    = "\033[94m"
    MOR     = "\033[95m"
    CYAN    = "\033[96m"

    @classmethod
    def kapat(cls):
        for a in list(vars(cls)):
            if a.isupper() and isinstance(getattr(cls, a), str) and "\033" in getattr(cls, a):
                setattr(cls, a, "")


SESSIZ = False
LOG_SEVIYE = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
_log_seviyesi = "INFO"


def yaz(metin=""):
    if not SESSIZ:
        print(metin)


def _log(kayit, seviye, metin):
    if LOG_SEVIYE[seviye] < LOG_SEVIYE.get(_log_seviyesi, 20):
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    renkler = {"DEBUG": Renk.GRI, "INFO": Renk.MAVI,
               "WARN": Renk.SARI, "ERROR": Renk.KIRMIZI}
    print(f"{renkler.get(seviye, '')}[{ts}][{seviye}][{kayit}]{Renk.RESET} {metin}")


def log_debug(k, m): _log(k, "DEBUG", m)
def log_info(k, m):  _log(k, "INFO", m)
def log_warn(k, m):  _log(k, "WARN", m)
def log_error(k, m): _log(k, "ERROR", m)


def log_dosya(dosya, satir):
    if not dosya:
        return
    try:
        with open(dosya, "a", encoding="utf-8") as f:
            f.write(re.sub(r"\033\[[0-9;]*m", "", satir) + "\n")
    except Exception:
        pass


BANNER = f"""
{Renk.CYAN} ╔══════════════════════════════════════════════════════════════╗{Renk.RESET}
{Renk.CYAN} ║{Renk.RESET}  {Renk.BOLD}{Renk.MOR}P A Y M E N T _ G R A N D{Renk.RESET}  {Renk.SARI}v{SURUM} ULTIMATE{Renk.RESET}        {Renk.CYAN}║{Renk.RESET}
{Renk.CYAN} ║{Renk.RESET}  {Renk.CYAN}Ödeme Formu Test Aracı + Çoklu Veritabanı Motoru{Renk.RESET}         {Renk.CYAN}║{Renk.RESET}
{Renk.CYAN} ║{Renk.RESET}  {Renk.SARI}SQLite|PostgreSQL|MySQL|Oracle|MSSQL | Risk | BIN{Renk.RESET}        {Renk.CYAN}║{Renk.RESET}
{Renk.CYAN} ╚══════════════════════════════════════════════════════════════╝{Renk.RESET}
{Renk.SARI}     Yapımcı : @markos39  |  Bina: {BINA_TARIHI}{Renk.RESET}
{Renk.KIRMIZI}     [!] UYARI: Yalnızca test/sandbox kullanımı. Sorumluluk kullanıcıya aittir.{Renk.RESET}
"""


# ═══════════════════════════════════════════════════════════
# 2) KART AĞLARI (19)
# ═══════════════════════════════════════════════════════════
AG_UZUNLUK = {
    "Visa": (13, 16, 19), "MasterCard": (16,), "American Express": (15,),
    "Discover": (16, 19), "Diners Club": (14, 16, 19),
    "JCB": (16, 17, 18, 19), "UnionPay": (16, 19),
    "Maestro": (12, 13, 14, 15, 16, 17, 18, 19),
    "Elo": (16,), "Troy": (16,), "MIR": (16, 17, 18, 19), "RuPay": (16,),
    "Verve": (16, 19), "Dankort": (16,), "UATP": (15,),
    "Laser": (16, 17, 18, 19), "Switch": (16, 18, 19), "InterPayment": (16, 17, 18, 19),
}
AG_CVV_UZUNLUK = {"American Express": 4, "UATP": 4}

TEST_BINLER = {
    "Visa": ["424242", "400000", "411111", "401288", "400005"],
    "MasterCard": ["555555", "510510", "222300", "520082", "222100"],
    "American Express": ["378282", "371449"],
    "Discover": ["601111", "601100", "644564"],
    "Diners Club": ["305693", "385200"],
    "JCB": ["353011", "356600"],
    "Maestro": ["675964"], "Troy": ["979202"], "UnionPay": ["620000"],
    "Elo": ["636368"], "MIR": ["220000"], "RuPay": ["607555"],
    "Verve": ["506099"], "Dankort": ["501971"], "UATP": ["1"],
    "Laser": ["6304"], "Switch": ["6759"], "InterPayment": ["4111"],
}

AG_BASLANGICLAR = {
    "Visa": ["4"],
    "MasterCard": ["51", "52", "53", "54", "55", "2221", "2222", "2720"],
    "American Express": ["34", "37"], "Discover": ["6011", "65"],
    "Troy": ["9792"], "UnionPay": ["62"], "Diners Club": ["36", "38", "300"],
    "JCB": ["3528", "3530", "3589"],
    "Maestro": ["5018", "5020", "5038", "5893", "6304", "6759"],
    "Elo": ["636368", "438935"], "MIR": ["2200", "2204"],
    "RuPay": ["60", "6521", "6522"], "Verve": ["506099", "5061", "5078", "6500"],
    "Dankort": ["5019"], "UATP": ["1"],
    "Laser": ["6304", "6706", "6771", "6709"],
    "Switch": ["6759", "564182", "633110"], "InterPayment": ["4111"],
}

BIN_VERITABANI = {
    "424242": {"kurum": "Stripe (resmî test)", "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "400000": {"kurum": "Stripe (resmî test)", "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "400005": {"kurum": "Stripe (resmî test)", "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "411111": {"kurum": "Genel test BIN (Visa)", "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "401288": {"kurum": "Genel test BIN (Visa)", "ulke": "US", "tip": "Kredi", "marka": "Visa"},
    "555555": {"kurum": "Genel test BIN (MC)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "510510": {"kurum": "Genel test BIN (MC)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "222300": {"kurum": "Genel test BIN (MC 2-serisi)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "222100": {"kurum": "Genel test BIN (MC 2-serisi)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "520082": {"kurum": "Stripe (resmî test)", "ulke": "US", "tip": "Kredi", "marka": "MasterCard"},
    "378282": {"kurum": "Genel test BIN (AMEX)", "ulke": "US", "tip": "Kredi", "marka": "American Express"},
    "371449": {"kurum": "Genel test BIN (AMEX)", "ulke": "US", "tip": "Kredi", "marka": "American Express"},
    "601111": {"kurum": "Genel test BIN (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "601100": {"kurum": "Genel test BIN (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "644564": {"kurum": "Genel test BIN (Discover)", "ulke": "US", "tip": "Kredi", "marka": "Discover"},
    "305693": {"kurum": "Genel test BIN (Diners)", "ulke": "US", "tip": "Kredi", "marka": "Diners Club"},
    "385200": {"kurum": "Genel test BIN (Diners)", "ulke": "US", "tip": "Kredi", "marka": "Diners Club"},
    "353011": {"kurum": "Genel test BIN (JCB)", "ulke": "JP", "tip": "Kredi", "marka": "JCB"},
    "356600": {"kurum": "Genel test BIN (JCB)", "ulke": "JP", "tip": "Kredi", "marka": "JCB"},
    "675964": {"kurum": "Genel test BIN (Maestro)", "ulke": "GB", "tip": "Banka", "marka": "Maestro"},
    "979202": {"kurum": "Troy test aralığı (TR)", "ulke": "TR", "tip": "Kredi", "marka": "Troy"},
    "620000": {"kurum": "Genel test BIN (UnionPay)", "ulke": "CN", "tip": "Kredi", "marka": "UnionPay"},
    "636368": {"kurum": "Genel test BIN (Elo)", "ulke": "BR", "tip": "Kredi", "marka": "Elo"},
}

ELO_BINLER = {
    "636368", "438935", "504175", "451416", "636297", "506699",
    "509048", "509067", "509049", "509069",
    "650031", "650033", "650035", "650051", "650054", "650057",
    "650058", "650059",
}


# ═══════════════════════════════════════════════════════════
# 3) ÇEKİRDEK
# ═══════════════════════════════════════════════════════════
def sadece_rakam(numara):
    return re.sub(r"\D", "", numara or "")


def luhn_dogrula(numara):
    rakamlar = [int(c) for c in sadece_rakam(numara)]
    if not 13 <= len(rakamlar) <= 19:
        return False
    toplam = 0
    for i, r in enumerate(reversed(rakamlar)):
        if i % 2 == 1:
            r *= 2
            if r > 9:
                r -= 9
        toplam += r
    return toplam % 10 == 0


def luhn_varyant_dogrula(numara):
    rakamlar = [int(c) for c in sadece_rakam(numara)]
    if not 13 <= len(rakamlar) <= 19:
        return False
    toplam = 0
    for i, r in enumerate(reversed(rakamlar)):
        if i % 2 == 1:
            r *= 2
            toplam += r // 10 + r % 10
        else:
            toplam += r
    return toplam % 10 == 0


def luhn_kontrol_rakami(prefix):
    rakamlar = [int(c) for c in prefix]
    toplam = 0
    for i, r in enumerate(reversed(rakamlar)):
        if i % 2 == 0:
            r *= 2
            if r > 9:
                r -= 9
        toplam += r
    return (10 - (toplam % 10)) % 10


def kart_ag(numara):
    rakam = sadece_rakam(numara)
    if not rakam:
        return "Bilinmiyor"
    if rakam.startswith("9792"):
        return "Troy"
    if rakam.startswith("1") and len(rakam) >= 13 and rakam[:2] != "13":
        return "UATP"
    if rakam.startswith("4"):
        return "Visa"
    if rakam[:2] in ("51", "52", "53", "54", "55"):
        return "MasterCard"
    if len(rakam) >= 4 and 2221 <= int(rakam[:4]) <= 2720:
        return "MasterCard"
    if rakam[:2] in ("34", "37"):
        return "American Express"
    if rakam[:3] in ("300", "301", "302", "303", "304", "305") or rakam[:2] in ("36", "38"):
        return "Diners Club"
    if len(rakam) >= 4 and 3528 <= int(rakam[:4]) <= 3589:
        return "JCB"
    if rakam[:6] in ELO_BINLER:
        return "Elo"
    if rakam[:4] == "6011" or rakam[:3] in ("644", "645", "646", "647", "648", "649") or rakam[:2] == "65":
        return "Discover"
    if rakam.startswith("62"):
        return "UnionPay"
    if rakam[:6] in ("564182", "633110"):
        return "Switch"
    if rakam[:4] in ("5018", "5020", "5038", "5893", "6304", "6759",
                     "6761", "6762", "6763", "6706", "6709", "6771"):
        return "Maestro"
    if rakam.startswith("5019"):
        return "Dankort"
    if rakam.startswith("2200") or rakam.startswith("2204"):
        return "MIR"
    if rakam[:6] in ("6521", "6522") or rakam[:4] == "6075":
        return "RuPay"
    if rakam[:6] in ("506099", "507865", "650018") or rakam[:4] in ("5061", "5078", "6500"):
        return "Verve"
    return "Bilinmiyor"


def uzunluk_bilgisi(numara, ag):
    uzunluk = len(sadece_rakam(numara))
    beklenen = AG_UZUNLUK.get(ag)
    if beklenen is None:
        return True, uzunluk, None
    return uzunluk in beklenen, uzunluk, beklenen


def cvv_dogrula(cvv, ag):
    cvv = str(cvv or "")
    beklenen = AG_CVV_UZUNLUK.get(ag, 3)
    if not cvv.isdigit() or len(cvv) != beklenen:
        return False, f"{beklenen} haneli olmalı"
    return True, "Geçerli"


def son_kullanma_dogrula(ay, yil):
    try:
        ay, yil = int(ay), int(yil)
    except (TypeError, ValueError):
        return False, "Ay/Yıl sayısal olmalı"
    if yil < 100:
        yil += 2000
    if not 1 <= ay <= 12:
        return False, "Ay 1-12 arasında olmalı"
    if yil < 2000 or yil > 2100:
        return False, "Yıl aralığı geçersiz"
    bugun = datetime.date.today()
    if yil < bugun.year or (yil == bugun.year and ay < bugun.month):
        return False, "Kartın süresi dolmuş"
    return True, "Geçerli"


def grupla(numara):
    return " ".join(numara[i:i + 4] for i in range(0, len(numara), 4))


def pan_maskela(numara):
    r = sadece_rakam(numara)
    if len(r) < 10:
        return "*" * len(r)
    return r[:6] + "*" * (len(r) - 10) + r[-4:]


def pan_hash(numara):
    return hashlib.sha256(sadece_rakam(numara).encode()).hexdigest()


def marka_normalize(marka):
    m = (marka or "").lower().replace(" ", "").replace("-", "").replace("_", "")
    esleme = {
        "visa": "Visa", "mastercard": "MasterCard", "amex": "American Express",
        "americanexpress": "American Express", "discover": "Discover",
        "dinersclub": "Diners Club", "jcb": "JCB", "unionpay": "UnionPay",
        "maestro": "Maestro", "elo": "Elo", "troy": "Troy", "mir": "MIR",
        "rupay": "RuPay", "verve": "Verve", "dankort": "Dankort",
        "uatp": "UATP", "laser": "Laser", "switch": "Switch",
        "interpayment": "InterPayment",
    }
    return esleme.get(m)


# ═══════════════════════════════════════════════════════════
# 4) RİSK MOTORU & SKOR
# ═══════════════════════════════════════════════════════════
def risk_analiz(numara, ag, luhn_ok, uzunluk_uygun, cvv_ok, skt_ok, bin_sonuc=None):
    faktorler, risk = [], 0.0
    if not luhn_ok:
        risk += 40; faktorler.append(("Luhn başarısız", 40, "kritik"))
    if ag == "Bilinmiyor":
        risk += 20; faktorler.append(("Ağ tespit edilemedi", 20, "yüksek"))
    if not uzunluk_uygun:
        risk += 15; faktorler.append(("Ağa uygun olmayan uzunluk", 15, "yüksek"))
    if cvv_ok is False:
        risk += 10; faktorler.append(("CVV formatı hatalı", 10, "orta"))
    if skt_ok is False:
        risk += 10; faktorler.append(("SKT geçersiz/süresi dolmuş", 10, "orta"))
    if bin_sonuc:
        if bin_sonuc.get("kaynak") in (None, "yok"):
            risk += 5; faktorler.append(("BIN kaydı bulunamadı", 5, "düşük"))
        if bin_sonuc.get("marka"):
            norm = marka_normalize(bin_sonuc["marka"])
            if norm and norm != ag:
                risk += 10
                faktorler.append((f"Marka uyuşmazlığı: {bin_sonuc['marka']} ≠ {ag}", 10, "yüksek"))
        if bin_sonuc.get("on_odeme") is True:
            risk += 5; faktorler.append(("Ön ödemeli kart", 5, "düşük"))
    r = sadece_rakam(numara)
    if r and len(set(r)) <= 2:
        risk += 10; faktorler.append(("Düşük entropi", 10, "orta"))
    if re.fullmatch(r"(\d)\1+", r or "x"):
        risk += 20; faktorler.append(("Tamamen tekrarlayan rakamlar", 20, "yüksek"))
    skor = min(100.0, risk)
    seviye = ("TEMİZ" if skor == 0 else "DÜŞÜK" if skor < 20
              else "ORTA" if skor < 50 else "YÜKSEK")
    return skor, faktorler, seviye


def risk_rapor(skor, faktorler, seviye):
    renk = {"TEMİZ": Renk.YESIL, "DÜŞÜK": Renk.CYAN, "ORTA": Renk.SARI,
            "YÜKSEK": Renk.KIRMIZI}.get(seviye, Renk.GRI)
    yaz()
    yaz(f"{Renk.BOLD}{Renk.SARI}── RİSK ANALİZİ ─────────────────────────────────────────{Renk.RESET}")
    bar = "█" * int(30 * skor / 100) + "░" * (30 - int(30 * skor / 100))
    yaz(f"  Risk Skoru : {renk}{skor:5.1f}/100{Renk.RESET}  [{renk}{bar}{Renk.RESET}]  {renk}{Renk.BOLD}{seviye}{Renk.RESET}")
    if faktorler:
        for ad, agirlik, cat in faktorler:
            crenk = {"kritik": Renk.KIRMIZI, "yüksek": Renk.SARI,
                     "orta": Renk.MAVI, "düşük": Renk.GRI}[cat]
            yaz(f"  {crenk}[{cat.upper():<6}]{Renk.RESET} {ad:<40} (+{agirlik})")
    else:
        yaz(f"  {Renk.YESIL}✓ Risk faktörü bulunamadı{Renk.RESET}")


def dogrulama_skoru(luhn_ok, luhn_var_ok, ag_biliniyor, uzunluk_uygun,
                    cvv_ok, skt_ok, bin_kayit_var):
    puan = 0.0
    if luhn_ok:      puan += 35
    if luhn_var_ok:  puan += 10
    if ag_biliniyor: puan += 15
    if uzunluk_uygun: puan += 15
    if cvv_ok is True: puan += 10
    if skt_ok is True: puan += 10
    if bin_kayit_var: puan += 5
    return puan


# ═══════════════════════════════════════════════════════════
# 5) ANALİZ
# ═══════════════════════════════════════════════════════════
def analiz_et(numara, cvv=None, ay=None, yil=None, bin_sonuc=None):
    rakam = sadece_rakam(numara)
    ag = kart_ag(rakam)
    luhn_ok = bool(rakam) and luhn_dogrula(rakam)
    luhn_var_ok = bool(rakam) and luhn_varyant_dogrula(rakam)
    uygun, uzunluk, beklenen = uzunluk_bilgisi(rakam, ag)
    cvv_ok = cvv_msj = None
    if cvv is not None:
        cvv_ok, cvv_msj = cvv_dogrula(cvv, ag)
    skt_ok = skt_msj = None
    if ay is not None and yil is not None:
        skt_ok, skt_msj = son_kullanma_dogrula(ay, yil)
    ek_ok = True
    if cvv_ok is not None:
        ek_ok = ek_ok and cvv_ok
    if skt_ok is not None:
        ek_ok = ek_ok and skt_ok
    gecerli = bool(rakam) and luhn_ok and uygun and ek_ok
    skor = dogrulama_skoru(luhn_ok, luhn_var_ok, ag != "Bilinmiyor", uygun,
                           cvv_ok, skt_ok,
                           bool(bin_sonuc and bin_sonuc.get("kaynak") not in (None, "yok")))
    return {
        "girdi": numara, "pan_maskeli": pan_maskela(rakam) if rakam else None,
        "pan_sha256": pan_hash(rakam) if rakam else None, "hane": uzunluk,
        "ag": ag, "beklenen_uzunluk": list(beklenen) if beklenen else None,
        "uzunluk_uygun": uygun, "luhn": luhn_ok, "luhn_varyant": luhn_var_ok,
        "cvv": {"girildi": cvv is not None, "gecerli": cvv_ok, "mesaj": cvv_msj},
        "skt": {"girildi": ay is not None and yil is not None,
                "gecerli": skt_ok, "mesaj": skt_msj},
        "dogrulama_skoru": skor, "gecerli": gecerli,
    }


# ═══════════════════════════════════════════════════════════
# 6) VERİTABANI KATMANI (SQLite/PostgreSQL/MySQL/Oracle/MSSQL)
# ═══════════════════════════════════════════════════════════
DB_TURLERI = ["sqlite", "postgresql", "mysql", "oracle", "mssql"]


def db_url_ayristir(url):
    """sqlite:///dosya.db | postgresql://u:p@h:5432/db | mysql://... |
       oracle://u:p@host:1521/?service_name=xe | mssql://u:p@host:1433/db"""
    m = re.match(r"^(sqlite|postgresql|postgres|mysql|oracle|mssql)://(.+)$", url.strip())
    if not m:
        return None, "URL formatı tanınamadı"
    tur, geri = m.group(1), m.group(2)
    tur = {"postgres": "postgresql"}.get(tur, tur)
    if tur == "sqlite":
        return {"tur": "sqlite", "yol": geri.replace("///", "/").lstrip("/") if geri.startswith("//") else geri}, None
    kimlik = re.match(r"^(?:(?P<u>[^:@/]*)(?::(?P<p>[^@/]*))?@)?(?P<host>[^/:?]+)(?::(?P<port>\d+))?(?:/(?P<db>[^?]*))?(?:\?(?P<params>.*))?$", geri)
    if not kimlik:
        return None, "Bağlantı parçası çözülemedi"
    return {
        "tur": tur,
        "kullanici": kimlik.group("u") or "",
        "parola": kimlik.group("p") or "",
        "host": kimlik.group("host"),
        "port": int(kimlik.group("port") or
                    {"postgresql": 5432, "mysql": 3306,
                     "oracle": 1521, "mssql": 1433}[tur]),
        "db": kimlik.group("db") or "",
        "params": kimlik.group("params") or "",
    }, None


class DBMotor:
    """Çoklu veritabanı soyutlaması. Tablolar:
       pg_dogrulama (doğrulama kayıtları), pg_bin_onbellek, pg_audit."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.tur = cfg["tur"]
        self.baglanti = None
        log_debug("DB", f"Motor başlatıldı: {self.tur}")

    # ── bağlantı ──
    def baglan(self):
        t = self.tur
        c = self.cfg
        try:
            if t == "sqlite":
                self.baglanti = sqlite3.connect(c["yol"])
                log_info("DB", f"SQLite bağlandı: {c['yol']}")
            elif t == "postgresql":
                if "postgresql" not in SURUCU:
                    return False, "psycopg2 kurulu değil: pip install psycopg2-binary"
                self.baglanti = SURUCU["postgresql"].connect(
                    host=c["host"], port=c["port"], user=c["kullanici"],
                    password=c["parola"], dbname=c["db"])
                log_info("DB", f"PostgreSQL bağlandı: {c['host']}:{c['port']}/{c['db']}")
            elif t == "mysql":
                if "mysql" not in SURUCU:
                    return False, "mysql-connector-python kurulu değil"
                self.baglanti = SURUCU["mysql"].connect(
                    host=c["host"], port=c["port"], user=c["kullanici"],
                    password=c["parola"], database=c["db"])
                log_info("DB", f"MySQL bağlandı: {c['host']}:{c['port']}/{c['db']}")
            elif t == "oracle":
                if "oracle" not in SURUCU:
                    return False, "oracledb kurulu değil: pip install oracledb"
                dsn = SURUCU["oracle"].makedsn(c["host"], c["port"], service_name=c["db"] or "XE")
                self.baglanti = SURUCU["oracle"].connect(
                    user=c["kullanici"], password=c["parola"], dsn=dsn)
                log_info("DB", f"Oracle bağlandı: {c['host']}:{c['port']}/{c['db'] or 'XE'}")
            elif t == "mssql":
                if "mssql" not in SURUCU:
                    return False, "pyodbc kurulu değil: pip install pyodbc"
                surucu_adi = next((s for s in pyodbc.drivers()
                                   if "ODBC Driver" in s or "SQL Server" in s), None)
                if not surucu_adi:
                    return False, "Sistemde ODBC SQL Server sürücüsü bulunamadı"
                bag = (f"DRIVER={{{surucu_adi}}};SERVER={c['host']},{c['port']};"
                       f"DATABASE={c['db'] or 'master'};UID={c['kullanici']};PWD={c['parola']};"
                       f"TrustServerCertificate=yes")
                self.baglanti = pyodbc.connect(bag)
                log_info("DB", f"MSSQL bağlandı: {c['host']}:{c['port']}/{c['db']}")
            else:
                return False, f"Desteklenmeyen tür: {t}"
            return True, None
        except Exception as e:
            return False, str(e)

    # ── sürüm sorgusu ──
    def surum(self):
        try:
            cur = self.baglanti.cursor()
            cur.execute({"sqlite": "SELECT sqlite_version()",
                         "postgresql": "SELECT version()",
                         "mysql": "SELECT VERSION()",
                         "oracle": "SELECT banner FROM v$version WHERE ROWNUM=1",
                         "mssql": "SELECT @@VERSION"}[self.tur])
            return str(cur.fetchone()[0])[:80]
        except Exception:
            return "bilinmiyor"

    # ── şema ──
    def sema_olustur(self):
        cur = self.baglanti.cursor()
        pk = {"sqlite": "INTEGER PRIMARY KEY AUTOINCREMENT",
              "postgresql": "BIGSERIAL PRIMARY KEY",
              "mysql": "BIGINT AUTO_INCREMENT PRIMARY KEY",
              "oracle": "NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY",
              "mssql": "BIGINT IDENTITY(1,1) PRIMARY KEY"}[self.tur]
        ts_t = {"oracle": "TIMESTAMP", "mssql": "DATETIME2"}.get(self.tur, "TIMESTAMP")

        if self.tur == "sqlite":
            cur.execute(f"""CREATE TABLE IF NOT EXISTS pg_dogrulama (
                id {pk}, zaman TEXT, pan_maskeli TEXT, pan_sha256 TEXT,
                hane INTEGER, ag TEXT, luhn INTEGER, luhn_varyant INTEGER,
                uzunluk_uygun INTEGER, cvv_gecerli INTEGER, skt_gecerli INTEGER,
                dogrulama_skoru REAL, risk_seviye TEXT, gecerli INTEGER)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS pg_bin_onbellek (
                bin TEXT PRIMARY KEY, veri TEXT, zaman TEXT)""")
            cur.execute(f"""CREATE TABLE IF NOT EXISTS pg_audit (
                id {pk}, zaman TEXT, islem TEXT, detay TEXT)""")
        elif self.tur == "oracle":
            # Oracle'da BIGSERIAL yok; IDENTITY ile
            try:
                cur.execute(f"""CREATE TABLE pg_dogrulama (
                    id {pk}, zaman {ts_t}, pan_maskeli VARCHAR2(24), pan_sha256 VARCHAR2(64),
                    hane INTEGER, ag VARCHAR2(32), luhn NUMBER(1), luhn_varyant NUMBER(1),
                    uzunluk_uygun NUMBER(1), cvv_gecerli NUMBER(1), skt_gecerli NUMBER(1),
                    dogrulama_skoru NUMBER, risk_seviye VARCHAR2(16), gecerli NUMBER(1))""")
            except Exception:
                pass   # tablo zaten var
            try:
                cur.execute("""CREATE TABLE pg_bin_onbellek (
                    bin VARCHAR2(10) PRIMARY KEY, veri CLOB, zaman {ts})""".format(ts=ts_t))
            except Exception:
                pass
            try:
                cur.execute(f"""CREATE TABLE pg_audit (
                    id {pk}, zaman {ts_t}, islem VARCHAR2(64), detay VARCHAR2(4000))""")
            except Exception:
                pass
        else:
            cur.execute(f"""CREATE TABLE IF NOT EXISTS pg_dogrulama (
                id {pk}, zaman {ts_t}, pan_maskeli VARCHAR(24), pan_sha256 VARCHAR(64),
                hane INT, ag VARCHAR(32), luhn SMALLINT, luhn_varyant SMALLINT,
                uzunluk_uygun SMALLINT, cvv_gecerli SMALLINT, skt_gecerli SMALLINT,
                dogrulama_skoru REAL, risk_seviye VARCHAR(16), gecerli SMALLINT)""")
            cur.execute(f"""CREATE TABLE IF NOT EXISTS pg_bin_onbellek (
                bin VARCHAR(10) PRIMARY KEY, veri TEXT, zaman {ts_t})""")
            cur.execute(f"""CREATE TABLE IF NOT EXISTS pg_audit (
                id {pk}, zaman {ts_t}, islem VARCHAR(64), detay TEXT)""")
        self.baglanti.commit()
        log_info("DB", "Şema hazır (pg_dogrulama, pg_bin_onbellek, pg_audit)")

    # ── yer tutucu dönüşümü (ORM'siz uyum) ──
    def _ph(self, sql):
        """DB'ye göre yer tutucu: sqlite/posgres/mssql ?, mysql %s, oracle :n"""
        if self.tur == "mysql":
            return sql.replace("?", "%s")
        if self.tur == "oracle":
            n = [0]
            def degistir(m):
                n[0] += 1
                return f":{n[0]}"
            return re.sub(r"\?", degistir, sql)
        return sql

    def _bool(self, v):
        """True/False/None → DB-friendly (Oracle/SQL Server için 1/0/NULL)."""
        if v is None:
            return None
        return 1 if v else 0

    # ── ekleme ──
    def dogrulama_ekle(self, s, risk_seviye=None):
        sql = self._ph("""INSERT INTO pg_dogrulama
            (zaman, pan_maskeli, pan_sha256, hane, ag, luhn, luhn_varyant,
             uzunluk_uygun, cvv_gecerli, skt_gecerli, dogrulama_skoru,
             risk_seviye, gecerli) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""")
        cur = self.baglanti.cursor()
        degerler = (datetime.datetime.now().isoformat(), s["pan_maskeli"],
                    s["pan_sha256"], s["hane"], s["ag"], self._bool(s["luhn"]),
                    self._bool(s["luhn_varyant"]), self._bool(s["uzunluk_uygun"]),
                    self._bool(s["cvv"]["gecerli"]), self._bool(s["skt"]["gecerli"]),
                    s["dogrulama_skoru"], risk_seviye, self._bool(s["gecerli"]))
        cur.execute(sql, degerler)
        self.baglanti.commit()
        log_debug("DB", f"Doğrulama kaydı eklendi: {s['pan_maskeli']}")

    def bin_onbelle_ekle(self, bin_no, veri_json):
        sql = self._ph("DELETE FROM pg_bin_onbellek WHERE bin = ?")
        cur = self.baglanti.cursor()
        cur.execute(sql, (bin_no,))
        cur.execute(self._ph("INSERT INTO pg_bin_onbellek (bin, veri, zaman) VALUES (?, ?, ?)"),
                    (bin_no, veri_json, datetime.datetime.now().isoformat()))
        self.baglanti.commit()

    def bin_onbelle_oku(self, bin_no):
        try:
            cur = self.baglanti.cursor()
            cur.execute(self._ph("SELECT veri FROM pg_bin_onbellek WHERE bin = ?"), (bin_no,))
            satir = cur.fetchone()
            return json.loads(satir[0]) if satir else None
        except Exception:
            return None

    def audit_ekle(self, islem, detay):
        cur = self.baglanti.cursor()
        cur.execute(self._ph("INSERT INTO pg_audit (zaman, islem, detay) VALUES (?, ?, ?)"),
                    (datetime.datetime.now().isoformat(), islem, detay))
        self.baglanti.commit()

    # ── sorgulama ──
    def gecmis(self, limit=20):
        cur = self.baglanti.cursor()
        cur.execute(self._ph(
            f"SELECT zaman, pan_maskeli, ag, luhn, dogrulama_skoru, gecerli "
            f"FROM pg_dogrulama ORDER BY id DESC LIMIT {int(limit)}"))
        return cur.fetchall()

    def istatistik(self):
        cur = self.baglanti.cursor()
        sonuc = {}
        cur.execute("SELECT COUNT(*) FROM pg_dogrulama")
        sonuc["toplam"] = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM pg_dogrulama WHERE gecerli = 1"
                    if self.tur not in ("oracle",) else
                    "SELECT COUNT(*) FROM pg_dogrulama WHERE gecerli = 1")
        sonuc["gecerli"] = int(cur.fetchone()[0])
        try:
            cur.execute(self._ph("SELECT ag, COUNT(*) FROM pg_dogrulama GROUP BY ag ORDER BY COUNT(*) DESC"))
            sonuc["aglar"] = cur.fetchall()
        except Exception:
            sonuc["aglar"] = []
        return sonuc


def db_baslat(url):
    """URL'den motor kurar; hata varsa (None, mesaj) döndürür."""
    cfg, hata = db_url_ayristir(url)
    if hata:
        return None, hata
    motor = DBMotor(cfg)
    ok, err = motor.baglan()
    if not ok:
        return None, err
    try:
        motor.sema_olustur()
    except Exception as e:
        return None, f"Şema hatası: {e}"
    return motor, None


# ═══════════════════════════════════════════════════════════
# 7) RAPOR (tek kart)
# ═══════════════════════════════════════════════════════════
def tam_rapor(numara, cvv=None, ay=None, yil=None, cikti=None,
              json_mod=False, tek=False, risk=False, bin_sonuc=None, db=None):
    sonuc = analiz_et(numara, cvv, ay, yil, bin_sonuc)

    risk_seviye = None
    if risk:
        rskor, rfakt, rsev = risk_analiz(
            numara, sonuc["ag"], sonuc["luhn"], sonuc["uzunluk_uygun"],
            sonuc["cvv"]["gecerli"], sonuc["skt"]["gecerli"], bin_sonuc)

    # DB kaydı
    if db:
        try:
            if risk:
                db.dogrulama_ekle(sonuc, risk_seviye=rsev)
            else:
                db.dogrulama_ekle(sonuc)
            db.audit_ekle("dogrulama", f"{sonuc['pan_maskeli']} → "
                          f"{'GECERLI' if sonuc['gecerli'] else 'GECERSIZ'}")
        except Exception as e:
            log_warn("DB", f"Kayıt eklenemedi: {e}")

    if json_mod:
        cikti_json = dict(sonuc)
        if risk:
            cikti_json["risk"] = {"skor": rskor, "seviye": rsev,
                                  "faktorler": [{"ad": a, "agirlik": w, "kategori": c}
                                                for a, w, c in rfakt]}
        metin = json.dumps(cikti_json, ensure_ascii=False, indent=2)
        yaz(metin)
        log_dosya(cikti, metin)
        return 0 if sonuc["gecerli"] else 1

    if tek:
        isaret = "GECERLI" if sonuc["gecerli"] else "GECERSIZ"
        yaz(f"{isaret}|{sonuc['ag']}|{sonuc['hane']}h|luhn={sonuc['luhn']}|"
            f"skor={sonuc['dogrulama_skoru']:.0f}|{sonuc['pan_maskeli']}")
        return 0 if sonuc["gecerli"] else 1

    yaz()
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    if not sadece_rakam(numara):
        yaz(f"{Renk.KIRMIZI}[!] Kart numarası boş.{Renk.RESET}")
        return 1

    yaz(f"{Renk.BOLD}Kart Numarası :{Renk.RESET} {Renk.CYAN}{numara}{Renk.RESET}")
    yaz(f"{Renk.BOLD}Maske (PCI)   :{Renk.RESET} {Renk.GRI}{sonuc['pan_maskeli']}{Renk.RESET}")
    yaz(f"{Renk.BOLD}PAN SHA-256   :{Renk.RESET} {Renk.GRI}{sonuc['pan_sha256'][:24]}…{Renk.RESET}")
    yaz(f"{Renk.BOLD}Kart Ağı      :{Renk.RESET} {sonuc['ag']}")
    beklenen = sonuc["beklenen_uzunluk"]
    if beklenen is None:
        u = f"({Renk.SARI}ağ tespit edilemedi{Renk.RESET})"
    elif sonuc["uzunluk_uygun"]:
        u = f"({Renk.YESIL}ağa uygun{Renk.RESET})"
    else:
        u = f"({Renk.KIRMIZI}ağa uygun değil, beklenen: {beklenen}{Renk.RESET})"
    yaz(f"{Renk.BOLD}Hane Sayısı   :{Renk.RESET} {sonuc['hane']} {u}")
    yaz(f"{Renk.BOLD}Luhn          :{Renk.RESET} "
        f"{Renk.YESIL}GEÇERLİ ✓{Renk.RESET}" if sonuc["luhn"] else
        f"{Renk.BOLD}Luhn          :{Renk.RESET} {Renk.KIRMIZI}GEÇERSİZ ✗{Renk.RESET}")
    yaz(f"{Renk.BOLD}Luhn Varyant  :{Renk.RESET} "
        + (f"{Renk.YESIL}✓{Renk.RESET}" if sonuc["luhn_varyant"]
           else f"{Renk.SARI}✗ (varyant uyumsuz){Renk.RESET}"))
    if sonuc["cvv"]["girildi"]:
        yaz(f"{Renk.BOLD}CVV           :{Renk.RESET} "
            + (f"{Renk.YESIL}Geçerli ✓{Renk.RESET}" if sonuc["cvv"]["gecerli"]
               else f"{Renk.KIRMIZI}{sonuc['cvv']['mesaj']} ✗{Renk.RESET}"))
    if sonuc["skt"]["girildi"]:
        yaz(f"{Renk.BOLD}SKT           :{Renk.RESET} "
            + (f"{Renk.YESIL}Geçerli ✓{Renk.RESET}" if sonuc["skt"]["gecerli"]
               else f"{Renk.KIRMIZI}{sonuc['skt']['mesaj']} ✗{Renk.RESET}"))
    skor = sonuc["dogrulama_skoru"]
    skrenk = Renk.YESIL if skor >= 80 else Renk.SARI if skor >= 50 else Renk.KIRMIZI
    yaz(f"{Renk.BOLD}Doğrulama Skoru:{Renk.RESET} {skrenk}{skor:.0f}/100{Renk.RESET}")
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    if sonuc["gecerli"]:
        yaz(f"{Renk.YESIL}{Renk.BOLD}SONUÇ: KART GEÇERLİ ✓{Renk.RESET}")
    else:
        yaz(f"{Renk.KIRMIZI}{Renk.BOLD}SONUÇ: KART GEÇERSİZ ✗{Renk.RESET}")
    if risk:
        risk_rapor(rskor, rfakt, rsev)
    log_dosya(cikti, f"{numara} → {'GEÇERLİ' if sonuc['gecerli'] else 'GEÇERSİZ'} "
                     f"(skor {skor:.0f}/100)")
    return 0 if sonuc["gecerli"] else 1


# ═══════════════════════════════════════════════════════════
# 8) BIN (TTL önbellek + DB önbellek)
# ═══════════════════════════════════════════════════════════
BIN_ONBELLEK_DOSYA = ".pg_bin_onbellek.json"
BIN_ONBELLEK_TTL = 7 * 24 * 3600
_bin_onbellek = {}
_son_sorgu_zamani = [0.0]


def onbellek_yukle():
    global _bin_onbellek
    if os.path.isfile(BIN_ONBELLEK_DOSYA):
        try:
            with open(BIN_ONBELLEK_DOSYA, "r", encoding="utf-8") as f:
                ham = json.load(f)
            simdi = time.time()
            _bin_onbellek = {k: v for k, v in ham.items()
                             if isinstance(v, dict) and (simdi - v.get("_ts", 0)) < BIN_ONBELLEK_TTL}
        except Exception:
            _bin_onbellek = {}


def onbellek_kaydet():
    try:
        with open(BIN_ONBELLEK_DOSYA, "w", encoding="utf-8") as f:
            json.dump(_bin_onbellek, f, ensure_ascii=False)
    except Exception:
        pass


def binlist_sorgula(bin_no, db=None, zaman_asimi=8):
    if bin_no in _bin_onbellek:
        return _bin_onbellek[bin_no].get("veri")
    if db:
        try:
            veri_db = db.bin_onbelle_oku(bin_no)
            if veri_db:
                return veri_db
        except Exception:
            pass
    gecen = time.time() - _son_sorgu_zamani[0]
    if gecen < 1.1:
        time.sleep(1.1 - gecen)
    try:
        _son_sorgu_zamani[0] = time.time()
        url = f"https://lookup.binlist.net/{bin_no}"
        istek = urllib.request.Request(url, headers={
            "User-Agent": f"{PROGRAM_ADI}/{SURUM}", "Accept-Version": "3"})
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
            veri = json.loads(yanit.read().decode("utf-8"))
            _bin_onbellek[bin_no] = {"_ts": time.time(), "veri": veri}
            onbellek_kaydet()
            if db:
                try:
                    db.bin_onbelle_ekle(bin_no, json.dumps(veri))
                except Exception:
                    pass
            return veri
    except Exception as e:
        log_warn("BIN", f"binlist sorgusu başarısız: {e}")
        return None


def bin_analiz(numara, online=False, bin8=False, db=None):
    rakam = sadece_rakam(numara)
    hane = 8 if bin8 and len(rakam) >= 8 else 6
    bin_no = rakam[:hane]
    sonuc = {"bin": bin_no, "bin_hane": hane, "marka": None, "kurum": None,
             "ulke": None, "tip": None, "on_odeme": None, "kaynak": None}
    kayit = BIN_VERITABANI.get(bin_no) or BIN_VERITABANI.get(rakam[:6])
    if kayit:
        sonuc.update(kayit)
        sonuc["kaynak"] = "yerleşik tablo (offline)"
    elif online:
        veri = binlist_sorgula(bin_no, db=db)
        if veri:
            sonuc["marka"] = veri.get("scheme")
            sonuc["tip"] = veri.get("type")
            sonuc["on_odeme"] = veri.get("prepaid")
            ulke = veri.get("country") or {}
            sonuc["ulke"] = ulke.get("name")
            banka = veri.get("bank") or {}
            sonuc["kurum"] = banka.get("name")
            sonuc["kaynak"] = "binlist.net (online)"
    if not sonuc["kaynak"]:
        sonuc["kaynak"] = "yok"
    return sonuc


def bin_rapor(numara, sonuc, cvv=None, ay=None, yil=None,
              json_mod=False, cikti=None, risk=False, db=None):
    rakam = sadece_rakam(numara)
    ag = kart_ag(rakam)
    derece1 = [("Luhn Kontrolü", luhn_dogrula(rakam)),
               ("Kart Ağı Tespiti", ag != "Bilinmiyor")]
    uygun, _, beklenen = uzunluk_bilgisi(rakam, ag)
    derece1.append(("Uzunluk Uygunluğu", uygun if beklenen is not None else None))
    if cvv is not None or (ay is not None and yil is not None):
        cvv_ok, skt_ok = True, True
        if cvv is not None:
            cvv_ok, _ = cvv_dogrula(cvv, ag)
        if ay is not None and yil is not None:
            skt_ok, _ = son_kullanma_dogrula(ay, yil)
        derece1.append(("CVV/SKT Kontrolü", cvv_ok and skt_ok))
    else:
        derece1.append(("CVV/SKT Kontrolü", None))
    kayit_var = sonuc.get("kaynak") not in (None, "yok")
    marka_uyum = None
    if sonuc.get("marka"):
        marka_uyum = (marka_normalize(sonuc["marka"]) == ag) and ag != "Bilinmiyor"
    derece2 = [("BIN Kaydı", kayit_var), ("Marka Uyumu", marka_uyum),
               ("Kurum Bilgisi", bool(sonuc.get("kurum"))),
               ("Ülke Bilgisi", bool(sonuc.get("ulke")))]
    kazanc = sum(1 for _, ok in derece1 + derece2 if ok is True)
    toplam = sum(1 for _, ok in derece1 + derece2 if ok is not None)
    durum = ("veri yok" if toplam == 0 else "YÜKSEK tutarlılık" if kazanc == toplam
             else "ORTA tutarlılık" if kazanc >= toplam / 2 else "DÜŞÜK tutarlılık")

    if json_mod:
        metin = json.dumps({
            "girdi_maskeli": pan_maskela(rakam), "ag": ag,
            "katman1": [{"kontrol": a, "gecerli": b} for a, b in derece1],
            "katman2": [{"kontrol": a, "gecerli": b} for a, b in derece2],
            "bin": sonuc,
            "realite_skoru": {"kazanc": kazanc, "toplam": toplam, "durum": durum}},
            ensure_ascii=False, indent=2)
        yaz(metin)
        log_dosya(cikti, metin)
        return 0 if kazanc == toplam else 1

    yaz()
    yaz(Renk.MAVI + "═" * 62 + Renk.RESET)
    yaz(f"{Renk.BOLD}{Renk.SARI} BIN / VERİTABANI ANALİZİ{Renk.RESET}")
    yaz(Renk.MAVI + "═" * 62 + Renk.RESET)
    yaz(f"{Renk.BOLD}Numara    :{Renk.RESET} {Renk.CYAN}{pan_maskela(rakam)}{Renk.RESET}")
    yaz(f"{Renk.BOLD}BIN ({sonuc['bin_hane']}) :{Renk.RESET} {sonuc['bin']}")
    yaz(f"{Renk.BOLD}Tespit Ağ :{Renk.RESET} {ag}")
    for baslik, derece in (("KATMAN 1 — NUMARA DOĞRULAMA", derece1),
                           ("KATMAN 2 — BIN / KURUM ANALİZİ", derece2)):
        yaz()
        yaz(f"{Renk.BOLD}{Renk.MAVI}{baslik}{Renk.RESET}")
        for ad, ok in derece:
            g = (f"{Renk.GRI}—{Renk.RESET}" if ok is None
                 else f"{Renk.YESIL}✓{Renk.RESET}" if ok else f"{Renk.KIRMIZI}✗{Renk.RESET}")
            yaz(f"  [{Renk.CYAN}D{Renk.RESET}] {ad:<22} : {g}")
    yaz()
    yaz(f"{Renk.BOLD}{Renk.SARI}BIN Detayları:{Renk.RESET}")
    kaynak_str = (f"{Renk.YESIL}{sonuc['kaynak']}{Renk.RESET}" if kayit_var
                  else f"{Renk.KIRMIZI}kayıt yok{Renk.RESET}")
    yaz(f"  Kaynak      : {kaynak_str}")
    for anahtar, ad in (("marka", "BIN Markası"), ("kurum", "Kurum"),
                        ("ulke", "Ülke"), ("tip", "Tip")):
        deger = sonuc.get(anahtar)
        yaz(f"  {ad:<12}: {deger if deger else Renk.GRI + 'bilinmiyor' + Renk.RESET}")
    if sonuc.get("on_odeme") is not None:
        yaz(f"  Ön Ödemeli  : {'Evet' if sonuc['on_odeme'] else 'Hayır'}")
    yaz(Renk.MAVI + "═" * 62 + Renk.RESET)
    yaz(f"{Renk.BOLD}REALİTE SKORU:{Renk.RESET} {Renk.YESIL}{kazanc}/{toplam}{Renk.RESET} ({durum})")
    if risk:
        s = analiz_et(rakam, cvv=cvv, ay=ay, yil=yil, bin_sonuc=sonuc)
        rskor, rfakt, rsev = risk_analiz(rakam, ag, s["luhn"], s["uzunluk_uygun"],
                                         s["cvv"]["gecerli"], s["skt"]["gecerli"], sonuc)
        risk_rapor(rskor, rfakt, rsev)
    yaz(Renk.MAVI + "═" * 62 + Renk.RESET)
    log_dosya(cikti, f"BIN {sonuc['bin']} → {kazanc}/{toplam} ({durum})")
    return 0 if kazanc == toplam else 1


# ═══════════════════════════════════════════════════════════
# 9) ÜRETİCİ & TEST KARTLARI
# ═══════════════════════════════════════════════════════════
def kart_uret(ag, adet=1, desen=None, skt_uret=False):
    kaynaklar = TEST_BINLER.get(ag) or AG_BASLANGICLAR.get(ag, [])
    if not kaynaklar:
        return []
    sonuclar, gorulen = [], set()
    deneme = 0
    while len(sonuclar) < adet and deneme < adet * 200:
        deneme += 1
        bas = random.choice(kaynaklar)
        hedef = random.choice(AG_UZUNLUK.get(ag, (16,)))
        eksik = hedef - len(bas) - 1
        if eksik < 0:
            continue
        prefix = bas + "".join(random.choice("0123456789") for _ in range(eksik))
        kart = prefix + str(luhn_kontrol_rakami(prefix))
        if kart in gorulen:
            continue
        if desen and not re.fullmatch(desen, kart):
            continue
        gorulen.add(kart)
        if skt_uret:
            yil = datetime.date.today().year + random.randint(1, 5)
            sonuclar.append({"kart": kart,
                             "skt": f"{random.randint(1, 12):02d}/{yil}",
                             "cvv": "".join(random.choice("0123456789")
                                            for _ in range(AG_CVV_UZUNLUK.get(ag, 3)))})
        else:
            sonuclar.append(kart)
    return sonuclar


TEST_KARTLARI = [
    ("4242 4242 4242 4242", "Visa", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("4000 0000 0000 0002", "Visa", "Stripe", "redd", "❌ Reddedilir (genel)"),
    ("4000 0000 0000 9995", "Visa", "Stripe", "yetersiz", "❌ Yetersiz bakiye"),
    ("4000 0000 0000 3220", "Visa", "Stripe", "3ds", "🔐 3DS doğrulama"),
    ("4000 0000 0000 0341", "Visa", "Stripe", "3ds", "🔐 3DS2 doğrulama"),
    ("4000 0000 0000 9235", "Visa", "Stripe", "3ds", "🔐 3DS2 doğrulama"),
    ("4000 0000 0000 3063", "Visa", "Stripe", "3ds", "🔐 3DS2 doğrulama"),
    ("4000 0000 0000 0069", "Visa", "Stripe", "sure_dolmus", "❌ Kart süresi dolmuş"),
    ("4000 0000 0000 0127", "Visa", "Stripe", "cvc_hatali", "❌ Hatalı CVC"),
    ("4000 0000 0000 0077", "Visa", "Stripe", "risk", "❌ Reddedilir (risk)"),
    ("4000 0000 0000 0101", "Visa", "Stripe", "islem_hatasi", "❌ İşlem hatası"),
    ("5555 5555 5555 4444", "MasterCard", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("2223 0000 4841 0010", "MasterCard", "Stripe", "basari", "✅ Başarılı (2-serisi)"),
    ("5105 1051 0510 5100", "MasterCard", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("5200 8282 8282 8210", "MasterCard", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("3782 822463 10005", "American Express", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("3714 496353 98431", "American Express", "Stripe", "redd", "❌ Reddedilir"),
    ("6011 1111 1111 1117", "Discover", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("6011 0009 9013 9424", "Discover", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("3056 9309 0259 04", "Diners Club", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("3530 1113 3330 0000", "JCB", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("3566 0020 2036 0505", "JCB", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("6759 6498 2643 8453", "Maestro", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("6200 0000 0000 0005", "UnionPay", "Stripe", "basari", "✅ Başarılı ödeme"),
    ("4111 1111 1111 1111", "Visa", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("4000 1111 1111 1115", "Visa", "Braintree/PayPal", "redd", "❌ Reddedilir"),
    ("4012 8888 8888 1881", "Visa", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("4222 2222 2222 2", "Visa", "Braintree/PayPal", "basari", "✅ Başarılı (13 hane)"),
    ("5555 5555 5555 4444", "MasterCard", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("2221 0000 0000 0009", "MasterCard", "Braintree/PayPal", "basari", "✅ Başarılı (2-serisi)"),
    ("3782 822463 10005", "American Express", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("6011 1111 1111 1117", "Discover", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("3852 0000 0232 37", "Diners Club", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
    ("3530 1113 3330 0000", "JCB", "Braintree/PayPal", "basari", "✅ Başarılı ödeme"),
]

SENONYOLAR = {
    "basari": "✅ Başarı", "redd": "❌ Red", "3ds": "🔐 3DS",
    "yetersiz": "❌ Yetersiz bakiye", "sure_dolmus": "❌ Süre dolmuş",
    "cvc_hatali": "❌ Hatalı CVC", "risk": "❌ Risk",
    "islem_hatasi": "❌ İşlem hatası",
}


def test_kartlari_goster(senaryo=None, json_mod=False, cikti=None):
    if senaryo and senaryo not in SENONYOLAR:
        yaz(f"{Renk.KIRMIZI}[!] Geçersiz senaryo. Seçenekler: {', '.join(SENONYOLAR)}{Renk.RESET}")
        return 2
    filtreli = [k for k in TEST_KARTLARI if not senaryo or k[3] == senaryo]
    if json_mod:
        veri = [{"kart": k, "ag": a, "saglayici": s, "senaryo": sen,
                 "davranis": d, "luhn": luhn_dogrula(k), "tespit_ag": kart_ag(k)}
                for k, a, s, sen, d in filtreli]
        metin = json.dumps(veri, ensure_ascii=False, indent=2)
        yaz(metin)
        log_dosya(cikti, metin)
        return 0
    yaz(f"\n{Renk.BOLD}{Renk.SARI}=== ONAYLI TEST KARTLARI (Stripe + Braintree + PayPal) ==={Renk.RESET}")
    if senaryo:
        yaz(f"{Renk.SARI}Senaryo: {SENONYOLAR[senaryo]}{Renk.RESET}")
    yaz(f"{Renk.GRI}Not: Yalnızca SANDBOX ortamında işleme alınır.{Renk.RESET}\n")
    mevcut = None
    for kart, ag, saglayici, sen, davranis in filtreli:
        if saglayici != mevcut:
            mevcut = saglayici
            yaz(f"{Renk.BOLD}{Renk.MAVI}── {saglayici} ─────────────────────────────{Renk.RESET}")
        luhn = luhn_dogrula(kart)
        tespit = kart_ag(kart)
        durum = f"{Renk.YESIL}geçerli{Renk.RESET}" if luhn else f"{Renk.KIRMIZI}GEÇERSİZ!{Renk.RESET}"
        uyum = f"{Renk.YESIL}✓{Renk.RESET}" if tespit == ag else f"{Renk.KIRMIZI}✗ ({tespit}){Renk.RESET}"
        yaz(f"  {Renk.CYAN}{kart:<23}{Renk.RESET} [{ag:<15}] {davranis:<30} Luhn: {durum} Ağ: {uyum}")
    yaz(f"\n{Renk.SARI}Ek bilgiler: CVV 123 (AMEX 1234) | SKT gelecek tarih | İsim serbest{Renk.RESET}")
    return 0


# ═══════════════════════════════════════════════════════════
# 10) TOPLU + ÇIKTILAR
# ═══════════════════════════════════════════════════════════
def ornek_dosya_olustur(dosya):
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


def _csv_yaz(dosya, kayitlar):
    try:
        with open(dosya, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["kart", "maske", "ag", "luhn", "cvv_gecerli",
                        "skt_gecerli", "skor", "sonuc"])
            for s in kayitlar:
                w.writerow([s["girdi"], s["pan_maskeli"], s["ag"], s["luhn"],
                            s["cvv"]["gecerli"], s["skt"]["gecerli"],
                            f"{s['dogrulama_skoru']:.0f}",
                            "GECERLI" if s["gecerli"] else "GECERSIZ"])
        return True
    except Exception as e:
        log_error("CSV", str(e))
        return False


def _jsonl_yaz(dosya, kayitlar):
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            for s in kayitlar:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        log_error("JSONL", str(e))
        return False


def _html_rapor_yaz(dosya, kayitlar, ozet):
    satirlar = []
    for s in kayitlar:
        renk = "#2ecc71" if s["gecerli"] else "#e74c3c"
        durum = "GEÇERLİ" if s["gecerli"] else "GEÇERSİZ"
        satirlar.append(
            f"<tr style='color:{renk}'><td>{s['pan_maskeli']}</td><td>{s['ag']}</td>"
            f"<td>{'✓' if s['luhn'] else '✗'}</td>"
            f"<td>{s['dogrulama_skoru']:.0f}</td><td>{durum}</td></tr>")
    html = f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<title>Payment_grand {SURUM} Raporu</title>
<style>body{{font-family:monospace;background:#1e1e2e;color:#cdd6f4;padding:2em}}
h1{{color:#cba6f7}} table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #45475a;padding:6px 10px;text-align:left}}
th{{background:#313244;color:#89b4fa}}</style></head><body>
<h1>Payment_grand v{SURUM} ULTIMATE — Toplu Rapor</h1>
<p>Toplam: {ozet['toplam']} | Geçerli: {ozet['gecerli']} | Geçersiz: {ozet['gecersiz']}
| {datetime.datetime.now().isoformat()}</p>
<table><tr><th>Maske</th><th>Ağ</th><th>Luhn</th><th>Skor</th><th>Sonuç</th></tr>
{''.join(satirlar)}</table>
<p><small>Yalnızca test/sandbox kullanımı. PCI-DSS maskeli.</small></p></body></html>"""
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    except Exception as e:
        log_error("HTML", str(e))
        return False


def dosyadan_dogrula(dosya, db=None, cikti=None, json_mod=False,
                     csv_cikti=None, jsonl_cikti=None, html_cikti=None):
    if not os.path.isfile(dosya):
        yaz(f"{Renk.KIRMIZI}[!] Dosya bulunamadı: {dosya}{Renk.RESET}")
        return 2
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            satirlar = [s.strip() for s in f if s.strip()]
    except Exception as e:
        yaz(f"{Renk.KIRMIZI}[!] Okunamadı: {e}{Renk.RESET}")
        return 2
    yaz(f"\n{Renk.BOLD}{Renk.SARI}Toplu doğrulama ({len(satirlar)} satır){Renk.RESET}")
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    dogru = yanlis = 0
    kayitlar = []
    for no, satir in enumerate(satirlar, 1):
        parcalar = [p.strip() for p in satir.replace(";", ",").split(",")]
        kart = parcalar[0]
        cvv = parcalar[1] if len(parcalar) > 1 and parcalar[1] else None
        ay = parcalar[2] if len(parcalar) > 2 and parcalar[2] else None
        yil = parcalar[3] if len(parcalar) > 3 and parcalar[3] else None
        s = analiz_et(kart, cvv=cvv, ay=ay, yil=yil)
        kayitlar.append(s)
        if db:
            try:
                db.dogrulama_ekle(s)
            except Exception as e:
                log_warn("DB", f"Kayıt: {e}")
        if s["gecerli"]:
            dogru += 1
            isaret = f"{Renk.YESIL}✓ GEÇERLİ{Renk.RESET}"
        else:
            yanlis += 1
            isaret = f"{Renk.KIRMIZI}✗ GEÇERSİZ{Renk.RESET}"
        yaz(f"  {no:>3}. {Renk.CYAN}{s['pan_maskeli']:<23}{Renk.RESET} [{s['ag']}] {isaret}")
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    yaz(f"{Renk.YESIL}Geçerli: {dogru}{Renk.RESET}  {Renk.KIRMIZI}Geçersiz: {yanlis}{Renk.RESET}  "
        f"{Renk.SARI}Toplam: {len(satirlar)}{Renk.RESET}")
    ozet = {"toplam": len(satirlar), "gecerli": dogru, "gecersiz": yanlis}
    if json_mod:
        metin = json.dumps({**ozet, "kayitlar": kayitlar}, ensure_ascii=False, indent=2)
        yaz(metin)
        log_dosya(cikti, metin)
    if csv_cikti and _csv_yaz(csv_cikti, kayitlar):
        yaz(f"{Renk.YESIL}[+] CSV: {csv_cikti}{Renk.RESET}")
    if jsonl_cikti and _jsonl_yaz(jsonl_cikti, kayitlar):
        yaz(f"{Renk.YESIL}[+] JSONL: {jsonl_cikti}{Renk.RESET}")
    if html_cikti and _html_rapor_yaz(html_cikti, kayitlar, ozet):
        yaz(f"{Renk.YESIL}[+] HTML: {html_cikti}{Renk.RESET}")
    if db:
        try:
            db.audit_ekle("toplu_dogrulama", f"{len(satirlar)} satır, {dogru} geçerli")
        except Exception:
            pass
    return 0


# ═══════════════════════════════════════════════════════════
# 11) KENDİ KENDİNİ TEST
# ═══════════════════════════════════════════════════════════
def oz_test():
    yaz(f"\n{Renk.BOLD}{Renk.SARI}=== KENDİ KENDİNİ TEST ==={Renk.RESET}")
    kontroller = []
    for kart, bekl in [("4242424242424242", True), ("4242424242424241", False),
                       ("378282246310005", True), ("5555555555554444", True),
                       ("1234567890123456", False)]:
        kontroller.append((f"Luhn: {kart}", luhn_dogrula(kart) == bekl))
        kontroller.append((f"Varyant: {kart}", luhn_varyant_dogrula(kart) == bekl))
    for _ in range(50):
        prefix = "".join(random.choice("0123456789") for _ in range(15))
        kart = prefix + str(luhn_kontrol_rakami(prefix))
        kontroller.append((f"Üret→Doğrula: {pan_maskela(kart)}", luhn_dogrula(kart)))
    for kart, bekl_ag in [("4242424242424242", "Visa"),
                          ("5555555555554444", "MasterCard"),
                          ("378282246310005", "American Express"),
                          ("9792021234561234", "Troy"),
                          ("2200001234561234", "MIR"),
                          ("5019711234561234", "Dankort")]:
        kontroller.append((f"Ağ: {bekl_ag}", kart_ag(kart) == bekl_ag))
    kontroller += [
        ("CVV: AMEX 4 hane", cvv_dogrula("1234", "American Express")[0]),
        ("CVV: Visa 4 hane reddedilmeli", not cvv_dogrula("1234", "Visa")[0]),
        ("SKT: geçmiş reddedilmeli", not son_kullanma_dogrula("01", "2020")[0]),
        ("SKT: ay 13 reddedilmeli", not son_kullanma_dogrula("13", "2028")[0]),
        ("Maske: doğru", pan_maskela("4242424242424242") == "424242******4242"),
        ("Hash: 64 hex", re.fullmatch(r"[0-9a-f]{64}", pan_hash("4242424242424242")) is not None),
        ("DB URL: sqlite", db_url_ayristir("sqlite:///test.db")[0]["tur"] == "sqlite"),
        ("DB URL: postgres", db_url_ayristir("postgresql://u:p@h:5432/x")[0]["port"] == 5432),
    ]
    _, _, sev = risk_analiz("4242424242424242", "Visa", True, True, True, True)
    kontroller.append(("Risk: temiz kart", sev in ("TEMİZ", "DÜŞÜK")))
    _, _, sev2 = risk_analiz("1111111111111111", "Bilinmiyor", False, True, None, None)
    kontroller.append(("Risk: 1111... YÜKSEK", sev2 == "YÜKSEK"))

    gecen = hata = 0
    for ad, ok in kontroller:
        if ok:
            gecen += 1
            yaz(f"  {Renk.YESIL}✓{Renk.RESET} {ad}")
        else:
            hata += 1
            yaz(f"  {Renk.KIRMIZI}✗{Renk.RESET} {ad}")
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    yaz(f"{Renk.YESIL}Geçen: {gecen}{Renk.RESET}   {Renk.KIRMIZI}Hatalı: {hata}{Renk.RESET}")
    return 0 if hata == 0 else 1


# ═══════════════════════════════════════════════════════════
# 12) MENÜ
# ═══════════════════════════════════════════════════════════
def sor(metin):
    return input(f"{Renk.CYAN}[?]{Renk.RESET} {metin}").strip()


def db_menu():
    yaz(f"\n{Renk.BOLD}{Renk.SARI}── VERİTABANI ─────────────────────────────{Renk.RESET}")
    yaz(f"  Kurulu sürücüler: {', '.join(SURUCU) if SURUCU else 'sadece sqlite'}")
    yaz(f"  Formatlar:")
    yaz(f"    sqlite      : {Renk.CYAN}sqlite:///dosya.db{Renk.RESET}")
    yaz(f"    postgresql  : {Renk.CYAN}postgresql://user:parola@host:5432/veritabani{Renk.RESET}")
    yaz(f"    mysql       : {Renk.CYAN}mysql://user:parola@host:3306/veritabani{Renk.RESET}")
    yaz(f"    oracle      : {Renk.CYAN}oracle://user:parola@host:1521/XEPDB1{Renk.RESET}")
    yaz(f"    mssql       : {Renk.CYAN}mssql://user:parola@host:1433/veritabani{Renk.RESET}")
    url = sor("Bağlantı URL'si [varsayılan: sqlite:///payment_grand.db]: ")
    url = url or "sqlite:///payment_grand.db"
    motor, hata = db_baslat(url)
    if not motor:
        yaz(f"{Renk.KIRMIZI}[!] DB başlatılamadı: {hata}{Renk.RESET}")
        return None
    yaz(f"{Renk.YESIL}[+] Bağlantı başarılı. Sunucu: {motor.surum()}{Renk.RESET}")
    return motor


def ana_menu_goster():
    yaz(BANNER)
    c = Renk.MAVI
    W = 66
    yaz(c + "┌" + "─" * W + "┐" + Renk.RESET)
    yaz(c + "│" + Renk.RESET + Renk.BOLD + Renk.SARI + " ANA MENÜ".ljust(W) + Renk.RESET + c + "│" + Renk.RESET)
    yaz(c + "├" + "─" * W + "┤" + Renk.RESET)
    satirlar = [
        (" [1]", " Tek Kart Doğrula", Renk.CYAN),
        (" [2]", " Tam Form Kontrolü (CVV + SKT + Risk)", Renk.CYAN),
        (" [3]", " Onaylı Test Kartları (senaryo filtreli)", Renk.CYAN),
        (" [4]", " Toplu Doğrulama (CSV/JSON/JSONL/HTML)", Renk.CYAN),
        (" [5]", " Test Kartı Üret (SKT/CVV dahil)", Renk.CYAN),
        (" [6]", " BIN / Veritabanı Sorgulama", Renk.CYAN),
        (" [7]", " PAN Maske / SHA-256 Parmak İzi", Renk.CYAN),
        (" [8]", " Risk Analizi (tek kart)", Renk.CYAN),
        (" [9]", " VERİTABANI: Bağlan / Geçmiş / İstatistik", Renk.MOR),
        (" [o]", " Kendi Kendini Test Et", Renk.CYAN),
        (" [h]", " Hakkında / Yardım", Renk.CYAN),
        (" [0]", " Çıkış", Renk.KIRMIZI),
    ]
    for num, metin, renk in satirlar:
        duz = num + metin
        yaz(c + "│" + Renk.RESET + renk + duz + Renk.RESET + " " * (W - len(duz)) + c + "│" + Renk.RESET)
    yaz(c + "└" + "─" * W + "┘" + Renk.RESET)


def ana_menu():
    motor = None
    while True:
        ana_menu_goster()
        db_durum = f"DB: {motor.tur if motor else 'kapalı'}"
        try:
            secim = input(f"\n{Renk.CYAN}[?]{Renk.RESET} Seçiminiz {Renk.GRI}({db_durum}){Renk.RESET}: ").strip()
        except (EOFError, KeyboardInterrupt):
            yaz(f"\n{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
            return
        if secim == "0":
            yaz(f"{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
            return
        elif secim == "1":
            girdi = sor("Kart numarası: ")
            if girdi:
                tam_rapor(girdi, db=motor)
        elif secim == "2":
            numara = sor("Kart numarası: ")
            if not numara:
                continue
            cvv = sor("CVV (boş geçilebilir): ")
            ay = sor("SKT ay (boş geçilebilir): ")
            yil = sor("SKT yıl (boş geçilebilir): ")
            tam_rapor(numara, cvv=cvv or None, ay=ay or None, yil=yil or None,
                      risk=True, db=motor)
        elif secim == "3":
            sen = sor(f"Senaryo ({'/'.join(SENONYOLAR)}, boş=tümü): ") or None
            test_kartlari_goster(senaryo=sen)
        elif secim == "4":
            girdi = sor("Dosya yolu [kartlar.txt]: ") or "kartlar.txt"
            if not os.path.isfile(girdi):
                cevap = input(f"{Renk.SARI}[i] '{girdi}' yok. Örnek oluşturulsun mu? (e/H): {Renk.RESET}").strip().lower()
                if cevap in ("e", "evet", "y", "yes") and ornek_dosya_olustur(girdi):
                    yaz(f"{Renk.YESIL}[+] Oluşturuldu: {girdi}{Renk.RESET}")
                else:
                    continue
            html = sor("HTML rapor (boş=kapalı): ") or None
            csvc = sor("CSV çıktı (boş=kapalı): ") or None
            jsonl = sor("JSONL çıktı (boş=kapalı): ") or None
            dosyadan_dogrula(girdi, db=motor, csv_cikti=csvc,
                             jsonl_cikti=jsonl, html_cikti=html)
        elif secim == "5":
            aglar = sorted(TEST_BINLER.keys())
            yaz(f"{Renk.BOLD}Kart ağı seçin:{Renk.RESET}")
            for i, a in enumerate(aglar, 1):
                yaz(f"  {Renk.CYAN}[{i}]{Renk.RESET} {a}")
            sec = sor("Seçim: ")
            if not sec.isdigit() or not (1 <= int(sec) <= len(aglar)):
                continue
            ag = aglar[int(sec) - 1]
            try:
                adet = max(1, min(int(sor("Kaç adet [1]: ") or "1"), 20))
            except ValueError:
                adet = 1
            skt_istek = input(f"{Renk.SARI}SKT + CVV üret? (e/H): {Renk.RESET}").strip().lower() in ("e", "evet", "y", "yes")
            kartlar = kart_uret(ag, adet, skt_uret=skt_istek)
            yaz(f"\n{Renk.YESIL}{Renk.BOLD}Üretilen TEST kartları ({ag}):{Renk.RESET}")
            for k in kartlar:
                if skt_istek:
                    yaz(f"  {Renk.CYAN}{grupla(k['kart'])}{Renk.RESET}  SKT: {k['skt']}  CVV: {k['cvv']}")
                else:
                    yaz(f"  {Renk.CYAN}{grupla(k)}{Renk.RESET}")
            yaz(f"{Renk.GRI}[i] Yalnızca resmî sandbox BIN'leri. Gerçek kart değildir.{Renk.RESET}")
        elif secim == "6":
            numara = sor("Kart numarası veya BIN: ")
            if len(sadece_rakam(numara)) < 6:
                yaz(f"{Renk.KIRMIZI}[!] En az 6 hane gerekli.{Renk.RESET}")
                continue
            online = input(f"{Renk.SARI}Çevrimiçi (binlist.net)? (e/H): {Renk.RESET}").strip().lower() in ("e", "evet", "y", "yes")
            bin8 = input(f"{Renk.SARI}8 haneli BIN? (e/H): {Renk.RESET}").strip().lower() in ("e", "evet", "y", "yes")
            sonuc = bin_analiz(numara, online=online, bin8=bin8, db=motor)
            bin_rapor(numara, sonuc, risk=True, db=motor)
        elif secim == "7":
            numara = sor("Kart numarası: ")
            r = sadece_rakam(numara)
            if r:
                yaz(f"{Renk.YESIL}Maske (PCI-DSS): {pan_maskela(r)}\nPAN SHA-256   : {pan_hash(r)}{Renk.RESET}")
        elif secim == "8":
            numara = sor("Kart numarası: ")
            s = analiz_et(numara)
            rskor, rfakt, rsev = risk_analiz(numara, s["ag"], s["luhn"],
                                             s["uzunluk_uygun"],
                                             s["cvv"]["gecerli"], s["skt"]["gecerli"])
            risk_rapor(rskor, rfakt, rsev)
        elif secim == "9":
            motor = db_menu() or motor
            if motor:
                yaz(f"\n{Renk.BOLD}Alt seçenek:{Renk.RESET}")
                yaz(f"  {Renk.CYAN}[1]{Renk.RESET} Geçmişi listele")
                yaz(f"  {Renk.CYAN}[2]{Renk.RESET} İstatistik")
                yaz(f"  {Renk.CYAN}[3]{Renk.RESET} Bağlantıyı kapat")
                alt = sor("Seçim [1]: ") or "1"
                if alt == "1":
                    try:
                        kayitlar = motor.gecmis(20)
                        yaz(f"\n{Renk.BOLD}{Renk.SARI}Son {len(kayitlar)} doğrulama kaydı:{Renk.RESET}")
                        for k in kayitlar:
                            g = f"{Renk.YESIL}✓{Renk.RESET}" if k[5] else f"{Renk.KIRMIZI}✗{Renk.RESET}"
                            yaz(f"  {g} {str(k[0])[:19]}  {k[1]:<22} [{k[2]}] luhn={k[3]} skor={float(k[4]):.0f}")
                    except Exception as e:
                        yaz(f"{Renk.KIRMIZI}[!] Sorgu hatası: {e}{Renk.RESET}")
                elif alt == "2":
                    try:
                        ist = motor.istatistik()
                        yaz(f"\n{Renk.BOLD}{Renk.SARI}DB İstatistikleri:{Renk.RESET}")
                        yaz(f"  Toplam kayıt : {ist['toplam']}")
                        yaz(f"  Geçerli      : {ist['gecerli']}")
                        for ag, sayi in ist.get("aglar", []):
                            yaz(f"  {ag:<20}: {sayi}")
                    except Exception as e:
                        yaz(f"{Renk.KIRMIZI}[!] Hata: {e}{Renk.RESET}")
                elif alt == "3":
                    try:
                        motor.baglanti.close()
                        yaz(f"{Renk.SARI}[i] Bağlantı kapatıldı.{Renk.RESET}")
                    except Exception:
                        pass
                    motor = None
        elif secim == "o":
            oz_test()
        elif secim == "h":
            hakkimda_goster()
        else:
            yaz(f"\n{Renk.KIRMIZI}[!] Geçersiz seçim: '{secim}'{Renk.RESET}")
        if secim != "0":
            try:
                input(f"\n{Renk.GRI}[Enter] devam etmek için...{Renk.RESET}")
            except (EOFError, KeyboardInterrupt):
                yaz()
                return


def hakkimda_goster():
    yaz()
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)
    yaz(f"{Renk.BOLD}{Renk.SARI}PAYMENT_GRAND v{SURUM} ULTIMATE{Renk.RESET}")
    yaz(f"{Renk.BOLD}Yapımcı:{Renk.RESET} {Renk.CYAN}@markos39{Renk.RESET}   Bina: {BINA_TARIHI}")
    yaz(f"{Renk.KIRMIZI}[!] Uyarı: Yalnızca test/sandbox kullanımı.{Renk.RESET}")
    yaz()
    yaz(f"{Renk.BOLD}Desteklenen veritabanları:{Renk.RESET}")
    for tur in DB_TURLERI:
        kurulu = "✓" if (tur == "sqlite" or tur in SURUCU) else "✗ (sürücü yok)"
        yaz(f"  {tur:<12} {kurulu}")
    yaz()
    yaz(f"{Renk.BOLD}Komut satırı:{Renk.RESET}")
    yaz(f"  python3 {PROGRAM_ADI}.py '4242 4242 4242 4242'")
    yaz(f"  python3 {PROGRAM_ADI}.py 4242424242424242 --db sqlite:///pg.db")
    yaz(f"  python3 {PROGRAM_ADI}.py 4242424242424242 --db postgresql://u:p@h/adb --risk")
    yaz(f"  python3 {PROGRAM_ADI}.py 4242424242424242 --bin --online --bin8 --json")
    yaz(f"  python3 {PROGRAM_ADI}.py kartlar.txt --html-rapor rapor.html --csv s.csv")
    yaz(f"  python3 {PROGRAM_ADI}.py --test --senaryo redd")
    yaz(f"  python3 {PROGRAM_ADI}.py --oztest")
    yaz(Renk.MAVI + "─" * 62 + Renk.RESET)


# ═══════════════════════════════════════════════════════════
# 13) ANA GİRİŞ
# ═══════════════════════════════════════════════════════════
def main():
    global SESSIZ, _log_seviyesi

    parser = argparse.ArgumentParser(
        prog=PROGRAM_ADI,
        description=f"Payment_grand v{SURUM} ULTIMATE — ödeme formu kart doğrulama test aracı.",
        epilog="Örnek: python3 payment_grand.py '4242 4242 4242 4242' --db sqlite:///pg.db")
    parser.add_argument("kart", nargs="?", help="Kart numarası VEYA toplu dosya yolu")
    parser.add_argument("--cvv", help="CVV/CVC (AMEX 4, diğerleri 3 hane)")
    parser.add_argument("--ay", help="Son kullanma ayı (1-12)")
    parser.add_argument("--yil", help="Son kullanma yılı (örn. 26 veya 2026)")
    parser.add_argument("-b", "--bin", action="store_true", help="BIN / veritabanı analizi")
    parser.add_argument("--bin8", action="store_true", help="8 haneli IIN sorgusu")
    parser.add_argument("--online", action="store_true", help="binlist.net sorgusu (önbellekli)")
    parser.add_argument("-t", "--test", action="store_true", help="Onaylı test kartlarını listele")
    parser.add_argument("--senaryo", choices=list(SENONYOLAR), help="Senaryo filtresi")
    parser.add_argument("--json", action="store_true", help="JSON çıktı")
    parser.add_argument("--tek", action="store_true", help="Tek satır özet")
    parser.add_argument("--risk", action="store_true", help="Risk analizini göster")
    parser.add_argument("--db", help="Veritabanı URL: sqlite:///f.db | postgresql://u:p@h/db | mysql://... | oracle://... | mssql://...")
    parser.add_argument("--db-gecmis", action="store_true", help="DB doğrulama geçmişini listele")
    parser.add_argument("--db-istatistik", action="store_true", help="DB istatistikleri göster")
    parser.add_argument("--db-test", metavar="URL", help="DB bağlantı testi")
    parser.add_argument("--cikti", help="Sonuçları dosyaya kaydet")
    parser.add_argument("--csv", help="Toplu modda CSV çıktısı")
    parser.add_argument("--jsonl", help="Toplu modda JSONL çıktısı")
    parser.add_argument("--html-rapor", help="Toplu modda HTML rapor")
    parser.add_argument("--oztest", action="store_true", help="Kendi kendini doğrulama testleri")
    parser.add_argument("--config", help="JSON config dosyası")
    parser.add_argument("--profil", choices=list(PROFILLER), help="Hazır profil (dev/prod/ci)")
    parser.add_argument("--log-seviye", choices=list(LOG_SEVIYE), help="Log seviyesi")
    parser.add_argument("--sessiz", action="store_true", help="Banner/süslemeleri kapat")
    parser.add_argument("--renksiz", action="store_true", help="Renkleri kapat")
    args = parser.parse_args()

    profil = PROFILLER.get(args.profil or "", {})
    config = {}
    if args.config and os.path.isfile(args.config):
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    if args.renksiz or config.get("renksiz") or (profil and not profil.get("renk", True)):
        Renk.kapat()
    if args.sessiz or config.get("sessiz"):
        SESSIZ = True
    _log_seviyesi = (args.log_seviye or config.get("log_seviye")
                     or (profil.get("log_seviye") if profil else None) or "INFO")

    onbellek_yukle()

    # ── DB test ──
    if args.db_test:
        motor, hata = db_baslat(args.db_test)
        if motor:
            yaz(f"{Renk.YESIL}[+] BAŞARILI: {args.db_test.split('://')[0]} | {motor.surum()}{Renk.RESET}")
            sys.exit(0)
        yaz(f"{Renk.KIRMIZI}[!] BAŞARISIZ: {hata}{Renk.RESET}")
        sys.exit(1)

    # ── DB motoru ──
    motor = None
    if args.db:
        motor, hata = db_baslat(args.db)
        if not motor:
            log_error("DB", f"Bağlanamadı: {hata}")
            yaz(f"{Renk.SARI}[i] DB olmadan devam ediliyor: {hata}{Renk.RESET}")

    # ── DB geçmiş / istatistik ──
    if args.db_gecmis or args.db_istatistik:
        if not motor:
            yaz(f"{Renk.KIRMIZI}[!] --db gerekli.{Renk.RESET}")
            sys.exit(2)
        if args.db_gecmis:
            for k in motor.gecmis(50):
                g = "✓" if k[5] else "✗"
                yaz(f"  {g} {str(k[0])[:19]}  {k[1]:<22} [{k[2]}] skor={float(k[4]):.0f}")
        else:
            ist = motor.istatistik()
            yaz(f"Toplam: {ist['toplam']} | Geçerli: {ist['gecerli']}")
            for ag, sayi in ist.get("aglar", []):
                yaz(f"  {ag:<20}: {sayi}")
        sys.exit(0)

    # ── oztest ──
    if args.oztest:
        sys.exit(oz_test())

    # ── test kartları ──
    if args.test:
        if not SESSIZ:
            yaz(BANNER)
        sys.exit(test_kartlari_goster(senaryo=args.senaryo, json_mod=args.json,
                                      cikti=args.cikti))

    # ── bin ──
    if args.bin or args.bin8:
        if not args.kart:
            yaz(f"{Renk.KIRMIZI}[!] --bin ile kart numarası gerekli.{Renk.RESET}")
            sys.exit(2)
        if not SESSIZ:
            yaz(BANNER)
        sonuc = bin_analiz(args.kart, online=args.online, bin8=args.bin8, db=motor)
        sys.exit(bin_rapor(args.kart, sonuc, cvv=args.cvv, ay=args.ay, yil=args.yil,
                           json_mod=args.json, cikti=args.cikti, risk=args.risk, db=motor))

    # ── menü ──
    if not args.kart:
        try:
            ana_menu()
        except KeyboardInterrupt:
            yaz(f"\n{Renk.SARI}Görüşmek üzere!{Renk.RESET}")
        sys.exit(0)

    # ── dosya mı kart mı? ──
    ham = sadece_rakam(args.kart)
    dosya_gibi = (os.path.isfile(args.kart)
                  or args.kart.lower().endswith((".txt", ".csv", ".list")))
    if dosya_gibi and len(ham) < 13:
        if not SESSIZ:
            yaz(BANNER)
        sys.exit(dosyadan_dogrula(args.kart, db=motor, cikti=args.cikti,
                                  json_mod=args.json, csv_cikti=args.csv,
                                  jsonl_cikti=args.jsonl, html_cikti=args.html_rapor))

    # ── tek kart ──
    if not SESSIZ:
        yaz(BANNER)
    sys.exit(tam_rapor(args.kart, cvv=args.cvv, ay=args.ay, yil=args.yil,
                       cikti=args.cikti, json_mod=args.json, tek=args.tek,
                       risk=args.risk, bin_sonuc=None, db=motor))


if __name__ == "__main__":
    main()
