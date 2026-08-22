#!/usr/bin/env python3
# ================================================================
# PATRONUM DELTA 007 MONOLİT - SQLite3 + GERÇEK UÇ NOKTALAR
# + Dahili Test Sunucusu (isteğe bağlı)
# ================================================================
# KULLANIM:
#   1. Production: export API_BASE_URL, AUTH_URL, CLIENT_ID, CLIENT_SECRET
#   2. Test:        python3 delta007.py --test        (kendi mock API'sini başlatır)
# ================================================================

import os
import sys
import json
import time
import re
import threading
import sqlite3
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Tuple

# ------------------------------------------------------------------
# Renklendirme (colorama opsiyonel)
# ------------------------------------------------------------------
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _Fake:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
        BRIGHT = DIM = NORMAL = ""
    Fore = Style = _Fake()

YESIL = Fore.GREEN
KIRMIZI = Fore.RED
MAVI = Fore.CYAN
SARI = Fore.YELLOW

DB_FILE = "delta007.db"
SCHEMA_VERSION = 2

# ================================================================
# SQLITE3 VERİTABANI
# ================================================================
class Database:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        return c

    def _init_db(self):
        c = self._conn()
        try:
            ver = 0
            try:
                r = c.execute("SELECT value FROM system_config WHERE key='schema_version'").fetchone()
                if r: ver = int(r["value"])
            except Exception:
                ver = 0

            if ver < SCHEMA_VERSION:
                c.executescript("""
                    DROP TABLE IF EXISTS profiles;
                    DROP TABLE IF EXISTS transactions;
                    DROP TABLE IF EXISTS system_config;
                """)
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
                    CREATE INDEX IF NOT EXISTS idx_tx_game ON transactions(game);
                    CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(status);
                    CREATE INDEX IF NOT EXISTS idx_tx_time ON transactions(created_at);
                """)
                for g, t, v in [("eFootball","Kullanıcı Kimliği",None),
                                ("PUBG Mobile","Oyuncu ID",None),
                                ("Brawl Stars","UserID",None)]:
                    c.execute("INSERT INTO profiles (game,identity_type,identity_value) VALUES (?,?,?)", (g,t,v))
                c.execute("INSERT OR REPLACE INTO system_config VALUES (?,?,CURRENT_TIMESTAMP)",("system_name","DELTA 007"))
                c.execute("INSERT OR REPLACE INTO system_config VALUES (?,?,CURRENT_TIMESTAMP)",("system_version","3.0-final"))
                c.execute("INSERT OR REPLACE INTO system_config VALUES (?,?,CURRENT_TIMESTAMP)",("schema_version",str(SCHEMA_VERSION)))
                c.commit()
                print(f"[DB] Şema v{ver} → v{SCHEMA_VERSION}")
            c.close()
        except sqlite3.OperationalError:
            c.close()
            os.remove(self.db_path)
            self._init_db()

    # Profiller
    def get_all_profiles(self) -> List[Dict]:
        c = self._conn(); r = c.execute("SELECT * FROM profiles ORDER BY game").fetchall(); c.close()
        return [dict(x) for x in r]
    def get_profile(self, game: str) -> Optional[Dict]:
        c = self._conn(); r = c.execute("SELECT * FROM profiles WHERE game=?", (game,)).fetchone(); c.close()
        return dict(r) if r else None
    def set_identity(self, game: str, val: str) -> bool:
        c = self._conn(); c.execute("UPDATE profiles SET identity_value=?,updated_at=CURRENT_TIMESTAMP WHERE game=?", (val,game)); c.commit(); ok = c.total_changes > 0; c.close(); return ok

    # İşlemler
    def add_transaction(self, d: Dict) -> int:
        c = self._conn()
        c.execute("""INSERT INTO transactions
            (transaction_id,game,recipient_identity,currency,amount,status,gateway,response_code,response_body,error_message)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (d.get("transaction_id"),d.get("game"),d.get("recipient_identity"),d.get("currency"),d.get("amount"),
             d.get("status","pending"),d.get("gateway"),d.get("response_code"),d.get("response_body"),d.get("error_message")))
        c.commit(); i=c.lastrowid; c.close(); return i
    def get_transactions(self, limit=50) -> List[Dict]:
        c = self._conn(); r = c.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall(); c.close()
        return [dict(x) for x in r]

    # Konfig
    def get_config(self, key: str) -> Optional[str]:
        c = self._conn(); r = c.execute("SELECT value FROM system_config WHERE key=?",(key,)).fetchone(); c.close()
        return r["value"] if r else None

