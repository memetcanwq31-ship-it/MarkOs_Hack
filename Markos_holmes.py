#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkOsint OSINT Toolbox - Safe Edition (Green theme)
- 8 araçlı interaktif menü, Terminal/Kali/Termux uyumlu (ANSI renkleri).
- Renk teması: Yeşil.
- YAPIMCI: @markospm19_
- KULLANIM: Sadece yasal/izinli hedefler için.
"""
from __future__ import annotations
import os
import sys
import re
import json
import time
import random
import socket
import gzip
import html as H
import http.client
import ssl
import concurrent.futures as cf
from typing import List, Tuple, Dict
from datetime import datetime
from urllib.parse import urlencode, urlparse, urljoin, unquote

# third-party
try:
    import requests
except Exception:
    print("Bu araç için 'requests' kütüphanesi gerekli. Kurulum: pip install requests")
    sys.exit(1)

# Optional EXIF reader for geotag extraction from images
HAS_EXIFREAD = True
try:
    import exifread
except Exception:
    HAS_EXIFREAD = False

# ---------------- Colors & Banner (Green theme) ----------------
GREEN = "\033[92m"
CYAN  = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BANNER = rf"""
{GREEN}===========================================================================
  __  __             _    ___  ____ ___ _   _ _____ 
 |  \/  | __ _ _ __ | |  / _ \/ ___|_ _| \ | |_   _|
 | |\/| |/ _` | '_ \| | | | | | \___ \| ||  \| | | |  
 | |  | | (_| | | | | | | |_| |___) | || |\  | | |  
 |_|  |_|\__,_|_| |_|_|  \___/|____/___|_| \_| |_|  

 [+] MarkOs İşletim Sistemine ait bir tool'dur.
 [ * ] MarkOsint OSINT Toolbox (Safe Edition)
 [ ! ] UYARI: Bu araç YETKİLİ kişiler tarafından ve yasal/etik amaçlarla kullanılmalıdır.
       Tüm sorumluluk kullanıcıya aittir.
       YAPIMCI: @markospm19_
===========================================================================
{RESET}
"""

USER_AGENTS = [
    "MarkOsint-Tool/1.0 (+https://example.local/)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
]
UA_REDDIT = "linux:markosint-tool:v1 (by /u/you)"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# ---------------- Helpers ----------------
def now_ts() -> str:
    return datetime.utcnow().isoformat() + "Z"

def clear_screen():
    # Termux/Kali/most terminals support ANSI; ensure Windows compatibility
    if os.name == "nt":
        os.system("")  # enable ANSI on some Windows consoles
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    clear_screen()
    print(BANNER)
    print(f"{GREEN}Versiyon:{RESET} MarkOsint Safe | {GREEN}Zaman:{RESET} {now_ts()}\n")

def save_report(prefix: str, data: dict) -> str:
    fname = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(REPORT_DIR, fname)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return path

def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s

def http_get_raw(url, method="GET", headers=None, body=None, timeout=10, max_redir=4):
    for _ in range(max_redir + 1):
        p = urlparse(url)
        scheme, host = p.scheme, p.hostname
        path = p.path or "/"
        if p.query:
            path += "?" + p.query
        port = p.port or (443 if scheme == "https" else 80)
        hdrs = {"User-Agent": random.choice(USER_AGENTS), "Accept": "*/*", "Accept-Encoding":"gzip, identity"}
        if headers:
            hdrs.update(headers)
        try:
            if scheme == "https":
                conn = http.client.HTTPSConnection(host, port, timeout=timeout, context=ssl.create_default_context())
            else:
                conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request(method, path, body=body, headers=hdrs)
            resp = conn.getresponse()
            data = resp.read()
            status = resp.status
            rh = {k.lower(): v for k, v in resp.getheaders()}
            conn.close()
        except Exception as e:
            return 0, {}, str(e).encode("utf-8", "ignore")
        if status in (301,302,303,307,308) and rh.get("location"):
            url = urljoin(url, rh["location"])
            if status == 303:
                method = "GET"; body = None
            continue
        if rh.get("content-encoding","").lower() == "gzip" and data[:2] == b"\x1f\x8b":
            try:
                data = gzip.decompress(data)
            except Exception:
                pass
        return status, rh, data
    return 0, {}, b"redirect_limit"

def ddg_search(query: str, n: int = 6):
    body = urlencode({"q": query, "kl": "us-en"})
    st, _, data = http_get_raw("https://html.duckduckgo.com/html/", method="POST", body=body,
                               headers={"Content-Type": "application/x-www-form-urlencoded", "Referer":"https://duckduckgo.com/"})
    if st != 200:
        return []
    h = data.decode("utf-8", "ignore")
    if "anomaly" in h.lower() or "unusual" in h.lower():
        return [{"blocked": True}]
    out = []
    for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
        link = m.group(1).replace("&amp;", "&")
        title = H.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if "uddg=" in link:
            for kv in urlparse(link).query.split("&"):
                k, _, v = kv.partition("=")
                if k == "uddg":
                    link = unquote(v)
        out.append({"title": title, "url": link})
        if len(out) >= n:
            break
    return out

# ---------------- Tool 1: Kullanıcı Aratma (Username Hunter) ----------------
SITES_BASIC = [
    ("GitHub", "https://github.com/{u}"), ("GitLab", "https://gitlab.com/{u}"),
    ("Reddit", "https://www.reddit.com/user/{u}"), ("Telegram", "https://t.me/{u}"),
    ("Instagram", "https://www.instagram.com/{u}/"), ("X/Twitter", "https://x.com/{u}"),
    ("Twitch", "https://www.twitch.tv/{u}"), ("Steam", "https://steamcommunity.com/id/{u}"),
]

def check_site(session, name, template, username, timeout=8):
    url = template.format(u=username)
    try:
        resp = session.head(url, allow_redirects=True, timeout=timeout)
        st = resp.status_code
        if st == 200:
            return {"site": name, "url": url, "found": True, "status": st, "note": "HEAD 200"}
        if st in (301,302,303) and resp.headers.get("Location"):
            return {"site": name, "url": url, "found": True, "status": st, "note": "redirect"}
        if st in (404,410):
            return {"site": name, "url": url, "found": False, "status": st, "note": "not found"}
        resp = session.get(url, allow_redirects=True, timeout=timeout)
        st = resp.status_code
        if st == 200:
            body = resp.text.lower()[:1500]
            if any(x in body for x in ("not found","this page isn't available","user not found","page not found")):
                return {"site": name, "url": url, "found": False, "status": st, "note": "page indicates not found"}
            return {"site": name, "url": url, "found": True, "status": st, "note": "GET 200"}
        return {"site": name, "url": url, "found": False, "status": st, "note": "other"}
    except requests.RequestException as e:
        return {"site": name, "url": url, "found": False, "status": None, "note": f"error: {e}"}

def tool_username_hunter(usernames: List[str], sites: List[Tuple[str,str]] = SITES_BASIC, threads: int = 12, delay: float = 0.02):
    session = build_session()
    results = {u: [] for u in usernames}
    tasks = [(u, name, tpl) for u in usernames for (name, tpl) in sites]
    def worker(task):
        u, name, tpl = task
        time.sleep(random.uniform(0, delay))
        session.headers["User-Agent"] = random.choice(USER_AGENTS)
        return u, check_site(session, name, tpl, u)
    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(worker, t) for t in tasks]
        for f in cf.as_completed(futures):
            try:
                u, res = f.result()
            except Exception:
                continue
            results[u].append(res)
    return results

# ---------------- Tool 2: Geotag Konum Bulma ----------------
def dms_to_deg(dms, ref):
    def to_float(x):
        return float(x.num) / float(x.den)
    deg = to_float(dms[0]) + to_float(dms[1]) / 60.0 + to_float(dms[2]) / 3600.0
    if ref in ("S", "W"):
        deg = -deg
    return deg

def extract_gps_from_image(path: str):
    if not HAS_EXIFREAD:
        return {"error": "exifread not installed (pip install exifread)"}
    try:
        with open(path, "rb") as fh:
            tags = exifread.process_file(fh, details=False)
        gps_lat = tags.get("GPS GPSLatitude")
        gps_lat_ref = tags.get("GPS GPSLatitudeRef")
        gps_lon = tags.get("GPS GPSLongitude")
        gps_lon_ref = tags.get("GPS GPSLongitudeRef")
        if gps_lat and gps_lon and gps_lat_ref and gps_lon_ref:
            lat = dms_to_deg(gps_lat.values, str(gps_lat_ref))
            lon = dms_to_deg(gps_lon.values, str(gps_lon_ref))
            return {"path": path, "latitude": lat, "longitude": lon}
        else:
            return {"path": path, "error": "no_gps"}
    except Exception as e:
        return {"path": path, "error": str(e)}

def tool_geotag_from_images(dirpath: str):
    if not os.path.isdir(dirpath):
        return {"error": "not_directory"}
    files = [os.path.join(dirpath, f) for f in os.listdir(dirpath) if f.lower().endswith((".jpg",".jpeg",".tiff"))]
    out = []
    for f in files:
        r = extract_gps_from_image(f)
        out.append(r)
    return {"scanned": len(files), "results": out, "ts": now_ts()}

def tool_geotag_from_json(jsonpath: str):
    if not os.path.exists(jsonpath):
        return {"error": "not_found"}
    try:
        j = json.load(open(jsonpath, "r", encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}
    out = []
    if isinstance(j, dict):
        items = j.get("data") or j.get("media") or j.get("items") or []
    else:
        items = j
    for it in items:
        loc = it.get("location") or it.get("place") or {}
        lat = loc.get("lat") or loc.get("latitude") or loc.get("lng")
        lon = loc.get("lon") or loc.get("longitude")
        if lat and lon:
            out.append({"id": it.get("id") or it.get("shortcode"), "lat": lat, "lon": lon, "place": loc.get("name")})
    return {"found": len(out), "locations": out, "ts": now_ts()}

# ---------------- Tool 3: Telefon Sorgu ----------------
def normalize_phone(phone: str) -> str:
    s = re.sub(r"[^\d+]", "", phone)
    if s.startswith("00"):
        s = "+" + s[2:]
    if s.startswith("0") and not s.startswith("00") and not s.startswith("+"):
        s = "+90" + s[1:]
    return s

def tool_phone_search(phone: str):
    norm = normalize_phone(phone)
    q = f'"{norm}"'
    hits = ddg_search(q, n=8)
    return {"phone": phone, "normalized": norm, "ddg_hits": hits, "ts": now_ts()}

# ---------------- Tool 4: Email aday + MX lookup ----------------
def mx_lookup(domain: str):
    url = "https://cloudflare-dns.com/dns-query?" + urlencode({"name": domain, "type": "MX"})
    st, rh, raw = http_get_raw(url, timeout=10)
    if st != 200:
        return []
    try:
        j = json.loads(raw.decode("utf-8", "ignore"))
        return [a.get("data") for a in (j or {}).get("Answer", []) if a.get("type") == 15]
    except Exception:
        return []

def tool_email_candidates(name: str, domains: List[str] = None):
    tokens = name.split()
    first, last = (tokens[0], tokens[-1]) if len(tokens) >= 2 else (tokens[0], "")
    def fold_tr(s):
        m = {"ç":"c","ğ":"g","ı":"i","ö":"o","ş":"s","ü":"u"}
        return "".join(m.get(c, c) for c in s).lower()
    f, l = fold_tr(first), fold_tr(last)
    locals_ = []
    for x in [f, l, f + l, f + "." + l, f + "_" + l, f[0] + l]:
        x = x.strip("._-")
        if x and x not in locals_:
            locals_.append(x)
    if not domains:
        domains = ["gmail.com","hotmail.com","outlook.com","yahoo.com","icloud.com"]
    candidates = [f"{loc}@{d}" for loc in locals_ for d in domains]
    mxs = {d: mx_lookup(d) for d in set(domains)}
    return {"name": name, "candidates": candidates, "mx": mxs, "ts": now_ts()}

# ---------------- Tool 5: IP Sorgu ----------------
def tool_ip_lookup(ip: str):
    if ip.startswith(("10.", "192.168.", "127.", "172.")):
        return {"error":"private_ip"}
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,org,as,query", timeout=8)
        j = r.json()
    except Exception as e:
        return {"error": str(e)}
    rdap = None
    st, rh, raw = http_get_raw(f"https://rdap.org/ip/{ip}", timeout=10)
    if st == 200:
        try:
            rdap = json.loads(raw.decode("utf-8", "ignore"))
        except Exception as ex:
            rdap = {"error": str(ex)}
    else:
        rdap = {"error": f"http_{st}"}
    return {"ip_api": j, "rdap": rdap, "ts": now_ts()}

# ---------------- Tool 6: GitHub & Reddit detay (public) ----------------
GITHUB_HDRS = {"Accept": "application/vnd.github+json"}
if os.environ.get("GH_TOKEN"):
    GITHUB_HDRS["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]

def tool_github_user(login: str):
    try:
        r = requests.get(f"https://api.github.com/users/{login}", headers=GITHUB_HDRS, timeout=8)
        if r.status_code != 200:
            return {"error": f"http_{r.status_code}"}
        j = r.json()
        keys = ("login","name","email","blog","location","bio","company","twitter_username","public_repos","followers","following","created_at")
        return {k: j.get(k) for k in keys if j.get(k) is not None}
    except Exception as e:
        return {"error": str(e)}

def tool_reddit_about(username: str):
    try:
        r = requests.get(f"https://www.reddit.com/user/{username}/about.json", headers={"User-Agent": UA_REDDIT}, timeout=8)
        if r.status_code != 200:
            return {"error": f"http_{r.status_code}"}
        j = r.json().get("data", {})
        if not j:
            return {"error":"not_found_or_blocked"}
        return {"created": datetime.utcfromtimestamp(j.get("created_utc", 0)).strftime("%Y-%m-%d"), "link_karma": j.get("link_karma"), "comment_karma": j.get("comment_karma")}
    except Exception as e:
        return {"error": str(e)}

# ---------------- Tool 7: DuckDuckGo live search ----------------
def tool_ddg(query: str, n: int = 10):
    return {"query": query, "results": ddg_search(query, n), "ts": now_ts()}

# ---------------- Tool 8: Reports management ----------------
def tool_list_reports():
    files = sorted(os.listdir(REPORT_DIR))
    return {"reports": files, "count": len(files)}

def tool_view_report(filename: str):
    path = os.path.join(REPORT_DIR, filename)
    if not os.path.exists(path):
        return {"error": "not_found"}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

# ---------------- Interactive Menu ----------------
def menu_print():
    print_banner()
    print(f"{GREEN}TOOLS MENU (8){RESET}")
    print(f" {GREEN}[1]{RESET} Kullanıcı Aratma (Username Hunter)")
    print(f" {GREEN}[2]{RESET} Geotag Konum Bulma (yerel fotoğraflardan veya JSON'dan)")
    print(f" {GREEN}[3]{RESET} Telefon Sorgu (normalize + web izleri)")
    print(f" {GREEN}[4]{RESET} Email Aday Üretimi + MX Kontrol")
    print(f" {GREEN}[5]{RESET} IP Sorgu (ip-api + RDAP)")
    print(f" {GREEN}[6]{RESET} GitHub & Reddit (public info)")
    print(f" {GREEN}[7]{RESET} Arama Motoru (DuckDuckGo canlı)")
    print(f" {GREEN}[8]{RESET} Raporlar (listele / görüntüle)")
    print(f" {GREEN}[0]{RESET} Çıkış")
    print()

def interactive():
    while True:
        menu_print()
        choice = input(f"{GREEN}[?]{RESET} Seçiminiz: ").strip()
        if choice == "0":
            print(f"{GREEN}Güvenli çıkış yapılıyor. MarkOsint — iyi çalışmalar.{RESET}")
            break
        elif choice == "1":
            u = input("Kullanıcı adı (veya virgülle birden fazla): ").strip()
            if not u:
                input("Enter ile devam...")
                continue
            users = [x.strip() for x in u.split(",") if x.strip()]
            consent = input("Bu taramayı yalnızca izinli hedef(ler) için yapacağınızı onaylıyor musunuz? (evet/hayır): ").strip().lower()
            if consent not in ("evet","e","yes","y"):
                print("Onay yok — iptal edildi."); input("Enter ile devam..."); continue
            res = tool_username_hunter(users, SITES_BASIC)
            path = save_report("username_hunt", {"meta":{"ts": now_ts(), "users": users}, "results": res})
            print(f"{GREEN}Rapor kaydedildi:{RESET} {path}")
            input("Enter ile devam...")
        elif choice == "2":
            print("Geotag aracı: 1) Klasördeki fotoğraflardan EXIF çek  2) Hazır JSON medya dosyasından konum oku")
            sel = input("Seçim (1 veya 2): ").strip()
            if sel == "1":
                if not HAS_EXIFREAD:
                    print("exifread yüklü değil. Yüklemek için: pip install exifread"); input("Enter ile devam..."); continue
                d = input("Fotoğraf klasörü yolu: ").strip()
                consent = input("Bu fotoğrafların size ait olduğunu / izinli olduğunu onaylıyor musunuz? (evet/hayır): ").strip().lower()
                if consent not in ("evet","e","yes","y"): print("Onay yok — iptal edildi."); input("Enter ile devam..."); continue
                out = tool_geotag_from_images(d)
                path = save_report("geotag_images", out)
                print(f"{GREEN}Sonuç kaydedildi:{RESET} {path}"); input("Enter ile devam...")
            elif sel == "2":
                j = input("Medya JSON dosya yolu: ").strip()
                consent = input("JSON içeriğinin size ait / izinli olduğunu onaylıyor musunuz? (evet/hayır): ").strip().lower()
                if consent not in ("evet","e","yes","y"): print("Onay yok — iptal edildi."); input("Enter ile devam..."); continue
                out = tool_geotag_from_json(j)
                path = save_report("geotag_json", out)
                print(f"{GREEN}Sonuç kaydedildi:{RESET} {path}"); input("Enter ile devam...")
            else:
                print("Geçersiz seçim."); input("Enter ile devam...")
        elif choice == "3":
            tel = input("Telefon numarası: ").strip()
            consent = input("Bu numarayı sorgulama yetkiniz olduğunu onaylıyor musunuz? (evet/hayır): ").strip().lower()
            if consent not in ("evet","e","yes","y"): print("Onay yok — iptal edildi."); input("Enter ile devam..."); continue
            out = tool_phone_search(tel)
            path = save_report("phone_search", out)
            print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
        elif choice == "4":
            name = input("İsim (First Last) veya direkt email: ").strip()
            if not name: input("Enter ile devam..."); continue
            if "@" in name:
                dom = name.split("@")[-1]; mxs = mx_lookup(dom)
                out = {"email": name, "mx": mxs, "ts": now_ts()}; path = save_report("email_direct", out)
                print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
            else:
                doms = input("Domainler (virgülle) veya ENTER için varsayılan: ").strip()
                domains = [d.strip() for d in doms.split(",") if d.strip()] if doms else None
                out = tool_email_candidates(name, domains)
                path = save_report("email_candidates", out)
                print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
        elif choice == "5":
            ip = input("IP adresi: ").strip()
            if not ip: input("Enter ile devam..."); continue
            out = tool_ip_lookup(ip)
            path = save_report("ip_lookup", out)
            print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
        elif choice == "6":
            sub = input("GitHub login (boşsa atla): ").strip()
            reddit = input("Reddit username (boşsa atla): ").strip()
            data = {}
            if sub: data["github"] = tool_github_user(sub)
            if reddit: data["reddit"] = tool_reddit_about(reddit)
            path = save_report("gh_rd", {"meta":{"ts": now_ts()}, "data": data})
            print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
        elif choice == "7":
            q = input("Arama sorgusu (DuckDuckGo): ").strip()
            if not q: input("Enter ile devam..."); continue
            out = tool_ddg(q, n=12)
            path = save_report("ddg_search", out)
            print(f"{GREEN}Kaydedildi:{RESET} {path}"); input("Enter ile devam...")
        elif choice == "8":
            r = tool_list_reports()
            print(json.dumps(r, ensure_ascii=False, indent=2))
            sel = input("Görüntülemek için dosya adı girin (ENTER ile iptal): ").strip()
            if sel:
                data = tool_view_report(sel)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            input("Enter ile devam...")
        else:
            print("Geçersiz seçim."); input("Enter ile devam...")

# ---------------- CLI entry ----------------
def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="MarkOsint Safe OSINT Toolbox (Green theme)")
    p.add_argument("--interactive", action="store_true", help="Start interactive menu")
    return p.parse_args()

def main():
    args = parse_args()
    if args.interactive or sys.stdin.isatty():
        interactive()
    else:
        print_banner()
        print("No action. Use --interactive")
        sys.exit(0)

if __name__ == "__main__":
    main()
