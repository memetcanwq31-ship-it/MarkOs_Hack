#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MARKOS X Ware V2.0 - Yerli Veil Framework
# Repo: github.com/memetcanwq31

import os
import sys
import time
import base64
import random
import string
import hashlib
import socket
import struct
import subprocess
import platform

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from Crypto.Random import get_random_bytes
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C = Fore
except ImportError:
    class _Dummy:
        def __getattr__(self, name): return ""
    C = _Dummy()
    Style = _Dummy()

BANNER = rf"""{C.RED}=====================================================
{C.GREEN}   MARKOS X Ware V2.0  |  Yerli Veil Framework
{C.RED}====================================================={Style.RESET_ALL}"""

def ask_key():
    """Kullanıcıdan şifreleme anahtarı alır, yoksa rastgele üretir."""
    key = input(f"{C.YELLOW}[*] Anahtar (boş = rastgele 32 byte): {Style.RESET_ALL}").strip()
    if key:
        return hashlib.sha256(key.encode()).digest()  # istediği uzunlukta deterministik key
    return get_random_bytes(32)

def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR döngüsü — şifreleme katmanı 1"""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def b64e(data: bytes) -> str:
    """Base64 katmanı"""
    return base64.b64encode(data).decode()

# ------------------------------------------------------------------
# MODÜL 1: VEIL PAYLOAD GENERATOR
# ------------------------------------------------------------------
def veil_modulu():
    print(f"\n{C.YELLOW}[*] Veil Payload Generator başlatıldı...")
    if not HAS_CRYPTO:
        print(f"{C.RED}[!] pycryptodome kurulu değil: pip install pycryptodome")
        input("\nDevam için Enter...")
        return

    print(f"{C.CYAN}[1] Metin -> AES-256-CBC + XOR + Base64 katmanlı şifreli dosya")
    print(f"{C.CYAN}[2] Şifreli dosyayı çöz ve göster (decryptor testi)")
    sec = input(f"\n{C.RED}Seçim: {Style.RESET_ALL}").strip()

    if sec == "1":
        msg = input(f"{C.YELLOW}[*] Şifrelenecek veri/dosya yolu: {Style.RESET_ALL}").strip()
        if os.path.isfile(msg):
            with open(msg, "rb") as f:
                data = f.read()
        else:
            data = msg.encode()

        key = ask_key()
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Katmanlar: Base64( AES( XOR(data) ) )
        xor_key = get_random_bytes(16)
        xored = xor_bytes(data, xor_key)
        encrypted = cipher.encrypt(pad(xored, AES.block_size))
        blob = base64.b64encode(iv + xor_key + encrypted).decode()

        out_name = "payload_" + "".join(random.choices(string.ascii_lowercase, k=6)) + ".markos"
        with open(out_name, "w") as f:
            f.write(blob)

        # runtime decryptor üret
        decryptor = f'''#!/usr/bin/env python3
# MARKOS X Ware decryptor - geri yükleme anahtarı hex olarak saklanmalı
import base64, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = bytes.fromhex("{key.hex()}")
XOR_LEN = 16

def xor_bytes(d, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(d))

def decrypt(path):
    raw = base64.b64decode(open(path).read())
    iv, xor_key, payload = raw[:16], raw[16:16+XOR_LEN], raw[16+XOR_LEN:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    data = xor_bytes(unpad(cipher.decrypt(payload), AES.block_size), xor_key)
    return data

if __name__ == "__main__":
    import sys
    sys.stdout.buffer.write(decrypt(sys.argv[1]))
'''
        dec_name = out_name.replace(".markos", "_decryptor.py")
        with open(dec_name, "w") as f:
            f.write(decryptor)

        print(f"\n{C.GREEN}[+] Şifreli blob : {out_name}")
        print(f"{C.GREEN}[+] Decryptor    : {dec_name}")
        print(f"{C.YELLOW}[!] Anahtar (kaybetme, hex): {key.hex()}")

    elif sec == "2":
        path = input(f"{C.YELLOW}[*] .markos dosya yolu: {Style.RESET_ALL}").strip()
        key_hex = input(f"{C.YELLOW}[*] Anahtar (hex): {Style.RESET_ALL}").strip()
        try:
            key = bytes.fromhex(key_hex)
            raw = base64.b64decode(open(path).read())
            iv, xor_key, payload = raw[:16], raw[16:32], raw[32:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            data = xor_bytes(unpad(cipher.decrypt(payload), AES.block_size), xor_key)
            print(f"\n{C.GREEN}[+] Çözülen veri:\n")
            try:
                print(data.decode())
            except UnicodeDecodeError:
                sys.stdout.buffer.write(data)
        except Exception as e:
            print(f"{C.RED}[!] Hata: {e}")

    input(f"\n{C.CYAN}Devam için Enter...")

# ------------------------------------------------------------------
# MODÜL 2: SOFTWARE - SİBER GÜVENLİK TARAYICISI
# ------------------------------------------------------------------
SUSPICIOUS_PROCS = ["mimikatz", "nc.exe", "ncat", "netcat", "hydra",
                    "wce", "pwdump", "procdump", "cobalt", "beacon"]
SUSPICIOUS_PORTS = {4444, 5555, 1234, 31337, 6667, 9001}  # klasik C2 portları

def software_modulu():
    print(f"\n{C.YELLOW}[*] SoftWare - Sistem Güvenlik Taraması")
    print(f"{C.CYAN}[1] Şüpheli süreç taraması")
    print(f"{C.CYAN}[2] Aktif bağlantı / C2 port analizi")
    print(f"{C.CYAN}[3] Startup kalıcılık kontrolü")
    print(f"{C.CYAN}[4] Dosya entropy + hash analizi (packer tespiti)")
    sec = input(f"\n{C.RED}Seçim: {Style.RESET_ALL}").strip()

    if sec == "1":
        try:
            out = subprocess.check_output(
                ["tasklist"] if platform.system() == "Windows" else ["ps", "aux"],
                text=True, errors="ignore")
            found = False
            for line in out.splitlines():
                low = line.lower()
                if any(s in low for s in SUSPICIOUS_PROCS):
                    print(f"{C.RED}[!] ŞÜPHELİ: {line.strip()}")
                    found = True
            if not found:
                print(f"{C.GREEN}[+] Şüpheli süreç bulunamadı.")
        except Exception as e:
            print(f"{C.RED}[!] Hata: {e}")

    elif sec == "2":
        try:
            out = subprocess.check_output(
                ["netstat", "-ano"] if platform.system() == "Windows" else ["ss", "-tunap"],
                text=True, errors="ignore")
            found = False
            for line in out.splitlines():
                for p in SUSPICIOUS_PORTS:
                    if f":{p} " in line or f":{p}\t" in line:
                        print(f"{C.RED}[!] C2 PORTU ({p}): {line.strip()}")
                        found = True
            if not found:
                print(f"{C.GREEN}[+] Şüpheli bağlantı yok.")
        except Exception as e:
            print(f"{C.RED}[!] Hata: {e}")

    elif sec == "3":
        if platform.system() == "Windows":
            startup = os.path.join(os.environ.get("APPDATA", ""),
                                   r"Microsoft\Windows\Start Menu\Programs\Startup")
            reg = subprocess.run(["reg", "query",
                                  r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"],
                                 capture_output=True, text=True)
            print(reg.stdout)
        else:
            for p in ["~/.bashrc", "~/.profile", "/etc/cron.d"]:
                path = os.path.expanduser(p)
                if os.path.exists(path):
                    print(f"{C.CYAN}[*] {path} son 5 satır:")
                    with open(path, errors="ignore") as f:
                        print("".join(f.readlines()[-5:]))

    elif sec == "4":
        path = input(f"{C.YELLOW}[*] Dosya yolu: {Style.RESET_ALL}").strip()
        try:
            with open(path, "rb") as f:
                data = f.read(1024 * 1024)
            md5 = hashlib.md5(data).hexdigest()
            sha256 = hashlib.sha256(data).hexdigest()
            if not data:
                raise ValueError("boş dosya")
            freq = {b: 0 for b in range(256)}
            for b in data:
                freq[b] += 1
            n = len(data)
            entropy = -sum((c / n) * __import__("math").log2(c / n)
                           for c in freq.values() if c)
            print(f"{C.GREEN}[+] MD5    : {md5}")
            print(f"{C.GREEN}[+] SHA256 : {sha256}")
            print(f"{C.GREEN}[+] Entropy: {entropy:.3f} / 8.0")
            if entropy > 7.2:
                print(f"{C.RED}[!] Yüksek entropy — dosya şifreli/pakellenmiş olabilir.")
        except Exception as e:
            print(f"{C.RED}[!] Hata: {e}")

    input(f"\n{C.CYAN}Devam için Enter...")

# ------------------------------------------------------------------
# MODÜL 3: ŞAKA MODÜLÜ (gizli çıkış: 3x ESC)
# ------------------------------------------------------------------
def troll_modulu():
    print(f"\n{C.RED}[🚨 CRITICAL ERROR] SYSTEM_FAILURE_DETECTED!")
    print(f"{C.YELLOW}[*] Sahte virüs simülasyonu başlatılıyor... (çıkış: 3x ESC)")
    time.sleep(1.5)
    esc_count = 0
    try:
        if platform.system() == "Windows":
            import msvcrt
            while True:
                os.system("cls")
                print(f"{C.RED}###################################################")
                print(f"{C.RED}#         ⚠️  WNCRY_RANSOMWARE_V4.0  ⚠️           #")
                print(f"{C.RED}###################################################")
                print(f"{C.RED}#  TÜM SİSTEM DOSYALARINIZ ŞİFRELENMİŞTİR!        #")
                print(f"{C.RED}#  SİSTEMİNİZ MARKOS X WARE TARAFINDAN ELE GEÇİRİLDİ #")
                print(f"{C.RED}###################################################")
                print(f"\n{C.YELLOW}[!] Dosyalar imha ediliyor... Lütfen bekleyin...")
                print(f"{C.RED}[ERROR 0x{random.randint(1000,9999)}] svchost.exe FAILED")
                t0 = time.time()
                while time.time() - t0 < 0.7:
                    if msvcrt.kbhit() and msvcrt.getch() == b"\x1b":
                        esc_count += 1
                        if esc_count >= 3:
                            raise KeyboardInterrupt
                    else:
                        esc_count = 0
        else:
            import tty, termios, select
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            tty.setraw(fd)
            try:
                while True:
                    os.system("clear")
                    print(f"{C.RED}###################################################")
                    print(f"{C.RED}#         ⚠️  WNCRY_RANSOMWARE_V4.0  ⚠️           #")
                    print(f"{C.RED}#  TÜM SİSTEM DOSYALARINIZ ŞİFRELENMİŞTİR!        #")
                    print(f"{C.RED}###################################################")
                    t0 = time.time()
                    while time.time() - t0 < 0.7:
                        r, _, _ = select.select([sys.stdin], [], [], 0.1)
                        if r and sys.stdin.read(1) == "\x1b":
                            esc_count += 1
                            if esc_count >= 3:
                                raise KeyboardInterrupt
                        else:
                            esc_count = 0
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{C.GREEN}[✓] Şaka modülü kapatıldı. Sistemin güvende kanka :)")
        time.sleep(2)

# ------------------------------------------------------------------
def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(BANNER)
        print(f"{C.GREEN} 1) Veil Payload Generator (gerçek)")
        print(f"{C.GREEN} 2) SoftWare - Güvenlik Tarayıcı (gerçek)")
        print(f"{C.GREEN} 3) Şaka Modülü (troll)")
        print(f"{C.GREEN} 0) Exit")
        sec = input(f"\n{C.RED}Seçiminiz: {Style.RESET_ALL}").strip()
        if sec == "1":
            veil_modulu()
        elif sec == "2":
            software_modulu()
        elif sec == "3":
            troll_modulu()
        elif sec == "0":
            print(f"{C.RED}Çıkılıyor...")
            time.sleep(1)
            sys.exit()
        else:
            print(f"{C.RED}[!] Geçersiz seçenek!")
            input("\nDevam için Enter...")

if __name__ == "__main__":
    main()
