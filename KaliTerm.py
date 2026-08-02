#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KaliTerm v2.0 — Kali Linux tarzı terminal emülatörü
(MarkOS Terminal'in Kali sürümü)
"""

import datetime
import fnmatch
import getpass
import os
import platform
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import time

# --- Windows'ta ANSI renk desteği ---
if sys.platform == "win32":
    os.system("")

C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_RED     = "\033[31m"
C_GREEN   = "\033[32m"
C_YELLOW  = "\033[33m"
C_BLUE    = "\033[34m"
C_MAGENTA = "\033[35m"
C_CYAN    = "\033[36m"
C_WHITE   = "\033[37m"

VERSION = "2.0"
HISTORY_FILE = os.path.expanduser("~/.kaliterm_history")

KALI_BANNER = f"""\
{C_RED}██╗  ██╗ █████╗ ██╗     ██╗    ████████╗███████╗██████╗ ███╗   ███╗{C_RESET}
{C_RED}██║ ██╔╝██╔══██╗██║     ██║    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║{C_RESET}
{C_RED}█████╔╝ ███████║██║     ██║       ██║   █████╗  ██████╔╝██╔████╔██║{C_RESET}
{C_RED}██╔═██╗ ██╔══██║██║     ██║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║{C_RESET}
{C_RED}██║  ██╗██║  ██║███████╗██║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║{C_RESET}
{C_RED}╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝{C_RESET}"""

# --- Kali Linux araç kataloğu (10 kategori) ---
KALI_TOOLS = {
    "01 - Bilgi Toplama": [
        ("nmap", "Ağ keşfi ve port tarama"),
        ("theHarvester", "E-posta, subdomain ve ana bilgisayar toplama"),
        ("whois", "Alan adı kayıt bilgileri"),
        ("dnsrecon", "DNS numaralandırma"),
        ("dnsenum", "DNS numaralandırma aracı"),
        ("recon-ng", "Web tabanlı OSINT çerçevesi"),
        ("maltego", "Grafik tabanlı istihbarat aracı"),
        ("whatweb", "Web sitesi teknoloji tespiti"),
    ],
    "02 - Zafiyet Analizi": [
        ("nikto", "Web sunucusu zafiyet tarayıcısı"),
        ("wpscan", "WordPress zafiyet tarayıcısı"),
        ("searchsploit", "Exploit-DB yerel arama"),
        ("openvas", "Zafiyet tarama çerçevesi"),
        ("nuclei", "Şablon tabanlı hızlı zafiyet tarayıcı"),
    ],
    "03 - Web Uygulama Analizi": [
        ("burpsuite", "Web proxy ve saldırı aracı"),
        ("zaproxy", "OWASP ZAP web güvenlik tarayıcısı"),
        ("sqlmap", "Otomatik SQL injection aracı"),
        ("gobuster", "Dizin ve DNS fuzzer"),
        ("ffuf", "Hızlı web fuzzer"),
        ("dirb", "Web dizin tarayıcı"),
        ("xsser", "XSS tespit ve sömürü aracı"),
        ("commix", "Komut enjeksiyon test aracı"),
    ],
    "04 - Parola Saldırıları": [
        ("hydra", "Çevrimiçi şifre kırma (protokoller)"),
        ("john", "John the Ripper şifre kırıcı"),
        ("hashcat", "GPU hızlandırmalı hash kırıcı"),
        ("medusa", "Paralel ağ oturum açma kırıcı"),
        ("ncrack", "Ağ kimlik doğrulama kırıcı"),
        ("crunch", "Sözlük üreteci"),
        ("cewl", "Web sitesinden kelime listesi üretme"),
    ],
    "05 - Kablosuz Saldırılar": [
        ("aircrack-ng", "Wi-Fi güvenlik denetim paketi"),
        ("wifite", "Otomatik kablosuz saldırı aracı"),
        ("reaver", "WPS PIN saldırısı"),
        ("kismet", "Kablosuz ağ dedektörü"),
        ("wifiphisher", "Sahte AP ile kimlik avı"),
    ],
    "06 - Sömürü Araçları": [
        ("metasploit-framework", "Sömürü geliştirme çerçevesi"),
        ("armitage", "Metasploit grafik arayüzü"),
        ("beef-xss", "Tarayıcı sömürü çerçevesi"),
        ("searchsploit", "Exploit veritabanı arama"),
    ],
    "07 - Sniffing & Spoofing": [
        ("wireshark", "Ağ paket analizörü"),
        ("tcpdump", "Komut satırı paket yakalayıcı"),
        ("ettercap", "MITM saldırı paketi"),
        ("bettercap", "Modern MITM çerçevesi"),
        ("macchanger", "MAC adresi değiştirici"),
    ],
    "08 - Post Exploitation": [
        ("powershell-empire", "Post-exploitation çerçevesi"),
        ("crackmapexec", "Ağ servislerinde yetki testi"),
        ("evil-winrm", "WinRM uzak shell"),
        ("chisel", "Hızlı tünelleme aracı"),
    ],
    "09 - Adli Bilişim": [
        ("autopsy", "Disk adli analiz aracı"),
        ("foremost", "Silinen dosya kurtarma"),
        ("binwalk", "Firmware analizi"),
        ("steghide", "Steganografi aracı"),
        ("exiftool", "Meta veri okuyucu"),
        ("volatility", "Bellek adli analizi"),
    ],
    "10 - Raporlama": [
        ("faraday", "Zafiyet yönetim platformu"),
        ("dradis", "Pentest raporlama çerçevesi"),
        ("pipal", "Parola istatistik analizi"),
    ],
}

ALIASES = {
    "ll": "ls -la",
    "la": "ls -a",
    "l": "ls",
    "disk": "df",
    "mem": "free",
    "ipaddr": "ipinfo",
    "cls": "clear",
    "kali": "banner",
    "h": "help",
    "q": "exit",
}

EXTERNAL_COMMANDS = [
    "whoami", "id", "hostname", "netstat", "ss", "route", "arp",
    "traceroute", "nslookup", "dig", "curl", "wget", "git",
    "python3", "pip3", "bash", "sh", "env", "du", "stat", "file",
    "strings", "hexdump", "xxd", "lsof", "mount", "ifconfig",
]


class KaliTermEngine:
    def __init__(self):
        self.cwd = os.getcwd()
        self._prev_cwd = self.cwd
        self.history = []
        self.uid_is_root = False
        self.cmds = {
            "help": self._cmd_help,
            "version": self._cmd_version,
            "about": self._cmd_version,
            "banner": self._cmd_banner,
            "clear": self._cmd_clear,
            "time": self._cmd_time,
            "date": self._cmd_date,
            "history": self._cmd_history,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "ls": self._cmd_ls,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "mkdir": self._cmd_mkdir,
            "touch": self._cmd_touch,
            "cp": self._cmd_cp,
            "mv": self._cmd_mv,
            "rm": self._cmd_rm,
            "find": self._cmd_find,
            "grep": self._cmd_grep,
            "head": self._cmd_head,
            "tail": self._cmd_tail,
            "wc": self._cmd_wc,
            "tree": self._cmd_tree,
            "fetch": self._cmd_fetch,
            "tools": self._cmd_tools,
            "tool": self._cmd_tool,
            "apt": self._cmd_apt,
            "su": self._cmd_su,
            "sudo": self._cmd_sudo,
            "run": self._cmd_run,
            "ping": self._cmd_ping,
            "uname": self._cmd_uname,
            "uptime": self._cmd_uptime,
            "df": self._cmd_df,
            "free": self._cmd_free,
            "ps": self._cmd_ps,
            "kill": self._cmd_kill,
            "sysinfo": self._cmd_sysinfo,
            "cpuinfo": self._cmd_cpuinfo,
            "meminfo": self._cmd_meminfo,
            "ipinfo": self._cmd_ipinfo,
        }
        for name in EXTERNAL_COMMANDS:
            self.cmds[name] = (lambda n: lambda a: self._run_external(n, a))(name)
        self._load_history()

    # ---------- geçmiş ----------
    def _load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    self.history = [ln.rstrip("\n") for ln in f if ln.strip()]
        except Exception:
            pass

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(self.history[-500:]))
        except Exception:
            pass

    # ---------- komut istemi ----------
    def prompt(self):
        user = "root" if self.uid_is_root else (getpass.getuser() or "kali")
        host = socket.gethostname() or "kali"
        home = os.path.expanduser("~")
        if self.cwd == home:
            shown = "~"
        elif self.cwd.startswith(home + os.sep):
            shown = "~" + self.cwd[len(home):]
        else:
            shown = self.cwd
        marker = "#" if self.uid_is_root else "$"
        color_user = C_RED if self.uid_is_root else C_GREEN
        return (f"{color_user}{user}@{host}{C_RESET}:{C_BLUE}{shown}{C_RESET}{marker} ")

    # ---------- ana çalıştırıcı ----------
    def execute(self, line):
        line = line.strip()
        if not line:
            return ""
        stages = self._split_pipeline(line)
        if len(stages) > 1:
            return self._pipeline(stages)
        try:
            parts = shlex.split(stages[0])
        except ValueError:
            return f"{stages[0]}: hatalı sözdizimi\n"
        if not parts:
            return ""
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("exit", "quit"):
            return "Çıkış yapılıyor...\n"
        if cmd in ALIASES:
            alias_cmd = ALIASES[cmd]
            if args:
                alias_cmd += " " + " ".join(shlex.join([a]) for a in args)
            return self.execute(alias_cmd)
        if cmd in self.cmds:
            return self.cmds[cmd](args)
        if shutil.which(cmd):
            return self._run([cmd] + args)
        if cmd in self._all_tool_names():
            return (f"'{cmd}' Kali Linux aracı — bu sistemde kurulu değil.\n"
                    f"  Detay     : tool {cmd}\n"
                    f"  Simüle kur: apt install {cmd}\n"
                    f"  Gerçek kur: sudo apt install {cmd}   (Linux'ta)\n")
        return f"{cmd}: komut bulunamadı. 'help' yazın.\n"

    # ---------- boru (pipeline) ----------
    def _split_pipeline(self, line):
        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = "|"
        lexer.whitespace_split = True
        lexer.commenters = ""
        try:
            return [tok.strip() for tok in lexer if tok.strip()]
        except ValueError:
            return [line]

    def _pipeline(self, stages):
        out = self.execute(stages[0])
        for stage in stages[1:]:
            out = self._apply_filter(stage, out)
        return out

    def _apply_filter(self, stage, text):
        try:
            parts = shlex.split(stage)
        except ValueError:
            return text
        if not parts:
            return text
        name = parts[0].lower()
        args = parts[1:]
        lines = text.splitlines(keepends=True)

        if name == "grep":
            if not args:
                return ""
            case_insensitive = "-i" in args
            args = [a for a in args if a != "-i"]
            pattern = args[0].lower() if case_insensitive else args[0]
            res = [ln for ln in lines
                   if pattern in (ln.lower() if case_insensitive else ln)]
            return "".join(res)
        if name == "head":
            n = 10
            if args and args[0].isdigit():
                n = int(args[0])
            return "".join(lines[:n])
        if name == "tail":
            n = 10
            if args and args[0].isdigit():
                n = int(args[0])
            return "".join(lines[-n:])
        if name == "wc":
            flags = set()
            for a in args:
                if a.startswith("-") and len(a) > 1:
                    flags.update(a[1:])
            if not flags:
                flags = {"l", "w", "c"}
            l, w, c = len(lines), sum(len(x.split()) for x in lines), len(text)
            vals = []
            for f in sorted(flags):
                if f == "l":
                    vals.append(str(l))
                elif f == "w":
                    vals.append(str(w))
                elif f == "c":
                    vals.append(str(c))
            return " ".join(vals) + "\n"
        if name == "sort":
            return "".join(sorted(lines, reverse=("-r" in args)))
        if name == "uniq":
            res, last = [], None
            for ln in lines:
                if ln != last:
                    res.append(ln)
                    last = ln
            return "".join(res)
        if name == "cat":
            return text
        if name == "tr" and len(args) >= 2 and len(args[0]) == len(args[1]) \
                and not args[0].startswith("-"):
            return text.translate(str.maketrans(args[0], args[1]))
        return text

    # ---------- alt süreç ----------
    def _run(self, parts):
        try:
            res = subprocess.run(parts, capture_output=True, text=True,
                                 timeout=15, cwd=self.cwd)
            out = res.stdout
            if res.stderr:
                out += res.stderr
            return out
        except FileNotFoundError:
            return f"{parts[0]}: komut bulunamadı (PATH'te yok)\n"
        except subprocess.TimeoutExpired:
            return f"{parts[0]}: zaman aşımı\n"
        except Exception as e:
            return f"{parts[0]}: {e}\n"

    def _run_external(self, name, args):
        if not shutil.which(name):
            return f"{name}: komut bulunamadı (PATH'te yok)\n"
        return self._run([name] + args)

    def _all_tool_names(self):
        return {n for tools in KALI_TOOLS.values() for n, _ in tools}

    def _spin(self, msg, seconds):
        frames = "|/-\\"
        end = time.time() + seconds
        i = 0
        while time.time() < end:
            print(f"\r{msg}... {frames[i % len(frames)]}", end="", flush=True)
            time.sleep(0.08)
            i += 1
        print("\r" + " " * (len(msg) + 10) + "\r", end="", flush=True)

    # ---------- sistem bilgisi ----------
    def _os_pretty(self):
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", encoding="utf-8") as f:
                    for ln in f:
                        if ln.startswith("PRETTY_NAME="):
                            return ln.split("=", 1)[1].strip().strip('"')
            except Exception:
                pass
        return f"{platform.system()} {platform.release()}"

    def _uptime_str(self):
        try:
            with open("/proc/uptime") as f:
                sec = float(f.read().split()[0])
            d, rem = divmod(int(sec), 86400)
            h, rem = divmod(rem, 3600)
            m, s = divmod(rem, 60)
            return f"up {d} gün, {h}:{m:02d}:{s:02d}"
        except Exception:
            return "up bilinmiyor"

    def _mem_str(self):
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                mem = {}
                for ln in f:
                    k, _, v = ln.partition(":")
                    mem[k] = int(v.strip().split()[0])
            total = mem.get("MemTotal", 0) // 1024
            avail = mem.get("MemAvailable", mem.get("MemFree", 0)) // 1024
            return f"{total - avail} MiB / {total} MiB"
        except Exception:
            return "N/A"

    def _h(self, n):
        for unit in ("B", "K", "M", "G", "T"):
            if n < 1024:
                return f"{n:.1f}{unit}"
            n /= 1024
        return f"{n:.1f}P"

    # ---------- komutlar ----------
    def _cmd_help(self, args):
        return f"""\
{C_BOLD}KaliTerm v{VERSION}{C_RESET} — Kali Linux tarzı terminal emülatörü

{C_YELLOW}Sistem Bilgisi{C_RESET}
  uname, whoami, id, hostname, uptime, free, df, ps, kill
  sysinfo, cpuinfo, meminfo, fetch (neofetch tarzı özet)

{C_YELLOW}Dosya İşlemleri{C_RESET}
  ls, cd, pwd, cat, echo, mkdir, touch, cp, mv, rm, find, tree

{C_YELLOW}Metin İşlemleri{C_RESET}
  grep, head, tail, wc, sort, uniq   (boru | ile birlikte çalışır)

{C_YELLOW}Ağ Komutları{C_RESET}
  ip, ifconfig, ipinfo, netstat, ss, route, ping, traceroute
  nslookup, dig, curl, wget

{C_YELLOW}Kali Linux Araçları{C_RESET}
  tools               - Araç kataloğu (10 kategori)
  tool <araç>         - Araç hakkında bilgi
  apt install <araç>  - Simüle kurulum (ör: apt install nmap)

{C_YELLOW}Diğer{C_RESET}
  banner, version, clear, history, run <komut>, su, sudo, exit

Örnekler:
  ls -la | grep py
  fetch
  tools
  nmap -sV 127.0.0.1    (nmap kuruluysa gerçekten çalışır)
"""

    def _cmd_version(self, args):
        return f"KaliTerm v{VERSION} — Kali Linux tarzı terminal emülatörü\n"

    def _cmd_banner(self, args):
        return KALI_BANNER + "\n"

    def _cmd_clear(self, args):
        return "\033[2J\033[H"

    def _cmd_time(self, args):
        return datetime.datetime.now().strftime("%H:%M:%S\n")

    def _cmd_date(self, args):
        return datetime.datetime.now().strftime("%Y-%m-%d (%A)\n")

    def _cmd_history(self, args):
        if not self.history:
            return ""
        return "\n".join(f"{i+1:4d}  {h}" for i, h in enumerate(self.history)) + "\n"

    def _cmd_cd(self, args):
        if not args or args[0] in ("~", ""):
            target = os.path.expanduser("~")
        elif args[0] == "-":
            target = getattr(self, "_prev_cwd", self.cwd)
        else:
            target = args[0]
        new = os.path.abspath(os.path.join(self.cwd, os.path.expanduser(target)))
        if not os.path.isdir(new):
            return f"cd: {args[0]}: Böyle bir dizin yok\n"
        self._prev_cwd = self.cwd
        self.cwd = new
        return ""

    def _cmd_pwd(self, args):
        return self.cwd + "\n"

    def _cmd_ls(self, args):
        path = self.cwd
        show_hidden, long = False, False
        for a in args:
            if a.startswith("-") and len(a) > 1:
                if "a" in a[1:]:
                    show_hidden = True
                if "l" in a[1:]:
                    long = True
            else:
                path = os.path.join(self.cwd, a)
        if not os.path.isdir(path):
            return f"ls: {path}: Böyle bir dizin yok\n"
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return f"ls: {path}: İzin reddedildi\n"
        if not show_hidden:
            entries = [e for e in entries if not e.startswith(".")]
        if long:
            lines = []
            for e in entries:
                full = os.path.join(path, e)
                try:
                    st = os.stat(full)
                    mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%b %d %H:%M")
                    lines.append(f"{stat.filemode(st.st_mode)} {st.st_size:>10} {mtime} {e}")
                except OSError:
                    lines.append(e)
            return "\n".join(lines) + "\n"
        colored = []
        for e in entries:
            full = os.path.join(path, e)
            if os.path.isdir(full):
                colored.append(C_BLUE + C_BOLD + e + C_RESET)
            elif os.path.islink(full):
                colored.append(C_CYAN + e + C_RESET)
            elif os.access(full, os.X_OK):
                colored.append(C_GREEN + e + C_RESET)
            else:
                colored.append(e)
        return "  ".join(colored) + "\n"

    def _cmd_cat(self, args):
        if not args:
            return "cat: kullanım: cat <dosya>\n"
        out = []
        for f in args:
            p = os.path.join(self.cwd, f)
            if not os.path.exists(p):
                out.append(f"cat: {f}: Böyle bir dosya veya dizin yok")
                continue
            if os.path.isdir(p):
                out.append(f"cat: {f}: Bir dizindir")
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    out.append(fh.read().rstrip("\n"))
            except Exception as e:
                out.append(f"cat: {f}: {e}")
        return "\n".join(out) + "\n"

    def _cmd_echo(self, args):
        if not args:
            return "\n"
        no_newline = args[0] == "-n"
        if no_newline:
            args = args[1:]
        text = os.path.expandvars(" ".join(args))
        return text + ("" if no_newline else "\n")

    def _cmd_mkdir(self, args):
        if not args:
            return "mkdir: kullanım: mkdir <dizin>\n"
        parents = "-p" in args
        args = [a for a in args if a != "-p"]
        for d in args:
            p = os.path.join(self.cwd, d)
            try:
                if parents:
                    os.makedirs(p, exist_ok=True)
                else:
                    os.mkdir(p)
            except FileExistsError:
                return f"mkdir: {d}: Zaten mevcut\n"
            except Exception as e:
                return f"mkdir: {d}: {e}\n"
        return ""

    def _cmd_touch(self, args):
        if not args:
            return "touch: kullanım: touch <dosya>\n"
        for f in args:
            p = os.path.join(self.cwd, f)
            try:
                with open(p, "a"):
                    os.utime(p, None)
            except Exception as e:
                return f"touch: {f}: {e}\n"
        return ""

    def _cmd_cp(self, args):
        if len(args) < 2:
            return "cp: kullanım: cp <kaynak> <hedef>\n"
        src = os.path.join(self.cwd, args[-2])
        dst = os.path.join(self.cwd, args[-1])
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            return f"cp: {e}\n"
        return ""

    def _cmd_mv(self, args):
        if len(args) < 2:
            return "mv: kullanım: mv <kaynak> <hedef>\n"
        src = os.path.join(self.cwd, args[-2])
        dst = os.path.join(self.cwd, args[-1])
        try:
            shutil.move(src, dst)
        except Exception as e:
            return f"mv: {e}\n"
        return ""

    def _cmd_rm(self, args):
        if not args:
            return "rm: kullanım: rm [-r] <hedef>\n"
        recursive = "-r" in args or "-rf" in args or "-fr" in args
        force = "-f" in args or "-rf" in args or "-fr" in args
        args = [a for a in args if not a.startswith("-")]
        for t in args:
            p = os.path.abspath(os.path.join(self.cwd, t))
            if p in (os.path.abspath(os.sep),
                     os.path.abspath(os.path.expanduser("~"))):
                return f"rm: {t}: Kritik dizin koruması — silme engellendi.\n"
            try:
                if os.path.isdir(p):
                    if recursive:
                        shutil.rmtree(p)
                    else:
                        return f"rm: {t}: Bir dizindir (-r kullanın)\n"
                else:
                    os.remove(p)
            except FileNotFoundError:
                if not force:
                    return f"rm: {t}: Böyle bir dosya yok\n"
            except Exception as e:
                if not force:
                    return f"rm: {t}: {e}\n"
        return ""

    def _cmd_find(self, args):
        path, pattern = self.cwd, None
        i = 0
        while i < len(args):
            if args[i] == "-name" and i + 1 < len(args):
                pattern = args[i + 1]
                i += 2
                continue
            if not args[i].startswith("-"):
                path = os.path.join(self.cwd, args[i])
            i += 1
        if not os.path.isdir(path):
            return f"find: {path}: Böyle bir dizin yok\n"
        out = []
        for root, dirs, files in os.walk(path):
            for name in dirs + files:
                if pattern and not fnmatch.fnmatch(name, pattern):
                    continue
                out.append(os.path.join(root, name))
        return "\n".join(out) + ("\n" if out else "")

    def _cmd_grep(self, args):
        if not args:
            return "grep: kullanım: grep [-i] <desen> [dosya...]\n"
        case_insensitive = "-i" in args
        args = [a for a in args if a != "-i"]
        if not args:
            return "grep: desen gerekli\n"
        pattern, files = args[0], args[1:]
        if not files:
            return ""  # pipeline modu
        needle = pattern.lower() if case_insensitive else pattern
        out = []
        for f in files:
            p = os.path.join(self.cwd, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    for ln in fh:
                        hay = ln.lower() if case_insensitive else ln
                        if needle in hay:
                            prefix = f + ":" if len(files) > 1 else ""
                            out.append(prefix + ln.rstrip("\n"))
            except Exception as e:
                out.append(f"grep: {f}: {e}")
        return "\n".join(out) + ("\n" if out else "")

    def _cmd_head(self, args):
        n, files = 10, []
        i = 0
        while i < len(args):
            a = args[i]
            if a.startswith("-") and len(a) > 1 and a[1:].isdigit():
                n = int(a[1:])
            elif a == "-n" and i + 1 < len(args) and args[i + 1].isdigit():
                n = int(args[i + 1])
                i += 1
            else:
                files.append(a)
            i += 1
        if not files:
            return "head: kullanım: head [-n N] <dosya>\n"
        out = []
        for f in files:
            p = os.path.join(self.cwd, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    out.append("".join(fh.readlines()[:n]).rstrip("\n"))
            except Exception as e:
                out.append(f"head: {f}: {e}")
        return "\n".join(out) + "\n"

    def _cmd_tail(self, args):
        n, files = 10, []
        i = 0
        while i < len(args):
            a = args[i]
            if a.startswith("-") and len(a) > 1 and a[1:].isdigit():
                n = int(a[1:])
            elif a == "-n" and i + 1 < len(args) and args[i + 1].isdigit():
                n = int(args[i + 1])
                i += 1
            else:
                files.append(a)
            i += 1
        if not files:
            return "tail: kullanım: tail [-n N] <dosya>\n"
        out = []
        for f in files:
            p = os.path.join(self.cwd, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    out.append("".join(fh.readlines()[-n:]).rstrip("\n"))
            except Exception as e:
                out.append(f"tail: {f}: {e}")
        return "\n".join(out) + "\n"

    def _cmd_wc(self, args):
        files = [a for a in args if not a.startswith("-")]
        flags = set()
        for a in args:
            if a.startswith("-") and len(a) > 1 and not a.startswith("--"):
                flags.update(a[1:])
        if not flags:
            flags = {"l", "w", "c"}
        if not files:
            return "wc: kullanım: wc [-lwc] <dosya>\n"
        lines_out = []
        total_l = total_w = total_c = 0
        for f in files:
            p = os.path.join(self.cwd, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                l, w, c = text.count("\n"), len(text.split()), len(text)
            except Exception as e:
                lines_out.append(f"wc: {f}: {e}")
                continue
            total_l += l; total_w += w; total_c += c
            vals = [str(l) if "l" in flags else "",
                    str(w) if "w" in flags else "",
                    str(c) if "c" in flags else ""]
            lines_out.append(" ".join(v for v in vals if v) + f" {f}")
        if len(files) > 1:
            vals = [str(total_l) if "l" in flags else "",
                    str(total_w) if "w" in flags else "",
                    str(total_c) if "c" in flags else ""]
            lines_out.append(" ".join(v for v in vals if v) + " toplam")
        return "\n".join(lines_out) + "\n"

    def _cmd_tree(self, args):
        path = self.cwd
        depth = 2
        i = 0
        while i < len(args):
            a = args[i]
            if a == "-L" and i + 1 < len(args):
                depth = int(args[i + 1]); i += 2; continue
            if not a.startswith("-"):
                path = os.path.join(self.cwd, a)
            i += 1
        if not os.path.isdir(path):
            return f"tree: {path}: Böyle bir dizin yok\n"

        def walk(p, prefix, level):
            out = []
            try:
                entries = sorted(os.listdir(p))
            except PermissionError:
                return out
            entries = [e for e in entries if not e.startswith(".")]
            for idx, e in enumerate(entries):
                full = os.path.join(p, e)
                last = idx == len(entries) - 1
                branch = "└── " if last else "├── "
                if os.path.isdir(full):
                    out.append(f"{prefix}{branch}{C_BLUE}{C_BOLD}{e}{C_RESET}/")
                    if level < depth:
                        out.extend(walk(full, prefix + ("    " if last else "│   "), level + 1))
                else:
                    out.append(f"{prefix}{branch}{e}")
            return out

        return os.path.basename(path) + "/\n" + "\n".join(walk(path, "", 1)) + "\n"

    def _cmd_fetch(self, args):
        user = getpass.getuser() or "kali"
        host = socket.gethostname() or "kali"
        os_name = self._os_pretty()
        kernel = platform.release() or "unknown"
        uptime = self._uptime_str()
        shell = "bash"
        term = os.environ.get("TERM", "xterm-256color")
        cpu = platform.processor() or platform.machine() or "unknown"
        mem = self._mem_str()
        pkgs = "N/A"
        if shutil.which("dpkg"):
            try:
                res = subprocess.run(["dpkg", "--list"], capture_output=True, text=True, timeout=10)
                pkgs = str(res.stdout.count("\n"))
            except Exception:
                pass
        art = f"""\
{C_RED}╔═══════════════════╗{C_RESET}  {C_GREEN}{user}@{host}{C_RESET}
{C_RED}║ ██╗  ██╗ █████╗ ║{C_RESET}  {C_BOLD}OS:{C_RESET}        {os_name}
{C_RED}║ ██║ ██╔╝██╔══██╗║{C_RESET}  {C_BOLD}Kernel:{C_RESET}    {kernel}
{C_RED}║ █████╔╝ ███████║║{C_RESET}  {C_BOLD}Uptime:{C_RESET}    {uptime}
{C_RED}║ ██╔═██╗ ██╔══██║║{C_RESET}  {C_BOLD}Shell:{C_RESET}     {shell}
{C_RED}║ ██║  ██╗██║  ██║║{C_RESET}  {C_BOLD}Terminal:{C_RESET}  {term}
{C_RED}║ ╚═╝  ╚═╝╚═╝  ╚═╝║{C_RESET}  {C_BOLD}CPU:{C_RESET}       {cpu}
{C_RED}╚═══════════════════╝{C_RESET}  {C_BOLD}Bellek:{C_RESET}    {mem}
{C_RED}                      {C_RESET}  {C_BOLD}Paketler:{C_RESET}   {pkgs}
"""
        return art + "\n"

    def _cmd_tools(self, args):
        out = [f"{C_BOLD}Kali Linux Araç Kataloğu{C_RESET} — {sum(len(v) for v in KALI_TOOLS.values())} araç\n"]
        for cat, tools in KALI_TOOLS.items():
            out.append(f"{C_YELLOW}{cat}{C_RESET}")
            for name, desc in tools:
                out.append(f"  {C_GREEN}{name:<22}{C_RESET} {desc}")
            out.append("")
        return "\n".join(out)

    def _cmd_tool(self, args):
        if not args:
            return "tool: kullanım: tool <araç-adı>\n"
        name = args[0].lower()
        for cat, tools in KALI_TOOLS.items():
            for tname, desc in tools:
                if tname == name:
                    return (f"{C_GREEN}{name}{C_RESET}: {desc}\n"
                            f"  Kategori : {cat}\n"
                            f"  Durum    : {'KURULU' if shutil.which(name) else 'kurulu değil'}\n"
                            f"  Simüle kur: apt install {name}\n")
        return f"tool: '{name}' katalogda bulunamadı. 'tools' yazın.\n"

    def _cmd_apt(self, args):
        if not args:
            return "apt: kullanım: apt install <araç>\n"
        if args[0] == "install" and len(args) > 1:
            name = args[1].lower()
            if shutil.which(name):
                return f"'{name}' zaten kurulu (gerçek sistemde).\n"
            if name not in self._all_tool_names():
                return f"apt: '{name}' KaliTerm kataloğunda yok. 'tools' yazın.\n"
            self._spin(f"Paket listeleri okunuyor", 0.6)
            self._spin(f"{name} indiriliyor", 0.8)
            self._spin(f"{name} kuruluyor", 0.7)
            return f"{C_GREEN}[✓]{C_RESET} '{name}' KaliTerm'e simüle olarak kuruldu.\n"
        if args[0] == "update":
            self._spin("Paket listeleri güncelleniyor", 1.0)
            return "Paket listeleri güncellendi.\n"
        return "apt: desteklenen alt komut: install, update\n"

    def _cmd_su(self, args):
        if self.uid_is_root:
            return "Zaten root'sunuz.\n"
        self.uid_is_root = True
        return "root@kali şifresi: \033[1;32mroot yetkileri etkin\033[0m\n"

    def _cmd_sudo(self, args):
        if not args:
            return "sudo: komut belirtilmedi\n"
        if args[0] in ("su", "bash", "sh") or args[0] == "-i":
            self.uid_is_root = True
            return "root yetkileri etkin\n"
        if args[0] == "apt":
            return self._cmd_apt(args[1:])
        return self.execute(" ".join(shlex.join(a) for a in args))

    def _cmd_run(self, args):
        if not args:
            return "run: kullanım: run <komut>\n"
        return self.execute(" ".join(shlex.join(a) for a in args))

    def _cmd_ping(self, args):
        if not args:
            return "ping: kullanım: ping <hedef>\n"
        target = args[0]
        if any(c in target for c in ";|&$`"):
            return "ping: Geçersiz hedef\n"
        if shutil.which("ping"):
            flag = "-n" if sys.platform == "win32" else "-c"
            return self._run(["ping", flag, "2", target])
        self._spin(f"{target} pingleniyor", 0.8)
        return f"--- {target} ping istatistikleri ---\n2 paket gönderildi, 2 alındı, %0 kayıp\n"

    def _cmd_uname(self, args):
        if shutil.which("uname"):
            if args and args[0].startswith("-"):
                return self._run(["uname"] + args)
            return self._run(["uname", "-a"])
        return self._platform_info()

    def _cmd_uptime(self, args):
        if shutil.which("uptime"):
            return self._run(["uptime"])
        return self._uptime_str() + "\n"

    def _cmd_df(self, args):
        if shutil.which("df"):
            return self._run(["df", "-h"] + args)
        return "df: komut bulunamadı (yalnızca Linux/macOS)\n"

    def _cmd_free(self, args):
        if shutil.which("free"):
            return self._run(["free", "-h"] + args)
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                mem = {}
                for ln in f:
                    k, _, v = ln.partition(":")
                    mem[k] = int(v.strip().split()[0])
            total = mem.get("MemTotal", 0) // 1024
            free_mem = mem.get("MemFree", 0) // 1024
            avail = mem.get("MemAvailable", free_mem) // 1024
            used = total - avail
            return (f"              toplam   kullanılan  boş\n"
                    f"Bellek:       {total:>6}M     {used:>6}M   {free_mem:>6}M\n")
        except Exception as e:
            return f"free: {e}\n"

    def _cmd_ps(self, args):
        if shutil.which("ps"):
            return self._run(["ps", "aux"])
        return "ps: komut bulunamadı\n"

    def _cmd_kill(self, args):
        if len(args) < 1:
            return "kill: kullanım: kill <pid>\n"
        try:
            pid = int(args[-1])
        except ValueError:
            return f"kill: '{args[-1]}' geçersiz PID\n"
        try:
            os.kill(pid, 9)
            return f"PID {pid} sonlandırıldı\n"
        except ProcessLookupError:
            return f"kill: PID {pid} bulunamadı\n"
        except PermissionError:
            return f"kill: PID {pid} için yetki yok\n"

    def _cmd_sysinfo(self, args):
        lines = [f"{C_BOLD}=== Sistem Bilgisi ==={C_RESET}"]
        lines.append(self._run(["uname", "-a"]) if shutil.which("uname") else self._platform_info())
        lines.append("Uptime  : " + self._uptime_str())
        lines.append("Bellek  : " + self._mem_str())
        lines.append("Tarih   : " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("Kullanıcı: " + (getpass.getuser() or "unknown"))
        lines.append("Hostname: " + (socket.gethostname() or "unknown"))
        lines.append("Python  : " + platform.python_version())
        if shutil.which("df"):
            lines.append("\n" + self._run(["df", "-h"]))
        return "\n".join(lines) + "\n"

    def _cmd_cpuinfo(self, args):
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"cpuinfo: {e}\n"
        return f"İşlemci: {platform.processor() or platform.machine()}\n" \
               f"Mimari : {platform.machine()}\n"

    def _cmd_meminfo(self, args):
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"meminfo: {e}\n"
        return f"Bellek  : {self._mem_str()}\n"

    def _cmd_ipinfo(self, args):
        if shutil.which("ip"):
            return self._run(["ip", "addr"])
        if shutil.which("ifconfig"):
            return self._run(["ifconfig"])
        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)
            return f"Hostname: {host}\nIP Adres: {ip}\n"
        except Exception as e:
            return f"ipinfo: {e}\n"

    def _platform_info(self):
        return f"{platform.system()} {platform.release()} ({platform.machine()})\n"


def main():
    engine = KaliTermEngine()
    print(KALI_BANNER)
    print(f"{C_GREEN}KaliTerm v{VERSION}{C_RESET} — {C_YELLOW}Kali Linux tarzı terminal{C_RESET}")
    print(f"{C_CYAN}Yardım için 'help', araç listesi için 'tools' yazın.{C_RESET}\n")

    import readline  # sekme tamamlama
    completions = (list(engine.cmds.keys()) + list(ALIASES.keys())
                   + sorted(engine._all_tool_names())
                   + EXTERNAL_COMMANDS)

    def completer(text, state):
        options = [c + " " for c in completions if c.startswith(text)]
        return options[state] if state < len(options) else None

    try:
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass

    while True:
        try:
            command = input(engine.prompt())
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break
        if not command.strip():
            continue
        engine.history.append(command)
        output = engine.execute(command)
        print(output, end="")
        if command.strip() in ("exit", "quit"):
            break
    engine._save_history()


if __name__ == "__main__":
    main()
