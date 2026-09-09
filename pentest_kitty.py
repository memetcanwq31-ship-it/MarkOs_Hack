#!/usr/bin/env python3
# ============================================================
#  PENTEST KİTİ v1.0 — Birleşik Ağ & ICS Keşif Aracı
#  Yalnızca SAHİP OLDUĞUN veya test için YETKİN olduğun
#  ağlarda kullan. Modbus aracı salt-okunurdur.
# ============================================================
import os
import sys
import socket
import struct
import concurrent.futures as cf

# ---------- ANSI Renkler (Termux uyumlu) ----------
R, G, Y, C, W = "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[97m"
B, S = "\033[1m", "\033[0m"

# ---------- Ortak yardımcılar ----------

def temizle():
    os.system("clear")


def banner():
    print(f"{R}{B}{'='*60}")
    print(f"{R}{B}   PENTEST KİTİ v1.0 — Ağ + IoT + ICS Keşif")
    print(f"{R}{B}   Sadece yetkili olduğun ağlarda kullan!")
    print(f"{R}{B}{'='*60}{S}")


def port_tara(hedef, port, timeout=0.5):
    try:
        with socket.socket() as s:
            s.settimeout(timeout)
            if s.connect_ex((hedef, port)) == 0:
                return port
    except Exception:
        pass
    return None


def hedefleri_al():
    """Ağ örneğiği veya tek IP alır -> IP listesi döndürür."""
    ag = input(f"{C}Ağ örneği (örn: 192.168.1.) veya tek IP: {W}").strip()
    if not ag:
        print(f"{R}[!] Boş girdi.")
        return None
    if ag.endswith(".") and ag.count(".") == 3:
        return [f"{ag}{i}" for i in range(1, 255)]
    if ag.count(".") == 3:
        return [ag]
    print(f"{R}[!] Format: 192.168.1. veya 192.168.1.10")
    return None


# ============================================================
#  MODÜL 1 — IoT / Kamera Ağ Tarayıcı
# ============================================================
KAMERA_PORTLARI = {
    554:   "RTSP (kamera canlı yayın)",
    8000:  "Hikvision",
    37777: "Dahua",
    34567: "Hikvision alternatif",
    80:    "HTTP (web arayüzü)",
    443:   "HTTPS",
    23:    "Telnet (kötü yapılandırma işareti)",
    9100:  "Yazıcı (yanlışlıkla açık)",
}


def kamera_tara():
    hedefler = hedefleri_al()
    if not hedefler:
        return

    print(f"{Y}[*] {len(hedefler)} IP taranıyor (birkaç dakika sürebilir)...{S}")
    bulunanlar = []

    def isle(ip):
        for kontrol in (80, 554):
            if port_tara(ip, kontrol, 0.3):
                return ip
        return None

    with cf.ThreadPoolExecutor(max_workers=100) as ex:
        for r in ex.map(isle, hedefler):
            if r:
                bulunanlar.append(r)
                print(f"  {G}[+] Canlı cihaz: {r}{S}")

    if not bulunanlar:
        print(f"{Y}[-] Canlı cihaz bulunamadı.{S}")
        return

    print(f"\n{G}{B}=== DETAYLI TARAMA ==={S}")
    for ip in bulunanlar:
        print(f"\n{W}{ip}:{S}")
        with cf.ThreadPoolExecutor(max_workers=20) as ex:
            acik = [p for p in KAMERA_PORTLARI if port_tara(ip, p, 0.5)]
        for p in acik:
            isaret = f" {Y}⚠ Varsayılan şifre denemesi için hedef olabilir{S}" \
                     if p in (554, 8000, 37777, 23) else ""
            print(f"  {p:>5}/tcp  {C}{KAMERA_PORTLARI[p]}{S}{isaret}")
        if not acik:
            print("  (bilinen portlar kapalı)")
    print(f"\n{Y}[!] Telnet/RTSP açık cihazlar varsayılan şifre kullanan "
          f"cihazlar olabilir — SAHİP oldıklarını düzelt, başkalarına dokunma.{S}")


