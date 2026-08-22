#!/usr/bin/env python3
# ============================================================================
# DELTA 007 MONOLITH v4.0 - ZERO DEPENDENCY PRODUCTION
# ============================================================================
# Hiçbir external kütüphane kullanmaz. Sadece Python stdlib:
#   urllib.request + ssl (gerçek HTTP/TCP/socket)
#   sqlite3 (gerçek veritabanı)
#   uuid, json, re, threading, os, sys, time, datetime
# ============================================================================
# KULLANIM:
#   export API_BASE_URL="https://api.sirketin.com"
#   export AUTH_URL="https://auth.sirketin.com/oauth2/token"
#   export CLIENT_ID="..."
#   export CLIENT_SECRET="..."
#   python3 delta007.py
# ============================================================================

import os
import sys
import json
import time
import re
import ssl
import uuid
import queue
import threading
import sqlite3
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

# --------------------------------------------------------------------------
# Renkli çıktı (opsiyonel - yoksa düz çalışır)
# --------------------------------------------------------------------------
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _F_: RED=GREEN=YELLOW=BLUE=CYAN=MAGENTA=WHITE=RESET=""
    Fore=Style=_F_()

G = Fore.GREEN; R = Fore.RED; C = Fore.CYAN; Y = Fore.YELLOW

DB_FILE = "delta007.db"
SCHEMA_VER = 2