db = Database()

# ================================================================
# LOG
# ================================================================
def log_i(m): print(MAVI+"[INFO] "+Fore.WHITE+m)
def log_ok(m): print(YESIL+"[OK] "+Fore.WHITE+m)
def log_w(m): print(SARI+"[WARN] "+Fore.WHITE+m)
def log_e(m): print(KIRMIZI+"[ERROR] "+Fore.WHITE+m)

# ================================================================
# KİMLİK DOĞRULAMA
# ================================================================
def val_identity(game:str, id_:str)->bool:
    id_=id_.strip()
    if game=="eFootball": return bool(re.fullmatch(r"[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{3}",id_.upper()))
    if game=="PUBG Mobile": return bool(re.fullmatch(r"[0-9]{5,20}",id_))
    if game=="Brawl Stars": return bool(re.fullmatch(r"#[A-Za-z0-9]{3,15}",id_))
    return False
def val_amount(s:str)->Optional[int]:
    try:
        a=int(s)
        return a if a>0 else None
    except: return None

# ================================================================
# OAUTH2 TOKEN YÖNETİMİ
# ================================================================
class OAuthToken:
    def __init__(self, auth_url:str, cid:str, csecret:str, scope:str=None, verify:bool=True, retry:int=3):
        self.url=auth_url; self.cid=cid; self.cs=csecret; self.scope=scope; self.v=verify; self.max=retry
        self._token=None; self._exp=0.0; self._lock=threading.Lock()
    def _fetch(self):
        p={"grant_type":"client_credentials","client_id":self.cid,"client_secret":self.cs}
        if self.scope: p["scope"]=self.scope
        b=1.0
        for a in range(1,self.max+1):
            try:
                r=requests.post(self.url,data=p,timeout=15,verify=self.v); r.raise_for_status()
                d=r.json(); t=d.get("access_token")
                if not t: raise RuntimeError("access_token yok")
                self._token=t; self._exp=time.time()+int(d.get("expires_in",3600))-60
                log_ok("Token alındı"); return
            except Exception as e:
                log_w(f"Token hatası ({a}/{self.max}): {e}")
                if a<self.max: time.sleep(b); b=min(b*2,30)
        raise RuntimeError("Token alınamadı")
    def get(self)->str:
        with self._lock:
            if not self._token or time.time()>=self._exp: self._fetch()
            return self._token

