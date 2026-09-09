import os
import sys
import socket
import struct
import concurrent.futures as cf

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
B = "\033[1m"
S = "\033[0m"


def temizle():
    os.system("clear")


def banner():
    print(R + B + "=" * 60)
    print(R + B + "   PENTEST KITI v1.0 - Ag + IoT + ICS Kesif")
    print(R + B + "   Sadece yetkili aglarda kullan!")
    print(R + B + "=" * 60 + S)


def port_tara(hedef, port, timeout=0.5):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        sonuc = s.connect_ex((hedef, port))
        s.close()
        if sonuc == 0:
            return port
    except Exception:
        pass
    return None


def hedefleri_al():
    ag = input(C + "Ag ornegi (orn: 192.168.1.) veya tek IP: " + W).strip()
    if not ag:
        print(R + "[!] Bos girdi." + S)
        return None
    if ag.endswith(".") and ag.count(".") == 3:
        return [ag + str(i) for i in range(1, 255)]
    if ag.count(".") == 3:
        return [ag]
    print(R + "[!] Format: 192.168.1. veya 192.168.1.10" + S)
    return None


KAMERA_PORTLARI = {
    554: "RTSP (kamera canli yalin)",
    8000: "Hikvision",
    37777: "Dahua",
    34567: "Hikvision alternatif",
    80: "HTTP (web arayuzu)",
    443: "HTTPS",
    23: "Telnet (kotu yapilandirma)",
    9100: "Yazici",
}


def kamera_tara():
    hedefler = hedefleri_al()
    if not hedefler:
        return
    print(Y + "[*] " + str(len(hedefler)) + " IP taraniyor..." + S)
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
                print("  " + G + "[+] Canli cihaz: " + r + S)

    if not bulunanlar:
        print(Y + "[-] Canli cihaz bulunamadi." + S)
        return

    print("\n" + G + B + "=== DETAYLI TARAMA ===" + S)
    for ip in bulunanlar:
        print("\n" + W + ip + ":" + S)
        with cf.ThreadPoolExecutor(max_workers=20) as ex:
            acik = []
            for p in KAMERA_PORTLARI:
                if port_tara(ip, p, 0.5):
                    acik.append(p)
        for p in acik:
            print("  " + str(p).rjust(5) + "/tcp  " + C + KAMERA_PORTLARI[p] + S)
        if not acik:
            print("  (bilinen portlar kapali)")


def modbus_okuma(ip, unit_id=1, baslangic=0, adet=10, port=502):
    tid = 0x1234
    pdu = struct.pack(">BHH", 0x03, baslangic, adet)
    apdu = struct.pack(">BBH", unit_id, 0, len(pdu)) + pdu
    paket = struct.pack(">HHH", tid, 0, len(apdu)) + apdu
    s = socket.socket()
    s.settimeout(3)
    s.connect((ip, port))
    s.sendall(paket)
    yanit = s.recv(260)
    s.close()
    if len(yanit) < 9 or (yanit[7] & 0x80):
        print(R + "[!] Hata yaniti: " + yanit.hex() + S)
        return
    adet_bayt = yanit[8]
    degerler = struct.unpack(">" + "H" * (adet_bayt // 2), yanit[9:9 + adet_bayt])
    for i in range(len(degerler)):
        print("  Register " + str(baslangic + i) + ": " + str(degerler[i]))


def modbus_tara():
    ip = input(C + "PLC IP (kendi lab cihazin): " + W).strip()
    if not ip:
        print(R + "[!] Bos girdi." + S)
        return
    print(Y + "[*] Port 502 kontrol ediliyor..." + S)
    if not port_tara(ip, 502, 1.0):
        print(R + "[!] Port 502 kapali - Modbus cihazi gorunmuyor." + S)
        return
    print(G + "[+] Modbus acik, salt-okuma sorgusu gonderiliyor..." + S)
    try:
        modbus_okuma(ip)
    except Exception as e:
        print(R + "[!] Baglanti hatasi: " + str(e) + S)


def modbus_bul():
    hedefler = hedefleri_al()
    if not hedefler:
        return
    print(Y + "[*] Port 502 taraniyor..." + S)
    for ip in hedefler:
        if port_tara(ip, 502, 0.3):
            print("  " + G + "[+] Modbus cihazi bulundu: " + ip + ":502" + S)


MODULLER = {
    "1": ("IoT / Kamera Ag Tarayici", kamera_tara),
    "2": ("Modbus PLC Okuyucu (salt-okuma)", modbus_tara),
    "3": ("Agdaki Modbus Cihazlarini Bul", modbus_bul),
}


def main():
    while True:
        temizle()
        banner()
        for k in MODULLER:
            print(" " + W + "[" + k + "] " + C + MODULLER[k][0] + S)
        print(" " + W + "[0] Cikis\n" + S)
        secim = input(G + "Secim: " + W).strip()
        if secim == "0":
            print(G + "Cikiliyor..." + S)
            sys.exit(0)
        if secim in MODULLER:
            MODULLER[secim][1]()
        else:
            print(R + "[!] Gecersiz secim." + S)
        input("\n" + Y + "Menu icin ENTER'a bas..." + S)


main()
