#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bu Tools Markos İşletim sistemine aittir yetkili kişiler kullanabilir
"""
OSINT MEGA v8 — MARKOS İŞLETİM SİSTEMİ OSINT (17 GERÇEK ARAÇ + VERİTABANI)
===========================================================================
Tüm araçlar GERÇEKTİR: her sonuç canlı API/HTTP yanıtıdır, sahte veri yoktur.
Instagram ID/konum için kendi hesabınızla oturum açılır (menü 17 veya otomatik).
Tarama geçmişi SQLite veritabanına kaydedilir: ~/.markos_osint.db
Yalnızca yetkilendirilmiş hedeflerde kullanın.
"""
import concurrent.futures as cf
import datetime as dt
import getpass
import gzip
import hashlib
import hmac
import html as H
import http.client
import json
import os
import random
import re
import socket
import sqlite3
import ssl
import sys
import time
import uuid
from urllib.parse import urlencode, urlparse, urljoin, unquote, quote

# ---------------------------------------------------------------- renkler
GREEN = "\033[92m"
BLUE  = "\033[94m"
RESET = "\033[0m"

def info(msg): print(BLUE + "[*] " + msg + RESET)
def ok(msg):   print(GREEN + "[+] " + msg + RESET)
def hata(msg): print(BLUE + "[-] " + msg + RESET)
def line(ch="=", n=62): print(GREEN + ch * n + RESET)

# ---------------------------------------------------------------- veritabanı (SQLite)
DB_PATH = os.path.join(os.path.expanduser("~"), ".markos_osint.db")

