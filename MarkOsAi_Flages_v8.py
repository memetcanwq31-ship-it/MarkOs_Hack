#!/usr/bin/env python3
"""
MarkOsAi_Flages_V8.py
Mark OS Asistan - CLI single-file assistant

Özellikler:
 - Komut satırı etkileşimi (REPL)
 - Basit kural tabanlı doğal dil yanıtlayıcı (fallback)
 - /search <sorgu> : DuckDuckGo Instant Answer (no API key)
 - /file <path> : dosya oluştur/güncelle (multi-line içerik)
 - /run <komut> : shell komutunu çalıştır (onay istenir)
 - /save <session.json> / /load <session.json> : oturum yönetimi
 - Optional: OPENAI_API_KEY varsa OpenAI çağrısı yapar (openai paketi gerekli)

Kullanım:
 > python3 MarkOsAi_Flages_V8.py
 Komutlar: /help
"""

import os
import sys
import json
import shlex
import subprocess
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import requests
except Exception:
    requests = None

# Optional OpenAI integration (will be used only if configured)
try:
    import openai
except Exception:
    openai = None

SESSION_DEFAULT_PATH = "markosai_session.json"


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


class MarkOsAssistant:
    def __init__(self, name: str = "Mark OS Asistan", author: str = "Mark"):
        self.name = name
        self.author = author
        self.history: List[Dict[str, Any]] = []
        self.config = {
            "use_openai": False,
            "openai_model": "gpt-3.5-turbo",
        }
        # check for OPENAI key
        if os.environ.get("OPENAI_API_KEY") and openai is not None:
            self.config["use_openai"] = True
            openai.api_key = os.environ.get("OPENAI_API_KEY")

    def add_history(self, role: str, text: str):
        self.history.append({"time": now_iso(), "role": role, "text": text})

    def simple_reply(self, prompt: str) -> str:
        """
        Kural tabanlı basit cevaplayıcı: belirli anahtar kelimelere göre yanıt üretir.
        Daha karmaşık yanıtlar için OpenAI veya başka bir model çağır.
        """
        p = prompt.strip().lower()
        # Greetings
        if any(p.startswith(x) for x in ("merhaba", "selam", "sa", "hello", "hi")):
            return "Merhaba! Ben Mark OS Asistan. Sana nasıl yardımcı olabilirim?"
        if "nasıl" in p and ("yapılır" in p or "yaparım" in p or "olur" in p):
            return "İstediğini adım adım yapmana yardımcı olabilirim — ne yapmak istiyorsun? (örn. /file, /search, /run)"
        if "kim" in p and "sen" in p:
            return f"Ben {self.name}, geliştiren: {self.author}."
        if "version" in p or "sürüm" in p:
            return "MarkOsAi_Flages_V8 — tek dosya CLI asistan (örnek sürüm)."
        # Small math
        if any(op in p for op in ["+", "-", "*", "×", "/", "÷"]) and any(ch.isdigit() for ch in p):
            try:
                # safe eval for basic math expressions: only digits and operators
                allowed = "0123456789+-*/(). "
                expr = "".join(ch for ch in p if ch in allowed)
                res = eval(expr, {"__builtins__": None}, {})
                return f"Hesaplama sonucu: {res}"
            except Exception:
                pass
        # fallback
        return ("Bunu doğrudan yanıtlayamıyorum. "
                "Basit görevleri yerine getirebilirim: /help yazıp komutları görebilirsin, "
                "veya daha kapsamlı cevaplar için OPENAI_API_KEY ile entegrasyon sağlayabilirsin.")

    def call_openai(self, prompt: str) -> Optional[str]:
        if not self.config.get("use_openai") or openai is None:
            return None
        try:
            # Chat completions style (gpt-3.5-turbo)
            resp = openai.ChatCompletion.create(
                model=self.config.get("openai_model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": f"You are {self.name}, a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2,
            )
            text = resp["choices"][0]["message"]["content"].strip()
            return text
        except Exception as e:
            return f"(OpenAI hatası: {e})"

    def search_web(self, query: str, max_lines: int = 6) -> str:
        """
        DuckDuckGo Instant Answer API kullanır (no API key).
        Eğer requests yüklü değilse uyarı döner.
        """
        if requests is None:
            return "requests kütüphanesi yüklü değil; web araması yapılamıyor. 'pip install requests' ile yükleyin."
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            j = r.json()
            answer = j.get("AbstractText") or j.get("Definition") or ""
            related = j.get("RelatedTopics", [])
            out_lines = []
            if answer:
                out_lines.append("Özet: " + answer)
            if related and len(out_lines) < max_lines:
                # collect some related topic texts
                count = 0
                for t in related:
                    if isinstance(t, dict):
                        txt = t.get("Text") or ""
                        if txt:
                            out_lines.append("- " + txt)
                            count += 1
                    if count >= (max_lines - len(out_lines)):
                        break
            if not out_lines:
                return "Arama yapıldı ama özet bulunamadı. Daha açık bir sorgu deneyin."
            return "\n".join(out_lines[:max_lines])
        except Exception as e:
            return f"Web arama hatası: {e}"

    def create_or_update_file(self, path: str, content: str, overwrite: bool = True) -> str:
        try:
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            mode = "w" if overwrite else "x"
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)
            return f"Dosya kaydedildi: {path}"
        except FileExistsError:
            return f"Hata: Dosya zaten var ve overwrite=False: {path}"
        except Exception as e:
            return f"Dosya yazma hatası: {e}"

    def run_shell_command(self, command: str, timeout: int = 30) -> str:
        """
        Güvenlik: komut çalıştırmadan önce kullanıcıdan onay istemek iyi bir fikirdir.
        Bu fonksiyon subprocess ile komutu çalıştırır ve stdout/stderr döner.
        """
        try:
            # shlex.split for safe tokenization (but complex commands may need shell=True)
            proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            if proc.returncode != 0:
                return f"[Kod {proc.returncode}] STDERR:\n{err}\nSTDOUT:\n{out}"
            return out or "(Çıktı yok)"
        except subprocess.TimeoutExpired:
            return f"Komut zaman aşımına uğradı (> {timeout}s)"
        except Exception as e:
            return f"Komut çalıştırma hatası: {e}"

    def save_session(self, path: str = SESSION_DEFAULT_PATH) -> str:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"name": self.name, "author": self.author, "history": self.history, "saved_at": now_iso()}, f, ensure_ascii=False, indent=2)
            return f"Oturum kaydedildi: {path}"
        except Exception as e:
            return f"Oturum kaydetme hatası: {e}"

    def load_session(self, path: str = SESSION_DEFAULT_PATH) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                j = json.load(f)
            self.history = j.get("history", [])
            return f"Oturum yüklendi: {path} (mesaj sayısı: {len(self.history)})"
        except Exception as e:
            return f"Oturum yükleme hatası: {e}"

    def handle_input(self, raw: str) -> str:
        raw = raw.strip()
        if not raw:
            return ""
        # Commands start with /
        if raw.startswith("/"):
            parts = shlex.split(raw)
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd in ("/help", "/h"):
                return self.help_text()
            if cmd == "/search":
                if not args:
                    return "Kullanım: /search <sorgu>"
                query = " ".join(args)
                self.add_history("user", f"/search {query}")
                res = self.search_web(query)
                self.add_history("assistant", res)
                return res
            if cmd == "/file":
                if not args:
                    return "Kullanım: /file <path>  (sonra çok satırlı içerik -> ctrl-D ile bitir)"
                path = args[0]
                print(f"Dosya içeriğini girin (bitirmek için CTRL-D / CTRL-Z):")
                # read multiline content from stdin
                try:
                    lines = sys.stdin.read()
                except KeyboardInterrupt:
                    lines = ""
                res = self.create_or_update_file(path, lines)
                self.add_history("user", f"/file {path}")
                self.add_history("assistant", res)
                return res
            if cmd == "/run":
                if not args:
                    return "Kullanım: /run <shell-komutu>"
                command = " ".join(args)
                # confirm
                confirm = input(f"'{command}' komutunu çalıştırmak istiyor musunuz? (evet/hayır): ").strip().lower()
                if confirm not in ("evet", "e", "yes", "y"):
                    return "Komut iptal edildi."
                self.add_history("user", f"/run {command}")
                res = self.run_shell_command(command)
                self.add_history("assistant", res)
                return res
            if cmd == "/save":
                path = args[0] if args else SESSION_DEFAULT_PATH
                res = self.save_session(path)
                return res
            if cmd == "/load":
                path = args[0] if args else SESSION_DEFAULT_PATH
                res = self.load_session(path)
                return res
            if cmd == "/history":
                n = int(args[0]) if args else 50
                out = []
                for i, m in enumerate(self.history[-n:], start=max(0, len(self.history)-n)+1):
                    out.append(f"{i}: [{m['role']}] {m['time']} - {m['text']}")
                return "\n".join(out) if out else "(Geçmiş boş)"
            if cmd == "/config":
                return json.dumps(self.config, ensure_ascii=False, indent=2)
            if cmd == "/exit" or cmd == "/quit":
                print("Çıkılıyor...")
                sys.exit(0)
            return f"Bilinmeyen komut: {cmd}. /help ile komut listesine bakın."
        # Not a command: normal natural-language prompt
        self.add_history("user", raw)
        # If configured, first try OpenAI
        if self.config.get("use_openai"):
            ai_resp = self.call_openai(raw)
            if ai_resp:
                self.add_history("assistant", ai_resp)
                return ai_resp
        # fallback local reply
        reply = self.simple_reply(raw)
        self.add_history("assistant", reply)
        return reply

    def help_text(self) -> str:
        return (
            "Mark OS Asistan - Komutlar:\n"
            " /help                 : Bu yardım metni\n"
            " /search <sorgu>       : Hızlı web özeti (DuckDuckGo Instant Answer)\n"
            " /file <path>          : Dosya oluştur/güncelle (içerik için stdin)\n"
            " /run <komut>          : Shell komutu çalıştır (onay ister)\n"
            " /save [path]          : Oturumu kaydet (varsayılan markosai_session.json)\n"
            " /load [path]          : Oturumu yükle\n"
            " /history [n]          : Son n mesajı göster (varsayılan 50)\n"
            " /config               : Konfigürasyonu göster\n"
            " /exit or /quit        : Çıkış\n"
            "\nNotlar:\n"
            " - Güvenlik: /run komutlarını dikkatli kullanın.\n"
            " - İleri düzey cevaplar için OPENAI_API_KEY ortam değişkeni belirtip openai paketini kurabilirsiniz.\n"
        )


def repl_loop():
    assistant = MarkOsAssistant()
    banner = f"{assistant.name} (MarkOsAi_Flages_V8) - Hoş geldiniz! /help ile komutları görün."
    print(banner)
    try:
        while True:
            try:
                raw = input("Sen: ")
            except EOFError:
                print("\nGörüşürüz.")
                break
            except KeyboardInterrupt:
                print("\nKapatılıyor.")
                break
            if not raw:
                continue
            # handle input
            out = assistant.handle_input(raw)
            if out:
                # pretty print assistant response
                print("\nAsistan:", out, "\n")
    except Exception as e:
        print("Beklenmedik hata:", e)


if __name__ == "__main__":
    repl_loop()
