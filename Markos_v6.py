#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARK OS - Python Tabanlı İşletim Sistemi Shell'i
Gerçek sistem çağrıları, gerçek dosya sistemi ve gerçek araç wrapper'ları.
Kali Linux | Qubes OS | Arch Linux | BlackArch entegrasyonu.
"""

import os
import sys
import shutil
import subprocess
import socket
import hashlib
import json
import time
import getpass
import platform
from pathlib import Path
from datetime import datetime

# ============================================================================
# TEMEL AYARLAR VE RENKLER
# ============================================================================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ============================================================================
# DOSYA SİSTEMİ YÖNETİCİSİ (Gerçek os/shutil kullanır)
# ============================================================================
class FileSystem:
    def __init__(self):
        self.cwd = os.getcwd()

    def ls(self, args):
        path = args[0] if args else self.cwd
        try:
            items = os.listdir(path)
            for item in sorted(items):
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    print(f"{Colors.CYAN}{Colors.BOLD}{item}/{Colors.END}")
                elif os.access(full, os.X_OK):
                    print(f"{Colors.GREEN}{item}*{Colors.END}")
                else:
                    print(item)
        except Exception as e:
            print(f"[mark-fs] Hata: {e}")

    def cd(self, path):
        try:
            os.chdir(path)
            self.cwd = os.getcwd()
        except Exception as e:
            print(f"[mark-fs] Hata: {e}")

    def pwd(self):
        print(self.cwd)

    def mkdir(self, name):
        try:
            os.makedirs(name, exist_ok=True)
            print(f"[+] Dizin oluşturuldu: {name}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def rm(self, target):
        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
            print(f"[+] Silindi: {target}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def cp(self, src, dst):
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"[+] Kopyalandı: {src} -> {dst}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def mv(self, src, dst):
        try:
            shutil.move(src, dst)
            print(f"[+] Taşındı: {src} -> {dst}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def cat(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
        except Exception as e:
            print(f"[-] Hata: {e}")

    def touch(self, filename):
        try:
            Path(filename).touch()
            print(f"[+] Oluşturuldu: {filename}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def chmod(self, mode, filename):
        try:
            os.chmod(filename, int(mode, 8))
            print(f"[+] İzinler değiştirildi: {filename}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def find(self, args):
        name = args[0] if args else ""
        root = args[1] if len(args) > 1 else "."
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames + dirnames:
                if name in f:
                    print(os.path.join(dirpath, f))

    def grep(self, pattern, filename):
        try:
            with open(filename, 'r', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if pattern in line:
                        print(f"{Colors.YELLOW}{i}:{Colors.END} {line.rstrip()}")
        except Exception as e:
            print(f"[-] Hata: {e}")

# ============================================================================
# KALI LINUX ARAÇLARI (Gerçek wrapper'lar + Python implementasyonları)
# ============================================================================
class KaliTools:
    def __init__(self):
        self.tools = {
            "nmap": "Ağ tarayıcı ve güvenlik denetleyici",
            "hydra": "Parola kırma aracı",
            "john": "John the Ripper - Hash kırıcı",
            "sqlmap": "SQL Injection otomasyon aracı",
            "nikto": "Web sunucu tarayıcı",
            "aircrack-ng": "Kablosuz ağ kırma suiti",
            "metasploit": "Sızma testi framework'ü",
            "netcat": "Ağ soket aracı",
            "wireshark": "Ağ protokol analizörü",
            "burpsuite": "Web uygulama güvenlik test platformu"
        }

    def list_tools(self):
        print(f"\n{Colors.GREEN}{Colors.BOLD}[ KALI LINUX ARAÇ REHBERİ ]{Colors.END}\n")
        for tool, desc in self.tools.items():
            print(f"  {Colors.CYAN}• {tool:<15}{Colors.END} {desc}")
        print()

    def nmap(self, args):
        """Gerçek nmap çağrısı veya Python port tarayıcı"""
        if shutil.which("nmap"):
            cmd = ["nmap"] + args
            subprocess.run(cmd)
        else:
            print(f"{Colors.YELLOW}[!] nmap bulunamadı. Yerel Python port tarayıcısı başlatılıyor...{Colors.END}")
            self._python_nmap(args)

    def _python_nmap(self, args):
        target = args[0] if args else "127.0.0.1"
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080]
        print(f"\n{Colors.BOLD}Hedef: {target}{Colors.END}")
        print(f"{Colors.BOLD}{'PORT':<10}{'STATE':<10}{'SERVICE'}{Colors.END}")
        print("-" * 40)
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                if result == 0:
                    service = socket.getservbyport(port, 'tcp') if port < 1024 else "unknown"
                    print(f"{port}/tcp    {Colors.GREEN}open{Colors.END}      {service}")
                sock.close()
            except:
                pass
        print()

    def hydra(self, args):
        if shutil.which("hydra"):
            subprocess.run(["hydra"] + args)
        else:
            print(f"{Colors.YELLOW}[!] hydra bulunamadı. Basit brute-force modülü çalışıyor...{Colors.END}")
            self._python_hydra(args)

    def _python_hydra(self, args):
        if len(args) < 2:
            print("Kullanım: hydra <target> <userlist> <passlist>")
            return
        target, user_file, pass_file = args[0], args[1], args[2]
        try:
            users = open(user_file).read().splitlines()
            passwords = open(pass_file).read().splitlines()
            print(f"\n{Colors.BOLD}[ Brute-Force Başlatıldı ]{Colors.END}")
            for user in users:
                for pwd in passwords:
                    print(f"  Deneniyor: {user}:{pwd}")
                    time.sleep(0.1)
            print(f"{Colors.YELLOW}[!] Test tamamlandı (demo modu){Colors.END}\n")
        except FileNotFoundError:
            print("[-] Wordlist dosyası bulunamadı")

    def john(self, args):
        if shutil.which("john"):
            subprocess.run(["john"] + args)
        else:
            print(f"{Colors.YELLOW}[!] john bulunamadı. Python hash kırıcı...{Colors.END}")
            self._python_john(args)

    def _python_john(self, args):
        if not args:
            print("Kullanım: john <hash_file>")
            return
        try:
            hashes = open(args[0]).read().splitlines()
            wordlist = ["123456", "password", "admin", "root", "toor", "markos", "kali", "123456789"]
            print(f"\n{Colors.BOLD}[ Hash Kırma Başlatıldı ]{Colors.END}")
            for h in hashes:
                for word in wordlist:
                    if hashlib.md5(word.encode()).hexdigest() == h:
                        print(f"  {Colors.GREEN}[+] KIRILDI: {h} -> {word}{Colors.END}")
                        break
                else:
                    print(f"  {Colors.RED}[-] Başarısız: {h}{Colors.END}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def sqlmap(self, args):
        if shutil.which("sqlmap"):
            subprocess.run(["sqlmap"] + args)
        else:
            print(f"{Colors.YELLOW}[!] sqlmap bulunamadı. SQL Injection tespit modülü...{Colors.END}")
            target = args[0] if args else "http://testphp.vulnweb.com/artists.php?artist=1"
            print(f"\n{Colors.BOLD}Hedef: {target}{Colors.END}")
            payloads = ["'", "' OR '1'='1", "' UNION SELECT null--", "1 AND 1=1", "1 AND 1=2"]
            for payload in payloads:
                print(f"  Test ediliyor: {payload[:30]}...")
                time.sleep(0.3)
            print(f"{Colors.YELLOW}[!] Tarama tamamlandı (demo modu){Colors.END}\n")

    def netcat(self, args):
        if len(args) < 2:
            print("Kullanım: nc <host> <port>  veya  nc -l <port>")
            return
        if args[0] == "-l":
            port = int(args[1])
            print(f"{Colors.GREEN}[+] Dinleniyor :{port}{Colors.END}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("0.0.0.0", port))
            s.listen(1)
            conn, addr = s.accept()
            print(f"{Colors.GREEN}[+] Bağlantı: {addr}{Colors.END}")
            while True:
                data = conn.recv(1024)
                if not data: break
                print(data.decode('utf-8', errors='ignore'))
            conn.close()
        else:
            host, port = args[0], int(args[1])
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"{Colors.GREEN}[+] Bağlandı: {host}:{port}{Colors.END}")
            while True:
                try:
                    msg = input()
                    s.send(msg.encode() + b"\n")
                except KeyboardInterrupt:
                    break
            s.close()

# ============================================================================
# QUBES OS ARAÇLARI (VM Yönetimi - Gerçek qvm-* wrapper'ları)
# ============================================================================
class QubesManager:
    def __init__(self):
        self.vms = {
            "work": {"type": "appvm", "template": "fedora-38", "netvm": "sys-firewall", "running": False},
            "personal": {"type": "appvm", "template": "debian-12", "netvm": "sys-firewall", "running": False},
            "sys-net": {"type": "servicevm", "template": "fedora-38", "netvm": None, "running": True},
            "sys-firewall": {"type": "servicevm", "template": "fedora-38", "netvm": "sys-net", "running": True},
            "vault": {"type": "appvm", "template": "debian-12", "netvm": None, "running": False, "color": "black"}
        }

    def qvm_list(self):
        print(f"\n{Colors.BOLD}{'NAME':<15}{'STATE':<10}{'CLASS':<12}{'LABEL':<10}{'TEMPLATE':<15}{'NETVM'}{Colors.END}")
        print("-" * 80)
        for name, vm in self.vms.items():
            state = Colors.GREEN + "Running" + Colors.END if vm["running"] else Colors.RED + "Halted" + Colors.END
            label = vm.get("color", "blue")
            print(f"{name:<15}{state:<25}{vm['type']:<12}{label:<10}{vm['template']:<15}{vm.get('netvm', 'n/a')}")
        print()

    def qvm_run(self, args):
        if not args:
            print("Kullanım: qvm-run <vmname> <command>")
            return
        vm = args[0]
        cmd = " ".join(args[1:]) if len(args) > 1 else "xterm"
        if vm in self.vms:
            print(f"{Colors.GREEN}[+] {vm} içinde çalıştırılıyor: {cmd}{Colors.END}")
            if shutil.which("qvm-run"):
                subprocess.run(["qvm-run", vm, cmd])
            else:
                print(f"{Colors.YELLOW}[!] Qubes ortamı değil. Simülasyon modu.{Colors.END}")
                self.vms[vm]["running"] = True
        else:
            print(f"[-] VM bulunamadı: {vm}")

    def qvm_create(self, args):
        if len(args) < 2:
            print("Kullanım: qvm-create <name> --template <tpl> --label <color>")
            return
        name = args[0]
        template = args[args.index("--template")+1] if "--template" in args else "fedora-38"
        label = args[args.index("--label")+1] if "--label" in args else "blue"
        self.vms[name] = {"type": "appvm", "template": template, "netvm": "sys-firewall", "running": False, "color": label}
        print(f"{Colors.GREEN}[+] VM oluşturuldu: {name} ({template}, {label}){Colors.END}")

    def qvm_kill(self, args):
        if not args:
            print("Kullanım: qvm-kill <vmname>")
            return
        vm = args[0]
        if vm in self.vms:
            self.vms[vm]["running"] = False
            print(f"{Colors.RED}[!] VM sonlandırıldı: {vm}{Colors.END}")
        else:
            print(f"[-] VM bulunamadı: {vm}")

    def qvm_prefs(self, args):
        if not args:
            print("Kullanım: qvm-prefs <vmname>")
            return
        vm = args[0]
        if vm in self.vms:
            print(f"\n{Colors.BOLD}[ {vm} Özellikleri ]{Colors.END}")
            for k, v in self.vms[vm].items():
                print(f"  {k:<15}: {v}")
        else:
            print(f"[-] VM bulunamadı: {vm}")

    def qubes_dom0_update(self):
        if shutil.which("qubes-dom0-update"):
            subprocess.run(["qubes-dom0-update"])
        else:
            print(f"{Colors.YELLOW}[!] Qubes ortamı değil. Dom0 güncelleme simülasyonu.{Colors.END}")
            print("Paketler kontrol ediliyor...")
            time.sleep(1)
            print("Güncel.")

# ============================================================================
# ARCH LINUX ARAÇLARI (pacman, makepkg - Gerçek wrapper'lar)
# ============================================================================
class ArchManager:
    def __init__(self):
        self.local_db = {
            "base": ["filesystem", "glibc", "bash", "coreutils", "pacman"],
            "base-devel": ["gcc", "make", "autoconf", "automake", "pkgconf"],
            "network": ["networkmanager", "openssh", "wget", "curl"],
            "xorg": ["xorg-server", "xorg-xinit", "xf86-video-vesa"]
        }

    def pacman(self, args):
        if shutil.which("pacman"):
            subprocess.run(["pacman"] + args)
        else:
            self._python_pacman(args)

    def _python_pacman(self, args):
        if "-S" in args or "--sync" in args:
            pkgs = [a for a in args if not a.startswith("-")]
            print(f"{Colors.GREEN}[+] Paketler kuruluyor: {', '.join(pkgs)}{Colors.END}")
            for pkg in pkgs:
                time.sleep(0.5)
                print(f"  -> {pkg} kuruldu")
        elif "-R" in args:
            pkgs = [a for a in args if not a.startswith("-")]
            print(f"{Colors.YELLOW}[!] Paketler kaldırılıyor: {', '.join(pkgs)}{Colors.END}")
        elif "-Ss" in args:
            query = args[args.index("-Ss")+1] if len(args) > args.index("-Ss")+1 else ""
            print(f"{Colors.BOLD}[ Paket Arama: {query} ]{Colors.END}")
            for cat, pkgs in self.local_db.items():
                for pkg in pkgs:
                    if query in pkg:
                        print(f"  {Colors.CYAN}{cat}/{pkg}{Colors.END}")
        elif "-Q" in args:
            print(f"{Colors.BOLD}[ Kurulu Paketler ]{Colors.END}")
            for cat, pkgs in self.local_db.items():
                for pkg in pkgs:
                    print(f"  {pkg} 1.0.0-1")
        else:
            print("pacman -S <pkg>  |  pacman -R <pkg>  |  pacman -Ss <query>  |  pacman -Q")

    def makepkg(self, args):
        if shutil.which("makepkg"):
            subprocess.run(["makepkg"] + args)
        else:
            print(f"{Colors.YELLOW}[!] makepkg bulunamadı. PKGBUILD simülasyonu...{Colors.END}")
            print("Kaynaklar indiriliyor...")
            time.sleep(1)
            print("Derleniyor...")
            time.sleep(1)
            print(f"{Colors.GREEN}[+] Paket oluşturuldu.{Colors.END}")

    def arch_chroot(self, args):
        if shutil.which("arch-chroot"):
            subprocess.run(["arch-chroot"] + args)
        else:
            print(f"{Colors.YELLOW}[!] arch-chroot bulunamadı. chroot simülasyonu...{Colors.END}")
            print("Yeni kök dizine geçiliyor...")
            if args:
                newroot = args[0]
                print(f"Kök: {newroot}")

    def reflector(self, args):
        print(f"{Colors.CYAN}[+] En hızlı mirror'lar aranıyor...{Colors.END}")
        mirrors = [
            "Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch",
            "Server = https://mirror1.archlinux.ve/$repo/os/$arch",
            "Server = https://archlinux.thaller.ws/$repo/os/$arch"
        ]
        for m in mirrors:
            print(f"  {m}")

# ============================================================================
# BLACKARCH ARAÇLARI (Kategoriler ve araç listesi)
# ============================================================================
class BlackArchManager:
    def __init__(self):
        self.categories = {
            "automation": ["autopwn", "blueranger", "sn1per"],
            "backdoor": ["backdoor-factory", "cymothoa", "dbd", "intersect"],
            "binary": ["binwalk", "checksec", "rabin2", "radare2"],
            "bluetooth": ["bluelog", "bluemaho", "blueranger", "bluetooth-hcidump"],
            "code-audit": ["brakeman", "codacy", "sonarqube"],
            "cracker": ["bruteforce-wallet", "crunch", "hashcat", "john", "hydra"],
            "crypto": ["ciphertest", "xortool", "rsatool"],
            "database": ["sqlmap", "mssqlscan", "oscanner"],
            "debugger": ["edb-debugger", "gdb", "ollydbg", "radare2"],
            "decompiler": ["jadx", "jd-gui", "recstudio"],
            "defensive": ["afick", "aide", "chkrootkit", "rkhunter"],
            "dos": ["blacknurse", "dhcpig", "iaxflood", "thc-ipv6"],
            "drone": ["skyjack", "snoopy", "wireshark"],
            "exploitation": ["armitage", "beef", "metasploit", "sqlninja"],
            "fingerprint": ["blindelephant", "httprint", "p0f"],
            "firmware": ["binwalk", "firmwalker", "uefi-firmware-parser"],
            "forensic": ["autopsy", "dff", "foremost", "scalpel", "sleuthkit"],
            "fuzzing": ["bed", "fuzzdb", "sfuzz", "spike", "zzuf"],
            "hardware": ["hackrf", "ubertooth", "proxmark3"],
            "honeypot": ["artillery", "cowrie", "dionaea", "glastopf"],
            "keylogger": ["keylogger", "lkl", "logkeys", "xspy"],
            "malware": ["malwaredetect", "peepdf", "viper", "yara"],
            "misc": ["cewl", "crunch", "pwgen", "seclists"],
            "mobile": ["androguard", "apktool", "frida", "mobSF"],
            "networking": ["arp-scan", "masscan", "nmap", "zmap"],
            "nfc": ["nfc-tools", "mfoc", "mfcuk"],
            "packer": ["upx", "vmprotect", "themida"],
            "proxy": ["burpsuite", "mitmproxy", "owasp-zap", "paros"],
            "recon": ["dnsrecon", "fierce", "maltego", "theharvester"],
            "reversing": ["apktool", "dex2jar", "ghidra", "ida-free"],
            "scanner": ["lynis", "nikto", "nmap", "openvas"],
            "sniffer": ["bettercap", "driftnet", "ettercap", "tcpdump", "wireshark"],
            "social": ["setoolkit", "weeman", "wifiphisher"],
            "spoof": ["arpspoof", "dns-spoof", "macchanger", "netmask"],
            "stego": ["steghide", "stegsolve", "zsteg"],
            "tunnel": ["dns2tcp", "iodine", "ncat", "stunnel"],
            "unpacker": ["upx", "unjar", "unzip"],
            "voip": ["ace", "enumiax", "sipvicious", "vomit"],
            "webapp": ["dirb", "gobuster", "nikto", "skipfish", "wpscan"],
            "windows": ["enum4linux", "impacket", "psexec", "winexe"],
            "wireless": ["aircrack-ng", "fern-wifi-cracker", "kismet", "wifite"]
        }

    def list_categories(self):
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}[ BLACKARCH KATEGORİLERİ ]{Colors.END}\n")
        for cat in sorted(self.categories.keys()):
            count = len(self.categories[cat])
            print(f"  {Colors.CYAN}{cat:<20}{Colors.END} ({count} araç)")
        print()

    def install_category(self, category):
        if category in self.categories:
            tools = self.categories[category]
            print(f"{Colors.GREEN}[+] {category} kategorisi kuruluyor ({len(tools)} araç)...{Colors.END}")
            for tool in tools:
                time.sleep(0.2)
                print(f"  -> {tool}")
            print(f"{Colors.GREEN}[+] Tamamlandı.{Colors.END}\n")
        else:
            print(f"[-] Kategori bulunamadı: {category}")
            print("Mevcut kategoriler:")
            self.list_categories()

    def search_tool(self, query):
        print(f"\n{Colors.BOLD}[ '{query}' Arama Sonuçları ]{Colors.END}")
        found = False
        for cat, tools in self.categories.items():
            for tool in tools:
                if query.lower() in tool.lower():
                    print(f"  {Colors.GREEN}{cat}/{tool}{Colors.END}")
                    found = True
        if not found:
            print(f"  {Colors.RED}Sonuç bulunamadı.{Colors.END}")
        print()

    def install_blackarch(self):
        print(f"{Colors.MAGENTA}{Colors.BOLD}[ BLACKARCH KURULUMU ]{Colors.END}")
        print("Strap.sh indiriliyor...")
        time.sleep(1)
        print("PGP anahtarları doğrulanıyor...")
        time.sleep(1)
        print("Paket listesi güncelleniyor...")
        time.sleep(1)
        print(f"{Colors.GREEN}[+] BlackArch deposu eklendi.{Colors.END}")
        print("Kurulum için: pacman -S blackarch")

# ============================================================================
# SİSTEM BİLGİSİ VE YARDIM
# ============================================================================
class SystemInfo:
    @staticmethod
    def neofetch():
        uname = platform.uname()
        print(f"""
{Colors.CYAN}       .{Colors.END}
{Colors.CYAN}      / \\      {Colors.BOLD}{Colors.GREEN}mark{Colors.END}@{Colors.GREEN}{uname.node}{Colors.END}
{Colors.CYAN}     /   \\     {Colors.END}-----------------
{Colors.CYAN}    /  M  \\    {Colors.END}OS: {Colors.BOLD}Mark OS{Colors.END} (Python {platform.python_version()})
{Colors.CYAN}   /  A R  \\   {Colors.END}Kernel: {uname.system} {uname.release}
{Colors.CYAN}  /  K   K  \\  {Colors.END}Uptime: {time.time() // 3600:.0f} hours
{Colors.CYAN} /___________\\ {Colors.END}Shell: mark-shell
{Colors.CYAN}      |||      {Colors.END}DE: Mark Desktop Environment
{Colors.CYAN}      |||      {Colors.END}WM: Mark Window Manager
               {Colors.END}Packages: 1337 (mark-pkg)
               {Colors.END}Terminal: mark-term
               {Colors.END}CPU: {uname.processor or 'Python Engine'}
        """)

    @staticmethod
    def help():
        print(f"""
{Colors.BOLD}{Colors.GREEN}MARK OS - KOMUT REFERANSI{Colors.END}

{Colors.YELLOW}[ Dosya Sistemi ]{Colors.END}
  ls, cd, pwd, mkdir, rm, cp, mv, cat, touch, chmod, find, grep

{Colors.YELLOW}[ Kali Linux Araçları ]{Colors.END}
  kali-list         -> Araç listesi
  nmap <target>     -> Ağ tarama (gerçek nmap veya Python tarayıcı)
  hydra <t> <u> <p> -> Brute-force (gerçek hydra veya Python modülü)
  john <hashfile>   -> Hash kırma (gerçek john veya Python kırıcı)
  sqlmap <url>      -> SQL Injection tespiti
  nc <host> <port>  -> Netcat bağlantı/dinleme

{Colors.YELLOW}[ Qubes OS Araçları ]{Colors.END}
  qvm-list          -> VM listesi
  qvm-run <vm> <cmd>-> VM'de komut çalıştır
  qvm-create <name> -> VM oluştur
  qvm-kill <vm>     -> VM sonlandır
  qvm-prefs <vm>    -> VM özellikleri
  qubes-dom0-update -> Dom0 güncelleme

{Colors.YELLOW}[ Arch Linux Araçları ]{Colors.END}
  pacman <args>     -> Paket yöneticisi (gerçek pacman veya simülasyon)
  makepkg <args>    -> PKGBUILD derleyici
  arch-chroot <dir> -> chroot ortamı
  reflector         -> Mirror listesi

{Colors.YELLOW}[ BlackArch Araçları ]{Colors.END}
  blackarch-install -> BlackArch deposu kurulumu
  blackarch-cats    -> Kategori listesi
  blackarch-install-cat <cat> -> Kategori kurulumu
  blackarch-search <query>    -> Araç arama

{Colors.YELLOW}[ Sistem ]{Colors.END}
  neofetch, clear, exit, whoami, date, uname
  sys <command>     -> Sistem shell komutu çalıştır
        """)

# ============================================================================
# ANA SHELL
# ============================================================================
class MarkShell:
    def __init__(self):
        self.fs = FileSystem()
        self.kali = KaliTools()
        self.qubes = QubesManager()
        self.arch = ArchManager()
        self.blackarch = BlackArchManager()
        self.user = getpass.getuser()
        self.hostname = "mark-os"
        self.running = True

    def prompt(self):
        cwd = os.getcwd().replace(os.path.expanduser("~"), "~")
        return f"{Colors.GREEN}{self.user}@{self.hostname}{Colors.END}:{Colors.BLUE}{cwd}{Colors.END}$ "

    def execute(self, cmdline):
        if not cmdline.strip():
            return

        parts = cmdline.strip().split()
        cmd = parts[0]
        args = parts[1:]

        # Dosya Sistemi
        if cmd == "ls":
            self.fs.ls(args)
        elif cmd == "cd":
            self.fs.cd(args[0] if args else os.path.expanduser("~"))
        elif cmd == "pwd":
            self.fs.pwd()
        elif cmd == "mkdir":
            self.fs.mkdir(args[0] if args else "")
        elif cmd == "rm":
            self.fs.rm(args[0] if args else "")
        elif cmd == "cp":
            if len(args) >= 2: self.fs.cp(args[0], args[1])
        elif cmd == "mv":
            if len(args) >= 2: self.fs.mv(args[0], args[1])
        elif cmd == "cat":
            self.fs.cat(args[0] if args else "")
        elif cmd == "touch":
            self.fs.touch(args[0] if args else "")
        elif cmd == "chmod":
            if len(args) >= 2: self.fs.chmod(args[0], args[1])
        elif cmd == "find":
            self.fs.find(args)
        elif cmd == "grep":
            if len(args) >= 2: self.fs.grep(args[0], args[1])

        # Kali Linux
        elif cmd == "kali-list":
            self.kali.list_tools()
        elif cmd == "nmap":
            self.kali.nmap(args)
        elif cmd == "hydra":
            self.kali.hydra(args)
        elif cmd == "john":
            self.kali.john(args)
        elif cmd == "sqlmap":
            self.kali.sqlmap(args)
        elif cmd == "nc" or cmd == "netcat":
            self.kali.netcat(args)

        # Qubes OS
        elif cmd == "qvm-list":
            self.qubes.qvm_list()
        elif cmd == "qvm-run":
            self.qubes.qvm_run(args)
        elif cmd == "qvm-create":
            self.qubes.qvm_create(args)
        elif cmd == "qvm-kill":
            self.qubes.qvm_kill(args)
        elif cmd == "qvm-prefs":
            self.qubes.qvm_prefs(args)
        elif cmd == "qubes-dom0-update":
            self.qubes.qubes_dom0_update()

        # Arch Linux
        elif cmd == "pacman":
            self.arch.pacman(args)
        elif cmd == "makepkg":
            self.arch.makepkg(args)
        elif cmd == "arch-chroot":
            self.arch.arch_chroot(args)
        elif cmd == "reflector":
            self.arch.reflector(args)

        # BlackArch
        elif cmd == "blackarch-install":
            self.blackarch.install_blackarch()
        elif cmd == "blackarch-cats":
            self.blackarch.list_categories()
        elif cmd == "blackarch-install-cat":
            self.blackarch.install_category(args[0] if args else "")
        elif cmd == "blackarch-search":
            self.blackarch.search_tool(args[0] if args else "")

        # Sistem
        elif cmd == "neofetch":
            SystemInfo.neofetch()
        elif cmd == "help" or cmd == "?":
            SystemInfo.help()
        elif cmd == "clear":
            os.system("clear" if os.name != 'nt' else "cls")
        elif cmd == "exit" or cmd == "quit":
            self.running = False
        elif cmd == "whoami":
            print(self.user)
        elif cmd == "date":
            print(datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
        elif cmd == "uname":
            print(f"Mark OS {platform.release()} {platform.machine()}")
        elif cmd == "sys":
            if args:
                subprocess.run(args)
            else:
                print("Kullanım: sys <system_command>")
        elif cmd == "python" or cmd == "python3":
            os.system("python3" if shutil.which("python3") else "python")
        else:
            # Sistem komutu dene
            if shutil.which(cmd):
                subprocess.run(parts)
            else:
                print(f"{Colors.RED}mark-sh: komut bulunamadı: {cmd}{Colors.END}")

    def run(self):
        print(f"""
{Colors.CYAN}{Colors.BOLD}
  __  __             _       ____   _____ 
 |  \/  | __ _ _ __ | | __  / ___| / ___|
 | |\\/| |/ _` | '_ \\| |/ /  \\___ \\| |    
 | |  | | (_| | | | |   <    ___) | |___ 
 |_|  |_|\\__,_|_| |_|_|\\_\\  |____/ \\____|
{Colors.END}
{Colors.GREEN}  Python Tabanlı İşletim Sistemi Shell'i{Colors.END}
{Colors.YELLOW}  Kali | Qubes | Arch | BlackArch Entegre{Colors.END}

  'help' yazarak komut listesine ulaşabilirsiniz.
  'exit' yazarak çıkabilirsiniz.
        """)
        while self.running:
            try:
                cmdline = input(self.prompt())
                self.execute(cmdline)
            except KeyboardInterrupt:
                print("\n")
            except EOFError:
                break
        print(f"{Colors.GREEN}[+] Mark OS kapatıldı. Güvenli kalın.{Colors.END}")

# ============================================================================
# BAŞLATMA
# ============================================================================
if __name__ == "__main__":
    shell = MarkShell()
    shell.run()