# ============================================================================
# SQLITE3 VERITABANI (Python stdlib - gerçek)
# ============================================================================
class Database:
    def __init__(self):
        self.db_path = DB_FILE
        self._init()

    def _baglan(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        return c

    def _init(self):
        c = self._baglan()
        try:
            ver = 0
            try:
                r = c.execute("SELECT value FROM system_config WHERE key='schema_version'").fetchone()
                if r: ver = int(r["value"])
            except Exception:
                ver = 0

            if ver < SCHEMA_VER:
                c.executescript("DROP TABLE IF EXISTS profiles; DROP TABLE IF EXISTS transactions; DROP TABLE IF EXISTS system_config;")
                c.executescript("""
                    CREATE TABLE profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game TEXT NOT NULL UNIQUE,
                        identity_type TEXT NOT NULL,
                        identity_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id TEXT NOT NULL UNIQUE,
                        game TEXT NOT NULL,
                        recipient_identity TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        gateway TEXT,
                        response_code INTEGER,
                        response_body TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE system_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX idx_tx_game ON transactions(game);
                    CREATE INDEX idx_tx_status ON transactions(status);
                    CREATE INDEX idx_tx_time ON transactions(created_at);
                """)
                for g, t, v in [("eFootball","Kullanıcı Kimliği",None), ("PUBG Mobile","Oyuncu ID",None), ("Brawl Stars","UserID",None)]:
                    c.execute("INSERT INTO profiles(game,identity_type,identity_value) VALUES(?,?,?)", (g,t,v))
                c.execute("INSERT OR REPLACE INTO system_config VALUES('system_name','DELTA 007',CURRENT_TIMESTAMP)")
                c.execute("INSERT OR REPLACE INTO system_config VALUES('system_version','4.0-stdlib',CURRENT_TIMESTAMP)")
                c.execute("INSERT OR REPLACE INTO system_config VALUES('schema_version',?,CURRENT_TIMESTAMP)", (str(SCHEMA_VER),))
                c.commit()
                print(f"[DB] Şema v{ver} -> v{SCHEMA_VER}")
            c.close()
        except sqlite3.OperationalError:
            c.close()
            if os.path.exists(self.db_path): os.remove(self.db_path)
            self._init()

    def profilleri_getir(self) -> List[Dict]:
        c = self._baglan()
        r = c.execute("SELECT * FROM profiles ORDER BY game").fetchall()
        c.close(); return [dict(x) for x in r]

    def profil_getir(self, game: str) -> Optional[Dict]:
        c = self._baglan()
        r = c.execute("SELECT * FROM profiles WHERE game=?", (game,)).fetchone()
        c.close(); return dict(r) if r else None

    def kimlik_ayarla(self, game: str, val: str) -> bool:
        c = self._baglan()
        c.execute("UPDATE profiles SET identity_value=?, updated_at=CURRENT_TIMESTAMP WHERE game=?", (val, game))
        c.commit(); ok = c.total_changes > 0; c.close(); return ok

    def islem_ekle(self, d: Dict) -> int:
        c = self._baglan()
        c.execute("""INSERT INTO transactions
            (transaction_id,game,recipient_identity,currency,amount,status,gateway,response_code,response_body,error_message)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (d["transaction_id"], d["game"], d["recipient_identity"], d["currency"], d["amount"],
             d["status"], d["gateway"], d["response_code"], d["response_body"], d["error_message"]))
        c.commit(); i = c.lastrowid; c.close(); return i

    def islemleri_getir(self, limit=50) -> List[Dict]:
        c = self._baglan()
        r = c.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        c.close(); return [dict(x) for x in r]

    def config_getir(self, key: str) -> Optional[str]:
        c = self._baglan()
        r = c.execute("SELECT value FROM system_config WHERE key=?", (key,)).fetchone()
        c.close(); return r["value"] if r else None

db = Database()

# ============================================================================
# LOG
# ============================================================================
def log_i(m): print(C + "[INFO] " + Fore.WHITE + m)
def log_ok(m): print(G + "[OK]   " + Fore.WHITE + m)
def log_w(m): print(Y + "[WARN] " + Fore.WHITE + m)
def log_e(m): print(R + "[ERROR] " + Fore.WHITE + m)

# ============================================================================
# KIMLIK DOGRULAMA
# ============================================================================
def kimlik_dogrula(game: str, kimlik: str) -> bool:
    k = kimlik.strip()
    if game == "eFootball":     return bool(re.fullmatch(r"[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}", k.upper()))
    if game == "PUBG Mobile":   return bool(re.fullmatch(r"[0-9]{5,20}", k))
    if game == "Brawl Stars":   return bool(re.fullmatch(r"#[A-Za-z0-9]{3,15}", k))
    return False

def miktar_dogrula(s: str) -> Optional[int]:
    try:
        a = int(s); return a if a > 0 else None
    except: return None

def cls(): os.system("cls" if os.name == "nt" else "clear")

# ============================================================================
# GERÇEK HTTP ISTEKLERI (urllib - Python stdlib, gerçek TCP/socket/SSL)
# ============================================================================
def http_post(url: str, data: dict, headers: dict, timeout: int = 20,
              verify_tls: bool = True, max_retry: int = 3) -> Dict:
    """
    Saf Python stdlib ile gerçek HTTP POST.
    urllib.request -> gerçek TCP socket -> gerçek SSL/TLS.
    """

    json_bytes = json.dumps(data).encode("utf-8")

    # SSL context
    ctx = ssl.create_default_context()
    if not verify_tls:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    backoff = 1.0
    for d in range(1, max_retry + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                body = resp.read().decode("utf-8")
                code = resp.getcode()
                try:
                    jbody = json.loads(body)
                except:
                    jbody = body
                return {"status": "success", "code": code, "response": jbody}

        except urllib.error.HTTPError as e:
            code = e.code
            try:
                err_body = e.read().decode("utf-8")[:2000]
            except:
                err_body = str(e)
            # Rate limit veya 5xx ise retry
            if code in (429, 500, 502, 503, 504) and d < max_retry:
                log_w(f"HTTP {code} - {backoff}s sonra yeniden deneniyor ({d}/{max_retry})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
                continue
            return {"status": "error", "code": code, "response": err_body}

        except urllib.error.URLError as e:
            # DNS hatası, bağlantı reddi, timeout vs.
            if isinstance(e.reason, TimeoutError) or "timed out" in str(e.reason).lower():
                log_w(f"Timeout ({d}/{max_retry})")
                if d < max_retry:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue
                return {"status": "error", "error": "Zaman aşımı"}
            else:
                log_e(f"Bağlantı hatası: {e.reason}")
                if d < max_retry:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue
                return {"status": "error", "error": str(e.reason)}

        except Exception as e:
            log_e(f"HTTP hatası: {e}")
            return {"status": "error", "error": str(e)}

    return {"status": "error", "error": "Denemeler tükendi"}

# ============================================================================
# OAUTH2 TOKEN YONETIMI (Client Credentials - gerçek HTTP ile)
# ============================================================================
class OAuth2TokenYonetici:
    def __init__(self, auth_url: str, client_id: str, client_secret: str,
                 scope: str = None, verify_tls: bool = True, max_retry: int = 3):
        self.url = auth_url
        self.cid = client_id
        self.cs = client_secret
        self.scope = scope
        self.verify = verify_tls
        self.max = max_retry
        self._token = None
        self._son = 0.0
        self._kilit = threading.Lock()

    def _al(self):
        payload = {"grant_type": "client_credentials", "client_id": self.cid, "client_secret": self.cs}
        if self.scope: payload["scope"] = self.scope
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        body = urllib.parse.urlencode(payload).encode("utf-8")

        ctx = ssl.create_default_context()
        if not self.verify:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        bekle = 1.0
        for d in range(1, self.max + 1):
            try:
                req = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                    j = json.loads(r.read().decode("utf-8"))
                    t = j.get("access_token")
                    if not t: raise RuntimeError("access_token dönmedi")
                    self._token = t
                    self._son = time.time() + int(j.get("expires_in", 3600)) - 60
                    log_ok("OAuth2 token alındı")
                    return
            except Exception as e:
                log_w(f"Token hatası ({d}/{self.max}): {e}")
                if d < self.max:
                    time.sleep(bekle)
                    bekle = min(bekle * 2, 30)
        raise RuntimeError("OAuth2 token alınamadı!")

    def token_getir(self) -> str:
        with self._kilit:
            if not self._token or time.time() >= self._son:
                self._al()
            return self._token

# ============================================================================
# GERCEK API GATEWAY (sadece stdlib)
# ============================================================================
class GercekGateway:
    def __init__(self, base_url: str, auth_url: str, client_id: str,
                 client_secret: str, verify_tls: bool = True):
        self.base = base_url.rstrip("/")
        self.verify = verify_tls
        self.oauth = OAuth2TokenYonetici(auth_url, client_id, client_secret, verify_tls=verify_tls)
        self._header_cache = None
        self._header_lock = threading.Lock()

    def _header(self) -> Dict:
        with self._header_lock:
            t = self.oauth.token_getir()
            return {
                "Authorization": f"Bearer {t}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

    def _endpoint(self, game: str, gateway: str = None) -> str:
        g = (gateway or "DEFAULT").upper()
        mp = {
            ("PUBG Mobile", "PUBG_OFFICIAL"): "/pubg/transfers",
            ("PUBG Mobile", "THIRD_PARTY"):   "/transfers/pubg",
            ("PUBG Mobile", "DEFAULT"):       "/transfers/pubg",
            ("eFootball", "DEFAULT"):         "/football/transfers",
            ("Brawl Stars", "DEFAULT"):       "/brawl/transfers",
        }
        p = mp.get((game, g)) or mp.get((game, "DEFAULT")) or "/transfers"
        return f"{self.base}{p}"

    def transfer(self, game: str, alici: str, currency: str, miktar: int,
                 gateway: str = None, max_retry: int = 3) -> Dict:
        ep = self._endpoint(game, gateway)
        payload = {"game": game, "recipient_identity": alici, "currency": currency, "amount": miktar}
        headers = self._header()
        log_i(f"POST {ep} | {game} | {alici} | {miktar} {currency}")
        return http_post(ep, payload, headers, verify_tls=self.verify, max_retry=max_retry)

# ============================================================================
# ISLEM YURUTUCU
# ============================================================================
def gateway_olustur() -> GercekGateway:
    b = os.environ["API_BASE_URL"].rstrip("/")
    a = os.environ["AUTH_URL"].rstrip("/")
    cid = os.environ["CLIENT_ID"]
    cs = os.environ["CLIENT_SECRET"]
    v = os.environ.get("VERIFY_TLS", "true").lower() in ("1", "true", "yes", "on")
    return GercekGateway(b, a, cid, cs, verify_tls=v)

def islem_id_uret() -> str:
    return f"DELTA-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}-{os.urandom(4).hex().upper()}"

def transfer_ve_kaydet(game: str, alici: str, currency: str, miktar: int, gateway: str = None) -> Dict:
    gw = gateway_olustur()
    sonuc = gw.transfer(game, alici, currency, miktar, gateway=gateway)
    tid = islem_id_uret()
    kayit = {
        "transaction_id": tid,
        "game": game,
        "recipient_identity": alici,
        "currency": currency,
        "amount": miktar,
        "status": sonuc.get("status", "unknown"),
        "gateway": (gateway or "DEFAULT").upper(),
        "response_code": sonuc.get("code"),
        "response_body": json.dumps(sonuc.get("response", {}), ensure_ascii=False)[:2000],
        "error_message": sonuc.get("error"),
    }
    db.islem_ekle(kayit)
    log_ok(f"İşlem kaydedildi: {tid}")
    return {"transaction_id": tid, **sonuc}

# ============================================================================
# KONSOL ARAYÜZÜ
# ============================================================================
def banner_goster():
    cls()
    B = r"""
██████╗ ███████╗██╗     ████████╗ █████╗
██╔══██╗██╔════╝██║     ╚══██╔══╝██╔══██╗
██║  ██║█████╗  ██║        ██║   ███████║
██║  ██║██╔══╝  ██║        ██║   ██╔══██║
██████╔╝███████╗███████╗   ██║   ██║  ██║
╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝

       [ DELTA 007 v4.0 - ZERO DEPENDENCY ]
       [ REAL ENDPOINTS - NO SIMULATION    ]
"""
    print(Fore.GREEN + B + (Style.RESET_ALL if 'Style' in dir() else ""))

def menu_goster():
    print(f"\n{G}[1]{Fore.WHITE} PUBG Mobile UC Transferi")
    print(f"{G}[2]{Fore.WHITE} eFootball Coins Transferi")
    print(f"{G}[3]{Fore.WHITE} Brawl Stars Elmas Transferi")
    print(f"{G}[4]{Fore.WHITE} Kimlik Yönetimi")
    print(f"{G}[5]{Fore.WHITE} Profilleri Görüntüle")
    print(f"{G}[6]{Fore.WHITE} İşlem Geçmişi")
    print(f"{G}[7]{Fore.WHITE} Sistem Bilgisi")
    print(f"{G}[0]{Fore.WHITE} Çıkış")

def profilleri_goster():
    for p in db.profilleri_getir():
        v = p["identity_value"] or "❌ Kayıtlı değil"
        print(f"  {p['game']:<15} | {p['identity_type']:<20} : {v}")

def sistem_bilgisi():
    print(f"  Sistem : {db.config_getir('system_name')} {db.config_getir('system_version')}")
    print(f"  Veritabanı : {DB_FILE} (SQLite3 - Python stdlib)")
    print(f"  HTTP       : urllib.request (Python stdlib - gerçek socket/TCP/TLS)")
    print(f"  API Base   : {os.environ.get('API_BASE_URL','?')}")
    print(f"  TLS        : {os.environ.get('VERIFY_TLS','true')}")
    print(f"  Dependency : ZERO external - sadece Python standart kütüphanesi")

def kimlik_ayarla():
    print("  1. eFootball  2. PUBG Mobile  3. Brawl Stars  0. İptal")
    s = input("  Oyun > ").strip()
    mp = {"1": "eFootball", "2": "PUBG Mobile", "3": "Brawl Stars"}
    g = mp.get(s)
    if not g: return
    p = db.profil_getir(g)
    if not p: log_e("Profil bulunamadı"); return
    mevcut = p.get("identity_value") or "(boş)"
    print(f"  {g} - {p['identity_type']} [mevcut: {mevcut}]")
    y = input(f"  Yeni {p['identity_type']}: ").strip()
    if not y: return
    if not kimlik_dogrula(g, y): log_e("Geçersiz format"); return
    if db.kimlik_ayarla(g, y): log_ok(f"Güncellendi -> {y}")
    else: log_e("Güncellenemedi")

def islem_gecmisi():
    islemler = db.islemleri_getir(20)
    if not islemler: print("  İşlem yok."); return
    for x in islemler:
        ik = "✅" if x["status"] == "success" else "❌" if x["status"] == "error" else "⏳"
        print(f"\n  {ik} {x['transaction_id']}")
        print(f"     {x['game']} | {x['recipient_identity']} | {x['amount']} {x['currency']}")
        print(f"     Durum: {x['status']} | Kod: {x['response_code'] or '-'} | {x['created_at']}")

def transfer_yap(game: str, currency: str):
    p = db.profil_getir(game)
    varsayilan = p["identity_value"] if p else None

    print(f"\n╔══ {game} - {currency} ═══╗")
    sor = f"  Alıcı {p['identity_type'] if p else 'Identity'}"
    if varsayilan: sor += f" [Enter = {varsayilan}]"
    alici = input(sor + ": ").strip()
    if not alici:
        if varsayilan: alici = varsayilan; log_i(f"Varsayılan: {alici}")
        else: log_e("Kimlik gerekli"); return
    if not kimlik_dogrula(game, alici): log_e("Geçersiz kimlik formatı"); return

    m = input(f"  Miktar ({currency}): ").strip()
    miktar = miktar_dogrula(m)
    if not miktar: log_e("Geçersiz miktar"); return

    print(f"\n  {game} | {alici} | {miktar} {currency}")
    if input("  Onay (e/E): ").strip().lower() not in ("e", "evet", "yes", "y", "1"):
        log_w("İptal edildi"); return

    log_i("GERÇEK API transferi başlatılıyor...")
    try:
        r = transfer_ve_kaydet(game, alici, currency, miktar)
        print(f"\n  ID    : {r.get('transaction_id', '-')}")
        print(f"  Durum : {r.get('status')}")
        if r.get("status") == "success":
            log_ok(f"{miktar} {currency} başarıyla transfer edildi!")
            if isinstance(r.get("response"), dict):
                print(f"  Yanıt: {json.dumps(r['response'], indent=2, ensure_ascii=False)[:500]}")
        elif r.get("status") == "error":
            log_e(f"HTTP {r.get('code', '?')}")
            if r.get("response"): print(f"  Sunucu: {str(r['response'])[:300]}")
            if r.get("error"):    print(f"  Hata  : {r['error']}")
        else:
            print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        log_e(f"Sistem hatası: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# ANA DONGU
# ============================================================================
def main():
    banner_goster()
    log_i("DELTA 007 PRODUCTION MODE")
    log_i("  HTTP: urllib.request (gerçek TCP/socket/SSL)")
    log_i("  DB  : SQLite3 (gerçek veritabanı)")
    log_i("  Dep : Sıfır external kütüphane")
    log_i(f"  API : {os.environ.get('API_BASE_URL', '?')}")

    while True:
        menu_goster()
        s = input(f"\n{Fore.BLUE}DELTA-007 > {Fore.WHITE}").strip().lower()

        if s in ("0","exit","quit","çıkış"): log_i("Kapanıyor..."); time.sleep(0.3); sys.exit(0)
        elif s in ("1","pubg","pubg uc","uc"): transfer_yap("PUBG Mobile", "UC")
        elif s in ("2","ef","efootball","coins"): transfer_yap("eFootball", "Coins")
        elif s in ("3","bs","brawl","brawl stars","elmas"): transfer_yap("Brawl Stars", "Elmas")
        elif s in ("4","kimlik","identity","profil"): kimlik_ayarla()
        elif s in ("5","profiller","show"): profilleri_goster(); input("\nEnter...")
        elif s in ("6","history","geçmiş","gecmis"): islem_gecmisi(); input("\nEnter...")
        elif s in ("7","sistem","info","bilgi"): sistem_bilgisi(); input("\nEnter...")
        else: log_w("Geçersiz seçim (0-7)")

# ============================================================================
# GIRIS NOKTASI
# ============================================================================
if __name__ == "__main__":
    gerekli = ["API_BASE_URL", "AUTH_URL", "CLIENT_ID", "CLIENT_SECRET"]
    eksik = [v for v in gerekli if v not in os.environ or not os.environ[v].strip()]

    if eksik:
        log_e("EKSİK ORTAM DEĞİŞKENLERİ: " + ", ".join(eksik))
        print("""
  KULLANIM:
    export API_BASE_URL="https://api.sirketin.com"
    export AUTH_URL="https://auth.sirketin.com/oauth2/token"
    export CLIENT_ID="musteri_client_id"
    export CLIENT_SECRET="musteri_client_secret"
    export VERIFY_TLS="true"
    python3 delta007.py
        """)
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print(); log_i("Kullanıcı tarafından sonlandırıldı."); sys.exit(0)
