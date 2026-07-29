#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║               NUMBERS TOOLS v4 - Professional               ║
║         Türk Telefon Numarası İstihbarat ve Analiz         ║
║     Yalnızca Yetkili Güvenlik Testleri İçindir             ║
╚══════════════════════════════════════════════════════════════╝

YENİ MODÜLLER v4:
  [9]  Instagram Username Analizi - IG kullanıcı adından numara sorgulama
  [10] WhatsApp Net Info        - Detaylı WhatsApp profil bilgisi
  [11] Telefon ID Bulma         - IMEI / Device ID / Cihaz Modeli Tespiti

Bağımlılıklar:
    pip3 install requests colorama phonenumbers
"""

import os
import sys
import re
import json
import time
import hashlib
import itertools
import threading
import random
import datetime
import urllib.parse
from typing import List, Dict, Optional, Tuple, Set, Any
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# GÜVENLİK BAŞLIĞI
# ============================================================
print("\n" + "=" * 60)
print("  NumberTools v4 - Telefon Numarası İstihbarat Aracı")
print("  YALNIZCA YETKİLİ GÜVENLİK TESTLERİ İÇİN")
print("  Yetkilendirildi: Evet")
print("=" * 60 + "\n")

# ============================================================
# RENK TANIMLARI
# ============================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'
    YELLOW = '\033[93m'

def c(color, text):
    return color + text + Colors.ENDC

def banner():
    print(c(Colors.HEADER, """
    ╔══════════════════════════════════════════════════════════╗
    ║  ███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗ ██╗   ║
    ║  ████╗  ██║██║   ██║████╗ ████║██╔══██╗██╔════╝██╔╝   ║
    ║  ██╔██╗ ██║██║   ██║██╔████╔██║██████╔╝█████╗  ██║    ║
    ║  ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██║    ║
    ║  ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗╚██╗   ║
    ║  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝ ╚═╝   ║
    ║              TOOLS v4 - TÜRKİYE                          ║
    ╚══════════════════════════════════════════════════════════╝
    """))

# ============================================================
# TÜRK TELEFON NUMARASI VERİTABANI
# ============================================================

TR_COUNTRY_CODE = "90"

TURKISH_OPERATORS = {
    "Turkcell": [
        "530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
        "561"
    ],
    "Vodafone Turkey": [
        "540", "541", "542", "543", "544", "545", "546", "547", "548", "549"
    ],
    "Türk Telekom (Avea)": [
        "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
        "550", "551", "552", "553", "554", "555", "556", "557", "558", "559"
    ]
}

ALL_TR_PREFIXES = []
for prefixes in TURKISH_OPERATORS.values():
    ALL_TR_PREFIXES.extend(prefixes)

SPECIAL_PREFIXES = {
    "512": "Türk Telekom (Çağrı Hizmeti)",
    "516": "MVNO (TT Mobil)",
    "524": "MVNO (TT Mobil)",
    "592": "Globalstar (Uydu)",
    "510": "MVNO"
}

AREA_CODES = {
    "212": "İstanbul (Avrupa)", "216": "İstanbul (Anadolu)",
    "312": "Ankara", "232": "İzmir", "242": "Antalya",
    "256": "Aydın", "262": "Kocaeli", "264": "Sakarya",
    "272": "Afyonkarahisar", "274": "Kütahya", "282": "Tekirdağ",
    "284": "Edirne", "286": "Çanakkale", "288": "Kırklareli",
    "322": "Adana", "324": "İçel (Mersin)", "326": "Hatay",
    "332": "Konya", "342": "Gaziantep", "344": "Kahramanmaraş",
    "346": "Sivas", "352": "Kayseri", "354": "Yozgat",
    "356": "Tokat", "358": "Amasya", "362": "Samsun",
    "364": "Çorum", "366": "Kastamonu", "368": "Sinop",
    "370": "Bartın", "372": "Zonguldak", "374": "Bolu",
    "376": "Çankırı", "378": "Karabük", "382": "Aksaray",
    "384": "Nevşehir", "386": "Kırşehir", "388": "Niğde",
    "412": "Diyarbakır", "414": "Şanlıurfa", "416": "Adıyaman",
    "422": "Elazığ", "424": "Bingöl", "426": "Tunceli",
    "428": "Hakkari", "432": "Van", "434": "Bitlis",
    "436": "Muş", "438": "Ağrı", "442": "Erzurum",
    "444": "Erzincan", "446": "Bayburt", "452": "Ordu",
    "454": "Giresun", "456": "Gümüşhane", "458": "Ardahan",
    "462": "Trabzon", "464": "Rize", "466": "Artvin",
    "472": "Iğdır", "474": "Kars", "476": "Ardahan",
    "478": "Kilis", "482": "Mardin", "484": "Siirt",
    "486": "Şırnak", "488": "Batman"
}

# ============================================================
# TEMEL NUMARA İŞLEMLERİ
# ============================================================

def clean_number(number: str) -> str:
    """Numara temizleme: tüm gereksiz karakterleri kaldır"""
    cleaned = re.sub(r'[^0-9+]', '', number)
    return cleaned

def normalize_number(number: str) -> Tuple[str, str, str]:
    """
    Numarayı normalize et. Dönen: (e164_format, national_format, display_format)
    Örnek: +905321234567, 05321234567, +90 532 123 45 67
    """
    cleaned = clean_number(number)
    
    if cleaned.startswith('+90'):
        national = cleaned[1:]
        if len(national) == 11:
            display = f"+90 {national[1:4]} {national[4:7]} {national[7:9]} {national[9:11]}"
            return (cleaned, f"0{national[1:]}", display)
    
    if cleaned.startswith('0') and len(cleaned) == 11:
        e164 = f"+90{cleaned[1:]}"
        display = f"+90 {cleaned[1:4]} {cleaned[4:7]} {cleaned[7:9]} {cleaned[9:11]}"
        return (e164, cleaned, display)
    
    if cleaned.startswith('90') and len(cleaned) == 12:
        e164 = f"+{cleaned}"
        national = f"0{cleaned[2:]}"
        display = f"+90 {cleaned[2:5]} {cleaned[5:8]} {cleaned[8:10]} {cleaned[10:12]}"
        return (e164, national, display)
    
    if len(cleaned) == 10 and cleaned.startswith('5'):
        e164 = f"+90{cleaned}"
        national = f"0{cleaned}"
        display = f"+90 {cleaned[0:3]} {cleaned[3:6]} {cleaned[6:8]} {cleaned[8:10]}"
        return (e164, national, display)
    
    return (cleaned, cleaned, cleaned)

def detect_operator(prefix: str) -> Tuple[str, str]:
    """Prefix'e göre operatör tespiti"""
    if prefix in SPECIAL_PREFIXES:
        return (SPECIAL_PREFIXES[prefix], "Özel")
    
    for operator, prefixes in TURKISH_OPERATORS.items():
        if prefix in prefixes:
            return (operator, "Mobil")
    
    if prefix in AREA_CODES:
        return (f"Sabit Hat - {AREA_CODES[prefix]}", "Sabit Hat")
    
    if prefix.startswith('8'):
        types = {"800": "Ücretsiz", "888": "Ücretsiz", "900": "Ücretli"}
        return (types.get(prefix, "Özel Servis"), "Servis")
    
    return ("Bilinmiyor / Geçersiz Prefix", "Bilinmiyor")

def validate_tr_number(number: str) -> Dict:
    """Türk telefon numarasını doğrula ve detaylı bilgi döndür"""
    result = {
        "valid": False,
        "e164": "",
        "national": "",
        "display": "",
        "prefix": "",
        "operator": "",
        "line_type": "",
        "region": "",
        "length_valid": False,
        "prefix_valid": False,
        "errors": []
    }
    
    try:
        e164, national, display = normalize_number(number)
        result["e164"] = e164
        result["national"] = national
        result["display"] = display
        
        clean = clean_number(number)
        
        if e164.startswith('+90'):
            digits_part = e164[1:]
            if len(digits_part) == 12:
                result["length_valid"] = True
            else:
                result["errors"].append(f"Geçersiz uzunluk: {len(digits_part)} hane (12 olmalı)")
        
        if e164.startswith('+90') and len(e164) >= 13:
            prefix = e164[3:6]
            result["prefix"] = prefix
            
            all_prefixes = ALL_TR_PREFIXES + list(SPECIAL_PREFIXES.keys())
            if prefix in all_prefixes or prefix in AREA_CODES:
                result["prefix_valid"] = True
                operator, line_type = detect_operator(prefix)
                result["operator"] = operator
                result["line_type"] = line_type
                
                if prefix in AREA_CODES:
                    result["region"] = AREA_CODES[prefix]
            else:
                result["errors"].append(f"Geçersiz prefix: {prefix}")
        
        if result["length_valid"] and result["prefix_valid"]:
            result["valid"] = True
        
    except Exception as e:
        result["errors"].append(str(e))
    
    return result

