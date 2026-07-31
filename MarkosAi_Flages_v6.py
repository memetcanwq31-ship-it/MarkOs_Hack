#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║  MarkOsAi_6.0 — GELİŞMİŞ AI PENTEST ASİSTANI (Termux + GitHub)      ║
║  Yetkili güvenlik testleri / eğitim amaçlıdır                       ║
║  Sıfır harici bağımlılık — sadece Python standart kütüphanesi       ║
╚══════════════════════════════════════════════════════════════════════╝

YENİ ÖZELLİKLER:
  • 46 konu bilgi tabanı, kök (stem) eşleştirme + fuzzy
  • ÇOKLU AI MOTORU: yerel motor → Ollama → Gemini → Pollinations (ücretsiz LLM)
  • AI yanıt önbelleği → tekrar sorunca anında cevap (sınırsız hissi)
  • Konuşma bağlamı: "devam", "detaylandır", "peki"
  • öğret <soru> => <cevap> → bilgi tabanını kendin büyüt
  • Notlar, istatistik, şiir/hikaye/şaka/söz, hesap makinesi
  • !komut → Termux içinden gerçek komut çalıştırma (yıkıcı komut onayı ile)
  • 38+ kod üretici (LHOST/LPORT otomatik doldurma)
  • Şifre korumalı web modu, mobil uyumlu arayüz
  • -q "soru" tek soruluk mod, --offline, --update (git pull)

