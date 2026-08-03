#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTP / SMS Flood Koruma Testi (kendi uygulaman için)

Soru: Uygulamamın SMS gönderim uç noktasını bir saldırgan sınırsız
çağırabiliyor mu? (rate-limit, captcha, per-IP/per-numara limit var mı?)

Kullanım:
    python3 sms_flood_test.py https://uygulaman.com/api/otp-gonder 905551234567 -n 20 -c 5
    # -n: toplam istek, -c: eşzamanlılık
"""

import sys
import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def tek_istek(url, payload, ek_headers, timeout=10):
    """Tek OTP isteği atar; (http_kodu, gecikme_ms, govde) döndürür."""
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": UA}
    headers.update(ek_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            g = r.read(200).decode("utf-8", "replace")
            return r.status, round((time.monotonic() - t0) * 1000), g
    except urllib.error.HTTPError as e:
        g = e.read(200).decode("utf-8", "replace")
        return e.code, round((time.monotonic() - t0) * 1000), g
    except Exception as e:
        return -1, round((time.monotonic() - t0) * 1000), str(e)


def flood_test(url, payload, ek_headers, toplam, eszaman):
    """toplam isteği eszaman kadar paralel işçiyle atar."""
    sonuclar = []
    with ThreadPoolExecutor(max_workers=eszaman) as havuz:
        gelecekler = [havuz.submit(tek_istek, url, payload, ek_headers)
                      for _ in range(toplam)]
        for g in gelecekler:
            sonuclar.append(g.result())
    return sonuclar


def raporla(sonuclar, toplam):
    print(f"\n{'='*52}")
    print(f"Toplam istek : {toplam}")

    kodlar = {}
    for kod, _, _ in sonuclar:
        kodlar[kod] = kodlar.get(kod, 0) + 1

    print("HTTP dağılımı :")
    for kod in sorted(kodlar):
        print(f"  {kod:<6} -> {kodlar[kod]} istek")

    gecikmeler = [g for _, g, _ in sonuclar]
    if gecikmeler:
        print(f"Gecikme       : ort {sum(gecikmeler)//len(gecikmeler)} ms, "
              f"maks {max(gecikmeler)} ms")

    # Analiz
    basarili = sum(n for k, n in kodlar.items() if 200 <= k < 300)
    engellendi = sum(n for k, n in kodlar.items() if k in (429, 400, 403))

    print("\nSONUÇ:")
    if basarili == toplam:
        print("  [KRİTİK] Tüm istekler başarılı -> rate-limit YOK.")
        print("  Saldırgan sistemini SMS masraf makinesi olarak kullanabilir.")
        print("  Öneri: IP + numara bazlı limit, captcha, cooldown ekle.")
    elif engellendi > 0 and basarili == 0:
        print("  [İYİ] Tüm istekler engellendi -> koruma aktif.")
    elif engellendi > 0:
        engel_an = None
        for i, (kod, _, _) in enumerate(sonuclar):
            if kod in (429, 400, 403):
                engel_an = i + 1
                break
        print(f"  [ORTA] İlk {basarili} istek geçti, sonra engel geldi "
              f"(~{engel_an}. istekte).")
        print("  Eşik değeri yüksek; toplu saldırıda masraf yine oluşur.")
    else:
        print("  [BELİRSİZ] Yanıtları gözden geçir; 2xx sayısına dikkat et.")


def main(argv):
    if len(argv) < 2:
        print("Kullanım: python3 sms_flood_test.py <URL> <telefon> [-n sayi] [-c eszaman]")
        print("Örnek  : python3 sms_flood_test.py https://uygulaman.com/api/otp 905551234567 -n 20 -c 5")
        print("Uyarı  : Yalnızca KENDİ uygulamanı test et.")
        return 1

    url, telefon = argv[0], argv[1]
    toplam, eszaman = 10, 3

    i = 2
    while i < len(argv):
        if argv[i] == "-n" and i + 1 < len(argv):
            toplam = int(argv[i + 1]); i += 2
        elif argv[i] == "-c" and i + 1 < len(argv):
            eszaman = int(argv[i + 1]); i += 2
        else:
            i += 1

    # Uygulamanın beklediği alan adına göre düzenle:
    payload = {"phone": telefon, "channel": "sms"}
    ek = {}  # {"Authorization": "Bearer ..."} gerekirse buraya

    print(f"[*] {url} -> {telefon} | {toplam} istek, {eszaman} eşzamanlı")
    sonuclar = flood_test(url, payload, ek, toplam, eszaman)
    raporla(sonuclar, toplam)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