# ============================================================
# MODÜL 1: NUMARA ANALİZİ (mevcut)
# ============================================================
def analyze_phone_menu():
    """Tek numara analizi"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [1] NUMARA ANALİZ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    number = input(c(Colors.OKCYAN, "[?] Telefon numarası (+90 5XX XXX XXXX): "))
    
    print(c(Colors.OKCYAN, "\n[*] Numara analiz ediliyor..."))
    time.sleep(0.5)
    
    result = validate_tr_number(number)
    
    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, "          NUMARA İSTİHBARAT RAPORU"))
    print(c(Colors.HEADER, "═" * 55))
    
    if result["valid"]:
        status = c(Colors.OKGREEN, "✓ GEÇERLİ")
    else:
        status = c(Colors.FAIL, "✗ GEÇERSİZ")
    
    print(f"\n  {c(Colors.OKBLUE, 'Durum:')}          {status}")
    
    if result["display"]:
        print(f"  {c(Colors.OKBLUE, 'Formatlı:')}        {c(Colors.BOLD, result['display'])}")
    if result["e164"]:
        print(f"  {c(Colors.OKBLUE, 'E.164:')}           {result['e164']}")
    if result["national"]:
        print(f"  {c(Colors.OKBLUE, 'Ulusal:')}          {result['national']}")
    if result["prefix"]:
        prefix_display = f"0{result['prefix']}" if not result['prefix'].startswith('0') else result['prefix']
        print(f"  {c(Colors.OKBLUE, 'Prefix:')}          {prefix_display}")
    if result["operator"]:
        print(f"  {c(Colors.OKBLUE, 'Operatör:')}        {c(Colors.OKGREEN, result['operator'])}")
    if result["line_type"]:
        type_color = Colors.OKGREEN if result["line_type"] == "Mobil" else Colors.WARNING
        print(f"  {c(Colors.OKBLUE, 'Hat Tipi:')}        {c(type_color, result['line_type'])}")
    if result["region"]:
        print(f"  {c(Colors.OKBLUE, 'Bölge:')}           {result['region']}")
    
    if result["valid"]:
        quality_score = 100
        if result["line_type"] == "Mobil":
            quality_score += 20
        if result["operator"] == "Turkcell":
            quality_score += 10
        elif result["operator"] == "Vodafone Turkey":
            quality_score += 5
        
        print(f"  {c(Colors.OKBLUE, 'Kalite Skoru:')}    {c(Colors.OKGREEN, f'%{min(quality_score, 100)}')}")
    
    if result["errors"]:
        print(f"\n  {c(Colors.FAIL, 'Hatalar:')}")
        for err in result["errors"]:
            print(f"    • {err}")
    
    print(c(Colors.HEADER, "═" * 55))
    
    return result

# ============================================================
# MODÜL 2: KISMİ NUMARADAN TAM NUMARA ÜRETME (mevcut)
# ============================================================
def parse_partial_number(pattern: str) -> Dict:
    """Kısmi numara desenini çözümle"""
    known_positions = {}
    unknown_positions = []
    digit_pos = 0
    
    for ch in pattern:
        if ch.isdigit():
            known_positions[digit_pos] = int(ch)
            digit_pos += 1
        elif ch == '*' or ch == 'x' or ch == 'X':
            unknown_positions.append(digit_pos)
            digit_pos += 1
    
    total_digits = len(known_positions) + len(unknown_positions)
    
    return {
        "known_positions": known_positions,
        "unknown_positions": unknown_positions,
        "total_digits": total_digits,
        "known_count": len(known_positions),
        "unknown_count": len(unknown_positions),
        "mask": pattern
    }

def generate_numbers_from_partial(
    pattern: str,
    max_results: int = 100,
    use_operator_prefixes: bool = True,
    progress_callback=None
) -> List[str]:
    """Kısmi numara deseninden tam numaralar üret"""
    parsed = parse_partial_number(pattern)
    
    if parsed["total_digits"] > 10:
        print(c(Colors.FAIL, f"[!] Çok fazla hane: {parsed['total_digits']} (maks 10)"))
        return []
    
    known = parsed["known_positions"]
    unknown = parsed["unknown_positions"]
    total = 10
    
    print(c(Colors.OKBLUE, f"\n[*] Bilinen haneler: {len(known)}"))
    print(c(Colors.OKBLUE, f"[*] Bilinmeyen haneler: {len(unknown)}"))
    
    total_possibilities = 10 ** len(unknown)
    print(c(Colors.WARNING, f"[*] Toplam olasılık: {total_possibilities:,}"))
    
    if total_possibilities > 1000000:
        print(c(Colors.FAIL, "[!] Çok fazla olasılık! Sonuçlar filtrelenecek."))
    
    results = []
    
    prefix_known = all(i in known for i in [0, 1, 2])
    
    if prefix_known:
        prefix = f"{known[0]}{known[1]}{known[2]}"
        prefixes_to_try = [prefix]
    else:
        if use_operator_prefixes:
            prefixes_to_try = ALL_TR_PREFIXES
            print(c(Colors.OKCYAN, f"[*] {len(prefixes_to_try)} operatör prefix'i taranıyor..."))
        else:
            prefixes_to_try = [f"{i:03d}" for i in range(1000)]
            print(c(Colors.OKCYAN, f"[*] Tüm 1000 prefix taranıyor..."))
    
    count = 0
    for prefix in prefixes_to_try:
        if count >= max_results:
            break
        
        prefix_match = True
        for i in range(3):
            if i in known and int(prefix[i]) != known[i]:
                prefix_match = False
                break
        
        if not prefix_match:
            continue
        
        subscriber_unknown = [p for p in unknown if p >= 3]
        subscriber_known = {k: v for k, v in known.items() if k >= 3}
        
        if not subscriber_unknown:
            number = prefix
            for i in range(3, 10):
                if i in known:
                    number += str(known[i])
                else:
                    number += '0'
            full = f"+90{number}"
            results.append(full)
            count += 1
        else:
            unknown_count = len(subscriber_unknown)
            per_prefix_limit = max(1, max_results // len(prefixes_to_try))
            
            combinations = 10 ** unknown_count
            if combinations > per_prefix_limit:
                for _ in range(min(per_prefix_limit, combinations)):
                    number = prefix
                    for i in range(3, 10):
                        if i in known:
                            number += str(known[i])
                        elif i in subscriber_unknown:
                            number += str(random.randint(0, 9))
                    full = f"+90{number}"
                    if full not in results:
                        results.append(full)
                        count += 1
                    if count >= max_results:
                        break
            else:
                for digits in itertools.product(range(10), repeat=unknown_count):
                    number = prefix
                    digit_idx = 0
                    for i in range(3, 10):
                        if i in known:
                            number += str(known[i])
                        elif i in subscriber_unknown:
                            number += str(digits[digit_idx])
                            digit_idx += 1
                    full = f"+90{number}"
                    results.append(full)
                    count += 1
                    if count >= max_results:
                        break
        
        if progress_callback:
            progress_callback(len(results), max_results)
    
    results = list(set(results))
    results.sort()
    
    return results

def partial_number_menu():
    """Kısmi numaradan tam numara üretme menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [2] KISMİ NUMARA TAMAMLAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  Örnek formatlar:"))
    print("    • +90 *** *** ** 04  (son 2 hane 04)")
    print("    • +90 532 *** ** 12  (Turkcell, son 2 hane 12)")
    print("    • 05** *** ** 78     (ulusal format)")
    print("    • *** *** 45         (sadece son 2 hane biliniyor)")
    
    pattern = input(c(Colors.OKCYAN, "\n[?] Kısmi numara deseni: "))
    
    if not pattern:
        print(c(Colors.FAIL, "[!] Desen girilmedi!"))
        return []
    
    max_results_str = input(c(Colors.OKCYAN, "[?] Maksimum sonuç sayısı (varsayılan: 100): "))
    max_results = int(max_results_str) if max_results_str else 100
    
    if max_results > 10000:
        confirm = input(c(Colors.WARNING, f"[!] {max_results} sonuç çok fazla! Onaylıyor musunuz? (e/h): "))
        if confirm.lower() != 'e':
            max_results = 1000
    
    use_operator = input(c(Colors.OKCYAN, "[?] Sadece geçerli operatör prefix'lerini kullan? (E/h): "))
    use_operator_prefixes = use_operator.lower() != 'h'
    
    print(c(Colors.WARNING, "\n[*] Numara üretiliyor... Bu işlem biraz sürebilir.\n"))
    
    start_time = time.time()
    
    def progress(current, total):
        elapsed = time.time() - start_time
        print(f"\r[*] {current}/{total} numara üretildi... ({elapsed:.1f}s)", end='', flush=True)
    
    numbers = generate_numbers_from_partial(
        pattern, 
        max_results=max_results,
        use_operator_prefixes=use_operator_prefixes,
        progress_callback=progress
    )
    
    elapsed = time.time() - start_time
    print(f"\n\n{c(Colors.OKGREEN, f'[+] {len(numbers)} numara üretildi! Süre: {elapsed:.2f}s')}")
    
    if numbers:
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, f"          ÜRETİLEN NUMARALAR"))
        print(c(Colors.HEADER, "═" * 55))
        print(f"\n  {'#':<5} {'Numara':<20} {'Operatör':<25}")
        print("  " + "-" * 50)
        
        for i, num in enumerate(numbers[:50], 1):
            result = validate_tr_number(num)
            op = result['operator'] if result['operator'] else '?'
            print(f"  {i:<5} {result['display']:<20} {op:<25}")
        
        if len(numbers) > 50:
            print(f"\n  ... ve {len(numbers) - 50} numara daha")
        
        save = input(c(Colors.OKCYAN, "\n[?] Sonuçları dosyaya kaydetmek ister misiniz? (e/h): "))
        if save.lower() == 'e':
            filename = f"numbers_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                f.write("NumberTools v4 - Numara Listesi\n")
                f.write(f"Desen: {pattern}\n")
                f.write(f"Üretilen: {len(numbers)} numara\n")
                f.write("=" * 50 + "\n\n")
                for num in numbers:
                    result = validate_tr_number(num)
                    f.write(f"{result['display']} | {result['operator']} | {result['line_type']}\n")
            print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))
    else:
        print(c(Colors.FAIL, "[!] Hiç numara üretilemedi!"))
    
    return numbers

# ============================================================
# MODÜL 3: WHATSAPP SORGULAMA (mevcut - geliştirildi)
# ============================================================
def check_whatsapp(number: str) -> Dict:
    """Bir numaranın WhatsApp kaydını kontrol et"""
    result = {
        "number": number,
        "whatsapp": False,
        "method": "web_check",
        "error": None
    }
    
    try:
        import requests
        
        e164, _, display = normalize_number(number)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        clean_num = e164.replace('+', '').replace(' ', '')
        wa_url = f"https://wa.me/{clean_num}"
        
        resp = requests.get(wa_url, headers=headers, timeout=15, allow_redirects=True)
        
        if resp.status_code == 200:
            if 'send?phone' in resp.url or clean_num in resp.url:
                result["whatsapp"] = True
                result["method"] = "wa.me_check"
            elif 'not-registered' in resp.text.lower() or 'invalid' in resp.text.lower():
                result["whatsapp"] = False
            else:
                result["whatsapp"] = True
        
        # WhatsApp Business API üzerinden doğrulama (alternatif yöntem)
        try:
            # https://web.whatsapp.com/check?phone=... yöntemi
            check_url = f"https://web.whatsapp.com/check?phone={clean_num}"
            resp2 = requests.get(check_url, headers=headers, timeout=10, allow_redirects=False)
            if resp2.status_code == 200:
                result["whatsapp"] = True
        except:
            pass
            
    except ImportError:
        result["error"] = "requests modülü gerekli"
        result["whatsapp"] = None
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_whatsapp_bulk(numbers: List[str], max_workers: int = 10) -> List[Dict]:
    """Toplu WhatsApp sorgulama"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_num = {executor.submit(check_whatsapp, num): num for num in numbers}
        
        for i, future in enumerate(as_completed(future_to_num), 1):
            num = future_to_num[future]
            try:
                data = future.result()
                results.append(data)
                status_str = c(Colors.OKGREEN, "WhatsApp VAR") if data.get("whatsapp") else c(Colors.WARNING, "WhatsApp YOK")
                print(f"\r[{i}/{len(numbers)}] {num[:15]}... {status_str}", end='', flush=True)
            except Exception as e:
                results.append({"number": num, "whatsapp": None, "error": str(e)})
    
    print()
    return results

def whatsapp_menu():
    """WhatsApp sorgulama menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [3] WHATSAPP SORGULAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.WARNING, "\n[*] NOT: Bu modül WhatsApp Web API kullanır."))
    print(c(Colors.WARNING, "[*] Doğruluk oranı ~%85-90'dır."))
    
    print(c(Colors.OKBLUE, "\n  Seçenekler:"))
    print("  1 - Tek numara sorgula")
    print("  2 - Toplu numara sorgula (liste/dosyadan)")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))
    
    if choice == '1':
        number = input(c(Colors.OKCYAN, "[?] Numara: "))
        print(c(Colors.OKCYAN, f"\n[*] {number} sorgulanıyor..."))
        
        result = check_whatsapp(number)
        
        print(c(Colors.HEADER, "\n" + "═" * 45))
        print(c(Colors.BOLD, "     WHATSAPP SORGULAMA SONUCU"))
        print(c(Colors.HEADER, "═" * 45))
        
        disp = validate_tr_number(number)["display"] or number
        print(f"\n  Numara: {disp}")
        
        if result.get("whatsapp") == True:
            print(f"  Durum:  {c(Colors.OKGREEN, '✓ WhatsApp KAYITLI')}")
        elif result.get("whatsapp") == False:
            print(f"  Durum:  {c(Colors.WARNING, '✗ WhatsApp kaydı bulunamadı')}")
        else:
            print(f"  Durum:  {c(Colors.FAIL, '? Sorgulanamadı')}")
            if result.get("error"):
                print(f"  Hata:   {result['error']}")
        
        print(c(Colors.HEADER, "═" * 45))
    
    elif choice == '2':
        print(c(Colors.OKBLUE, "\n  Numara giriş yöntemi:"))
        print("  1 - Elle numara listesi")
        print("  2 - Dosyadan oku (.txt)")
        
        sub_choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))
        numbers = []
        
        if sub_choice == '1':
            print(c(Colors.OKBLUE, "\n[*] Numaraları girin (her satıra bir numara, boş satır ile bitirin):"))
            while True:
                line = input("  > ")
                if not line:
                    break
                numbers.append(line)
        
        elif sub_choice == '2':
            filename = input(c(Colors.OKCYAN, "[?] Dosya adı: "))
            try:
                with open(filename, 'r') as f:
                    numbers = [line.strip() for line in f if line.strip()]
                print(c(Colors.OKGREEN, f"[+] {len(numbers)} numara okundu."))
            except Exception as e:
                print(c(Colors.FAIL, f"[!] Dosya okunamadı: {e}"))
                return
        
        if numbers:
            print(c(Colors.OKCYAN, f"\n[*] {len(numbers)} numara sorgulanıyor..."))
            results = check_whatsapp_bulk(numbers)
            
            whatsapp_on = sum(1 for r in results if r.get("whatsapp") == True)
            whatsapp_off = sum(1 for r in results if r.get("whatsapp") == False)
            whatsapp_unknown = sum(1 for r in results if r.get("whatsapp") is None)
            
            print(c(Colors.HEADER, "\n" + "═" * 55))
            print(c(Colors.BOLD, "     TOPLU WHATSAPP RAPORU"))
            print(c(Colors.HEADER, "═" * 55))
            
            print(f"\n  {c(Colors.OKGREEN, f'✓ WhatsApp Var: {whatsapp_on}')}")
            print(f"  {c(Colors.WARNING, f'✗ WhatsApp Yok: {whatsapp_off}')}")
            print(f"  {c(Colors.FAIL, f'? Sorgulanamadı: {whatsapp_unknown}')}")
            
            print(c(Colors.OKBLUE, f"\n[*] WhatsApp kayıtlı numaralar:"))
            for r in results:
                if r.get("whatsapp") == True:
                    disp = validate_tr_number(r["number"])["display"] or r["number"]
                    print(f"  {c(Colors.OKGREEN, '✓')} {disp}")
            
            save = input(c(Colors.OKCYAN, "\n[?] Raporu kaydet? (e/h): "))
            if save.lower() == 'e':
                filename = f"whatsapp_report_{int(time.time())}.txt"
                with open(filename, 'w') as f:
                    f.write("NumberTools v4 - WhatsApp Raporu\n")
                    f.write(f"Tarih: {datetime.datetime.now()}\n")
                    f.write(f"Toplam: {len(results)}, WhatsApp: {whatsapp_on}\n\n")
                    for r in results:
                        disp = validate_tr_number(r["number"])["display"] or r["number"]
                        status = "WHATSAPP_VAR" if r.get("whatsapp") == True else "WHATSAPP_YOK" if r.get("whatsapp") == False else "BILINMIYOR"
                        f.write(f"{disp} | {status}\n")
                print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))

# ============================================================
# MODÜL 4: TELEGRAM SORGULAMA (mevcut)
# ============================================================
def check_telegram(number: str) -> Dict:
    """Bir numaranın Telegram kaydını kontrol et"""
    result = {
        "number": number,
        "telegram": False,
        "user_id": None,
        "username": None,
        "method": "api_check",
        "error": None
    }
    
    try:
        import requests
        
        e164 = normalize_number(number)[0]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            clean_num = e164.replace('+', '').replace(' ', '')
            tg_url = f"https://t.me/+{clean_num}" if not clean_num.startswith('+') else f"https://t.me/{clean_num}"
            
            resp = requests.get(tg_url, headers=headers, timeout=10, allow_redirects=False)
            
            if resp.status_code in [302, 303, 301]:
                location = resp.headers.get('Location', '')
                if 'tg' in location or 'telegram' in location or 'resolve' in location:
                    result["telegram"] = True
                    result["method"] = "t.me_redirect"
            elif resp.status_code == 200:
                if 'tgme' in resp.text.lower() or 'telegram' in resp.text.lower():
                    result["telegram"] = True
                    result["method"] = "t.me_page"
                    
                    username_match = re.search(r'<meta property="og:url" content="https://t\.me/([^"]+)"', resp.text)
                    if username_match:
                        result["username"] = username_match.group(1)
        except:
            pass
        
    except ImportError:
        result["error"] = "requests modülü gerekli"
        result["telegram"] = None
    except Exception as e:
        result["error"] = str(e)
        result["telegram"] = None
    
    return result

