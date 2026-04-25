#!/bin/bash
# M3SFMODE Kurulum Scripti - Linux/Termux

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          M3SFMODE Kurulum Scripti v1.0.0                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Gerekli paketleri kontrol et
echo "[*] Sistem kontrol ediliyor..."

if ! command -v clang++ &> /dev/null; then
    echo "[!] clang++ bulunamadi. Kurulum yapiliyor..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
            sudo apt-get update
            sudo apt-get install -y clang
        elif [[ "$ID" == "fedora" ]]; then
            sudo dnf install -y clang
        elif [[ "$ID" == "arch" ]]; then
            sudo pacman -S clang
        fi
    fi
fi

# Build
echo "[*] Derleme yapiliyor..."
make clean
make release

if [ $? -eq 0 ]; then
    echo "[+] Derleme basarili!"
else
    echo "[-] Derleme hata!"
    exit 1
fi

# Kurulum
echo "[*] Sistem'e kuruluyor..."
sudo make install

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║             Kurulum Tamamlandi! ✓                        ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Kullanim: m3sfmode                                      ║"
echo "║  Yardim:   m3sfmode help                                 ║"
echo "║  Versiyon: 1.0.0                                         ║"
echo "║  GitHub:   github.com/memetcanwq31-ship-it/m3sfmode     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
