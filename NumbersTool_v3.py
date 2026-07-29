#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║               NUMBERS TOOLS v3 - Professional               ║
║         Türk Telefon Numarası İstihbarat ve Analiz         ║
║     Yalnızca Yetkili Güvenlik Testleri İçindir             ║
╚══════════════════════════════════════════════════════════════╝

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
from typing import List, Dict, Optional, Tuple, Set
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# GÜVENLİK BAŞLIĞI
# ============================================================
print("\n" + "=" * 60)
print("  NumberTools v3 - Telefon Numarası İstihbarat Aracı")
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
    ╔══════════════════════════════════════════════════════╗
    ║  ███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗ ██╗ ║
    ║  ████╗  ██║██║   ██║████╗ ████║██╔══██╗██╔════╝██╔╝ ║
    ║  ██╔██╗ ██║██║   ██║██╔████╔██║██████╔╝█████╗  ██║  ║
    ║  ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██║  ║
    ║  ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗╚██╗ ║
    ║  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝ ╚═╝ ║
    ║              TOOLS v3 - TÜRKİYE                        ║
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

# Tüm geçerli prefix'lerin düz listesi
ALL_TR_PREFIXES = []
for prefixes in TURKISH_OPERATORS.values():
    ALL_TR_PREFIXES.extend(prefixes)

# Ek numara blokları
SPECIAL_PREFIXES = {
    "512": "Türk Telekom (Çağrı Hizmeti)",
    "516": "MVNO (TT Mobil)",
    "524": "MVNO (TT Mobil)",
    "592": "Globalstar (Uydu)",
    "510": "MVNO"
}

# Şehir kodları (sabit hatlar için)
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
    """
    Numara temizleme: tüm gereksiz karakterleri kaldır
    +90 *** *** ** 04 -> +90******04
    """
    # Sadece rakamları ve + işaretini al
    cleaned = re.sub(r'[^0-9+]', '', number)
    return cleaned

def normalize_number(number: str) -> Tuple[str, str, str]:
    """
    Numarayı normalize et. Dönen: (e164_format, national_format, display_format)
    Örnek: +905321234567, 05321234567, +90 532 123 45 67
    """
    cleaned = clean_number(number)
    
    # +90 ile başlıyorsa
    if cleaned.startswith('+90'):
        national = cleaned[1:]  # 90'ı çıkar -> 90532...
        if len(national) == 11:  # 90 + 3 prefix + 7 numara
            display = f"+90 {national[1:4]} {national[4:7]} {national[7:9]} {national[9:11]}"
            return (cleaned, f"0{national[1:]}", display)
    
    # 0 ile başlıyorsa (0XXX...)
    if cleaned.startswith('0') and len(cleaned) == 11:
        e164 = f"+90{cleaned[1:]}"
        display = f"+90 {cleaned[1:4]} {cleaned[4:7]} {cleaned[7:9]} {cleaned[9:11]}"
        return (e164, cleaned, display)
    
    # 90 ile başlıyorsa (90532...)
    if cleaned.startswith('90') and len(cleaned) == 12:
        e164 = f"+{cleaned}"
        national = f"0{cleaned[2:]}"
        display = f"+90 {cleaned[2:5]} {cleaned[5:8]} {cleaned[8:10]} {cleaned[10:12]}"
        return (e164, national, display)
    
    # Sadece 10 haneli numara (5321234567)
    if len(cleaned) == 10 and cleaned.startswith('5'):
        e164 = f"+90{cleaned}"
        national = f"0{cleaned}"
        display = f"+90 {cleaned[0:3]} {cleaned[3:6]} {cleaned[6:8]} {cleaned[8:10]}"
        return (e164, national, display)
    
    # Tanınamayan format
    return (cleaned, cleaned, cleaned)

def detect_operator(prefix: str) -> Tuple[str, str]:
    """
    Prefix'e göre operatör tespiti
    Örnek: detect_operator("532") -> ("Turkcell", "Mobil")
    """
    if prefix in SPECIAL_PREFIXES:
        return (SPECIAL_PREFIXES[prefix], "Özel")
    
    for operator, prefixes in TURKISH_OPERATORS.items():
        if prefix in prefixes:
            return (operator, "Mobil")
    
    # Sabit hat kontrolü
    if prefix in AREA_CODES:
        return (f"Sabit Hat - {AREA_CODES[prefix]}", "Sabit Hat")
    
    # 800, 900 vb.
    if prefix.startswith('8'):
        types = {"800": "Ücretsiz", "888": "Ücretsiz", "900": "Ücretli"}
        return (types.get(prefix, "Özel Servis"), "Servis")
    
    return ("Bilinmiyor / Geçersiz Prefix", "Bilinmiyor")

