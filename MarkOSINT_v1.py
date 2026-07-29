#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkOSINT v1.0 - Gerçek kamuya açık OSINT araçları
Yetkili güvenlik testleri / pentest için.
Sahte / simüle endpoint YOK.
"""

import re
import json
import sys
import time
import hashlib
import urllib.parse
from datetime import datetime

try:
    import requests
except ImportError:
    print("[!] pip install requests"); sys.exit(1)

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, number_type, PhoneNumberType
    HAS_PHONE = True
except ImportError:
    HAS_PHONE = False
    print("[!] opsiyonel: pip install phonenumbers")

# ─── ortak ───────────────────────────────────────────────
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"})

PHONE_RE = re.compile(
    r"(?:\+|00)?(?:90)?[\s\-.]?0?5\d{2}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}"
    r"|(?:\+|00)\d{1,3}[\s\-.]?\d{6,14}"
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def norm_tr_phone(raw: str) -> dict:
    digits = re.sub(r"[^\d+]", "", raw or "")
    out = {"raw": raw, "e164": None, "national": None, "valid": False, "operator": None, "region": None}
    if not HAS_PHONE:
        # basit TR normalizasyon
        d = re.sub(r"\D", "", digits)
        if d.startswith("90") and len(d) == 12:
            out["e164"] = "+" + d
            out["national"] = "0" + d[2:]
            out["valid"] = d[2] == "5"
        elif d.startswith("0") and len(d) == 11:
            out["e164"] = "+90" + d[1:]
            out["national"] = d
            out["valid"] = d[1] == "5"
        elif len(d) == 10 and d.startswith("5"):
            out["e164"] = "+90" + d
            out["national"] = "0" + d
            out["valid"] = True
        return out
    try:
        if not digits.startswith("+"):
            if digits.startswith("00"):
                digits = "+" + digits[2:]
            elif digits.startswith("0"):
                digits = "+90" + digits[1:]
            elif digits.startswith("90") and len(digits) >= 12:
                digits = "+" + digits
            elif len(digits) == 10:
                digits = "+90" + digits
            else:
                digits = "+" + digits
        p = phonenumbers.parse(digits, None)
        out["valid"] = phonenumbers.is_valid_number(p)
        out["e164"] = phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
        out["national"] = phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.NATIONAL)
        out["region"] = geocoder.description_for_number(p, "tr") or geocoder.description_for_number(p, "en")
        out["operator"] = carrier.name_for_number(p, "tr") or carrier.name_for_number(p, "en")
        out["tz"] = list(timezone.time_zones_for_number(p))
        t = number_type(p)
        types = {
            PhoneNumberType.MOBILE: "mobile",
            PhoneNumberType.FIXED_LINE: "fixed",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_or_mobile",
            PhoneNumberType.VOIP: "voip",
            PhoneNumberType.TOLL_FREE: "toll_free",
        }
        out["line_type"] = types.get(t, str(t))
    except Exception as e:
        out["error"] = str(e)
    return out


# ─── 1) Instagram: GERÇEK internal web API ────────────────
# Endpoint yıllardır bilinen public web client ID ile çalışır.
# Rate-limit / IP ban olabilir. Enrollment/session cookie GEREKMEZ (public).

IG_APP_ID = "936619743392459"

def ig_profile(username: str) -> dict:
    username = username.strip().lstrip("@")
    result = {
        "username": username,
        "ok": False,
        "user_id": None,
        "full_name": None,
        "biography": None,
        "external_url": None,
        "followers": None,
        "following": None,
        "posts": None,
        "is_private": None,
        "is_verified": None,
        "is_business": None,
        "business_phone": None,
        "business_email": None,
        "public_email": None,
        "public_phone": None,
        "phones_in_bio": [],
        "emails_in_bio": [],
        "profile_pic": None,
        "error": None,
        "source": None,
    }

    headers = {
        "User-Agent": UA,
        "X-IG-App-ID": IG_APP_ID,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
        "Accept": "*/*",
    }

    # Yöntem A: i.instagram.com web_profile_info (en güvenilir)
    urls = [
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(username)}",
        f"https://www.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(username)}",
    ]
    for url in urls:
        try:
            r = S.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                data = r.json()
                user = (data.get("data") or {}).get("user") or {}
                if not user:
                    continue
                result.update(_parse_ig_user(user))
                result["ok"] = True
                result["source"] = url.split("/")[2]
                return result
            if r.status_code in (401, 403, 429):
                result["error"] = f"HTTP {r.status_code} (rate-limit/ban). VPN veya bekleyin."
            else:
                result["error"] = f"HTTP {r.status_code}"
        except Exception as e:
            result["error"] = str(e)

    # Yöntem B: HTML gömülü JSON (fallback)
    try:
        r = S.get(f"https://www.instagram.com/{username}/", headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200:
            # "user_id":"123" veya "profilePage_123"
            m = re.search(r'"profilePage_(\d+)"', r.text)
            if not m:
                m = re.search(r'"user_id"\s*:\s*"(\d+)"', r.text)
            if m:
                result["user_id"] = m.group(1)
                result["ok"] = True
                result["source"] = "html"
            # bio
            bm = re.search(r'"biography"\s*:\s*"((?:\\.|[^"\\])*)"', r.text)
            if bm:
                bio = bytes(bm.group(1), "utf-8").decode("unicode_escape")
                result["biography"] = bio
                result["phones_in_bio"] = list(dict.fromkeys(PHONE_RE.findall(bio)))
                result["emails_in_bio"] = list(dict.fromkeys(EMAIL_RE.findall(bio)))
            if not result["ok"] and "Sorry, this page isn't available" in r.text:
                result["error"] = "kullanıcı yok veya kaldırılmış"
            elif result["ok"]:
                result["error"] = None
    except Exception as e:
        result["error"] = result.get("error") or str(e)

    return result


def _parse_ig_user(user: dict) -> dict:
    bio = user.get("biography") or ""
    out = {
        "user_id": str(user.get("id") or user.get("pk") or ""),
        "full_name": user.get("full_name"),
        "biography": bio,
        "external_url": user.get("external_url"),
        "followers": (user.get("edge_followed_by") or {}).get("count"),
        "following": (user.get("edge_follow") or {}).get("count"),
        "posts": (user.get("edge_owner_to_timeline_media") or {}).get("count"),
        "is_private": user.get("is_private"),
        "is_verified": user.get("is_verified"),
        "is_business": user.get("is_business_account") or user.get("is_business"),
        "business_phone": user.get("business_phone_number"),
        "business_email": user.get("business_email"),
        "public_email": user.get("public_email"),
        "public_phone": user.get("public_phone_number") or user.get("contact_phone_number"),
        "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
        "phones_in_bio": list(dict.fromkeys(PHONE_RE.findall(bio))),
        "emails_in_bio": list(dict.fromkeys(EMAIL_RE.findall(bio))),
    }
    # işletme iletişim
    bcm = user.get("business_contact_method")
    if isinstance(bcm, dict):
        out["business_phone"] = out["business_phone"] or bcm.get("phone_number")
        out["business_email"] = out["business_email"] or bcm.get("email")
    return out


# ─── 2) WhatsApp: GERÇEK wa.me kontrolü ───────────────────
# Profil foto / about / private lists için whatsapp-web.js + QR oturumu gerekir.
# Burada yalan uydurmuyoruz: sadece kayıt varlığı + deep-link.

def wa_check(number: str) -> dict:
    info = norm_tr_phone(number)
    e164 = info.get("e164")
    out = {
        "number": number,
        "e164": e164,
        "registered": None,
        "wa_me": None,
        "note": "Profil/about için whatsapp-web.js oturumu gerekir; bunu simüle etmiyoruz.",
        "error": None,
    }
    if not e164:
        out["error"] = "numara parse edilemedi"
        return out
    digits = e164.replace("+", "")
    out["wa_me"] = f"https://wa.me/{digits}"
    try:
        r = S.get(out["wa_me"], timeout=15, allow_redirects=True)
        # WhatsApp genelde 200 + chat deep link döner; “geçersiz” sayfada net sinyaller değişkendir.
        # Aktif yöntem: sayfa + final URL
        text = (r.text or "").lower()
        bad = any(x in text for x in ["phone number shared via url is invalid", "error", "not found"])
        if r.status_code == 200 and not bad and ("wa.me" in r.url or "whatsapp" in r.url or "send" in r.url):
            out["registered"] = True
        elif bad:
            out["registered"] = False
        else:
            out["registered"] = None
            out["error"] = f"belirsiz yanıt HTTP {r.status_code}"
    except Exception as e:
        out["error"] = str(e)
    return out


# ─── 3) Facebook: public username → id (graph) ───────────
# Private data yok. "Graph ID" bazen açık profilde bulunur.

def fb_public_lookup(username_or_url: str) -> dict:
    u = username_or_url.strip()
    if "facebook.com" in u:
        m = re.search(r"facebook\.com/([^/?#]+)", u)
        u = m.group(1) if m else u
    u = u.lstrip("@")
    out = {"input": username_or_url, "username": u, "user_id": None, "name": None, "url": f"https://www.facebook.com/{u}", "error": None}
    try:
        r = S.get(out["url"], timeout=20, allow_redirects=True)
        if r.status_code != 200:
            out["error"] = f"HTTP {r.status_code}"
            return out
        # gerçek HTML içindeki entity_id / userID patternleri
        patterns = [
            r'"userID"\s*:\s*"(\d+)"',
            r'"entity_id"\s*:\s*"(\d+)"',
            r'fb://profile/(\d+)',
            r'"pageID"\s*:\s*"(\d+)"',
            r'content="fb://profile/(\d+)"',
        ]
        for p in patterns:
            m = re.search(p, r.text)
            if m:
                out["user_id"] = m.group(1)
                break
        nm = re.search(r'<title>([^<]+)</title>', r.text)
        if nm:
            out["name"] = nm.group(1).replace(" | Facebook", "").strip()
        if not out["user_id"]:
            out["error"] = "public id HTML'den çıkmadı (login wall / gizli profil olabilir)"
    except Exception as e:
        out["error"] = str(e)
    return out


# ─── 4) Numara OSINT (gerçek) ────────────────────────────
def phone_osint(number: str) -> dict:
    info = norm_tr_phone(number)
    info["whatsapp"] = wa_check(number)
    # Truecaller vb. resmi API anahtarı olmadan toplu scrape yasak/kırılgan;
    # burada ek yalan API yok.
    info["public_search_urls"] = []
    e164 = info.get("e164")
    if e164:
        d = e164.replace("+", "")
        info["public_search_urls"] = [
            f"https://www.google.com/search?q=%22{urllib.parse.quote(e164)}%22",
            f"https://www.google.com/search?q=%22{urllib.parse.quote(info.get('national') or '')}%22",
            f"https://wa.me/{d}",
            f"https://t.me/{e164}",
        ]
    return info


# ─── 5) IMEI: SADECE verilen IMEI'den devam ─────────────
# Numara → IMEI kamuya açık çalışmaz. Bunu iddia eden kod yalandır.

def luhn_imei(imei: str) -> bool:
    if not re.fullmatch(r"\d{15}", imei):
        return False
    s = 0
    for i, ch in enumerate(imei):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        s += n
    return s % 10 == 0


# Bilinen küçük TAC örnekleri (gerçek GSMA DB değildir; lokal referans)
# Tam model için imei.info UI veya GSMA ticari erişim gerekir.
TAC_LOCAL = {
    "35391810": ("Apple", "iPhone"),
    "35693803": ("Apple", "iPhone"),
    "35478910": ("Samsung", "Galaxy"),
    "35328510": ("Samsung", "Galaxy"),
}


def imei_lookup(imei: str) -> dict:
    imei = re.sub(r"\D", "", imei)
    out = {
        "imei": imei,
        "valid_luhn": False,
        "tac": None,
        "snr": None,
        "cd": None,
        "brand_guess": None,
        "model_guess": None,
        "error": None,
        "note": "Numaradan IMEI üretilemez. IMEI cihazda *#06# ile alınır / sahibinden / operatör kaydından gelir.",
    }
    if len(imei) != 15:
        out["error"] = "IMEI 15 hane olmalı"
        return out
    out["valid_luhn"] = luhn_imei(imei)
    out["tac"] = imei[:8]
    out["snr"] = imei[8:14]
    out["cd"] = imei[14]
    if out["tac"] in TAC_LOCAL:
        out["brand_guess"], out["model_guess"] = TAC_LOCAL[out["tac"]]
    # IMEI.info HTML (açık sayfa, API değil) — kırılabilir
    try:
        r = S.get(f"https://www.imei.info/?imei={imei}", timeout=15)
        if r.status_code == 200:
            # kaba parse
            bm = re.search(r"Brand\s*</.+?>\s*<.+?>([^<]+)", r.text, re.I | re.S)
            mm = re.search(r"Model\s*</.+?>\s*<.+?>([^<]+)", r.text, re.I | re.S)
            if bm:
                out["brand_guess"] = bm.group(1).strip()
            if mm:
                out["model_guess"] = mm.group(1).strip()
            out["source"] = "imei.info"
    except Exception as e:
        out["error"] = str(e)
    return out


def phone_to_imei_truth(number: str) -> dict:
    """Gerçeği yaz: bu işlem public OSP ile yapılamaz."""
    n = norm_tr_phone(number)
    return {
        "number": n.get("e164") or number,
        "imei": None,
        "possible": False,
        "reason": (
            "MSISDN→IMEI eşlemesi yalnızca mobil şebeke çekirdeğinde (HLR/VLR/UDM) "
            "ve regüle operatör API'lerinde (ör. CAMARA Device Identifier) veya "
            "BTK/e-Devlet (hat sahibi oturumu) ile görülür. "
            "İnternetten rastgele numara yazıp IMEI çeken gerçek bir public servis yoktur."
        ),
        "authorized_paths": [
            "Operatör enterprise / law-enforcement API (yetkili)",
            "CAMARA Device Identifier (operatör ürün erişimi + abone rızası)",
            "Cihaz sahibi: *#06#",
            "Yetkili BTK e-Devlet IMEI-MSISDN (hat sahibi girişi)",
        ],
        "phone_meta": n,
    }


# ─── 6) İsim OSINT (gerçek: arama URL + basit Google-dfd yok)
# Google otomatik scrape anti-bot yüzünden kırılır; yalan SERP parser yok.
def name_osint(name: str) -> dict:
    q = name.strip()
    enc = urllib.parse.quote(q)
    return {
        "name": q,
        "ok": True,
        "note": "İsimden garantili Meta/WA ID üretilmez. Aşağısı manuel/OSINT başlangıç linkleri.",
        "queries": {
            "google": f"https://www.google.com/search?q={enc}",
            "google_quotes": f"https://www.google.com/search?q=%22{enc}%22",
            "linkedin": f"https://www.google.com/search?q=site%3Alinkedin.com+{enc}",
            "instagram": f"https://www.google.com/search?q=site%3Ainstagram.com+{enc}",
            "facebook": f"https://www.google.com/search?q=site%3Afacebook.com+{enc}",
            "github": f"https://www.google.com/search?q=site%3Agithub.com+{enc}",
        },
        "next_steps": [
            "Bulunan IG username'i ig_profile() ile tara",
            "Bulunan FB username'i fb_public_lookup() ile tara",
            "Bio/CTAs'taki numaraları phone_osint() ile doğrula",
        ],
    }


# ─── CLI ─────────────────────────────────────────────────
def dump(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def menu():
    while True:
        print("""
