#!/bin/bash

# Güvenlik Araçları Otomatik Kurulum Scripti
# Security Tools Automated Installation Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Güvenlik Araçları Kurulum Paketi   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Sistem Kontrolü
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Bu script root yetkisiyle çalıştırılmalıdır!${NC}"
   echo "Lütfen: sudo bash install.sh"
   exit 1
fi

# OS Tespiti
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    fi
    echo -e "${GREEN}[✓] İşletim Sistemi: $OS${NC}"
else
    echo -e "${RED}[✗] Bu script sadece Linux/Kali Linux için çalışır${NC}"
    exit 1
fi

# Yapılandırma
TOOLS_DIR="$HOME/security-tools"
mkdir -p "$TOOLS_DIR"

echo -e "${YELLOW}[*] Kurulum dizini: $TOOLS_DIR${NC}"
echo ""

# Fonksiyonlar
install_tool() {
    local tool=$1
    local package=$2
    
    echo -e "${BLUE}[→] $tool kuruluyor...${NC}"
    
    if apt-get install -y "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] $tool başarıyla kuruldu${NC}"
    else
        echo -e "${RED}[✗] $tool kurulamadı${NC}"
    fi
}

install_from_git() {
    local name=$1
    local url=$2
    local dir="$TOOLS_DIR/$name"
    
    echo -e "${BLUE}[→] $name GitHub'dan klonlanıyor...${NC}"
    
    if git clone "$url" "$dir" &> /dev/null; then
        echo -e "${GREEN}[✓] $name başarıyla klonlandı: $dir${NC}"
        return 0
    else
        echo -e "${RED}[✗] $name klonlanamadı${NC}"
        return 1
    fi
}

# Sistem Güncelleme
echo -e "${BLUE}========== SISTEM GÜNCELLEMESİ ==========${NC}"
echo -e "${YELLOW}[*] Paket listeleri güncelleniyor...${NC}"
apt-get update -y
apt-get upgrade -y
echo -e "${GREEN}[✓] Sistem güncellendi${NC}"
echo ""

# Temel Araçlar Kurulumu
echo -e "${BLUE}========== TEMEL ARAÇLAR ==========${NC}"

TOOLS=(
    "git|git"
    "curl|curl"
    "wget|wget"
    "nano|nano"
    "vim|vim"
    "htop|htop"
    "build-essential|build-essential"
    "python3|python3"
    "python3-pip|python3-pip"
    "perl|perl"
    "ruby|ruby"
)

for tool in "${TOOLS[@]}"; do
    IFS='|' read -r name package <<< "$tool"
    install_tool "$name" "$package"
done
echo ""

# Güvenlik Araçları Kurulumu
echo -e "${BLUE}========== GÜVENLİK ARAÇLARI ==========${NC}"

SECURITY_TOOLS=(
    "nmap|nmap"
    "netcat|netcat-traditional"
    "wireshark|wireshark"
    "tcpdump|tcpdump"
    "aircrack-ng|aircrack-ng"
    "hashcat|hashcat"
    "john|john"
    "sqlmap|sqlmap"
    "nikto|nikto"
    "hydra|hydra-gtk"
)

for tool in "${SECURITY_TOOLS[@]}"; do
    IFS='|' read -r name package <<< "$tool"
    install_tool "$name" "$package"
done
echo ""

# Kali Linux Araçları
echo -e "${BLUE}========== KALI LINUX ARAÇLARI ==========${NC}"

if command -v apt-get &> /dev/null; then
    KALI_TOOLS=(
        "metasploit-framework|metasploit-framework"
        "burpsuite|burpsuite"
        "gobuster|gobuster"
        "masscan|masscan"
        "responder|responder"
    )
    
    for tool in "${KALI_TOOLS[@]}"; do
        IFS='|' read -r name package <<< "$tool"
        install_tool "$name" "$package"
    done
fi
echo ""

# GitHub Araçlarından Kurulum
echo -e "${BLUE}========== GITHUB ARAÇLARI ==========${NC}"

GITHUB_TOOLS=(
    "Mr-Holmes|https://github.com/Lucksi/Mr-Holmes.git"
    "TheHarvester|https://github.com/laramies/theHarvester.git"
    "SubList3r|https://github.com/aboul3la/Sublist3r.git"
    "wafw00f|https://github.com/enablesecurity/wafw00f.git"
    "dirsearch|https://github.com/maurosoria/dirsearch.git"
    "commix|https://github.com/commixproject/commix.git"
    "Recon-ng|https://github.com/lanmaster53/recon-ng.git"
    "Empire|https://github.com/BC-SECURITY/Empire.git"
)

for tool in "${GITHUB_TOOLS[@]}"; do
    IFS='|' read -r name url <<< "$tool"
    install_from_git "$name" "$url"
done
echo ""

# Python Kütüphaneleri Kurulumu
echo -e "${BLUE}========== PYTHON KÜTÜPHANELERI ==========${NC}"

PIP_PACKAGES=(
    "requests"
    "beautifulsoup4"
    "paramiko"
    "scapy"
    "pexpect"
    "pycryptodome"
    "selenium"
    "shodan"
)

for package in "${PIP_PACKAGES[@]}"; do
    echo -e "${BLUE}[→] pip: $package kuruluyor...${NC}"
    if pip3 install "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] pip: $package kuruldu${NC}"
    else
        echo -e "${RED}[✗] pip: $package kurulamadı${NC}"
    fi