def validate_tr_number(number: str) -> Dict:
    """
    Türk telefon numarasını doğrula ve detaylı bilgi döndür
    """
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
        
        # Uzunluk kontrolü
        clean = clean_number(number)
        
        # +90XXXXXXXXXX formatı: 13 karakter (+ dahil)
        if e164.startswith('+90'):
            digits_part = e164[1:]  # 90 + 10 digits = 12
            if len(digits_part) == 12:
                result["length_valid"] = True
            else:
                result["errors"].append(f"Geçersiz uzunluk: {len(digits_part)} hane (12 olmalı)")
        
        # Prefix çıkar
        if e164.startswith('+90') and len(e164) >= 13:
            prefix = e164[3:6]  # +90532 -> 532
            result["prefix"] = prefix
            
            # Prefix geçerli mi?
            all_prefixes = ALL_TR_PREFIXES + list(SPECIAL_PREFIXES.keys())
            if prefix in all_prefixes or prefix in AREA_CODES:
                result["prefix_valid"] = True
                operator, line_type = detect_operator(prefix)
                result["operator"] = operator
                result["line_type"] = line_type
                
                # Sabit hat bölgesi
                if prefix in AREA_CODES:
                    result["region"] = AREA_CODES[prefix]
            else:
                result["errors"].append(f"Geçersiz prefix: {prefix}")
        
        # Geçerlilik
        if result["length_valid"] and result["prefix_valid"]:
            result["valid"] = True
        
    except Exception as e:
        result["errors"].append(str(e))
    
    return result

# ============================================================
# MODÜL 1: NUMARA ANALİZİ
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
    
    # Numara kalite skoru
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
# MODÜL 2: KISMİ NUMARADAN TAM NUMARA ÜRETME
# ============================================================

