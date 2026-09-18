#!/usr/bin/env python3
# N-SPEARSTION v3.2 - %100 Gerçek Veri + Cihaz Tespiti
import os
import sys
import socket
import struct
import time
import re
import subprocess
import threading

try:
    import psutil
    PSUTIL_VAR = True
except ImportError:
    PSUTIL_VAR = False

try:
    import requests
    REQUESTS_VAR = True
except ImportError:
    REQUESTS_VAR = False

try:
    from scapy.all import ARP, Ether, srp
    SCAPY_VAR = True
except Exception:
    SCAPY_VAR = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    YESIL = Fore.GREEN + Style.BRIGHT
    MAVI = Fore.CYAN + Style.BRIGHT
    KIRMIZI = Fore.RED + Style.BRIGHT
    BEYAZ = Fore.WHITE + Style.BRIGHT
    MOR = Fore.MAGENTA + Style.BRIGHT
    SARI = Fore.YELLOW + Style.BRIGHT
except ImportError:
    YESIL = MAVI = KIRMIZI = BEYAZ = MOR = SARI = ""

LOGO = rf"""
{YESIL}  ███▄    █        ██████  ██▓███  ▓█████  ▄▄▄       ██▀███
{YESIL}  ██ ▀█   █      ▒██    ▒ ▓██░  ██▒▓█   ▀ ▒████▄    ▓██ ▒ ██▒
{YESIL} ▓██  ▀█ ██▒     ░ ▓██▄   ▓██░ ██▓▒▒███   ▒██  ▀█▄  ▓██ ░▄█ ▒
{YESIL} ▓██▒  ▐▌██▒       ▒   ██▒▒██▄█▓▒ ▒▒▓█  ▄ ░██▄▄▄▄██ ▒██▀▀█▄
{YESIL} ▒██░   ▓██░     ▒██████▒▒▒██▒ ░  ░░▒████▒ ▓█   ▓██▒░██▓ ▒██▒
{MOR} ░ ▒░   ▒ ▒      ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░░ ▒░ ░ ▒▒   ▓▒█░░ ▒▓ ░▒▓░
{BEYAZ} -----------------------------------------------------------
{BEYAZ}       ★ N-SPEARSTION REAL-TIME NETWORK INTERFACE v3.2 ★
{BEYAZ}  Gerçek Veri + Yakın Cihaz Tespit Motoru
{KIRMIZI} [*] Yakin Hackleme ~ Yakin Analiz Araclari Eklenecektir 
{KIRMIZI} [!] Tekrar Hatirlatmak İsterim Bu Tamamen Egtim Amaclidir
"""

# ==========================================
# GENEL YARDIMCI FONKSİYONLAR
# ==========================================

def temizle():
    os.system('clear' if os.name == 'posix' else 'cls')

def mac_adreslerini_topla():
    sonuclar = {}
    if not PSUTIL_VAR:
        return {"/!\\ psutil kurulu değil": "-"}
    try:
        adresler = psutil.net_if_addrs()
    except Exception:
        return {"Hata": "Arayüzler okunamadı"}
    for arayuz, addr_list in adresler.items():
        mac = None
        if os.name == 'posix':
            yol = f"/sys/class/net/{arayuz}/address"
            if os.path.exists(yol):
                try:
                    with open(yol) as f:
                        mac = f.read().strip().upper()
                except Exception:
                    pass
        if not mac:
            for addr in addr_list:
                if getattr(psutil, 'AF_LINK', None) is not None and addr.family == psutil.AF_LINK:
                    mac = addr.address.upper()
                    break
                if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', addr.address):
                    mac = addr.address.upper().replace('-', ':')
                    break
        if mac in (None, '', '00:00:00:00:00:00'):
            mac = "Yok (sanal/loopback)"
        sonuclar[arayuz] = mac
    return sonuclar

def aktif_baglanti_cozumle():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3)
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def public_ip_ve_konum():
    if not REQUESTS_VAR:
        return {"hata": "requests kütüphanesi kurulu değil"}
    try:
        r = requests.get("http://ip-api.com/json/",
                         params={"fields": "status,query,country,city,isp,org,as,lat,lon"},
                         timeout=8)
        d = r.json()
        if d.get("status") == "success":
            return d
    except Exception:
        pass
    try:
        r = requests.get("https://ipinfo.io/json", timeout=8)
        d = r.json()
        if d.get("ip"):
            lat, lon = (d.get("loc", ",")).split(",")
            return {"query": d["ip"], "city": d.get("city", "-"),
                    "country": d.get("country", "-"), "isp": d.get("org", "-"),
                    "org": d.get("org", "-"), "as": d.get("org", "-"),
                    "lat": lat, "lon": lon}
    except Exception:
        pass
    return {"hata": "Public IP alınamadı - internet bağlantısını kontrol edin"}

