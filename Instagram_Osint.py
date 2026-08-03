#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Kamu Profil Bilgi Aracı (OSINT)

- SADECE herkese açık verileri okur; hiçbir şey göndermez/değiştirmez.
- Bağımlılık YOK: yalnızca Python 3 standart kütüphanesi.
- Kullanım:
    python3 ig_info.py kullanici_adi
    python3 ig_info.py kullanici_adi --json
    python3 ig_info.py kullanici_adi -o cikti.json
    HTTPS_PROXY=http://127.0.0.1:8080 python3 ig_info.py kullanici_adi
"""

import os
import sys
import json
import time
import ssl
import socket
import http.client
from urllib.parse import urlparse

APP_ID = "936619743392459"          # Instagram web istemcisinin herkese açık app id'si
HOST = "i.instagram.com"
PORT = 443
TIMEOUT = 10
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


# ---------- socket: ağ katmanı ----------

def tcp_check(host=HOST, port=PORT, timeout=5):
    """Hedef sunucuya gerçek TCP bağlantısı kurar; (host, port) döndürür."""
    with socket.create_connection((host, port), timeout=timeout) as s:
        return s.getpeername()


def proxy_tunnel(proxy_url, target_host, target_port, timeout=TIMEOUT):
    """HTTP CONNECT tüneli açar ve TLS sarılmış socket döndürür."""
    p = urlparse(proxy_url if "://" in proxy_url else "http://" + proxy_url)
    if p.scheme != "http":
        raise ValueError("Yalnızca http proxy desteklenir")
    proxy_host, proxy_port = p.hostname, (p.port or 8080)

    raw = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    req = (f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
           f"Host: {target_host}:{target_port}\r\n\r\n").encode()
    raw.sendall(req)

    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = raw.recv(4096)
        if not chunk:
            break
        buf += chunk

    status_line = buf.split(b"\r\n", 1)[0]
    if b" 200 " not in status_line:
        raw.close()
        raise OSError(f"Proxy CONNECT reddedildi: {status_line.decode(errors='replace')}")

    ctx = ssl.create_default_context()
    return ctx.wrap_socket(raw, server_hostname=target_host)


class ProxyHTTPSConnection(http.client.HTTPSConnection):
    """İsteğe bağlı HTTP proxy tüneli destekli HTTPS bağlantısı."""

    def __init__(self, host, port, timeout=TIMEOUT, proxy=None):
        super().__init__(host, port, timeout=timeout)
        self._proxy = proxy

    def connect(self):
        if self._proxy:
            self.sock = proxy_tunnel(self._proxy, self.host, self.port, self.timeout)
        else:
            super().connect()


# ---------- HTTP katmanı ----------

def fetch_profile(username, token=None, proxy=None):
    """Instagram web profil endpoint'inden herkese açık bilgiyi çeker."""
    try:
        remote = tcp_check()
        print(f"[*] Bağlantı kuruldu -> {remote[0]}:{remote[1]}")
    except OSError as e:
        return {"error": f"Instagram'a bağlanılamadı: {e}"}

    conn = ProxyHTTPSConnection(HOST, PORT, timeout=TIMEOUT, proxy=proxy)
    path = f"/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "x-ig-app-id": APP_ID,
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    t0 = time.monotonic()
    try:
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8", "replace")
        status = resp.status
    except Exception as e:
        return {"error": f"HTTP isteği başarısız: {e}"}
    finally:
        conn.close()
    elapsed = time.monotonic() - t0

    if status == 200:
        try:
            user = json.loads(raw)["data"]["user"]
        except (ValueError, KeyError, TypeError):
            return {"error": "Yanıt JSON olarak çözümlenemedi", "http": status}
        if user is None:
            return {"error": f"@{username} bulunamadı", "http": status}
        return {
            "username":     user["username"],
            "full_name":    user["full_name"],
            "is_private":   user["is_private"],
            "is_verified":  user["is_verified"],
            "followers":    user["edge_followed_by"]["count"],
            "following":    user["edge_follow"]["count"],
            "posts":        user["edge_owner_to_timeline_media"]["count"],
            "biography":    user.get("biography", ""),
            "external_url": user.get("external_url"),
            "latency_ms":   round(elapsed * 1000),
        }

    if status == 404:
        return {"error": f"@{username} bulunamadı", "http": 404}

    if status in (400, 429) and "login" in raw.lower():
        return {"error": "login_required: çok sık istek atıldı, birkaç dakika bekleyip tekrar dene",
                "http": status}

    return {"error": f"Beklenmeyen HTTP {status}", "http": status, "raw": raw[:300]}


# ---------- çıktı ----------

def format_table(data):
    if "error" in data:
        return f"[!] {data['error']}"
    satirlar = [
        f"Kullanıcı     : @{data['username']}",
        f"Ad Soyad      : {data['full_name']}",
        f"Gizli hesap   : {'Evet' if data['is_private'] else 'Hayır'}",
        f"Doğrulanmış   : {'Evet' if data['is_verified'] else 'Hayır'}",
        f"Takipçi       : {data['followers']:,}",
        f"Takip         : {data['following']:,}",
        f"Gönderi       : {data['posts']:,}",
        f"Biyografi     : {data['biography']}",
    ]
    if data.get("external_url"):
        satirlar.append(f"Dış bağlantı  : {data['external_url']}")
    satirlar.append(f"Yanıt süresi  : {data['latency_ms']} ms")
    return "\n".join(satirlar)


# ---------- giriş noktası ----------

def parse_args(argv):
    """sys.argv'yi ayrıştırır: konumlar, -o, --json."""
    konumlar, out_file, raw_json = [], None, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "-o":
            if i + 1 >= len(argv):
                print("[-o] bir dosya yolu bekler", file=sys.stderr)
                sys.exit(2)
            out_file = argv[i + 1]
            i += 2
            continue
        if a == "--json":
            raw_json = True
        elif a.startswith("-"):
            print(f"Bilinmeyen seçenek: {a}", file=sys.stderr)
            sys.exit(2)
        else:
            konumlar.append(a)
        i += 1
    return konumlar, out_file, raw_json


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    konumlar, out_file, raw_json = parse_args(argv)

    if not konumlar:
        print("Kullanım: python3 ig_info.py <kullanici_adi> [--json] [-o dosya.json]")
        print("Örnek  : python3 ig_info.py elonmusk")
        print("Not    : Bu araç SADECE herkese açık veriyi okur; takipçi eklemez.")
        return 1

    username = konumlar[0].lstrip("@").strip()

    # os.environ: ortam değişkenlerinden opsiyonel ayarlar
    token = os.environ.get("IG_TOKEN")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    print(f"[*] @{username} sorgulanıyor ...")
    sonuc = fetch_profile(username, token=token, proxy=proxy)

    if raw_json:
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        print(format_table(sonuc))

    # os: sonucu dosyaya yaz
    if out_file:
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(sonuc, f, indent=2, ensure_ascii=False)
            print(f"[+] {os.path.abspath(out_file)} kaydedildi")
        except OSError as e:
            print(f"[!] Dosya yazılamadı: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