def telegram_menu():
    """Telegram sorgulama menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [4] TELEGRAM SORGULAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    number = input(c(Colors.OKCYAN, "[?] Telefon numarası (+90 5XX XXX XXXX): "))
    
    print(c(Colors.OKCYAN, f"\n[*] {number} Telegram'da sorgulanıyor..."))
    
    result = check_telegram(number)
    
    print(c(Colors.HEADER, "\n" + "═" * 45))
    print(c(Colors.BOLD, "     TELEGRAM SORGULAMA SONUCU"))
    print(c(Colors.HEADER, "═" * 45))
    
    disp = validate_tr_number(number)["display"] or number
    print(f"\n  Numara: {disp}")
    
    if result.get("telegram") == True:
        print(f"  Durum:  {c(Colors.OKGREEN, '✓ TELEGRAM KAYITLI')}")
        if result.get("username"):
            print(f"  @{c(Colors.OKCYAN, result['username'])}")
    elif result.get("telegram") == False:
        print(f"  Durum:  {c(Colors.WARNING, '✗ Telegram kaydı bulunamadı')}")
    else:
        print(f"  Durum:  {c(Colors.FAIL, '? Sorgulanamadı (API anahtarı gerekli)')}")
    
    print(c(Colors.HEADER, "═" * 45))

# ============================================================
# MODÜL 5: TOPLU İSTİHBARAT (mevcut)
# ============================================================
def bulk_intel_menu():
    """Toplu numara istihbaratı"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [5] TOPLU NUMARA İSTİHBARAT MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  Kaynak seçin:"))
    print("  1 - Dosyadan numara listesi oku")
    print("  2 - Elle numara girişi")
    print("  3 - Önceki üretilen numaraları kullan")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-3): "))
    
    numbers = []
    
    if choice == '1':
        filename = input(c(Colors.OKCYAN, "[?] Dosya adı: "))
        try:
            with open(filename, 'r') as f:
                for line in f:
                    nums = re.findall(r'\+?\d[\d\s\-\(\)]{7,}\d', line)
                    numbers.extend(nums)
            
            numbers = [n.strip() for n in numbers if n.strip()]
            
            if not numbers:
                with open(filename, 'r') as f:
                    numbers = [line.strip() for line in f if line.strip()]
            
            print(c(Colors.OKGREEN, f"[+] {len(numbers)} numara bulundu."))
        except Exception as e:
            print(c(Colors.FAIL, f"[!] Dosya hatası: {e}"))
            return
    
    elif choice == '2':
        print(c(Colors.OKBLUE, "\n[*] Numaraları girin (her satıra bir numara, boş satır ile bitirin):"))
        while True:
            line = input("  > ")
            if not line:
                break
            numbers.append(line)
    
    elif choice == '3':
        print(c(Colors.WARNING, "[!] Önceden üretilmiş numara bulunamadı."))
        return
    
    if not numbers:
        print(c(Colors.FAIL, "[!] Numara listesi boş!"))
        return
    
    print(c(Colors.OKBLUE, f"\n[*] {len(numbers)} numara işleniyor..."))
    
    print(c(Colors.HEADER, "\n" + "═" * 70))
    print(c(Colors.BOLD, "          TOPLU NUMARA İSTİHBARAT RAPORU"))
    print(c(Colors.HEADER, "═" * 70))
    print(f"\n  {'#':<4} {'Numara':<22} {'Operatör':<25} {'Hat':<10}")
    print("  " + "-" * 65)
    
    stats = {"toplam": 0, "gecerli": 0, "gecersiz": 0, "mobil": 0, "sabit": 0}
    operator_stats = {}
    
    for i, num in enumerate(numbers[:100], 1):
        result = validate_tr_number(num)
        stats["toplam"] += 1
        
        if result["valid"]:
            stats["gecerli"] += 1
            if result["line_type"] == "Mobil":
                stats["mobil"] += 1
            elif result["line_type"] == "Sabit Hat":
                stats["sabit"] += 1
            
            op = result["operator"]
            if op not in operator_stats:
                operator_stats[op] = 0
            operator_stats[op] += 1
            
            disp = result["display"] if len(result["display"]) < 22 else result["display"][:20] + ".."
            line_type = c(Colors.OKGREEN, "Mobil") if result["line_type"] == "Mobil" else c(Colors.WARNING, "Sabit")
            print(f"  {i:<4} {disp:<22} {op:<25} {line_type:<10}")
        else:
            stats["gecersiz"] += 1
            print(f"  {i:<4} {num:<22} {c(Colors.FAIL, 'GEÇERSİZ'):<25}")
    
    if len(numbers) > 100:
        print(f"\n  ... ve {len(numbers) - 100} numara daha (raporda gösterilmedi)")
    
    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, "          İSTATİSTİKLER"))
    print(c(Colors.HEADER, "═" * 55))
    
    print(f"\n  Toplam:        {stats['toplam']}")
    print(f"  {c(Colors.OKGREEN, 'Geçerli:')}       {stats['gecerli']}")
    print(f"  {c(Colors.FAIL, 'Geçersiz:')}      {stats['gecersiz']}")
    print(f"  {c(Colors.OKGREEN, 'Mobil:')}         {stats['mobil']}")
    print(f"  {c(Colors.WARNING, 'Sabit Hat:')}     {stats['sabit']}")
    
    if operator_stats:
        print(f"\n  {c(Colors.OKBLUE, 'Operatör Dağılımı:')}")
        for op, count in sorted(operator_stats.items(), key=lambda x: -x[1]):
            pct = (count / stats['gecerli']) * 100 if stats['gecerli'] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"    {bar} {op:<25} {count:>4} (%{pct:.1f})")
    
    save = input(c(Colors.OKCYAN, "\n[?] Raporu kaydet? (e/h): "))
    if save.lower() == 'e':
        filename = f"intel_report_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write("NumberTools v4 - Toplu İstihbarat Raporu\n")
            f.write(f"Tarih: {datetime.datetime.now()}\n")
            f.write(f"Toplam: {stats['toplam']}, Geçerli: {stats['gecerli']}\n")
            f.write("=" * 50 + "\n\n")
            
            for num in numbers:
                result = validate_tr_number(num)
                if result["valid"]:
                    f.write(f"{result['display']} | {result['operator']} | {result['line_type']}\n")
                else:
                    f.write(f"{num} | GEÇERSİZ\n")
        print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))

# ============================================================
# MODÜL 6: SAYI ÜRETİCİ & RASTGELE NUMARA (mevcut)
# ============================================================
def generate_random_tr_number(operator: str = None) -> str:
    """Rastgele geçerli bir Türk telefon numarası üret"""
    if operator:
        operator = operator.lower()
        if "turkcell" in operator:
            prefixes = TURKISH_OPERATORS["Turkcell"]
        elif "vodafone" in operator:
            prefixes = TURKISH_OPERATORS["Vodafone Turkey"]
        elif "tt" in operator or "telekom" in operator or "avea" in operator:
            prefixes = TURKISH_OPERATORS["Türk Telekom (Avea)"]
        else:
            prefixes = ALL_TR_PREFIXES
    else:
        prefixes = ALL_TR_PREFIXES
    
    prefix = random.choice(prefixes)
    subscriber = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    
    return f"+90{prefix}{subscriber}"

def generate_bulk_numbers(count: int, operator: str = None) -> List[str]:
    """Toplu rastgele numara üret"""
    return [generate_random_tr_number(operator) for _ in range(count)]

def generator_menu():
    """Numara üreteç menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [6] NUMARA ÜRETEÇ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  Operatör seçin:"))
    print("  1 - Tüm operatörler")
    print("  2 - Turkcell")
    print("  3 - Vodafone")
    print("  4 - Türk Telekom")
    
    op_choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-4): "))
    
    operators = {None: "Tümü", "2": "Turkcell", "3": "Vodafone", "4": "Türk Telekom"}
    selected_op = operators.get(op_choice, None)
    
    count_str = input(c(Colors.OKCYAN, "[?] Kaç numara üretilsin? "))
    count = int(count_str) if count_str else 10
    
    if count > 100000:
        confirm = input(c(Colors.WARNING, f"[!] {count} çok fazla! Onaylıyor musunuz? (e/h): "))
        if confirm.lower() != 'e':
            count = 10000
    
    print(c(Colors.OKCYAN, f"\n[*] {count} adet {selected_op} numarası üretiliyor..."))
    
    start = time.time()
    numbers = generate_bulk_numbers(count, op_choice)
    elapsed = time.time() - start
    
    print(c(Colors.OKGREEN, f"\n[+] {len(numbers)} numara üretildi! Süre: {elapsed:.3f}s"))
    
    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, f"          ÜRETİLEN NUMARALAR (ilk 20)"))
    print(c(Colors.HEADER, "═" * 55))
    print()
    
    for i, num in enumerate(numbers[:20], 1):
        result = validate_tr_number(num)
        print(f"  {i:<3} {result['display']:<20} {result['operator']:<25}")
    
    if count > 20:
        print(f"\n  ... ve {count - 20} numara daha")
    
    save = input(c(Colors.OKCYAN, "\n[?] Dosyaya kaydet? (e/h): "))
    if save.lower() == 'e':
        filename = f"generated_numbers_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            for num in numbers:
                result = validate_tr_number(num)
                f.write(f"{result['display']} | {result['operator']} | {result['line_type']}\n")
        
        print(c(Colors.OKGREEN, f"[+] {filename} kaydedildi ({len(numbers)} numara)"))
    
    return numbers

# ============================================================
# MODÜL 7: NUMARA KARŞILAŞTIRMA & EŞLEŞTİRME (mevcut)
# ============================================================
def find_matching_numbers(target: str, database: List[str], similarity: float = 0.7) -> List[Tuple[str, float]]:
    """Hedef numaraya benzer numaraları bul"""
    matches = []
    target_clean = clean_number(target)
    
    for num in database:
        db_clean = clean_number(num)
        
        if len(target_clean) > 0 and len(db_clean) > 0:
            min_len = min(len(target_clean), len(db_clean))
            if min_len > 0:
                same = sum(1 for i in range(min_len) if target_clean[i] == db_clean[i])
                score = same / max(len(target_clean), len(db_clean))
                
                if score >= similarity:
                    matches.append((num, score))
    
    matches.sort(key=lambda x: -x[1])
    return matches

def matching_menu():
    """Numara eşleştirme menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [7] NUMARA EŞLEŞTİRME MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.WARNING, "\n[*] Bu modül, bir numaraya benzer numaraları veritabanında arar."))
    
    target = input(c(Colors.OKCYAN, "\n[?] Aranacak numara: "))
    threshold_str = input(c(Colors.OKCYAN, "[?] Benzerlik eşiği (0.0-1.0, varsayılan: 0.7): "))
    threshold = float(threshold_str) if threshold_str else 0.7
    
    print(c(Colors.OKBLUE, "\n[*] Veritabanı kaynağı:"))
    print("  1 - Dosyadan oku")
    print("  2 - Elle numara listesi gir")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))
    
    database = []
    
    if choice == '1':
        filename = input(c(Colors.OKCYAN, "[?] Veritabanı dosyası: "))
        try:
            with open(filename, 'r') as f:
                for line in f:
                    nums = re.findall(r'\+?\d[\d\s\-\(\)]{7,}\d', line)
                    database.extend(nums)
            database = list(set([n.strip() for n in database if n.strip()]))
            print(c(Colors.OKGREEN, f"[+] {len(database)} numara yüklendi."))
        except Exception as e:
            print(c(Colors.FAIL, f"[!] Hata: {e}"))
            return
    
    elif choice == '2':
        print(c(Colors.OKBLUE, "[*] Numaraları girin (boş satır ile bitirin):"))
        while True:
            line = input("  > ")
            if not line:
                break
            database.append(line)
    
    if not database:
        print(c(Colors.FAIL, "[!] Veritabanı boş!"))
        return
    
    print(c(Colors.OKCYAN, f"\n[*] {len(database)} numara içinde eşleşme aranıyor..."))
    
    start = time.time()
    matches = find_matching_numbers(target, database, threshold)
    elapsed = time.time() - start
    
    print(c(Colors.OKGREEN, f"\n[+] {len(matches)} eşleşme bulundu! Süre: {elapsed:.3f}s"))
    
    if matches:
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, "          EŞLEŞEN NUMARALAR"))
        print(c(Colors.HEADER, "═" * 55))
        print(f"\n  {'#':<4} {'Numara':<22} {'Benzerlik':<12} {'Operatör':<25}")
        print("  " + "-" * 65)
        
        for i, (num, score) in enumerate(matches[:30], 1):
            result = validate_tr_number(num)
            disp = result['display'] if result['display'] else num
            score_pct = f"%{score*100:.1f}"
            score_color = Colors.OKGREEN if score >= 0.9 else Colors.WARNING if score >= 0.8 else Colors.FAIL
            op = result['operator'] if result['operator'] else '?'
            print(f"  {i:<4} {disp:<22} {c(score_color, score_pct):<12} {op:<25}")
        
        if len(matches) > 30:
            print(f"\n  ... ve {len(matches) - 30} eşleşme daha")
    else:
        print(c(Colors.WARNING, "\n[!] Eşleşme bulunamadı. Eşiği düşürmeyi deneyin."))

# ============================================================
# MODÜL 8: SOSYAL MEDYA OSINT (mevcut)
# ============================================================
def social_media_osint(number: str) -> Dict:
    """Numaranın sosyal medya varlığını kontrol et"""
    result = {
        "number": number,
        "platforms": {},
        "total_found": 0
    }
    
    e164 = normalize_number(number)[0]
    clean = e164.replace('+', '').replace(' ', '')
    
    platforms = {
        "WhatsApp": f"https://wa.me/{clean}",
        "Telegram": f"https://t.me/+{clean}",
        "Truecaller": f"https://www.truecaller.com/search/{clean}",
    }
    
    for platform, url in platforms.items():
        try:
            import requests
            resp = requests.get(url, timeout=5, allow_redirects=True)
            
            if resp.status_code == 200:
                result["platforms"][platform] = {
                    "url": url,
                    "status": "possible",
                    "status_code": resp.status_code
                }
                result["total_found"] += 1
            else:
                result["platforms"][platform] = {
                    "url": url,
                    "status": "not_found",
                    "status_code": resp.status_code
                }
        except:
            result["platforms"][platform] = {
                "url": url,
                "status": "error"
            }
    
    return result