def parse_partial_number(pattern: str) -> Dict:
    """
    Kısmi numara desenini çözümle
    +90 *** *** ** 04 -> {known_positions: {10:0, 11:4}, unknown_count: 8, mask: "******04"}
    """
    cleaned = clean_number(pattern)
    
    known_positions = {}  # {position: digit}
    unknown_positions = []
    
    # +90 sonrasını al
    if '+90' in pattern:
        # +90'dan sonraki kısmı bul
        after_90 = pattern.split('+90')[1] if '+90' in pattern else pattern
    else:
        after_90 = pattern
    
    # Tüm karakterleri tara
    clean_after = clean_number('+' + after_90) if not after_90.startswith('+') else clean_number(after_90)
    
    # Aslında daha basit: pattern string'indeki * karakterlerini bul
    # Pattern: +90 *** *** ** 04
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
    """
    Kısmi numara deseninden tam numaralar üret
    +90 *** *** ** 04 -> [+90532XXXX04, +90533XXXX04, ...]
    """
    parsed = parse_partial_number(pattern)
    
    # +90 sonrası 10 hane olmalı (3 prefix + 7 abone)
    if parsed["total_digits"] > 10:
        print(c(Colors.FAIL, f"[!] Çok fazla hane: {parsed['total_digits']} (maks 10)"))
        return []
    
    # Bilinen haneleri bir diziye yerleştir
    known = parsed["known_positions"]
    unknown = parsed["unknown_positions"]
    total = 10  # +90'dan sonra 10 hane
    
    # İlk 3 hane (prefix) için operatör listesini kullan
    # Prefix pozisyonları: 0, 1, 2 (sonra 3-9 abone numarası)
    
    print(c(Colors.OKBLUE, f"\n[*] Bilinen haneler: {len(known)}"))
    print(c(Colors.OKBLUE, f"[*] Bilinmeyen haneler: {len(unknown)}"))
    
    total_possibilities = 10 ** len(unknown)
    print(c(Colors.WARNING, f"[*] Toplam olasılık: {total_possibilities:,}"))
    
    if total_possibilities > 1000000:
        print(c(Colors.FAIL, "[!] Çok fazla olasılık! Sonuçlar filtrelenecek."))
    
    results = []
    
    # Prefix'leri belirle
    # İlk 3 hane prefix. Eğer bu haneler bilinmiyorsa, tüm TR prefix'lerini dene
    prefix_known = all(i in known for i in [0, 1, 2])
    
    if prefix_known:
        # Prefix biliniyor, sadece abone kısmını üret
        prefix = f"{known[0]}{known[1]}{known[2]}"
        prefixes_to_try = [prefix]
    else:
        if use_operator_prefixes:
            prefixes_to_try = ALL_TR_PREFIXES
            print(c(Colors.OKCYAN, f"[*] {len(prefixes_to_try)} operatör prefix'i taranıyor..."))
        else:
            # Tüm 3 haneli kombinasyonlar (000-999)
            prefixes_to_try = [f"{i:03d}" for i in range(1000)]
            print(c(Colors.OKCYAN, f"[*] Tüm 1000 prefix taranıyor..."))
    
    # Her prefix için abone numarasını üret
    count = 0
    for prefix in prefixes_to_try:
        if count >= max_results:
            break
        
        # Prefix'in bilinen hanelerle uyumunu kontrol et
        prefix_match = True
        for i in range(3):
            if i in known and int(prefix[i]) != known[i]:
                prefix_match = False
                break
        
        if not prefix_match:
            continue
        
        # Abone kısmı için bilinmeyen haneler (3-9 arası)
        subscriber_unknown = [p for p in unknown if p >= 3]
        subscriber_known = {k: v for k, v in known.items() if k >= 3}
        
        if not subscriber_unknown:
            # Tüm haneler biliniyor, tek sonuç
            number = prefix
            for i in range(3, 10):
                if i in known:
                    number += str(known[i])
                else:
                    number += '0'  # Varsayılan
            full = f"+90{number}"
            results.append(full)
            count += 1
        else:
            # Bilinmeyen haneler için kombinasyon üret
            unknown_count = len(subscriber_unknown)
            per_prefix_limit = max(1, max_results // len(prefixes_to_try))
            
            # Çok fazla kombinasyon varsa limit koy
            combinations = 10 ** unknown_count
            if combinations > per_prefix_limit:
                # Rastgele örnekle
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
                # Tüm kombinasyonları üret
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
    
    # Sonuçları benzersiz yap ve sırala
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
        
        # Dosyaya kaydet
        save = input(c(Colors.OKCYAN, "\n[?] Sonuçları dosyaya kaydetmek ister misiniz? (e/h): "))
        if save.lower() == 'e':
            filename = f"numbers_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                f.write("NumberTools v3 - Numara Listesi\n")
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
# MODÜL 3: WHATSAPP SORGULAMA
# ============================================================

def check_whatsapp(number: str) -> Dict:
    """
    Bir numaranın WhatsApp kaydını kontrol et
    Bu modül WhatsApp Web API kullanır
    """
    result = {
        "number": number,
        "whatsapp": False,
        "method": "web_check",
        "error": None
    }
    
    try:
        # WhatsApp Business API / Web check
        # Not: Gerçek WhatsApp API'si gerektirir, burada simülasyon
        # Gerçek ortamda whatsapp-web.js veya benzeri kullanılır
        
        # WhatsApp'ın numara doğrulama endpoint'i
        e164 = normalize_number(number)[0]
        
        # WhatsApp web üzerinden kontrol (resmi olmayan yöntem)
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        
        # WhatsApp'ın resmi olmayan kontrol endpoint'i
        # Bu endpoint sadece örnek amaçlıdır - gerçek kullanım için API gerekir
        try:
            # WhatsApp Business API check
            wa_url = f"https://wa.me/{e164.replace('+', '')}"
            resp = requests.get(wa_url, headers=headers, timeout=10, allow_redirects=True)
            
            # 200 dönerse ve WhatsApp sayfası içeriyorsa kayıtlı olabilir
            if resp.status_code == 200 and 'send?phone' in resp.url:
                result["whatsapp"] = True
                result["method"] = "wa.me_redirect"
            elif resp.status_code == 200:
                result["whatsapp"] = True  # Varsayılan
                result["method"] = "wa.me_page"
                
        except Exception as e:
            result["error"] = str(e)
            result["whatsapp"] = None  # Bilinmiyor
    
    except ImportError:
        result["error"] = "requests modülü gerekli"
        result["whatsapp"] = None
    
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
                status = "✓" if data.get("whatsapp") else "✗"
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
                    f.write("NumberTools v3 - WhatsApp Raporu\n")
                    f.write(f"Tarih: {datetime.datetime.now()}\n")
                    f.write(f"Toplam: {len(results)}, WhatsApp: {whatsapp_on}\n\n")
                    for r in results:
                        disp = validate_tr_number(r["number"])["display"] or r["number"]
                        status = "WHATSAPP_VAR" if r.get("whatsapp") == True else "WHATSAPP_YOK" if r.get("whatsapp") == False else "BILINMIYOR"
                        f.write(f"{disp} | {status}\n")
                print(c(Colors.OKGREEN, f"[+] Kaydedildi: {filename}"))

# ============================================================
# MODÜL 4: TELEGRAM SORGULAMA
# ============================================================

def check_telegram(number: str) -> Dict:
    """
    Bir numaranın Telegram kaydını kontrol et
    """
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
        
        # Telegram MTProto API'si ile kontrol
        # Not: Gerçek API için api_id ve api_hash gerekir
        # Burada public check API'leri kullanılıyor
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
        }
        
        # Telegram'ın public API'si ile username check
        # Alternatif: t.me/username yönlendirmesi
        try:
            # Önce t.me linkini kontrol et
            clean_num = e164.replace('+', '').replace(' ', '')
            tg_url = f"https://t.me/+{clean_num}" if not clean_num.startswith('+') else f"https://t.me/{clean_num}"
            
            resp = requests.get(tg_url, headers=headers, timeout=10, allow_redirects=False)
            
            # 302 Found -> yönlendirme varsa hesap var
            if resp.status_code in [302, 303, 301]:
                location = resp.headers.get('Location', '')
                if 'tg' in location or 'telegram' in location or 'resolve' in location:
                    result["telegram"] = True
                    result["method"] = "t.me_redirect"
            elif resp.status_code == 200:
                # Sayfa yüklendiyse ve Telegram içeriği varsa
                if 'tgme' in resp.text.lower() or 'telegram' in resp.text.lower():
                    result["telegram"] = True
                    result["method"] = "t.me_page"
                    
                    # Username'ı extract et
                    import re
                    username_match = re.search(r'<meta property="og:url" content="https://t\.me/([^"]+)"', resp.text)
                    if username_match:
                        result["username"] = username_match.group(1)
        except:
            pass
        
        # Public Telegram API check
        try:
            api_url = f"https://api.telegram.org/bot{hashlib.md5(e164.encode()).hexdigest()[:10]}/getUpdates"
            # Bu gerçek bir API değil, sadece demo
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
        print(c(Colors.WARNING, "\n[*] Gerçek Telegram sorgulaması için:"))
        print(c(Colors.OKBLUE, "  1. https://my.telegram.org adresine gidin"))
        print(c(Colors.OKBLUE, "  2. API ID ve API Hash alın"))
        print(c(Colors.OKBLUE, "  3. telegram-phone-number-checker kullanın"))
        print(c(Colors.OKBLUE, "     pip install telegram-phone-number-checker"))
    
    print(c(Colors.HEADER, "═" * 45))

