#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NumberTools v4 - Türk Telefon Numarası İstihbarat Aracı
Yalnızca yetkili güvenlik testleri içindir.

Bağımlılıklar:
    pip3 install requests
"""

import os
import sys
import re
import json
import time
import random
import itertools
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("[!] 'requests' modülü gerekli. Kurulum: pip3 install requests")
    sys.exit(1)

# ============================================================
# RENK TANIMLARI
# ============================================================
class Colors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKCYAN  = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'

def c(color, text):
    return color + str(text) + Colors.ENDC

def banner():
    print(c(Colors.HEADER, """
    ╔══════════════════════════════════════════════╗
    ║         NUMBER TOOLS v4 - TÜRKİYE            ║
    ║   Telefon Numarası İstihbarat ve Analiz      ║
    ║      Yalnızca Yetkili Testler İçin           ║
    ╚══════════════════════════════════════════════╝
    """))

# ============================================================
# OPERATÖR / PREFIX VERİTABANI
# ============================================================
TURKISH_OPERATORS = {
    "Turkcell": ["530","531","532","533","534","535","536","537","538","539","561"],
    "Vodafone Turkey": ["540","541","542","543","544","545","546","547","548","549"],
    "Türk Telekom (Avea)": ["500","501","502","503","504","505","506","507","508","509",
                            "550","551","552","553","554","555","556","557","558","559"]
}
ALL_TR_PREFIXES = [p for plist in TURKISH_OPERATORS.values() for p in plist]

SPECIAL_PREFIXES = {
    "512": "Türk Telekom (Çağrı Hizmeti)",
    "516": "MVNO (TT Mobil)",
    "524": "MVNO (TT Mobil)",
    "592": "Globalstar (Uydu)",
    "510": "MVNO"
}

AREA_CODES = {
    "212": "İstanbul (Avrupa)", "216": "İstanbul (Anadolu)", "312": "Ankara",
    "232": "İzmir", "242": "Antalya", "256": "Aydın", "262": "Kocaeli",
    "264": "Sakarya", "272": "Afyonkarahisar", "274": "Kütahya",
    "282": "Tekirdağ", "284": "Edirne", "286": "Çanakkale", "288": "Kırklareli",
    "322": "Adana", "324": "Mersin", "326": "Hatay", "332": "Konya",
    "342": "Gaziantep", "344": "Kahramanmaraş", "346": "Sivas",
    "352": "Kayseri", "354": "Yozgat", "356": "Tokat", "358": "Amasya",
    "362": "Samsun", "364": "Çorum", "366": "Kastamonu", "368": "Sinop",
    "370": "Bartın", "372": "Zonguldak", "374": "Bolu", "376": "Çankırı",
    "378": "Karabük", "382": "Aksaray", "384": "Nevşehir", "386": "Kırşehir",
    "388": "Niğde", "412": "Diyarbakır", "414": "Şanlıurfa",
    "416": "Adıyaman", "422": "Elazığ", "424": "Bingöl", "426": "Tunceli",
    "428": "Hakkari", "432": "Van", "434": "Bitlis", "436": "Muş",
    "438": "Ağrı", "442": "Erzurum", "444": "Erzincan", "446": "Bayburt",
    "452": "Ordu", "454": "Giresun", "456": "Gümüşhane", "458": "Ardahan",
    "462": "Trabzon", "464": "Rize", "466": "Artvin", "472": "Iğdır",
    "474": "Kars", "476": "Ardahan", "478": "Kilis", "482": "Mardin",
    "484": "Siirt", "486": "Şırnak", "488": "Batman"
}

# ============================================================
# TEMEL NUMARA İŞLEMLERİ
# ============================================================
def clean_number(number: str) -> str:
    return re.sub(r'[^0-9+]', '', str(number))

def normalize_number(number: str):
    """Dönen: (e164, national, display)"""
    cleaned = clean_number(number)

    if cleaned.startswith('+90') and len(cleaned) == 12:
        n = cleaned[3:]
        return (cleaned, "0" + n, f"+90 {n[0:3]} {n[3:6]} {n[6:8]} {n[8:10]}")

    if cleaned.startswith('90') and len(cleaned) == 12:
        n = cleaned[2:]
        return ("+90" + n, "0" + n, f"+90 {n[0:3]} {n[3:6]} {n[6:8]} {n[8:10]}")

    if cleaned.startswith('0') and len(cleaned) == 11:
        n = cleaned[1:]
        return ("+90" + n, cleaned, f"+90 {n[0:3]} {n[3:6]} {n[6:8]} {n[8:10]}")

    if len(cleaned) == 10 and cleaned.startswith('5'):
        return ("+90" + cleaned, "0" + cleaned,
                f"+90 {cleaned[0:3]} {cleaned[3:6]} {cleaned[6:8]} {cleaned[8:10]}")

    return (cleaned, cleaned, cleaned)

def detect_operator(prefix: str):
    if prefix in SPECIAL_PREFIXES:
        return (SPECIAL_PREFIXES[prefix], "Özel")
    for operator, prefixes in TURKISH_OPERATORS.items():
        if prefix in prefixes:
            return (operator, "Mobil")
    if prefix in AREA_CODES:
        return (f"Sabit Hat - {AREA_CODES[prefix]}", "Sabit Hat")
    if prefix.startswith('8') or prefix.startswith('9'):
        return ("Özel Servis", "Servis")
    return ("Bilinmiyor / Geçersiz Prefix", "Bilinmiyor")

def validate_tr_number(number: str) -> dict:
    result = {
        "valid": False, "e164": "", "national": "", "display": "",
        "prefix": "", "operator": "", "line_type": "", "region": "",
        "length_valid": False, "prefix_valid": False, "errors": []
    }
    try:
        e164, national, display = normalize_number(number)
        result["e164"], result["national"], result["display"] = e164, national, display

        if e164.startswith('+90') and len(e164) == 13:
            result["length_valid"] = True
            prefix = e164[3:6]
            result["prefix"] = prefix

            all_prefixes = ALL_TR_PREFIXES + list(SPECIAL_PREFIXES.keys()) + list(AREA_CODES.keys())
            if prefix in all_prefixes:
                result["prefix_valid"] = True
                operator, line_type = detect_operator(prefix)
                result["operator"], result["line_type"] = operator, line_type
                if prefix in AREA_CODES:
                    result["region"] = AREA_CODES[prefix]
            else:
                result["errors"].append(f"Geçersiz prefix: {prefix}")
        elif e164.startswith('+90'):
            result["errors"].append(f"Geçersiz uzunluk (12 hane olmalı)")
        else:
            result["errors"].append("Türk numarası formatı değil (+90)")

        result["valid"] = result["length_valid"] and result["prefix_valid"]
    except Exception as e:
        result["errors"].append(str(e))
    return result

def safe_int(text, default):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default

def ask_save(content: str, prefix: str):
    save = input(c(Colors.OKCYAN, "\n[?] Dosyaya kaydet? (e/h): ")).lower()
    if save == 'e':
        filename = f"{prefix}_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))

# ============================================================
# MODÜL 1: NUMARA ANALİZİ
# ============================================================
def analyze_phone_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [1] NUMARA ANALİZ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    number = input(c(Colors.OKCYAN, "\n[?] Telefon numarası (+90 5XX XXX XXXX): "))
    result = validate_tr_number(number)

    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, "          NUMARA İSTİHBARAT RAPORU"))
    print(c(Colors.HEADER, "═" * 55))

    status = c(Colors.OKGREEN, "✓ GEÇERLİ") if result["valid"] else c(Colors.FAIL, "✗ GEÇERSİZ")
    print(f"\n  Durum:     {status}")
    if result["display"]:
        print(f"  Formatlı:  {c(Colors.BOLD, result['display'])}")
    if result["e164"]:
        print(f"  E.164:     {result['e164']}")
    if result["prefix"]:
        print(f"  Prefix:    0{result['prefix']}")
    if result["operator"]:
        print(f"  Operatör:  {c(Colors.OKGREEN, result['operator'])}")
    if result["line_type"]:
        print(f"  Hat Tipi:  {result['line_type']}")
    if result["region"]:
        print(f"  Bölge:     {result['region']}")

    if result["errors"]:
        print(f"\n  Hatalar:")
        for err in result["errors"]:
            print(f"    • {err}")

    print(c(Colors.HEADER, "═" * 55))

# ============================================================
# MODÜL 2: KISMİ NUMARA TAMAMLAMA
# ============================================================
def generate_numbers_from_partial(pattern: str, max_results: int = 100,
                                  use_operator_prefixes: bool = True) -> list:
    known = {}
    unknown = []
    digit_pos = 0
    for ch in pattern:
        if ch.isdigit():
            known[digit_pos] = int(ch)
            digit_pos += 1
        elif ch in ('*', 'x', 'X'):
            unknown.append(digit_pos)
            digit_pos += 1

    total_digits = digit_pos
    if total_digits > 10:
        print(c(Colors.FAIL, f"[!] Çok fazla hane: {total_digits} (maks 10)"))
        return []

    print(c(Colors.OKBLUE, f"\n[*] Bilinen haneler: {len(known)}, Bilinmeyen: {len(unknown)}"))

    # Prefix belirle
    if all(i in known for i in [0, 1, 2]):
        prefixes_to_try = [f"{known[0]}{known[1]}{known[2]}"]
    elif use_operator_prefixes:
        prefixes_to_try = [p for p in ALL_TR_PREFIXES
                           if all(i not in known or int(p[i]) == known[i] for i in range(3))]
    else:
        prefixes_to_try = [f"{i:03d}" for i in range(1000)
                           if all(i not in known or int(str(i).zfill(3)[j]) == known[j] for j in range(3))]

    if not prefixes_to_try:
        print(c(Colors.FAIL, "[!] Desenle eşleşen prefix yok!"))
        return []

    sub_unknown = [p for p in unknown if p >= 3]
    sub_known = {k: v for k, v in known.items() if k >= 3}
    results = set()
    per_prefix_limit = max(1, max_results // len(prefixes_to_try))

    for prefix in prefixes_to_try:
        if len(results) >= max_results:
            break
        if not sub_unknown:
            number = prefix + ''.join(str(sub_known.get(i, 0)) for i in range(3, 10))
            results.append(f"+90{number}")
        elif len(sub_unknown) <= 4 and (10 ** len(sub_unknown)) <= per_prefix_limit * 10:
            for digits in itertools.product(range(10), repeat=len(sub_unknown)):
                if len(results) >= max_results:
                    break
                number = prefix
                di = 0
                for i in range(3, 10):
                    if i in sub_known:
                        number += str(sub_known[i])
                    else:
                        number += str(digits[di])
                        di += 1
                results.append(f"+90{number}")
        else:
            # Rastgele örnekleme (uzay çok büyükse)
            for _ in range(per_prefix_limit):
                if len(results) >= max_results:
                    break
                number = prefix
                for i in range(3, 10):
                    if i in sub_known:
                        number += str(sub_known[i])
                    else:
                        number += str(random.randint(0, 9))
                if f"+90{number}" not in results:
                    results.append(f"+90{number}")

    results = sorted(set(results))[:max_results]
    return results

def partial_number_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [2] KISMİ NUMARA TAMAMLAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    print(c(Colors.OKBLUE, "\n  Örnek formatlar:"))
    print("    • +90 532 *** ** 04  (Turkcell, son 2 hane 04)")
    print("    • 05** *** ** 78     (ulusal format)")

    pattern = input(c(Colors.OKCYAN, "\n[?] Kısmi numara deseni: ")).strip()
    if not pattern:
        print(c(Colors.FAIL, "[!] Desen girilmedi!"))
        return

    max_results = safe_int(input(c(Colors.OKCYAN, "[?] Maksimum sonuç (varsayılan: 100): ")), 100)
    max_results = min(max_results, 10000)

    print(c(Colors.WARNING, "\n[*] Numara üretiliyor...\n"))
    start = time.time()
    numbers = generate_numbers_from_partial(pattern, max_results=max_results)
    elapsed = time.time() - start

    print(c(Colors.OKGREEN, f"\n[+] {len(numbers)} numara üretildi! Süre: {elapsed:.2f}s\n"))

    report_lines = [f"Desen: {pattern}", f"Üretilen: {len(numbers)} numara", "=" * 50, ""]
    for i, num in enumerate(numbers[:50], 1):
        r = validate_tr_number(num)
        line = f"  {i:<4} {r['display']:<22} {r['operator']}"
        print(line)
        report_lines.append(line)
    if len(numbers) > 50:
        print(f"\n  ... ve {len(numbers) - 50} numara daha")
        report_lines.append(f"... ve {len(numbers) - 50} numara daha")

    ask_save("\n".join(report_lines), "numbers")

# ============================================================
# MODÜL 3: WHATSAPP SORGULAMA
# ============================================================
def check_whatsapp(number: str) -> dict:
    result = {"number": number, "whatsapp": None, "error": None}
    try:
        e164 = normalize_number(number)[0]
        clean = e164.replace('+', '')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        }

        resp = requests.get(f"https://wa.me/{clean}", headers=headers,
                            timeout=15, allow_redirects=True)

        if resp.status_code == 200 and 'send?phone' in resp.url:
            result["whatsapp"] = True
        elif resp.status_code == 404:
            result["whatsapp"] = False
        elif resp.status_code == 200:
            result["whatsapp"] = False
        else:
            result["error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        result["error"] = str(e)
    return result

def whatsapp_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [3] WHATSAPP SORGULAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    print(c(Colors.WARNING, "\n[*] wa.me üzerinden kontrol (~%85 doğruluk)"))

    print(c(Colors.OKBLUE, "\n  1 - Tek numara"))
    print("  2 - Toplu (dosyadan)")
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))

    if choice == '1':
        number = input(c(Colors.OKCYAN, "\n[?] Numara: "))
        result = check_whatsapp(number)
        disp = validate_tr_number(number)["display"] or number

        print(c(Colors.HEADER, "\n" + "═" * 45))
        print(f"  Numara: {disp}")
        if result["whatsapp"] is True:
            print(f"  Durum:  {c(Colors.OKGREEN, '✓ WhatsApp KAYITLI')}")
        elif result["whatsapp"] is False:
            print(f"  Durum:  {c(Colors.WARNING, '✗ Kayıt bulunamadı')}")
        else:
            print(f"  Durum:  {c(Colors.FAIL, '? Sorgulanamadı: ' + str(result['error']))}")
        print(c(Colors.HEADER, "═" * 45))

    elif choice == '2':
        filename = input(c(Colors.OKCYAN, "\n[?] Dosya adı: "))
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                numbers = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(c(Colors.FAIL, f"[!] Dosya okunamadı: {e}"))
            return

        print(c(Colors.OKCYAN, f"\n[*] {len(numbers)} numara sorgulanıyor...\n"))
        results = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(check_whatsapp, n): n for n in numbers}
            for i, fut in enumerate(as_completed(futures), 1):
                data = fut.result()
                results.append(data)
                st = "VAR" if data["whatsapp"] else ("YOK" if data["whatsapp"] is False else "?")
                print(f"\r[{i}/{len(numbers)}] Son işlenen: {data['number']} -> {st}",
                      end='', flush=True)
        print()

        found = [r for r in results if r["whatsapp"] is True]
        print(c(Colors.HEADER, f"\n═ WhatsApp Var: {len(found)} / {len(results)} ═"))
        report = [f"Toplam: {len(results)}, WhatsApp Var: {len(found)}", "=" * 40, ""]
        for r in found:
            disp = validate_tr_number(r["number"])["display"] or r["number"]
            print(f"  ✓ {disp}")
            report.append(disp)

        ask_save("\n".join(report), "whatsapp_report")

# ============================================================
# MODÜL 4: TELEGRAM SORGULAMA
# ============================================================
def check_telegram(number: str) -> dict:
    result = {"number": number, "telegram": None, "username": None, "error": None}
    try:
        e164 = normalize_number(number)[0]
        clean = e164.replace('+', '')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        resp = requests.get(f"https://t.me/+{clean}", headers=headers,
                            timeout=10, allow_redirects=False)

        if resp.status_code in (301, 302, 303, 307):
            location = resp.headers.get('Location', '')
            if 'tg' in location or 'telegram' in location:
                result["telegram"] = True
        elif resp.status_code == 200:
            result["telegram"] = True
    except Exception as e:
        result["error"] = str(e)
    return result

def telegram_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [4] TELEGRAM SORGULAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    number = input(c(Colors.OKCYAN, "\n[?] Telefon numarası: "))
    result = check_telegram(number)

    disp = validate_tr_number(number)["display"] or number
    print(c(Colors.HEADER, "\n" + "═" * 45))
    print(f"  Numara: {disp}")
    if result["telegram"] is True:
        print(f"  Durum:  {c(Colors.OKGREEN, '✓ TELEGRAM KAYITLI (muhtemel)')}")
    elif result["telegram"] is False:
        print(f"  Durum:  {c(Colors.WARNING, '✗ Kayıt bulunamadı')}")
    else:
        print(f"  Durum:  {c(Colors.FAIL, '? Sorgulanamadı: ' + str(result['error']))}")
    print(c(Colors.WARNING, "  Not: t.me/numara her zaman kesin sonuç vermez."))
    print(c(Colors.HEADER, "═" * 45))

# ============================================================
# MODÜL 5: TOPLU İSTİHBARAT
# ============================================================
def bulk_intel_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [5] TOPLU NUMARA İSTİHBARAT MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    filename = input(c(Colors.OKCYAN, "\n[?] Numara listesi dosyası: "))
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            numbers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(c(Colors.FAIL, f"[!] Dosya hatası: {e}"))
        return

    if not numbers:
        print(c(Colors.FAIL, "[!] Liste boş!"))
        return

    print(c(Colors.OKBLUE, f"\n[*] {len(numbers)} numara işleniyor...\n"))

    stats = {"toplam": 0, "gecerli": 0, "mobil": 0, "sabit": 0}
    operator_stats = {}
    report = []

    for i, num in enumerate(numbers[:100], 1):
        r = validate_tr_number(num)
        stats["toplam"] += 1
        if r["valid"]:
            stats["gecerli"] += 1
            if r["line_type"] == "Mobil":
                stats["mobil"] += 1
            elif r["line_type"] == "Sabit Hat":
                stats["sabit"] += 1
            operator_stats[r["operator"]] = operator_stats.get(r["operator"], 0) + 1
            line = f"  {i:<4} {r['display']:<22} {r['operator']:<25} {r['line_type']}"
        else:
            line = f"  {i:<4} {num:<22} GEÇERSİZ"
        print(line)
        report.append(line)

    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(f"  Toplam: {stats['toplam']} | Geçerli: {stats['gecerli']} | "
          f"Mobil: {stats['mobil']} | Sabit: {stats['sabit']}")

    if operator_stats:
        print(f"\n  Operatör Dağılımı:")
        for op, count in sorted(operator_stats.items(), key=lambda x: -x[1]):
            pct = count / max(stats["gecerli"], 1) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"    {bar} {op:<25} {count:>4} (%{pct:.1f})")

    ask_save("\n".join(report), "intel_report")

# ============================================================
# MODÜL 6: NUMARA ÜRETEÇ
# ============================================================
def generate_random_tr_number(operator: str = None) -> str:
    prefixes = ALL_TR_PREFIXES
    if operator:
        op = operator.lower()
        if "turkcell" in op:
            prefixes = TURKISH_OPERATORS["Turkcell"]
        elif "vodafone" in op:
            prefixes = TURKISH_OPERATORS["Vodafone Turkey"]
        elif "telekom" in op or "tt" in op or "avea" in op:
            prefixes = TURKISH_OPERATORS["Türk Telekom (Avea)"]
    prefix = random.choice(prefixes)
    subscriber = ''.join(str(random.randint(0, 9)) for _ in range(7))
    return f"+90{prefix}{subscriber}"

def generator_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [6] NUMARA ÜRETEÇ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    print(c(Colors.OKBLUE, "\n  1 - Tüm operatörler"))
    print("  2 - Turkcell")
    print("  3 - Vodafone")
    print("  4 - Türk Telekom")
    op_choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-4): "))

    op_map = {"2": "Turkcell", "3": "Vodafone", "4": "Türk Telekom"}
    selected_op = op_map.get(op_choice)

    count = safe_int(input(c(Colors.OKCYAN, "[?] Kaç numara? ")), 10)
    count = min(count, 100000)

    start = time.time()
    numbers = [generate_random_tr_number(selected_op) for _ in range(count)]
    elapsed = time.time() - start

    print(c(Colors.OKGREEN, f"\n[+] {len(numbers)} numara üretildi! Süre: {elapsed:.3f}s\n"))

    report = [f"Operatör: {selected_op or 'Tümü'}", f"Adet: {len(numbers)}", ""]
    for i, num in enumerate(numbers[:20], 1):
        r = validate_tr_number(num)
        line = f"  {i:<3} {r['display']:<22} {r['operator']}"
        print(line)
        report.append(line)

    ask_save("\n".join(report) + "\n" + "\n".join(numbers), "generated_numbers")

# ============================================================
# MODÜL 7: NUMARA EŞLEŞTİRME
# ============================================================
def find_matching_numbers(target: str, database: list, similarity: float = 0.7):
    target_clean = clean_number(target)
    matches = []
    for num in database:
        db_clean = clean_number(num)
        if not target_clean or not db_clean:
            continue
        min_len = min(len(target_clean), len(db_clean))
        same = sum(1 for i in range(min_len) if target_clean[i] == db_clean[i])
        score = same / max(len(target_clean), len(db_clean))
        if score >= similarity:
            matches.append((num, score))
    matches.sort(key=lambda x: -x[1])
    return matches

def matching_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [7] NUMARA EŞLEŞTİRME MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    target = input(c(Colors.OKCYAN, "\n[?] Aranacak numara: "))
    threshold = float(input(c(Colors.OKCYAN, "[?] Benzerlik eşiği (0.0-1.0): ") or 0.7))

    filename = input(c(Colors.OKCYAN, "[?] Veritabanı dosyası: "))
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            database = list(set(line.strip() for line in f if line.strip()))
    except Exception as e:
        print(c(Colors.FAIL, f"[!] Hata: {e}"))
        return

    print(c(Colors.OKCYAN, f"\n[*] {len(database)} numarada aranıyor..."))
    matches = find_matching_numbers(target, database, threshold)

    print(c(Colors.OKGREEN, f"\n[+] {len(matches)} eşleşme bulundu!\n"))
    for i, (num, score) in enumerate(matches[:30], 1):
        r = validate_tr_number(num)
        disp = r['display'] or num
        print(f"  {i:<4} {disp:<22} %{score*100:.1f}  {r['operator']}")

    if not matches:
        print(c(Colors.WARNING, "\n[!] Eşleşme yok. Eşiği düşürmeyi deneyin."))

# ============================================================
# MODÜL 8: SOSYAL MEDYA OSINT
# ============================================================
def osint_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [8] SOSYAL MEDYA OSINT MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    number = input(c(Colors.OKCYAN, "\n[?] Telefon numarası: "))
    clean = normalize_number(number)[0].replace('+', '')

    platforms = {
        "WhatsApp": f"https://wa.me/{clean}",
        "Telegram": f"https://t.me/+{clean}",
        "Truecaller": f"https://www.truecaller.com/search/tr/{clean}",
    }

    print(c(Colors.OKCYAN, "\n[*] Platformlar kontrol ediliyor...\n"))
    print(c(Colors.HEADER, "═" * 55))
    found = 0
    for name, url in platforms.items():
        try:
            resp = requests.get(url, timeout=10, allow_redirects=True,
                                headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                print(f"  {c(Colors.OKGREEN, '✓')} {name:<12} {url}")
                found += 1
            else:
                print(f"  {c(Colors.WARNING, '✗')} {name:<12} (HTTP {resp.status_code})")
        except Exception as e:
            print(f"  {c(Colors.FAIL, '?')} {name:<12} ({e})")
    print(c(Colors.HEADER, f"═ Bulunan: {found}/{len(platforms)} ═"))

# ============================================================
# MODÜL 9: INSTAGRAM USERNAME ANALİZİ
# ============================================================
INSTAGRAM_APP_ID = "936619743392459"

def instagram_username_analyze(username: str) -> dict:
    result = {
        "username": username, "exists": False, "user_id": None,
        "full_name": None, "biography": None, "external_url": None,
        "follower_count": 0, "following_count": 0, "post_count": 0,
        "is_private": False, "is_verified": False, "is_business": False,
        "business_category": None, "contact_phone_number": None,
        "contact_email": None, "phones_extracted": [], "emails_extracted": [],
        "error": None
    }

    headers = {
        'X-IG-App-ID': INSTAGRAM_APP_ID,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
        'Accept': '*/*',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
    }

    try:
        resp = requests.get(
            f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers=headers, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            user = data.get('data', {}).get('user')
            if not user:
                result["error"] = "Kullanıcı bulunamadı"
                return result

            result["exists"] = True
            result["user_id"] = user.get('id')
            result["full_name"] = user.get('full_name')
            result["biography"] = user.get('biography', '')
            result["external_url"] = user.get('external_url')
            result["follower_count"] = user.get('edge_followed_by', {}).get('count', 0)
            result["following_count"] = user.get('edge_follow', {}).get('count', 0)
            result["post_count"] = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
            result["is_private"] = user.get('is_private', False)
            result["is_verified"] = user.get('is_verified', False)
            result["is_business"] = user.get('is_business_account', False)
            result["business_category"] = user.get('business_category_name')

            if user.get('business_phone_number'):
                result["contact_phone_number"] = user['business_phone_number']
            if user.get('business_email'):
                result["contact_email"] = user['business_email']
            if user.get('public_phone_number'):
                result["contact_phone_number"] = user['public_phone_number']
            if user.get('public_email'):
                result["contact_email"] = user['public_email']

            # Bio'dan telefon ve email çıkar
            bio = result["biography"] or ''
            patterns = [
                r'(?:\+90|0)5[0-9]{2}\s?\d{3}\s?\d{2}\s?\d{2}',
                r'(?:\+90|0)5[0-9]{2}[0-9]{7}',
            ]
            for pat in patterns:
                for p in re.findall(pat, bio):
                    clean_p = re.sub(r'[^0-9+]', '', p)
                    if clean_p not in result["phones_extracted"]:
                        result["phones_extracted"].append(clean_p)

            result["emails_extracted"] = re.findall(
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', bio)

        elif resp.status_code == 404:
            result["error"] = "Kullanıcı bulunamadı (404)"
        elif resp.status_code == 401 or resp.status_code == 403:
            result["error"] = "Instagram erişimi engelledi (IP kısıtlı olabilir)"
        elif resp.status_code == 429:
            result["error"] = "Rate limit aşıldı (429)"
        else:
            result["error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        result["error"] = str(e)

    return result

def print_insta_result(result, full=True):
    uname = result['username']
    if result["exists"]:
        print(f"\n  {c(Colors.OKGREEN, f'✓ @{uname} bulundu!')}")
        tags = []
        if result["is_verified"]:
            tags.append('✓ DOĞRULANMIŞ')
        tags.append('🔒 GİZLİ' if result["is_private"] else '🔓 AÇIK')
        if result["is_business"]:
            tags.append('🏢 İŞLETME')
        print(f"  {' | '.join(tags)}")
        print(f"  User ID:    {result['user_id']}")
        print(f"  İsim:       {result['full_name'] or '?'}")
        if result["biography"]:
            print(f"  Bio:        {result['biography'][:150]}")
        if result["external_url"]:
            print(f"  Web:        {result['external_url']}")
        print(f"  Takipçi:    {result['follower_count']:,}")
        print(f"  Takip:      {result['following_count']:,}")
        print(f"  Gönderi:    {result['post_count']:,}")

        if result["business_category"]:
            print(f"  Kategori:   {result['business_category']}")
        if result["contact_phone_number"]:
            print(f"  {c(Colors.OKGREEN, '✓ Telefon:')} {result['contact_phone_number']}")
        if result["contact_email"]:
            print(f"  {c(Colors.OKGREEN, '✓ Email:')}   {result['contact_email']}")
        if result["phones_extracted"]:
            print(f"  {c(Colors.OKGREEN, '✓ Bio telefon:')} {', '.join(result['phones_extracted'])}")
        if result["emails_extracted"]:
            print(f"  {c(Colors.OKGREEN, '✓ Bio email:')}   {', '.join(result['emails_extracted'])}")
        if not (result["contact_phone_number"] or result["phones_extracted"]
                or result["contact_email"] or result["emails_extracted"]):
            print(f"  {c(Colors.WARNING, '✗ İletişim bilgisi bulunamadı')}")
    else:
        print(f"\n  {c(Colors.FAIL, f'✗ @{uname} bulunamadı')}")
        if result.get("error"):
            print(f"  {c(Colors.WARNING, 'Sebep: ' + result['error'])}")

def instagram_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [9] INSTAGRAM USERNAME ANALİZ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    print(c(Colors.OKBLUE, "\n  1 - Profil analizi"))
    print("  2 - Toplu sorgulama (dosyadan)")
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))

    if choice == '1':
        username = input(c(Colors.OKCYAN, "\n[?] Instagram kullanıcı adı: ")).strip().lstrip('@')
        if not username:
            print(c(Colors.FAIL, "[!] Kullanıcı adı gerekli!"))
            return
        print(c(Colors.OKCYAN, f"\n[*] @{username} analiz ediliyor..."))
        result = instagram_username_analyze(username)
        print_insta_result(result)
        print(c(Colors.HEADER, "═" * 60))

    elif choice == '2':
        filename = input(c(Colors.OKCYAN, "\n[?] Username listesi dosyası: "))
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                usernames = [l.strip().lstrip('@') for l in f if l.strip()]
        except Exception as e:
            print(c(Colors.FAIL, f"[!] Hata: {e}"))
            return

        print(c(Colors.OKCYAN, f"\n[*] {len(usernames)} username sorgulanıyor...\n"))
        results = []
        for i, uname in enumerate(usernames, 1):
            print(f"\r[*] [{i}/{len(usernames)}] @{uname}", end='', flush=True)
            results.append(instagram_username_analyze(uname))
            time.sleep(1.5)  # Rate limit koruması
        print("\n")

        report = []
        for r in results:
            status = "✓" if r["exists"] else "✗"
            phone = r.get('contact_phone_number') or ','.join(r.get('phones_extracted', [])) or '-'
            email = r.get('contact_email') or ','.join(r.get('emails_extracted', [])) or '-'
            line = f"  {status} @{r['username']:<20} Tel: {phone:<20} Email: {email}"
            print(line)
            report.append(f"@{r['username']} | Tel: {phone} | Email: {email}")

        ask_save("\n".join(report), "instagram_report")

# ============================================================
# MODÜL 10: TAC / IMEI SORGULAMA
# ============================================================
TAC_DATABASE = {
    "35011703": ("Apple Inc.", "iPhone 16 Pro"),
    "35011601": ("Apple Inc.", "iPhone 15"),
    "35011505": ("Apple Inc.", "iPhone 14 Pro Max"),
    "35011404": ("Apple Inc.", "iPhone 13 Pro Max"),
    "35011203": ("Apple Inc.", "iPhone 11 Pro Max"),
    "35859103": ("Samsung", "Galaxy S24 Ultra"),
    "35859003": ("Samsung", "Galaxy S23 Ultra"),
    "35858903": ("Samsung", "Galaxy S22 Ultra"),
    "35853302": ("Samsung", "Galaxy Z Flip 6"),
    "35854002": ("Samsung", "Galaxy A55"),
    "86429001": ("Xiaomi", "Mi 14"),
    "86429101": ("Xiaomi", "Redmi Note 13"),
    "86262101": ("Huawei", "P60"),
    "86976801": ("Oppo", "Find X7"),
}

KNOWN_BRAND_TACS = {
    "3501": "Apple Inc.", "3502": "Apple Inc.", "3503": "Apple Inc.",
    "3504": "Apple Inc.", "3505": "Apple Inc.", "3506": "Apple Inc.",
    "3507": "Apple Inc.", "3508": "Apple Inc.", "3509": "Apple Inc.",
    "3510": "Apple Inc.", "3511": "Apple Inc.", "3512": "Apple Inc.",
    "3513": "Apple Inc.", "3514": "Apple Inc.", "3515": "Apple Inc.",
    "3516": "Apple Inc.", "3517": "Apple Inc.",
    "3532": "Samsung", "3533": "Samsung", "3534": "Samsung",
    "3545": "Nokia", "3546": "Nokia", "3547": "Nokia",
    "3555": "Motorola", "3556": "Motorola",
    "3558": "Sony", "3560": "LG", "3561": "LG",
    "3566": "HTC", "3569": "BlackBerry",
    "3572": "Google/Pixel", "3574": "OnePlus",
    "3577": "Huawei", "3578": "Huawei", "3579": "Huawei",
    "3580": "Xiaomi", "3581": "Xiaomi", "3582": "Xiaomi",
    "3585": "Samsung", "3586": "Samsung", "3590": "Samsung",
    "8642": "Xiaomi", "8626": "Huawei", "8697": "Oppo",
}

def lookup_device_by_tac(tac: str) -> dict:
    result = {"tac": tac, "brand": None, "model": None, "matched": False}
    if tac in TAC_DATABASE:
        result["brand"], result["model"] = TAC_DATABASE[tac]
        result["matched"] = True
        return result
    brand_prefix = tac[:4]
    if brand_prefix in KNOWN_BRAND_TACS:
        result["brand"] = KNOWN_BRAND_TACS[brand_prefix]
        result["matched"] = True
        result["model"] = f"(TAC prefix {brand_prefix} → {result['brand']} aralığı)"
    return result

def validate_imei(imei: str) -> bool:
    """Luhn algoritması ile IMEI kontrolü"""
    if len(imei) != 15 or not imei.isdigit():
        return False
    total = 0
    for i, d in enumerate(imei):
        d = int(d)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0

def phone_id_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [10] IMEI / TAC SORGULAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    print(c(Colors.OKBLUE, "\n  1 - IMEI sorgulama (Luhn + TAC)")
    print("  2 - TAC kodu sorgulama")
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))

    if choice == '1':
        imei = re.sub(r'[^0-9]', '', input(c(Colors.OKCYAN, "\n[?] IMEI (15 hane): ")))
        if len(imei) != 15:
            print(c(Colors.FAIL, f"[!] IMEI 15 hane olmalı ({len(imei)} girildi)"))
            return

        luhn_ok = validate_imei(imei)
        tac = imei[:8]
        device = lookup_device_by_tac(tac)

        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(f"  IMEI:        {imei}")
        print(f"  Luhn Check:  {c(Colors.OKGREEN, '✓ GEÇERLİ') if luhn_ok else c(Colors.FAIL, '✗ GEÇERSİZ (kontrol hanesi yanlış)')}")
        print(f"  TAC:         {tac}")
        if device["matched"]:
            print(f"  Marka:       {c(Colors.OKGREEN, device['brand'])}")
            print(f"  Model:       {device['model']}")
        else:
            print(f"  Marka:       {c(Colors.WARNING, 'Yerel TAC veritabanında yok')}")
        print(c(Colors.HEADER, "═" * 55))

    elif choice == '2':
        tac = re.sub(r'[^0-9]', '', input(c(Colors.OKCYAN, "\n[?] TAC kodu (8 hane): ")))
        if len(tac) != 8:
            print(c(Colors.FAIL, "[!] TAC 8 hane olmalı"))
            return
        device = lookup_device_by_tac(tac)
        print(c(Colors.HEADER, "\n" + "═" * 55))
        if device["matched"]:
            print(f"  ✓ Marka: {device['brand']}")
            print(f"  ✓ Model: {device['model']}")
        else:
            print(c(Colors.FAIL, "  ✗ Yerel veritabanında bulunamadı"))
            print(f"  GSMA resmi sorgu: https://imeidb.gsma.com/")
        print(c(Colors.HEADER, "═" * 55))

# ============================================================
# HIZLI TARAMA
# ============================================================
def quick_scan_menu():
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [H] HIZLI TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))

    number = input(c(Colors.OKCYAN, "\n[?] Telefon numarası: "))

    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, "          HIZLI TARAMA RAPORU"))
    print(c(Colors.HEADER, "═" * 55))

    r = validate_tr_number(number)
    print(c(Colors.OKBLUE, "\n[1] NUMARA ANALİZİ"))
    if r["valid"]:
        print(f"    {r['display']} | {r['operator']} | {r['line_type']}")
    else:
        print(f"    {c(Colors.FAIL, 'Geçersiz numara!')}")

    print(c(Colors.OKBLUE, "\n[2] WHATSAPP"))
    wa = check_whatsapp(number)
    if wa["whatsapp"] is True:
        print(f"    {c(Colors.OKGREEN, '✓ KAYITLI')}")
    elif wa["whatsapp"] is False:
        print(f"    {c(Colors.WARNING, '✗ Kayıt yok')}")
    else:
        print(f"    {c(Colors.FAIL, '? Sorgulanamadı')}")

    print(c(Colors.OKBLUE, "\n[3] TELEGRAM"))
    tg = check_telegram(number)
    if tg["telegram"] is True:
        print(f"    {c(Colors.OKGREEN, '✓ KAYITLI (muhtemel)')}")
    elif tg["telegram"] is False:
        print(f"    {c(Colors.WARNING, '✗ Kayıt yok')}")
    else:
        print(f"    {c(Colors.FAIL, '? Sorgulanamadı')}")

    print(c(Colors.HEADER, "\n═" * 28 + "═"))

# ============================================================
# ANA MENÜ
# ============================================================
def main_menu():
    banner()
    print(c(Colors.OKBLUE, "\n  Modüller:"))
    print(f"  {c(Colors.BOLD, '[1]')}   Numara Analizi")
    print(f"  {c(Colors.BOLD, '[2]')}   Kısmi Numara Tamamlama")
    print(f"  {c(Colors.BOLD, '[3]')}   WhatsApp Sorgulama")
    print(f"  {c(Colors.BOLD, '[4]')}   Telegram Sorgulama")
    print(f"  {c(Colors.BOLD, '[5]')}   Toplu İstihbarat")
    print(f"  {c(Colors.BOLD, '[6]')}   Numara Üreteç")
    print(f"  {c(Colors.BOLD, '[7]')}   Numara Eşleştirme")
    print(f"  {c(Colors.BOLD, '[8]')}   Sosyal Medya OSINT")
    print(f"  {c(Colors.OKGREEN, c(Colors.BOLD, '[9]'))}   Instagram Username Analizi")
    print(f"  {c(Colors.OKGREEN, c(Colors.BOLD, '[10]'))}  IMEI / TAC Sorgulama")
    print(f"  {c(Colors.BOLD, '[H]')}   Hızlı Tarama")
    print(f"  {c(Colors.BOLD, '[0]')}   Çıkış")

    choice = input(c(Colors.OKCYAN, "\n  [?] Seçiminiz: ")).strip().upper()

    if choice == '0':
        print(c(Colors.OKGREEN, "\n[+] Kapatıldı. Güvenli günler!"))
        return False

    menu_map = {
        '1': analyze_phone_menu, '2': partial_number_menu,
        '3': whatsapp_menu, '4': telegram_menu,
        '5': bulk_intel_menu, '6': generator_menu,
        '7': matching_menu, '8': osint_menu,
        '9': instagram_menu, '10': phone_id_menu,
        'H': quick_scan_menu,
    }

    if choice in menu_map:
        try:
            menu_map[choice]()
        except KeyboardInterrupt:
            print(c(Colors.WARNING, "\n\n[!] İptal edildi."))
        except Exception as e:
            print(c(Colors.FAIL, f"\n[!] Hata: {e}"))
    else:
        print(c(Colors.FAIL, f"[!] Geçersiz seçim: {choice}"))

    input(c(Colors.OKCYAN, "\n  [*] Devam etmek için Enter..."))
    return True

# ============================================================
# BAŞLANGIÇ
# ============================================================
if __name__ == "__main__":
    try:
        while main_menu():
            pass
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n\n[!] Ctrl+C ile çıkıldı."))
        sys.exit(0)