# ============================================================
#  MODÜL 2 — Modbus (Elektrik/PLC) Salt-Okuma İstemcisi
# ============================================================

def modbus_okuma(ip, unit_id=1, baslangic=0, adet=10, port=502):
    tid = 0x1234
    pdu = struct.pack(">BHH", 0x03, baslangic, adet)  # 0x03 = Read Holding Registers
    apdu = struct.pack(">BBH", unit_id, 0, len(pdu)) + pdu
    paket = struct.pack(">HHH", tid, 0, len(apdu)) + apdu

    with socket.socket() as s:
        s.settimeout(3)
        s.connect((ip, port))
        s.sendall(paket)
        yanit = s.recv(260)

    if len(yanit) < 9 or yanit[7] & 0x80:
        print(f"{R}[!] Hata yanıtı veya kısa cevap: {yanit.hex()}{S}")
        return
    adet_bayt = yanit[8]
    degerler = struct.unpack(f">{adet_bayt // 2}H", yanit[9:9 + adet_bayt])
    for i, v in enumerate(degerler):
        print(f"  Register {baslangic + i}: {v} (0x{v:04X})")


def modbus_tara():
    ip = input(f"{C}PLC IP (kendi lab cihazın / simülatörün): {W}").strip()
    if not ip:
        print(f"{R}[!] Boş girdi.")
        return
    try:
        unit = input(f"{C}Unit ID (Enter=1): {W}").strip()
        unit = int(unit) if unit else 1
        basla = input(f"{C}Başlangıç register (Enter=0): {W}").strip()
        basla = int(basla) if basla else 0
        adet = input(f"{C}Register adedi (Enter=10): {W}").strip()
        adet = int(adet) if adet else 10
    except ValueError:
        print(f"{R}[!] Sayı girişi hatalı.")
        return

    print(f"{Y}[*] Port 502 kontrol ediliyor...{S}")
    if not port_tara(ip, 502, 1.0):
        print(f"{R}[!] Port 502 kapalı — Modbus TCP cihazı görünmüyor.{S}")
        return

    print(f"{G}[+] Modbus açık, salt-okuma sorgusu gönderiliyor...{S}")
    try:
        modbus_okuma(ip, unit, basla, adet)
    except Exception as e:
        print(f"{R}[!] Bağlantı hatası: {e}{S}")
    print(f"{Y}[!] Not: Sadece OKUMA yapıldı. Yazma (fonksiyon 0x06/0x10) "
          f"üretim sistemine zarar verir — bu araç bilinçli olarak yazma yapmaz.{S}")


# ============================================================
#  BONUS — Modbus port tarama (bir ağdaki PLC'leri bul)
# ============================================================

def modbus_bul():
    hedefler = hedefleri_al()
    if not hedefler:
        return
    print(f"{Y}[*] Port 502 taranıyor...{S}")
    with cf.ThreadPoolExecutor(max_workers=100) as ex:
        for ip in hedefler:
            if port_tara(ip, 502, 0.3):
                print(f"  {G}[+] Modbus cihazı bulundu: {ip}:502{S}")


# ============================================================
#  ANA MENÜ
# ============================================================
MODULLER = {
    "1": ("IoT / Kamera Ağ Tarayıcı", kamera_tara),
    "2": ("Modbus PLC Okuyucu (salt-okuma)", modbus_tara),
    "3": ("Ağdaki Modbus/PLC Cihazlarını Bul", modbus_bul),
}


def main():
    while True:
        temizle()
        banner()
        for k, (ad, _) in MODULLER.items():
            print(f" {W}[{k}] {C}{ad}")
        print(f" {W}[0] Çıkış\n{S}")

        secim = input(f"{G}Seçim: {W}").strip()
        if secim == "0":
            print(f"{G}Çıkılıyor...{S}")
            sys.exit(0)
        if secim in MODULLER:
            MODULLER[secim][1]()
        else:
            print(f"{R}[!] Geçersiz seçim.{S}")

        input(f"\n{Y}Menüye dönmek için ENTER'a bas...{S}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}Kesinti algılandı, çıkılıyor...{S}")
        sys.exit(0)