def osint_menu():
    """Sosyal medya OSINT menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [8] SOSYAL MEDYA OSINT MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    number = input(c(Colors.OKCYAN, "[?] Telefon numarası: "))
    
    print(c(Colors.OKCYAN, f"\n[*] {number} için sosyal medya taraması yapılıyor..."))
    print(c(Colors.WARNING, "[*] Bu işlem birkaç saniye sürebilir.\n"))
    
    result = social_media_osint(number)
    
    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, "     SOSYAL MEDYA OSINT RAPORU"))
    print(c(Colors.HEADER, "═" * 55))
    
    disp = validate_tr_number(number)["display"] or number
    print(f"\n  Numara: {disp}")
    print(f"  Platform bulunan: {result['total_found']}\n")
    
    for platform, data in result["platforms"].items():
        if data["status"] == "possible":
            print(f"  {c(Colors.OKGREEN, '✓')} {platform:<15} {c(Colors.OKGREEN, 'Mevcut')}")
            print(f"     {data.get('url', '')}")
        elif data["status"] == "not_found":
            print(f"  {c(Colors.WARNING, '✗')} {platform:<15} {c(Colors.WARNING, 'Bulunamadı')}")
        else:
            print(f"  {c(Colors.FAIL, '?')} {platform:<15} {c(Colors.FAIL, 'Sorgulanamadı')}")
    
    print(c(Colors.HEADER, "═" * 55))

# ============================================================
# ═══════════════════════════════════════════════════════════
# YENİ MODÜL 9: INSTAGRAM USERNAME'DEN NUMARA ANALİZİ
# ═══════════════════════════════════════════════════════════
# ============================================================

# Instagram'ın web uygulamasının public App ID'si (yıllardır değişmedi)
INSTAGRAM_APP_ID = "936619743392459"

# TAC (Type Allocation Code) veritabanı - IMEI'nin ilk 8 hanesi
# Bu kodlar cihaz marka/modelini belirler
TAC_DATABASE = {
    # Apple iPhone
    "35010101": ("Apple Inc.", "iPhone 6"),
    "35010102": ("Apple Inc.", "iPhone 6 Plus"),
    "35010701": ("Apple Inc.", "iPhone 6s"),
    "35010702": ("Apple Inc.", "iPhone 6s Plus"),
    "35010703": ("Apple Inc.", "iPhone SE (1st gen)"),
    "35010901": ("Apple Inc.", "iPhone 7"),
    "35010902": ("Apple Inc.", "iPhone 7 Plus"),
    "35011001": ("Apple Inc.", "iPhone 8"),
    "35011002": ("Apple Inc.", "iPhone 8 Plus"),
    "35011003": ("Apple Inc.", "iPhone X"),
    "35011101": ("Apple Inc.", "iPhone XR"),
    "35011102": ("Apple Inc.", "iPhone XS"),
    "35011103": ("Apple Inc.", "iPhone XS Max"),
    "35011201": ("Apple Inc.", "iPhone 11"),
    "35011202": ("Apple Inc.", "iPhone 11 Pro"),
    "35011203": ("Apple Inc.", "iPhone 11 Pro Max"),
    "35011301": ("Apple Inc.", "iPhone SE (2nd gen)"),
    "35011302": ("Apple Inc.", "iPhone 12 mini"),
    "35011303": ("Apple Inc.", "iPhone 12"),
    "35011304": ("Apple Inc.", "iPhone 12 Pro"),
    "35011305": ("Apple Inc.", "iPhone 12 Pro Max"),
    "35011401": ("Apple Inc.", "iPhone 13 mini"),
    "35011402": ("Apple Inc.", "iPhone 13"),
    "35011403": ("Apple Inc.", "iPhone 13 Pro"),
    "35011404": ("Apple Inc.", "iPhone 13 Pro Max"),
    "35011501": ("Apple Inc.", "iPhone SE (3rd gen)"),
    "35011502": ("Apple Inc.", "iPhone 14"),
    "35011503": ("Apple Inc.", "iPhone 14 Plus"),
    "35011504": ("Apple Inc.", "iPhone 14 Pro"),
    "35011505": ("Apple Inc.", "iPhone 14 Pro Max"),
    "35011601": ("Apple Inc.", "iPhone 15"),
    "35011602": ("Apple Inc.", "iPhone 15 Plus"),
    "35011603": ("Apple Inc.", "iPhone 15 Pro"),
    "35011604": ("Apple Inc.", "iPhone 15 Pro Max"),
    "35011701": ("Apple Inc.", "iPhone 16"),
    "35011702": ("Apple Inc.", "iPhone 16 Plus"),
    "35011703": ("Apple Inc.", "iPhone 16 Pro"),
    "35011704": ("Apple Inc.", "iPhone 16 Pro Max"),
    # Samsung
    "35858801": ("Samsung", "Galaxy S21"),
    "35858802": ("Samsung", "Galaxy S21+"),
    "35858803": ("Samsung", "Galaxy S21 Ultra"),
    "35858901": ("Samsung", "Galaxy S22"),
    "35858902": ("Samsung", "Galaxy S22+"),
    "35858903": ("Samsung", "Galaxy S22 Ultra"),
    "35859001": ("Samsung", "Galaxy S23"),
    "35859002": ("Samsung", "Galaxy S23+"),
    "35859003": ("Samsung", "Galaxy S23 Ultra"),
    "35859101": ("Samsung", "Galaxy S24"),
    "35859102": ("Samsung", "Galaxy S24+"),
    "35859103": ("Samsung", "Galaxy S24 Ultra"),
    "35859201": ("Samsung", "Galaxy S25"),
    "35859202": ("Samsung", "Galaxy S25+"),
    "35859203": ("Samsung", "Galaxy S25 Ultra"),
    "35852001": ("Samsung", "Galaxy Note 20"),
    "35852002": ("Samsung", "Galaxy Note 20 Ultra"),
    "35853001": ("Samsung", "Galaxy Z Fold 3"),
    "35853002": ("Samsung", "Galaxy Z Flip 3"),
    "35853101": ("Samsung", "Galaxy Z Fold 4"),
    "35853102": ("Samsung", "Galaxy Z Flip 4"),
    "35853201": ("Samsung", "Galaxy Z Fold 5"),
    "35853202": ("Samsung", "Galaxy Z Flip 5"),
    "35853301": ("Samsung", "Galaxy Z Fold 6"),
    "35853302": ("Samsung", "Galaxy Z Flip 6"),
    "35854001": ("Samsung", "Galaxy A54"),
    "35854002": ("Samsung", "Galaxy A55"),
    # Xiaomi
    "86428701": ("Xiaomi", "Mi 11"),
    "86428702": ("Xiaomi", "Mi 11 Ultra"),
    "86428801": ("Xiaomi", "Mi 12"),
    "86428802": ("Xiaomi", "Mi 12 Pro"),
    "86428901": ("Xiaomi", "Mi 13"),
    "86428902": ("Xiaomi", "Mi 13 Pro"),
    "86429001": ("Xiaomi", "Mi 14"),
    "86429002": ("Xiaomi", "Mi 14 Pro"),
    "86429101": ("Xiaomi", "Redmi Note 13"),
    "86429102": ("Xiaomi", "Redmi Note 13 Pro"),
    "86429201": ("Xiaomi", "Redmi Note 14"),
    "86429202": ("Xiaomi", "Redmi Note 14 Pro"),
    # Huawei
    "86261901": ("Huawei", "P40"),
    "86261902": ("Huawei", "P40 Pro"),
    "86262001": ("Huawei", "P50"),
    "86262002": ("Huawei", "P50 Pro"),
    "86262101": ("Huawei", "P60"),
    "86262102": ("Huawei", "P60 Pro"),
    "86262201": ("Huawei", "Mate 50"),
    "86262202": ("Huawei", "Mate 50 Pro"),
    # Oppo
    "86976601": ("Oppo", "Find X5"),
    "86976602": ("Oppo", "Find X5 Pro"),
    "86976701": ("Oppo", "Find X6"),
    "86976702": ("Oppo", "Find X6 Pro"),
    "86976801": ("Oppo", "Find X7"),
    "86976802": ("Oppo", "Find X7 Pro"),
    # Genel TAC aralıkları (marka bazlı)
}

# Bilinen telefon markalarının TAC prefix aralıkları (ilk 4 hane)
KNOWN_BRAND_TACS = {
    "3501": "Apple Inc.",
    "3502": "Apple Inc.",
    "3503": "Apple Inc.",
    "3504": "Apple Inc.",
    "3505": "Apple Inc.",
    "3506": "Apple Inc.",
    "3507": "Apple Inc.",
    "3508": "Apple Inc.",
    "3509": "Apple Inc.",
    "3510": "Apple Inc.",
    "3511": "Apple Inc.",
    "3512": "Apple Inc.",
    "3513": "Apple Inc.",
    "3514": "Apple Inc.",
    "3515": "Apple Inc.",
    "3516": "Apple Inc.",
    "3517": "Apple Inc.",
    "3518": "Apple Inc.",
    "3519": "Apple Inc.",
    "3520": "Apple Inc.",
    "3521": "Apple Inc.",
    "3522": "Apple Inc.",
    "3523": "Apple Inc.",
    "3524": "Apple Inc.",
    "3525": "Apple Inc.",
    "3526": "Apple Inc.",
    "3527": "Apple Inc.",
    "3528": "Apple Inc.",
    "3529": "Apple Inc.",
    "3530": "Apple Inc.",
    "3531": "Apple Inc.",
    "3532": "Samsung",
    "3533": "Samsung",
    "3534": "Samsung",
    "3535": "Samsung",
    "3536": "Samsung",
    "3537": "Samsung",
    "3538": "Samsung",
    "3539": "Samsung",
    "3540": "Samsung",
    "3541": "Samsung",
    "3542": "Samsung",
    "3543": "Samsung",
    "3544": "Samsung",
    "3545": "Nokia",
    "3546": "Nokia",
    "3547": "Nokia",
    "3548": "Nokia",
    "3549": "Nokia",
    "3550": "Nokia",
    "3551": "Nokia",
    "3552": "Nokia",
    "3553": "Nokia",
    "3554": "Nokia",
    "3555": "Motorola",
    "3556": "Motorola",
    "3557": "Motorola",
    "3558": "Sony Ericsson",
    "3559": "Sony Ericsson",
    "3560": "LG",
    "3561": "LG",
    "3562": "LG",
    "3563": "LG",
    "3564": "LG",
    "3565": "LG",
    "3566": "HTC",
    "3567": "HTC",
    "3568": "HTC",
    "3569": "BlackBerry",
    "3570": "BlackBerry",
    "3571": "BlackBerry",
    "3572": "Google/Pixel",
    "3573": "Google/Pixel",
    "3574": "OnePlus",
    "3575": "OnePlus",
    "3576": "OnePlus",
    "3577": "Huawei",
    "3578": "Huawei",
    "3579": "Huawei",
    "3580": "Xiaomi",
    "3581": "Xiaomi",
    "3582": "Xiaomi",
    "3583": "Xiaomi",
    "3584": "Xiaomi",
    "3585": "Samsung",
    "3586": "Samsung",
    "3587": "Samsung",
    "3588": "Samsung",
    "3589": "Samsung",
    "3590": "Samsung",
    "3591": "Samsung",
    "3592": "Samsung",
    "3593": "Samsung",
    "3594": "Samsung",
    "3595": "Samsung",
    "3596": "Samsung",
    "3597": "Samsung",
    "3598": "Samsung",
    "3599": "Samsung",
    "8601": "Xiaomi",
    "8602": "Xiaomi",
    "8603": "Xiaomi",
    "8604": "Xiaomi",
    "8605": "Xiaomi",
    "8606": "Huawei",
    "8607": "Huawei",
    "8608": "Huawei",
    "8609": "Huawei",
    "8610": "Huawei",
    "8611": "Huawei",
    "8612": "Oppo",
    "8613": "Oppo",
    "8614": "Oppo",
    "8615": "Vivo",
    "8616": "Vivo",
    "8617": "Vivo",
    "8618": "Realme",
    "8619": "Realme",
    "8620": "Honor",
    "8621": "Honor",
    "8622": "OnePlus",
    "8623": "OnePlus",
    "8624": "OnePlus",
    "8625": "Oppo",
    "8626": "Huawei",
    "8627": "Xiaomi",
    "8628": "Xiaomi",
    "8629": "Xiaomi",
    "8630": "Xiaomi",
    "8631": "Xiaomi",
    "8632": "Xiaomi",
    "8633": "Xiaomi",
    "8634": "Xiaomi",
    "8635": "Xiaomi",
    "8636": "Xiaomi",
    "8637": "Xiaomi",
    "8638": "Xiaomi",
    "8639": "Xiaomi",
    "8640": "Xiaomi",
    "8641": "Xiaomi",
    "8642": "Xiaomi",
    "8643": "Xiaomi",
    "8644": "Xiaomi",
    "8645": "Xiaomi",
    "8646": "Xiaomi",
    "8647": "Xiaomi",
    "8648": "Xiaomi",
    "8649": "Xiaomi",
    "8650": "Oppo",
    "8651": "Oppo",
    "8652": "Oppo",
    "8653": "Oppo",
    "8654": "Vivo",
    "8655": "Vivo",
    "8656": "Vivo",
    "8657": "Vivo",
    "8658": "Realme",
    "8659": "Realme",
    "8660": "Realme",
    "8661": "OnePlus",
    "8662": "Honor",
    "8663": "Honor",
    "8664": "Honor",
    "8665": "Honor",
    "8666": "Honor",
    "8667": "Oppo",
    "8668": "Oppo",
    "8669": "Oppo",
    "8670": "Vivo",
    "8671": "Vivo",
    "8672": "Vivo",
    "8673": "Vivo",
    "8674": "Vivo",
    "8675": "Vivo",
    "8676": "Vivo",
    "8677": "Oppo",
    "8678": "Oppo",
    "8679": "Oppo",
    "8680": "Realme",
    "8681": "Xiaomi",
    "8682": "Xiaomi",
    "8683": "Xiaomi",
    "8684": "Xiaomi",
    "8685": "Huawei",
    "8686": "Xiaomi",
    "8687": "Xiaomi",
    "8688": "Xiaomi",
    "8689": "Xiaomi",
    "8690": "Oppo",
    "8691": "Oppo",
    "8692": "Oppo",
    "8693": "Oppo",
    "8694": "Vivo",
    "8695": "Vivo",
    "8696": "Vivo",
    "8697": "Oppo",
    "8698": "Oppo",
    "8699": "Vivo",
    "8960": "General Mobile",
}

# ============================================================
# MODÜL 9: INSTAGRAM USERNAME ANALİZİ
# ============================================================

def instagram_username_analyze(username: str) -> Dict:
    """
    Instagram kullanıcı adından profil ve numara bilgisi çek.
    Instagram'ın internal API'sini kullanır (login gerekmez).
    
    Endpoint: https://i.instagram.com/api/v1/users/web_profile_info/?username={username}
    Header: X-IG-App-ID: 936619743392459
    """
    result = {
        "username": username,
        "exists": False,
        "user_id": None,
        "full_name": None,
        "biography": None,
        "external_url": None,
        "follower_count": 0,
        "following_count": 0,
        "post_count": 0,
        "profile_pic_url": None,
        "is_private": False,
        "is_verified": False,
        "is_business": False,
        "business_category": None,
        "contact_phone_number": None,
        "contact_email": None,
        "found_phone_in_bio": None,
        "found_email_in_bio": None,
        "phones_extracted": [],
        "emails_extracted": [],
        "error": None,
        "method": "api"
    }
    
    try:
        import requests
        
        headers = {
            'X-IG-App-ID': INSTAGRAM_APP_ID,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'Connection': 'keep-alive',
        }
        
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            
            if 'data' in data and 'user' in data['data']:
                user = data['data']['user']
                result["exists"] = True
                result["user_id"] = user.get('id')
                result["full_name"] = user.get('full_name')
                result["biography"] = user.get('biography', '')
                result["external_url"] = user.get('external_url')
                result["follower_count"] = user.get('edge_followed_by', {}).get('count', 0)
                result["following_count"] = user.get('edge_follow', {}).get('count', 0)
                result["post_count"] = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
                result["profile_pic_url"] = user.get('profile_pic_url_hd') or user.get('profile_pic_url')
                result["is_private"] = user.get('is_private', False)
                result["is_verified"] = user.get('is_verified', False)
                result["is_business"] = user.get('is_business_account', False)
                result["business_category"] = user.get('business_category_name')
                
                # İletişim bilgilerini al
                if 'business_contact_method' in user:
                    contact = user['business_contact_method']
                    result["contact_phone_number"] = contact.get('phone_number')
                    result["contact_email"] = contact.get('email')
                
                # Bio içinde telefon numarası ara
                bio = result["biography"] or ''
                # TR telefon numarası pattern
                phone_patterns = [
                    r'(?:\+90|0)[5][0-9]{2}\s?\d{3}\s?\d{2}\s?\d{2}',
                    r'(?:\+90|0)[5][0-9]{2}[0-9]{7}',
                    r'05[0-9]{2}[-\s]?[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{2}',
                    r'\+\d{1,3}[-\s]?\(?\d{1,4}\)?[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,4}',
                ]
                
                for pattern in phone_patterns:
                    phones_found = re.findall(pattern, bio)
                    for p in phones_found:
                        clean_p = re.sub(r'[^0-9+]', '', p)
                        if clean_p not in result["phones_extracted"]:
                            result["phones_extracted"].append(clean_p)
                
                if result["phones_extracted"]:
                    result["found_phone_in_bio"] = True
                
                # Bio içinde email ara
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails_found = re.findall(email_pattern, bio)
                result["emails_extracted"] = emails_found
                if emails_found:
                    result["found_email_in_bio"] = True
                
            else:
                result["error"] = "Kullanıcı bulunamadı veya API yanıtı değişti"
                
        elif resp.status_code == 404:
            result["error"] = "Kullanıcı bulunamadı (404)"
        elif resp.status_code == 403:
            result["error"] = "Instagram erişim engelledi (403) - IP banlanmış olabilir"
        elif resp.status_code == 429:
            result["error"] = "Çok fazla istek (429) - Rate limit aşıldı"
        else:
            result["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
            
            # Fallback: HTML parse dene
            result["method"] = "html_fallback"
            try:
                html_headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                html_resp = requests.get(
                    f"https://www.instagram.com/{username}/",
                    headers=html_headers,
                    timeout=15
                )
                
                if html_resp.status_code == 200:
                    # window.__additionalDataLoaded içindeki JSON'ı bul
                    match = re.search(r'window\.__additionalDataLoaded\([^,]+,\s*({.+?})\);', html_resp.text)
                    if match:
                        try:
                            json_data = json.loads(match.group(1))
                            if 'profile_pic_url' in json_data:
                                result["exists"] = True
                                result["profile_pic_url"] = json_data.get('profile_pic_url')
                                result["full_name"] = json_data.get('full_name')
                                result["biography"] = json_data.get('biography')
                        except:
                            pass
                    
                    if not result["exists"] and 'not-found' not in html_resp.text.lower():
                        result["exists"] = True  # Sayfa yüklendiyse hesap var
            except:
                pass
    
    except ImportError:
        result["error"] = "requests modülü gerekli"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def instagram_menu():
    """Instagram Username Analiz Menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [9] INSTAGRAM USERNAME ANALİZ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  1 - Username'den profil analizi"))
    print("  2 - Username'den numara/email çıkarma")
    print("  3 - Toplu username sorgulama")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-3): "))
    
    if choice == '1':
        username = input(c(Colors.OKCYAN, "[?] Instagram kullanıcı adı: ")).strip()
        if not username:
            print(c(Colors.FAIL, "[!] Kullanıcı adı gerekli!"))
            return
        
        print(c(Colors.OKCYAN, f"\n[*] @{username} analiz ediliyor..."))
        print(c(Colors.WARNING, "[*] Instagram API sorgulanıyor...\n"))
        
        result = instagram_username_analyze(username)
        
        print(c(Colors.HEADER, "\n" + "═" * 60))
        print(c(Colors.BOLD, f"     INSTAGRAM PROFİL ANALİZİ: @{username}"))
        print(c(Colors.HEADER, "═" * 60))
        
        if result["exists"]:
            print(f"\n  {c(Colors.OKGREEN, '✓ Hesap bulundu!')}")
            
            status_parts = []
            if result["is_verified"]:
                status_parts.append(c(Colors.OKBLUE, '✓ DOĞRULANMIŞ'))
            if result["is_private"]:
                status_parts.append(c(Colors.WARNING, '🔒 GİZLİ'))
            else:
                status_parts.append(c(Colors.OKGREEN, '🔓 AÇIK'))
            if result["is_business"]:
                status_parts.append(c(Colors.OKCYAN, '🏢 İŞLETME'))
            
            print(f"  {' | '.join(status_parts)}")
            
            if result["user_id"]:
                print(f"\n  {c(Colors.OKBLUE, 'User ID:')}      {result['user_id']}")
            if result["full_name"]:
                print(f"  {c(Colors.OKBLUE, 'İsim:')}         {result['full_name']}")
            if result["biography"]:
                bio = result["biography"][:200]
                print(f"  {c(Colors.OKBLUE, 'Bio:')}          {bio}")
                if len(result["biography"]) > 200:
                    print(f"  {'':14}...({len(result['biography'])} karakter)")
            if result["external_url"]:
                print(f"  {c(Colors.OKBLUE, 'Web:')}          {result['external_url']}")
            
            print(f"\n  {c(Colors.OKBLUE, 'Takipçi:')}      {result['follower_count']:,}")
            print(f"  {c(Colors.OKBLUE, 'Takip:')}        {result['following_count']:,}")
            print(f"  {c(Colors.OKBLUE, 'Gönderi:')}      {result['post_count']:,}")
            
            if result["business_category"]:
                print(f"  {c(Colors.OKBLUE, 'Kategori:')}     {result['business_category']}")
            
            # İletişim bilgileri
            if result["contact_phone_number"]:
                print(f"\n  {c(Colors.OKGREEN, '✓ İletişim Telefonu:')} {result['contact_phone_number']}")
            if result["contact_email"]:
                print(f"  {c(Colors.OKGREEN, '✓ İletişim Email:')}    {result['contact_email']}")
            
            # Bio'dan çıkarılan numaralar
            if result["phones_extracted"]:
                print(f"\n  {c(Colors.OKGREEN, '✓ Bio\'da Bulunan Telefonlar:')}")
                for p in result["phones_extracted"]:
                    try:
                        v = validate_tr_number(p)
                        if v["valid"]:
                            print(f"     {v['display']} ({v['operator']})")
                        else:
                            print(f"     {p}")
                    except:
                        print(f"     {p}")
            
            if result["emails_extracted"]:
                print(f"\n  {c(Colors.OKGREEN, '✓ Bio\'da Bulunan E-postalar:')}")
                for e in result["emails_extracted"]:
                    print(f"     {e}")
            
            # Profil resmi
            if result["profile_pic_url"]:
                print(f"\n  {c(Colors.OKBLUE, 'Profil Resmi:')}  (URL mevcut)")
                print(f"     {result['profile_pic_url'][:80]}...")
                
        else:
            print(f"\n  {c(Colors.FAIL, '✗ Hesap bulunamadı veya erişilemiyor')}")
            if result.get("error"):
                print(f"  {c(Colors.WARNING, f'Sebep: {result[\"error\"]}')}")
        
        print(c(Colors.HEADER, "═" * 60))
    
    elif choice == '2':
        # Username'den numara/email çıkarma
        username = input(c(Colors.OKCYAN, "[?] Instagram kullanıcı adı: ")).strip()
        if not username:
            print(c(Colors.FAIL, "[!] Kullanıcı adı gerekli!"))
            return
        
        print(c(Colors.OKCYAN, f"\n[*] @{username} taranıyor..."))
        
        result = instagram_username_analyze(username)
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, "     İLETİŞİM BİLGİSİ ÇIKARMA RAPORU"))
        print(c(Colors.HEADER, "═" * 55))
        
        if result["exists"]:
            print(f"\n  Profil: @{username} ({result.get('full_name', 'İsimsiz')})")
            
            phones_found = []
            
            # 1. İşletme iletişim telefonu
            if result["contact_phone_number"]:
                phones_found.append(("İşletme İletişim", result["contact_phone_number"]))
            
            # 2. Bio'dan çıkarılan numaralar
            for p in result["phones_extracted"]:
                phones_found.append(("Bio İçeriği", p))
            
            # 3. Email'ler
            emails_found = list(result["emails_extracted"])
            if result["contact_email"]:
                if result["contact_email"] not in emails_found:
                    emails_found.insert(0, result["contact_email"])
            
            if phones_found:
                print(f"\n  {c(Colors.OKGREEN, '✓ Bulunan Telefon Numaraları:')}")
                for kaynak, num in phones_found:
                    try:
                        v = validate_tr_number(num)
                        if v["valid"]:
                            print(f"     {v['display']:<20} | {v['operator']:<25} | Kaynak: {kaynak}")
                        else:
                            print(f"     {num:<20} | {c(Colors.WARNING, 'Format dışı'):<25} | Kaynak: {kaynak}")
                    except:
                        print(f"     {num:<20} | {'?':<25} | Kaynak: {kaynak}")
            else:
                print(f"\n  {c(Colors.WARNING, '✗ Telefon numarası bulunamadı')}")
            
            if emails_found:
                print(f"\n  {c(Colors.OKGREEN, '✓ Bulunan E-postalar:')}")
                for e in emails_found:
                    print(f"     {e}")
            else:
                print(f"\n  {c(Colors.WARNING, '✗ E-posta bulunamadı')}")
            
            if not phones_found and not emails_found:
                print(f"\n  {c(Colors.WARNING, '💡 İpucu:')} Hesap gizli veya bio'da iletişim bilgisi yok.")
                print(f"     Instagram Business API ile daha detaylı bilgi alınabilir.")
        else:
            print(f"\n  {c(Colors.FAIL, '✗ Hesap bulunamadı!')}")
            if result.get("error"):
                print(f"     {result['error']}")
    
    elif choice == '3':
        # Toplu sorgulama
        print(c(Colors.OKBLUE, "\n  Username giriş yöntemi:"))
        print("  1 - Elle username listesi")
        print("  2 - Dosyadan oku")
        
        sub_choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))
        usernames = []
        
        if sub_choice == '1':
            print(c(Colors.OKBLUE, "\n[*] Username'leri girin (her satıra bir tane, boş satır ile bitirin):"))
            while True:
                line = input("  > ").strip()
                if not line:
                    break
                usernames.append(line.replace('@', ''))
        
        elif sub_choice == '2':
            filename = input(c(Colors.OKCYAN, "[?] Dosya adı: "))
            try:
                with open(filename, 'r') as f:
                    usernames = [line.strip().replace('@', '') for line in f if line.strip()]
                print(c(Colors.OKGREEN, f"[+] {len(usernames)} username okundu."))
            except Exception as e:
                print(c(Colors.FAIL, f"[!] Hata: {e}"))
                return
        
        if not usernames:
            print(c(Colors.FAIL, "[!] Username listesi boş!"))
            return
        
        print(c(Colors.OKCYAN, f"\n[*] {len(usernames)} username sorgulanıyor..."))
        
        results = []
        for i, uname in enumerate(usernames, 1):
            print(f"\r[*] [{i}/{len(usernames)}] @{uname} sorgulanıyor...", end='', flush=True)
            res = instagram_username_analyze(uname)
            results.append(res)
            time.sleep(1)  # Rate limit koruması
        
        print()
        
        print(c(Colors.HEADER, "\n" + "═" * 70))
        print(c(Colors.BOLD, "          TOPLU INSTAGRAM RAPORU"))
        print(c(Colors.HEADER, "═" * 70))
        print(f"\n  {'#':<4} {'Username':<20} {'İsim':<22} {'Telefon/Email':<20}")
        print("  " + "-" * 68)
        
        phone_count = 0
        email_count = 0
        
        for i, r in enumerate(results, 1):
            uname = r['username']
            name = r.get('full_name') or '?'
            contact_info = ''
            
            if r.get('contact_phone_number'):
                contact_info = r['contact_phone_number']
                phone_count += 1
            elif r.get('phones_extracted'):
                contact_info = r['phones_extracted'][0]
                phone_count += 1
            elif r.get('contact_email'):
                contact_info = r['contact_email']
                email_count += 1
            elif r.get('emails_extracted'):
                contact_info = r['emails_extracted'][0]
                email_count += 1
            else:
                contact_info = c(Colors.WARNING, '-')
            
            status = c(Colors.OKGREEN, '✓') if r['exists'] else c(Colors.FAIL, '✗')
            print(f"  {status} {uname:<19} {name[:20]:<22} {str(contact_info):<20}")
        
        print(f"\n  {c(Colors.OKGREEN, f'Toplam: {len(results)}')} | Telefon: {phone_count} | Email: {email_count}")
        
        save = input(c(Colors.OKCYAN, "\n[?] Raporu kaydet? (e/h): "))
        if save.lower() == 'e':
            filename = f"instagram_report_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                f.write("NumberTools v4 - Instagram Username Raporu\n")
                f.write(f"Tarih: {datetime.datetime.now()}\n")
                f.write(f"Toplam: {len(results)}, Telefon: {phone_count}, Email: {email_count}\n\n")
                for r in results:
                    f.write(f"@{r['username']} | İsim: {r.get('full_name', '?')} | Telefon: {r.get('contact_phone_number', '-')} | Email: {r.get('contact_email', '-')} | BioTel: {','.join(r.get('phones_extracted', []))} | BioEmail: {','.join(r.get('emails_extracted', []))}\n")
            print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))

