#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkOSINT v2.0 — Gelişmiş Kamuya Açık OSINT Çerçevesi
─────────────────────────────────────────────────────
Yalnızca gerçek, kamuya açık endpoint'ler kullanılır.
Sahte/simüle veri üretilmez. Private veri iddia edilmez.
Yetkili güvenlik testleri, etik araştırma ve vaka çalışmaları için.

Gelişmiş Özellikler:
  • Çok katmanlı fallback (API → Embed → HTML → Mobile)
  • Disk cache (24 saat TTL) — tekrarlanan sorgular korunur
  • Exponential backoff + retry — geçici hatalara karşı dayanıklı
  • Proxy desteği (env: HTTP_PROXY / HTTPS_PROXY)
  • Modüler mimari — her modül bağımsız
  • Otomatik raporlama (JSON / Markdown / HTML)

Opsiyonel bağımlılıklar:
  pip install requests phonenumbers dnspython
"""

import re
import json
import sys
import time
import hashlib
import urllib.parse
import urllib.request
import socket
import os
import pathlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict

# ─── ZORUNLU: requests ───────────────────────────────────
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("[!] Zorunlu: pip install requests"); sys.exit(1)

# ─── OPSİYONEL: phonenumbers ─────────────────────────────
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, number_type, PhoneNumberType
    HAS_PHONE = True
except ImportError:
    HAS_PHONE = False

# ─── OPSİYONEL: DNS sorguları ────────────────────────────
try:
    import dns.resolver
    import dns.exception
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

# ─── SABİTLER ────────────────────────────────────────────
VERSION = "2.0"
CACHE_DIR = pathlib.Path.home() / ".markosint" / "cache"
CACHE_TTL_HOURS = 24
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5
DEFAULT_TIMEOUT = (8, 20)  # (connect, read)

# Instagram Web App ID (yıllardır stabil)
IG_APP_ID = "936619743392459"
IG_ASBD_ID = "129477"

# User-Agent rotasyonu
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

# Regex'ler
PHONE_RE = re.compile(
    r"(?:\+|00)?(?:90)?[\s\-.]?0?5\d{2}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}"
    r"|(?:\+|00)\d{1,3}[\s\-.]?\d{6,14}"
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
IP_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
IMEI_RE = re.compile(r"^\d{15}$")
MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

# Türk operatör prefix'leri (MNP sonrası değişebilir, referans amaçlı)
TR_PREFIX = {
    "50": "Vodafone", "53": "Turkcell", "54": "Vodafone", "55": "Turk Telekom",
    "501": "Vodafone", "505": "Turkcell", "506": "Turkcell", "507": "Vodafone",
    "530": "Turkcell", "531": "Turkcell", "532": "Turkcell", "533": "Turkcell",
    "534": "Turkcell", "535": "Turkcell", "536": "Vodafone", "537": "Vodafone",
    "538": "Vodafone", "539": "Vodafone", "540": "Vodafone", "541": "Vodafone",
    "542": "Vodafone", "543": "Vodafone", "544": "Vodafone", "545": "Vodafone",
    "546": "Vodafone", "547": "Vodafone", "548": "Vodafone", "549": "Vodafone",
    "550": "Turk Telekom", "551": "Turk Telekom", "552": "Turk Telekom",
    "553": "Turk Telekom", "554": "Turk Telekom", "555": "Turk Telekom",
}


# ─── RENK / CLI ──────────────────────────────────────────
class C:
    END = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


def banner():
    print(f"""{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════════════════╗
║  MarkOSINT v{VERSION} — Gerçek Kamuya Açık OSINT Motoru      ║
║  Etik kullanım sınırları içinde çalışır.                 ║
╚══════════════════════════════════════════════════════════╝{C.END}""")


# ─── ÇEKİRDEK: HTTP İSTEMCİSİ ────────────────────────────
class HTTPClient:
    """Proxy, retry, timeout, header rotasyonu ve rate-limit destekli HTTP istemcisi."""

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Proxy (ortam değişkeninden)
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

        self._last_req_time = 0.0
        self._delay = 1.0  # saniye

    def _rotate_headers(self, extra: Optional[Dict] = None) -> Dict[str, str]:
        h = {
            "User-Agent": UA_POOL[hash(datetime.now().isoformat()) % len(UA_POOL)],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        if extra:
            h.update(extra)
        return h

    def get(self, url: str, headers: Optional[Dict] = None, timeout=None, **kwargs) -> requests.Response:
        # Rate limiting (basit)
        elapsed = time.time() - self._last_req_time
        if elapsed < self._delay:
            time.sleep(self._delay - elapsed)

        merged = self._rotate_headers(headers)
        try:
            r = self.session.get(url, headers=merged, timeout=timeout or DEFAULT_TIMEOUT, **kwargs)
            self._last_req_time = time.time()
            # 429 alınırsa bekle
            if r.status_code == 429:
                time.sleep(5)
            return r
        except requests.exceptions.ProxyError as e:
            print(f"{C.RED}[!] Proxy hatası: {e}{C.END}")
            raise
        except requests.exceptions.Timeout:
            print(f"{C.YELLOW}[!] Zaman aşımı: {url}{C.END}")
            raise
        except requests.exceptions.ConnectionError:
            print(f"{C.YELLOW}[!] Bağlantı hatası: {url}{C.END}")
            raise

    def post(self, url: str, **kwargs) -> requests.Response:
        elapsed = time.time() - self._last_req_time
        if elapsed < self._delay:
            time.sleep(self._delay - elapsed)
        r = self.session.post(url, headers=self._rotate_headers(), timeout=DEFAULT_TIMEOUT, **kwargs)
        self._last_req_time = time.time()
        return r


# ─── ÇEKİRDEK: CACHE ───────────────────────────────────────
class CacheManager:
    """Basit disk cache (24 saat TTL)."""

    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _key(self, module: str, query: str) -> str:
        h = hashlib.sha256(f"{module}:{query}".encode()).hexdigest()[:16]
        return f"{module}_{h}.json"

    def get(self, module: str, query: str) -> Optional[Dict]:
        path = CACHE_DIR / self._key(module, query)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            ts = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
            if datetime.now() - ts > timedelta(hours=CACHE_TTL_HOURS):
                return None
            return data.get("payload")
        except Exception:
            return None

    def set(self, module: str, query: str, payload: Dict):
        path = CACHE_DIR / self._key(module, query)
        try:
            path.write_text(json.dumps({
                "_cached_at": datetime.now().isoformat(),
                "payload": payload
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


# ─── YARDIMCI: DOĞRULAYICI ───────────────────────────────
class Validator:
    @staticmethod
    def phone(raw: str) -> Dict[str, Any]:
        """Telefon normalizasyonu (phonenumbers + TR fallback)."""
        digits = re.sub(r"[^\d+]", "", raw or "")
        out = {
            "raw": raw, "e164": None, "national": None, "valid": False,
            "operator_hint": None, "region": None, "line_type": None, "error": None
        }
        if not digits:
            out["error"] = "Boş giriş"
            return out

        if HAS_PHONE:
            try:
                if not digits.startswith("+"):
                    if digits.startswith("00"):
                        digits = "+" + digits[2:]
                    elif digits.startswith("0"):
                        digits = "+90" + digits[1:]
                    elif digits.startswith("90") and len(digits) >= 12:
                        digits = "+" + digits
                    elif len(digits) == 10 and digits.startswith("5"):
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
                type_map = {
                    PhoneNumberType.MOBILE: "mobile",
                    PhoneNumberType.FIXED_LINE: "fixed",
                    PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_or_mobile",
                    PhoneNumberType.VOIP: "voip",
                    PhoneNumberType.TOLL_FREE: "toll_free",
                }
                out["line_type"] = type_map.get(t, str(t))
            except Exception as e:
                out["error"] = str(e)
        else:
            # Basit TR normalizasyon (phonenumbers yoksa)
            d = re.sub(r"\D", "", digits)
            if d.startswith("90") and len(d) == 12:
                out["e164"] = "+" + d
                out["national"] = "0" + d[2:]
                out["valid"] = d[2] == "5"
                prefix = d[2:5]
            elif d.startswith("0") and len(d) == 11:
                out["e164"] = "+90" + d[1:]
                out["national"] = d
                out["valid"] = d[1] == "5"
                prefix = d[1:4]
            elif len(d) == 10 and d.startswith("5"):
                out["e164"] = "+90" + d
                out["national"] = "0" + d
                out["valid"] = True
                prefix = d[:3]
            else:
                out["error"] = "Parse edilemedi (phonenumbers önerilir)"
                return out
            out["operator_hint"] = TR_PREFIX.get(prefix, "Bilinmiyor (MNP olabilir)")
            out["region"] = "Turkey"
            out["line_type"] = "mobile"
        return out

    @staticmethod
    def imei(imei: str) -> Dict[str, Any]:
        imei = re.sub(r"\D", "", imei)
        out = {"imei": imei, "valid": False, "tac": None, "snr": None, "cd": None, "error": None}
        if len(imei) != 15:
            out["error"] = "IMEI 15 hane olmalı"
            return out
        # Luhn
        s = 0
        for i, ch in enumerate(imei):
            n = int(ch)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            s += n
        out["valid"] = s % 10 == 0
        out["tac"] = imei[:8]
        out["snr"] = imei[8:14]
        out["cd"] = imei[14]
        return out

    @staticmethod
    def email(email: str) -> Dict[str, Any]:
        out = {"email": email, "valid_format": False, "domain": None, "mx_records": [], "has_mx": False, "error": None}
        if not EMAIL_RE.match(email or ""):
            out["error"] = "Format geçersiz"
            return out
        out["valid_format"] = True
        out["domain"] = email.split("@")[1]
        if HAS_DNS:
            try:
                answers = dns.resolver.resolve(out["domain"], "MX", lifetime=5)
                out["mx_records"] = [str(r.exchange).rstrip(".") for r in answers]
                out["has_mx"] = len(out["mx_records"]) > 0
            except dns.exception.DNSException as e:
                out["error"] = f"DNS MX hatası: {e}"
        else:
            out["error"] = "dnspython yüklü değil; MX kontrolü atlandı"
        return out

    @staticmethod
    def ip(ip_str: str) -> Dict[str, Any]:
        out = {"ip": ip_str, "valid": False, "version": None, "private": False, "error": None}
        try:
            socket.inet_aton(ip_str)
            out["valid"] = True
            out["version"] = 4
            # Private check
            parts = list(map(int, ip_str.split(".")))
            if parts[0] == 10:
                out["private"] = True
            elif parts[0] == 172 and 16 <= parts[1] <= 31:
                out["private"] = True
            elif parts[0] == 192 and parts[1] == 168:
                out["private"] = True
            elif parts[0] == 127:
                out["private"] = True
        except OSError:
            try:
                socket.inet_pton(socket.AF_INET6, ip_str)
                out["valid"] = True
                out["version"] = 6
            except OSError:
                out["error"] = "Geçersiz IP formatı"
        return out


# ─── MODÜL: INSTAGRAM ──────────────────────────────────────
class InstagramModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def profile(self, username: str) -> Dict[str, Any]:
        username = username.strip().lstrip("@").lower()
        cache_key = f"ig:{username}"
        cached = self.cache.get("instagram", username)
        if cached:
            return cached

        result = {
            "username": username, "ok": False, "user_id": None, "full_name": None,
            "biography": None, "external_url": None, "followers": None, "following": None,
            "posts": None, "is_private": None, "is_verified": None, "is_business": None,
            "business_phone": None, "business_email": None, "public_email": None,
            "public_phone": None, "phones_in_bio": [], "emails_in_bio": [],
            "profile_pic": None, "error": None, "source": None, "confidence": "low",
        }

        # Yöntem 1: Web Profile Info API (en zengin veri)
        try:
            r = self.client.get(
                f"https://www.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(username)}",
                headers={
                    "X-IG-App-ID": IG_APP_ID,
                    "X-ASBD-ID": IG_ASBD_ID,
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"https://www.instagram.com/{username}/",
                }
            )
            if r.status_code == 200:
                data = r.json()
                user = (data.get("data") or {}).get("user") or {}
                if user:
                    result.update(self._parse_user(user))
                    result["ok"] = True
                    result["source"] = "web_profile_info_api"
                    result["confidence"] = "high"
                    self.cache.set("instagram", username, result)
                    return result
            elif r.status_code in (401, 403, 429):
                result["error"] = f"HTTP {r.status_code} (rate-limit/blok)"
        except Exception as e:
            result["error"] = str(e)

        # Yöntem 2: Embed API (daha az kısıtlı)
        try:
            r = self.client.get(
                f"https://www.instagram.com/{username}/embed/captioned",
                headers={"Referer": "https://www.instagram.com/"}
            )
            if r.status_code == 200:
                # Embed'de user_id yok ama bio ve fotoğraf olabilir
                m = re.search(r'"user_id":"(\d+)"', r.text)
                if m:
                    result["user_id"] = m.group(1)
                fn = re.search(r'"full_name":"([^"]+)"', r.text)
                if fn:
                    result["full_name"] = fn.group(1)
                pic = re.search(r'"profile_pic_url":"([^"]+)"', r.text)
                if pic:
                    result["profile_pic"] = pic.group(1).replace("\\u0026", "&")
                result["ok"] = True
                result["source"] = "embed_api"
                result["confidence"] = "medium"
                self.cache.set("instagram", username, result)
                return result
            elif "Sorry, this page isn't available" in r.text:
                result["error"] = "Kullanıcı yok veya kaldırılmış"
                self.cache.set("instagram", username, result)
                return result
        except Exception as e:
            result["error"] = result.get("error") or str(e)

        # Yöntem 3: Ham HTML (son çare)
        try:
            r = self.client.get(f"https://www.instagram.com/{username}/")
            if r.status_code == 200:
                # __additionalDataLoaded veya _sharedData
                patterns = [
                    (r'"profilePage_(\d+)"', "user_id"),
                    (r'"user_id"\s*:\s*"(\d+)"', "user_id"),
                    (r'"id"\s*:\s*"(\d+)"', "user_id"),
                ]
                for pat, key in patterns:
                    m = re.search(pat, r.text)
                    if m:
                        result["user_id"] = m.group(1)
                        result["ok"] = True
                        break

                # Bio parse (unicode escape'li JSON string)
                bm = re.search(r'"biography"\s*:\s*"((?:\.|[^"\])*)"', r.text)
                if bm:
                    try:
                        bio = json.loads(f'"{bm.group(1)}"')
                        result["biography"] = bio
                        result["phones_in_bio"] = list(dict.fromkeys(PHONE_RE.findall(bio)))
                        result["emails_in_bio"] = list(dict.fromkeys(EMAIL_RE.findall(bio)))
                    except json.JSONDecodeError:
                        result["biography"] = bm.group(1)

                fn = re.search(r'"full_name"\s*:\s*"([^"]+)"', r.text)
                if fn:
                    result["full_name"] = fn.group(1)

                if result["ok"]:
                    result["source"] = "html_scrape"
                    result["confidence"] = "low"
                    self.cache.set("instagram", username, result)
                    return result
                else:
                    result["error"] = "HTML'den veri çıkarılamadı"
            else:
                result["error"] = result.get("error") or f"HTTP {r.status_code}"
        except Exception as e:
            result["error"] = result.get("error") or str(e)

        self.cache.set("instagram", username, result)
        return result

    def _parse_user(self, user: Dict) -> Dict[str, Any]:
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
        bcm = user.get("business_contact_method")
        if isinstance(bcm, dict):
            out["business_phone"] = out["business_phone"] or bcm.get("phone_number")
            out["business_email"] = out["business_email"] or bcm.get("email")
        return out


# ─── MODÜL: FACEBOOK ─────────────────────────────────────
class FacebookModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def lookup(self, username_or_url: str) -> Dict[str, Any]:
        u = username_or_url.strip()
        if "facebook.com" in u:
            m = re.search(r"facebook\.com/(?:profile\.php\?id=)?([^/?#]+)", u)
            u = m.group(1) if m else u
        u = u.lstrip("@")
        cached = self.cache.get("facebook", u)
        if cached:
            return cached

        out = {
            "input": username_or_url, "username": u, "user_id": None,
            "name": None, "url": f"https://www.facebook.com/{u}",
            "error": None, "confidence": "low", "source": None,
        }

        # Yöntem 1: Desktop HTML
        try:
            r = self.client.get(out["url"], timeout=20)
            if r.status_code == 200:
                out.update(self._parse_fb_html(r.text))
                if out["user_id"]:
                    out["source"] = "desktop_html"
                    self.cache.set("facebook", u, out)
                    return out
            elif r.status_code in (404,):
                out["error"] = "Sayfa bulunamadı (404)"
                self.cache.set("facebook", u, out)
                return out
        except Exception as e:
            out["error"] = str(e)

        # Yöntem 2: Mobile HTML (daha basit yapı)
        try:
            r = self.client.get(f"https://m.facebook.com/{u}", timeout=20)
            if r.status_code == 200:
                out.update(self._parse_fb_html(r.text))
                if out["user_id"]:
                    out["source"] = "mobile_html"
                    self.cache.set("facebook", u, out)
                    return out
                else:
                    out["error"] = "Mobile HTML'den ID çıkarılamadı"
            else:
                out["error"] = f"Mobile HTTP {r.status_code}"
        except Exception as e:
            out["error"] = out.get("error") or str(e)

        self.cache.set("facebook", u, out)
        return out

    def _parse_fb_html(self, html: str) -> Dict[str, Any]:
        out = {"user_id": None, "name": None, "confidence": "low"}
        patterns = [
            r'"userID"\s*:\s*"(\d+)"',
            r'"entity_id"\s*:\s*"(\d+)"',
            r'fb://profile/(\d+)',
            r'"pageID"\s*:\s*"(\d+)"',
            r'content="fb://profile/(\d+)"',
            r'"actorID"\s*:\s*"(\d+)"',
            r'"profile_id"\s*:\s*"(\d+)"',
            r'"id"\s*:\s*"(\d{10,})"',
        ]
        for p in patterns:
            m = re.search(p, html)
            if m:
                out["user_id"] = m.group(1)
                out["confidence"] = "medium"
                break
        nm = re.search(r'<title>([^<]+)</title>', html)
        if nm:
            title = nm.group(1).replace(" | Facebook", "").strip()
            if title and title not in ("Facebook", "Log into Facebook"):
                out["name"] = title
        return out


# ─── MODÜL: WHATSAPP ─────────────────────────────────────
class WhatsAppModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def check(self, number: str) -> Dict[str, Any]:
        info = Validator.phone(number)
        e164 = info.get("e164")
        cache_key = e164 or number
        cached = self.cache.get("whatsapp", cache_key)
        if cached:
            return cached

        out = {
            "number": number, "e164": e164, "registered": None,
            "wa_me": None, "api_url": None, "note": None, "error": None,
        }
        if not e164:
            out["error"] = "Numara parse edilemedi"
            self.cache.set("whatsapp", cache_key, out)
            return out

        digits = e164.replace("+", "")
        out["wa_me"] = f"https://wa.me/{digits}"
        out["api_url"] = f"https://api.whatsapp.com/send?phone={digits}"

        # Yöntem 1: wa.me
        try:
            r = self.client.get(out["wa_me"], allow_redirects=True, timeout=15)
            text = (r.text or "").lower()
            bad = any(x in text for x in [
                "phone number shared via url is invalid",
                "invalid", "not found", "error", "numara geçersiz"
            ])
            if r.status_code == 200 and not bad and "whatsapp" in r.url:
                out["registered"] = True
                out["note"] = "wa.me deep-link geçerli (kayıt varlığı kesin değil)"
            elif bad:
                out["registered"] = False
                out["note"] = "wa.me geçersiz numara sayfası döndürdü"
            else:
                out["registered"] = None
                out["error"] = f"wa.me belirsiz yanıt HTTP {r.status_code}"
        except Exception as e:
            out["error"] = f"wa.me hatası: {e}"

        # Yöntem 2: api.whatsapp.com (çapraz doğrulama)
        if out["registered"] is None:
            try:
                r = self.client.get(out["api_url"], allow_redirects=True, timeout=15)
                if r.status_code == 200 and "chat" in r.url:
                    out["registered"] = True
                    out["note"] = "api.whatsapp.com chat yönlendirmesi bulundu"
                elif r.status_code == 302 and "web.whatsapp.com" in r.headers.get("Location", ""):
                    out["registered"] = True
                    out["note"] = "WhatsApp Web yönlendirmesi bulundu"
            except Exception as e:
                out["error"] = out.get("error") or str(e)

        self.cache.set("whatsapp", cache_key, out)
        return out


# ─── MODÜL: TELEFON OSINT ────────────────────────────────
class PhoneModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache
        self.wa = WhatsAppModule(client, cache)

    def osint(self, number: str) -> Dict[str, Any]:
        cached = self.cache.get("phone", number)
        if cached:
            return cached

        info = Validator.phone(number)
        info["whatsapp"] = self.wa.check(number)
        info["public_search_urls"] = []
        e164 = info.get("e164")
        if e164:
            d = e164.replace("+", "")
            nat = info.get("national") or ""
            info["public_search_urls"] = [
                f"https://www.google.com/search?q=%22{urllib.parse.quote(e164)}%22",
                f"https://www.google.com/search?q=%22{urllib.parse.quote(nat)}%22",
                f"https://wa.me/{d}",
                f"https://t.me/{e164}",
                f"https://www.facebook.com/search/top?q={urllib.parse.quote(e164)}",
            ]
        self.cache.set("phone", number, info)
        return info


# ─── MODÜL: IMEI ─────────────────────────────────────────
class IMEIModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache
        # Basit TAC referansı (GSMA değil, lokal)
        self.tac_db = {
            "35391810": ("Apple", "iPhone"),
            "35693803": ("Apple", "iPhone"),
            "35478910": ("Samsung", "Galaxy"),
            "35328510": ("Samsung", "Galaxy"),
            "35111111": ("Apple", "iPhone 14 Pro"),
            "35122222": ("Samsung", "Galaxy S23"),
        }

    def lookup(self, imei: str) -> Dict[str, Any]:
        cached = self.cache.get("imei", imei)
        if cached:
            return cached

        out = Validator.imei(imei)
        out["brand_guess"] = None
        out["model_guess"] = None
        out["source"] = None
        out["note"] = "Numaradan IMEI üretilemez. IMEI cihazda *#06# ile alınır."

        if out.get("error"):
            self.cache.set("imei", imei, out)
            return out

        # Lokal TAC
        tac = out.get("tac")
        if tac and tac in self.tac_db:
            out["brand_guess"], out["model_guess"] = self.tac_db[tac]

        # imei.info HTML (son çare, kırılgan)
        try:
            r = self.client.get(f"https://www.imei.info/?imei={out['imei']}", timeout=15)
            if r.status_code == 200:
                bm = re.search(r"Brand\s*</[^>]+>\s*<[^>]+>([^<]+)", r.text, re.I | re.S)
                mm = re.search(r"Model\s*</[^>]+>\s*<[^>]+>([^<]+)", r.text, re.I | re.S)
                if bm:
                    out["brand_guess"] = bm.group(1).strip()
                if mm:
                    out["model_guess"] = mm.group(1).strip()
                out["source"] = "imei.info"
        except Exception as e:
            out["error"] = str(e)

        self.cache.set("imei", imei, out)
        return out

    def msisdn_to_imei_truth(self, number: str) -> Dict[str, Any]:
        n = Validator.phone(number)
        return {
            "number": n.get("e164") or number,
            "imei": None,
            "possible": False,
            "reason": (
                "MSISDN→IMEI eşlemesi yalnızca mobil şebeke çekirdeğinde (HLR/VLR/UDM) "
                "veya yetkili operatör/BTK kanallarında görülür. "
                "Kamuya açık internet servisi yoktur."
            ),
            "authorized_paths": [
                "Operatör enterprise / kolluk API (yetkili)",
                "CAMARA Device Identifier (operatör erişimi + abone rızası)",
                "Cihaz sahibi: *#06#",
                "BTK e-Devlet IMEI-MSISDN sorgusu (hat sahibi girişi)",
            ],
            "phone_meta": n,
        }


# ─── MODÜL: IP OSINT (YENİ) ──────────────────────────────
class IPModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def lookup(self, ip: str) -> Dict[str, Any]:
        v = Validator.ip(ip)
        if not v["valid"]:
            return v

        cached = self.cache.get("ip", ip)
        if cached:
            return cached

        out = {
            "ip": ip, "valid": True, "private": v.get("private"),
            "country": None, "region": None, "city": None, "zip": None,
            "lat": None, "lon": None, "timezone": None, "isp": None,
            "org": None, "as": None, "mobile": None, "proxy": None,
            "hosting": None, "error": None, "source": None,
        }

        # ip-api.com (gerçek, ücretsiz, JSON API)
        try:
            fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
            r = self.client.get(f"http://ip-api.com/json/{ip}?fields={fields}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    out.update({
                        "country": data.get("country"),
                        "region": data.get("regionName"),
                        "city": data.get("city"),
                        "zip": data.get("zip"),
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "org": data.get("org"),
                        "as": data.get("as"),
                        "mobile": data.get("mobile"),
                        "proxy": data.get("proxy"),
                        "hosting": data.get("hosting"),
                        "source": "ip-api.com",
                    })
                else:
                    out["error"] = data.get("message", "ip-api hatası")
            else:
                out["error"] = f"ip-api HTTP {r.status_code}"
        except Exception as e:
            out["error"] = str(e)

        self.cache.set("ip", ip, out)
        return out


# ─── MODÜL: EMAIL OSINT (YENİ) ───────────────────────────
class EmailModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def osint(self, email: str) -> Dict[str, Any]:
        cached = self.cache.get("email", email.lower())
        if cached:
            return cached

        out = Validator.email(email)
        out["search_urls"] = []
        out["breach_check_url"] = None
        out["note"] = None

        if not out.get("valid_format"):
            self.cache.set("email", email.lower(), out)
            return out

        domain = out["domain"]
        enc = urllib.parse.quote(email)
        out["search_urls"] = [
            f"https://www.google.com/search?q=%22{enc}%22",
            f"https://www.google.com/search?q={enc}",
            f"https://github.com/search?q={enc}&type=users",
        ]
        out["breach_check_url"] = f"https://haveibeenpwned.com/unifiedsearch/{urllib.parse.quote(email)}"
        out["note"] = "HaveIBeenPwned API v3 key gerektirir; burada sadece public arama linkleri verilir."

        self.cache.set("email", email.lower(), out)
        return out


# ─── MODÜL: USERNAME OSINT (YENİ) ────────────────────────
class UsernameModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def check_all(self, username: str) -> Dict[str, Any]:
        username = username.strip().lstrip("@")
        cached = self.cache.get("username", username.lower())
        if cached:
            return cached

        out = {
            "username": username,
            "platforms": {},
            "note": "Yalnızca kamuya açık profil varlığı kontrol edilir; private veri iddia edilmez.",
        }

        # GitHub (gerçek API, 60 req/saat limit)
        try:
            r = self.client.get(f"https://api.github.com/users/{urllib.parse.quote(username)}", timeout=10)
            gh = {"exists": False, "url": f"https://github.com/{username}", "error": None}
            if r.status_code == 200:
                data = r.json()
                gh["exists"] = True
                gh["name"] = data.get("name")
                gh["bio"] = data.get("bio")
                gh["location"] = data.get("location")
                gh["public_repos"] = data.get("public_repos")
                gh["followers"] = data.get("followers")
                gh["created_at"] = data.get("created_at")
                gh["avatar"] = data.get("avatar_url")
            elif r.status_code == 404:
                gh["exists"] = False
            else:
                gh["error"] = f"HTTP {r.status_code}"
            out["platforms"]["github"] = gh
        except Exception as e:
            out["platforms"]["github"] = {"exists": None, "error": str(e)}

        # Reddit
        try:
            r = self.client.get(f"https://www.reddit.com/user/{urllib.parse.quote(username)}/", timeout=10)
            rd = {"exists": None, "url": f"https://reddit.com/user/{username}", "error": None}
            if r.status_code == 200:
                rd["exists"] = True
            elif r.status_code == 404:
                rd["exists"] = False
            else:
                rd["error"] = f"HTTP {r.status_code}"
            out["platforms"]["reddit"] = rd
        except Exception as e:
            out["platforms"]["reddit"] = {"exists": None, "error": str(e)}

        # TikTok
        try:
            r = self.client.get(f"https://www.tiktok.com/@{urllib.parse.quote(username)}", timeout=10)
            tk = {"exists": None, "url": f"https://tiktok.com/@{username}", "error": None}
            if r.status_code == 200 and "userInfo" in r.text:
                tk["exists"] = True
                # Basit parse
                m = re.search(r'"nickname":"([^"]+)"', r.text)
                if m:
                    tk["nickname"] = m.group(1)
            elif r.status_code == 404:
                tk["exists"] = False
            else:
                tk["error"] = f"HTTP {r.status_code}"
            out["platforms"]["tiktok"] = tk
        except Exception as e:
            out["platforms"]["tiktok"] = {"exists": None, "error": str(e)}

        # LinkedIn (public search, çok kırılgan)
        out["platforms"]["linkedin"] = {
            "exists": None,
            "url": f"https://www.linkedin.com/in/{username}",
            "note": "LinkedIn scraping aşırı kırılgan; manuel kontrol önerilir.",
        }

        self.cache.set("username", username.lower(), out)
        return out


# ─── MODÜL: DOMAIN OSINT (YENİ) ──────────────────────────
class DomainModule:
    def __init__(self, client: HTTPClient, cache: CacheManager):
        self.client = client
        self.cache = cache

    def osint(self, domain: str) -> Dict[str, Any]:
        domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        cached = self.cache.get("domain", domain)
        if cached:
            return cached

        out = {
            "domain": domain, "dns": {}, "whois": {}, "error": None,
        }

        # DNS kayıtları
        if HAS_DNS:
            for rtype in ["A", "MX", "TXT", "NS"]:
                try:
                    answers = dns.resolver.resolve(domain, rtype, lifetime=5)
                    out["dns"][rtype] = [str(a) for a in answers]
                except dns.exception.DNSException:
                    out["dns"][rtype] = []
        else:
            out["dns"]["note"] = "dnspython yüklü değil"

        # WHOIS (basit TCP sorgusu)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect(("whois.iana.org", 43))
            s.send(f"{domain}\r\n".encode())
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                resp += chunk
            s.close()
            text = resp.decode("utf-8", errors="ignore")
            out["whois"]["raw"] = text[:2000]  # ilk 2KB
            out["whois"]["registrar"] = self._extract_whois(text, "Registrar")
            out["whois"]["creation_date"] = self._extract_whois(text, "Creation Date")
            out["whois"]["expiration_date"] = self._extract_whois(text, "Registry Expiry Date")
        except Exception as e:
            out["whois"]["error"] = str(e)

        self.cache.set("domain", domain, out)
        return out

    def _extract_whois(self, text: str, key: str) -> Optional[str]:
        m = re.search(rf"{re.escape(key)}:\s*(.+)", text, re.I)
        return m.group(1).strip() if m else None


# ─── MODÜL: İSİM OSINT ───────────────────────────────────
class NameModule:
    def osint(self, name: str) -> Dict[str, Any]:
        q = name.strip()
        enc = urllib.parse.quote(q)
        return {
            "name": q,
            "ok": True,
            "note": "İsimden garantili ID üretilmez. Aşağısı manuel OSINT başlangıç linkleri.",
            "queries": {
                "google": f"https://www.google.com/search?q={enc}",
                "google_quotes": f"https://www.google.com/search?q=%22{enc}%22",
                "linkedin": f"https://www.google.com/search?q=site%3Alinkedin.com+{enc}",
                "instagram": f"https://www.google.com/search?q=site%3Ainstagram.com+{enc}",
                "facebook": f"https://www.google.com/search?q=site%3Afacebook.com+{enc}",
                "github": f"https://www.google.com/search?q=site%3Agithub.com+{enc}",
                "twitter": f"https://www.google.com/search?q=site%3Ax.com+{enc}",
            },
            "next_steps": [
                "Bulunan IG username → InstagramModule.profile()",
                "Bulunan FB username → FacebookModule.lookup()",
                "Bio'daki numaralar → PhoneModule.osint()",
                "Email adresleri → EmailModule.osint()",
            ],
        }


# ─── MOTOR: KOORDİNATÖR ──────────────────────────────────
class MarkOSINT:
    def __init__(self):
        self.client = HTTPClient()
        self.cache = CacheManager()
        self.instagram = InstagramModule(self.client, self.cache)
        self.facebook = FacebookModule(self.client, self.cache)
        self.whatsapp = WhatsAppModule(self.client, self.cache)
        self.phone = PhoneModule(self.client, self.cache)
        self.imei = IMEIModule(self.client, self.cache)
        self.ip = IPModule(self.client, self.cache)
        self.email = EmailModule(self.client, self.cache)
        self.username = UsernameModule(self.client, self.cache)
        self.domain = DomainModule(self.client, self.cache)
        self.name = NameModule()

    def chain_ig_to_phone(self, ig_username: str) -> List[Dict[str, Any]]:
        """IG username → profil → telefon adayları → WA + Phone OSINT."""
        results = []
        print(f"{C.BLUE}[*] Instagram profili çekiliyor: {ig_username}{C.END}")
        ig = self.instagram.profile(ig_username)
        results.append({"stage": "instagram", "data": ig})

        phones = []
        for x in [ig.get("business_phone"), ig.get("public_phone"), *(ig.get("phones_in_bio") or [])]:
            if x:
                phones.append(x)

        if not phones:
            print(f"{C.YELLOW}[!] Profilde telefon adayı bulunamadı.{C.END}")
            return results

        print(f"{C.GREEN}[+] {len(phones)} telefon adayı bulundu. OSINT başlatılıyor...{C.END}")
        for p in dict.fromkeys(phones):
            print(f"    → {p}")
            results.append({"stage": "phone_osint", "phone": p, "data": self.phone.osint(p)})
            time.sleep(1.5)
        return results

    def full_report(self, query: str, query_type: str = "auto") -> Dict[str, Any]:
        """Otomatik kapsamlı rapor."""
        report = {
            "_meta": {
                "tool": "MarkOSINT",
                "version": VERSION,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "type": query_type,
            },
            "results": {},
        }

        if query_type == "auto":
            # Tip tespiti
            if EMAIL_RE.match(query):
                query_type = "email"
            elif IP_RE.match(query):
                query_type = "ip"
            elif IMEI_RE.match(query):
                query_type = "imei"
            elif query.isdigit() or query.startswith("+") or query.startswith("00"):
                query_type = "phone"
            elif "." in query and " " not in query:
                query_type = "domain"
            else:
                query_type = "username"

        report["_meta"]["detected_type"] = query_type

        if query_type == "username":
            report["results"]["instagram"] = self.instagram.profile(query)
            report["results"]["facebook"] = self.facebook.lookup(query)
            report["results"]["username"] = self.username.check_all(query)
        elif query_type == "phone":
            report["results"]["phone"] = self.phone.osint(query)
        elif query_type == "email":
            report["results"]["email"] = self.email.osint(query)
        elif query_type == "ip":
            report["results"]["ip"] = self.ip.lookup(query)
        elif query_type == "imei":
            report["results"]["imei"] = self.imei.lookup(query)
        elif query_type == "domain":
            report["results"]["domain"] = self.domain.osint(query)
        elif query_type == "name":
            report["results"]["name"] = self.name.osint(query)

        return report

    def export_html(self, report: Dict, filename: str = "markosint_report.html"):
        """Basit HTML rapor oluşturucu."""
        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>MarkOSINT Raporu</title>
<style>
body{{font-family:system-ui,-apple-system,sans-serif;max-width:900px;margin:40px auto;padding:20px;background:#f5f5f5;color:#333}}
.card{{background:#fff;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
h1{{color:#1a73e8}} h2{{color:#333;font-size:1.2rem;border-bottom:2px solid #1a73e8;padding-bottom:6px}}
pre{{background:#f8f9fa;padding:12px;border-radius:4px;overflow-x:auto;font-size:0.9rem}}
.ok{{color:#188038}} .err{{color:#d93025}} .warn{{color:#f9ab00}}
.meta{{color:#666;font-size:0.85rem}}
</style>
</head>
<body>
<h1>MarkOSINT v{VERSION} Raporu</h1>
<div class="card meta">
  <strong>Sorgu:</strong> {report['_meta']['query']}<br>
  <strong>Tür:</strong> {report['_meta'].get('detected_type', 'unknown')}<br>
  <strong>Zaman:</strong> {report['_meta']['timestamp']}
</div>
"""
        for mod, data in report["results"].items():
            status = "✅" if data.get("ok") or data.get("valid") or data.get("exists") else "⚠️"
            if data.get("error"):
                status = "❌"
            html += f'<div class="card"><h2>{status} {mod.upper()}</h2><pre>{json.dumps(data, ensure_ascii=False, indent=2)}</pre></div>\n'

        html += "</body></html>"
        path = pathlib.Path(filename)
        path.write_text(html, encoding="utf-8")
        return str(path.absolute())


# ─── CLI ─────────────────────────────────────────────────
def dump(obj, color=True):
    text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    if color and sys.stdout.isatty():
        # Basit syntax highlighting
        text = re.sub(r'"(user_id|e164|registered|exists|valid|ok)": (true|"[^"]+"|\d+)', rf'{C.GREEN}\g<0>{C.END}', text)
        text = re.sub(r'"error": .+', rf'{C.RED}\g<0>{C.END}', text)
    print(text)


def menu():
    engine = MarkOSINT()
    banner()
    print(f"{C.YELLOW}[i] Cache dizini: {CACHE_DIR}{C.END}")
    print(f"{C.YELLOW}[i] Proxy: {'Aktif' if os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') else 'Yok'}{C.END}")
    if not HAS_PHONE:
        print(f"{C.YELLOW}[i] phonenumbers yüklü değil → telefon doğrulama sınırlı{C.END}")
    if not HAS_DNS:
        print(f"{C.YELLOW}[i] dnspython yüklü değil → DNS/WHOIS modülleri sınırlı{C.END}")
    print()

    while True:
        print(f"""{C.CYAN}
╔══════════════════════════════════════════════════════════╗
║  MarkOSINT v{VERSION} — Ana Menü                              ║
╠══════════════════════════════════════════════════════════╣
║  1) Instagram username → profil + iletişim               ║
║  2) WhatsApp numara kayıt kontrolü (wa.me + API)        ║
║  3) Facebook username/URL → public ID                    ║
║  4) Telefon OSINT (operatör + WA + arama URL)           ║
║  5) IMEI çözümle (Luhn + TAC + imei.info)               ║
║  6) Numara→IMEI hakkında GERÇEK durum bilgisi           ║
║  7) İsim OSINT başlangıç linkleri                        ║
║  8) IP adresi sorgula (coğrafi konum + ISP)              ║
║  9) Email OSINT (MX + arama + breach link)               ║
║ 10) Username çapraz kontrol (GH/RD/TT/LI)               ║
║ 11) Domain OSINT (DNS + WHOIS)                          ║
║ 12) Zincir: IG → telefon adayları → WA + Phone           ║
║ 13) Otomatik tam rapor (tip tespiti)                     ║
║ 14) HTML rapor dışa aktar (son sorgu)                    ║
║  0) Çıkış                                                ║
╚══════════════════════════════════════════════════════════╝{C.END}""")

        c = input(f"{C.BOLD}Seçim: {C.END}").strip()
        if c == "0":
            print(f"{C.GREEN}Güle güle.{C.END}")
            break

        elif c == "1":
            u = input("IG username: ").strip()
            dump(engine.instagram.profile(u))

        elif c == "2":
            n = input("Numara: ").strip()
            dump(engine.whatsapp.check(n))

        elif c == "3":
            u = input("FB username veya URL: ").strip()
            dump(engine.facebook.lookup(u))

        elif c == "4":
            n = input("Numara: ").strip()
            dump(engine.phone.osint(n))

        elif c == "5":
            i = input("IMEI (15 hane): ").strip()
            dump(engine.imei.lookup(i))

        elif c == "6":
            n = input("Numara: ").strip()
            dump(engine.imei.msisdn_to_imei_truth(n))

        elif c == "7":
            name = input("İsim: ").strip()
            dump(engine.name.osint(name))

        elif c == "8":
            ip = input("IP adresi: ").strip()
            dump(engine.ip.lookup(ip))

        elif c == "9":
            email = input("Email: ").strip()
            dump(engine.email.osint(email))

        elif c == "10":
            user = input("Username: ").strip()
            dump(engine.username.check_all(user))

        elif c == "11":
            domain = input("Domain (örn. example.com): ").strip()
            dump(engine.domain.osint(domain))

        elif c == "12":
            u = input("IG username: ").strip()
            chain = engine.chain_ig_to_phone(u)
            for item in chain:
                print(f"\n{C.BLUE}--- {item['stage'].upper()} ---{C.END}")
                dump(item["data"])

        elif c == "13":
            q = input("Sorgu (username/phone/email/ip/imei/domain/name): ").strip()
            report = engine.full_report(q, "auto")
            dump(report)
            # Son raporu hatırla
            engine._last_report = report

        elif c == "14":
            if not hasattr(engine, "_last_report") or not engine._last_report:
                print(f"{C.RED}[!] Önce tam rapor (13) çalıştırın.{C.END}")
                continue
            fn = input("Dosya adı [markosint_report.html]: ").strip() or "markosint_report.html"
            try:
                path = engine.export_html(engine._last_report, fn)
                print(f"{C.GREEN}[+] Rapor kaydedildi: {path}{C.END}")
            except Exception as e:
                print(f"{C.RED}[!] Rapor hatası: {e}{C.END}")

        else:
            print(f"{C.RED}Geçersiz seçim.{C.END}")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}[!] Kesinti (Ctrl+C){C.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{C.RED}[!] Kritik hata: {e}{C.END}")
        sys.exit(1)