def db_init():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS taramalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arac TEXT NOT NULL,
        hedef TEXT NOT NULL,
        sonuc TEXT,
        zaman TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS hedefler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tip TEXT, deger TEXT UNIQUE,
        ilk_gorulme TEXT, son_gorulme TEXT)""")
    con.commit()
    con.close()

def db_kaydet(arac, hedef, sonuc):
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try:
        con = sqlite3.connect(DB_PATH, timeout=10)
        con.execute("INSERT INTO taramalar (arac, hedef, sonuc, zaman) VALUES (?,?,?,?)",
                    (arac, hedef, json.dumps(sonuc, ensure_ascii=False, default=str), now))
        con.execute("""INSERT INTO hedefler (tip, deger, ilk_gorulme, son_gorulme)
                       VALUES (?,?,?,?)
                       ON CONFLICT(deger) DO UPDATE SET son_gorulme=excluded.son_gorulme""",
                    (arac, hedef, now, now))
        con.commit()
        con.close()
        return True
    except Exception as e:
        hata(f"Veritabanı yazma hatası: {e}")
        return False

def db_son_kayitlar(n=20):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT id, arac, hedef, zaman FROM taramalar ORDER BY id DESC LIMIT ?",
                       (n,)).fetchall()
    con.close()
    return rows

def db_hedef_listesi():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT tip, deger, ilk_gorulme, son_gorulme FROM hedefler "
                       "ORDER BY son_gorulme DESC LIMIT 100").fetchall()
    con.close()
    return rows

def db_ozet():
    con = sqlite3.connect(DB_PATH)
    arac = con.execute("SELECT arac, COUNT(*) FROM taramalar GROUP BY arac ORDER BY COUNT(*) DESC").fetchall()
    top = con.execute("SELECT hedef, COUNT(*) FROM taramalar GROUP BY hedef "
                      "ORDER BY COUNT(*) DESC LIMIT 5").fetchall()
    con.close()
    return arac, top

def db_temizle():
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM taramalar")
    con.execute("DELETE FROM hedefler")
    con.commit()
    con.close()

# ---------------------------------------------------------------- sabitler
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
]
UA_REDDIT = "linux:osint-mega:v8 (gerçek osint aracı)"
IG_UA = ("Instagram 222.0.0.13.114 Android (30/11; 440dpi; 1080x2400; "
         "OnePlus; KB2000; OnePlus8T; qcom; tr_TR; 497616884)")
WEB_APP_ID = "936619743392459"
MOBILE_APP_ID = "124024574287414"
# GERÇEK imza anahtarı — Instagram 222.0.0.13.114 (dilame/instagram-private-api'den doğrulanmış)
IG_SIG_KEY = "9193488027538fd3450b83b7d05286d4ca9599a0f7eeed90d8c85925698a05dc"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".markos_ig_session.json")

GH_HDRS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
if os.environ.get("GH_TOKEN"):
    GH_HDRS["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
                1433, 1521, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 9090, 9200, 27017]

# ---------------------------------------------------------------- HTTP çekirdeği
def http_get(url, method="GET", body=None, headers=None, timeout=10, max_redir=4):
    """Redirect + gzip destekli. set-cookie: TÜM çerezler listeye toplanır (login için kritik)."""
    for _ in range(max_redir + 1):
        p = urlparse(url)
        scheme, host = p.scheme, p.hostname
        path = p.path or "/"
        if p.query:
            path += "?" + p.query
        port = p.port or (443 if scheme == "https" else 80)
        hdrs0 = {"User-Agent": random.choice(UA_LIST), "Accept": "*/*",
                 "Accept-Language": "tr-TR,en-US;q=0.8",
                 "Accept-Encoding": "gzip, identity", "Connection": "close"}
        if headers:
            hdrs0.update(headers)
        try:
            if scheme == "https":
                conn = http.client.HTTPSConnection(host, port, timeout=timeout,
                                                   context=ssl.create_default_context())
            else:
                conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request(method, path, body=body, headers=hdrs0)
            resp = conn.getresponse()
            data = resp.read()
            status = resp.status
            rh = {}
            for k, v in resp.getheaders():
                kl = k.lower()
                if kl == "set-cookie":
                    rh.setdefault("set-cookie", []).append(v)
                else:
                    rh[kl] = v
            conn.close()
        except Exception as e:
            return 0, {}, str(e).encode("utf-8", "ignore")
        if status in (301, 302, 303, 307, 308) and rh.get("location"):
            url = urljoin(url, rh["location"])
            if status == 303:
                method, body = "GET", None
            continue
        if rh.get("content-encoding", "").lower() == "gzip" and data[:2] == b"\x1f\x8b":
            try:
                data = gzip.decompress(data)
            except Exception:
                pass
        return status, rh, data
    return 0, {}, b"redirect_limit"


def api_json(url, headers=None, timeout=12):
    st, _, data = http_get(url, headers=headers, timeout=timeout)
    if st == 0:
        return None, "ağ hatası"
    if st in (403, 429):
        return None, f"HTTP {st} (rate limit / bot engeli)"
    if st == 404:
        return None, "HTTP 404"
    try:
        return json.loads(data.decode("utf-8", "ignore")), None
    except Exception:
        return None, "JSON parse hatası"


def ddg_search(query, n=8):
    body = urlencode({"q": query, "kl": "tr-tr"})
    st, _, data = http_get("https://html.duckduckgo.com/html/", method="POST", body=body,
                           headers={"Content-Type": "application/x-www-form-urlencoded",
                                    "Referer": "https://duckduckgo.com/"})
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


def dork_links(query):
    print(BLUE + f"    Google: https://www.google.com/search?q={urlencode(query)}" + RESET)
    print(BLUE + f"    Bing  : https://www.bing.com/search?q={urlencode(query)}" + RESET)

# ---------------------------------------------------------------- isim/email türetme
def fold_tr(s):
    m = {"ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i", "ö": "o", "Ö": "o",
         "ş": "s", "Ş": "s", "ü": "u", "Ü": "u", "â": "a", "î": "i", "û": "u"}
    return "".join(m.get(c, c) for c in s).strip().lower()


def username_guesses(first, last):
    f, l = fold_tr(first), fold_tr(last)
    raw = [f, l, f + l, f + "." + l, f + "_" + l, f + "-" + l, f[0] + l,
           f + "." + l[0], l + "." + f, l + "_" + f, l + f,
           f + l + "01", f[0] + l + "01", f + l + "_" + l]
    if not l:
        raw = [f, f + "01", f + "2024", f + "_" + f]
    out = []
    for x in raw:
        x = x.strip("._-")
        if len(x) >= 2 and x not in out:
            out.append(x)
    return out


def email_guesses(first, last, domains):
    f, l = fold_tr(first), fold_tr(last)
    locals_ = []
    for x in [f, l, f + l, f + "." + l, f + "_" + l, f + "-" + l, f[0] + l,
              f + "." + l[0], l + "." + f, l + "_" + f]:
        x = x.strip("._-")
        if x and x not in locals_:
            locals_.append(x)
    return [f"{x}@{d}" for d in domains for x in locals_]

# ---------------------------------------------------------------- DNS (DoH)
def dns_query(name, rtype):
    rmap = {"A": 1, "AAAA": 28, "MX": 15, "NS": 2, "TXT": 16, "PTR": 12, "SOA": 6}
    j, e = api_json("https://cloudflare-dns.com/dns-query?" + urlencode({"name": name, "type": rtype}),
                    headers={"Accept": "application/dns-json"})
    if e:
        return []
    return [a.get("data") for a in (j or {}).get("Answer", []) if a.get("type") == rmap.get(rtype)]


def mx_lookup(domain):
    return dns_query(domain, "MX")


def ptr_lookup(ip):
    if ":" in ip:
        return "IPv6 PTR atlandı"
    name = ".".join(reversed(ip.split("."))) + ".in-addr.arpa"
    recs = dns_query(name, "PTR")
    return recs[0] if recs else "PTR kaydı yok"


def domain_rdap(domain):
    j, e = api_json("https://rdap.org/domain/" + domain, timeout=15)
    if e or not j:
        return {"hata": e or "kayıt bulunamadı"}
    out = {}
    for k in ("ldhName", "handle"):
        if j.get(k):
            out[k] = j.get(k)
    if j.get("status"):
        out["durum"] = j["status"]
    if j.get("nameservers"):
        out["nameserver"] = [n.get("ldhName") for n in j["nameservers"] if n.get("ldhName")]
    ev = {}
    for e2 in (j.get("events") or []):
        if e2.get("eventAction") in ("registration", "expiration", "last changed"):
            ev[e2["eventAction"]] = e2.get("eventDate")
    if ev:
        out["tarihler"] = ev
    ents = []
    for ent in (j.get("entities") or [])[:4]:
        vc = ((ent.get("vcardArray") or [None, []])[1]) or []
        rec = {}
        for item in vc:
            if item[0] == "fn": rec["isim"] = item[3]
            if item[0] == "org": rec["kurum"] = item[3]
            if item[0] == "email": rec["email"] = item[3]
            if item[0] == "tel": rec["telefon"] = item[3]
        if rec:
            ents.append(rec)
    if ents:
        out["kayit_sahipleri"] = ents
    return out

# ---------------------------------------------------------------- platform kontrolü
SITES = [
    ("GitHub", "https://github.com/{u}", "ok"), ("GitLab", "https://gitlab.com/{u}", "ok"),
    ("Bitbucket", "https://bitbucket.org/{u}", "ok"), ("Reddit", "https://www.reddit.com/user/{u}", "ok"),
    ("Telegram", "https://t.me/{u}", "ok"), ("YouTube", "https://www.youtube.com/@{u}", "dusuk"),
    ("TikTok", "https://www.tiktok.com/@{u}", "dusuk"), ("X/Twitter", "https://x.com/{u}", "dusuk"),
    ("Instagram", "https://www.instagram.com/{u}/", "ok"), ("Facebook", "https://www.facebook.com/{u}", "dusuk"),
    ("LinkedIn", "https://www.linkedin.com/in/{u}", "dusuk"), ("Medium", "https://medium.com/@{u}", "ok"),
    ("Dev.to", "https://dev.to/{u}", "ok"), ("Hashnode", "https://hashnode.com/@{u}", "ok"),
    ("HackerNews", "https://news.ycombinator.com/user?id={u}", "ok"), ("Keybase", "https://keybase.io/{u}", "ok"),
    ("Gravatar", "https://en.gravatar.com/{u}", "ok"), ("Twitch", "https://www.twitch.tv/{u}", "ok"),
    ("SoundCloud", "https://soundcloud.com/{u}", "ok"), ("Spotify", "https://open.spotify.com/user/{u}", "ok"),
    ("Steam", "https://steamcommunity.com/id/{u}", "ok"), ("Tumblr", "https://{u}.tumblr.com", "ok"),
    ("Pinterest", "https://www.pinterest.com/{u}/", "ok"), ("Flickr", "https://www.flickr.com/people/{u}/", "ok"),
    ("Vimeo", "https://vimeo.com/{u}", "ok"), ("Dribbble", "https://dribbble.com/{u}", "ok"),
    ("Behance", "https://www.behance.net/{u}", "ok"), ("VK", "https://vk.com/{u}", "dusuk"),
    ("Mastodon", "https://mastodon.social/@{u}", "ok"), ("Bluesky", "https://bsky.app/profile/{u}", "ok"),
    ("Chess.com", "https://www.chess.com/member/{u}", "ok"), ("Lichess", "https://lichess.org/@/{u}", "ok"),
    ("Duolingo", "https://www.duolingo.com/profile/{u}", "dusuk"), ("Strava", "https://www.strava.com/athletes/{u}", "ok"),
    ("Last.fm", "https://www.last.fm/user/{u}", "ok"), ("MyAnimeList", "https://myanimelist.net/profile/{u}", "ok"),
    ("Patreon", "https://www.patreon.com/{u}", "dusuk"), ("Ko-fi", "https://ko-fi.com/{u}", "ok"),
    ("BuyMeACoffee", "https://www.buymeacoffee.com/{u}", "ok"), ("PayPal.me", "https://www.paypal.me/{u}", "ok"),
    ("Ask.fm", "https://ask.fm/{u}", "ok"), ("Wattpad", "https://www.wattpad.com/user/{u}", "ok"),
    ("Pastebin", "https://pastebin.com/u/{u}", "ok"), ("CodePen", "https://codepen.io/{u}", "ok"),
    ("Replit", "https://replit.com/@{u}", "ok"), ("Archive.org", "https://archive.org/@{u}", "ok"),
]
LITE = {"GitHub", "Reddit", "Telegram", "YouTube", "TikTok", "X/Twitter", "Medium", "Dev.to",
        "GitLab", "Keybase", "Gravatar", "Twitch", "SoundCloud", "Spotify", "Steam", "Tumblr",
        "Pinterest", "Mastodon", "Bluesky", "Chess.com", "Lichess", "HackerNews", "VK", "Instagram"}


def check_site(site, username):
    name, tpl, conf = site
    url = tpl.format(u=username)
    st, _, body = http_get(url, timeout=8)
    if name == "HackerNews" and st == 200 and b"No such user" in body:
        return name, "yok", url
    if name == "Instagram" and st == 200 and b"this page isn't available" in body.lower():
        return name, "yok", url
    if st == 200:
        return name, ("BULUNDU" if conf == "ok" else "BULUNDU*"), url
    if st in (404, 410):
        return name, "yok", url
    if st in (403, 429):
        return name, "bot engeli", url
    if st == 0:
        return name, "ağ hatası", url
    return name, f"durum {st}", url


def platform_checks(username, sites, threads=10):
    res = {}
    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        futs = [ex.submit(check_site, s, username) for s in sites]
        for f in cf.as_completed(futs):
            name, durum, url = f.result()
            res[name] = {"durum": durum, "url": url}
    return res

# ================================================================ INSTAGRAM — CANLI OTURUM
def ig_signed(payload_dict):
    """Mobil API için HMAC-SHA256 imzalı signed_body (ig_sig_key_version=4)."""
    payload = json.dumps(payload_dict, separators=(",", ":"))
    sig = hmac.new(IG_SIG_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return urlencode({"ig_sig_key_version": "4", "signed_body": sig + "." + payload})


def ig_headers(sessionid=None, extra=None):
    h = {"User-Agent": IG_UA, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
         "x-ig-app-id": MOBILE_APP_ID, "x-ig-capabilities": "3brTv10=",
         "x-ig-connection-type": "WIFI", "Accept-Language": "tr-TR, en-US", "Accept-Encoding": "identity"}
    if sessionid:
        h["Cookie"] = f"sessionid={sessionid}"
    if extra:
        h.update(extra)
    return h


def extract_sessionid(rh):
    for ck in rh.get("set-cookie", []):
        for part in ck.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "sessionid" and v:
                return v
    return None


def ig_device_register(device):
    body = ig_signed({"device_id": device["device_id"], "guid": device["guid"],
                      "phone_id": device["phone_id"], "device_user_agent": IG_UA,
                      "android_id": device["device_id"].replace("android-", ""),
                      "timezone_offset": "10800"})
    st, rh, data = http_get("https://i.instagram.com/api/v1/devices/register/",
                            method="POST", body=body, headers=ig_headers(), timeout=15)
    return st


def ig_login_attempt(device, username, password):
    lp = {"phone_id": device["phone_id"], "_csrftoken": "missing", "username": username,
          "guid": device["guid"], "device_id": device["device_id"], "password": password,
          "login_attempt_count": "0"}
    st, rh, data = http_get("https://i.instagram.com/api/v1/accounts/login/",
                            method="POST", body=ig_signed(lp), headers=ig_headers(), timeout=20)
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
    except Exception:
        return {"hata": f"parse hatası (HTTP {st})"}
    if st == 200 and j.get("logged_in_user"):
        sid = extract_sessionid(rh)
        if sid:
            return {"sessionid": sid, "username": username}
        return {"hata": "giriş oldu ama sessionid çerezi alınamadı"}
    msg = j.get("message", "bilinmeyen hata")
    if msg == "challenge_required":
        return {"hata": "challenge_required — tarayıcıdan bu hesaba girip güvenlik adımını (checkpoint) çözün, sonra tekrar deneyin"}
    if msg == "two_factor_required":
        return {"two_factor": True, "identifier": (j.get("two_factor_info") or {}).get("two_factor_identifier"),
                "device": device}
    if "bad_password" in str(msg).lower() or st == 400:
        return {"hata": "şifre hatalı"}
    return {"hata": f"{msg} (HTTP {st})"}


def ig_two_factor(device, username, code, identifier):
    lp = {"username": username, "two_factor_identifier": identifier,
          "verification_code": code, "trust_this_device": "1",
          "guid": device["guid"], "device_id": device["device_id"]}
    st, rh, data = http_get("https://i.instagram.com/api/v1/accounts/two_factor_login/",
                            method="POST", body=ig_signed(lp), headers=ig_headers(), timeout=20)
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
    except Exception:
        return {"hata": f"2FA parse hatası (HTTP {st})"}
    if st == 200 and j.get("logged_in_user"):
        sid = extract_sessionid(rh)
        if sid:
            return {"sessionid": sid, "username": username}
    return {"hata": f"2FA başarısız: {j.get('message', 'bilinmiyor')} (HTTP {st})"}


def ig_login_flow(username, password):
    device = build_device_fingerprint()
    ig_device_register(device)
    res = ig_login_attempt(device, username, password)
    if res.get("two_factor"):
        ok("2FA doğrulaması gerekiyor.")
        kod = input(BLUE + "[?] Telefonundaki/uygulamadaki 6 haneli kod: " + RESET).strip()
        if not kod:
            return {"hata": "kod girilmedi"}
        return ig_two_factor(device, username, kod, res.get("identifier"))
    return res


def save_ig_session(sessionid, username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"sessionid": sessionid, "username": username}, f)


def load_ig_session():
    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("sessionid"):
            return d
    except Exception:
        pass
    return None


def delete_ig_session():
    try:
        os.remove(SESSION_FILE)
    except Exception:
        pass


def ig_session_valid(sessionid):
    st, _, data = http_get("https://i.instagram.com/api/v1/accounts/current_user/?edit=true",
                           headers=ig_headers(sessionid), timeout=12)
    return st == 200 and b'"user"' in data


def get_active_session(ask=True):
    """Kayıtlı oturumu döner; yoksa ve ask=True ise giriş ister."""
    saved = load_ig_session()
    if saved and ig_session_valid(saved["sessionid"]):
        return saved
    if saved:
        delete_ig_session()
        hata("Kayıtlı IG oturumu geçersiz olmuş, silindi.")
    if ask:
        cevap = input(BLUE + "[?] IG oturumu yok. Kendi hesabınla giriş yapılsın mı? [e/h]: " + RESET).strip().lower()
        if cevap == "e":
            u = input(BLUE + "[?] IG kullanıcı adı: " + RESET).strip()
            p = getpass.getpass(BLUE + "[?] IG şifre: " + RESET)
            if not u or not p:
                hata("Kullanıcı adı/şifre boş.")
                return None
            sonuc = ig_login_flow(u, p)
            if sonuc and sonuc.get("sessionid"):
                save_ig_session(sonuc["sessionid"], u)
                ok(f"Giriş başarılı — oturum kaydedildi (kullanıcı: {u})")
                return sonuc
            hata(f"Giriş başarısız: {sonuc.get('hata') if sonuc else 'bilinmiyor'}")
    return None


def ig_fetch_profile(username, sessionid=None, after=None, first=12,
                     host="www.instagram.com", app_id=WEB_APP_ID, ua=None):
    params = {"username": username, "first": str(first)}
    if after:
        params["after"] = after
    path = "/api/v1/users/web_profile_info/?" + urlencode(params)
    hdrs = {"User-Agent": ua or UA_LIST[0], "Accept": "*/*", "Accept-Encoding": "identity",
            "x-ig-app-id": app_id, "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{username}/"}
    if sessionid:
        hdrs["Cookie"] = f"sessionid={sessionid}"
    st, _, raw = http_get(f"https://{host}{path}", headers=hdrs, timeout=15)
    if st in (302, 401):
        return None, {"error": "login_wall"}
    if st == 0:
        return None, {"error": "network"}
    try:
        data = json.loads(raw.decode("utf-8", "ignore"))
    except Exception:
        return None, {"error": "parse"}
    user = ((data or {}).get("data") or {}).get("user")
    if user is None:
        return None, {"error": "no_user", "detail": (data or {}).get("message", "kullanıcı bulunamadı")}
    return data, None


def ig_scrape_html(username, sessionid=None):
    hdrs = {"User-Agent": UA_LIST[0], "Accept-Language": "tr-TR,en-US;q=0.8"}
    if sessionid:
        hdrs["Cookie"] = f"sessionid={sessionid}"
    st, _, raw = http_get(f"https://www.instagram.com/{username}/", headers=hdrs, timeout=15)
    if st != 200:
        return None
    h = raw.decode("utf-8", "ignore")
    for pat in (r'"user_id"\s*:\s*"?(\d+)"?', r'"pk"\s*:\s*"?(\d{7,16})"?',
                r'<meta property="al:android:url" content="[^"]*user\?userId=(\d+)"',
                r'"id"\s*:\s*"(\d{7,16})"'):
        m = re.search(pat, h)
        if m:
            return m.group(1)
    return None


def ig_legacy_a1(username, sessionid=None):
    hdrs = {"User-Agent": UA_LIST[0], "x-ig-app-id": WEB_APP_ID}
    if sessionid:
        hdrs["Cookie"] = f"sessionid={sessionid}"
    st, _, raw = http_get(f"https://www.instagram.com/{username}/?__a=1&__d=dis", headers=hdrs, timeout=15)
    if st == 200:
        try:
            data = json.loads(raw.decode("utf-8", "ignore"))
            u = ((data.get("graphql") or {}).get("user")) or data.get("user")
            if u and u.get("id"):
                return u
        except Exception:
            pass
    return None


def ig_usernameinfo(username, sessionid):
    st, _, raw = http_get(f"https://i.instagram.com/api/v1/users/{username}/usernameinfo/",
                          headers=ig_headers(sessionid), timeout=15)
    try:
        data = json.loads(raw.decode("utf-8", "ignore"))
        u = data.get("user")
        if u and u.get("pk"):
            return u
    except Exception:
        pass
    return None


def ig_get_user_id(username, sessionid=None):
    """5 yöntemli GERÇEK ID zinciri — ilk başarılı olan döner."""
    for host, app_id, ua in (("www.instagram.com", WEB_APP_ID, None),
                             ("i.instagram.com", MOBILE_APP_ID, IG_UA)):
        data, err = ig_fetch_profile(username, sessionid, host=host, app_id=app_id, ua=ua)
        if data:
            u = data["data"]["user"]
            if u.get("id"):
                return u["id"], {"kaynak": f"web_profile_info ({host})", "profil": u}, None
    sid = ig_scrape_html(username, sessionid)
    if sid:
        return sid, {"kaynak": "profil HTML", "profil": {"id": sid, "username": username}}, None
    u = ig_legacy_a1(username, sessionid)
    if u and u.get("id"):
        return u["id"], {"kaynak": "__a=1", "profil": u}, None
    if sessionid:
        u = ig_usernameinfo(username, sessionid)
        if u and u.get("pk"):
            return u["pk"], {"kaynak": "usernameinfo (mobil API)", "profil": u}, None
    return None, None, {"error": "tüm yöntemler başarısız",
                        "detail": "Instagram bot koruması. Menü 17 ile kendi hesabınla giriş yap veya 10-15 dk bekleyin."}


def normalize_ig_user(u, kaynak):
    if kaynak.startswith("usernameinfo"):
        return {"id": u.get("pk"), "full_name": u.get("full_name"), "biography": u.get("biography"),
                "is_private": u.get("is_private"), "is_verified": u.get("is_verified"),
                "followers": u.get("follower_count"), "following": u.get("following_count"),
                "media_count": u.get("media_count")}
    return {"id": u.get("id"), "full_name": u.get("full_name"), "biography": u.get("biography"),
            "is_private": u.get("is_private"), "is_verified": u.get("is_verified"),
            "followers": (u.get("edge_followed_by") or {}).get("count"),
            "following": (u.get("edge_follow") or {}).get("count"),
            "media_count": (u.get("edge_owner_to_timeline_media") or {}).get("count")}


def ig_location_details(loc_id, sessionid):
    """Konum ID'sinden tam adres/koordinat (mobil API, oturumla)."""
    if not sessionid or not loc_id:
        return None
    st, _, raw = http_get(f"https://i.instagram.com/api/v1/locations/{loc_id}/info/",
                          headers=ig_headers(sessionid), timeout=12)
    if st != 200:
        return None
    try:
        j = json.loads(raw.decode("utf-8", "ignore"))
        return j.get("location")
    except Exception:
        return None