# ================================================================
# GERÇEK GATEWAY
# ================================================================
class Gateway:
    def __init__(self, base:str, auth:str, cid:str, cs:str, verify:bool=True):
        self.base=base.rstrip("/"); self.v=verify
        self.oauth=OAuthToken(auth,cid,cs,verify=verify)
        self.ses=requests.Session()
    def _hdr(self)->Dict:
        t=self.oauth.get()
        if not t: raise RuntimeError("Token alınamadı")
        return {"Authorization":f"Bearer {t}","Content-Type":"application/json","Accept":"application/json"}
    def _ep(self, game:str, gw:str=None)->str:
        g=(gw or "DEFAULT").upper()
        m={("PUBG Mobile","PUBG_OFFICIAL"):"/pubg/transfers",("PUBG Mobile","THIRD_PARTY"):"/transfers/pubg",
           ("PUBG Mobile","DEFAULT"):"/transfers/pubg",("eFootball","DEFAULT"):"/football/transfers",
           ("Brawl Stars","DEFAULT"):"/brawl/transfers"}
        p=m.get((game,g)) or m.get((game,"DEFAULT")) or "/transfers"
        return f"{self.base}{p}"
    def post(self, ep:str, payload:Dict, retry:tuple=(429,500,502,503,504), maxr:int=3, bb:float=1.0)->Dict:
        h=self._hdr()
        for a in range(1,maxr+1):
            try:
                r=self.ses.post(ep,json=payload,headers=h,timeout=20,verify=self.v)
                if r.ok: return {"status":"success","code":r.status_code,"response":r.json()}
                if r.status_code in retry and a<maxr:
                    time.sleep(bb*(2**(a-1))); continue
                return {"status":"error","code":r.status_code,"response":r.text[:2000]}
            except requests.Timeout:
                log_w(f"Timeout ({a}/{maxr})")
                if a<maxr: time.sleep(bb*(2**(a-1)))
                else: return {"status":"error","error":"Timeout"}
            except requests.ConnectionError as e:
                log_e(f"Bağlantı: {e}")
                if a<maxr: time.sleep(bb*(2**(a-1)))
                else: return {"status":"error","error":str(e)}
            except Exception as e:
                log_e(f"HTTP: {e}"); return {"status":"error","error":str(e)}
        return {"status":"error","error":"Denemeler tükendi"}
    def transfer(self, game:str, recv:str, cur:str, amt:int, dry:bool=True, gw:str=None)->Dict:
        if not amt or amt<=0: return {"status":"error","error":"Geçersiz miktar"}
        ep=self._ep(game,gw); p={"game":game,"recipient_identity":recv,"currency":cur,"amount":amt}
        if dry: return {"status":"dry_run","url":ep,"payload":p,"gateway":(gw or "DEFAULT").upper(),"message":"DRY RUN"}
        return self.post(ep,p)

# ================================================================
# ARAYÜZ
# ================================================================
def gw_build()->Gateway:
    b=os.environ.get("API_BASE_URL","").rstrip("/"); a=os.environ.get("AUTH_URL","").rstrip("/")
    cid=os.environ.get("CLIENT_ID",""); cs=os.environ.get("CLIENT_SECRET","")
    v=os.environ.get("VERIFY_TLS","true").lower() in ("1","true","yes","on")
    if not b: raise RuntimeError("API_BASE_URL eksik")
    if not a: raise RuntimeError("AUTH_URL eksik")
    if not cid or not cs: raise RuntimeError("CLIENT_ID/SECRET eksik")
    return Gateway(b,a,cid,cs,verify=v)

def tx_id()->str:
    return f"DELTA-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}-{os.urandom(4).hex().upper()}"

def exec_tx(game:str, recv:str, cur:str, amt:int, gw:str=None)->Dict:
    g=gw_build(); r=g.transfer(game,recv,cur,amt,dry=False,gateway=gw)
    tid=tx_id()
    db.add_transaction({"transaction_id":tid,"game":game,"recipient_identity":recv,"currency":cur,"amount":amt,
        "status":r.get("status","unknown"),"gateway":(gw or "DEFAULT").upper(),
        "response_code":r.get("code"),"response_body":json.dumps(r.get("response",{}),ensure_ascii=False)[:2000],
        "error_message":r.get("error")})
    return {"transaction_id":tid,**r}

def cls(): os.system("cls" if os.name=="nt" else "clear")

def banner():
    cls()
    B=r"""
██████╗ ███████╗██╗     ████████╗ █████╗ 
██╔══██╗██╔════╝██║     ╚══██╔══╝██╔══██╗
██║  ██║█████╗  ██║        ██║   ███████║
██║  ██║██╔══╝  ██║        ██║   ██╔══██║
██████╔╝███████╗███████╗   ██║   ██║  ██║
╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝

         [ DELTA 007 - SQLite3 ]
         [ PRODUCTION MONOLITH   ]
"""
    print(Fore.GREEN+B+Style.RESET_ALL if 'Style' in dir() else B)

def menu():
    print(f"\n{YESIL}[1]{Fore.WHITE} PUBG Mobile UC Transferi")
    print(f"{YESIL}[2]{Fore.WHITE} eFootball Coins Transferi")
    print(f"{YESIL}[3]{Fore.WHITE} Brawl Stars Elmas Transferi")
    print(f"{YESIL}[4]{Fore.WHITE} Kimlik Yönetimi")
    print(f"{YESIL}[5]{Fore.WHITE} Profiller")
    print(f"{YESIL}[6]{Fore.WHITE} İşlem Geçmişi")
    print(f"{YESIL}[7]{Fore.WHITE} Sistem Bilgisi")
    print(f"{YESIL}[0]{Fore.WHITE} Çıkış")