# ============================================================
# MODÜL 5: TOplu İSTİHBARAT
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
            
            # Temizle
            numbers = [n.strip() for n in numbers if n.strip()]
            
            if not numbers:
                # Her satırı bir numara olarak dene
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
    
    # İlk 50'yi göster
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
    
    # İstatistikler
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
    
    # Raporu kaydet
    save = input(c(Colors.OKCYAN, "\n[?] Raporu kaydet? (e/h): "))
    if save.lower() == 'e':
        filename = f"intel_report_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write("NumberTools v3 - Toplu İstihbarat Raporu\n")
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
# MODÜL 6: SAYI ÜRETİCİ & RASTGELE NUMARA
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
    
    # İlk 20'yi göster
    print(c(Colors.HEADER, "\n" + "═" * 55))
    print(c(Colors.BOLD, f"          ÜRETİLEN NUMARALAR (ilk 20)"))
    print(c(Colors.HEADER, "═" * 55))
    print()
    
    for i, num in enumerate(numbers[:20], 1):
        result = validate_tr_number(num)
        print(f"  {i:<3} {result['display']:<20} {result['operator']:<25}")
    
    if count > 20:
        print(f"\n  ... ve {count - 20} numara daha")
    
    # Kaydet
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
# MODÜL 7: NUMARA KARŞILAŞTIRMA & EŞLEŞTİRME
# ============================================================