def varsayilan_gateway():
    if os.name == 'posix':
        try:
            with open('/proc/net/route') as f:
                next(f)
                for satir in f:
                    p = satir.strip().split()
                    if len(p) > 7 and p[1] == '00000000':
                        gw = socket.inet_ntoa(struct.pack('<L', int(p[2], 16)))
                        return gw, p[0]
        except (FileNotFoundError, PermissionError, ValueError):
            pass
    else:
        try:
            cikti = os.popen('route print -4 0.0.0.0').read()
            for satir in cikti.splitlines():
                p = satir.split()
                if len(p) >= 5 and p[0] == '0.0.0.0' and p[1] == '0.0.0.0':
                    try:
                        socket.inet_aton(p[2])
                        return p[2], p[3]
                    except (socket.error, IndexError):
                        continue
        except Exception:
            pass
    return None, None

def dns_sunuculari():
    dnsler = []
    if os.name == 'posix':
        try:
            with open('/etc/resolv.conf') as f:
                for satir in f:
                    satir = satir.strip()
                    if satir.startswith('nameserver'):
                        dnsler.append(satir.split()[1])
        except (FileNotFoundError, PermissionError):
            pass
    else:
        try:
            cikti = os.popen('ipconfig /all').read()
            for satir in cikti.splitlines():
                if 'DNS Sunucular' in satir or 'DNS Servers' in satir:
                    val = satir.split(':', 1)[1].strip()
                    if val:
                        dnsler.append(val)
        except Exception:
            pass
    return list(dict.fromkeys(dnsler)) or ["Bulunamadı"]

def tum_arayuzleri_tara():
    if not PSUTIL_VAR:
        return []
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
    except Exception:
        return []
    harita = []
    for ad, adresler in interfaces.items():
        v4, v6, mask = "Yok", "Yok", "Yok"
        for addr in adresler:
            try:
                if addr.family == socket.AF_INET:
                    v4 = addr.address
                    mask = addr.netmask or "Yok"
                elif addr.family == socket.AF_INET6:
                    v6 = addr.address.split('%')[0]
            except Exception:
                continue
        try:
            calisiyor = stats[ad].isup if ad in stats else False
            hiz = f"{stats[ad].speed} Mbps" if ad in stats and stats[ad].speed > 0 else "-"
        except Exception:
            calisiyor, hiz = False, "-"
        harita.append({"kart": ad, "ipv4": v4, "ipv6": v6, "mask": mask,
                       "durum": "ÇALIŞIYOR" if calisiyor else "KAPALI", "hiz": hiz})
    return harita

def arp_tablosu():
    girdiler = []
    if os.name == 'posix':
        try:
            with open('/proc/net/arp') as f:
                next(f)
                for satir in f:
                    p = satir.split()
                    if len(p) >= 6 and p[3] != '00:00:00:00:00:00':
                        girdiler.append({"ip": p[0], "mac": p[3].upper(), "arayuz": p[5]})
        except (FileNotFoundError, PermissionError):
            pass
    else:
        try:
            cikti = os.popen('arp -a').read()
            for satir in cikti.splitlines():
                m = re.search(r'\(?(\d+\.\d+\.\d+\.\d+)\)?\s+(?:at\s+)?([0-9a-fA-F:-]{17})', satir)
                if m:
                    girdiler.append({"ip": m.group(1), "mac": m.group(2).upper(), "arayuz": "?"})
        except Exception:
            pass
    return girdiler

def baglantilari_al():
    if not PSUTIL_VAR:
        return []
    try:
        return psutil.net_connections()
    except (PermissionError, psutil.AccessDenied):
        return None
    except Exception:
        return []

def proses_adi(pid):
    if not pid or pid <= 0:
        return "bilinmiyor"
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "erişilemedi"

# ==========================================
# CİHAZ TESPİT MODÜLÜ (YENİ)
# ==========================================

def yerel_ag_bilgisi():
    """Aktif IP + subnet mask'tan CIDR aralığı üretir."""
    aktif_ip = aktif_baglanti_cozumle()
    if not aktif_ip:
        return None, None
    cidr = None
    if PSUTIL_VAR:
        try:
            for ad, adresler in psutil.net_if_addrs().items():
                for addr in adresler:
                    if addr.family == socket.AF_INET and addr.address == aktif_ip:
                        cidr = mask_to_cidr(addr.netmask) if addr.netmask else 24
                        break
                if cidr:
                    break
        except Exception:
            pass
    return aktif_ip, cidr or 24