def ig_timeline_locations(username, sessionid, max_posts=30):
    """Medya akışını sayfalayarak geotag'ları toplar ve zenginleştirir."""
    edges, after = [], None
    while len(edges) < max_posts:
        data, err = ig_fetch_profile(username, sessionid, after=after)
        if err or not data:
            break
        m = (data.get("data") or {}).get("user", {}).get("edge_owner_to_timeline_media") or {}
        page = m.get("edges") or []
        if not page:
            break
        edges.extend(page)
        pi = m.get("page_info") or {}
        if not pi.get("has_next_page"):
            break
        after = pi.get("end_cursor")
        time.sleep(1.5)
    locs = []
    for e in edges[:max_posts]:
        node = e.get("node", {})
        loc = node.get("location")
        if not loc:
            continue
        caps = (node.get("edge_media_to_caption") or {}).get("edges", [])
        cap = caps[0].get("node", {}).get("text", "")[:100] if caps else ""
        lid = str(loc.get("id") or "")
        adres = loc.get("address_json")
        if isinstance(adres, str):
            try:
                adres = json.loads(adres)
            except Exception:
                pass
        detay = ig_location_details(lid, sessionid)
        if detay:
            adr2 = detay.get("address_json")
            if isinstance(adr2, str):
                try:
                    adr2 = json.loads(adr2)
                except Exception:
                    pass
            adres = adr2 or adres
        locs.append({"kisa_kod": node.get("shortcode"),
                     "tarih_utc": node.get("taken_at_timestamp"),
                     "yer": (detay or {}).get("name") or loc.get("name"),
                     "lat": (detay or {}).get("lat") or loc.get("lat"),
                     "lng": (detay or {}).get("lng") or loc.get("lng"),
                     "adres": adres, "altyazi": cap})
    return locs


def ig_user_info(user_id, sessionid):
    if not sessionid:
        return None
    st, _, raw = http_get(f"https://i.instagram.com/api/v1/users/{user_id}/info/",
                          headers=ig_headers(sessionid), timeout=15)
    try:
        data = json.loads(raw.decode("utf-8", "ignore"))
        return data.get("user")
    except Exception:
        return None


def ig_deep_dive(username, sessionid=None, max_posts=30):
    """GERÇEK ID + profil + geotag konumlar + (oturumla) public alanlar."""
    user_id, meta, err = ig_get_user_id(username, sessionid)
    if not user_id:
        return {"username": username, "hata": err}
    kaynak = (meta or {}).get("kaynak", "?")
    prof = normalize_ig_user((meta or {}).get("profil") or {}, kaynak)
    prof["id"] = user_id
    out = {"username": username, "id_kaynak": kaynak, "profile": prof, "locations": []}
    if not prof.get("is_private"):
        out["locations"] = ig_timeline_locations(username, sessionid, max_posts)
    else:
        out["not"] = "private hesap — medya ve konum görünmüyor"
    if sessionid:
        extra = ig_user_info(user_id, sessionid)
        if extra:
            ek = {}
            for k in ("public_email", "public_phone_number", "public_phone_country_code",
                      "city_name", "address_street", "zip", "external_url", "is_business", "category"):
                if extra.get(k):
                    ek[k] = extra.get(k)
            if ek:
                prof["ek"] = ek
    return out

# ---------------------------------------------------------------- cihaz fingerprint (IMEI)
def luhn_check_digit(body):
    total = 0
    for i, ch in enumerate(reversed(body)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - (total % 10)) % 10


def build_device_fingerprint():
    imei = "86" + "".join(random.choices("0123456789", k=6)) + "".join(random.choices("0123456789", k=6))
    imei += str(luhn_check_digit(imei))
    return {"imei": imei,
            "device_id": "android-" + hashlib.md5(imei.encode()).hexdigest()[:16],
            "phone_id": str(uuid.uuid4()), "guid": str(uuid.uuid4())}