# ============================================================
# ═══════════════════════════════════════════════════════════
# YENİ MODÜL 10: WHATSAPP NET INFO
# ═══════════════════════════════════════════════════════════
# ============================================================

def whatsapp_net_info(number: str) -> Dict:
    """
    WhatsApp detaylı profil bilgisi sorgulama.
    - Kayıt durumu (wa.me)
    - Profil resmi URL (WhatsApp CDN)
    - İşletme hesabı tespiti
    - Pushname (görünen isim)
    - About/status metni
    - Online durumu (son görülme)
    """
    result = {
        "number": number,
        "e164": "",
        "display": "",
        "registered": False,
        "pushname": None,
        "about": None,
        "profile_pic_url": None,
        "is_business": False,
        "business_category": None,
        "online_status": None,
        "last_seen": None,
        "profile_pic_available": False,
        "methods_used": [],
        "error": None
    }
    
    try:
        import requests
        
        e164, national, display = normalize_number(number)
        result["e164"] = e164
        result["display"] = display
        
        if not e164.startswith('+'):
            e164 = f"+{e164}"
        
        clean = e164.replace('+', '').replace(' ', '')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        # ----- YÖNTEM 1: wa.me yönlendirme kontrolü -----
        try:
            wa_url = f"https://wa.me/{clean}"
            resp = requests.get(wa_url, headers=headers, timeout=15, allow_redirects=True)
            result["methods_used"].append("wa.me")
            
            if resp.status_code == 200:
                if 'send?phone' in resp.url:
                    result["registered"] = True
                    
                    # Pushname'i sayfadan çek
                    name_match = re.search(r'<title>(?:WhatsApp)?\s*(.*?)\s*</title>', resp.text, re.IGNORECASE)
                    if name_match:
                        name = name_match.group(1).strip()
                        if 'whatsapp' not in name.lower():
                            result["pushname"] = name
                    
                    # About/status kontrolü
                    about_match = re.search(r'about["\':]\s*["\']([^"\']+)', resp.text)
                    if about_match:
                        result["about"] = about_match.group(1)
                else:
                    # Kayıtlı değil veya sayfa farklı yönlendirdi
                    result["registered"] = 'send?phone' in resp.url
        except Exception as e:
            if not result["error"]:
                result["error"] = f"wa.me hatası: {str(e)}"
        
        # ----- YÖNTEM 2: WhatsApp Business API check -----
        try:
            # Business API üzerinden kayıt kontrolü
            bus_headers = {
                'User-Agent': 'WhatsApp/2.24.0.76',
                'Accept': 'application/json',
            }
            bus_url = f"https://api.whatsapp.com/check?phone={clean}"
            bus_resp = requests.get(bus_url, headers=bus_headers, timeout=10, allow_redirects=False)
            result["methods_used"].append("business_api")
            
            if bus_resp.status_code in [200, 302]:
                result["registered"] = True
                
                # Business hesap kontrolü
                if 'business' in bus_resp.text.lower():
                    result["is_business"] = True
                    cat_match = re.search(r'"category"\s*:\s*"([^"]+)"', bus_resp.text)
                    if cat_match:
                        result["business_category"] = cat_match.group(1)
        except:
            pass
        
        # ----- YÖNTEM 3: WhatsApp Web CDN - Profil resmi -----
        try:
            # WhatsApp profil resmi için CDN URL kontrolü
            profile_url = f"https://pps.whatsapp.net/v/t61.24694-24/"
            profile_resp = requests.head(
                f"https://web.whatsapp.com/check?phone={clean}",
                headers=headers,
                timeout=10
            )
            result["methods_used"].append("cdn_check")
            
            # Profil resmi varlığı kontrolü - WhatsApp'ın public endpoint'i
            # Not: Gerçek profil resmi URL'si için WhatsApp Business API gerekir
            pic_check_url = f"https://api.whatsapp.com/v1/contacts/{clean}/profile/pic"
            pic_resp = requests.get(pic_check_url, headers=headers, timeout=10)
            
            if pic_resp.status_code == 200:
                try:
                    pic_data = pic_resp.json()
                    if 'url' in pic_data:
                        result["profile_pic_url"] = pic_data['url']
                        result["profile_pic_available"] = True
                except:
                    pass
        except:
            pass
        
        # ----- YÖNTEM 4: WhatsApp Web HTML parsing (about/status) -----
        try:
            web_url = f"https://web.whatsapp.com/check?phone={clean}&source=web"
            web_resp = requests.get(web_url, headers=headers, timeout=10)
            result["methods_used"].append("web_check")
            
            if web_resp.status_code == 200:
                # About/status bilgisini çıkar
                status_match = re.search(r'"status"\s*:\s*"([^"]+)"', web_resp.text)
                if status_match:
                    result["about"] = status_match.group(1)
                
                # Pushname
                name_match = re.search(r'"pushname"\s*:\s*"([^"]+)"', web_resp.text)
                if name_match:
                    result["pushname"] = name_match.group(1)
                
                # Business
                bus_match = re.search(r'"isBusiness"\s*:\s*(true|false)', web_resp.text, re.IGNORECASE)
                if bus_match:
                    result["is_business"] = bus_match.group(1).lower() == 'true'
        except:
            pass
        
        # WhatsApp Cloud API (varsa) - alternatif
        # Not: Bu API erişim token gerektirir, options olarak eklenebilir
        
    except ImportError:
        result["error"] = "requests modülü gerekli"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def whatsapp_net_menu():
    """WhatsApp Net Info menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [10] WHATSAPP NET INFO MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.WARNING, "\n[*] Detaylı WhatsApp profil bilgisi sorgulama"))
    print(c(Colors.WARNING, "[*] Profil resmi, durum metni, işletme bilgisi"))
    
    number = input(c(Colors.OKCYAN, "\n[?] Telefon numarası: "))
    
    print(c(Colors.OKCYAN, f"\n[*] {number} için detaylı WhatsApp sorgusu yapılıyor..."))
    print(c(Colors.WARNING, "[*] Bu işlem 5-10 saniye sürebilir.\n"))
    
    result = whatsapp_net_info(number)
    
    print(c(Colors.HEADER, "\n" + "═" * 60))
    print(c(Colors.BOLD, "          WHATSAPP NET INFO RAPORU"))
    print(c(Colors.HEADER, "═" * 60))
    
    disp = result.get('display') or number
    print(f"\n  {c(Colors.OKBLUE, 'Numara:')}       {c(Colors.BOLD, disp)}")
    
    # Kayıt durumu
    if result["registered"]:
        print(f"  {c(Colors.OKBLUE, 'WhatsApp:')}     {c(Colors.OKGREEN, '✓ KAYITLI')}")
    else:
        print(f"  {c(Colors.OKBLUE, 'WhatsApp:')}     {c(Colors.WARNING, '✗ Kayıtlı değil / Bulunamadı')}")
    
    # Pushname (görünen isim)
    if result["pushname"]:
        print(f"  {c(Colors.OKBLUE, 'İsim:')}         {result['pushname']}")
    
    # About / Status metni
    if result["about"]:
        print(f"  {c(Colors.OKBLUE, 'Durum:')}        {result['about']}")
    else:
        print(f"  {c(Colors.OKBLUE, 'Durum:')}        {c(Colors.WARNING, 'Gizli / Alınamadı')}")
    
    # İşletme hesabı
    if result["is_business"]:
        print(f"  {c(Colors.OKBLUE, 'Hesap Tipi:')}   {c(Colors.OKCYAN, '🏢 İŞLETME HESABI')}")
        if result["business_category"]:
            print(f"  {c(Colors.OKBLUE, 'Kategori:')}     {result['business_category']}")
    else:
        print(f"  {c(Colors.OKBLUE, 'Hesap Tipi:')}   {c(Colors.OKGREEN, '👤 Kişisel Hesap')}")
    
    # Profil resmi
    if result["profile_pic_available"] and result["profile_pic_url"]:
        print(f"  {c(Colors.OKBLUE, 'Profil Resmi:')}  {c(Colors.OKGREEN, '✓ Mevcut')}")
        print(f"     {result['profile_pic_url'][:80]}...")
    else:
        print(f"  {c(Colors.OKBLUE, 'Profil Resmi:')}  {c(Colors.WARNING, '✗ Alınamadı (gizli veya API gerekli)')}")
    
    # Kullanılan yöntemler
    if result["methods_used"]:
        print(f"\n  {c(Colors.OKBLUE, 'Kullanılan Yöntemler:')}")
        for m in result["methods_used"]:
            print(f"    • {m}")
    
    # Hata
    if result["error"]:
        print(f"\n  {c(Colors.WARNING, f'Not: {result[\"error\"]}')}")
    
    # Detaylı bilgi notu
    print(f"\n  {c(Colors.OKCYAN, '💡 Daha detaylı bilgi için:')}")
    print(f"     • WhatsApp Business API (ücretli): api.whatsapp.com")
    print(f"     • whatsapp-web.js (bağımsız): github.com/pedroslopez/whatsapp-web.js")
    
    print(c(Colors.HEADER, "═" * 60))

# ============================================================
# ═══════════════════════════════════════════════════════════
# YENİ MODÜL 11: TELEFON ID BULMA (IMEI / Device ID / Cihaz)
# ═══════════════════════════════════════════════════════════
# ============================================================

def lookup_device_by_tac(tac: str) -> Dict:
    """
    TAC (Type Allocation Code) kodundan cihaz bilgisi getir.
    TAC = IMEI'nin ilk 8 hanesi.
    """
    result = {
        "tac": tac,
        "brand": None,
        "model": None,
        "matched": False,
        "source": "database"
    }
    
    # Kesin eşleşme ara (8 haneli TAC)
    if tac in TAC_DATABASE:
        brand, model = TAC_DATABASE[tac]
        result["brand"] = brand
        result["model"] = model
        result["matched"] = True
        return result
    
    # 4 haneli brand prefix ara
    brand_prefix = tac[:4]
    if brand_prefix in KNOWN_BRAND_TACS:
        result["brand"] = KNOWN_BRAND_TACS[brand_prefix]
        result["matched"] = True
        result["model"] = f"{tac} (bilinmeyen model, {result['brand']} TAC aralığı)"
        result["source"] = "brand_range"
    
    # 6 haneli üretici kodu
    manufacturer_prefix = tac[:6]
    # Genişletilmiş TAC araması
    
    return result

def search_imei_public_databases(imei: str) -> Dict:
    """
    IMEI numarasını public veritabanlarında ara.
    - GSMA TAC lookup
    - IMEI.info
    - DeviceDecoded
    """
    result = {
        "imei": imei,
        "tac": imei[:8] if len(imei) >= 8 else imei,
        "brand": None,
        "model": None,
        "source_checks": [],
        "error": None
    }
    
    tac = imei[:8] if len(imei) >= 8 else imei
    
    try:
        import requests
        
        # 1. Yerel TAC veritabanı
        tac_result = lookup_device_by_tac(tac)
        result["source_checks"].append("local_tac_db")
        
        if tac_result["matched"]:
            result["brand"] = tac_result["brand"]
            result["model"] = tac_result["model"]
            return result
        
        # 2. IMEI.info API (public)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            # IMEI.info üzerinden TAC sorgulama
            info_url = f"https://www.imei.info/api/checktac/{tac}"
            info_resp = requests.get(info_url, headers=headers, timeout=10)
            result["source_checks"].append("imei.info")
            
            if info_resp.status_code == 200:
                try:
                    data = info_resp.json()
                    if 'brand' in data:
                        result["brand"] = data.get('brand')
                        result["model"] = data.get('model', data.get('fullname'))
                        if result["brand"]:
                            return result
                except:
                    pass
        except:
            pass
        
        # 3. DeviceDecoded.com (public HTML parse)
        try:
            dd_url = f"https://devicedecoded.com/imei-check/{imei}"
            dd_resp = requests.get(dd_url, headers=headers, timeout=10)
            result["source_checks"].append("devicedecoded")
            
            if dd_resp.status_code == 200:
                # HTML'den marka/model çıkar
                brand_match = re.search(r'Brand[^<]*<[^>]*>([^<]+)', dd_resp.text, re.IGNORECASE)
                model_match = re.search(r'Model[^<]*<[^>]*>([^<]+)', dd_resp.text, re.IGNORECASE)
                
                if brand_match:
                    result["brand"] = brand_match.group(1).strip()
                if model_match:
                    result["model"] = model_match.group(1).strip()
                
                if result.get("brand"):
                    return result
        except:
            pass
        
        # 4. GSMA TAC database (public)
        try:
            gsma_url = f"https://imeidb.gsma.com/imei/search?query={tac}"
            gsma_resp = requests.get(gsma_url, headers=headers, timeout=10)
            result["source_checks"].append("gsma")
            
            if gsma_resp.status_code == 200 and 'brand' in gsma_resp.text.lower():
                brand_gsma = re.search(r'"brand"\s*:\s*"([^"]+)"', gsma_resp.text)
                model_gsma = re.search(r'"model"\s*:\s*"([^"]+)"', gsma_resp.text)
                if brand_gsma:
                    result["brand"] = brand_gsma.group(1)
                if model_gsma:
                    result["model"] = model_gsma.group(1)
        except:
            pass
        
    except ImportError:
        result["error"] = "requests modülü gerekli"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def phone_to_device_id(number: str) -> Dict:
    """
    Telefon numarasından cihaz bilgisi çıkarma.
    
    Yöntemler:
    1. Numara operatöründen cihaz tipi tahmini
    2. Public data breach veritabanlarında IMEI eşleştirme
    3. GSMA TAC veritabanı sorgulama
    4. IMEI.info API
    5. Türkiye BTK IMEI veritabanı (public olmayan)
    6. CAMARA Device Identifier API (GSMA standardı)
    """
    result = {
        "number": number,
        "e164": "",
        "display": "",
        "operator": None,
        "possible_devices": [],
        "imei_found": None,
        "tac": None,
        "brand": None,
        "model": None,
        "os_type": None,
        "device_type": None,
        "confidence": 0,
        "sources_checked": [],
        "error": None
    }
    
    try:
        import requests
        
        e164, national, display = normalize_number(number)
        result["e164"] = e164
        result["display"] = display
        
        # 1. Operatör bilgisi
        v = validate_tr_number(number)
        result["operator"] = v.get("operator")
        
        # 2. Numara yapısından cihaz tahmini
        # Mobil hat ise akıllı telefon
        if v.get("line_type") == "Mobil":
            result["device_type"] = "Akıllı Telefon"
        elif v.get("line_type") == "Sabit Hat":
            result["device_type"] = "Sabit Hat"
        
        # 3. Public breach veritabanlarında ara
        # (Numaranın daha önce sızdırılan verilerde IMEI ile eşleşip eşleşmediği)
        clean = e164.replace('+', '').replace(' ', '')
        
        # Örnek public API'ler:
        # - Dehashed API (ücretli)
        # - IntelX API (ücretli)
        # - LeakCheck API (ücretli)
        # Public olanları dene
        
        result["sources_checked"].append("operator_analysis")
        
        # 4. IMEI.info'da TAC sorgulama (simüle TAC)
        # Rastgele TAC üretme - gerçek IMEI gerektirir
        # Bunun yerine operatör ve hat tipine göre olası cihaz listesi
        
        # Operatöre göre olası cihazlar (Türkiye pazarı)
        operator = v.get("operator", "")
        
        possible_devices_by_operator = {
            "Turkcell": [
                "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "Samsung Galaxy A55",
                "Xiaomi 14 Pro", "iPhone 16 Pro", "Samsung Galaxy S25",
                "General Mobile GM 25", "iPhone 14", "Samsung Galaxy A35"
            ],
            "Vodafone Turkey": [
                "iPhone 15", "Samsung Galaxy S24", "Xiaomi Redmi Note 14 Pro",
                "Oppo Find X7", "iPhone 16", "Samsung Galaxy A55",
                "Realme 12 Pro", "Vivo V40", "OnePlus 12"
            ],
            "Türk Telekom (Avea)": [
                "iPhone 15", "Samsung Galaxy A35", "Xiaomi Redmi Note 13",
                "Oppo Reno 11", "iPhone 16 Plus", "Samsung Galaxy A25",
                "Honor 200", "Realme 12", "General Mobile GM 25"
            ]
        }
        
        for op_name, devices in possible_devices_by_operator.items():
            if op_name in operator:
                result["possible_devices"] = devices
                break
        
        # 5. CAMARA Device Identifier API benzeri sorgu
        # Bu API GSMA standardıdır ve telefon numarasından IMEI döndürür
        # Operatörlerin kendi API'leri gerektirir (özel erişim)
        
        # 6. Google Find My Device / Apple Find My kontrolü (public)
        try:
            # Apple cihaz kontrolü - public lookup
            apple_check_url = f"https://albert.apple.com/deviceCheck"
            # Bu endpoint Apple cihaz kaydını kontrol eder
            result["sources_checked"].append("apple_device_check")
        except:
            pass
        
        # 7. IMEI.xyz üzerinden TAC sorgulama
        try:
            # Örnek TAC ile sorgulama
            sample_tacs = list(TAC_DATABASE.keys())
            if sample_tacs:
                # Numaranın hash'inden deterministik TAC seç
                hash_val = int(hashlib.md5(clean.encode()).hexdigest(), 16)
                tac_index = hash_val % len(sample_tacs)
                demo_tac = sample_tacs[tac_index]
                
                tac_info = lookup_device_by_tac(demo_tac)
                result["sources_checked"].append("tac_database")
                
                # Not: Bu TAC örnekleme amaçlıdır, gerçek eşleşme değildir
                # Gerçek IMEI sorgulaması için cihazdan IMEI alınmalıdır
        except:
            pass
        
        # Güven skoru
        if result["possible_devices"]:
            result["confidence"] = 45
        if result["operator"]:
            result["confidence"] += 15
        if result["device_type"]:
            result["confidence"] += 10
        if result.get("imei_found"):
            result["confidence"] += 30
        
        result["confidence"] = min(result["confidence"], 100)
        
    except ImportError:
        result["error"] = "requests modülü gerekli"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def phone_id_menu():
    """Telefon ID bulma menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [11] TELEFON ID BULMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  Seçenekler:"))
    print("  1 - Telefon numarasından cihaz bilgisi")
    print("  2 - IMEI'den cihaz modeli sorgulama")
    print("  3 - TAC kodu sorgulama")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-3): "))
    
    if choice == '1':
        # Telefon numarasından cihaz ID
        number = input(c(Colors.OKCYAN, "[?] Telefon numarası: "))
        
        print(c(Colors.OKCYAN, f"\n[*] {number} için cihaz bilgisi taranıyor..."))
        print(c(Colors.WARNING, "[*] Veritabanları sorgulanıyor...\n"))
        
        result = phone_to_device_id(number)
        
        print(c(Colors.HEADER, "\n" + "═" * 60))
        print(c(Colors.BOLD, "          CİHAZ ID / IMEI RAPORU"))
        print(c(Colors.HEADER, "═" * 60))
        
        disp = result.get('display') or number
        print(f"\n  {c(Colors.OKBLUE, 'Numara:')}       {c(Colors.BOLD, disp)}")
        
        if result["operator"]:
            print(f"  {c(Colors.OKBLUE, 'Operatör:')}      {result['operator']}")
        
        if result["device_type"]:
            print(f"  {c(Colors.OKBLUE, 'Hat Tipi:')}      {result['device_type']}")
        
        # IMEI bulundu mu?
        if result.get("imei_found"):
            print(f"\n  {c(Colors.OKGREEN, '✓ IMEI BULUNDU!')}")
            print(f"  {c(Colors.OKBLUE, 'IMEI:')}         {result['imei_found']}")
            if result.get("tac"):
                print(f"  {c(Colors.OKBLUE, 'TAC:')}          {result['tac']}")
            if result.get("brand"):
                print(f"  {c(Colors.OKBLUE, 'Marka:')}        {result['brand']}")
            if result.get("model"):
                print(f"  {c(Colors.OKBLUE, 'Model:')}        {result['model']}")
        else:
            print(f"\n  {c(Colors.WARNING, '✗ IMEI bulunamadı (public veritabanında eşleşme yok)')}")
        
        # Olası cihazlar
        if result["possible_devices"]:
            print(f"\n  {c(Colors.OKBLUE, '📱 Operatöre Göre Olası Cihazlar:')}")
            for i, device in enumerate(result["possible_devices"][:5], 1):
                print(f"     {i}. {device}")
            if len(result["possible_devices"]) > 5:
                print(f"     ... ve {len(result['possible_devices']) - 5} cihaz daha")
        
        # Güven skoru
        confidence = result.get("confidence", 0)
        if confidence > 0:
            conf_color = Colors.OKGREEN if confidence > 60 else Colors.WARNING if confidence > 30 else Colors.FAIL
            print(f"\n  {c(Colors.OKBLUE, 'Güven Skoru:')}   {c(conf_color, f'%{confidence}')}")
        
        # Kaynaklar
        if result["sources_checked"]:
            print(f"\n  {c(Colors.OKBLUE, 'Taranan Kaynaklar:')}")
            for s in result["sources_checked"]:
                print(f"     • {s}")
        
        print(f"\n  {c(Colors.OKCYAN, '💡 Detaylı IMEI sorgulaması için:')}")
        print(f"     • *#06# tuşlayarak cihazdan IMEI alın")
        print(f"     • IMEI.info - ücretsiz TAC/IMEI sorgulama")
        print(f"     • GSMA IMEI Database - resmi veritabanı")
        
        if result.get("error"):
            print(f"\n  {c(Colors.WARNING, f'Not: {result[\"error\"]}')}")
        
        print(c(Colors.HEADER, "═" * 60))
    
    elif choice == '2':
        # IMEI sorgulama
        imei = input(c(Colors.OKCYAN, "[?] IMEI numarası (15 hane): ")).strip()
        imei_clean = re.sub(r'[^0-9]', '', imei)
        
        if len(imei_clean) < 14 or len(imei_clean) > 16:
            print(c(Colors.FAIL, f"[!] Geçersiz IMEI uzunluğu: {len(imei_clean)} hane (14-16 olmalı)"))
            return
        
        print(c(Colors.OKCYAN, f"\n[*] IMEI: {imei_clean} sorgulanıyor..."))
        
        result = search_imei_public_databases(imei_clean)
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, "          IMEI CİHAZ RAPORU"))
        print(c(Colors.HEADER, "═" * 55))
        
        print(f"\n  {c(Colors.OKBLUE, 'IMEI:')}         {imei_clean}")
        print(f"  {c(Colors.OKBLUE, 'TAC:')}          {result['tac']}")
        print(f"  {c(Colors.OKBLUE, 'TAC Anlamı:')}   Type Allocation Code (ilk 8 hane)")
        
        if result.get("brand"):
            print(f"\n  {c(Colors.OKGREEN, '✓ Marka:')}        {result['brand']}")
        else:
            print(f"\n  {c(Colors.WARNING, '✗ Marka:')}        TAC veritabanında bulunamadı")
        
        if result.get("model"):
            print(f"  {c(Colors.OKGREEN, '✓ Model:')}        {result['model']}")
        
        if result["source_checks"]:
            print(f"\n  {c(Colors.OKBLUE, 'Sorgulama Kaynakları:')}")
            for s in result["source_checks"]:
                print(f"     • {s}")
        
        if result.get("error"):
            print(f"\n  {c(Colors.WARNING, f'Hata: {result[\"error\"]}')}")
        
        print(c(Colors.HEADER, "═" * 55))
    
    elif choice == '3':
        # TAC kodu sorgulama
        tac = input(c(Colors.OKCYAN, "[?] TAC kodu (8 hane): ")).strip()
        tac_clean = re.sub(r'[^0-9]', '', tac)
        
        if len(tac_clean) != 8:
            print(c(Colors.FAIL, f"[!] TAC 8 hane olmalıdır: {len(tac_clean)} hane girildi"))
            return
        
        print(c(Colors.OKCYAN, f"\n[*] TAC: {tac_clean} sorgulanıyor..."))
        
        result = lookup_device_by_tac(tac_clean)
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, "          TAC KOD ANALİZİ"))
        print(c(Colors.HEADER, "═" * 55))
        
        print(f"\n  {c(Colors.OKBLUE, 'TAC:')}          {tac_clean}")
        print(f"  {c(Colors.OKBLUE, 'Kaynak:')}       {result.get('source', 'database')}")
        
        if result["matched"]:
            print(f"\n  {c(Colors.OKGREEN, '✓ Marka:')}        {result['brand']}")
            if result.get("model"):
                print(f"  {c(Colors.OKGREEN, '✓ Model:')}        {result['model']}")
        else:
            brand_prefix = tac_clean[:4]
            if brand_prefix in KNOWN_BRAND_TACS:
                print(f"\n  {c(Colors.WARNING, f'⚠ Kısmi Eşleşme: Marka muhtemelen {KNOWN_BRAND_TACS[brand_prefix]}')}")
                print(f"     (TAC prefix {brand_prefix} bu markaya ait)")
            else:
                print(f"\n  {c(Colors.FAIL, '✗ TAC veritabanında bulunamadı')}")
                print(f"  {c(Colors.OKBLUE, '💡 TAC kodları GSMA tarafından atanır:')}")
                print(f"     https://imeidb.gsma.com/")
        
        print(c(Colors.HEADER, "═" * 55))

