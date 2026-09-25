import os 
import sys 
import socket
from colorama import Fore, Style, init 

# Colorama'yı başlatıyoruz (Windows uyumluluğu için)
init(autoreset=True)

def banner():
    print(rf"{Fore.RED}=====================")
    print(rf"{Fore.GREEN}  MARKOS X Zero V1.0")
    print(rf"{Fore.RED}=====================")

def menu(): 
    print(f"{Fore.GREEN}[1] RAT") 
    print(f"{Fore.GREEN}[2] DDoS Attack") 
    print(f"{Fore.GREEN}[3] WAF Control") 
    print(f"{Fore.GREEN}[4] WAF ByPass") 
    print(f"{Fore.GREEN}[5] SMS Bomber") 
    print(f"{Fore.GREEN}[6] Kamera Hack") 
    print(f"{Fore.GREEN}[7] Siber Aktif Saldiri Paketi") 
    print(f"{Fore.GREEN}[8] Siber Aktif Savunma Paketi") 
    print(f"{Fore.GREEN}[9] Osint Tools") 
    print(f"{Fore.GREEN}[10] MarkOs Paketi")
    print(f"{Fore.GREEN}[0] Exit") 

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # Ekranı temizler
        banner()
        menu()
        
        # Kullanıcıdan girdi alma ve kontrol etme
        secenek = input(f"\n{Fore.RED}Seçiminiz: {Style.RESET_ALL}")
        
        if secenek == "1":
            print("RAT modülü seçildi... (Kodları buraya ekle)")
            input("\nDevam etmek için Enter'a bas...")
        elif secenek == "2":
            print("DDoS Attack modülü seçildi...")
            input("\nDevam etmek için Enter'a bas...")
        # Diğer seçenekleri (3, 4, 5...) buraya aynı mantıkla ekleyebilirsin
        elif secenek == "0":
            print(f"{Fore.YELLOW}Çıkış yapılıyor...")
            sys.exit()
        else:
            print(f"{Fore.RED}Geçersiz seçenek! Lütfen tekrar deneyin.")
            input("\nDevam etmek için Enter'a bas...")

if __name__ == "__main__":
    main()