def show_profiles():
    for p in db.get_all_profiles():
        v=p["identity_value"] or "❌ Kayıtlı değil"
        print(f"  {p['game']:<15} | {p['identity_type']:<20} : {v}")

def show_sysinfo():
    print(f"  Adı  : {db.get_config('system_name')}")
    print(f"  Sürüm: {db.get_config('system_version')}")
    print(f"  DB   : {DB_FILE}")
    print(f"  API  : {os.environ.get('API_BASE_URL','AYARLANMAMIŞ')}")
    print(f"  TLS  : {os.environ.get('VERIFY_TLS','true')}")

def set_id():
    print("  1.eFootball  2.PUBG Mobile  3.Brawl Stars  0.İptal")
    c=input("  Oyun > ").strip()
    m={"1":"eFootball","2":"PUBG Mobile","3":"Brawl Stars"}
    g=m.get(c)
    if not g: return
    p=db.get_profile(g)
    if not p: log_e("Profil yok"); return
    cur=p.get("identity_value") or "(boş)"
    print(f"  {g} - {p['identity_type']} [mevcut: {cur}]")
    y=input(f"  Yeni {p['identity_type']}: ").strip()
    if not y: return
    if not val_identity(g,y):
        log_e("Geçersiz format"); return
    if db.set_identity(g,y): log_ok(f"Güncellendi → {y}")
    else: log_e("Güncellenemedi")

def show_hist():
    t=db.get_transactions(20)
    if not t: print("  İşlem yok"); return
    for x in t:
        i="✅" if x["status"]=="success" else "❌" if x["status"]=="error" else "⏳"
        print(f"\n  {i} {x['transaction_id']}")
        print(f"     {x['game']} | {x['recipient_identity']} | {x['amount']} {x['currency']}")
        print(f"     Durum: {x['status']} | Kod: {x['response_code'] or '-'} | {x['created_at']}")

def do_tx(game:str, cur:str):
    p=db.get_profile(game); dflt=p["identity_value"] if p else None
    print(f"\n╔══ {game} - {cur} ═══╗")
    pr=f"  Alıcı {p['identity_type'] if p else 'Identity'}"
    if dflt: pr+=f" [Enter={dflt}]"
    rec=input(pr+": ").strip()
    if not rec:
        if dflt: rec=dflt; log_i(f"Varsayılan: {rec}")
        else: log_e("Kimlik gerekli"); return
    if not val_identity(game,rec): log_e("Geçersiz kimlik"); return
    a=input(f"  Miktar ({cur}): ").strip(); amt=val_amount(a)
    if not amt: log_e("Geçersiz miktar"); return
    print(f"\n  {game} | {rec} | {amt} {cur}")
    if input("  Onay (e/E): ").strip().lower() not in ("e","evet","yes","y","1"): log_w("İptal"); return
    log_i("İşlem başlıyor...")
    try:
        r=exec_tx(game,rec,cur,amt)
        print(f"  ID: {r.get('transaction_id','-')} | Durum: {r.get('status')}")
        if r.get("status")=="success": log_ok("Başarılı!")
        elif r.get("status")=="error": log_e(f"Hata HTTP {r.get('code','?')}: {r.get('response','')[:300]} {r.get('error','')}")
        else: print(json.dumps(r,indent=2,ensure_ascii=False)[:500])
    except Exception as e:
        log_e(str(e))