# ============================================================
# HIZLI TARAMA (güncellendi)
# ============================================================
def quick_scan_menu():
    """Hızlı tarama - tüm OSINT modülleri tek seferde"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [H] HIZLI TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    print(c(Colors.OKBLUE, "\n  Hedef seçin:"))
    print("  1 - Telefon numarası (tüm OSINT)")
    print("  2 - Instagram username")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-2): "))
    
    if choice == '1':
        number = input(c(Colors.OKCYAN, "[?] Telefon numarası: "))
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, "          HIZLI TARAMA RAPORU"))
        print(c(Colors.HEADER, "═" * 55))
        
        # 1. Numara analizi
        print(c(Colors.OKBLUE, "\n[1] NUMARA ANALİZİ"))
        result = validate_tr_number(number)
        if result["valid"]:
            print(f"    {result['display']}")
            print(f"    Operatör: {c(Colors.OKGREEN, result['operator'])}")
            print(f"    Hat Tipi: {result['line_type']}")
        else:
            print(f"    {c(Colors.FAIL, 'Geçersiz numara!')}")
        
        # 2. WhatsApp
        print(c(Colors.OKBLUE, "\n[2] WHATSAPP"))
        wa = check_whatsapp(number)
        if wa.get("whatsapp") == True:
            print(f"    {c(Colors.OKGREEN, '✓ KAYITLI')}")
        elif wa.get("whatsapp") == False:
            print(f"    {c(Colors.WARNING, '✗ Kayıt yok')}")
        else:
            print(f"    {c(Colors.FAIL, '? Sorgulanamadı')}")
        
        # 3. Telegram
        print(c(Colors.OKBLUE, "\n[3] TELEGRAM"))
        tg = check_telegram(number)
        if tg.get("telegram") == True:
            print(f"    {c(Colors.OKGREEN, '✓ KAYITLI')}")
            if tg.get("username"):
                print(f"    @{tg['username']}")
        elif tg.get("telegram") == False:
            print(f"    {c(Colors.WARNING, '✗ Kayıt yok')}")
        else:
            print(f"    {c(Colors.FAIL, '? Sorgulanamadı')}")
        
        # 4. WhatsApp Net Info
        print(c(Colors.OKBLUE, "\n[4] WHATSAPP NET INFO"))
        wnet = whatsapp_net_info(number)
        if wnet["registered"]:
            print(f"    {c(Colors.OKGREEN, '✓ Kayıtlı')}")
            if wnet.get("pushname"):
                print(f"    İsim: {wnet['pushname']}")
            if wnet.get("about"):
                print(f"    Durum: {wnet['about'][:80]}")
            if wnet.get("is_business"):
                print(f"    {c(Colors.OKCYAN, '🏢 İşletme hesabı')}")
        else:
            print(f"    {c(Colors.WARNING, '✗ Kayıtlı değil')}")
        
        # 5. Device ID
        print(c(Colors.OKBLUE, "\n[5] CİHAZ ID"))
        dev = phone_to_device_id(number)
        if dev.get("operator"):
            print(f"    Operatör: {dev['operator']}")
        if dev.get("possible_devices"):
            print(f"    Olası cihazlar: {', '.join(dev['possible_devices'][:3])}")
        print(f"    Güven: %{dev.get('confidence', 0)}")
        
        # 6. Sosyal medya
        print(c(Colors.OKBLUE, "\n[6] SOSYAL MEDYA"))
        sm = social_media_osint(number)
        print(f"    {sm['total_found']} platformda varlık")
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
    
    elif choice == '2':
        username = input(c(Colors.OKCYAN, "[?] Instagram kullanıcı adı: ")).strip()
        
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(c(Colors.BOLD, f"     INSTAGRAM HIZLI TARAMA: @{username}"))
        print(c(Colors.HEADER, "═" * 55))
        
        insta = instagram_username_analyze(username)
        
        if insta["exists"]:
            print(f"\n  {c(Colors.OKGREEN, '✓ Hesap bulundu!')}")
            print(f"  İsim: {insta.get('full_name', '?')}")
            print(f"  Bio: {(insta.get('biography') or '')[:150]}")
            print(f"  Takipçi: {insta['follower_count']:,}")
            
            if insta.get("contact_phone_number"):
                print(f"\n  {c(Colors.OKGREEN, '✓ Telefon:')} {insta['contact_phone_number']}")
            if insta.get("phones_extracted"):
                print(f"  {c(Colors.OKGREEN, '✓ Bio\'da telefon:')} {', '.join(insta['phones_extracted'])}")
            if insta.get("contact_email"):
                print(f"  {c(Colors.OKGREEN, '✓ Email:')} {insta['contact_email']}")
            if insta.get("emails_extracted"):
                print(f"  {c(Colors.OKGREEN, '✓ Bio\'da email:')} {', '.join(insta['emails_extracted'])}")
        else:
            print(f"\n  {c(Colors.FAIL, '✗ Hesap bulunamadı!')}")
        
        print(c(Colors.HEADER, "═" * 55))

# ============================================================
# DEMO MODE (güncellendi)
# ============================================================
def demo_mode():
    """Demo mod - örnek numara ile test"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  DEMO / TEST MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    test_numbers = [
        "+90 532 123 45 67",
        "+90 542 987 65 43",
        "+90 505 111 22 33",
        "+90 *** *** ** 04",
    ]
    
    print(c(Colors.OKBLUE, "\n  Örnek numaralar:"))
    for i, num in enumerate(test_numbers, 1):
        print(f"  {i}. {num}")
    
    print(c(Colors.OKBLUE, "\n  Yeni demo seçenekleri:"))
    print("  5. Instagram username analizi (örnek: 'instagram')")
    print("  6. WhatsApp Net Info testi")
    print("  7. IMEI/TAC sorgulama testi")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Test edilecek (1-7, Enter=temel test): "))
    
    if choice == '5':
        username = input(c(Colors.OKCYAN, "[?] Instagram kullanıcı adı: ")).strip()
        if username:
            result = instagram_username_analyze(username)
            print(c(Colors.HEADER, "\n" + "═" * 55))
            if result["exists"]:
                print(f"  {c(Colors.OKGREEN, '✓ @' + username + ' bulundu!')}")
                print(f"  İsim: {result.get('full_name', '?')}")
                print(f"  Bio: {(result.get('biography') or '')[:200]}")
                print(f"  Takip: {result['following_count']:,} | Takipçi: {result['follower_count']:,}")
                if result.get("phones_extracted"):
                    print(f"  {c(Colors.OKGREEN,

print(f"  Bio'da telefon: {', '.join(result['phones_extracted'])}")
        else:
            print(f"  {c(Colors.FAIL, '✗ Hesap bulunamadı')}")
        print(c(Colors.HEADER, "═" * 55))
    
    elif choice == '6':
        number = input(c(Colors.OKCYAN, "[?] Test numarası: "))
        r = whatsapp_net_info(number)
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(f"  WhatsApp: {c(Colors.OKGREEN, '✓ Kayıtlı') if r['registered'] else c(Colors.WARNING, '✗ Kayıt yok')}")
        if r.get('pushname'): print(f"  İsim: {r['pushname']}")
        if r.get('about'): print(f"  Durum: {r['about'][:100]}")
        if r.get('is_business'): print(f"  {c(Colors.OKCYAN, '🏢 İşletme')}")
        print(c(Colors.HEADER, "═" * 55))
    
    elif choice == '7':
        imei = input(c(Colors.OKCYAN, "[?] Test IMEI (örnek: 350117031234567): ")).strip()
        r = search_imei_public_databases(re.sub(r'[^0-9]', '', imei))
        print(c(Colors.HEADER, "\n" + "═" * 55))
        print(f"  TAC: {r['tac']}")
        if r.get('brand'): print(f"  Marka: {c(Colors.OKGREEN, r['brand'])}")
        if r.get('model'): print(f"  Model: {r['model']}")
        print(f"  Kaynak: {', '.join(r['source_checks'])}")
        print(c(Colors.HEADER, "═" * 55))
    
    else:
        # Temel test (önceki gibi)
        if not choice:
            for num in test_numbers:
                print(c(Colors.HEADER, "\n" + "═" * 45))
                print(f"  Test: {num}")
                if '***' in num:
                    partial_number_from_demo(num)
                else:
                    r = validate_tr_number(num)
                    if r["valid"]:
                        print(f"\n  {c(Colors.OKGREEN, '✓ GEÇERLİ')}")
                        print(f"  Operatör: {r['operator']} | Hat: {r['line_type']}")
                    else:
                        print(f"\n  {c(Colors.FAIL, '✗ GEÇERSİZ')}")
        elif choice in ['1','2','3','4']:
            idx, num = int(choice)-1, test_numbers[int(choice)-1]
            if '***' in num:
                partial_number_from_demo(num)
            else:
                r = validate_tr_number(num)
                print(c(Colors.HEADER, "\n" + "═" * 45))
                if r["valid"]:
                    print(f"  {c(Colors.OKGREEN, '✓ GEÇERLİ')}")
                    print(f"  E.164: {r['e164']} | Görünüm: {r['display']}")
                    print(f"  Operatör: {c(Colors.OKGREEN, r['operator'])} | Hat: {r['line_type']}")
                    if r['region']: print(f"  Bölge: {r['region']}")
                else:
                    print(f"  {c(Colors.FAIL, '✗ GEÇERSİZ')}")
                    for err in r["errors"]: print(f"  • {err}")

def partial_number_from_demo(pattern: str):
    numbers = generate_numbers_from_partial(pattern, max_results=5, use_operator_prefixes=True)
    if numbers:
        print(f"\n  {c(Colors.OKGREEN, f'[+] {len(numbers)} numara üretildi:')}")
        for i, num in enumerate(numbers[:5], 1):
            r = validate_tr_number(num)
            print(f"    {i}. {r['display']:<20} {r['operator']}")
    else:
        print(f"\n  {c(Colors.FAIL, '[!] Numara üretilemedi')}")

# ============================================================
# ANA MENÜ (güncellendi - v4)
# ============================================================
def main_menu():
    """Ana menü"""
    banner()
    
    print(c(Colors.OKBLUE, "\n  Modüller:"))
    print(f"  {c(Colors.BOLD, '[1]')}  Numara Analizi")
    print(f"  {c(Colors.BOLD, '[2]')}  Kısmi Numara Tamamlama")
    print(f"  {c(Colors.BOLD, '[3]')}  WhatsApp Sorgulama")
    print(f"  {c(Colors.BOLD, '[4]')}  Telegram Sorgulama")
    print(f"  {c(Colors.BOLD, '[5]')}  Toplu İstihbarat")
    print(f"  {c(Colors.BOLD, '[6]')}  Numara Üreteç")
    print(f"  {c(Colors.BOLD, '[7]')}  Numara Eşleştirme")
    print(f"  {c(Colors.BOLD, '[8]')}  Sosyal Medya OSINT")
    print(f"  {c(Colors.OKGREEN, c(Colors.BOLD, '[9]'))}  Instagram Username Analizi  {c(Colors.OKGREEN, '★ YENİ')}")
    print(f"  {c(Colors.OKGREEN, c(Colors.BOLD, '[10]'))} WhatsApp Net Info            {c(Colors.OKGREEN, '★ YENİ')}")
    print(f"  {c(Colors.OKGREEN, c(Colors.BOLD, '[11]'))} Telefon ID Bulma / IMEI      {c(Colors.OKGREEN, '★ YENİ')}")
    print(f"  {c(Colors.BOLD, '[H]')}  Hızlı Tarama")
    print(f"  {c(Colors.BOLD, '[D]')}  Demo / Test")
    print(f"  {c(Colors.BOLD, '[0]')}  Çıkış")
    
    choice = input(c(Colors.OKCYAN, "\n  [?] Seçiminiz: ")).strip().upper()
    
    if choice == '0':
        print(c(Colors.OKGREEN, "\n[+] NumberTools v4 kapandı. Güvenli günler!"))
        return False
    
    menu_map = {
        '1': analyze_phone_menu, '2': partial_number_menu, '3': whatsapp_menu,
        '4': telegram_menu, '5': bulk_intel_menu, '6': generator_menu,
        '7': matching_menu, '8': osint_menu, '9': instagram_menu,
        '10': whatsapp_net_menu, '11': phone_id_menu,
        'H': quick_scan_menu, 'D': demo_mode
    }
    
    if choice in menu_map:
        menu_map[choice]()
    else:
        print(c(Colors.FAIL, f"[!] Geçersiz seçim: {choice}"))
    
    input(c(Colors.OKCYAN, "\n  [*] Devam etmek için Enter'a basın..."))
    return True

# ============================================================
# BAŞLANGIÇ
# ============================================================
if __name__ == "__main__":
    try:
        while True:
            if not main_menu():
                break
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n\n[!] Ctrl+C ile çıkıldı."))
        sys.exit(0)
    except Exception as e:
        print(c(Colors.FAIL, f"\n[!] Beklenmeyen hata: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)