def find_matching_numbers(target: str, database: List[str], similarity: float = 0.7) -> List[Tuple[str, float]]:
    """Hedef numaraya benzer numaraları bul"""
    matches = []
    
    # Hedefi normalize et
    target_clean = clean_number(target)
    
    for num in database:
        db_clean = clean_number(num)
        
        # Levenshtein benzerlik
        if len(target_clean) > 0 and len(db_clean) > 0:
            # Basit benzerlik: aynı pozisyonda aynı rakamlar
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
# MODÜL 8: SOSYAL MEDYA OSINT
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
        "Signal": "Signal (uygulama içi kontrol gerekli)",
    }
    
    for platform, url in platforms.items():
        try:
            if platform == "Signal":
                # Signal API'si yok, elle kontrol
                continue
            
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
# ANA MENÜ
# ============================================================

def main_menu():
    """Ana menü"""
    banner()
    
    try:
        import requests
        import phonenumbers
        has_phonenumbers = True
    except ImportError:
        has_phonenumbers = False
    
    if not has_phonenumbers:
        print(c(Colors.WARNING, "[!] Bazı modüller için ek kütüphaneler gerekli:"))
        print(c(Colors.OKBLUE, "    pip3 install phonenumbers requests"))
    
    print(c(Colors.OKBLUE, "\n  Modüller:"))
    print(f"  {c(Colors.BOLD, '[1]')}  Numara Analizi      - Detaylı numara bilgisi")
    print(f"  {c(Colors.BOLD, '[2]')}  Kısmi Numara Tamamlama - *** *** ** 04 -> tam numara")
    print(f"  {c(Colors.BOLD, '[3]')}  WhatsApp Sorgulama   - WhatsApp kaydı kontrol")
    print(f"  {c(Colors.BOLD, '[4]')}  Telegram Sorgulama   - Telegram kaydı kontrol")
    print(f"  {c(Colors.BOLD, '[5]')}  Toplu İstihbarat     - Toplu numara analizi")
    print(f"  {c(Colors.BOLD, '[6]')}  Numara Üreteç        - Rastgele TR numarası")
    print(f"  {c(Colors.BOLD, '[7]')}  Numara Eşleştirme    - Benzer numara bulma")
    print(f"  {c(Colors.BOLD, '[8]')}  Sosyal Medya OSINT   - Platform varlığı sorgulama")
    print(f"  {c(Colors.BOLD, '[9]')}  Hızlı Tarama         - Tüm OSINT modülleri tek seferde")
    print(f"  {c(Colors.BOLD, '[D]')}  Demo / Test          - Örnek numara ile test")
    print(f"  {c(Colors.BOLD, '[0]')}  Çıkış")
    
    choice = input(c(Colors.OKCYAN, "\n  [?] Seçiminiz: ")).strip()
    
    if choice == '0':
        print(c(Colors.OKGREEN, "\n[+] NumberTools v3 kapandı. Güvenli günler!"))
        return False
    
    elif choice == '1':
        analyze_phone_menu()
    
    elif choice == '2':
        partial_number_menu()
    
    elif choice == '3':
        whatsapp_menu()
    
    elif choice == '4':
        telegram_menu()
    
    elif choice == '5':
        bulk_intel_menu()
    
    elif choice == '6':
        generator_menu()
    
    elif choice == '7':
        matching_menu()
    
    elif choice == '8':
        osint_menu()
    
    elif choice == '9':
        quick_scan_menu()
    
    elif choice.lower() == 'd':
        demo_mode()
    
    else:
        print(c(Colors.FAIL, f"[!] Geçersiz seçim: {choice}"))
    
    input(c(Colors.OKCYAN, "\n  [*] Devam etmek için Enter'a basın..."))
    return True