done
echo ""

# Metasploit Veritabanı Kurulumu
echo -e "${BLUE}========== METASPLOIT AYARLARI ==========${NC}"

if command -v msfdb &> /dev/null; then
    echo -e "${YELLOW}[*] PostgreSQL servisi başlatılıyor...${NC}"
    systemctl start postgresql
    
    echo -e "${YELLOW}[*] Metasploit veritabanı başlatılıyor...${NC}"
    msfdb delete &> /dev/null || true
    msfdb init
    
    echo -e "${GREEN}[✓] Metasploit hazır${NC}"
fi
echo ""

# Kullanıcı Dizinleri Oluşturma
echo -e "${BLUE}========== DİZİNLER OLUŞTURULUYOR ==========${NC}"

DIRS=(
    "$TOOLS_DIR/wordlists"
    "$TOOLS_DIR/payloads"
    "$TOOLS_DIR/wordlists/rockyou"
    "$TOOLS_DIR/scripts"
    "$HOME/.bashrc.d"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
    echo -e "${GREEN}[✓] Dizin oluşturuldu: $dir${NC}"
done
echo ""

# Rockyou Wordlist İndirme
echo -e "${BLUE}========== WORDLIST İNDİRİLMESİ ==========${NC}"

if [ ! -f "$TOOLS_DIR/wordlists/rockyou.txt" ]; then
    echo -e "${YELLOW}[*] RockYou wordlist indiriliyor...${NC}"
    cd "$TOOLS_DIR/wordlists/rockyou"
    if wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt; then
        echo -e "${GREEN}[✓] RockYou wordlist indirildi${NC}"
    else
        echo -e "${YELLOW}[!] RockYou wordlist indirilemedi (manuel olarak indirebilirsiniz)${NC}"
    fi
fi
echo ""

# Konfigürasyon Dosyaları
echo -e "${BLUE}========== KONFIGÜRASYON DOSYALARI ==========${NC}"

# Bash Alias Dosyası Oluşturma
cat > "$HOME/.bashrc.d/security-aliases" <<'EOF'
# Güvenlik Araçları Alias'ları

alias nmap-scan='nmap -sV -A'
alias nmap-full='nmap -p- -sV'
alias nmap-udp='nmap -sU -sV'

alias airmon='sudo airmon-ng'
alias airodump='sudo airodump-ng'

alias msfconsole='msfconsole'
alias msfvenom-list='msfvenom -l payloads'

alias sqlmap-auto='sqlmap -u'

alias enum-users='net users'
alias enum-groups='net group'

alias hash-md5="echo -n 'text' | md5sum"
alias hash-sha1="echo -n 'text' | sha1sum"
alias hash-sha256="echo -n 'text' | sha256sum"

alias tools-dir='cd ~/security-tools'

# Fonksiyonlar
extract() {
    if [ -f $1 ]; then
        case $1 in
            *.tar.bz2)   tar xjf $1   ;;
            *.tar.gz)    tar xzf $1   ;;
            *.bz2)       bunzip2 $1   ;;
            *.rar)       unrar x $1   ;;
            *.gz)        gunzip $1    ;;
            *.tar)       tar xf $1    ;;
            *.tbz2)      tar xjf $1   ;;
            *.tgz)       tar xzf $1   ;;
            *.zip)       unzip $1     ;;
            *.Z)         uncompress $1;;
            *.7z)        7z x $1      ;;
            *)           echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# IP Adresi Al
myip() {
    curl -s https://icanhazip.com/
}

# Lokal IP
localip() {
    hostname -I
}

# Port Kontrol
check-port() {
    nc -zv $1 $2
}
EOF

echo -e "${GREEN}[✓] Alias dosyası oluşturuldu${NC}"
echo ""

# Başlangıç Dosyası Güncelle
if ! grep -q "security-aliases" "$HOME/.bashrc"; then
    echo "source $HOME/.bashrc.d/security-aliases" >> "$HOME/.bashrc"
    echo -e "${GREEN}[✓] Bashrc güncellenmiştir${NC}"
fi
echo ""

# Özet
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   KURULUM BAŞARIYLA TAMAMLANDI! ✓${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Kurulum Özeti:${NC}"
echo -e "  📁 Araçlar Dizini: $TOOLS_DIR"
echo -e "  🔧 Metasploit: msfconsole"
echo -e "  🌐 Nmap: nmap [hedef]"
echo -e "  🔍 Wireshark: wireshark"
echo -e "  🛡️  Aircrack-ng: airmon-ng start wlan0"
echo ""
echo -e "${YELLOW}Kullanışlı Komutlar:${NC}"
echo -e "  tools-dir          → Araçlar dizinine git"
echo -e "  myip               → Dış IP adresini göster"
echo -e "  localip            → Yerel IP adresini göster"
echo -e "  check-port host 22 → Port kontrolü yap"
echo ""
echo -e "${RED}⚠️  YASAL UYARI:${NC}"
echo -e "Bu araçlar yalnızca YETKILI testler için kullanılabilir!"
echo -e "Kötü amaçlı kullanım yasadışıdır ve cezai işlem uygulanır."
echo ""
echo -e "${BLUE}Daha fazla bilgi için: cat TOOLS_INSTALLATION.md${NC}"
echo ""