def maps_link(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"


def cluster_locations(locs):
    """Geotag'ları ~1km çözünürlükte kümeler: en aktif bölge + merkez nokta."""
    noktalar = [l for l in locs if l.get("lat") is not None and l.get("lng") is not None]
    if not noktalar:
        return None
    gruplar = {}
    for l in noktalar:
        k = (round(l["lat"], 2), round(l["lng"], 2))
        gruplar.setdefault(k, []).append(l)
    top = max(gruplar.values(), key=len)
    mlat = round(sum(l["lat"] for l in noktalar) / len(noktalar), 5)
    mlng = round(sum(l["lng"] for l in noktalar) / len(noktalar), 5)
    return {"toplam_geotag": len(noktalar), "benzersiz_bolge": len(gruplar),
            "en_aktif_bolge": top[0].get("yer"), "en_aktif_sayi": len(top),
            "kumes_merkezi": {"lat": mlat, "lng": mlng}, "harita": maps_link(mlat, mlng)}

# ---------------------------------------------------------------- GitHub / Reddit / HN
def github_search_name(name):
    j, e = api_json("https://api.github.com/search/users?" + urlencode({"q": f'"{name}" in:fullname'}),
                    headers=GH_HDRS)
    if e or not j:
        return [], e
    return j.get("items", [])[:8], None


def github_user_detail(login):
    j, e = api_json("https://api.github.com/users/" + login, headers=GH_HDRS)
    if e or not j:
        return {"login": login, "hata": e or "yanıt yok"}
    keys = ("login", "name", "email", "blog", "location", "bio", "company",
            "twitter_username", "public_repos", "followers", "following", "created_at")
    return {k: j.get(k) for k in keys if j.get(k) is not None}


def reddit_user(username):
    j, e = api_json("https://www.reddit.com/user/" + username + "/about.json",
                    headers={"User-Agent": UA_REDDIT})
    if e:
        return {"hata": e}
    d = (j or {}).get("data", {})
    if not d:
        return {"hata": "kullanıcı yok / engellendi"}
    return {"oluşturma": dt.datetime.fromtimestamp(d.get("created_utc", 0), tz=dt.timezone.utc).strftime("%Y-%m-%d"),
            "link_karma": d.get("link_karma"), "yorum_karma": d.get("comment_karma"),
            "mod_mu": d.get("is_mod")}


def reddit_search(name):
    j, e = api_json("https://www.reddit.com/search.json?" + urlencode({"q": f'"{name}"', "limit": 12}),
                    headers={"User-Agent": UA_REDDIT})
    if e:
        return [], e
    out = []
    for c in (j or {}).get("data", {}).get("children", []):
        d = c.get("data", {})
        out.append({"baslik": d.get("title"), "sub": d.get("subreddit"), "yazar": d.get("author"),
                    "url": "https://www.reddit.com" + (d.get("permalink") or "")})
    return out, None


def hn_search(**params):
    j, e = api_json("https://hn.algolia.com/api/v1/search?" + urlencode(params))
    if e:
        return [], e
    out = []
    for h in (j or {}).get("hits", []):
        out.append({"baslik": h.get("title") or h.get("story_title"),
                    "url": h.get("url") or "https://news.ycombinator.com/item?id=" + str(h.get("objectID")),
                    "yazar": h.get("author"), "tarih": h.get("created_at")})
    return out, None

# ---------------------------------------------------------------- telefon / IP
def phone_lookup(phone, country="TR"):
    num = re.sub(r"\D", "", phone)
    if not num.startswith(("90", "1", "44", "49", "33", "7", "81", "86", "91")):
        num = {"TR": "90", "US": "1", "DE": "49", "GB": "44", "FR": "33"}.get(country.upper(), "90") + num
    j, e = api_json("https://api.veriphone.io/v2/verify?" + urlencode({"phone": num}))
    if e or not j:
        return {"hata": e or "yanıt yok"}
    keys = ("phone_valid", "phone_e164", "country", "carrier", "line_type", "national_format")
    return {k: j.get(k) for k in keys if j.get(k) is not None}


def is_private_ip(ip):
    try:
        a, b, c, d = (int(x) for x in ip.split("."))
    except Exception:
        return True
    return (a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168) or a == 127
            or (a == 169 and b == 254) or (a == 100 and 64 <= b <= 127) or a == 0 or a >= 224)


def ip_lookup(ip):
    fields = "status,country,regionName,city,lat,lon,timezone,isp,org,as,reverse,mobile,proxy,hosting,query"
    j, e = api_json("http://ip-api.com/json/" + ip + "?" + urlencode({"fields": fields}))
    if e or not j:
        return {"hata": e or "yanıt yok"}
    if j.get("status") != "success":
        return {"hata": j.get("message", "bilinmiyor")}
    return {k: j.get(k) for k in ("query", "country", "regionName", "city", "lat", "lon",
                                  "timezone", "isp", "org", "as", "reverse", "mobile", "proxy", "hosting")}


def rdap_summary(ip):
    j, e = api_json(f"https://rdap.org/ip/{ip}", timeout=15)
    if e or not j:
        return {"hata": e or "yanıt yok"}
    out = {}
    for k in ("handle", "name", "type", "startAddress", "endAddress", "country"):
        if j.get(k):
            out[k] = j[k]
    for ent in (j.get("entities") or [])[:3]:
        vc = ((ent.get("vcardArray") or [None, []])[1]) or []
        for item in vc:
            if item[0] == "fn": out.setdefault("kurum", []).append(item[3])
            if item[0] == "email": out.setdefault("email", []).append(item[3])
    if j.get("events"):
        out["son_guncelleme"] = [e.get("eventDate") for e in j["events"] if e.get("eventAction") == "last changed"]
    return out

# ---------------------------------------------------------------- SMTP
def smtp_exchange(s, cmd, wait=4):
    if cmd:
        s.sendall((cmd + "\r\n").encode())
    buf = b""
    deadline = time.time() + wait
    while time.time() < deadline:
        try:
            d = s.recv(4096)
        except (socket.timeout, OSError):
            break
        if not d:
            break
        buf += d
        lines = [ln for ln in buf.split(b"\r\n") if ln]
        if lines and re.match(rb"^\d{3} ", lines[-1]):
            break
    return buf.decode("utf-8", "ignore")


def smtp_validate(mx, rcpt, mail_from="noreply@osint.local"):
    try:
        s = socket.create_connection((mx, 25), timeout=8)
        s.settimeout(4)
        smtp_exchange(s, "")
        ehlo = smtp_exchange(s, "EHLO osint.local")
        if "STARTTLS" in ehlo.upper():
            try:
                smtp_exchange(s, "STARTTLS")
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=mx)
                smtp_exchange(s, "EHLO osint.local")
            except Exception:
                pass
        smtp_exchange(s, f"MAIL FROM:<{mail_from}>")
        rc = smtp_exchange(s, f"RCPT TO:<{rcpt}>")
        smtp_exchange(s, "QUIT")
        s.close()
        if rc.startswith("250"): sonuc = "muhtemelen VAR"
        elif rc.startswith("5"): sonuc = "yok/reddedildi"
        elif rc.startswith("4"): sonuc = "geçici hata"
        else: sonuc = "belirsiz"
        return {"adres": rcpt, "mx": mx, "sonuc": sonuc, "yanit": rc.strip()[:120]}
    except Exception as e:
        return {"adres": rcpt, "mx": mx, "sonuc": "bağlantı hatası", "yanit": str(e)[:120]}


def send_test_mail(to_addr, subject, body):
    import smtplib
    domain = to_addr.split("@")[-1]
    mx = mx_lookup(domain)
    if not mx:
        return {"hata": f"{domain} için MX kaydı yok"}
    host = mx[0].split()[-1].rstrip(".")
    try:
        s = smtplib.SMTP(host, 25, timeout=15)
        s.ehlo()
        try:
            s.starttls()
            s.ehlo()
        except Exception:
            pass
        s.mail("osint@osint.local")
        rc = s.rcpt(to_addr)
        if rc[0] == 250:
            s.data(f"From: osint@osint.local\r\nTo: {to_addr}\r\nSubject: {subject}\r\n\r\n{body}")
        s.quit()
        return {"durum": "gönderim denendi", "rcpt_kodu": rc[0]}
    except Exception as e:
        return {"hata": str(e)}

# ---------------------------------------------------------------- web'den profil çıkarma
def extract_profiles_from_urls(urls):
    found = {"instagram": set(), "github": set(), "twitter": set(), "linkedin": set(), "telegram": set()}
    for u in urls:
        p = urlparse(u)
        host = (p.hostname or "").lower()
        segs = [s for s in p.path.split("/") if s]
        if "instagram.com" in host and segs:
            found["instagram"].add(segs[0])
        elif "github.com" in host and segs and segs[0] not in ("login", "signup", "topics", "collections", "explore"):
            found["github"].add(segs[0])
        elif host in ("x.com", "twitter.com") and segs and segs[0] not in ("home", "explore", "i", "login", "search", "hashtag"):
            found["twitter"].add(segs[0])
        elif "linkedin.com" in host and segs:
            found["linkedin"].add(segs[0])
        elif "t.me" in host and segs:
            found["telegram"].add(segs[0])
    return found

# ================================================================ DİĞER ARAÇLAR
def url_chain(url, timeout=10, max_hops=5):
    chain = []
    method = "GET"
    for _ in range(max_hops):
        p = urlparse(url)
        scheme, host = p.scheme, p.hostname
        if not scheme or not host:
            break
        path = p.path or "/"
        if p.query:
            path += "?" + p.query
        port = p.port or (443 if scheme == "https" else 80)
        hdrs = {"User-Agent": UA_LIST[0], "Accept": "*/*",
                "Accept-Encoding": "identity", "Connection": "close"}
        try:
            if scheme == "https":
                conn = http.client.HTTPSConnection(host, port, timeout=timeout,
                                                   context=ssl.create_default_context())
            else:
                conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request(method, path, headers=hdrs)
            resp = conn.getresponse()
            data = resp.read()
            status = resp.status
            rh = {k.lower(): v for k, v in resp.getheaders()}
            loc = rh.get("location")
            conn.close()
        except Exception as e:
            chain.append({"url": url, "durum": 0, "hata": str(e)})
            return chain, 0, {}, b""
        chain.append({"url": url, "durum": status, "yeni_konum": loc})
        if status in (301, 302, 303, 307, 308) and loc:
            url = urljoin(url, loc)
            if status == 303:
                method = "GET"
            continue
        return chain, status, rh, data
    return chain, 0, {}, b""


def ssl_cert_info(host, port=443):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=8) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as s:
                cert = s.getpeercert()
        issuer = dict(x for x in cert.get("issuer", []))
        subject = dict(x for x in cert.get("subject", []))
        return {"veren": issuer.get("organizationName") or issuer.get("commonName"),
                "cn": subject.get("commonName"),
                "baslangic": cert.get("notBefore"), "bitis": cert.get("notAfter"),
                "san": [x[1] for x in cert.get("subjectAltName", [])][:8]}
    except Exception as e:
        return {"hata": str(e)}


