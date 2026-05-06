# Güvenlik Araçları Kurulum Rehberi

> ⚠️ **Yasal Uyarı**: Bu araçlar yalnızca eğitim ve yetkili güvenlik testleri için kullanılmalıdır. Kötü amaçlı kullanım yasadışıdır.

---

## İçindekiler
1. [Kali Linux](#kali-linux)
2. [Metasploit Framework](#metasploit-framework)
3. [Mr Holmes](#mr-holmes)
4. [Diğer Önemli Araçlar](#diğer-önemli-araçlar)
5. [Docker Kurulumu](#docker-kurulumu)

---

## Kali Linux

### Resmi Kurulum

**Windows/Mac/Linux:**
- [Kali Linux İndirme](https://www.kali.org/get-kali/)
- [Kurulum Kılavuzu](https://www.kali.org/docs/installation/)

**WSL (Windows Subsystem for Linux) ile:**
```bash
wsl --install -d kalilinux
```

**VirtualBox/VMware ile:**
1. ISO dosyasını indirin
2. Sanal makine oluşturun
3. Minimum 2GB RAM ayırın

### Temel Araçlar
```bash
# Sistemi güncelle
sudo apt update && sudo apt upgrade -y

# Temel araçlar
sudo apt install -y metasploit-framework sqlmap nmap wireshark burpsuite john hashcat aircrack-ng

# İnternet bağlantısını test et
ping google.com
```

---

## Metasploit Framework

### Kurulum

**Linux/Kali (Önceden Yüklü):**
```bash
# Veritabanı başlat
sudo systemctl start postgresql
sudo msfdb init

# Metasploit konsolunu aç
msfconsole
```

**Debian/Ubuntu:**
```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/base/install.sh | bash
```

**Resmi Kaynaklar:**
- [Metasploit Docs](https://docs.metasploit.com/)
- [GitHub Repo](https://github.com/rapid7/metasploit-framework)

### Temel Komutlar
```bash
# Msfconsole başlat
msfconsole

# Modülü ara
search exploit/windows/smb

# Modülü seç
use exploit/windows/smb/ms17_010_eternalblue

# Seçenekleri göster
show options

# Hedefi ayarla
set RHOST 192.168.1.100

# Exploit çalıştır
run
```

---

## Mr Holmes

### Kurulum

```bash
# GitHub'dan klonla
git clone https://github.com/Lucksi/Mr-Holmes.git
cd Mr-Holmes

# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python holmes.py
```

**Özellikler:**
- Email reconnaissance
- Domain bilgisi toplama
- Sosyal medya araştırması
- OSINT (Open Source Intelligence)

### Kullanım
```bash
python holmes.py -e target@example.com
python holmes.py -d example.com
```

---

## Diğer Önemli Araçlar

### 1. **Nmap** - Port ve Ağ Taraması
```bash
# Kurulum
sudo apt install nmap

# Temel tarama
nmap 192.168.1.100

# Detaylı tarama
nmap -sV -A 192.168.1.100

# Tüm portları tara
nmap -p- 192.168.1.100
```

### 2. **Wireshark** - Ağ Analizi
```bash
# Kurulum
sudo apt install wireshark

# Çalıştır
wireshark

# Terminal kullanımı
tshark -i eth0 -w capture.pcap
```

### 3. **SQLMap** - SQL İnjection Testi
```bash
# Kurulum
sudo apt install sqlmap

# Basit kullanım
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Tüm veri tabanlarını listele
sqlmap -u "http://target.com/page.php?id=1" --dump-all
```

### 4. **Burp Suite** - Web Uygulama Test
```bash
# İndirme
# https://portswigger.net/burp/communitydownload

# Linux kurulumu
sudo apt install burpsuite

# Çalıştır
burpsuite
```

### 5. **Aircrack-ng** - WiFi Güvenliği
```bash
# Kurulum
sudo apt install aircrack-ng

# Monitor moduna geç
sudo airmon-ng start wlan0

# WiFi ağlarını tara
sudo airodump-ng wlan0mon

# Handshake yakala
sudo airodump-ng -c 6 -bssid XX:XX:XX:XX:XX:XX -w capture wlan0mon

# Şifre kırma
aircrack-ng -w wordlist.txt -b XX:XX:XX:XX:XX:XX capture-01.cap
```

### 6. **John the Ripper** - Şifre Kırma
```bash
# Kurulum
sudo apt install john

# Hash dosyasını kır
john --wordlist=wordlist.txt hashes.txt

# Belirli format kullan
john --format=md5 --wordlist=wordlist.txt hashes.txt

# Sonuçları göster
john --show hashes.txt
```

### 7. **Hashcat** - GPU Şifre Kırma
```bash
# Kurulum
sudo apt install hashcat

# MD5 hash kırma
hashcat -m 0 hashes.txt wordlist.txt

# SHA256 kırma
hashcat -m 1400 hashes.txt wordlist.txt
```

---

## Docker Kurulumu

Tüm araçları Docker container içinde çalıştırın:

### Dockerfile
```dockerfile
FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y \
    metasploit-framework \
    nmap \
    sqlmap \
    wireshark \
    aircrack-ng \
    john \
    hashcat \
    git \
    python3 \
    python3-pip

RUN git clone https://github.com/Lucksi/Mr-Holmes.git /opt/mr-holmes
WORKDIR /opt/mr-holmes
RUN pip install -r requirements.txt

WORKDIR /root
CMD ["/bin/bash"]
```

### Kurulum ve Çalıştırma
```bash
# Docker image oluştur
docker build -t security-tools .

# Container çalıştır
docker run -it security-tools

# Kalıcı veri için
docker run -it -v $(pwd):/data security-tools
```

---

## Kurulum Otomasyonu (Linux/Kali)

Aşağıdaki script tüm araçları otomatik kurar:

```bash
#!/bin/bash

echo "Güvenlik Araçları Kurulumu Başlıyor..."

# Sistem güncelle
sudo apt update
sudo apt upgrade -y

# Temel araçlar
sudo apt install -y \
    metasploit-framework \
    nmap \
    sqlmap \
    wireshark \
    burpsuite \
    john \
    hashcat \
    aircrack-ng \
    git \
    python3 \
    python3-pip \
    curl \
    wget

# Mr Holmes kurulumu
echo "Mr Holmes kuruluyor..."
git clone https://github.com/Lucksi/Mr-Holmes.git ~/tools/mr-holmes
cd ~/tools/mr-holmes
pip install -r requirements.txt

# PostgreSQL başlat (Metasploit için)
sudo systemctl start postgresql
sudo msfdb init

echo "Kurulum tamamlandı! ✓"
echo "Msfconsole başlatmak için: msfconsole"
echo "Nmap kullanmak için: nmap [hedef]"
echo "SQLMap kullanmak için: sqlmap -u [URL]"
```

---

## Öğrenme Kaynakları

### Resmi Dokümantasyon
- 📚 [Metasploit Academy](https://www.offensive-security.com/metasploit-course/)
- 📚 [Kali Linux Docs](https://www.kali.org/docs/)
- 📚 [HackTheBox](https://www.hackthebox.com/)
- 📚 [TryHackMe](https://tryhackme.com/)

### Türkçe Kaynaklar
- 🇹🇷 [BTK Akademi Siber Güvenlik](https://www.btkakademi.gov.tr/)
- 🇹🇷 [Siber Güvenlik Eğitimleri](https://www.udemy.com/)

---

## Yasal Kullanım

✅ **LEGAL KULLANIM:**
- Kendi sistemlerinize test yapma
- Yetkili kuruluşlar için penetration testing
- Eğitim ve öğrenme amaçlı
- Etik hackerlik sertifikaları için

❌ **YASAL OLMAYAN KULLANIM:**
- Başkasının sistemine izinsiz erişim
- Veri hırsızlığı
- DDoS saldırıları
- Kötü amaçlı yazılım dağıtma

---

## Güvenlik İpuçları

1. **Test Ortamı Oluştur**: Sanal makine kullan
2. **İzin Al**: Daima test etme izni al
3. **Logları Tuttur**: Tüm işlemleri dokümante et
4. **Gizlilik Anlaşması**: NDA imzala (profesyonel testler için)
5. **VPN Kullan**: Testleriniz sırasında VPN bağlantısı kullan

---

## Sorun Giderme

### Metasploit veritabanı hatası
```bash
sudo msfdb delete
sudo msfdb init
```

### Nmap kurulum sorunu
```bash
sudo apt install -y build-essential
sudo apt install nmap
```

### WiFi arayüzü görünmüyor
```bash
sudo rfkill list
sudo rfkill unblock wifi
```

---

## İletişim ve Destek

Sorularınız için resmi kaynakları kontrol edin:
- [Metasploit Discord](https://discord.gg/metasploit)
- [Kali Linux Forums](https://forums.kali.org/)
- [StackOverflow](https://stackoverflow.com/)

---

**Son Güncelleme**: 2026-05-06
**Lisans**: Educational Use Only