def mask_to_cidr(mask):
    try:
        return bin(int(socket.inet_aton(mask).hex(), 16)).count('1')
    except Exception:
        return 24

def subnet_ip_listesi(ip, cidr):
    """CIDR'a göre tarama listesi üretir (max /24 için 254 host)."""
    try:
        cidr = max(24, min(cidr, 30))  # çok geniş ağları /24 ile sınırla (hız)
        ag = struct.unpack('>I', socket.inet_aton(ip))[0] >> (32 - cidr)
        hostlar = []
        for i in range(1, (1 << (32 - cidr)) - 1):
            host_ip = ((ag << (32 - cidr)) + i)
            hostlar.append(socket.inet_ntoa(struct.pack('>I', host_ip)))
        return hostlar
    except Exception:
        return []

def ip_to_int(ip):
    return struct.unpack('>I', socket.inet_aton(ip))[0]

def cidr_prefix_of(ip, cidr):
    return ip_to_int(ip) >> (32 - cidr)

def ping_host(ip, sonuc_listesi, kilit):
    """Tek host'a ping atar, başarılıysa listeye ekler. Ping yoksa port 80/443/22 dener."""
    param = '-n' if os.name == 'nt' else '-c'
    zaman = '-w' if os.name == 'nt' else '-W'
    timeout = '1000' if os.name == 'nt' else '1'
    try:
        r = subprocess.run(['ping', param, '1', zaman, timeout, ip],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        if r.returncode == 0:
            with kilit:
                sonuc_listesi.append(ip)
            return
    except Exception:
        pass
    # Ping engellenmiş olabilir: yaygın portlara hızlı TCP bağlantısı dene
    for port in (80, 443, 22):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                with kilit:
                    sonuc_listesi.append(ip)
                s.close()
                return
            s.close()
        except Exception:
            continue

def scapy_arp_tara(ip, cidr):
    """scapy varsa ARP taraması (en hızlı ve en doğru yöntem)."""
    try:
        ag = ip_to_int(ip) & ((0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF)
        hosts = [socket.inet_ntoa(struct.pack('>I', ag + i))
                 for i in range(1, (1 << (32 - cidr)) - 1)]
        arp = ARP(pdst=hosts)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        paket = ether / arp
        yanit, _ = srp(paket, timeout=2, verbose=0)
        cihazlar = []
        for gonderilen, alinan in yanit:
            cihazlar.append({"ip": alinan.psrc, "mac": alinan.hwsrc.upper()})
        return cihazlar
    except Exception:
        return None  # hata → fallback tetiklenir

def cihazlari_tespit_et():
    print(f"\n{MAVI}[*] Yerel ağ bilgileri alınıyor...")
    aktif_ip, cidr = yerel_ag_bilgisi()
    if not aktif_ip:
        print(f"{KIRMIZI}[!] Aktif ağ bağlantısı yok - tarama yapılamaz.")
        return

    print(f"{YESIL}[+] Yerel IP: {BEYAZ}{aktif_ip}  {SARI}/ {cidr}")
    gw, _ = varsayilan_gateway()
    print(f"{YESIL}[+] Gateway: {BEYAZ}{gw or 'Bilinmiyor'}")

    hostlar = subnet_ip_listesi(aktif_ip, cidr)
    print(f"{MAVI}[*] {len(hostlar)} IP taraması başlıyor ({'scapy ARP' if SCAPY_VAR else 'ping + port sweep'})...\n")

    # --- Yöntem 1: scapy ARP (varsa) ---
    cihazlar = None
    if SCAPY_VAR:
        cihazlar = scapy_arp_tara(aktif_ip, cidr)
        if cihazlar is not None:
            print(f"{SARI}    (ARP taraması kullanıldı)")

    # --- Yöntem 2: ping sweep fallback ---
    if cihazlar is None:
        sonuc = []
        kilit = threading.Lock()
        threadler = []
        # Tüm hostlara paralel ping (thread havuzu mantığıyla gruplanmış)
        batch = 60
        for i in range(0, len(hostlar), batch):
            grup = hostlar[i:i + batch]
            for ip in grup:
                t = threading.Thread(target=ping_host, args=(ip, sonuc, kilit), daemon=True)
                threadler.append(t)
                t.start()
            for t in grup_threadleri(threadler[i:i + batch]):
                t.join()
        cihazlar = [{"ip": x, "mac": "?"} for x in sonuc]
        print(f"{SARI}    (ping/port-sweep taraması kullanıldı)")

    if not cihazlar:
        print(f"{KIRMIZI}[-] Ağda yanıt veren cihaz bulunamadı.")
        return

    # MAC'leri ARP tablosundan zenginleştir (ping yönteminde MAC boş kalır)
    arp_map = {g['ip']: g['mac'] for g in arp_tablosu()}
    for c in cihazlar:
        if c["mac"] == "?" and c["ip"] in arp_map:
            c["mac"] = arp_map[c["ip"]]

    # Hostname çözmeye çalış (bazı cihazlarda çalışır)
    print(f"\n{SARI}--- BULUNAN CİHAZLAR ({len(cihazlar)} adet) ---")
    kendi_ip = aktif_ip
    for c in sorted(cihazlar, key=lambda x: ip_to_int(x['ip'])):
        hostname = "-"
        if SCAPY_VAR is False:
            try:
                hostname = socket.gethostbyaddr(c['ip'])[0]
            except Exception:
                pass
        etiket = ""
        if c['ip'] == kendi_ip:
            etiket = f"  {MOR}← BU CİHAZ"
        elif c['ip'] == gw:
            etiket = f"  {SARI}← GATEWAY (Modem/Router)"
        print(f"{YESIL}[+] {BEYAZ}{c['ip']:<16} {MAVI}MAC: {c['mac']:<20} {BEYAZ}{hostname}{etiket}")
    print(f"\n{BEYAZ}Not: Ping'i kapalı (stealth) cihazlar ARP/ping yöntemine göre görünmeyebilir.")
    print(f"{BEYAZ}En doğru sonuç için: pip install scapy")

def grup_threadleri(threadler):
    return threadler

def menu_cihaz_tespiti():
    try:
        cihazlari_tespit_et()
    except Exception as e:
        print(f"{KIRMIZI}[!] Tarama hatası: {e}")
    input(f"\n{MOR}[ENTER] Menüye dönmek için basın...")

# ==========================================
# DİĞER MENÜLER
# ==========================================

def menu_2():
    print(f"\n{MAVI}[*] Sistem ve Arayüz Analizi...\n")
    try:
        print(f"{YESIL}[+] Cihaz Adı: {BEYAZ}{socket.gethostname()}")
    except Exception:
        print(f"{KIRMIZI}[!] Hostname alınamadı")
    print(f"{YESIL}[+] Platform: {BEYAZ}{sys.platform} ({os.name})")
    print(f"\n{SARI}--- FİZİKSEL DONANIM (MAC) ADRESLERİ ---")
    for arayuz, mac in mac_adreslerini_topla().items():
        print(f"{YESIL}[+] {arayuz}: {BEYAZ}{mac}")
    gw, arayuz = varsayilan_gateway()
    print(f"\n{SARI}--- YÖNLENDİRME ---")
    print(f"{YESIL}[+] Varsayılan Gateway: {BEYAZ}{gw or 'Bulunamadı'}  (arayüz: {arayuz or '-'})")
    print(f"{YESIL}[+] DNS Sunucuları: {BEYAZ}{', '.join(dns_sunuculari())}")
    input(f"\n{MOR}[ENTER] Menüye dönmek için basın...")

def menu_3():
    print(f"\n{MAVI}[*] Canlı IP Kayıtları Okunuyor...\n")
    aktif_ip = aktif_baglanti_cozumle()
    print(f"{SARI}--- AKTİF BAĞLANTI ---")
    if aktif_ip:
        print(f"{YESIL}[√] Yerel Çıkış IPv4: {BEYAZ}{aktif_ip}")
    else:
        print(f"{KIRMIZI}[!] Aktif internet bağlantısı yok")
    pub = public_ip_ve_konum()
    print(f"\n{SARI}--- HALKA AÇIK IP BİLGİSİ (CANLI SORGU) ---")
    if "hata" in pub:
        print(f"{KIRMIZI}[!] {pub['hata']}")
    else:
        print(f"{YESIL}[√] Public IP: {BEYAZ}{pub.get('query', '-')}")
        print(f"{YESIL}[√] Konum: {BEYAZ}{pub.get('city', '-')}, {pub.get('country', '-')}")
        print(f"{YESIL}[√] Koordinat: {BEYAZ}{pub.get('lat', '-')}, {pub.get('lon', '-')}")
        print(f"{YESIL}[√] ISP: {BEYAZ}{pub.get('isp', '-')}")
        print(f"{YESIL}[√] Organizasyon/AS: {BEYAZ}{pub.get('org', '-')} / {pub.get('as', '-')}")
    print(f"\n{SARI}--- TÜM AĞ ARAYÜZLERİ ---")
    kartlar = tum_arayuzleri_tara()
    if not kartlar:
        print(f"{KIRMIZI}[!] Arayüzler okunamadı (psutil gerekli)")
    for kart in kartlar:
        print(f"{MAVI}[{kart['kart']}]  {SARI}[{kart['durum']} @ {kart['hiz']}]")
        print(f"   ∟ IPv4: {BEYAZ}{kart['ipv4']}  {SARI}mask: {kart['mask']}")
        print(f"   ∟ IPv6: {BEYAZ}{kart['ipv6']}")
    input(f"\n{MOR}[ENTER] Menüye dönmek için basın...")

def menu_4():
    print(f"\n{MAVI}[*] Gerçek Zamanlı Güvenlik Denetimi...\n")
    baglantilar = baglantilari_al()
    if baglantilar is None:
        print(f"{KIRMIZI}[!] Soket bilgisi için root izni gerekiyor.")
    else:
        dinleyenler = [c for c in baglantilar if c.status == 'LISTEN']
        kurulu = [c for c in baglantilar if c.status == 'ESTABLISHED']
        print(f"{SARI}--- DİNLENEN PORTLAR ---")
        if dinleyenler:
            for c in sorted(dinleyenler, key=lambda x: (x.laddr.ip if x.laddr else '', x.laddr.port if x.laddr else 0)):
                if not c.laddr:
                    continue
                print(f"{YESIL}[+] {BEYAZ}{c.laddr.ip}:{c.laddr.port:<6} "
                      f"{MAVI}PID: {c.pid or '-':<7} {BEYAZ}{proses_adi(c.pid)}")
        else:
            print(f"{KIRMIZI}[-] Dinlenen port yok")
        print(f"\n{SARI}--- AKTİF (ESTABLISHED) BAĞLANTILAR ---")
        if kurulu:
            for c in kurulu:
                if not c.laddr or not c.raddr:
                    continue
                print(f"{YESIL}[+] {BEYAZ}{c.laddr.ip}:{c.laddr.port}  →  "
                      f"{MAVI}{c.raddr.ip}:{c.raddr.port}  {BEYAZ}({proses_adi(c.pid)})")
        else:
            print(f"{KIRMIZI}[-] Kurulu bağlantı yok")
        print(f"\n{SARI}--- GÜVENLİK DEĞERLENDİRMESİ ---")
        harici = [c for c in dinleyenler if c.laddr and c.laddr.ip in ('0.0.0.0', '::')]
        if harici:
            print(f"{KIRMIZI}[!] UYARI: {len(harici)} soket 0.0.0.0 üzerinde - harici erişime açık!")
        else:
            print(f"{YESIL}[+] Dinleyen soketler hariciye açık değil")
    print(f"\n{SARI}--- ARP ÖNBELLEĞİ ---")
    arp = arp_tablosu()
    if arp:
        for g in arp:
            print(f"{YESIL}[+] {BEYAZ}{g['ip']:<16} {MAVI}{g['mac']:<20} {BEYAZ}{g['arayuz']}")
    else:
        print(f"{KIRMIZI}[-] ARP girdisi bulunamadı")
    input(f"\n{MOR}[ENTER] Menüye dönmek için basın...")

# ==========================================
# ANA PROGRAM
# ==========================================

def ana_program():
    while True:
        temizle()
        print(LOGO)
        print("-" * 61)
        print(f"{YESIL}  [1] Yakındaki Cihazları Tespit Et (Ağ Taraması)")
        print(f"{YESIL}  [2] Sistem + MAC + Gateway + DNS Analizi")
        print(f"{YESIL}  [3] Yerel ve Public IP + Konum + ISP (Canlı)")
        print(f"{YESIL}  [4] Güvenlik Denetimi: Portlar + Bağlantılar + ARP")
        print(f"{KIRMIZI}  [0] Çıkış")
        print("-" * 61)
        secenek = input(f"{BEYAZ}N-Spearstion > Seçiminiz: ").strip()
        try:
            if secenek == "1": menu_cihaz_tespiti()
            elif secenek == "2": menu_2()
            elif secenek == "3": menu_3()
            elif secenek == "4": menu_4()
            elif secenek == "0":
                print(f"\n{YESIL}N-Spearstion kapatılıyor.")
                sys.exit(0)
            else:
                print(f"\n{KIRMIZI}[-] Geçersiz seçenek!")
                time.sleep(1.5)
        except (KeyboardInterrupt, EOFError):
            print(f"\n{SARI}[*] Menüye dönülüyor...")
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        ana_program()
    except KeyboardInterrupt:
        print(f"\n{KIRMIZI}[!] Oturum sonlandırıldı.")
        sys.exit(0)