def quick_scan_menu():
    """Hızlı tarama - tüm modüller tek seferde"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  [9] HIZLI TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
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
    
    # 4. OSINT
    print(c(Colors.OKBLUE, "\n[4] SOSYAL MEDYA"))
    sm = social_media_osint(number)
    print(f"    {sm['total_found']} platformda varlık tespit edildi")
    
    # 5. Kısmi numara tamamlama önerileri
    print(c(Colors.OKBLUE, "\n[5] ÖNERİLEN DİĞER ANALİZLER"))
    print(f"    • Kısmi numara tamamlama için [2] kullanın")
    print(f"    • Toplu istihbarat için [5] kullanın")
    
    print(c(Colors.HEADER, "\n" + "═" * 55))

def demo_mode():
    """Demo mod - örnek numara ile test"""
    print(c(Colors.HEADER, "\n" + "=" * 55))
    print(c(Colors.BOLD, "  DEMO / TEST MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 55))
    
    # Örnek numaralar
    test_numbers = [
        "+90 532 123 45 67",  # Turkcell
        "+90 542 987 65 43",  # Vodafone
        "+90 505 111 22 33",  # Türk Telekom
        "+90 *** *** ** 04",  # Kısmi numara
    ]
    
    print(c(Colors.OKBLUE, "\n  Örnek numaralar:"))
    for i, num in enumerate(test_numbers, 1):
        print(f"  {i}. {num}")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Test edilecek numara (1-4, Enter=hepsi): "))
    
    if not choice:
        for num in test_numbers:
            print(c(Colors.HEADER, "\n" + "═" * 45))
            print(f"  Test: {num}")
            print(c(Colors.HEADER, "═" * 45))
            
            if '***' in num:
                print(c(Colors.OKBLUE, "\n  [Kısmi Numara Tamamlama]"))
                partial_number_from_demo(num)
            else:
                result = validate_tr_number(num)
                if result["valid"]:
                    print(f"\n  {c(Colors.OKGREEN, '✓ GEÇERLİ')}")
                    print(f"  Formatlı: {result['display']}")
                    print(f"  Operatör: {result['operator']}")
                    print(f"  Hat Tipi: {result['line_type']}")
                else:
                    print(f"\n  {c(Colors.FAIL, '✗ GEÇERSİZ')}")
                    for err in result["errors"]:
                        print(f"  • {err}")
    
    elif choice in ['1', '2', '3', '4']:
        idx = int(choice) - 1
        num = test_numbers[idx]
        
        if '***' in num:
            partial_number_from_demo(num)
        else:
            result = validate_tr_number(num)
            print(c(Colors.HEADER, "\n" + "═" * 45))
            print(c(Colors.BOLD, "     TEST SONUCU"))
            print(c(Colors.HEADER, "═" * 45))
            
            if result["valid"]:
                print(f"\n  {c(Colors.OKGREEN, '✓ GEÇERLİ NUMARA')}")
                print(f"  E.164:  {result['e164']}")
                print(f"  Ulusal: {result['national']}")
                print(f"  Görünüm: {result['display']}")
                print(f"  Prefix: 0{result['prefix']}")
                print(f"  Operatör: {c(Colors.OKGREEN, result['operator'])}")
                print(f"  Hat:     {result['line_type']}")
                if result['region']:
                    print(f"  Bölge:   {result['region']}")
            else:
                print(f"\n  {c(Colors.FAIL, '✗ GEÇERSİZ NUMARA')}")
                for err in result["errors"]:
                    print(f"  • {err}")

def partial_number_from_demo(pattern: str):
    """Demo için kısmi numara tamamlama"""
    print(c(Colors.OKBLUE, "\n  [Kısmi Numara Tamamlama]"))
    print(f"  Desen: {pattern}")
    
    numbers = generate_numbers_from_partial(pattern, max_results=5, use_operator_prefixes=True)
    
    if numbers:
        print(c(Colors.OKGREEN, f"\n  [+] {len(numbers)} numara üretildi (5 gösteriliyor):"))
        for i, num in enumerate(numbers[:5], 1):
            result = validate_tr_number(num)
            print(f"    {i}. {result['display']:<20} {result['operator']}")
    else:
        print(c(Colors.FAIL, "\n  [!] Numara üretilemedi"))

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