========== MarkOSINT v1.0 (GERÇEK KAYNAKLAR) ==========
 1) Instagram username → user_id + public profil
 2) WhatsApp numara kayıt kontrolü (wa.me)
 3) Facebook username/url → public id (HTML)
 4) Telefon OSINT (operator + WA + arama URL)
 5) IMEI çözümle (elle verilen IMEI)
 6) Numara→IMEI hakkında GERÇEK durum
 7) İsim OSINT linkleri
 8) Hızlı zincir: IG username → telefon adayları → WA
 0) Çıkış
=======================================================
""")
        c = input("Seçim: ").strip()
        if c == "0":
            break
        elif c == "1":
            u = input("IG username: ").strip()
            dump(ig_profile(u))
        elif c == "2":
            n = input("Numara: ").strip()
            dump(wa_check(n))
        elif c == "3":
            u = input("FB username veya URL: ").strip()
            dump(fb_public_lookup(u))
        elif c == "4":
            n = input("Numara: ").strip()
            dump(phone_osint(n))
        elif c == "5":
            i = input("IMEI (15 hane): ").strip()
            dump(imei_lookup(i))
        elif c == "6":
            n = input("Numara: ").strip()
            dump(phone_to_imei_truth(n))
        elif c == "7":
            name = input("İsim: ").strip()
            dump(name_osint(name))
        elif c == "8":
            u = input("IG username: ").strip()
            ig = ig_profile(u)
            dump(ig)
            phones = []
            for x in [ig.get("business_phone"), ig.get("public_phone"), *(ig.get("phones_in_bio") or [])]:
                if x:
                    phones.append(x)
            print("\n--- Telefon adayları + WA ---")
            for p in dict.fromkeys(phones):
                dump(phone_osint(p))
                time.sleep(1)
        else:
            print("Geçersiz")


if __name__ == "__main__":
    menu()
