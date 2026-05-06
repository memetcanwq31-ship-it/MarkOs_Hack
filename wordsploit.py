"""
WordSploit - Universal Security Tools Framework
Tüm platformlarda (Windows, macOS, Linux, Kali) çalışır
Universal güvenlik framework'ü
"""

__version__ = "1.0.0"
__author__ = "memetcanwq31-ship-it"
__description__ = "WordSploit - Universal Security Tools Framework"

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class WordSploit:
    """
    WordSploit - Tüm platformlarda çalışan güvenlik framework'ü
    """
    
    def __init__(self):
        self.version = __version__
        self.os_type = platform.system()  # Windows, Linux, Darwin (macOS)
        self.python_version = platform.python_version()
        self.home_dir = Path.home()
        self.wordsploit_dir = self.home_dir / ".wordsploit"
        self.tools_dir = self.wordsploit_dir / "tools"
        self.config_dir = self.wordsploit_dir / "config"
        self.wordlists_dir = self.wordsploit_dir / "wordlists"
        
        # Dizinleri oluştur
        self._create_directories()
        
    def _create_directories(self):
        """Gerekli dizinleri oluştur"""
        for directory in [self.wordsploit_dir, self.tools_dir, 
                         self.config_dir, self.wordlists_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def display_banner(self):
        """WordSploit banner'ı göster"""
        banner = """
        ╔══════════════════════════════════════════╗
        ║                                          ║
        ║          🚀 WORDSPLOIT 1.0.0 🚀         ║
        ║                                          ║
        ║    Universal Security Tools Framework    ║
        ║                                          ║
        ║  Windows | Linux | macOS | Kali Linux   ║
        ║                                          ║
        ╚══════════════════════════════════════════╝
        
        Platform: {os}
        Python: {python}
        Directory: {dir}
        
        """.format(
            os=self.os_type,
            python=self.python_version,
            dir=self.wordsploit_dir
        )
        print(banner)
    
    def check_system(self):
        """Sistem bilgilerini kontrol et ve göster"""
        print("[*] Sistem Bilgileri:")
        print(f"    ├─ İşletim Sistemi: {self.os_type}")
        print(f"    ├─ Python Sürümü: {self.python_version}")
        print(f"    ├─ Mimari: {platform.machine()}")
        print(f"    ├─ Hostname: {platform.node()}")
        print(f"    └─ Processor: {platform.processor()}")
        print()
    
    def install_requirements(self):
        """Gerekli Python paketlerini yükle"""
        print("[*] Gerekli Python paketleri yükleniyor...")
        
        requirements = [
            'requests',
            'beautifulsoup4',
            'paramiko',
            'scapy',
            'pexpect',
            'pycryptodome',
            'selenium',
            'shodan',
            'colorama',
            'click',
            'tabulate',
            'pyyaml'
        ]
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ])
            
            for package in requirements:
                print(f"  [→] {package} kuruluyor...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ])
            
            print("[✓] Tüm paketler kuruldu!")
        except subprocess.CalledProcessError as e:
            print(f"[✗] Hata: {e}")
    
    def get_tools_list(self) -> Dict:
        """Tüm araçları listele"""
        tools = {
            "Network Scanning": {
                "nmap": {
                    "description": "Port taraması ve ağ keşfi",
                    "command": "nmap",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "masscan": {
                    "description": "Hızlı port taraması",
                    "command": "masscan",
                    "platform": ["Linux", "Darwin"]
                }
            },
            "Web Tools": {
                "sqlmap": {
                    "description": "SQL injection testi",
                    "command": "sqlmap",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "nikto": {
                    "description": "Web sunucu taraması",
                    "command": "nikto",
                    "platform": ["Linux", "Darwin"]
                },
                "burp-suite": {
                    "description": "Web uygulama test framework'ü",
                    "command": "burpsuite",
                    "platform": ["Windows", "Linux", "Darwin"]
                }
            },
            "Exploitation": {
                "metasploit": {
                    "description": "Exploit framework",
                    "command": "msfconsole",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "msfvenom": {
                    "description": "Payload üretimi",
                    "command": "msfvenom",
                    "platform": ["Windows", "Linux", "Darwin"]
                }
            },
            "Password Cracking": {
                "john": {
                    "description": "Şifre kırma",
                    "command": "john",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "hashcat": {
                    "description": "GPU şifre kırma",
                    "command": "hashcat",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "hydra": {
                    "description": "Kuvvet saldırısı",
                    "command": "hydra",
                    "platform": ["Linux", "Darwin"]
                }
            },
            "OSINT": {
                "mr-holmes": {
                    "description": "E-mail reconnaissance",
                    "command": "python mr_holmes.py",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "theHarvester": {
                    "description": "E-mail ve subdomain toplama",
                    "command": "theHarvester",
                    "platform": ["Windows", "Linux", "Darwin"]
                }
            },
            "Wireless": {
                "aircrack-ng": {
                    "description": "WiFi güvenlik testi",
                    "command": "aircrack-ng",
                    "platform": ["Linux", "Darwin"]
                }
            },
            "Network Analysis": {
                "wireshark": {
                    "description": "Paket analiz aracı",
                    "command": "wireshark",
                    "platform": ["Windows", "Linux", "Darwin"]
                },
                "tcpdump": {
                    "description": "Paket yakalama",
                    "command": "tcpdump",
                    "platform": ["Linux", "Darwin"]
                }
            }
        }
        return tools
    
    def list_all_tools(self):
        """Tüm araçları formatlanmış şekilde göster"""
        tools = self.get_tools_list()
        
        print("\n" + "="*80)
        print("WORDSPLOIT - TÜM ARAÇLAR")
        print("="*80 + "\n")
        
        for category, category_tools in tools.items():
            print(f"\n📦 {category}")
            print("-" * 80)
            
            for tool_name, tool_info in category_tools.items():
                platforms = ", ".join(tool_info["platform"])
                print(f"  ├─ {tool_name:20} | {tool_info['description']}")
                print(f"  │  └─ Komut: {tool_info['command']}")
                print(f"  │  └─ Platform: {platforms}\n")
    
    def show_quick_commands(self):
        """Hızlı komut referansı göster"""
        commands = {
            "Network Scanning": [
                ("nmap -sV -A <target>", "Detaylı tarama"),
                ("nmap -p- <target>", "Tüm portları tara"),
                ("nmap -sU <target>", "UDP taraması"),
            ],
            "Web Testing": [
                ("sqlmap -u '<url>' --dbs", "Veritabanları listele"),
                ("nikto -h <target>", "Web sunucusu tara"),
            ],
            "Password Cracking": [
                ("john --wordlist=rockyou.txt hashes.txt", "John ile kırma"),
                ("hashcat -m 0 hashes.txt wordlist.txt", "Hashcat MD5 kırma"),
                ("hydra -l user -P wordlist.txt <host> ssh", "SSH brute force"),
            ],
            "OSINT": [
                ("python mr_holmes.py -e target@example.com", "Email reconnaissance"),
                ("theHarvester -d example.com -b google", "Subdomain toplama"),
            ]
        }
        
        print("\n" + "="*80)
        print("HIZLI KOMUT REFERANSI")
        print("="*80 + "\n")
        
        for category, cmds in commands.items():
            print(f"\n{category}:")
            for cmd, description in cmds:
                print(f"  $ {cmd}")
                print(f"    → {description}\n")
    
    def export_config(self):
        """Konfigürasyon dosyası oluştur"""
        config = {
            "version": self.version,
            "os": self.os_type,
            "python_version": self.python_version,
            "directories": {
                "home": str(self.home_dir),
                "wordsploit": str(self.wordsploit_dir),
                "tools": str(self.tools_dir),
                "config": str(self.config_dir),
                "wordlists": str(self.wordlists_dir)
            }
        }
        
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"[✓] Konfigürasyon kaydedildi: {config_file}")
        return config_file

def main():
    """Ana başlangıç fonksiyonu"""
    ws = WordSploit()
    
    # Banner göster
    ws.display_banner()
    
    # Sistem bilgileri
    ws.check_system()
    
    # Tüm araçları göster
    ws.list_all_tools()
    
    # Hızlı komutlar
    ws.show_quick_commands()
    
    # Konfigürasyon dosyası oluştur
    ws.export_config()
    
    print("\n" + "="*80)
    print("WordSploit hazır! Komutları çalıştırmaya başlayabilirsiniz.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