# ================================================================
# DAHİLİ TEST SUNUCUSU (isteğe bağlı)
# ================================================================
def run_test_server():
    """Flask olmadan, basit bir HTTP test sunucusu."""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
    except ImportError:
        log_e("Test sunucusu için gerekli modül yok")
        sys.exit(1)

    class MockHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try: data = json.loads(body)
            except: data = {}

            # OAuth2 token endpoint'i
            if "/oauth2/token" in self.path:
                resp = {"access_token": "mock-token-" + uuid.uuid4().hex, "expires_in": 3600, "token_type": "Bearer"}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode())
                return

            # Transfer endpoint'leri
            amount = data.get("amount", 0)
            game = data.get("game", "unknown")
            recipient = data.get("recipient_identity", "unknown")
            currency = data.get("currency", "UC")

            # Başarılı transfer mock'u
            resp = {
                "status": "completed",
                "transaction_id": "MOCK-" + uuid.uuid4().hex.upper(),
                "game": game,
                "recipient": recipient,
                "currency": currency,
                "amount": amount,
                "message": f"{amount} {currency} başarıyla {recipient} hesabına gönderildi."
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())

        def log_message(self, format, *args):
            log_i(f"[Mock API] {args[0]} {args[1]} {args[2]}")

    # Rastgele port bul
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    server = HTTPServer(("127.0.0.1", port), MockHandler)
    log_ok(f"Test API sunucusu http://127.0.0.1:{port}")
    log_i("PID: " + str(os.getpid()))

    # Ortam değişkenlerini mock API'ye yönlendir
    os.environ["API_BASE_URL"] = f"http://127.0.0.1:{port}"
    os.environ["AUTH_URL"] = f"http://127.0.0.1:{port}/oauth2/token"
    os.environ["CLIENT_ID"] = "test-client"
    os.environ["CLIENT_SECRET"] = "test-secret"
    os.environ["VERIFY_TLS"] = "false"

    # Sunucuyu arka planda başlat
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    log_ok("Test API hazır. Menüye dönülüyor...")

# ================================================================
# MAIN
# ================================================================
def main():
    # Test modu kontrolü
    if "--test" in sys.argv:
        run_test_server()

    banner()
    log_i("DELTA 007 başlatıldı. Tüm işlemler gerçek API'ye gider.")
    if "--test" in sys.argv:
        log_i("TEST MODU - Dahili mock API kullanılıyor.")

    while True:
        menu()
        c = input(f"\n{Fore.BLUE}DELTA-007 > {Fore.WHITE}").strip().lower()

        if c in ("0","exit","quit","çıkış"): log_i("Kapanıyor..."); time.sleep(0.3); sys.exit(0)
        elif c in ("1","pubg","pubg uc","uc"): do_tx("PUBG Mobile","UC")
        elif c in ("2","ef","efootball","coins"): do_tx("eFootball","Coins")
        elif c in ("3","bs","brawl","brawl stars","elmas"): do_tx("Brawl Stars","Elmas")
        elif c in ("4","kimlik","identity","profil"): set_id()
        elif c in ("5","profiller","show"): show_profiles(); input("\nEnter...")
        elif c in ("6","history","geçmiş","gecmis","geçmiş"): show_hist(); input("\nEnter...")
        elif c in ("7","sistem","info","bilgi"): show_sysinfo(); input("\nEnter...")
        elif c in ("help","yardim"): menu()
        else: log_w("Geçersiz seçim (0-7)")

# ================================================================
# ENTRY
# ================================================================
if __name__ == "__main__":
    # Test modu: ortam değişkenleri gerekmez
    if "--test" in sys.argv:
        main()
        sys.exit(0)

    # Production modu: ortam değişkenleri kontrolü
    req = ["API_BASE_URL","AUTH_URL","CLIENT_ID","CLIENT_SECRET"]
    miss = [v for v in req if v not in os.environ or not os.environ[v].strip()]
    if miss:
        log_e("EKSİK ORTAM DEĞİŞKENLERİ: " + ", ".join(miss))
        print("\n  Production için export edin:")
        print("  export API_BASE_URL=\"https://api.production.com\"")
        print("  export AUTH_URL=\"https://auth.production.com/oauth2/token\"")
        print("  export CLIENT_ID=\"your_client_id\"")
        print("  export CLIENT_SECRET=\"your_client_secret\"")
        print("  export VERIFY_TLS=true")
        print("\n  Test için --test parametresiyle çalıştırın:")
        print("  python3 delta007.py --test")
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print(); log_i("Sonlandırıldı"); sys.exit(0)