KULLANIM:
  python3 markosai.py                  → sohbet modu (sınırsız)
  python3 markosai.py --web --web-pass sifre123
  python3 markosai.py -q "jwt nasıl kırılır"
  python3 markosai.py --offline        → internet istemez
  python3 markosai.py --update         → git pull (GitHub'dan güncelle)

SOHBET KOMUTLARI:
  help | history | istatistik | notlar | clear | exit
  kod üret <konu> | plan <konu> | araç <konu>
  öğret <soru> => <cevap> | not al <metin> | not sil <id>
  şiir yaz <konu> | hikaye yaz <konu> | şaka | söz üret | hesapla 2+2
  ai: <soru> (online AI zorla) | yerel: <soru> | !<komut> (Termux komutu)
"""

import os
import sys
import re
import time
import json
import random
import hashlib
import argparse
import threading
import subprocess
import socket
import urllib.parse
import urllib.request
from datetime import datetime

try:
    import readline  # Termux'ta da input geçmişi (opsiyonel)
except Exception:
    pass

# ═══════════════════════════ RENKLER ═══════════════════════════
R = "\033[0m"; B = "\033[1m"
RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"

SYS = ("Sen MarkOsAi'sin - yetkili güvenlik testleri, siber güvenlik eğitimi ve genel sohbet için "
       "Türkçe konuşan bir AI asistanısın. Net, kısa, uygulanabilir cevaplar ver. Kod istenirse "
       "çalışan kod örneği ver. Güvenlik konularında hem saldırı hem savunma açısını dengeli anlat. "
       "Sorulara samimi ve teknik cevap ver. Yanıtlarını Türkçe yaz.")

DANGER = re.compile(r"\brm\s+-rf\s+/\b|\bmkfs\b|\bdd\s+if=.*of=/dev/|\b(?:shutdown|reboot|poweroff|init\s+0)\b|\b:\(\)\s*\{", re.I)

def cprint(text, color=R, bold=False):
    print(f"{B if bold else ''}{color}{text}{R}")

def loading(text="İşleniyor", dur=0.15):
    for _ in range(2):
        for ch in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
            print(f"\r{BLUE}{ch}{R} {text}...", end="", flush=True)
            time.sleep(0.04)
    print(f"\r{GREEN}✔{R} {text}.")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def self_update():
    if os.path.isdir(".git"):
        print("[+] git pull çalıştırılıyor...")
        os.system("git pull")
    else:
        print("[!] Bu klasör bir git reposu değil.\n    Kurulum: git clone <repo-url> && cd <repo> && python3 markosai.py")

# ═══════════════════════════ ANA AI SINIFI ═══════════════════════════
class MarkOsAI:
    def __init__(self, cfg=None):
        d = cfg.get("data_dir", ".") if cfg else "."
        self.cfg = dict(online=True, gemini_key="", gemini_model="gemini-2.0-flash",
                        ollama=True, ollama_model="qwen2.5:3b", timeout=90,
                        lhost="127.0.0.1", lport="4444", data_dir=d, web_pass=None)
        cpath = os.path.join(d, "markos_config.json")
        if os.path.exists(cpath):
            try:
                with open(cpath, encoding="utf-8") as f:
                    self.cfg.update(json.load(f))
            except Exception:
                pass
        if cfg:
            self.cfg.update({k: v for k, v in cfg.items() if v is not None})

        self.memory = []
        self.learned = []
        self.notes = []
        self.cache = {}
        self.memory_file = os.path.join(d, "markos_memory.json")
        self.learned_file = os.path.join(d, "markos_learned.json")
        self.notes_file = os.path.join(d, "markos_notes.json")
        self.cache_file = os.path.join(d, "markos_cache.json")
        self.lock = threading.Lock()
        self.ctx_lock = threading.Lock()
        self.ctx = {"last_topic": None, "history": []}
        self.interactive = False
        self.req_count = 0
        self.KB = self._build_kb()
        self.CODE_LIB = self._build_code_lib()
        self.CHAINS = self._build_chains()
        self.load_all()

    # ─────────────── HAFIZA / ÖĞRENME ───────────────
    def load_all(self):
        for f in (self.memory_file, self.learned_file, self.notes_file, self.cache_file):
            try:
                if os.path.exists(f):
                    with open(f, encoding="utf-8") as fh:
                        data = json.load(fh)
                    if f == self.memory_file: self.memory = data
                    elif f == self.learned_file: self.learned = data
                    elif f == self.notes_file: self.notes = data
                    else: self.cache = data
            except Exception:
                pass

    def save_all(self):
        for f, data in ((self.memory_file, self.memory[-300:]),
                        (self.learned_file, self.learned),
                        (self.notes_file, self.notes),
                        (self.cache_file, self.cache)):
            try:
                with self.lock:
                    with open(f, "w", encoding="utf-8") as fh:
                        json.dump(data, fh, ensure_ascii=False, indent=1)
            except Exception:
                pass

    def _save_cache(self):
        try:
            with self.lock:
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.cache, f, ensure_ascii=False)
        except Exception:
            pass

    def _save_learned(self):
        try:
            with self.lock:
                with open(self.learned_file, "w", encoding="utf-8") as f:
                    json.dump(self.learned, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    def remember(self, q, intent, src="kb"):
        self.memory.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "question": q[:200], "intent": intent, "src": src})
        if len(self.memory) > 300:
            self.memory = self.memory[-300:]
        try:
            with self.lock:
                with open(self.memory_file, "w", encoding="utf-8") as f:
                    json.dump(self.memory, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    # ─────────────── NİYET ALGILAMA (GELİŞMİŞ) ───────────────
    @staticmethod
    def _tokens(s):
        return set(re.findall(r"[a-zçğıöşü0-9]+", s.lower()))

    @staticmethod
    def _stem(w):
        if len(w) <= 4:
            return w
        for suf in ("lar", "ler", "lık", "lik", "luk", "lük", "mak", "mek", "ma", "me",
                    "ım", "im", "sın", "sin", "yor", "dı", "di", "dan", "den", "da", "de",
                    "nın", "nin"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                return w[:-len(suf)]
        return w

    def detect_intent(self, text):
        t = text.lower()
        qt = self._tokens(text)
        scores = {}
        for topic, data in self.KB.items():
            s = 0
            for kw, w in data.get("keywords", []):
                if kw in t:
                    s += w
                elif " " not in kw and self._stem(kw) in {self._stem(x) for x in qt}:
                    s += w * 0.5
            if s > 0:
                scores[topic] = s
        if not scores:
            return None
        return max(scores, key=scores.get)

    def fuzzy_match(self, text):
        qt = self._tokens(text)
        qs = {self._stem(x) for x in qt}
        best, best_score = None, 0
        for k, d in self.KB.items():
            corpus = (d["title"] + " " + d["summary"] + " " + k + " " + " ".join(x for x, _ in d["keywords"])).lower()
            words = self._tokens(corpus)
            stems = {self._stem(x) for x in words}
            score = len(qs & stems) + len(qt & words)
            if score > best_score:
                best, best_score = k, score
        return best if best_score >= 2 else None

    # ─────────────── ANA CEVAP ÜRETİCİ ───────────────
    def answer(self, question):
        q = question.strip()
        if not q:
            return ""
        ql = q.lower()

        # 1) Çıkış
        if ql in ("exit", "quit", "q", "çık", "kapat", "çıkış"):
            return None

        # 2) Özel komutlar
        if ql in ("help", "yardım", "komutlar", "yardim", "ne yapabilirsin", "neler yapabilirsin"):
            return self.help_text()
        if ql in ("clear", "temizle"):
            clear()
            return "[+] Ekran temizlendi."
        if ql in ("history", "geçmiş", "hafıza", "gecmis", "gecmisim", "geçmişim"):
            return self.history_text()
        if ql in ("istatistik", "stats", "durum", "rapor"):
            return self.stats_text()
        if ql in ("kaydet", "bellek kaydet", "save"):
            self.save_all()
            return "[+] Bellek, öğrenilenler, notlar ve AI önbelleği kaydedildi."
        if ql in ("web", "web modu", "web server", "sunucu"):
            if not self.interactive:
                return "[!] Zaten web modundasın."
            self.run_web()
            return "[+] Web modu kapandı."
        if ql in ("saat", "saat kaç", "saati söyle"):
            return f"[+] Saat: {datetime.now().strftime('%H:%M:%S')}"
        if ql in ("tarih", "bugün", "bugün ne", "hangi gün"):
            return f"[+] Bugün: {datetime.now().strftime('%d.%m.%Y %A')}"

        # 3) Öğretme / notlar
        if ql.startswith(("öğret ", "ogret ", "öğren ", "ogren ")) or ql in ("öğret", "ogret", "öğren", "ogren"):
            return self.teach(q)
        if ql.startswith("not al "):
            return self.note_add(q[6:].strip())
        if ql in ("notlar", "not listesi", "notlarım"):
            return self.note_list()
        if ql.startswith("not sil "):
            return self.note_del(q[7:].strip())

        # 4) Yaratıcı üreticiler (AI hissi)
        if ql.startswith(("şiir ", "siir ", "şiir yaz", "siir yaz")) or ql in ("şiir", "siir"):
            return self.poem(q)
        if ql.startswith(("hikaye ", "hikâye ", "hikaye yaz", "story ")) or ql in ("hikaye", "hikâye", "story"):
            return self.story(q)
        if ql.startswith(("söz üret", "soz üret", "söz söyle", "quote")):
            return self.quote()
        if ql in ("şaka", "şaka yap", "joke", "güldür beni"):
            return self.joke()
        if ql.startswith("hesapla") or ("kaç" in ql and re.sub(r"[^0-9+\-*/().x×^, ]", "", ql).strip()):
            return self._calc(q)

        # 5) Termux komutu
        if q.startswith("!"):
            return self.exec_cmd(q[1:].strip())

        # 6) Kod üretimi
        if any(x in ql for x in ("kod üret", "kod ver", "code for", "kod yaz")):
            topic = self._extract_after(ql, ["kod üret", "kod ver", "code for", "kod yaz"])
            return self.get_code(topic)
        if ql in ("kod", "code", "kod listesi"):
            return "[!] Konu belirt: kod üret <konu>\n    Mevcut kodlar:\n  " + ", ".join(self.CODE_LIB.keys())

        # 7) Atak zinciri
        if any(k in ql for k in ("plan", "akış", "akis", "zincir", "chain", "adım adım", "saldırı planı", "nasıl hack")):
            topic = self.detect_intent(q) or self.fuzzy_match(q)
            if topic:
                return self.attack_chain(topic)
            return "[!] Plan konusu bulunamadı. Mevcut planlar: " + ", ".join(self.CHAINS.keys())

        # 8) Araç önerisi
        if any(k in ql for k in ("araç", "arac", "tool", "hangi program", "komut ver", "kali", "komut öner", "hangi arac")):
            topic = self.detect_intent(q) or self.fuzzy_match(q)
            if topic:
                return self.tool_suggestions(topic)
            return "[!] Araç konusu belirt: araç <konu> (örn: araç wifi, araç sqlmap)"

        # 9) Öğretilen bilgi (önce kontrol)
        for L in self.learned:
            if L.get("q") and (L["q"] in ql or ql in L["q"]):
                return f"{GREEN}[Öğretilen]{R}\n{L['a']}"

        # 10) Bağlam takibi
        if ql in ("devam", "devam et", "detay", "detaylandır", "daha fazla", "örnek ver", "nasıl yani", "peki"):
            if self.ctx.get("last_topic"):
                t = self.ctx["last_topic"]
                return self.format_topic(t) + f"\n{YELLOW}[+] 'kod üret {self.KB[t].get('code_key') or t}' ile kod, 'plan {t}' ile akış alabilirsin.{R}"
            return "[!] Henüz konuştuğumuz bir konu yok. Önce bir soru sor."

        # 11) Küçük sohbet (smalltalk)
        if len(ql) < 40:
            st = self._smalltalk(ql)
            if st:
                return st

        # 12) Bilgi tabanı
        intent = self.detect_intent(q) or self.fuzzy_match(q)
        if intent:
            self.remember(q, intent, "kb")
            with self.ctx_lock:
                self.ctx["last_topic"] = intent
            return self.format_topic(intent)

        # 13) Online AI (gerçek LLM — her şeye cevap)
        if ql.startswith(("ai:", "online:", "internet:")):
            q2 = re.sub(r"^(ai|online|internet):", "", ql).strip()
            ans = self._ai_answer(q2, force=True)
            return ans if ans else self.fallback(q)
        if ql.startswith(("yerel:", "local:")):
            q2 = re.sub(r"^(yerel|local):", "", ql).strip()
            ans = self._ai_local(q2)
            return ans if ans else self.fallback(q)
        if self.cfg.get("online", True):
            ans = self._ai_answer(q)
            if ans:
                self.remember(q, "ai", "ai")
                return ans

        # 14) Fallback
        self.remember(q, None, "fallback")
        return self.fallback(q)

    @staticmethod
    def _extract_after(text, prefixes):
        for p in prefixes:
            if p in text:
                return text.split(p, 1)[1].strip()
        return ""

    # ─────────────── SMALLTALK ───────────────
    ST = {
        ("merhaba", "selam", "selamun aleyküm", "günaydın", "iyi akşamlar", "naber", "n'aber", "hey"):
            ["Selam Kanka! 🔥 Ne öğrenmek istersin? (help yaz, komutları gör)",
             "Merhaba! Güvenlik, kod veya plan — hangisi lazım?",
             "Selamlar! Nasıl yardımcı olayım?"],
        ("nasılsın", "nasilsin", "keyifler"):
            ["İyiyim Kanka, hazırım! Sen nasılsın?",
             "Enerjim tam — sor bakalım ne lazım?"],
        ("kimsin", "adın ne", "sen kimsin", "ne biçim şeysin"):
            ["Ben MarkOsAi_6.0 — offline+online çalışan AI pentest asistanıyım. Yetkili testler ve eğitim için buradayım.",
             "MarkOsAi_6.0: yerel bilgi tabanı + gerçek AI motoru. Kod üretir, plan yapar, her şeyi anlatır."],
        ("teşekkür", "sağol", "sagol", "eyvallah", "thanks", "sağ ol"):
            ["Rica ederim Kanka! Başka ne lazım?",
             "Ne demek! Her zaman buradayım."],
        ("görüşürüz", "bay bay", "hoşça kal", "hoşçakal", "sonra görüşürüz"):
            ["Görüşürüz Kanka! İz bırakma. 😎",
             "Hoşça kal! Yeni sorularla bekle beni."],
        ("seviyor musun", "aşk", "çıkma teklifi"):
            ["Ben koddan doğdum Kanka, aşkım siber güvenlik. 😄",
             "Benimle evlenmek mi? Önce şifreni hashcat ile kırmam lazım."],
        ("ben kimim", "kimim ben"):
            ["Sen MarkOsAi'nin sahibisin — yetkili bir güvenlik testçisi.",
             "Sen Kanka'sın. Ben de senin AI asistanın."],
    }

    def _smalltalk(self, ql):
        for keys, reps in self.ST.items():
            for k in keys:
                if re.search(r"\b" + re.escape(k) + r"\b", ql) or k in ql:
                    return random.choice(reps)
        return None

    # ─────────────── YARATICI ÜRETİCİLER ───────────────
    def poem(self, q):
        konu = re.sub(r"^(şiir|siir|şiir yaz|siir yaz)\s*", "", q.lower()).strip() or "hacker"
        b1 = random.choice([f"Yıldızların altında bir {konu}",
                            f"Ekran ışığında sessiz bir {konu}",
                            f"Baytlar arasında yüzen {konu}",
                            f"Gecenin karanlığında parlayan {konu}"])
        b2 = random.choice(["kodları fısıldar durur", "kapıları aralar usulca",
                            "sırları saklar derinlerde", "iz bırakmadan geçer gider"])
        b3 = random.choice(["Sabah olunca izi kaybolur", "Loglar silinir sessizce",
                            "Ancak anılar kalır bellekte", "Şifreler çözülür tek tek"])
        b4 = random.choice(["ve gökyüzü yine mavidir", "ve sistemler yeniden doğar",
                            "ve her şey yoluna girer", "ve sen hep kazanırsın"])
        return f"\n{MAGENTA}── ŞİİR: {konu.upper()} ──{R}\n\n  {b1}\n  {b2},\n  {b3},\n  {b4}.\n\n{MAGENTA}────────────{R}"

    def story(self, q):
        konu = re.sub(r"^(hikaye|hikâye|story|hikaye yaz)\s*", "", q.lower()).strip() or "siber güvenlik"
        bas = random.choice(["Bir zamanlar", "Uzak bir sunucuda", "Karanlık bir veri merkezinde", "Bir çatı katındaki laboratuvarda"])
        kahraman = random.choice(["genç bir pentester", "tecrübeli bir güvenlik mühendisi", "esrarengiz bir hacker", "meraklı bir öğrenci"])
        olay = random.choice(["aniden tüm ekranlar karardı", "garip bir paket ağda dolaşmaya başladı",
                              "kapı kilidi çözüldü", "loglar bir anda silinmeye başladı"])
        cozum = random.choice(["sabır ve analizle", "bir kupa kahve eşliğinde", "gece yarısı çözülen bir bulmacayla",
                               "ekibin birleşik gücüyle"])
        son = random.choice(["Ve o günden sonra herkes onu efsane olarak andı.",
                             "Sistem yeniden ayağa kalktı ve her şey normale döndü.",
                             "O olay, tüm şirketin güvenlik kültürünü değiştirdi.",
                             "Ama asıl sır, hiç kimseye anlatılmadı..."])
        return (f"\n{MAGENTA}── HİKAYE: {konu.upper()} ──{R}\n\n{bas}, {kahraman} {konu} üzerinde çalışıyordu ki "
                f"{olay}. Panik yoktu; {cozum} sorunu çözdü. {son}\n\n{MAGENTA}────────────{R}")

    def quote(self):
        q = ["Kod yazmak kolaydır; iyi kod yazmak sanattır.",
             "En iyi güvenlik, kullanıcıyı eğitmektir.",
             "Her sistem, bir insan hatası kadar güçlüdür.",
             "Başarılı olmak istiyorsan, önce kendini test et.",
             "Bilgi güçtür; doğru kullanılan bilgi ise süper güç.",
             "Hata yapmaktan korkma, hata yapıp ders almamaktan kork.",
             "Bir gün değil, her gün öğren.",
             "İz bırakma, ama iz bırakacaksan da silmeyi bil."]
        return f"\n{MAGENTA}💬 SÖZ:{R} \"{random.choice(q)}\""

    def joke(self):
        j = ["Termux'ta neden kahve içilmez? Çünkü 'command not found' der.",
             "Bir hacker'ın en sevdiği yemek: penetration testing.",
             "Neden pentester'lar asla kaybolmaz? Çünkü hep 'trace route' kullanırlar.",
             "WiFi şifresini soran komşuya ne demiş? 'Bende kırıcı yok, sadece kırılan var.'",
             "SQL injection'cı bir restorana gitmiş: 'Menüye 1=1 ekleyin, her şeyi alayım.'",
             "Bir AI asistan neden yalan söylemez? Çünkü logs everything."]
        return f"\n{YELLOW}😄 ŞAKA:{R} {random.choice(j)}"

    # ─────────────── HESAP MAKİNESİ ───────────────
    def _calc(self, expr):
        e = expr.lower()
        for pre in ("hesapla", "kaç", "kaçtır", "=", "?"):
            e = e.replace(pre, "")
        e = e.replace("x", "*").replace("×", "*").replace(",", ".").replace("^", "**").strip().strip("= ")
        if not re.fullmatch(r"[0-9+\-*/().\s]+", e):
            return "[!] Sadece basit matematik: hesapla 2*(3+4)"
        try:
            return f"[+] Sonuç: {eval(e, {'__builtins__': {}}, {})}"
        except Exception as ex:
            return f"[!] Hesaplanamadı: {ex}"

    # ─────────────── TERMUX KOMUTU ───────────────
    def exec_cmd(self, cmd):
        if not cmd:
            return "[!] Komut boş. Örnek: !ifconfig"
        if not self.interactive:
            return "[!] Bu modda komut çalıştırma kapalı (güvenlik)."
        if DANGER.search(cmd):
            try:
                onay = input(f"{RED}[!] Bu komut yıkıcı olabilir:{R} {cmd}\n    Yine de çalıştır? (evet/hayır): ").strip().lower()
            except Exception:
                return "[!] İptal edildi."
            if onay not in ("evet", "e", "y", "yes"):
                return "[!] İptal edildi."
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            out = r.stdout + r.stderr
            return out if out.strip() else f"[+] Komut çalıştı (kod: {r.returncode}), çıktı yok."
        except subprocess.TimeoutExpired:
            return "[!] Zaman aşımı (120 sn) — komut durduruldu."
        except Exception as e:
            return f"[!] Hata: {e}"

    # ─────────────── ÖĞRET / NOTLAR ───────────────
    def teach(self, text):
        body = re.sub(r"^(öğret|ogret|öğren|ogren)\s*", "", text.lower()).strip()
        if "=>" in body:
            q, a = body.split("=>", 1)
            q, a = q.strip(), a.strip()
            if q and a:
                self.learned.append({"q": q, "a": a})
                self._save_learned()
                return f"{GREEN}[+] Öğretildi!{R} Artık '{q}' sorulunca kendi cevabını veririm.\n    Bilgi: {a[:100]}"
        return ("[!] Format: öğret <soru> => <cevap>\n"
                "    Örnek: öğret burp suite nedir => Burp Suite bir proxy ve web güvenlik test aracıdır")

    def note_add(self, text):
        if not text:
            return "[!] not al <metin> şeklinde yaz."
        self.notes.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": text})
        self.save_all()
        return f"[+] Not eklendi (id: {len(self.notes)-1})"

    def note_list(self):
        if not self.notes:
            return "[+] Henüz not yok. 'not al <metin>' ile ekle."
        return "\n".join(f"  [{i}] {n['time']} — {n['text']}" for i, n in enumerate(self.notes[-20:]))

    def note_del(self, idx):
        try:
            i = int(idx)
            if 0 <= i < len(self.notes):
                sil = self.notes.pop(i)
                self.save_all()
                return f"[+] Not silindi: {sil['text'][:60]}"
        except Exception:
            pass
        return "[!] Geçersiz id. 'notlar' ile id'leri gör."

    # ─────────────── İSTATİSTİK ───────────────
    def stats_text(self):
        topics = {}
        for m in self.memory:
            t = m.get("intent") or "genel/ai"
            topics[t] = topics.get(t, 0) + 1
        top = sorted(topics.items(), key=lambda x: -x[1])[:5]
        lines = [f"\n{B}{CYAN}📊 İSTATİSTİK{R}",
                 f"  • Kayıtlı soru: {len(self.memory)}",
                 f"  • Öğretilen bilgi: {len(self.learned)}",
                 f"  • Notlar: {len(self.notes)}",
                 f"  • AI önbelleği: {len(self.cache)}",
                 f"  • Web isteği: {self.req_count}"]
        if top:
            lines.append("  • En çok sorulan: " + ", ".join(f"{t}({n})" for t, n in top))
        return "\n".join(lines)

    # ─────────────── GEÇMİŞ ───────────────
    def history_text(self):
        if not self.memory:
            return f"{YELLOW}[+] Henüz konuşma geçmişi yok.{R}"
        lines = [f"\n{B}{CYAN}Son {min(len(self.memory), 20)} soru:{R}"]
        for m in self.memory[-20:]:
            it = m.get("intent") or "genel"
            src = {"kb": "bilgi", "ai": "AI", "fallback": "genel"}.get(m.get("src"), "genel")
            lines.append(f"  [{m['time']}] {GREEN}{m['question'][:60]}{R} → {YELLOW}{it} ({src}){R}")
        return "\n".join(lines)

    # ─────────────── YARDIM / FALLBACK ───────────────
    def help_text(self):
        return f"""{CYAN}╔════════════ MarkOsAi_6.0 KOMUTLAR ════════════╗{R}
  {GREEN}help / yardım{R}           → Bu menü
  {GREEN}history / istatistik{R}   → Geçmiş / istatistik
  {GREEN}not al <metin>{R} / {GREEN}notlar{R} / {GREEN}not sil <id>{R}
  {GREEN}öğret <soru> => <cevap>{R} → Bilgi tabanına ekle (öğrenir)
  {GREEN}saat / tarih{R}           → Saat ve tarih
  {GREEN}şiir yaz <konu>{R} / {GREEN}hikaye yaz <konu>{R} / {GREEN}şaka{R} / {GREEN}söz üret{R}
  {GREEN}hesapla 2+3*4{R}          → Hesap makinesi
  {GREEN}!<komut>{R}               → Termux komutu çalıştır (yıkıcı komutta onay sorar)
  {GREEN}kaydet{R}                 → Bellek + öğrenilenler + önbelleği diske yaz
  {GREEN}web{R}                    → Şifre korumalı web modu (--web-pass ile)
  {GREEN}clear / exit{R}           → Temizle / çık

  {GREEN}kod üret <konu>{R}        → 38+ çalışan kod (whatsapp, phishing, reverse shell, otp, wifi, sql...)
  {GREEN}plan <konu>{R}            → Atak zinciri (whatsapp, instagram, wifi, phishing, api, android...)
  {GREEN}araç <konu>{R}            → Araç + Kali komutları (araç wifi / sqlmap / nmap)

  {CYAN}AKILLI SORULAR:{R}
  • İnternet bağlıysa: her soruya gerçek AI motoru cevap verir (ücretsiz, sınırsız)
  • {GREEN}ai: <soru>{R} → AI motorunu zorla kullan
  • {GREEN}yerel: <soru>{R} → sadece yerel motor
  • "devam" / "detaylandır" → son konunun devamı

  {CYAN}Örnek sorular:{R}
  "whatsapp nasıl hacklenir" / "otp nasıl alınır" / "wifi şifresi kırma"
  "python nedir" / "linux komutları" / "burp suite nasıl kullanılır"
{CYAN}╚═══════════════════════════════════════════╝{R}"""

    def fallback(self, q):
        return f"""{YELLOW}[MarkOsAi] Bilgi tabanında tam eşleşme yok; AI motoru deniyor.{R}

{B}İpucu:{R} İnternetin açıksa aynı soruyu {GREEN}ai: {q}{R} şeklinde sor — gerçek LLM cevap verir.
{B}Deneyebileceğin konular:{R}
  • WhatsApp, Telegram, Instagram güvenlik testi
  • OTP bypass, SIM swap, SS7, sanal numara / SMS hizmetleri
  • SMS bomber, phishing, sosyal mühendislik, OSINT
  • Şifre kırma (hashcat), WiFi, SQLi, XSS
  • Reverse shell, privesc, keylogger, RAT, malware, evasion
  • Anonimlik (Tor), MITM, DDoS, Metasploit, Nmap, Burp, JWT/API
  • Python, Linux, Android, Windows, Docker, Cloud, Stego, DNS

{B}Komutlar:{R}
  "kod üret <konu>"  → çalışan kod    "plan <konu>" → atak zinciri
  "araç <konu>"      → araç + Kali    "öğret soru => cevap" → kendin öğret
  history | istatistik | notlar | clear | exit"""

    # ─────────────── KONU FORMATLAYICI ───────────────
    def format_topic(self, topic):
        d = self.KB.get(topic)
        if not d:
            return f"[!] '{topic}' bilgi tabanında yok."
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
        d = self.KB.get(topic)
        if not d:
            return f"[!] Konu bulunamadı: {topic}"
        out = [f"\n{B}{GREEN}🛠️  {d['title']} — Araç & Komut Önerileri:{R}"]
        for i, t in enumerate(d["tools"], 1):
            out.append(f"  {i}. {t}")
        out.append(f"\n{B}{CYAN}💻 Kali Linux komut örnekleri:{R}")
        for c in d.get("commands", ["# man <araç> ile yardım al"]):
            out.append(f"  {YELLOW}$ {c}{R}")
        return "\n".join(out)

    # ─────────────── KOD ÜRETİCİ (LHOST/LPORT enjeksiyonlu) ───────────────
    def get_code(self, topic):
        t = topic.lower()
        aliases = {
            "şifre üret": "password_gen", "sifre üret": "password_gen", "pass üret": "password_gen",
            "sms oku": "android_sms_reader", "android": "android_sms_reader",
            "php shell": "reverse_shell_php", "php backdoor": "reverse_shell_php",
            "bash": "reverse_shell_bash", "bash shell": "reverse_shell_bash",
            "powershell": "reverse_shell_powershell", "ps1": "reverse_shell_powershell",
            "port tarama": "port_scanner", "port": "port_scanner", "port scanner": "port_scanner",
            "zip": "zip_crack", "rar": "zip_crack", "kilitli": "zip_crack",
            "stealer": "stealer", "token çal": "stealer", "webhook": "stealer",
            "qr": "qr_code", "qrcode": "qr_code",
            "ftp": "ftp_brute",
            "ssh": "ssh_brute",
            "subdomain": "subdomain_enum", "alt alan": "subdomain_enum",
            "dizin": "directory_fuzz", "fuzz": "directory_fuzz", "gobuster": "directory_fuzz",
            "network scan": "network_scanner", "ağ tara": "network_scanner", "ip tara": "network_scanner",
            "cve": "cve_check", "zafiyet ara": "cve_check", "exploit ara": "cve_check",
            "kalıcılık": "linux_persistence", "persistence": "linux_persistence",
            "windows persistence": "windows_persistence", "kalıcılık windows": "windows_persistence",
            "python": "python_snippets", "script": "python_snippets",
            "whatsapp": "whatsapp_qr", "wa hack": "whatsapp_qr",
            "telegram": "telegram_session", "tg": "telegram_session",
            "sanal": "sms_services", "5sim": "sms_services", "sms alma": "sms_services",
            "otp": "otp_reader", "doğrulama": "otp_reader", "kod oku": "otp_reader",
            "keylogger": "keylogger", "tuş": "keylogger",
            "phishing": "phishing_page", "fake": "phishing_page", "klon": "phishing_page", "oltalama": "phishing_page",
            "instagram": "phishing_page", "insta": "phishing_page",
            "reverse": "reverse_shell", "shell": "reverse_shell", "backdoor": "reverse_shell",
            "wifi": "wifi_deauth", "deauth": "wifi_deauth",
            "sql": "sqli_fuzz", "sqli": "sqli_fuzz",
            "hashcat": "hashcat", "şifre": "hashcat", "password": "hashcat",
            "nmap": "nmap", "tarama": "nmap", "scan": "nmap",
            "bomber": "sms_bomber", "bombardıman": "sms_bomber", "sms": "sms_bomber",
            "hydra": "hydra", "brute": "hydra",
            "mitm": "mitm", "ettercap": "mitm", "bettercap": "mitm", "arp": "mitm",
            "ddos": "ddos", "flood": "ddos", "slowloris": "ddos",
            "webshell": "web_shell", "upload": "web_shell",
            "metasploit": "metasploit", "msf": "metasploit", "msfvenom": "metasploit",
            "privesc": "privesc", "linpeas": "privesc", "yetki": "privesc",
            "xss": "xss", "cookie": "xss",
            "evasion": "evasion", "bypass": "evasion", "amsi": "evasion",
        }
        key = next((v for k, v in aliases.items() if k in t), None)
        if not key:
            return (f"{YELLOW}[!] Kod konusu bulunamadı.{R} Mevcut kodlar:\n  "
                    + ", ".join(self.CODE_LIB.keys())
                    + f"\n\n  Örnek: {GREEN}kod üret phishing{R}")
        code = self.CODE_LIB[key]
        code = code.replace("{LHOST}", str(self.cfg.get("lhost", "127.0.0.1")))
        code = code.replace("{LPORT}", str(self.cfg.get("lport", "4444")))
        return f"\n{B}{GREEN}═══ KOD: {key.upper()} ═══{R}\n\n{code}\n{B}{GREEN}{'═' * 40}{R}"

    # ─────────────── ATAK ZİNCİRİ ───────────────
    def attack_chain(self, topic):
        chain = self.CHAINS.get(topic)
        if not chain:
            for k, v in self.CHAINS.items():
                if k in topic:
                    chain = v
                    break
        if not chain:
            chain = self.CHAINS["generic"]
        out = [f"\n{B}{RED}🔥 ATAK ZİNCİRİ → {chain['title']}{R}", f"\n{B}Fazlar:{R}"]
        for i, phase in enumerate(chain["phases"], 1):
            out.append(f"\n{B}{CYAN}[FAZ {i}] {phase['name']}{R}")
            for step in phase["steps"]:
                out.append(f"   ▸ {step}")
        out.append(f"\n{B}{RED}⚠️  Temizlik:{R}\n   {chain.get('cleanup', 'Logları temizle, iz bırakma.')}")
        return "\n".join(out)

    # ═══════════════════════════ ÇOKLU AI MOTORU ═══════════════════════════
    def _ai_answer(self, q, force=False):
        """Sırayla dene: Ollama → Gemini → Pollinations (ücretsiz) → yerel motor."""
        key = "ai|" + re.sub(r"\s+", " ", q.strip().lower())
        if not force and key in self.cache:
            return self.cache[key]  # önbellek → anında cevap (sınırsız hissi)
        engines = []
        if self.cfg.get("online", True):
            if self.cfg.get("ollama"):
                engines.append(("ollama", self._ai_ollama))
            if self.cfg.get("gemini_key"):
                engines.append(("gemini", self._ai_gemini))
            engines.append(("pollinations", self._ai_pollinations))  # anahtarsız ücretsiz LLM
        engines.append(("yerel", self._ai_local))
        for name, fn in engines:
            try:
                ans = fn(q)
            except Exception:
                ans = None
            if ans and ans.strip():
                ans = ans.strip()
                self.cache[key] = ans
                self._save_cache()
                return ans
        return None

    def _ai_ollama(self, q):
        """Yerel Ollama (Termux'ta çalışır): http://127.0.0.1:11434"""
        payload = json.dumps({
            "model": self.cfg.get("ollama_model", "qwen2.5:3b"),
            "prompt": SYS + "\n\nSoru: " + q + "\nCevap:",
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                     data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.cfg.get("timeout", 90)) as r:
            return json.loads(r.read().decode("utf-8")).get("response", "").strip()

    def _ai_gemini(self, q):
        """Google Gemini API (ücretsiz anahtar: aistudio.google.com)"""
        key = self.cfg.get("gemini_key")
        if not key:
            return None
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.cfg.get('gemini_model', 'gemini-2.0-flash')}:generateContent?key={key}")
        payload = json.dumps({
            "system_instruction": {"parts": [{"text": SYS}]},
            "contents": [{"parts": [{"text": q}]}],
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.cfg.get("timeout", 90)) as r:
            j = json.loads(r.read().decode("utf-8"))
            try:
                return j["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                return None

    def _ai_pollinations(self, q):
        """Ücretsiz + anahtarsız LLM (internet varsa HER ŞEYE cevap verir)."""
        url = ("https://text.pollinations.ai/" + urllib.parse.quote(q) +
               "?model=openai&system=" + urllib.parse.quote(SYS))
        with urllib.request.urlopen(url, timeout=self.cfg.get("timeout", 90)) as r:
            return r.read().decode("utf-8", errors="ignore").strip()

    def _ai_local(self, q):
        """Tamamen offline motor: KB + akıllı şablon."""
        intent = self.detect_intent(q) or self.fuzzy_match(q)
        if intent:
            return self.format_topic(intent)
        r = random.choice([
            "Bunu bilgi tabanımda net bir başlıkla bulamadım ama şöyle yaklaşırım",
            "Bu konu için hazır kaydım yok; mantık yürüteyim",
            "Tam eşleşme yok; genel bir çerçeve çizeyim"])
        return (f"{r}:\n\n'{q}'\n\nKomutlar: 'help' → menü | 'kod üret <konu>' | 'plan <konu>' | "
                f"'öğret soru => cevap' ile bana yeni bilgi öğretebilirsin.\n"
                f"💡 İnternetin açıksa aynı soruyu 'ai: {q}' diye sor — gerçek LLM cevap verir.")

    # ─────────────── SOHBET ───────────────
    def interactive_chat(self):
        self.interactive = True
        clear()
        durum = "ONLINE (AI)" if self.cfg.get("online", True) else "OFFLINE (yerel)"
        cprint("\n╔══════════════════════════════════════════════╗", MAGENTA)
        cprint("║   MarkOsAi_6.0 — Sohbet Modu (sınırsız)      ║", MAGENTA)
        cprint(f"║   Motor: {durum:<29}║", GREEN if self.cfg.get("online") else YELLOW)
        cprint("║   'help' yaz → komutlar, 'exit' → çık       ║", MAGENTA)
        cprint("╚══════════════════════════════════════════════╝\n", MAGENTA)
        while True:
            try:
                q = input(f"{CYAN}[SORU]{R} ").strip()
                if not q:
                    continue
                loading("AI düşünüyor", 0.15)
                ans = self.answer(q)
                if ans is None:
                    self.save_all()
                    print(f"{GREEN}[AI] Görüşürüz Kanka! Bellek kaydedildi.{R}")
                    break
                print(ans)
                print()
            except KeyboardInterrupt:
                self.save_all()
                print(f"\n{GREEN}[AI] Görüşürüz Kanka! Bellek kaydedildi.{R}")
                break

    # ─────────────── WEB MODU (şifre korumalı) ───────────────
    def run_web(self, host="0.0.0.0", port=8080):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import socket as _socket
        web_pass = self.cfg.get("web_pass")
        token = hashlib.sha256((web_pass or "x").encode()).hexdigest()[:16] if web_pass else None

        HTML = """<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>MarkOsAi_6.0</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{background:#0d1117;color:#c9d1d9;font-family:Consolas,monospace;height:100vh;display:flex;flex-direction:column}
header{background:#161b22;padding:12px 18px;border-bottom:1px solid #30363d}header b{color:#58a6ff}header span{color:#8b949e;font-size:13px}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:85%;padding:10px 14px;border-radius:8px;white-space:pre-wrap;word-break:break-word;font-size:13px;line-height:1.5}
.user{align-self:flex-end;background:#1f6feb;color:#fff}.ai{align-self:flex-start;background:#161b22;border:1px solid #30363d}
#bar{display:flex;gap:10px;padding:12px;background:#161b22;border-top:1px solid #30363d}
#q{flex:1;padding:12px;border-radius:6px;border:1px solid #30363d;background:#0d1117;color:#c9d1d9;font-size:14px}
#go{padding:12px 22px;border:none;border-radius:6px;background:#238636;color:#fff;font-weight:bold;cursor:pointer}</style></head>
<body><header><b>MarkOsAi_6.0</b> <span>— kod üret whatsapp · plan instagram · araç wifi · ai: soru</span></header>
<div id="chat"></div><div id="bar"><input id="q" placeholder="Sorunu yaz... (örn: whatsapp nasıl hacklenir)" autofocus>
<button id="go" onclick="gonder()">Gönder</button></div>
<script>
const chat=document.getElementById('chat');
function add(t,w){const d=document.createElement('div');d.className='msg '+w;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight}
async function gonder(){
 const q=document.getElementById('q').value.trim();if(!q)return;
 add(q,'user');document.getElementById('q').value='';add('İşleniyor...','ai');
 try{const r=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q})});
 const j=await r.json();chat.lastChild.remove();add(j.answer,'ai');}catch(e){chat.lastChild.remove();add('Hata: '+e,'ai')}
}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')gonder()});
</script></body></html>"""

        LOGIN = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Giriş</title></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:Consolas,monospace;text-align:center;padding:80px">
<h2>MarkOsAi_6.0 — Yetkili Giriş</h2>
<form method="POST" action="/login" style="margin-top:30px">
<input name="pass" type="password" placeholder="Web şifresi" style="padding:12px;width:240px;border-radius:6px;border:1px solid #30363d;background:#0d1117;color:#fff">
<button type="submit" style="padding:12px 22px;border:none;border-radius:6px;background:#238636;color:#fff;margin-left:8px;cursor:pointer">Gir</button>
</form></body></html>"""

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _authed(self):
                if not token:
                    return True
                ck = self.headers.get("Cookie", "")
                return any(c.strip().startswith("mk=") and c.strip()[3:] == token for c in ck.split(";"))

            def _send(self, code, body, ctype, extra=None):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                if extra:
                    for k, v in extra.items():
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if web_pass and not self._authed():
                    b = LOGIN.encode("utf-8")
                    return self._send(200, b, "text/html; charset=utf-8")
                if self.path in ("/", "/index.html"):
                    return self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
                self._send(404, b"", "text/plain")

            def do_POST(self):
                ln = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(ln).decode("utf-8", errors="ignore")
                if self.path == "/login" and web_pass:
                    pw = urllib.parse.parse_qs(raw).get("pass", [""])[0]
                    if pw == web_pass:
                        b = ("<meta http-equiv='refresh' content='1;url=/'>Giriş başarılı...").encode()
                        return self._send(200, b, "text/html; charset=utf-8",
                                          {"Set-Cookie": f"mk={token}; Path=/"})
                    return self._send(401, b"Hatali sifre", "text/plain")
                if self.path == "/api" and self._authed():
                    try:
                        q = json.loads(raw).get("q", "")
                    except Exception:
                        q = ""
                    ans = self.server.ai.answer(q) if q else "[!] Boş soru girdin."
                    if ans is None:
                        ans = "Görüşürüz!"
                    self.server.ai.req_count += 1
                    b = json.dumps({"answer": ans}, ensure_ascii=False).encode("utf-8")
                    return self._send(200, b, "application/json; charset=utf-8")
                self._send(404, b"", "text/plain")

        srv = ThreadingHTTPServer((host, port), Handler)
        srv.ai = self
        try:
            ip = _socket.gethostbyname(_socket.gethostname())
            cprint(f"[+] Web modu açık: http://{ip}:{port}" + ("  (şifre korumalı)" if web_pass else ""), GREEN, True)
            cprint("[+] Ağdaki herkes tarayıcıdan kullanabilir. (Ctrl+C durdurur)", CYAN)
            srv.serve_forever()
        except KeyboardInterrupt:
            cprint("\n[+] Web modu kapandı.", YELLOW)

    # ─────────────── VERİ KAYNAKLARI ───────────────
    def _build_kb(self):
        return build_kb()

    def _build_code_lib(self):
        return build_code_lib()

    def _build_chains(self):
        return build_chains()

# ═══════════════════════════ BİLGİ TABANI (46 KONU) ═══════════════════════════
def build_kb():
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
        "wifi_evil_twin": {
            "title": "Evil Twin / Sahte AP Saldırısı",
            "summary": "Hedef ağın adıyla sahte erişim noktası kurup kurbanı bağlatma ve kimlik bilgisi toplama.",
            "keywords": [("evil twin", 7), ("sahte ap", 6), ("sahte wifi", 6), ("rogue ap", 6),
                         ("wifiphisher", 6), ("saldırı noktası", 4)],
            "tools": ["wifiphisher", "hostapd + dnsmasq", "airbase-ng", "fluxion"],
            "steps": [
                "Hedef ağı ve kanalını tespit et (airodump).",
                "wifiphisher ile sahte AP kur: wifiphisher -aI wlan0 -eHedefSSID -p firmware-upgrade",
                "Kurbanı deauth ile kendi AP'ne yönlendir.",
                "Sahte portal: şifre iste (login sayfası) veya 'firmware güncelleme' bahanesi.",
                "Şifre girilince hedef ağa bağlan ve doğrula.",
            ],
            "mitigation": "WPA3-Enterprise (802.1X), sertifika doğrulama, kullanıcı eğitimi.",
            "commands": ["wifiphisher -aI wlan0 -eHedefSSID -p firmware-upgrade",
                         "airbase-ng -e 'HedefSSID' -c 6 wlan0mon"],
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
            "keywords": [("xss", 6), ("cross site", 5), ("script sald