def grab_banner(host, port):
    try:
        s = socket.create_connection((host, port), timeout=4)
        s.settimeout(3)
        if port in (80, 8080, 8888):
            s.sendall(b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            data = s.recv(512)
        elif port == 443:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                ss.sendall(b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
                data = ss.recv(512)
        else:
            data = s.recv(256)
        s.close()
        text = data.decode("utf-8", "ignore").strip()
        return text[:120].replace("\r", " ").replace("\n", " | ")
    except Exception:
        return None


def scan_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return port, True
    except Exception:
        return port, False


def port_scan(host, ports=None, threads=30):
    ports = ports or COMMON_PORTS
    acik = []
    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        futs = [ex.submit(scan_port, host, p) for p in ports]
        for f in cf.as_completed(futs):
            p, a = f.result()
            if a:
                acik.append(p)
    acik.sort()
    banner = {}
    for p in acik[:12]:
        banner[p] = grab_banner(host, p)
    return acik, banner


def crt_subdomains(domain, timeout=30):
    st, _, data = http_get("https://crt.sh/?q=%25." + domain + "&output=json", timeout=timeout)
    if st != 200:
        return [], {}, f"crt.sh HTTP {st} (bazen yavaş/engelli — sonra tekrar deneyin)"
    try:
        rows = json.loads(data.decode("utf-8", "ignore"))
    except Exception:
        return [], {}, "JSON parse hatası"
    subs = set()
    for r in rows:
        for name in (r.get("name_value") or "").split("\n"):
            nm = name.strip().strip("*.").strip(".").lower()
            if nm and nm.endswith(domain) and nm != domain:
                subs.add(nm)
    subs = sorted(subs)
    alive = {}

    def resolve(nm):
        try:
            alive[nm] = socket.gethostbyname(nm)
        except Exception:
            pass

    with cf.ThreadPoolExecutor(max_workers=20) as ex:
        futs = [ex.submit(resolve, n) for n in subs[:60]]
        for f in futs:
            f.result()
    return subs, alive, None


def mac_lookup(mac):
    mac = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(mac) != 12:
        return {"hata": "geçersiz MAC — 12 hex karakter gerekli (örn. AA:BB:CC:DD:EE:FF)"}
    st, _, data = http_get("https://api.maclookup.app/v2/macs/" + mac,
                           headers={"User-Agent": "osint-mega"}, timeout=12)
    if st == 0:
        return {"hata": "ağ hatası"}
    if st == 404:
        return {"sonuc": "üretici bulunamadı (özel/random MAC olabilir)"}
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
        return {"mac": mac, "bulundu": j.get("found"), "uretici": j.get("vendor"),
                "tip": j.get("type"), "erisim": j.get("accessType")}
    except Exception:
        return {"hata": "parse hatası", "ham": data[:200].decode("utf-8", "ignore")}


def cve_search(q):
    if re.fullmatch(r"CVE-\d{4}-\d{4,7}", q.upper()):
        st, _, data = http_get("https://cve.circl.lu/api/cve/" + q.upper(), timeout=15)
        if st == 200:
            try:
                return [json.loads(data.decode("utf-8", "ignore"))], None
            except Exception:
                pass
        return [], "CVE bulunamadı / API yanıt vermedi"
    st, _, data = http_get("https://cve.circl.lu/api/search/" + quote(q), timeout=15)
    if st != 200:
        return [], f"HTTP {st}"
    try:
        return json.loads(data.decode("utf-8", "ignore")) or [], None
    except Exception:
        return [], "parse hatası"


def identify_hash(h):
    h = h.strip()
    if re.fullmatch(r"[0-9a-fA-F]{32}", h): return "MD5 veya NTLM (32 hex — ayırt etmek için uzunluk yetmez)"
    if re.fullmatch(r"[0-9a-fA-F]{40}", h): return "SHA-1"
    if re.fullmatch(r"[0-9a-fA-F]{64}", h): return "SHA-256"
    if re.fullmatch(r"[0-9a-fA-F]{128}", h): return "SHA-512"
    if re.match(r"^\$2[aby]\$\d{2}\$", h): return "bcrypt"
    if re.match(r"^\$1\$", h): return "MD5 crypt"
    if re.match(r"^\$5\$", h): return "SHA-256 crypt"
    if re.match(r"^\$6\$", h): return "SHA-512 crypt"
    return None


def pwned_count(sha1_hex):
    prefix, suffix = sha1_hex[:5], sha1_hex[5:]
    st, _, data = http_get("https://api.pwnedpasswords.com/range/" + prefix, timeout=12)
    if st != 200:
        return None
    for ln in data.decode("utf-8", "ignore").splitlines():
        s, _, cnt = ln.partition(":")
        if s.lower() == suffix.lower():
            return int(cnt)
    return 0


def emailrep(email):
    st, _, data = http_get("https://emailrep.io/" + email,
                           headers={"User-Agent": "osint-mega", "Accept": "application/json"}, timeout=15)
    if st in (401, 403):
        return {"hata": "emailrep.io anahtar istiyor (ücretsiz tier limiti dolmuş olabilir)"}
    if st != 200:
        return {"hata": f"HTTP {st}"}
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
    except Exception:
        return {"hata": "parse hatası"}
    out = {"email": j.get("email"), "reputation": j.get("reputation"),
           "suspicious": j.get("suspicious"), "references": j.get("references"), "details": {}}
    d = j.get("details") or {}
    for k in ("malicious_activity", "credentials_leaked", "spam", "spoofable",
              "domain_reputation", "new_domain", "free_provider", "disposable",
              "deliverable", "valid_mx", "suspicious_tld"):
        if k in d:
            v = d[k]
            out["details"][k] = v.get("summary") if isinstance(v, dict) else v
    return out


def wayback_available(url):
    st, _, data = http_get("https://archive.org/wayback/available?" + urlencode({"url": url}), timeout=15)
    if st == 200:
        try:
            j = json.loads(data.decode("utf-8", "ignore"))
            return ((j.get("archived_snapshots") or {}).get("closest")) or None
        except Exception:
            pass
    return None


def wayback_cdx(domain, limit=40):
    st, _, data = http_get("http://web.archive.org/cdx/search/cdx?" + urlencode(
        {"url": domain + "/*", "output": "json", "limit": str(limit), "collapse": "urlkey",
         "fl": "timestamp,original,statuscode"}), timeout=25)
    if st != 200:
        return [], f"HTTP {st}"
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
        if j and j[0] == ["timestamp", "original", "statuscode"]:
            return j[1:], None
        return j, None
    except Exception as e:
        return [], "parse hatası: " + str(e)


def shodan_host(ip):
    key = os.environ.get("SHODAN_API_KEY")
    if not key:
        return {"hata": "SHODAN_API_KEY ortam değişkeni gerekli — https://account.shodan.io/register (ücretsiz hesap) ile alınır"}
    st, _, data = http_get(f"https://api.shodan.io/shodan/host/{ip}?key={key}", timeout=15)
    if st != 200:
        return {"hata": f"HTTP {st} (geçersiz anahtar / IP'de veri yok / limit)"}
    try:
        j = json.loads(data.decode("utf-8", "ignore"))
    except Exception:
        return {"hata": "parse hatası"}
    return {"ip": j.get("ip_str"), "hostname": j.get("hostnames"), "os": j.get("os"),
            "org": j.get("org"), "isp": j.get("isp"), "portlar": j.get("ports"),
            "lokasyon": {k: j.get(k) for k in ("country_name", "city", "region_name", "latitude", "longitude")},
            "vulnler": j.get("vulns") or [], "banner_sayisi": len(j.get("data") or [])}

# ================================================================ BANNER
def banner():
    line("=")
    print(GREEN + "         OSINT MEGA v8 — MARKOS İŞLETİM SİSTEMİ OSINT (17 GERÇEK ARAÇ)" + RESET)
    print(BLUE + "   Tüm araçlar GERÇEKTİR: canlı API/HTTP sorguları, sahte veri yok" + RESET)
    line("=")
    print(GREEN + "  [ + ] " + BLUE + "Bu Araç OSINT Aracıdır" + RESET)
    print(BLUE + "  [ * ] " + GREEN + "Bu Araç Markos İşletim sistemine Aittir" + RESET)
    print(GREEN + "  [ ! ] " + BLUE + "Bu Aracı yetkili kişiler kullanabilir" + RESET)
    print(BLUE + "  [ ! ] " + GREEN + "Sorumluluk kullanıcıya aittir" + RESET)
    line("=")
    print(GREEN + " [ 1 ] " + BLUE + "Username → CANLI IG ID + KONUM (oturum açarak)")
    print(GREEN + " [ 2 ] " + BLUE + "Telefon → ülke/operatör + web izi + dork")
    print(GREEN + " [ 3 ] " + BLUE + "İsim → kişisel bilgi taraması (OSINT)")
    print(GREEN + " [ 4 ] " + BLUE + "Email → aday + MX + SMTP doğrulama + test maili")
    print(GREEN + " [ 5 ] " + BLUE + "IP → konum, ISP, RDAP, PTR")
    print(GREEN + " [ 6 ] " + BLUE + "Arama motoru (canlı DuckDuckGo + dorklar)")
    print(GREEN + " [ 7 ] " + BLUE + "Domain OSINT (DNS + WHOIS/RDAP + başlık)")
    print(GREEN + " [ 8 ] " + BLUE + "URL güvenlik analizi (redirect + başlıklar + SSL)")
    print(GREEN + " [ 9 ] " + BLUE + "IP port taraması (TCP connect + banner)")
    print(GREEN + " [10 ] " + BLUE + "Alt alan adı keşfi (crt.sh sertifika şeffaflığı)")
    print(GREEN + " [11 ] " + BLUE + "MAC adresi → üretici (OUI)")
    print(GREEN + " [12 ] " + BLUE + "CVE / zafiyet arama (cve.circl.lu)")
    print(GREEN + " [13 ] " + BLUE + "Hash analizi + sızıntı kontrolü (pwned)")
    print(GREEN + " [14 ] " + BLUE + "Email repütasyonu (emailrep.io)")
    print(GREEN + " [15 ] " + BLUE + "Wayback makinesi / arşiv kontrolü")
    print(GREEN + " [16 ] " + BLUE + "Shodan sorgu (SHODAN_API_KEY gerekir)")
    print(GREEN + " [17 ] " + BLUE + "IG oturum yönetimi (giriş / durum / çıkış)")
    print(GREEN + " [18 ] " + BLUE + "Veritabanı — tarama geçmişi (SQLite)")
    print(GREEN + " [ 0 ] " + BLUE + "Çıkış")
    line("=")

# ================================================================ MENÜ SEÇENEKLERİ
def opt_username():
    line("=")
    print(GREEN + "  [1] USERNAME → CANLI IG ID + KONUM" + RESET)
    line("=")
    u = input(BLUE + "[?] Instagram kullanıcı adı: " + RESET).strip()
    if not u:
        return
    sess = get_active_session(ask=True)
    info(f"'{u}' için 5 yöntemli gerçek ID zinciri çalıştırılıyor...")
    r = ig_deep_dive(u, sess["sessionid"] if sess else None, max_posts=30)
    db_kaydet("ig_username", u, r)
    if "hata" in r:
        hata(r["hata"].get("detail", r["hata"]))
        return
    p = r["profile"]
    ok(f"GERÇEK USER ID : {p['id']}   (kaynak: {r['id_kaynak']})")
    ok(f"Tam ad         : {p.get('full_name')}")
    ok(f"Biyografi      : {p.get('biography')}")
    ok(f"Private        : {p.get('is_private')} | Doğrulanmış: {p.get('is_verified')}")
    ok(f"Takipçi/Takip  : {p.get('followers')} / {p.get('following')}")
    ok(f"Medya sayısı   : {p.get('media_count')}")
    for k, v in (p.get("ek") or {}).items():
        ok(f"{k:<24}: {v}")
    locs = r.get("locations") or []
    if locs:
        ok(f"{len(locs)} medyada KONUM ETİKETİ bulundu:")
        for loc in locs[:12]:
            ll = f"{loc['lat']}, {loc['lng']}" if loc["lat"] is not None else "koordinat yok"
            ts = (dt.datetime.fromtimestamp(loc["tarih_utc"], tz=dt.timezone.utc).strftime("%Y-%m-%d")
                  if loc["tarih_utc"] else "-")
            print(GREEN + f"      • {loc['yer']} | {ll} | {ts} | {maps_link(loc['lat'], loc['lng']) if loc['lat'] is not None else ''}" + RESET)
        kl = cluster_locations(locs)
        if kl:
            ok("KONUM KÜME ANALİZİ (gerçek geotag verisinden):")
            ok(f"Toplam geotag: {kl['toplam_geotag']} | Benzersiz bölge: {kl['benzersiz_bolge']}")
            ok(f"En aktif bölge: {kl['en_aktif_bolge']} (x{kl['en_aktif_sayi']})")
            ok(f"Merkez nokta: {kl['kumes_merkezi']} — {kl['harita']}")
    elif "not" in r:
        hata(r["not"])
    else:
        hata("Medyalarda geotag bulunamadı (kullanıcı konum etiketi kullanmıyor olabilir).")
    dev = build_device_fingerprint()
    info("Cihaz fingerprint (Luhn geçerli IMEI — üretilir, başkasından çekilmez):")
    print(BLUE + f"    IMEI: {dev['imei']} | device_id: {dev['device_id']}" + RESET)
    info("Aynı username diğer platformlarda aranıyor (~46 site)...")
    pc = platform_checks(u, SITES, 10)
    db_kaydet("platform_checks", u, pc)
    for site, r2 in pc.items():
        if r2["durum"].startswith("BULUNDU"):
            ok(f"{site:<12} {r2['durum']:<10} {r2['url']}")

def opt_phone():
    line("=")
    print(GREEN + "  [2] TELEFON → ÜLKE/OPERATÖR + WEB İZİ" + RESET)
    line("=")
    tel = input(BLUE + "[?] Telefon numarası (örn. +905551112233): " + RESET).strip()
    if not tel:
        return
    ulke = input(BLUE + "[?] Ülke kodu (varsayılan TR): " + RESET).strip() or "TR"
    info("veriphone.io sorgulanıyor...")
    pl = phone_lookup(tel, ulke)
    print(BLUE + "\n[+] Telefon bilgisi:" + RESET)
    print(GREEN + json.dumps(pl, ensure_ascii=False, indent=2) + RESET)
    e164 = pl.get("phone_e164") or re.sub(r"\D", "", tel)
    nat = pl.get("national_format")
    web_iz = []
    if pl.get("phone_valid"):
        for q in [f'"{e164}"', f'"{nat}"']:
            info(f"Web aranıyor: {q}")
            for r in ddg_search(q, 6):
                print(GREEN + f"    • {r['title'][:70]} — {r['url']}" + RESET)
                web_iz.append(r["url"])
            time.sleep(2.5)
        info("Elle çalıştırmak için dork linkleri:")
        dork_links(f'"{e164}" OR "{nat}"')
    else:
        hata("Numara geçersiz görünüyor (veriphone doğrulaması).")
    db_kaydet("telefon", tel, {"bilgi": pl, "web_izleri": web_iz})
    hata("Dürüst sınır: mobil hat için sokak seviyesi konum ücretsiz API'de YOKTUR. Alınan: ülke, operatör, hat tipi + web izi.")

def opt_name():
    line("=")
    print(GREEN + "  [3] İSİM → KİŞİSEL BİLGİ TARAMASI (OSINT)" + RESET)
    print(BLUE + "  Beklenen süre: ~1-2 dakika (rate-limit koruması dahil)" + RESET)
    line("=")
    name = input(BLUE + "[?] Hedef isim (örn. 'Ahmet Yılmaz'): " + RESET).strip()
    if not name:
        return
    report = {"hedef": name, "zaman": dt.datetime.now(dt.timezone.utc).isoformat()}
    tokens = name.split()
    first, last = (tokens[0], tokens[-1]) if len(tokens) >= 2 else (tokens[0], "")
    guesses = username_guesses(first, last)
    report["aday_kullanici_adlari"] = guesses[:4]
    info(f"Aday kullanıcı adları: {', '.join(guesses[:4])}")

    info(f"[PLATFORM] '{guesses[0]}' ~46 platformda aranıyor...")
    pc_all = {}
    for i, cand in enumerate(guesses[:4]):
        sites = SITES if i == 0 else [s for s in SITES if s[0] in LITE]
        pc_all[cand] = platform_checks(cand, sites, 10)
    report["platform"] = pc_all
    bulunan = [(c, s, r["url"]) for c, res in pc_all.items() for s, r in res.items()
               if r["durum"].startswith("BULUNDU")]
    if bulunan:
        ok(f"Bulunan hesaplar ({len(bulunan)}):")
        for c, s, url in bulunan:
            print(GREEN + f"    • {s:<12} ({c}) -> {url}" + RESET)
    else:
        hata("Adaylarla hiçbir platformda hesap bulunamadı.")

    info("[WEB] DuckDuckGo derin araması yapılıyor...")
    queries = [f'"{name}"', f'"{name}" site:instagram.com', f'"{name}" site:linkedin.com',
               f'"{name}" site:github.com', f'"{name}" (twitter.com OR site:x.com)',
               f'"{name}" site:facebook.com']
    web_res, all_urls = {}, []
    for q in queries:
        print(BLUE + f"    aranıyor: {q}" + RESET)
        res = ddg_search(q, 6)
        time.sleep(2.5)
        if res and res[0].get("blocked"):
            hata("DDG anomaly kiliti — kısa bekleyip tekrar deneyin.")
            continue
        web_res[q] = res
        all_urls += [r["url"] for r in res]
    report["web"] = web_res
    profs = extract_profiles_from_urls(all_urls)
    report["webden_profiller"] = {k: sorted(v)[:5] for k, v in profs.items()}
    for k, v in profs.items():
        if v:
            ok(f"[WEB] {k}: {', '.join(sorted(v)[:5])}")

    info("[GITHUB] isim aranıyor...")
    items, err = github_search_name(name)
    gh_rows = [github_user_detail(it["login"]) for it in items[:6]]
    report["github"] = {"hata": err, "hesaplar": gh_rows}
    if err:
        hata(f": {err} (60 istek/saat limiti — GH_TOKEN ile aşılır)")
    for g in gh_rows:
        ok(f"{g.get('login')} | {g.get('name','')} | email: {g.get('email','-')} | "
           f"lokasyon: {g.get('location','-')} | blog: {g.get('blog','-')}")

    info("[REDDIT] aranıyor...")
    ru = reddit_user(guesses[0])
    report["reddit_kullanici"] = ru
    if "hata" not in ru:
        ok(f"oluşturma: {ru['oluşturma']} | link: {ru['link_karma']} | yorum: {ru['yorum_karma']}")
    rposts, rerr = reddit_search(name)
    report["reddit_gonderiler"] = {"hata": rerr, "sonuclar": rposts[:8]}
    for p in rposts[:8]:
        print(GREEN + f"    • r/{p['sub']} — {p['baslik'][:60]}" + RESET)

    info("[HACKERNEWS] aranıyor...")
    hn = {"yazar": [], "metin": []}
    hn["yazar"], _ = hn_search(tags="author_" + guesses[0], hitsPerPage=10)
    hn["metin"], _ = hn_search(query=name, hitsPerPage=10)
    report["hackernews"] = hn
    for x in hn["yazar"][:5]:
        print(GREEN + f"    • [yazar] {x['baslik'][:60]} — {x['url']}" + RESET)

    info("[INSTAGRAM] bulunan hesaplar derin taranıyor (canlı ID + konum)...")
    sess = get_active_session(ask=False)
    ig_targets = list(dict.fromkeys([guesses[0]] + list(profs["instagram"])))[:3]
    ig_res = {}
    for u in ig_targets:
        ig_res[u] = ig_deep_dive(u, sess["sessionid"] if sess else None, 20)
        time.sleep(2)
    report["instagram"] = ig_res
    for u, r in ig_res.items():
        if "hata" in r:
            hata(f"{u}: {r['hata'].get('detail', r['hata'])}")
            continue
        p = r["profile"]
        ok(f"{u} -> GERÇEK ID: {p['id']} | {p.get('full_name')} | private: {p.get('is_private')} | kaynak: {r['id_kaynak']}")
        for loc in r.get("locations", [])[:8]:
            ll = f"{loc['lat']}, {loc['lng']}" if loc["lat"] is not None else "koordinat yok"
            print(GREEN + f"      • KONUM: {loc['yer']} | {ll} | adres: {loc['adres']}" + RESET)

    info("[EMAIL] aday üretimi + MX kontrolü...")
    if first and last:
        domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"]
        emails = email_guesses(first, last, domains)
        report["email_adaylari"] = emails[:30]
        print(BLUE + "    Adaylar: " + ", ".join(emails[:20]) + RESET)
        for d in domains:
            mx = mx_lookup(d)
            print(GREEN + f"    MX {d}: {', '.join(mx) if mx else 'kayıt yok'}" + RESET)

    info("[DORK] Google/Bing için hazır sorgular:")
    for d in [f'"{name}"', f'"{name}" site:instagram.com', f'"{name}" site:linkedin.com',
              f'"{name}" site:github.com', f'"{name}" email OR telefon OR "e-posta"']:
        dork_links(d)

    fname = "osint_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    ok(f"JSON rapor kaydedildi: {fname}")
    db_kaydet("isim_taramasi", name, report)

def opt_email():
    line("=")
    print(GREEN + "  [4] EMAIL → ADAY + MX + SMTP DOĞRULAMA + TEST MAİLİ" + RESET)
    print(BLUE + "  (toplu istenmeyen mail/spam gönderimi YOKTUR —" + RESET)
    print(BLUE + "   yalnızca açıkça belirttiğiniz tek adrese test gönderilir)" + RESET)
    line("=")
    hedef = input(BLUE + "[?] Email adresi veya 'Ad Soyad': " + RESET).strip()
    if not hedef:
        return
    sonuclar = []
    if "@" in hedef:
        adres = hedef.strip()
        info(f"{adres} için MX + SMTP doğrulama...")
        dom = adres.split("@")[-1]
        mx = mx_lookup(dom)
        print(GREEN + f"    MX {dom}: {', '.join(mx) if mx else 'kayıt yok'}" + RESET)
        if mx:
            host = mx[0].split()[-1].rstrip(".")
            sonuc = smtp_validate(host, adres)
            ok(f"{sonuc['sonuc']} | {sonuc['yanit']}")
            sonuclar.append(sonuc)
        info("Web izi aranıyor...")
        for r in ddg_search(f'"{adres}"', 6):
            print(GREEN + f"    • {r['title'][:70]} — {r['url']}" + RESET)
        time.sleep(2.5)
    else:
        tokens = hedef.split()
        first, last = (tokens[0], tokens[-1]) if len(tokens) >= 2 else (tokens[0], "")
        extra = input(BLUE + "[?] Ek domainler (virgülle; boş = varsayılan): " + RESET).strip()
        domains = [d.strip() for d in extra.split(",") if d.strip()] or \
                  ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"]
        emails = email_guesses(first, last, domains)
        ok(f"{len(emails)} aday email üretildi:")
        print(BLUE + "    " + ", ".join(emails[:30]) + RESET)
        info("MX kayıtları kontrol ediliyor...")
        mxs = {}
        for d in set(domains):
            mxs[d] = mx_lookup(d)
            print(GREEN + f"    MX {d}: {', '.join(mxs[d]) if mxs[d] else 'kayıt yok'}" + RESET)
        info("SMTP RCPT TO ile ilk 10 aday doğrulanıyor (kullanıcı enumerasyonu)...")
        n = 0
        for adres in emails:
            dom = adres.split("@")[-1]
            if not mxs.get(dom):
                continue
            host = mxs[dom][0].split()[-1].rstrip(".")
            sonuc = smtp_validate(host, adres)
            ok(f"{adres:<40} {sonuc['sonuc']:<18} {sonuc['yanit'][:50]}")
            sonuclar.append(sonuc)
            n += 1
            if n >= 10:
                break
            time.sleep(0.3)
    db_kaydet("email", hedef, sonuclar)
    gonder = input(BLUE + "\n[?] Açıkça belirttiğiniz TEK adrese test maili gönderilsin mi? (adres / boş=hayır): " + RESET).strip()
    if "@" in gonder:
        info(f"{gonder} adresine test maili deneniyor...")
        print(GREEN + json.dumps(send_test_mail(gonder, "OSINT test", "Bu bir yetkili test mailidir."), ensure_ascii=False, indent=2) + RESET)

def opt_ip():
    line("=")
    print(GREEN + "  [5] IP ADRESİ → KONUM, ISP, RDAP, PTR" + RESET)
    line("=")
    ip = input(BLUE + "[?] IP adresi: " + RESET).strip()
    if not ip:
        return
    if is_private_ip(ip):
        hata("Özel/yerel adres — dışarıdan anlamlı veri yok.")
        return
    info("ip-api.com sorgulanıyor...")
    il = ip_lookup(ip)
    print(GREEN + "\n[+] IP bilgisi:" + RESET)
    print(GREEN + json.dumps(il, ensure_ascii=False, indent=2) + RESET)
    info("PTR (ters DNS) sorgulanıyor...")
    ptr = ptr_lookup(ip)
    print(GREEN + f"    {ptr}" + RESET)
    info("RDAP (kayıt sahibi / ağ) sorgulanıyor...")
    rdap = rdap_summary(ip)
    print(GREEN + json.dumps(rdap, ensure_ascii=False, indent=4) + RESET)
    db_kaydet("ip", ip, {"ip_api": il, "ptr": ptr, "rdap": rdap})

def opt_search():
    line("=")
    print(GREEN + "  [6] ARAMA MOTORU — CANLI DUCKDUCKGO + DORK LİNKLERİ" + RESET)
    line("=")
    q = input(BLUE + "[?] Arama sorgusu: " + RESET).strip()
    if not q:
        return
    info(f"DuckDuckGo'da aranıyor: {q}")
    res = ddg_search(q, 10)
    if res and res[0].get("blocked"):
        hata("DDG anomaly kiliti — 30-60 sn bekleyip tekrar deneyin.")
        return
    for i, r in enumerate(res, 1):
        print(GREEN + f"  {i}. {r['title'][:80]}" + RESET)
        print(BLUE + f"     {r['url']}" + RESET)
    db_kaydet("arama", q, res)
    info("Google/Bing dork linkleri:")
    dork_links(q)

def opt_domain():
    line("=")
    print(GREEN + "  [7] DOMAIN OSINT — DNS + WHOIS/RDAP + BAŞLIK" + RESET)
    line("=")
    d = input(BLUE + "[?] Alan adı (örn. ornek.com): " + RESET).strip()
    if not d:
        return
    d = re.sub(r"^https?://(www\.)?", "", d).strip("/").split("/")[0].lower()
    info("DNS kayıtları sorgulanıyor (Cloudflare DoH)...")
    dns = {}
    for tip in ("A", "AAAA", "MX", "NS", "TXT"):
        sonuc = dns_query(d, tip)
        dns[tip] = sonuc
        if sonuc:
            print(GREEN + f"    {tip:<5}: {', '.join(str(x) for x in sonuc[:6])}" + RESET)
        else:
            print(BLUE + f"    {tip:<5}: kayıt yok / yanıt yok" + RESET)
    info("RDAP WHOIS sorgulanıyor...")
    rdap = domain_rdap(d)
    print(GREEN + json.dumps(rdap, ensure_ascii=False, indent=4) + RESET)
    info("Site başlığı deneniyor...")
    st, _, data = http_get("https://" + d, timeout=12)
    m = re.search(rb"<title[^>]*>(.*?)</title>", data, re.S | re.I)
    baslik = m.group(1).decode("utf-8", "ignore").strip()[:80] if m else "-"
    if st in (200, 301, 302):
        print(GREEN + f"    HTTP {st} | başlık: {baslik}" + RESET)
    else:
        hata(f"HTTP {st} — site çekilemedi (bot engeli veya site kapalı olabilir).")
    db_kaydet("domain", d, {"dns": dns, "rdap": rdap, "http": st, "baslik": baslik})

def opt_url():
    line("=")
    print(GREEN + "  [8] URL GÜVENLİK ANALİZİ — REDIRECT + BAŞLIKLAR + SSL" + RESET)
    line("=")
    u = input(BLUE + "[?] URL (örn. https://ornek.com/path): " + RESET).strip()
    if not u:
        return
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    chain, st, rh, body = url_chain(u)
    info("Redirect zinciri:")
    for hop in chain:
        if hop.get("hata"):
            print(BLUE + f"    {hop['url']} -> hata: {hop['hata']}" + RESET)
        else:
            print(GREEN + f"    HTTP {hop['durum']}  {hop['url']}" + RESET)
    print(BLUE + f"    Son durum: HTTP {st}" + RESET)
    if body:
        m = re.search(rb"<title[^>]*>(.*?)</title>", body, re.S | re.I)
        print(GREEN + f"    Başlık: {m.group(1).decode('utf-8','ignore').strip()[:100] if m else '-'}" + RESET)
    info("Güvenlik başlıkları denetimi:")
    guv = {"strict-transport-security": "HSTS", "content-security-policy": "CSP",
           "x-frame-options": "X-Frame-Options", "x-content-type-options": "X-Content-Type-Options",
           "referrer-policy": "Referrer-Policy", "permissions-policy": "Permissions-Policy"}
    guv_sonuc = {}
    for k, ad in guv.items():
        guv_sonuc[ad] = bool(rh.get(k))
        if rh.get(k):
            print(GREEN + f"    ✓ {ad:<24} VAR" + RESET)
        else:
            print(BLUE + f"    ✗ {ad:<24} yok" + RESET)
    if rh.get("server"):
        print(GREEN + f"    server: {rh['server'][:80]}" + RESET)
    if rh.get("x-powered-by"):
        print(GREEN + f"    x-powered-by: {rh['x-powered-by'][:80]}" + RESET)
    host = urlparse(u).hostname or (chain[-1]["url"].split("/")[2] if chain else "")
    info("SSL sertifika bilgisi:")
    cert = ssl_cert_info(host)
    print(GREEN + json.dumps(cert, ensure_ascii=False, indent=2) + RESET)
    info("Çözümlenen IP:")
    ipinfo = {}
    try:
        ip = socket.gethostbyname(host)
        print(GREEN + f"    {ip}" + RESET)
        ipinfo = ip_lookup(ip)
        print(GREEN + json.dumps(ipinfo, ensure_ascii=False, indent=2) + RESET)
    except Exception as e:
        hata(str(e))
    db_kaydet("url", u, {"zincir": chain, "durum": st, "guvenlik": guv_sonuc, "ssl": cert, "ip": ipinfo})

def opt_ports():
    line("=")
    print(GREEN + "  [9] IP PORT TARAMASI — TCP CONNECT + BANNER" + RESET)
    line("=")
    hst = input(BLUE + "[?] Hedef IP/domain: " + RESET).strip()
    if not hst:
        return
    info(f"{hst} taranıyor ({len(COMMON_PORTS)} yaygın port)...")
    try:
        ip = socket.gethostbyname(hst)
    except Exception:
        ip = hst
    acik, banner = port_scan(ip)
    if not acik:
        hata("Açık port bulunamadı (hedef filtrelenmiş olabilir).")
        db_kaydet("port_taramasi", hst, {"acik_portlar": [], "banner": {}})
        return
    ok(f"Açık portlar ({len(acik)}): {', '.join(str(p) for p in acik)}")
    for p in acik[:12]:
        b = banner.get(p)
        print(GREEN + f"    {p:<6} {'banner: ' + b if b else ''}" + RESET)
    if len(acik) > 12:
        print(BLUE + f"    ... ve {len(acik) - 12} port daha" + RESET)
    db_kaydet("port_taramasi", hst, {"acik_portlar": acik, "banner": banner})

def opt_subdomains():
    line("=")
    print(GREEN + "  [10] ALT ALAN ADI KEŞFİ — crt.sh (SERTİFİKA ŞEFFAFLIĞI)" + RESET)
    line("=")
    d = input(BLUE + "[?] Alan adı (örn. ornek.com): " + RESET).strip()
    if not d:
        return
    d = re.sub(r"^https?://(www\.)?", "", d).strip("/").split("/")[0].lower()
    info(f"crt.sh'den sertifika geçmişi sorgulanıyor (30 sn sürebilir)...")
    subs, alive, err = crt_subdomains(d)
    if err:
        hata(str(err))
        return
    ok(f"{len(subs)} alt alan adı bulundu:")
    for s in subs[:40]:
        ip = alive.get(s, "")
        print(GREEN + f"    {s:<45} {ip}" + RESET)
    if len(subs) > 40:
        print(BLUE + f"    ... ve {len(subs) - 40} tane daha (ilk 60 çözümlendi)" + RESET)
    db_kaydet("alt_alan", d, {"alt_alanlar": subs, "canli_ip": alive})

def opt_mac():
    line("=")
    print(GREEN + "  [11] MAC ADRESİ → ÜRETİCİ (OUI)" + RESET)
    line("=")
    mac = input(BLUE + "[?] MAC adresi (örn. AA:BB:CC:DD:EE:FF): " + RESET).strip()
    if not mac:
        return
    info("maclookup.app sorgulanıyor...")
    sonuc = mac_lookup(mac)
    print(GREEN + json.dumps(sonuc, ensure_ascii=False, indent=2) + RESET)
    db_kaydet("mac", mac, sonuc)

def opt_cve():
    line("=")
    print(GREEN + "  [12] CVE / ZAFİYET ARAMA (cve.circl.lu)" + RESET)
    line("=")
    q = input(BLUE + "[?] Anahtar kelime veya CVE id (örn. openssh veya CVE-2024-6387): " + RESET).strip()
    if not q:
        return
    info(f"'{q}' aranıyor...")
    sonuc, err = cve_search(q)
    if err:
        hata(err)
        return
    if not sonuc:
        hata("Sonuç yok.")
        return
    ok(f"{len(sonuc)} kayıt bulundu (ilk 10 gösteriliyor):")
    for c in sonuc[:10]:
        cvss = c.get("cvss")
        cv = f"CVSS {cvss}" if cvss is not None else "CVSS -"
        tarih = (c.get("Published") or c.get("published") or "")[:10]
        ozet = (c.get("summary") or c.get("description") or "")[:150]
        print(GREEN + f"    • {c.get('id')} | {cv} | {tarih}")
        print(BLUE + f"      {ozet}" + RESET)
    db_kaydet("cve", q, sonuc[:10])

def opt_hash():
    line("=")
    print(GREEN + "  [13] HASH ANALİZİ + SIZINTI KONTROLÜ (pwnedpasswords)" + RESET)
    line("=")
    h = input(BLUE + "[?] Hash veya parola: " + RESET).strip()
    if not h:
        return
    tip = identify_hash(h)
    if tip:
        ok(f"Tespit edilen format: {tip}")
    else:
        print(BLUE + "    Format tanınamadı (düz parola olarak işleniyor)." + RESET)
    if re.fullmatch(r"[0-9a-fA-F]{40}", h):
        sha1 = h.lower()
    else:
        sha1 = hashlib.sha1(h.encode()).hexdigest().lower()
    info("Sızıntı veritabanı kontrolü (SHA-1 k-anonimlik, parola gönderilmez)...")
    cnt = pwned_count(sha1)
    if cnt is None:
        hata("pwnedpasswords API'ye ulaşılamadı.")
    elif cnt == 0:
        ok("Bu değer bilinen sızıntı veritabanlarında BULUNAMADI.")
    else:
        hata(f"UYARI: Bu değer sızıntı veritabanlarında {cnt} kez geçiyor — ele geçirilmiş bir parola olabilir!")
    db_kaydet("hash", h, {"format": tip, "sha1": sha1, "sizinti_sayisi": cnt})

def opt_emailrep():
    line("=")
    print(GREEN + "  [14] EMAIL REPÜTASYONU (emailrep.io)" + RESET)
    line("=")
    e = input(BLUE + "[?] Email adresi: " + RESET).strip()
    if not e:
        return
    info(f"{e} sorgulanıyor...")
    sonuc = emailrep(e)
    print(GREEN + json.dumps(sonuc, ensure_ascii=False, indent=2) + RESET)
    db_kaydet("email_rep", e, sonuc)

def opt_wayback():
    line("=")
    print(GREEN + "  [15] WAYBACK MAKİNESİ / ARŞİV KONTROLÜ" + RESET)
    line("=")
    u = input(BLUE + "[?] URL veya domain (örn. ornek.com): " + RESET).strip()
    if not u:
        return
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    info("En yakın arşiv anlık görüntüsü aranıyor...")
    snap = wayback_available(u)
    if snap:
        print(GREEN + f"    • {snap.get('timestamp')} — {snap.get('url')} (durum {snap.get('status')})" + RESET)
    else:
        hata("Bu URL için arşiv anlık görüntüsü yok.")
    domain = urlparse(u).hostname or u
    info(f"CDX geçmişi çekiliyor ({domain})...")
    rows, err = wayback_cdx(domain)
    if err:
        hata(str(err))
        return
    if not rows:
        hata("Arşiv geçmişi yok.")
        return
    ok(f"{len(rows)} snapshot (ilk 15):")
    for r in rows[:15]:
        ts, orig, st = r[0], r[1], r[2] if len(r) > 2 else ""
        tarih = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
        print(GREEN + f"    {tarih}  HTTP {st:<4} {orig[:70]}" + RESET)
    db_kaydet("wayback", u, {"snapshot": snap, "cdx": rows[:15]})

def opt_shodan():
    line("=")
    print(GREEN + "  [16] SHODAN SORGU — PORT + VULN (SHODAN_API_KEY gerekir)" + RESET)
    line("=")
    ip = input(BLUE + "[?] IP adresi: " + RESET).strip()
    if not ip:
        return
    if is_private_ip(ip):
        hata("Özel/yerel adres — Shodan'da anlamlı veri yok.")
        return
    info("Shodan sorgulanıyor...")
    sonuc = shodan_host(ip)
    print(GREEN + json.dumps(sonuc, ensure_ascii=False, indent=2) + RESET)
    db_kaydet("shodan", ip, sonuc)

def opt_ig_session():
    line("=")
    print(GREEN + "  [17] IG OTURUM YÖNETİMİ" + RESET)
    line("=")
    saved = load_ig_session()
    if saved:
        gecerli = ig_session_valid(saved["sessionid"])
        print(GREEN + f"    Durum: {'AKTİF' if gecerli else 'GEÇERSİZ'} (kullanıcı: {saved['username']})" + RESET)
    else:
        hata("Kayıtlı oturum yok.")
    sec = input(BLUE + "[?] [g]iriş / [ç]ıkış / [v]azgeç: " + RESET).strip().lower()
    if sec == "g":
        u = input(BLUE + "[?] IG kullanıcı adı: " + RESET).strip()
        p = getpass.getpass(BLUE + "[?] IG şifre: " + RESET)
        if not u or not p:
            hata("Boş giriş.")
            return
        sonuc = ig_login_flow(u, p)
        if sonuc and sonuc.get("sessionid"):
            save_ig_session(sonuc["sessionid"], u)
            ok(f"Oturum kaydedildi: {u}")
        else:
            hata(f"Giriş başarısız: {sonuc.get('hata') if sonuc else 'bilinmiyor'}")
    elif sec == "ç":
        delete_ig_session()
        ok("Oturum silindi.")

def opt_db():
    line("=")
    print(GREEN + "  [18] VERİTABANI — TARAMA GEÇMİŞİ (SQLite: ~/.markos_osint.db)" + RESET)
    line("=")
    sec = input(BLUE + "[?] [s]on kayıtlar / [h]edef listesi / [ö]zet / [t]emizle / [v]azgeç: " + RESET).strip().lower()
    if sec == "s":
        for rid, arac, hedef, zaman in db_son_kayitlar(20):
            print(GREEN + f"    #{rid:<4} {arac:<14} {hedef:<35} {zaman}" + RESET)
    elif sec == "h":
        for tip, deger, ilk, son in db_hedef_listesi():
            print(GREEN + f"    {tip:<14} {deger:<35} ilk: {ilk} son: {son}" + RESET)
    elif sec == "ö":
        ozet, top = db_ozet()
        ok("Araç bazında tarama sayısı:")
        for arac, cnt in ozet:
            print(GREEN + f"    {arac:<14} {cnt} kayıt" + RESET)
        ok("En çok taranan hedefler:")
        for hedef, cnt in top:
            print(GREEN + f"    {hedef:<35} {cnt} kez" + RESET)
    elif sec == "t":
        onay = input(BLUE + "[?] Tüm veritabanı silinsin mi? [e/h]: " + RESET).strip().lower()
        if onay == "e":
            db_temizle()
            ok("Veritabanı temizlendi.")
        else:
            hata("İptal.")
    else:
        hata("İptal.")

# ================================================================ ANA MENÜ
def main():
    if os.name == "nt":
        os.system("")
    db_init()
    banner()
    while True:
        try:
            secim = input(BLUE + "\n[?] Seçiminiz: " + RESET).strip()
        except (EOFError, KeyboardInterrupt):
            print(GREEN + "\n[+] Çıkılıyor. Markos İşletim Sistemi OSINT — iyi avlar." + RESET)
            break
        if secim == "0":
            print(GREEN + "\n[+] Çıkılıyor. Markos İşletim Sistemi OSINT — iyi avlar." + RESET)
            break
        elif secim == "1": opt_username()
        elif secim == "2": opt_phone()
        elif secim == "3": opt_name()
        elif secim == "4": opt_email()
        elif secim == "5": opt_ip()
        elif secim == "6": opt_search()
        elif secim == "7": opt_domain()
        elif secim == "8": opt_url()
        elif secim == "9": opt_ports()
        elif secim == "10": opt_subdomains()
        elif secim == "11": opt_mac()
        elif secim == "12": opt_cve()
        elif secim == "13": opt_hash()
        elif secim == "14": opt_emailrep()
        elif secim == "15": opt_wayback()
        elif secim == "16": opt_shodan()
        elif secim == "17": opt_ig_session()
        elif secim == "18": opt_db()
        else:
            hata("Geçersiz seçim.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(GREEN + "\n[+] Çıkılıyor. Markos İşletim Sistemi OSINT — iyi avlar." + RESET)
